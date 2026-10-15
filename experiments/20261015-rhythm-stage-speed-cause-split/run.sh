#!/usr/bin/env bash
# Cause split of the red res=sub candidates of the confound world (synthetic traces only, no participants).
# Design: .steering/20261015-rhythm-stage-speed-cause-split/design.md
#
# Usage: bash run.sh --selftest
#        GSE_REPLAY=<gse-replay.exe> bash run.sh --smoke --step <c100|c200> [--jobs N]
#        GSE_REPLAY=<gse-replay.exe> bash run.sh --main  --step <c100|c200> [--jobs N]
#   --selftest  scripts/selftest_split.py (design 3.6)
#   --smoke     SEED + sets.smoke_seed_offset, sets.smoke_P sessions, bootstrap smoke_bootstrap, no gate
#   --main      SEED, sets.P sessions: the rows of the confound world's main run, the gate against its e13.json
#               (design 1.5), then (a) and (b)
#   --jobs      parallel workers (default 8). The results do not depend on it.
# The rows are made with the confound world's instrument where it is (design 1.1): its gen_sessions.py with its
# config.json and the arguments of its run.sh prepare (--world confound --c <c> --smoke --p-n <P>), the capabilities
# gate and its replay_all.py. The work directory (work-*/, git-ignored) is removed at the end; only the JSON of
# results/<step>/<mode>/ is committed (the smoke's is git-ignored).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREV_DIR="$EXP_DIR/../20261014-rhythm-stage-speed-confound-world"
MODE=""
JOBS=8
STEP=""
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest|--smoke|--main)
      [ -z "$MODE" ] || { echo "one mode only" >&2; exit 2; }; MODE="${1#--}"; shift ;;
    --jobs) JOBS="$2"; shift 2 ;;
    --step) STEP="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$MODE" ] || { echo "a mode is required: --selftest, --smoke or --main" >&2; exit 2; }
case "$JOBS" in ''|*[!0-9]*) echo "--jobs must be a positive integer" >&2; exit 2 ;; esac
[ "$JOBS" -ge 1 ] || { echo "--jobs must be a positive integer" >&2; exit 2; }
case "$MODE" in
  smoke|main) case "$STEP" in c100|c200) ;; *) echo "--$MODE needs --step c100 or c200" >&2; exit 2 ;; esac ;;
  *) [ -z "$STEP" ] || { echo "--step is for --smoke and --main only" >&2; exit 2; } ;;
esac

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

# jq-free reads of config.json (one value per call)
cfgv() {
  local v
  v="$("$PY" -c "import json,sys; c=json.load(open(sys.argv[1],encoding='utf-8')); print(eval(sys.argv[2]))" "$2" "$1")"
  echo "${v%$'\r'}"
}

cd "$EXP_DIR/scripts"
if [ "$MODE" = selftest ]; then
  "$PY" selftest_split.py "$EXP_DIR/config.json"
  exit $?
fi

# design 1.1: the confound world's instrument is the one config.json pins
"$PY" split.py "$EXP_DIR/config.json" --check-prev

HMM_VERSION="$(grep -m1 'pub const HMM_VERSION' "$REPO_ROOT/src-tauri/src/analysis/engine.rs" | sed -E 's/.*"([^"]+)".*/\1/')"
WANT_HMM="$(cfgv "c['prev']['hmm_version']" "$EXP_DIR/config.json")"
[ "$HMM_VERSION" = "$WANT_HMM" ] || { echo "HMM_VERSION $HMM_VERSION is not $WANT_HMM (design 1.1)" >&2; exit 2; }

[ -n "${GSE_REPLAY:-}" ] || { echo "GSE_REPLAY is required (design 1.1)" >&2; exit 2; }
if [ ! -f "$GSE_REPLAY" ] && [ -f "$GSE_REPLAY.exe" ]; then GSE_REPLAY="$GSE_REPLAY.exe"; fi
[ -f "$GSE_REPLAY" ] || { echo "gse-replay not found: $GSE_REPLAY" >&2; exit 2; }
REPLAY_SHA="$(sha256sum "$GSE_REPLAY" | cut -d' ' -f1)"
WANT_SHA="$(cfgv "c['prev']['gse_replay_sha256']" "$EXP_DIR/config.json")"
[ "$REPLAY_SHA" = "$WANT_SHA" ] || { echo "gse-replay SHA-256 $REPLAY_SHA is not $WANT_SHA (design 1.1)" >&2; exit 2; }

# design 3.6: the selftest passes before every run
"$PY" selftest_split.py "$EXP_DIR/config.json"

BASE_SEED="$(tr -d '[:space:]' < "$EXP_DIR/SEED")"
case "$BASE_SEED" in ''|*[!0-9]*) echo "SEED must be a non-negative integer" >&2; exit 2 ;; esac
if [ "$MODE" = smoke ]; then
  SEED_RUN=$(( 10#$BASE_SEED + $(cfgv "c['sets']['smoke_seed_offset']" "$EXP_DIR/config.json") ))
  P_N="$(cfgv "c['sets']['smoke_P']" "$EXP_DIR/config.json")"
  SMOKE_ARG=(--smoke)
else
  SEED_RUN=$(( 10#$BASE_SEED ))
  P_N="$(cfgv "c['sets']['P']" "$EXP_DIR/config.json")"
  SMOKE_ARG=()
fi
C="$(cfgv "c['ceiling']['steps']['$STEP']" "$PREV_DIR/config.json")"
WORK="$EXP_DIR/work-$STEP-$MODE"
OUT="$EXP_DIR/results/.partial-$STEP-$MODE"
DEST="$EXP_DIR/results/$STEP/$MODE"
rm -rf "$WORK" "$OUT"
mkdir -p "$WORK" "$OUT"
echo "$SEED_RUN" > "$WORK/SEED.run"

# the confound world's prepare (its run.sh), from its scripts/
(
  cd "$PREV_DIR/scripts"
  "$PY" gen_sessions.py "$PREV_DIR/config.json" "$WORK/SEED.run" "$WORK" --hmm-version "$HMM_VERSION" \
    --world confound --c "$C" --smoke --p-n "$P_N"
  PYTHONUTF8=1 "$PY" "$REPO_ROOT/scripts/capabilities_gate.py" "$WORK/ndjson" --require key --json > "$OUT/capabilities.json"
  echo "Step 0 OK: capabilities gate passed (seed $SEED_RUN)"
  "$PY" replay_all.py "$GSE_REPLAY" "$WORK" --jobs "$JOBS"
)

set +e
"$PY" split.py "$EXP_DIR/config.json" "$WORK" "$OUT" --step "$STEP" --seed "$SEED_RUN" --jobs "$JOBS" \
  --replay-sha "$REPLAY_SHA" "${SMOKE_ARG[@]}"
RC=$?
set -e
rm -rf "$DEST"
mkdir -p "$(dirname "$DEST")"
mv "$OUT" "$DEST"
rm -rf "$WORK"
if [ "$RC" -ne 0 ]; then
  echo "split.py exited $RC; what it wrote is in $DEST" >&2
  exit "$RC"
fi
echo "done: $DEST"
