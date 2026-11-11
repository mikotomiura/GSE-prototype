#!/usr/bin/env bash
# 追記（2026-11-11）: CS1 の種を足す 6 本（conditions.md の追記）。P-REREP → 6 本 → report（前の 27 本と合わせて）→ provenance_add。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
SEED="$(cat "$EXP_DIR/SEED")"
JOBS="${JOBS:-8}"
PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)-$$}"
"$PY" -I -X utf8 -c "import sys; sys.path.insert(0, '$SC'); import pinned"
"$PY" -I -X utf8 "$SC/run_add.py" "$SEED" "$OUT" "$JOBS" --run-id "$RUN_ID"
"$PY" -I -X utf8 "$SC/sens_report.py" "$OUT" --run-id "$RUN_ID"
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261110-per-person-sensitivity/scripts experiments/20261110-per-person-sensitivity/run_add.sh experiments/20261110-per-person-sensitivity/conditions.md experiments/20261104-timeseries-tau-extend/scripts)" \
  "$EXP_DIR" "$RUN_ID" "$JOBS" "$OUT/provenance_add.json" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
head, dirty, exp, run_id, jobs, out = sys.argv[1:7]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
sys.path.insert(0, os.path.join(exp, "scripts"))
import pinned
d = os.path.dirname(out)
P = dict(run_id=run_id, git_head=head, uncommitted=dirty.splitlines(), jobs=int(jobs),
         python=platform.python_version(), numpy=numpy.__version__, machine=platform.platform(),
         scripts={os.path.basename(p): h(p) for p in sorted(glob.glob(os.path.join(exp, "scripts", "*.py")))},
         run_add_sh=h(os.path.join(exp, "run_add.sh")), conditions=h(os.path.join(exp, "conditions.md")),
         seed_file=h(os.path.join(exp, "SEED")), pinned=pinned.hashes(),
         plan_add=dict(sha256=h(os.path.join(d, "plan_add.json")), content=json.load(open(os.path.join(d, "plan_add.json")))),
         summary_sha256=h(os.path.join(d, "summary.json")))
json.dump(P, open(out, "w"), indent=1)
PY
echo "終わり: $RUN_ID"
