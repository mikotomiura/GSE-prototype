# Manuscript outline

This outline fixes the structure of the manuscript and the evidence for each claim before the results of the
measurement are analysed. It contains no result value. Each claim names the registered question and section that
define it, the result file from which its numbers are copied, and the table or figure that reports it. The
pre-registration (`experiment/preregistration.md`, with the Windows addendum in its section 10) and the record of
deviations (`experiment/deviations.md`) take precedence over this outline wherever they differ.

## Working title

Observing Japanese IME conversion without recording text: Observability limits, a cross-platform logger, and a
synthetic-input validation

The title may be changed to a question form after the text-recoverability results are known; the claims below do not
depend on the title.

## Journal requirements to be met

The manuscript is prepared for *Behavior Research Methods* as an original research article. The journal's instructions
for authors require: the conventions of the Publication Manual of the American Psychological Association, 7th edition,
for style, citations and references; double spacing, 1-inch margins and page numbers; a title page with the authors'
names and affiliations and the corresponding author's address, telephone number and e-mail address; an abstract of no
more than 250 words; a section headed Declarations, before the reference list, that keeps every heading of the
journal's list and writes "Not applicable" under a heading that does not apply; an Open Practices Statement
immediately prior to the References section; a data availability statement; data citations with a persistent
identifier in the reference list; and, under the journal's Level 2 of the Transparency and Openness Guidelines, all
relevant information (stimuli, the methods being validated, new analyses) in a trusted repository. The instructions
state no limit on length. They are read again immediately before submission.

## Scope of the claims

- The primary contribution is the estimate of agreement between the logger and a reference input field under
  scripted input. Every other result is reported next to it and is not used to qualify it.
- All input is synthetic. No claim is made about agreement in natural typing, about other input methods, about other
  applications than the reference input fields, or about the path from a physical keyboard.
- Estimates are reported with their intervals. In the abstract and the conclusions they are given as the ranges of
  their intervals, without evaluative words, and no threshold of adequate agreement is set. A pooled value is labelled
  as pooled and is not an estimate of accuracy in natural typing. An estimate in the primary scope is given together
  with the fraction of trials that the scope sets aside and the estimate over all trials.
- The text-recoverability results are reported as they come out. If a granularity of the key rows lets a phrase be
  identified well above chance, the manuscript says so, and it does not describe the log as safe to publish. The
  recommendation concerns one phrase at a time and the key rows only.
- The observability analysis is an argument from the documented public interfaces of the two systems. It is worded
  as "no documented interface provides" and not as a proof that observation is impossible.
- The manuscript makes no claim of priority. Its difference from earlier loggers is stated as a difference of design:
  which loggers handle input-method conversion, and which of them do so without reading the text.

## Contributions

1. **Observability analysis.** What the conversion state of another application exposes, on Windows and macOS, to a
   program that does not read text, and why the two systems leave different routes: window events of the input method
   on Windows, inference from key presses on macOS.
2. **A cross-platform logger and its validation (primary).** A stand-alone logger that writes a category for every key
   press and one summary row for every conversion session (duration, arrow-key presses, abandonment), and that
   declares in its log which of its channels it records. Its rows are compared with the sessions assembled from the
   calls that a reference input field received from the input method, in three cells (macOS with live conversion on,
   macOS with live conversion off, Windows with the Microsoft input method), under a pre-registered protocol.
3. **Text recoverability.** How accurately an attacker can identify the typed phrase among K candidates, or
   reconstruct the typed reading, from the key rows of a published log, and which of two granularities that keep no
   time keeps identification near chance.
4. **Runtime cost.** The CPU time and memory of the logger with the machine idle and with scripted typing, per
   system.
5. **A validation dataset.** The logs of the measurement, with the ground truth of the reference input field, the
   scripted plans and the record of every press sent, the phrase corpus and the runtime samples, released with a
   datasheet so that other observers can be evaluated against the same reference. The dataset is synthetic input in
   one kind of reference input field per system; it is not a record of human writing and not a benchmark of natural
   typing.

## Section plan

### Abstract (at most 250 words)

Background (keystroke logging in writing research; input-method conversion in Japanese; text-level loggers bypass
conversion and content-level loggers read the text). What was done (observability analysis; logger; validation
against a reference input field with synthetic input in three cells; recoverability attacks; runtime cost; dataset).
Results as interval ranges: recall and precision of detection, bias and limits of agreement of the duration, agreement
of abandonment, per-text agreement, recoverability against chance, runtime cost under two conditions. Availability:
pre-registrations, code, data.

### 1. Introduction

- Keystroke logging as a method of writing research, and the measures it supports (pauses, revisions, production
  rates).
