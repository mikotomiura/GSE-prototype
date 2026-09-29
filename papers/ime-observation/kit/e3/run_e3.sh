#!/usr/bin/env bash
# Run one condition of the execution-cost measurement (E3): sample the standalone observer for a fixed time.
#
#   bash run_e3.sh <idle|working> <duration_s> <interval_s> <out_dir>
#
#   idle      Nothing operates the machine while the observer runs.
#   working   Synthetic typing is played meanwhile. This script does not type: it prints the command of the
#             cell runner, and the person who measures starts it in another terminal.
#
# The observer is started by the person who measures (or, for the working condition, by the cell runner);
# this script only samples the process named by E3_PROC (default: ime-observation-logger; on Windows without
# the .exe suffix). Rows taken while the process is absent carry zero in every column and are left out by the
# summary, so the sampler may be started first.
#
# Output (out_dir must not exist): samples.tsv (a header and one row per sample) and conditions.txt.
# Then:  python3 summarize_e3.py idle=<idle dir>/samples.tsv working=<working dir>/samples.tsv
#
# Battery is not measured: the machine runs on mains power and a discharge cannot be read. The battery
# column of the sampler is kept only so that the layout stays the same on both systems.
#
# Must run under bash 3.2 (the macOS default): always brace variables as ${VAR}; no arrays or mapfile.
set -eu

HERE="$(cd "$(dirname "$0")" && pwd)"
KIT="$(cd "${HERE}/.." && pwd)"

usage () {
  echo "usage: bash run_e3.sh <idle|working> <duration_s> <interval_s> <out_dir>" >&2
  exit 2
}
[ $# -eq 4 ] || usage
COND="$1"; DURATION_S="$2"; INTERVAL_S="$3"; OUT="$4"
case "${COND}" in idle|working) ;; *) usage ;; esac
case "${DURATION_S}" in ''|*[!0-9]*) usage ;; esac
case "${INTERVAL_S}" in ''|*[!0-9]*) usage ;; esac
[ "${DURATION_S}" -gt 0 ] && [ "${INTERVAL_S}" -gt 0 ] || usage

E3_PROC="${E3_PROC:-ime-observation-logger}"; export E3_PROC

case "$(uname -s)" in
  Darwin) OS=macos ;;
  MINGW*|MSYS*|CYGWIN*) OS=windows ;;
  *) echo "run_e3.sh: unsupported system: $(uname -s) (macOS and Windows only)" >&2; exit 2 ;;
esac

if [ -e "${OUT}" ]; then
  echo "run_e3.sh: ${OUT} already exists; an earlier measurement is never overwritten" >&2
  exit 3
fi

proc_present () {
  if [ "${OS}" = "macos" ]; then
    pgrep -x "${E3_PROC}" >/dev/null 2>&1
  else
    powershell.exe -NoProfile -NonInteractive -Command "if (Get-Process -Name \"${E3_PROC}\" -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >/dev/null 2>&1
  fi
}

# A short window cannot represent a rate: warn before the run, not after it.
ROWS=$(( DURATION_S / INTERVAL_S ))
if [ "${ROWS}" -lt 480 ]; then
  echo "note: about ${ROWS} rows; fewer than 480 usable rows are reported as insufficient by the summary" >&2
fi
if proc_present; then
  echo "observer process found: ${E3_PROC}"
else
  echo "note: no process named ${E3_PROC} is running yet; rows are written as absent until it appears" >&2
fi

if [ "${COND}" = "working" ]; then
  echo "working condition: start the typing in another terminal, after this sampler has started:"
  echo "  python3 \"${KIT}/run/run_cell.py\" --cell <CELL.json> --plan <PLAN.jsonl> --run-dir <RUN_DIR>"
  echo "  (add the send-consent flag described in run/README.md; this script never types)"
else
  echo "idle condition: leave the keyboard and the pointer alone for the whole run"
fi

mkdir -p "${OUT}"
printf 'epoch_s\tcpu_pct\trss_kb\tthreads\tbattery_pct\trss_alt_kb\tenergy_impact\tref_energy_impact\n' > "${OUT}/samples.tsv"
{
  echo "condition=${COND}"
  echo "os=${OS}"
  echo "process=${E3_PROC}"
  echo "duration_s=${DURATION_S}"
  echo "interval_s=${INTERVAL_S}"
  echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${OUT}/conditions.txt"

bash "${HERE}/sample-${OS}.sh" "${DURATION_S}" "${INTERVAL_S}" >> "${OUT}/samples.tsv"

echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${OUT}/conditions.txt"
echo "done. next: python3 \"${HERE}/summarize_e3.py\" ${COND}=\"${OUT}/samples.tsv\""
