#!/usr/bin/env bash
# Rhythm stage desk check, graded world: synthetic traces only, no participants.
# Design: .steering/20261014-rhythm-stage-graded-world/design.md (the graded world, the steps, pilot 0 per step, the
# L1800 controls, the lambdas per step), on top of .steering/20261013-rhythm-stage-round2/design.md (round 2: the
# lambda choice) and .steering/20261012-rhythm-stage-desk-check/design.md (round 1). Copied from
# experiments/20261013-rhythm-stage-round2/run.sh (d98103a0).
#
# Usage: bash run.sh (--selftest | --ceiling | --pilot | --smoke | --main) [--step t025|t050|t075] [--jobs N]
#   --selftest  design 3.7: every self-test (the gse-replay causality test when GSE_REPLAY is set).
#   --ceiling   design 3.0 (pilot 0, after the freeze, before any pilot 1): the self-tests without gse-replay, then
#               SEED + ceiling.seed_offset, ceiling.P P sessions of each step in ceiling.steps (--world graded --t),
#               AUC(A) and AUC(A_speed) per label and classifier, and each step's status (go, ceiling, unmeasured).
#               Writes results/ceiling/ (committed).
#   --pilot     design 3.9 (needs --step; the step must be go in results/ceiling/ceiling.json): SEED +
#               sets.pilot.seed_offset, sets.pilot.P P sessions of the step through gse-replay, the self-tests on them,
#               then the L300 part (PC1, PCs-) and the L1800 part (PC1-1800, PCl-) on [0] + pc_stall.pilot_grid. No
#               candidate is run. Writes results/<step>/pilot/ (committed). Then, from this directory,
#               `$PYTHON scripts/checks.py --apply-pilot config.json results/<step>/pilot/pilot.json <step>` writes
#               pc_stall.lam.<step> and pc_stall.lam_1800.<step>; the numbers go to design section 8.
#   --smoke     the pipeline check of the main run of a step: SEED + 2, 12 P sessions and their twins, every
#               self-test, then the checks with bootstrap 200 and 2 permutations. Writes results/<step>/main-smoke/
#               (git-ignored).
#   --main      design 3.1-3.6: SEED, sets.P.n P sessions of the step and their twins through gse-replay, every
#               self-test, then the checks. Writes results/<step>/main/ (committed). Run it when no CI job and no other
#               heavy job is running on this machine (design 4: G-GEAR is a self-hosted runner).
#   --jobs      parallel workers (default 8). The results do not depend on it.
#
# Environment:
#   PYTHON      python with requirements.txt installed (default: .venv next to this file)
#   GSE_REPLAY  the gse-replay binary of EH1 (design 1.1: C:/wt/_target-portrait-eh1/release/gse-replay.exe, SHA-256
#               71d09dab...986, checked); required by --pilot, --smoke and --main. It is not built here.
#
# The generated NDJSON, labels and per-second features stay in work-*/ (git-ignored). Only the aggregated JSON is
# committed.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EH1_DIR="$EXP_DIR/../20261010-portrait-eh1-round5"
WORLD="graded"  # graded world design 1.3: the step's t comes from config.json ceiling.steps
EXPECTED_REPLAY_SHA="71d09dab44526f2322a05833ae1a0fb33ffcc4908bfba796258276f083d78986"  # design 1.1
MODE=""
JOBS=8
STEP=""
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest|--ceiling|--pilot|--smoke|--main)
      [ -z "$MODE" ] || { echo "one mode only" >&2; exit 2; }; MODE="${1#--}"; shift ;;
    --jobs) JOBS="$2"; shift 2 ;;
    --step) STEP="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$MODE" ] || { echo "a mode is required: --selftest, --ceiling, --pilot, --smoke or --main" >&2; exit 2; }
case "$JOBS" in ''|*[!0-9]*) echo "--jobs must be a positive integer" >&2; exit 2 ;; esac
[ "$JOBS" -ge 1 ] || { echo "--jobs must be a positive integer" >&2; exit 2; }
case "$MODE" in
  pilot|smoke|main) [ -n "$STEP" ] || { echo "--$MODE needs --step (t025, t050 or t075)" >&2; exit 2; } ;;
  *) [ -z "$STEP" ] || { echo "--step is for --pilot, --smoke and --main only" >&2; exit 2; } ;;
esac
case "$STEP" in ''|t[0-9][0-9][0-9]) ;; *) echo "--step must look like t025" >&2; exit 2 ;; esac

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
[ -n "$HMM_VERSION" ] || { echo "HMM_VERSION not found" >&2; exit 2; }

