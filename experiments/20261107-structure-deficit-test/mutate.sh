#!/usr/bin/env bash
# 変異（conditions.md の V2・前の試験の m1〜m3・m6〜m8・m15 を引き継ぎ、m31〜m39 を足した）: 名指しの対照が赤（終了コード 3）になることを確かめる。合成のデータだけを使う。
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
run m15 P-TAU
run m31 P-Q
run m32 P-Q
run m33 P-SHUF
run m34 P-SHUF
run m35 P-QW
run m36 P-D
run m37 P-OTHER
run m38 P-OTHER
run m39 P-SAME
