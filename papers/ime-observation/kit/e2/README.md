# kit/e2: closed-set identification by simulation attack

This directory holds the closed-set part of the leakage evaluation: given the publishable form of a log, decide which
of K candidate phrases was typed, and measure how much of this identification survives when features of the log are
removed. The open-set reconstruction of the typed reading is a separate component.

| File | Content |
|---|---|
| `simulate_obs.py` | Predicted observation of one planned trial, and the feature transforms of the removal experiment |
| `closed_set.py` | The attack, the evaluation, and the command line |

Both files use the Python standard library only. Each has a fast default `--selftest` (a few seconds).

## What the attacker sees

The attacker sees the publishable form of a log: the category and the time of each key row, and the rows of type
`ime_shadow`. The raw key code is not part of it. There are 14 categories, and every letter key falls into the single
category `alphabetic`. The format is `obs/1` in [`../formats/FORMATS.md`](../formats/FORMATS.md).

The reader `read_obs` accepts the header, `key` rows and `ime_shadow` rows of a standalone-logger output and rejects
every other row type and every unknown key. The attack never reads the runner's ground-truth log or its oracle log,
which record what was sent and are not part of a publishable log. The typed phrase enters the evaluation only when the
accuracy is computed, and it is taken from the plan (the stimulus list), not from any log the attacker could see.

## Attacker knowledge

Knowledge is defined in levels. This component implements level K2.

| Level | Attacker knows |
|---|---|
| K0 | the log only |
| K1 | K0 and the genre of the text (which corpus) |
| K2 | K0 and a closed set of K candidate phrases (K = 10, 100, 1000) |

Under K2 the attacker also knows the scenario, the OS, the typing-speed level, the generator, the recipes and the
configuration, because a published experimental protocol reveals them. The attacker does not know the typed phrase, and
does not know the random draws inside the scenario (candidate index, number of arrow keys, thinking pause, inter-key
intervals).

## Attack procedure

1. For each candidate phrase, run the scenario generator (`build_trial` of `../gen/generate_plan.py`, imported and not
   reimplemented) with the known scenario, OS and speed level, and map the resulting key presses to categories with the
   table below. This is the predicted log of the candidate.
2. Apply the same feature transform to the observed log and to every predicted log.
3. Compute the distance between the observed and each predicted log and choose the closest candidate. Ties are broken
   with `random.Random(seed)`.

All candidates are predicted with one shared stream of random draws, so that a difference in draws does not reorder the
candidates. Candidates that cannot be typed in the scenario (for example, a character outside the kana layout in the
kana-input scenario) receive an infinite distance.

### Distance

The distance is an edit distance over tokens. A token is a category with a count and the interval since the previous
token. Insertion and deletion cost the count of the token. A substitution between different categories costs the larger
count. Two tokens of the same category cost the difference of their counts plus a pause penalty. An interval shorter
than `PAUSE_MS` (600 ms) is treated as typing jitter and ignored, because the law of inter-key intervals does not depend
on the phrase. For longer intervals the penalty is `W_TIME` (0.5) times the difference divided by `TAU_MS` (1000 ms),
capped at `W_TIME`. These constants were fixed as part of the design and are not tuned on results.

For the `timing="bin1s"` feature sets (`bin1s`, `bin1s_count`) two further corrections apply, because a 1-second grid
is an artefact of when the observation happened to start, not a property of the phrase:

- **Grid phase.** The grid an observed log's times are floored to is anchored to the (unknown) absolute time of its
  first row, not to any candidate's simulated log. For every candidate, the predicted log is binned at each of ten
  grid phases 0, 100, ..., 900 ms (`PHASES`, step `PHASE_STEP_MS`), and the smallest of the ten distances is kept.
  Searching the phase can only lower a candidate's distance, and it lowers every candidate's distance by a similar
  amount on average, so it is a correction to a systematic source of spurious distance, not an extra source of power
  over an attacker who does not search it -- an attacker with less information could still align on the phase that
  happens to match the true bin boundaries of an observed log it does not know the absolute start time of.
- **Bin-edge discount.** Two tokens a single bin apart can differ by up to one window (1000 ms) purely because of
  where the grid falls, which is not evidence of a real pause. `_gap` therefore discounts one `WINDOW_MS` from an
  interval before judging it against `PAUSE_MS`, for `timing="bin1s"` only.

### Candidates and accuracy

