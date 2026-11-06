#!/usr/bin/env bash
# 構造の足りなさの仮説を確かめる試験（conditions.md・EM だけ）。データと中間は repo の外。ラベルは使わない。
# Step 0（capabilities_gate.py）は当たらない（GSE のログ用・前の実験と同じ逸脱）。
# 前の試験のディレクトリ（tau-extend・ml-improve・tau-mode-candidate）は変えない。P-SAME は前の 2 つのコードを別のプロセスで呼び、
# P-REPRO は前の 2 つの results/summary.json と照らす。P-D1 は tau-mode-candidate の門のスクリプトを使う。
# 組 (5, o) を先に回して P-REPRO を照らし、外れたら残りの 5 組に進まずに止める（conditions D6・V1）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
COA_OLD="$DATA_DIR/landscape/coauthor_work"
COA="$DATA_DIR/landscape/coauthor_work_obs"
CS1_REF="$DATA_DIR/cs1/work2021_ref"
CS1="$DATA_DIR/cs1/work2021_obs"
CZIP="$DATA_DIR/coauthor/raw/coauthor.zip"
K21="$DATA_DIR/cs1/raw/2021/keystrokes.csv"
HOLD="$DATA_DIR/cs1/holdout.json"
BIN="$DATA_DIR/klicke/bin/gse-replay"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
GATE_SC="$EXP_DIR/../20261106-tau-mode-candidate/scripts"
TAU="$EXP_DIR/../20261104-timeseries-tau-extend"
MLI="$EXP_DIR/../20261104-coauthor-ml-improve"
SEED="$(cat "$EXP_DIR/SEED")"
JOBS="${JOBS:-6}"
PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="$(date +%Y%m%dT%H%M%S)-$$"
sha() { "$PY" -I -X utf8 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
mkdir -p "$OUT"
MANIFEST="${INPUT_MANIFEST:-}"
if [ -z "$MANIFEST" ]; then
  [ "$(sha "$CZIP")" = 8d7380ca3811c671e774e43bfb9f5d3265e2a5d425788a066a612831aa1e418b ] || { echo "coauthor.zip の SHA-256 が違う" >&2; exit 1; }
  [ "$(sha "$K21")" = 950a587bb3a410efc4aad0e64974d6442806345fddd13af76676dfb8006a22b6 ] || { echo "CS1 2021 の SHA-256 が違う" >&2; exit 1; }
  [ "$(sha "$BIN")" = 26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3 ] || { echo "gse-replay の SHA-256 が違う" >&2; exit 1; }
  [ "$(sha "$HOLD")" = a5a32fcefeb97b038afd170e2672262fd5a71230d5e851319eaa076b606bdc47 ] || { echo "CS1 の holdout の SHA-256 が違う" >&2; exit 1; }
else
  [ "$(sha "$MANIFEST")" = "${INPUT_MANIFEST_SHA256:?INPUT_MANIFEST_SHA256 が要る（引き継ぎに書いた値）}" ] || { echo "manifest の SHA-256 が違う" >&2; exit 1; }
  "$PY" -I -X utf8 "$GATE_SC/manifest.py" check "$DATA_DIR" "$MANIFEST" > "$OUT/input_manifest_check.json"
fi
RAW="$DATA_DIR/landscape/structure_deficit_writer_values"
rm -f "$OUT/summary.json" "$OUT/provenance.json" "$OUT/repro_check.json" "$OUT/q_gate.json" "$RAW".*.pkl
# 門の単体（陰性対照を含む）
"$PY" -I -X utf8 "$GATE_SC/check_same_cs1.py" --selftest
"$PY" -I -X utf8 "$SC/repro_check.py" --selftest
# V1 P-D1: 中間の門（前の試験と同じ）
"$PY" -I -X utf8 "$EXP_DIR/../20261103-coauthor-per-person/scripts/check_same.py" "$COA_OLD" "$COA" > "$OUT/check_same_coauthor.json"
"$PY" -I -X utf8 "$GATE_SC/check_same_cs1.py" "$CS1_REF" "$CS1" "$EXP_DIR/../20261104-cs1-landscape/results/build_summary_2021.json" > "$OUT/check_same_cs1.json"
# 陽性対照（合成のデータだけ）
"$PY" -I -X utf8 "$SC/ml.py" --selftest "$SEED" "$OUT/selftest.json" --run-id "$RUN_ID"
# 変異（名指しの対照が赤になること）を本計算の前の門にする
OUT="$OUT" RUN_ID="$RUN_ID" PYTHON="$PY" bash "$EXP_DIR/mutate.sh"
"$PY" -I -X utf8 "$SC/check_mutations.py" "$OUT/mutations" "$OUT/selftest.json" "$RUN_ID"
# 本計算 1: P-Q（q_gate.json・外れれば ml.py が止まる）→ 組 (5, o) → P-REPRO（外れれば終了コード 3 で止まる）
GSE_ML_RAW="$RAW" "$PY" -I -X utf8 "$SC/ml.py" "$COA" "$CS1" "$SEED" "$OUT" "$JOBS" --run-id "$RUN_ID" --groups q5_o
"$PY" -I -X utf8 "$SC/repro_check.py" "$OUT/summary.json" "$TAU/results/summary.json" "$MLI/results/summary.json" "$OUT/repro_check.json"
# 本計算 2: 残りの 5 組（summary.json に足していく）
GSE_ML_RAW="$RAW" "$PY" -I -X utf8 "$SC/ml.py" "$COA" "$CS1" "$SEED" "$OUT" "$JOBS" --run-id "$RUN_ID" --groups q5_p,q3_o,q3_p,q7_o,q7_p
# provenance（git の HEAD・実験のディレクトリの未コミットの変更・スクリプトの SHA-256・入力の SHA-256 の一覧のハッシュ・版）
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261107-structure-deficit-test/scripts experiments/20261107-structure-deficit-test/run.sh experiments/20261107-structure-deficit-test/mutate.sh experiments/20261107-structure-deficit-test/conditions.md experiments/20261107-structure-deficit-test/SEED experiments/20261104-timeseries-tau-extend/scripts experiments/20261104-timeseries-tau-extend/results/summary.json experiments/20261104-coauthor-ml-improve/scripts experiments/20261104-coauthor-ml-improve/results/summary.json experiments/20261106-tau-mode-candidate/scripts)" \
  "$EXP_DIR" "$COA" "$CS1" "$HOLD" "$BIN" "$RUN_ID" "$OUT/provenance.json" "$MANIFEST" "$JOBS" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
