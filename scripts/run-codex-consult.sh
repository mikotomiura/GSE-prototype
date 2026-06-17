#!/usr/bin/env bash
# scripts/run-codex-consult.sh
# codex-consult Skill から呼ばれる設計相談 wrapper。
# 入力ファイル (markdown 抜粋) を受け取り、固定 prompt で Codex に第二意見を求める。
#
# 使い方:
#   scripts/run-codex-consult.sh /tmp/codex-consult-input.md
#   scripts/run-codex-consult.sh --preview /tmp/codex-consult-input.md
#
# exit code:
#   0: 完了 (stdout に結果 or preview)
#   1: 予算超過 / 入力エラー / Codex エラー
#   2: secrets-filter が機密を検出 (fail-closed)

set -uo pipefail

PREVIEW=false
if [ "${1:-}" = "--preview" ]; then
  PREVIEW=true
  shift
fi

INPUT_FILE="${1:-}"
if [ -z "$INPUT_FILE" ] || [ ! -f "$INPUT_FILE" ]; then
  echo "[run-codex-consult] usage: $0 [--preview] <input-md-file>" >&2
  exit 1
fi

TMPDIR_WORK=$(mktemp -d)
trap 'rm -rf "$TMPDIR_WORK"' EXIT

# 機密フィルタ (fail-closed)
if ! scripts/secrets-filter.sh < "$INPUT_FILE" > "$TMPDIR_WORK/filtered.md"; then
  rc=$?
  if [ "$rc" -eq 2 ]; then
    echo "[run-codex-consult] BLOCKED: secrets-filter detected sensitive content" >&2
    exit 2
  fi
  echo "[run-codex-consult] FAILED: secrets-filter error rc=$rc" >&2
  exit 1
fi

# 予算チェック
TODAY=$(date +%Y-%m-%d)
DATA=$(cat .codex/budget.json)
BUDGET=$(echo "$DATA" | jq -r '.daily_token_budget')
PER_INV=$(echo "$DATA" | jq -r '.per_invocation_max')
USED=$(echo "$DATA" | jq -r --arg d "$TODAY" 'if .today.date == $d then .today.tokens_used else 0 end')
if [ $((BUDGET - USED)) -lt "$PER_INV" ]; then
  echo "[run-codex-consult] BLOCKED: budget exceeded ($USED/$BUDGET used today)" >&2
  exit 1
fi

PROMPT="以下の設計案について、独立した視点から:
1. 抜けている観点 (主要な落とし穴、エッジケース)
2. 候補案以外に検討すべき選択肢
3. 採用案のリスクと、軽減策の追加アイデア
4. トレードオフ評価で見落としがちな点

400 語以内、優先度順に。日本語可。「採用案を支持/不支持」ではなく盲点指摘 + 追加アイデアに専念。

---
$(cat "$TMPDIR_WORK/filtered.md")"

# Preview モード: 送信せず内容を表示して終了
if [ "$PREVIEW" = "true" ]; then
  echo "=== Preview (this content will be sent to Codex) ==="
  echo "$PROMPT"
  echo "=== End of preview ==="
  exit 0
fi

# Codex 呼び出し (固定パラメータ)
codex exec --json --sandbox read-only --skip-git-repo-check \
  -m gpt-5.5 -c model_reasoning_effort=medium \
  - <<< "$PROMPT" > "$TMPDIR_WORK/result.jsonl"

# 最終 agent_message のみ出力
jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text' \
  "$TMPDIR_WORK/result.jsonl"

# トークン使用量を予算に反映 (atomic + flock)
TOKENS=$(jq -r 'select(.type=="usage") | .usage.total_tokens // 0' "$TMPDIR_WORK/result.jsonl" | tail -1)
TOKENS=${TOKENS:-0}

(
  flock -x 9
  jq --arg d "$TODAY" --argjson t "$TOKENS" \
    'if .today.date == $d
     then .today.tokens_used += $t | .today.invocations += 1
     else .history += [.today] | .history = (.history | sort_by(.date) | .[-30:])
          | .today = {date: $d, tokens_used: $t, invocations: 1}
     end' \
    .codex/budget.json > .codex/budget.json.tmp \
    && mv .codex/budget.json.tmp .codex/budget.json \
    || echo "[run-codex-consult] WARN: budget update failed" >&2
) 9> .codex/budget.json.lock
