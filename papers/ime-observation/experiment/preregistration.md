# Pre-registration: agreement of a content-free observer of Japanese input-method conversion with the input method's own state (macOS cells)

## Status

This is a draft. It is not frozen and no measurement has been made under it. The freeze adds two marks to this
file (see the section on the freeze); until they are present, `run.sh` and `kit/analysis/pipeline.py` refuse to
analyse real data. The cells on Windows are registered in an addendum that is frozen before the first Windows
measurement.

## 1. Study information

### 1.1 Purpose

Keystroke-logging research on Japanese text production has to take account of the input method: a writer types
a reading, the input method converts it, and the writer accepts, changes or abandons the conversion. The observer
under test (`kit/logger`, a stand-alone program) records this process without recording any text. For every key
press it writes one of fourteen key categories and a time; for every conversion session it writes one summary row
with the session's duration (`dwell_ms`), the number of arrow-key presses during the session (`nav`) and whether
the session was abandoned (`abandon`). No character, reading, candidate string or window name is written.

On macOS no public interface reports the conversion state of another application, so the observer infers each
session from key presses while Japanese input is active. A session opens at the first letter or digit key, is
closed as committed by Return, by any key other than a letter, digit, space, backspace, arrow or input-mode key,
or by a change to non-Japanese input, and is closed as abandoned by Escape. Space marks a candidate window as
shown; backspace and arrow keys keep the session open. A session that reaches 20 seconds is cut off and produces
no row.

This study estimates how closely those rows agree with the input method's own state, recorded at the same time by
a reference input field, under scripted input whose intent is known. It also estimates how much of the typed text
can be recovered from a published log, and what the observer costs the machine.

### 1.2 Questions

The study estimates; it tests no hypothesis. Every estimate is reported with an interval, and none is turned into
a pass or fail decision, except the margin of the text-recoverability study, which decides which log granularity
is recommended (section 6.6).

1. Detection. What fraction of the input method's conversion sessions does the observer report as one row
   (recall), and what fraction of the observer's rows correspond to one session (precision)? How often does the
   observer split one session into several rows, or merge several sessions into one?
2. Per-session agreement. For sessions the observer reports as one row, how does `dwell_ms` differ from the
   session's duration, how often does `abandon` agree with the session's outcome, and how often does `nav` equal
   the number of arrow keys pressed during the session? Does the observer produce no row for sessions of 20
   seconds or longer, as specified?
3. Per-text agreement. When trials are grouped into texts, do four aggregates a writing researcher computes
   (number of conversions, mean conversion time, abandonment rate, fraction of time spent converting) agree
   between the observation and the ground truth?
4. Text recoverability. Given only a published log, how accurately can an attacker identify which of K candidate
   phrases was typed, and how far can an attacker with a language model reconstruct the typed reading? Which
   granularity of the published log keeps identification near chance?
5. Runtime cost. What CPU time and resident memory does the observer use while the machine is idle and while
   synthetic typing is played?

The scripted input also allows a check of the instruments themselves: for each trial, whether the input method
did what the plan intended (one session, committed or cancelled as planned). This is reported (section 6.3) and
is not used to remove trials from the evaluation.

### 1.3 Scope of this registration

This registration covers two cells on macOS: the standard Japanese input method with live conversion on, and the
same input method with live conversion off. It covers the agreement analyses of questions 1 to 3 for these
cells, question 4 on their observation logs, and question 5 on macOS.

Not covered here, and registered in an addendum before any measurement if they are carried out: the Windows cells
(the standard Microsoft input method is planned), any cell with another input method, and a check of the same
scenarios in an application other than the reference input field.

## 2. Design

### 2.1 Type of study

A method-validation study with synthetic input only. No person takes part and no person's typing is recorded. All
key presses are generated from a plan and sent by a program.

### 2.2 System under test and instruments

- **Observer** (`kit/logger`). The program under test. For the measurement it is built from an export of this
  directory made at the freezing commit; the SHA-256 of its manifest is written into the header of every log it
  produces (`manifest_sha256`), so that each log can be tied to the published code.
- **Reference input field** (`kit/refinput-macos`). A minimal application that implements the text-input client
  protocol of the macOS text system and records, with wall-clock and monotonic times, every call the input method
  makes: marked text set (with its length), text inserted (with its length), marked text accepted, a request for
  the position of the text, a command, and each key-down it receives (key code only). No text is recorded. It
  empties its text after every commit, so that no trial sees the text of an earlier one.
