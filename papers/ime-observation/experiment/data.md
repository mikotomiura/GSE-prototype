# Data

The raw run directories are never committed to git. Each one is deposited in a data repository and is
recorded here with the SHA-256 of its deposited archive.

## Run directories used by `run.sh`

`run.sh` reads the lines of the form `- run_dir: PATH  manifest_sha256: HEX` below (a relative path is relative
to this file; `HEX` is the SHA-256 of that run directory's `run.json`, 64 lowercase hexadecimal digits). The
analysis stops when the hash is missing or differs. Lines inside HTML comments and code fences are not read.
Add one line per run directory after the data has been retrieved from the deposit and unpacked. Runs whose
manifest says `aborted` are left out by the pipeline and are counted in the results. The labels that were
used are printed when the analysis ends.

<!-- - run_dir: /path/to/an/unpacked/run-directory  manifest_sha256: 0000000000000000000000000000000000000000000000000000000000000000 -->

## Deposits

| Cell label | Deposit location | SHA-256 of the archive | Date deposited |
|---|---|---|---|
| (to be filled in) | (to be filled in) | (to be filled in) | (to be filled in) |

## Deposit procedure

1. Deposit only `run.json` and the four logs of a run directory: `plan.jsonl`, `oracle.jsonl`,
   `gt.jsonl` and `obs.jsonl`. A log that an aborted run recorded with a null hash need not exist.
2. Do not deposit the `*.stderr.txt` files or `runner.error.txt`. They stay on the measuring machine.
3. On the measuring machine, bundle the files with
   `python3 kit/analysis/pipeline.py --pack <run-dir> --out <archive.zip> [--also-user NAME ...] [--also-home PATH ...]`.
   Pass the login name and the home directory of the measuring machine with `--also-user` and `--also-home`
   (each may be given more than once). The command refuses, with exit status 1 and without writing the
   archive, a run in which any of the five files contains an absolute path (a drive letter, a UNC path,
   `/Users/`, `/home/`, `/Volumes/`, an MSYS drive path such as `/c/`), the home directory, the repository
   path, a login name, or content in the ground-truth or observation log; it exits with status 2 when a log
   no longer matches the hash recorded in `run.json`. Only paths that begin with `~` or `<repo>`, and
   relative paths, are allowed. It never overwrites an existing archive, writes the files in a fixed order
   with fixed times so that packing twice gives the same bytes, checks the contents of the archive again,
   and prints the archive's SHA-256.
4. Record the printed SHA-256 in the table above, together with the hash of `run.json`
   (`manifest_sha256` in the line of the list above).
5. Deposit that archive, unchanged. `python3 kit/analysis/pipeline.py --check-deposit <run-dir> ...` runs the
   same check on unpacked directories without writing an archive.

## Machine that ran the deposit check

Record, for every archive, the machine on which `--pack` was run and the values that were passed. The check
finds only the values it is given (see the docstring of `pipeline.py` for what it cannot find).

| Cell label | Machine (operating system, host role) | `--also-user` values | `--also-home` values | Date checked |
|---|---|---|---|---|
| (to be filled in) | (to be filled in) | (to be filled in) | (to be filled in) | (to be filled in) |
