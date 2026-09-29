# Scenario emitter

The emitter plays a `plan/1` file (see `../formats/FORMATS.md`) through a key-sending backend and writes an
`oracle/1` log: for every key it sends, the time at which it was actually sent. The oracle records what was
intended and when; it is used only to verify the observed ground truth and is never given to an observer.

| File | Role |
|---|---|
| `emit.py` | Core: timing, oracle writing, oracle validation, command line |
| `backend_dryrun.py` | Sends nothing; used to exercise the core and the timing |
| `backend_macos.py` | Posts synthetic key events through Quartz Event Services (`CGEventPost`, via `ctypes`) |
| `keymap_macos.json` | Key name to macOS virtual key code |

## Usage

```
python3 emit.py --plan PLAN --out ORACLE --backend dryrun
python3 emit.py --plan PLAN --out ORACLE --backend macos --i-understand-this-sends-keys \
    --backend-opt focus_app=<bundle id of the target application>
python3 emit.py --validate ORACLE
python3 emit.py --selftest
python3 backend_macos.py --probe
```

The output file must not exist (an existing oracle is never overwritten). The command line plays the blocks
of a plan in order and does not reset the input method between blocks; a caller that needs a reset uses the
`Emitter` class directly (`write_reset`, then `run_block`) so that the `reset` row precedes `block_begin`.

## Safety rules for real sending

- Synthetic keys are delivered to **the application that is in front**. Prepare the target window, and do not
  touch the keyboard or change the front application while a run is in progress.
- A backend other than `dryrun` refuses to start (exit status 2, no output file) unless
  `--i-understand-this-sends-keys` is given. No self-test, probe, or validation path sends a key.
- On macOS the process that runs the emitter (the terminal application) must hold the Accessibility permission.
  Without it the system drops the events silently, so the backend checks the permission on start and refuses
  to run when it is missing. The emitter never changes the permission.
- The `focus_away` and `focus_back` pseudo-keys bring another application to the front through AppleScript.
  `focus_back` requires `--backend-opt focus_app=<bundle id>`; `focus_away` uses `away_app` (default
  `com.apple.finder`).
- A plan that uses a key the backend cannot send (for example a key that only another backend provides) is
  refused before anything is sent, and the offending key names are printed.

## Timing

All waiting uses `time.perf_counter()`: the emitter sleeps until 2 ms before the target and busy-waits for the
remainder. It waits only for the plan's `gap_before_ms` (before a trial), `marker_gap_ms` (between marker keys),
and `at_ms` (within a trial, relative to the trial start). A marker key is released immediately after its press.
Each `sent` and `marker` row carries `t_wall_ms` (Unix time in milliseconds) and `t_mono_ns` (monotonic clock in
nanoseconds), both taken immediately before dispatch. The self-test requires the 95th percentile of the
difference between actual and planned send time to stay under 20 ms.

## Reading an oracle

Rows appear in this order: header; for each block, an optional `reset`, `block_begin`, one `marker` per marker
key press (`seq` is its index in the block's marker array), then for each trial `trial_begin`, one `sent` per
step (`step` is the index into the plan's `steps`), `trial_end`; finally `block_end`. `--validate` checks the
header, the row kinds and key sets, integer timestamps, the nesting of blocks and trials, the pairing of
presses and releases, and that the monotonic clock does not run backwards; it prints line numbers and never
prints a value from the file.

## Adding a backend

Provide `backend_<name>.py` with `SUPPORTED_KEYS` (a frozenset of key names, pseudo-keys included) and a
`Backend` class with `__init__(opts)` (unknown options raise), `open()`, `send(key, down)`, and `close()`.
The core waits; the backend only sends. The core always calls `close()`, including after an exception.
