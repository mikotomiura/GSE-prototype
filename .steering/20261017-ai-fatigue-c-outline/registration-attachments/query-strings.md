# Query strings of the source database's searches, and of this review's coverage search

Attachment to the registration (GSRR-25). All times are Japan Standard Time (UTC+9). Search IDs S-xx are the labels the source database uses for its survey rounds. "Hit count" is the total the interface reported. Query strings are copied verbatim; Japanese terms are kept as written, with an English gloss.

## How to read this inventory

- The source database consists of (a) a 34-record exploratory base bibliography (searches in section 1) and (b) a set of "additional candidates" that were added to the base during 2026-09-28 to 2026-09-30 (sections 2 to 12; 225 candidates by the end of 2026-09-30, reduced to 220 after merging duplicate versions and same-report records). Together the base and the first 225 candidates are the 259 records of the pre-registration stage.
- Searches were run through public APIs or web interfaces. No paid database was used. No contact address was sent to any API.
- Records found by a search were never added to the candidate list by the search alone. The general route was: (1) a machine step (regular-expression screen on title and abstract, as stated per section); (2) reading of title and abstract by an AI assistant, who tabulated the records in a survey fact file; (3) the researcher's scope decisions (see "Scope decisions" below) and, on 2026-09-30, the researcher's decision that every primary study that a paper describes as AI-related is added regardless of the AI assistant's own eligibility view. After that decision, only non-primary items (reviews, theory papers, datasets) and systems the paper does not describe as AI or machine learning were left out.
- Scope decisions (2026-09-30, researcher): (a) studies that manipulate or compare AI introduction or use and measure users' fatigue, exhaustion or burnout are in scope whatever the design and direction of results; (b) studies of monitoring automation are in scope only if the paper describes the system as AI or machine learning; (c) candidates found by the surveys are judged on a separate sheet, without changing the base records.
- Language, date and document-type filters: none were applied at query time in any search below unless stated. For S-13, S-14 and S-15, records with a publication year later than 2026 were dropped after retrieval (0 records were affected).

## Candidate counts by origin (pre-registration stage, 259 records)

Counts are those recorded when the 259 records were cross-checked against the search-development queries. Base bibliography 34; S-04 workload/time-only comparative studies 47; S-04 other 39; S-12 25; S-05 9; S-02 13; S-14 46; S-13 20; S-08 and S-15 together 26.

## Order of sections

1. Base bibliography: 53 web queries (2026-09-18)
2. Search-gap check (2026-09-28)
3. Search sizing for the planned surveys (2026-09-29, before the surveys; counts only)
4. S-12 Japanese-language and Japan-related literature (2026-09-29 21:12 to 21:21)
5. S-02 retrieval of 11 pre-identified records (2026-09-29 21:38; not a search)
6. S-08 AI-fatigue scales (2026-09-29 21:46)
7. S-04 fatigue and burnout among AI users, comparative studies (2026-09-29 21:58)
8. S-05 fatigue while monitoring automation (2026-09-29 22:08)
9. S-15 overreliance on AI and fatigue (2026-09-30 03:59)
10. S-14 AI stressors and burnout (2026-09-30 04:01, supplementary 04:02)
11. S-13 organisation-level AI fatigue (2026-09-30 04:03)
12. Surveys that added no candidates (S-09, S-11) and the search-development trial
13. Non-search additions and other routes into the candidate list
14. Review-aimed search (2026-10-02 02:50 to 03:53), which produced the 43 review-search records
15. One record added by hand
16. Coverage search of this review (run once before registration; not a search of the source database)

---

## 1. Base bibliography: 53 logged web queries

- **Purpose:** discover and verify the records of the 34-record exploratory base bibliography (known core papers, scales, existing reviews, bibliographic checks).
- **Date and time:** 2026-09-18 for all 53 queries. Time of day: not recorded.
- **Source/interface:** public web search ("web search of public scholarly information"); the search engine is not named in the log. Where a query ends in "[domains: ...]" the log records a domain restriction.
- **Filters:** none recorded other than the domain restrictions shown.
- **Hit counts:** not recorded (the log says total hits were not obtained and must not be used as PRISMA counts).
- **How records entered:** records were found and checked by the researcher and an AI assistant on the public web and entered the base bibliography directly; the screening column of the base bibliography is "unscreened" for all 34 records. These queries produced the base bibliography, not the later additional candidates.
- **Note:** these were general web queries, not database-specific search strings; the 53 queries are preserved in the base bibliography's search-log sheet and reproduced here. Hit counts were not kept.

| ID | Query string (verbatim) | Purpose (English gloss) |
|---|---|---|
| Q001 | "AI fatigue" "Lau" "101186" | verify the original paper of a dedicated scale |
| Q002 | "Fatigued by uncertainties" | known core paper |
| Q003 | "AI Fatigue and Mental Health Implications" | existing review check |
| Q004 | "AI fatigue" scale review human AI interaction | search for core studies and scales |
| Q005 | "AI fatigue" "Too Much" | search for conceptual reviews |
| Q006 | "AI fatigue" "scale" -site:researchgate.net -site:substack.com -site:linkedin.com | further scale search |
| Q007 | "generative AI" "fatigue" "uncertainty" | uncertainty and fatigue |
| Q008 | "AI-induced fatigue" study | direct studies of AI-induced fatigue |
| Q009 | "Too Much, Too Fast" "fatigue" | bibliographic check of a known review |
| Q010 | "AI-induced fatigue among students in higher education" | student fatigue profile |
| Q011 | "Understanding AI Fatigue" "Parreño" | search for a qualitative student study |
| Q012 | "Balancing Cognitive Load, Fatigue, and Human Resilience" | researchers' cognitive load and fatigue |
| Q013 | "AI fatigue" "Parreño" 1000 | search for a qualitative student study |
| Q014 | "Trust erodes, fatigue builds" | prompt revision and fatigue |
| Q015 | "cognitive fatigue" "Zhao" "2026" AI | risk perception and fatigue |
| Q016 | "Learners’ AI dependence and critical thinking" | AI dependence and cognitive fatigue |
| Q017 | "10.3389/fpsyg.2026.1921504" | check of a cognitive-load review |
| Q018 | "The Cognitive Cost of AI" "Decision Fatigue" | check of a decision-fatigue study |
| Q019 | "Fatigued by uncertainties" "832" | sample-size check |
| Q020 | "Trust erodes, fatigue builds" "1045" | sample-size check |
| Q021 | "Too Much, Too Fast" "Ragolane" [domains: ijahss.com, ijahss.net, ijahss.org] | publisher check of an existing review |
| Q022 | "The Cognitive Cost of AI" [domains: pubmed.ncbi.nlm.nih.gov, pmc.ncbi.nlm.nih.gov] | check of the primary bibliographic record |
| Q023 | "generative AI" "technostress" "burnout" study | search for adjacent studies |
| Q024 | "Insights from the Job Demands–Resources Model" | two-sided associations at work |
| Q025 | "From Technostressors to AI-Stressors" | existing review on AI stressors |
| Q026 | "AI fatigue" scale Japanese 日本語 | search for a Japanese scale (log: insufficient to establish absence) |
| Q027 | "Mitigating Learning Burnout Caused by Generative Artificial Intelligence Misuse" | learning-burnout study |
| Q028 | "The Impact of Generative AI on Critical Thinking" Lee | verification burden and cognitive effort |
| Q029 | "To Trust or to Think" | cognitive cost of oversight and overreliance prevention |
| Q030 | "AI" "cognitive load" "randomized" ChatGPT | search for intervention studies with neutral or reduced results |
| Q031 | "The Impact of Generative AI on Critical Thinking" "3706598" | bibliographic check |
| Q032 | "Mitigating Learning Burnout" "Dong" | check of author and study information |
| Q033 | "Zoom Exhaustion" "100119" | original paper of a digital-fatigue scale |
| Q034 | "Updated methodological guidance for the conduct of scoping reviews" | review methodology |
| Q035 | "3713778" "Lee" | DOI check of a conference paper |
| Q036 | "AI anxiety scale" "Wang" "2019" | original paper of an AI-anxiety scale |
| Q037 | "Psychometric qualities" "Fatigue Assessment Scale" | original paper of a general fatigue scale |
| Q038 | "Development of an instrument for measuring different types of cognitive load" | original paper of a cognitive-load instrument |
| Q039 | "The Impact of Generative AI on Critical Thinking" "319" "Lee" [domains: microsoft.com, arxiv.org, dl.acm.org] | sample size and author-version check |
| Q040 | "Mitigating Learning Burnout" "51" "2025" [domains: mdpi.com] | publisher bibliographic check |
| Q041 | "Artificial intelligence anxiety" "619" "Wang" [domains: tandfonline.com] | volume, year and author check |
| Q042 | "PRISMA Extension for Scoping Reviews" [domains: pubmed.ncbi.nlm.nih.gov] | bibliographic check |
| Q043 | "Psychometric qualities of a brief self-rated fatigue measure" [domains: pubmed.ncbi.nlm.nih.gov] | bibliographic check |
| Q044 | "Zoom Exhaustion & Fatigue Scale" "Fauville" [domains: par.nsf.gov, stanford.edu] | check of the authors' open version |
| Q045 | "Reliability and Validity of the Japanese Version" "Fatigue" "Tokumasu" | search for Japanese versions of a general fatigue scale (not registered) |
| Q046 | "10.11124/JBIES-20-00167" "Peters" | author and volume check |
| Q047 | "Zoom Exhaustion Fatigue Scale" Fauville Luo Queiroz Bailenson Hancock | author and abstract check |
| Q048 | "Tokumasu" "Fatigue Assessment" | search for Japanese versions of a general fatigue scale (not registered) |
| Q049 | Reliability Validity Japanese Fatigue Assessment Scale Tokumasu DOI 2025 | as Q048 |
| Q050 | Fauville Zoom Exhaustion Fatigue Scale 2021 15 124 395 | scale and sample check |
| Q051 | Development validation artificial intelligence anxiety scale Yu Yin Wang Yi Shun 2019 2022 | distinguish online year from volume year |
| Q052 | Mitigating Learning Burnout Dong Wang Han 2025 Informatics 51 | author check |
| Q053 | "Tokumasu" "Matsuki" "Fatigue" | search for Japanese versions of a general fatigue scale (not registered) |

