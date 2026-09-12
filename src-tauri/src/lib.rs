pub mod analysis;
// アプリ本体の診断ログ (tracing) をファイルに残す writer。
// ⚠️ stdout だけだと Finder 起動の .app では**どこにも残らない** (2026-08-08 実測)。
pub mod applog;
// ★ **このビルドが何を記録できるか**の単一情報源 (ADR-013 D1/D2)。OS API 非依存の宣言表。
// ⚠️ 送出元ベースで決め `#[cfg]` を反映する (writer から導出すると macOS で ime_shadow を過大申告する)。
pub mod capabilities;
// G1 統制タスク実験の「G1 モード」判定 (OS API 非依存の純ロジック + current_exe のみ)。
// 効果 (ローテート / 5 分でのブロック終了 / プローブ停止 / 二重起動 fail-loud) は lib.rs が適用する。
pub mod g1;
pub mod input;
pub mod logger;
// ⚠️★★★ O1 (R3-a・自然作業の常時収集) の「O1 モード」判定と、そのモードでだけ変わる方針
//   (ADR-014 D6 / ADR-016 判断 4b-0)。★ `g1` と同層の純判定モジュールで、
//   効果 (門を通す / 常時のインジケータ / 宣言でのローテート / 猶予つき自動提出) は
//   `lib.rs` と `reconcile` が適用する。
pub mod o1;
// 提出ファイル名ラベル用 participant_id 検証の単一情報源 (feature 非依存)。
// packaging (提出 CLI) と submit_latest_session (アプリ内提出) の双方が参照する。
pub mod participant_id;
// 提出ツール (gse-package / gse-submit) 共有の匿名化+age 暗号化 (data-privacy SSOT)。
// age 依存はこの module 経由のみ。blind アプリ本体 (default features) には載せない (D3)。
#[cfg(feature = "package")]
pub mod packaging;
// 提出物 (.age / .sent / 台帳 / 参加者 ID / 送信先設定) の**状態の規約**。
// ⚠️ ★ feature gate の外に置く: 盲検アプリ本体も「未送信 N 件」を数えるため
// (数えるのに age は要らない)。両側が同じ規約を読むことで drift を防ぐ。
pub mod submission;
// ⚠️★★★ セッション NDJSON の **行の分類規則の単一真実源** (2026-09-03)。
//   ★ 同じ規則が packaging / reconcile / o1 の 3 か所に手書きコピーされていて食い違っていた。
//   ⚠️ feature gate の**外**に置く (盲検アプリ本体の o1 sweep も、package 側の収束器も読む)。
pub mod ndjson_scan;
// G1 自動提出の収束器 (ディスクの状態を突き合わせ、足りない仕事だけをする)。
// age と HTTP を使うので package feature 側 (`gse-submit --reconcile` が実行主体)。
#[cfg(feature = "package")]
pub mod reconcile;
// ⚠️★★★ O1 (R3): 記録の **即時一時停止 / 再開** (ADR-014 D7-ii)。
//   ★ 依存を 1 つも持たない葉モジュール (logger / lib.rs / Frontend の 3 者から読まれる)。
pub mod recording;
// ⚠️★★★ O1 (R3): 被験者による **区間指定削除** (ADR-014 D7-iii / 判断 3 の根拠 3)。
//   ★ OS API を呼ばない純粋なファイル層なので `input/` にも `analysis/` にも入れない。
pub mod redaction;
// macOS: overlay 窓を非アクティブ NSPanel 化する FFI グルー (decisions D7)。
#[cfg(target_os = "macos")]
mod overlay_panel;
pub mod schema_dto;
#[cfg(target_os = "macos")]
pub mod sensors;
// メニューバー / タスクトレイの常駐アイコン (計測中かの表示 + いつでも終了)。
// ⚠️ 窓を閉じると UI ごと消えるのに計測は生きている、という穴を塞ぐ。
pub mod tray;

use crate::analysis::engine::{CognitiveState, CognitiveStateEngine};
use crate::analysis::heads::TaskDomain;
use crate::analysis::intervention::{
    InterventionAction, InterventionDecision, InterventionInput, InterventionPolicyState,
};
use crate::analysis::loop_step::FeatSnapshot;
use crate::logger::{
    Condition, DismissReason, ExpectedQuadrant, LabelPool, LogEntry, LogStatus, ProbeRef,
    ProbeSource, SharedLogTarget, SkipReason, TaskKind, Track, UserLabelKind,
};
use crossbeam_channel::{self, Receiver, RecvTimeoutError, Sender};
#[allow(unused_imports)]
use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};
use tauri::{Emitter, Manager, State};

// Phase 1 Ground Truth: 2 秒デバウンス用タイムスタンプ（epoch ms）。
// Tauri コマンド経路とグローバルホットキー経路の両方から参照される。
static LAST_LABEL_MS: AtomicU64 = AtomicU64::new(0);
const LABEL_DEBOUNCE_MS: u64 = 2000;

// ReviewMarker: 1 秒デバウンス (連打防止)。UserLabel とは独立。
static LAST_MARKER_MS: AtomicU64 = AtomicU64::new(0);
const MARKER_DEBOUNCE_MS: u64 = 1000;

// Task B: 自己マーカー hotkey (Ctrl+Shift+Alt+M) の 1 秒デバウンス (MARKER_DEBOUNCE_MS を共用)。
static LAST_SELF_MARKER_MS: AtomicU64 = AtomicU64::new(0);

// Task B: プローブスケジューラがセッション開始時刻 (epoch ms) を読むための共有値。
// start_session が Release で store し、専用プローブスレッドが Acquire で読む。
// 0 = セッション未開始。値が変わったらスレッドはスケジューラを再初期化する。
static SESSION_START_MS: AtomicU64 = AtomicU64::new(0);

// M0 凍結 (decisions D1): 較正セッション (condition=blind_calibration) では収量優先の
// ProbeConfig::calibration() を使う。record_session_meta が condition から設定する。
static SESSION_IS_CALIBRATION: AtomicBool = AtomicBool::new(false);

// M0 凍結 (decisions D1): プローブスレッドが「session_meta 受領後」にスケジューラを初期化する
// ためのゲート。**どの session_start 向けの meta か** を記録し、scheduler は session_start と
// 照合してから calibration 選択を採用する (cross-review HIGH: 世代未照合だと前セッションの古い
// meta が新セッションに適用されうる)。frontend は start_session (SESSION_START_MS を set) →
// record_session_meta (この値を set) の順で呼ぶ。0 = まだどの世代の meta も未受領。
// プローブの schedule は session_start に anchor されるため、初期化が最大 1Hz 分遅れても決定性・
// session_elapsed 計算は不変 (warm-up 31s 以内に必ず確定する)。
static SESSION_META_FOR_START_MS: AtomicU64 = AtomicU64::new(0);

// M0 (D1・code-review HIGH): session_meta 受領を待つ猶予。これを超えても未受領なら
// プローブのサイレント全滅を避け default プロファイルで初期化し warn する。warm-up (31s) より
// 十分短く、通常 (数 ms で受領) はこの fallback 経路に入らない。
const PROBE_META_READY_GRACE_MS: u64 = 5_000;

// Task C: セッションが宣言する介入の有効/無効 (session_meta.intervention_enabled)。
// record_session_meta が設定し、get_intervention_decision が抑止判断に使う。
// main/overlay の両ウィンドウが同コマンドを叩くため単一情報源で抑止される (cross-review)。
static INTERVENTION_ENABLED: AtomicBool = AtomicBool::new(true);

// 通常は false のまま = 既存挙動と完全同一 (pilot 非汚染)。

// 終了処理が既に走っているか。⚠️ ★ 終了の入口は 3 つある
// (画面の「セッション終了」/ トレイの「終了」/ main 窓の ×)。二重に走らせると
// ログを閉じる待ち合わせが二重になり `exit(0)` が競合する。★ 最初の 1 回だけ通す。
static SHUTTING_DOWN: AtomicBool = AtomicBool::new(false);

// デバッグ用: 次回の get_intervention_decision (overlay) で Nudge を一度だけ強制表示するフラグ。
// `force_nudge` コマンドが true にし、overlay ウィンドウの判定が swap で消費する (ワンショット)。
// overlay 自身が消費するため main の decide() 上書きと race しない。通常は false = 既存挙動と同一。
static FORCE_NUDGE: AtomicBool = AtomicBool::new(false);

// ---------------------------------------------------------------------------
// G1 統制タスク実験モード (experiments/20260801-controlled-friction-task)
// ---------------------------------------------------------------------------

/// G1 モードの引き金 (`"marker"` / `"env"`)。`run()` が起動時に 1 回だけ書き、以後は読み取り専用。
///
/// ⚠️ ★ `OnceLock` にしているのは「実行時に切り替えられない」ことを型で示すためである。
/// 実行時トグルにすると、プローブを**スレッドごと起こさない**ことで
/// 「発火はしたが黙殺した」状態を構造的に消している設計が崩れる (D-7)。
static G1_MODE: std::sync::OnceLock<Option<&'static str>> = std::sync::OnceLock::new();

/// このプロセスで開始したブロック数。2 回目以降の `start_session` がローテートする判断に使う。
/// ⚠️ ★ **`session_active` が false→true になったときだけ**増やす (連打・再試行で増やさない)。
static G1_BLOCKS_STARTED: AtomicU64 = AtomicU64::new(0);

/// ⚠️★★★ **いまのセッションで `record_session_meta` が成功したか** (2026-08-19・G-1)。
///
/// ★ 用途は 1 つだけ: 「**二度押し**」と「**`record_session_meta` 失敗後の再押下**」を分ける。
/// ⚠️ 後者でローテートすると**中身がほぼ空の孤児ファイルが 1 本増える**
/// (★ 旧 code-review HIGH が防いでいたもの)。
/// ⚠️ **`packaging::has_any_data_row` はこれを止められない** —— 同関数が読み飛ばすのは
/// `meta` / `hook_health` / `ime_state` だけで、**`session_start` 行があるファイルは通る**
/// (2026-08-19 実測)。★ したがって「提出側で二重化されている」という説明は成り立たない。
static SESSION_META_RECORDED: AtomicBool = AtomicBool::new(false);

/// 分析スレッドがドレイン (非アクティブ) 分岐に入っているか。
///
/// ⚠️★ **G1 のブロック終了で `session_end` の後ろに `feat` / `key` 行が続くのを防ぐための同期点。**
/// `session_active=false` を立てても、分析スレッドは既に `rx.recv_timeout(...)` に入っており
/// **次の 1Hz マークまで最大 ~1000ms ブロックしうる**。その 1 イテレーションが
/// `try_send(Key/Feat)` を投げるので、★ **固定 sleep では追い越しを防げない**
/// (code-review HIGH。当初 200ms にしていたのは「非アクティブ時 sleep は 50ms」という
/// 誤った根拠に基づいていた——待つべきは `recv_timeout` の上限である)。
/// → **分析スレッドがドレインに入ったことを観測してから** `BlockEnd` を送る。
static ANALYSIS_IDLE: AtomicBool = AtomicBool::new(true);

// ---------------------------------------------------------------------------
// O1 (R3-a) 自然作業の常時収集 — 宣言と日次ローテート
// ---------------------------------------------------------------------------

/// ⚠️★★★ **いま宣言されている作業の種類。`None` = 未宣言。**
///
/// ★ ADR-016 **判断 4b-3**: `unknown` を enum に足さず、**`session_meta` 行の *不在***で
/// 未宣言を表す。→ この値が `None` のあいだ、⚠️ **`session_meta` 行を 1 本も書かない**。
///
/// ⚠️ **推測して埋めない** —— 同意文書 §2 逐語「こちらで勝手に推測して埋めることはしません」。
/// ★ 観測から推定して埋めるのは **ADR-010 D3 の閉ループ禁止**にも触れる。
///
/// ★ 日次ローテートが `session_meta` を書き直すかどうかもこの値で決まる
/// (⚠️ 未宣言のまま日をまたいだファイルに、宣言を捏造しない)。
static DECLARED_TASK_KIND: Mutex<Option<logger::TaskKind>> = Mutex::new(None);

/// ⚠️★ **いま書いているセッションファイルを開いた時刻** (epoch ms)。日次ローテートの基準。
///
/// ★ `Instant` ではなく **epoch ms** にしてあるのは、スリープ / 休止のあいだも
/// 経過に含めるためである (⚠️ `Instant` は OS によって止まる)。
/// ★ 0 = まだ開いていない (日次ローテートは動かない)。
static O1_LOG_OPENED_MS: AtomicU64 = AtomicU64::new(0);

/// ⚠️★★★ **O1 のローテートを 1 本に直列化する排他** (code-reviewer MEDIUM・2026-08-27)。
///
/// ★ 入口は 2 つある —— **宣言 UI** (`declare_task_kind`) と **日次ローテートスレッド**。
/// ⚠️ ログのロックだけでは足りない: `DECLARED_TASK_KIND` の読みと `O1_LOG_OPENED_MS` の
/// 更新がその外にあると、交錯したときに
/// **ファイルに書かれた `session_meta` と UI / engine head が食い違う**
/// (★ 日次スレッドが「未宣言」を読んだ直後に宣言が入り、
/// **宣言したばかりのファイルを未宣言として閉じ直す**)。
///
/// ★ ロック順序は **`O1_ROTATE` → `LogState` → `DECLARED_TASK_KIND`** で固定する。
/// ⚠️ 他の箇所 (`get_recording_status`) はこの 3 つを**入れ子にしない**ので、循環はできない。
///
/// ★ G1 の [`BLOCK_TRANSITION`] と同じ役割・同じ流儀である
/// (⚠️ ★ **通常運用 / G1 では誰も取らない** = 無競合)。
static O1_ROTATE: Mutex<()> = Mutex::new(());

/// ローテート 1 回で宣言をどう扱うか。
///
/// ⚠️ ★ **`Option<TaskKind>` にしない。** ★ 「新しく宣言する」と「いまの宣言を引き継ぐ」は
/// 意味が違い、⚠️ 後者は **ロックの中で現在値を読む**必要がある (上記の交錯を避けるため)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum O1Declaration {
    /// ★ 宣言 UI からの 1 回。**この値を新しいファイルへ書き、確定させる**。
    Set(logger::TaskKind),
    /// ★ 日次ローテート。**いまの宣言をそのまま引き継ぐ**。
    /// ⚠️ 未宣言 (`None`) なら `session_meta` を 1 行も書かない (判断 4b-3)。
    KeepCurrent,
}

/// 宣言されている作業の種類を読む (`None` = 未宣言)。
fn declared_task_kind() -> Option<logger::TaskKind> {
    *DECLARED_TASK_KIND.lock().unwrap_or_else(|p| p.into_inner())
}

/// ⚠️★★★ **ブロック遷移の直列化点** (D-1・2026-08-21)。
///
/// 「開始する」の押下 ([`start_session`]) と **ブロックの自動終了**は、この 1 本を通る。
///
/// ## ★ 守っているのは値ではなく **順序** である
///
/// > **`BlockEnd` は、次のブロックの `Rotate` より前にログ channel へ入る。**
///
/// ⚠️ これが破れると `protocol.md §1`「1 ブロック = 1 ファイル」が壊れる ——
/// ★ **G1 リブートの原因 (P010 block07) と同じ失敗クラス**である。
/// `preregistration.md §3.6` がブロックの事後除外を禁じているので、走り出したら**回復不能**。
///
/// ## ⚠️ なぜ原子変数の比較だけでは足りないか
///
/// [`start_session`] は `Rotate` / `SessionStart` を**ログのロックの中**で送るが、
/// `SESSION_START_MS.store(now)` は**ロックを抜けた後**で行う。
/// → ★ 「**`Rotate` は送られたが `SESSION_START_MS` はまだ 0**」という窓が実在するので、
/// ⚠️ `compare_exchange` や再確認では「押下が後」の交錯を閉じられない。
/// (`logger.rs` の `Rotate` は `block_closed` を `false` に戻すため、
/// 直後の `BlockEnd` が**新しいファイルへ `session_end` を書く**。)
///
/// ## ⚠️★★ ロック順序 (★ 反転させない)
///
/// ```text
/// BLOCK_TRANSITION  →  latest_feat  →  intervention  →  log
/// ```
///
/// ★ **最も外側**に置く。⚠️ 自動終了スレッドは `log` の `Mutex` を**取らない**
/// (自分の `Sender` clone を持っている) ので、★ **循環はそもそも作れない**。
///
/// ## ★ 通常運用 (G1 でない) への影響はゼロ
///
/// 自動終了スレッドは `if g1_mode().is_some()` の中でしか spawn されないので、
/// ★ 非 G1 では **他に取る者がいない = 無競合**である。観測可能な挙動は 1 バイトも変わらない。
static BLOCK_TRANSITION: Mutex<()> = Mutex::new(());

/// [`BLOCK_TRANSITION`] を取る唯一の入口。★ poison を repo 全体の流儀で扱う。
///
/// ⚠️ poison しても**諦めない**: 遷移の排他を落とすと、この関数が防いでいる
/// ブロック境界の破れがそのまま戻る。
fn lock_block_transition() -> std::sync::MutexGuard<'static, ()> {
    BLOCK_TRANSITION.lock().unwrap_or_else(|p| p.into_inner())
}

/// G1 モードか (引き金つき)。`None` なら通常運用。
fn g1_mode() -> Option<&'static str> {
    *G1_MODE.get().unwrap_or(&None)
}

// ---------------------------------------------------------------------------
// ログ状態 (quit_app からも参照できるよう Tauri state で管理)
// ---------------------------------------------------------------------------

pub(crate) struct LogState {
    tx: Sender<LogEntry>,
    /// ⚠️ ★ **いま書いている先**の共有ハンドル。G1 のローテートで変わるので、
    /// 起動時のパスを `String` で持ち回ってはならない (前ブロックのファイルを指し続ける)。
    target: SharedLogTarget,
    /// ロガースレッドが End を処理し終えたときに通知される受信端
    shutdown_rx: Receiver<()>,
}

impl LogState {
    /// 他スレッドへ渡すためロガー Sender を clone して返す。
    /// 生の `tx` を公開せず「スレッドへ move する用途の clone」だけを意図として露出する。
    pub(crate) fn clone_log_tx(&self) -> Sender<LogEntry> {
        self.tx.clone()
    }

    /// いま書いている NDJSON のパス (ローテート追随)。
    fn current_path(&self) -> String {
        // ⚠️ poison 時に空文字を返すと `quit_app` がそれを behavioral_gt.py に渡し、
        // `Path::new("").parent()` から**意図しないフォルダを開く** (code-review MEDIUM)。
        // 他のロック箇所と同じく into_inner でデータを取り出す。
        self.target
            .lock()
            .unwrap_or_else(|p| p.into_inner())
            .path
            .to_string_lossy()
            .to_string()
    }

    /// ⚠️★★★ **いま実際に書けているか** (R-11)。★ ローテートで変わるので共有ハンドルから読む。
    ///
    /// `LogStatus::Ok` 以外 (temp へフォールバック / 破棄) は **`false`** である。
    fn status(&self) -> bool {
        self.target.lock().unwrap_or_else(|p| p.into_inner()).status == LogStatus::Ok
    }
}

/// 分析スレッドへのリセットシグナル。
/// start_session コマンドが `true` にセットすると、分析スレッドが
/// FeatureExtractor をクリアして `false` に戻す。
struct ResetSignal(Arc<AtomicBool>);

/// セッションアクティブフラグ。
/// start_session が呼ばれるまで分析スレッドは打鍵イベントをドレインする。
struct SessionActive(Arc<AtomicBool>);

/// 直近の 1Hz Feat スナップショット。
/// Opportunity MVP は Need を `p_stuck` から取り、Opportunity の補助情報として
/// F3/F4/F6 と idle_ms を読む。OS API はここに入れず、analysis 出力のみを保持する。
struct LatestFeatState(Arc<Mutex<Option<FeatSnapshot>>>);

/// MVP Opportunity のポリシー状態。
/// cooldown / daily cap / recent dismiss を保持する。
struct InterventionState(Arc<Mutex<InterventionPolicyState>>);

/// ログ書込先の状態 (fail-loud バナー用)。`run()` が SessionLogger の共有ハンドルを
/// managed state に保持し、`get_log_status` コマンドがフロントへ返す。
///
/// ⚠️ ★ 値のコピーではなく共有ハンドルを持つ。G1 のローテート先が書けずに temp へ落ちたとき、
/// 起動時の `Ok` を返し続けると **バナーが出ないまま想定外の場所に書き続ける** ため。
struct LogStatusState(SharedLogTarget);

/// フロントへ返すログ状態 DTO (#1 層2 fail-loud)。`ok=false` ならバナーを常時表示する。
/// data-privacy: キーストローク内容は含めない。パスは診断のため含める (本文ではない)。
#[derive(serde::Serialize, Clone)]
struct LogStatusDto {
    ok: bool,
    /// "ok" | "fallback" | "disabled"
    mode: String,
    /// 被験者/研究者に見せる固定和文メッセージ (mode に応じて切替)。
    message: String,
    /// 実際に書いている / 書こうとしたパス (診断用・null 許容)。
    actual_path: Option<String>,
}

/// `try_send` 失敗を Full / Disconnected で区別した診断メッセージに変換する (#1 層2 誤誘導ラベル是正)。
/// crossbeam の `TrySendError` は両者を Display で区別するが、従来コマンドは両方 "log channel full"
/// で潰しており **disconnected (consumer 死亡 = ログファイル作成失敗)** を full と誤表示していた。
///
/// NOTE: 本修正で consumer は `File::create` 失敗でも死なず (logger.rs `open_log_target` の sink 縮退)、
/// Disconnected は原則発生しない。万一 Disconnected が出たら consumer スレッドの異常終了 ≒
/// プログラミングエラーなので、コマンドは敢えて `Err` を上流 (フロント) に伝え **fail-loud** とする
/// (カードは閉じず・診断文言で原因が分かる)。これは「静かに握り潰さない」#1 の設計意図と一致する。
fn log_send_error<T>(e: crossbeam_channel::TrySendError<T>) -> String {
    match e {
        crossbeam_channel::TrySendError::Full(_) => {
            "log channel full (consumer backlog)".to_string()
        }
        crossbeam_channel::TrySendError::Disconnected(_) => {
            "log channel disconnected (logger thread died — likely log file create failure)"
                .to_string()
        }
    }
}

// ---------------------------------------------------------------------------
// Tauri コマンド
// ---------------------------------------------------------------------------

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

/// フック（キーボード監視）が有効かどうかを返す。
/// 両プラットフォーム共通: HOOK_ACTIVE フラグで実際のフック状態を確認。
/// Windows: SetWindowsHookExW 成功時に true。フック無効化時に false → 自動復旧。
/// macOS: CGEventTap インストール成功時に true。権限未付与時は false。
#[tauri::command]
fn get_hook_status() -> bool {
    crate::input::hook::HOOK_ACTIVE.load(std::sync::atomic::Ordering::Relaxed)
}

#[tauri::command]
fn get_cognitive_state(state: State<CognitiveStateEngine>) -> HashMap<String, f64> {
    let probs = state.get_current_state();
    let mut map = HashMap::new();
    for (k, v) in probs {
        let key_str = match k {
            CognitiveState::Flow => "flow",
            CognitiveState::Incubation => "incubation",
            CognitiveState::Stuck => "stuck",
        };
        map.insert(key_str.to_string(), v);
    }
    map
}

/// デバッグ専用コマンドのバックエンド側ゲート (defense-in-depth・cross-review 両者一致指摘)。
/// フロントの `VITE_GSE_DEBUG` 表示 gate に加え、ランタイム env `GSE_DEBUG=1` を要求する。
/// 被験者が DevTools から直接 invoke しても env 未設定なら拒否され、実験ログ汚染を防ぐ。
/// `VITE_GSE_DEBUG` はビルド時フロント env で Rust からは読めないため、研究者はスモーク時に
/// `GSE_DEBUG=1` も設定する (二重 gate)。Err で返すため DevTools に拒否理由が表示される。
fn ensure_debug_enabled() -> Result<(), String> {
    match std::env::var("GSE_DEBUG") {
        Ok(v) if v == "1" => Ok(()),
        _ => Err("debug command disabled (set GSE_DEBUG=1 to enable)".to_string()),
    }
}

/// デバッグ用: 次回の `get_intervention_decision` (overlay) で Nudge を一度だけ強制表示する。
/// nudge→dismiss→`record_intervention_dismiss` の経路を能動的に検証するため (#1 repro)。
/// ワンショットフラグ方式。Dashboard の debugView gate からのみ呼ぶ。
#[tauri::command]
fn force_nudge() -> Result<(), String> {
    ensure_debug_enabled()?;
    FORCE_NUDGE.store(true, Ordering::Release);
    Ok(())
}

/// デバッグ用: スケジューラ発火と同じ `probe_triggered`(source=random_probe) を即時 emit する。
/// card→回答/skip→`record_realtime_*` の経路を能動的に検証するため (#1 repro)。Dashboard の
/// debugView gate からのみ呼ぶ。`ProbeId::generate` で型安全に有効 ID を作る (本文混入を排除・data-privacy)。
#[tauri::command]
fn debug_force_probe(app: tauri::AppHandle) -> Result<(), String> {
    use crate::analysis::probe_scheduler::ProbeId;
    use rand::SeedableRng;

    ensure_debug_enabled()?;
    let now = epoch_ms();
    let session_start = SESSION_START_MS.load(Ordering::Acquire);
    if session_start == 0 {
        tracing::warn!("debug_force_probe called before session start (ignored)");
        return Err("session not started".to_string());
    }
    // 直近 ~30s 窓を session_start でクランプ (self_marker と同じ窓ロジック)。
    let (ws, we) = crate::analysis::probe_scheduler::self_marker_window_clamped(now, session_start);
    // デバッグ専用: now を seed に有効 ID を型安全生成。同一 ms に連打すると ID 衝突しうるが
    // debugView gate 下の動作確認用途のため実害なし。
    let mut rng = rand::rngs::StdRng::seed_from_u64(now);
    let probe_id = ProbeId::generate(&mut rng);
    app.emit(
        "probe_triggered",
        serde_json::json!({
            "probe_id": probe_id.as_str(),
            "source": "random_probe",
            "analysis_window_start_ms": ws,
            "analysis_window_end_ms": we,
        }),
    )
    .map_err(|e| format!("probe_triggered emit failed: {}", e))?;
    tracing::info!("debug_force_probe emitted at {}", now);
    Ok(())
}

/// overlay 窓の実状態 (位置/サイズ/可視性/Windows のクリック透過 ex-style)。
/// idle 残存バグ (背後アプリのクリックを奪う) を一次情報で監査するための読み取り専用 DTO。
#[derive(serde::Serialize)]
struct OverlayWindowState {
    /// outer_position (physical px)。idle 退避済みなら大きな負値 (例 -20000)。
    x: i32,
    y: i32,
    /// outer_size (physical px)。idle 退避済みなら 1x1 近辺 (OS の最小サイズに clamp されうる)。
    width: u32,
    height: u32,
    /// Tauri から見た可視フラグ。idle でも hide() しない設計 (D10) なので true のはず。
    /// None = is_visible() 取得失敗 (「非表示」と区別して監査を誤読させないため Option)。
    visible: Option<bool>,
    /// 番兵: 画面外退避済みか。Overlay.tsx の退避量 OFFSCREEN_POS(-20000) に対し余裕を持たせた
    /// -10000 を閾値にする。idle で false なら退避が効いていない (H4)。
    offscreen: bool,
    /// Windows のみ: WS_EX_TRANSPARENT (OS クリック透過) が立っているか。macOS は None。
    ex_transparent: Option<bool>,
    /// Windows のみ: WS_EX_LAYERED が立っているか。macOS は None。
    ex_layered: Option<bool>,
}

/// デバッグ用: overlay 窓の実位置/サイズ/可視性/(Windows) クリック透過 ex-style を読み返す。
/// オーバーレイ残存バグ (idle で背後アプリのクリックを奪う) を推測でなく一次情報で監査するための
/// **読み取り専用** 計装 (窓を一切変更しない)。フロント (Overlay.tsx) が各状態遷移直後に `tag` 付きで
/// 呼び、結果を tracing に出して「どの遷移後 idle で窓が画面に残るか」の状態行列を埋める。
/// `ensure_debug_enabled()` (GSE_DEBUG=1) ゲート下。被験者ビルドでは VITE_GSE_DEBUG off で呼ばれない。
#[tauri::command]
fn debug_overlay_window_state(
    app: tauri::AppHandle,
    tag: String,
) -> Result<OverlayWindowState, String> {
    ensure_debug_enabled()?;
    let win = app
        .get_webview_window("overlay")
        .ok_or_else(|| "overlay window not found".to_string())?;
    let pos = win.outer_position().map_err(|e| e.to_string())?;
    let size = win.outer_size().map_err(|e| e.to_string())?;
    // is_visible 取得失敗は None で報告する (false=非表示 と混同させない・監査の誤読防止)。
    let visible = win.is_visible().ok();

    // Windows のみ: GWL_EXSTYLE を読み返し、WS_EX_TRANSPARENT (set_ignore_cursor_events が
    // 実効したか) を確認する。#11461 で透明 WebView2 窓には効かない疑いを一次情報で検証する。
    #[cfg(windows)]
    let (ex_transparent, ex_layered) = {
        // NOTE: GetWindowLongPtrW は 64bit ターゲット限定 API (windows crate)。配布対象は x64
        // (Surface Pro 8) のため実害なし。将来 32bit ビルドが必要になれば GetWindowLongW へ分岐する。
        use windows::Win32::Foundation::HWND;
        use windows::Win32::UI::WindowsAndMessaging::{
            GetWindowLongPtrW, GWL_EXSTYLE, WS_EX_LAYERED, WS_EX_TRANSPARENT,
        };
        match win.hwnd() {
            Ok(hwnd) => {
                // バージョン橋渡し: `win.hwnd()` は Tauri が依存する windows 0.61 の HWND を返すが、
                // 本クレートが直接 import する GetWindowLongPtrW は windows 0.58 の HWND を要求する
                // (0.x の異 minor は semver 非互換で型が統一されない)。両版とも
                // `HWND(pub *mut c_void)` と同一レイアウトなので、生ポインタ経由で 0.58 HWND を
                // 構築して渡す (transmute 不要・cross-review H1 対応)。
                let hwnd058 = HWND(hwnd.0);
                // SAFETY: GetWindowLongPtrW は read-only な Win32 照会で副作用を持たない。
                // hwnd058 は Tauri 所有の有効な overlay 窓ハンドル (生ポインタ同値) で、本コマンドは
                // メインスレッドで同期実行されるため実行中に破棄されない。
                // (NOTE/H2: 透明 always_on_top layered 窓の EXSTYLE は常に非0 のため、本 debug
                //  用途では「0=失敗」と「0=フラグ無し」の曖昧さは実害なし。)
                let ex = unsafe { GetWindowLongPtrW(hwnd058, GWL_EXSTYLE) } as u32;
                (
                    Some(ex & WS_EX_TRANSPARENT.0 != 0),
                    Some(ex & WS_EX_LAYERED.0 != 0),
                )
            }
            Err(e) => {
                tracing::warn!("debug_overlay_window_state: hwnd() failed: {}", e);
                (None, None)
            }
        }
    };
    #[cfg(not(windows))]
    let (ex_transparent, ex_layered): (Option<bool>, Option<bool>) = (None, None);

    let offscreen = pos.x <= -10_000 || pos.y <= -10_000;
    tracing::info!(
        target: "overlay_audit",
        tag = %tag,
        x = pos.x,
        y = pos.y,
        w = size.width,
        h = size.height,
        visible = ?visible,
        offscreen = offscreen,
        ex_transparent = ?ex_transparent,
        ex_layered = ?ex_layered,
        "overlay_window_state"
    );
    Ok(OverlayWindowState {
        x: pos.x,
        y: pos.y,
        width: size.width,
        height: size.height,
        visible,
        offscreen,
        ex_transparent,
        ex_layered,
    })
}

/// G1 モードをフロントへ返す (fail-loud 表示用)。`None` なら通常運用。
///
/// ⚠️ ★ なぜ画面に出すのか: マーカーが外れる / アプリをフォルダの外に出す / launcher で
/// `open -a` してしまう、のいずれでも **黙って通常モードで起動する**。
/// ★ 2026-08-05 の実測では `open -a gse-next` が `/Applications` の通常アプリを起こした。
/// 実施後に `validate_blocks.py --dataset` が赤くなって初めて気づくのでは遅い
/// (`preregistration.md §3.6` がブロックの事後除外を禁じている) ため、
/// **開始する前に画面で分かる**ようにする。
#[tauri::command]
fn get_g1_mode() -> Option<String> {
    g1_mode().map(|s| s.to_string())
}

/// ログ書込先の状態をフロントへ返す (#1 層2 fail-loud)。起動時にフロントが取得し、
/// `ok=false` なら「ログがどこに / 書けていない」旨の警告バナーを常時表示する。
#[tauri::command]
fn get_log_status(status: State<'_, LogStatusState>) -> LogStatusDto {
    // ローテート後の状態を読む (共有ハンドル)。poison 時は保守的に「書けていない」を返す。
    let current = match status.0.lock() {
        Ok(t) => t.status.clone(),
        Err(_) => LogStatus::Disabled {
            error: "log target state poisoned".to_string(),
        },
    };
    match &current {
        LogStatus::Ok => LogStatusDto {
            ok: true,
            mode: "ok".to_string(),
            message: String::new(),
            actual_path: None,
        },
        LogStatus::Fallback { actual, .. } => LogStatusDto {
            ok: false,
            mode: "fallback".to_string(),
            message: "ログの保存先に書き込めなかったため一時フォルダに保存しています。\
                      データは残りますが、研究者に連絡してください。"
                .to_string(),
            actual_path: Some(actual.to_string_lossy().to_string()),
        },
        LogStatus::Disabled { .. } => LogStatusDto {
            ok: false,
            mode: "disabled".to_string(),
            message: "ログを保存できません（記録が失われます）。\
                      作業を続ける前に研究者に連絡してください。"
                .to_string(),
            actual_path: None,
        },
    }
}

#[tauri::command]
fn get_intervention_decision(
    window_label: String,
    engine: State<CognitiveStateEngine>,
    latest_feat: State<LatestFeatState>,
    intervention: State<InterventionState>,
    log: State<Arc<Mutex<LogState>>>,
) -> InterventionDecision {
    // overlay WebView は表示専用。main 側ポーリングだけが policy state を進める。
    if window_label == "overlay" {
        // デバッグ強制 Nudge。**consumer は overlay 分岐**である。
        //   - FORCE_NUDGE → overlay 分岐 (ここ) で消費。overlay が自分の poll で nudge を直接返すため
        //     main の decide() 上書きと race しない。Overlay 側が nudgeVisible を保持し持続させる。
        // どちらもワンショット (swap)・reason="debug_force" でログし解析時に除外可能。
        if FORCE_NUDGE.swap(false, Ordering::AcqRel) {
            let now = epoch_ms();
            let idle_ms = get_keyboard_idle_ms();
            let decision = {
                let guard = intervention.0.lock().unwrap_or_else(|p| p.into_inner());
                guard.force_nudge_decision(idle_ms)
            };
            let _ = log.lock().unwrap_or_else(|p| p.into_inner()).tx.try_send(
                LogEntry::InterventionDecision {
                    timestamp: now,
                    action: decision.action.as_str().to_string(),
                    need_score: decision.need_score,
                    opportunity_score: decision.opportunity_score,
                    p_stuck: decision.p_stuck,
                    idle_ms: decision.idle_ms,
                    reason: decision.reason.clone(),
                    suppressed_by: decision.suppressed_by.clone(),
                },
            );
            return decision;
        }
        return intervention
            .0
            .lock()
            .unwrap_or_else(|p| p.into_inner())
            .last_decision();
    }

    // Task C: セッションが介入無効を宣言した場合は policy を進めず none を返す。
    // 無効時は last_decision が safe_default のまま据え置かれ overlay も none を表示する
    // (較正中の介入混入を防ぐ。cross-review: 宣言と実挙動の乖離解消)。
    if !INTERVENTION_ENABLED.load(Ordering::Acquire) {
        return InterventionDecision::safe_default();
    }

    let now = epoch_ms();
    let p_stuck = engine
        .get_current_state()
        .get(&CognitiveState::Stuck)
        .copied()
        .unwrap_or(0.0);
    let idle_ms = get_keyboard_idle_ms();
    let latest = latest_feat
        .0
        .lock()
        .unwrap_or_else(|p| p.into_inner())
        .clone();
    let (f3, f4, f6) = latest
        .map(|f| (f.f3, f.f4, f.f6))
        .unwrap_or((0.0, 0.0, 0.0));

    let input = InterventionInput {
        now_ms: now,
        p_stuck,
        f3_correction_rate: f3,
        f4_burst_length: f4,
        f6_pause_after_del_rate: f6,
        idle_ms,
    };

    let mut guard = intervention.0.lock().unwrap_or_else(|p| p.into_inner());
    let result = guard.decide(input);
    if result.should_log {
        let _ = log.lock().unwrap_or_else(|p| p.into_inner()).tx.try_send(
            LogEntry::InterventionDecision {
                timestamp: now,
                action: result.decision.action.as_str().to_string(),
                need_score: result.decision.need_score,
                opportunity_score: result.decision.opportunity_score,
                p_stuck: result.decision.p_stuck,
                idle_ms: result.decision.idle_ms,
                reason: result.decision.reason.clone(),
                suppressed_by: result.decision.suppressed_by.clone(),
            },
        );
    }
    result.decision
}