- **Executor** (`kit/emit`). Sends the planned key presses as system key events and records each press as sent
  (the oracle), with wall-clock and monotonic times taken immediately before dispatch. It refuses to start if
  either clock resolves more coarsely than 1 ms.
- **Runner** (`kit/run/run_cell.py`). Starts the reference input field and the observer, and before every block
  brings the reference input field to the front, confirms that it is in front, and switches the input method to
  Japanese. It then sends the block, and after the last block keeps both programs running for `settle_ms`
  (1,000 ms) before stopping them, so that the 50 ms window of the ground-truth rule (section 4.3) is observed
  after the last commit. A run is aborted if the front-window check fails or if either program stops.

### 2.3 Factors

- **Cell**: live conversion on, live conversion off. Each cell has its own procedure file:
  `kit/gen/recipes.json` (on) and `kit/gen/recipes.macos-live-off.json` (off). They differ only where live
  conversion changes how the input method responds to Return and Escape.
- **Scenario**: S1 to S15 (table below). S9 (choosing a candidate with the mouse) has no procedure, because no means
  of locating the candidate window for a scripted click was established; it is not run and is reported as not
  evaluated. S11 (conversion without Space under live conversion) is run only with live conversion on. A cell
  therefore has 14 scenarios (on) or 13 (off).
- **Speed**: three levels of the interval between key presses (section 3.3).
- **Think time**: in scenarios with a pause before the decisive key, the pause is drawn per trial from a
  log-uniform distribution between 0.2 and 20 seconds. It is a continuous covariate, not a factor.

| Scenario | Procedure (live conversion on) |
|---|---|
| S1 | Type the reading, Space, pause, Return twice (commit) |
| S2 | Type the reading, Space two to five times (cycling the candidates), pause, Return twice |
| S3 | Type the reading, Return (commit without conversion) |
| S4 | Type the reading, Space, pause, Escape twice (cancel with the candidate window shown) |
| S5 | Type the reading, Escape four times (cancel without conversion) |
| S6 | Type the reading, Backspace once per kana typed (delete everything) |
| S7 | Type the reading, Space, right arrow one to three times, pause, Return twice |
| S8 | Type the reading, Space twice, pause, a digit choosing a candidate, Return |
| S10 | Type the first half of the reading, Tab (a predictive candidate), pause, Return |
| S11 | Type the reading, Return (live conversion converts without Space) |
| S12 | Type a kana string with the kana keyboard layout, Space, Return twice |
| S13 | Type the reading, Space, wait 21 seconds, Return twice (a session over 20 seconds) |
| S14 | Type the reading, Space, switch the input mode off and on |
| S15 | Type the reading, Space, bring another application to the front for one second, return, Return twice |

With live conversion off, a single Return commits and a single Escape cancels without conversion, so S1, S5, S7,
S12, S13 and S15 use one Return or one Escape where the table shows two or four. These procedures were fixed in
the calibration pilot (section 3.1).

### 2.4 Plans and randomisation

Each cell has one plan, generated by `kit/gen/generate_plan.py` from the settings in
`experiment/plan_config.macos.json`, the cell's procedure file, the phrase corpus `kit/corpus/data/phrases.jsonl`
(SHA-256 `c8f890cb4d0848bf04e6d7d95efe4e4d3dfd02a23eb1c7f103344f14d13e4620`) and the seed in `experiment/SEED`
(20260929):

    python3 kit/gen/generate_plan.py --config experiment/plan_config.macos.json \
      --recipes kit/gen/<procedure file of the cell> --corpus kit/corpus/data/phrases.jsonl \
      --os macos --seed 20260929 --out <plan>

A block holds 25 trials of one speed. The order of trials within each speed, the cut into blocks, the order of
blocks and the order of scenarios within a block are all determined by the seed, and each trial draws its phrase,
key intervals, think time, candidate index and arrow count from a random state derived from the seed and the
trial identifier. The plan records the SHA-256 of the settings, procedure and corpus files it was built from. The
plan is generated on the measuring machine; its SHA-256 is recorded in the run manifest.

### 2.5 Blinding

