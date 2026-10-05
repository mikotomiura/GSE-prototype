# Deviations

Departures from the frozen registration (`preregistration.md`, tag `ime-observation-prereg-macos`), recorded
under section 8 before the analysis they affect is run. Each entry gives its date, the reason and the effect. D1
to D5 were made for the Windows cell before any Windows measurement; the evidence that they leave the macOS
cells unchanged is given at the end. D6 concerns the macOS measurement.

## D1. Scenario S4 presses three Escapes on Windows (2026-10-03)

**What changes.** Under the Windows procedure, scenario S4 (cancel with the candidate window shown) types the
reading, presses Space, pauses and presses Escape three times instead of twice. The table of section 2.3 lists
two Escapes for every system, and the plan generator checked S4 against two Escapes under every profile
(`_scenario_checks` in `kit/gen/generate_plan.py`), so the Windows addendum could not make this change within the
parts that section 8 lets it change. The generator now reads the Escapes of S4 from a new entry of each profile,
`cancel_converted`: three for `windows` and two for both macOS profiles. The Windows sections (`os.windows`) of
both procedure files press the third Escape.

**Reason.** The Windows calibration pilot (Microsoft IME, Windows 11 25H2, build 26200) found that two Escapes
do not cancel a reading that was converted into several segments: the first Escape reverts the focused segment,
the second returns the reading to kana and opens the prediction window, and only the third cancels the
composition; an Escape after the cancel reached the field as a plain key press. A reading converted into one
segment was cancelled by the second Escape. With two Escapes every S4 trial of the pilot (9 of 9) left an
uncommitted reading that was carried into the next trial and changed the procedure of that trial. Together with the
carry-over of S8, whose digit pick needed a Return (fixed within section 8 by the Windows profile), it hid the
clock-alignment marker of the reference input field in three of six blocks. Check runs with both changes (39
trials on each of the two reference fields) left no reading uncommitted, cancelled every S4 trial at the third Escape
and found the marker in every block.

**Effect.** In the Windows cell, S4 keeps its intent (`commit: none`, `abandon: true`). The third Escape adds one key
press to each S4 trial; when the reading is cancelled by the second Escape, the third is expected to reach the
reference input field as a key press outside a composition, and the Escape after which each S4 session ended is
reported (section 10.7). Because the generator reads the Escapes of S4 from the profiles, the difference between the
two freezing tags shows lines that touch the macOS profiles (the new entry, with the two Escapes of the frozen check)
and the check of S4, which all profiles share. On the macOS cells: see the end of this file.

## D2. The analysis accepts the registered plan and reference of the Windows cell (2026-10-03)

**What changes.** Before analysing real data, `kit/analysis/pipeline.py` checks that each run used the plan that
section 2.4 gives its cell (reason 1 of section 3.4). The frozen check accepted a run only when its cell records live
conversion `on` or `off` and its plan log is one of the two macOS measurement plans, so every run of a Windows cell
would have counted as aborted. The check now accepts a run whose cell records the operating system `windows` when its
plan log is the measurement plan of the Windows cell (SHA-256
`b7bdf8fc120036f18ceff53d2bf8def43ef11a818a119bc24b0c7f4fbc4836b0`, section 10.6) and its reference log comes from
the TSF reference input field (header `src` `win_tsf`, section 10.4); the check of the macOS cells is unchanged. When a
Windows cell is analysed, the delivery results record both values (`registered_plan_sha256_windows`,
`windows_reference_src`).

**Reason.** Section 8 lets the Windows addendum change only the Windows parts of the rule file, of the procedure files
and of the generator's profiles, and add new files; the plan check is in none of them. Without the change the
registered analysis could not be run on any Windows run. The check of the reference makes the choice of the reference
input field (section 10.4) a closed rule rather than a statement.

## D3. The scopes of the Windows cell take the long trials from the presses sent (2026-10-03)

