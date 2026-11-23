#!/usr/bin/env bash
# MhD の配管の空回し（conditions.md）。データと中間は repo の外。代理のラベルで、詰まりの推定ではない。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
WORK="$DATA_DIR/landscape/coauthor_work"
OUT="${OUT:-$EXP_DIR/results}"
SEED="$(cat "$EXP_DIR/SEED")"
python3 -I "$EXP_DIR/scripts/dryrun.py" --selftest "$WORK" "$SEED"
python3 -I "$EXP_DIR/scripts/dryrun.py" "$WORK" "$SEED" "$OUT"
python3 -I -c "import json,sys,hashlib,glob,os;h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest();fs=sorted(glob.glob(sys.argv[3]+'/s*.json'));json.dump({'git_head':sys.argv[1],'git_dirty_paths':[l for l in sys.argv[2].splitlines() if l],'script_sha256':h(sys.argv[4]),'input_files':len(fs),'input_sha256_of_sha256_list':hashlib.sha256(''.join(os.path.basename(f)+h(f) for f in fs).encode()).hexdigest(),'python':sys.version.split()[0]},open(sys.argv[5],'w'),indent=1)" \
  "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$(git -C "$REPO_ROOT" status --porcelain -- experiments/20261103-mhd-pipeline-dryrun/scripts experiments/20261103-mhd-pipeline-dryrun/run.sh)" \
  "$WORK" "$EXP_DIR/scripts/dryrun.py" "$OUT/provenance.json"
