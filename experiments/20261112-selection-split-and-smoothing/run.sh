#!/usr/bin/env bash
# 計算 A（書き手の二分）と B（共通の基の平滑・本人の連鎖の平滑を他人で選ぶ）（conditions.md）。場所は HP Z2（git-bash）。
# selftest → 変異 → 入力の照合 → compute（P-REPRO・B2・B1 の P-REPRO-POOL と当て直し）→ ab（A・B の集計と表）→ provenance。
# 書き手ごとの値（mode の pickle・B の値）は repo の外。人は開かない。repo に置くのは集計値だけ。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
COA="$DATA_DIR/landscape/coauthor_work_obs"
CS1="$DATA_DIR/cs1/work2021_obs"
RAW="${RAW:-$DATA_DIR/landscape/tau_mode_candidate_writer_values}"
BVALS="${BVALS:-$DATA_DIR/landscape/selection_split_smoothing_values.pkl}"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
JOBS="${JOBS:-16}"
PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)-$$}"
sha() { "$PY" -I -X utf8 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
[ "$(cat "$EXP_DIR/SEED")" = 2026110401 ] || { echo "SEED が条件の値と違う" >&2; exit 1; }
mkdir -p "$OUT"
rm -rf "$OUT/mutations"; mkdir -p "$OUT/mutations"
"$PY" -I -X utf8 "$SC/selftest.py" "$OUT/selftest.json" --run-id "$RUN_ID"
for m in s1 s2 s3 s4 s5 s6 s7; do
  set +e
  "$PY" -I -X utf8 "$SC/selftest.py" "$OUT/mutations/$m.json" --mutate "$m" --run-id "$RUN_ID" > "$OUT/mutations/$m.log" 2>&1
  echo $? > "$OUT/mutations/$m.exit"
  set -e
done
"$PY" -I -X utf8 "$SC/check_mutations.py" "$OUT/mutations" "$RUN_ID"
if [ "${SELFTEST_ONLY:-0}" = 1 ]; then echo "selftest と変異だけ（SELFTEST_ONLY=1）: $RUN_ID"; exit 0; fi
# 入力の照合（mode と同じ manifest・判断 13 の形）
MANIFEST="${INPUT_MANIFEST:?INPUT_MANIFEST が要る（mode と同じ manifest）}"
[ "$(sha "$MANIFEST")" = "${INPUT_MANIFEST_SHA256:?INPUT_MANIFEST_SHA256 が要る}" ] || { echo "manifest の SHA-256 が違う" >&2; exit 1; }
[ "$INPUT_MANIFEST_SHA256" = e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406 ] || { echo "manifest が条件の値と違う" >&2; exit 1; }
"$PY" -I -X utf8 "$EXP_DIR/../20261104-timeseries-tau-extend/scripts/manifest.py" check "$DATA_DIR" "$MANIFEST" > "$OUT/input_manifest_check.json"
rm -f "$OUT/summary.json" "$OUT/tables.md" "$OUT/repro_check.json" "$OUT/timing.json" "$OUT/provenance.json" "$BVALS"
"$PY" -I -X utf8 "$SC/compute.py" "$COA" "$CS1" "$RAW" "$BVALS" "$OUT" "$JOBS" --run-id "$RUN_ID"
"$PY" -I -X utf8 "$SC/ab.py" "$RAW" "$BVALS" "$OUT" --run-id "$RUN_ID"
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" \
  "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261112-selection-split-and-smoothing experiments/20261106-tau-mode-candidate/scripts experiments/20261106-tau-mode-candidate/results/summary.json)" \
  "$EXP_DIR" "$RUN_ID" "$OUT/provenance.json" "$MANIFEST" "$JOBS" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
head, dirty, exp, run_id, out, manifest, jobs = sys.argv[1:8]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
sys.path.insert(0, os.path.join(exp, "scripts"))
import pinned4
d = os.path.dirname(out)
json.dump(dict(run_id=run_id, git_head=head, git_dirty_paths=[l for l in dirty.splitlines() if l],
               python=platform.python_version(), numpy=numpy.__version__, machine=platform.platform(), jobs=int(jobs),
               scripts={os.path.basename(p): h(p) for p in sorted(glob.glob(os.path.join(exp, "scripts", "*.py")))},
               run_sh=h(os.path.join(exp, "run.sh")), conditions=h(os.path.join(exp, "conditions.md")),
               seed_file=h(os.path.join(exp, "SEED")), pinned=pinned4.hashes(), input_manifest_sha256=h(manifest),
               repro_check=json.load(open(os.path.join(d, "repro_check.json"))),
               timing=json.load(open(os.path.join(d, "timing.json"))),
               summary_sha256=h(os.path.join(d, "summary.json"))), open(out, "w"), indent=1)
PY
echo "終わり: $RUN_ID"
