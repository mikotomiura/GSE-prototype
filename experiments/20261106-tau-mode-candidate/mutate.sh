#!/usr/bin/env bash
# 変異（conditions.md の V2・前の試験の m1〜m3・m6〜m8・m11〜m15 に m16〜m27 を足した）: 名指しの対照が赤（終了コード 3）になることを確かめる。合成のデータだけを使う。
# 出力先を走る前に空にし、各実行に今回の実行の識別子を渡して JSON に書かせる（B の判断 11 の直し）。
set -uo pipefail
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SC="$EXP_DIR/scripts"; OUT="${OUT:-$EXP_DIR/results}/mutations"; SEED="$(cat "$EXP_DIR/SEED")"
RUN_ID="${RUN_ID:?RUN_ID が要る（run.sh が渡す）}"
rm -rf "$OUT"
mkdir -p "$OUT"
PY="${PYTHON:-python3}"
run() {
  local m="$1" ctl="$2"
  "$PY" -I -X utf8 "$SC/ml.py" --selftest "$SEED" "$OUT/$m.json" --mutate "$m" --only "$ctl" --run-id "$RUN_ID" > "$OUT/$m.log" 2>&1
  echo $? > "$OUT/$m.exit"
}
run m1 P-LEAK
run m2 P-AR1
run m3 P-PRIOR
run m6 P-S
run m7 P-S
run m8 P-OTH
run m11 P-INF
run m12 P-JOINT
run m13 P-PR1
run m14 P-SUBSET
run m15 P-TAU
run m16 P-MODE
run m17 P-MODE,P-LIMIT
run m18 P-NEGINF
run m19 P-NEGINF
run m20 P-INFCI
run m21 P-AB
run m22 P-NOSEL
run m23 P-SAME
run m24 P-SAVE
run m25 P-NEGINF
run m26 P-FINITE
run m27 P-NEGINF
