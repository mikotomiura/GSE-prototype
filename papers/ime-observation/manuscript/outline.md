# Manuscript outline

This outline fixes the structure of the manuscript, the evidence for each claim and the rules for reporting before
the results of the measurement are analysed. It contains no result value. Each claim names the registered question and
section that define it, or states that it is not registered; the file from which its values are copied; and the table
or figure that reports it. The pre-registration (`experiment/preregistration.md`, with the Windows addendum in its
section 10) and the record of deviations (`experiment/deviations.md`) take precedence over this outline wherever they
differ.

## Title

Logging Japanese IME conversion without recording text: Observability limits, a cross-platform logger, and a
synthetic-input validation

The title is fixed here and is not changed after the results are known. "Logging" is used because on macOS the
conversion is inferred from key presses rather than observed. "Without recording text" means that no character,
reading, candidate string or window name is written; how much of the text can nonetheless be recovered from a log is
a question of the study (contribution 3).

## Journal requirements to be met

The manuscript is prepared for *Behavior Research Methods* as an original research article. The journal's instructions
for authors require: the conventions of the Publication Manual of the American Psychological Association, 7th edition,
for style, citations and references; double spacing, 1-inch margins and page numbers; a title page with the authors'
names and affiliations and the corresponding author's address, telephone number and e-mail address; an abstract of no
more than 250 words; a section headed Declarations, before the reference list, that keeps every heading of the
journal's list and writes "Not applicable" under a heading that does not apply; an Open Practices Statement
immediately prior to the References section; a data availability statement; data citations with a persistent
identifier in the reference list; and, under the journal's Level 2 of the Transparency and Openness Guidelines, all
relevant information (stimuli, the methods being validated, new analyses) in a trusted repository. Among the
affirmations made at submission is that the manuscript includes appropriate measures of variability and, when
relevant, of statistical power; the precision plan of the registration answers it (section 5.4). The instructions
state no limit on length. They are read again immediately before submission.

## Scope of the claims

- The primary contribution is the estimate of agreement between the logger's rows and the sessions assembled, by fixed
  rules, from the calls that a reference input field received from the input method. The reference is a reference
  input field, not the input method's internal state, and on Windows the reference and the logger record different
  constructs (a composition; a visible window of the input method), so the agreement includes the difference between
  them.
- All input is synthetic, and the procedures were calibrated in pilots so that each conversion ends within its trial;
  a conversion that runs from one trial into the next is excluded, and the fraction of trials excluded for this reason
  is reported next to every primary estimate. No claim is made about agreement in natural typing, about other input
  methods, about applications other than the reference input fields, or about the path from a physical keyboard.
- The checks of the instruments (agreement between plan and ground truth, delivery of the presses, losses of focus,
  clock differences) are reported before the primary estimates and are used to read them, never to exclude trials or
  to adjust values. Which check is used to read which estimate is listed in the claims table (RF1).
- Estimates are reported with their intervals where the registration gives them; the runtime cost, F1, counts and the
  delivery and clock figures are reported without intervals. No threshold of adequate agreement is set and no estimate
  is described with evaluative words. A pooled value is labelled as pooled and is not an estimate of accuracy in
  natural typing; the Wilson interval of a pooled proportion ignores the clustering of trials in blocks and is a lower
  bound of the uncertainty. An estimate in the primary scope is given together with the fraction of trials that the
  scope sets aside and the estimate over all trials.
- The text-recoverability results are reported as they come out. Where a granularity of the key rows does not meet the
  registered near-chance rule, the manuscript says so; where neither granularity meets it, no granularity is
  recommended. The rule judges the identification of one phrase among K candidates in one trial; its margin (2/K) and
  the values of K are design choices, not a criterion of privacy, and the manuscript does not describe any log as safe
  to publish. The judgement concerns the key rows of presses; the session rows, the key rows with times, and on
  Windows the rows of modifier keys and of key releases, were not given to the attacks, and publishing them is not
  evaluated. Identifying a writer from the timing of a log is not evaluated either.
- The observability analysis is an analysis of the documented public interfaces of the two systems; it is not part of
  the registration. It is worded as "no documented interface provides" and not as a proof that observation is
  impossible.
- The manuscript makes no claim of priority. Its difference from earlier loggers is stated as a difference of design,
  in a comparison table: which loggers handle input-method conversion, which read the text, and how each was
  validated.

## Contributions

