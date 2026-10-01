# 査読 R1（打鍵の時刻を測る道具を外部の基準で検証してきた立場）・round 3・stage `prereg`

対象: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（abc5d7f9 の版）。今回は round 2 から変わった節と、変わった関数だけを見ました。

## 結論

**minor**（直してから凍結）です。前の round の指摘 21 件のうち、15 件は解消、6 件は部分的に解消、未解消は 0 件でした。ただし今回の直しで新しい穴が 4 つできました。そのうち 1 件（§3.4 の run を中止扱いにする新しい規則）は major で、凍結の前に直す必要があります。

## 1. 接地（この立場が論文に求める基準・逐語）

- **G1 外部の基準と区間の明示**（Plant 2016）: "In closing I would propose that researchers self-validate their own timing accuracy using external chronometry (e.g., … using a Black Box ToolKit or oscilloscope) and state confi- dence intervals on publication."
- **G2 代理での検証の否定**（Plant 2016。B と ^ は引用符が抽出で化けたもの）: "Worryingly in the literature there seems to be a growing trend towardBchecking^ timing accuracy by proxy by running a study and if the results generally tally with those expected or are in line with previously published findings then the timing Bmust^ have been acceptable."
- **G3 正常に見えるログは確信の根拠にならない**（Plant 2016）: "Worryingly the log files suggested that the test had run normally imbuing an unwarranted confidence in the experiment, equipment, and soft- ware used."
- **G4 その場・その構成で確かめ、一般化しない**（Plant 2016）: "The only way to be sure of timing accuracy is to check it when paradigms are running in-situ, on the experimenter ’s own equipment, at the time a given study is carried out. Generalization across apparently similar hardware types or categories of study is folly."
- **G5 偏り（accuracy）とばらつき（precision）を分けて報告する**（Bridges et al. 2020）: "Precision refers to the trial-to-trial variability of the measures: the jitter of the timing measurement or its “variable error”. Accuracy refers to the “constant error” of a measurement which, in timing terms, is often referred to as the “lag”, “offset” or “bias” from the true value." / "We stress the importance of scientists making their own timing validation measurements for their own stimuli and computer configuration."
- **G6 合成入力は実際の使い方の構造を持つべき**（Pinet et al. 2017。改行のハイフンは抽出のまま）: "A lim- itation of this approach is that their manipulation involved fixed intervals and a single button. A crucial and original feature of the present study is the use of three distinct keys from the keyboard, and the generation of variable delays between keys, just as it happens in actual experiments involv- ing sequence production."

## 2. 引き継ぎの判定

### A. round 2 の新しい指摘

| 指摘 | 判定 | 理由（1 行）と今の版の位置 |
|---|---|---|
| N1 | 解消 | §3.3 に区間の幅の記述と "this does not guarantee that 0.95 and 0.90 are told apart (71 of 75 gives the interval 0.871 to 0.979)" が入った。速さごとの精度の文は新しい nit（N-5）。 |
| N2 | 部分的に解消 | 条件 1・2 は満たした（§6.1 の組成の段落と `pipeline.py` の `_composition`）。条件 3 は §6.1 の要旨の段落（"In the abstract and the conclusions, estimates are given as the ranges of their intervals…"）に入っていない。「直す一覧に入れなかった」は理由ではない。 |
| N3 | 解消 | §4.5 の `long` と `received carry`、`_Machine._apply`（打ち切る打鍵は入らない）、`summarise_trials` が一致する。§3.3 の表の列の和（on 603/852/940、off 553/783/876）が、試行数から §3.1 の `long` を引いた数と一致することを確かめた。 |
| N4 | 解消（文で書く道） | §6.9 の最後の 2 文と §7 の予測の項。§6.6 との関係が残る（N-6）。 |
| N5 | 解消（原則） | §6.8 第 2 段落と `align_blocks`。ただし合わせ直しの実装に新しい穴がある（N-2）。 |
| N6 | 解消 | §7 "polling the input source, is not exercised"。 |
| N7 | 解消 | §1.2 の最後の文と、§6.2 の "the only exclusion that rests on what the input method did"。 |
| N8 | 部分的に解消 | 範囲と比較の組は `pipeline.py` の `L1_SCOPES`／`L2_SCOPES`／`COMPARISONS` と合う。§6.2 の `log_truncated` は "a session still open when the log ends" のままで、どちらのログかが無い。 |
| N9 | 解消 | §6.8 の表の注。 |
| N10 | 解消 | §4.4 の最後の文。 |
| N11 | 解消 | §6.6 Navigation と題。 |

