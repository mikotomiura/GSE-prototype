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

## D-audit-3: Windows 実機計測の結論 — 真因は「idle 残存」でなく「カード box の透明余白」
- 計測 (GSE_log_issue.docx・gse_20260629_005937): **退避は Windows で完全に機能**。probe→idle/nudge→idle/
  wall→idle すべてで `offscreen=true`(x=-20000, w=17×10) + `ex_transparent=true`。→ H1/H4 棄却、退避は健全。
- 唯一の on-screen idle 行 (idle-after-1500ms=offscreen=false) は probe→idle の**遅延タイマーが正規表示の
  Nudge を拾った計装ノイズ** (真の上書き H2/H3 ではない)。
- ユーザー確認: クリックを奪われたのは「**カード(probe/Nudge)表示中**」。widget-show ログ
  `w=406 h=439 ex_transparent=false` = box(406×439) がカード実寸(~358×~300)より大きく、**透明余白が
  Windows でクリックを奪っていた** (#11461: 透明 WebView2 窓は透明ピクセルでもクリック捕捉)。
  → 真因は「idle 残存」ではなく「カード box の透明余白」。framing を訂正。

## D-audit-4: 修正方針 — overlay 窓をカード実寸ちょうどに縮める (窓=カード=透明余白ゼロ)
- 退避(idle)は健全なので触らない。widget(カード表示)時の box を**カード実寸**へ縮め、透明余白を物理的に消す。
  Windows は透明部分を透過できないため、これが唯一の堅牢策 (実寸縮小)。
- 実装: ResizeObserver で `offsetWidth/offsetHeight` (CSS transform 非依存=pop-in scale で縮小値を拾わない)
  を測り、窓を実寸へ setSize。カード CSS を viewport 単位 (100vw/100vh) から切り離し
  (nudge width 340px固定 / probe maxHeight 600px固定)、窓縮小↔カード縮小の無限ループを遮断。
- レビュー対応:
  - code-reviewer HIGH: フォールバックが実カードより小さいと初回フレームでボタンクリップ=較正喪失 →
    **フォールバックは必ず実カードより大きい側** (PROBE 380×470 / NUDGE 360×250。過大は自己回復・過小は到達不能)。
  - code-reviewer MEDIUM: maxHeight 固定で画面収まり保証を失う → 窓を **monitor clamp** (winH=min(winH, monH-2*margin))。
  - cross-review (Claude+Codex 一致) HIGH: `.nudge-card overflow:hidden` + clamp で dismiss クリップの逃げ場なし →
    `.nudge-card` を `overflow-y:auto` 化 (ProbeCard と同じ保険)。
- 検証: tsc green / vite build green / code-reviewer(再)・security-checker・cross-review 全解消。
  Windows 実機での最終確認 (カード表示中にカード外クリックが背後へ通る) はユーザーの dev 機で。
