# タスクリスト

## 準備
- [x] 関連する docs を読む (§10, sync-session.*)
- [x] design.md 記入・承認

## 実装
- [x] `scripts/sync-all.sh` (macOS/Linux) を作成
- [x] `scripts/sync-all.ps1` (Windows) を作成

## 検証
- [x] dry-run (--no-commit) で動作確認
- [x] 本番実行: 7件の metrics 生成 + gse-dataset push 完了

## レビュー
- [x] code-reviewer によるレビュー (HIGH 2件 + MEDIUM 1件 対応済み)

## ドキュメント
- [x] docs/development-guidelines.md §10.2 にバッチ同期の使い方を追記

## 完了処理
- [x] /finish-task (be9006c)
