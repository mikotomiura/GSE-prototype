//! Phase 1 dataset-repo-setup: NDJSON セッションログの JSON Schema を機械生成するための
//! DTO (Data Transfer Object) ミラー型。
//!
//! **本モジュールは production path ではない**。logger::LogEntry の手書き NDJSON 出力を
//! 忠実に反映したミラー型であり、`bin/emit_schema` からのみ使用される。schemars による
//! JsonSchema 派生と serde Serialize のみが目的で、実際の NDJSON 書き込みは `logger.rs`
//! の `writeln!` ベース実装が行う (float フォーマット固定のため手書き実装を維持)。
//!
//! ## なぜ DTO ミラーが必要か
//!
//! `logger::LogEntry` は `f64` の小数桁数固定フォーマット (`{:.4}`) を `writeln!` で
//! 直接指定しており、`serde::Serialize` 経由で出すと形式が崩れて gse-replay の
//! ゴールデン byte-equal が落ちる。したがって `LogEntry` 本体には `Serialize` を
//! 派生させない方針で、schema 生成のためだけに本 DTO を用意する。
//!
//! ## 追加時のメンテ
//!
//! `LogEntry` に新バリアントや新フィールドが入ったら、本 DTO も同期する必要がある。
//! 同期漏れは `.github/workflows/ci.yml` の schema drift check で機械的に検知される
//! (emit_schema の出力が `src-tauri/schema/current.json` と diff すると CI が FAIL)。

use schemars::JsonSchema;
use serde::Serialize;