---

## 2. Search-gap check of the base bibliography

- **Purpose:** find records the base bibliography might have missed, using reproducible API queries.
- **Date and time:** 2026-09-28. Time of day: not recorded (the result file carries only the date).
- **Source/interface:** OpenAlex works search (`search=` parameter, free-text; up to 50 results viewed per query) and Crossref works search (`query.bibliographic=`, up to 50 rows per query), both via public APIs. Europe PMC was planned but not run (the log says: not run for time reasons).
- **Filters:** online publication on or before 2026-09-28; English (Japanese-language records to be logged separately if found). Quotation marks are the engine's phrase marks; the log notes that neither engine guarantees exact-phrase matching.
- **Queries (verbatim), with reported hit counts (OpenAlex / Crossref):**
  1. "AI fatigue" (158 / 752,472)
  2. "AI-induced fatigue" (4 / 2,385,273)
  3. "generative AI" fatigue (31,618 / 815,534)
  4. ChatGPT fatigue (19,900 / 248,107)
  5. chatbot fatigue users (9,686 / 347,615)
  6. "AI exhaustion" OR "AI burnout" (249 / 595,527)
  7. "decision fatigue" artificial intelligence (1,362 / 2,420,206)
  8. "cognitive fatigue" "generative AI" (1,049 / 1,416,271)
  9. "prompt fatigue" OR "prompting fatigue" (139 / 247,747)
  10. "AI technostress" fatigue (21 / 754,090)
  11. "AI fatigue scale" OR "AI fatigue" scale (23,624,334 / 1,513,925)
- **Deviation / caveat recorded by the sources:** the Crossref counts are relevance-ranked matches against all of Crossref and do not measure relevant literature; query 11's OpenAlex count is an artefact of an unquoted word. Only the top 50 records per query and source were compared.
- **Selection:** 933 records were viewed. A machine screen (title or abstract containing a fatigue-family term and an AI-use term, with exclusion signals for driver or EEG fatigue detection, materials fatigue, and AI as a fatigue-detection tool) left 141 new unique records; these were prejudged by an AI assistant on title and machine-extracted keywords only (abstracts not read) and proposed, not added, to the base bibliography.
- **How records went into the candidate list:** only a subset was carried forward. Eight starred records (one starred row being a second version of a systematic-review preprint) were picked for abstract retrieval and, together with records traced from the reference list of an existing review in the base bibliography, form the 11 records of S-02 (section 5). The remaining records of the 141 were not added to the candidate list at this stage. How the three or four reference-list records were selected is not recorded beyond "citation tracing of the reference list of one base-bibliography review".
- **Cross-match:** two dataset records from another review by the same research team (found by that team's own 2026-09-19 review, not by this database's searches) were compared with the candidate list (S-02 section 5, below); they were not added.

---

## 3. Search sizing for the planned surveys (counts only)

- **Purpose:** estimate how large each planned survey would be and confirm that seed papers exist; not a full search.
- **Date and time:** 2026-09-29, before the survey rounds. Time of day: not recorded (the work was recorded at 12:14 that day).
- **Source/interface:** OpenAlex free-text search, Europe PMC (`TITLE_ABS`), Semantic Scholar bulk search, J-STAGE and CiNii Research (public APIs); Crossref and DataCite for seed-paper existence checks.
- **Deviation recorded:** OpenAlex's anonymous search returned HTTP 429 after 7 of 26 first-round queries and was not usable afterwards; counts judged meaningless were marked "not a guide".
- **Queries (verbatim) and counts:**
  - OpenAlex: "AI fatigue" 158; "AI fatigue scale" 6; "content moderators" burnout 177; "prompt fatigue" 139 (not a guide); "AI hype" fatigue 124 (not a guide); citations of one scale paper: 2
  - Europe PMC: TITLE_ABS:("ambient AI" OR "AI scribe" OR "ambient scribe" OR "ambient listening" OR "ambient artificial intelligence") AND TITLE_ABS:(burnout OR fatigue OR "cognitive load" OR exhaustion) — 89
  - Europe PMC: TITLE_ABS:("large language model" OR "generative AI" OR "AI-generated" OR "artificial intelligence") AND TITLE_ABS:("draft replies" OR "draft responses" OR "in-basket" OR inbox) AND TITLE_ABS:(burnout OR fatigue OR "cognitive burden" OR "task load") — 18
  - Europe PMC: TITLE_ABS:"passive fatigue" — 26; TITLE_ABS:("automation complacency" OR "automation-induced complacency") — 25; TITLE_ABS:"alert fatigue" — 537; TITLE_ABS:"alert fatigue" AND TITLE_ABS:("artificial intelligence" OR "machine learning") — 80
  - Europe PMC: TITLE_ABS:("generative AI" OR ChatGPT OR "large language model") AND TITLE_ABS:(fatigue OR exhaustion OR burnout) AND TITLE_ABS:(physician OR nurse OR clinician OR radiologist) — 67
  - Europe PMC: TITLE_ABS:("generative AI" OR "generative artificial intelligence" OR ChatGPT OR "large language model") AND TITLE_ABS:(fatigue OR exhaustion OR burnout) AND TITLE_ABS:(longitudinal OR diary OR "experience sampling" OR randomized OR randomised OR "multi-wave" OR "time-lagged") — 24
  - Semantic Scholar bulk: "passive fatigue" 87; "passive fatigue" + (automated | automation) 36; "alert fatigue" 1,214; "alert fatigue" + ("artificial intelligence" | "machine learning") 251; ("AI scribe" | "ambient scribe" | "ambient AI") + (burnout | fatigue) 95; "decision fatigue" + ("artificial intelligence" | "generative AI") 39
  - J-STAGE: `AI 疲労` ("AI fatigue") 9,066 full-text matches (top 100 titles: no relevant record); `生成AI 疲労` ("generative AI fatigue") 201; `AI疲れ` ("AI tiredness") 3
  - CiNii Research: `AI 疲労` 157 (top 100: 32 titles with both term types, none relevant); `生成AI 疲労` 2
  - Developer-tool fatigue (Copilot, coding assistants): not measured (term ambiguity; OpenAlex unavailable)
- **How records went into the candidate list:** none directly. The sizing informed which survey rounds to run; seed papers it confirmed were used to test the later searches.

---

## 4. S-12: Japanese-language literature and Japan-related studies

- **Purpose:** find Japanese-language studies, or studies of Japanese participants, on fatigue among people who use, supervise or evaluate AI.
- **Date and time:** 2026-09-29. Japanese-source queries 21:12:33; abstract screen of J-STAGE pages 21:17:53 and 21:19:26 (second pass for six pages); English-source queries 21:21:36.
- **Query design fixed before the first query** (the design note was written before 21:12).
- **Term lists:**
  - AI terms (Japanese set, 6): `AI`, `人工知能` (artificial intelligence), `ChatGPT`, `大規模言語モデル` (large language model), `LLM`, `チャットボット` (chatbot)
  - Fatigue terms (Japanese set, 7): `疲労` (fatigue), `疲れ` (tiredness), `疲弊` (exhaustion/wear-out), `燃え尽き` (burn-out), `バーンアウト` (burnout), `消耗` (depletion), `テクノストレス` (technostress)
  - Narrow AI terms (4): `生成AI` (generative AI), `ChatGPT`, `大規模言語モデル`, `LLM`; burden terms (2): `負担` (burden), `負荷` (load)
  - English AI terms (5): generative AI, ChatGPT, large language model, artificial intelligence, chatbot; English fatigue terms (4): fatigue, burnout, exhaustion, technostress
- **Queries and results (Japanese-language sources):**

| Source | Field | Query strings | Runs | Total hits (sum) |
|---|---|---|---|---|
| J-STAGE WebAPI (service 3, count 1000; fields are matched as substrings; a space between two words means AND; no OR) | title | every pair `<Japanese AI term> <Japanese fatigue term>`, e.g. `AI 疲労`, `AI 疲れ`, `人工知能 燃え尽き` | 42 | 14 (only `AI 疲労` returned hits: 14) |
| J-STAGE | abstract | same 42 pairs | 42 | 25 (9 queries with hits, e.g. `AI 疲労` 12, `AI 疲れ` 4) |
| J-STAGE | title | every pair `<narrow AI term> <burden term>`, e.g. `生成AI 負荷` | 8 | 3 |
| J-STAGE | abstract | same 8 pairs | 8 | 156 |
| J-STAGE | title | every pair `<English AI term> <English fatigue term>`, e.g. `large language model exhaustion` | 20 | 1 |
| J-STAGE | abstract | same 20 pairs | 20 | 16 |
| J-STAGE | full text (counts only, for comparison) | `AI 疲労`; `生成AI 疲労` | 2 | 9,066; 201 |
| CiNii Research (all), title, OpenSearch v1 | title | `(AI OR 人工知能 OR ChatGPT OR 大規模言語モデル OR LLM OR チャットボット) (疲労 OR 疲れ OR 疲弊 OR 燃え尽き OR バーンアウト OR 消耗 OR テクノストレス)` | 1 | 54 |
| CiNii Research (all) | title | `(生成AI OR ChatGPT OR 大規模言語モデル OR LLM) (負担 OR 負荷)` | 1 | 24 |
| CiNii Research (all) | title | `("generative AI" OR ChatGPT OR "large language model" OR "artificial intelligence" OR chatbot) (fatigue OR burnout OR exhaustion OR technostress)` | 1 | 19 |
| CiNii Research (KAKEN research projects) | title | the same three strings | 3 | 9, 2, 2 |
| National Diet Library Search (OpenSearch) | title | every pair `<Japanese AI term> <Japanese fatigue term>` (e.g. `AI 疲労`, `AI 疲れ`) | 42 | 132 (9 queries with hits) |