### B. round 2 で部分的に解消／未解消とした round 1 の指摘

| 指摘 | 判定 | 理由（1 行）と今の版の位置 |
|---|---|---|
| M1 | 解消 | §6.8 第 5 段落で推奨を `no_time`・`counts_only` に限った。§7 "finer granularities are not evaluated"。 |
| M3 | 解消 | §6.6 Cut-off を書き直した。 |
| M5 | 解消 | §7 の基準の項を放棄に狭めた。 |
| m1 | 部分的に解消 | 量は入った（§6.1・§3.3 の "at most about 1.8 … 1.34 times"）。ただしその量が、ブロックごとに層の試行数が違うことを入れていない（N-4）。 |
| m2 | 解消 | `pilot-macos.md` の Clocks（66 ms から約 370 ms へ）と §6.9。 |
| m4 | 解消 | §3.2 の最後の文。§3.4 の新しい検査の時機とは食い違う（N-1 の (c)）。 |
| m5 | 部分的に解消 | 行と偽陽性は出るようになった。ただし数えるのは「試行の中に focus_out の行がある試行」だけで、セル単位の合計しか出ない（N-3）。 |
| m10 | 解消 | §6.2 の `clock_jump` の理由。1,000 ms 未満のずれは事象を隣の試行まで動かせないので、論理として成り立つ。 |
| m11 | 部分的に解消 | §3.1 で預ける約束は戻った。しかし §3.1 が指す "the criteria set out there" は、`pilot-macos.md` の Raw logs で "will be written here" のまま。 |
| n3 | 部分的に解消（round 2 と同じ） | §5 と §9 は、コミットを `notes.md` に手で書く形のまま。研究者の選択として了承する。 |

## 3. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 4 | 新しい 2 つの文が、仕組みより強いことを言っている。§6.2 "so that a failure of the reference is not read as one of the observer" は、焦点を失ったままの後続の試行を拾わない（N-3）。§6.8 "more than any trial sends in a row" は「送る」数の話で、観測に 1 つ余分な行が入った場合を守らない（N-2）。それ以外は控えめに書かれている。 |
| b 方法の穴 | 3 | round 2 の穴はほぼ塞がった。今回の直しで次の穴ができた: 完了した run を、観測（試験の対象）の余分な key 行で中止扱いにしうる規則（N-1）／偽の錨で以後のブロックがすべて採点されなくなる（N-2）／焦点の喪失の範囲を数えない（N-3）。 |
| c 持ち帰れるもの | 4 | round 2 から大きくは変わらない。範囲の組成（`_composition`）と、層 none に限った試行ごとの差が加わり、読者が自分の配分に重み付けし直しやすくなった。 |
| d 簡潔さと構成 | 3 | 11,217 語（+20%）。増えた分の多くは別の節の言い換えで、相互参照が増えた（打ち切りの範囲の依存は §6.4・§7・`PRIMARY_NOTE` の 3 か所）。規程に分量の定めは無い（J11）ので欠陥にはしない。 |
| e 規程への適合 | 4 | J5（ばらつき）、J6・J7（n と精度）は満たす。J9 "set inclusion/exclusion criteria in advance … and stick to them" に対して、§3.4 の "that cannot be explained" が裁量を残す（N-1）。 |
| f 先行研究の位置づけ | 3 | round 2 から変わらない（References は 9 件のまま）。 |
| g 固定の十分さ | 4 | 推定の対象、主要指標、範囲、n の順序、問 4 の判定は 1 通りに決まっている。残りは 3 点: run の中止の判断に定義の無い「説明できる」が入る（N-1）／パイロットの預ける基準が未記載（m11）／`log_truncated` の対象のログ（N8）。 |

## 4. 新しい指摘（重い順）