#[tauri::command]
fn record_intervention_dismiss(
    action: String,
    reason: Option<String>,
    intervention: State<InterventionState>,
    log: State<Arc<Mutex<LogState>>>,
) -> Result<(), String> {
    let parsed_action = InterventionAction::parse(&action)
        .ok_or_else(|| format!("invalid intervention action: {:?}", action))?;
    let now = epoch_ms();
    // 既存: 介入抑制 (cooldown / recent_dismiss) のためメモリ状態を更新する。
    intervention
        .0
        .lock()
        .unwrap_or_else(|p| p.into_inner())
        .record_dismiss(parsed_action, now);
    // 追加 (WBS 0.8 / v0.4 §9): ユーザー応答側を NDJSON へ固定カテゴリで残す。
    // 理由は省略可 (フェード/無選択 = silent)。未知値はエラーにして黙って捨てない。
    let reason = parse_dismiss_reason(reason.as_deref())?;
    log.lock()
        .unwrap_or_else(|p| p.into_inner())
        .tx
        .try_send(LogEntry::InterventionResponse {
            timestamp: now,
            action: parsed_action.as_str().to_string(),
            reason,
            // Nudge dismiss は経過時間を持たない (elapsed_ms は埋めない)。
            elapsed_ms: None,
        })
        .map_err(log_send_error)?;
    Ok(())
}

/// 最後のキー押下からの経過ミリ秒を返す (Dashboard キーボードアクティビティ表示用)
/// キーが一度も押されていない場合は 0 を返す。
#[tauri::command]
fn get_keyboard_idle_ms() -> u64 {
    let last = crate::input::hook::last_key_ms();
    if last == 0 {
        return 0;
    }
    let now_ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    now_ms.saturating_sub(last)
}

/// 最後のキー押下時刻を UNIX エポックミリ秒で返す (advice.md §D)
/// JS 側で Date.now() - idle_ms として逆算するより精度が高い。
/// キーが一度も押されていない場合は 0 を返す。
#[tauri::command]
fn get_last_keypress_timestamp() -> u64 {
    crate::input::hook::last_key_ms()
}

fn epoch_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}

/// 診断情報を返す (バグ報告・トラブルシューティング用)
/// hook_active, last_key_ms, OS, arch, version を含む。
#[tauri::command]
fn get_diagnostics() -> HashMap<String, String> {
    let mut diag = HashMap::new();
    diag.insert(
        "hook_active".into(),
        crate::input::hook::HOOK_ACTIVE
            .load(Ordering::Relaxed)
            .to_string(),
    );
    diag.insert(
        "last_key_ms".into(),
        crate::input::hook::last_key_ms().to_string(),
    );
    // ⚠️★★ 「設置できた」(`hook_active`) と「届いている」(`!hook_starved`) は別概念である
    //   (`input::liveness`)。★ 研究者向けの診断には**両方**出す。
    //   ⚠️★★★ **旧注記を訂正した (2026-08-28)。** 旧文は
    //   「`get_hook_status`（= 被験者の画面のバナー）は意図的に変えていない」と書いていたが、
    //   ★ `get_hook_status` は `HOOK_ACTIVE` しか読んでいない (定義を見よ)。
    //   ⚠️ 実際に被験者の画面を作っているのは **`get_recording_status` → `recording_health`**
    //   であり、そちらは `HOOK_STARVED` を読む。
    //   → ★ 「被験者に見せるもの」(`HOOK_STARVED`) と「研究者が見るもの」
    //     (`HOOK_NOT_DELIVERING`) を**別の旗**に分けてある。
    // ⚠️★★ **生の判定を出す** (`HOOK_NOT_DELIVERING`)。★ `HOOK_STARVED` は 2026-08-28 から
    //   「被験者に見せるか」を持つ旗になり、O1 では 30 分まで false のままなので、
    //   ⚠️ そちらを出すと**この診断の意味が O1 のあいだだけ変わる** (判断 D-6 に反する)。
    diag.insert(
        "hook_starved".into(),
        crate::input::hook::HOOK_NOT_DELIVERING
            .load(Ordering::Relaxed)
            .to_string(),
    );
    // ★ 参考: **被験者に見えている状態**。⚠️ 通常運用 / G1 では上と必ず一致し、
    //   O1 でだけ「まだ見せていない」区間が出る (★ 研究者が両方を突き合わせられるようにする)。
    diag.insert(
        "hook_starved_shown".into(),
        crate::input::hook::HOOK_STARVED
            .load(Ordering::Relaxed)
            .to_string(),
    );
    // ★ 2026-08-09 以降は Windows でも加算されるので、macOS 限定の節から出した。
    diag.insert(
        "callback_count".into(),
        crate::input::hook::CALLBACK_COUNT
            .load(Ordering::Relaxed)
            .to_string(),
    );
    diag.insert("os".into(), std::env::consts::OS.to_string());
    diag.insert("arch".into(), std::env::consts::ARCH.to_string());
    diag.insert("version".into(), env!("CARGO_PKG_VERSION").to_string());
    // macOS: Input Monitoring / Accessibility 権限の TCC 状態を診断に含める。
    // CGPreflightListenEventAccess() が true でも CGEventTap が動作しない場合、
    // コード署名と TCC データベースの不一致が原因と判断できる。
    #[cfg(target_os = "macos")]
    {
        #[link(name = "ApplicationServices", kind = "framework")]
        extern "C" {
            fn CGPreflightListenEventAccess() -> bool;
            fn AXIsProcessTrusted() -> bool;
        }
        // SAFETY: CGPreflightListenEventAccess / AXIsProcessTrusted は
        // pure read-only の TCC チェック。メモリ安全性への影響なし。
        let preflight = unsafe { CGPreflightListenEventAccess() };
        let ax_trusted = unsafe { AXIsProcessTrusted() };

        diag.insert("input_monitoring_granted".into(), preflight.to_string());
        diag.insert("ax_is_trusted".into(), ax_trusted.to_string());
        // ★ `callback_count` は両 OS 共通の節へ移した (上記)。
        diag.insert(
            "consecutive_tap_failures".into(),
            crate::input::hook::CONSECUTIVE_TAP_FAILURES
                .load(Ordering::Relaxed)
                .to_string(),
        );
        diag.insert(
            "using_accessibility_fallback".into(),
            crate::input::hook::USING_ACCESSIBILITY_FALLBACK
                .load(Ordering::Relaxed)
                .to_string(),
        );

        // current_exe() を1回だけ呼び出して再利用する
        if let Ok(exe) = std::env::current_exe() {
            // バンドルパス: .app まで遡って報告
            let bundle_path = exe
                .ancestors()
                .find(|p| p.extension().is_some_and(|e| e == "app"))
                .map(|p| p.to_string_lossy().to_string())
                .unwrap_or_else(|| exe.to_string_lossy().to_string());
            diag.insert("bundle_path".into(), bundle_path);

            // quarantine xattr の有無
            if let Some(app_path) = exe
                .ancestors()
                .find(|p| p.extension().is_some_and(|e| e == "app"))
            {
                let has_quarantine = std::process::Command::new("xattr")
                    .args(["-p", "com.apple.quarantine"])
                    .arg(app_path)
                    .output()
                    .map(|o| o.status.success())
                    .unwrap_or(false);
                diag.insert("quarantine_present".into(), has_quarantine.to_string());
            }

            // コード署名の有効性
            let codesign_ok = std::process::Command::new("codesign")
                .args(["--verify", "--strict"])
                .arg(&exe)
                .output()
                .map(|o| o.status.success())
                .unwrap_or(false);
            diag.insert("codesign_valid".into(), codesign_ok.to_string());
        }
    }
    diag
}

/// macOS: Input Monitoring の TCC エントリをリセットし、System Settings を再度開く。
/// ユーザーが権限を付与しても CGEventTap が作成できない場合の最終手段。
/// tccutil reset ListenEvent は全アプリの Input Monitoring をリセットする点に注意。
#[cfg(target_os = "macos")]
#[tauri::command]
fn reset_input_monitoring() -> String {
    #[link(name = "ApplicationServices", kind = "framework")]
    extern "C" {
        fn CGRequestListenEventAccess() -> bool;
    }

    let output = std::process::Command::new("tccutil")
        .args(["reset", "ListenEvent"])
        .output();

    match output {
        Ok(o) if o.status.success() => {
            tracing::info!("TCC ListenEvent reset successful, re-requesting permission...");
            // SAFETY: CGRequestListenEventAccess は副作用として System Settings ダイアログを
            // 表示するのみ。メモリ安全性への影響なし。
            unsafe {
                CGRequestListenEventAccess();
            }
            "TCC reset successful. System Settings should open.".into()
        }
        Ok(o) => {
            let stderr = String::from_utf8_lossy(&o.stderr).to_string();
            tracing::warn!("tccutil failed (exit={}): {}", o.status, stderr);
            "TCC reset failed. Try running in Terminal: tccutil reset ListenEvent".into()
        }
        Err(e) => {
            tracing::error!("Failed to run tccutil: {}", e);
            format!("Failed to run tccutil: {}", e)
        }
    }
}

/// Windows: reset_input_monitoring のスタブ（no-op）。
#[cfg(not(target_os = "macos"))]
#[tauri::command]
fn reset_input_monitoring() -> String {
    "Not applicable on this platform".into()
}

/// macOS: Accessibility の TCC エントリをリセットする。
/// Accessibility フォールバックモードで権限付与が失敗した場合の回復手段。
/// tccutil reset Accessibility は全アプリの Accessibility をリセットする点に注意。
#[cfg(target_os = "macos")]
#[tauri::command]
fn reset_accessibility() -> String {
    let output = std::process::Command::new("tccutil")
        .args(["reset", "Accessibility"])
        .output();

    match output {
        Ok(o) if o.status.success() => {
            tracing::info!("TCC Accessibility reset successful");
            "TCC Accessibility reset successful. The app will re-prompt for permission.".into()
        }
        Ok(o) => {
            let stderr = String::from_utf8_lossy(&o.stderr).to_string();
            tracing::warn!(
                "tccutil Accessibility reset failed (exit={}): {}",
                o.status,
                stderr
            );
            "TCC Accessibility reset failed. Try: tccutil reset Accessibility".into()
        }
        Err(e) => {
            tracing::error!("Failed to run tccutil: {}", e);
            format!("Failed to run tccutil: {}", e)
        }
    }
}

/// Windows: reset_accessibility のスタブ（no-op）。
#[cfg(not(target_os = "macos"))]
#[tauri::command]
fn reset_accessibility() -> String {
    "Not applicable on this platform".into()
}

/// macOS: System Settings の Accessibility ペインを直接開く。
/// ad-hoc 署名ではプログラムによる権限プロンプトが動作しないため、
/// ユーザーに手動で「+」ボタンからアプリを追加してもらう。
#[cfg(target_os = "macos")]
#[tauri::command]
fn open_accessibility_settings() -> String {
    match std::process::Command::new("open")
        .arg("x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility")
        .spawn()
    {
        Ok(_) => "System Settings opened.".into(),
        Err(e) => {
            tracing::warn!("Failed to open System Settings: {}", e);
            format!("Failed to open: {}", e)
        }
    }
}

/// Windows: open_accessibility_settings のスタブ（no-op）。
#[cfg(not(target_os = "macos"))]
#[tauri::command]
fn open_accessibility_settings() -> String {
    "Not applicable on this platform".into()
}

/// 現在のセッションログファイルのパスを返す (UI表示用)
#[tauri::command]
fn get_session_file(log: State<Arc<Mutex<LogState>>>) -> String {
    log.lock().unwrap_or_else(|p| p.into_inner()).current_path()
}

// --- ⚠️★★★ 研究者向け: `ime_shadow` の生存読み出し ------------------------------
//
// ★ **なぜ要るか** (2026-09-11):
//   `ime_shadow` は `gse-replay` が**読み飛ばす**ので (`bin/replay.rs`)、
//   ★ 実機での確認手段が **NDJSON を jq で開くことだけ**だった。
//   ⚠️ しかも NDJSON は **1 セッションで 2 本できる** (起動時に 1 本 → 「開始する」で
//   ローテート) ので、**取り違えやすい**。
//   → ★ 「**いまどのファイルに何行書けているか**」を画面で見られるようにする。
//
// ⚠️★★★ **被験者には出さない。** 二重ゲート:
//   1. backend: `ensure_debug_enabled()` (= `GSE_DEBUG=1`) が無ければ `Err`
//   2. frontend: `Dashboard.tsx` の `debugView` (= `VITE_GSE_DEBUG=1`) で囲む
//   ⚠️ **`get_diagnostics` には足さない** —— あの診断パネルは `debugView` で囲まれておらず、
//   フックが 20 秒以上有効にならないと**被験者にも出る**。★ 放棄回数を被験者に見せない。

/// 研究者向けデバッグ読み出し DTO。
///
/// ⚠️ **キーストローク内容は一切含まない** —— ★ 入っているのは
/// **ファイルパス**と**件数 3 つ**だけである (data-privacy CD1)。
// ⚠️ `Clone` は付けない —— ★ 値で構築して即返すだけで、state に保持しない。
#[derive(serde::Serialize)]
struct ImeShadowDebugDto {
    /// いま書いている NDJSON の絶対パス (⚠️ ローテート追随)。
    log_path: String,
    /// ★ **`log_path` のファイルに書かれた** `ime_shadow` 行の数
    /// (⚠️ ローテートで 0 に戻る。プロセス累計ではない)。
    emitted: u64,
    /// そのうち `abandon = false` (= Enter / その他キーによる確定)。
    confirmed: u64,
    /// そのうち `abandon = true` (= ESC による放棄)。
    abandoned: u64,
}

/// ⚠️★★★ 研究者向け: `ime_shadow` の生存状況を返す (`GSE_DEBUG=1` 必須)。
///
/// ★ `confirmed` は `emitted - abandoned` で**導出する** (別カウンタを持たない) ——
/// ⚠️ 3 つを別々に増やすと、読み出しが途中に挟まったときに**和が合わない**。
/// ★ 件数は **`log_path` が指すファイルに実際に書かれた行数**である
/// (⚠️ ローテートで 0 に戻る。`logger::tally_ime_shadow` の doc が正本)。
/// ★ `saturating_sub` は**保険**であって根拠ではない ——
/// 根拠は `logger::ime_shadow_tally` が固定する読み書きの順序のほうにある。
#[tauri::command]
fn get_ime_shadow_debug(log: State<Arc<Mutex<LogState>>>) -> Result<ImeShadowDebugDto, String> {
    ensure_debug_enabled()?;
    // ★ 読み出しの順序は `logger::ime_shadow_tally` が持つ (⚠️ あちらの doc が正本)。
    let (emitted, abandoned) = logger::ime_shadow_tally();
    Ok(ImeShadowDebugDto {
        log_path: log.lock().unwrap_or_else(|p| p.into_inner()).current_path(),
        emitted,
        confirmed: emitted.saturating_sub(abandoned),
        abandoned,
    })
}

// --- O1 (R3): 被験者の 3 点セット (ADR-014 D7) ---------------------------------------
//
// ⚠️★★★ **この 3 つが揃っていることが、ADR-014 判断 3（倫理審査は不要）の根拠 3 である。**
// 逐語「⚠️ **削除 UI が実装されないまま収集を始めた時点で崩れる**」。
//
// | # | 要件 | ★ ここでの実装 |
// |---|---|---|
// | i | 稼働中インジケータ | [`get_recording_status`]（Frontend が常時ポーリングして表示） |
// | ii | 即時の一時停止 | [`set_recording_paused`] |
// | iii | 事後の区間指定削除 | [`delete_time_range`]（⚠️ **理由を引数に取らない**） |

/// 稼働中インジケータ (D7-i) が表示するもの。
#[derive(serde::Serialize)]
struct RecordingStatusDto {
    /// ⚠️ いま**一時停止中**か。★ `false` なら記録している。
    paused: bool,
    /// いま書いているセッションファイル (UI が「これは消せない」と示すために使う)。
    current_file: String,
    /// セッション NDJSON を置いているディレクトリ。
    session_dir: String,
    /// ★ O1 モードの引き金 (`"marker"` / `"env"`)。⚠️ 通常運用では `None`。
    o1_mode: Option<&'static str>,
    /// ⚠️★★★ **いま宣言されている作業の種類** (`None` = **未宣言**)。
    ///
    /// ★ ADR-016 判断 4b-3: `unknown` を enum に足さず、**`session_meta` 行の *不在*** で
    /// 未宣言を表す。→ ここも `None` のままにし、⚠️ **UI が「未設定」と描く**。
    /// ★ こちらで勝手に推測して埋めない (同意文書 §2 の逐語)。
    task_kind: Option<&'static str>,
    /// ⚠️★★★ **実際に記録できているか** (研究者判断 R-11・2026-08-26)。
    ///
    /// ★ 旧実装は `paused` だけを見ており、⚠️ **フックが死んでいても
    /// 「記録しています」と出した** (security-checker MEDIUM-2)。
    /// ★ トレイ (`tray::current_state`) は見ているのに**アプリ内バッジだけが見ていなかった**。
    /// → ★ 同意文書 §4 の逐語「印が出ていないときは記録していません」を守るには、
    /// **「止めた」と「壊れている」を分けて出す**必要がある (トレイの `MeasureState` と同じ理屈)。
    ///
    /// | 値 | 意味 |
    /// |---|---|
    /// | `"recording"` | ★ 記録できている |
    /// | `"paused"` | ★ 被験者が止めている |
    /// | `"broken"` | ⚠️★★★ **止めていないのに記録できていない** (フックの死 / 書込不可) |
    health: &'static str,
    /// ⚠️ `health == "broken"` のとき、**何が壊れているか**を被験者に出す 1 行。
    health_detail: Option<String>,
}

/// 記録の稼働状態を返す (D7-i: 稼働中インジケータ)。
///
/// ⚠️★★★ **Frontend で判定しない。** `typescript-standards` / `architecture-rules` ルール 3 に従い、
/// 「記録しているか」の判断は Rust 側が持ち、UI は受け取った真偽値を描くだけにする。
#[tauri::command]
fn get_recording_status(log: State<Arc<Mutex<LogState>>>) -> RecordingStatusDto {
    let (dir, _participant_id) = crate::logger::session_log_dir();
    let paused = crate::recording::is_paused();
    // ⚠️★★★ **「止めた」と「壊れている」を分ける** (R-11)。★ 材料はトレイと同じ 3 つ:
    //   `HOOK_ACTIVE` (設置できたか) / `!HOOK_STARVED` (実際に届いているか) /
    //   `LogStatus` (書けているか)。
    // ★ ロックは 1 回だけ取る (⚠️ 2 回取ると、その間のローテートでパスと状態が食い違う)。
    let (current_file, log_ok) = {
        let guard = log.lock().unwrap_or_else(|p| p.into_inner());
        (guard.current_path(), guard.status())
    };
    let (health, health_detail) = recording_health(
        paused,
        crate::input::hook::HOOK_ACTIVE.load(Ordering::Relaxed),
        crate::input::hook::HOOK_STARVED.load(Ordering::Relaxed),
        log_ok,
    );
    RecordingStatusDto {
        paused,
        current_file,
        session_dir: dir.display().to_string(),
        o1_mode: crate::o1::mode().map(|s| s.as_str()),
        task_kind: declared_task_kind().map(|k| k.as_str()),
        health,
        health_detail,
    }
}

/// 稼働中インジケータの 3 値を決める**純関数** (R-11)。
///
/// ⚠️★★★ **順序が意味を持つ**: ★ 「被験者が止めた」が最優先である ——
/// 止めているあいだフックが遊んでいるのは**当たり前**なので、
/// ⚠️ そこで「壊れています」と出すと**被験者が自分の操作を故障と誤解する**。
///
/// ★ `installed && !starved` はトレイの `current_state` と**同じ式**である
/// (⚠️ 2 か所で違う式を書くと、片方だけ直して静かに食い違う)。
fn recording_health(
    paused: bool,
    hook_installed: bool,
    hook_starved: bool,
    log_ok: bool,
) -> (&'static str, Option<String>) {
    if paused {
        return ("paused", None);
    }
    if !log_ok {
        return (
            "broken",
            Some("記録の保存先に書き込めていません。研究者に連絡してください。".to_string()),
        );
    }
    if !hook_installed || hook_starved {
        return (
            "broken",
            Some("キーボードの記録ができていません。研究者に連絡してください。".to_string()),
        );
    }
    ("recording", None)
}

/// O1 モードか (引き金つき)。★ `get_g1_mode` の鏡像。通常運用では `None`。
#[tauri::command]
fn get_o1_mode() -> Option<&'static str> {
    crate::o1::mode().map(|s| s.as_str())
}

/// ⚠️★★★ O1 の**開始前ゲート**の状態 (研究者判断 R-7)。
#[derive(serde::Serialize)]
struct O1EnrollmentDto {
    /// ★ 1 回きりの同意確認が済んでいるか。
    consent_acknowledged: bool,
    /// ★ O1 専用の参加者 ID (未登録なら `None`)。
    participant_id: Option<String>,
}

/// O1 の開始前ゲートを読む。
#[tauri::command]
fn get_o1_enrollment() -> O1EnrollmentDto {
    O1EnrollmentDto {
        consent_acknowledged: crate::submission::o1_consent_acknowledged(),
        participant_id: crate::submission::read_o1_participant_id(),
    }
}

/// ⚠️★★★ O1 の**同意確認と参加者 ID を 1 アクションで登録する** (研究者判断 R-7)。
///
/// ★ 被験者が押すのは**この 1 回だけ**である。⚠️ 以後は再確認しない
/// (同意文書 §5 の逐語「**自動的に**送ります」を守るため)。
///
/// ⚠️ **ID が妥当でなければ確認も記録しない** (fail-closed) —— ★ 「確認は済んだが
/// ID が無いので送られない」という**中途半端な状態を作らない**。
#[tauri::command]
fn acknowledge_o1_enrollment(participant_id: String) -> Result<(), String> {
    if !crate::o1::is_o1() {
        return Err("この画面はこの記録では使いません。".to_string());
    }
    // ★ 先に ID を検証して保存する (⚠️ 失敗したら確認の印を置かない)。
    crate::submission::write_o1_participant_id(&participant_id)?;
    crate::submission::write_o1_consent_ack(epoch_ms())?;
    tracing::info!("O1: enrollment acknowledged (participant id registered)");
    Ok(())
}

/// ⚠️★★★ O1 の**ローテート 1 回**を実行する (宣言の変更 / 日次ローテートの共通経路)。
///
/// ★ ADR-016 **判断 4b-1** が要求する 3 点を **1 アクションで**行う:
/// **`session_meta` 出力 → ログのローテート → `engine.reset()`**。
///
/// ## ⚠️★★★ 順序が意味を持つ (★ 3 つとも実測に基づく)
///
/// 1. **`Rotate` を先に送る。** ⚠️ 先に `SessionMeta` を書くと、宣言が**旧ファイル**に落ちて
///    新ファイルが未宣言になる —— ★ 意味が逆になる (旧ファイルの大半はその宣言ではない)。
/// 2. **`engine.reset()` は `set_domain` より前。** ⚠️ `reset()` は逐語
///    「head も既定 (Writing) に戻す」(`analysis/engine.rs`) ので、
///    ★ 後に呼ぶと**宣言した head が黙って取り消される**。
/// 3. **`set_domain` はログ送信に成功した後。** ★ 送信に失敗したまま head だけ切り替わると
///    「Coding head で採点された `feat` 行が、head 宣言の無いファイルに書かれる」状態になり、
///    ⚠️ **本番とリプレイの採点が食い違う** (= Replay-as-Truth の破れ・security-checker 2026-08-18)。
///
/// `task_kind` が `None` (= 未宣言) のときは **`session_meta` を 1 行も書かない**
/// (★ 判断 4b-3: 行の**不在**で未宣言を表す)。
fn o1_rotate(
    log: &Arc<Mutex<LogState>>,
    engine: &CognitiveStateEngine,
    reset_signal: &ResetSignal,
    declaration: O1Declaration,
    reason: &str,
) -> Result<(), String> {
    // ⚠️★★★ **一時停止中は 1 バイトも書かない** (同意文書 §4 の逐語「すぐ止める」)。
    //
    // ★ `Rotate` は制御エントリなので停止ゲートを**通る**が、`SessionMeta` は
    //   `recording::is_writable_while_paused` が**落とす** (`recording.rs`)。
    //   → ⚠️ そのまま進むと **`head_id` がファイルに 1 行も残らないまま head だけ切り替わり**、
    //   再開後の `feat` 行は宣言 head で採点されるのにファイルは無宣言になる
    //   ＝ ★ **本番とリプレイの採点が食い違う** (本関数が防ごうとしている当の破れ)。
    //   ⚠️ UI も「作業の種類: ○○」と出したままログは未宣言になる。
    // → ★ **止めているあいだはローテートしない。** 日次ローテートは次の tick で再試行され、
    //   宣言はエラーとして被験者に返す (⚠️ 黙って落とさない)。
    if crate::recording::is_paused() {
        return Err(
            "記録を止めているあいだは変更できません。「記録を再開する」を押してからお試しください。"
                .to_string(),
        );
    }

    // ⚠️★★★ **ローテートは丸ごと 1 本に直列化する** (code-reviewer MEDIUM・2026-08-27)。
    //   ★ 入口は 2 つある —— 宣言 UI (`declare_task_kind`) と日次ローテートスレッド。
    //   ⚠️ ログのロックだけでは足りない: `DECLARED_TASK_KIND` の読みと
    //   `O1_LOG_OPENED_MS` の更新がその外にあると、交錯したときに
    //   **ファイルに書かれた `session_meta` と UI / engine head が食い違う**。
    let _serialize = O1_ROTATE.lock().unwrap_or_else(|p| p.into_inner());

    let new_path = logger::next_session_path();
    let now = epoch_ms();

    let guard = log.lock().unwrap_or_else(|p| p.into_inner());
    // ⚠️★★ **容量を先に見る** (`start_session` と同じ形)。`Rotate` だけが落ちると、
    //   直後の `SessionMeta` が **既に `session_end` を書き終えた旧ファイル**に積まれる。
    //   ★ 沈黙して間違った結果を出すのが最悪なので、到達したら必ず止める。
    if !log_channel_has_room(&guard.tx, 2) {
        tracing::error!("O1: log channel is full; refusing to rotate ({reason})");
        return Err(
            "ログの書き込みが詰まっています。少し待ってからもう一度お試しください。".to_string(),
        );
    }

    // ★ **宣言の読みもロックの中で行う。** ⚠️ 外で読むと、日次スレッドが「未宣言」を
    //   読んだ直後に宣言が入り、**宣言したばかりのファイルを未宣言として閉じ直す**。
    let mut declared = DECLARED_TASK_KIND.lock().unwrap_or_else(|p| p.into_inner());
    let kind = match declaration {
        O1Declaration::Set(k) => Some(k),
        // ⚠️★★★ **宣言を捏造しない。** 未宣言のまま日をまたいだファイルには書かない
        //   (判断 4b-3: 行の**不在**で未宣言を表す)。
        O1Declaration::KeepCurrent => *declared,
    };

    tracing::info!("O1: rotating session log ({reason}) -> {:?}", new_path);
    guard
        .tx
        .try_send(LogEntry::Rotate { new_path })
        .map_err(log_send_error)?;

    // ⚠️★★ **ローテートはここで成立している。** ★ 基準を先に引き直す ——
    //   引き直さないと、下の `SessionMeta` が落ちたときに日次スレッドが 60 秒ごとに
    //   再試行し、⚠️ **失敗のたびに新しい NDJSON が増える** (ロガーが詰まっている、
    //   つまり最も再現しやすい状況で churn する・code-reviewer HIGH)。
    O1_LOG_OPENED_MS.store(now, Ordering::Release);

    // ★ ここから新しいファイルである。⚠️ **reset は `set_domain` より前** (上記 2)。
    engine.reset();
    reset_signal.0.store(true, Ordering::Release);

    if let Some(k) = kind {
        let domain = TaskDomain::from(k);
        let head_id = domain.head_id();
        if let Err(e) = guard.tx.try_send(LogEntry::SessionMeta {
            timestamp: now,
            track: Track::Main,
            task_kind: k,
            // ⚠️★★★ **判断 O1-5: O1 では介入を出さない。** ★ ここを引数にしない
            //   (フロントから `true` を渡せる形にすると、自然作業に介入が混ざる経路ができる)。
            intervention_enabled: false,
            condition: None,
            label_pool: None,
            head_id,
        }) {
            // ⚠️★★★ **宣言を「無し」に巻き戻す** (code-reviewer HIGH・2026-08-27)。
            //   ★ 新しいファイルの**真の状態は未宣言**である。巻き戻さないと
            //   `get_recording_status` が「宣言済み」と嘘をつき、⚠️ **翌日のローテートが
            //   被験者の選んでいない種別を新ファイルに書く**。
            //   ★ engine の head は `reset()` で既に Writing へ戻っており、ここでは
            //   `set_domain` を**呼ばない**ので、ログと engine の状態は一致したままである。
            *declared = None;
            tracing::error!(
                "O1: rotated but FAILED to record the declaration: {}",
                log_send_error(e)
            );
            return Err("作業の種類を記録できませんでした。もう一度選んでください。".to_string());
        }
        // ★ 送信に成功した**後**に head を差し替える (上記 3)。
        let applied = engine.set_domain(domain);
        debug_assert_eq!(
            applied, head_id,
            "記録した head_id と反映した head が食い違った"
        );
    }

    // ★ ログへ積めた後に**初めて**宣言を確定させる (⚠️ ロックの中なので交錯しない)。
    if let O1Declaration::Set(k) = declaration {
        *declared = Some(k);
    }
    Ok(())
}

/// ⚠️★★★ O1: **作業の種類を宣言する / 宣言し直す** (ADR-016 判断 4 / 4b-1 / 4b-2 / 4b-3)。
///
/// ★ 同意文書 §2 の逐語「作業が変わったら、そのつど選び直してください」に対応する唯一の経路。
///
/// ⚠️ **`record_session_meta` には手を触れていない** —— そちらは「開始する」押下から呼ばれる
/// Phase1 / G1 の経路であり、★ **O1 の分岐を混ぜない** (G1 / Phase1 を 1 バイトも変えない)。
#[tauri::command]
fn declare_task_kind(
    task_kind: String,
    log: State<'_, Arc<Mutex<LogState>>>,
    engine: State<'_, CognitiveStateEngine>,
    reset_signal: State<'_, ResetSignal>,
) -> Result<(), String> {
    // ⚠️ 新 enum 値は足さない (判断 4b-2)。未知値は**黙って捨てず**エラーにする。
    let kind = logger::TaskKind::parse(&task_kind)
        .ok_or_else(|| format!("invalid task_kind: {:?}", task_kind))?;

    match crate::o1::decide_declaration_action(crate::o1::is_o1(), g1_mode().is_some()) {
        crate::o1::DeclarationAction::NotO1 => {
            // ⚠️ 通常運用 / G1 では宣言 UI 自体が出ない。★ ここへ来たら呼び出し側の誤りである。
            Err("この画面は O1 モードでのみ使えます。".to_string())
        }
        crate::o1::DeclarationAction::RotateAndDeclare => {
            o1_rotate(
                &log,
                &engine,
                &reset_signal,
                O1Declaration::Set(kind),
                &format!("declaration -> {}", kind.as_str()),
            )?;
            tracing::info!("O1: task_kind declared: {}", kind.as_str());
            Ok(())
        }
    }
}

/// 記録を即時に一時停止 / 再開する (D7-ii)。★ **戻り値は適用後の状態**。
///
/// ⚠️★★★ **理由を聞かない。** ★ 同意文書 §4 の逐語「**理由を聞きません**」。
///
/// ★ 状態が**変わったときだけ** `recording_pause` 行を書く（⚠️ 連打の回数を残さない）。
/// ⚠️ 「止める」方向の行は **`set_paused` の前**に送る —— ★ 後に送ると自分自身が
/// 一時停止ゲートに落ちて、**止めた事実が記録されない**。
#[tauri::command]
fn set_recording_paused(paused: bool, log: State<Arc<Mutex<LogState>>>) -> bool {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    // ★ 先に「遷移するのか」を知る必要があるが、⚠️ 判定と適用の間に別スレッドが
    //   割り込む経路は無い (UI からの単一コマンド) ので `swap` 1 回で足りる。
    let previous = crate::recording::set_paused(paused);
    if previous != paused {
        // ⚠️ `recording_pause` は `is_writable_while_paused` が通す行種なので、
        //   ★ 停止中に送っても書かれる (再開の記録が消えない)。
        let guard = log.lock().unwrap_or_else(|p| p.into_inner());
        if let Err(e) = guard.tx.try_send(LogEntry::RecordingPause {
            timestamp: now,
            paused,
        }) {
            // ⚠️ 記録できなくても**状態は変える**。★ 被験者の「止めて」を、
            //   ログが詰まっているという内部事情で断らない。
            tracing::warn!("failed to log recording_pause transition: {e:?}");
        }
    }
    paused
}

/// 区間指定削除の結果 (D7-iii)。
#[derive(serde::Serialize)]
struct RedactionOutcomeDto {
    files_touched: usize,
    lines_removed: usize,
    /// ⚠️ 書きかけなので触らなかったファイル数 (★ ふつうは 0 か 1)。
    files_skipped: usize,
}