- **Queries and results (English-language sources, Japan-related):**
  - Europe PMC, `TITLE_ABS` plus affiliation, result type "core": `TITLE_ABS:("generative AI" OR ChatGPT OR "large language model" OR "artificial intelligence" OR chatbot) AND TITLE_ABS:(fatigue OR burnout OR exhaustion OR technostress) AND (TITLE_ABS:(Japan OR Japanese) OR AFF:Japan)` — 22 hits
  - Europe PMC: same without `OR AFF:Japan`: `TITLE_ABS:("generative AI" OR ChatGPT OR "large language model" OR "artificial intelligence" OR chatbot) AND TITLE_ABS:(fatigue OR burnout OR exhaustion OR technostress) AND TITLE_ABS:(Japan OR Japanese)` — 11 hits
  - Semantic Scholar bulk search (title and abstract): `("generative AI" | ChatGPT | "large language model" | "artificial intelligence" | chatbot) + (fatigue | burnout | exhaustion | technostress) + (Japan | Japanese)` — 25 hits
  - OpenAlex search: `("generative AI" OR ChatGPT OR "large language model" OR "artificial intelligence" OR chatbot) AND (fatigue OR burnout OR exhaustion OR technostress) AND (Japan OR Japanese)` — **not run successfully**: HTTP 503 ("anonymous search is paused"), retried at 21:40 with the same result. No count.
- **Filters:** no date, language or document-type filter. Records retrieved before de-duplication: J-STAGE 215, CiNii Research 110, National Diet Library Search 132. The union of the three English-source runs, de-duplicated by DOI, was 39 records.
- **Not searched (recorded):** Ichushi Web (paid), the Information Processing Society of Japan digital library (no scripted search), Google Scholar (automated retrieval prohibited), conference abstracts not in J-STAGE or CiNii; the abstract field of CiNii Research (returned 0 hits in a trial).
- **How records went into the candidate list:** a machine screen with pre-fixed regular expressions kept records whose title contained both an AI term and a fatigue term, and J-STAGE records matched via the abstract field whose abstract text contained both (22 passed from 145 abstracts checked); 75 Japanese-source records remained after de-duplication by title. An AI assistant read titles and abstracts and tabulated them (most were materials fatigue, "Al alloy", or AI used to detect human fatigue). Five English records on Japanese participants and four non-Japan records on AI use and burnout became candidates on the first assembly (2026-09-30 04:50); 16 more S-12 records were added on 2026-09-30 by researcher decision (section 13).
- **Deviations recorded:** six J-STAGE pages lacked the machine-readable abstract and were read from the page body with the same expressions (5 passed); two records were added from outside the fixed queries (one by following a reference of a retrieved paper, one by reading a supplementary table).

---

## 5. S-02: retrieval of 11 pre-identified records (not a search)

- **Purpose:** retrieve bibliographic data, abstracts and (where open) full text for 11 records selected from the search-gap check and from the reference list of one existing review; plus two IEEE DataPort datasets.
- **Date and time:** 2026-09-29 21:38:40 (design fixed before the run).
- **Source/interface:** Crossref and DataCite lookups by DOI; Europe PMC and Semantic Scholar by DOI; publisher pages. No query string: records were fetched by DOI.
- **Hit count:** not applicable (11 DOIs given; abstracts obtained for 10, 1 not obtained).
- **How records entered:** all 11 became candidate rows (S-02 candidates). On 2026-09-30 two further primary studies were added from a systematic-review preprint (section 13, matching).
- **Deviation recorded:** one open full text (Zenodo) could not be fetched on 2026-09-29 (HTTP 403) and was read on 2026-09-30 from a downloaded copy.

---

## 6. S-08: AI-fatigue scales

- **Purpose:** find development and validation papers of measures in which AI appears in the items or definition.
- **Date and time:** 2026-09-29 21:46:49 (design fixed before the run).
- **Queries (verbatim):**
  - Europe PMC (`TITLE_ABS`, result type "core"): `TITLE_ABS:("AI fatigue" OR "artificial intelligence fatigue" OR "generative AI fatigue" OR "ChatGPT fatigue" OR "AI-induced fatigue" OR "AI-related fatigue" OR "chatbot fatigue" OR "GenAI fatigue" OR "AI exhaustion" OR "AI burnout") AND TITLE_ABS:(scale OR questionnaire OR inventory OR instrument OR psychometric OR validation OR "factor analysis")` — 2 hits (all viewed)
  - Semantic Scholar bulk search: `("AI fatigue" | "artificial intelligence fatigue" | "generative AI fatigue" | "ChatGPT fatigue" | "AI-induced fatigue" | "AI-related fatigue" | "chatbot fatigue" | "GenAI fatigue" | "AI exhaustion" | "AI burnout") + (scale | questionnaire | inventory | instrument | psychometric | validation | "factor analysis")` — 6 hits (all viewed)
  - Crossref `query.title` (relevance ranked; top 50 titles viewed; count not meaningful): `AI fatigue scale`; `AI fatigue questionnaire`; `generative AI fatigue scale`
  - OpenAlex search: `("AI fatigue" OR "artificial intelligence fatigue" OR "generative AI fatigue" OR "ChatGPT fatigue" OR "AI-induced fatigue" OR "AI-related fatigue" OR "chatbot fatigue" OR "GenAI fatigue" OR "AI exhaustion" OR "AI burnout") AND (scale OR questionnaire OR inventory OR instrument OR psychometric OR validation OR "factor analysis")` — 350 hits (top 200 titles viewed; 24 with both an AI term and a fatigue term were read)
  - Semantic Scholar citations of the original paper of one AI-fatigue scale, by DOI (10.1016/j.chbr.2026.101186) — 5 records, all viewed
- **Filters:** none.
- **Deviation recorded:** OpenAlex returned HTTP 503 at 21:21 for S-12 but responded at 21:46.
- **How records went into the candidate list:** titles read by an AI assistant; scale-development papers were already in the base bibliography. Records that were neither scales nor already present (position papers, reviews, primary studies) were listed in the survey file. Three further S-08 primary-study records were added on 2026-09-30 by researcher decision (section 13).

---

## 7. S-04: fatigue and burnout among AI users, comparative studies

- **Purpose:** find studies comparing groups or periods with and without AI that measured users' fatigue, burnout, exhaustion, workload or burden.
- **Date and time:** 2026-09-29 21:58:48 (design fixed before the run).
- **Source/interface:** Europe PMC REST (`TITLE_ABS`, result type "core", all records); Semantic Scholar bulk search; OpenAlex search (up to 1,000 by relevance).
- **Queries (verbatim) and hits:**
  - Europe PMC Q1 (AI documentation support) — 170: `TITLE_ABS:("ambient AI" OR "AI scribe" OR "ambient scribe" OR "ambient listening" OR "ambient artificial intelligence" OR "ambient documentation" OR "digital scribe") AND TITLE_ABS:(burnout OR fatigue OR exhaustion OR "cognitive load" OR "task load" OR workload OR "documentation burden")`
  - Europe PMC Q2 (AI draft replies) — 28: `TITLE_ABS:("large language model" OR "generative AI" OR "AI-generated" OR "artificial intelligence") AND TITLE_ABS:("draft replies" OR "draft responses" OR "in-basket" OR inbox OR "patient messages") AND TITLE_ABS:(burnout OR fatigue OR "cognitive burden" OR "task load" OR workload)`
  - Europe PMC Q3 (general, including non-health) — 85: `TITLE_ABS:("generative AI" OR "large language model" OR ChatGPT OR Copilot OR "AI assistant" OR "AI tool" OR "artificial intelligence") AND TITLE_ABS:(burnout OR fatigue OR exhaustion) AND TITLE_ABS:(randomized OR randomised OR "controlled trial" OR crossover OR "pre-post" OR "before and after" OR "quasi-experimental" OR "difference-in-differences" OR "field experiment")`
  - Semantic Scholar bulk (non-health) — 1,119: `("generative AI" | ChatGPT | Copilot | "large language model" | "AI assistant") + (burnout | fatigue | exhaustion | "cognitive load" | workload) + (randomized | experiment | "field experiment" | intervention | "quasi-experimental" | "difference-in-differences")`
  - OpenAlex (same terms as Q3; top 1,000 by relevance) — 124,279: `("generative AI" OR "large language model" OR ChatGPT OR Copilot OR "AI assistant" OR "AI tool" OR "artificial intelligence") AND (burnout OR fatigue OR exhaustion) AND (randomized OR randomised OR "controlled trial" OR crossover OR "pre-post" OR "before and after" OR "quasi-experimental" OR "difference-in-differences" OR "field experiment")`
