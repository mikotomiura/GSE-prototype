#!/usr/bin/env bash
# 窓の歩みの用量反応の本計算（conditions D6・V1）。Mac で回す。データ・中間・書き手ごとの値・母数は repo の外。
# 先に run_synth.sh（合成の門）が全部通っていること。実行の順: P-PIN → 入力の照合 → P-ROWS → 列 A30 → 列 A1 →
# 端の再現の門（P-REPRO-N・P-REPRO-U）→ 列 A5・A10・A15 → 列 C → 列 C′ → 列 B（DROP_B=1 なら外す）→ analyze → provenance。
# 端の再現の門が外れたら終了コード 3 で止める（D6: 許容を変えずに HP Z2 で全部を回し直す。Mac の結果は notes に使わない）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S13_EXP="$EXP_DIR/../20261107-unsmoothed-residual-check"
TSC="$EXP_DIR/../20261104-timeseries-tau-extend/scripts"
SC="$EXP_DIR/scripts"
: "${DATA_DIR:=$HOME/gse-public-data}"
COA="$DATA_DIR/landscape/coauthor_work_obs"
SIDE_CO="$DATA_DIR/landscape/unsmoothed_residual_coauthor.json.gz"
RAW_DIR="$DATA_DIR/landscape/window_overlap_raw"
OUT="${OUT:-$EXP_DIR/results}"
SEED="$(cat "$EXP_DIR/SEED")"
JOBS="${JOBS:-6}"
PY="${PYTHON:?PYTHON が要る（repo の外の仮想環境・Python 3.11・numpy 2.4.4）}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="$(date +%Y%m%dT%H%M%S)-$$"
sha() { "$PY" -I -X utf8 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
stamp() { echo "[$(date +%H:%M:%S)] $*"; }
mkdir -p "$OUT" "$RAW_DIR"
# 合成の門が通っていること（selftest・変異・配管の通し）
"$PY" -I -X utf8 - "$OUT" <<'PY' || { echo "合成の門（run_synth.sh）が通っていない" >&2; exit 5; }
import json, os, sys
o = sys.argv[1]
st = json.load(open(os.path.join(o, "selftest.json"), encoding="utf-8"))
e2e = json.load(open(os.path.join(o, "e2e_synth.json"), encoding="utf-8"))
s13 = json.load(open(os.path.join(o, "selftest_s13.json"), encoding="utf-8"))
ok = st["all_passed"] and all(m["hit"] for m in st["mutations"].values()) and len(st["mutations"]) == 21 and e2e["passed"] and s13["all_passed"]
sys.exit(0 if ok else 5)
PY
stamp "P-PIN"
"$PY" -I -X utf8 - "$SC" > "$OUT/pin_check.json" <<'PY' || { echo "P-PIN が外れた" >&2; exit 4; }
import json, sys
sys.path.insert(0, sys.argv[1])
import swap
print(json.dumps(dict(swap.PIN), indent=1))
sys.exit(0 if swap.PIN["pin_ok"] else 4)
PY
stamp "入力の照合（S13 と同じ manifest）"
: "${INPUT_MANIFEST:?INPUT_MANIFEST が要る}"
[ "$(sha "$INPUT_MANIFEST")" = "${INPUT_MANIFEST_SHA256:?INPUT_MANIFEST_SHA256 が要る}" ] || { echo "manifest の SHA-256 が違う" >&2; exit 1; }
"$PY" -I -X utf8 "$TSC/manifest.py" check "$DATA_DIR" "$INPUT_MANIFEST" > "$OUT/input_manifest_check.json"
: "${VARIANT_MANIFEST:?VARIANT_MANIFEST が要る}"
[ "$(sha "$VARIANT_MANIFEST")" = "${VARIANT_MANIFEST_SHA256:?VARIANT_MANIFEST_SHA256 が要る}" ] || { echo "新しい中間の manifest の SHA-256 が違う" >&2; exit 1; }
"$PY" -I -X utf8 - "$VARIANT_MANIFEST" "$SIDE_CO" > "$OUT/variant_manifest_check.json" <<'PY'
import hashlib, json, os, sys
m = json.load(open(sys.argv[1]))
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
p = sys.argv[2]
bad = int(not os.path.exists(p) or m["files"].get(os.path.basename(p)) != h(p))
gate = bool(m["u_gate"]["coauthor"]["passed"])
print(json.dumps(dict(files=1, mismatched_or_missing=bad, u_gate_passed=gate)))
sys.exit(0 if bad == 0 and gate else 1)
PY
rm -rf "$OUT/parts" "$OUT/summary.json" "$OUT/tables.md" "$OUT/readings.json" "$OUT/figure_medians.csv" "$OUT/provenance.json" \
  "$OUT/repro_check.json" "$OUT/rows_check.json"
rm -f "$RAW_DIR"/unsmoothed_residual_params.coauthor.*.npz "$RAW_DIR"/unsmoothed_residual_writer_values.coauthor.*.json \
  "$RAW_DIR"/extra_writer_values.coauthor.*.json
stamp "P-ROWS（入力の時刻の照合を含む）"
"$PY" -I -X utf8 "$SC/rows_check.py" "$COA" "$SIDE_CO" "$SEED" "$OUT/rows_check.json"
column() {
  local col="$1" t0
  t0=$(date +%s)
  stamp "当てはめ $col"
  "$PY" -I -X utf8 "$SC/drive.py" fit "$col" "$COA" "$SIDE_CO" "$SEED" "$OUT" "$RAW_DIR" "$JOBS" --run-id "$RUN_ID"
  stamp "残差 $col"
  "$PY" -I -X utf8 "$SC/drive.py" residual "$col" "$COA" "$SIDE_CO" "$SEED" "$OUT" "$RAW_DIR" --run-id "$RUN_ID"
  stamp "足す量 $col"
  "$PY" -I -X utf8 "$SC/drive.py" extra "$col" "$COA" "$SIDE_CO" "$SEED" "$OUT" "$RAW_DIR" --run-id "$RUN_ID"
  echo "$col $(( $(date +%s) - t0 ))" >> "$OUT/parts/column_seconds.txt"
}
mkdir -p "$OUT/parts"
column A30
column A1
stamp "端の再現の門（P-REPRO-N・P-REPRO-U）"
"$PY" -I -X utf8 "$SC/analyze.py" "$OUT" "$RAW_DIR" "$SEED" --run-id "$RUN_ID" --cols A1,A30 > /dev/null
"$PY" -I -X utf8 - "$SC" "$OUT" "$S13_EXP/results/summary.json" <<'PY' || { echo "端の再現の門が外れた（D6: HP Z2 で回し直す）" >&2; exit 3; }
import json, os, subprocess, sys
sc, out, s13 = sys.argv[1:4]
R = {}
for col in ("A30", "A1"):
    p = os.path.join(out, "repro_%s.json" % col)
    subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(sc, "repro_dose.py"), os.path.join(out, "summary.json"), s13, p, col])
    R[col] = json.load(open(p))
    os.remove(p)
