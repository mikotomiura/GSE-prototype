# Datasheet: records of the synthetic-input validation

This datasheet describes the dataset "Logging Japanese IME conversion without recording text: Records of the
synthetic-input validation" (DOI 10.5281/zenodo.23183438). It follows the sections proposed by Gebru et al. (2021):
motivation, composition, collection process, preprocessing, uses, distribution and maintenance. The registrations,
the article and the code repository give the details that are referred to here. Values that are known only when the
files are deposited are marked "(to be filled in at deposit)".

## Motivation

**Purpose.** The dataset holds the records of a pre-registered validation of a logger that records when a Japanese
input method converts input, as the duration of a conversion session, the number of arrow-key presses during it and
whether it was abandoned, without recording any text. The logger's rows were compared with a reference: an input field
that records the calls it receives from the input method. Scripted key presses from a generated plan drove both. The
records are released so that the registered analyses can be re-run from the deposit, and so that other rules that infer
conversions from key presses can be evaluated against the same reference without new measurement.

**Creator and funding.** The dataset was created by Mikoto Miura, an independent researcher (Hiroshima, Japan; ORCID
0009-0000-4196-0508). The work received no funding.

## Composition

**Instances.** The unit of the dataset is a run: one plan, played once by the runner on a measuring machine. A plan
consists of blocks, and a block consists of trials. A trial types the reading of one phrase, or a string of kana made
by the generator, by one of the scenarios S1 to S15 (for example, converting and committing, cancelling, cycling
through the candidates, or bringing another application to the front) at one of three speeds. S9 is never run, and S11
runs only on macOS with live conversion on, so a plan has 14 or 13 scenarios (section 2.3 of the registration). No
instance represents a person.

**Files of a run.** Each run has five files, whose fields are specified in `FORMATS.md` (a run that the runner aborted
may lack a log):

| File | Format | What it holds |
|---|---|---|
| `run.json` | run manifest | The versions of the system, the input method and the programs, the settings of the run, the outcome of the checks of the front window, and the SHA-256 of every log |
| `plan.jsonl` | `plan/1` | The blocks and trials of the plan: scenario, speed, phrase identifier, intended outcome and key schedule, with the SHA-256 of the generator's settings, procedures and corpus |
| `oracle.jsonl` | `oracle/1` | Every press and release as the executor sent it, by key name, with wall-clock and monotonic times; block and trial boundaries; the block-start markers |
| `gt.jsonl` | `gt/1` | The calls that the reference input field received from the input method: kinds, lengths in UTF-16 code units and times; the key codes of key-downs; changes of focus. No text |
| `obs.jsonl` | `obs/1` | The logger's header, its key rows (fourteen categories of key, without key names, with press and release) and its session rows (duration, number of arrow-key presses, abandonment). No text |

**Parts.** The dataset has two parts, which are kept apart.

1. *Measurement runs*, made from the registered plans after the freezes of the registrations:
   - `macos-standard-live-on`: macOS Japanese input method, Romaji input, live conversion on; 3,150 trials in 126
     blocks.
   - `macos-standard-live-off`: the same with live conversion off; 2,925 trials in 117 blocks.
   - `windows-msime-tsf`: Microsoft IME (Japanese), Romaji input, with the reference field that is a client of the
     Text Services Framework; 2,925 trials in 117 blocks (attempt 2).
   - The `working` condition of the runtime-cost study on each system: the logger running while the runner plays the
     plan of `macos-standard-live-on` (macOS) or of `windows-msime-tsf` (Windows). Its logs are deposited under the
     rules of the measurement runs (to be filled in at deposit).
   - The runtime samples of the logger (CPU and memory at 30-second intervals) in the `idle` and the `working`
     condition on each system, as `samples.tsv`.
