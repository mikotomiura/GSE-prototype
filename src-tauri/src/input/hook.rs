use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::OnceLock;

use crossbeam_channel::Sender;

use crate::analysis::features::InputEvent;

// ---------------------------------------------------------------------------
// Japanese IME mode VK codes — shared between platforms.
// Windows: captured by WH_KEYBOARD_LL before IME engine.
// macOS: detected via JIS HID keycodes in CGEventTap callback.
// ---------------------------------------------------------------------------
pub const VK_DBE_ALPHANUMERIC: u32 = 0xF0; // 英数: Switch to alphanumeric (A mode)
pub const VK_DBE_KATAKANA: u32 = 0xF1; // カタカナ: Switch to katakana
pub const VK_DBE_HIRAGANA: u32 = 0xF2; // ひらがな: Switch to hiragana (あ mode)
pub const VK_DBE_SBCSCHAR: u32 = 0xF3; // 半角: Single-byte character mode
pub const VK_DBE_DBCSCHAR: u32 = 0xF4; // 全角: Double-byte character mode
pub const VK_KANJI: u32 = 0x19; // 半角/全角: Half-width / full-width toggle

// ---------------------------------------------------------------------------
// Shared atomic state — accessed by both platform implementations and
// the analysis/IME polling threads.
// ---------------------------------------------------------------------------

/// Cross-process IME composition state.
/// Windows: updated by WinEvent hook (EVENT_OBJECT_IME_SHOW/HIDE).
/// macOS: updated by CGEventTap keystroke state machine.
pub static IME_ACTIVE: AtomicBool = AtomicBool::new(false);

/// Returns true if an IME is currently composing text in the foreground application.
pub fn is_ime_active() -> bool {
    IME_ACTIVE.load(Ordering::Relaxed)
}

/// Japanese IME input mode: true = あ/カ (Japanese), false = A (alphanumeric/coding).
/// The analysis thread reads this for HMM β-selection (writing vs coding baselines).
pub static IME_OPEN: AtomicBool = AtomicBool::new(false);

/// Returns true if the Japanese IME is currently in Japanese-input mode.
pub fn is_ime_open() -> bool {
    IME_OPEN.load(Ordering::Relaxed)
}

/// Dirty flag: set by hook callback when a VK_DBE_* / VK_KANJI key is pressed.
/// The IME open polling thread reads this to emit LogEntry::ImeState with a fresh timestamp.
pub static IME_STATE_DIRTY: AtomicBool = AtomicBool::new(false);

/// Unix epoch millisecond timestamp of the most recent keypress.
/// Windows: updated by WH_KEYBOARD_LL callback.
/// macOS: updated by CGEventTap callback.
pub static LAST_KEY_MS: AtomicU64 = AtomicU64::new(0);

/// Returns the Unix epoch millisecond timestamp of the last keypress.
pub fn last_key_ms() -> u64 {
    LAST_KEY_MS.load(Ordering::Relaxed)
}

// ---------------------------------------------------------------------------
// macOS-specific atomics
// ---------------------------------------------------------------------------

/// IME inline composition state (macOS only): true when the user is actively typing
/// romaji that the IME is converting to kana (marked/underlined text).
#[cfg(target_os = "macos")]
pub static IME_COMPOSING: AtomicBool = AtomicBool::new(false);

/// Set to true once any JIS IME key has been observed (macOS only).
/// Disables TIS polling to avoid per-app input source interference.
#[cfg(target_os = "macos")]
pub static JIS_KEYBOARD_SEEN: AtomicBool = AtomicBool::new(false);

/// true when the keyboard hook is successfully installed.
/// Read by `get_hook_status` Tauri command to report hook state.
/// Windows: SetWindowsHookExW 成功時に true、フック無効化時に false。
/// macOS: CGEventTap インストール成功時に true。
pub static HOOK_ACTIVE: AtomicBool = AtomicBool::new(false);

/// macOS: CGEventTap コールバックが呼ばれた回数（診断用）。
/// 0 のままなら「タップは作成されたがイベントが届いていない」ことを示す。
#[cfg(target_os = "macos")]
pub static CALLBACK_COUNT: AtomicU64 = AtomicU64::new(0);

// ---------------------------------------------------------------------------
// Lock-free channels — shared between platforms
// ---------------------------------------------------------------------------

/// Lock-free sender for keystroke events → analysis thread.
pub static EVENT_SENDER: OnceLock<Sender<InputEvent>> = OnceLock::new();

/// Lock-free wake signal sender for the IME open polling thread.
pub static POLL_WAKE_TX: OnceLock<Sender<()>> = OnceLock::new();

/// Store the polling thread's wake channel sender.
/// Must be called before `init_hook` so the sender is ready when the hook fires.
pub fn set_poll_wake_sender(tx: Sender<()>) {
    let _ = POLL_WAKE_TX.set(tx);
}

// ---------------------------------------------------------------------------
// Platform-specific hook implementations
// ---------------------------------------------------------------------------

#[cfg(target_os = "windows")]
#[path = "hook_windows.rs"]
mod hook_windows;

#[cfg(target_os = "macos")]
#[path = "hook_macos.rs"]
mod hook_macos;

/// Install the platform-specific keyboard hook and begin delivering InputEvents to `sender`.
/// Spawns a dedicated background thread; returns immediately.
pub fn init_hook(sender: Sender<InputEvent>) {
    let _ = EVENT_SENDER.set(sender);

    #[cfg(target_os = "windows")]
    hook_windows::start();

    #[cfg(target_os = "macos")]
    hook_macos::start();
}
