# context-A — 査読者役と監査役の両方に渡すもの（attack-me・stage `prereg`・round 1）

作成: 2026-10-01（G-GEAR・メイン）。対象物は枝 `feature/ime-m3-prereg` の `d0cf4343` で commit 済み。

## 対象物

- `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（事前登録の**下書き**・未凍結）
- 投稿先: *Behavior Research Methods*（BRM・Psychonomic Society・Springer）。事前登録は凍結の後に OSF Registries に公開で登録し、論文の Open Practices Statement から URL で参照する予定。
- stage `prereg`: 凍結してよいか（accept）／直してから凍結（minor）／直して再査読（major）／計画から立て直す（reject）を判定する。**原稿（論文本体）はまだ無い**。それ自体を欠陥にしない。

## 読んでよいファイルの一覧（これだけ・絶対パス・1 行 1 件）

★ 第 1 群（先に読む: 対象物と、対象物が名指しする設定・手順・報告）

- `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\plan_config.macos.json`
- `C:\GSE-prototype\papers\ime-observation\experiment\config.json`
- `C:\GSE-prototype\papers\ime-observation\experiment\gt_rules.json`
- `C:\GSE-prototype\papers\ime-observation\experiment\SEED`
- `C:\GSE-prototype\papers\ime-observation\experiment\run.sh`
- `C:\GSE-prototype\papers\ime-observation\experiment\notes.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\pilot-macos.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\data.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\env.md`
- `C:\GSE-prototype\papers\ime-observation\kit\gen\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\gen\recipes.json`
- `C:\GSE-prototype\papers\ime-observation\kit\gen\recipes.macos-live-off.json`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\e3\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\run\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\pilot\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\refinput-macos\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\emit\README.md`

★ 第 2 群（コード。事前登録の記述が実装と合っているかを確かめるときに、必要な箇所だけ開く。全部を通読しなくてよい）

- `C:\GSE-prototype\papers\ime-observation\kit\analysis\pipeline.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\gt_sessions.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\match.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\l1.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\l2.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\stats.py`
- `C:\GSE-prototype\papers\ime-observation\kit\gen\generate_plan.py`
- `C:\GSE-prototype\papers\ime-observation\kit\run\run_cell.py`
- `C:\GSE-prototype\papers\ime-observation\kit\pilot\clock_sync.py`
- `C:\GSE-prototype\papers\ime-observation\kit\pilot\seal_obs.py`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\closed_set.py`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\open_set.py`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\src\input\ime_compose.rs`（観測器の macOS の状態機械）

⚠️ 一覧に無いもの（`kit\corpus\data\` の刺激のコーパス、他の `kit\` のファイル、`papers\ime-observation\` の外）は読まない。生ログ（`*.jsonl`・`*.ndjson`）・`runs\`・`sealed\` は、この機械にも一覧にも無い。

## 測った値（メインが機械で測った・2026-10-01）

| 項目 | 値 |
|---|---|
| 本文の語数（`## References` より前・字下げのコマンド行を除く） | 5,434 語 |
| References の語数 / 件数 | 211 語 / 9 件 |
| 見出し | `##` 10 個・`###` 28 個 |
| 表 | 1（シナリオの手順） |
| 字下げのコマンド | 4（計画の生成・凍結のハッシュ・E2 の 2 本） |

## 投稿規程の一次の抜粋（この round で取り直した）

- URL: `https://link.springer.com/journal/13428/submission-guidelines`（取得 2026-10-01・`curl -sL` で HTML を取り、テキストにして逐語を照合した。原本の SHA-256 `07987b78cf29e2989abbb61ae2480478c60a0e34602ad8d2a4cc1db6672e7778`）
- 以下はすべて**照合済み**（原文に逐語で在る）。

| # | 要件 | 逐語 | 照合 |
|---|---|---|---|
| J1 | 誌の範囲 | "Behavior Research Methods publishes articles concerned with the methods, techniques, and instrumentation of research in experimental psychology. … Authors are encouraged to write their articles in such a way that readers can easily use the materials in their own work (e.g., by making stimuli and programming code available)." | 照合済み |
| J2 | TOP Level 2 | "In 2020, the Editorial Board of Behavior Research Methods decided that the journal follows the Open Science Initiative's Level 2 Transparency and Openness Guidelines. This means that all relevant information must be placed in a trusted repository. This applies to stimuli and methods being validated, new analyses being reported, and new equipment being described. BRM readers want practical solutions." | 照合済み |
| J3 | Open Practices Statement | "All submitted manuscripts must include an Open Practices Statement immediately prior to the References section of the paper." 例文: "Stimuli, validation data and analysis code are available at (url …). Validation study 1 was preregistered (url for the preregistration)." | 照合済み |
| J4 | 生データの公開 | "A submission to the journal implies that materials described in the manuscript, including all relevant raw data, will be freely available to any researcher wishing to use them for non-commercial purposes, without breaching participant confidentiality." | 照合済み |
| J5 | 投稿時の確認 (d) | "the manuscript includes appropriate measures of variability, effect size, and (when relevant) statistical power." | 照合済み |
| J6 | n の決め方（Statistical Guidelines） | "… Alternatively an analysis might focus on estimation of an effect size rather than on a hypothesis test. In any case, the Method section should make clear what criteria were used to determine the sample size." | 照合済み |
| J7 | 精度で設計する（同） | "In many scientific investigations the goal of an experiment is to measure the magnitude of an effect with some degree of precision. … some of the bias issues described above can be avoided by designing experiments to measure effects to a desired degree of precision (range of confidence interval)." | 照合済み |
| J8 | 共変量（同） | "Covariate analyses should either be planned in advance (and in that case would benefit from preregistration) or be described as exploratory." | 照合済み |
| J9 | 除外（同） | "Best practice is to set inclusion/exclusion criteria in advance (and pre-register where appropriate) and stick to them, but if that is not done then whatever procedure was followed should be reported." | 照合済み |
| J10 | 要旨 | "Abstract: There must be an abstract of no more than 250 words." | 照合済み（⚠️ 事前登録には適用されない。原稿の段で使う） |
| J11 | 事前登録の書式 | 規程は事前登録の書式・必須の節を定めていない | 規定なし（取得した範囲の原文に該当の文が無い） |