REPLAY_ARGS=()
if [ "$MODE" != ceiling ]; then
  if [ -n "${GSE_REPLAY:-}" ]; then
    # Windows (EH1 round 1 notes W1): git-bash resolves the name without .exe for -x, but Python's open() does not
    if [ ! -f "$GSE_REPLAY" ] && [ -f "$GSE_REPLAY.exe" ]; then GSE_REPLAY="$GSE_REPLAY.exe"; fi
    [ -f "$GSE_REPLAY" ] || { echo "gse-replay not found: $GSE_REPLAY" >&2; exit 2; }
    # design 1.1: the EH1 build only (code-reviewer L6)
    REPLAY_SHA="$(sha256sum "$GSE_REPLAY" | cut -d' ' -f1)"
    [ "$REPLAY_SHA" = "$EXPECTED_REPLAY_SHA" ] || { echo "gse-replay SHA-256 $REPLAY_SHA is not the EH1 build (design 1.1)" >&2; exit 2; }
    REPLAY_ARGS=(--gse-replay "$GSE_REPLAY")
  elif [ "$MODE" != selftest ]; then
    echo "GSE_REPLAY is required (design 1.1: the EH1 build, not built here)" >&2; exit 2
  fi
fi

# cfg <python expression on c (config.json)>: prints one non-negative integer or fails
cfg() {
  local v
  v="$("$PY" -c "import json,sys; c=json.load(open(sys.argv[1],encoding='utf-8')); v=eval(sys.argv[2]); print(v) if type(v) is int and v >= 0 else sys.exit('config.json: ' + sys.argv[2] + ' must be a non-negative integer')" "$EXP_DIR/config.json" "$1")"
  v="${v%$'\r'}"  # Python on Windows ends the line with CRLF
  case "$v" in ''|*[!0-9]*) echo "config.json: $1 must be a non-negative integer" >&2; exit 2 ;; esac
  echo "$v"
}
BASE_SEED="$(tr -d '[:space:]' < "$EXP_DIR/SEED")"
case "$BASE_SEED" in ''|*[!0-9]*) echo "SEED must be a non-negative integer" >&2; exit 2 ;; esac

cd "$EXP_DIR/scripts"
ST_TMP="$EXP_DIR/work-selftest"

# selftest [extra args...]: the self-tests (design 3.7); a failure stops the run
selftest() {
  rm -rf "$ST_TMP"
  "$PY" selftest.py "$EXP_DIR/config.json" "$EH1_DIR" "$ST_TMP" --hmm-version "$HMM_VERSION" "$@"
  rm -rf "$ST_TMP"
}

