//! v2 介入ポリシーのオフライン反実仮想評価。
//!
//! 既存セッションの logged feat 列を `intervention::decide()` で時刻順にステップし、
//! 「もし v2 が動いていたらどう発火したか」を再現する。GT (point user_label) は
//! forward-fill で区間化し、decision×GT の 2×2 で安全性指標を算出する。
//!
//! すべて純粋関数で構成され、副作用も OS API も持たない (analysis/ 純粋性維持)。
//! 設計判断は `.steering/20260606-gse-v2-intervention-eval/decisions.md` を参照。
//!
//! # 評価指標
//! - **HIR (有害介入率)** = ACT∩PROTECT / labeled-ACT … 最重要・安全性指標。
//! - **Precision** = ACT∩STALL / labeled-ACT。labeled-ACT 上で HIR+Precision=1。
//! - **DC (defer 正答率)** = W 秒以内に回復した defer 区間 / 全 defer 区間。
//! - **Burden** = ACT 回数 / セッション分。
//!
//! # 限界
//! - cadence: production は 500ms ポーリング、本評価は feat 1Hz ステップ。wall 累積
//!   タイミングに微差が出る (HIR の定性結論は頑健だが数値は近似)。
//! - `wall_active` を常に false とみなす: 本評価は「実際には wall を提示していない」
//!   反実仮想なので、wall 提示中 (`wall_active=true`) の状態遷移は再現しない。
//! - フィードバック効果 (誤介入が後続打鍵を変える相互作用) は再現不可。
//! - GT は旧 3 クラス自己申告由来 → 本評価は verdict ではなく screening。

use serde::Serialize;

use crate::analysis::intervention::{
    InterventionAction, InterventionInput, InterventionPolicyState,
};
use crate::analysis::loop_step::FeatSnapshot;
use crate::analysis::metrics::{
    compute_recovered_at, LabelClass, RangeLabel, UserLabelEvent, DEFAULT_P_FLOW_THRESHOLD,
    DEFAULT_RECOVERY_WINDOW_MS,
};

/// defer 区間の回復探索窓の既定値（暫定）。
///
/// 回復窓 W の pre-registration は別タスク (スコープ外)。今回は素の指標算出までなので
/// Stuck 回復と同じ既定値 (15 分) を流用する。セッション長 (1.5–8.5 分) では実質
/// 「session 末尾までに p_flow>0.5 へ回復したか」を測る (decisions.md D5)。
pub const DEFAULT_DEFER_RECOVERY_WINDOW_MS: u64 = DEFAULT_RECOVERY_WINDOW_MS;

/// 二値化した decision。ACT={nudge, wall} / HOLD={none, defer}。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum DecisionBinary {
    Hold,
    Act,
}

fn binarize_action(action: InterventionAction) -> DecisionBinary {
    match action {
        InterventionAction::Nudge | InterventionAction::Wall => DecisionBinary::Act,
        InterventionAction::None | InterventionAction::Defer => DecisionBinary::Hold,
    }
}

/// 二値化した GT。PROTECT={flow, incubation} / STALL={stuck}。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum GtBinary {
    Protect,
    Stall,
}

fn binarize_label(label: LabelClass) -> GtBinary {
    match label {
        LabelClass::Flow | LabelClass::Incubation => GtBinary::Protect,
        LabelClass::Stuck => GtBinary::Stall,
    }
}

/// 各 action の発火回数内訳。
#[derive(Debug, Clone, Copy, Serialize, Default)]
pub struct ActionCounts {
    pub none: u32,
    pub nudge: u32,
    pub wall: u32,
    pub defer: u32,
}

