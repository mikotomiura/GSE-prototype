# context-A — 査読者役と監査役の両方に渡すもの（attack-me・stage `prereg`・round 5）

作成: 2026-10-02（G-GEAR・メイン）。対象物は枝 `feature/ime-m3-prereg` の `ba89bcbd` で commit 済み（公開物とコードを最後に変えたのは `e4052dd8`。その後の `ba89bcbd` は `.steering\` だけ）。

## 対象物

- `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（事前登録の**下書き**・未凍結・SHA-256 `d6e7dbf68b5721a125ee9e4d84d9ac846b9aaca9dc5f082fc9340137d324b00e`）
- 投稿先: *Behavior Research Methods*（BRM・Psychonomic Society・Springer）。事前登録は凍結の後に OSF Registries に公開で登録し、論文の Open Practices Statement から URL で参照する予定。
- stage `prereg`・**round 5**（round 4 の指摘を受けて直し、さらに凍結の前に測定機でパイロットのログに解析のコードを当てた版）: 凍結してよいか（accept）／直してから凍結（minor）／直して再査読（major）／計画から立て直す（reject）を判定する。**原稿（論文本体）はまだ無い**。それ自体を欠陥にしない。
- ★ **round 5 は、round 4 から変わった箇所に絞って見る**（下の「round 4 から変わった箇所」）。変わっていない節は round 4 までの判定のままとし、再掲しない。
- ★ round 4 で「約束の文だけ」だった事前登録 §3.1 の 2 つの点検（問 4 の割り当てをパイロットの観測の key 行に流す・パイロットの参照のログに `delivery.py` を当てる）と、`experiment\pilot-macos.md` の Raw logs（預ける基準）は、**今の版では中身がある**（測定機で行った結果）。⚠️ パイロットのログそのもの（生ログ）は、この機械にも一覧にも無い。§3.1 の数は、文書の中での整合と、コードが数えるものとの対応で見る。

## round 4 から変わった箇所（`git diff 40ad7801..ba89bcbd -- papers\` から・メインが節ごとにまとめた）

### 事前登録（`preregistration.md`）の節

