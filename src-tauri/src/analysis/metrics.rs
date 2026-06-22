//! Phase 1 Task 2: UserLabel × FeatSnapshot の突き合わせメトリクス算出。
//!
//! すべて純粋関数で構成されており、副作用を持たない (analysis/ 純粋性維持)。
//! `recovered_at` 等の派生値はログ記録時ではなく本モジュールで計算する設計のため、
//! 閾値変更時に過去セッションを再処理するだけで再計算できる。

use serde::Serialize;

use crate::analysis::loop_step::FeatSnapshot;

/// Stuck ラベルからの回復探索の既定ウィンドウ: 15 分。
pub const DEFAULT_RECOVERY_WINDOW_MS: u64 = 15 * 60 * 1000;

/// 回復判定の既定閾値: `p_flow > 0.5`。
pub const DEFAULT_P_FLOW_THRESHOLD: f64 = 0.5;

/// HMM argmax とラベル時刻を突き合わせる近接窓: ±1 秒。
pub const LABEL_MATCH_WINDOW_MS: u64 = 1_000;

/// リード/ラグ探索窓: ラベル時刻から ±60 秒。
pub const LEAD_LAG_WINDOW_MS: u64 = 60_000;

/// GT ラベル種別（replay.rs の ReplayEvent::UserLabel から復号される）。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum LabelClass {
    Flow,
    Incubation,
    Stuck,
}

impl LabelClass {
    /// NDJSON の `label` フィールド文字列から変換。
    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "flow" => Some(Self::Flow),
            "incubation" => Some(Self::Incubation),
            "stuck" => Some(Self::Stuck),
            _ => None,
        }
    }

    fn index(self) -> usize {
        match self {
            Self::Flow => 0,
            Self::Incubation => 1,
            Self::Stuck => 2,
        }
    }

    fn as_str(self) -> &'static str {
        match self {
            Self::Flow => "Flow",
            Self::Incubation => "Incubation",
            Self::Stuck => "Stuck",
        }
    }
}

const CLASSES: [LabelClass; 3] = [LabelClass::Flow, LabelClass::Incubation, LabelClass::Stuck];

/// UserLabel の一点イベント表現（replay.rs から渡される）。
#[derive(Debug, Clone, Copy)]
pub struct UserLabelEvent {
    pub timestamp: u64,
    pub label: LabelClass,
}

/// 3×3 混同行列。`matrix[i][j]` は「正解クラス i、推定クラス j」の件数。
/// 行列の順序は [Flow, Incubation, Stuck]。
#[derive(Debug, Clone, Serialize)]
pub struct ConfusionMatrix {
    pub matrix: [[u32; 3]; 3],
}

#[derive(Debug, Clone, Serialize)]
pub struct ClassMetrics {
    pub class: LabelClass,
    pub precision: f64,
    pub recall: f64,
    pub f1: f64,
    pub support: u32,
}

#[derive(Debug, Clone, Serialize)]
pub struct SessionMetrics {
    pub total_labels: u32,
    pub confusion: ConfusionMatrix,
    pub per_class: [ClassMetrics; 3],
    pub macro_f1: f64,
    pub micro_f1: f64,
    /// HMM の検出リード (正 = HMM が先行) / ラグ (負 = 遅延) の中央値（ms）。
    /// ラベルごとに ±60 秒窓内で「同クラスが argmax になった最初の時刻」を求める。
    pub detection_lead_ms_median: Option<i64>,
    /// Stuck → p_flow > 0.5 到達までの時間の中央値（ms）。
    pub stuck_recovery_ms_median: Option<u64>,
    /// v0.4 アウトカム指標 (a)AI依存度 / (b)自力解決率。`--metrics` 経路で算出して
    /// 付与する。HMM 精度メトリクス (上記) とは独立で、key/paste 行が無い経路
    /// (`compute_range_metrics` 等) では `None`。additive・後方互換 (既存利用側不変)。
    pub outcome: Option<OutcomeMetrics>,
    pub warnings: Vec<String>,
}

// ── v0.4 Outcome metrics (a)AI依存度 / (b)自力解決率 ────────────────────────
//
// 設計: `.steering/20260623-outcome-metrics/design.md` (v2 採用)。
// 「Stuck エピソード」を基盤抽象にし、その上に (a)(b) を載せる。トリガは
// `StuckTrigger` で外出しし (既定 = p_stuck 閾値)、研究設計フォークをコードに
// 焼き込まない。すべて content-free (vk コード / 文字数 / 確率のみ。Unicode 内容に
// 触れない = data-privacy ルール1)。

/// Stuck 候補の判定トリガ。既定は `PStuckThreshold` (全セッションで算出可能)。
/// `UserLabel` / `InterventionFired` は再処理で切替可能だが既定にしない
/// (`.steering/20260623-outcome-metrics/decisions.md` CD-OM1)。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum StuckTrigger {
    /// `p_stuck >= p_stuck_trigger` の feat を Stuck とみなす (既定)。
    PStuckThreshold,
    /// `user_label == stuck` を Stuck とみなす (GT。較正セッションのみ)。
    UserLabel,
    /// 介入発火 (`intervention_decision.action != none`) を Stuck とみなす。
    InterventionFired,
}

/// アウトカム指標の算出パラメータ。既定値は研究設計上の暫定値であり、
/// 再処理で調整可能 (metrics.rs の「閾値変更時に過去セッションを再処理するだけで
/// 再計算できる」哲学に従う)。ユーザー承認 2026-06-23。
#[derive(Debug, Clone, Copy)]
pub struct OutcomeConfig {
    /// Stuck 候補の判定トリガ。
    pub trigger: StuckTrigger,
    /// `PStuckThreshold` 時の閾値。Wall トリガ (p_stuck>0.70) より緩め = 候補を広く拾い
    /// 回復判定で絞る。
    pub p_stuck_trigger: f64,
    /// 連続 Stuck feat をひとつのエピソードに統合する最大間隙 (ms)。
    /// 1 ローリングウィンドウ = 30s。瞬間的な p_stuck 低下を同一エピソードに吸収する。
    pub merge_gap_ms: u64,
    /// エピソード後、回復 (p_flow>0.5) を探す窓 (ms)。handoff 指定の 5 分。
    pub recovery_window_ms: u64,
    /// 「net_diff 正進行」とみなす回復窓内 manual_insert_chars 純増の下限 (文字)。
    /// 既定 1 = 最小解釈 (純増 1 文字以上で前進)。ユーザー承認 2026-06-23。
    pub net_diff_min: u64,
    /// 「large paste」とみなす external_paste_chars の下限 (文字)。
    pub large_threshold: u64,
    /// 「after_stuck」= エピソード後この窓 (ms) 内の paste を stuck 起因とみなす。
    pub after_window_ms: u64,
}

impl Default for OutcomeConfig {
    fn default() -> Self {
        Self {
            trigger: StuckTrigger::PStuckThreshold,
            p_stuck_trigger: 0.60,
            merge_gap_ms: 30_000,
            recovery_window_ms: 5 * 60 * 1000,
            net_diff_min: 1,
            large_threshold: 50,
            after_window_ms: 120_000,
        }
    }
}

/// content-free な paste イベント (文字数のみ。中身は持たない)。
#[derive(Debug, Clone, Copy)]
pub struct PasteEvent {
    pub timestamp: u64,
    pub chars: u64,
}

