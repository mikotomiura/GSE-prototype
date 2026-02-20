use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Mutex;
use std::thread;
use std::time::{SystemTime, UNIX_EPOCH};

use crossbeam_channel::Sender;
use lazy_static::lazy_static;
use windows::Win32::Foundation::{HINSTANCE, HMODULE, HWND, LPARAM, LRESULT, WPARAM};
use windows::Win32::UI::Accessibility::{SetWinEventHook, HWINEVENTHOOK};
use windows::Win32::UI::WindowsAndMessaging::{
    CallNextHookEx, DispatchMessageW, GetMessageW, SetWindowsHookExW, HHOOK, KBDLLHOOKSTRUCT, MSG,
    WH_KEYBOARD_LL, WM_KEYDOWN, WM_KEYUP, WM_SYSKEYDOWN, WM_SYSKEYUP,
};

use crate::analysis::features::InputEvent;

// IME WinEvent constants (winuser.h, Windows 8+)
// These fire in ANY foreground process - no DLL injection needed with WINEVENT_OUTOFCONTEXT
const EVENT_OBJECT_IME_CHANGE: u32 = 0x8016; // Composition string changed (romaji → hiragana)
const EVENT_OBJECT_IME_SHOW: u32 = 0x8017; // IME UI shown (candidate list appeared)
const EVENT_OBJECT_IME_HIDE: u32 = 0x8018; // IME UI hidden (composition confirmed/cancelled)

// WINEVENT flags (winuser.h) - not exposed as typed constants in windows crate 0.58
const WINEVENT_OUTOFCONTEXT: u32 = 0x0000; // Callback fires in hook thread (no DLL injection)
const WINEVENT_SKIPOWNPROCESS: u32 = 0x0002; // Ignore IME events from our own process

/// Cross-process IME composition state.
/// Updated by the WinEvent hook when IME starts/stops in ANY foreground application.
/// This is the only reliable cross-process IME detection method that requires no DLL injection.
pub static IME_ACTIVE: AtomicBool = AtomicBool::new(false);

/// Returns true if an IME is currently composing text in the foreground application.
pub fn is_ime_active() -> bool {
    IME_ACTIVE.load(Ordering::Relaxed)
}

