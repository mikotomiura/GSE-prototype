pub mod analysis;
pub mod input;
pub mod logger;
#[cfg(target_os = "macos")]
pub mod sensors;
pub mod wall_server;

use crate::analysis::engine::{CognitiveState, CognitiveStateEngine};
use crate::logger::{LogEntry, SessionLogger};
use crate::wall_server::WallServerState;
use crossbeam_channel::{self, Receiver, RecvTimeoutError, Sender};
#[allow(unused_imports)]
use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};
use tauri::{Manager, State};

// ---------------------------------------------------------------------------
// ログ状態 (quit_app からも参照できるよう Tauri state で管理)
// ---------------------------------------------------------------------------

struct LogState {
    tx: Sender<LogEntry>,
    path: String,
    /// ロガースレッドが End を処理し終えたときに通知される受信端
    shutdown_rx: Receiver<()>,
}

/// 分析スレッドへのリセットシグナル。
/// start_session コマンドが `true` にセットすると、分析スレッドが
/// FeatureExtractor をクリアして `false` に戻す。
struct ResetSignal(Arc<AtomicBool>);

/// セッションアクティブフラグ。
/// start_session が呼ばれるまで分析スレッドは打鍵イベントをドレインする。
struct SessionActive(Arc<AtomicBool>);

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
    log.lock().unwrap_or_else(|p| p.into_inner()).path.clone()
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
    log: State<Arc<Mutex<LogState>>>,
) {
    // リセットシグナルを先にセットしてからセッションを有効化する。
    // 分析スレッドが active=true を Acquire で読んだ時点で、
    // それより前に Release された reset=true も可視であることが保証される。
    // 逆順だと、分析スレッドが active=true を見た瞬間に reset がまだ false で、
    // 前セッションの沈黙時間が初回更新に混入するレースコンディションが発生する。
    engine.reset();
    reset_signal.0.store(true, Ordering::Release);
    session_active.0.store(true, Ordering::Release);
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    let guard = log.lock().unwrap_or_else(|p| p.into_inner());
    let _ = guard.tx.try_send(LogEntry::SessionStart { timestamp: now });

    // setup() で事前生成されたオーバーレイウィンドウを maximize → show する。
    // ウィンドウ生成自体は setup() (メインスレッド) で行うことで、
    // Windows での tokio ワーカースレッドからの WebviewWindowBuilder::build()
    // デッドロックを回避する。
    if let Some(win) = app.get_webview_window("overlay") {
        let _ = win.maximize();
        let _ = win.show();
        tracing::info!("Overlay window shown");
    } else {
        tracing::error!("Overlay window not found — setup() may have failed");
    }
}

/// アプリ終了。終了前に以下を順に実行する:
///   1. WallServer を停止 (ファイアウォールルール削除)
///   2. セッションログを閉じる (LogEntry::End を送信)
///   3. shutdown_rx でロガー完了を待機 (固定 sleep の代わり)
///   4. behavioral_gt.py でラベリング分析を実行 (Python が PATH にある場合)
///   5. セッションフォルダを Explorer で開く
#[tauri::command]
fn quit_app(app: tauri::AppHandle, log: State<Arc<Mutex<LogState>>>, wall: State<WallServerState>) {
    // WallServer を先に停止してファイアウォールルールを削除
    wall.stop();

    // ログ終了マーカーを送信し、shutdown_rx を取得
    let (session_path, shutdown_rx) = {
        let guard = log.lock().unwrap_or_else(|p| p.into_inner());
        let _ = guard.tx.try_send(LogEntry::End);
        (guard.path.clone(), guard.shutdown_rx.clone())
    };

    let app_handle = app.clone();

    // バックグラウンドスレッドで分析→フォルダ表示→アプリ終了
    thread::spawn(move || {
        // ロガースレッドのファイルクローズを channel で安全に待機 (最大2秒)
        let _ = shutdown_rx.recv_timeout(Duration::from_millis(2000));

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
// アプリ起動
// ---------------------------------------------------------------------------

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tracing_subscriber::fmt::init();

    // セッションロガー起動
    let log_path = logger::default_log_path();
    let log_path_str = log_path.to_string_lossy().to_string();
    tracing::info!("Session log: {}", log_path_str);

    let (_session_logger, log_tx, log_shutdown_rx) = SessionLogger::start(log_path);

    // LogState を Arc<Mutex> でラップして Tauri state に渡す
    let log_state = Arc::new(Mutex::new(LogState {
        tx: log_tx.clone(),
        path: log_path_str,
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

    // エンジン初期化
    let engine = CognitiveStateEngine::new();
    let engine_for_thread = engine.clone();
    let engine_for_monitor = engine.clone();
    let log_tx_ime_poll = log_tx.clone();
    let log_tx_for_monitor = log_tx.clone();
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
                thread::sleep(Duration::from_millis(50));
                continue;
            }

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
                Ok(event) => Some(LoopInput::Key(event)),
                Err(RecvTimeoutError::Timeout) => None,
                Err(RecvTimeoutError::Disconnected) => break,
            };

            // step() 本体は analysis/loop_step.rs に抽出済み。
            // リピート検出・IME ポーズ分岐・silence-break protection・
            // 1Hz ゲート・沈黙 3 状態機構・Feat 生成をすべて担う。
            let ime_open = input::hook::IME_OPEN.load(Ordering::Relaxed);
            let out = step(&mut state, &engine_for_thread, input, now_ms(), ime_open);

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
                    thread::sleep(std::time::Duration::from_millis(100));
                    continue;
                }
            } else {
                ime_active_since = None;
            }

            // IME_ACTIVE 状態変化時にログを送出（初回は必ず emit）
            if last_active.map_or(true, |prev| prev != active) {
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

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(move |app| {
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

            // Overlay ウィンドウを setup() で事前生成する (hidden, non-maximized)。
            // setup() はメインスレッドで実行されるため、Windows での
            // WebviewWindowBuilder::build() デッドロックを回避できる。
            //
            // macOS では visible(false) + maximized(true) の同時指定で
            // 不透明なオーバーレイが表示される問題があったが、ここでは
            // maximized を指定せず visible(false) のみで生成する。
            // maximize() + show() は start_session で制御された順序で実行される。
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
            .visible(false)
            .build()
            {
                Ok(_) => tracing::info!("Overlay window pre-created (hidden)"),
                Err(e) => tracing::error!("Failed to pre-create overlay window: {}", e),
            }
            Ok(())
        })
        .manage(engine)
        .manage(log_state)
        .manage(WallServerState::new())
        .manage(ResetSignal(should_reset))
        .manage(SessionActive(session_active))
        .invoke_handler(tauri::generate_handler![
            greet,
            get_cognitive_state,
            get_keyboard_idle_ms,
            get_last_keypress_timestamp,
            get_hook_status,
            get_diagnostics,
            reset_input_monitoring,
            reset_accessibility,
            open_accessibility_settings,
            start_session,
            quit_app,
            get_session_file,
            wall_server::start_wall_server,
            wall_server::stop_wall_server,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
