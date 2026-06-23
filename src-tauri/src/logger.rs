use std::fs::{self, File};
use std::io::{BufWriter, Write};
use std::path::{Path, PathBuf};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use crossbeam_channel::{bounded, Receiver, RecvTimeoutError, Sender};
use rand::Rng;

/// ユーザーが付与する Ground Truth ラベルの種別
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum UserLabelKind {
    Flow,
    Incubation,
    Stuck,
}

impl UserLabelKind {
    /// NDJSON に書き込む時の文字列表現
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Flow => "flow",
            Self::Incubation => "incubation",
            Self::Stuck => "stuck",
        }
    }

    /// `Tauri コマンド`引数 (String) から安全に変換。未知ラベルは `None`。
    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "flow" => Some(Self::Flow),
            "incubation" => Some(Self::Incubation),
            "stuck" => Some(Self::Stuck),
            _ => None,
        }
    }
}

/// v0.3 較正スモークのセッション系列 (track)。`main` = 本系列、`exploratory` = 探索系列。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Track {
    Main,
    Exploratory,
}

impl Track {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Main => "main",
            Self::Exploratory => "exploratory",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "main" => Some(Self::Main),
            "exploratory" => Some(Self::Exploratory),
            _ => None,
        }
    }
}

/// v0.3 較正スモークの課題種別 (task_kind)。session_meta で宣言する。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TaskKind {
    Argumentative,
    Correspondence,
    Creative,
    VibeCoding,
}

impl TaskKind {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Argumentative => "argumentative",
            Self::Correspondence => "correspondence",
            Self::Creative => "creative",
            Self::VibeCoding => "vibe_coding",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "argumentative" => Some(Self::Argumentative),
            "correspondence" => Some(Self::Correspondence),
            "creative" => Some(Self::Creative),
            "vibe_coding" => Some(Self::VibeCoding),
            _ => None,
        }
    }
}

/// `realtime_label` の出所 (source)。`random_probe` = backend が割当てたランダムプローブ、
/// `self_marker` = ユーザー自発の hotkey マーカー (副データ)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ProbeSource {
    RandomProbe,
    SelfMarker,
}

impl ProbeSource {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::RandomProbe => "random_probe",
            Self::SelfMarker => "self_marker",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "random_probe" => Some(Self::RandomProbe),
            "self_marker" => Some(Self::SelfMarker),
            _ => None,
        }
    }
}

/// `realtime_label` の skip 理由 (skip_reason)。`none` = 回答済み(skip でない)、
/// `dont_remember` = 直前の状態を思い出せない、`dismissed` = プローブを閉じた。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SkipReason {
    None,
    DontRemember,
    Dismissed,
}

impl SkipReason {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::None => "none",
            Self::DontRemember => "dont_remember",
            Self::Dismissed => "dismissed",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "none" => Some(Self::None),
            "dont_remember" => Some(Self::DontRemember),
            "dismissed" => Some(Self::Dismissed),
            _ => None,
        }
    }
}

/// `vignette_response` の想定象限 (expected_quadrant)。尺度理解テストの正解ラベル。
/// `UserLabelKind` とは別物 (`idle` を含み、認知状態 GT ではなく教示の正解)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ExpectedQuadrant {
    Flow,
    Stuck,
    Incubation,
    Idle,
}

impl ExpectedQuadrant {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Flow => "flow",
            Self::Stuck => "stuck",
            Self::Incubation => "incubation",
            Self::Idle => "idle",
        }
    }

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

/// 介入応答の理由 (reason)。`InterventionResponse` の理由カテゴリ (本文は含まない)。
///
/// **Nudge dismiss** (Need 誤りと Opportunity 誤りを分離・v0.4 §9):
/// `not_stuck` = 詰まっていない (Need 誤り)、`want_to_struggle` = 今はもがきたい (Opportunity 誤り)、
/// `just_close` = 単に閉じる、`silent` = 理由を選ばず閉じた/フェードアウト。
///
/// **Wall 応答** (Phase A2・⏸/順守の捕捉):
/// `early_unlock` = 2分タイマー完走前に解除 (非順守)、`completed` = 2分完走後に解除 (順守)、
/// `idle_timeout` = 長時間アイドルによる自動解除 (enum 予約のみ・現状未配線)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DismissReason {
    NotStuck,
    WantToStruggle,
    JustClose,
    Silent,
    /// Wall: 2分タイマー完走前の早期解除 (非順守)。
    EarlyUnlock,
    /// Wall: 2分タイマー完走後の通常解除 (順守)。
    Completed,
    /// Wall: 長時間アイドルによる自動解除。enum 予約のみ (現状未配線・将来用)。
    IdleTimeout,
}

impl DismissReason {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::NotStuck => "not_stuck",
            Self::WantToStruggle => "want_to_struggle",
            Self::JustClose => "just_close",
            Self::Silent => "silent",
            Self::EarlyUnlock => "early_unlock",
            Self::Completed => "completed",
            Self::IdleTimeout => "idle_timeout",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "not_stuck" => Some(Self::NotStuck),
            "want_to_struggle" => Some(Self::WantToStruggle),
            "just_close" => Some(Self::JustClose),
            "silent" => Some(Self::Silent),
            "early_unlock" => Some(Self::EarlyUnlock),
            "completed" => Some(Self::Completed),
            "idle_timeout" => Some(Self::IdleTimeout),
            _ => None,
        }
    }
}

/// セッションの実験条件 (condition)。Phase 1b 較正=`blind_calibration`、Phase 2 AB/BA=`a`/`b`、
/// Phase 3 MRT=`nudge`/`defer`、それ以外=`baseline`。固定カテゴリのみ。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Condition {
    BlindCalibration,
    A,
    B,
    Nudge,
    Defer,
    Baseline,
}

impl Condition {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::BlindCalibration => "blind_calibration",
            Self::A => "a",
            Self::B => "b",
            Self::Nudge => "nudge",
            Self::Defer => "defer",
            Self::Baseline => "baseline",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "blind_calibration" => Some(Self::BlindCalibration),
            "a" => Some(Self::A),
            "b" => Some(Self::B),
            "nudge" => Some(Self::Nudge),
            "defer" => Some(Self::Defer),
            "baseline" => Some(Self::Baseline),
            _ => None,
        }
    }
}

/// ラベルプール (label_pool)。`calibration_blind` = blind 較正で集めたラベル (X1 判定に使用)、
/// `post_intervention` = 介入可視環境で集めたラベル (合算せず別管理)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LabelPool {
    CalibrationBlind,
    PostIntervention,
}

impl LabelPool {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::CalibrationBlind => "calibration_blind",
            Self::PostIntervention => "post_intervention",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "calibration_blind" => Some(Self::CalibrationBlind),
            "post_intervention" => Some(Self::PostIntervention),
            _ => None,
        }
    }
}

/// `realtime_label` の (source, probe_id) を結合して不変条件を型で保証する。
/// `source=self_marker ⇒ probe_id=null` を構造的に表現する: `SelfMarker` は
/// probe_id を持てず、`RandomProbe` は必ず probe_id を持つ。
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ProbeRef {
    /// backend 割当のランダムプローブ。`probe_assignment` の probe_id と対応する。
    RandomProbe { probe_id: String },
    /// ユーザー自発の hotkey マーカー。probe_id は持たない。
    SelfMarker,
}

impl ProbeRef {
    /// NDJSON の `source` 文字列。
    fn source(&self) -> ProbeSource {
        match self {
            Self::RandomProbe { .. } => ProbeSource::RandomProbe,
            Self::SelfMarker => ProbeSource::SelfMarker,
        }
    }

    /// NDJSON の `probe_id`。`SelfMarker` は常に `None`。
    fn probe_id(&self) -> Option<&str> {
        match self {
            Self::RandomProbe { probe_id } => Some(probe_id.as_str()),
            Self::SelfMarker => None,
        }
    }
}

/// `LogEntry::UserLabel` の NDJSON 1 行を生成する純粋関数。
/// `writeln!` の format に直接持たせるとテストしにくいため分離してある。
fn format_user_label_line(
    timestamp: u64,
    label: UserLabelKind,
    recovered_at: Option<u64>,
) -> String {
    let recovered = match recovered_at {
        Some(t) => t.to_string(),
        None => "null".to_string(),
    };
    format!(
        r#"{{"type":"user_label","t":{},"label":"{}","recovered_at":{}}}"#,
        timestamp,
        label.as_str(),
        recovered,
    )
}

/// `LogEntry::ImeShadow` の NDJSON 1 行を生成する純粋関数。
fn format_ime_shadow_line(
    timestamp: u64,
    dwell_ms: u64,
    candidate_nav_count: u32,
    abandon: bool,
) -> String {
    format!(
        r#"{{"type":"ime_shadow","t":{},"dwell_ms":{},"nav":{},"abandon":{}}}"#,
        timestamp, dwell_ms, candidate_nav_count, abandon,
    )
}

/// `LogEntry::InterventionDecision` の NDJSON 1 行を生成する純粋関数。
fn format_intervention_decision_line(
    timestamp: u64,
    action: &str,
    need_score: f64,
    opportunity_score: f64,
    p_stuck: f64,
    idle_ms: u64,
    wall_accum_ms: u64,
    reason: &str,
    suppressed_by: &[String],
) -> String {
    let suppressed = serde_json::to_string(suppressed_by).unwrap_or_else(|_| "[]".to_string());
    format!(
        r#"{{"type":"intervention_decision","t":{},"action":"{}","need_score":{:.4},"opportunity_score":{:.4},"p_stuck":{:.4},"idle_ms":{},"wall_accum_ms":{},"reason":"{}","suppressed_by":{}}}"#,
        timestamp,
        action,
        need_score,
        opportunity_score,
        p_stuck,
        idle_ms,
        wall_accum_ms,
        reason,
        suppressed,
    )
}

/// 数値 (1..=5 等) の `Option<u8>` を NDJSON 値 (`数値` または `null`) に変換する。
fn json_opt_u8(v: Option<u8>) -> String {
    match v {
        Some(n) => n.to_string(),
        None => "null".to_string(),
    }
}

