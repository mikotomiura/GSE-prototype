//! シム: GSE の `src-tauri/src/input/hook.rs` のうち、逐語コピーした 3 ファイル
//! （`ime_compose.rs` / `ime_cloak.rs` / `ime_mode.rs`）が参照する**定数と Atomic だけ**。
//!
//! ⚠️ 値と型は GSE の `hook.rs` と同じでなければならない（`check_manifest.py --against-gse` が照合する）。
//! ⚠️ フックのコールバック・チャネル・OS API はここに無い（ドライバは `driver_*.rs`）。
//!
//! 変換セッションの状態は、GSE と同じくここの Atomic で監視ループ（`main.rs`）へ渡す。

use std::sync::atomic::{AtomicBool, AtomicU32, AtomicU64};

pub const VK_DBE_ALPHANUMERIC: u32 = 0xF0;
pub const VK_DBE_KATAKANA: u32 = 0xF1;
pub const VK_DBE_HIRAGANA: u32 = 0xF2;
pub const VK_DBE_SBCSCHAR: u32 = 0xF3;
pub const VK_DBE_DBCSCHAR: u32 = 0xF4;
pub const VK_KANJI: u32 = 0x19;

pub static IME_ACTIVE: AtomicBool = AtomicBool::new(false);
pub static IME_COMPOSITION_START_MS: AtomicU64 = AtomicU64::new(0);
pub static IME_SHADOW_DWELL_MS: AtomicU64 = AtomicU64::new(0);
pub static IME_CANDIDATE_NAV_COUNT: AtomicU32 = AtomicU32::new(0);
pub static IME_SHADOW_ABANDON: AtomicBool = AtomicBool::new(false);
pub static IME_SHADOW_READY: AtomicBool = AtomicBool::new(false);
pub static IME_COMPOSING: AtomicBool = AtomicBool::new(false);
pub static IME_COMPOSE_NAV: AtomicU32 = AtomicU32::new(0);