- [severity: major] 完了した run を、観測（試験の対象）自身の余分な key 行で「中止した試み」にでき、その判断に裁量が残る
  - 位置と引用:
    - §3.4: "A completed run counts as aborted when … one of its logs holds a row without a press the executor sent that cannot be explained (the check of `experiment/data.md`, made before the logs are deposited)."
    - `data.md` 手順 4: "`excess_rows` over all presses must be 0 for the observation and for the reference … a run whose extra rows cannot be explained counts as an aborted attempt and is not analysed"
    - `delivery.py` の selftest: "observation: a duplicate row is counted as excess"
  - なぜ問題か:
    - (a) 観測が同じ打鍵を 2 度書く（重複）は、観測の誤りそのものです。macOS ではこの key 行からセッションを推定するので、重複は偽陽性や分割に直結します。それが run ごと解析から外れて、やり直しの 3 回の中から「きれいな」run が選ばれうる。これは §1.2 の原則 "are reported and are not used to remove trials from the evaluation" と食い違います。§6.3 の "the number of rows without a sent press" も、解析する run では構造上 0 になります。
    - (b) 「説明できる」の中身が事前に決まっていない。J9 "Best practice is to set inclusion/exclusion criteria in advance … and stick to them" に照らして、観測の結果を見てから run を残すか決める余地があります。説明を探すときにセッション行を開いてよいかも書かれていません。
    - (c) 検査の時機が "before the logs are deposited" で、§3.2 "is repeated before the next item of this order is run" と両立が保証されていません。on のセルで見つかったのが off の測定の後なら、順序と入力法の学習の前提が崩れます。
    - G3 にあるとおり、道具自身のログで run の健全さを決めると、確信の根拠を取り違えます。
  - 解消の条件:
    - (1) 観測の余分な行のうち、送った打鍵から決めた許容幅の中にあるもの（重複）は中止の理由にしないと書く。その数は §6.3 の結果として報告し、run は解析する。
    - (2) 中止にする場合を、事前に閉じた一覧で定義する（例: どの送出からも許容幅の外にあり、block の外の上限も超える行＝外からの入力）。
    - (3) 検査は各 run の直後、§3.2 の次の項目の前に行うと書く。
    - (4) 説明を探すときに使ってよいのは、届き方の報告と参照ログだけで、観測のセッション行は開かないと書く。
    - (5) 中止にした run の届き方の数も報告すると書く。
  - 自信: 文と実装の食い違いは高。実際に起きる頻度は低い（パイロットでは入力モードのキー以外はすべて届いた）。

- [severity: minor] 合わせ直しが、試行の中にできた「矢印 4 つちょうど」の並びで 1 ブロックずれ、以後のブロックがすべて採点されなくなる
  - 位置と引用:
    - §6.8: "the assignment resumes at the next block-start marker, which the observer records as four arrow presses, more than any trial sends in a row."
    - `kit\e2\README.md`: "one dropped press in some 100,000 loses one block and shifts no other"
    - `closed_set.py` の `align_blocks`。`open_set.py` も同じ `align_plan` を使う。
  - なぜ問題か:
    - 印は区分の上で `navigation` が 4 つで、どのブロックでも同じです。S7（矢印 3 つ）に余分な矢印が 1 つ入ると（あるいは隣の打鍵の区分が変わると）、ちょうど 4 つの並びができ、錨として認識されます。
    - コードを追うと、ブロック i が合わず `cursor = _next_anchor(cats, nxt_marker, a + 1)` がこの偽の錨に移ります。ブロック i+1 は不一致で、`cursor` は M_{i+1} に移ります。その後は各回、`_next_anchor(cats, marker, cursor)` が `cursor` の位置にある 1 つ前のブロックの印を返します。自分の列も次のブロックの列もそこで一致しないため、元に戻らず、以後のブロックはすべて採点されません。
    - selftest は「矢印 3 つは錨にならない」「印の欠け」「1 つ欠け・1 つ余分」は確かめていますが、この場合は無い。
    - 合わせ直しは、まさに「余分な・変わった打鍵」のための仕組みで、§6.8 の言い方（"sends"）は観測の側を守っていません。凍結の後に見つかると、登録の結果として壊れた値を報告することになります（§8）。
  - 解消の条件:
    - 失敗の後の再開を「錨を順に試し、計画の次のブロックの列全体が一致する最初の錨」に変える（1 つの錨で諦めない）。
    - selftest に「矢印 3 つの S7 に余分な矢印が 1 つ」の対照を足し、失うのがそのブロックだけであることを確かめる。
    - §6.8 と README の文を、観測の側の場合まで含む形に合わせる。
  - 自信: 論理は高（コードを手で追った）。起きる頻度は低。

