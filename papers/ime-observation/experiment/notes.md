# Notes

## Questions and result files

The questions, the estimates that answer them, and the precision that counts as informative are stated in
`preregistration.md`. The result files are:

| Question | Estimates | Result file |
|---|---|---|
| Does the observer detect the compositions the input method performs? | Precision, recall, split and merge rates | `results/e1_detection.json` |
| Do the per-composition records agree with the input method's own state? | Dwell error, abandonment, navigation counts, the 20-second cut-off, plan-versus-ground-truth disagreements | `results/e1_l1.json` |
| Do the per-text aggregates a writing researcher computes agree? | Bland-Altman limits and ICC(2,1) of four per-text measures | `results/e1_l2.json` |
| How much of the typed text can be recovered from a published log? | Closed-set identification accuracy against chance, open-set character error rate against a prior-only baseline | `results/e2_closed_set.json`, `results/e2_open_set.json` |
| What does the observer cost the machine? | CPU and resident memory under two conditions | `results/e3_<system>_<condition>.json` |

## Pre-registration

The analysis is frozen in `preregistration.md`. `run.sh` and `pipeline.py` refuse to analyse real data until
that file carries, outside HTML comments and code fences, exactly one line starting `frozen_at: YYYY-MM-DD`
and exactly one line `sha256: <64 lowercase hex digits>`. Placeholders and empty values are not marks. The
recorded `sha256` must equal the value printed by

    python3 kit/analysis/pipeline.py --freeze-hash --config experiment/config.json --seed-file experiment/SEED

which is the SHA-256 of the text made of the SHA-256 (lowercase hex) of `config.json`, of `SEED` and of the
ground-truth rule file named by `gt_rules`, in this order, each followed by a line feed. A person writes the
value in the file when the analysis is frozen; both entry points recompute it and stop with exit status 3
when it differs, so that the analysis settings cannot change after the freeze. Analysis code is fixed by the
tag of the freezing commit. `config.json`, `SEED` and the rule file are stored with LF line ends so that the
hash is the same on every machine. Synthetic runs (`bash run.sh --synthetic`) do not need the freeze because
they read no real data.

The protocol is frozen in two stages. The first freeze covers the macOS cells. The addendum for the Windows
cells, frozen before the first Windows measurement, may change only the Windows blocks of the rule file and
its own section of `preregistration.md`; it then rewrites the two marks. That `config.json`, `SEED`, the
macOS block of the rule file and the macOS sections are unchanged is shown by the difference between the two
freezing tags.

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

Before these, `pipeline.py` checks the freeze marks, the run manifests, and the SHA-256 of every log against
its manifest.

## Analysis settings

Every cell is analysed under two session definitions: the one that follows the operating system of the
cell (`macos_def` or `windows_def`) and the common definition `all`; the results are stored as
`cells[label][definition]`. On the reference side of a macOS cell the two definitions hold the same
sessions. The cell label comes from the `label` of the cell file recorded in `run.json`. `iou_min`,
`obs_end_offset_ms`, `theta` and `drop_start_while_open` are passed to the matcher; `bootstrap_B`, `limit_ms`,
`text_size_trials` and `mixtures` to the level-1 and level-2 stages.

Clock offsets are not corrected: every block is compared with a zero offset (`clock_offsets_ms` is not passed
to the matcher). The dwell error is a difference of durations and does not depend on the offset, and a session
pairs under the overlap criterion while the offset stays at or below a third of its length. The per-block
offsets between the observation, the reference input field and the executor are measured at the block-start
markers with `kit/pilot/clock_sync.py` in every run and reported with the results.

## Borrowed methods

| Method | Where it is used | Source |
|---|---|---|
| Wilson score interval | detection rates, abandonment and navigation agreement, plan-versus-ground-truth disagreements, closed-set accuracy | Wilson (1927) |
| Percentile bootstrap | intervals of the dwell error, the ICC and the open-set error rate | Efron (1979) |
| Resampling whole blocks (cluster bootstrap) | the same intervals | Cameron, Gelbach and Miller (2008) |
| Bland-Altman limits of agreement | dwell error, per-text aggregates | Bland and Altman (1986) |
| ICC(2,1), absolute agreement | per-text aggregates | Shrout and Fleiss (1979); McGraw and Wong (1996) |
| Cohen's kappa | abandonment | Cohen (1960) |
| Witten-Bell smoothing | the open-set attacker's character language model | Witten and Bell (1991) |

Full references are listed in `preregistration.md`.
