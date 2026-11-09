//! 手跡のポインタの一点を macOS から読む（ADR-050 D2・ADR-051）。
//!
//! いまの一点（位置と左の押下）だけを読む。フックもイベントの tap も使わず、権限も要らない。
//! キーボードの状態は読まない。objc2-app-kit 0.3.2 の `NSEvent::mouseLocation`・
//! `NSEvent::pressedMouseButtons` はどちらも safe の関数で、`MainThreadMarker` を要求しない宣言
//! （クラスメソッド・`extern_methods!` の `unsafe(method(..))` で `MainThreadOnly` の指定が無い）。
//! したがって手跡のポインタのスレッド（メインスレッドでない）から呼んでよい。

use super::handmark_pointer::PointerSample;
use objc2_app_kit::NSEvent;

/// 左のボタン（`pressedMouseButtons` の最下位のビット）。
const LEFT_BUTTON: usize = 1;

/// 一点を 1 回読む。
pub fn read() -> PointerSample {
    let p = NSEvent::mouseLocation();
    let buttons = NSEvent::pressedMouseButtons();
    PointerSample::new(p.x, p.y, buttons & LEFT_BUTTON != 0)
}