- [severity: minor] 焦点の喪失の行は「focus_out の行がある試行」だけを数えるので、喪失が続いた試行と、S15 で焦点が戻らなかった場合を拾わない
  - 位置と引用:
    - §6.2: "the trials with such a loss are counted per stratum in the delivery report, and the observation rows assigned to them, and how many of these are false positives, are reported with the detection results, so that a failure of the reference is not read as one of the observer."
    - `delivery.py` の `_focus_losses`（focus_out の時刻を試行に割り当てるだけ。`focus_in` は読まない。参照は `focus_in`／`focus_out` の両方を記録する: `kit\refinput-macos\README.md`）。
    - `pipeline.py`: `scenario != "S15"` を除いたうえで、`_focus_loss` がセル × 比較 × 範囲の合計だけを返す。
  - なぜ問題か:
    - runner が前面を確かめるのはブロックの前だけです。焦点が試行 k で外れて戻らなければ、k+1 からブロックの終わりまで参照は呼び出しを受けません。一方で観測は全打鍵を見ているので、行は偽陽性になります。この後続の試行は一覧に入りません。
    - 試行の間の 1 秒で外れた場合は、どの試行にも付きません。
    - S15 で "return" に失敗した場合は、S15 は除かれ、後続には focus_out が無いので、何も付きません。
    - 主の推定は層ごとなのに、行と偽陽性はセルの合計だけで、層の値を読み替えられません。
    - G3（正常に見えるログが確信を与える）に当たります: 参照のログが「1 回外れた」とだけ言い、その後は正常に見えます。
  - 解消の条件:
    - `focus_out` から次の `focus_in` までを喪失の区間とし、その区間と重なる試行をすべて数える。S15 も、計画した 1 秒を超えて戻らなかった分を数える。
    - その試行に割り当たる行と偽陽性を、層（少なくとも速さ）ごとに出す。
    - §6.2 の文をこの定義に合わせる。
  - 自信: 高

- [severity: minor] 層ごとの設計効果の上限「約 1.8（区間で約 1.34 倍）」は、ブロックごとに層の試行数が違うことを入れておらず、小さすぎる
  - 位置と引用:
    - §6.1: "within a planned stratum the 75 trials are spread over about 42 blocks, so the design effect is at most about 1.8 (an interval at most about 1.34 times wider)"
    - §3.3: "so D is at most about 1.8 … and at most about 1.34 times that"
    - `generate_plan.py`: 速さごとの 1,050 試行を `_shuffle` して `block_size` 25 で切る。
  - なぜ問題か:
    - ブロックあたりの数 m_j が等しくないとき、設計効果は 1 + (Σm_j²/Σm_j − 1)ρ です。
    - 乱数で切ると m_j は超幾何分布（平均 1.79、分散約 1.62）に従い、Σm_j²/Σm_j は約 2.7 になります。ρ = 1 の上限は約 2.7（区間で約 1.64 倍）で、1.8 ではありません。
    - 計画は固定されているので、実際の値は凍結の前に計算できます。
    - J5 "appropriate measures of variability" と G1（区間を明示する）の点で、Wilson を層で使うことの根拠になる量が過小です。
  - 解消の条件: 2 か所の値を、計画から計算した層ごとの Σm_j²/Σm_j の最大（と、それに当たる区間の倍率）に置き換えるか、式と期待値（約 2.7・約 1.64 倍）で書く。
  - 自信: 式は高。2.7 は期待値で、実際の計画の値は中。

- [severity: nit] 速さごとの「1.4〜1.8 点」は、独立を仮定したときの値であることが文の中で分からない
  - 位置と引用: §3.3 "In the primary scope a speed level holds 603 (slow), 852 (mid) and 940 (fast) trials … which locate a recall near 0.95 to within 1.4 to 1.8 points."
  - なぜ問題か:
    - ブロックは 1 つの速さだけで 25 試行なので、速さで合わせた値の設計効果は最大 25（§3.3 自身が連続量について "D between 1 and 25" と書いている）、幅は最大 5 倍です。
    - 次の文が下限と断っていますが、この数は N2 の速さの比較の読みに使われます。
    - recall の分母はセッションで、試行ではありません。
  - 解消の条件: 「試行を独立とみなしたとき 1.4〜1.8 点、速さのブロックの設計効果で最大約 5 倍」と書く（または、速さで合わせた割合にもブロックの再標本の区間を添える）。
  - 自信: 高

