# Deviations

Departures from the frozen registration (`preregistration.md`, tag `ime-observation-prereg-macos`), recorded
under section 8 before the analysis they affect is run. Each entry gives its date, the reason and the effect.

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
clock-alignment marker of the reference input field in three of six blocks. A check run with both changes (39
trials on each reference path) left no reading uncommitted, cancelled every S4 trial at the third Escape and found
the marker in every block.

**Effect.** None on the macOS cells. Their plans are generated, and their analysis is run, from the macOS freezing
tag (section 8), and the macOS profiles keep two Escapes. A macOS plan generated after this change from either
procedure file, with the measurement settings and the same seed, differs from one generated from the tag only in the
recorded SHA-256 of the procedure file (checked on 2026-10-03). In the Windows cells, S4 keeps its intent
(`commit: none`, `abandon: true`). The third Escape adds one key press to each S4 trial; when the reading is cancelled
by the second Escape, the third is expected to reach the reference input field as a key press outside a
composition. Because the generator reads the Escapes of S4 from the profiles, the difference between the two
freezing tags shows lines that touch the macOS profiles (the new `cancel_converted` entry, with the two Escapes of
the frozen check) and the check of S4, which is shared by all profiles; that these lines leave the macOS plans
unchanged is shown by the comparison above. The Windows addendum refers to this entry for them.

## D2. The analysis accepts the registered plan of the Windows cell (2026-10-03)

**What changes.** Before analysing real data, `kit/analysis/pipeline.py` checks that each run used the plan that
section 2.4 gives its cell (reason 1 of section 3.4). The frozen check accepted a run only when its cell records live
conversion `on` or `off` and its plan log is one of the two macOS measurement plans, so every run of a Windows cell
would have counted as aborted. The check now accepts a run whose cell records the operating system `windows` when its
plan log is the measurement plan of the Windows cell (SHA-256
`b7bdf8fc120036f18ceff53d2bf8def43ef11a818a119bc24b0c7f4fbc4836b0`, given in the Windows addendum); the check of the
macOS cells is unchanged. When a Windows cell is analysed, the delivery results also record this value
(`registered_plan_sha256_windows`).

**Reason.** Section 8 lets the Windows addendum change only the Windows parts of the rule file, of the procedure files
and of the generator's profiles, and add new files; the plan check is in none of them. Without the change the
registered analysis could not be run on any Windows run.

**Effect.** None on the macOS cells: on two synthetic macOS runs the four result files of the changed code are
byte-identical to those of the code at the macOS freezing tag (checked on 2026-10-03), and the macOS analysis is run
from that tag (section 8).

## D3. The scopes of the Windows cell take the long trials from the ground truth (2026-10-03)

**What changes.** Questions 1 to 3 are answered primarily over the trials that are not long (scope `under_limit`,
section 6.4), and the long trials come from the prediction of section 4.5. The prediction models the macOS observer,
which infers sessions from key presses; the Windows observer reads the input method's own composition events, so no
prediction from the key presses applies to it, and the frozen pipeline computed a Windows cell under `all_trials`
only. For a Windows cell a trial is now long when a ground-truth session assigned to it lasts at least `limit_ms`
(20,000 ms, end minus start on the wall clock, the duration that the cut-off check of section 6.6 uses), and
`under_limit` and `over_limit` are built from these trials by the same code as on macOS (`kit/analysis/gt_scope.py`,
which hands them to `kit/analysis/match.py` in the form of a prediction). The comparisons with the prediction
(`gt_pred`, `pred_obs`) and the prediction's layers are not computed for a Windows cell. The result files state this
(`note_windows` beside the primary estimates, and `long_trials_from` per Windows cell).

**Reason.** The cut-off at 20 seconds is the same on both systems, so without a scope the primary agreement of a
Windows cell would mix the sessions that the observer is specified not to report with its errors, and could not be
compared with the macOS cells. The ground truth already records each session's start and end, which the cut-off check of section 6.6 uses.

**Effect.** None on the macOS cells (the comparison of D2). On a Windows cell the long trials are defined by what the
input method did rather than by what was sent; with the corrected Windows procedure, the trials whose planned presses
span at least 20 seconds were exactly the long trials of the ground truth in two check runs of the pilot (10 of 10
each, `experiment/pilot-windows.md`). A trial whose session is shortened or lengthened by the input method (for
example a commit at a loss of focus) is classified by the session the reference recorded.
