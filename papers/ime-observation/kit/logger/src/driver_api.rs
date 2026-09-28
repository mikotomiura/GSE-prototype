//! ドライバ（OS ごとの打鍵の取得）と核（監視ループ・書き出し）の**境界の型**。
//!
//! ⚠️ 012（macOS）/ 013・014（Windows）はこの形に合わせて書き、`main.rs` を触らない。
//! 各ドライバは `pub fn start(ctx: DriverCtx) -> Result<std::thread::JoinHandle<()>, String>` を持つ。
//!
//! - ドライバは打鍵を `KeyEvent` にして `ctx.keys` へ送る（`vk` は Windows の VK に写した値・`t` は壁時計 ms）。
//! - 変換セッションの状態は `input::hook`（シム）の Atomic で受け渡す（GSE と同じ）。
//! - `ctx.stop` が立ったらスレッドは終わる。

use std::sync::atomic::AtomicBool;
use std::sync::mpsc::Sender;
use std::sync::Arc;

/// 打鍵 1 件。⚠️ 文字は持たない（VK は種別に畳んでから書き出す）。
pub struct KeyEvent {
    /// 壁時計 ms（Unix epoch）。
    pub t: u64,
    /// Windows の VK に写した値。
    pub vk: u32,
    /// 押下 = `true`・離し = `false`。
    pub press: bool,
}

/// ドライバに渡すもの。（差し込み口が空の間は中身を読む者がいないので dead_code を許す。）
#[allow(dead_code)]
pub struct DriverCtx {
    pub keys: Sender<KeyEvent>,
    pub stop: Arc<AtomicBool>,
}
