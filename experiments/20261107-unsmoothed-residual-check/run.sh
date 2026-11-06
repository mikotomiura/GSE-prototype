#!/usr/bin/env bash
# 平滑の無い記号の対照（u・n）と擬似残差の検査（conditions.md）。HP Z2 で回す。データ・中間・書き手ごとの値は repo の外。
# ラベルは使わない。Step 0（capabilities_gate.py）は当たらない（GSE のログ用・前の実験と同じ逸脱）。
# tau-extend（experiments/20261104-timeseries-tau-extend/）のディレクトリ・条件・コードは変えない（数式のコードは読み込むだけ）。
# 実行の順は n → o → u。o の直後に P-REPRO（tau-extend の summary.json と照らす）を通し、外れれば u に進まない。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAU_EXP="$EXP_DIR/../20261104-timeseries-tau-extend"
TSC="$TAU_EXP/scripts"
: "${DATA_DIR:=$HOME/gse-public-data}"
COA_OLD="$DATA_DIR/landscape/coauthor_work"
COA="$DATA_DIR/landscape/coauthor_work_obs"
CS1_REF="$DATA_DIR/cs1/work2021_ref"
CS1="$DATA_DIR/cs1/work2021_obs"
SIDE_CO="$DATA_DIR/landscape/unsmoothed_residual_coauthor.json.gz"
SIDE_CS="$DATA_DIR/landscape/unsmoothed_residual_cs1.json.gz"
RAW_DIR="$DATA_DIR/landscape"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
SEED="$(cat "$EXP_DIR/SEED")"
JOBS="${JOBS:-6}"
PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="$(date +%Y%m%dT%H%M%S)-$$"
sha() { "$PY" -I -X utf8 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
mkdir -p "$OUT"
stamp() { echo "[$(date +%H:%M:%S)] $*"; }
# P-PIN: 読み込む tau-extend の 3 ファイルの SHA-256（各スクリプトも読み込み時に照らし、外れれば終了コード 4 で止まる）
"$PY" -I -X utf8 "$SC/pin_probe.py" > "$OUT/pin_check.json" || { echo "P-PIN: tau-extend のファイルの SHA-256 が条件の値と違う" >&2; exit 4; }
# 入力の照合（tau-extend と同じ manifest）と、新しい中間（u・n）の manifest
: "${INPUT_MANIFEST:?INPUT_MANIFEST が要る（tau-extend と同じ manifest・引き継ぎに書いた値）}"
[ "$(sha "$INPUT_MANIFEST")" = "${INPUT_MANIFEST_SHA256:?INPUT_MANIFEST_SHA256 が要る}" ] || { echo "manifest の SHA-256 が違う" >&2; exit 1; }
"$PY" -I -X utf8 "$TSC/manifest.py" check "$DATA_DIR" "$INPUT_MANIFEST" > "$OUT/input_manifest_check.json"
: "${VARIANT_MANIFEST:?VARIANT_MANIFEST が要る（Mac の build_mac.sh が作った manifest）}"
[ "$(sha "$VARIANT_MANIFEST")" = "${VARIANT_MANIFEST_SHA256:?VARIANT_MANIFEST_SHA256 が要る}" ] || { echo "新しい中間の manifest の SHA-256 が違う" >&2; exit 1; }
"$PY" -I -X utf8 - "$VARIANT_MANIFEST" "$SIDE_CO" "$SIDE_CS" > "$OUT/variant_manifest_check.json" <<'PY'
import hashlib, json, os, sys
m = json.load(open(sys.argv[1]))
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
bad = sum(1 for p in sys.argv[2:4] if not os.path.exists(p) or m["files"].get(os.path.basename(p)) != h(p))
gate = all(g["passed"] for g in m["u_gate"].values()) and set(m["u_gate"]) == {"coauthor", "cs1"}
print(json.dumps(dict(files=2, mismatched_or_missing=bad, u_gate_passed=gate)))
sys.exit(0 if bad == 0 and gate else 1)
PY
rm -rf "$OUT/parts" "$OUT/summary.json" "$OUT/tables.md" "$OUT/provenance.json" "$OUT/repro_check.json" \
  "$RAW_DIR"/unsmoothed_residual_params.*.npz "$RAW_DIR"/unsmoothed_residual_writer_values.*.json
stamp "門の単体と P-D1"
"$PY" -I -X utf8 "$TSC/build_cs1_obs.py" --selftest
"$PY" -I -X utf8 "$TSC/check_same_cs1.py" --selftest
"$PY" -I -X utf8 "$SC/repro_check.py" --selftest
"$PY" -I -X utf8 "$EXP_DIR/../20261103-coauthor-per-person/scripts/check_same.py" "$COA_OLD" "$COA" > "$OUT/check_same_coauthor.json"
"$PY" -I -X utf8 "$TSC/check_same_cs1.py" "$CS1_REF" "$CS1" "$EXP_DIR/../20261104-cs1-landscape/results/build_summary_2021.json" > "$OUT/check_same_cs1.json"
stamp "引き継ぐ陽性対照（tau-extend の ml.py --selftest をそのまま）"
"$PY" -I -X utf8 "$TSC/ml.py" --selftest "$SEED" "$OUT/selftest_inherited.json" --run-id "$RUN_ID" \
  --only P-XI,P-BATCH,P-EM3,P-AR1,P-PRIOR,P-CH,P-POOL,P-AR,P-LEAK,P-EM2,P-S,P-OTH,P-INF,P-JOINT,P-PR1
stamp "足す陽性対照と変異"
"$PY" -I -X utf8 "$SC/selftest.py" "$SEED" "$OUT/selftest.json" --run-id "$RUN_ID"
OUT="$OUT" RUN_ID="$RUN_ID" PYTHON="$PY" bash "$EXP_DIR/mutate.sh"
"$PY" -I -X utf8 "$SC/check_mutations.py" "$OUT/mutations" "$OUT/selftest.json" "$RUN_ID"
stamp "配管の合成の通し（fit → residual → report・合成のデータだけ）"
"$PY" -I -X utf8 "$SC/e2e_synth.py" "$SEED" "$OUT/e2e_synth.json" "$JOBS"
# 本計算（n → o → u）。書き手ごとの値・母数は repo の外（人が開いて読まない）
column() {
  local col="$1"
  for ds in coauthor cs1; do
    if [ "$ds" = coauthor ]; then work="$COA"; side="$SIDE_CO"; else work="$CS1"; side="$SIDE_CS"; fi
    stamp "当てはめ $col $ds"
    "$PY" -I -X utf8 "$SC/fit.py" "$ds" "$col" "$work" "$side" "$SEED" "$OUT" "$RAW_DIR" "$JOBS" --run-id "$RUN_ID"
    stamp "残差 $col $ds"
    "$PY" -I -X utf8 "$SC/residual.py" "$ds" "$col" "$work" "$side" "$SEED" "$OUT" "$RAW_DIR" --run-id "$RUN_ID"
  done
  "$PY" -I -X utf8 "$SC/report.py" "$OUT" --run-id "$RUN_ID"
}
column n
column o
# V1 P-REPRO: o の列を tau-extend の summary.json と相対 1e-9 で照らす。外れれば終了コード 3（u に進まない・notes に使わない）
stamp "P-REPRO"
"$PY" -I -X utf8 "$SC/repro_check.py" "$OUT/summary.json" "$TAU_EXP/results/summary.json" "$OUT/repro_check.json"
column u
stamp "provenance"
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" \
  "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261107-unsmoothed-residual-check/scripts experiments/20261107-unsmoothed-residual-check/run.sh experiments/20261107-unsmoothed-residual-check/mutate.sh experiments/20261107-unsmoothed-residual-check/conditions.md experiments/20261107-unsmoothed-residual-check/SEED experiments/20261104-timeseries-tau-extend/scripts experiments/20261104-timeseries-tau-extend/results/summary.json papers/per-person-learning/kit/symbols)" \
  "$EXP_DIR" "$COA" "$CS1" "$SIDE_CO" "$SIDE_CS" "$RAW_DIR" "$RUN_ID" "$OUT/provenance.json" "$INPUT_MANIFEST" "$VARIANT_MANIFEST" "$JOBS" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
