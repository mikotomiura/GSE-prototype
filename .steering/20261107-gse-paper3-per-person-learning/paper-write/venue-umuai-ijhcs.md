# UMUAI / IJHCS venue fit: primary sources (retrieved 2026-11-07)
Method key: Chrome = get_page_text / innerText in Chrome (curl was blocked by Springer "Client Challenge" and ScienceDirect 403). OpenAlex = API. Nothing here is from WebFetch or third-party summaries.

## 1. UMUAI (Springer, journal 11257)
Sources (Chrome): https://link.springer.com/journal/11257/aims-and-scope ; /submission-guidelines ; /how-to-publish-with-us

### Aims and scope (verbatim)
"User Modeling and User-Adapted Interaction provides an interdisciplinary forum for the dissemination of novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation."
List includes: "acquisition and formal representation of user models, including modeling of affect, personality, knowledge, expertise, interests, preferences, attitudes, goals, plans, culture, relationships and mental models"; "methods for the design and evaluation of user models and adaptive systems"; "responsible adaptation: fairness, accountability, explainability, transparency and control"; "privacy, accountability, and security of information for personalization"; "adaptive user interfaces and agents"; "personalization in areas such as affective computing, ubiquitous and mobile computing ... behaviour change interventions ... workplace".
"The journal mainly publishes empirical research papers. Theoretical proposals should normally be appropriately substantiated, e.g., by empirical results, by an analytical discussion of the results of a computer implementation, or in very rare cases by a formal analysis."
"The central audience of the journal are researchers, students and industrial practitioners from the following areas: Adaptive Systems, Human-Computer Interaction, Artificial Intelligence, the Instructional Sciences, Information Systems, Linguistics, and the Information Sciences."

### Article types and length limits
NOT FOUND on the submission-guidelines page: it names no article types, no body word/page limit, no figure/table cap. Only limit: "Please provide an abstract of 150 to 250 words" and "4 to 6 keywords". (Recent papers are all labelled OriginalPaper in the journal listing.) Whether a length limit exists elsewhere (submission system, editor page): unchecked.

### Required sections/statements (verbatim)
- "The following statements should be included under the heading "Statements and Declarations" ... submissions that do not include relevant declarations will be returned as incomplete." Competing Interests required.
- "Author Contribution information and Competing Interest information must be provided at submission via the submission interface."
- Summary of requirements: "placed in a 'Declarations' section before the reference list under a heading of 'Funding' and/or 'Competing interests'. Other declarations include Ethics approval, Consent, Data, Material and/or Code availability and Authors' contribution statements."
- "All original research must include a data availability statement."
- LLM use: "Use of an LLM should be properly documented in the Methods section".
- Decimal headings, at most three levels. Author-year citation. Footnotes not endnotes.

### Supplementary (verbatim)
"Springer accepts electronic multimedia files ... and other supplementary files to be published online along with an article". "Refer to the supplementary files as 'Online Resource'". "Supplementary Information (SI) will be published as received from the author without any conversion, editing, or reformatting." Text: PDF; spreadsheets .csv/.xlsx; .zip allowed. "We encourage research data to be archived in data repositories wherever possible."
Not stated: whether reviewers read SI, whether SI counts toward length. -> UNCHECKED.

### Publishing model / cost (verbatim)
"User Modeling and User-Adapted Interaction is a hybrid journal." Options: "Subscription publishing model - published articles are made available to institutions and individuals who subscribe ... or who pay to read specific articles." and "Authors can also choose to publish under the subscription publishing model (no APC charges apply); both options will be offered after the paper has been accepted."
APC: "£2490.00 GBP / $3390.00 USD / €2790.00 EUR" (OpenAlex shows apc_usd 3290, stale). Subscription route "isn't suitable if your funders require immediate access (for example NIH or Plan S)". Colour online free; "For color in the print version, authors will be expected to make a contribution".
=> ZERO-COST PATH: YES (subscription route, no APC, no page charges stated; chosen after acceptance).
Preprint policy: not on these pages. UNCHECKED (Springer Nature general policy permits preprints, but not verified here).

### Format / review
"Manuscripts should be submitted in LaTeX. We recommend using Springer Nature's LaTeX template. The submission should include the original source ... and a PDF ... Word files are also accepted." Review: "single-blind" -> no anonymisation needed; "usually reviewed by two referees".

