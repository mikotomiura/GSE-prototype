# タスクリスト — claude-env-codex-bridge

## 準備
- [x] 36 未コミットファイルを調査・分類 (modified/untracked, 既存 tracked 慣習の確認)
- [x] settings.json 差分で hook 帰属を確定 (codex hook 3 種 + MultiEdit post-fmt)
- [x] コミット整理計画を design.md に記載・ユーザー承認

## 実装 (コミット整理)
- [x] Commit 1: `.gitignore` に token_log 3 種を追加 (chore(git))
- [x] Commit 2: agent 指示書再構成 + workflow skills + 命令スリム化 + hook/docs + steering (docs(agents))
- [x] Commit 3: Codex bridge (skills/hooks/scripts/.codex/settings.json) (chore(codex))
- [x] Commit 4: 本タスクの steering 記録 (chore(steering))

## 検証
- [x] token_log が ignore される (git status に出ない・`!!` 表示) を確認
- [x] settings.json 参照の全 hook スクリプトが存在 (codex-budget-guard/secrets-pre-filter/token-report-stop/stop-check/pre-edit-banned/post-fmt)
- [x] 各 commit の `git show --stat` で意図ファイルのみを確認
- [x] 製品コード (`src/`, `src-tauri/`) 無変更 → ビルド検証不要
- [ ] コミット後 `git status` クリーン (steering commit 後に最終確認)

## レビュー
- [~] code-reviewer/security-checker: 設定整理のみ・製品コード無変更のため軽量。/finish-task で要否判断。

## 完了処理
- [x] design.md (コミット計画) 確定
- [ ] /finish-task (parity skip 見込み・cross-review は設定変更のため要否判断)
- [ ] push / PR