- **Filters:** none at query time.
- **Deviations recorded:** (1) OpenAlex did not interpret AND, OR and quotation marks as expected (top results were general reviews), so a machine pre-screen replaced the planned first manual title screen; the screen was fixed before looking at the records that passed. (2) The screen's design-term pattern missed one seed paper (a pre/post intervention study); a supplementary pattern re-admitted 22 records. (3) An abstract-cleaning error (text after a "<" sign removed) affected 31 abstracts; they were re-extracted with corrected abstracts. (4) 135 records without abstracts were screened on title only. A seed paper on time-only measures (Tai-Seale et al. 2024) was not retrieved by these queries and was added separately (section 13).
- **How records went into the candidate list:** 2,319 unique records; machine screen (AI term, fatigue or load term, comparative-design term in title or abstract) left 993; Europe PMC records were kept whole and Semantic Scholar/OpenAlex-only records were kept only if title or abstract contained burnout, fatigue or exhaust (267 records, 289 after the supplement). Extraction by AI sub-assistants, verification by the main assistant against abstracts. Tabulated comparative studies measuring fatigue/burnout (34 rows) and cross-sectional user/non-user comparisons (5 rows; 33 and 4 after merging rows that overlapped other sections) became candidates on first assembly; the 47 workload/time-only comparative studies were added later (section 13).

---

## 8. S-05: fatigue while monitoring automation

- **Purpose:** find studies of passive fatigue, vigilance decrement and complacency among people who monitor automated or AI systems.
- **Date and time:** 2026-09-29 22:08:22 (design fixed before the run).
- **Queries (verbatim) and hits:**
  - Crossref, six seed DOIs looked up one by one (10.1201/b12791-3.1, 10.1037/a0034386, 10.1016/j.promfg.2015.07.499, 10.1177/0018720811423261, 10.1016/j.aap.2018.04.004, 10.1177/0018720810376055) — 6 records
  - Europe PMC (`TITLE_ABS`, result type "core"):
    - E1 `TITLE_ABS:"passive fatigue"` — 26
    - E2 `TITLE_ABS:("automation complacency" OR "automation-induced complacency")` — 25
    - E3 `TITLE_ABS:("vigilance decrement" OR "vigilance decline" OR underload) AND TITLE_ABS:(automation OR automated OR autonomous OR "artificial intelligence") AND TITLE_ABS:(fatigue OR sleepiness OR drowsiness OR arousal)` — 11
    - E4 `TITLE_ABS:("human oversight" OR "human-in-the-loop" OR "human monitoring" OR supervisory OR supervision) AND TITLE_ABS:("artificial intelligence" OR "machine learning" OR "AI system" OR "AI-assisted") AND TITLE_ABS:(fatigue OR vigilance OR complacency)` — 36
  - Semantic Scholar bulk search:
    - S1 `"passive fatigue"` — 87
    - S2 `("passive fatigue" | "task-induced fatigue" | "vigilance decrement" | underload) + (automation | automated | autonomous | "artificial intelligence")` — 205
    - S3 `("human oversight" | "human-in-the-loop" | "AI-assisted" | "decision support") + (vigilance | "passive fatigue" | complacency) + ("artificial intelligence" | "machine learning")` — 52
  - OpenAlex was not used for this round.
- **Filters:** none.
- **Deviation recorded:** a source-merge defect let an empty abstract from one source overwrite a retrieved abstract; six records were extracted without their abstracts and four table rows were corrected after review (the machine screen itself was applied before the merge and was not affected).
- **How records went into the candidate list:** 354 unique records; machine screen (a fatigue/vigilance term and an automation/AI/supervision term in title or abstract) passed 221. By the researcher's scope decision (b), only the 9 records in which the paper describes the monitored system as AI or machine learning became candidates; studies of conventional automation (for example most automated-driving studies) were left out of the candidate list.

---

## 9. S-15: overreliance on AI and fatigue (both directions)

- **Purpose:** find studies measuring both reliance on, or uncritical acceptance of, AI or automation and fatigue or exhaustion.
- **Date and time:** 2026-09-30 03:59:20 (query design fixed at 03:54, before any query was run).
- **Source/interface:** Europe PMC REST (`TITLE_ABS`, result type "core", all records); Semantic Scholar bulk search. No OpenAlex search.
- **Queries (verbatim) and hits:**
  - E1 — 51: `TITLE_ABS:("automation bias" OR overreliance OR "over-reliance" OR overtrust OR "over-trust" OR "AI reliance" OR "reliance on AI" OR "AI dependence" OR "AI dependency" OR "algorithmic advice" OR "advice taking" OR complacency) AND TITLE_ABS:(fatigue OR "decision fatigue" OR "mental fatigue" OR "ego depletion" OR exhaustion OR "sleep deprivation" OR sleepiness OR burnout) AND TITLE_ABS:("artificial intelligence" OR "machine learning" OR "decision support" OR algorithm OR "large language model" OR ChatGPT OR "generative AI" OR automation OR automated)`
  - E2 — 114: `TITLE_ABS:("decision fatigue" OR "mental fatigue" OR "cognitive fatigue") AND TITLE_ABS:("artificial intelligence" OR "decision support" OR "machine learning" OR "large language model" OR "generative AI" OR ChatGPT OR algorithm)`
  - S1 — 436: `("automation bias" | overreliance | "over-reliance" | "AI reliance" | "reliance on AI" | "AI dependence" | complacency) + (fatigue | "decision fatigue" | "mental fatigue" | exhaustion | depletion)`
  - S2 — 58: `("decision fatigue" | "mental fatigue" | "cognitive fatigue") + ("AI advice" | "AI recommendations" | "decision support" | "algorithmic advice" | "AI-assisted")`
  - S3 — 36: `("generative AI" | ChatGPT | "large language model") + (dependence | dependency | overreliance) + (fatigue | exhaustion | burnout)`
- **Filters:** none at query time; records dated after 2026 excluded after retrieval (0 records).
- **Hit count after de-duplication:** 641 unique records. Machine screen (reliance, fatigue and AI/automation term groups all present in title or abstract): 192 passed; 6 already known; 187 sent to extraction. 189 of the 641 had no abstract and were screened on title alone.
- **How records went into the candidate list:** AI sub-assistants extracted fields from abstracts; the main assistant verified rows of primary studies measuring both reliance and fatigue against abstracts. 17 records became candidates on first assembly; 6 more primary studies the paper called AI-related were added on 2026-09-30 07:48 after a review found the first assembly had been narrowed by the assistant's own eligibility view.
- **Deviation recorded:** the stored query record of E1 was rewritten on 2026-09-30 (about 04:25) as a list of three AND-joined clauses because the text exceeded a 500-character check; joined with " AND " it reproduces the string above.

---

## 10. S-14: AI stressors / technostress and burnout (main and supplementary)

- **Purpose:** find studies of AI-related stressors (technostress, AI anxiety, job-loss awareness) and burnout, exhaustion or strain.
- **Date and time:** main search 2026-09-30 04:01:22; supplementary search 04:02:50 (design fixed at 03:54 for the main search).
- **Queries (verbatim) and hits:**
  - Main, Europe PMC E1 — 24: `TITLE_ABS:(technostress OR "techno-stress" OR technostressor OR technostressors OR "AI anxiety" OR "AI awareness" OR STARA OR "AI-induced stress" OR "AI stressors" OR "AI-related stress") AND TITLE_ABS:(burnout OR "burn-out" OR exhaustion OR "emotional exhaustion" OR strain) AND TITLE_ABS:("artificial intelligence" OR "generative AI" OR ChatGPT OR "machine learning" OR "large language model" OR robot OR algorithm)`
  - Main, Europe PMC E2 — 11: `TITLE_ABS:("artificial intelligence" OR "generative AI" OR ChatGPT OR "large language model") AND TITLE_ABS:("Maslach Burnout Inventory" OR "Copenhagen Burnout Inventory" OR "Oldenburg Burnout Inventory" OR "Burnout Assessment Tool" OR "Shirom-Melamed")`
  - Main, Semantic Scholar S1 — 93: `(technostress | technostressor | "AI anxiety" | "AI awareness" | STARA | "AI stressor") + (burnout | exhaustion | strain) + ("artificial intelligence" | "generative AI" | ChatGPT)`
  - Main, Semantic Scholar S2 — 14: `("AI-induced technostress" | "AI technostress" | "AI-stressors" | "AI stressors") + (burnout | exhaustion | well-being)`
  - Supplementary, Europe PMC — 31: `TITLE_ABS:(technostress OR "job stress" OR "work stress" OR "occupational stress" OR "AI anxiety" OR "AI awareness" OR STARA) AND TITLE_ABS:(burnout OR "burn-out" OR exhaustion OR "emotional exhaustion") AND TITLE_ABS:(AI OR "artificial intelligence" OR "AI adoption" OR "AI dependency" OR "generative AI" OR ChatGPT)`
  - Supplementary, Semantic Scholar — 17: `("AI adoption" | "AI dependency" | "AI use" | "AI usage" | "AI implementation") + ("job stress" | technostress | "work stress") + (burnout | exhaustion)`
- **Filters:** none at query time; records dated after 2026 excluded after retrieval (0 records).
- **Counts:** main search 113 unique records, 95 passed the machine screen (stressor, burnout and AI term groups in title or abstract), 4 already known, 92 sent to extraction; supplementary search 44 unique records, all passed, 6 already known, 24 overlapped with the main search, giving 14 more; 106 records extracted in total.
- **Deviation recorded (one line):** the supplementary search was added because the main search retrieved none of its three seed papers; its query was written into the script and run (04:02:50) before the justification was written to the decision log (about 04:05); no record written before the run exists.
- **How records went into the candidate list:** as in section 9: AI extraction, main-assistant verification, then 34 candidates on first assembly and 12 more (4 + 6 + 2 records split into versions) added on 2026-09-30 after the same review.

---

## 11. S-13: organisation-level AI fatigue

