#!/usr/bin/env bash
# Rhythm stage desk check, person world: synthetic traces only, no participants.
# Design: .steering/20261123-rhythm-stage-person-world/design.md (the four steps m049 m068 r049 r068; (5) re-identification
# and (6) a per-person reader; the verdict rule and the window tables of the earlier task, in scripts/). Copied from
# experiments/20261122-rhythm-stage-relative-timing/run.sh (the selftest, provenance, publish and replay parts); changed:
# the modes, the steps, the world arguments (config.json person.steps and person.k), the order of the steps, and person.py
# as the analysis.
#
# Usage: bash run.sh (--selftest | --mutants | --ceiling | --pilot-k | --pilot | --apply-pilot | --smoke | --main)
#                    [--step m049|m068|r049|r068] [--jobs N]
#   --selftest   design 3.7: every self-test (with the gse-replay causality test when GSE_REPLAY is set).
#   --mutants    design 3.7: each mutant put in place in turn; each must make its self-test fail (19 new + 7 earlier).
#   --ceiling    design 3.0 (pilot 0; needs --step): the self-tests, then SEED + person.seed_offsets.ceiling, 240 sessions
#                of the step at full length, the baselines' AUC, PC-raw and the readers of model A; the gate of the step.
#                No gse-replay. Writes results/<step>/ceiling/ (committed). A person-r step needs person.k.<step> first.
#   --pilot-k    design 1.7 (needs a person-r --step): PC-raw AUC over the k grid at SEED + 1 (no gse-replay), the choice
#                of k against the same-ICC person-m step's pilot value. Writes results/<step>/pilot-k/ (committed).
#   --pilot      design 1.7 (needs --step and a go in results/<step>/ceiling/): SEED + 1, 240 sessions through gse-replay,
#                PCp / PCps on the lambda grid, PC1-id / PC1-pers, PC-raw. Writes results/<step>/pilot/ (committed).
#   --apply-pilot  (needs --step) writes person.k.<step> from pilot-k and pc_person.lam / pc_pers.lam from the pilot into
#                config.json (the file is changed: commit it before the smoke).
#   --smoke      the pipeline check of the main run: SEED + 2, 40 x 6 sessions at 0.05 of the length, bootstrap 200, 2
#                permutations. Writes results/<step>/main-smoke/ (git-ignored).
#   --main       design 1.5-1.8: SEED, 240 sessions through gse-replay, every self-test, then person.py --run. Writes
#                results/<step>/main/ (committed). Look at gh run list and the processes first and note them (design 4).
#   --jobs       parallel workers (default 8). The results do not depend on it.
#
# The steps run in the order m049, m068, r049, r068; a step is refused until the previous step's results/<step>/main/
# summary.json exists (design 1.3: commit each step's main result before the next).
#
# Environment:
#   PYTHON      python with requirements.txt installed (default: .venv next to this file)
#   GSE_REPLAY  the gse-replay binary of EH1 (C:/wt/_target-portrait-eh1/release/gse-replay.exe, SHA-256 71d09dab...986,
#               checked); required by --pilot, --smoke and --main. It is not built here.
#
# The generated NDJSON, labels and per-second features stay in work-*/ (git-ignored). Only aggregated JSON is committed.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPECTED_REPLAY_SHA="71d09dab44526f2322a05833ae1a0fb33ffcc4908bfba796258276f083d78986"
STEP_ORDER="m049 m068 r049 r068"
MODE=""
JOBS=8
STEP=""
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest|--mutants|--ceiling|--pilot-k|--pilot|--apply-pilot|--smoke|--main)
      [ -z "$MODE" ] || { echo "one mode only" >&2; exit 2; }; MODE="${1#--}"; shift ;;
    --jobs) JOBS="$2"; shift 2 ;;
    --step) STEP="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$MODE" ] || { echo "a mode is required: --selftest, --mutants, --ceiling, --pilot-k, --pilot, --apply-pilot, --smoke or --main" >&2; exit 2; }
case "$JOBS" in ''|*[!0-9]*) echo "--jobs must be a positive integer" >&2; exit 2 ;; esac
[ "$JOBS" -ge 1 ] || { echo "--jobs must be a positive integer" >&2; exit 2; }
case "$MODE" in
  ceiling|pilot-k|pilot|apply-pilot|smoke|main) [ -n "$STEP" ] || { echo "--$MODE needs --step (m049, m068, r049 or r068)" >&2; exit 2; } ;;
  *) [ -z "$STEP" ] || { echo "--step is not for --$MODE" >&2; exit 2; } ;;