- In Japanese most text passes through an input method: a reading is typed, converted, and accepted, changed or
  abandoned. The conversion is part of the writing process and is invisible to a logger that records only key
  presses or only the resulting text.
- Logging the conversion directly means reading the composition string, which records the text that a participant
  writes. A logger that records no text is easier to deploy and to share, if it can be shown what it records and what
  it leaks.
- The three questions of the paper: what can be observed without reading text; how closely such a log agrees with the
  input method's own sessions; and how much of the text the log still reveals.
- Contributions (the list above) and the structure of the paper.

### 2. Background and related work

- Keystroke loggers for writing research and what they record: loggers such as Inputlog and ScriptLog, which a recent
  comparison lists as not supporting non-alphabetic writing; Translog-II, which records input-method events in its
  own editor together with the text; and a hybrid logger for non-alphabetic scripts that reconstructs the state of
  the text by reading it.
- Studies of writing processes in Japanese and Chinese that use keystroke data: a hidden Markov model of writing
  processes from keystroke data that does not treat the input method; a thesis on writing Chinese with a keyboard in
  which pauses before the selection of characters emerged as a category of their own; an English-to-Japanese
  translation-process corpus whose logs record the keystrokes typed into the input method together with the text.
- Keystroke datasets released without the typed text (for example key positions or hand only), which show that
  dropping text is not new in itself; what is new here is a log of the conversion that holds no text.
- What timing and key categories can reveal about text: attacks that infer typed text from keystroke timing, which
  motivate the recoverability study and the restriction of its recommendation to granularities that keep no time.
- Agreement methods used in this paper (limits of agreement, kappa, intraclass correlation, cluster bootstrap).

### 3. What can be observed without reading text

- Windows. The Text Services Framework activates per thread of the calling process, and its sinks are registered on
  objects of that process; no documented call names another process. Documentation for assistive technology states
  that access to the composition string requires creating the thread manager inside the target application. The only
  route into every application is a text service loaded into each process, which would replace the user's input
  method. Message hooks that would intercept the input-method messages of other windows load code into the target
  processes. The accessibility events of the input method's windows (show, change, hide), received out of context,
  carry no string in their callback arguments. The text-edit pattern of UI Automation reports the finalized string
  of a composition, so it is not content-free. Some systems cloak the candidate window instead of hiding it, which
  the cloak notifications report. An event for a change of the conversion target exists but is raised by the
  application's accessibility provider, so its presence depends on the application; it is not used.
- macOS. The marked text of an input field is held by the in-process text-input client protocol of the target
  application; no attribute or notification of the accessibility interface reports marked text or a composition; an
  input method runs as a process of its own whose client is the system's text services, so there is no counterpart of
  a text service loaded into the target process; the list of windows can show a candidate window only by polling and
  not before a conversion; the current input source gives the input mode only. A logger that records no text can therefore only infer sessions from key presses.
- Consequence: the two systems observe different constructs (a visible window of the input method; a segment of kana
  input inferred from keys), so the measures of the two systems are defined differently and are validated
  separately.
- Table 1: interfaces considered, per system, what each exposes, whether it carries text, and whether the logger
  uses it.

### 4. The logger

- Rows: one key row per press and release with one of fourteen categories and a time (input-mode keys and, on macOS,
  F13 to F19 and modifier keys produce no row); one session row with `t`, `dwell_ms`, `nav` and `abandon`. No
  character, reading, candidate string or window name is written.
- Session rules on macOS (opening at the first letter or digit key, closing by Return or another closing key as
  committed, by Escape as abandoned, by a change to non-Japanese input; Space marks a candidate window as shown; the
  20-second cut-off without a row).
- Sessions on Windows (window events of the input method; the cloaking path with its 150 ms gap and 20-second
  cut-off; the safety valve of the event path at about 25 seconds; `nav` and `abandon` counted system-wide while a
  session is open, so they are upper bounds).
- The log header: the format, the system, the version, the SHA-256 of the manifest of the code it was built from, and
  the channels the log records, so that a log declares what it can and cannot contain.
- The content-free format: closed enumerations for every string, integers with bounded ranges, no unknown keys, no
  escapes; a validator rejects any log that departs from it.
- Table 2: row formats, key categories, and the definition of a session, `nav` and `abandon` on each system.

### 5. Validation method