- **Purpose:** find studies where organisational factors (leadership, policy, support) shape workers' AI-related fatigue or burnout, or where the organisation is the unit of analysis ("change fatigue" and similar).
- **Date and time:** 2026-09-30 04:03:12 (design fixed at 03:54).
- **Queries (verbatim) and hits:**
  - Europe PMC E1 — 78: `TITLE_ABS:("artificial intelligence" OR "generative AI" OR ChatGPT OR "AI adoption" OR "AI implementation") AND TITLE_ABS:(organizational OR organisational OR leadership OR "organizational support" OR "change management" OR "human resource" OR "AI policy" OR managerial OR supervisor) AND TITLE_ABS:(fatigue OR burnout OR exhaustion OR "change fatigue")`
  - Europe PMC E2 — 39: `TITLE_ABS:("change fatigue" OR "initiative fatigue" OR "transformation fatigue" OR "innovation fatigue" OR "AI fatigue") AND TITLE_ABS:(organization OR organisation OR organizational OR organisational OR workplace OR employee OR employees)`
  - Semantic Scholar S1 — 166: `("change fatigue" | "transformation fatigue" | "innovation fatigue" | "AI fatigue") + (organization | organisation | workplace | employees)`
  - Semantic Scholar S2 — 30: `("AI adoption" | "AI implementation" | "generative AI") + (leadership | "organizational support" | "change management" | "AI policy") + (burnout | exhaustion | fatigue)`
- **Filters:** none at query time; records dated after 2026 excluded after retrieval.
- **Counts:** 270 unique records; 112 passed the machine screen (organisation, fatigue and AI term groups); 2 already known; 110 sent to extraction. 64 of the 270 had no abstract.
- **How records went into the candidate list:** as in section 9: 15 candidates on first assembly, 5 more primary studies added on 2026-09-30 after the review of AI-based narrowing.

---

## 12. Rounds that added no candidates; search-development trial

- **S-09 (theory frameworks) and S-11 (use of the word "fatigue" for AI), 2026-09-30:** abstracts of framework source papers were fetched by DOI (18:25 and 18:28) and the 259 pre-registration records were read for how they use the term (retrieval 18:13). These rounds ran no topic search and added no candidates. In S-11, a Crossref title search for "Concept Analysis of Prompt Fatigue" (top 5 results) returned no matching record, and a Semantic Scholar title search returned HTTP 429 twice (18:28 and 18:35), so it was not run. No candidate resulted.
- **Search-development trial v0 (2026-10-01, 01:34 to 02:33):** the registration's draft query strings were run once to count hits and test recall against 25 known seed records (Europe PMC, Semantic Scholar, ERIC, arXiv, Zenodo). It was a development step, not a source of candidates; no record from it was added to the candidate list. Its strings and counts are in the protocol's own query appendix.

---

## 13. Non-search additions and other routes into the candidate list

These routes were not searches.

