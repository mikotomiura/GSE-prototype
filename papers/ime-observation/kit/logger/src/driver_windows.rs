//! Windows driver of the standalone logger: the low-level keyboard hook and the input-method window
//! events.
//!
//! One thread installs both hooks and pumps its message queue, which the operating system requires
//! before it delivers low-level hook calls and out-of-context WinEvent notifications. The thread
//! polls the queue and the stop flag, so it ends well within the stop deadline of the driver
//! contract. No code is injected into another process, and no callback argument carries text.
//!
//! Start-up is synchronous: `start` returns only after the hooks are installed, and reports a failed
//! installation as an error instead of running silently without observing.
//!
//! Known limits. A hook that the operating system removes after installation is not re-installed:
//! the thread stays alive and the log then contains no key rows, which is indistinguishable from an
//! idle session. Timestamps are taken when a callback runs, and a callback runs when the thread next
//! polls its queue, so a timestamp can trail the physical event by up to the polling interval.

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::mpsc::{sync_channel, RecvTimeoutError, SyncSender};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use windows::Win32::Foundation::HINSTANCE;
use windows::Win32::System::LibraryLoader::GetModuleHandleW;
use windows::Win32::UI::WindowsAndMessaging::{
    DispatchMessageW, PeekMessageW, MSG, PM_NOREMOVE, PM_REMOVE, WM_QUIT,
};

use crate::driver_api::{DriverCtx, DriverHandle};

mod ime_winevent;
mod keyboard;

/// Upper bound on the wait for the hook thread to report the result of the installation.
const START_TIMEOUT: Duration = Duration::from_secs(5);
/// Sleep between two empty polls of the message queue.
const IDLE_SLEEP: Duration = Duration::from_millis(1);

/// Wall-clock time in milliseconds since the Unix epoch.
fn wall_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}

pub fn start(ctx: DriverCtx) -> Result<DriverHandle, String> {
    keyboard::set_sender(ctx.keys)?;
    let stop = Arc::clone(&ctx.stop);
    let (ack_tx, ack_rx) = sync_channel::<Result<(), String>>(1);
    let thread = thread::Builder::new()
        .name("ime-observation-driver".to_string())
        .spawn(move || hook_thread(&stop, &ack_tx))
        .map_err(|e| format!("cannot spawn the hook thread: {e}"))?;
    match ack_rx.recv_timeout(START_TIMEOUT) {
        Ok(Ok(())) => Ok(DriverHandle::new(thread)),
        Ok(Err(e)) => {
            let _ = thread.join();
            Err(e)
        }
        Err(RecvTimeoutError::Timeout) => {
            ctx.stop.store(true, Ordering::Release);
            Err("the hook thread did not report its start within 5 seconds".to_string())
        }
        Err(RecvTimeoutError::Disconnected) => {
            let _ = thread.join();
            Err("the hook thread ended before reporting its start".to_string())
        }
    }
}

/// Body of the hook thread: install, report, pump until stopped, uninstall.
fn hook_thread(stop: &AtomicBool, ack: &SyncSender<Result<(), String>>) {
    // SAFETY: `PeekMessageW` with a default `MSG` only creates the message queue of this thread,
    // which a low-level hook requires before it is installed.
    unsafe {
        let mut msg = MSG::default();
        let _ = PeekMessageW(&mut msg, None, 0, 0, PM_NOREMOVE);
    }
    let keyboard_hook = match keyboard::install(module_handle()) {
        Ok(h) => h,
        Err(e) => {
            let _ = ack.send(Err(e));
            return;
        }
    };
    let ime_hook = match ime_winevent::install() {
        Ok(h) => h,
        Err(e) => {
            keyboard::uninstall(keyboard_hook);
            let _ = ack.send(Err(e));
            return;
        }
    };
    tracing::info!("keyboard and input-method window hooks installed");
    let _ = ack.send(Ok(()));

    pump_until_stopped(stop);

    ime_winevent::uninstall(ime_hook);
    keyboard::uninstall(keyboard_hook);
}

/// Handle of the current executable module. A null instance is accepted by the call but is not used,
/// because some Windows 11 configurations then leave the hook without callbacks.
fn module_handle() -> HINSTANCE {
    // SAFETY: `GetModuleHandleW(None)` returns the handle of the calling process's executable.
    match unsafe { GetModuleHandleW(None) } {
        Ok(h) => HINSTANCE(h.0),
        Err(e) => {
            tracing::warn!("GetModuleHandleW failed ({e:?}); using a null instance");
            HINSTANCE::default()
        }
    }
}

/// Dispatches queued messages until the stop flag is raised or a quit message arrives. The queue is
/// polled rather than waited on, which keeps the hook callbacks and the stop flag served by one loop.
fn pump_until_stopped(stop: &AtomicBool) {
    while !stop.load(Ordering::Acquire) {
        let mut msg = MSG::default();
        // SAFETY: `msg` is a valid, exclusively borrowed `MSG`; the calls run on the thread that owns
        // the queue.
        if unsafe { PeekMessageW(&mut msg, None, 0, 0, PM_REMOVE) }.as_bool() {
            if msg.message == WM_QUIT {
                break;
            }
            let _ = unsafe { DispatchMessageW(&msg) };
        } else {
            thread::sleep(IDLE_SLEEP);
        }
    }
}