sys.path.insert(0, sys.argv[3] + "/scripts")
import pinned
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
head, dirty, exp, coa, cs1, side_co, side_cs, raw, run_id, out, man, vman, jobs = sys.argv[1:14]
kit = os.path.realpath(exp + "/../../papers/per-person-learning/kit/symbols")
files = sorted(glob.glob(exp + "/scripts/*.py") + [exp + "/run.sh", exp + "/mutate.sh", exp + "/build_mac.sh", exp + "/conditions.md",
               exp + "/SEED", exp + "/../20261104-timeseries-tau-extend/results/summary.json"]
              + glob.glob(exp + "/../20261104-timeseries-tau-extend/scripts/*.py") + glob.glob(kit + "/*.py") + [kit + "/constants.json"])
def list_hash(d, pat):
    fs = sorted(glob.glob(os.path.join(d, pat)))
    return dict(files=len(fs), sha256_of_sha256_list=hashlib.sha256("".join(os.path.basename(f) + h(f) for f in fs).encode()).hexdigest())
raw_files = sorted(glob.glob(os.path.join(raw, "unsmoothed_residual_params.*.npz")) + glob.glob(os.path.join(raw, "unsmoothed_residual_writer_values.*.json")))
json.dump(dict(git_head=head, git_dirty_paths=[l for l in dirty.splitlines() if l], run_id=run_id,
               files_sha256={os.path.relpath(os.path.realpath(f), os.path.realpath(exp + "/../..")): h(f) for f in files},
               pinned_loaded_sha256=pinned.SHA, pin_ok=pinned.PIN_OK,
               coauthor_inputs=list_hash(coa, "s[0-9]*.json"), cs1_inputs=list_hash(cs1, "u[0-9]*.json"),
               variant_sidecar_sha256={os.path.basename(p): h(p) for p in (side_co, side_cs)},
               writer_level_files_sha256={os.path.basename(p): h(p) for p in raw_files},
               input_manifest_sha256=h(man), variant_manifest_sha256=h(vman),
               jobs=int(jobs), platform=platform.platform(), machine=platform.machine(),
               python=sys.version.split()[0], numpy=numpy.__version__), open(out, "w"), indent=1)
PY
stamp "済んだ"