/// decision×GT の 2×2 混同行列。
///
/// PROTECT を守る (HOLD) のが正、STALL に介入する (ACT) のが正。
/// `fp` (PROTECT に ACT) が有害介入で、HIR の分子。
#[derive(Debug, Clone, Copy, Serialize, Default)]
pub struct BinaryConfusion {
    /// PROTECT & HOLD: 正しい抑制。
    pub tn: u32,
    /// PROTECT & ACT: **有害介入** (HIR 分子)。
    pub fp: u32,
    /// STALL & HOLD: 見送り。
    #[serde(rename = "fn")]
    pub fn_: u32,
    /// STALL & ACT: 有益介入。
    pub tp: u32,
}

/// 介入評価の集計結果 (`--intervention --json` で出力)。
#[derive(Debug, Clone, Serialize)]
pub struct InterventionMetrics {
    /// ステップした feat (= decision) の総数。
    pub total_decisions: u32,
    pub action_counts: ActionCounts,
    /// ACT (nudge+wall) 回数。
    pub act_count: u32,
    /// HOLD (none+defer) 回数。
    pub hold_count: u32,
    /// GT 区間に乗った decision 数。
    pub labeled_decisions: u32,
    /// labeled_decisions / total_decisions。GT カバレッジ (検定力の目安)。
    pub gt_coverage: f64,
    pub binary_confusion: BinaryConfusion,
    /// GT が当たった ACT 数 (= fp+tp、HIR/Precision の分母)。
    pub act_labeled: u32,
    /// GT が当たらなかった ACT 数 (カバレッジ注意)。
    pub act_unlabeled: u32,
    /// 有害介入率 = fp / (fp+tp)。labeled-ACT が 0 なら `None`。
    pub hir: Option<f64>,
    /// Precision = tp / (tp+fp)。labeled-ACT が 0 なら `None`。
    pub precision: Option<f64>,
    /// defer 区間 (連続する defer の run) の総数。
    pub defer_runs: u32,
    /// W 秒以内に p_flow>0.5 へ回復した defer 区間数。
    pub defer_recovered: u32,
    /// DC = defer_recovered / defer_runs。defer 区間が 0 なら `None`。
    pub dc: Option<f64>,
    /// DC 算出に使った回復窓 (ms)。暫定既定値 (D5)。
    pub recovery_window_ms: u64,
    /// セッション長 (last_feat_ts - first_feat_ts、ms)。
    pub session_duration_ms: u64,
    /// Burden = ACT 回数 / セッション分。
    pub burden_per_min: f64,
    pub warnings: Vec<String>,
}

impl InterventionMetrics {
    /// decision が 1 件も無い (feat 空) ときのゼロ値。
    /// フィールド追加時の同期漏れを 1 箇所に閉じる。
    fn empty(recovery_window_ms: u64, warnings: Vec<String>) -> Self {
        Self {
            total_decisions: 0,
            action_counts: ActionCounts::default(),
            act_count: 0,
            hold_count: 0,
            labeled_decisions: 0,
            gt_coverage: 0.0,
            binary_confusion: BinaryConfusion::default(),
            act_labeled: 0,
            act_unlabeled: 0,
            hir: None,
            precision: None,
            defer_runs: 0,
            defer_recovered: 0,
            dc: None,
            recovery_window_ms,
            session_duration_ms: 0,
            burden_per_min: 0.0,
            warnings,
        }
    }
}

