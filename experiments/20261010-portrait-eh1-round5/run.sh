#!/usr/bin/env bash
# EH1 round 5 of the portrait: synthetic traces only, no participants. E1-3 only, world v2 only.
# Criteria are frozen in .steering/20261010-portrait-eh1-round5/design.md section 3 (commit 92d262fd).
#
# Usage: bash run.sh [--smoke] [--pilot | --pilot-replicate | --replicate] [--jobs N]
#   (no mode)          the main run: the traces are generated exactly as in rounds 1 to 4 (same generator, same
#                      SEED, world v2); compares the names round 4 ran with round 4's e13.json (compare_round4.json).
#   --pilot            design 3.9 (the main run's pilot): SEED + 1, 40 P sessions, PC1 and PCahead of each form and
#                      scheduler on the lambda grid; writes results/pilot-v2/ (git-ignored). Write the chosen lambdas
#                      to config.json pcahead.lam and the numbers to design section 8.
#   --pilot-replicate  design 3.9 (the replicate pilot): SEED + replicate.pilot_seed_offset, replicate.P P sessions,
#                      the 12 replicate controls on the grid, L300 only; writes results/pilot-replicate/ (git-ignored).
#                      Write the chosen lambdas to config.json replicate.lam.
#   --replicate        design 3.10: replicate r = 0 .. replicate.n - 1 with seed SEED + replicate.seed_offset + r,
#                      replicate.P P sessions, the 12 controls, L300 only. A replicate whose process fails is run again
#                      with the same seed up to replicate.max_retries times, then written as crashed. Replicates already
#                      written to results/.partial-replicate/ are kept (a stopped run resumes); the summary checks that
#                      all of them line up (seeds, controls, lambdas, config hash, commit). Writes results/replicate/.
#   --smoke            with no mode: the pipeline check of the main run (P 12, bootstrap 200, 2 permutations);
#                      with --pilot-replicate or --replicate: the same at the smoke size (P 12; one replicate);
#                      written to results/<mode>-smoke/ (git-ignored).
#   --jobs             parallel workers of checks.py (default 8). The results do not depend on it (design 3.8).
#
# Environment:
#   GSE_REPLAY  path to a gse-replay binary built from this commit (default: build it with cargo
#               into $CARGO_TARGET_DIR or ../../../_target-portrait-eh1 next to the worktree)
#   PYTHON      python with requirements.txt installed (default: .venv next to this file)
#
# The generated NDJSON and the per-second features stay in work-*/ (git-ignored). Only the aggregated JSON of the
# main run (results/v2/) and of the replicates (results/replicate/) are committed.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMOKE=""
MODE="main"
WORLD="v2"
JOBS=8
while [ $# -gt 0 ]; do
  case "$1" in
    --smoke) SMOKE="--smoke"; shift ;;
    --pilot) [ "$MODE" = main ] || { echo "one mode only" >&2; exit 2; }; MODE="pilot"; shift ;;
    --pilot-replicate) [ "$MODE" = main ] || { echo "one mode only" >&2; exit 2; }; MODE="pilot-replicate"; shift ;;
    --replicate) [ "$MODE" = main ] || { echo "one mode only" >&2; exit 2; }; MODE="replicate"; shift ;;
    --jobs) JOBS="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
case "$JOBS" in ''|*[!0-9]*) echo "--jobs must be a positive integer" >&2; exit 2 ;; esac
[ "$JOBS" -ge 1 ] || { echo "--jobs must be a positive integer" >&2; exit 2; }
if [ -n "$SMOKE" ] && [ "$MODE" = pilot ]; then echo "--smoke and --pilot are exclusive" >&2; exit 2; fi

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

