//! 手跡の下の縁の帯の窓（macOS と Windows・ADR-051）。Windows の窓の作りは末尾の `imp`（判断 9）。試作 `handmark_edge_strip.rs` の窓の作りと見張りを写した。
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

/// 帯が人に見えうるか。窓の `occlusionState` が見えているだけでは足りない（浮く層の窓は、画面のロック中も
/// 見えている扱いのまま・2026-11-12 の画面の確かめ）。画面がロックされている・この利用者の画面が前に出ていない
/// （ユーザーの切り替え）・主画面が眠っているときは、見えていない。読めなかった値は見えていない側に倒す。
/// 拾えないもの: ロックしないスクリーンセーバー・Dock に隠れた分。
fn strip_seen(occlusion_visible: bool, session: Option<SessionView>, display_asleep: bool) -> bool {
    let Some(session) = session else {
        return false;
    };
    occlusion_visible && !session.locked && session.on_console && !display_asleep
}

/// 画面のセッションの読み（`CGSessionCopyCurrentDictionary`）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct SessionView {
    /// `CGSSessionScreenIsLocked` が真（ロックしていない間は鍵そのものが無い）。
    locked: bool,
    /// `kCGSSessionOnConsoleKey` が真（ユーザーの切り替えで裏にいるときは偽）。鍵が無ければ偽。
    on_console: bool,
}

/// 開いた回数（世代）と見えているかを 1 つの値に詰める（下位 1 ビットが見えているか）。
/// 見張りが「確かめてから書く」間に閉じて開き直されても、古い世代の読みを書かないように、比べて書く（CAS）。
fn pack_seen(gen: u32, visible: bool) -> u64 {
    (u64::from(gen) << 1) | u64::from(visible)
}

fn gen_of(v: u64) -> u32 {
    (v >> 1) as u32
}

fn seen_of(v: u64) -> bool {
    v & 1 == 1
}

/// 今の値 `cur` が世代 `gen` のときだけ、見えているかを `visible` にした値を返す（違う世代なら書かない）。
fn write_if_gen(cur: u64, gen: u32, visible: bool) -> Option<u64> {
    (gen_of(cur) == gen).then(|| pack_seen(gen, visible))
}

/// 開き直し: 世代を 1 つ進め、見えているかを偽にする（最初の読みまで見えていない）。
fn next_open(cur: u64) -> u64 {
    pack_seen(gen_of(cur).wrapping_add(1), false)
}

/// 見えているかが前回の送りから変わったか（最初の読みは必ず送る）。
fn visibility_changed(last: Option<bool>, now: bool) -> bool {
    last != Some(now)
}

/// 帯の層の警告の唯一の出口（`flag` ごとに 1 回だけ・値や状態を渡さない）。macOS と Windows の `imp` が使う。
#[cfg(any(target_os = "macos", windows))]
fn warn_once(flag: &std::sync::atomic::AtomicBool, reason: &str) {
    if !flag.swap(true, std::sync::atomic::Ordering::AcqRel) {
        tracing::warn!("handmark: edge strip: {}", reason);
    }
}

#[cfg(target_os = "macos")]
mod imp {
    use super::*;
    use crate::analysis::handmark::state::StageState;
    use crate::handmark_pointer_thread::StripSpot;
    use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
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
    /// 開いた回数（世代）と、帯が見えているか（`strip_seen`）。`pack_seen` の形。閉じたら見えているは偽。
    static STRIP_SEEN: AtomicU64 = AtomicU64::new(0);
    /// `setup()` で窓を作れなかった（以後の `open` はすぐ失敗にする）。
    static BUILD_FAILED: AtomicBool = AtomicBool::new(false);
    /// 「作れなかった・出せなかった」警告を出した（1 走行に 1 回）。
    static WARNED: AtomicBool = AtomicBool::new(false);
    /// 画面のセッションが読めなかったことを 1 回だけ残したか（見えていないのか、読めていないのかを後で分けるため）。
    static SESSION_WARNED: AtomicBool = AtomicBool::new(false);
    /// 見張りのスレッドが生きている（開け閉めを何度しても 1 本）。
    static PROBE_RUNNING: AtomicBool = AtomicBool::new(false);
    /// 帯の下端の高さ（点・f64 のビット）と主画面の高さ（点・f64 のビット）。近さの計算が読む。記録しない。
    static BOTTOM_BITS: AtomicU64 = AtomicU64::new(0);
    static SCREEN_H_BITS: AtomicU64 = AtomicU64::new(0);

