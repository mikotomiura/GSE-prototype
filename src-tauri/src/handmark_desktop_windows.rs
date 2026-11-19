//! 手跡の背景の窓をデスクトップのすぐ上に保ち、デスクトップのアイコンの画素を背景の窓へ写す（Windows だけ・判断 9・10）。
//!
//! 背景の窓は Tauri の WebView2 のトップレベルの窓（画面共有に写さない）。Windows のデスクトップのアイコンは
//! デスクトップの窓（`Progman`）の子なので、その上に置いた窓はアイコンの上に重なる。そこで:
//! - **並び**: 16ms ごとに、背景の窓が `Progman` より上で最初に見える窓かを見て、違えば `Progman` のすぐ上へ入れ直す
//!   （Win+D・デスクトップのクリックで `Progman` が前に出るため）。判定は `handmark_desktop::decide_restack`。
//! - **アイコン**: `PrintWindow(SysListView32, 0)` で一覧の絵（背景は透明度 0）を取り、変わった 64×64 の区画だけを
//!   背景の窓へ送る。窓の前端は模様のある画素にだけ重ねる（`source-atop`）ので、模様がアイコンの後ろを流れて見える。
//!   取り直すのは、explorer の一覧の出来事（WinEvent・out-of-context）を受けて 50ms たったときと、5 秒ごとの保険。
//!
//! 読むもの・読まないもの（判断 10）:
//! - 読むのは窓のクラス名（`Progman`・`SHELLDLL_DefView`・`SysListView32` を探すため）・z 順・矩形・一覧の画素だけ。
//!   名前の文字列・窓の題名・アイコンの矩形（UI Automation）は読まない。WinEvent のコールバックの引数に文字列は無い。
//! - 画素は記録しない・tracing の値に入れない・背景の窓以外へ送らない。区画の要約（hash）だけを持ち、画素は送ったら捨てる。

