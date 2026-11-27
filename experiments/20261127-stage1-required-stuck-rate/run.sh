#!/usr/bin/env bash
# 1 コマンドで再現する: bash run.sh
set -euo pipefail
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
PY="${PYTHON:-$HOME/gse-venvs/handmark-desk/bin/python}"
"$PY" -I scripts/required_rate.py --selftest
"$PY" -I scripts/required_rate.py "$(cat SEED)" results 300 > results/run.log
# 第 2 版（3 名を合わせた判定と下限）
"$PY" -I scripts/pooled.py --selftest
"$PY" -I scripts/pooled.py "$(cat SEED)" results 300 10 > results/pooled_run.log
