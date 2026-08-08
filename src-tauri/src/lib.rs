pub mod analysis;
// アプリ本体の診断ログ (tracing) をファイルに残す writer。
// ⚠️ stdout だけだと Finder 起動の .app では**どこにも残らない** (2026-08-08 実測)。
pub mod applog;
// G1 統制タスク実験の「G1 モード」判定 (OS API 非依存の純ロジック + current_exe のみ)。
// 効果 (ローテート / 5 分でのブロック終了 / プローブ停止 / 二重起動 fail-loud) は lib.rs が適用する。
pub mod g1;
pub mod input;
pub mod logger;
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
// G1 自動提出の収束器 (ディスクの状態を突き合わせ、足りない仕事だけをする)。
// age と HTTP を使うので package feature 側 (`gse-submit --reconcile` が実行主体)。
#[cfg(feature = "package")]
pub mod reconcile;
// macOS: overlay 窓を非アクティブ NSPanel 化する FFI グルー (decisions D7)。
#[cfg(target_os = "macos")]
mod overlay_panel;
pub mod schema_dto;
#[cfg(target_os = "macos")]
pub mod sensors;
// メニューバー / タスクトレイの常駐アイコン (計測中かの表示 + いつでも終了)。
// ⚠️ 窓を閉じると UI ごと消えるのに計測は生きている、という穴を塞ぐ。
pub mod tray;
pub mod wall_server;

use crate::analysis::engine::{CognitiveState, CognitiveStateEngine};
use crate::analysis::intervention::{
    InterventionAction, InterventionDecision, InterventionInput, InterventionPolicyState,
};
use crate::analysis::loop_step::FeatSnapshot;
use crate::logger::{
    Condition, DismissReason, ExpectedQuadrant, LabelPool, LogEntry, LogStatus, ProbeRef,
    ProbeSource, SharedLogTarget, SkipReason, TaskKind, Track, UserLabelKind,
};
use crate::wall_server::WallServerState;
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

// デバッグ用: 次回の get_intervention_decision (main) で Wall を一度だけ強制発動するフラグ。
// `force_wall` コマンドが true にし、main ウィンドウの判定が swap で消費する (ワンショット)。
// 通常は false のまま = 既存挙動と完全同一 (pilot 非汚染)。
static FORCE_WALL: AtomicBool = AtomicBool::new(false);

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
    /// サーバスレッド (wall_server) に渡すためロガー Sender を clone して返す。
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
/// cooldown / daily cap / recent dismiss / Wall 累積時間を保持する。
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

/// デバッグ用: 次回の `get_intervention_decision` (main) で Wall を強制発動する。
/// Wall→QR→スマホ解除→介入応答 (A2) 捕捉の end-to-end 検証用。較正/開発時に
/// Dashboard のデバッグボタンからのみ呼ぶ。フラグを立てるだけで挙動は判定側がワンショット消費する。
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

#[tauri::command]
fn force_wall() -> Result<(), String> {
    ensure_debug_enabled()?;
    FORCE_WALL.store(true, Ordering::Release);
    Ok(())
}

