# R3（BRM・メタサイエンスと統計の方法論の立場）round 5 の査読

## 1. 接地（文献から逐語で抜き出した基準）

- **W1 精確さと網羅性**（Wicherts et al., 2016）: "each described step should allow only one interpretation or implementation (it should be precise). Finally, a preregistration should exclude the possibility that other steps may also be taken (it should be exhaustive)."
- **W2 前もって書いた構文を 1 回だけ走らせる**（同）: "the syntax for the statistical analyses should preferably be created in advance to be run (once) on the collected data to yield the final statistical results."
- **W3 除外と停止**（同）: "an ideal preregistration specifically and precisely describes which types of participants will be excluded from the analyses, and also explicates that the stated rules of exclusion will be the only ones that will be used"／"C4: Determining the data collection stopping rule on the basis of desired results or intermediate significance testing."
- **L1 精度で n を正当化する**（Lakens, 2022）: "The only aspect a researcher needs to justify for a sample size justification based on accuracy is the desired width of the confidence interval with respect to their inferential goal, and their assumption about the population standard deviation of the measure."
- **L2 パイロットから得た推定値の不確かさ**（Lakens, 2022。Leon et al. の引用）: "Contrary to tradition, a pilot study does not provide a meaningful effect size estimate for planning subsequent studies due to the imprecision inherent in data from small samples."
- **K1 ICC の報告**（Koo & Li, 2016）: "The best practice of reporting ICC should include software information, "model," "type," and "definition" selections."／"it is more appropriate to evaluate the level of reliability based on the 95% confident interval of the ICC estimate, not the ICC estimate itself."

## 2. 引き継ぎの判定

| 指摘 | 判定 | 理由（1 行）と今の版の位置 |
|---|---|---|
| 新 1（§3.4 の規則が 1 通りに決まらない） | 解消 | 4 点とも直っている。(i) 命令行は §3.4:398-399 と data.md:41-42。(ii) ブロックの区間ごとの規則は §3.4:403-421 と `delivery.py` の `_segments`。(iii) exit 2 は §3.4:438。(iv) `pipeline.py` の `analyse` が 904-907 行で `reference_abort_reasons` を使う（§5:561）。計画の SHA-256 だけはコードが照合せず手作業に残る。これは新しい指摘 4 に書いた |
| 新 2（閾値をパイロットの参照のログに当てていない） | 解消 | §3.1:234-247 と、`pipeline.py`:216-224 の定数 |
| 新 3（問 3 の主の範囲が k の混合になる） | 解消（開示） | §6.7:768-776 と §7:983-984。平均の k × テキストの数が、範囲の中の試行の数と合うことを確かめた（例: on・slow で 4.60 × 126 ≈ 580、603 × 1008/1050 ≈ 579） |
| 新 4（§6.6 の仕様との一致を読む統計が無い） | 解消 | §6.6:753-755。§6.4:677 は問 1 を `over_limit` でも計算するので、§6.6 が読む数は実際に出る |
| 新 5（§3.3 の設計効果の段落） | 解消 | §3.3:363-369。計算は合う（1.96/√75 = 0.226、1.96/√31 = 0.352、√3.4 = 1.84）。`plan_figures`（spec_predict.py:574-633）が `ranges`・`max_layer`・`n_blocks_min/max`・`texts_by_speed.histogram` を出すので、値は再現できる |
| nit a（§6.3 と §3.4 の食い違い） | 解消 | §6.3:658-660 |
| nit b（§3.1 の 2 つの約束の書き方） | 解消 | §3.1:189-191 と 225-233 |
| nit c（相殺は検出しない） | 解消 | §3.4:452-455 と §7:986-989 |
| B-1（問 3 の量に抜いた試行の数が混ざる） | 解消 | 新 3 の開示による |

C（共通の変更）について:

