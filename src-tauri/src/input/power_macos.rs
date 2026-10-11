//! macOS のスリープの通知（`NSWorkspaceWillSleepNotification` / `NSWorkspaceDidWakeNotification`）。
//!
//! `observe_macos.rs` のフォーカスの通知と同じ作法: 背景の `NSOperationQueue` で受け、ブロックの中は
//! `try_send` だけ。観測の寿命ぶん解放しない（意図的な forget）。

use std::ptr::NonNull;

use block2::RcBlock;
use objc2_app_kit::{
    NSWorkspace, NSWorkspaceDidWakeNotification, NSWorkspaceWillSleepNotification,
};
use objc2_foundation::{NSNotification, NSOperationQueue};

use super::{PowerEvent, POWER_TX};

fn observe(name: &'static objc2_foundation::NSString, ev: PowerEvent) {
    let workspace = NSWorkspace::sharedWorkspace();
    let center = workspace.notificationCenter();
    let queue = NSOperationQueue::new();
    let block: RcBlock<dyn Fn(NonNull<NSNotification>)> =
        RcBlock::new(move |_n: NonNull<NSNotification>| {
            if let Some(tx) = POWER_TX.get() {
                let _ = tx.try_send(ev);
            }
        });
    // SAFETY: ブロックが捕捉するのは Copy の列挙値だけで、任意のスレッドで何度呼ばれても安全。
    // 背景のキューを渡しているので、通知をポストする OS 側のスレッドを塞がない。
    let token = unsafe {
        center.addObserverForName_object_queue_usingBlock(Some(name), None, Some(&queue), &block)
    };
    std::mem::forget(workspace);
    std::mem::forget(center);
    std::mem::forget(queue);
    std::mem::forget(block);
    std::mem::forget(token);
}

pub fn start() {
    // SAFETY: AppKit が定義する通知名の定数（extern static）を読むだけ。
    let (sleep, wake) = unsafe {
        (
            NSWorkspaceWillSleepNotification,
            NSWorkspaceDidWakeNotification,
        )
    };
    observe(sleep, PowerEvent::Suspending);
    observe(wake, PowerEvent::Resumed);
}
