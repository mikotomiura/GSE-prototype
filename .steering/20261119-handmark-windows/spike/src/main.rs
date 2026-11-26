//! 手跡の Windows 版の確かめの試作（使い捨て・main に入れない・design.md §1）。
//!
//! 使い方:
//!   spike probe-pointer <label> [秒]          位置とクリックの読み（ADR-050 の条件 (a)）
//!   spike layer <W|B1|B2|T|none> [秒]         背景の層の候補
//!   spike strip [秒]                          下の縁の帯
//!   spike tree                                デスクトップの窓の並び（Progman・WorkerW・DefView）を出す
//!
//! 出すのは数と成否だけ。位置の列・押下の時刻はファイルにも標準出力にも出さない。

use std::cell::RefCell;
use std::io::Write;
use std::time::{Duration, Instant};

use windows::core::{w, PCWSTR};
use windows::Win32::Foundation::{
    BOOL, COLORREF, FILETIME, HINSTANCE, HWND, LPARAM, LRESULT, POINT, RECT, WPARAM,
};
use windows::Win32::Graphics::Gdi::{
    BeginPaint, BitBlt, CreateCompatibleBitmap, CreateCompatibleDC, CreateSolidBrush, DeleteDC,
    DeleteObject, EndPaint, EnumDisplayMonitors, FillRect, GetDC, GetMonitorInfoW, GetPixel,
    InvalidateRect, ReleaseDC, SelectObject, HDC, HMONITOR, MONITORINFO, PAINTSTRUCT, SRCCOPY,
};
use windows::Win32::System::LibraryLoader::GetModuleHandleW;
use windows::Win32::System::Threading::{GetCurrentProcess, GetProcessTimes};
use windows::Win32::UI::HiDpi::{
    SetProcessDpiAwarenessContext, DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2,
};
use windows::Win32::UI::Input::KeyboardAndMouse::{GetAsyncKeyState, VK_LBUTTON};
use windows::Win32::UI::Shell::{SHAppBarMessage, ABM_GETSTATE, ABM_GETTASKBARPOS, APPBARDATA};
use windows::Win32::UI::WindowsAndMessaging::*;

// ---------------------------------------------------------------- 出力

fn out(s: &str) {
    let mut o = std::io::stdout().lock();
    let _ = writeln!(o, "{s}");
    let _ = o.flush();
}

macro_rules! say {
    ($($t:tt)*) => { out(&format!($($t)*)) };
}

// ---------------------------------------------------------------- 共通

fn hinstance() -> HINSTANCE {
    // SAFETY: 自分のモジュールの取得だけ。
    let m = unsafe { GetModuleHandleW(None) }.expect("GetModuleHandleW");
    HINSTANCE(m.0)
}

fn cpu_ms() -> f64 {
    let (mut c, mut e, mut k, mut u) = (
        FILETIME::default(),
        FILETIME::default(),
        FILETIME::default(),
        FILETIME::default(),
    );
    // SAFETY: 自プロセスの時間の読み。
    unsafe { GetProcessTimes(GetCurrentProcess(), &mut c, &mut e, &mut k, &mut u) }
        .expect("GetProcessTimes");
    let f = |t: FILETIME| ((u64::from(t.dwHighDateTime) << 32) | u64::from(t.dwLowDateTime)) as f64;
    (f(k) + f(u)) / 10_000.0
}

fn primary_monitor() -> (RECT, RECT) {
    // SAFETY: 主画面の問い合わせだけ。
    unsafe {
        let hm = windows::Win32::Graphics::Gdi::MonitorFromPoint(
            POINT { x: 0, y: 0 },
            windows::Win32::Graphics::Gdi::MONITOR_DEFAULTTOPRIMARY,
        );
        let mut mi = MONITORINFO {
            cbSize: std::mem::size_of::<MONITORINFO>() as u32,
            ..Default::default()
        };
        let _ = GetMonitorInfoW(hm, &mut mi);
        (mi.rcMonitor, mi.rcWork)
    }
}

fn rect_s(r: &RECT) -> String {
    format!(
        "({},{})-({},{}) {}x{}",
        r.left,
        r.top,
        r.right,
        r.bottom,
        r.right - r.left,
        r.bottom - r.top
    )
}

fn class_name(h: HWND) -> String {
    let mut buf = [0u16; 128];
    // SAFETY: バッファの長さを渡している。
    let n = unsafe { GetClassNameW(h, &mut buf) };
    String::from_utf16_lossy(&buf[..n.max(0) as usize])
}

fn pump_until(deadline: Instant, mut tick: impl FnMut()) {
    let mut msg = MSG::default();
    let mut last = Instant::now();
    while Instant::now() < deadline {
        // SAFETY: このスレッドのメッセージを回すだけ。
        unsafe {
            while PeekMessageW(&mut msg, HWND::default(), 0, 0, PM_REMOVE).as_bool() {
                let _ = TranslateMessage(&msg);
                DispatchMessageW(&msg);
            }
        }
        if last.elapsed() >= Duration::from_secs(1) {
            last = Instant::now();
            tick();
        }
        std::thread::sleep(Duration::from_millis(4));
    }
}

// ---------------------------------------------------------------- (a) 位置とクリック

fn probe_pointer(label: &str, secs: u64) {
    let started_cpu = cpu_ms();
    let mut reads: u64 = 0;
    let mut pos_fail: u64 = 0;
    let mut pos_changed: u64 = 0;
    let mut press_edges: u64 = 0;
    // 立ち上がりを見逃したが「前回の呼び出しから押された」ビット（最下位）だけが立っていた回数。
    let mut lsb_only: u64 = 0;
    let mut down_reads: u64 = 0;
    let mut last: Option<(i32, i32)> = None;
    let mut was_down = false;
    let start = Instant::now();
    let mut next_report = Duration::from_secs(5);
    say!("probe-pointer label={label} secs={secs} interval=16ms (VK_LBUTTON のみを読む)");
    while start.elapsed() < Duration::from_secs(secs) {
        let mut p = POINT::default();
        // SAFETY: いまの一点を読むだけ。
        match unsafe { GetCursorPos(&mut p) } {
            Ok(()) => {
                let now = (p.x, p.y);
                if last.is_some_and(|l| l != now) {
                    pos_changed += 1;
                }
                last = Some(now);
            }
            Err(_) => pos_fail += 1,
        }
        // SAFETY: マウスの左ボタンの仮想キーだけを渡す（キーボードの仮想キーは読まない・ADR-050 D3）。
        let s = unsafe { GetAsyncKeyState(i32::from(VK_LBUTTON.0)) } as u16;
        let down = s & 0x8000 != 0;
        if down {
            down_reads += 1;
        }
        if down && !was_down {
            press_edges += 1;
        } else if !down && !was_down && s & 0x0001 != 0 {
            lsb_only += 1;
        }
        was_down = down;
        reads += 1;
        if start.elapsed() >= next_report {
            say!(
                "  t={:>3}s reads={reads} press_edges={press_edges} lsb_only={lsb_only} pos_changed={pos_changed} pos_fail={pos_fail}",
                next_report.as_secs()
            );
            next_report += Duration::from_secs(5);
        }
        std::thread::sleep(Duration::from_millis(16));
    }
    let wall = start.elapsed().as_secs_f64();
    say!(
        "RESULT probe-pointer label={label} reads={reads} ({:.1}/s) press_edges={press_edges} lsb_only={lsb_only} down_reads={down_reads} pos_changed={pos_changed} pos_fail={pos_fail} cpu_ms={:.0}",
        reads as f64 / wall,
        cpu_ms() - started_cpu
    );
}