For each trial, `evaluate` builds a candidate set of the typed phrase and K-1 decoys. A decoy is drawn only from
phrases the scenario could actually have produced: the same reading-length range and, for a kana-input scenario (S12),
the same kana-layout-typable characters that the plan generator itself requires when it builds a plan
(`_scenario_pool`, mirroring `plan_rows` of `../gen/generate_plan.py`). A decoy is further excluded when the reading it
would actually type under this scenario and OS (`typed_reading` of `../gen/generate_plan.py`, called through
`_typed_reading`) coincides with the reading the true phrase would actually type: a scenario that only types part of
the reading (S10, the first half) or a synthetic reading (S12) can otherwise make two phrases indistinguishable even
though their full readings differ, which would make an unfair decoy rather than a hard one. Correctness of a trial is
judged the same way, on the typed reading of the chosen candidate against the typed reading of the true one, not on
phrase identity or on the full reading.

A run's accuracy is the fraction of counted trials judged correct this way. It is reported next to the chance level
1/K, with a Wilson 95% interval, a `by_scenario` breakdown (raw accuracy and trial count per scenario), and the mean
rank of the typed phrase. Trials whose phrase is not in the corpus (synthetic kana strings) are not counted and are
reported as `n_skipped`.

The Wilson interval treats every counted trial as an independent Bernoulli draw. The plan generator groups trials into
blocks (`block_id`) that share context (a marker reset, the same run of the generator's random state); trials within a
block are not independent of each other in general, so the reported interval understates the true uncertainty to the
extent trials within a block are correlated. This kit does not implement a block-clustered interval; a numeric
acceptance margin set by the analysis plan should allow for this.

## Feature sets and the removal experiment

| Name | Times | Alphabetic runs |
|---|---|---|
| `all` | exact (ms) | kept |
| `no_time` | removed | kept |
| `no_runs` | exact (ms) | run length removed: one token per run between delimiters |
| `bin1s` | coarsened to 1-second bins | kept |
| `bin1s_count` | 1-second bins | run length removed: one token per run between delimiters |
| `counts_only` | removed | run length removed: one token per run between delimiters |

With `runs="count"`, every maximal run of consecutive alphabetic rows -- a run ends at the next row of a different
category, for example space or punctuation -- is stamped with the time of its first row (so the run collapses to one
token further down the pipeline), regardless of how many 1-second bins the run happens to span; a bin edge inside a
continuous run of letters is not, by itself, a break. Rows of other categories keep their order and times.

`FEATURE_SETS` forms a coarsening order: a feature set G is derivable from a feature set F (an attacker who sees F
could compute the result an attacker restricted to G would get, by discarding timing and/or run detail) exactly when G
is not more detailed than F in either dimension (`coarser_or_equal`). `all` is the finest and dominates every other set;
`counts_only` is the coarsest and dominates only itself. For example, `no_runs` (exact times, run length removed)
dominates both `bin1s_count` (coarsen its times further) and `counts_only` (remove its times further); `bin1s`
(coarsened times, runs kept) dominates `no_time` (remove its bin information further) as well as `bin1s_count` and
`counts_only`.

The raw accuracy of each feature set (`acc_raw`) is reported as measured. A removed feature need not lower it: the
timing feature of this attack compares only long pauses, whose length is drawn independently of the phrase, and
removing detail can leave the raw accuracy unchanged or higher -- an attacker who is given a detailed feature set can
always throw information away and run the attack as if a coarser one had been observed, so a feature set can never be
genuinely safer to publish than any feature set derivable from it. `acc` is therefore the maximum of `acc_raw` over the
feature set and every feature set derivable from it (`acc_source` names which one attained the maximum), and it is
`acc`, not `acc_raw`, that a publication-granularity decision should be read from (see below). The selftest prints both
`acc` and `acc_raw` for all feature sets on its synthetic observations; the order of the feature sets is not rearranged
to fit an expectation.

## Key name to category table

`KEYCAT` in `simulate_obs.py` maps each key name of the generator to a category. It is copied from `from_vk` in
[`../logger/src/key_category.rs`](../logger/src/key_category.rs). The selftest checks it in two ways: against the
virtual-key codes in `VK_OF`, passed through a parser of the match arms of `from_vk` in that source file, and against the
set of key names of the generator. A change in either therefore turns the selftest red.

| Key name | Windows virtual key | Category |
|---|---|---|
| `a` to `z` | 0x41 to 0x5A | `alphabetic` |
| `0` to `9` | 0x30 to 0x39 | `numeric` |
| `space` | 0x20 | `space` |
| `enter` | 0x0D | `enter` |
| `esc` | 0x1B | `escape` |
| `backspace` | 0x08 | `backspace` |
| `tab` | 0x09 | `tab` |
| `left`, `up`, `right`, `down` | 0x25 to 0x28 | `navigation` |
| `minus` | 0xBD | `punctuation` |
| `comma`, `period` | 0xBC, 0xBE | `sentence_punctuation` |
| `shift` | 0xA0 | `modifier` |
| `ime_on`, `ime_off`, `f13` to `f19`, `mouse_click`, `focus_away`, `focus_back` | not observed | no row |

The last row is the one place this assumption about the logger is stated: the IME toggles and F13 to F19 (the
block-start markers) are assumed to lie outside the observed key set of the Windows logger (`is_observed_key`), and the
last three names are pseudo keys of the runner that produce no key event on either OS. This has not been verified
against a logger run; it is to be confirmed in the calibration pilot. The first macOS calibration pilot confirmed it
on macOS: the IME toggles and F13 and F14, the markers sent, produced no row (the macOS logger observes F1 to F12
only, so F15 to F19 cannot produce one either), and of the 4,000 presses inside trials, the 18 without a row were
all IME toggles. Because an unobserved marker cannot
align the observation's clock, the block-start markers are now arrow keys (`left`, `right`, `left`), which are
observed as `navigation`; runs that use them need `--markers-in-obs`. The virtual-key codes of the IME toggles and of
F13 map to `other` in `from_vk`, which is the category `read_obs`/`segment_by_plan` expect from them when a log is found
to include them after all (see `--ime-toggle-in-obs` and `--markers-in-obs` below). If a listed key does produce a row
and neither switch is used, the prediction misses that row for every candidate alike, so the effect on the ranking of
candidates within a scenario is expected to be small (this was not measured). A wrong entry for a key that occurs
inside the reading would weaken the attack, so the table errs on the conservative side.

## Usage

```sh
python3 closed_set.py --obs obs1.ndjson [obs2.ndjson ...] --plan plan1.jsonl [plan2.jsonl ...] \
    --corpus corpus.jsonl --recipes ../gen/recipes.json --config config.json \
    --K 10,100,1000 --seed 1 --out e2_closed.json
```

`--obs` and `--plan` are paired in order. Every observation's header `os` must agree with its plan's header `os`;
otherwise the run stops rather than scoring the pair under the wrong OS's rules. The evaluator supplies the trial
boundaries: the observed presses are cut into trials in plan order, and the number of presses and the category
sequence of every trial must agree with the plan. Otherwise the run stops with exit code 2 and names the trial, and it
never shifts later trials silently. If the block-start marker presses appear in the observation, add
`--markers-in-obs`; if the IME toggle presses (`ime_on`, `ime_off`, as category `other`) appear in the observation, add
`--ime-toggle-in-obs`. Both default to off (see the key table above). `--out` is only ever created, never overwritten;
an existing path is a usage error. Exit codes: 0 success, 2 usage error or unreadable input.

`--recipes` must be the file the plans were built from (the plan header's `recipes_sha256` is the SHA-256 of that
file): for a macOS cell with live conversion off, pass `../gen/recipes.macos-live-off.json`. `closed_set.py`
predicts each candidate's key presses from these procedures, so it compares the SHA-256 of the file passed with
every plan's header and stops with exit code 2 when they differ, rather than building the predictions from the wrong
procedures. (`open_set.py` reads only the kana layout and the typed reading from the recipes, which are the same in
both files, and does not make this comparison.)

The output is one JSON file with `assumptions`, `params` (including `phase_step_ms`), the hashes of the inputs, and
`results[K][feature set]` with `acc`, `acc_ci`, `acc_source`, `acc_raw`, `acc_ci_raw`, `chance`, `n`, `n_skipped`,
`mean_rank` and `by_scenario` (see [Candidates and accuracy](#candidates-and-accuracy) and
[Feature sets and the removal experiment](#feature-sets-and-the-removal-experiment)). The same inputs and seed give
byte-identical output on the same machine and Python version.

On a synthetic world of 1200 candidate phrases and K = 1000, `evaluate` measured about 0.03 s per trial for a feature
set with `timing != "bin1s"` and about 0.11 s per trial for a `timing="bin1s"` feature set (the ten-phase search of the
distance correction above), around 0.15 s per trial for all six feature sets together (one Python process, no
parallelism; see the module docstring of `closed_set.py` for the measurement). This is linear in the number of trials
and does not depend on K beyond building K predicted logs, most of which are shared with other trials of the same
phrase, scenario, speed and OS (`Predictor`'s cache) and computed once. No length-based pruning of the distance is
implemented: at this rate a real run of a few hundred trials finishes in well under a minute, and a lower bound that
skipped exact distances for some candidates would have to be implemented carefully to keep `ranking` and
`rank_of_true`, not only `chosen`, exact for the trials that are not pruned (see the `attack` docstring); it was not
judged worth that risk at the measured speed.

## Scope of the claim

The results are for this attack only. No upper bound on identifiability is claimed. A stronger attacker could use a
language model over candidate readings, estimate the trial boundaries itself, marginalise the window boundaries of the
count features, or combine several trials of the same typist; none of these is included. Giving the attacker the
trial boundaries, the scenario, the OS and the speed level strengthens the attack, and the use of a single predicted
sample per candidate weakens it. The rows of type `ime_shadow` are read but not used: `nav` and `abandon` follow from
the intent of the scenario and not from the phrase, and `dwell_ms` is a function of key times that the timing feature
already uses. The gain of using `dwell_ms` separately was not measured.

If identification succeeds at rates well above chance, the result is reported as it is.

## How the publication-granularity recommendation is derived

The feature sets form a coarsening order (`coarser_or_equal`, see above): `all` is the most detailed, `counts_only` the
coarsest. On the real logs, run the attack for every feature set and every K, and read `acc` -- the maximum, over each
feature set and every feature set derivable from it, of the raw accuracy an attacker would measure -- next to its
Wilson interval (`acc_ci`) and the chance level 1/K; `acc_raw` and `acc_ci_raw` are kept alongside for inspection but
are not the basis of the recommendation, because an attacker who is given a detailed log can always throw information
away, so `acc_raw` alone can understate what publishing that much detail permits. The recommended granularity is the
coarsest feature set whose `acc` is still within the margin above chance that the analysis plan declares acceptable.
The margin is fixed before the real logs are analysed, and should allow for the block-level dependence the Wilson
interval does not (see [Candidates and accuracy](#candidates-and-accuracy)). This kit reports the accuracy, the
interval, `acc_source` and the chance level, and does not decide the margin.

## Verification

```sh
python3 simulate_obs.py --selftest
python3 closed_set.py --selftest
bash ../check.sh
```

The selftest of `closed_set.py` builds a synthetic corpus, plans, and observations with 30 ms of timing perturbation,
over six scenarios including S12 (kana input, decoys constrained by the kana layout) and S10 (only the first half is
typed). It checks the following.

- Positive control: with all features the accuracy exceeds chance (K = 10 and 40, Wilson lower bound above 1/K), and it is
  at least 0.5 at K = 10.
- Negative controls: an observation without information (the same categories and times for every trial, including S12
  trials) and an observation swapped between trials both stay at the chance level, on the raw accuracy, inside a 99%
  Wilson interval.
- The reported accuracy (`acc`) of every feature set is at least the reported accuracy of every feature set derivable
  from it, and at least its own raw accuracy; `acc_source` names a feature set whose raw accuracy equals `acc`.
- `_gap`'s bin1s discount: a one-window interval is not penalised as a pause under `timing="bin1s"`, but the same
  interval is penalised under `timing="exact"`, and a two-window interval is still penalised under `bin1s`.
- Determinism: the same seed gives byte-identical results and a different seed changes them.
- The typed phrase does not influence the choice (passing it changes only the reported rank), and ties are broken by the
  seed.
- A decoy whose typed reading collides with the true phrase's typed reading (for example, two S10 phrases sharing a
  first half) is excluded rather than silently included.
- The observation reader rejects other row types, unknown keys, categories outside the enumeration, a header whose `os`
  is not `macos`/`windows`, a malformed `ime_shadow` row, a duplicate JSON object key and deeply nested JSON (all as
  the same clean error, not an uncaught exception).
- The command line runs end to end, and it stops on a dropped press, on unpaired inputs, on a corpus that is too small,
  on mismatched marker or IME-toggle switches, on an observation/plan `os` mismatch, and on an existing `--out` path
  (which is left untouched).