1. **Observability analysis.** What the conversion state of another application exposes, on Windows and macOS, to a
   program that does not read text, from the documented public interfaces of each system, and why the two systems
   leave different routes: window events of the input method on Windows, inference from key presses on macOS. The
   analysis concerns the operating systems and applies to any input method on them; the agreement concerns the input
   methods measured.
2. **A cross-platform logger and its validation.** A stand-alone logger that writes a category for every key press and
   release and one summary row for every conversion session (duration, arrow-key presses, abandonment), and that
   declares in its log which of its channels it records. Its rows are compared with the sessions assembled from the
   calls that a reference input field received from the input method, in three cells (macOS with live conversion on,
   macOS with live conversion off, Windows with the Microsoft input method), under a pre-registered protocol. The
   estimate of this agreement is the primary contribution of the paper.
3. **Text recoverability.** How accurately an attacker can identify the typed phrase among K candidates, or
   reconstruct the typed reading, from the key rows of a published log, and whether either of two granularities that
   keep no time keeps identification near chance under the registered rule.
4. **Runtime cost.** The CPU time and memory of the logger with the machine idle and with scripted typing, per
   system.
5. **A validation dataset.** The logs of the measurement, with the ground truth of the reference input field, the
   scripted plans and the record of every press sent, the phrase corpus and the runtime samples, released with a
   datasheet. With these records an alternative rule that infers sessions from key presses can be evaluated against
   the same ground truth without new measurement; an observer that needs other signals has to be run again with the
   kit, which does not reproduce the same reference. The dataset is synthetic input in one kind of reference input
   field per system; it is not a record of human writing and not a benchmark of natural typing.

## Rule for the abstract

Fixed before the results. For each cell the abstract reports: (i) recall and precision of detection in the primary
comparison and scope, as the range from the lowest lower end to the highest upper end of the per-stratum Wilson
intervals, with the fraction of trials that the primary scope sets aside; (ii) the bias of `dwell_ms` against the
reference, as the range of the per-speed intervals; (iii) the near-chance judgement of the recoverability study and
the recommended granularity, or that none is recommended; (iv) the mean CPU of the logger in each condition of the
runtime-cost study, without an interval. The values over all trials and every other estimate are given in the tables
of the main text and the supplement and are not quoted in the abstract.

## Section plan

Sections are numbered here for reference; the manuscript follows the heading levels of the APA style.

### Abstract (at most 250 words)

Background (keystroke logging in writing research; input-method conversion in Japanese; loggers that record key
presses or the resulting text do not record the conversion, and loggers that record it read the text). What was done
(observability analysis; logger; validation against a reference input field with synthetic input in three cells;
recoverability attacks; runtime cost; dataset). Results by the rule above. Availability: pre-registrations, code, data.

### 1. Introduction

- Keystroke logging as a method of writing research, and the measures it supports (inter-key intervals and pauses,
  revisions, production rates).
- In Japanese most text passes through an input method: a reading is typed, converted, and accepted, changed or
  abandoned. The conversion is part of the writing process. A logger of key presses does not record it directly: it
  can only be inferred from the presses by rules whose validity has to be shown. A logger of the resulting text does
  not see it at all.
- Logging the conversion directly means reading the composition string, which records the text that a participant
  writes. A logger that writes no text changes what has to be protected when a log is kept or shared, but only if it is
  known what the log records and how much of the text it still reveals.
- The three questions of the paper: what can be logged without reading text; how closely such a log agrees with the
  sessions that an input field receives from the input method; and how much of the text the log still reveals.
- Contributions (the list above). All analyses of agreement, recoverability and the dataset come from the same
  measurement runs.

### 2. Background and related work

- Keystroke loggers for writing research and the dimensions on which they have been compared: whether they work across
  applications, whether they support non-alphabetic writing, and whether they record key-down and key-up times. A
  comparison table (Table 1) places this logger next to Inputlog (by version, since language-specific versions for
  non-alphabetic scripts are being developed), ScriptLog, Translog-II (which records input-method events in its own
  editor together with the text) and a hybrid logger for non-alphabetic scripts that reconstructs the state of the
  text by reading it and was validated with human input against screen recordings. Added dimensions: whether the
  logger handles input-method conversion, whether it reads the text, whether it distinguishes pauses before and after
  a conversion is committed, and how it was validated. Each cell is filled from the primary documentation of the tool,
  with its version and the date it was checked; the cells where this logger is weak are kept (no validation with human
  input, no validation in applications other than the reference fields, no separation of inter-key intervals by script
  layer).
