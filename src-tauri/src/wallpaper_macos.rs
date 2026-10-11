//! macOS の壁紙の API（`NSWorkspace`）。EH3 の肖像の層の OS 依存の部分。
//!
//! EH2 の試作 `experiments/20261009-portrait-eh2/macos/eh2_wallpaper.swift` の移植:
//! - 画面ごとの設定と読み戻しは `setDesktopImageURL:forScreen:options:error:` /
//!   `desktopImageURLForScreen:`。置き方の options は、そのときの画面の options をそのまま渡す
//!   （この層は options を変えないので、戻すときも元の options のまま）。
//! - 画像が読めるファイルでない（動く壁紙など）なら戻せないので動かさない。
//!
//! ⚠️ AppKit（`NSScreen`）はメインスレッドで呼ぶ。壁紙のスレッドからは、`lib.rs` が渡す
//! 「メインスレッドで実行する」関数（`AppHandle::run_on_main_thread`）を通して呼び、結果を待つ。
//! メインスレッドからは呼ばない（待つとデッドロックする・技術的制約 5 と同じ理由）。
//! ⚠️ 何も記録しない（`wallpaper.rs` のモジュールの doc）。

use std::path::{Path, PathBuf};
use std::sync::mpsc;
use std::sync::Arc;
use std::time::Duration;

use objc2::MainThreadMarker;
use objc2_app_kit::{NSScreen, NSWorkspace};
use objc2_foundation::{NSNumber, NSString, NSURL};

use crate::wallpaper::{Backend, Monitor};

/// メインスレッドで仕事をさせる関数（`lib.rs` が `AppHandle::run_on_main_thread` で作る）。
pub type MainRunner = Arc<dyn Fn(Box<dyn FnOnce() + Send>) + Send + Sync>;

/// メインスレッドの応答を待つ上限。
const MAIN_TIMEOUT: Duration = Duration::from_secs(5);

pub struct MacBackend {
    run_on_main: MainRunner,
}

impl MacBackend {
    pub fn new(run_on_main: MainRunner) -> Self {
        Self { run_on_main }
    }

    /// `f` をメインスレッドで実行して結果を待つ。
    fn on_main<T: Send + 'static>(
        &self,
        f: impl FnOnce(MainThreadMarker) -> T + Send + 'static,
    ) -> Result<T, String> {
        let (tx, rx) = mpsc::channel();
        (self.run_on_main)(Box::new(move || {
            if let Some(mtm) = MainThreadMarker::new() {
                let _ = tx.send(f(mtm));
            }
        }));
        rx.recv_timeout(MAIN_TIMEOUT)
            .map_err(|_| "main thread did not answer".to_string())
    }
}

/// 画面の識別子: `deviceDescription["NSScreenNumber"]`（CGDirectDisplayID）。並び順は抜き差しや
/// 主画面の切り替えで変わるので使わない。
fn screen_number(s: &NSScreen) -> Option<String> {
    let desc = s.deviceDescription();
    let n = desc.objectForKey(&NSString::from_str("NSScreenNumber"))?;
    n.downcast_ref::<NSNumber>()
        .map(|n| n.unsignedIntValue().to_string())
}

fn screen_at(mtm: MainThreadMarker, id: &str) -> Option<objc2::rc::Retained<NSScreen>> {
    let screens = NSScreen::screens(mtm);
    (0..screens.count())
        .map(|i| screens.objectAtIndex(i))
        .find(|s| screen_number(s).as_deref() == Some(id))
}

fn file_path_of(url: &NSURL) -> Option<PathBuf> {
    if !url.isFileURL() {
        return None;
    }
    url.path().map(|p| PathBuf::from(p.to_string()))
}

impl Backend for MacBackend {
    fn monitors(&mut self) -> Result<Vec<Monitor>, String> {
        self.on_main(|mtm| {
            let screens = NSScreen::screens(mtm);
            let mut out = Vec::new();
            for i in 0..screens.count() {
                let s = screens.objectAtIndex(i);
                let frame = s.frame();
                let scale = s.backingScaleFactor();
                let w = (frame.size.width * scale).round();
                let h = (frame.size.height * scale).round();
                let Some(id) = screen_number(&s) else {
                    continue;
                };
                if w >= 1.0 && h >= 1.0 {
                    out.push(Monitor {
                        id,
                        width: w as u32,
                        height: h as u32,
                    });
                }
            }
            out
        })
    }

    fn get(&mut self, monitor_id: &str) -> Result<Option<PathBuf>, String> {
        let id = monitor_id.to_string();
        self.on_main(move |mtm| {
            let screen = screen_at(mtm, &id)?;
            let ws = NSWorkspace::sharedWorkspace();
            let url = ws.desktopImageURLForScreen(&screen)?;
            file_path_of(&url)
        })
    }

    fn set(&mut self, monitor_id: &str, path: &Path) -> Result<(), String> {
        let id = monitor_id.to_string();
        let path = path.to_string_lossy().to_string();
        self.on_main(move |mtm| {
            let screen = screen_at(mtm, &id).ok_or_else(|| "no such screen".to_string())?;
            let ws = NSWorkspace::sharedWorkspace();
            let url = NSURL::fileURLWithPath(&NSString::from_str(&path));
            let options = ws
                .desktopImageOptionsForScreen(&screen)
                .unwrap_or_default();
            // SAFETY: options は NSWorkspace 自身が返した辞書（またはその型の空の辞書）で、
            // キーと値の型は API の約束どおり。
            unsafe { ws.setDesktopImageURL_forScreen_options_error(&url, &screen, &options) }
                .map_err(|e| e.localizedDescription().to_string())
        })?
    }

    fn background_is_picture(&mut self) -> Option<bool> {
        // すべての画面の画像が読めるファイルなら 1 枚の画像とみなす（動く壁紙は読めるファイルでない）。
        // メインスレッドが応答しないときは `None`（一時的な失敗で、次の機会に確かめ直す）。
        self.on_main(|mtm| {
            let screens = NSScreen::screens(mtm);
            let ws = NSWorkspace::sharedWorkspace();
            (0..screens.count()).all(|i| {
                let s = screens.objectAtIndex(i);
                ws.desktopImageURLForScreen(&s)
                    .and_then(|u| file_path_of(&u))
                    .is_some_and(|p| p.is_file())
            })
        })
        .ok()
    }

    fn position(&mut self) -> Option<i32> {
        None // options は set のたびにそのときの値を渡すので、別に保存しない
    }

    fn set_position(&mut self, _position: i32) -> Result<(), String> {
        Ok(())
    }

    fn is_os_managed_copy(&self, _path: &Path) -> bool {
        false
    }
}
