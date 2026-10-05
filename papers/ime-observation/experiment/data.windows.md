# Data of the Windows cell

The runs of the Windows cell and of question 5 on Windows are recorded here, not in `data.md`, so that the
analysis of the macOS cells (from the macOS freezing tag, with `run.sh`, which reads `data.md`) and the analysis of the
Windows cell (from the Windows freezing tag, with the command of section 10.7 of the pre-registration) each read only
their own runs. Everything not stated here is as in `data.md`: the raw run directories are never committed to git,
and each one is deposited and recorded with the SHA-256 of its deposited archive.

## Run directories used by the analysis of the Windows cell

The lines of the form `- run_dir: PATH  manifest_sha256: HEX` below are read as in `data.md` (a relative path is
relative to this file; lines inside HTML comments and code fences are not read). Only runs of the Windows cell are
listed here; the runs of question 5 appear only in the tables below.

<!-- - run_dir: /path/to/an/unpacked/run-directory  manifest_sha256: 0000000000000000000000000000000000000000000000000000000000000000 -->

- run_dir: runs/windows-msime-tsf-2  manifest_sha256: 5c74a1fad735b5983152847d29a540e71673f7d13257950af9726ddd79a33d82

## Deposits

| Cell label | Deposit location | SHA-256 of the archive | Date deposited |
|---|---|---|---|
| windows-msime-tsf (attempt 2; packed on the measuring machine, Windows 11 Home, with `--also-user` and `--also-home` each given once) | not yet deposited | `f2287a7494b108a7b827f96da48f523e84e1a9478121d03fa82dca2c8749cd06` | not yet deposited |

## Run checks (sections 3.4 and 10.8 of the pre-registration)

One line per attempt of the Windows cell and of the `working` condition of question 5, also for an attempt that the
runner aborted, made as in `data.md` (Deposit procedure, step 1) with two differences: the plan's SHA-256 is checked
against the plan of section 10.6, and the reference log's header must name `win_tsf`. Right after each attempt its
line is committed and pushed (section 10.8). The figures of the rule on presses are read from the version `excluding_mode_keys` of
`reference.segments`; the figure of deviation D4 is the largest count over the segments of the observation of
`observation.segments` (version `excluding_mode_keys`) minus the marker presses of the segment. The bounds of the
four counts are 0.

| Cell label | Attempt | Aborted by the runner | Checked at | SHA-256 of the plan | `src` of the reference log | `delivery.py` exit status | `max_beyond_markers_before_last_block` | `beyond_markers_last_block` | `n_loss_spans_with_unexplained_presses` | Observation rows beyond the markers (D4) | Counts as aborted | Deposited |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| windows-msime-tsf | 1 | No: the runner was stopped from outside at about 00:59 JST, 21 minutes in (the shell that ran it was ended by the coding assistant's session under low memory); no manifest was written, so no manifest SHA-256 | 2026-10-04T01:00+09:00 | `b7bdf8fc120036f18ceff53d2bf8def43ef11a818a119bc24b0c7f4fbc4836b0` | `win_tsf` | 0 | 0 | 0 | 0 | 14 (last segment, cut off) | Yes (incomplete) | No |
| windows-msime-tsf | Not numbered (refused before the first trial) | Yes: started at about 01:51 JST with administrator rights, the runner refused to go on (`refusing to run with administrator rights`) before the first trial; no key was sent (the oracle log holds its header only); manifest SHA-256 `0027d0a428b554181ae3aa36f08f6e564fe7c207bb30d8718942be6c99ced1b9` | 2026-10-04T01:56+09:00 | `b7bdf8fc120036f18ceff53d2bf8def43ef11a818a119bc24b0c7f4fbc4836b0` | `win_tsf` | 0 | 0 | none (no trial) | 0 | 0 | No: by the researcher's decision this start, which sent no key, is not counted among the at most three attempts | No |
| windows-msime-tsf | 2 | No: ran from 01:57 to 13:03 JST, all 2925 planned trials measured, none incomplete; manifest SHA-256 `5c74a1fad735b5983152847d29a540e71673f7d13257950af9726ddd79a33d82` | 2026-10-04T13:04+09:00 | `b7bdf8fc120036f18ceff53d2bf8def43ef11a818a119bc24b0c7f4fbc4836b0` | `win_tsf` | 0 | 0 | 0 | 0 | 0 | No | No |
| windows-msime-tsf, question 5 `working` | 1 | No: ran from 21:29 JST on 2026-10-04 to 08:35 JST on 2026-10-05, all 2925 planned trials measured, none incomplete; manifest SHA-256 `1e5f40ac835978ad2adc722b3e17b23bb4b6b4424706c87b7de377ec552e217a` | 2026-10-05T10:03+09:00 | `b7bdf8fc120036f18ceff53d2bf8def43ef11a818a119bc24b0c7f4fbc4836b0` | `win_tsf` | 0 | 0 | 0 | 0 | 0 | No | No |
