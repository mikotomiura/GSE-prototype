use std::fs::{self, File};
use std::io::{self, BufWriter, Write};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use crossbeam_channel::{bounded, Receiver, RecvTimeoutError, Sender};
use rand::Rng;

use crate::analysis::anonymize::KeyCategory;
use crate::analysis::heads::{HeadId, TaskDomain};

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

/// ADR-006 Alternative C のルーティング: **宣言された `task_kind` が domain head を選ぶ**。
///
/// ⚠️ **変換をここに 1 本だけ置く。** `lib.rs` (本番) も `bin/replay.rs` (リプレイ) も
/// この経路を通す。2 箇所に書くと片方だけ更新されて本番とリプレイの挙動がずれる
/// (= ゴールデンが守れなくなる)。
///
/// ⚠️ 依存方向: `logger` → `analysis` は既存 (`HMM_VERSION` を参照している) なので
/// この向きで置く。逆に `analysis` 側へ `TaskKind` を持ち込むと
/// `analysis` が `logger` に依存してしまい `docs/repository-structure.md` §4 に反する。
///
/// ⚠️ `_ =>` を書かないこと。`TaskKind` に variant を足したら**必ず head を決めさせる**。
impl From<TaskKind> for TaskDomain {
    fn from(kind: TaskKind) -> Self {
        match kind {
            // 論述・文通は Writing head (Phase1 で走っていた挙動そのもの)
            TaskKind::Argumentative | TaskKind::Correspondence => TaskDomain::Writing,
            // Creative は打鍵 β が原理的に不適 (ADR-006 #3) だが代替 head がまだ無い。
            // 数値挙動は Writing と同一のまま、head_id だけ分けて事後に分離可能にする
            // (.steering/20260818-adr006-head-extraction-wiring/decisions.md D-6)
            TaskKind::Creative => TaskDomain::WritingFallback,
            // ここが 2b で実際に挙動が変わる唯一の分岐
            TaskKind::VibeCoding => TaskDomain::Coding,
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
/// ⚠️★★★ **Wall 応答 (`early_unlock` / `completed` / `idle_timeout`) は 2026-08-23 に削除した**
/// (Wall 自体の削除に伴う・`.steering/20260823-wall-removal/`)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DismissReason {
    NotStuck,
    WantToStruggle,
    JustClose,
    Silent,
}

impl DismissReason {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::NotStuck => "not_stuck",
            Self::WantToStruggle => "want_to_struggle",
            Self::JustClose => "just_close",
            Self::Silent => "silent",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "not_stuck" => Some(Self::NotStuck),
            "want_to_struggle" => Some(Self::WantToStruggle),
            "just_close" => Some(Self::JustClose),
            "silent" => Some(Self::Silent),
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
    reason: &str,
    suppressed_by: &[String],
) -> String {
    let suppressed = serde_json::to_string(suppressed_by).unwrap_or_else(|_| "[]".to_string());
    format!(
        r#"{{"type":"intervention_decision","t":{},"action":"{}","need_score":{:.4},"opportunity_score":{:.4},"p_stuck":{:.4},"idle_ms":{},"reason":"{}","suppressed_by":{}}}"#,
        timestamp, action, need_score, opportunity_score, p_stuck, idle_ms, reason, suppressed,
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

/// `format_feat_line` の引数束。
///
/// ⚠️★ **位置引数にしない理由**: `feat` 行は 13 個の `f64` が連続するため、
/// 位置引数だと呼び出し側で `p_inc`/`p_stuck` や `raw_x`/`raw_y` を**入れ替えても
/// コンパイルが通る**（型が誤りを弾かない・code-reviewer 指摘）。
/// フィールド名で束ねれば、書き出し側は field init shorthand で名前一致が強制される。
struct FeatLine {
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
    keys: u64,
    bs_keys: u64,
}

/// `LogEntry::Feat` の NDJSON 1 行を生成する純粋関数。
///
/// ⚠️★★★ **小数桁数はゴールデンスナップショットの byte-equal 契約そのもの**である
/// (`f1`/`f4`=`{:.2}` / `f5`=`{:.1}` / それ以外の f64=`{:.4}` / `alpha`=`{:.2}`)。
/// 桁数を変えると既存 NDJSON との比較・`gse-replay --metrics` の再解釈が壊れるため、
/// 変更するときは `docs/development-guidelines.md` §3 の手順を踏むこと。
///
/// `keys` / `bs_keys` は **Tier 0 配線 (記録のみ)** で追加した整数フィールドで、
/// 行末に append する (既存フィールドの位置・精度は 1 文字も変えない)。
/// 打鍵の**数**のみで文字内容・VK 生値は含まない (data-privacy)。
fn format_feat_line(v: &FeatLine) -> String {
    format!(
        r#"{{"type":"feat","t":{},"f1":{:.2},"f3":{:.4},"f4":{:.2},"f5":{:.1},"f6":{:.4},"p_flow":{:.4},"p_inc":{:.4},"p_stuck":{:.4},"raw_x":{:.4},"raw_y":{:.4},"ewma_x":{:.4},"ewma_y":{:.4},"obs":{},"alpha":{:.2},"keys":{},"bs_keys":{}}}"#,
        v.timestamp,
        v.f1,
        v.f3,
        v.f4,
        v.f5,
        v.f6,
        v.p_flow,
        v.p_inc,
        v.p_stuck,
        v.raw_x,
        v.raw_y,
        v.ewma_x,
        v.ewma_y,
        v.obs,
        v.alpha,
        v.keys,
        v.bs_keys,
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
#[allow(clippy::too_many_arguments)]
fn format_session_meta_line(
    timestamp: u64,
    track: Track,
    task_kind: TaskKind,
    intervention_enabled: bool,
    condition: Option<Condition>,
    label_pool: Option<LabelPool>,
    head_id: HeadId,
) -> String {
    format!(
        r#"{{"type":"session_meta","track":"{}","task_kind":"{}","intervention_enabled":{},"condition":{},"label_pool":{},"head_id":"{}","ts":{}}}"#,
        track.as_str(),
        task_kind.as_str(),
        intervention_enabled,
        json_opt_str(condition.map(|c| c.as_str())),
        json_opt_str(label_pool.map(|p| p.as_str())),
        head_id.as_str(),
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
    elapsed_ms: u64,
    changes: u16,
) -> String {
    debug_assert!(
        (1..=5).contains(&q1_friction) && (1..=5).contains(&q2_progress),
        "vignette_response: q1/q2 が 1..=5 外"
    );
    format!(
        r#"{{"type":"vignette_response","vignette_id":{},"expected_quadrant":"{}","q1_friction":{},"q2_progress":{},"elapsed_ms":{},"changes":{},"ts":{}}}"#,
        json_opt_str(Some(vignette_id)),
        expected_quadrant.as_str(),
        q1_friction,
        q2_progress,
        elapsed_ms,
        changes,
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
        /// ★ Tier 0 (記録のみ): 特徴量ウィンドウ内の総キー押下数 (= `f3` の分母)。
        ///
        /// **打鍵の「数」だけ**であり、どのキーを押したか・何を書いたかは含まない
        /// (data-privacy CD1: `vk_code` は既存の `key` 行の話で、本行には入らない)。
        /// ⚠️★ HMM にも X/Y 合成式にも流さない。消費者は将来の recovery 推定器のみ。
        /// ⚠️★★★ **累積でも毎秒の打鍵数でもない。窓の右端は最後の打鍵時刻**であり、
        /// **沈黙中は同じ値がくり返し書かれる**（★ 正本: `analysis/loop_step.rs` の
        /// `FeatSnapshot::keys` の doc）。★ **行をまたいで足し上げないこと。**
        keys: u64,
        /// ★ Tier 0 (記録のみ): 特徴量ウィンドウ内の BS/Del 押下数 (= `f3` の分子)。
        ///
        /// `f3` は `{:.4}` 丸めなので `f3 × keys` は整数に戻らない。`keys − bs_keys` を
        /// 丸め誤差なしで得るために整数で別に持つ。窓の意味は `keys` と同じ。
        bs_keys: u64,
    },
    /// IME入力モードの切替イベント
    /// on=true  → 日本語入力モード (あ/カ) に移行 → β_writing を使用
    /// on=false → 英数直接入力モード (A) に移行   → β_coding を使用
    ImeState {
        timestamp: u64,
        on: bool,
        active: bool,
    },
    /// ⚠️★★ キーボードフックの生存状態が変わった (`input::liveness`)。
    ///
    /// 2026-08-09 の Windows 実機で、**5 分間 0 打のブロックが「正常」として自動提出された**
    /// (`windows-verification.md` §5-7)。⚠️ 提出物 (`.age`) だけを見ても
    /// 「打っていない」のか「記録できていない」のか**区別できなかった**のが最大の問題である。
    ///
    /// ★ そこで本行は **判断ではなく測った量** (`starved_ms`) を載せる。
    /// 後から閾値を変えて再解釈でき、解析側 (`analyze.py` / `validate_blocks.py`) が
    /// 「このブロックは無効」と機械判定できる。
    HookHealth {
        timestamp: u64,
        /// false = 「設置済みなのにイベントが届いていない」と判断した状態。
        alive: bool,
        /// 「システムには入力があるのに自前のフックが呼ばれなかった」時間の累積 (ms)。
        starved_ms: u64,
        /// このイベントで**再設置を要求した**か。
        rehook: bool,
        /// ⚠️★ 分析スレッドへ渡せずに**捨てた**打鍵イベントの累計 (プロセス開始から)。
        ///
        /// ★ フックが呼ばれていても channel が詰まれば記録は失われる。
        /// 「呼ばれた」と「記録できた」は別なので、両方を残す。
        dropped: u64,
        /// ⚠️★★★ **前の `hook_health` 行からの `dropped` の増分** (ADR-013 D4・穴 B)。
        ///
        /// ★ `dropped` は**累積カウンタ**なのに、解析側が「この区間で落ちた」と読む誤りが
        /// **実際に起きた** (前タスクの除外規則・code-reviewer HIGH で修正)。
        /// → ⚠️ 改名 (`dropped_total`) は breaking なので採らず、**併記で誤読を消す**。
        ///
        /// ★ 最初の行では「プロセス開始からの増分」＝ `dropped` と同値になる。
        dropped_delta: u64,
    },
    /// ★ **30 秒未満の在席×非打鍵 (micro 帯) を 60 秒窓で数えた行** (ADR-013 D4・穴 A)。
    ///
    /// ## なぜ要るか
    ///
    /// ⚠️ `hook_health` は `liveness::Thresholds::log_after_ms`(30 秒) を越えないと 1 行も出ない。
    /// → ★ **30 秒未満の帯について永久に何も言えない**状態を埋める。
    ///
    /// ## ⚠️★★★ **何を測っていないか** (★ 過大に読ませない・2026-08-19 レビュー指摘)
    ///
    /// `liveness::step` は **`system_input_seen == false` のとき値を凍結する**。
    /// → ★ 本行が数えるのは「**端末に触れてはいるのに打鍵が来ていない**」時間であり、
    /// ⚠️ **マウスにも触れず静止して考えている時間は、ほぼ 0 ms しか計上されない。**
    ///
    /// ⚠️ したがって **[P121] の「局所思考」をそのまま測るものではない。**
    /// ★ 投資判断に使うなら**過小評価の向き**であることを併記すること
    /// (★ 「micro 帯はこれだけしか無い」と読むと誤る)。
    ///
    /// ⚠️ **在席の判定にマウス等の入力が効く**（`GetLastInputInfo` /
    /// `CGEventSourceSecondsSinceLastEventType` は**キー以外も含む**）。
    /// ★ マウスの動き自体は**記録しない**が、この値を左右することは同意文書に開示してある。
    ///
    /// ## ⚠️★★★ `n_lt30 == 0` の窓は出力しない
    ///
    /// 理由は 2 つ: ① ログ量が減る、② **毎分必ず 1 行出す形にしない**。
    ///
    /// ⚠️★★★ **ただし「空窓を出さない」を *プライバシー統制として* 数えてはならない**
    /// (security-checker MEDIUM・2026-08-19 の訂正)。★ 窓は連続しており行は壁時計 `t` を持つので、
    /// **1 行でも出れば窓グリッドの位相が定まり、以後の各窓について「出た/出なかった」の
    /// 二値列が復元できる** —— ★ **出さないこと自体が信号**である。
    ///
    /// ★ **実際に効いている統制はこちら**:
    /// - **60 秒に集計して *位置* を落としている** (本数と合計しか残らない)
    /// - 共有物では `analysis::anonymize` が `t` を `session_start` 相対へ直すので
    ///   **壁時計 (何時に働いたか) は出ない**
    /// - **計測中しか出ない** (セッション外は 1 行も出ない)
    /// - raw はローカル保持 ＋ **ブロック単位のオプトイン送信**
    ///
    /// ★ なお「分単位で打鍵していたか」は **`key` 行から既に完全に導出できる**ので、
    /// 本行の限界情報増分はその軸ではほぼゼロである。⚠️ 新しいのは `sum_lt30_ms` の側 (上記)。
    ///
    /// ## ★ `hook_health` の意味論は 1 文字も変えていない
    ///
    /// ⚠️ 変えると **ADR-011 の探索トラックと ADR-012 Stage 0 が再計算**になる。
    /// ★ 本行は別トラックとして足すだけなので、**≥30 秒トラックの旧ログ (G1 を含む) と
    /// 新ログが同一意味論のまま比較できる**。
    StarveWindow {
        timestamp: u64,
        /// 窓の長さ (ms)。固定 60_000。
        win_ms: u64,
        /// この窓で**閉じた** micro エピソードの本数。⚠️ ★ 0 なら行を出さない。
        n_lt30: u64,
        /// その合計時間 (ms)。⚠️ **失うのは micro 沈黙の *位置*** (本数と合計は残る)。
        sum_lt30_ms: u64,
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
        intervention_enabled: bool,
        condition: Option<Condition>,
        label_pool: Option<LabelPool>,
        /// ★ ADR-006 Phase 2b: **どの domain head がこのセッションを採点したか**。
        ///
        /// `task_kind` から機械的に決まる (`TaskDomain::from`) が、両方を残す。
        /// `task_kind` は**被験者の宣言**、`head_id` は**実際に走った推論器**であり、
        /// ルーティング表が変われば同じ `task_kind` でも別の head になる。
        /// 特に `writing_fallback` (= Creative を Writing head で採点している) を
        /// 事後に分離するために要る (`.steering/.../decisions.md` D-6)。
        ///
        /// ⚠️ `FeatSnapshot` ではなくここに置く。`FeatSnapshot` に足すと
        /// ゴールデン snapshot が全滅して 2b の acceptance (既存 4 本 byte-equal) が消える。
        head_id: HeadId,
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
    ///
    /// `elapsed_ms` / `changes` は「読まずに送った」回答を事後に分離するための
    /// content-free な回答挙動メタ (data-privacy ルール 1: 数値のみ・本文を含まない)。
    VignetteResponse {
        timestamp: u64,
        vignette_id: String,
        expected_quadrant: ExpectedQuadrant,
        q1_friction: u8,
        q2_progress: u8,
        /// 場面の表示から**記録に成功するまで**の所要時間 (ms)。
        /// 送信失敗による再送があった場合は初回表示からの累積。
        elapsed_ms: u64,
        /// Q1/Q2 スライダー合計の値変更回数。即答と熟慮を分ける。
        changes: u16,
    },
    /// ⚠️★★★ **記録の一時停止 / 再開の遷移マーカー** (O1 / ADR-014 **D7-ii**)。
    ///
    /// ★ 被験者が「止める」「再開する」を押した**瞬間**に 1 行だけ書く。
    /// ⚠️ 状態が変わらない押下（連打）では**書かない** —— ★ 押した回数は研究に要らないし、
    /// **回数を残すと「何回止めたか」という行動記録になる**（同意文書に無い記録）。
    ///
    /// ## ⚠️★★★ なぜ「止めた」を記録するのか（★ 一見矛盾している）
    ///
    /// ★ ADR-013 **D1** と同じ理屈である —— ⚠️ 書かないと解析側は
    /// 「**被験者が止めていた 3 時間**」と「**本当に何も起きなかった 3 時間**」を
    /// **永久に区別できない**。→ ★ `left_observation` の内訳を割るという O1 の目的が壊れる。
    ///
    /// ⚠️ **記録するのは遷移の時刻と向きだけ**である。★ 理由は聞かないし、書かない。
    RecordingPause { timestamp: u64, paused: bool },
    /// ⚠️★★★ **フォーカス遷移の時刻**（O1 / ADR-014 **D4** の L-c）。
    ///
    /// ★ 持つのは **時刻 1 個だけ**である。⚠️ HWND / PID / アプリ識別子 /
    /// ウィンドウタイトル / 通し番号は **1 バイトも持たない**（D4 の禁止表）。
    ///
    /// ## ⚠️ これで何が言えて、何が言えないか
    ///
    /// | ★ 言える | ⚠️ 言えない |
    /// |---|---|
    /// | 遷移が**いつ**起きたか / **離脱の滞在時間**（2 時刻の差） | ⚠️ **どこへ行ったか**（アプリ・用途・役割） |
    /// | 遷移の**頻度分布** | ⚠️★★★ **「注意の逸脱の頻度」ではない** —— ★ 同一アプリ内のウィンドウ切替も同じ 1 行になる（両 OS とも識別子なしには分離不能・D4 の禁止表） |
    FocusTransition { timestamp: u64 },
    /// ⚠️★★★ **ポインタ活動の 1 秒ビン**（O1 / ADR-014 **D4** の L-b）。
    ///
    /// ★ 中身は [`crate::analysis::pointer_bin::PointerBin`] の量子化スカラだけ。
    /// ⚠️ **ゼロ抑制**されているので、活動が無い秒には行が無い（D5）。
    PointerBin {
        timestamp: u64,
        moved: u8,
        buttons: u8,
        wheel: u8,
    },
    /// ⚠️★★★ **`EnableSecureEventInput` の区間フラグ**（O1 / **macOS のみ**）。
    ///
    /// ★ 有効な間は **tap が「有効」のまま KeyDown だけが届かない**。
    /// → ⚠️ この行が無いと「**打鍵ゼロ**」と「**打鍵が見えない**」を混同し、
    /// **パスワード入力の直後に必ず Stuck / Incubation へ倒れる系統的バイアス**が入る。
    ///
    /// ⚠️ **中身は一切取得しない。** ★ on/off の遷移だけである。
    SecureInput { timestamp: u64, on: bool },
    /// **G1: ブロック終了マーカー。** 現ファイルに `session_end` を書いて flush するが、
    /// ★ **書込先は切り替えない**。切り替えは次の `Rotate` が行う。
    ///
    /// ★ なぜ 2 段階に分けるか: ブロック終了時に新ファイルを開くと、10 ブロック目の後に
    /// **中身が `meta` 1 行だけの 11 本目**が残る。`gse-submit` は
    /// `find_latest_session_ndjson` で**最新 1 本**を選ぶので、
    /// ⚠️ ★ **被験者が「提出する」を押すと空ファイルが出てしまう**。
    /// → 開くのは「次のブロックを始めるとき」だけにする。
    BlockEnd,
    /// **G1: 書込先を次のブロック用に切り替える。**
    ///
    /// 現ファイルを (まだなら `session_end` を書いてから) 閉じ、`new_path` を開いて
    /// ⚠️ ★ **新ファイルの実時刻で `meta`(session_start) を書く**。
    /// `analysis::anonymize::find_session_start` が `t` の基点にするのがこの行なので、
    /// 前ファイルの値を引き継ぐと**匿名化後の時刻が全部ずれる**。
    Rotate { new_path: PathBuf },
    /// セッション終了マーカー
    End,
}

impl LogEntry {
    /// このエントリが NDJSON に書く `"type"` の値。★ **制御用の内部エントリは `None`**。
    ///
    /// ## ⚠️★★★ なぜ要るのか
    ///
    /// ★ 一時停止 (`recording::is_writable_while_paused`) の判断を **1 か所**に閉じるため。
    /// ⚠️ 判断を writer の match 腕（19 個）に散らすと、★ **新しい行種を足した人が
    /// 一時停止の考慮を忘れ、止めたはずの記録が黙って残る**。
    ///
    /// ★ 値は `capabilities::KNOWN_LINE_TYPES` と一致していなければならない
    /// （[`tests::line_type_matches_known_line_types`] が機械的に固定する）。
    pub fn line_type(&self) -> Option<&'static str> {
        Some(match self {
            LogEntry::Key { .. } => "key",
            LogEntry::Paste { .. } => "paste",
            LogEntry::Feat { .. } => "feat",
            LogEntry::ImeState { .. } => "ime_state",
            LogEntry::ImeShadow { .. } => "ime_shadow",
            LogEntry::HookHealth { .. } => "hook_health",
            LogEntry::StarveWindow { .. } => "starve_window",
            LogEntry::SessionStart { .. } => "session_start",
            LogEntry::UserLabel { .. } => "user_label",
            LogEntry::ReviewMarker { .. } => "review_marker",
            LogEntry::SessionMeta { .. } => "session_meta",
            LogEntry::ProbeAssignment { .. } => "probe_assignment",
            LogEntry::RealtimeLabel { .. } => "realtime_label",
            LogEntry::VignetteResponse { .. } => "vignette_response",
            LogEntry::InterventionDecision { .. } => "intervention_decision",
            LogEntry::InterventionResponse { .. } => "intervention_response",
            LogEntry::RecordingPause { .. } => "recording_pause",
            LogEntry::FocusTransition { .. } => "focus_transition",
            LogEntry::PointerBin { .. } => "pointer_bin",
            LogEntry::SecureInput { .. } => "secure_input",
            // ★ ここから下は**行を書かない制御エントリ**である
            //   (`BlockEnd` / `Rotate` は `meta`(session_end/session_start) を副作用で書くが、
            //   ⚠️ それは `meta` 行であってこのエントリ自身の行ではない)。
            LogEntry::BlockEnd | LogEntry::Rotate { .. } | LogEntry::End => return None,
        })
    }

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
        elapsed_ms: u64,
        changes: u16,
    ) -> Self {
        LogEntry::VignetteResponse {
            timestamp,
            vignette_id,
            expected_quadrant,
            q1_friction: q1_friction.clamp(1, 5),
            q2_progress: q2_progress.clamp(1, 5),
            elapsed_ms,
            changes,
        }
    }
}

/// ログ書込先の確定結果。`SessionLogger::start` が返し、`run()` が UI へ fail-loud するための情報源。
///
/// **背景 (#1 層2 / blockers B1)**: 旧実装は consumer スレッド内で `File::create` が失敗すると
/// `tracing::error` のみ残して early return → スレッド死亡 → 以後 channel が Disconnected になり、
/// キーストロークは `let _ = try_send` で握り潰されて **NDJSON 全損・無通知**、probe/nudge の
/// record コマンドは Err を返してカードが閉じなくなっていた。本 enum と temp フォールバックで
/// 「静かな全損」を撲滅し、書込先の状態を UI に明示する。
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum LogStatus {
    /// 意図したパス (GSE_DATASET or ~/Documents/GSE-sessions) に正常に書ける。
    Ok,
    /// primary が書けず temp へフォールバックした。データは保全されるが配置が想定外。
    Fallback {
        intended: PathBuf,
        actual: PathBuf,
        error: String,
    },
    /// primary も temp も書けず、書き込みを破棄 (sink) している。データは保全されない。
    Disabled { error: String },
}

/// **いま書いている先**。G1 のローテート (`LogEntry::Rotate`) で変わりうるため、
/// 起動時の値をコピーして持ち回るのではなく共有ハンドル越しに読む。
///
/// ⚠️ ★ `status` も一緒に持つのが要点である。ローテート先が書けずに temp へ落ちたとき、
/// 起動時の `LogStatus::Ok` を UI が持ち続けると **fail-loud バナーが出ないまま
/// 想定外の場所に書き続ける**。#1 (静かな全損) の再発になるため、
/// **path と status を 1 つの構造体で同時に更新する**。
#[derive(Debug, Clone)]
pub struct LogTarget {
    pub path: PathBuf,
    pub status: LogStatus,
}

/// `LogTarget` の共有ハンドル。logger スレッドが書き、UI コマンドと `quit_app` が読む。
pub type SharedLogTarget = Arc<Mutex<LogTarget>>;

/// 書込先を確定する。`primary` → temp フォールバック → `io::sink()` 縮退の順に試す。
/// 戻り値の `Box<dyn Write + Send>` を BufWriter で包めば consumer ループの `writeln!` 群は無改変
/// (sink は書き込みを捨てる)。**いずれの場合も consumer スレッドは生かし続ける**ことで channel が
/// Disconnected にならず、`record_*` コマンドのカードが閉じなくなる #1 を構造的に防ぐ。
fn open_log_target(primary: &Path) -> (Box<dyn Write + Send>, PathBuf, LogStatus) {
    match create_file_at(primary) {
        Ok(f) => (Box::new(f), primary.to_path_buf(), LogStatus::Ok),
        Err(e_primary) => {
            let fallback = temp_fallback_path(primary);
            tracing::error!(
                "SessionLogger: failed to create {:?}: {} — falling back to {:?}",
                primary,
                e_primary,
                fallback
            );
            match create_file_at(&fallback) {
                Ok(f) => (
                    Box::new(f),
                    fallback.clone(),
                    LogStatus::Fallback {
                        intended: primary.to_path_buf(),
                        actual: fallback,
                        error: e_primary.to_string(),
                    },
                ),
                Err(e_fallback) => {
                    tracing::error!(
                        "SessionLogger: fallback {:?} also failed: {} — logging DISABLED (data will be lost)",
                        fallback,
                        e_fallback
                    );
                    (
                        Box::new(io::sink()),
                        primary.to_path_buf(),
                        LogStatus::Disabled {
                            error: format!("primary: {}; fallback: {}", e_primary, e_fallback),
                        },
                    )
                }
            }
        }
    }
}

/// 親ディレクトリを作成してから NDJSON ファイルを作成する。
/// NDJSON はキーストローク動態 (VK コード列) を含むため、unix では **ファイルを所有者のみ** に
/// 制限する (file=0600)。`$TMPDIR` が共有ディレクトリに上書きされた環境でも他ユーザーが打鍵ログの
/// **内容**を読めない (data-privacy ルール 2)。
/// NOTE: 親ディレクトリの権限は変更しない。`$GSE_DATASET/raw/<id>` 等のユーザー指定・共有前提の
/// 既存ディレクトリを 0700 へ締めると研究者/別プロセスのアクセスを壊す副作用があるため
/// (cross-review 指摘)。内容保護は file=0600 で足り、ディレクトリ一覧 (ファイル名) は機微でない。
fn create_file_at(path: &Path) -> io::Result<File> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        std::fs::OpenOptions::new()
            .write(true)
            .create(true)
            .truncate(true)
            .mode(0o600)
            .open(path)
    }
    #[cfg(not(unix))]
    {
        // Windows (プライマリターゲット): NTFS の既定 ACL ではユーザープロファイル配下
        // (Documents / %TEMP%) は他ユーザーから読めないため、ここでは追加制限をしない。
        // より厳密な ACL 設定 (icacls 相当) が必要になれば別タスクで対応する (data-privacy)。
        File::create(path)
    }
}

/// temp フォールバック先 (`$TMPDIR/GSE-sessions/<pid>_<filename>`)。primary のファイル名に
/// プロセス ID を前置し、同秒起動 (ファイル名は秒粒度) や残骸との衝突で既存フォールバックを
/// truncate 上書きするのを防ぐ (cross-review 指摘)。
fn temp_fallback_path(primary: &Path) -> PathBuf {
    let name = primary
        .file_name()
        .map(|n| n.to_string_lossy().to_string())
        .unwrap_or_else(|| "gse_session.ndjson".to_string());
    let unique = format!("{}_{}", std::process::id(), name);
    std::env::temp_dir().join("GSE-sessions").join(unique)
}

/// `meta`(session_start) 行を書く。★ **新しいファイルを開くたびに必ず呼ぶ**
/// (起動時 / `LogEntry::Rotate` 時)。
///
/// - `hmm_version` は `engine.rs` の定数。`gse-replay` がゴールデンスナップショットと
///   突き合わせる際に同一バージョンであることを検証する。
/// - `g1_mode` は G1 実施時のみ `Some(..)`。⚠️ ★ **`&str` ではなく `G1Source` を受ける。**
///   手書き JSON なのでエスケープが無く、将来ここへ参加者 ID のような外部由来の文字列が
///   渡ると **NDJSON の 1 行が黙って壊れ**、解析側 (`validate_blocks.py` / `anonymize`) が
///   誤読する。★ 値域を型で閉じてその経路を作らせない (security review MEDIUM)。
///   ⚠️ ★ **`None` のときは `g1_mode` キーを出さない** (`skip_serializing_if` 相当を手書きで担保)。
///   ★ キーの順序を含めて既存キーの並びを変えないこと。
/// - `app_version` / `capabilities` は **2026-08-19 に ADR-013 D1 で追加**した。
///   ⚠️★★ **上の「従来と 1 バイトも変わらない」という記述はこの追加で成り立たなくなったので消した。**
///   ★ 代わりに確かめた事実 (2026-08-19 実測):
///   ゴールデン (`tests/snapshots/*.json`) は `FeatSnapshot` の配列で **`meta` を含まない**、
///   読み手 (`anonymize.rs:111` / `validate_blocks.py:409`) は **JSON パース**である。
///   → ★ additive なフィールド追加は**どちらも壊さない**。
/// セッション開始時に **1 回だけ** `meta` へ刻むキーボードレイアウト識別子。
///
/// ## ⚠️★★★ なぜ `OnceLock` で外から入れるのか
///
/// ★ 値の取得は **OS API**（Win: `GetKeyboardLayoutNameW` / mac: TIS）なので
/// `input/` の中でしか呼べない（`architecture-rules` ルール 2）。
/// ⚠️ `logger` から `input` を直接呼ぶと依存が増えるので、
/// ★ **`lib.rs` が起動時に解決して入れる**形にする。
///
/// ⚠️ **未設定なら `meta` にフィールドを出さない** —— ★ 「取れなかった」と
/// 「取っていない」を無理に 0 値で埋めない（ADR-013 D1 の趣旨）。
static KEYBOARD_LAYOUT_ID: std::sync::OnceLock<String> = std::sync::OnceLock::new();

/// キーボードレイアウト識別子を登録する（★ 起動時に 1 回だけ）。
///
/// ⚠️ **識別子のみ**。★ 文字変換の結果を入れてはならない（`data-privacy` ルール 7）。
pub fn set_keyboard_layout_id(id: String) {
    let _ = KEYBOARD_LAYOUT_ID.set(id);
}

/// `meta` に足すレイアウト断片（★ 未設定なら空文字列 = 従来と 1 バイトも変わらない）。
fn keyboard_layout_fragment() -> String {
    match KEYBOARD_LAYOUT_ID.get() {
        // ⚠️ 識別子は英数字とハイフン/ドットしか来ない想定だが、★ 念のため
        //   ★ **英数字と `.` `-` `_` 以外を落とす** (⚠️ JSON を壊す文字を通さない)。
        Some(id) => {
            let safe: String = id
                .chars()
                .filter(|c| c.is_ascii_alphanumeric() || matches!(c, '.' | '-' | '_'))
                .collect();
            format!(r#","keyboard_layout":"{}""#, safe)
        }
        None => String::new(),
    }
}

/// `meta` に足す O1 モードの断片 (★ 非 O1 なら空文字列 = 従来と 1 バイトも変わらない)。
///
/// ⚠️★★★ **`g1_mode` の直後・`app_version` の前**に置く (★ キー順を固定する)。
/// ★ 値域は `O1Source` で型に閉じているので、⚠️ 外部由来の文字列が JSON を壊す経路は無い
/// (`g1_mode` が security review MEDIUM で採った作法と同じ)。
fn o1_mode_fragment() -> String {
    match crate::o1::mode() {
        Some(src) => format!(r#","o1_mode":"{}""#, src.as_str()),
        None => String::new(),
    }
}

fn write_meta_start(
    writer: &mut impl Write,
    session_start: u64,
    g1_mode: Option<crate::g1::G1Source>,
) {
    // ⚠️★★★ **`app_version` と `capabilities` は必ず末尾に足す** (ADR-013 D1)。
    //   既存キーの順序を動かすと、`g1_mode` を足したときに担保した
    //   「G1 でないときの出力は従来と 1 バイトも変わらない」という性質のうち、
    //   ★ **キー順に依存している読み手** (目視 diff / 過去ログとの突き合わせ) が壊れる。
    // ★ なお `anonymize.rs:111` も `validate_blocks.py:409` も **JSON パース**なので、
    //   additive なフィールド追加そのものは安全である (2026-08-19 実測)。
    let app_version = crate::capabilities::app_version();
    let capabilities = crate::capabilities::capabilities_json();
    // ★ O1: セッション開始時に 1 回だけ。⚠️ 未設定なら空文字列で、従来の出力と同一になる。
    let layout = keyboard_layout_fragment();
    // ★ O1: 実施時にしか出ない (⚠️ 通常運用 / G1 の出力は 1 バイトも変わらない・R-1)。
    let o1 = o1_mode_fragment();
    match g1_mode.map(|s| s.as_str()) {
        None => {
            let _ = writeln!(
                writer,
                r#"{{"type":"meta","session_start":{},"hmm_version":"{}"{},"app_version":"{}","capabilities":{}{}}}"#,
                session_start,
                crate::analysis::engine::HMM_VERSION,
                o1,
                app_version,
                capabilities,
                layout,
            );
        }
        Some(source) => {
            let _ = writeln!(
                writer,
                r#"{{"type":"meta","session_start":{},"hmm_version":"{}","g1_mode":"{}"{},"app_version":"{}","capabilities":{}{}}}"#,
                session_start,
                crate::analysis::engine::HMM_VERSION,
                source,
                o1,
                app_version,
                capabilities,
                layout,
            );
        }
    }
}

/// `meta`(session_end) 行を書く。ブロック終了 / ローテート / 終了の 3 経路で使う。
fn write_meta_end(writer: &mut impl Write, session_end: u64) {
    let _ = writeln!(writer, r#"{{"type":"meta","session_end":{}}}"#, session_end);
}

/// NDJSON形式でセッションデータを書き込むロガー。
/// バックグラウンドスレッドでファイルIOを行うため、
/// 送信側 (分析スレッド) は非ブロッキングで送信できる。
pub struct SessionLogger {
    /// 起動時に確定した書込先 (診断用の不変値)。
    /// ⚠️ ★ **ローテート後の「いま書いている先」ではない**。それは `target` を見ること。
    pub log_path: PathBuf,
    /// いま書いている先 + その状態 (ローテートで更新される共有ハンドル)。
    pub target: SharedLogTarget,
    _handle: thread::JoinHandle<()>,
}

/// `LogChannel` がまだ `start()` されていないことを表す `LogStatus::Disabled` の理由文字列。
///
/// ⚠️ ★ 「まだ開いていない」を **`Ok` ではなく `Disabled`** で表すのは意図的である。
/// 万一 `start()` が呼ばれないまま UI が状態を読んだら、★ **偽の緑ではなく警告バナー**が出る。
/// (`Dashboard.tsx` は起動時に 1 回だけ読み、以後ポーリングしない = 誤った値は貼り付いたままになる。)
pub const LOGGER_NOT_STARTED: &str = "session logger has not started yet";

/// ★ **NDJSON をまだ作らない**段階のロガーハンドル (channel + 共有ハンドルだけ)。
///
/// ## なぜ 2 段階に分かれているか (2026-08-06・follow-up F-3)
///
/// ⚠️ ★ `tauri-plugin-single-instance` に止められた 2 個目のプロセスは、
/// **止められる前に NDJSON を作ってから死ぬ**。実測で **0 行のファイル**ができた
/// (`.steering/20260805-g1-app-mode-and-log-rotation/decisions.md` R-8 結果 4)。
/// `gse-submit` は最新 1 本を選ぶため、★ 被験者が「提出する」を押すと空の `.age` が出る。
///
/// ★ 原因は **順序**である (一次資料: `tauri` 2.10.2 `src/app.rs`):
/// プラグインの `exit(0)` は `Builder::build()` 末尾の `initialize_plugins` で走り、
/// **ユーザーの `.setup()` クロージャはその後の `App::run()` の中**で呼ばれる。
/// → ★ `new()` を `run()` の先頭で、`start()` を `.setup()` の中で呼べば、
/// **2 個目のプロセスはファイルを作る前に死ぬ**。
///
/// ⚠️ ★ 提出側の緩和 (`packaging::has_any_data_row`) は残す。**置き換えではなく二重化**である
/// (起動直後のクラッシュ・ディスク不足など、二重起動以外の原因でも空ファイルは出るため)。
///
/// ⚠️ ★ **`start()` が返す `SessionLogger` は呼び出し側で即 drop してよい**（`lib.rs` はそうしている）。
/// `JoinHandle` は drop しても join も停止もしないので、consumer スレッドは走り続ける。
/// ★ **将来 `SessionLogger` に `Drop` を実装する場合はこの前提が壊れる**ので、
/// そのときは `lib.rs` の `.setup()` 側で保持するように直すこと（cross-review 2026-08-06）。
///
/// `tx` / `shutdown_rx` / `target` は `start()` の前から配れる。スレッドは
/// `start()` まで走らないので、それまでに送られた行は bounded(512) に溜まり、
/// `start()` 後に順に書かれる (★ 取りこぼさない)。
pub struct LogChannel {
    /// ログ行の送信端。`start()` の前から Clone して配ってよい。
    pub tx: Sender<LogEntry>,
    rx: Receiver<LogEntry>,
    shutdown_tx: Sender<()>,
    /// `LogEntry::End` 処理完了の通知端 (`quit_app` が待つ)。
    pub shutdown_rx: Receiver<()>,
    block_end_tx: Sender<()>,
    /// ★ `LogEntry::BlockEnd` を **書いて flush し終えた** ことの通知端。
    ///
    /// ⚠️★ **なぜ要るか (G1 自動提出)**: ブロック終了の直後に収束器 (`gse-submit --reconcile`)
    /// を起こすが、収束器は「`session_end` を持つファイル」しか触らない。`BlockEnd` は
    /// channel 越しの非同期処理なので、★ **送った直後にはまだ `session_end` が書かれていない**。
    /// そのまま起こすと、そのブロックは毎回 1 周遅れて拾われることになる
    /// (収束型なので損失にはならないが、⚠️ **最後のブロックはプロセスが生き続ける限り
    /// 送られない** — `lib.rs` は `overlay` 窓があるため × で閉じても終了しない)。
    ///
    /// ★ 固定 sleep で待たないのは、`ANALYSIS_IDLE` を入れたときと同じ理由である:
    /// **待つべき時間ではなく、待つべき状態を観測する**。
    pub block_end_rx: Receiver<()>,
    /// いま書いている先 + 状態。`start()` が **同じ Arc を上書き**する
    /// (★ `.manage()` に渡した後から差し替えられるようにするため)。
    pub target: SharedLogTarget,
}

impl Default for LogChannel {
    fn default() -> Self {
        Self::new()
    }
}

impl LogChannel {
    /// channel と共有ハンドルだけを用意する。★ **ファイルは作らない**。
    pub fn new() -> Self {
        let (tx, rx) = bounded::<LogEntry>(512);
        let (shutdown_tx, shutdown_rx) = bounded::<()>(1);
        // ★ 容量 1 + `try_send` にする。⚠️ 誰も待っていないブロック終了で
        //   logger スレッドを**絶対に止めない**ため (ログの遅延は打鍵の取りこぼしになる)。
        let (block_end_tx, block_end_rx) = bounded::<()>(1);
        let target: SharedLogTarget = Arc::new(Mutex::new(LogTarget {
            path: PathBuf::new(),
            status: LogStatus::Disabled {
                error: LOGGER_NOT_STARTED.to_string(),
            },
        }));
        Self {
            tx,
            rx,
            shutdown_tx,
            shutdown_rx,
            block_end_tx,
            block_end_rx,
            target,
        }
    }

    /// 書込先を開き、consumer スレッドを起こす。★ **ここで初めて NDJSON ができる**。
    ///
    /// 書込先は **spawn 前に同期的に確定** する (`open_log_target`)。これにより:
    /// - この時点で書込可否を検証できる (GSE_DATASET 妥当性・macOS Documents 権限) → `LogStatus` を UI へ。
    /// - File::create 失敗でも consumer スレッドが死なず channel が Disconnected にならない (#1 解消)。
    ///
    /// `g1_mode` は G1 実施時のみ `Some(..)`。`meta` 行に刻んで事後検証できるようにする
    /// (⚠️ ★ マーカーが外れると黙って通常モードになるため・D-7)。
    pub fn start(
        self,
        log_path: PathBuf,
        g1_mode: Option<crate::g1::G1Source>,
    ) -> (SessionLogger, LogStatus) {
        let LogChannel {
            tx: _tx,
            rx,
            shutdown_tx,
            shutdown_rx: _shutdown_rx,
            block_end_tx,
            block_end_rx: _block_end_rx,
            target,
        } = self;
        SessionLogger::spawn(log_path, g1_mode, rx, shutdown_tx, block_end_tx, target)
    }
}

impl SessionLogger {
    /// ロガーを開始し、ログエントリ送信用の `Sender`・シャットダウン通知用の `Receiver`・
    /// 書込先の `LogStatus` を返す。`Sender` を Clone して複数スレッドから送信可能。
    /// `shutdown_rx` は `LogEntry::End` 処理完了後に値を受信する。
    ///
    /// ★ `LogChannel::new()` → `start()` を 1 呼び出しにまとめた薄いラッパである
    /// (テストと、2 段階に分ける必要のない呼び出し側のため)。
    /// ⚠️ **`run()` はこれを使わない** — 2 個目のプロセスがファイルを作ってしまうため
    /// (`LogChannel` のコメント参照)。
    pub fn start(
        log_path: PathBuf,
        g1_mode: Option<crate::g1::G1Source>,
    ) -> (Self, Sender<LogEntry>, Receiver<()>, LogStatus) {
        let channel = LogChannel::new();
        let tx = channel.tx.clone();
        let shutdown_rx = channel.shutdown_rx.clone();
        let (logger, status) = channel.start(log_path, g1_mode);
        (logger, tx, shutdown_rx, status)
    }

    fn spawn(
        log_path: PathBuf,
        g1_mode: Option<crate::g1::G1Source>,
        rx: Receiver<LogEntry>,
        shutdown_tx: Sender<()>,
        block_end_tx: Sender<()>,
        target: SharedLogTarget,
    ) -> (Self, LogStatus) {
        // 書込先を spawn 前に同期確定 (primary → temp → sink)。actual_path を log_path に採用する。
        let (boxed, actual_path, status) = open_log_target(&log_path);
        let resolved_path = actual_path.clone();
        // ★ 共有ハンドルを**上書き**する (新しい Arc を作らない)。`.manage()` 済みの
        //   `LogStatusState` が同じ Arc を握っているため。poison しても保守的に上書きする。
        {
            let mut t = target.lock().unwrap_or_else(|p| p.into_inner());
            *t = LogTarget {
                path: actual_path.clone(),
                status: status.clone(),
            };
        }
        let target_for_thread = target.clone();

        let handle = thread::spawn(move || {
            let mut writer = BufWriter::new(boxed);

            // セッション開始メタデータ
            let session_start = now_ms();
            write_meta_start(&mut writer, session_start, g1_mode);

            // ★ ブロックを `session_end` で閉じ済みか。`BlockEnd` → `Rotate` → `End` の
            // どの順で来ても **`session_end` を 1 ファイルにつき 1 行だけ**にするための状態。
            let mut block_closed = false;

            // ⚠️★★★ **記録の一時停止状態**（O1 / ADR-014 D7-ii）。
            // ★ **ストリーム内の `RecordingPause` 行だけ**で進める（上のゲートの doc を参照）。
            let mut recording_paused = false;

            tracing::info!("SessionLogger: writing to {:?}", actual_path);

            let flush_interval = Duration::from_secs(5);
            let mut last_flush = Instant::now();
            let mut dirty = false;

            loop {
                let timeout = flush_interval.saturating_sub(last_flush.elapsed());
                match rx.recv_timeout(timeout) {
                    Ok(entry) => {
                        // ⚠️★★★ **一時停止中はここで落とす** (O1 / ADR-014 D7-ii)。
                        //
                        // ★ 被験者への約束は逐語「**すぐ止める**」であり、その実体は
                        //   **ファイルに 1 バイトも書かないこと**である。→ ★ **書き出しの唯一の入口**で
                        //   落とす（⚠️ 19 個の match 腕に条件を散らさない）。
                        // ★ 通すのは `recording_pause`（＝ 再開を記録できなくなる）と
                        //   `meta`（＝ ファイルの整合性）だけ。判断は `recording` の純関数が持つ。
                        // ⚠️ 制御エントリ (`BlockEnd` / `Rotate` / `End`) は `line_type()` が `None` を返し、
                        //   ★ **常に通る**（止めている間もアプリは正しく終了できなければならない）。
                        //
                        // ## ⚠️★★★ なぜグローバル Atomic を読まないのか（★ テストで再現して直した）
                        //
                        // ⚠️ `recording::is_paused()` をここで読むと、**キューに積まれた順序**と
                        //   **フラグが切り替わる時刻**がずれる —— ★ 停止中に積まれた行が、
                        //   ロガーが取り出す前に被験者が再開すると **書かれてしまう**
                        //   (2026-08-23 に `paused_logger_writes_no_data_rows` で実際に再現した)。
                        // → ★ **ストリーム内の `RecordingPause` 行で状態を進める。**
                        //   ⚠️ これなら「積まれた順」と「止まっていた区間」が定義上ずれない。
                        //   ★ グローバル Atomic は UI の稼働中インジケータ専用である。
                        if recording_paused {
                            if let Some(t) = entry.line_type() {
                                if !crate::recording::is_writable_while_paused(t) {
                                    continue;
                                }
                            }
                        }
                        match entry {
                            LogEntry::Key {
                                vk_code,
                                timestamp,
                                is_press,
                            } => {
                                // ⚠️★★★ **書き出し境界で VK をカテゴリへ量子化する** (ADR-014 判断 6)。
                                // `consent.md` の記録項目表は「キーの**種類**」と約束しており、
                                // 生 VK (キー個体) をローカル NDJSON に残すのは文言とずれていた。
                                // 匿名化 (`analysis::anonymize`) は従来 transfer 境界 (`gse-package`)
                                // でのみ効いていたが、ここへ前倒しする。
                                //
                                // **失われないもの**: `is_backspace` / `is_text_producing` は
                                // 14 カテゴリから完全復元できる (`replay.rs` の代表 VK 逆写像)。
                                // 推論は in-memory 経路 (`InputEvent.is_backspace`) なので無影響。
                                let category = KeyCategory::from_vk(vk_code).as_str();
                                let _ = writeln!(
                                    writer,
                                    r#"{{"type":"key","t":{},"category":"{}","press":{}}}"#,
                                    timestamp, category, is_press,
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
                                keys,
                                bs_keys,
                            } => {
                                // ★ field init shorthand なので、名前が一致しない限りコンパイルが通らない
                                // (13 個の連続する f64 の取り違えを型システムに弾かせる)。
                                let _ = writeln!(
                                    writer,
                                    "{}",
                                    format_feat_line(&FeatLine {
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
                                        keys,
                                        bs_keys,
                                    }),
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
                            LogEntry::HookHealth {
                                timestamp,
                                alive,
                                starved_ms,
                                rehook,
                                dropped,
                                dropped_delta,
                            } => {
                                // ⚠️★ `dropped` (累積) は**そのまま残す** (非破壊)。`dropped_delta` を
                                //   **末尾に併記**する (ADR-013 D4)。改名は breaking なので採らない。
                                let _ = writeln!(
                                    writer,
                                    r#"{{"type":"hook_health","t":{},"alive":{},"starved_ms":{},"rehook":{},"dropped":{},"dropped_delta":{}}}"#,
                                    timestamp, alive, starved_ms, rehook, dropped, dropped_delta,
                                );
                                dirty = true;
                            }
                            LogEntry::StarveWindow {
                                timestamp,
                                win_ms,
                                n_lt30,
                                sum_lt30_ms,
                            } => {
                                let _ = writeln!(
                                    writer,
                                    r#"{{"type":"starve_window","t":{},"win_ms":{},"n_lt30":{},"sum_lt30_ms":{}}}"#,
                                    timestamp, win_ms, n_lt30, sum_lt30_ms,
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
                                intervention_enabled,
                                condition,
                                label_pool,
                                head_id,
                            } => {
                                let _ = writeln!(
                                    writer,
                                    "{}",
                                    format_session_meta_line(
                                        timestamp,
                                        track,
                                        task_kind,
                                        intervention_enabled,
                                        condition,
                                        label_pool,
                                        head_id
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
                                elapsed_ms,
                                changes,
                            } => {
                                let _ = writeln!(
                                    writer,
                                    "{}",
                                    format_vignette_response_line(
                                        timestamp,
                                        &vignette_id,
                                        expected_quadrant,
                                        q1_friction,
                                        q2_progress,
                                        elapsed_ms,
                                        changes
                                    ),
                                );
                                dirty = true;
                            }
                            LogEntry::RecordingPause { timestamp, paused } => {
                                // ★ **書いてから状態を進める。** ⚠️ 先に進めると「止める」の行自身が
                                //   ゲートに落ちて、**止めた事実が記録されない**。
                                recording_paused = paused;
                                // ⚠️★★★ **遷移の時刻と向きだけ**。理由も回数も書かない
                                //   (`LogEntry::RecordingPause` の doc)。
                                let _ = writeln!(
                                    writer,
                                    r#"{{"type":"recording_pause","t":{},"paused":{}}}"#,
                                    timestamp, paused,
                                );
                                // ★ **すぐ flush する。** ⚠️ 5 秒バッファのままだと、
                                //   「止めた」直後にアプリが落ちたときに**止めた事実が消え**、
                                //   その先の空白が「信号が無かった」と読まれる。
                                let _ = writer.flush();
                                last_flush = Instant::now();
                                dirty = false;
                            }
                            LogEntry::FocusTransition { timestamp } => {
                                // ⚠️★★★ **時刻しか書けない形**にしてある (variant にそれしか無い)。
                                let _ = writeln!(
                                    writer,
                                    r#"{{"type":"focus_transition","t":{}}}"#,
                                    timestamp,
                                );
                                dirty = true;
                            }
                            LogEntry::PointerBin {
                                timestamp,
                                moved,
                                buttons,
                                wheel,
                            } => {
                                // ★ 量子化スカラだけ。⚠️ 座標・向き・速度は型として存在しない。
                                let _ = writeln!(
                                    writer,
                                    r#"{{"type":"pointer_bin","t":{},"moved":{},"buttons":{},"wheel":{}}}"#,
                                    timestamp, moved, buttons, wheel,
                                );
                                dirty = true;
                            }
                            LogEntry::SecureInput { timestamp, on } => {
                                let _ = writeln!(
                                    writer,
                                    r#"{{"type":"secure_input","t":{},"on":{}}}"#,
                                    timestamp, on,
                                );
                                dirty = true;
                            }
                            LogEntry::BlockEnd => {
                                // ★ 閉じるだけ。次のファイルは開かない (11 本目の空ファイル対策)。
                                if !block_closed {
                                    write_meta_end(&mut writer, now_ms());
                                    block_closed = true;
                                }
                                let _ = writer.flush();
                                last_flush = Instant::now();
                                dirty = false;
                                // ★ **flush の後**に知らせる。⚠️ 先に知らせると、収束器が
                                //   `session_end` の無いファイルを見て「まだ閉じていない」と
                                //   判断してしまう (待った意味が消える)。
                                //   `try_send` なので誰も待っていなくてもここで止まらない。
                                let _ = block_end_tx.try_send(());
                            }
                            LogEntry::Rotate { new_path } => {
                                // ⚠️★ **一意化を先に行う。** 呼び出し側 (UI スレッド) の exists 判定と
                                // 実作成の間には窓があり、ファイル名は秒粒度なので同じパスが来うる。
                                // ★ ここで先に別名へ振ることで、下の「同一パス」判定に落ちる
                                // = **2 つの論理ブロックが 1 ファイルに黙って混ざる**経路を消す
                                // (cross-review: Codex 指摘)。logger スレッドは単一なので窓が閉じる。
                                let new_path = unique_path_from(new_path);

                                // ⚠️★ **ここに「同一パスなら skip」のガードは置かない。**
                                // 上の一意化が先に走るので、書きかけのファイルは必ず存在する
                                // → `unique_path_from` が別名を返す → 同一パスには**なりえない**。
                                // ★ 実際、ガードを書いて**わざと壊しても赤にならなかった**（到達不能）。
                                // 発火しない検査を残すと「守られているつもり」を作るので置かない。
                                // 唯一同一パスになりうるのは現ファイルがディスク上に無いとき
                                // （外部削除 / LogStatus::Disabled の sink）で、その場合は開き直すほうが正しい。
                                if !block_closed {
                                    write_meta_end(&mut writer, now_ms());
                                }
                                let _ = writer.flush();

                                // ★ 旧ファイルはここで drop される (writer の差し替えで閉じる)。
                                let (boxed, actual, new_status) = open_log_target(&new_path);
                                writer = BufWriter::new(boxed);

                                // ⚠️ ★ **新ファイルの実時刻**で meta を書く。
                                // anonymize.rs の find_session_start がこの行を `t` の基点にするため、
                                // 前ファイルの値を引き継ぐと匿名化後の時刻が全部ずれる。
                                write_meta_start(&mut writer, now_ms(), g1_mode);
                                let _ = writer.flush();

                                if new_status != LogStatus::Ok {
                                    // ⚠️ ★ ローテート先が書けなかった。UI のバナーへ伝える必要がある
                                    // (起動時 Ok のまま黙って temp に書き続けるのが #1 の再発)。
                                    tracing::error!(
                                        "SessionLogger: rotate to {:?} degraded: {:?}",
                                        new_path,
                                        new_status
                                    );
                                } else {
                                    tracing::info!("SessionLogger: rotated to {:?}", actual);
                                }
                                // ⚠️ poison でも黙って諦めない。他の箇所と同じく into_inner で
                                // データを取り出して更新する (ここだけ握り潰すと、ローテート先が
                                // temp に落ちたことが UI に届かない・cross-review: Codex 指摘)。
                                {
                                    let mut t =
                                        target_for_thread.lock().unwrap_or_else(|e| e.into_inner());
                                    t.path = actual;
                                    t.status = new_status;
                                }

                                block_closed = false;
                                last_flush = Instant::now();
                                dirty = false;
                            }
                            LogEntry::End => {
                                // ★ 直前に BlockEnd が来ていたら二重に書かない。
                                if !block_closed {
                                    write_meta_end(&mut writer, now_ms());
                                }
                                break;
                            }
                        }
                    }
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
            // 実際に書いている場所を log_path に採用する (fallback 時は temp パス)。
            log_path: resolved_path,
            target,
            _handle: handle,
        };

        (logger, status)
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
    let (dir, participant_id) = session_log_dir();
    tracing::info!(
        resolved_log_dir = %dir.display(),
        participant_id = %participant_id,
        source = if std::env::var("GSE_DATASET").is_ok() { "GSE_DATASET env" } else { "fallback (Documents/GSE-sessions)" },
        "session log path resolved"
    );

    // ⚠️★★★ 同意文書 §5「クラウド同期フォルダには置きません」の**実装上の担保**（R-10）。
    //   ★ 保存先が確定したこの 1 か所で見る（⚠️ 起動のたびに 1 回だけ）。
    warn_if_cloud_synced(&dir);

    let ts = chrono_like_filename();
    dir.join(session_file_name(crate::o1::is_o1(), &ts))
}

/// セッション NDJSON のファイル名 (純関数)。
///
/// ## ⚠️★★★ O1 だけ接頭辞が変わる
///
/// ★ `reconcile` は「閉じ終わった NDJSON」を**ディスクの状態だけ**から拾う収束器で、
/// G1 のときは `meta` 行の `g1_mode` を根拠に「これは G1 の記録である」と判定している
/// (⚠️ 共有フォルダに Phase1 の較正セッションが同居するため・code-review HIGH)。
/// → ★ **O1 にも同じ強さの根拠が要る。**
///
/// ⚠️ 本来は `g1_mode` と同じく `meta` 行に `o1_mode` を刻むほうが強い (事後検証ができる) が、
/// それは `schema_dto.rs` → `schema/current.json` の変更を伴い、**gse-dataset の parity 更新**が要る。
/// ★ 本タスクは「schema を 1 バイトも変えない」制約下にあるので、**ファイル名で表す**。
/// (→ 研究者へ返す論点として `.steering/00000000-o1-collection-enablement/decisions.md` に記録。)
///
/// ★ **`gse_` 接頭辞は保つ。** ⚠️ 外すと `redaction::is_redactable_session_file` の
/// フィルタから外れ、**被験者の区間指定削除が O1 のファイルに効かなくなる** (削除保証の破れ)。
fn session_file_name(o1_mode: bool, ts: &str) -> String {
    if o1_mode {
        format!("{}{}.ndjson", crate::o1::SESSION_FILE_PREFIX, ts)
    } else {
        format!("gse_{}.ndjson", ts)
    }
}

/// セッションログを置くディレクトリと、決定に使った参加者 ID を返す。
///
/// ⚠️ ★ **ここでは `tracing` に何も出さない**。この関数は `applog` から
/// **subscriber を設置する前**にも呼ばれるため、ここで `info!` しても
/// どこにも出ずに消える (それが「出ている」と誤解される)。
/// 可観測性のためのログは呼び出し側 (`default_log_path`) が持つ。
pub fn session_log_dir() -> (PathBuf, String) {
    let participant_id = resolve_participant_id();
    let dir = log_dir_for(std::env::var("GSE_DATASET").ok(), &participant_id);
    (dir, participant_id)
}

/// 保存先ディレクトリを決める**唯一の式**。★ env を読まないので並列テストで安全。
///
/// ⚠️ ★ `session_log_dir()` (NDJSON) と `app_log_path()` (診断ログ) の**両方がここを通る**。
/// 2 つの場所に同じ分岐を書くと、片方だけ直して静かにフォルダが割れる。
fn log_dir_for(dataset: Option<String>, participant_id: &str) -> PathBuf {
    match dataset {
        Some(d) => PathBuf::from(d).join("raw").join(participant_id),
        None => fallback_log_dir(),
    }
}

/// 診断ログのファイル名。
const APP_LOG_FILE_NAME: &str = "gse-app.log";

/// アプリ本体の診断ログ (`tracing`) を書き出すファイル。
///
/// ★ **セッション NDJSON と同じフォルダ**に置く。理由:
/// 1. 研究者が NDJSON を見に行く場所と同じなので、探す場所が増えない。
///    ⚠️ ★ **被験者向けの `README_先に読む.txt` はこのフォルダに触れていない**
///    (2026-08-08 に `dist-readme-macos.txt` を grep して確認)。
///    → 研究者がログを取り寄せるときは**場所を伝える必要がある**。
/// 2. `quit_app` (アプリ内の終了ボタン) がこのフォルダをファイルマネージャで開く
///    (`lib.rs`)。⚠️ ★ ただし **× で閉じた場合はこの経路を通らない**
///    (`windows-verification.md §4-1`)。
/// 3. ⚠️ 収束器 (`reconcile.rs:189`) は `*.ndjson` しか拾わないので、
///    `.log` を同居させても**提出物には混ざらない** (実装で確認済み)。
///
/// # ⚠️ ★ なぜ `session_log_dir()` をそのまま呼ばないのか
///
/// この関数は **`tracing` の購読者を設置する前**に呼ばれる。`resolve_participant_id()` には
/// 「新しい ID を生成して `~/.gse/participant_id` に永続化し、それを `info!` で記録する」
/// という副作用があり、⚠️ ★ **ここで先に呼ぶとその 1 行がどこにも出ないまま消える**。
/// `GSE_DATASET` が無いとき (= 被験者の実機) は保存先が参加者 ID に依存しないので、
/// ★ **ID を解決しない**。副作用は後続の `default_log_path()` に任せる (そこは購読者の設置後)。
pub fn app_log_path() -> PathBuf {
    let dataset = std::env::var("GSE_DATASET").ok();
    let dir = match dataset {
        // ★ ID を解決しない (上記)。保存先が ID に依存しない経路なので、
        //   副作用 (生成 + 永続化 + その `info!`) を購読者の設置前に先取りしない。
        None => fallback_log_dir(),
        Some(d) => log_dir_for(Some(d), &resolve_participant_id()),
    };
    dir.join(APP_LOG_FILE_NAME)
}

/// 既存ファイルを踏まない次のセッションパスを返す (G1 のローテート用)。
///
/// ⚠️ ★ **`chrono_like_filename()` は秒粒度**である。同じ秒に 2 回ローテートすると
/// `create_file_at` の `truncate(true)` が **前のブロックを丸ごと消す**。
/// ブロック間隔は 5 分なので通常は起きないが、「開始する」を連打すれば起こせる。
/// ★ 静かな全損 (気づけない失敗) になるので、運用の注意ではなく**構造で防ぐ**。
///
/// 衝突時は `gse_YYYYMMDD_HHMMSS_2.ndjson`, `_3` … と後置する。
pub fn next_session_path() -> PathBuf {
    unique_path_from(default_log_path())
}

/// `next_session_path` の本体。★ **base を引数に取る**ので env に依存せず単体テストできる
/// (`default_log_path()` は `GSE_DATASET` / `HOME` を読むため、そのままだと
/// 並列テストで env を触ることになり検証が不安定になる)。
fn unique_path_from(base: PathBuf) -> PathBuf {
    if !base.exists() {
        return base;
    }
    let dir = base.parent().map(|p| p.to_path_buf()).unwrap_or_default();
    let stem = base
        .file_stem()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or_else(|| "gse_session".to_string());
    for n in 2..1000u32 {
        let candidate = dir.join(format!("{}_{}.ndjson", stem, n));
        if !candidate.exists() {
            return candidate;
        }
    }
    // ★ 1000 本ぶつかるのは異常事態。pid を混ぜて必ず別名にする (黙って上書きしない)。
    dir.join(format!("{}_{}.ndjson", stem, std::process::id()))
}

/// フォールバック: ~/Documents/GSE-sessions/
fn fallback_log_dir() -> PathBuf {
    let base = std::env::var("USERPROFILE")
        .or_else(|_| std::env::var("HOME"))
        .unwrap_or_else(|_| ".".to_string());
    PathBuf::from(base).join("Documents").join("GSE-sessions")
}

/// ⚠️★★★ **クラウド同期フォルダの名前**（研究者判断 R-10・2026-08-26）。
///
/// ★ 同意文書 §5 は逐語で「⚠️ **クラウド同期フォルダ（OneDrive 等）には置きません**」と
/// 約束しているが、⚠️ **実装上の担保が 1 つも無かった**（security-checker MEDIUM-6）——
/// `fallback_log_dir()` は `Documents` を**文字列で組み立てるだけ**で、
/// ★ Windows の「ドキュメントを OneDrive にリダイレクト」やジャンクションを検査していない。
/// → ⚠️ **O1 は数日〜数週間ぶんの平文 NDJSON が残る**ので、同期対象になると影響が大きい。
/// ⚠️★★★ **実際のパスの形に合わせること。** ★ 2026-08-26 にテストで実際に踏んだ:
/// macOS の iCloud Drive は逐語 `Library/Mobile Documents/com~apple~CloudDocs` であり、
/// ⚠️ **`icloud` という語はパスに 1 度も現れない**。Google Drive も **空白入り**である。
/// → ★ 「それらしい語」ではなく **実在するディレクトリ名**を並べる。
const CLOUD_SYNC_MARKERS: [&str; 7] = [
    "onedrive",
    // ⚠️ macOS の iCloud Drive (★ `icloud` ではない)
    "com~apple~clouddocs",
    "mobile documents",
    "dropbox",
    // ⚠️ 空白入り (★ `googledrive` では当たらない)
    "google drive",
    "box sync",
    "creative cloud files",
];

/// ★ 解決済みの保存先が**クラウド同期の下にあるか**（純関数）。
///
/// ⚠️ ★ 判定は**小文字化した実パスの部分一致**である。★ 完全ではないが、
/// **無検査よりはるかに良く、誤検知しても失うのは警告 1 行だけ**である
/// （⚠️ 記録は止めない —— 止めると「気づいたら何も取れていない」を作る）。
pub fn looks_cloud_synced(path: &Path) -> Option<&'static str> {
    let lower = path.to_string_lossy().to_lowercase();
    CLOUD_SYNC_MARKERS.into_iter().find(|m| lower.contains(m))
}

/// ⚠️★★★ 保存先がクラウド同期の下なら **fail-loud で警告する**（起動時 1 回）。
///
/// ★ **止めない。** ⚠️ 記録を止めると「気づいたら何も取れていなかった」になり、
/// ★ ADR-012 D-4 が「被験者側の停止スイッチ」を却下したのと同じ失敗様式に落ちる。
/// → ★ **`tracing::error!` で残し、判断は人に返す**（`g1::other_instance_running` と同じ流儀）。
///
/// ⚠️ **実パスで見る**（`canonicalize`）—— ★ リダイレクトやジャンクションは
/// 組み立てた文字列には現れない。取れなければ元のパスで見る（★ 検査できないことを
/// 理由に「安全」と言わない）。
pub fn warn_if_cloud_synced(dir: &Path) {
    let resolved = std::fs::canonicalize(dir).unwrap_or_else(|_| dir.to_path_buf());
    if let Some(marker) = looks_cloud_synced(&resolved) {
        tracing::error!(
            resolved_log_dir = %resolved.display(),
            marker = marker,
            "SESSION LOGS ARE INSIDE A CLOUD-SYNCED FOLDER.              The consent form promises they are not (O1 keeps weeks of plaintext NDJSON).              Move the folder out of the sync root, or set GSE_DATASET to a local path."
        );
    }
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

    // --- 診断ログ (gse-app.log) の置き場 ---

    /// ★ 診断ログは **セッション NDJSON と同じフォルダ**に置く、が唯一の要件である。
    ///
    /// ⚠️★★★ **同意文書 §5「クラウド同期フォルダには置きません」の実装上の担保** (R-10)。
    ///
    /// ★ O1 は数日〜数週間ぶんの**平文 NDJSON** が残るので、同期対象になると影響が大きい。
    #[test]
    fn cloud_synced_paths_are_recognised() {
        use std::path::Path;
        // ⚠️ Windows の「ドキュメントを OneDrive にリダイレクト」の実際の形
        assert_eq!(
            looks_cloud_synced(Path::new(r"C:\Users\x\OneDrive\Documents\GSE-sessions")),
            Some("onedrive")
        );
        // ⚠️★★★ macOS の iCloud Drive —— ★ **逐語で `com~apple~CloudDocs`**。
        //   ⚠️ 「icloud」という語はパスに 1 度も現れない (★ ここを実際に踏んだ)。
        assert_eq!(
            looks_cloud_synced(Path::new(
                "/Users/x/Library/Mobile Documents/com~apple~CloudDocs/GSE-sessions"
            )),
            Some("com~apple~clouddocs")
        );
        // ⚠️ Google Drive は**空白入り** (★ `googledrive` では当たらない)
        assert_eq!(
            looks_cloud_synced(Path::new(r"G:\My Drive\GSE-sessions")),
            None,
            "★ マウントドライブは名前から判別できない (⚠️ 既知の限界)"
        );
        assert_eq!(
            looks_cloud_synced(Path::new("/Users/x/Google Drive/GSE-sessions")),
            Some("google drive")
        );
        assert_eq!(
            looks_cloud_synced(Path::new("/Users/x/Dropbox/GSE-sessions")),
            Some("dropbox")
        );
        // ★ 大文字小文字を問わない
        assert_eq!(
            looks_cloud_synced(Path::new(r"C:\Users\x\onedrive - contoso\GSE-sessions")),
            Some("onedrive")
        );
        // ★ ふつうのローカル保存先は通す (⚠️ 誤検知で毎回警告を出さない)
        assert_eq!(
            looks_cloud_synced(Path::new(r"C:\Users\x\Documents\GSE-sessions")),
            None
        );
        assert_eq!(
            looks_cloud_synced(Path::new("/Users/x/Documents/GSE-sessions")),
            None
        );
    }

    /// ⚠️★★★ O1 (R3-a): **ファイル名だけが O1 の目印である** (schema を変えないため)。
    ///
    /// ★ ここが崩れると 2 つ同時に壊れる:
    /// 1. `reconcile::closed_o1_sessions` が O1 の記録を拾えない (= **提出されない**)
    /// 2. `redaction::is_redactable_session_file` が外れる (= **被験者が消せない**)
    #[test]
    fn o1_sessions_are_named_apart_but_keep_the_gse_prefix() {
        let o1 = session_file_name(true, "00000000_101112");
        let normal = session_file_name(false, "00000000_101112");
        assert_eq!(o1, "gse_o1_00000000_101112.ndjson");
        assert_eq!(normal, "gse_00000000_101112.ndjson");
        assert_ne!(o1, normal);
        // ★ `reconcile` / `redaction` の共通フィルタを通り抜けること
        for name in [o1.as_str(), normal.as_str()] {
            assert!(name.starts_with("gse_"), "{name}");
            assert!(name.ends_with(".ndjson"), "{name}");
            assert!(!name.ends_with(".anon.ndjson"), "{name}");
        }
        // ★ O1 だけが O1 判定を通ること
        assert!(crate::o1::is_o1_session_file_name(&o1));
        assert!(!crate::o1::is_o1_session_file_name(&normal));
    }

    /// ⚠️ ★ `log_dir_for` を 2 か所から呼んでいるので、片方だけ直すと静かにフォルダが割れる。
    /// ここで両分岐を突き合わせておく (env を触らないので並列テストで安全)。
    #[test]
    fn app_log_and_session_log_share_a_directory() {
        // GSE_DATASET 無し (= 被験者の実機): 参加者 ID に依存しない
        assert_eq!(log_dir_for(None, "P007"), fallback_log_dir());
        assert_eq!(log_dir_for(None, "P999"), log_dir_for(None, "P007"));

        // GSE_DATASET 有り (= 開発機): <dataset>/raw/<PID>
        assert_eq!(
            log_dir_for(Some("/tmp/ds".to_string()), "P007"),
            PathBuf::from("/tmp/ds").join("raw").join("P007")
        );
    }

    /// ⚠️ ★ 提出物に混ざらないこと。収束器 (`reconcile.rs`) は `*.ndjson` だけを拾うので、
    /// 診断ログの名前が `.ndjson` で終わってはならない。
    #[test]
    fn app_log_is_not_picked_up_as_a_session_file() {
        assert!(!APP_LOG_FILE_NAME.ends_with(".ndjson"));
        assert!(APP_LOG_FILE_NAME.ends_with(".log"));
    }

    // --- #1 層2: consumer 耐障害化 (open_log_target フォールバック) ---

    #[test]
    fn open_log_target_ok_for_writable_primary() {
        let dir = std::env::temp_dir().join(format!("gse_ok_{}", std::process::id()));
        let primary = dir.join("gse_oktest.ndjson");
        let (_writer, actual, status) = open_log_target(&primary);
        assert_eq!(status, LogStatus::Ok);
        assert_eq!(actual, primary);
        assert!(primary.exists());
        let _ = fs::remove_file(&actual);
        let _ = fs::remove_dir_all(&dir);
    }

    // --- follow-up F-3: LogChannel は start() までファイルを作らない ---

    /// ⚠️★★ **`LogChannel::new()` は NDJSON を作ってはならない。**
    ///
    /// これが F-3 の本体である。single-instance プラグインに止められる 2 個目のプロセスは
    /// `.setup()` に到達せずに `exit(0)` するので、`new()` が作らないかぎり
    /// **空ファイルは残らない** (decisions R-8 結果 4 の退行の恒久修正)。
    #[test]
    fn log_channel_new_does_not_create_file_until_start() {
        let dir = std::env::temp_dir().join(format!("gse_f3_{}", std::process::id()));
        let path = dir.join("gse_f3test.ndjson");
        let _ = fs::remove_file(&path);

        let channel = LogChannel::new();
        assert!(
            !path.exists(),
            "LogChannel::new() must NOT create the NDJSON: {:?}",
            path
        );

        // ★ start() 前の状態は Ok であってはならない (偽の緑を出さない)。
        {
            let t = channel.target.lock().unwrap();
            assert!(
                matches!(&t.status, LogStatus::Disabled { error } if error == LOGGER_NOT_STARTED),
                "before start(), status must be Disabled(not started), got {:?}",
                t.status
            );
        }

        // ★ 共有ハンドルは start() で**同じ Arc のまま**上書きされること
        //   (`.manage()` に渡した後から差し替えるため。ここが崩れると UI が
        //    「まだ開いていない」状態を握り続ける)。
        let shared = channel.target.clone();
        let (logger, status) = channel.start(path.clone(), None);
        assert_eq!(status, LogStatus::Ok);
        assert!(path.exists(), "start() must create the NDJSON: {:?}", path);
        {
            let t = shared.lock().unwrap();
            assert_eq!(t.path, path, "start() must overwrite the SHARED target");
            assert_eq!(t.status, LogStatus::Ok);
        }

        drop(logger);
        let _ = fs::remove_file(&path);
        let _ = fs::remove_dir_all(&dir);
    }

    /// ★ `start()` の前に送った行を取りこぼさない (channel は先に配られている)。
    #[test]
    fn log_channel_buffers_entries_sent_before_start() {
        let dir = std::env::temp_dir().join(format!("gse_f3buf_{}", std::process::id()));
        let path = dir.join("gse_f3buf.ndjson");
        let _ = fs::remove_file(&path);

        let channel = LogChannel::new();
        let tx = channel.tx.clone();
        // ★ スレッドはまだ走っていない。bounded(512) に溜まる。
        tx.try_send(LogEntry::SessionStart {
            timestamp: 1_700_000_000_000,
        })
        .expect("send before start must succeed (channel exists)");

        let shutdown_rx = channel.shutdown_rx.clone();
        let (logger, _status) = channel.start(path.clone(), None);
        tx.try_send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger should finish");

        let body = fs::read_to_string(&path).unwrap();
        assert!(
            body.contains(r#""type":"session_start""#),
            "entry sent before start() must still be written: {}",
            body
        );
        // ⚠️★ **`meta` は必ず 1 行目**でなければならない。start() 前に溜まった行が
        //   先に書かれると `validate_blocks.py` の `g1_mode` 検査 (`§5.4-6`) と
        //   `analyze.py` の meta 読み取りが壊れる。
        let first = body.lines().next().unwrap_or_default();
        assert!(
            first.contains(r#""type":"meta""#),
            "meta must be the FIRST line even when entries were buffered: {}",
            first
        );

        drop(logger);
        let _ = fs::remove_file(&path);
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn open_log_target_falls_back_to_temp_when_primary_unwritable() {
        // primary の祖先を「ファイル」にして create_dir_all を失敗させる
        // (File::create が親ディレクトリを作れない状況を再現)。
        let blocker = std::env::temp_dir().join(format!("gse_blocker_{}.tmp", std::process::id()));
        {
            let mut f = File::create(&blocker).unwrap();
            writeln!(f, "x").unwrap();
        }
        // blocker(ファイル) の配下に dir を掘ろうとするので create_dir_all が失敗する。
        let unique = format!("gse_fbtest_{}.ndjson", std::process::id());
        let primary = blocker.join("sub").join(&unique);

        let (mut writer, actual, status) = open_log_target(&primary);
        // primary は書けず temp へ Fallback する (consumer は死なない = channel 維持)。
        assert!(
            matches!(status, LogStatus::Fallback { .. }),
            "expected Fallback, got {:?}",
            status
        );
        // actual は temp フォールバック先で、実際に書ける。
        assert_eq!(actual, temp_fallback_path(&primary));
        writeln!(writer, "hello").unwrap();
        writer.flush().unwrap();
        assert!(actual.exists(), "fallback file should exist: {:?}", actual);

        // 後始末
        let _ = fs::remove_file(&actual);
        let _ = fs::remove_file(&blocker);
    }

    #[test]
    fn start_falls_back_keeps_channel_alive_and_writes_entries() {
        // #1 層2 回帰: primary が書けなくても (a) channel が Disconnected にならず send が成功し続け
        // (= カードが閉じる)、(b) fallback ファイルに実エントリが書かれること。
        let blocker =
            std::env::temp_dir().join(format!("gse_start_blocker_{}.tmp", std::process::id()));
        {
            let mut f = File::create(&blocker).unwrap();
            writeln!(f, "x").unwrap();
        }
        // blocker(ファイル) 配下を primary にして File::create を失敗させる。
        let primary = blocker
            .join("sub")
            .join(format!("gse_start_fb_{}.ndjson", std::process::id()));

        let (logger, tx, shutdown_rx, status) = SessionLogger::start(primary.clone(), None);
        assert!(
            matches!(status, LogStatus::Fallback { .. }),
            "expected Fallback, got {:?}",
            status
        );
        // channel は生存 → send は成功する (Disconnected にならない = #1 解消)。
        tx.send(LogEntry::SessionStart { timestamp: 4242 })
            .expect("channel must stay connected on fallback");
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        // 実際の書込先 (= fallback) に SessionStart 行が残る。
        let actual = logger.log_path.clone();
        assert_eq!(actual, temp_fallback_path(&primary));
        let contents = fs::read_to_string(&actual).expect("read back fallback log");
        assert!(
            contents.contains(r#"{"type":"session_start","t":4242}"#),
            "fallback file missing entry:\n{contents}"
        );

        let _ = fs::remove_file(&actual);
        let _ = fs::remove_file(&blocker);
    }

    // -----------------------------------------------------------------------
    // G1: ブロックごとのローテート (protocol.md §1 「1 ブロック = NDJSON 1 ファイル」)
    // -----------------------------------------------------------------------

    /// テスト用の一意なログパス (同時実行しても衝突しない)。
    /// `session_end` を数えるときの目印。
    /// ★ テスト間で共有する (リテラルを複製しない)。
    const SESSION_END_NEEDLE: &str = r#""type":"meta","session_end""#;

    fn rot_test_path(tag: &str, n: u32) -> PathBuf {
        std::env::temp_dir().join("GSE-rot-test").join(format!(
            "gse_{}_{}_{}.ndjson",
            tag,
            std::process::id(),
            n
        ))
    }

    /// ⚠️★★★ **ADR-014 判断 6 の核心の回帰**: `key` 行に **生 VK が 1 つも出ない**。
    ///
    /// `consent.md` の記録項目表は「キーの**種類**（文字キー / バックスペース / 空白 / 改行 など）」と
    /// 約束している。量子化は従来 transfer 境界 (`gse-package`) でのみ効いており、
    /// **ローカル NDJSON には生 VK (キー個体) が残っていた**。2026-08-23 に書き出し境界へ前倒しした。
    ///
    /// ★ 併せて **カテゴリの弁別が生きている**ことも見る (全部 `other` に潰れていないか)。
    #[test]
    fn key_line_records_category_and_never_raw_vk() {
        let p = rot_test_path("keycat", 1);
        let (logger, tx, shutdown_rx, _status) = SessionLogger::start(p.clone(), None);

        tx.send(LogEntry::SessionStart { timestamp: 1000 }).unwrap();
        // 弁別が要る 4 種を送る: 英字 / バックスペース / 文末句読点 / 語内記号。
        for (i, vk) in [0x41u32, 0x08, 0xBE, 0xDB].iter().enumerate() {
            tx.send(LogEntry::Key {
                vk_code: *vk,
                timestamp: 1100 + i as u64,
                is_press: true,
            })
            .unwrap();
        }
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let c = fs::read_to_string(&p).unwrap();
        drop(logger);
        let _ = fs::remove_file(&p);

        // ⚠️★★★ 文字列 `contains` ではなく **フィールド集合** で検査する
        //   (cross-review 2026-08-23 の指摘: `!contains("\"vk\"")` は
        //    「他フィールド名が `vk` を部分文字列に持たない」という暗黙の前提に依存する)。
        let mut cats: Vec<String> = Vec::new();
        for line in c.lines().filter(|l| !l.trim().is_empty()) {
            let v: serde_json::Value =
                serde_json::from_str(line).unwrap_or_else(|e| panic!("bad json {line}: {e}"));
            let obj = v.as_object().expect("each line is an object");
            if obj.get("type").and_then(|t| t.as_str()) != Some("key") {
                continue;
            }
            // ⚠️★★★ `key` 行のキー集合は {type, t, category, press} ちょうど。
            let keys: std::collections::BTreeSet<&str> = obj.keys().map(|k| k.as_str()).collect();
            let want: std::collections::BTreeSet<&str> =
                ["type", "t", "category", "press"].into_iter().collect();
            assert_eq!(keys, want, "key line field set changed: {line}");
            cats.push(
                obj["category"]
                    .as_str()
                    .expect("category is a string")
                    .to_string(),
            );
        }

        // ★ 4 種が別々に弁別されている (全部 `other` に潰れていない)。
        assert_eq!(
            cats,
            vec![
                "alphabetic".to_string(),
                "backspace".to_string(),
                "sentence_punctuation".to_string(),
                "punctuation".to_string(),
            ],
            "categories were not discriminated as expected"
        );
    }

    /// ⚠️★★★ `line_type()` が `capabilities::KNOWN_LINE_TYPES` と食い違わないこと。
    ///
    /// ★ 一時停止 (`recording::is_writable_while_paused`) の判断は `line_type()` の
    /// 文字列に乗っているので、⚠️ **綴りがずれると止めたはずの行が黙って書かれる。**
    #[test]
    fn line_type_matches_known_line_types() {
        use std::collections::BTreeSet;
        let known: BTreeSet<&str> = crate::capabilities::KNOWN_LINE_TYPES
            .iter()
            .copied()
            .collect();
        // ★ 代表を 1 つずつ作って `line_type()` を通す (⚠️ 全 variant を列挙する)。
        let entries = sample_entries_for_line_type();
        let mut seen: BTreeSet<&str> = BTreeSet::new();
        for e in &entries {
            if let Some(t) = e.line_type() {
                assert!(known.contains(t), "{t:?} が KNOWN_LINE_TYPES に無い");
                seen.insert(t);
            }
        }
        // ⚠️★★★ **新しい行種を足したら KNOWN にも足す**、を機械的に固定する。
        //   ★ 逆方向 (KNOWN の全部に variant があるか) は `capabilities` 側の
        //   「logger.rs が書く行種リテラルと突き合わせる網羅テスト」が既に見ている。
        assert!(
            seen.contains("recording_pause"),
            "recording_pause が漏れている"
        );
        assert!(seen.contains("key"));
    }

    /// ⚠️★★★ **一時停止中はデータ行が 1 行も書かれない** (ADR-014 D7-ii)。
    ///
    /// ★ 被験者への約束「すぐ止める」の実体を、**実際に logger を走らせて**固定する。
    /// ⚠️ 通ってよいのは `recording_pause` と `meta` だけである。
    #[test]
    fn paused_logger_writes_no_data_rows() {
        let p = rot_test_path("paused", 1);
        let (logger, tx, shutdown_rx, _status) = SessionLogger::start(p.clone(), None);

        // ★ 「止める」の遷移行 → その後のデータ行 → 「再開する」→ データ行。
        tx.send(LogEntry::RecordingPause {
            timestamp: 1_700_000_000_000,
            paused: true,
        })
        .unwrap();
        // ⚠️ ここで `recording::set_paused` を呼ばない —— ★ ロガーの判断は
        //   **ストリーム内の `RecordingPause` 行**だけで決まる（グローバル Atomic は UI 用）。
        tx.send(LogEntry::Key {
            vk_code: 0x41,
            timestamp: 1_700_000_000_100,
            is_press: true,
        })
        .unwrap();
        tx.send(LogEntry::SessionStart {
            timestamp: 1_700_000_000_150,
        })
        .unwrap();
        tx.send(LogEntry::RecordingPause {
            timestamp: 1_700_000_000_200,
            paused: false,
        })
        .unwrap();
        tx.send(LogEntry::Key {
            vk_code: 0x42,
            timestamp: 1_700_000_000_300,
            is_press: true,
        })
        .unwrap();
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let c = fs::read_to_string(&p).unwrap();
        drop(logger);
        let _ = fs::remove_file(&p);

        let types: Vec<String> = c
            .lines()
            .filter(|l| !l.trim().is_empty())
            .map(|l| {
                let v: serde_json::Value = serde_json::from_str(l).expect("valid json");
                v["type"].as_str().unwrap().to_string()
            })
            .collect();

        // ⚠️ 停止中に送った `key` / `session_start` が 1 行も無いこと。
        assert_eq!(
            types.iter().filter(|t| *t == "session_start").count(),
            0,
            "一時停止中の session_start が書かれている: {types:?}"
        );
        assert_eq!(
            types.iter().filter(|t| *t == "key").count(),
            1,
            "書かれてよい key は再開後の 1 行だけ: {types:?}"
        );
        // ★ 遷移は 2 行とも残る (⚠️ 「止めた」も「再開した」も記録できなければ意味が無い)。
        assert_eq!(
            types.iter().filter(|t| *t == "recording_pause").count(),
            2,
            "遷移行が欠けている: {types:?}"
        );
    }

    /// ★ `line_type_matches_known_line_types` 用の代表エントリ (全 variant)。
    fn sample_entries_for_line_type() -> Vec<LogEntry> {
        vec![
            LogEntry::Key {
                vk_code: 0x41,
                timestamp: 1,
                is_press: true,
            },
            LogEntry::Paste {
                timestamp: 1,
                external_paste_chars: None,
            },
            LogEntry::Feat {
                timestamp: 1,
                f1: 0.0,
                f3: 0.0,
                f4: 0.0,
                f5: 0.0,
                f6: 0.0,
                p_flow: 0.0,
                p_inc: 0.0,
                p_stuck: 0.0,
                raw_x: 0.0,
                raw_y: 0.0,
                ewma_x: 0.0,
                ewma_y: 0.0,
                obs: 0,
                alpha: 0.0,
                keys: 0,
                bs_keys: 0,
            },
            LogEntry::ImeState {
                timestamp: 1,
                on: false,
                active: false,
            },
            LogEntry::SessionStart { timestamp: 1 },
            LogEntry::ReviewMarker { timestamp: 1 },
            LogEntry::RecordingPause {
                timestamp: 1,
                paused: true,
            },
            LogEntry::BlockEnd,
            LogEntry::Rotate {
                new_path: PathBuf::from("x"),
            },
            LogEntry::End,
        ]
    }

    /// ⚠️★★★ **logger → replay の形式契約**を往復で固定する。
    ///
    /// ★ 既存の category 経路は `anonymize_ndjson` を通るため **時刻が相対化された形**
    /// しか検査していなかった。⚠️ **logger が今書く形（category ＋ *絶対* 時刻）** は
    /// どのフィクスチャにも無く、形式ドリフトを検知できなかった
    /// (`.steering/20260823-r3-accept-and-role-category/` D-18)。
    ///
    /// ★ 静的フィクスチャではなく **実際に logger を走らせて書いたログ** を検査するので、
    /// 書き出し側が変わればここが落ちる。
    #[test]
    fn logger_output_keeps_absolute_time_and_all_categories() {
        use crate::analysis::anonymize::KeyCategory;

        let p = rot_test_path("roundtrip", 1);
        let (logger, tx, shutdown_rx, _status) = SessionLogger::start(p.clone(), None);

        // ★ 全 14 カテゴリの代表 VK を 1 つずつ送る。
        let vks: [u32; 14] = [
            0x41, 0x30, 0xBA, 0xBE, 0x09, 0x08, 0x2E, 0x20, 0x0D, 0x25, 0x10, 0x70, 0x1B, 0x07,
        ];
        tx.send(LogEntry::SessionStart {
            timestamp: 1_700_000_000_000,
        })
        .unwrap();
        for (i, vk) in vks.iter().enumerate() {
            tx.send(LogEntry::Key {
                vk_code: *vk,
                timestamp: 1_700_000_000_000 + i as u64 * 100,
                is_press: true,
            })
            .unwrap();
        }
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let c = fs::read_to_string(&p).unwrap();
        drop(logger);
        let _ = fs::remove_file(&p);

        let mut seen: Vec<String> = Vec::new();
        for line in c.lines().filter(|l| !l.trim().is_empty()) {
            let v: serde_json::Value = serde_json::from_str(line).expect("valid json");
            if v.get("type").and_then(|t| t.as_str()) != Some("key") {
                continue;
            }
            // ⚠️ 時刻が **絶対のまま** であること (logger は相対化しない)。
            let t = v["t"].as_u64().expect("t is u64");
            assert!(
                t >= 1_700_000_000_000,
                "logger must keep absolute time: {t}"
            );
            seen.push(v["category"].as_str().unwrap().to_string());
        }

        // ★ 送った VK の category 列と、書かれた category 列が完全一致する。
        let want: Vec<String> = vks
            .iter()
            .map(|vk| KeyCategory::from_vk(*vk).as_str().to_string())
            .collect();
        assert_eq!(
            seen, want,
            "logger category output drifted from KeyCategory"
        );
        // ★ 14 カテゴリすべてが 1 度ずつ現れている (代表 VK の取り違え検出)。
        let distinct: std::collections::BTreeSet<&String> = seen.iter().collect();
        assert_eq!(distinct.len(), 14, "representative vks collided: {seen:?}");
    }

    /// ⚠️★★★ **O1 の宣言変更 1 回が、replay できる形の 2 本に割れる** (ADR-016 判断 4b-1 / 4b-3)。
    ///
    /// ★ `lib.rs::o1_rotate` が送る順序 (**`Rotate` → `SessionMeta`**) をそのまま再現し、
    /// 次の 3 つを固定する:
    ///
    /// 1. ⚠️ **未宣言の区間には `session_meta` 行が 1 本も無い** (判断 4b-3: 行の*不在*で表す)
    /// 2. ★ **宣言は新しいファイルの側に入る** —— ⚠️ 逆順に送ると宣言が旧ファイルへ落ち、
    ///    「大半がその宣言ではないファイル」と「宣言の無いファイル」ができて意味が反転する
    /// 3. ⚠️★★★ **どちらのファイルにも相異なる `task_kind` が 2 つ入らない**
    ///    (★ 入ると `gse-replay` が `Err` で落ちる —— ローテートが要る理由そのもの)
    #[test]
    fn o1_declaration_puts_the_meta_in_the_new_file_and_leaves_the_old_one_undeclared() {
        let p1 = rot_test_path("o1decl", 1);
        let p2 = rot_test_path("o1decl", 2);
        let (logger, tx, shutdown_rx, status) = SessionLogger::start(p1.clone(), None);
        assert_eq!(status, LogStatus::Ok);

        // ── 未宣言の区間 (★ O1 は `session_start` を積まない: 押下が無い) ──
        tx.send(LogEntry::Key {
            vk_code: 65,
            timestamp: 1100,
            is_press: true,
        })
        .unwrap();

        // ── 宣言 1 回 = `o1_rotate` と同じ順序で 2 通 ──
        thread::sleep(Duration::from_millis(5));
        tx.send(LogEntry::Rotate {
            new_path: p2.clone(),
        })
        .unwrap();
        tx.send(LogEntry::SessionMeta {
            timestamp: 2000,
            track: Track::Main,
            task_kind: TaskKind::VibeCoding,
            // ⚠️★ O1 では常に false (判断 O1-5)。
            intervention_enabled: false,
            condition: None,
            label_pool: None,
            head_id: TaskDomain::from(TaskKind::VibeCoding).head_id(),
        })
        .unwrap();
        tx.send(LogEntry::Key {
            vk_code: 66,
            timestamp: 2100,
            is_press: true,
        })
        .unwrap();
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let c1 = fs::read_to_string(&p1).expect("file 1");
        let c2 = fs::read_to_string(&p2).expect("file 2");

        // ① 未宣言の区間は `session_meta` を 1 行も持たない
        assert_eq!(
            c1.matches(r#""type":"session_meta""#).count(),
            0,
            "⚠️ 未宣言の区間に宣言が書かれている (判断 4b-3 の破れ):\n{c1}"
        );
        // ★ それでも「いつ・どの版で取ったか」は残る (ADR-013 D1)
        assert_eq!(c1.matches(r#""type":"meta","session_start""#).count(), 1);
        assert_eq!(c1.matches(r#""type":"meta","session_end""#).count(), 1);

        // ② 宣言は**新しい**ファイルに 1 本だけ入る
        assert_eq!(
            c2.matches(r#""type":"session_meta""#).count(),
            1,
            "⚠️ 宣言が新しいファイルに入っていない:\n{c2}"
        );
        assert!(c2.contains(r#""task_kind":"vibe_coding""#), "{c2}");
        assert!(c2.contains(r#""head_id":"coding_v0""#), "{c2}");
        assert!(
            c2.contains(r#""intervention_enabled":false"#),
            "⚠️ O1 で介入が有効のまま記録されている (判断 O1-5):\n{c2}"
        );

        // ③ ⚠️★★★ どちらのファイルにも `task_kind` は高々 1 種類
        //    (★ 2 種類あると `gse-replay` が Err で落ちる = ローテートが要る理由)
        for (name, c) in [("file1", &c1), ("file2", &c2)] {
            let kinds: std::collections::BTreeSet<&str> =
                ["argumentative", "correspondence", "creative", "vibe_coding"]
                    .into_iter()
                    .filter(|k| c.contains(&format!(r#""task_kind":"{k}""#)))
                    .collect();
            assert!(
                kinds.len() <= 1,
                "⚠️ {name} に相異なる task_kind が {} 種類ある: {kinds:?}",
                kinds.len()
            );
        }

        drop(logger);
        let _ = fs::remove_file(&p1);
        let _ = fs::remove_file(&p2);
    }

    /// ★★ 本タスクの核心の回帰: `Rotate` で **2 本のファイルに分かれ**、
    /// **それぞれが自分の `meta`(session_start) と `session_end` を 1 行ずつ持つ**。
    ///
    /// ⚠️ ★ 2 本目の `session_start` が 1 本目と別の実時刻であることも見る。
    /// `analysis::anonymize::find_session_start` がこの行を `t` の基点にするため、
    /// 引き継いでしまうと**匿名化後の時刻が全部ずれる** (静かに間違う)。
    #[test]
    fn rotate_splits_log_into_two_files_each_with_own_meta() {
        let p1 = rot_test_path("rot", 1);
        let p2 = rot_test_path("rot", 2);
        let (logger, tx, shutdown_rx, status) = SessionLogger::start(p1.clone(), None);
        assert_eq!(status, LogStatus::Ok);

        tx.send(LogEntry::SessionStart { timestamp: 1000 }).unwrap();
        tx.send(LogEntry::Key {
            vk_code: 65,
            timestamp: 1100,
            is_press: true,
        })
        .unwrap();
        tx.send(LogEntry::BlockEnd).unwrap();
        // ★ 2 本目の session_start が別時刻になるよう now_ms の粒度 (ms) 以上待つ。
        thread::sleep(Duration::from_millis(5));
        tx.send(LogEntry::Rotate {
            new_path: p2.clone(),
        })
        .unwrap();
        tx.send(LogEntry::SessionStart { timestamp: 2000 }).unwrap();
        tx.send(LogEntry::Key {
            vk_code: 0x08, // VK_BACK -> category "backspace"
            timestamp: 2100,
            is_press: true,
        })
        .unwrap();
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let c1 = fs::read_to_string(&p1).expect("block 1 file");
        let c2 = fs::read_to_string(&p2).expect("block 2 file");

        // 1 本目: 自分の meta / 自分の key / session_end を 1 行ずつ。
        // ⚠️ ★ `"session_start"` だけで数えると `{"type":"session_start","t":..}` エントリにも
        // 当たる。**meta 行**を数えたいので `"type":"meta","session_start"` で絞る。
        assert_eq!(
            c1.matches(r#""type":"meta","session_start""#).count(),
            1,
            "b1:\n{c1}"
        );
        assert_eq!(c1.matches(r#""type":"meta","session_end""#).count(), 1);
        assert!(
            c1.contains(r#""category":"alphabetic""#),
            "b1 missing its key:\n{c1}"
        );
        // ★ 2 本目の打鍵が 1 本目に混ざっていないこと (= ブロックが本当に分かれた)。
        assert!(
            !c1.contains(r#""category":"backspace""#),
            "b1 leaked b2 key:\n{c1}"
        );

        // 2 本目: 自分の meta / 自分の key / session_end。
        assert_eq!(
            c2.matches(r#""type":"meta","session_start""#).count(),
            1,
            "b2:\n{c2}"
        );
        assert_eq!(c2.matches(r#""type":"meta","session_end""#).count(), 1);
        assert!(
            c2.contains(r#""category":"backspace""#),
            "b2 missing its key:\n{c2}"
        );
        assert!(
            !c2.contains(r#""category":"alphabetic""#),
            "b2 leaked b1 key:\n{c2}"
        );

        // ★ 2 本目の meta が **新ファイルの実時刻** で書かれている (引き継ぎでない)。
        let meta_ts = |c: &str| -> u64 {
            let line = c.lines().next().unwrap();
            let v: serde_json::Value = serde_json::from_str(line).unwrap();
            v["session_start"].as_u64().unwrap()
        };
        assert!(
            meta_ts(&c2) > meta_ts(&c1),
            "block 2 meta must use its own wall clock: {} vs {}",
            meta_ts(&c2),
            meta_ts(&c1)
        );

        // 共有ハンドルがローテート後のパスを指している (UI / quit_app が読む値)。
        assert_eq!(logger.target.lock().unwrap().path, p2);

        let _ = fs::remove_file(&p1);
        let _ = fs::remove_file(&p2);
    }

    /// ⚠️★★ **同じパスへの `Rotate` が来ても、前のブロックを壊さず・混ぜない。**
    ///
    /// 呼び出し側 (UI スレッド) の一意化と実作成 (logger スレッド) の間には窓があり、
    /// ファイル名は秒粒度なので**同じパスが来うる**。守るべき性質は 2 つある:
    /// - 書きかけのブロックを **truncate しない**（code-review MEDIUM）
    /// - ⚠️ 2 つの論理ブロックを **1 ファイルに黙って混ぜない**（cross-review: Codex 指摘）
    ///
    /// ★ logger スレッド側で**先に一意化**するので、同一パス要求は
    /// 「無視」ではなく **別名への正しいローテート**になる（両方の性質を同時に満たす）。
    #[test]
    fn rotate_to_current_path_neither_truncates_nor_merges_blocks() {
        let p = rot_test_path("same", 0);
        let (logger, tx, shutdown_rx, _status) = SessionLogger::start(p.clone(), None);
        tx.send(LogEntry::Key {
            vk_code: 65,
            timestamp: 1,
            is_press: true,
        })
        .unwrap();
        // ★ いま書いている先と同じパスへローテートを要求する。
        let current = logger.target.lock().unwrap().path.clone();
        tx.send(LogEntry::Rotate { new_path: current }).unwrap();
        tx.send(LogEntry::Key {
            vk_code: 0x08, // VK_BACK -> category "backspace"
            timestamp: 2,
            is_press: true,
        })
        .unwrap();
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let c1 = fs::read_to_string(&p).unwrap();
        // ★ 前半の打鍵が生きている = **truncate されていない**。
        assert!(
            c1.contains(r#""category":"alphabetic""#),
            "rotate truncated the block:\n{c1}"
        );
        // ★ 後半の打鍵が混ざっていない = **マージされていない**。
        assert!(
            !c1.contains(r#""category":"backspace""#),
            "blocks were merged:\n{c1}"
        );
        assert_eq!(
            c1.matches(r#""type":"meta","session_end""#).count(),
            1,
            "{c1}"
        );

        // ★ 後半は別名のファイルへ行っている。
        let rotated = logger.target.lock().unwrap().path.clone();
        assert_ne!(rotated, p, "rotation must land on a different path");
        let c2 = fs::read_to_string(&rotated).unwrap();
        assert!(c2.contains(r#""category":"backspace""#), "{c2}");
        assert!(!c2.contains(r#""category":"alphabetic""#), "{c2}");

        let _ = fs::remove_file(&p);
        let _ = fs::remove_file(&rotated);
    }

    /// ★★ **ブロック終了の合図が届き、その時点で `session_end` が読める。**
    ///
    /// ⚠️ G1 の自動提出 (収束器) は「`session_end` を持つファイル」しか触らないので、
    /// 中身が揃う前に合図が来ると **そのブロックを毎回 1 周遅れて拾う**ことになる。
    /// ★ とくに最後のブロックは、`lib.rs` が `overlay` 窓を持つためプロセスが
    /// × では終了せず、⚠️ **次の起動が来ないまま送られない**。
    ///
    /// ## ⚠️★ この検査が **押さえていないこと** (わざと壊して実測した)
    ///
    /// | 壊し方 | 結果 |
    /// |---|---|
    /// | `BlockEnd` の `flush()` を外す | ★ **赤** (3 回とも) |
    /// | `try_send` を送らない | ★ **赤** (5 秒でタイムアウト) |
    /// | ⚠️ `try_send` を `flush()` の **前**に動かす | **緑のまま** (3 回とも) |
    ///
    /// ★ 3 つ目が緑なのは、2 つの操作が同じスレッドで**隣り合っている**ため、
    /// 読み手が「flush 前」の窓を掴めないからである。
    /// → ⚠️ **順序そのものはこの検査では守られていない。** 守っているのは実装側のコメントである。
    /// ★ ここに「順序を検査している」と書かないのは、**発火しない検査を持っているつもり**に
    /// ならないためである。実際に守れているのは
    /// **「合図が来る」「その時点で `session_end` が読める」** の 2 点である。
    #[test]
    fn block_end_ack_arrives_and_session_end_is_readable() {
        let p = rot_test_path("ack", 0);
        let channel = LogChannel::new();
        let tx = channel.tx.clone();
        let block_end_rx = channel.block_end_rx.clone();
        let (logger, _status) = channel.start(p.clone(), None);

        tx.send(LogEntry::Key {
            vk_code: 65,
            timestamp: 1,
            is_press: true,
        })
        .unwrap();
        tx.send(LogEntry::BlockEnd).unwrap();
        block_end_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("BlockEnd ack did not arrive");

        // ★ 合図を受け取った直後に読む。sleep を挟まない (挟んだら何も検査していない)。
        let c = fs::read_to_string(&p).unwrap();
        assert!(
            c.contains(r#""type":"meta","session_end""#),
            "合図の時点で session_end が読めなければならない:\n{c}"
        );
        assert!(
            c.contains(r#""category":"alphabetic""#),
            "直前の行も flush されていること:\n{c}"
        );
        drop(logger);
        let _ = fs::remove_file(&p);
    }

    /// ⚠️ 誰も合図を待っていなくても logger は止まらない (容量 1 の channel を埋めても進む)。
    /// ★ ここが詰まると打鍵の記録が遅れる = ブロックが壊れる。
    #[test]
    fn block_end_ack_never_blocks_the_logger() {
        let p = rot_test_path("ack_nb", 0);
        // ★ 受信端を **捨てる**。以後 try_send は必ず失敗する経路になる。
        let (_logger, tx, shutdown_rx, _status) = SessionLogger::start(p.clone(), None);
        for _ in 0..5 {
            tx.send(LogEntry::BlockEnd).unwrap();
        }
        tx.send(LogEntry::Key {
            vk_code: 0x08, // VK_BACK -> category "backspace"
            timestamp: 2,
            is_press: true,
        })
        .unwrap();
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger stalled on the block-end ack");
        let c = fs::read_to_string(&p).unwrap();
        assert!(c.contains(r#""category":"backspace""#), "{c}");
        let _ = fs::remove_file(&p);
    }

    /// ⚠️★★★ **G-1 の回帰テスト**: セッション実行中の「開始する」再押下 (＝ `RotateForRestart`)。
    ///
    /// ## ★ 何を再現しているか (P010 block07・実発生)
    ///
    /// 従来はローテートせずに `SessionStart` だけを積んでいたため、
    /// **1 ファイルに 2 セッション**が入った (`protocol.md §1`「1 ブロック = 1 ファイル」の破れ)。
    /// → ★ いまは `Rotate` が送られるので、`BlockEnd` が来ていなくても
    /// **前のファイルが `session_end` で閉じ、新しいファイルが開く**。
    ///
    /// ⚠️ ここが本命: **1 本目に `session_start` エントリが 2 本入らないこと**。
    /// ★ 同じ性質を解析側の `validate_blocks.py` も独立に検査している。
    #[test]
    fn double_start_rotates_and_closes_previous() {
        let p1 = rot_test_path("restart", 1);
        let p2 = rot_test_path("restart", 2);
        let (_logger, tx, shutdown_rx, status) = SessionLogger::start(p1.clone(), None);
        assert_eq!(status, LogStatus::Ok);

        // ① ブロック開始 → 打鍵。
        tx.send(LogEntry::SessionStart { timestamp: 1000 }).unwrap();
        tx.send(LogEntry::Key {
            vk_code: 65,
            timestamp: 1100,
            is_press: true,
        })
        .unwrap();

        // ② ⚠️ **`BlockEnd` を送らない** (＝ ブロックは実行中のまま)。ここで再押下が起きる。
        thread::sleep(Duration::from_millis(5));
        tx.send(LogEntry::Rotate {
            new_path: p2.clone(),
        })
        .unwrap();
        tx.send(LogEntry::SessionStart { timestamp: 2000 }).unwrap();
        tx.send(LogEntry::Key {
            vk_code: 0x08, // VK_BACK -> category "backspace"
            timestamp: 2100,
            is_press: true,
        })
        .unwrap();
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let c1 = fs::read_to_string(&p1).expect("1 本目");
        let c2 = fs::read_to_string(&p2).expect("2 本目");

        // ★★★ 本命: 1 本目の `session_start` エントリは **1 本だけ**。
        assert_eq!(
            c1.matches(r#"{"type":"session_start""#).count(),
            1,
            "★ 1 ファイルに 2 セッションが入っている (P010 block07 の再発):\n{c1}"
        );
        // ★ `BlockEnd` を送っていなくても `Rotate` が閉じる。
        assert_eq!(
            c1.matches(r#""type":"meta","session_end""#).count(),
            1,
            "前のセッションが閉じられていない:\n{c1}"
        );
        assert!(
            c1.contains(r#""category":"alphabetic""#),
            "1 本目の打鍵が無い:\n{c1}"
        );
        assert!(
            !c1.contains(r#""category":"backspace""#),
            "再押下後の打鍵が 1 本目に混ざった:\n{c1}"
        );

        // ★ 2 本目は自分の meta と自分の打鍵を持つ。
        assert_eq!(c2.matches(r#""type":"meta","session_start""#).count(), 1);
        assert_eq!(c2.matches(r#"{"type":"session_start""#).count(), 1);
        assert!(
            c2.contains(r#""category":"backspace""#),
            "2 本目の打鍵が無い:\n{c2}"
        );

        let _ = fs::remove_file(&p1);
        let _ = fs::remove_file(&p2);
    }

    /// ★ ADR-013 D4 (穴 B): `dropped_delta` は **前回行からの差分**として書かれる。
    ///
    /// ⚠️ `dropped` (累積) は**そのまま残る** (非破壊)。
    /// ★ 差分の計算は `lib.rs` の監視スレッドが行うので、ここでは
    /// 「合成した値がそのままの意味で 1 行に並ぶ」ことを固定する。
    #[test]
    fn dropped_delta_is_written_alongside_cumulative_dropped() {
        let p = rot_test_path("dropdelta", 0);
        let (_logger, tx, shutdown_rx, _status) = SessionLogger::start(p.clone(), None);

        // 1 行目: 累積 3 / 増分 3 (プロセス開始からの増分)。
        tx.send(LogEntry::HookHealth {
            timestamp: 1000,
            alive: true,
            starved_ms: 0,
            rehook: false,
            dropped: 3,
            dropped_delta: 3,
        })
        .unwrap();
        // 2 行目: 累積 10 / 増分 7。⚠️ ここを累積で読むと「10 個落ちた区間」と誤読される。
        tx.send(LogEntry::HookHealth {
            timestamp: 2000,
            alive: true,
            starved_ms: 0,
            rehook: false,
            dropped: 10,
            dropped_delta: 7,
        })
        .unwrap();
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let c = fs::read_to_string(&p).unwrap();
        assert!(c.contains(r#""dropped":3,"dropped_delta":3"#), "{c}");
        assert!(c.contains(r#""dropped":10,"dropped_delta":7"#), "{c}");
        // ★ 手書き書式なのでパースを確かめる。
        for line in c.lines().filter(|l| l.contains(r#""type":"hook_health""#)) {
            let v: serde_json::Value = serde_json::from_str(line).unwrap();
            assert!(v["dropped_delta"].is_u64(), "{line}");
        }
        let _ = fs::remove_file(&p);
    }

    /// ★ ADR-013 D4 (穴 A): `starve_window` 行の形を固定する。
    #[test]
    fn starve_window_line_shape_is_stable() {
        let p = rot_test_path("starvewin", 0);
        let (_logger, tx, shutdown_rx, _status) = SessionLogger::start(p.clone(), None);
        tx.send(LogEntry::StarveWindow {
            timestamp: 1_700_000_060_000,
            win_ms: 60_000,
            n_lt30: 7,
            sum_lt30_ms: 4_200,
        })
        .unwrap();
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let c = fs::read_to_string(&p).unwrap();
        assert!(
            c.contains(
                r#"{"type":"starve_window","t":1700000060000,"win_ms":60000,"n_lt30":7,"sum_lt30_ms":4200}"#
            ),
            "{c}"
        );
        let _ = fs::remove_file(&p);
    }

    /// ⚠️ `BlockEnd` の直後に `End` (アプリ終了) が来ても `session_end` は **1 行だけ**。
    /// 二重に書くと解析側がブロック終端を取り違える。
    #[test]
    fn block_end_then_quit_writes_session_end_once() {
        let p = rot_test_path("once", 0);
        let (_logger, tx, shutdown_rx, _status) = SessionLogger::start(p.clone(), None);
        tx.send(LogEntry::BlockEnd).unwrap();
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let c = fs::read_to_string(&p).unwrap();
        assert_eq!(
            c.matches(r#""type":"meta","session_end""#).count(),
            1,
            "session_end must appear exactly once:\n{c}"
        );
        let _ = fs::remove_file(&p);
    }

    /// ⚠️★★★ **D-1 が守っている順序の「意味」をここで固定する** (2026-08-21・Codex 指摘 4)。
    ///
    /// ★ `lib.rs` の `BLOCK_TRANSITION` が保証するのは
    /// 「**`BlockEnd` は次のブロックの `Rotate` より前に channel へ入る**」だけである。
    /// ⚠️ **なぜそれが要るのか**は logger 側の挙動で決まっているので、**ここでテストする**。
    ///
    /// ★ 本テストが赤くなるのは、`Rotate` 処理の `block_closed = false` を消したときである。
    /// ⚠️ そのとき `lib.rs` の排他は**要らなくなるのではなく意味が変わる** —— 気づけるようにしておく。
    ///
    /// ⚠️ ★ 純関数テスト (`g1::decide_block_end`) は「押下が**先**」しか閉じられない。
    /// **「押下が**後**」の帰結**——順序が逆転したときに何が壊れるか——は本テストが持つ。
    #[test]
    fn a_rotate_before_block_end_moves_session_end_into_the_new_file() {
        let first = rot_test_path("order", 10);
        let second = rot_test_path("order", 11);
        let _ = fs::remove_file(&first);
        let _ = fs::remove_file(&second);

        let (_logger, tx, shutdown_rx, _status) = SessionLogger::start(first.clone(), None);
        // ⚠️★★★ **順序が逆転した場合**を再現する: 先に `Rotate`、後から `BlockEnd`。
        tx.send(LogEntry::Rotate {
            new_path: second.clone(),
        })
        .unwrap();
        tx.send(LogEntry::BlockEnd).unwrap();
        tx.send(LogEntry::End).unwrap();
        shutdown_rx
            .recv_timeout(Duration::from_secs(5))
            .expect("logger did not shut down in time");

        let old_file = fs::read_to_string(&first).unwrap();
        // ⚠️ `Rotate` は衝突回避で別名へ振りうる (`unique_path_from`) ので、
        //   ★ 実際に開かれたファイルを**名前で決め打ちしない**。
        let new_file = fs::read_to_string(&second)
            .unwrap_or_else(|_| panic!("rotate 先が開かれていない: {second:?}"));

        // ★ 旧ファイルは `Rotate` の時点で 1 回だけ閉じられている (ここは正しい)。
        assert_eq!(
            old_file.matches(SESSION_END_NEEDLE).count(),
            1,
            "旧ファイルの session_end が 1 本でない:\n{old_file}"
        );
        // ⚠️★★★ **これが壊れ方である**: 後から来た `BlockEnd` が
        //   **始まったばかりの新しいファイル**へ `session_end` を書く。
        //   ★ `protocol.md §1`「1 ブロック = 1 ファイル」の破れであり、
        //     以後の `key` / `feat` は `session_end` の**後ろ**に積まれる。
        assert_eq!(
            new_file.matches(SESSION_END_NEEDLE).count(),
            1,
            "★ Rotate が block_closed を false に戻すので、後続の BlockEnd は\n\
             新ファイルへ session_end を書く。⚠️ ここが 0 になったなら logger の挙動が\n\
             変わっている (lib.rs の BLOCK_TRANSITION の前提も見直すこと):\n{new_file}"
        );

        let _ = fs::remove_file(&first);
        let _ = fs::remove_file(&second);
    }

    /// ★★ 非回帰の要: `g1_mode` が `None` のとき `meta` 行に **`g1_mode` キーが出ない**。
    ///
    /// ## ⚠️★★★ 2026-08-19 に期待値を更新した (ADR-013 D1)
    ///
    /// 本テストは元々「**従来と 1 バイトも変わらない**」を固定していた。
    /// ★ ADR-013 D1 が `app_version` / `capabilities` の追記を決めたので、
    /// **その主張はもう成り立たない**。→ 主張を弱めるのではなく、**何が守られているかを書き直す**:
    ///
    /// 1. ★ `g1_mode` は G1 のときにしか出ない (**元々の意図**。ここは不変)
    /// 2. ★ **キーの順序**が固定されている (追記は必ず末尾)
    /// 3. ★ 手書き JSON が**パースできる**
    ///
    /// ⚠️ 更新の根拠 (2026-08-19 実測): ゴールデン (`tests/snapshots/*.json`) は
    /// `FeatSnapshot` の配列で **`meta` を含まない**ため、この行の変更では壊れない。
    /// 読み手 (`anonymize.rs` / `validate_blocks.py`) も **JSON パース**である。
    #[test]
    fn meta_line_is_byte_identical_when_not_g1() {
        let mut buf: Vec<u8> = Vec::new();
        write_meta_start(&mut buf, 1234, None);
        let s = String::from_utf8(buf).unwrap();

        // ★ キー順まで含めて固定する (追記は必ず末尾であること)。
        let expected = format!(
            "{{\"type\":\"meta\",\"session_start\":1234,\"hmm_version\":\"{}\",\
             \"app_version\":\"{}\",\"capabilities\":{}}}\n",
            crate::analysis::engine::HMM_VERSION,
            crate::capabilities::app_version(),
            crate::capabilities::capabilities_json(),
        );
        assert_eq!(s, expected);

        // ⚠️★ **元々の意図**: G1 でないログに `g1_mode` を混ぜない。
        assert!(
            !s.contains("g1_mode"),
            "G1 でないのに g1_mode が出ている: {s}"
        );

        // ★ 手書き書式なので毎回パースを確かめる。
        let v: serde_json::Value = serde_json::from_str(s.trim()).unwrap();
        assert_eq!(v["type"], "meta");
        assert!(v.get("g1_mode").is_none());
        assert!(v["capabilities"]["unconditional"].is_array());
        assert!(v["capabilities"]["threshold_gated"].is_array());
    }

    /// ★ G1 のときだけ引き金を刻む (マーカーが外れたことを事後に検出できるようにする)。
    #[test]
    fn meta_line_records_g1_source_when_g1() {
        let mut buf: Vec<u8> = Vec::new();
        write_meta_start(&mut buf, 1234, Some(crate::g1::G1Source::Marker));
        let s = String::from_utf8(buf).unwrap();
        assert!(s.contains(r#""g1_mode":"marker""#), "{s}");
        // JSON として妥当であること (手書き書式なので毎回確かめる)。
        let v: serde_json::Value = serde_json::from_str(s.trim()).unwrap();
        assert_eq!(v["g1_mode"], "marker");
        assert_eq!(v["session_start"], 1234);
    }

    /// ⚠️★ ファイル名は**秒粒度**。同じ秒に 2 回ローテートしても
    /// **前のブロックを truncate で消さない**こと。
    #[test]
    fn next_session_path_does_not_reuse_existing_file() {
        let dir = std::env::temp_dir().join(format!("gse_nsp_{}", std::process::id()));
        fs::create_dir_all(&dir).unwrap();
        let base = dir.join("gse_20260805_223000.ndjson");

        // 未使用なら base をそのまま返す (通常経路を変えない)。
        assert_eq!(unique_path_from(base.clone()), base);

        // ★ 既に在るなら別名を返す (= truncate で前のブロックを消さない)。
        File::create(&base).unwrap();
        let second = unique_path_from(base.clone());
        assert_ne!(second, base, "rotation must not reuse an existing path");
        assert_eq!(second, dir.join("gse_20260805_223000_2.ndjson"));

        // ★ 3 本目もぶつからない。
        File::create(&second).unwrap();
        assert_eq!(
            unique_path_from(base.clone()),
            dir.join("gse_20260805_223000_3.ndjson")
        );

        let _ = fs::remove_file(&base);
        let _ = fs::remove_file(&second);
        let _ = fs::remove_dir_all(&dir);
    }

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
            "high_need_but_low_opportunity",
            &["recent_dismiss".to_string()],
        );
        assert_eq!(
            line,
            r#"{"type":"intervention_decision","t":1700000000000,"action":"defer","need_score":0.7800,"opportunity_score":0.3200,"p_stuck":0.7800,"idle_ms":4200,"reason":"high_need_but_low_opportunity","suppressed_by":["recent_dismiss"]}"#
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

    // ---- ADR-006 Phase 2b: task_kind -> domain head のルーティング表 ----

    /// ★ 2b のルーティング表そのものを固定する。
    ///
    /// この表が変わるということは「同じ task_kind が別の推論器で採点される」という
    /// **挙動変更**であり、`HMM_VERSION` の bump とゴールデン再生成を伴う。
    #[test]
    fn task_kind_routes_to_expected_domain() {
        assert_eq!(
            TaskDomain::from(TaskKind::Argumentative),
            TaskDomain::Writing
        );
        assert_eq!(
            TaskDomain::from(TaskKind::Correspondence),
            TaskDomain::Writing
        );
        assert_eq!(
            TaskDomain::from(TaskKind::Creative),
            TaskDomain::WritingFallback
        );
        assert_eq!(TaskDomain::from(TaskKind::VibeCoding), TaskDomain::Coding);
    }

    /// Creative / Correspondence は Writing head で走る (ADR-006 #3 からの逸脱・D-6)。
    /// Creative は識別子だけ `writing_fallback` に分かれる。
    #[test]
    fn creative_and_correspondence_route_to_writing_head() {
        use crate::analysis::heads::head_for;

        assert_eq!(
            head_for(TaskDomain::from(TaskKind::Correspondence))
                .head_id()
                .as_str(),
            "writing"
        );
        assert_eq!(
            head_for(TaskDomain::from(TaskKind::Creative))
                .head_id()
                .as_str(),
            "writing_fallback"
        );
    }

    /// Creative は **数値挙動が Writing と完全に同一**である。
    /// 分かれているのは head_id だけ = ゴールデンへの影響はゼロ。
    #[test]
    fn creative_latent_axes_match_writing_head() {
        use crate::analysis::features::Features;
        use crate::analysis::heads::head_for;

        let f = Features {
            f1_flight_time_median: 200.0,
            f3_correction_rate: 0.12,
            f4_burst_length: 6.0,
            f5_pause_count: 3.0,
            f6_pause_after_del_rate: 0.15,
            keys: 0,
            bs_keys: 0,
        };
        let writing = head_for(TaskDomain::Writing);
        let creative = head_for(TaskDomain::WritingFallback);

        for ime_open in [true, false] {
            assert_eq!(
                writing.latent_axes(&f, ime_open),
                creative.latent_axes(&f, ime_open),
                "Creative は Writing head へ流すので数値は一致するはず (ime_open={ime_open})"
            );
        }
    }

    /// `task_kind` が未知の文字列なら `TaskKind::parse` が None を返し、
    /// 呼び出し側 (`lib.rs` / `bin/replay.rs`) が Writing へフォールバックする。
    /// ★ 既存 Phase1 ログはそもそも `session_meta` を持たないため、この経路が
    ///   ゴールデン 4 本の byte-equal を支えている。
    #[test]
    fn unknown_task_kind_falls_back_to_writing() {
        use crate::analysis::heads::head_for;

        let domain = match TaskKind::parse("hand_writing_on_paper") {
            Some(kind) => TaskDomain::from(kind),
            None => TaskDomain::Writing,
        };
        assert_eq!(domain, TaskDomain::Writing);
        assert_eq!(head_for(domain).head_id().as_str(), "writing");
    }

    // ---- session_meta ----

    #[test]
    fn session_meta_line_main_vibe_coding() {
        // condition / label_pool 省略時は null を出す (旧フィクスチャ互換)。
        let line = format_session_meta_line(
            1_700_000_000_000,
            Track::Main,
            TaskKind::VibeCoding,
            true,
            None,
            None,
            HeadId::CodingV0,
        );
        assert_eq!(
            line,
            r#"{"type":"session_meta","track":"main","task_kind":"vibe_coding","intervention_enabled":true,"condition":null,"label_pool":null,"head_id":"coding_v0","ts":1700000000000}"#
        );
    }

    #[test]
    fn session_meta_line_exploratory_track() {
        let line = format_session_meta_line(
            42,
            Track::Exploratory,
            TaskKind::Argumentative,
            false,
            None,
            None,
            HeadId::Writing,
        );
        assert_eq!(
            line,
            r#"{"type":"session_meta","track":"exploratory","task_kind":"argumentative","intervention_enabled":false,"condition":null,"label_pool":null,"head_id":"writing","ts":42}"#
        );
    }

    #[test]
    fn session_meta_line_with_condition_and_label_pool() {
        let line = format_session_meta_line(
            7,
            Track::Main,
            TaskKind::Creative,
            true,
            Some(Condition::BlindCalibration),
            Some(LabelPool::CalibrationBlind),
            HeadId::WritingFallback,
        );
        assert_eq!(
            line,
            r#"{"type":"session_meta","track":"main","task_kind":"creative","intervention_enabled":true,"condition":"blind_calibration","label_pool":"calibration_blind","head_id":"writing_fallback","ts":7}"#
        );
    }

    // ---- feat ----

    #[test]
    fn feat_line_fixes_field_order_and_precision() {
        // ⚠️★★★ 既存フィールドの位置と小数桁数はゴールデンの byte-equal 契約。
        // Tier 0 の keys / bs_keys は **行末に append** され、既存部分を 1 文字も動かさない。
        // ★ 全フィールドに異なる値を入れて、取り違え (p_inc↔p_stuck 等) も検出できるようにする。
        let line = format_feat_line(&FeatLine {
            timestamp: 1_700_000_001_000,
            f1: 104.567,   // {:.2} → 104.57
            f3: 0.333_333, // {:.4} → 0.3333
            f4: 4.25,      // {:.2} → 4.25
            f5: 2.0,       // {:.1} → 2.0
            f6: 0.5,       // {:.4} → 0.5000
            p_flow: 0.6,
            p_inc: 0.3,
            p_stuck: 0.1,
            raw_x: 0.123_456, // {:.4} → 0.1235 (四捨五入)
            raw_y: 0.7,
            ewma_x: 0.25,
            ewma_y: 0.8,
            obs: 13,
            alpha: 0.3, // {:.2} → 0.30
            keys: 9,
            bs_keys: 3,
        });
        assert_eq!(
            line,
            r#"{"type":"feat","t":1700000001000,"f1":104.57,"f3":0.3333,"f4":4.25,"f5":2.0,"f6":0.5000,"p_flow":0.6000,"p_inc":0.3000,"p_stuck":0.1000,"raw_x":0.1235,"raw_y":0.7000,"ewma_x":0.2500,"ewma_y":0.8000,"obs":13,"alpha":0.30,"keys":9,"bs_keys":3}"#
        );
    }

    #[test]
    fn feat_line_records_key_counts_as_integers_only() {
        // ★ Tier 0 は「打鍵の数」のみ。文字内容・VK 生値は 1 バイトも入らない (data-privacy)。
        // 0 打のウィンドウでも null ではなく 0 を書く (書くときは常に値を書く)。
        let line = format_feat_line(&FeatLine {
            timestamp: 1,
            f1: 0.0,
            f3: 0.0,
            f4: 0.0,
            f5: 0.0,
            f6: 0.0,
            p_flow: 0.34,
            p_inc: 0.33,
            p_stuck: 0.33,
            raw_x: 0.0,
            raw_y: 0.0,
            ewma_x: 0.0,
            ewma_y: 0.0,
            obs: 0,
            alpha: 0.0,
            keys: 0,
            bs_keys: 0,
        });
        assert!(line.ends_with(r#""keys":0,"bs_keys":0}"#));
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

    /// ⚠️★★★ **旧 `intervention_response_line_wall_with_elapsed` を置き換えた**
    /// (Wall 削除・2026-08-23)。★ 旧テストは Wall の早期解除/通常解除で `elapsed_ms` を
    /// 検査していた。
    ///
    /// ⚠️ **`elapsed_ms` を書く経路は Wall だけだった**ので、現状 **production では常に `None`** である。
    /// ★ フォーマット自体は additive に残す（NDJSON schema で `elapsed_ms` は optional）ので、
    /// **書式の契約だけをここで固定する**。⚠️ 使う経路が復活しないなら次の整理で落とす候補。
    #[test]
    fn intervention_response_line_can_still_carry_elapsed_ms() {
        assert_eq!(
            format_intervention_response_line(
                12345,
                "nudge",
                DismissReason::JustClose,
                Some(45_000)
            ),
            r#"{"type":"intervention_response","t":12345,"action":"nudge","reason":"just_close","elapsed_ms":45000}"#
        );
    }

    #[test]
    fn new_enums_roundtrip() {
        for r in [
            DismissReason::NotStuck,
            DismissReason::WantToStruggle,
            DismissReason::JustClose,
            DismissReason::Silent,
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
        let line = format_vignette_response_line(
            1_700_000_000_000,
            "v2f1",
            ExpectedQuadrant::Flow,
            2,
            5,
            8_400,
            3,
        );
        assert_eq!(
            line,
            r#"{"type":"vignette_response","vignette_id":"v2f1","expected_quadrant":"flow","q1_friction":2,"q2_progress":5,"elapsed_ms":8400,"changes":3,"ts":1700000000000}"#
        );
    }

    #[test]
    fn vignette_response_line_idle_quadrant() {
        let line = format_vignette_response_line(99, "v2d2", ExpectedQuadrant::Idle, 1, 1, 0, 2);
        assert_eq!(
            line,
            r#"{"type":"vignette_response","vignette_id":"v2d2","expected_quadrant":"idle","q1_friction":1,"q2_progress":1,"elapsed_ms":0,"changes":2,"ts":99}"#
        );
    }

    #[test]
    fn vignette_response_constructor_clamps_q_to_1_5() {
        // DC-4: 構築子経由で q1/q2 が 1..=5 に clamp される (0→1, 9→5)。
        let entry = LogEntry::vignette_response(
            7,
            "v2s1".to_string(),
            ExpectedQuadrant::Stuck,
            0,
            9,
            1_200,
            4,
        );
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
    /// format 関数の単体テストでは捕捉できない **アーム内の引数取り違え** (例: フラグ同士の
    /// intervention_enabled の入れ替え) を read-back で守る。
    #[test]
    fn writer_loop_emits_new_variants_to_file() {
        let mut path = std::env::temp_dir();
        path.push(format!(
            "gse_probe_schema_test_{}.ndjson",
            std::process::id()
        ));
        let (_logger, tx, shutdown_rx, _status) = SessionLogger::start(path.clone(), None);

        tx.send(LogEntry::SessionMeta {
            timestamp: 1000,
            track: Track::Main,
            task_kind: TaskKind::VibeCoding,
            intervention_enabled: true,
            condition: Some(Condition::BlindCalibration),
            label_pool: Some(LabelPool::CalibrationBlind),
            head_id: HeadId::CodingV0,
        })
        .unwrap();
        tx.send(LogEntry::InterventionResponse {
            timestamp: 1500,
            action: "nudge".to_string(),
            reason: DismissReason::NotStuck,
            elapsed_ms: None,
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
            vignette_id: "v2s1".to_string(),
            expected_quadrant: ExpectedQuadrant::Stuck,
            q1_friction: 5,
            q2_progress: 1,
            elapsed_ms: 6_500,
            changes: 5,
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
            r#"{"type":"session_meta","track":"main","task_kind":"vibe_coding","intervention_enabled":true,"condition":"blind_calibration","label_pool":"calibration_blind","head_id":"coding_v0","ts":1000}"#
        ), "session_meta 行が不正 (引数取り違えの可能性):\n{contents}");
        assert!(
            contents.contains(
                r#"{"type":"intervention_response","t":1500,"action":"nudge","reason":"not_stuck"}"#
            ),
            "intervention_response (nudge) 行が不正:\n{contents}"
        );
        assert!(contents.contains(
            r#"{"type":"probe_assignment","probe_id":"p-1","scheduled_ts":2000,"session_elapsed_ms":1000}"#
        ), "probe_assignment 行が不正:\n{contents}");
        assert!(contents.contains(
            r#"{"type":"realtime_label","probe_id":"p-1","source":"random_probe","q1_friction":3,"q2_progress":4,"answered":true,"skip_reason":"none","latency_ms":500,"analysis_window_start_ms":2969,"analysis_window_end_ms":2999,"ts":3000}"#
        ), "realtime_label 行が不正:\n{contents}");
        assert!(contents.contains(
            r#"{"type":"vignette_response","vignette_id":"v2s1","expected_quadrant":"stuck","q1_friction":5,"q2_progress":1,"elapsed_ms":6500,"changes":5,"ts":4000}"#
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
        let (_logger, tx, shutdown_rx, _status) = SessionLogger::start(path.clone(), None);

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