    /// 帯が出ていて見えているか（駆動役が刻みごとに読む）。閉じたら偽。
    pub fn visible() -> bool {
        SHOWN.load(Ordering::Acquire) && seen_of(STRIP_SEEN.load(Ordering::Acquire))
    }

    /// 見えているかを偽にする（世代は残す）。
    fn clear_seen() {
        STRIP_SEEN.fetch_and(!1, Ordering::SeqCst);
    }

    /// 世代 `gen` の読みとして見えているかを書く。その間に開き直されていたら書かずに偽を返す。
    fn set_seen_for(gen: u32, visible: bool) -> bool {
        STRIP_SEEN
            .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |cur| {
                write_if_gen(cur, gen, visible)
            })
            .is_ok()
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
                warn_once(
                    &WARNED,
                    &format!("unavailable: window could not be built: {e}"),
                );
                return;
            }
        };
        // NSPanel にした窓を壊すとプロセスごと落ちる。閉じる要求は隠すだけにする。
        let handle = app.handle().clone();
        window.on_window_event(move |event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                hide_and_clear(&handle);
            }
        });
        if let Err(e) = make_panel(app.handle(), &window) {
            BUILD_FAILED.store(true, Ordering::Release);
            warn_once(&WARNED, &format!("unavailable: {e}"));
            hide_and_clear(app.handle());
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

    /// 帯を隠し、出ている印（`SHOWN`・`STRIP_SEEN` の見えている）も偽にする。閉じる要求・出せなかったとき・`close` が使う
    /// （印だけ残ると、隠れた帯の見張りが回り続け、近さの計算も帯がある前提で続く）。メインスレッドから呼ぶ。
    fn hide_and_clear(app: &AppHandle<Wry>) {
        SHOWN.store(false, Ordering::SeqCst);
        clear_seen();
        hide_panel(app);
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
                // 世代を進め、見えているかを偽にする（前の開きの読みを持ち越さない・最初の読みまで見えていない）。
                // 古い世代の見張りの書き込みは `set_seen_for` で捨てられる。
                let _ = STRIP_SEEN.fetch_update(Ordering::SeqCst, Ordering::SeqCst, |cur| {
                    Some(next_open(cur))
                });
                // SeqCst: 見張りの抜け際(`PROBE_RUNNING` を偽にしてから `SHOWN` を読む)との store→load の相互排他。
                SHOWN.store(true, Ordering::SeqCst);
                start_probe(handle);
            }
            Err(e) => {
                warn_once(&WARNED, &format!("unavailable: {e}"));
                hide_and_clear(&handle);
            }
        });
        if dispatched.is_err() {
            warn_once(&WARNED, "unavailable: main thread is not available");
        }
    }

    /// 帯を隠す。描画も止めさせる（状態に `null` を送る）。
    pub fn close(app: &AppHandle<Wry>) {
        SHOWN.store(false, Ordering::SeqCst);
        clear_seen();
        let _ = app.emit_to(
            LABEL,
            crate::handmark_stage::STATE_EVENT,
            Option::<StageState>::None,
        );
        let handle = app.clone();
        let _ = app.run_on_main_thread(move || {
            // 先に送られた `open` の処理がメインスレッドで後から走って `SHOWN` を真に戻していても、
            // ここ（その後に走る）でもう一度偽にする（隠れた帯の見張りが回り続けないように）。
            hide_and_clear(&handle);
        });
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
        // SeqCst: 直前の `SHOWN.store(true)` と、見張りの抜け際の `PROBE_RUNNING.store(false)` → `SHOWN.load` が、
        // 互いに相手の書きを見落として両方が古い値を読む(見張り 0 本で帯が出たまま)ことを避ける。
        if PROBE_RUNNING.swap(true, Ordering::SeqCst) {
            return;
        }
        let spawned = std::thread::Builder::new()
            .name("gse-handmark-strip-probe".to_string())
            .spawn(move || probe_loop(app));
        if spawned.is_err() {
            PROBE_RUNNING.store(false, Ordering::Release);
            warn_once(&WARNED, "unavailable: probe thread could not start");
        }
    }

    /// 帯の置き場と見えているかを 250ms ごとに読み、見えているかが変わったときだけ窓へ知らせる。
    /// 閉じたら抜ける（抜けたあとに開き直されていたら引き継ぐ）。
    fn probe_loop(app: AppHandle<Wry>) {
        let mut last: Option<bool> = None;
        let mut seen_gen = gen_of(STRIP_SEEN.load(Ordering::Acquire));
        loop {
            std::thread::sleep(PROBE_EVERY);
            if !SHOWN.load(Ordering::Acquire) || crate::is_shutting_down() {
                clear_seen();
                // SeqCst: `open` 側の `SHOWN.store(true)` → `PROBE_RUNNING.swap(true)` と store→load が向かい合う。
                // Release/Acquire では両側が古い値を読みうるので、この 4 つの操作は全順序にする。
                PROBE_RUNNING.store(false, Ordering::SeqCst);
                // 抜ける直前に開き直されていたら、自分が続ける。
                if SHOWN.load(Ordering::SeqCst)
                    && !crate::is_shutting_down()
                    && !PROBE_RUNNING.swap(true, Ordering::SeqCst)
                {
                    continue;
                }
                return;
            }
            // 読みの前に世代を覚える。書く直前に同じでなければ(読む間に閉じ→開き直しがあった)捨てる。
            let gen = gen_of(STRIP_SEEN.load(Ordering::Acquire));
            if gen != seen_gen {
                // 開き直し: 窓は見えているかを覚えていないので、最初の読みを必ず送る。
                seen_gen = gen;
                last = None;
            }
            // 窓の一覧・セッション・画面の眠りはメインスレッドの外で読む（WindowServer とのやりとりで描画を止めない）。
            let main_display = core_graphics::display::CGDisplay::main();
            let main = main_display.bounds();
            let session = read_session();
            if session.is_none() {
                warn_once(&SESSION_WARNED, "session dictionary unavailable");
            }
            let asleep = main_display.is_asleep();
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
            // 読めなかった刻みは、見えていない側に倒す（前の「見えている」を残さない）。窓への送りは変えない。
            if dispatched.is_err() {
                set_seen_for(gen, false);
                continue;
            }
            let Ok(occlusion_visible) = rx.recv_timeout(PROBE_EVERY * 4) else {
                set_seen_for(gen, false);
                continue;
            };
            let visible = strip_seen(occlusion_visible, session, asleep);
            // 読んでいる間に閉じられていた・閉じて開き直されていたら捨てる(古い読みを新しい窓の値にしない)。
            if !SHOWN.load(Ordering::Acquire) || !set_seen_for(gen, visible) {
                continue;
            }
            if visibility_changed(last, visible) {
                last = Some(visible);
                let _ = app.emit_to(LABEL, VISIBLE_EVENT, visible);
            }
        }
    }

    #[link(name = "CoreGraphics", kind = "framework")]
    extern "C" {
        fn CGSessionCopyCurrentDictionary() -> core_foundation::dictionary::CFDictionaryRef;
    }

    /// 画面のセッションを読む。読めなければ None（`strip_seen` は見えていない側に倒す）。
    /// 読むのはロックの印と前に出ているかの 2 つの真偽値だけで、利用者の名前などの他の鍵は読まない。
    fn read_session() -> Option<SessionView> {
        use core_foundation::base::{CFType, TCFType};
        use core_foundation::boolean::CFBoolean;
        use core_foundation::dictionary::CFDictionary;
        use core_foundation::number::CFNumber;
        use core_foundation::string::CFString;
        // SAFETY: Copy の規則の関数で、戻り値は呼び出し側が所有する CFDictionary か NULL（Apple の文書）。
        // NULL を確かめてから create の規則で包み、Drop で解放する。
        let raw = unsafe { CGSessionCopyCurrentDictionary() };
        if raw.is_null() {
            return None;
        }
        // SAFETY: raw は NULL でなく、Copy の規則で所有している（上の注記）。create の規則で包み、Drop で 1 回だけ解放する。
        let dict: CFDictionary<CFString, CFType> =
            unsafe { CFDictionary::wrap_under_create_rule(raw) };
        // 値は CFBoolean のことも CFNumber のこともある（on_console は CFNumber の 1 を実測）。
        let truthy = |key: &'static str| -> Option<bool> {
            let v = dict.find(CFString::from_static_string(key))?;
            if let Some(b) = v.downcast::<CFBoolean>() {
                return Some(bool::from(b));
            }
            v.downcast::<CFNumber>()
                .and_then(|n| n.to_i64())
                .map(|n| n != 0)
        };
        Some(SessionView {
            locked: truthy("CGSSessionScreenIsLocked").unwrap_or(false),
            on_console: truthy("kCGSSessionOnConsoleKey").unwrap_or(false),
        })
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

