//! Task D (v0.3 較正スモーク): オフライン較正解析。
//!
//! 記録済み NDJSON から抽出した `SessionData` を入力に、時間隔離窓で X(認知摩擦)/Y(エンゲージメント)
//! を集約し、被験者内 方向付き C-index・2段ゲート・MNAR 上下限・ビネット採点・二軸性を算出する。
//! すべて純関数で副作用なし (`analysis/` 純粋性維持・architecture-rules ルール 2/6)。
//!
//! # 方法論の根拠
//!
//! - 時間隔離窓 (t−31s..t−1s): `decisions.md` D-8 / 設計書 §4.2。probe 後 (t..t+60s) は使わない。
//! - 方向付き C-index (`|r|≥0.30` 廃止): D-10 / §7 / PreReg-4。0.5=偶然 / 1.0=完全 / <0.5=逆。
//! - 前向き固定 holdout (先頭2セッション=較正→凍結→残り=評価): D-11 / §8 / PreReg-5。
//! - Recall 点推定は出さない (独立陽性<30件で検出力なし): D-12 / §9 / PreReg-6。
//! - MNAR は除外でなく上下限の範囲報告: D-12 / §10 / PreReg-7。
//! - 既存 `metrics.rs` の confusion/precision/recall は v0.2 流のため**流用しない** (D-14)。
//! - 確証/探索の隔離: `track=exploratory` は主指標に混ぜない (§1.3)。
//!
//! # 責務境界
//!
//! 本モジュールは「1 被験者の複数セッション」を入力に被験者内 C-index/holdout/測定法統計/MNAR/
//! ビネット/二軸性を算出する (`compute_calibration_metrics`)。被験者**横断**の最終ゲート
//! (`model_gate` / `measurement_gate`) は複数被験者が必要なため純関数として提供し、実データの
//! 多被験者オーケストレーション (P000/P001/... 走査) は Task E が担う。

use serde::Serialize;

use crate::analysis::loop_step::FeatSnapshot;

// =============================================================================
// 列挙型 (reader 側ミラー。logger.rs の producer enum とは独立 = metrics.rs::LabelClass と同方針で
//          analysis→logger のレイヤー依存を避ける)
// =============================================================================

/// セッション系列。`main` = 本系列 (主指標)、`exploratory` = 探索系列 (主指標から除外)。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum TrackKind {
    Main,
    Exploratory,
}

impl TrackKind {
    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "main" => Some(Self::Main),
            "exploratory" => Some(Self::Exploratory),
            _ => None,
        }
    }
}

/// `realtime_label` の出所。`random_probe` = 一様ランダム (主データ・C-index/分母の対象)、
/// `self_marker` = ユーザー自発 (副データ・C-index 主指標には混ぜない)。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum ProbeSourceKind {
    RandomProbe,
    SelfMarker,
}

impl ProbeSourceKind {
    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "random_probe" => Some(Self::RandomProbe),
            "self_marker" => Some(Self::SelfMarker),
            _ => None,
        }
    }
}

/// skip 理由。`none` = 回答済み、`dont_remember` = 思い出せない、`dismissed` = 閉じた。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SkipReasonKind {
    None,
    DontRemember,
    Dismissed,
}

impl SkipReasonKind {
    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "none" => Some(Self::None),
            "dont_remember" => Some(Self::DontRemember),
            "dismissed" => Some(Self::Dismissed),
            _ => None,
        }
    }
}

/// (q1,q2) から推論する 2×2 象限 / ビネットの想定象限。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum QuadrantKind {
    Flow,
    Stuck,
    Incubation,
    Idle,
}

impl QuadrantKind {
    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "flow" => Some(Self::Flow),
            "stuck" => Some(Self::Stuck),
            "incubation" => Some(Self::Incubation),
            "idle" => Some(Self::Idle),
            _ => None,
        }
    }
}

// =============================================================================
// 窓集約の差し替え可能スペック (AggSpec)。既定 = ewma の中央値 (設計判断 A, 2026-06-17 確定)。
// =============================================================================

/// 窓集約で使う X/Y の源。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AggSource {
    /// `ewma_x`/`ewma_y` (ヒステリシス EMA 後 = デプロイ系が表示・行動に使うモデル出力)。
    Ewma,
    /// `raw_x`/`raw_y` (EMA 前 = 窓ローカル)。
    Raw,
}

/// 窓内サンプルの集約統計量。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AggStat {
    /// 中央値 (過渡スパイクに頑健・既定)。
    Median,
    /// 平均 (単純代表値)。
    Mean,
    /// 末尾値 (t−1s に最も近い feat・窓と時刻整合だが単点で脆弱)。
    Tail,
}

/// 窓集約スペック。`AggSpec::default()` = `{ Ewma, Median }`。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct AggSpec {
    pub source: AggSource,
    pub stat: AggStat,
}

impl Default for AggSpec {
    fn default() -> Self {
        Self {
            source: AggSource::Ewma,
            stat: AggStat::Median,
        }
    }
}

impl AggSpec {
    fn source_str(&self) -> &'static str {
        match self.source {
            AggSource::Ewma => "ewma",
            AggSource::Raw => "raw",
        }
    }
    fn stat_str(&self) -> &'static str {
        match self.stat {
            AggStat::Median => "median",
            AggStat::Mean => "mean",
            AggStat::Tail => "tail",
        }
    }
}

// =============================================================================
// 入力データ (replay.rs が NDJSON から抽出して渡す)
// =============================================================================

/// 1 つの `realtime_label` プローブと、その時間隔離窓の境界。
#[derive(Debug, Clone)]
pub struct ProbeRecord {
    pub source: ProbeSourceKind,
    pub answered: bool,
    /// 回答時のみ `Some(1..=5)`。skip は `None`。
    pub q1_friction: Option<u8>,
    pub q2_progress: Option<u8>,
    pub skip_reason: SkipReasonKind,
    pub latency_ms: u64,
    pub window_start_ms: u64,
    pub window_end_ms: u64,
}

/// 1 つの `vignette_response` (尺度理解テスト)。
#[derive(Debug, Clone)]
pub struct VignetteRecord {
    pub expected: QuadrantKind,
    pub q1_friction: u8,
    pub q2_progress: u8,
}

/// 1 セッション分の抽出結果。CLI は順序 = セッション時刻順で複数渡す (1 被験者ぶん)。
#[derive(Debug, Clone)]
pub struct SessionData {
    pub track: TrackKind,
    pub probes: Vec<ProbeRecord>,
    pub vignettes: Vec<VignetteRecord>,
    /// X/Y の源となる FeatSnapshot 列 (timestamp 昇順を仮定)。
    pub feats: Vec<FeatSnapshot>,
    /// `probe_assignment` (一様ランダムプローブ scheduled) の件数。
    /// 提示はされたが `realtime_label` が記録されなかった probe (途中クラッシュ等) の検出に使う
    /// = silent missingness の監査 (PreReg-7 MNAR・cross-review Codex#1)。
    pub random_probe_assignment_count: usize,
    /// セッション開始時刻 (`session_meta.ts`)。前向き holdout の時刻単調性検証に使う。
    /// session_meta がなければ `None`。
    pub session_start_ms: Option<u64>,
    /// NDJSON 抽出時に skip した行数 (データ品質の可視化・cross-review Codex#2)。
    pub skipped_parse: u64,
    pub skipped_unknown_enum: u64,
    pub skipped_out_of_range: u64,
}

