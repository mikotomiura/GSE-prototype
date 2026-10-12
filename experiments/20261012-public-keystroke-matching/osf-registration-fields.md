# OSF の registration の各欄の文面（凍結のときに使う・未登録）

作成 2026-10-12。2026-10-13 に判断 51 を反映した。同じ日に、**OSF の現行のテンプレート「OSF Preregistration」v4 の設問に組み直した**。前の版は古い版の欄を想定していて、v4 とずれていた（研究者の指摘）。設問・必須の印・選択肢は、OSF の API の一次で確かめた。

- テンプレートの一覧: `https://api.osf.io/v2/schemas/registrations/`。「OSF Preregistration」は id `697b72f611a8e98484c6139b`・schema_version 4・active。
- 設問: `https://api.osf.io/v2/schemas/registrations/697b72f611a8e98484c6139b/schema_blocks/`（87 ブロック）。

登録は研究者が自分のアカウントで行う（Claude はログインしない・判断 25）。

## 使い方

- **テンプレートは「OSF Preregistration」（v4）を選ぶ。** 既存のデータ向けの「Secondary Data Preregistration」もある。ただ、v4 には「Foreknowledge of data or evidence」の設問があり、既存のデータの事前の知識をそこで申告できる。だから v4 で足りる。
- 下の **[必須]** は v4 で required の欄。必須でない欄も、文面がある所は埋める。
- 文面は英語の版（論文用のリポジトリの `preregistration.md`）の節の名前を引く。添付するファイルの名前も、リポジトリの名前（`preregistration.md`）にそろえる。
- **ファイル**: `C:\keystroke-log-release-matching` の `preregistration.md`・`config.json`・`SEED`（コミット `cf5353da`・判断 53 の後）。v4 のファイルの欄は Study design・Data collection procedures・Manipulated variables・Measured variables・Indices・Statistical models の下にある。
  - `preregistration.md` は Study design の欄に添付する。
  - `config.json` と `SEED` は Statistical models の欄に添付する。1 つの欄に 1 ファイルしか付けられなければ、`SEED` は Indices の欄に付ける。
  - 登録の後にファイルを差し替えない。差し替えると「Other」の SHA-256 と合わなくなる。
- 凍結は KLiCKe の著者の返事を待たない（判断 51 が判断 49 を改めた）。

---

## Metadata の段（テンプレートの外）

**Title**

How far do processing steps applied to public keystroke logs protect against matching logs to texts?

**Description**

Keystroke logs of writing are released publicly with processing intended to hide the texts, such as masking letters and digits. Because the texts often exist elsewhere, an attacker can try to match a released log to its text among candidate texts. This study measures how far release forms (the masking used in practice and alternative forms: key categories, dropped position and word count, merged separators, rounded times, coarsened segment values, suppression, substitution and permutation) protect against matching attackers that know the processing, on the public KLiCKe corpus of English argumentative essays and on the public ENJA15 corpus of Japanese translations typed with an input method. Accuracy is reported against the chance level 1/N and against an attacker that uses only total length, together with how far standard process measures of writing research remain computable after processing. No pass or fail criterion is set. The full plan is in the attached preregistration.md, with all parameter values in config.json and the random seed in SEED.

**License**: CC-By Attribution 4.0 International（論文用のリポジトリの `LICENSE-DOCS` とそろえる）

**Subjects**（bepress の分類・画面の一覧で名前を確かめる）: Physical Sciences and Mathematics → Computer Sciences → Information Security（主）／ Arts and Humanities → Rhetoric and Composition（副）

**Tags**: keystroke logging / privacy / data release / de-identification / re-identification / linkage attack / writing process / preregistration / keystroke dynamics

**Contributors**: 研究者だけ。**Affiliated institutions**: 空（所属なし・判断 7）。

---

## 1. Overview

**Research questions or hypotheses** [必須]