/// point label を forward-fill で区間化する (decisions.md D2)。
///
/// 各 label がその時刻から次の label まで状態を保持するとみなす。区間は
/// `[label_i, label_{i+1}-1]` の**連続した**閉区間列で、先頭は `first_ts` へ、
/// 末尾は `last_ts` へ延伸する。連続性 (`end_i = start_{i+1}-1`) により
/// union は `[min(first_ts, labels), max(last_ts, labels)]` を隙間なくカバーし、
/// 必ず `[first_ts, last_ts]` を包含する (= 全 feat に GT が当たる)。
/// label が `first_ts` 以前 / `last_ts` 以後にある場合は区間が feat 範囲を
/// はみ出すが、`range_class_at` の閉区間ヒットには無害。
///
/// `labels` は未ソートでも良い (内部でコピーして昇順整列する)。
/// 空なら空 Vec を返す (GT なし → HIR/Precision 算出不能)。
pub fn derive_ranges_from_points(
    labels: &[UserLabelEvent],
    first_ts: u64,
    last_ts: u64,
) -> Vec<RangeLabel> {
    if labels.is_empty() {
        return Vec::new();
    }
    let mut sorted: Vec<UserLabelEvent> = labels.to_vec();
    sorted.sort_by_key(|l| l.timestamp);

    let n = sorted.len();
    let mut ranges = Vec::with_capacity(n);
    for (i, lbl) in sorted.iter().enumerate() {
        let start = if i == 0 {
            first_ts.min(lbl.timestamp)
        } else {
            lbl.timestamp
        };
        let end = if i + 1 == n {
            last_ts.max(lbl.timestamp)
        } else {
            // 次 label 直前まで。境界の二重計上を避けるため -1ms。
            sorted[i + 1].timestamp.saturating_sub(1)
        };
        ranges.push(RangeLabel {
            start_ms: start,
            end_ms: end,
            label: lbl.label,
        });
    }
    ranges
}

/// 時刻 `ts` を含む区間の GT クラスを返す (forward-fill 区間は重ならない閉区間)。
fn range_class_at(ts: u64, ranges: &[RangeLabel]) -> Option<LabelClass> {
    ranges
        .iter()
        .find(|r| ts >= r.start_ms && ts <= r.end_ms)
        .map(|r| r.label)
}

/// `key_press_ts`（昇順）から `ts` 時点の idle_ms を復元する。
///
/// production の `get_keyboard_idle_ms` と同セマンティクス: 直前の key press からの
/// 経過 ms。`ts` 以前の press が無ければ 0 (production も last_key=0 で 0 を返す)。
fn idle_ms_at(ts: u64, key_press_ts: &[u64]) -> u64 {
    let upto = key_press_ts.partition_point(|&k| k <= ts);
    if upto == 0 {
        0
    } else {
        ts.saturating_sub(key_press_ts[upto - 1])
    }
}

