# Data

The raw run directories are never committed to git. Each one is deposited in a data repository and is
recorded here with the SHA-256 of its deposited archive.

## Run directories used by `run.sh`

`run.sh` reads the lines of the form `- run_dir: PATH` below (a relative path is relative to this file).
Add one line per run directory after the data has been retrieved from the deposit and unpacked. Runs whose
manifest says `aborted` are left out by the pipeline and are counted in the results.

<!-- - run_dir: /path/to/an/unpacked/run-directory -->

## Deposits

| Cell label | Deposit location | SHA-256 of the archive | Date deposited |
|---|---|---|---|
| (to be filled in) | (to be filled in) | (to be filled in) | (to be filled in) |

## Deposit procedure

1. Deposit only `run.json` and the four logs of a run directory: `plan.jsonl`, `oracle.jsonl`,
   `gt.jsonl` and `obs.jsonl`.
2. Do not deposit the `*.stderr.txt` files or `runner.error.txt`. They stay on the measuring machine.
3. Immediately before depositing, run
   `python3 kit/analysis/pipeline.py --check-deposit <run-dir> [<run-dir> ...]`
   and continue only if it exits 0. It refuses a directory in which any of the five files contains the
   absolute path of a home directory, the login name of the user, or the absolute path of the repository.
4. Record the archive's SHA-256 in the table above.
