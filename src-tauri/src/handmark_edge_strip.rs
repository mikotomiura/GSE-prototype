//! 手跡の下の縁の帯の試作（spike・本線に入れない・macOS だけ）。
//!
//! `.steering/20261030-handmark-edge-strip-impl/` の design.md を参照。背景の層（`handmark_stage_spike`）が
//! 出ているときだけ、主画面の下の縁に高さ 14 点の帯を出す。帯は本体の窓 1 枚で、非アクティブの NSPanel・
//! 浮く層・全 Space・全画面の上・クリック透過にする（設計のタスクの判断 4）。
//!
//! 段 1 では、帯の中身は揺れる線 1 本だけで、確かめ用に窓の状態を 1 秒ごとに `tracing` へ出す。
//! トレイの「背景を見る」は、自分が前面に出られるかを読むだけで、何も隠さない（判断 7 の確かめ）。
//!
//! 守ること（背景の層と同じ）:
//! - 推定を use しない。アプリの名前を読まない・書かない。本人の操作を記録しない（ログに出すのは窓の状態と、
//!   前面に出られたかと待った時間だけ）。
//! - NSPanel にした窓を壊さない（壊すとプロセスごと落ちる・`handmark_spike.rs`）。閉じる要求は隠すだけにする。

/// 帯の窓の label。capabilities/handmark-stage.json と src/main.tsx の分岐と一致させる。
pub const LABEL: &str = "handmark-edge-strip";

#[cfg(target_os = "macos")]
mod imp {
    use super::LABEL;
    use std::sync::atomic::{AtomicBool, Ordering};
    use std::sync::mpsc;
    use std::time::{Duration, Instant};
    use tauri::{AppHandle, Manager, Wry};
    use tauri_nspanel::ManagerExt;

    /// 帯の高さ（論理 px = 点）。仮（設計の論点 5）。
    const HEIGHT: f64 = 14.0;
    /// 前面に出るのを待つ上限と、読む間隔（設計の論点 6）。
    const ACTIVATE_WAIT: Duration = Duration::from_millis(1000);
    const ACTIVATE_POLL: Duration = Duration::from_millis(50);
    /// 確かめ用に窓の状態を読む間隔。
    const PROBE_EVERY: Duration = Duration::from_millis(1000);

    /// 帯が出ている間だけ true。
    static SHOWN: AtomicBool = AtomicBool::new(false);
    /// 前面に出られるかの読みが走っている間だけ true（重ねて走らせない）。
    static ACTIVATING: AtomicBool = AtomicBool::new(false);

    fn ns_window(window: &tauri::WebviewWindow<Wry>) -> Result<&objc2_app_kit::NSWindow, String> {
        let ptr = window
            .ns_window()
            .map_err(|e| format!("ns_window failed: {e}"))?;
        if ptr.is_null() {
            return Err("ns_window is null".to_string());
        }
        // SAFETY: Tauri が返す NSWindow のポインタで、帯の窓は壊さない（隠すだけ）のでアプリの終了まで生きている。
        //   呼び出しはすべてメインスレッド（setup と run_on_main_thread の中）で行う。
        Ok(unsafe { &*(ptr as *const objc2_app_kit::NSWindow) })
    }