- Studies of writing processes in Japanese and Chinese that use keystroke data: a hidden Markov model of writing
  processes from keystroke data that does not treat the input method; a thesis on writing Chinese with a keyboard in
  which pauses before the selection of characters emerged as a category of their own; an English-to-Japanese
  translation-process corpus whose logs record the keystrokes typed into the input method together with the text; the
  naming of Japanese, with its several scripts and input modes, as future work for a logger of non-alphabetic scripts.
- Keystroke datasets released without the typed text (for example key positions or hand only). Not recording text is
  not new in itself; the design difference here is a log of the conversion that holds no text.
- Validation of timing instruments in behavioural research, which compares software timing with an external device
  and warns that idealised scripts give a best case. This study places its reference at the software layer because the
  construct (a conversion session) exists only in the calls an application receives; an external device would time
  the path of the keys, not the conversion. What this choice gives up (the physical path of the keys, an external clock)
  is stated in section 5.3 and in the limitations.
- What timing and key categories can reveal about text, and that timed records can also identify a writer; this study
  evaluates neither timed records nor writer identification.
- Agreement methods used in this paper (limits of agreement, kappa, intraclass correlation, cluster bootstrap).

### 3. What can be logged without reading text

- Method (stated first): the interfaces examined on each system (for Windows the Text Services Framework, the
  input-method manager, message hooks, accessibility events, UI Automation and the desktop compositor; for macOS the
  text-input client protocol, the accessibility attributes and notifications, the input-method framework, the window
  list and the input sources), the documents read, with their URLs, the dates they were retrieved and the system
  versions they describe, and the criterion for each interface (whether a program running outside the target
  application can obtain the conversion state through it without reading text). The list of documents is given in the
  supplement.
- Windows. The Text Services Framework activates per thread of the calling process, and its sinks are registered on
  objects of that process; no documented call names another process. Documentation for assistive technology states
  that access to the composition string requires creating the thread manager inside the target application. The only
  documented route into every application is a text service loaded into each process, which would replace the user's
  input method. Message hooks that would intercept the input-method messages of other windows load code into the target
  processes. The accessibility events of the input method's windows (show, change, hide), received out of context,
  carry no string in their callback arguments. The text-edit pattern of UI Automation reports the finalized string
  of a composition, so it is not content-free. Some systems cloak the candidate window instead of hiding it, which
  the cloak notifications report. An event for a change of the conversion target exists but is raised by the
  application's accessibility provider, so its presence depends on the application; it is not used.
- macOS. No documented interface reports the marked text of another application: it is held by the in-process
  text-input client protocol of the target application, and no attribute or notification of the accessibility interface
  reports marked text or a composition. An input method runs as a process of its own whose client is the system's text
  services, so there is no counterpart of a text service loaded into the target process. The list of windows shows a
  candidate window, but only by polling and only after a conversion has begun, so it misses the typing of the reading;
  the logger does not use it. The current input source gives the input mode only. The logger therefore infers sessions
  from key presses and the input mode.
- Consequence: the two systems log different constructs (a visible window of the input method; a segment of kana input
  inferred from keys), so the measures of the two systems are defined differently and are validated separately.
- Table 2: interfaces examined, per system, what each exposes, whether it carries text, whether the logger uses it,
  and the source and date.

### 4. The logger

- Rows: one key row per press and release with one of fourteen categories and a time; the input-mode keys produce no
  row on either system, the keys F13 to F19 produce no row on macOS and F13 and the keys above it none on Windows, and
  modifier keys produce rows on Windows but not on macOS. One session row with `t`, `dwell_ms`, `nav` and `abandon`. No character, reading,
  candidate string or window name is written.
- Session rules on macOS (opening at the first letter or digit key, closing by Return or another closing key as
  committed, by Escape as abandoned, by a change to non-Japanese input; Space marks a candidate window as shown; the
  20-second cut-off without a row).
- Sessions on Windows (window events of the input method; the cloaking path with its 150 ms gap and 20-second
  cut-off; the safety valve of the event path at about 25 seconds; `nav` and `abandon` counted system-wide while a
  session is open, so they are upper bounds). A row does not record which path wrote it, and which path drove the
  measured input method was not determined; rows of 20 to 25 seconds and of about 25 seconds are only indications of
  the first path and of its safety valve.
- The log header: the format, the system, the version, the SHA-256 of the manifest of the code it was built from, and
  the channels the log records, so that a log declares what it can and cannot contain.
