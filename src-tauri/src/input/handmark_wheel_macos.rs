//! 手跡の背景の層の表現の入力: ホイール（macOS だけ・spike・ADR-040 D7・判断 9）。
//!
//! - ホイールだけを聞く tap（聞くだけ）を、O1 の `observe_macos.rs` の tap とは別のファイル・別のスレッドで持つ。
//!   macOS ではホイールに繰り返し読む方法がなく、入力監視の許可と tap が要る（results.md §4 の実測）。
//! - 持つのは、前に読まれてからの回した量の和 1 つだけ（列を作らない）。位置も時刻も読まない。
//! - 入れている間だけスレッドと tap を作る。切ったら tap ごとスレッドを終え、溜まった量を捨てる（D4）。
//! - 検査は `crate::handmark_stage_guard`。

use core_foundation::runloop::{kCFRunLoopDefaultMode, CFRunLoop};
use core_graphics::event::{
    CGEvent, CGEventTap, CGEventTapLocation, CGEventTapOptions, CGEventTapPlacement, CGEventType,
    EventField,
};
use std::sync::atomic::{AtomicBool, AtomicI64, Ordering};
use std::time::{Duration, Instant};

/// 前に読まれてから回した量（1 回ぶんを 1000）。
static AMOUNT_MILLI: AtomicI64 = AtomicI64::new(0);
/// tap のスレッドが動いているか。
static RUNNING: AtomicBool = AtomicBool::new(false);
/// OS が tap を無効にした（スレッドの側で有効に戻す）。
static DISABLED: AtomicBool = AtomicBool::new(false);
/// 最後に tap を作れなかった時刻（作り直しを詰めて試さない）。
static LAST_FAILURE: std::sync::Mutex<Option<Instant>> = std::sync::Mutex::new(None);

const RETRY_AFTER: Duration = Duration::from_secs(5);

/// 1 回の通知の量を、見本と同じ 1 回ぶんの単位にする（画面を下へ送る向きを正）。
/// 連続の装置（トラックパッド）は画素の量を 100 で 1 回ぶんにして ±1 で頭打ち。刻みの装置は 1 回ぶん。
fn amount(event: &CGEvent) -> f64 {
    let continuous =
        event.get_integer_value_field(EventField::SCROLL_WHEEL_EVENT_IS_CONTINUOUS) != 0;
    if continuous {
        let px = event.get_double_value_field(EventField::SCROLL_WHEEL_EVENT_POINT_DELTA_AXIS_1);
        (-px / 100.0).clamp(-1.0, 1.0)
    } else {
        let lines = event.get_integer_value_field(EventField::SCROLL_WHEEL_EVENT_DELTA_AXIS_1);
        -(lines.signum() as f64)
    }
}

/// tap の通知。数を足すだけ（ブロックしない・ログを出さない）。
fn on_event(event_type: CGEventType, event: &CGEvent) {
    if matches!(
        event_type,
        CGEventType::TapDisabledByTimeout | CGEventType::TapDisabledByUserInput
    ) {
        DISABLED.store(true, Ordering::Release);
        return;
    }
    if matches!(event_type, CGEventType::ScrollWheel) {
        AMOUNT_MILLI.fetch_add((amount(event) * 1_000.0) as i64, Ordering::Relaxed);
    }
}

/// 前に読まれてから回した量を返し、0 に戻す。
pub fn take() -> f64 {
    AMOUNT_MILLI.swap(0, Ordering::AcqRel) as f64 / 1_000.0
}

/// 切ったときに呼ぶ。溜まった量を捨てる。
pub fn discard() {
    AMOUNT_MILLI.store(0, Ordering::Release);
}

/// `wanted` が true を返す間だけ動く tap のスレッドを、動いていなければ起こす。
/// 作れなかったときは 5 秒あけてから試す。
pub fn ensure_running(wanted: fn() -> bool) {
    if RUNNING.load(Ordering::Acquire) {
        return;
    }
    if let Ok(last) = LAST_FAILURE.lock() {
        if last.is_some_and(|t| t.elapsed() < RETRY_AFTER) {
            return;
        }
    }
    if RUNNING.swap(true, Ordering::AcqRel) {
        return;
    }
    let spawned = std::thread::Builder::new()
        .name("gse-handmark-wheel".to_string())
        .spawn(move || {
            run(wanted);
            discard();
            RUNNING.store(false, Ordering::Release);
        });
    if spawned.is_err() {
        RUNNING.store(false, Ordering::Release);
        note_failure();
    }
}

fn note_failure() {
    if let Ok(mut last) = LAST_FAILURE.lock() {
        *last = Some(Instant::now());
    }
}

fn run(wanted: fn() -> bool) {
    let run_loop = CFRunLoop::get_current();
    let tap = CGEventTap::new(
        CGEventTapLocation::Session,
        CGEventTapPlacement::HeadInsertEventTap,
        CGEventTapOptions::ListenOnly,
        vec![CGEventType::ScrollWheel],
        |_proxy, event_type, event| {
            on_event(event_type, event);
            None
        },
    );
    let Ok(tap) = tap else {
        note_failure();
        return;
    };
    let Ok(source) = tap.mach_port.create_runloop_source(0) else {
        note_failure();
        return;
    };
    // SAFETY: `kCFRunLoopDefaultMode` は CoreFoundation の定数で、常に有効。
    run_loop.add_source(&source, unsafe { kCFRunLoopDefaultMode });
    tap.enable();
    DISABLED.store(false, Ordering::Release);
    while wanted() {
        if DISABLED.swap(false, Ordering::AcqRel) {
            tap.enable();
        }
        CFRunLoop::run_in_mode(
            // SAFETY: 同上。
            unsafe { kCFRunLoopDefaultMode },
            Duration::from_millis(100),
            false,
        );
    }
    // スレッドを抜けると tap と run loop の source が捨てられ、取得が止まる。
}