- **C1（runner が中止した run にも預ける前の点検を当てる）**: 理由は成り立つ。Ctrl+C や前面の確認の失敗は、人の介入と相関しうる。ただしこの直しで副作用が 2 つ出た（新しい指摘 1・2）。
- **C2（焦点の規則を 2 度改めた）**:
  - データを見てからの分岐（W3 の C4）にはあたらない。結果の値は誰も見ていない。1 度目の改訂はパイロットの参照の側のログ、2 度目は計画から作った oracle で決めた。
  - 観測は 1 回しかないので（約 87 分で 1 回。Poisson の 95% 区間は約 0.03〜5.6 回）、「could abort most runs」という控えめな書き方は L2 に沿っている。
  - 開示（§3.1:251-256）はほぼ足りる。欠けているのは 3 点: 100 ms の根拠（新しい指摘 3）、78% を再現する手段（新しい指摘 7）、500 ms と 100 ms が設計の選択であるという明記。

## 3. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 4 | 規則の記述とコードは、区間・上限・版・焦点の区間のまとめ方・100 ms の差し引きまで一致する。食い違いは 2 つ。(1) pilot-macos.md:189-190 は `--check-deposit` が内容のない形式も検査すると書くが、中止した run には当てない（新しい指摘 2）。(2) §3.4:445-452 の「the rules」は計画の SHA-256 も含むように読めるが、コードはそれを当てない（新しい指摘 4） |
| b 方法の穴 | 4 | 停止の規則は閉じた。新しい穴は 2 か所に限られる。(1) 中止した run を預ける経路（新しい指摘 1・2）。(2) 送出の遅れ 100 ms が、遅れの上限ちょうどに置かれていること（新しい指摘 3） |
| c 持ち帰れるもの | 4 | round 4 から変わらない。`plan_figures` によって §3.3 と §6.7 の数を読者が再現できるようになった |
| d 簡潔さと構成 | 3 | 本文は 14,665 語（+21%）。§3.1 の 2 つ目の項目（234-256 行）は、手順・結果・規則の改訂の経緯を 23 行の 1 段落に混ぜている。停止の規則は §3.4、data.md の手順 1、`pipeline.py` の docstring の 3 か所に書かれ、すでにずれが出ている（新しい指摘 2） |
| e 規程への適合 | 4 | J9（除外を前もって決める）と J6/J7（精度で n を決める）は満たす。J4（生データ）は、中止した run の扱い（新しい指摘 1）で預けられない記録が人のしるしでない理由で増える |
| f 先行研究の位置づけ | 4 | round 4 から変わらない（References は 9 件のまま）。ICC は §6.7:761-765 で、K1 が求める model・type・definition・software を書いている |
| g 固定の十分さ | 4 | 命令行・定数・版・exit 2・検査の対象が 1 通りに決まった。残りは 3 つ。(1) 計画の SHA-256 の照合が手作業（新しい指摘 4）。(2) 「the segment's trials」が終わらなかった試行を含むか（新しい指摘 1）。(3) §3.3:368「Over a speed level (about 1,050 pairs」は全試行の数で、主の範囲では 553〜940 対しかない（半幅は 0.064〜0.083 × SD × √D）。(3) は小さい |

## 4. 新しい指摘

- [severity: minor] 中止した run の点検で、途中で止まった試行の打鍵が「外からの打鍵」に数えられる
  - 位置と引用:
    - §3.4:405-407「minus the presses of the segment's trials that reached the reference」
    - §3.4:448-450「The same check is made on a run that the runner aborted: such a run is never analysed, and it is deposited only if the check passes」
    - delivery.py:40-41「n_reached = the sum, over the measured trials whose trial_begin wall time lies in the segment」
    - delivery.py:95-96（焦点の規則）「(of any trial, measured or not)」
    - run_cell.py:58-59「A child that exits while the run is in progress stops the run at the next key」
  - なぜ問題か:
    - `_segments` は trial_end のある試行（`done`）しか説明に数えない。
    - 試行の途中で止まった run では、その試行の打鍵のうち参照に届いたものが n_unexplained に入る。k = 0 なので、ほぼ必ず「the reference log holds key presses that the measured trials and the procedure do not explain」の理由で預けられない。人のしるしでないのに、人の打鍵を示す理由で記録される。
    - 焦点の規則は終わらなかった試行も数えるので、2 つの規則で扱いが食い違う。
    - 「the segment's trials」が 1 通りに読めない（W1）。
  - 解消の条件: 次のどちらか。
    - 終わらなかった試行の送った打鍵も説明に数える（焦点の規則と揃える）。
    - §3.4 と data.md に「試行の途中で止まった run は点検に通らず預けない」と書き、表でこの理由を区別する。
  - 自信: 高（コードで確かめた）

