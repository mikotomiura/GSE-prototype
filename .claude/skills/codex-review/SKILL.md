---
name: codex-review
description: >
  OpenAI Codex CLI に独立した第二意見レビューを依頼する。code-reviewer (Claude) のレビューに
  別 LLM の視点を加えたい時、または /cross-review コマンドから呼び出される時に使う。
  入力は git diff のみ。scripts/secrets-filter.sh で機密情報と proprietary plugin 出力を
  除去してから渡す。読み取り専用 (sandbox=read-only) で書き込みは行わない。
  対象が docs/external-skills.md で「外部 LLM 送信禁止」とされる Skill の出力を含む場合、
  または .codex/budget.json の予算超過時は実行を中止する。
allowed-tools: Bash(scripts/run-codex-review.sh *), Bash(git *), Bash(jq *), Read
---

# Codex Review Skill

## 適用条件 (すべて満たす必要)

1. `/cross-review` コマンドから呼ばれた、または `code-reviewer` が第二意見を要求した、
   またはユーザーが「もう一度別の視点で見て」と明示した
2. 対象 diff に機密ファイル (`.env`, `*.pem`, `*.key`, `*credentials*`) を含まない
3. 対象 diff に proprietary plugin 出力 (`*.pdf` / `*.docx` / `*.xlsx` / `*.pptx`) を含まない
4. `.codex/budget.json` の当日予算余裕が `per_invocation_max` 以上ある

## 実行フロー

### Step 1: Proprietary / 機密混入チェック

```bash
DIFF_FILES=$(git diff --name-only)
if echo "$DIFF_FILES" | grep -E '\.(pdf|docx|xlsx|pptx)$' > /dev/null; then
  echo "[codex-review] BLOCKED: diff contains proprietary plugin outputs"
  exit 1
fi
if echo "$DIFF_FILES" | grep -E '(\.env|\.pem|\.key|credentials)' > /dev/null; then
  echo "[codex-review] BLOCKED: diff contains likely secrets"
  exit 1
fi
```

### Step 2: wrapper 経由で Codex 呼び出し

wrapper 内で予算チェック・secrets-filter・Codex 呼び出し・予算反映を一括実行:

```bash
scripts/run-codex-review.sh
```

## 出力の取り扱い

Codex のレビュー結果を **そのまま** Claude に返す。Claude は呼び出し元 (`/cross-review` 等) で:

- Codex 指摘が Claude のレビューと **一致** するか?
- Codex 指摘が Claude が **見落とした** 観点か?
- Codex 指摘が **誤検知** か?

を判定し、統合レポートを作る。

## 関連 Skill / ファイル

- `codex-rescue` — 修正実装の委譲 (workspace-write + 要承認)
- `.codex/config.toml` — モデル / sandbox 既定
- `.codex/budget.json` — 日次予算
- `scripts/run-codex-review.sh` — 本 Skill 専用 wrapper
- `scripts/secrets-filter.sh` — 機密フィルタ
- `docs/external-skills.md` — proprietary 判定基盤

## アンチパターン

- ❌ 予算チェックを skip して呼ぶ
- ❌ secrets-filter を通さずに raw diff を渡す
- ❌ proprietary plugin の出力ファイルを混ぜる
- ❌ rescue 用途 (書き込み) で本 Skill を使う (codex-rescue を使う)
- ❌ Codex の応答を盲信する (Claude 側で誤検知判定が必要)
