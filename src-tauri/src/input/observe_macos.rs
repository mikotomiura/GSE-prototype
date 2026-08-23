// O1 (R3-a) の非打鍵チャネル — macOS 実装。
//
// ## ⚠️★★★ 現状: **未実装（明示的なスタブ）**
//
// ★ 先例: `sensors_macos.rs`（CoreMotion を「stub (not available)」と明記して置いている）。
//
// ### ⚠️ なぜスタブなのか（★ 「忘れている」のではない）
//
// | # | 理由 |
// |---|---|
// | 1 | ⚠️★★★ **本タスクの作業機は Windows のみ**であり、`NSWorkspace` 通知 / 2 本目の `CGEventTap` / `IsSecureEventInputEnabled` / `TISCopyCurrentKeyboardLayoutInputSource` の FFI を **1 行も型検査できない**。★ `cargo check --target aarch64-apple-darwin` は Objective-C コンパイラが要るため本機では通らない（2026-08-23 実測） |
// | 2 | ⚠️ 検証されていない FFI を `input/` に置くと、**macOS の CI が落ちる**か、さらに悪く **黙って動かない計器**になる |
// | 3 | ★ ADR-013 **D1** は「**計器が無い**」を正当な状態として設計に入れている —— [`FOCUS_AVAILABLE`] / [`POINTER_AVAILABLE`] を `false` にすれば、macOS のログは **「測っていない」と自己申告**する。⚠️ 0 行を「信号が無かった」と誤読されない |
// | 4 | ⚠️ **ADR-016 D9 の前提 1（mac の同時稼働の実機確認）が未了**である。★ 実機確認より先に実装しても、確認で落ちれば作り直しになる |
//
// ### ★ 実装するときに必要なもの（⚠️ 調査済み・ADR-014 D4 の表）
//
// - **L-c**: `NSWorkspace.didActivateApplicationNotification`（★ **TCC 不要**）。
//   ⚠️ 通知オブジェクトから **アプリ識別子を読まない**（時刻だけ取る）。
// - **L-b**: ⚠️★★★ **既存 tap とは *別 tap*** に `MouseMoved` / `*Dragged` / `ScrollWheel` を張る。
//   ★ 相乗りさせると**打鍵観測を巻き込んで失効する**。
// - **`secure_input`**: `IsSecureEventInputEnabled()`（Carbon・`#[link]` 1 行）を 1Hz で確認。
// - **レイアウト**: `TISCopyCurrentKeyboardLayoutInputSource` → 識別子のみ。
//   ⚠️★★★ **`UCKeyTranslate` を呼ばない。**
//
// ⚠️ 実装する前に **ADR-016 D9 前提 1（tap 2 系統の実機確認）** を閉じること。

/// ⚠️ macOS では **フォーカス遷移の計器が無い**（★ 0 行は「測っていない」の意味）。
pub const FOCUS_AVAILABLE: bool = false;
/// ⚠️ macOS では **ポインタの計器が無い**（同上）。
pub const POINTER_AVAILABLE: bool = false;

/// 何もしない。★ スレッドも起こさない。
pub fn start() {
    tracing::info!(
        "O1: non-keystroke observation is not implemented on macOS yet. \
         focus_transition / pointer_bin rows will not be emitted; \
         capabilities declares them as absent (ADR-013 D1)."
    );
}

/// ⚠️ 未実装。★ `None` は「計器が無い」であって「配列が不明」ではない。
pub fn keyboard_layout_id() -> Option<String> {
    None
}

/// ⚠️ 未実装。★ `None` は「計器が無い」であって「secure ではない」ではない。
pub fn secure_input_enabled() -> Option<bool> {
    None
}