// ---------------------------------------------------------------- 窓の描画（共通）

#[derive(Default)]
struct Paint {
    frame: u64,
    w: i32,
    h: i32,
    /// 透過の色（黒）で塗るか（false なら暗い灰色で全面を塗る）。
    keyed: bool,
    /// 取り込みの確かめのために、決まった場所に橙の四角を止めて描く。
    freeze_probe: bool,
    /// 描かずに透かす矩形（デスクトップのアイコン・窓の中の座標）。B3 だけ。
    holes: Vec<RECT>,
    /// 穴を抜かずに 1 行おきに透かす（B4）。
    faint_holes: bool,
}

thread_local! {
    static PAINT: RefCell<Paint> = RefCell::new(Paint::default());
}

const ORANGE: COLORREF = COLORREF(0x0000_80FF); // 0x00BBGGRR
const KEY: COLORREF = COLORREF(0x0000_0000);

/// 取り込みの確かめに使う四角（窓の中の座標）。画面の中央の 200x200。
fn probe_rect(w: i32, h: i32) -> RECT {
    RECT {
        left: w / 2 - 100,
        top: h / 2 - 100,
        right: w / 2 + 100,
        bottom: h / 2 + 100,
    }
}

extern "system" fn wndproc(hwnd: HWND, msg: u32, wp: WPARAM, lp: LPARAM) -> LRESULT {
    // SAFETY: Win32 の窓の手続き。描画は BeginPaint の DC だけに行う。
    unsafe {
        match msg {
            WM_TIMER => {
                PAINT.with(|p| p.borrow_mut().frame += 1);
                let _ = InvalidateRect(hwnd, None, false);
                LRESULT(0)
            }
            WM_PAINT => {
                let mut ps = PAINTSTRUCT::default();
                let hdc = BeginPaint(hwnd, &mut ps);
                PAINT.with(|p| draw(hdc, &p.borrow()));
                let _ = EndPaint(hwnd, &ps);
                LRESULT(0)
            }
            WM_WINDOWPOSCHANGING => {
                if let Some(insert) = KEEP_BELOW.with(|k| *k.borrow()) {
                    let wp_ = &mut *(lp.0 as *mut WINDOWPOS);
                    wp_.hwndInsertAfter = insert;
                    wp_.flags &= !SWP_NOZORDER;
                }
                DefWindowProcW(hwnd, msg, wp, lp)
            }
            WM_MOUSEACTIVATE => LRESULT(MA_NOACTIVATE as isize),
            _ => DefWindowProcW(hwnd, msg, wp, lp),
        }
    }
}

thread_local! {
    /// 候補 B: z 順を保つ相手（この窓の上に来る窓・HWND_BOTTOM なら最下）。
    static KEEP_BELOW: RefCell<Option<HWND>> = const { RefCell::new(None) };
}

unsafe fn draw(hdc: HDC, p: &Paint) {
    let bg = if p.keyed { KEY } else { COLORREF(0x0030_3030) };
    let full = RECT {
        left: 0,
        top: 0,
        right: p.w,
        bottom: p.h,
    };
    let b = CreateSolidBrush(bg);
    FillRect(hdc, &full, b);
    let _ = DeleteObject(b);
    let o = CreateSolidBrush(ORANGE);
    if p.freeze_probe {
        FillRect(hdc, &probe_rect(p.w, p.h), o);
    } else {
        // 横に動く 80x80 の四角と、縦に動く細い帯。
        let span = (p.w - 80).max(1) as u64;
        let x = (p.frame * 6 % span) as i32;
        let y = p.h / 3;
        FillRect(
            hdc,
            &RECT {
                left: x,
                top: y,
                right: x + 80,
                bottom: y + 80,
            },
            o,
        );
        let yy = (p.frame * 3 % p.h.max(1) as u64) as i32;
        FillRect(
            hdc,
            &RECT {
                left: 0,
                top: yy,
                right: p.w,
                bottom: yy + 4,
            },
            o,
        );
    }
    let _ = DeleteObject(o);
    if p.keyed && !p.holes.is_empty() {
        let k = CreateSolidBrush(KEY);
        for r in &p.holes {
            if p.faint_holes {
                // 1 行おきに透かす（模様は半分の濃さで残り、アイコンが透けて見える）。
                let mut y = r.top;
                while y < r.bottom {
                    FillRect(hdc, &RECT { left: r.left, top: y, right: r.right, bottom: y + 1 }, k);
                    y += 2;
                }
            } else {
                FillRect(hdc, r, k);
            }
        }
        let _ = DeleteObject(k);
    }
}

// ---------------------------------------------------------------- デスクトップのアイコンの矩形（UI Automation）