1. **Reference-list tracing of one existing review (base bibliography), 2026-09-28:** three records picked from its reference list and added to S-02 (a task list of the same day says four; the S-02 list has three). Method of selection is not recorded beyond this.
2. **Citation tracing within S-12 (2026-09-29):** one record followed from the reference list of a retrieved Cureus paper; one supplementary table read to check a scale's items. Not searches.
3. **Matching the included studies of an existing review (2026-09-30, 10:45 to 11:05):** the 32 included studies of a non-peer-reviewed systematic review posted on Zenodo were matched by DOI against the base and the candidates; 3 were in the base, 1 was already a candidate, 28 were new. The 28 were screened by regular expressions for AI terms and fatigue terms in title and abstract (applied after the matching, not fixed in advance); two primary studies passed and were added as candidates. The other 26 were not added. This is a record-matching step, not a search.
4. **Primary studies the AI assistant had screened out (2026-09-30, 07:48):** after a review found that candidates had been narrowed by the assistant's own eligibility view, all primary studies that a paper describes as AI-related were added from the survey fact files (132 to 157 candidates).
5. **Workload/time-only comparative studies, S-04 (2026-09-30, 11:32 and 12:40):** by researcher decision, 34 studies were added from the S-04 extraction table (rows with no fatigue scale and a workload or time measure), then 12 studies that the table's classification had missed plus one seed paper (Tai-Seale et al. 2024; bibliographic data from Europe PMC by DOI) were added. The 12 and the seed were selected by re-reading 21 abstracts retrieved by DOI/Europe PMC and OpenAlex. Totals: 159 to 193 to 206 candidates.
6. **Researcher decision on 19 further primary studies (2026-09-30, 15:47 to 16:17):** from the existing S-08 and S-12 fact files (3 and 16 records), applying four conditions (a literature item; a research report or trial protocol; the paper names the system as AI or machine learning; real people's fatigue, burnout or burden is an object of the study). Abstracts were re-fetched from Europe PMC, Semantic Scholar, OpenAlex, Crossref and CiNii Research by DOI. 206 to 225 candidates.
7. **Cross-matching with another review's dataset records (2026-09-28):** two IEEE DataPort records found by a different review of the same team were compared with the candidate list; they were not added (no collection procedure documented).
8. **Merging:** on 2026-09-30 to 2026-10-01, 5 duplicate-version records were merged into single records (225 to 220 additional candidates). This removed records; it added none.

## 14. Review-aimed search (2026-10-02), the source of the 43 review-search records

- **Purpose:** find existing reviews of AI-related fatigue, to check whether this review's questions had already been answered.
- **Date and time:** 2026-10-02, 02:50 to 03:53.
- **Sources/interfaces:** OpenAlex, Europe PMC, Crossref and Semantic Scholar, through their free public APIs without keys; no contact address was sent.
- **Definition fixed before the run:** records published from 2020-01-01, in any language, whose title or abstract has an AI term (artificial intelligence, AI, generative AI, ChatGPT, large language model(s), LLM(s), chatbot(s), machine learning, algorithm(s)/algorithmic, automation/automated, 自動化 "automation", 人工知能 "artificial intelligence", 生成 AI "generative AI") and a fatigue term (fatigue, exhaustion, burnout/burn-out, weariness, tiredness, technostress, 疲労 "fatigue", 燃え尽き "burnout", バーンアウト "burnout", テクノストレス "technostress"), and either a review term in the title or abstract (review, systematic review, scoping review, meta-analysis, meta-synthesis, literature review, umbrella review, state of the art, レビュー "review", 総説 "review article", メタ分析 "meta-analysis") or a review document type in the API. One query was run per fatigue term (AI terms OR-ed, AND the fatigue term, AND review terms OR-ed); when a query returned more than 2,000 records it was split by AI term. Crossref was queried with bibliographic text queries ("{AI term} {fatigue term} review"), each cut at 2,000 records. The term check was a Python regular expression without word boundaries (case-insensitive except for "AI").
- **Counts:** 132 queries (OpenAlex 38, of which 16 failed with HTTP 429, and none of the queries by review document type ran; Europe PMC 22; Crossref 36, all cut at 2,000 records; Semantic Scholar 36). After merging duplicates by DOI or normalised title: 5,721 records, of which 79 were already in the source database.
- **How records went into the candidate list:** a machine rule on titles sorted the records into layers. The two layers with an AI term, a fatigue term and a review term in the title (122 records, 99 after merging titles) were sorted again by title words, and the 48 that were not about AI detecting or predicting fatigue, about non-human (material) fatigue or a peer-review report were kept as a reading list; two clear misfits were removed (46). Three of the 46 were already in the source database; the other 43 are the review-search records. They were not screened before registration.
- **Limitations recorded with the search:** matching without word boundaries and the broad AI terms brought in many technical records; 16 OpenAlex queries are missing; Crossref results are the top 2,000 by relevance; reviews without a review term in the title were not read; no paid database was used.

Every query as run, copied from the search log:

| # | API | Query string (verbatim) | Run at | Hits reported | Retrieved | Passed the term check | Truncated | Error |
|---|---|---|---|---|---|---|---|---|
| 1 | OpenAlex | ("artificial intelligence") AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:50:38 | 1217 | 1220 | 1006 | False | None |
| 2 | OpenAlex | (AI) AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:50:59 | 1586 | 1588 | 1305 | False | None |
| 3 | OpenAlex | ("generative AI") AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:51:24 | 96 | 96 | 83 | False | None |
| 4 | OpenAlex | (ChatGPT) AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:51:31 | 75 | 75 | 61 | False | None |
| 5 | OpenAlex | ("large language model") AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:51:39 | 175 | 175 | 132 | False | None |
| 6 | OpenAlex | (LLM) AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:51:46 | 177 | 177 | 134 | False | None |
| 7 | OpenAlex | (chatbot) AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:51:54 | 79 | 79 | 67 | False | None |
| 8 | OpenAlex | ("machine learning") AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:52:02 | 1147 | 1148 | 812 | False | None |
| 9 | OpenAlex | (algorithm) AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:52:22 | 1395 | 1395 | 1015 | False | None |
| 10 | OpenAlex | (algorithmic) AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:52:44 | 1395 | 1396 | 1015 | False | None |
| 11 | OpenAlex | (automation) AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:53:05 | 352 | 352 | 302 | False | None |
| 12 | OpenAlex | (automated) AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:53:15 | 724 | 725 | 534 | False | None |
| 13 | OpenAlex | (自動化) AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:53:30 | 1 | 1 | 0 | False | None |
| 14 | OpenAlex | (人工知能) AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:53:42 | 1 | 1 | 0 | False | None |
| 15 | OpenAlex | (生成AI) AND (fatigue) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:53:53 | 1 | 1 | 1 | False | None |
| 16 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (exhaustion) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:54:05 | 685 | 687 | 532 | False | None |
| 17 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (burnout) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:54:20 | 1195 | 1196 | 1024 | False | None |
| 18 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (burn-out) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:54:43 | 196 | 196 | 21 | False | None |
| 19 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (weariness) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:54:51 | 45 | 45 | 21 | False | None |
| 20 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (tiredness) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:54:58 | 182 | 182 | 53 | False | None |
| 21 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (technostress) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:55:07 | 212 | 212 | 203 | False | None |
| 22 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (疲労) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:55:16 | 42 | 42 | 5 | False | None |
| 23 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (燃え尽き) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:55:23 | None | 0 | 0 | False | HTTP 429 |
| 24 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (バーンアウト) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:57:05 | None | 0 | 0 | False | HTTP 429 |
| 25 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (テクノストレス) AND (review OR "systematic review" OR "scoping review" OR meta-analysis OR meta-synthesis OR "literature review" OR "umbrella review" OR "state of the art" OR レビュー OR 総説 OR メタ分析) | 2026-10-02 02:57:55 | None | 0 | 0 | False | HTTP 429 |
| 26 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (fatigue) | 2026-10-02 02:58:46 | None | 0 | 0 | False | HTTP 429 |
| 27 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (exhaustion) | 2026-10-02 02:59:37 | None | 0 | 0 | False | HTTP 429 |
| 28 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (burnout) | 2026-10-02 03:00:27 | None | 0 | 0 | False | HTTP 429 |
| 29 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (burn-out) | 2026-10-02 03:01:18 | None | 0 | 0 | False | HTTP 429 |
| 30 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (weariness) | 2026-10-02 03:02:09 | None | 0 | 0 | False | HTTP 429 |
| 31 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (tiredness) | 2026-10-02 03:02:59 | None | 0 | 0 | False | HTTP 429 |
| 32 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (technostress) | 2026-10-02 03:03:50 | None | 0 | 0 | False | HTTP 429 |
| 33 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (疲労) | 2026-10-02 03:04:41 | None | 0 | 0 | False | HTTP 429 |
| 34 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (燃え尽き) | 2026-10-02 03:05:31 | None | 0 | 0 | False | HTTP 429 |
| 35 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (バーンアウト) | 2026-10-02 03:06:22 | None | 0 | 0 | False | HTTP 429 |
| 36 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot OR "machine learning" OR algorithm OR algorithmic OR automation OR automated OR 自動化 OR 人工知能 OR 生成AI) AND (テクノストレス) | 2026-10-02 03:07:13 | None | 0 | 0 | False | HTTP 429 |
| 37 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"fatigue") AND (TITLE_ABS:"review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" OR TITLE_ABS:"meta-analysis" OR TITLE_ABS:"meta-synthesis" OR TITLE_ABS:"literature review" OR TITLE_ABS:"umbrella review" OR TITLE_ABS:"state of the art" OR TITLE_ABS:"レビュー" OR TITLE_ABS:"総説" OR TITLE_ABS:"メタ分析" OR PUB_TYPE:"review") AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:50:55 | 593 | 593 | 533 | False | None |
| 38 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"exhaustion") AND (TITLE_ABS:"review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" OR TITLE_ABS:"meta-analysis" OR TITLE_ABS:"meta-synthesis" OR TITLE_ABS:"literature review" OR TITLE_ABS:"umbrella review" OR TITLE_ABS:"state of the art" OR TITLE_ABS:"レビュー" OR TITLE_ABS:"総説" OR TITLE_ABS:"メタ分析" OR PUB_TYPE:"review") AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:51:45 | 104 | 104 | 97 | False | None |
| 39 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"burnout") AND (TITLE_ABS:"review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" OR TITLE_ABS:"meta-analysis" OR TITLE_ABS:"meta-synthesis" OR TITLE_ABS:"literature review" OR TITLE_ABS:"umbrella review" OR TITLE_ABS:"state of the art" OR TITLE_ABS:"レビュー" OR TITLE_ABS:"総説" OR TITLE_ABS:"メタ分析" OR PUB_TYPE:"review") AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:51:51 | 212 | 212 | 207 | False | None |
| 40 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"burn-out") AND (TITLE_ABS:"review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" OR TITLE_ABS:"meta-analysis" OR TITLE_ABS:"meta-synthesis" OR TITLE_ABS:"literature review" OR TITLE_ABS:"umbrella review" OR TITLE_ABS:"state of the art" OR TITLE_ABS:"レビュー" OR TITLE_ABS:"総説" OR TITLE_ABS:"メタ分析" OR PUB_TYPE:"review") AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:52:19 | 2 | 2 | 2 | False | None |
| 41 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"weariness") AND (TITLE_ABS:"review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" OR TITLE_ABS:"meta-analysis" OR TITLE_ABS:"meta-synthesis" OR TITLE_ABS:"literature review" OR TITLE_ABS:"umbrella review" OR TITLE_ABS:"state of the art" OR TITLE_ABS:"レビュー" OR TITLE_ABS:"総説" OR TITLE_ABS:"メタ分析" OR PUB_TYPE:"review") AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:52:21 | 1 | 1 | 1 | False | None |
| 42 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"tiredness") AND (TITLE_ABS:"review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" OR TITLE_ABS:"meta-analysis" OR TITLE_ABS:"meta-synthesis" OR TITLE_ABS:"literature review" OR TITLE_ABS:"umbrella review" OR TITLE_ABS:"state of the art" OR TITLE_ABS:"レビュー" OR TITLE_ABS:"総説" OR TITLE_ABS:"メタ分析" OR PUB_TYPE:"review") AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:52:24 | 8 | 8 | 3 | False | None |
| 43 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"technostress") AND (TITLE_ABS:"review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" OR TITLE_ABS:"meta-analysis" OR TITLE_ABS:"meta-synthesis" OR TITLE_ABS:"literature review" OR TITLE_ABS:"umbrella review" OR TITLE_ABS:"state of the art" OR TITLE_ABS:"レビュー" OR TITLE_ABS:"総説" OR TITLE_ABS:"メタ分析" OR PUB_TYPE:"review") AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:52:29 | 11 | 11 | 11 | False | None |
| 44 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"疲労") AND (TITLE_ABS:"review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" OR TITLE_ABS:"meta-analysis" OR TITLE_ABS:"meta-synthesis" OR TITLE_ABS:"literature review" OR TITLE_ABS:"umbrella review" OR TITLE_ABS:"state of the art" OR TITLE_ABS:"レビュー" OR TITLE_ABS:"総説" OR TITLE_ABS:"メタ分析" OR PUB_TYPE:"review") AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:52:34 | 0 | 0 | 0 | False | None |
| 45 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"燃え尽き") AND (TITLE_ABS:"review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" OR TITLE_ABS:"meta-analysis" OR TITLE_ABS:"meta-synthesis" OR TITLE_ABS:"literature review" OR TITLE_ABS:"umbrella review" OR TITLE_ABS:"state of the art" OR TITLE_ABS:"レビュー" OR TITLE_ABS:"総説" OR TITLE_ABS:"メタ分析" OR PUB_TYPE:"review") AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:52:38 | 0 | 0 | 0 | False | None |
| 46 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"バーンアウト") AND (TITLE_ABS:"review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" OR TITLE_ABS:"meta-analysis" OR TITLE_ABS:"meta-synthesis" OR TITLE_ABS:"literature review" OR TITLE_ABS:"umbrella review" OR TITLE_ABS:"state of the art" OR TITLE_ABS:"レビュー" OR TITLE_ABS:"総説" OR TITLE_ABS:"メタ分析" OR PUB_TYPE:"review") AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:52:43 | 0 | 0 | 0 | False | None |
| 47 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"テクノストレス") AND (TITLE_ABS:"review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" OR TITLE_ABS:"meta-analysis" OR TITLE_ABS:"meta-synthesis" OR TITLE_ABS:"literature review" OR TITLE_ABS:"umbrella review" OR TITLE_ABS:"state of the art" OR TITLE_ABS:"レビュー" OR TITLE_ABS:"総説" OR TITLE_ABS:"メタ分析" OR PUB_TYPE:"review") AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:52:49 | 0 | 0 | 0 | False | None |
| 48 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"fatigue") AND PUB_TYPE:"review" AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:52:51 | 378 | 378 | 373 | False | None |
| 49 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"exhaustion") AND PUB_TYPE:"review" AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:53:12 | 81 | 81 | 80 | False | None |
| 50 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"burnout") AND PUB_TYPE:"review" AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:53:30 | 149 | 149 | 149 | False | None |
| 51 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"burn-out") AND PUB_TYPE:"review" AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:53:36 | 2 | 2 | 2 | False | None |
| 52 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"weariness") AND PUB_TYPE:"review" AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:53:39 | 1 | 1 | 1 | False | None |
| 53 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"tiredness") AND PUB_TYPE:"review" AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:53:41 | 1 | 1 | 1 | False | None |
| 54 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"technostress") AND PUB_TYPE:"review" AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:53:44 | 8 | 8 | 8 | False | None |
| 55 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"疲労") AND PUB_TYPE:"review" AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:53:48 | 0 | 0 | 0 | False | None |
| 56 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"燃え尽き") AND PUB_TYPE:"review" AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:53:50 | 0 | 0 | 0 | False | None |
| 57 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"バーンアウト") AND PUB_TYPE:"review" AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:53:52 | 0 | 0 | 0 | False | None |
| 58 | EuropePMC | (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"AI" OR TITLE_ABS:"generative AI" OR TITLE_ABS:"ChatGPT" OR TITLE_ABS:"large language model" OR TITLE_ABS:"LLM" OR TITLE_ABS:"chatbot" OR TITLE_ABS:"machine learning" OR TITLE_ABS:"algorithm" OR TITLE_ABS:"algorithmic" OR TITLE_ABS:"automation" OR TITLE_ABS:"automated" OR TITLE_ABS:"自動化" OR TITLE_ABS:"人工知能" OR TITLE_ABS:"生成AI") AND (TITLE_ABS:"テクノストレス") AND PUB_TYPE:"review" AND FIRST_PDATE:[2020-01-01 TO 2026-12-31] | 2026-10-02 02:53:55 | 0 | 0 | 0 | False | None |
| 59 | Crossref | artificial intelligence fatigue review | 2026-10-02 03:03:52 | 3973608 | 2000 | 16 | True | None |
| 60 | Crossref | AI fatigue review | 2026-10-02 03:03:56 | 3628421 | 2000 | 26 | True | None |
| 61 | Crossref | generative AI fatigue review | 2026-10-02 03:04:01 | 3675679 | 2000 | 4 | True | None |
| 62 | Crossref | ChatGPT fatigue review | 2026-10-02 03:04:06 | 3203722 | 2000 | 9 | True | None |
| 63 | Crossref | large language model fatigue review | 2026-10-02 03:04:11 | 5241058 | 2000 | 4 | True | None |
| 64 | Crossref | chatbot fatigue review | 2026-10-02 03:04:16 | 3190359 | 2000 | 11 | True | None |
| 65 | Crossref | machine learning fatigue review | 2026-10-02 03:04:20 | 4961965 | 2000 | 23 | True | None |
| 66 | Crossref | algorithm fatigue review | 2026-10-02 03:04:25 | 3498150 | 2000 | 17 | True | None |
| 67 | Crossref | automation fatigue review | 2026-10-02 03:04:30 | 3351276 | 2000 | 18 | True | None |
| 68 | Crossref | automated fatigue review | 2026-10-02 03:04:35 | 3301008 | 2000 | 14 | True | None |
| 69 | Crossref | artificial intelligence exhaustion review | 2026-10-02 03:04:39 | 3909249 | 2000 | 3 | True | None |
| 70 | Crossref | AI exhaustion review | 2026-10-02 03:04:43 | 3563646 | 2000 | 6 | True | None |
| 71 | Crossref | generative AI exhaustion review | 2026-10-02 03:04:48 | 3610921 | 2000 | 2 | True | None |
| 72 | Crossref | ChatGPT exhaustion review | 2026-10-02 03:04:52 | 3138640 | 2000 | 1 | True | None |
| 73 | Crossref | large language model exhaustion review | 2026-10-02 03:04:57 | 5179331 | 2000 | 1 | True | None |
| 74 | Crossref | chatbot exhaustion review | 2026-10-02 03:05:02 | 3125278 | 2000 | 1 | True | None |
| 75 | Crossref | machine learning exhaustion review | 2026-10-02 03:05:08 | 4898790 | 2000 | 0 | True | None |
| 76 | Crossref | algorithm exhaustion review | 2026-10-02 03:05:13 | 3433407 | 2000 | 1 | True | None |
| 77 | Crossref | automation exhaustion review | 2026-10-02 03:05:18 | 3286389 | 2000 | 4 | True | None |
| 78 | Crossref | automated exhaustion review | 2026-10-02 03:05:22 | 3236072 | 2000 | 1 | True | None |
| 79 | Crossref | artificial intelligence burnout review | 2026-10-02 03:05:28 | 3933932 | 2000 | 25 | True | None |
| 80 | Crossref | AI burnout review | 2026-10-02 03:05:36 | 3588683 | 2000 | 36 | True | None |
| 81 | Crossref | generative AI burnout review | 2026-10-02 03:05:45 | 3635960 | 2000 | 12 | True | None |
| 82 | Crossref | ChatGPT burnout review | 2026-10-02 03:05:57 | 3163819 | 2000 | 22 | True | None |
| 83 | Crossref | large language model burnout review | 2026-10-02 03:06:07 | 5203812 | 2000 | 14 | True | None |
| 84 | Crossref | chatbot burnout review | 2026-10-02 03:06:16 | 3150453 | 2000 | 26 | True | None |
| 85 | Crossref | machine learning burnout review | 2026-10-02 03:06:26 | 4923168 | 2000 | 11 | True | None |
| 86 | Crossref | algorithm burnout review | 2026-10-02 03:06:30 | 3458585 | 2000 | 32 | True | None |
| 87 | Crossref | automation burnout review | 2026-10-02 03:06:35 | 3311570 | 2000 | 32 | True | None |
| 88 | Crossref | automated burnout review | 2026-10-02 03:06:40 | 3261252 | 2000 | 26 | True | None |
| 89 | Crossref | artificial intelligence weariness review | 2026-10-02 03:06:44 | 3902824 | 2000 | 3 | True | None |
| 90 | Crossref | AI weariness review | 2026-10-02 03:06:49 | 3557193 | 2000 | 6 | True | None |
| 91 | Crossref | generative AI weariness review | 2026-10-02 03:06:54 | 3604472 | 2000 | 3 | True | None |
| 92 | Crossref | ChatGPT weariness review | 2026-10-02 03:06:59 | 3132152 | 2000 | 4 | True | None |
| 93 | Crossref | large language model weariness review | 2026-10-02 03:07:03 | 5173088 | 2000 | 1 | True | None |
| 94 | Crossref | chatbot weariness review | 2026-10-02 03:07:09 | 3118789 | 2000 | 1 | True | None |
| 95 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (fatigue) + (review \| "systematic review" \| "scoping review" \| meta-analysis \| meta-synthesis \| "literature review" \| "umbrella review" \| "state of the art" \| "レビュー" \| "総説" \| "メタ分析") | 2026-10-02 02:52:20 | 1942 | 1942 | 1540 | False | None |
| 96 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (exhaustion) + (review \| "systematic review" \| "scoping review" \| meta-analysis \| meta-synthesis \| "literature review" \| "umbrella review" \| "state of the art" \| "レビュー" \| "総説" \| "メタ分析") | 2026-10-02 02:52:29 | 253 | 253 | 206 | False | None |
| 97 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (burnout) + (review \| "systematic review" \| "scoping review" \| meta-analysis \| meta-synthesis \| "literature review" \| "umbrella review" \| "state of the art" \| "レビュー" \| "総説" \| "メタ分析") | 2026-10-02 02:52:51 | 507 | 507 | 457 | False | None |
| 98 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (burn-out) + (review \| "systematic review" \| "scoping review" \| meta-analysis \| meta-synthesis \| "literature review" \| "umbrella review" \| "state of the art" \| "レビュー" \| "総説" \| "メタ分析") | 2026-10-02 02:54:18 | 42 | 42 | 8 | False | None |
| 99 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (weariness) + (review \| "systematic review" \| "scoping review" \| meta-analysis \| meta-synthesis \| "literature review" \| "umbrella review" \| "state of the art" \| "レビュー" \| "総説" \| "メタ分析") | 2026-10-02 02:54:22 | 23 | 23 | 12 | False | None |
| 100 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (tiredness) + (review \| "systematic review" \| "scoping review" \| meta-analysis \| meta-synthesis \| "literature review" \| "umbrella review" \| "state of the art" \| "レビュー" \| "総説" \| "メタ分析") | 2026-10-02 02:54:27 | 62 | 62 | 24 | False | None |
| 101 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (technostress) + (review \| "systematic review" \| "scoping review" \| meta-analysis \| meta-synthesis \| "literature review" \| "umbrella review" \| "state of the art" \| "レビュー" \| "総説" \| "メタ分析") | 2026-10-02 02:54:31 | 101 | 101 | 101 | False | None |
| 102 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + ("疲労") + (review \| "systematic review" \| "scoping review" \| meta-analysis \| meta-synthesis \| "literature review" \| "umbrella review" \| "state of the art" \| "レビュー" \| "総説" \| "メタ分析") | 2026-10-02 02:54:44 | 0 | 0 | 0 | False | None |
| 103 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + ("燃え尽き") + (review \| "systematic review" \| "scoping review" \| meta-analysis \| meta-synthesis \| "literature review" \| "umbrella review" \| "state of the art" \| "レビュー" \| "総説" \| "メタ分析") | 2026-10-02 02:54:48 | 0 | 0 | 0 | False | None |
| 104 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + ("バーンアウト") + (review \| "systematic review" \| "scoping review" \| meta-analysis \| meta-synthesis \| "literature review" \| "umbrella review" \| "state of the art" \| "レビュー" \| "総説" \| "メタ分析") | 2026-10-02 02:54:52 | 0 | 0 | 0 | False | None |
| 105 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + ("テクノストレス") + (review \| "systematic review" \| "scoping review" \| meta-analysis \| meta-synthesis \| "literature review" \| "umbrella review" \| "state of the art" \| "レビュー" \| "総説" \| "メタ分析") | 2026-10-02 02:55:03 | 0 | 0 | 0 | False | None |
| 106 | SemanticScholar | ("artificial intelligence") + (fatigue) | 2026-10-02 02:55:10 | 644 | 644 | 604 | False | None |
| 107 | SemanticScholar | (AI) + (fatigue) | 2026-10-02 02:55:19 | 806 | 806 | 757 | False | None |
| 108 | SemanticScholar | ("generative AI") + (fatigue) | 2026-10-02 02:55:24 | 34 | 34 | 32 | False | None |
| 109 | SemanticScholar | (ChatGPT) + (fatigue) | 2026-10-02 02:55:28 | 38 | 38 | 38 | False | None |
| 110 | SemanticScholar | ("large language model") + (fatigue) | 2026-10-02 02:55:33 | 69 | 69 | 65 | False | None |
| 111 | SemanticScholar | (LLM) + (fatigue) | 2026-10-02 02:55:45 | 60 | 60 | 55 | False | None |
| 112 | SemanticScholar | (chatbot) + (fatigue) | 2026-10-02 02:55:58 | 35 | 35 | 35 | False | None |
| 113 | SemanticScholar | ("machine learning") + (fatigue) | 2026-10-02 02:56:10 | 655 | 655 | 597 | False | None |
| 114 | SemanticScholar | (algorithm) + (fatigue) | 2026-10-02 02:56:24 | 787 | 787 | 732 | False | None |
| 115 | SemanticScholar | (algorithmic) + (fatigue) | 2026-10-02 02:56:30 | 787 | 787 | 732 | False | None |
| 116 | SemanticScholar | (automation) + (fatigue) | 2026-10-02 02:56:35 | 185 | 185 | 175 | False | None |
| 117 | SemanticScholar | (automated) + (fatigue) | 2026-10-02 02:56:40 | 364 | 364 | 333 | False | None |
| 118 | SemanticScholar | ("自動化") + (fatigue) | 2026-10-02 02:56:44 | 0 | 0 | 0 | False | None |
| 119 | SemanticScholar | ("人工知能") + (fatigue) | 2026-10-02 02:56:56 | 0 | 0 | 0 | False | None |
| 120 | SemanticScholar | ("生成AI") + (fatigue) | 2026-10-02 02:57:08 | 0 | 0 | 0 | False | None |
| 121 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (exhaustion) | 2026-10-02 02:57:12 | 327 | 327 | 308 | False | None |
| 122 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (burnout) | 2026-10-02 02:57:18 | 860 | 860 | 813 | False | None |
| 123 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (burn-out) | 2026-10-02 02:57:24 | 61 | 61 | 14 | False | None |
| 124 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (weariness) | 2026-10-02 02:57:28 | 27 | 27 | 21 | False | None |
| 125 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (tiredness) | 2026-10-02 02:57:40 | 100 | 100 | 45 | False | None |
| 126 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + (technostress) | 2026-10-02 02:57:45 | 182 | 182 | 179 | False | None |
| 127 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + ("疲労") | 2026-10-02 02:57:49 | 0 | 0 | 0 | False | None |
| 128 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + ("燃え尽き") | 2026-10-02 02:57:53 | 0 | 0 | 0 | False | None |
| 129 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + ("バーンアウト") | 2026-10-02 02:57:57 | 0 | 0 | 0 | False | None |
| 130 | SemanticScholar | ("artificial intelligence" \| AI \| "generative AI" \| ChatGPT \| "large language model" \| LLM \| chatbot \| "machine learning" \| algorithm \| algorithmic \| automation \| automated \| "自動化" \| "人工知能" \| "生成AI") + ("テクノストレス") | 2026-10-02 02:58:01 | 0 | 0 | 0 | False | None |
| 131 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot) AND fatigue AND (review OR "systematic review" OR "scoping review" OR "meta-analysis" OR "literature review" OR "umbrella review" OR "state of the art" OR "meta-synthesis") ; filter: title.search (a later re-run limited to titles) | 2026-10-02 03:50:02 | None | 0 | 0 | False | HTTP 429 |
| 132 | OpenAlex | ("artificial intelligence" OR AI OR "generative AI" OR ChatGPT OR "large language model" OR LLM OR chatbot) AND exhaustion AND (review OR "systematic review" OR "scoping review" OR "meta-analysis" OR "literature review" OR "umbrella review" OR "state of the art" OR "meta-synthesis") ; filter: title.search (a later re-run limited to titles) | 2026-10-02 03:53:34 | None | 0 | 0 | False | HTTP 429 |