The observer's session rows of the calibration pilot were never read. Before any analysis of the pilot, each
observation log was split into its key rows, which were analysed, and its session rows, which were written to a
sealed file padded to a multiple of 1 MiB (`kit/pilot/seal_obs.py`), so that not even their number could be
inferred; the sealed files were not opened. The ground-truth definition, the procedures, the analysis code and
the analysis settings were all fixed without reference to any session row of the observer. No session row of the
measurement is read before the freeze.

## 3. Sampling plan

### 3.1 Data that exist before the freeze

A calibration pilot was run on the measuring machine before the freeze; it is reported in
`experiment/pilot-macos.md`, and its raw logs will be deposited with the measurement data after the check that
report describes. Its runs used provisional
settings (three trials per scenario and speed). Only the reference side was analysed: the reference input field's
calls, the oracle, the plan, and the key rows of the observation. The following were computed from it and
informed this protocol:

- the call sequences the reference input field receives in each scenario, from which the ground-truth rule of
  section 4.3 was fixed (in particular the 50 ms continuation window for live conversion);
- the agreement between the plan and the ground-truth sessions (124 of 126 trials with live conversion on, 117 of
  117 with it off, 39 of 39 with the procedure file for live conversion off), from which the procedures were
  revised and the carry-over exclusion (section 6.2) was defined;
- the clock differences between the observation, the reference input field and the executor at the block-start
  markers;
- the fraction of sent key presses that produced a key row in the observation (4,072 of 4,090 and 3,972 of 3,990;
  the missing presses were the input-mode keys, which the observer does not record by design);
- the time per trial, from which the number of trials was set.

No session row of the observation was read, no agreement between the observation and the ground truth was
computed, and no text-recoverability or runtime analysis was run on pilot data.

### 3.2 Data collection

Each cell is measured in one run on the measuring machine (Apple Silicon, macOS 27.0 or the version recorded in
`experiment/env.md`, JIS keyboard, Romaji input). The machine runs on mains power, with automatic updates, network
time synchronisation, sleep, screen lock and the screen saver turned off. The input method's predictive candidates
are left at their default (shown). The input method's learning is not reset: no method of resetting it was found,
and the plans request no reset. The run manifest records the system and input-method versions and these settings.

Before each block the runner switches the input method to Japanese by pressing the kana key, after confirming that
the reference input field is in front. A block begins with a marker of four arrow presses (left, right, left,
right), 150 ms apart, which both logs record and which is used to measure the clock differences; it is longer than
the longest run of arrow presses inside any trial, so it cannot be confused with one. Trials are separated by 1,000
ms.

### 3.3 Sample size and settings of the plan

- **Trials**: 75 per cell, scenario and speed: 3,150 trials with live conversion on and 2,925 with it off. The
  generator estimates 11.9 and 11.2 hours per run (13.6 and 13.8 seconds per trial, including waits and markers;
  the estimate leaves out the start of each block). In the pilot the measured time per trial (11.0 seconds with
  live conversion on, 11.9 with it off) was close to the generator's estimate for the pilot's key intervals (11.2
  and 11.4 seconds). Near a proportion of 0.95 the half-width of a 95% Wilson interval is about 5.3 percentage
  points with 75 trials (6.0 with 60, 6.6 with 50). The number was chosen so that each run fits in one night.
- **Key intervals**: log-normal, with medians of 480 ms (slow), 240 ms (middle) and 120 ms (fast) and a log-scale
  standard deviation of 0.3. The medians follow the per-participant mean inter-key intervals that Dhakal, Feit,
  Kristensson and Oulasvirta (2018) report for the slowest tenth of their participants (481 ms), for all
  participants (239 ms) and for the fastest tenth (122 ms). Those values come from transcription typing of English
  sentences; they are used to span the range of typing speeds, not as estimates of Japanese typing. With a
  log-scale standard deviation of 0.3 the mean interval is about 4.6% above the median. The spread is a design
  choice that makes intervals vary; it is not estimated from data. An interval shorter than the key hold plus 1 ms
  (61 ms) is raised to it, which affects about 1% of the intervals of the fast level.
- **Key hold**: 60 ms from key-down to key-up. The generator never overlaps two presses, so the hold must stay below
  the shortest intervals of the fast level; the input method acts on key-down, and key-up times are not part of
  any measure.
- **Other settings**: candidate index up to 4 (S2, S8), up to three arrow presses (S7), kana strings of four to
  eight characters (S12).

