#!/usr/bin/env bash
# 感度の合成の CoAuthor の複製に最頻値の分解を当てる（conditions.md）。実データは使わない。selftest → 変異 → 本計算 → provenance。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SENS="$EXP_DIR/../20261110-per-person-sensitivity/results"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
JOBS="${JOBS:-8}"
PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)-$$}"
[ "$(cat "$EXP_DIR/SEED")" = 2026111001 ] || { echo "SEED が条件の値と違う" >&2; exit 1; }
mkdir -p "$OUT"
"$PY" -I -X utf8 "$SC/selftest.py" "$OUT/selftest.json" --run-id "$RUN_ID" --jobs "$JOBS"
OUT="$OUT" RUN_ID="$RUN_ID" JOBS="$JOBS" PYTHON="$PY" bash "$EXP_DIR/mutate.sh"
"$PY" -I -X utf8 "$SC/check_mutations.py" "$OUT/mutations" "$RUN_ID"
prov() {
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" \
  "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261111-sensitivity-mode-decomposition experiments/20261110-per-person-sensitivity/scripts experiments/20261110-per-person-sensitivity/results experiments/20261106-tau-mode-candidate/scripts experiments/20261104-timeseries-tau-extend/scripts)" \
  "$EXP_DIR" "$RUN_ID" "$JOBS" "$OUT/$1" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
head, dirty, exp, run_id, jobs, out = sys.argv[1:7]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
sys.path.insert(0, os.path.join(exp, "scripts"))
import pinned2
P = dict(run_id=run_id, git_head=head, uncommitted=dirty.splitlines(), jobs=int(jobs),
         python=platform.python_version(), numpy=numpy.__version__, machine=platform.platform(),
         scripts={os.path.basename(p): h(p) for p in sorted(glob.glob(os.path.join(exp, "scripts", "*.py")))},
         run_sh=h(os.path.join(exp, "run.sh")), mutate_sh=h(os.path.join(exp, "mutate.sh")),
         conditions=h(os.path.join(exp, "conditions.md")), seed_file=h(os.path.join(exp, "SEED")),
         pinned=pinned2.hashes())
s = os.path.join(os.path.dirname(out), "summary.json")
if os.path.exists(s):
    S = json.load(open(s))
    P["summary_sha256"] = h(s)
    P["seconds"] = S.get("seconds")
json.dump(P, open(out, "w"), indent=1)
PY
}
prov provenance.pre.json
"$PY" -I -X utf8 "$SC/run_decomp.py" "$SENS" "$OUT" "$JOBS" --run-id "$RUN_ID"
prov provenance.json
echo "終わり: $RUN_ID"
