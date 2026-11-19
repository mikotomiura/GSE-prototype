#!/usr/bin/env bash
# 対称版の対照と選ばれた τ（conditions.md の追記「対称版の対照と選ばれた τ」・判断 34 の A と C）。場所は HP Z2（git-bash）。
# selftest → 変異 → ctrl（P-REPRO-SYMSUM・P-REPRO-MODE1・P-REPRO-B1・共通の 2 倍率と最頻値・集計）→ provenance_ctrl。
# 読む値（mode の pickle・B の値・対称版の値）と書く値は repo の外。人は開かない。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
COA="$DATA_DIR/landscape/coauthor_work_obs"
RAW="${RAW:-$DATA_DIR/landscape/tau_mode_candidate_writer_values}"
BVALS="${BVALS:-$DATA_DIR/landscape/selection_split_smoothing_values.pkl}"
SVALS="${SVALS:-$DATA_DIR/landscape/selection_split_smoothing_sym_values.pkl}"
CVALS="${CVALS:-$DATA_DIR/landscape/selection_split_smoothing_ctrl_values.pkl}"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
JOBS="${JOBS:-16}"
PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)-$$}"
[ "$(cat "$EXP_DIR/SEED")" = 2026110401 ] || { echo "SEED が条件の値と違う" >&2; exit 1; }
[ -f "$OUT/repro_check.json" ] && [ -f "$OUT/sym_summary.json" ] || { echo "A・B か対称版の結果が無い" >&2; exit 1; }
rm -rf "$OUT/mutations_ctrl" "$OUT/selftest_ctrl.json"
mkdir -p "$OUT/mutations_ctrl"
"$PY" -I -X utf8 "$SC/selftest_ctrl.py" "$OUT/selftest_ctrl.json" --run-id "$RUN_ID"
for m in z1 z2 z3 z4 z5; do
  set +e
  "$PY" -I -X utf8 "$SC/selftest_ctrl.py" "$OUT/mutations_ctrl/$m.json" --mutate "$m" --run-id "$RUN_ID" > "$OUT/mutations_ctrl/$m.log" 2>&1
  echo $? > "$OUT/mutations_ctrl/$m.exit"
  set -e
done
"$PY" -I -X utf8 - "$OUT/mutations_ctrl" "$RUN_ID" <<'PY'
import json, os, sys
d, run_id = sys.argv[1:3]
want = {"z1": "P-MODEA", "z2": "P-WEIGHT", "z3": "P-CTRLCELL", "z4": "P-CTRLCELL", "z5": "P-FORM"}
bad = []
for m, ctl in want.items():
    ex = open(os.path.join(d, m + ".exit")).read().strip()
    S = json.load(open(os.path.join(d, m + ".json"))) if os.path.exists(os.path.join(d, m + ".json")) else {}
    if ex != "3" or S.get("run_id") != run_id or S.get("mutate") != [m] or S.get(ctl, {}).get("passed", True):
        bad.append((m, ctl, ex))
if bad:
    sys.exit("変異の門が外れた: %r" % bad)
print("変異の門: すべて名指しの門が赤")
PY
if [ "${SELFTEST_ONLY:-0}" = 1 ]; then echo "selftest と変異だけ（SELFTEST_ONLY=1）: $RUN_ID"; exit 0; fi
[ ! -d "$CVALS" ] || { echo "CVALS がディレクトリを指している" >&2; exit 1; }
for p in "$RAW.coauthor.pkl" "$BVALS" "$SVALS"; do
  [ "$("$PY" -I -c 'import os,sys;print(os.path.normcase(os.path.realpath(sys.argv[1])))' "$p")" != \
    "$("$PY" -I -c 'import os,sys;print(os.path.normcase(os.path.realpath(sys.argv[1])))' "$CVALS")" ] || { echo "CVALS が入力と同じ" >&2; exit 1; }
done
rm -f -- "$OUT/ctrl_summary.json" "$OUT/ctrl_tables.md" "$OUT/ctrl_check.json" "$OUT/ctrl_timing.json" "$OUT/provenance_ctrl.json" "$CVALS"
"$PY" -I -X utf8 "$SC/ctrl.py" "$COA" "$RAW" "$BVALS" "$SVALS" "$CVALS" "$OUT" "$JOBS" --run-id "$RUN_ID"
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" \
  "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261112-selection-split-and-smoothing/scripts experiments/20261112-selection-split-and-smoothing/run_ctrl.sh experiments/20261112-selection-split-and-smoothing/conditions.md experiments/20261106-tau-mode-candidate/scripts)" \
  "$EXP_DIR" "$RUN_ID" "$OUT/provenance_ctrl.json" "$JOBS" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
head, dirty, exp, run_id, out, jobs = sys.argv[1:7]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
sys.path.insert(0, os.path.join(exp, "scripts"))
import pinned4
d = os.path.dirname(out)
with open(out, "w", newline="\n") as f:
    json.dump(dict(run_id=run_id, git_head=head, git_dirty_paths=[l for l in dirty.splitlines() if l],
                   python=platform.python_version(), numpy=numpy.__version__, machine=platform.platform(), jobs=int(jobs),
                   scripts={os.path.basename(p): h(p) for p in sorted(glob.glob(os.path.join(exp, "scripts", "*.py")))},
                   run_ctrl_sh=h(os.path.join(exp, "run_ctrl.sh")), conditions=h(os.path.join(exp, "conditions.md")),
                   pinned=pinned4.hashes(), ctrl_check=json.load(open(os.path.join(d, "ctrl_check.json"))),
                   ctrl_timing=json.load(open(os.path.join(d, "ctrl_timing.json"))),
                   ctrl_summary_sha256=h(os.path.join(d, "ctrl_summary.json"))), f, indent=1)
PY
echo "終わり: $RUN_ID"