## 15. One record added by hand

- One record (a conference short paper) was found by the researcher on 2026-10-01 in the AIS eLibrary while reading the 34 records of the base bibliography, and added to the candidates by hand. It was not found by a search.

## 16. Coverage search of this review

- **Purpose:** count eligible records that the source database does not hold (registration GSRR-21, GSRR-32, GSRR-39). It is not a search of the source database, and its records are never candidates for the main set. Sections 1 to 15 describe the source database; this section describes the only search this review runs.
- **Sources and interfaces:** OpenAlex API (filter `title_and_abstract.search`); Europe PMC REST API (field `TITLE_ABS`, which returns the same count as `TITLE` OR `ABSTRACT`: checked on 2026-10-18 with `fatigue`, 176,047 both ways, and with a word that does not exist, 0); ACM Digital Library web interface, ACM Guide to Computing Literature (fields `Title` OR `Abstract`), read page by page (50 records) by `acm_export.js` in the browser, after the site's own bot check had passed by itself. OpenAlex was queried with author 1's free API key, sent in a request header and not recorded (the search log says only whether a key was used); no key or contact address was sent to Europe PMC or the ACM Digital Library **[at registration: confirm]**.
- **Filters:** none. No date limit, no document-type limit, no language limit.
- **Date and time of the run:** **[at registration: per source, start and end, JST]**.
- **Counts reported by each source and records retrieved:** **[at registration]**. The merge stops if the records read differ from the count the source reported.
- **Export files:** kept outside the repository (they hold abstracts) and not released. Their names and SHA-256 are listed here **[at registration]**.
- **Merging and removal (GSRR-32):** **[at registration: records by source; after merging; matching the source database (the 34 exploratory records and the 264 additional candidates); new records]**.
- **Coverage sample (GSRR-39):** 300 new records drawn with Python `random.sample`, seed 20261022, from the IDs CS00001 onwards sorted alphabetically. The list of new records (ID, DOI, title, year, sources, and whether drawn) is attached **[at registration: file and SHA-256]**.
- **Tools:** `scripts/c_search.py` (export, merging, removal, draw; `selftest` checks the merging, the removal and the draw on made-up records) and `scripts/acm_export.js` **[at registration: SHA-256]**.
- **Check before the run (GSRR-26):** on 2026-10-18 the OpenAlex query, restricted to 2022-11-30 onwards and to articles, reviews and preprints, retrieved all 11 included exploratory records (11 of 11 are in OpenAlex). These records shaped the terms, so the check is optimistic. Counts the same day, for planning only: OpenAlex 6,526 (with those restrictions); Europe PMC 1,455 (no restriction); ACM Digital Library 702 (no restriction).

