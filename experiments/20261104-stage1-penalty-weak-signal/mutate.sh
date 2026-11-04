#!/usr/bin/env bash
# 変異（conditions.md W3）: 名指しの門が赤（終了コード 3）になることを確かめる。合成のデータだけ。
set -uo pipefail
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SC="$EXP_DIR/scripts"; OUT="${OUT:-$EXP_DIR/results}/mutations"; SEED="$(cat "$EXP_DIR/SEED")"
RUN_ID="${RUN_ID:?RUN_ID が要る（run.sh が渡す）}"
PY="${PYTHON:-python3}"
rm -rf "$OUT"; mkdir -p "$OUT"
run() {
  local m="$1" g="$2"
  "$PY" -I -X utf8 "$SC/selftest_weak.py" "$SEED" "$OUT/$m.json" --only "$g" --mutate "$m" --run-id "$RUN_ID" > "$OUT/$m.log" 2>&1
  echo $? > "$OUT/$m.exit"
}
run w1 W1
run w2 W2
run w3 W5
run w4 W1