/// Windows の帯（判断 4・9）。Mac 版と同じ約束（駆動役が開け閉めを決める・窓は何も返さない・帯は従）で、
/// 窓の作りだけが違う: 最前面・クリック透過・焦点を取らない・作業領域の下端（全画面なら画面の下端）。
/// 画面共有に写さないかは読み戻し、写るなら帯は出さない（背景は閉じない）。
/// 見張りが読むのは作業領域・前面の窓の矩形とクラス名・入力のデスクトップの名前だけで、窓の題名は読まない。
#[cfg(windows)]
mod imp {
    use super::*;
    use crate::analysis::handmark::state::StageState;
    use crate::handmark_pointer_thread::StripSpot;
    use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
    use std::sync::mpsc;
    use std::time::Duration;
    use tauri::{AppHandle, Emitter, Manager, Wry};
    use windows::Win32::Foundation::{HWND, RECT};
    use windows::Win32::System::StationsAndDesktops::{
        CloseDesktop, GetUserObjectInformationW, OpenInputDesktop, DESKTOP_ACCESS_FLAGS,
        DESKTOP_CONTROL_FLAGS, UOI_NAME,
    };
    use windows::Win32::UI::WindowsAndMessaging::{
        GetClassNameW, GetForegroundWindow, GetWindowRect, GetWindowThreadProcessId,
        SystemParametersInfoW, SPI_GETWORKAREA, SYSTEM_PARAMETERS_INFO_UPDATE_FLAGS,
    };

