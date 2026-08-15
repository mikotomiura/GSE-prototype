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
    InterventionAction, InterventionInput, InterventionPolicyState, InterventionThresholds,
    OpportunityReason,
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

/// `nudge_need` 閾値 sweep の既定点 (0.50–0.90, 0.05 刻み, 9 点)。
///
/// ⚠️ 下限 0.50 は DC 不変条件 (`evaluate_defer_runs` doc) を守るための厳格な境界。
/// defer は `need >= nudge_need` のときのみ生じるため、`nudge_need >= 0.50` なら
/// run 内 feat は `p_flow <= 1 - nudge_need <= 0.50` で回復閾値 (`> 0.5`) を満たさず、
/// 回復は構造上 run の後に限られる。0.50 未満へ下げると本不変条件が破れる
/// (起点を run 終端の次 feat へ要変更)。
pub const DEFAULT_SWEEP_NUDGE_NEED: [f64; 9] =
    [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90];

/// sweep 下限。これ未満の `nudge_need` は DC 不変条件を壊すため拒否する。
pub const MIN_SWEEP_NUDGE_NEED: f64 = 0.50;

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

impl BinaryConfusion {
    /// 4 セルの総和 (この confusion に載った labeled decision 数)。
    fn total(&self) -> u32 {
        self.tn + self.fp + self.fn_ + self.tp
    }

    /// 別の confusion を要素ごとに足し込む (セッション横断プール用)。
    /// `saturating_add` で非現実的データ量での overflow panic も防ぐ
    /// (`intervention.rs` の累積と非対称にしない)。
    fn merge(&mut self, other: &BinaryConfusion) {
        self.tn = self.tn.saturating_add(other.tn);
        self.fp = self.fp.saturating_add(other.fp);
        self.fn_ = self.fn_.saturating_add(other.fn_);
        self.tp = self.tp.saturating_add(other.tp);
    }
}

/// 評価のために `decide()` の結果から保持する 1 decision 分。
///
/// production が捨てている `opportunity_reason` を reason 別層別化のために保持する
/// (`feats[i]` と 1:1 対応)。need_score / opportunity_score / suppressed_by は現行の
/// 成果物 (reason 別 HIR + 閾値 sweep) では消費されず、保持すると dead-field となり
/// clippy を汚すため敢えて持たない。将来 suppressor 別 defer correctness (plan Phase 2)
/// が要れば `decide()` から自明に再取得できる (decisions.md 参照)。
#[derive(Debug, Clone, Copy)]
struct EvalDecision {
    ts: u64,
    action: InterventionAction,
    opportunity_reason: OpportunityReason,
}

/// opportunity reason ごとに層別化した混同行列と派生指標。
///
/// 全 labeled decision を `opportunity_reason` で 1 つの bucket に振り分けるため、
/// 各 reason の `confusion` を足し合わせると全体の `binary_confusion` に一致する
/// (保存則。テストで検証)。HIR=0.647 の「犯人 reason」を特定するのが主目的。
#[derive(Debug, Clone, Serialize)]
pub struct ReasonStratum {
    pub reason: OpportunityReason,
    /// この reason に属する labeled decision の混同行列。
    pub confusion: BinaryConfusion,
    /// この reason の ACT 総数 (labeled + unlabeled)。発火ボリュームの目安。
    pub act_count: u32,
    /// labeled-ACT 数 (= fp+tp、HIR/Precision の分母)。
    pub act_labeled: u32,
    /// 有害介入率 = fp/(fp+tp)。labeled-ACT が 0 なら `None`。
    pub hir: Option<f64>,
    /// Precision = tp/(tp+fp)。labeled-ACT が 0 なら `None`。
    pub precision: Option<f64>,
}