# cfg <python expression on c (config.json)>: prints one non-negative integer or fails
cfg() {
  local v
  v="$("$PY" -c "import json,sys; c=json.load(open(sys.argv[1],encoding='utf-8')); v=$1; print(v) if type(v) is int and v >= 0 else sys.exit('config.json: $1 must be a non-negative integer')" "$EXP_DIR/config.json")"
  v="${v%$'\r'}"  # Python on Windows ends the line with CRLF
  case "$v" in ''|*[!0-9]*) echo "config.json: $1 must be a non-negative integer" >&2; exit 2 ;; esac
  echo "$v"
}
BASE_SEED="$(tr -d '[:space:]' < "$EXP_DIR/SEED")"
case "$BASE_SEED" in ''|*[!0-9]*) echo "SEED must be a non-negative integer" >&2; exit 2 ;; esac

case "$MODE" in
  main) SUFFIX="$WORLD${SMOKE:+-smoke}" ;;
  pilot) SUFFIX="pilot-$WORLD" ;;
  *) SUFFIX="$MODE${SMOKE:+-smoke}" ;;
esac
WORK="$EXP_DIR/work-$SUFFIX"
# results are written to a partial directory and replace results/$SUFFIX only when every step has passed,
# so that a failed run never leaves files of two runs side by side (round 2 /cross-review)
FINAL_OUT="$EXP_DIR/results/$SUFFIX"
OUT="$EXP_DIR/results/.partial-$SUFFIX"
rm -rf "$WORK"
if [ "$MODE" != replicate ]; then rm -rf "$OUT"; fi  # design 3.10: written replicates are kept (resume)
mkdir -p "$OUT" "$WORK"
# publish: the old results are moved aside (not deleted) before the new ones take their place, and removed
# only after the move succeeded. ⚠️ Do not run two runs of the same world and mode at the same time.
publish() {
  local old="$EXP_DIR/results/.old-$SUFFIX"
  rm -rf "$old"
  if [ -e "$FINAL_OUT" ]; then mv "$FINAL_OUT" "$old"; fi
  mv -T "$OUT" "$FINAL_OUT"
  rm -rf "$old"
}
cd "$EXP_DIR/scripts"

# prepare <seed> <work> <extra gen_sessions args...>: Step 1 (generate the synthetic sessions; labels in a separate
# file the replay never sees), Step 0 (ADR-013 Migration 4: the capabilities gate on the inputs this analysis reads,
# after generation because the inputs are generated here) and Step 2 (GSE's own computation of the F series)
prepare() {
  local seed="$1" work="$2"
  shift 2
  # every step ends the function on failure: set -e does not act inside a function called as an if condition
  mkdir -p "$work" || return 1
  echo "$seed" > "$work/SEED.run" || return 1
  "$PY" gen_sessions.py "$EXP_DIR/config.json" "$work/SEED.run" "$work" --hmm-version "$HMM_VERSION" --world "$WORLD" "$@" \
    || return 1
  local caps_tmp="$work/.capabilities.json.tmp"
  PYTHONUTF8=1 "$PY" "$REPO_ROOT/scripts/capabilities_gate.py" "$work/ndjson" --require key --json > "$caps_tmp" || return 1
  mv "$caps_tmp" "$work/capabilities.json" || return 1
  echo "Step 0 OK: capabilities gate passed (seed $seed)"
  "$PY" replay_all.py "$GSE_REPLAY" "$work" || return 1
}