    /// 帯の高さ（論理 px）。
    const HEIGHT: f64 = 14.0;
    /// 見張りの間隔。
    const PROBE_EVERY: Duration = Duration::from_millis(250);

    static SHOWN: AtomicBool = AtomicBool::new(false);
    static STRIP_SEEN: AtomicU64 = AtomicU64::new(0);
    static BUILD_FAILED: AtomicBool = AtomicBool::new(false);
    static WARNED: AtomicBool = AtomicBool::new(false);
    static SESSION_WARNED: AtomicBool = AtomicBool::new(false);
    static PROBE_RUNNING: AtomicBool = AtomicBool::new(false);
    /// 帯の下端の高さ（物理ピクセル・主画面の下端から）と主画面の高さ（物理ピクセル）。近さの計算が読む。記録しない。
    static BOTTOM_BITS: AtomicU64 = AtomicU64::new(0);
    static SCREEN_H_BITS: AtomicU64 = AtomicU64::new(0);

    /// 帯が出ていて見えているか（駆動役が刻みごとに読む）。閉じたら偽。
    pub fn visible() -> bool {
        SHOWN.load(Ordering::Acquire) && seen_of(STRIP_SEEN.load(Ordering::Acquire))
    }

    fn clear_seen() {
        STRIP_SEEN.fetch_and(!1, Ordering::SeqCst);
    }