use crate::handmark_desktop::{changed_tiles, decide_restack, Restack, TileOut};
use std::sync::atomic::{AtomicBool, AtomicIsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread::JoinHandle;
use std::time::{Duration, Instant};
use windows::core::{w, PCWSTR};
use windows::Win32::Foundation::{HWND, RECT};
use windows::Win32::Graphics::Gdi::{
    CreateCompatibleDC, CreateDIBSection, DeleteDC, DeleteObject, GetDC, ReleaseDC, SelectObject,
    BITMAPINFO, BITMAPINFOHEADER, BI_RGB, DIB_RGB_COLORS,
};
use windows::Win32::Storage::Xps::{PrintWindow, PRINT_WINDOW_FLAGS};
use windows::Win32::UI::Accessibility::{SetWinEventHook, UnhookWinEvent, HWINEVENTHOOK};
use windows::Win32::UI::WindowsAndMessaging::{
    DispatchMessageW, FindWindowExW, FindWindowW, GetWindow, GetWindowDisplayAffinity,
    GetWindowRect, GetWindowThreadProcessId, IsWindowVisible, PeekMessageW, SetWindowPos,
    ShowWindow, TranslateMessage, EVENT_OBJECT_CREATE, EVENT_OBJECT_NAMECHANGE, GW_HWNDPREV,
    HWND_BOTTOM, MSG, PM_REMOVE, SWP_ASYNCWINDOWPOS, SWP_NOACTIVATE, SWP_NOMOVE, SWP_NOSIZE,
    SW_SHOWNOACTIVATE, WDA_EXCLUDEFROMCAPTURE, WINEVENT_OUTOFCONTEXT, WINEVENT_SKIPOWNPROCESS,
};

/// 並びを見る間隔。
const RESTACK_MS: u64 = 16;
/// 一覧の出来事を受けてから取り直すまで（続けて来る出来事をまとめる）。
const SETTLE_MS: u128 = 50;
/// 出来事が来なくても取り直す間隔（保険）。
const FALLBACK_MS: u128 = 5_000;

/// 一覧の窓（WinEvent のコールバックが自分の出来事かを見分けるため）。0 は未設定。
static LISTVIEW: AtomicIsize = AtomicIsize::new(0);
/// 一覧に出来事があった（取り直しの印）。
static DIRTY: AtomicBool = AtomicBool::new(false);
/// 動いている番（1 つだけ）。
static KEEPER: Mutex<Option<Keeper>> = Mutex::new(None);

struct Keeper {
    stop: Arc<AtomicBool>,
    join: JoinHandle<()>,
}

/// 窓の取り込みの除外を読み戻す。`WDA_EXCLUDEFROMCAPTURE` でなければ Err（fail-closed）。
pub fn check_excluded_from_capture(hwnd: isize) -> Result<(), String> {
    let mut affinity = 0u32;
    // SAFETY: `hwnd` は呼び手（背景の窓のメインスレッド）が持つ生きた窓。`affinity` はこの関数の中の書き込み先。
    unsafe { GetWindowDisplayAffinity(HWND(hwnd as _), &mut affinity) }
        .map_err(|e| format!("GetWindowDisplayAffinity failed: {e}"))?;
    if affinity != WDA_EXCLUDEFROMCAPTURE.0 {
        return Err(format!(
            "display affinity read back is {affinity:#x}, not WDA_EXCLUDEFROMCAPTURE (fail-closed)"
        ));
    }
    Ok(())
}

/// 焦点を奪わずに窓を出す。
pub fn show_no_activate(hwnd: isize) {
    // SAFETY: `hwnd` は呼び手が持つ生きた窓。戻り値（前に見えていたか）は使わない。
    let _ = unsafe { ShowWindow(HWND(hwnd as _), SW_SHOWNOACTIVATE) };
}

/// 番を始める（動いていれば止めてから）。`send` はアイコンの区画を背景の窓へ送る口（画面の幅・高さと区画）。
/// `screen_w`・`screen_h` は主画面の大きさ（物理ピクセル・主画面は (0,0) から始まる）。
pub fn start(
    stage: isize,
    screen_w: u32,
    screen_h: u32,
    send: impl Fn(u32, u32, Vec<TileOut>) + Send + 'static,
) {
    stop();
    let stop_flag = Arc::new(AtomicBool::new(false));
    let flag = Arc::clone(&stop_flag);
    let spawned = std::thread::Builder::new()
        .name("gse-handmark-desktop".to_string())
        .spawn(move || run(HWND(stage as _), screen_w, screen_h, &flag, &send));
    match spawned {
        Ok(join) => {
            if let Ok(mut k) = KEEPER.lock() {
                *k = Some(Keeper {
                    stop: stop_flag,
                    join,
                });
            }
        }
        Err(_) => tracing::warn!("handmark desktop: keeper thread could not be started"),
    }
}

/// 番を止めて待つ。
pub fn stop() {
    let keeper = KEEPER.lock().ok().and_then(|mut k| k.take());
    if let Some(k) = keeper {
        k.stop.store(true, Ordering::Release);
        let _ = k.join.join();
    }
}

/// クラス名で子を探す。
fn child(parent: HWND, class: PCWSTR) -> Option<HWND> {
    // SAFETY: クラス名は静的な UTF-16 の文字列。見つからなければ Err（null）。
    unsafe { FindWindowExW(parent, None, class, None) }
        .ok()
        .filter(|h| !h.is_invalid())
}

fn progman() -> Option<HWND> {
    // SAFETY: 同上（トップレベルの窓をクラス名で探すだけ）。
    unsafe { FindWindowW(w!("Progman"), None) }
        .ok()
        .filter(|h| !h.is_invalid())
}

/// デスクトップの一覧（`Progman` → `SHELLDLL_DefView` → `SysListView32`）。
fn listview(pm: HWND) -> Option<HWND> {
    let dv = child(pm, w!("SHELLDLL_DefView"))?;
    child(dv, w!("SysListView32"))
}

/// `pm` のすぐ上の窓と、上で最初に見える窓。
fn above(pm: HWND) -> (Option<HWND>, Option<HWND>) {
    // SAFETY: z 順をたどるだけの問い合わせ。返る窓は他のプロセスのものもあるが、見えるかを問うだけで触らない。
    let just = unsafe { GetWindow(pm, GW_HWNDPREV) }
        .ok()
        .filter(|h| !h.is_invalid());
    let mut cur = just;
    while let Some(c) = cur {
        // SAFETY: 同上。
        if unsafe { IsWindowVisible(c) }.as_bool() {
            return (just, Some(c));
        }
        // SAFETY: 同上。
        cur = unsafe { GetWindow(c, GW_HWNDPREV) }
            .ok()
            .filter(|h| !h.is_invalid());
    }
    (just, None)
}

/// 並びを 1 回直す。最下へ落としたら真を返す（理由は呼び手が 1 回だけ残す）。
fn restack(stage: HWND) -> bool {
    let pm = progman();
    let (just, first) = pm.map(above).unwrap_or((None, None));
    let flags = SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_ASYNCWINDOWPOS;
    match decide_restack(pm.is_some(), first, just, stage) {
        Restack::Keep => false,
        Restack::Below(h) => {
            // SAFETY: `stage` は背景の窓（メインスレッドが持つ）。非同期で送るので、こちらは待たない。
            let _ = unsafe { SetWindowPos(stage, h, 0, 0, 0, 0, flags) };
            false
        }
        Restack::Bottom => {
            // SAFETY: 同上。
            let _ = unsafe { SetWindowPos(stage, HWND_BOTTOM, 0, 0, 0, 0, flags) };
            true
        }
    }
}

/// WinEvent のコールバック。一覧の出来事なら印を立てるだけ（`hook-constraints`: Atomic だけ）。
unsafe extern "system" fn on_list_event(
    _hook: HWINEVENTHOOK,
    _event: u32,
    hwnd: HWND,
    _id_object: i32,
    _id_child: i32,
    _thread: u32,
    _time: u32,
) {
    let lv = LISTVIEW.load(Ordering::Relaxed);
    if lv != 0 && hwnd.0 as isize == lv {
        DIRTY.store(true, Ordering::Relaxed);
    }
}

/// explorer の一覧の出来事を受ける（`EVENT_OBJECT_CREATE`〜`NAMECHANGE` の連続区間・explorer の pid だけ）。
fn hook_list_events(lv: HWND) -> Option<HWINEVENTHOOK> {
    let mut pid = 0u32;
    // SAFETY: `lv` は他のプロセスの窓だが、持ち主の pid を問うだけ。
    unsafe { GetWindowThreadProcessId(lv, Some(&mut pid)) };
    if pid == 0 {
        return None;
    }
    // SAFETY: out-of-context のフックで DLL を注入しない。コールバックはこのスレッドのメッセージの汲みの中で呼ばれ、
    //   同じスレッドで `UnhookWinEvent` する。
    let hook = unsafe {
        SetWinEventHook(
            EVENT_OBJECT_CREATE,
            EVENT_OBJECT_NAMECHANGE,
            None,
            Some(on_list_event),
            pid,
            0,
            WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS,
        )
    };
    (!hook.is_invalid()).then_some(hook)
}

/// 主画面の矩形（物理ピクセル）を、一覧の絵から切り出す。一覧の絵は premultiplied の BGRA（上から下）。
/// 取れなければ None。
fn capture(lv: HWND, screen_w: u32, screen_h: u32) -> Option<Vec<u32>> {
    let mut r = RECT::default();
    // SAFETY: 矩形を問うだけ。
    unsafe { GetWindowRect(lv, &mut r) }.ok()?;
    let (lw, lh) = (r.right - r.left, r.bottom - r.top);
    if lw <= 0 || lh <= 0 || lw > 32_768 || lh > 32_768 {
        return None;
    }
    let mut out = vec![0u32; (screen_w as usize) * (screen_h as usize)];
    // SAFETY: 画面の DC から互換の DC と 32bpp の DIB を作り、一覧の絵を描かせて読み、すべて同じ関数の中で解放する。
    //   DIB の画素は `bits` が指す `lw * lh` 個の u32 で、DC を解放するまで生きている。
    unsafe {
        let sdc = GetDC(None);
        let mdc = CreateCompatibleDC(sdc);
        let bmi = BITMAPINFO {
            bmiHeader: BITMAPINFOHEADER {
                biSize: std::mem::size_of::<BITMAPINFOHEADER>() as u32,
                biWidth: lw,
                biHeight: -lh,
                biPlanes: 1,
                biBitCount: 32,
                biCompression: BI_RGB.0,
                ..Default::default()
            },
            ..Default::default()
        };
        let mut bits: *mut core::ffi::c_void = std::ptr::null_mut();
        let ok = match CreateDIBSection(mdc, &bmi, DIB_RGB_COLORS, &mut bits, None, 0) {
            Ok(bmp) if !bits.is_null() => {
                let old = SelectObject(mdc, bmp);
                let n = (lw as usize) * (lh as usize);
                std::ptr::write_bytes(bits as *mut u32, 0, n);
                let printed = PrintWindow(lv, mdc, PRINT_WINDOW_FLAGS(0)).as_bool();
                if printed {
                    let src = std::slice::from_raw_parts(bits as *const u32, n);
                    for y in 0..screen_h as i32 {
                        let sy = y - r.top;
                        if !(0..lh).contains(&sy) {
                            continue;
                        }
                        for x in 0..screen_w as i32 {
                            let sx = x - r.left;
                            if (0..lw).contains(&sx) {
                                out[(y as usize) * (screen_w as usize) + x as usize] =
                                    src[(sy as usize) * (lw as usize) + sx as usize];
                            }
                        }
                    }
                    // 読んだ絵は捨てる（DIB を 0 で塗ってから解放する）。
                    std::ptr::write_bytes(bits as *mut u32, 0, n);
                }
                SelectObject(mdc, old);
                let _ = DeleteObject(bmp);
                printed
            }
            _ => false,
        };
        let _ = DeleteDC(mdc);
        ReleaseDC(None, sdc);
        if !ok {
            return None;
        }
    }
    Some(out)
}

/// メッセージを汲む（WinEvent のコールバックはここで呼ばれる）。
fn pump() {
    let mut msg = MSG::default();
    // SAFETY: このスレッドの待ち行列からメッセージを取り出して配るだけ。
    unsafe {
        while PeekMessageW(&mut msg, None, 0, 0, PM_REMOVE).as_bool() {
            let _ = TranslateMessage(&msg);
            DispatchMessageW(&msg);
        }
    }
}

fn run(stage: HWND, sw: u32, sh: u32, stop: &AtomicBool, send: &dyn Fn(u32, u32, Vec<TileOut>)) {
    let mut hook: Option<HWINEVENTHOOK> = None;
    let mut hooked_lv: isize = 0;
    let mut warned_bottom = false;
    let mut warned_hook = false;
    let mut prev: Vec<u64> = Vec::new();
    let mut dirty_since: Option<Instant> = None;
    // 最初の取り直しはすぐ。
    let mut last_capture = Instant::now() - Duration::from_millis(FALLBACK_MS as u64);
    DIRTY.store(false, Ordering::Relaxed);
    while !stop.load(Ordering::Acquire) {
        pump();
        if restack(stage) && !warned_bottom {
            warned_bottom = true;
            tracing::warn!("handmark desktop: Progman not found; stage placed at the bottom (icons drawn above the pattern)");
        }
        let lv = progman().and_then(listview);
        let lv_id = lv.map_or(0, |h| h.0 as isize);
        // 一覧が替わった（explorer の再起動など）: 印の相手を替え、フックを張り直す。
        if lv_id != hooked_lv {
            if let Some(h) = hook.take() {
                // SAFETY: 同じスレッドで張ったフックを外す。
                let _ = unsafe { UnhookWinEvent(h) };
            }
            LISTVIEW.store(lv_id, Ordering::Relaxed);
            hooked_lv = lv_id;
            if let Some(l) = lv {
                hook = hook_list_events(l);
                if hook.is_none() && !warned_hook {
                    warned_hook = true;
                    tracing::warn!(
                        "handmark desktop: list events not hooked; icons refresh every 5 s only"
                    );
                }
            }
            DIRTY.store(true, Ordering::Relaxed);
        }
        if DIRTY.swap(false, Ordering::Relaxed) && dirty_since.is_none() {
            dirty_since = Some(Instant::now());
        }
        let settled = dirty_since.is_some_and(|t| t.elapsed().as_millis() >= SETTLE_MS);
        let due = last_capture.elapsed().as_millis() >= FALLBACK_MS;
        if settled || due {
            dirty_since = None;
            last_capture = Instant::now();
            if let (Some(l), true) = (lv, sw > 0 && sh > 0) {
                if let Some(mut px) = capture(l, sw, sh) {
                    let tiles = changed_tiles(&mut prev, &px, sw, sh);
                    px.fill(0);
                    if !tiles.is_empty() {
                        send(sw, sh, tiles);
                    }
                }
            }
        }
        std::thread::sleep(Duration::from_millis(RESTACK_MS));
    }
    if let Some(h) = hook.take() {
        // SAFETY: 同じスレッドで張ったフックを外す。
        let _ = unsafe { UnhookWinEvent(h) };
    }
    LISTVIEW.store(0, Ordering::Relaxed);
}