/// v2 介入ポリシーをオフラインで反実仮想リプレイし、評価指標を算出する。
///
/// # 引数
/// - `feats`: logged feat 列 (timestamp 昇順を仮定)。p_stuck/f3/f4/f6/timestamp を使う。
/// - `point_labels`: NDJSON の point user_label (GT、未ソートでも可)。
/// - `key_press_ts`: key press の timestamp 列 (昇順を仮定)。idle_ms 復元用。
/// - `recovery_window_ms`: DC の回復探索窓。
pub fn compute_intervention_metrics(
    feats: &[FeatSnapshot],
    point_labels: &[UserLabelEvent],
    key_press_ts: &[u64],
    recovery_window_ms: u64,
) -> InterventionMetrics {
    let mut warnings: Vec<String> = Vec::new();

    if feats.is_empty() {
        warnings.push(
            "no feat snapshots found — intervention metrics unavailable (verify hmm_version \
             >= 0.2.0 with Phase 1 feat logging)"
                .to_string(),
        );
        return InterventionMetrics::empty(recovery_window_ms, warnings);
    }

    let first_ts = feats.first().map(|f| f.timestamp).unwrap_or(0);
    let last_ts = feats.last().map(|f| f.timestamp).unwrap_or(first_ts);

    if point_labels.is_empty() {
        warnings.push(
            "no user_label entries — GT-binarized HIR/Precision unavailable (DC/Burden still \
             computed from feat stream)"
                .to_string(),
        );
    }
    let ranges = derive_ranges_from_points(point_labels, first_ts, last_ts);

    // ── decide() を時刻順にステップ ──────────────────────────────────
    // `decisions[i]` は `feats[i]` に 1:1 対応する (同一ループで push)。
    // evaluate_defer_runs はこの対応を前提に feats を timestamp で再走査する。
    let mut policy = InterventionPolicyState::new(first_ts);
    let mut decisions: Vec<(u64, InterventionAction)> = Vec::with_capacity(feats.len());
    for f in feats {
        let input = InterventionInput {
            now_ms: f.timestamp,
            p_stuck: f.p_stuck,
            f3_correction_rate: f.f3,
            f4_burst_length: f.f4,
            f6_pause_after_del_rate: f.f6,
            idle_ms: idle_ms_at(f.timestamp, key_press_ts),
            monk_mode: false,
            wall_active: false,
        };
        let action = policy.decide(input).decision.action;
        decisions.push((f.timestamp, action));
    }

    // ── action 内訳 & decision×GT 混同行列 ───────────────────────────
    let mut counts = ActionCounts::default();
    let mut cm = BinaryConfusion::default();
    let mut labeled_decisions = 0u32;
    let mut act_unlabeled = 0u32;

    for &(ts, action) in &decisions {
        match action {
            InterventionAction::None => counts.none += 1,
            InterventionAction::Nudge => counts.nudge += 1,
            InterventionAction::Wall => counts.wall += 1,
            InterventionAction::Defer => counts.defer += 1,
        }
        let act = binarize_action(action);
        match range_class_at(ts, &ranges).map(binarize_label) {
            Some(gt) => {
                labeled_decisions += 1;
                match (gt, act) {
                    (GtBinary::Protect, DecisionBinary::Hold) => cm.tn += 1,
                    (GtBinary::Protect, DecisionBinary::Act) => cm.fp += 1,
                    (GtBinary::Stall, DecisionBinary::Hold) => cm.fn_ += 1,
                    (GtBinary::Stall, DecisionBinary::Act) => cm.tp += 1,
                }
            }
            None => {
                if act == DecisionBinary::Act {
                    act_unlabeled += 1;
                }
            }
        }
    }

    let act_count = counts.nudge + counts.wall;
    let hold_count = counts.none + counts.defer;
    let act_labeled = cm.fp + cm.tp;
    let hir = if act_labeled > 0 {
        Some(cm.fp as f64 / act_labeled as f64)
    } else {
        None
    };
    let precision = if act_labeled > 0 {
        Some(cm.tp as f64 / act_labeled as f64)
    } else {
        None
    };

    // ── defer 区間 (連続 run) の回復判定 → DC ────────────────────────
    let (defer_runs, defer_recovered) = evaluate_defer_runs(&decisions, feats, recovery_window_ms);
    let dc = if defer_runs > 0 {
        Some(defer_recovered as f64 / defer_runs as f64)
    } else {
        None
    };

    // ── Burden ──────────────────────────────────────────────────────
    let session_duration_ms = last_ts.saturating_sub(first_ts);
    let minutes = session_duration_ms as f64 / 60_000.0;
    let burden_per_min = if minutes > 0.0 {
        act_count as f64 / minutes
    } else {
        0.0
    };

    let total_decisions = decisions.len() as u32;
    let gt_coverage = if total_decisions > 0 {
        labeled_decisions as f64 / total_decisions as f64
    } else {
        0.0
    };

    InterventionMetrics {
        total_decisions,
        action_counts: counts,
        act_count,
        hold_count,
        labeled_decisions,
        gt_coverage,
        binary_confusion: cm,
        act_labeled,
        act_unlabeled,
        hir,
        precision,
        defer_runs,
        defer_recovered,
        dc,
        recovery_window_ms,
        session_duration_ms,
        burden_per_min,
        warnings,
    }
}

