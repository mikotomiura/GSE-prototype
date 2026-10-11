//! Windows のスリープの通知（`RegisterSuspendResumeNotification`・`DEVICE_NOTIFY_CALLBACK`）。
//!
//! 窓を作らずにコールバックで受ける。コールバックの中は `try_send` だけ（`hook-constraints`）。

use windows::Win32::Foundation::HANDLE;
use windows::Win32::System::Power::{
    RegisterSuspendResumeNotification, DEVICE_NOTIFY_SUBSCRIBE_PARAMETERS,
};
use windows::Win32::UI::WindowsAndMessaging::{
    DEVICE_NOTIFY_CALLBACK, PBT_APMRESUMEAUTOMATIC, PBT_APMSUSPEND,
};

use super::{PowerEvent, POWER_TX};

/// 電源の通知のコールバック。
///
/// ⚠️ ログを書かない・ロックを取らない（`try_send` だけ）。
unsafe extern "system" fn power_callback(
    _context: *const core::ffi::c_void,
    kind: u32,
    _setting: *const core::ffi::c_void,
) -> u32 {
    let ev = match kind {
        PBT_APMSUSPEND => Some(PowerEvent::Suspending),
        PBT_APMRESUMEAUTOMATIC => Some(PowerEvent::Resumed),
        _ => None,
    };
    if let (Some(ev), Some(tx)) = (ev, POWER_TX.get()) {
        let _ = tx.try_send(ev);
    }
    0 // ERROR_SUCCESS
}

pub fn start() {
    // 引数の構造体は登録の間ずっと生きている必要があるので、プロセスの寿命ぶん漏らす（意図的）。
    let params: &'static mut DEVICE_NOTIFY_SUBSCRIBE_PARAMETERS =
        Box::leak(Box::new(DEVICE_NOTIFY_SUBSCRIBE_PARAMETERS {
            Callback: Some(power_callback),
            Context: std::ptr::null_mut(),
        }));
    // SAFETY: DEVICE_NOTIFY_CALLBACK のとき、受け手は DEVICE_NOTIFY_SUBSCRIBE_PARAMETERS へのポインタ。
    // 構造体は漏らしてあるので、登録が生きている間ずっと有効である。
    let r = unsafe {
        RegisterSuspendResumeNotification(
            HANDLE(params as *mut DEVICE_NOTIFY_SUBSCRIBE_PARAMETERS as *mut core::ffi::c_void),
            DEVICE_NOTIFY_CALLBACK,
        )
    };
    if let Err(e) = r {
        tracing::warn!("EH3: suspend notification could not be registered: {e}");
    }
}
