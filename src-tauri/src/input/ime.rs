use std::sync::atomic::Ordering;

use windows::{
    core::*,
    Win32::Foundation::{BOOL, HWND, LPARAM},
    Win32::System::Com::*,
    Win32::UI::Accessibility::*,
    Win32::UI::WindowsAndMessaging::{EnumWindows, GetClassNameW, IsWindowVisible},
};

pub struct ImeMonitor {
    automation: Option<IUIAutomation>,
}

impl ImeMonitor {
    pub fn new() -> Self {
        unsafe {
            // COM is initialized here for the UIAutomation fallback.
            let _ = CoInitializeEx(None, COINIT_MULTITHREADED);

            let automation: Result<IUIAutomation> =
                CoCreateInstance(&CUIAutomation, None, CLSCTX_INPROC_SERVER);

            if let Ok(auto) = automation {
                Self {
                    automation: Some(auto),
                }
            } else {
                Self { automation: None }
            }
        }
    }

    /// Returns true if IME (Japanese input method, etc.) is currently composing text.
    ///
    /// Detection strategy (in priority order):
    ///
    /// 1. **WinEvent (PRIMARY)**: The WinEvent hook in hook.rs monitors
    ///    EVENT_OBJECT_IME_CHANGE/SHOW/HIDE across all processes via WINEVENT_OUTOFCONTEXT.
    ///    This is the only method that reliably detects the romaji→hiragana composition
    ///    phase (before the candidate list appears). Works for any foreground application.
    ///
    ///    WHY the old ImmGetContext approach failed:
    ///    ImmGetContext() returns NULL for windows owned by a different process.
    ///    Since we never type in our own app, it ALWAYS returned NULL.
    ///
    /// 2. **EnumWindows (SECONDARY)**: Scans all top-level windows for visible IME
    ///    candidate windows by class name. Covers the candidate-selection phase as a
    ///    belt-and-suspenders fallback if the WinEvent hasn't fired yet.
    ///
    /// 3. **UIAutomation (TERTIARY)**: Original approach retained as last resort.
    ///    Limited: only fires when the focused element is the IME window itself,
    ///    which doesn't happen during normal composition.
    pub fn is_candidate_window_open(&self) -> bool {
        let winevent_active = crate::input::hook::is_ime_active();

        // --- SECONDARY: EnumWindows scan for visible IME candidate windows ---
        // NOTE: "MSCTFIME UI" is intentionally excluded here.
        // That class belongs to the language bar (A/あ button on taskbar) which is
        // ALWAYS visible when Japanese IME is loaded, even when NOT composing.
        // Including it caused a permanent false-positive that paused all analysis.
        let enumwindows_active = is_ime_candidate_window_visible();

        // --- TERTIARY: UIAutomation focused-element check ---
        let uia_active = if let Some(auto) = &self.automation {
            let mut found = false;
            unsafe {
                if let Ok(element) = auto.GetFocusedElement() {
                    if let Ok(class_name) = element.CurrentClassName() {
                        let name = class_name.to_string();
                        if name.contains("Candidate") || name.contains("Ime") {
                            found = true;
                        }
                    }
                    if !found {
                        if let Ok(name_bstr) = element.CurrentName() {
                            let name = name_bstr.to_string();
                            if name.contains("候補") {
                                found = true;
                            }
                        }
                    }
                }
            }
            found
        } else {
            false
        };

        // Safety: if WinEvent says IME is active but neither EnumWindows nor UIAutomation
        // confirms a visible candidate window, the IME_ACTIVE flag is stale.
        // This happens when EVENT_OBJECT_IME_HIDE was missed (e.g. focus change, crash).
        // Reset it here to prevent permanently pausing all keystroke analysis.
        if winevent_active && !enumwindows_active && !uia_active {
            crate::input::hook::IME_ACTIVE.store(false, Ordering::Relaxed);
            return false;
        }

        winevent_active || enumwindows_active || uia_active
    }
}

/// Scan all top-level windows for visible IME candidate windows using EnumWindows.
///
/// Known IME candidate window class names on Windows 10/11:
///   - "CandidateUI_UIElement" : Modern IME candidate list (Microsoft IME, Google IME)
///   - "IME"               : Classic IMM32 IME window
///   - "*Candidate*"       : Catch-all for other IME implementations
///
/// INTENTIONALLY EXCLUDED:
///   - "MSCTFIME UI" : This is the TSF language bar (A/あ indicator on the taskbar).
///     It is ALWAYS visible on systems with Japanese IME loaded, even during normal
///     Latin text entry. Including it caused the engine to be permanently paused.
fn is_ime_candidate_window_visible() -> bool {
    // The callback sets *lparam to true and stops enumeration when an IME window is found.
    unsafe extern "system" fn callback(hwnd: HWND, lparam: LPARAM) -> BOOL {
        // Skip invisible windows
        if !IsWindowVisible(hwnd).as_bool() {
            return BOOL(1); // Continue enumeration
        }

        let mut buf = [0u16; 256];
        let len = GetClassNameW(hwnd, &mut buf);
        if len > 0 {
            let class = String::from_utf16_lossy(&buf[..len as usize]);

            // Match visible IME candidate windows only.
            // Do NOT include "MSCTFIME" - that is the always-visible language bar.
            if class.contains("CandidateUI")
                || class == "IME"
                || class.contains("Candidate")
            {
                // Signal found via lparam (pointer to bool on caller's stack)
                *(lparam.0 as *mut bool) = true;
                return BOOL(0); // Stop enumeration
            }
        }

        BOOL(1) // Continue enumeration
    }

    let mut found = false;
    unsafe {
        // Ignore the Result: BOOL(0) from our callback is interpreted as "error"
        // by EnumWindows, but it just means we stopped early after finding a match.
        let _ = EnumWindows(Some(callback), LPARAM(&mut found as *mut bool as isize));
    }
    found
}

// Kept for API compatibility (unused)
pub fn is_ime_active_check() -> bool {
    false
}
