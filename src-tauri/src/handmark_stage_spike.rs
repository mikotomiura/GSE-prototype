//! 手跡の背景の層の試作（spike・本線に入れない）。
//!
//! `.steering/20261016-handmark-stage-spike/` の design.md を参照。
//! 環境変数 `GSE_HANDMARK_STAGE_SPIKE=1` で起動したときだけ、macOS の主画面の全体に透明な窓を
//! デスクトップの高さ（壁紙の上・アイコンと他の窓の下）で出し、自然世界（霧・草・粒・波紋）を描く。
//! 材料は打鍵の時刻と、カーソルの位置・左のクリック・ホイール（`crate::handmark_stage_pointer`・ADR-040）。
//! `.steering/20261021-handmark-stage-pointer/` で等高線の波から見本 Version 5 の自然世界に替え、計測の CSV を外した。
//!
//! 守ること（親タスク `.steering/20261015-tangibility-design/decisions.md` 判断 16・表現の議論の判断 2）:
//! - 推定（`engine`・`invitation`・`p_stuck`・`level`）を use しない。受け取るのは打鍵の時刻とポインタだけ。
//! - 壁紙の画像を読まない・書かない（EH3 の壁紙の経路に触れない）。
//! - 本人の操作を記録しない。窓はマウスを受けない（ポインタは Rust が読んで送る）。窓は何も返さない
//!   （計測の CSV と `invoke` の口は外した・判断 4）。このファイルはポインタの値の型を知らない。
//! - `GSE_HANDMARK_STAGE_SPIKE_SYNTH_POINTER=1` のときは OS を読まず合成のポインタを使う（負荷の計測用）。
//!   `GSE_HANDMARK_STAGE_SPIKE_POINTER_OFF=1` のときはカーソル・クリック・ホイールを切った状態で始める（同じく計測用・トレイで入れ直せる）。
//! - 共有の種別は既定のまま出す（写るかを測る）。`GSE_HANDMARK_STAGE_SPIKE_PROTECT=1` のときだけ「なし」にし、
//!   読み返せなければ出さない（小面と同じ fail-closed）。

#[cfg(target_os = "macos")]
use std::sync::atomic::{AtomicBool, Ordering};

/// 背景の窓の label。capabilities/handmark-stage.json と src/main.tsx の分岐と一致させる。
pub const LABEL: &str = "handmark-stage";
/// 打鍵を窓へ知らせるイベント名。
#[cfg(target_os = "macos")]
const KEY_EVENT: &str = "handmark-stage-key";
/// 風の目標を窓へ配るイベント名（背景と下の縁の帯の 2 つの窓だけへ `emit_to`）。
#[cfg(target_os = "macos")]
const WIND_EVENT: &str = "handmark-wind";

#[cfg(target_os = "macos")]
const ENV_ENABLE: &str = "GSE_HANDMARK_STAGE_SPIKE";
#[cfg(target_os = "macos")]
const ENV_PROTECT: &str = "GSE_HANDMARK_STAGE_SPIKE_PROTECT";
#[cfg(target_os = "macos")]
const ENV_SYNTH_POINTER: &str = "GSE_HANDMARK_STAGE_SPIKE_SYNTH_POINTER";
#[cfg(target_os = "macos")]
const ENV_POINTER_OFF: &str = "GSE_HANDMARK_STAGE_SPIKE_POINTER_OFF";

/// 窓が出ていて打鍵を送ってよいときだけ true。閉じたら false に戻す。
#[cfg(target_os = "macos")]
static ACTIVE: AtomicBool = AtomicBool::new(false);

#[cfg(target_os = "macos")]
mod imp {
    use super::*;
    use crate::handmark_wind::{Wind, TICK_MS};
    use std::sync::{Mutex, OnceLock};
    use std::time::{Duration, Instant};
    use tauri::{AppHandle, Emitter, Manager, Wry};

    // CGWindowLevelKey（CGWindowLevel.h）のデスクトップの層（アイコンの層 kCGDesktopIconWindowLevelKey より下）。
    const K_CG_DESKTOP_WINDOW_LEVEL_KEY: i32 = 2;

