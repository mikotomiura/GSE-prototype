#!/usr/bin/env bash
# S1-E5 の区間の作り方とブロックの長さを模擬の被覆で選ぶ（conditions.md）。データはすべて合成。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${OUT:-$EXP_DIR/results}"; SEED="$(cat "$EXP_DIR/SEED")"; PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
mkdir -p "$OUT"
DIRTY="$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261126-stage1-resampling-coverage experiments/20261103-mhd-dryrun-v2/scripts/daysim.py)"
"$PY" -I -X utf8 - "$OUT/provenance.json" "$REPO_ROOT" "$SEED" "$DIRTY" <<'PY'
import hashlib, json, platform, subprocess, sys, numpy
out, root, seed, dirty = sys.argv[1:5]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
files = ["experiments/20261126-stage1-resampling-coverage/" + f for f in ("scripts/coverage.py", "conditions.md", "SEED", "run.sh")] + ["experiments/20261103-mhd-dryrun-v2/scripts/daysim.py"]
json.dump(dict(head=subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(), dirty=dirty, seed=int(seed),
               python=platform.python_version(), numpy=numpy.__version__, sha256={f: h(f"{root}/{f}") for f in files}), open(out, "w"), indent=1)
PY
"$PY" -I -X utf8 "$EXP_DIR/scripts/coverage.py" "$SEED" "$OUT"
