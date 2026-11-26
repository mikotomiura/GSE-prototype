//! 手跡の背景の層の窓（macOS と Windows・ADR-051）。macOS は試作 `handmark_stage_spike.rs` の窓の作りを写した。
//!
//! 主画面の全体に透明な窓をデスクトップの高さ（壁紙の上・アイコンと他の窓の下）で出す。窓はマウスを受けない。
//! Windows はデスクトップのアイコンが `Progman` の子なので、トップレベルの窓を `Progman` のすぐ上に保ち
//! （`handmark_desktop_windows`）、アイコンの画素をこの窓へ写して模様のある所にだけ重ねる（判断 9・10）。
//! 開け閉めは駆動役の出来事（`handmark_driver::Effect`）だけが決める（環境変数の門は無い）。
//! 窓は何も返さない（`invoke` の口も記録も無い）。受け取るのは状態（`StageState`）だけで、
//! 推定（`engine`・`invitation`・`p_stuck`・`level`）を use しない。壁紙の画像を読まない・書かない。
//!
//! 窓は `setup()`（メインスレッド）で隠したまま作り、`open` / `close` は `run_on_main_thread` で行う。
//! 閉じる要求は止めて隠す（NSWindow を壊さない）。

use crate::analysis::handmark::state::StageState;
use crate::analysis::handmark::stopped::StoppedFrame;

/// 背景の窓の label。`capabilities/handmark-stage.json` と `src/main.tsx` の分岐と一致させる。
pub const LABEL: &str = "handmark-stage";
/// 状態を窓へ配るイベント名（`StageState` か、閉じたときの `null`）。
pub const STATE_EVENT: &str = "handmark-state";
/// 止まりの層（ADR-056）を窓へ配るイベント名（研究者用の設定が入っているときだけ送る・手跡の窓だけ）。
pub const STOPPED_EVENT: &str = "handmark-stopped";
/// 跡の場を窓へ配るイベント名（手跡の窓だけ・`emit_to`。ポインタ・ADR-050 D2〜D4）。
pub const TRACE_EVENT: &str = "handmark-trace";
/// 波紋の種（押下が始まった正準の位置）を窓へ配るイベント名（手跡の窓だけ）。
pub const RIPPLE_EVENT: &str = "handmark-ripple";
/// デスクトップのアイコンの区画を受ける、手跡の窓の中の関数の名前（Windows だけ・判断 10）。
/// アイコンの画素はイベント（`emit_to`）で送らない: Tauri のイベントは宛先を絞っても、全窓から聞く `listen` の受け手には
/// 届き、他の窓から同じ名前で偽の区画も送れる（tauri 2.10.2 `event/listener.rs` の `match_any_or_filter`）。
/// 手跡の窓の WebView だけで `eval` して、この関数を呼ぶ。
pub const ICONS_HOOK: &str = "__gseHandmarkIcons";

#[cfg(any(target_os = "macos", windows))]
mod imp {
    use super::*;
    use crate::analysis::handmark::trace::{encode_cells, RipplePoint, TraceState};
    use std::sync::atomic::{AtomicU32, AtomicU8, Ordering};
    use tauri::{AppHandle, Emitter, Manager, Wry};

    /// 主画面の大きさ（macOS は論理の point、Windows は物理ピクセル・f32 のビット）。窓を出すときに置き、
    /// ポインタのスレッドが一点を正準の箱へ写すのと、Windows のアイコンの写しの大きさにだけ使う。記録・tracing・窓へは出さない（ADR-050 D2）。0 は未設定。
    static SCREEN_W_BITS: AtomicU32 = AtomicU32::new(0);
    static SCREEN_H_BITS: AtomicU32 = AtomicU32::new(0);

    /// 主画面の大きさ（point）。未設定なら `(0.0, 0.0)`（`to_point` が `None` にする）。
    pub(crate) fn screen_size_pt() -> (f64, f64) {
        (
            f64::from(f32::from_bits(SCREEN_W_BITS.load(Ordering::Acquire))),
            f64::from(f32::from_bits(SCREEN_H_BITS.load(Ordering::Acquire))),
        )
    }

