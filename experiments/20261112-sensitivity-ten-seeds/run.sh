#!/usr/bin/env bash
# 計算 D: 感度の合成の種を 10 に増やし、検出率と誤警報率を出す（conditions.md）。実データは使わない。場所は HP Z2（git-bash）。
# selftest → 変異 → 本計算（時間の規則つき・55 本）→ report（summary・tables・machine_check）→ provenance。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
SEED="$(cat "$EXP_DIR/SEED")"
JOBS="${JOBS:-16}"
PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)-$$}"
[ "$SEED" = 2026111001 ] || { echo "SEED が条件の値と違う" >&2; exit 1; }
mkdir -p "$OUT"
# 失敗した再実行で前回の集計が残らないように頭で消す（Codex の指摘 4）。複製と plan.json は再開に使うので残す
rm -rf "$OUT/mutations" "$OUT/summary.json" "$OUT/tables.md" "$OUT/machine_check.json" "$OUT/provenance.json" \
  "$OUT/provenance.pre.json" "$OUT/selftest.json"
mkdir -p "$OUT/mutations"
"$PY" -I -X utf8 "$SC/selftest10.py" "$OUT/selftest.json" --run-id "$RUN_ID"
for m in e1 e2 e3 e4 e5 e6 e7 e8; do
  set +e
  "$PY" -I -X utf8 "$SC/selftest10.py" "$OUT/mutations/$m.json" --mutate "$m" --run-id "$RUN_ID" > "$OUT/mutations/$m.log" 2>&1
  echo $? > "$OUT/mutations/$m.exit"
  set -e
done
"$PY" -I -X utf8 "$SC/check_mutations.py" "$OUT/mutations" "$RUN_ID"
if [ "${SELFTEST_ONLY:-0}" = 1 ]; then echo "selftest と変異だけ（SELFTEST_ONLY=1）: $RUN_ID"; exit 0; fi
prov() {
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" \
  "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261112-sensitivity-ten-seeds experiments/20261110-per-person-sensitivity/scripts experiments/20261110-per-person-sensitivity/results/calibration.json experiments/20261104-timeseries-tau-extend/scripts)" \
  "$EXP_DIR" "$RUN_ID" "$JOBS" "$OUT/$1" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
head, dirty, exp, run_id, jobs, out = sys.argv[1:7]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
sys.path.insert(0, os.path.join(exp, "scripts"))
import pinned5, ten
d = os.path.dirname(out)
P = dict(run_id=run_id, git_head=head, git_dirty_paths=[l for l in dirty.splitlines() if l], jobs=int(jobs),
         python=platform.python_version(), numpy=numpy.__version__, machine=platform.platform(),
         scripts={os.path.basename(p): h(p) for p in sorted(glob.glob(os.path.join(exp, "scripts", "*.py")))},
         run_sh=h(os.path.join(exp, "run.sh")), conditions=h(os.path.join(exp, "conditions.md")),
         seed_file=h(os.path.join(exp, "SEED")), pinned=pinned5.hashes(), code_hash=ten.code_hash())
if os.path.exists(os.path.join(d, "plan.json")):
    P["plan_sha256"] = h(os.path.join(d, "plan.json"))
if os.path.exists(os.path.join(d, "summary.json")):
    P["summary_sha256"] = h(os.path.join(d, "summary.json"))
json.dump(P, open(out, "w"), indent=1)
PY
}
prov provenance.pre.json
"$PY" -I -X utf8 "$SC/ten.py" run "$SEED" "$OUT" "$JOBS" --run-id "$RUN_ID"
"$PY" -I -X utf8 "$SC/ten.py" report "$OUT" --run-id "$RUN_ID"
prov provenance.json
echo "終わり: $RUN_ID"
