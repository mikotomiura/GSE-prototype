#!/usr/bin/env bash
# EH1 round 2 of the portrait: synthetic traces only, no participants.
# Criteria are frozen in .steering/20261009-portrait-eh1-round2/design.md section 3 (commit ea02e557;
# section 3.11, the oracle, added before any real configuration was run: commit 6b8ef7de).
#
# Usage: bash run.sh [--smoke | --pilot] [--world v1|v2] [--jobs N]
#   v2 = the primary record of round 2; v1 = secondary (E1-3 declared not applicable before the results).
#   The traces are generated exactly as in round 1 (same generator, same SEED).
#   --pilot  design 3.10: SEED + 1, world v2, 40 P sessions, E1-3 of the positive controls only. Writes to
#            results/pilot-<world>/ (git-ignored); copy the numbers to design section 8 by hand.
#   --jobs   parallel workers of checks.py (default 16). Lower it on machines with little memory; the
#            results do not depend on it (design 3.9).
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
PILOT=""
WORLD="v2"
JOBS=16
while [ $# -gt 0 ]; do
  case "$1" in
    --smoke) SMOKE="--smoke"; shift ;;
    --pilot) PILOT="--pilot"; shift ;;
    --world) WORLD="$2"; shift 2 ;;
    --jobs) JOBS="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
case "$WORLD" in v1|v2) ;; *) echo "--world must be v1 or v2" >&2; exit 2 ;; esac
case "$JOBS" in ''|*[!0-9]*) echo "--jobs must be a positive integer" >&2; exit 2 ;; esac
[ "$JOBS" -ge 1 ] || { echo "--jobs must be a positive integer" >&2; exit 2; }
if [ -n "$SMOKE" ] && [ -n "$PILOT" ]; then echo "--smoke and --pilot are exclusive" >&2; exit 2; fi
if [ -n "$PILOT" ] && [ "$WORLD" != "v2" ]; then echo "--pilot runs on world v2 only (design 3.10)" >&2; exit 2; fi

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
fi
# Windows (round 1 notes W1): git-bash resolves the name without .exe for -x, but Python's open() does not
if [ ! -f "$GSE_REPLAY" ] && [ -f "$GSE_REPLAY.exe" ]; then GSE_REPLAY="$GSE_REPLAY.exe"; fi
[ -f "$GSE_REPLAY" ] || { echo "gse-replay not found: $GSE_REPLAY" >&2; exit 2; }

SEED_FILE="$EXP_DIR/SEED"
GEN_EXTRA=""
if [ -n "$PILOT" ]; then
  SUFFIX="pilot-$WORLD"
else
  SUFFIX="$WORLD${SMOKE:+-smoke}"
fi
WORK="$EXP_DIR/work-$SUFFIX"
# results are written to a partial directory and replace results/$SUFFIX only when every step has passed,
# so that a failed run never leaves files of two runs side by side (round 2 /cross-review)
FINAL_OUT="$EXP_DIR/results/$SUFFIX"
OUT="$EXP_DIR/results/.partial-$SUFFIX"
rm -rf "$WORK" "$OUT"
mkdir -p "$OUT" "$WORK"
if [ -n "$PILOT" ]; then
  # design 3.10: another seed and 40 P sessions (the other sets at smoke size; the pilot does not use them)
  read -r OFFSET PILOT_P < <("$PY" -c "import json,sys; p=json.load(open(sys.argv[1],encoding='utf-8'))['sets']['pilot']; print(int(p['seed_offset']), int(p['P']))" "$EXP_DIR/config.json")
  case "$OFFSET$PILOT_P" in ''|*[!0-9]*) echo "sets.pilot in config.json must hold non-negative integers" >&2; exit 2 ;; esac
  SEED_FILE="$WORK/SEED.pilot"
  echo $(( $(tr -d '[:space:]' < "$EXP_DIR/SEED") + OFFSET )) > "$SEED_FILE"
  GEN_EXTRA="--smoke --p-n $PILOT_P"
fi
cd "$EXP_DIR/scripts"

# Step 1: generate the synthetic sessions (labels in a separate file the replay never sees)
"$PY" gen_sessions.py "$EXP_DIR/config.json" "$SEED_FILE" "$WORK" --hmm-version "$HMM_VERSION" --world "$WORLD" $SMOKE $GEN_EXTRA

# Step 0 (ADR-013 Migration 4): the capabilities gate, on the inputs this analysis reads (key rows).
# It runs after generation because the inputs are generated here.
CAPS_TMP="$OUT/.capabilities.json.tmp"
PYTHONUTF8=1 "$PY" "$REPO_ROOT/scripts/capabilities_gate.py" "$WORK/ndjson" --require key --json > "$CAPS_TMP"
mv "$CAPS_TMP" "$OUT/capabilities.json"
echo "Step 0 OK: capabilities gate passed"

# Step 2: GSE's own computation of the F series
"$PY" replay_all.py "$GSE_REPLAY" "$WORK"

# Step 3: self-tests of the instruments, then the checks
if [ -n "$PILOT" ]; then
  "$PY" checks.py "$EXP_DIR/config.json" "$SEED_FILE" "$WORK" "$OUT" --world "$WORLD" --jobs "$JOBS" --pilot
  rm -rf "$FINAL_OUT" && mv "$OUT" "$FINAL_OUT"
  echo "pilot done: $FINAL_OUT/pilot_e13.json (not committed; copy the PC numbers to design section 8)"
  exit 0
fi
"$PY" selftest.py "$EXP_DIR/config.json" "$WORK"
"$PY" checks.py "$EXP_DIR/config.json" "$SEED_FILE" "$WORK" "$OUT" --world "$WORLD" --jobs "$JOBS" $SMOKE
"$PY" render_samples.py "$EXP_DIR/config.json" "$SEED_FILE" "$WORK" "$OUT"

# Step 4: provenance
"$PY" - "$OUT/provenance.json" "$GSE_REPLAY" "$HMM_VERSION" "$WORLD" "$SMOKE" "$EXP_DIR" "$REPO_ROOT" "$JOBS" "$SEED_FILE" <<'PYEOF'
import hashlib, json, os, platform, subprocess, sys
from importlib.metadata import version
out, binary, hmm, world, smoke, exp_dir, repo, jobs, seed_file = sys.argv[1:10]
sha = hashlib.sha256(open(binary, "rb").read()).hexdigest()
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
def git_dirty(args):
    # None when git itself fails (not on PATH, dubious ownership): an empty output would read as clean
    r = subprocess.run(["git"] + args, capture_output=True, text=True)
    return bool(r.stdout.strip()) if r.returncode == 0 else None
# the instruments only: results/ fills with untracked files while the run writes them
dirty = git_dirty(["-C", exp_dir, "status", "--porcelain", "--", ".", ":(exclude)results"])
src_dirty = git_dirty(["-C", repo, "status", "--porcelain", "--", "src-tauri"])
json.dump({"world": world, "smoke": bool(smoke), "git_commit": commit, "experiment_dir_dirty": dirty,
           "src_tauri_dirty": src_dirty,
           "gse_replay_sha256": sha, "hmm_version": hmm, "python": platform.python_version(),
           "platform": platform.platform(), "cpu_count": os.cpu_count(), "jobs": int(jobs),
           "seed": int(open(seed_file).read().strip()),
           "packages": {p: version(p) for p in ("numpy", "scipy", "scikit-learn", "pillow")}},
          open(out, "w"), indent=1)
PYEOF
rm -rf "$FINAL_OUT" && mv "$OUT" "$FINAL_OUT"
echo "done: $FINAL_OUT"
