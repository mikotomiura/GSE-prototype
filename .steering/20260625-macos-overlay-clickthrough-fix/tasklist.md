# タスクリスト

## 調査（このセッションで完了）
- [x] 症状の切り分け（debug_force_probe 経由・console 無反応・赤帯なし・両カード・背後アプリ反応）
- [x] CSS 無実を確認（overlay-root/カードは pointer-events:auto）
- [x] 窓構成特定（独立 overlay 窓・transparent/decorations(false)/always_on_top・非フォーカス）
- [x] 真因の方向確定（setIgnoreCursorEvents(false) が macOS で実効化していない）
- [x] codex-consult 実施（盲点 7 点を design.md に反映）
- [x] 次セッション用プロンプト作成（next-session-prompt.md）

## 実装（/fix-bug）
- [x] 第一試行（誤診・撤回）: Rust 側 click-through 権威化（setIgnoresMouseEvents 直接操作＋読み返し）。
      実機で**解決せず** → 真因は ignoresMouseEvents ではないと判明。Rust objc 機構は全撤去。
- [x] 真因確定（ソースレベル調査）: **非 key 窓 + WKWebView acceptsFirstMouse 既定 false**。
      非アクティブ窓のクリックがボタンへ配送されず毎回握りつぶされる（decisions.md D6）。
- [x] 最小修正: overlay 窓生成に `WebviewWindowBuilder::accept_first_mouse(true)` を付与（lib.rs）。
      `setIgnoreCursorEvents` の toggle は従来 JS 経路を維持（このゲートは正しく動作）。
- [x] ビルド検証: cargo build (aarch64) OK / npm run build (tsc && vite build) OK。
- [ ] **macOS 実機操作確認（ユーザー・runbook.md）**: 非アクティブ窓で Probe/Nudge が初回クリックで発火。
      ＋ Windows 非回帰。
- [ ] 完了処理: code-reviewer + security-checker（差分が builder 1 行のため軽量）→ /cross-review → PR。

## 完了処理
- [x] decisions.md（D5 第一試行・D6 真因訂正と最小修正）
- [x] runbook.md（acceptFirstMouse 前提に更新・不足時の NSPanel/専用窓 follow-up 明記）
- [ ] ブランチ fix/macos-overlay-clickthrough で commit・PR（実機検証後）