- [severity: minor] runner が中止した run は、内容のない形式の検査を受けずに預けられうる
  - 位置と引用:
    - pipeline.py:123-124「(e) content in the ground-truth or observation log (the content-free validator), for a run that was not aborted.」（1025-1026 行も同じ）
    - pilot-macos.md:189-190「It applies the same rules and also checks the files for paths and names and the logs for the content-free form.」
    - pilot-macos.md:178-179「A run that the runner aborted is a candidate on the same terms as in the measurement.」
  - なぜ問題か:
    - C1 で、人の介入と相関しうる中止した run に、預ける道を開いた。
    - そうした run にだけ内容の検査が外れている。
    - 文書（pilot-macos.md、data.md:64-69）はこの例外を書いていない。
  - 解消の条件: 次のどちらか。
    - 中止した run にも検査を当てる（例: 切れた最後の 1 行だけ許す）。
    - §3.4・data.md・pilot-macos.md に、例外とその理由を書く。
  - 自信: 高（コード）。重さは中

- [severity: minor] 焦点の規則の 100 ms と、人がいないのに中止にする経路が、パイロットの数で裏付けられていない
  - 位置と引用:
    - §3.4:430-432「counted from 100 ms before the span to its end, so that a press sent just before the span whose row falls inside it is matched」
    - §4.4:503-504「up to about 100 ms after the session ended」
    - §7:994-995「a row that the observer duplicates there makes the run count as aborted without a person」
  - なぜ問題か:
    - 行の遅れが 100 ms を超えると、区間の直前に送った打鍵の行が区間に入る。その打鍵は送った数に数えられないので、人がいなくても中止になる。定数は「about」で書かれた遅れの上限そのもので、余裕が無い。
    - パイロットの 3 run の delivery report には、観測の遅れ（`observation.timing.delay_ms`）がすでにあるのに、§3.1 に書いていない。
    - 参照の key-down が tail（300 ms）を超えて遅れたときも、外からの打鍵に数えられる。この経路も §7 に無い。
    - 原因が系統的なら、3 回とも中止になり、セルは「not measured」になる（§3.4:458）。
    - W1 と、§2.1:88「section 7 states what they do not catch」に照らして足りない。
  - 解消の条件:
    - §3.1 に、パイロットの観測の key 行の遅れの最大と、参照の key-down の遅れの最大を報告する。
    - 500 ms と 100 ms を、その数に照らした設計の選択として明記する。
    - §7 に、この 2 つの経路を「人がいなくても中止にする原因」として足す。
  - 自信: 中

- [severity: minor] 計画の SHA-256 の理由だけはコードが当てないのに、文はすべての規則を当てるように読める
  - 位置と引用:
    - §3.4:445-446「`kit/analysis/pipeline.py` applies the same rules to the delivery report it computes and refuses to analyse a run that they catch」
    - §3.4:450「`pipeline.py --pack` and `--check-deposit` apply the rules to every run directory」
    - §2.4:171-172「a run whose plan has a different SHA-256 is not analysed」
    - pipeline.py の `analyse`（872-907 行）と `_abort_rule_findings` は、§2.4 の値と照合しない
  - なぜ問題か:
    - 計画の違いを止めるのは、data.md の表を手で埋める作業だけである（W2）。
    - 引き継ぎに書かれた見送りの理由（config.json に足すと凍結のハッシュが変わる）は成り立たない。k と同じく `pipeline.py` の定数に置けば、凍結のタグで固定される（§5:552-554）。config.json もハッシュの形式も変わらない。
  - 解消の条件: 次のどちらか。
    - 2 つの SHA-256 を `pipeline.py` の定数にし、`analyse` と `--pack`/`--check-deposit` で照合する。
    - 2 つの文を「the two rules on the delivery report」に狭め、計画の照合は手作業（data.md の手順 1）であると書く。
  - 自信: 中

