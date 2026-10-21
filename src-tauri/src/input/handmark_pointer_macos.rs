//! 手跡の背景の層の表現の入力を macOS から読む（spike・ADR-040 D6）。
//!
//! いまの一点だけを読む。フックもイベントの tap も使わず、権限も要らない
//! （枝 `docs/tangibility-design` の `.steering/20261020-handmark-multi-input/design.md` §1・§2 の実測）。
//! キーボードの状態は読まない。objc2-app-kit 0.3 ではどちらも safe でメインスレッドを要らない宣言。

use super::handmark_pointer::PointerSample;
use objc2_app_kit::NSEvent;

/// 左のボタン（`pressedMouseButtons` の最下位のビット・判断 6）。
const LEFT_BUTTON: usize = 1;

pub fn read() -> PointerSample {
    let p = NSEvent::mouseLocation();
    let buttons = NSEvent::pressedMouseButtons();
    PointerSample::new(p.x, p.y, buttons & LEFT_BUTTON != 0)
}
