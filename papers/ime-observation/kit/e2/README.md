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
capped at `W_TIME`. These three constants were fixed as part of the design and are not tuned on results.

### Candidates and accuracy

`evaluate` builds, for each trial, a candidate set of the typed phrase and K-1 phrases drawn from the corpus with
readings that differ from the typed reading and from each other. Accuracy is the fraction of trials in which the chosen
candidate is the typed phrase. It is reported with a Wilson 95% interval and next to the chance level 1/K. The mean rank
of the typed phrase is reported as well. Trials whose phrase is not in the corpus (synthetic kana strings) are not
counted and are reported as `n_skipped`. The correct answer is the typed reading, not the original text of the phrase.

## Feature sets and the removal experiment

| Name | Times | Alphabetic runs |
|---|---|---|
| `all` | exact (ms) | kept |
| `no_time` | removed | kept |
| `no_runs` | exact (ms) | run length removed: only the count per 1-second window is kept |
| `bin1s` | coarsened to 1-second bins | kept |
| `bin1s_count` | 1-second bins | count per 1-second window only |
| `counts_only` | removed | one count for the whole trial |

With `runs="count"` the alphabetic keys of a window are moved to the position of the first alphabetic key of that window
and stamped with the start of the window, so neither the order nor the exact times inside the window remain. Rows of
other categories keep their order and times.

The values are reported as measured. A removed feature need not lower the accuracy: the timing feature of this attack
compares only long pauses, whose length is drawn independently of the phrase, and removing it can leave the accuracy
unchanged or slightly higher. The selftest prints the accuracies of all feature sets on its synthetic observations so
that this can be seen; the order of the feature sets is not rearranged to fit an expectation.

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

The last row is an assumption about the logger that has not been verified against a logger run: the IME toggles and
F13 to F19 are assumed to lie outside the set of keys the logger reports, and the last three names are pseudo keys of
the runner that produce no key event. The virtual-key codes of the IME toggles and of F13 map to `other` in `from_vk`.
The assumption is to be confirmed in the calibration pilot. If a listed key does produce a row, the prediction misses that
row for every candidate alike, so the effect on the ranking of candidates within a scenario is expected to be small
(this was not measured). A wrong entry for a key that occurs inside the reading would weaken the attack, so the table
errs on the conservative side.

## Usage

```sh
python3 closed_set.py --obs obs1.ndjson [obs2.ndjson ...] --plan plan1.jsonl [plan2.jsonl ...] \
    --corpus corpus.jsonl --recipes ../gen/recipes.json --config config.json \
    --K 10,100,1000 --seed 1 --out e2_closed.json
```

`--obs` and `--plan` are paired in order. The evaluator supplies the trial boundaries: the observed presses are cut into
trials in plan order, and the number of presses and the category sequence of every trial must agree with the plan.
Otherwise the run stops with exit code 2 and names the trial, and it never shifts later trials silently. If the
block-start marker presses appear in the observation, add `--markers-in-obs`. Exit codes: 0 success, 2 usage error or
unreadable input.

The output is one JSON file with `assumptions`, `params`, the hashes of the inputs, and `results[K][feature set]` with
`acc`, `acc_ci`, `chance`, `n`, `n_skipped` and `mean_rank`. The same inputs and seed give byte-identical output on the
same machine and Python version.

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

The feature sets are ordered from the most detailed log to progressively coarser logs. On the real logs, run the attack
for every feature set and every K, and compare the accuracy and its Wilson interval with the chance level 1/K. The
recommended granularity is the coarsest feature set at which the accuracy is still within the margin above chance that
the analysis plan declares acceptable. The margin is fixed before the real logs are analysed. This kit reports the
accuracy, the interval and the chance level, and does not decide the margin.

## Verification

```sh
python3 simulate_obs.py --selftest
python3 closed_set.py --selftest
bash ../check.sh
```

The selftest of `closed_set.py` builds a synthetic corpus, plans, and observations with 30 ms of timing perturbation. It
checks the following.

- Positive control: with all features the accuracy exceeds chance (K = 10 and 40, Wilson lower bound above 1/K), and it is
  at least 0.5 at K = 10.
- Negative controls: an observation without information (the same categories and times for every trial) and an
  observation swapped between trials both stay at chance (1/K inside a 99% Wilson interval).
- Determinism: the same seed gives byte-identical results and a different seed changes them.
- The typed phrase does not influence the choice (passing it changes only the reported rank), and ties are broken by the
  seed.
- The observation reader rejects other row types, unknown keys and categories outside the enumeration.
- The command line runs end to end, and it stops on a dropped press, on unpaired inputs and on a corpus that is too small.
