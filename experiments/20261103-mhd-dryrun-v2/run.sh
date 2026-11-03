#!/usr/bin/env bash
# MhD の配管の空回し 第 2 版（conditions.md）。(a) 合成の日の模擬・(b) CoAuthor の版の直し。
# データと中間は repo の外。結果は詰まりの推定ではない。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
WORK="$DATA_DIR/landscape/coauthor_work"
OUT="${OUT:-$EXP_DIR/results}"
SEED="$(cat "$EXP_DIR/SEED")"
PY="python3 -I"
mkdir -p "$OUT"
GIT_HEAD="$(git -C "$REPO_ROOT" rev-parse HEAD)"
GIT_DIRTY="$(git -C "$REPO_ROOT" status --porcelain -- experiments/20261103-mhd-dryrun-v2/scripts experiments/20261103-mhd-dryrun-v2/run.sh experiments/20261103-mhd-dryrun-v2/conditions.md experiments/20261103-mhd-dryrun-v2/SEED)"

# 陽性対照（通らなければ止まる）
$PY "$EXP_DIR/scripts/daysim.py" --selftest "$SEED" "$OUT"
$PY "$EXP_DIR/scripts/dryrun_v2.py" --selftest "$WORK" "$SEED" "$OUT"
# 変異（P3・C1 が赤になることを JSON で名指しで確かめる。最後まで走らなかったら止める）
check_red() {  # $1 = json, $2 = 名指しの対照
  $PY - "$1" "$2" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
if "SELFTEST" not in d:
    sys.exit("最後まで走っていない: " + sys.argv[1])
if d[sys.argv[2]]["pass_"]:
    sys.exit("変異で %s が赤にならなかった: %s" % (sys.argv[2], sys.argv[1]))
print("red as expected", sys.argv[2], sys.argv[1])
PYEOF
}
for m in m1 m2; do
  rm -f "$OUT/selftest_daysim_$m.json" "$OUT/selftest_coauthor_$m.json"
  $PY "$EXP_DIR/scripts/daysim.py" --selftest --mutate "$m" "$SEED" "$OUT" || true
  check_red "$OUT/selftest_daysim_$m.json" P3
  $PY "$EXP_DIR/scripts/dryrun_v2.py" --selftest --mutate "$m" "$WORK" "$SEED" "$OUT" || true
  check_red "$OUT/selftest_coauthor_$m.json" C1
done
# 本計算
$PY "$EXP_DIR/scripts/daysim.py" "$SEED" "$OUT"
$PY "$EXP_DIR/scripts/dryrun_v2.py" "$WORK" "$SEED" "$OUT"
# 来歴（HEAD と未コミットの変更は冒頭で取った）
$PY - "$GIT_HEAD" "$GIT_DIRTY" "$WORK" "$EXP_DIR/scripts/daysim.py" "$EXP_DIR/scripts/dryrun_v2.py" "$OUT/provenance.json" <<'PYEOF'
import glob, hashlib, json, os, sys
import numpy
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
fs = sorted(f for f in glob.glob(sys.argv[3] + "/s*.json") if os.path.basename(f) != "sessions.json")
json.dump({"git_head": sys.argv[1], "git_dirty_paths": [l for l in sys.argv[2].splitlines() if l],
           "script_sha256": {"daysim.py": h(sys.argv[4]), "dryrun_v2.py": h(sys.argv[5])},
           "coauthor_session_files": len(fs),
           "coauthor_session_sha256_of_sha256_list": hashlib.sha256("".join(os.path.basename(f) + h(f) for f in fs).encode()).hexdigest(),
           "coauthor_sessions_json_sha256": h(sys.argv[3] + "/sessions.json"),
           "coauthor_build_summary_sha256": h(sys.argv[3] + "/build_summary.json"),
           "python": sys.version.split()[0], "numpy": numpy.__version__},
          open(sys.argv[6], "w"), indent=1)
PYEOF
