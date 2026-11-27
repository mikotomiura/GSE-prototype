#!/usr/bin/env bash
# 変異（conditions の V2・m61〜m83）: 名指しの対照が赤（終了コード 3）になることを確かめる。合成のデータだけを使う。
# 出力先を走る前に空にし、各実行に今回の実行の識別子を渡して JSON に書かせる（S13 と同じ門）。
set -uo pipefail
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SC="$EXP_DIR/scripts"; OUT="${OUT:-$EXP_DIR/results}/mutations"; SEED="$(cat "$EXP_DIR/SEED")"
RUN_ID="${RUN_ID:?RUN_ID が要る（run.sh が渡す）}"
JOBS="${JOBS:-4}"
rm -rf "$OUT"
mkdir -p "$OUT"
PY="${PYTHON:-python3}"
run() {
  local m="$1" ctl="$2"
  "$PY" -I -X utf8 "$SC/selftest_dose.py" "$SEED" "$OUT/$m.json" --mutate "$m" --only "$ctl" --run-id "$RUN_ID" --jobs "$JOBS" > "$OUT/$m.log" 2>&1
  echo $? > "$OUT/$m.exit"
}
run m61 P-STRIDE
run m62 P-STRIDE
run m63 P-PHASE
run m64 P-PHASE
run m65 P-MI
run m66 P-MI
run m67 P-FIRST
run m68 P-SWAP
run m69 P-READ
run m70 P-BLOCK
run m71 P-BLOCK
run m72 P-DS
run m74 P-PAIR
run m75 P-READ
run m76 P-TIME
run m77 P-MI
run m79 P-READ
run m80 P-MI
run m81 P-PAIR
run m82 P-READ
run m83 P-READ