    #[link(name = "CoreGraphics", kind = "framework")]
    extern "C" {
        fn CGWindowLevelForKey(key: i32) -> i32;
    }

    static APP: OnceLock<AppHandle<Wry>> = OnceLock::new();
    /// 風（打鍵の時刻だけを持つ）。分析スレッドが `press` し、風のスレッドが `tick` する。
    static WIND: Mutex<Wind> = Mutex::new(Wind::new());
    /// 風の時計の起点。
    static T0: OnceLock<Instant> = OnceLock::new();

    fn now_ms() -> u64 {
        T0.get_or_init(Instant::now).elapsed().as_millis() as u64
    }

    /// 背景が出ている間、250ms ごとに風の目標を計算して 2 つの窓へ配る（判断 1）。
    fn start_wind(app: AppHandle<Wry>) {
        let spawned = std::thread::Builder::new()
            .name("gse-handmark-wind".to_string())
            .spawn(move || {
                while ACTIVE.load(Ordering::Acquire) && !crate::is_shutting_down() {
                    std::thread::sleep(Duration::from_millis(TICK_MS));
                    let target = match WIND.lock() {
                        Ok(mut w) => w.tick(now_ms()),
                        Err(_) => return,
                    };
                    let _ = app.emit_to(LABEL, WIND_EVENT, target);
                    let _ = app.emit_to(crate::handmark_edge_strip::LABEL, WIND_EVENT, target);
                }
            });
        if let Err(e) = spawned {
            tracing::warn!("handmark stage spike: wind thread could not start: {}", e);
        }
    }

    fn ns_window(window: &tauri::WebviewWindow<Wry>) -> Result<&objc2_app_kit::NSWindow, String> {
        let ptr = window
            .ns_window()
            .map_err(|e| format!("ns_window failed: {e}"))?;
        if ptr.is_null() {
            return Err("ns_window is null".to_string());
        }
        // SAFETY: Tauri が返す NSWindow のポインタで、窓は壊さない（hide だけ）のでアプリの終了まで生きている。
        //   呼び出しはすべてメインスレッド（setup と run_on_main_thread の中）で行う。
        Ok(unsafe { &*(ptr as *const objc2_app_kit::NSWindow) })
    }

    /// `setup()`（メインスレッド）から呼ぶ。開発用のビルドで環境変数があるときだけ動く
    /// （配布物のビルドでは環境変数があっても何もしない）。
    pub fn setup(app: &tauri::App<Wry>) {
        if !cfg!(debug_assertions) || !crate::handmark_spike::env_flag(ENV_ENABLE) {
            return;
        }
        let window = match tauri::WebviewWindowBuilder::new(
            app,
            LABEL,
            tauri::WebviewUrl::App("index.html".into()),
        )
        .title("GSE handmark stage spike")
        .inner_size(800.0, 600.0)
        .resizable(false)
        .decorations(false)
        .transparent(true)
        .shadow(false)
        .skip_taskbar(true)
        .focused(false)
        .visible(false)
        .build()
        {
            Ok(w) => w,
            Err(e) => {
                tracing::warn!("handmark stage spike: window could not be built: {}", e);
                return;
            }
        };

        match prepare(&window) {
            Ok(()) => {
                let _ = APP.set(app.handle().clone());
                ACTIVE.store(true, Ordering::Release);
                let synthetic = crate::handmark_spike::env_flag(ENV_SYNTH_POINTER);
                if crate::handmark_spike::env_flag(ENV_POINTER_OFF) {
                    crate::handmark_stage_pointer::set_cursor_on(false);
                    crate::handmark_stage_pointer::set_click_on(false);
                    crate::handmark_stage_pointer::set_wheel_on(false);
                }
                // ポインタを読むスレッドは窓が出ている間だけ回る（閉じると ACTIVE が false になり抜ける）。
                let pointer = crate::handmark_stage_pointer::start(
                    app.handle().clone(),
                    LABEL,
                    &ACTIVE,
                    synthetic,
                );
                // 下の縁の帯は、背景が出たときだけ作る（.steering/20261030-handmark-edge-strip-impl/）。
                crate::handmark_edge_strip::setup(app);
                start_wind(app.handle().clone());
                tracing::info!(
                    protect = crate::handmark_spike::env_flag(ENV_PROTECT),
                    synthetic_pointer = synthetic,
                    pointer_off = crate::handmark_spike::env_flag(ENV_POINTER_OFF),
                    pointer_started = pointer.is_ok(),
                    "handmark stage spike: stage shown at desktop level"
                );
            }
            Err(e) => {
                tracing::warn!("handmark stage spike: stage NOT shown: {}", e);
                let _ = window.hide();
            }
        }
    }