if [ "$MODE" = replicate ]; then
  N="$(cfg "c['replicate']['n']")"
  OFF="$(cfg "c['replicate']['seed_offset']")"
  RETRIES="$(cfg "c['replicate']['max_retries']")"
  REP_P="$(cfg "c['replicate']['P']")"
  GEN_EXTRA=(--smoke --p-n "$REP_P")
  if [ -n "$SMOKE" ]; then N=1; GEN_EXTRA=(--smoke); fi
  for (( r = 0; r < N; r++ )); do
    RJ="$OUT/$(printf 'replicate_%02d.json' "$r")"
    if [ -f "$RJ" ]; then echo "replicate $r: kept $RJ"; continue; fi
    SEED_R=$(( 10#$BASE_SEED + 10#$OFF + r ))  # 10#: never octal
    attempt=0
    until [ -f "$RJ" ]; do
      if [ "$attempt" -gt "$RETRIES" ]; then
        echo "replicate $r: still failing after $RETRIES retries -> crashed (design 3.10)" >&2
        "$PY" summarize_replicates.py crashed "$EXP_DIR/config.json" "$EXP_DIR/SEED" "$r" "$OUT"
        break
      fi
      [ "$attempt" -gt 0 ] && echo "replicate $r: retry $attempt with the same seed $SEED_R at $(date '+%F %T')" >&2
      attempt=$(( attempt + 1 ))
      rm -rf "$WORK"
      if prepare "$SEED_R" "$WORK" "${GEN_EXTRA[@]}" \
         && "$PY" checks.py "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" "$OUT" --world "$WORLD" --jobs "$JOBS" \
              --replicate "$r"; then
        :
      else
        rm -f "$RJ"  # a half-written file is not a replicate
      fi
    done
    rm -rf "$WORK"
  done
  "$PY" summarize_replicates.py "$EXP_DIR/config.json" "$EXP_DIR/SEED" "$OUT" "$N" "$OUT/replicate_summary.json"
  publish
  echo "done: $FINAL_OUT"
  exit 0
fi

if [ "$MODE" = pilot ]; then
  OFFSET="$(cfg "c['sets']['pilot']['seed_offset']")"
  PILOT_P="$(cfg "c['sets']['pilot']['P']")"
  prepare $(( 10#$BASE_SEED + 10#$OFFSET )) "$WORK" --smoke --p-n "$PILOT_P"
  "$PY" checks.py "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" "$OUT" --world "$WORLD" --jobs "$JOBS" --pilot
  publish
  echo "pilot done: $FINAL_OUT/pilot_e13.json (not committed; write the lambdas to config.json, the numbers to design section 8)"
  exit 0
fi

if [ "$MODE" = pilot-replicate ]; then
  OFFSET="$(cfg "c['replicate']['pilot_seed_offset']")"
  REP_P="$(cfg "c['replicate']['P']")"
  if [ -n "$SMOKE" ]; then GEN_EXTRA=(--smoke); else GEN_EXTRA=(--smoke --p-n "$REP_P"); fi
  prepare $(( 10#$BASE_SEED + 10#$OFFSET )) "$WORK" "${GEN_EXTRA[@]}"
  "$PY" checks.py "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" "$OUT" --world "$WORLD" --jobs "$JOBS" --pilot-replicate
  publish
  echo "replicate pilot done: $FINAL_OUT/pilot_replicate_e13.json (not committed; write the lambdas to config.json replicate.lam)"
  exit 0
fi

# the main run (and its smoke)
prepare "$BASE_SEED" "$WORK" $SMOKE
mv "$WORK/capabilities.json" "$OUT/capabilities.json"

# Step 3: self-tests of the instruments, then the checks
"$PY" selftest.py "$EXP_DIR/config.json" "$WORK"
"$PY" checks.py "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" "$OUT" --world "$WORLD" --jobs "$JOBS" $SMOKE
if [ -z "$SMOKE" ]; then
  # design 3.6 (descriptive): the same names against round 4 (round 4's smoke results are not committed)
  "$PY" compare_round4.py "$EXP_DIR/../20261010-portrait-eh1-round4/results/$WORLD/e13.json" "$OUT/e13.json" \
    "$OUT/compare_round4.json"
fi

# Step 4: provenance
"$PY" - "$OUT/provenance.json" "$GSE_REPLAY" "$HMM_VERSION" "$WORLD" "$SMOKE" "$EXP_DIR" "$REPO_ROOT" "$JOBS" "$WORK/SEED.run" <<'PYEOF'
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
publish
echo "done: $FINAL_OUT"
