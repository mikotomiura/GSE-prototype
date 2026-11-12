//! 手跡の下の縁の帯の窓（macOS だけ・ADR-051）。試作 `handmark_edge_strip.rs` の窓の作りと見張りを写した。
//!
//! 主画面の下の縁に高さ 14 点の透明な窓を 1 枚出す。非アクティブの NSPanel・浮く層・全 Space・全画面の補助・
//! クリック透過・焦点を取らない。背景の窓（`handmark_stage`）と同じく、開け閉めは駆動役の出来事
//! （`handmark_driver::Effect`）だけが決める（環境変数の門は無い）。受け取る状態は背景と同じ `StageState` で、
//! 窓は何も返さない（`invoke` の口も記録も無い）。推定（`engine`・`invitation`・`p_stuck`・`level`）を use しない。
//!
//! 帯は従である: 作れなかった・出せなかったときは理由を 1 行だけ警告に残し、背景は閉じない。
//! 見張りのスレッドは開いている間だけ 250ms ごとに、帯の置き場（Dock の上端、全画面の窓があれば画面の下端）と
//! 帯が見えているか（`occlusionState`）を読む。読むのは他の窓の層・持ち主の pid・大きさだけで、
//! アプリや窓の名前は読まない。見えているかが変わったときだけ、帯の窓へ知らせる。

/// 帯の窓の label。`capabilities/handmark-stage.json` と `src/main.tsx` の分岐と一致させる。
pub const LABEL: &str = "handmark-edge-strip";
/// 帯が見えているか（真偽値）を帯の窓へ配るイベント名。
const VISIBLE_EVENT: &str = "handmark-strip-visible";
/// 帯へのカーソルの近さ 0〜10 を帯の窓へ配るイベント名。
const NEAR_EVENT: &str = "handmark-strip-near";

/// 窓（CG の座標・左上が原点・点）が主画面の幅いっぱいで、画面の下端まで届いているか。
/// 全画面のアプリの窓とみなす。切り欠きのある画面では全画面の窓の上端が下がるので、上端は見ない。
fn reaches_screen_bottom(x: f64, y: f64, w: f64, h: f64, screen_w: f64, screen_h: f64) -> bool {
    x.abs() < 1.0 && (w - screen_w).abs() < 1.0 && (y + h - screen_h).abs() < 1.0
}

/// 帯の下端の高さ（主画面の下端から・点）。全画面の窓があるときは画面の下端（0）、無ければ Dock を除いた
/// 領域の下端。原点はどちらも主画面の枠の原点を基準にする。
fn strip_bottom_pt(frame_origin_y: f64, visible_origin_y: f64, fullscreen: bool) -> f64 {
    let bottom = if fullscreen {
        frame_origin_y
    } else {
        visible_origin_y
    };
    bottom - frame_origin_y
}

/// 見えているかが前回の送りから変わったか（最初の読みは必ず送る）。
fn visibility_changed(last: Option<bool>, now: bool) -> bool {
    last != Some(now)
}

