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

/// フォーカス遷移 1 回ぶん。
///
/// ⚠️★★★ **時刻と「GSE 自身の窓か」の真偽しか運べない。** ★ 型として「これ以上のものが運べない」形に
/// してある —— HWND・PID・アプリ識別子を運ぼうとしたらコンパイルが通らない（ADR-014 D4 の禁止表）。
/// `own` は自分のプロセスかどうかの 1 bit で、他のアプリを識別しない。
///
/// `own` を使うのは EH3 だけである: GSE の窓（招待の説明と設定の窓）への遷移とそこから戻る遷移を
/// 記録しない（図像を押したことが時刻から読めないようにする・`.steering/20261011-portrait-eh3-impl/decisions.md`
/// 判断 6 #3）。O1 の記録は変えない（`own` は NDJSON に出ない）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct FocusEvent {
    pub t: u64,
    pub own: bool,
}

/// フォーカス遷移を送る先。
pub static FOCUS_TX: OnceLock<Sender<FocusEvent>> = OnceLock::new();

/// 1 秒ビンのポインタ活動を送る先（★ ゼロ抑制済み）。
pub static POINTER_TX: OnceLock<Sender<PointerBin>> = OnceLock::new();

/// `secure_input` の **区間フラグ**（on/off）を送る先。
///
/// ⚠️★★★ **`bool` 1 個しか流れない**（★ `FOCUS_TX` と同じ作法）。
/// ★ 変化したときだけ送る（送出側が edge-detection する。ADR-014 D4 の段1）。
pub static SECURE_INPUT_TX: OnceLock<Sender<bool>> = OnceLock::new();

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
    pub const SECURE_INPUT_AVAILABLE: bool = false;
}

/// ⚠️ 二重に `start()` が呼ばれても `imp::start()` を 1 回しか実行しない
/// （security-checker LOW-L2）。★ `imp::start()`（特に macOS 側）は observer/tap を
/// 設置する副作用を持ち、二重設置すると同じ Atomic カウンタを 2 系統が加算して
/// `pointer_bin`/`focus_transition` の値が水増しされる。
static STARTED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);

/// 観測を開始する。★ 送信端を先に登録してから呼ぶこと。
///
/// ⚠️ 専用スレッドを起こして即座に返る（★ `init_hook` と同じ作法）。
pub fn start(
    focus_tx: Sender<FocusEvent>,
    pointer_tx: Sender<PointerBin>,
    secure_tx: Sender<bool>,
) {
    // ⚠️ 二重初期化しても壊れないように `OnceLock` の失敗は無視する
    //   (★ 2 回目の `start` は「既に動いている」が正しい振る舞い)。
    let _ = FOCUS_TX.set(focus_tx);
    let _ = POINTER_TX.set(pointer_tx);
    let _ = SECURE_INPUT_TX.set(secure_tx);
    if STARTED.swap(true, std::sync::atomic::Ordering::AcqRel) {
        tracing::warn!("O1: observe::start() called more than once; ignoring the second call");
        return;
    }
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
///
/// ⚠️★★★ **`imp::` 経由**にする（`cfg!(target_os = "macos")` の直書きをやめた・
/// security-checker/code-reviewer MEDIUM-4）。★ `FOCUS_AVAILABLE`/`POINTER_AVAILABLE` と
/// 同じ「宣言は `observe` 側の実装有無と 1 対 1」というルールに揃える —— 直書きのままだと
/// 将来 macOS 実装を消しても宣言だけ `true` に残り、過大申告になる。
pub const SECURE_INPUT_AVAILABLE: bool = imp::SECURE_INPUT_AVAILABLE;
