#!/usr/bin/env bash
# 段 1 の罰の強さ —— 弱い信号での確かめ（conditions.md）。データはすべて合成。
# HMM_VERSION・gse-dataset は当たらない（GSE の推定とログを使わない）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREV="$REPO_ROOT/experiments/20261104-stage1-penalty-synthetic"
OUT="${OUT:-$EXP_DIR/results}"; SC="$EXP_DIR/scripts"; SEED="$(cat "$EXP_DIR/SEED")"
JOBS="${JOBS:-8}"; REPS="${REPS:-400}"; PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="$(date +%Y%m%dT%H%M%S)-$$"
mkdir -p "$OUT"
# 来歴は計算の前に取り、途中で落ちても書く（trap）。前の実験の sim.py・report.py・summary.json も刻む
HEAD="$(git -C "$REPO_ROOT" rev-parse HEAD)"
DIRTY="$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261104-stage1-penalty-weak-signal/scripts experiments/20261104-stage1-penalty-weak-signal/run.sh experiments/20261104-stage1-penalty-weak-signal/mutate.sh experiments/20261104-stage1-penalty-weak-signal/conditions.md experiments/20261104-stage1-penalty-weak-signal/SEED experiments/20261104-stage1-penalty-synthetic/scripts experiments/20261104-stage1-penalty-synthetic/results/summary.json)"
STAGE="start"
write_prov() {
  local rc=$?
  "$PY" -I -X utf8 - "$HEAD" "$DIRTY" "$EXP_DIR" "$PREV" "$RUN_ID" "$REPS" "$JOBS" "$OUT/provenance.json" "$STAGE" "$rc" <<'PY' || true
import glob, hashlib, json, os, platform, sys
import numpy
head, dirty, exp, prev, run_id, reps, jobs, out, stage, rc = sys.argv[1:11]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
files = sorted(glob.glob(os.path.join(exp, "scripts", "*.py"))) + [os.path.join(exp, f) for f in ("run.sh", "mutate.sh", "conditions.md", "SEED")]
pfiles = [os.path.join(prev, "scripts", f) for f in ("sim.py", "report.py", "selftest.py")] + [os.path.join(prev, "results", "summary.json")]
json.dump(dict(run_id=run_id, git_head=head, dirty=dirty.splitlines(), reps=int(reps), jobs=int(jobs),
               last_stage=stage, exit_code=int(rc),
               python=platform.python_version(), numpy=numpy.__version__, machine=platform.platform(),
               sha256={os.path.relpath(f, exp): h(f) for f in files + pfiles}),
          open(out, "w"), ensure_ascii=False, indent=1)
PY
}
trap write_prov EXIT
rm -rf "$OUT/raw" "$OUT/summary.json" "$OUT/tables.md" "$OUT/provenance.json"
STAGE="selftest"
"$PY" -I -X utf8 "$SC/selftest_weak.py" "$SEED" "$OUT/selftest.json" --run-id "$RUN_ID"
STAGE="mutations"
OUT="$OUT" RUN_ID="$RUN_ID" PYTHON="$PY" bash "$EXP_DIR/mutate.sh"
"$PY" -I -X utf8 "$SC/check_mutations.py" "$OUT/mutations" "$RUN_ID"
STAGE="sim"
"$PY" -I -X utf8 "$SC/weak.py" "$SEED" "$OUT" "$JOBS" --reps "$REPS" --run-id "$RUN_ID"
STAGE="report"
"$PY" -I -X utf8 "$SC/report_weak.py" "$OUT" --run-id "$RUN_ID"
STAGE="done"
echo "done: $RUN_ID"
