# context-A — 査読者役と監査役の両方に渡すもの（attack-me・stage `prereg`・round 4）

作成: 2026-10-02（G-GEAR・メイン）。対象物は枝 `feature/ime-m3-prereg` の `159a2ec8`（公開物とコードは `88d96553` で直したもの。`159a2ec8` までの後のコミットは `.steering\` だけ）で commit 済み。

## 対象物

- `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（事前登録の**下書き**・未凍結・SHA-256 `cde06d9651e2dd838d1c4e7d5031824479bf2501423f00ebd7afd45ea2fdbafe`）
- 投稿先: *Behavior Research Methods*（BRM・Psychonomic Society・Springer）。事前登録は凍結の後に OSF Registries に公開で登録し、論文の Open Practices Statement から URL で参照する予定。
- stage `prereg`・**round 4**（round 3 の指摘を受けて直した版）: 凍結してよいか（accept）／直してから凍結（minor）／直して再査読（major）／計画から立て直す（reject）を判定する。**原稿（論文本体）はまだ無い**。それ自体を欠陥にしない。
- ★ **round 4 は、round 3 から変わった箇所に絞って見る**（下の「round 3 から変わった箇所」）。変わっていない節は round 3 の判定のままとし、再掲しない。
- ⚠️ 事前登録 §3.1 の 2 つの文（パイロットの生ログを預ける基準は凍結の前に `experiment\pilot-macos.md` に書く／問 4 の割り当てだけをパイロットの観測の key 行に流し、採点したブロックの割合を §3.1 に書く）は、**今は約束の文だけで、中身はまだ無い**（測定機での作業が残っている）。中身が無いこと自体は既知の未了として扱い、約束の文の書き方（何を・いつ・どこに）を見る。

## round 3 から変わった箇所（`git diff abc5d7f9..159a2ec8 -- papers\` から・メインが節ごとにまとめた）

### 事前登録（`preregistration.md`）の節

| 節 | 何が変わったか（記述だけ。理由は各役の引き継ぎに書いた） |
|---|---|
| §1.2 Questions | 区間を付けないものに「問 4 の場面ごと・速さごとの正解率」「§6.3 の配送の数」を足した／問 2 の打ち切りの問いを「20 秒の打ち切りに達するセッション」に／問 3 の量の名前（conversions per trial）／問 4 の問いを、公開するログの key 行・試行の句 1 つの識別・時刻を持たない 2 つの粒度に絞った |
| §3.1 Data that exist before the freeze | 預ける基準を凍結の前に書くこと／問 4 の割り当てだけをパイロットの key 行に流し、採点したブロックの割合をここに書くこと（どちらも約束の文） |
| §3.2 Data collection | §3.4 の検査を各 run の直後・次の項目の前に行う |
| §3.3 Sample size, precision and settings of the plan | 速さごとの精度は試行を独立とみなしたときの値で、速さの設計効果は最大 25／打ち切りの下に残る試行の表は §6.2 の除外の前の数／設計効果を、ブロックごとの層の試行数のばらつき（Σm²/Σm）で計算し直した（2 つの計画から: 層あたり 33〜39 / 30〜37 ブロック・Σm²/Σm は 2.4〜3.1 / 2.5〜3.4・D は最大約 3.4・区間で最大約 1.8 倍）／一致の限界の幅の目安（Bland & Altman）を足し、予想しないのは kappa と ICC だけに |
| §3.4 Stopping rule | run の中止を「計画の SHA-256 が違う」か「参照のログが実行器の外からの打鍵を示す」（`delivery.py` 単体の参照の `excess_rows` > 0、または `rows_outside_trials` が 1 ブロック 5 を超える）だけの閉じた規則にした。説明による例外を認めない。検査は run の直後・解析の前に行い、結果と時刻を `data.md` に記録する。観測の余分な行は中止の理由にしない |
| §4.5 The observer's specified rows (prediction) | 印の打鍵は oracle が時刻を記録し、キーは計画から取る／`carried out` の定義（試行の外で打ち切られたもの・ログの終わりで開いているものを含む） |
| §4.6 Texts | 4 つの量を、テキストのうち解析の範囲に入る試行の上で計算する（conversions per trial・時間の割合の分母は範囲の試行の時間の和）。範囲の試行が無いテキストは値なし |
| §6.1 Units, intervals and wording | 設計効果は §3.3 を参照（約 3.4・約 1.8 倍）／区間を付けないものの一覧（§1.2 と同じ）／要旨と結論では、主の範囲の推定値に、範囲が外す試行の割合と `all_trials` の値を並べる |
| §6.2 Exclusions and other contingencies | `log_truncated` は正解の側（参照のログ）／焦点の喪失は `focus_out` から次の `focus_in` までの区間で、重なる試行を数え、S15 は切り替えが試行の中で戻らないときだけ数える・行と偽陽性を速さごとにも／問 4 は合うブロックへ進む |
| §6.3 Plan versus ground truth, and delivery | 観測の余分な行は観測器の結果として解析に残り、参照の余分な行は run を中止にする |
| §6.4 Scopes and comparisons | `over_limit` の断片の行の割り当て（重なり最大）／問 3 は範囲の試行の上でテキストの量を計算する／打ち切りの規則は §1.1 を参照し、観測器のログからは打ち切られたセッションが分からないので、読者は 20 秒以上の変換の割合を別の情報源から見積もる必要がある |
| §6.6 Question 2: per-session agreement | 仕様（specified rows）との一致は試行ごとの行の数で読み、短い行の対は時刻だけで外れうる（§6.9） |
| §6.7 Question 3: per-text agreement | テキストごとの範囲の試行の数を速さごとに報告／1 つの速さの偏りの区間は、その速さの一致の報告に付けたもの／重み付けし直しの版を「carried out と received carry のどちらでもない試行」に（closing key in reading の試行は残す）。4 つの層のどれでもない試行の版は診断 |
| §6.8 Question 4: text recoverability | ブロックの置き方（印と全試行が合う所）・合わないブロックは採点せず次の合うブロックへ・試行の中の矢印 4 つは次のブロックがそこで合わない限り印とみなさない・損失は 1 ブロック／場面ごと・速さごとの正解率は記述で区間なし／規則は試行の句 1 つの識別を判定し、同じ書き手の複数の試行の組み合わせ・既知の最終テキストとの突き合わせは評価せず、ログ全体の安全を述べない／ブロック内の依存の向きの書き直し |
| §6.9 Clock differences | 回収の遅れは観測の区間全体をずらす |
| §6.11 Missing data | テキストに範囲の試行が無いときの null |
| §7 Threats to validity and limitations | 時刻を持つ集合は推定だけで、ms と 1 秒のビンの中間の粒度は評価しない／入力モードはモードキー（ブロックの頭のかなキーと S14 の英数キー・かなキー）だけで切り替え、ほかの経路（メニュー・ショートカット）は試していない／依存の向きの書き直し／**新しい項**「The text-recoverability study judges one phrase at a time」 |

