use std::sync::atomic::Ordering;
use std::time::{SystemTime, UNIX_EPOCH};

use crossbeam_channel::Sender;
use windows::{
    core::*,
    Win32::Foundation::{BOOL, HWND, LPARAM},
    Win32::System::Com::*,
    Win32::UI::Accessibility::*,
    Win32::UI::Input::Ime::{ImmGetContext, ImmGetOpenStatus, ImmReleaseContext},
    Win32::UI::WindowsAndMessaging::{
        EnumWindows, GetClassNameW, GetForegroundWindow, IsWindowVisible,
    },
};

use crate::logger::LogEntry;

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
                        // Check for "Candidate" only; do NOT include "Ime" — WebView2
                        // accessibility elements may expose class names containing "Ime"
                        // (e.g. ImeMode, ImeInputMode), which would cause a false-positive
                        // that permanently pauses analysis when the Tauri window has focus.
                        if name.contains("Candidate") {
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
        if is_stale_winevent_active(winevent_active, enumwindows_active, uia_active) {
            crate::input::hook::IME_ACTIVE.store(false, Ordering::Relaxed);
            return false;
        }

        winevent_active || enumwindows_active || uia_active
    }
}

/// Scan all top-level windows for visible IME candidate windows using EnumWindows.
///
/// マッチ判定そのもの (どのクラス名を候補ウィンドウとみなすか、"MSCTFIME UI" や
/// 完全一致 "IME" をなぜ除外するか) は `is_ime_candidate_class_name` の doc を参照。
///
/// ⚠️★★★ **2026-08-22 に `pub` へ上げた (収集開始前)。**
/// ★ 理由: `examples/ime_winevent_probe.rs` から**この関数そのもの**を叩いて
/// 実機での検出率を測るため。⚠️ プローブ側にロジックを**複製すると
/// 「複製の方が動いた」という無意味な計測**になり、本番経路の可否を答えられない。
/// ★ 公開したのは可視性だけで、シグネチャも中身も変えていない。
pub fn is_ime_candidate_window_visible() -> bool {
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

            if is_ime_candidate_class_name(&class) {
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

// ---------------------------------------------------------------------------
// IME candidate window decisions (pure — テストできる形に切り出す)
// ---------------------------------------------------------------------------

/// WinEvent (`IME_ACTIVE`) が立っているのに EnumWindows / UIAutomation のどちらも
/// 候補ウィンドウを確認できないとき、`IME_ACTIVE` は stale (EVENT_OBJECT_IME_HIDE 取りこぼし)。
///
/// ⚠️★ stale のまま放置すると、二度と `EVENT_OBJECT_IME_HIDE` が来ない限り
/// 分析が永久に一時停止する (fail-open ではなく fail-stuck になる)。
fn is_stale_winevent_active(
    winevent_active: bool,
    enumwindows_active: bool,
    uia_active: bool,
) -> bool {
    winevent_active && !enumwindows_active && !uia_active
}

/// IME 候補ウィンドウのクラス名判定。
///
/// ⚠️★★ **"MSCTFIME UI" (言語バーの A/あ 表示) と、完全一致の "IME" (IMM32 の常駐
/// システムウィンドウ) を含めてはならない。** どちらも日本語 IME 読み込み時は常時
/// 可視なため、含めると変換していないときも false positive になり、
/// 分析が永久に一時停止する事故になる (実際に起きた不具合)。
/// ★ 部分一致 "CandidateUI" / "Candidate" のみで判定することでこれらを自然に除外する。
fn is_ime_candidate_class_name(class: &str) -> bool {
    class.contains("CandidateUI") || class.contains("Candidate")
}

/// Spawn a dedicated background thread for IME open/close state tracking.
///
/// # Detection strategy (layered, in priority order)
///
/// **Primary — `ImmGetOpenStatus` polling:**
/// When `ImmGetContext(foreground_hwnd)` returns a non-null HIMC, `ImmGetOpenStatus`
/// gives the authoritative IME mode. This works when the foreground window is owned
/// by a process whose IME context is accessible (rare on Windows 10/11 for cross-process
/// windows, but used as a supplement when available).
///
/// **Fallback — `IME_STATE_DIRTY` flag from VK_DBE_* keys:**
/// `hook_callback` detects VK_DBE_* / VK_KANJI key presses and atomically updates
/// `IME_OPEN` + sets `IME_STATE_DIRTY`. When `ImmGetContext` returns NULL (typical for
/// cross-process windows), this thread reads the dirty flag and emits `LogEntry::ImeState`
/// at its own timestamp — ensuring the log entry is always temporally separated from
/// the triggering keystroke (no same-millisecond flapping).
///
/// # Lag reduction (ADVICE.md v2 requirement)
///
/// Instead of a fixed 100ms sleep, the thread waits on `wake_rx` with a 100ms timeout.
/// `hook_callback` sends a wake signal on every keypress (non-blocking `try_send`).
/// On wake, we sleep 5ms to let the OS route the key through the IME engine, then poll.
/// Maximum lag during active typing: ~5ms (down from 100ms).
///
/// # No flapping guarantee
///
/// `LogEntry::ImeState` is emitted only from THIS thread, never from the analysis thread
/// processing the key event. The timestamp is `SystemTime::now()` at the moment of
/// emission — always ≥5ms after the triggering keystroke.
pub fn spawn_ime_open_polling_thread(
    log_tx: Sender<LogEntry>,
    wake_rx: crossbeam_channel::Receiver<()>,
) {
    std::thread::spawn(move || {
        // Option<bool>: None = まだ一度も検出していない初期状態。
        // Some(v) = 前回 emit した状態。
        // None の場合は current_state が false でも必ず emit する
        // (起動直後に IME が A モードのまま VK 240 を押した場合を捕捉する)。
        let mut last_state: Option<bool> = None;

        loop {
            // Wait for a keystroke wake signal, or fall back to 100ms idle poll.
            let woke_by_key = wake_rx
                .recv_timeout(std::time::Duration::from_millis(100))
                .is_ok();

            if woke_by_key {
                // Brief delay: gives the OS time to route the key through the IME
                // engine so that ImmGetOpenStatus / IME_OPEN reflect the new mode.
                std::thread::sleep(std::time::Duration::from_millis(5));
            }

            // --- PRIMARY: ImmGetContext-based detection ---
            // May return NULL for cross-process windows on Windows 10/11.
            let mut imm_succeeded = false;
            unsafe {
                let hwnd = GetForegroundWindow();
                if !hwnd.0.is_null() {
                    let himc = ImmGetContext(hwnd);
                    if !himc.0.is_null() {
                        let current_state = ImmGetOpenStatus(himc).as_bool();
                        let _ = ImmReleaseContext(hwnd, himc);
                        imm_succeeded = true;

                        // last_state が None (初回) か、前回と異なる場合のみ emit
                        if last_state.map_or(true, |prev| prev != current_state) {
                            last_state = Some(current_state);
                            crate::input::hook::IME_OPEN.store(current_state, Ordering::Relaxed);
                            emit_ime_state(&log_tx, current_state);
                        }
                    }
                }
            }

            // --- FALLBACK: VK_DBE_* dirty flag from hook_callback ---
            // Used when ImmGetContext returns NULL (typical cross-process case).
            // IME_OPEN was already updated by the hook; we just need to detect the
            // change and emit the log entry with a fresh timestamp.
            if !imm_succeeded {
                if crate::input::hook::IME_STATE_DIRTY.swap(false, Ordering::AcqRel) {
                    let current_state = crate::input::hook::IME_OPEN.load(Ordering::Acquire);
                    // last_state が None (初回) か、前回と異なる場合のみ emit
                    if last_state.map_or(true, |prev| prev != current_state) {
                        last_state = Some(current_state);
                        emit_ime_state(&log_tx, current_state);
                    }
                }
            }
        }
    });
}

/// Emit a `LogEntry::ImeState` to the logger channel with the current wall-clock time.
fn emit_ime_state(log_tx: &Sender<LogEntry>, on: bool) {
    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    let active = crate::input::hook::IME_ACTIVE.load(Ordering::Relaxed);
    let _ = log_tx.try_send(LogEntry::ImeState {
        timestamp: ts,
        on,
        active,
    });
    tracing::debug!(
        "IME open: {} (polling)",
        if on { "ON (あ)" } else { "OFF (A)" }
    );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn stale_when_only_winevent_signals_active() {
        assert!(
            is_stale_winevent_active(true, false, false),
            "★ WinEvent だけが active なら stale とみなし、放置せずリセットする"
        );
    }

    #[test]
    fn not_stale_when_enumwindows_confirms() {
        assert!(!is_stale_winevent_active(true, true, false));
    }

    #[test]
    fn not_stale_when_uia_confirms() {
        assert!(!is_stale_winevent_active(true, false, true));
    }

    #[test]
    fn not_stale_when_winevent_itself_is_false() {
        // WinEvent が false のときは「stale」という概念自体が当てはまらない。
        assert!(!is_stale_winevent_active(false, false, false));
    }

    #[test]
    fn matches_known_candidate_class_names() {
        assert!(is_ime_candidate_class_name("CandidateUI_UIElement"));
        assert!(is_ime_candidate_class_name("SomeCandidateWindow"));
    }

    /// ★★ 回帰テストの本体。この 2 クラス名を含めると分析が永久停止する不具合が実際に起きた。
    #[test]
    fn excludes_language_bar_and_imm32_system_window() {
        assert!(
            !is_ime_candidate_class_name("MSCTFIME UI"),
            "言語バー (A/あ 表示) は変換中でなくても常時可視 → 含めると誤検知が固定化する"
        );
        assert!(
            !is_ime_candidate_class_name("IME"),
            "IMM32 の常駐システムウィンドウは常時可視 → 完全一致 'IME' は含めない"
        );
    }

    #[test]
    fn does_not_match_unrelated_class_names() {
        assert!(!is_ime_candidate_class_name("Chrome_WidgetWin_1"));
        assert!(!is_ime_candidate_class_name(""));
    }
}
