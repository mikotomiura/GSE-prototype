// macOS IME monitoring: ImeMonitor + IME open polling + TIS (Text Input Source) detection.
//
// ImeMonitor: reads IME_ACTIVE atomic set by the CGEventTap callback's
// keystroke state machine. When true, the HMM engine is paused.
//
// IME open polling: two detection paths:
//   Path A — JIS physical keys (fast, ~5ms): trust IME_OPEN set by hook callback.
//   Path B — ANSI/US keyboards (100ms TIS poll): menu-bar switch fallback.
//
// TIS detection: polls TISCopyCurrentKeyboardInputSource() via dispatch_sync_f
// to main GCD queue (required by HIToolbox). Checks if the input source ID
// contains "inputmethod.Japanese".

use std::ffi::c_void;
use std::sync::atomic::Ordering;
use std::time::{SystemTime, UNIX_EPOCH};

use core_foundation::base::{CFRelease, TCFType};
use core_foundation::string::CFString;
use crossbeam_channel::Sender;

use crate::logger::LogEntry;

// ---------------------------------------------------------------------------
// ImeMonitor — reads keystroke-based composition state from CGEventTap
// ---------------------------------------------------------------------------

pub struct ImeMonitor;

impl ImeMonitor {
    pub fn new() -> Self {
        tracing::info!(
            "IME Monitor: keystroke-based composition detection enabled \
             (CGEventTap state machine)"
        );
        Self
    }

    pub fn is_candidate_window_open(&self) -> bool {
        crate::input::hook::IME_ACTIVE.load(Ordering::Acquire)
    }
}

// ---------------------------------------------------------------------------
// spawn_ime_open_polling_thread — IME open/close state machine
// ---------------------------------------------------------------------------

pub fn spawn_ime_open_polling_thread(
    log_tx: Sender<LogEntry>,
    wake_rx: crossbeam_channel::Receiver<()>,
) {
    std::thread::spawn(move || {
        let mut last_state: Option<bool> = None;

        loop {
            let woke_by_key = wake_rx
                .recv_timeout(std::time::Duration::from_millis(100))
                .is_ok();

            if woke_by_key {
                std::thread::sleep(std::time::Duration::from_millis(5));
            }

            let dirty = crate::input::hook::IME_STATE_DIRTY.swap(false, Ordering::AcqRel);

            let current_state = if dirty {
                crate::input::hook::IME_OPEN.load(Ordering::Acquire)
            } else if crate::input::hook::JIS_KEYBOARD_SEEN.load(Ordering::Acquire) {
                crate::input::hook::IME_OPEN.load(Ordering::Acquire)
            } else {
                is_japanese_ime_open()
            };

            if last_state.map_or(true, |prev| prev != current_state) {
                last_state = Some(current_state);
                crate::input::hook::IME_OPEN.store(current_state, Ordering::Relaxed);
                let active = crate::input::hook::IME_ACTIVE.load(Ordering::Acquire);
                emit_ime_state(&log_tx, current_state, active);
            }
        }
    });
}

fn emit_ime_state(log_tx: &Sender<LogEntry>, on: bool, active: bool) {
    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    let _ = log_tx.try_send(LogEntry::ImeState {
        timestamp: ts,
        on,
        active,
    });
    tracing::debug!(
        "IME open: {}, active: {} (polling)",
        if on { "ON (あ)" } else { "OFF (A)" },
        active,
    );
}

// ---------------------------------------------------------------------------
// TIS FFI declarations (Carbon framework)
// ---------------------------------------------------------------------------

#[allow(non_camel_case_types)]
type TISInputSourceRef = *const c_void;
#[allow(non_camel_case_types)]
type CFStringRef = *const c_void;

#[link(name = "Carbon", kind = "framework")]
extern "C" {
    fn TISCopyCurrentKeyboardInputSource() -> TISInputSourceRef;
    fn TISGetInputSourceProperty(source: TISInputSourceRef, key: CFStringRef) -> *const c_void;
    #[allow(non_upper_case_globals)]
    static kTISPropertyInputSourceID: CFStringRef;
}

#[link(name = "System", kind = "dylib")]
extern "C" {
    #[allow(non_upper_case_globals)]
    static _dispatch_main_q: c_void;
    fn dispatch_sync_f(
        queue: *const c_void,
        context: *mut c_void,
        work: unsafe extern "C" fn(*mut c_void),
    );
}

struct TisQueryCtx {
    result: bool,
}

unsafe extern "C" fn tis_query_main_thread(ctx: *mut c_void) {
    let ctx = &mut *(ctx as *mut TisQueryCtx);

    let source = TISCopyCurrentKeyboardInputSource();
    if source.is_null() {
        ctx.result = false;
        return;
    }

    let id_ref = TISGetInputSourceProperty(source, kTISPropertyInputSourceID);

    ctx.result = if id_ref.is_null() {
        false
    } else {
        let cf_str = CFString::wrap_under_get_rule(id_ref as core_foundation::string::CFStringRef);
        let id_str = cf_str.to_string();
        id_str.contains("inputmethod.Japanese")
    };

    CFRelease(source);
}

/// Returns true if the current system keyboard input source is a Japanese IME.
/// Safe to call from any thread — internally dispatches to the main GCD queue.
fn is_japanese_ime_open() -> bool {
    let mut ctx = TisQueryCtx { result: false };
    unsafe {
        dispatch_sync_f(
            &_dispatch_main_q as *const c_void,
            &mut ctx as *mut TisQueryCtx as *mut c_void,
            tis_query_main_thread,
        );
    }
    ctx.result
}
