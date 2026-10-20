# Manuscript outline

This outline fixes the structure of the manuscript and the evidence for each claim. The sections listed here are
written before the results of the main computation are known and contain no result value. The preregistration
(`preregistration.md` of the study repository, registered on OSF) takes precedence over this outline wherever they
differ; the threat model, the attackers and the procedure are taken from it and are not changed.

## Title

How far does the processing of public keystroke logs protect against matching logs to texts?

Working title, close to the title of the preregistration. To be fixed before the results are seen.

## Venue requirements to be met

Proceedings on Privacy Enhancing Technologies 2027, submission template of 2027: at most 12 pages for the main body;
double-blind review (anonymous option of the class, third-person references to the author's own work, identifying
external material only through an anonymised copy); the first page must state how the work is relevant to real-world
privacy applications; three mandatory sections (ethical considerations, open science, AI use) between the
acknowledgements and the references, outside the page limit; appendices are not required reading.

## Structure

| Section | File | Depends on the results | State |
|---|---|---|---|
| 1 Introduction | `sections/introduction.tex` | Contributions paragraph only | Not written |
| 2 Background and related work | `sections/related.tex` | No | Not written |
| 3 Threat model | `sections/threat-model.tex` | No | Draft |
| 4 Data and release forms | `sections/data.tex` | Counts after exclusion | Not written |
| 5 Attackers | `sections/attackers.tex` | No | Not written |
| 6 Evaluation protocol | `sections/protocol.tex` | No | Not written |
| 7 Results | `sections/results.tex` | Yes | After the main computation |
| 8 Discussion and limitations | `sections/discussion.tex` | Partly | Limitations first |
| 9 Conclusion | `sections/conclusion.tex` | Yes | After the main computation |
| Ethical considerations | `sections/ethics.tex` | No | Not written |
| Open science | `sections/open-science.tex` | No | Not written |
| AI use | `sections/ai-use.tex` | No | Not written |

## Claims and evidence: Section 3 (Threat model)

| Claim | Evidence | Strength used in the text |
|---|---|---|
| A competition released essay logs with letters and digits replaced by `q`, keeping punctuation, times, activity, text change, cursor position and word count | `kaggle2023lwp`, data page (quotation) | Quoted |
| Two programming keystroke datasets mask identifying text with `@`, one character for one character | `edwards2023csedm`, Section 4 ("mask the characters of identifying text with the @ character"; example `@@@n()`) | Quoted |
| Times remain in both releases | `kaggle2023lwp` column list; `edwards2023csedm` processes characters only | Stated as "the masking applies to characters" |
| The winning solution rebuilt the text from masked logs and used word and sentence lengths | `inubushi2024first` (quotations) | Quoted |
| The release argument of the programming datasets concerns labelled keystroke samples | `edwards2023csedm`, Section 4 and conclusion (two quotations) | Quoted; the paper is not said to ignore texts |
| KLiCKe: 4,992 essays, four SAT-based prompts, 30 minutes, MTurk in 2022, released with logs and human scores; scored by trained raters on a six-point holistic scale | `tian2025klicke`, Sections 2.1, 2.3 and 3 | Stated |
| The procedure of the competition data names the same platform, kind of prompts and sequence of tasks as KLiCKe | `kaggle2023lwp`, data collection procedure page | Stated; whether the essays are the same is not examined (preregistration, Data) |
| Writing tools keep text and process together and show replays to instructors | `grammarly2026authorship` (support page, quotations); `turnitin2026clarity` (product page, quotations) | Existence only; the product page is promotional and does not state what instructors see |
| Attacker knowledge, goals, N, closed world, Wagner and Eckhoff taxonomy, KeyTAR outside the threat model | Preregistration, "Threat model" and "Attackers" | Restated without change |

## Not claimed in Section 3

- That the competition essays are KLiCKe essays.
- That any party has matched a released log to a text.
- That the writing tools release logs.