- [severity: nit] §6.6 の over_limit の「specified: the same rows」と、§6.9 の「断片の行は時刻だけで対にならない」が互いを参照していない
  - 位置と引用: §6.6 "how they compare with the predicted rows of those trials (`pred_obs`; specified: the same rows)" / §6.9 "a short predicted row, such as the fragment of one key interval after a cut-off, can fail to pair for timing alone."
  - なぜ問題か:
    - over_limit の行の多くは、打ち切りの後の断片（打鍵の間隔 1 つ分、速いときは約 120 ms）です。IoU の対では、回収の遅れ（約 100 ms）だけで対になりません。
    - 「specified: the same rows」の確かめは、数でしか成り立ちません。
  - 解消の条件: §6.6 に「仕様との一致は試行ごとの行の数で見る。対の結果は §6.9 の理由で外れうる」と 1 文添える。
  - 自信: 中

- [severity: nit] `carried_out` が「後の試行で終わる」以外の場合にも立つ
  - 位置と引用: §4.5 "**carried out**: a session that the trial started ends in a later trial" と、`summarise_trials` の `if s["end_trial"] != tid: d["carried_out"] = True`。
  - なぜ問題か: 次のブロックの初めの kana や印の打鍵で打ち切られたセッション（`end_trial` は None）や、ログの終わりで開いたままのセッションでも、`carried_out` が真になります。層 `carried_out` の定義と実装が少しずれます。§3.1 の 188 と 184 の差の一部はこれかもしれません。
  - 解消の条件: §4.5 に「試行の外で打ち切られたものと、ログの終わりで開いているものを含む」と書くか、コードを定義に合わせる。
  - 自信: 中

## 5. 総合の推奨: minor（直してから凍結）

1. 前の round の指摘は 21 件中 15 件が解消、6 件が部分的に解消で、未解消は無い。新しい `long`・`received carry` の定義は、実装・§3.1・§3.3 の数と一致した（表の列の和で確かめた）。
2. ただし直しで 4 つの穴ができた。中でも §3.4 の中止の規則は、試験の対象自身の誤りで run を捨てうる裁量を残していて、凍結の前に必ず直す必要がある（major）。
3. どの穴も解消の条件は局所的で具体的なので、条件どおりに直したかはメインが確かめられる。全体を再査読するほどではなく、凍結の前の修正で足りる。

## 6. 読めなかった範囲と、注入の疑い

### 読んでいない
- **第 1 群**:
  - `plan_config.macos.json`・`config.json`・`gt_rules.json`・`SEED`・`run.sh`・`env.md`
  - `kit\gen\README.md`・`recipes.json`・`recipes.macos-live-off.json`・`keymap_macos.json`
  - `kit\e3\README.md`・`kit\run\README.md`・`kit\pilot\README.md`・`kit\logger\README.md`・`kit\emit\README.md`
- **第 2 群（コード）**:
  - `gt_sessions.py`・`l1.py`・`stats.py`・`run_cell.py`・`clock_sync.py`・`seal_obs.py`
  - Rust の 3 ファイル
  - `l2.py` と `open_set.py` は検索の行だけで、関数の本体は読んでいない。

### 一部だけ読んだ
- **第 1 群**:
  - `kit\e2\README.md`・`kit\refinput-macos\README.md`（検索だけ）
  - `pilot-macos.md`（1〜8 行、38〜41 行、Clocks と Raw logs の節）
- **第 2 群（コード）**:
  - `spec_predict.py`（1〜540 行。selftest は読んでいない）
  - `match.py`（100〜159 行、715〜944 行）
  - `pipeline.py`（180〜199 行、590〜819 行）
  - `delivery.py`（検索だけ）
  - `closed_set.py`（40〜121 行、545〜760 行、1256〜1383 行）
  - `generate_plan.py`（585〜600 行）
- **接地の 3 本**: 該当箇所と検索だけ。

### 全文を読んだ
`preregistration.md`・`notes.md`・`data.md`・`context-A.md`・`carryover-R1.md`。

### 注入の疑い
無し（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。
