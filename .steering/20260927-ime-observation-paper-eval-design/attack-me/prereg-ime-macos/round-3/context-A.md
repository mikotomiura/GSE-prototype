# context-A — 査読者役と監査役の両方に渡すもの（attack-me・stage `prereg`・round 3）

作成: 2026-10-02（G-GEAR・メイン）。対象物は枝 `feature/ime-m3-prereg` の `abc5d7f9`（事前登録の本文は `6fa79171` で直したもの・コードは `0bb61430` で直したもの）で commit 済み。

## 対象物

- `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（事前登録の**下書き**・未凍結・SHA-256 `309c24354f523ad16fb3a038e5c7f0ed6fc0b721cd92c7a6502a2594dd94c762`）
- 投稿先: *Behavior Research Methods*（BRM・Psychonomic Society・Springer）。事前登録は凍結の後に OSF Registries に公開で登録し、論文の Open Practices Statement から URL で参照する予定。
- stage `prereg`・**round 3**（round 2 の指摘を受けて直した版）: 凍結してよいか（accept）／直してから凍結（minor）／直して再査読（major）／計画から立て直す（reject）を判定する。**原稿（論文本体）はまだ無い**。それ自体を欠陥にしない。
- ★ **round 3 は、round 2 から変わった箇所に絞って見る**（下の「round 2 から変わった箇所」）。変わっていない節は round 2 の判定のままとし、再掲しない。

## round 2 から変わった箇所（`git diff 384712ee..abc5d7f9` から・メインが節ごとにまとめた）

### 事前登録（`preregistration.md`）の節

| 節 | 何が変わったか（記述だけ。理由は各役の引き継ぎに書いた） |
|---|---|
| 題 | 比べる相手を "the input method's own calls" から "a reference input field" に |
| §1.1 Purpose | 行を書かないキー（入力モードのキー・F13〜F19・修飾キー）を明記 |
| §1.2 Questions | 区間を付けるものと付けないものの範囲を書き直した／問 1〜3 の主の範囲／`carry_over` を、入力法のふるまいに依る唯一の除外として明記 |
| §3.1 Data that exist before the freeze | パイロットの生ログを預ける約束と、封印した行を預けるときだけ開けること（解析しない）／予測の値を `spec_predict.py --from-plan` で計算し直した（`long` の新しい定義・`received carry`・S12 の内訳） |
| §3.2 Data collection | やり直しの試みを次の実行の前に行い、学習は戻さない |
| §3.3 Sample size, precision and settings of the plan | n を決めた順序・精度の文の書き直し・表の作り方（round(n·p)）・最小の層 31・主の範囲の速さごとの n・打ち切りの下に残る試行の表（新しい `long` の定義で計算し直し）・設計効果の量（最大で約 1.34 倍）・一致の限界・kappa・ICC の幅を予想しない理由 |
| §3.4 Stopping rule | 計画の SHA-256 が違う run と、説明できない余分な行のある run を、中止した試みに数える |
| §4.4 Observation intervals | 回収は 1 枠で、回収の前に次のセッションが閉じると 1 行が失われる |
| §4.5 The observer's specified rows (prediction) | セッションごとに「打鍵が入った試行」を持つ／`long` と `received carry` の定義を書き直し（`started none` を置き換え）／closing key in reading の説明（S12 のかな配列）／予測の行も重なり最大で試行に割り当てる |
| §6.1 Units, intervals and wording | 主の範囲で速さのあいだの組成が違うこと／区間を付けるもの（偏り・一致の限界・混合の偏りを含む）と付けないもの／設計効果の量 |
| §6.2 Exclusions and other contingencies | `clock_jump` の閾値の理由／`carry_over` を唯一の例外として明記・除いた観測の行を数える／焦点の喪失の試行の観測の行と偽陽性を検出の結果に出す／問 4 の攻撃は、計画と合わないブロックを採点せずに次のブロックの印から再開する |
| §6.4 Scopes and comparisons | `long` の新しい定義／問 3 の主を `under_limit` に（`all_trials` は副で、この設計の打ち切り率に依存）／問ごとの範囲と比較の組／主の範囲が外すのは打ち切りだけ／層は重なりうる・`received carry` |
| §6.6 Question 2: per-session agreement | Navigation の正解は送った矢印の数／Cut-off の「specified」を予測の側に限った |
| §6.7 Question 3: per-text agreement | 主と副の範囲・偏りと一致の限界の区間・ICC の model の名前（mixed・ICC(A,1)）・混合の偏りの区間（速さごとに再標本）・テキストのシナリオの混ざり方は期待値の上でだけ等しい・試行ごとの差を層 none に限った版も出す |
| §6.8 Question 4: text recoverability | ブロックごとの割り当てと採点しないブロック／ブロックで再標本した区間（記述）と速さごとの正解率／1 秒のビンを推奨から外した（推奨は `no_time`・`counts_only` だけ）／通る確率の表の注／推奨はセッションの行を公開しないときの key 行の粒度／ブロック内の依存の向き／open set は判定の規則に入らない |
| §6.9 Clock differences | 区間の長さが違うときの言い方／`pred_obs` の短い予測の行が時刻だけで対にならないこと |
| §6.10 Question 5: runtime cost | `working` は計画を最後まで流し、最初の 8 時間の標本を使う |
| §7 Threats to validity and limitations | 基準の項の言い方／`n_continued_commits` の項を放棄に狭めた／入力ソースのポーリングの経路を試していない／やり直しの学習／1 つの入力法の項／予測が模さないもの（回収・送出から観測器までの遅れ）／打ち切りの範囲の項の書き直し（読みの長さ・`all_trials` の値）／独立を仮定する区間の項（新設） |
| §8 Deviations and addenda | 凍結のタグの結果を常に登録の結果として報告／追補が変えてよい既存のファイルの Windows の部分を列挙 |
| §9 Freeze | 凍結コミットの 40 桁の識別子・書き出しの根（`experiment/` と `kit/` を持つ最上位のディレクトリ） |

変わっていない節: Status・§1.3・§2（2.1〜2.5）・§4.1〜§4.3・§4.6・§5・§6.3・§6.5・§6.11・§6.12・References。

### 一覧の公開物のうち変わったファイル

`experiment\notes.md`（問いの形・結果のファイルの中身・追補の範囲・区間の長さの言い方・統計の表）・`experiment\pilot-macos.md`（Clocks の段落）・`experiment\data.md`（手順 4: 試行の外の行の上限をログごとに・説明できない run は中止した試みに数える）・`experiment\gt_rules.json`（`_note` の 1 文）・`kit\e2\README.md`・`kit\refinput-macos\README.md`（試行の独立の文）。

### コード（第 2 群）で変わった関数

- `kit\analysis\spec_predict.py`: `_Machine`（セッションごとの打鍵が入った試行）・`summarise_trials`（`long`・`received_carry`）・`by_stratum`・`_plan_rows`／`parse_plan`／`oracle_from_plan`／`_is_ms`（`--from-plan`）・`predict`・`main`・定数 `FORMAT`・`BLOCK_GAP_MS`・`MODIFIER_KEYS`。出力の形式は `spec_predict/2`。
- `kit\analysis\match.py`: `PREDICTION_FORMAT`・`parse_prediction`（`received_carry` を必須に）・`evaluate`（`scope` に `layer_none_trials`）。
- `kit\analysis\pipeline.py`: `L2_SCOPES`・`PRIMARY`・`PRIMARY_NOTE`・`_spread`・`_composition`・`_prediction_summary`・`_focus_loss`・`_detection_view`・`run_stages`・`analyse`。
- `kit\analysis\l2.py`: `_agree`・`_ba_stat`・`_ba_interval`・`_percentile_interval`・`_ci_status`・`mixture_bias`・`_stratified_replicates`・`_mix_total`・`per_trial`（`only_trials`）・`agreement`・`stratify`・`evaluate`。
- `kit\analysis\delivery.py`: `_focus_losses`（`trials_with_focus_out`）。
- `kit\analysis\stats.py`: `icc` の docstring だけ。
- `kit\e2\closed_set.py`: `DEFAULT_BOOTSTRAP`・`marker_categories`・`_is_anchor`・`_next_anchor`・`align_blocks`・`align_plan`・`merge_alignments`・`segment_by_plan`・`evaluate`（`--bootstrap`・`by_speed`）・`run`・`main`。
- `kit\e2\open_set.py`: `load_trials`（`closed_set.align_plan` を使う）・`run`・`main`。

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
- `C:\GSE-prototype\papers\ime-observation\kit\emit\keymap_macos.json`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\e3\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\run\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\pilot\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\refinput-macos\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\emit\README.md`

