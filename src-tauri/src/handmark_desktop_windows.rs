//! 手跡の背景の窓をデスクトップのすぐ上に保ち、デスクトップのアイコンの画素を背景の窓へ写す（Windows だけ・判断 9・10）。
//!
//! 背景の窓は Tauri の WebView2 のトップレベルの窓（画面共有に写さない）。Windows のデスクトップのアイコンは
//! デスクトップの窓（`Progman`）の子なので、その上に置いた窓はアイコンの上に重なる。そこで:
//! - **並び**: 16ms ごとに、背景の窓が `Progman` より上で最初に見える窓かを見て、違えば `Progman` のすぐ上へ入れ直す
//!   （Win+D・デスクトップのクリックで `Progman` が前に出るため）。判定は `handmark_desktop::decide_restack`。
//! - **アイコン**: `PrintWindow(SysListView32, 0)` で一覧の絵（背景は透明度 0）を取り、変わった 64×64 の区画だけを
//!   背景の窓へ送る。窓の前端は模様のある画素にだけ重ねる（`source-atop`）ので、模様がアイコンの後ろを流れて見える。
//!   取り直すのは、explorer の一覧の出来事（WinEvent・out-of-context・一覧のスレッドだけ）が止んで 50ms たったときと、
//!   5 秒ごとの保険。30 秒ごとに全部を送り直す（窓の層と番の要約がずれても戻る）。
//!
//! 読むもの・読まないもの（判断 10）:
//! - 読むのは窓のクラス名（`Progman`・`SHELLDLL_DefView`・`SysListView32` を探すため）・z 順・矩形・見えるか・一覧の画素だけ。
//!   名前の文字列・窓の題名・アイコンの矩形（UI Automation）は読まない。WinEvent のコールバックの引数に文字列は無い。
//! - 画素は記録しない・tracing の値に入れない・背景の窓以外へ送らない。番が持ち回すのは画素の入れ物（取り直しのたびに
//!   0 で塗る）と区画の要約（hash）だけ。止めるときは 0 で塗って捨てる。
//!
//! 止め方: `stop` は印を立てるだけで待たない（`PrintWindow` は explorer に同期で描かせるので、explorer が固まると番も
//! 止まる。待つと駆動役やメインスレッドまで止まる）。番は各回の頭と送る直前に印を見て、立っていれば何もせず抜ける。