### 3.4 Stopping rule

Each cell is run once to completion. If a run is aborted (the runner stops it), the cell is run again from the
start with the same plan, in a new run directory, up to three attempts. Aborted runs are reported with their
reason and are not analysed. A cell that is not completed in three attempts is reported as not measured.

## 4. Variables

### 4.1 Manipulated

Cell, scenario and speed (section 2.3); think time varies within scenarios as a covariate.

### 4.2 Recorded

- The plan (`plan.jsonl`): every trial's scenario, speed, phrase, intent and key schedule.
- The oracle (`oracle.jsonl`): every press as sent, the block markers, and each trial's begin and end.
- The ground-truth log (`gt.jsonl`): the reference input field's calls (kinds, lengths and times only).
- The observation (`obs.jsonl`): key rows (category and time) and session rows (`t`, `dwell_ms`, `nav`,
  `abandon`).
- The run manifest (`run.json`): the cell settings, the SHA-256 and line count of every log, the system and
  program versions, and the outcome of every front-window check.

### 4.3 Ground-truth sessions

Sessions are assembled from the reference input field's log by `kit/analysis/gt_sessions.py` with the `mac_nstic`
rules of `experiment/gt_rules.json`:

- A session opens at the first call that sets marked text of positive length.
- It closes as committed at a call that inserts text of positive length, or that accepts the marked text, when no
  call setting marked text of positive length follows within 50 ms.
- It closes as cancelled at a call that sets marked text of length zero, when no call inserting text of positive
  length follows within 50 ms.

With live conversion the input method commits the head of a reading while the rest is still being typed; the
50 ms window keeps such a commit inside its session (in the pilot the following call came 0.5 to 7.9 ms later,
and every window between 10 and 900 ms gave the same sessions). The outcome of a session is the reason it finally
closed; a session whose head was committed this way and whose rest was cancelled is a cancellation. Each session
also records how many commits were followed by a continuation (`n_continued_commits`).

A session is assigned to the trial it overlaps most in wall-clock time. Its true navigation count is the number of
arrow presses the oracle records as sent for that trial within the session. A session is reported as lasting 20
seconds or more when its duration reaches 20,000 ms.

### 4.4 Observation intervals

A session row's interval is `[t - dwell_ms, t]` on the wall clock. No offset is added at either end, and no
clock correction is applied (section 6.8).

### 4.5 Texts

For the per-text measures, the trials of each block are cut, in plan order, into texts of eight consecutive
trials; the remainder of a block (one trial with blocks of 25) is not used. Every text is of one speed. The four
measures are computed for every text on both sides: the number of conversions (sessions or rows), the mean
conversion time (total duration over the sessions or rows with a non-zero duration), the abandonment rate
(cancelled sessions, or rows with `abandon` set, over all), and the fraction of time spent converting (total
duration over the time from the first trial's begin to the last trial's end).

## 5. Analysis code and settings

The whole analysis of questions 1 to 3 is run by one command, `bash experiment/run.sh`, which reads the run
directories listed in `experiment/data.md`. The analysis code is fixed by the tag of the freezing commit. The
settings are in `experiment/config.json`: overlap criterion `iou_min` = 0.5, observation end offset 0 ms,
`theta` = 0.5, sessions with a start inside an open session not dropped, texts of 8 trials, 2,000 bootstrap
resamples, cut-off limit 20,000 ms, and three mixtures of speeds for the mixture analysis. The ground-truth rules
are in `experiment/gt_rules.json` and the seed in `experiment/SEED`. Before any statistic, the pipeline checks the
freeze marks, the SHA-256 of every log against its manifest, the content-free format of every log, and that the
observation declares both of its channels.

Every analysis is repeated under two session definitions: the definition of the cell's system (`macos_def`) and
the definition common to both systems (`all`). On the reference side of a macOS cell they hold the same sessions.

## 6. Analysis plan

### 6.1 Units and intervals

The primary estimates are given per stratum: cell, scenario and speed. Estimates pooled over scenarios weight
them equally and are labelled as such; because synthetic input has no natural mix of scenarios, a pooled value is
not an estimate of accuracy in natural typing. Proportions carry 95% Wilson intervals (Wilson, 1927). Continuous
measures carry 95% percentile bootstrap intervals (Efron, 1979) that resample whole blocks (Cameron, Gelbach, &
Miller, 2008), because trials in one block share the state of the input method. All resampling uses the seed in
`experiment/SEED`.

