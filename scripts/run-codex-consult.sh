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

# 予算管理 / JSON パースは python で行う (jq / flock 非依存: macOS に flock が無いため。
# run-codex-review.sh と同一方式に統一)。
PYTHON=$(command -v python3 || command -v python || true)
if [ -z "$PYTHON" ]; then
  echo "[run-codex-consult] FAILED: python not found (予算管理/JSON パースに必須)" >&2
  exit 1
fi

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

# 結果を python で parse: 最終 agent_message を stdout、token を budget.json へ反映 (jq/flock 不要)。
"$PYTHON" - "$TMPDIR_WORK/result.jsonl" <<'PY'
import json, sys, datetime
texts, tokens = [], 0


def find_tokens(o):
    """usage の載る位置は codex のバージョンで揺れるため、total_tokens を再帰探索する。
    旧実装は `.type=="usage"` 決め打ちで、形が変わると**黙って 0 を記録**し予算ガードを無効化していた。"""
    if isinstance(o, dict):
        v = o.get('total_tokens')
        if isinstance(v, int):
            return v
        for x in o.values():
            r = find_tokens(x)
            if r:
                return r
    elif isinstance(o, list):
        for x in o:
            r = find_tokens(x)
            if r:
                return r
    return 0


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
    tokens = find_tokens(o) or tokens
# 最終 agent_message を出力 (stdout = 相談結果)
print('\n'.join(texts))
if not tokens:
    print('[run-codex-consult] WARN: token usage not found in codex output; '
          'budget records invocation only', file=sys.stderr)
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
