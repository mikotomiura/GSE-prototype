# 次セッション開始プロンプト（macOS オーバーレイ idle 残存バグ）

このタスクは **新しいセッションで実装**する。コピペで開始できるよう以下を渡す。

---

macOS で、被験者が他アプリ（ブラウザの Google Docs 等）で作業中に「透明なオーバーレイ窓が
画面に残存し背後クリックを奪う」バグを修正する。根本原因と修正方針は
`.steering/20260629-macos-overlay-idle-clickthrough/`（requirement.md / design.md）に確定済み。

## 一言で言う根本原因
オーバーレイ idle 処理（`src/components/Overlay.tsx:167-174`）が `ignoresMouseEvents=YES` に
頼るだけで**窓を画面外退避も縮小もしない**。Wall 後は全画面、Probe 後は右上 box のまま
透明窓が残り、透過が効かないと背後クリックを奪う。revert された card 窓方式が持っていた
`画面外(-20000,-20000)` 退避が失われたのが直接原因。

## やること
1. `architecture-rules` / `intervention-design` / `typescript-standards` Skill を Read。
2. `Overlay.tsx` の idle 分岐に **画面外退避（setPosition(-20000,-20000)、必要なら setSize 1x1）** を追加。
   退避は `setOverlayInteractive(false)` の成否と**独立**に実行（panel 変換失敗時のブロック増幅条件を断つ）。
   統合 effect の `cancelled` ガードと整合させ、show（box/全画面）を後から潰さない順序にする。
3. `src-tauri/src/overlay_panel.rs:55` の「画面外退避するので…」コメントを実装に合わせて修正。
4. （推奨）Rust に `ignoresMouseEvents` 読み返し debug command を追加（回帰番兵）。
5. `cargo build --target aarch64-apple-darwin` → 実機 smoke（runbook 化、design.md のチェックリスト）。
6. `/finish-task`（code-reviewer + security-checker + /cross-review 必須）。
7. 検証後 memory `macos-overlay-clickthrough-bug` を更新。

## 非回帰で死守する点（D7-D13・前回の苦労）
- Probe カードはカード内クリック可・カード外は透過（非ブロック設計）。
- Wall は全画面ブロック維持。
- 前面アプリのタイピングフォーカスを奪わない（D12: resign_key）。
- `window.hide()`/`orderOut` は使わない（D10: webview JS 休眠で probe 取りこぼし）。
- `maximize()`/`unmaximize()`/`setStyleMask` 再適用はしない（D8: NSPanel+WKWebView クラッシュ）。
- Windows 非回帰。

## 参考
- 厳密 Web 調査（出典付き）: tauri#13070 / #11461 / wry#1266（透明 WebView がクリックを奪う）、
  Apple Forums 814798（Tahoe 26.3-RC/26.4-beta の OS 退行・本機 26.5.1 GA では主因でない）。
- 前回タスク: `.steering/20260625-macos-overlay-clickthrough-fix/`（D7-D13、card 窓方式の revert 経緯）。