use crate::handmark_desktop::{changed_tiles, crop_primary, decide_restack, Restack, TileOut};
use std::sync::atomic::{AtomicBool, AtomicIsize, AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use windows::core::{w, PCWSTR};
use windows::Win32::Foundation::{HWND, RECT};
use windows::Win32::Graphics::Gdi::{
    CreateCompatibleDC, CreateDIBSection, DeleteDC, DeleteObject, GdiFlush, GetDC, ReleaseDC,
    SelectObject, BITMAPINFO, BITMAPINFOHEADER, BI_RGB, DIB_RGB_COLORS,
};
use windows::Win32::Storage::Xps::{PrintWindow, PRINT_WINDOW_FLAGS};
use windows::Win32::UI::Accessibility::{SetWinEventHook, UnhookWinEvent, HWINEVENTHOOK};
use windows::Win32::UI::WindowsAndMessaging::{
    DispatchMessageW, FindWindowExW, FindWindowW, GetSystemMetrics, GetWindow,
    GetWindowDisplayAffinity, GetWindowRect, GetWindowThreadProcessId, IsWindow, IsWindowVisible,
    PeekMessageW, SetWindowPos, ShowWindow, TranslateMessage, EVENT_OBJECT_CREATE,
    EVENT_OBJECT_NAMECHANGE, GW_HWNDPREV, HWND_BOTTOM, MSG, PM_REMOVE, SM_CXSCREEN, SM_CYSCREEN,
    SWP_ASYNCWINDOWPOS, SWP_NOACTIVATE, SWP_NOMOVE, SWP_NOSIZE, SWP_NOZORDER, SW_SHOWNOACTIVATE,
    WDA_EXCLUDEFROMCAPTURE, WINEVENT_OUTOFCONTEXT, WINEVENT_SKIPOWNPROCESS,
};

/// 並びを見る間隔。
const RESTACK_MS: u64 = 16;
/// 一覧の出来事が止んでから取り直すまで（続けて来る出来事をまとめる）。
const SETTLE_MS: u128 = 50;
/// 出来事が来なくても取り直す間隔（保険）。
const FALLBACK_MS: u128 = 5_000;
/// 全部を送り直す間隔（窓の層と要約のずれを戻す）。
const RESEND_ALL_MS: u128 = 30_000;
/// 一覧の絵の一辺の上限と画素の数の上限（壊れた矩形で大きすぎる入れ物を作らない）。
const MAX_SIDE: i32 = 16_384;
const MAX_PIXELS: i64 = 64 * 1024 * 1024;

/// 一覧の窓（WinEvent のコールバックが自分の出来事かを見分けるため）。0 は未設定。
static LISTVIEW: AtomicIsize = AtomicIsize::new(0);
/// 一覧に出来事があった（取り直しの印）。
static DIRTY: AtomicBool = AtomicBool::new(false);
/// 動いている番の止める印（1 つだけ）。
static KEEPER: Mutex<Option<Arc<AtomicBool>>> = Mutex::new(None);
/// 番の世代。`start`・`stop` のたびに進む。共有の印（`LISTVIEW`・`DIRTY`・`LAYOUT_LOST`）に触れてよいのは、
/// 世代が今の値と同じ番だけ（遅れて抜ける古い番が、新しい番の印を消さないように）。窓へ渡す区画にも付け、
/// 窓は古い世代の区画を捨てる。
static GEN: AtomicU64 = AtomicU64::new(0);
/// 開いた後にデスクトップの並びが崩れた（一覧が 3 秒見つからない）。背景の窓の様子を「出せなかった」にする。
static LAYOUT_LOST: AtomicBool = AtomicBool::new(false);
/// 一覧が見つからないまま、並びが崩れたとみなすまで。
const LOST_AFTER_MS: u128 = 3_000;
/// 取り直しが続けて失敗したら、窓の層を消させる回数。
const FAILS_BEFORE_CLEAR: u32 = 3;

/// 開いた後にデスクトップの並びが崩れたか（背景の窓の層の `status` が読む）。
pub fn layout_lost() -> bool {
    LAYOUT_LOST.load(Ordering::Acquire)
}

/// 区画を渡す口の形（世代・画面の幅・高さ・層を消してから置くか・区画）。
pub type SendTiles = Box<dyn Fn(u64, u32, u32, bool, Vec<TileOut>) + Send>;

/// 番が窓へ渡す口。
pub struct Sink {
    /// 区画を背景の窓へ渡す。引数は 世代・画面の幅・高さ（物理ピクセル）・層を消してから置くか・区画。
    pub send: SendTiles,
    /// 開いている間に主画面の大きさが変わった（物理ピクセル）。窓の層がポインタの写しの大きさを置き直す。
    pub on_resize: Box<dyn Fn(u32, u32) + Send>,
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

/// デスクトップの並びが、アイコンの後ろに背景を置ける形か（`Progman` の子に `SHELLDLL_DefView` と一覧がある）。
/// 違う並び（24H2 より前・壁紙のアプリが WorkerW を作った後など）では、`Progman` のすぐ上は不透明な WorkerW の
/// 下になりうるので、背景は出さない（出せなかったと扱う）。
pub fn desktop_layout_supported() -> bool {
    progman().and_then(listview).is_some()
}

/// 焦点を奪わずに窓を出す。
pub fn show_no_activate(hwnd: isize) {
    // SAFETY: `hwnd` は呼び手が持つ生きた窓。戻り値（前に見えていたか）は使わない。
    let _ = unsafe { ShowWindow(HWND(hwnd as _), SW_SHOWNOACTIVATE) };
}

/// 番を始める（動いていれば止めてから）。
pub fn start(stage: isize, sink: Sink) {
    stop();
    let gen = GEN.fetch_add(1, Ordering::AcqRel) + 1;
    LAYOUT_LOST.store(false, Ordering::Release);
    let flag = Arc::new(AtomicBool::new(false));
    let mine = Arc::clone(&flag);
    let spawned = std::thread::Builder::new()
        .name("gse-handmark-desktop".to_string())
        .spawn(move || run(HWND(stage as _), gen, &mine, &sink));
    match spawned {
        Ok(_) => {
            if let Ok(mut k) = KEEPER.lock() {
                *k = Some(flag);
            } else {
                flag.store(true, Ordering::Release);
            }
        }
        Err(_) => tracing::warn!("handmark desktop: keeper thread could not be started"),
    }
}

/// 番に止める印を立てる（待たない）。番は次の回の頭か、送る直前に抜ける。世代も進める（古い番は以後、共有の印にも
/// 窓にも触れない）。
pub fn stop() {
    GEN.fetch_add(1, Ordering::AcqRel);
    let flag = KEEPER.lock().ok().and_then(|mut k| k.take());
    if let Some(f) = flag {
        f.store(true, Ordering::Release);
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
            // SAFETY: `stage` は背景の窓（メインスレッドが持つ・各回の頭で生きているかを見た）。非同期で送るので待たない。
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

/// 一覧の出来事を受ける（`EVENT_OBJECT_CREATE`〜`NAMECHANGE` の連続区間・一覧を持つ explorer のスレッドだけ）。
fn hook_list_events(lv: HWND) -> Option<HWINEVENTHOOK> {
    let mut pid = 0u32;
    // SAFETY: `lv` は他のプロセスの窓だが、持ち主の pid と tid を問うだけ。
    let tid = unsafe { GetWindowThreadProcessId(lv, Some(&mut pid)) };
    if pid == 0 || tid == 0 {
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
            tid,
            WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS,
        )
    };
    (!hook.is_invalid()).then_some(hook)
}

/// 一覧の絵の入れ物（番の中で持ち回す・取り直しのたびに 0 で塗る）。
struct Canvas {
    src: Vec<u32>,
    out: Vec<u32>,
}

impl Canvas {
    fn wipe(&mut self) {
        self.src.fill(0);
        self.out.fill(0);
    }
}

/// 一覧の絵を取り、主画面（物理ピクセル `sw` × `sh`）の分を `c.out` に置く。一覧が隠れている（「デスクトップの
/// アイコンを表示」を切った）ときは全部透明。取れなければ偽（`c.out` は透明）。
fn capture(lv: HWND, sw: u32, sh: u32, c: &mut Canvas) -> bool {
    c.out.clear();
    c.out.resize((sw as usize) * (sh as usize), 0);
    // SAFETY: 見えるかを問うだけ。
    if !unsafe { IsWindowVisible(lv) }.as_bool() {
        return true;
    }
    let mut r = RECT::default();
    // SAFETY: 矩形を問うだけ。
    if unsafe { GetWindowRect(lv, &mut r) }.is_err() {
        return false;
    }
    let (lw, lh) = (r.right - r.left, r.bottom - r.top);
    if lw <= 0
        || lh <= 0
        || lw > MAX_SIDE
        || lh > MAX_SIDE
        || i64::from(lw) * i64::from(lh) > MAX_PIXELS
    {
        return false;
    }
    let n = (lw as usize) * (lh as usize);
    c.src.clear();
    c.src.resize(n, 0);
    // SAFETY: 画面の DC から互換の DC と 32bpp の DIB を作り、一覧の絵を描かせ、`GdiFlush` で描き終えてから読み、
    //   すべて同じ関数の中で解放する。DIB の画素は `bits` が指す `n` 個の u32 で、`DeleteObject(bmp)` まで生きている
    //   （読むのも 0 で塗るのもその前）。
    let printed = unsafe {
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
                std::ptr::write_bytes(bits as *mut u32, 0, n);
                let printed = PrintWindow(lv, mdc, PRINT_WINDOW_FLAGS(0)).as_bool();
                let _ = GdiFlush();
                if printed {
                    c.src
                        .copy_from_slice(std::slice::from_raw_parts(bits as *const u32, n));
                }
                // 読んだ絵は DIB に残さない（0 で塗ってから解放する）。
                std::ptr::write_bytes(bits as *mut u32, 0, n);
                SelectObject(mdc, old);
                let _ = DeleteObject(bmp);
                printed
            }
            _ => false,
        };
        let _ = DeleteDC(mdc);
        ReleaseDC(None, sdc);
        ok
    };
    let cropped = printed
        && crop_primary(
            &c.src, lw as u32, lh as u32, r.left, r.top, &mut c.out, sw, sh,
        );
    c.src.fill(0);
    cropped
}

/// 主画面の大きさ（物理ピクセル・このプロセスは Per-Monitor DPI aware）。
fn primary_size() -> (u32, u32) {
    // SAFETY: 引数は定数で、副作用の無い問い合わせ。
    let (w, h) = unsafe { (GetSystemMetrics(SM_CXSCREEN), GetSystemMetrics(SM_CYSCREEN)) };
    (w.max(0) as u32, h.max(0) as u32)
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

fn unhook(hook: &mut Option<HWINEVENTHOOK>) {
    if let Some(h) = hook.take() {
        // SAFETY: 同じスレッドで張ったフックを外す。
        let _ = unsafe { UnhookWinEvent(h) };
    }
}

fn run(stage: HWND, gen: u64, stop: &AtomicBool, sink: &Sink) {
    let current = || !stop.load(Ordering::Acquire) && GEN.load(Ordering::Acquire) == gen;
    let mut hook: Option<HWINEVENTHOOK> = None;
    let mut hooked_lv: isize = 0;
    let mut warned_bottom = false;
    let mut warned_hook = false;
    let mut warned_lost = false;
    let mut prev: Vec<u64> = Vec::new();
    let mut canvas = Canvas {
        src: Vec::new(),
        out: Vec::new(),
    };
    let mut last_event: Option<Instant> = None;
    // 最初の取り直しはすぐ（層を消してから置く）。
    let mut last_capture = Instant::now() - Duration::from_millis(FALLBACK_MS as u64);
    let mut last_full = Instant::now();
    let mut last_size = primary_size();
    let mut lv_missing_since: Option<Instant> = None;
    // 窓の層を空にさせた（一覧を見失った・取り直しが続けて失敗した）。戻ったら全部を送り直す。
    let mut cleared = false;
    let mut fails = 0u32;
    DIRTY.store(false, Ordering::Relaxed);
    loop {
        if !current() {
            break;
        }
        // SAFETY: 窓がまだあるかを問うだけ（壊れた後の再利用された HWND を動かさない）。
        if !unsafe { IsWindow(stage) }.as_bool() {
            break;
        }
        pump();
        if restack(stage) && !warned_bottom {
            warned_bottom = true;
            tracing::warn!("handmark desktop: Progman not found; stage placed at the bottom");
        }
        // 主画面の大きさが変わった: 窓の大きさと、ポインタの写しの大きさを置き直し、全部を送り直す。
        let size = primary_size();
        if size != last_size && size.0 > 0 && size.1 > 0 {
            last_size = size;
            let flags = SWP_NOZORDER | SWP_NOACTIVATE | SWP_ASYNCWINDOWPOS;
            // SAFETY: `stage` は背景の窓（頭で生きているかを見た）。非同期で送るので待たない。
            let _ = unsafe { SetWindowPos(stage, None, 0, 0, size.0 as i32, size.1 as i32, flags) };
            (sink.on_resize)(size.0, size.1);
            prev.clear();
            last_capture = Instant::now() - Duration::from_millis(FALLBACK_MS as u64);
        }
        let (sw, sh) = last_size;
        let lv = progman().and_then(listview);
        let lv_id = lv.map_or(0, |h| h.0 as isize);
        // 一覧が替わった（explorer の再起動など）: 印の相手を替え、フックを張り直し、全部を送り直す。
        if lv_id != hooked_lv {
            unhook(&mut hook);
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
            prev.clear();
            DIRTY.store(true, Ordering::Relaxed);
        }
        // 一覧を見失った: 古い写しを残さない（空にさせる）。3 秒続けば並びが崩れたとみなす（窓の層が出せなかった扱いへ）。
        if lv.is_none() {
            let since = *lv_missing_since.get_or_insert_with(Instant::now);
            if !cleared && current() && sw > 0 && sh > 0 {
                (sink.send)(gen, sw, sh, true, Vec::new());
                cleared = true;
                prev.clear();
            }
            if since.elapsed().as_millis() >= LOST_AFTER_MS && current() {
                LAYOUT_LOST.store(true, Ordering::Release);
                if !warned_lost {
                    warned_lost = true;
                    tracing::warn!(
                        "handmark desktop: desktop list lost; stage reported unavailable"
                    );
                }
            }
        } else {
            lv_missing_since = None;
        }
        // 出来事が来るたびに時刻を進める（止んでから 50ms で取り直す）。
        if DIRTY.swap(false, Ordering::Relaxed) {
            last_event = Some(Instant::now());
        }
        let settled = last_event.is_some_and(|t| t.elapsed().as_millis() >= SETTLE_MS);
        let due = last_capture.elapsed().as_millis() >= FALLBACK_MS;
        if last_full.elapsed().as_millis() >= RESEND_ALL_MS {
            last_full = Instant::now();
            prev.clear();
        }
        if settled || due {
            last_event = None;
            last_capture = Instant::now();
            if let (Some(l), true) = (lv, sw > 0 && sh > 0) {
                if capture(l, sw, sh, &mut canvas) {
                    fails = 0;
                    // 要約が空（最初・一覧が替わった・大きさが変わった・空にさせた後・30 秒ごと）なら、層を消してから置かせる。
                    let reset = prev.is_empty();
                    let tiles = changed_tiles(&mut prev, &canvas.out, sw, sh);
                    canvas.wipe();
                    if current() && (reset || !tiles.is_empty()) {
                        (sink.send)(gen, sw, sh, reset, tiles);
                        cleared = false;
                    }
                } else {
                    canvas.wipe();
                    fails = fails.saturating_add(1);
                    if fails >= FAILS_BEFORE_CLEAR && !cleared && current() {
                        (sink.send)(gen, sw, sh, true, Vec::new());
                        cleared = true;
                        prev.clear();
                    }
                }
            }
        }
        std::thread::sleep(Duration::from_millis(RESTACK_MS));
    }
    unhook(&mut hook);
    canvas.wipe();
    // 次の番が始まっていれば、共有の印に触れない。
    if GEN.load(Ordering::Acquire) == gen {
        LISTVIEW.store(0, Ordering::Relaxed);
    }
}