#[cfg(target_os = "macos")]
mod imp {
    use super::*;
    use crate::analysis::handmark::state::StageState;
    use crate::handmark_pointer_thread::StripSpot;
    use std::sync::atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering};
    use std::sync::mpsc;
    use std::time::Duration;
    use tauri::{AppHandle, Emitter, Manager, Wry};
    use tauri_nspanel::ManagerExt;

    /// 帯の高さ（論理 px = 点）。
    const HEIGHT: f64 = 14.0;
    /// 見張りの間隔。
    const PROBE_EVERY: Duration = Duration::from_millis(250);

    /// 帯が出ている間だけ true。
    static SHOWN: AtomicBool = AtomicBool::new(false);
    /// 帯が出ていて、見えている（`occlusionState`）か。閉じたら偽。
    static STRIP_VISIBLE: AtomicBool = AtomicBool::new(false);
    /// `setup()` で窓を作れなかった（以後の `open` はすぐ失敗にする）。
    static BUILD_FAILED: AtomicBool = AtomicBool::new(false);
    /// 「作れなかった・出せなかった」警告を出した（1 走行に 1 回）。
    static WARNED: AtomicBool = AtomicBool::new(false);
    /// 見張りのスレッドが生きている（開け閉めを何度しても 1 本）。
    static PROBE_RUNNING: AtomicBool = AtomicBool::new(false);
    /// 開いた回数（見張りが開き直しに気づいて、最初の読みを必ず送る）。
    static OPEN_GEN: AtomicU32 = AtomicU32::new(0);
    /// 帯の下端の高さ（点・f64 のビット）と主画面の高さ（点・f64 のビット）。近さの計算が読む。記録しない。
    static BOTTOM_BITS: AtomicU64 = AtomicU64::new(0);
    static SCREEN_H_BITS: AtomicU64 = AtomicU64::new(0);

    fn warn_once(reason: &str) {
        if !WARNED.swap(true, Ordering::AcqRel) {
            tracing::warn!("handmark: edge strip unavailable: {}", reason);
        }
    }

    /// 帯が出ていて見えているか（駆動役が刻みごとに読む）。閉じたら偽。
    pub fn visible() -> bool {
        SHOWN.load(Ordering::Acquire) && STRIP_VISIBLE.load(Ordering::Acquire)
    }

    /// 帯の置き場（出ていなければ `None`）。ポインタのスレッドが近さの計算にだけ使う。
    pub fn spot() -> Option<StripSpot> {
        if !SHOWN.load(Ordering::Acquire) {
            return None;
        }
        let screen_h_pt = f64::from_bits(SCREEN_H_BITS.load(Ordering::Acquire));
        if !screen_h_pt.is_finite() || screen_h_pt <= 0.0 {
            return None;
        }
        Some(StripSpot {
            bottom_pt: f64::from_bits(BOTTOM_BITS.load(Ordering::Acquire)),
            screen_h_pt,
        })
    }

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

    /// `setup()`（メインスレッド）から呼ぶ。窓を隠したまま作り、NSPanel にして振る舞いを決める。
    pub fn setup(app: &tauri::App<Wry>) {
        let window = match tauri::WebviewWindowBuilder::new(
            app,
            LABEL,
            tauri::WebviewUrl::App("index.html".into()),
        )
        .title("GSE")
        .inner_size(800.0, HEIGHT)
        .resizable(false)
        .decorations(false)
        .transparent(true)
        .shadow(false)
        .skip_taskbar(true)
        .focused(false)
        .visible(false)
        // この窓は他のアプリの窓に覆われることが多い。WKWebView の既定（inactiveSchedulingPolicy = suspend）では
        // 数分でタイマーと描画が絞られる（背景の窓の 2026-11-09 の画面の確かめと同じ）。この窓も絞りを切る
        // （macOS 14 以降で効く・wry 0.54）。完全に覆われたときに描かないのは窓の側の判断で行う。
        .background_throttling(tauri::utils::config::BackgroundThrottlingPolicy::Disabled)
        .build()
        {
            Ok(w) => w,
            Err(e) => {
                BUILD_FAILED.store(true, Ordering::Release);
                warn_once(&format!("window could not be built: {e}"));
                return;
            }
        };
        // NSPanel にした窓を壊すとプロセスごと落ちる。閉じる要求は隠すだけにする。
        let handle = app.handle().clone();
        window.on_window_event(move |event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                hide_panel(&handle);
            }
        });
        if let Err(e) = make_panel(app.handle(), &window) {
            BUILD_FAILED.store(true, Ordering::Release);
            warn_once(&e);
            hide_panel(app.handle());
        }
    }

    /// NSPanel 化と振る舞い（浮く層・全 Space・全画面の補助・クリック透過）。どれかが失敗したら Err。
    fn make_panel(app: &AppHandle<Wry>, window: &tauri::WebviewWindow<Wry>) -> Result<(), String> {
        // 非アクティブの NSPanel・Floating（上げない・tauri-nspanel #104 の IME の件）。
        crate::overlay_panel::convert_overlay_to_panel(window)
            .map_err(|e| format!("NSPanel conversion failed: {e}"))?;
        let panel = app
            .get_webview_panel(LABEL)
            .map_err(|_| "panel is not available".to_string())?;
        panel.set_ignore_mouse_events(true);
        // 振る舞いは試作の試し 4（run16）と同じ 4 つ。`convert_overlay_to_panel` の 2 つを置き換える。
        let ns = ns_window(window)?;
        ns.setCollectionBehavior(
            objc2_app_kit::NSWindowCollectionBehavior::CanJoinAllSpaces
                | objc2_app_kit::NSWindowCollectionBehavior::Stationary
                | objc2_app_kit::NSWindowCollectionBehavior::IgnoresCycle
                | objc2_app_kit::NSWindowCollectionBehavior::FullScreenAuxiliary,
        );
        ns.setIgnoresMouseEvents(true);
        Ok(())
    }

    /// 帯を隠す（壊さない）。メインスレッドから呼ぶ。
    fn hide_panel(app: &AppHandle<Wry>) {
        match app.get_webview_panel(LABEL) {
            Ok(panel) => panel.order_out(None),
            Err(_) => {
                if let Some(w) = app.get_webview_window(LABEL) {
                    let _ = w.hide();
                }
            }
        }
    }

    /// 大きさ・位置を決めて前に出す（メインスレッドで行う）。どれかが失敗したら Err。
    fn place_and_show(app: &AppHandle<Wry>) -> Result<(), String> {
        let window = app
            .get_webview_window(LABEL)
            .ok_or_else(|| "window is not available".to_string())?;
        let panel = app
            .get_webview_panel(LABEL)
            .map_err(|_| "panel is not available".to_string())?;
        // 主画面の下の縁。縦の位置は直後に Dock の上端へ合わせる。
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
        let ns = ns_window(&window)?;
        follow_dock(ns, false);
        // key にしない（フォーカスを奪わない）。
        ns.orderFrontRegardless();
        panel.resign_key_window();
        Ok(())
    }

    /// 帯を出す。出せなくても背景は閉じない（理由を 1 行だけ警告に残す）。
    pub fn open(app: &AppHandle<Wry>) {
        if BUILD_FAILED.load(Ordering::Acquire) {
            return;
        }
        let handle = app.clone();
        let dispatched = app.run_on_main_thread(move || match place_and_show(&handle) {
            Ok(()) => {
                OPEN_GEN.fetch_add(1, Ordering::AcqRel);
                SHOWN.store(true, Ordering::Release);
                start_probe(handle);
            }
            Err(e) => {
                warn_once(&e);
                hide_panel(&handle);
            }
        });
        if dispatched.is_err() {
            warn_once("main thread is not available");
        }
    }

    /// 帯を隠す。描画も止めさせる（状態に `null` を送る）。
    pub fn close(app: &AppHandle<Wry>) {
        SHOWN.store(false, Ordering::Release);
        STRIP_VISIBLE.store(false, Ordering::Release);
        let _ = app.emit_to(
            LABEL,
            crate::handmark_stage::STATE_EVENT,
            Option::<StageState>::None,
        );
        let handle = app.clone();
        let _ = app.run_on_main_thread(move || hide_panel(&handle));
    }

    /// 状態を帯の窓へ配る（背景の窓へ配るのと同じ値）。
    pub fn emit_state(app: &AppHandle<Wry>, state: &StageState) {
        let _ = app.emit_to(LABEL, crate::handmark_stage::STATE_EVENT, Some(*state));
    }

    /// カーソルの近さ（0〜10）を帯の窓だけへ配る。値は記録・tracing に出さない（ADR-050 D2）。
    pub(crate) fn emit_near(app: &AppHandle<Wry>, near: u8) {
        let _ = app.emit_to(LABEL, NEAR_EVENT, near);
    }

    /// 見張りを 1 本だけ起こす（すでに回っていれば何もしない）。
    fn start_probe(app: AppHandle<Wry>) {
        if PROBE_RUNNING.swap(true, Ordering::AcqRel) {
            return;
        }
        let spawned = std::thread::Builder::new()
            .name("gse-handmark-strip-probe".to_string())
            .spawn(move || probe_loop(app));
        if spawned.is_err() {
            PROBE_RUNNING.store(false, Ordering::Release);
            warn_once("probe thread could not start");
        }
    }

    /// 帯の置き場と見えているかを 250ms ごとに読み、見えているかが変わったときだけ窓へ知らせる。
    /// 閉じたら抜ける（抜けたあとに開き直されていたら引き継ぐ）。
    fn probe_loop(app: AppHandle<Wry>) {
        let mut last: Option<bool> = None;
        let mut seen_gen = OPEN_GEN.load(Ordering::Acquire);
        loop {
            std::thread::sleep(PROBE_EVERY);
            if !SHOWN.load(Ordering::Acquire) || crate::is_shutting_down() {
                STRIP_VISIBLE.store(false, Ordering::Release);
                PROBE_RUNNING.store(false, Ordering::Release);
                // 抜ける直前に開き直されていたら、自分が続ける。
                if SHOWN.load(Ordering::Acquire)
                    && !crate::is_shutting_down()
                    && !PROBE_RUNNING.swap(true, Ordering::AcqRel)
                {
                    continue;
                }
                return;
            }
            let gen = OPEN_GEN.load(Ordering::Acquire);
            if gen != seen_gen {
                // 開き直し: 窓は見えているかを覚えていないので、最初の読みを必ず送る。
                seen_gen = gen;
                last = None;
            }
            // 窓の一覧はメインスレッドの外で読む（WindowServer とのやりとりで描画を止めない）。
            let main = core_graphics::display::CGDisplay::main().bounds();
            let fullscreen = fullscreen_window_shown(main.size.width, main.size.height);
            let (tx, rx) = mpsc::channel();
            let handle = app.clone();
            let dispatched = app.run_on_main_thread(move || {
                if !SHOWN.load(Ordering::Acquire) {
                    return;
                }
                let Some(window) = handle.get_webview_window(LABEL) else {
                    return;
                };
                let Ok(ns) = ns_window(&window) else { return };
                follow_dock(ns, fullscreen);
                let _ = tx.send(
                    ns.occlusionState()
                        .contains(objc2_app_kit::NSWindowOcclusionState::Visible),
                );
            });
            if dispatched.is_err() {
                continue;
            }
            let Ok(visible) = rx.recv_timeout(PROBE_EVERY * 4) else {
                continue;
            };
            // 読んでいる間に閉じられていたら捨てる。
            if !SHOWN.load(Ordering::Acquire) {
                continue;
            }
            STRIP_VISIBLE.store(visible, Ordering::Release);
            if visibility_changed(last, visible) {
                last = Some(visible);
                let _ = app.emit_to(LABEL, VISIBLE_EVENT, visible);
            }
        }
    }

    /// 主画面に、他のアプリの全画面の窓（層 0・幅いっぱいで下端まで）が出ているか。
    /// 読むのは窓の層・持ち主の pid・大きさだけで、アプリや窓の名前は読まない。
    /// 見張りのスレッドから呼ぶ（CGWindowListCopyWindowInfo はメインスレッドを要しない）。
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
                    reaches_screen_bottom(x, y, w, h, screen_w, screen_h)
                }
                _ => false,
            }
        })
    }

    /// 帯を、主画面の今の Space で使える領域（Dock を除く）の下端へ置く。Dock が引っ込んでいれば画面の下端になる。
    /// 全画面の Space でも `visibleFrame` は Dock を除いたままなので、他のアプリの全画面の窓が出ているときは
    /// 画面の下端へ置く。置いた下端の高さと主画面の高さ（点）を Atomic に置く。メインスレッドから呼ぶ。
    fn follow_dock(ns: &objc2_app_kit::NSWindow, fullscreen: bool) {
        let Some(mtm) = objc2::MainThreadMarker::new() else {
            return;
        };
        // 主画面（メニューバーのある画面・原点 0,0）。
        let Some(screen) = objc2_app_kit::NSScreen::screens(mtm).firstObject() else {
            return;
        };
        let sf = screen.frame();
        let vf = screen.visibleFrame();
        let lift = strip_bottom_pt(sf.origin.y, vf.origin.y, fullscreen);
        BOTTOM_BITS.store(lift.to_bits(), Ordering::Release);
        SCREEN_H_BITS.store(sf.size.height.to_bits(), Ordering::Release);
        let target = objc2_foundation::NSRect::new(
            objc2_foundation::NSPoint::new(sf.origin.x, sf.origin.y + lift),
            objc2_foundation::NSSize::new(sf.size.width, HEIGHT),
        );
        let now = ns.frame();
        let same = (now.origin.x - target.origin.x).abs() < 0.5
            && (now.origin.y - target.origin.y).abs() < 0.5
            && (now.size.width - target.size.width).abs() < 0.5
            && (now.size.height - target.size.height).abs() < 0.5;
        if !same {
            ns.setFrame_display(target, true);
        }
    }
}