esac
case "$STEP" in ''|m049|m068|r049|r068) ;; *) echo "--step must be m049, m068, r049 or r068" >&2; exit 2 ;; esac
[ "$MODE" != pilot-k ] || case "$STEP" in r*) ;; *) echo "--pilot-k is for the person-r steps (r049, r068)" >&2; exit 2 ;; esac

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
NEEDS_REPLAY=0
case "$MODE" in pilot|smoke|main) NEEDS_REPLAY=1 ;; esac
if [ "$MODE" = selftest ] || [ "$NEEDS_REPLAY" = 1 ]; then
  if [ -n "${GSE_REPLAY:-}" ]; then
    # Windows: git-bash resolves the name without .exe for -x, but Python's open() does not
    if [ ! -f "$GSE_REPLAY" ] && [ -f "$GSE_REPLAY.exe" ]; then GSE_REPLAY="$GSE_REPLAY.exe"; fi
    [ -f "$GSE_REPLAY" ] || { echo "gse-replay not found: $GSE_REPLAY" >&2; exit 2; }
    REPLAY_SHA="$(sha256sum "$GSE_REPLAY" | cut -d' ' -f1)"
    [ "$REPLAY_SHA" = "$EXPECTED_REPLAY_SHA" ] || { echo "gse-replay SHA-256 $REPLAY_SHA is not the EH1 build" >&2; exit 2; }
    REPLAY_ARGS=(--gse-replay "$GSE_REPLAY")
  elif [ "$NEEDS_REPLAY" = 1 ]; then
    echo "GSE_REPLAY is required (the EH1 build, not built here)" >&2; exit 2
  fi
fi

BASE_SEED="$(tr -d '[:space:]' < "$EXP_DIR/SEED")"
case "$BASE_SEED" in ''|*[!0-9]*) echo "SEED must be a non-negative integer" >&2; exit 2 ;; esac

# cfg <python expression on c (config.json)>: prints one non-negative integer or fails
cfg() {
  local v
  v="$("$PY" -c "import json,sys; c=json.load(open(sys.argv[1],encoding='utf-8')); v=eval(sys.argv[2]); print(v) if type(v) is int and v >= 0 else sys.exit('config.json: ' + sys.argv[2] + ' must be a non-negative integer')" "$EXP_DIR/config.json" "$1")"
  v="${v%$'\r'}"  # Python on Windows ends the line with CRLF
  case "$v" in ''|*[!0-9]*) echo "config.json: $1 must be a non-negative integer" >&2; exit 2 ;; esac
  echo "$v"
}

cd "$EXP_DIR/scripts"
ST_TMP="$EXP_DIR/work-selftest"

# selftest [extra args...]: the self-tests (design 3.7); a failure stops the run
selftest() {
  rm -rf "$ST_TMP"
  "$PY" selftest.py "$EXP_DIR/config.json" "$ST_TMP" --hmm-version "$HMM_VERSION" "$@"
  rm -rf "$ST_TMP"
}

# step_args <step>: the generator's world arguments of a step (person.steps, and person.k for a person-r step)
step_args() {
  local v
  v="$("$PY" -c "import json,sys; c=json.load(open(sys.argv[1],encoding='utf-8'))['person']; s=c['steps'][sys.argv[2]]; k=c['k'].get(sys.argv[2]); ok=s['world'] in ('person-m','person-r') and (s['world']=='person-m' or k is not None); print(('--world %s --icc %r' % (s['world'], float(s['icc']))) + (' --k %r' % float(k) if s['world']=='person-r' else '') if ok else sys.exit('step ' + sys.argv[2] + ': not a person world, or no k in config.json (run --pilot-k and --apply-pilot first)'))" "$EXP_DIR/config.json" "$1")"
  v="${v%$'\r'}"
  [ -n "$v" ] || return 1
  echo "$v"
}

