# Manuscript outline

This outline fixes the structure of the manuscript and the evidence for each claim. The sections listed here are
written before the results of the main computation are known and contain no result value. The preregistration (the
English version registered on OSF, `preregistration.md` of the study repository) takes precedence over this outline
wherever they differ; the threat model, the attackers and the procedure are taken from it and are not changed.

## Title

How far does the processing of public keystroke logs protect against matching logs to texts?

Working title, close to the title of the preregistration. To be fixed before the results are seen.

## Venue requirements to be met

Proceedings on Privacy Enhancing Technologies 2027, submission template of 2027: at most 12 pages for the main body;
double-blind review (anonymous option of the class, third-person references to the author's own work, identifying
external material only through an anonymised copy); the first page must state how the work is relevant to real-world
privacy applications; three mandatory sections (ethical considerations, open science, AI use) between the
acknowledgements and the references, outside the page limit, in the order of the template (after `\appendix`, as in
the template's example); appendices are not required reading, so every result needed for a conclusion is in the main
body.

## Structure

| Section | File | Depends on the results | State |
|---|---|---|---|
| 1 Introduction | `sections/introduction.tex` | Contributions paragraph only | Not written |
| 2 Background and related work | `sections/related.tex` | No | Not written |
| 3 Threat model | `sections/threat-model.tex` | No | Draft, revised after the first pre-submission review |
| 4 Data and release forms | `sections/data.tex` | Counts after exclusion | Not written |
| 5 Attackers | `sections/attackers.tex` | No | Not written |
| 6 Evaluation protocol | `sections/protocol.tex` | No | Not written |
| 7 Results, with a short subsection on the Japanese translation logs (question 4) | `sections/results.tex` | Yes | After the main computation |
| 8 Discussion and limitations | `sections/discussion.tex` | Partly | Limitations first |
| 9 Conclusion | `sections/conclusion.tex` | Yes | After the main computation |
| Ethical considerations | `sections/ethics.tex` | No | Draft |
| Open science | `sections/open-science.tex` | No | Not written |
| AI use | `sections/ai-use.tex` | No | Draft |
| Appendices (after the references): all writers for A0 to A3, forms R5 and R6, the full KeyTAR rows | to be added | Yes | After the main computation |

## First page

The first page states the real-world relevance through harm (b) and the release that motivates the study: a public
release hid essay texts by masking letters and digits, the lengths that remain were used to predict scores, and the
texts of such essays are held by public corpora, teachers and writers. Under such a threat a releasing party needs to
know which processing withstands matching. Evidence: as in Section 3. The contributions paragraph is written after the
results and does not claim more than the evaluation of processing used in practice and of alternatives against the
attackers tried.

## What a releasing party takes away

The results are material for choosing which columns to keep, how coarsely to give times and lengths, and whether to
release full logs or windows. No rule recommends a form (preregistration, "Summary table and figure"). The
recommendations in the discussion are stated as "against this attacker, at this N, this form had this multiple of 1/N
and kept this much of the process measures".

## Claims and evidence: Section 2 (Background and related work)

| Claim | Evidence | Strength used in the text |
|---|---|---|
| Matching as an attack is not new: timing alone selects the typed text among candidates; lengths select phrases; timing and spaces select search queries; timing reconstructs input | `gonzalez2021reverse`, `wright2008spotme`, `monaco2019searching`, `qiu2026keytar` (preregistration, "What is not concluded") | Stated as prior work; no claim of a stronger attack |
| The processing steps are not new (substitution, permutation, suppression; rounding of latencies) | `vassallo2017privacy` (abstract only; our definitions follow the names), `leinonen2017preventing` | Stated; our forms are our definitions |
| Records are linked through auxiliary information the releasing party did not anticipate | `narayanan2008robust` | Stated |
| Evaluations of anonymisation for behavioural data often assume a weak attacker | `hanisch2021survey` (quotation) | Quoted |
| Earlier work on releasing keystroke data considered labelled keystroke samples and identification, not texts | `leinonen2017preventing`, `edwards2023csedm` | Stated for these works; not "no work considers texts" |
| What is new: the evaluation, on public keystroke data whose texts are known, of the processing used in practice and of alternatives, by an attack that matches logs to texts | Preregistration, "What is not concluded" (last item); the literature searches before registration found no such evaluation | "To our knowledge" |

## Claims and evidence: Section 3 (Threat model)

| Claim | Evidence | Strength used in the text |
|---|---|---|
| A competition released essay logs with letters and digits replaced by `q`, keeping punctuation, times, activity, text change, cursor position and word count | `kaggle2023lwp`, data page (quotation) | Quoted |
| The winning solution rebuilt the text from masked logs and used word and sentence lengths | `inubushi2024first` (quotations) | Quoted; only lengths, not times, are said to be used |
| Two programming keystroke datasets mask identifying text with `@`, one character for one character; the program is not hidden; times are not processed | `edwards2023csedm`, Section 4 ("mask the characters of identifying text with the @ character"; example `@@@n()`); the paper processes characters only | Stated as another masking that keeps lengths, not as an instance of the threat |
| Earlier releases answered the timing risk in terms of labelled keystroke samples | `edwards2023csedm` (two quotations), `leinonen2017preventing` | Quoted; the papers are not said to ignore texts |
| KLiCKe: 4,992 essays, four SAT-based prompts, 30 minutes, MTurk in 2022, released with logs and human scores | `tian2025klicke`, Sections 2.1, 2.3 and 3 | Stated |
| The procedure of the competition data names the same platform, kind of prompts and sequence of tasks as KLiCKe | `kaggle2023lwp`, data collection procedure page | Stated; whether the essays are the same is not examined, for ethical reasons |
| Writing tools keep text and process together and offer replays to instructors | `grammarly2026authorship` (support page); `turnitin2026clarity` (product page) | Existence only; no release of such logs is known |
| Settings table: holder, direction, when the closed world holds, what is newly learned | Reasoning from the settings; the preregistration's "Threat model" (setting, goals, N, closed world) | Stated as the scope of the evaluation and its limits |
| Attacker knowledge, goals, N, closed world, Wagner and Eckhoff taxonomy, KeyTAR outside the threat model | Preregistration, "Threat model" and "Attackers" | Restated; "links across several publications" is made concrete as "several releases (such as several logs of the same writer)", and "external" is defined as outside the releasing party |
| The results are a description of the attackers tried, with no proof of safety and no upper bound | Preregistration, "What is not concluded" | Stated |

## Ethical considerations: plan

- No external committee; reasons (no affiliation). Public data only, aggregates only.
- Consent of the KLiCKe participants in the words of the corpus authors (personal communication); consent of the ENJA15
  participants (quotation from the corpus paper); licences.
- Stakeholders and what each could lose or gain: the writers of KLiCKe and ENJA15, the writers of the competition
  data, the releasing parties, readers who could reuse the procedures. Harms and benefits under the Menlo principles,
  and the duty-based reasons (consent scope, no new collection) alongside the consequences.
- The competition data are not used, and whether they share essays with KLiCKe is not examined, because doing so would
  test a real release without its participants' consent to that use.
- The releasing party of the competition data is informed before submission that this evaluation will be published
  and that its data were not matched (to be done after the results; the date is reported).
- The KLiCKe authors receive the paper when it is complete.

## Not claimed in Section 3

- That the competition essays are KLiCKe essays.
- That any party has matched a released log to a text.
- That the writing tools release logs.
- That the closed-world accuracy measures the risk in the classroom or published-essay settings.
