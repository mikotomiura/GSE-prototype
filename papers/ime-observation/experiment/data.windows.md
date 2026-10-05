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

How the attempts above were counted (the start refused before the first trial, and attempt 1, which was stopped from
outside the runner) is recorded as deviation D7 in `experiment/deviations.md`.

## Check of section 10.8 (versions differ from the pilot)

Before the first attempt, the versions of the system and of the input method were read on the measuring machine
after a restart that completed a pending update: Windows 11 build 26200.9457 and `IMJPTIP.DLL` 10.0.26100.9278, which
differ from those of the pilot (build 26200.8875, `IMJPTIP.DLL` 10.0.26100.8875; section 10.4). As section 10.8
requires, the check plan of the pilot (`verify` in `experiment/pilot-windows.md`: 39 trials, one per scenario and
speed, seed 8; SHA-256 `f02e046b1efd91d36f3c2785d91d098a670b905dcfce923f64f9cc7041440154`, read from the `plan_sha256` of the
manifest of the check run) was run first, with the cell file of the measurement
(deviation D5), on 2026-10-04 from 00:27 to 00:37 JST. A first start of the check was aborted by the runner before
any key was sent (deviation D5). In the check the runner aborted nothing and every front-window check passed. The
observation log was sealed before the reference side was read. The ground-truth sessions, assembled with the `win_tsf`
rules of `experiment/gt_rules.json`, were 39 (30 committed, 9 cancelled), and every trial produced the session its
plan intends (39 of 39), so the Windows cell was measured with these versions.

## What else ran on the measuring machine during attempt 2

Attempt 2 of the cell (question 1 to 4) ran from 01:57 to 13:03 JST on 2026-10-04. What the event logs of the machine
show for that window (read on 2026-10-05 with `Get-WinEvent`): one Windows Update install, at 04:52, of a Microsoft
Defender Antivirus security-intelligence update (events 43, 44, 19 of `Microsoft-Windows-WindowsUpdateClient`; no
other update was downloaded or installed); no Defender scan event (ids 1000 to 1002 of the Defender operational log);
and 11 events of id 12 of `Microsoft-Windows-UserModePowerService` (01:57:06, 02:07:05 and :07, 04:46:46 and :48,
10:46:25 to 10:48:14), which are power-state changes of the user-mode power service and were not read further. There was
no restart or unexpected shutdown (ids 41, 42, 1074 absent). The task-scheduler operational log has no event in the
window (the log is not enabled on this machine), so what the task scheduler started cannot be told from the records,
and the Claude Code sessions that ran on the machine were not read. This is what the records show, not a claim that
nothing else ran.

## Closed set of question 4 and the summary of experiment 3 (analysis run on 2026-10-05, Surface Pro 8)

- **Closed set** (sections 6.8 and 10.7 of the pre-registration, with deviation D8). The code was `kit/e2/closed_set.py` of
  commit `14c85e6e` (the frozen export with that one file replaced; the difference from the tagged file is the switch
  `--skip-scenario`, its self-test and its docstring; self-test OK, 157 checks). Inputs were checked before the run:
  `plan.jsonl` `b7bdf8fc120036f18ceff53d2bf8def43ef11a818a119bc24b0c7f4fbc4836b0`, `obs.jsonl`
  `58f0bda61fa4310c58a643bb605a68c360f34378b651a3b85d58290fabcd2562`. Command (from the replaced export):
  `python kit/e2/closed_set.py --obs <run>/obs.jsonl --plan <run>/plan.jsonl --corpus kit/corpus/data/phrases.jsonl
  --recipes kit/gen/recipes.json --config experiment/plan_config.windows.json --K 10,100,1000 --seed 20260929
  --bootstrap 2000 --markers-in-obs --skip-scenario S12 --out results/windows/e2_closed_set_windows-msime-tsf.json`.
  Exit 0 after about 2 h 40 min on this machine (standard error empty). Output SHA-256
  `93b5eb2bb7e43056899b78b6bcf486505ec91bced94844d065dcdd74a8d238b7`. `n_trials` 2,925 (all scored; 0 unscored blocks),
  `skipped_scenarios` `{"S12": 225}`, and for every K (10, 100, 1000) and every feature set `n` 2,700 and `n_skipped` 0.
  The comparison with chance (rule of section 6.8) is not made here.
- **Experiment 3** (section 10.9). `samples.tsv` SHA-256: idle `43ab3b395635e0d5c78abc008db31368b48bcc6595c74f74f59e8e21debc5f59`,
  working `638da0eaafcf156a441068e91a36578199736c435f08e140391617e43fcca88f`. Both are `status: measured`; in `working`
  `cpu_all_zero` is false (as in the record of M7). Summary `results/windows/e3_windows.txt` (SHA-256
  `dd12cc822693dd022c6ad711797ef1abd6c7b99c2a8363edcbbd2ef09967cc18`), made with `kit/e3/summarize_e3.py idle=... working=...`
  of the export.
