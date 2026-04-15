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
    pub warnings: Vec<String>,
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
}
