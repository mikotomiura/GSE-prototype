#!/usr/bin/env bash
# 1 コマンド再現（reproducibility-discipline ルール 4）
set -euo pipefail
cd "$(dirname "$0")"
DATASET="${GSE_DATASET:-${DATASET_ROOT:-$HOME/gse-dataset}}"
SEED=$(grep -oE 'PERMUTATION_SEED=([0-9]+)' SEED | grep -oE '[0-9]+')
echo "[run] dataset=$DATASET seed=$SEED"
python3 analyze.py --dataset "$DATASET" --seed "$SEED" \
  --derivation-pid P013 --out metrics.json
