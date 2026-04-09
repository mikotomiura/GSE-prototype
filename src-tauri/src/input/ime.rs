// Platform-specific IME monitor implementations.
// Each platform provides:
//   - ImeMonitor: checks if IME candidate window is open
//   - spawn_ime_open_polling_thread: background thread for IME open/close state tracking

#[cfg(target_os = "windows")]
#[path = "ime_windows.rs"]
mod ime_windows;

#[cfg(target_os = "macos")]
#[path = "ime_macos.rs"]
mod ime_macos;

#[cfg(target_os = "windows")]
pub use ime_windows::{spawn_ime_open_polling_thread, ImeMonitor};

#[cfg(target_os = "macos")]
pub use ime_macos::{spawn_ime_open_polling_thread, ImeMonitor};