/// デスクトップのアイコンの一覧（DefView の下の SysListView32）の子の矩形だけを読む。名前は読まない。
/// 返す矩形は画面の座標。
fn icon_rects() -> Result<Vec<RECT>, String> {
    use windows::Win32::System::Com::{CoCreateInstance, CoInitializeEx, CLSCTX_INPROC_SERVER, COINIT_APARTMENTTHREADED};
    use windows::Win32::UI::Accessibility::{CUIAutomation, IUIAutomation, TreeScope_Children};
    let pm = progman().ok_or("Progman not found")?;
    let dv = find(pm, HWND::default(), w!("SHELLDLL_DefView"))
        .or_else(|| {
            // 古い並び: DefView を持つトップレベルの WorkerW。
            let mut t = find(HWND::default(), HWND::default(), w!("WorkerW"));
            while let Some(h) = t {
                if let Some(d) = find(h, HWND::default(), w!("SHELLDLL_DefView")) {
                    return Some(d);
                }
                t = find(HWND::default(), h, w!("WorkerW"));
            }
            None
        })
        .ok_or("DefView not found")?;
    let lv = find(dv, HWND::default(), w!("SysListView32")).ok_or("SysListView32 not found")?;
    // SAFETY: このスレッドで COM を使い、UIA の要素から矩形だけを読む。
    unsafe {
        let _ = CoInitializeEx(None, COINIT_APARTMENTTHREADED);
        let uia: IUIAutomation = CoCreateInstance(&CUIAutomation, None, CLSCTX_INPROC_SERVER)
            .map_err(|e| format!("CUIAutomation: {e}"))?;
        let el = uia.ElementFromHandle(lv).map_err(|e| format!("ElementFromHandle: {e}"))?;
        let cond = uia.CreateTrueCondition().map_err(|e| format!("TrueCondition: {e}"))?;
        let arr = el
            .FindAll(TreeScope_Children, &cond)
            .map_err(|e| format!("FindAll: {e}"))?;
        let n = arr.Length().map_err(|e| format!("Length: {e}"))?;
        let mut v = Vec::new();
        for i in 0..n {
            if let Ok(e) = arr.GetElement(i) {
                if let Ok(r) = e.CurrentBoundingRectangle() {
                    if r.right > r.left && r.bottom > r.top {
                        v.push(r);
                    }
                }
            }
        }
        Ok(v)
    }
}

fn icons_report() {
    let t = Instant::now();
    match icon_rects() {
        Ok(v) => {
            let mut u = RECT { left: i32::MAX, top: i32::MAX, right: i32::MIN, bottom: i32::MIN };
            for r in &v {
                u.left = u.left.min(r.left);
                u.top = u.top.min(r.top);
                u.right = u.right.max(r.right);
                u.bottom = u.bottom.max(r.bottom);
            }
            let size = v.first().map(|r| format!("{}x{}", r.right - r.left, r.bottom - r.top)).unwrap_or("-".into());
            say!("icons count={} first_size={size} union={} read_ms={}", v.len(), if v.is_empty() { "-".into() } else { rect_s(&u) }, t.elapsed().as_millis());
        }
        Err(e) => say!("icons FAIL {e}"),
    }
}

fn register_class() -> PCWSTR {
    let cls = w!("HandmarkWinSpike");
    let wc = WNDCLASSW {
        lpfnWndProc: Some(wndproc),
        hInstance: hinstance(),
        lpszClassName: cls,
        // SAFETY: 既定の矢印のカーソル。
        hCursor: unsafe { LoadCursorW(None, IDC_ARROW) }.unwrap_or_default(),
        ..Default::default()
    };
    // SAFETY: 1 回だけ登録する。
    unsafe { RegisterClassW(&wc) };
    cls
}

// ---------------------------------------------------------------- 取り込みの確かめ

/// 画面を取り込み、橙の四角（画面の座標）の中の格子 10x10 の点のうち、橙の点の数を返す。
fn capture_orange(screen_rect: RECT) -> u32 {
    // SAFETY: 画面の DC からメモリの DC へ写して点を読むだけ。作った GDI の物はすべて解放する。
    unsafe {
        let w = screen_rect.right - screen_rect.left;
        let h = screen_rect.bottom - screen_rect.top;
        let sdc = GetDC(HWND::default());
        let mdc = CreateCompatibleDC(sdc);
        let bmp = CreateCompatibleBitmap(sdc, w, h);
        let old = SelectObject(mdc, bmp);
        let _ = BitBlt(
            mdc,
            0,
            0,
            w,
            h,
            sdc,
            screen_rect.left,
            screen_rect.top,
            SRCCOPY,
        );
        let mut n = 0;
        for i in 0..10 {
            for j in 0..10 {
                let c = GetPixel(mdc, w * (2 * i + 1) / 20, h * (2 * j + 1) / 20).0;
                let (r, g, b) = (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF);
                if r > 200 && (100..160).contains(&g) && b < 60 {
                    n += 1;
                }
            }
        }
        SelectObject(mdc, old);
        let _ = DeleteObject(bmp);
        let _ = DeleteDC(mdc);
        ReleaseDC(HWND::default(), sdc);
        n
    }
}

fn affinity_s(hwnd: HWND) -> String {
    let mut a: u32 = 0;
    // SAFETY: 読み戻しだけ。
    match unsafe { GetWindowDisplayAffinity(hwnd, &mut a) } {
        Ok(()) => format!("0x{a:02X}"),
        Err(e) => format!("err({e})"),
    }
}

/// 取り込みの確かめ: 四角を止め、除外なし（対照）→ 除外ありの順に取り込む。
/// `origin` は窓の中の座標を画面の座標へ直すずれ。
fn capture_check(hwnd: HWND, origin: (i32, i32)) {
    let (w, h) = PAINT.with(|p| {
        let mut p = p.borrow_mut();
        p.freeze_probe = true;
        (p.w, p.h)
    });
    let r = probe_rect(w, h);
    let sr = RECT {
        left: r.left + origin.0,
        top: r.top + origin.1,
        right: r.right + origin.0,
        bottom: r.bottom + origin.1,
    };
    let settle = |ms| pump_until(Instant::now() + Duration::from_millis(ms), || {});
    // SAFETY: 自分の窓の再描画を頼むだけ。
    unsafe {
        let _ = InvalidateRect(hwnd, None, false);
    }
    settle(500);
    // SAFETY: 自分の窓の取り込みの設定。
    let off = unsafe { SetWindowDisplayAffinity(hwnd, WDA_NONE) };
    settle(300);
    let control = capture_orange(sr);
    // SAFETY: 同上。
    let on = unsafe { SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE) };
    settle(500);
    let excluded = capture_orange(sr);
    say!(
        "CAPTURE set_none={} control_orange={control}/100 set_exclude={} readback={} excluded_orange={excluded}/100",
        off.is_ok(),
        on.as_ref().map(|_| "ok".to_string()).unwrap_or_else(|e| format!("err({e})")),
        affinity_s(hwnd)
    );
    PAINT.with(|p| p.borrow_mut().freeze_probe = false);
}

// ---------------------------------------------------------------- デスクトップの窓の並び

fn find(parent: HWND, after: HWND, class: PCWSTR) -> Option<HWND> {
    // SAFETY: 窓の検索だけ。
    unsafe { FindWindowExW(parent, after, class, PCWSTR::null()) }
        .ok()
        .filter(|h| !h.is_invalid())
}

fn progman() -> Option<HWND> {
    // SAFETY: 窓の検索だけ。
    unsafe { FindWindowW(w!("Progman"), PCWSTR::null()) }
        .ok()
        .filter(|h| !h.is_invalid())
}

