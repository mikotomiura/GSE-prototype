#!/usr/bin/env bash
# 手順の感度を合成で確かめる（conditions.md）。実データは使わない。selftest → 変異 → 本計算（時間の規則つき）→ report → provenance。
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
mkdir -p "$OUT"
# 読み込むコードの SHA-256（pinned.py が外れれば止める）
"$PY" -I -X utf8 -c "import sys; sys.path.insert(0, '$SC'); import pinned"
"$PY" -I -X utf8 "$SC/sens_selftest.py" "$SEED" "$OUT/selftest.json" --run-id "$RUN_ID" --jobs "$JOBS"
OUT="$OUT" RUN_ID="$RUN_ID" PYTHON="$PY" bash "$EXP_DIR/mutate.sh"
"$PY" -I -X utf8 "$SC/sens_check_mutations.py" "$OUT/mutations" "$OUT/selftest.json" "$RUN_ID"
"$PY" -I -X utf8 "$SC/run_synth.py" "$SEED" "$OUT" "$JOBS" --run-id "$RUN_ID"
"$PY" -I -X utf8 "$SC/sens_report.py" "$OUT" --run-id "$RUN_ID"
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261110-per-person-sensitivity experiments/20261104-timeseries-tau-extend/scripts)" \
  "$EXP_DIR" "$RUN_ID" "$JOBS" "$OUT/provenance.json" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
head, dirty, exp, run_id, jobs, out = sys.argv[1:7]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
sys.path.insert(0, os.path.join(exp, "scripts"))
import pinned
P = dict(run_id=run_id, git_head=head, uncommitted=dirty.splitlines(), jobs=int(jobs),
         python=platform.python_version(), numpy=numpy.__version__, machine=platform.platform(),
         scripts={os.path.basename(p): h(p) for p in sorted(glob.glob(os.path.join(exp, "scripts", "*.py")))},
         run_sh=h(os.path.join(exp, "run.sh")), mutate_sh=h(os.path.join(exp, "mutate.sh")),
         conditions=h(os.path.join(exp, "conditions.md")), seed_file=h(os.path.join(exp, "SEED")),
         pinned=pinned.hashes())
json.dump(P, open(out, "w"), indent=1)
PY
echo "終わり: $RUN_ID"
