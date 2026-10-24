# Manuscript outline

This outline fixes the structure of the manuscript and the evidence for each claim. The sections listed here are
written before the results of the main computation are known and contain no result value. The preregistration (the
English version registered on OSF, `preregistration.md` of the study repository) takes precedence over this outline
wherever they differ; the threat model, the attackers and the procedure are taken from it and are not changed.

## Title

Hiding the Text, Keeping the Process: Matching Processed Keystroke Logs to Texts Held by Others

Fixed on 21 October 2026, before the results were seen. It names the aim of the releasing party (hide the text, keep
the process) and the premise of the attack (the texts are held by others), and it states no direction of the results.
The preregistration's title was "How far do processing steps applied to public keystroke logs protect against
matching logs to texts?".

## Venue requirements to be met

Proceedings on Privacy Enhancing Technologies 2027, submission template of 2027: at most 12 pages for the main body;
double-blind review (anonymous option of the class, third-person references to the author's own work, identifying
external material only through an anonymised copy); the first page must state how the work is relevant to real-world
privacy applications; three mandatory sections (ethical considerations, open science, AI use) between the
acknowledgements and the references, outside the page limit, in the order of the template (`\appendix`, the acknowledgements, the three sections, the references, then the
appendix sections, as in
the template's example); appendices are not required reading, so every result needed for a conclusion is in the main
body.

## Structure

| Section | File | Depends on the results | State |
|---|---|---|---|
| 1 Introduction | `sections/introduction.tex` | Contributions paragraph only | Skeleton with draft paragraphs; approach, harms and contributions left as bracketed plans |
| 2 Background and related work | `sections/related.tex` | No | Skeleton with draft paragraphs; the scope of the searches behind "To our knowledge" is given by sources, dates and counts (search terms were not recorded) |
| 3 Threat model | `sections/threat-model.tex` | No | Draft, revised after the first pre-submission review |
| 4 Data and release forms | `sections/data.tex` | Counts after exclusion | Draft; the counts after exclusion are left blank |
| 5 Attackers | `sections/attackers.tex` | No | Draft |
| 6 Evaluation protocol | `sections/protocol.tex` | No | Draft; the list of deviations is updated after the main computation |
| 7 Results, with a short subsection on the Japanese translation logs (question 4) | `sections/results.tex` | Yes | After the main computation |
| 8 Discussion and limitations | `sections/discussion.tex` | Partly | Limitations drafted; the paragraph on agreements drafted from primary sources (DataShop terms, the competition rules, the KLiCKe terms); the take-aways after the results |
| 9 Conclusion | `sections/conclusion.tex` | Yes | After the main computation |
| Ethical considerations | `sections/ethics.tex` | No | Draft |
| Open science | `sections/open-science.tex` | No | Draft |
| AI use | `sections/ai-use.tex` | No | Draft |
| Appendices (after the references): all writers for A0 to A3, forms R5 and R6, the full KeyTAR rows, the exploratory tables | to be added | Yes | After the main computation |

## First page

The first page states the real-world relevance through harm (a) and the release that motivates the study: a public
release hid the texts of essays by masking letters and digits, with the stated goal "to prevent reproduction of the
essay text"; the lengths that remain were used to predict scores; and texts on the same prompts are held by those who
collected and scored them and by public corpora. The question is whether the processing meets its own goal against an
attacker who holds candidate texts, and what it costs research. The evaluation answers it for one log against N
candidates in a closed world; harm (b), linking a log to a named writer, is stated only as a consequence if logs were
released by class or found from a published essay. The first page also says that the auxiliary information is the
text, not a labelled sample of keystrokes. The contributions paragraph is written after the results and does not
claim more than the evaluation of the masking used in one public release and of alternatives against the attackers
tried. Harm (a) is the link between a processed log and its text for a party that holds the text; the stated goal is
the prevention of reproduction, and reading it as keeping the text apart from the process is ours.

## What a releasing party takes away

The results are material for choosing which columns to keep, how coarsely to give times and lengths, and whether to
release full logs or windows, with two axes reported for each form: the accuracy of matching and how far the standard
process measures can still be computed. No rule recommends a form (preregistration, "Summary table and figure"); the
paper does not say that a form "works" or "withstands" matching. The recommendations in the discussion are stated as
"against this attacker, at this N, this form had this multiple of 1/N and kept this much of the process measures".
Agreements not to re-identify, which releasing parties also use, are discussed alongside the processing in Section 8.

## Page budget

Estimated on 21 October 2026, before the results, and revised after the first pre-submission review of the manuscript
(the appendices are not required reading, so nothing that a result in the body needs is moved). The main body runs
from page 1 to page 11 (about 11 pages after the revision). The results (two tables, one figure, the subsection on the
Japanese translation logs, about 2.5 pages), the three paragraphs of the introduction, the take-aways, the conclusion
(about 0.8 page) and the abstract (about 0.25 page) bring it to about 14.5 pages, so about 2.5 pages move to the
appendices after the results, in this order: (1, done on 21 October 2026: Section 8.1 now refers to Section 3.5,
and the absence of a recommendation and the handling of the data are each stated once) merge the overlap of the assumptions (Section 3.5) and the
limitations (Section 8.1), and state once each the absence of a recommendation and the handling of the data; (2) the
checks after acquisition and on synthetic logs (Sections 4.2 and 4.3), keeping in the body the agreement of the segment
rule and a one-sentence summary of each deviation; (3) the details of the registration (seeds and hashes) of Section
6.8, into the open science section, keeping a two-sentence summary in Section 6; (4) the procedures of the exploratory
analyses (Section 6.7), keeping one paragraph that names them; (5) the details of the methods for the Japanese
translation logs (Sections 4.1, 4.3, 5.5 and 6.6), keeping in the body the candidates, the segment rule, the quantity
that answers question 4 and the rule for "exceeds". The details of A3 and of the alignment and the table of process
measures stay in the body, since the main results depend on them. If (1) to (5) do not suffice, the next candidates
are chosen with the results in view.

## Claims and evidence: Section 2 (Background and related work)

| Claim | Evidence | Strength used in the text |
|---|---|---|
| Matching as an attack is not new: timing alone selects the typed text among candidates; lengths select phrases; timing and spaces select search queries; timing reconstructs input | `gonzalez2021reverse`, `wright2008spotme`, `monaco2019searching`, `qiu2026keytar` (preregistration, "What is not concluded") | Stated as prior work; no claim of a stronger attack |
| The processing steps are not new (substitution, permutation, suppression; rounding of latencies) | `vassallo2017privacy` (abstract only; our definitions follow the names), `leinonen2017preventing` | Stated; our forms are our definitions |
| Records are linked through auxiliary information the releasing party did not anticipate | `narayanan2008robust` | Stated |
| Evaluations of anonymisation for behavioural data often assume a weak attacker | `hanisch2021survey` (quotation) | Quoted |
| Earlier work on releasing keystroke data considered labelled keystroke samples and identification, not texts | `leinonen2017preventing`, `edwards2023csedm` | Stated for these works; not "no work considers texts" |
| What is new: the evaluation, on public keystroke data whose texts are known, of the masking used in one public release and of alternatives, by an attack that matches logs to texts | Preregistration, "What is not concluded" (last item); the literature searches before registration found no such evaluation | "To our knowledge", with the sources, dates and counts of the searches in two sentences (the search terms were not recorded and are not reconstructed) |

## Claims and evidence: Section 3 (Threat model)

| Claim | Evidence | Strength used in the text |
|---|---|---|
| A competition released essay logs with letters and digits replaced by `q`, keeping punctuation, times, activity, text change, cursor position and word count | `kaggle2023lwp`, data page (quotation) | Quoted |
| The winning solution rebuilt the text from masked logs and used word and sentence lengths | `inubushi2024first` (quotations) | Quoted; only lengths, not times, are said to be used |
| Two programming keystroke datasets mask identifying text with `@`, one character for one character; the program is not hidden; times are not processed | `edwards2023csedm`, Section 4 ("mask the characters of identifying text with the @ character"; example `@@@n()`); the paper processes characters only | Stated as another masking that keeps lengths, not as an instance of the threat |
| Earlier releases answered the timing risk in terms of labelled keystroke samples | `edwards2023csedm` (two quotations), `leinonen2017preventing` | Quoted; the papers are not said to ignore texts |
| KLiCKe: 4,992 essays, four SAT-based prompts, 30 minutes, MTurk in 2022, released with logs and human scores | `tian2025klicke`, Sections 2.1, 2.3 and 3 | Stated |
| The procedure of the competition data names the same platform, kind of prompts and sequence of tasks as KLiCKe | `kaggle2023lwp`, data collection procedure page | Stated; whether the essays are the same is not examined, for ethical reasons |
| The competition data were drawn from the KLiCKe corpus before it was released | Authors of KLiCKe, personal communication (2026-10-24; date removed in the submitted version) | Reported as told; the authors did not say whether all or some of the essays are in the released corpus; not checked against either release. For a hidden essay that is in the released corpus, the masking no longer keeps its log apart from its text, since the text was released later; the correspondence of records can then be found by comparing the logs, a link across releases outside the attacker of this study |
| Writing tools keep text and process together and offer replays to instructors | `grammarly2026authorship` (support page); `turnitin2026clarity` (product page) | Existence only; no release of such logs is known |
| The competition states the goal "to prevent reproduction of the essay text"; the essays were scored, so their texts exist outside the release | `kaggle2023lwp` (quotation); the competition asks for the score to be predicted (`inubushi2024first`) | Quoted; stated |
| Settings table: holder, direction, when the closed world holds, what is newly learned. The preregistration's holders (teachers, raters or platforms; the essay published with its text; the essay published in a class or online) are kept: raters and the collecting party under "texts on the same prompts", teachers and platforms under "classroom", the published essay as its own row | Reasoning from the settings; the preregistration's "Threat model" (setting, goals, N, closed world) | Stated as the scope of the evaluation and its limits; the evaluation corresponds directly to the first row only |
| A releasing party may release only parts of logs; no such release is known | None; stated as a choice of the releasing party | Stated as a choice, with "we know of no such release" |
| A matched log would also be a labelled sample of the writer's keystrokes | Reasoning from the definitions in `edwards2023csedm` | Conditional ("if ... were matched") |
| The attacker follows the recommendation to know the technique and its parameters | `hanisch2021survey` (recommendation on evaluation) | Stated |
| Japanese translation logs: candidates are translations of the same source text by other translators | Preregistration, "ENJA15" | Stated as how the evaluation builds candidates, not as a setting |
| Attacker knowledge, goals, N, closed world, Wagner and Eckhoff taxonomy, KeyTAR outside the threat model | Preregistration, "Threat model" and "Attackers" | Restated; "links across several publications" is made concrete as "several releases (such as several logs of the same writer)"; "external" is defined as not part of the releasing party; the preregistration lists the goals (a) and (b) without order, and the paper makes (a) the main harm and states (b) as conditional |
| Assumptions and the direction of bias: closed world, training data, known window ends (favour); attackers within the threat model without language models, earlier texts or several releases (limit); uniform decoys (unknown); no abstention and no false-match rate; per-writer distribution only to the 90th percentile | Preregistration, "Threat model", "Candidates", "Reported quantities", "What is not concluded" | Stated as limits |
| The results are a description of the attackers tried, with no proof of safety and no upper bound | Preregistration, "What is not concluded" | Stated |

## Ethical considerations: plan

- No external committee (no affiliation); no reason is given for not seeking a board outside an institution (decided 21 October 2026). Public data and a public model only, aggregates only. In the
  submitted version, check that the wording about affiliation and the dated personal communication do not identify
  the author beyond what the venue requires (to be decided with the handling of double-blind review).
- Consent of the KLiCKe participants in the words of the corpus authors (personal communication); consent of the ENJA15
  participants (quotation from the paper that describes its collection, LREC 2016); licences and the terms of the
  KeyTAR model.
- Stakeholders and what each could lose, with and without misuse of the paper; naming the competition data next to a
  public corpus is weighed as a harm. Reasons from duties (consent scope, no new collection, the competition data not
  used) in a paragraph of their own; consequences under the Menlo principles.
- The competition data are not used, and whether they share essays with KLiCKe is not examined, because doing so would
  test a real release without its participants' agreement to that use. The authors of KLiCKe told us the competition
  data were drawn from KLiCKe; this is reported as a personal communication and not checked. Reporting it is itself a
  disclosure (the records of the two releases can be put in correspondence without the procedures), weighed against
  the reasons to report it; the reason not to match is that the competition data are another party's release with the
  stated goal of preventing reproduction of the texts, not a lack of consent.
- The releasing party of the competition data is informed before submission that this evaluation will be published
  and that its data were not matched (after the results; the date is reported).
- The scope in which the attack code is published (the preregistration's three options), and the reasons.
- The KLiCKe authors receive the paper when it is complete.
- Submitted version: the personal communication is undated and the registration link is withheld (anonymised copy of the study repository instead); both are restored in the camera-ready version.
- Code: published only for the two corpora evaluated; no code reads other released logs.
- The benefit is stated as the measurement on two corpora, not as a means for releasing parties to measure their own
  logs (the code covers the two corpora only).
- The releasing party of the competition data is informed as soon as the results are known, about two weeks before
  submission, with time to respond; the date, the time given and the response are reported.
- Submitted version: "the authors", and "no institutional ethics committee was available to the authors", with the
  no reason for not seeking a board outside an institution; a statement of interests (the recording software, the
  plan to release logs collected with it, no financial interest, no funding; decided 21 October 2026).

## Not claimed in Section 3

- That the competition essays are KLiCKe essays.
- That any party has matched a released log to a text.
- That the writing tools release logs.
- That the closed-world accuracy measures the risk in the classroom or published-essay settings.
- That harm (b) has occurred in any release.