    fn set_seen_for(gen: u32, visible: bool) -> bool {
        STRIP_SEEN
            .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |cur| {
                write_if_gen(cur, gen, visible)
            })
            .is_ok()
    }

    /// 帯の置き場（出ていなければ `None`）。ポインタのスレッドが近さの計算にだけ使う（単位は物理ピクセル。
    /// ポインタの一点も Windows では物理ピクセルなので揃う）。
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

    /// `setup()`（メインスレッド）から呼ぶ。窓を隠したまま作る。
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
        .always_on_top(true)
        // 覆われていても描画を絞らない（背景の窓と同じ）。
        .background_throttling(tauri::utils::config::BackgroundThrottlingPolicy::Disabled)
        .build()
        {
            Ok(w) => w,
            Err(e) => {
                BUILD_FAILED.store(true, Ordering::Release);
                warn_once(
                    &WARNED,
                    &format!("unavailable: window could not be built: {e}"),
                );
                return;
            }
        };
        let handle = app.handle().clone();
        window.on_window_event(move |event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                hide_and_clear(&handle);
            }
        });
    }

    fn hide_and_clear(app: &AppHandle<Wry>) {
        SHOWN.store(false, Ordering::SeqCst);
        clear_seen();
        if let Some(w) = app.get_webview_window(LABEL) {
            let _ = w.hide();
        }
    }

    /// 作業領域（物理ピクセル）。読めなければ None。
    fn work_area() -> Option<RECT> {
        let mut r = RECT::default();
        // SAFETY: 書き込み先はこの関数の中の RECT で、SPI_GETWORKAREA はそこに主画面の作業領域を書くだけ。
        unsafe {
            SystemParametersInfoW(
                SPI_GETWORKAREA,
                0,
                Some(&mut r as *mut RECT as *mut core::ffi::c_void),
                SYSTEM_PARAMETERS_INFO_UPDATE_FLAGS(0),
            )
        }
        .ok()?;
        Some(r)
    }

    /// 前面の窓が主画面の全体を覆っているか（他のプロセスの窓で、デスクトップではない）。
    /// 読むのは前面の窓の矩形・持ち主の pid・クラス名だけ（題名は読まない）。
    fn fullscreen_foreground(screen_w: f64, screen_h: f64) -> bool {
        // SAFETY: 前面の窓を問うだけ（無ければ null）。
        let fg = unsafe { GetForegroundWindow() };
        if fg.is_invalid() {
            return false;
        }
        let mut pid = 0u32;
        // SAFETY: 持ち主の pid を問うだけ。
        unsafe { GetWindowThreadProcessId(fg, Some(&mut pid)) };
        if pid == std::process::id() {
            return false;
        }
        if is_desktop_class(fg) {
            return false;
        }
        let mut r = RECT::default();
        // SAFETY: 矩形を問うだけ。
        if unsafe { GetWindowRect(fg, &mut r) }.is_err() {
            return false;
        }
        reaches_screen_bottom(
            f64::from(r.left),
            f64::from(r.top),
            f64::from(r.right - r.left),
            f64::from(r.bottom - r.top),
            screen_w,
            screen_h,
        ) && r.top <= 0
    }

    /// デスクトップの窓（`Progman`・`WorkerW`）か。Win+D やデスクトップのクリックで前面になり、画面の全体を覆う。
    fn is_desktop_class(h: HWND) -> bool {
        let mut buf = [0u16; 32];
        // SAFETY: クラス名を固定の長さの手元の配列に書かせるだけ。
        let n = unsafe { GetClassNameW(h, &mut buf) };
        let name = String::from_utf16_lossy(&buf[..n.max(0) as usize]);
        name == "Progman" || name == "WorkerW"
    }

    /// 画面がロックされているか（入力のデスクトップが `Default` でない）。読めなければ None。
    fn read_locked() -> Option<bool> {
        // SAFETY: 入力のデスクトップを読みの権限なしで開き、名前を手元の配列に読み、同じ関数で閉じる。
        //   ロック中は開けない（Winlogon のデスクトップ）ことがあり、そのときは None を返す。
        unsafe {
            let desk =
                OpenInputDesktop(DESKTOP_CONTROL_FLAGS(0), false, DESKTOP_ACCESS_FLAGS(0)).ok()?;
            let mut buf = [0u16; 64];
            let mut needed = 0u32;
            let read = GetUserObjectInformationW(
                windows::Win32::Foundation::HANDLE(desk.0),
                UOI_NAME,
                Some(buf.as_mut_ptr() as *mut core::ffi::c_void),
                (buf.len() * 2) as u32,
                Some(&mut needed),
            );
            let _ = CloseDesktop(desk);
            read.ok()?;
            let len = buf.iter().position(|&c| c == 0).unwrap_or(buf.len());
            Some(String::from_utf16_lossy(&buf[..len]) != "Default")
        }
    }

    /// 帯の下端（主画面の下端からの高さ・物理ピクセル）を決めて置く。メインスレッドから呼ぶ。
    fn follow_work_area(
        window: &tauri::WebviewWindow<Wry>,
        fullscreen: bool,
    ) -> Result<(), String> {
        let monitor = window
            .primary_monitor()
            .map_err(|e| format!("primary_monitor failed: {e}"))?
            .ok_or_else(|| "no primary monitor".to_string())?;
        let size = *monitor.size();
        let pos = *monitor.position();
        let screen_h = f64::from(size.height);
        let work_bottom = work_area().map_or(screen_h, |r| f64::from(r.bottom - pos.y));
        // 作業領域の下端（主画面の下端からの高さ）。全画面なら 0（画面の下端）。
        let lift = strip_bottom_pt(0.0, screen_h - work_bottom, fullscreen).max(0.0);
        let height = (HEIGHT * monitor.scale_factor()).round().max(1.0) as u32;
        BOTTOM_BITS.store(lift.to_bits(), Ordering::Release);
        SCREEN_H_BITS.store(screen_h.to_bits(), Ordering::Release);
        let y = pos.y + size.height as i32 - lift as i32 - height as i32;
        let target_pos = tauri::PhysicalPosition::new(pos.x, y);
        let target_size = tauri::PhysicalSize::new(size.width, height);
        if window.outer_position().ok() != Some(target_pos) {
            window
                .set_position(target_pos)
                .map_err(|e| format!("set_position failed: {e}"))?;
        }
        if window.outer_size().ok() != Some(target_size) {
            window
                .set_size(target_size)
                .map_err(|e| format!("set_size failed: {e}"))?;
        }
        Ok(())
    }

    /// 大きさ・位置・クリックの透過・画面共有の除外を決めて、焦点を奪わずに出す（メインスレッドで行う）。
    fn place_and_show(app: &AppHandle<Wry>) -> Result<(), String> {
        let window = app
            .get_webview_window(LABEL)
            .ok_or_else(|| "window is not available".to_string())?;
        follow_work_area(&window, false)?;
        window
            .set_ignore_cursor_events(true)
            .map_err(|e| format!("set_ignore_cursor_events failed: {e}"))?;
        window
            .set_always_on_top(true)
            .map_err(|e| format!("set_always_on_top failed: {e}"))?;
        window
            .set_content_protected(true)
            .map_err(|e| format!("set_content_protected failed: {e}"))?;
        let hwnd = window.hwnd().map_err(|e| format!("hwnd failed: {e}"))?.0 as isize;
        crate::handmark_desktop_windows::check_excluded_from_capture(hwnd)?;
        crate::handmark_desktop_windows::show_no_activate(hwnd);
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
                let _ = STRIP_SEEN.fetch_update(Ordering::SeqCst, Ordering::SeqCst, |cur| {
                    Some(next_open(cur))
                });
                SHOWN.store(true, Ordering::SeqCst);
                start_probe(handle);
            }
            Err(e) => {
                warn_once(&WARNED, &format!("unavailable: {e}"));
                hide_and_clear(&handle);
            }
        });
        if dispatched.is_err() {
            warn_once(&WARNED, "unavailable: main thread is not available");
        }
    }

    /// 帯を隠す。描画も止めさせる（状態に `null` を送る）。
    pub fn close(app: &AppHandle<Wry>) {
        SHOWN.store(false, Ordering::SeqCst);
        clear_seen();
        let _ = app.emit_to(
            LABEL,
            crate::handmark_stage::STATE_EVENT,
            Option::<StageState>::None,
        );
        let handle = app.clone();
        let _ = app.run_on_main_thread(move || {
            hide_and_clear(&handle);
        });
    }

    /// 状態を帯の窓へ配る（背景の窓へ配るのと同じ値）。
    pub fn emit_state(app: &AppHandle<Wry>, state: &StageState) {
        let _ = app.emit_to(LABEL, crate::handmark_stage::STATE_EVENT, Some(*state));
    }

    /// カーソルの近さ（0〜10）を帯の窓だけへ配る。値は記録・tracing に出さない（ADR-050 D2）。
    pub(crate) fn emit_near(app: &AppHandle<Wry>, near: u8) {
        let _ = app.emit_to(LABEL, NEAR_EVENT, near);
    }

    fn start_probe(app: AppHandle<Wry>) {
        if PROBE_RUNNING.swap(true, Ordering::SeqCst) {
            return;
        }
        let spawned = std::thread::Builder::new()
            .name("gse-handmark-strip-probe".to_string())
            .spawn(move || probe_loop(app));
        if spawned.is_err() {
            PROBE_RUNNING.store(false, Ordering::Release);
            warn_once(&WARNED, "unavailable: probe thread could not start");
        }
    }

    /// 帯の置き場と見えているかを 250ms ごとに読み、見えているかが変わったときだけ窓へ知らせる（Mac 版と同じ形）。
    fn probe_loop(app: AppHandle<Wry>) {
        let mut last: Option<bool> = None;
        let mut seen_gen = gen_of(STRIP_SEEN.load(Ordering::Acquire));
        loop {
            std::thread::sleep(PROBE_EVERY);
            if !SHOWN.load(Ordering::Acquire) || crate::is_shutting_down() {
                clear_seen();
                PROBE_RUNNING.store(false, Ordering::SeqCst);
                if SHOWN.load(Ordering::SeqCst)
                    && !crate::is_shutting_down()
                    && !PROBE_RUNNING.swap(true, Ordering::SeqCst)
                {
                    continue;
                }
                return;
            }
            let gen = gen_of(STRIP_SEEN.load(Ordering::Acquire));
            if gen != seen_gen {
                seen_gen = gen;
                last = None;
            }
            let locked = read_locked();
            if locked.is_none() {
                warn_once(&SESSION_WARNED, "input desktop unavailable");
            }
            let screen_h = f64::from_bits(SCREEN_H_BITS.load(Ordering::Acquire));
            let (tx, rx) = mpsc::channel();
            let handle = app.clone();
            let dispatched = app.run_on_main_thread(move || {
                if !SHOWN.load(Ordering::Acquire) {
                    return;
                }
                let Some(window) = handle.get_webview_window(LABEL) else {
                    return;
                };
                let Ok(Some(monitor)) = window.primary_monitor() else {
                    return;
                };
                let (sw, sh) = (
                    f64::from(monitor.size().width),
                    f64::from(monitor.size().height),
                );
                let fullscreen = fullscreen_foreground(sw, sh);
                let placed = follow_work_area(&window, fullscreen).is_ok();
                let _ = tx.send(placed && window.is_visible().unwrap_or(false));
            });
            if dispatched.is_err() || !screen_h.is_finite() || screen_h <= 0.0 {
                set_seen_for(gen, false);
                continue;
            }
            let Ok(shown) = rx.recv_timeout(PROBE_EVERY * 4) else {
                set_seen_for(gen, false);
                continue;
            };
            // 画面の眠りは読まない（Windows では眠ると描画も止まる）。ロックが読めなければ見えていない側に倒す。
            let session = locked.map(|locked| SessionView {
                locked,
                on_console: true,
            });
            let visible = strip_seen(shown, session, false);
            if !SHOWN.load(Ordering::Acquire) || !set_seen_for(gen, visible) {
                continue;
            }
            if visibility_changed(last, visible) {
                last = Some(visible);
                let _ = app.emit_to(LABEL, VISIBLE_EVENT, visible);
            }
        }
    }
}