### Recent papers (OpenAlex source S160628929, is_oa; body words = sum of Intro..Conclusion sections counted from the article HTML in Chrome, approximate, excludes refs/notes)
| Paper | Year | Body words (approx) | Sections | Methods vs supplement | Contribution |
|---|---|---|---|---|---|
| Exploring raw data transformations on inertial sensor data to model user expertise... 10.1007/s11257-024-09393-2 | 2024 | ~13,300 (Intro 836 / Background 1908 / Methods 6248 / Results+Disc 3881 / Concl 425) | 1 Intro 2 Background 3 Materials and methods 4 Results and discussions 5 Conclusions | Methods fully in body; no Online Resource/Supplementary mentioned | new method comparison (sensor transforms for user models) |
| Toward personalized driving assistance: individual differences in effect of driving support... 10.1007/s11257-026-09448-6 | 2026 | ~9,800 (Intro 786 / Related 1560 / Method 2307 / Analysis 2904 / Interaction 1511 / Discussion 585 / Concl 167) | Intro, Related works, Materials and method, 2 analysis sections, General discussion, Conclusion, Data Availability | all in body, no SI mentioned | empirical measurement of individual differences (moderation by driver traits) |
| Exploring the impact of explainable AI and cognitive capabilities on users' decisions 10.1007/s11257-025-09438-0 | 2025 | ~12,900 (Intro 1518 / Related 2434 / Hypotheses+task 2292 / Study design 2008 / Results 2368 / Discussion 2043 / Concl 258) | Intro, Related work, Hypotheses and task design, Study design, Results, Discussion, Conclusion, Data availability | all in body, no SI mentioned | empirical user study (hypothesis-driven) |
Others seen in list but not opened: 09396-z (rule-based learning recommender), 09414-0 (AdaptUI framework), 09395-0 (federated next-app prediction, arXiv copy exists), 09427-3 (recommender comparison). Not opened: "reproduction/refutation" type papers - none identified.
Observation: all three have no SI; body 10-13k words in Springer HTML; Data availability statement short.

## 2. IJHCS (Elsevier, ISSN 1071-5819)
Sources (Chrome): https://www.sciencedirect.com/journal/international-journal-of-human-computer-studies/publish/guide-for-authors ; .../publish/open-access-options

### Aims and scope (verbatim)
"The International Journal of Human-Computer Studies publishes research on the design and use of interactive computer technology." Areas include "Adaptive user interfaces", "Affective computing", "Computational interaction", "Empirical studies of user behaviour", "HCI evaluation methodologies", "Human-AI interaction", "Intelligent tutoring systems", "User experience and usability", "Wearable computers".
"The journal focuses on concrete research contributions, which are relevant to the theory and practice of innovative interactive systems. Articles are in general expected to focus on concrete solutions for concrete user audiences."
Not normally considered: "Magazine-style contributions or essays which analyse an issue but do not comprise significant and robust design and evaluation elements." "Standard evaluations of off-the-shelf commercial products." "Survey-based studies, e.g., those which use questionnaires to identify relations between factors affecting technology adoption or surveys profiling different user groups." "Studies that describe military applications." Reviews only by prior contact with Editors-in-Chief.
Prior publication: "IJHCS does not consider submissions that are extensions, rewrites, or re-analyses of previously published refereed conference papers" (CHI, CSCW, ACM DL, IEEE Xplore, LNCS treated as archival). Preprints do not count: "Sharing preprints, such as on a preprint server, will not count as prior publication."
Note for fit: "Personalization" / user modelling is not named as a scope item except "Adaptive user interfaces". Emphasis is on design + evaluation with users; pure ML-evaluation may be a weaker fit (my reading, not a quote).

### Article types and length limits
No type list with limits on the guide. Only: abstract "does not exceed 250 words"; "1 to 7 keywords"; "3 to 5 bullet points, each a maximum of 85 characters" Highlights (required); graphical abstract optional; author Vitae "maximum 100 words" each. No body word/page limit and no figure/table cap found. "Use tables sparingly".

