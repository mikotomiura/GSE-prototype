# Preregistration: How far do processing steps applied to public keystroke logs protect against matching logs to texts?

> Status: fixed before any data were acquired. The commit of the repository that holds this file, and the SHA-256 of this file, `config.json` and `SEED`, are given in the OSF registration. Every later change follows "Deviations".
> Authoritative version: this English version as registered, together with `config.json` and `SEED` (the SHA-256 of each file is given in the registration). The values of every parameter are in `config.json`.

This document fixes, before any data are acquired, the main computation of a study that asks how far the processing applied to publicly released keystroke logs protects against an attack that matches a log to its text. The planned venue is the Proceedings on Privacy Enhancing Technologies. No pass or fail criterion is set. The values of k, N and the processing levels are experimental settings, not thresholds.

## What was seen before this registration was fixed (disclosure)

At the time of fixing, no log, text or score of the KLiCKe corpus had been opened. Only the following had been seen.

- The KLiCKe paper (Tian, Crossley & Van Waes, 2025): column definitions, tasks, numbers of writers and the table of process measures; the GitHub README; the Inputlog community page (Inputlog, n.d.); the structure of the Google Drive folder (file names and counts, not contents).
- The description pages and rules of the Kaggle competition "Linking Writing Processes to Writing Quality" (The Learning Agency Lab, 2023) and the write-up of its first-place solution (Inubushi, 2024). No values of the competition data were seen.
- ENJA15: on 2026-09-13, one file (`P01_T1.xml`) was downloaded for an unrelated purpose (whether the conversion process of a Japanese input method remains in public data) and its event types were counted (CRITT TPR-DB, 2016). No quantity related to matching was computed, and that file is not used.
- The KeyTAR artifact (Qiu et al., 2026): the description and file list of the Zenodo record (contents not downloaded).
- Three earlier prototypes by the author (lengths of Japanese texts, synthetic input, and a trial on the author's own typing records). The segment rules, the alignment, the penalty λ = 8, the coarsened form R4(w) and its grid of w (1, 2, 4, 8) come from them; λ was fixed in the preregistration of the trial on the author's own records and is not tuned here. No result of those prototypes is used as a value or as a basis for a prediction in this study. The author's own records are not used in this study.
- The pre-freeze check on synthetic logs (section "Check on synthetic logs"; `scripts/synthetic_logs.py`; no human data; results in `notes.md` and `results/synthetic_check.json`). Its results and two rounds of review of the check led to the following changes before fixing.
  - Forms R3, R3-u, R3-t and R7 release the press time (`down_time`) only; `up_time` and `action_time` are dropped. In a simulation in which a drag's duration appears in its hold time, pairs of logs with the same key categories and press times but different contents ("twins") received identical R3 output in only 12 of 304 pairs (4%; 5% for R3-t(100) and 7% for R7(0.25)), because the values of `up_time` and `action_time` were released. No attacker and no utility measure uses hold times. However, because the next key press cannot occur before a drag is released, a drag's duration (and the duration of a held key, when the next press follows its release) remains as a lower bound of the next press interval. With this constraint in the simulation, the revised forms still gave identical output in only 12 of 308 pairs (4%), and only `down_time` differed. A form that releases times cannot remove this path; it is reported as a limitation.
  - Forms R3, R3-u, R3-t and R7 also drop `up_event` (the released key), because a released key that differs from the pressed key (for example in key rollover) could reveal the release order.
  - The navigation category is split into ArrowLeft, ArrowRight, Home, End and other navigation, because attacker A1' moves the cursor with the left and right arrows, Home and End, which a single navigation category does not allow.
  - The modifier category is split into Control and Meta, and other modifiers (Shift, Alt, CapsLock). A shortcut is defined as the next non-modifier press after a Control or Meta press. With a single modifier category, Shift and Control could not be distinguished, and removing every letter after a modifier deleted the first letter of capitalised words (exact recovery of word lengths fell to 0% even in synthetic logs without edits). The held state of a modifier cannot be read because its action time is set to 0 in KLiCKe.
  - After a Control press, attacker A1' moves Home and End to the start and end of the document, and treats the arrows as uncertain.
  - In form R6, letters and digits of strings that do not come from a key press (pasted text, replaced text and removed text) are masked to `q`.
  - The timing table of attacker A3: a character-type pair seen fewer than 20 times takes the value of all intervals; a shortcut press breaks the chain of consecutive character presses.
  - The segment rule keeps a trailing open segment if it contains a counted press.
  - A window is a run of record segments that contains k non-empty segments (empty segments between them are inside the window but not counted). Empty segments arise after a comma or a period followed by a space (11% of segments in synthetic logs without edits); counting them made record windows cover fewer words than the k words of a candidate window.

## Questions

1. How far do processing steps applied to public keystroke logs (the processing used in practice and alternative candidate processing) protect against an attack that matches a log to its text? Accuracy is reported next to the chance level 1/N and next to the accuracy of attacker A0, which uses only the total length of the log.
2. How does the effect change with the columns that are kept (position, word count, separators, times) and with the attacker?
3. After processing, how far can the standard process measures of writing research be computed, and how closely do they agree with the values before processing?
4. In Japanese translation logs written with an input method (ENJA15), how far above the chance level 1/N and above A0 is the accuracy of the same type of matching (differences and 95% intervals)? The word "exceeds" is used only when the lower bounds of the intervals of both differences (to 1/N and to A0) are above 0.

The study does not say that a processing step "works". It says "against this attacker, at this N, the accuracy is this multiple of 1/N and this much above A0".

## Threat model

- **Setting.** A party that releases keystroke logs (a researcher, a provider of educational data, a competition organiser) processes the logs to hide the texts and releases them, as in the `q` masking of the Kaggle competition. The texts themselves exist elsewhere: the same essay is published with its text, teachers, raters or platforms hold the texts, or the essay is published in a class or online.
- **Attacker knowledge.** One processed log and N candidate texts that include the true text (essays on the same prompt). The attacker knows the processing procedure (Kerckhoffs's principle). The attacker may train on public data of the same type (logs before processing paired with texts); in this study, these are the writers of the prompts not used for evaluation, and their texts are never candidates. The attacker does not use the writer's earlier texts, text generated by language models, or links across several publications. The public KeyTAR model (attacker A4) contains a public language model and is reported as a reference outside this threat model. In the taxonomy of Wagner and Eckhoff (2018), the attacker is passive, external, static and has prior knowledge (the candidate set and training data).
- **Goals and harms.** (a) Learning the content of a hidden text (defeating the purpose of the processing). (b) Linking a log and its columns (times, revision process, scores, other columns) to a text and to its writer (where the writer of the text is known, the writing process becomes linked to the writer). This study measures the link between a log and a text that underlies (a) and (b); it does not identify writers.
- **N and settings.** N = 10 (a narrowed candidate set: a small class or a submission list), 100 (a year or course), 1,000 (a large corpus on the same prompt).
- **Closed world.** The true text is always among the candidates. The open world is examined as a diagnostic.

## Data

### KLiCKe (English free writing; Tian, Crossley & Van Waes, 2025)

| Item | Value |
|---|---|
| Condition to acquire | The data are acquired after this registration is fixed. The reply of the authors to an inquiry is not awaited (the terms of use are public; Inputlog, n.d.). If the reply raises a concern about this use, the computation is stopped, the acquired data are deleted, and the course of events is reported |
| Files acquired | Keystroke logs (CSV), essays and human scores of the argumentative writing task only. The demographics file is not acquired (its questionnaire asked for the Mechanical Turk worker ID). If it is bundled in a zip archive, the archive is not extracted and only its SHA-256 is recorded. The typing tests and the vocabulary test are not used |
| Version | Date of acquisition, Drive file IDs, SHA-256 of each file and the GitHub commit, recorded in `data.md` and `config.json` |
| Prompts and writers | 4 prompts, 4,992 writers as reported (1,136 to 1,329 per prompt), recounted in check 1 |
| Exclusion | Writers with a missing log, text or score; writers whose text has fewer than 50 words (runs of letters and digits). Counts are reported. Writers whose final draft rebuilt from the log does not match the distributed text are kept in full-text matching (accuracy is also reported separately by match and mismatch); windows follow the rule in "Windows" |
| Split by prompt | The 4 prompts are split with the seed (`split`) into two pairs. Attackers train on one pair and are evaluated on the other, then the roles are swapped. Every writer is evaluated once |
| Active writing window | From the first key press to the last event whose `text_change` is not empty in R0. This is applied to every form, as a trimming step a releasing party would apply before processing (Tian et al., 2025, §4.1, also removes inactivity at the start and end) |
| Linking | The Kaggle data are not linked to KLiCKe. The Kaggle data were collected with the same procedure as KLiCKe, but whether they contain the same essays is not examined |

### ENJA15 (Japanese translation with an input method; Carl, Aizawa & Yamada, 2016; Zou & Carl, 2026; CRITT TPR-DB, 2016)

| Item | Value |
|---|---|
| Condition to acquire | The license type and terms of use are confirmed in the primary source. The authors of ENJA15 are not contacted |
| Access | The DAV endpoint of the TPR-DB repository. The SVN revision is fixed and recorded in `data.md` |
| Sessions | From-scratch translation (T). The meaning of T, P and D is confirmed in Carl et al. (2016) and Zou and Carl (2026) before acquisition; if it cannot be confirmed, the ENJA15 part is not carried out |
| True text and decoys | The true text is the translation of the log. Decoys are translations of the same source text by other translators |

### The public KeyTAR model (Qiu et al., 2026)

| Item | Value |
|---|---|
| Condition to acquire | The researcher approves the 15 GB download |
| Version | SHA-256 of `keytar.zip` in Zenodo record 17254163 |
| Use | The released fine-tuned model is used as it is (no training on KLiCKe). Its terms of use (`model_licenses`, `ethics.txt`) are read before the main computation; if they do not allow this use, A4 is not run |

## Checks after acquisition and before the main computation

This registration is fixed before data acquisition. After acquisition, and before any value of matching or utility is computed, only the following is done and written in `notes.md` under "Data checks" (check 7 is an exception that computes R0 values of 50 writers only to verify formulas; it computes no value of a processed form and no correlation with human scores). No other quantity is computed.

1. SHA-256 of the files, numbers of rows, writers, writers per prompt and excluded writers, and the number of writer IDs that appear in more than one prompt (if not 0, the logs of an evaluated writer are removed from the training set of the split).
2. Column names, the values of `Activity`, and the values of the pressed keys (the values not in the category map `key_categories` of `config.json`). Also the counts that verify the assumptions of the synthetic-log simulation: rows whose `down_event` and `up_event` differ; rows whose `text_change` contains " => " more than once; Paste rows whose `text_change` is `NoChange`; rows with a shortcut effect (such as paste or undo) whose preceding non-modifier press is not Control (cases where the rule "the next press after Control" fails); modifier rows whose `action_time` is not 0; Leftclick rows whose `activity` is neither a move nor Nonproduction.
3. The share of writers whose final draft rebuilt from the R0 log matches the distributed text (exact match after whitespace normalisation) and the distribution of the normalised edit distance.
4. The share of agreement between the segment values counted from the log with the segment rule (below) and the values counted from the true correspondence in R0 (the error of the rule).
5. ENJA15: numbers of sessions, translations, translators per source text, and source texts per translator (whether translators and source texts are crossed or nested; this decides the resampling in the ENJA15 part), and the values of `Type` and `IMEtext`.
6. A4: inference time and GPU memory for one log drawn with the seed (no reconstruction or matching value is looked at). The default settings of KeyTAR (beam width and others) are recorded in `data.md`.
7. Verification of the utility formulas: among writers whose Inputlog values are in the distribution, 50 writers drawn with the seed (`check7`) (all of them if fewer than 50). For each of the 10 measures, the R0 value computed with our formulas is compared with the Inputlog value distributed with KLiCKe (if any): Spearman correlation and absolute difference (and whether both use the same active writing window). No correlation with human scores is computed. A measure "disagrees" if the Spearman correlation is below 0.9 or the median absolute difference exceeds 10% of the median R0 value; its formula is then revised and reported as a deviation (the result of the formula before revision is also reported). A formula is revised at most once, and the revised formula is not re-verified on the same or other writers (this is reported). If no Inputlog values are distributed, check 7 is not done and this is reported (Inputlog is not run by us).

The values of checks 3 and 4 do not change the procedure. Writers who do not match in check 3 stay in full-text matching, and windows follow the rule in "Windows". The error in check 4 is reported with the tables, and the segment rule is not changed.

If column names or values differ from what is assumed here and the procedure has to be changed, the procedure before and after is recorded as a deviation. Attackers and exclusion rules are not changed after looking at check values (if they are, it is a deviation, and the result before the change is also reported).

## Release forms (processing)

Fixed per column. KLiCKe columns: `event_id`, `down_time`, `up_time`, `action_time`, the pressed key (`down_event`, `up_event`), `activity`, `text_change`, `cursor_position`, `word_count` (names are confirmed in check 2).

| ID | Pressed key | activity | text_change | position | word_count | Times (down, up, action) | Table |
|---|---|---|---|---|---|---|---|
| R0 No processing (reference) | as is | as is | as is | as is | as is | as is | main |
| R1 `q` masking (as in the Kaggle data) | letters and digits to `q` | as is | letters and digits to `q` | as is | as is | as is | main |
| R2 Categories; position and word count kept | category | dropped | dropped | as is | as is | as is | main |
| R3 Categories; position and word count dropped | category of the pressed key only (`up_event` dropped) | dropped | dropped | dropped | dropped | down only (up and action dropped) | main |
| R3-u R3 with characters and separators merged | category, with letters, digits, space, punctuation and Enter merged into "char" | dropped | dropped | dropped | dropped | down only | main |
| R3-t(w) R3 with rounded times | category | dropped | dropped | dropped | dropped | down rounded to floor(t/w)·w, w = 10, 100, 1,000 ms | main |
| R4(w) Segment values only | none | none | none | none | none | none | main |
| R7(p) Suppression | presses dropped from R3 | dropped | dropped | dropped | dropped | down of the remaining presses | main |
| R5 Substitution (our definition, after the name in Vassallo et al., 2017) | letters and digits to a random QWERTY neighbour | as is | the same substitution | as is | as is | as is | appendix |
| R6 Permutation (likewise) | identities of typed letters and digits (input and the typed side of a replacement) permuted within each segment | as is | the same permutation for typed characters; letters and digits of strings that do not come from a press (pasted, replaced and removed text) masked to `q` | as is | as is | as is | appendix |

- Categories: letter, digit, space, punctuation, BackSpace, Delete, Enter, ArrowLeft, ArrowRight, Home, End, other navigation (ArrowUp, ArrowDown, PageUp, PageDown), Control and Meta, other modifiers (Shift, Alt, CapsLock), mouse, and other (16 categories). R3-u merges letter, digit, space, punctuation and Enter into "char". The map is `key_categories` and `key_categories_detail` in `config.json`.
- Forms R3, R3-u, R3-t and R7 release `event_id`, the press time and the category of the pressed key only. Release times and hold times are dropped because they carry the duration of a drag or of a held key, and the released key (`up_event`) is dropped. A drag's duration (and that of a held key, when the next press follows its release) remains as a lower bound of the next press interval; a form that releases times cannot remove this (see "What is not concluded").
- R4(w): segments are built from the R0 categories with the segment rule below, and only the sequence floor(value/w) (w = 1, 2, 4, 8) is released.
- R7(p): each event (a press and its release) is dropped independently with probability p (0.1, 0.25, 0.5), and `event_id` is renumbered.
- R5 to R7 are our definitions after the names in the abstract of Vassallo et al. (2017), whose full text was not available free of charge; they do not reproduce that work.
- The `@` masking of Edwards, Hart and Shrestha (2023) is not in the table and is discussed in the text.
- KLiCKe sets the action time of modifier keys to 0 (Tian et al., 2025, §2.1.5). No attacker uses hold times (they remain in R0, R1, R2, R5 and R6).
- Columns not in the table (such as Pause Time, listed in Tian et al., 2025, §2) are dropped in every form except R0. No form keeps a column derived from times (R3-t does not release columns that could be recomputed from rounded times). If check 2 finds columns not in the table, they are dropped by this rule and listed.
- R3-t(w) differs from R3 only in its times; attackers that do not use times (A0, A1', A2) give the same values as in R3. The effect of times is read as differences in A3.

### Check on synthetic logs (before fixing)

On synthetic logs that include deletion, deletion of a selection, replacement, paste, movement (arrows, Home, End, mouse) and undo (`scripts/synthetic_logs.py`; no human data), it is checked whether the segment lengths can be recomputed from the columns each form releases. The paths are differences of `position`, differences of `word_count`, `activity`, the number of events, press intervals, and replay of the category column as an editor (A1'). In R2 the lengths are expected to be recoverable, and this is reported. In addition: for R7(p), the share of logs in which the path of the true text is cut, the share of true groups above the cap, the inflation of the true text's cost by the cap (cost with the cap minus cost with groups up to 10), and, as a secondary quantity, the difference between the true text's cost and the cost of the true correspondence; the behaviour of the wrapper added to the template `align.py` (fixed full-text end; replaced group list for R7, including logs in which groups of 4 or more are chosen); and how much one replay error lowers the timing term of the true text in A3 on R3-u. This check is done before fixing, and its results and the revised forms are part of the fixed version. Any change of forms or rules is recorded in "What was seen before this registration was fixed". If a path other than A1' is found in R3, R3-u, R3-t or R7, the form is revised before fixing.

**Results** (2026-10-12; numbers in `notes.md`; quantities that depend on the simulation's assumptions should be read with them):

- Column paths: the output of the R3 family is a function of the key categories and press times by definition of the forms. This was confirmed on the implementation with twins (308 pairs that share the category sequence and differ only in hidden choices: mouse targets, extents of selections, pasted words, letters). With timing that does not depend on content, R3, R3-u, R3-t(100) and R7(0.25) gave identical output in every pair, and R0, R1 and R2 differed in every pair (in R2 through `cursor_position` and `word_count`). Mutations that keep a column (`cursor_position`, `up_time`) make this check fail. Hence there is no path through position, word count or `activity` in the R3 family; the number of events equals the length of the category column.
- Time path: in a simulation in which a drag's duration appears in its hold time and the next press follows the release, the revised R3 family gave identical output in only 4% of pairs (12), and only `down_time` differed. A drag's duration remains as a lower bound of the next press interval (a limitation; held keys were not simulated). Before revision, the value itself was released in `up_time` and `action_time`.
- R2: rebuilding from `position` recovered the word-length sequence exactly in 64% of logs with light editing (A1' alone: 19%).
- R7(p): in logs without edits (200), the share of true groups above the cap was 0.01%, 0.3% and 1.2% of groups (p = 0.1, 0.25, 0.5). The path of the true text was never cut, in full texts or in windows (k non-empty segments, k = 5 to 50). The inflation of the true text's cost by the cap (capped cost minus the cost with groups up to 10) occurred in 0.5%, 9.5% and 41% of logs, with a mean of 0.0005, 0.004 and 0.019 per word and a maximum of 0.11, 0.17 and 0.26 per word. Groups of 4 or more were chosen in 51% (p = 0.25) and 99.5% (p = 0.5) of alignments.
- Wrapper: the fixed full-text end, the handling of infinity (all candidates infinite; only the true text infinite), the replaced group list with `max_group`, and the treatment of a negative text segment as an input error (not as "no path") were confirmed in the self-test (with a window end, the wrapper returns the same groups as the template `align.py`).
- A3 on R3-u: with one replay error at relative position f of the final draft, roughly a fraction f of the gap between the true text's timing term and the mean of the decoys remained (median share remaining at f = 0.1, 0.5, 0.9: 0.07, 0.48, 0.90 for an extra character, 0.10, 0.50, 0.91 for a missing character). After the error the correspondence is shifted, and later timing terms fall to the level of the decoys. The timing term of A3 on R3-u in effect uses only the part before the first replay error (added to "What is not concluded").

## Segments

| Object | Rule |
|---|---|
| Text (English) | A word is a run of letters and digits; the segment value is the number of letters and digits in the word. Other characters separate words |
| Log (category column) | A letter or digit press adds 1, a BackSpace press subtracts 1, and a space, punctuation or Enter press closes the segment. If the next non-modifier press after a Control or Meta press is a letter or digit (in R3-u, a "char"), it is a shortcut and is neither counted nor a separator (the held state cannot be read from the times because the modifier action time is 0). Navigation, modifiers, mouse, Delete and other presses are neither counted nor separators. A trailing open segment is kept if it contains a counted press. Deletion of a selection, paste and replacement cannot be seen in the category column and are counted with this rule as they are (the error is reported in check 4 against the true correspondence in R0) |
| Text (Japanese, ENJA15) | The translation is split at punctuation (、。，．) and line breaks; the segment value is the standard number of keystrokes to type the reading of the segment with an input method (the conversion table `romaji_table.py` of an earlier prototype and the readings of SudachiPy; versions in `config.json`) |
| Log (ENJA15) | Among events with `Type="IME"` or `Type="insert"`, a letter press adds 1 and `[Back]` subtracts 1; a press whose committed string contains punctuation closes the segment |

## Alignment (common to A1, A1', A2 and A3)

- A group is "p record segments to q text segments", with (p, q) in (1,1), (2,1), (1,2), (3,1), (1,3) (the `ORDER` of the template `align.py`). The cost is |record sum − text sum| + λ × (p − 1 + q − 1), with λ = 8 (not tuned).
- Among paths of equal cost, the group earlier in `ORDER` is chosen; where the end point can be chosen, the smaller text position.
- End point: in window matching the whole record is used and the text may end early. In full-text matching both the record and the text are used to the end (the end point is fixed at (number of record segments, number of text segments)).
- Only for R7(p), the group sizes are extended: when suppression drops a separator press, one record segment corresponds to several text segments. The upper bound of q in (1,q) and of p' in (p',1) is ceil(3/(1 − p)) (4 at p = 0.1 and 0.25, 6 at p = 0.5). The groups are ordered as (1,1), then by increasing p' and q, with (p',1) before (1,q) of the same size (the lists are given per p in `alignment.r7_groups` of `config.json`). The cost formula is the same. The cap is fixed; the inflation of the true text's cost by the cap is measured on synthetic logs and reported. The R7 alignment uses a cost that ignores the binomial variance; it is not a likelihood-based attacker (see "What is not concluded").
- A candidate with no path has infinite cost (it is never chosen). If all candidates are infinite, all candidates tie (1/N). For each form and attacker, the number of cases with "all candidates infinite" and with "only the true text infinite while a decoy is finite" is reported separately.
- The template `align.py` (`scripts/align.py`, SHA-256 `6c03dc66afa563903c2d65e90e7247c1faafeb32fe614209c31353f066e07543`) implements the window end only. The fixed full-text end, the handling of infinity and the R7 groups are added as a wrapper (`scripts/align_ext.py`) and were checked on synthetic logs. Because the template's `ORDER` is fixed and `max_group` (default 3) can only narrow the groups, for R7 the group list itself is replaced and `max_group` is set to the cap (4 or 6).

## Attackers

All attackers know the processing. Attackers that need training (A2-b, A3) use the R0 logs and texts of all writers of the two prompts not being evaluated, and apply the same processing as the evaluated form to the training logs.

| ID | Forms | Procedure |
|---|---|---|
| A0 Total length | all | The candidate minimising the absolute difference between the number of letter and digit presses minus BackSpace presses in the log (R3-u: "char" presses minus BackSpace; R7: counted the same way on the remaining presses and multiplied by 1/(1 − p)) and the number of letters and digits in the candidate (R3-u: all characters). In R4(w): the sum of the record's segment values against the sum of floor(value/w) over the candidate's segments |
| A1 Final-draft lengths | R0, R1, R2, R5, R6 | Rebuilds the final draft from `text_change` and `position` (R2: categories and `position`), as in Inubushi (2024), and aligns its word-length sequence with each candidate's word-length sequence over the full text; the candidate with the minimum cost |
| A1' Editor replay | R3, R3-t, R7 | Replays the category column as an editor: a character press inserts at the cursor; BackSpace deletes to the left and Delete to the right; ArrowLeft, ArrowRight, Home and End move the cursor (lines are separated by Enter); other navigation and mouse put the cursor at the end (uncertain); after a Control press, Home and End go to the start and end of the document and the arrows are uncertain (cursor to the end); shortcuts are ignored. All of this uses the category column only. The word lengths of the replayed draft are compared as in A1. In R7, against the candidate's word lengths multiplied by (1 − p) |
| A2 Segment alignment | R2, R3, R3-t, R4, R7 (R4 and R7 apply the same processing to candidates: floor(value/w) for R4, (1 − p)·value for R7) | The candidate whose segment sequence has the minimum alignment cost with the log's segment sequence |
| A2-b Boundary estimation | R3-u | A logistic regression trained on the training logs (processed to R3-u) predicts whether each "char" press is a separator (space, punctuation, Enter). The predicted separators of the evaluated log form segments, compared as in A2. Features and regularisation in `A2b` of `config.json` |
| A3 Timing | R0, R1, R2, R3, R3-t, R3-u, R5, R6 (R7: the segment-duration version) | From the training logs, the mean and variance of the log interval are estimated for each character pair (previous character, next character); pairs seen fewer than 20 times take the value of their character-type pair, and type pairs seen fewer than 20 times take the value of all intervals. For each segment of the evaluated log without BackSpace, the log-likelihood of its interval sequence under the character pairs of the corresponding candidate segment (from the A2 alignment of the record segments with the words of the candidate; it can be built in every form that releases key categories, so A3 on full texts in R0, R1, R5 and R6 also uses it; R7 uses the R7 groups) is summed; the candidate with the maximum. R3-t uses the probability of the rounding interval. R3-u uses a combined score of length and timing: the A1' replay (in R3-u, Enter is merged into "char" and lines are unknown, so Home and End are also uncertain and put the cursor at the end) gives the sequence of "char" items of the final draft, which is matched one-to-one from the start with all characters of the candidate (including spaces and punctuation). Timing terms use only pairs of adjacent final characters that were consecutive "char" presses in the log (modifier and navigation presses are skipped; a shortcut press breaks the chain), up to the length of a shorter candidate. The length term is the log-likelihood of the difference between the replayed "char" count and the candidate's character count under its empirical distribution with additive smoothing (estimated on training logs processed to R3-u and replayed by A1'; the table of character-pair intervals comes from the R0 training logs). The score is the sum of the two terms, and the candidate with the maximum. Two versions of the timing term are reported, the sum and the per-term mean of the log-likelihood, and A3 on R3-u is the maximum of the two. A candidate with no timing term has a timing term of 0. A length-only version is reported as secondary, to separate the contribution of timing. For R7, the log duration between the first and last remaining press of a segment is evaluated with a regression on the log of the candidate segment's character count (estimated on training logs with the same suppression) |
| A4 KeyTAR (non-adaptive reference, outside the threat model) | R0, R1, R2, R3, R3-t | Only letter, digit and space presses are taken; their interval sequence is cut into chunks of 20 record segments (words), each chunk is given to the public model to reconstruct the text (beam width and other settings are the artifact's defaults, recorded in `data.md` at check 6), and the candidate (in windows, the candidate window) with the minimum normalised edit distance to the concatenated reconstruction is chosen. KeyTAR assumes standard English input (Qiu et al., 2026). It is not fine-tuned, does not adapt to the processing, and is not part of the "strongest attacker" in the main tables |

- Because A4 is computationally expensive, 125 writers are drawn from each prompt (500 in total, seed `eval_sample`), and the main tables report all attackers on these 500 writers. A0 to A3 on all writers are reported in the appendix. If A4 cannot be run on the local GPU and the number of writers has to be reduced, only the A4 rows use the reduced sample, and the main tables stay at 500 writers (recorded as a deviation).
- No attacker uses a column that its form does not release.
- The writer identifier is the string of the distributed ID column, used verbatim in the seed derivation (`writer`).

### Attackers on windows

Windows are defined on the R0 segment sequence. A window is a run of R0 record segments that contains k non-empty segments (segments with a counted press; empty segments between them are inside the window but not counted). Its rows run from the row after the separator before the first segment to the separator that closes the last segment (including mouse, navigation and modifier rows in between). Each form takes these rows and re-segments them with its own rule, so every form starts from the same range of presses. Because the ends of a window coincide with R0 word boundaries, the attacker knows both boundaries even in forms that hide separators (R3-u) or drop presses (R7). This favours the attacker, and window results are read with this condition (the difference between R3 and R3-u in windows may be smaller than for fragments released in practice).

| Attacker | Input and comparison in windows |
|---|---|
| A0 | The value counted from the window's presses as in the full text, against the candidate window's number of letters and digits (R3-u: all characters; R4: the sum of floor(value/w)) |
| A1, A1' | Not run in windows (they rebuild the final draft, which a part of the process does not determine) |
| A2, A2-b | The window's segment sequence is aligned with the candidate window's segment sequence using the window end. In windows, A2 is also applied to R0, R1, R5 and R6 (every form tells key categories, so segments can be built; R4 uses the segment values) |
| A3 | On the A2 alignment (R3-u: the A2-b segment alignment), the same likelihood as in full texts. The A3 on R3-u uses the one-to-one A1' correspondence in full texts and the A2-b alignment in windows, so the difference between full texts and windows also reflects the mechanism (noted in the report). In windows, A3 on R3-u uses only the timing term (the length term is part of A0's window count) |
| A4 | The interval sequence of the window's presses is reconstructed and compared with the candidate window |

## Candidates, scope and numbers

| Item | Value |
|---|---|
| True text | The distributed text of the log's writer |
| Decoys | N − 1 texts drawn uniformly without replacement from the distributed texts of all writers of the same prompt after exclusion (except the log's writer). Because of the split by prompt, no training writer's text is a decoy |
| N | 10, 100, 1,000 |
| Draws | Per log, 20 draws for N = 10 and 100, 5 draws for N = 1,000 |
| Scope | Full text, and windows (k non-empty segments, k = 5, 10, 20, 50) |
| True window | Replaying the R0 log gives, for each press, the character of the final draft it became (the true correspondence). The true window is the k text words starting at the word that contains most of the surviving characters of the window's first segment. The true correspondence is built once in R0, and every form and attacker uses the same true windows. Windows whose first segment has no surviving character, and windows that run past the end of the text, are not used. For writers whose final draft (the R0 replay) does not match the distributed text, the words of both are aligned after whitespace normalisation (word edit-distance alignment; among equal costs, match, substitution, deletion and insertion in this order, then the smaller text position), and only windows whose first word maps to a word of the distributed text are used. Windows that do not map are not used and are counted |
| Decoy windows | One window of length k drawn uniformly from the valid windows of each decoy text |
| Window starts | 5 per log, drawn uniformly from the valid starts |
| Ties | 1/m when the true text is among m tied candidates |
| Too few | If a prompt has fewer than N valid writers, its cell for that N is not reported (counts reported). Logs with no valid window of length k are excluded from that k (counts reported) |
| Intervals | Percentile bootstrap with writers as units, 2,000 resamples, 95%, stratified by prompt. Cells of the same sample (500 writers or all writers) use the same resamples. The resamples for the 500-writer sample and for all writers are drawn separately with the same seed derivation (`use` = `bootstrap`, with the sample name in the `writer` field: `main500` for the 500 writers and `all` for all writers) |
| Random numbers | `seed = int.from_bytes(sha256(f"{SEED}:{use}:{prompt}:{writer}:{N}:{k}:{draw}".encode()).digest()[:8], "big")` is passed to `numpy.random.default_rng`; unused fields are empty strings. `use` is one of `split`, `eval_sample`, `decoys`, `window_start`, `r5_sub`, `r6_perm`, `r7_drop`, `bootstrap`, `enja_decoys`, `negative_control`, `check7` and `synthetic` (the check on synthetic logs) |

## Reported quantities

- **Main quantities**: for each form, attacker, N and scope, the accuracy and its interval, the multiple of 1/N, and the gain over A0 (difference in accuracy and its interval).
- **Strongest attacker**: for each form, the maximum over the adaptive attackers available in that form (A0 to A3, A1', A2-b). Its interval takes the maximum again within each bootstrap resample, and the share of resamples in which each attacker is selected is reported. A4 is reported in a separate row.
- **Contrasts between forms**: the difference of the strongest attacker's accuracy and its interval for adjacent pairs: R1 − R2 (from `q` masking to categories, and dropping `activity` and `text_change`), R2 − R3 (dropping position and word count together), R3 − R3-u (separators), R3 − R3-t(w) (rounding of times; attackers that do not use times give a difference of 0, so the A3 difference is also reported). R1 − R2 and R2 − R3 change several columns at once. R3 − R3-u and R3 − R3-t change one column, but in R3-u the available attackers also change (A2-b instead of A1' and A2; A3 uses the combined score), and in R3-t the likelihood of A3 also changes (probability of the rounding interval), so these differences contain both the column and the attacker. No form drops all times (the coarsest rounding, w = 1,000 ms, stands in for it).
- **Secondary**: rank of the true text (top-5 accuracy, mean reciprocal rank); the distribution of accuracy per writer (10th, 50th, 90th percentiles); A2 with λ = 4 and 16 (N = 1,000, full text); the open-world diagnostic (the AUC separating the strongest attacker's minimum cost over candidates that include the true text from the minimum cost over candidates without it; N = 1,000, full text); accuracy split by match and mismatch of the rebuilt draft; counts of missing paths.

## Utility

The measures are the 10 in Table 5 of Tian et al. (2025): mean P-burst length (2 s), mean R-burst length, mean pause (intervals over 200 ms), mean within-word pause, mean between-word pause, mean deletion length, deletion proportion, mean insertion length, insertion proportion, and the variance of production rate over 10 equal intervals. Definitions follow Table 5, computed with our own formulas. R-bursts are delimited by insertions or deletions as in Table 5 (runs up to a pause over 2 s ending in a revision or an insertion away from the leading edge). The deletion length is counted per run even in R0 (the sum of deleted characters over consecutive deletion events; Table 5, "one deletion activity"). The variance of production rate is the standard deviation, relative to the "task maximum" of Table 5: the production rate of each interval (character presses divided by the interval duration) is divided by the maximum interval rate over all writers of the same prompt after exclusion in R0 (the same denominator for every form and sample), and the standard deviation over the 10 intervals is taken (Tian et al., 2025, give no operational definition of the task maximum; this is ours). The formulas are in `utility.formulas` of `config.json`. R0 and every processed form are computed with the same code, and Inputlog values are used only to verify formulas in check 7. Characters are counted as character presses, word boundaries as separator presses (space, punctuation, Enter), and pauses as intervals between presses (also in R0). In R0, deletions and insertions are counted from `activity`, `text_change` and `position`.

"ok" means computed with the same inputs and formula as R0, "approx" means computed from other inputs with the approximation rules below, and "none" means not computed. The cells are fixed before seeing data:

| Measure | R0, R1, R5, R6 | R2 | R3 | R3-u | R3-t(10, 100) | R3-t(1,000) | R7 | R4 |
|---|---|---|---|---|---|---|---|---|
| P-burst | ok | ok | ok | ok | approx | none | approx | none |
| R-burst | ok | approx | approx | approx | approx | none | approx | none |
| Mean pause (200 ms) | ok | ok | ok | ok | approx | none | approx | none |
| Within-word and between-word pauses | ok | ok | ok | none | approx | none | approx | none |
| Deletion length and proportion | ok | approx | approx | approx | approx | approx | approx | none |
| Insertion length and proportion | ok | approx | approx | approx | approx | approx | approx | none |
| Variance of production rate | ok | ok | ok | ok | approx | approx | approx | none |

Approximation rules: the character count is the number of character presses; a deletion is one character per BackSpace or Delete press; an insertion is a character press while the A1' cursor is not at the end; a word boundary is a separator press; counts in R7 are multiplied by 1/(1 − p).

Samples: the summary table and figure use the same 500 writers as the main matching tables. The appendix also gives all writers after exclusion (4 prompts). The random processing of R7, R5 and R6 is applied once per log, and the same processed logs as in matching are used (seeds `r7_drop`, `r5_sub`, `r6_perm`).

Reported: for each measure and form, (a) the Spearman correlation with the R0 value, (b) the median and the 10th and 90th percentiles of the ratio to the R0 value (writers whose R0 value is 0 or undefined are left out of that ratio, with counts per measure and form), and (c) the Spearman correlation with human scores for R0 and each form side by side. Everything is reported per prompt, with the mean and range over the 4 prompts. Intervals are percentile bootstrap with writers as units, stratified by prompt, 2,000 resamples, 95% (the same resamples as the matching cells of the same sample). Whether processed logs can be written in the Inputlog format (.idfx) is described (optional).

## Summary table and figure

Table: full text, 500 writers, one table for N = 1,000 and one for N = 10 (the small setting of the threat model). Rows: the main forms (R0, R1, R2, R3, R3-u, R3-t(w), R4(w), R7(p)). Columns: accuracy of A0; accuracy and interval of the strongest attacker; the selected attacker (by point estimate, and the share of bootstrap resamples per attacker); multiple of 1/N; gain over A0; numbers of utility measures that are computable, approximate or not computed; the median Spearman correlation with R0 over the 10 measures (the same definition and the same 500 writers as the vertical axis of the figure). R5, R6 and A4 are in tables of the same form in the appendix. All cells are given in the appendix; no cell is selected for being favourable.

Figure: horizontal axis, the strongest attacker's multiple of 1/N (N = 1,000, full text); vertical axis, the median Spearman correlation with R0 over the fixed set of 10 measures (a "none" measure counts as 0, an "approx" measure counts with its approximate value; markers show the numbers of "none" and "approx"). R4 has all 10 measures "none", so its vertical value is 0, and the figure notes this. The main forms are plotted, and the forms not dominated on both axes (the Pareto front) are described.

Reading: the table and figure are material for choosing a processing step; no rule recommends a form. The paper states "against this attacker and at this N, this form had this multiple and kept this much utility", and leaves the decision to the releasing party.

## Predictions (written before results; a miss does not change the conclusions)

Predictions of the strongest attacker's accuracy at N = 1,000 on full texts, adopted by the researcher (the proposals were written by the AI assistant; see "Use of AI").

| Form | Prediction | Reason |
|---|---|---|
| R0, R1, R2 | 95% or more | The word-length sequence of the final draft is recovered from the columns (the reconstruction of Inubushi, 2024). A sequence of several hundred words is nearly unique |
| R3, R3-t | 80% or more | Navigation keys remain as categories, and A1' recovers most of the shape of the final draft; it fails after mouse use and vertical movement |
| R3-u | 10% to 60% | Separators can only be inferred from times (A2-b). A3 combines narrowing by the length term (difference in the number of all characters) with the character-pair interval term |
| R7(p) | Falls with p; below 30% at p = 0.5 | Segment values are disturbed by binomial variation |
| R4(w) | At w = 1 about as high as A2 on R3; at w = 8 about as high as A0 | Coarsening removes the information in the length sequence |
| R5, R6 (appendix) | 95% or more | Word lengths are preserved |
| A4 (appendix) | Below 10 times 1/N | KeyTAR was trained and evaluated on short texts without revision (Qiu et al., 2026) |

## Diagnostics

- Negative control: the log is swapped for the log of another writer B of the same prompt and matched in the same way (the true text stays the same; B is drawn per log from all writers of the same prompt after exclusion in the evaluation pair with seed `negative_control`, `draw` empty). Decoys are N − 1 texts drawn with the `decoys` seed from the population without B and the log's writer (there are always N candidates). Scope: the main forms, the strongest attacker, N = 10 and 1,000, full texts and the 500 writers (with the same numbers of draws as the main computation). The strongest attacker is fixed to the attacker selected by the point estimate of the main computation for the same form, N, full texts and 500 writers; it is not selected again within the negative control, because the maximum over attackers that are all at 1/N lies above 1/N. The value for each adaptive attacker is also reported. Accuracy near 1/N is expected.
- Bias of true windows: the distribution of the A2 alignment cost at the true window's position is shown next to the distribution of the alignment cost of the whole log (to see whether true windows sit at positions that favour the alignment).

## ENJA15

- Forms: R0j (no processing), R3j (categories: romaji letters, conversion and commit keys, `[Back]`, commits of punctuation, Enter, navigation, other; the `Type` attribute is kept, and strings such as `Value` and `IMEtext` are removed), R3j-t(w) (keydown times rounded, w = 10, 100, 1,000 ms) and R4(w). There are no keyup events, so hold times are not used.
- Attackers: A0 and A2. A1, A1', A3 and A4 are not run (they rely on English models or on rebuilding the final draft). A0 for ENJA15 takes, on the log side, the number of letter presses among `Type="IME"` or `Type="insert"` events minus the number of `[Back]` presses (R4: the sum of segment values), and on the translation side the sum of the standard keystroke counts of the readings (as in the segment rule; R4: the sum of floor(value/w) over segments), and chooses the candidate with the minimum absolute difference.
- Exclusion: sessions with a missing log or translation, an empty translation, or a log with neither `Type="IME"` nor letter `Type="insert"` events (not Japanese input). Counts are reported.
- Decoys: translations of the same source text by other translators (N = 10 and N = all). For N = 10, 9 translations are drawn uniformly without replacement from the other translators (seed `enja_decoys`, 20 draws per log); for N = all, all are used. Source texts with fewer than 10 translators have no N = 10 cell (counts reported). Identical translations tie (1/m). Translator identity is not used.
- Resampling: percentile bootstrap with translators as units, 2,000 resamples, 95%. If check 5 finds any translator who translated two or more source texts (crossed), translators are resampled with all their sessions, without stratification (a source text with no log in a resample is left out of that resample's mean, and the number of such resamples is reported). If every translator translated one source text (nested), translators are resampled stratified by source text. ENJA15 is smaller than KLiCKe (the number of translators is counted in check 5), and its intervals are expected to be wide; their widths are reported as they are.
- Quantity answering question 4: accuracy of A2 at full text and N = all, with its differences from 1/N and from A0 (differences and intervals). The decision uses the mean over source texts; values per source text are only described. Accuracy, 1/N and the accuracy of A0 are aggregated in the same way (the mean over logs within each source text, then the mean over source texts), and the differences are taken within each bootstrap resample between values aggregated in the same way. The wording rule of question 4 ("exceeds") is applied to R3j; R3j-t(w) and R4(w) are reported with the same rule. In R0j the committed strings remain in the log and matching is trivial; it is reported as a reference and not used for the decision.
- Check of input-method paths (after acquisition, before the main computation): on logs that include updates of uncommitted strings, cancelled conversions and commits, it is confirmed that no column of R3j (`IMEtext`, `Value` and others) retains a string. If a string remains, the form is revised and the change is recorded as a deviation.

## Handling of logs

- The KLiCKe and ENJA15 logs and texts are public data, but they are not put in the repository (`raw/`, outside version control). Only aggregates are put in the repository. Results per writer and excerpts of texts and logs are not published.
- Logs and texts are not sent to external language models. A4 runs on a local GPU.

## Ethical considerations (material for the paper)

- The researcher is not affiliated with a research institution and has no ethics committee to which the study could be submitted. The paper states that no external committee reviewed the study and why.
- The KLiCKe paper (Tian et al., 2025) mentions neither ethics approval nor consent to public release. On consent it states only that "participants were presented with an informed consent form outlining the study's objectives and procedures" (§2.1). Tian's dissertation (Tian, 2023), which used the same recruitment, mentions neither ethics approval nor the wording of consent. The authors were contacted; the content of their reply will be reported.
- The principles of the Menlo Report (Dittrich & Kenneally, 2012): respect for persons (the purpose the participants agreed to was writing research, and this study evaluates the protection of public logs; it collects no new data, identifies no individual, does not acquire demographics and publishes only aggregates); beneficence (the results inform how releasing parties process logs and contribute to protecting writers, including the participants; the harm is the publication of a procedure that links logs to texts); justice (no new burden is placed on participants, and the benefit reaches every writer whose keystroke logs are released; with free public data and code, anyone can repeat the evaluation); and respect for law and public interest (the data are used under their terms of use, Inputlog, n.d., and their sources are cited).
- The Kaggle data are not linked to KLiCKe.

## Use of AI (material for the paper)

- The design proposals, the text of this registration and the proposals for predictions were written by an AI assistant (Claude, Anthropic), and the researcher chose among them; a decision log records the questions on which the researcher chose an option other than the one recommended. AI reviewers were also used in a pre-registration review; their points were verified against primary sources before the researcher decided whether to adopt them. That review is not evidence for the study.
- Logs and texts are not sent to AI systems ("Handling of logs").

## Open science (material for the paper)

- Published: this registration (OSF), the code for processing, attackers and aggregation, and the aggregated results (a release of the paper repository on Zenodo with a DOI). The Zenodo record and the paper cite the OSF DOI.
- Not published: the data (obtained from each source and not redistributed) and results per writer.
- The scope of publication of the attack code is decided by the researcher at the paper stage. Options: (1) publish everything; (2) publish the code for reading, processing and evaluating KLiCKe and ENJA15, but not code that reads other public logs directly (code that reads the Kaggle data is not written at all); (3) share on request.

## What is not concluded

- No proof of safety and no upper bound on the risk of matching is claimed (the results are limited to the attackers tried here and to the closed world). The strongest attacker is the maximum over the attackers tried, not an attack that combines all length and timing information (only A3 on R3-u combines them). The R7 alignment is not likelihood-based. The timing term of A3 on R3-u uses a one-to-one correspondence from the start and in effect uses only the part before the first replay error (check on synthetic logs). In the R3 family, a drag's duration (and that of a held key, when the next press follows its release) remains as a lower bound of the next press interval. No attacker targets it, but it can enter the interval features of A2-b and the segment durations of A3 on R7. The rule "the next press after Control" of the segment rule and of A1' fails from the second key when several keys are pressed while Control is held (for example Ctrl+Z twice), because the held state cannot be read when the modifier action time is 0.
- No pass or fail is decided.
- No difference by writer attributes is claimed (demographics are not acquired).
- Matching results are not described as identification of writers.
- ENJA15 results are not generalised to Japanese free writing or to Japanese input-method logs in general. Differences from KLiCKe are not attributed to language or input method (prompt, input mode and language differ at once).
- KLiCKe results are not generalised to other task formats (a 30-minute limit, argumentative essays, crowdsourced writers) or to logs that did not pass the selection of the KLiCKe release (such as the removal of logs with much pasting; Tian et al., 2025).
- Matching as an attack is not claimed to be new (González et al., 2021; Qiu et al., 2026; Monaco, 2019; Wright et al., 2008), nor are the processing steps themselves (substitution, permutation, suppression; Vassallo et al., 2017). What may be claimed as new is the evaluation, on public keystroke data whose texts are known, of the processing used in practice and of alternative candidate processing, by an attack that matches logs to texts.

## Deviations

After fixing, any change to a value or procedure written here is recorded in "Deviations" in `notes.md` with its time and reason, and the result with the value before the change is also kept.

## Open items

- Whether PoPETs requires an online presentation or a recorded video (not related to the main computation and not a condition for fixing). Confirmed in the PETS 2027 call for papers (retrieved 2026-10-12): in-person attendance is not required for publication ("in-person attendance is not strictly required for publication in the proceedings"), and there are no submission or publication charges ("does not have article processing charges or article submission charges"). Whether authors who do not attend must submit a recording is not stated; the researcher will ask the program chairs.
- The reply of the KLiCKe authors (inquiry sent on 2026-10-12). The registration is fixed and the data are acquired without waiting for the reply (not a condition for fixing). If there is no reply, one reminder is sent on 2026-10-26. The content of the reply is reported in the ethics section. If the reply raises a concern about this use, the computation is stopped, the acquired data are deleted, and the course of events is reported.
- Whether A4 on 500 writers runs on the local GPU (measured in check 6; if not, only the A4 rows are reduced by the same number per prompt and recorded as a deviation).
- The check on synthetic logs was done on 2026-10-12, and its results and revisions are included (closed).

## References

- Carl, M., Aizawa, A., & Yamada, M. (2016). ENJA15: A free corpus of English–Japanese translation process. Asia-Pacific Forum on Translation and Intercultural Studies (APTIF 2016). https://research.cbs.dk/en/publications/enja15-a-free-corpus-of-english-japanese-translation-process/
- CRITT TPR-DB. (2016–). ENJA15 Translog-II logs [Data set]. SourceForge.
- Dittrich, D., & Kenneally, E. (2012, August). The Menlo Report: Ethical principles guiding information and communication technology research. U.S. Department of Homeland Security, Science and Technology Directorate, Cyber Security Division.
- Edwards, J., Hart, K., & Shrestha, R. (2023). Review of CSEDM data and introduction of two public CS1 keystroke datasets. Journal of Educational Data Mining, 15(1).
- González, N., Calot, E. P., Ierache, J. S., & Hasperué, W. (2021). The reverse problem of keystroke dynamics: Guessing typed text with keystroke timings only. In 2021 International Conference on Electrical, Computer and Energy Technologies (ICECET) (pp. 1–6). https://doi.org/10.1109/ICECET52533.2021.9698782
- Inputlog. (n.d.). Community: Building a library. Retrieved 2026-10-12, from https://www.inputlog.net/community/
- Inubushi, T. (2024, January 21). [1st place solution] Data cleaning + FE + external data + model ensemble. Kaggle. https://www.kaggle.com/competitions/linking-writing-processes-to-writing-quality/writeups/tomoo-inubushi-1st-place-solution-data-cleaning-fe
- Kerckhoffs, A. (1883). La cryptographie militaire. Journal des sciences militaires, 9, 5–38 (January) and 161–191 (February).
- Monaco, J. V. (2019). What are you searching for? A remote keylogging attack on search engine autocomplete. In 28th USENIX Security Symposium.
- Qiu, M., Chuang, L., Kim, D., Qu, H., Chen, T., & Kwong, A. (2026). KeyTAR: Practical keystroke timing attacks and input reconstruction. In 2026 IEEE Symposium on Security and Privacy (SP). https://doi.org/10.1109/SP63933.2026.00106
- The Learning Agency Lab. (2023). Linking writing processes to writing quality [Competition]. Kaggle. https://www.kaggle.com/competitions/linking-writing-processes-to-writing-quality
- Tian, Y. (2023). Argumentation in L1 and L2 adult writers: A process-based perspective using keystroke logging [Doctoral dissertation, Georgia State University]. https://doi.org/10.57709/35889705
- Tian, Y., Crossley, S. A., & Van Waes, L. (2025). The KLiCKe corpus: Keystroke logging in compositions for knowledge evaluation. Journal of Writing Research, 17(1), 23–60. https://doi.org/10.17239/jowr-2025.17.01.02
- Vassallo, G., Van hamme, T., Preuveneers, D., & Joosen, W. (2017). Privacy-preserving behavioral authentication on smartphones. In Proceedings of the 1st International Workshop on Human-centered Sensing, Networking, and Systems (HumanSys '17) (pp. 1–6). ACM. https://doi.org/10.1145/3144730.3144731
- Wagner, I., & Eckhoff, D. (2018). Technical privacy metrics: A systematic survey. ACM Computing Surveys, 51(3), Article 57. https://doi.org/10.1145/3168389
- Wright, C. V., Ballard, L., Coull, S. E., Monrose, F., & Masson, G. M. (2008). Spot me if you can: Uncovering spoken phrases in encrypted VoIP conversations. In 2008 IEEE Symposium on Security and Privacy. https://doi.org/10.1109/SP.2008.21
- Zou, L., & Carl, M. (2026). Using Translog-II for conducting keylogging experiments. Data, 11(7), 176. https://doi.org/10.3390/data11070176
