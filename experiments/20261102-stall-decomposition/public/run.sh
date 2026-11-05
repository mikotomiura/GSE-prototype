#!/usr/bin/env bash
# 公開データの停滞の型（../conditions.md）。データと中間は repo の外。記述だけ・検定なし。
# 俯瞰（20261102-public-data-landscape）の中間を使い回す。作り直さない。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
LAND="$DATA_DIR/landscape"
KTAR="$DATA_DIR/klicke/work.tar.gz"
CZIP="$DATA_DIR/coauthor/raw/coauthor.zip"
META=("$DATA_DIR/coauthor/raw/metadata_creative.csv" "$DATA_DIR/coauthor/raw/metadata_argumentative.csv")
OUT="${OUT:-$HERE/results}"
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
[ "$(sha "$CZIP")" = 8d7380ca3811c671e774e43bfb9f5d3265e2a5d425788a066a612831aa1e418b ] || { echo "coauthor.zip の SHA-256 が違う" >&2; exit 1; }
[ "$(sha "${META[0]}")" = 66fd2ca541999412de4050a85c17274f02eea04424e83906b697f4cd824c65bf ] || { echo "metadata_creative の SHA-256 が違う" >&2; exit 1; }
[ "$(sha "${META[1]}")" = cfadf031b21c07951f648b02422b6703850359c7ff6a78a8ef513624c8e4c0d1 ] || { echo "metadata_argumentative の SHA-256 が違う" >&2; exit 1; }
python3 -I "$HERE/analyze_public.py" --selftest
mkdir -p "$OUT"
python3 -I "$HERE/analyze_public.py" "$KTAR" "$LAND/klicke_side.json" "$LAND/coauthor_work" "$LAND/holdout.json" "$OUT" "$CZIP" "${META[@]}"
python3 -I - "$REPO_ROOT" "$KTAR" "$LAND" "$HERE" "$OUT/provenance.json" <<'PY'
import glob, hashlib, json, os, subprocess, sys
root, ktar, land, here, out = sys.argv[1:]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
cw = sorted(glob.glob(os.path.join(land, "coauthor_work", "*.json")))
cat = hashlib.sha256()
for p in cw:
    cat.update(os.path.basename(p).encode()); cat.update(h(p).encode())
json.dump({"git_head": subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(),
           "git_dirty_paths": [l for l in subprocess.check_output(["git", "-C", root, "status", "--porcelain", "--", "experiments/20261102-stall-decomposition", ":!experiments/20261102-stall-decomposition/public/results"], text=True).splitlines() if l],
           "klicke_work_tar_sha256": h(ktar), "klicke_side_sha256": h(os.path.join(land, "klicke_side.json")),
           "holdout_sha256": h(os.path.join(land, "holdout.json")),
           "coauthor_work_files": len(cw), "coauthor_work_digest": cat.hexdigest(),
           "scripts_sha256": {os.path.relpath(p, root): h(p) for p in [os.path.join(here, "analyze_public.py"), os.path.join(here, "../types_core.py"), os.path.join(here, "../../20261102-public-data-landscape/scripts/analyze_landscape.py"), os.path.join(here, "../../20261101-klicke-early-stall-trigger/scripts/analyze_item2.py")]}},
          open(out, "w"), indent=1)
PY