/// Progman に 0x052C を送り、壁紙の後ろに WorkerW を作らせる（Lively などと同じ非公開の手）。
fn spawn_workerw(pm: HWND) {
    let mut r: usize = 0;
    // SAFETY: 非公開のメッセージを送るだけ（タイムアウトつき）。
    unsafe {
        SendMessageTimeoutW(pm, 0x052C, WPARAM(0xD), LPARAM(0x1), SMTO_NORMAL, 1000, Some(&mut r));
        SendMessageTimeoutW(pm, 0x052C, WPARAM(0), LPARAM(0), SMTO_NORMAL, 1000, Some(&mut r));
    }
}

fn tree() {
    let Some(pm) = progman() else {
        say!("Progman not found");
        return;
    };
    say!("Progman={:?}", pm.0);
    let mut c = find(pm, HWND::default(), PCWSTR::null());
    while let Some(h) = c {
        say!("  child of Progman: {:?} class={}", h.0, class_name(h));
        c = find(pm, h, PCWSTR::null());
    }
    // トップレベルの WorkerW と、その子の DefView。
    let mut t = find(HWND::default(), HWND::default(), w!("WorkerW"));
    while let Some(h) = t {
        let dv = find(h, HWND::default(), w!("SHELLDLL_DefView"));
        // SAFETY: 見えているかの問い合わせだけ。
        let vis = unsafe { IsWindowVisible(h) }.as_bool();
        say!("  top-level WorkerW {:?} visible={vis} has_DefView={}", h.0, dv.is_some());
        t = find(HWND::default(), h, w!("WorkerW"));
    }
    // Progman の上にある窓（z 順で 1 つ上）。
    // SAFETY: z 順の問い合わせだけ。
    if let Ok(prev) = unsafe { GetWindow(pm, GW_HWNDPREV) } {
        say!("  above Progman: {:?} class={}", prev.0, class_name(prev));
    }
}

// ---------------------------------------------------------------- (b) 背景の層

