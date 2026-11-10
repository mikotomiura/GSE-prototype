#!/usr/bin/env bash
# CoAuthor と CS1 2021 で τ の格子を広げ、共通の構造を先に選ぶ 2 段の行を組む（conditions.md・EM だけ）。データと中間は repo の外。
# ラベルは使わない。Step 0（capabilities_gate.py）は当たらない（GSE のログ用・前の実験と同じ逸脱）。
# 前回（experiments/20261104-coauthor-ml-improve/）のディレクトリは変えない。P-REPRO で前回の summary.json と照らす。
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
SEED="$(cat "$EXP_DIR/SEED")"
JOBS="${JOBS:-6}"
PY="${PYTHON:-python3}"
# 1 プロセス 1 スレッド（書き手ごとに並べるので BLAS の多重を抑える）
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="$(date +%Y%m%dT%H%M%S)-$$"
sha() { "$PY" -I -X utf8 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
mkdir -p "$OUT"
# 入力の照合。生データが手元にあれば SHA-256 で照らす（Mac）。無ければ Mac で作った中間の manifest で照らす（別の PC・判断 13）
MANIFEST="${INPUT_MANIFEST:-}"
if [ -z "$MANIFEST" ]; then
  [ "$(sha "$CZIP")" = 8d7380ca3811c671e774e43bfb9f5d3265e2a5d425788a066a612831aa1e418b ] || { echo "coauthor.zip の SHA-256 が違う" >&2; exit 1; }
  [ "$(sha "$K21")" = 950a587bb3a410efc4aad0e64974d6442806345fddd13af76676dfb8006a22b6 ] || { echo "CS1 2021 の SHA-256 が違う" >&2; exit 1; }
  [ "$(sha "$BIN")" = 26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3 ] || { echo "gse-replay の SHA-256 が違う" >&2; exit 1; }
  [ "$(sha "$HOLD")" = a5a32fcefeb97b038afd170e2672262fd5a71230d5e851319eaa076b606bdc47 ] || { echo "CS1 の holdout の SHA-256 が違う" >&2; exit 1; }
else
  [ "$(sha "$MANIFEST")" = "${INPUT_MANIFEST_SHA256:?INPUT_MANIFEST_SHA256 が要る（引き継ぎに書いた値）}" ] || { echo "manifest の SHA-256 が違う" >&2; exit 1; }
  "$PY" -I -X utf8 "$SC/manifest.py" check "$DATA_DIR" "$MANIFEST" > "$OUT/input_manifest_check.json"
fi
RAW="$DATA_DIR/landscape/timeseries_tau_extend_writer_values"
PREV="$EXP_DIR/../20261104-coauthor-ml-improve"
rm -f "$OUT/summary.json" "$OUT/provenance.json" "$OUT/repro_check.json" "$RAW".*.json
# 変換と門の単体（陰性対照を含む・1 秒以内）
"$PY" -I -X utf8 "$SC/build_cs1_obs.py" --selftest
"$PY" -I -X utf8 "$SC/check_same_cs1.py" --selftest
"$PY" -I -X utf8 "$SC/repro_check.py" --selftest
# V1 P-D1: 中間の門（CoAuthor は B と同じ・CS1 は判断 6）
"$PY" -I -X utf8 "$EXP_DIR/../20261103-coauthor-per-person/scripts/check_same.py" "$COA_OLD" "$COA" > "$OUT/check_same_coauthor.json"
"$PY" -I -X utf8 "$SC/check_same_cs1.py" "$CS1_REF" "$CS1" "$EXP_DIR/../20261104-cs1-landscape/results/build_summary_2021.json" > "$OUT/check_same_cs1.json"
# 陽性対照（合成のデータだけ）
"$PY" -I -X utf8 "$SC/ml.py" --selftest "$SEED" "$OUT/selftest.json" --run-id "$RUN_ID"
# 変異（名指しの対照が赤になること）を本計算の前の門にする
OUT="$OUT" RUN_ID="$RUN_ID" PYTHON="$PY" bash "$EXP_DIR/mutate.sh"
"$PY" -I -X utf8 "$SC/check_mutations.py" "$OUT/mutations" "$OUT/selftest.json" "$RUN_ID"
# 本計算（書き手ごとの値は repo の外に残す・人が開いて読まない）
GSE_ML_RAW="$RAW" "$PY" -I -X utf8 "$SC/ml.py" "$COA" "$CS1" "$SEED" "$OUT" "$JOBS" --run-id "$RUN_ID"
# provenance（git の HEAD・実験のディレクトリ全体の未コミットの変更・スクリプトの SHA-256・入力の SHA-256 の一覧のハッシュ・版）
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261104-timeseries-tau-extend/scripts experiments/20261104-timeseries-tau-extend/run.sh experiments/20261104-timeseries-tau-extend/mutate.sh experiments/20261104-timeseries-tau-extend/conditions.md experiments/20261104-timeseries-tau-extend/SEED experiments/20261104-coauthor-ml-improve/scripts experiments/20261104-coauthor-ml-improve/results/summary.json)" \
  "$EXP_DIR" "$COA" "$CS1" "$HOLD" "$BIN" "$RUN_ID" "$OUT/provenance.json" "$MANIFEST" "$JOBS" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
hx = lambda p: h(p) if os.path.exists(p) else None  # 別の PC では生データ・replay・holdout が無い（manifest で照らした）
head, dirty, exp, coa, cs1, hold, binp, run_id, out, manifest, jobs = sys.argv[1:12]
files = sorted(glob.glob(exp + "/scripts/*.py") + [exp + "/run.sh", exp + "/mutate.sh", exp + "/conditions.md", exp + "/SEED",
               exp + "/../20261103-coauthor-per-person/scripts/check_same.py",
               exp + "/../20261104-cs1-landscape/scripts/build_cs1.py"]
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
# V1 P-REPRO: 前回と重なるセルを相対 1e-9 で照らす（HP Z2・同じ版で回す門）。外れれば終了コード 3（notes に使わず止めて調べる）
"$PY" -I -X utf8 "$SC/repro_check.py" "$OUT/summary.json" "$PREV/results/summary.json" "$OUT/repro_check.json"
