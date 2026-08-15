#!/usr/bin/env bash
# 1 コマンド再現 — experiments/20260815-expression-power
# reproducibility-discipline ルール 4。
#
# 使い方:
#   bash run.sh            # 全部（計算 → アンカー → 要約 → 自己検査）
#   bash run.sh calc       # 検出力計算だけ
#   bash run.sh anchor     # 実測アンカーだけ（★ gse-dataset が要る）
#   bash run.sh selftest   # 自己検査だけ
#
# ⚠️★★ Windows コンソールは cp932。PYTHONIOENCODING / PYTHONUTF8 を必ず立てる
#      （★ experiments/20260812-expression-layer0-drone で実測した落とし穴）。
set -euo pipefail

cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

PY="${PYTHON:-python}"
DATASET="${GSE_DATASET:-C:/gse-dataset}"

calc() {
  echo "== 検出力計算 =="
  "$PY" scripts/power_calc.py \
    --config power.config.json \
    --seed SEED \
    --out results/power.json
}

mc() {
  echo "== 検出力（主経路・並べ替えの直接模擬・numpy）=="
  "$PY" scripts/power_mc.py \
    --config power.config.json \
    --seed SEED \
    --out results/power_mc.json
}

anchor() {
  echo "== 実測アンカー（★ 集計値のみ出力）=="
  if [ -d "$DATASET/raw" ]; then
    "$PY" scripts/block_variance.py --dataset "$DATASET" --out results/block_variance.json
  else
    echo "!! gse-dataset が $DATASET に無い。副アンカーを飛ばす" >&2
  fi
  # ★ 主アンカー: Phase1 コホート（P010–P014）。⚠️ 生ログは repo 外に置く
  if [ -n "${GSE_PHASE1_NDJSON:-}" ] && [ -d "${GSE_PHASE1_NDJSON}" ]; then
    "$PY" scripts/block_variance.py --flat-dir "${GSE_PHASE1_NDJSON}" \
      --out results/block_variance_cohort.json
  else
    echo "!! GSE_PHASE1_NDJSON が未設定。主アンカー（P010-P014）を飛ばす" >&2
  fi
}

summarize() {
  echo "== 要約表の生成 =="
  extra=""
  [ -f results/power_mc.json ] && extra="$extra --power-mc results/power_mc.json"
  [ -f results/block_variance_cohort.json ] && \
    extra="$extra --anchor-cohort results/block_variance_cohort.json"
  "$PY" scripts/summarize.py \
    --power results/power.json \
    --anchor results/block_variance.json \
    $extra \
    --out results/summary.md
}

selftest() {
  echo "== 自己検査（依存ゼロ）=="
  "$PY" scripts/power_selftest.py
  echo "== oracle 検査（numpy / scipy による独立実装との突き合わせ）=="
  if "$PY" -c "import numpy, scipy" 2>/dev/null; then
    "$PY" scripts/oracle_check.py
  else
    echo "!! numpy / scipy が無いので oracle 検査を飛ばす（★ 主結果の再現には影響しない）" >&2
  fi
}

case "${1:-all}" in
  calc) calc ;;
  mc) mc ;;
  anchor) anchor ;;
  summarize) summarize ;;
  selftest) selftest ;;
  all)
    calc
    mc
    anchor
    summarize
    selftest
    ;;
  *)
    echo "usage: bash run.sh [all|calc|mc|anchor|summarize|selftest]" >&2
    exit 2
    ;;
esac