fn layer(cand: &str, secs: u64) {
    let cls = register_class();
    let (mon, _) = primary_monitor();
    let (w, h) = (mon.right - mon.left, mon.bottom - mon.top);
    let keyed = matches!(cand, "B1" | "B2" | "B3" | "B4" | "T");
    PAINT.with(|p| {
        *p.borrow_mut() = Paint {
            w,
            h,
            keyed,
            ..Default::default()
        }
    });
    say!("layer candidate={cand} primary={}", rect_s(&mon));
    let cpu0 = cpu_ms();
    let t0 = Instant::now();

    // SAFETY: 窓を作り、置き場を決める。終わったら DestroyWindow する。
    let (hwnd, origin) = unsafe {
        match cand {
            "W" | "WL" => {
                let Some(pm) = progman() else {
                    say!("FAIL Progman not found");
                    return;
                };
                spawn_workerw(pm);
                // 24H2 以降: WorkerW は Progman の子。以前: DefView を持つトップレベルの WorkerW の次の WorkerW。
                let child_ww = find(pm, HWND::default(), w!("WorkerW"));
                let dv_in_pm = find(pm, HWND::default(), w!("SHELLDLL_DefView"));
                let (parent, layout) = if let Some(ww) = child_ww {
                    (pm, format!("24H2-style (WorkerW {:?} is child of Progman, DefView in Progman={})", ww.0, dv_in_pm.is_some()))
                } else {
                    let mut t = find(HWND::default(), HWND::default(), w!("WorkerW"));
                    let mut target = None;
                    while let Some(hh) = t {
                        if find(hh, HWND::default(), w!("SHELLDLL_DefView")).is_some() {
                            target = find(HWND::default(), hh, w!("WorkerW"));
                            break;
                        }
                        t = find(HWND::default(), hh, w!("WorkerW"));
                    }
                    match target {
                        Some(ww) => (ww, format!("legacy (top-level WorkerW {:?})", ww.0)),
                        None => {
                            say!("FAIL no WorkerW found after 0x052C");
                            return;
                        }
                    }
                };
                say!("  W layout: {layout}");
                // 親の座標: 親はふつう仮想画面の全体を覆うので、主画面の位置へずらす。
                let mut pr = RECT::default();
                let _ = GetWindowRect(parent, &mut pr);
                let ox = mon.left - pr.left;
                let oy = mon.top - pr.top;
                // 24H2 の Progman の下では、子に WS_EX_LAYERED が要るという報告がある。両方を試せるよう環境変数で切る。
                let layered = cand == "WL";
                let ex = if layered { WS_EX_LAYERED } else { WINDOW_EX_STYLE(0) };
                let hwnd = match CreateWindowExW(
                    ex,
                    cls,
                    w!("handmark spike W"),
                    WS_CHILD | WS_VISIBLE,
                    ox,
                    oy,
                    w,
                    h,
                    parent,
                    HMENU::default(),
                    hinstance(),
                    None,
                ) {
                    Ok(hh) => hh,
                    Err(e) => {
                        say!("FAIL CreateWindowExW(child): {e}");
                        return;
                    }
                };
                if layered {
                    let _ = SetLayeredWindowAttributes(hwnd, KEY, 255, LWA_ALPHA);
                }
                if parent == pm {
                    // DefView（アイコン）の下・WorkerW（壁紙）の上へ。
                    if let Some(dv) = dv_in_pm {
                        let r = SetWindowPos(hwnd, dv, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);
                        say!("  placed below DefView: {}", r.is_ok());
                    }
                }
                say!("  layered={layered} parent_ok={}", GetParent(hwnd).map(|p| p == parent).unwrap_or(false));
                (hwnd, (mon.left, mon.top))
            }
            "B1" | "B2" | "B3" | "B4" | "T" => {
                let topmost = cand == "T";
                let mut ex = WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE | WS_EX_TRANSPARENT | WS_EX_LAYERED;
                if topmost {
                    ex |= WS_EX_TOPMOST;
                }
                let hwnd = match CreateWindowExW(
                    ex,
                    cls,
                    w!("handmark spike"),
                    WS_POPUP,
                    mon.left,
                    mon.top,
                    w,
                    h,
                    HWND::default(),
                    HMENU::default(),
                    hinstance(),
                    None,
                ) {
                    Ok(hh) => hh,
                    Err(e) => {
                        say!("FAIL CreateWindowExW: {e}");
                        return;
                    }
                };
                let _ = SetLayeredWindowAttributes(hwnd, KEY, 0, LWA_COLORKEY);
                let _ = ShowWindow(hwnd, SW_SHOWNOACTIVATE);
                if !topmost {
                    let insert = if cand == "B1" {
                        HWND_BOTTOM
                    } else {
                        // B2: Progman の 1 つ上の窓の下（= Progman のすぐ上）へ。
                        match progman().and_then(|pm| GetWindow(pm, GW_HWNDPREV).ok()) {
                            Some(prev) if prev != hwnd => prev,
                            _ => HWND_BOTTOM,
                        }
                    };
                    KEEP_BELOW.with(|k| *k.borrow_mut() = Some(insert));
                    let r = SetWindowPos(hwnd, insert, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);
                    say!("  z-order insert_after={:?} ok={}", insert.0, r.is_ok());
                }
                (hwnd, (mon.left, mon.top))
            }
            "none" => {
                // 対照: 見えない窓でタイマーと描画の要求だけ回す。
                let hwnd = CreateWindowExW(
                    WS_EX_TOOLWINDOW,
                    cls,
                    w!("handmark spike none"),
                    WS_POPUP,
                    0,
                    0,
                    w,
                    h,
                    HWND::default(),
                    HMENU::default(),
                    hinstance(),
                    None,
                )
                .expect("CreateWindowExW");
                (hwnd, (0, 0))
            }
            _ => {
                say!("unknown candidate {cand}");
                return;
            }
        }
    };
    // SAFETY: 自分の窓のタイマー（16ms）。
    unsafe { SetTimer(hwnd, 1, 16, None) };

    let report = |hwnd: HWND, t: u64| {
        // SAFETY: 状態の問い合わせだけ。
        let (vis, iconic, parent) = unsafe {
            (
                IsWindowVisible(hwnd).as_bool(),
                IsIconic(hwnd).as_bool(),
                GetParent(hwnd).map(|p| format!("{:?}", p.0)).unwrap_or("-".into()),
            )
        };
        // SAFETY: 窓が生きているか。
        let alive = unsafe { IsWindow(hwnd).as_bool() };
        say!("  t={t:>3}s alive={alive} visible={vis} iconic={iconic} parent={parent}");
    };

    let mut sec = 0u64;
    let b3 = matches!(cand, "B3" | "B4");
    PAINT.with(|p| p.borrow_mut().faint_holes = cand == "B4");
    let refresh_holes = || {
        if let Ok(v) = icon_rects() {
            // 画面の座標 → 窓の中の座標（窓は主画面の原点に置いた）。アイコンの縁を 2px 広げる。
            let holes: Vec<RECT> = v
                .iter()
                .map(|r| RECT {
                    left: r.left - origin.0 - 2,
                    top: r.top - origin.1 - 2,
                    right: r.right - origin.0 + 2,
                    bottom: r.bottom - origin.1 + 2,
                })
                .collect();
            PAINT.with(|p| p.borrow_mut().holes = holes);
        }
    };
    // B3: デスクトップ（Progman）のすぐ上にいなければ、置き直す。置き直した回数と、前面の窓の種類の変化を出す。
    let mut follows = 0u32;
    let mut last_fg = String::new();
    let mut follow = |hwnd: HWND, t: u64| {
        // SAFETY: z 順の問い合わせと自分の窓の置き直しだけ。名前は読まず、窓の種類（class）だけを見る。
        unsafe {
            let fg = class_name(GetForegroundWindow());
            if fg != last_fg {
                say!("  t={t:>3}s foreground_class={fg}");
                last_fg = fg;
            }
            let Some(pm) = progman() else { return };
            let Ok(prev) = GetWindow(pm, GW_HWNDPREV) else { return };
            if prev == hwnd {
                return;
            }
            // 自分より上で、Progman のすぐ上にいる窓の下へ。
            KEEP_BELOW.with(|k| *k.borrow_mut() = Some(prev));
            let r = SetWindowPos(hwnd, prev, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);
            follows += 1;
            say!("  t={t:>3}s FOLLOW above Progman (was below class={}) ok={}", class_name(prev), r.is_ok());
        }
    };
    if b3 {
        refresh_holes();
        let n = PAINT.with(|p| p.borrow().holes.len());
        say!("  B3 icon holes={n}");
    }
    pump_until(t0 + Duration::from_secs(3), || {});
    if cand != "none" {
        capture_check(hwnd, origin);
    }
    let cpu_after_setup = cpu_ms();
    let t_anim = Instant::now();
    pump_until(t0 + Duration::from_secs(secs), || {
        sec += 1;
        if b3 {
            follow(hwnd, sec + 3);
            if sec % 2 == 0 {
                refresh_holes();
            }
        }
        if sec % 5 == 0 {
            report(hwnd, sec + 3);
        }
    });
    if b3 {
        say!("  B3 follows={follows}");
    }
    let anim_s = t_anim.elapsed().as_secs_f64();
    let frames = PAINT.with(|p| p.borrow().frame);
    say!(
        "RESULT layer candidate={cand} frames={frames} anim_s={anim_s:.1} cpu_ms_total={:.0} cpu_pct_anim={:.2}%",
        cpu_ms() - cpu0,
        (cpu_ms() - cpu_after_setup) / (anim_s * 1000.0) * 100.0
    );
    // SAFETY: 自分の窓を壊す。
    unsafe {
        let _ = DestroyWindow(hwnd);
    }
}

// ---------------------------------------------------------------- (c) 下の縁の帯

extern "system" fn count_monitor(_: HMONITOR, _: HDC, r: *mut RECT, lp: LPARAM) -> BOOL {
    // SAFETY: EnumDisplayMonitors から渡された RECT と、呼び出し側の Vec へのポインタ。
    unsafe {
        let v = &mut *(lp.0 as *mut Vec<RECT>);
        v.push(*r);
    }
    BOOL(1)
}

fn taskbar() -> (RECT, u32, usize) {
    let mut abd = APPBARDATA {
        cbSize: std::mem::size_of::<APPBARDATA>() as u32,
        ..Default::default()
    };
    // SAFETY: タスクバーの位置と状態の問い合わせ。
    unsafe {
        let ok = SHAppBarMessage(ABM_GETTASKBARPOS, &mut abd);
        let st = SHAppBarMessage(ABM_GETSTATE, &mut abd);
        (abd.rc, abd.uEdge, (ok != 0) as usize * 2 + (st & 1))
    }
}

