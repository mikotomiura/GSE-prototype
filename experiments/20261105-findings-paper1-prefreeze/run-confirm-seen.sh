#!/usr/bin/env bash
# 凍結の前の計算 2（conditions-2.md）: 確認の解析スクリプトを見た書き手で空回しする。判定の値は書かない。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
PY="${CONFIRM_PY:-$DATA_DIR/venv-findings1/bin/python}"
OUT="$EXP_DIR/results"
[ "$("$PY" -m pip freeze)" = "$(cat "$EXP_DIR/requirements-confirm.txt")" ] || { echo "環境が requirements-confirm.txt と違う" >&2; exit 1; }
[ "$(shasum -a 256 "$DATA_DIR/cs1/holdout.json" | cut -d' ' -f1)" = a5a32fcefeb97b038afd170e2672262fd5a71230d5e851319eaa076b606bdc47 ] || { echo "取り置きの一覧が違う" >&2; exit 1; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
"$PY" -I "$EXP_DIR/scripts/confirm_p1.py" --selftest
"$PY" -I "$EXP_DIR/scripts/confirm_p1.py" seen "$DATA_DIR/cs1/work2019" "$DATA_DIR/cs1/holdout.json" "$DATA_DIR/klicke/work" 20261106 "$OUT"
"$PY" -I -c "import json,sys,hashlib;h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest();json.dump({'git_head':sys.argv[1],'git_dirty_paths':[l for l in sys.argv[2].splitlines() if l],'confirm_p1_sha256':h(sys.argv[3]),'prefreeze_sha256':h(sys.argv[4])},open(sys.argv[5],'w'),indent=1)" \
  "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$(git -C "$REPO_ROOT" status --porcelain -- experiments/20261105-findings-paper1-prefreeze/scripts experiments/20261105-findings-paper1-prefreeze/run-confirm-seen.sh)" \
  "$EXP_DIR/scripts/confirm_p1.py" "$EXP_DIR/scripts/prefreeze.py" "$OUT/provenance_confirm_seen.json"