★ 第 2 群（コード。事前登録の記述が実装と合っているかを確かめるときに、必要な箇所だけ開く。round 3 では上の「変わった関数」を優先する）

- `C:\GSE-prototype\papers\ime-observation\kit\analysis\pipeline.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\gt_sessions.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\match.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\l1.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\l2.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\stats.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\spec_predict.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\delivery.py`
- `C:\GSE-prototype\papers\ime-observation\kit\gen\generate_plan.py`
- `C:\GSE-prototype\papers\ime-observation\kit\run\run_cell.py`
- `C:\GSE-prototype\papers\ime-observation\kit\pilot\clock_sync.py`
- `C:\GSE-prototype\papers\ime-observation\kit\pilot\seal_obs.py`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\closed_set.py`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\open_set.py`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\src\input\ime_compose.rs`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_macos.rs`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_macos\keymap.rs`

⚠️ 一覧に無いもの（`kit\corpus\data\` の刺激のコーパス、他の `kit\` のファイル、`papers\ime-observation\` の外）は読まない。生ログ（`*.jsonl`・`*.ndjson`）・`runs\`・`sealed\` は、この機械にも一覧にも無い。

## 測った値（メインが機械で測った・2026-10-02）

測り方は round 2 と同じ（`## References` より前の行から、4 字下げのコマンド行を除き、空白で区切った語のうち英数字を含むものを数えた）。