R["passed"] = all(R[c]["passed"] for c in ("A30", "A1"))
json.dump(R, open(os.path.join(out, "repro_check.json"), "w"), indent=1)
print(json.dumps({c: dict(leaves=R[c]["leaves"], mismatched=R[c]["mismatched"], max_rel_diff=R[c]["max_rel_diff"]) for c in ("A30", "A1")}))
sys.exit(0 if R["passed"] else 3)
PY
for col in A5 A10 A15 C5 C10 C15 C30 P1-5 P1-10 P1-15 P1-30 P3-5 P3-10 P3-15 P3-30; do column "$col"; done
if [ "${DROP_B:-0}" != 1 ]; then for col in B5 B10 B15 B30; do column "$col"; done; fi
stamp "集計と読み（analyze）"
"$PY" -I -X utf8 "$SC/analyze.py" "$OUT" "$RAW_DIR" "$SEED" --run-id "$RUN_ID"
stamp "provenance"
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" \
  "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261127-window-overlap-dose experiments/20261107-unsmoothed-residual-check/scripts experiments/20261107-unsmoothed-residual-check/results/summary.json experiments/20261104-timeseries-tau-extend/scripts papers/per-person-learning/kit/symbols)" \
  "$EXP_DIR" "$COA" "$SIDE_CO" "$RAW_DIR" "$RUN_ID" "$OUT/provenance.json" "$INPUT_MANIFEST" "$VARIANT_MANIFEST" "$JOBS" "${DROP_B:-0}" <<'PY'
import glob, hashlib, json, os, platform, subprocess, sys
import numpy
sys.path.insert(0, sys.argv[3] + "/scripts")
import swap
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
head, dirty, exp, coa, side, raw, run_id, out, man, vman, jobs, drop_b = sys.argv[1:13]
root = os.path.realpath(exp + "/../..")
files = sorted(glob.glob(exp + "/scripts/*.py") + [exp + "/run.sh", exp + "/run_synth.sh", exp + "/mutate.sh", exp + "/conditions.md", exp + "/SEED",
               exp + "/../20261107-unsmoothed-residual-check/results/summary.json"])
fs = sorted(glob.glob(os.path.join(coa, "s[0-9]*.json")))
raw_files = sorted(glob.glob(os.path.join(raw, "*.coauthor.*")))
blas = numpy.show_config(mode="dicts")["Build Dependencies"]["blas"]["name"]
json.dump(dict(git_head=head, git_dirty_paths=[l for l in dirty.splitlines() if l], run_id=run_id,
               files_sha256={os.path.relpath(os.path.realpath(f), root): h(f) for f in files},
               pin=swap.PIN, coauthor_inputs=dict(files=len(fs), sha256_of_sha256_list=hashlib.sha256(
                   "".join(os.path.basename(f) + h(f) for f in fs).encode()).hexdigest()),
               sidecar_sha256=h(side), writer_level_files=len(raw_files),
               input_manifest_sha256=h(man), variant_manifest_sha256=h(vman), jobs=int(jobs), drop_b=drop_b == "1",
               platform=platform.platform(), machine=platform.machine(), cpu=subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
               capture_output=True, text=True).stdout.strip(), python=sys.version.split()[0], numpy=numpy.__version__, blas=blas,
               venv=os.path.realpath(sys.prefix).replace(os.path.expanduser("~"), "~")), open(out, "w"), indent=1)
PY
stamp "済んだ"