/// 不透明 ID の `Option<&str>` を NDJSON 値 (`"..."` または `null`) に変換する。
/// JSON injection を防ぐため必ず `serde_json` でエスケープする (プライバシー境界:
/// 値は生成済み不透明 ID のみで本文を含まない前提だが、escape は defense in depth)。
fn json_opt_str(v: Option<&str>) -> String {
    match v {
        Some(s) => serde_json::to_string(s).unwrap_or_else(|_| "null".to_string()),
        None => "null".to_string(),
    }
}

/// `Option<u64>` を NDJSON 値 (`<n>` または `null`) に変換する。
fn json_opt_u64(v: Option<u64>) -> String {
    match v {
        Some(n) => n.to_string(),
        None => "null".to_string(),
    }
}

/// `LogEntry::Paste` の NDJSON 1 行を生成する純粋関数。
/// `external_paste_chars` は**ペースト文字数 (整数) のみ**で、クリップボードの中身は含まない
/// (data-privacy: 長さは内容ではない)。取得不能時は `null`。
fn format_paste_line(timestamp: u64, external_paste_chars: Option<u64>) -> String {
    format!(
        r#"{{"type":"paste","t":{},"external_paste_chars":{}}}"#,
        timestamp,
        json_opt_u64(external_paste_chars),
    )
}

/// `LogEntry::InterventionResponse` の NDJSON 1 行を生成する純粋関数。
/// 介入提示に対するユーザー応答 (理由) を固定カテゴリで記録する。
/// `intervention_decision` (判定側) とは別の「ユーザー応答側」ログ。本文は含まない。
/// `action` は呼び出し側で `InterventionAction::as_str()` を通した検証済み固定値のみが渡る
/// (schema 上は `InterventionActionDto` enum と一致)。自由文字列は来ない。
/// `elapsed_ms` は `Some` の時のみ出力する。`None` (Nudge dismiss) では従来出力と byte 同一
/// (後方互換)。schema_dto は `skip_serializing_if = Option::is_none` 相当で一致させる。
fn format_intervention_response_line(
    timestamp: u64,
    action: &str,
    reason: DismissReason,
    elapsed_ms: Option<u64>,
) -> String {
    match elapsed_ms {
        Some(ms) => format!(
            r#"{{"type":"intervention_response","t":{},"action":{},"reason":"{}","elapsed_ms":{}}}"#,
            timestamp,
            json_opt_str(Some(action)),
            reason.as_str(),
            ms,
        ),
        None => format!(
            r#"{{"type":"intervention_response","t":{},"action":{},"reason":"{}"}}"#,
            timestamp,
            json_opt_str(Some(action)),
            reason.as_str(),
        ),
    }
}

/// `LogEntry::SessionMeta` の NDJSON 1 行を生成する純粋関数。
fn format_session_meta_line(
    timestamp: u64,
    track: Track,
    task_kind: TaskKind,
    monk_mode: bool,
    intervention_enabled: bool,
    condition: Option<Condition>,
    label_pool: Option<LabelPool>,
) -> String {
    format!(
        r#"{{"type":"session_meta","track":"{}","task_kind":"{}","monk_mode":{},"intervention_enabled":{},"condition":{},"label_pool":{},"ts":{}}}"#,
        track.as_str(),
        task_kind.as_str(),
        monk_mode,
        intervention_enabled,
        json_opt_str(condition.map(|c| c.as_str())),
        json_opt_str(label_pool.map(|p| p.as_str())),
        timestamp,
    )
}

/// `LogEntry::ProbeAssignment` の NDJSON 1 行を生成する純粋関数。
fn format_probe_assignment_line(
    probe_id: &str,
    scheduled_ts: u64,
    session_elapsed_ms: u64,
) -> String {
    format!(
        r#"{{"type":"probe_assignment","probe_id":{},"scheduled_ts":{},"session_elapsed_ms":{}}}"#,
        json_opt_str(Some(probe_id)),
        scheduled_ts,
        session_elapsed_ms,
    )
}

/// `LogEntry::RealtimeLabel` の NDJSON 1 行を生成する純粋関数。
/// 不変条件 (skip⇒q1/q2=null, answered⇒1..=5, self_marker⇒probe_id=null) は
/// `LogEntry::realtime_label_*` コンストラクタ側で保証する。本関数は安全網として
/// `debug_assert!` で検証してから整形する。
#[allow(clippy::too_many_arguments)]
fn format_realtime_label_line(
    timestamp: u64,
    probe_id: Option<&str>,
    source: ProbeSource,
    q1_friction: Option<u8>,
    q2_progress: Option<u8>,
    answered: bool,
    skip_reason: SkipReason,
    latency_ms: u64,
    analysis_window_start_ms: u64,
    analysis_window_end_ms: u64,
) -> String {
    debug_assert_eq!(
        answered,
        q1_friction.is_some(),
        "realtime_label: answered と q1_friction の有無が不一致"
    );
    debug_assert_eq!(
        q1_friction.is_some(),
        q2_progress.is_some(),
        "realtime_label: q1/q2 の有無が不一致"
    );
    debug_assert!(
        q1_friction.is_none_or(|v| (1..=5).contains(&v)),
        "realtime_label: q1_friction が 1..=5 外"
    );
    debug_assert!(
        q2_progress.is_none_or(|v| (1..=5).contains(&v)),
        "realtime_label: q2_progress が 1..=5 外"
    );
    debug_assert!(
        !(matches!(source, ProbeSource::SelfMarker) && probe_id.is_some()),
        "realtime_label: self_marker は probe_id を持てない"
    );
    format!(
        r#"{{"type":"realtime_label","probe_id":{},"source":"{}","q1_friction":{},"q2_progress":{},"answered":{},"skip_reason":"{}","latency_ms":{},"analysis_window_start_ms":{},"analysis_window_end_ms":{},"ts":{}}}"#,
        json_opt_str(probe_id),
        source.as_str(),
        json_opt_u8(q1_friction),
        json_opt_u8(q2_progress),
        answered,
        skip_reason.as_str(),
        latency_ms,
        analysis_window_start_ms,
        analysis_window_end_ms,
        timestamp,
    )
}

/// `LogEntry::VignetteResponse` の NDJSON 1 行を生成する純粋関数。
fn format_vignette_response_line(
    timestamp: u64,
    vignette_id: &str,
    expected_quadrant: ExpectedQuadrant,
    q1_friction: u8,
    q2_progress: u8,
) -> String {
    debug_assert!(
        (1..=5).contains(&q1_friction) && (1..=5).contains(&q2_progress),
        "vignette_response: q1/q2 が 1..=5 外"
    );
    format!(
        r#"{{"type":"vignette_response","vignette_id":{},"expected_quadrant":"{}","q1_friction":{},"q2_progress":{},"ts":{}}}"#,
        json_opt_str(Some(vignette_id)),
        expected_quadrant.as_str(),
        q1_friction,
        q2_progress,
        timestamp,
    )
}

/// ログエントリの種別
#[derive(Debug)]
pub enum LogEntry {
    /// キーストロークイベント (生データ)
    Key {
        vk_code: u32,
        timestamp: u64,
        is_press: bool,
    },
    /// ペーストイベント (Ctrl+V / Cmd+V) の発生時刻と文字数。
    /// AI 依存度指標 (D4) 向けに回数を、(b) 自力解決率 (v0.4 §4.2 `manual_contribution_ratio`)
    /// 向けに `external_paste_chars` (ペースト**文字数=整数のみ**) を記録する。1 ペースト = 1 行。
    /// VK + 修飾キー状態から検出し、クリップボードは**長さのみ取得して中身は即破棄**する
    /// (data-privacy: 長さは内容ではない。CD1)。取得不能時は `None`。
    Paste {
        timestamp: u64,
        external_paste_chars: Option<u64>,
    },
    /// 特徴量 + HMM状態確率 + 診断データ (分析スレッドから)
    Feat {
        timestamp: u64,
        f1: f64,
        f3: f64,
        f4: f64,
        f5: f64,
        f6: f64,
        p_flow: f64,
        p_inc: f64,
        p_stuck: f64,
        raw_x: f64,
        raw_y: f64,
        ewma_x: f64,
        ewma_y: f64,
        obs: usize,
        alpha: f64,
    },
    /// IME入力モードの切替イベント
    /// on=true  → 日本語入力モード (あ/カ) に移行 → β_writing を使用
    /// on=false → 英数直接入力モード (A) に移行   → β_coding を使用
    ImeState {
        timestamp: u64,
        on: bool,
        active: bool,
    },
    /// ユーザーが「開始する」を押した時刻 (セッション境界マーカー)
    SessionStart { timestamp: u64 },
    /// Ground Truth ユーザーラベル (Phase 1)
    /// `recovered_at` はログ記録時は常に `None`。
    /// `gse-replay --metrics` 実行時にオフライン純粋関数で後付け計算される。
    UserLabel {
        timestamp: u64,
        label: UserLabelKind,
        recovered_at: Option<u64>,
    },
    /// 事後レビュー用ブックマークマーカー (Phase 1 GT 改善)
    /// ユーザーが「ここを後で見返したい」と思った瞬間を記録する。
    /// 認知状態の判断は含まない (UserLabel とは意味論が異なる)。
    ReviewMarker { timestamp: u64 },
    /// IME 変換セッションの影ログ (Phase 2b, Windows のみ)。
    /// HMM には統合しない。Phase 3 のデータ判断材料として蓄積。
    ImeShadow {
        timestamp: u64,
        dwell_ms: u64,
        candidate_nav_count: u32,
        abandon: bool,
    },
    /// MVP Opportunity 判定ログ。
    /// 固定カテゴリ文字列と数値のみ。本文・Unicode 文字・ウィンドウタイトルは含めない。
    InterventionDecision {
        timestamp: u64,
        action: String,
        need_score: f64,
        opportunity_score: f64,
        p_stuck: f64,
        idle_ms: u64,
        wall_accum_ms: u64,
        reason: String,
        suppressed_by: Vec<String>,
    },
    /// 介入提示に対するユーザー応答 (reason)。`intervention_decision` (判定側) とは別の
    /// 「ユーザー応答側」ログ。Nudge dismiss は Need/Opportunity 誤りを分離 (WBS 0.8 / v0.4 §9)、
    /// Wall は早期解除/通常解除(順守) を区別 (Phase A2)。固定カテゴリ + 時刻のみ。本文は含めない。
    /// `elapsed_ms` は Wall 提示(/shake)〜解除(/unlock) の経過時間。Nudge dismiss では `None`。
    InterventionResponse {
        timestamp: u64,
        action: String,
        reason: DismissReason,
        elapsed_ms: Option<u64>,
    },
    /// v0.3 較正スモーク: セッション開始宣言 (track / task_kind / Monk・介入トグル)。
    /// 数値・固定カテゴリのみ。`ts` で timestamp を持つ (既存 `t` とは別命名・§14 準拠)。
    /// `condition` = 実験条件 (WBS 0.11)、`label_pool` = ラベルプール (WBS 0.4)。いずれも省略可。
    SessionMeta {
        timestamp: u64,
        track: Track,
        task_kind: TaskKind,
        monk_mode: bool,
        intervention_enabled: bool,
        condition: Option<Condition>,
        label_pool: Option<LabelPool>,
    },
    /// v0.3 較正スモーク: ランダムプローブ割当の監査記録。
    /// 「モデル非依存・一様ランダム」を後から検証するため scheduled/shown を両方残す。
    /// `probe_id` は backend 生成の不透明 ID (本文非由来)。
    ProbeAssignment {
        probe_id: String,
        scheduled_ts: u64,
        session_elapsed_ms: u64,
    },
    /// v0.3 較正スモーク: 主データ (リアルタイム/自己マーカー回答)。
    /// 不変条件は `realtime_label_answered` / `realtime_label_skipped` で保証する:
    /// skip⇒q1/q2=None、answered⇒q1/q2=Some(1..=5)、self_marker⇒probe_id=None。
    /// 直接構築せずコンストラクタ経由を推奨 (writer 側 `debug_assert!` が安全網)。
    RealtimeLabel {
        timestamp: u64,
        probe_id: Option<String>,
        source: ProbeSource,
        q1_friction: Option<u8>,
        q2_progress: Option<u8>,
        answered: bool,
        skip_reason: SkipReason,
        latency_ms: u64,
        analysis_window_start_ms: u64,
        analysis_window_end_ms: u64,
    },
    /// v0.3 較正スモーク: 尺度理解テスト回答 (ビネット 8 問)。
    /// 常に回答あり (q1/q2 は 1..=5)。`expected_quadrant` は教示の正解ラベル。
    VignetteResponse {
        timestamp: u64,
        vignette_id: String,
        expected_quadrant: ExpectedQuadrant,
        q1_friction: u8,
        q2_progress: u8,
    },
    /// セッション終了マーカー
    End,
}

