//! 手跡のポインタの一点を Windows から読む（ADR-050 D2・D3・ADR-051）。
//!
//! いまの一点（位置と左の押下）だけを読む。フックも Raw Input も使わず、権限も要らない
//! （2026-11-19 の確かめ・`.steering/20261119-handmark-windows/results.md` §1）。
//! `GetAsyncKeyState` に渡す仮想キーは `VK_LBUTTON` だけで、キーボードの仮想キーは渡さない
//! （ADR-050 D3・`handmark_guard.rs` が縛る）。返り値の最上位ビット（いま押されている）だけを見て、
//! 最下位ビット（前回の呼び出しから押された）は使わない（起動直後に立つことがあり、他のプロセスとも共有される）。
//! 昇格した窓が前面の間は押下が読めない（UIPI）。表現の入力の取りこぼしは許す（ADR-050 D6）。

use super::handmark_pointer::{from_top_left, PointerSample};
use windows::Win32::Foundation::POINT;
use windows::Win32::UI::Input::KeyboardAndMouse::{GetAsyncKeyState, VK_LBUTTON};
use windows::Win32::UI::WindowsAndMessaging::GetCursorPos;

/// 一点を 1 回読む。`screen_h` は主画面の高さ（物理ピクセル）。位置を読めなければ（安全なデスクトップの間など）`None`。
pub fn read(screen_h: f64) -> Option<PointerSample> {
    let mut p = POINT::default();
    // SAFETY: `p` はこの関数の中の有効な書き込み先で、GetCursorPos はそこに書くだけ。
    unsafe { GetCursorPos(&mut p) }.ok()?;
    // SAFETY: 引数は定数の仮想キー（マウスの左ボタン）で、副作用の無い問い合わせ。
    let state = unsafe { GetAsyncKeyState(i32::from(VK_LBUTTON.0)) };
    let left_down = (state as u16) & 0x8000 != 0;
    Some(from_top_left(
        f64::from(p.x),
        f64::from(p.y),
        screen_h,
        left_down,
    ))
}