/// ⚠️★★★ **時間帯を指定して記録を削除する** (D7-iii)。
///
/// ★ 同意文書 §4 の逐語「**時間帯を指定して削除できます（例:「昨日の 14:00〜15:00」）。
/// ⚠️ 理由を説明する必要はありません。**」
///
/// - ⚠️ **引数に理由が無い。** ★ 追加してはならない。
/// - ⚠️ **いま書いているファイルは触らない** —— ★ 書き込み中に差し替えるとロガーの
///   `BufWriter` がすでに開いている fd へ書き続け、**削除したはずの行が復活する**。
///   → ★ UI は「先に一時停止してください」と促し、`files_skipped>0` をそのまま表示する。
/// - ★ 台帳へ「消した事実」を 1 行残す（⚠️ **何を消したかは書かない**）。
#[tauri::command]
fn delete_time_range(
    from_ms: u64,
    to_ms: u64,
    log: State<Arc<Mutex<LogState>>>,
    engine: State<'_, CognitiveStateEngine>,
    reset_signal: State<'_, ResetSignal>,
) -> Result<RedactionOutcomeDto, String> {
    if from_ms > to_ms {
        return Err("開始時刻が終了時刻より後になっています。".to_string());
    }

    // ⚠️★★★ **O1 では先に現行ファイルを閉じる** (code-reviewer / security-checker が一致して指摘)。
    //
    // ★ 下の `skip` は「いま書いているファイル」を常に除外する。Phase1 / G1 の現行ファイルは
    //   1 セッション〜5 分ぶんなので実害が小さいが、⚠️★★★ **O1 の現行ファイルは
    //   日次ローテートまで最大 24 時間ぶん**である。
    //   → ⚠️ **直近 24 時間を 1 行も消せない**。しかも `RecordingControls` は
    //   「さきに『すぐ止める』を押してください」と案内するのに、⚠️ **一時停止しても
    //   `current_path` は変わらないので消せるようにならない** (実行不能な回避策)。
    //   ★ 同意文書 §4-3 は逐語で「送られる前（＝ **その日**と、その次の 2 日ほど）…
    //   **あなたの端末の上で消えます**」と約束しており、**ADR-014 判断 3 の根拠 3 がここで崩れる**。
    //
    // → ★ **ローテートしてから消す。** 閉じた瞬間から 48 時間の猶予が始まるので、
    //   ⚠️ 提出側も安全側に倒れる (★ いま閉じたファイルはまだ包まれない)。
    // ⚠️ 失敗しても**削除は続ける** —— ★ 消せる範囲だけでも消すほうが、
    //   「消えませんでした」と返すより被験者の要求に近い (`files_skipped` で正直に出る)。
    //
    // ⚠️★ **一時停止中はローテートしない。** ★ 停止中は `session_meta` が停止ゲートに落ちるので
    //   (`recording::is_writable_while_paused`)、回すと**宣言が黙って失われる**。
    //   ★ 停止中に「いまの区間」を消したい場合は、⚠️ そもそも停止後の記録が無いので
    //   失うものは停止前の分だけであり、**再開すれば次の削除で必ず届く**。
    //   ⚠️ 画面は `files_skipped` をそのまま出すので、黙って取りこぼすことはない。
    if crate::o1::is_o1() && !crate::recording::is_paused() {
        // ⚠️★★★ **ローテートの *完了* を待つ** (cross-review / Codex MEDIUM・2026-08-27)。
        //
        // ★ `o1_rotate` は `LogEntry::Rotate` を**チャネルに積むだけ**で、実際に
        //   `session_end` を書いて新しいファイルを開くのは**ロガースレッド**である。
        //   → ⚠️ 待たずに `current_path()` を読むと、**まだ旧ファイルを指している**ので
        //   ★ **閉じたはずのファイルを `skip` に渡してしまい、消したかった当のものが残る**。
        //   ⚠️ さらに悪いことに、ロガーが旧ファイルの fd へ書いている最中に
        //   `redact_file` が置き換えると **消したはずの行が復活する**。
        //
        // ★ 待ち方: `logger` は `Rotate` の処理で
        //   `write_meta_end` → flush → 新ファイルを開く → `write_meta_start` → flush →
        //   **最後に `target.path` を更新する**。→ ★ **パスが変わったことが「完了」の証拠**である。
        let before = log.lock().unwrap_or_else(|p| p.into_inner()).current_path();
        match o1_rotate(
            &log,
            &engine,
            &reset_signal,
            O1Declaration::KeepCurrent,
            "before redaction",
        ) {
            Ok(()) => {
                // ⚠️ 無限には待たない。★ 待てなかったら `files_skipped` に出るだけで、
                //   **黙って旧ファイルを壊しに行くことはない** (安全側)。
                let deadline = std::time::Instant::now() + Duration::from_secs(5);
                loop {
                    let now_path = log.lock().unwrap_or_else(|p| p.into_inner()).current_path();
                    if now_path != before {
                        break;
                    }
                    if std::time::Instant::now() >= deadline {
                        tracing::warn!(
                            "O1: the rotation before redaction did not complete in time;                              the newest file will be skipped"
                        );
                        break;
                    }
                    thread::sleep(Duration::from_millis(20));
                }
            }
            Err(e) => {
                tracing::warn!(
                    "O1: could not close the current log before redaction ({e});                      the newest file will be skipped"
                );
            }
        }
    }

    let (dir, _participant_id) = crate::logger::session_log_dir();
    let current = log.lock().unwrap_or_else(|p| p.into_inner()).current_path();
    let current_path = PathBuf::from(&current);
    let skip = if current.is_empty() {
        None
    } else {
        Some(current_path.as_path())
    };

    let summary = crate::redaction::redact_dir(&dir, from_ms, to_ms, skip).map_err(|e| {
        tracing::error!("delete_time_range failed: {e:?}");
        "記録の削除に失敗しました。".to_string()
    })?;

    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    if let Err(e) = crate::redaction::append_ledger(&dir, now, from_ms, to_ms, &summary) {
        // ⚠️ 台帳が書けなくても**削除は成功している**。★ 削除を失敗扱いにして
        //   「消えていないのでは」と被験者に思わせない。
        tracing::warn!("failed to append redaction ledger: {e:?}");
    }
    tracing::info!(
        files_touched = summary.files_touched,
        lines_removed = summary.lines_removed,
        files_skipped = summary.files_skipped,
        "delete_time_range completed"
    );
    Ok(RedactionOutcomeDto {
        files_touched: summary.files_touched,
        lines_removed: summary.lines_removed,
        files_skipped: summary.files_skipped,
    })
}

// --- アプリ内提出 (案A sidecar / mac Gatekeeper 根絶) -------------------------------
//
// 被験者が既に Gatekeeper 承認済みの GSE アプリから「提出する」を押すと、同梱 `gse-submit`
// を **子プロセス**として起動して最新セッションを匿名化 + age 暗号化する。親アプリが exec した
// 子プロセスは Gatekeeper に再評価されない (バンドル内バイナリは app の信頼を継承) ため、
// 別 exe/別スクリプトの `com.apple.quarantine` 発火を根絶する。`age` 依存は `gse-submit`
// (feature = "package") 側に閉じ、本コマンドは subprocess 起動のみで `age` を link しない
// (隔離方針 D3 を維持・default の Tauri ビルドに載る)。匿名化 + 暗号化ロジックは
// `packaging.rs` を `gse-submit` 経由で再利用し、重複実装しない。

/// アプリ内提出の結果 (frontend へ返す DTO)。`ok=false` は `Err` 経由で返すため通常 true。
#[derive(serde::Serialize)]
struct SubmitOutcome {
    /// 生成された `.age` 提出物の絶対パス (stdout から抽出できた場合)。UI が保存先として表示する。
    out_path: Option<String>,
}

/// gse-submit の stdout から生成 `.age` の絶対パスを抽出する (best-effort)。
/// submit.rs (`gse-submit`) は「提出ファイルの場所:」の次行にインデント付きでパスを出す
/// (`src/bin/submit.rs` の成功時 stdout)。書式変更に頑健にするため `.age` で終わる行を拾う。
fn extract_age_path(stdout: &str) -> Option<String> {
    stdout
        .lines()
        .map(str::trim)
        .find(|l| !l.is_empty() && l.ends_with(".age"))
        .map(|l| l.to_string())
}

/// 同梱された研究者公開鍵 (`pubkey.txt` / `recipient.txt`) を bundle resource から解決する。
/// 見つかれば `GSE_RECIPIENT` に渡す絶対パスを返す。見つからなければ `None` (この場合
/// gse-submit は exe 隣の鍵探索にフォールバックし、無ければ案内付きで fail-loud)。
fn resolve_bundled_recipient(app: &tauri::AppHandle) -> Option<String> {
    let resource_dir = app.path().resource_dir().ok()?;
    // resources の配置形式 (フラット / resources/ サブディレクトリ) の差異に頑健にするため
    // 複数候補を探す。
    for sub in ["", "resources"] {
        let base = if sub.is_empty() {
            resource_dir.clone()
        } else {
            resource_dir.join(sub)
        };
        for name in ["pubkey.txt", "recipient.txt"] {
            let p = base.join(name);
            if p.is_file() {
                return Some(p.to_string_lossy().into_owned());
            }
        }
    }
    None
}

/// `gse-submit` を子プロセスとして実行する (ブロッキング)。`submit_latest_session` から
/// `spawn_blocking` 経由で呼ばれ、メインスレッド/イベントループを塞がない。
/// binary 解決 → env 設定 (`GSE_PARTICIPANT_ID` / `GSE_RECIPIENT`) → 実行 → 結果解釈までを行う。
/// 同梱 `gse-submit` の絶対パス (current_exe の隣)。
/// mac=`.app/Contents/MacOS/gse-submit` (リリースで同梱済)、
/// win=`gse-next.exe` と同階層 `gse-submit.exe` (ポータブル配布フォルダに co-located)。
///
/// ★ 手動提出と自動提出 (収束器) の**両方**がこれを使う (解決規則を 2 つ持たない)。
fn resolve_submit_bin() -> Result<PathBuf, String> {
    let exe =
        std::env::current_exe().map_err(|e| format!("実行ファイルのパスを取得できません: {e}"))?;
    let dir = exe
        .parent()
        .ok_or("実行ファイルの親ディレクトリを解決できません。")?;
    let bin_name = if cfg!(windows) {
        "gse-submit.exe"
    } else {
        "gse-submit"
    };
    let submit_bin = dir.join(bin_name);
    if !submit_bin.is_file() {
        // ⚠️★★ **絶対パスを画面に出さない** (security-checker MEDIUM-1)。
        //
        //   このメッセージは `last_error` 経由でスタート画面の `<code>` に出るが、
        //   ★ 画面の文言は「**次の内容を研究者にお伝えください**」であり、
        //   **被験者にスクリーンショット共有を促している**。Windows のポータブル配布では
        //   `C:\Users\<実名>\Downloads\...` になりうるので、
        //   ⚠️ ★ **P012 と実名が同じ画像に並ぶ = 仮名化が解ける**。
        //   ★ 診断に要る絶対パスは **ローカルのログにだけ**残す。
        tracing::error!(
            "gse-submit not found: {}",
            redact_home_path(&submit_bin.to_string_lossy())
        );
        return Err(format!(
            "提出ツール ({bin_name}) が見つかりません。配布パッケージが壊れている可能性があります。研究者に連絡してください。"
        ));
    }
    Ok(submit_bin)
}

fn run_submit_blocking(app: tauri::AppHandle, id: String) -> Result<SubmitOutcome, String> {
    let submit_bin = resolve_submit_bin()?;

    // 同梱公開鍵を env 経由で渡す (gse-submit は GSE_RECIPIENT を最優先で採用)。
    let recipient = resolve_bundled_recipient(&app);
    if recipient.is_none() {
        // mac は exe 隣 (Contents/MacOS) に鍵が無く resource 経由が唯一の経路。解決失敗を可視化し
        // 「公開鍵未解決」の原因切り分けを容易にする (gse-submit 側で fail-loud になる)。
        tracing::warn!(
            "in-app submit: bundled recipient (pubkey.txt) not resolved; relying on gse-submit fallback"
        );
    }

    // 参加者 ID は env で渡し対話プロンプトを省略する (子プロセスに TTY が無いため)。
    let mut cmd = std::process::Command::new(&submit_bin);
    cmd.env("GSE_PARTICIPANT_ID", &id);
    if let Some(r) = &recipient {
        cmd.env("GSE_RECIPIENT", r);
    }
    // Windows: 子プロセスのコンソール窓を出さない (CREATE_NO_WINDOW)。
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    let output = cmd
        .output()
        .map_err(|e| format!("提出ツールの起動に失敗しました: {e}"))?;

    if output.status.success() {
        tracing::info!("in-app submit succeeded for participant {}", id);
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(SubmitOutcome {
            out_path: extract_age_path(&stdout),
        })
    } else {
        // fail-loud: 詳細 (stderr→stdout) は UI にのみ返しリトライ可能にする。ログには exit code
        // のみ残す。さらに UI へ返す詳細はホームパス (= OS ユーザー名を含み得る) を伏せる
        // (被験者がエラー画面を共有しても実名が漏れない・data-privacy)。
        tracing::warn!("in-app submit failed (exit {:?})", output.status.code());
        let stderr = String::from_utf8_lossy(&output.stderr);
        let stdout = String::from_utf8_lossy(&output.stdout);
        let raw = if !stderr.trim().is_empty() {
            stderr.trim()
        } else {
            stdout.trim()
        };
        let detail = redact_home_path(raw);
        Err(if detail.is_empty() {
            "提出に失敗しました (詳細不明)。研究者に連絡してください。".to_string()
        } else {
            detail
        })
    }
}

/// 文字列中のローカルのホームディレクトリパス (`$USERPROFILE` / `$HOME`、= OS ユーザー名を
/// 含み得る) を `~` に伏せる。被験者がエラー詳細をスクショ共有しても実名が漏れないようにする
/// (data-privacy)。`gse-submit` の失敗メッセージには `~/Documents/...` 等のパスが混入し得る。
fn redact_home_path(detail: &str) -> String {
    let homes: Vec<String> = ["USERPROFILE", "HOME"]
        .iter()
        .filter_map(std::env::var_os)
        .map(|v| v.to_string_lossy().into_owned())
        .filter(|s| !s.is_empty())
        .collect();
    redact_prefixes(detail, &homes)
}

/// `homes` 中の各パス文字列を `~` に置換する純関数 (env 非依存・並列テスト安全)。
fn redact_prefixes(detail: &str, homes: &[String]) -> String {
    let mut out = detail.to_string();
    for h in homes {
        out = out.replace(h, "~");
    }
    out
}

// --- G1 自動提出 (収束器の起動と、その結果の可視化) --------------------------------
//
// ★ アプリ本体は **収束器を起こすだけ**である (`design.md` §2)。匿名化・age 暗号化・HTTP は
//   すべて `gse-submit` (feature = "package") の中にあり、⚠️ **盲検アプリ本体に age も HTTP も
//   載せない** (decisions D3)。→ ★ Tauri CSP を 1 文字も触らずに外部送信が成立する。
//
// ⚠️★ **「起こしたつもりで動いていない」を検知する経路が要る** (`design.md` §2)。
//   `silent-failure-in-guard-scripts` の型そのものなので、★ 失敗はログではなく
//   **画面 (未送信件数の隣)** に出す。

/// 収束器の直近の失敗。★ 画面に出すために保持する (`None` = 直近は成功)。
static SUBMIT_LAST_ERROR: Mutex<Option<String>> = Mutex::new(None);

/// ★ 送信先が設定されていない (`g1-submit.json` が無い / 空) ことを直近の実行が報告したか。
///
/// ⚠️★★ **これを画面に出さないと、研究者の設定忘れが「誰も気づかない全損」になる**
/// (code-review HIGH)。`.age` はできるので `errors` は空・exit 0 で、
/// ★ **未送信件数だけが静かに増える**。UI は「次のブロックの後に再試行します」と
/// 書いているが、⚠️ 実際には**永久に送られない**。
static SUBMIT_UPLOAD_DISABLED: AtomicBool = AtomicBool::new(false);

// --- ★ 送信の「成功」を画面に出すための実測値 (2026-08-10) ------------------------
//
// ⚠️★★ 送信成功はこれまで **何も表示していなかった** (箱が消えるだけ)。しかも承認から
//   完了まで実機で 6.2 秒 / 5.7 秒かかっており、その間も無表示だった。
//   → ★ 「警告が消えた ＝ 成功」と読ませていた (memory `silent-success-is-not-visible`)。
//
// ⚠️★★ **根拠を「ボタンを押したこと」にしない。** 収束器が `.sent` を置いたときだけ
//   `GSE_RECONCILE` の `sent` が増える (`reconcile.rs` の設計核 ③: アップロードが
//   `Ok(())` を返したときにだけ `.sent` を置く)。★ ここが端末から得られる最強の証拠であり、
//   押下や `awaiting_approval` の減少を根拠にすると **偽のレシート**になる。

/// 最後に **1 件以上送れた** 時刻 (epoch ms)。`0` = このプロセスではまだ 1 件も送れていない。
static SUBMIT_LAST_SENT_MS: AtomicU64 = AtomicU64::new(0);

/// そのとき送れた本数 (レシートの「N 件」)。
static SUBMIT_LAST_SENT_COUNT: AtomicU64 = AtomicU64::new(0);

/// いま走っている収束器の本数。★ `> 0` = 送信中 (画面に「送信しています…」を出す)。
///
/// ⚠️ 起点が 2 本ある (起動時 / 承認・ブロック終了時) ので bool ではなく数える。
static SUBMIT_IN_FLIGHT: AtomicU64 = AtomicU64::new(0);

/// `SUBMIT_IN_FLIGHT` を必ず戻すための番兵。
///
/// ⚠️★ 手で `fetch_sub` を書くと、途中の panic や `?` の early return で**戻し忘れる**。
/// そうなると画面は「送信しています…」のまま**永久に固まり**、
/// ★ 未送信件数の警告も (`!sending` gate により) 出なくなる = **沈黙が悪化する**。
struct InFlightGuard;

/// いま走っている収束器の**きっかけ**。0=無し / 1=起動時 / 2=ブロック終了後 / 3=承認後。
///
/// ⚠️★ 画面が「送信しています…」を出してよいかの判断に使う。★ **起動時のスキャンだけは
/// 出さない**: 毎回走って平常時は何もしないので、出すと起動のたびに箱が点滅する。
/// ⚠️ 逆に、それ以外 (ブロック終了後・承認後) は **`.age` を作る前から**出さないと、
/// ★ 梱包中 (`unsent` がまだ 0) が無表示になる (code-reviewer MEDIUM)。
static SUBMIT_IN_FLIGHT_REASON: AtomicU64 = AtomicU64::new(0);

/// 収束器が走り始めた時刻 (epoch ms)。0 = 走っていない。
///
/// ⚠️★ 「数秒かかります」は嘘になりうる: 送信の timeout は **180 秒/件**で、
/// 3 件なら最悪 9 分かかる。★ その間 `!sending` ゲートで
/// **未送信カード (唯一の安全装置) が隠れる**ので、経過時間を画面へ渡して判断させる。
static SUBMIT_IN_FLIGHT_SINCE_MS: AtomicU64 = AtomicU64::new(0);

/// 収束器のきっかけ。★ 数値は DTO 経由でフロントへ渡る。
#[derive(Clone, Copy, PartialEq, Eq)]
enum ReconcileReason {
    Startup = 1,
    BlockEnd = 2,
    Approval = 3,
    /// ⚠️★★★ O1 (R3-a): **日次ローテートでファイルが 1 本閉じた**。
    /// ★ 閉じた直後は猶予 (48 時間) の中なので **まだ包まれない**。
    /// ⚠️ それでも回すのは、**前々日ぶんが猶予を抜けている**からである
    /// (`design.md` §1「起動のきっかけはヒント」と同じ収束型の考え方)。
    O1DailyRotation = 4,
}

impl ReconcileReason {
    /// ログ用の名前 (従来の `reason` 文字列と同じ文言を保つ)。
    fn label(self) -> &'static str {
        match self {
            ReconcileReason::Startup => "at startup",
            ReconcileReason::BlockEnd => "after block",
            ReconcileReason::Approval => "after approval",
            ReconcileReason::O1DailyRotation => "after daily rotation",
        }
    }
}

impl InFlightGuard {
    fn new(reason: ReconcileReason) -> Self {
        // ⚠️★ `Release` にする。⚠️ `Relaxed` だと `last_sent_ms` の `Release` ストアと
        //   同期せず、★ aarch64 (macOS ビルド) で「`sending=false` なのに `last_sent_ms=0`」を
        //   観測する並びがありうる = 送信成功直後の 1 ポーリング分だけレシートが出ない
        //   (code-reviewer LOW)。
        let prev = SUBMIT_IN_FLIGHT.fetch_add(1, Ordering::Release);
        SUBMIT_IN_FLIGHT_REASON.store(reason as u64, Ordering::Release);
        if prev == 0 {
            SUBMIT_IN_FLIGHT_SINCE_MS.store(now_epoch_ms(), Ordering::Release);
        }
        Self
    }
}

impl Drop for InFlightGuard {
    fn drop(&mut self) {
        // `fetch_sub` は減算 **前**の値を返す。1 なら自分が最後の 1 本である。
        if SUBMIT_IN_FLIGHT.fetch_sub(1, Ordering::Release) == 1 {
            SUBMIT_IN_FLIGHT_REASON.store(0, Ordering::Release);
            SUBMIT_IN_FLIGHT_SINCE_MS.store(0, Ordering::Release);
        }
    }
}

/// いまの epoch ms。
///
/// ⚠️★ 失敗時に **`0` を返さない**。`0` は `last_sent_ms` で
/// 「まだ 1 件も送っていない」を表すセンチネルなので、★ 衝突すると
/// **実際に送れてもレシートが永久に出ない** (システム時計が 1970 以前の端末・
/// code-reviewer LOW)。
fn now_epoch_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(1)
}

/// ★ レシートの根拠を捨てる (「前の回のレシート」が次の回に残らないようにする)。
///
/// ⚠️★★ これを呼ばないと、`last_sent_ms` は**プロセス全体で 1 個**しかないため:
/// - ブロック終了直後の梱包前に **前の回のレシート**が数秒出る (code-reviewer HIGH-2)
/// - 参加者 ID を打ち直すと、別 ID の `.age` が orphan 化して `unsent=0` になり、
///   ★ **偽レシート**が出続ける (security-checker MEDIUM-2)
fn reset_sent_receipt() {
    SUBMIT_LAST_SENT_MS.store(0, Ordering::Release);
    SUBMIT_LAST_SENT_COUNT.store(0, Ordering::Release);
}

/// スタート画面へ返す提出状態 (G1 モードのときだけフロントが読む)。
#[derive(serde::Serialize, Clone)]
struct SubmissionStatusDto {
    /// 未送信の `.age` 本数。★ **突き合わせで数える** (カウンタを持たない)。
    unsent: usize,
    /// 直近の自動提出で起きた問題 (無ければ `null`)。
    last_error: Option<String>,
    /// ★ 送信先が未設定 (研究者の設定忘れ / 意図的な停止・D-4)。
    upload_disabled: bool,
    /// ★ **被験者の確認待ち**の本数 (`.age` は在るが「送信する」がまだ押されていない・D-14)。
    awaiting_approval: usize,
    /// ★ いま収束器が走っている (= 送信を試みている最中)。
    sending: bool,
    /// ★ 最後に 1 件以上送れた時刻 (epoch ms)。`null` = このプロセスではまだ無い。
    last_sent_ms: Option<u64>,
    /// ★ そのとき送れた本数。`last_sent_ms` が `null` なら `0`。
    last_sent_count: usize,
    /// ★★ **件数を本当に数えられたか。**
    ///
    /// ⚠️ ホーム or 参加者 ID が解決できないと `unsent` / `awaiting_approval` は
    /// 「実際に 0 件」ではなく **「数えられなかった」** の意味で 0 になる。
    /// ★ ここを見ずに「✅ 送信を待っている記録はありません」を出すと、
    /// `.age` が実在するのに **fail-open で緑を出す** (code-reviewer MEDIUM)。
    counted: bool,
    /// いま走っている収束器のきっかけ (0=無し / 1=起動時 / 2=ブロック終了後 / 3=承認後)。
    sending_reason: u64,
    /// 収束器が走り始めた時刻 (epoch ms)。`null` = 走っていない。
    sending_since_ms: Option<u64>,
}

/// 未送信件数と直近のエラーを返す。★ 0 件・エラー無しなら UI は何も出さない。
///
/// ⚠️ ★ 件数は **`unsent_age_files` と同じ規則**で数える (この参加者のブロック分だけ)。
/// 別々の規則にすると、画面の件数と実際に送られる対象が drift する。
#[tauri::command]
fn get_submission_status() -> SubmissionStatusDto {
    // ⚠️★ 「0 件だった」と「数えられなかった」を **区別して**返す (`counted`)。
    let (unsent, awaiting_approval, counted) = match (
        crate::submission::default_submission_dir(),
        crate::submission::read_g1_participant_id(),
    ) {
        (Some(dir), Some(id)) => (
            crate::submission::unsent_count(&dir, &id),
            crate::submission::awaiting_approval_count(&dir, &id),
            true,
        ),
        _ => (0, 0, false),
    };
    let last_error = SUBMIT_LAST_ERROR
        .lock()
        .unwrap_or_else(|p| p.into_inner())
        .clone();
    let last_sent_ms = match SUBMIT_LAST_SENT_MS.load(Ordering::Acquire) {
        0 => None,
        ms => Some(ms),
    };
    SubmissionStatusDto {
        unsent,
        last_error,
        upload_disabled: SUBMIT_UPLOAD_DISABLED.load(Ordering::Relaxed),
        awaiting_approval,
        // ⚠️★ `Acquire` にする (`InFlightGuard` の `Release` と対にする)。
        sending: SUBMIT_IN_FLIGHT.load(Ordering::Acquire) > 0,
        last_sent_ms,
        last_sent_count: SUBMIT_LAST_SENT_COUNT.load(Ordering::Acquire) as usize,
        counted,
        sending_reason: SUBMIT_IN_FLIGHT_REASON.load(Ordering::Acquire),
        sending_since_ms: match SUBMIT_IN_FLIGHT_SINCE_MS.load(Ordering::Acquire) {
            0 => None,
            ms => Some(ms),
        },
    }
}

/// ★ 被験者が「送信する」を押したときに呼ぶ (D-14: 送信前の確認)。
///
/// 確認待ちの `.age` **すべて**に確認の印を付け、そのまま収束器を起こす。
/// ⚠️ ★ **印を付けるところまでは同期**にする。押したのに何も起きていない状態を作らない。
#[tauri::command]
fn approve_pending_submissions(app: tauri::AppHandle) -> Result<usize, String> {
    let dir = crate::submission::default_submission_dir()
        .ok_or("提出物フォルダを解決できませんでした。")?;
    let id =
        crate::submission::read_g1_participant_id().ok_or("参加者 ID が登録されていません。")?;
    let n = crate::submission::approve_pending(&dir, &id)?;
    tracing::info!("G1: participant approved {} submission(s)", n);
    // ★ 確認直後に送る。⚠️ 失敗しても `.age` と確認の印は残るので、次の機会に送られる。
    spawn_reconcile(app, ReconcileReason::Approval);
    Ok(n)
}

/// 登録済みの G1 参加者 ID を返す (未登録なら `null`)。
#[tauri::command]
fn get_g1_participant_id() -> Option<String> {
    crate::submission::read_g1_participant_id()
}

/// G1 参加者 ID を登録する。⚠️ ★ 妥当でない ID は **書かずに** `Err` を返す (fail-closed)。
#[tauri::command]
fn set_g1_participant_id(id: String) -> Result<(), String> {
    // ⚠️★★ **ID が変わったらレシートの根拠を捨てる** (security-checker MEDIUM-2)。
    //
    //   `last_sent_ms` はプロセス全体で 1 個しか無いのに、`unsent` /
    //   `awaiting_approval` は **現在の ID 限定**で数える。被験者が `P012` → `P013`
    //   (あるいは `p012`) と打ち直すと既存の `.age` が全部 orphan 化して 0 件になり、
    //   ★ **前の ID で送った実績のレシートが「この回の記録を送信しました」として出続ける**。
    //   → 未送信が恒久的に届かないまま、被験者にも研究者にも警告が出ない。
    let changed = crate::submission::read_g1_participant_id().as_deref() != Some(id.trim());
    crate::submission::write_g1_participant_id(&id)?;
    if changed {
        reset_sent_receipt();
    }
    Ok(())
}

/// 収束器 (`gse-submit --reconcile`) を **別スレッドで** 1 回起こす。
///
/// ★ `reason` はログ用のきっかけ名 (`"at startup"` / `"after block"`)。
/// ⚠️ ★ **G1 でも O1 でもなければ何もしない** (通常運用 = Phase1 の挙動を 1 バイトも変えない)。
/// ★ 何度呼んでも安全 (収束器はべき等) なので、二重起動を気にしなくてよい。
fn spawn_reconcile(app: tauri::AppHandle, reason: ReconcileReason) {
    if !auto_submit_enabled() {
        return;
    }
    spawn_reconcile_with_guard(app, reason, InFlightGuard::new(reason));
}

/// 自動提出の経路が開いているか。
///
/// ⚠️★★★ **G1 と O1 の 2 つだけ**である。★ 通常運用 (Phase1) では
/// `.age` を作りも送りもしない (従来どおり手動提出だけ)。
///
/// ## ⚠️★★★ O1 は **1 回きりの同意確認**が済むまで開かない (研究者判断 R-7)
///
/// ★ D-14 の `.age.ok` (毎回の送信確認) は O1 では外した (R-2)。⚠️ しかしそれは
/// 「**同意手続きを経ていない人が配布ビルドを起動する経路を塞ぐ**」役も担っていた。
/// ⚠️★★★ security-checker HIGH-4 の実測: **G1 をやった端末に O1 ビルドを置くだけで、
/// 人の操作ゼロで常時記録＋48 時間後の自動送信が始まる**
/// (★ `~/.gse/g1_participant_id` が既に残っているため)。
/// → ★ **確認が済むまで送信経路を開かない。** ⚠️ `.age` は作られる (データは失われない)。
fn auto_submit_enabled() -> bool {
    if crate::o1::is_o1() {
        return crate::submission::o1_consent_acknowledged();
    }
    g1_mode().is_some()
}

/// ★★ 番兵を **呼び出し側で作ってから**渡す版。
///
/// ⚠️★★ ブロック終了経路がこれを使う理由 (code-reviewer HIGH-2):
///   `emit("g1-block-ended")` でフロントはスタート画面へ戻り、**即座に**状態を読みに来る。
///   ところが `sending: true` が立つのは `block_end_ack` を待った**後**なので、その窓では
///   `awaiting_approval=0 / unsent=0 / sending=false / last_sent_ms=前の回` になり、
///   ★ **前の回のレシート**が最大 3 秒 (ack タイムアウト時 8 秒) 残る。2 ブロック目以降**毎回**。
///   → ★ 番兵を **emit より前**で作れば、スタート画面が出た瞬間から `sending: true` になり、
///     レシートも全クリアカードも**構造的に**出せなくなる。
fn spawn_reconcile_with_guard(
    app: tauri::AppHandle,
    reason: ReconcileReason,
    in_flight: InFlightGuard,
) {
    if !auto_submit_enabled() {
        return;
    }
    let reason = reason.label();
    // ⚠️★★ **スレッドの外で**数え始める。中で数えると、被験者が「送信する」を押して
    //   確認カードが消えてから、スレッドが起きて `sending` が立つまでの間に
    //   ★ **無表示の窓**ができる (今回潰そうとしている沈黙そのもの)。
    //   `approve_pending_submissions` はこの関数を呼んでから返るので、
    //   ★ フロントが押下直後に読む状態には既に `sending: true` が乗っている。
    // ⚠️★ **ラベルをモードに合わせる** (2026-08-27)。★ O1 でもこの経路を使うようになったので、
    //   「G1 auto-submit」と固定で書くと ⚠️ **ログを読む人がモードを取り違える**。
    let mode_label = if crate::o1::is_o1() { "O1" } else { "G1" };
    thread::spawn(move || {
        // ★ スレッドが終わるとき (下の early return も含め) に必ず戻す。
        let _in_flight = in_flight;
        // ⚠️ ★ **ブロック中には走らせない** (`design.md` §1: 測定中の端末に負荷をかけない)。
        //   起動時のヒントはスレッドで遅れて走るので、被験者が数秒後に「開始する」を押すと
        //   ★ **ブロック中に age 暗号化と送信が走りうる** (code-review LOW)。
        //   ★ 見送っても損失にならない (次のブロック終了で必ず拾われる)。
        if SESSION_START_MS.load(Ordering::Acquire) != 0 {
            tracing::info!(
                "{} auto-submit ({}): skipped (a block is running; will run at block end)",
                mode_label,
                reason
            );
            return;
        }
        let outcome = run_reconcile_blocking(&app);
        let mut slot = SUBMIT_LAST_ERROR.lock().unwrap_or_else(|p| p.into_inner());
        match outcome {
            Ok(Some(summary)) => {
                tracing::info!("{} auto-submit ({}): {}", mode_label, reason, summary);
                *slot = None;
            }
            Ok(None) => {
                // ★ 何もしなかった (ID 未登録)。⚠️ **失敗ではないので画面に出さない。**
                //   ⚠️ ★ 直前の失敗を **消しもしない** (成功していないため)。
                tracing::info!(
                    "{} auto-submit ({}): skipped (participant id not registered yet)",
                    mode_label,
                    reason
                );
            }
            Err(e) => {
                // ⚠️ ログだけにしない。★ 画面へ出すために保持する。
                tracing::error!("{} auto-submit ({}) FAILED: {}", mode_label, reason, e);
                *slot = Some(e);
            }
        }
    });
}

/// 収束器を子プロセスとして実行する (ブロッキング)。
///
/// `Ok(Some(要約))` = 走った / `Ok(None)` = **参加者 ID 未登録なので何もしなかった**。
///
/// ⚠️★ ID 未登録を **エラーにしない**のは、★ **初回起動では必ずこの状態になる**からである
/// (被験者はまだ ID を入力していない)。エラーにすると、⚠️ **ID を入力する前のスタート画面に
/// 赤いエラーが出る** — 手引きは「未送信が残っていないことだけ確認してください」と
/// 書いているので、これは被験者を無用に不安にさせる。
/// ★ この時点で失うものは無い: ID が要るのは `.age` の名前だけで、
/// ID が入るまでブロックは 1 つも始められない (`g1_start_gate`)。
fn run_reconcile_blocking(app: &tauri::AppHandle) -> Result<Option<String>, String> {
    // ⚠️★★★ **O1 は専用の ID ファイルを読む** (研究者判断 R-7)。
    //   ★ `g1_participant_id` を流用すると、G1 をやった端末で **ID 入力の操作すら要らなくなる**。
    let id = match if crate::o1::is_o1() {
        crate::submission::read_o1_participant_id()
    } else {
        crate::submission::read_g1_participant_id()
    } {
        Some(id) => id,
        None => return Ok(None),
    };
    let submit_bin = resolve_submit_bin()?;

    let mut cmd = std::process::Command::new(&submit_bin);
    cmd.arg("--reconcile");
    // ⚠️★★★ O1 は **別の規則**で収束させる (`gse_o1_*` を対象・48 時間の猶予・承認なし)。
    //   ★ 判定は**アプリ側の 1 か所**で行って渡す —— `gse-submit` の `current_exe()` は
    //   macOS のバンドル内 sidecar だとアプリ本体と階層が違い、⚠️ 自前で `o1.mode` を
    //   探させると**静かに G1 の規則で包む**ことになる。
    if crate::o1::is_o1() {
        cmd.arg("--o1");
    }
    cmd.env("GSE_PARTICIPANT_ID", &id);
    if let Some(r) = resolve_bundled_recipient(app) {
        cmd.env("GSE_RECIPIENT", r);
    }
    // Windows: 子プロセスのコンソール窓を出さない (CREATE_NO_WINDOW)。
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    let output = cmd
        .output()
        .map_err(|e| format!("自動提出ツールを起動できませんでした: {e}"))?;
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let summary = extract_reconcile_summary(&stdout);
    // ★ 「送信先が未設定」は errors にも exit code にも出ない。要約行から拾って画面へ届ける。
    SUBMIT_UPLOAD_DISABLED.store(
        summary
            .as_ref()
            .map(|s| summary_flag(s, "upload_disabled"))
            .unwrap_or(false),
        Ordering::Relaxed,
    );
    // ★★ 送信できた事実を記録する (レシートの根拠)。
    // ⚠️ ★ **exit code を見る前に**やる。errors が在っても「送れた分は送れた」ので、
    //   部分成功を捨てない (`.sent` は成功した本にだけ置かれている)。
    record_sent_if_any(
        summary.as_deref().and_then(|s| summary_count(s, "sent")),
        // ⚠️★ `0` は「まだ 1 件も送っていない」のセンチネルなので返さない (`now_epoch_ms`)。
        now_epoch_ms,
    );
    if output.status.success() {
        return Ok(Some(summary.unwrap_or_else(|| "done".to_string())));
    }
    // fail-loud。⚠️★ **詳細をそのまま画面に出さない** (code-review MEDIUM):
    //   子プロセスの stderr は `gse-submit: P012_block03_gse_20260807_101112.age を送信できません: …`
    //   の形で **参加者 ID とセッション日時**を含む。`redact_home_path` はホームパスしか伏せない。
    //   ★ 画面には定型文だけを出し、⚠️ 詳細は**ローカルのログにだけ**残す。
    let stderr = String::from_utf8_lossy(&output.stderr);
    let raw = if !stderr.trim().is_empty() {
        stderr.trim()
    } else {
        stdout.trim()
    };
    tracing::error!("G1 auto-submit detail: {}", redact_home_path(raw));
    Err(format!(
        "記録の自動送信に失敗しました (未送信 {} 件)。実施はそのまま続けてください。",
        summary
            .as_ref()
            .and_then(|s| summary_count(s, "unsent"))
            .unwrap_or(0)
    ))
}

/// `gse-submit --reconcile` が出す要約行 (`GSE_RECONCILE {...}`) を取り出す。
///
/// ★ ここで拾えるのは **件数だけ**である (ファイル名も参加者 ID も出していない・data-privacy)。
fn extract_reconcile_summary(stdout: &str) -> Option<String> {
    stdout
        .lines()
        .map(str::trim)
        .find_map(|l| l.strip_prefix("GSE_RECONCILE "))
        .map(|s| s.to_string())
}

/// 要約行 (JSON) から bool を読む。読めなければ `false` (安全側)。
fn summary_flag(summary: &str, key: &str) -> bool {
    serde_json::from_str::<serde_json::Value>(summary)
        .ok()
        .and_then(|v| v.get(key).and_then(|x| x.as_bool()))
        .unwrap_or(false)
}

/// 要約行 (JSON) から件数を読む。
fn summary_count(summary: &str, key: &str) -> Option<usize> {
    serde_json::from_str::<serde_json::Value>(summary)
        .ok()
        .and_then(|v| v.get(key).and_then(|x| x.as_u64()))
        .map(|n| n as usize)
}

/// 収束器が報告した `sent` を、レシートの根拠として記録する。
///
/// ⚠️★★ **`sent == 0` では何も書き換えない。** 収束器はアプリ起動時にも走り、
/// ★ **平常時はほぼ毎回 `sent: 0`** である。0 で上書きすると
/// ⚠️ **本当に送れた直後のレシートが数秒で消える** (被験者から見ると「出て、消えた」)。
/// ★ この関数が保つのは「**最後に本当に送れたのはいつ・何件か**」であって、
/// 「直近の実行の結果」ではない。
///
/// 時刻は引数で受ける (テストが実時計に依存しないため)。
fn record_sent_if_any(sent: Option<usize>, now_ms: impl FnOnce() -> u64) {
    let n = match sent {
        Some(n) if n > 0 => n,
        _ => return,
    };
    SUBMIT_LAST_SENT_COUNT.store(n as u64, Ordering::Relaxed);
    // ★ 件数を先に置き、時刻を Release で置く。読む側は時刻を Acquire で読むので、
    //   「新しい時刻・古い件数」の組み合わせが観測されない。
    SUBMIT_LAST_SENT_MS.store(now_ms(), Ordering::Release);
}