/// content-free な key press (vk コードのみ。data-privacy ルール1 で記録許可)。
#[derive(Debug, Clone, Copy)]
pub struct KeyPress {
    pub timestamp: u64,
    pub vk: u32,
}

/// Stuck エピソード = `p_stuck >= 閾値` (または他トリガ) が `merge_gap_ms` 以内の
/// 中断を挟んで連続する区間。`end_ms` 以降に回復を探す。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub struct StuckEpisode {
    pub start_ms: u64,
    pub end_ms: u64,
}

/// v0.4 アウトカム指標。すべて数値のみ (本文・キーストローク内容を含まない)。
/// 算出不能 (分母 0) の比率は `None` (NaN を出さない)。
#[derive(Debug, Clone, Serialize)]
pub struct OutcomeMetrics {
    // ── (b) 自力解決率 ──
    /// 文字生成キー press − backspace/delete press (0 下限)。content-free な近似 (proxy)。
    /// **注意 (cross-review AGREE-3)**: NDJSON の key 行は修飾キー同時押し状態を持たないため、
    /// `Ctrl+V` / `Cmd+V` の `V` (0x56) も 1 文字として計上される。external paste 1 回ごとに
    /// manual を +1 程度過大評価し、`manual_contribution_ratio` を僅かに manual 寄りに偏らせる。
    /// 解析時は外れ値として扱う前提 (capture-schema-freeze CD5 A3 と同様の注意)。
    pub manual_insert_chars: u64,
    /// external_paste_chars の総和 (capture 済 paste のみ)。
    pub external_paste_chars_total: u64,
    /// `manual / (manual + paste)`。分母 0 → None。
    pub manual_contribution_ratio: Option<f64>,
    /// 回復エピソードのうち「external paste 無し かつ net_diff 正進行」で回復した割合。
    /// 分母 = 回復したエピソード数。回復 0 → None。
    pub productive_manual_recovery_rate: Option<f64>,
    // ── (a) AI依存度 ──
    /// capture 済 external paste (external_paste_chars が Some) の件数。
    pub external_paste_count: u32,
    /// 文字数欠落 (旧 NDJSON, capture-schema-freeze 以前) のため outcome 集計から
    /// 除外した paste の件数。これが大きいセッションは manual_contribution_ratio が
    /// manual 寄りに偏るため、研究者が偏りに気づけるよう数値で残す
    /// (code-reviewer MEDIUM 対応・収集時に算出して付与)。
    pub excluded_paste_count: u32,
    /// `external_paste_chars >= large_threshold` の paste 割合。paste 0 → None。
    pub large_paste_rate: Option<f64>,
    /// エピソード後 after_window 内に paste があったエピソードの割合。episode 0 → None。
    pub paste_after_stuck_rate: Option<f64>,
    /// 回復窓内に paste 無しで回復したエピソードの割合 (分母 = 全エピソード)。episode 0 → None。
    pub self_recovery_without_paste: Option<f64>,
    /// 補助指標: 1 時間あたりの external paste 回数。span 0 → None。
    pub paste_count_per_hour: Option<f64>,
    // ── 透明性のための内訳 ──
    pub stuck_episode_count: u32,
    pub recovered_episode_count: u32,
}

/// vk コードが「文字生成キー」(印字可能文字を生む) かを content-free に判定する。
/// Windows VK 規約 (macOS はフック層で変換済み)。Unicode 内容には一切触れない。
/// 含む: 英数 (0x30-0x39, 0x41-0x5A) / Space / Enter / Tab / テンキー (0x60-0x6F) /
/// OEM 句読点 (0xBA-0xC0, 0xDB-0xDF, 0xE2)。除外: 修飾・ナビゲーション・ファンクション・
/// backspace/delete。エピソード/比率の分子分母を安定させるための保守的集合
/// (`.steering/20260623-outcome-metrics/decisions.md` CD-OM2)。
pub fn is_text_producing(vk: u32) -> bool {
    matches!(vk,
        0x30..=0x39   // '0'-'9'
        | 0x41..=0x5A // 'A'-'Z'
        | 0x20        // VK_SPACE
        | 0x0D        // VK_RETURN (改行も文字)
        | 0x09        // VK_TAB
        | 0x60..=0x6F // テンキー 0-9 と * + . - / separator
        | 0xBA..=0xC0 // OEM_1..OEM_3 (; = , - . / `)
        | 0xDB..=0xDF // OEM_4..OEM_8 ([ \ ] ')
        | 0xE2        // OEM_102 (\ / <>)
    )
}

/// backspace / delete か (replay.rs `is_backspace` と同義。文字を減らすキー)。
pub fn is_backspace(vk: u32) -> bool {
    vk == 0x08 || vk == 0x2E // VK_BACK / VK_DELETE
}

/// feat 列を Stuck エピソードに分割する。**現状 `PStuckThreshold` のみ実装** している。
/// `feats` は timestamp 昇順を仮定。`merge_gap_ms` 以内の中断は同一エピソードに統合。
///
/// `UserLabel` / `InterventionFired` は feat だけでは判定できず (ラベル時刻列・介入発火列を
/// 要する) 将来拡張のため予約済み。それらが指定された場合は p_stuck の結果を黙って返さず
/// **空を返す** (cross-review AGREE-1: 仕様前走り防止)。トリガ別の時刻列から組む共通部は
/// `episodes_from_sorted_ts` に切り出してあり、将来 `segment_episodes_from_ts(&label_ts, cfg)`
/// 等を足せる。
pub fn segment_stuck_episodes(feats: &[FeatSnapshot], cfg: &OutcomeConfig) -> Vec<StuckEpisode> {
    if cfg.trigger != StuckTrigger::PStuckThreshold {
        return Vec::new();
    }
    let stuck_ts: Vec<u64> = feats
        .iter()
        .filter(|f| f.p_stuck >= cfg.p_stuck_trigger)
        .map(|f| f.timestamp)
        .collect();
    episodes_from_sorted_ts(&stuck_ts, cfg.merge_gap_ms)
}

/// 昇順タイムスタンプ列を merge_gap で統合してエピソード化する (トリガ非依存の共通部)。
fn episodes_from_sorted_ts(sorted_ts: &[u64], merge_gap_ms: u64) -> Vec<StuckEpisode> {
    let mut episodes = Vec::new();
    let mut iter = sorted_ts.iter().copied();
    if let Some(first) = iter.next() {
        let mut start = first;
        let mut prev = first;
        for ts in iter {
            if ts.saturating_sub(prev) <= merge_gap_ms {
                prev = ts;
            } else {
                episodes.push(StuckEpisode {
                    start_ms: start,
                    end_ms: prev,
                });
                start = ts;
                prev = ts;
            }
        }
        episodes.push(StuckEpisode {
            start_ms: start,
            end_ms: prev,
        });
    }
    episodes
}

/// 窓 `[lo, hi]` 内の manual_insert_chars 純増 = 文字生成キー press − backspace press
/// (0 下限)。content-free。
fn manual_insert_chars_in(keys: &[KeyPress], lo: u64, hi: u64) -> u64 {
    let mut text = 0u64;
    let mut back = 0u64;
    for k in keys {
        if k.timestamp >= lo && k.timestamp <= hi {
            if is_backspace(k.vk) {
                back += 1;
            } else if is_text_producing(k.vk) {
                text += 1;
            }
        }
    }
    text.saturating_sub(back)
}

