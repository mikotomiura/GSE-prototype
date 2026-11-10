#!/usr/bin/env bash
# 変異（conditions.md V1）: 名指しの対照が赤（終了コード 3）になることを確かめる。合成だけ。
set -uo pipefail
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SC="$EXP_DIR/scripts"; OUT="${OUT:-$EXP_DIR/results}/mutations"; SEED="$(cat "$EXP_DIR/SEED")"
RUN_ID="${RUN_ID:?RUN_ID が要る（run.sh が渡す）}"
rm -rf "$OUT"
mkdir -p "$OUT"
PY="${PYTHON:-python3}"
run() {
  local m="$1" ctl="$2"
  "$PY" -I -X utf8 "$SC/sens_selftest.py" "$SEED" "$OUT/$m.json" --mutate "$m" --only "$ctl" --run-id "$RUN_ID" > "$OUT/$m.log" 2>&1
  echo $? > "$OUT/$m.exit"
}
run v1 P-DIFF
run v2 P-PLANT0
run v3 P-JOINTW
run v4 P-GROUP
run v5 P-SPLIT
