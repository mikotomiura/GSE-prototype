#!/usr/bin/env bash
# Rhythm stage desk check: synthetic traces only, no participants.
# Design: .steering/20261012-rhythm-stage-desk-check/design.md (frozen 2b7db259; world v4).
#
# Usage: bash run.sh (--selftest | --ceiling | --pilot | --smoke | --main) [--jobs N]
#   --selftest  design 3.7: every self-test (the gse-replay causality test when GSE_REPLAY is set).
#   --ceiling   design 3.0 (pilot 0, before the freeze): the self-tests without gse-replay, then SEED +
#               ceiling.seed_offset, ceiling.P P sessions of each world in ceiling.prefer, AUC(A) and AUC(A_speed) per
#               label and classifier, and the chosen world. Writes results/ceiling/ (committed).
#   --pilot     design 3.9 (pilot 1, after the freeze): SEED + sets.pilot.seed_offset, sets.pilot.P P sessions of world
#               v4 through gse-replay, the self-tests on them, then PC1 and the PC-stall of each of the
#               24 candidates on [0] + pc_stall.pilot_grid, L300 only. No candidate is run. Writes results/pilot/
#               (committed). Write the chosen lambdas to config.json pc_stall.lam and the numbers to design section 8.
#   --smoke     the pipeline check of the main run: SEED + 2 (not the main run's sessions), 12 P sessions and their twins, every self-test, then the
#               checks with bootstrap 200 and 2 permutations. Writes results/main-smoke/ (git-ignored).
#   --main      design 3.1-3.6: SEED, sets.P.n P sessions of world v4 and their twins through gse-replay, every
#               self-test, then the checks. Writes results/main/ (committed). Run it when no CI job is running on
#               this machine (design 4: G-GEAR is a self-hosted runner).
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
WORLD="v4"  # design 3.0: the world chosen by pilot 0 (the freeze)
EXPECTED_REPLAY_SHA="71d09dab44526f2322a05833ae1a0fb33ffcc4908bfba796258276f083d78986"  # design 1.1
MODE=""
JOBS=8
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest|--ceiling|--pilot|--smoke|--main)
      [ -z "$MODE" ] || { echo "one mode only" >&2; exit 2; }; MODE="${1#--}"; shift ;;
    --jobs) JOBS="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$MODE" ] || { echo "a mode is required: --selftest, --ceiling, --pilot, --smoke or --main" >&2; exit 2; }
case "$JOBS" in ''|*[!0-9]*) echo "--jobs must be a positive integer" >&2; exit 2 ;; esac
[ "$JOBS" -ge 1 ] || { echo "--jobs must be a positive integer" >&2; exit 2; }

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

# provenance <out file> <seed> <worlds> (design 3.8)
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
publish() {
  local final="$EXP_DIR/results/$1" part="$EXP_DIR/results/.partial-$1" old="$EXP_DIR/results/.old-$1"
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
  "$PY" gen_sessions.py "$EXP_DIR/config.json" "$work/SEED.run" "$work" --hmm-version "$HMM_VERSION" --world "$WORLD" "$@" \
    || return 1
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
  WORLDS="$("$PY" -c "import json,sys; print(' '.join(json.load(open(sys.argv[1],encoding='utf-8'))['ceiling']['prefer']))" "$EXP_DIR/config.json")"
  WORLDS="${WORLDS%$'\r'}"
  WORK_ARGS=()
  for W in $WORLDS; do
    WORK="$EXP_DIR/work-ceiling-$W"
    rm -rf "$WORK"
    mkdir -p "$WORK"
    echo "$SEED_RUN" > "$WORK/SEED.run"
    "$PY" gen_sessions.py "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" --hmm-version "$HMM_VERSION" --world "$W" \
      --smoke --p-n "$P_N"
    WORK_ARGS+=(--work "$W=$WORK")
  done
  "$PY" ceiling.py "$EXP_DIR/config.json" "$EXP_DIR/work-ceiling-${WORLDS%% *}/SEED.run" "$OUT" "${WORK_ARGS[@]}" --jobs "$JOBS"
  GSE_REPLAY="" provenance "$OUT/provenance.json" "$SEED_RUN" "$WORLDS"
  publish "$SUFFIX"
  for W in $WORLDS; do rm -rf "$EXP_DIR/work-ceiling-$W"; done
  echo "done: $EXP_DIR/results/$SUFFIX/ceiling.json (append the values and the chosen world to the end of design 3.0, then commit)"
  exit 0
fi

case "$MODE" in
  pilot) SUFFIX="pilot"; OFFSET="$(cfg "c['sets']['pilot']['seed_offset']")"; P_N="$(cfg "c['sets']['pilot']['P']")" ;;
  smoke) SUFFIX="main-smoke"; OFFSET=2; P_N=12 ;;  # SEED + 2: the smoke does not look at the main run's sessions
  main) SUFFIX="main"; OFFSET=0; P_N="$(cfg "c['sets']['P']['n']")" ;;
esac
SEED_RUN=$(( 10#$BASE_SEED + 10#$OFFSET ))
if [ "$MODE" != pilot ]; then  # code-reviewer L5: before hours of generation and replay
  "$PY" -c "import json,sys; sys.path.insert(0,'.'); import stage; c=json.load(open(sys.argv[1],encoding='utf-8')); m=[k for k in stage.candidates() if c['pc_stall']['lam'].get(k) is None]; sys.exit('config.json pc_stall.lam is not set for ' + str(m) + ': run the pilot first') if m else None" "$EXP_DIR/config.json"
fi
WORK="$EXP_DIR/work-$SUFFIX"
OUT="$EXP_DIR/results/.partial-$SUFFIX"
rm -rf "$WORK" "$OUT"
mkdir -p "$OUT"
# P sessions only are used; the other sets are made at the smoke size (each P session is drawn from
# derive_rng(seed, "P", i) and is written first, so it does not depend on the other sets: data.md)
prepare "$SEED_RUN" "$WORK" --smoke --p-n "$P_N"
mv "$WORK/capabilities.json" "$OUT/capabilities.json"
if [ "$MODE" = pilot ]; then
  selftest "${REPLAY_ARGS[@]}" --work "$WORK" --seed-file "$WORK/SEED.run" --jobs "$JOBS"
  "$PY" checks.py "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" "$OUT" --jobs "$JOBS" --pilot
else
  twins "$WORK"
  selftest "${REPLAY_ARGS[@]}" --work "$WORK" --seed-file "$WORK/SEED.run" --jobs "$JOBS" --require-twins
  SMOKE_ARG=()
  [ "$MODE" = smoke ] && SMOKE_ARG=(--smoke)
  "$PY" checks.py "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" "$OUT" --jobs "$JOBS" "${SMOKE_ARG[@]}"
fi
provenance "$OUT/provenance.json" "$SEED_RUN" "$WORLD"
publish "$SUFFIX"
rm -rf "$WORK"
echo "done: $EXP_DIR/results/$SUFFIX"