#[cfg(target_os = "macos")]
pub use imp::{close, emit_state, open, setup, spot, visible};
// 近さを帯の窓へ送る口は crate の中だけ（呼べるのは `lib.rs` のポインタのスレッドだけ・検査が縛る）。
#[cfg(target_os = "macos")]
pub(crate) use imp::emit_near;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_fullscreen_window_reaches_the_bottom() {
        // 切り欠きのない画面の全画面。
        assert!(reaches_screen_bottom(
            0.0, 0.0, 1512.0, 982.0, 1512.0, 982.0
        ));
        // 切り欠きのある画面の全画面（上端が下がる）。
        assert!(reaches_screen_bottom(
            0.0, 38.0, 1512.0, 944.0, 1512.0, 982.0
        ));
    }

    #[test]
    fn a_zoomed_window_above_the_dock_does_not() {
        // メニューバーの下から Dock の上まで（全画面の外で広げた窓）。
        assert!(!reaches_screen_bottom(
            0.0, 33.0, 1512.0, 901.0, 1512.0, 982.0
        ));
        // 幅が足りない窓。
        assert!(!reaches_screen_bottom(
            0.0, 0.0, 800.0, 982.0, 1512.0, 982.0
        ));
        // 横にずれた窓。
        assert!(!reaches_screen_bottom(
            100.0, 0.0, 1512.0, 982.0, 1512.0, 982.0
        ));
    }

    #[test]
    fn the_strip_sits_on_the_dock_unless_a_fullscreen_window_is_up() {
        // Dock が 70pt 出ている主画面（フレームの原点 0・使える領域の原点 70）。
        assert_eq!(strip_bottom_pt(0.0, 70.0, false), 70.0);
        assert_eq!(strip_bottom_pt(0.0, 70.0, true), 0.0);
        // Dock が引っ込んでいれば、どちらも画面の下端。
        assert_eq!(strip_bottom_pt(0.0, 0.0, false), 0.0);
    }

    #[test]
    fn visibility_is_sent_on_the_first_read_and_on_change_only() {
        assert!(visibility_changed(None, true));
        assert!(visibility_changed(None, false));
        assert!(!visibility_changed(Some(true), true));
        assert!(!visibility_changed(Some(false), false));
        assert!(visibility_changed(Some(true), false));
        assert!(visibility_changed(Some(false), true));
    }
}