// =============================================================================
// 基本ヘルパ (中央値・平均)
// =============================================================================

fn median_f64(values: &[f64]) -> Option<f64> {
    if values.is_empty() {
        return None;
    }
    let mut v = values.to_vec();
    v.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    let n = v.len();
    Some(if n % 2 == 1 {
        v[n / 2]
    } else {
        (v[n / 2 - 1] + v[n / 2]) / 2.0
    })
}

fn mean_f64(values: &[f64]) -> Option<f64> {
    if values.is_empty() {
        return None;
    }
    Some(values.iter().sum::<f64>() / values.len() as f64)
}

fn median_u64(values: &[u64]) -> Option<u64> {
    if values.is_empty() {
        return None;
    }
    let mut v = values.to_vec();
    v.sort_unstable();
    let n = v.len();
    Some(if n % 2 == 1 {
        v[n / 2]
    } else {
        // 偶数個は 2 値の平均。巨大 latency 値での加算オーバーフローを避ける overflow-safe 計算。
        let (a, b) = (v[n / 2 - 1], v[n / 2]);
        a / 2 + b / 2 + (a % 2 + b % 2) / 2
    })
}

// =============================================================================
// 象限推論 (scope 6 / PreReg-1)。frontend VignetteTest.tsx の inferQuadrant と同一規則。
// 端 (1-2 / 4-5) のみ採り、3 は曖昧として None (不一致扱い)。権威採点は本関数。
// =============================================================================

/// (q1摩擦, q2前進) → 象限。flow=低摩擦高前進 / stuck=高摩擦低前進 /
/// incubation=高摩擦高前進(詰まりつつ前進) / idle=低摩擦低前進。3 を含む曖昧は `None`。
pub fn infer_quadrant(q1: u8, q2: u8) -> Option<QuadrantKind> {
    let f_high = q1 >= 4;
    let f_low = q1 <= 2;
    let p_high = q2 >= 4;
    let p_low = q2 <= 2;
    if f_low && p_high {
        Some(QuadrantKind::Flow)
    } else if f_high && p_low {
        Some(QuadrantKind::Stuck)
    } else if f_high && p_high {
        Some(QuadrantKind::Incubation)
    } else if f_low && p_low {
        Some(QuadrantKind::Idle)
    } else {
        None
    }
}

// =============================================================================
// 方向付き 順序 C-index (scope 3 / §7 / PreReg-4)
// =============================================================================

/// 方向付き順序 C-index (concordance)。
///
/// `pairs`: `(x, q)` の列。`q_i != q_j` の比較可能ペアのみを母数とし、`(x_i−x_j)` と `(q_i−q_j)` の
/// 符号一致を concordant=1.0 / 逆=0.0 / `x` タイ=0.5 で数える (AUC / Harrell C と同形)。
///
/// 戻り値: 比較可能ペアが 1 つ以上あれば `Some(c)`、なければ `None`。
/// `0.5` = 偶然 / `1.0` = 完全一致 / `<0.5` = 逆方向。`O(n^2)` だが probe 数は小 (≤数百)。
pub fn concordance_index(pairs: &[(f64, u8)]) -> Option<f64> {
    let mut comparable: u64 = 0;
    let mut concordant: f64 = 0.0;
    for (i, &(xi, qi)) in pairs.iter().enumerate() {
        for &(xj, qj) in &pairs[i + 1..] {
            if qi == qj {
                continue; // 同順位は順序情報を持たない
            }
            comparable += 1;
            if xi == xj {
                concordant += 0.5; // x タイ
            } else if (xi > xj) == (qi > qj) {
                concordant += 1.0; // x の大小と q の大小が一致
            }
        }
    }
    if comparable == 0 {
        None
    } else {
        Some(concordant / comparable as f64)
    }
}

// =============================================================================
// 前向き固定 holdout (scope 3 / §8 / PreReg-5)
// =============================================================================

/// 較正に使うセッション数 (先頭からこの数を β 較正に使い C-index 評価から除外する)。
pub const HOLDOUT_CALIBRATION_SESSIONS: usize = 2;

/// 時刻順 (= 入力順) のセッション列を (較正用先頭 N, 評価用残り) に分割する。
/// セッション数 ≤ N の場合、評価集合は空になる (C-index 算出不能)。
pub fn prospective_holdout<T>(sessions: &[T]) -> (&[T], &[T]) {
    let split = sessions.len().min(HOLDOUT_CALIBRATION_SESSIONS);
    sessions.split_at(split)
}

// =============================================================================
// 窓集約 (scope 2 / §4.2)
// =============================================================================

/// 窓 `[start_ms, end_ms]` 内の FeatSnapshot から X/Y を集約した結果。
#[derive(Debug, Clone, Copy)]
pub struct WindowAgg {
    pub x_friction: f64,
    pub y_engagement: f64,
    pub feat_count: usize,
}

/// 窓 `[start_ms, end_ms]` 内の FeatSnapshot を集め、`spec` に従い X/Y を集約する。
/// 窓内 feat が 0 件 (全沈黙でエンジン pause 等) なら `None`。
pub fn aggregate_window(
    feats: &[FeatSnapshot],
    start_ms: u64,
    end_ms: u64,
    spec: AggSpec,
) -> Option<WindowAgg> {
    // (timestamp, x, y) を窓内ぶん収集。
    let mut rows: Vec<(u64, f64, f64)> = feats
        .iter()
        .filter(|f| f.timestamp >= start_ms && f.timestamp <= end_ms)
        .map(|f| {
            let (x, y) = match spec.source {
                AggSource::Ewma => (f.ewma_x, f.ewma_y),
                AggSource::Raw => (f.raw_x, f.raw_y),
            };
            (f.timestamp, x, y)
        })
        .collect();
    if rows.is_empty() {
        return None;
    }
    let (x, y) = match spec.stat {
        AggStat::Median => {
            let xs: Vec<f64> = rows.iter().map(|r| r.1).collect();
            let ys: Vec<f64> = rows.iter().map(|r| r.2).collect();
            (median_f64(&xs).unwrap(), median_f64(&ys).unwrap())
        }
        AggStat::Mean => {
            let xs: Vec<f64> = rows.iter().map(|r| r.1).collect();
            let ys: Vec<f64> = rows.iter().map(|r| r.2).collect();
            (mean_f64(&xs).unwrap(), mean_f64(&ys).unwrap())
        }
        AggStat::Tail => {
            // t−1s に最も近い = timestamp 最大の feat。入力の昇順仮定に依存せず明示的に最大を採る。
            rows.sort_by_key(|r| r.0);
            let last = rows.last().unwrap();
            (last.1, last.2)
        }
    };
    Some(WindowAgg {
        x_friction: x,
        y_engagement: y,
        feat_count: rows.len(),
    })
}

// =============================================================================
// 集約済み観測 (内部): 1 probe = 窓集約 X/Y + 主観 q1/q2
// =============================================================================

#[derive(Debug, Clone, Copy)]
struct ProbeObservation {
    /// 窓内 feat が 0 件なら `None` (C-index ペアから除外)。
    x_friction: Option<f64>,
    y_engagement: Option<f64>,
    q1: Option<u8>,
    q2: Option<u8>,
    answered: bool,
    source: ProbeSourceKind,
    skip_reason: SkipReasonKind,
    latency_ms: u64,
}