5.1 Overview: three records of each trial (the plan with the intended outcome and the record of every press sent; the
calls that the reference input field received; the logger's rows) and a fourth derived one (the rows that the
logger's rules specify for the presses sent, macOS only). Figure 1: the components and the data they record.

5.2 Cells and machines: macOS (standard Japanese input method, live conversion on and off, one Apple Silicon machine);
Windows (Microsoft input method with the Text Services Framework reference input field, one x86-64 tablet); versions
and settings recorded per run; learning of the input method not reset.

5.3 Reference input fields and ground-truth rules: the macOS client of the text-input protocol and the rule that
assembles sessions from its calls (the 50 ms continuation window for live conversion); the Windows field that is a
client of the Text Services Framework and its rule (a composition from start to end, committed when the committed
length is positive); definitions by system and the common definition.

5.4 Scenarios, speeds and plans: the scenarios and their procedures per cell (Table 3); three speeds with key-interval
medians of 480, 240 and 120 ms from published typing data; think times from 0.2 to 20 seconds; 75 trials per
scenario and speed; plans generated from a seed, with the SHA-256 of every input and of the plans registered.

5.5 Calibration pilots and blinding: what the pilots fixed (procedures, ground-truth rules, the stopping-rule
settings, the choice of the Windows reference field); the logger's session rows of the pilots sealed and never read.

5.6 The specified rows (macOS): the prediction from the presses sent, and the three comparisons (ground truth against
observation, primary; ground truth against prediction; prediction against observation).

5.7 Checks of the instruments: agreement between the plan and the ground truth; delivery of the presses to the
observation and to the reference; the stopping rule (presses from outside, losses of focus, and on Windows the key
rows that no sent press explains); clock differences at the block markers.

5.8 Analysis: exclusions; scopes (`under_limit` primary, `over_limit`, `all_trials`); matching by interval overlap;
measures of questions 1 to 3; intervals (Wilson for proportions; percentile bootstrap resampling whole blocks for
continuous measures, kappa and the ICC); missing values reported as null.

5.9 Pre-registration and deviations: the two frozen registrations, the freeze marks and tags, and the deviations
recorded before the Windows measurement (Table 4) and any recorded later.

### 6. Study 1: Detection and per-session agreement

Questions 1 and 2 per cell, with the comparisons, the scopes, the layers of the prediction (macOS), the Windows
diagnostics, and the attempts and exclusions.

### 7. Study 2: Per-text agreement

Question 3: four per-text measures per speed, the mixtures of speeds, and the per-trial differences by scenario and
speed for reweighting.

### 8. Study 3: Text recoverability

Question 4: the closed-set identification over six feature sets and three values of K, the near-chance rule and the
recommendation from the macOS cells, the Windows judgement as a qualification, and the open-set reconstruction with
its baseline and negative control.

### 9. Study 4: Runtime cost

Question 5 on both systems, two conditions each, reported side by side and never reduced to one figure.

### 10. The dataset

Contents, formats, how the data were produced and checked, what was not deposited and why, licence, persistent
identifier, intended uses, and limits. The dataset has two parts that are kept apart: the measurement runs, made from
the registered plans, and the calibration-pilot runs that meet the registered criteria, made from other plans with
provisional settings. A datasheet in the form proposed by Gebru et al. is released with the data.
Intended uses stated in the manuscript: (a) the calls that an input method makes to an input field, per system and
setting, as a basis for re-examining definitions of a conversion; (b) evaluating another observer on the same plans
with the same executor and reference input fields; (c) studying how far a key log without text reveals the text, with
the typed phrases known.

### 11. Recommendations for researchers

Per system, which measures the results support and which comparisons they do not (for example measures defined
differently on the two systems), how the 20-second cut-off changes a researcher's aggregates, and the granularity of
key rows that the recoverability study supports for publication. Each recommendation cites the result it rests on;
none is written before the results.

### 12. Limitations

Synthetic input; one input method per system and one kind of reference input field; the reference is software on the
same machine; the learning of the input method not reset; one machine and one version per system; S9 (choosing a
candidate with the mouse) not evaluated; the cut-off scope; the stopping rule's blind spots; intervals that treat
trials as independent where stated; the recoverability study judges one phrase at a time; battery use not measured.

### 13. Conclusions

### Declarations

Placed before the reference list, with the journal's headings: Funding; Conflicts of interest/Competing interests;
Ethics approval (Not applicable: no person took part, and all input was generated by a program); Consent to
participate (Not applicable); Consent for publication (Not applicable); Availability of data and materials (the data
availability statement, with the persistent identifier of the dataset); Code availability; Authors' contributions
(optional in the journal's list). Acknowledgments, if any, form a separate section before the reference list.

### Open Practices Statement

Placed immediately prior to the References. The two registrations on OSF Registries (macOS cells:
https://osf.io/9nh7r, DOI 10.17605/OSF.IO/9NH7R; Windows addendum: https://osf.io/4jwzn, DOI 10.17605/OSF.IO/4JWZN);
the code, materials and analysis scripts in a public repository with an archived release and DOI; the data with their
own DOI. The analyses reported as registered are run from the freezing tags; deviations are reported.

### References

## Claims and evidence

The result files are those named in `experiment/notes.md`. The macOS results are written to `experiment/results/` by
`experiment/run.sh` from the macOS freezing tag; the Windows results to `experiment/results/windows/` by the command
of section 10.7 of the pre-registration from the Windows freezing tag. The files of question 4 are
`e2_closed_set_<cell>.json` and `e2_open_set_<cell>.json`, and those of question 5 are `e3_<system>.txt`. Every number
in the manuscript is copied from these files by a script kept with the manuscript; no number is typed or rounded by
hand.

| ID | Claim | Registered definition | Evidence | Reported in |
|---|---|---|---|---|
| OB1 | On Windows no documented interface lets a program that runs outside the target application read or follow the composition of the Text Services Framework; the only documented route is code loaded into the target process. | Section 10.3 (the observer on Windows) | Microsoft documentation of the thread manager, of the sink registration and of input-method accessibility; documentation of message hooks | Section 3, Table 1 |
| OB2 | The window events of the input method, received out of context, carry no string; the text-edit pattern of UI Automation carries the finalized string. | Section 10.3 | Microsoft documentation of the event callback, the event constants and the text-edit pattern | Section 3, Table 1 |
| OB3 | On macOS no documented interface reports the marked text or composition state of another application; the input mode is available, the composition is not. | Section 1.1 | Apple documentation of the text-input client protocol, the accessibility attributes and notifications, the input-method framework, the window list and the input sources | Section 3, Table 1 |
| OB4 | The two systems therefore log different constructs, which are validated separately and not compared as equal. | Sections 1.1, 10.3, 10.11 (two constructs) | OB1 to OB3; the session rules of the logger | Sections 3, 4 and 11; Table 2 |
| LG1 | The logger writes key categories and session summaries and no text; every log carries its format, its channels and the SHA-256 of the code it was built from. | Sections 1.1, 2.2, 10.3 | `kit/formats/FORMATS.md` (`obs/1`); `kit/formats/validate_logs.py`; the content-free check that the analysis applies to every log before any statistic | Section 4, Table 2 |
| LG2 | The macOS session rules and the Windows session paths are those stated, including the cut-off and the safety valve. | Sections 1.1, 4.5, 10.3 | Logger source in `kit/logger/`; the self-test of `kit/analysis/spec_predict.py` against that source | Section 4 |
| AG1 | Recall, precision, split rate and merge rate of the session rows against the reference, per cell, scenario and speed, in the primary comparison and scope, with the set-aside fraction and the estimate over all trials. | Question 1; sections 6.4, 6.5, 10.7 | `e1_detection.json` (macOS and Windows), primary comparison `gt_obs` under `under_limit` | Section 6; Figure 2; Table 5; per-stratum tables in the supplement |
| AG2 | Error of `dwell_ms` (median absolute error; Bland-Altman bias and limits of agreement). | Question 2; section 6.6 | `e1_l1.json` | Section 6; Figure 3; Table 6 |
| AG3 | Agreement of `abandon` with the session's outcome (raw agreement; kappa per speed), also split by commits followed by a continuation. | Question 2; section 6.6 | `e1_l1.json` | Section 6; Table 6 |
| AG4 | Agreement of `nav` with the arrow presses sent during the session. | Question 2; section 6.6 | `e1_l1.json` | Section 6; Table 6 |
| AG5 | Behaviour at the 20-second cut-off: rows of 20 seconds or more, and rows of the long trials against the specified rows (macOS); rows of 20 to 25 seconds and of 25 seconds or more, and the sensitivity analysis of the long trials (Windows). | Questions 1 and 2; sections 6.6, 10.7 | `e1_l1.json`; `e1_detection.json` (`over_limit`, `under_limit_gt_duration`, `long_trials_from`) | Section 6 |
| AG6 | Separation of the disagreement into the validity of the rules (ground truth against prediction) and their execution (prediction against observation), macOS only. | Section 6.4 | `e1_detection.json`; `e1_l1.json` (`gt_pred`, `pred_obs`, layers) | Section 6; Table 5 |
| AG7 | Trials in which the input method did not do what the plan intended, by type, kept in the evaluation. | Section 6.3 | `e1_l1.json` (plan against ground truth) | Section 5.7 or 6; supplement |
| AG8 | Delivery of the presses to the observation and the reference, and the clock differences at the block markers. | Sections 6.3, 6.9 | `e1_delivery.json`; the output of `kit/pilot/clock_sync.py` per run | Section 5.7; supplement |
| AG9 | Every attempt of every run, including attempts aborted or stopped, with its reason and figures; exclusions by reason, stratum and number. | Sections 3.4, 6.2, 10.8 | `experiment/data.md`, `experiment/data.windows.md` (run checks); `e1_delivery.json`; `e1_detection.json` | Section 5 or 6; Table of attempts |
| AG10 | Per-text agreement of four measures per speed (Bland-Altman bias and limits; ICC(A,1)), the biases under three mixtures of speeds, and per-trial differences by scenario and speed. | Question 3; section 6.7 | `e1_l2.json` | Section 7; Figure 4; Table 7 |
| RC1 | Closed-set identification accuracy against the chance level 1/K for six feature sets, K of 10, 100 and 1,000, per cell, with the number of unscored blocks and trials. | Question 4; section 6.8 | `e2_closed_set_<cell>.json` | Section 8; Figure 5 |
| RC2 | The recommended granularity of the key rows (or that none is recommended), decided from the two macOS cells by the registered near-chance rule; the same judgement on Windows as a qualification. | Question 4; sections 6.8, 10.7 | `e2_closed_set_<cell>.json` for the three cells | Sections 8 and 11; Table 8 |
| RC3 | Open-set reconstruction: character error rate of the attack and of the prior-only baseline, their difference, and the difference from the shuffled control, for the attackers K0, K1 and K1+. | Question 4; section 6.8 | `e2_open_set_<cell>.json` | Section 8 |
| RT1 | CPU (mean, median, 95th percentile, maximum), final memory and memory slope of the logger, idle and working, per system; values of the two systems not compared. | Question 5; sections 6.10, 10.9 | `e3_macos.txt`, `e3_windows.txt` | Section 9; Table 9 |
| DS1 | The dataset holds, for each measurement run admitted by the stopping rule, the plan, the record of the presses sent, the reference log, the observation log and the run manifest; the runtime samples; the phrase corpus; the generator settings and the seed; and, as a separate part, the raw logs of the calibration-pilot runs that meet the registered criteria. | Sections 3.1, 3.4, 4.2, 6.10, 10.10; `experiment/pilot-macos.md` and `experiment/pilot-windows.md` (Raw logs) | `experiment/data.md`, `experiment/data.windows.md` (deposits and their SHA-256); `kit/formats/FORMATS.md` | Section 10; Table 10 |
| DS2 | Every deposited log passed the content-free check and the checks of the stopping rule at deposit time. | Section 3.4; `experiment/data.md` (deposit procedure) | Output of `kit/analysis/pipeline.py --pack` and `--check-deposit` | Section 10 |
| DS3 | The dataset supports uses (a) to (c) of section 10 and is limited to synthetic input, the recorded versions, and one kind of reference input field per system. | Sections 2.1, 7, 10.11 | Datasheet released with the data | Section 10 |

## Tables and figures

- Figure 1: the components (generator, executor, input method, reference input field, logger, prediction) and what
  each records.
- Figure 2: recall and precision with Wilson intervals by scenario and speed, per cell, primary comparison and scope.
- Figure 3: Bland-Altman plots of the duration error per cell and speed.
- Figure 4: per-text bias and limits of agreement of the four measures per speed.
- Figure 5: closed-set accuracy against K for the six feature sets, with the chance level, per cell.
- Table 1: observability of the conversion state by interface and system.
- Table 2: the logger's rows and the definitions on each system.
- Table 3: scenarios and procedures per cell.
- Table 4: deviations from the registrations.
- Table 5: detection per speed and cell, for the three comparisons.
- Table 6: per-session agreement.
- Table 7: per-text agreement.
- Table 8: the near-chance judgement and the recommendation.
- Table 9: runtime cost.
- Table 10: contents of the dataset, with the measurement runs and the calibration-pilot runs as separate parts.
- Supplement: the per-stratum tables, generated from the result files.

## Open items before the manuscript is complete

- The bibliographic records of the platform documentation (Microsoft and Apple), of the loggers named in section 2,
  of the datasheet proposal, of the tokenizer used for the readings and of the corpus source are to be confirmed
  against their primary sources when the sections that cite them are drafted.
- The count of accessibility attributes and notifications examined on macOS is to be confirmed on the system version
  of the measurement before it is stated.
- The form in which the list of exported files of each freezing tag can be recomputed from the public repository is
  to be fixed before the release.
- Whether the observation logs of the `working` condition are deposited in addition to the samples is to be stated in
  the datasheet.
