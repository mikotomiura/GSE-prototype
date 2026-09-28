//! macOS ドライバの差し込み口（空）。中身は issue 012。
//! ⚠️ このファイルは `manifest.json` に載せない（012 が自分の `manifest.macos.json` に載せる）。

use crate::driver_api::DriverCtx;

pub fn start(_ctx: DriverCtx) -> Result<std::thread::JoinHandle<()>, String> {
    Err("macOS ドライバは未実装（issue 012）".to_string())
}