impl LogEntry {
    /// `RealtimeLabel` (回答あり) を不変条件を満たして構築する。
    /// q1/q2 は `1..=5` に clamp、`answered=true`、`skip_reason=None` を設定する。
    /// `probe`/`source` の整合 (self_marker⇒probe_id=null) は `ProbeRef` が型で保証する。
    #[allow(clippy::too_many_arguments)]
    pub fn realtime_label_answered(
        timestamp: u64,
        probe: &ProbeRef,
        q1_friction: u8,
        q2_progress: u8,
        latency_ms: u64,
        analysis_window_start_ms: u64,
        analysis_window_end_ms: u64,
    ) -> Self {
        LogEntry::RealtimeLabel {
            timestamp,
            probe_id: probe.probe_id().map(str::to_string),
            source: probe.source(),
            q1_friction: Some(q1_friction.clamp(1, 5)),
            q2_progress: Some(q2_progress.clamp(1, 5)),
            answered: true,
            skip_reason: SkipReason::None,
            latency_ms,
            analysis_window_start_ms,
            analysis_window_end_ms,
        }
    }

    /// `RealtimeLabel` (skip) を不変条件を満たして構築する。
    /// `q1/q2=None`、`answered=false` を設定する。`skip_reason` は `None` を許さず
    /// `DontRemember` / `Dismissed` のみ受ける (skip なのに理由 none は不整合のため)。
    pub fn realtime_label_skipped(
        timestamp: u64,
        probe: &ProbeRef,
        skip_reason: SkipReason,
        latency_ms: u64,
        analysis_window_start_ms: u64,
        analysis_window_end_ms: u64,
    ) -> Self {
        let skip_reason = match skip_reason {
            SkipReason::None => {
                tracing::warn!(
                    "realtime_label_skipped: skip_reason=None は不整合のため Dismissed に正規化 (呼び出し側バグの可能性)"
                );
                SkipReason::Dismissed
            }
            other => other,
        };
        LogEntry::RealtimeLabel {
            timestamp,
            probe_id: probe.probe_id().map(str::to_string),
            source: probe.source(),
            q1_friction: None,
            q2_progress: None,
            answered: false,
            skip_reason,
            latency_ms,
            analysis_window_start_ms,
            analysis_window_end_ms,
        }
    }

    /// `VignetteResponse` を不変条件を満たして構築する (q1/q2 を `1..=5` clamp)。
    /// 直接構築だと clamp されない (writer 側 `debug_assert!` は release で無効) ため、
    /// producer はこの構築子経由を使う (DC-4 / cross-review)。
    pub fn vignette_response(
        timestamp: u64,
        vignette_id: String,
        expected_quadrant: ExpectedQuadrant,
        q1_friction: u8,
        q2_progress: u8,
    ) -> Self {
        LogEntry::VignetteResponse {
            timestamp,
            vignette_id,
            expected_quadrant,
            q1_friction: q1_friction.clamp(1, 5),
            q2_progress: q2_progress.clamp(1, 5),
        }
    }
}

/// NDJSON形式でセッションデータを書き込むロガー。
/// バックグラウンドスレッドでファイルIOを行うため、
/// 送信側 (分析スレッド) は非ブロッキングで送信できる。
pub struct SessionLogger {
    pub log_path: PathBuf,
    _handle: thread::JoinHandle<()>,
}

impl SessionLogger {
    /// ロガーを開始し、ログエントリ送信用の `Sender` とシャットダウン通知用の `Receiver` を返す。
    /// `Sender` を Clone して複数スレッドから送信可能。
    /// `shutdown_rx` は `LogEntry::End` 処理完了後に値を受信する。
    pub fn start(log_path: PathBuf) -> (Self, Sender<LogEntry>, Receiver<()>) {
        let (tx, rx) = bounded::<LogEntry>(512);
        let (shutdown_tx, shutdown_rx) = bounded::<()>(1);
        let path_clone = log_path.clone();

        let handle = thread::spawn(move || {
            // 親ディレクトリを作成
            if let Some(parent) = path_clone.parent() {
                let _ = fs::create_dir_all(parent);
            }

            let file = match File::create(&path_clone) {
                Ok(f) => f,
                Err(e) => {
                    tracing::error!("SessionLogger: failed to create {:?}: {}", path_clone, e);
                    return;
                }
            };

            let mut writer = BufWriter::new(file);

            // セッション開始メタデータ
            // hmm_version は engine.rs の HMM_VERSION 定数。
            // gse-replay がゴールデンスナップショットと突き合わせる際に
            // 同一バージョンであることを検証する。
            let session_start = now_ms();
            let _ = writeln!(
                writer,
                r#"{{"type":"meta","session_start":{},"hmm_version":"{}"}}"#,
                session_start,
                crate::analysis::engine::HMM_VERSION,
            );

            tracing::info!("SessionLogger: writing to {:?}", path_clone);

            let flush_interval = Duration::from_secs(5);
            let mut last_flush = Instant::now();
            let mut dirty = false;

            loop {
                let timeout = flush_interval.saturating_sub(last_flush.elapsed());
                match rx.recv_timeout(timeout) {
                    Ok(entry) => match entry {
                        LogEntry::Key {
                            vk_code,
                            timestamp,
                            is_press,
                        } => {
                            let _ = writeln!(
                                writer,
                                r#"{{"type":"key","t":{},"vk":{},"press":{}}}"#,
                                timestamp, vk_code, is_press,
                            );
                            dirty = true;
                        }
                        LogEntry::Paste {
                            timestamp,
                            external_paste_chars,
                        } => {
                            let _ = writeln!(
                                writer,
                                "{}",
                                format_paste_line(timestamp, external_paste_chars),
                            );
                            dirty = true;
                        }
                        LogEntry::Feat {
                            timestamp,
                            f1,
                            f3,
                            f4,
                            f5,
                            f6,
                            p_flow,
                            p_inc,
                            p_stuck,
                            raw_x,
                            raw_y,
                            ewma_x,
                            ewma_y,
                            obs,
                            alpha,
                        } => {
                            let _ = writeln!(
                                writer,
                                r#"{{"type":"feat","t":{},"f1":{:.2},"f3":{:.4},"f4":{:.2},"f5":{:.1},"f6":{:.4},"p_flow":{:.4},"p_inc":{:.4},"p_stuck":{:.4},"raw_x":{:.4},"raw_y":{:.4},"ewma_x":{:.4},"ewma_y":{:.4},"obs":{},"alpha":{:.2}}}"#,
                                timestamp,
                                f1,
                                f3,
                                f4,
                                f5,
                                f6,
                                p_flow,
                                p_inc,
                                p_stuck,
                                raw_x,
                                raw_y,
                                ewma_x,
                                ewma_y,
                                obs,
                                alpha,
                            );
                            dirty = true;
                        }
                        LogEntry::ImeState {
                            timestamp,
                            on,
                            active,
                        } => {
                            let _ = writeln!(
                                writer,
                                r#"{{"type":"ime_state","t":{},"on":{},"active":{}}}"#,
                                timestamp, on, active,
                            );
                            dirty = true;
                        }
                        LogEntry::SessionStart { timestamp } => {
                            let _ = writeln!(
                                writer,
                                r#"{{"type":"session_start","t":{}}}"#,
                                timestamp,
                            );
                            dirty = true;
                        }
                        LogEntry::UserLabel {
                            timestamp,
                            label,
                            recovered_at,
                        } => {
                            let _ = writeln!(
                                writer,
                                "{}",
                                format_user_label_line(timestamp, label, recovered_at),
                            );
                            dirty = true;
                        }
                        LogEntry::ReviewMarker { timestamp } => {
                            let _ = writeln!(
                                writer,
                                r#"{{"type":"review_marker","t":{}}}"#,
                                timestamp,
                            );
                            dirty = true;
                        }
                        LogEntry::ImeShadow {
                            timestamp,
                            dwell_ms,
                            candidate_nav_count,
                            abandon,
                        } => {
                            let _ = writeln!(
                                writer,
                                "{}",
                                format_ime_shadow_line(
                                    timestamp,
                                    dwell_ms,
                                    candidate_nav_count,
                                    abandon
                                ),
                            );
                            dirty = true;
                        }
                        LogEntry::InterventionDecision {
                            timestamp,
                            action,
                            need_score,
                            opportunity_score,
                            p_stuck,
                            idle_ms,
                            wall_accum_ms,
                            reason,
                            suppressed_by,
                        } => {
                            let _ = writeln!(
                                writer,
                                "{}",
                                format_intervention_decision_line(
                                    timestamp,
                                    &action,
                                    need_score,
                                    opportunity_score,
                                    p_stuck,
                                    idle_ms,
                                    wall_accum_ms,
                                    &reason,
                                    &suppressed_by
                                ),
                            );
                            dirty = true;
                        }
                        LogEntry::InterventionResponse {
                            timestamp,
                            action,
                            reason,
                            elapsed_ms,
                        } => {
                            let _ = writeln!(
                                writer,
                                "{}",
                                format_intervention_response_line(
                                    timestamp, &action, reason, elapsed_ms
                                ),
                            );
                            dirty = true;
                        }
                        LogEntry::SessionMeta {
                            timestamp,
                            track,
                            task_kind,
                            monk_mode,
                            intervention_enabled,
                            condition,
                            label_pool,
                        } => {
                            let _ = writeln!(
                                writer,
                                "{}",
                                format_session_meta_line(
                                    timestamp,
                                    track,
                                    task_kind,
                                    monk_mode,
                                    intervention_enabled,
                                    condition,
                                    label_pool
                                ),
                            );
                            dirty = true;
                        }
                        LogEntry::ProbeAssignment {
                            probe_id,
                            scheduled_ts,
                            session_elapsed_ms,
                        } => {
                            let _ = writeln!(
                                writer,
                                "{}",
                                format_probe_assignment_line(
                                    &probe_id,
                                    scheduled_ts,
                                    session_elapsed_ms
                                ),
                            );
                            dirty = true;
                        }
                        LogEntry::RealtimeLabel {
                            timestamp,
                            probe_id,
                            source,
                            q1_friction,
                            q2_progress,
                            answered,
                            skip_reason,
                            latency_ms,
                            analysis_window_start_ms,
                            analysis_window_end_ms,
                        } => {
                            let _ = writeln!(
                                writer,
                                "{}",
                                format_realtime_label_line(
                                    timestamp,
                                    probe_id.as_deref(),
                                    source,
                                    q1_friction,
                                    q2_progress,
                                    answered,
                                    skip_reason,
                                    latency_ms,
                                    analysis_window_start_ms,
                                    analysis_window_end_ms,
                                ),
                            );
                            dirty = true;
                        }
                        LogEntry::VignetteResponse {
                            timestamp,
                            vignette_id,
                            expected_quadrant,
                            q1_friction,
                            q2_progress,
                        } => {
                            let _ = writeln!(
                                writer,
                                "{}",
                                format_vignette_response_line(
                                    timestamp,
                                    &vignette_id,
                                    expected_quadrant,
                                    q1_friction,
                                    q2_progress
                                ),
                            );
                            dirty = true;
                        }
                        LogEntry::End => {
                            let _ =
                                writeln!(writer, r#"{{"type":"meta","session_end":{}}}"#, now_ms());
                            break;
                        }
                    },
                    Err(RecvTimeoutError::Timeout) => {
                        // 5秒間アイドル → バッファフラッシュ
                    }
                    Err(RecvTimeoutError::Disconnected) => break,
                }

                // 5秒間隔でバッファフラッシュ (I/O負荷軽減)
                if dirty && last_flush.elapsed() >= flush_interval {
                    let _ = writer.flush();
                    last_flush = Instant::now();
                    dirty = false;
                }
            }

            let _ = writer.flush();
            // ファイルを閉じ終えたことを quit_app に通知する
            let _ = shutdown_tx.send(());
            tracing::info!("SessionLogger: session closed");
        });

        let logger = Self {
            log_path,
            _handle: handle,
        };

        (logger, tx, shutdown_rx)
    }
}

/// UNIX時刻をミリ秒で返す
fn now_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}