fn build_observation(p: &ProbeRecord, feats: &[FeatSnapshot], spec: AggSpec) -> ProbeObservation {
    let agg = aggregate_window(feats, p.window_start_ms, p.window_end_ms, spec);
    ProbeObservation {
        x_friction: agg.map(|a| a.x_friction),
        y_engagement: agg.map(|a| a.y_engagement),
        q1: p.q1_friction,
        q2: p.q2_progress,
        answered: p.answered,
        source: p.source,
        skip_reason: p.skip_reason,
        latency_ms: p.latency_ms,
    }
}

/// 回答済み random_probe 観測から (X, Q1) ペアを作る (C-index の主データ)。
fn pairs_x_q1(obs: &[ProbeObservation]) -> Vec<(f64, u8)> {
    obs.iter()
        .filter(|o| o.source == ProbeSourceKind::RandomProbe && o.answered)
        .filter_map(|o| Some((o.x_friction?, o.q1?)))
        .collect()
}

fn pairs_y_q2(obs: &[ProbeObservation]) -> Vec<(f64, u8)> {
    obs.iter()
        .filter(|o| o.source == ProbeSourceKind::RandomProbe && o.answered)
        .filter_map(|o| Some((o.y_engagement?, o.q2?)))
        .collect()
}

// =============================================================================
// 2段ゲート (scope 4 / PreReg-2 / PreReg-4) — 被験者横断の純関数
// =============================================================================

/// PreReg-2 閾値。
pub const ANSWER_RATE_MIN: f64 = 0.80;
pub const ANSWER_RATE_PER_SUBJECT_KILL: f64 = 0.70;
pub const LATENCY_MEDIAN_MAX_MS: u64 = 10_000;
pub const VALID_PROBES_MIN: usize = 20;

/// PreReg-4 閾値。
pub const CINDEX_GO_MEDIAN: f64 = 0.65;
pub const CINDEX_GO_ALL_MIN: f64 = 0.55;
pub const CINDEX_KILL_MEDIAN: f64 = 0.55;
pub const CINDEX_KILL_PER_SUBJECT: f64 = 0.50;

/// 測定法ゲート (PreReg-2) の被験者横断判定。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum MeasurementGate {
    Pass,
    Kill,
}

/// 測定法ゲート: 全体回答率 `<0.80`、または 2 人以上で `<0.70` なら Kill。
/// (latency / 有効件数 / ビネットは被験者ごとの要件として `SubjectCalibration` で別途検証する)。
pub fn measurement_gate(
    overall_answer_rate: f64,
    per_subject_answer_rates: &[f64],
) -> MeasurementGate {
    let below_kill = per_subject_answer_rates
        .iter()
        .filter(|&&r| r < ANSWER_RATE_PER_SUBJECT_KILL)
        .count();
    if overall_answer_rate < ANSWER_RATE_MIN || below_kill >= 2 {
        MeasurementGate::Kill
    } else {
        MeasurementGate::Pass
    }
}

/// モデルゲート (PreReg-4) の判定。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum ModelGate {
    Go,
    Kill,
    Inconclusive,
}

/// モデルゲート: 各被験者の C-index 集合に対し、
/// 中央値 `≥0.65` かつ全員 `>0.55` = Go / 中央値 `≤0.55` または 2 人以上 `≤0.50` = Kill / 他 = INCONCLUSIVE。
/// 空集合は INCONCLUSIVE。
pub fn model_gate(subject_cindices: &[f64]) -> ModelGate {
    if subject_cindices.is_empty() {
        return ModelGate::Inconclusive;
    }
    let median = median_f64(subject_cindices).unwrap();
    let all_above = subject_cindices.iter().all(|&c| c > CINDEX_GO_ALL_MIN);
    let below_kill = subject_cindices
        .iter()
        .filter(|&&c| c <= CINDEX_KILL_PER_SUBJECT)
        .count();
    if median >= CINDEX_GO_MEDIAN && all_above {
        ModelGate::Go
    } else if median <= CINDEX_KILL_MEDIAN || below_kill >= 2 {
        ModelGate::Kill
    } else {
        ModelGate::Inconclusive
    }
}

// =============================================================================
// 出力 (scope 7) — Serialize 構造体
// =============================================================================

/// 窓集約スペックの JSON 表現。
#[derive(Debug, Clone, Serialize)]
pub struct AggSpecReport {
    pub source: String,
    pub stat: String,
}

/// 測定法統計 (被験者単位)。
#[derive(Debug, Clone, Serialize)]
pub struct MeasurementStats {
    /// 提示されたランダムプローブ数 (= source=random_probe の realtime_label 件数)。回答率の分母。
    pub random_probe_total: usize,
    pub random_probe_answered: usize,
    pub answer_rate: f64,
    pub latency_median_ms: Option<u64>,
    /// 有効プローブ = 回答済みランダムプローブ。
    pub valid_count: usize,
    pub no_answer_rate: f64,
    pub dont_remember_count: usize,
    /// `probe_assignment` (scheduled) の総数。回答率の分母は到達確認済みの `realtime_label` だが、
    /// assigned > labeled の差は「提示されたが label 未記録」(途中クラッシュ等) の silent missingness を示す。
    pub random_probe_assigned: usize,
    /// `assigned − realtime_label` の正値差。>0 は回答率が過大評価されうる監査シグナル (PreReg-7, Codex#1)。
    pub assigned_without_label: usize,
    /// PreReg-2 の被験者要件 (回答率≥0.80 & latency 中央値≤10s & 有効≥20) を満たすか。
    pub per_subject_pass: bool,
}

/// 被験者内 C-index (評価セッションのみ・回答済み random_probe)。
#[derive(Debug, Clone, Serialize)]
pub struct SubjectCindex {
    /// 評価セッションの観測をプールした C-index (X↔Q1)。比較可能ペアなしは `None`。
    pub x_q1_pooled: Option<f64>,
    /// 評価セッションごとの C-index の中央値 (X↔Q1)。PreReg-4 「各人の C-index 中央値」の文言準拠。
    pub x_q1_session_median: Option<f64>,
    pub y_q2_pooled: Option<f64>,
    pub y_q2_session_median: Option<f64>,
    /// C-index に使った評価観測数 (回答済み random_probe・X あり)。
    pub eval_pair_source_count: usize,
}

/// MNAR 上下限 (PreReg-7)。未回答 q を 全高(5)/全低(1) に置いた X↔Q1 C-index の範囲。
#[derive(Debug, Clone, Serialize)]
pub struct MnarBounds {
    /// 点推定 (回答済みのみ)。
    pub point: Option<f64>,
    pub lower: Option<f64>,
    pub upper: Option<f64>,
    pub no_answer_rate: f64,
    /// 無回答率 >20%。
    pub caution: bool,
    /// 無回答率 >30% (主分析不成立)。
    pub invalid: bool,
}

/// ビネット採点 (PreReg-1)。
#[derive(Debug, Clone, Serialize)]
pub struct VignetteScore {
    pub total: usize,
    pub matched: usize,
    /// 6/8 以上 (被験者単位の通過)。
    pub passed: bool,
}

/// 6/8 の合格最小一致数。
pub const VIGNETTE_PASS_MIN: usize = 6;