fn strip(secs: u64) {
    let mut mons: Vec<RECT> = Vec::new();
    // SAFETY: 画面の列挙。
    unsafe {
        let _ = EnumDisplayMonitors(
            HDC::default(),
            None,
            Some(count_monitor),
            LPARAM(&mut mons as *mut _ as isize),
        );
    }
    say!("strip monitors={}", mons.len());
    for (i, m) in mons.iter().enumerate() {
        say!("  monitor[{i}] {}", rect_s(m));
    }
    let cls = register_class();
    let place = || {
        let (mon, work) = primary_monitor();
        let (tb, edge, flags) = taskbar();
        (mon, work, tb, edge, flags)
    };
    let (mon, work, tb, edge, flags) = place();
    say!(
        "  primary={} work={} taskbar={} edge={edge} got_pos={} autohide={}",
        rect_s(&mon),
        rect_s(&work),
        rect_s(&tb),
        flags & 2 != 0,
        flags & 1 != 0
    );
    let height = 14;
    let (w, bottom) = (work.right - work.left, work.bottom);
    PAINT.with(|p| {
        *p.borrow_mut() = Paint {
            w,
            h: height,
            keyed: true,
            ..Default::default()
        }
    });
    // SAFETY: 帯の窓を作って出す。終わったら壊す。
    let hwnd = unsafe {
        let hwnd = CreateWindowExW(
            WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE | WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_TOPMOST,
            cls,
            w!("handmark spike strip"),
            WS_POPUP,
            work.left,
            bottom - height,
            w,
            height,
            HWND::default(),
            HMENU::default(),
            hinstance(),
            None,
        )
        .expect("CreateWindowExW");
        let _ = SetLayeredWindowAttributes(hwnd, KEY, 0, LWA_COLORKEY);
        let _ = ShowWindow(hwnd, SW_SHOWNOACTIVATE);
        let r = SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE);
        say!("  strip exclude_from_capture={} readback={}", r.is_ok(), affinity_s(hwnd));
        SetTimer(hwnd, 1, 16, None);
        hwnd
    };
    let cpu0 = cpu_ms();
    let t0 = Instant::now();
    let mut last = (work, tb, flags);
    let mut last_fg = String::new();
    pump_until(t0 + Duration::from_secs(secs), || {
        let (mon, work, tb, _, flags) = place();
        if (work, tb, flags) != last {
            say!(
                "  t={:>3}s CHANGED work={} taskbar={} autohide={} -> 帯を置き直す",
                t0.elapsed().as_secs(),
                rect_s(&work),
                rect_s(&tb),
                flags & 1 != 0
            );
            // SAFETY: 自分の窓の位置の更新。
            unsafe {
                let _ = SetWindowPos(
                    hwnd,
                    HWND_TOPMOST,
                    work.left,
                    work.bottom - height,
                    work.right - work.left,
                    height,
                    SWP_NOACTIVATE,
                );
            }
            last = (work, tb, flags);
        }
        // 前面の窓が主画面の全体を覆っているか（全画面のアプリ）。名前は読まない。
        // SAFETY: 前面の窓の大きさの問い合わせだけ。
        let fg = unsafe {
            let f = GetForegroundWindow();
            let mut r = RECT::default();
            let _ = GetWindowRect(f, &mut r);
            let full = r.left <= mon.left && r.top <= mon.top && r.right >= mon.right && r.bottom >= mon.bottom;
            // 帯が z 順で前面の窓より上にあるか: 帯から上へたどって前面の窓に会わなければ上。
            let mut above = true;
            let mut cur = GetWindow(hwnd, GW_HWNDPREV).ok();
            while let Some(c) = cur {
                if c == f {
                    above = false;
                    break;
                }
                cur = GetWindow(c, GW_HWNDPREV).ok();
            }
            format!("fg_fullscreen={full} strip_above_fg={above}")
        };
        if fg != last_fg {
            say!("  t={:>3}s {fg}", t0.elapsed().as_secs());
            last_fg = fg;
        }
    });
    say!(
        "RESULT strip secs={secs} cpu_pct={:.2}%",
        (cpu_ms() - cpu0) / (t0.elapsed().as_secs_f64() * 1000.0) * 100.0
    );
    // SAFETY: 自分の窓を壊す。
    unsafe {
        let _ = DestroyWindow(hwnd);
    }
}

// ---------------------------------------------------------------- B5: アイコンを模様の上に描き直す

/// 取り出したアイコン 1 つ（画面の座標の矩形と、乗算済みの BGRA の画素）。
struct IconImg {
    rect: RECT,
    px: Vec<u32>,
}

/// 32bpp・上から下の DIB を作る。
unsafe fn dib(hdc: HDC, w: i32, h: i32) -> Result<(windows::Win32::Graphics::Gdi::HBITMAP, *mut u32), String> {
    use windows::Win32::Graphics::Gdi::{CreateDIBSection, BITMAPINFO, BITMAPINFOHEADER, BI_RGB, DIB_RGB_COLORS};
    let bi = BITMAPINFO {
        bmiHeader: BITMAPINFOHEADER {
            biSize: std::mem::size_of::<BITMAPINFOHEADER>() as u32,
            biWidth: w,
            biHeight: -h,
            biPlanes: 1,
            biBitCount: 32,
            biCompression: BI_RGB.0,
            ..Default::default()
        },
        ..Default::default()
    };
    let mut bits: *mut core::ffi::c_void = std::ptr::null_mut();
    let bmp = CreateDIBSection(hdc, &bi, DIB_RGB_COLORS, &mut bits, None, 0).map_err(|e| format!("CreateDIBSection: {e}"))?;
    Ok((bmp, bits as *mut u32))
}

