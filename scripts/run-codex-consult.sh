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

# Windows git-bash の日本語ロケール (cp932) で Unicode エラーにならないよう UTF-8 を強制。
# ここで落ちると codex 課金後・budget 更新前に死に、消費が記録されない。
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8

# budget.json は repo root 基準で参照する (cwd 依存だと予算チェックが不成立になる)
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
BUDGET_FILE="$ROOT/.codex/budget.json"
export BUDGET_FILE

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
# `if ! cmd; then rc=$?` は **常に 0** になる (`!` が反転した後のステータスを拾うため)。
# それだと secrets-filter の exit 2 (機密検出) と 1 (故障) を区別できず、
# 呼び出し側が「機密でブロック」と「codex 故障」を取り違える。
scripts/secrets-filter.sh < "$INPUT_FILE" > "$TMPDIR_WORK/filtered.md"
rc=$?
if [ "$rc" -ne 0 ]; then
  if [ "$rc" -eq 2 ]; then
    echo "[run-codex-consult] BLOCKED: secrets-filter detected sensitive content" >&2
    exit 2
  fi
  echo "[run-codex-consult] FAILED: secrets-filter error rc=$rc" >&2
  exit 1
fi

# 予算チェック (python; jq 不要)
# budget.json が壊れていると BUDGET_INFO が空になり、`$((BUDGET - USED))` が
# 「算術エラー -> if 偽 -> そのまま codex を呼ぶ」で **fail-open** する。明示的に止める。
if ! BUDGET_INFO=$("$PYTHON" - "$BUDGET_FILE" 2>/dev/null <<'PY'
import json, sys, datetime


def need_int(v):
    """非整数 / bool / 負値 / 桁あふれを弾く。ここを緩めると値が bash の算術に渡り、
    `$((BUDGET - USED))` が構文エラー → set -e 無しで続行 → **素通り** になる。"""
    if isinstance(v, bool) or not isinstance(v, int) or v < 0 or v > 10**12:
        raise ValueError(f'invalid budget value: {v!r}')
    return v


d = json.load(open(sys.argv[1], encoding='utf-8'))
today = datetime.date.today().isoformat()
used = d['today']['tokens_used'] if d['today'].get('date') == today else 0
print(need_int(d['daily_token_budget']), need_int(d['per_invocation_max']), need_int(used))
PY
); then
  echo "[run-codex-consult] FAILED: .codex/budget.json を読めない / 値が不正" >&2
  exit 1
fi
BUDGET=$(echo "$BUDGET_INFO" | cut -d' ' -f1)
PER_INV=$(echo "$BUDGET_INFO" | cut -d' ' -f2)
USED=$(echo "$BUDGET_INFO" | cut -d' ' -f3)
for v in "$BUDGET" "$PER_INV" "$USED"; do
  case "$v" in
    ''|*[!0-9]*) echo "[run-codex-consult] FAILED: 予算値が整数として読めない" >&2; exit 1 ;;
  esac
done
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
if ! codex exec --json --sandbox read-only --skip-git-repo-check \
  -m gpt-6-astra -c model_reasoning_effort=medium \
  - <<< "$PROMPT" > "$TMPDIR_WORK/result.jsonl"; then
  echo "[run-codex-consult] FAILED: codex exec error" >&2
  exit 1
fi

# 結果を python で parse: 最終 agent_message を stdout、token を budget.json へ反映 (jq/flock 不要)。
"$PYTHON" - "$TMPDIR_WORK/result.jsonl" <<'PY'
import json, os, sys, datetime
texts, tokens = [], 0


def find_tokens(o):
    """usage の載る位置も**キー名**も codex のバージョンで揺れるため再帰探索する。
    旧実装は `.type=="usage"` の `total_tokens` 決め打ちで、形が変わると
    **黙って 0 を記録**し予算ガードを無効化していた。

    実測 (codex-cli 0.142.5): `turn.completed.usage` に `total_tokens` は無く
    `{input_tokens, cached_input_tokens, output_tokens, reasoning_output_tokens}` が入る。
    cached_input_tokens は input_tokens の内数、reasoning_output_tokens は
    output_tokens の内数なので、合計は input + output で採る。"""
    if isinstance(o, dict):
        v = o.get('total_tokens')
        if isinstance(v, int):
            return v
        i, out = o.get('input_tokens'), o.get('output_tokens')
        if isinstance(i, int) or isinstance(out, int):
            return (i if isinstance(i, int) else 0) + (out if isinstance(out, int) else 0)
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
    # codex は usage を**累積**で出すため最大値を採る。行ごとの加算にすると
    # 累積形式で二重計上になる。非累積形式なら過小計上だが、予算を緩める方向の
    # 誤りは WARN で気づけるようにしてある。
    tokens = max(tokens, find_tokens(o))
# 最終 agent_message を出力 (stdout = 相談結果)
print('\n'.join(texts))
if not tokens:
    print('[run-codex-consult] WARN: token usage not found in codex output; '
          'budget records invocation only', file=sys.stderr)
# トークン使用量を予算に反映 (read-modify-write)
p = os.environ.get('BUDGET_FILE') or '.codex/budget.json'
d = json.load(open(p, encoding='utf-8'))
today = datetime.date.today().isoformat()
if d['today'].get('date') == today:
    d['today']['tokens_used'] += tokens
    d['today']['invocations'] += 1
else:
    d.setdefault('history', []).append(d['today'])
    # ⚠️ history は append-only（消さない）。run-codex-review.sh と同じ直し（2026-09-21 に review 側だけ
    #   `[-30:]` を外し、こちらに残っていた —— 2026-10-01 の attack-me の完了時レビューで発見）。
    d['history'] = sorted(d['history'], key=lambda x: x.get('date', ''))
    d['today'] = {'date': today, 'tokens_used': tokens, 'invocations': 1}
# 同ディレクトリの一時ファイル + os.replace で atomic に差し替える。
# `open(p, 'w')` は開いた瞬間に truncate するため、中断で budget.json が壊れる。
tmp = p + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
os.replace(tmp, p)
PY
