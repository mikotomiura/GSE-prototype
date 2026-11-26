//! 手跡の「ほかの窓をどける」の Windows の部分（handmark-reveal-count 判断 3・4）。
//!
//! どける: `EnumWindows`（上から下の重なり順）で、見えている他のアプリのトップレベルの窓を覚え
//! （判定は `handmark_reveal::is_windows_candidate`）、`ShowWindowAsync(SW_SHOWMINNOACTIVE)` で最小化する
//! （応答しないアプリで止まらないよう非同期）。管理者として動く窓は最小化できないことがあり、その窓は残る。
//! 戻す: 下から上の順に、まだ在り、覚えたときと同じプロセスの窓で、最小化されたままの窓だけ
//! `ShowWindowAsync(SW_RESTORE)`（非同期なので元の重なりは近づけるだけで、保証はしない）。
//!
//! 覚えた窓のハンドルと pid は記録・tracing に出さない。窓の題名は読まない（クラス名はシェルの窓を見分けるためだけに読む）。

use std::sync::Mutex;

use windows::Win32::Foundation::{BOOL, HWND, LPARAM};
use windows::Win32::Graphics::Dwm::{DwmGetWindowAttribute, DWMWA_CLOAKED};
use windows::Win32::System::Threading::GetCurrentProcessId;
use windows::Win32::UI::WindowsAndMessaging::{
    EnumWindows, GetClassNameW, GetWindow, GetWindowLongPtrW, GetWindowThreadProcessId, IsIconic,
    IsWindow, IsWindowVisible, ShowWindowAsync, GWL_EXSTYLE, GW_OWNER, SW_RESTORE,
    SW_SHOWMINNOACTIVE, WS_EX_APPWINDOW, WS_EX_TOOLWINDOW,
};

use crate::handmark_reveal::{
    is_shell_class, is_windows_candidate, restore_order, should_restore_window, WinWindow,
};

/// どけたときに覚えた窓（ハンドルと、その窓のプロセスの ID）。上から下の順・メモリだけ。
static REMEMBERED: Mutex<Vec<(isize, u32)>> = Mutex::new(Vec::new());

fn remembered() -> std::sync::MutexGuard<'static, Vec<(isize, u32)>> {
    REMEMBERED.lock().unwrap_or_else(|p| p.into_inner())
}

/// どける（`true`）・戻す（`false`）。どの thread からでも呼べる（非同期の `ShowWindowAsync` だけを使う）。
pub fn apply(reveal: bool) {
    if reveal {
        reveal_now();
    } else {
        restore_now();
    }
}

fn reveal_now() {
    let found = visible_other_windows();
    for (h, _) in &found {
        // SAFETY: 列挙で得たトップレベルの窓のハンドル。閉じられていても ShowWindowAsync は失敗を返すだけ。
        let _ = unsafe { ShowWindowAsync(HWND(*h as _), SW_SHOWMINNOACTIVE) };
    }
    let mut g = remembered();
    // 戻す前に 2 回どけた（駆動役は交互にしか出さないが念のため）: 前に覚えたものを捨てない
    for w in found {
        if !g.contains(&w) {
            g.push(w);
        }
    }
}

fn restore_now() {
    let list = std::mem::take(&mut *remembered());
    for (h, pid) in restore_order(&list) {
        let hwnd = HWND(h as _);
        // SAFETY: IsWindow は読むだけの照会で、閉じた窓のハンドルにも偽を返す。
        let exists = unsafe { IsWindow(hwnd) }.as_bool();
        let same_process = exists && process_of(hwnd) == pid;
        // SAFETY: IsIconic は読むだけの照会。
        let minimized = exists && unsafe { IsIconic(hwnd) }.as_bool();
        if should_restore_window(exists, same_process, minimized) {
            // SAFETY: まだ在る窓。非同期なので応答しないアプリでも止まらない。
            let _ = unsafe { ShowWindowAsync(hwnd, SW_RESTORE) };
        }
    }
}

/// 窓のプロセスの ID（取れなければ 0）。
fn process_of(hwnd: HWND) -> u32 {
    let mut pid: u32 = 0;
    // SAFETY: 読むだけの照会。出力先はこの関数のスタックの u32。
    let _ = unsafe { GetWindowThreadProcessId(hwnd, Some(&mut pid)) };
    pid
}

/// 見えている他のアプリのトップレベルの窓（上から下の順・ハンドルとプロセスの ID）。
fn visible_other_windows() -> Vec<(isize, u32)> {
    struct Collect {
        me: u32,
        out: Vec<(isize, u32)>,
    }
    unsafe extern "system" fn callback(hwnd: HWND, lparam: LPARAM) -> BOOL {
        // SAFETY: lparam は呼び出し側のスタックにある `Collect` を指し、同期の EnumWindows の間だけ生きていて、
        // その間ほかに触る者はいない。
        let c = unsafe { &mut *(lparam.0 as *mut Collect) };
        let (attrs, pid) = attributes(hwnd, c.me);
        if is_windows_candidate(&attrs) {
            c.out.push((hwnd.0 as isize, pid));
        }
        BOOL(1)
    }
    // SAFETY: 自プロセスの ID を読むだけ。
    let me = unsafe { GetCurrentProcessId() };
    let mut c = Collect {
        me,
        out: Vec::new(),
    };
    // SAFETY: コールバックは `Collect` への生ポインタだけを使い、列挙が終わるまで `c` は動かない。
    let r = unsafe { EnumWindows(Some(callback), LPARAM(&mut c as *mut Collect as isize)) };
    if r.is_err() {
        tracing::warn!("handmark: reveal could not list the windows");
    }
    c.out
}

/// 1 枚の窓の属性（真偽だけ）とプロセスの ID。題名は読まない。`hwnd` は `EnumWindows` が渡したハンドル。
fn attributes(hwnd: HWND, me: u32) -> (WinWindow, u32) {
    let mut cloaked: u32 = 0;
    // SAFETY: 読むだけの照会。出力先はこのスタックの u32 で、大きさを正しく渡す。
    let cloaked_ok = unsafe {
        DwmGetWindowAttribute(
            hwnd,
            DWMWA_CLOAKED,
            (&mut cloaked as *mut u32).cast(),
            std::mem::size_of::<u32>() as u32,
        )
    }
    .is_ok();
    // SAFETY: 読むだけの照会。
    let has_owner = unsafe { GetWindow(hwnd, GW_OWNER) }
        .ok()
        .is_some_and(|h| !h.is_invalid());
    // SAFETY: 読むだけの照会（配布は x64 なので Ptr 版を使う・lib.rs の既存の使い方と同じ）。
    let ex = unsafe { GetWindowLongPtrW(hwnd, GWL_EXSTYLE) } as u32;
    let pid = process_of(hwnd);
    let mut buf = [0u16; 64];
    // SAFETY: 読むだけの照会。書き込み先はこのスタックの配列で、長さは slice から渡る。
    let n = unsafe { GetClassNameW(hwnd, &mut buf) };
    let class = String::from_utf16_lossy(&buf[..usize::try_from(n).unwrap_or(0)]);
    // SAFETY: 読むだけの照会。
    let (visible, minimized) =
        unsafe { (IsWindowVisible(hwnd).as_bool(), IsIconic(hwnd).as_bool()) };
    (
        WinWindow {
            visible,
            minimized,
            cloaked: cloaked_ok && cloaked != 0,
            has_owner,
            tool_window: ex & WS_EX_TOOLWINDOW.0 != 0,
            app_window: ex & WS_EX_APPWINDOW.0 != 0,
            own_process: pid == me,
            shell_class: is_shell_class(&class),
        },
        pid,
    )
}