    fn set_screen_size_pt(w: f64, h: f64) {
        SCREEN_W_BITS.store((w as f32).to_bits(), Ordering::Release);
        SCREEN_H_BITS.store((h as f32).to_bits(), Ordering::Release);
    }

    /// 場の窓への payload。この型はこのファイルの外へ出さない（`Serialize` はここだけ）。
    #[derive(Clone, serde::Serialize)]
    #[serde(rename_all = "camelCase")]
    struct TracePayload {
        epoch: u32,
        /// 送った時刻（ポインタのスレッドの単調な ms。窓は届くまでのずれの最小との差で、遅れて届いた値を捨てる）。
        t_ms: u64,
        /// `i * GRID_W + col` の順に `bend`・`pull_x`・`pull_y`（各 −127〜127）。
        cells: Vec<i8>,
    }

    /// 波紋の種の payload。`x`・`y` は正準の箱（横 1.6・縦 1.0）。
    #[derive(Clone, serde::Serialize)]
    #[serde(rename_all = "camelCase")]
    struct RipplePayload {
        /// 押下が始まった刻みの場の世代（窓は今の世代より古い波紋を捨てる）。
        epoch: u32,
        t_ms: u64,
        x: f32,
        y: f32,
    }

    /// 場の量子化は `trace::encode_cells`（机上のコマと同じ関数・手跡の PR 4）。
    fn trace_payload(state: &TraceState, t_ms: u64) -> TracePayload {
        TracePayload {
            epoch: state.epoch,
            t_ms,
            cells: encode_cells(&state.cells),
        }
    }