impl ReasonStratum {
    /// 混同行列と ACT 総数から派生指標を埋めて構築する。
    fn from_parts(reason: OpportunityReason, confusion: BinaryConfusion, act_count: u32) -> Self {
        let act_labeled = confusion.fp + confusion.tp;
        let (hir, precision) = if act_labeled > 0 {
            (
                Some(confusion.fp as f64 / act_labeled as f64),
                Some(confusion.tp as f64 / act_labeled as f64),
            )
        } else {
            (None, None)
        };
        Self {
            reason,
            confusion,
            act_count,
            act_labeled,
            hir,
            precision,
        }
    }
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
    /// STALL recall = tp / (tp+fn)。STALL labeled が 0 なら `None`。
    pub recall: Option<f64>,
    /// opportunity reason 別の混同行列・HIR 分解 (enum 固定順で決定的)。
    pub reason_breakdown: Vec<ReasonStratum>,
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
            recall: None,
            reason_breakdown: Vec::new(),
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
    thresholds: &InterventionThresholds,
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
    // 注入 thresholds で policy を構築する (production は既定値、sweep は sweep 値)。
    let mut policy = InterventionPolicyState::new_with_thresholds(first_ts, *thresholds);
    let mut decisions: Vec<EvalDecision> = Vec::with_capacity(feats.len());
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
        let decision = policy.decide(input).decision;
        decisions.push(EvalDecision {
            ts: f.timestamp,
            action: decision.action,
            opportunity_reason: decision.opportunity_reason,
        });
    }

    // ── action 内訳 & decision×GT 混同行列 (全体 + reason 別) ─────────
    let mut counts = ActionCounts::default();
    let mut cm = BinaryConfusion::default();
    let mut labeled_decisions = 0u32;
    let mut act_unlabeled = 0u32;
    // reason 別アキュムレータ (OpportunityReason::ALL 固定順で index 付け)。
    let mut reason_cm = [BinaryConfusion::default(); OpportunityReason::ALL.len()];
    let mut reason_act = [0u32; OpportunityReason::ALL.len()];

    for d in &decisions {
        match d.action {
            InterventionAction::None => counts.none += 1,
            InterventionAction::Nudge => counts.nudge += 1,
            InterventionAction::Wall => counts.wall += 1,
            InterventionAction::Defer => counts.defer += 1,
        }
        let act = binarize_action(d.action);
        let ridx = reason_index(d.opportunity_reason);
        if act == DecisionBinary::Act {
            reason_act[ridx] += 1;
        }
        match range_class_at(d.ts, &ranges).map(binarize_label) {
            Some(gt) => {
                labeled_decisions += 1;
                // 全体と reason 別の同じセルを 1 回の分類で両方加算する
                // (保存則: 各 labeled decision はちょうど 1 reason bucket に入る)。
                let rc = &mut reason_cm[ridx];
                match (gt, act) {
                    (GtBinary::Protect, DecisionBinary::Hold) => {
                        cm.tn += 1;
                        rc.tn += 1;
                    }
                    (GtBinary::Protect, DecisionBinary::Act) => {
                        cm.fp += 1;
                        rc.fp += 1;
                    }
                    (GtBinary::Stall, DecisionBinary::Hold) => {
                        cm.fn_ += 1;
                        rc.fn_ += 1;
                    }
                    (GtBinary::Stall, DecisionBinary::Act) => {
                        cm.tp += 1;
                        rc.tp += 1;
                    }
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
    let stall_labeled = cm.fn_ + cm.tp;
    let recall = if stall_labeled > 0 {
        Some(cm.tp as f64 / stall_labeled as f64)
    } else {
        None
    };

    // reason 別層別化を enum 固定順で構築 (決定的)。空 reason は省く
    // (全 reason を回しても和は不変なので保存則テストは成立する)。
    let reason_breakdown: Vec<ReasonStratum> = OpportunityReason::ALL
        .iter()
        .enumerate()
        .filter(|(i, _)| reason_cm[*i].total() > 0 || reason_act[*i] > 0)
        .map(|(i, &r)| ReasonStratum::from_parts(r, reason_cm[i], reason_act[i]))
        .collect();

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
        recall,
        reason_breakdown,
        defer_runs,
        defer_recovered,
        dc,
        recovery_window_ms,
        session_duration_ms,
        burden_per_min,
        warnings,
    }
}

/// `OpportunityReason` を `OpportunityReason::ALL` 内の固定 index へ写す。
/// reason 別アキュムレータの添字付けに使う (O(8))。
fn reason_index(r: OpportunityReason) -> usize {
    // ALL は全 variant を網羅するので position は必ず Some。サイレント縮退ではない
    // ことを debug_assert で明示する (保存則の根拠を unwrap_or で隠さない)。
    OpportunityReason::ALL
        .iter()
        .position(|&x| x == r)
        .unwrap_or_else(|| {
            debug_assert!(false, "OpportunityReason::ALL must contain every variant");
            0
        })
}

/// 連続する defer decision を 1 区間として数え、各区間先頭 (defer onset) から
/// `window_ms` 以内に p_flow>0.5 へ回復したかを判定する。
/// 戻り値 = (defer 区間数, 回復した区間数)。
///
/// 回復起点は run 先頭の timestamp (= defer を初めて下した時刻)。`compute_recovered_at`
/// は起点以降を走査するため run 内 feat も候補に入るが、defer は `need=p_stuck >=
/// nudge_need` のときのみ生じる (intervention.rs の分岐順) ため、`nudge_need >= 0.50`
/// なら run 内 feat は必ず `p_flow <= 1 - nudge_need <= 0.50` で回復閾値 (`> 0.5`) を
/// 満たさない。よって回復は構造上 run の **後** に限られる。sweep は `nudge_need` を
/// 0.50–0.90 に限定しこの不変条件を守る (0.50 未満へ下げた場合のみ破れ、その際は
/// 起点を run 終端の次 feat へ要変更。`DEFAULT_SWEEP_NUDGE_NEED` / `MIN_SWEEP_NUDGE_NEED`)。
fn evaluate_defer_runs(
    decisions: &[EvalDecision],
    feats: &[FeatSnapshot],
    window_ms: u64,
) -> (u32, u32) {
    let mut runs = 0u32;
    let mut recovered = 0u32;
    let mut i = 0;
    while i < decisions.len() {
        if decisions[i].action != InterventionAction::Defer {
            i += 1;
            continue;
        }
        // run の先頭
        let run_start_ts = decisions[i].ts;
        runs += 1;
        // run を消費
        while i < decisions.len() && decisions[i].action == InterventionAction::Defer {
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
    match m.recall {
        Some(v) => out.push_str(&format!(
            "  STALL recall: {:.3}  (tp / {} STALL-labeled)\n",
            v,
            m.binary_confusion.fn_ + m.binary_confusion.tp,
        )),
        None => out.push_str("  STALL recall: n/a (no STALL labeled)\n"),
    }
    if !m.reason_breakdown.is_empty() {
        out.push_str(&format!(
            "{}\n",
            format_reason_breakdown(&m.reason_breakdown)
        ));
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

/// reason 別 HIR 分解の pretty テーブル (`--intervention` / `--sweep` 共用)。
fn format_reason_breakdown(strata: &[ReasonStratum]) -> String {
    let mut out = String::new();
    out.push_str("  By opportunity reason (labeled cells; fp = ACT∩PROTECT = harmful):\n");
    out.push_str("    reason                    ACT   fp   tp    HIR   Prec\n");
    let fmt_opt = |v: Option<f64>| {
        v.map(|x| format!("{:.3}", x))
            .unwrap_or_else(|| "  n/a".to_string())
    };
    for s in strata {
        out.push_str(&format!(
            "    {:<22} {:>4} {:>4} {:>4}  {:>5} {:>5}\n",
            s.reason.as_str(),
            s.act_count,
            s.confusion.fp,
            s.confusion.tp,
            fmt_opt(s.hir),
            fmt_opt(s.precision),
        ));
    }
    out
}

// =============================================================================
// threshold sweep (Phase 0) — production を一切変えず nudge_need を振って計測する
// =============================================================================

/// sweep の 1 セッション分入力 (所有データ。bin 層が NDJSON から構築して渡す)。
pub struct SweepInput {
    pub feats: Vec<FeatSnapshot>,
    pub point_labels: Vec<UserLabelEvent>,
    pub key_press_ts: Vec<u64>,
}

/// sweep の 1 閾値点における (セッション横断) プール済み指標。
#[derive(Debug, Clone, Serialize)]
pub struct SweepPoint {
    /// この点で用いた `nudge_need` 閾値。
    pub nudge_need: f64,
    pub total_decisions: u32,
    pub act_count: u32,
    pub binary_confusion: BinaryConfusion,
    pub act_labeled: u32,
    pub hir: Option<f64>,
    pub precision: Option<f64>,
    pub recall: Option<f64>,
    pub defer_runs: u32,
    pub defer_recovered: u32,
    pub dc: Option<f64>,
    /// プール対象セッションの総分数 (burden の分母)。
    pub total_minutes: f64,
    pub burden_per_min: f64,
    /// この閾値点での reason 別分解 (プール済み)。
    pub reason_breakdown: Vec<ReasonStratum>,
}

/// `nudge_need` threshold sweep レポート (`--sweep` で出力)。
#[derive(Debug, Clone, Serialize)]
pub struct InterventionSweepReport {
    pub sessions: u32,
    pub recovery_window_ms: u64,
    pub sweep_points: Vec<SweepPoint>,
    pub warnings: Vec<String>,
}

/// `nudge_need` を sweep し、各点で全セッションを独立評価して指標をプールする。
///
/// production の判定ロジックは不変で、`nudge_need` のみを注入閾値で差し替える
/// (他閾値は既定固定)。各セッションは独自の `InterventionPolicyState` で評価され
/// (cooldown / cap は session/day 単位)、混同行列・カウントを生の整数で足し合わせる。
///
/// ⚠️ `MIN_SWEEP_NUDGE_NEED` 未満の点は DC 不変条件を壊すため評価せず warning に記録する。
pub fn compute_intervention_sweep(
    sessions: &[SweepInput],
    sweep_nudge_need: &[f64],
    recovery_window_ms: u64,
) -> InterventionSweepReport {
    let mut warnings: Vec<String> = Vec::new();
    let base = InterventionThresholds::default();
    let mut sweep_points: Vec<SweepPoint> = Vec::with_capacity(sweep_nudge_need.len());

    // 検定力の可視化: 個別セッションの no-feat / no-label warning はプールで捨てるため、
    // 集約 warning を 1 行ずつ立てる (利用者が検定力ゼロに気づけるように)。flood は避ける。
    let n_sessions = sessions.len();
    let sessions_no_feats = sessions.iter().filter(|s| s.feats.is_empty()).count();
    let sessions_no_labels = sessions
        .iter()
        .filter(|s| s.point_labels.is_empty())
        .count();
    if sessions_no_feats > 0 {
        warnings.push(format!(
            "{}/{} session(s) had no feat snapshots (excluded from all metrics)",
            sessions_no_feats, n_sessions
        ));
    }
    if sessions_no_labels > 0 {
        warnings.push(format!(
            "{}/{} session(s) had no user_label GT (HIR/Precision/Recall unsupported for those; \
             DC/Burden still pooled)",
            sessions_no_labels, n_sessions
        ));
    }

    for &nn in sweep_nudge_need {
        if nn < MIN_SWEEP_NUDGE_NEED {
            warnings.push(format!(
                "skipped nudge_need={:.2}: below MIN_SWEEP_NUDGE_NEED={:.2} \
                 (would break DC defer-run invariant)",
                nn, MIN_SWEEP_NUDGE_NEED
            ));
            continue;
        }
        let thresholds = InterventionThresholds {
            nudge_need: nn,
            ..base
        };

        let mut cm = BinaryConfusion::default();
        let mut act_count = 0u32;
        let mut total_decisions = 0u32;
        let mut defer_runs = 0u32;
        let mut defer_recovered = 0u32;
        let mut total_minutes = 0.0f64;
        let mut reason_cm = [BinaryConfusion::default(); OpportunityReason::ALL.len()];
        let mut reason_act = [0u32; OpportunityReason::ALL.len()];

        for s in sessions {
            let m = compute_intervention_metrics(
                &s.feats,
                &s.point_labels,
                &s.key_press_ts,
                recovery_window_ms,
                &thresholds,
            );
            cm.merge(&m.binary_confusion);
            act_count = act_count.saturating_add(m.act_count);
            total_decisions = total_decisions.saturating_add(m.total_decisions);
            defer_runs = defer_runs.saturating_add(m.defer_runs);
            defer_recovered = defer_recovered.saturating_add(m.defer_recovered);
            total_minutes += m.session_duration_ms as f64 / 60_000.0;
            for st in &m.reason_breakdown {
                let i = reason_index(st.reason);
                reason_cm[i].merge(&st.confusion);
                reason_act[i] = reason_act[i].saturating_add(st.act_count);
            }
        }

        let act_labeled = cm.fp + cm.tp;
        let (hir, precision) = if act_labeled > 0 {
            (
                Some(cm.fp as f64 / act_labeled as f64),
                Some(cm.tp as f64 / act_labeled as f64),
            )
        } else {
            (None, None)
        };
        let stall_labeled = cm.fn_ + cm.tp;
        let recall = if stall_labeled > 0 {
            Some(cm.tp as f64 / stall_labeled as f64)
        } else {
            None
        };
        let dc = if defer_runs > 0 {
            Some(defer_recovered as f64 / defer_runs as f64)
        } else {
            None
        };
        let burden_per_min = if total_minutes > 0.0 {
            act_count as f64 / total_minutes
        } else {
            0.0
        };
        let reason_breakdown: Vec<ReasonStratum> = OpportunityReason::ALL
            .iter()
            .enumerate()
            .filter(|(i, _)| reason_cm[*i].total() > 0 || reason_act[*i] > 0)
            .map(|(i, &r)| ReasonStratum::from_parts(r, reason_cm[i], reason_act[i]))
            .collect();

        sweep_points.push(SweepPoint {
            nudge_need: nn,
            total_decisions,
            act_count,
            binary_confusion: cm,
            act_labeled,
            hir,
            precision,
            recall,
            defer_runs,
            defer_recovered,
            dc,
            total_minutes,
            burden_per_min,
            reason_breakdown,
        });
    }

    // 全閾値点で labeled-ACT が 0 なら HIR/Precision は全点 n/a = 検定力ゼロ。明示する。
    if !sweep_points.is_empty() && sweep_points.iter().all(|p| p.act_labeled == 0) {
        warnings.push(
            "no labeled ACT at any swept threshold — HIR/Precision unsupported \
             (zero statistical power; verify GT coverage)"
                .to_string(),
        );
    }

    InterventionSweepReport {
        sessions: sessions.len() as u32,
        recovery_window_ms,
        sweep_points,
        warnings,
    }
}

/// sweep の pretty-print 出力 (`--sweep` サブコマンド)。
pub fn format_intervention_sweep_pretty(r: &InterventionSweepReport) -> String {
    let mut out = String::new();
    out.push_str(&format!(
        "InterventionSweep (nudge_need; pooled over {} session(s), recovery window {}ms)\n",
        r.sessions, r.recovery_window_ms,
    ));
    out.push_str(
        "  other thresholds fixed at production defaults; lower=ACT more / higher=ACT fewer\n",
    );
    out.push_str("    nn     ACT   fp   tp    HIR   Prec Recall     DC  Burden/min\n");
    let fmt_opt = |v: Option<f64>| {
        v.map(|x| format!("{:.3}", x))
            .unwrap_or_else(|| "  n/a".to_string())
    };
    for p in &r.sweep_points {
        out.push_str(&format!(
            "    {:.2} {:>5} {:>4} {:>4}  {:>5} {:>5} {:>5}  {:>5}  {:>9.3}\n",
            p.nudge_need,
            p.act_count,
            p.binary_confusion.fp,
            p.binary_confusion.tp,
            fmt_opt(p.hir),
            fmt_opt(p.precision),
            fmt_opt(p.recall),
            fmt_opt(p.dc),
            p.burden_per_min,
        ));
    }
    // reason 別分解は production 既定 nudge_need 点で 1 つ提示する。
    // magic number 0.60 を埋め込まず Default から引くことで、const 変更時に表示が嘘にならない。
    let default_nn = InterventionThresholds::default().nudge_need;
    if let Some(def) = r
        .sweep_points
        .iter()
        .find(|p| (p.nudge_need - default_nn).abs() < 1e-9)
    {
        out.push_str(&format!(
            "\n  Reason breakdown at nudge_need={:.2} (production default):\n",
            default_nn
        ));
        out.push_str(&format_reason_breakdown(&def.reason_breakdown));
    }
    for w in &r.warnings {
        out.push_str(&format!("  warning: {}\n", w));
    }
    out
}

// =============================================================================
// Nudge FP/TP 診断 — ACT decision を (reason × GT) で層別し特徴量分布を出す
// =============================================================================
// 目的: correction_after_pause の FP 群 (GT=PROTECT) と TP 群 (GT=STALL) が
// 決定時の特徴量 (p_stuck / f3 / f4 / f6 / idle_ms) で分離できるかを診断する。
// production を変えず (既定 thresholds で decide を再実行し特徴量を読むだけ)。

/// 特徴量 1 種の min/median/max (FP/TP 分離の手掛かり)。
#[derive(Debug, Clone, Copy, Serialize, Default)]
pub struct MinMedMax {
    pub min: f64,
    pub median: f64,
    pub max: f64,
}

fn min_med_max(mut xs: Vec<f64>) -> MinMedMax {
    if xs.is_empty() {
        return MinMedMax::default();
    }
    xs.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    let n = xs.len();
    let median = if n % 2 == 1 {
        xs[n / 2]
    } else {
        (xs[n / 2 - 1] + xs[n / 2]) / 2.0
    };
    MinMedMax {
        min: xs[0],
        median,
        max: xs[n - 1],
    }
}

/// ACT decision の GT 群。PROTECT=有害(FP)母集団 / STALL=有益(TP)母集団 / Unlabeled=GT 圏外。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum GtGroup {
    Protect,
    Stall,
    Unlabeled,
}

impl GtGroup {
    fn as_str(self) -> &'static str {
        match self {
            Self::Protect => "protect(fp)",
            Self::Stall => "stall(tp)",
            Self::Unlabeled => "unlabeled",
        }
    }
    fn index(self) -> usize {
        match self {
            Self::Protect => 0,
            Self::Stall => 1,
            Self::Unlabeled => 2,
        }
    }
    const ALL: [GtGroup; 3] = [Self::Protect, Self::Stall, Self::Unlabeled];
}

/// reason × GT 群ごとの ACT decision の特徴量サマリ。
#[derive(Debug, Clone, Serialize)]
pub struct NudgeDiagnosticGroup {
    pub reason: OpportunityReason,
    pub gt: GtGroup,
    pub count: u32,
    pub p_stuck: MinMedMax,
    pub f3: MinMedMax,
    pub f4: MinMedMax,
    pub f6: MinMedMax,
    pub idle_ms: MinMedMax,
}

/// Nudge FP/TP 診断レポート (`--nudge-diag` で出力)。
#[derive(Debug, Clone, Serialize)]
pub struct NudgeDiagnostic {
    pub sessions: u32,
    pub total_act: u32,
    pub groups: Vec<NudgeDiagnosticGroup>,
    pub warnings: Vec<String>,
}

/// 特徴量ベクタの群別アキュムレータ。
#[derive(Default)]
struct FeatAccum {
    p_stuck: Vec<f64>,
    f3: Vec<f64>,
    f4: Vec<f64>,
    f6: Vec<f64>,
    idle_ms: Vec<f64>,
}

/// (reason, gt) を診断アキュムレータの平坦化 index へ写す。push 側・集計側で
/// 同じ式を共有し、添字算出の暗黙前提を 1 箇所に閉じる。
fn group_idx(reason: OpportunityReason, gt: GtGroup) -> usize {
    reason_index(reason) * GtGroup::ALL.len() + gt.index()
}

/// 各セッションで decide を再実行し、ACT decision を (reason × GT) で層別して
/// 決定時の特徴量サマリ (min/median/max) を pooled で算出する。production 不変。
pub fn compute_nudge_diagnostic(
    sessions: &[SweepInput],
    thresholds: &InterventionThresholds,
) -> NudgeDiagnostic {
    let mut warnings: Vec<String> = Vec::new();
    let n_reason = OpportunityReason::ALL.len();
    // index = reason_index * 3 + gt.index()
    let mut acc: Vec<FeatAccum> = (0..n_reason * GtGroup::ALL.len())
        .map(|_| FeatAccum::default())
        .collect();
    let mut total_act = 0u32;

    for s in sessions {
        if s.feats.is_empty() {
            continue;
        }
        let first_ts = s.feats.first().map(|f| f.timestamp).unwrap_or(0);
        let last_ts = s.feats.last().map(|f| f.timestamp).unwrap_or(first_ts);
        let ranges = derive_ranges_from_points(&s.point_labels, first_ts, last_ts);
        let mut policy = InterventionPolicyState::new_with_thresholds(first_ts, *thresholds);
        for f in &s.feats {
            let idle = idle_ms_at(f.timestamp, &s.key_press_ts);
            let input = InterventionInput {
                now_ms: f.timestamp,
                p_stuck: f.p_stuck,
                f3_correction_rate: f.f3,
                f4_burst_length: f.f4,
                f6_pause_after_del_rate: f.f6,
                idle_ms: idle,
                monk_mode: false,
                wall_active: false,
            };
            let decision = policy.decide(input).decision;
            if binarize_action(decision.action) != DecisionBinary::Act {
                continue;
            }
            total_act += 1;
            let gt = match range_class_at(f.timestamp, &ranges).map(binarize_label) {
                Some(GtBinary::Protect) => GtGroup::Protect,
                Some(GtBinary::Stall) => GtGroup::Stall,
                None => GtGroup::Unlabeled,
            };
            let a = &mut acc[group_idx(decision.opportunity_reason, gt)];
            a.p_stuck.push(f.p_stuck);
            a.f3.push(f.f3);
            a.f4.push(f.f4);
            a.f6.push(f.f6);
            a.idle_ms.push(idle as f64);
        }
    }

    let mut groups: Vec<NudgeDiagnosticGroup> = Vec::new();
    for &reason in OpportunityReason::ALL.iter() {
        for gt in GtGroup::ALL {
            let a = &acc[group_idx(reason, gt)];
            let count = a.p_stuck.len() as u32;
            if count == 0 {
                continue;
            }
            groups.push(NudgeDiagnosticGroup {
                reason,
                gt,
                count,
                p_stuck: min_med_max(a.p_stuck.clone()),
                f3: min_med_max(a.f3.clone()),
                f4: min_med_max(a.f4.clone()),
                f6: min_med_max(a.f6.clone()),
                idle_ms: min_med_max(a.idle_ms.clone()),
            });
        }
    }
    if total_act == 0 {
        warnings.push(
            "no ACT decisions found — nothing to diagnose (verify thresholds and GT coverage)"
                .to_string(),
        );
    } else if !groups.iter().any(|g| g.gt != GtGroup::Unlabeled) {
        // ACT はあるが全て GT 圏外 → FP/TP 分離が出せない (検定力ゼロ)。
        warnings.push(
            "GT coverage 0 for ACT decisions — FP/TP split unavailable (all ACT fell outside \
             labeled ranges)"
                .to_string(),
        );
    }

    NudgeDiagnostic {
        sessions: sessions.len() as u32,
        total_act,
        groups,
        warnings,
    }
}

/// 診断の pretty-print 出力 (`--nudge-diag` サブコマンド)。
pub fn format_nudge_diagnostic_pretty(d: &NudgeDiagnostic) -> String {
    let mut out = String::new();
    out.push_str(&format!(
        "NudgeDiagnostic (ACT decisions by reason×GT, pooled over {} session(s); ACT={})\n",
        d.sessions, d.total_act,
    ));
    out.push_str("  each feature cell = min / median / max\n");
    out.push_str(
        "  reason                 gt            n   p_stuck            f3                 f4                 f6                 idle_ms\n",
    );
    let f = |m: &MinMedMax| format!("{:.2}/{:.2}/{:.2}", m.min, m.median, m.max);
    let fi = |m: &MinMedMax| format!("{:.0}/{:.0}/{:.0}", m.min, m.median, m.max);
    for g in &d.groups {
        out.push_str(&format!(
            "  {:<22} {:<11} {:>3}   {:<17}  {:<17}  {:<17}  {:<17}  {}\n",
            g.reason.as_str(),
            g.gt.as_str(),
            g.count,
            f(&g.p_stuck),
            f(&g.f3),
            f(&g.f4),
            f(&g.f6),
            fi(&g.idle_ms),
        ));
    }
    for w in &d.warnings {
        out.push_str(&format!("  warning: {}\n", w));
    }
    out
}

// =============================================================================
// correction_after_pause veto floor の counterfactual 評価 (Step 2)
// =============================================================================
// P000 診断で TP の下限は f4=2.38 / f6=0.37。FP のみが低裾に居るため、
// 「correction_after_pause を f4<floor OR f6<floor なら veto」は TP ゼロコストで
// FP 低裾だけ切る候補。各候補を全セッションでプール評価し HIR/recall を試算する。
// production は既定 (floor None) で不変。

/// f4 floor 候補 (P000 TP の f4 下限)。
pub const CORRECTION_F4_FLOOR_CANDIDATE: f64 = 2.38;
/// f6 floor 候補 (P000 TP の f6 下限)。
pub const CORRECTION_F6_FLOOR_CANDIDATE: f64 = 0.37;

/// correction floor 候補 1 つの pooled 結果行。
#[derive(Debug, Clone, Serialize)]
pub struct CorrectionFloorRow {
    pub label: String,
    pub f4_floor: Option<f64>,
    pub f6_floor: Option<f64>,
    pub nudge: u32,
    pub binary_confusion: BinaryConfusion,
    pub act_labeled: u32,
    pub hir: Option<f64>,
    pub precision: Option<f64>,
    pub recall: Option<f64>,
    pub defer_runs: u32,
    pub dc: Option<f64>,
    pub burden_per_min: f64,
}

/// correction floor counterfactual レポート (`--corr-floor` で出力)。
#[derive(Debug, Clone, Serialize)]
pub struct CorrectionFloorReport {
    pub sessions: u32,
    pub recovery_window_ms: u64,
    pub rows: Vec<CorrectionFloorRow>,
    pub warnings: Vec<String>,
}

/// 1 候補 (thresholds) を全セッションでプール評価して 1 行を作る。
fn pool_correction_floor_row(
    label: &str,
    thresholds: &InterventionThresholds,
    sessions: &[SweepInput],
    recovery_window_ms: u64,
) -> CorrectionFloorRow {
    let mut cm = BinaryConfusion::default();
    let mut nudge = 0u32;
    let mut act_count = 0u32;
    let mut defer_runs = 0u32;
    let mut defer_recovered = 0u32;
    let mut total_minutes = 0.0f64;
    for s in sessions {
        let m = compute_intervention_metrics(
            &s.feats,
            &s.point_labels,
            &s.key_press_ts,
            recovery_window_ms,
            thresholds,
        );
        cm.merge(&m.binary_confusion);
        nudge = nudge.saturating_add(m.action_counts.nudge);
        act_count = act_count.saturating_add(m.act_count);
        defer_runs = defer_runs.saturating_add(m.defer_runs);
        defer_recovered = defer_recovered.saturating_add(m.defer_recovered);
        total_minutes += m.session_duration_ms as f64 / 60_000.0;
    }
    let act_labeled = cm.fp + cm.tp;
    let (hir, precision) = if act_labeled > 0 {
        (
            Some(cm.fp as f64 / act_labeled as f64),
            Some(cm.tp as f64 / act_labeled as f64),
        )
    } else {
        (None, None)
    };
    let stall_labeled = cm.fn_ + cm.tp;
    let recall = if stall_labeled > 0 {
        Some(cm.tp as f64 / stall_labeled as f64)
    } else {
        None
    };
    let dc = if defer_runs > 0 {
        Some(defer_recovered as f64 / defer_runs as f64)
    } else {
        None
    };
    let burden_per_min = if total_minutes > 0.0 {
        act_count as f64 / total_minutes
    } else {
        0.0
    };
    CorrectionFloorRow {
        label: label.to_string(),
        f4_floor: thresholds.correction_f4_floor,
        f6_floor: thresholds.correction_f6_floor,
        nudge,
        binary_confusion: cm,
        act_labeled,
        hir,
        precision,
        recall,
        defer_runs,
        dc,
        burden_per_min,
    }
}

/// baseline + f4-floor + f6-floor + both(OR) の 4 候補を counterfactual 評価する。
/// production は変えず、注入 thresholds で decide を再実行してプールする。
pub fn compute_correction_floor_report(
    sessions: &[SweepInput],
    recovery_window_ms: u64,
) -> CorrectionFloorReport {
    let base = InterventionThresholds::default();
    let candidates: [(&str, InterventionThresholds); 4] = [
        ("baseline", base),
        (
            "f4>=2.38",
            InterventionThresholds {
                correction_f4_floor: Some(CORRECTION_F4_FLOOR_CANDIDATE),
                ..base
            },
        ),
        (
            "f6>=0.37",
            InterventionThresholds {
                correction_f6_floor: Some(CORRECTION_F6_FLOOR_CANDIDATE),
                ..base
            },
        ),
        (
            "f4>=2.38|f6>=0.37",
            InterventionThresholds {
                correction_f4_floor: Some(CORRECTION_F4_FLOOR_CANDIDATE),
                correction_f6_floor: Some(CORRECTION_F6_FLOOR_CANDIDATE),
                ..base
            },
        ),
    ];
    let rows = candidates
        .iter()
        .map(|(label, t)| pool_correction_floor_row(label, t, sessions, recovery_window_ms))
        .collect();
    let mut warnings: Vec<String> = Vec::new();
    let no_labels = sessions
        .iter()
        .filter(|s| s.point_labels.is_empty())
        .count();
    if no_labels > 0 {
        warnings.push(format!(
            "{}/{} session(s) had no user_label GT (HIR/recall pooled only over labeled sessions)",
            no_labels,
            sessions.len()
        ));
    }
    CorrectionFloorReport {
        sessions: sessions.len() as u32,
        recovery_window_ms,
        rows,
        warnings,
    }
}

/// correction floor レポートの pretty-print 出力 (`--corr-floor` サブコマンド)。
pub fn format_correction_floor_pretty(r: &CorrectionFloorReport) -> String {
    let mut out = String::new();
    out.push_str(&format!(
        "CorrectionFloorReport (correction_after_pause veto, pooled over {} session(s), W={}ms)\n",
        r.sessions, r.recovery_window_ms,
    ));
    out.push_str("  veto = drop correction_after_pause nudge when f4<floor OR f6<floor\n");
    out.push_str("  ⚠️ floors are P000 IN-SAMPLE TP minima — \"TP zero-cost\" is partly tautological; re-validate on holdout / new subjects before adopting\n");
    out.push_str(
        "    candidate              nudge   fp   tp    HIR   Prec Recall     DC  Burden/min\n",
    );
    let fmt_opt = |v: Option<f64>| {
        v.map(|x| format!("{:.3}", x))
            .unwrap_or_else(|| "  n/a".to_string())
    };
    for row in &r.rows {
        out.push_str(&format!(
            "    {:<20} {:>5} {:>4} {:>4}  {:>5} {:>5} {:>5}  {:>5}  {:>9.3}\n",
            row.label,
            row.nudge,
            row.binary_confusion.fp,
            row.binary_confusion.tp,
            fmt_opt(row.hir),
            fmt_opt(row.precision),
            fmt_opt(row.recall),
            fmt_opt(row.dc),
            row.burden_per_min,
        ));
    }
    for w in &r.warnings {
        out.push_str(&format!("  warning: {}\n", w));
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
            // ★ Tier 0 (記録のみ)。介入評価は本フィールドを読まない。
            keys: 0,
            bs_keys: 0,
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
        let m = compute_intervention_metrics(
            &feats,
            &labels,
            &presses,
            60_000,
            &InterventionThresholds::default(),
        );
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
        let m = compute_intervention_metrics(
            &feats,
            &labels,
            &presses,
            60_000,
            &InterventionThresholds::default(),
        );
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
        let m = compute_intervention_metrics(
            &feats,
            &labels,
            &presses,
            60_000,
            &InterventionThresholds::default(),
        );
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
        let m = compute_intervention_metrics(
            &feats,
            &labels,
            &presses,
            60_000,
            &InterventionThresholds::default(),
        );
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
        let m = compute_intervention_metrics(
            &feats,
            &[],
            &presses,
            60_000,
            &InterventionThresholds::default(),
        );
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
        let m = compute_intervention_metrics(
            &feats,
            &[],
            &presses,
            60_000,
            &InterventionThresholds::default(),
        );
        assert_eq!(m.act_count, 1);
        assert_eq!(m.act_unlabeled, 1);
        assert_eq!(m.labeled_decisions, 0);
        assert_eq!(m.gt_coverage, 0.0);
        assert!(m.hir.is_none());
    }

    #[test]
    fn empty_feats_yields_warning_no_panic() {
        let m =
            compute_intervention_metrics(&[], &[], &[], 60_000, &InterventionThresholds::default());
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
        let m = compute_intervention_metrics(
            &feats,
            &[],
            &presses,
            60_000,
            &InterventionThresholds::default(),
        );
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
        let m = compute_intervention_metrics(
            &feats,
            &labels,
            &presses,
            60_000,
            &InterventionThresholds::default(),
        );
        let s = format_intervention_pretty(&m);
        assert!(s.contains("InterventionMetrics"));
        assert!(s.contains("HIR"));
        assert!(s.contains("DC"));
        assert!(s.contains("Burden"));
    }

    // ── reason 別層別化 / recall / sweep ─────────────────────────────

    /// reason 別 confusion の総和が全体 confusion に一致する (保存則)。
    /// 各 labeled decision はちょうど 1 reason bucket に入るので必ず成立する。
    #[test]
    fn reason_breakdown_sums_to_global_confusion() {
        let feats = vec![
            feat_full(10_000, 0.20, 0.66, 0.05, 6.0, 0.0), // short+post_burst → nudge (ACT)
            feat_full(11_000, 0.10, 0.72, 0.05, 5.0, 0.0), // active_typing → defer (HOLD)
            feat_full(12_000, 0.80, 0.05, 0.0, 5.0, 0.0),  // 低 need → none (HOLD)
        ];
        // idle: feat0=10000-7000=3000(short), feat1=11000-10500=500(active), feat2=12000-11800=200(active)
        let presses = vec![7_000u64, 10_500, 11_800];
        let labels = vec![
            ulabel(10_000, LabelClass::Flow),
            ulabel(11_500, LabelClass::Stuck),
        ];
        let m = compute_intervention_metrics(
            &feats,
            &labels,
            &presses,
            60_000,
            &InterventionThresholds::default(),
        );
        let g = m.binary_confusion;
        let (mut tn, mut fp, mut fnv, mut tp) = (0u32, 0u32, 0u32, 0u32);
        for s in &m.reason_breakdown {
            tn += s.confusion.tn;
            fp += s.confusion.fp;
            fnv += s.confusion.fn_;
            tp += s.confusion.tp;
        }
        assert_eq!((tn, fp, fnv, tp), (g.tn, g.fp, g.fn_, g.tp));
        // post_burst_pause で発火した nudge が PROTECT に乗り fp=1 として層別化される
        assert!(m
            .reason_breakdown
            .iter()
            .any(|s| s.reason == OpportunityReason::PostBurstPause
                && s.confusion.fp == 1
                && s.hir == Some(1.0)));
    }

    /// STALL recall = tp/(tp+fn)。
    #[test]
    fn recall_is_tp_over_stall_labeled() {
        let feats = vec![
            feat_full(10_000, 0.20, 0.66, 0.05, 6.0, 0.0), // post_burst nudge (ACT)
            feat_full(11_000, 0.10, 0.05, 0.0, 5.0, 0.0),  // 低 need none (HOLD)
        ];
        let presses = vec![7_000u64];
        let labels = vec![ulabel(10_000, LabelClass::Stuck)]; // 全区間 Stuck
        let m = compute_intervention_metrics(
            &feats,
            &labels,
            &presses,
            60_000,
            &InterventionThresholds::default(),
        );
        assert_eq!(m.binary_confusion.tp, 1);
        assert_eq!(m.binary_confusion.fn_, 1);
        assert_eq!(m.recall, Some(0.5));
    }

    /// nudge_need を上げると pooled ACT は単調非増加 (sweep の健全性)。
    #[test]
    fn sweep_act_count_monotonic_in_nudge_need() {
        // 全 feat short+post_burst (高 opportunity)、need を 0.62/0.68/0.74 に並べる。
        let feats = vec![
            feat_full(10_000, 0.20, 0.62, 0.05, 6.0, 0.0),
            feat_full(11_000, 0.20, 0.68, 0.05, 6.0, 0.0),
            feat_full(12_000, 0.20, 0.74, 0.05, 6.0, 0.0),
        ];
        let presses = vec![7_000u64]; // 各 feat の idle = 3000/4000/5000ms (全て short_pause)
        let sessions = vec![SweepInput {
            feats,
            point_labels: Vec::new(),
            key_press_ts: presses,
        }];
        let report = compute_intervention_sweep(&sessions, &DEFAULT_SWEEP_NUDGE_NEED, 60_000);
        assert_eq!(report.sweep_points.len(), DEFAULT_SWEEP_NUDGE_NEED.len());
        let acts: Vec<u32> = report.sweep_points.iter().map(|p| p.act_count).collect();
        for w in acts.windows(2) {
            assert!(
                w[1] <= w[0],
                "act_count must be non-increasing as nudge_need rises: {:?}",
                acts
            );
        }
        // 下限 0.50 では 3 件全て発火、上端 0.90 では 0 件 (全 need < 0.90)。
        assert_eq!(acts.first(), Some(&3));
        assert_eq!(acts.last(), Some(&0));
    }

    /// MIN_SWEEP_NUDGE_NEED 未満の点は DC 不変条件保護のため skip + warning。
    #[test]
    fn sweep_skips_below_min_threshold() {
        let feats = vec![feat_full(10_000, 0.20, 0.66, 0.05, 6.0, 0.0)];
        let presses = vec![7_000u64];
        let sessions = vec![SweepInput {
            feats,
            point_labels: Vec::new(),
            key_press_ts: presses,
        }];
        let report = compute_intervention_sweep(&sessions, &[0.40, 0.60], 60_000);
        assert_eq!(report.sweep_points.len(), 1); // 0.40 は評価せず
        assert_eq!(report.sweep_points[0].nudge_need, 0.60);
        assert!(report.warnings.iter().any(|w| w.contains("0.40")));
    }

    /// DC 不変条件の前提を 2 定数の関係で固定する: sweep 下限 `MIN_SWEEP_NUDGE_NEED` で
    /// run 内 feat の p_flow は `1 - MIN_SWEEP_NUDGE_NEED` 以下、これが回復閾値
    /// `DEFAULT_P_FLOW_THRESHOLD` (strict `>`) を満たさないこと。将来どちらかが動いて
    /// `1 - MIN > THRESH` になると不変条件が静かに破れるため、ここで早期に落とす。
    #[test]
    // 定数同士の比較なのは意図どおり (const をまたいだ静的ガード)。clippy の
    // assertions_on_constants はこの用途では誤検出なので明示的に許可する。
    #[allow(clippy::assertions_on_constants)]
    fn dc_invariant_threshold_floor_holds() {
        assert!(
            1.0 - MIN_SWEEP_NUDGE_NEED <= DEFAULT_P_FLOW_THRESHOLD,
            "DC invariant broken: run-internal p_flow ({}) could exceed recovery threshold ({})",
            1.0 - MIN_SWEEP_NUDGE_NEED,
            DEFAULT_P_FLOW_THRESHOLD
        );
    }

    // ── Nudge FP/TP 診断 ─────────────────────────────────────────────

    /// correction_after_pause の ACT を GT 群 (Protect=fp / Stall=tp) で分離し、
    /// p_stuck median が群で異なることを確認する。
    #[test]
    fn nudge_diagnostic_splits_fp_and_tp_by_gt() {
        let feats = vec![
            // correction_after_pause (f3>=0.20) + short pause、need 0.62 → nudge、GT=Flow → fp
            feat_full(10_000, 0.20, 0.62, 0.25, 5.0, 0.0),
            // 同 reason、need 0.80 → nudge、GT=Stuck → tp
            feat_full(11_000, 0.10, 0.80, 0.25, 5.0, 0.0),
        ];
        let presses = vec![7_000u64]; // feat0 idle=3000, feat1 idle=4000 (どちらも short)
        let labels = vec![
            ulabel(10_000, LabelClass::Flow),
            ulabel(10_500, LabelClass::Stuck),
        ];
        let sessions = vec![SweepInput {
            feats,
            point_labels: labels,
            key_press_ts: presses,
        }];
        let d = compute_nudge_diagnostic(&sessions, &InterventionThresholds::default());
        assert_eq!(d.total_act, 2);
        let protect = d.groups.iter().find(|g| {
            g.reason == OpportunityReason::CorrectionAfterPause && g.gt == GtGroup::Protect
        });
        let stall = d.groups.iter().find(|g| {
            g.reason == OpportunityReason::CorrectionAfterPause && g.gt == GtGroup::Stall
        });
        assert_eq!(protect.map(|g| g.count), Some(1));
        assert_eq!(stall.map(|g| g.count), Some(1));
        // p_stuck median は protect(0.62) < stall(0.80)
        assert!(protect.unwrap().p_stuck.median < stall.unwrap().p_stuck.median);
    }

    #[test]
    fn nudge_diagnostic_empty_no_panic() {
        let d = compute_nudge_diagnostic(&[], &InterventionThresholds::default());
        assert_eq!(d.total_act, 0);
        assert!(d.groups.is_empty());
        assert!(d.warnings.iter().any(|w| w.contains("no ACT")));
    }

    /// `OpportunityReason::ALL` の網羅性ガード: `reason_index` が各 variant に
    /// 一意の index を割り当て、全 8 種を被覆すること (variant 追加時に ALL 更新を
    /// 忘れると診断/層別が index 0 へサイレント縮退するのを早期に落とす)。
    #[test]
    fn opportunity_reason_all_is_complete_and_unique() {
        use std::collections::HashSet;
        assert_eq!(OpportunityReason::ALL.len(), 8);
        let idxs: HashSet<usize> = OpportunityReason::ALL
            .iter()
            .map(|&r| reason_index(r))
            .collect();
        assert_eq!(idxs.len(), 8, "reason_index must be unique per variant");
        let strs: HashSet<&str> = OpportunityReason::ALL.iter().map(|r| r.as_str()).collect();
        assert_eq!(strs.len(), 8, "as_str must be unique per variant");
    }

    /// correction floor counterfactual: f6 floor が低 f6 の FP nudge を veto し、
    /// nudge 数と fp が baseline より減ること。
    #[test]
    fn correction_floor_report_reduces_nudges() {
        let feats = vec![
            feat_full(10_000, 0.20, 0.66, 0.25, 5.0, 0.0), // correction, f6=0.0 → veto 対象 (GT=Flow=fp)
            feat_full(11_000, 0.10, 0.80, 0.25, 5.0, 0.50), // correction, f6=0.50 → 残す (GT=Stuck=tp)
        ];
        let presses = vec![7_000u64];
        let labels = vec![
            ulabel(10_000, LabelClass::Flow),
            ulabel(10_500, LabelClass::Stuck),
        ];
        let sessions = vec![SweepInput {
            feats,
            point_labels: labels,
            key_press_ts: presses,
        }];
        let r = compute_correction_floor_report(&sessions, 60_000);
        assert_eq!(r.rows.len(), 4);
        let baseline = r.rows.iter().find(|x| x.label == "baseline").unwrap();
        let f6 = r.rows.iter().find(|x| x.label == "f6>=0.37").unwrap();
        assert_eq!(baseline.nudge, 2);
        assert!(
            f6.nudge < baseline.nudge,
            "f6 floor should veto the low-f6 nudge"
        );
        assert!(f6.binary_confusion.fp < baseline.binary_confusion.fp);
        // TP は f6=0.50>=floor なので維持される
        assert_eq!(f6.binary_confusion.tp, baseline.binary_confusion.tp);
    }
}