**What changes.** Questions 1 to 3 are answered primarily over the trials that are not long (scope `under_limit`,
section 6.4), and the long trials come from the prediction of section 4.5. The prediction models the macOS observer,
which infers sessions from key presses; the Windows observer follows the input method's window (section 10.3), which
the presses do not determine, so no prediction applies to it, and the frozen pipeline computed a Windows cell under
`all_trials` only. For a Windows cell a trial is now long when the presses that the executor sent in it span at least
`limit_ms` (20,000 ms) on the wall clock, from the first press to the last, and `under_limit` and `over_limit` are
built from these trials by the code used on macOS (`kit/analysis/scope_windows.py` hands them to
`kit/analysis/match.py` in the form of a prediction). As a sensitivity analysis, detection under `under_limit` is also
computed with the long trials of the ground truth (a reference session of at least `limit_ms`), and the trials that
the two rules classify differently and those whose reference session lasts from 19 to 21 seconds are counted. The
comparisons with the prediction (`gt_pred`, `pred_obs`) and the prediction's layers are not computed for a Windows
cell. The result files state this (`note_windows` beside the primary estimates, and `long_trials_from` per Windows
cell).

**Reason.** Without a scope the primary agreement of a Windows cell would mix the long trials, in which the observer
may cut a session off, with its errors, and could not be compared with the macOS cells. The rule uses the oracle and the
plan alone, as the macOS scope does, so neither side of a comparison decides which trials are compared. It is not the
rule of the observer's own cut-off, which on Windows depends on the path that drives it (section 10.3); the boundary
counts and the sensitivity analysis report how much this matters.

**Effect.** On a Windows cell the long trials are defined by what was sent. With the corrected Windows procedure, the
trials whose presses span at least 20 seconds were exactly the long trials of the ground truth in two check runs of
the pilot with the TSF field: 10 trials of one plan, run twice.

## D4. A key row of the observation that no sent press explains counts a Windows run as aborted (2026-10-03)

**What changes.** For a run whose plan is for Windows, the rules of section 3.4 have one more: the observation log is
divided into segments at the block starts, as the reference log is, and the run counts as aborted when in any segment
the key rows that no sent press explains exceed the marker presses of the segment (version `excluding_mode_keys` of
`observation.segments` in the delivery report; the observer writes no row for the runner's `VK_IME_ON`, so there is no
allowance for it). `kit/analysis/pipeline.py` applies the rule in the analysis and in `--pack` and `--check-deposit`,
and records it when a Windows cell is analysed (`windows_observation_presses_from_outside_abort`).

**Reason.** The TSF reference input field receives only the keys that the input method does not consume, so a person
typing into it while it has the focus would pass the rule on presses from outside, and, since the focus is not lost,
the rule on the loss of focus. On macOS the reference field received every key-down, so this case was closed. Section
2.1 states that no person's typing is part of the data; without the rule this could not be supported on Windows.

**Effect.** In every segment of the seven runs of the Windows pilot the key rows of the observation that no sent press
explains were exactly the marker presses. The rule also aborts a run in which the observer writes a key row twice,
which is an error of the observer under test; the figures of such a run are reported (section 10.8). It cannot catch
a press of a key that the observer does not record (section 10.3), a person's press that cancels a sent press that the
observation lost, or input with the pointer, touch or pen. It applies to the runs of the Windows cell and of the
`working` condition on Windows, and not to macOS plans.

## D5. The cell file of the Windows measurement names the two programs with backslashes (2026-10-04)

**What changes.** `kit/run/README.windows.md` (step 3) makes the cell file of the measurement by copying
`kit/run/cell.windows.json` and filling in `ime`, `clock_sync_disabled` and `auto_update_disabled`. In the cell file of
the measurement the first entries of `refinput_cmd` and `logger_cmd` are also written with backslashes, as
`kit\refinput-windows\target\release\refinput_tsf.exe` and `kit\logger\target\release\ime-observation-logger.exe`,
still relative to the top directory of the published materials. Nothing else in the cell file differs from the
template, and the template, the runner and every other file of the tag are unchanged. The same cell file is used for
the check of section 10.8 (the input method's version differs from the pilot's) and for the runs of the Windows cell and
of the `working` condition; the run manifest records it.