No confirmatory hypothesis is tested; the study is descriptive. The questions are:
(1) How far do the processing steps used in public releases of keystroke logs, and alternative processing steps, protect against attacks that match a released log to its text among N candidate texts? Accuracy is reported against the chance level 1/N and against an attacker that uses only the total length of the log (A0).
(2) How does the protection change with the columns that are kept (position, word count, separators, times) and with the attacker?
(3) After processing, how far can the standard process measures of writing research still be computed, and how closely do they agree with their values before processing?
(4) On Japanese translation logs typed with an input method (ENJA15), how far above 1/N and above A0 is the accuracy of the same kind of matching? The word "exceeds" is used only when the lower bounds of the 95% intervals of both differences (to 1/N and to A0) are above 0.
Predictions written before any data were acquired are in the section "Predictions" of preregistration.md; a miss does not change the conclusions.

**Foreknowledge of data or evidence** [必須・1 つ選ぶ]

推奨: **「Authors' limited observation of the data could not influence their analysis decisions.」**

理由: KLiCKe の記録・本文・得点は 1 つも開いていない（KLiCKe だけなら「Data exists but the authors have not observed it yet.」に当たる）。一方、ENJA15 は 2026-09-13 に別の目的で 1 ファイル（`P01_T1.xml`）を取得し、イベントの種類の数を数えた。その他に見たのは、KLiCKe のフォルダの構成（ファイル名と数）と、Kaggle の記録の説明だけである。1 つの選択でデータ全体を申告するので、見たことのある分を含む方を選ぶ。「not observed」を選ぶと、ENJA15 の 1 ファイルについて言い過ぎになる。

**Explanation of foreknowledge and managing unintended influences**

