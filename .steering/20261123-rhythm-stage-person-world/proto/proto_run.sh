#!/usr/bin/env bash
# Throwaway prototype (design flow: time the stages; the values are never used for any design decision).
# Usage: bash proto_run.sh <log dir outside the repo, e.g. the session scratchpad> [jobs, default 12]
# Copies the experiment to experiments/zz-proto-person-world (untracked; never commit it; delete it afterwards),
# sets SEED 4000, relaxes the two gates a copy outside git cannot pass (proto_patch.py), then runs m049 through
# ceiling, pilot, apply-pilot, smoke and main, writing one line per stage to <log dir>/proto_times.log.
set -u
S="${1:?log dir}"
JOBS="${2:-12}"
WT="C:/wt/rhythm-stage-person-world"
HERE="$WT/.steering/20261123-rhythm-stage-person-world/proto"
P="$WT/experiments/zz-proto-person-world"
mkdir -p "$S"
rm -rf "$P"
cp -r "$WT/experiments/20261123-rhythm-stage-person-world" "$P"
rm -rf "$P/work-"* "$P/results"
echo 4000 > "$P/SEED"
python "$HERE/proto_patch.py" "$P" || exit 1
export PYTHON=C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python
export GSE_REPLAY=C:/wt/_target-portrait-eh1/release/gse-replay.exe
cd "$P" || exit 1
log="$S/proto_times.log"; : > "$log"
echo "jobs=$JOBS" >> "$log"
for mode in ceiling pilot apply-pilot smoke main; do
  t0=$(date +%s)
  bash run.sh --$mode --step m049 --jobs "$JOBS" > "$S/proto_$mode.log" 2>&1
  rc=$?
  echo "$mode rc=$rc secs=$(( $(date +%s) - t0 ))" >> "$log"
  [ $rc -eq 0 ] || exit $rc
done
echo ALLDONE >> "$log"
