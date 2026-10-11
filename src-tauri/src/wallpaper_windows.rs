//! Windows の壁紙の API（`IDesktopWallpaper`）。EH3 の肖像の層の OS 依存の部分。
//!
//! EH2 の試作 `experiments/20261009-portrait-eh2/windows/eh2_wallpaper.ps1` の移植:
//! - モニタごとの設定と読み戻しは `IDesktopWallpaper` の `SetWallpaper` / `GetWallpaper`。
//! - 背景の種類はレジストリ `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Wallpapers` の
//!   `BackgroundType`（0 = 画像・1 = 単色・2 = スライドショー・3 = スポットライト）と、
//!   `GetStatus` の `DSS_SLIDESHOW`。
//! - 元の画像が `%APPDATA%\Microsoft\Windows\Themes` の写しなら、壁紙を替えた瞬間に上書きされるので戻せない。
//!
//! ⚠️ COM は呼び出したスレッドで初期化する（`wallpaper::Manager` を持つ専用のスレッドで作る）。
//! ⚠️ 何も記録しない（`wallpaper.rs` のモジュールの doc）。

use std::path::{Path, PathBuf};

use windows::core::{HSTRING, PWSTR};
use windows::Win32::System::Com::{
    CoCreateInstance, CoInitializeEx, CoTaskMemFree, CLSCTX_ALL, COINIT_APARTMENTTHREADED,
};
use windows::Win32::System::Registry::{RegGetValueW, HKEY_CURRENT_USER, RRF_RT_REG_DWORD};
use windows::Win32::UI::Shell::{
    DesktopWallpaper, IDesktopWallpaper, DESKTOP_WALLPAPER_POSITION, DSS_SLIDESHOW,
};

use crate::wallpaper::{Backend, Monitor};

/// `IDesktopWallpaper` を持つ backend。作ったスレッドでだけ使う（`Send` ではない）。
///
/// STA で初期化するがメッセージは回さない: `IDesktopWallpaper` の呼び出しは同期で、このスレッドへの
/// コールバックを受けないため。スレッドの寿命はプロセスと同じなので `CoUninitialize` は呼ばない。
pub struct WindowsBackend {
    api: IDesktopWallpaper,
}

/// COM が返した文字列を `String` にして解放する。
///
/// # Safety
/// `p` は COM が `CoTaskMemAlloc` で確保して返した（またはヌルの）文字列であること。
unsafe fn take_pwstr(p: PWSTR) -> Option<String> {
    if p.is_null() {
        return None;
    }
    let s = p.to_string().ok();
    CoTaskMemFree(Some(p.0 as *const core::ffi::c_void));
    s
}

impl WindowsBackend {
    /// このスレッドで COM を初期化し、`DesktopWallpaper` を作る。
    pub fn new() -> Result<Self, String> {
        // SAFETY: 専用のスレッドで 1 回だけ呼ぶ。すでに初期化済み（S_FALSE）でも続けてよい。
        let hr = unsafe { CoInitializeEx(None, COINIT_APARTMENTTHREADED) };
        if hr.is_err() {
            return Err(format!("CoInitializeEx failed: {hr:?}"));
        }
        // SAFETY: CLSID と IID は windows crate の定義どおり。戻り値はスマートポインタで解放される。
        let api: IDesktopWallpaper =
            unsafe { CoCreateInstance(&DesktopWallpaper, None, CLSCTX_ALL) }
                .map_err(|e| format!("CoCreateInstance(DesktopWallpaper) failed: {e}"))?;
        Ok(Self { api })
    }

    fn background_type() -> Option<u32> {
        let key = HSTRING::from(r"Software\Microsoft\Windows\CurrentVersion\Explorer\Wallpapers");
        let name = HSTRING::from("BackgroundType");
        let mut data: u32 = 0;
        let mut size = std::mem::size_of::<u32>() as u32;
        // SAFETY: 出力先は u32 1 個ぶんで、その大きさを `size` で渡している。
        let rc = unsafe {
            RegGetValueW(
                HKEY_CURRENT_USER,
                &key,
                &name,
                RRF_RT_REG_DWORD,
                None,
                Some(&mut data as *mut u32 as *mut core::ffi::c_void),
                Some(&mut size),
            )
        };
        rc.is_ok().then_some(data)
    }
}

impl Backend for WindowsBackend {
    fn monitors(&mut self) -> Result<Vec<Monitor>, String> {
        // SAFETY: COM の呼び出し。返る文字列は `take_pwstr` で解放する。
        let count = unsafe { self.api.GetMonitorDevicePathCount() }.map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for i in 0..count {
            // SAFETY: 同上。
            let Some(id) = (unsafe {
                self.api
                    .GetMonitorDevicePathAt(i)
                    .ok()
                    .and_then(|p| take_pwstr(p))
            }) else {
                continue;
            };
            let hid = HSTRING::from(id.as_str());
            // SAFETY: 同上。いま接続していないモニタは RECT が取れない（飛ばす）。
            let Ok(r) = (unsafe { self.api.GetMonitorRECT(&hid) }) else {
                continue;
            };
            let (w, h) = (r.right - r.left, r.bottom - r.top);
            if w <= 0 || h <= 0 {
                continue;
            }
            out.push(Monitor {
                id,
                width: w as u32,
                height: h as u32,
            });
        }
        Ok(out)
    }

    fn get(&mut self, monitor_id: &str) -> Result<Option<PathBuf>, String> {
        let hid = HSTRING::from(monitor_id);
        // SAFETY: COM の呼び出し。返る文字列は `take_pwstr` で解放する。
        let p = unsafe { self.api.GetWallpaper(&hid) }.map_err(|e| e.to_string())?;
        // SAFETY: COM が返した文字列。
        let s = unsafe { take_pwstr(p) };
        Ok(s.filter(|s| !s.is_empty()).map(PathBuf::from))
    }

    fn set(&mut self, monitor_id: &str, path: &Path) -> Result<(), String> {
        let hid = HSTRING::from(monitor_id);
        let hpath = HSTRING::from(path.as_os_str());
        // SAFETY: COM の呼び出し。引数の文字列はこの呼び出しの間だけ生きていればよい。
        unsafe { self.api.SetWallpaper(&hid, &hpath) }.map_err(|e| e.to_string())
    }

    fn background_is_picture(&mut self) -> Option<bool> {
        // SAFETY: COM の呼び出し。
        // 取得に失敗したときは「分からない」（一時的な COM の失敗で本人の差し替えと取り違えない）
        let slideshow = unsafe { self.api.GetStatus() }.ok()?.0 & DSS_SLIDESHOW.0 != 0;
        let picture_type = matches!(Self::background_type(), Some(0) | None);
        Some(!slideshow && picture_type)
    }

    fn position(&mut self) -> Option<i32> {
        // SAFETY: COM の呼び出し。
        unsafe { self.api.GetPosition() }.ok().map(|p| p.0)
    }

    fn set_position(&mut self, position: i32) -> Result<(), String> {
        // SAFETY: COM の呼び出し。値は以前 `GetPosition` で読んだもの。
        unsafe { self.api.SetPosition(DESKTOP_WALLPAPER_POSITION(position)) }
            .map_err(|e| e.to_string())
    }

    fn is_os_managed_copy(&self, path: &Path) -> bool {
        let Some(appdata) = std::env::var_os("APPDATA") else {
            return true; // 確かめられないときは戻せない側に倒す
        };
        let themes = PathBuf::from(appdata).join(r"Microsoft\Windows\Themes");
        path.to_string_lossy()
            .to_lowercase()
            .starts_with(&themes.to_string_lossy().to_lowercase())
    }
}
