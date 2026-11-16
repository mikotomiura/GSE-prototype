#!/usr/bin/env bash
# R1 の定義の検査の 2 回目（conditions-2.md）。使い方: ./run2.sh length|grid|klicke
set -euo pipefail
MODE="$1"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$EXP_DIR/../.." && pwd)"
DATA_DIR="${DATA_DIR:-$HOME/gse-public-data}"
PY="${DEFCHECK_PY:-$DATA_DIR/venv-findings1/bin/python}"
WORK="$DATA_DIR/cs1/work2019_holdout"
HOLD="$DATA_DIR/cs1/holdout.json"
KWORK="$DATA_DIR/klicke/work"
RUN1="$EXP_DIR/results/defcheck.json"
KREF="$REPO_ROOT/experiments/20261106-findings-paper1-exploration/results/explore_klicke.json"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CONFIRM_JOBS="${CONFIRM_JOBS:-8}"
case "$MODE" in
  length|grid)
    got=$(shasum -a 256 "$HOLD" | cut -d' ' -f1)
    [ "$got" = a5a32fcefeb97b038afd170e2672262fd5a71230d5e851319eaa076b606bdc47 ] || { echo "holdout.json の SHA-256 が違う" >&2; exit 2; }
    "$PY" -I "$EXP_DIR/scripts/defcheck2.py" "$MODE" "$WORK" "$HOLD" "$RUN1" "${OUT:-$EXP_DIR/results/$MODE.json}" ;;
  klicke)
    n=$(ls "$KWORK" | grep -c '^w[0-9]*\.json$' || true)
    [ "$n" = 4992 ] || { echo "KLiCKe の中間の書き手が 4,992 でない（$n）" >&2; exit 2; }
    "$PY" -I "$EXP_DIR/scripts/defcheck2.py" klicke "$KWORK" "$KREF" "${OUT:-$EXP_DIR/results/klicke.json}" ;;
  *) echo "mode は length・grid・klicke" >&2; exit 2 ;;
esac
