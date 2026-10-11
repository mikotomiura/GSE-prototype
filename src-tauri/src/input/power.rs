//! スリープの直前と復帰の通知（EH3 の肖像の「終わり」と「始まり」・`.steering/20261011-portrait-eh3-impl/decisions.md`
//! 判断 3 #2）。OS 依存は `power_{windows,macos}.rs` に閉じ、ここは受け口だけ。
//!
//! ⚠️ 何も記録しない: 通知は肖像の層の終わり・始まりにだけ使い、NDJSON・applog に出さない
//! （スリープの区間は打鍵の記録の空白からも組み直せる・要件 R-9）。
//! ⚠️ コールバックの中は `try_send` だけ（`hook-constraints`）。

use std::sync::OnceLock;

use crossbeam_channel::Sender;

/// 電源の出来事。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PowerEvent {
    /// これからスリープに入る（Windows は約 2 秒の猶予しかない）。
    Suspending,
    /// スリープから戻った。
    Resumed,
}

/// 電源の出来事を送る先。
pub static POWER_TX: OnceLock<Sender<PowerEvent>> = OnceLock::new();

#[cfg(target_os = "windows")]
#[path = "power_windows.rs"]
mod imp;

#[cfg(target_os = "macos")]
#[path = "power_macos.rs"]
mod imp;

#[cfg(not(any(target_os = "windows", target_os = "macos")))]
mod imp {
    pub fn start() {}
}

/// 通知の購読を始める。★ 送信端を先に登録する。2 回目は何もしない。
pub fn start(tx: Sender<PowerEvent>) {
    if POWER_TX.set(tx).is_err() {
        return;
    }
    imp::start();
}