/// 窓 `[lo, hi]` 内に paste が 1 件以上あるか。
fn has_paste_in(pastes: &[PasteEvent], lo: u64, hi: u64) -> bool {
    pastes
        .iter()
        .any(|p| p.timestamp >= lo && p.timestamp <= hi)
}

/// v0.4 アウトカム指標を算出する純粋関数。
/// `feats` は回復判定 (p_flow>0.5) と session span に使う。`episodes` は
/// `segment_stuck_episodes` 等で得た Stuck 候補区間。すべて timestamp 昇順を仮定。
pub fn compute_outcome_metrics(
    episodes: &[StuckEpisode],
    pastes: &[PasteEvent],
    keys: &[KeyPress],
    feats: &[FeatSnapshot],
    cfg: &OutcomeConfig,
) -> OutcomeMetrics {
    // (b) セッション全体の manual_insert_chars / paste 総和。
    // 破損/巨大値での u64 wrap を防ぐため saturating で畳む (cross-review CLAUDE-1)。
    let manual_insert_chars = manual_insert_chars_in(keys, u64::MIN, u64::MAX);
    let external_paste_chars_total: u64 = pastes
        .iter()
        .fold(0u64, |acc, p| acc.saturating_add(p.chars));
    let denom = manual_insert_chars.saturating_add(external_paste_chars_total);
    let manual_contribution_ratio = if denom > 0 {
        Some(manual_insert_chars as f64 / denom as f64)
    } else {
        None
    };

    // (a) paste 集計
    let external_paste_count = pastes.len() as u32;
    let large_paste_count = pastes
        .iter()
        .filter(|p| p.chars >= cfg.large_threshold)
        .count() as u32;
    let large_paste_rate = ratio(large_paste_count, external_paste_count);

    // エピソード単位の集計
    let episode_count = episodes.len() as u32;
    let mut paste_after_stuck = 0u32;
    let mut self_recovery_no_paste = 0u32;
    let mut recovered_count = 0u32;
    let mut productive_recovery = 0u32;

    for ep in episodes {
        // after_stuck 窓内の paste
        if has_paste_in(
            pastes,
            ep.end_ms,
            ep.end_ms.saturating_add(cfg.after_window_ms),
        ) {
            paste_after_stuck += 1;
        }

        // 回復 (p_flow>0.5) を end_ms 以降 recovery_window 内に探す (既存プリミティブ再利用)
        if let Some(rec_ts) = compute_recovered_at(
            ep.end_ms,
            feats,
            cfg.recovery_window_ms,
            DEFAULT_P_FLOW_THRESHOLD,
        ) {
            recovered_count += 1;
            // 回復までの間 [end_ms, rec_ts] に paste が無いか
            let no_paste = !has_paste_in(pastes, ep.end_ms, rec_ts);
            if no_paste {
                self_recovery_no_paste += 1;
                // net_diff 正進行 (manual 純増 >= net_diff_min) かつ paste 無し
                if manual_insert_chars_in(keys, ep.end_ms, rec_ts) >= cfg.net_diff_min {
                    productive_recovery += 1;
                }
            }
        }
    }

    let paste_after_stuck_rate = ratio(paste_after_stuck, episode_count);
    let self_recovery_without_paste = ratio(self_recovery_no_paste, episode_count);
    let productive_manual_recovery_rate = ratio(productive_recovery, recovered_count);

    // 補助: paste_count_per_hour (feat 列の span をセッション時間とみなす)
    let paste_count_per_hour = match (feats.first(), feats.last()) {
        (Some(f0), Some(f1)) if f1.timestamp > f0.timestamp => {
            let hours = (f1.timestamp - f0.timestamp) as f64 / 3_600_000.0;
            if hours > 0.0 {
                Some(external_paste_count as f64 / hours)
            } else {
                None
            }
        }
        _ => None,
    };

    OutcomeMetrics {
        manual_insert_chars,
        external_paste_chars_total,
        manual_contribution_ratio,
        productive_manual_recovery_rate,
        external_paste_count,
        // 収集時にしか分からないため compute では 0。`--metrics` 経路 (replay.rs) が
        // collect_paste_events の戻り値で上書きする。
        excluded_paste_count: 0,
        large_paste_rate,
        paste_after_stuck_rate,
        self_recovery_without_paste,
        paste_count_per_hour,
        stuck_episode_count: episode_count,
        recovered_episode_count: recovered_count,
    }
}

/// `num / den` を比率で返す。den == 0 → None (NaN を出さない)。
fn ratio(num: u32, den: u32) -> Option<f64> {
    if den > 0 {
        Some(num as f64 / den as f64)
    } else {
        None
    }
}

/// Option<f64> の比率を pretty 出力用に整形 (None → "n/a")。
fn fmt_opt_ratio(v: Option<f64>) -> String {
    v.map(|x| format!("{:.3}", x))
        .unwrap_or_else(|| "n/a".to_string())
}

/// Stuck ラベル時刻以降、`p_flow > threshold` に達する最初の FeatSnapshot 時刻を返す。
/// `window_ms` 以内に到達しなければ `None`。
pub fn compute_recovered_at(
    stuck_ts: u64,
    feats: &[FeatSnapshot],
    window_ms: u64,
    p_flow_threshold: f64,
) -> Option<u64> {
    let deadline = stuck_ts.saturating_add(window_ms);
    feats
        .iter()
        .filter(|f| f.timestamp >= stuck_ts && f.timestamp <= deadline)
        .find(|f| f.p_flow > p_flow_threshold)
        .map(|f| f.timestamp)
}

/// 混同行列 / per-class F1 / 中央値を算出する主関数。
///
/// `labels` と `feats` はともに timestamp 昇順を仮定（未ソートでも概ね動くが、
/// 連続 Stuck の扱いなどは順序依存のため呼び出し側で整えること）。
pub fn compute_session_metrics(
    labels: &[UserLabelEvent],
    feats: &[FeatSnapshot],
) -> SessionMetrics {
    let mut warnings: Vec<String> = Vec::new();
    let mut confusion = [[0u32; 3]; 3];
    let mut leads: Vec<i64> = Vec::new();
    let mut recoveries: Vec<u64> = Vec::new();

    if labels.is_empty() {
        warnings.push("no user_label entries found".to_string());
    }
    if feats.is_empty() && !labels.is_empty() {
        warnings.push("no feat snapshots found".to_string());
    }

    for lbl in labels {
        match nearest_feat(lbl.timestamp, feats, LABEL_MATCH_WINDOW_MS) {
            Some(f) => {
                let predicted = argmax_class(f);
                confusion[lbl.label.index()][predicted.index()] += 1;
            }
            None => {
                warnings.push(format!(
                    "label at t={} has no FeatSnapshot within ±{}ms",
                    lbl.timestamp, LABEL_MATCH_WINDOW_MS
                ));
            }
        }

        if let Some(lead_ms) = detection_lead_ms(lbl, feats, LEAD_LAG_WINDOW_MS) {
            leads.push(lead_ms);
        }

        if lbl.label == LabelClass::Stuck {
            if let Some(rec_ts) = compute_recovered_at(
                lbl.timestamp,
                feats,
                DEFAULT_RECOVERY_WINDOW_MS,
                DEFAULT_P_FLOW_THRESHOLD,
            ) {
                recoveries.push(rec_ts.saturating_sub(lbl.timestamp));
            }
        }
    }

    let per_class = [
        per_class_metrics(LabelClass::Flow, &confusion),
        per_class_metrics(LabelClass::Incubation, &confusion),
        per_class_metrics(LabelClass::Stuck, &confusion),
    ];

    // scikit-learn 互換の macro F1: 固定分母 3 で平均。support=0 のクラスは
    // per_class_metrics() が precision=recall=f1=0.0 を返すので、そのまま加算。
    // こうすることでセッション間比較時に分母が変動しない（D3 の通り）。
    let macro_f1 = per_class.iter().map(|c| c.f1).sum::<f64>() / per_class.len() as f64;

    let micro_f1 = compute_micro_f1(&confusion);

    let total_labels = labels.len() as u32;

    SessionMetrics {
        total_labels,
        confusion: ConfusionMatrix { matrix: confusion },
        per_class,
        macro_f1,
        micro_f1,
        detection_lead_ms_median: median_i64(&mut leads),
        stuck_recovery_ms_median: median_u64(&mut recoveries),
        // outcome は key/paste 行を要するため compute_session_metrics では計算しない。
        // `--metrics` 経路 (replay.rs) が compute_outcome_metrics の結果を後から付与する。
        outcome: None,
        warnings,
    }
}