### Required sections/statements (verbatim)
- Highlights at submission (separate file named with "highlights").
- Declaration of competing interests (declarations tool, Word file uploaded). Funding sources statement ("This research did not receive any specific grant ..." if none).
- CRediT author statement ("Corresponding authors are required to acknowledge co-author contributions using CRediT").
- Generative-AI declaration section before references if AI used.
- Research data: "Option C ... Deposit your research data in a relevant data repository. Cite and link to this dataset in your article. If this is not possible, make a statement explaining why research data cannot be shared."
- Numbered sections (1, 1.1...). Acknowledgements directly before references.

### Supplementary (verbatim)
"We encourage the use of supplementary materials such as applications, images, and sound clips". "Cite all supplementary files in the manuscript text." "Submit all supplementary material at the same time as your manuscript." "all supplementary material provided will appear online exactly as received." Not stated: whether reviewers read it or whether it counts toward length -> UNCHECKED. Recent papers use "Appendix" inside the article.

### Publishing model / cost (verbatim)
Two choices: "Open access ... An open access publication fee is payable by authors, or their institution or funder." and "Subscription ... No open access publication fee." "Your publication choice will have no effect on the peer review process or acceptance of your submission." APC: "All articles USD 3000" (excl. taxes; personalised price shown at submission).
Self-archiving: "This journal has an embargo period of 24 months for self-archiving" for accepted manuscript under subscription. Preprints OK anytime (above); free SSRN posting offered at submission.
=> ZERO-COST PATH: YES (subscription, no fee). No page charges stated. Subscription + preprint on arXiv/SSRN allowed.

### Format / review
"We encourage you use our LaTeX template" (Elsevier LaTeX template; link on the guide). Word single-column also fine; "A PDF is not an acceptable source file." Review: "single anonymized review process" -> no author anonymisation needed (the guide says editors first screen, then "a minimum of two reviewers").

### Recent papers (OpenAlex source S4210190811, is_oa; counts from the ScienceDirect HTML in Chrome; section totals include the heading's whole element, so approximate)
| Paper | Year | Body words (approx) | Sections | Methods vs appendix | Contribution |
|---|---|---|---|---|---|
| Physiological and behavioral modeling of stress and cognitive load in web-based question answering 10.1016/j.ijhcs.2026.103952 | 2026 | ~12,200 (Intro 1440 / Background 1844 / User study 2443 / Data analysis 1836 / Results 1760 / Discussion 2461 / Concl 338) | 1 Intro 2 Background and related work 3 User study 4 Data analysis 5 Results 6 Discussion 7 Conclusion 8 Open science & transparency, CRediT, competing interest, Appendix A-D, Data availability | full methods in body; appendices A-D hold descriptive stats, plots, a sensitivity analysis (neutral-response exclusion), a rest-adjusted model (~700 words total) | new measurement/modelling from behavioural + physiological signals |
| Designing personalized mental health interventions for anxiety: CBT therapists' perspective 10.1016/j.ijhcs.2024.103319 | 2024 | ~11,400 (Intro 1078 / Background 1033 / Method 1361 / Interviews 3157 / Ideation 2493 / Discussion 1831 / Limits 309 / Concl 142) | qualitative: Intro, Background, Method, 2 Results, Discussion, Future work and limitations, Conclusions, "Appendix. Supplementary materials" (25 words, link only) | supplementary only as a data link | design/qualitative empirical study |
Not opened (other candidates): 103907 (XR agents, 2026), 103690 (personas and LLMs, 2025), 103648 (mental models, code completion, 2025), 103314 (user types, 2024), 103797, 103942. Only 2 IJHCS papers were read in the time; not 3-5.
Observation: IJHCS papers are long (11-12k words) with an explicit "Open science & transparency" section in the 2026 paper; there are many user-study papers, few offline-ML-evaluation papers among those seen.

## Gaps (not done)
- Springer submission guide has no length/article-type info: check the submission system or the editors' page. Springer preprint policy page not fetched. Whether Springer SI is read by reviewers: not stated.
- Elsevier LaTeX template page and 'Elsevier preprint/sharing policy' beyond the guide: not fetched.
- Only 3 UMUAI and 2 IJHCS papers read; none was a reproduction/refutation/resource paper, so those contribution types are not evidenced for either journal.
- Word counts are from rendered HTML (approximate).