// Wrapper to make HHOOK Send+Sync for lazy_static
struct ThreadSafeHook(#[allow(dead_code)] HHOOK);
unsafe impl Send for ThreadSafeHook {}
unsafe impl Sync for ThreadSafeHook {}

// Wrapper to make HWINEVENTHOOK Send+Sync for lazy_static
// The hook handle must stay alive for the duration of the app to keep the hook active.
struct ThreadSafeWinEventHook(#[allow(dead_code)] HWINEVENTHOOK);
unsafe impl Send for ThreadSafeWinEventHook {}
unsafe impl Sync for ThreadSafeWinEventHook {}

lazy_static! {
    static ref HOOK_HANDLE: Mutex<Option<ThreadSafeHook>> = Mutex::new(None);
    static ref WINEVENT_HOOK_HANDLE: Mutex<Option<ThreadSafeWinEventHook>> = Mutex::new(None);
    static ref EVENT_SENDER: Mutex<Option<Sender<InputEvent>>> = Mutex::new(None);
}

/// WinEvent callback for cross-process IME detection.
/// Called in the hook thread's message loop when IME events occur in any process.
/// WINEVENT_OUTOFCONTEXT ensures this runs in our thread without DLL injection.
unsafe extern "system" fn win_event_callback(
    _hook: HWINEVENTHOOK,
    event: u32,
    _hwnd: HWND,
    _id_object: i32,
    _id_child: i32,
    _id_event_thread: u32,
    _dwms_event_time: u32,
) {
    match event {
        // Composition started or changed: romaji typed / hiragana displayed / candidate shown
        EVENT_OBJECT_IME_SHOW | EVENT_OBJECT_IME_CHANGE => {
            IME_ACTIVE.store(true, Ordering::Relaxed);
        }
        // Composition ended: user pressed Enter (confirm) or Escape (cancel)
        EVENT_OBJECT_IME_HIDE => {
            IME_ACTIVE.store(false, Ordering::Relaxed);
        }
        _ => {}
    }
}

pub fn init_hook(sender: Sender<InputEvent>) {
    // Store sender in global state for use in hook callback
    {
        let mut s = (*EVENT_SENDER).lock().unwrap();
        *s = Some(sender);
    }

    // Spawn dedicated hook thread
    // Both WH_KEYBOARD_LL and WinEvent hooks require a message loop to function.
    thread::spawn(|| {
        unsafe {
            // --- Step 1: Install low-level keyboard hook ---
            let hook_id =
                SetWindowsHookExW(WH_KEYBOARD_LL, Some(hook_callback), HINSTANCE::default(), 0);

            match hook_id {
                Ok(h) => {
                    {
                        let mut handle = (*HOOK_HANDLE).lock().unwrap();
                        *handle = Some(ThreadSafeHook(h));
                    }
                    tracing::info!("Keyboard hook installed");
                }
                Err(e) => {
                    tracing::error!("Failed to install keyboard hook: {:?}", e);
                    return;
                }
            }

            // --- Step 2: Install WinEvent hook for cross-process IME detection ---
            // Range [EVENT_OBJECT_IME_CHANGE=0x8016, EVENT_OBJECT_IME_HIDE=0x8018] covers
            // the entire IME lifecycle: composition start → candidate display → commit/cancel.
            //
            // WINEVENT_OUTOFCONTEXT: callback fires in our thread's message loop.
            //   - No DLL injection required.
            //   - Works across all processes including UWP/sandboxed apps.
            // WINEVENT_SKIPOWNPROCESS: ignore IME events from our own process.
            let ime_hook = SetWinEventHook(
                EVENT_OBJECT_IME_CHANGE, // 0x8016: fires when romaji → hiragana conversion starts
                EVENT_OBJECT_IME_HIDE,   // 0x8018: fires when composition ends
                HMODULE::default(), // NULL - no DLL needed for WINEVENT_OUTOFCONTEXT
                Some(win_event_callback),
                0, // All processes
                0, // All threads
                WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS,
            );

            if ime_hook.is_invalid() {
                tracing::warn!("Failed to install IME WinEvent hook");
            } else {
                tracing::info!("IME WinEvent hook installed (cross-process IME detection active)");
                let mut handle = (*WINEVENT_HOOK_HANDLE).lock().unwrap();
                *handle = Some(ThreadSafeWinEventHook(ime_hook));
            }

            // --- Step 3: Message loop ---
            // Required for WH_KEYBOARD_LL to receive events.
            // Also required for WinEvent callbacks (WINEVENT_OUTOFCONTEXT) to be delivered:
            // With WINEVENT_OUTOFCONTEXT, Windows posts events to the thread's message queue
            // and dispatches them via DispatchMessageW. Both calls are required.
            let mut msg = MSG::default();
            while GetMessageW(&mut msg, None, 0, 0).as_bool() {
                DispatchMessageW(&msg);
            }
        }
    });
}

unsafe extern "system" fn hook_callback(code: i32, wparam: WPARAM, lparam: LPARAM) -> LRESULT {
    if code >= 0 {
        let event_type = wparam.0 as u32;
        let is_press = event_type == WM_KEYDOWN || event_type == WM_SYSKEYDOWN;
        let is_release = event_type == WM_KEYUP || event_type == WM_SYSKEYUP;

        if is_press || is_release {
            let vk_code = (*(lparam.0 as *const KBDLLHOOKSTRUCT)).vkCode;
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_millis() as u64;

            let event = InputEvent {
                vk_code,
                timestamp,
                is_press,
            };

            // Non-blocking send attempt
            if let Ok(guard) = (*EVENT_SENDER).try_lock() {
                if let Some(sender) = guard.as_ref() {
                    let _ = sender.try_send(event);
                }
            }
        }
    }

    CallNextHookEx(None, code, wparam, lparam)
}
