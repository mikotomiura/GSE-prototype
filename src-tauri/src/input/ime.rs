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

// ★ `is_ime_candidate_window_visible` は `examples/ime_winevent_probe.rs` が
//   **本番の検出関数そのもの**を叩いて実機検出率を測るために公開している
//   (⚠️ プローブ側で複製すると本番経路の可否を答えられない)。
//
// ⚠️★★★ **呼んでよいのは「ポーリングスレッド」と `examples/` だけである。**
//   ★ 中身は `EnumWindows` で**全トップレベル窓を同期列挙する重い関数**であり、
//   ⚠️ フックコールバックから呼ぶと `hook-constraints` **Win-1**
//   (コールバック内は Atomic ＋ `try_send` のみ) に違反する。
//   ⚠️ **Windows 限定の export** なので、macOS に対応物は無い (対称性は意図的に崩している)。
#[cfg(target_os = "windows")]
pub use ime_windows::{spawn_ime_open_polling_thread, ImeMonitor};

// ⚠️★ `#[doc(hidden)]`: 公開 API ではなく **診断用の出口**である、と型レベルで示す
//   (2026-08-22・cross-review 低 / security-checker LOW)。★ example から呼ぶために `pub` は要る。
#[cfg(target_os = "windows")]
#[doc(hidden)]
pub use ime_windows::is_ime_candidate_window_visible;

#[cfg(target_os = "macos")]
pub use ime_macos::{spawn_ime_open_polling_thread, ImeMonitor};