- The content-free format: closed enumerations for every string, integers with bounded ranges, no unknown keys, no
  escapes. A validator checks this shape on every log. It does not check the meaning of an integer: that no content is
  written into an integer field rests on the logger's source, identified by the manifest's SHA-256.
- What a researcher can compute from such a log (Table 4): for common measures of writing research (inter-key intervals
  and pauses, pauses before and after a conversion is committed, revisions, conversions and their duration,
  abandonment), on each system, whether the measure can be computed from the logger's rows alone, whether this study
  validates it (with the claim that does), and if not, why. The study validates the conversion summaries, the four
  per-text aggregates and the timing of key rows on the software path; it validates no other measure.
- Table 3: row formats, key categories, and the definition of a session, `nav` and `abandon` on each system.

### 5. Validation method

5.1 Overview: three records of each trial (the plan with the intended outcome and the record of every press sent; the
calls that the reference input field received; the logger's rows) and a fourth derived one (the rows that the
logger's rules specify for the presses sent, macOS only). All questions are answered from the same measurement runs.
Figure 1: the components and the data they record.

5.2 Cells and machines: macOS (standard Japanese input method, live conversion on and off, one Apple Silicon machine);
Windows (Microsoft input method with the Text Services Framework reference input field, one x86-64 tablet); the
versions recorded per run, including that the Windows versions at the measurement differed from the pilot's and the
registered check of section 10.8 passed (39 of 39); learning of the input method not reset.

5.3 Reference input fields and ground-truth rules: the macOS client of the text-input protocol and the rule that
assembles sessions from its calls (the 50 ms continuation window for live conversion); the Windows field that is a
client of the Text Services Framework and its rule (a composition from start to end, committed when the committed
length is positive); definitions by system and the common definition. Why the reference is at the software layer and
what that gives up: both records come from software on the same machine, so the agreement is between two software
records and not accuracy against an external standard; the kind of field affects the reference (in the pilot the
two Windows fields committed at different points in one scenario).

5.4 Scenarios, speeds and plans: the scenarios and their procedures per cell (Table 5), calibrated in the pilots so
that each conversion ends within its trial; three speeds with key-interval medians of 480, 240 and 120 ms that follow
published transcription typing of English sentences and span the range of typing speeds without estimating Japanese
typing; think times from 0.2 to 20 seconds; 75 trials per scenario and speed; plans generated from a seed. The
precision plan: the half-widths of Wilson intervals at the planned numbers of trials, the strata that remain under the
cut-off (the smallest with 30 and 31 trials), the design effect of the blocks, and that the number of trials was not
revised after the prediction showed how many trials the cut-off sets aside.

5.5 Calibration pilots and blinding: what the pilots fixed (procedures, ground-truth rules, the stopping-rule
settings, the choice of the Windows reference field); the logger's session rows of the pilots sealed and never read.
On macOS the key rows that were read are the input from which the logger infers its sessions, so the blinding withheld
the logger's output, not its input.

5.6 The specified rows (macOS): the prediction from the presses sent, and the three comparisons (ground truth against
observation, primary; ground truth against prediction; prediction against observation).

5.7 Checks of the instruments: agreement between the plan and the ground truth; delivery of the presses to the
observation and to the reference; the stopping rule (presses from outside, losses of focus, and on Windows the key
rows that no sent press explains); clock differences at the block markers; every attempt and how attempts were counted
(deviation D6).

5.8 Analysis: exclusions; scopes (`under_limit` primary, `over_limit`, `all_trials`); matching by interval overlap;
measures of questions 1 to 3; intervals (Wilson for proportions; percentile bootstrap resampling whole blocks for
continuous measures, kappa and the ICC); missing values reported as null.

5.9 Pre-registration and deviations: a table of the two freezes (dates, tags, the SHA-256 of the lists of exported
files, the OSF registrations), with the reason that the freeze marks of the file carry the date of the second freeze;
the deviations D1 to D6 (Table 6).

### 6. Results: what the reference establishes, detection and per-session agreement

First what the reference establishes (RF1), then questions 1 and 2 per cell, with the comparisons, the scopes, the
layers of the prediction (macOS), the Windows diagnostics, and the timing of the key rows (KT1).

### 7. Results: per-text agreement

Question 3: four per-text measures per speed, the mixtures of speeds, and the per-trial differences by scenario and
speed for reweighting.

### 8. Results: text recoverability

Question 4: the closed-set identification over six feature sets and three values of K, the near-chance rule and the
recommendation from the macOS cells, the Windows judgement reported as a qualification, and the open-set
reconstruction with its baseline and negative control. The feature sets that keep time are reported as estimates
only, because the synthetic key intervals are independent of the keys and carry none of the timing structure of human
typing. The attacker knows the generator and the procedures, and the input has no typing errors, conditions that are
expected to favour identification; this is stated as an expectation, not as a result.

### 9. Results: runtime cost

Question 5 on both systems, two conditions each, reported side by side and never reduced to one figure; the values of
the two systems are not compared, because the samplers measure differently.

### 10. The dataset

Contents, formats, how the data were produced and checked, what was not deposited and why. The dataset has two parts
that are kept apart: the measurement runs, made from the registered plans, and the calibration-pilot runs that meet the
registered criteria, made from other plans with provisional settings. Runs that the runner aborted are included when
they pass the same checks, as the registration states. Licence (data and documents CC BY 4.0, code Apache-2.0), the
repository (Zenodo) and the persistent identifier, maintenance, contact, versioning and errata. A datasheet in the
form proposed by Gebru et al. is released with the data. Intended uses: (a) the calls that an input method makes to
an input field, per system and setting, as a basis for re-examining definitions of a conversion; (b1) evaluating, from
the deposited records alone, another rule that infers sessions from key presses (the prediction of this study is a
worked example); (b2) evaluating an observer that needs other signals by running the kit again, which does not
reproduce the same reference, because the learning of the input method and the versions differ; (c) studying how far a
key log without text reveals the text, with the typed phrases known. Uses for which the dataset is not suited: as a
record of human writing, as a benchmark of natural typing, or for inferences about writers.

### 11. Recommendations for researchers

Only recommendations that set no threshold, each with its basis (a result, a registered rule, or a construct):
(a) measures that are defined differently on the two systems are not compared across systems; (b) the 20-second
cut-off changes a researcher's aggregates in a direction that follows from the rule (lower mean conversion time and
fraction of time converting; conversions per trial and abandonment rate in either direction), and its size depends on
the writing and is not given; on Windows a row's path cannot be read from the log; (c) the recoverability judgement is
stated as registered: whether a granularity is near chance under the registered rule, which is not a privacy
criterion, or that no granularity is recommended; (d) researchers can repeat the validation on their own machine and
versions with the kit, of which the 39-trial check of the registration is the smallest unit, and what that check covers
and does not; (e) agreement in the researcher's own application cannot be measured with this kit. All recommendations
hold for the reference input fields and synthetic input of this study.

