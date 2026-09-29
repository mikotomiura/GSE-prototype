# kit/e3 provenance (internal; not published)

`*.internal.*` is dropped by the public export and is outside `_style_check.py`. This file records where the
files of `kit/e3/` come from. The public `README.md` does not say so.

## Copies (issue 023, decision 60 / 61)

Both are copies of the samplers of the earlier run-time cost experiment, kept under `experiments/`. The
executable lines are the same as the original. Differences:

1. The process name. The original names it as a constant (`gse-next`); the copy reads the environment
   variable `E3_PROC` (default `ime-observation-logger`).
2. All comment lines (`#`) were translated into academic English and reworded so that they carry no
   project name, no mark characters and no reference to files that do not exist under `kit/`
   (decision 60: the original comments are Japanese and mention the project, which conflicts with decision 36).

| Copy | Original | SHA-256 of the original | Changed executable lines |
|---|---|---|---|
| `sample-macos.sh` | `experiments/20260903-o1-runtime-cost/scripts/sample-macos.sh` | `244f79c34af93c4cd89bfe90c40a2fadeb1e4fcf73abbbc8e0f1f1389ce62f31` | `pgrep -x 'gse-next'` becomes `pgrep -x "${E3_PROC}"`; one line added: `E3_PROC="${E3_PROC:-ime-observation-logger}"` |
| `sample-windows.sh` | `experiments/20260903-o1-runtime-cost/scripts/sample-windows.sh` | `a8f1ab2f078d9bd21c5c9a464f804eef13d8673318b88c6568d1664505a0589b` | `Get-Process -Name "gse-next"` becomes `Get-Process -Name $env:E3_PROC`; one line added: `E3_PROC="${E3_PROC:-ime-observation-logger}"; export E3_PROC` |

`023-acceptance.sh` (AC 2) checks this mechanically: with comment lines and blank lines removed, every added
line contains `E3_PROC` and every removed line is the process-name line.

## Rewritten, not copied

- `calibrate-cpu.sh` was written again in English (decision 60). Original:
  `experiments/20260903-o1-runtime-cost/scripts/calibrate-cpu.sh`, SHA-256
  `a44cd1e900b11ed812726759c673a40120098b952ad2c52b2b73f03e113b96b1`. The way of measuring is the same
  (a busy loop saturates one core; ground truth = increase of `ps -o cputime` over wall-clock time; the readings
  of `ps -o %cpu` and `top -l 2/3/4` are printed next to it; the reading for the absent process is the negative
  control). Not changed: it prints values for a person to compare and adds no automatic verdict. Added: it
  exits 2 on a system other than macOS, because it depends on `top -l` and `ps -o cputime`.
- `summarize_e3.py` re-implements `experiments/20260903-o1-runtime-cost/scripts/summarize.py` (SHA-256
  `0756b023f71d33b0d3dbd8982950cdbeca9b56d144e8ff568821869926b7f919`) for the parts E3 needs. Formulas
  taken from it unchanged: the CPU mean over the rows in which the process is present with empty CPU values
  left out; the least-squares slope of the resident memory in MB/h over the rows with a positive resident
  size; the `31/1` thread form; skipped lines counted; rows with the process absent (all columns zero) left out;
  the floor of 480 rows. Confirmed on 2026-09-30 from the original: it does not multiply any calibration value into the
  result (`calibrate-cpu.sh` is a manual check).
  Added here: median, 95th percentile (linear interpolation) and maximum; per-condition blocks; the status
  `not measured` / `insufficient` / `measured` and exit codes. Not taken: thresholds and verdicts of the
  original table, the NDJSON size, the energy report, the start-up report and the battery.
- `run_e3.sh` and `README.md` are new. `run_e3.sh` replaces `run.sh` of the original for one condition (it
  writes the same 8-column header and calls the sampler).

## Not verified here

- The process-name match of `pgrep -x` on macOS for a 22-character name (`ime-observation-logger`) was not
  checked on a Mac. If macOS compares only a truncated name, the sampler reports the process as absent and the
  summary says `not measured`; the fix would be `pgrep -f` or a shorter binary name, which goes beyond the
  process-name line (decision 12) and must be reported. `run_e3.sh` prints a note at the start when it does
  not find the process. Check it at the start of the measurement.
- `calibrate-cpu.sh` and the macOS sampler were not run on a Mac in this issue (the loop ran on Windows).
  The Windows sampler and `run_e3.sh` were run against an absent process only (all rows zero, `not measured`).