#[cfg(windows)]
pub(crate) use imp::emit_near;
#[cfg(windows)]
pub use imp::{close, emit_state, open, setup, spot, visible};

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
    fn the_strip_is_seen_only_unlocked_on_console_and_awake() {
        let open = Some(SessionView {
            locked: false,
            on_console: true,
        });
        assert!(strip_seen(true, open, false));
        // 窓が覆われている。
        assert!(!strip_seen(false, open, false));
        // 画面のロック中（2026-11-12 は occlusionState が見えているのままだった）。
        let locked = Some(SessionView {
            locked: true,
            on_console: true,
        });
        assert!(!strip_seen(true, locked, false));
        // ユーザーの切り替えで裏にいる。
        let away = Some(SessionView {
            locked: false,
            on_console: false,
        });
        assert!(!strip_seen(true, away, false));
        // 主画面が眠っている。
        assert!(!strip_seen(true, open, true));
        // セッションが読めない。
        assert!(!strip_seen(true, None, false));
    }

    #[test]
    fn a_read_from_an_older_open_is_not_written() {
        let open1 = next_open(0);
        let g1 = gen_of(open1);
        // 同じ世代の読みは書ける。
        let seen = write_if_gen(open1, g1, true).expect("same gen");
        assert!(seen_of(seen));
        // 確かめた後に閉じて開き直された: 世代が進み、見えているは偽から始まる。
        let open2 = next_open(seen);
        assert!(!seen_of(open2));
        assert_ne!(gen_of(open2), g1);
        // 古い世代の読みは書かない（前の開きの「見えている」を新しい開きへ持ち越さない）。
        assert_eq!(write_if_gen(open2, g1, true), None);
        // 世代が一周しても詰め方が崩れない。
        let wrapped = next_open(pack_seen(u32::MAX, true));
        assert_eq!(gen_of(wrapped), 0);
        assert!(!seen_of(wrapped));
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
