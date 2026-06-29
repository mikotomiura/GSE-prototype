# 設計判断

## D-audit-1: 本セッションは「計装＋手順書」に限定し、恒久修正は Windows 計測後にする
- 背景: requirement.md/hypotheses.md が「推測で直さず計測で白黒つける」を要求。観測 OS は Windows
  実機で、当環境 (macOS) では再現も Windows 型チェックもできない。
- 判断: 読み取り専用の窓状態 readback 計装 (Rust debug command + Overlay.tsx ログ) と状態行列 runbook
  までを実装し、真因確定 (H1-H5) と修正は Windows 実機計測の次段に回す。
- 根拠: 計測前に投機修正を入れると測定がノイズで汚れる。計装は二重 debug gate で被験者ビルド no-op。

## D-audit-2: cross-review H1 — windows クレート版数不一致 (0.58 vs 0.61) を生ポインタ橋渡しで解消
- 背景: cross-review (Claude+Codex 一致) が、`win.hwnd()` は Tauri 依存の windows 0.61 の HWND を返す
  一方、本クレート直 import の `GetWindowLongPtrW` は windows 0.58 の HWND を要求し、0.x の異 minor は
  semver 非互換で型統一されない → Windows でコンパイルエラー、と指摘 (Cargo.lock に両版共存を確認)。
- 判断: Cargo.toml の windows を 0.61 へ引き上げる (Option A) のではなく、生ポインタ経由で 0.58 HWND を
  構築して橋渡しする (Option B): `let hwnd058 = HWND(hwnd.0);`。
- 根拠:
  - 両版の HWND は **どちらも `pub struct HWND(pub *mut core::ffi::c_void)`** とレジストリ source で確認。
    `.0` は公開フィールドで同一レイアウト → transmute 不要・安全に再構築できる。
  - `GetWindowLongPtrW<P0: Param<HWND(0.58)>>` は 0.58 HWND 値を受理する (source で bound 確認)。
  - Option A (0.61 引き上げ) は hook_windows.rs/ime_windows.rs の 0.58→0.61 破壊的変更を伴い、macOS では
    型チェック不能でリスク大。Option B は本コマンド内に閉じた局所変更。
- 検証: Tauri build script (winres/llvm-rc) が macOS で動かず本体の Windows check は不可だったため、
  橋渡し部のみを切り出した scratch crate (windows 0.58 + 0.61 併存) を
  `cargo check --target x86_64-pc-windows-msvc` で **コンパイル成功** を確認。本体の最終 Windows ビルドは
  CI で確定する。
- H2 (GetWindowLongPtrW の 0 返し曖昧性): 透明 always_on_top layered 窓の EXSTYLE は常に非0 のため debug
  用途では実害なしと判断し、SetLastError ダンスは入れずコメントで明記。
- X1 (debug_assertions で囲む): 既存 debug command 群 (force_wall 等) と同様 ensure_debug_enabled() のみで
  揃える。窓ジオメトリは非機密で security-checker も clear 済みのため不採用 (一貫性優先)。