**Reason.** Started from the top directory as the README describes, the runner could not start the observer or the
reference input field: `subprocess.Popen` on Windows refused the relative program paths with forward slashes (`FileNotFoundError`,
WinError 2), and the first attempt of the check of section 10.8 was aborted by the runner on 2026-10-04 before any key
was sent. The same programs started from the same directory when the paths were written with backslashes or began with
`./`. The pilot did not find this because its cell files named the programs by absolute paths. The
template could not be corrected without changing a file of the tag.

**Effect.** The programs, their arguments and the directory they run from are those of the template; only the
separator in the two paths differs. No key was sent in the aborted attempt, and it is not a run of the Windows cell.

## D6. The macOS runs were not made on separate nights (2026-10-05)

**What changes.** Section 3.2 states that the runs are made on separate nights, in the order live conversion on,
live conversion off, `idle` and `working`, and section 6.10 measures each condition of question 5 on one night. The
runs were made in this order, each after the check of the one before it, but each was started as soon as that check
was done (times in UTC; local time is UTC+9): the cell with live conversion on from 2026-10-02 16:03 to 2026-10-03
04:04, the cell with it off from 04:19 to 15:27 on 2026-10-03, `idle` from 2026-10-03 15:37 to 23:37, and `working`
from 2026-10-04 13:03 to 2026-10-05 01:04. The run with live conversion off began in the local afternoon, and it and
`idle` both fell in the night from 2026-10-03 to 2026-10-04.

**Reason.** The operator chose to start each item when the one before it had been completed and checked, rather than
wait for the next night.

**Effect.** The order of section 3.2, which keeps the learning added by the replay of section 6.10 from preceding the
two cells, is kept, and no two items overlapped. Nothing else of the registration depends on the hour of a run.
The background load on the machine during each run is reported in `env.md`.

## The macOS cells are unchanged

The macOS plans and analysis are generated and run from the macOS tag (section 8). That the changed files would give
the same results was checked on 2026-10-03, on Windows 11 with Python 3.11.9, in checkouts with LF line ends of the
macOS tag and of the commit that holds the code of the addendum (`3cc151c7`; the commits after it up to the
freezing commit of the addendum change documents only):

- Plans: in each checkout,
  `python kit/gen/generate_plan.py --config experiment/plan_config.macos.json --recipes kit/gen/<file> --corpus
  kit/corpus/data/phrases.jsonl --os macos --seed 20260929 --out <plan>` for both procedure files. From the macOS tag
  the plans have the SHA-256 that section 2.4 gives (`c7a5469d…` and `3759ebf7…`); from the changed files they have
  `e7a541b17830f94c48e7f284e0f89f608a257ed66eb8abf541be5a0ba7f7ed3f` and
  `3bf24b2eb7ba67fcb8692d45d06c120b890f39f26bae97dc120888b2496e91fb`, and with the recorded SHA-256 of the procedure
  file replaced by the same string the two plans of each file are byte-identical.
- Analysis: two synthetic macOS runs made by `python kit/analysis/pipeline.py --synthetic <dir> --seed 4` (macOS tag)
  were analysed in each checkout by `python kit/analysis/pipeline.py --runs <dir>/run-a <dir>/run-b --config <cfg>
  --seed 7 --out <out>`, with a configuration file holding `bootstrap_B` 2000 and the rule file
  `kit/analysis/gt_rules.example.json`. The four result files were byte-identical: `e1_delivery.json` `d8298a16…`,
  `e1_detection.json` `a8fa275d…`, `e1_l1.json` `d849701d…`, `e1_l2.json` `8a95c080…`.
- The self-test of `kit/analysis/pipeline.py` checks, on synthetic runs, that an analysis of macOS cells alone records
  none of the values of D2 to D4 and that the rule of D4 does not apply to a macOS run; it does not compare with the
  macOS tag.
