# Pre-registration: agreement between an observer of Japanese input-method conversion that records no text and the input method's own calls (macOS cells)

## Status

This is a draft. It is not frozen and no measurement has been made under it. The freeze adds two marks to this
file (see section 9); until they are present, `run.sh` and `kit/analysis/pipeline.py` refuse to analyse real data.
The cells on Windows are registered in an addendum that is frozen before the first Windows measurement (section 8).

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
shown; backspace and arrow keys keep the session open. A session is cut off, without a row, at the first key press
that comes 20 seconds or more after it opened; that press then starts afresh, so a letter or digit opens a new
session.

This study estimates how closely those rows agree with the sessions assembled, by the rule of section 4.3, from
the calls that a reference input field received from the input method at the same time, under scripted input whose
intent is known. Because the observer's rules are deterministic, the rows it is specified to write can be computed
from the presses that were sent; this prediction (section 4.5) is used to separate the disagreements that follow
from the rules from those that follow from carrying them out (section 6.4). The study also estimates how much of the
typed text can be recovered from a published log, and what the observer costs the machine.

### 1.2 Questions

The study estimates; it tests no hypothesis. Every proportion and every continuous estimate is reported with an
interval; F1 and the counts are reported without one (section 6.1). No estimate is turned into a pass or fail
decision, except the near-chance rule of the text-recoverability study, which decides which log granularity is
recommended (section 6.8).

1. Detection. What fraction of the sessions assembled from the reference input field does the observer report as
   one row (recall), and what fraction of the observer's rows correspond to one session (precision)? How often does
   the observer split one session into several rows, or merge several sessions into one?
2. Per-session agreement. For sessions the observer reports as one row, how does `dwell_ms` differ from the
   session's duration, how often does `abandon` agree with the session's outcome, and how often does `nav` equal
   the number of arrow keys pressed during the session? For the trials whose session reaches the 20-second cut-off,
   does the observer write no row for that session, as specified?
3. Per-text agreement. When trials are grouped into texts, how closely do four aggregates a writing researcher
   might compute (number of conversions, mean conversion time, abandonment rate, fraction of time spent converting)
   agree between the observation and the ground truth?
4. Text recoverability. Given only a published log, how accurately can an attacker identify which of K candidate
   phrases was typed, and how far can an attacker with a language model reconstruct the typed reading? Which
   granularity of the published log keeps identification near chance?
5. Runtime cost. What CPU time and resident memory does the observer use while the machine is idle and while
   synthetic typing is played?

Questions 1 and 2 are answered for the trials whose session the observer's rules do not cut off; the trials whose
session they do cut off are examined separately (section 6.4). The scripted input also allows checks of the
instruments themselves, which are reported and are not used to remove trials from the evaluation: for each trial,
whether the input method did what the plan intended (one session, committed or cancelled as planned; section
6.3), and for each key press, whether and when it reached the observation and the reference input field (section
6.3).

### 1.3 Scope of this registration

This registration covers two cells on macOS: the standard Japanese input method with live conversion on, and the
same input method with live conversion off. It covers the agreement analyses of questions 1 to 3 for these cells,
question 4 on their observation logs, and question 5 on macOS.

An addendum, registered and frozen before any Windows measurement, may add the Windows cells (the standard
Microsoft input method is planned) and question 5 on Windows; nothing else is added by addendum (section 8).
Other input methods, and applications other than the reference input field, are outside this study: each would
need its own procedures and ground-truth rules, calibrated in a pilot of its own, and would answer a different
question (whether the agreement transfers), which is left to a separate study.

## 2. Design

### 2.1 Type of study

A method-validation study with synthetic input only. No person takes part, and no person's typing is part of the
data. All key presses of the measurement are generated from a plan and sent by a program.

### 2.2 System under test and instruments

- **Observer** (`kit/logger`). The program under test. For the measurement it is built from an export of this
  directory made at the freezing commit; the SHA-256 of its manifest is written into the header of every log it
  produces (`manifest_sha256`), so that each log can be tied to the published code.
- **Reference input field** (`kit/refinput-macos`). A minimal application that implements the text-input client
  protocol of the macOS text system and records, with wall-clock and monotonic times, every call the input method
  makes: marked text set (with its length), text inserted (with its length), marked text accepted, a request for
  the position of the text, a command, each key-down it receives (key code only), and each change of focus. No text
  is recorded. It empties its text after every commit, so that no trial sees the text of an earlier one.
- **Executor** (`kit/emit`). Sends the planned key presses as system key events and records each press as sent
  (the oracle), with wall-clock and monotonic times taken immediately before dispatch. It refuses to start if
  either clock resolves more coarsely than 1 ms.
- **Runner** (`kit/run/run_cell.py`). Starts the reference input field and the observer, and before every block
  brings the reference input field to the front, confirms that it is in front, and switches the input method to
  Japanese by pressing the kana key. It then sends the block, and after the last block keeps both programs running
  for `settle_ms` (1,000 ms) before stopping them, so that the 50 ms window of the ground-truth rule (section 4.3)
  is observed after the last commit. A run is aborted if the front-window check fails or if either program stops.
- **Prediction** (`kit/analysis/spec_predict.py`). Applies the observer's specified rules to the oracle and the plan
  (section 4.5). Its selftest compares its rule tables with the observer's source code, so that a change on either
  side is detected.
- **Delivery report** (`kit/analysis/delivery.py`). Compares, press by press, the oracle with the plan, with the key
  rows of the observation and with the key-downs of the reference log (section 6.3).

