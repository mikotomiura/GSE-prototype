# 差分（登録版 0.10〈コミット 7838b0ec〉→ 0.11〈コミット 1139499c〉・word-diff）

[-…-] は消した文、{+…+} は足した文。

diff --git a/.steering/20261017-ai-fatigue-c-outline/registration-en.md b/.steering/20261017-ai-fatigue-c-outline/registration-en.md
index d67898a1..5787becd 100644
--- a/.steering/20261017-ai-fatigue-c-outline/registration-en.md
+++ b/.steering/20261017-ai-fatigue-c-outline/registration-en.md
@@ -1,6 +1,6 @@
# TRACE: How studies of "AI fatigue" tie fatigue to AI, measure it and report it. Protocol for a registered methodological review

Registration draft [-0.10-]{+0.11+} (2026-10-17). Not yet registered. Form: Generalized Systematic Review Registration (GSRR; van den Akker et al., 2023). Each GSRR item is answered under its own number. Fields to be filled at registration are marked **[at registration]**.

---

@@ -11,9 +11,8 @@ Registration draft 0.10 (2026-10-17). Not yet registered. Form: Generalized Syst
TRACE is the name of this review's coding scheme (GSRR-43); it is not an acronym and not the name of a measure of fatigue. It links three things in each study: how fatigue is tied to AI (C1), what the fatigue items ask about (C2), and what the report states and concludes (C3 to C7: what is measured on the AI side, whether reporting is complete and internally consistent, whether samples overlap, and whether the title and the main conclusion pass three checks against the design, the level of attribution and the name of the main instrument). These checks compare designs, attribution levels and names; they are not validity evidence.

**[GSRR-2] Contributors.** Two authors.
- Author 1 (first author): Mikoto Miura, Independent Researcher. ORCID: https://orcid.org/0009-0000-4196-0508. [-Lead-]{+Lead, screener+} and [-coder 1.-]{+the only coder.+}
- Author 2 (co-author): **[at registration: name, affiliation, ORCID]**. [---]{+Screener in sensitivity analysis 5 (GSRR-62) and reader of the manuscript.+} Author 2 [-is coder 2 by default (see GSRR-44).-]{+does not code.+}
- Both authors built the source literature database.

**[GSRR-3] Subjects.** Human–AI interaction; occupational and educational psychology; psychometrics; meta-research.
@@ -23,11 +22,14 @@ TRACE is the name of this review's coding scheme (GSRR-43); it is not an acronym
| Task | Who |
|---|---|
| Research questions and coding rules | Author 1 |
| Eligibility screening {+of the 34 exploratory records+} in the source database | Authors 1 and [-2 (see GSRR-33)-]{+2, before registration (GSRR-37)+} |
| [-Coding (C1–C7)-]{+Eligibility screening of the additional candidates (main set)+} | [-Coder-]{+Author+} 1 and [-coder 2, independently-]{+the AI screener, independently; author 1 decides where they differ (GSRR-33)+} |
| [-Reconciliation-]{+Second screening after the manuscript draft+} | [-Coders-]{+Authors+} 1 and 2 {+(sensitivity analysis 5, GSRR-62) |+}
{+| Coding (C1–C7) | Author 1, twice, at least four weeks apart (GSRR-44) |+}
{+| Reconciliation of the two passes | Author 1+} (GSRR-48) |
| AI {+screener (Claude Opus, Anthropic) | Judges eligibility and centre under fixed instructions (attachment 6). It is a screener, not a coder |+}
{+| AI+} assistant (Claude, Anthropic) | Drafts values for C4f and C5 only. [-Both coders make their own-]{+In each pass, author 1 makes the+} recalculations or [-record their own-]{+records the+} signs before opening a draft, and then [-check-]{+checks+} every drafted value (GSRR-44). The assistant is not a coder |
| Tables and the check of every number in them | Author 1 [-builds; author 2-]{+builds the tables by script and+} checks {+every number in the manuscript+} against the [-code table-]{+script output+} |
| Registration | Author 1 |

## Type, stages and dates
@@ -41,12 +43,13 @@ TRACE is the name of this review's coding scheme (GSRR-43); it is not an acronym
**[GSRR-6] Review stages.**
1. Exploration. Done before registration (GSRR-10).
2. Registration of this protocol and its codebook (version 2).
3. [-**Closing-]{+**Screening of the additional candidates** by author 1 and the AI screener (GSRR-33), and **closing+} the main set on 2026-12-31** (GSRR-39).
4. **Calibration [-coding.** Five records are drawn at random from the closed candidate pool, or from-]{+coding** on+} the exploration [-set if the pool is small (GSRR-39). They-]{+set, in parallel with stage 3: author 1 codes all its primary studies twice, in November and December 2026, at least four weeks apart (GSRR-44). These codes+} are used only to refine definitions and are [-excluded from all main-set counts.-]{+not data.+} Any change is registered as an amendment before stage 5 begins. {+No main-set record is used for calibration.+}
5. **Main coding.**
   - [-The-]{+Author 1 codes the+} main set [-is coded by two coders, independently.-]{+twice, at least four weeks apart.+}
   - The exploration set is [-re-coded-]{+coded again+} under the [-same-]{+final+} rules, also [-by two coders independently.-]{+twice.+} Its results go in a separate [-table.-]{+table, flagged as calibration material.+}
6. Reconciliation, synthesis and reporting.
{+7. **Second screening after the manuscript draft** by authors 1 and 2, reported as sensitivity analysis 5 (GSRR-62).+}

**[GSRR-7] Current review stage.** Stage 2. No record of the main set has been coded. The main set is not closed.

