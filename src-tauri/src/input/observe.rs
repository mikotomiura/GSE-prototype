//! ★★★ **O1 の非打鍵チャネル**（R3-a・ADR-014 **D4** の段 1）。
//!
//! ## ★ 何を観測するのか（⚠️ 段 1 の凍結表の中だけ・1 本も足さない）
//!
//! | チャネル | ★ 記録するもの | ⚠️ 記録しないもの |
//! |---|---|---|
//! | **L-c フォーカス遷移** | ★ **遷移が起きた時刻のみ** | ⚠️ HWND / PID / アプリ識別子 / ウィンドウタイトル / 通し番号 |
//! | **L-b ポインタ** | ★ **1 秒ビンの量子化スカラ**（[`crate::analysis::pointer_bin`]）・⚠️ ゼロ抑制 | ⚠️ 座標 / 軌跡 / 符号付き dx,dy / 解像度 |
//! | **`secure_input`**（mac のみ） | ★ 区間フラグ | ⚠️ 中身は一切取らない |
//! | **キーボードレイアウト** | ★ セッション開始時に **1 回だけ**・識別子のみ | ⚠️★★★ `ToUnicodeEx` / `UCKeyTranslate` を**呼ばない** |
//!
//! ## ⚠️★★★ なぜ「時刻だけ」で足りるのか
//!
//! ★ O1 の問いは **`left_observation` の内訳が割れるか**（ADR-014 D9）である。
//! ADR-009 D2 が要求しているのは逐語「**フォーカス喪失・復帰の *時刻***」「**離脱の滞在時間**」
//! であって、⚠️ **どこへ行ったか**ではない。
//! → ★ **「どのアプリか」を持たないことは機能の欠落ではなく、設計そのものである。**
//!
//! ## ★ 層の位置
//!
//! ⚠️ OS API はこのモジュール**配下の `observe_{windows,macos}.rs`** に閉じ込める
//! （`architecture-rules` ルール 2）。★ ここ（`observe.rs`）は OS 非依存の受け口である。
//!
//! ## ⚠️ フックコールバックの制約
//!
//! ★ `hook-constraints` はここでも同じく効く —— **Atomic と `try_send` のみ**。
//! ⚠️ コールバック内でログを書かない / ロックを取らない / 文字列を作らない。

use std::sync::OnceLock;

use crossbeam_channel::Sender;

use crate::analysis::pointer_bin::PointerBin;

/// フォーカス遷移の **時刻** を送る先。
///
/// ⚠️★★★ **`u64` 1 個しか流れない。** ★ 型として「これ以上のものが運べない」形にしてある ——
/// HWND を運ぼうとしたらコンパイルが通らない。
pub static FOCUS_TX: OnceLock<Sender<u64>> = OnceLock::new();

/// 1 秒ビンのポインタ活動を送る先（★ ゼロ抑制済み）。
pub static POINTER_TX: OnceLock<Sender<PointerBin>> = OnceLock::new();

/// ⚠️ 送れずに捨てた観測の累計（★ フォーカス + ポインタの合計）。
///
/// ★ `hook.rs::EVENTS_DROPPED` と同じ作法 —— コールバック内ではカウンタを上げるだけで、
/// ⚠️ **ログは書かない**。
pub static OBSERVATIONS_DROPPED: std::sync::atomic::AtomicU64 =
    std::sync::atomic::AtomicU64::new(0);

// ---------------------------------------------------------------------------
// Platform-specific implementations
// ---------------------------------------------------------------------------

#[cfg(target_os = "windows")]
#[path = "observe_windows.rs"]
mod imp;

#[cfg(target_os = "macos")]
#[path = "observe_macos.rs"]
mod imp;

#[cfg(not(any(target_os = "windows", target_os = "macos")))]
mod imp {
    pub fn start() {}
    pub fn keyboard_layout_id() -> Option<String> {
        None
    }
    pub fn secure_input_enabled() -> Option<bool> {
        None
    }
    pub const FOCUS_AVAILABLE: bool = false;
    pub const POINTER_AVAILABLE: bool = false;
}

/// 観測を開始する。★ 送信端を先に登録してから呼ぶこと。
///
/// ⚠️ 専用スレッドを起こして即座に返る（★ `init_hook` と同じ作法）。
pub fn start(focus_tx: Sender<u64>, pointer_tx: Sender<PointerBin>) {
    // ⚠️ 二重初期化しても壊れないように `OnceLock` の失敗は無視する
    //   (★ 2 回目の `start` は「既に動いている」が正しい振る舞い)。
    let _ = FOCUS_TX.set(focus_tx);
    let _ = POINTER_TX.set(pointer_tx);
    imp::start();
}

/// キーボードレイアウトの **識別子のみ** を返す（例: Windows `00000411` / macOS `com.apple.keylayout.US`）。
///
/// ## ⚠️★★★ なぜ識別子だけなのか
///
/// ★ 文境界の妥当性が配列に依存する —— macOS の keycode は **物理キー位置**なので、
/// Dvorak では `.` が US の `E` の位置に来る。→ ★ **どの配列だったか**が後から要る。
///
/// ⚠️★★★ **文字へ変換しない。** `ToUnicodeEx` / `UCKeyTranslate` を呼んだ瞬間に
/// **入力文字そのものがプロセス内に出現する**（`data-privacy` ルール 1 の一線）。
pub fn keyboard_layout_id() -> Option<String> {
    imp::keyboard_layout_id()
}

/// macOS の `EnableSecureEventInput` が有効か。★ Windows では常に `None`。
///
/// ## ⚠️★★★ なぜ要るのか（★ サーヴェイで判明した必須項目）
///
/// ★ `EnableSecureEventInput` は**システム全体のシングルトン**で、有効な間
/// **tap は「有効」のまま KeyDown だけが届かない**。
/// → ⚠️ **「打鍵ゼロ」と「打鍵が見えない」を混同すると、パスワード入力の直後に
/// 必ず Stuck / Incubation へ倒れる系統的バイアス**が入り、
/// ★ `left_observation` の内訳を割るという O1 の目的そのものを壊す。
pub fn secure_input_enabled() -> Option<bool> {
    imp::secure_input_enabled()
}

/// このビルドで **フォーカス遷移の計器があるか**（ADR-013 D1 の自己刻印用）。
///
/// ⚠️★★★ 「0 行」を「**信号が無かった**」と読ませてよいのは、計器がある場合だけである。
pub const FOCUS_AVAILABLE: bool = imp::FOCUS_AVAILABLE;

/// このビルドで **ポインタの計器があるか**（同上）。
pub const POINTER_AVAILABLE: bool = imp::POINTER_AVAILABLE;

/// このビルドで **`secure_input` の計器があるか**（★ macOS のみ真になりうる）。
pub const SECURE_INPUT_AVAILABLE: bool = cfg!(target_os = "macos");
