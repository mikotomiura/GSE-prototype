# タスクリスト — calibration-blind-dashboard

## 準備
- [x] App.tsx / Dashboard.tsx / Overlay.tsx を読み現状フロー把握
- [x] typescript-standards / data-privacy Skill 参照
- [x] 設計承認 (Step C)

## 実装
- [x] App.tsx: `calibrationMode` state (既定 true) 追加
- [x] App.tsx: Start 画面に「較正モード (モデル出力を非表示)」トグル追加
- [x] App.tsx: `<Dashboard calibrationMode={...} />` を渡す
- [x] Dashboard.tsx: `calibrationMode?: boolean` prop 追加・既定 false
- [x] Dashboard.tsx: Current State / 確率バー / GT カウンタ / info-box / state 色クラスを較正時非表示
- [x] Dashboard.tsx: 較正モード中立注記を追加
- [x] App.css: `.state-calibration` / `.calibration-notice` 最小スタイル

## テスト
- [x] `npm run build` (tsc + vite) で型エラー・any なし → 緑 (built in 492ms)
- [~] `npm run lint` → スクリプト無し (package.json に lint なし)
- [~] `cargo build`: Rust 無変更のため回帰なし (省略・理由明記)
- [x] 手動確認項目を design.md に明記 (GUI headless 不可)

## レビュー
- [~] code-reviewer + security-checker: サブエージェントが 529 Overloaded で複数回失敗 →
      インライン自己レビュー実施 (HIGH なし)。独立レビューは /finish-task の /cross-review で再試行。
- [x] HIGH 指摘への対応: 自己レビューで HIGH なし

## ドキュメント
- [x] docs/functional-design.md に blind calibration dashboard を追記 (機能7 + v0.3 callout)
- [x] glossary に用語追加 (較正モード / calibration mode)

## 完了処理
- [ ] /finish-task で /cross-review (jq 不在なら Claude 単独・理由明記)
- [ ] git commit (選択 add)
