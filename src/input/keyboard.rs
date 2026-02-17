use std::sync::Mutex;
use std::time::Instant;
use std::collections::VecDeque;
use tracing::{info, warn, error};
use once_cell::sync::Lazy;
use windows::Win32::UI::WindowsAndMessaging::{
    SetWindowsHookExW, UnhookWindowsHookEx, CallNextHookEx, WH_KEYBOARD_LL,
    WM_KEYDOWN, KBDLLHOOKSTRUCT,
};
use windows::Win32::UI::Input::KeyboardAndMouse::VK_BACK;
use windows::Win32::Foundation::{WPARAM, LPARAM, LRESULT};
use windows::Win32::System::LibraryLoader::GetModuleHandleW;
use crate::inference::rules::{classify_state, FlowState};
use crate::inference::hmm::HMM;

// Static variable to store the hook handle (stored as isize, converted to/from HHOOK)
static HOOK_HANDLE: Mutex<Option<isize>> = Mutex::new(None);

// Static variable to store the last key press time
static LAST_KEY_TIME: Mutex<Option<Instant>> = Mutex::new(None);

// Static variable to track backspace key press times (for 5-second sliding window)
static BACKSPACE_TIMES: Mutex<VecDeque<Instant>> = Mutex::new(VecDeque::new());

// Static variable to store the last backspace press time (for F6 pause-after-delete)
static LAST_BACKSPACE_PRESS: Mutex<Option<Instant>> = Mutex::new(None);

// Static variable for HMM instance (lazy initialization with once_cell)
static HMM_INSTANCE: Lazy<Mutex<HMM>> = Lazy::new(|| {
    Mutex::new(HMM::new())
});

// Static variable to track the previous state (for detecting transitions)
// This prevents unnecessary overlay updates on every keystroke
static LAST_STATE: Mutex<Option<FlowState>> = Mutex::new(None);

// Threshold for considering a key press as a character input (filters some special keys)
const MIN_FLIGHT_TIME_FOR_INPUT: u64 = 10;

