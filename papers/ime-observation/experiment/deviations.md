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