/// 二軸性 (PreReg-8・報告併走)。realtime_label の (q1,q2) 象限分布。
#[derive(Debug, Clone, Serialize)]
pub struct Bidimensionality {
    pub flow: usize,
    pub stuck: usize,
    pub incubation: usize,
    pub idle: usize,
    /// q=3 を含む曖昧 (象限分類不能)。
    pub ambiguous: usize,
    /// 分類済みに占めるインキュベーション(③ 非対角)の割合。
    pub incubation_fraction: f64,
    /// 非対角 (incubation + idle) の割合。
    pub off_diagonal_fraction: f64,
    /// インキュベーション ≥10% なら二軸性検証可能。<10% は「検証不能」。
    pub verifiable: bool,
}

/// 二軸性検証可能とみなすインキュベーション出現の下限。
pub const BIDIMENSIONALITY_MIN_INCUBATION: f64 = 0.10;

/// Recall 報告 (PreReg-6)。点推定は出さない。
#[derive(Debug, Clone, Serialize)]
pub struct RecallReport {
    pub reported: bool,
    /// 独立陽性エピソード数 (一様ランダムプローブ分母)。
    pub positive_episode_count: usize,
    pub reason: String,
}

/// Recall 点推定を出す最小の独立陽性エピソード数 (PreReg-6)。
pub const RECALL_MIN_POSITIVES: usize = 30;

/// 較正レポート (1 被験者ぶん)。`gse-replay --calibration ... --json` が出力する metrics.json。
#[derive(Debug, Clone, Serialize)]
pub struct CalibrationReport {
    pub schema: String,
    /// 主指標に含めるか (track=main のセッションが存在するか)。
    pub included_in_primary: bool,
    pub session_count: usize,
    pub main_session_count: usize,
    pub exploratory_session_count: usize,
    pub calibration_session_count: usize,
    pub evaluation_session_count: usize,
    pub agg: AggSpecReport,
    pub measurement: MeasurementStats,
    pub cindex: SubjectCindex,
    pub mnar: MnarBounds,
    pub vignette: VignetteScore,
    pub bidimensionality: Bidimensionality,
    pub recall: RecallReport,
    pub notes: Vec<String>,
}

// =============================================================================
// 集計の中核 (scope 7)
// =============================================================================

/// 1 被験者の複数セッション (時刻順) から較正レポートを算出する。
///
/// - `track=exploratory` のセッションは主指標 (C-index/測定法/MNAR/二軸性) から除外する (§1.3)。
/// - 前向き holdout: main セッションの先頭 2 を較正として C-index から除外、残りを評価とする (§8)。
/// - C-index は評価セッションの回答済み random_probe 観測のみ。
/// - Recall 点推定は出さない (PreReg-6)。
pub fn compute_calibration_metrics(sessions: &[SessionData], spec: AggSpec) -> CalibrationReport {
    let mut notes: Vec<String> = Vec::new();

    let main_sessions: Vec<&SessionData> = sessions
        .iter()
        .filter(|s| s.track == TrackKind::Main)
        .collect();
    let exploratory_count = sessions.len() - main_sessions.len();
    if exploratory_count > 0 {
        notes.push(format!(
            "{} exploratory session(s) excluded from primary metrics (§1.3)",
            exploratory_count
        ));
    }

    // 前向き holdout の前提: 入力 = 時刻順。session_start_ms が非単調なら holdout で未来→過去の
    // 時間リークが起きうるため警告する (Codex#3)。timestamp 欠落セッションは検証から除外。
    let starts: Vec<u64> = main_sessions
        .iter()
        .filter_map(|s| s.session_start_ms)
        .collect();
    if starts.windows(2).any(|w| w[0] > w[1]) {
        notes.push(
            "main sessions are NOT in ascending session_start order — prospective holdout may leak \
             future→past; pass sessions in chronological order (§8, Codex#3)"
                .to_string(),
        );
    }

    // データ品質: 抽出時の skip 行数を集計して可視化する (Codex#2)。
    let skipped_parse: u64 = sessions.iter().map(|s| s.skipped_parse).sum();
    let skipped_unknown: u64 = sessions.iter().map(|s| s.skipped_unknown_enum).sum();
    let skipped_range: u64 = sessions.iter().map(|s| s.skipped_out_of_range).sum();
    if skipped_parse + skipped_unknown + skipped_range > 0 {
        notes.push(format!(
            "extraction skipped lines: parse={} unknown_enum={} out_of_range={} (data quality)",
            skipped_parse, skipped_unknown, skipped_range
        ));
    }

    // 前向き holdout 分割 (main のみ)。
    let (calib, eval) = prospective_holdout(&main_sessions);
    if eval.is_empty() && !main_sessions.is_empty() {
        notes.push(format!(
            "evaluation set empty: need >{} main sessions for prospective holdout C-index (§8)",
            HOLDOUT_CALIBRATION_SESSIONS
        ));
    }

    // --- 測定法統計 (main 全セッションの提示プローブで集計) ---
    // 回答率は提示ランダムプローブが分母 (PreReg-2)。
    let all_main_obs: Vec<ProbeObservation> = main_sessions
        .iter()
        .flat_map(|s| {
            s.probes
                .iter()
                .map(|p| build_observation(p, &s.feats, spec))
        })
        .collect();
    let random_obs: Vec<&ProbeObservation> = all_main_obs
        .iter()
        .filter(|o| o.source == ProbeSourceKind::RandomProbe)
        .collect();
    let random_total = random_obs.len();
    let random_answered = random_obs.iter().filter(|o| o.answered).count();
    let answer_rate = if random_total == 0 {
        0.0
    } else {
        random_answered as f64 / random_total as f64
    };
    let no_answer_rate = if random_total == 0 {
        0.0
    } else {
        (random_total - random_answered) as f64 / random_total as f64
    };
    let dont_remember_count = random_obs
        .iter()
        .filter(|o| o.skip_reason == SkipReasonKind::DontRemember)
        .count();
    let latencies: Vec<u64> = random_obs
        .iter()
        .filter(|o| o.answered)
        .map(|o| o.latency_ms)
        .collect();
    let latency_median = median_u64(&latencies);
    let per_subject_pass = answer_rate >= ANSWER_RATE_MIN
        && latency_median.is_some_and(|m| m <= LATENCY_MEDIAN_MAX_MS)
        && random_answered >= VALID_PROBES_MIN;

    // 割当 (probe_assignment) と到達 (realtime_label) の gap = silent missingness の監査 (Codex#1)。
    let random_probe_assigned: usize = main_sessions
        .iter()
        .map(|s| s.random_probe_assignment_count)
        .sum();
    let assigned_without_label = random_probe_assigned.saturating_sub(random_total);
    if assigned_without_label > 0 {
        notes.push(format!(
            "{} probe_assignment(s) had no matching realtime_label — answer_rate may overstate \
             (silent missingness, PreReg-7); investigate session integrity",
            assigned_without_label
        ));
    }

    let measurement = MeasurementStats {
        random_probe_total: random_total,
        random_probe_answered: random_answered,
        answer_rate,
        latency_median_ms: latency_median,
        valid_count: random_answered,
        no_answer_rate,
        dont_remember_count,
        random_probe_assigned,
        assigned_without_label,
        per_subject_pass,
    };

    // --- 被験者内 C-index (評価セッションのみ) ---
    let eval_obs: Vec<ProbeObservation> = eval
        .iter()
        .flat_map(|s| {
            s.probes
                .iter()
                .map(|p| build_observation(p, &s.feats, spec))
        })
        .collect();
    let eval_pairs_x_q1 = pairs_x_q1(&eval_obs);
    let x_q1_pooled = concordance_index(&eval_pairs_x_q1);
    let y_q2_pooled = concordance_index(&pairs_y_q2(&eval_obs));

    // セッションごとの C-index → 中央値 (PreReg-4 文言準拠)。
    let per_session_x_q1: Vec<f64> = eval
        .iter()
        .filter_map(|s| {
            let obs: Vec<ProbeObservation> = s
                .probes
                .iter()
                .map(|p| build_observation(p, &s.feats, spec))
                .collect();
            concordance_index(&pairs_x_q1(&obs))
        })
        .collect();
    let per_session_y_q2: Vec<f64> = eval
        .iter()
        .filter_map(|s| {
            let obs: Vec<ProbeObservation> = s
                .probes
                .iter()
                .map(|p| build_observation(p, &s.feats, spec))
                .collect();
            concordance_index(&pairs_y_q2(&obs))
        })
        .collect();
    let cindex = SubjectCindex {
        x_q1_pooled,
        x_q1_session_median: median_f64(&per_session_x_q1),
        y_q2_pooled,
        y_q2_session_median: median_f64(&per_session_y_q2),
        eval_pair_source_count: eval_pairs_x_q1.len(),
    };

    // --- MNAR 上下限 (評価セッションの random_probe・X あり) ---
    let mnar = compute_mnar_bounds(&eval_obs);

    // --- ビネット採点 (全セッションのビネット。通常は最初のセッションに 8 問) ---
    let vignette = score_vignettes_internal(sessions);

    // --- 二軸性 (PreReg-8): 「自然データ」の象限分布なので holdout 評価集合に限定せず main 全体で集計する
    //     (較正/評価の区別とは独立した記述統計・報告併走であり、モデルゲートの判定には用いない)。
    let bidimensionality = compute_bidimensionality(&all_main_obs);

    // --- Recall (点推定なし。PreReg-6) ---
    // 「独立陽性エピソード」= 一様ランダムプローブのうち主観が Stuck 象限 (高摩擦・低前進) の回答数。
    // この件数を根拠に点推定を withhold する (<30 では検出力なし)。分母は一様ランダムプローブのみ。
    let positive_episode_count = all_main_obs
        .iter()
        .filter(|o| o.source == ProbeSourceKind::RandomProbe && o.answered)
        .filter(|o| match (o.q1, o.q2) {
            (Some(q1), Some(q2)) => infer_quadrant(q1, q2) == Some(QuadrantKind::Stuck),
            _ => false,
        })
        .count();
    let recall = RecallReport {
        reported: false,
        positive_episode_count,
        reason: format!(
            "PreReg-6: point estimate withheld (Stuck-quadrant positives among uniform random probes \
             < {} needed for power; smoke withholds Recall)",
            RECALL_MIN_POSITIVES
        ),
    };

    CalibrationReport {
        schema: "calibration/v0.3".to_string(),
        included_in_primary: !main_sessions.is_empty(),
        session_count: sessions.len(),
        main_session_count: main_sessions.len(),
        exploratory_session_count: exploratory_count,
        calibration_session_count: calib.len(),
        evaluation_session_count: eval.len(),
        agg: AggSpecReport {
            source: spec.source_str().to_string(),
            stat: spec.stat_str().to_string(),
        },
        measurement,
        cindex,
        mnar,
        vignette,
        bidimensionality,
        recall,
        notes,
    }
}