### 2.3 Factors

- **Cell**: live conversion on, live conversion off. Each cell has its own procedure file:
  `kit/gen/recipes.json` (on) and `kit/gen/recipes.macos-live-off.json` (off). They differ only where live
  conversion changes how the input method responds to Return and Escape.
- **Scenario**: S1 to S15 (table below). S9 (choosing a candidate with the mouse) has no procedure, because no means
  of locating the candidate window for a scripted click was established; it is not run and is reported as not
  evaluated. S11 (conversion without Space under live conversion) is run only with live conversion on. A cell
  therefore has 14 scenarios (on) or 13 (off). With live conversion on, S3 and S11 have the same procedure (type the
  reading, Return) and the same intent; they are kept as two scenarios because they were designed to test different
  behaviours of the input method, and they are reported separately, each with its own trials. In pooled values each
  counts with its own trials.
- **Speed**: three levels of the interval between key presses (section 3.3).
- **Think time**: in scenarios with a pause before the decisive key, the pause is drawn per trial from a
  log-uniform distribution between 0.2 and 20 seconds. Its role in the design is to place sessions on both sides of
  the observer's 20-second cut-off. It is not a factor of any registered analysis; any analysis of the dependence
  of an estimate on think time is exploratory (section 6.12).

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
plans were generated before the freeze on two machines (Python 3.11.9 and 3.14.4) with byte-identical results:
SHA-256 `c7a5469de0febbbc2e90259e477900ab0eb68c74b86f420b1e9491799a1210ba` (live conversion on, 3,150 trials in
126 blocks) and `3759ebf7832ba561820abab504929dbadd7e775a33e22ba0e89b92e4800009a2` (off, 2,925 trials in 117
blocks). The plan used for a run is generated on the measuring machine; a run whose plan has a different SHA-256 is
not analysed, and the run manifest records the SHA-256 of the plan it used.

### 2.5 Blinding

The observer's session rows of the calibration pilot were never read. Before any analysis of the pilot, each
observation log was split into its key rows, which were analysed, and its session rows, which were written to a
sealed file padded to a multiple of 1 MiB (`kit/pilot/seal_obs.py`), so that not even their number could be
inferred; the sealed files were not opened. The key rows that were read are, on macOS, the very input from which
the observer infers its sessions: the blinding withheld the observer's output, not its input. The ground-truth
definition, the procedures, the analysis code and the analysis settings were all fixed without reference to any
session row of the observer. The prediction of section 4.5 uses only the oracle and the plan. No session row of the
measurement is read before the freeze.

## 3. Sampling plan

### 3.1 Data that exist before the freeze

A calibration pilot was run on the measuring machine before the freeze; it is reported in
`experiment/pilot-macos.md`. Its runs used provisional settings: one to three trials per scenario and speed,
key-interval medians of 300, 200 and 120 ms, a three-key block-start marker (F13, F14, F13 in the first pilot and
`left`, `right`, `left` from then on), and seeds 1 to 6 instead of the one in `experiment/SEED`. Their other
generator settings (the spread of the key intervals, the key hold, the think time, the candidate index, the
arrow count, the phrase length, and the gaps between trials and between marker presses) were those of
`experiment/plan_config.macos.json`. Their plans requested an input-method reset before each block, but no reset
command was given, so no reset was made. Only the reference side was analysed: the reference input field's
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
- the time per trial, from which it was checked that a run fits in one night (section 3.3).

In addition, outside the runs, a few key sequences were typed by hand on the measuring machine, in the reference
input field and in another application, to check whether the response of the input method to a single Return
after a conversion depended on how the key was sent (it did not). These checks were diagnostic; their records are
not part of the data and are not deposited.

No session row of the observation was read, no agreement between the observation and the ground truth was
computed, and no text-recoverability or runtime analysis was run on pilot data.

Before the freeze, the prediction of section 4.5 was also computed on the two measurement plans, with an oracle
built from the plans' own times (no sending delay; 2 s between blocks). No observation exists or was read for
this. With live conversion on, it predicts 2,638 rows; in 677 of the 3,150 trials a session that the trial started
is cut off at 20 seconds (423 of the 1,050 slow trials, 158 mid and 96 fast); in 188 trials (all S6) a session runs
on into a later trial; 113 trials start no session of their own (they follow an S6 trial); 314 trials start more
than one session; and 113 trials type a long-vowel mark, comma or full stop. With live conversion off the
corresponding figures are 2,417 rows, 650 of 2,925 trials (398 slow, 157 mid, 95 fast), 186, 109, 280 and 99.
The number of trials per stratum that remain under the cut-off is given in section 3.3. The values of the
analysis are computed from the oracles of the measurement, not from these.

### 3.2 Data collection

Each cell is measured in one run on the measuring machine (Apple Silicon, macOS 27.0 or the version recorded in
`experiment/env.md`, JIS keyboard, Romaji input). The machine runs on mains power, with automatic updates, network
time synchronisation, sleep, screen lock and the screen saver turned off. The input method's predictive candidates
are left at their default (shown). The input method's learning is not reset: no method of resetting it was found,
and the plans request no reset (section 7). The run manifest records the system and input-method versions and
these settings.

The runs are made on separate nights in this order: the cell with live conversion on, the cell with live
conversion off, then the two conditions of question 5 (section 6.10), `idle` and then `working`. The order is
fixed so that the replay of section 6.10 adds no learning before the cells of questions 1 to 4 are measured.

