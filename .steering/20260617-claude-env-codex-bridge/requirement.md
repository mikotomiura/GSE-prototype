# Task — claude-env-codex-bridge (未コミット agent 環境設定の整理・コミット)

## 背景

作業ツリーに **36 個の未コミットファイル** が ~5 セッション越しに残存し、毎タスクの commit staging を
汚している (E / blind dashboard でも選択 add で回避してきた)。中身は GSE 製品コードではなく
**Claude Code / Codex CLI のエージェント環境設定** (Codex bridge / workflow skills / agent 指示書
再構成 / hook・docs 調整 / steering 記録) で、Claude Code 環境構築 (bootstrap→verify) の Phase 5-9 の
成果が未コミットのまま溜まっている。

## ゴール

これらを **論理単位に整理してコミット**し、作業ツリーをクリーンにする。ランタイム生成物
(token_log / lock) は **`.gitignore` 化**してコミット対象から除外する。製品コード (`src/`, `src-tauri/`)
には触れない。

## スコープ

### 含むもの (コミットする env 設定)
- **Codex bridge**: `.claude/agents/cross-reviewer.md`, `.claude/commands/cross-review.md`,
  `.claude/hooks/{codex-budget-guard,secrets-pre-filter,token-report-stop}.sh`,
  `.claude/skills/{codex-consult,codex-rescue,codex-review}/`, `.codex/{budget.json,config.toml}`,
  `scripts/{run-codex-consult,run-codex-review,secrets-filter}.sh`, `docs/external-skills.md`,
  `.claude/settings.json` (hook 登録)。
- **Workflow skills + command 整理**: `.claude/skills/{implementation-workflow,empirical-prompt-tuning}/`,
  `.claude/commands/{add-feature,fix-bug,refactor,start-task,finish-task}.md` (skill 参照へスリム化)。
- **Agent 指示書再構成**: `CLAUDE.md` / `AGENTS.md` スリム化, `docs/agent-shared.md` 新設。
- **Hook / docs 調整**: `.claude/hooks/{pre-edit-banned,pre-edit-steering,stop-check}.sh`,
  `docs/architecture.md`, `docs/development-guidelines.md`。
- **Steering 記録**: `.steering/_setup-progress.md`, `_verify-report-20260616.md`,
  `deferred-evaluations.md` (既存 `_verify-report-*` / `_setup-progress` が tracked = 同慣習で追従)。

### 含まないもの
- 製品コード (`src/`, `src-tauri/`) の変更。機能追加・挙動変更。
- ランタイム生成物のコミット (`.steering/_token_log.md`, `_token_log.last_key`, `_token_log.md.lock`)
  → これらは `.gitignore` で除外する。
- env 設定の**内容**の再設計 (中身が正しいかの監査はせず、現状の成果を整理してコミットするのみ)。
- `.codex/budget.json` の `today` ランタイムカウンタの値の意味づけ変更 (コミット時の扱いは design で確定)。

## 受け入れ条件

- [ ] env 設定が論理単位 (codex-bridge / workflow-skills / agent-instructions / hooks-docs / steering) で
      コミットされる (type=chore/docs、Refs 付き)。
- [ ] `.steering/_token_log.*` (md/last_key/lock) が `.gitignore` に追加され、コミットされない。
- [ ] コミット後 `git status` がクリーン (意図して残す runtime 生成物以外、追跡対象の未コミットが無い)。
- [ ] 製品コード (`src/`, `src-tauri/`) は無変更。`cargo`/`npm` ビルドに影響しない (設定のみ)。
- [ ] hook が settings.json と整合し、参照先スクリプトが存在する (壊れた hook 参照を残さない)。

## 関連ドキュメント
- `.steering/_setup-progress.md` (環境構築フェーズ進捗)
- `docs/agent-shared.md` / `CLAUDE.md` / `AGENTS.md` (3 ファイル体制)
- `.codex/config.toml` / `.codex/budget.json` / `scripts/secrets-filter.sh` (Codex bridge)

## 運用メモ
- /reimagine 適用: **No**
- 理由: 設計の再構築ではなく、既存の env 設定成果を論理単位に整理してコミットする chore。判断点は
  「コミット粒度」と「gitignore 対象」のみで、design.md + 承認で確定すれば足りる。
- ブランチ: `chore/claude-env-codex-bridge` (起点 = origin/main 295a481 相当 = A..E + blind 統合済)。
