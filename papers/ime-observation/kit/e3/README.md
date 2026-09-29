# Execution cost of the standalone observer (E3)

This directory measures what the standalone observer (`ime-observation-logger`) costs the machine while it
runs: CPU and resident memory of that one process, under two conditions.

| Condition | What happens during the run |
|---|---|
| `idle` | The observer runs and nothing operates the machine. |
| `working` | The observer runs while the scenario emitter types a synthetic plan (`../run/run_cell.py`). |

The cost is reported for both conditions. It is never reduced to a single figure such as "the observer uses
N % CPU": an observer that is cheap when idle and expensive while typing, or the other way round, would hide
behind one number.

## Files

| File | Purpose |
|---|---|
| `run_e3.sh` | Samples the observer for one condition and writes `samples.tsv` and `conditions.txt`. |
| `sample-macos.sh`, `sample-windows.sh` | The sampler of each system, called by `run_e3.sh`. |
| `summarize_e3.py` | Summarises `samples.tsv` per condition (`--selftest` runs its negative controls). |
| `calibrate-cpu.sh` | A manual positive and negative control of the macOS CPU instrument. |

## What is measured

The samplers record one row every interval and nothing else about the machine: the process is found by its
name (`E3_PROC`, default `ime-observation-logger`, without `.exe` on Windows) and no other process is
listed and no window title is read.

| Column | macOS | Windows |
|---|---|---|
| CPU (%) | increase of the cumulative CPU time (`ps -o cputime`) divided by the increase of the wall-clock time | the performance counter `\Process(<name>)\% Processor Time` |
| Resident memory (KB) | the `mem` column of `top -l 3` | working set |
| Threads | the `th` column of `top -l 3` | thread count |

- CPU is on the basis one core = 100 %, on both systems. A machine with ten cores has a maximum of 1000 %.
- On macOS the CPU figure comes from a cumulative counter, so a burst shorter than the interval is not
  missed. `top -l 2` is not used for CPU: its second frame includes the start-up time of `top` and reads
  about 0.48 times the true load. `calibrate-cpu.sh` shows this for yourself: it saturates one core and prints
  the ground truth next to what each instrument reports, then prints what `top` reports for an absent process
  (empty or 0 is correct). Run it once on a new machine, before the measurement. It uses one core at full load
  for about 15 seconds and its output is not read by the summary.
- Resident memory and threads are read at the sampling instant, so a peak shorter than the interval is not
  seen in them.
- The `power` and reference columns of the macOS sampler (the energy impact) are recorded but not
  summarised: the energy impact is a dimensionless index, not watts, and Windows has no per-process
  counterpart.
- The first row of a run has an empty CPU value (there is no previous counter). The summary leaves it out;
  it is not read as 0.
- Rows taken while the process is absent carry zero in every column. The summary leaves them out and reports
  how many there were. A file in which every row is zero is reported as `not measured`, never as a low cost.

## Battery is not measured

The machine runs on mains power during the measurement, and on mains power the battery level does not fall
(it may even rise), so a discharge cannot be read and a control without the observer would add nothing: every
column of the observed process is zero when the process is not there. The battery column of the samplers
is kept only so that the layout is the same on both systems; the summary does not read it.

## Procedure

Run every step on each system (macOS and Windows), on mains power, with sleep, the screen lock and the
screen saver turned off.

1. Build the observer (see `../logger/README.md`) and run `calibrate-cpu.sh` once (macOS).
2. `idle`: start the observer, then

   ```
   bash run_e3.sh idle 14400 30 runs/e3-idle
   ```

   and leave the keyboard and the pointer alone. Four hours at a 30-second interval gives 480 rows.
3. `working`: start the sampler first,

   ```
   bash run_e3.sh working 14400 30 runs/e3-working
   ```

   then, in another terminal, start the cell runner that starts the observer and types the plan (see
   `../run/README.md`; `run_e3.sh` prints the command and never types itself). The cell file must name the
   observer, not a wrapper script, so that the sampled process is the observer. If the plan is shorter than
   the run, repeat it or pick a longer plan: the working condition should cover the whole window.
4. Summarise both conditions together:

   ```
   python3 summarize_e3.py idle=runs/e3-idle/samples.tsv working=runs/e3-working/samples.tsv
   ```

The output directory must not exist: an earlier measurement is never overwritten. A window shorter than
480 usable rows (`--min-samples`) is reported as `insufficient`: a short window cannot stand for a rate
such as the growth of the resident memory.

## The summary

For each condition `summarize_e3.py` prints the mean, median, 95th percentile and maximum of the CPU, the
final resident memory, and the least-squares slope of the resident memory in MB per hour. The status is one of
`measured`, `insufficient` and `not measured`; only `measured` may be quoted. Exit status: 0 when every
file is measured, 1 otherwise, 2 for a usage error.

`python3 summarize_e3.py --selftest` checks the arithmetic on known series (a CPU time that rises by 0.02
seconds every second gives 2.0 %; the values 1 to 100 give a mean of 50.5 and a 95th percentile of 95.05;
a growth of 10 MB per hour gives a slope of 10) and the negative controls: a file with no rows, a file in
which every row is zero, a file without a CPU value and a short run are each reported as not measured or
insufficient.

If the observer has a longer process name than the system compares (some systems compare only the first
characters of a name), the sampler finds nothing and the summary says `not measured`; check the name with
`pgrep -x` (macOS) or `Get-Process` (Windows) before a long run. `run_e3.sh` prints a note when it does
not find the process at its start.