/// MNAR 上下限: 未回答 random_probe の q1 を 5(全高)/1(全低) に置いて X↔Q1 C-index を再計算。
///
/// 母数は「**窓 X を持つ** random_probe」に統一する: 上下限の感度分析は窓 X がある probe でしか
/// 計算できないため、no_answer_rate / caution / invalid もその母集団で定義しないと、バウンド計算に
/// 寄与しない probe で欠測フラグが立つ非対称が生じる (code-reviewer HIGH 対応)。
fn compute_mnar_bounds(obs: &[ProbeObservation]) -> MnarBounds {
    // 窓 X を持つ random_probe のみが感度分析の対象母集団。
    let with_x: Vec<&ProbeObservation> = obs
        .iter()
        .filter(|o| o.source == ProbeSourceKind::RandomProbe && o.x_friction.is_some())
        .collect();
    let total = with_x.len();
    let unanswered = with_x.iter().filter(|o| !o.answered).count();
    let no_answer_rate = if total == 0 {
        0.0
    } else {
        unanswered as f64 / total as f64
    };

    // 点推定 (回答済みのみ)。
    let point_pairs: Vec<(f64, u8)> = with_x
        .iter()
        .filter(|o| o.answered)
        .filter_map(|o| Some((o.x_friction?, o.q1?)))
        .collect();
    let point = concordance_index(&point_pairs);

    // fill: 未回答に q を代入 (母数 with_x と一致)。
    let fill = |q_fill: u8| -> Option<f64> {
        let pairs: Vec<(f64, u8)> = with_x
            .iter()
            .filter_map(|o| {
                let x = o.x_friction?;
                let q = if o.answered { o.q1? } else { q_fill };
                Some((x, q))
            })
            .collect();
        concordance_index(&pairs)
    };
    let c_high = fill(5); // 全高摩擦
    let c_low = fill(1); // 全低摩擦
                         // 上下限 (どちらの仮定が上/下になるかはデータ依存なので min/max を取る)。
    let (lower, upper) = match (c_high, c_low) {
        (Some(a), Some(b)) => (Some(a.min(b)), Some(a.max(b))),
        (only @ Some(_), None) | (None, only @ Some(_)) => (only, only),
        (None, None) => (None, None),
    };

    MnarBounds {
        point,
        lower,
        upper,
        no_answer_rate,
        caution: no_answer_rate > 0.20,
        invalid: no_answer_rate > 0.30,
    }
}

/// ビネット採点 (PreReg-1): 全セッションの vignette_response を集計 (通常は最初のセッションに 8 問)。
fn score_vignettes_internal(sessions: &[SessionData]) -> VignetteScore {
    let vignettes: Vec<&VignetteRecord> =
        sessions.iter().flat_map(|s| s.vignettes.iter()).collect();
    let total = vignettes.len();
    let matched = vignettes
        .iter()
        .filter(|v| infer_quadrant(v.q1_friction, v.q2_progress) == Some(v.expected))
        .count();
    VignetteScore {
        total,
        matched,
        passed: matched >= VIGNETTE_PASS_MIN,
    }
}

/// 二軸性 (PreReg-8): 回答済み random_probe の (q1,q2) 象限分布。
fn compute_bidimensionality(obs: &[ProbeObservation]) -> Bidimensionality {
    let mut flow = 0;
    let mut stuck = 0;
    let mut incubation = 0;
    let mut idle = 0;
    let mut ambiguous = 0;
    for o in obs
        .iter()
        .filter(|o| o.source == ProbeSourceKind::RandomProbe && o.answered)
    {
        match (o.q1, o.q2) {
            (Some(q1), Some(q2)) => match infer_quadrant(q1, q2) {
                Some(QuadrantKind::Flow) => flow += 1,
                Some(QuadrantKind::Stuck) => stuck += 1,
                Some(QuadrantKind::Incubation) => incubation += 1,
                Some(QuadrantKind::Idle) => idle += 1,
                None => ambiguous += 1,
            },
            _ => ambiguous += 1,
        }
    }
    let classified = flow + stuck + incubation + idle;
    let incubation_fraction = if classified == 0 {
        0.0
    } else {
        incubation as f64 / classified as f64
    };
    let off_diagonal_fraction = if classified == 0 {
        0.0
    } else {
        (incubation + idle) as f64 / classified as f64
    };
    Bidimensionality {
        flow,
        stuck,
        incubation,
        idle,
        ambiguous,
        incubation_fraction,
        off_diagonal_fraction,
        verifiable: incubation_fraction >= BIDIMENSIONALITY_MIN_INCUBATION,
    }
}