/// pretty-print 出力を生成（`--metrics` サブコマンドで使う）。
pub fn format_pretty(m: &SessionMetrics) -> String {
    let mut out = String::new();
    let (n_flow, n_inc, n_stuck) = (
        m.per_class[0].support,
        m.per_class[1].support,
        m.per_class[2].support,
    );
    out.push_str("SessionMetrics\n");
    out.push_str(&format!(
        "  Total labels: {} (Flow:{}, Inc:{}, Stuck:{})\n",
        m.total_labels, n_flow, n_inc, n_stuck
    ));
    out.push_str(&format!("  Macro F1: {:.3}\n", m.macro_f1));
    out.push_str(&format!("  Micro F1: {:.3}\n", m.micro_f1));
    out.push_str("  Per-class:\n");
    for c in &m.per_class {
        out.push_str(&format!(
            "    {:10} P={:.3}  R={:.3}  F1={:.3}  support={}\n",
            c.class.as_str(),
            c.precision,
            c.recall,
            c.f1,
            c.support,
        ));
    }
    out.push_str("  Confusion (rows = truth, cols = pred):\n");
    out.push_str("                Flow   Inc    Stuck\n");
    for (i, row) in m.confusion.matrix.iter().enumerate() {
        out.push_str(&format!(
            "    {:10}  {:>4}  {:>4}   {:>4}\n",
            CLASSES[i].as_str(),
            row[0],
            row[1],
            row[2],
        ));
    }
    match m.detection_lead_ms_median {
        Some(v) => out.push_str(&format!(
            "  Detection lead median: {:+} ms  (positive = HMM leads user)\n",
            v
        )),
        None => out.push_str("  Detection lead median: n/a\n"),
    }
    match m.stuck_recovery_ms_median {
        Some(v) => out.push_str(&format!("  Stuck recovery median: {} ms\n", v)),
        None => out.push_str("  Stuck recovery median: n/a\n"),
    }
    if let Some(o) = &m.outcome {
        out.push_str("  Outcome metrics (v0.4):\n");
        out.push_str(&format!(
            "    Stuck episodes: {} (recovered: {})\n",
            o.stuck_episode_count, o.recovered_episode_count
        ));
        out.push_str(&format!(
            "    manual_insert_chars: {}  external_paste_chars: {}  external_paste_count: {} (excluded: {})\n",
            o.manual_insert_chars, o.external_paste_chars_total, o.external_paste_count, o.excluded_paste_count
        ));
        out.push_str(&format!(
            "    manual_contribution_ratio: {}\n",
            fmt_opt_ratio(o.manual_contribution_ratio)
        ));
        out.push_str(&format!(
            "    productive_manual_recovery_rate: {}\n",
            fmt_opt_ratio(o.productive_manual_recovery_rate)
        ));
        out.push_str(&format!(
            "    self_recovery_without_paste: {}  paste_after_stuck_rate: {}\n",
            fmt_opt_ratio(o.self_recovery_without_paste),
            fmt_opt_ratio(o.paste_after_stuck_rate)
        ));
        out.push_str(&format!(
            "    large_paste_rate: {}  paste_count_per_hour: {}\n",
            fmt_opt_ratio(o.large_paste_rate),
            o.paste_count_per_hour
                .map(|v| format!("{:.2}", v))
                .unwrap_or_else(|| "n/a".to_string())
        ));
    }
    out.push_str(&format!("  Warnings: {}\n", m.warnings.len()));
    for w in &m.warnings {
        out.push_str(&format!("    - {}\n", w));
    }
    out
}

// --- internal helpers -----------------------------------------------------

fn nearest_feat<'a>(
    ts: u64,
    feats: &'a [FeatSnapshot],
    window_ms: u64,
) -> Option<&'a FeatSnapshot> {
    feats
        .iter()
        .filter(|f| abs_diff(f.timestamp, ts) <= window_ms)
        .min_by_key(|f| abs_diff(f.timestamp, ts))
}

fn abs_diff(a: u64, b: u64) -> u64 {
    if a >= b {
        a - b
    } else {
        b - a
    }
}

/// HMM argmax 付与。タイブレークは Flow > Incubation > Stuck の固定順（稀だが発生しうる）。
fn argmax_class(f: &FeatSnapshot) -> LabelClass {
    if f.p_flow >= f.p_inc && f.p_flow >= f.p_stuck {
        LabelClass::Flow
    } else if f.p_inc >= f.p_stuck {
        LabelClass::Incubation
    } else {
        LabelClass::Stuck
    }
}

/// ラベル周辺 ±window_ms の FeatSnapshot を走査し、
/// ラベルと同じクラスが argmax になった中で **ラベル時刻に最も近い** feat を返す。
/// 戻り値 = label_ts - feat_ts (正 = HMM がラベルより先行 / 負 = 遅延)。
///
/// 初版は `find()` で先頭ヒット (窓内の最小 timestamp) を拾っていたが、
/// それはラベルから遠い偶発的な同クラス出現を拾う問題があった。
/// 実データ (gse_20260415_080214) で lead 中央値が +50s と窓端付近に貼り付き、
/// M1 指摘として顕在化。`min_by_key(abs_diff)` に変更して「ラベル時刻に最も近い
/// 同クラス feat」に再定義する (2026-04-15, decisions.md D9)。
fn detection_lead_ms(lbl: &UserLabelEvent, feats: &[FeatSnapshot], window_ms: u64) -> Option<i64> {
    let lo = lbl.timestamp.saturating_sub(window_ms);
    let hi = lbl.timestamp.saturating_add(window_ms);
    let hit = feats
        .iter()
        .filter(|f| f.timestamp >= lo && f.timestamp <= hi)
        .filter(|f| argmax_class(f) == lbl.label)
        .min_by_key(|f| abs_diff(f.timestamp, lbl.timestamp))?;
    // 正 = HMM がラベルより先行 (feat が早い → label_ts - feat_ts が正)。
    Some(lbl.timestamp as i64 - hit.timestamp as i64)
}

