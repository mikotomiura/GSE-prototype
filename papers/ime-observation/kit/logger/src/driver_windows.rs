//! Windows ドライバの差し込み口（空）。中身は issue 013 / 014。
//! ⚠️ このファイルは `manifest.json` に載せない（013 / 014 が自分の `manifest.windows.json` に載せる）。

use crate::driver_api::DriverCtx;

pub fn start(_ctx: DriverCtx) -> Result<std::thread::JoinHandle<()>, String> {
    Err("Windows ドライバは未実装（issue 013 / 014）".to_string())
}
