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

# 陽性対照（通らなければ止まる）
$PY "$EXP_DIR/scripts/daysim.py" --selftest "$SEED" "$OUT"
$PY "$EXP_DIR/scripts/dryrun_v2.py" --selftest "$WORK" "$SEED" "$OUT"
# 変異（赤になることを確かめる。緑なら止める）
for m in m1 m2; do
  if $PY "$EXP_DIR/scripts/daysim.py" --selftest --mutate "$m" "$SEED" "$OUT"; then echo "daysim の変異 $m が赤にならなかった" >&2; exit 1; fi
  if $PY "$EXP_DIR/scripts/dryrun_v2.py" --selftest --mutate "$m" "$WORK" "$SEED" "$OUT"; then echo "dryrun_v2 の変異 $m が赤にならなかった" >&2; exit 1; fi
done
# 本計算
$PY "$EXP_DIR/scripts/daysim.py" "$SEED" "$OUT"
$PY "$EXP_DIR/scripts/dryrun_v2.py" "$WORK" "$SEED" "$OUT"
# 来歴
$PY -c "import json,sys,hashlib,glob,os;h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest();fs=sorted(glob.glob(sys.argv[3]+'/s*.json'));json.dump({'git_head':sys.argv[1],'git_dirty_paths':[l for l in sys.argv[2].splitlines() if l],'script_sha256':{'daysim.py':h(sys.argv[4]),'dryrun_v2.py':h(sys.argv[5])},'coauthor_input_files':len(fs),'coauthor_input_sha256_of_sha256_list':hashlib.sha256(''.join(os.path.basename(f)+h(f) for f in fs).encode()).hexdigest(),'python':sys.version.split()[0],'numpy':__import__('numpy').__version__},open(sys.argv[6],'w'),indent=1)" \
  "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$(git -C "$REPO_ROOT" status --porcelain -- experiments/20261103-mhd-dryrun-v2/scripts experiments/20261103-mhd-dryrun-v2/run.sh)" \
  "$WORK" "$EXP_DIR/scripts/daysim.py" "$EXP_DIR/scripts/dryrun_v2.py" "$OUT/provenance.json"
