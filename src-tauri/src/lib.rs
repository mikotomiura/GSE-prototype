pub mod analysis;
pub mod input;
pub mod logger;
pub mod wall_server;

use crate::analysis::{
    engine::{CognitiveState, CognitiveStateEngine},
    features::FeatureExtractor,
};
use crate::logger::{LogEntry, SessionLogger};
use crate::wall_server::WallServerState;
use crossbeam_channel::{self, Receiver, RecvTimeoutError, Sender};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};
use tauri::State;

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

/// macOS版との互換性維持のため提供。
/// Windows版ではシステム権限プロンプトが不要なため常に `true` を返す。
#[tauri::command]
fn get_hook_status() -> bool {
    true
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

/// 現在のセッションログファイルのパスを返す (UI表示用)
#[tauri::command]
fn get_session_file(log: State<Arc<Mutex<LogState>>>) -> String {
    log.lock()
        .unwrap_or_else(|p| p.into_inner())
        .path
        .clone()
}

/// 「開始する」ボタン押下時に呼ばれる。
/// 1. セッションアクティブフラグをセット (分析スレッドのドレインを終了)
/// 2. CognitiveStateEngine を初期状態にリセット
/// 3. 分析スレッドの FeatureExtractor リセットを要求 (AtomicBool シグナル)
/// 4. LogEntry::SessionStart をログに記録
#[tauri::command]
fn start_session(
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
}

/// アプリ終了。終了前に以下を順に実行する:
///   1. WallServer を停止 (ファイアウォールルール削除)
///   2. セッションログを閉じる (LogEntry::End を送信)
///   3. shutdown_rx でロガー完了を待機 (固定 sleep の代わり)
///   4. behavioral_gt.py でラベリング分析を実行 (Python が PATH にある場合)
///   5. セッションフォルダを Explorer で開く
#[tauri::command]
fn quit_app(
    app: tauri::AppHandle,
    log: State<Arc<Mutex<LogState>>>,
    wall: State<WallServerState>,
) {
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
                tracing::info!(
                    "Auto-analysis: python {:?} {}",
                    script,
                    session_path
                );
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

        // セッションフォルダを Explorer で開く
        if let Some(folder) = Path::new(&session_path).parent() {
            tracing::info!("Opening session folder: {:?}", folder);
            let _ = std::process::Command::new("explorer")
                .arg(folder)
                .spawn();
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
    let (tx, rx) = crossbeam_channel::bounded(64);

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
        tracing::info!("Analysis thread started");
        let mut extractor = FeatureExtractor::new(600);
        let mut last_event_time = Instant::now();
        let mut next_engine_update = Instant::now();
        let mut presses_since_silence: u32 = 0;

        loop {
            // start_session が呼ばれるまでチャネルをドレインして処理をスキップする。
            if !session_active_for_thread.load(Ordering::Acquire) {
                while rx.try_recv().is_ok() {}
                thread::sleep(Duration::from_millis(50));
                continue;
            }

            // start_session コマンドによるリセット要求をチェック
            if should_reset_for_thread.swap(false, Ordering::AcqRel) {
                extractor = FeatureExtractor::new(600);
                last_event_time = Instant::now();
                next_engine_update = Instant::now();
                presses_since_silence = 0;
            }

            // 動的タイムアウト: 次の1Hzマークまでの残り時間
            let now = Instant::now();
            let timeout = if next_engine_update > now {
                next_engine_update - now
            } else {
                Duration::from_millis(0)
            };

            // イベント受信 (タイムアウトは次の1Hzマークまで)
            match rx.recv_timeout(timeout.max(Duration::from_millis(1))) {
                Ok(event) => {
                    // バッファに追加 (IMEポーズ中でも常に)
                    extractor.process_event(event);

                    // キーイベントをログ記録（全打鍵を記録、推論頻度とは独立）
                    let _ = log_tx_analysis.try_send(LogEntry::Key {
                        vk_code: event.vk_code,
                        timestamp: event.timestamp,
                        is_press: event.is_press,
                    });

                    // IMEポーズ中は last_event_time の更新とストリークカウントをスキップ
                    if engine_for_thread.get_paused() {
                        continue;
                    }

                    if event.is_press {
                        // Silence-break protection (non-repeat only):
                        // 自動リピートは意図的な復帰ではないため、沈黙復帰カウントに含めない。
                        // 10秒以上の沈黙後、3打鍵以上の連続入力で初めて
                        // last_event_time をリセットし「タイピング復帰」と判定する。
                        if !event.is_repeat {
                            if last_event_time.elapsed() > Duration::from_secs(10) {
                                presses_since_silence += 1;
                                if presses_since_silence >= 3 {
                                    last_event_time = Instant::now();
                                    presses_since_silence = 0;
                                }
                            } else {
                                last_event_time = Instant::now();
                                presses_since_silence = 0;
                            }
                        }

                        // Backspaceストリークカウント（1Hz gate の外側で全打鍵）
                        // リピートイベントも含める: BS長押しによる一気消しでペナルティを発動させる
                        // is_backspace はフック層で OS 固有キーコードから判定済み
                        engine_for_thread.register_keystroke(event.is_backspace);
                    }
                }
                Err(RecvTimeoutError::Timeout) => {
                    // タイムアウト = 1Hzマーク到達 → フォールスルーして推論へ
                }
                Err(RecvTimeoutError::Disconnected) => break,
            }

            // ── 独立 1Hz ゲート ──────────────────────────────────────
            let now = Instant::now();
            if now < next_engine_update {
                continue;
            }

            // 絶対時刻ベースインクリメント (累積ドリフト防止)
            // スレッドスタール後のキャッチアップ: 大幅に遅れた場合は現在時刻にリセット
            next_engine_update += Duration::from_secs(1);
            if next_engine_update < now {
                next_engine_update = now + Duration::from_secs(1);
            }

            if engine_for_thread.get_paused() {
                continue;
            }

            let ime_open = input::hook::IME_OPEN.load(Ordering::Relaxed);
            let silence_secs = last_event_time.elapsed().as_secs_f64();

            // 特徴量計算: バッファの実データを優先し、空の場合のみ合成サイレンス特徴量を使用
            let mut features = extractor.calculate_features();

            let (log_features, diag_opt) = if features.f1_flight_time_median > 0.0
                && silence_secs < 5.0
            {
                // 通常パス: バッファに実データあり + 直近タイピング中 → α=0.3 で更新
                let d = engine_for_thread.update(&features, ime_open);
                (features, d)
            } else if features.f1_flight_time_median > 0.0 {
                // 沈黙パス (バッファに実データあり): 5秒以上沈黙中
                // 古いウィンドウデータを α=0.3 で連続入力すると Incubation にロックインするため、
                // α=0.15 の update_silence を使用する。
                // F5 に進行中の沈黙を加算し、摩擦フロアを適用する。
                if silence_secs >= 2.0 {
                    features.f5_pause_count += silence_secs / 2.0;
                }
                if silence_secs >= 8.0 {
                    let f6_floor = ((silence_secs - 8.0) / 25.0).clamp(0.0, 0.50);
                    let f3_floor = ((silence_secs - 10.0) / 30.0).clamp(0.0, 0.40);
                    features.f6_pause_after_del_rate = features.f6_pause_after_del_rate.max(f6_floor);
                    features.f3_correction_rate = features.f3_correction_rate.max(f3_floor);
                }
                let d = engine_for_thread.update_silence(&features, ime_open, silence_secs);
                (features, d)
            } else if let Some(sf) = extractor.make_silence_observation(silence_secs) {
                // 合成サイレンスパス: バッファ空 → 合成特徴量で α=0.15 更新
                let d = engine_for_thread.update_silence(&sf, ime_open, silence_secs);
                (sf, d)
            } else {
                // silence < 2s かつ f1=0 (データ不足) → スキップ
                continue;
            };

            // 特徴量 + 状態確率をログ記録
            let state_probs = engine_for_thread.get_current_state();
            let p_flow = state_probs
                .get(&CognitiveState::Flow)
                .copied()
                .unwrap_or(0.0);
            let p_inc = state_probs
                .get(&CognitiveState::Incubation)
                .copied()
                .unwrap_or(0.0);
            let p_stuck = state_probs
                .get(&CognitiveState::Stuck)
                .copied()
                .unwrap_or(0.0);

            let now_ts = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_millis() as u64;

            let (raw_x, raw_y, ewma_x, ewma_y, obs, alpha) = match &diag_opt {
                Some(d) => (d.raw_x, d.raw_y, d.ewma_x, d.ewma_y, d.obs, d.alpha),
                None => (0.0, 0.0, 0.0, 0.0, 0, 0.0),
            };

            let _ = log_tx_analysis.try_send(LogEntry::Feat {
                timestamp: now_ts,
                f1: log_features.f1_flight_time_median,
                f3: log_features.f3_correction_rate,
                f4: log_features.f4_burst_length,
                f5: log_features.f5_pause_count,
                f6: log_features.f6_pause_after_del_rate,
                p_flow,
                p_inc,
                p_stuck,
                raw_x,
                raw_y,
                ewma_x,
                ewma_y,
                obs,
                alpha,
            });
        }
    });

    // IME モニタースレッド
    thread::spawn(move || {
        tracing::info!("IME Monitor thread started");
        let monitor = input::ime::ImeMonitor::new();
        // IME_ACTIVE が true になった時刻。8 秒以上続いたら EVENT_OBJECT_IME_HIDE
        // 取りこぼしと判断してフラグを自動リセットする。
        let mut ime_active_since: Option<Instant> = None;
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
                    thread::sleep(std::time::Duration::from_millis(100));
                    continue;
                }
            } else {
                ime_active_since = None;
            }

            // IME候補ウィンドウ表示中はHMM推論を一時停止する。
            // 確率はリセットせず直前の状態を維持する。
            // 候補選択中の認知状態（Incubation等）を破壊しない。
            engine_for_monitor.set_paused(active);
            thread::sleep(std::time::Duration::from_millis(100));
        }
    });

    // IME open ポーリングスレッド (wake-on-keystroke + VK_DBE_* fallback)
    //
    // wake チャネル (bounded 1):
    //   フックコールバックがキー押下ごとに非ブロッキング try_send → ポーリングスレッドが
    //   recv_timeout(100ms) で即起床 → 5ms 待機後に ImmGetOpenStatus または
    //   IME_STATE_DIRTY フラグで状態を確認。
    //   同一ミリ秒 flapping 不可能（LogEntry::ImeState はポーリングスレッドのタイムスタンプ）。
    //   アイドル時最大ラグ 100ms → アクティブ打鍵時最大ラグ ~5ms。
    let (poll_wake_tx, poll_wake_rx) = crossbeam_channel::bounded::<()>(1);
    input::hook::set_poll_wake_sender(poll_wake_tx);
    input::ime::spawn_ime_open_polling_thread(log_tx_ime_poll, poll_wake_rx);

    // キーボードフック開始 (set_poll_wake_sender の後に呼ぶこと)
    input::hook::init_hook(tx);

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
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
            start_session,
            quit_app,
            get_session_file,
            wall_server::start_wall_server,
            wall_server::stop_wall_server,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
