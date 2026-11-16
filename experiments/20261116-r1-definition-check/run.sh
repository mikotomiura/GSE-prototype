#!/usr/bin/env bash
# R1 に定義の検査を当てる（conditions.md）。1 コマンドで再現する。
set -euo pipefail
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$EXP_DIR/../.." && pwd)"
DATA_DIR="${DATA_DIR:-$HOME/gse-public-data}"
PY="${DEFCHECK_PY:-$DATA_DIR/venv-findings1/bin/python}"
WORK="$DATA_DIR/cs1/work2019_holdout"
HOLD="$DATA_DIR/cs1/holdout.json"
CONF="$REPO_ROOT/experiments/20261105-findings-paper1-prefreeze/results_holdout/confirm_holdout.json"
X11="$REPO_ROOT/experiments/20261106-findings-paper1-exploration/results/explore_comparison.json"

# 入力の照合（外れたら止める）
want_hold=a5a32fcefeb97b038afd170e2672262fd5a71230d5e851319eaa076b606bdc47
got_hold=$(shasum -a 256 "$HOLD" | cut -d' ' -f1)
[ "$got_hold" = "$want_hold" ] || { echo "holdout.json の SHA-256 が違う" >&2; exit 2; }
for d in "$WORK" "${WORK}_q995" "${WORK}_w15" "${WORK}_w60"; do
  "$PY" -I -c 'import json,sys; s=json.load(open(sys.argv[1]+"/build_summary.json")).get("holdout_sha256"); sys.exit(0 if s=="028f2256d4f0bb8223c17887925a54483822e6cbda8d642e970b4bf8a20afd77" else 3)' "$d" \
    || { echo "$d の holdout_sha256 が違う" >&2; exit 3; }
done

mkdir -p "$EXP_DIR/results"
"$PY" -I - "$REPO_ROOT" "$EXP_DIR/results/provenance.json" <<'PYEOF'
import hashlib, json, subprocess, sys
root, out = sys.argv[1:]
files = ["experiments/20261116-r1-definition-check/scripts/defcheck.py",
         "experiments/20261116-r1-definition-check/conditions.md",
         "experiments/20261105-findings-paper1-prefreeze/scripts/confirm_p1.py",
         "experiments/20261105-findings-paper1-prefreeze/scripts/prefreeze.py",
         "experiments/20261101-klicke-early-stall-trigger/scripts/analyze_item2.py",
         "experiments/20261106-findings-paper1-exploration/scripts/explore_comparison.py",
         "experiments/20261107-stall-shape-multiverse/scripts/core.py",
         "experiments/20261103-stall-candidates-c1c2c6/candidates.py",
         "experiments/20261105-findings-paper1-prefreeze/results_holdout/confirm_holdout.json",
         "experiments/20261106-findings-paper1-exploration/results/explore_comparison.json"]
h = {f: hashlib.sha256(open(root + "/" + f, "rb").read()).hexdigest() for f in files}
head = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
dirty = subprocess.run(["git", "-C", root, "status", "--porcelain", "--", "experiments/20261116-r1-definition-check/scripts",
                        "experiments/20261116-r1-definition-check/conditions.md"], capture_output=True, text=True).stdout.strip()
json.dump({"git_head": head, "uncommitted_script_or_conditions": bool(dirty), "sha256": h}, open(out, "w"), indent=1)
PYEOF

export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CONFIRM_JOBS="${CONFIRM_JOBS:-8}"
"$PY" -I "$EXP_DIR/scripts/defcheck.py" "$WORK" "$HOLD" "$CONF" "$X11" "$EXP_DIR/results/defcheck.json"
