# Environment

Fill in one section per machine that produces or analyses run directories. Record the values at the time
of the run; do not edit them afterwards.

## Analysis machine

| Item | Value |
|---|---|
| Operating system and version | (to be filled in) |
| Python version (`python3 --version`) | (to be filled in) |
| Python packages | none (standard library only) |
| Commit of this repository | (to be filled in) |
| Date of the analysis | (to be filled in) |

## Measuring machines (one row per cell)

| Cell label | Operating system and build | Input method and version | Rust toolchain (`rustc --version`) | Swift version (`swiftc --version`) |
|---|---|---|---|---|
| macos-standard-live-on | macOS 27.0.1 (26A434), Apple Silicon, 10 logical processors | macOS Japanese, Romaji input (JapaneseIM-RomajiTyping 6.3) | rustc 1.99.0 (b940084d7 2026-09-28) | Apple Swift version 6.4 (swiftlang-6.4.0.34.1) |
| macos-standard-live-off | macOS 27.0.1 (26A434), Apple Silicon, 10 logical processors | macOS Japanese, Romaji input (JapaneseIM-RomajiTyping 6.3) | rustc 1.99.0 (b940084d7 2026-09-28) | Apple Swift version 6.4 (swiftlang-6.4.0.34.1) |
| macos-e3-working | macOS 27.0.1 (26A434), Apple Silicon, 10 logical processors | macOS Japanese, Romaji input (JapaneseIM-RomajiTyping 6.3) | rustc 1.99.0 (b940084d7 2026-09-28) | Apple Swift version 6.4 (swiftlang-6.4.0.34.1) |

The `idle` condition of question 5 ran on the same machine with the same build. All macOS runs were made on
2026-10-02 to 2026-10-05 on mains power. The same machine also hosts a runner of a continuous-integration
service, which was left running: build jobs of another project started on it 12 times during the run with live
conversion on, 8 times during the run with live conversion off, 5 times during `idle` and once during `working`,
each lasting 2 to 35 minutes. The pre-registration does not restrict background load; it is reported as a
limitation.

## Lock files

The logger and the reference input fields are built from lock files that are committed with the kit.
Record the SHA-256 of each one used for a run.

| File | SHA-256 |
|---|---|
| `kit/logger/Cargo.lock` | `206d2ed8be683458ca035fed879c057a55cd119e431960a4059544a51621a71b` (macOS runs) |
| `kit/refinput-windows/Cargo.lock` | (to be filled in) |

The macOS reference input field has no lock file; record the Swift version above.
