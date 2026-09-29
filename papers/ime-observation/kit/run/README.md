# Cell runner

`run_cell.py` measures one cell (operating system x input method x settings) with one command. It starts the
standalone observer and the reference input field as child processes, resets the input method at the start of
each block that asks for it, brings the reference input field to the front, plays a plan through the scenario
emitter (`../emit/emit.py`), stops the children, and leaves everything in one run directory. The runner uses
only the Python standard library.

## Usage

```
python3 run_cell.py --cell CELL.json --plan PLAN.jsonl --run-dir runs/<name>
python3 run_cell.py --cell CELL.json --plan PLAN.jsonl --run-dir runs/<name> --i-understand-this-sends-keys
python3 run_cell.py --selftest
```

- The run directory must not exist; it is created by the runner and an existing one is never reused or
  changed. Run directories are ignored by git (`runs/`).
- A backend other than `dryrun` sends real key events to the application in front, and the runner refuses to
  start (exit status 2) without `--i-understand-this-sends-keys`. The flag check, the check of the cell file and
  the plan, and the check that the run directory does not exist all come before the first child process is
  started.
- Exit status: 0 the run completed; 1 the run was aborted (or the manifest could not be written); 2 the run was
  refused or could not start.

## Before a measurement

Check these by hand; the runner records the statements in the cell file and cannot verify them.

1. Time synchronisation is off for the duration of the run (`clock_sync_disabled`), so the wall clock does not
   step. Automatic updates of the operating system and of the input method are off (`auto_update_disabled`).
2. The operating system version and the input method's name and version are written into `ime` (they are copied
   into the manifest).
3. Nothing else is in front of the reference input field, and nobody touches the keyboard or the pointer while a
   real backend is sending: synthetic keys go to whatever application is in front.
4. On macOS the terminal application that runs the runner holds the Accessibility permission.
5. `reset_cmd` really clears the input method's dictionary and learning, and `focus_cmd` really brings the
   reference input field to the front. Both differ by system and input method and are checked in a calibration
   pilot; `cell.example.json` gives placeholders only.

## The cell file

A JSON object. Unknown keys and missing keys are refused.

| Key | Meaning |
|---|---|
| `os` | `macos` or `windows`; must equal the plan's `os` |
| `ime` | name and version of the input method (a string) |
| `ime_settings` | the settings of the input method for this cell (an object; copied into the manifest) |
| `refinput_cmd` | argument array that starts the reference input field; `{out}` is replaced by the path of its log |
| `logger_cmd` | argument array that starts the observer; `{out}` is replaced by the path of its log |
| `reset_cmd` | argument array run before each block whose plan row has `reset_ime` true; empty means no reset |
| `focus_cmd` | argument array run before each block; empty means nothing is run |
| `ready_wait_ms` | how long to wait after starting the children before the first block |
| `backend` | `dryrun`, `macos`, or `windows` |
| `clock_sync_disabled`, `auto_update_disabled` | statements by the person who prepared the machine |
| `backend_opts` | optional; options passed to the backend (for example the application to bring to the front) |
| `stop_wait_ms` | optional, default 5000; how long a child has to end after the termination request |
| `settle_ms` | optional, default 0; a wait after the last block, before the children are stopped |
| `command_timeout_ms` | optional, default 60000; the limit for `reset_cmd` and `focus_cmd` |

Commands are run without a shell, with standard input closed and standard output discarded.

## Sequence

1. The plan and the cell are read and checked; a real backend is loaded and checked against the plan's keys.
2. The run directory is created and the plan is copied into it.
3. The observer and then the reference input field are started; the runner waits `ready_wait_ms`.
4. For each block: `reset_cmd` (if the block asks for it) with its exit status written to the oracle as a
   `reset` row, then `focus_cmd`, then the block is played. A focus command that exits with a non-zero status
   or times out aborts the run, because the keys would go to the wrong window. A reset command that cannot
   start or times out is recorded with exit status -1 and the run continues (the analysis decides what to
   exclude).
5. Both children are asked to end (`SIGTERM`; on Windows `terminate`). A child that is still running after
   `stop_wait_ms` is killed. The manifest records, for each child, its exit status and whether it had already
   exited, was terminated, or was killed.

If a child exits while the run is in progress, no further key is pressed (a key already held is released), the
other child is stopped, and the manifest says `aborted` with the reason. A run in which a child wrote no output
is aborted too.

## The run directory

| File | Content |
|---|---|
| `plan.jsonl` | a byte-for-byte copy of the plan that was played |
| `oracle.jsonl` | what the emitter sent and when (`oracle/1`, including the `reset` rows) |
| `gt.jsonl` | the reference input field's log (`gt/1`) |
| `obs.jsonl` | the observer's log (`obs/1`) |
| `run.json` | the manifest (`run/1`), below |
| `logger.stderr.txt`, `refinput.stderr.txt` | what each child wrote to standard error |

`run.json` holds: `cell` (as given, with the optional keys filled in), `plan_sha256`, `git_commit` (the
commit of the checkout that holds the runner, or `null`), `started` and `ended` (`wall_ms`, and `mono_ns` from
the same clock as the `t_mono_ns` of the oracle rows), `outputs` (`file`, `sha256`, and `lines` of each of the
four logs; `null` for a log that is absent or empty), `children` (`exit_code`, `stopped`, `stderr_file`),
`resets`, `focus_exit_codes`, `aborted`, and `abort_reason`.

The `gt` and `obs` logs use the clocks of their own processes, so their times are aligned to the oracle in
the analysis, not by the runner.
