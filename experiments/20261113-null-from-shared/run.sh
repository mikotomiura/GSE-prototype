#!/usr/bin/env bash
# 計算 (f): 実データの共通そのものを真の生成にした帰無（conditions.md）。場所は HP Z2（git-bash）。
# selftest → 変異 → 入力の照合 → m0 の当てはめ（実データ・repo の外）→ 門 → 較正 → 本計算 55 本 → report → provenance。
# m0 の npz は repo の外（人は開かない）。repo に置くのは合成から測った集計と SHA-256 だけ。門で止まれば exit 5。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
COA="$DATA_DIR/landscape/coauthor_work_obs"
M0="${M0:-$DATA_DIR/landscape/null_from_shared_m0.npz}"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
SEED="$(cat "$EXP_DIR/SEED")"
JOBS="${JOBS:-16}"
PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)-$$}"
sha() { "$PY" -I -X utf8 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
[ "$SEED" = 2026111001 ] || { echo "SEED が条件の値と違う" >&2; exit 1; }
mkdir -p "$OUT"
# 失敗した再実行で前回の集計が残らないように頭で消す。m0_fit.json・gate.json・calibration.json・複製・plan.json は再開に使うので残す
rm -rf "$OUT/mutations" "$OUT/summary.json" "$OUT/tables.md" "$OUT/provenance.json" "$OUT/provenance.pre.json" \
  "$OUT/selftest.json" "$OUT/input_manifest_check.json"
mkdir -p "$OUT/mutations"
"$PY" -I -X utf8 "$SC/selftest_null.py" "$OUT/selftest.json" --run-id "$RUN_ID" --jobs 4
for m in n1 n2 n3 n4 n5 n6 n7; do
  set +e
  "$PY" -I -X utf8 "$SC/selftest_null.py" "$OUT/mutations/$m.json" --mutate "$m" --run-id "$RUN_ID" --jobs 4 > "$OUT/mutations/$m.log" 2>&1
  echo $? > "$OUT/mutations/$m.exit"
  set -e
done
"$PY" -I -X utf8 "$SC/check_mutations.py" "$OUT/mutations" "$RUN_ID"
if [ "${SELFTEST_ONLY:-0}" = 1 ]; then echo "selftest と変異だけ（SELFTEST_ONLY=1）: $RUN_ID"; exit 0; fi
# 入力の照合（B と同じ manifest）
MANIFEST="${INPUT_MANIFEST:?INPUT_MANIFEST が要る（B と同じ manifest）}"
[ "$(sha "$MANIFEST")" = "${INPUT_MANIFEST_SHA256:?INPUT_MANIFEST_SHA256 が要る}" ] || { echo "manifest の SHA-256 が違う" >&2; exit 1; }
[ "$INPUT_MANIFEST_SHA256" = e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406 ] || { echo "manifest が条件の値と違う" >&2; exit 1; }
"$PY" -I -X utf8 "$EXP_DIR/../20261104-timeseries-tau-extend/scripts/manifest.py" check "$DATA_DIR" "$MANIFEST" > "$OUT/input_manifest_check.json"
# m0（D1）: 既にあれば当て直さない（null.py が npz の SHA-256 を m0_fit.json と照らす）
if [ ! -f "$OUT/m0_fit.json" ] || [ ! -f "$M0" ]; then
  rm -f "$OUT/m0_fit.json" "$OUT/gate.json" "$OUT/calibration.json" "$OUT/plan.json"
  [ -z "$(ls -A "$OUT/replicates" 2>/dev/null)" ] || { echo "m0 を作り直すのに古い複製が残っている（消してからやり直す）" >&2; exit 1; }
  "$PY" -I -X utf8 "$SC/fit_m0.py" "$COA" "$M0" "$OUT/m0_fit.json" "$JOBS"
fi
prov() {
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" \
  "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261113-null-from-shared/scripts experiments/20261113-null-from-shared/run.sh experiments/20261113-null-from-shared/conditions.md experiments/20261113-null-from-shared/SEED experiments/20261112-sensitivity-ten-seeds/scripts experiments/20261111-sensitivity-mode-decomposition/scripts experiments/20261112-selection-split-and-smoothing/scripts experiments/20261110-per-person-sensitivity/scripts experiments/20261104-timeseries-tau-extend/scripts experiments/20261106-tau-mode-candidate/scripts experiments/20261106-tau-mode-candidate/results/summary.json)" \
  "$EXP_DIR" "$RUN_ID" "$JOBS" "$OUT/$1" "$M0" "$MANIFEST" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
head, dirty, exp, run_id, jobs, out, m0, manifest = sys.argv[1:9]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
sys.path.insert(0, os.path.join(exp, "scripts"))
import fit_m0, null, pinned6
d = os.path.dirname(out)
P = dict(run_id=run_id, git_head=head, git_dirty_paths=[l for l in dirty.splitlines() if l], jobs=int(jobs),
         python=platform.python_version(), numpy=numpy.__version__, machine=platform.platform(),
         scripts={os.path.basename(p): h(p) for p in sorted(glob.glob(os.path.join(exp, "scripts", "*.py")))},
         run_sh=h(os.path.join(exp, "run.sh")), conditions=h(os.path.join(exp, "conditions.md")),
         seed_file=h(os.path.join(exp, "SEED")), pinned=pinned6.hashes(),
         b_code={os.path.relpath(p, pinned6.EXP): v for p, v in fit_m0.PINNED.items()},
         code_hash=null.code_hash(), m0_npz_sha256=h(m0), input_manifest_sha256=h(manifest))
for f in ("m0_fit.json", "gate.json", "calibration.json", "plan.json", "summary.json"):
    if os.path.exists(os.path.join(d, f)):
        P[f.replace(".json", "") + "_sha256"] = h(os.path.join(d, f))
json.dump(P, open(out, "w"), indent=1)
PY
}
prov provenance.pre.json
set +e
"$PY" -I -X utf8 "$SC/null.py" run "$SEED" "$M0" "$OUT/m0_fit.json" "$OUT" "$JOBS" --run-id "$RUN_ID"
rc=$?
set -e
if [ "$rc" = 5 ]; then
  prov provenance.json
  echo "門で止まった（gate.json）。本計算に入っていない。研究者に聞く: $RUN_ID" >&2
  exit 5
fi
[ "$rc" = 0 ] || exit "$rc"
"$PY" -I -X utf8 "$SC/null.py" report "$OUT" --run-id "$RUN_ID"
prov provenance.json
echo "終わり: $RUN_ID"
