#!/usr/bin/env bash
# 停滞の手前の推定の上がり（conditions.md）。前の実験の 2 回目の中間を使う（replay はやり直さない）。
# 中間が無ければ experiments/20261031-coauthor-pre-request-signal/run2.sh で作る。
# Step 0 の逸脱は前の実験と同じ（capabilities_gate は GSE のログ用）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${COAUTHOR_DIR:=$HOME/gse-public-data/coauthor}"
WORK="$COAUTHOR_DIR/work2_dwell100"
OUT="$EXP_DIR/results"
[ -d "$WORK/writers" ] || bash "$REPO_ROOT/experiments/20261031-coauthor-pre-request-signal/run2.sh"
mkdir -p "$OUT"
python3 -I "$EXP_DIR/scripts/analyze_stall.py" "$WORK" "$COAUTHOR_DIR/raw/metadata_creative.csv" \
  "$COAUTHOR_DIR/raw/metadata_argumentative.csv" "$(cat "$EXP_DIR/SEED")" "$OUT"
python3 -I -c "import json,sys;json.dump({'git_head':sys.argv[1]},open(sys.argv[2],'w'),indent=1)" "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$OUT/provenance.json"
# 探索（事前に決めていない・notes.md の「探索」）
python3 -I "$EXP_DIR/scripts/explore_raw.py" "$WORK" "$COAUTHOR_DIR/raw/metadata_creative.csv" \
  "$COAUTHOR_DIR/raw/metadata_argumentative.csv" "$(cat "$EXP_DIR/SEED")" "$OUT/explore_raw.json" > /dev/null