/// Unsafe extern callback for the keyboard hook
/// This function is called by Windows for every keyboard event
unsafe extern "system" fn keyboard_proc(
    n_code: i32,
    w_param: WPARAM,
    l_param: LPARAM,
) -> LRESULT {
    if n_code >= 0 {
        // Only process on WM_KEYDOWN events
        if w_param.0 == WM_KEYDOWN as usize {
            let kb_struct = &*(l_param.0 as *const KBDLLHOOKSTRUCT);
            let current_time = Instant::now();
            let vk_code = kb_struct.vkCode;

            // Handle Backspace key separately
            if vk_code == VK_BACK.0 as u32 {
                // Add backspace timestamp to the deque
                match BACKSPACE_TIMES.lock() {
                    Ok(mut guard) => {
                        guard.push_back(current_time);

                        // Record last backspace press for F6 (pause-after-delete)
                        if let Ok(mut lb) = LAST_BACKSPACE_PRESS.lock() {
                            *lb = Some(current_time);
                        }

                        // Remove timestamps older than 5 seconds
                        while let Some(&oldest_time) = guard.front() {
                            if current_time.duration_since(oldest_time).as_secs() >= 5 {
                                guard.pop_front();
                            } else {
                                break;
                            }
                        }

                        info!("Backspace detected (total in 5s window: {})", guard.len());
                    }
                    Err(_) => {
                        error!("Failed to acquire BACKSPACE_TIMES lock - mutex poisoned");
                    }
                }
            } else {
                // Regular key press - calculate flight time
                let mut last_time_guard = LAST_KEY_TIME.lock()
                    .expect("LAST_KEY_TIME mutex poisoned - critical failure");
                
                if let Some(prev_time) = *last_time_guard {
                    let flight_time = current_time.duration_since(prev_time);
                    let flight_time_ms = flight_time.as_millis() as u64;

                    // Only count it as flight time if it's above minimum threshold
                    if flight_time_ms >= MIN_FLIGHT_TIME_FOR_INPUT {
                        // Get backspace count from the deque
                        let backspace_count = match BACKSPACE_TIMES.lock() {
                            Ok(guard) => guard.len() as u32,
                            Err(_) => {
                                error!("Failed to acquire BACKSPACE_TIMES lock");
                                0
                            }
                        };

                        // Compute pause-after-delete (F6): time since last backspace press to this key
                        let pause_after_delete_ms_opt = match LAST_BACKSPACE_PRESS.lock() {
                            Ok(guard) => guard.map(|t| current_time.duration_since(t).as_millis() as u64),
                            Err(_) => {
                                error!("Failed to acquire LAST_BACKSPACE_PRESS lock");
                                None
                            }
                        };

                        // Hesitation if pause after delete > 2000ms
                        let hesitation = match pause_after_delete_ms_opt {
                            Some(ms) if ms >= 2000 => true,
                            _ => false,
                        };

                        // For HMM, include hesitation as an extra backspace signal (simple proxy)
                        let backspace_count_for_hmm = backspace_count + if hesitation { 1 } else { 0 };

                        // --- PHASE 2: Rule-based classification ---
                        let rule_state = classify_state(flight_time_ms, backspace_count, pause_after_delete_ms_opt);

                        // --- PHASE 3: HMM-based probabilistic classification ---
                        // Optimize: Single lock for both update and read operations
                        let (hmm_state, flow_prob, incubation_prob, stuck_prob) = {
                            let mut hmm = HMM_INSTANCE.lock()
                                .expect("HMM mutex poisoned - critical system failure");
                            let state = hmm.update(flight_time_ms as f64, backspace_count_for_hmm);
                            let (flow, incub, stuck) = hmm.state_probs();
                            (state, flow, incub, stuck)
                        };

                        // Log with appropriate level based on HMM state
                        // (more accurate due to probabilistic modeling)
                        // Also update overlay if state has changed
                        match hmm_state {
                            FlowState::Flow => {
                                info!(
                                    "[STATE: FLOW] FlightTime: {}ms | Backspace: {} | Rule: {} | HMM Probs: FLOW={:.2}% INC={:.2}% STUCK={:.2}% | Key: {}",
                                    flight_time_ms, backspace_count, rule_state.as_str(),
                                    flow_prob * 100.0, incubation_prob * 100.0, stuck_prob * 100.0,
                                    vk_code
                                );
                                // Update overlay if state has changed
                                if let Ok(mut last_state) = LAST_STATE.lock() {
                                    if *last_state != Some(FlowState::Flow) {
                                        crate::update_overlay_from_state(FlowState::Flow);
                                        *last_state = Some(FlowState::Flow);
                                    }
                                }
                            }
                            FlowState::Incubation => {
                                warn!(
                                    "[STATE: INCUBATION] FlightTime: {}ms | Backspace: {} | Rule: {} | HMM Probs: FLOW={:.2}% INC={:.2}% STUCK={:.2}% | Key: {}",
                                    flight_time_ms, backspace_count, rule_state.as_str(),
                                    flow_prob * 100.0, incubation_prob * 100.0, stuck_prob * 100.0,
                                    vk_code
                                );
                                // Update overlay if state has changed
                                if let Ok(mut last_state) = LAST_STATE.lock() {
                                    if *last_state != Some(FlowState::Incubation) {
                                        crate::update_overlay_from_state(FlowState::Incubation);
                                        *last_state = Some(FlowState::Incubation);
                                    }
                                }
                            }
                            FlowState::Stuck => {
                                error!(
                                    "[STATE: STUCK] FlightTime: {}ms | Backspace: {} | Rule: {} | HMM Probs: FLOW={:.2}% INC={:.2}% STUCK={:.2}% | Key: {}",
                                    flight_time_ms, backspace_count, rule_state.as_str(),
                                    flow_prob * 100.0, incubation_prob * 100.0, stuck_prob * 100.0,
                                    vk_code
                                );
                                // Update overlay if state has changed
                                if let Ok(mut last_state) = LAST_STATE.lock() {
                                    if *last_state != Some(FlowState::Stuck) {
                                        crate::update_overlay_from_state(FlowState::Stuck);
                                        *last_state = Some(FlowState::Stuck);
                                    }
                                }
                            }
                        }
                    }
                } else {
                    info!("First key press detected (key: {})", vk_code);
                }

                *last_time_guard = Some(current_time);
            }
        }
    }

    // Always call the next hook in the chain
    let hook_handle = HOOK_HANDLE.lock().unwrap();
    if let Some(handle) = *hook_handle {
        let hhook = windows::Win32::UI::WindowsAndMessaging::HHOOK(handle as *mut std::ffi::c_void);
        CallNextHookEx(hhook, n_code, w_param, l_param)
    } else {
        CallNextHookEx(None, n_code, w_param, l_param)
    }
}

/// Install the global keyboard hook
/// Must be called from the main thread that runs the message loop
pub fn install_hook() -> Result<(), String> {
    unsafe {
        // Get the module handle for the current executable
        let hmodule = GetModuleHandleW(None)
            .map_err(|e| format!("Failed to get module handle: {}", e))?;

        // Install the hook
        let hook_handle = SetWindowsHookExW(
            WH_KEYBOARD_LL,
            Some(keyboard_proc),
            hmodule,
            0, // Thread ID 0 means global hook
        )
        .map_err(|e| format!("SetWindowsHookExW failed: {}", e))?;

        // Store as isize for compatibility with static initialization
        *HOOK_HANDLE.lock().unwrap() = Some(hook_handle.0 as isize);
        Ok(())
    }
}

/// Uninstall the global keyboard hook
pub fn uninstall_hook() {
    let mut hook_guard = HOOK_HANDLE.lock().unwrap();
    if let Some(handle) = *hook_guard {
        unsafe {
            let hhook = windows::Win32::UI::WindowsAndMessaging::HHOOK(handle as *mut std::ffi::c_void);
            let _ = UnhookWindowsHookEx(hhook);
        }
        *hook_guard = None;
    }
}