/// 参加者 ID 未設定時の既定値 (従来挙動を不変に保つ)
const DEFAULT_PARTICIPANT_ID: &str = "P000";

/// 参加者 ID として許可する最大長 (ディレクトリ名の暴走防止)
const MAX_PARTICIPANT_ID_LEN: usize = 64;

/// Windows の予約デバイス名 (大文字小文字無視で比較)。allowlist は通過するが、
/// ディレクトリ名に使うと `create_dir_all` が `ERROR_INVALID_NAME` で失敗し、
/// 原因の分かりにくいセッションログ欠落を招くため拒否する (本機の主ターゲットは Windows 11)。
const WINDOWS_RESERVED_NAMES: &[&str] = &[
    "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8",
    "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
];

/// 参加者 ID が保存先パスの構成要素として安全かを検証する。
///
/// allowlist 方式: ASCII 英数字 + `_` + `-` のみ、長さ 1..=64。
/// これにより `.`(→`..`)・`/`・`\`・`:`・空白・null・改行・`~`・`$` 等を一括拒否し、
/// パストラバーサル / パス注入を構造的に防ぐ。参加者 ID 規約 (`P000`/`P003` 等) は
/// 完全にカバーされる。加えて Windows 予約デバイス名 (`CON`/`NUL` 等) を拒否する。
/// 検証は呼び出し側で trim 済みの値に対して行う。
fn is_valid_participant_id(id: &str) -> bool {
    if id.is_empty() || id.len() > MAX_PARTICIPANT_ID_LEN {
        return false;
    }
    if !id
        .bytes()
        .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
    {
        return false;
    }
    let upper = id.to_ascii_uppercase();
    !WINDOWS_RESERVED_NAMES.contains(&upper.as_str())
}

/// 候補列 (優先順) から最初の妥当な参加者 ID を返す純粋関数。
///
/// env / 永続化値に依存しないため単体テスト可能。各候補は前後空白を trim してから
/// `is_valid_participant_id` で検証し、最初に妥当だったものを返す。妥当な候補が
/// なければ `None` (呼び出し側が自動生成 / 既定値に委ねる)。
fn first_valid_id(candidates: &[Option<&str>]) -> Option<String> {
    for raw in candidates.iter().flatten() {
        let id = raw.trim();
        if is_valid_participant_id(id) {
            return Some(id.to_string());
        }
    }
    None
}

/// 端末ごとに一意な不透明参加者 ID を自動生成する。
///
/// 形式は `P` + 12 桁ランダム hex (48 bit, 例 `Pa3f9c2e1b7d0`)。常に
/// `is_valid_participant_id` を通過し (ASCII 英数字のみ・13 文字)、sync スクリプトの
/// `P*` glob とも互換。値はキーストローク等の本文に一切由来しない (プライバシー境界:
/// data-privacy Skill — 自動付与 ID は不透明で被験者本人も内容を推定できない)。
fn generate_participant_id() -> String {
    // 48 bit (= 12 hex 桁) を thread_rng (CSPRNG) から引く。誕生日衝突は端末数 N に対し
    // 約 N²/2⁴⁹ で、研究運用の N (≤ 数百規模) では実用上無視できる (桁を変える際の判断材料)。
    let bits: u64 = rand::thread_rng().gen::<u64>() & 0x0000_FFFF_FFFF_FFFF;
    format!("P{bits:012x}")
}

/// 自動生成した参加者 ID を永続化するファイルのパス `~/.gse/participant_id`。
///
/// 基点は `USERPROFILE` → `HOME` の順 (`fallback_log_dir` と同流儀)。どちらも未設定で
/// home が解決できなければ `None` を返す (永続化不能 → 呼び出し側が `P000` fallback)。
fn participant_id_store_path() -> Option<PathBuf> {
    let base = std::env::var("USERPROFILE")
        .or_else(|_| std::env::var("HOME"))
        .ok()?;
    Some(PathBuf::from(base).join(".gse").join("participant_id"))
}

/// 指定パスから参加者 ID を読み出す純粋ヘルパー (I/O は `path` に対してのみ・env 非依存)。
///
/// ファイルが無い / 読めない / 値が不正なら `None`。値は trim してから
/// `is_valid_participant_id` で検証する (破損・手編集による不正値 = path injection を防ぐ)。
/// env / home に依存しないため一時ファイルで単体テスト可能。
fn load_id_from(path: &Path) -> Option<String> {
    let raw = fs::read_to_string(path).ok()?;
    let id = raw.trim();
    if is_valid_participant_id(id) {
        Some(id.to_string())
    } else {
        if !id.is_empty() {
            tracing::warn!("persisted participant id rejected (invalid format); will regenerate");
        }
        None
    }
}

/// 参加者 ID を指定パスへ **アトミックに** 書く純粋ヘルパー (env 非依存・テスト可能)。
///
/// 同一ディレクトリの一時ファイルへ書いてから `fs::rename` で差し替える。これにより
/// 途中クラッシュ / 同時起動で `path` 自身が空 / 部分書き込みになることを防ぎ、次回の
/// `load_id_from` が「空 → 再生成」に倒れて端末 ID が変わる事故を回避する
/// (D4「再起動でも ID 不変」を守る)。親ディレクトリが無ければ作成する。
fn persist_id_to(path: &Path, id: &str) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    // 一時名に pid を含め、並行起動どうしの一時ファイル衝突を避ける。
    // 同一ボリューム内 rename のため `fs::rename` はアトミック (Windows/Unix とも既存を置換)。
    let tmp = path.with_file_name(format!("participant_id.tmp.{}", std::process::id()));
    fs::write(&tmp, id)?;
    fs::rename(&tmp, path).inspect_err(|_| {
        // rename 失敗時は一時ファイルを残さない (掃除はベストエフォート)。
        let _ = fs::remove_file(&tmp);
    })
}

/// 永続化済みの参加者 ID を読み出す。home (`USERPROFILE`/`HOME`) 不明なら `None`。
fn load_persisted_id() -> Option<String> {
    load_id_from(&participant_id_store_path()?)
}