// =============================================================================
// pretty 出力 (人間向け・--json なしの既定)
// =============================================================================

/// `CalibrationReport` を人間可読テキストに整形する (`metrics.rs::format_pretty` と同方針)。
pub fn format_calibration_pretty(r: &CalibrationReport) -> String {
    let mut out = String::new();
    out.push_str("=== GSE 較正解析 (v0.3 / Task D) ===\n");
    out.push_str(&format!(
        "sessions: {} (main {} / exploratory {}) | holdout: calib {} / eval {} | agg: {}/{}\n",
        r.session_count,
        r.main_session_count,
        r.exploratory_session_count,
        r.calibration_session_count,
        r.evaluation_session_count,
        r.agg.source,
        r.agg.stat,
    ));
    if !r.included_in_primary {
        out.push_str("[!] 主指標対象の main セッションなし\n");
    }
    out.push_str("\n-- 測定法ゲート (PreReg-2, 被験者単位) --\n");
    out.push_str(&format!(
        "  random probes: {} shown / {} answered (rate {:.1}%)\n",
        r.measurement.random_probe_total,
        r.measurement.random_probe_answered,
        r.measurement.answer_rate * 100.0,
    ));
    out.push_str(&format!(
        "  latency median: {} | valid: {} | dont_remember: {} | per-subject pass: {}\n",
        r.measurement
            .latency_median_ms
            .map(|m| format!("{} ms", m))
            .unwrap_or_else(|| "n/a".to_string()),
        r.measurement.valid_count,
        r.measurement.dont_remember_count,
        r.measurement.per_subject_pass,
    ));
    out.push_str(&format!(
        "  probe_assignment: {} assigned{}\n",
        r.measurement.random_probe_assigned,
        if r.measurement.assigned_without_label > 0 {
            format!(
                " | [!] {} assigned without label (silent missingness)",
                r.measurement.assigned_without_label
            )
        } else {
            String::new()
        },
    ));
    out.push_str("\n-- 被験者内 C-index (PreReg-4, 評価セッションのみ) --\n");
    out.push_str(&format!(
        "  X<->Q1 (摩擦): pooled {} / session-median {}\n",
        fmt_opt(r.cindex.x_q1_pooled),
        fmt_opt(r.cindex.x_q1_session_median),
    ));
    out.push_str(&format!(
        "  Y<->Q2 (前進): pooled {} / session-median {}  [secondary]\n",
        fmt_opt(r.cindex.y_q2_pooled),
        fmt_opt(r.cindex.y_q2_session_median),
    ));
    out.push_str(&format!(
        "  (eval pair source: {} answered random probes)\n",
        r.cindex.eval_pair_source_count,
    ));
    out.push_str("\n-- MNAR 上下限 (PreReg-7, X<->Q1) --\n");
    out.push_str(&format!(
        "  point {} | bounds [{}, {}] | no-answer {:.1}%{}{}\n",
        fmt_opt(r.mnar.point),
        fmt_opt(r.mnar.lower),
        fmt_opt(r.mnar.upper),
        r.mnar.no_answer_rate * 100.0,
        if r.mnar.caution {
            " [CAUTION >20%]"
        } else {
            ""
        },
        if r.mnar.invalid {
            " [INVALID >30%]"
        } else {
            ""
        },
    ));
    out.push_str("\n-- ビネット (PreReg-1) --\n");
    out.push_str(&format!(
        "  {}/{} matched -> {}\n",
        r.vignette.matched,
        r.vignette.total,
        if r.vignette.passed { "PASS" } else { "FAIL" },
    ));
    out.push_str("\n-- 二軸性 (PreReg-8) --\n");
    out.push_str(&format!(
        "  flow {} / stuck {} / incubation {} / idle {} / ambiguous {}\n",
        r.bidimensionality.flow,
        r.bidimensionality.stuck,
        r.bidimensionality.incubation,
        r.bidimensionality.idle,
        r.bidimensionality.ambiguous,
    ));
    out.push_str(&format!(
        "  incubation {:.1}% (off-diagonal {:.1}%) -> {}\n",
        r.bidimensionality.incubation_fraction * 100.0,
        r.bidimensionality.off_diagonal_fraction * 100.0,
        if r.bidimensionality.verifiable {
            "二軸性 検証可能"
        } else {
            "二軸性 検証不能 (<10%)"
        },
    ));
    out.push_str("\n-- Recall (PreReg-6) --\n");
    out.push_str(&format!(
        "  withheld (positives {}). {}\n",
        r.recall.positive_episode_count, r.recall.reason,
    ));
    if !r.notes.is_empty() {
        out.push_str("\n-- notes --\n");
        for n in &r.notes {
            out.push_str(&format!("  * {}\n", n));
        }
    }
    out.push_str(
        "\n[!] 被験者横断の Go/Kill/INCONCLUSIVE 最終判定はコホート全体が必要 (Task E)。\
         本レポートは 1 被験者の C-index/測定法統計を提供する。\n",
    );
    out
}

fn fmt_opt(v: Option<f64>) -> String {
    match v {
        Some(x) => format!("{:.3}", x),
        None => "n/a".to_string(),
    }
}

