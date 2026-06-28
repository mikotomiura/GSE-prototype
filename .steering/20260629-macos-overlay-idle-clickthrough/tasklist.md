# タスクリスト: macOS オーバーレイ idle 残存クリック阻害の修正

## 実装
- [x] Skill 参照 (architecture-rules / intervention-design / typescript-standards)
- [x] `Overlay.tsx` idle 分岐に画面外退避 (setPosition(-20000,-20000) + setSize(1x1)) を追加
- [x] 退避は `setOverlayInteractive(false)` の成否と独立 (try/catch 分離)
- [x] `cancelled` ガードで stale 退避が show を後から潰さない順序にする
- [x] show 経路のモニタ解決を `currentMonitor() ?? primaryMonitor()` (resolveShowMonitor) へ
      (退避後 currentMonitor が null を返す HIGH 退行対策・code-reviewer 指摘)
- [x] `overlay_panel.rs:55` の嘘コメントを実装に合わせて修正
- [x] (任意・推奨) ignoresMouseEvents 読み返し debug command → 対象プロパティ違い + objc FFI
      追加リスクで **defer** (decisions.md D4 に理由記録)

## 検証
- [x] `npx tsc --noEmit` green
- [x] `cargo build --target aarch64-apple-darwin` green (警告は既存の unused var のみ)
- [x] code-reviewer PASS / security-checker リスクなし / cross-review (Claude+Codex) コード修正不要
- [ ] **実機 smoke (runbook.md 1-10)** — 物理 macOS 機が必要・研究者が手動実行 (本セッションでは未実施)

## 完了処理
- [x] steering 最終化 (requirement/design/decisions/runbook/tasklist)
- [ ] commit (scoped) → 実機 smoke green 後に main へマージ
- [x] memory `macos-overlay-clickthrough-bug` を「idle 残存も解決 (smoke 保留)」へ更新