# require_prev <step>: the previous step of STEP_ORDER has its main result (design 1.3)
require_prev() {
  local prev=""
  for s in $STEP_ORDER; do
    if [ "$s" = "$1" ]; then
      [ -z "$prev" ] || { [ -f "$EXP_DIR/results/$prev/main/summary.json" ] \
        && "$PY" -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); assert d.get('smoke') is False and d.get('five') and d.get('six') and all('verdicts' in v for v in list(d['five'].values()) + [d['six']]) and d.get('wiring', {}).get('passed') is True" "$EXP_DIR/results/$prev/main/summary.json" 2>/dev/null \
        && git -C "$EXP_DIR" ls-files --error-unmatch "results/$prev/main/summary.json" >/dev/null 2>&1 \
        && [ -z "$(git -C "$EXP_DIR" status --porcelain -- "results/$prev/main/summary.json")" ]; } \
        || { echo "step $1 comes after $prev: results/$prev/main/summary.json is missing or holds no verdicts, a passed wiring check or a committed, unchanged file (commit each step's main result first)" >&2; exit 2; }
      return 0
    fi
    prev="$s"
  done
}

# provenance <out file> <seed> <step>
provenance() {
  if [ -n "${GSE_REPLAY:-}" ] && [ "$NEEDS_REPLAY" = 1 ] && [ "$(sha256sum "$GSE_REPLAY" | cut -d' ' -f1)" != "$EXPECTED_REPLAY_SHA" ]; then
    echo "gse-replay changed during the run (SHA-256 is no longer the EH1 build): not published" >&2
    return 1
  fi
  local binary=""
  [ "$NEEDS_REPLAY" = 1 ] && binary="${GSE_REPLAY:-}"
  "$PY" - "$1" "$HMM_VERSION" "$EXP_DIR" "$JOBS" "$2" "$3" "$MODE" "$binary" <<'PYEOF'
import hashlib, json, os, platform, subprocess, sys
from importlib.metadata import version
out, hmm, exp_dir, jobs, seed, step, mode, binary = sys.argv[1:9]
commit = subprocess.run(["git", "-C", exp_dir, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
r = subprocess.run(["git", "-C", exp_dir, "status", "--porcelain", "--", ".", ":(exclude)results"],
                   capture_output=True, text=True)
dirty = bool(r.stdout.strip()) if r.returncode == 0 else None  # None when git itself fails
cfg_sha = hashlib.sha256(open(os.path.join(exp_dir, "config.json"), "rb").read()).hexdigest()
replay = None
if binary:
    replay = {"path": binary, "sha256": hashlib.sha256(open(binary, "rb").read()).hexdigest()}
cfg = json.load(open(os.path.join(exp_dir, "config.json"), encoding="utf-8"))
sys.path.insert(0, os.path.join(exp_dir, "scripts"))
import person  # the code fingerprint of the instruments (scripts/*.py and run.sh)
json.dump({"mode": mode, "code_sha256": person.code_fingerprint(), "git_commit": commit, "experiment_dir_dirty": dirty, "config_sha256": cfg_sha,
           "hmm_version_in_meta": hmm, "gse_replay": replay, "seed": int(seed), "step": step,
           "world": cfg["person"]["steps"][step], "k": cfg["person"]["k"].get(step),
           "python": platform.python_version(), "platform": platform.platform(), "cpu_count": os.cpu_count(),
           "jobs": int(jobs),
           "packages": {p: version(p) for p in ("numpy", "scipy", "scikit-learn", "threadpoolctl")}},
          open(out, "w", encoding="utf-8", newline="\n"), indent=1)
PYEOF
}

# publish <suffix>: the partial directory replaces results/<suffix> only when every step has passed
publish() {
  local flat="${1//\//-}"
  local final="$EXP_DIR/results/$1" part="$EXP_DIR/results/.partial-$flat" old="$EXP_DIR/results/.old-$flat"
  mkdir -p "$(dirname "$final")"
  rm -rf "$old"
  if [ -e "$final" ]; then mv "$final" "$old"; fi
  mv -T "$part" "$final"
  rm -rf "$old"
}

# generate <seed> <work> <extra gen_sessions args...>: the 240 sessions of the step and the capabilities gate
generate() {
  local seed="$1" work="$2"
  shift 2
  mkdir -p "$work" || return 1
  echo "$seed" > "$work/SEED.run" || return 1
  # shellcheck disable=SC2086  # WORLD_ARGS is a few words
  "$PY" gen_sessions.py "$EXP_DIR/config.json" "$work/SEED.run" "$work" --hmm-version "$HMM_VERSION" $WORLD_ARGS --run-mode "$MODE" "$@" \
    || return 1
  local caps_tmp="$work/.capabilities.json.tmp"
  PYTHONUTF8=1 "$PY" "$REPO_ROOT/scripts/capabilities_gate.py" "$work/ndjson" --require key --json > "$caps_tmp" || return 1
  mv "$caps_tmp" "$work/capabilities.json" || return 1
  echo "Step 0 OK: capabilities gate passed (seed $seed)"
}

if [ "$MODE" = selftest ]; then
  selftest "${REPLAY_ARGS[@]}"
  exit 0
fi

if [ "$MODE" = mutants ]; then
  rm -rf "$ST_TMP"
  "$PY" selftest.py "$EXP_DIR/config.json" "$ST_TMP" --hmm-version "$HMM_VERSION" --mutants
  rm -rf "$ST_TMP"
  exit 0
fi

require_prev "$STEP"

if [ "$MODE" = apply-pilot ]; then
  cd "$EXP_DIR"
  "$PY" scripts/person.py --apply-pilot config.json --step "$STEP" --what all
  exit 0
fi

# the instruments must be committed before a main run (provenance records the commit; design 6); the smoke only warns
if [ "$MODE" = main ] || [ "$MODE" = smoke ]; then
  DIRTY="$(git -C "$EXP_DIR" status --porcelain -- . ':(exclude)results' 2>/dev/null || echo unknown)"
  if [ -n "$DIRTY" ]; then
    if [ "$MODE" = main ]; then
      echo "the experiment directory has uncommitted changes (or git failed): commit before --main:" >&2
      echo "$DIRTY" | head -5 >&2
      exit 2
    fi
    echo "WARNING: the experiment directory has uncommitted changes (the smoke goes on)" >&2
  fi
fi

SEED_OFF_KEY=""
case "$MODE" in
  ceiling) SEED_OFF_KEY="ceiling" ;; pilot-k) SEED_OFF_KEY="kgrid" ;; pilot) SEED_OFF_KEY="pilot" ;;
  smoke) SEED_OFF_KEY="smoke" ;; main) SEED_OFF_KEY="main" ;;