KLiCKe (the main dataset): no log, text or score has been downloaded or opened. Only the corpus paper, the README of its GitHub repository, the terms-of-use page and the structure of its file folder (file names and counts) were read. ENJA15: one file (P01_T1.xml) was downloaded on 2026-09-13 for an unrelated purpose (whether input-method conversion is recorded in public data), and only its event types were counted; no quantity related to matching was computed, and that file is not used. Also read: the description page, rules and first-place solution write-up of a related Kaggle competition (no data values), and the description and file list of the public KeyTAR artifact. Three earlier prototypes (Japanese text, synthetic input and the researcher's own logs) gave the segment rule, the alignment and the penalty λ = 8; their numerical results are not used as values or as grounds for predictions here. Before fixing, all procedures were checked on synthetic logs generated by our code without human data, and the forms and rules were revised in response; the revisions are listed in the section "What was seen before this registration was fixed (disclosure)" of preregistration.md. After acquisition, only the checks 1 to 7 listed in the section "Checks after acquisition and before the main computation" are done before the main computation, and any change after fixing is recorded as a deviation with the results before the change.

## 2. Research Design

**Study type** [必須・複数選択可]

推奨: **「Descriptive study」と「Simulation study」の 2 つ。**

理由: 既存の公開データで、加工の形ごとの照合の正答率と有用性の指標を記述する研究である（Descriptive）。攻撃は、公開する者の加工に対する攻撃者の動きを模擬して性能を測る（Simulation の説明 "Using existing or synthetic data to assess performance of a model, mimic operation of an existing or proposed system" に当たる）。被験者を無作為に割り付けないので、Randomized Experiment は選ばない。

**Intention for causal interpretation**（必須ではない）

推奨: **「No causal relationship inferred」**（加工の形の違いによる正答率の差は、同じ記録に形を掛け分けた比較だが、因果の推定として書かない。「結論に使わないこと」に合わせる）

**Blinding of experimental treatments** [必須・複数選択可]

推奨: **「No blinding is involved.」**

**Additional blinding during research or analysis**

No blinding. Unintended influences are limited by fixing all forms, attackers, rules, parameter values (config.json) and the random seed (SEED) before acquiring the data, by computing only the listed checks before the main computation, and by reporting every cell of the plan.

**Study design** [必須]

Each evaluated keystroke log is processed into each release form and matched by each attacker against N candidate texts (the true text and N − 1 decoys of the same prompt), for N = 10, 100 and 1,000, on full texts and on windows of k non-empty segments (k = 5, 10, 20, 50). Every log receives every form (a within-log comparison of forms); there are no groups of subjects. Attackers that need training are trained on the writers of the two prompts not being evaluated (the four prompts are split into two pairs, and the roles are swapped, so every writer is evaluated once). The release forms, segment rules, alignment, attackers, candidates and reported quantities are defined in the sections "Release forms (processing)", "Segments", "Alignment", "Attackers" and "Candidates, scope and numbers" of the attached preregistration.md.

（ファイルの欄: `preregistration.md` を添付する）

**Randomization**

There is no random assignment of subjects. All random draws (the split of prompts, the 500-writer evaluation sample, decoys, window starts, random processing in R5, R6 and R7, the negative control and bootstrap resamples) use a seed derived from the fixed string in SEED with the formula in preregistration.md (section "Candidates, scope and numbers", row "Random numbers").

## 3. Sampling

**Data collection procedures** [必須]

No new data are collected. KLiCKe (Tian, Crossley & Van Waes, 2025): the keystroke logs, essays and human scores of the argumentative writing task are acquired after this registration is fixed, without waiting for the authors' reply to an inquiry (the terms of use are public; if the reply raises a concern about this use, the computation is stopped, the acquired data are deleted, and this is reported). The demographics file is not acquired. ENJA15 (Carl, Aizawa & Yamada, 2016; Zou & Carl, 2026): from-scratch translation sessions are taken from the TPR-DB repository at a fixed Subversion revision, after the licence and terms of use and the meaning of the session types are confirmed in the primary sources; if they cannot be confirmed, the ENJA15 part is not carried out. The public KeyTAR model (Qiu et al., 2026) is taken from Zenodo record 17254163. The versions and SHA-256 of all files are recorded at acquisition (section "Data").

**Sample size** [必須]

KLiCKe: all writers after exclusion (4,992 writers in 4 prompts as reported, 1,136 to 1,329 per prompt; recounted after acquisition). The main tables use 500 writers (125 per prompt) drawn with the seed; all writers after exclusion are reported in the appendix for attackers A0 to A3. Candidates per log: N = 10, 100 and 1,000, with 20, 20 and 5 draws per log. Windows: 5 starts per log for each k. ENJA15: all from-scratch translation sessions after exclusion.

**Sample size rationale**

The sample is the whole public corpus. The 500-writer sample is set by the computational cost of the reference attacker A4 (KeyTAR); if it cannot be run on the local GPU, only its rows use a smaller sample (section "Attackers").

**Starting and stopping rules** [必須]

Not applicable: existing data are used, and all eligible records are used. There is no pilot phase with the data; the procedures were checked on synthetic logs before fixing.

## 4. Variables

**Manipulated variables** [必須]

None by random assignment. By design, every log is processed into every release form, and the following are varied: release form (R0 to R7 and their parameters, defined in the section "Release forms (processing)"), attacker (A0, A1, A1', A2, A2-b, A3, A4), number of candidates N, and scope (full text or window size k). All values are in config.json.

**Measured variables** [必須]

For each log, form, attacker, N and scope: whether the true text is chosen (ties count as 1/m), the rank of the true text, and the alignment costs. For each log and form: the 10 process measures of Table 5 of Tian et al. (2025) (section "Utility"). For each writer: the human score as distributed (used only for correlations with the process measures). For exclusion: whether the log, text and score exist and the number of words of the text.

**Indices** [必須]

Accuracy (mean credit over draws, then over writers), its multiple of 1/N, its gain over A0, the strongest adaptive attacker per form (maximum within each bootstrap resample), contrasts between adjacent forms, top-5 accuracy and mean reciprocal rank (secondary), and, for utility, Spearman correlations with the unprocessed values, ratios to the unprocessed values and Spearman correlations with human scores (sections "Reported quantities" and "Utility"; formulas in config.json, utility.formulas).

## 5. Analysis Plan

**Statistical models** [必須]

No statistical model is fitted for inference; the study reports estimates with intervals. Intervals are 95% percentile bootstrap intervals with 2,000 resamples, with writers as units stratified by prompt (KLiCKe) and translators as units (ENJA15, stratified by source text or not depending on whether translators and source texts are crossed). The strongest attacker's interval takes the maximum within each resample. A negative control replaces each log with the log of another writer of the same prompt and is expected to give about 1/N (section "Diagnostics"). Attacker A2-b uses a logistic regression and attacker A3 a likelihood model of key intervals, both trained on the other pair of prompts (section "Attackers"; settings in config.json).

（ファイルの欄: `config.json` と `SEED` を添付する）

**Transformations** [必須]

The release forms, the segment rules and the alignment are defined in preregistration.md and config.json. In every form, the log is trimmed to the active writing time, from the first key press to the last event that changes the text. Keys are mapped to 16 categories (config.json, key_categories).

**Inference criteria** [必須]

No significance test and no pass or fail criterion; results are reported as estimates with 95% intervals, and every cell of the plan is reported. The word "exceeds" (question 4, ENJA15) is used only when the lower bounds of both intervals (difference to 1/N and difference to A0) are above 0. Multiple comparisons are not corrected because no test is made; no form is recommended by a rule (section "Summary table and figure").

**Data inclusion and exclusion** [必須]

KLiCKe: writers with a missing log, text or score, and writers whose text has fewer than 50 words (runs of letters and digits), are excluded; writers whose reconstructed final draft differs from the distributed text are kept, and accuracy is reported separately for agreement and disagreement. ENJA15: sessions with a missing log or translation, an empty translation, or no Japanese input events are excluded. All counts are reported (sections "Data" and "ENJA15"). There is no outlier rule.

**Missing data** [必須]

Cells with too few valid writers (a prompt with fewer than N eligible writers) or no valid window of length k are not reported, and their counts are reported. Candidates without an alignment path have infinite cost; if all candidates are infinite, all tie (1/N). These cases are counted (sections "Alignment" and "Candidates, scope and numbers").

**Other planned analysis**

Secondary quantities: top-5 accuracy, mean reciprocal rank, the 10th, 50th and 90th percentiles of per-writer accuracy, A2 with the alignment penalty 4 and 16, an open-world diagnostic, accuracy split by agreement of the reconstructed final draft, the number of logs without an alignment path, the negative control and a check of bias in the true windows (sections "Reported quantities" and "Diagnostics"). The public KeyTAR model (A4) is reported as a reference outside the threat model.

## 6. Other

**Context and additional information**

The authoritative version of the plan is the attached preregistration.md together with config.json and SEED. The files are those of commit cf5353da274f371a0be060cf62efc9fb452afd61 of the repository https://github.com/mikotomiura/keystroke-log-release-matching (private until the paper is submitted). SHA-256: preregistration.md 3b206fc3c5894398b28836f1d4b861ed8c0aecfaeb29d6a99a3afde0aa22b846; config.json 54158b3bc63071c58fd01b31638cc1b7d0e3e368d88282ee5f54df4ee5e4d1b1; SEED d766284cd36eea562c99c5268cedd99a4bd2ae5ed9d75cb1bad330633cbbe9ff; notes.md 433bb13807d4322c5e651ab17563e5d481e313722be39c38cb2258f7869c827a; results/synthetic_check.json ff157d3dde9321d980f3868e83cb3ef4a00db6bd831650c44da979e50c83a70c; scripts/align.py 6c03dc66afa563903c2d65e90e7247c1faafeb32fe614209c31353f066e07543; scripts/align_ext.py 79579f266ab972277322ae7b3a2c0387c87eb783c3ebbd8638f49b55768c2a8d; scripts/replay.py 0456ba3427e14f79aa502308a38e34437067e667ceab1022d6ca84e248b564ad; scripts/romaji_table.py d2101efb9f36201b7fb51ea7c4283c114854cf13bba8fae379b6f85ae381fbd2; scripts/selftest_synthetic.py 8aa09de9ab4405f5bcad3769b7cabc0dd38ea9bd0437ddbbfe419aa3a349e990; scripts/synthetic_check.py 153f7e784cf4d4dfa5434874e10acc548ac3411f50623195c87892c208e630c5; scripts/synthetic_logs.py 5ac1b5d17e27437129eeebe15da8659819c7707cd43ca84fc85d0e54aa61f8b1. No data had been acquired when these files were committed. Code and aggregated results will be released in this repository with a Zenodo DOI. Logs and texts are not redistributed. The ethical considerations, including the absence of an ethics committee available to the researcher, are in the section "Ethical considerations". The plan and its text were drafted with an AI assistant (Claude, Anthropic) and decided by the researcher (section "Use of AI").
