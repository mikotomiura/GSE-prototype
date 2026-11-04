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
# 来歴は計算の前に取り、SHA_START を取った後に落ちても書く（trap）。前の実験の sim.py・report.py・selftest.py・summary.json も刻む
HEAD="$(git -C "$REPO_ROOT" rev-parse HEAD)"
DIRTY="$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261104-stage1-penalty-weak-signal/scripts experiments/20261104-stage1-penalty-weak-signal/run.sh experiments/20261104-stage1-penalty-weak-signal/mutate.sh experiments/20261104-stage1-penalty-weak-signal/conditions.md experiments/20261104-stage1-penalty-weak-signal/SEED experiments/20261104-stage1-penalty-synthetic/scripts experiments/20261104-stage1-penalty-synthetic/results/summary.json)"
STAGE="start"
# 入力のファイルの SHA-256 は計算の前に取り（sha256）、終わりに取り直して違うものを changed_during_run に書く
hash_inputs() {
  "$PY" -I -X utf8 - "$EXP_DIR" "$PREV" <<'PY'
import glob, hashlib, json, os, sys
exp, prev = sys.argv[1:3]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
files = sorted(glob.glob(os.path.join(exp, "scripts", "*.py"))) + [os.path.join(exp, f) for f in ("run.sh", "mutate.sh", "conditions.md", "SEED")]
pfiles = [os.path.join(prev, "scripts", f) for f in ("sim.py", "report.py", "selftest.py")] + [os.path.join(prev, "results", "summary.json")]
print(json.dumps({os.path.relpath(f, exp): h(f) for f in files + pfiles}))
PY
}
SHA_START="$(hash_inputs)"
write_prov() {
  local rc=$?
  local sha_end
  sha_end="$(hash_inputs || echo '{"__hash_failed__": "1"}')"
  "$PY" -I -X utf8 - "$HEAD" "$DIRTY" "$RUN_ID" "$REPS" "$JOBS" "$OUT/provenance.json" "$STAGE" "$rc" "$SHA_START" "$sha_end" <<'PY' || true
import json, platform, sys
import numpy
head, dirty, run_id, reps, jobs, out, stage, rc, s0, s1 = sys.argv[1:11]
s0, s1 = json.loads(s0), json.loads(s1)
failed = "__hash_failed__" in s1
changed = [] if failed else sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
json.dump(dict(run_id=run_id, git_head=head, dirty=dirty.splitlines(), reps=int(reps), jobs=int(jobs),
               last_stage=stage, exit_code=int(rc),
               python=platform.python_version(), numpy=numpy.__version__, machine=platform.platform(),
               sha256=s0, changed_during_run=changed, end_hash_failed=failed),
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