### 6.2 Exclusions

Applied before matching, and reported by reason, stratum and number:

- `clock_jump`: two adjacent events of the reference or oracle log whose wall-clock and monotonic differences
  disagree by more than 1,000 ms. The affected trials, from the jump to the end of its block, are excluded.
- `log_truncated`: a session still open when the log ends.
- `carry_over`: a session that overlaps two or more trials. The composition was not closed in its own trial and
  ran on into the next, so every trial it overlaps is excluded (in the pilot, 2 of 126 trials with live conversion
  on, in S8 and S10).
- Observation rows are assigned to the trial they overlap most and are excluded with that trial.
- Aborted runs (section 3.4).

Not excluded: trials in which the input method did not do what the plan intended (they are counted, section
6.3); sessions in which a start arrived while a session was open (counted); observation rows with `dwell_ms` equal
to zero, which the observer produces when the wall clock steps back (they stay in the matching as intervals of
zero length, so they count as false positives, and their number is reported in every bucket).

### 6.3 Plan versus ground truth

For every trial, the assembled sessions are compared with the plan's intent and classified as agreeing or as one
of the disagreement types (no session, an unexpected session, several sessions, a commit where a cancellation was
planned, a cancellation where a commit was planned, a session open at the end). The counts and rates are reported
with Wilson intervals, per stratum and overall. These trials stay in the evaluation: removing them would keep only
the trials in which the input method behaved as planned.

### 6.4 Question 1: detection

Sessions and observation rows are matched one to one in descending order of interval overlap (intersection over
union) among the pairs that reach 0.5. Among the items left unmatched, one session with two or more rows whose
combined interval reaches the criterion is a split, and one row with two or more sessions is a merge; the rest
are misses and false positives. Because a fragment that reaches the criterion on its own becomes a one-to-one pair,
the split and merge rates are then recounted: an unmatched row whose length lies at least half (`theta`) within a
matched session counts toward a split, and an unmatched session lying at least half within a matched row counts
toward a merge. The primary pairing is not changed by the recount.

Reported per stratum: recall (pairs over sessions), precision (pairs over rows), split rate, merge rate, miss
rate and false-positive rate, each with a Wilson interval, and F1 without an interval.

### 6.5 Question 2: per-session agreement

Over the one-to-one pairs of each stratum:

- **Duration**: the error is `dwell_ms` minus the session's duration. Reported: the median absolute error with a
  bootstrap interval, and the Bland-Altman bias with a bootstrap interval and 95% limits of agreement (Bland &
  Altman, 1986). Pairs whose `dwell_ms` is zero are left out of these figures and counted.
- **Abandonment**: the session's outcome (cancelled or not) against the row's `abandon` flag. Reported: the 2 by 2
  table, the raw agreement with a Wilson interval, and Cohen's kappa (Cohen, 1960). The same figures are reported
  separately for sessions with and without a commit followed by a continuation (`n_continued_commits` greater than
  zero, or zero), as a diagnostic: with live conversion on, about 4 in 10 cancellations in the pilot followed such
  a commit. This split does not replace the main figure.
- **Navigation**: the exact-agreement rate of `nav` with the true count, with a Wilson interval, and the
  distribution of the difference.
- **Cut-off**: the number of sessions of 20 seconds or more that nonetheless appear in a pair, split or merge, and
  the number of rows of 20 seconds or more; the specified behaviour is zero for both.

### 6.6 Question 3: per-text agreement

For each of the four measures of section 4.5 and each speed: the Bland-Altman bias and limits of agreement of the
per-text difference (observation minus ground truth), and the intraclass correlation ICC(2,1) for absolute
agreement (Shrout & Fleiss, 1979; McGraw & Wong, 1996) with a 95% interval from resampling blocks (the texts of a
block form one cluster). The interval is withheld, with the reason, when the ICC is undefined in the sample or in
any resample. The per-speed values are primary; values pooled over speeds are reported for comparison, because a
difference in level between speeds inflates a pooled ICC. A text is not used if any of its trials was not run or
was excluded; the numbers of such texts are reported by reason, block and speed. The bias of each measure is also
reported for three mixtures of speeds (slow, middle and fast in proportions 0.6/0.3/0.1, equal, and 0.1/0.3/0.6)
to show whether the aggregate's bias moves with the mix.