Before each block the runner switches the input method to Japanese by pressing the kana key, after confirming that
the reference input field is in front. A block begins with a marker of four arrow presses (left, right, left,
right), 150 ms apart, which both logs record and which is used to measure the clock differences; it is longer than
the longest run of arrow presses inside any trial, so it cannot be confused with one. Trials are separated by 1,000
ms.

### 3.3 Sample size, precision and settings of the plan

- **Trials**: 75 per cell, scenario and speed: 3,150 trials with live conversion on and 2,925 with it off. The
  number was chosen for the precision of the per-stratum proportions (table below): near a proportion of 0.95 the
  half-width of a 95% Wilson interval is about 5 percentage points with 75 trials. It was then checked that a run
  fits in one night: the generator estimates 11.9 and 11.2 hours (13.6 and 13.8 seconds per trial, including waits
  and markers; the estimate leaves out the start of each block), and in the pilot the measured time per trial
  (11.0 seconds with live conversion on, 11.9 with it off) was close to the generator's estimate for the pilot's key
  intervals (11.2 and 11.4 seconds).
- **Precision of proportions**: half-width, in percentage points, of the 95% Wilson interval at the proportion p
  for the numbers of trials that occur in this design (75: a stratum; 225: a scenario over the three speeds; 1,050:
  a speed over the 14 scenarios; 3,150: a cell; 34: the smallest number of S1 trials of one speed that remain under
  the cut-off, see below):

  | n | p = 0.5 | 0.8 | 0.95 | 0.99 |
  |---|---|---|---|---|
  | 34 | 15.9 | 13.2 | 8.7 | 5.1 |
  | 75 | 11.0 | 8.9 | 5.4 | 3.5 |
  | 225 | 6.5 | 5.2 | 2.9 | 1.5 |
  | 1,050 | 3.0 | 2.4 | 1.3 | 0.6 |
  | 3,150 | 1.7 | 1.4 | 0.8 | 0.4 |

  With 75 trials a stratum's recall near 0.95 is located to within about 5 points, which separates an observer that
  misses about one session in twenty from one that misses one in ten, but not finer differences; a speed level
  (1,050 trials) locates it to about 1.3 points. Pooled values carry intervals that ignore the clustering of trials
  in blocks (section 6.1) and are read as lower bounds of the uncertainty.
- **Trials under the cut-off**: questions 1 and 2 are answered over the trials whose session the observer's rules
  do not cut off (section 6.4), so their strata are smaller than 75. From the prediction on the measurement plans
  (section 3.1), the trials that remain per scenario and speed (slow / mid / fast) are:

  | Scenario | on | off |
  |---|---|---|
  | S1 | 34 / 70 / 73 | 44 / 69 / 73 |
  | S2 | 39 / 64 / 71 | 43 / 68 / 72 |
  | S3 | 60 / 75 / 75 | 59 / 75 / 75 |
  | S4 | 43 / 67 / 71 | 38 / 67 / 74 |
  | S5 | 63 / 75 / 75 | 65 / 75 / 75 |
  | S6 | 3 / 30 / 63 | 5 / 30 / 70 |
  | S7 | 38 / 69 / 72 | 40 / 65 / 73 |
  | S8 | 36 / 63 / 73 | 35 / 67 / 66 |
  | S10 | 75 / 75 / 75 | 75 / 75 / 75 |
  | S11 | 56 / 75 / 75 | not run |
  | S12 | 75 / 75 / 75 | 75 / 75 / 75 |
  | S13 | 1 / 4 / 6 | 0 / 2 / 2 |
  | S14 | 53 / 75 / 75 | 51 / 75 / 75 |
  | S15 | 51 / 75 / 75 | 47 / 75 / 75 |

  S13 is designed to exceed the cut-off and is examined in the over-limit scope (section 6.4); S6 keeps its session
  open with Backspace, so at the slow and middle speeds it is mostly carried into the next trial and cut off. These
  strata are reported with their small numbers and wide intervals, or as null when they are empty (section 6.11).
- **Precision of continuous measures**: for a mean difference (the bias of `dwell_ms`, a per-text bias), the
  half-width of the 95% interval is about 1.96 x SD x sqrt(D / n), where SD is the standard deviation of the
  differences, n the number of pairs or texts, and D the design effect of the blocks, 1 + (m - 1) x rho, with m the
  mean number of items per block and rho the correlation within a block. In a stratum the 75 trials are spread over
  about 42 blocks (m about 1.8), so D is at most about 1.8 and usually near 1: the half-width is about 0.23 x SD (for
  example 2.3 ms when SD is 10 ms, 11 ms when it is 50 ms). Over a speed level (about 1,050 pairs, m about 25) it is
  about 0.06 x SD x sqrt(D), with D between 1 and 25. Per speed there are 126 texts (on) and 117 (off) in 42 and 39
  blocks (three texts per block). The width of an interval for the limits of agreement, for kappa and for the ICC
  depends on the values estimated and is reported as estimated.
- **Key intervals**: log-normal, with medians of 480 ms (slow), 240 ms (middle) and 120 ms (fast) and a log-scale
  standard deviation of 0.3. The medians follow the per-participant mean inter-key intervals that Dhakal, Feit,
  Kristensson and Oulasvirta (2018) report for the slowest tenth of their participants (481 ms), for all
  participants (239 ms) and for the fastest tenth (122 ms). Those values come from transcription typing of English
  sentences; they are used to span the range of typing speeds, not as estimates of Japanese typing. With a
  log-scale standard deviation of 0.3 the mean interval is about 4.6% above the median. The spread is a design
  choice that makes intervals vary; it is not estimated from data. An interval shorter than the key hold plus 1 ms
  (61 ms) is raised to it, which affects about 1% of the intervals of the fast level. The intervals are drawn
  independently of the keys (section 7).