### Query strings (verbatim)

| Source | Query string |
|---|---|
| OpenAlex | (fatigue OR exhaustion OR exhausted OR burnout OR "burn-out" OR depletion OR depleted OR tiredness OR weariness) AND ("artificial intelligence" OR "generative AI" OR GenAI OR ChatGPT OR "large language model" OR "large language models" OR LLM OR chatbot OR "AI tool" OR "AI tools" OR "AI assistant" OR "AI-assisted" OR "AI use") NOT ("fatigue life" OR "fatigue crack" OR "fatigue strength" OR "fatigue damage" OR "driver fatigue" OR "driver drowsiness" OR "fatigue detection" OR "muscle fatigue" OR battery OR alloy OR welded) |
| Europe PMC | (TITLE_ABS:fatigue OR TITLE_ABS:exhaustion OR TITLE_ABS:exhausted OR TITLE_ABS:burnout OR TITLE_ABS:"burn-out" OR TITLE_ABS:depletion OR TITLE_ABS:depleted OR TITLE_ABS:tiredness OR TITLE_ABS:weariness) AND (TITLE_ABS:"artificial intelligence" OR TITLE_ABS:"generative AI" OR TITLE_ABS:GenAI OR TITLE_ABS:ChatGPT OR TITLE_ABS:"large language model" OR TITLE_ABS:"large language models" OR TITLE_ABS:LLM OR TITLE_ABS:chatbot OR TITLE_ABS:"AI tool" OR TITLE_ABS:"AI tools" OR TITLE_ABS:"AI assistant" OR TITLE_ABS:"AI-assisted" OR TITLE_ABS:"AI use") NOT (TITLE_ABS:"fatigue life" OR TITLE_ABS:"fatigue crack" OR TITLE_ABS:"fatigue strength" OR TITLE_ABS:"fatigue damage" OR TITLE_ABS:"driver fatigue" OR TITLE_ABS:"driver drowsiness" OR TITLE_ABS:"fatigue detection" OR TITLE_ABS:"muscle fatigue" OR TITLE_ABS:battery OR TITLE_ABS:alloy OR TITLE_ABS:welded) |
| ACM Digital Library | (Title:(fatigue OR exhaustion OR exhausted OR burnout OR "burn-out" OR depletion OR depleted OR tiredness OR weariness) OR Abstract:(fatigue OR exhaustion OR exhausted OR burnout OR "burn-out" OR depletion OR depleted OR tiredness OR weariness)) AND (Title:("artificial intelligence" OR "generative AI" OR GenAI OR ChatGPT OR "large language model" OR "large language models" OR LLM OR chatbot OR "AI tool" OR "AI tools" OR "AI assistant" OR "AI-assisted" OR "AI use") OR Abstract:("artificial intelligence" OR "generative AI" OR GenAI OR ChatGPT OR "large language model" OR "large language models" OR LLM OR chatbot OR "AI tool" OR "AI tools" OR "AI assistant" OR "AI-assisted" OR "AI use")) NOT (Title:("fatigue life" OR "fatigue crack" OR "fatigue strength" OR "fatigue damage" OR "driver fatigue" OR "driver drowsiness" OR "fatigue detection" OR "muscle fatigue" OR battery OR alloy OR welded) OR Abstract:("fatigue life" OR "fatigue crack" OR "fatigue strength" OR "fatigue damage" OR "driver fatigue" OR "driver drowsiness" OR "fatigue detection" OR "muscle fatigue" OR battery OR alloy OR welded)) |
