//! 手跡の下の縁の帯の試作（spike・本線に入れない・macOS だけ）。
//!
//! `.steering/20261030-handmark-edge-strip-impl/` の design.md を参照。背景の層（`handmark_stage_spike`）が
//! 出ているときだけ、主画面の下の縁に高さ 14 点の帯を出す。帯は本体の窓 1 枚で、非アクティブの NSPanel・
//! 浮く層・全 Space・全画面の上・クリック透過にする（設計のタスクの判断 4）。
//!
//! 帯の中身は `src/components/HandmarkEdgeStrip.tsx`（風で揺れる線・霧・粒）。帯が全部覆われたかを 250ms ごとに
//! `occlusionState` で読み、変わったときだけ窓へ知らせる（窓は覆われている間は描かない・設計の論点 3）。
//! 変わったときは `tracing` にも 1 行出す（確かめ用）。
//! 帯の位置は、主画面の今の Space で使える領域（Dock を除く）の下端に合わせて動かす（判断 5）。
//! トレイの「背景を見る」（他の窓をどける操作）は `handmark_reveal.rs`。
//!
//! 守ること（背景の層と同じ）:
//! - 推定を use しない。アプリの名前を読まない・書かない。本人の操作を記録しない（ログに出すのは窓の状態と、
//!   前面に出られたかと待った時間だけ）。
//! - NSPanel にした窓を壊さない（壊すとプロセスごと落ちる・`handmark_spike.rs`）。閉じる要求は隠すだけにする。

/// 帯の窓の label。capabilities/handmark-stage.json と src/main.tsx の分岐と一致させる。
pub const LABEL: &str = "handmark-edge-strip";

/// 窓（CG の座標・左上が原点・点）が主画面の幅いっぱいで、画面の下端まで届いているか。
/// 全画面のアプリの窓とみなす（判断 6）。切り欠きのある画面では全画面の窓の上端が下がるので、上端は見ない。
#[cfg_attr(not(target_os = "macos"), allow(dead_code))]
fn reaches_screen_bottom(x: f64, y: f64, w: f64, h: f64, screen_w: f64, screen_h: f64) -> bool {
    x.abs() < 1.0 && (w - screen_w).abs() < 1.0 && (y + h - screen_h).abs() < 1.0
}

#[cfg(target_os = "macos")]
mod imp {
    use super::LABEL;
    use std::sync::atomic::{AtomicBool, Ordering};
    use std::sync::mpsc;
    use std::time::Duration;
    use tauri::Emitter;
    use tauri::{AppHandle, Manager, Wry};
    use tauri_nspanel::ManagerExt;

    /// 帯の高さ（論理 px = 点）。仮（設計の論点 5）。
    const HEIGHT: f64 = 14.0;
    /// 帯が覆われたかを読む間隔。
    const PROBE_EVERY: Duration = Duration::from_millis(250);
    /// 帯が見えているかを窓へ知らせるイベント名（帯の窓だけへ `emit_to`）。
    const VISIBLE_EVENT: &str = "handmark-strip-visible";

    /// 帯を出さない起動（負荷を帯の有無で比べる計測用・判断 4）。
    const ENV_OFF: &str = "GSE_HANDMARK_EDGE_STRIP_OFF";

    /// 帯が出ている間だけ true。
    static SHOWN: AtomicBool = AtomicBool::new(false);

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
        if crate::handmark_spike::env_flag(ENV_OFF) {
            tracing::info!("handmark edge strip: not built ({ENV_OFF}=1)");
            return;
        }
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

    /// 帯の窓が見えているかを 250ms ごとに読み、変わったときだけ窓へ知らせて `tracing` に出す。
    /// 帯が隠れたら抜ける。
    fn start_probe(app: AppHandle<Wry>) {
        let spawned = std::thread::Builder::new()
            .name("gse-handmark-strip-probe".to_string())
            .spawn(move || {
                let mut last: Option<bool> = None;
                loop {
                    std::thread::sleep(PROBE_EVERY);
                    if !SHOWN.load(Ordering::Acquire) || crate::is_shutting_down() {
                        return;
                    }
                    let (tx, rx) = mpsc::channel();
                    let handle = app.clone();
                    let _ = app.run_on_main_thread(move || {
                        let Some(window) = handle.get_webview_window(LABEL) else {
                            return;
                        };
                        let Ok(ns) = ns_window(&window) else { return };
                        let lift = follow_dock(ns);
                        let _ = tx.send((
                            ns.occlusionState()
                                .contains(objc2_app_kit::NSWindowOcclusionState::Visible),
                            ns.isOnActiveSpace(),
                            lift,
                        ));
                    });
                    let Ok((visible, on_active_space, lift)) = rx.recv_timeout(PROBE_EVERY * 4)
                    else {
                        continue;
                    };
                    if let Some(lift) = lift {
                        tracing::info!(
                            bottom_lift_pt = lift,
                            "handmark edge strip: moved to the bottom of the visible area"
                        );
                    }
                    if last != Some(visible) {
                        last = Some(visible);
                        let _ = app.emit_to(LABEL, VISIBLE_EVENT, visible);
                        tracing::info!(
                            occlusion_visible = visible,
                            on_active_space,
                            "handmark edge strip: visibility changed"
                        );
                    }
                }
            });
        if let Err(e) = spawned {
            tracing::warn!("handmark edge strip: probe thread could not start: {}", e);
        }
    }

