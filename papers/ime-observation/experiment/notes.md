# Notes

## Claims under test

The claims are C3, C4 and C5 of the design document, section 0. For each one, state here the measure that
decides it, the comparison it is read against, and the width of the interval that would count as
informative (to be filled in when the pre-registration is written).

| Claim | Measure | Result file |
|---|---|---|
| C3 | Detection of compositions (precision, recall, split and merge rates) | `results/e1_detection.json` |
| C4 | Level-1 agreement (dwell error, abandonment, navigation counts) | `results/e1_l1.json` |
| C5 | Level-2 agreement (per-text aggregates, ICC(2,1), Bland-Altman) | `results/e1_l2.json` |

## Pre-registration

The analysis is frozen in `preregistration.md` (not yet written). `run.sh` and `pipeline.py` refuse to
analyse real data until that file carries, outside HTML comments and code fences, exactly one line
`frozen_at: YYYY-MM-DD` and exactly one line `sha256: <64 lowercase hex digits>`. Placeholders and empty
values are not marks. The recorded `sha256` must equal the value printed by

    python3 kit/analysis/pipeline.py --freeze-hash --config experiment/config.json --seed-file experiment/SEED

which is the SHA-256 of the text made of the SHA-256 (lowercase hex) of `config.json`, of `SEED` and of the
ground-truth rule file named by `gt_rules`, in this order, each followed by a line feed. A person writes the
value in the file when the analysis is frozen; both entry points recompute it and stop with exit status 3
when it differs, so that the analysis settings cannot change after the freeze. Analysis code is fixed by the
tag of the freezing commit. `config.json`, `SEED` and the rule file are stored with LF line ends so that the
hash is the same on every machine. Synthetic runs (`bash run.sh --synthetic`) do not need the freeze because
they read no real data.

## Step 0 replaced

The reproduction template's Step 0 calls a capability-gate script of the parent repository. This
experiment's directory does not refer to anything outside `papers/` (the directory must be exportable on
its own), so Step 0 is replaced by checks that `pipeline.py` performs before any statistic:

1. the content-free validators for the ground-truth and observation logs, the plan validator, and the
   oracle validator (a log with content, or with the wrong shape, stops the run with exit status 1);
2. a check that the observation log's header declares the `key` and `ime_shadow` channels in its
   capabilities, so a run made with a logger that lacks either channel cannot be analysed by mistake;
3. when the header places `ime_shadow` among the gated channels and the ground truth holds sessions, at
   least one `ime_shadow` row must exist: a gated channel that produced no row cannot be judged.

## Analysis settings

Every cell is analysed under two session definitions: the one that follows the operating system of the
cell (`macos_def` or `windows_def`) and the common definition `all`; the results are stored as
`cells[label][definition]`. The cell label comes from the `label` of the cell file recorded in `run.json`.
`theta` (default 0.5) and `drop_start_while_open` (default false) are passed to the matcher.

Unresolved: `clock_offsets_ms`, the correction for the gap between the clock of the ground-truth side and the
clock of the observation side, is not passed to the matcher, so every block is compared with a zero offset.
Where the offsets come from is to be decided after the calibration pilot.

## Borrowed methods

Sources are added here as `[Pn]` identifiers when the pre-registration is written.

| Method | Where it is used | Source |
|---|---|---|
| Wilson score interval | proportions in all three results | (to be filled in) |
| Cluster bootstrap over blocks | dwell error, ICC intervals | (to be filled in) |
| Bland-Altman limits of agreement | dwell error, per-text aggregates | (to be filled in) |
| ICC(2,1), absolute agreement | per-text aggregates | (to be filled in) |
| Cohen's kappa | abandonment | (to be filled in) |
