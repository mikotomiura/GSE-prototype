# AGENTS.md — Codex CLI 指示

## このファイルについて

このファイルは OpenAI Codex CLI (`codex` コマンド) がセッション開始時に読み込みます。
**Codex CLI 固有の動作プロトコル** に集中して書きます。

- プロジェクト共通の情報 (概要 / アーキテクチャ / 技術制約 / 規約 / テスト / git) は
  `@docs/agent-shared.md` を参照してください。Claude Code も同じファイルを読みます。
- Claude Code 固有の動作 (Plan mode / Skill / `.steering` ワークフロー) は `CLAUDE.md` を見てください。

## 共通コンテキスト

@docs/agent-shared.md

## サンドボックス既定

- **既定**: `read-only` — レビュー / 調査用途。書き込み禁止。
- **`workspace-write`** — `codex-rescue` 経由かつ git worktree 隔離
  (`.worktrees/codex-rescue-*`) でのみ許可。
- **`danger-full-access`** — 使用禁止。

詳細は `.codex/config.toml` (Phase 5 で正式化)。

## 承認モード

- 既定: `untrusted` — 全シェルコマンドが事前承認を要求する。
- バッチ実行 (`/cross-review` 等) では Claude Code 側で `--ask-for-approval=on-failure` に切替可。

## モデル設定

- 既定モデル: `gpt-6-sol`、reasoning effort 既定: `medium`（★ 2026-09-25 に `gpt-5.5`〔CLI 上で Legacy〕から更新）
- ★ 役割ごとの割当: **レビュー（`/cross-review`）・設計相談（`codex-consult`）= `gpt-6-astra`**（見逃しコスト・やり直しの効かない判断）／ **rescue（実装）= `gpt-6-sol`**。値の実体は `.codex/config.toml`・`scripts/run-codex-review.sh`・`scripts/run-codex-consult.sh`・`codex-rescue` Skill
- レビュー特化タスクでは `-c model_reasoning_effort=xhigh` を Skill から指定可。

## 出力形式

- バッチ呼び出しは `--json` 必須 (Skill / hook が `jq` でパースする前提)。
- 最終応答のみ取り出す:
  `jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text'`

## Rescue モード (codex-rescue Skill 経由のみ)

1. メイン worktree から `git worktree add .worktrees/codex-rescue-<ts> HEAD`
2. その worktree で `codex exec --sandbox workspace-write --ask-for-approval`
3. 完了 diff をメイン worktree の Claude が review、merge は人間判断

## 禁止事項

- 機密情報 (`.env`, `*.pem`, `*.key`, `*credentials*`) を入力に含める
- **NDJSON セッションログ・キーストローク内容** を入力に含める (`data-privacy` Skill 参照)
- `docs/external-skills.md` で「外部 LLM への送信」が「禁止」の Skill 出力 / 中間生成物を入力に含める
- メイン worktree への直接書き込み (rescue は必ず別 worktree で)
- 同時に複数 codex セッションを動かす (`~/.codex/config.toml` の race condition 回避)

## 技術的制約

`@docs/agent-shared.md` の「技術的制約 (厳守)」に従うこと
(windows crate のみ / unsafe 隔離 / フックは非ブロッキング / `analysis/` で OS API 禁止 等)。

## 関連ファイル (Phase 5 で生成)

- `.codex/config.toml` — Codex CLI 設定 (モデル / sandbox 既定)
- `.codex/budget.json` — 日次トークン予算
- `scripts/secrets-filter.sh` — 機密 + proprietary 入力フィルタ
- `.claude/skills/codex-consult/SKILL.md` — 設計相談 (Plan mode で第二意見)
- `.claude/skills/codex-review/SKILL.md` — diff レビュー (read-only)
- `.claude/skills/codex-rescue/SKILL.md` — rescue (workspace-write + worktree 隔離 + 明示承認)
