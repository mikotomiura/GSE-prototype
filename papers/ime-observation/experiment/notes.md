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

The analysis is frozen in `preregistration.md` (not yet written). `run.sh` refuses to analyse real data
until that file carries a `frozen_at:` line and a `sha256:` line. `config.json` and `SEED` are frozen
with it. Synthetic runs (`bash run.sh --synthetic`) do not need the freeze because they read no real data.

## Step 0 replaced

The reproduction template's Step 0 calls a capability-gate script of the parent repository. This
experiment's directory does not refer to anything outside `papers/` (the directory must be exportable on
its own), so Step 0 is replaced by two checks that `pipeline.py` performs before any statistic:

1. the content-free validators for the ground-truth and observation logs, the plan validator, and the
   oracle validator (a log with content, or with the wrong shape, stops the run with exit status 1);
2. a check that the observation log's header declares the `key` and `ime_shadow` channels in its
   capabilities, so a run made with a logger that lacks either channel cannot be analysed by mistake.

## Borrowed methods

Sources are added here as `[Pn]` identifiers when the pre-registration is written.

| Method | Where it is used | Source |
|---|---|---|
| Wilson score interval | proportions in all three results | (to be filled in) |
| Cluster bootstrap over blocks | dwell error, ICC intervals | (to be filled in) |
| Bland-Altman limits of agreement | dwell error, per-text aggregates | (to be filled in) |
| ICC(2,1), absolute agreement | per-text aggregates | (to be filled in) |
| Cohen's kappa | abandonment | (to be filled in) |
