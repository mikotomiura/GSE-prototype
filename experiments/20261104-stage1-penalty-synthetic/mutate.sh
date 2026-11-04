#!/usr/bin/env bash
# 変異（conditions.md C5）: 名指しの門が赤（終了コード 3）になることを確かめる。合成のデータだけ。
set -uo pipefail
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SC="$EXP_DIR/scripts"; OUT="${OUT:-$EXP_DIR/results}/mutations"; SEED="$(cat "$EXP_DIR/SEED")"
RUN_ID="${RUN_ID:?RUN_ID が要る（run.sh が渡す）}"
PY="${PYTHON:-python3}"; JOBS="${JOBS:-8}"
rm -rf "$OUT"; mkdir -p "$OUT"
run() {
  local m="$1" g="$2"
  "$PY" -I -X utf8 "$SC/selftest.py" "$SEED" "$OUT/$m.json" --only "$g" --mutate "$m" --jobs "$JOBS" --run-id "$RUN_ID" > "$OUT/$m.log" 2>&1
  echo $? > "$OUT/$m.exit"
}
run m1 G2
run m2 G3
run m3 G1
run m4 G8
run m5 G4