変わっていない節: 題・Status・§1.1・§1.3・§2（2.1〜2.5）・§4.1〜§4.4・§5・§6.5・§6.10・§6.12・§8・§9・References。

### 一覧の公開物のうち変わったファイル

`experiment\data.md`（「Run checks」の表を新設・手順 1 を「run の直後に `delivery.py` 単体で中止の検査」に・旧手順 4 を消した）・`experiment\notes.md`（主の比較と範囲を名指すのは問 1〜3 の 3 つの結果のファイル）・`kit\e2\README.md`（攻撃者が見るのは key 行・セッション行は攻撃に渡さない／ブロックの依存の理由／余裕 2/K は設計の選択／合わせ直しで足された・重複した打鍵も 1 ブロックだけを失う／範囲の文〔句 1 つの識別・ログ全体の安全を述べない〕／2 つの集合の順序）。

### コード（第 2 群）で変わった関数

- `kit\analysis\l2.py`: `MEASURES`（`n_conversions` を `conversions_per_trial` に改名）・`text_layout`（`out_of_scope`）・`aggregate`（量を範囲の試行の上で）・`_outside_report`・`mixture_bias`（`by_stratum` から区間を外した）・`evaluate`（`per_trial_uncontaminated`・`texts.trials_in_scope_by_speed`）・docstring。試行ごとの量（`per_trial` の `n_conversions` ほか）は名前も定義も変えていない。
- `kit\analysis\match.py`: `parse_prediction`（`uncontaminated`）・`evaluate`（`scope.uncontaminated_trials`）。
- `kit\analysis\delivery.py`: `_loss_intervals`（新設）・`_focus_losses`・`evaluate`（出力の名前を `reference_focus_out` から `reference_focus_loss`〔`trials_with_focus_loss`〕に）。
- `kit\analysis\pipeline.py`: `_focus_loss`（`by_speed`）・`run_stages`・`analyse`（S15 の除外は `delivery.py` に移した）・docstring。
- `kit\e2\closed_set.py`: `align_blocks`（合わないブロックの後の再開）・selftest。

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

★ 第 2 群（コード。事前登録の記述が実装と合っているかを確かめるときに、必要な箇所だけ開く。round 4 では上の「変わった関数」を優先する）

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

測り方は round 2・round 3 と同じ（`## References` より前の行から、4 字下げのコマンド行を除き、空白で区切った語のうち英数字を含むものを数えた）。

| 項目 | round 2 の版 | round 3 の版 | 今の版 |
|---|---|---|---|
| 本文の語数 | 9,326 語 | 11,217 語 | **12,143 語**（round 3 の版から +8%） |
| References の語数 / 件数 | 205 語 / 9 件 | 205 語 / 9 件 | 205 語 / 9 件（変わらない） |
| 見出し（References を除く） | `##` 10・`###` 30 | `##` 10・`###` 30 | `##` 10・`###` 30 |
| 表 | 5 | 5 | 5 |
| 字下げのコマンド | 4 | 4 | 4 |

## 投稿規程の一次の抜粋（この round で取り直した）

- URL: `https://link.springer.com/journal/13428/submission-guidelines`（取得 2026-10-02・`curl -sL`（cookie つき）で HTML を取り、テキストにして逐語を照合した。原本の SHA-256 `c83e1f7da38063f04a70ab8e384ee8680b333ce4ec45048062ec2db8bca3ce7f`。round 3 の原本とはバイトが違う〔ページの動的な部分〕が、下の 17 文はすべて逐語で在る）
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
