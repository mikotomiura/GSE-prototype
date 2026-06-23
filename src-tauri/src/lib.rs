pub mod analysis;
pub mod input;
pub mod logger;
pub mod schema_dto;
#[cfg(target_os = "macos")]
pub mod sensors;
pub mod wall_server;

use crate::analysis::engine::{CognitiveState, CognitiveStateEngine};
use crate::analysis::intervention::{
    InterventionAction, InterventionDecision, InterventionInput, InterventionPolicyState,
};
use crate::analysis::loop_step::FeatSnapshot;
use crate::logger::{
    Condition, DismissReason, ExpectedQuadrant, LabelPool, LogEntry, ProbeRef, ProbeSource,
    SessionLogger, SkipReason, TaskKind, Track, UserLabelKind,
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

// Task C: セッションが宣言する介入の有効/無効 (session_meta.intervention_enabled)。
// record_session_meta が設定し、get_intervention_decision が抑止判断に使う。
// main/overlay の両ウィンドウが同コマンドを叩くため単一情報源で抑止される (cross-review)。
static INTERVENTION_ENABLED: AtomicBool = AtomicBool::new(true);

// デバッグ用: 次回の get_intervention_decision (main) で Wall を一度だけ強制発動するフラグ。
// `force_wall` コマンドが true にし、main ウィンドウの判定が swap で消費する (ワンショット)。
// 通常は false のまま = 既存挙動と完全同一 (pilot 非汚染)。
static FORCE_WALL: AtomicBool = AtomicBool::new(false);

// ---------------------------------------------------------------------------
// ログ状態 (quit_app からも参照できるよう Tauri state で管理)
// ---------------------------------------------------------------------------

pub(crate) struct LogState {
    tx: Sender<LogEntry>,
    path: String,
    /// ロガースレッドが End を処理し終えたときに通知される受信端
    shutdown_rx: Receiver<()>,
}

impl LogState {
    /// サーバスレッド (wall_server) に渡すためロガー Sender を clone して返す。
    /// 生の `tx` を公開せず「スレッドへ move する用途の clone」だけを意図として露出する。
    pub(crate) fn clone_log_tx(&self) -> Sender<LogEntry> {
        self.tx.clone()
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
#[tauri::command]
fn force_wall() {
    FORCE_WALL.store(true, Ordering::Release);
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
            guard.force_wall_decision(idle_ms)
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
        .map_err(|e| format!("log channel full: {}", e))?;
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
    log.lock().unwrap_or_else(|p| p.into_inner()).path.clone()
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
        .map_err(|e| format!("log channel full: {}", e))?;
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
        .map_err(|e| format!("log channel full: {}", e))?;
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
        .map_err(|e| format!("log channel full: {}", e))?;
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
        .map_err(|e| format!("log channel full: {}", e))?;
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
        .map_err(|e| format!("log channel full: {}", e))?;
    Ok(())
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
    *latest_feat.0.lock().unwrap_or_else(|p| p.into_inner()) = None;
    *intervention.0.lock().unwrap_or_else(|p| p.into_inner()) = InterventionPolicyState::new(now);
    let guard = log.lock().unwrap_or_else(|p| p.into_inner());
    let _ = guard.tx.try_send(LogEntry::SessionStart { timestamp: now });

    // Task B: プローブスケジューラへセッション開始時刻を共有する。
    // 専用スレッドが値の変化を検出してスケジューラを再初期化する。
    SESSION_START_MS.store(now, Ordering::Release);

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

    tauri::Builder::default()
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

            // Task B: ランダム時点プローブの専用スケジューラスレッド (DB-2)。
            // 1Hz Analysis Thread はレイテンシ要件があり AppHandle も持たないため、
            // emit と logger 送信の両方が要るプローブ駆動は専用スレッドに分離する。
            // IME Monitor 風の sleep ポーリングで 1Hz 駆動 (wake 信号は不要)。
            // scheduler 純ロジックは analysis/probe_scheduler.rs (OS API 非依存)。
            {
                use crate::analysis::probe_scheduler::{ProbeConfig, ProbeScheduler};
                let app_handle = app.handle().clone();
                let probe_log_tx = log_tx_probe;
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
                            // 新セッション検出 (DB-6)。entropy から u64 seed を引いて
                            // seed_from_u64 で初期化し、seed を tracing に記録する。本番は
                            // 非決定論的でありつつ「この seed でこの scheduled_ts 系列が出た」
                            // ことを後から再現でき、一様性監査 (D-14) が成立する。NDJSON schema は
                            // Task A で凍結のため seed は trace ログにのみ残す (schema 不変)。
                            active_session_start = session_start;
                            let seed: u64 = rand::random();
                            tracing::info!(
                                "probe scheduler seed={} for session_start={}",
                                seed,
                                session_start
                            );
                            scheduler = Some(ProbeScheduler::from_seed(
                                seed,
                                ProbeConfig::default(),
                                session_start,
                            ));
                        }
                        let now = now_ms();
                        // idle は get_keyboard_idle_ms と同じ計算 (last_key==0 は 0)。
                        let last_key = crate::input::hook::last_key_ms();
                        let idle = if last_key == 0 {
                            0
                        } else {
                            now.saturating_sub(last_key)
                        };
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
        .manage(LatestFeatState(latest_feat))
        .manage(InterventionState(intervention_state))
        .invoke_handler(tauri::generate_handler![
            greet,
            get_cognitive_state,
            get_intervention_decision,
            force_wall,
            record_intervention_dismiss,
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
mod task_c_command_tests {
    use super::*;

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