/// アプリ内「提出する」ボタンの Tauri コマンド。最新セッションを同梱 `gse-submit` で
/// 匿名化 + 暗号化し、`.age` を生成する。失敗は fail-loud で `Err` を UI に返す (静かに失わない)。
///
/// `gse-submit` の匿名化 + age 暗号化は数百 ms 以上かかり得るため、`async` + `spawn_blocking`
/// で subprocess をワーカースレッドに退避し、IPC/メインスレッド (overlay 制御等のイベントループ)
/// を塞がない。
#[tauri::command]
async fn submit_latest_session(
    app: tauri::AppHandle,
    participant_id: String,
) -> Result<SubmitOutcome, String> {
    // ⚠️★★★ **O1 では手動提出を受け付けない** (security-checker HIGH-1・2026-08-27)。
    //
    // ★ この経路は `gse-submit` を**引数なし**で起こし、`packaging::find_latest_session_ndjson`
    //   が **`session_end` を要求せずに最新の `gse_*.ndjson` を選ぶ**。
    //   → ⚠️ O1 では **いま書いている最大 24 時間ぶんのファイル**がその場で `.age` に包まれる。
    //
    // ⚠️★★★ 帰結が 2 つとも重い:
    //   1. **48 時間の猶予を丸ごと迂回する** —— `redact_dir` は `.age` を触らないので、
    //      ★ **その瞬間から被験者は消せない** (同意文書 §4-3 の逐語の破れ ＝ 判断 3 の根拠 3)。
    //   2. `submission::age_for_stem` が「既に包んである」と判定するため、
    //      ⚠️ **猶予明けの収束器がその stem を二度と包まない** → 静かなデータ欠落。
    //
    // ★ O1 の提出経路は収束器 (`--reconcile --o1`) **1 本だけ**にする。
    //   ⚠️ UI 側 (`Dashboard.tsx`) でも当該セクションを出さないが、**両方で塞ぐ**
    //   (画面だけの対処にすると、次に画面をいじった人が黙って穴を開け直す)。
    if crate::o1::is_o1() {
        tracing::warn!("O1: manual submit rejected (auto-submission handles O1 after the grace)");
        return Err("この記録は自動で提出されます。手動での提出は使いません。".to_string());
    }

    let id = participant_id.trim().to_string();
    if !crate::participant_id::is_valid_participant_id(&id) {
        return Err(
            "参加者 ID が正しくありません (英数字のみ・1〜16 文字。例: P006)。".to_string(),
        );
    }

    // ブロッキングな subprocess 実行をワーカースレッドへ退避 (UI を固めない)。
    tauri::async_runtime::spawn_blocking(move || run_submit_blocking(app, id))
        .await
        .map_err(|e| format!("提出処理の実行に失敗しました: {e}"))?
}

/// Phase 1 Ground Truth ラベル記録の共通処理。
///
/// Tauri コマンド (`record_user_label`) と OS グローバルホットキーの
/// 両経路から呼ばれる。サーバー側で timestamp を付与し 2 秒デバウンスを適用する。
/// 成功時は記録した timestamp (epoch ms) を返す。
fn record_label_internal(log: &Arc<Mutex<LogState>>, label: UserLabelKind) -> Result<u64, String> {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| e.to_string())?
        .as_millis() as u64;
    // compare_exchange で「now 書き込みに勝ったスレッドだけ通す」race-free デバウンス。
    // Tauri コマンド経路とホットキー経路が同時発火してもログ重複しない。
    loop {
        let last = LAST_LABEL_MS.load(Ordering::Relaxed);
        if now.saturating_sub(last) < LABEL_DEBOUNCE_MS {
            return Err("debounced (<2s since last label)".to_string());
        }
        if LAST_LABEL_MS
            .compare_exchange(last, now, Ordering::Relaxed, Ordering::Relaxed)
            .is_ok()
        {
            break;
        }
    }
    log.lock()
        .unwrap_or_else(|p| p.into_inner())
        .tx
        .try_send(LogEntry::UserLabel {
            timestamp: now,
            label,
            recovered_at: None,
        })
        .map_err(log_send_error)?;
    tracing::info!("user_label recorded: {} @ {}", label.as_str(), now);
    Ok(now)
}

