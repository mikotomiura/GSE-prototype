#!/usr/bin/env bash
# Rhythm stage desk check: synthetic traces only, no participants.
# Design: .steering/20261012-rhythm-stage-desk-check/design.md (sections 1-3 and 9 committed before pilot 0).
#
# Usage: bash run.sh (--selftest | --ceiling) [--jobs N]
#   --selftest  design 3.7 (the tests pilot 0 needs): the world (v1 and v2 equal EH1 round 5's generator, v3 is v2
#               with the declared changes), the speed quantities, model A_speed, the AUC and the choice rule.
#   --ceiling   design 3.0 (pilot 0, before the freeze): the self-tests, then SEED + ceiling.seed_offset,
#               ceiling.P P sessions of each world in ceiling.prefer (the other sets at the smoke size, unused),
#               AUC(A) and AUC(A_speed) per label and classifier, and the chosen world. No gse-replay, no stage
#               candidate, no positive control. Writes results/ceiling/ (committed). Append the values and the
#               chosen world to the end of design 3.0 and commit: that commit is the freeze.
#   --jobs      parallel workers (default 8). The results do not depend on it.
#
# Environment:
#   PYTHON  python with requirements.txt installed (default: .venv next to this file)
#
# The generated NDJSON and labels stay in work-*/ (git-ignored). Only the aggregated JSON is committed.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EH1_DIR="$EXP_DIR/../20261010-portrait-eh1-round5"
MODE=""
JOBS=8
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) [ -z "$MODE" ] || { echo "one mode only" >&2; exit 2; }; MODE="selftest"; shift ;;
    --ceiling) [ -z "$MODE" ] || { echo "one mode only" >&2; exit 2; }; MODE="ceiling"; shift ;;
    --jobs) JOBS="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$MODE" ] || { echo "a mode is required: --selftest or --ceiling" >&2; exit 2; }
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
rm -rf "$ST_TMP"
"$PY" selftest.py "$EXP_DIR/config.json" "$EH1_DIR" "$ST_TMP" --hmm-version "$HMM_VERSION"
rm -rf "$ST_TMP"
if [ "$MODE" = selftest ]; then exit 0; fi

# --ceiling. Results go to a partial directory that replaces results/ceiling only when every step has passed.
SUFFIX="ceiling"
FINAL_OUT="$EXP_DIR/results/$SUFFIX"
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

# provenance (design 3.8)
"$PY" - "$OUT/provenance.json" "$HMM_VERSION" "$EXP_DIR" "$JOBS" "$SEED_RUN" "$WORLDS" <<'PYEOF'
import hashlib, json, os, platform, subprocess, sys
from importlib.metadata import version
out, hmm, exp_dir, jobs, seed, worlds = sys.argv[1:7]
commit = subprocess.run(["git", "-C", exp_dir, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
r = subprocess.run(["git", "-C", exp_dir, "status", "--porcelain", "--", ".", ":(exclude)results"],
                   capture_output=True, text=True)
dirty = bool(r.stdout.strip()) if r.returncode == 0 else None  # None when git itself fails
cfg_sha = hashlib.sha256(open(os.path.join(exp_dir, "config.json"), "rb").read()).hexdigest()
json.dump({"mode": "ceiling", "git_commit": commit, "experiment_dir_dirty": dirty, "config_sha256": cfg_sha,
           "hmm_version_in_meta": hmm, "gse_replay": None, "seed": int(seed), "worlds": worlds.split(),
           "python": platform.python_version(), "platform": platform.platform(), "cpu_count": os.cpu_count(),
           "jobs": int(jobs),
           "packages": {p: version(p) for p in ("numpy", "scipy", "scikit-learn", "threadpoolctl")}},
          open(out, "w", encoding="utf-8", newline="\n"), indent=1)
PYEOF

old="$EXP_DIR/results/.old-$SUFFIX"
rm -rf "$old"
if [ -e "$FINAL_OUT" ]; then mv "$FINAL_OUT" "$old"; fi
mv -T "$OUT" "$FINAL_OUT"
rm -rf "$old"
for W in $WORLDS; do rm -rf "$EXP_DIR/work-ceiling-$W"; done
echo "done: $FINAL_OUT/ceiling.json (append the values and the chosen world to the end of design 3.0, then commit)"
