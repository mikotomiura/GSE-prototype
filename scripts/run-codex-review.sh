#!/usr/bin/env bash
# scripts/run-codex-review.sh
# cross-reviewer エージェント / codex-review Skill から呼ばれる wrapper。
# 任意の codex exec コマンド実行を防ぐため、パラメータを固定化する。
# jq 非依存 (python 使用) — jq 未導入環境向けに python 化 (2026-06-16)。
#
# 使い方: scripts/run-codex-review.sh > /tmp/cross-review-codex.md
# 内部で git diff | scripts/secrets-filter.sh を通し、固定 prompt で Codex を呼ぶ。
#
# exit code:
#   0: Codex レビュー完了 (stdout に結果)
#   1: 予算超過 / Codex エラー / python 不在
#   2: secrets-filter が機密を検出 (fail-closed)

set -uo pipefail

PYTHON=$(command -v python3 || command -v python || true)
if [ -z "$PYTHON" ]; then
  echo "[run-codex-review] FAILED: python not found (予算管理/JSON パースに必須)" >&2
  exit 1
fi

TMPDIR_WORK=$(mktemp -d)
trap 'rm -rf "$TMPDIR_WORK"' EXIT

git diff > "$TMPDIR_WORK/raw.diff"

# 機密フィルタ (fail-closed)
if ! scripts/secrets-filter.sh < "$TMPDIR_WORK/raw.diff" > "$TMPDIR_WORK/input.diff"; then
  rc=$?
  if [ "$rc" -eq 2 ]; then
    echo "[run-codex-review] BLOCKED: secrets-filter detected sensitive content" >&2
    exit 2
  fi
  echo "[run-codex-review] FAILED: secrets-filter error rc=$rc" >&2
  exit 1
fi

# 予算チェック (python; jq 不要)
BUDGET_INFO=$("$PYTHON" - <<'PY'
import json, datetime
d = json.load(open('.codex/budget.json', encoding='utf-8'))
today = datetime.date.today().isoformat()
used = d['today']['tokens_used'] if d['today'].get('date') == today else 0
print(d['daily_token_budget'], d['per_invocation_max'], used)
PY
)
BUDGET=$(echo "$BUDGET_INFO" | cut -d' ' -f1)
PER_INV=$(echo "$BUDGET_INFO" | cut -d' ' -f2)
USED=$(echo "$BUDGET_INFO" | cut -d' ' -f3)
if [ $((BUDGET - USED)) -lt "$PER_INV" ]; then
  echo "[run-codex-review] BLOCKED: budget exceeded ($USED/$BUDGET used today)" >&2
  exit 1
fi

PROMPT="独立した第二意見として以下の git diff をレビューしてください。
焦点 (優先度順):
1. 明らかなバグ / 論理ミス
2. セキュリティ上の懸念 (input validation, auth, injection)
3. テストカバレッジの不足
4. Claude が見逃しがちな盲点 (静的解析が拾わない設計の歪み)

400 語以内、優先度順に。日本語可。誤検知の可能性がある場合は明示。

---
$(cat "$TMPDIR_WORK/input.diff")"

# 固定パラメータで Codex を呼ぶ
if ! codex exec --json --sandbox read-only --skip-git-repo-check \
  -m gpt-5.5 -c model_reasoning_effort=medium \
  - <<< "$PROMPT" > "$TMPDIR_WORK/result.jsonl"; then
  echo "[run-codex-review] FAILED: codex exec error" >&2
  exit 1
fi

# 結果を python で parse: 最終 agent_message を stdout、token を budget.json へ反映 (jq/flock 不要)。
"$PYTHON" - "$TMPDIR_WORK/result.jsonl" <<'PY'
import json, sys, datetime
texts, tokens = [], 0
for line in open(sys.argv[1], encoding='utf-8'):
    line = line.strip()
    if not line:
        continue
    try:
        o = json.loads(line)
    except Exception:
        continue
    if o.get('type') == 'item.completed' and o.get('item', {}).get('type') == 'agent_message':
        texts.append(o['item'].get('text', ''))
    if o.get('type') == 'usage':
        tokens = o.get('usage', {}).get('total_tokens', 0) or tokens
# 最終 agent_message を出力 (stdout = レビュー本文)
print('\n'.join(texts))
# トークン使用量を予算に反映 (read-modify-write)
p = '.codex/budget.json'
d = json.load(open(p, encoding='utf-8'))
today = datetime.date.today().isoformat()
if d['today'].get('date') == today:
    d['today']['tokens_used'] += tokens
    d['today']['invocations'] += 1
else:
    d.setdefault('history', []).append(d['today'])
    d['history'] = sorted(d['history'], key=lambda x: x.get('date', ''))[-30:]
    d['today'] = {'date': today, 'tokens_used': tokens, 'invocations': 1}
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
PY
