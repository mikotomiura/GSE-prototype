# ime-observation-logger

A standalone logger that reuses a reference conversion-session state machine, without modifying the
application it is drawn from, to produce the observations used by the evaluation. This logger, not the
originating application, is what the evaluation runs. Output follows format `obs/1` (see
`../formats/FORMATS.md`).

The observation is content-free by construction: a `key` line carries only one of fourteen categories
(which key was pressed is discarded), and an `ime_shadow` line carries only counts (`dwell_ms`, `nav`,
`abandon`). No character, candidate string, reading or window name is recorded.

Provenance of the reused logic (which files or ranges were copied and from where) is kept separately, in
`PROVENANCE.internal.md`, which is not published alongside this directory.

## Driver contract (`src/driver_api.rs`)

Each driver exposes `pub fn start(ctx: DriverCtx) -> Result<DriverHandle, String>`. It sends every
observed key transition as `KeyEvent { t, vk, press }` (`t` is wall-clock time in milliseconds; `vk` is
mapped to the Windows virtual-key space) to `ctx.keys`, and exchanges conversion-session state through
the atomics exposed by `src/input/hook.rs`.

- **Stop**: once `ctx.stop` is raised, a driver must end its own thread within
  `driver_api::STOP_DEADLINE_MS` (500 ms by default). The core loop watches driver liveness with
  `JoinHandle::is_finished()` and ends with an error if a driver thread terminates unexpectedly.
- **Candidate-window observation hook**: returning `Some(Box<dyn FnMut() -> bool + Send>)` in
  `DriverHandle.candidate_window_observer` lets the core's monitoring loop (`Monitor::poll`) call it
  once per cycle to judge whether a candidate window is currently open (`None`, the default, falls back
  to reading `IME_ACTIVE` directly). The **calling thread** is whichever thread calls `Monitor::poll`
  (which may differ from a driver's own key-capture thread). A driver whose observer relies on a
  COM-based accessibility API must perform that API's initialization on its first call, on the calling
  thread (see the module documentation of `driver_api.rs` for the reasoning).

## Build, selftest, verification

```bash
# From the repository root.
cargo test  --manifest-path papers/ime-observation/kit/logger/Cargo.toml      # includes the copied state machine's tests
cargo build --release --manifest-path papers/ime-observation/kit/logger/Cargo.toml
papers/ime-observation/kit/logger/target/release/ime-observation-logger --selftest --out /tmp/obs.jsonl
python3 papers/ime-observation/kit/formats/validate_logs.py --kind obs /tmp/obs.jsonl

python3 papers/ime-observation/kit/logger/check_manifest.py --self               # copies match the manifest (does not read the reference source tree)
python3 papers/ime-observation/kit/logger/check_manifest.py --against-upstream   # copies match the reference source tree's current files (drift check)
python3 papers/ime-observation/kit/logger/check_manifest.py --selftest           # negative controls for the verifier itself
```

Run as: `ime-observation-logger --out <path> [--duration-s <n>]` (until a driver is present for the
current platform, this ends with "not implemented"). The output path is opened with
`OpenOptions::new().write(true).create_new(true)` (**an existing observation log is never overwritten**;
the path is opened only after the driver has started successfully). Passing `--out` twice, or a negative
or non-integer `--duration-s`, is a usage error (exit 2). `--selftest` removes its default output path
(used when `--out` is not given) after it runs.

## Rewriting the manifest

`check_manifest.py --update --manifest <manifest*.json> --entries <spec.json>` rewrites **exactly one**
manifest, merging **by id** (an entry whose id already exists is replaced; every other existing entry is
kept; no other `manifest*.json` is opened). `spec.json` is an array of entries carrying `kind`, `id`,
`path`, `upstream_path`, the anchor fields, `symbol`, `check_decls` and `reason`; `sha256`,
`upstream_range_sha256`, `upstream_last_commit` and the manifest's own `upstream_repo_commit` are filled
in by the verifier. Verification refuses to write an entry whose copy is not verbatim against the
reference source (or, for a `new` entry with anchors, whose transcribed judgment no longer matches).

A `kind: "new"` entry is, by default, not checked at all by `--against-upstream` (the mere presence of
`upstream_path` triggers nothing). Whichever of these applies must be requested explicitly:

- `"check_decls": true` — verifies that every `pub const|static NAME: T = V;` declaration on the copy
  side has the same type and value as the corresponding declaration at `upstream_path` (used to pin a
  shim's constants and statics).
- `"start_anchor"` / `"end_anchor"` (with `"upstream_range_sha256"` filled in by the verifier) — verifies
  that the SHA-256 of that range of `upstream_path` (sliced the same way as an excerpt: from the start
  anchor, inclusive, to the end anchor, exclusive, matching whole lines, with each anchor occurring
  exactly once) has not changed. This pins a piece of reference *logic* rather than reference *text*: the
  copy need not be verbatim.

If `--against-upstream` fails, the reference implementation has changed. The copy should be refreshed
from the reference source and its tests re-run before `--update` is called again; a failing copy should
never be hand-edited into passing.

## Limitations

- SHA-256 is computed after normalizing CRLF to LF, so this check cannot by itself distinguish a
  pure line-ending change.
- `Cargo.lock` is resolved from the same starting lockfile as the reference implementation's own
  manifest, so that every shared crate is pinned to the same version. Bumping a version or adding a
  crate should re-resolve from that same starting lockfile with `cargo check`, rather than running
  `cargo update` or `cargo generate-lockfile` with no arguments, which would resolve everything to its
  latest version.
- Building this logger on Windows does not compile the `#[cfg(target_os = "macos")]` side.