fn per_class_metrics(class: LabelClass, cm: &[[u32; 3]; 3]) -> ClassMetrics {
    let i = class.index();
    let tp = cm[i][i] as f64;
    let fp: f64 = (0..3).filter(|&j| j != i).map(|j| cm[j][i] as f64).sum();
    let fn_: f64 = (0..3).filter(|&j| j != i).map(|j| cm[i][j] as f64).sum();
    let support = (0..3).map(|j| cm[i][j]).sum::<u32>();
    let precision = if tp + fp > 0.0 { tp / (tp + fp) } else { 0.0 };
    let recall = if tp + fn_ > 0.0 { tp / (tp + fn_) } else { 0.0 };
    let f1 = if precision + recall > 0.0 {
        2.0 * precision * recall / (precision + recall)
    } else {
        0.0
    };
    ClassMetrics {
        class,
        precision,
        recall,
        f1,
        support,
    }
}

/// 多クラスの micro F1 = micro precision = micro recall = accuracy。
///
/// **分母**: 混同行列の合計 = `nearest_feat` でマッチしたラベル数のみ。
/// ラベル近傍に FeatSnapshot が無く warnings に落ちたラベルは含まれない。
/// マッチ率が低いセッションでは `total_labels` より小さな分母になる点に注意
/// （`baseline_metrics.md` では warnings 件数を併記して判断する）。
fn compute_micro_f1(cm: &[[u32; 3]; 3]) -> f64 {
    let tp: u32 = (0..3).map(|i| cm[i][i]).sum();
    let total: u32 = cm.iter().flatten().sum();
    if total == 0 {
        0.0
    } else {
        tp as f64 / total as f64
    }
}

fn median_i64(values: &mut [i64]) -> Option<i64> {
    if values.is_empty() {
        return None;
    }
    values.sort_unstable();
    let mid = values.len() / 2;
    if values.len() % 2 == 0 {
        // i64 加算のオーバーフロー回避のため i128 経由で計算。
        // (両端が i64::MIN と i64::MAX の両立は LEAD_LAG_WINDOW_MS=60_000
        // で現実には起きないが、関数契約として安全側に倒す)
        let a = values[mid - 1] as i128;
        let b = values[mid] as i128;
        Some(((a + b) / 2) as i64)
    } else {
        Some(values[mid])
    }
}

fn median_u64(values: &mut [u64]) -> Option<u64> {
    if values.is_empty() {
        return None;
    }
    values.sort_unstable();
    let mid = values.len() / 2;
    if values.len() % 2 == 0 {
        // sort 後なので a <= b、`a + (b - a) / 2` は u64 でも overflow しない。
        let a = values[mid - 1];
        let b = values[mid];
        Some(a + (b - a) / 2)
    } else {
        Some(values[mid])
    }
}

// ── Range-based labeling (Phase 1 GT 改善) ────────────────────────────

/// 範囲ラベル: セグメント [start_ms, end_ms] に対するラベル。
/// 区間内の全 FeatSnapshot と比較することで、1 ラベルから多数の
/// feat-label ペアが生成され、統計検出力が大幅に向上する。
#[derive(Debug, Clone, Copy)]
pub struct RangeLabel {
    pub start_ms: u64,
    pub end_ms: u64,
    pub label: LabelClass,
}