### 6.7 Question 4: text recoverability

Run on the observation logs of each cell separately, with the plan, procedure file and settings that built them
(the attack refuses a mismatch). Block markers are recorded by the observer and are declared to the attack
(`--markers-in-obs`); input-mode switches are not recorded on macOS and are not declared. The ground truth is the
reading that was typed, not the original sentence. The attacker sees what a published log holds: the category and
time of every key row, and the session rows.

**Closed set.** For each trial the attacker is given K candidate phrases, the true one and K - 1 decoys drawn from
the phrases the trial's scenario could have produced (excluding phrases with the same typed reading), and knows
the scenario, the system, the speed level, the generator, the procedures and the settings. For each candidate it
generates the expected log with the same generator and chooses the candidate whose expected log is closest to the
observed one. K is 10, 100 and 1,000; the seed is the one in `experiment/SEED`.

    python3 kit/e2/closed_set.py --obs <obs> --plan <plan> --corpus kit/corpus/data/phrases.jsonl \
      --recipes kit/gen/<procedure file of the cell> --config experiment/plan_config.macos.json \
      --K 10,100,1000 --seed 20260929 --markers-in-obs --out results/e2_closed_set_<cell>.json

The attack is repeated for six feature sets that remove information from the log: exact times and run lengths
(`all`), no times (`no_time`), no lengths of letter runs (`no_runs`), times in 1-second bins (`bin1s`), 1-second
bins without run lengths (`bin1s_count`), and neither (`counts_only`). An attacker given a detailed log can always
discard information, so the accuracy reported for a feature set is the maximum over that set and every coarser set
derivable from it. Reported: the accuracy with its Wilson interval, the chance level 1/K, the mean rank of the true
phrase, and the accuracy per scenario. A trial whose phrase is a generated kana string (S12) is not counted.

The accuracy of a feature set is **near chance** at a given K when the upper end of its 95% Wilson interval is at
most 2/K. The recommended granularity for publishing logs is, at each K, the most detailed feature sets that are
near chance (the maximal elements, in the coarsening order, of the near-chance sets; the order is partial, so there
may be more than one). If no feature set is near chance at some K, no granularity is recommended for that K and this
is reported. The Wilson interval treats trials as independent although trials of one block share context; judging
by the upper end allows for part of this, and the remainder is stated as a limitation.

**Open set.** The attacker sees only the categories of the key presses and, with a character language model,
searches for the kana string that the romanisation would spell with exactly the observed letter keys and the
observed punctuation, maximising its probability. Two knowledge levels are reported: K0, a character unigram model,
and K1, a character trigram model with Witten-Bell smoothing (Witten & Bell, 1991) trained on the corpus with the
evaluation phrases' whole works held out. Whole works, in an order drawn with the seed in `experiment/SEED`, are
held out for evaluation until they hold at least a fifth of the phrases (three of the twelve works of this corpus),
and a training phrase with the same reading as an evaluation phrase is removed. A stronger attacker, K1+, for which
the corpus is split by phrase instead of by work, is reported alongside K1. The baseline is the same model without the log, drawing a string from its prior, either
knowing only the number of segments or given the true length (both are reported).

    python3 kit/e2/open_set.py --obs <obs> --plan <plan> --corpus kit/corpus/data/phrases.jsonl \
      --recipes kit/gen/<procedure file of the cell> --split-seed 20260929 --seed 20260929 \
      --eval-fraction 0.2 --split both --n 3 --smoothing wb --beam 8 --length-info both \
      --bootstrap 1000 --markers-in-obs --out results/e2_open_set_<cell>.json

Reported: the character error rate of the attack and of the baseline, their paired difference (`gain`), and the
difference from a negative control in which each trial is decoded from another trial's observation
(`gain_vs_shuffled`), each with a block-clustered percentile bootstrap interval. Kana-input trials (S12) are
excluded. Neither attack is claimed to be the strongest possible; the results hold for these attacks.

### 6.8 Clock differences

The per-block differences between the observation, the reference input field and the executor are measured at
the block-start markers with `kit/pilot/clock_sync.py` for every run and reported (median, range, drift per hour
and per-block values). They are not used to correct the matching: the duration error is a difference of durations
and does not depend on them, and a session is still paired as long as the offset stays at or below a third of its
length (in the pilot the largest difference between the observation and the reference was 22 ms).