- **Key hold**: 60 ms from key-down to key-up. The generator never overlaps two presses, so the hold must stay below
  the shortest intervals of the fast level; the input method acts on key-down, and key-up times are not part of
  any measure.
- **Other settings**: candidate index up to 4 (S2, S8), up to three arrow presses (S7), kana strings of four to
  eight characters (S12).

### 3.4 Stopping rule

Each cell is run once to completion. If a run is aborted (the runner stops it), the cell is run again from the
start with the same plan, in a new run directory, up to three attempts. Aborted runs are reported with their
reason and are not analysed. A cell that is not completed in three attempts is reported as not measured. The same
rule applies to each condition of question 5: a condition that is aborted or insufficient (section 6.10) is run
again on another night, up to three attempts in all, and every attempt is reported.

## 4. Variables

### 4.1 Manipulated

Cell, scenario and speed (section 2.3); think time varies within scenarios (section 2.3).

### 4.2 Recorded

- The plan (`plan.jsonl`): every trial's scenario, speed, phrase, intent and key schedule.
- The oracle (`oracle.jsonl`): every press as sent, the block markers, and each trial's begin and end.
- The ground-truth log (`gt.jsonl`): the reference input field's calls (kinds, lengths and times only), the key
  code of each key-down it receives, and each change of its focus.
- The observation (`obs.jsonl`): key rows (category and time) and session rows (`t`, `dwell_ms`, `nav`,
  `abandon`).
- The run manifest (`run.json`): the cell settings, the SHA-256 and line count of every log, the SHA-256 of the
  plan, the system and program versions, and the outcome of every front-window check.

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
clock correction is applied (section 6.9). The time `t` is the time at which the row was collected, which can be up
to about 100 ms after the session ended; `dwell_ms` is measured from the session's own start and end and does not
include this delay.

### 4.5 The observer's specified rows (prediction)

`kit/analysis/spec_predict.py` applies the observer's rules (section 1.1, as written in its source: the mapping of
macOS key codes to virtual-key codes, the order in which a key updates the input-mode flag and then drives the
session, the transitions of the session and the 20-second cut-off) to every press in the oracle, in the order and
at the times the oracle records. It also models what the oracle does not record: the kana key that the runner
presses at the start of every block, and the marker presses (from the plan). Presses that send no key event (the
switch to another application in S15) are skipped. The result is, per run, the list of sessions the observer is
specified to form, each with its start, end, `nav`, `abandon` and how it ended (a row, cut off, or open at the end of
the log), and per trial:

- **long**: a session that the trial started is cut off at 20 seconds;
- **carried out**: a session that the trial started ends in a later trial;
- **started none**: the trial started no session (in this design, its presses all went into a session carried over
  from an earlier trial);
- **closing key in reading**: the trial types a long-vowel mark, a comma or a full stop, whose keys close a session
  under the observer's rules.

The predicted rows are the predicted sessions that end with a row. Their times are the oracle's dispatch times; the
observer's rows carry the time at which the event reached the observer, and the time at which the row was collected
(section 4.4).

### 4.6 Texts

For the per-text measures, the trials of each block are cut, in plan order, into texts of eight consecutive
trials; the remainder of a block (one trial with blocks of 25) is not used. Every text is of one speed. The four
measures are computed for every text on both sides: the number of conversions (sessions or rows), the mean
conversion time (total duration over the sessions, or over the rows with a non-zero `dwell_ms`; every session has a
positive duration), the abandonment rate (cancelled sessions, or rows with `abandon` set, over all), and the
fraction of time spent converting (total duration over the time from the first trial's begin to the last trial's
end). The four measures are examples of aggregates a writing researcher might compute from such a log; they were
not selected from a review of the writing literature.

## 5. Analysis code and settings

The whole analysis of questions 1 to 3 is run by one command, `bash experiment/run.sh`, which reads the run
directories listed in `experiment/data.md`. The analysis code, including the prediction and the key map it reads
(`kit/emit/keymap_macos.json`), is fixed by the tag of the freezing commit; the analysis is run from a clean checkout
of that tag, and the commit is recorded with the results in `experiment/notes.md`. The result files record the
SHA-256 of the configuration, the rule file, the key map, every manifest and every input log. The settings are in
`experiment/config.json`: overlap criterion `iou_min` = 0.5, observation end offset 0 ms, `theta` = 0.5, sessions
with a start inside an open session not dropped, texts of 8 trials, 2,000 bootstrap resamples, cut-off limit 20,000
ms, and three mixtures of speeds for the mixture analysis. The ground-truth rules are in `experiment/gt_rules.json`
and the seed in `experiment/SEED`. Before any statistic, the pipeline checks the freeze marks, the SHA-256 of every
log against its manifest, the content-free format of every log, and that the observation declares both of its
channels.

The definition of the cell's system (`macos_def`) is the definition of the analysis. The analysis is also run under
the definition common to both systems (`all`); on the reference side of a macOS cell the two hold the same sessions,
which the pipeline checks and reports (`same_sessions_as_all`), and the results under `all` are not otherwise
reported.

## 6. Analysis plan

### 6.1 Units, intervals and wording