/// 範囲ラベルを用いたメトリクス算出。
///
/// 各 RangeLabel の [start, end] 区間内に含まれる全 feat に対して
/// argmax を取り、confusion matrix を構築する。
/// detection_lead / stuck_recovery は範囲ラベルでは算出しない
/// (区間全体がラベルなので「検出タイミング」の概念がない)。
pub fn compute_range_metrics(
    range_labels: &[RangeLabel],
    feats: &[FeatSnapshot],
) -> SessionMetrics {
    let mut warnings: Vec<String> = Vec::new();
    let mut confusion = [[0u32; 3]; 3];
    let mut total_segments = 0u32;

    if range_labels.is_empty() {
        warnings.push("no range labels found".to_string());
    }
    if feats.is_empty() && !range_labels.is_empty() {
        warnings.push("no feat snapshots found".to_string());
    }

    for rl in range_labels {
        let feats_in_range: Vec<&FeatSnapshot> = feats
            .iter()
            .filter(|f| f.timestamp >= rl.start_ms && f.timestamp <= rl.end_ms)
            .collect();

        if feats_in_range.is_empty() {
            warnings.push(format!(
                "segment [{}, {}] has no FeatSnapshot",
                rl.start_ms, rl.end_ms,
            ));
            continue;
        }

        for f in &feats_in_range {
            let predicted = argmax_class(f);
            confusion[rl.label.index()][predicted.index()] += 1;
        }
        total_segments += 1;
    }

    let per_class = [
        per_class_metrics(LabelClass::Flow, &confusion),
        per_class_metrics(LabelClass::Incubation, &confusion),
        per_class_metrics(LabelClass::Stuck, &confusion),
    ];

    let macro_f1 = per_class.iter().map(|c| c.f1).sum::<f64>() / per_class.len() as f64;
    let micro_f1 = compute_micro_f1(&confusion);

    SessionMetrics {
        total_labels: total_segments,
        confusion: ConfusionMatrix { matrix: confusion },
        per_class,
        macro_f1,
        micro_f1,
        detection_lead_ms_median: None,
        stuck_recovery_ms_median: None,
        outcome: None,
        warnings,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn feat(timestamp: u64, p_flow: f64, p_inc: f64, p_stuck: f64) -> FeatSnapshot {
        FeatSnapshot {
            timestamp,
            f1: 0.0,
            f3: 0.0,
            f4: 0.0,
            f5: 0.0,
            f6: 0.0,
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

    #[test]
    fn recovered_at_returns_first_qualifying_timestamp() {
        let feats = vec![
            feat(1000, 0.1, 0.2, 0.7),
            feat(2000, 0.3, 0.3, 0.4),
            feat(3000, 0.6, 0.3, 0.1), // p_flow > 0.5
            feat(4000, 0.9, 0.05, 0.05),
        ];
        let got = compute_recovered_at(1000, &feats, 60_000, 0.5);
        assert_eq!(got, Some(3000));
    }

    #[test]
    fn recovered_at_respects_window_deadline() {
        let feats = vec![
            feat(1000, 0.1, 0.2, 0.7),
            feat(1500, 0.1, 0.2, 0.7),
            feat(60_000, 0.9, 0.05, 0.05), // 窓(1000+5000=6000) 外
        ];
        let got = compute_recovered_at(1000, &feats, 5_000, 0.5);
        assert_eq!(got, None);
    }

    #[test]
    fn recovered_at_handles_consecutive_stucks() {
        // 1 つ目の Stuck (t=1000) は t=3000 で回復、2 つ目の Stuck (t=5000)
        // もそれぞれ独立に評価される（本関数は Stuck ごとに呼ぶ前提）。
        let feats = vec![
            feat(1000, 0.1, 0.2, 0.7),
            feat(3000, 0.8, 0.1, 0.1),
            feat(5000, 0.2, 0.2, 0.6),
            feat(7000, 0.7, 0.2, 0.1),
        ];
        assert_eq!(compute_recovered_at(1000, &feats, 60_000, 0.5), Some(3000));
        assert_eq!(compute_recovered_at(5000, &feats, 60_000, 0.5), Some(7000));
    }

    #[test]
    fn recovered_at_returns_none_on_empty_feats() {
        assert_eq!(compute_recovered_at(1000, &[], 60_000, 0.5), None);
    }

    #[test]
    fn session_metrics_all_correct_gives_f1_one() {
        let labels = vec![
            UserLabelEvent {
                timestamp: 1000,
                label: LabelClass::Flow,
            },
            UserLabelEvent {
                timestamp: 2000,
                label: LabelClass::Incubation,
            },
            UserLabelEvent {
                timestamp: 3000,
                label: LabelClass::Stuck,
            },
        ];
        let feats = vec![
            feat(1000, 0.9, 0.05, 0.05),
            feat(2000, 0.2, 0.7, 0.1),
            feat(3000, 0.1, 0.2, 0.7),
        ];
        let m = compute_session_metrics(&labels, &feats);
        assert_eq!(m.total_labels, 3);
        assert!((m.macro_f1 - 1.0).abs() < 1e-9);
        assert!((m.micro_f1 - 1.0).abs() < 1e-9);
        assert_eq!(m.confusion.matrix[0][0], 1);
        assert_eq!(m.confusion.matrix[1][1], 1);
        assert_eq!(m.confusion.matrix[2][2], 1);
    }

    #[test]
    fn session_metrics_all_inverted_gives_zero_f1() {
        // 正解 Flow だが HMM は Stuck、など全部誤答
        let labels = vec![
            UserLabelEvent {
                timestamp: 1000,
                label: LabelClass::Flow,
            },
            UserLabelEvent {
                timestamp: 2000,
                label: LabelClass::Stuck,
            },
        ];
        let feats = vec![feat(1000, 0.05, 0.05, 0.9), feat(2000, 0.9, 0.05, 0.05)];
        let m = compute_session_metrics(&labels, &feats);
        assert!((m.macro_f1 - 0.0).abs() < 1e-9);
        assert!((m.micro_f1 - 0.0).abs() < 1e-9);
    }

    #[test]
    fn session_metrics_empty_labels_yields_warning_no_panic() {
        let feats = vec![feat(1000, 0.9, 0.05, 0.05)];
        let m = compute_session_metrics(&[], &feats);
        assert_eq!(m.total_labels, 0);
        assert_eq!(m.macro_f1, 0.0);
        assert_eq!(m.micro_f1, 0.0);
        assert!(m.warnings.iter().any(|w| w.contains("no user_label")));
        assert!(m.detection_lead_ms_median.is_none());
        assert!(m.stuck_recovery_ms_median.is_none());
    }

    #[test]
    fn session_metrics_timestamp_mismatch_adds_warning() {
        let labels = vec![UserLabelEvent {
            timestamp: 1000,
            label: LabelClass::Flow,
        }];
        // 最近傍 feat が 5s 離れており LABEL_MATCH_WINDOW_MS(1s) 超過
        let feats = vec![feat(6000, 0.9, 0.05, 0.05)];
        let m = compute_session_metrics(&labels, &feats);
        assert!(m
            .warnings
            .iter()
            .any(|w| w.contains("no FeatSnapshot within")));
        // 混同行列には計上されない
        assert_eq!(m.confusion.matrix.iter().flatten().sum::<u32>(), 0);
    }

    #[test]
    fn detection_lead_positive_when_hmm_leads() {
        // ラベル t=5000。ラベル時刻の feat は Flow で不一致、同クラス (Stuck) argmax
        // は t=3000 のみ → HMM が 2000ms 先行 → +2000
        let labels = vec![UserLabelEvent {
            timestamp: 5000,
            label: LabelClass::Stuck,
        }];
        let feats = vec![
            feat(3000, 0.1, 0.2, 0.7),   // Stuck (同クラス)
            feat(5000, 0.9, 0.05, 0.05), // Flow (不一致)
        ];
        let m = compute_session_metrics(&labels, &feats);
        assert_eq!(m.detection_lead_ms_median, Some(2000));
    }

    #[test]
    fn stuck_recovery_median_only_counts_recovered_events() {
        let labels = vec![
            UserLabelEvent {
                timestamp: 1000,
                label: LabelClass::Stuck,
            },
            UserLabelEvent {
                timestamp: 100_000,
                label: LabelClass::Stuck,
            },
        ];
        let feats = vec![
            feat(1000, 0.1, 0.2, 0.7),
            feat(2000, 0.6, 0.3, 0.1), // 1秒で回復
            feat(100_000, 0.1, 0.2, 0.7),
            // 2 つ目は回復なし
        ];
        let m = compute_session_metrics(&labels, &feats);
        assert_eq!(m.stuck_recovery_ms_median, Some(1000));
    }

    #[test]
    fn label_class_parse() {
        assert_eq!(LabelClass::parse("flow"), Some(LabelClass::Flow));
        assert_eq!(
            LabelClass::parse("incubation"),
            Some(LabelClass::Incubation)
        );
        assert_eq!(LabelClass::parse("stuck"), Some(LabelClass::Stuck));
        assert_eq!(LabelClass::parse("FLOW"), None);
        assert_eq!(LabelClass::parse(""), None);
    }

    #[test]
    fn detection_lead_picks_nearest_not_first() {
        // ラベル t=5000、窓内に同クラス argmax が 3 点 (t=1000/4800/60000)。
        // 旧実装は t=1000 (先頭ヒット) を拾い lead=+4000 と過大評価。
        // 新実装は t=4800 (abs_diff=200) を選び lead=+200。
        let labels = vec![UserLabelEvent {
            timestamp: 5000,
            label: LabelClass::Stuck,
        }];
        let feats = vec![
            feat(1000, 0.1, 0.2, 0.7),
            feat(4800, 0.1, 0.2, 0.7),
            feat(60_000, 0.1, 0.2, 0.7),
        ];
        let m = compute_session_metrics(&labels, &feats);
        assert_eq!(m.detection_lead_ms_median, Some(200));
    }

    #[test]
    fn argmax_tiebreak_prefers_flow_then_incubation() {
        // [0.4, 0.4, 0.2]: Flow と Inc が同率 → Flow 優先 (D2)
        let labels = vec![UserLabelEvent {
            timestamp: 1000,
            label: LabelClass::Flow,
        }];
        let feats = vec![feat(1000, 0.4, 0.4, 0.2)];
        let m = compute_session_metrics(&labels, &feats);
        assert_eq!(m.confusion.matrix[0][0], 1); // 正解 Flow, 推定 Flow

        // [0.1, 0.45, 0.45]: Inc と Stuck が同率 → Inc 優先 (D2)
        let labels2 = vec![UserLabelEvent {
            timestamp: 1000,
            label: LabelClass::Incubation,
        }];
        let feats2 = vec![feat(1000, 0.1, 0.45, 0.45)];
        let m2 = compute_session_metrics(&labels2, &feats2);
        assert_eq!(m2.confusion.matrix[1][1], 1); // 正解 Inc, 推定 Inc
    }

    #[test]
    fn per_class_handles_tp_fp_zero_without_nan() {
        // Flow のラベルは 1 件だが HMM が Stuck と誤判定 →
        //   Flow: tp=0, fp=0 (推定 Flow が 0 件), fn=1 → precision=0, recall=0
        //   Stuck: tp=0, fp=1 (正解 Stuck が 0 件), fn=0 → precision=0, recall=0
        let labels = vec![UserLabelEvent {
            timestamp: 1000,
            label: LabelClass::Flow,
        }];
        let feats = vec![feat(1000, 0.1, 0.1, 0.8)];
        let m = compute_session_metrics(&labels, &feats);
        for c in &m.per_class {
            assert!(!c.precision.is_nan());
            assert!(!c.recall.is_nan());
            assert!(!c.f1.is_nan());
            assert_eq!(c.f1, 0.0);
        }
        assert!(!m.macro_f1.is_nan());
        assert!(!m.micro_f1.is_nan());
    }

    #[test]
    fn format_pretty_produces_expected_structure() {
        let labels = vec![UserLabelEvent {
            timestamp: 1000,
            label: LabelClass::Flow,
        }];
        let feats = vec![feat(1000, 0.9, 0.05, 0.05)];
        let m = compute_session_metrics(&labels, &feats);
        let s = format_pretty(&m);
        assert!(s.contains("SessionMetrics"));
        assert!(s.contains("Total labels: 1"));
        assert!(s.contains("Confusion"));
        assert!(s.contains("Warnings: 0"));
    }

    // ── v0.4 Outcome metrics tests ───────────────────────────────────

    fn kp(timestamp: u64, vk: u32) -> KeyPress {
        KeyPress { timestamp, vk }
    }
    fn pe(timestamp: u64, chars: u64) -> PasteEvent {
        PasteEvent { timestamp, chars }
    }

    #[test]
    fn text_producing_and_backspace_classification() {
        assert!(is_text_producing(0x41)); // 'A'
        assert!(is_text_producing(0x30)); // '0'
        assert!(is_text_producing(0x20)); // Space
        assert!(is_text_producing(0xBC)); // OEM_COMMA
        assert!(!is_text_producing(0x08)); // Backspace は文字生成ではない
        assert!(!is_text_producing(0x10)); // Shift (修飾)
        assert!(!is_text_producing(0x25)); // Left arrow (ナビゲーション)
        assert!(is_backspace(0x08)); // VK_BACK
        assert!(is_backspace(0x2E)); // VK_DELETE
        assert!(!is_backspace(0x41));
    }

    #[test]
    fn segment_merges_within_gap_and_splits_beyond() {
        let cfg = OutcomeConfig {
            merge_gap_ms: 30_000,
            ..OutcomeConfig::default()
        };
        // stuck @1000,2000,3000 (連続) → 1 エピソード。@100_000 は gap>30s → 別エピソード。
        let feats = vec![
            feat(1000, 0.1, 0.2, 0.7),
            feat(2000, 0.1, 0.2, 0.7),
            feat(3000, 0.1, 0.2, 0.7),
            feat(5000, 0.8, 0.1, 0.1), // not stuck (dip < gap, absorbed only if両端 stuck)
            feat(100_000, 0.1, 0.2, 0.7),
        ];
        let eps = segment_stuck_episodes(&feats, &cfg);
        assert_eq!(eps.len(), 2);
        assert_eq!(
            eps[0],
            StuckEpisode {
                start_ms: 1000,
                end_ms: 3000
            }
        );
        assert_eq!(
            eps[1],
            StuckEpisode {
                start_ms: 100_000,
                end_ms: 100_000
            }
        );
    }

    #[test]
    fn segment_absorbs_short_dip_within_gap() {
        let cfg = OutcomeConfig {
            merge_gap_ms: 30_000,
            ..OutcomeConfig::default()
        };
        // stuck @1000, dip @2000(not stuck), stuck @3000。stuck 間隙 2000ms <= gap → 統合。
        let feats = vec![
            feat(1000, 0.1, 0.2, 0.7),
            feat(2000, 0.8, 0.1, 0.1),
            feat(3000, 0.1, 0.2, 0.7),
        ];
        let eps = segment_stuck_episodes(&feats, &cfg);
        assert_eq!(eps.len(), 1);
        assert_eq!(
            eps[0],
            StuckEpisode {
                start_ms: 1000,
                end_ms: 3000
            }
        );
    }

    #[test]
    fn manual_insert_chars_nets_backspace_and_floors_at_zero() {
        // 文字3 - backspace1 = 2
        let keys = vec![kp(1, 0x41), kp(2, 0x42), kp(3, 0x43), kp(4, 0x08)];
        assert_eq!(manual_insert_chars_in(&keys, u64::MIN, u64::MAX), 2);
        // backspace 過多でも 0 下限 (NaN/underflow 無し)
        let keys2 = vec![kp(1, 0x41), kp(2, 0x08), kp(3, 0x08)];
        assert_eq!(manual_insert_chars_in(&keys2, u64::MIN, u64::MAX), 0);
        // 修飾キーは数えない
        let keys3 = vec![kp(1, 0x10), kp(2, 0x11), kp(3, 0x41)];
        assert_eq!(manual_insert_chars_in(&keys3, u64::MIN, u64::MAX), 1);
    }

    #[test]
    fn segment_reserved_trigger_returns_empty_not_pstuck() {
        // UserLabel / InterventionFired は未実装 → p_stuck の結果を黙って返さず空 (AGREE-1)。
        let feats = vec![feat(1000, 0.1, 0.2, 0.7), feat(2000, 0.1, 0.2, 0.7)];
        for trigger in [StuckTrigger::UserLabel, StuckTrigger::InterventionFired] {
            let cfg = OutcomeConfig {
                trigger,
                ..OutcomeConfig::default()
            };
            assert!(
                segment_stuck_episodes(&feats, &cfg).is_empty(),
                "reserved trigger {trigger:?} must not masquerade as p_stuck episodes"
            );
        }
        // 既定 (PStuckThreshold) は従来通りエピソードを返す
        let cfg = OutcomeConfig::default();
        assert_eq!(segment_stuck_episodes(&feats, &cfg).len(), 1);
    }

    #[test]
    fn outcome_paste_chars_total_saturates_no_overflow() {
        // 破損 NDJSON 由来の巨大 chars でも wrap せず None/誤正値を出さない (CLAUDE-1)。
        let cfg = OutcomeConfig::default();
        let pastes = vec![pe(1, u64::MAX), pe(2, 100)];
        let o = compute_outcome_metrics(&[], &pastes, &[], &[], &cfg);
        assert_eq!(o.external_paste_chars_total, u64::MAX); // saturated, not wrapped
                                                            // manual=0, paste=MAX → ratio = 0 / MAX = 0.0 (NaN でない)
        let r = o.manual_contribution_ratio.unwrap();
        assert!(!r.is_nan());
        assert!(r.abs() < 1e-9);
    }

    #[test]
    fn outcome_empty_session_no_nan_all_none() {
        let cfg = OutcomeConfig::default();
        let o = compute_outcome_metrics(&[], &[], &[], &[], &cfg);
        assert_eq!(o.manual_insert_chars, 0);
        assert_eq!(o.external_paste_count, 0);
        assert!(o.manual_contribution_ratio.is_none());
        assert!(o.productive_manual_recovery_rate.is_none());
        assert!(o.large_paste_rate.is_none());
        assert!(o.paste_after_stuck_rate.is_none());
        assert!(o.self_recovery_without_paste.is_none());
        assert!(o.paste_count_per_hour.is_none());
        assert_eq!(o.stuck_episode_count, 0);
    }

    #[test]
    fn outcome_self_recovery_without_paste_and_productive() {
        let cfg = OutcomeConfig::default();
        // Stuck @10_000-11_000、その後 manual で打鍵し p_flow>0.5 に回復 (paste 無し)。
        let feats = vec![
            feat(10_000, 0.1, 0.2, 0.7),
            feat(11_000, 0.1, 0.2, 0.7),
            feat(20_000, 0.8, 0.1, 0.1), // 回復 (recovery_window 5分内)
        ];
        let episodes = segment_stuck_episodes(&feats, &cfg);
        assert_eq!(episodes.len(), 1);
        // 回復までの間 (11_000..20_000) に文字キー3つ → net_diff=3 >= 1
        let keys = vec![kp(12_000, 0x41), kp(13_000, 0x42), kp(14_000, 0x43)];
        let o = compute_outcome_metrics(&episodes, &[], &keys, &feats, &cfg);
        assert_eq!(o.stuck_episode_count, 1);
        assert_eq!(o.recovered_episode_count, 1);
        assert_eq!(o.self_recovery_without_paste, Some(1.0));
        assert_eq!(o.productive_manual_recovery_rate, Some(1.0));
        assert_eq!(o.paste_after_stuck_rate, Some(0.0));
        // manual のみ → manual_contribution_ratio = 1.0
        assert_eq!(o.manual_contribution_ratio, Some(1.0));
    }

    #[test]
    fn outcome_paste_in_recovery_window_excludes_self_recovery() {
        let cfg = OutcomeConfig::default();
        let feats = vec![
            feat(10_000, 0.1, 0.2, 0.7),
            feat(11_000, 0.1, 0.2, 0.7),
            feat(20_000, 0.8, 0.1, 0.1), // 回復
        ];
        let episodes = segment_stuck_episodes(&feats, &cfg);
        // 回復までの間に paste (60 chars, large) → self_recovery 不成立・after_stuck 成立
        let pastes = vec![pe(15_000, 60)];
        let keys = vec![kp(16_000, 0x41)];
        let o = compute_outcome_metrics(&episodes, &pastes, &keys, &feats, &cfg);
        assert_eq!(o.recovered_episode_count, 1);
        assert_eq!(o.self_recovery_without_paste, Some(0.0));
        assert_eq!(o.productive_manual_recovery_rate, Some(0.0)); // 回復1・productive0
        assert_eq!(o.paste_after_stuck_rate, Some(1.0)); // end(11_000)+120s 内に paste(15_000)
        assert_eq!(o.external_paste_count, 1);
        assert_eq!(o.large_paste_rate, Some(1.0)); // 60 >= 50
                                                   // manual=1, paste=60 → ratio = 1/61
        let r = o.manual_contribution_ratio.unwrap();
        assert!((r - 1.0 / 61.0).abs() < 1e-9);
    }

    #[test]
    fn outcome_large_paste_rate_threshold_boundary() {
        let cfg = OutcomeConfig::default(); // large_threshold = 50
        let pastes = vec![pe(1, 49), pe(2, 50), pe(3, 100)];
        let o = compute_outcome_metrics(&[], &pastes, &[], &[], &cfg);
        assert_eq!(o.external_paste_count, 3);
        // 50 と 100 が large (>=50) → 2/3
        assert_eq!(o.large_paste_rate, Some(2.0 / 3.0));
        assert_eq!(o.external_paste_chars_total, 199);
    }

    #[test]
    fn outcome_not_recovered_episode_productive_denominator_excludes_it() {
        let cfg = OutcomeConfig::default();
        // Stuck だが回復窓内に p_flow>0.5 が来ない → recovered=0 → productive=None
        let feats = vec![feat(10_000, 0.1, 0.2, 0.7), feat(11_000, 0.1, 0.2, 0.7)];
        let episodes = segment_stuck_episodes(&feats, &cfg);
        assert_eq!(episodes.len(), 1);
        let o = compute_outcome_metrics(&episodes, &[], &[], &feats, &cfg);
        assert_eq!(o.recovered_episode_count, 0);
        assert!(o.productive_manual_recovery_rate.is_none());
        assert_eq!(o.self_recovery_without_paste, Some(0.0)); // 分母=全エピソード1
    }

    // ── RangeLabel / compute_range_metrics tests ────────────────────

    #[test]
    fn range_metrics_counts_all_feats_in_range() {
        let feats = vec![
            feat(1000, 0.9, 0.05, 0.05), // Flow argmax
            feat(2000, 0.8, 0.1, 0.1),   // Flow argmax
            feat(3000, 0.1, 0.6, 0.3),   // Inc argmax
        ];
        let range_labels = vec![RangeLabel {
            start_ms: 1000,
            end_ms: 3000,
            label: LabelClass::Flow,
        }];
        let m = compute_range_metrics(&range_labels, &feats);
        assert_eq!(m.total_labels, 1); // 1 segment
                                       // confusion: Flow truth vs [2 Flow pred, 1 Inc pred, 0 Stuck pred]
        assert_eq!(m.confusion.matrix[0][0], 2); // Flow→Flow
        assert_eq!(m.confusion.matrix[0][1], 1); // Flow→Inc
        assert_eq!(m.confusion.matrix[0][2], 0); // Flow→Stuck
    }

    #[test]
    fn range_metrics_multiple_segments() {
        let feats = vec![
            feat(1000, 0.9, 0.05, 0.05), // Flow
            feat(2000, 0.8, 0.1, 0.1),   // Flow
            feat(5000, 0.1, 0.1, 0.8),   // Stuck
            feat(6000, 0.1, 0.2, 0.7),   // Stuck
        ];
        let range_labels = vec![
            RangeLabel {
                start_ms: 1000,
                end_ms: 2000,
                label: LabelClass::Flow,
            },
            RangeLabel {
                start_ms: 5000,
                end_ms: 6000,
                label: LabelClass::Stuck,
            },
        ];
        let m = compute_range_metrics(&range_labels, &feats);
        assert_eq!(m.total_labels, 2);
        assert_eq!(m.confusion.matrix[0][0], 2); // Flow→Flow correct
        assert_eq!(m.confusion.matrix[2][2], 2); // Stuck→Stuck correct
        assert!(m.micro_f1 > 0.99); // perfect
    }

    #[test]
    fn range_metrics_empty_segment_warns() {
        let feats = vec![feat(1000, 0.9, 0.05, 0.05)];
        let range_labels = vec![RangeLabel {
            start_ms: 5000,
            end_ms: 6000,
            label: LabelClass::Flow,
        }];
        let m = compute_range_metrics(&range_labels, &feats);
        assert_eq!(m.total_labels, 0); // skipped
        assert!(!m.warnings.is_empty());
    }

    #[test]
    fn range_metrics_no_detection_lead() {
        let feats = vec![feat(1000, 0.9, 0.05, 0.05)];
        let range_labels = vec![RangeLabel {
            start_ms: 1000,
            end_ms: 1000,
            label: LabelClass::Flow,
        }];
        let m = compute_range_metrics(&range_labels, &feats);
        assert!(m.detection_lead_ms_median.is_none());
        assert!(m.stuck_recovery_ms_median.is_none());
    }
}
