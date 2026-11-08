## Review of the stall-shape multiverse manuscript, round 5 (reviewer R1)

Role: a JEDM reviewer from the tradition of keystroke logging and measuring writing and programming processes, with a sceptic's sub-voice asking whether the measure really measures what it claims. I am writing as "a reviewer in this position", not as any real person. Nothing was written to disk.

### 1. Grounding: standards taken from the two papers, quoted verbatim

- **G1. The threshold must account for typing facility, because counts and durations carry typing speed.**
  - Guo et al. 2020 (guo2020.txt l.302–305): "A personalized threshold was necessary, rather than a single fixed threshold for all students, because students vary widely in their typing facility. Because they laboriously enter text letter by letter, poor typists may have many long pauses between keystrokes that are not indicative of planning behavior."
- **G2. The position of a behaviour within the session matters.**
  - Guo et al. 2020 (l.2214–2217): "our current modeling methods do not address the fact that writing behaviors, such as editing, may change in probability and contribution to essay quality over the course of a writing session".
- **G3. Heuristic labels need external evidence, and generalisation needs replication.**
  - Guo et al. 2020 (l.2201–2204): "we used relatively simple heuristics to define our writing states ... Further research that combines think-aloud protocols and other sources of evidence with keystroke logging might enable us to build even more effective classification procedures".
  - Guo et al. 2020 (l.2210): "results may not necessarily generalize to a broader population or to different conditions so replication with other conditions and participant samples is typically recommended."
- **G4. Feature consistency across settings comes first.**
  - Li & An 2026: "establishing feature consistency is an initial first step ( Guo et al., 2018 ), where consistency refers to the extent to which feature properties behave similarly across settings."
- **G5. A long pause is not the same as a cognitive state.**
  - Li & An 2026: "imagine that a student paused 10 s when he was spelling “pen.” This does not reflect he had major cognitive difficulty on spelling. This happens simply because he stretched; or he was distracted".
- **G6. Report the reliability of the outcome.**
  - Li & An 2026: "Inter-rater reliability, measured by Krippendorff’s alpha ( Hayes and Krippendorff, 2007 ), was 0.92, indicating high agreement."

### 2. Carry-over findings from round 4

- **m1: resolved.** "raised half of the pause definitions above +0.1" now appears in the abstract (l.13–14), introduction (l.37–38), discussion (l.7–8), conclusion (l.7–8) and Table 5. 9 of 18 matches the table's 0/6/9/3.
- **m2: partly resolved.** Table 2's note and the body now say "default and precedented". But the old term survives: discussion.tex:10–11 "Within levels in use, our result resembles…" and conclusion.tex:6 "on levels in use its size moved". Table 2's own note says the default window and condition "have no use outside the detector", so "levels in use" contradicts it (see N2).
- **m3: resolved.** κ 0.60 / 0.76 is in methods l.16 and limitations l.36–37, together with the attenuation towards zero.
- **m4: resolved.** Results l.250–252 limit the φ finding to two CS1 cells and add that φ "does not show which assumption of a count model fails". The abstract still says "within-writer overdispersion also moved with the definition" without the scope, but the introduction and conclusion carry it, so I treat this as acceptable.
- **m5: resolved.** Limitations l.40–42 cover planning early, review or waiting late, and say the positive corner cannot be told apart from that route. This answers G2.
- **n1: resolved.** Results l.146–147 now separate speed ("every stall interval lay below zero") from length ("no point value was negative and 54 intervals lay above zero").
- **n2: resolved.** Table 5's column header and discussion l.21 both say "exploratory".
- **n3: resolved.** Table 2's note says "12 definitions, including the baseline".

### 3. Scores a–f

- **a. Fit to JEDM's scope and contribution: 4.** The paper gives a methodological map plus a reporting convention, which fits the "generalizable methodologies" requirement. The reading of the range is proposed after seeing the results, and the paper says so.
- **b. Validity of method and measurement: 4.** Against G1, the paper now has a key-press-rate control, six speed measures and a pause family. CS1 is converted from edit events and pastes are dropped (S2), which is disclosed. The length adjustment overlaps the label by construction, which is acknowledged in results l.135–136 and limitations l.38–39.
- **c. Agreement between claims and evidence: 3.** The numbers check out against score.csv. My spot checks all matched:
  - 10 definitions with a positive interval, all W = 15 s with a writer quantile;
  - 48/17/2/22 unadjusted, 0/74/1/14 given length, and 71 below −0.1 given speed;
  - 54 positive intervals given length, with 35 including zero.

  The weak points are in the summary sentences (N1, N2, N4).
