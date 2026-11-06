# Outline — per-person learning in sequence models of keystroke logs

Status: Step 1 draft (claims and novelty), 2026-11-07. Target: User Modeling and User-Adapted Interaction (empirical research paper). Numbers are aggregated values (medians over writers) from the four analyses that make up the frozen scope of this paper. No new analyses enter this paper.

## Take-home sentence

When a per-person sequence model is compared with a pooled model of the same structure, its advantage depends on that structure: with a three-state hidden Markov model the per-person fit gains up to +0.19 nats per symbol, but when the structure and the shrinkage strength are both selected on other people, an autoregressive HMM is chosen everywhere and the per-person gain falls to about 0.001 nats per symbol or less (CoAuthor) and to exactly zero (CS1).

## Contributions

C1. The per-person advantage is a property of the comparison, not only of the people.
- Type: re-examination of an established kind of claim (that personal models beat general models), with a partial reversal.
- Compared with: studies that report personal models outperforming population models for behavioral data (cross-dataset behavior modeling; idiographic versus nomothetic modeling; keystroke-based user modeling). Citations to be settled in a literature round (see "Open items").
- Evidence: main table (per-person minus same-structure pooled, by number of training sessions k, for hmm3 and the two-stage selection). CoAuthor 15-session panel: hmm3 +0.188 (k = 5), +0.165 (k = 15); two-stage selection: +4.1e-4 to +7.2e-4 for k = 1 to 15; CS1: 0 at every k because infinite shrinkage is selected.
- Strength: established for these two datasets and this 26-symbol quantization; conditional beyond them. The two-stage CoAuthor differences (about 1e-3 or less) are of the same order as the numerical drift allowed in the reproduction checks, so they are reported as "no material per-person gain", not as a small positive gain. Exception reported as a value only: CoAuthor 9-person panel, ar1 at k = 20 and 30 (+0.003 and +0.005), with interior shrinkage selected.

C2. A structure that conditions on the previous symbol outperforms each person's own first-order Markov baseline, whereas the per-person three-state HMM does not.
- Type: new measurement (baseline comparison that is usually omitted).
- Compared with: evaluations of personal HMMs against pooled HMMs only.
- Evidence: per-person minus own first-order Markov chain. hmm3: about −0.5 (CoAuthor) and about −1.1 (CS1), negative for all or all but one writer. Two-stage selection (AR(1)-HMM, K = 3): positive for every writer at every k; +0.220 at k = 1 to +0.020 at k = 15 (CoAuthor), +0.050 to +0.029 (CS1).
- Most of the advantage over the first-order Markov baseline comes from the pooled structure rather than from the per-person fit; the pooled model's advantage over that baseline is largest with few training symbols and shrinks with k (for the CoAuthor 9-person panel, ar1 at k = 30, the pooled model falls below it).
- Strength: established for these data. The reading that the per-person HMM was compensating for missing short-range dependence is consistent with C1 and C2 but was not tested (two structure families, one quantization).

C3. An evaluation protocol for per-person gains: select structure and shrinkage strength on other people, extend the shrinkage grid to its limits (up to 10^6 and the pooled limit) so that the selection does not sit on the grid boundary, and report per-person minus same-structure pooled alongside per-person minus own first-order Markov.
- Type: method (procedure), offered as a reusable check rather than as a new estimator.
- Compared with: hierarchical / partial-pooling practice in which the pooling strength is tuned on the same person or fixed.
- Evidence: on the shorter grid (up to 10^4) the selected shrinkage sat on the upper boundary. With the grid extended to 10^6 and the pooled limit, every CS1 writer selected the pooled limit for ar2 and ar3 (all k), so the boundary pile-up had indicated that full pooling is best, not that the grid was too short (the pooled limit beats 10^6 by at most 2.4e-4). For CoAuthor with ar structures and few training symbols the selection still sits at 10^6, and the gap between 10^6 and the pooled limit is about 1e-3 or less; for ar1 with many training symbols (k ≥ 8) interior values are selected. The structure selected in the two-stage procedure did not change.
- Strength: demonstrated on two datasets; generality of the procedure is argued, not tested.

Supporting result (not a separate contribution; supplementary tables): for CoAuthor with the autoregressive structure at large shrinkage (10^5 and above), the small remaining difference from the pooled model is, comparing medians, larger in the gap between the prior mode and the pooled parameters than in the contribution of the person's own data. This is a median comparison, not a per-writer decomposition, and does not apply to CS1.

Supporting result 2 (supplementary; one paragraph in the main text): logistic models on a proxy label. The per-person model's advantage over other people's base rate and over the pooled model is not an advantage over the person's own base rate (per-person minus own base rate is near 0 at every k), and shrinking coefficients toward the person does not raise within-writer discrimination above pooled coefficients with a per-person intercept. The label is an event of AI-assisted writing (CoAuthor) or completion acceptance (CS1), with about six evaluation questions per writer in CoAuthor; it is not read as being stuck or as any cognitive state.

## Out of scope (stated once, in the limitations section)

- The hidden states are not given names and are not read as cognitive or affective states; better prediction of the 26-symbol sequence is short-range sequential dependence, not structure of mental state.
- Sessions and assignments are not days; results are not extended to other languages, input methods, or other populations of writers or programmers.
- No thresholds or significance tests are used; all numbers are descriptive medians with interquartile ranges and the share of writers favouring the per-person fit.

## Open items before Step 2

- Literature round: studies that claim personal-over-general gains for behavioral or keystroke models, and the partial-pooling literature that C3 is compared with. Novelty claims in C1 and C3 stay provisional until then.
- Preprint policy of the target journal (not yet read in the primary source).
