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
        /// G1 統制タスク実験モードの引き金 (`"marker"` | `"env"`)。**start 形状のみ**。
        ///
        /// ⚠️ ★ **G1 実施時にしか出ない**ので、通常運用の NDJSON は従来と byte 単位で同一である
        /// (ゴールデンスナップショットと既存フィクスチャの非回帰がこれに依存する)。
        ///
        /// ★ なぜ記録するか: マーカーが外れる / アプリをフォルダの外に出す /
        /// launcher の `open -a` で通常アプリが起動する、のいずれでも**黙って通常モードになる**。
        /// この行が無いブロックは「G1 モードで取れていない」と**事後に判定できる**
        /// (`preregistration.md §5.4` 第 10 版 / `.steering/20260805-g1-app-mode-and-log-rotation`)。
        #[serde(skip_serializing_if = "Option::is_none")]
        g1_mode: Option<String>,
    },
    /// ユーザーが「開始する」ボタンを押した時刻。
    SessionStart { t: u64 },
    /// キーストロークイベント (raw VK コード + 押下/離上)。
    Key { t: u64, vk: u32, press: bool },
    /// ペーストイベント (Ctrl+V / Cmd+V) の発生時刻と文字数。
    /// AI 依存度指標 (D4) 向けに**回数** (行数) を、(b) 自力解決率 (v0.4 §4.2
    /// `manual_contribution_ratio`) 向けに `external_paste_chars` (ペースト**文字数=整数のみ**)
    /// を記録する。1 ペースト = 1 行。VK + 修飾キー状態から検出し、クリップボードは
    /// **長さのみ取得して中身は即破棄**する (**中身は一切記録しない**・data-privacy CD1)。
    /// 旧フィクスチャ互換のため `external_paste_chars` は省略可 (取得不能時も `null`)。
    Paste {
        t: u64,
        external_paste_chars: Option<u64>,
    },
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
        /// ★ Tier 0 (記録のみ): 特徴量ウィンドウ内の総キー押下数 (= `f3` の分母)。
        /// **打鍵の数のみ**で、どのキーか・何を書いたかは含まない (data-privacy CD1)。
        ///
        /// ⚠️★★★ **累積カウンタではなく、窓の右端は「最後の打鍵時刻」であって `t` ではない。**
        /// **沈黙中は同じ値が毎秒くり返される**ので、**feat 行をまたいで足し上げてはいけない**
        /// (実測つきの説明は `analysis/loop_step.rs` の `FeatSnapshot::keys` の doc が正本)。
        ///
        /// ⚠️ **producer は常に値を書く**が、schema 上は省略可 (`Option`) にしている。
        /// Tier 0 配線より前に収集された NDJSON には本フィールドが無く、それらも
        /// この schema で検証できる必要があるため (`Paste.external_paste_chars` と同じ扱い・
        /// ADR-005 additive)。「読むときは省略可・書くときは必須」の非対称は意図的。
        ///
        /// ⚠️★ HMM にも X/Y 合成式にも流していない (記録のみ)。`HMM_VERSION` は不変。
        #[serde(default)]
        keys: Option<u64>,
        /// ★ Tier 0 (記録のみ): 特徴量ウィンドウ内の BS/Del 押下数 (= `f3` の分子)。
        /// `f3` は `{:.4}` 丸めのため、`keys − bs_keys` を整数で得るには分子も整数で必要になる。
        /// 窓の意味・省略可の理由は `keys` と同じ。
        #[serde(default)]
        bs_keys: Option<u64>,
    },
    /// IME 入力モード/候補ウィンドウ状態の切替。
    ImeState { t: u64, on: bool, active: bool },
    /// ⚠️★ キーボードフックの生存状態の変化 (`input::liveness`)。
    ///
    /// `alive=false` は「フックは設置済みだが、システムに入力があるのに
    /// コールバックが呼ばれていない」状態を指す。★ **判断ではなく測った量** (`starved_ms`) を
    /// 併記するので、解析側が閾値を変えて再解釈できる。
    /// 背景: `windows-verification.md` §5-7 (5 分間 0 打のブロックが正常提出された)。
    HookHealth {
        t: u64,
        alive: bool,
        starved_ms: u64,
        rehook: bool,
        /// 分析スレッドへ渡せずに捨てた打鍵イベントの累計。
        /// ★ 「フックが呼ばれた」と「記録できた」は別なので両方残す。
        dropped: u64,
    },
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
    /// 介入提示に対するユーザー応答 (reason)。`intervention_decision` (判定側) とは別の
    /// 「ユーザー応答側」ログ (WBS 0.8 / v0.4 §9)。Nudge dismiss は Need/Opportunity 誤りを分離、
    /// Wall は早期解除/通常解除(順守) を区別する (Phase A2)。固定カテゴリ + 時刻のみ。本文は含まない。
    /// `elapsed_ms` = Wall 提示(/shake)〜解除(/unlock) の経過時間。Nudge dismiss では省略 (`null`)。
    /// `action="wall"` かつ `elapsed_ms=null` は通常フロー外解除 (/shake 未経由) を意味し、
    /// 後段解析は経過時間を持つ実 early_unlock と区別できる。
    InterventionResponse {
        t: u64,
        action: InterventionActionDto,
        reason: DismissReasonDto,
        #[serde(skip_serializing_if = "Option::is_none")]
        elapsed_ms: Option<u64>,
    },
    /// v0.3 較正スモーク: セッション開始宣言 (track / task_kind / Monk・介入トグル)。
    /// timestamp は既存の `t` と別命名の `ts` (§14 設計準拠)。
    /// `condition` = 実験条件 (WBS 0.11)、`label_pool` = ラベルプール (WBS 0.4)。
    /// 旧フィクスチャ互換のため両者とも省略可 (`null`)。
    SessionMeta {
        track: TrackDto,
        task_kind: TaskKindDto,
        monk_mode: bool,
        intervention_enabled: bool,
        condition: Option<ConditionDto>,
        label_pool: Option<LabelPoolDto>,
        /// ADR-006 Phase 2b: どの domain head がこのセッションを採点したか。
        /// 旧フィクスチャ互換のため省略可 (`null`)。
        head_id: Option<HeadIdDto>,
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
        /// 場面の表示から**記録に成功するまで**の所要時間 (ms)。読まずに送った回答の事後分離用。
        /// 送信に失敗して再送した場合は、初回表示からの累積になる。
        elapsed_ms: u64,
        /// Q1/Q2 スライダー合計の値変更回数。即答と熟慮を分ける。
        changes: u16,
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

/// ADR-006 Phase 2b: どの domain head がセッションを採点したか (session_meta)。
///
/// `task_kind` (被験者の宣言) と対にして残す。ルーティング表が変われば
/// 同じ `task_kind` でも別の head になるため、実際に走った推論器を記録する。
/// `writing_fallback` = Creative を Writing head で採点している状態
/// (ADR-006 #3 からの意図的な逸脱)。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum HeadIdDto {
    Writing,
    WritingFallback,
    CodingV0,
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

/// `intervention_response` の理由 (reason)。
/// Nudge dismiss (WBS 0.8 / v0.4 §9): `not_stuck` = Need 誤り、`want_to_struggle` = Opportunity 誤り、
/// `just_close` = 単に閉じる、`silent` = 理由未選択 (フェードアウト)。
/// Wall 応答 (Phase A2): `early_unlock` = 早期解除 (非順守)、`completed` = 通常解除 (順守)、
/// `idle_timeout` = 長時間アイドル自動解除 (enum 予約のみ・現状未配線)。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum DismissReasonDto {
    NotStuck,
    WantToStruggle,
    JustClose,
    Silent,
    EarlyUnlock,
    Completed,
    IdleTimeout,
}

/// `session_meta` の実験条件 (WBS 0.11)。Phase 1b=`blind_calibration`、Phase 2 AB/BA=`a`/`b`、
/// Phase 3 MRT=`nudge`/`defer`、それ以外=`baseline`。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ConditionDto {
    BlindCalibration,
    A,
    B,
    Nudge,
    Defer,
    Baseline,
}

/// `session_meta` のラベルプール (WBS 0.4)。X1 判定には `calibration_blind` のみ使用。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum LabelPoolDto {
    CalibrationBlind,
    PostIntervention,
}
