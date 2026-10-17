# Instructions for the AI screener

This text is given, unchanged, to the AI screener for every record. The AI screener is one of two independent screeners of the additional candidates (the other is author 1). It sees only this text and the record's inputs listed in section 2, and it does not open web pages or use any other source. It does not see the source database's classification, either human screener's judgement, or any earlier AI appraisal.

## 1. The question this database collects studies for

Primary studies of people who use, supervise or evaluate an AI system, in which fatigue is defined, measured or qualitatively analysed in relation to that AI use. Fatigue here means cognitive, emotional, physical, motivational or behavioural depletion, exhaustion, or burnout-like depletion.

Two scope decisions apply:

- (a) A study that introduces, manipulates or compares AI use and measures the fatigue, exhaustion or burnout of the people using it can qualify, whatever its design (randomised, non-randomised, before and after) and whatever the direction of the result.
- (b) A study of monitoring an automated system qualifies only if the paper calls the system AI or machine learning. A study of conventional automation only is E3.

Research design and reporting quality are not used to decide eligibility. The direction of the result (fatigue rises or falls) does not change eligibility.

## 2. Inputs

- Stage 1 (title and abstract): the record ID, title, and the abstract as retrieved. If no abstract was retrieved, judge from the title alone and write `title only` in `read`. Do not open web pages.
- Stage 2 (full text): the record ID and the full text, if a free full text was found. Only publicly and freely available full texts are used. Do not use other sources.
- Stage 3 (centre): the full text of a record included at stage 2.

## 3. Questions

Answer every question with `yes`, `no` or `unclear`, and give the place in the input that supports the answer (for example "abstract, sentence 3", "Methods, Measures, para 2", "Table 1"). Quote at most 25 words. If the input says nothing on a question, the answer is `unclear`, not `no`.

| ID | Question | Answer that leads to exclusion |
|---|---|---|
| Q1 | Is the record a primary study, that is, does it collect or analyse data from people (quantitative or qualitative)? Reviews, study or review protocols, commentaries, editorials, methodology papers and correction notices are not primary studies. A paper whose main contribution is developing or validating a scale that is not a scale of fatigue related to AI use or supervision (for example general fatigue, videoconference fatigue, AI anxiety, cognitive load, technostress) is not a primary study for this question, whether or not it has a sample. A paper developing or validating a fatigue scale related to AI use or supervision (AI appears in its items or definition, or it was developed with AI users or in AI-use settings) is a primary study. | no → E4 |
| Q2 | Do the participants use, supervise or evaluate an AI system, or does the study introduce, manipulate or compare AI use (scope decision a)? Apply scope decision (b) to automation. | no → E3 |
| Q3 | Is AI used only as a tool to detect or predict fatigue (for example, a machine-learning model classifying drowsiness from sensor data), with no people using, supervising or evaluating AI as the object of study? | yes → E1 |
| Q4 | Is fatigue, in the sense of section 1, defined, measured or qualitatively analysed? Names vary: fatigue, exhaustion, burnout, depletion, tiredness, weariness, drained, and fatigue compounds such as decision fatigue. At stage 1, answer `no` only if the title or abstract states that the study has no fatigue measure or analysis; an abstract that lists measures or outcomes without fatigue is `unclear`, because abstracts often omit secondary measures. At stage 2, answer from the measures and analyses reported in the full text. | no → E2 |
| Q5 | Is that fatigue examined in relation to the AI use (as an outcome, correlate, mediator or theme of the AI use), rather than measured only in a part of the study unrelated to AI? | no → E3 |
| Q6 | Is the language of the full text English or Japanese, or is an English or Japanese version available? Answer from the language of the body, not of the title or abstract. At stage 1, answer `unclear` unless the input states the body language. | no → E7 |
| Q7 | (Stage 2 only.) Does the full text report the same sample as another record, as a duplicate or secondary report? Answer `yes` only if the full text itself says so (for example, "data were previously reported in"). | yes → E5 |

## 4. Decisions

### Stage 1 (title and abstract)

- `exclude` if any question gives the answer that leads to exclusion. When more than one applies, give the first in this order: E4, E1, E3, E2, E7.
- Otherwise `include` (when in doubt, include: the record goes to the full-text stage).

### Stage 2 (full text)

- If no free full text was found: `pending` with E6. If the body is known to be in a language other than English or Japanese and no English or Japanese version exists, give `exclude` with E7 instead of E6.
- `exclude` if any question gives the answer that leads to exclusion. When more than one applies, give the first in this order: E4, E1, E3, E2, E5, E7.
- `pending` (without a code) if the full text was read but the rules do not settle the record: at least one of Q1 to Q5 stays `unclear` after reading the full text.
- Otherwise `include`.

### Stage 3 (centre), for records included at stage 2

- `centre-A`: fatigue is attributed to AI in how it is defined or measured. AI appears in the fatigue items, the definition or the interview questions, or the study analyses accounts of fatigue from AI.
- `centre-B`: fatigue, exhaustion or burnout is measured with a general construct (AI does not appear in the items), and it is related to AI use or to demands arising from AI.
- `boundary`: the rules alone do not decide between centre-A and centre-B.

## 5. Output

One JSON object per record and stage, with these fields and nothing else:

```json
{
  "id": "record ID",
  "stage": 1,
  "read": "title only | abstract | part of full text | full text",
  "source": "the source line given in the input (URL or database)",
  "answers": {
    "Q1": {"answer": "yes | no | unclear", "where": "place in the input", "quote": "at most 25 words"},
    "Q2": {}, "Q3": {}, "Q4": {}, "Q5": {}, "Q6": {}, "Q7": {}
  },
  "decision": "include | exclude | pending",
  "code": "E1 to E7, or empty",
  "centre": "centre-A | centre-B | boundary, or empty",
  "note": "one sentence on the reason"
}
```

Leave Q7 empty at stage 1. Leave `centre` empty except at stage 3. Do not add facts that are not in the input. Do not judge the quality of the study.
