# 設計 — claude-env-codex-bridge (コミット整理計画)

## 実装アプローチ

製品コードに触れず、未コミットの agent 環境設定を **論理単位で 3 + 1 コミット**に整理する。
ランタイム生成物は `.gitignore` で除外。ファイル選択 add のみ (`git add -A` は使わない)。

## コミット計画

### Commit 1 — `chore(git): ignore steering runtime token-log artifacts`
- `.gitignore` に追記: `.steering/_token_log.md` / `.steering/_token_log.last_key` /
  `.steering/_token_log.md.lock`。
- 理由: token_log はランタイム生成物・`.lock` は一時ロック。コミット対象外 (受け入れ条件)。

### Commit 2 — `docs(agents): restructure agent instructions + workflow skills + hook/docs tweaks`
- 新規: `docs/agent-shared.md`, `docs/external-skills.md`,
  `.claude/skills/implementation-workflow/`, `.claude/skills/empirical-prompt-tuning/`。
- 修正: `CLAUDE.md`, `AGENTS.md` (スリム化・@参照化),
  `.claude/commands/{add-feature,fix-bug,refactor,start-task,finish-task}.md` (skill 参照へスリム化),
  `.claude/hooks/{pre-edit-banned,pre-edit-steering,stop-check}.sh`,
  `docs/architecture.md`, `docs/development-guidelines.md`,
  `.steering/_setup-progress.md`, `.steering/_verify-report-20260616.md`,
  `.steering/deferred-evaluations.md`。
- 理由: Claude Code 環境の「指示書 3 ファイル体制 + workflow DRY skill + hook/docs 調整」を 1 単位に。

### Commit 3 — `chore(codex): add Codex CLI bridge (cross-review + skills + hooks + scripts)`
- 新規: `.claude/agents/cross-reviewer.md`, `.claude/commands/cross-review.md`,
  `.claude/hooks/{codex-budget-guard,secrets-pre-filter,token-report-stop}.sh`,
  `.claude/skills/{codex-consult,codex-rescue,codex-review}/`,
  `.codex/budget.json`, `.codex/config.toml`,
  `scripts/{run-codex-consult,run-codex-review,secrets-filter}.sh`。
- 修正: `.claude/settings.json` (codex hook 登録 + MultiEdit post-fmt matcher)。
- 理由: Codex CLI 連携を 1 単位に。settings.json は登録対象スクリプトと同コミットで参照整合を保つ。

### Commit 4 — `chore(steering): record claude-env-codex-bridge task`
- 新規: `.steering/20260617-claude-env-codex-bridge/` (本タスクの記録)。

## 判断点 (確定)
- **token_log は gitignore**: ランタイム生成物。`_verify-report-*`/`_setup-progress` は既存が tracked の
  ため同慣習でコミットする (整合)。
- **`.codex/budget.json` は現状のままコミット**: `today` ランタイムカウンタは編集しない (スコープ「内容の
  再設計はしない」・guard が日次管理)。値の意味づけ変更はしない。
- **settings.json は Commit 3**: 追加分は codex hook 3 種 + MultiEdit→post-fmt。参照先スクリプトと同梱。

## 影響範囲
- 製品コード (`src/`, `src-tauri/`) 無変更 → `cargo`/`npm` ビルドに影響なし。
- agent 環境 (hook/skill/command/instruction) がコミットされ、以後のセッションで版管理される。
  settings.json と hook スクリプトを同コミットにし、壊れた hook 参照を残さない。

## テスト戦略
- ビルド検証は不要 (設定のみ・製品コード不変)。
- コミット後 `git status` がクリーン (token_log 等の gitignore 済み runtime 以外に追跡対象の未コミットが無い) ことを確認。
- 各コミットの `git show --stat` で意図したファイルのみ含まれることを確認。
- hook 参照整合: settings.json が参照する 5 hook スクリプトが全て存在することを確認。

## ロールバック計画
- 全て設定の追加・整理。問題があれば当該コミットを revert (製品コードに副作用なし)。