/// 自動生成した参加者 ID を `~/.gse/participant_id` に永続化する。
///
/// home 不明 / 書込失敗は `Err` を返し、呼び出し側が `P000` fallback に倒す。`anyhow` は
/// 本 crate (lib) の依存ではないため (replay.rs と同方針)、std の `io::Result` で伝播する。
fn persist_id(id: &str) -> std::io::Result<()> {
    let path = participant_id_store_path().ok_or_else(|| {
        std::io::Error::new(
            std::io::ErrorKind::NotFound,
            "no home directory (USERPROFILE/HOME) to persist participant id",
        )
    })?;
    persist_id_to(&path, id)
}

/// `resolve_with_store` の判定結果。
///
/// `Existing` = 永続化値 / env 由来で **再永続化しない** (D4 ③: env は永続化しない)。
/// `Generated` = 新規生成のため呼び出し側が永続化を試みる。両者を型で区別することで
/// 「env を誤って永続ストアに書く」事故を構造的に防ぐ。
#[derive(Debug, PartialEq, Eq)]
enum Resolution {
    Existing(String),
    Generated(String),
}

/// 参加者 ID の解決順を表す純粋関数 (I/O 非依存・テスト可能)。
///
/// 優先順 (D4): 永続化値 → `GSE_PARTICIPANT_ID` → `GSE_PID` → 自動生成。
/// 永続化値 / env のいずれかが妥当ならそれを `Existing` で返す (再永続化しない)。
/// すべて未設定 / 不正なら `generated` を `Generated` で返す (呼び出し側が永続化)。
fn resolve_with_store(
    persisted: Option<&str>,
    env_primary: Option<&str>,
    env_secondary: Option<&str>,
    generated: &str,
) -> Resolution {
    match first_valid_id(&[persisted, env_primary, env_secondary]) {
        Some(id) => Resolution::Existing(id),
        None => Resolution::Generated(generated.to_string()),
    }
}

/// 参加者 ID を解決する (D4: 完全自動生成 + ローカル永続化)。
///
/// ## 解決順
/// 1. 永続化値 `~/.gse/participant_id` (妥当な場合) — 端末ごとに安定し再起動でも不変
/// 2. `GSE_PARTICIPANT_ID` (研究者の明示上書き、永続化はしない)
/// 3. `GSE_PID` (既存 sync スクリプト `metrics/$PID/` と共有、永続化はしない)
/// 4. 自動生成 `P`+12桁hex → `~/.gse/participant_id` に永続化 (env 未設定でも P000 衝突しない)
/// 5. 生成値の書込失敗時のみ `P000` (永続化不能時の安定 fallback)
///
/// env 由来の値は永続ストアに書かない (override に徹する)。不正な env 値は
/// `tracing::warn!` で可視化して次候補へフォールバックする (生値はログに出さない)。
/// リセットは `~/.gse/participant_id` を削除すると次回起動で再生成される。
fn resolve_participant_id() -> String {
    let persisted = load_persisted_id();
    let env_primary = std::env::var("GSE_PARTICIPANT_ID").ok();
    let env_secondary = std::env::var("GSE_PID").ok();

    // warn 出力と実際の採用 (first_valid_id) は同一述語 `is_valid_participant_id` に
    // 依存する。判定基準を変えるときは両者がズレないよう同関数のみを変更すること。
    for (key, val) in [
        ("GSE_PARTICIPANT_ID", &env_primary),
        ("GSE_PID", &env_secondary),
    ] {
        if let Some(raw) = val {
            if !is_valid_participant_id(raw.trim()) {
                tracing::warn!(
                    env_key = key,
                    "participant id from env rejected (must be [A-Za-z0-9_-], 1..=64 chars); falling back"
                );
            }
        }
    }

    let generated = generate_participant_id();
    match resolve_with_store(
        persisted.as_deref(),
        env_primary.as_deref(),
        env_secondary.as_deref(),
        &generated,
    ) {
        Resolution::Existing(id) => id,
        Resolution::Generated(id) => match persist_id(&id) {
            Ok(()) => {
                tracing::info!(
                    participant_id = %id,
                    "generated and persisted new participant id (~/.gse/participant_id)"
                );
                id
            }
            Err(e) => {
                tracing::warn!(
                    error = %e,
                    "failed to persist generated participant id; using P000 fallback"
                );
                DEFAULT_PARTICIPANT_ID.to_string()
            }
        },
    }
}

/// セッションログの保存先パスを決定する。
///
/// ## 優先順位 (2 段、明示的制御)
/// 1. 環境変数 `GSE_DATASET` が設定されていれば `$GSE_DATASET/raw/<participant_id>/`
/// 2. そうでなければ fallback `~/Documents/GSE-sessions/`
///
/// 参加者 ID は `resolve_participant_id()` が 永続化値 `~/.gse/participant_id` →
/// `GSE_PARTICIPANT_ID` → `GSE_PID` → 自動生成 (`P`+12桁hex, 永続化) → `P000` の順で
/// 解決する。env 未設定でも端末ごとに一意な ID が自動付与・永続化されるため、複数被験者が
/// 各自の端末で操作しても `P000` には衝突しない。fallback 経路 (`~/Documents/GSE-sessions/`)
/// は従来どおり参加者 ID を含まない。
///
/// ## 以前の挙動との差分
/// 旧実装は exe の兄弟を最大 5 階層上まで走査して `gse-dataset/raw/P000/` を
/// 暗黙的に優先していたが、CI・別開発マシン・Tauri bundle 配布先で予期しないパス
/// に書き込むリスクがあったため、20260416 に env + fallback の 2 段に簡素化した。
/// 20260619 に参加者 ID を `P000` 固定から env 可変へ拡張 (Part 1)、さらに完全自動生成 +
/// `~/.gse/participant_id` 永続化へ拡張した (Part 2 / D4。複数参加者のデータ収集対応)。
/// 開発者が `gse-dataset` リポジトリに書きたい場合は shell rc / PowerShell
/// `$PROFILE` で `GSE_DATASET` を明示的に設定する (docs/development-guidelines.md §Session データ管理 参照)。
///
/// ## 可観測性
/// 決定したディレクトリと参加者 ID は `tracing::info!` で常時出力する。どのセッションが
/// どの参加者 ID でどこに書かれたかが運用ログから即確認できる。
pub fn default_log_path() -> PathBuf {
    let participant_id = resolve_participant_id();
    let dir = if let Ok(dataset) = std::env::var("GSE_DATASET") {
        PathBuf::from(dataset).join("raw").join(&participant_id)
    } else {
        fallback_log_dir()
    };
    tracing::info!(
        resolved_log_dir = %dir.display(),
        participant_id = %participant_id,
        source = if std::env::var("GSE_DATASET").is_ok() { "GSE_DATASET env" } else { "fallback (Documents/GSE-sessions)" },
        "session log path resolved"
    );

    let ts = chrono_like_filename();
    dir.join(format!("gse_{}.ndjson", ts))
}

/// フォールバック: ~/Documents/GSE-sessions/
fn fallback_log_dir() -> PathBuf {
    let base = std::env::var("USERPROFILE")
        .or_else(|_| std::env::var("HOME"))
        .unwrap_or_else(|_| ".".to_string());
    PathBuf::from(base).join("Documents").join("GSE-sessions")
}