/// Phase 1 Ground Truth ラベル記録の Tauri コマンド。
///
/// `label` は "flow" / "incubation" / "stuck" のみ許可。それ以外は `Err`。
/// 成功時は `user_label_recorded` Tauri イベントを emit し、
/// Dashboard counter widget のリアルタイム更新に使う。
#[tauri::command]
fn record_user_label(
    app: tauri::AppHandle,
    label: String,
    log: State<'_, Arc<Mutex<LogState>>>,
) -> Result<(), String> {
    // ⚠️★★★ **O1 では被験者由来のラベル行を記録しない** (2026-08-31)。
    //   ★ 起動ログが名指ししている当の行型がこれである（逐語 `user_label / review_marker rows
    //     that the consent form does not list`）。⚠️ それなのに門が無かった。
    //   ★ `src/` からの参照は 0 件で現時点の到達経路は無いが、
    //     ⚠️ **コマンドは invoke_handler に登録されたまま**であり、
    //     ★ 「UI 側だけの対処は次に UI をいじった人が穴を開け直す」という
    //       2026-08-30 の教訓がそのまま当てはまる。
    if !crate::o1::label_row_allowed(crate::o1::is_o1()) {
        tracing::warn!(
            "record_user_label: ignored in O1 mode (the O1 consent form does not list this row). \
             This is a gate, not a failure."
        );
        return Ok(());
    }
    let kind = UserLabelKind::parse(&label).ok_or_else(|| format!("invalid label: {:?}", label))?;
    let timestamp = record_label_internal(&log, kind)?;
    if let Err(e) = app.emit(
        "user_label_recorded",
        serde_json::json!({
            "label": kind.as_str(),
            "timestamp": timestamp,
        }),
    ) {
        tracing::warn!("user_label_recorded emit failed: {}", e);
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// Task C: v0.3 較正スモークの収集 command 群 (frontend → logger)
// すべて数値・固定カテゴリ・不透明 ID のみを記録する (data-privacy)。
// ---------------------------------------------------------------------------

/// 受領した不透明 ID (vignette_id 等) の検証。本文/ウィンドウタイトル由来の文字列が
/// ID に混入するのを境界で遮断する (`[A-Za-z0-9_-]`・1..=16 文字)。
///
/// ⚠️ 規則の本体は `analysis::calibration_eval::is_valid_opaque_id` に 1 つだけ置く。
/// NDJSON 読込側 (`gse-replay`) も同じ関数を使うので、**規則が二重管理にならない**。
fn is_valid_opaque_id(s: &str) -> bool {
    crate::analysis::calibration_eval::is_valid_opaque_id(s)
}

/// 受領した (source, probe_id) を検証して `ProbeRef` を構築する (DC-3 / cross-review #7)。
/// random_probe ⇒ probe_id は Some かつ `ProbeId::is_valid`、self_marker ⇒ probe_id は None。
fn build_probe_ref(source: &str, probe_id: Option<String>) -> Result<ProbeRef, String> {
    let source =
        ProbeSource::parse(source).ok_or_else(|| format!("invalid source: {:?}", source))?;
    match source {
        ProbeSource::RandomProbe => {
            let id = probe_id.ok_or_else(|| "random_probe requires probe_id".to_string())?;
            if !crate::analysis::probe_scheduler::ProbeId::is_valid(&id) {
                return Err("invalid probe_id format".to_string());
            }
            Ok(ProbeRef::RandomProbe { probe_id: id })
        }
        ProbeSource::SelfMarker => {
            if probe_id.is_some() {
                return Err("self_marker must not carry a probe_id".to_string());
            }
            Ok(ProbeRef::SelfMarker)
        }
    }
}

/// 省略可の固定カテゴリ文字列を `Condition` に検証する (capture-schema-freeze)。
/// `None` / 空文字 → `None` (未指定)。未知値は黙って捨てず `Err`。
fn parse_optional_condition(s: Option<&str>) -> Result<Option<Condition>, String> {
    match s {
        None | Some("") => Ok(None),
        Some(s) => Condition::parse(s)
            .map(Some)
            .ok_or_else(|| format!("invalid condition: {:?}", s)),
    }
}

/// 省略可の固定カテゴリ文字列を `LabelPool` に検証する (capture-schema-freeze)。
fn parse_optional_label_pool(s: Option<&str>) -> Result<Option<LabelPool>, String> {
    match s {
        None | Some("") => Ok(None),
        Some(s) => LabelPool::parse(s)
            .map(Some)
            .ok_or_else(|| format!("invalid label_pool: {:?}", s)),
    }
}

/// 介入応答の dismiss 理由を検証する (capture-schema-freeze 0.8)。
/// `None` / 空文字 → `Silent` (理由未選択でフェード相当)。未知値は `Err`。
fn parse_dismiss_reason(s: Option<&str>) -> Result<DismissReason, String> {
    match s {
        None | Some("") => Ok(DismissReason::Silent),
        Some(s) => {
            DismissReason::parse(s).ok_or_else(|| format!("invalid dismiss reason: {:?}", s))
        }
    }
}

/// v0.3 較正: セッション開始宣言を記録する (§3・§14)。固定カテゴリのみ許可。
// ⚠️ 引数はフロントとの IPC 契約 (`invoke("record_session_meta", {...})`) そのものなので、
//   構造体へまとめると App.tsx 側の呼び出し形が変わる。ADR-006 2b で engine を 1 つ足した
//   結果 7 個を超えたが、契約を守るためここは許可する。
#[allow(clippy::too_many_arguments)]
#[tauri::command]
fn record_session_meta(
    track: String,
    task_kind: String,
    intervention_enabled: bool,
    condition: Option<String>,
    label_pool: Option<String>,
    log: State<'_, Arc<Mutex<LogState>>>,
    engine: State<'_, CognitiveStateEngine>,
) -> Result<(), String> {
    // ⚠️★★★ **O1 では受け付けない** (cross-review / Codex HIGH・2026-08-27)。
    //
    // ★ O1 の宣言経路は `declare_task_kind` **1 本だけ**である。こちらを通されると:
    //   1. ⚠️ `intervention_enabled` を引数で受けるので **判断 O1-5 (介入を出さない) が破れる**
    //   2. ⚠️ **ローテートしないまま** `session_meta` を積むので、宣言を変えると
    //      1 ファイルに相異なる `task_kind` が 2 つ入り **`gse-replay` が `Err`** になる
    //   3. ⚠️ 未宣言を「行の不在」で表す判断 4b-3 が壊れる
    if crate::o1::is_o1() {
        tracing::warn!("O1: record_session_meta rejected (use declare_task_kind instead)");
        return Err("この画面はこの記録では使いません。".to_string());
    }

    let track = Track::parse(&track).ok_or_else(|| format!("invalid track: {:?}", track))?;
    let task_kind =
        TaskKind::parse(&task_kind).ok_or_else(|| format!("invalid task_kind: {:?}", task_kind))?;
    // ★ ADR-006 Phase 2b: 宣言された task_kind が domain head を選ぶ。
    //   ここでは **head_id を求めるだけ**で engine には触らない。差し替えは
    //   検証がすべて通り、session_meta 行の送信に成功した**後**に行う (下記)。
    let domain = TaskDomain::from(task_kind);
    let head_id = domain.head_id();
    // 省略可。指定時のみ固定カテゴリへ検証し、未知値はエラーにする (黙って捨てない)。
    let condition = parse_optional_condition(condition.as_deref())?;
    let label_pool = parse_optional_label_pool(label_pool.as_deref())?;
    // 介入の有効/無効をプロセス全体へ反映 (両ウィンドウの get_intervention_decision が参照)。
    INTERVENTION_ENABLED.store(intervention_enabled, Ordering::Release);
    // M0 (D1): 較正セッションなら収量優先プロファイルを選ぶフラグを立てる。condition が
    // blind_calibration のときのみ true (X1 較正のラベル収量を稼ぐ)。世代タグ
    // (SESSION_META_FOR_START_MS) を**この値を確定させた後**に Release で公開し、プローブスレッドが
    // 正しいプロファイルで初期化できるようにする (Acquire 側で IS_CALIBRATION の可視性が保証される)。
    SESSION_IS_CALIBRATION.store(
        matches!(condition, Some(Condition::BlindCalibration)),
        Ordering::Release,
    );
    // この meta が属する世代 = 現在の session_start。スケジューラはこれと session_start を照合する。
    let current_session_start = SESSION_START_MS.load(Ordering::Acquire);
    SESSION_META_FOR_START_MS.store(current_session_start, Ordering::Release);
    log.lock()
        .unwrap_or_else(|p| p.into_inner())
        .tx
        .try_send(LogEntry::SessionMeta {
            timestamp: epoch_ms(),
            track,
            task_kind,
            intervention_enabled,
            condition,
            label_pool,
            head_id,
        })
        .map_err(log_send_error)?;

    // ⚠️★ **head の差し替えはここで初めて行う。**
    //   検証エラーやログチャネル満杯で早期 return した場合に engine だけ切り替わると、
    //   「Coding head で採点された feat 行が、head 宣言の無いファイルに書かれる」状態になる。
    //   そのファイルを gse-replay に食わせると task_kind 不在で Writing head へフォールバックし、
    //   **本番とリプレイの採点が食い違う** (= Replay-as-Truth の破れ)。
    //   security-checker 指摘・2026-08-18。
    //
    //   ⚠️ 残る窓: start_session (engine.reset() で Writing に戻る) と本コマンドの間に挟まる
    //     1Hz tick は Writing head で採点される。App.tsx が start_session 成功直後に
    //     invoke するので実測 1 秒未満だが、ゼロではない (塞ぐには start_session に
    //     task_kind を持たせる必要があり、フロントの IPC 契約変更を伴う)。
    let applied = engine.set_domain(domain);
    debug_assert_eq!(
        applied, head_id,
        "記録した head_id と反映した head が食い違った"
    );

    tracing::info!(
        "session_meta recorded: track={} task_kind={} head_id={}",
        track.as_str(),
        task_kind.as_str(),
        head_id.as_str()
    );
    // ⚠️★★★ G-1: **`Ok` を返す直前**に立てる。フロントはこの `Ok` を見て `isStarted` へ進み、
    //   失敗時にだけ**再押下を促す**。→ ★ この旗が「握手が済んだか」と一対一に対応する。
    //   以後の再押下は**本物の二度押し**として扱ってよい (`g1::decide_start_action`)。
    SESSION_META_RECORDED.store(true, Ordering::Release);
    Ok(())
}

/// v0.3 較正: プローブ回答 (回答あり) を realtime_label として記録する (§4)。
/// 窓 (analysis_window_*) は probe_triggered から受領した値をそのまま転記する (DB-4)。
#[allow(clippy::too_many_arguments)]
#[tauri::command]
fn record_realtime_answer(
    probe_id: Option<String>,
    source: String,
    q1_friction: u8,
    q2_progress: u8,
    latency_ms: u64,
    window_start_ms: u64,
    window_end_ms: u64,
    log: State<'_, Arc<Mutex<LogState>>>,
) -> Result<(), String> {
    // ⚠️★★★ **O1 では被験者由来のラベル行を記録しない** (2026-08-31)。
    //   ★ `record_self_marker` と**同じ判断・同じ純関数**を共有する
    //     (⚠️ 1 つだけ塞ぐと「塞いだつもり」になる —— 2026-08-30 の事故がその形だった)。
    //   ⚠️ UI 側だけの対処に頼らない: 次に UI をいじった人が黙って穴を開け直す。
    if !crate::o1::label_row_allowed(crate::o1::is_o1()) {
        tracing::warn!(
            "{}: ignored in O1 mode (the O1 consent form does not list this row). \
             This is a gate, not a failure.",
            "record_realtime_answer"
        );
        return Ok(());
    }
    let probe = build_probe_ref(&source, probe_id)?;
    if window_end_ms < window_start_ms {
        return Err("window_end_ms must be >= window_start_ms".to_string());
    }
    log.lock()
        .unwrap_or_else(|p| p.into_inner())
        .tx
        .try_send(LogEntry::realtime_label_answered(
            epoch_ms(),
            &probe,
            q1_friction,
            q2_progress,
            latency_ms,
            window_start_ms,
            window_end_ms,
        ))
        .map_err(log_send_error)?;
    Ok(())
}

/// v0.3 較正: プローブ skip を realtime_label として記録する (§4・§10 MNAR)。
#[tauri::command]
fn record_realtime_skip(
    probe_id: Option<String>,
    source: String,
    skip_reason: String,
    latency_ms: u64,
    window_start_ms: u64,
    window_end_ms: u64,
    log: State<'_, Arc<Mutex<LogState>>>,
) -> Result<(), String> {
    // ⚠️★★★ **O1 では被験者由来のラベル行を記録しない** (2026-08-31)。
    //   ★ `record_self_marker` と**同じ判断・同じ純関数**を共有する
    //     (⚠️ 1 つだけ塞ぐと「塞いだつもり」になる —— 2026-08-30 の事故がその形だった)。
    //   ⚠️ UI 側だけの対処に頼らない: 次に UI をいじった人が黙って穴を開け直す。
    if !crate::o1::label_row_allowed(crate::o1::is_o1()) {
        tracing::warn!(
            "{}: ignored in O1 mode (the O1 consent form does not list this row). \
             This is a gate, not a failure.",
            "record_realtime_skip"
        );
        return Ok(());
    }
    let probe = build_probe_ref(&source, probe_id)?;
    if window_end_ms < window_start_ms {
        return Err("window_end_ms must be >= window_start_ms".to_string());
    }
    let skip_reason = SkipReason::parse(&skip_reason)
        .ok_or_else(|| format!("invalid skip_reason: {:?}", skip_reason))?;
    if matches!(skip_reason, SkipReason::None) {
        return Err("skip_reason must be dont_remember or dismissed".to_string());
    }
    log.lock()
        .unwrap_or_else(|p| p.into_inner())
        .tx
        .try_send(LogEntry::realtime_label_skipped(
            epoch_ms(),
            &probe,
            skip_reason,
            latency_ms,
            window_start_ms,
            window_end_ms,
        ))
        .map_err(log_send_error)?;
    Ok(())
}

/// 「今とても詰まっている」ワンタップ自己ラベルの単一実装。
/// Dashboard ボタン (`record_self_marker` コマンド)・D ホットキーの両経路がこれを呼び、
/// **`LAST_SELF_MARKER_MS` デバウンスを共有**して多重記録を防ぐ (M カード式マーカーとも共有)。
/// 多段カード (M) と違いカードを出さず即記録する (ESM 単一・低負荷)。
/// `source=self_marker`・Stuck 象限 (q1_friction=5/q2_progress=1) の自己申告ラベル。
/// 窓は self_marker_window_clamped (直前 ~30s、session_start でクランプ)。本文は含まない。
/// 戻り値: 記録したら true、デバウンス/送信失敗で false。
fn record_self_marker_inner(now: u64, tx: &Sender<LogEntry>) -> bool {
    // ボタン(IPC スレッド)と D/M ホットキー(別スレッド)が同時に呼びうるため、
    // load+store では二重記録の race がある。compare_exchange で原子的に「枠を予約」する
    // (LAST_LABEL_MS と同流儀)。CAS 失敗 = 他経路が先に取った → スキップ。
    let last = LAST_SELF_MARKER_MS.load(Ordering::Relaxed);
    if now.saturating_sub(last) < MARKER_DEBOUNCE_MS {
        return false;
    }
    if LAST_SELF_MARKER_MS
        .compare_exchange(last, now, Ordering::Relaxed, Ordering::Relaxed)
        .is_err()
    {
        return false;
    }
    let session_start = SESSION_START_MS.load(Ordering::Acquire);
    let (ws, we) = crate::analysis::probe_scheduler::self_marker_window_clamped(now, session_start);
    if let Err(e) = tx.try_send(LogEntry::realtime_label_answered(
        now,
        &ProbeRef::SelfMarker,
        5, // q1_friction: とても詰まった
        1, // q2_progress: まったく進んでいない
        0, // latency_ms: ワンタップ (即時)
        ws,
        we,
    )) {
        tracing::warn!("self marker send failed (label dropped): {}", e);
        return false;
    }
    tracing::info!("self marker (one-tap stuck) recorded at {}", now);
    true
}

/// 「今とても詰まっている」ワンタップ自己ラベル (Dashboard ボタン経路)。
/// D ホットキーと同じ `record_self_marker_inner` を呼びデバウンスを共有する。
/// 戻り値: 実際に記録したら true、デバウンスで弾かれたら false (UI 側は true の時だけ確認表示)。
#[tauri::command]
fn record_self_marker(log: State<'_, Arc<Mutex<LogState>>>) -> Result<bool, String> {
    // ⚠️★★★ **O1 では記録しない** (2026-08-30)。
    //   ★ O1 のグローバルショートカットを登録しない判断と**同じ理由**である。逐語:
    //     「could write user_label / review_marker rows that **the consent form does not list**」
    //   ⚠️ 旧実装はホットキーだけを塞ぎ、**Dashboard のボタンは素通り**だった
    //     (★ 2026-08-30 に実機の画面を見て発見。⚠️ 機械検査は 1 つも捕まえなかった)。
    //   ★ **UI 側だけで隠さない**: 隠し忘れ / 将来の UI 変更 / IPC の直叩きでも
    //     ここが最後の門になる (`data-privacy`: 同意範囲の外へ出る経路は backend で閉じる)。
    //   ★ 判定は純関数 `o1::self_marker_allowed` に委譲する (⚠️ `O1_MODE` は OnceLock で
    //     テストから切り替えられないため。`analysis_gate_open` / `decide_probe_init` と同じ形)。
    if !crate::o1::self_marker_allowed(crate::o1::is_o1()) {
        tracing::warn!(
            "record_self_marker ignored: O1 mode does not collect self labels \
             (the O1 consent form does not list this row). This is a gate, not a failure."
        );
        return Ok(false);
    }
    let tx = log.lock().unwrap_or_else(|p| p.into_inner()).clone_log_tx();
    Ok(record_self_marker_inner(epoch_ms(), &tx))
}

/// v0.3 較正: 尺度理解テスト (ビネット) 回答を記録する (§6・§14)。
/// vignette_id は不透明 ID のみ・q1/q2 は構築子で 1..=5 clamp (DC-4)。
#[tauri::command]
fn record_vignette_response(
    vignette_id: String,
    expected_quadrant: String,
    q1_friction: u8,
    q2_progress: u8,
    elapsed_ms: u64,
    changes: u16,
    log: State<'_, Arc<Mutex<LogState>>>,
) -> Result<(), String> {
    // ⚠️★★★ **O1 では被験者由来のラベル行を記録しない** (2026-08-31)。
    //   ★ `record_self_marker` と**同じ判断・同じ純関数**を共有する
    //     (⚠️ 1 つだけ塞ぐと「塞いだつもり」になる —— 2026-08-30 の事故がその形だった)。
    //   ⚠️ UI 側だけの対処に頼らない: 次に UI をいじった人が黙って穴を開け直す。
    if !crate::o1::label_row_allowed(crate::o1::is_o1()) {
        tracing::warn!(
            "{}: ignored in O1 mode (the O1 consent form does not list this row). \
             This is a gate, not a failure.",
            "record_vignette_response"
        );
        return Ok(());
    }
    let quadrant = ExpectedQuadrant::parse(&expected_quadrant)
        .ok_or_else(|| format!("invalid expected_quadrant: {:?}", expected_quadrant))?;
    if !is_valid_opaque_id(&vignette_id) {
        return Err("invalid vignette_id format".to_string());
    }
    log.lock()
        .unwrap_or_else(|p| p.into_inner())
        .tx
        .try_send(LogEntry::vignette_response(
            epoch_ms(),
            vignette_id,
            quadrant,
            q1_friction,
            q2_progress,
            elapsed_ms,
            changes,
        ))
        .map_err(log_send_error)?;
    Ok(())
}

/// overlay (macOS は NSPanel) のクリック受理を切り替える (decisions D9)。
/// `interactive=true` でカードがクリックを捕捉、`false` で背後アプリへ透過。
/// macOS は `ignoresMouseEvents` を panel に Rust 権威で設定する (JS の setIgnoreCursorEvents は
/// NSPanel 化窓で実効しないため)。非 macOS は従来の set_ignore_cursor_events に委譲 (Windows 非回帰)。
#[tauri::command]
fn set_overlay_interactive(app: tauri::AppHandle, interactive: bool) -> Result<(), String> {
    #[cfg(target_os = "macos")]
    {
        if let Err(e) = crate::overlay_panel::set_panel_interactive(&app, interactive) {
            tracing::error!("set_panel_interactive failed: {}", e);
            return Err(e);
        }
    }
    #[cfg(not(target_os = "macos"))]
    {
        match app.get_webview_window("overlay") {
            Some(win) => win
                .set_ignore_cursor_events(!interactive)
                .map_err(|e| e.to_string())?,
            // macOS 経路 (get_webview_panel 失敗) と成否契約を揃える: overlay 窓が無い
            // (setup 失敗等) と box のクリック処理が無音で効かなくなるため可視化する
            // (code-reviewer 指摘)。Windows 非回帰のため Err には倒さず warn に留める。
            None => tracing::warn!("set_overlay_interactive: overlay window not found"),
        }
    }
    Ok(())
}

/// G1: 他の GSE プロセスが動いていないかを OS に聞き、見つかったら画面へ出す (別スレッド)。
///
/// ⚠️ ★ **同期に呼んではならない。** 2026-08-06 に実測した (macOS 26.5.2・5 回):
/// `/usr/bin/pgrep` の子プロセス起動に **28.2 / 19.0 / 18.8 / 18.5 / 18.1 ms**。
/// ★ Windows の `tasklist.exe` は **未計測**である (この環境からは測れない)。
/// → ★ `start_session` の応答に載せると「開始する」の反応が鈍る。応答は先に返し、
///   検査は別スレッドで走らせて **結果だけを emit** する (待たせない・止めない)。
///
/// ★ 止めずに画面へ出すのは `setup()` 側と同じ方針である (列挙の失敗や名前の一致ミスで
/// 実施を潰さないため。判断は人に返す)。フロントの `second-instance-blocked` は
/// `setDuplicateBlocked(true)` で冪等なので、複数回来ても害はない。
fn spawn_duplicate_instance_check(app: tauri::AppHandle, delay: Duration, when: &'static str) {
    thread::spawn(move || {
        if !delay.is_zero() {
            thread::sleep(delay);
        }
        if crate::g1::other_instance_running() {
            tracing::error!(
                "G1: ANOTHER GSE PROCESS IS RUNNING ({}). Keystrokes will be split across \
                 two NDJSON files (protocol.md 2-3). Quit the other one.",
                when
            );
            let _ = app.emit("second-instance-blocked", ());
        }
    });
}

/// ログ channel に `needed` 通ぶんの空きがあるか。
///
/// ⚠️★ **`try_send` してから失敗を拾うのでは遅い**場面がある (`start_session` は巻き戻せない
/// 副作用を先に出す)。★ そこで**送る前に**空きを見る。
///
/// `capacity()` は bounded なら必ず `Some` を返す (`logger.rs` の `bounded(512)`)。
/// ⚠️ 万一 `None` (unbounded) なら常に空きがあるとみなす。
///
/// ## ⚠️★★★ これは **予約ではなく確認**である (Codex MEDIUM・2026-08-19)
///
/// 空きを見てから実際に送るまでのあいだに**他の送信者 (分析スレッド等) が割り込める**ので、
/// ★ **原子的な保証にはならない**。→ 「`Rotate` は通ったが `SessionStart` だけ落ちる」は
/// **確率が下がるだけで消えない**。
/// ⚠️ だから送信側の失敗処理 (`Rotate` は fail-loud で中止 / `SessionStart` は `ERROR` ログ) を
/// **省いてはならない**。★ 本関数の役目は「巻き戻せない副作用を出す前に、
/// **明らかに詰まっているとき**を弾く」ことだけである。
fn log_channel_has_room(tx: &Sender<LogEntry>, needed: usize) -> bool {
    match tx.capacity() {
        Some(cap) => cap.saturating_sub(tx.len()) >= needed,
        None => true,
    }
}

/// 「開始する」ボタン押下時に呼ばれる。
/// 1. セッションアクティブフラグをセット (分析スレッドのドレインを終了)
/// 2. CognitiveStateEngine を初期状態にリセット
/// 3. 分析スレッドの FeatureExtractor リセットを要求 (AtomicBool シグナル)
/// 4. LogEntry::SessionStart をログに記録
#[tauri::command]
fn start_session(
    app: tauri::AppHandle,
    engine: State<CognitiveStateEngine>,
    session_active: State<SessionActive>,
    reset_signal: State<ResetSignal>,
    latest_feat: State<LatestFeatState>,
    intervention: State<InterventionState>,
    log: State<Arc<Mutex<LogState>>>,
) -> Result<(), String> {
    // ⚠️★★★ **O1 では「開始する」を受け付けない** (cross-review / Codex HIGH・2026-08-27)。
    //
    // ★ UI 側では判定が済むまでスタート画面を出さない (fail-closed) が、
    //   ⚠️ **IPC は残っている**ので、将来の UI 変更や直接呼び出しで到達しうる。
    //   → ★ `submit_latest_session` と同じく **両方で塞ぐ**。
    //
    // ⚠️★★★ 到達したときの帰結が重い: `SESSION_START_MS` が立つが、
    //   **O1 にはブロック自動終了スレッドが無い** (`if g1_mode().is_some()` の中でしか起きない)
    //   ので **0 に戻す経路が存在しない**。→ `spawn_reconcile_with_guard` が
    //   「ブロック中なので走らせない」で **プロセスの寿命いっぱい skip し続け、
    //   自動提出が黙って止まる**。
    if crate::o1::is_o1() {
        tracing::warn!("O1: start_session rejected (recording is always on in O1 mode)");
        return Err("この記録は常に動いています。開始の操作は要りません。".to_string());
    }

    // ★★ G1: 参加者 ID が無いまま**ブロックを始めさせない** (`requirement.md` 受け入れ条件 1)。
    //
    // ⚠️ ★ **何も触る前に**返す。ここから先はログのローテートまで進むので、途中で止めると
    //   `G1_BLOCKS_STARTED` と実ファイルがずれる。
    // ⚠️ ★ 通常運用 (マーカー無し) は `g1_start_gate` が必ず `Ok` を返す = 非回帰。
    // ★ フロントもボタンを無効化するが、**バックエンド側にも置く** (二重 gate)。
    //   フロントだけだと DevTools から直接 invoke できてしまい、
    //   ID 無しの `.age` が誰のものか分からないまま研究者に届く。
    crate::submission::g1_start_gate(
        g1_mode().is_some(),
        crate::submission::read_g1_participant_id().as_deref(),
    )?;

    // ⚠️★★★ **ブロック遷移の排他をここで取る** (D-1・2026-08-21)。
    //
    // ★ ここから `SESSION_START_MS.store(now)` までが**ひと続き**になる。
    //   ⚠️ そうしないと「`Rotate` は送られたが `SESSION_START_MS` はまだ 0」という窓が残り、
    //   ブロック自動終了スレッドの `BlockEnd` が**新しいファイルへ `session_end` を書く**
    //   (`logger.rs` の `Rotate` が `block_closed` を `false` に戻すため)。
    //
    // ⚠️★★ **ログのロックより前に取る。** ロック順序は
    //   `BLOCK_TRANSITION` → `latest_feat` → `intervention` → `log` で固定してある。
    // ⚠️ 自動終了スレッドがアイドル待ち中なら最大 1500 ms 待たされるが、
    //   ★ その待ちは「押下を待たせている」のではなく「**押下が壊れないように待たせている**」。
    // ★ 途中の `return` でも RAII で必ず解放される。オーバーレイの `win.show()` の
    //   **前**に明示的に `drop` する (ロック中にウィンドウ操作をしない・follow-up F-2 と同じ判断)。
    let block_transition = lock_block_transition();

    // ⚠️★★★ **「触る前に断る」** (G-1・2026-08-19)。
    //
    // ★ ここから下の `engine.reset()` / `reset_signal` / `latest_feat` / `intervention` は
    //   `swap` より**前**に置かなければならない (下のコメント参照: 分析スレッドとの可視性順序)。
    //   → ⚠️ したがって**それらを実行した後に送信が失敗しても巻き戻せない**。
    //   ★ そこで「これから最大 2 通 (`Rotate` + `SessionStart`) 送る」ぶんの空きを、
    //     **状態を 1 つも触る前に**確かめて、足りなければここで断る。
    // ⚠️ 残る失敗は `Disconnected` (ロガースレッドが死んでいる) だけで、それはどの道記録できない。
    //
    // ⚠️★★★ **G1 モードのときだけ検査する。** 通常運用では `Rotate` を送らないので
    //   「2 通の途中で切れる」失敗様式がそもそも無く、★ ここで弾くと
    //   **これまで開始できていた場面で開始できなくなる** = 既定の挙動の変更になる
    //   (研究者決定 #2「リブートの範囲は計器＋運用」の外)。
    if g1_mode().is_some() {
        let guard = log.lock().unwrap_or_else(|p| p.into_inner());
        if !log_channel_has_room(&guard.tx, 2) {
            tracing::error!("start_session: log channel is full; refusing to start a block");
            return Err("ログの書き込みが詰まっています。ブロックを開始できません。\
                 このブロックはまだ始まっていません。少し待ってからもう一度「開始する」を押してください。"
                .to_string());
        }
    }

    // リセットシグナルを先にセットしてからセッションを有効化する。
    // 分析スレッドが active=true を Acquire で読んだ時点で、
    // それより前に Release された reset=true も可視であることが保証される。
    // 逆順だと、分析スレッドが active=true を見た瞬間に reset がまだ false で、
    // 前セッションの沈黙時間が初回更新に混入するレースコンディションが発生する。
    engine.reset();
    reset_signal.0.store(true, Ordering::Release);
    // ★ 旧値を取る。⚠️ 既に true (= 連打・record_session_meta 失敗後の再押下) なら
    //   **新しいブロックではない**。
    // ⚠️★★★ **2026-08-19 に意味が変わった (G-1)。** 従来はこの場合「何もしない」＝
    //   ローテートせずに `SessionStart` だけを積んでいたため、**1 ファイルに 2 セッション**が
    //   入った (P010 block07 で実発生・`protocol.md §1` の破れ)。
    //   → ★ いまは **`RotateForRestart`** として「前を閉じてから新しいファイルを開く」。
    //   ★ ただし **数えない** ので、code-review HIGH の指摘 (無条件に数えると孤児が増える) は
    //   引き続き満たしている。判定は `g1::decide_start_action` を見ること。
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    // ⚠️★ **ログのロックより前に**済ませる。★ `intervention` → `log` の順で取る箇所が
    //   既にある (デバッグ強制系の周辺) ので、ここで `log` → `intervention` と
    //   入れ子にすると**ロック順序が反転**する。→ 入れ子にしない。
    *latest_feat.0.lock().unwrap_or_else(|p| p.into_inner()) = None;
    *intervention.0.lock().unwrap_or_else(|p| p.into_inner()) = InterventionPolicyState::new(now);
    // ★ ロックは**ログへ送る間だけ**保持する (follow-up F-2 / code-review LOW)。
    //   以前は `win.show()` を含む関数末尾まで持っていた。デッドロックはしないが、
    //   ⚠️ ロック中にウィンドウ操作 (別スレッドへ波及しうる) を行う形は残さない。
    let was_active;
    {
        let guard = log.lock().unwrap_or_else(|p| p.into_inner());

        // ⚠️★★★ **`swap` はログのロックの *中* で行う** (2026-08-19・G-1 の詰め)。
        //
        // ★ 「開始する」は送信中に disabled にならないので、**2 回続けて押すと
        //   `start_session` が並行に走りうる**。`swap` だけでは
        //   「どちらが新規か」は決まるが、⚠️ **ログへ書く順序までは決まらない**。
        //   → 素直に書くと次の交錯が残る:
        //     A(新規) が swap → B(再押下) が swap → **B が先にロックを取って
        //     ローテート** → B が `SessionStart` → **その後 A が `SessionStart`**
        //     ＝ ⚠️ **新しいファイルに `session_start` が 2 本**（P010 block07 と同じ形）。
        // ★ ロックの中で swap すれば「誰が新規か」と「何を書くか」が**同時に**決まるので、
        //   押した順に file1 → (閉じる) → file2 と必ず 1 本ずつになる。
        was_active = session_active.0.swap(true, Ordering::Release);

        // ★ G1: ログのローテート方針は**純関数** `g1::decide_start_action` が決める
        //   (1 ブロック = NDJSON 1 ファイル・protocol.md §1)。効果だけをここで適用する。
        //   ⚠️ ★ **G1 モードでないときは何もしない。** 通常運用 (Phase1) では「戻る → 開始する」で
        //   ファイルが分かれてしまうと、`gse-submit` が最新 1 本しか出さないため
        //   **前半が提出されなくなる**。既定の挙動を 1 バイトも変えないこと。
        // ⚠️★ **`!was_active` の枝は従来のまま**である。そこに置かれた
        //   「無条件に**数える**と孤児ファイルが 1 本増える」(code-review HIGH) という指摘は
        //   ★ **数えることへの指摘**なので、数えない `RotateForRestart` とは両立する。
        let action = crate::g1::decide_start_action(
            g1_mode().is_some(),
            was_active,
            G1_BLOCKS_STARTED.load(Ordering::Acquire),
            SESSION_META_RECORDED.load(Ordering::Acquire),
        );

        // ⚠️★★★ **`record_session_meta` 失敗後の再押下では、ログを 1 行も書かない。**
        //   ★ 書くと (a) ローテートすれば**中身がほぼ空の孤児ファイル**が 1 本増え、
        //   (b) ローテートしなければ**同じファイルに 2 本目の `session_start`** が入る。
        //   ⚠️ (a) は `has_any_data_row` では止まらない (`session_start` 行があるファイルは通る)。
        //   → ★ 何も書かずに戻り、フロントに `record_session_meta` を再試行させる。
        if !action.writes_session_start() {
            tracing::info!(
                "G1: start pressed again before session_meta was recorded; \
                 not touching the log (retry path)"
            );
            // ★ ここで抜けるので `SESSION_START_MS` は**引き直さない**
            //   (ブロックの 5 分は 1 回目の押下から数える = ログの `session_start` と一致する)。
            //   ★ オーバーレイも 1 回目で既に出ている。
            return Ok(());
        }

        // ★ これから新しい (または開き直した) ブロックが始まる。握手はこれからなので落とす。
        // ⚠️★★ **旧値を控えておく** (code-reviewer HIGH・2026-08-21)。
        //   ★ 下の `Rotate` 送信が失敗したとき、ここを `false` にしたままにすると
        //     次の押下が `decide_start_action(g1, was_active=true, _, meta_recorded=false)`
        //     → **`RetryAfterMetaFailure`** に落ちる。⚠️ その経路は `Ok(())` を返すのに
        //     **ログを 1 行も書かず restart もしない**ので、フロントは `record_session_meta` へ進み、
        //     ⚠️★★★ **旧ファイルに 2 本目の `session_meta`** が入る (`protocol.md §1` の破れ)。
        //   ★ `session_active` を枝ごとに戻しているのと同じ形で、ここも戻す。
        let meta_recorded_before = SESSION_META_RECORDED.swap(false, Ordering::AcqRel);
        // ★ カウンタは「新しいブロックを始めた」経路だけが進める。
        //   ⚠️★★★ 二度押し (`RotateForRestart`) は**増やさない** —— 数えると
        //   code-review HIGH が指摘した「孤児ファイルを 1 本増やす」形に戻る。
        let blocks_started = if action.counts_block() {
            G1_BLOCKS_STARTED.fetch_add(1, Ordering::AcqRel) + 1
        } else {
            G1_BLOCKS_STARTED.load(Ordering::Acquire)
        };

        // ★ `Rotate` 1 通で「前を閉じる → 新ファイル → `meta`」が全部済む
        //   (`logger.rs` の `Rotate` 処理が `write_meta_end` → `open_log_target` →
        //   `write_meta_start` を順に行う)。★ 失敗した試行も別ファイルとして残る (捨てない)。
        if action.rotates() {
            let reason = if action == crate::g1::StartAction::RotateForRestart {
                "restart while active (G-1)".to_string()
            } else {
                format!("block #{blocks_started}")
            };
            // ⚠️ ファイル名は秒粒度。衝突回避は **logger スレッド側**でも行う
            // (ここは別スレッドなので exists 判定と create の間に窓がある・code-review MEDIUM)。
            let new_path = logger::next_session_path();
            tracing::info!("G1: rotating session log ({}) -> {:?}", reason, new_path);
            if let Err(e) = guard.tx.try_send(LogEntry::Rotate { new_path }) {
                // ⚠️★★ **ここで進んではならない** (cross-review HIGH・Claude と Codex が一致)。
                // channel (bounded 512) が満杯だと Rotate だけが落ち、直後の SessionStart 以降が
                // **既に `session_end` を書き終えた旧ファイル**に積まれる。
                // = protocol.md §1 が (b) を却下した「沈黙して間違った結果を出す」失敗そのもの。
                // ★ 上の容量ガードでほぼ到達しないが、**到達したら必ず止める**。
                tracing::error!("G1: FAILED to rotate session log: {}", log_send_error(e));
                if action == crate::g1::StartAction::RotateForNewBlock {
                    G1_BLOCKS_STARTED.fetch_sub(1, Ordering::AcqRel);
                }
                // ⚠️★★★ **巻き戻し方が枝で違う。**
                //   `RotateForNewBlock`: このブロックは始まっていない → `false` に戻す。
                //   `RotateForRestart` : ★ **`true` のままにする** —— 前のセッションは
                //     まだ開いており計測も続いている。`false` にすると
                //     「`session_end` の無い開きっぱなしのファイル」を計測停止扱いにしてしまう。
                if action != crate::g1::StartAction::RotateForRestart {
                    session_active.0.store(false, Ordering::Release);
                }
                // ⚠️★★★ **握手の状態も戻す** (code-reviewer HIGH・2026-08-21)。
                //   ★ 戻さないと `RotateForRestart` の失敗後に `RetryAfterMetaFailure` へ落ち、
                //     **旧ファイルに 2 本目の `session_meta`** が入る。
                //   ★ 戻せば次の押下は同じ `RotateForRestart` として**素直に再試行**される
                //     (文言「もう一度『開始する』を押してください」と一致する)。
                SESSION_META_RECORDED.store(meta_recorded_before, Ordering::Release);
                return Err("ログの切り替えに失敗しました。ブロックを開始できません。\
                     このブロックはまだ始まっていません。もう一度「開始する」を押してください。"
                    .to_string());
            }
        }

        // ⚠️★★ **落ちたことを黙らせない** (code-reviewer MEDIUM・2026-08-19)。
        //   `Rotate` は成功したのに `SessionStart` が落ちると、新ファイルは `meta` だけを持ち
        //   `session_start` を持たない。★ `validate_blocks.py` は **0 本を FAIL にしない**設計
        //   (旧版のログを赤にしないため) なので、⚠️ **黙って通ってしまう**。
        //   ★ ここまで来ると巻き戻せないので `Err` は返さず、診断ログに必ず残す。
        if let Err(e) = guard.tx.try_send(LogEntry::SessionStart { timestamp: now }) {
            tracing::error!(
                "FAILED to record session_start: {} \
                 (the block will look like it never started)",
                log_send_error(e)
            );
        }
    }

    // ★ G1: **ブロックを始めるたびに**二重起動を見に行く (follow-up F-1 / code-review M6)。
    //   ⚠️ 従来は起動 1.5 秒後の 1 回だけだったので、★ **G1 アプリを開いた後に**
    //   被験者が旧アプリ (Phase1 用 `/Applications`) を開くと、警告が出ないまま
    //   打鍵が 2 本の NDJSON に割れた (protocol.md §2-3)。
    //   ★ 応答時間には載せない (上の `spawn_duplicate_instance_check` の実測コメント参照)。
    if g1_mode().is_some() && !was_active {
        spawn_duplicate_instance_check(app.clone(), Duration::ZERO, "at block start");
    }

    // Task B: プローブスケジューラへセッション開始時刻を共有する。
    // 専用スレッドが値の変化を検出してスケジューラを再初期化する。
    // M0 (D1): session_start を公開した時点では SESSION_META_FOR_START_MS はまだこの世代を指さない
    // (前セッションの値 or 0)。スケジューラは session_start と meta 世代を照合してから初期化するため、
    // record_session_meta が来るまで較正プロファイル選択は確定しない (race 排除)。明示リセットは不要
    // (世代照合が staleness を吸収する)。
    SESSION_START_MS.store(now, Ordering::Release);

    // ⚠️★★★ **ここでブロック遷移の排他を離す** (D-1)。
    //   ★ `Rotate` / `SessionStart` の送信と `SESSION_START_MS` の更新が
    //     ひと続きで済んだので、自動終了スレッドはこの先で
    //     `decide_block_end` の照合により `Superseded` を返して**中止する**。
    //   ⚠️ 下の `win.show()` は**ロックの外**で行う (ロック中にウィンドウ操作をしない)。
    drop(block_transition);

    // setup() で事前生成されたオーバーレイウィンドウを show する (サイズ制御は Overlay.tsx)。
    // ウィンドウ生成自体は setup() (メインスレッド) で行うことで、
    // Windows での tokio ワーカースレッドからの WebviewWindowBuilder::build()
    // デッドロックを回避する。
    if let Some(win) = app.get_webview_window("overlay") {
        // macOS: overlay は NSPanel 化済み (decisions D7)。`maximize()` は内部で `setStyleMask:` を
        // 呼び、panel に載る WKWebView の contentLayoutRect オブザーバ解除に失敗して NSRangeException で
        // クラッシュする (実機確認・D8)。全画面化は Overlay.tsx 側が明示 setSize/setPosition (モニタ全域)
        // で行うため、ここでは show() のみ (JS を起こす目的)。透明窓なので一瞬の表示は不可視。
        let _ = win.show();
        tracing::info!("Overlay window shown");
    } else {
        tracing::error!("Overlay window not found — setup() may have failed");
    }
    Ok(())
}

/// アプリ終了。終了前に以下を順に実行する:
///   1. セッションログを閉じる (LogEntry::End を送信)
///   2. shutdown_rx でロガー完了を待機 (固定 sleep の代わり)
///   3. behavioral_gt.py でラベリング分析を実行 (Python が PATH にある場合)
///   4. セッションフォルダを Explorer で開く
#[tauri::command]
fn quit_app(app: tauri::AppHandle, log: State<Arc<Mutex<LogState>>>) {
    shutdown(&app, &log);
}

/// 終了処理が始まっているか。★ トレイの更新スレッドが抜けるために見る。
pub(crate) fn is_shutting_down() -> bool {
    SHUTTING_DOWN.load(Ordering::SeqCst)
}

/// 終了処理の権利を取る。★ 最初の 1 回だけ `true` を返す。
///
/// ⚠️ 終了の入口は 4 つある（画面の「セッション終了」/ スタート画面の「GSE を終了」/
/// トレイの「終了」/ main 窓の ×）。二重に入ると、ログを閉じる待ち合わせが二重になり
/// `exit(0)` が競合する。
///
/// ★ フラグを**引数で受ける**ので単体で検算できる（グローバルだとテスト順に依存する）。
fn claim_shutdown(flag: &AtomicBool) -> bool {
    !flag.swap(true, Ordering::SeqCst)
}

/// 終了時に「分析を起動してセッションフォルダを開く」かどうか。
///
/// ⚠️★ **G1（被験者の端末）ではやらない。** 被験者の画面に NDJSON の並んだフォルダが
/// 開くのは混乱のもとであり、`behavioral_gt.py` も被験者の端末には無い。
///
/// ⚠️★ **セッションパスが空のときもやらない。** ロガーが開けていない場合に空文字が来ると、
/// `Path::new("").parent()` は `Some("")` を返すので、★ **意図しないフォルダを開く**
/// (2026-08-08 の cross-review。★ スタート画面に終了ボタンを足して
/// 「セッション未開始のまま終了する」経路が現実的になったので、ここを塞ぐ)。
fn wants_researcher_exit_flow(not_g1: bool, session_path: &str) -> bool {
    not_g1 && !session_path.trim().is_empty()
}

/// ★ 終了経路の**唯一の実装**。
///
/// ⚠️ 以前は `quit_app`（画面の「セッション終了」）だけがここを通っていた。
/// トレイの「終了」と main 窓の × も**同じ道**を通す — 経路ごとに書くと、
/// ★ どれか 1 つだけ「ログを閉じずに落ちる」ようになる（静かに壊れる）。
///
/// `AppHandle` から State を引くので、コマンド以外からも呼べる。
pub(crate) fn shutdown_and_exit(app: &tauri::AppHandle) {
    let log = app.state::<Arc<Mutex<LogState>>>();
    shutdown(app, &log);
}

fn shutdown(app: &tauri::AppHandle, log: &Arc<Mutex<LogState>>) {
    if !claim_shutdown(&SHUTTING_DOWN) {
        tracing::info!("shutdown already in progress; ignoring the second request");
        return;
    }
    tracing::info!("shutdown requested");

    // ログ終了マーカーを送信し、shutdown_rx を取得
    let (session_path, shutdown_rx) = {
        let guard = log.lock().unwrap_or_else(|p| p.into_inner());
        let _ = guard.tx.try_send(LogEntry::End);
        (guard.current_path(), guard.shutdown_rx.clone())
    };

    let researcher_flow = wants_researcher_exit_flow(g1_mode().is_none(), &session_path);

    let app_handle = app.clone();

    // バックグラウンドスレッドで分析→フォルダ表示→アプリ終了
    thread::spawn(move || {
        // ロガースレッドのファイルクローズを channel で安全に待機 (最大2秒)
        let _ = shutdown_rx.recv_timeout(Duration::from_millis(2000));

        if researcher_flow {
            // behavioral_gt.py を探して実行
            match find_behavioral_gt() {
                Some(script) => {
                    tracing::info!("Auto-analysis: python {:?} {}", script, session_path);
                    match std::process::Command::new("python")
                        .args([script.to_str().unwrap_or(""), &session_path])
                        .spawn()
                    {
                        Ok(_) => tracing::info!("behavioral_gt.py launched"),
                        Err(e) => tracing::warn!("Failed to launch behavioral_gt.py: {}", e),
                    }
                    // Python 分析に少し時間を与えてから Explorer を開く
                    thread::sleep(std::time::Duration::from_millis(1500));
                }
                None => {
                    tracing::warn!(
                        "behavioral_gt.py not found. Skipping auto-analysis. \
                         Run manually: python analysis/behavioral_gt.py {}",
                        session_path
                    );
                }
            }

            // セッションフォルダをファイルマネージャで開く
            if let Some(folder) = Path::new(&session_path).parent() {
                tracing::info!("Opening session folder: {:?}", folder);
                #[cfg(target_os = "windows")]
                {
                    let _ = std::process::Command::new("explorer").arg(folder).spawn();
                }
                #[cfg(target_os = "macos")]
                {
                    let _ = std::process::Command::new("open").arg(folder).spawn();
                }
            }
        } else {
            tracing::info!(
                "G1 mode: skipping auto-analysis and the folder popup (participant-facing exit)"
            );
        }

        thread::sleep(std::time::Duration::from_millis(200));
        app_handle.exit(0);
    });
}

// ---------------------------------------------------------------------------
// behavioral_gt.py の場所を探す
// ---------------------------------------------------------------------------

/// 実行ファイルの上位ディレクトリを最大5段階遡って analysis/behavioral_gt.py を探す。
/// 開発時は CWD が gse-prototype-v2/GSE-Next なので ./analysis/ が見つかる。
fn find_behavioral_gt() -> Option<PathBuf> {
    // まず CWD 基準で探す
    let cwd_candidate = PathBuf::from("analysis/behavioral_gt.py");
    if cwd_candidate.exists() {
        return Some(cwd_candidate);
    }

    // 次に実行ファイルの上位ディレクトリを遡って探す
    if let Ok(exe) = std::env::current_exe() {
        let mut dir = exe.parent()?.to_path_buf();
        for _ in 0..5 {
            let candidate = dir.join("analysis").join("behavioral_gt.py");
            if candidate.exists() {
                return Some(candidate);
            }
            if let Some(parent) = dir.parent() {
                dir = parent.to_path_buf();
            } else {
                break;
            }
        }
    }

    None
}

// ---------------------------------------------------------------------------
// Phase 2b: IME Shadow Features (★ 両 OS)
// ---------------------------------------------------------------------------

/// IME Shadow の Atomic データを読み取り、LogEntry::ImeShadow を送出する。
///
/// ⚠️★★★ **2026-09-11 (issue 008): `#[cfg(target_os = "windows")]` を外した。**
/// ★ macOS 側も `input/ime_compose.rs::drive` が同じ Atomic を駆動する。
/// ⚠️ **駆動源は OS で違う** (Windows = 窓イベント / macOS = 打鍵の状態機械)。
/// 由来の非対称は `capabilities` (ADR-013) と `meta` 行の OS で判別する。
///
/// 2 つの経路で emit が発生する:
/// 1. 正常: `IME_SHADOW_READY=true` → dwell は事前計算済み
///    (Windows = WinEvent IME_HIDE / cloak resolver、macOS = 終端キー)
/// 2. Stale: IME_HIDE が取りこぼされ safety valve のタイムアウト
///    (`input::ime_cloak::MONITOR_SAFETY_VALVE_MS`) → START_MS > 0 なら独自に dwell 計算
///
/// ⚠️★★★ **経路 2 は Windows 限定である** —— ★ 呼び出し側の `#[cfg]` がそれを固定する。
/// macOS の `IME_ACTIVE` は「候補表示中に別の字を打った」「Backspace」でも false に落ちるが、
/// それは**セッションの途中**なので、そこで経路 2 に入ると
/// ⚠️ **途中の偽の行を出したうえ `START_MS` を 0 にしてセッションを壊す**。
fn emit_ime_shadow(log_tx: &Sender<LogEntry>, timestamp: u64) {
    use std::sync::atomic::Ordering::Relaxed;
    // ⚠️★ G1: この経路は IME Monitor スレッドから呼ばれ、**`session_active` を見ていない**
    // (code-review HIGH)。ブロックを閉じた後に IME の後始末が飛んでくると
    // `session_end` の後ろに `ime_shadow` 行が続く。
    // ★ G1 モードのときだけ止める (通常運用の挙動は変えない)。
    // `SESSION_START_MS` はブロック終了時に 0 に戻されるので、これが「ブロック中か」を表す。
    if g1_mode().is_some() && SESSION_START_MS.load(Ordering::Acquire) == 0 {
        // ⚠️★★★ **捨てることを明示する** (2026-09-11・review MEDIUM)。
        //   ★ 旧実装はここで素通しており、`IME_SHADOW_READY` が立ったまま残った。
        //   ⚠️ すると**ブロック外で閉じた変換**が、次ブロック開始後の最初のポーリングで
        //   **「いまの時刻」で 1 行出る** —— G1 は `t` でブロックを切り分けるので、
        //   ★ 前ブロックの変換が次ブロックの記録に混ざる。
        //   ⚠️ `START_MS` も落とす (残すと stale 経路が同じ変換をもう一度出す)。
        input::hook::IME_SHADOW_READY.store(false, Ordering::Release);
        input::hook::IME_COMPOSITION_START_MS.store(0, Relaxed);
        return;
    }
    if input::hook::IME_SHADOW_READY.swap(false, Ordering::AcqRel) {
        // 正常経路: IME_HIDE で dwell 計算済み
        let dwell_ms = input::hook::IME_SHADOW_DWELL_MS.swap(0, Relaxed);
        let candidate_nav_count = input::hook::IME_CANDIDATE_NAV_COUNT.swap(0, Relaxed);
        let abandon = input::hook::IME_SHADOW_ABANDON.swap(false, Relaxed);
        let _ = log_tx.try_send(LogEntry::ImeShadow {
            timestamp,
            dwell_ms,
            candidate_nav_count,
            abandon,
        });
    } else {
        // Stale 経路: IME_HIDE が来なかった場合のフォールバック
        //
        // ⚠️★★★ **Windows 限定である。** ★ 2026-09-11 まで、この不変条件は
        //   「呼び出し側の `#[cfg]` が固定する」という**コメントだけ**で守られていた。
        //   ⚠️ しかし本体は両 OS でコンパイルされ、READY ポーリング経路は両 OS から呼ぶ。
        //   → 将来 macOS の呼び出し点が 1 つ増えた瞬間に、
        //   **セッション途中で `START_MS` を 0 にする偽の行**が macOS で出る。
        //   ★ 不変条件をコメントからコードへ移す (review MEDIUM)。
        #[cfg(target_os = "windows")]
        {
            let start = input::hook::IME_COMPOSITION_START_MS.swap(0, Relaxed);
            if start > 0 {
                let dwell_ms = timestamp.saturating_sub(start);
                let candidate_nav_count = input::hook::IME_CANDIDATE_NAV_COUNT.swap(0, Relaxed);
                let abandon = input::hook::IME_SHADOW_ABANDON.swap(false, Relaxed);
                let _ = log_tx.try_send(LogEntry::ImeShadow {
                    timestamp,
                    dwell_ms,
                    candidate_nav_count,
                    abandon,
                });
            }
        }
    }
}

// ---------------------------------------------------------------------------
// アプリ起動
// ---------------------------------------------------------------------------

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // ★ `tracing` を stdout **と** ファイルの両方へ流す (`applog` のモジュールコメント参照)。
    //   ⚠️ 旧 `tracing_subscriber::fmt::init()` は stdout だけで、Finder 起動の `.app` では
    //   どこにも残っていなかった (2026-08-08 に実測)。
    crate::applog::init_tracing(&crate::logger::app_log_path());

    // ★ G1 モードの判定 — **起動時に 1 回だけ**読む (g1.rs のモジュールコメント参照)。
    //   実行時トグルにすると、プローブスケジューラを「スレッドごと起こさない」ことで
    //   「発火はしたが黙殺した」を構造的に消している設計 (下の kill switch) が崩れる。
    let g1_source = crate::g1::detect_from_env();
    G1_MODE
        .set(g1_source.map(|s| s.as_str()))
        .expect("G1_MODE is set exactly once in run()");
    if let Some(src) = g1_source {
        tracing::warn!(
            "G1 MODE ENABLED (source={}): session log rotates per block, blocks auto-end at {} ms, \
             probe scheduler will NOT start. \
             See experiments/20260801-controlled-friction-task/preregistration.md 5.4.",
            src.as_str(),
            crate::g1::BLOCK_DURATION_MS
        );
    }

    // ★ O1 モード (R3-a・自然作業の常時収集) の判定 —— **起動時に 1 回だけ**読む。
    //   ⚠️★★★ **G1 と同時には立てない** (`o1::resolve` が G1 を勝たせる)。理由は
    //   `preregistration.md §3.6` がブロックの事後除外を禁じており、G1 の 1 ブロックは
    //   **取り返しがつかない**ためである。★ 起動そのものは止めない (g1.rs の倒し方と同じ)。
    let o1_detected = crate::o1::detect_from_env();
    if crate::o1::modes_conflict(g1_source, o1_detected) {
        // ⚠️★★★ 事故だが**静かに壊れてはならない**。診断ログに必ず残す。
        tracing::error!(
            "BOTH g1.mode and o1.mode are present in the distribution folder \
             (g1={:?}, o1={:?}). O1 mode is DISABLED and this run behaves as G1. \
             Remove one marker; a G1 block cannot be excluded after the fact \
             (preregistration.md 3.6).",
            g1_source,
            o1_detected
        );
    }
    let o1_source = crate::o1::resolve(g1_source, o1_detected);
    crate::o1::set_mode(o1_source);
    if let Some(src) = o1_source {
        tracing::warn!(
            "O1 MODE ENABLED (source={}): recording runs WITHOUT pressing start \
             (ADR-016 4b-0), the session log rotates every {} ms, closed logs are held \
             {} ms before submission, and interventions are OFF. \
             See docs/adr/ADR-014-continuous-natural-work-collection.md D6/D8.",
            src.as_str(),
            crate::o1::ROTATE_AFTER_MS,
            crate::o1::SUBMIT_GRACE_MS
        );
        // ⚠️★★★ **判断 O1-5: O1 では介入を出さない。**
        //   ★ 既定値は `true` (下の `INTERVENTION_ENABLED`) で、O1 は
        //   `record_session_meta` を通らないので **何もしなければ Nudge が出る**。
        //   → ★ ここで明示的に落とす。理由は (1) 介入が入ると自然作業ではなくなる
        //   (観測している行動を介入が変える) (2) 同意文書に「助言が出ることがある」旨が無い。
        INTERVENTION_ENABLED.store(false, Ordering::Release);
    }

    // セッションロガー — ★ **ここではまだ NDJSON を作らない** (follow-up F-3)。
    //
    // ⚠️ ★ `tauri-plugin-single-instance` に止められた 2 個目のプロセスは、止められる前に
    //   NDJSON を作ってから死ぬ (実測で 0 行のファイル・decisions R-8 結果 4)。
    //   `gse-submit` は最新 1 本を選ぶので、★ 被験者が「提出する」を押すと空の `.age` が出る。
    // ★ 一次資料 (`tauri` 2.10.2 `src/app.rs`) で確認した順序:
    //   プラグインの `exit(0)` は `Builder::build()` 末尾の `initialize_plugins` で走り、
    //   **`.setup()` クロージャはその後の `App::run()` の中**で呼ばれる。
    //   → ★ 実際にファイルを開くのは `.setup()` の中 (`log_channel.start(..)`)。
    //   ここでは channel と共有ハンドルだけを作り、スレッド群に配る。
    let log_path = logger::default_log_path();
    let log_path_str = log_path.to_string_lossy().to_string();
    tracing::info!("Session log (will open in setup): {}", log_path_str);

    let log_channel = logger::LogChannel::new();
    let log_tx = log_channel.tx.clone();
    let log_shutdown_rx = log_channel.shutdown_rx.clone();
    // ★ G1: ブロックが `session_end` まで書けたことの合図 (自動提出の起点を正しくするため)。
    let block_end_ack_rx = log_channel.block_end_rx.clone();
    // ★ 書込先はローテートで変わる。値をコピーせず共有ハンドルを配る。
    //   `start()` が**この同じ Arc を上書き**するので、`.manage()` の順序は変えなくてよい。
    let log_target = log_channel.target.clone();

    // LogState を Arc<Mutex> でラップして Tauri state に渡す
    let log_state = Arc::new(Mutex::new(LogState {
        tx: log_tx.clone(),
        target: log_target.clone(),
        shutdown_rx: log_shutdown_rx,
    }));
    // ★ O1 (R3-a): 日次ローテートスレッド用 (⚠️ O1 モードでしか起こさない)。
    //   ★ `o1_rotate` は `start_session` と同じく **ログのロックの中**で
    //   `Rotate` → `SessionMeta` を送るので、`LogState` そのものが要る。
    let o1_log_state = log_state.clone();

    // キーストローク入力チャネル
    let (tx, rx) = crossbeam_channel::bounded::<crate::analysis::features::InputEvent>(64);

    // セッション開始リセットシグナル (start_session → 分析スレッド)
    let should_reset = Arc::new(AtomicBool::new(false));
    let should_reset_for_thread = should_reset.clone();
    // ★ O1 (R3-a): 日次ローテートスレッド用 (⚠️ O1 モードでしか起こさない)。
    let should_reset_for_o1 = should_reset.clone();

    // セッションアクティブフラグ (start_session まで false → 分析スレッドがドレイン)
    let session_active = Arc::new(AtomicBool::new(false));
    let session_active_for_thread = session_active.clone();
    // ★ G1: ブロック自動終了スレッド用 (5 分でブロックを閉じる)。
    let session_active_for_g1 = session_active.clone();
    // ★ トレイの状態表示用 (1Hz で読むだけ・書かない)。
    let session_active_for_tray = session_active.clone();
    // ★★ フック生存監視スレッド用 (`input::liveness`)。
    let session_active_for_liveness = session_active.clone();

    let initial_now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    let latest_feat = Arc::new(Mutex::new(None));
    let latest_feat_for_thread = latest_feat.clone();
    let intervention_state = Arc::new(Mutex::new(InterventionPolicyState::new(initial_now)));

    // エンジン初期化
    let engine = CognitiveStateEngine::new();
    let engine_for_thread = engine.clone();
    // ★ O1 (R3-a): 日次ローテートスレッド用 (⚠️ O1 モードでしか起こさない)。
    let engine_for_o1 = engine.clone();
    // ⚠️★ IME Monitor 用の clone は **2026-08-23 に不要になった** ——
    //   IME で `set_paused` を駆動しなくなったため (decisions D-10)。
    let log_tx_ime_poll = log_tx.clone();
    let log_tx_for_monitor = log_tx.clone();
    let log_tx_probe = log_tx.clone();
    let log_tx_g1 = log_tx.clone();
    let log_tx_liveness = log_tx.clone();
    // ★ O1 (R3-a): 非打鍵チャネルのドレインスレッド用。
    let log_tx_for_observe = log_tx.clone();
    let log_tx_analysis = log_tx;

    // 分析スレッド
    //
    // 独立1Hzゲートアーキテクチャ:
    //   recv_timeout のタイムアウトを「次の1Hzマークまでの残り時間」に動的調整し、
    //   イベントの有無に関わらず正確な ~1Hz 間隔で HMM 推論を実行する。
    //   next_engine_update += 1s (絶対時刻ベース) で累積ドリフトを防止する。
    //
    //   イベント処理 (process_event, register_keystroke, ログ記録) は到着次第即座に行う。
    //   HMM 推論は 1Hz ゲートでのみ実行し、Time Dilation を防ぐ。
    //
    // Silence-break protection:
    //   10秒以上の沈黙後、1-2回の孤立打鍵では last_event_time をリセットしない。
    //   3回以上の連続打鍵が確認されて初めて「タイピング復帰」と判定する。
    //   これにより沈黙中に蓄積した Stuck 状態が1打鍵で消失する問題を防止する。
    thread::spawn(move || {
        use crate::analysis::loop_step::{step, AnalysisState, LoopInput};

        tracing::info!("Analysis thread started");

        // 壁時計 ms を統一時刻表現として使用する (判断 13)。
        // step() 内部の silence 計算・1Hz ゲート進行・Feat ログ timestamp、
        // さらに gse-replay が NDJSON の `t` を再生する際の基準まで、
        // すべて同じ表現で揃えることで production と replay の挙動を一致させる。
        let now_ms = || -> u64 {
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_millis() as u64
        };

        let mut state = AnalysisState::new(now_ms(), 600);

        // ⚠️★★★ O1 (R3-a): **門を外すかどうかは起動時に決まる** (`o1::mode` は OnceLock)。
        //   ★ ループの中で毎回読まず、ここで 1 回だけ確定させる (実行時トグルではない)。
        let o1_always_on = crate::o1::is_o1();

        loop {
            // start_session が呼ばれるまでチャネルをドレインして処理をスキップする。
            // ⚠️★★★ O1 では門を通す (ADR-016 判断 4b-0 の「(B) 常時収集」)。
            //   ★ `LogEntry::Key` はこのループの**中でしか出ない**ので、門を外さないと
            //   打鍵チャネルが丸ごと空になり、⚠️ **計器の欠損が「非打鍵区間」に化ける**。
            //   ★ 非 O1 では `session_active` そのものなので G1 / Phase1 は 1 バイトも変わらない。
            if !crate::o1::analysis_gate_open(
                o1_always_on,
                session_active_for_thread.load(Ordering::Acquire),
            ) {
                while rx.try_recv().is_ok() {}
                // ★ G1: 「もうこのスレッドは LogEntry を投げない」ことの表明。
                //   ブロック終了スレッドがこれを観測してから session_end を書く。
                ANALYSIS_IDLE.store(true, Ordering::Release);
                thread::sleep(Duration::from_millis(50));
                continue;
            }
            // ★ ここから先は Key/Feat を送りうる。**recv_timeout に入る前に**表明を降ろす。
            ANALYSIS_IDLE.store(false, Ordering::Release);

            // start_session コマンドによるリセット要求をチェック
            if should_reset_for_thread.swap(false, Ordering::AcqRel) {
                state.reset(now_ms(), 600);
            }

            // 動的タイムアウト: 次の 1Hz マークまでの残り時間
            let current = now_ms();
            let remaining_ms = state.next_engine_update_ms.saturating_sub(current);
            let timeout = Duration::from_millis(remaining_ms.max(1));

            // イベント受信 (タイムアウトは次の 1Hz マークまで)
            let input = match rx.recv_timeout(timeout) {
                Ok(event) => {
                    // ペーストイベント (Ctrl+V / Cmd+V) を NDJSON に記録する。
                    // フック層は VK + 修飾キー状態のみから is_paste を立てる。
                    // (b) 自力解決率 (v0.4 manual_contribution_ratio) 向けに、フック外 (本スレッド)
                    // でクリップボードの**文字数のみ**を**同期**取得する (CD1)。中身は
                    // clipboard_char_count 内で数えた直後に破棄され、保存・送信しない (data-privacy)。
                    //
                    // 同期読みにする理由 (cross-review HIGH 対応・CD5 改訂): クリップボード読みを
                    // 別スレッドへ逃がすと (1) ペースト連打で thread が無制限に積まれる、
                    // (2) 直後に session End が来ると paste 行が無音で欠落する race、
                    // (3) 検出〜読取の間にクリップボードが変わる TOCTOU 窓が広がる、の 3 つを招く。
                    // 研究用の捕捉では「正確さ > 数 ms のレイテンシ」。同期読みなら 3 問題とも消え、
                    // 代償は稀なクリップボード競合時の僅かな 1Hz tick 遅延のみ (30s 窓では無視可能)。
                    // LogEntry 変換を analysis/ の外で行い architecture-rules ルール6 を守る。
                    if event.is_paste {
                        let external_paste_chars = crate::input::clipboard::clipboard_char_count();
                        let _ = log_tx_analysis.try_send(LogEntry::Paste {
                            timestamp: event.timestamp,
                            external_paste_chars,
                        });
                    }
                    Some(LoopInput::Key(event))
                }
                Err(RecvTimeoutError::Timeout) => None,
                Err(RecvTimeoutError::Disconnected) => break,
            };

            // step() 本体は analysis/loop_step.rs に抽出済み。
            // リピート検出・IME ポーズ分岐・silence-break protection・
            // 1Hz ゲート・沈黙 3 状態機構・Feat 生成をすべて担う。
            // tick_now を 1 度だけ取り step に渡す（code-reviewer 指摘: タイミング一貫性）。
            let tick_now = now_ms();
            let ime_open = input::hook::IME_OPEN.load(Ordering::Acquire);
            let out = step(&mut state, &engine_for_thread, input, tick_now, ime_open);

            // 中立記録型 → LogEntry 変換（architecture-rules ルール 6 遵守のため、
            // LogEntry への変換は analysis/ の外で行う）
            if let Some(k) = out.key {
                let _ = log_tx_analysis.try_send(LogEntry::Key {
                    vk_code: k.vk_code,
                    timestamp: k.timestamp,
                    is_press: k.is_press,
                });
            }
            if let Some(f) = out.feat {
                *latest_feat_for_thread
                    .lock()
                    .unwrap_or_else(|p| p.into_inner()) = Some(f.clone());
                let _ = log_tx_analysis.try_send(LogEntry::Feat {
                    timestamp: f.timestamp,
                    f1: f.f1,
                    f3: f.f3,
                    f4: f.f4,
                    f5: f.f5,
                    f6: f.f6,
                    p_flow: f.p_flow,
                    p_inc: f.p_inc,
                    p_stuck: f.p_stuck,
                    raw_x: f.raw_x,
                    raw_y: f.raw_y,
                    ewma_x: f.ewma_x,
                    ewma_y: f.ewma_y,
                    obs: f.obs,
                    alpha: f.alpha,
                    // ★ Tier 0 (記録のみ): 打鍵数をそのまま NDJSON へ。推論には使わない。
                    keys: f.keys,
                    bs_keys: f.bs_keys,
                });
            }
        }
    });

    // IME モニタースレッド
    thread::spawn(move || {
        tracing::info!("IME Monitor thread started");
        let monitor = input::ime::ImeMonitor::new();
        // IME_ACTIVE が true になった時刻。`MONITOR_SAFETY_VALVE_MS` 以上続いたら
        // EVENT_OBJECT_IME_HIDE 取りこぼしと判断してフラグを自動リセットする。
        let mut ime_active_since: Option<Instant> = None;
        // IME_ACTIVE 変更検出: 状態が変化した際に ImeState ログを送出
        let mut last_active: Option<bool> = None;
        loop {
            let active = monitor.is_candidate_window_open();

            // Safety valve: EVENT_OBJECT_IME_HIDE はフォーカス変更やクラッシュ時に
            // 取りこぼすことがある。IME_ACTIVE が `MONITOR_SAFETY_VALVE_MS` 以上
            // true のままなら stale とみなしてリセットする。
            if active {
                let since = ime_active_since.get_or_insert_with(Instant::now);
                // ⚠️★★★ **2026-08-23: 8 秒 → 25 秒。**
                //   ★ 旧値 8 秒は「候補ウィンドウ表示は数秒以内」という前提だったが、
                //   ⚠️ 実測でこの信号は **変換セッション全体** を覆い、
                //   自然な打鍵で **6974ms** の区間が出た。★ 8 秒では実データを切る。
                //   ⚠️ `CloakFold::MAX_SESSION_MS` (20 秒) より**外側**に置くこと ——
                //   内側にすると fold より先に発火して **1 変換で 2 行**出る
                //   (★ `ime_cloak.rs` の `MAX_SESSION_MS` doc を参照)。
                //   ★ pause を外した (上記) ので、長く立ちっぱなしでも推論は止まらない。
                // ⚠️★★★ **値は `ime_cloak::MONITOR_SAFETY_VALVE_MS` から導出する。**
                //   ★ ここに数値をハードコードすると、あちらの `const _: () = assert!()` が
                //   **同じファイル内の 2 定数を比べるだけ**になり、
                //   ⚠️ 「fold が valve の内側で発火する」不変条件が**黙って破れる**
                //   (2026-08-23・cross-review HIGH)。
                if since.elapsed()
                    > Duration::from_millis(input::ime_cloak::MONITOR_SAFETY_VALVE_MS)
                {
                    tracing::warn!(
                        valve_ms = input::ime_cloak::MONITOR_SAFETY_VALVE_MS,
                        "IME_ACTIVE stale — auto-resetting"
                    );
                    input::hook::IME_ACTIVE.store(false, Ordering::Release);
                    ime_active_since = None;
                    // ⚠️★ `set_paused(false)` は呼ばない —— ★ IME で pause しなくなったので
                    //   ここで解除するものが無い (上のコメント / decisions D-10)。
                    last_active = Some(false);
                    let ts = std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_millis() as u64;
                    let ime_on = input::hook::IME_OPEN.load(Ordering::Acquire);
                    let _ = log_tx_for_monitor.try_send(logger::LogEntry::ImeState {
                        timestamp: ts,
                        on: ime_on,
                        active: false,
                    });
                    // Phase 2b: stale リセット時も shadow データを emit
                    #[cfg(target_os = "windows")]
                    emit_ime_shadow(&log_tx_for_monitor, ts);
                    thread::sleep(std::time::Duration::from_millis(100));
                    continue;
                }
            } else {
                ime_active_since = None;
            }

            // IME_ACTIVE 状態変化時にログを送出（初回は必ず emit）
            if last_active.is_none_or(|prev| prev != active) {
                // ⚠️ 使用箇所 (下の `emit_ime_shadow`) が Windows 限定なので、束縛も同じ
                //    `#[cfg]` に揃える (macOS では unused variable になる)。
                // ★ **対の関係**: 使用側の `#[cfg]` を外すならこの束縛も外すこと
                //   (外し忘れると macOS で「未定義の変数」として**即コンパイルエラー**になる
                //    ＝ 黙って壊れないので安全側だが、原因が分かるように書いておく)。
                #[cfg(target_os = "windows")]
                let was_active = last_active.unwrap_or(false);
                last_active = Some(active);
                let ts = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis() as u64;
                let ime_on = input::hook::IME_OPEN.load(Ordering::Acquire);
                let _ = log_tx_for_monitor.try_send(logger::LogEntry::ImeState {
                    timestamp: ts,
                    on: ime_on,
                    active,
                });
                // Phase 2b: active→false 遷移時に IME Shadow データを emit
                #[cfg(target_os = "windows")]
                if was_active && !active {
                    emit_ime_shadow(&log_tx_for_monitor, ts);
                }
            }

            // Phase 2b: IME_SHADOW_READY の直接ポーリング
            // is_candidate_window_open() 内の safety valve が IME_ACTIVE を即座に
            // リセットするため、Monitor が active→false 遷移を観測できないケースがある。
            // WinEvent IME_HIDE は正しく READY を set するので、遷移に依存せず
            // READY フラグを毎ポーリングでチェックする。
            //
            // ⚠️★★★ **2026-09-11 (issue 008): ここだけ `#[cfg]` を外した。**
            //   ★ macOS で `ime_shadow` が出るのは**この経路だけ**である
            //     (上の 2 つ = stale valve / active→false 遷移 は Windows 限定のまま)。
            //   ⚠️ 理由は `emit_ime_shadow` の doc —— macOS の `IME_ACTIVE` は
            //     セッション途中でも false に落ちるので、遷移で emit すると記録が壊れる。
            //   ★ この経路は `READY` が立っているときしか `emit_ime_shadow` を呼ばないので、
            //     Windows 限定の stale 経路 (`START_MS > 0` 分岐) には入らない。
            if input::ime_compose::should_drain_ready(
                input::hook::IME_SHADOW_READY.load(Ordering::Acquire),
                active,
                cfg!(target_os = "windows"),
            ) {
                let ts = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis() as u64;
                emit_ime_shadow(&log_tx_for_monitor, ts);
            }

            // ⚠️★★★ **2026-08-23: IME による推論の一時停止を止めた (研究者判断)。**
            //
            // ★ 旧コードはここで `engine.set_paused(active)` を呼んでいた。
            //   意図は「候補選択中の打鍵で推定を汚さない」であり、⚠️ **その意図は正しい**。
            //
            // ⚠️★★★ **しかし実測で、この信号は「候補リスト表示」ではなく
            //   「IME 変換セッション全体 (ローマ字入力〜確定)」を覆うことが分かった。**
            //   ★ 自然な打鍵 60 秒 (打鍵 281) での uncloaked 区間:
            //   6464 / 5714 / 5004 / 3456 / 6974 / 3279 ms —— ★ 候補を眺める時間ではない。
            //   ★ 打鍵中のサンプルの **69% が uncloaked** (実測G)。
            //
            // → ⚠️★★★ **これで pause すると、日本語論述の推定窓が約 56〜60% 消える。**
            //   ★ G1 の主タスクは日本語論述なので、較正データを半分以上捨てることになる。
            //   ⚠️ 引き継ぎ §3.2 の「15〜20%」は、信号を候補表示だと誤解していた時の見積り。
            //
            // ★ **決定 (研究者・2026-08-23)**: **記録はする。pause はしない。**
            //   ⚠️ `analysis/loop_step.rs` の replay 経路も**同時に外してある**
            //   (★ 外さないと live と replay が食い違い Replay-as-Truth が壊れる)。
            //
            // ★ 詳細: `.steering/20260823-ime-active-cloak-rewiring/decisions.md` D-10。
            thread::sleep(std::time::Duration::from_millis(100));
        }
    });

    // キーボードフック・IME ポーリングの Sender を setup() に渡すために保持。
    // フックは Tauri 初期化完了後 (setup() 内) でインストールする。
    // Tauri の run() がウィンドウシステム・tokio ランタイム・WebView2 を初期化するため、
    // それ以前にフックをインストールすると、初期化過程でフックが無効化される。
    let hook_tx = tx;
    let ime_poll_log_tx = log_tx_ime_poll;

    // Phase 1 Ground Truth: グローバルホットキーのハンドラが使うための LogState clone。
    // プラグインのハンドラ(Fn)は Send + Sync が必要なので、Arc<Mutex<LogState>> を
    // move で持ち込む。
    let log_state_for_shortcut = log_state.clone();

    let builder = tauri::Builder::default();

    // ★★ 二重起動の検出。**公式文書の指示どおり最初に登録する**
    //    (「The Single Instance plugin must be the first one to be registered to work well」)。
    //
    // ⚠️ ★ なぜ要るか (2026-08-05 の実測・decisions R-7):
    //    `/Applications/gse-next.app` と G1 フォルダのコピーは **同じ bundle ID でも
    //    別プロセスとして平然と共存し、NDJSON が 2 本に割れた**。
    //    ★ 「macOS は 2 個目のインスタンスを起動しない」は **この形では成立しない**。
    //    2 つが同時に走ると両方がキーボードを掴み、打鍵が 2 本に分かれる (protocol.md §2-3)。
    //
    // 2 個目のプロセスはプラグインが終了させ、このコールバックは **1 個目**で走る。
    // ★ 黙って前面に出すだけにしない: 画面へ通知して fail-loud にする
    //   (被験者から見ると「開いたのに何も起きない」ため、理由が分からないと詰む)。
    let builder = builder.plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
        tracing::warn!(
            "second instance launch detected and blocked (G1: two instances would split keystrokes \
             across two NDJSON files; see protocol.md 2-3)"
        );
        if let Some(win) = app.get_webview_window("main") {
            let _ = win.show();
            let _ = win.set_focus();
        }
        let _ = app.emit("second-instance-blocked", ());
    }));

    // macOS: overlay 窓を非アクティブ NSPanel 化するためのプラグイン (decisions D7)。
    // crate 自体が macОS 限定依存のため登録も cfg ゲートする。
    #[cfg(target_os = "macos")]
    let builder = builder.plugin(tauri_nspanel::init());
    builder
        .plugin(tauri_plugin_opener::init())
        .plugin(
            tauri_plugin_global_shortcut::Builder::new()
                .with_handler(move |app, shortcut, event| {
                    use tauri_plugin_global_shortcut::{Code, Modifiers, ShortcutState};
                    if event.state() != ShortcutState::Pressed {
                        return;
                    }
                    #[cfg(target_os = "macos")]
                    let mods = Modifiers::SUPER | Modifiers::SHIFT | Modifiers::ALT;
                    #[cfg(not(target_os = "macos"))]
                    let mods = Modifiers::CONTROL | Modifiers::SHIFT | Modifiers::ALT;
                    // ReviewMarker は認知状態ラベルではなくブックマーク。
                    // UserLabel とは別経路で処理する。
                    if shortcut.matches(mods, Code::KeyR) {
                        let now = std::time::SystemTime::now()
                            .duration_since(std::time::UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_millis() as u64;
                        // 1 秒デバウンス (連打防止)
                        let last = LAST_MARKER_MS.load(std::sync::atomic::Ordering::Relaxed);
                        if now.saturating_sub(last) < MARKER_DEBOUNCE_MS {
                            return;
                        }
                        LAST_MARKER_MS.store(now, std::sync::atomic::Ordering::Relaxed);
                        let _ = log_state_for_shortcut
                            .lock()
                            .unwrap_or_else(|p| p.into_inner())
                            .tx
                            .try_send(logger::LogEntry::ReviewMarker { timestamp: now });
                        tracing::info!("review marker recorded at {}", now);
                        return;
                    }
                    // Task B: 自己マーカー (副データ)。被験者が「今 Stuck」と感じた瞬間に押す。
                    // probe_id=null・source=self_marker で probe_triggered を emit する。
                    // realtime_label のログ自体は Task C の回答コマンドが行う (B は窓を確定して渡すまで)。
                    if shortcut.matches(mods, Code::KeyM) {
                        let now = std::time::SystemTime::now()
                            .duration_since(std::time::UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_millis() as u64;
                        let last = LAST_SELF_MARKER_MS.load(std::sync::atomic::Ordering::Relaxed);
                        if now.saturating_sub(last) < MARKER_DEBOUNCE_MS {
                            return;
                        }
                        LAST_SELF_MARKER_MS.store(now, std::sync::atomic::Ordering::Relaxed);
                        // DB-8 を self_marker にも適用: 窓始端を session_start でクランプし、
                        // 開始前/前セッションの打鍵が分析窓に混入するのを防ぐ。
                        let session_start =
                            SESSION_START_MS.load(std::sync::atomic::Ordering::Acquire);
                        let (ws, we) = crate::analysis::probe_scheduler::self_marker_window_clamped(
                            now,
                            session_start,
                        );
                        let _ = app.emit(
                            "probe_triggered",
                            serde_json::json!({
                                "probe_id": serde_json::Value::Null,
                                "source": "self_marker",
                                "analysis_window_start_ms": ws,
                                "analysis_window_end_ms": we,
                            }),
                        );
                        tracing::info!("self marker probe_triggered at {}", now);
                        return;
                    }
                    // ワンタップ「今とても詰まっている」self_marker。カードを出さず即記録する
                    // (M=カード式と別)。Stuck 象限 (q1=5/q2=1)。ボタン経路と共通の inner を呼び
                    // デバウンス (LAST_SELF_MARKER_MS) を共有する。
                    if shortcut.matches(mods, Code::KeyD) {
                        let tx = log_state_for_shortcut
                            .lock()
                            .unwrap_or_else(|p| p.into_inner())
                            .clone_log_tx();
                        record_self_marker_inner(epoch_ms(), &tx);
                        return;
                    }
                    let label = if shortcut.matches(mods, Code::KeyF) {
                        UserLabelKind::Flow
                    } else if shortcut.matches(mods, Code::KeyI) {
                        UserLabelKind::Incubation
                    } else if shortcut.matches(mods, Code::KeyS) {
                        UserLabelKind::Stuck
                    } else {
                        return;
                    };
                    match record_label_internal(&log_state_for_shortcut, label) {
                        Ok(ts) => {
                            let _ = app.emit(
                                "user_label_recorded",
                                serde_json::json!({
                                    "label": label.as_str(),
                                    "timestamp": ts,
                                }),
                            );
                        }
                        Err(e) => {
                            tracing::warn!("shortcut label recording failed: {}", e);
                        }
                    }
                })
                .build(),
        )
        .setup(move |app| {
            // ★★ セッションログのファイルを**ここで初めて開く** (follow-up F-3)。
            //
            // ⚠️ ★ ここに来ている = **single-instance プラグインに止められなかった** ということ
            //   である (プラグインの `exit(0)` は `Builder::build()` の中で走り、この
            //   クロージャは `App::run()` の中で呼ばれる。一次資料: `tauri` 2.10.2 `src/app.rs`)。
            //   → ★ 2 個目のプロセスは **NDJSON を作らずに死ぬ**。
            // ⚠️ これは提出側の `has_any_data_row` を**置き換えるものではない**。
            //   起動直後のクラッシュ等でも空ファイルは出るので、両方残す。
            // ⚠️★★★ **ロガーを起こす *前* にレイアウトを解決する。**
            //
            // ★ `meta`(session_start) はロガースレッドが**起動直後に書く**ので、
            //   後から `set_keyboard_layout_id` を呼んでも**間に合わない**
            //   (2026-08-23 に実機で確認: `keyboard_layout` が meta に載らなかった)。
            // ⚠️ 識別子のみ。★ 文字変換 (`ToUnicodeEx` / `UCKeyTranslate`) は呼ばない。
            //   ⚠️ 取れなければ `meta` にフィールドを出さない (0 値で埋めない・ADR-013 D1)。
            if let Some(layout) = input::observe::keyboard_layout_id() {
                tracing::info!(keyboard_layout = %layout, "O1: keyboard layout recorded");
                logger::set_keyboard_layout_id(layout);
            }

            let (session_logger, log_status) = log_channel.start(log_path, g1_source);
            if log_status != LogStatus::Ok {
                tracing::error!(
                    "Session log status is not Ok: {:?} (intended {})",
                    log_status,
                    log_path_str
                );
            }
            // `SessionLogger` を drop すると JoinHandle が detach されるだけで、
            // consumer スレッドは走り続ける (従来 `run()` 末尾での drop と同じ挙動)。
            drop(session_logger);

            // ── ⚠️★★★ O1 (R3-a): 日次ローテート (判断 O1-2 の実施条件 1) ──────────
            //
            // ★ **閉じないファイルは提出候補にならない。** `write_meta_end`(`session_end`) は
            //   **Rotate / BlockEnd (G1 限定) / アプリ終了**でしか書かれず、⚠️ O1 は
            //   「開始する」を押さないので、**アプリを終了しない被験者のファイルは何日も
            //   開いたまま**になる (`reconcile` は `session_end` を持つファイルしか触らない)。
            //
            // ⚠️ **O1 モードでしか起こさない。** ★ 通常運用 / G1 のログは 1 行も動かない。
            if crate::o1::is_o1() {
                let now = epoch_ms();
                O1_LOG_OPENED_MS.store(now, Ordering::Release);
                let o1_log = o1_log_state;
                let o1_engine = engine_for_o1;
                let o1_reset = ResetSignal(should_reset_for_o1);
                let o1_app = app.handle().clone();
                thread::spawn(move || {
                    tracing::info!("O1 daily-rotate thread started");
                    loop {
                        // ★ 60 秒粒度で足りる (24 時間に対して 0.07%)。⚠️ スリープからの復帰でも
                        //   epoch ms の差で判定するので、寝ていたぶんも経過に入る。
                        thread::sleep(Duration::from_secs(60));
                        if is_shutting_down() {
                            tracing::info!("O1 daily-rotate thread stopping (shutdown)");
                            return;
                        }
                        let opened = O1_LOG_OPENED_MS.load(Ordering::Acquire);
                        if opened == 0 {
                            continue;
                        }
                        if !crate::o1::should_rotate_daily(
                            opened,
                            epoch_ms(),
                            crate::o1::ROTATE_AFTER_MS,
                        ) {
                            continue;
                        }
                        // ⚠️★★★ **止めているあいだは回さない。** ★ 止めている間は 1 行も
                        //   書かれないので閉じる意味が無く、`SessionMeta` だけが停止ゲートに
                        //   落ちて**宣言が黙って失われる**。再開後の tick で必ず拾われる。
                        if crate::recording::is_paused() {
                            continue;
                        }
                        // ⚠️★★★ **宣言を捏造しない。** 未宣言のまま日をまたいだファイルには
                        //   `session_meta` を書かない (判断 4b-3: 行の**不在**で未宣言を表す)。
                        //   ★ 宣言済みなら書き直す —— `engine.reset()` が head を Writing に
                        //   戻すので、⚠️ 書き直さないと**翌日から宣言が黙って失われる**。
                        //   ★ 現在値の読みは `o1_rotate` がロックの中で行う (交錯を避けるため)。
                        if let Err(e) = o1_rotate(
                            &o1_log,
                            &o1_engine,
                            &o1_reset,
                            O1Declaration::KeepCurrent,
                            "daily rotation",
                        ) {
                            // ⚠️ 失敗しても基準は引き直さない → 次の tick で再試行する
                            //   (★ 収束型。1 回落ちても翌分で拾う)。
                            tracing::error!("O1: daily rotation failed: {e}");
                            continue;
                        }
                        // ★ 1 本閉じたので収束器を回す。⚠️ いま閉じたファイルは猶予の中なので
                        //   **まだ包まれない** —— 拾われるのは **48 時間前に閉じた分**である。
                        spawn_reconcile(o1_app.clone(), ReconcileReason::O1DailyRotation);
                    }
                });
            }

            // --- キーボードフック・IME ポーリングの初期化 ---
            // Tauri の setup() はメインスレッドで、Tauri ランタイム初期化完了後に実行される。
            // ウィンドウシステムが完全に初期化された後にフックをインストールすることで、
            // Tauri 初期化がフックを無効化する問題を回避する。

            // IME open ポーリングスレッド (wake-on-keystroke + VK_DBE_* fallback)
            let (poll_wake_tx, poll_wake_rx) = crossbeam_channel::bounded::<()>(1);
            input::hook::set_poll_wake_sender(poll_wake_tx);
            input::ime::spawn_ime_open_polling_thread(ime_poll_log_tx, poll_wake_rx);

            // ⚠️★★★ cloak resolver スレッド (Windows 限定・2026-08-23)。
            //   ★ この Windows 11 の IME 候補 UI は `ShowWindow` ではなく **DWM の
            //   cloak/uncloak** で表示制御されており、文書化された
            //   `EVENT_OBJECT_IME_*`(0x8027-29) は実測で 1 件も飛ばない。
            //   → ★ cloak を第 2 の駆動源にする (`input/ime_cloak.rs` のモジュール doc)。
            //   ⚠️ **`init_hook` より前に呼ぶこと** —— チャネルの送信端が
            //   `CLOAK_EVENT_TX` に載る前にフックが飛ぶと、その分を取りこぼす。
            #[cfg(target_os = "windows")]
            input::ime::spawn_cloak_resolver_thread();

            // キーボードフック開始 (set_poll_wake_sender の後に呼ぶこと)
            let _hook_started = input::hook::init_hook(hook_tx);

            // ── ⚠️★★★ O1 (R3-a): 非打鍵チャネル (ADR-014 D4 の段 1) ──────────────
            //
            // ★ **記録のみ。推論には 1 バイトも流さない** (ADR-014 **D4b**)。
            //   → ⚠️ ここで作るチャネルは `logger` へ直行し、`analysis` を**通らない**。
            //   ★ Tier 0 配線 (`keys` / `bs_keys`) と同じ形である。
            //
            // ⚠️ 容量を大きめ (256) に取る理由: ★ ドレインは 1 本のスレッドが回すが、
            //   フォアグラウンド遷移は**まとめて飛ぶ**ことがある (ウィンドウの復元時など)。
            //   ⚠️ 溢れたぶんは `observe::OBSERVATIONS_DROPPED` が数える (★ 黙って消さない)。
            let (focus_tx, focus_rx) = crossbeam_channel::bounded::<u64>(256);
            let (pointer_tx, pointer_rx) =
                crossbeam_channel::bounded::<crate::analysis::pointer_bin::PointerBin>(256);
            // ⚠️★★★ `secure_input` は macOS のみ実装がある（Windows/その他では送信元が無い）。
            //   容量は小さくてよい（★ 状態が変化したときにしか送られない）。
            let (secure_tx, secure_rx) = crossbeam_channel::bounded::<bool>(16);
            input::observe::start(focus_tx, pointer_tx, secure_tx);

            // ★ ドレインスレッド: 観測 → `LogEntry`。⚠️ 判断も集計もしない (そのまま流すだけ)。
            let log_tx_observe = log_tx_for_observe;
            thread::spawn(move || loop {
                crossbeam_channel::select! {
                    recv(focus_rx) -> msg => match msg {
                        Ok(timestamp) => {
                            // ⚠️ 送れなくても**待たない** (★ ログが詰まって観測が滞留するのを避ける)。
                            let _ = log_tx_observe
                                .try_send(LogEntry::FocusTransition { timestamp });
                        }
                        Err(_) => break,
                    },
                    recv(pointer_rx) -> msg => match msg {
                        Ok(bin) => {
                            let _ = log_tx_observe.try_send(LogEntry::PointerBin {
                                timestamp: bin.timestamp,
                                moved: bin.moved,
                                buttons: bin.buttons,
                                wheel: bin.wheel,
                            });
                        }
                        Err(_) => break,
                    },
                    recv(secure_rx) -> msg => match msg {
                        Ok(on) => {
                            let timestamp = SystemTime::now()
                                .duration_since(UNIX_EPOCH)
                                .unwrap_or_default()
                                .as_millis() as u64;
                            // ⚠️★★★ cross-review (Codex) 指摘: `secure_input` は edge-encoded な
                            //   区間フラグであり、`observe_macos.rs` 側のチャネル送信は
                            //   HIGH-1 是正で保護済みだが、この 2 段目（ロガーへの送信）は
                            //   focus/pointer と同じ「送れなくても待たない」パターンのままだった。
                            //   ★ ここが落ちても致命的ではない (edge を失っても次回の変化で
                            //   復帰する) が、focus/pointer と違って**検知手段が無い**ままだと
                            //   ADR-013 の「黙って消さない」原則に反するため、少なくとも数える。
                            if log_tx_observe
                                .try_send(LogEntry::SecureInput { timestamp, on })
                                .is_err()
                            {
                                crate::input::observe::OBSERVATIONS_DROPPED
                                    .fetch_add(1, Ordering::Relaxed);
                            }
                        }
                        Err(_) => break,
                    },
                }
            });

            // ★★ G1: 他の GSE が動いていないかを OS に聞く（プラグインの**穴を埋める**）。
            //
            // ⚠️ ★ 2026-08-05 の実測: `tauri-plugin-single-instance` は
            //   **両方のビルドがプラグインを持っている**ときにしか効かない。
            //   **プラグインの無い旧ビルド**（被験者の /Applications にある Phase1 用）と
            //   新ビルドは **2 プロセス同時に走った**。★ これが protocol.md §2-3 の
            //   「打鍵が 2 本の NDJSON に割れる」当のシナリオである。
            //
            // ★ ここでは**止めない**（列挙の失敗や名前の一致ミスで実施を潰さないため）。
            //   代わりに**画面に出す**。判断は人に返す。
            // ★ setup() を塞がないよう別スレッドで。窓が出てから知らせる (1.5s)。
            //   ⚠️ これは**起動時の 1 回**。ブロック開始ごとの検査は `start_session` にある
            //   (follow-up F-1)。★ 片方だけでは「起動後に旧アプリを開かれる」を捕まえられない。
            if g1_mode().is_some() {
                spawn_duplicate_instance_check(
                    app.handle().clone(),
                    Duration::from_millis(1500),
                    "at startup",
                );

                // ★ G1: 起動時にも収束器を回す (`design.md` §1「起動のきっかけはヒント」)。
                //   ⚠️ ★ **前回の実施で送れなかった分**をここで拾う。取りこぼしても
                //   次のブロック終了で拾われるので、ここが失敗しても正しさは壊れない。
                //   ★ この時点ではまだブロックが始まっていない (被験者はスタート画面) ので
                //   「ブロック中に走らせない」を満たす。
                spawn_reconcile(app.handle().clone(), ReconcileReason::Startup);
            }

            // ⚠️★★★ O1 (R3-a): 起動時にも収束器を回す (研究者判断 O1-2 の自動提出)。
            //
            // ★ 収束型なので「起動」は**ヒントにすぎない**。⚠️ ここが落ちても、
            //   次の日次ローテートの後で拾われる。
            // ★ 猶予 (48 時間) を過ぎたファイルだけが包まれるので、
            //   ⚠️ **起動直後に「昨日の記録」がいきなり送られることはない**。
            //
            // ⚠️★★★ **収束器を回す *前* に、開いたまま残ったファイルを閉じる** (2026-09-03)。
            //
            // ★ `session_end` を書くのは `shutdown()` だけで、そこへ入るのは
            //   **トレイの終了 / main 窓の × / `quit_app`** の 3 経路しか無い。
            //   ⚠️ `ExitRequested` / `SIGTERM` / `WM_ENDSESSION` のハンドラは repo に無い。
            //   → ★ **トレイから終了せずに PC を再起動するだけ**で、その日のファイルは
            //     永久に提出候補から外れていた (`o1::close_orphaned_sessions` の doc 参照)。
            // ⚠️ 走査はファイルを読むので **setup() を塞がない**ようスレッドに逃がす。
            //   ★ 収束器は同じスレッドで**閉じ終わってから**起こす (順序を保証する)。
            //
            // ⚠️★★ **sweep が panic しても収束器は必ず走らせる** (cross-review LOW・2026-09-03)。
            //   ★ 旧版はコメントで「ここが落ちても収束器は走る」と書いていたが、⚠️ **嘘だった**
            //   —— panic するとスレッドごと死に、`spawn_reconcile` に到達しない
            //   (= 起動時の収束が丸ごと失われる)。→ ★ `catch_unwind` で包む。
            //
            // ⚠️★ **`log_path_str` を「いま書いている先」として使えるのは、これが *起動時 1 回* だから**
            //   である。★ `logger.rs` は「書き先の権威は `SharedLogTarget.path` であり、
            //   起動時の値をコピーして持ち回るな」と明示している。
            //   ⚠️ **sweep をローテート時や定期実行に広げるなら、必ず共有ハンドルから読み直すこと**
            //   (★ さもないとライブファイルに `session_end` を書く)。
            if crate::o1::is_o1() {
                let sweep_app = app.handle().clone();
                let sweep_current = std::path::PathBuf::from(&log_path_str);
                thread::spawn(move || {
                    let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                        let dir = sweep_current.parent()?;
                        Some(crate::o1::close_orphaned_sessions(
                            dir,
                            Some(sweep_current.as_path()),
                            now_epoch_ms(),
                        ))
                    }));
                    match outcome {
                        Ok(Some(sweep)) if sweep.closed > 0 || sweep.failed > 0 => {
                            // ⚠️★ **画面にも届ける** —— 権限やディスクで閉じられない端末は
                            //   ★ 無音で提出ゼロになる (cross-review LOW)。
                            tracing::warn!(
                                closed = sweep.closed,
                                failed = sweep.failed,
                                "O1 orphan sweep finished"
                            );
                        }
                        Ok(_) => {}
                        Err(_) => {
                            tracing::error!(
                                "O1 orphan sweep panicked; continuing to the reconciler anyway"
                            );
                        }
                    }
                    spawn_reconcile(sweep_app, ReconcileReason::Startup);
                });
            }

            // ★ G1: ブロックを 5:00 ちょうどで自動終了する専用スレッド。
            //
            // ⚠️ ★ なぜアプリ側に置くか (D-6 の「見直しタイミング」の決着):
            //   記入ページ (writing-pad.html) は **被験者の打鍵を止める** 役 (readOnly + 告知)。
            //   本スレッドは **NDJSON のブロック境界を切る** 役である。役割が違うので二重ではない。
            //   ★ 手順は「ページを開く → 開始する」の順に統一したので、ページの 5:00 が
            //   先に来る = ★ **末尾の打鍵は落ちない** (protocol.md §4.2 / §4b.2)。
            //   ⚠️⚠️ ★ 第 12 版の訂正: ここにはかつて「取りこぼしが構造的にゼロ」と書いてあった。
            //     ★ この順序が守るのは **末尾側だけ** である。⚠️ ページのゲートを押してから
            //     アプリの「開始する」を押すまでの間に打ち始めれば、**頭が落ちる**
            //     (ゲート押下で記入欄に focus が入り、すぐ打てる)。
            //     → 手順書で抑止するが保証はしない。preregistration.md §2.12-1 / §3.8。
            //
            // ⚠️ ★ ブラウザ側の setTimeout ではなく Rust スレッドにした理由:
            //   G1 実施中、GSE の窓は**背面**にある (被験者はブラウザを見ている)。
            //   WebView の背面タイマーはスロットリングされうるため、ログ境界を託せない。
            //
            // ⚠️ ★ 残り時間は emit しない。`§4.4` が「残り時間のアナウンスをしない」と定めており、
            //   カウントダウンは `§2.2` が却下した「時間圧」を全ブロックに入れることになる。
            //   出すのは「終わった」1 回だけである。
            // ⚠️★★ キーボードフックの生存監視 (2026-08-09 の silent death 対策)。
            //
            //   背景: Windows 実機で **5 分間 0 打のブロックが「正常」として自動提出された**。
            //   `HOOK_ACTIVE` は「設置できた」しか意味せず、OS が低レベルフックを黙って外しても
            //   true のままだったからである (`windows-verification.md` §5-7)。
            //
            //   ★ 独立スレッドにする理由: トレイのスレッドに載せると、**トレイの生成に失敗した
            //   環境では検知ごと消える** (`Failed to build the tray icon` は実在する経路)。
            //   ⚠️ 判断は `input::liveness` の純関数に閉じてあり、ここは配線だけを持つ。
            {
                /// ⚠️★★★ **O1 でトレイ警告を出すまでの starvation** (研究者判断 2026-08-28)。
                ///
                /// ★ 30 分。⚠️ **ログ (30 秒) と再設置 (120 秒) は変えない** ——
                /// 変えているのは「**被験者の画面に警告を出すまで**」だけである。
                ///
                /// ★ 根拠: O1 の宣言 4 択には「デザイン・映像・制作作業」があり、
                /// ⚠️ そこでは「マウスだけで 2 分」が**常態**になる
                /// (2026-08-28 に実機で「⚠ 計測できていません」＋生存中フックの再設置を実測)。
                /// ★ 誤警告は被験者の作業を直接壊すが、⚠️ 再設置の遅れは**復旧力を削る**ので、
                /// **同じ数字にしてはならない** (`liveness::participant_visible_starved` の doc を見よ)。
                ///
                /// ⚠️ 値を変えるときは `input/liveness.rs` の
                /// `o1_tray_threshold_matches_lib_rs` が赤くなる。★ 両方そろえて直すこと。
                const O1_LIVENESS_TRAY_AFTER_MS: u64 = 1_800_000;

                let liveness_session_active = session_active_for_liveness;
                let liveness_log_tx = log_tx_liveness;
                thread::spawn(move || {
                    use crate::input::liveness::{self, HookHealth, Starvation, Thresholds};

                    const TICK_MS: u64 = 1000;

                    let th = Thresholds::default();
                    // ⚠️★★★ **O1 のときだけ、被験者の目に入るトレイ警告を遅らせる**
                    //   (研究者判断 2026-08-28・`O1_LIVENESS_TRAY_AFTER_MS`)。
                    //   ★ `None` = 通常運用 / G1 = 従来どおり `Down` と同義。
                    //   ⚠️ ログ (30 秒) と再設置 (120 秒) は **O1 でも据え置き**である。
                    let o1_tray_after_ms = if crate::o1::is_o1() {
                        Some(O1_LIVENESS_TRAY_AFTER_MS)
                    } else {
                        None
                    };
                    let mut starv = Starvation::default();
                    let mut prev_tick = liveness::last_system_input_tick();
                    let mut prev_callbacks =
                        crate::input::hook::CALLBACK_COUNT.load(Ordering::Relaxed);
                    // ⚠️★ 「呼ばれた」と「記録できた」は別。channel が詰まって捨てた分を見張る。
                    let mut prev_dropped =
                        crate::input::hook::EVENTS_DROPPED.load(Ordering::Relaxed);
                    // ★ `tick_ms` は公称値ではなく**実測**を渡す (スリープ復帰やスケジューラ遅延で
                    //   `starved_ms` が実時間からずれるのを防ぐ)。★ 測った量を残すのが本行の趣旨。
                    let mut last_tick_at = Instant::now();
                    let mut prev_health = HookHealth::Ok;
                    // ⚠️★★ 再設置は **1 エピソードにつき 1 回**だけ (cross-review 両者一致 HIGH)。
                    //   ★ 時間バックオフ (60 秒ごと再試行) にしていたが、それだと
                    //   **マウスのみ / 読書中心の作業**という既知の誤検知
                    //   (`liveness.rs` のテストで仕様として固定済み) のあいだ、
                    //   ⚠️ **生きているフックを 60 秒おきに壊し続ける**。
                    //   しかもそれが起きるのは無打鍵で読んでいる時間 = 研究上重要な区間である。
                    //   ★ 本当に死んでいるなら 1 回で直るか直らないかであり、
                    //     繰り返しても得るものが無い。
                    let mut rehook_done_this_episode = false;
                    let mut rehook_attempts_this_episode: u32 = 0;
                    // ⚠️★ この starvation エピソードで到達した最大値。
                    //   `step()` は復帰した瞬間に 0 へ戻すので、そのまま書くと
                    //   **復帰行が `starved_ms: 0` になり「何秒落ちていたか」が消える**
                    //   (code-reviewer MEDIUM)。★ 測った量を残すのが本行の存在理由なので保持する。
                    let mut peak_starved_ms: u64 = 0;
                    // ★ ADR-013 D4 (穴 A): 30 秒未満の在席×非打鍵を 60 秒窓で数える。
                    //   ⚠️ `hook_health` の出力条件・意味論は 1 文字も変えない (別トラックとして足すだけ)。
                    let mut micro_window = liveness::MicroStarveWindow::new();
                    // ⚠️★★★ ADR-013 D4 (穴 B): **前の `hook_health` 行からの** dropped 増分。
                    //   ★ 下の `prev_dropped` は「`tracing` に出したとき」だけ更新されるので**流用できない**。
                    //   混ぜると `dropped_delta` が「前回行からの差分」ではなくなる。
                    let mut dropped_at_last_line: u64 = 0;
                    // ★ ブロック境界を見るための 1 tick 前の**セッション開始時刻**。
                    //   ⚠️★★★ `session_active` の立ち上がりでは**足りない** ——
                    //   実行中の再押下 (`RotateForRestart`) は `true` のままなので発火しない
                    //   (Codex HIGH・2026-08-19)。→ `liveness::is_new_block_epoch` を見よ。
                    let mut prev_session_start_ms: u64 = 0;

                    loop {
                        thread::sleep(Duration::from_millis(TICK_MS));
                        if is_shutting_down() {
                            return;
                        }

                        // ⚠️★★★ O1 (R3-a): **`session_active` をそのまま使わない。**
                        //   ★ `liveness::step` は第 2 引数が false のとき `starved_ms` を
                        //   **0 に落とす**。O1 では `session_active` が永久に false なので、
                        //   ⚠️ そのまま渡すと **フックが死んでも永久に検出できない**
                        //   (★ mac の `CGEventTap` 失効が無検出になる = 事前登録 §7 E1 の穴)。
                        //   ★ 一時停止中は数えない (打鍵が来なくて当たり前・元の意図と同じ)。
                        //   ⚠️ 非 O1 は `session_active` そのもの (挙動は 1 バイトも変わらない)。
                        let session_active = crate::o1::recording_active(
                            crate::o1::is_o1(),
                            liveness_session_active.load(Ordering::Acquire),
                            crate::recording::is_paused(),
                        );

                        // ★ 生 tick の「変化」だけを見る (絶対時刻へ変換しない = ラップアラウンド安全)。
                        let tick = liveness::last_system_input_tick();
                        // ⚠️★ 比較規則は **OS ごとに違う**ので `liveness` 側に置いてある
                        //   (Windows は等値・macOS は揺れの許容幅つき)。ここで `!=` と書かない。
                        let system_input_seen = liveness::system_input_seen(prev_tick, tick);
                        prev_tick = tick;

                        let callbacks = crate::input::hook::CALLBACK_COUNT.load(Ordering::Relaxed);
                        let hook_event_seen = callbacks != prev_callbacks;
                        prev_callbacks = callbacks;

                        // ⚠️★ 「呼ばれた」だけでは足りない。channel が詰まって**捨てた**分は
                        //   記録されていないので、増えたら必ず残す
                        //   (★ コールバック内ではログを書けないのでここで報告する)。
                        let dropped = crate::input::hook::EVENTS_DROPPED.load(Ordering::Relaxed);
                        if dropped > prev_dropped {
                            tracing::error!(
                                dropped_total = dropped,
                                dropped_now = dropped - prev_dropped,
                                "keystroke events were dropped before reaching the analysis thread \
                                 (channel full); those keystrokes are NOT in the session log"
                            );
                            prev_dropped = dropped;
                        }

                        // ★ 経過は公称値ではなく**実測**を渡す。
                        let elapsed_ms = last_tick_at.elapsed().as_millis() as u64;
                        last_tick_at = Instant::now();

                        let prev_starved_ms = starv.starved_ms;
                        starv = liveness::step(
                            starv,
                            session_active,
                            system_input_seen,
                            hook_event_seen,
                            elapsed_ms,
                        );
                        let health = liveness::health(starv, th);
                        peak_starved_ms = peak_starved_ms.max(starv.starved_ms);

                        // ⚠️★★★ **窓集計は下の `continue` より前に置く。**
                        //   `if health == prev_health && !rehook { continue; }` は 1Hz ループの
                        //   残りを全部飛ばすので、後ろに置くと **窓がまるごと消える**
                        //   (health が変わらない = 平常時こそ micro 帯が出る区間である)。
                        // ⚠️★★★ **ブロック境界で計器の状態を揃える**
                        //   (security-checker MEDIUM ＋ Codex HIGH)。
                        //   ★ 新しいブロックが始まったら `dropped_delta` の基準を引き直し、
                        //   集計途中の窓は**捨てる**。そうしないと、ローテート後の最初の行の差分が
                        //   **前のブロックのファイルにある行からの差分**になり、
                        //   ⚠️ `dropped_delta` / `starve_window` が消そうとした「区間の取り違え」を
                        //   **ファイル境界で再導入する** (`validate_blocks.py` はブロック単位で読む)。
                        //
                        // ⚠️★★★ **`session_active` の立ち上がりで見てはならない。**
                        //   実行中の再押下 (`RotateForRestart`) は `true` のままなので
                        //   **その経路でだけ発火しない** (＝ G-1 で新設した経路そのもの)。
                        let session_start_ms = SESSION_START_MS.load(Ordering::Acquire);
                        let new_block_epoch =
                            liveness::is_new_block_epoch(prev_session_start_ms, session_start_ms);
                        if new_block_epoch {
                            dropped_at_last_line = dropped;
                            micro_window = liveness::MicroStarveWindow::new();
                            // ⚠️★★★ **累積 starvation もここで揃える** (code-reviewer HIGH・2026-08-21)。
                            //   ★ `step()` が 0 に落とすのは**打鍵が届いた tick**か**非計測の tick**だけ。
                            //   ⚠️ 再押下は**マウス**なので、エポックの tick では `starved_ms` は
                            //     増え続けており、★ **次の tick (打鍵) で「正 → 0」が成立して
                            //     前ブロックの値が新窓へ計上される**。
                            //   → ★ 通常のブロック境界 (`session_active = false`) と同じ形に揃える。
                            //   ⚠️ **`peak_starved_ms` は戻さない** —— 戻すと復帰行の `starved_ms` が
                            //     0 になり、「何秒落ちていたか」という**測った量が消える**。
                            starv = liveness::reset_starvation_at_new_block(new_block_epoch, starv);
                        }
                        prev_session_start_ms = session_start_ms;

                        if let Some(tally) = micro_window.tick(
                            session_active,
                            // ⚠️★★★ **事後レビュー所見 C** (2026-08-19)。
                            //   実行中の再押下 (`RotateForRestart`) は `session_active` を
                            //   `true` のまま維持するので、★ 窓を捨てた**同じ tick**に
                            //   捨てる前の `prev_starved_ms` が「正 → 0」として
                            //   **新しい窓へ**計上されうる (= 前ブロックのエピソードの誤帰属)。
                            //   → ★ `tick()` の方針「**誤帰属より既知の切り捨てを採る**」に揃える。
                            liveness::starved_ms_carried_into_new_window(
                                new_block_epoch,
                                prev_starved_ms,
                            ),
                            starv.starved_ms,
                            th,
                            elapsed_ms,
                        ) {
                            if liveness_log_tx
                                .try_send(LogEntry::StarveWindow {
                                    timestamp: SystemTime::now()
                                        .duration_since(UNIX_EPOCH)
                                        .unwrap_or_default()
                                        .as_millis()
                                        as u64,
                                    // ★ **実測の窓長**を載せる (公称 60_000 ではない)。
                                    //   ⚠️ 公称を書くと `n_lt30 / win_ms` が過大評価になる。
                                    win_ms: tally.win_ms,
                                    n_lt30: tally.n_lt30,
                                    sum_lt30_ms: tally.sum_lt30_ms,
                                })
                                .is_err()
                            {
                                // ★ 落ちても致命ではない (micro 帯は投資判断の材料であって合否ではない)。
                                //   ⚠️ ただし黙って消さない。
                                tracing::warn!(
                                    "failed to record a starve_window line (log queue full)"
                                );
                            }
                        }

                        // ⚠️★★★ **このフラグは「被験者に見えるもの」を表す** (2026-08-28)。
                        //   ★ 読み手は **2 つ**ある (⚠️ 「トレイだけ」ではない ——
                        //     code-reviewer / security-checker が一致して指摘):
                        //     1. `tray::current_state` … トレイの「⚠ 計測できていません」
                        //     2. `get_recording_status` → `recording_health` …
                        //        **アプリ内のバッジ**と「キーボードの記録ができていません」
                        //   → ★ どちらも被験者向けなので、O1 ではまとめて 30 分まで遅らせる。
                        //   ⚠️ **`health` は触らない**ので、この直後の再設置と
                        //     NDJSON の `alive` は **1 ミリも変わらない**。
                        crate::input::hook::HOOK_STARVED.store(
                            liveness::participant_visible_starved(health, starv, o1_tray_after_ms),
                            Ordering::Relaxed,
                        );
                        // ⚠️★★ **研究者向けの診断はモードに依らず「届いていない」を指す** (D-6)。
                        //   ★ 上の旗は O1 で 30 分遅れるので、⚠️ そのまま診断に出すと
                        //     `hook_starved` が **O1 のあいだだけ意味を変える**。
                        crate::input::hook::HOOK_NOT_DELIVERING
                            .store(health == HookHealth::Down, Ordering::Relaxed);

                        // ★ Down の間、既存の再設置経路を起こす (D-3)。
                        //   ⚠️★★★ **2026-09-05 に「1 回で諦める」をやめた。**
                        //   ★ 旧実装は戻り値に関わらず `= true` で済みにしていたので、
                        //   ⚠️ macOS (`request_reinstall` が定数 `false`) では
                        //   **「試したことにして永久に諦める」**動きだった。
                        //   → ★ 判定は `liveness` の純関数に出した (両 OS でテストする)。
                        let mut rehook = false;
                        if liveness::rehook_should_attempt(
                            health == HookHealth::Down,
                            rehook_attempts_this_episode,
                            rehook_done_this_episode,
                        ) {
                            rehook_attempts_this_episode += 1;
                            rehook = crate::input::hook::request_reinstall();
                            // ★ **要求が実際に出たときだけ**済みにする。
                            rehook_done_this_episode = rehook;
                        }
                        // ★ 本物の復帰 (フックが呼ばれた or 計測終了) でエピソードを閉じる。
                        if liveness::rehook_episode_closed(starv.starved_ms) {
                            rehook_done_this_episode = false;
                            rehook_attempts_this_episode = 0;
                        }

                        // ★ 1Hz で連発しない。状態が変わったとき、または再設置したときだけ記録する。
                        if health == prev_health && !rehook {
                            continue;
                        }

                        match health {
                            HookHealth::Suspect if prev_health == HookHealth::Ok => {
                                tracing::error!(
                                    starved_ms = starv.starved_ms,
                                    "keyboard hook may be dead: the system saw input but the hook \
                                     was not called (keystrokes may NOT be recorded)"
                                );
                            }
                            HookHealth::Down if prev_health != HookHealth::Down => {
                                // ⚠️★★★ **機序を 1 回で決着させるための診断** (2026-09-05)。
                                //   ★ 2026-09-04 の 8 時間実測では、120 s 級の欠測が
                                //   「tap が disable されていた」のか「イベントが来なかった
                                //   だけ」なのかを**区別する記録が無かった**。
                                //   → ★ `tap_enabled` が `Some(false)` なら層 2 の担当、
                                //     `Some(true)` なら **disable されていないのに飢えている**
                                //     (⚠️ 再有効化では直らない = 層 3 の担当) と読める。
                                //   ⚠️ `None` は「その OS では答えられない」であって
                                //     「無効」ではない。
                                let tap_enabled =
                                    crate::input::hook::hook_reports_enabled();
                                tracing::error!(
                                    starved_ms = starv.starved_ms,
                                    rehook_requested = rehook,
                                    tap_enabled = ?tap_enabled,
                                    watchdog_recoveries =
                                        crate::input::hook::watchdog_recoveries(),
                                    "keyboard hook is NOT delivering events; keystrokes are NOT \
                                     being recorded for this block"
                                );
                            }
                            HookHealth::Ok if prev_health != HookHealth::Ok => {
                                tracing::info!("keyboard hook is delivering events again");
                            }
                            _ => {}
                        }

                        // ★ 復帰行には**エピソードのピーク**を載せる (現在値は 0 に戻っているため)。
                        let reported_starved_ms = if health == HookHealth::Ok {
                            peak_starved_ms
                        } else {
                            starv.starved_ms
                        };
                        if liveness_log_tx
                            .try_send(LogEntry::HookHealth {
                                timestamp: SystemTime::now()
                                    .duration_since(UNIX_EPOCH)
                                    .unwrap_or_default()
                                    .as_millis() as u64,
                                alive: health != HookHealth::Down,
                                starved_ms: reported_starved_ms,
                                rehook,
                                dropped,
                                // ★ 前の **行** からの増分 (ADR-013 D4・穴 B)。
                                //   ★ ブロック内の最初の行では「**ブロック開始**からの増分」になる
                                //   (⚠️ 基準はブロック開始で引き直す。ファイル境界をまたがせない)。
                                dropped_delta: dropped.saturating_sub(dropped_at_last_line),
                            })
                            .is_err()
                        {
                            // ⚠️★ この行は「そのブロックが有効か」を判断する唯一の証跡なので、
                            //   落ちたことだけは残す (監視スレッドなのでログ制約は無い)。
                            tracing::error!("failed to record a hook_health line (log queue full)");
                            // ⚠️★★★ **落ちたときは「行が出た」ことを前提にした状態を 1 つも進めない。**
                            //   ★ `dropped_at_last_line` / `peak_starved_ms` / `prev_health` は
                            //   すべて「直前の行が持ち去った情報」を表す。
                            //   ⚠️ 進めると、`prev_health` が一致して次の tick が `continue` に落ち、
                            //   **「何秒落ちていたか」と状態遷移そのものが永久に消える**
                            //   (code-reviewer MEDIUM・2026-08-19)。
                            //   → ★ 据え置けば次の tick で**同じ行を出し直せる**。
                        } else {
                            dropped_at_last_line = dropped;
                            if health == HookHealth::Ok {
                                peak_starved_ms = 0;
                            }
                            prev_health = health;
                        }
                    }
                });
            }

            if g1_mode().is_some() {
                let app_handle = app.handle().clone();
                let block_log_tx = log_tx_g1;
                let block_session_active = session_active_for_g1;
                let block_end_ack = block_end_ack_rx;
                thread::spawn(move || {
                    tracing::info!(
                        "G1: block auto-end thread started (limit={} ms)",
                        crate::g1::BLOCK_DURATION_MS
                    );
                    loop {
                        thread::sleep(Duration::from_millis(500));
                        // ★ 判定は純関数 `g1::decide_block_end` が持つ (`decide_start_action` と同じ流儀)。
                        let start = SESSION_START_MS.load(Ordering::Acquire);
                        let now = SystemTime::now()
                            .duration_since(UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_millis() as u64;
                        // ★ ポーリング時点では交代を判定しない (`observed == current` を渡す)。
                        if crate::g1::decide_block_end(
                            start,
                            start,
                            now,
                            crate::g1::BLOCK_DURATION_MS,
                        ) != crate::g1::BlockEndAction::EndBlock
                        {
                            continue; // 未開始 / まだ 5 分に達していない
                        }

                        // ⚠️★★★ **ここから 4) までがブロック遷移の臨界区間**である (D-1)。
                        //   ★ 「開始する」の押下 (`start_session`) と直列化することで、
                        //     `BlockEnd` が**次のブロックの `Rotate` より前**にログ channel へ入る
                        //     ことを保証する。⚠️ これが破れると `session_end` が
                        //     **新しいファイル**へ書かれる (`protocol.md §1` の破れ = リブートの原因と同型)。
                        //   ⚠️ `emit` / `spawn_reconcile` は**外に出す** (ブロックとブロックの間の
                        //     処理であり排他は要らない。ロックを長く持たない)。
                        let block_transition = lock_block_transition();

                        // ⚠️★★★ **排他を取ってから交代を照合する** (D-1「押下が先」の交錯)。
                        //   ★ ポーリングと排他の取得の間に「開始する」が押されて
                        //     **新しいブロックが始まっていた**なら、ここで進むと
                        //     `SESSION_START_MS.store(0)` が**始まったばかりのブロックを殺す**
                        //     —— しかも `start == 0` で `continue` するので
                        //     ⚠️ **自動終了も二度と来ない**。
                        //   ⚠️ 実行中の再押下 (`RotateForRestart`) は `session_active` を
                        //     `true` のまま維持するので、★ **`session_active` を見ていては気づけない**。
                        //     照合するのは `SESSION_START_MS` (どちらの経路でも必ず動く) である。
                        //   ⚠️★★ **`EndBlock` 以外はすべて中止する** (Codex 指摘・2026-08-21)。
                        //   ★ `== Superseded` と書くと、将来 `decide_block_end` の分類が増えたときに
                        //     **新しい枝が黙って「閉じてよい」側へ倒れる**。
                        //   ⚠️ 判定が増えるほど危険側へ倒れる形にしない (fail-closed)。
                        //   ★ `now` は**排他を取った後に採り直す** (code-reviewer MEDIUM・2026-08-21)。
                        //   ⚠️ 押下と競合して最大 ~1.5 秒待たされたとき、古い `now` で判定し、
                        //     古い値をログに残すことになる。
                        let now = SystemTime::now()
                            .duration_since(UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_millis() as u64;
                        let current_start_ms = SESSION_START_MS.load(Ordering::Acquire);
                        let recheck = crate::g1::decide_block_end(
                            start,
                            current_start_ms,
                            now,
                            crate::g1::BLOCK_DURATION_MS,
                        );
                        if recheck != crate::g1::BlockEndAction::EndBlock {
                            tracing::info!(
                                "G1: aborting the auto-end ({:?}); \
                                 the block that is running now is left intact",
                                recheck
                            );
                            continue;
                        }

                        // 1) 先に分析スレッドを止める。⚠️ ★ これを後にすると
                        //    `session_end` の**後ろ**に feat / key 行が続きうる。
                        block_session_active.store(false, Ordering::Release);
                        SESSION_START_MS.store(0, Ordering::Release);

                        // 2) ⚠️★ **分析スレッドがドレインに入ったことを観測してから**進む。
                        //    固定 sleep では足りない: 分析スレッドは既に recv_timeout に入って
                        //    いて **次の 1Hz マークまで最大 ~1000ms** ブロックしうるので、
                        //    その在庫 1 イテレーションが session_end を追い越して
                        //    Key/Feat を投げる (code-review HIGH)。
                        let deadline = Instant::now() + Duration::from_millis(1500);
                        while !ANALYSIS_IDLE.load(Ordering::Acquire) {
                            if Instant::now() >= deadline {
                                // ★ 黙って進まない。追い越しが起きたかもしれないことを残す。
                                tracing::warn!(
                                    "G1: analysis thread did not go idle within 1500ms; \
                                     a feat/key line may follow session_end in this block"
                                );
                                break;
                            }
                            thread::sleep(Duration::from_millis(20));
                        }

                        // 3) ブロックを閉じる。⚠️ ★ ここでは**新しいファイルを開かない**
                        //    (10 ブロック目の後に空の 11 本目が残り、`gse-submit` が
                        //    最新 1 本としてそれを出してしまうため)。開くのは次の start_session。
                        // ⚠️★★ **前の回の合図を捨ててから送る** (code-review HIGH)。
                        //   合図の channel は容量 1 で、下の `recv_timeout` が待ち切れなかった
                        //   回の合図は**残る**。残ったままだと次のブロックで `recv_timeout` が
                        //   ★ **古い合図で即座に返り**、`session_end` が書かれる前に収束器を
                        //   起こす → 以後ずっと 1 ブロック遅れる。
                        //   ⚠️ プロセスは × で終了しない (D-10) ので、
                        //   **最後のブロックがこのプロセスの間ずっと送られない**。
                        while block_end_ack.try_recv().is_ok() {}

                        let closed = match block_log_tx.try_send(LogEntry::BlockEnd) {
                            Err(e) => {
                                tracing::error!("G1: FAILED to close block: {}", log_send_error(e));
                                false
                            }
                            Ok(()) => {
                                tracing::info!("G1: block auto-ended at {} ms", now);
                                true
                            }
                        };

                        // ⚠️★★★ **ここで臨界区間を抜ける** (D-1)。
                        //   ★ `BlockEnd` は channel へ入った。以後に「開始する」が押されても、
                        //     その `Rotate` は **`BlockEnd` の後ろ**に並ぶので
                        //     `session_end` は**閉じたブロックのファイル**に書かれる。
                        //   ⚠️ 以下 (番兵・`emit`・自動提出) は**ブロックとブロックの間**の処理であり、
                        //     排他は要らない。★ ロックを必要以上に長く持たない。
                        drop(block_transition);

                        // ⚠️★★ 4) の **前**に番兵を立てる (code-reviewer HIGH-2)。
                        //   スタート画面が出た瞬間から `sending: true` にしないと、
                        //   ★ 梱包が始まるまでの数秒、**前の回のレシート**
                        //   (1 ブロック目は「✅ 送信を待っている記録はありません」) が出る。
                        let in_flight = InFlightGuard::new(ReconcileReason::BlockEnd);
                        // ★★ 併せて **前の回のレシートを捨てる**。`last_sent_ms` はプロセスに
                        //   1 個しか無いので、捨てないと「この回」が前の回を指しうる。
                        reset_sent_receipt();

                        // 4) 画面へ通知 (スタート画面へ戻す)。★ 「終わった」だけを伝える。
                        let _ = app_handle.emit("g1-block-ended", ());

                        // 5) ★ 自動提出を起こす。⚠️ ★ **`session_end` が書かれてから**にする。
                        //    収束器は「`session_end` を持つファイル」しか触らないので、
                        //    先に起こすとこのブロックは 1 周遅れる。⚠️ とくに **最後のブロック**は
                        //    `overlay` 窓があるためプロセスが × で終了せず、
                        //    「次の起動」が来ないまま送られない。
                        //    ★ 固定 sleep ではなく **合図を待つ** (ANALYSIS_IDLE と同じ考え方)。
                        if closed {
                            match block_end_ack.recv_timeout(Duration::from_secs(5)) {
                                Ok(()) => {}
                                Err(_) => {
                                    // ★ 黙って進まない。収束型なので次の機会に拾えるが、
                                    //   ⚠️ 待てなかったこと自体を残す。
                                    tracing::warn!(
                                        "G1: block-end ack did not arrive within 5s; \
                                         this block will be picked up on a later reconcile"
                                    );
                                }
                            }
                        }
                        // ⚠️ ★ ここは **ブロックとブロックの間** である (被験者はスタート画面)。
                        //    `design.md` の「ブロック中に走らせない」を満たす。
                        // ★ 番兵は 4) の前で作ってある。ここでは**渡すだけ**にして、
                        //   「スタート画面が出てから送信中が立つまで」の窓を無くす。
                        spawn_reconcile_with_guard(
                            app_handle.clone(),
                            ReconcileReason::BlockEnd,
                            in_flight,
                        );
                    }
                });
            }

            // Task B: ランダム時点プローブの専用スケジューラスレッド (DB-2)。
            // 1Hz Analysis Thread はレイテンシ要件があり AppHandle も持たないため、
            // emit と logger 送信の両方が要るプローブ駆動は専用スレッドに分離する。
            // IME Monitor 風の sleep ポーリングで 1Hz 駆動 (wake 信号は不要)。
            // scheduler 純ロジックは analysis/probe_scheduler.rs (OS API 非依存)。
            //
            // ★ G1 統制タスク実験の kill switch (B-1): env `GSE_DISABLE_PROBES=1` のとき
            // **このスレッドを起こさない**。poll 側で握り潰すのではなくスレッドごと止めるのは、
            // 「発火はしたが黙殺した」状態を残さないためである (probe_assignment も
            // probe_triggered も構造的に発生しえなくなる)。
            // 既定 (未設定) では従来どおり起動するので通常運用の挙動は変わらない。
            // 根拠と非影響の論証: experiments/20260801-controlled-friction-task/preregistration.md
            // §2.6 / §5.4 ・ analysis::probe_scheduler::probes_disabled_by_env。
            {
                use crate::analysis::probe_scheduler::{
                    decide_probe_init, driver_idle_ms, probes_disabled_by_env, ProbeConfig,
                    ProbeInitDecision, ProbeScheduler,
                };
                // ★ 引き金は 2 本ある (preregistration.md §5.4 第 10 版 / D-7)。
                //   ⚠️ ★ **env の経路を消していない。** G1 モード (フォルダのマーカー) を
                //   **第 2 の引き金として足した**だけである。したがって:
                //     - 「G1 の実施時はプローブスケジューラを起動しない」 → 強化される
                //     - 「既定 (未設定) では従来どおり起動する」          → 無変更
                //     - 合格経路                                          → 1 本も増えない
                //   ★ §5.4-2 の客観検証 (validate_blocks.py で probe 行 0) はそのまま残す。
                let disabled_by_env =
                    probes_disabled_by_env(std::env::var("GSE_DISABLE_PROBES").ok().as_deref());
                let disabled_by_g1 = g1_mode();
                let probes_disabled = disabled_by_env || disabled_by_g1.is_some();
                if probes_disabled {
                    // ★ 実施ログに必ず 1 行残す。実機で「止まっているつもり」を防ぐ番兵であり、
                    // 実施後の客観検証は NDJSON 側 (probe_assignment 行 0) で行う。
                    tracing::warn!(
                        "probe scheduler DISABLED (env={}, g1_mode={:?}) \
                         (G1 controlled-friction experiment; preregistration.md 2.6 / 5.4). \
                         No scheduled probe_assignment / probe_triggered will be produced. \
                         NOTE: the self-marker hotkey is user-initiated and is NOT gated here; \
                         G1 forbids pressing it (protocol.md).",
                        disabled_by_env,
                        disabled_by_g1
                    );
                }
                let app_handle = app.handle().clone();
                let probe_log_tx = log_tx_probe;
                if !probes_disabled {
                    thread::spawn(move || {
                        tracing::info!("Probe scheduler thread started");
                        let now_ms = || -> u64 {
                            SystemTime::now()
                                .duration_since(UNIX_EPOCH)
                                .unwrap_or_default()
                                .as_millis() as u64
                        };
                        let mut scheduler: Option<ProbeScheduler> = None;
                        let mut active_session_start: u64 = 0;
                        // M0 (D1): 現在初期化済みのプロファイルの away 閾値。idle 判定で参照する。
                        // 較正/配備で同値 (3 分) だが、選択した config から引いて将来の差異に備える。
                        let mut active_away_idle_ms: u64 = ProbeConfig::default().away_idle_ms;
                        loop {
                            thread::sleep(Duration::from_millis(1000));
                            let session_start = SESSION_START_MS.load(Ordering::Acquire);
                            if session_start == 0 {
                                // セッション未開始: スケジューラを破棄して待機。
                                scheduler = None;
                                active_session_start = 0;
                                continue;
                            }
                            if session_start != active_session_start {
                                // M0 (D1): session_meta (condition) を session_start と**世代照合**してから
                                // プロファイルを選ぶ。frontend は start_session → record_session_meta の順で
                                // 呼ぶため、照合一致まで待たないと calibration 選択が race する。古い世代の
                                // meta は不一致で弾かれる (cross-review HIGH)。純ロジック decide_probe_init に
                                // 判定を委譲し、ここでは Atomic 読みと副作用 (warn/初期化) のみ行う。
                                let meta_for = SESSION_META_FOR_START_MS.load(Ordering::Acquire);
                                let meta_is_calibration =
                                    SESSION_IS_CALIBRATION.load(Ordering::Acquire);
                                let waited = now_ms().saturating_sub(session_start);
                                let (calibration, meta_fallback) = match decide_probe_init(
                                    session_start,
                                    meta_for,
                                    meta_is_calibration,
                                    waited,
                                    PROBE_META_READY_GRACE_MS,
                                ) {
                                    // この session_start 向けの meta 未受領・grace 内: 再試行
                                    // (active_session_start は更新しない。schedule は session_start
                                    // anchor のため遅延は決定性に影響しない)。
                                    ProbeInitDecision::Wait => continue,
                                    ProbeInitDecision::Start {
                                        calibration,
                                        meta_fallback,
                                    } => (calibration, meta_fallback),
                                };
                                if meta_fallback {
                                    // meta 送信が失敗/未送信のまま grace 超過。サイレント全滅を避け
                                    // default で初期化し warn する (code-review HIGH)。
                                    tracing::warn!(
                                        "probe scheduler: session_meta not received {}ms after \
                                     session_start={}; falling back to default ProbeConfig \
                                     (calibration NOT applied — check record_session_meta)",
                                        waited,
                                        session_start
                                    );
                                }
                                // 新セッション検出 (DB-6)。entropy から u64 seed を引いて
                                // seed_from_u64 で初期化し、seed を tracing に記録する。本番は
                                // 非決定論的でありつつ「この seed でこの scheduled_ts 系列が出た」
                                // ことを後から再現でき、一様性監査 (D-14) が成立する。NDJSON schema は
                                // Task A で凍結のため seed は trace ログにのみ残す (schema 不変)。
                                active_session_start = session_start;
                                // M0 (D1): 較正は収量優先、それ以外 (配備・baseline・fallback) は default。
                                let config = if calibration {
                                    ProbeConfig::calibration()
                                } else {
                                    ProbeConfig::default()
                                };
                                active_away_idle_ms = config.away_idle_ms;
                                let seed: u64 = rand::random();
                                tracing::info!(
                                    "probe scheduler seed={} calibration={} for session_start={}",
                                    seed,
                                    calibration,
                                    session_start
                                );
                                scheduler =
                                    Some(ProbeScheduler::from_seed(seed, config, session_start));
                            }
                            let now = now_ms();
                            // idle 計算は driver_idle_ms (純ロジック) に委譲。F4: last_key==0 は
                            // 「idle 不明」として away_idle_ms に倒し、離席中の誤発火を防ぐ
                            // (Dashboard 表示用 get_keyboard_idle_ms とは意図的に挙動が異なる)。
                            let last_key = crate::input::hook::last_key_ms();
                            // away_idle_ms は初期化済みプロファイル (active_away_idle_ms) を参照。
                            let idle = driver_idle_ms(now, last_key, active_away_idle_ms);
                            let Some(sched) = scheduler.as_mut() else {
                                continue;
                            };
                            if let Some(fired) = sched.poll(now, idle) {
                                // (2) probe_assignment ログ (一様性の監査用・scheduled_ts)。
                                let _ = probe_log_tx.try_send(LogEntry::ProbeAssignment {
                                    probe_id: fired.probe_id.as_str().to_string(),
                                    scheduled_ts: fired.scheduled_ts,
                                    session_elapsed_ms: fired.session_elapsed_ms,
                                });
                                // (3) frontend へ emit (回答カード表示は Task C)。
                                if let Err(e) = app_handle.emit(
                                    "probe_triggered",
                                    serde_json::json!({
                                        "probe_id": fired.probe_id.as_str(),
                                        "source": "random_probe",
                                        "analysis_window_start_ms": fired.window_start_ms,
                                        "analysis_window_end_ms": fired.window_end_ms,
                                    }),
                                ) {
                                    tracing::warn!("probe_triggered emit failed: {}", e);
                                }
                                tracing::info!(
                                    "probe fired: {} at {}",
                                    fired.probe_id.as_str(),
                                    fired.scheduled_ts
                                );
                            }
                        }
                    });
                } // if !probes_disabled
            }

            // Phase 1 Ground Truth: グローバルホットキー 3 本を登録。
            // macOS: Cmd+Shift+Option+F/I/S、Windows/Linux: Ctrl+Shift+Alt+F/I/S。
            // 失敗は warn に落として起動を継続する(録画ラベリングなしでも運用可)。
            //
            // ⚠️★★★ **O1 では登録しない** (security-checker MEDIUM・2026-08-27)。★ 理由は 2 つ:
            //   1. ⚠️ O1 は数日〜数週間の常時稼働なので、**被験者の業務アプリから
            //      6 通りの打鍵を数週間奪う**。
            //   2. ⚠️★★★ 誤爆すると **同意文書 §3 の記録項目表に無い `user_label` /
            //      `review_marker` 行**が残る。★ 「記録するもの」を文書より広げてはならない。
            //   ★ プローブが O1 で構造的に発火しない (D-5) のと同じ筋である。
            if crate::o1::is_o1() {
                tracing::info!(
                    "O1: global shortcuts are NOT registered                      (they would take 6 key combinations away for weeks and could write                      user_label / review_marker rows that the consent form does not list)"
                );
            } else {
                use tauri_plugin_global_shortcut::{Code, GlobalShortcutExt, Modifiers, Shortcut};
                #[cfg(target_os = "macos")]
                let mods = Modifiers::SUPER | Modifiers::SHIFT | Modifiers::ALT;
                #[cfg(not(target_os = "macos"))]
                let mods = Modifiers::CONTROL | Modifiers::SHIFT | Modifiers::ALT;
                let shortcuts = [
                    Shortcut::new(Some(mods), Code::KeyF),
                    Shortcut::new(Some(mods), Code::KeyI),
                    Shortcut::new(Some(mods), Code::KeyS),
                    Shortcut::new(Some(mods), Code::KeyR), // Review marker
                    Shortcut::new(Some(mods), Code::KeyM), // Task B: 自己マーカー (self_marker, カード式)
                    Shortcut::new(Some(mods), Code::KeyD), // ワンタップ「今詰まっている」self_marker
                ];
                for sc in shortcuts {
                    if let Err(e) = app.global_shortcut().register(sc) {
                        tracing::warn!("global_shortcut register failed: {}", e);
                    }
                }
            }

            // Overlay ウィンドウを setup() で事前生成する (hidden, non-maximized)。
            // setup() はメインスレッドで実行されるため、Windows での
            // WebviewWindowBuilder::build() デッドロックを回避できる。
            //
            // macOS では visible(false) + maximized(true) の同時指定で
            // 不透明なオーバーレイが表示される問題があったが、ここでは
            // maximized を指定せず visible(false) のみで生成する。
            // start_session で show() し、サイズ制御 (全画面/box) は Overlay.tsx が明示 setSize で行う
            // (macOS で NSPanel 化後は maximize() が WKWebView をクラッシュさせるため。D8)。
            match tauri::WebviewWindowBuilder::new(
                app,
                "overlay",
                tauri::WebviewUrl::App("index.html".into()),
            )
            .title("GSE Overlay")
            .decorations(false)
            .transparent(true)
            .always_on_top(true)
            .skip_taskbar(true)
            // 非アクティブ (key にならない) overlay 窓ではクリックがボタンへ届かず握りつぶされる
            // (macOS。WKWebView の acceptsFirstMouse 既定 false)。下の to_panel() による非アクティブ
            // NSPanel 化と併せ、Pluely の Tauri 2.x レシピに倣い acceptFirstMouse も有効化する
            // (decisions D7)。フォーカスは奪わない (非ブロック設計を維持)。
            .accept_first_mouse(true)
            .visible(false)
            .build()
            {
                Ok(_) => tracing::info!("Overlay window pre-created (hidden)"),
                Err(e) => tracing::error!("Failed to pre-create overlay window: {}", e),
            }

            // macOS: overlay 窓を非アクティブ NSPanel 化する (decisions D7)。
            // 透明 overlay 窓は非 key 窓のためクリックを webview へルーティングせず、カードの
            // ボタンが押せなかった (真因)。NSWindowStyleMaskNonActivatingPanel + canBecomeKeyWindow
            // により、フォーカスを奪わずにクリックを webview へ配送する (Spotlight/Raycast 方式)。
            #[cfg(target_os = "macos")]
            if let Some(overlay) = app.get_webview_window("overlay") {
                if let Err(e) = crate::overlay_panel::convert_overlay_to_panel(&overlay) {
                    tracing::error!("Failed to convert overlay to NSPanel: {}", e);
                }
            }

            // ★★ 常駐トレイ。⚠️ **窓を閉じると UI ごと消えるのに計測は生きている**という穴を塞ぐ
            //   (`tray.rs` のモジュールコメント参照)。★ 失敗しても起動は止めない
            //   — トレイが出ないことより、アプリが起動しないことのほうが重い。
            if let Err(e) = crate::tray::setup(app.handle(), session_active_for_tray) {
                tracing::error!("Failed to build the tray icon: {}", e);
            }
            Ok(())
        })
        // ⚠️★★ × で閉じたときに**プロセスを残さない**。
        //   `lib.rs` は実行時に `overlay` 窓を作るので、main を閉じても
        //   「全部の窓が閉じた」に到達せず、★ Tauri は終了しない。
        //   2026-08-08 に **3 時間動き続けていた実例**（CPU 157 分・記録継続中）を見つけた。
        //   ★ overlay の × は無視する（そもそも枠が無いが、将来 close されても道連れにしない）。
        .on_window_event(|window, event| {
            if !matches!(event, tauri::WindowEvent::CloseRequested { .. }) {
                return;
            }
            if window.label() == "overlay" {
                return;
            }
            tracing::info!("main window close requested -> shutting down");
            crate::shutdown_and_exit(window.app_handle());
        })
        .manage(engine)
        .manage(log_state)
        .manage(ResetSignal(should_reset))
        .manage(SessionActive(session_active))
        .manage(LatestFeatState(latest_feat))
        .manage(InterventionState(intervention_state))
        .manage(LogStatusState(log_target))
        .invoke_handler(tauri::generate_handler![
            greet,
            get_cognitive_state,
            get_intervention_decision,
            force_nudge,
            debug_force_probe,
            // ⚠️★★★ 研究者向け (GSE_DEBUG=1 必須)。被験者ビルドでは Err を返す。
            get_ime_shadow_debug,
            debug_overlay_window_state,
            get_log_status,
            get_g1_mode,
            // G1 自動提出 (★ すべて G1 モード限定の画面からしか呼ばれない)。
            get_g1_participant_id,
            set_g1_participant_id,
            get_submission_status,
            approve_pending_submissions,
            record_intervention_dismiss,
            get_keyboard_idle_ms,
            get_last_keypress_timestamp,
            get_hook_status,
            get_diagnostics,
            reset_input_monitoring,
            reset_accessibility,
            open_accessibility_settings,
            start_session,
            set_overlay_interactive,
            quit_app,
            get_session_file,
            // ⚠️★★★ O1 (R3): ADR-014 D7 の 3 点セット (稼働中インジケータ / 即時の一時停止 /
            //   事後の区間指定削除)。★ **判断 3 の根拠 3 がこの 3 つで立っている。**
            get_recording_status,
            set_recording_paused,
            delete_time_range,
            // ⚠️★★★ O1 (R3): 作業の種類の宣言 (ADR-016 判断 4 / 4b)。
            //   ★ O1 モードの画面からしか呼ばれない (非 O1 では `Err` を返す)。
            get_o1_mode,
            declare_task_kind,
            get_o1_enrollment,
            acknowledge_o1_enrollment,
            submit_latest_session,
            record_user_label,
            record_session_meta,
            record_realtime_answer,
            record_realtime_skip,
            record_self_marker,
            record_vignette_response,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[cfg(test)]
mod shutdown_tests {
    use super::*;

    /// ⚠️★ 終了の入口は 4 つある（画面 / スタート画面 / トレイ / ×）。
    /// **2 回目以降は通さない** — 通すとログを閉じる待ち合わせが二重になり `exit(0)` が競合する。
    #[test]
    fn only_the_first_shutdown_request_is_claimed() {
        let flag = AtomicBool::new(false);
        assert!(claim_shutdown(&flag), "★ 1 回目は通るはず");
        assert!(!claim_shutdown(&flag), "★ 2 回目は弾くはず");
        assert!(!claim_shutdown(&flag), "★ 3 回目も弾くはず");
    }

    /// ⚠️★ G1（被験者の端末）では分析起動もフォルダ表示もしない。
    #[test]
    fn g1_exit_never_opens_the_folder() {
        assert!(
            !wants_researcher_exit_flow(false, "/tmp/gse_20260808_010101.ndjson"),
            "★ G1 なのに被験者の画面へフォルダを開こうとしている"
        );
    }

    /// ⚠️★ セッションパスが空なら、研究者運用でも何も開かない。
    ///
    /// ★ `Path::new("").parent()` は `Some("")` を返すので、**意図しないフォルダが開く**。
    /// スタート画面に終了ボタンを足したことで「未開始のまま終了」が現実的になった。
    #[test]
    fn empty_session_path_never_opens_the_folder() {
        assert!(!wants_researcher_exit_flow(true, ""));
        assert!(!wants_researcher_exit_flow(true, "   "));
    }

    /// 研究者運用 + 実パスのときだけ従来どおり動く（★ 非回帰）。
    #[test]
    fn researcher_flow_still_runs_for_a_real_session() {
        assert!(wants_researcher_exit_flow(
            true,
            "/tmp/gse_20260808_010101.ndjson"
        ));
    }
}

#[cfg(test)]
mod task_c_command_tests {
    use super::*;

    // #1 層2: 誤誘導ラベル是正 — Full と Disconnected を文言で区別すること。
    #[test]
    fn log_send_error_distinguishes_full_and_disconnected() {
        let (tx, rx) = crossbeam_channel::bounded::<u8>(1);
        tx.try_send(0).unwrap(); // 容量 1 を満杯にする
        let full = tx.try_send(1).unwrap_err();
        let full_msg = log_send_error(full);
        assert!(full_msg.contains("full"), "got: {}", full_msg);
        assert!(!full_msg.contains("disconnected"), "got: {}", full_msg);

        drop(rx); // receiver を落として Disconnected を作る
        let disc = tx.try_send(2).unwrap_err();
        let disc_msg = log_send_error(disc);
        assert!(disc_msg.contains("disconnected"), "got: {}", disc_msg);
    }

    /// ⚠️★★★ **「触る前に断る」ためのガード** (G-1・2026-08-19)。
    ///
    /// ## ★ なぜ `try_send` の失敗を拾うだけでは足りないか
    ///
    /// ⚠️★★★ **稼働中インジケータの 3 値** (研究者判断 R-11・2026-08-26)。
    ///
    /// ★ 同意文書 §4 の逐語「印が出ていないときは記録していません」を守るには、
    /// ⚠️ **「止めた」と「壊れている」を分けて出す**必要がある
    /// (★ トレイの `MeasureState` が `Stopped` と `HookDown` を分けたのと同じ理屈)。
    #[test]
    fn recording_health_separates_paused_from_broken() {
        // ★ 正常
        assert_eq!(recording_health(false, true, false, true).0, "recording");
        // ★ 被験者が止めた —— ⚠️ **最優先**。止めているあいだフックが遊ぶのは当たり前なので、
        //   ここで「壊れています」と出すと**自分の操作を故障と誤解する**。
        for installed in [false, true] {
            for starved in [false, true] {
                for log_ok in [false, true] {
                    assert_eq!(
                        recording_health(true, installed, starved, log_ok).0,
                        "paused",
                        "paused=true のとき常に paused であること"
                    );
                }
            }
        }
        // ⚠️★★★ 止めていないのに記録できていない = **broken**
        //   (★ 旧実装はここを "recording" と出していた)
        assert_eq!(recording_health(false, false, false, true).0, "broken");
        assert_eq!(recording_health(false, true, true, true).0, "broken");
        assert_eq!(recording_health(false, true, false, false).0, "broken");
        // ★ broken のときは必ず被験者向けの 1 行が付く (⚠️ 黙って赤くしない)
        for args in [
            (false, false, false, true),
            (false, true, true, true),
            (false, true, false, false),
        ] {
            let (h, d) = recording_health(args.0, args.1, args.2, args.3);
            assert_eq!(h, "broken");
            assert!(d.is_some(), "broken なのに説明が無い: {args:?}");
        }
        // ★ 正常 / 停止では説明を付けない
        assert!(recording_health(false, true, false, true).1.is_none());
        assert!(recording_health(true, true, false, true).1.is_none());
    }

    /// ⚠️★★★ **O1 では「被験者に見えるもの」だけが遅れる** (研究者判断 2026-08-28)。
    ///
    /// ★ このテストが要る理由 (security-checker HIGH・2026-08-28): `HOOK_STARVED` の読み手は
    /// トレイだけでなく **`recording_health` 経由のアプリ内バッジ**でもある。
    /// ⚠️ その連鎖は `liveness` の単体テストからも `recording_health` の単体テストからも
    /// **見えない**ので、★ ここで**つないだ形**を固定する。
    ///
    /// - 2 分: O1 は `"recording"` のまま (⚠️ 誤警告を出さない) / 通常運用は従来どおり `"broken"`
    /// - 30 分: ★ O1 でも `"broken"` になる (⚠️ **永久には隠さない**)
    #[test]
    fn o1_delays_the_broken_badge_but_normal_mode_is_unchanged() {
        use crate::input::liveness::{self, HookHealth, Starvation, Thresholds};
        const O1_TRAY_AFTER_MS: u64 = 1_800_000;

        let th = Thresholds::default();
        let at_2min = Starvation {
            starved_ms: 120_000,
        };
        let at_30min = Starvation {
            starved_ms: O1_TRAY_AFTER_MS,
        };

        // ★ 前提: 2 分で `Down` である (= 再設置と NDJSON は動いている)。
        assert_eq!(liveness::health(at_2min, th), HookHealth::Down);

        // ⚠️ O1: 2 分では**見せない** → バッジは "recording" のまま。
        let shown_o1 = liveness::participant_visible_starved(
            liveness::health(at_2min, th),
            at_2min,
            Some(O1_TRAY_AFTER_MS),
        );
        assert!(!shown_o1, "O1 で 2 分の誤警告を出してはならない");
        assert_eq!(recording_health(false, true, shown_o1, true).0, "recording");

        // ★ 通常運用 / G1: 従来どおり "broken" (⚠️ 挙動を変えていないことの対照)。
        let shown_normal =
            liveness::participant_visible_starved(liveness::health(at_2min, th), at_2min, None);
        assert!(shown_normal);
        assert_eq!(
            recording_health(false, true, shown_normal, true).0,
            "broken"
        );

        // ⚠️★ 30 分に達したら O1 でも "broken" になる (★ 隠し続けない)。
        let shown_late = liveness::participant_visible_starved(
            liveness::health(at_30min, th),
            at_30min,
            Some(O1_TRAY_AFTER_MS),
        );
        assert!(shown_late, "O1 でも 30 分で被験者に知らせること");
        let (h, d) = recording_health(false, true, shown_late, true);
        assert_eq!(h, "broken");
        assert!(d.is_some(), "broken なのに説明が無い");
    }

    /// `start_session` は `engine.reset()` / `reset_signal` / `latest_feat` / `intervention` を
    /// **`session_active` の `swap` より前に**書き換える (分析スレッドとの可視性順序のため・
    /// この順序は動かせない)。→ ⚠️ **送信が失敗した時点では、もう巻き戻せない副作用が出ている。**
    /// → ★ そこで「これから送るぶんの空きがあるか」を**状態を 1 つも触る前に**確かめる。
    #[test]
    fn log_capacity_guard_rejects_when_full() {
        let (tx, _rx) = crossbeam_channel::bounded::<LogEntry>(3);
        // 空: 2 通ぶんの空きがある。
        assert!(log_channel_has_room(&tx, 2));

        tx.try_send(LogEntry::SessionStart { timestamp: 1 })
            .unwrap();
        // 残り 2: ちょうど足りる (境界)。
        assert!(log_channel_has_room(&tx, 2));

        tx.try_send(LogEntry::SessionStart { timestamp: 2 })
            .unwrap();
        // 残り 1: ⚠️ 足りない → ここで断らないと Rotate だけが落ちて
        //   SessionStart が**閉じ終わった旧ファイル**に積まれる。
        assert!(!log_channel_has_room(&tx, 2));
        assert!(log_channel_has_room(&tx, 1));

        tx.try_send(LogEntry::SessionStart { timestamp: 3 })
            .unwrap();
        assert!(!log_channel_has_room(&tx, 1));
        // ★ 0 通は常に真 (何も送らないなら空きは要らない)。
        assert!(log_channel_has_room(&tx, 0));
    }

    #[test]
    fn build_probe_ref_random_requires_valid_id() {
        // 有効な 16 文字 → RandomProbe。
        assert_eq!(
            build_probe_ref("random_probe", Some("ABCDEFGHIJKLMNOP".to_string())),
            Ok(ProbeRef::RandomProbe {
                probe_id: "ABCDEFGHIJKLMNOP".to_string()
            })
        );
        // 不正形式 (短い / 文字種違反) → Err。
        assert!(build_probe_ref("random_probe", Some("short".to_string())).is_err());
        assert!(build_probe_ref("random_probe", Some("bad.char12345678".to_string())).is_err());
        // probe_id 欠落 → Err。
        assert!(build_probe_ref("random_probe", None).is_err());
    }

    #[test]
    fn build_probe_ref_self_marker_rejects_probe_id() {
        assert_eq!(
            build_probe_ref("self_marker", None),
            Ok(ProbeRef::SelfMarker)
        );
        // self_marker が probe_id を持つのは不整合 → Err (#7 / DC-3)。
        assert!(build_probe_ref("self_marker", Some("ABCDEFGHIJKLMNOP".to_string())).is_err());
    }

    #[test]
    fn build_probe_ref_rejects_unknown_source() {
        assert!(build_probe_ref("bogus", None).is_err());
    }

    #[test]
    fn is_valid_opaque_id_accepts_ids_rejects_junk() {
        assert!(is_valid_opaque_id("v1"));
        assert!(is_valid_opaque_id("v8"));
        assert!(!is_valid_opaque_id("")); // 空
        assert!(!is_valid_opaque_id("has space")); // 空白
        assert!(!is_valid_opaque_id("toolong-toolong-x")); // 17 文字 (>16)
        assert!(!is_valid_opaque_id("本文")); // マルチバイト/本文
    }

    // --- capture-schema-freeze: 固定カテゴリ検証 (IPC 境界) ---

    #[test]
    fn parse_optional_condition_accepts_known_rejects_unknown() {
        assert_eq!(parse_optional_condition(None), Ok(None)); // 省略
        assert_eq!(parse_optional_condition(Some("")), Ok(None)); // 空文字 = 省略扱い
        assert_eq!(
            parse_optional_condition(Some("blind_calibration")),
            Ok(Some(Condition::BlindCalibration))
        );
        assert_eq!(
            parse_optional_condition(Some("nudge")),
            Ok(Some(Condition::Nudge))
        );
        // 未知値は黙って捨てず Err。
        assert!(parse_optional_condition(Some("bogus")).is_err());
        assert!(parse_optional_condition(Some("BLIND_CALIBRATION")).is_err()); // 大文字は別物
    }

    #[test]
    fn parse_optional_label_pool_accepts_known_rejects_unknown() {
        assert_eq!(parse_optional_label_pool(None), Ok(None));
        assert_eq!(parse_optional_label_pool(Some("")), Ok(None));
        assert_eq!(
            parse_optional_label_pool(Some("calibration_blind")),
            Ok(Some(LabelPool::CalibrationBlind))
        );
        assert!(parse_optional_label_pool(Some("pool")).is_err());
    }

    #[test]
    fn parse_dismiss_reason_defaults_silent_rejects_unknown() {
        // 省略/空 = silent (フェード相当)。
        assert_eq!(parse_dismiss_reason(None), Ok(DismissReason::Silent));
        assert_eq!(parse_dismiss_reason(Some("")), Ok(DismissReason::Silent));
        assert_eq!(
            parse_dismiss_reason(Some("not_stuck")),
            Ok(DismissReason::NotStuck)
        );
        assert_eq!(
            parse_dismiss_reason(Some("want_to_struggle")),
            Ok(DismissReason::WantToStruggle)
        );
        // 未知値は Err (黙って silent に倒さない)。
        assert!(parse_dismiss_reason(Some("whatever")).is_err());
    }
}

#[cfg(test)]
mod submit_command_tests {
    use super::{extract_age_path, redact_home_path, redact_prefixes};
    // participant_id 検証の規則テストは crate::participant_id (単一情報源) 側に置く。

    /// ⚠️★★★ **env を読む側 (`redact_home_path`) にも検査を置く** (security review MEDIUM, 2026-09-12)。
    ///
    /// ★ 従来は純関数 `redact_prefixes` しか覆われておらず、**env を読む経路が無保護**だった。
    /// ⚠️ そこが壊れると (キー名の typo / `var_os` → `var` 置換など) `homes` が空になり、
    /// `redact_prefixes(detail, &[])` が**入力をそのまま返す**。
    /// → ⚠️ 被験者に見せる提出失敗メッセージへ **OS ユーザー名を含むフルパスが素通り**する。
    /// ★ 黙って壊れる型の欠陥なので、テストで止める。
    ///
    /// ⚠️ **env を書かない** (★ `set_var` は他のテストと競合し `unsafe` でもある)。
    ///
    /// ⚠️★★★ **2026-09-12 (R-4): env が取れないときは `panic!` する** —— 以前は
    /// 無音で `return` していた (= skip)。★ しかしそれでは **「通った」と「skip した」が
    /// CI ログで区別できず**、⚠️ **回帰保護が実質無効なまま緑に見える**。
    /// ★ これは `silent-success-is-not-visible` と同型の欠陥である。
    /// ⚠️ 本テストが守っているのは **被験者に見せる提出失敗メッセージへ OS ユーザー名を含む
    /// フルパスが素通りする経路**なので、「守っているつもりで守っていない」状態が最も悪い。
    /// → ★ **env の不在は skip の理由ではなく、前提の崩壊として赤にする。**
    /// ★ CI 側は `check` job の「env 前提の検査」step が先に鳴るので、
    /// ⚠️ この panic が出たときは「実行環境の前提が変わった」と読む
    /// (★ どちらの step が赤いかで原因が分かれる)。
    #[test]
    fn redact_home_path_masks_real_home_from_env() {
        let Some(home) = ["USERPROFILE", "HOME"]
            .iter()
            .filter_map(std::env::var_os)
            .map(|v| v.to_string_lossy().into_owned())
            .find(|s| !s.is_empty())
        else {
            // ⚠️ 値そのものは出さない (★ OS ユーザー名が入る = まさに本テストが守る情報)。
            panic!(
                "USERPROFILE / HOME がどちらも読めない。\
                 ★ このテストは `redact_home_path` の **env を読む経路** の回帰保護であり、\
                 skip すると保護が無効なまま緑になる。\
                 → ⚠️ 実行環境に少なくとも一方を立てること (CI は `check` job の検査 step 参照)。"
            );
        };

        let detail = format!("could not read input {home}/Documents/GSE-sessions/x.ndjson: nope");
        let masked = redact_home_path(&detail);

        // ⚠️★★★ **失敗メッセージにも実ホームを出さない** (security review LOW, 2026-09-12)。
        //   ★ このテストが失敗するのは **`masked` がホームを含んでしまったとき**なので、
        //   ⚠️ `masked` をそのまま出すと **失敗ログに OS ユーザー名が出る** ——
        //   ★ つまり **守っている当の情報を、守りが壊れた瞬間に自分で漏らす**。
        //   ⚠️ CI ログのマスクは登録済み secret にしか効かないので、ここが唯一の防御である。
        //   → ★ 伏せてもなお「どこが伏せ損ねたか」の**構造は読める**ようにする。
        //
        // ⚠️★★★ **ユーザー名単体も伏せる** (code review MEDIUM, 2026-09-12)。
        //   ★ `home` の完全一致だけを伏せると、**部分的にしか伏せ損ねない退行**を取りこぼす ——
        //   例: `USERPROFILE` 側だけ置換されて `~\johnd/Documents/...` になった場合、
        //   ⚠️ 1 つ目の assert は通り (完全一致の `home` を含まない)、
        //   **2 つ目の assert の失敗メッセージに OS ユーザー名が残る**。
        let user = std::path::Path::new(&home)
            .file_name()
            .map(|s| s.to_string_lossy().into_owned())
            .unwrap_or_default();
        let show = |s: &str| {
            let t = s.replace(&home, "<HOME>");
            if user.is_empty() {
                t
            } else {
                t.replace(&user, "<USER>")
            }
        };

        assert!(
            !masked.contains(&home),
            "home leaked: masked={}",
            show(&masked)
        );
        assert!(
            masked.contains("~/Documents/GSE-sessions/x.ndjson"),
            "got: {}",
            show(&masked)
        );
        // ★ ホームを含まない文字列は素通し (⚠️ 過剰な伏せ字で原因が読めなくならないこと)。
        assert_eq!(redact_home_path("no path here"), "no path here");
    }

    #[test]
    fn redact_prefixes_masks_home_without_touching_env() {
        // env を触らない純関数テスト (並列テスト安全)。
        let homes = vec!["/Users/tanaka_taro".to_string()];
        let masked = redact_prefixes(
            "could not read input /Users/tanaka_taro/Documents/GSE-sessions/x.ndjson: nope",
            &homes,
        );
        assert!(!masked.contains("tanaka_taro"), "home leaked: {masked}");
        assert!(
            masked.contains("~/Documents/GSE-sessions/x.ndjson"),
            "got: {masked}"
        );
        // ホームを含まない文字列はそのまま。空 homes でも無変化。
        assert_eq!(redact_prefixes("no path here", &homes), "no path here");
        assert_eq!(redact_prefixes("plain", &[]), "plain");
    }

    #[test]
    fn extract_age_path_picks_dot_age_line() {
        // submit.rs の実際の出力形 (「提出ファイルの場所:」の次行にインデント付きパス)。
        let stdout = "✓ 最新セッションを匿名化 (12 行) → age 暗号化しました。\n\n  \
             提出ファイルの場所:\n    /Users/p/Documents/GSE-submissions/P006_gse_x.age\n\n\
             → このファイルを研究者の Dropbox に提出してください。";
        assert_eq!(
            extract_age_path(stdout).as_deref(),
            Some("/Users/p/Documents/GSE-submissions/P006_gse_x.age")
        );
    }

    #[test]
    fn extract_age_path_none_when_absent() {
        assert_eq!(extract_age_path("no path here\njust text"), None);
        assert_eq!(extract_age_path(""), None);
    }
}

/// ★ 提出レシート (「送信しました」) の根拠に関するテスト。
///
/// ⚠️★★ ここで守っているのは **「押した ≠ 送れた」** である。レシートは
/// 収束器が `.sent` を置いた本数 (`GSE_RECONCILE` の `sent`) からしか作られない。
#[cfg(test)]
mod submission_receipt_tests {
    use super::{
        now_epoch_ms, record_sent_if_any, reset_sent_receipt, summary_count, InFlightGuard,
        ReconcileReason, SUBMIT_IN_FLIGHT, SUBMIT_IN_FLIGHT_REASON, SUBMIT_IN_FLIGHT_SINCE_MS,
        SUBMIT_LAST_SENT_COUNT, SUBMIT_LAST_SENT_MS,
    };
    use std::sync::atomic::Ordering;

    /// ⚠️★★★ **本モジュールのプロセス共有グローバルを触るテストは、必ずこのロックを取る。**
    ///
    /// ★ 対象: `SUBMIT_IN_FLIGHT` / `SUBMIT_IN_FLIGHT_REASON` / `SUBMIT_IN_FLIGHT_SINCE_MS`
    /// / `SUBMIT_LAST_SENT_MS` / `SUBMIT_LAST_SENT_COUNT`。
    ///
    /// ⚠️ `cargo test` は既定で並列に走るので、これらを触るテストが 2 本以上あると
    /// ★ 互いの値を踏み合って **単独では緑・全体では赤**になる
    /// (`packaging.rs` の一時ディレクトリ衝突と同じ形)。
    ///
    /// ⚠️★★ **2026-09-02 に実際に踏んだ。** 旧版はこのロックを `IN_FLIGHT_TEST_LOCK` と呼び、
    /// `SUBMIT_IN_FLIGHT*` を触る 2 本にだけ掛けていた。★ 一方
    /// `SUBMIT_LAST_SENT_*` を書き換える 2 本 (`only_a_real_send_writes_the_receipt` /
    /// `reset_sent_receipt_clears_both_values`) は **どちらもロックを取っていなかった**
    /// ——「危険は分かっていたのに防御が半分にしか掛かっていない」形である。
    /// → ⚠️ CI (mac) で `only_a_real_send_writes_the_receipt` が落ち、
    ///   手元でも **40 回中 1 回**再現した。★ ロック名を実体に合わせて改名した上で
    ///   **グローバルを触る 4 本すべて**に掛ける。
    static SUBMIT_GLOBALS_TEST_LOCK: std::sync::Mutex<()> = std::sync::Mutex::new(());

    /// ⚠️★ 旧コメントは「静的変数を共有するので、**この 1 関数の中で**順に検査する
    /// (並列テスト安全)」と書いていたが、★ **誤りである。**
    /// 1 関数の中で順に見ても、**別のテスト関数**が同じ static を触れば防げない
    /// (それが 2026-09-02 に起きたことである)。→ ロックで守る。
    #[test]
    fn only_a_real_send_writes_the_receipt() {
        let _lock = SUBMIT_GLOBALS_TEST_LOCK
            .lock()
            .unwrap_or_else(|p| p.into_inner());
        SUBMIT_LAST_SENT_MS.store(0, Ordering::Relaxed);
        SUBMIT_LAST_SENT_COUNT.store(0, Ordering::Relaxed);

        // ① 要約行が読めない (収束器が古い / 出力が壊れた) → 何も書かない。
        record_sent_if_any(None, || 1_000);
        assert_eq!(
            SUBMIT_LAST_SENT_MS.load(Ordering::Relaxed),
            0,
            "★ 根拠が無いのにレシートを出してはならない"
        );

        // ② `sent: 0` (= 送るものが無かった / 送れなかった) → 何も書かない。
        record_sent_if_any(Some(0), || 2_000);
        assert_eq!(
            SUBMIT_LAST_SENT_MS.load(Ordering::Relaxed),
            0,
            "★ 0 件をレシートにしてはならない"
        );

        // ③ 実際に送れた → 時刻と件数が入る。
        record_sent_if_any(Some(2), || 3_000);
        assert_eq!(SUBMIT_LAST_SENT_MS.load(Ordering::Acquire), 3_000);
        assert_eq!(SUBMIT_LAST_SENT_COUNT.load(Ordering::Relaxed), 2);

        // ④ ⚠️★★ その後の「送るものが無い」実行でレシートが**消えてはならない**。
        //    収束器はアプリ起動のたびに走り、平常時はほぼ毎回 `sent: 0` である。
        //    ここで 0 を書くと、被験者から見て「出て、すぐ消えた」になる。
        record_sent_if_any(Some(0), || 4_000);
        assert_eq!(
            SUBMIT_LAST_SENT_MS.load(Ordering::Acquire),
            3_000,
            "★ 送れた事実は次の空振りで消えてはならない"
        );
        assert_eq!(SUBMIT_LAST_SENT_COUNT.load(Ordering::Relaxed), 2);

        // ⑤ 次に送れたら更新される。
        record_sent_if_any(Some(1), || 5_000);
        assert_eq!(SUBMIT_LAST_SENT_MS.load(Ordering::Acquire), 5_000);
        assert_eq!(SUBMIT_LAST_SENT_COUNT.load(Ordering::Relaxed), 1);

        SUBMIT_LAST_SENT_MS.store(0, Ordering::Relaxed);
        SUBMIT_LAST_SENT_COUNT.store(0, Ordering::Relaxed);
    }

    /// ★ `gse-submit` が実際に出す形の要約行から `sent` が読めること
    /// (⚠️ ここが読めないと、レシートは永久に出ない = 沈黙に戻る)。
    #[test]
    fn sent_is_read_from_the_real_summary_line() {
        // submit.rs `main()` の `serde_json::json!` と同じキー並び。
        let line = r#"{"packaged":1,"sent":1,"unsent":0,"upload_disabled":false,"skipped_busy":false,"awaiting_approval":0,"errors":0}"#;
        assert_eq!(summary_count(line, "sent"), Some(1));
        assert_eq!(summary_count(line, "unsent"), Some(0));
        // 知らないキーは None (勝手に 0 と読まない)。
        assert_eq!(summary_count(line, "nope"), None);
    }

    /// ⚠️★ 番兵が panic でも in-flight を戻すこと。
    /// 戻し忘れると画面が「送信しています…」のまま**永久に固まる**。
    #[test]
    fn in_flight_returns_to_zero_even_on_panic() {
        let _lock = SUBMIT_GLOBALS_TEST_LOCK
            .lock()
            .unwrap_or_else(|p| p.into_inner());
        SUBMIT_IN_FLIGHT.store(0, Ordering::Relaxed);
        let r = std::panic::catch_unwind(|| {
            let _g = InFlightGuard::new(ReconcileReason::Approval);
            assert_eq!(SUBMIT_IN_FLIGHT.load(Ordering::Relaxed), 1);
            panic!("収束器が落ちた");
        });
        assert!(r.is_err(), "★ panic を捕まえられていない");
        assert_eq!(
            SUBMIT_IN_FLIGHT.load(Ordering::Relaxed),
            0,
            "★ 送信中のまま固まる"
        );
        // ⚠️★ きっかけと開始時刻も戻ること。戻し忘れると画面が
        //   「起動時のスキャンではない」と読み続け、★ 送信中カードが出たままになる。
        assert_eq!(
            SUBMIT_IN_FLIGHT_REASON.load(Ordering::Acquire),
            0,
            "★ きっかけが残っている"
        );
        assert_eq!(
            SUBMIT_IN_FLIGHT_SINCE_MS.load(Ordering::Acquire),
            0,
            "★ 開始時刻が残っている"
        );
    }

    /// ⚠️★★ **入れ子でも、最後の 1 本が抜けるまできっかけを消さないこと。**
    ///
    /// ブロック終了経路は `emit` の前で番兵を立て、収束器スレッドへ渡す。
    /// ★ その最中に承認経路がもう 1 本立つと番兵が 2 本になる。
    /// ⚠️ 内側が落ちた時点で 0 に戻すと、**まだ送っているのに送信中カードが消える**。
    #[test]
    fn nested_guards_keep_the_reason_until_the_last_one_drops() {
        let _lock = SUBMIT_GLOBALS_TEST_LOCK
            .lock()
            .unwrap_or_else(|p| p.into_inner());
        SUBMIT_IN_FLIGHT.store(0, Ordering::Relaxed);
        SUBMIT_IN_FLIGHT_REASON.store(0, Ordering::Relaxed);
        let outer = InFlightGuard::new(ReconcileReason::BlockEnd);
        {
            let _inner = InFlightGuard::new(ReconcileReason::Approval);
            assert_eq!(SUBMIT_IN_FLIGHT.load(Ordering::Acquire), 2);
        }
        assert_eq!(SUBMIT_IN_FLIGHT.load(Ordering::Acquire), 1);
        assert_ne!(
            SUBMIT_IN_FLIGHT_REASON.load(Ordering::Acquire),
            0,
            "★ 内側が抜けただけできっかけを消した = 送信中カードが早く消える"
        );
        drop(outer);
        assert_eq!(SUBMIT_IN_FLIGHT_REASON.load(Ordering::Acquire), 0);
        assert_eq!(SUBMIT_IN_FLIGHT_SINCE_MS.load(Ordering::Acquire), 0);
    }

    /// ⚠️★ `now_epoch_ms()` は **`0` を返さない**。`0` は `last_sent_ms` の
    /// 「まだ 1 件も送っていない」センチネルなので、衝突すると
    /// ★ 実際に送れてもレシートが永久に出ない。
    #[test]
    fn now_epoch_ms_never_returns_the_sentinel() {
        assert_ne!(now_epoch_ms(), 0);
    }

    /// ★ レシートの根拠を捨てる操作が、両方の値を落とすこと。
    #[test]
    fn reset_sent_receipt_clears_both_values() {
        let _lock = SUBMIT_GLOBALS_TEST_LOCK
            .lock()
            .unwrap_or_else(|p| p.into_inner());
        SUBMIT_LAST_SENT_MS.store(1234, Ordering::Relaxed);
        SUBMIT_LAST_SENT_COUNT.store(7, Ordering::Relaxed);
        reset_sent_receipt();
        assert_eq!(SUBMIT_LAST_SENT_MS.load(Ordering::Acquire), 0);
        assert_eq!(SUBMIT_LAST_SENT_COUNT.load(Ordering::Acquire), 0);
    }
}

// ---------------------------------------------------------------------------
// ⚠️★★★ 研究者向け読み出しが「被験者に漏れない」ことを固定するテスト
// ---------------------------------------------------------------------------
//
// ★ ここで守る不変条件は **UI と backend にまたがる**ので、型では表せない。
//   → `capabilities.rs` と同じ様式で **ソースの実物**を検査する (ADR-013 §Context-4)。

#[cfg(test)]
mod debug_readout_tests {
    use super::*;
    use std::sync::atomic::Ordering::Relaxed;
    use std::sync::{Mutex, MutexGuard};

    static TALLY_LOCK: Mutex<()> = Mutex::new(());

    fn acquire() -> MutexGuard<'static, ()> {
        let g = TALLY_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        logger::reset_ime_shadow_tally();
        g
    }

    /// ★ 確定は `emitted - abandoned` で導出できる (別カウンタを持たない設計)。
    #[test]
    fn tally_counts_confirmed_and_abandoned() {
        let _g = acquire();
        logger::tally_ime_shadow(false);
        logger::tally_ime_shadow(true);
        logger::tally_ime_shadow(false);
        let (emitted, abandoned) = logger::ime_shadow_tally();
        assert_eq!(emitted, 3);
        assert_eq!(abandoned, 1);
        assert_eq!(emitted - abandoned, 2, "確定件数は差で出す");
    }

    /// ★ ローテートで 0 に戻る (⚠️ `log_path` と意味を揃えるため)。
    #[test]
    fn the_tally_resets_on_rotation() {
        let _g = acquire();
        logger::tally_ime_shadow(true);
        logger::tally_ime_shadow(false);
        assert_eq!(logger::ime_shadow_tally(), (2, 1));
        logger::reset_ime_shadow_tally();
        assert_eq!(
            logger::ime_shadow_tally(),
            (0, 0),
            "ローテート後も前ファイルの件数が残っている"
        );
    }

    /// ⚠️★★★ **並行下でも `abandoned <= emitted` が破れないこと。**
    ///
    /// ★ 2026-09-11 の review HIGH への回帰テスト。
    /// ⚠️ 旧実装は書き手が `ABANDONED` を**先**に増やしており、
    /// **共有状態そのものが `abandoned = emitted + 1` を通っていた**
    /// (★ 5000 万回の実測で 1034 万回の違反が報告された)。
    /// ⚠️ 旧テストは**単一スレッド**で `n <= n + 1` を見るだけだったので**自明に真**で、
    /// この欠陥を取り逃がした。→ ★ **書き手を別スレッドに立てて読む**。
    #[test]
    fn abandoned_never_exceeds_emitted_under_concurrency() {
        let _g = acquire();
        let stop = std::sync::Arc::new(std::sync::atomic::AtomicBool::new(false));
        let stop_w = stop.clone();
        let writer = std::thread::spawn(move || {
            while !stop_w.load(Relaxed) {
                // ⚠️ **すべて放棄**にするのが最悪条件 (2 つのカウンタが同じ速さで進む)。
                logger::tally_ime_shadow(true);
            }
        });
        let mut violations = 0u64;
        for _ in 0..2_000_000 {
            let (emitted, abandoned) = logger::ime_shadow_tally();
            if abandoned > emitted {
                violations += 1;
            }
        }
        stop.store(true, Relaxed);
        writer.join().expect("writer スレッドが panic した");
        assert_eq!(
            violations, 0,
            "abandoned > emitted を {violations} 回観測した (順序の不変条件が破れている)"
        );
        logger::reset_ime_shadow_tally();
    }

    /// ⚠️★★★ **backend ゲートが外れていないこと。**
    /// ★ `get_ime_shadow_debug` は `ensure_debug_enabled()?` を必ず通る。
    ///
    /// ⚠️★★★ **2026-09-11 に fail-open を 2 つ塞いだ** (review MEDIUM):
    /// 1. 旧版は文字列の**存在**しか見ておらず、`// ensure_debug_enabled()?;` と
    ///    **コメントアウトされても緑**になった → ★ **最初の文**が一致することを見る。
    /// 2. 旧版は関数末尾が取れないと `unwrap_or(body.len())` で**ファイル末尾まで**走査し、
    ///    ⚠️ **このテスト自身のアサーション文字列**に当たって自分で自分を通していた
    ///    → ★ `expect` にして **fail-closed** にする。
    #[test]
    fn the_debug_command_is_gated_on_the_backend() {
        let src = include_str!("lib.rs");
        let at = src
            .find("fn get_ime_shadow_debug(")
            .expect("get_ime_shadow_debug が lib.rs に無い");
        let body = &src[at..];
        let end = body
            .find(
                "
}",
            )
            .expect("get_ime_shadow_debug の関数末尾が取れない (検査が無効になっている)");
        // ★ 関数シグネチャの次から、コメント・空行・`use` を飛ばした **最初の文**。
        //   ⚠️ `contains` だとコメントアウトされたゲートを弾けない。
        let first_stmt = body[..end]
            .lines()
            .skip(1)
            .map(str::trim)
            .find(|l| !l.is_empty() && !l.starts_with("//") && !l.starts_with("use "))
            .expect("get_ime_shadow_debug の本体が空");
        assert_eq!(
            first_stmt, "ensure_debug_enabled()?;",
            "get_ime_shadow_debug の先頭が backend ゲートでない (被験者ビルドで呼べてしまう)"
        );
    }

    /// ⚠️★★★ **被験者に見える診断パネルへ漏れていないこと。**
    ///
    /// ★ `get_diagnostics` が返す [`DiagnosticInfo`] は `Dashboard.tsx` で
    /// `debugView` に囲まれておらず、**フックが 20 秒以上有効にならないと被験者にも出る**。
    /// ⚠️ しかも `Object.entries` で全フィールドを吐くので、足した瞬間に漏れる。
    ///
    /// # ⚠️ 既知の限界 (`capabilities.rs` の同種検査と同じ性質)
    ///
    /// ★ これは**直書きの識別子**しか見ない。⚠️ `diag.extend(helper())` のように
    /// **ヘルパ経由**で入れられると素通りする。★ より強くするなら
    /// `get_diagnostics()` を実際に呼んでキー集合を固定値と照合する振る舞いテストにする。
    /// ⚠️ また検査対象は **`get_diagnostics` 1 関数だけ**で、
    /// 被験者に見える他の面 (`get_log_status` / `get_recording_status`) は保護外である。
    #[test]
    fn the_participant_visible_diagnostics_do_not_carry_the_tally() {
        let src = include_str!("lib.rs");
        let at = src
            .find("fn get_diagnostics(")
            .expect("get_diagnostics が lib.rs に無い");
        let body = &src[at..];
        let end = body
            .find(
                "
}",
            )
            .unwrap_or(body.len());
        for forbidden in ["IME_SHADOW_EMITTED", "IME_SHADOW_ABANDONED", "abandoned"] {
            assert!(
                !body[..end].contains(forbidden),
                "get_diagnostics に {forbidden} が入った。                 ★ あの診断は debugView で囲まれておらず被験者にも出る (較正のブラインドが壊れる)"
            );
        }
    }

    /// ⚠️★★★ **frontend ゲートが外れていないこと。**
    /// ★ 読み出しブロックは `debugView &&` の内側に無ければならない。
    #[test]
    fn the_readout_block_is_gated_on_the_frontend() {
        let src = include_str!("../../src/components/Dashboard.tsx");
        // ⚠️ ★ **呼び出し箇所**を狙う —— ★ 素朴に `find("get_ime_shadow_debug")` にすると
        //   interface の doc コメント (ファイル冒頭) に当たり、gate の外だと誤判定する
        //   (2026-09-11 に本テスト自身が踏んだ)。
        let at = src
            .find(r#"invoke<ImeShadowDebug>("get_ime_shadow_debug")"#)
            .expect("Dashboard.tsx が get_ime_shadow_debug を呼んでいない");
        // ★ 呼び出しの手前に `debugView &&` が在り、かつその間に閉じ括弧 `)}` が無いこと。
        let head = &src[..at];
        let gate = head
            .rfind("{debugView && (")
            .expect("読み出しの手前に debugView gate が無い");
        assert!(
            !head[gate..].contains(")}"),
            "debugView gate が読み出しブロックの前で閉じている (被験者に出てしまう)"
        );
    }
}