    /// 窓の様子の印(駆動役が読む)。0 = まだ・1 = 出た・2 = 失敗(作れなかった・出せなかった)。
    static STATUS: AtomicU8 = AtomicU8::new(0);
    /// `setup()` で窓を作れなかった(以後の `open` はすぐ失敗にする)。
    static BUILD_FAILED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);

    /// 窓の様子(駆動役が刻みごとに読む)。
    pub fn status() -> crate::handmark_driver::WindowStatus {
        use crate::handmark_driver::WindowStatus;
        match STATUS.load(Ordering::Acquire) {
            // Windows: 開いた後にデスクトップの並びが崩れたら、見えない窓を出せた扱いにしない（駆動役が閉じる）。
            #[cfg(windows)]
            1 if crate::handmark_desktop_windows::layout_lost() => WindowStatus::Failed,
            1 => WindowStatus::Shown,
            2 => WindowStatus::Failed,
            _ => WindowStatus::Pending,
        }
    }

    #[cfg(target_os = "macos")]
    // CGWindowLevelKey（CGWindowLevel.h）のデスクトップの層（アイコンの層 kCGDesktopIconWindowLevelKey より下）。
    const K_CG_DESKTOP_WINDOW_LEVEL_KEY: i32 = 2;

    #[cfg(target_os = "macos")]
    #[link(name = "CoreGraphics", kind = "framework")]
    extern "C" {
        fn CGWindowLevelForKey(key: i32) -> i32;
    }

    #[cfg(target_os = "macos")]
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

    /// `setup()`（メインスレッド）から呼ぶ。窓を隠したまま作る。
    pub fn setup(app: &tauri::App<Wry>) {
        let window = match tauri::WebviewWindowBuilder::new(
            app,
            LABEL,
            tauri::WebviewUrl::App("index.html".into()),
        )
        .title("GSE")
        .inner_size(800.0, 600.0)
        .resizable(false)
        .decorations(false)
        .transparent(true)
        .shadow(false)
        .skip_taskbar(true)
        .focused(false)
        .visible(false)
        // この窓は作業中の窓にならず、他のアプリの窓に覆われることが多い。WKWebView の既定
        // （inactiveSchedulingPolicy = suspend）では、数分でタイマーと描画が絞られ、背景が粗く遅くなる
        // （2026-11-09 の画面の確かめ）。この窓だけ絞りを切る（macOS 14 以降で効く・wry 0.54）。
        .background_throttling(tauri::utils::config::BackgroundThrottlingPolicy::Disabled)
        .build()
        {
            Ok(w) => w,
            Err(e) => {
                tracing::warn!("handmark stage: window could not be built: {}", e);
                BUILD_FAILED.store(true, Ordering::Release);
                return;
            }
        };
        let hide_target = window.clone();
        window.on_window_event(move |event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                // Windows: アイコンの写しの番も止め、窓の層を消させる（`close` と同じ）。
                #[cfg(windows)]
                {
                    stop_icons(&hide_target);
                    let _ = hide_target.emit_to(LABEL, STATE_EVENT, Option::<StageState>::None);
                }
                let _ = hide_target.hide();
            }
        });
    }

    /// 大きさ・層・Spaces・クリックの透過を設定して前に出す。どれかが失敗したら Err。
    #[cfg(target_os = "macos")]
    fn prepare(window: &tauri::WebviewWindow<Wry>) -> Result<(), String> {
        let monitor = window
            .primary_monitor()
            .map_err(|e| format!("primary_monitor failed: {e}"))?
            .ok_or_else(|| "no primary monitor".to_string())?;
        // 作業領域ではなく画面の全体（メニューバーと Dock の下も壁紙がある）。
        window
            .set_size(*monitor.size())
            .map_err(|e| format!("set_size failed: {e}"))?;
        // 論理の point の大きさ（ポインタの写しにだけ使う）。
        let scale = monitor.scale_factor();
        if scale > 0.0 {
            set_screen_size_pt(
                f64::from(monitor.size().width) / scale,
                f64::from(monitor.size().height) / scale,
            );
        }
        window
            .set_position(*monitor.position())
            .map_err(|e| format!("set_position failed: {e}"))?;
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
        // 画面の共有・収録・スクリーンショットに写さない(NSWindowSharingNone)。読み返せなければ出さない。
        //   macOS 15 以降の収録で効くかは画面の確かめで見る。
        window
            .set_content_protected(true)
            .map_err(|e| format!("set_content_protected failed: {e}"))?;
        if ns.sharingType() != objc2_app_kit::NSWindowSharingType::None {
            return Err("sharingType read back is not None (fail-closed)".to_string());
        }
        // key にしない（フォーカスを奪わない）。
        ns.orderFrontRegardless();
        Ok(())
    }

    /// アイコンの区画の payload（Windows だけ・判断 10）。この型はこのファイルの外へ出さない。
    /// `rgba` は straight の RGBA を base64 にしたもの。空なら「この区画を消す」。
    #[cfg(windows)]
    #[derive(Clone, serde::Serialize)]
    #[serde(rename_all = "camelCase")]
    struct IconTilePayload {
        x: u32,
        y: u32,
        w: u32,
        h: u32,
        rgba: String,
    }

    /// 画面の大きさ（物理ピクセル）・層を消してから置くか・変わった区画。
    #[cfg(windows)]
    #[derive(Clone, serde::Serialize)]
    #[serde(rename_all = "camelCase")]
    struct IconsPayload {
        /// 番の世代（窓は閉じた後の世代・古い世代の区画を捨てる）。
        gen: u64,
        screen_w: u32,
        screen_h: u32,
        reset: bool,
        tiles: Vec<IconTilePayload>,
    }

    #[cfg(windows)]
    fn icons_payload(
        gen: u64,
        screen_w: u32,
        screen_h: u32,
        reset: bool,
        tiles: Vec<crate::handmark_desktop::TileOut>,
    ) -> IconsPayload {
        use base64::Engine as _;
        IconsPayload {
            gen,
            screen_w,
            screen_h,
            reset,
            tiles: tiles
                .into_iter()
                .map(|t| IconTilePayload {
                    x: t.x,
                    y: t.y,
                    w: t.w,
                    h: t.h,
                    rgba: base64::engine::general_purpose::STANDARD.encode(&t.rgba),
                })
                .collect(),
        }
    }

    /// 手跡の窓の WebView だけで、窓が置いた受け口を呼ぶ（他の窓には届かない・他の窓からは呼べない）。
    /// 区画も「閉じた」の知らせも同じ口を通るので、窓の中で順に処理される。
    #[cfg(windows)]
    fn call_icons_hook(window: &tauri::WebviewWindow<Wry>, json: &str) {
        let _ = window.eval(format!("window.{ICONS_HOOK}&&window.{ICONS_HOOK}({json})"));
    }

    /// 番を止め、窓の層に「この世代より前の区画を受けない・層を消す」と知らせる（区画と同じ口なので、閉じる前に
    /// 番が送った区画より後に処理される）。
    #[cfg(windows)]
    fn stop_icons(window: &tauri::WebviewWindow<Wry>) {
        crate::handmark_desktop_windows::stop();
        let gen = crate::handmark_desktop_windows::current_gen();
        call_icons_hook(window, &format!("{{\"closeGen\":{gen}}}"));
    }

    /// 大きさ・クリックの透過・画面共有の除外を設定し、焦点を奪わずに出して、デスクトップの番を始める。
    /// どれかが失敗したら Err（出さない）。
    #[cfg(windows)]
    fn prepare(window: &tauri::WebviewWindow<Wry>) -> Result<(), String> {
        let monitor = window
            .primary_monitor()
            .map_err(|e| format!("primary_monitor failed: {e}"))?
            .ok_or_else(|| "no primary monitor".to_string())?;
        // 作業領域ではなく画面の全体（タスクバーの下も壁紙がある）。座標は物理ピクセル（主画面は (0,0) から）。
        window
            .set_size(*monitor.size())
            .map_err(|e| format!("set_size failed: {e}"))?;
        window
            .set_position(*monitor.position())
            .map_err(|e| format!("set_position failed: {e}"))?;
        set_screen_size_pt(
            f64::from(monitor.size().width),
            f64::from(monitor.size().height),
        );
        window
            .set_ignore_cursor_events(true)
            .map_err(|e| format!("set_ignore_cursor_events failed: {e}"))?;
        // 画面の共有・収録・スクリーンショットに写さない。tao は SetWindowDisplayAffinity の戻り値を捨てるので
        // 自分で読み戻し、WDA_EXCLUDEFROMCAPTURE でなければ出さない（fail-closed・Mac と同じ）。
        window
            .set_content_protected(true)
            .map_err(|e| format!("set_content_protected failed: {e}"))?;
        let hwnd = window.hwnd().map_err(|e| format!("hwnd failed: {e}"))?;
        let hwnd = hwnd.0 as isize;
        crate::handmark_desktop_windows::check_excluded_from_capture(hwnd)?;
        // デスクトップの並びが違う（24H2 より前・壁紙のアプリの WorkerW など）と、Progman のすぐ上は不透明な窓の
        // 下になりうる。見えないのに出せた扱いにしないよう、出さない（駆動役は出せなかった理由を行に書く）。
        if !crate::handmark_desktop_windows::desktop_layout_supported() {
            return Err(
                "desktop layout not supported (no SHELLDLL_DefView under Progman)".to_string(),
            );
        }
        crate::handmark_desktop_windows::show_no_activate(hwnd);
        let target = window.clone();
        crate::handmark_desktop_windows::start(
            hwnd,
            crate::handmark_desktop_windows::Sink {
                send: Box::new(move |gen, sw, sh, reset, tiles| {
                    // 手跡の窓の WebView だけで、窓が置いた受け口を呼ぶ（他の窓には届かない・他の窓からは呼べない）。
                    let payload = icons_payload(gen, sw, sh, reset, tiles);
                    if let Ok(json) = serde_json::to_string(&payload) {
                        call_icons_hook(&target, &json);
                    }
                }),
                // 開いている間に主画面の大きさが変わった: ポインタの写しの大きさを置き直す（窓の大きさは番が直す）。
                on_resize: Box::new(|w, h| set_screen_size_pt(f64::from(w), f64::from(h))),
            },
        );
        Ok(())
    }

    /// 窓を出す(メインスレッドで行う)。出せなくても何も返さない(警告だけ)。
    pub fn open(app: &AppHandle<Wry>) {
        STATUS.store(0, Ordering::Release);
        if BUILD_FAILED.load(Ordering::Acquire) {
            STATUS.store(2, Ordering::Release);
            return;
        }
        let handle = app.clone();
        let dispatched = app.run_on_main_thread(move || {
            let Some(window) = handle.get_webview_window(LABEL) else {
                tracing::warn!("handmark stage: window is not available");
                STATUS.store(2, Ordering::Release);
                return;
            };
            match prepare(&window) {
                Ok(()) => STATUS.store(1, Ordering::Release),
                Err(e) => {
                    tracing::warn!("handmark stage: stage NOT shown: {}", e);
                    let _ = window.hide();
                    STATUS.store(2, Ordering::Release);
                }
            }
        });
        if dispatched.is_err() {
            STATUS.store(2, Ordering::Release);
        }
    }

    /// 窓を隠す。描画も止めさせる(状態に `null` を送る)。
    pub fn close(app: &AppHandle<Wry>) {
        // Windows: 先にデスクトップの番を止める（印を立てるだけで待たない）。前端は状態の null で写しを消す。
        #[cfg(windows)]
        crate::handmark_desktop_windows::stop();
        let _ = app.emit_to(LABEL, STATE_EVENT, Option::<StageState>::None);
        let handle = app.clone();
        let _ = app.run_on_main_thread(move || {
            // 直前の `open` の `prepare`（メインスレッドに先に積まれた）が番を始めていても、ここで止める
            // （メインスレッドの待ち行列は順に走るので、開いてすぐ閉じても番が残らない）。
            if let Some(w) = handle.get_webview_window(LABEL) {
                #[cfg(windows)]
                stop_icons(&w);
                let _ = w.hide();
            }
        });
    }

    /// 状態を窓へ配る。
    pub fn emit_state(app: &AppHandle<Wry>, state: &StageState) {
        let _ = app.emit_to(LABEL, STATE_EVENT, Some(*state));
    }

    /// 止まりの層を手跡の窓だけへ配る（窓を閉じたときは `STATE_EVENT` の `None` で窓の側が消す）。
    pub fn emit_stopped(app: &AppHandle<Wry>, frame: &StoppedFrame) {
        let _ = app.emit_to(LABEL, STOPPED_EVENT, frame);
    }

    /// 跡の場を手跡の窓だけへ配る（全窓へ流す `emit` は使わない）。`t_ms` はポインタのスレッドの単調な ms。
    pub(crate) fn emit_trace(app: &AppHandle<Wry>, state: &TraceState, t_ms: u64) {
        let _ = app.emit_to(LABEL, TRACE_EVENT, trace_payload(state, t_ms));
    }

    /// 波紋の種を手跡の窓だけへ配る。
    pub(crate) fn emit_ripple(app: &AppHandle<Wry>, r: &RipplePoint, t_ms: u64) {
        let _ = app.emit_to(
            LABEL,
            RIPPLE_EVENT,
            RipplePayload {
                epoch: r.epoch,
                t_ms,
                x: r.x,
                y: r.y,
            },
        );
    }

    #[cfg(test)]
    mod tests {
        use super::*;
        use crate::analysis::handmark::trace::{BEND_MAX, CELLS, MOTE_MAX};

        #[test]
        fn payload_is_cell_major_bend_pull_x_pull_y() {
            let mut st = TraceState {
                epoch: 7,
                cells: [[0.0; 3]; CELLS],
            };
            st.cells[0] = [BEND_MAX, 0.0, 0.0];
            st.cells[1] = [0.0, MOTE_MAX, -MOTE_MAX];
            st.cells[CELLS - 1] = [-BEND_MAX, 0.0, MOTE_MAX];
            let p = trace_payload(&st, 123);
            assert_eq!((p.epoch, p.t_ms, p.cells.len()), (7, 123, CELLS * 3));
            assert_eq!(&p.cells[0..6], &[127, 0, 0, 0, 127, -127]);
            assert_eq!(&p.cells[(CELLS - 1) * 3..], &[-127, 0, 127]);
        }

        #[test]
        fn the_screen_size_round_trips() {
            set_screen_size_pt(1440.0, 900.0);
            assert_eq!(screen_size_pt(), (1440.0, 900.0));
        }
    }
}

#[cfg(any(target_os = "macos", windows))]
pub use imp::{close, emit_state, emit_stopped, open, setup, status};
// 窓へ送る口と画面の大きさは crate の中だけ（呼べるのは `lib.rs` のポインタのスレッドだけ・検査が縛る）。
#[cfg(any(target_os = "macos", windows))]
pub(crate) use imp::{emit_ripple, emit_trace, screen_size_pt};
