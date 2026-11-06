#!/usr/bin/env bash
# 変異（conditions.md の V2・m41〜m51）: 名指しの対照が赤（終了コード 3）になることを確かめる。合成のデータだけを使う。
# 出力先を走る前に空にし、各実行に今回の実行の識別子を渡して JSON に書かせる（tau-extend と同じ門）。
set -uo pipefail
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SC="$EXP_DIR/scripts"; OUT="${OUT:-$EXP_DIR/results}/mutations"; SEED="$(cat "$EXP_DIR/SEED")"
RUN_ID="${RUN_ID:?RUN_ID が要る（run.sh が渡す）}"
rm -rf "$OUT"
mkdir -p "$OUT"
PY="${PYTHON:-python3}"
run() {
  local m="$1" ctl="$2"
  "$PY" -I -X utf8 "$SC/selftest.py" "$SEED" "$OUT/$m.json" --mutate "$m" --only "$ctl" --run-id "$RUN_ID" > "$OUT/$m.log" 2>&1
  echo $? > "$OUT/$m.exit"
}
run m41 P-RAW
run m42 P-U
run m43 P-THIN
run m44 P-THIN
run m45 P-RES-CAL
run m46 P-RES-CAL
run m47 P-RES-MIS
run m48 P-CRN
run m49 P-NPZ
run m50 P-SAME
run m51 P-PIN
