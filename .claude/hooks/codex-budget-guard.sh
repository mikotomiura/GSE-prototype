#!/usr/bin/env bash
# codex-budget-guard.sh
# PreToolUse on Bash — codex の外部呼び出しを検査し、
# .codex/budget.json の当日予算余裕が per_invocation_max 未満ならブロック (exit 2)
#
# 設計原則: **判定できないなら通さない (fail-closed)**。
# `set -e` が無いシェルでは、コマンド不在・JSON 破損・非整数値がすべて
# 「エラーだが処理は継続」になり、ガードが静かに素通りする。各段で明示的に止める。

set -uo pipefail

INPUT_JSON=$(cat)

# 高速早期 exit: raw JSON に codex の文字列が無ければ parse すらしない (Bash 全発火対策)
case "$INPUT_JSON" in
  *codex*) ;;
  *) exit 0 ;;
esac

# JSON / 予算のパースは python (jq 非依存)。失敗を 0 や空文字へ縮退させると
# BUDGET=0/USED=0/PER_INV=0 → `0 -lt 0` が false → **PASS** となりガードが
# 黙って無効化される。判定不能なら通さない。
PYTHON=$(command -v python3 || command -v python || true)
if [ -z "$PYTHON" ]; then
    echo "[guard] BLOCKED: python not found — codex 予算を検証できないため通さない (fail-closed)" >&2
    exit 2
fi

# Windows git-bash の日本語ロケール (cp932) で UnicodeDecodeError にならないよう UTF-8 を強制
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8

if ! COMMAND=$(printf '%s' "$INPUT_JSON" | "$PYTHON" -c \
    "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null); then
    echo "[guard] BLOCKED: hook 入力 JSON を parse できない — fail-closed" >&2
    exit 2
fi

# codex の**サブコマンドを限定しない**。`codex exec` 決め打ちだと
# `codex e` (alias) / `codex review` / `codex --cd . exec` / 行継続 がすべて素通りする。
# ただし判定は**コマンド位置** (行頭 / パイプ / `;` / `&&` / `||` / `(` の直後) に限る。
# 単に「codex という語を含むか」にすると、ヒアドキュメント内で codex に言及しただけの
# 無関係な Bash 呼び出しまでブロックしてしまう (実際に踏んだ)。
# 対話 REPL も予算チェックの対象にして構わない (安全側)。
# 判定は python で行う。`grep` に頼ると **grep 不在・regex エラーでも exit 0 = 素通り**
# になり、外部コマンド不在で静かに壊れるという本件と同じ穴が残る。
CODEX_HIT=$(printf '%s' "$COMMAND" | "$PYTHON" -c \
    "import re,sys; print('1' if re.search(r'(?m)(^|[|;&(]|&&|\|\|)[ \t]*(\S*/)?codex([ \t]|$)', sys.stdin.read()) else '0')" 2>/dev/null)
if [ "$CODEX_HIT" != "1" ] && [ "$CODEX_HIT" != "0" ]; then
    echo "[guard] BLOCKED: codex 判定に失敗 — fail-closed" >&2
    exit 2
fi
[ "$CODEX_HIT" = "0" ] && exit 0

# リポジトリルート基準で budget.json を探す。cwd 依存だと
# 「ファイルが無い → PASS」でガードが丸ごと無効化される。
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
BUDGET_FILE="$ROOT/.codex/budget.json"

# budget.json が無ければスキップ (Phase 5 未完了環境では guard 不適用)
if [ ! -f "$BUDGET_FILE" ]; then
    echo "[guard] PASS: .codex/budget.json absent (Phase 5 not run, no budget guard)"
    exit 0
fi

if ! BUDGET_INFO=$("$PYTHON" - "$BUDGET_FILE" 2>/dev/null <<'PY'
import json, sys, datetime


def need_int(v):
    """非整数 / bool / 負値 / 桁あふれを弾く。
    ここを緩めると値が bash の算術に渡り、`$((BUDGET - USED))` が
    構文エラー → set -e 無しで続行 → **PASS** という fail-open になる。"""
    if isinstance(v, bool) or not isinstance(v, int) or v < 0 or v > 10**12:
        raise ValueError(f'invalid budget value: {v!r}')
    return v


d = json.load(open(sys.argv[1], encoding='utf-8'))
today = datetime.date.today().isoformat()
used = d['today']['tokens_used'] if d.get('today', {}).get('date') == today else 0
print(need_int(d['daily_token_budget']), need_int(d['per_invocation_max']), need_int(used))
PY
); then
    echo "[guard] BLOCKED: .codex/budget.json を読めない / 値が不正 — fail-closed" >&2
    exit 2
fi
BUDGET=$(echo "$BUDGET_INFO" | cut -d' ' -f1)
PER_INV=$(echo "$BUDGET_INFO" | cut -d' ' -f2)
USED=$(echo "$BUDGET_INFO" | cut -d' ' -f3)

# python 側で検証済みだが、受け渡しの崩れも算術エラー = fail-open になるので二重に確認する
for v in "$BUDGET" "$PER_INV" "$USED"; do
    case "$v" in
        ''|*[!0-9]*)
            echo "[guard] BLOCKED: 予算値が整数として読めない — fail-closed" >&2
            exit 2
            ;;
    esac
done

REMAINING=$((BUDGET - USED))
if [ "$REMAINING" -lt "$PER_INV" ]; then
    echo "[guard] BLOCKED: codex daily budget exceeded (used=$USED budget=$BUDGET per_inv=$PER_INV remaining=$REMAINING)" >&2
    echo "[guard]          Wait until tomorrow or update .codex/budget.json to reset." >&2
    exit 2
fi

echo "[guard] PASS: codex budget OK ($REMAINING tokens remaining)"
exit 0