/// デバッグ用: 次回の `get_intervention_decision` (overlay) で Nudge を一度だけ強制表示する。
/// nudge→dismiss→`record_intervention_dismiss` の経路を能動的に検証するため (#1 repro)。
/// `force_wall` と同方式のワンショットフラグ。Dashboard の debugView gate からのみ呼ぶ。
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
    is_monk_mode: bool,
    is_wall_active: bool,
    engine: State<CognitiveStateEngine>,
    latest_feat: State<LatestFeatState>,
    intervention: State<InterventionState>,
    log: State<Arc<Mutex<LogState>>>,
) -> InterventionDecision {
    // overlay WebView は表示専用。main 側ポーリングだけが policy state を進める。
    if window_label == "overlay" {
        // デバッグ強制 Nudge。**consumer は overlay 分岐**である点が FORCE_WALL と非対称:
        //   - FORCE_WALL  → main (非 overlay) 分岐で消費 (下記)。App が isWallActive を立て持続。
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
                    wall_accum_ms: decision.wall_accum_ms,
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

    // デバッグ強制 Wall (main ウィンドウのみ・ワンショット)。HMM 状態や介入トグルに依らず
    // 一度だけ action=wall を返す。App が isWallActive=true にすると次 tick から既存の
    // wall_active 分岐が Wall を維持する。reason="debug_force" でログし解析時に除外可能。
    if FORCE_WALL.swap(false, Ordering::AcqRel) {
        let now = epoch_ms();
        let idle_ms = get_keyboard_idle_ms();
        let decision = {
            let mut guard = intervention.0.lock().unwrap_or_else(|p| p.into_inner());
            guard.force_wall_decision(now, idle_ms)
        };
        let _ = log.lock().unwrap_or_else(|p| p.into_inner()).tx.try_send(
            LogEntry::InterventionDecision {
                timestamp: now,
                action: decision.action.as_str().to_string(),
                need_score: decision.need_score,
                opportunity_score: decision.opportunity_score,
                p_stuck: decision.p_stuck,
                idle_ms: decision.idle_ms,
                wall_accum_ms: decision.wall_accum_ms,
                reason: decision.reason.clone(),
                suppressed_by: decision.suppressed_by.clone(),
            },
        );
        return decision;
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
        monk_mode: is_monk_mode,
        wall_active: is_wall_active,
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
                wall_accum_ms: result.decision.wall_accum_ms,
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
            // Nudge dismiss は経過時間を持たない (Wall 応答のみ elapsed_ms を埋める)。
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
        diag.insert(
            "callback_count".into(),
            crate::input::hook::CALLBACK_COUNT
                .load(Ordering::Relaxed)
                .to_string(),
        );
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
                .find(|p| p.extension().map_or(false, |e| e == "app"))
                .map(|p| p.to_string_lossy().to_string())
                .unwrap_or_else(|| exe.to_string_lossy().to_string());
            diag.insert("bundle_path".into(), bundle_path);

            // quarantine xattr の有無
            if let Some(app_path) = exe
                .ancestors()
                .find(|p| p.extension().map_or(false, |e| e == "app"))
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
        return Err(format!(
            "提出ツール ({}) が見つかりません。配布パッケージが壊れている可能性があります。研究者に連絡してください。",
            submit_bin.display()
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
        .filter_map(|k| std::env::var_os(k))
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
}

/// 未送信件数と直近のエラーを返す。★ 0 件・エラー無しなら UI は何も出さない。
///
/// ⚠️ ★ 件数は **`unsent_age_files` と同じ規則**で数える (この参加者のブロック分だけ)。
/// 別々の規則にすると、画面の件数と実際に送られる対象が drift する。
#[tauri::command]
fn get_submission_status() -> SubmissionStatusDto {
    let (unsent, awaiting_approval) = match (
        crate::submission::default_submission_dir(),
        crate::submission::read_g1_participant_id(),
    ) {
        (Some(dir), Some(id)) => (
            crate::submission::unsent_count(&dir, &id),
            crate::submission::awaiting_approval_count(&dir, &id),
        ),
        _ => (0, 0),
    };
    let last_error = SUBMIT_LAST_ERROR
        .lock()
        .unwrap_or_else(|p| p.into_inner())
        .clone();
    SubmissionStatusDto {
        unsent,
        last_error,
        upload_disabled: SUBMIT_UPLOAD_DISABLED.load(Ordering::Relaxed),
        awaiting_approval,
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
    spawn_reconcile(app, "after approval");
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
    crate::submission::write_g1_participant_id(&id)
}

/// 収束器 (`gse-submit --reconcile`) を **別スレッドで** 1 回起こす。
///
/// ★ `reason` はログ用のきっかけ名 (`"at startup"` / `"after block"`)。
/// ⚠️ ★ **G1 モードでなければ何もしない** (通常運用の挙動を 1 バイトも変えない)。
/// ★ 何度呼んでも安全 (収束器はべき等) なので、二重起動を気にしなくてよい。
fn spawn_reconcile(app: tauri::AppHandle, reason: &'static str) {
    if g1_mode().is_none() {
        return;
    }
    thread::spawn(move || {
        // ⚠️ ★ **ブロック中には走らせない** (`design.md` §1: 測定中の端末に負荷をかけない)。
        //   起動時のヒントはスレッドで遅れて走るので、被験者が数秒後に「開始する」を押すと
        //   ★ **ブロック中に age 暗号化と送信が走りうる** (code-review LOW)。
        //   ★ 見送っても損失にならない (次のブロック終了で必ず拾われる)。
        if SESSION_START_MS.load(Ordering::Acquire) != 0 {
            tracing::info!(
                "G1 auto-submit ({}): skipped (a block is running; will run at block end)",
                reason
            );
            return;
        }
        let outcome = run_reconcile_blocking(&app);
        let mut slot = SUBMIT_LAST_ERROR.lock().unwrap_or_else(|p| p.into_inner());
        match outcome {
            Ok(Some(summary)) => {
                tracing::info!("G1 auto-submit ({}): {}", reason, summary);
                *slot = None;
            }
            Ok(None) => {
                // ★ 何もしなかった (ID 未登録)。⚠️ **失敗ではないので画面に出さない。**
                //   ⚠️ ★ 直前の失敗を **消しもしない** (成功していないため)。
                tracing::info!(
                    "G1 auto-submit ({}): skipped (participant id not registered yet)",
                    reason
                );
            }
            Err(e) => {
                // ⚠️ ログだけにしない。★ 画面へ出すために保持する。
                tracing::error!("G1 auto-submit ({}) FAILED: {}", reason, e);
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
    let id = match crate::submission::read_g1_participant_id() {
        Some(id) => id,
        None => return Ok(None),
    };
    let submit_bin = resolve_submit_bin()?;

    let mut cmd = std::process::Command::new(&submit_bin);
    cmd.arg("--reconcile");
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
    let kind = UserLabelKind::parse(&label).ok_or_else(|| format!("invalid label: {:?}", label))?;
    let timestamp = record_label_internal(&*log, kind)?;
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
fn is_valid_opaque_id(s: &str) -> bool {
    !s.is_empty()
        && s.len() <= 16
        && s.bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_')
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
#[tauri::command]
fn record_session_meta(
    track: String,
    task_kind: String,
    monk_mode: bool,
    intervention_enabled: bool,
    condition: Option<String>,
    label_pool: Option<String>,
    log: State<'_, Arc<Mutex<LogState>>>,
) -> Result<(), String> {
    let track = Track::parse(&track).ok_or_else(|| format!("invalid track: {:?}", track))?;
    let task_kind =
        TaskKind::parse(&task_kind).ok_or_else(|| format!("invalid task_kind: {:?}", task_kind))?;
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
            monk_mode,
            intervention_enabled,
            condition,
            label_pool,
        })
        .map_err(log_send_error)?;
    tracing::info!(
        "session_meta recorded: track={} task_kind={}",
        track.as_str(),
        task_kind.as_str()
    );
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
    log: State<'_, Arc<Mutex<LogState>>>,
) -> Result<(), String> {
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
        ))
        .map_err(log_send_error)?;
    Ok(())
}

/// overlay (macOS は NSPanel) のクリック受理を切り替える (decisions D9)。
/// `interactive=true` でカード/Wall がクリックを捕捉、`false` で背後アプリへ透過。
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
            // (setup 失敗等) と box/Wall のクリックブロックが無音で効かなくなるため可視化する
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

    // リセットシグナルを先にセットしてからセッションを有効化する。
    // 分析スレッドが active=true を Acquire で読んだ時点で、
    // それより前に Release された reset=true も可視であることが保証される。
    // 逆順だと、分析スレッドが active=true を見た瞬間に reset がまだ false で、
    // 前セッションの沈黙時間が初回更新に混入するレースコンディションが発生する。
    engine.reset();
    reset_signal.0.store(true, Ordering::Release);
    // ★ 旧値を取る。⚠️ 既に true (= 連打・record_session_meta 失敗後の再押下) なら
    //   **新しいブロックではない**ので、下のローテートを回してはならない (code-review HIGH)。
    let was_active = session_active.0.swap(true, Ordering::Release);
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    *latest_feat.0.lock().unwrap_or_else(|p| p.into_inner()) = None;
    *intervention.0.lock().unwrap_or_else(|p| p.into_inner()) = InterventionPolicyState::new(now);
    // ★ ロックは**ログへ送る間だけ**保持する (follow-up F-2 / code-review LOW)。
    //   以前は `win.show()` を含む関数末尾まで持っていた。デッドロックはしないが、
    //   ⚠️ ロック中にウィンドウ操作 (別スレッドへ波及しうる) を行う形は残さない。
    {
        let guard = log.lock().unwrap_or_else(|p| p.into_inner());

        // ★ G1: 2 ブロック目以降はログをローテートする (1 ブロック = NDJSON 1 ファイル・protocol.md §1)。
        //   ⚠️ ★ **G1 モードでないときは何もしない。** 通常運用 (Phase1) では「戻る → 開始する」で
        //   ファイルが分かれてしまうと、`gse-submit` が最新 1 本しか出さないため
        //   **前半が提出されなくなる**。既定の挙動を 1 バイトも変えないこと。
        // ⚠️★ **`was_active` が false のときだけ**ローテートする。
        //   「開始する」は送信中に disabled にならず、record_session_meta 失敗時の文言は
        //   **明示的に再押下を促す**ので、無条件に数えると孤児ファイルが 1 本増える
        //   (= protocol.md §1「1 ブロック = 1 ファイル」の破れ・code-review HIGH)。
        if g1_mode().is_some() && !was_active {
            let blocks_started = G1_BLOCKS_STARTED.fetch_add(1, Ordering::AcqRel);
            if blocks_started > 0 {
                // ⚠️ ファイル名は秒粒度。衝突回避は **logger スレッド側**でも行う
                // (ここは別スレッドなので exists 判定と create の間に窓がある・code-review MEDIUM)。
                let new_path = logger::next_session_path();
                tracing::info!(
                    "G1: rotating session log for block #{} -> {:?}",
                    blocks_started + 1,
                    new_path
                );
                if let Err(e) = guard.tx.try_send(LogEntry::Rotate { new_path }) {
                    // ⚠️★★ **ここで進んではならない** (cross-review HIGH・Claude と Codex が一致)。
                    // channel (bounded 512) が満杯だと Rotate だけが落ち、直後の SessionStart 以降が
                    // **既に `session_end` を書き終えた旧ファイル**に積まれる。
                    // = protocol.md §1 が (b) を却下した「沈黙して間違った結果を出す」失敗そのもの。
                    // ★ 触った状態を**全部巻き戻して** Err を返し、画面に出す (start_session の
                    // 失敗はフロントが「開始に失敗しました」と表示する)。
                    tracing::error!("G1: FAILED to rotate session log: {}", log_send_error(e));
                    G1_BLOCKS_STARTED.fetch_sub(1, Ordering::AcqRel);
                    session_active.0.store(false, Ordering::Release);
                    return Err("ログの切り替えに失敗しました。ブロックを開始できません。\
                         このブロックはまだ始まっていません。もう一度「開始する」を押してください。"
                        .to_string());
                }
            }
        }

        let _ = guard.tx.try_send(LogEntry::SessionStart { timestamp: now });
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
///   1. WallServer を停止 (ファイアウォールルール削除)
///   2. セッションログを閉じる (LogEntry::End を送信)
///   3. shutdown_rx でロガー完了を待機 (固定 sleep の代わり)
///   4. behavioral_gt.py でラベリング分析を実行 (Python が PATH にある場合)
///   5. セッションフォルダを Explorer で開く
#[tauri::command]
fn quit_app(app: tauri::AppHandle, log: State<Arc<Mutex<LogState>>>, wall: State<WallServerState>) {
    shutdown(&app, &log, &wall);
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
    let wall = app.state::<WallServerState>();
    shutdown(app, &log, &wall);
}

fn shutdown(app: &tauri::AppHandle, log: &Arc<Mutex<LogState>>, wall: &WallServerState) {
    if !claim_shutdown(&SHUTTING_DOWN) {
        tracing::info!("shutdown already in progress; ignoring the second request");
        return;
    }
    tracing::info!("shutdown requested");

    // WallServer を先に停止してファイアウォールルールを削除
    wall.stop();

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
// Phase 2b: IME Shadow Features (Windows のみ)
// ---------------------------------------------------------------------------

/// IME Shadow の Atomic データを読み取り、LogEntry::ImeShadow を送出する。
/// IME Monitor スレッドの active→false 遷移時に呼ばれる。
///
/// 2 つの経路で emit が発生する:
/// 1. 正常: WinEvent IME_HIDE が到着し IME_SHADOW_READY=true → dwell は事前計算済み
/// 2. Stale: IME_HIDE が取りこぼされ 8s タイムアウト → START_MS > 0 なら独自に dwell 計算
#[cfg(target_os = "windows")]
fn emit_ime_shadow(log_tx: &Sender<LogEntry>, timestamp: u64) {
    use std::sync::atomic::Ordering::Relaxed;
    // ⚠️★ G1: この経路は IME Monitor スレッドから呼ばれ、**`session_active` を見ていない**
    // (code-review HIGH)。ブロックを閉じた後に IME の後始末が飛んでくると
    // `session_end` の後ろに `ime_shadow` 行が続く。
    // ★ G1 モードのときだけ止める (通常運用の挙動は変えない)。
    // `SESSION_START_MS` はブロック終了時に 0 に戻されるので、これが「ブロック中か」を表す。
    if g1_mode().is_some() && SESSION_START_MS.load(Ordering::Acquire) == 0 {
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

    // キーストローク入力チャネル
    let (tx, rx) = crossbeam_channel::bounded::<crate::analysis::features::InputEvent>(64);

    // セッション開始リセットシグナル (start_session → 分析スレッド)
    let should_reset = Arc::new(AtomicBool::new(false));
    let should_reset_for_thread = should_reset.clone();

    // セッションアクティブフラグ (start_session まで false → 分析スレッドがドレイン)
    let session_active = Arc::new(AtomicBool::new(false));
    let session_active_for_thread = session_active.clone();
    // ★ G1: ブロック自動終了スレッド用 (5 分でブロックを閉じる)。
    let session_active_for_g1 = session_active.clone();
    // ★ トレイの状態表示用 (1Hz で読むだけ・書かない)。
    let session_active_for_tray = session_active.clone();

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
    let engine_for_monitor = engine.clone();
    let log_tx_ime_poll = log_tx.clone();
    let log_tx_for_monitor = log_tx.clone();
    let log_tx_probe = log_tx.clone();
    let log_tx_g1 = log_tx.clone();
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

        loop {
            // start_session が呼ばれるまでチャネルをドレインして処理をスキップする。
            if !session_active_for_thread.load(Ordering::Acquire) {
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
            let ime_open = input::hook::IME_OPEN.load(Ordering::Relaxed);
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
                });
            }
        }
    });

    // IME モニタースレッド
    thread::spawn(move || {
        tracing::info!("IME Monitor thread started");
        let monitor = input::ime::ImeMonitor::new();
        // IME_ACTIVE が true になった時刻。8 秒以上続いたら EVENT_OBJECT_IME_HIDE
        // 取りこぼしと判断してフラグを自動リセットする。
        let mut ime_active_since: Option<Instant> = None;
        // IME_ACTIVE 変更検出: 状態が変化した際に ImeState ログを送出
        let mut last_active: Option<bool> = None;
        loop {
            let active = monitor.is_candidate_window_open();

            // Safety valve: EVENT_OBJECT_IME_HIDE はフォーカス変更やクラッシュ時に
            // 取りこぼすことがある。IME_ACTIVE が 8 秒以上 true のままなら stale と
            // みなしてリセット。実際の IME 変換は数秒以内に確定/キャンセルされる。
            if active {
                let since = ime_active_since.get_or_insert_with(Instant::now);
                if since.elapsed() > Duration::from_secs(8) {
                    tracing::warn!("IME_ACTIVE stale for >8s — auto-resetting");
                    input::hook::IME_ACTIVE.store(false, Ordering::Relaxed);
                    ime_active_since = None;
                    engine_for_monitor.set_paused(false);
                    last_active = Some(false);
                    let ts = std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_millis() as u64;
                    let ime_on = input::hook::IME_OPEN.load(Ordering::Relaxed);
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
            if last_active.map_or(true, |prev| prev != active) {
                let was_active = last_active.unwrap_or(false);
                last_active = Some(active);
                let ts = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis() as u64;
                let ime_on = input::hook::IME_OPEN.load(Ordering::Relaxed);
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
            #[cfg(target_os = "windows")]
            if !active && input::hook::IME_SHADOW_READY.load(Ordering::Acquire) {
                let ts = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis() as u64;
                emit_ime_shadow(&log_tx_for_monitor, ts);
            }

            // IME候補ウィンドウ表示中はHMM推論を一時停止する。
            // 確率はリセットせず直前の状態を維持する。
            // 候補選択中の認知状態（Incubation等）を破壊しない。
            engine_for_monitor.set_paused(active);
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

            // --- キーボードフック・IME ポーリングの初期化 ---
            // Tauri の setup() はメインスレッドで、Tauri ランタイム初期化完了後に実行される。
            // ウィンドウシステムが完全に初期化された後にフックをインストールすることで、
            // Tauri 初期化がフックを無効化する問題を回避する。

            // IME open ポーリングスレッド (wake-on-keystroke + VK_DBE_* fallback)
            let (poll_wake_tx, poll_wake_rx) = crossbeam_channel::bounded::<()>(1);
            input::hook::set_poll_wake_sender(poll_wake_tx);
            input::ime::spawn_ime_open_polling_thread(ime_poll_log_tx, poll_wake_rx);

            // キーボードフック開始 (set_poll_wake_sender の後に呼ぶこと)
            input::hook::init_hook(hook_tx);

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
                spawn_reconcile(app.handle().clone(), "at startup");
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
                        let start = SESSION_START_MS.load(Ordering::Acquire);
                        if start == 0 {
                            continue; // ブロック未開始
                        }
                        let now = SystemTime::now()
                            .duration_since(UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_millis() as u64;
                        if now.saturating_sub(start) < crate::g1::BLOCK_DURATION_MS {
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
                        spawn_reconcile(app_handle.clone(), "after block");
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
            {
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
        .manage(WallServerState::new())
        .manage(ResetSignal(should_reset))
        .manage(SessionActive(session_active))
        .manage(LatestFeatState(latest_feat))
        .manage(InterventionState(intervention_state))
        .manage(LogStatusState(log_target))
        .invoke_handler(tauri::generate_handler![
            greet,
            get_cognitive_state,
            get_intervention_decision,
            force_wall,
            force_nudge,
            debug_force_probe,
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
            submit_latest_session,
            record_user_label,
            record_session_meta,
            record_realtime_answer,
            record_realtime_skip,
            record_self_marker,
            record_vignette_response,
            wall_server::start_wall_server,
            wall_server::stop_wall_server,
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
    use super::{extract_age_path, redact_prefixes};
    // participant_id 検証の規則テストは crate::participant_id (単一情報源) 側に置く。

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