    /// 背景の層の `setup()`（メインスレッド）から、背景が出たときだけ呼ぶ。
    pub fn setup(app: &tauri::App<Wry>) {
        let window = match tauri::WebviewWindowBuilder::new(
            app,
            LABEL,
            tauri::WebviewUrl::App("index.html".into()),
        )
        .title("GSE handmark edge strip spike")
        .inner_size(800.0, HEIGHT)
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
                tracing::warn!("handmark edge strip: window could not be built: {}", e);
                return;
            }
        };
        match prepare(app.handle(), &window) {
            Ok(()) => {
                SHOWN.store(true, Ordering::Release);
                start_probe(app.handle().clone());
                tracing::info!("handmark edge strip: strip shown");
            }
            Err(e) => {
                tracing::warn!("handmark edge strip: strip NOT shown: {}", e);
                if let Ok(panel) = app.get_webview_panel(LABEL) {
                    panel.order_out(None);
                } else {
                    let _ = window.hide();
                }
            }
        }
    }

    /// NSPanel 化・層・振る舞い・クリック透過・位置。どれかが失敗したら Err。
    fn prepare(app: &AppHandle<Wry>, window: &tauri::WebviewWindow<Wry>) -> Result<(), String> {
        // 非アクティブの NSPanel・Floating（上げない・tauri-nspanel #104 の IME の件）。
        crate::overlay_panel::convert_overlay_to_panel(window)
            .map_err(|e| format!("NSPanel conversion failed: {e}"))?;
        let panel = app
            .get_webview_panel(LABEL)
            .map_err(|e| format!("get_webview_panel({LABEL}) failed: {e:?}"))?;
        panel.set_ignore_mouse_events(true);

        // 主画面の下の縁（作業領域ではなく画面の全体の下端。Dock とは何もしない・論点 5）。
        let monitor = window
            .primary_monitor()
            .map_err(|e| format!("primary_monitor failed: {e}"))?
            .ok_or_else(|| "no primary monitor".to_string())?;
        let scale = monitor.scale_factor();
        let height = (HEIGHT * scale).round() as u32;
        let size = *monitor.size();
        let pos = *monitor.position();
        window
            .set_size(tauri::PhysicalSize::new(size.width, height))
            .map_err(|e| format!("set_size failed: {e}"))?;
        window
            .set_position(tauri::PhysicalPosition::new(
                pos.x,
                pos.y + size.height as i32 - height as i32,
            ))
            .map_err(|e| format!("set_position failed: {e}"))?;

        // 振る舞いは試し 4（run16）と同じ 4 つ。convert_overlay_to_panel の 2 つを置き換える。
        let ns = ns_window(window)?;
        ns.setCollectionBehavior(
            objc2_app_kit::NSWindowCollectionBehavior::CanJoinAllSpaces
                | objc2_app_kit::NSWindowCollectionBehavior::Stationary
                | objc2_app_kit::NSWindowCollectionBehavior::IgnoresCycle
                | objc2_app_kit::NSWindowCollectionBehavior::FullScreenAuxiliary,
        );
        ns.setIgnoresMouseEvents(true);
        // key にしない（フォーカスを奪わない）。
        ns.orderFrontRegardless();
        panel.resign_key_window();
        tracing::info!(
            level = ns.level(),
            behavior = ns.collectionBehavior().0,
            "handmark edge strip: window prepared"
        );
        Ok(())
    }

    /// 確かめ用（段 1）: 帯の窓の状態を 1 秒ごとに読んで出す。帯が隠れたら抜ける。
    fn start_probe(app: AppHandle<Wry>) {
        let spawned = std::thread::Builder::new()
            .name("gse-handmark-strip-probe".to_string())
            .spawn(move || loop {
                std::thread::sleep(PROBE_EVERY);
                if !SHOWN.load(Ordering::Acquire) || crate::is_shutting_down() {
                    return;
                }
                let handle = app.clone();
                let _ = app.run_on_main_thread(move || {
                    let Some(window) = handle.get_webview_window(LABEL) else {
                        return;
                    };
                    let Ok(ns) = ns_window(&window) else { return };
                    let visible_bit = ns
                        .occlusionState()
                        .contains(objc2_app_kit::NSWindowOcclusionState::Visible);
                    tracing::info!(
                        occlusion_visible = visible_bit,
                        on_active_space = ns.isOnActiveSpace(),
                        is_visible = ns.isVisible(),
                        level = ns.level(),
                        "handmark edge strip: probe"
                    );
                });
            });
        if let Err(e) = spawned {
            tracing::warn!("handmark edge strip: probe thread could not start: {}", e);
        }
    }

    /// トレイの「背景を見る」（段 1）: 自分を前面に出し、最大 1 秒の間に前面になったかを読んで出す。
    /// 何も隠さない。メインスレッドは止めない（待つのは別スレッド）。
    pub fn probe_activate(app: &AppHandle<Wry>) {
        if ACTIVATING.swap(true, Ordering::AcqRel) {
            return;
        }
        let handle = app.clone();
        let spawned = std::thread::Builder::new()
            .name("gse-handmark-activate".to_string())
            .spawn(move || {
                let started = Instant::now();
                let _ = handle.run_on_main_thread(|| {
                    if let Some(mtm) = objc2::MainThreadMarker::new() {
                        objc2_app_kit::NSApplication::sharedApplication(mtm).activate();
                    }
                });
                let mut active = false;
                while started.elapsed() < ACTIVATE_WAIT {
                    std::thread::sleep(ACTIVATE_POLL);
                    let (tx, rx) = mpsc::channel();
                    let _ = handle.run_on_main_thread(move || {
                        let _ = tx.send(
                            objc2_app_kit::NSRunningApplication::currentApplication().isActive(),
                        );
                    });
                    if rx.recv_timeout(ACTIVATE_POLL * 4).unwrap_or(false) {
                        active = true;
                        break;
                    }
                }
                tracing::info!(
                    active,
                    activate_wait_ms = started.elapsed().as_millis() as u64,
                    "handmark edge strip: activate probe"
                );
                ACTIVATING.store(false, Ordering::Release);
            });
        if spawned.is_err() {
            ACTIVATING.store(false, Ordering::Release);
            tracing::warn!("handmark edge strip: activate thread could not start");
        }
    }

    /// 閉じる要求のとき: 隠すだけ（壊さない）。
    pub fn close(app: &AppHandle<Wry>) {
        SHOWN.store(false, Ordering::Release);
        match app.get_webview_panel(LABEL) {
            Ok(panel) => panel.order_out(None),
            Err(_) => {
                if let Some(w) = app.get_webview_window(LABEL) {
                    let _ = w.hide();
                }
            }
        }
    }

    pub fn is_shown() -> bool {
        SHOWN.load(Ordering::Acquire)
    }
}

#[cfg(target_os = "macos")]
pub use imp::{close, is_shown, probe_activate, setup};