/// chrono 非依存のタイムスタンプ文字列生成 (標準ライブラリのみ)
fn chrono_like_filename() -> String {
    // UNIX時刻から YYYYMMDD_HHMMSS を近似生成
    // 完全な精度は不要 (セッション識別に使うだけ)
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    // 2000-01-01 00:00:00 UTC からの秒数ベースで日時を概算
    // 注: 簡易実装のためタイムゾーンはUTC
    let days_since_epoch = secs / 86400;
    let time_of_day = secs % 86400;
    let h = time_of_day / 3600;
    let m = (time_of_day % 3600) / 60;
    let s = time_of_day % 60;

    // グレゴリオ暦変換 (ユリウス通算日から)
    let jd = days_since_epoch + 2440588; // UNIX epoch = JD 2440588
    let a = jd + 32044;
    let b = (4 * a + 3) / 146097;
    let c = a - (146097 * b) / 4;
    let d = (4 * c + 3) / 1461;
    let e = c - (1461 * d) / 4;
    let m_cal = (5 * e + 2) / 153;
    let day = e - (153 * m_cal + 2) / 5 + 1;
    let month = m_cal + 3 - 12 * (m_cal / 10);
    let year = 100 * b + d - 4800 + m_cal / 10;

    format!("{:04}{:02}{:02}_{:02}{:02}{:02}", year, month, day, h, m, s)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn user_label_kind_parse_valid() {
        assert_eq!(UserLabelKind::parse("flow"), Some(UserLabelKind::Flow));
        assert_eq!(
            UserLabelKind::parse("incubation"),
            Some(UserLabelKind::Incubation)
        );
        assert_eq!(UserLabelKind::parse("stuck"), Some(UserLabelKind::Stuck));
    }

    #[test]
    fn user_label_kind_parse_rejects_unknown() {
        assert_eq!(UserLabelKind::parse(""), None);
        assert_eq!(UserLabelKind::parse("Flow"), None); // case-sensitive
        assert_eq!(UserLabelKind::parse("focused"), None);
        assert_eq!(UserLabelKind::parse("flow "), None); // trailing space
    }

    #[test]
    fn user_label_kind_as_str_roundtrip() {
        for k in [
            UserLabelKind::Flow,
            UserLabelKind::Incubation,
            UserLabelKind::Stuck,
        ] {
            assert_eq!(UserLabelKind::parse(k.as_str()), Some(k));
        }
    }

    #[test]
    fn user_label_line_flow_without_recovered() {
        let line = format_user_label_line(1_700_000_000_000, UserLabelKind::Flow, None);
        assert_eq!(
            line,
            r#"{"type":"user_label","t":1700000000000,"label":"flow","recovered_at":null}"#
        );
    }

    #[test]
    fn user_label_line_incubation_without_recovered() {
        let line = format_user_label_line(42, UserLabelKind::Incubation, None);
        assert_eq!(
            line,
            r#"{"type":"user_label","t":42,"label":"incubation","recovered_at":null}"#
        );
    }

    #[test]
    fn user_label_line_stuck_with_recovered() {
        let line = format_user_label_line(1000, UserLabelKind::Stuck, Some(1500));
        assert_eq!(
            line,
            r#"{"type":"user_label","t":1000,"label":"stuck","recovered_at":1500}"#
        );
    }

    #[test]
    fn user_label_line_stuck_without_recovered() {
        let line = format_user_label_line(1000, UserLabelKind::Stuck, None);
        assert_eq!(
            line,
            r#"{"type":"user_label","t":1000,"label":"stuck","recovered_at":null}"#
        );
    }

    #[test]
    fn ime_shadow_line_normal_completion() {
        let line = format_ime_shadow_line(1_700_000_000_000, 1234, 3, false);
        assert_eq!(
            line,
            r#"{"type":"ime_shadow","t":1700000000000,"dwell_ms":1234,"nav":3,"abandon":false}"#
        );
    }

    #[test]
    fn ime_shadow_line_abandoned() {
        let line = format_ime_shadow_line(42, 500, 0, true);
        assert_eq!(
            line,
            r#"{"type":"ime_shadow","t":42,"dwell_ms":500,"nav":0,"abandon":true}"#
        );
    }

    #[test]
    fn ime_shadow_line_zero_dwell_and_nav() {
        let line = format_ime_shadow_line(1000, 0, 0, false);
        assert_eq!(
            line,
            r#"{"type":"ime_shadow","t":1000,"dwell_ms":0,"nav":0,"abandon":false}"#
        );
    }

    #[test]
    fn intervention_decision_line_defer_with_suppression() {
        let line = format_intervention_decision_line(
            1_700_000_000_000,
            "defer",
            0.78,
            0.32,
            0.78,
            4200,
            12_000,
            "high_need_but_low_opportunity",
            &["recent_dismiss".to_string()],
        );
        assert_eq!(
            line,
            r#"{"type":"intervention_decision","t":1700000000000,"action":"defer","need_score":0.7800,"opportunity_score":0.3200,"p_stuck":0.7800,"idle_ms":4200,"wall_accum_ms":12000,"reason":"high_need_but_low_opportunity","suppressed_by":["recent_dismiss"]}"#
        );
    }

    #[test]
    fn user_label_line_flow_with_recovered_is_accepted_but_unusual() {
        // `gse-replay --metrics` は Stuck にしか recovered_at を埋めないが、
        // フォーマッタ自体は label の種類に関係なく数値を受け入れる設計。
        let line = format_user_label_line(1, UserLabelKind::Flow, Some(2));
        assert_eq!(
            line,
            r#"{"type":"user_label","t":1,"label":"flow","recovered_at":2}"#
        );
    }

    // ---- v0.3 較正スモーク: 付随 enum の round-trip ----

    #[test]
    fn new_enums_as_str_roundtrip() {
        for t in [Track::Main, Track::Exploratory] {
            assert_eq!(Track::parse(t.as_str()), Some(t));
        }
        for k in [
            TaskKind::Argumentative,
            TaskKind::Correspondence,
            TaskKind::Creative,
            TaskKind::VibeCoding,
        ] {
            assert_eq!(TaskKind::parse(k.as_str()), Some(k));
        }
        for s in [ProbeSource::RandomProbe, ProbeSource::SelfMarker] {
            assert_eq!(ProbeSource::parse(s.as_str()), Some(s));
        }
        for r in [
            SkipReason::None,
            SkipReason::DontRemember,
            SkipReason::Dismissed,
        ] {
            assert_eq!(SkipReason::parse(r.as_str()), Some(r));
        }
        for q in [
            ExpectedQuadrant::Flow,
            ExpectedQuadrant::Stuck,
            ExpectedQuadrant::Incubation,
            ExpectedQuadrant::Idle,
        ] {
            assert_eq!(ExpectedQuadrant::parse(q.as_str()), Some(q));
        }
    }

    #[test]
    fn new_enums_parse_rejects_unknown() {
        assert_eq!(Track::parse("Main"), None); // case-sensitive
        assert_eq!(TaskKind::parse("coding"), None);
        assert_eq!(ProbeSource::parse(""), None);
        assert_eq!(SkipReason::parse("skip"), None);
        assert_eq!(ExpectedQuadrant::parse("focused"), None);
    }

    // ---- session_meta ----

    #[test]
    fn session_meta_line_main_vibe_coding() {
        // condition / label_pool 省略時は null を出す (旧フィクスチャ互換)。
        let line = format_session_meta_line(
            1_700_000_000_000,
            Track::Main,
            TaskKind::VibeCoding,
            false,
            true,
            None,
            None,
        );
        assert_eq!(
            line,
            r#"{"type":"session_meta","track":"main","task_kind":"vibe_coding","monk_mode":false,"intervention_enabled":true,"condition":null,"label_pool":null,"ts":1700000000000}"#
        );
    }

    #[test]
    fn session_meta_line_exploratory_monk_mode() {
        let line = format_session_meta_line(
            42,
            Track::Exploratory,
            TaskKind::Argumentative,
            true,
            false,
            None,
            None,
        );
        assert_eq!(
            line,
            r#"{"type":"session_meta","track":"exploratory","task_kind":"argumentative","monk_mode":true,"intervention_enabled":false,"condition":null,"label_pool":null,"ts":42}"#
        );
    }

    #[test]
    fn session_meta_line_with_condition_and_label_pool() {
        let line = format_session_meta_line(
            7,
            Track::Main,
            TaskKind::Creative,
            false,
            true,
            Some(Condition::BlindCalibration),
            Some(LabelPool::CalibrationBlind),
        );
        assert_eq!(
            line,
            r#"{"type":"session_meta","track":"main","task_kind":"creative","monk_mode":false,"intervention_enabled":true,"condition":"blind_calibration","label_pool":"calibration_blind","ts":7}"#
        );
    }

    // ---- paste / intervention_response ----

    #[test]
    fn paste_line_with_and_without_chars() {
        assert_eq!(
            format_paste_line(1234, Some(42)),
            r#"{"type":"paste","t":1234,"external_paste_chars":42}"#
        );
        assert_eq!(
            format_paste_line(5678, None),
            r#"{"type":"paste","t":5678,"external_paste_chars":null}"#
        );
    }

    #[test]
    fn intervention_response_line_basic() {
        // Nudge dismiss (elapsed_ms=None) は従来出力と byte 同一 (後方互換)。
        assert_eq!(
            format_intervention_response_line(99, "nudge", DismissReason::WantToStruggle, None),
            r#"{"type":"intervention_response","t":99,"action":"nudge","reason":"want_to_struggle"}"#
        );
    }

    #[test]
    fn intervention_response_line_wall_with_elapsed() {
        // Wall 早期解除 (elapsed_ms=Some) は経過時間を含む。
        assert_eq!(
            format_intervention_response_line(
                12345,
                "wall",
                DismissReason::EarlyUnlock,
                Some(45_000)
            ),
            r#"{"type":"intervention_response","t":12345,"action":"wall","reason":"early_unlock","elapsed_ms":45000}"#
        );
        // Wall 通常解除 (順守)。
        assert_eq!(
            format_intervention_response_line(
                67890,
                "wall",
                DismissReason::Completed,
                Some(121_500)
            ),
            r#"{"type":"intervention_response","t":67890,"action":"wall","reason":"completed","elapsed_ms":121500}"#
        );
    }

    #[test]
    fn new_enums_roundtrip() {
        for r in [
            DismissReason::NotStuck,
            DismissReason::WantToStruggle,
            DismissReason::JustClose,
            DismissReason::Silent,
            DismissReason::EarlyUnlock,
            DismissReason::Completed,
            DismissReason::IdleTimeout,
        ] {
            assert_eq!(DismissReason::parse(r.as_str()), Some(r));
        }
        for c in [
            Condition::BlindCalibration,
            Condition::A,
            Condition::B,
            Condition::Nudge,
            Condition::Defer,
            Condition::Baseline,
        ] {
            assert_eq!(Condition::parse(c.as_str()), Some(c));
        }
        for p in [LabelPool::CalibrationBlind, LabelPool::PostIntervention] {
            assert_eq!(LabelPool::parse(p.as_str()), Some(p));
        }
        assert_eq!(DismissReason::parse("nope"), None);
        assert_eq!(Condition::parse(""), None);
        assert_eq!(LabelPool::parse("pool"), None);
    }

    // ---- probe_assignment ----

    #[test]
    fn probe_assignment_line_basic() {
        let line = format_probe_assignment_line("p-001", 1_700_000_000_000, 95_000);
        assert_eq!(
            line,
            r#"{"type":"probe_assignment","probe_id":"p-001","scheduled_ts":1700000000000,"session_elapsed_ms":95000}"#
        );
    }

    #[test]
    fn probe_assignment_line_escapes_probe_id() {
        // probe_id は生成済み不透明 ID の想定だが、escape で JSON injection を防ぐ。
        let line = format_probe_assignment_line("a\"b", 1, 2);
        assert_eq!(
            line,
            r#"{"type":"probe_assignment","probe_id":"a\"b","scheduled_ts":1,"session_elapsed_ms":2}"#
        );
    }

    // ---- realtime_label ----

    #[test]
    fn realtime_label_line_answered_random_probe() {
        let entry = LogEntry::realtime_label_answered(
            1_700_000_000_000,
            &ProbeRef::RandomProbe {
                probe_id: "p-001".to_string(),
            },
            3,
            4,
            2500,
            1_699_999_969_000,
            1_699_999_999_000,
        );
        let LogEntry::RealtimeLabel {
            timestamp,
            probe_id,
            source,
            q1_friction,
            q2_progress,
            answered,
            skip_reason,
            latency_ms,
            analysis_window_start_ms,
            analysis_window_end_ms,
        } = entry
        else {
            panic!("expected RealtimeLabel");
        };
        let line = format_realtime_label_line(
            timestamp,
            probe_id.as_deref(),
            source,
            q1_friction,
            q2_progress,
            answered,
            skip_reason,
            latency_ms,
            analysis_window_start_ms,
            analysis_window_end_ms,
        );
        assert_eq!(
            line,
            r#"{"type":"realtime_label","probe_id":"p-001","source":"random_probe","q1_friction":3,"q2_progress":4,"answered":true,"skip_reason":"none","latency_ms":2500,"analysis_window_start_ms":1699999969000,"analysis_window_end_ms":1699999999000,"ts":1700000000000}"#
        );
    }

    #[test]
    fn realtime_label_answered_clamps_q_to_1_5() {
        let entry = LogEntry::realtime_label_answered(
            1,
            &ProbeRef::SelfMarker,
            0, // → 1
            9, // → 5
            0,
            0,
            0,
        );
        let LogEntry::RealtimeLabel {
            q1_friction,
            q2_progress,
            ..
        } = entry
        else {
            panic!("expected RealtimeLabel");
        };
        assert_eq!(q1_friction, Some(1));
        assert_eq!(q2_progress, Some(5));
    }

    #[test]
    fn realtime_label_self_marker_has_null_probe_id() {
        let entry = LogEntry::realtime_label_answered(1, &ProbeRef::SelfMarker, 2, 2, 0, 0, 0);
        let LogEntry::RealtimeLabel {
            probe_id, source, ..
        } = entry
        else {
            panic!("expected RealtimeLabel");
        };
        assert_eq!(probe_id, None);
        assert_eq!(source, ProbeSource::SelfMarker);
        // フォーマット時に probe_id が null になる。
        let line = format_realtime_label_line(
            1,
            None,
            ProbeSource::SelfMarker,
            Some(2),
            Some(2),
            true,
            SkipReason::None,
            0,
            0,
            0,
        );
        assert!(line.contains(r#""probe_id":null"#));
        assert!(line.contains(r#""source":"self_marker""#));
    }

    #[test]
    fn realtime_label_skipped_has_null_q_and_reason() {
        let entry = LogEntry::realtime_label_skipped(
            7,
            &ProbeRef::RandomProbe {
                probe_id: "p-9".to_string(),
            },
            SkipReason::DontRemember,
            800,
            0,
            0,
        );
        let LogEntry::RealtimeLabel {
            probe_id,
            q1_friction,
            q2_progress,
            answered,
            skip_reason,
            ..
        } = entry
        else {
            panic!("expected RealtimeLabel");
        };
        assert_eq!(probe_id.as_deref(), Some("p-9"));
        assert_eq!(q1_friction, None);
        assert_eq!(q2_progress, None);
        assert!(!answered);
        assert_eq!(skip_reason, SkipReason::DontRemember);

        let line = format_realtime_label_line(
            7,
            Some("p-9"),
            ProbeSource::RandomProbe,
            None,
            None,
            false,
            SkipReason::DontRemember,
            800,
            0,
            0,
        );
        assert_eq!(
            line,
            r#"{"type":"realtime_label","probe_id":"p-9","source":"random_probe","q1_friction":null,"q2_progress":null,"answered":false,"skip_reason":"dont_remember","latency_ms":800,"analysis_window_start_ms":0,"analysis_window_end_ms":0,"ts":7}"#
        );
    }

    #[test]
    fn realtime_label_skipped_rejects_reason_none() {
        // skip なのに skip_reason=None は不整合 → Dismissed に正規化する。
        let entry =
            LogEntry::realtime_label_skipped(1, &ProbeRef::SelfMarker, SkipReason::None, 0, 0, 0);
        let LogEntry::RealtimeLabel { skip_reason, .. } = entry else {
            panic!("expected RealtimeLabel");
        };
        assert_eq!(skip_reason, SkipReason::Dismissed);
    }

    // ---- vignette_response ----

    #[test]
    fn vignette_response_line_basic() {
        let line =
            format_vignette_response_line(1_700_000_000_000, "v1", ExpectedQuadrant::Flow, 2, 5);
        assert_eq!(
            line,
            r#"{"type":"vignette_response","vignette_id":"v1","expected_quadrant":"flow","q1_friction":2,"q2_progress":5,"ts":1700000000000}"#
        );
    }

    #[test]
    fn vignette_response_line_idle_quadrant() {
        let line = format_vignette_response_line(99, "v8", ExpectedQuadrant::Idle, 1, 1);
        assert_eq!(
            line,
            r#"{"type":"vignette_response","vignette_id":"v8","expected_quadrant":"idle","q1_friction":1,"q2_progress":1,"ts":99}"#
        );
    }

    #[test]
    fn vignette_response_constructor_clamps_q_to_1_5() {
        // DC-4: 構築子経由で q1/q2 が 1..=5 に clamp される (0→1, 9→5)。
        let entry = LogEntry::vignette_response(7, "v3".to_string(), ExpectedQuadrant::Stuck, 0, 9);
        let LogEntry::VignetteResponse {
            q1_friction,
            q2_progress,
            ..
        } = entry
        else {
            panic!("expected VignetteResponse");
        };
        assert_eq!(q1_friction, 1);
        assert_eq!(q2_progress, 5);
    }

    /// 付随 enum の `as_str()` 値を **リテラルで固定**する。`schema_dto.rs` の DTO enum は
    /// `#[serde(rename_all = "snake_case")]` で同じ文字列を生成するが、両側は手書きのため
    /// CI の schema drift check (= DTO 側 emit_schema vs current.json) では logger 側 `as_str`
    /// のタイポ (例 "vibecoding") を検知できない。NDJSON 実出力と schema の整合を守る砦。
    #[test]
    fn new_enum_as_str_matches_schema_snake_case() {
        assert_eq!(Track::Main.as_str(), "main");
        assert_eq!(Track::Exploratory.as_str(), "exploratory");
        assert_eq!(TaskKind::Argumentative.as_str(), "argumentative");
        assert_eq!(TaskKind::Correspondence.as_str(), "correspondence");
        assert_eq!(TaskKind::Creative.as_str(), "creative");
        assert_eq!(TaskKind::VibeCoding.as_str(), "vibe_coding");
        assert_eq!(ProbeSource::RandomProbe.as_str(), "random_probe");
        assert_eq!(ProbeSource::SelfMarker.as_str(), "self_marker");
        assert_eq!(SkipReason::None.as_str(), "none");
        assert_eq!(SkipReason::DontRemember.as_str(), "dont_remember");
        assert_eq!(SkipReason::Dismissed.as_str(), "dismissed");
        assert_eq!(ExpectedQuadrant::Flow.as_str(), "flow");
        assert_eq!(ExpectedQuadrant::Stuck.as_str(), "stuck");
        assert_eq!(ExpectedQuadrant::Incubation.as_str(), "incubation");
        assert_eq!(ExpectedQuadrant::Idle.as_str(), "idle");
    }

    /// writer ループの match アーム経由 (LogEntry → 実ファイル) の end-to-end テスト。
    /// format 関数の単体テストでは捕捉できない **アーム内の引数取り違え** (例: monk_mode と
    /// intervention_enabled の入れ替え) を read-back で守る。
    #[test]
    fn writer_loop_emits_new_variants_to_file() {
        let mut path = std::env::temp_dir();
        path.push(format!(
            "gse_probe_schema_test_{}.ndjson",
            std::process::id()
        ));
        let (_logger, tx, shutdown_rx) = SessionLogger::start(path.clone());

        tx.send(LogEntry::SessionMeta {
            timestamp: 1000,
            track: Track::Main,
            task_kind: TaskKind::VibeCoding,
            monk_mode: false,
            intervention_enabled: true,
            condition: Some(Condition::BlindCalibration),
            label_pool: Some(LabelPool::CalibrationBlind),
        })
        .unwrap();
        tx.send(LogEntry::InterventionResponse {
            timestamp: 1500,
            action: "nudge".to_string(),
            reason: DismissReason::NotStuck,
            elapsed_ms: None,
        })
        .unwrap();
        tx.send(LogEntry::InterventionResponse {
            timestamp: 1600,
            action: "wall".to_string(),
            reason: DismissReason::Completed,
            elapsed_ms: Some(122_345),
        })
        .unwrap();
        tx.send(LogEntry::ProbeAssignment {
            probe_id: "p-1".to_string(),
            scheduled_ts: 2000,
            session_elapsed_ms: 1000,
        })
        .unwrap();
        tx.send(LogEntry::realtime_label_answered(
            3000,
            &ProbeRef::RandomProbe {
                probe_id: "p-1".to_string(),
            },
            3,
            4,
            500,
            2969,
            2999,
        ))
        .unwrap();
        tx.send(LogEntry::VignetteResponse {
            timestamp: 4000,
            vignette_id: "v1".to_string(),
            expected_quadrant: ExpectedQuadrant::Stuck,
            q1_friction: 5,
            q2_progress: 1,
        })
        .unwrap();
        tx.send(LogEntry::End).unwrap();

        // End 処理 (flush + close) 完了を待つ。
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let contents = fs::read_to_string(&path).expect("read back log file");
        let _ = fs::remove_file(&path);

        assert!(contents.contains(
            r#"{"type":"session_meta","track":"main","task_kind":"vibe_coding","monk_mode":false,"intervention_enabled":true,"condition":"blind_calibration","label_pool":"calibration_blind","ts":1000}"#
        ), "session_meta 行が不正 (引数取り違えの可能性):\n{contents}");
        assert!(
            contents.contains(
                r#"{"type":"intervention_response","t":1500,"action":"nudge","reason":"not_stuck"}"#
            ),
            "intervention_response (nudge) 行が不正:\n{contents}"
        );
        assert!(
            contents.contains(
                r#"{"type":"intervention_response","t":1600,"action":"wall","reason":"completed","elapsed_ms":122345}"#
            ),
            "intervention_response (wall) 行が不正:\n{contents}"
        );
        assert!(contents.contains(
            r#"{"type":"probe_assignment","probe_id":"p-1","scheduled_ts":2000,"session_elapsed_ms":1000}"#
        ), "probe_assignment 行が不正:\n{contents}");
        assert!(contents.contains(
            r#"{"type":"realtime_label","probe_id":"p-1","source":"random_probe","q1_friction":3,"q2_progress":4,"answered":true,"skip_reason":"none","latency_ms":500,"analysis_window_start_ms":2969,"analysis_window_end_ms":2999,"ts":3000}"#
        ), "realtime_label 行が不正:\n{contents}");
        assert!(contents.contains(
            r#"{"type":"vignette_response","vignette_id":"v1","expected_quadrant":"stuck","q1_friction":5,"q2_progress":1,"ts":4000}"#
        ), "vignette_response 行が不正:\n{contents}");
    }

    /// ペーストイベントが NDJSON に「時刻のみ」で記録され、クリップボードの中身に
    /// 相当するフィールド (text/content/data 等) が一切出力されないことを read-back で保証する
    /// (data-privacy: 回数のみ・中身禁止)。
    #[test]
    fn writer_loop_emits_paste_event_count_only() {
        let mut path = std::env::temp_dir();
        path.push(format!(
            "gse_paste_schema_test_{}.ndjson",
            std::process::id()
        ));
        let (_logger, tx, shutdown_rx) = SessionLogger::start(path.clone());

        tx.send(LogEntry::Paste {
            timestamp: 1234,
            external_paste_chars: Some(42),
        })
        .unwrap();
        tx.send(LogEntry::Paste {
            timestamp: 5678,
            external_paste_chars: None,
        })
        .unwrap();
        tx.send(LogEntry::End).unwrap();

        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let contents = fs::read_to_string(&path).expect("read back log file");
        let _ = fs::remove_file(&path);

        // 1 ペースト = 1 行・時刻 + 文字数のみ。回数は行数で算出できる。
        assert!(
            contents.contains(r#"{"type":"paste","t":1234,"external_paste_chars":42}"#),
            "paste 行が不正:\n{contents}"
        );
        assert!(
            contents.contains(r#"{"type":"paste","t":5678,"external_paste_chars":null}"#),
            "paste 行が不正:\n{contents}"
        );
        let paste_lines = contents
            .lines()
            .filter(|l| l.contains(r#""type":"paste""#))
            .count();
        assert_eq!(paste_lines, 2, "ペースト回数=行数が一致しない:\n{contents}");

        // クリップボードの中身に相当するキーが NDJSON に存在しないこと (中身記録禁止)。
        // external_paste_chars は文字数 (整数) のみで中身ではない (どの forbidden 部分文字列も含まない)。
        for forbidden in ["text", "content", "data", "clipboard", "payload"] {
            assert!(
                !contents.contains(forbidden),
                "paste ログに中身相当フィールド '{forbidden}' が混入:\n{contents}"
            );
        }
    }

    // --- 参加者 ID 解決 / バリデーション ---

    #[test]
    fn participant_id_accepts_canonical_and_extended() {
        // 参加者 ID 規約 (P000/P003 等) と allowlist 内の拡張形を許可
        assert!(is_valid_participant_id("P000"));
        assert!(is_valid_participant_id("P003"));
        assert!(is_valid_participant_id("P123"));
        assert!(is_valid_participant_id("pilot_01"));
        assert!(is_valid_participant_id("a-b_C9"));
    }

    #[test]
    fn participant_id_rejects_empty() {
        assert!(!is_valid_participant_id(""));
    }

    #[test]
    fn participant_id_rejects_path_traversal() {
        // パストラバーサル / パス区切りは構造的に拒否
        assert!(!is_valid_participant_id("."));
        assert!(!is_valid_participant_id(".."));
        assert!(!is_valid_participant_id("../secret"));
        assert!(!is_valid_participant_id("..\\secret"));
        assert!(!is_valid_participant_id("a/b"));
        assert!(!is_valid_participant_id("a\\b"));
        assert!(!is_valid_participant_id("P000/../P001"));
    }

    #[test]
    fn participant_id_rejects_special_chars() {
        assert!(!is_valid_participant_id("P 000")); // 空白
        assert!(!is_valid_participant_id("P\0")); // null
        assert!(!is_valid_participant_id("P000\n")); // 改行
        assert!(!is_valid_participant_id("P:000")); // ドライブ/コロン
        assert!(!is_valid_participant_id("~")); // ホーム展開記号
        assert!(!is_valid_participant_id("$HOME")); // 変数展開記号
    }

    #[test]
    fn participant_id_length_boundary() {
        let max = "P".repeat(MAX_PARTICIPANT_ID_LEN);
        assert!(is_valid_participant_id(&max)); // 64 は OK
        let over = "P".repeat(MAX_PARTICIPANT_ID_LEN + 1);
        assert!(!is_valid_participant_id(&over)); // 65 は NG
    }

    #[test]
    fn participant_id_rejects_windows_reserved_names() {
        // 大文字小文字を問わず予約デバイス名は拒否
        for name in ["CON", "con", "Nul", "PRN", "aux", "COM1", "lpt9"] {
            assert!(!is_valid_participant_id(name), "{name} は拒否されるべき");
        }
        // 予約名を部分に含むだけ (完全一致でない) なら許可
        assert!(is_valid_participant_id("CON1"));
        assert!(is_valid_participant_id("CONSOLE"));
        assert!(is_valid_participant_id("P_CON"));
        assert!(is_valid_participant_id("COM10")); // 予約は COM1..=COM9 のみ
    }

    #[test]
    fn first_valid_id_prefers_first() {
        assert_eq!(
            first_valid_id(&[Some("P001"), Some("P002")]).as_deref(),
            Some("P001")
        );
    }

    #[test]
    fn first_valid_id_skips_invalid_to_next() {
        // 先頭が未設定 / 不正なら後続へ
        assert_eq!(
            first_valid_id(&[None, Some("P002")]).as_deref(),
            Some("P002")
        );
        assert_eq!(
            first_valid_id(&[Some("../bad"), Some("P002")]).as_deref(),
            Some("P002")
        );
    }

    #[test]
    fn first_valid_id_none_when_all_absent_or_invalid() {
        // すべて未設定 / 不正なら None (呼び出し側が自動生成 / P000 に委ねる)
        assert_eq!(first_valid_id(&[None, None]), None);
        assert_eq!(first_valid_id(&[Some(""), Some("..")]), None);
    }

    #[test]
    fn first_valid_id_trims_whitespace() {
        // 前後空白は trim してから検証
        assert_eq!(first_valid_id(&[Some("  P005  ")]).as_deref(), Some("P005"));
    }

    // --- 自動生成 (Part 2 / D4) ---

    #[test]
    fn generated_id_has_expected_format() {
        let id = generate_participant_id();
        // `P` + 12 桁 hex = 13 文字。allowlist を必ず通過する。
        assert_eq!(id.len(), 13, "P + 12 hex = 13 文字: {id}");
        assert!(id.starts_with('P'), "先頭は P: {id}");
        assert!(
            id[1..].bytes().all(|b| b.is_ascii_hexdigit()),
            "P 以降は hex のみ: {id}"
        );
        assert!(
            is_valid_participant_id(&id),
            "生成 ID は is_valid_participant_id を通過する: {id}"
        );
    }

    #[test]
    fn generated_id_is_not_constant() {
        // 乱数由来であること (定数フォールバックの退行検知)。48bit から複数引いて
        // 全て同一になる確率は無視できる。
        let ids: std::collections::HashSet<String> =
            (0..50).map(|_| generate_participant_id()).collect();
        assert!(ids.len() > 1, "生成 ID が乱数化されていない: {ids:?}");
    }

    // --- 解決順 (Part 2 / D4): 永続化値 → env → 自動生成 ---

    #[test]
    fn resolve_with_store_prefers_persisted_over_env_and_generated() {
        let r = resolve_with_store(Some("Pstored"), Some("P001"), Some("P002"), "Pgenerated");
        assert_eq!(r, Resolution::Existing("Pstored".to_string()));
    }

    #[test]
    fn resolve_with_store_env_primary_over_secondary_and_generated() {
        // 永続化値が無ければ GSE_PARTICIPANT_ID → GSE_PID の順。
        let r = resolve_with_store(None, Some("P001"), Some("P002"), "Pgenerated");
        assert_eq!(r, Resolution::Existing("P001".to_string()));
        let r = resolve_with_store(None, Some("../bad"), Some("P002"), "Pgenerated");
        assert_eq!(r, Resolution::Existing("P002".to_string()));
    }

    #[test]
    fn resolve_with_store_env_is_not_persisted() {
        // env 由来の値は `Existing` で返る = 呼び出し側は永続化しない (D4 ③)。
        // `Generated` でないことを型レベルで保証する。
        let r = resolve_with_store(None, Some("P003"), None, "Pgenerated");
        assert_eq!(r, Resolution::Existing("P003".to_string()));
        assert!(
            !matches!(r, Resolution::Generated(_)),
            "env 値は Generated にならない (永続化対象でない)"
        );
    }

    #[test]
    fn resolve_with_store_generates_when_all_absent_or_invalid() {
        // 永続化値も env も無い / 不正 → 自動生成 ID を Generated で返す (永続化対象)。
        let r = resolve_with_store(None, None, None, "Pgenerated");
        assert_eq!(r, Resolution::Generated("Pgenerated".to_string()));
        let r = resolve_with_store(Some("  "), Some("../x"), Some(""), "Pgenerated");
        assert_eq!(r, Resolution::Generated("Pgenerated".to_string()));
    }

    #[test]
    fn resolve_with_store_skips_invalid_persisted_to_env() {
        // 永続化値が壊れていても env が妥当ならそちらを採用 (再永続化はしない)。
        let r = resolve_with_store(Some("../evil"), Some("P007"), None, "Pgenerated");
        assert_eq!(r, Resolution::Existing("P007".to_string()));
    }

    // --- 永続化 I/O 往復 (Part 2 / D4): env を触らず一時ファイルで結線を検証 ---

    #[test]
    fn persist_and_load_roundtrip_without_env() {
        // env / home を汚さないため、明示パス経由の `persist_id_to`/`load_id_from` で
        // 「生成 → 永続 → 再読込で同一 ID」「不在 → None」「不正値 → reject」「上書き」を検証する。
        let mut dir = std::env::temp_dir();
        dir.push(format!("gse_pid_roundtrip_{}", std::process::id()));
        let path = dir.join("participant_id");

        // 生成 ID を永続化し、再読込で同一値が返る (= D4「再起動でも不変」の核)。
        let id = generate_participant_id();
        persist_id_to(&path, &id).expect("persist should succeed");
        assert_eq!(load_id_from(&path).as_deref(), Some(id.as_str()));

        // 上書き (atomic rename) で値が更新される。
        persist_id_to(&path, "P000").expect("overwrite should succeed");
        assert_eq!(load_id_from(&path).as_deref(), Some("P000"));

        // 手編集で不正値が混入しても trim 後に reject → None (path injection 防御の往復確認)。
        fs::write(&path, "../evil").expect("write bad value");
        assert_eq!(load_id_from(&path), None);

        // ファイル不在は None。
        fs::remove_file(&path).expect("remove");
        assert_eq!(load_id_from(&path), None);

        let _ = fs::remove_dir_all(&dir);
    }
}
