#!/usr/bin/env bash
# B1 の対称版（conditions.md の追記・判断 19）。場所は HP Z2（git-bash・計算 D の後）。
# selftest → 変異 → sym（P-REPRO-SELF・P-REPRO-B1・倍率 0.03 の本人の当て直し・集計）→ provenance_sym。
# 読む値（mode の pickle・B の値）と書く値は repo の外。人は開かない。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
COA="$DATA_DIR/landscape/coauthor_work_obs"
RAW="${RAW:-$DATA_DIR/landscape/tau_mode_candidate_writer_values}"
BVALS="${BVALS:-$DATA_DIR/landscape/selection_split_smoothing_values.pkl}"
SVALS="${SVALS:-$DATA_DIR/landscape/selection_split_smoothing_sym_values.pkl}"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
JOBS="${JOBS:-16}"
PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)-$$}"
[ "$(cat "$EXP_DIR/SEED")" = 2026110401 ] || { echo "SEED が条件の値と違う" >&2; exit 1; }
[ -f "$OUT/repro_check.json" ] || { echo "A・B の本計算の repro_check.json が無い" >&2; exit 1; }
# selftest の出力だけを先に消す（本計算の結果は本計算の直前に消す・Codex の指摘 1）
rm -rf "$OUT/mutations_sym" "$OUT/selftest_sym.json"
mkdir -p "$OUT/mutations_sym"
"$PY" -I -X utf8 "$SC/selftest_sym.py" "$OUT/selftest_sym.json" --run-id "$RUN_ID"
for m in y1 y2 y3 y4 y5; do
  set +e
  "$PY" -I -X utf8 "$SC/selftest_sym.py" "$OUT/mutations_sym/$m.json" --mutate "$m" --run-id "$RUN_ID" > "$OUT/mutations_sym/$m.log" 2>&1
  echo $? > "$OUT/mutations_sym/$m.exit"
  set -e
done
"$PY" -I -X utf8 - "$OUT/mutations_sym" "$RUN_ID" <<'PY'
import json, os, sys
d, run_id = sys.argv[1:3]
want = {"y1": "P-REPLAY", "y2": "P-SYMPRIOR", "y3": "P-SELW", "y4": "P-REPLAY03", "y5": "P-SYMCELL"}
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
# 書く値の場所を確かめてから消す（ディレクトリでない・入力と同じでない・Codex の指摘 2）
[ ! -d "$SVALS" ] || { echo "SVALS がディレクトリを指している" >&2; exit 1; }
for p in "$RAW.coauthor.pkl" "$BVALS"; do
  [ "$("$PY" -I -c 'import os,sys;print(os.path.normcase(os.path.realpath(sys.argv[1])))' "$p")" != \
    "$("$PY" -I -c 'import os,sys;print(os.path.normcase(os.path.realpath(sys.argv[1])))' "$SVALS")" ] || { echo "SVALS が入力と同じ" >&2; exit 1; }
done
rm -f -- "$OUT/sym_summary.json" "$OUT/sym_tables.md" "$OUT/sym_check.json" "$OUT/sym_timing.json" "$OUT/provenance_sym.json" "$SVALS"
"$PY" -I -X utf8 "$SC/sym.py" "$COA" "$RAW" "$BVALS" "$SVALS" "$OUT" "$JOBS" --run-id "$RUN_ID"
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" \
  "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261112-selection-split-and-smoothing/scripts experiments/20261112-selection-split-and-smoothing/run_sym.sh experiments/20261112-selection-split-and-smoothing/conditions.md experiments/20261106-tau-mode-candidate/scripts)" \
  "$EXP_DIR" "$RUN_ID" "$OUT/provenance_sym.json" "$JOBS" <<'PY'
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
                   run_sym_sh=h(os.path.join(exp, "run_sym.sh")), conditions=h(os.path.join(exp, "conditions.md")),
                   pinned=pinned4.hashes(), sym_check=json.load(open(os.path.join(d, "sym_check.json"))),
                   sym_timing=json.load(open(os.path.join(d, "sym_timing.json"))),
                   sym_summary_sha256=h(os.path.join(d, "sym_summary.json"))), f, indent=1)
PY
echo "終わり: $RUN_ID"
