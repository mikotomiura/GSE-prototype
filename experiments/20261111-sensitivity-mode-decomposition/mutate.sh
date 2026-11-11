#!/usr/bin/env bash
# 変異（conditions.md V1）: 名指しの門が赤（終了コード 3）になることを確かめる。合成だけ。全門を回す。
set -uo pipefail
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SC="$EXP_DIR/scripts"; OUT="${OUT:-$EXP_DIR/results}/mutations"
RUN_ID="${RUN_ID:?RUN_ID が要る（run.sh が渡す）}"
JOBS="${JOBS:-8}"
PY="${PYTHON:-python3}"
rm -rf "$OUT"
mkdir -p "$OUT"
for m in u1 u2 u3 u4 u5; do
  "$PY" -I -X utf8 "$SC/selftest.py" "$OUT/$m.json" --mutate "$m" --run-id "$RUN_ID" --jobs "$JOBS" > "$OUT/$m.log" 2>&1
  echo $? > "$OUT/$m.exit"
done