    /// 主画面に、他のアプリの全画面の窓（層 0・幅いっぱいで下端まで）が出ているか。
    /// 読むのは窓の層・持ち主の pid・大きさだけで、アプリや窓の名前は読まない（判断 6）。
    fn fullscreen_window_shown(screen_w: f64, screen_h: f64) -> bool {
        use core_foundation::base::{CFType, TCFType};
        use core_foundation::dictionary::{CFDictionary, CFDictionaryRef};
        use core_foundation::number::CFNumber;
        use core_foundation::string::CFString;
        use core_graphics::window::{
            copy_window_info, kCGNullWindowID, kCGWindowBounds, kCGWindowLayer,
            kCGWindowListExcludeDesktopElements, kCGWindowListOptionOnScreenOnly,
            kCGWindowOwnerPID,
        };
        let me = std::process::id() as i32;
        let Some(list) = copy_window_info(
            kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements,
            kCGNullWindowID,
        ) else {
            return false;
        };
        // SAFETY: 3 つとも CoreGraphics の定数の CFString で、プロセスの間ずっと生きている。
        let (layer_key, pid_key, bounds_key) = unsafe {
            (
                CFString::wrap_under_get_rule(kCGWindowLayer),
                CFString::wrap_under_get_rule(kCGWindowOwnerPID),
                CFString::wrap_under_get_rule(kCGWindowBounds),
            )
        };
        let (kx, ky, kw, kh) = (
            CFString::from_static_string("X"),
            CFString::from_static_string("Y"),
            CFString::from_static_string("Width"),
            CFString::from_static_string("Height"),
        );
        list.iter().any(|item| {
            // SAFETY: CGWindowListCopyWindowInfo の要素は CFDictionary（Apple の文書）。get の規則で包み、所有しない。
            let dict: CFDictionary<CFString, CFType> =
                unsafe { CFDictionary::wrap_under_get_rule(*item as CFDictionaryRef) };
            let int = |k: &CFString| {
                dict.find(k)
                    .and_then(|v| v.downcast::<CFNumber>())
                    .and_then(|n| n.to_i32())
            };
            if int(&layer_key) != Some(0) || int(&pid_key) == Some(me) {
                return false;
            }
            let Some(b) = dict
                .find(&bounds_key)
                .and_then(|v| v.downcast::<CFDictionary>())
            else {
                return false;
            };
            // SAFETY: kCGWindowBounds の値は X・Y・Width・Height の CFNumber を持つ CFDictionary（Apple の文書）。
            let b: CFDictionary<CFString, CFType> =
                unsafe { CFDictionary::wrap_under_get_rule(b.as_concrete_TypeRef()) };
            let f = |k: &CFString| {
                b.find(k)
                    .and_then(|v| v.downcast::<CFNumber>())
                    .and_then(|n| n.to_f64())
            };
            match (f(&kx), f(&ky), f(&kw), f(&kh)) {
                (Some(x), Some(y), Some(w), Some(h)) => {
                    super::reaches_screen_bottom(x, y, w, h, screen_w, screen_h)
                }
                _ => false,
            }
        })
    }

    /// 帯を、主画面の今の Space で使える領域（Dock を除く）の下端へ置く（判断 5）。
    /// 全画面の外では Dock のすぐ上、Dock が引っ込んでいれば画面の下端になる見込み。
    /// 全画面の Space でも visibleFrame は Dock を除いたままなので（run8 の (4)）、他のアプリの全画面の窓が
    /// 出ているときは画面の下端へ置く（判断 6）。
    /// 動かしたときだけ、画面の下端からの高さ（点）を返す。メインスレッドから呼ぶ。
    fn follow_dock(ns: &objc2_app_kit::NSWindow) -> Option<f64> {
        let mtm = objc2::MainThreadMarker::new()?;
        // 主画面（メニューバーのある画面・原点 0,0）。
        let screen = objc2_app_kit::NSScreen::screens(mtm).firstObject()?;
        let sf = screen.frame();
        let vf = screen.visibleFrame();
        let bottom = if fullscreen_window_shown(sf.size.width, sf.size.height) {
            sf.origin.y
        } else {
            vf.origin.y
        };
        let target = objc2_foundation::NSRect::new(
            objc2_foundation::NSPoint::new(sf.origin.x, bottom),
            objc2_foundation::NSSize::new(sf.size.width, HEIGHT),
        );
        let now = ns.frame();
        let same = (now.origin.x - target.origin.x).abs() < 0.5
            && (now.origin.y - target.origin.y).abs() < 0.5
            && (now.size.width - target.size.width).abs() < 0.5
            && (now.size.height - target.size.height).abs() < 0.5;
        if same {
            return None;
        }
        ns.setFrame_display(target, true);
        Some(bottom - sf.origin.y)
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
pub use imp::{close, is_shown, setup};

#[cfg(test)]
mod tests {
    use super::reaches_screen_bottom;

    #[test]
    fn a_fullscreen_window_reaches_the_bottom() {
        // 切り欠きのない画面の全画面。
        assert!(reaches_screen_bottom(0.0, 0.0, 1512.0, 982.0, 1512.0, 982.0));
        // 切り欠きのある画面の全画面（上端が下がる）。
        assert!(reaches_screen_bottom(0.0, 38.0, 1512.0, 944.0, 1512.0, 982.0));
    }

    #[test]
    fn a_zoomed_window_above_the_dock_does_not() {
        // メニューバーの下から Dock の上まで（全画面の外で広げた窓）。
        assert!(!reaches_screen_bottom(0.0, 33.0, 1512.0, 901.0, 1512.0, 982.0));
        // 幅が足りない窓。
        assert!(!reaches_screen_bottom(0.0, 0.0, 800.0, 982.0, 1512.0, 982.0));
        // 横にずれた窓。
        assert!(!reaches_screen_bottom(100.0, 0.0, 1512.0, 982.0, 1512.0, 982.0));
    }
}
