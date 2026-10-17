# 差分（round 5 の直し・コミット 1139499c → 5fd670fd・word-diff）

[-…-] は消した文、{+…+} は足した文。

diff --git a/.steering/20261017-ai-fatigue-c-outline/registration-attachments/ai-screening/instructions.md b/.steering/20261017-ai-fatigue-c-outline/registration-attachments/ai-screening/instructions.md
index 18dd1df2..92a70676 100644
--- a/.steering/20261017-ai-fatigue-c-outline/registration-attachments/ai-screening/instructions.md
+++ b/.steering/20261017-ai-fatigue-c-outline/registration-attachments/ai-screening/instructions.md
@@ -1,6 +1,6 @@
# Instructions for the AI screener

This text is given, unchanged, to the AI screener for every record. The AI screener is one of two independent screeners of the additional candidates (the other is author 1). It sees only this text and the record's inputs listed in section [-2.-]{+2, and it does not open web pages or use any other source.+} It does not see the source database's classification, either human screener's judgement, or any earlier AI appraisal.

## 1. The question this database collects studies for

@@ -15,7 +15,7 @@ Research design and reporting quality are not used to decide eligibility. The di

## 2. Inputs

- Stage 1 (title and abstract): the record ID, title, and the abstract as retrieved. If no abstract was retrieved, [-you may open the record's landing page-]{+judge+} from[-its DOI or URL to read-] the [-abstract. Write what you read-]{+title alone and write `title only`+} in `read`. {+Do not open web pages.+}
- Stage 2 (full text): the record ID and the full text, if a free full text was found. Only publicly and freely available full texts are used. Do not use other sources.
- Stage 3 (centre): the full text of a record included at stage 2.

@@ -30,7 +30,7 @@ Answer every question with `yes`, `no` or `unclear`, and give the place in the i
| Q3 | Is AI used only as a tool to detect or predict fatigue (for example, a machine-learning model classifying drowsiness from sensor data), with no people using, supervising or evaluating AI as the object of study? | yes → E1 |
| Q4 | Is fatigue, in the sense of section 1, defined, measured or qualitatively analysed? Names vary: fatigue, exhaustion, burnout, depletion, tiredness, weariness, drained, and fatigue compounds such as decision fatigue. At stage 1, answer `no` only if the title or abstract states that the study has no fatigue measure or analysis; an abstract that lists measures or outcomes without fatigue is `unclear`, because abstracts often omit secondary measures. At stage 2, answer from the measures and analyses reported in the full text. | no → E2 |
| Q5 | Is that fatigue examined in relation to the AI use (as an outcome, correlate, mediator or theme of the AI use), rather than measured only in a part of the study unrelated to AI? | no → E3 |
| Q6 | Is the language of the full text English or Japanese, or is an English or Japanese version available? Answer from the language of the body, not of the title or abstract. At stage 1, answer `unclear` unless the [-record's page or bibliography-]{+input+} states the body language. | no → E7 |
| Q7 | (Stage 2 only.) Does the full text report the same sample as another record, as a duplicate or secondary report? Answer `yes` only if the full text itself says so (for example, "data were previously reported in"). | yes → E5 |

## 4. Decisions
@@ -62,7 +62,7 @@ One JSON object per record and stage, with these fields and nothing else:
  "id": "record ID",
  "stage": 1,
  "read": "title only | abstract | part of full text | full text",
  "source": [-"where-]{+"the source line given in+} the [-abstract-]{+input (URL+} or [-full text was read (URL)",-]{+database)",+}
  "answers": {
    "Q1": {"answer": "yes | no | unclear", "where": "place in the input", "quote": "at most 25 words"},
    "Q2": {}, "Q3": {}, "Q4": {}, "Q5": {}, "Q6": {}, "Q7": {}
diff --git a/.steering/20261017-ai-fatigue-c-outline/registration-en.md b/.steering/20261017-ai-fatigue-c-outline/registration-en.md
index 5787becd..144bd6dd 100644
--- a/.steering/20261017-ai-fatigue-c-outline/registration-en.md
+++ b/.steering/20261017-ai-fatigue-c-outline/registration-en.md
@@ -109,11 +109,11 @@ The third point was checked in 16 searches of free sources (Europe PMC, OpenAlex
  - what their items ask about — fatigue, avoidance, irritation, futility, reduced interest (C2b)? For reduced interest, avoidance and futility, toward what target?
  - the type of instrument used for the AI-side variable (C3)?
- **RQ3 (reporting).** How complete and how internally consistent is reporting? (C4)
- **RQ4 (sample overlap).** Consider the records, the records linked[-by the source database-] as the same [-sample,-]{+sample (E5, GSRR-35),+} and the records with signs of overlap that could not be confirmed. How many are there of each? How many studies remain when linked records are counted once? (C5) We do not establish independence.
- **RQ5 (title versus content).** Do titles and abstracts match the name of the main instrument, the design and the level of attribution? (C6)

**[GSRR-12] Secondary research questions.**
- **SQ1.** How are the answers to RQ2–RQ5 and SQ2 distributed within each of the[-source database's-] two [-eligibility groups (assigned-]{+centre groups, centre-A and centre-B, assigned+} at [-screening, GSRR-33)?-]{+screening (GSRR-33)?+} The tables of the two groups stand side by side; no statement says that a value is larger, smaller, more or less common in one group than in the other.
  - Centre-A: fatigue attributed to AI in its definition, measurement or analysis.
  - Centre-B: a general fatigue construct examined in relation to AI use.
  - RQ1 is not tabulated by these groups, because the grouping is defined by attribution and the tables would be circular. For the same reason, SQ1 leaves out C6c and reports C7 conditions (i) and (iii) only.
@@ -185,19 +185,20 @@ No paid databases were used.
## Screening (eligibility)

**[GSRR-33] Screening stages.** For the 34 exploratory records, the source database's two screeners (authors 1 and 2) screened independently and reconciled their disagreements; this review takes those final decisions. The additional candidates are screened after registration by two independent screeners: author 1 and an AI screener (Claude Opus, Anthropic). There are three stages: title and abstract; full text; and centre (centre-A, centre-B or boundary, for records included at full text).
- **Each stage.** Author 1 and the AI screener judge every record [-independently. Author 1 does not see-]{+independently, with+} the [-AI screener's judgement-]{+same questions and decision rules (GSRR-36). The work goes in batches+} of[-a record-] at {+most nine records, cut from the fixed screening order. For each batch and stage, author 1's judgements are committed to+} a [-stage before recording-]{+version-controlled repository, with+} their [-own judgement of it at-]{+time, before the AI screener's output for+} that [-stage.-]{+batch is opened; the AI screener writes its output to a file, and its SHA-256 and time are recorded. Both times are released (GSRR-41).+} Where the two differ, author 1 decides at that stage, after reading the AI screener's answers and the passages it cites (GSRR-38). Records that both screeners exclude at a stage are excluded; [-records-]{+if their exclusion codes differ, author 1 decides the code. Records+} that both include go on to the next stage. {+At the full-text stage, a record that is pending for either screener, or that both leave pending, is decided by author 1 as include, exclude or pending; a record still pending on 2026-12-31 is outside the main set and is counted in Table 3 and the flow diagram. At the centre stage either screener may answer boundary, but the final value is centre-A or centre-B, decided by author 1; the number of records that either screener judged boundary is reported.+}
{+- **Same sample (E5).** At the full-text stage, a record is linked to another as the same sample only if its full text says so (attachment 6, Q7), decided like any other exclusion. Within a linked group, the record coded is the one with the earliest publication date (if equal, the first in the screening order). For the exploration set, the source database's links are used.+}
- **The AI screener.** It follows fixed instructions (attachment 6). They turn the source database's criteria (GSRR-24, GSRR-35) into seven questions, each answered `yes`, `no` or `unclear` with the place in the input that supports the answer, and fixed rules that turn the answers into a decision and an exclusion code. At the title and abstract stage, a record is included when in doubt. [-Each record is judged on its own,-]{+It judges the records of a batch+} in {+one call, each against the instructions;+} a[-separate call per-] batch {+is never re-run, except once when the output is not in the required format, in which case the first output in the required format is used and the number+} of [-at most nine records. The AI screener-]{+re-runs is reported. It+} sees only the instructions and the record's {+inputs from the screening database: the+} title and abstract (first [-stage)-]{+stage; if no abstract was retrieved, the title alone)+} or {+the+} full text (later stages). It does not {+open web pages or use any other source, and it does not+} see the source database's classification, author 1's judgements or any earlier AI appraisal. [-Its output-]{+One model identifier+} is [-stored with-]{+used throughout (recorded at registration **[at registration]**); if it becomes unavailable,+} its [-SHA-256 before author 1 opens it.-]{+successor is first checked on the 34 exploratory records against the pass lines of GSRR-37, and the change is reported as a deviation.+}
- **Full texts.** Both screeners use the same full text: only versions that are publicly and freely available. They are retrieved by script (open-access locations listed by OpenAlex, Europe PMC and Semantic Scholar), then by author 1 in a web browser; author 1 passes any bot check and saves PDFs that the browser only displays. A full text from Europe PMC may be its full-text XML, which is the publisher's text extracted by machine. No full text is retyped or rewritten. If no free full text is found, the record is pending with E6 (GSRR-35).
- **After registration**, author 1 knows these coding rules. To limit the effect of that knowledge:
  - the remaining candidates are all 264 additional candidates, including the 79 that author 1 screened before registration (GSRR-32) and the 43 review-search records; the earlier judgements are not shown to author 1 during screening;
  - they are screened in a fixed order: within each population group the record IDs, sorted alphabetically, are shuffled with Python `random.shuffle`, using a generator freshly seeded with 20261018 for each group; the groups are then interleaved, one record from each group in the order listed in GSRR-16, so that progress by 2026-12-31 does not depend on the group;
  - records with no population group in the source database are placed in the group unknown. Before registration, 51 of the 264 additional candidates had none: the 43 review-search records, seven records that the source database's machine classification labels review-type, and one record added by hand. To see why, an AI assistant read their titles and abstracts twice, in two independent readings with fixed definitions, only for document type and population group, not for eligibility: both readings found 50 to be documents without participants (reviews, study or review protocols, commentaries and a correction notice); the readings differed on the remaining record, which has no abstract, and its document type was left undetermined. No human read the abstracts of the 43 review-search records for this purpose;
  - the resulting order list and its SHA-256 are attached to the registration, with the Python version used **[at registration]**;
  - no [-coding-]{+additional candidate+} is [-done-]{+coded+} during [-screening;-]{+screening (calibration on the exploration set runs in parallel, GSRR-44);+}
  - every screening decision made after registration is released with its date, author 1's judgement, the AI screener's judgement and the exclusion code (GSRR-41);
  - exclusions for E2 and E3 are counted by population group, and the candidates still unscreened on 2026-12-31 are counted by population group.

**[GSRR-34] Screened fields / blinding.** Author 1 screens from a database that contains the bibliographic data, the abstract and the free full text of each record and no judgement: neither the AI screener's, nor author 1's earlier ones, nor the AI appraisals author 1 read before 2026-10-17. Before registration, author 1 had screened 79 additional candidates and read AI-generated preliminary appraisals before judging (GSRR-32); author 1 may remember them (GSRR-65). The AI screener is blind to all judgements (GSRR-33). {+Blinding holds within a stage only: for a record on which the two screeners differed, author 1 has read the AI screener's answers before judging that record at the next stage.+}

**[GSRR-35] Used exclusion criteria.**
- E1: AI only as a fatigue-detection tool.
@@ -208,16 +209,16 @@ No paid databases were used.
- E6: full text unavailable.
- E7: language other than English or Japanese.

E5 records are not coded. They stay linked to their group for C5 (GSRR-43). Each E5 group has exactly one coded [-record,-]{+record (GSRR-33),+} whose C5 value is "linked[-by the source database-] as the same sample"; no other coded record has that value. An uncoded E5 record is counted in the RQ4 record counts with the set and population group of its group's coded record.

**[GSRR-36] Screener instructions.** [-Author 1:-]{+Both screeners use+} the [-source database's criteria-]{+questions of attachment 6 (sections 1 to 4) and its decision rules: inclusion when+} in {+doubt at+} the [-screening database (attachment 6 gives-]{+title and abstract stage, the order of exclusion codes, and+} the [-same criteria as questions).-]{+definitions of pending and of the centre values. Author 1 records a decision and a code for each record and does not fill in the AI screener's output format.+} The AI [-screener:-]{+screener receives+} the [-instructions-]{+whole+} of attachment 6, with [-their-]{+its+} SHA-256.

**[GSRR-37] Screening reliability.**
- *Exploratory records.* The source database's two screeners agreed on 32 of the 34 exploratory records on three categories. That is exploration material.
- *AI screener, checked before registration.* The pass lines were set before the AI screener was applied: at the title and abstract stage, none of the 13 records that the two human screeners finally included or left pending is excluded; at the full-text stage and the centre stage, Cohen's kappa of at least 0.6 against the human final decisions. If a line was missed, the instructions could be revised once and applied again; if it was still missed, the AI screener's judgements would be advisory only and author 1 would decide every record. The instructions were written from the source database's criteria without looking at the human decisions, but those criteria were themselves refined on these 34 records, so the accuracy may be optimistic. Round 1 met all three lines (title and abstract: 13 of 13 passed on, 19 of 21 exclusions also excluded; full text: 33 of 34 agreed, kappa 0.945; centre: 10 of 10 agreed). One question (whether fatigue is measured) was then clarified for the title and abstract stage, because the AI screener had excluded records whose abstracts listed measures without fatigue; the registered instructions are the clarified version. Round [-2, with the registered instructions,-]{+2+} also met all three lines (title and abstract: 13 of 13 passed on, 16 of 21 exclusions also excluded; full text: 32 of 34 agreed, kappa 0.893; centre: 10 of 10 agreed). The {+pre-set rule did not call for the revision before round 2: it was a departure from the rule, and it is reported as one. In rounds 1 and 2 the instructions allowed the AI screener to open a record's web page when no abstract had been retrieved; this was then removed, so that both screeners see the same inputs, and round 3 applied the registered instructions, without web access, to the same records in batches of at most nine (title and abstract: 13 of 13 passed on, 16 of 21 exclusions also excluded, 4 records judged from the title alone; full text: 32 of 34 agreed, kappa 0.893; centre: 10 of 10 agreed, centre-A 7 and centre-B 3, kappa 1.0). Round 3 gave the same decisions as round 2. The pass lines were committed before round 1, and the instructions before each round; the commits and the record-by-record judgements of all three rounds are given with attachment 6, with the+} two records on which round [-2-]{+3+} differed from the human [-decision are reported with attachment 6.-]{+decision.+}
- *Additional candidates.* For each stage, the agreement between author 1 and the AI screener before reconciliation is reported as percentage agreement and Cohen's kappa, with the number of records each screener sent [-on.-]{+on, the number of differences decided as author 1 had judged and as the AI screener had judged, and, at the centre stage, the number of records judged boundary. Because author 1 decides every difference, this agreement describes how often the two screeners agreed; it is not the AI screener's accuracy. A drop in agreement below the pass lines does not change the procedure; it is reported.+}

**[GSRR-38] Screening reconciliation procedure.** Author 1 decides every record on which author 1 and the AI screener differ, at the stage where they differ, after reading the AI screener's answers and cited passages. Both judgements before reconciliation are kept and released [-(GSRR-41).-]{+(GSRR-41), with the number of differences decided each way (GSRR-37).+} The main set therefore rests on one human screener and an AI screener, not on two human screeners; sensitivity analysis 5 (GSRR-62) repeats the full-text screening with two human screeners after the manuscript draft.

**[GSRR-39] Sampling and sample size.**
- **Exploration set.** The 10 primary studies the source database included from the 34-record bibliography, and the four item-coded instruments. Used for calibration and coded again after calibration (GSRR-6). Its tables are flagged as calibration material.
@@ -228,9 +229,9 @@ E5 records are not coded. They stay linked to their group for C5 (GSRR-43). Each
- **Calibration.** Calibration uses all primary studies of the exploration set (GSRR-44). No record of the main set is used for calibration or removed from it.
- **Minimum size.** The minimum is counted in coded records, not instruments; E5-linked records are not coded (GSRR-35), so each coded record is one study. It applies to every table on its own: a table (a set, a population group or a centre) based on fewer than 10 studies reports counts only, without proportions. The 10-study rule does not apply to the proportions of item types within one instrument, which follow the C2b rule. For C2b, if fewer than 3 instruments with available items are first seen in the main set, each instrument's counts are still given, without proportions. The number of "items unavailable" instruments is always shown next to the C2b tables.

**[GSRR-40] Screening procedure justification.** The source database had a second human screener only for the 34 exploratory records. A second human screening of the 264 additional candidates before coding would fall on the co-author, whose time is [-limited.-]{+limited during the screening period.+} An AI screener, checked against the human decisions on the 34 records before registration, is used as the independent second screener [-instead, and the-]{+instead. The+} two-human screening is [-done-]{+moved to+} after the manuscript {+draft, when the co-author reads the+} draft {+anyway, and is limited to the full-text+} and {+centre stages of the records that either screener sent to full text; it is+} reported as a sensitivity analysis (GSRR-62). {+If the co-author cannot do it, it is not done (GSRR-62).+}

**[GSRR-41] Data management and sharing.** The list of record IDs, with author 1's judgement and the AI screener's judgement at each stage, the final decision, the exclusion code and the decision date, will be released with the code table (GSRR-50). The AI screener's outputs are released with their quotations, which are limited to 25 words [-each;-]{+each, except quotations of scale items, which are removed before release;+} no abstract or full text is released. {+The times of author 1's commits and of the AI screener's outputs are released (GSRR-33).+}

**[GSRR-42] Miscellaneous screening details.** On 2026-10-17, the screening of the additional candidates had stopped part-way through a list ordered by population group. Some groups, such as health professionals, had no human screening yet. All 264 records are screened again in the fixed order (GSRR-33), and every result table shows counts by population group.

@@ -261,7 +262,7 @@ General rules:
| C2d | Measurement properties reported (per instrument) | Item disclosure: all / some / none. Reliability in this sample: reported / not. Factor analysis in this sample: reported / not. Reason for choosing the instrument: given (a sentence on why it fits the construct or population; a citation alone does not count) / not. No COSMIN rating is made |
| C3 | AI-side variable instrument (all that apply; each value is counted once per record) | amount of use / dependence or addiction type (source scale) / attitude or acceptance / other / none |
| C4 | Reporting completeness and internal consistency (values per rule) | (a) N in the text vs. table denominators: consistent / inconsistent (which) / no comparison possible (N given in only one place). (b) Direction of the main relation in the abstract, results and discussion: consistent / inconsistent (where) / not applicable. (c) Discriminant validity: the report's own stated criterion vs. its reported values: consistent / inconsistent / no criterion stated / not applicable. We bring in no thresholds of our own. (d) Ethics statements within the report (approval present, approving body): consistent / inconsistent / not reported. (e) Qualitative coding, in two columns: codebook available (yes / no) and agreement (value given / index named only / none); both not applicable for quantitative studies. (f) Recalculation: see the rules below this table |
| C5 | Sample overlap | Category: linked[-by the source database-] as the same sample (E5 [-group)-]{+group: by the source database for the exploration set, at screening for the additional candidates, GSRR-33)+} / signs present but not confirmed / no signs. Signs, each recorded: shared authors, region, survey site, grant number, identical N. [-We do not decide sameness ourselves-]{+Sameness is decided only where a report states it (E5); otherwise the signs are recorded and no decision is made+} |
| C6 | Title and abstract versus content | (a) Construct term in the title vs. the name of the main instrument. Term families: {fatigue, tiredness, 疲労, 疲れ}; {exhaustion, depletion, 消耗, 枯渇}; {burnout, バーンアウト, 燃え尽き}. A construct term is any word of these families, including inflected forms and compounds (tired, fatigued, exhausted, techno-exhaustion). Values: same family (at least one family shared, so a name with two families matches either) / different family / instrument name has no family term / instrument unnamed / not verifiable / no construct term in the title. This is a name check only. The item content of the main instrument (its C2b type composition) is reported next to it and is not turned into a match or mismatch. (b) Causal wording vs. design: see the rules below this table. (c) AI-fatigue term in the title vs. attribution. The coder records whether the title uses an AI-fatigue term (the list in C7 (ii)): yes / no. C6c is then derived by script: "no AI-fatigue term in the title" if no, whatever the main instrument; "AI-fatigue term with L3–L6" if yes and the main instrument's C1 representative value is L3, L4, L5 or L6; "AI-fatigue term with L1a–L2" if yes and the value is L1a, L1b or L2; "cannot decide" if yes and the main instrument cannot be identified or its C1 value is not verifiable |
| C7 | Does the main conclusion meet any of three conditions (design, attribution level, names)? | The main conclusion is the first sentence of the abstract's conclusion section. If there is none, it is the last sentence of the abstract. It is copied verbatim. "Beyond what was measured" if any of these holds. (i) C6b is a mismatch. (ii) The conclusion uses an AI-fatigue term ("AI fatigue", "AI-induced fatigue", "AI-related fatigue", "GenAI fatigue", or the Japanese equivalent) while the main instrument's C1 representative value is L3, L4, L5 or L6. (iii) The construct term in the conclusion is in a different term family from the name of the main instrument, by the C6a rules. (iii) is "no term to compare" if the conclusion has no construct term or the instrument name has no family term, and "not verifiable" if the instrument name is not verifiable; "not verifiable" is checked before "no term to compare". (i) is "not verifiable" if C6b is. Otherwise "within what was measured". "Within what was measured" means only that none of (i)–(iii) holds; it does not mean that the item content of the instrument supports the conclusion. Each condition is also recorded on its own as met / not met (and not verifiable; for (iii), also no term to compare), and each is a separate problem type (GSRR-57); the summary value is reported only in the per-study table, and is "not verifiable" if no condition is met and one is not verifiable. "Cannot decide" is checked first: if the conclusion cannot be identified, all three conditions are "cannot decide"; if only the main instrument cannot be identified, (i) is still derived and (ii) and (iii) are "cannot decide". The coder codes only the conclusion sentence and its construct term; C7 is then derived by script from the reconciled codes. If any input is "unresolved", the summary value of C7 is "unresolved"; a condition is "unresolved" only if one of its own inputs is |

@@ -271,7 +272,7 @@ General rules:
  - Values in tables are included. Degrees of freedom given in a table note are used; degrees of freedom that would have to be inferred from the sample size are not, and the result is "cannot be calculated". A p-value shown only by asterisks is treated as an inequality at the threshold stated in the table note; without a stated threshold it is "cannot be calculated". "Cannot be calculated" stays in the denominator (GSRR-53). A test reported in both the text and a table is counted once, from the text. Each result records whether it came from the text or a table.
  - Percentages from counts and denominators.
  - An indirect effect as a×b, only for a single-mediator path where a, b and the indirect effect are reported at the same level of standardization.
- **Who recalculates.** Author 1 recalculates in each of the two coding passes, independently of the other pass. The AI draft is generated by author 1 and stored unopened, with its SHA-256 recorded. It is opened only after the values of both passes {+and of the third pass (GSRR-48)+} are fixed, and is then used only as a cross-check; its agreement with the human values is reported. Data are the reconciled human values.
- These rules follow the logic of statcheck (Nuijten et al., 2016), which recalculates p from t, F, r, χ² and Z with their degrees of freedom, with four differences: the coder judges each test rather than scanning the whole text, so a test is one-tailed only if the report says one-tailed, one-sided or directional for that test; values printed in tables are included; p-values that the report says are adjusted for multiple testing are not counted; and percentages and indirect effects are added. The procedure is carried out by people, not by statcheck.
- **Tolerance.** A value is consistent if it falls within the range implied by rounding the inputs to their reported decimals.
- **Unit.** Each recalculated result. Each record is then summarised by the first value that applies: any inconsistency (at least one inconsistent result); none (at least one consistent result and no inconsistent one); cannot be calculated (results to recalculate, none of which could be calculated); not applicable (no result to recalculate). The gross-inconsistency summary uses the same order: any gross inconsistency (at least one grossly inconsistent result); none (at least one calculated result and no grossly inconsistent one); cannot be calculated; not applicable. Because results cluster in records, the number of recalculated results per record and the number of consistent, inconsistent and grossly inconsistent results are also reported (GSRR-56).
@@ -296,12 +297,12 @@ General rules:

**[GSRR-44] Extraction stages.** This is a single-coder review: author 1 codes every record twice, at least four weeks apart, and the second pass is made without looking at the first. The agreement reported is agreement between two passes of one coder, not between coders, and no claim of independent coding is made.
1. **Worked examples.** Before calibration, author 1 tries the definitions on worked examples that include multiple instruments, a qualitative study and missing values.
2. **Calibration** (GSRR-39). Author 1 codes all primary studies of the exploration set twice: the first pass in November 2026 and the second in December 2026, at least four weeks later. Agreement between the two passes is computed on each of these units: each C1 level; C2a, C2c and C2d per instrument; C2b primary type, boundary and target per item; C3, C4 (a)–(d), each column of C4 (e), C5, C6a, C6b and the C6c title input per record; the C4f judgement of each result recalculated in both passes; the conclusion sentence, whether the conclusion and the main instrument could be identified, whether the conclusion uses an AI-fatigue term, and the construct-term family of the conclusion. For every unit below 80% percentage [-agreement,-]{+agreement in at least 5 units of comparison,+} the definitions are amended and the amendment is registered before main coding; {+units with fewer than 5 are reported but do not trigger an amendment. An amendment is based only on+} the [-low-]{+disagreements between the two calibration passes, and the record IDs it rests on are listed with it; nothing read while screening the additional candidates is used. Amended definitions are not checked again before main coding; their+} agreement is [-reported.-]{+seen in the two passes of main coding (GSRR-65).+} Derived values and the agreement with the AI draft are not criteria. Kappa is reported alongside percentage agreement but is not a criterion, because rare categories make it unstable in 10 studies. Calibration codes are not data.
3. **Main coding.** Author 1 codes all records of the main set, the late stratum and the exploration set twice under the final codebook, at least four weeks apart. {+The first pass is saved with its SHA-256 and closed before the second begins, and the second pass takes the records in a different order, drawn with Python `random.shuffle` (seed 20261020).+}
4. **Use of exploration codes for instruments.** If a main-set study uses an instrument already coded in the exploration set, its C2b values come from the exploration values of the main coding (under the final codebook, not the calibration codes), but only if the item wording is verbatim identical. Otherwise the instrument is coded as a new version.
5. **AI drafts** are allowed only for C4f and C5.
   - For C4f, author 1 recomputes every value in both passes before seeing the [-draft (GSRR-43),-]{+draft,+} and the {+draft is opened only after the third pass (GSRR-43, GSRR-48); the+} agreement between human and AI values is reported.
   - For C5, the AI bibliographic matches are generated by author 1 and stored unopened, with their SHA-256 recorded. In each pass, author 1 first records the signs of overlap from the reports; the matches are opened only after both passes {+and the third pass+} have [-recorded-]{+fixed+} the [-signs,-]{+C5 codes,+} and every match is then checked.

**[GSRR-45] Extractor instructions.** This protocol, the C2b codebook (version 2) and a coding form with the definitions above.

@@ -385,7 +386,7 @@ General rules:

**[GSRR-58] Synthesist blinding.** None. The synthesis is computed by script from the code table.

**[GSRR-59] Synthesis reliability.** All tables are produced by script from the code [-table.-]{+table, and every result value in the manuscript is copied from the script output by a script, not typed by hand.+} Author 1 checks every number in the manuscript against the script output. {+No second person checks the numbers (GSRR-65).+}

**[GSRR-60] Synthesis reconciliation procedure.** Discrepancies are traced to the code table and the script and corrected.

@@ -396,14 +397,14 @@ General rules:
2. Records in the C5 category "signs present but not confirmed" removed.
3. C2b counted with secondary types included: each boundary item counts once for its primary type and once for its secondary type, and the denominator stays the number of coded items.
4. Each pass's values in place of the reconciled values.
5. **Main set decided by two human screeners.** After the manuscript draft is written, author 2 reads it, and then authors 1 and 2 screen again, each on their own and then together, at the full-text stage and the centre stage: every additional candidate that author 1 or the AI screener sent to the full-text stage (GSRR-33). Records {+sent to the full-text stage after 2026-12-31 are not included. Records+} that both excluded at the title and abstract stage are not screened again. Both screeners {+screen from the screening database without the judgements of the main screening; author 1 may remember them, so the independence this adds is mainly author 2's. Differences are settled by discussion; records still unsettled are counted as unresolved and kept out of the set of this analysis. Both screeners+} then know the results, so this screening is not blind to them; it shows whether the problem statements depend on how the main set was screened, not a screening free of that knowledge. Studies that this screening adds to the main set are coded once by author 1 under the final rules and flagged as single-pass; studies it removes are dropped. The tables and problem statements are computed again, and every difference from the main analysis is reported. Both screeners' judgements before reconciliation and the final decisions are released (GSRR-41). {+If any problem statement differs from the main analysis, the scope sentence of the abstract says so. If author 2 cannot do this screening, it is not done and no one else is asked: Table 13 shows the column empty with the reason, and Table 2, the limitations and the scope sentence of the abstract state that no two-human screening was done.+}

**[GSRR-63] Synthesis procedure justification.** The questions ask what practices are present in the coded set. Counts with denominators answer them; proportions describe the coded set and are not estimates of how often a practice occurs in the literature.

**[GSRR-64] Synthesis data management and sharing.** As in GSRR-50. The synthesis script `c_synthesis.py` implements:
- the screening order;
- the derived values (C1 representative value, C4f summary, C6c, C7 and each of its conditions);
- agreement per set and unit [-(GSRR-47);-]{+(GSRR-47), and the screening agreement between author 1 and the AI screener per stage, with the differences decided each way and the records judged boundary (GSRR-37);+}
- the tables of GSRR-56 by set; the record-level tables also by population group and by centre (the centre tables leave out C1, C6c and C7 (ii), GSRR-12); C4f per result and the RQ4 counts also by population group; the C2b tables and the instruments used by set only; including C2a, C2c, C2d, C2b per instrument, the instruments used, C4f per result, the per-study table and RQ4 study counts;
- the problem statements of GSRR-57;
- sensitivity analyses 1–4 of GSRR-62. Analysis 5 is computed by running the same script on the code tables of the main set as decided in that screening.
@@ -417,13 +418,18 @@ The script stops if a required file or column is missing, a cell is empty or a v
  - Before registration, author 1 had screened 79 additional candidates, after reading AI-generated preliminary appraisals (GSRR-34). Author 1 screens them again without these judgements, but may remember them.
  - The main set rests on one human screener and an AI screener, not on two human screeners. The AI screener's accuracy was checked on the 34 exploratory records, whose criteria were refined on those same records, and which include more studies of centre-A and a different mix of population groups than the additional candidates; its accuracy on the additional candidates may be lower (GSRR-37).
  - Only free full texts are used. Records without one stay pending (E6) and are not coded; this includes records whose abstract alone did not settle whether fatigue was measured.
  - The two-human screening (sensitivity analysis 5) is done after the results are [-known.-]{+known, and may not be done at all if author 2 cannot do it.+}
{+  - The AI screener judges up to nine records in one call, so the records of a batch may influence one another.+}
{+  - The AI screener's judgements are independent of author 1's, but its instructions were written by author 1 from criteria refined on the same 34 records; the independence is of judgement, not of perspective.+}
  - C6a and C7 (iii) compare names. "Within what was measured" does not mean that the item content supports the conclusion.
  - Before registration, human screening of the additional candidates was uneven across population groups. The fixed, interleaved order spreads screening across groups, and records still unscreened on 2026-12-31 are counted by group (GSRR-33).
  - The search drew on free sources only.
  - The eligibility criteria shape the outcomes. E3 removes studies with no relation to AI, so C1 "L6 none" is truncated. The fatigue definition includes motivational depletion, so the share of `MOT` items is partly set at entry.
  - Item content does not show what scores contain.
  - Coding is by one person in two passes. The agreement reported is within one coder, not between coders (GSRR-44), and the coder wrote the earlier narrative review (GSRR-46).
  {+- Calibration uses studies that the coder had read and partly coded while building the rules, so calibration agreement may be higher than agreement on new studies. Amended definitions are not checked before main coding (GSRR-44).+}
{+  - Calibration runs while the coder screens the additional candidates; amendments rest only on calibration disagreements (GSRR-44), but the coder's reading of candidates cannot be kept out of the coder's mind.+}
{+  - No second person checks the numbers in the tables (GSRR-59), and no second person codes.+}
  - The person who decides eligibility after registration is the coder, who knows the rules (GSRR-33). The fixed order, the AI screener's independent judgements and the released decisions show this influence but do not remove it.
  - The exploration set was used to build the rules and for calibration, and is then coded again; its tables are calibration material (GSRR-39).
  - Codebook version 2 was written after the exploration results were seen (GSRR-10).
diff --git a/papers/ai-fatigue-measurement/manuscript/draft/figure1.tex b/papers/ai-fatigue-measurement/manuscript/draft/figure1.tex
index dda75170..89659b0e 100644
--- a/papers/ai-fatigue-measurement/manuscript/draft/figure1.tex
+++ b/papers/ai-fatigue-measurement/manuscript/draft/figure1.tex
@@ -13,10 +13,10 @@
  node distance=7mm and 9mm]
  \node[box] (cand) {Additional candidates in the source database\\(n = ---)};
  \node[side, right=of cand] (unscr) {Unscreened on 31 December 2026\\(n = ---, by population group)};
  \node[box, below=of cand] (scr) {Screened by [-both authors, final decision\\recorded-]{+the first author and the AI screener;\\final decision recorded+} on or before 31 December 2026\\(n = {+---; pending at full text: n =+} ---)};
  \node[side, right=of scr] (excl) {Excluded, by code\\(n = ---; E2 and E3 by population group)};
  \node[box, below=of scr] (incl) {Included primary studies\\(records n = ---)};
  \node[side, right=of incl] [-(calib) {Calibration records, removed\\(n = ---; rounds = ---;\\small-pool rule applied: ---)};-]{+(agree) {Agreement of the two screeners per stage,\\and differences decided each way\\(Table~3 note; not the AI screener's accuracy)};+}
  \node[box, below=of incl] (main) {Main set\\records: n = ---\\studies, E5-linked records counted once:\\n = ---};
  \node[side, right=of main] (late) {Late stratum: included after\\31 December 2026, before main coding\\(n = ---; reported outside the primary counts)};
  \node[box, below=10mm of main] (expl) {Exploration set (reported separately)\\primary studies from the exploratory\\bibliography of 34 records: 10;\\item-coded instruments: 4};
@@ -25,7 +25,6 @@
  \draw[arr] (scr) -- (incl);
  \draw[arr] (scr) -- (excl);
  \draw[arr] (incl) -- (main);
[-  \draw[arr] (incl) -- (calib);-]
  \draw[arr, dashed] (unscr.east) -- ++(4mm,0) |- (late.east);
\end{tikzpicture}
\end{document}
diff --git a/papers/ai-fatigue-measurement/manuscript/draft/main.tex b/papers/ai-fatigue-measurement/manuscript/draft/main.tex
index 47503425..c5acd856 100644
--- a/papers/ai-fatigue-measurement/manuscript/draft/main.tex
+++ b/papers/ai-fatigue-measurement/manuscript/draft/main.tex
@@ -174,14 +174,17 @@ registration attachment.}
\subsection{Eligibility and screening}
Eligibility follows the source database. Both authors screened the 34 exploratory records. The additional candidates
were screened after registration by two independent screeners, the first author and an AI screener (Claude Opus,
Anthropic), at three stages: title and abstract, full text, and centre. [-The AI screener followed-]{+Both used+} registered [-instructions-]{+questions+} that turn the
eligibility criteria into seven [-questions, each-]{+questions with fixed decision rules; the AI screener+} answered {+each+} with the passage
that supports it,[-and-] saw only the instructions and the [-record;-]{+record from the screening database, and opened no web page. Work+}
{+went in batches of at most nine records;+} the first [-author did not see its judgement-]{+author's judgements+} of a [-record before recording-]{+batch were committed, with+} their [-own.-]{+time,+}
{+before the AI screener's output was opened.+} Where the two differed, the first author decided at that [-stage.-]{+stage, and the+}
{+final centre was always A or B.+} Before registration, the AI screener was
checked against the two human screeners' final decisions on the 34 exploratory records, with pass lines set in
[-advance:-]{+advance. After the first round met the lines, one question was clarified, which the pre-set rule did not call for, and+}
{+web access was then removed; with the registered instructions,+} it {+again+} passed on [-every record-]{+all 13 records+} that the humans included or left pending,[-and-] agreed
with them at full text {+on 32 of 34 records+} (kappa [-0.89)-]{+0.89),+} and {+agreed+} on the centre of [-every-]{+all 10+} included [-study.-]{+studies.+}
These records were used to refine the source database's criteria, so this accuracy may be optimistic. Only free full texts were used; records without one stayed pending.
Before registration the first author had screened 79 additional candidates after reading AI-generated preliminary
appraisals; all candidates were screened again, in a fixed order alternating between population groups, from a
database that showed no earlier judgement, and every decision is released.
@@ -233,8 +236,9 @@ the number of evaluable records, the number not evaluable and the number unresol
or absence in this set; they are not frequencies. Sensitivity analyses use peer-reviewed records only, remove records
with unconfirmed signs of overlap, count the secondary type of boundary items, and use each pass's values in turn.
In a fifth analysis, both authors screened again, at full text and centre, every candidate that either screener had
sent to full [-text,-]{+text by 31 December 2026,+} after the second author had read the manuscript draft; studies this added
were coded once, and the tables and problem statements were computed again. This screening was done with the results
known. {+\tbd{If it was not done: say so here and in the abstract.}+}

\section{Results}
\tbd{Written only after the tables have been generated from the code table, in the registered terms.}
@@ -284,8 +288,11 @@ additional candidates in their mix of studies; the screening by both authors is
results known. Before registration the first author had screened 79 additional candidates after reading AI-generated
appraisals, and may remember them. The person who decides eligibility is the coder, who knows the rules; the fixed
screening order, the AI screener's independent judgements and the released decisions show this influence but do not
remove it. {+The AI screener judged up to nine records in one call, and its instructions were written by the first+}
{+author, so its independence is of judgement, not of perspective.+} Only free full texts were used, and the source
database drew on free sources only, so the main set is not a census and its proportions are not estimates for the
literature. {+Before registration, human screening was uneven across population groups; all candidates were screened+}
{+again in an order that alternates between groups.+}

The eligibility criteria shape some outcomes. Studies with no relation to AI are excluded, so the value of no
attribution to AI (C1, L6) is truncated; and the fatigue definition includes motivational depletion, so the share of
@@ -297,7 +304,9 @@ C6a and the third condition of C7 compare names. A conclusion coded within what
conditions; it is not shown that the items support it. Coding was done by one person in two passes, so the agreement
reported shows how consistently one coder applied the rules, not whether another person would apply them in the same
way; the coder wrote the earlier narrative review, and the codes carry that view. The exploration set was used to
build the rules and for calibration, and its tables are calibration [-material.-]{+material; calibration agreement may be higher than+}
{+agreement on new studies, and amended definitions were not checked before main coding. No second person checked the+}
{+numbers; result values were copied into the manuscript by script.+} \tbd{Limitations added by
deviations from the registration, if any.}

\section{Conclusions}
diff --git a/papers/ai-fatigue-measurement/manuscript/draft/tables.tex b/papers/ai-fatigue-measurement/manuscript/draft/tables.tex
index 6be97f3b..bd83c29a 100644
--- a/papers/ai-fatigue-measurement/manuscript/draft/tables.tex
+++ b/papers/ai-fatigue-measurement/manuscript/draft/tables.tex
@@ -59,9 +59,16 @@ Set & Records & Studies (E5 counted once) & Instruments & Six population groups
Main set & --- & --- & --- & --- & --- \\
Late stratum & --- & --- & --- & --- & --- \\
Exploration set & --- & --- & --- & --- & --- \\
{+Pending at full text on 31 December 2026 & --- & & & --- & \\+}
Unscreened on 31 December 2026 & --- & & & --- & \\
\bottomrule
\end{tabularx}

{+\smallskip+}
{+\raggedright\footnotesize A note gives, for each screening stage, the agreement between the first author and the AI screener+}
{+(percentage and kappa), the records each sent on, the differences decided as each had judged, and the records judged+}
{+boundary at the centre stage, all of which the first author assigned to centre A or B. This agreement is not the AI+}
{+screener's accuracy.+}
\end{table}

\begin{table}[!htbp]
@@ -84,8 +91,9 @@ Records coded in one pass only & --- & & & --- & & & --- & & \\
\smallskip
\raggedright\footnotesize Calib., calibration passes on the exploration set; Explor., exploration set coded again under the final rules.
Kappa with a bootstrap 95\% confidence interval. Both passes are by the same coder, at least four weeks apart, so this
is agreement within one coder, not between coders. {+The calibration studies had been read and partly coded by the coder+}
{+while building the rules, so calibration agreement may be higher than on new studies.+} Agreement with the AI draft is
agreement with a draft, not with a correct value.
\end{table}

\begin{table}[!htbp]
@@ -268,7 +276,8 @@ One row per row of Table 12 & --- & --- & --- & --- & --- & --- \\
\smallskip
\raggedright\footnotesize Analysis 3 applies to the C2b tables and is reported beside Table 7. Analysis 5 uses the main set
as decided by both authors after the manuscript draft, with the results known; the numbers of studies it added and
removed are given in a [-note.-]{+note, and the record-level tables of the main set under analysis 5 are in the supplement.+}
{+If analysis 5 was not done, its column is empty and the note gives the reason.+}
\end{table}

\begin{table}[!htbp]
diff --git a/papers/ai-fatigue-measurement/manuscript/outline.md b/papers/ai-fatigue-measurement/manuscript/outline.md
index c8b3ff0b..d59d933f 100644
--- a/papers/ai-fatigue-measurement/manuscript/outline.md
+++ b/papers/ai-fatigue-measurement/manuscript/outline.md
@@ -78,14 +78,17 @@ manuscript:
  twice, at least four weeks apart (GSRR-44). The agreement reported is between two passes of one coder, not between
  coders, and no claim of independent coding is made. The coder wrote the earlier narrative review, so the codes carry
  that view of what counts as a problem (GSRR-46).
- The main set is the set of studies included by 31 December 2026 {+after screening+} by[-two independent screeners,-] the first author and an AI
  [-screener whose accuracy was checked against human decisions before registration;-]{+screener, each on their own;+} the first author decided where they differed (GSRR-33, [-GSRR-37,-]{+GSRR-38,+} GSRR-39). {+The AI+}
{+  screener was checked against human decisions on records that had been used to refine the criteria, so its accuracy+}
{+  may be optimistic (GSRR-37). Only free full texts were used; records without one stayed pending and were not coded+}
{+  (GSRR-65).+} It does not rest on two human screeners; the screening by both
  authors after the manuscript draft is a sensitivity analysis, done knowing the results (GSRR-62). The set was drawn
  from one literature database built from free sources, and the first author, who screened it, knew the coding rules;
  before registration, the first author had screened 79 of the additional candidates after reading AI-generated
  appraisals (GSRR-34, GSRR-65). {+Human screening before registration was uneven across population groups; all+}
{+  candidates were screened again in an order that alternates between groups (GSRR-33).+} It is not a census of the
  literature on AI and fatigue. Every claim about the main set is about that set.

## Relation to the authors' earlier narrative review

@@ -131,7 +134,8 @@ validity evidence.

The released materials (the code table with codes, item numbers and source pages but no item text; the screening
decisions made after registration; the scripts) are the means by which the tables can be recomputed and the scheme
[-reused.-]{+reused; whether other people apply the scheme in the same way has not been tested.+} They are not claimed as new
findings. The tables can be recomputed from the code table; checking the C2b codes
themselves requires the original instruments at the pages given.

## Rule for the abstract
@@ -142,7 +146,8 @@ the main set only:
- one sentence on the scope of the set, which is never removed: a set drawn from one literature database built from
  free sources, screened by the first author and an AI screener, closed on 31 December 2026, and not a census of the
  literature; with the number of studies and instruments coded and the number of candidates still unscreened on that
  date; {+if any problem statement changes when both authors screen the set (sensitivity analysis 5), or if that+}
{+  screening was not done, the sentence says so (GSRR-62);+}
- how the coding was done: by one coder, the first author, twice;
- the three things TRACE links, each with counts and no evaluative word: the distribution of the representative level
  of attribution (C1); for the instruments first seen in the main set with printed items, for each
@@ -374,12 +379,17 @@ columns; no value is filled in before coding.
  | Main set | — | — | — | — | — |
  | Late stratum | — | — | — | — | — |
  | Exploration set | — | — | — | — | — |
  {+| Pending at full text on 31 December 2026 | — | | | — | |+}
  | Unscreened on 31 December 2026 | — | | | — | |

  {+A note gives, for each screening stage, the agreement between the first author and the AI screener, the records+}
{+  each sent on, the differences decided each way and the records judged boundary (GSRR-37); this agreement is not+}
{+  the AI screener's accuracy.+}

- Table 4: agreement between the two coding passes of one coder per code (percentage agreement, kappa with bootstrap
  95% CI, n), with the calibration passes, the main set and the exploration set in separate columns; the C4f agreement
  with the AI draft; records coded in one pass only. The heading states that this is agreement within one coder
  [-(GSRR-44).-]{+(GSRR-44), and a note that calibration agreement may be higher than on new studies (GSRR-65).+}
- Table 5: C1 representative level (L1a, L1b, L2, L3, L4, L5, L6, excluded values), count and, where allowed,
  proportion.
- Table 6: C2a origin, modification (per kind: stated / found by comparison / no change / not verifiable) and format;
@@ -410,7 +420,9 @@ columns; no value is filled in before coding.
  that made records not evaluable (GSRR-57).

- Table 13: sensitivity analyses (problem statements as in Table 12, with C7 by condition), with analysis 5 (main set
  decided by both authors after the draft) in its own columns and the number of studies it added and [-removed.-]{+removed; the+}
{+  record-level tables under analysis 5 go in the supplement. If analysis 5 was not done, its column is empty with the+}
{+  reason (GSRR-62).+}
- Table 14: recommendations.

  | Recommendation | Code | Row of Table 12 | Source: existing standard (cited) or proposal of this scheme | Question → what is measured → evidence needed → wording allowed (proposal) |