The primary estimates are given per stratum: cell, scenario and speed. Values per speed (pooled over the scenarios)
and per cell (pooled over the strata) are sums of the counts, or collections of the pairs, of their strata; every
stratum has the same number of planned trials, so the strata weigh about equally apart from exclusions and the
cut-off scope. Because synthetic input has no natural mix of scenarios, a pooled value is not an estimate of
accuracy in natural typing, and it is labelled as pooled. Proportions carry 95% Wilson intervals (Wilson, 1927),
which treat trials as independent: within a stratum the 75 trials are spread over about 42 blocks, so the effect of
the blocks is small, and for pooled proportions the interval is read as a lower bound of the uncertainty. Continuous
measures, the limits of agreement, kappa and the ICC carry 95% percentile bootstrap intervals (Efron, 1979) that
resample whole blocks (Cameron, Gelbach, & Miller, 2008), because trials in one block share the state of the input
method. F1 and counts carry no interval. All resampling uses the seed in `experiment/SEED`, with 2,000 resamples.

In the abstract and the conclusions, estimates are given as the ranges of their intervals, without evaluative
words (such as good, high or acceptable agreement); no threshold of adequate agreement is set.

### 6.2 Exclusions and other contingencies

Applied before matching, and reported by reason, stratum and number. These are the only exclusions:

- `clock_jump`: two adjacent events of the reference or oracle log whose wall-clock and monotonic differences
  disagree by more than 1,000 ms. The affected trials, from the jump to the end of its block, are excluded.
- `log_truncated`: a session still open when the log ends.
- `carry_over`: a session of the ground truth that overlaps two or more trials. The composition was not closed in its
  own trial and ran on into the next, so every trial it overlaps is excluded (in the pilot, two carry-overs with live
  conversion on, in S8 and S10, excluded four trials).
- Observation rows are assigned to the trial they overlap most and are excluded with that trial.
- Aborted runs (section 3.4).

Not excluded: trials in which the input method did not do what the plan intended (they are counted, section
6.3); sessions in which a start arrived while a session was open (counted); observation rows with `dwell_ms` equal
to zero, which the observer produces when the wall clock steps back (they stay in the matching as intervals of
zero length, so they count as false positives, and their number is reported in every bucket); and the trials whose
session the observer's rules cut off, which are set aside from the primary scope but analysed (section 6.4).

Other contingencies:

- A loss of focus of the reference input field inside a block, other than the planned switch of S15, is not
  excluded: the reference then receives no call, so the trial appears as a plan-versus-ground-truth disagreement
  (section 6.3); the trials with such a loss are counted per stratum in the delivery report.
- If the input method stops responding or restarts during a run, the affected trials are not excluded; they appear
  as disagreements and are reported. A run that the runner aborts is handled by section 3.4.
- If the system or input-method version recorded in a run manifest differs from that of an earlier run, the run is
  analysed as recorded and the difference is reported as a deviation (section 8).
- A text whose measure cannot be computed on one side is left out of that measure's figures and counted (section
  6.11).
- If the closed-set attack stops because the observed presses of some trial do not agree with the plan, the closed
  set of that cell is reported as not computed, with the trial named, and no recommendation is made (section 6.8).
- The run of the `working` condition of question 5 is not used for questions 1 to 4.

### 6.3 Plan versus ground truth, and delivery of the presses

For every trial, the assembled sessions are compared with the plan's intent and classified as agreeing or as one
of the disagreement types (no session, an unexpected session, several sessions, a commit where a cancellation was
planned, a cancellation where a commit was planned, a session open at the end). The counts and rates are reported
with Wilson intervals, per stratum and overall. These trials stay in the evaluation: removing them would keep only
the trials in which the input method behaved as planned.

