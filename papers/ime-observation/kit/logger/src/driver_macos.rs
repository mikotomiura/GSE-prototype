//! Placeholder for the macOS driver. The implementation is added by later work and tracked in its own
//! manifest, not in `manifest.json`.

use crate::driver_api::{DriverCtx, DriverHandle};

pub fn start(_ctx: DriverCtx) -> Result<DriverHandle, String> {
    Err("the macOS driver is not implemented yet".to_string())
}
