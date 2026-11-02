#!/usr/bin/env bash
# 段 1 の残りの確かめ（checks/conditions.md）。中間は上の 2 つの run.sh が作ったものを使う（作り直さない）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXP="$(cd "$HERE/.." && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
: "${GSE_SESSIONS:=$HOME/Documents/GSE-sessions}"
: "${WORK:=$HOME/gse-o1-derived/20261102-stall-decomposition}"
LAND="$DATA_DIR/landscape"
OUT="${OUT:-$HERE/results}"
COND_TS="$(git -C "$REPO_ROOT" log -1 --format=%ct 28a91da0)"
FILES=()
for f in "$GSE_SESSIONS"/gse_o1_*.ndjson; do
  d="$(basename "$f" .ndjson | cut -d_ -f3)"
  { [ "$d" \< 20261018 ] || [ "$d" \> 20261101 ]; } && continue
  [ "$(stat -f %m "$f")" -lt "$COND_TS" ] || continue
  FILES+=("$f")
done
[ "${#FILES[@]}" -eq 18 ] || { echo "O1 のファイルが上の条件の 18 本でない" >&2; exit 1; }
python3 -I "$HERE/analyze_checks.py" --selftest
mkdir -p "$OUT"
python3 -I "$HERE/analyze_checks.py" "$(cat "$EXP/SEED")" "$OUT/checks.json" "$DATA_DIR/klicke/work.tar.gz" "$LAND/klicke_side.json" \
  "$LAND/coauthor_work" "$LAND/holdout.json" "$DATA_DIR/coauthor/raw/coauthor.zip" \
  "$DATA_DIR/coauthor/raw/metadata_creative.csv" "$DATA_DIR/coauthor/raw/metadata_argumentative.csv" "$WORK" "${FILES[@]}"
python3 -I - "$REPO_ROOT" "$HERE" "$OUT/provenance.json" <<'PY'
import hashlib, json, os, subprocess, sys
root, here, out = sys.argv[1:]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
json.dump({"git_head": subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(),
           "git_dirty_paths": [l for l in subprocess.check_output(["git", "-C", root, "status", "--porcelain", "--", "experiments/20261102-stall-decomposition", ":!experiments/20261102-stall-decomposition/checks/results"], text=True).splitlines() if l],
           "scripts_sha256": {os.path.relpath(p, root): h(p) for p in [os.path.join(here, "analyze_checks.py"), os.path.join(here, "../types_core.py"), os.path.join(here, "../public/analyze_public.py"), os.path.join(here, "../o1/analyze_o1.py")]}},
          open(out, "w"), indent=1)
PY