2. *Calibration-pilot runs*, made before the freezes from other plans, with provisional settings, that meet the
   registered criteria for deposit (`experiment/pilot-macos.md` and `experiment/pilot-windows.md`, section "Raw
   logs"). The candidates are the macOS pilot runs `pilot-1`, `verify-1`, `verify-s5`, `pilot2-on`, `pilot2-off`,
   `verify-off` and `short-1`, the Windows pilot runs with the TSF reference field `short-tsf`, `pilot-tsf`,
   `verify-tsf` and `toolcheck-tsf`, and the three Windows attempts that the runner aborted. The Windows pilot runs
   with the other reference field are not deposited, because that field received the key press that switches the
   input method on as a key-down, which the stopping rule counts as a press from outside. Which candidates pass the
   check at deposit: (to be filled in at deposit).

Shared by both parts are the phrase corpus (`phrases.jsonl`: 1,800 phrases, 150 from each of 12 works, with their
readings in hiragana, 6 to 30 characters long, median 16, and the identifier of the source work), the settings and
procedures of the plan generator and the seed, the specification of the formats (`FORMATS.md`) and this datasheet.

**Files of the deposit.** The deposit holds one archive per run, made by the packing command (section "Preprocessing"),
and the shared files. The SHA-256 of each archive is also recorded in `experiment/data.md` (macOS) and
`experiment/data.windows.md` (Windows) of the code repository.

| File | Part | Contents | SHA-256 |
|---|---|---|---|
| (to be filled in at deposit) | Measurement | `macos-standard-live-on`, attempt 1 | `77bd8a8e64563921a9d3e49fc5fa552a67d4633a66669354852dea651fed49b8` |
| (to be filled in at deposit) | Measurement | `macos-standard-live-off`, attempt 1 | `e1cdf2e8b63ab402a950e37b8841ce302ccb280f396fefc148c8891971d73d10` |
| (to be filled in at deposit) | Measurement | `windows-msime-tsf`, attempt 2 | `f2287a7494b108a7b827f96da48f523e84e1a9478121d03fa82dca2c8749cd06` |
| (to be filled in at deposit) | Measurement | The other runs and the runtime samples | (to be filled in at deposit) |
| (to be filled in at deposit) | Calibration pilot | The pilot runs that passed the check | (to be filled in at deposit) |
| `phrases.jsonl` | Shared | The phrase corpus | `c8f890cb4d0848bf04e6d7d95efe4e4d3dfd02a23eb1c7f103344f14d13e4620` |
| (to be filled in at deposit) | Shared | Generator settings, procedures and seed; `FORMATS.md`; this datasheet | (to be filled in at deposit) |

**Labels.** The reference log is the ground truth: the conversion sessions of the reference are assembled from its
calls by the registered rules, which differ by system (`experiment/gt_rules.json` of the code repository). The plan
states the intended outcome of every trial. The session rows of the logger are the data under test, not labels.

**Missing information, errors and noise.** Every planned trial of the three measurement runs was measured. The records
were not corrected. Known departures are reported per run in the article and in the run records: in the run of
`macos-standard-live-off` the reference field lost the focus once outside the plan, for 2.7 s, and 11 sent presses did
not reach it; key presses are injected and their times depend on the scheduling of the machine; other software ran on
the measuring machines (`experiment/env.md` and the article). The definitions of the reference differ between the two
systems, so measures computed from the reference are not comparable across systems.

**Relationships between files.** Trials and blocks are linked across the plan and the executor's record by their
identifiers. The reference log and the logger's log carry no trial identifiers; they are aligned with the executor's
record by time, using the block-start markers (four arrow-key presses at the start of each block).

**Splits.** None are defined. The registered analyses set scopes of trials (section 6 of the registration).

**Self-containment.** The fields of every file can be read from the deposit alone with `FORMATS.md`. The analyses need
the code release (DOI 10.5281/zenodo.23183441), which is archived separately.

**People and personal data.** No participants were recruited, and no file holds text that a person wrote. The key
presses of every run were generated by a program and sent by the executor. Both the reference log and the logger's log
would record a person's key presses made during a run (the reference by key code, the logger by category). The logs
were checked for key presses that the program did not send, by the stopping rule of the registration (sections 3.4 and
10.8) right after each run and again at deposit; a run that the rule catches is not deposited. The blind spots of the
rule are stated in section 7 of the registration ("The stopping rule counts presses, not keys") and in the article. In
one run (`macos-standard-live-off`) the operator reported a pointer click on another window; no key was pressed. The
observation log of the `idle` condition of the runtime-cost study is not deposited, because it holds the key presses
that started the sampling; only its samples are. The packing command refuses a run whose files hold an absolute path,
the path of the repository, or a login name or home directory given to it. Of the machine, the run manifest records
the platform string, the processor architecture, the Python version and the version of the operating system, not
its host name.

**Offensive content.** The phrases are sentences of literary works whose copyright has expired, selected by length and
by the characters of their readings; they were not screened for content and may contain expressions that some readers
find offensive.

## Collection process

**How the records were made.** The plan generator made each plan from the phrase corpus, the procedures of the
scenarios, the settings and the seed. The runner played the plan: the executor injected the presses through the
interfaces of the operating system into the reference input field, which wrote the reference log, while the
stand-alone logger (`kit/logger` of the code repository) wrote its log. All files were written by these programs
during the runs.

**Machines and versions.** macOS: an Apple Silicon laptop with macOS 27.0.1 (26A434) and the macOS Japanese input
method (Romaji input) for the measurement; the pilots ran on macOS 27.0. Windows: an x86-64 tablet computer with
Windows 11 Home 25H2 and Microsoft IME (Japanese, Romaji input), build 26200.8875 with `IMJPTIP.DLL` 10.0.26100.8875 in
the pilot and build 26200.9457 with `IMJPTIP.DLL` 10.0.26100.9278 in the measurement. Both machines had a JIS keyboard
layout. The learning of the input methods was not
reset. The versions of every run are in its manifest; the measuring machines are described in `experiment/env.md` and
in section 10.4 of the registration.

**Sampling.** The plans were generated from the registered settings with the seed; the plans, their randomisation and
the number of trials per scenario and speed are set out in sections 2.4 and 3.3 of the registration (section 10.6 for
Windows) and in the settings of the generator. The phrases were drawn from the corpus by the generator.

**Who was involved.** The author ran the measuring machines. An AI coding assistant started and monitored the runs, ran
the checks of the runs and the packing, under the author's instructions (see the AI declaration of the article). No
one was paid to take part.

**Timeframe.** The calibration pilots ran before the freeze of the registration of the macOS cells (2 October 2026) and
before the freeze of the Windows addendum (3 October 2026). The macOS runs of the measurement and of the runtime-cost
study were made from 2 to 5 October 2026, and the Windows runs from 4 to 5 October 2026.

**Ethical review.** Not applicable: no participants were recruited, and no person's data were collected.

## Preprocessing, cleaning and labelling

None. The deposited logs are the files that the programs wrote; no value was changed, removed or added. During the
pilots, the observation logs were sealed: each was moved aside unread, and only a copy of its key rows was analysed.
At deposit they are unsealed, which restores the file as the logger wrote it, and deposited whole; their session rows
were not analysed. The packing command stops when a log does not match the SHA-256 recorded in the run manifest. At
deposit, the packing command
(`kit/analysis/pipeline.py --pack` of the code release) bundles only the manifest and the four logs of a run, checks
them as described under "People and personal data", applies the stopping rule and the check of the content-free formats
again, refuses a run that fails or cannot be checked, writes the files in a fixed order with fixed times so that
packing twice gives the same archive, and prints the SHA-256 of the archive. The error output of the programs was not
deposited. The runtime samples are the samples as the sampler wrote them; their summaries are in the code release.

## Uses

**Uses so far.** The registered analyses of the study: detection of conversion sessions, agreement of their duration,
of the number of arrow-key presses and of abandonment with the reference, per session and per text, how far the key
rows reveal the typed text, and the runtime cost of the logger. The result files are in the code repository
(`experiment/results`). An article that reports the study is in preparation.

**Uses that the records support from the deposit alone.** (a) Examining the calls that an input method makes to an
input field, per system and setting, as a basis for re-examining definitions of a conversion. (b) Evaluating another
rule that infers sessions from key presses against the same reference, by applying it to the executor's record or to
the key rows of the logger's log; the prediction of the study is a worked example. (c) Studying how far a key log
without text reveals the text, with the typed phrases known.

**What limits other uses.** The input is synthetic: fixed phrases typed by a program without errors or corrections,
with injected key events, on one machine and one version of each input method per system, with one kind of reference
input field per system and the learning of the input methods not reset. Evaluating a logger that needs other signals,
such as the windows of the input method, is a use of the code rather than of the dataset: it means running the kit
again, which does not reproduce the same reference, because the learning of the input method and the versions differ.

**Uses for which the dataset is not suited.** As a record of human writing, as a benchmark of natural typing, or for
inferences about writers.

## Distribution

The dataset is distributed through Zenodo under DOI 10.5281/zenodo.23183438, under the Creative Commons Attribution
4.0 International licence. The code that made the records and reads them is distributed separately under the Apache
License 2.0 (DOI 10.5281/zenodo.23183441; https://github.com/mikotomiura/ime-conversion-logging). The phrases come from
works whose copyright has expired, obtained from Aozora Bunko (https://www.aozora.gr.jp/), which allows its files to be
copied and redistributed freely and asks that the information recorded in them be kept; the corpus records the
identifier of every source work, and `experiment/data.md` of the code repository lists the source works with the
SHA-256 of the archives downloaded. No other restriction is known to the author. Date of release: (to be filled in at
deposit).

## Maintenance

The dataset is hosted by Zenodo. The contact is the corresponding author, Mikoto Miura, whose address is given in the
article. Corrections will be released as new versions under the same concept identifier, with a record of what
changed; the earlier versions remain on Zenodo. The dataset holds no personal data, so no limit on its retention
applies.
Others may build on the dataset under its licence; additions are not merged into it.

## Reference

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., and Crawford, K. (2021).
Datasheets for datasets. Communications of the ACM, 64(12), 86-92. https://doi.org/10.1145/3458723
