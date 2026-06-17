#!/usr/bin/env bash
# codex-budget-guard.sh
# PreToolUse on Bash — `codex exec` を含むコマンドを検査し、
# .codex/budget.json の当日予算余裕が per_invocation_max 未満ならブロック (exit 2)

set -uo pipefail

INPUT_JSON=$(cat)
COMMAND=$(echo "$INPUT_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

# codex を含まないコマンドは即座に通過
case "$COMMAND" in
  *codex*) ;;
  *) exit 0 ;;
esac

if ! echo "$COMMAND" | grep -qE 'codex[[:space:]]+exec'; then
    exit 0
fi

# .codex/budget.json が無ければスキップ (Phase 5 未完了環境では guard 不適用)
if [ ! -f .codex/budget.json ]; then
    echo "[guard] PASS: .codex/budget.json absent (Phase 5 not run, no budget guard)"
    exit 0
fi

TODAY=$(date +%Y-%m-%d)
DATA=$(cat .codex/budget.json)
BUDGET=$(echo "$DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['daily_token_budget'])" 2>/dev/null || echo "0")
PER_INV=$(echo "$DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['per_invocation_max'])" 2>/dev/null || echo "0")
USED=$(echo "$DATA" | python3 -c "import sys,json,os; d=json.load(sys.stdin); print(d['today']['tokens_used'] if d.get('today',{}).get('date')=='$TODAY' else 0)" 2>/dev/null || echo "0")

REMAINING=$((BUDGET - USED))
if [ "$REMAINING" -lt "$PER_INV" ]; then
    echo "[guard] BLOCKED: codex daily budget exceeded (used=$USED budget=$BUDGET per_inv=$PER_INV remaining=$REMAINING)" >&2
    echo "[guard]          Wait until tomorrow or update .codex/budget.json to reset." >&2
    exit 2
fi

echo "[guard] PASS: codex budget OK ($REMAINING tokens remaining)"
exit 0