@@ -68,7 +71,7 @@ The third point was checked in 16 searches of free sources (Europe PMC, OpenAlex

*Prior work by the same authors.* Our critical narrative review (unpublished draft, 2026; both authors of this review are its authors) described such problems qualitatively. It covered 11 reports drawn from a 34-record exploratory bibliography: the 10 primary studies in our exploration set and one report whose full text was unavailable. It was not preregistered.

*What this review does.* It describes, under rules fixed in advance (amendments after calibration are registered before main coding, GSRR-6), how studies of AI-related fatigue tie fatigue to AI, what their fatigue items ask about, and whether what their reports state and conclude stays within what they measured. For the problem types of GSRR-57 it reports whether each is present in the main set; these state whether a problem type is present or absent in the set, not how often it occurs, and they do not test whether the observations of the narrative review are reproduced. The observations of the narrative review are set beside them; the words "confirm", "replicate" and "replication" are not used about them. The primary counts come from records that were not used to build the rules. [-Before registration, author 1 had read the full text of none of them, and author 2's full-text reading-]{+Their eligibility+} is [-recorded at registration **[at registration]**. Both authors screen their full texts-]{+decided+} after registration (GSRR-33).

*How the issues noted during exploration map to the codes.* The table maps the seven issues noted during exploration (below) to the codes. "Problem type" means the code has values that GSRR-57 reports as observed or not observed. The other codes are described.

@@ -95,6 +98,7 @@ The third point was checked in 16 searches of free sources (Europe PMC, OpenAlex
- **2026-10-16.** The narrative review draft was revised.
- **2026-10-17.** The item coding of 2026-10-15 was corrected after an internal review, and codebook version 2 was written. Version 2 was therefore written after the exploration results were seen.
- **2026-10-17.** The source database's final decisions on the 34 records were set: 10 primary studies included, 3 pending for unavailable full text, 21 excluded. These 10 studies and the four instruments form the exploration set (GSRR-39).
{+- **2026-10-17.** The instructions for the AI screener (attachment 6) were written from the source database's criteria and then applied to the 34 exploratory records, in two rounds; one question was clarified between the rounds (GSRR-37). The AI screener has not judged any additional candidate. A database of the 264 additional candidates (bibliographic data, abstracts and free full texts, with no judgements) was built for screening.+}

**[GSRR-11] Primary research questions.** All primary answers come from the main set. They are descriptive (GSRR-57).
- **RQ1 (attribution).** At which level do studies tie their main fatigue instrument to AI? (C1)
@@ -109,7 +113,7 @@ The third point was checked in 16 searches of free sources (Europe PMC, OpenAlex
- **RQ5 (title versus content).** Do titles and abstracts match the name of the main instrument, the design and the level of attribution? (C6)

**[GSRR-12] Secondary research questions.**
- **SQ1.** How are the answers to RQ2–RQ5 and SQ2 distributed within each of the source database's two eligibility [-groups?-]{+groups (assigned at screening, GSRR-33)?+} The tables of the two groups stand side by side; no statement says that a value is larger, smaller, more or less common in one group than in the other.
  - Centre-A: fatigue attributed to AI in its definition, measurement or analysis.
  - Centre-B: a general fatigue construct examined in relation to AI use.
  - RQ1 is not tabulated by these groups, because the grouping is defined by attribution and the tables would be circular. For the same reason, SQ1 leaves out C6c and reports C7 conditions (i) and (iii) only.
@@ -129,14 +133,14 @@ The third point was checked in 16 searches of free sources (Europe PMC, OpenAlex

## Software, funding, conflicts

**[GSRR-17] Software.** Python (version recorded) for the screening order, the [-calibration draws,-]{+screening database,+} the derived values, counting and agreement statistics. Spreadsheets for {+screening and+} coding forms. The {+AI screener is Claude Opus (Anthropic), run as subagents of Claude Code; the model identifier and the dates of use are recorded. The+} scripts will be released (GSRR-64).

**[GSRR-18] Funding.** None.

**[GSRR-19] Conflicts of interest.** No financial conflicts. Non-financial conflicts:
- Both authors built the source literature database.
- Both authors wrote the earlier narrative review of the exploration records. Their view of what counts as a problem is therefore shaped by that work.
- Neither author is an author of any primary study to be coded. If [-a coder-]{+author 1+} turns out to be one,[-that coder does not code that study. The other coder's codes are used, and-] the [-record-]{+study+} is {+coded and+} flagged [-as single-coded.-]{+in every table.+}

**[GSRR-20] Overlapping authorships.** As in GSRR-19. The narrative review will be cited.

@@ -173,24 +177,27 @@ No paid databases were used.
**[GSRR-31] Search strategy justification.** The review asks about measurement and reporting practice in an already assembled body of studies. It does not estimate an effect, so a new exhaustive search is not needed. The limits are stated in GSRR-65.

**[GSRR-32] Miscellaneous search strategy details.**
- The source database collected 225 records, which became 220 after merging versions, plus one record added by hand. These 221 are the additional candidates. On 2026-10-17, author 1 had screened 79 of them: 71 at title and abstract [-level-]{+level,+} and 8[-(all review-type records, none included)-] at full-text [-level.-]{+level (4 excluded, 4 pending; none included). These earlier judgements are not used: all 264 additional candidates are screened again after registration (GSRR-33).+}
- The review-aimed search produced a list of 46 records, separate from the 221. Three of them are also in the 34-record bibliography or the 221. The other 43 were unscreened on 2026-10-17. In this protocol, "additional candidates" means the 221 and these 43 (264 records).
- A planned systematic search for the source database has not been run. If it runs, its new records are candidates on the same terms: those with [-both-]{+a+} final [-decisions-]{+decision+} by 2026-12-31 enter the main set, later ones the late stratum (GSRR-39).
- The three exploratory records pending for unavailable full text join the exploration set if their full texts are obtained and they are included. They are never part of the main set.

## Screening (eligibility)

**[GSRR-33] Screening stages.** [-The-]{+For the 34 exploratory records, the+} source [-database screens titles and abstracts, then full texts. Two-]{+database's two+} screeners (authors 1 and 2) [-screen independently,-]{+screened independently+} and [-disagreements are reconciled. This-]{+reconciled their disagreements; this+} review takes [-the-]{+those+} final decisions. {+The additional candidates are screened after registration by two independent screeners: author 1 and an AI screener (Claude Opus, Anthropic). There are three stages: title and abstract; full text; and centre (centre-A, centre-B or boundary, for records included at full text).+}
{+- **Each stage.** Author 1 and the AI screener judge every record independently. Author 1 does not see the AI screener's judgement of a record at a stage before recording their own judgement of it at that stage. Where the two differ, author 1 decides at that stage, after reading the AI screener's answers and the passages it cites (GSRR-38). Records that both screeners exclude at a stage are excluded; records that both include go on to the next stage.+}
{+- **The AI screener.** It follows fixed instructions (attachment 6). They turn the source database's criteria (GSRR-24, GSRR-35) into seven questions, each answered `yes`, `no` or `unclear` with the place in the input that supports the answer, and fixed rules that turn the answers into a decision and an exclusion code. At the title and abstract stage, a record is included when in doubt. Each record is judged on its own, in a separate call per batch of at most nine records. The AI screener sees only the instructions and the record's title and abstract (first stage) or full text (later stages).+} It does not [-re-screen.-]{+see the source database's classification, author 1's judgements or any earlier AI appraisal. Its output is stored with its SHA-256 before author 1 opens it.+}
{+- **Full texts.** Both screeners use the same full text: only versions that are publicly and freely available. They are retrieved by script (open-access locations listed by OpenAlex, Europe PMC and Semantic Scholar), then by author 1 in a web browser; author 1 passes any bot check and saves PDFs that the browser only displays. A full text from Europe PMC may be its full-text XML, which is the publisher's text extracted by machine. No full text is retyped or rewritten. If no free full text is found, the record is pending with E6 (GSRR-35).+}
- **After registration**, [-the screeners know-]{+author 1 knows+} these coding rules. To limit the effect of that knowledge:
  - the remaining candidates are all {+264+} additional [-candidates without a final decision by both screeners on the registration date, whatever their screening stage (including-]{+candidates, including+} the [-71 screened by-]{+79 that+} author 1 [-at title and abstract level-]{+screened before registration (GSRR-32)+} and the 43 review-search [-records);-]{+records; the earlier judgements are not shown to author 1 during screening;+}
  - they are screened in a fixed order: within each population group the record IDs, sorted alphabetically, are shuffled with Python `random.shuffle`, using a generator freshly seeded with 20261018 for each group; the groups are then interleaved, one record from each group in the order listed in GSRR-16, so that progress by 2026-12-31 does not depend on the group;
  - records with no population group in the source database are placed in the group unknown. Before registration, 51 of the 264 additional candidates had none: the 43 review-search records, seven records that the source database's machine classification labels review-type, and one record added by hand. To see why, an AI assistant read their titles and abstracts twice, in two independent readings with fixed definitions, only for document type and population group, not for eligibility: both readings found 50 to be documents without participants (reviews, study or review protocols, commentaries and a correction notice); the readings differed on the remaining record, which has no abstract, and its document type was left undetermined. No human read the abstracts of the 43 review-search records for this purpose;
  - the resulting order list and its SHA-256 are attached to the registration, with the Python version used **[at registration]**;
  - no coding is done during screening;
  - every screening decision made after registration is released with its date, [-each-]{+author 1's judgement, the AI+} screener's judgement and the exclusion code (GSRR-41);
  - exclusions for E2 and E3 are counted by population group, and the candidates still unscreened on 2026-12-31 are counted by population group.

**[GSRR-34] Screened fields / blinding.** Author 1 [-read AI-generated preliminary-]{+screens from a database that contains the bibliographic data, the abstract and the free full text of each record and no judgement: neither the AI screener's, nor author 1's earlier ones, nor the AI+} appraisals {+author 1 read+} before [-judging. Author 2 did not.-]{+2026-10-17.+} Before registration, author 1 had screened [-71-]{+79+} additional candidates[-at title-] and [-abstract level, and 8 at full-text level, all 8 of which were excluded (GSRR-32). Author 2's prior full-text reading-]{+read AI-generated preliminary appraisals before judging (GSRR-32); author 1 may remember them (GSRR-65). The AI screener+} is [-recorded at registration **[at registration]**.-]{+blind to all judgements (GSRR-33).+}

**[GSRR-35] Used exclusion criteria.**
- E1: AI only as a fatigue-detection tool.
@@ -203,28 +210,29 @@ No paid databases were used.

E5 records are not coded. They stay linked to their group for C5 (GSRR-43). Each E5 group has exactly one coded record, whose C5 value is "linked by the source database as the same sample"; no other coded record has that value. An uncoded E5 record is counted in the RQ4 record counts with the set and population group of its group's coded record.

**[GSRR-36] Screener instructions.** [-The-]{+Author 1: the+} source database's {+criteria in the+} screening [-sheet.-]{+database (attachment 6 gives the same criteria as questions). The AI screener: the instructions of attachment 6, with their SHA-256.+}

**[GSRR-37] Screening reliability.**
[-Reported by the source database.-]{+- *Exploratory records.*+} The {+source database's two screeners agreed on 32 of the+} 34 exploratory records[-had 32/34 agreement between screeners-] on three categories. That is exploration material.
{+- *AI screener, checked before registration.* The pass lines were set before the AI screener was applied: at the title and abstract stage, none of the 13 records that the two human screeners finally included or left pending is excluded; at the full-text stage and the centre stage, Cohen's kappa of at least 0.6 against the human final decisions. If a line was missed, the instructions could be revised once and applied again; if it was still missed, the AI screener's judgements would be advisory only and author 1 would decide every record. The instructions were written from the source database's criteria without looking at the human decisions, but those criteria were themselves refined on these 34 records, so the accuracy may be optimistic. Round 1 met all three lines (title and abstract: 13 of 13 passed on, 19 of 21 exclusions also excluded; full text: 33 of 34 agreed, kappa 0.945; centre: 10 of 10 agreed). One question (whether fatigue is measured) was then clarified for the title and abstract stage, because the AI screener had excluded records whose abstracts listed measures without fatigue; the registered instructions are the clarified version. Round 2, with the registered instructions, also met all three lines (title and abstract: 13 of 13 passed on, 16 of 21 exclusions also excluded; full text: 32 of 34 agreed, kappa 0.893; centre: 10 of 10 agreed). The two records on which round 2 differed from the human decision are reported with attachment 6.+}
{+- *Additional candidates.* For each stage, the agreement between author 1 and the AI screener before reconciliation is reported as percentage agreement and Cohen's kappa, with the number of records each screener sent on.+}

**[GSRR-38] Screening reconciliation procedure.** [-Discussion between-]{+Author 1 decides every record on which author 1 and+} the [-screeners.-]{+AI screener differ, at the stage where they differ, after reading the AI screener's answers and cited passages.+} Both judgements before reconciliation are [-kept.-]{+kept and released (GSRR-41). The main set therefore rests on one human screener and an AI screener, not on two human screeners; sensitivity analysis 5 (GSRR-62) repeats the full-text screening with two human screeners after the manuscript draft.+}

**[GSRR-39] Sampling and sample size.**
- **Exploration set.** The 10 primary studies the source database included from the 34-record bibliography, and the four item-coded instruments. [-Coded-]{+Used for calibration and coded+} again after [-registration-]{+calibration+} (GSRR-6). {+Its tables are flagged as calibration material.+}
- **Main set.** Primary studies among the additional candidates [-for which both screeners'-]{+whose+} final[-inclusion-] decision [-was-]{+after reconciliation (GSRR-38) is to include,+} recorded[-in the source database-] on or before 2026-12-31. Excluded from it:
  - the exploration records, even if found again;
  - records [-still screened by one screener only, or by AI only,-]{+without a final full-text decision+} on that [-date;-]
[-  - the calibration records.-]{+date.+}
- **Late stratum.** Studies included after 2026-12-31 and before stage 5 begins are reported as a separate stratum, outside the primary counts. They are coded {+twice+} by [-both coders-]{+author 1+} under the same rules. Studies included after stage 5 begins are listed but not coded.
- [-**Candidate pool and calibration sample.** The candidate pool is the main set as closed on 2026-12-31, before calibration records are removed.-]{+**Calibration.**+} Calibration[-records are drawn with Python `random.sample` from the pool's record IDs, sorted alphabetically. The first round uses seed 20261017. Round k (k = 2, 3)-] uses [-seed 20261017 + k − 1 and draws from the IDs not yet drawn.-]
[-- **Small pool.** If the pool has 24-]{+all primary+} studies[-or fewer (fewer than the 15 that calibration can remove plus the minimum-] of[-10), calibration is done on exploration-set records instead, and no main-set record is removed. Exploration records are drawn by the same procedure from-] the {+exploration set (GSRR-44). No+} record[-IDs-] of the [-primary studies in the exploration-]{+main+} set[-on 2026-12-31, not from instruments (seed 20261019 + k − 1), at most two rounds (10 records). If every exploration study-] is used for[-calibration, the whole exploration table is flagged as calibration material. If agreement is still below 80%, the procedure in GSRR-44 step 2 for low agreement applies. Exploration records used for-] calibration [-are flagged and reported separately within the exploration table.-]{+or removed from it.+}
- **Minimum size.** The minimum is counted[-after calibration records are removed,-] in coded records, not instruments; E5-linked records are not coded (GSRR-35), so each coded record is one study. It applies to every table on its own: a table (a set, a population group or a centre) based on fewer than 10 studies reports counts only, without proportions. The 10-study rule does not apply to the proportions of item types within one instrument, which follow the C2b rule. For C2b, if fewer than 3 instruments with available items are first seen in the main set, each instrument's counts are still given, without proportions. The number of "items unavailable" instruments is always shown next to the C2b tables.

**[GSRR-40] Screening procedure justification.** [-Coding is-]{+The source database had a second human screener only for+} the [-costly part-]{+34 exploratory records. A second human screening+} of [-this review. Re-screening-]{+the 264 additional candidates before coding+} would [-repeat-]{+fall on+} the [-source database's two-screener process.-]{+co-author, whose time is limited. An AI screener, checked against the human decisions on the 34 records before registration, is used as the independent second screener instead, and the two-human screening is done after the manuscript draft and reported as a sensitivity analysis (GSRR-62).+}

**[GSRR-41] Data management and sharing.** The list of record IDs, with [-each-]{+author 1's judgement and the AI+} screener's [-judgement,-]{+judgement at each stage,+} the final[-eligibility-] decision, the exclusion code and the decision date, will be released with the code table (GSRR-50). {+The AI screener's outputs are released with their quotations, which are limited to 25 words each; no abstract or full text is released.+}

**[GSRR-42] Miscellaneous screening details.** On 2026-10-17, the screening of the additional candidates had stopped part-way through a list ordered by population group. Some groups, such as health professionals, had no human screening yet. [-Every-]{+All 264 records are screened again in the fixed order (GSRR-33), and every+} result table[-therefore-] shows counts by population group.[-The screening order after registration is fixed (GSRR-33).-]

## Extraction (coding)

@@ -238,7 +246,7 @@ General rules:
  - C2 is coded per fatigue instrument within a record.
  - C2b is coded per item.
- **Fatigue instrument.** C1, C2 and C6a refer to the study's fatigue instrument(s), not to instruments for the AI-side variable.
- **Set of an instrument version.** A version belongs to the first set, in the order exploration, main, late, in which a record uses it. Its items take the same set. "First seen in the main set" means this set is the main set.[-A version used only by calibration records belongs to no set and is not reported in the set tables.-]
- **Instrument.** The set of items actually administered in the study, for example a subscale only when only the subscale was used. An instrument version is identified by its item wording together with its language. Items are coded as printed in the report, including translations, and the language is recorded. If the report gives no items but states that an existing scale was used without modification, the items are taken from the cited source and flagged (`item_source` = source). For such an instrument, C2a origin is the existing scale's name or "existing general scale, wording not verifiable", and each kind of modification is "not verifiable", because a comparison with the source would compare the source with itself. Otherwise the instrument is coded "items unavailable". The C2b denominator is the number of coded items: the printed items, or the items taken from the cited source. The instrument's full item count is shown next to it.
- **Main instrument.** The fatigue instrument whose variable is named first in the abstract's results. If the abstract has no results, it is the instrument described first in the methods.
- **Main relation.** The first relation between an AI-side variable and fatigue reported in the abstract's results.
@@ -254,17 +262,17 @@ General rules:
| C3 | AI-side variable instrument (all that apply; each value is counted once per record) | amount of use / dependence or addiction type (source scale) / attitude or acceptance / other / none |
| C4 | Reporting completeness and internal consistency (values per rule) | (a) N in the text vs. table denominators: consistent / inconsistent (which) / no comparison possible (N given in only one place). (b) Direction of the main relation in the abstract, results and discussion: consistent / inconsistent (where) / not applicable. (c) Discriminant validity: the report's own stated criterion vs. its reported values: consistent / inconsistent / no criterion stated / not applicable. We bring in no thresholds of our own. (d) Ethics statements within the report (approval present, approving body): consistent / inconsistent / not reported. (e) Qualitative coding, in two columns: codebook available (yes / no) and agreement (value given / index named only / none); both not applicable for quantitative studies. (f) Recalculation: see the rules below this table |
| C5 | Sample overlap | Category: linked by the source database as the same sample (E5 group) / signs present but not confirmed / no signs. Signs, each recorded: shared authors, region, survey site, grant number, identical N. We do not decide sameness ourselves |
| C6 | Title and abstract versus content | (a) Construct term in the title vs. the name of the main instrument. Term families: {fatigue, tiredness, 疲労, 疲れ}; {exhaustion, depletion, 消耗, 枯渇}; {burnout, バーンアウト, 燃え尽き}. A construct term is any word of these families, including inflected forms and compounds (tired, fatigued, exhausted, techno-exhaustion). Values: same family (at least one family shared, so a name with two families matches either) / different family / instrument name has no family term / instrument unnamed / not verifiable / no construct term in the title. This is a name check only. The item content of the main instrument (its C2b type composition) is reported next to it and is not turned into a match or mismatch. (b) Causal wording vs. design: see the rules below this table. (c) AI-fatigue term in the title vs. attribution. [-Coders record-]{+The coder records+} whether the title uses an AI-fatigue term (the list in C7 (ii)): yes / no. C6c is then derived by script: "no AI-fatigue term in the title" if no, whatever the main instrument; "AI-fatigue term with L3–L6" if yes and the main instrument's C1 representative value is L3, L4, L5 or L6; "AI-fatigue term with L1a–L2" if yes and the value is L1a, L1b or L2; "cannot decide" if yes and the main instrument cannot be identified or its C1 value is not verifiable |
| C7 | Does the main conclusion meet any of three conditions (design, attribution level, names)? | The main conclusion is the first sentence of the abstract's conclusion section. If there is none, it is the last sentence of the abstract. It is copied verbatim. "Beyond what was measured" if any of these holds. (i) C6b is a mismatch. (ii) The conclusion uses an AI-fatigue term ("AI fatigue", "AI-induced fatigue", "AI-related fatigue", "GenAI fatigue", or the Japanese equivalent) while the main instrument's C1 representative value is L3, L4, L5 or L6. (iii) The construct term in the conclusion is in a different term family from the name of the main instrument, by the C6a rules. (iii) is "no term to compare" if the conclusion has no construct term or the instrument name has no family term, and "not verifiable" if the instrument name is not verifiable; "not verifiable" is checked before "no term to compare". (i) is "not verifiable" if C6b is. Otherwise "within what was measured". "Within what was measured" means only that none of (i)–(iii) holds; it does not mean that the item content of the instrument supports the conclusion. Each condition is also recorded on its own as met / not met (and not verifiable; for (iii), also no term to compare), and each is a separate problem type (GSRR-57); the summary value is reported only in the per-study table, and is "not verifiable" if no condition is met and one is not verifiable. "Cannot decide" is checked first: if the conclusion cannot be identified, all three conditions are "cannot decide"; if only the main instrument cannot be identified, (i) is still derived and (ii) and (iii) are "cannot decide". [-Coders code-]{+The coder codes+} only the conclusion sentence and its construct term; C7 is then derived by script from the reconciled codes. If any input is "unresolved", the summary value of C7 is "unresolved"; a condition is "unresolved" only if one of its own inputs is |

**C4f recalculation rules.**
- **What is recalculated.**
  - p-values from reported test statistics and degrees of freedom (t, F, r, χ², z). A z is recalculated only when the report gives it, including a column labelled z or critical ratio in a table of estimates; [-coders do-]{+the coder does+} not form z from an estimate and its standard error. Tests are two-tailed unless the report says otherwise. A p-value that the report says is adjusted for multiple testing is not counted. A p-value reported as an inequality (for example, p < .001) is consistent if the recalculated value satisfies it. A p-value printed as p = .000 is read as p < .001, and "ns" or "n.s." as p ≥ .05 (or p ≥ the α the report states). A test statistic reported with neither a p-value nor a significance marker is not recalculated. An inconsistency that changes the conclusion at α = .05 is also counted separately as a gross inconsistency.
  - Values in tables are included. Degrees of freedom given in a table note are used; degrees of freedom that would have to be inferred from the sample size are not, and the result is "cannot be calculated". A p-value shown only by asterisks is treated as an inequality at the threshold stated in the table note; without a stated threshold it is "cannot be calculated". "Cannot be calculated" stays in the denominator (GSRR-53). A test reported in both the text and a table is counted once, from the text. Each result records whether it came from the text or a table.
  - Percentages from counts and denominators.
  - An indirect effect as a×b, only for a single-mediator path where a, b and the indirect effect are reported at the same level of standardization.
- **Who recalculates.** [-Both coders recalculate independently.-]{+Author 1 recalculates in each of the two coding passes, independently of the other pass.+} The AI draft is generated by author 1 and stored unopened, with its SHA-256 recorded. It is opened only after {+the values of+} both [-coders have fixed their values,-]{+passes are fixed,+} and is then used only as a cross-check; its agreement with the human values is reported. Data are the reconciled human values.
- These rules follow the logic of statcheck (Nuijten et al., 2016), which recalculates p from t, F, r, χ² and Z with their degrees of freedom, with four differences: the [-coders judge-]{+coder judges+} each test rather than scanning the whole text, so a test is one-tailed only if the report says one-tailed, one-sided or directional for that test; values printed in tables are included; p-values that the report says are adjusted for multiple testing are not counted; and percentages and indirect effects are added. The procedure is carried out by people, not by statcheck.
- **Tolerance.** A value is consistent if it falls within the range implied by rounding the inputs to their reported decimals.
- **Unit.** Each recalculated result. Each record is then summarised by the first value that applies: any inconsistency (at least one inconsistent result); none (at least one consistent result and no inconsistent one); cannot be calculated (results to recalculate, none of which could be calculated); not applicable (no result to recalculate). The gross-inconsistency summary uses the same order: any gross inconsistency (at least one grossly inconsistent result); none (at least one calculated result and no grossly inconsistent one); cannot be calculated; not applicable. Because results cluster in records, the number of recalculated results per record and the number of consistent, inconsistent and grossly inconsistent results are also reported (GSRR-56).

@@ -286,46 +294,43 @@ General rules:
- **Mismatch:** causal wording in a study whose design has no manipulation.
- **Match:** any other design, or "no causal wording".

**[GSRR-44] Extraction stages.** {+This is a single-coder review: author 1 codes every record twice, at least four weeks apart, and the second pass is made without looking at the first. The agreement reported is agreement between two passes of one coder, not between coders, and no claim of independent coding is made.+}
1. **Worked examples.** Before calibration, [-both coders try-]{+author 1 tries+} the definitions on worked examples that include multiple instruments, a qualitative study and missing values.
2. **Calibration** (GSRR-39). [-It ends when percentage agreement is-]{+Author 1 codes all primary studies of the exploration set twice: the first pass in November 2026 and the second in December 2026,+} at least [-80%-]{+four weeks later. Agreement between the two passes is computed+} on each of these units: each C1 level; C2a, C2c and C2d per instrument; C2b primary type, boundary and target per item; C3, C4 (a)–(d), each column of C4 (e), C5, C6a, C6b and the C6c title input per record; the C4f judgement of each result {+recalculated in+} both [-coders recalculated;-]{+passes;+} the conclusion sentence, whether the conclusion and the main instrument could be identified, whether the conclusion uses an AI-fatigue term, and the construct-term family of the conclusion. [-Derived values and the agreement with the AI draft are not stopping criteria. Otherwise, five more records are drawn (GSRR-39) and also excluded from the counts, up to two further rounds. If agreement is still-]{+For every unit+} below [-80%,-]{+80% percentage agreement,+} the definitions are [-amended,-]{+amended and+} the amendment is [-registered, and-]{+registered before main coding;+} the low agreement is reported. {+Derived values and the agreement with the AI draft are not criteria.+} Kappa is reported alongside percentage agreement but is not a[-stopping-] criterion, because rare categories make it unstable in [-five records.-]{+10 studies. Calibration codes are not data.+}
3. **Main coding.** [-Both coders code-]{+Author 1 codes+} all records of the main [-set-]{+set, the late stratum+} and the exploration set [-independently.-]{+twice under the final codebook, at least four weeks apart.+}
4. **Use of exploration codes for instruments.** If a main-set study uses an instrument already coded in the exploration set, its C2b values come from the[-re-coded-] exploration values [-(the-]{+of the+} main coding [-under-]{+(under+} the final codebook, not the calibration codes), but only if the item wording is verbatim identical. Otherwise the instrument is coded as a new version.
5. **AI drafts** are allowed only for C4f and C5.
   - For C4f, [-both coders recompute-]{+author 1 recomputes+} every value {+in both passes+} before seeing the draft (GSRR-43), and the agreement between human and AI values is reported.
   - For C5, the AI bibliographic matches are generated by author 1 and stored unopened, with their SHA-256 recorded. [-Each coder-]{+In each pass, author 1+} first records the signs of overlap from the reports;[-only then does the coder open-] the matches {+are opened only after both passes have recorded the signs,+} and[-check-] every [-one of them.-]

[-**If coder 2 is unavailable.** Author 2 is coder 2 by default. If author 2 cannot code, a third person who did not write the rules is sought. If no such person-]{+match+} is[-available, author 1 codes twice, at least four weeks apart. The results are-] then [-labelled as single-coder results, and no claim of independent coding is made.-]{+checked.+}

**[GSRR-45] Extractor instructions.** This protocol, the C2b codebook (version 2) and a coding form with the definitions above.

**[GSRR-46] Extractor blinding.** [-Coders know-]{+Author 1 knows+} the research [-questions. Neither coder sees-]{+questions and+} the {+rules. The second pass is made without looking at the first. The+} C4f AI draft [-until both have fixed their values (GSRR-43). The-]{+and the+} C5 bibliographic matches are opened only after [-each coder has recorded the signs (GSRR-44). Coder 2 does not see coder 1's codes or the-]{+both passes are fixed (GSRR-43, GSRR-44). The+} version-1 codebook values [-until coder 2 has finished. Both default coders-]{+are not consulted. Author 1+} wrote the earlier narrative review, so [-they share a-]{+the codes carry author 1's+} view of what counts as a [-problem. Their agreement is therefore reported as agreement between two coders who share that view, not as agreement between independent perspectives-]{+problem+} (GSRR-65).

**[GSRR-47] Extraction reliability.** {+Agreement between the two passes of author 1:+}
- C1: Cohen's kappa for each level, as a binary code, and for the representative value.
- C2b: kappa per item for the primary type, for `boundary`, and for the secondary type among items[-both coders-] marked as [-boundary.-]{+boundary in both passes.+}
- C2a, C2c and C2d: kappa per instrument.
- C2b target: kappa over all items, with "no target" as a category.
- C3, C4 (a)–(d), each column of C4 (e), C5, C6a, C6b, the C6c title input, and the C4f record summary and its gross-inconsistency summary: kappa per record.
- C4f per result: the number of results recalculated [-by-]{+in+} only one [-coder,-]{+pass,+} and, for results {+recalculated in+} both [-coders recalculated,-]{+passes,+} kappa for the judgement (consistent / inconsistent / grossly inconsistent / cannot be calculated).
- C6c and C7 are derived, so no kappa is computed for them. For the conclusion sentence, whether the conclusion and the main instrument could be identified, whether the conclusion uses an AI-fatigue term, and the construct-term family of the conclusion, the percentage of identical choices is reported.
- C4f: agreement between the reconciled[-human-] values and the AI draft, per recalculated result. It is reported [-only and is not a stopping criterion.-]{+only.+}
- Records coded [-by-]{+in+} only one [-coder-]{+pass+} are counted and reported.
- Percentage agreement is reported alongside every kappa.
- 95% CIs by bootstrap (2,000 resamples, seed 20261017) over records, and over instrument versions for item-level codes.
- If both [-coders-]{+passes+} use a single category, kappa is undefined and only percentage agreement is reported.
- Reported separately for the {+calibration passes, the+} exploration set and the main set.

**[GSRR-48] Extraction reconciliation procedure.**
- [-Coders discuss-]{+Disagreements between the two passes are resolved by a third pass by author 1, made with both earlier passes and+} the full [-text.-]{+text visible.+}
- Disagreements that remain are coded "unresolved". Unresolved codes are excluded from proportions, and their number is reported; the exception is C2b, where unresolved items stay in the item denominator as their own category (GSRR-53). A derived value (the C1 representative value, the C4f record summary, C6c, C7) is "unresolved" if any of its inputs is.
-[-In the single-coder procedure (GSRR-44), disagreements between the two passes are resolved by a third pass by author 1, made with both earlier passes visible, and the record is flagged.-]
[---] A sensitivity analysis uses each [-coder's-]{+pass's+} values in turn (GSRR-62).
- Codes [-before-]{+of both passes+} and [-after reconciliation-]{+the reconciled codes+} are[-both-] kept.

**[GSRR-49] Extraction procedure justification.**
- Each code answers one question: RQ1 = C1; RQ2 = C2a–C2d and C3; RQ3 = C4; RQ4 = C5; RQ5 = C6; SQ2 = C7. SQ1 is answered by grouping.
- [-Two independent coders are used because most-]{+Most+} codes require judgement. {+A second human coder was not available without a workload the co-author could not take on, so author 1 codes twice, at least four weeks apart. The two passes show how consistently one coder applies the rules; they do not show whether another person would apply them in the same way.+}

**[GSRR-50] Data management and sharing.**
- At publication, the following go in the same OSF project as this registration: the code table (CSV), the codebook and the coding form under CC BY 4.0, and the scripts under the MIT licence.
@@ -371,6 +376,7 @@ General rules:
  - C7: each condition separately, as three problem types: (i) causal wording not supported by the design; (ii) an AI-fatigue term in the conclusion while the main instrument's C1 representative value is L3 to L6; (iii) the construct term of the conclusion and the name of the main instrument in different term families. (iii) and C6a are name checks; they do not compare the content of the instruments.
- C2b types are not problem types. Their distribution is described, without calling any type a problem, because this review's eligibility definition includes motivational and behavioural depletion (GSRR-24).
- **Evaluable records.** A record is evaluable for a problem type only if its value can show or not show the problem: C4 (a)–(d) consistent or inconsistent; C4 (e) a codebook value of yes or no, and an agreement value of value given, index named only or none; C4f any inconsistency or none (records with at least one calculated result), and likewise for the gross summary; C5 any category; C6a same or different family; C6b match or mismatch; C6c any of its three derived values other than "cannot decide"; each condition of C7 met or not met. Other values ("not reported", "no criterion stated", "no comparison possible", "cannot be calculated", "cannot decide", "no term to compare", "instrument name has no family term", "instrument unnamed", "no construct term in the title") make a record not evaluable for that problem type.
{+- The main set is the set decided by author 1 and the AI screener (GSRR-33, GSRR-39). Whether each statement holds when the main set is decided by two human screeners is reported as sensitivity analysis 5 (GSRR-62).+}
- For each problem type, among the evaluable main-set records: if at least one shows it, we write that it "was observed in the main set"; if none does, that it "was not observed in the main set"; if no record is evaluable, that it "could not be evaluated". Each statement gives the count, the number of evaluable records, the number not evaluable and the number unresolved. In the abstract, the abstract rule of the outline applies (attachment 5).
- Values inherited from the exploration coding (GSRR-44, step 4) concern C2b, which is not a problem type, so they never enter a problem statement.
- The words "confirm", "replicate" and "replication" are not used about the observations of the narrative review, and no word of frequency or severity ("common", "rare", "widespread", "serious") is used about a problem type.
@@ -379,42 +385,47 @@ General rules:

**[GSRR-58] Synthesist blinding.** None. The synthesis is computed by script from the code table.

**[GSRR-59] Synthesis reliability.** {+All tables are produced by script from the code table.+} Author [-2-]{+1+} checks every number in [-every table-]{+the manuscript+} against the [-code table.-]{+script output.+}

**[GSRR-60] Synthesis reconciliation procedure.** Discrepancies are traced to the code table and the script and corrected.

**[GSRR-61] Publication bias analyses.** Not applicable (no effect estimates).

**[GSRR-62] Sensitivity analyses.** Analyses 1, [-2 and-]{+2,+} 4 {+and 5+} are applied to the problem statements of GSRR-57; analysis 3 is applied to the C2b tables. {+Analysis 5 is also applied to the record-level tables of the main set.+}
1. Peer-reviewed records only.
2. Records in the C5 category "signs present but not confirmed" removed.
3. C2b counted with secondary types included: each boundary item counts once for its primary type and once for its secondary type, and the denominator stays the number of coded items.
4. Each [-coder's-]{+pass's+} values in place of the reconciled values.
{+5. **Main set decided by two human screeners.** After the manuscript draft is written, author 2 reads it, and then authors 1 and 2 screen again, each on their own and then together, at the full-text stage and the centre stage: every additional candidate that author 1 or the AI screener sent to the full-text stage (GSRR-33). Records that both excluded at the title and abstract stage are not screened again. Both screeners then know the results, so this screening is not blind to them; it shows whether the problem statements depend on how the main set was screened, not a screening free of that knowledge. Studies that this screening adds to the main set are coded once by author 1 under the final rules and flagged as single-pass; studies it removes are dropped. The tables and problem statements are computed again, and every difference from the main analysis is reported. Both screeners' judgements before reconciliation and the final decisions are released (GSRR-41).+}

**[GSRR-63] Synthesis procedure justification.** The questions ask what practices are present in the coded set. Counts with denominators answer them; proportions describe the coded set and are not estimates of how often a practice occurs in the literature.

**[GSRR-64] Synthesis data management and sharing.** As in GSRR-50. The synthesis script `c_synthesis.py` implements:
- the screening [-order and the calibration draws;-]{+order;+}
- the derived values (C1 representative value, C4f summary, C6c, C7 and each of its conditions);
- agreement per set and unit (GSRR-47);
- the tables of GSRR-56 by set; the record-level tables also by population group and by centre (the centre tables leave out C1, C6c and C7 (ii), GSRR-12); C4f per result and the RQ4 counts also by population group; the C2b tables and the instruments used by set only; including C2a, C2c, C2d, C2b per instrument, the instruments used, C4f per result, the per-study table and RQ4 study counts;
- the problem statements of GSRR-57;
- sensitivity analyses 1–4 of GSRR-62. {+Analysis 5 is computed by running the same script on the code tables of the main set as decided in that screening.+}

The script stops if a required file or column is missing, a cell is empty or a value of any coded column is outside its code list, including impossible combinations (a gross inconsistency in a result that is not inconsistent) and a repeated value in a multi-value code. `make_dummy.py` builds a dummy code table, runs the script on it and checks boundary cases with assertions:[-calibration draws and small pools,-] the screening order, C1, C6c and C7 derivation (two-family names, missing terms, unresolved inputs, "cannot decide" when only the main instrument is unknown, the centre tables without C1, C6c and C7 (ii), each condition of C7 on its own), denominators, evaluable records per problem type (including a set in which no record is evaluable), the C4f summary order (a record with consistent and incalculable results), [-two-coder-]{+two-pass+} agreement on C4f results, minimum sizes in studies, multi-value codes, version sets, C2b with and without secondary types, the instruments used (including versions first seen in another set, whether a version refers to AI, and versions whose records differ in instructions, origin or disclosure), C4f per result (including by source), the per-study table, agreement coverage, sensitivity outputs, input validation and E5 links. Both files are attached to the registration with their SHA-256 **[at registration]**.

**[GSRR-65] Miscellaneous synthesis details.**
- Amendments after registration are logged with their date, reason and affected items, and listed in the report.
- Known limitations:
  - The rules were built from the exploration set.
  - {+Before registration, author 1 had screened 79 additional candidates, after reading AI-generated preliminary appraisals (GSRR-34).+} Author 1 [-has seen the titles, abstracts-]{+screens them again without these judgements, but may remember them.+}
{+  - The main set rests on one human screener+} and {+an+} AI [-appraisals-]{+screener, not on two human screeners. The AI screener's accuracy was checked on the 34 exploratory records, whose criteria were refined on those same records, and which include more studies+} of [-71-]{+centre-A and a different mix of population groups than the additional candidates; its accuracy on the+} additional [-candidates.-]{+candidates may be lower (GSRR-37).+}
{+  - Only free full texts are used. Records without one stay pending (E6) and are not coded; this includes records whose abstract alone did not settle whether fatigue was measured.+}
{+  - The two-human screening (sensitivity analysis 5) is done after the results are known.+}
  - C6a and C7 (iii) compare names. "Within what was measured" does not mean that the item content supports the conclusion.
  - [-Human-]{+Before registration, human+} screening of the additional candidates [-is-]{+was+} uneven across population groups. {+The fixed, interleaved order spreads screening across groups, and records still unscreened on 2026-12-31 are counted by group (GSRR-33).+}
  - The search drew on free sources only.
  - The eligibility criteria shape the outcomes. E3 removes studies with no relation to AI, so C1 "L6 none" is truncated. The fatigue definition includes motivational depletion, so the share of `MOT` items is partly set at entry.
  - Item content does not show what scores contain.
  - [-Both authors-]{+Coding is by one person in two passes. The agreement reported is within one coder, not between coders (GSRR-44), and the coder+} wrote the earlier narrative [-review, and the default coder 2 is one of them-]{+review+} (GSRR-46).
  - The [-people-]{+person+} who [-decide-]{+decides+} eligibility after registration [-are-]{+is+} the [-coders, and they know-]{+coder, who knows+} the rules (GSRR-33). The fixed [-order-]{+order, the AI screener's independent judgements+} and the released decisions show this influence but do not remove it.
  {+- The exploration set was used to build the rules and for calibration, and is then coded again; its tables are calibration material (GSRR-39).+}
  - Codebook version 2 was written after the exploration results were seen (GSRR-10).
  - C2b relies on printed items. Instruments whose items are not printed are coded "items unavailable", and the instruments with printed items may differ systematically from the others.

@@ -439,3 +450,4 @@ The script stops if a required file or column is missing, a cell is empty or a v
3. Query strings of the source database's searches **[at registration]**.
4. The screening order list for the remaining candidates (GSRR-33) **[at registration]**.
5. The manuscript outline (structure, claims and evidence, abstract rule and table shells), with its version, date and SHA-256, fixed with this registration **[at registration]**. Its scope rules, abstract rule, claims-and-evidence table and table shells bind the report, and differences from them are reported as deviations. Its discussion plan and recommendations are not registered. Where the outline and this registration differ, this registration takes precedence.
{+6. Instructions for the AI screener (English), with their SHA-256, and the check of the AI screener against the human decisions on the 34 exploratory records (GSRR-37): the judgements of both rounds, record by record, without abstracts, full texts or quotations of scale items.+}
diff --git a/papers/ai-fatigue-measurement/manuscript/draft/main.tex b/papers/ai-fatigue-measurement/manuscript/draft/main.tex
index ed815a1a..47503425 100644
--- a/papers/ai-fatigue-measurement/manuscript/draft/main.tex
+++ b/papers/ai-fatigue-measurement/manuscript/draft/main.tex
@@ -35,9 +35,8 @@ within digital burnout.
\textbf{Question.} How do such studies tie fatigue to AI, and do their titles and conclusions stay within that tie,
their design and their instruments' names?
\textbf{Methods.} TRACE, a registered methodological review, coded studies from one free-source literature database,
screened by[-authors who knew-] the [-rules-]{+first author and an AI screener+} and closed on 31 December 2026 (not a census). [-\tbd{Coding as it happened: two-]
[-coders sharing the view of an earlier narrative review / the first author and a third person / the first author twice}-]{+One coder+} applied
seven [-codes.-]{+codes twice.+}
\textbf{Results.} \tbd{Written from the tables after coding, by the registered abstract rule.}
\textbf{Availability.} Registration, outline, code table with per-instrument and per-study tables, codebook and scripts
are open.
@@ -162,7 +161,7 @@ recalculate ratios and P-values from reported confidence intervals in medical ab
\subsection{Registration and reporting}
The protocol was registered with the Generalized Systematic Review Registration form \citep{vandenakker2023} on
\tbd{date} (\tbd{identifier}), with the C2b codebook (version 2), the synthesis script and its test generator, the
screening [-order-]{+order, the instructions for the AI screener+} and the manuscript outline as attachments. Amendments are listed in Table~2 with their dates, reasons
and affected items. The report follows the checklist for meta-epidemiological methodology research
\citep{murad2017}, supplemented by the items of PRISMA 2020 that it lacks \citep{page2021}; the broader guideline for
methodological studies \citep{lawson2020} was still under development at registration.
@@ -173,19 +172,26 @@ records and additional candidates. This review ran no search of its own. \tbd{Se
registration attachment.}

\subsection{Eligibility and screening}
Eligibility follows the source database. Both authors [-screened,-]{+screened the 34 exploratory records. The additional candidates+}
{+were screened after registration by two independent screeners, the first author+} and {+an AI screener (Claude Opus,+}
{+Anthropic), at three stages: title and abstract, full text, and centre. The AI screener followed registered+}
{+instructions that turn+} the [-final decision was recorded-]{+eligibility criteria into seven questions, each answered+} with {+the passage that supports it,+}
{+and saw only the instructions and the record; the first author did not see+} its [-date.-]{+judgement of a record before recording+}
{+their own. Where the two differed, the first author decided at that stage. Before registration, the AI screener was+}
{+checked against the two human screeners' final decisions on the 34 exploratory records, with pass lines set in+}
{+advance: it passed on every record that the humans included or left pending, and agreed with them at full text+}
{+(kappa 0.89) and on the centre of every included study. These records were used to refine the source database's+}
{+criteria, so this accuracy may be optimistic. Only free full texts were used; records without one stayed pending.+}
Before registration the first author had screened [-71-]{+79+} additional candidates[-at title and abstract level-] after reading AI-generated preliminary
appraisals; [-the second author had not read these appraisals. After registration the remaining-]{+all+} candidates [-are-]{+were+} screened {+again,+} in a fixed [-order,-]{+order+} alternating between population groups, {+from a+}
{+database that showed no earlier judgement,+} and every decision is released.

\subsection{Sets}
The exploration set is the 10 primary studies included from the exploratory bibliography and four item-coded
instruments; the rules were built from it, {+it was used for calibration,+} and it is reported separately. The main set is
the primary studies among the additional candidates [-for which both screeners'-]{+whose+} final decision {+to include+} was recorded on or before
31 December [-2026, less-]
[-the calibration records.-]{+2026.+} Studies included later and before main coding form a late stratum, reported outside the primary
counts.[-Calibration records are drawn at random from the closed pool (seed 20261017), or from the exploration-]
[-set if the pool has 24 studies or fewer.-] A table based on fewer than 10 coded studies reports counts without proportions.

\subsection{Coding}
Units are the record (C1 and C3 to C7), the fatigue instrument (C2) and the item (C2b). Missing values have their own
@@ -204,17 +210,19 @@ codes, and a missing code stands alone in a cell. Table~1 lists the seven codes
  interview theme or not at all; and a construct term in a different family from the instrument's name.
\end{itemize}
C4f follows the logic of statcheck \citep{nuijten2016}, which recalculates p from reported test statistics and degrees
of freedom, with four differences: [-coders judge-]{+the coder judges+} each test rather than scanning the whole text; values in tables are
included; p-values that the report says are adjusted for multiple testing are not counted; and percentages and indirect
effects are added. The work is done by people. An AI assistant drafts values for C4f and for the bibliographic matches
of C5 only; the drafts are stored unopened with their SHA-256 and opened only after {+the values of+} both [-coders have fixed their own-]
[-values.-]{+coding passes+}
{+are fixed.+}

\subsection{Calibration, coding and reconciliation}
[-\tbd{Who coded, as it happened.} By default both authors code-]{+One coder, the first author, coded+} every record [-independently. Coding stops calibrating when-]
[-percentage agreement reaches 80\% on every registered unit; otherwise more records are drawn, up to two further rounds.-]
[-Both default coders share-]{+twice, at least four weeks apart, without looking at the first pass+}
{+during+} the [-view-]{+second. For calibration, all studies+} of [-an earlier narrative review, so their agreement is-]{+the exploration set were coded twice in November and December 2026;+}
{+every registered unit below 80\%+} agreement between [-coders who-]
[-share that view. Disagreements are discussed,-]{+the passes led to an amendment of the definitions, registered+}
{+before main coding. The main set, the late stratum+} and {+the exploration set were then coded twice under the final+}
{+rules. A third pass, with both earlier passes visible, resolved differences;+} those that [-remain-]{+remained+} are coded
unresolved. {+The agreement reported is within one coder, not between coders.+}

\subsection{Synthesis}
All values are computed by the registered script from the reconciled code table. The review describes; it estimates no
@@ -223,14 +231,17 @@ advance; among them, a problem type ``was observed in the main set'' if at least
in the main set'' if none does, and ``could not be evaluated'' if no record can show it. Each statement gives the count,
the number of evaluable records, the number not evaluable and the number unresolved. These statements report presence
or absence in this set; they are not frequencies. Sensitivity analyses use peer-reviewed records only, remove records
with unconfirmed signs of overlap, count the secondary type of boundary items, and use each [-coder's-]{+pass's+} values in turn.
{+In a fifth analysis, both authors screened again, at full text and centre, every candidate that either screener had+}
{+sent to full text, after the second author had read the manuscript draft; studies this added were coded once, and the+}
{+tables and problem statements were computed again. This screening was done with the results known.+}

\section{Results}
\tbd{Written only after the tables have been generated from the code table, in the registered terms.}

\begin{enumerate}
  \item Records and sets (Figure~1, Table~3).
  \item [-Coder agreement-]{+Agreement between the two coding passes+} (Table~4).
  \item RQ1 attribution (Table~5).
  \item RQ2 instruments and items (Tables~6, 7, 8 and 15).
  \item RQ3 reporting (Table~9).
@@ -267,11 +278,14 @@ authors to state the level at which a fatigue measure is tied to AI, so that row

\subsection{Limitations}
The rules were built from the exploration set, and the C2b codebook (version 2) was written after the exploration
results had been seen. {+The main set rests on one human screener and an AI screener, not on two human screeners, and+}
{+the AI screener's accuracy was checked on records that had been used to refine the criteria and that differ from the+}
{+additional candidates in their mix of studies; the screening by both authors is a sensitivity analysis made with the+}
{+results known.+} Before registration the first author had [-seen the titles, abstracts and AI-generated-]
[-appraisals of 71-]{+screened 79+} additional [-candidates. After registration, the people-]{+candidates after reading AI-generated+}
{+appraisals, and may remember them. The person+} who [-decide-]{+decides+} eligibility [-are-]{+is+} the [-coders,-]{+coder,+} who [-know-]{+knows+} the rules; the fixed
screening [-order-]{+order, the AI screener's independent judgements+} and the released decisions show this influence but do not
remove it. [-Human-]
[-screening of the additional candidates is uneven across population groups,-]{+Only free full texts were used,+} and the source database drew on free sources only, so the main set is not
a census and its proportions are not estimates for the literature.

The eligibility criteria shape some outcomes. Studies with no relation to AI are excluded, so the value of no
attribution to AI (C1, L6) is truncated; and the fatigue definition includes motivational depletion, so the share of
@@ -280,8 +294,10 @@ printed are coded as items unavailable, and the instruments with printed items m
others. Item content shows what an instrument asks about, not what its scores contain.

C6a and the third condition of C7 compare names. A conclusion coded within what was measured meets none of the three
conditions; it is not shown that the items support it. [-Both authors-]{+Coding was done by one person in two passes, so the agreement+}
{+reported shows how consistently one coder applied the rules, not whether another person would apply them in the same+}
{+way; the coder+} wrote the earlier narrative review, and [-by-]
[-default both code, so their agreement is agreement between coders who share-]{+the codes carry+} that view. {+The exploration set was used to+}
{+build the rules and for calibration, and its tables are calibration material.+} \tbd{Limitations added by
deviations from the registration, if any.}

\section{Conclusions}
@@ -292,8 +308,8 @@ deviations from the registration, if any.}
\textbf{Competing interests.} No financial interests. Both authors built the source literature database \tbd{and wrote
the earlier narrative review}.
\textbf{Ethics.} Not applicable; no human participants.
\textbf{Use of AI.} An AI {+screener judged eligibility as the second independent screener, and an AI+} assistant drafted
values for C4f and [-C5-]{+C5,+} as described in the Method \tbd{and any other use in preparing the manuscript}.
\textbf{Author contributions.} \tbd{to be agreed}
\textbf{Data and code availability.} The registration, the code table, the codebook (CC BY 4.0) and the scripts (MIT
licence) are in the OSF project of the registration \tbd{link}.
diff --git a/papers/ai-fatigue-measurement/manuscript/draft/tables.tex b/papers/ai-fatigue-measurement/manuscript/draft/tables.tex
index c25f13f4..6be97f3b 100644
--- a/papers/ai-fatigue-measurement/manuscript/draft/tables.tex
+++ b/papers/ai-fatigue-measurement/manuscript/draft/tables.tex
@@ -57,7 +57,6 @@ Date & Registration item or outline section & Change and reason & Codes or table
Set & Records & Studies (E5 counted once) & Instruments & Six population groups & Centre A / Centre B \\
\midrule
Main set & --- & --- & --- & --- & --- \\
[-Calibration records & --- & --- & --- & --- & --- \\-]
Late stratum & --- & --- & --- & --- & --- \\
Exploration set & --- & --- & --- & --- & --- \\
Unscreened on 31 December 2026 & --- & & & --- & \\
@@ -67,24 +66,26 @@ Unscreened on 31 December 2026 & --- & & & --- & \\

\begin{table}[!htbp]
\centering
\caption{Agreement between [-coders who share the rules-]{+two coding passes of one coder+} (shell).}
\footnotesize
[-\begin{tabularx}{\linewidth}{p{34mm}XXXXXX}-]{+\begin{tabularx}{\linewidth}{p{34mm}XXXXXXXXX}+}
\toprule
Code or unit & {+Calib., agreement (\%) & Calib., kappa (95\% CI) & Calib., n &+} Main set, agreement (\%) & Main set, kappa (95\% CI) & Main set, n & Explor. set, agreement (\%) & Explor. set, kappa (95\% CI) & Explor. set, n \\
\midrule
C1 to C3, C4 (a) to (e), C5, C6 (one row each) & --- & --- & --- & --- & --- & --- {+& --- & --- & ---+} \\
C4f: results found [-by-]{+in+} one [-coder-]{+pass+} only & --- & & --- & --- & & --- {+& --- & & ---+} \\
C4f: judgement on results found [-by-]{+in+} both {+passes & --- & --- & ---+} & --- & --- & --- & --- & --- & --- \\
C7: construct term of the conclusion (family) & --- & --- & --- & --- & --- & --- {+& --- & --- & ---+} \\
C4f: agreement with the AI draft & {+& & &+} --- & & --- & --- & & --- \\
[-Single-coded records-]{+Records coded in one pass only & --- & &+} & --- & & & --- & & \\
\bottomrule
\end{tabularx}

\smallskip
\raggedright\footnotesize {+Calib., calibration passes on the exploration set;+} Explor., [-exploration.-]{+exploration set coded again under the final rules.+}
Kappa with a bootstrap 95\% confidence interval. {+Both passes are by the same coder, at least four weeks apart, so this+}
{+is agreement within one coder, not between coders.+} Agreement with the AI draft is agreement with a draft, not with a
correct value.[-The coders share the rules and the view of an earlier narrative review.-]
\end{table}

\begin{table}[!htbp]
@@ -256,16 +257,18 @@ or ``could not be evaluated''. A note gives, for each row, the values that made
\centering
\caption{Sensitivity analyses of the problem statements (shell).}
\small
[-\begin{tabularx}{\linewidth}{XXXXXX}-]{+\begin{tabularx}{\linewidth}{XXXXXXX}+}
\toprule
Problem type & Main analysis & 1: peer-reviewed only & 2: overlap signs removed & 4: [-coder-]{+pass+} 1 & 4: [-coder-]{+pass+} 2 {+& 5: screened by both authors+} \\
\midrule
One row per row of Table 12 & --- & --- & --- & --- & --- {+& ---+} \\
\bottomrule
\end{tabularx}

\smallskip
\raggedright\footnotesize Analysis 3 applies to the C2b tables and is reported beside Table 7. {+Analysis 5 uses the main set+}
{+as decided by both authors after the manuscript draft, with the results known; the numbers of studies it added and+}
{+removed are given in a note.+}
\end{table}

\begin{table}[!htbp]
diff --git a/papers/ai-fatigue-measurement/manuscript/outline.md b/papers/ai-fatigue-measurement/manuscript/outline.md
index d35183aa..c8b3ff0b 100644
--- a/papers/ai-fatigue-measurement/manuscript/outline.md
+++ b/papers/ai-fatigue-measurement/manuscript/outline.md
@@ -74,17 +74,18 @@ manuscript:
  content of the instruments, and the number of records in which both hold is reported. "Within what was measured"
  means only that none of the three conditions holds; it does not mean that the item content of the instrument
  supports the conclusion.
- The coding rules were written by the first author [-(GSRR-4). The two default coders share the view of what counts-]
[-  as a problem that comes from-]{+(GSRR-4), who is also+} the [-earlier narrative review, so their-]{+only coder and codes every record+}
{+  twice, at least four weeks apart (GSRR-44). The+} agreement {+reported+} is[-agreement-] between [-coders who share-]
[-  that view,-]{+two passes of one coder,+} not between
  [-independent perspectives (GSRR-46). If coder 2 was a third person who did not write the-]
[-  rules, the agreement is reported as agreement with a coder who did not write the rules. If the first author coded-]
[-  twice, the results are reported as single-coder results-]{+coders,+} and no claim of independent coding is [-made (GSRR-44).-]{+made. The coder wrote the earlier narrative review, so the codes carry+}
{+  that view of what counts as a problem (GSRR-46).+}
- The main set is the set of studies [-for which both screeners' final inclusion decision was recorded-]{+included+} by 31 December [-2026.-]{+2026 by two independent screeners, the first author and+}
{+  an AI screener whose accuracy was checked against human decisions before registration; the first author decided+}
{+  where they differed (GSRR-33, GSRR-37, GSRR-39).+} It {+does not rest on two human screeners; the screening by both+}
{+  authors after the manuscript draft is a sensitivity analysis, done knowing the results (GSRR-62). The set+} was drawn
  from one literature database built from free sources, and[-was screened after-]
[-  registration by-] the [-authors,-]{+first author,+} who {+screened it,+} knew the coding rules;
  before registration, the first author had [-seen the titles,-]
[-  abstracts and AI-generated appraisals of 71-]{+screened 79+} of the additional candidates [-(GSRR-33, GSRR-34,-]{+after reading AI-generated+}
{+  appraisals (GSRR-34,+} GSRR-65). It is not a census of the literature on AI and [-fatigue, and the population groups were screened unevenly before registration (GSRR-42).-]{+fatigue.+} Every claim about the main set
  is about that set.

## Relation to the authors' earlier narrative review

@@ -118,7 +119,7 @@ validity evidence.
1. **TRACE, a registered coding scheme that links three things in each study: how fatigue is tied to AI, what the
   fatigue items ask about, and what the report states and concludes (GSRR-1).** Seven codes (C1 to C7) with their rules and a codebook
   for item content, fixed before the main coding of the main set; amendments made after calibration are
   listed in Table 2. Its only reliability evidence is the agreement between [-its coders-]{+two coding passes of one coder+} (see Scope).
2. **A description of how a set of studies not used to build the rules attributes fatigue to AI, measures it and
   reports it** (RQ1 to RQ5, SQ1, SQ2), with the problem statements of the registration (new points 2, 4 and 5 above).
3. **Item-level content of the fatigue instruments** (new point 3): for instruments first seen in the main
@@ -139,11 +140,10 @@ Fixed before coding. The abstract states the question of the review (Contributio
the main set only:

- one sentence on the scope of the set, which is never removed: a set drawn from one literature database built from
  free sources, screened by[-authors who knew-] the [-rules,-]{+first author and an AI screener,+} closed on 31 December 2026, and not a census of the
  literature; with the number of studies and instruments [-coded, the number of calibration records removed-]{+coded+} and the number of candidates still unscreened on that
  date;
- how the coding was [-done, as it happened under GSRR-44: by the two default coders, who share the view of the-]
[-  narrative review;-]{+done:+} by {+one coder,+} the first [-author and a third person; or by the first author-]{+author,+} twice;
- the three things TRACE links, each with counts and no evaluative word: the distribution of the representative level
  of attribution (C1); for the instruments first seen in the main set with printed items, for each
  item-content type, the number of instruments with at least one item of that type, out of the instruments with coded
@@ -237,11 +237,13 @@ that the method can be read without the registration.
   why it was chosen.
2. Source of records: the literature database built by both authors and its searches (GSRR-21 to GSRR-32); the
   exploratory bibliography and the additional candidates; no search of this review's own.
3. Eligibility and screening: criteria (GSRR-24, GSRR-35); the [-two-screener process;-]{+first author and the AI screener as independent+}
{+   screeners at each stage, and how differences were decided (GSRR-33, GSRR-38); the AI screener's instructions, and+}
{+   its accuracy against human decisions on the exploratory records before registration (GSRR-36, GSRR-37); how free+}
{+   full texts were obtained;+} what was screened before registration and by whom (GSRR-32, GSRR-34); the fixed screening
   order after registration and the release of every decision (GSRR-33, GSRR-41).
4. Sets: exploration set (the 10 primary studies and four item-coded instruments of GSRR-39), {+used for calibration;+}
   main [-set,-]{+set;+} late [-stratum, candidate pool and calibration sample, small-pool rule,-]{+stratum;+} minimum sizes (GSRR-39).
5. Coding: units, instrument and main-instrument rules, missing-value codes, and the codes C1 to C7 with the C4f and
   C6b rules (GSRR-43); the codebook (version 2); the use of AI drafts for C4f and C5 only (GSRR-44). For C4f, a short
   table of what it shares with statcheck (Nuijten et al., 2016), which recalculates p from t, F, r, χ² and Z with their
@@ -249,8 +251,8 @@ that the method can be read without the registration.
   tables included, with the rules for degrees of freedom in table notes, asterisk-only p-values and tests reported
   twice; p-values adjusted for multiple testing not counted; z recalculated only when reported; percentages and
   indirect effects added; done by people.
6. Calibration, coding, blinding and reconciliation (GSRR-44 to [-GSRR-48), including the procedure if coder 2 is-]
[-   unavailable,-]{+GSRR-48): one coder, two passes at least four weeks+}
{+   apart,+} and what the agreement between the [-two coders-]{+passes+} can and cannot show [-(GSRR-46).-]{+(GSRR-44, GSRR-46).+}
7. Synthesis: derived values, missing data, the tables, the problem statements and the sensitivity analyses
   (GSRR-52 to GSRR-62); the script and its tests (GSRR-64).
8. Deviations from the registration and from this outline, each with its reason (also in Table 2).
@@ -258,10 +260,10 @@ that the method can be read without the registration.
### 4. Results

1. Records and sets: flow diagram; candidates screened and unscreened on 31 December 2026 by population group;
   exclusions by code and, for E2 and E3, by population group; [-calibration rounds-]{+agreement between the first author+} and[-records removed; whether-] the [-small-pool rule applied;-]{+AI screener+}
{+   at each stage;+} studies and E5-linked records (Figure 1, Table 3).
2. [-Coder agreement-]{+Agreement between the two coding passes+} per code and set, {+including the calibration passes,+} with the AI-draft
   cross-check for C4f, which is agreement with a draft, not with a correct value (Table 4).
3. RQ1 attribution (Table 5).
4. RQ2 instruments and items: origin, modification and format; adaptation procedures; reported disclosure; every
   instrument version used in the main set; item content per instrument first seen in the main set;
@@ -274,7 +276,7 @@ that the method can be read without the registration.
8. Problem statements (Table 12).
9. SQ1 by centre (supplementary tables set side by side, without comparison statements; without C1 and C6c, and
   with C7 conditions (i) and (iii) only).
10. Sensitivity analyses 1 to [-4-]{+5+} (Table 13).
11. Exploration set and late stratum (supplementary tables, labelled as such).

The text of each subsection is written only after the tables have been generated from the code table. It states what
@@ -332,9 +334,9 @@ the flow figures from the released screening decisions.

| ID | Claim | Registered definition | Evidence | Reported in |
|---|---|---|---|---|
| SC1 | The flow of records from the additional candidates to the main set, the[-calibration records removed, the-] late stratum, and the unscreened candidates by population [-group.-]{+group; agreement between the first author and the AI screener at each stage.+} | GSRR-32, GSRR-33, {+GSRR-37,+} GSRR-39, GSRR-41 | Released screening [-decisions; calibration draws output by the script-]{+decisions+} | Section 4.1; Figure 1; Table 3 |
| SC2 | The number of studies and of records, with E5-linked records counted once and separately. | GSRR-39, GSRR-56 (RQ4) | Script output, RQ4 study counts | Section 4.1; Table 3 |
| AG1 | Agreement between [-coders-]{+the two coding passes of one coder+} per code and [-set (between coders who share-]{+set, including+} the [-rules,-]{+calibration passes (GSRR-44,+} GSRR-46), and between the reconciled[-human-] values and the AI draft for C4f; the number of [-single-coded records.-]{+records coded in one pass only.+} | {+GSRR-44,+} GSRR-46, GSRR-47 | Script output, agreement | Section 4.2; Table 4 |
| R1 | Distribution of the representative level of attribution of the main fatigue instrument; values for other instruments in the supplement. | RQ1; GSRR-43 (C1) | Script output, C1 tables | Section 4.3; Table 5; abstract |
| R2a | Origin, modification and format of the fatigue instruments; reported adaptation procedures; reported disclosure. | RQ2; GSRR-43 (C2a, C2c, C2d) | Script output, instrument tables | Section 4.4; Table 6 |
| R2b | Item-content composition of each instrument first seen in the main set with printed items, the number of instruments with at least one item of each type, and the targets of reduced-interest, avoidance and futility items; the number of instruments with items unavailable. | RQ2; GSRR-43 (C2b), GSRR-56; codebook version 2 | Script output, C2b per instrument; per-instrument summary table | Section 4.4; Table 7; abstract |
@@ -346,7 +348,7 @@ the flow figures from the released screening decisions.
| S2 | Each condition of C7 ((i), (ii) and (iii)) separately, and the records in which C6a and C7 (iii) both hold. | SQ2; GSRR-43 (C7), GSRR-56 | Script output, C7 table | Section 4.7; Table 11 |
| PS1 | The problem statements of the registration for the main set, with each condition of C7 as its own type. | GSRR-57 | Script output, problem statements | Section 4.8; Table 12; abstract |
| S1 | Answers to RQ2 to RQ5 and SQ2 by centre, without C1 and C6c, and with C7 by conditions (i) and (iii) only. | SQ1; GSRR-12 | Script output, centre tables | Section 4.9; supplement |
| SE1 | The problem statements under sensitivity analyses 1, [-2-]{+2, 4+} and [-4,-]{+5, the record-level tables under analysis 5,+} and the C2b tables under analysis 3. | GSRR-62 | Script output, sensitivity [-outputs-]{+outputs; for analysis 5, the script run on the code tables of the set decided by both authors+} | Section 4.10; Table 13 |
| EX1 | The exploration set and the late stratum under the same rules, labelled as such and not compared with the main set. | GSRR-39, GSRR-56, GSRR-57 | Script output, tables by set | Section 4.11; supplement |
| PT1 | The C1 to C7 values of each coded study. | GSRR-56 (per-study table) | Script output, per-study table | Supplement |
| D1 | Recommendations, each tied to one code and to either an existing standard or a proposal of this scheme. Not a finding of this review. | Not registered (discussion) | The registered definitions of GSRR-43; the standards listed in the note to Table 14 | Section 5.3; Table 14 |
@@ -361,8 +363,8 @@ in a table of fewer than 10 studies shows a count without a proportion. Values e
("not verifiable", "not applicable", "unresolved") are shown in every table. The shells below fix the rows and
columns; no value is filled in before coding.

- Figure 1: flow diagram (additional candidates; [-screened;-]{+screened by the first author and the AI screener;+} excluded by code;
  main set;[-calibration records;-] late stratum; unscreened on 31 December 2026).
- Table 1: the codes C1 to C7, their units and their values (from the registration).
- Table 2: deviations from the registration and from this outline, with dates and reasons.
- Table 3: sets and their composition.
@@ -370,14 +372,14 @@ columns; no value is filled in before coding.
  | | Records | Studies (E5 counted once) | Instruments | By population group (six columns) | Centre-A / Centre-B |
  |---|---|---|---|---|---|
  | Main set | — | — | — | — | — |
[-  | Calibration records | — | — | — | — | — |-]
  | Late stratum | — | — | — | — | — |
  | Exploration set | — | — | — | — | — |
  | Unscreened on 31 December 2026 | — | | | — | |

- Table 4: agreement {+between the two coding passes of one coder+} per code (percentage agreement, kappa with bootstrap
  95% CI, n), {+with the calibration passes, the+} main {+set+} and {+the+} exploration [-sets-]{+set+} in separate columns; the C4f agreement
  with the AI draft; [-single-coded records.-]{+records coded in one pass only.+} The heading states that [-the-]
[-  coders share the rules (GSRR-46).-]{+this is agreement within one coder+}
{+  (GSRR-44).+}
- Table 5: C1 representative level (L1a, L1b, L2, L3, L4, L5, L6, excluded values), count and, where allowed,
  proportion.
- Table 6: C2a origin, modification (per kind: stated / found by comparison / no change / not verifiable) and format;
@@ -407,7 +409,8 @@ columns; no value is filled in before coding.
  One row for each problem type of GSRR-57; C7 has three rows, one per condition. A note gives, for each row, the values
  that made records not evaluable (GSRR-57).

- Table 13: sensitivity analyses (problem statements as in Table 12, with C7 by [-condition).-]{+condition), with analysis 5 (main set+}
{+  decided by both authors after the draft) in its own columns and the number of studies it added and removed.+}
- Table 14: recommendations.

  | Recommendation | Code | Row of Table 12 | Source: existing standard (cited) or proposal of this scheme | Question → what is measured → evidence needed → wording allowed (proposal) |
@@ -438,8 +441,7 @@ columns; no value is filled in before coding.
- The second author's details, and the registration identifier and date.
- The authorship of the narrative review, how it is cited (published, preprint or unpublished manuscript) and how its
  relation to this review is stated, to be agreed with the co-author when the manuscript draft is complete. Until
  then, this outline refers to the[-shared-] view of the [-coders-]{+coder+} (GSRR-46), and the Declarations state the authorship as agreed.
- Whether a reporting guideline for methodological studies has been published (checked immediately before
  submission).
- The script that copies values from the synthesis output into the manuscript.
