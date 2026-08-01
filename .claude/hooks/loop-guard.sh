#!/usr/bin/env bash
# loop-guard.sh — Loop Engineering 二段監視の下段 (無料・機械的 Stop hook)
# 進まないループを確定的に止める: fingerprint 連続 / max_attempts / token_ceiling。
# LLM を呼ばない。active な loop タスクが無ければ必ず PASS で抜ける (fail-safe)。
# 重要: この hook は worker の *worktree* 内で発火する。runtime ファイルは main
# checkout にしか無いため、まず main root を解決し、issue は worktree のブランチ
# (loop/<id>-<short>) から束縛する (直近イベント依存だと並行時に別 issue を掴む)。
# selfcheck: safe   # active loop 無し/欠損時は必ず PASS exit 0 → hook-selfcheck の smoke 対象
set -uo pipefail

PREFIX="[guard]"
pass()  { echo "$PREFIX PASS: $1"; exit 0; }                       # noise 抑制: 1 行だけ
block() { jq -cn --arg r "$PREFIX BLOCKED: $1" '{decision:"block",reason:$r}'; \
          echo "$PREFIX BLOCKED: $1" >&2; exit 0; }                 # JSON で停止指示

command -v jq >/dev/null 2>&1 || pass "jq unavailable (fail-open)"

# --- main checkout を解決 (worktree list の先頭 = main。空白入りパスにも耐える) -
MAIN_ROOT="$(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print substr($0,10); exit}')"
[ -n "${MAIN_ROOT:-}" ] || MAIN_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "${MAIN_ROOT:-}" ] || pass "not in a git repo"

# --- 現在の issue = worktree の loop/<id>-<short> ブランチに束縛 --------------
BR="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
case "${BR:-}" in
  loop/*) ISSUE="$(printf '%s' "${BR#loop/}" | sed 's/-.*$//')" ;;
  *)      pass "not a loop worktree (branch=${BR:-none})" ;;      # main/dashboard は素通り
esac

# --- active な loop タスクを検出 (main checkout の最新 _loop-config.json) -------
CFG="$(ls -t "$MAIN_ROOT"/.steering/*/_loop-config.json 2>/dev/null | head -n1 || true)"
[ -n "${CFG:-}" ] && [ -f "$CFG" ] || pass "no active loop task"

EVENTS="$(jq -r '.events_path // empty' "$CFG" 2>/dev/null || true)"
[ -z "${EVENTS:-}" ] && EVENTS="$(dirname "$CFG")/_loop-events.jsonl"
[ -f "$EVENTS" ] || pass "no events yet ($EVENTS)"

MAX_ATT="$(jq -r '.budget.max_attempts // 6'            "$CFG")"
TOK_CEIL="$(jq -r '.budget.token_ceiling // 0'          "$CFG")"
NP_THRESH="$(jq -r '.budget.no_progress_threshold // 4' "$CFG")"   # 既定 4

# --- events を 1 行ずつ検証 (並行 append の壊れ行を捨てる) → この issue に絞る ---
EV="$(jq -R 'fromjson? // empty' "$EVENTS" 2>/dev/null \
      | jq -s --arg iss "$ISSUE" '[ .[] | select(.issue==$iss) ]' 2>/dev/null || echo '[]')"

# 同一 fingerprint の末尾連続数
STREAK="$(printf '%s' "$EV" | jq -r '
  [ .[] | select(.fingerprint!=null) | .fingerprint ] as $fps
  | if ($fps|length)==0 then 0
    else ($fps|reverse) as $r | ($r[0]) as $h
      | (reduce $r[] as $x ({n:0,stop:false};
           if .stop then . elif $x==$h then {n:(.n+1),stop:false} else {n:.n,stop:true} end).n)
    end' 2>/dev/null || echo 0)"
LAST_FP="$(printf '%s' "$EV" | jq -r '[ .[] | select(.fingerprint!=null) | .fingerprint ] | (last // "")' 2>/dev/null || echo "")"
ATT="$(printf '%s' "$EV" | jq -r '[ .[] | select(.attempt!=null) | .attempt ] | (max // 0)' 2>/dev/null || echo 0)"

# --- token 使用量 (main checkout の _token_log.md。散文行を除外し数値行だけ合算) -
USED=0
TLOG="$MAIN_ROOT/.steering/_token_log.md"
if [ -f "$TLOG" ] && [ "${TOK_CEIL:-0}" -gt 0 ] 2>/dev/null; then
  # 1 行 = "<idempotency-key> <int>"。key 重複排除。第1列が key 形・末列が整数の行のみ。
  USED="$(awk '$1 ~ /^[A-Za-z0-9_.-]+$/ && $NF ~ /^[0-9]+$/ && !seen[$1]++ {s+=$NF} END{print s+0}' "$TLOG" 2>/dev/null || echo 0)"
fi

now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
append_stop() {  # no_progress_stop を idempotent に 1 度だけ append (jq で安全に生成)
  local last_ev
  last_ev="$(tail -n 1 "$EVENTS" | jq -r '.event // empty' 2>/dev/null || true)"
  [ "$last_ev" = "no_progress_stop" ] && return 0
  jq -cn --arg ts "$(now)" --arg iss "$ISSUE" --argjson att "${ATT:-0}" \
         --arg fp "$LAST_FP" --arg d "$1" \
    '{ts:$ts,issue:$iss,phase:"verify",event:"no_progress_stop",attempt:$att,fingerprint:$fp,detail:$d}' \
    >> "$EVENTS"
}

# --- 判定 (機械的・確定的) ----------------------------------------------------
if [ "${STREAK:-0}" -ge "${NP_THRESH:-4}" ] 2>/dev/null; then
  append_stop "同一fingerprint×${STREAK} (>= ${NP_THRESH})、前進なしで停止"
  block "issue ${ISSUE}: 同一failure×${STREAK} → no_progress_stop"
fi
if [ "${ATT:-0}" -ge "${MAX_ATT:-6}" ] 2>/dev/null; then
  block "issue ${ISSUE}: attempt ${ATT} >= max_attempts ${MAX_ATT}"
fi
if [ "${TOK_CEIL:-0}" -gt 0 ] 2>/dev/null && [ "${USED:-0}" -ge "${TOK_CEIL}" ] 2>/dev/null; then
  block "token_ceiling 超過: ${USED} >= ${TOK_CEIL}"
fi

pass "issue ${ISSUE}: streak=${STREAK}/${NP_THRESH} attempt=${ATT}/${MAX_ATT} tokens=${USED}/${TOK_CEIL}"