The delivery of the presses is reported descriptively, per cell and speed (`kit/analysis/delivery.py`): the delay of
each press against the plan's schedule; for the observation's key rows and for the reference log's key-downs, the
fraction of sent presses that arrived and the number of rows without a sent press (inside trials, and outside them,
where the block markers and the runner's kana presses fall); and, in the trials where every press arrived, the delay
of each row after its press and the error of each interval between consecutive rows. Input-mode keys, which the
observer does not record by design, are reported with and without. These figures concern events generated in
software; no claim is made about the path from a physical keyboard (section 7).

### 6.4 Scopes and comparisons

**Scopes.** The prediction (section 4.5) marks, from what was sent, the trials whose session the observer's rules cut
off at 20 seconds (long trials). Each analysis of questions 1 and 2 is computed under three scopes, which select
trials after the exclusions and, like the exclusions, at the level of a trial (the sessions and the rows of a trial
go together):

- `under_limit`: the trials that are not long. **The primary scope of questions 1 and 2.**
- `over_limit`: the long trials only. For these trials the specified behaviour is that the long session produces no
  row; the rows that the observer writes after a cut-off (a letter or digit pressed after it opens a fresh session,
  for example the digit of S8 after a long pause) are rows of these trials.
- `all_trials`: every trial, reported as secondary.

The scope is decided from the oracle and the plan alone, so it does not depend on the observation. A session or row
that belongs to no trial is in `under_limit`. Question 3 is answered under `all_trials` (primary), because the
aggregates a researcher computes include the long sessions, and under `under_limit` (secondary), in which the
sessions and rows of the long trials are left out on both sides while the texts are kept.

**Comparisons.** The prediction also allows the disagreement between the ground truth and the observation to be
traced. Each scope is computed for three comparisons, with the same matching and the same measures:

- ground truth against observation (`gt_obs`): the questions of this study. **Primary.**
- ground truth against prediction (`gt_pred`): how well the observer's rules, carried out exactly, describe the
  sessions of the reference input field (the validity of the rules). It is computed without the observation.
- prediction against observation (`pred_obs`): whether the observer carries out its rules (missed presses, timing,
  implementation). Here the predicted rows take the place of the ground truth; the exclusions of the ground truth are
  kept, so all three comparisons cover the same trials.

The two secondary comparisons are reported next to the primary one; no arithmetic relation between the three is
claimed. Disagreements that the rules predict (for example the session of S6 kept open by Backspace and carried into
the next trial, the session of S10 closed by Tab, a reading split by a long-vowel mark, comma or full stop, and, with
live conversion on, a session closed by the first of two Returns or Escapes while the ground truth closes at a later
one) are counted in `gt_pred` as disagreements of the rules; they are not removed from `gt_obs`.

**Layers.** As a diagnostic, the detection measures of each comparison and scope are also reported, pooled and per
speed, for the trials of four layers from the prediction: carried out, started none, closing key in reading, and the
trials in none of the three. A carried-out session contaminates the next trial whatever its scenario; the layers show
where this happens.

### 6.5 Question 1: detection

Sessions and observation rows are matched one to one in descending order of interval overlap (intersection over
union) among the pairs that reach 0.5. Among the items left unmatched, one session with two or more rows whose
combined interval reaches the criterion is a split, and one row with two or more sessions is a merge; the rest
are misses and false positives. Because a fragment that reaches the criterion on its own becomes a one-to-one pair,
the split and merge rates are then recounted: an unmatched row whose length lies at least half (`theta`) within a
matched session counts toward a split, and an unmatched session lying at least half within a matched row counts
toward a merge. The primary pairing is not changed by the recount.

Reported per stratum, per speed and per cell, for each comparison and scope: recall (pairs over sessions),
precision (pairs over rows), split rate, merge rate, miss rate and false-positive rate, each with a Wilson interval,
and F1 without an interval.

### 6.6 Question 2: per-session agreement

Over the one-to-one pairs of each stratum, per speed and per cell, for each comparison, under `under_limit`
(primary) and `all_trials`:

- **Duration**: the error is `dwell_ms` minus the session's duration. Reported: the median absolute error with a
  bootstrap interval, and the Bland-Altman bias and 95% limits of agreement (Bland & Altman, 1986), each with a
  bootstrap interval. A row with `dwell_ms` equal to zero never enters a pair (section 6.2); the number of such rows
  is reported.
- **Abandonment**: the session's outcome (cancelled or not) against the row's `abandon` flag. Reported: the 2 by 2
  table, the raw agreement with a Wilson interval, and Cohen's kappa (Cohen, 1960) with a bootstrap interval. Within
  one stratum the ground truth has mostly one outcome, so kappa is often undefined there; kappa is read per speed,
  where both outcomes occur, and an interval is withheld, with its reason, when kappa is undefined in the sample or in
  any resample. The same figures are reported separately for sessions with and without a commit followed by a
  continuation (`n_continued_commits` greater than zero, or zero), as a diagnostic: with live conversion on, about 4
  in 10 cancellations in the pilot followed such a commit. This split does not replace the main figure.
- **Navigation**: the exact-agreement rate of `nav` with the true count, with a Wilson interval, and the
  distribution of the difference.
- **Cut-off**: under `over_limit`, the number of long sessions that nonetheless appear in a pair, split or merge
  (specified: zero), the number of rows of the long trials, and how they compare with the predicted rows of those
  trials (`pred_obs`); in every scope, the number of rows of 20 seconds or more (specified: zero).

### 6.7 Question 3: per-text agreement

For each of the four measures of section 4.6 and each speed: the Bland-Altman bias and limits of agreement of the
per-text difference (observation minus ground truth), and the intraclass correlation for absolute agreement of a
single measurement, ICC(2,1) in the notation of Shrout and Fleiss (1979), which McGraw and Wong (1996) call ICC(A,1),
computed by `kit/analysis/stats.py` from the mean squares of a two-way analysis of variance with the two methods as
columns, with a 95% interval from resampling blocks (the texts of a block form one cluster). The interval is
withheld, with the reason, when the ICC is undefined in the sample or in any resample. The per-speed values are
primary; values pooled over speeds are reported for comparison, because a difference in level between speeds
inflates a pooled ICC. A text is not used if any of its trials was not run or was excluded; the numbers of such texts
are reported by reason, block and speed. The bias of each measure is also reported for three mixtures of speeds
(slow, middle and fast in proportions 0.6/0.3/0.1, equal, and 0.1/0.3/0.6) to show whether the aggregate's bias
moves with the mix.

A text mixes the scenarios of its block about equally, so every per-text value and ICC holds for that mix of
scenarios only. So that a reader can weight the scenarios differently, three per-trial differences (observation
minus ground truth) are also reported per scenario and speed, with the mean on each side and a block-bootstrap
interval: the number of conversions, the summed conversion time and the number of cancelled conversions.

### 6.8 Question 4: text recoverability

Run on the observation logs of each cell separately, with the plan, procedure file and settings that built them
(the attack refuses a mismatch). Block markers are recorded by the observer and are declared to the attack
(`--markers-in-obs`); input-mode switches are not recorded on macOS and are not declared. The ground truth is the
reading that was typed, not the original sentence. The attacks read the category and time of every key row; they
do not use the session rows, so the session rows are outside the scope of the recommendation below.

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
phrase, and the accuracy per scenario. A trial whose phrase is a generated kana string (S12) is not counted, which
leaves 2,925 trials with live conversion on and 2,700 with it off.

The synthetic key intervals are drawn independently of the keys (section 3.3), so the logs carry none of the timing
of particular key pairs that human typing has. The attack's accuracy on the feature sets that keep millisecond times
(`all`, `no_runs`) therefore cannot be carried over to human logs: for these two sets the accuracy is reported as an
estimate only, and they are excluded from the recommendation. The recommendation considers only the sets that keep
no time or times in 1-second bins (`bin1s`, `bin1s_count`, `no_time`, `counts_only`), in which intervals between
particular keys, of the order of tens of milliseconds, do not survive. Pauses between words and phrases, which human
logs also carry, are not modelled either (section 7).

The accuracy of a feature set is **near chance** at K = 10 or K = 100 when the upper end of its 95% Wilson interval is
at most 2/K. The rule's behaviour at the planned numbers of trials is fixed before the measurement: the probability
that a set is judged near chance, when its true accuracy is c/K, is

| n (trials) | K | c = 1 | 1.5 | 2 | 3 |
|---|---|---|---|---|---|
| 2,925 (on) | 10 | 1.000 | 1.000 | 0.024 | 0.000 |
| 2,925 | 100 | 0.994 | 0.487 | 0.020 | 0.000 |
| 2,925 | 1,000 | 0.210 | 0.067 | 0.020 | 0.001 |
| 2,700 (off) | 10 | 1.000 | 1.000 | 0.025 | 0.000 |
| 2,700 | 100 | 0.989 | 0.447 | 0.019 | 0.000 |
| 2,700 | 1,000 | 0.067 | 0.017 | 0.004 | 0.000 |

(binomial probability that the Wilson upper end is at most 2/K). At K = 1,000 an attack at the chance level would be
judged near chance only rarely, so K = 1,000 is reported descriptively and is not part of the rule. A feature set is
near chance for the recommendation when it is near chance at both K = 10 and K = 100 in both cells. The recommended
granularity for publishing logs is the most detailed feature sets that are near chance in this sense (the maximal
elements, in the coarsening order, of the near-chance sets among the four considered; the order is partial, so there
may be more than one). If none of the four is near chance, no granularity is recommended, and this is reported. The
Wilson interval treats trials as independent although trials of one block share context; judging by the upper end
allows for part of this, and the remainder is stated as a limitation.

**Open set.** The attacker sees only the categories of the key presses and, with a character language model,
searches for the kana string that the romanisation would spell with exactly the observed letter keys and the
observed punctuation, maximising its probability. Two knowledge levels are reported. K0 knows nothing of the genre
beyond the frequency of single characters: its model is a character unigram model estimated from the training
phrases of the same corpus. K1 knows the genre but not the individual work: a character trigram model with
Witten-Bell smoothing (Witten & Bell, 1991) trained on the corpus with the evaluation phrases' whole works held out.
Whole works, in an order drawn with the seed in `experiment/SEED`, are held out for evaluation until they hold at
least a fifth of the phrases (three of the twelve works of this corpus), and a training phrase with the same reading
as an evaluation phrase is removed. A stronger attacker, K1+, for which the corpus is split by phrase instead of by
work, is reported alongside K1. The baseline is the same model without the log, drawing a string from its prior,
either knowing only the number of segments or given the true length (both are reported).

    python3 kit/e2/open_set.py --obs <obs> --plan <plan> --corpus kit/corpus/data/phrases.jsonl \
      --recipes kit/gen/<procedure file of the cell> --split-seed 20260929 --seed 20260929 \
      --eval-fraction 0.2 --split both --n 3 --smoothing wb --beam 8 --length-info both \
      --bootstrap 2000 --markers-in-obs --out results/e2_open_set_<cell>.json

Reported: the character error rate of the attack and of the baseline, their paired difference (`gain`), and the
difference from a negative control in which each trial is decoded from another trial's observation
(`gain_vs_shuffled`), each with a block-clustered percentile bootstrap interval. Kana-input trials (S12) are
excluded. Neither attack is claimed to be the strongest possible; the results hold for these attacks.

### 6.9 Clock differences

The per-block differences between the observation, the reference input field and the executor are measured at
the block-start markers with `kit/pilot/clock_sync.py` for every run and reported (median, range, drift per hour
and per-block values). They are not used to correct the matching: the duration error is a difference of durations
and does not depend on them, and a session is still paired as long as the offset between the two intervals stays
at or below a third of its length. In the pilot the largest difference between the observation and the reference
was 22 ms; the collection delay of a row (section 4.4) adds up to about 100 ms to the end of an observation interval,
so a session shorter than about 370 ms could fail to pair for these reasons alone.

### 6.10 Question 5: runtime cost

Measured with `kit/e3` under two conditions, one night each, for eight hours at a 30-second interval: `idle` (the
observer runs and nothing operates the machine) and `working` (the observer runs while the runner plays the plan of
the cell with live conversion on). Reported for each condition: the mean, median, 95th percentile and maximum of the
observer's CPU (one core is 100%), its final resident memory and the least-squares slope of its resident memory in
MB per hour. A condition with fewer than 480 usable samples or a window shorter than four hours is insufficient
(section 3.4). The two conditions are always reported together and never reduced to one figure. Battery use is not
measured.

### 6.11 Missing data

A stratum with no pair, a measure that cannot be computed (no session, zero variance, fewer than two blocks) and an
interval that cannot be formed are reported as null with the reason, never as zero. Trials of a plan that were not
run are reported by stratum.

### 6.12 Exploratory analyses

Any analysis not described here (for example, the dependence of the duration error on think time, or comparisons
between the two cells) is reported as exploratory.

## 7. Threats to validity and limitations

- **The reference is a reference input field, not the input method's internal state.** The ground truth is assembled
  from the calls that one minimal client of the macOS text system received. The reference is placed at this software
  layer because a conversion exists only as the calls between the input method and an application; an external
  timing device would time the path of the keys, not the conversion. Another application may receive other calls
  from the same input method; the agreement is estimated for this client (section 1.3).
- **The ground truth depends on the rule of section 4.3.** With live conversion on, the rule folds the automatic
  commits made while a reading is typed into one session. A rule that did not fold them would define a conversion
  differently (several sessions per reading), not merely with another window; the window's width did not matter in
  the pilot (10 to 900 ms). The sessions affected are visible through `n_continued_commits` (section 6.6).
- **The input is synthetic.** Key events are generated in software by the executor and enter the system's event
  stream where it posts them; the path from a physical keyboard through its hardware and driver is not exercised,
  and no claim is made about it. Key intervals are drawn independently of the keys and pauses follow the procedures,
  so human timing structure (the timing of particular key pairs, pauses between words) is absent; this limits the
  text-recoverability results (section 6.8). Error correction is limited to the scenarios.
- **The input method's learning is not reset.** Candidate order and the position of automatic commits may change
  over the runs as the input method learns. The run order is fixed (section 3.2). Intervals resample blocks, which
  covers dependence within a block but not dependence that runs across blocks.
- **One machine, one system version, one input-method version.** The results hold for the recorded versions.
- **Software clocks.** All times come from the clocks of the processes on one machine; no external reference clock
  is used. Clock differences between the logs are measured at the block-start markers and reported (section 6.9);
  the collection delay of a row is up to about 100 ms (section 4.4).
- **S9 is not evaluated** (choosing a candidate with the mouse).
- **The prediction is a model of the observer's specification.** It reproduces the rules of the observer's source
  (its selftest checks them against the source) and models the runner's kana press at the start of each block; it
  does not model modifier keys, which no plan of this study sends. A difference between the prediction and the
  observation is reported as such (`pred_obs`), not attributed to a cause.
- **The cut-off scope removes trials from the primary estimates.** The primary estimates of questions 1 and 2
  describe the sessions the observer is specified to report; how often a session is cut off depends on the design
  (think time, speed, S6, S13), so the fraction of long trials is a property of this design, not of natural typing.

## 8. Deviations and addenda

Any departure from this registration after the freeze is recorded in `experiment/deviations.md` with its date,
reason and effect before the affected analysis is run, and is reported in the paper.

The Windows addendum covers only the Windows cells and question 5 on Windows (section 1.3). It may change only the
Windows blocks of `experiment/gt_rules.json` and add its own section to this file, and it may add new files that
only the Windows cells use (for example a generator settings file for Windows); it may not change any other existing
file. When it is frozen it replaces the two freeze marks; that `experiment/config.json`, `experiment/SEED`, the macOS
block of the rule file, the files used by the macOS cells and the macOS sections of this file are unchanged is shown
by the difference between the two freezing tags and stated in the addendum. The macOS analysis is run from the
macOS freezing tag, also after the addendum. The addendum is registered before the first Windows measurement.

## 9. Freeze

The freeze adds to this file two lines outside comments and code fences: one starting with `frozen_at:` followed by
the date, and one starting with `sha256:` followed by 64 lowercase hexadecimal digits. The latter is the value that

    python3 kit/analysis/pipeline.py --freeze-hash --config experiment/config.json --seed-file experiment/SEED

prints: the SHA-256 of the SHA-256 of `config.json`, of `SEED` and of `gt_rules.json`, in this order, each
followed by a line feed. The freezing commit is tagged. The frozen file is registered on OSF Registries with the
two marks and the SHA-256 of the list of files exported from the freezing commit, and the registration is public.
The list holds one line per exported file, with its path relative to the export root and its SHA-256 separated by a
space, sorted by the bytes of the path, each line ending in a line feed. The URL and date of the registration are
recorded in `experiment/notes.md`. The registration date precedes the first measurement run.

The settings of the plan generator (`experiment/plan_config.macos.json`), the two procedure files, the corpus, the
key map of the prediction and the analysis code are not part of the hash; they are fixed by the freezing tag. Every
plan records the SHA-256 of its settings, procedure and corpus files, and the SHA-256 of the two measurement plans is
given in section 2.4. At the time of writing these files have the SHA-256:

| File | SHA-256 |
|---|---|
| `experiment/plan_config.macos.json` | `eb0ff955834d135a99d1dff3ae4cb1d58a8734c819835b3afbc5db08edf02209` |
| `kit/gen/recipes.json` | `158cac1bcc15effac2eafc994d788e585b61e3c43f410d558c87c2188866d16f` |
| `kit/gen/recipes.macos-live-off.json` | `36aad15abc118e8f57533db43a880c1615008af8f2fb4dd33b846f6d1abb9168` |
| `kit/corpus/data/phrases.jsonl` | `c8f890cb4d0848bf04e6d7d95efe4e4d3dfd02a23eb1c7f103344f14d13e4620` |
| `kit/emit/keymap_macos.json` | `be191e029fa9d706cf378f20e0d5dac2f67f90c0a20d3b130d8f81ed6c918802` |

If any of them changes before the freeze, the table and the plan hashes of section 2.4 are updated in the freezing
commit.

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