- [severity: nit] 「捕まえないもの」の一覧が網羅的でない
  - 位置と引用:
    - §2.1:88「section 7 states what they do not catch」
    - pilot-macos.md:187-188 は 2 項目だけを挙げる
  - なぜ問題か: S15 の計画した切り替えの間（約 1 秒 × 225 試行）に人が打っても、どちらの規則にも掛からない。焦点の規則が計画した喪失を外すため。§7:986-995 にこの場合が無い。
  - 解消の条件: §7 に 1 文足す。pilot-macos.md は §7 を参照するだけにする。
  - 自信: 高

- [severity: nit] 「three reasons」と書いた後に 4 つ目の理由がある
  - 位置と引用: §3.4:391-392「for any of three reasons」と、438 行「also counts as aborted」
  - なぜ問題か: data.md:45-48 は 4 つを並べている。§3.4 だけ数が合わない。
  - 解消の条件: §3.4 で 4 つを 1 か所に並べる。
  - 自信: 高

- [severity: nit] パイロットの点検に使ったコードの版が分からない／78% を再現できない
  - 位置と引用:
    - §3.1:231-232「so no defect was found and the code was not changed」
    - §3.1:255「about 78% of the time of a run lies within 500 ms of a press sent」
  - なぜ問題か:
    - closed_set.py の `_is_anchor`・`align_blocks` は、この round で変わった（context-A）。点検がどちらの版で行われたか分からない。きれいなログでは結果は同じなので、影響は小さい。
    - 78% は、一覧のコード（`plan_figures` を含む）では計算されない。
  - 解消の条件: 点検に使ったコミットを書く。78% の計算手順を示すか、kit からは再現できないと書く。
  - 自信: 中

- [severity: nit] `idle` を点検から外す理由
  - 位置と引用: §3.4:439-440「the `idle` condition sends no key and has no plan」
  - なぜ問題か: `idle` では、観測の key 行があればそれはすべて人の打鍵である。それなのに、`idle` の観測のログを残すのか・預けるのかが書かれていない。
  - 解消の条件: 次のどちらか。
    - 預けないと書く。
    - 「key 行が 0」を規則にする。
  - 自信: 低〜中

## 5. 総合の推奨: minor（直してから凍結）

- round 4 の指摘 8 件と B-1 はすべて解消した。停止の規則は、命令行・定数・版・コードの拒否まで 1 通りに閉じた。k = 0・版の選択・焦点の規則の改訂は、結果を見ない較正として開示されており、C4 にはあたらない。
- 新しい穴は、中止した run を預ける経路（終わらなかった試行の扱い、内容の検査の例外）と、100 ms の根拠・誤って中止にする経路の記載に限られる。推定の対象・指標・解析の分岐は変わらない。
- 直すのは文の変更か、コードの小さな変更で済み、再査読は要らない。

## 6. 読めなかった範囲と、注入の疑い

**読んでいない範囲:**
- preregistration.md: §4.1・§4.2、§8・§9、References（変わっていない節）。
- delivery.py: selftest（608 行以降）。
- pipeline.py: selftest の `_case_reference_abort_rule`・`_case_section34_enforcement`、`--pack` の本体。
- l2.py の全体。closed_set.py は Grep の範囲だけ。
- plan_config・config.json・gt_rules・SEED・run.sh・notes.md・env.md、ほかの README、l1・match・stats・gt_sessions・generate_plan・clock_sync・seal_obs・open_set、logger の Rust のソース。
- run_cell.py は 50-71 行と Grep だけ。e3 README は 100-129 行と Grep だけ。

**一覧の外:** 開いていない。Grep はすべて一覧のファイルを 1 つずつ指定した。一覧の外の行は出力に出ていない。

**注入の疑い:** なし。