// =============================================================================
// Tests — 合成 in-code データで決定論的に検証 (受け入れ条件の golden 相当)
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    fn feat_at(ts: u64, ewma_x: f64, ewma_y: f64) -> FeatSnapshot {
        FeatSnapshot {
            timestamp: ts,
            f1: 0.0,
            f3: 0.0,
            f4: 0.0,
            f5: 0.0,
            f6: 0.0,
            p_flow: 0.34,
            p_inc: 0.33,
            p_stuck: 0.33,
            raw_x: ewma_x, // テストでは raw=ewma にして source 切替の影響を分離
            raw_y: ewma_y,
            ewma_x,
            ewma_y,
            obs: 0,
            alpha: 0.3,
        }
    }

    // ---- infer_quadrant ----

    #[test]
    fn infer_quadrant_matches_frontend_rule() {
        assert_eq!(infer_quadrant(1, 5), Some(QuadrantKind::Flow)); // 低摩擦・高前進
        assert_eq!(infer_quadrant(5, 1), Some(QuadrantKind::Stuck)); // 高摩擦・低前進
        assert_eq!(infer_quadrant(5, 5), Some(QuadrantKind::Incubation)); // 高摩擦・高前進
        assert_eq!(infer_quadrant(1, 1), Some(QuadrantKind::Idle)); // 低摩擦・低前進
        assert_eq!(infer_quadrant(3, 5), None); // q1=3 は曖昧
        assert_eq!(infer_quadrant(4, 3), None); // q2=3 は曖昧
        assert_eq!(infer_quadrant(3, 3), None);
    }

    // ---- concordance_index ----

    #[test]
    fn concordance_perfect_agreement_is_one() {
        // x が大きいほど q も大きい (完全一致)。
        let pairs = [(0.1, 1u8), (0.5, 3), (0.9, 5)];
        assert_eq!(concordance_index(&pairs), Some(1.0));
    }

    #[test]
    fn concordance_perfect_reverse_is_zero() {
        let pairs = [(0.9, 1u8), (0.5, 3), (0.1, 5)];
        assert_eq!(concordance_index(&pairs), Some(0.0));
    }

    #[test]
    fn concordance_x_tie_counts_half() {
        // q は異なるが x が同値 → 0.5。
        let pairs = [(0.5, 1u8), (0.5, 5)];
        assert_eq!(concordance_index(&pairs), Some(0.5));
    }

    #[test]
    fn concordance_equal_q_excluded() {
        // 全ペアで q 同値 → 比較可能ペア 0 → None。
        let pairs = [(0.1, 3u8), (0.9, 3)];
        assert_eq!(concordance_index(&pairs), None);
    }

    #[test]
    fn concordance_chance_level_exactly_half() {
        // 偶然水準 (0.5) の厳密回帰保護。
        // 点 A(1,1) B(2,1) C(1,2) D(2,2)。比較可能ペア (q 異なる) = A-C / A-D / B-C / B-D の 4 つ。
        //  A-C: q1<2, x 1.0==1.0 → tie 0.5
        //  A-D: q1<2, x 1.0<2.0 → concordant 1.0
        //  B-C: q1<2, x 2.0>1.0 → discordant 0.0
        //  B-D: q1<2, x 2.0==2.0 → tie 0.5
        // 合計 2.0 / 4 = 0.5。
        let pairs = [(1.0, 1u8), (2.0, 1), (1.0, 2), (2.0, 2)];
        assert_eq!(concordance_index(&pairs), Some(0.5));
    }

    // ---- aggregate_window ----

    #[test]
    fn aggregate_window_median_ewma() {
        let feats = [
            feat_at(1000, 0.2, 0.8),
            feat_at(2000, 0.6, 0.4),
            feat_at(3000, 0.4, 0.6),
        ];
        let agg = aggregate_window(&feats, 1000, 3000, AggSpec::default()).unwrap();
        assert!((agg.x_friction - 0.4).abs() < 1e-9); // median of [0.2,0.6,0.4]
        assert!((agg.y_engagement - 0.6).abs() < 1e-9);
        assert_eq!(agg.feat_count, 3);
    }

    #[test]
    fn aggregate_window_empty_is_none() {
        let feats = [feat_at(1000, 0.2, 0.8)];
        assert!(aggregate_window(&feats, 5000, 6000, AggSpec::default()).is_none());
    }

    #[test]
    fn aggregate_window_tail_picks_latest() {
        let feats = [
            feat_at(3000, 0.9, 0.1),
            feat_at(1000, 0.1, 0.9), // 順序が逆でも timestamp 最大を採る
        ];
        let spec = AggSpec {
            source: AggSource::Ewma,
            stat: AggStat::Tail,
        };
        let agg = aggregate_window(&feats, 0, 4000, spec).unwrap();
        assert!((agg.x_friction - 0.9).abs() < 1e-9);
    }

    // ---- prospective_holdout ----

    #[test]
    fn holdout_splits_first_two() {
        let s = [1, 2, 3, 4, 5];
        let (calib, eval) = prospective_holdout(&s);
        assert_eq!(calib, &[1, 2]);
        assert_eq!(eval, &[3, 4, 5]);
    }

    #[test]
    fn holdout_few_sessions_empty_eval() {
        let s = [1, 2];
        let (calib, eval) = prospective_holdout(&s);
        assert_eq!(calib, &[1, 2]);
        assert!(eval.is_empty());
    }

    // ---- model_gate ----

    #[test]
    fn model_gate_go() {
        // 中央値≥0.65 かつ全員>0.55。
        assert_eq!(model_gate(&[0.66, 0.70, 0.80]), ModelGate::Go);
    }

    #[test]
    fn model_gate_kill_low_median() {
        assert_eq!(model_gate(&[0.50, 0.55, 0.40]), ModelGate::Kill);
    }

    #[test]
    fn model_gate_kill_two_below_50() {
        // 中央値は高めでも 2 人以上≤0.50 → Kill。
        assert_eq!(model_gate(&[0.50, 0.50, 0.90, 0.90, 0.90]), ModelGate::Kill);
    }

    #[test]
    fn model_gate_inconclusive() {
        // 中央値 0.60 (>0.55 かつ >0.55 だが <0.65)、全員>0.55、≤0.50 は 0 人。
        assert_eq!(model_gate(&[0.60, 0.60, 0.62]), ModelGate::Inconclusive);
    }

    #[test]
    fn model_gate_empty_inconclusive() {
        assert_eq!(model_gate(&[]), ModelGate::Inconclusive);
    }

    #[test]
    fn model_gate_high_median_one_dropout_is_inconclusive() {
        // median=0.70≥0.65 だが 1 人が ≤0.50 で all>0.55 不成立 → Go 不可。
        // median は >0.55 かつ ≤0.50 は 1 人 (<2) → Kill 不可。→ INCONCLUSIVE に落ちることを固定。
        assert_eq!(model_gate(&[0.50, 0.70, 0.80]), ModelGate::Inconclusive);
    }

    // ---- measurement_gate ----

    #[test]
    fn measurement_gate_pass() {
        assert_eq!(
            measurement_gate(0.85, &[0.85, 0.90, 0.80]),
            MeasurementGate::Pass
        );
    }

    #[test]
    fn measurement_gate_kill_overall() {
        assert_eq!(measurement_gate(0.75, &[0.75, 0.75]), MeasurementGate::Kill);
    }

    #[test]
    fn measurement_gate_kill_two_below_70() {
        // 全体は 0.80 でも 2 人以上 <0.70 → Kill。
        assert_eq!(
            measurement_gate(0.80, &[0.65, 0.69, 0.95, 0.95]),
            MeasurementGate::Kill
        );
    }

    // ---- compute_calibration_metrics (統合・決定論) ----

    /// 強い X↔Q1 整合を持つ 1 被験者・4 セッション (先頭2=較正除外)。
    fn make_subject_sessions() -> Vec<SessionData> {
        // 各セッション: 3 probe (q1 = 1,3,5)、窓 X を q1 と単調にして concordance=1.0 を狙う。
        let make_session = |track: TrackKind, with_vignettes: bool| -> SessionData {
            let mut feats = Vec::new();
            let mut probes = Vec::new();
            // probe ごとに窓を分け、X を q1 に単調対応させる。
            let specs = [(1u8, 0.10f64), (3u8, 0.50), (5u8, 0.90)];
            for (i, (q1, x)) in specs.iter().enumerate() {
                let base = 10_000 + i as u64 * 40_000;
                let ws = base;
                let we = base + 30_000;
                // 窓内に 2 feat (X=x, Y=逆相関で Y↔Q2 も整合させる)。
                feats.push(feat_at(ws + 5_000, *x, 1.0 - *x));
                feats.push(feat_at(ws + 15_000, *x, 1.0 - *x));
                probes.push(ProbeRecord {
                    source: ProbeSourceKind::RandomProbe,
                    answered: true,
                    q1_friction: Some(*q1),
                    q2_progress: Some(6 - *q1), // q2 は q1 の逆 → Y(=1-x) と整合
                    skip_reason: SkipReasonKind::None,
                    latency_ms: 2_000,
                    window_start_ms: ws,
                    window_end_ms: we,
                });
            }
            let vignettes = if with_vignettes {
                vec![
                    VignetteRecord {
                        expected: QuadrantKind::Flow,
                        q1_friction: 1,
                        q2_progress: 5,
                    },
                    VignetteRecord {
                        expected: QuadrantKind::Flow,
                        q1_friction: 2,
                        q2_progress: 4,
                    },
                    VignetteRecord {
                        expected: QuadrantKind::Stuck,
                        q1_friction: 5,
                        q2_progress: 1,
                    },
                    VignetteRecord {
                        expected: QuadrantKind::Stuck,
                        q1_friction: 4,
                        q2_progress: 2,
                    },
                    VignetteRecord {
                        expected: QuadrantKind::Incubation,
                        q1_friction: 5,
                        q2_progress: 5,
                    },
                    VignetteRecord {
                        expected: QuadrantKind::Incubation,
                        q1_friction: 4,
                        q2_progress: 4,
                    },
                    VignetteRecord {
                        expected: QuadrantKind::Idle,
                        q1_friction: 1,
                        q2_progress: 1,
                    },
                    VignetteRecord {
                        expected: QuadrantKind::Idle,
                        q1_friction: 2,
                        q2_progress: 2,
                    },
                ]
            } else {
                Vec::new()
            };
            SessionData {
                track,
                probes,
                vignettes,
                feats,
                random_probe_assignment_count: 3,
                session_start_ms: None,
                skipped_parse: 0,
                skipped_unknown_enum: 0,
                skipped_out_of_range: 0,
            }
        };
        vec![
            make_session(TrackKind::Main, true),  // session 1 (calib)
            make_session(TrackKind::Main, false), // session 2 (calib)
            make_session(TrackKind::Main, false), // session 3 (eval)
            make_session(TrackKind::Main, false), // session 4 (eval)
        ]
    }

    #[test]
    fn compute_calibration_strong_concordance() {
        let sessions = make_subject_sessions();
        let r = compute_calibration_metrics(&sessions, AggSpec::default());
        assert!(r.included_in_primary);
        assert_eq!(r.main_session_count, 4);
        assert_eq!(r.calibration_session_count, 2);
        assert_eq!(r.evaluation_session_count, 2);
        // 評価セッションで X↔Q1 完全一致 → 1.0。
        assert_eq!(r.cindex.x_q1_pooled, Some(1.0));
        assert_eq!(r.cindex.x_q1_session_median, Some(1.0));
        // Y↔Q2: Y=1-x, q2=6-q1 → 両方単調逆 → concordance も 1.0。
        assert_eq!(r.cindex.y_q2_pooled, Some(1.0));
        // 全回答 → 回答率 100%。
        assert!((r.measurement.answer_rate - 1.0).abs() < 1e-9);
        assert_eq!(r.measurement.random_probe_total, 12);
        assert_eq!(r.measurement.random_probe_answered, 12);
        // ビネット 8/8 一致。
        assert_eq!(r.vignette.matched, 8);
        assert_eq!(r.vignette.total, 8);
        assert!(r.vignette.passed);
        // MNAR: 無回答なし → point=lower=upper=1.0。
        assert_eq!(r.mnar.point, Some(1.0));
        assert_eq!(r.mnar.lower, Some(1.0));
        assert_eq!(r.mnar.upper, Some(1.0));
        assert!(!r.mnar.caution);
        // Recall は withheld。
        assert!(!r.recall.reported);
    }

    #[test]
    fn compute_calibration_excludes_exploratory() {
        let mut sessions = make_subject_sessions();
        // 評価相当のセッションを exploratory にする → main は 3 本に減り eval は 1 本。
        sessions[3].track = TrackKind::Exploratory;
        let r = compute_calibration_metrics(&sessions, AggSpec::default());
        assert_eq!(r.exploratory_session_count, 1);
        assert_eq!(r.main_session_count, 3);
        assert_eq!(r.evaluation_session_count, 1);
        assert!(r.notes.iter().any(|n| n.contains("exploratory")));
    }

    #[test]
    fn compute_calibration_mnar_bounds_widen_with_skips() {
        // 評価セッションに skip プローブ (窓 X あり) を足し、上下限が分離することを確認。
        let mut sessions = make_subject_sessions();
        // eval セッション (index 3) に未回答プローブを追加。窓 X は高め (0.95)。
        let s = &mut sessions[3];
        let ws = 200_000;
        let we = ws + 30_000;
        s.feats.push(feat_at(ws + 10_000, 0.95, 0.05));
        s.probes.push(ProbeRecord {
            source: ProbeSourceKind::RandomProbe,
            answered: false,
            q1_friction: None,
            q2_progress: None,
            skip_reason: SkipReasonKind::DontRemember,
            latency_ms: 0,
            window_start_ms: ws,
            window_end_ms: we,
        });
        let r = compute_calibration_metrics(&sessions, AggSpec::default());
        // 無回答が混じる → no_answer_rate > 0。
        assert!(r.mnar.no_answer_rate > 0.0);
        // 上下限が定義される。
        assert!(r.mnar.lower.is_some() && r.mnar.upper.is_some());
        assert!(r.mnar.lower.unwrap() <= r.mnar.upper.unwrap());
    }

    #[test]
    fn compute_calibration_insufficient_sessions_empty_eval() {
        let sessions = vec![
            make_subject_sessions()[0].clone(),
            make_subject_sessions()[1].clone(),
        ];
        let r = compute_calibration_metrics(&sessions, AggSpec::default());
        assert_eq!(r.evaluation_session_count, 0);
        assert_eq!(r.cindex.x_q1_pooled, None);
        assert!(r.notes.iter().any(|n| n.contains("evaluation set empty")));
    }

    /// 空のセッション (probe/vignette/feat なし) を track 指定で作るヘルパ。
    fn empty_session(track: TrackKind, start_ms: Option<u64>, assigned: usize) -> SessionData {
        SessionData {
            track,
            probes: Vec::new(),
            vignettes: Vec::new(),
            feats: Vec::new(),
            random_probe_assignment_count: assigned,
            session_start_ms: start_ms,
            skipped_parse: 0,
            skipped_unknown_enum: 0,
            skipped_out_of_range: 0,
        }
    }

    #[test]
    fn non_monotonic_sessions_emit_warning_note() {
        // session_start が降順 → 時刻リーク警告 (Codex#3)。
        let sessions = vec![
            empty_session(TrackKind::Main, Some(3000), 0),
            empty_session(TrackKind::Main, Some(1000), 0),
        ];
        let r = compute_calibration_metrics(&sessions, AggSpec::default());
        assert!(r
            .notes
            .iter()
            .any(|n| n.contains("NOT in ascending session_start")));
    }

    #[test]
    fn assigned_without_label_is_surfaced() {
        // probe_assignment が 5 件あるが realtime_label が 0 件 → gap=5 を監査出力 (Codex#1)。
        let sessions = vec![empty_session(TrackKind::Main, Some(1000), 5)];
        let r = compute_calibration_metrics(&sessions, AggSpec::default());
        assert_eq!(r.measurement.random_probe_assigned, 5);
        assert_eq!(r.measurement.random_probe_total, 0);
        assert_eq!(r.measurement.assigned_without_label, 5);
        assert!(r
            .notes
            .iter()
            .any(|n| n.contains("no matching realtime_label")));
    }
}