/// デスクトップのアイコンの一覧の窓を、黒と白の下地へ 2 回描かせ、差から色と透明度を取る。
/// 戻り値: アイコンごとの画像と、アイコンの外の点の透明度の最大（0 なら下地を塗っていない＝取り出せた）。
fn extract_icons() -> Result<(Vec<IconImg>, u8), String> {
    use windows::Win32::Storage::Xps::{PrintWindow, PRINT_WINDOW_FLAGS};
    let rects = icon_rects()?;
    let pm = progman().ok_or("Progman not found")?;
    let dv = find(pm, HWND::default(), w!("SHELLDLL_DefView")).ok_or("DefView not found")?;
    let lv = find(dv, HWND::default(), w!("SysListView32")).ok_or("SysListView32 not found")?;
    // SAFETY: 自分の DIB に、一覧の窓を描かせて読むだけ。作った GDI の物は解放する。
    unsafe {
        let mut wr = RECT::default();
        GetWindowRect(lv, &mut wr).map_err(|e| format!("GetWindowRect: {e}"))?;
        let (w, h) = (wr.right - wr.left, wr.bottom - wr.top);
        let sdc = GetDC(HWND::default());
        let mut caps: Vec<Vec<u32>> = Vec::new();
        for fill in [0x0000_0000u32, 0x00FF_FFFFu32] {
            let mdc = CreateCompatibleDC(sdc);
            let (bmp, bits) = dib(sdc, w, h)?;
            let old = SelectObject(mdc, bmp);
            let buf = std::slice::from_raw_parts_mut(bits, (w * h) as usize);
            buf.fill(fill);
            let flags: u32 = std::env::var("SPIKE_PW_FLAGS").ok().and_then(|v| v.parse().ok()).unwrap_or(0);
            let target = if std::env::var("SPIKE_PW_TARGET").as_deref() == Ok("dv") { dv } else { lv };
            let ok = PrintWindow(target, mdc, PRINT_WINDOW_FLAGS(flags)).as_bool();
            let mid = buf[((h / 2) * w + w * 3 / 4) as usize];
            if std::env::var("SPIKE_PW_DIAG").is_ok() {
                say!("    fill={fill:06X} ok={ok} sample_mid_right={mid:08X}");
                // アイコンの矩形の中の画素の透明度のバイトと色の分布（数だけ）。
                let (mut a0c0, mut a0c, mut aff, mut apart) = (0u64, 0u64, 0u64, 0u64);
                for r in &rects {
                    for y in (r.top - wr.top).max(0)..(r.bottom - wr.top).min(h) {
                        for x in (r.left - wr.left).max(0)..(r.right - wr.left).min(w) {
                            let v = buf[(y * w + x) as usize];
                            let a = v >> 24;
                            let c = v & 0xFFFFFF;
                            if a == 0 && c == 0 { a0c0 += 1 } else if a == 0 { a0c += 1 } else if a == 255 { aff += 1 } else { apart += 1 }
                        }
                    }
                }
                say!("    icons-area: alpha0_black={a0c0} alpha0_color={a0c} alpha255={aff} alpha_partial={apart}");
            }
            caps.push(buf.to_vec());
            SelectObject(mdc, old);
            let _ = DeleteObject(bmp);
            let _ = DeleteDC(mdc);
            if !ok {
                ReleaseDC(HWND::default(), sdc);
                return Err("PrintWindow failed".into());
            }
        }
        ReleaseDC(HWND::default(), sdc);
        // フラグ 0 の PrintWindow は、透明な下地（透明度 0）の上にアイコンだけを、透明度つきで描く（2026-11-19 に実測）。
        // 1 回目（黒の下地）の画像をそのまま乗算済みの BGRA として使う。各チャンネルは透明度を超えないように切る。
        let b = &caps[0];
        let alpha_at = |i: usize| -> (u8, u32) {
            let v = b[i];
            let a = v >> 24;
            let mut c = 0u32;
            for s in [0, 8, 16] {
                c |= ((v >> s) & 0xFF).min(a) << s;
            }
            (a as u8, (a << 24) | c)
        };
        // アイコンの外の点（画面の右半分の格子）で、下地が残っているか。
        let mut outside_max = 0u8;
        for y in (h / 10..h).step_by((h / 10).max(1) as usize) {
            for x in (w / 2..w).step_by((w / 20).max(1) as usize) {
                let inside = rects.iter().any(|r| x + wr.left >= r.left && x + wr.left < r.right && y + wr.top >= r.top && y + wr.top < r.bottom);
                if !inside {
                    outside_max = outside_max.max(alpha_at((y * w + x) as usize).0);
                }
            }
        }
        let mut out = Vec::new();
        for r in rects {
            let (rw, rh) = (r.right - r.left, r.bottom - r.top);
            let mut px = Vec::with_capacity((rw * rh) as usize);
            for yy in 0..rh {
                for xx in 0..rw {
                    let (x, y) = (r.left - wr.left + xx, r.top - wr.top + yy);
                    px.push(if x >= 0 && y >= 0 && x < w && y < h { alpha_at((y * w + x) as usize).1 } else { 0 });
                }
            }
            out.push(IconImg { rect: r, px });
        }
        Ok((out, outside_max))
    }
}

fn iconsnap() {
    let t = Instant::now();
    match extract_icons() {
        Ok((v, outside)) => {
            let (mut opaque, mut partial, mut total) = (0u64, 0u64, 0u64);
            for i in &v {
                for p in &i.px {
                    let a = p >> 24;
                    total += 1;
                    if a >= 250 {
                        opaque += 1;
                    } else if a > 5 {
                        partial += 1;
                    }
                }
            }
            say!(
                "iconsnap icons={} pixels={total} opaque={:.1}% partial={:.1}% outside_alpha_max={outside} ms={}",
                v.len(),
                opaque as f64 * 100.0 / total.max(1) as f64,
                partial as f64 * 100.0 / total.max(1) as f64,
                t.elapsed().as_millis()
            );
        }
        Err(e) => say!("iconsnap FAIL {e}"),
    }
}

/// 最初の「見える」窓を Progman の上へたどる。見えない窓（IME など）は飛ばす。
unsafe fn first_visible_above_progman(pm: HWND) -> Option<HWND> {
    let mut cur = GetWindow(pm, GW_HWNDPREV).ok();
    while let Some(c) = cur {
        if IsWindowVisible(c).as_bool() {
            return Some(c);
        }
        cur = GetWindow(c, GW_HWNDPREV).ok();
    }
    None
}

