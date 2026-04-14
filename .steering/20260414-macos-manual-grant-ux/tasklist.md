# タスクリスト

## 実装
- [x] lib.rs: open_accessibility_settings コマンド追加
- [x] Dashboard.tsx: 手動付与手順 UI + ボタン
- [x] バージョンバンプ 0.1.20 → 0.1.21

## テスト
- [x] cargo check — 成功
- [x] npx tsc --noEmit — 成功

## レビュー
- [x] code-reviewer — HIGH 1件対応済み (invoke エラーハンドリング)、capabilities は false positive
- [x] security-checker — (code-reviewer で同時確認、コマンドインジェクションリスクなし)

## 完了処理
- [ ] git commit + push + tag v0.1.21