# provenance <out file> <seed> <worlds> (design 3.8; worlds names the step and t, graded world design 1.2)
provenance() {
  "$PY" - "$1" "$HMM_VERSION" "$EXP_DIR" "$JOBS" "$2" "$3" "$MODE" "${GSE_REPLAY:-}" <<'PYEOF'
import hashlib, json, os, platform, subprocess, sys
from importlib.metadata import version
out, hmm, exp_dir, jobs, seed, worlds, mode, binary = sys.argv[1:9]
commit = subprocess.run(["git", "-C", exp_dir, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
r = subprocess.run(["git", "-C", exp_dir, "status", "--porcelain", "--", ".", ":(exclude)results"],
                   capture_output=True, text=True)
dirty = bool(r.stdout.strip()) if r.returncode == 0 else None  # None when git itself fails
cfg_sha = hashlib.sha256(open(os.path.join(exp_dir, "config.json"), "rb").read()).hexdigest()
replay = None
if binary:
    replay = {"path": binary, "sha256": hashlib.sha256(open(binary, "rb").read()).hexdigest()}
json.dump({"mode": mode, "git_commit": commit, "experiment_dir_dirty": dirty, "config_sha256": cfg_sha,
           "hmm_version_in_meta": hmm, "gse_replay": replay, "seed": int(seed), "worlds": worlds.split(),
           "python": platform.python_version(), "platform": platform.platform(), "cpu_count": os.cpu_count(),
           "jobs": int(jobs),
           "packages": {p: version(p) for p in ("numpy", "scipy", "scikit-learn", "threadpoolctl")}},
          open(out, "w", encoding="utf-8", newline="\n"), indent=1)
PYEOF
}

# publish <suffix>: the partial directory replaces results/<suffix> only when every step has passed
# (a suffix may be <step>/<mode>: the partial and old directories flatten the slash)
publish() {
  local flat="${1//\//-}"
  local final="$EXP_DIR/results/$1" part="$EXP_DIR/results/.partial-$flat" old="$EXP_DIR/results/.old-$flat"
  mkdir -p "$(dirname "$final")"
  rm -rf "$old"
  if [ -e "$final" ]; then mv "$final" "$old"; fi
  mv -T "$part" "$final"
  rm -rf "$old"
}

# prepare <seed> <work> <gen_sessions args...>: generate the sessions (labels in a separate file the replay never
# sees), the capabilities gate on the inputs (ADR-013 Migration 4, as EH1), and gse-replay's F series per second
prepare() {
  local seed="$1" work="$2"
  shift 2
  mkdir -p "$work" || return 1
  echo "$seed" > "$work/SEED.run" || return 1
  "$PY" gen_sessions.py "$EXP_DIR/config.json" "$work/SEED.run" "$work" --hmm-version "$HMM_VERSION" --world "$WORLD" \
    --t "$T" "$@" || return 1
  local caps_tmp="$work/.capabilities.json.tmp"
  PYTHONUTF8=1 "$PY" "$REPO_ROOT/scripts/capabilities_gate.py" "$work/ndjson" --require key --json > "$caps_tmp" || return 1
  mv "$caps_tmp" "$work/capabilities.json" || return 1
  echo "Step 0 OK: capabilities gate passed (seed $seed)"
  "$PY" replay_all.py "$GSE_REPLAY" "$work" --jobs "$JOBS" || return 1
}

# twins <work>: design 3.4 item 6, the twin of each P session through gse-replay
twins() {
  "$PY" twins.py "$EXP_DIR/config.json" "$1/SEED.run" "$1" --hmm-version "$HMM_VERSION" || return 1
  "$PY" replay_all.py "$GSE_REPLAY" "$1/twins" --jobs "$JOBS" || return 1
}

# step_t <step>: the step's t from config.json ceiling.steps (graded world design 1.2)
step_t() {
  local v
  v="$("$PY" -c "import json,sys; s=json.load(open(sys.argv[1],encoding='utf-8'))['ceiling']['steps']; print(repr(float(s[sys.argv[2]]))) if sys.argv[2] in s else sys.exit('unknown step ' + sys.argv[2])" "$EXP_DIR/config.json" "$1")"
  echo "${v%$'\r'}"
}

if [ "$MODE" = selftest ]; then
  selftest "${REPLAY_ARGS[@]}"
  exit 0
fi

if [ "$MODE" = ceiling ]; then
  selftest
  SUFFIX="ceiling"
  OUT="$EXP_DIR/results/.partial-$SUFFIX"
  rm -rf "$OUT"
  mkdir -p "$OUT"
  OFFSET="$(cfg "c['ceiling']['seed_offset']")"
  P_N="$(cfg "c['ceiling']['P']")"
  SEED_RUN=$(( 10#$BASE_SEED + 10#$OFFSET ))  # 10#: never octal
  STEPS="$("$PY" -c "import json,sys; print(' '.join(json.load(open(sys.argv[1],encoding='utf-8'))['ceiling']['steps']))" "$EXP_DIR/config.json")"
  STEPS="${STEPS%$'\r'}"
  WORK_ARGS=()
  for S in $STEPS; do
    T="$(step_t "$S")"
    WORK="$EXP_DIR/work-ceiling-$S"
    rm -rf "$WORK"
    mkdir -p "$WORK"
    echo "$SEED_RUN" > "$WORK/SEED.run"
    "$PY" gen_sessions.py "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" --hmm-version "$HMM_VERSION" --world "$WORLD" \
      --t "$T" --smoke --p-n "$P_N"
    WORK_ARGS+=(--work "$S=$WORK")
  done
  "$PY" ceiling.py "$EXP_DIR/config.json" "$EXP_DIR/work-ceiling-${STEPS%% *}/SEED.run" "$OUT" "${WORK_ARGS[@]}" --jobs "$JOBS"
  GSE_REPLAY="" provenance "$OUT/provenance.json" "$SEED_RUN" "graded $STEPS"
  publish "$SUFFIX"
  for S in $STEPS; do rm -rf "$EXP_DIR/work-ceiling-$S"; done
  echo "done: $EXP_DIR/results/$SUFFIX/ceiling.json (append the values and each step's status to design section 8, then commit)"
  exit 0
fi

T="$(step_t "$STEP")"
# graded world design 3.0: only a go step runs the pilot 1, the smoke and the main run
STATUS="$("$PY" -c "import json,sys; print(json.load(open(sys.argv[1],encoding='utf-8'))['steps'][sys.argv[2]]['status'])" "$EXP_DIR/results/ceiling/ceiling.json" "$STEP")" \
  || { echo "results/ceiling/ceiling.json has no status for $STEP (run --ceiling first)" >&2; exit 2; }
STATUS="${STATUS%$'\r'}"
[ "$STATUS" = go ] || { echo "step $STEP is $STATUS in results/ceiling/ceiling.json: not run (design 3.0)" >&2; exit 2; }
case "$MODE" in
  pilot) SUFFIX="$STEP/pilot"; OFFSET="$(cfg "c['sets']['pilot']['seed_offset']")"; P_N="$(cfg "c['sets']['pilot']['P']")" ;;
  smoke) SUFFIX="$STEP/main-smoke"; OFFSET=2; P_N=12 ;;  # SEED + 2: the smoke does not look at the main run's sessions
  main) SUFFIX="$STEP/main"; OFFSET=0; P_N="$(cfg "c['sets']['P']['n']")" ;;
esac
SEED_RUN=$(( 10#$BASE_SEED + 10#$OFFSET ))
PILOT_JSON="$EXP_DIR/results/$STEP/pilot/pilot.json"
if [ "$MODE" != pilot ]; then  # code-reviewer L5: before hours of generation and replay; graded world design 1.2
  "$PY" -c "import json,sys; sys.path.insert(0,'.'); import checks; from pathlib import Path; checks.main_lams(json.load(open(sys.argv[1],encoding='utf-8')), Path(sys.argv[2]), int(sys.argv[3]), sys.argv[4])" \
    "$EXP_DIR/config.json" "$PILOT_JSON" "$BASE_SEED" "$STEP"
fi
FLAT="${SUFFIX//\//-}"
WORK="$EXP_DIR/work-$FLAT"
OUT="$EXP_DIR/results/.partial-$FLAT"
rm -rf "$WORK" "$OUT"
mkdir -p "$OUT"
# P sessions only are used; the other sets are made at the smoke size (each P session is drawn from
# derive_rng(seed, "P", i) and is written first, so it does not depend on the other sets: data.md)
prepare "$SEED_RUN" "$WORK" --smoke --p-n "$P_N"
mv "$WORK/capabilities.json" "$OUT/capabilities.json"
if [ "$MODE" = pilot ]; then
  selftest "${REPLAY_ARGS[@]}" --work "$WORK" --seed-file "$WORK/SEED.run" --jobs "$JOBS"
  "$PY" checks.py "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" "$OUT" --jobs "$JOBS" --step "$STEP" --pilot
else
  twins "$WORK"
  selftest "${REPLAY_ARGS[@]}" --work "$WORK" --seed-file "$WORK/SEED.run" --jobs "$JOBS" --require-twins
  SMOKE_ARG=()
  [ "$MODE" = smoke ] && SMOKE_ARG=(--smoke)
  "$PY" checks.py "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" "$OUT" --jobs "$JOBS" --step "$STEP" \
    --pilot-json "$PILOT_JSON" "${SMOKE_ARG[@]}"
fi
provenance "$OUT/provenance.json" "$SEED_RUN" "$WORLD step=$STEP t=$T"
publish "$SUFFIX"
rm -rf "$WORK"
echo "done: $EXP_DIR/results/$SUFFIX"
if [ "$MODE" = pilot ]; then  # design 3.9: a stopped L300 part stops the step; a stopped L1800 part does not
  STOP="$("$PY" -c "import json,sys; print(json.load(open(sys.argv[1],encoding='utf-8')).get('stop') or '')" "$PILOT_JSON")"
  STOP="${STOP%$'\r'}"
  STOP18="$("$PY" -c "import json,sys; print(json.load(open(sys.argv[1],encoding='utf-8'))['parts']['L1800'].get('stop') or '')" "$PILOT_JSON")"
  STOP18="${STOP18%$'\r'}"
  if [ -n "$STOP" ]; then
    echo "=== PILOT STOPPED (L300): $STOP — step $STEP is undecidable (pilot_stop); tell the researcher (design 3.9) ===" >&2
  else
    [ -z "$STOP18" ] || echo "=== the L1800 part stopped: $STOP18 — L1800 of step $STEP is undecidable (pilot_stop, design 3.9) ===" >&2
    echo "next: $PY scripts/checks.py --apply-pilot config.json results/$STEP/pilot/pilot.json $STEP (from $EXP_DIR)"
  fi
fi
