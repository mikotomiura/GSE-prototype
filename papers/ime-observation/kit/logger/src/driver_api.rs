//! ドライバ（OS ごとの打鍵の取得）と核（監視ループ・書き出し）の**境界の型**。
//!
//! ⚠️ 012（macOS）/ 013・014（Windows）はこの形に合わせて書き、`main.rs` を触らない。
//! 各ドライバは `pub fn start(ctx: DriverCtx) -> Result<DriverHandle, String>` を持つ。
//!
//! - ドライバは打鍵を `KeyEvent` にして `ctx.keys` へ送る（`vk` は Windows の VK に写した値・`t` は壁時計 ms）。
//! - 変換セッションの状態は `input::hook`（シム）の Atomic で受け渡す（GSE と同じ）。
//! - ⚠️★ **停止の契約**（issue 011 merge ゲートレビュー item 4）: `ctx.stop` が立ったら、ドライバは
//!   自分のスレッドを [`STOP_DEADLINE_MS`] 以内に終えること（タイマーや Windows なら
//!   `MsgWaitForMultipleObjects` 等で `ctx.stop` を定期的に見る）。核のループは
//!   `JoinHandle::is_finished()` でドライバの生死を見張り、想定外にスレッドが終わっていればエラーで
//!   終わる（`ctx.keys` の Sender が drop された場合は `mpsc::RecvTimeoutError::Disconnected` でも
//!   検出されるが、`is_finished()` はそれより早く・打鍵を一度も送らないまま死んだ場合にも効く）。
//! - ⚠️★ **候補窓の観測の差し込み口**（issue 011 merge ゲートレビュー item 1）: ドライバは
//!   [`DriverHandle::candidate_window_observer`] に `Some(Box<dyn FnMut() -> bool + Send>)` を
//!   入れて返してよい。核の監視ループ（`main.rs` の `Monitor::poll` / `run_cycle`）は毎周期
//!   これを 1 回呼び、その戻り値を「候補窓が開いているか」として使う。`None`（既定）なら
//!   核は `input::hook::IME_ACTIVE.load(Acquire)` を使う（旧実装と同じ・macOS は GSE でも
//!   これが実体 —— `ime_macos.rs:44`）。
//!
//!   ⚠️★★★ **呼び出しスレッド**: この観測関数は `Monitor::poll` を呼ぶスレッド
//!   （`main.rs::run()` のメインループのスレッド。ドライバ自身の打鍵取得スレッドとは**別**でよい）
//!   から呼ばれる。GSE の `ImeMonitor`（`ime_windows.rs`）は UIAutomation の COM
//!   （`CoInitializeEx` + `CoCreateInstance`）を、`ImeMonitor::new()` の呼び出し時に
//!   **その呼び出し元スレッドの中で**初期化しており（`ime_windows.rs:33-48`）、
//!   COM オブジェクト（`IUIAutomation`）はそのスレッドでしか安全に使えない
//!   （別スレッドから呼ぶとハングするか失敗する）。→ ★ Windows ドライバ（013 / 014）が
//!   UIAutomation を使う実装を返すなら、COM の初期化は**この観測関数の初回呼び出し時に、
//!   呼び出し元スレッド上で**行うこと（`ctx` を渡すスレッドと揃える必要はない）。

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

/// ドライバの起動結果。
#[allow(dead_code)]
pub struct DriverHandle {
    /// ドライバのスレッド。`ctx.stop` を立ててから [`STOP_DEADLINE_MS`] 以内に終わること。
    pub thread: std::thread::JoinHandle<()>,
    /// 候補窓が開いているかの観測関数（無ければ核が既定＝`IME_ACTIVE` の読み取りを使う）。
    /// 呼び出しスレッドの注意はこのファイル冒頭を参照。
    pub candidate_window_observer: Option<Box<dyn FnMut() -> bool + Send>>,
}

impl DriverHandle {
    /// 観測関数を持たないドライバ（差し込み口だけの実装など）用の簡易コンストラクタ。
    /// ⚠️ 012〜014 が実装するまで呼び手が無い（差し込み口はエラーを返すだけ）。
    #[allow(dead_code)]
    pub fn new(thread: std::thread::JoinHandle<()>) -> Self {
        Self {
            thread,
            candidate_window_observer: None,
        }
    }
}

/// ドライバが `ctx.stop` を見てスレッドを終えるまでに許される最大遅れ（ms）。
/// ★ 核はこれを強制はしない（`JoinHandle::is_finished()` の定期チェックで検出する側）。
/// ここは契約の明文化であり、ドライバの実装（012〜014）が満たすべき上限。
#[allow(dead_code)]
pub const STOP_DEADLINE_MS: u64 = 500;
