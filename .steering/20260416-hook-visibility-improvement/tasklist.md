# タスクリスト

## 実装

### Preflight 層
- [x] `.claude/hooks/preflight.sh` を新規作成
- [x] `.claude/settings.json` の UserPromptSubmit を preflight.sh に差し替え

### Guard 層
- [x] `.claude/hooks/pre-edit-steering.sh` に [guard] PASS 出力を追加
- [x] `.claude/hooks/pre-edit-banned.sh` に [guard] PASS 出力を追加

### Report 層
- [x] `.claude/hooks/post-fmt.sh` を新規作成（cargo fmt + 変更報告）
- [x] `.claude/settings.json` の PostToolUse を post-fmt.sh に差し替え

## テスト
- [x] preflight: タスクあり状態で正常表示確認
- [x] guard PASS: 正常な .rs 編集で [guard] PASS 表示確認
- [x] guard BLOCKED: println! を含む編集で BLOCKED 表示確認
- [x] post-fmt: フォーマット不要時は無言確認

## ドキュメント
- [x] `CLAUDE.md` の hook セクション更新（3層構造の説明）
- [x] `docs/development-guidelines.md` §9 更新（Preflight/Guard/Report 層の詳細）

## 完了処理
- [x] git commit (ee15a5b feat(hooks): 3-layer preflight dashboard)