| 節 | 何が変わったか（記述だけ。理由は各役の引き継ぎに書いた） |
|---|---|
| §1.2 Questions | 問 4 の終わりに「(Section 6.8 states what is not evaluated.)」 |
| §2.1 Type of study | 「§3.4 の規則が、ログに人の打鍵のしるしのある run を外す（捕まえないものは §7）」を足した |
| §3.1 Data that exist before the freeze | 預ける基準の文を 2 文に分けた（基準は凍結の前に `pilot-macos.md` に書く／満たす run の生ログを預ける）。凍結の前の 2 つの点検を、**対象の run・命令の引数・結果**つきで書いた: (1) 問 4 の割り当てを、矢印の印を使ったパイロットの 3 run（`pilot2-on`・`pilot2-off`・`verify-off`）の観測の key 行に `--markers-in-obs` とパイロットの 3 打鍵の印で流した（15 / 15 ブロック・282 試行・割り当てのない打鍵 0・再同期は試されていない）。(2) 同じ 3 run に §3.4 の引数で `delivery.py` を当てた（かなキーも S14 のモードキーも参照に key-down を残さない → k = 0・モードキーは送った打鍵に数えない／区間の余りは最大 0／区間の最後の行から次のブロックまで最小 1,582 ms／S15 以外の焦点の喪失は `pilot2-off` に 1 回・31 ms・前後 3 秒に観測の key 行 0・6 run で約 87 分）。焦点の規則を凍結の前に 2 度改めた理由（喪失ごとに中止では約 12 時間の run の多くが中止になりうる／喪失の中の key 行をすべて数える最初の版では、計画から作った oracle で run の時間の約 78% が送った打鍵から 500 ms 以内）。OFF の carried out 186 の内訳。`spec_predict.py --from-plan` が `plan_figures`（§3.3・§6.7 が引く計画の数）も書く |
| §3.2 Data collection | §3.4 の点検は 2 つのセルと `working` の run に当てる（`idle` は打鍵も計画も無い） |
| §3.3 Sample size, precision and settings of the plan | 主の範囲の試行の上の Σm²/Σm（最大 3.05〔ON・S14 mid〕・3.22〔OFF・S15 mid〕）を足した／「usually near 1」を「near 1 only when rho is small」に／最小の主の層（31）の半幅（約 0.35 × SD）を足した |
| §3.4 Stopping rule | **書き直した**。完了した run を中止に数える理由は 3 つ（計画の SHA-256／参照のログの外からの打鍵／S15 の計画した切り替え以外の焦点の喪失の中で、観測が実行器の送っていない打鍵を記録した）。`delivery.py` の命令行（`--pre-ms 20 --tail-ms 300`）。**Presses from outside**: oracle の `block_begin` で区間に分け、区間ごとに「送った打鍵で説明されない参照の key-down の数」を数え、どの区間でも手順が作る打鍵（最初の区間は k・最後の区間は印だけ・ほかは印＋k）を超えたら中止。k = 0 とモードキーの扱いは §3.1 のパイロットで決めた（版は `excluding_mode_keys`）。**Loss of focus**: S15 以外の喪失を前後 500 ms 広げ、重なる区間をまとめ、区間ごとに観測の key 行の数と、実行器が送って観測が記録する打鍵（試行の押下〔モードキーを除く〕と印・区間の 100 ms 前から数える）の数を比べ、超えたら中止。`delivery.py` が入力を拒む（exit 2）run も中止。検査の対象（2 つのセルと `working`）。`data.md` の表に記録するもの。`pipeline.py` も同じ規則を当てて拒む。中止に数えた run は預けない。runner が中止した run にも同じ点検を当て、通るか、参照のログも観測のログも無いときだけ預ける。`pipeline.py --pack` / `--check-deposit` が全 run に当てる。取りこぼしと外からの打鍵の相殺は検出しない。喪失の外では観測の余分な行は中止の理由にしない |
| §5 Analysis code and settings | pipeline は §3.4 の規則に当たる run を拒む |
| §6.2 Exclusions and other contingencies | Not excluded の「the trials whose presses went into a session that the observer's rules cut off」／焦点の喪失の項を書き直した（§3.4 で中止に数える場合・解析する run にも打っている最中の喪失がありうる・その試行は計画と正解の食い違いとして現れ除外しない・S15 は切り替えが自分の試行の中で戻るときだけ計画したもの） |
| §6.3 Plan versus ground truth, and delivery | ブロックの区間ごとの「説明されない行」を報告に足した／参照の余分な行が run を中止にするかは §3.4 の規則だけで決まる |
| §6.4 Scopes and comparisons | 打ち切りの読者向けの文を書き直した（key 行は打ち切りの候補を示すが、macOS では入力モードが残らないので確定できない／打ち切りが 4 つの量を動かす向き） |
| §6.6 Question 2: per-session agreement | 仕様の行との一致は `pred_obs` の `over_limit` の層ごとの検出の数（予測の行・観測の行・対・取りこぼし・偽陽性）で読み、ほかの統計は計算しない |
| §6.7 Question 3: per-text agreement | 範囲の試行の数 k の開示（平均 4.60 / 6.49 / 7.17・4.56 / 6.43 / 7.21・slow で k ≤ 3 が 30 / 126・27 / 117・k = 8 は 4・0・k = 0 なし）／限界と ICC は k の分布の上の値で速さのあいだで比べない／偏りはテキストに等しい重み／k が小さいほど片側で計算できず落ちるテキストが増える／持ち越しの無い版では S6 が両セル・全速さで 0 試行、S13 は主の範囲に無い → 重み付けし直せず、層は null と理由／診断は「the trials of the layer none (section 6.4)」 |
| §6.8 Question 4: text recoverability | 印は矢印の連なりの**右の端**で探す（直前の矢印が印を隠さない）／1 つの違いで失うのはそのブロックだけ、ブロックのあいだに足された打鍵は何も失わない（selftest の場合で確かめた・一般には証明していない）／「Presses that no scored block covers (including those of unscored blocks) are counted」 |
| §7 Threats to validity and limitations | 打ち切りの項に k と「key 行だけでは確定できない」を足した／**新しい項**「The stopping rule counts presses, not keys」（相殺・焦点を動かさないショートカット・キーを押さずに焦点を移して戻る人・喪失の区間の中の取りこぼしと終わりの直前 100 ms・観測器の重複行）／「judges one phrase at a time」の項を §6.8 の参照に縮めた |

変わっていない節: 題・Status・§1.1・§1.3・§2.2〜§2.5・§4（4.1〜4.6）・§6.1・§6.5・§6.9〜§6.12・§8・§9・References。

### 一覧の公開物のうち変わったファイル

- `experiment\data.md`: 「Run checks」の前置き（k = 0・`excluding_mode_keys`・上限は両方 0）と表の列（runner の中止・計画の SHA-256・`delivery.py` の終了コード・`max_beyond_markers_before_last_block`・`beyond_markers_last_block`・`n_unplanned_loss_spans_with_unexplained_presses`・中止に数えるか・預けたか）。手順 1（命令行・計画の SHA-256 の照合・中止に数える条件・runner が中止した run も・喪失の外では観測の余分な行は止めない）。梱包の手順（§3.4 の規則に当たる run と点検できない run を拒む）。
- `experiment\pilot-macos.md`: Raw logs を、本計測と揃えた預ける基準に置き換えた（runner の run が候補・§3.4 の規則がパイロットで決めた設定と run 自身の印〔3 打鍵〕で当たらない・`pipeline.py --check-deposit` が通る・喪失の外では観測の余分な行は止めない・封印したセッション行は凍結と本計測の後に預けるためにだけ開ける・凍結の前に 6 run と最初のパイロットの前の短い run に規則を当て、どれにも当たらなかった）。
- `kit\e2\README.md`: 錨は印の区分の連なりの右の端／ブロックのあいだに足された打鍵は何も失わない／ブロック末の閉じる Return の欠けで失うのはそのブロックだけ／selftest の場合で確かめた・一般には証明していない。