- **d. Status labels (prespecified / added / exploratory / descriptive): 3.** S1 is careful. But the abstract and introduction put a descriptive result inside a sentence that opens "By criteria set before the computations" (N3).
- **e. Reproducibility: 4.** Code, conditions and aggregate tables are released, and the 20 mutants and selftests are recorded. Two gaps: the conditions are in Japanese with an English summary still to come, and the DOI is not yet there.
- **f. Writing and length: 4.** The arithmetic of the reading table is correct, but the rule and the summaries disagree about what "imprecise" is (N5).

### 4. New findings

**N1 [minor]: the abstract says the CS1 rate ratio "moved", although by the paper's own criterion it did not reach the threshold.**
- Where: abstract.tex:14–15 "Rate ratios between the programming editions and within-writer overdispersion also moved with the definition".
- Compare:
  - results.tex:190–191 "20 of 89 definitions (22%) reversed the ratio, below the 25% we had set";
  - methods.tex:196–197 "did not reach it";
  - introduction.tex:40–41 and conclusion.tex:8–9, which both add "below a criterion".
- Why it matters: in the abstract alone, the paper's own verdict is replaced by a bare "moved", which makes the claim stronger than the evidence. Against G4, a reader would take this as a lack of consistency across settings.
- To resolve: write in the abstract "reversed for 20 of 89, below a criterion set after seeing point values", or the same wording as the introduction.
- Confidence: high.

**N2 [minor]: the discussion and conclusion summarise the precedented grid as "only the size moved", but among precedented fixed pause thresholds the direction changed too. The term "levels in use" also remains (the m2 residue).**
- Where:
  - discussion.tex:4–6 "on the grid of default and precedented levels it was negative or negligible, and what moved there was its size and, among fixed pause thresholds, its presence";
  - conclusion.tex:5–6 "for stalls its direction changed only where a 15-s window met a writer quantile, and on levels in use its size moved; for pauses the values were mostly negligible";
  - discussion.tex:10–11 "Within levels in use".
- Evidence against: results.tex:26–29 says the pause intervals were above zero at 2 s and 5 s and below zero at 10 s, so "The direction therefore changed". Methods l.145–146 gives 2–10 s as "within the range used in writing", which makes these precedented levels. The abstract (l.12–13) does say "the direction changed between them", so the abstract and the discussion/conclusion disagree.
- Why it matters: the closing narrative becomes "direction changes only at a non-precedented corner". For the pause detector that is false (although the flips are between negligible values).
- To resolve:
  - make the summary sentences in the discussion and conclusion read "for pauses the direction changed between mostly negligible values";
  - replace "levels in use" with "default and precedented levels".
- Confidence: high.

**N3 [minor]: a descriptive result sits inside a sentence that claims a prespecified criterion.**
- Where:
  - abstract.tex:9–12 "By criteria set before the computations, ... its direction changed: it was positive only for ten definitions ... and on a grid of default and precedented levels it was negative or negligible. Among fixed pause thresholds the values were mostly negligible";
  - introduction.tex:33–37 has the same structure.
- Why it matters: methods.tex:199 says "Sizes, the reading by classes of interval and the grid of default and precedented levels were set after seeing the results". S1 labels them "[D]". "Negative or negligible" on the precedented grid, and "mostly negligible", are both sizes on a post-hoc grid. As written, a [D] statement reads as if a prespecified criterion established it.
- To resolve: split the sentence so that "By criteria set before" covers only presence and direction, and attach "(descriptive, after seeing results)" to the precedented grid and to the sizes.
- Confidence: medium-high.