### 12. Limitations

The reference is a reference input field, not the input method's internal state, and another application may receive
other calls; the ground truth depends on the rule that folds automatic commits under live conversion; on Windows the
reference and the logger record different constructs, and applications that draw their own candidates were not
tested. The input is synthetic and idealised: procedures calibrated so that conversions end within a trial, no
overlapping presses, intervals independent of the keys, no typing errors, no pauses at word and phrase boundaries,
injected events only, and input modes switched only by the mode keys; for each, the measures it may affect and the
expected direction. The reference is software on the same machine; no external clock was used. The learning of the
input method was not reset; one machine and one version per system, and the Windows versions differed from the
pilot's. S9 (choosing a candidate with the mouse) was not evaluated. The cut-off scope removes trials from the primary
estimates. The Windows `nav` and `abandon` are upper bounds whose excess this design does not exercise, because only
the executor typed. The stopping rule has stated blind spots. Intervals that treat trials as independent are lower
bounds. The recoverability study judges one phrase at a time, evaluates no timed record, and does not evaluate
granularities between milliseconds and one-second bins. Battery use was not measured.

### 13. Conclusions

Including the questions left to other studies: other input methods, other applications, and human typing.

### Declarations

Placed before the reference list, with the journal's headings: Funding; Conflicts of interest/Competing interests;
Ethics approval (Not applicable: no participants were recruited and all input of the measurement was generated by a
program; the deposit checks screen the logs for key presses that the program did not send, with the blind spots stated
in the limitations); Consent to participate (Not applicable); Consent for publication (Not applicable); Availability of
data and materials (the data availability statement, with the persistent identifier of the dataset); Code
availability; Authors' contributions (optional in the journal's list). Acknowledgments, if any, form a separate
section before the reference list.

### Open Practices Statement