| 項目 | round 1 の版 | round 2 の版 | 今の版 |
|---|---|---|---|
| 本文の語数 | 5,307 語 | 9,326 語 | **11,217 語**（round 2 の版から +20%） |
| References の語数 / 件数 | 205 語 / 9 件 | 205 語 / 9 件 | 205 語 / 9 件（変わらない） |
| 見出し（References を除く） | `##` 9・`###` 28 | `##` 10・`###` 30 | `##` 10・`###` 30 |
| 表 | 1 | 5 | 5 |
| 字下げのコマンド | 4 | 4 | 4 |

## 投稿規程の一次の抜粋（この round で取り直した）

- URL: `https://link.springer.com/journal/13428/submission-guidelines`（取得 2026-10-02・`curl -sL`（cookie つき）で HTML を取り、テキストにして逐語を照合した。原本の SHA-256 `034f0e0cb6e40f6bf72316d5ad2a3839a3515e4cef1a6829cbb0cc178ff63523`。round 2 の原本とはバイトが違う〔ページの動的な部分〕が、下の 17 文はすべて逐語で在る）
- 以下はすべて**照合済み**（原文に逐語で在る）。

| # | 要件 | 逐語 | 照合 |
|---|---|---|---|
| J1 | 誌の範囲 | "Behavior Research Methods publishes articles concerned with the methods, techniques, and instrumentation of research in experimental psychology. … Authors are encouraged to write their articles in such a way that readers can easily use the materials in their own work (e.g., by making stimuli and programming code available)." | 照合済み |
| J2 | TOP Level 2 | "In 2020, the Editorial Board of Behavior Research Methods decided that the journal follows the Open Science Initiative's Level 2 Transparency and Openness Guidelines. This means that all relevant information must be placed in a trusted repository. This applies to stimuli and methods being validated, new analyses being reported, and new equipment being described. BRM readers want practical solutions." | 照合済み |
| J3 | Open Practices Statement | "All submitted manuscripts must include an Open Practices Statement immediately prior to the References section of the paper." 例文: "… Validation study 1 was preregistered (url for the preregistration)." | 照合済み |
| J4 | 生データの公開 | "A submission to the journal implies that materials described in the manuscript, including all relevant raw data, will be freely available to any researcher wishing to use them for non-commercial purposes, without breaching participant confidentiality." | 照合済み |
| J5 | 投稿時の確認 (d) | "the manuscript includes appropriate measures of variability, effect size, and (when relevant) statistical power." | 照合済み |
| J6 | n の決め方（Statistical Guidelines） | "Alternatively an analysis might focus on estimation of an effect size rather than on a hypothesis test. In any case, the Method section should make clear what criteria were used to determine the sample size." | 照合済み |
| J7 | 精度で設計する（同） | "In many scientific investigations the goal of an experiment is to measure the magnitude of an effect with some degree of precision. … some of the bias issues described above can be avoided by designing experiments to measure effects to a desired degree of precision (range of confidence interval)." | 照合済み |
| J8 | 共変量（同） | "Covariate analyses should either be planned in advance (and in that case would benefit from preregistration) or be described as exploratory." | 照合済み |
| J9 | 除外（同） | "Best practice is to set inclusion/exclusion criteria in advance (and pre-register where appropriate) and stick to them, but if that is not done then whatever procedure was followed should be reported." | 照合済み |
| J10 | 要旨 | "There must be an abstract of no more than 250 words." | 照合済み（⚠️ 事前登録には適用されない。原稿の段で使う） |
| J11 | 事前登録の書式 | 規程は事前登録の書式・必須の節・分量を定めていない（原文の "preregistration" は 3 か所で、例文・共変量・変数の選択の文だけ） | 規定なし（取得した範囲の原文に該当の文が無い） |
