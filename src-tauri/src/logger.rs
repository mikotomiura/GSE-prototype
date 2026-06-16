use std::fs::{self, File};
use std::io::{BufWriter, Write};
use std::path::PathBuf;
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use crossbeam_channel::{bounded, Receiver, RecvTimeoutError, Sender};

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

/// `LogEntry::SessionMeta` の NDJSON 1 行を生成する純粋関数。
fn format_session_meta_line(
    timestamp: u64,
    track: Track,
    task_kind: TaskKind,
    monk_mode: bool,
    intervention_enabled: bool,
) -> String {
    format!(
        r#"{{"type":"session_meta","track":"{}","task_kind":"{}","monk_mode":{},"intervention_enabled":{},"ts":{}}}"#,
        track.as_str(),
        task_kind.as_str(),
        monk_mode,
        intervention_enabled,
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
    /// v0.3 較正スモーク: セッション開始宣言 (track / task_kind / Monk・介入トグル)。
    /// 数値・固定カテゴリのみ。`ts` で timestamp を持つ (既存 `t` とは別命名・§14 準拠)。
    SessionMeta {
        timestamp: u64,
        track: Track,
        task_kind: TaskKind,
        monk_mode: bool,
        intervention_enabled: bool,
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
                        LogEntry::SessionMeta {
                            timestamp,
                            track,
                            task_kind,
                            monk_mode,
                            intervention_enabled,
                        } => {
                            let _ = writeln!(
                                writer,
                                "{}",
                                format_session_meta_line(
                                    timestamp,
                                    track,
                                    task_kind,
                                    monk_mode,
                                    intervention_enabled
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

/// セッションログの保存先パスを決定する。
///
/// ## 優先順位 (2 段、明示的制御)
/// 1. 環境変数 `GSE_DATASET` が設定されていれば `$GSE_DATASET/raw/P000/`
/// 2. そうでなければ fallback `~/Documents/GSE-sessions/`
///
/// ## 以前の挙動との差分
/// 旧実装は exe の兄弟を最大 5 階層上まで走査して `gse-dataset/raw/P000/` を
/// 暗黙的に優先していたが、CI・別開発マシン・Tauri bundle 配布先で予期しないパス
/// に書き込むリスクがあったため、20260416 に env + fallback の 2 段に簡素化した。
/// 開発者が `gse-dataset` リポジトリに書きたい場合は shell rc / PowerShell
/// `$PROFILE` で `GSE_DATASET` を明示的に設定する (docs/development-guidelines.md §Session データ管理 参照)。
///
/// ## 可観測性
/// 決定したディレクトリは `tracing::info!` で常時出力する。どのセッションが
/// どこに書かれたかが運用ログから即確認できる。
pub fn default_log_path() -> PathBuf {
    let dir = if let Ok(dataset) = std::env::var("GSE_DATASET") {
        PathBuf::from(dataset).join("raw").join("P000")
    } else {
        fallback_log_dir()
    };
    tracing::info!(
        resolved_log_dir = %dir.display(),
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
        let line = format_session_meta_line(
            1_700_000_000_000,
            Track::Main,
            TaskKind::VibeCoding,
            false,
            true,
        );
        assert_eq!(
            line,
            r#"{"type":"session_meta","track":"main","task_kind":"vibe_coding","monk_mode":false,"intervention_enabled":true,"ts":1700000000000}"#
        );
    }

    #[test]
    fn session_meta_line_exploratory_monk_mode() {
        let line =
            format_session_meta_line(42, Track::Exploratory, TaskKind::Argumentative, true, false);
        assert_eq!(
            line,
            r#"{"type":"session_meta","track":"exploratory","task_kind":"argumentative","monk_mode":true,"intervention_enabled":false,"ts":42}"#
        );
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
            r#"{"type":"session_meta","track":"main","task_kind":"vibe_coding","monk_mode":false,"intervention_enabled":true,"ts":1000}"#
        ), "session_meta 行が不正 (引数取り違えの可能性):\n{contents}");
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
}