Placed immediately prior to the References. The two registrations on OSF Registries (macOS cells:
https://osf.io/9nh7r, DOI 10.17605/OSF.IO/9NH7R; Windows addendum: https://osf.io/4jwzn, DOI 10.17605/OSF.IO/4JWZN);
the code, materials and analysis scripts in a public repository with an archived release and DOI; the data with their
own DOI. The analyses reported as registered are run from the freezing tags; deviations are reported; the
observability analysis and anything labelled exploratory were not registered.

### References

## Claims and evidence

The result files are those named in `experiment/notes.md`. The macOS results are written to `experiment/results/` by
`experiment/run.sh` from the macOS freezing tag; the Windows results to `experiment/results/windows/` by the command
of section 10.7 of the pre-registration from the Windows freezing tag. The files of question 4 are
`e2_closed_set_<cell>.json` and `e2_open_set_<cell>.json`, and those of question 5 are `e3_<system>.txt`. Every
result value in the manuscript is copied from these files by a script kept with the manuscript; no result value is
typed or rounded by hand. Values of the design (settings, plan counts) are copied from the registration.

| ID | Claim | Registered definition | Evidence | Reported in |
|---|---|---|---|---|
| OB1 | On Windows no documented interface lets a program that runs outside the target application read or follow the composition of the Text Services Framework; the only documented route is code loaded into the target process. | Not registered (documentation analysis) | Microsoft documentation of the thread manager, of the sink registration and of input-method accessibility; documentation of message hooks; each with URL and retrieval date | Section 3, Table 2 |
| OB2 | The window events of the input method, received out of context, carry no string; the text-edit pattern of UI Automation carries the finalized string. | Not registered (documentation analysis) | Microsoft documentation of the event callback, the event constants and the text-edit pattern | Section 3, Table 2 |
| OB3 | On macOS no documented interface reports the marked text of another application; the window list shows a candidate window only by polling and only after a conversion has begun; the input source gives the input mode only. | Not registered (documentation analysis) | Apple documentation of the text-input client protocol, the accessibility attributes and notifications (counted on the system version of the measurement), the input-method framework, the window list and the input sources | Section 3, Table 2 |
| OB4 | The two systems therefore log different constructs, which are validated separately and not compared as equal. | Sections 1.1, 10.3, 10.11 (two constructs) | OB1 to OB3; the session rules of the logger | Sections 3, 4 and 11; Table 3 |
| LG1a | Every deposited and analysed log has the content-free shape: closed enumerations for strings, bounded integers, no unknown keys or escapes. | Section 5 (checks before any statistic) | `kit/formats/FORMATS.md` (`obs/1`, scope of guarantee); `kit/formats/validate_logs.py`; the check applied by the analysis and by `--pack` | Section 4 |
| LG1b | The logger writes no character, reading, candidate string or window name; that no content is written into an integer field is a property of its source, which the shape check does not test. | Sections 1.1, 2.2, 10.3 | Logger source in `kit/logger/` and its unit tests; the manifest's SHA-256 in every log header | Section 4, Table 3 |
| LG2a | The macOS session rules are those stated, including the cut-off. | Sections 1.1, 4.5 | Logger source and unit tests (`kit/logger/src/input/ime_compose.rs`); the self-test of `kit/analysis/spec_predict.py` against that source | Section 4 |
| LG2b | The Windows session paths are those stated, including the cut-off and the safety valve; which path drove the measured input method is not known, so the Windows estimates hold for an unknown mixture of the two paths. | Sections 10.3, 10.7 | Logger source and unit tests (`kit/logger/src/driver_windows/` and `kit/logger/src/input/ime_cloak.rs`); no prediction applies | Sections 4 and 12 |
| LG3 | Which common measures of writing research can be computed from the logger's rows on each system, and which of them this study validates. | Not registered (description) | Table 4, each validated entry citing its claim | Section 4, Table 4 |
| RF1 | What the reference establishes and what it does not: the agreement between plan and ground truth by type; the delivery of the presses; the losses of focus of the reference and the observation rows of the trials concerned (reported separately; primary values unchanged); the clock differences; the difference between the two Windows fields in the pilot; no external clock. | Sections 6.2, 6.3, 6.9, 10.7 | `e1_l1.json` (plan against ground truth); `e1_delivery.json`; `e1_detection.json` (rows of trials with a loss of focus); the output of `kit/pilot/clock_sync.py` per run; `experiment/pilot-windows.md` | Section 6, before the primary estimates |
| AG1 | Recall, precision, split rate and merge rate of the session rows against the reference, per cell, scenario and speed, in the primary comparison and scope, with the fractions set aside by the scope and by carry-over and the estimate over all trials. A miss can come from timing or from a difference of construct length as well as from detection, because the matching needs an overlap of 0.5 without correction. | Question 1; sections 6.2, 6.4, 6.5, 6.9, 10.7 | `e1_detection.json` (macOS and Windows), primary comparison `gt_obs` under `under_limit` | Section 6; Figure 2; Table 7 (per speed and cell; on Windows the primary comparison only); per-stratum tables in the supplement |
| AG2 | Difference of `dwell_ms` from the reference session's duration (median absolute difference; Bland-Altman bias and limits of agreement), per stratum. | Question 2; section 6.6 | `e1_l1.json` | Section 6; Figure 3 (per stratum); Table 8 |
| AG3 | Agreement of `abandon` with the session's outcome (raw agreement; kappa per speed), also split by commits followed by a continuation. | Question 2; section 6.6 | `e1_l1.json` | Section 6; Table 8 |
| AG4 | Agreement of `nav` with the arrow presses that the executor sent during the session (the reference for this measure is the executor, not the reference input field). | Question 2; section 6.6 | `e1_l1.json` | Section 6; Table 8 |
| AG5 | Behaviour at the 20-second cut-off: rows of 20 seconds or more, and rows of the long trials against the specified rows (macOS); rows of 20 to 25 seconds and of 25 seconds or more, and the sensitivity analysis of the long trials (Windows), reported descriptively. | Questions 1 and 2; sections 6.6, 10.7 | `e1_l1.json`; `e1_detection.json` (`over_limit`, `under_limit_gt_duration`, `long_trials_from`) | Section 6 |
| AG6 | Separation of the disagreement into the validity of the rules (ground truth against prediction) and their execution (prediction against observation), macOS only. | Section 6.4 | `e1_detection.json`; `e1_l1.json` (`gt_pred`, `pred_obs`, layers) | Section 6; Table 7 |
| AG9 | Every attempt of every run, including attempts aborted, stopped or refused, with its reason and figures, how attempts were counted, and the check of section 10.8; exclusions by reason, stratum and number. | Sections 3.4, 6.2, 10.8; deviation D6 | `experiment/data.md`, `experiment/data.windows.md` (run checks; check of section 10.8); `experiment/deviations.md`; `e1_delivery.json`; `e1_detection.json` | Section 5.7; table of attempts |
| AG10 | Per-text agreement of four measures per speed (Bland-Altman bias and limits; ICC(A,1)), the biases under three mixtures of speeds, and per-trial differences by scenario and speed. | Question 3; section 6.7 | `e1_l2.json` | Section 7; Figure 4; Table 9 |
| KT1 | Timing of the key rows on the software path, per system, descriptive: the delay of each row after its press and the error of each interval between consecutive rows, in the trials where every press arrived. No claim is made about the path from a physical keyboard. | Section 6.3 | `e1_delivery.json` | Section 6 |
| RC1 | Closed-set identification accuracy against the chance level 1/K for six feature sets, K of 10, 100 and 1,000, per cell, with the number of unscored blocks and trials. | Question 4; section 6.8 | `e2_closed_set_<cell>.json` | Section 8; Figure 5 |
| RC2 | The near-chance judgement and the recommended granularity of the key rows, or that none is recommended, decided from the two macOS cells by the registered rule; the same judgement on Windows reported separately as a qualification; with the margin 2/K, the probabilities of the rule at the planned numbers of trials, and the block-resampled interval. | Question 4; sections 6.8, 7, 10.7 | `e2_closed_set_<cell>.json` for the three cells; the table of section 6.8 of the registration | Sections 8 and 11; Table 10 |
| RC3 | Open-set reconstruction: character error rate of the attack and of the prior-only baseline, their difference, and the difference from the shuffled control, for the attackers K0, K1 and K1+. | Question 4; section 6.8 | `e2_open_set_<cell>.json` | Section 8 |
| RT1 | CPU (mean, median, 95th percentile, maximum), final memory and memory slope of the logger, idle and working, per system; values of the two systems not compared. | Question 5; sections 6.10, 10.9 | `e3_macos.txt`, `e3_windows.txt` | Section 9; Table 11 |
| RE1 | Measures defined differently on the two systems are not compared across systems. | Basis: construct (OB4) | OB4; Table 3 | Section 11 |
| RE2 | The direction in which the 20-second cut-off moves each per-text aggregate; its size is not given; on Windows a row's path cannot be read from the log. | Basis: rule (sections 1.1, 6.4, 10.3) | The registered rules; AG5 for the logger's behaviour at the cut-off | Section 11 |
| RE3 | The recoverability judgement as registered. | Basis: result (RC2) | RC2 | Section 11 |
| RE4 | The validation can be repeated on a researcher's machine and versions with the kit; the 39-trial check of section 10.8 is its smallest unit. | Basis: registered procedure (section 10.8) | `kit/run/README.windows.md`; `experiment/pilot-windows.md` (`verify`); the check of section 10.8 in `experiment/data.windows.md` | Section 11 |
| RE5 | Agreement in a researcher's own application cannot be measured with this kit. | Basis: registered limitation (section 10.11) | Section 10.11 of the registration | Section 11 |
| DS1 | The dataset holds, for each measurement run that the registration lets be deposited (completed runs that pass the checks, and runs aborted by the runner that pass them), the plan, the record of the presses sent, the reference log, the observation log and the run manifest; the runtime samples; the phrase corpus; the generator settings and the seed; and, as a separate part, the raw logs of the calibration-pilot runs that meet the registered criteria. | Sections 3.1, 3.4, 4.2, 6.10, 10.10; `experiment/pilot-macos.md` and `experiment/pilot-windows.md` (Raw logs) | `experiment/data.md`, `experiment/data.windows.md` (deposits and their SHA-256) | Section 10; Table 12 |
| DS2 | Every deposited log passed the content-free shape check and the rules of the stopping rule at deposit time, and the plan of every measurement run was checked by hand against the registration. | Section 3.4; `experiment/data.md` (deposit procedure) | Output of `kit/analysis/pipeline.py --pack` and `--check-deposit`; the tables of run checks in `experiment/data.md` and `experiment/data.windows.md` | Section 10 |
| DS3 | The fields of the records support uses (a), (b1) and (c) from the deposit alone; use (b2) needs the kit to be run again. | Not registered (description) | `kit/formats/FORMATS.md` (the fields of `gt/1`, `obs/1`, `plan/1`, `oracle/1`); the prediction as a worked example of use (b1); the datasheet | Section 10 |

## Tables and figures

- Figure 1: the components (generator, executor, input method, reference input field, logger, prediction) and what
  each records.
- Figure 2: recall and precision with Wilson intervals by scenario and speed, per cell, primary comparison and scope.
- Figure 3: difference of `dwell_ms` from the reference duration per stratum (bias and limits of agreement with
  intervals), per cell.
- Figure 4: per-text bias and limits of agreement of the four measures per speed.
- Figure 5: closed-set accuracy against K for the six feature sets, with the chance level, per cell.
- Table 1: comparison of keystroke loggers for writing research.
- Table 2: interfaces examined for logging the conversion state, by system.
- Table 3: the logger's rows and the definitions on each system.
- Table 4: measures of writing research that can be computed from the logger's rows, and those this study validates.
- Table 5: scenarios and procedures per cell.
- Table 6: deviations from the registrations.
- Table 7: detection per speed and cell (three comparisons on macOS, the primary comparison on Windows).
- Table 8: per-session agreement.
- Table 9: per-text agreement.
- Table 10: the near-chance judgement, the properties of the rule and the recommendation.
- Table 11: runtime cost.
- Table 12: contents of the dataset, with the measurement runs and the calibration-pilot runs as separate parts.
- Table of attempts: every attempt of every run with its reason and figures.
- Supplement: the per-stratum tables, generated from the result files; the list of documents of the observability
  analysis.

## Open items before the manuscript is complete

- The bibliographic records of the platform documentation (Microsoft and Apple), of the loggers of Table 1, of the
  studies of timing instruments, of the work on keylogging side channels, of the datasheet proposal, of the tokenizer
  used for the readings and of the corpus source are to be confirmed against their primary sources when the sections
  that cite them are drafted.
- The count of accessibility attributes and notifications examined on macOS is to be taken on the system version of the
  measurement before it is stated.
- Whether literature on evaluating text entry through input methods should be placed in section 2 is to be checked
  against primary sources.
- The form in which the list of exported files of each freezing tag can be recomputed from the public repository is
  to be fixed before the release.
- Whether the observation logs of the `working` condition are deposited in addition to the samples is to be stated in
  the datasheet.
- The full SHA-256 of the check plan of section 10.8 is to be copied into `experiment/data.windows.md` from the run
  manifest of the check.