fn b5(secs: u64) {
    use windows::Win32::Foundation::SIZE;
    use windows::Win32::Graphics::Gdi::{AC_SRC_ALPHA, AC_SRC_OVER, BLENDFUNCTION};
    let cls = register_class();
    let icons_all = std::env::var("SPIKE_ICONS_ALL").is_ok();
    say!("b5 icons_all={icons_all}");
    let (mon, _) = primary_monitor();
    let (w, h) = (mon.right - mon.left, mon.bottom - mon.top);
    say!("b5 primary={}", rect_s(&mon));
    // SAFETY: 窓・DIB を作り、毎コマ UpdateLayeredWindow で出す。終わったら壊す。
    unsafe {
        let hwnd = CreateWindowExW(
            WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE | WS_EX_TRANSPARENT | WS_EX_LAYERED,
            cls,
            w!("handmark spike B5"),
            WS_POPUP,
            mon.left,
            mon.top,
            w,
            h,
            HWND::default(),
            HMENU::default(),
            hinstance(),
            None,
        )
        .expect("CreateWindowExW");
        let sdc = GetDC(HWND::default());
        let mdc = CreateCompatibleDC(sdc);
        let (bmp, bits) = dib(sdc, w, h).expect("dib");
        let old = SelectObject(mdc, bmp);
        let buf = std::slice::from_raw_parts_mut(bits, (w * h) as usize);
        let present = |hwnd: HWND| {
            let blend = BLENDFUNCTION {
                BlendOp: AC_SRC_OVER as u8,
                BlendFlags: 0,
                SourceConstantAlpha: 255,
                AlphaFormat: AC_SRC_ALPHA as u8,
            };
            let pos = POINT { x: mon.left, y: mon.top };
            let size = SIZE { cx: w, cy: h };
            let src = POINT { x: 0, y: 0 };
            UpdateLayeredWindow(hwnd, sdc, Some(&pos), Some(&size), mdc, Some(&src), COLORREF(0), Some(&blend), ULW_ALPHA)
        };
        buf.fill(0);
        let r = present(hwnd);
        say!("  first UpdateLayeredWindow ok={}", r.is_ok());
        let _ = ShowWindow(hwnd, SW_SHOWNOACTIVATE);
        let aff = SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE);
        say!("  exclude_from_capture={} readback={}", aff.is_ok(), affinity_s(hwnd));

        let mut icons: Vec<IconImg> = Vec::new();
        let refresh = |icons: &mut Vec<IconImg>| match extract_icons() {
            Ok((v, _)) => *icons = v,
            Err(e) => say!("  extract FAIL {e}"),
        };
        refresh(&mut icons);
        say!("  icons={}", icons.len());

        let orange: u32 = 0xFFFF_8000;
        let t0 = Instant::now();
        let cpu0 = cpu_ms();
        let mut frame: u64 = 0;
        let mut last_sec = 0u64;
        let mut follows = 0u32;
        let mut msg = MSG::default();
        let mut extract_ms_max = 0u128;
        while t0.elapsed() < Duration::from_secs(secs) {
            while PeekMessageW(&mut msg, HWND::default(), 0, 0, PM_REMOVE).as_bool() {
                let _ = TranslateMessage(&msg);
                DispatchMessageW(&msg);
            }
            frame += 1;
            // 模様: 横に動く 80x80 の四角と、縦に流れる高さ 4 の帯（試作の他の候補と同じ）。
            buf.fill(0);
            let span = (w - 80).max(1) as u64;
            let x0 = (frame * 6 % span) as i32;
            let y0 = h / 3;
            let yy = (frame * 3 % h.max(1) as u64) as i32;
            let mut fill_rect = |l: i32, t: i32, r: i32, b: i32| {
                for y in t.max(0)..b.min(h) {
                    let row = (y * w) as usize;
                    buf[row + l.max(0) as usize..row + r.min(w) as usize].fill(orange);
                }
            };
            fill_rect(x0, y0, x0 + 80, y0 + 80);
            fill_rect(0, yy, w, yy + 4);
            // アイコン: 模様のある画素にだけ、アイコンを上から重ねる（模様の無い所は透明のまま）。
            for ic in &icons {
                let r = ic.rect;
                let (rw, rh) = (r.right - r.left, r.bottom - r.top);
                for iy in 0..rh {
                    let y = r.top - mon.top + iy;
                    if y < 0 || y >= h {
                        continue;
                    }
                    for ix in 0..rw {
                        let x = r.left - mon.left + ix;
                        if x < 0 || x >= w {
                            continue;
                        }
                        let d = &mut buf[(y * w + x) as usize];
                        // SPIKE_ICONS_ALL: 本番の形（アイコンの窓を別に重ねる）を真似て、模様の無い所にも写しを重ねる。
                        if *d == 0 && !icons_all {
                            continue;
                        }
                        let s = ic.px[(iy * rw + ix) as usize];
                        let sa = s >> 24;
                        if sa == 0 {
                            continue;
                        }
                        let inv = 255 - sa;
                        let mut o = 0u32;
                        for sh in [0, 8, 16, 24] {
                            let sc = (s >> sh) & 0xFF;
                            let dc = (*d >> sh) & 0xFF;
                            o |= ((sc + dc * inv / 255).min(255)) << sh;
                        }
                        *d = o;
                    }
                }
            }
            let _ = present(hwnd);
            let sec = t0.elapsed().as_secs();
            // デスクトップのすぐ上にいなければ置き直す（見えない窓は飛ばす）。毎コマ見る
            // （1 秒ごとだと、デスクトップのクリックや Win+D のたびに 1 秒消える）。
            if let Some(pm) = progman() {
                if first_visible_above_progman(pm) != Some(hwnd) {
                    if let Ok(prev) = GetWindow(pm, GW_HWNDPREV) {
                        if prev != hwnd {
                            let _ = SetWindowPos(hwnd, prev, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);
                            follows += 1;
                            say!("  t={sec:>3}s FOLLOW (foreground_class={})", class_name(GetForegroundWindow()));
                        }
                    }
                }
            }
            if sec != last_sec {
                last_sec = sec;
                if sec % 2 == 0 {
                    let te = Instant::now();
                    refresh(&mut icons);
                    extract_ms_max = extract_ms_max.max(te.elapsed().as_millis());
                }
            }
            std::thread::sleep(Duration::from_millis(16));
        }
        let wall = t0.elapsed().as_secs_f64();
        say!(
            "RESULT b5 frames={frame} fps={:.1} follows={follows} extract_ms_max={extract_ms_max} cpu_pct={:.2}%",
            frame as f64 / wall,
            (cpu_ms() - cpu0) / (wall * 1000.0) * 100.0
        );
        SelectObject(mdc, old);
        let _ = DeleteObject(bmp);
        let _ = DeleteDC(mdc);
        ReleaseDC(HWND::default(), sdc);
        let _ = DestroyWindow(hwnd);
    }
}

// ---------------------------------------------------------------- main

fn main() {
    // SAFETY: プロセスの DPI の扱いを 1 回だけ設定する。
    let dpi = unsafe { SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2) };
    let args: Vec<String> = std::env::args().collect();
    let secs = |i: usize, d: u64| args.get(i).and_then(|s| s.parse().ok()).unwrap_or(d);
    say!("dpi_aware_v2={}", dpi.is_ok());
    match args.get(1).map(String::as_str) {
        Some("probe-pointer") => probe_pointer(args.get(2).map(String::as_str).unwrap_or("-"), secs(3, 60)),
        Some("layer") => layer(args.get(2).map(String::as_str).unwrap_or("none"), secs(3, 60)),
        Some("strip") => strip(secs(2, 60)),
        Some("tree") => tree(),
        Some("icons") => icons_report(),
        Some("iconsnap") => iconsnap(),
        Some("b5") => b5(secs(2, 60)),
        Some("b5all") => {
            std::env::set_var("SPIKE_ICONS_ALL", "1");
            b5(secs(2, 60))
        }
        _ => say!("usage: spike probe-pointer <label> [secs] | layer <W|WL|B1|B2|T|none> [secs] | strip [secs] | tree"),
    }
}