/// 連続する defer decision を 1 区間として数え、各区間先頭 (defer onset) から
/// `window_ms` 以内に p_flow>0.5 へ回復したかを判定する。
/// 戻り値 = (defer 区間数, 回復した区間数)。
///
/// 回復起点は run 先頭の timestamp (= defer を初めて下した時刻)。`compute_recovered_at`
/// は起点以降を走査するため run 内 feat も候補に入るが、defer は `need=p_stuck >=
/// NUDGE_NEED_THRESHOLD(0.60)` のときのみ生じる (intervention.rs の分岐順) ため、
/// run 内 feat は必ず `p_flow <= 1 - 0.60 = 0.40 < 0.5` で回復閾値を満たさない。
/// よって回復は構造上 run の **後** に限られる (NUDGE_NEED_THRESHOLD を 0.50 未満へ
/// 下げた場合のみ本不変条件は破れる — その際は起点を run 終端の次 feat へ要変更)。
fn evaluate_defer_runs(
    decisions: &[(u64, InterventionAction)],
    feats: &[FeatSnapshot],
    window_ms: u64,
) -> (u32, u32) {
    let mut runs = 0u32;
    let mut recovered = 0u32;
    let mut i = 0;
    while i < decisions.len() {
        if decisions[i].1 != InterventionAction::Defer {
            i += 1;
            continue;
        }
        // run の先頭
        let run_start_ts = decisions[i].0;
        runs += 1;
        // run を消費
        while i < decisions.len() && decisions[i].1 == InterventionAction::Defer {
            i += 1;
        }
        if compute_recovered_at(run_start_ts, feats, window_ms, DEFAULT_P_FLOW_THRESHOLD).is_some()
        {
            recovered += 1;
        }
    }
    (runs, recovered)
}

