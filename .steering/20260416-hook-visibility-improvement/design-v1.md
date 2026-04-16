# 設計 (v1: 初回案)

## 実装アプローチ

既存 hook スクリプトを改修し、全 hook で明示的なステータス表示を追加する。

1. **PreToolUse**: パス時に `[PASS]` メッセージを stdout に出力
2. **UserPromptSubmit**: 固定 echo → 動的シェルスクリプトに差し替え。.steering/ 状態、未コミット変更数、design.md 有無を毎回チェックして表示
3. **PostToolUse**: cargo fmt の実行結果（変更有無）を表示
4. **SessionStart**: 既存の git 情報に加え、有効 hook の一覧を表示
5. **Stop**: 現状維持（すでに明示的）

## 変更対象

### 修正するファイル
- `.claude/settings.json` — UserPromptSubmit の command を外部スクリプトに変更
- `.claude/hooks/pre-edit-steering.sh` — パス時に `[PASS] steering check: ...` を追加
- `.claude/hooks/pre-edit-banned.sh` — パス時に `[PASS] banned pattern check` を追加
- `.claude/hooks/session-start.sh` — hook 一覧表示を追加
- `docs/development-guidelines.md` §9 — hook 動作の説明更新
- `CLAUDE.md` — hook 説明セクション更新

### 新規作成するファイル
- `.claude/hooks/user-prompt-check.sh` — UserPromptSubmit 用の動的チェックスクリプト
- `.claude/hooks/post-edit-fmt.sh` — PostToolUse 用のフォーマット結果表示スクリプト

### 削除するファイル
- なし

## 影響範囲

- Claude Code の全セッションで hook 出力が変わる
- 既存の BLOCKED 動作は維持（追加のみ）

## 既存パターンとの整合性

- 既存 hook の exit code 規約を踏襲: 0=通過, 2=BLOCKED
- 出力フォーマットは `[PASS]` / `[CHECK]` / `[BLOCKED]` で統一

## テスト戦略

- 手動テスト: 各 hook を意図的にトリガーして表示を確認
- BLOCKED テスト: 禁止パターン（println!等）を含むダミー編集で BLOCKED を確認
- PASS テスト: 正常な編集で [PASS] 表示を確認

## ロールバック計画

settings.json と hooks/ を git revert で戻すだけ。コア機能への影響なし。