esac
OFFSET="$(cfg "c['person']['seed_offsets']['$SEED_OFF_KEY']")"
SEED_RUN=$(( 10#$BASE_SEED + 10#$OFFSET ))  # 10#: never octal
SUFFIX="$STEP/$MODE"
[ "$MODE" = smoke ] && SUFFIX="$STEP/main-smoke"
FLAT="${SUFFIX//\//-}"
WORK="$EXP_DIR/work-$FLAT"
OUT="$EXP_DIR/results/.partial-$FLAT"
rm -rf "$WORK" "$OUT"
mkdir -p "$OUT"

if [ "$MODE" = pilot-k ]; then
  selftest
  echo "$SEED_RUN" > "$OUT/SEED.run"
  "$PY" person.py --pilot-k "$EXP_DIR/config.json" "$OUT/SEED.run" "$OUT" --step "$STEP" --jobs "$JOBS"
  rm -f "$OUT/SEED.run"
  GSE_REPLAY="" provenance "$OUT/provenance.json" "$SEED_RUN" "$STEP"
  publish "$SUFFIX"
  echo "done: $EXP_DIR/results/$SUFFIX (then: bash run.sh --apply-pilot --step $STEP)"
  exit 0
fi

WORLD_ARGS="$(step_args "$STEP")"
[ -n "$WORLD_ARGS" ] || { echo "unknown step $STEP" >&2; exit 2; }
case "$MODE" in
  ceiling) selftest; generate "$SEED_RUN" "$WORK"
           "$PY" person.py --ceiling "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" "$OUT" --step "$STEP" --jobs "$JOBS"
           mv "$WORK/capabilities.json" "$OUT/capabilities.json" ;;
  pilot|smoke|main)
    SMOKE_ARG=()
    [ "$MODE" = smoke ] && SMOKE_ARG=(--smoke)
    selftest "${REPLAY_ARGS[@]}"
    generate "$SEED_RUN" "$WORK" "${SMOKE_ARG[@]}"
    "$PY" replay_all.py "$GSE_REPLAY" "$WORK" --jobs "$JOBS"
    mv "$WORK/capabilities.json" "$OUT/capabilities.json"
    if [ "$MODE" = pilot ]; then
      "$PY" person.py --pilot "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" "$OUT" --step "$STEP" --jobs "$JOBS"
    else
      "$PY" person.py --run "$EXP_DIR/config.json" "$WORK/SEED.run" "$WORK" "$OUT" --step "$STEP" --jobs "$JOBS" "${SMOKE_ARG[@]}"
    fi ;;
esac
provenance "$OUT/provenance.json" "$SEED_RUN" "$STEP"
publish "$SUFFIX"
echo "done: $EXP_DIR/results/$SUFFIX"
rm -rf "$WORK"
if [ "$MODE" = main ]; then  # design 3.7: the wiring on the run's own columns (the results are kept either way)
  "$PY" person.py --wiring "$EXP_DIR/results/$SUFFIX/summary.json" "$EXP_DIR/config.json" || {
    echo "=== MAIN RUN OF $STEP: the wiring check failed; tell the researcher and do not go on (design 3.7) ===" >&2; exit 3; }
fi
if [ "$MODE" = pilot ]; then
  echo "next: bash run.sh --apply-pilot --step $STEP (writes pc_person.lam and pc_pers.lam), commit config.json, then --smoke"
fi
