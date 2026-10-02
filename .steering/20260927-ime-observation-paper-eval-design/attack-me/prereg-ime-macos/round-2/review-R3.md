# R3（BRM の方法論・統計と事前登録の査読者）round 2 の報告

**対象:** `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（round 2 の版）
**総合の推奨:** minor（直してから凍結）。ただし新しい major が 2 件あり、どちらも凍結の前に直す必要がある（5 を参照）。

## 1. 接地: 抜き出した基準

1. **Lakens (2022)、精度で n を決めるとき（l.692–697。行の端のハイフンは戻した）:** "The only aspect a researcher needs to justify for a sample size justification based on accuracy is the desired width of the confidence interval with respect to their inferential goal, and their assumption about the population standard deviation of the measure."
2. **Lakens (2022)、精度の目標が実は検定であるとき（l.747–752）:** "If the goal is indeed to get an effect size estimate that is precise enough so that two effects can be differentiated with high probability, the inferential goal is actually a hypothesis test, which requires designing a study with sufficient power to reject effects"
   - 同 l.731–732: "What is less straightforward is to justify how a desired level of accuracy is related to inferential goals."
   - 同 l.280–282: "even when resource constraints are not the primary justification for the sample size in a study, it is always a secondary justification."
3. **Wicherts et al. (2016)、除外は網羅的に（l.465–469）:** "an ideal preregistration speciﬁcally and precisely describes which types of participants will be excluded from the analyses, and also explicates that the stated rules of exclusion will be the only ones that will be used to discard participants (it should be exhaustive)."
4. **Wicherts et al. (2016)、標本の計画（l.501–503）:** "The sampling plan should also specify when additional participants are to be sampled in cases where the targeted sample size is not met (e.g., due to drop-out or data exclusions)."
   - 同じ表の項目（l.213）: "C3 Correcting, coding, or discarding data during data collection in a non-blinded manner"
5. **Wicherts et al. (2016)、どの変数と推定法を使うか:** l.428–430 "the ideal preregistration should specify which dependent variable(s) will be used in testing particular hypotheses"、l.229 "A14 Choosing the estimation method, software package, and computation of SEs"
6. **Koo & Li (2016)、ICC の型と解釈:**
   - l.52: "researchers should explicitly specify the ICC form they used in their calculation. … The best practice of reporting ICC should include software information, “model,” “type,” and “definition” selections."
   - l.427: "We should use the 2-way mixed-effects model if the selected raters are the only raters of interest."
   - l.479: "there are no standard values for acceptable reliability using ICC."

## 2. 引き継ぎ（carryover-R3.md）の判定

| 指摘 | 判定 | 理由（1 行）・今の版の位置 |
|---|---|---|
| M1 20 秒の打ち切りの扱い | **解消** | 主の範囲を `under_limit` とし、予測から決定的に決める。`over_limit` は別に分析し、問 3 の主は `all_trials`。どれも事前に 1 通りに決まった。コードの `PRIMARY` も同じ組を名指す（pipeline.py:181–183）。位置は §1.2 末段・§4.5・§6.4・§6.6 Cut-off・§7。⚠️ 決めた中身には新しい穴がある（N1・N4）。 |
| M2 E2 の判定規則 | **部分的に解消** | K=1000 を判定から外し、通る確率の表と「両セル × K=10・100」の結合で決まった（§6.8）。残り: 余裕の幅 2/K がプライバシーの上で何を意味するかの根拠が無い（基準 2 の後半の文）。依存の扱いの理由づけ（上端で判定するので一部を吸収する）は成り立たない（N5）。 |
| M3 n の根拠・「agree」の規則 | **部分的に解消** | 幅の表があり、評価の語を使わない（§6.1 第 2 段落）。問 3 を "how closely" にした。ICC が文の混ぜ方の下でだけ成り立つことも書いた（§6.7 第 2 段落）。残り: 一致の限界・kappa・ICC の予想幅が無い。新しく足した「それで何が区別できるか」の 1 文が誤りで、主の範囲では精度の目標にも届かない（N2）。 |
| m1 凍結のハッシュ | **部分的に解消** | 一覧の書式（§9）、5 ファイルの SHA-256 の表、計画の SHA-256（§2.4）、追補の後もタグから回すこと（§8）は入った。残り: 「書き出しの根」（どのディレクトリか）と、一覧を作るコマンドが書かれていない。このため登録する一覧の SHA-256 を読者が計算し直せない。凍結コミットの 40 桁の SHA も登録に入らない（タグは動かせる）。 |
| m2 pooled の重み | **解消** | §6.1 を「件数の和」に直した。⚠️ 主の範囲では層の重みが等しくなくなる（N7）。 |
| m3 依存の扱い | **解消** | 層の中は約 42 ブロックに散ること、pooled は不確かさの下限と読むこと（§6.1）、設計効果の式（§3.3）が書かれ、一貫した。 |
| m4 除外が網羅的か・不測の事態 | **部分的に解消** | "These are the only exclusions" と Other contingencies が入った（§6.2）。残り: 完走した後に欠陥が見つかった run の扱いが無い。登録の外の data.md に、run 単位の関門がある（N6）。 |
| m5 所要時間の食い違い | **部分的に解消** | §3.3・pilot-macos.md:146–159 が揃った。残り: n=75 は本番の打鍵間隔を決める前に決めた（pilot-macos.md:157 "The key intervals of the measurement were set afterwards"）。その後に見直したかどうかが §3.3 に無い。 |
| m6 kappa と LoA の区間 | **解消** | kappa は速さ別に読み、区間を出さない理由も出す。LoA の上下にブロックのブートストラップの区間を付ける（§6.6・l1.py:174–176・183–213）。 |
| n1 ICC の型の名前 | **部分的に解消** | ICC(2,1) = ICC(A,1)、stats.py、二元配置の分散分析を明記した（§6.7）。残り: model（random か mixed か）を書いていない。stats.py:192 は "two-way random" と書くが、比べる 2 方法は「それだけが関心の評定者」なので、Koo は mixed を勧める（基準 6 の l.427）。計算式は同じなので、直すのは解釈の名前だけ。 |
| n2 F1 の区間・2 つの定義 | **解消** | §1.2・§6.1・§6.5 と §5（`same_sessions_as_all`）。 |

## 3. 評価表 a〜g

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | §3.3 の「separates …」は設計で支えられない（N2）。問 3 の主を `all_trials` にした理由が §7 と矛盾する（N1）。§6.8 の「上端で一部を吸収」は統計として成り立たない（N5）。§1.2 の「すべての連続量に区間」はコードと合わない（N3）。 |
| b 方法の穴 | 3 | `long` の定義により、打ち切りの帰結が後の試行を通って主の範囲に残る（N4）。主の範囲では速さごとに層の組成が違う（N7）。run 単位の関門に再実行の規則が無い（N6）。 |
| c 持ち帰れるもの | 4 | 予測を介して「規則の妥当性 `gt_pred`」と「実装の忠実さ `pred_obs`」に分ける方法は、同じ種類の推論型の観測器に使い回せる（J1）。主の組をコードが名指して検査する作り（pipeline.py:181–186・1302–1303）も手本になる。 |
| d 簡潔さと構成 | 3 | 本文は 9,326 語（+76%）。§6.4 の総則（3 範囲 × 3 比較）が §6.6・§6.7 の個別の記述と食い違う（N3）。§7 は §6 の繰り返しが多い。 |
| e 規程への適合 | 4 | J6（n を決めた基準を書く）・J7（精度で設計）・J9（除外を事前に決める）・J8（共変量なし・探索は §6.12）・J3（OSF の URL を予定）に沿う。ただし J7 の精度の目標が主の範囲で満たされないことが書かれていない（N2）。J9 の除外の一部が登録の外の data.md にある（N6）。 |
| f 先行研究の位置づけ | 3 | ICC の表記は Shrout–Fleiss と McGraw–Wong で対応づけた。Koo の model の選び方は反映していない（n1）。near chance の余裕 2/K と、pooled の Wilson を「下限」と読む扱いには、出典も導出も無い。事前登録としては許容できる範囲。 |
| g 固定の十分さ | 3 | 主の比較・範囲・単位は文とコードで 1 通りに決まり、大きく良くなった。残り: 文と凍結するコードの食い違い（問 3 の区間、問 2 の範囲の数、問 3 の比較）（N3）、`long` の定義の文（N4）、run 単位の関門（N6）、書き出しの根（m1）。 |

## 4. 新しい指摘

### N1 [major] 問 3 の主を `all_trials` にした理由が §7 と矛盾し、主の値が設計の打ち切り率で決まる

- **位置と引用:**
  - §6.4 l.503–505「Question 3 is answered under `all_trials` (primary), because the aggregates a researcher computes include the long sessions」
  - §7 l.720–722「how often a session is cut off depends on the design (think time, speed, S6, S13), so the fraction of long trials is a property of this design, not of natural typing.」
  - §3.1 l.215–216「(423 of the 1,050 slow trials, 158 mid and 96 fast)」
- **なぜ問題か:**
  - `all_trials` では、slow（on）の約 40% の試行で、長いセッションが仕様どおり行を出さない。そのため文ごとの変換の回数・平均の変換時間・変換に使った時間の割合の偏りと ICC は、主に設計の考える時間（0.2〜20 s の対数一様）と読みの長さで決まる。§6.7 l.574–576 の速さの混合の偏りも同じで、速さの間の打ち切り率の差（40% / 15% / 9%）をほぼそのまま映す。
  - 「研究者が実際に受ける偏り」という理由は、研究者のデータでの打ち切り率が自然な率であるときにだけ成り立つ。しかし §7 は、この設計の率は自然ではないと書いている。
  - 主の推定量が何を推定しているかの言明が、登録の中で両立していない（基準 5）。
- **解消の条件:** 凍結の前に、次のどちらかを宣言する。
  - (a) 問 3 の主を `under_limit` にし（問 1・2 と揃える）、`all_trials` は設計に依存する副として示す。
  - (b) `all_trials` を主のまま残す。その場合は §6.7 と §7 に次を書く:
    - 主の値（混合の偏りを含む）が、この設計の長い試行の割合に依存すること。予測の割合を速さ別・セル別に §3.1 から載せる。
    - 自然な執筆での偏りの推定ではないこと。
    - 要旨では、この割合と並べてだけ報告すること。
- **自信:** 高（仕組み）／中（大きさ。打ち切りの後の断片の行が一部を打ち消すため）

### N2 [major] n の根拠の推論が誤っており、主の範囲ではさらに目標に届かない

- **位置と引用:**
  - §3.3 l.264–266「With 75 trials a stratum's recall near 0.95 is located to within about 5 points, which separates an observer that misses about one session in twenty from one that misses one in ten, but not finer differences; a speed level (1,050 trials) locates it to about 1.3 points.」
  - §3.3 l.244–246「The number was chosen for the precision of the per-stratum proportions」
  - 表 l.274「| S1 | 34 / 70 / 73 | 44 / 69 / 73 |」
- **なぜ問題か:**
  1. **n=75 でも区別できない（手計算）。** 真の recall が 0.95・n=75 のとき、Wilson の 95% 区間が 0.90 を除くには 73/75 以上の成功が要る。その確率は約 0.27 しかない。観測が 71/75 でも区間は [0.871, 0.979] で 0.90 を含む。「2 つの値を区別する」が目標なら、それは検定であり検出力の設計が要る（基準 2）。
  2. **主の範囲（`under_limit`）では目標から遠い。** slow で 43 試行以下の層は on で 7/14、off で 6/13。半幅は 0.95 付近で 7〜9 点。S1 slow（on）の 34 試行では、34/34 でも下端が 34/(34+1.96²) = 0.8985 で、0.90 を除けない。
  3. **速さの水準の値も違う。** 主の範囲の slow は 1,050 ではなく 627（on）/ 577（off）試行で、半幅は約 1.7 点になる。
  4. **決めた順序が文と記録で違って見える。** pilot-macos.md:154–159 では n=75 が時間の見積もりと並んで決まり、その後に打鍵間隔が決まった。§3.3 は「精度で選び、その後で 1 晩に収まることを確かめた」と書く。資源の制約は少なくとも副の根拠として書くべきである（基準 2 の l.280–282）。
- **解消の条件:**
  - "separates …" を、区間の幅の記述（例:「約 ±5 点で位置を示す。0.95 と 0.90 の区別は保証しない」）に替える。
  - 主の範囲での層の n と半幅を、目標に届く層・届かない層に分けて書く。
  - 速さの水準の n を主の範囲の値に直す。
  - 「n=75 は本番の打鍵間隔を決める前に決め、打ち切り率が分かった後も見直さなかった。資源（1 晩）が副の根拠」と順序を書く。
  - n を増やす必要はない。言えることを設計に合わせればよい。
- **自信:** 高（二項・Wilson を手計算で再計算した）

### N3 [minor] 登録の文と、凍結するコードが計算するものが食い違う

- **位置と引用:**
  - (i) §1.2 l.37「Every proportion and every continuous estimate is reported with an interval」と §6.1 l.431–432「Continuous measures, the limits of agreement, kappa and the ICC carry 95% percentile bootstrap intervals」。一方で l2.py:310–319（`_agree` は Bland–Altman の偏りと LoA を区間なしで返し、区間は `icc21_ci` だけ）と l2.py:385–389（`mixture_bias` の戻り値に区間が無い）。このため、**問 3 の主の推定値（速さ別の偏りと LoA）と混合の偏りに区間が出ない。**
  - (ii) §6.4 l.492「Each analysis of questions 1 and 2 is computed under three scopes」に対し、§6.6 l.544–545「under `under_limit` (primary) and `all_trials`」と pipeline.py:179 `L1_SCOPES = ("under_limit", "all_trials")` は 2 つの範囲。
  - (iii) §6.4 l.508「Each scope is computed for three comparisons」に対し、pipeline.py:47–48・659 は問 3（level 2）を `gt_obs` だけで回す。§6.7 はこれを書いていない。
  - (iv) §1.2 の全称の主張に対し、§6.8 l.605 の平均順位（closed_set.py:401 に区間なし）、§6.10 の CPU・メモリの傾き、§6.9 の時計の差は区間を持たない。
- **なぜ問題か:** 凍結の後に問 3 の LoA に区間を足すと、区間の作り方を結果を見てから選ぶことになる（基準 5 の A14）。登録の文が契約なのに、凍結するコードはそれを出さない。
- **解消の条件:**
  - 凍結の前に、次のどちらかにする。
    - l2.py に、問 3 の偏り・LoA・混合の偏りのブロックのブートストラップ区間を足す（selftest 付き）。
    - または §1.2・§6.1・§6.7 に「区間を付けないもの」を列挙する。
  - §6.4 を「検出は 3 範囲、問 2 は 2 範囲（`over_limit` は §6.6 Cut-off だけ）、問 3 は `gt_obs` だけ」と書き直す。
- **自信:** 高

### N4 [minor] `long` は打ち切られたセッションが「始まった試行」で決まるので、後の試行に落ちた打ち切りの帰結が主の範囲に残る。文はそう書いていない

- **位置と引用:**
  - §1.2 l.58「Questions 1 and 2 are answered for the trials whose session the observer's rules do not cut off」
  - §6.4 l.497–499「the rows that the observer writes after a cut-off (a letter or digit pressed after it opens a fresh session …) are rows of these trials.」
  - spec_predict.py:318–327（`long` は `start_trial` に付く）
- **なぜ問題か:**
  - S6 のセッションは後の試行へ持ち越される（§3.1: on で 188 試行）。その打ち切りが後の試行で起きると、次のものはその試行に属し、`under_limit` に残る: 後の試行のまっさらな断片の行、その試行で失われたセッション、§4.5 の "started none" の試行。このため §6.4 の `over_limit` の説明は、持ち越しの場合に誤りになる。
  - 定義を後から「打ち切られたセッションが重なるすべての試行」に変えたくなる余地が残る（基準 3、基準 4 の A12 の文脈）。
  - 件数は登録に無い。slow・mid で無視できない可能性がある（推測）。
- **解消の条件:** 凍結の前に、次のどちらかにする。
  - 定義を文で正確に書く（「打ち切られたセッションが始まった試行。それが重なる後の試行は `under_limit` に残る」）。§3.1 の予測から、その後の試行の数を速さ別に載せ、§6.4 の `over_limit` の文を直す。
  - または定義とコードと §3.3 の表を「重なるすべての試行」に変える。
- **自信:** 高（コード）／中（件数）

### N5 [minor] §6.8 の依存の理由づけが成り立たず、通る確率の表は「最大値」に当てる規則を表していない

- **位置と引用:**
  - l.636–637「judging by the upper end allows for part of this, and the remainder is stated as a limitation.」
  - l.603–604「the accuracy reported for a feature set is the maximum over that set and every coarser set derivable from it」
  - l.619–620「the probability that a set is judged near chance, when its true accuracy is c/K, is」
- **なぜ問題か:**
  - **依存の理由づけ:** ブロックの中に相関があると広がるのは、上端そのものである。独立を仮定した Wilson の上端で判定すると、相関があるときに near chance と判定しやすくなる（プライバシーにとって危ない向き）。表の c=2 の値 0.024・0.025・0.020・0.019 は、独立の下での片側 2.5% そのもので、設計効果のための余裕が無いことを示している。キットの kit/e2/README.md:96–98・242–243 は "a numeric acceptance margin set by the analysis plan should allow for this" と書くが、登録はそうしていない。
  - **表と規則のずれ:** 推奨に使う値は、粗い集合を含めた最大値（closed_set.py:390–394）である。表は 1 つの二項分布の確率なので、粗い集合を持つ特徴集合では、通る確率を実際より高く示す（ただし安全な向き）。
- **解消の条件:**
  - 文を次のどちらかに替える。
    - (a)「key rows は送った打鍵だけで決まり、句・間隔・おとりは試行ごとに独立に引くので、ブロックの中の相関はほぼ無いと見込む」という論証。加えて、正解率のブロックのブートストラップ区間を記述として併記する（規則は変えない）。
    - (b) 設計効果を数で置いた余裕。
  - 表の注に「1 つの集合の正解率についての確率。最大値で報告する集合では、これが上限になる」と書く。
- **自信:** 高（論理）／中（実際の相関の大きさ）

### N6 [minor] 登録の外に run 単位の関門があり、その後の分岐が決まっていない

- **位置と引用:**
  - data.md:39–43「A run that does not meet this is not deposited until the extra rows are explained, and the finding is reported.」
  - data.md:11「Add one line per run directory after the data has been retrieved from the deposit」（寄託しない run は解析されない）
  - §2.4 l.165–166「a run whose plan has a different SHA-256 is not analysed」
  - §8 l.726–727「… before the affected analysis is run」
- **なぜ問題か:**
  - §6.2 の "These are the only exclusions" の外で、run が解析から落ちる。§3.4 の 3 回の試みに数えるのか、説明できなかったらどうするのか、セルを測り直すのかが決まっていない（基準 4・C3）。
  - 凍結したコード（例: spec_predict.py）の欠陥が `pred_obs` で見つかるのは解析の後である。§8 の「解析の前に記録」は満たせない。
- **解消の条件:**
  - §3.4 か §6.2 に次を書く。
    - 寄託の検査に落ちた run と、計画の SHA-256 が違う run を、中断した試みとして同じ 3 回の規則で数え直す（あるいは解析するが寄託しない、など 1 通りに決める）。
    - 説明できなかったときの扱い。
  - §8 に「凍結したタグの結果を常に登録の結果として報告する。欠陥が分かった後の解析し直しは、逸脱としてその横に示す」を足す。
- **自信:** 高（文）／中（起きる見込み）

### N7 [minor] 主の範囲での速さ別の pooled は、速さごとに組成（シナリオ・読みの長さ）が違う

- **位置と引用:**
  - §6.1 l.426–428「every stratum has the same number of planned trials, so the strata weigh about equally apart from exclusions and the cut-off scope.」
  - §3.3 表（slow on: S6 3・S13 1・S1 34 から S10・S12 の 75 まで）
- **なぜ問題か:**
  - 主の範囲では、slow の pooled の重みは層によって 1〜75 とばらつき、fast はほとんど 63〜75。
  - 間を置かない S3（slow on で 15 試行が長い）・S5・S14 でも長い試行が出る。つまり slow では読みの長い句が抜け、読みの長さの分布が速さで変わる。
  - pooled を速さの間で比べると、速さの効果にシナリオの組成と読みの長さが混ざる。§7 の列挙 "(think time, speed, S6, S13)" には読みの長さが無い。
- **解消の条件:**
  - 「主の範囲での速さ別 pooled は組成が違うので、速さの効果として比べない」と書く（またはシナリオに等しい重みを付けた平均を副として足す）。
  - §7 に読みの長さを足し、主の範囲の読みの長さの分布を速さ別に報告する。
- **自信:** 中〜高

### N8 [nit] §3.3 の Wilson の表の作り方が書かれておらず、書かれたとおりに計算すると一部が合わない

- **位置と引用:** l.251「half-width … of the 95% Wilson interval at the proportion p」、l.259「| 75 | 11.0 | 8.9 | 5.4 | 3.5 |」
- **なぜ問題か:** p をそのまま使うと、n=75 の半幅は 5.3（p=0.95）と 3.2（p=0.99）になる（手計算）。表の値は成功数を整数に丸めた場合（71/75・74/75）と一致する。他のセルはどちらの計算でも合う。
- **解消の条件:** 「x = round(p·n)、全幅の半分」と書くか、計算したスクリプトを名指す。
- **自信:** 高

### N9 [nit] 「4 つの層」は分割ではない

- **位置と引用:** §6.4 l.523–524「for the trials of four layers from the prediction: carried out, started none, closing key in reading, and the trials in none of the three.」
- **なぜ問題か:** 3 つの旗は独立の真偽値で（spec_predict.py:316–317）、1 つの試行が 2 つの層に入りうる。
- **解消の条件:** 重なる試行を各層に数えることを 1 文で書く。
- **自信:** 高

## 5. 総合の推奨: minor（直してから凍結）

- **round 1 からの進み:** round 1 の major のうち M1 は解消し、M2・M3 は部分的に解消した。打ち切りの扱い・判定規則・主の比較と範囲は事前に 1 通りに決まり、コードが主を名指して検査する。固定の核は満たしている。
- **残る穴の性質:** 新しい major（N1 問 3 の主の範囲の理由、N2 n の根拠の推論）と minor は、どれも登録の文と、設計・凍結するコードとの食い違いである。どれにも閉じた形の解消の条件があり、計画の立て直しは要らない。
- **凍結の前に直す理由と、再査読の条件:** 凍結の後では、これらはすべて逸脱か、結果を見てからの選択になる。直した後は、文とコードの機械の照合と、メインの確認で足りる。ただし、問 3 に (a)(b) 以外の道を採る場合や、n や設計を変える場合は再査読が要る。

## 6. 読めなかった範囲・注入の疑い

**全文を読んだもの:**
- preregistration.md
- context-A.md・carryover-R3.md
- config.json・plan_config.macos.json・run.sh・data.md

**一部だけ読んだもの:**
- pilot-macos.md: l.140–164
- pipeline.py・match.py・l1.py: 検索した箇所だけ
- spec_predict.py: l.1–80・276–355
- closed_set.py: l.28–57・336–402・740–760
- stats.py: l.88–227
- l2.py: l.40–79・300–389
- kit/e2/README.md: l.225–259 と検索した箇所
- notes.md・kit/logger/README.md: 検索した箇所だけ

**読んでいないもの:**
- 実験のファイル: gt_rules.json・SEED・env.md
- README: kit の gen・e3・run・pilot・refinput-macos・emit の各 README
- 設定: recipes.json・recipes.macos-live-off.json・keymap_macos.json
- Python: gt_sessions.py・delivery.py・generate_plan.py・run_cell.py・clock_sync.py・seal_obs.py・open_set.py
- Rust: ime_compose.rs・driver_macos.rs・keymap.rs
- 接地の 3 本: 検索した箇所と、上に引いた節のまわりだけ読んだ（全文は読んでいない）

**注入の疑い:** 読んだ範囲には無い。