### 6.9 Question 5: runtime cost

Measured with `kit/e3` under two conditions, one night each, for eight hours at a 30-second interval: `idle` (the
observer runs and nothing operates the machine) and `working` (the observer runs while the runner plays the plan of
the cell with live conversion on). Reported for each condition: the mean, median, 95th percentile and maximum of the
observer's CPU (one core is 100%), its final resident memory and the least-squares slope of its resident memory in
MB per hour. A condition with fewer than 480 usable samples or a window shorter than four hours is reported as
insufficient. The two conditions are always reported together and never reduced to one figure. Battery use is not
measured.

### 6.10 Missing data

A stratum with no pair, a measure that cannot be computed (no session, zero variance, fewer than two blocks) and an
interval that cannot be formed are reported as null with the reason, never as zero. Trials of a plan that were not
run are reported by stratum.

### 6.11 Exploratory analyses

Any analysis not described here (for example, the dependence of the duration error on think time, or comparisons
between the two cells) is reported as exploratory.

## 7. Deviations and addenda

Any departure from this registration after the freeze is recorded in `experiment/deviations.md` with its date,
reason and effect before the affected analysis is run, and is reported in the paper.

The Windows addendum may change only the Windows blocks of `experiment/gt_rules.json` and its own section of this
file. When it is frozen it replaces the two freeze marks; that `experiment/config.json`, `experiment/SEED`, the
macOS block of the rule file and the macOS sections of this file are unchanged is shown by the difference between
the two freezing tags and stated in the addendum. The addendum is registered before the first Windows measurement.

## 8. Freeze

The freeze adds to this file two lines outside comments and code fences: one starting with `frozen_at:` followed by
the date, and one starting with `sha256:` followed by 64 lowercase hexadecimal digits. The latter is the value that

    python3 kit/analysis/pipeline.py --freeze-hash --config experiment/config.json --seed-file experiment/SEED

prints: the SHA-256 of the SHA-256 of `config.json`, of `SEED` and of `gt_rules.json`, in this order, each
followed by a line feed. The freezing commit is tagged. The frozen file is registered on OSF Registries with the
two marks and the SHA-256 of the list of files exported from the freezing commit, and the registration is public.
The URL and date of the registration are recorded in `experiment/notes.md`. The registration date precedes the
first measurement run.

The settings of the plan generator (`experiment/plan_config.macos.json`), the procedure files and the corpus are
not part of the hash; they are fixed by the freezing tag, and every plan records their SHA-256.

## References

Bland, J. M., & Altman, D. G. (1986). Statistical methods for assessing agreement between two methods of clinical
measurement. *The Lancet, 327*(8476), 307-310. https://doi.org/10.1016/S0140-6736(86)90837-8

Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2008). Bootstrap-based improvements for inference with clustered
errors. *The Review of Economics and Statistics, 90*(3), 414-427. https://doi.org/10.1162/rest.90.3.414

Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement,
20*(1), 37-46. https://doi.org/10.1177/001316446002000104

Dhakal, V., Feit, A. M., Kristensson, P. O., & Oulasvirta, A. (2018). Observations on typing from 136 million
keystrokes. In *Proceedings of the 2018 CHI Conference on Human Factors in Computing Systems* (Paper 646).
https://doi.org/10.1145/3173574.3174220

Efron, B. (1979). Bootstrap methods: Another look at the jackknife. *The Annals of Statistics, 7*(1), 1-26.
https://doi.org/10.1214/aos/1176344552

McGraw, K. O., & Wong, S. P. (1996). Forming inferences about some intraclass correlation coefficients.
*Psychological Methods, 1*(1), 30-46. https://doi.org/10.1037/1082-989X.1.1.30

Shrout, P. E., & Fleiss, J. L. (1979). Intraclass correlations: Uses in assessing rater reliability. *Psychological
Bulletin, 86*(2), 420-428. https://doi.org/10.1037/0033-2909.86.2.420

Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the
American Statistical Association, 22*(158), 209-212. https://doi.org/10.1080/01621459.1927.10502953

Witten, I. H., & Bell, T. C. (1991). The zero-frequency problem: Estimating the probabilities of novel events in
adaptive text compression. *IEEE Transactions on Information Theory, 37*(4), 1085-1094.
https://doi.org/10.1109/18.87000