### コード（第 2 群）で変わった関数・定数

- `kit\analysis\delivery.py`: 定数 `FOCUS_MARGIN_MS = 500`・`OBS_SEND_DELAY_MS = 100`。`read_plan`（ブロックの印）・`read_oracle`（`block_begin` の時刻・block_id は整数だけ）・`_segments`（新設: ブロックの区間ごとの「説明されない数」）・`_side`（`segments` の 2 版 `all_presses` / `excluding_mode_keys`・`max_beyond_markers_before_last_block`・`beyond_markers_last_block`・`ms_from_last_row_to_next_block`）・`_focus_losses`（計画した喪失／計画外の喪失・`n_loss_intervals_unplanned_with_presses`・`n_presses_in_unplanned_losses`〔記述・送った打鍵を含む〕・`n_unplanned_loss_spans`・`n_unplanned_loss_spans_with_unexplained_presses`・`n_presses_unexplained_in_unplanned_losses`〔規則が使う〕）・`evaluate`（`params.focus_margin_ms`・`params.obs_send_delay_ms`）・selftest。
- `kit\analysis\pipeline.py`: 定数 `RUNNER_KANA_PRESSES_PER_BLOCK = 0`・`REFERENCE_RECEIVES_MODE_KEYS = False`・`DELIVERY_PRE_MS = 20`・`DELIVERY_TAIL_MS = 300`。`reference_abort_segments`・`reference_abort_reasons`（新設）・`analyse`（規則に当たる run を拒む・`e1_delivery.json` の `abort_rule`）・`_abort_rule_findings`・`deposit_check_files`（`--pack` / `--check-deposit` が完了・中止を問わず規則を当てる）・selftest（`_case_reference_abort_rule`・`_case_section34_enforcement`）。
- `kit\analysis\l2.py`: `per_trial`（計画にある層で試行の無いものを `status: no_trial` と `trials_not_used` で出す）・selftest。
- `kit\analysis\spec_predict.py`: `plan_figures`（新設・`--from-plan` の出力に層ごとの試行・ブロック・Σm²/Σm と、速さごとのテキストあたりの long でない試行の数の分布）・selftest。
- `kit\e2\closed_set.py`: `_is_anchor`（右の端）・`_next_anchor`・`align_blocks`・selftest。

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

★ 第 2 群（コード。事前登録の記述が実装と合っているかを確かめるときに、必要な箇所だけ開く。round 5 では上の「変わった関数・定数」を優先する）

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

⚠️ 一覧に無いもの（`kit\corpus\data\` の刺激のコーパス、他の `kit\` のファイル、`papers\ime-observation\` の外）は読まない。⚠️ **Grep は一覧のファイルだけを対象にする**（ディレクトリ全体〔`kit\` など〕を Grep しない。一覧の外のファイルの行が出力に混ざるため）。生ログ（`*.jsonl`・`*.ndjson`）・`runs\`・`sealed\` は、この機械にも一覧にも無い。

## 測った値（メインが機械で測った・2026-10-02）

測り方は round 2〜4 と同じ（`## References` より前の行から、4 字下げのコマンド行を除き、空白で区切った語のうち英数字を含むものを数えた）。

| 項目 | round 3 の版 | round 4 の版 | 今の版 |
|---|---|---|---|
| 本文の語数 | 11,217 語 | 12,143 語 | **14,665 語**（round 4 の版から +21%） |
| References の語数 / 件数 | 205 語 / 9 件 | 205 語 / 9 件 | 205 語 / 9 件（変わらない） |
| 見出し（References を除く） | `##` 10・`###` 30 | `##` 10・`###` 30 | `##` 10・`###` 30 |
| 表 | 5 | 5 | 5 |
| 字下げのコマンド（ブロック） | 4 | 4 | 5（§3.4 に 1 つ足した） |

## 投稿規程の一次の抜粋（この round で取り直した）

- URL: `https://link.springer.com/journal/13428/submission-guidelines`（取得 2026-10-02・`curl -sL`（cookie つき）で HTML を取り、テキストにして逐語を照合した。原本の SHA-256 `54ceba57b628b3a3d7503f4ac313661e37654da5fccebde32776c7bb015e50a6`。round 4 の原本とはバイトが違う〔ページの動的な部分〕が、下の 17 文はすべて逐語で在る）
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