**N4 [minor]: the main results do not state that the "positive corner" (the 10 definitions with W = 15 s and a writer quantile) becomes negative for all 10 once typing speed is adjusted.**
- Where: results.tex:16–23, discussion.tex:16–24, limitations.tex:40–42.
- Evidence: in figdata/score.csv, rows i = 81–90 are the definitions with a positive interval. Their adjusted intervals ("ahi") are all below zero, e.g. i = 90: adj −0.0343 [−0.0627, −0.0055]. Results l.140–141 only gives the total, "for all 89".
- Also: one of the 10 barely excludes zero (i = 81: lo = 0.0020), and S2 drops the count to 9 in the restricted time.
- Why it matters: G1 is the concern the field's standard puts first, namely that counts carry typing facility. The headline "direction changed" rests on these 10. Limitations names only the position-in-session route, so the more direct route is not stated: a writer-quantile θ is short for fast typists, and with W = 15 s the stall behaves more like a pause rate and so tracks the rate of key presses.
- To resolve:
  - add one sentence to results 4.1 or 4.2 that the 10 positive definitions all fall below zero given speed (exploratory);
  - add to limitations that the corner may follow speed through the writer quantile;
  - optionally note the margin of i = 81.
- Confidence: medium. The mechanism is not tested, but the numerical fact is certain.

**N5 [minor]: the four-class reading listed in the abstract, introduction and conclusion does not match the rule in the discussion.**
- Where:
  - abstract.tex:17–18, introduction.tex:48–49 and conclusion.tex:12–13 name four readings: "consistent, negligible, dependent on the definition or imprecise";
  - discussion.tex:45–48 "Report a consistent direction or a negligible association when one class holds at least 90% of the classified definitions, report that the conclusion depends on the definition otherwise, and give the number of imprecise intervals in either case";
  - S1 l.60 "imprecise intervals counted apart".
- Why it matters: the rule never produces "imprecise" as the reading of a range. It is only a count reported alongside. The rule is also undefined when every definition is imprecise. A reader trying to apply the proposal cannot tell when to report "imprecise".
- To resolve: either say in the summaries "read as consistent, negligible or dependent, with the number of imprecise intervals", or add to the rule a condition under which a range reads as imprecise (for example, imprecise intervals above some share).
- Confidence: high.

**N6 [minor]: the post-hoc 90% rule sits on a knife-edge in Table 5.**
- Where: results.tex:168, "Stalls, full grid (89) ... Given speed (exploratory) depends: 71/8/0/10".
- Why it matters: 71 / 79 = 89.9%, just under 90%. One more definition moving from negligible to below −0.1 would change the reading to "below". The rule was set after seeing the results ([D]). Showing only the class label makes the reading look sturdier than it is.
- To resolve: show the share of the leading class in Table 5 (e.g. 89.9%), and note in the discussion that the reading is sensitive near the threshold.
- Confidence: high.

**N7 [nit]: the same word "below −0.1" is counted two ways.**
- Where: results.tex:21–22 "58 definitions gave a negative correlation of at least 0.1 in absolute value" uses point values; Table 5 gives "48" below −0.1 using intervals.
- Why it matters: both are correct (score.csv rows 1–58 vs rows 1–48), but a reader will look for the discrepancy.
- To resolve: add "(point value)" and "(whole interval)" at each place.
- Confidence: high.

### 5. Overall recommendation: minor revision

- The numbers agree with the result files. The carry-over findings are resolved except m2, which is partly resolved. The measurement problem the field cares about first (G1, typing facility) is addressed with controls and adjustments.
- The remaining problems are in the summary sentences: the abstract leaves out the paper's own criterion verdict (N1), the summaries miss that the pause direction changed on precedented levels (N2), status labels are mixed in one sentence (N3), and the four reading classes do not match the rule (N5). None needs a new computation.
- The explanation of the positive corner by speed (N4) and the knife-edge of the reading (N6) can be handled by stating them.

### 6. Not read, and suspected injection

**Not read:**
- guo2020.txt lines 2011–3656. I read only 2200–2250 (the limitations) via grep, so the appendix and later references were not read.
- From the supplement, only lines 1–210 of supplement.tex. Not read: the rest of supplement.tex (S3 onwards), tab_s3.tex, tab_s4.tex, tab_pause.tex.
- main.tex, related.tex (apart from grep hits), availability.tex, declarations.tex, references.bib and main.pdf (the figures were not checked visually).
- Of the figure data, only score.csv. Not read: ratio_cs19_kl.csv, ratio_cs19_cs21.csv, phi.csv, lengths.csv.
- All of conditions*.md and results/*.json. In particular, I did not cross-check the 3/5/0/4 for the default-and-precedented grid in Table 5 against round9_classes.json.

**Suspected injection:** none in the range I read.