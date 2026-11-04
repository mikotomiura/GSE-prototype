#!/usr/bin/env bash
# 段 1 のロジスティックの罰の強さの決め方を合成で比べる（conditions.md）。データはすべて合成。
# HMM_VERSION・gse-dataset は当たらない（GSE の推定とログを使わない）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${OUT:-$EXP_DIR/results}"; SC="$EXP_DIR/scripts"; SEED="$(cat "$EXP_DIR/SEED")"
JOBS="${JOBS:-8}"; REPS="${REPS:-400}"; PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="$(date +%Y%m%dT%H%M%S)-$$"
mkdir -p "$OUT"
# 来歴は計算の前に取り、途中で落ちても書く（trap）
HEAD="$(git -C "$REPO_ROOT" rev-parse HEAD)"
DIRTY="$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261104-stage1-penalty-synthetic/scripts experiments/20261104-stage1-penalty-synthetic/run.sh experiments/20261104-stage1-penalty-synthetic/mutate.sh experiments/20261104-stage1-penalty-synthetic/conditions.md experiments/20261104-stage1-penalty-synthetic/SEED)"
STAGE="start"
write_prov() {
  local rc=$?
  "$PY" -I -X utf8 - "$HEAD" "$DIRTY" "$EXP_DIR" "$RUN_ID" "$REPS" "$JOBS" "$OUT/provenance.json" "$STAGE" "$rc" <<'PY' || true
import glob, hashlib, json, os, platform, sys
import numpy
head, dirty, exp, run_id, reps, jobs, out, stage, rc = sys.argv[1:10]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
files = sorted(glob.glob(os.path.join(exp, "scripts", "*.py"))) + [os.path.join(exp, f) for f in ("run.sh", "mutate.sh", "conditions.md", "SEED")]
json.dump(dict(run_id=run_id, git_head=head, dirty=dirty.splitlines(), reps=int(reps), jobs=int(jobs),
               last_stage=stage, exit_code=int(rc),
               python=platform.python_version(), numpy=numpy.__version__, machine=platform.platform(),
               sha256={os.path.relpath(f, exp): h(f) for f in files}),
          open(out, "w"), ensure_ascii=False, indent=1)
PY
}
trap write_prov EXIT
rm -rf "$OUT/raw" "$OUT/summary.json" "$OUT/proposal.json" "$OUT/tables.md" "$OUT/provenance.json"
STAGE="selftest"
# 門（G1〜G8・小さな反復）
"$PY" -I -X utf8 "$SC/selftest.py" "$SEED" "$OUT/selftest.json" --jobs "$JOBS" --run-id "$RUN_ID"
STAGE="mutations"
# 変異（名指しの門が赤になること）を本計算の前の門にする
OUT="$OUT" RUN_ID="$RUN_ID" PYTHON="$PY" JOBS="$JOBS" bash "$EXP_DIR/mutate.sh"
"$PY" -I -X utf8 "$SC/check_mutations.py" "$OUT/mutations" "$RUN_ID"
STAGE="sim"
# 本計算（反復ごとの値は results/raw/・git に入れない）
"$PY" -I -X utf8 "$SC/sim.py" "$SEED" "$OUT" "$JOBS" --reps "$REPS" --run-id "$RUN_ID"
STAGE="report"
# 集計・案の値・G7・G8（主の結果）
"$PY" -I -X utf8 "$SC/report.py" "$OUT" --run-id "$RUN_ID"
STAGE="done"
echo "done: $RUN_ID"
