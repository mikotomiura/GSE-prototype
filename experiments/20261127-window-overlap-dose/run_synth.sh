#!/usr/bin/env bash
# 合成のデータだけの門（conditions V2・D6）: P-PIN・引き継ぐ selftest（S13 と tau-extend をそのまま）・足す陽性対照・変異・
# 配管の通し・時間の見積もり。実データは読まない。実データの本計算（run.sh）はこの出力が全部通ったときだけ進む。
set -euo pipefail
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S13_EXP="$EXP_DIR/../20261107-unsmoothed-residual-check"
TSC="$EXP_DIR/../20261104-timeseries-tau-extend/scripts"
SC="$EXP_DIR/scripts"
OUT="${OUT:-$EXP_DIR/results}"
SEED="$(cat "$EXP_DIR/SEED")"
JOBS="${JOBS:-6}"
PY="${PYTHON:?PYTHON が要る（repo の外の仮想環境・Python 3.11・numpy 2.4.4）}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="${RUN_ID:-synth-$(date +%Y%m%dT%H%M%S)-$$}"
mkdir -p "$OUT"
stamp() { echo "[$(date +%H:%M:%S)] $*"; }
stamp "P-PIN"
"$PY" -I -X utf8 - "$SC" > "$OUT/pin_check.json" <<'PY' || { echo "P-PIN が外れた" >&2; exit 4; }
import json, sys
sys.path.insert(0, sys.argv[1])
import swap
print(json.dumps(dict(swap.PIN), indent=1))
sys.exit(0 if swap.PIN["pin_ok"] else 4)
PY
stamp "引き継ぐ対照（S13 の selftest.py・repro_check.py の selftest、tau-extend の ml.py --selftest をそのまま）"
"$PY" -I -X utf8 "$S13_EXP/scripts/selftest.py" "$SEED" "$OUT/selftest_s13.json" --run-id "$RUN_ID"
"$PY" -I -X utf8 "$S13_EXP/scripts/repro_check.py" --selftest > "$OUT/repro_check_selftest.json"
"$PY" -I -X utf8 "$TSC/ml.py" --selftest "$SEED" "$OUT/selftest_inherited.json" --run-id "$RUN_ID" \
  --only P-XI,P-BATCH,P-EM3,P-AR1,P-PRIOR,P-CH,P-POOL,P-AR,P-LEAK,P-EM2,P-S,P-OTH,P-INF,P-JOINT,P-PR1
stamp "足す陽性対照（P-STRIDE〜P-READ）"
"$PY" -I -X utf8 "$SC/selftest_dose.py" "$SEED" "$OUT/selftest.json" --run-id "$RUN_ID" --jobs "$JOBS"
stamp "変異（m61〜m83）"
OUT="$OUT" RUN_ID="$RUN_ID" PYTHON="$PY" JOBS="$JOBS" bash "$EXP_DIR/mutate.sh"
"$PY" -I -X utf8 "$SC/check_mutations_dose.py" "$OUT/mutations" "$OUT/selftest.json" "$RUN_ID"
stamp "配管の合成の通し（全 21 列・合成のデータだけ）"
"$PY" -I -X utf8 "$SC/e2e_dose.py" "$SEED" "$OUT/e2e_synth.json" "$JOBS"
stamp "時間の見積もり"
"$PY" -I -X utf8 "$SC/timing_dose.py" "$SEED" "$S13_EXP/results/timing.json" "$S13_EXP/results/summary.json" \
  "$OUT/e2e_synth.json" "$OUT/timing.json" "$JOBS"
echo "$RUN_ID" > "$OUT/synth_run_id"
stamp "済んだ（合成）"
