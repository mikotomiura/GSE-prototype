#!/usr/bin/env bash
# フォーカスの遷移と受領（conditions.md）。研究者本人の O1 の記録（この Mac）から集計だけを出す。
# 中間（停滞の始まりの行だけ）は repo の外に置く。NDJSON と中間を外部の LLM に送らない（data-privacy）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${GSE_SESSIONS:=$HOME/Documents/GSE-sessions}"
: "${WORK:=$HOME/gse-o1-derived/20261101-focus-leave-before-receipt}"
OUT="$EXP_DIR/results"
mkdir -p "$WORK" "$OUT"
(cd "$REPO_ROOT/src-tauri" && cargo build --bin gse-replay)
REPLAY="$REPO_ROOT/src-tauri/target/debug/gse-replay"
for f in "$GSE_SESSIONS"/gse_o1_*.ndjson; do
  b="$(basename "$f" .ndjson)"
  [ -s "$WORK/$b.onsets.json" ] && continue
  "$REPLAY" "$f" --features > "$WORK/tmp.json" 2> "$WORK/$b.err"
  python3 -I "$EXP_DIR/scripts/slim.py" "$WORK/tmp.json" "$WORK/$b.onsets.json"
  rm -f "$WORK/tmp.json"
done
python3 -I "$EXP_DIR/scripts/analyze.py" "$WORK" "$GSE_SESSIONS" "$(cat "$EXP_DIR/SEED")" "$OUT"
python3 -I -c "import json,sys;json.dump({'git_head':sys.argv[1],'replay_parse_failures':sys.argv[2]},open(sys.argv[3],'w'),indent=1)" \
  "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$(cat "$WORK"/*.err | grep -c 'failed to parse' || true)" "$OUT/provenance.json"