    /// 大きさ・層・Spaces・クリックの透過・共有の種別を設定して前に出す。どれかが失敗したら Err。
    fn prepare(window: &tauri::WebviewWindow<Wry>) -> Result<(), String> {
        let monitor = window
            .primary_monitor()
            .map_err(|e| format!("primary_monitor failed: {e}"))?
            .ok_or_else(|| "no primary monitor".to_string())?;
        // 作業領域ではなく画面の全体（メニューバーと Dock の下も壁紙がある）。
        window
            .set_size(*monitor.size())
            .map_err(|e| format!("set_size failed: {e}"))?;
        window
            .set_position(*monitor.position())
            .map_err(|e| format!("set_position failed: {e}"))?;

        if crate::handmark_spike::env_flag(ENV_PROTECT) {
            window
                .set_content_protected(true)
                .map_err(|e| format!("set_content_protected failed: {e}"))?;
        }

        let ns = ns_window(window)?;
        // SAFETY: CoreGraphics の純粋な問い合わせで、引数は CGWindowLevelKey の定数。
        let level = unsafe { CGWindowLevelForKey(K_CG_DESKTOP_WINDOW_LEVEL_KEY) };
        ns.setLevel(level as objc2_app_kit::NSWindowLevel);
        ns.setCollectionBehavior(
            objc2_app_kit::NSWindowCollectionBehavior::CanJoinAllSpaces
                | objc2_app_kit::NSWindowCollectionBehavior::Stationary
                | objc2_app_kit::NSWindowCollectionBehavior::IgnoresCycle,
        );
        ns.setIgnoresMouseEvents(true);

        if crate::handmark_spike::env_flag(ENV_PROTECT)
            && ns.sharingType() != objc2_app_kit::NSWindowSharingType::None
        {
            return Err("sharingType read back is not None (fail-closed)".to_string());
        }
        // key にしない（フォーカスを奪わない）。
        ns.orderFrontRegardless();
        tracing::info!(level, "handmark stage spike: window level set");
        Ok(())
    }

    /// 分析スレッドから呼ぶ。窓が出ているときだけ、打鍵があったことを送る。
    pub fn notify_key() {
        if !ACTIVE.load(Ordering::Acquire) {
            return;
        }
        if let Ok(mut w) = WIND.lock() {
            w.press(now_ms());
        }
        let Some(app) = APP.get() else { return };
        // 打鍵の合図は描画を起こすのに使う（風そのものは WIND_EVENT で配る）。
        let _ = app.emit_to(LABEL, KEY_EVENT, ());
        let _ = app.emit_to(crate::handmark_edge_strip::LABEL, KEY_EVENT, ());
    }

    /// トレイの「背景を閉じる」。隠すだけ（記録しない）。
    pub fn close(app: &AppHandle<Wry>) {
        ACTIVE.store(false, Ordering::Release);
        if let Some(w) = app.get_webview_window(LABEL) {
            let _ = w.hide();
        }
    }

    pub fn is_shown(_app: &AppHandle<Wry>) -> bool {
        ACTIVE.load(Ordering::Acquire)
    }
}

#[cfg(target_os = "macos")]
pub use imp::{close, is_shown, notify_key, setup};

#[cfg(not(target_os = "macos"))]
pub fn notify_key() {}