/// NDJSON 1 行の種別を表す tagged union。`type` フィールドでバリアントを識別する。
/// logger::LogEntry の NDJSON 出力と同じ shape。
#[derive(Serialize, JsonSchema)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum LogEntryDto {
    /// セッション境界マーカー。
    /// - 開始: `{"type":"meta","session_start":<ms>,"hmm_version":"<semver>"}`
    /// - 終了: `{"type":"meta","session_end":<ms>}`
    ///
    /// **排他制約 (schema では表現されていない producer 側の事実上のルール)**:
    /// 実際の `logger.rs` は上記 2 形状のどちらか一方しか emit しない。
    /// 具体的には:
    /// - start: `session_start` と `hmm_version` が Some、`session_end` は None
    /// - end:   `session_end` が Some、他 2 つは None
    /// 「3 つとも Some」「3 つとも None」「start と end を同時に」は不正だが
    /// schemars の tagged enum では 2 形状を別 variant にすると同一 tag 衝突が
    /// 発生するため、スキーマ上は loose にして Option 3 つを並列にしている。
    /// validator 側の追加チェックを入れたい場合は外部 JSON Logic で補う。
    Meta {
        #[serde(skip_serializing_if = "Option::is_none")]
        session_start: Option<u64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        hmm_version: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        session_end: Option<u64>,
    },
    /// ユーザーが「開始する」ボタンを押した時刻。
    SessionStart { t: u64 },
    /// キーストロークイベント (raw VK コード + 押下/離上)。
    Key { t: u64, vk: u32, press: bool },
    /// 1Hz ゲートで吐かれる特徴量 + HMM 状態確率 + 診断データ。
    ///
    /// **obs の型について**: `logger::LogEntry::Feat` 本体では `obs: usize` だが、
    /// schema 上は `u64` に格上げしている。理由:
    /// - `usize` は 32-bit ターゲットで u32 に縮む可能性があり、schema の
    ///   `uint64` 指定と実 NDJSON 数値表現の間に乖離が生まれる
    /// - 実運用では obs は 0..=25 の小さな整数しか入らないため u64 で十分安全
    /// - 将来 usize → u64 の意図的格上げを logger 側に反映する場合でも schema は不変
    Feat {
        t: u64,
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
        obs: u64,
        alpha: f64,
    },
    /// IME 入力モード/候補ウィンドウ状態の切替。
    ImeState { t: u64, on: bool, active: bool },
    /// Phase 1 Ground Truth ユーザーラベル。
    /// `recovered_at` はログ記録時は常に null、`gse-replay --metrics` で後付け算出。
    UserLabel {
        t: u64,
        label: UserLabelKindDto,
        recovered_at: Option<u64>,
    },
    /// 事後レビュー用ブックマークマーカー。認知状態ラベルではなく、
    /// 「ここを後で見返したい」という意図のみを記録する。
    ReviewMarker { t: u64 },
    /// IME 変換セッションの影ログ (Phase 2b, Windows のみ)。
    /// `dwell_ms` は IME 候補ウィンドウ表示〜非表示の時間、
    /// `nav` は変換中の矢印キー押下回数、`abandon` は ESC による変換放棄。
    ImeShadow {
        t: u64,
        dwell_ms: u64,
        nav: u32,
        abandon: bool,
    },
    /// MVP Opportunity 判定ログ。
    /// Need/Opportunity と抑制理由を後から検証するための固定カテゴリ記録。
    InterventionDecision {
        t: u64,
        action: InterventionActionDto,
        need_score: f64,
        opportunity_score: f64,
        p_stuck: f64,
        idle_ms: u64,
        wall_accum_ms: u64,
        reason: String,
        suppressed_by: Vec<String>,
    },
    /// v0.3 較正スモーク: セッション開始宣言 (track / task_kind / Monk・介入トグル)。
    /// timestamp は既存の `t` と別命名の `ts` (§14 設計準拠)。
    SessionMeta {
        track: TrackDto,
        task_kind: TaskKindDto,
        monk_mode: bool,
        intervention_enabled: bool,
        ts: u64,
    },
    /// v0.3 較正スモーク: ランダムプローブ割当の監査記録。
    /// `probe_id` は backend 生成の不透明 ID (本文非由来)。
    ProbeAssignment {
        probe_id: String,
        scheduled_ts: u64,
        session_elapsed_ms: u64,
    },
    /// v0.3 較正スモーク: 主データ (リアルタイム/自己マーカー回答)。
    ///
    /// **不変条件 (schema では緩く、producer 側で強制)**:
    /// - skip (`answered=false`) ⇒ `q1_friction`/`q2_progress` は null
    /// - `answered=true` ⇒ `q1_friction`/`q2_progress` は 1..=5
    /// - `source=self_marker` ⇒ `probe_id` は null
    ///
    /// `logger.rs` の `LogEntry::realtime_label_answered` / `..._skipped` コンストラクタが
    /// これらを保証する。schemars は Option を緩く出すため validator 側で補検証する。
    RealtimeLabel {
        probe_id: Option<String>,
        source: ProbeSourceDto,
        q1_friction: Option<u8>,
        q2_progress: Option<u8>,
        answered: bool,
        skip_reason: SkipReasonDto,
        latency_ms: u64,
        analysis_window_start_ms: u64,
        analysis_window_end_ms: u64,
        ts: u64,
    },
    /// v0.3 較正スモーク: 尺度理解テスト回答 (ビネット)。常に回答あり (q1/q2 は 1..=5)。
    /// `expected_quadrant` は教示の正解ラベル (`UserLabelKindDto` とは別物で `idle` を含む)。
    VignetteResponse {
        vignette_id: String,
        expected_quadrant: ExpectedQuadrantDto,
        q1_friction: u8,
        q2_progress: u8,
        ts: u64,
    },
}

/// Ground Truth ラベルの種別。NDJSON 文字列は "flow" / "incubation" / "stuck"。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum UserLabelKindDto {
    Flow,
    Incubation,
    Stuck,
}

/// 介入ポリシーの出力種別。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum InterventionActionDto {
    None,
    Nudge,
    Wall,
    Defer,
}

/// v0.3 較正スモークのセッション系列。`main` = 本系列、`exploratory` = 探索系列。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum TrackDto {
    Main,
    Exploratory,
}

/// v0.3 較正スモークの課題種別 (session_meta)。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum TaskKindDto {
    Argumentative,
    Correspondence,
    Creative,
    VibeCoding,
}

/// `realtime_label` の出所。`random_probe` = backend 割当、`self_marker` = 自発 hotkey。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ProbeSourceDto {
    RandomProbe,
    SelfMarker,
}

/// `realtime_label` の skip 理由。`none` = 回答済み、`dont_remember` / `dismissed` = skip。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum SkipReasonDto {
    None,
    DontRemember,
    Dismissed,
}

/// `vignette_response` の想定象限。教示の正解ラベル (`idle` を含む)。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ExpectedQuadrantDto {
    Flow,
    Stuck,
    Incubation,
    Idle,
}
