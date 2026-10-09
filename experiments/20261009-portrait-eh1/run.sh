#!/usr/bin/env bash
# EH1 of the portrait: synthetic traces only, no participants.
# Criteria are frozen in .steering/20261009-portrait-eh1-eh2/design.md section 3 (commit abfb2c45).
#
# Usage: bash run.sh [--smoke] [--world v1|v2]
#   v1 = the frozen design (section 1.2). v2 = the deviation of section 8 (same pause structure for
#   FLOW and STRUGGLE). Both are reported; v1 is the primary record.
#
# Environment:
#   GSE_REPLAY  path to a gse-replay binary built from this commit (default: build it with cargo
#               into $CARGO_TARGET_DIR or ../../../_target-portrait-eh1 next to the worktree)
#   PYTHON      python with requirements.txt installed (default: .venv next to this file)
#
# The generated NDJSON and the per-second features stay in work-<world>/ (git-ignored). Only the
# aggregated JSON and a few PNG files under results/<world>/ are committed.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMOKE=""
WORLD="v1"
while [ $# -gt 0 ]; do
  case "$1" in
    --smoke) SMOKE="--smoke"; shift ;;
    --world) WORLD="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
case "$WORLD" in v1|v2) ;; *) echo "--world must be v1 or v2" >&2; exit 2 ;; esac

if [ -n "${PYTHON:-}" ]; then
  PY="$PYTHON"
elif [ -x "$EXP_DIR/.venv/Scripts/python" ]; then
  PY="$EXP_DIR/.venv/Scripts/python"
elif [ -x "$EXP_DIR/.venv/bin/python" ]; then
  PY="$EXP_DIR/.venv/bin/python"
else
  PY="$(command -v python3 || command -v python)"
fi
: "${PY:?python not found}"

HMM_VERSION="$(grep -m1 'pub const HMM_VERSION' "$REPO_ROOT/src-tauri/src/analysis/engine.rs" | sed -E 's/.*"([^"]+)".*/\1/')"
if [ -z "${GSE_REPLAY:-}" ]; then
  export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$REPO_ROOT/../_target-portrait-eh1}"
  cargo build --release --bin gse-replay --manifest-path "$REPO_ROOT/src-tauri/Cargo.toml"
  GSE_REPLAY="$CARGO_TARGET_DIR/release/gse-replay"
  [ -x "$GSE_REPLAY" ] || GSE_REPLAY="$GSE_REPLAY.exe"
fi

SUFFIX="$WORLD${SMOKE:+-smoke}"
WORK="$EXP_DIR/work-$SUFFIX"
OUT="$EXP_DIR/results/$SUFFIX"
rm -rf "$WORK"
mkdir -p "$OUT"
cd "$EXP_DIR/scripts"

# Step 1: generate the synthetic sessions (labels in a separate file the replay never sees)
"$PY" gen_sessions.py "$EXP_DIR/config.json" "$EXP_DIR/SEED" "$WORK" --hmm-version "$HMM_VERSION" --world "$WORLD" $SMOKE

# Step 0 (ADR-013 Migration 4): the capabilities gate, on the inputs this analysis reads (key rows).
# It runs after generation because the inputs are generated here.
CAPS_TMP="$OUT/.capabilities.json.tmp"
PYTHONUTF8=1 "$PY" "$REPO_ROOT/scripts/capabilities_gate.py" "$WORK/ndjson" --require key --json > "$CAPS_TMP"
mv "$CAPS_TMP" "$OUT/capabilities.json"
echo "Step 0 OK: capabilities gate passed"

# Step 2: GSE's own computation of the F series
"$PY" replay_all.py "$GSE_REPLAY" "$WORK"

# Step 3: self-tests of the instruments, then the checks
"$PY" selftest.py "$EXP_DIR/config.json" "$WORK"
"$PY" checks.py "$EXP_DIR/config.json" "$EXP_DIR/SEED" "$WORK" "$OUT" $SMOKE
"$PY" render_e18.py "$EXP_DIR/config.json" "$EXP_DIR/SEED" "$WORK" "$OUT"

# Step 4: provenance
"$PY" - "$OUT/provenance.json" "$GSE_REPLAY" "$HMM_VERSION" "$WORLD" "$SMOKE" "$EXP_DIR" <<'PYEOF'
import hashlib, json, platform, subprocess, sys
from importlib.metadata import version
out, binary, hmm, world, smoke, exp_dir = sys.argv[1:7]
sha = hashlib.sha256(open(binary, "rb").read()).hexdigest()
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
dirty = bool(subprocess.run(["git", "-C", exp_dir, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip())
json.dump({"world": world, "smoke": bool(smoke), "git_commit": commit, "experiment_dir_dirty": dirty,
           "gse_replay_sha256": sha, "hmm_version": hmm, "python": platform.python_version(),
           "packages": {p: version(p) for p in ("numpy", "scipy", "scikit-learn", "pillow")}},
          open(out, "w"), indent=1)
PYEOF
echo "done: $OUT"