/// pretty-print 出力を生成 (`--intervention` サブコマンド)。
pub fn format_intervention_pretty(m: &InterventionMetrics) -> String {
    let mut out = String::new();
    out.push_str("InterventionMetrics (offline counterfactual replay)\n");
    out.push_str(&format!(
        "  Decisions: {} (none:{}, nudge:{}, wall:{}, defer:{})\n",
        m.total_decisions,
        m.action_counts.none,
        m.action_counts.nudge,
        m.action_counts.wall,
        m.action_counts.defer,
    ));
    out.push_str(&format!("  ACT: {}  HOLD: {}\n", m.act_count, m.hold_count));
    out.push_str(&format!(
        "  GT coverage: {:.1}% ({}/{} decisions labeled)\n",
        m.gt_coverage * 100.0,
        m.labeled_decisions,
        m.total_decisions,
    ));
    out.push_str("  Decision×GT (rows = GT, cols = decision):\n");
    out.push_str("                HOLD   ACT\n");
    out.push_str(&format!(
        "    PROTECT     {:>4}  {:>4}   (ACT∩PROTECT = harmful)\n",
        m.binary_confusion.tn, m.binary_confusion.fp,
    ));
    out.push_str(&format!(
        "    STALL       {:>4}  {:>4}\n",
        m.binary_confusion.fn_, m.binary_confusion.tp,
    ));
    match m.hir {
        Some(v) => out.push_str(&format!(
            "  HIR (harmful intervention rate): {:.3}  (ACT∩PROTECT / {} labeled-ACT)\n",
            v, m.act_labeled,
        )),
        None => out.push_str("  HIR: n/a (no labeled ACT)\n"),
    }
    match m.precision {
        Some(v) => out.push_str(&format!("  Precision: {:.3}\n", v)),
        None => out.push_str("  Precision: n/a (no labeled ACT)\n"),
    }
    if m.act_unlabeled > 0 {
        out.push_str(&format!(
            "  (note: {} ACT decisions fell outside GT coverage)\n",
            m.act_unlabeled,
        ));
    }
    match m.dc {
        Some(v) => out.push_str(&format!(
            "  DC (defer correctness): {:.3}  ({}/{} defer runs recovered within {}ms)\n",
            v, m.defer_recovered, m.defer_runs, m.recovery_window_ms,
        )),
        None => out.push_str("  DC: n/a (no defer runs)\n"),
    }
    let dur_s = m.session_duration_ms as f64 / 1000.0;
    out.push_str(&format!(
        "  Burden: {:.3} ACT/min  (session {:.1}s)\n",
        m.burden_per_min, dur_s,
    ));
    out.push_str(&format!("  Warnings: {}\n", m.warnings.len()));
    for w in &m.warnings {
        out.push_str(&format!("    - {}\n", w));
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    fn feat_full(
        timestamp: u64,
        p_flow: f64,
        p_stuck: f64,
        f3: f64,
        f4: f64,
        f6: f64,
    ) -> FeatSnapshot {
        let p_inc = (1.0 - p_flow - p_stuck).max(0.0);
        FeatSnapshot {
            timestamp,
            f1: 0.0,
            f3,
            f4,
            f5: 0.0,
            f6,
            p_flow,
            p_inc,
            p_stuck,
            raw_x: 0.0,
            raw_y: 0.0,
            ewma_x: 0.0,
            ewma_y: 0.0,
            obs: 0,
            alpha: 0.0,
        }
    }

    fn ulabel(timestamp: u64, label: LabelClass) -> UserLabelEvent {
        UserLabelEvent { timestamp, label }
    }

    // ── idle_ms_at ──────────────────────────────────────────────────

    #[test]
    fn idle_ms_uses_last_press_before_ts() {
        let presses = vec![1_000u64, 4_000, 7_000];
        assert_eq!(idle_ms_at(7_500, &presses), 500); // 7500 - 7000
        assert_eq!(idle_ms_at(4_000, &presses), 0); // press 丁度
        assert_eq!(idle_ms_at(500, &presses), 0); // press 前は 0
        assert_eq!(idle_ms_at(6_000, &presses), 2_000); // 6000 - 4000
    }

    // ── derive_ranges_from_points ───────────────────────────────────

    #[test]
    fn derive_ranges_forward_fills_and_covers_session() {
        let labels = vec![
            ulabel(2_000, LabelClass::Flow),
            ulabel(5_000, LabelClass::Stuck),
        ];
        let ranges = derive_ranges_from_points(&labels, 1_000, 8_000);
        assert_eq!(ranges.len(), 2);
        // 先頭は session 頭 (1000) まで延伸、次 label 直前 (4999) まで
        assert_eq!(ranges[0].start_ms, 1_000);
        assert_eq!(ranges[0].end_ms, 4_999);
        assert_eq!(ranges[0].label, LabelClass::Flow);
        // 末尾は session 末 (8000) まで延伸
        assert_eq!(ranges[1].start_ms, 5_000);
        assert_eq!(ranges[1].end_ms, 8_000);
        assert_eq!(ranges[1].label, LabelClass::Stuck);
        // 全区間カバー: 任意の ts に GT が当たる
        assert_eq!(range_class_at(1_000, &ranges), Some(LabelClass::Flow));
        assert_eq!(range_class_at(4_999, &ranges), Some(LabelClass::Flow));
        assert_eq!(range_class_at(5_000, &ranges), Some(LabelClass::Stuck));
        assert_eq!(range_class_at(8_000, &ranges), Some(LabelClass::Stuck));
    }

    #[test]
    fn derive_ranges_empty_labels_yields_no_ranges() {
        let ranges = derive_ranges_from_points(&[], 1_000, 8_000);
        assert!(ranges.is_empty());
        assert_eq!(range_class_at(5_000, &ranges), None);
    }

    #[test]
    fn derive_ranges_label_before_first_feat_still_covers_session() {
        // user_label が first_ts より前にあるケース (自己申告が初回 feat より早い)。
        // 連続区間なので [first_ts, last_ts] は隙間なくカバーされる。
        let labels = vec![
            ulabel(500, LabelClass::Flow), // first_ts(1000) より前
            ulabel(5_000, LabelClass::Stuck),
        ];
        let ranges = derive_ranges_from_points(&labels, 1_000, 8_000);
        // feat 範囲 [1000, 8000] の全点に GT が当たる
        for ts in [1_000u64, 2_000, 4_999, 5_000, 8_000] {
            assert!(
                range_class_at(ts, &ranges).is_some(),
                "ts={} should be covered",
                ts
            );
        }
        assert_eq!(range_class_at(1_000, &ranges), Some(LabelClass::Flow));
        assert_eq!(range_class_at(5_000, &ranges), Some(LabelClass::Stuck));
    }

    // ── HIR 境界値 ──────────────────────────────────────────────────

    /// post_burst_pause (idle 3s, f4>=4, 低 f3/f6) + 高 need + GT=Flow を全 feat に
    /// 与えると、全 ACT が PROTECT に乗り HIR=1.0 になる。
    #[test]
    fn all_act_on_protect_gives_hir_one() {
        // press 列で各 feat の idle を ~3000ms (short pause) にする
        let feats = vec![
            feat_full(10_000, 0.20, 0.66, 0.05, 6.0, 0.0),
            feat_full(11_000, 0.20, 0.66, 0.05, 6.0, 0.0),
        ];
        // 各 feat の 3s 前に press → idle=3000 → short_pause + post_burst → Nudge
        let presses = vec![7_000u64, 8_000];
        let labels = vec![ulabel(10_000, LabelClass::Flow)]; // 全区間 Flow=PROTECT
        let m = compute_intervention_metrics(&feats, &labels, &presses, 60_000);
        assert_eq!(m.act_count, 2, "both feats should ACT (nudge)");
        assert_eq!(m.action_counts.nudge, 2);
        assert_eq!(m.binary_confusion.fp, 2, "ACT∩PROTECT = harmful");
        assert_eq!(m.binary_confusion.tp, 0);
        assert_eq!(m.hir, Some(1.0));
        assert_eq!(m.precision, Some(0.0));
    }

    /// 同じ ACT でも GT=Stuck なら HIR=0 / Precision=1。
    #[test]
    fn all_act_on_stall_gives_hir_zero() {
        let feats = vec![feat_full(10_000, 0.20, 0.66, 0.05, 6.0, 0.0)];
        let presses = vec![7_000u64];
        let labels = vec![ulabel(10_000, LabelClass::Stuck)];
        let m = compute_intervention_metrics(&feats, &labels, &presses, 60_000);
        assert_eq!(m.act_count, 1);
        assert_eq!(m.hir, Some(0.0));
        assert_eq!(m.precision, Some(1.0));
        assert_eq!(m.binary_confusion.tp, 1);
    }

    // ── DC 境界値 ───────────────────────────────────────────────────

    /// active typing (idle<2s) + 高 need → defer。直後に p_flow>0.5 へ回復 → DC=1.0。
    #[test]
    fn defer_then_recovery_gives_dc_one() {
        let feats = vec![
            // idle≈500ms (active typing) + need 0.72 → defer
            feat_full(10_000, 0.10, 0.72, 0.05, 5.0, 0.0),
            // 回復: p_flow>0.5
            feat_full(11_000, 0.80, 0.10, 0.0, 5.0, 0.0),
        ];
        let presses = vec![9_500u64]; // feat[0] の 500ms 前
        let labels = vec![ulabel(10_000, LabelClass::Stuck)];
        let m = compute_intervention_metrics(&feats, &labels, &presses, 60_000);
        assert_eq!(m.action_counts.defer, 1, "first feat should defer");
        assert_eq!(m.defer_runs, 1);
        assert_eq!(m.defer_recovered, 1);
        assert_eq!(m.dc, Some(1.0));
    }

    #[test]
    fn defer_without_recovery_gives_dc_zero() {
        let feats = vec![
            feat_full(10_000, 0.10, 0.72, 0.05, 5.0, 0.0),
            feat_full(11_000, 0.15, 0.70, 0.05, 5.0, 0.0), // p_flow まだ低い
        ];
        let presses = vec![9_500u64, 10_500];
        let labels = vec![ulabel(10_000, LabelClass::Stuck)];
        let m = compute_intervention_metrics(&feats, &labels, &presses, 60_000);
        assert!(m.defer_runs >= 1);
        assert_eq!(m.defer_recovered, 0);
        assert_eq!(m.dc, Some(0.0));
    }

    // ── Burden / カバレッジ / 空入力 ────────────────────────────────

    #[test]
    fn burden_is_act_count_per_minute() {
        // セッション長 120s (2分)、ACT 2 件 → Burden = 1.0 ACT/min。
        // t=60_000 / 120_000 の 3s 前に press を置き short pause + post_burst → Nudge。
        let feats = vec![
            feat_full(60_000, 0.20, 0.66, 0.05, 6.0, 0.0),
            feat_full(120_000, 0.20, 0.66, 0.05, 6.0, 0.0),
        ];
        let presses = vec![57_000u64, 117_000];
        let m = compute_intervention_metrics(&feats, &[], &presses, 60_000);
        assert_eq!(m.session_duration_ms, 60_000); // last - first = 120k-60k
        assert_eq!(m.act_count, 2);
        // 60s セッション → 2 ACT / 1 min = 2.0
        assert!((m.burden_per_min - 2.0).abs() < 1e-9);
    }

    #[test]
    fn act_unlabeled_counted_when_no_gt_coverage() {
        // GT (point label) が無いと ACT に GT が当たらず act_unlabeled に積まれる。
        // 実 13 セッションの 0-label セッションで通る経路。
        let feats = vec![feat_full(10_000, 0.20, 0.66, 0.05, 6.0, 0.0)];
        let presses = vec![7_000u64]; // idle 3s → nudge
        let m = compute_intervention_metrics(&feats, &[], &presses, 60_000);
        assert_eq!(m.act_count, 1);
        assert_eq!(m.act_unlabeled, 1);
        assert_eq!(m.labeled_decisions, 0);
        assert_eq!(m.gt_coverage, 0.0);
        assert!(m.hir.is_none());
    }

    #[test]
    fn empty_feats_yields_warning_no_panic() {
        let m = compute_intervention_metrics(&[], &[], &[], 60_000);
        assert_eq!(m.total_decisions, 0);
        assert!(m.hir.is_none());
        assert!(m.dc.is_none());
        assert!(m.warnings.iter().any(|w| w.contains("no feat")));
    }

    #[test]
    fn no_labels_still_computes_dc_and_burden() {
        let feats = vec![
            feat_full(10_000, 0.10, 0.72, 0.05, 5.0, 0.0),
            feat_full(11_000, 0.80, 0.10, 0.0, 5.0, 0.0),
        ];
        let presses = vec![9_500u64];
        let m = compute_intervention_metrics(&feats, &[], &presses, 60_000);
        // GT 無し → HIR/Precision は n/a だが DC は出る
        assert!(m.hir.is_none());
        assert_eq!(m.gt_coverage, 0.0);
        assert_eq!(m.dc, Some(1.0));
        assert!(m.warnings.iter().any(|w| w.contains("no user_label")));
    }

    #[test]
    fn format_intervention_pretty_has_expected_structure() {
        let feats = vec![feat_full(10_000, 0.20, 0.66, 0.05, 6.0, 0.0)];
        let presses = vec![7_000u64];
        let labels = vec![ulabel(10_000, LabelClass::Flow)];
        let m = compute_intervention_metrics(&feats, &labels, &presses, 60_000);
        let s = format_intervention_pretty(&m);
        assert!(s.contains("InterventionMetrics"));
        assert!(s.contains("HIR"));
        assert!(s.contains("DC"));
        assert!(s.contains("Burden"));
    }
}