hx = lambda p: h(p) if os.path.exists(p) else None
head, dirty, exp, coa, cs1, hold, binp, run_id, out, manifest, jobs = sys.argv[1:12]
files = sorted(glob.glob(exp + "/scripts/*.py") + [exp + "/run.sh", exp + "/mutate.sh", exp + "/conditions.md", exp + "/SEED",
               exp + "/../20261103-coauthor-per-person/scripts/check_same.py"]
              + glob.glob(exp + "/../20261106-tau-mode-candidate/scripts/*.py")
              + glob.glob(exp + "/../20261104-timeseries-tau-extend/scripts/*.py")
              + [exp + "/../20261104-timeseries-tau-extend/results/summary.json"]
              + glob.glob(exp + "/../20261104-coauthor-ml-improve/scripts/*.py")
              + [exp + "/../20261104-coauthor-ml-improve/results/summary.json"])
def list_hash(d, pat):
    fs = sorted(glob.glob(os.path.join(d, pat)))
    return dict(files=len(fs), sha256_of_sha256_list=hashlib.sha256("".join(os.path.basename(f) + h(f) for f in fs).encode()).hexdigest())
json.dump(dict(git_head=head, git_dirty_paths=[l for l in dirty.splitlines() if l], run_id=run_id,
               files_sha256={os.path.relpath(os.path.realpath(f), os.path.realpath(exp + "/..")): h(f) for f in files},
               coauthor_inputs=list_hash(coa, "s[0-9]*.json"), cs1_inputs=list_hash(cs1, "u[0-9]*.json"),
               cs1_holdout_sha256=hx(hold), gse_replay_sha256=hx(binp),
               input_manifest_sha256=h(manifest) if manifest else None,
               raw_checked_on_mac=(json.load(open(manifest)).get("raw_checked_on_mac") if manifest else None),
               jobs=int(jobs), platform=platform.platform(), machine=platform.machine(),
               python=sys.version.split()[0], numpy=numpy.__version__), open(out, "w"), indent=1)
PY
