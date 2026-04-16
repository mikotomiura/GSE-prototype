# Hook Visibility Improvement

## 背景

現状の Claude Code hook は結果がユーザーに見えず、有効に機能しているか判断できない。
- UserPromptSubmit: 毎回同じ固定文言が流れるだけ。Claude が実際にチェックを行っているか不明
- PreToolUse: BLOCKED 時のみ表示、パス時は無言。hook が動いているか分からない
- PostToolUse: cargo fmt が無言実行。フォーマット変更があったかどうか不明
- Claude が「毎回チェックしてから作業に入る」ことが強制されていない

## ゴール

1. 全 hook で明示的なステータス表示を行い、チェック結果の透明性を確保する
2. Claude が毎ターン、作業開始前に必要なチェックを実行し、結果をユーザーに明示する仕組みを作る
3. /reimagine 適用判断など、現状リマインダのみの項目に対して機械的な強制力を持たせる

## スコープ

### 含むもの
- .claude/settings.json の hook 設定変更
- .claude/hooks/ 配下のスクリプト修正・追加
- CLAUDE.md の関連セクション更新（hook 説明部分）
- docs/development-guidelines.md §9 の更新

### 含まないもの
- GSE のコア機能（engine.rs, hook.rs, features.rs 等）の変更
- 新しい Skill / Command の追加
- フロントエンド (src/*.tsx) の変更

## 受け入れ条件

- [ ] 全 hook (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop) でパス/失敗が明示される
- [ ] UserPromptSubmit が動的チェック（.steering/ 状態、未コミット変更数など）を実行し結果を表示する
- [ ] PreToolUse がパス時にも [PASS] メッセージを出力する
- [ ] ユーザーが hook の有効性を毎ターン確認できる

## 関連ドキュメント

- docs/development-guidelines.md §9 (Claude Code Hooks)
- .claude/settings.json (hook 設定)
- .claude/hooks/ (実装スクリプト)

## 運用メモ
- /reimagine 適用: Yes
- 理由: hook の設計自体に複数の実装案がありえる（チェック粒度、表示形式、強制力の程度）。破壊と構築で最良案を選ぶ
