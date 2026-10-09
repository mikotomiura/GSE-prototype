# 査読報告 — Behavior Research Methods・原稿の全体・round 2
立場: 打鍵記録から書字過程の指標を計算して使う書字研究の利用者。入力方式を通して書く言語の記録の道具と、打鍵記録から内容が漏れる経路にも通じている。下位人格は「で、読者は何に使えるのか」と問う実務家。

---

## 1. 接地（この立場が論文に求める基準）

**G1 特徴量の定義を明示する（Conijn et al., 2019）。**
- "The selection of the correct keystroke features is crucial for the interpretation of the results and therefore, the derived conclusions."
- "The terminology of these time-based features is sometimes used interchangeably."

ロガーの論文は、どの指標が、どの定義で計算できるかをはっきり書く必要がある。

**G2 時刻の精度は、書字研究が実際に扱う効果の大きさと比べる（Conijn et al., 2019）。**
- "participants paused 36 ms longer between words in the email writing task, compared to the copy task"
- "the mean key press time was 5 ms lower"
- バーストの定義: "without an IKI longer than two seconds and without a revision and without an insertion away from the leading edge"

書字研究の尺度は、2 s の休止の閾値だけではない。数 ms から数十 ms の IKI の差や、押している時間も含む。

**G3 文字を書かないログでも、漏れを評価し、攻撃者の前提を明示する（Monaco, 2018）。**
- "nontrivial information gains can be achieved even in the presence of substantial measurement error"
- "word identification assumes the user types a dictionary word"

**G4 時刻の検証は、経路のどこで測ったかを明示する（Monaco, 2018）。**
- "The temporal resolution and precision of each keystroke depends on the sampling rate of the sensor, where in the processing pipeline it was detected, the speed and scheduling policy of the host computer, and the keyboard itself."

**G5 入力方式を通す書字では、確定の前後の休止が中核の指標である（Crotti et al., 2026）。**
- "IKIs before the characters used to confirm IME candidates (category (d)) and transitions between words that occur after an IME conversion (category (e)) are computed separately"
- "A robust input logger for research should identify these types of IKIs"

**G6 比べる相手の検証の範囲は、相手自身の言葉で扱う（Crotti et al., 2026）。**
- "Given the small sample (two participants), results are only illustrative."
- "We acknowledge that the benchmark we presented validates the proposed DSW algorithm under controlled conditions"

**Crotti との比べ方の公平さ（評価表 f）を本文で照合した結果。** 表 1（related.tex:43-50）の Hybrid logger の行は、相手の本文と一致する。
- 置き場所（Word と Chrome のプラグイン、Inputlog と併用）
- 確定を推論で検出すること
- 確定の前と後の IKI を分けること（相手の (d)(e)）
- key-up と key-down の両方の時刻（相手の Table III）
- 検証の範囲（2 人、1 つの入力方式、画面の録画と照合）

Translog-II の key-up の注 c と、Inputlog 9.5 の版の注 a も、相手の本文どおりである。公平さの残りは nit 1 件だけ（下の n4）。

---

## 2. 評価表

**a 主張と根拠の一致: 3**
- Windows の `abandon` を「upper bound」とする記述が、結果の向き（論理ロガーの放棄率は参照より低い）と逆に読まれる（M1）。
- §7 は、低い ICC を「参照の差が小さいことによる分が、不一致による分と同じくらいある」と説明している（"as much as any disagreement"）。しかし表 13 では、一致の限界の幅が参照のテキスト間 SD の数十倍ある（M2）。
- §10 ¶1 に、原稿が方法の節で自らに禁じた評価の語がある（m1）。
- macOS の不一致が主に規則から来るという推論そのものは、指定行との比較（recall 0.996、一致の限界 −3〜3 ms）で支えられている。

**b 方法の穴: 4**
- 事前登録、凍結、逸脱の記録は厚い。
- 書字研究の利用者の目で残る穴は 2 つ。
  - 確定の時刻（セッションの終わり）と始まりの誤差を分けて見ていない（§10 ¶3 が自ら認める）。G5 の確定の前後の休止に直結する（m2）。
  - 離鍵の時刻を検証していないこと（開示されている）。

**c 持ち帰れるもの: 3**
- 表 4、推奨 (a)〜(f)、データセットの用途の節は、round 1 から大きく改善した。
- それでも、読者がいちばん計算しそうな問 3 のテキストごとの集計値を、Discussion も結論も解釈していない（M2）。
- 「The scales of writing research」の段落は、並べ方の焦点がずれている（m2）。

**d 簡潔さと構成: 3**
- 約 25,900 語。
- Discussion に、結果の節に無い新しい値が初めて出る（m3）。
- 生成された定型の句「no_time near chance on Windows: no」が本文に 3 回出る（m5）。
- §10 ¶4 は §3 と §3.5 の言い直し（n2）。
- §8 の中で「not a criterion of privacy」が 3 回出る（n3）。

**e 規程への適合: 4**
- 満たしている点:
  - 要旨は 248 語（上限 250）
  - Open Practices Statement が References の直前にある
  - Declarations の見出しが揃っている
  - タイトル頁が別ファイル（`submission/title-page.tex`）にある
  - データとコードの文献項目（references.bib:26-40）は、DOI 以外の DataCite の最小の情報を満たす
- 残り:
  - タイトル頁が `\pagestyle{empty}` で頁番号が無い（n5）
  - 表と図に内部の識別子が残っている（m5。"Figures and tables are to be designed as per APA style."）

**f 先行研究の位置づけ: 4**
- 表 1 は公平で、Crotti の中核の次元（確定の前後の IKI）も入った。
- 「尺度」の段落は、書字研究の尺度を休止の閾値だけで代表させている。G2 の ms 単位の IKI の効果を落としている（m2）。

---

## 2b. 引き継ぎの判定（round 1 の 15 行）

| # | 判定 | 根拠（今の原稿の位置と逐語） |
|---|---|---|
| 1 | 一部 | **解消した部分:**<br>・要旨（main.tex:128、132-133）"lowest where the logger's rules predict disagreement" と "lowest in a scenario built to outlast the 20-s cut-off"<br>・results-agreement.tex:170 "What sets the ends of the ranges."<br>・§6.3 と結論にプールした値<br>・§10 を新設<br>**残る部分:** 要旨は依然として区間の端の範囲（0.280–1.000 など）だけで、典型的な一致の大きさ（プールした値は 0.89〜0.91）が要旨だけでは分からない。→ m6 |
| 2 | 一部 | **解消した部分:**<br>・conclusions.tex:58-59 "using the numbers of keys of each category alone: a log that records no text can still reveal which of a few known texts was typed"<br>・recommendations.tex:33-36<br>・recoverability.tex:111-114（counts_only が最大を与えたこと、囮の長さを揃えていないこと）<br>**残る部分:** 要旨に大きさが無い。→ m6 |
| 3 | 一部 | 表 4（logger.tex:159, 161, 162, 165）に "Without overlap only"・"Bounded by pauses only"・"Keys of one document or application & No"・"As window appearances; one conversion can give several rows" が入った。<br>ただし、ログにマウスやポインタの事象が無いことは、§4 にも表 4 にも書かれていない。→ m8 |
| 4 | 解消 | introduction.tex:34-35 と conclusions.tex:10-12 "Which of the two Windows routes drove the measured input method was not determined, the cloaking route depends on the class"。results-agreement.tex:246-247 "the absence of such rows is consistent with the cloaking path, which writes none, but does not show which path drove the input method" |
| 5 | 解消 | table-text-agreement.tex:4 の "-- (reference constant)" と Reference SD の列。results-text.tex:13-17。method.tex:350-351 に D11。<br>（別件として、ICC の解釈の文に新しい問題がある。→ M2） |
| 6 | 一部 | 方法の節に寄せたこと自体はできている（method.tex:345-353）。<br>ただし、結果の節だけを読む読者に向けたプールした Wilson 区間の注意が、§6.3（results-agreement.tex:161-168）と §10 ¶1-2 に無い。→ m4 |
| 7 | 解消 | 記録では「列を足した」となっているが、実際は列ではなく変換の列のセルに入った。related.tex:49 "inter-key intervals before a candidate is confirmed and after a conversion told apart"。自分の行は related.tex:50 "the time of a commit is approximated by the row's time and duration"。注 a と注 b（related.tex:54-57）。実質は満たしている |
| 8 | 解消 | results-agreement.tex:32-40 "What else ran on the machines." |
| 9 | 解消 | recommendations.tex:53-58 の (f)。パスワードへの言及は n6 |
| 10 | 解消 | submission/title-page.tex:29-30（住所と電話の欄は repo の外で記入）。頁番号は n5 |
| 11 | 解消 | references.bib:26-40（DOI は寄託の後の `\tbd`） |
| 12 | 一部 | **残っている内部の識別子と定型の句:**<br>・fig-closed-set.tex:11-19 の凡例 `no_runs`・`bin1s`・`bin1s_count`・`no_time`・`counts_only`<br>・table-closed-set.tex:9-20<br>・table-open-set.tex:10-32 の K0・K1・K1+<br>・results-agreement.tex:237 "(\texttt{over\_limit})"<br>・図 2 の説明文の "(under_limit)"<br>・本文に生成された句 "no_time near chance on Windows: no"<br>→ m5 |
| 13 | 解消 | leijten2013 は references.bib:167 にあるが、本文のどこからも引かれていない（.tex を grep して引用 0 件） |
| 14 | 解消 | related.tex:48 "Key-down only \citep{zou2026}$^{c}$" と注 c（related.tex:58） |
| 15 | 未解消 | README.md:25-27 "## Component staging areas / Subsequent components are built at the following locations." → n1 |

---

## 3. 指摘の一覧（重い順）

### M1 [major] Windows の `abandon` を「upper bound」と表すが、結果は参照より低い向きである

**位置と引用**
- logger.tex:108-109 "so both are upper bounds for the session"
- 表 4、logger.tex:167 "Abandonment & Yes & Upper bound & ..."
- results-agreement.tex:297-298 "so they are upper bounds"
- limitations.tex:23-24 "are upper bounds; this design does not exercise their excess"

**結果の側の値**
- table-session.tex:16-18: Windows の `abandon` の一致は 0.896・0.836・0.824、kappa は 0.629・0.467・0.431。
- table-text-agreement.tex:40-42: テキストごとの放棄率の偏りは −0.074・−0.150・−0.171。区間はすべて 0 より下。
- 参照のテキスト間 SD は 0.16〜0.21。

**なぜ問題か**
- 「upper bound」が述べているのは、数え方の規則の性質である（他のアプリの Escape を数えうる）。測定された量の向きではない。
- 表 4 は「研究者が何を計算できるか」の表である。読者は、Windows の放棄率を「多めに出る」と読んでしまう。実際の測定は、速い速度で参照の放棄率の大半を下回っている。
- Discussion の Windows の段落（discussion.tex:80-86）は、持続時間と recall だけを論じ、放棄には触れていない。
- G1 の観点: "The selection of the correct keystroke features is crucial for the interpretation of the results"（Conijn 2019）。

**解消の条件**
- 表 4、§4.4、§6.4、§13 で、規則の性質と、この研究で観測された向きを分けて書く。例: "counted in any application, so it can exceed the session's; in this study the per-text rate was lower than the reference's at every speed (Table 13)"。
- 偏りが、取り逃した放棄から来るのか、窓が 1 つの変換を複数の行に分けて分母が増えることから来るのかを書く。2×2 表の向きと、シナリオごとの値（補遺）を 1〜2 文で示せばよい。仮説なら仮説と明記する。

**自信: 高**（向きは表の値から確実。原因の切り分けは補遺の Windows の層の表を読み切れていないため中）

---

### M2 [major] 問 3（テキストごとの集計値）の解釈に根拠を超える部分があり、Discussion と結論がこの問に触れない

**位置と引用**
- results-text.tex:17-19 "Where the reference's values vary little between texts, as for these strata and for the fraction of time converting on macOS, a low ICC reflects the small differences between the texts of this design as much as any disagreement."
- 対応する値（table-text-agreement.tex:19）: macOS・live conversion off・slow の Fraction of time converting は Reference SD 0.007、一致の限界 −0.226〜0.113、ICC 0.002。

**なぜ問題か**
- 一致の限界の幅（約 0.34）は、参照のテキスト間 SD の約 48 倍ある。
- 「as much as any disagreement」は量を示さない帰属である。値は、不一致の大きさがテキスト間の差を大きく上回ることを示している。
- 書字研究の利用者がこのログから実際に計算するのは、テキストや書き手ごとの集計値である。たとえば Windows の平均変換時間は −1,395〜−2,343 ms ずれ、ICC は 0.36〜0.50（table-text-agreement.tex:37-39）。それなのに、§10 の 7 段落も §14 も問 3 を解釈しない。
- BRM の規程の逐語: "BRM readers want practical solutions."

**解消の条件**
1. §7 の文を、量で言い換える。例: 「一致の限界の幅は参照のテキスト間 SD の約 N 倍」。
2. §10 に短い段落を足し、4 つの集計値ごとに、偏りの向きと、一致の限界と参照のテキスト間の広がりとの比を記述的に述べる（評価の語は使わない）。
3. 結論の最後の段落に 1 文を足す。

**自信: 高**

---

### m1 [minor] Discussion ¶1 の評価の語（著者の側の点検の指摘は当たる）

**位置と引用**
- discussion.tex:12-13 "The macOS logger detected almost exactly the sessions that its own rules specify for the presses sent, with almost the same durations."
- 同類: discussion.tex:25 "gave the same picture"、discussion.tex:32-33 "thus arise mainly"、discussion.tex:55-56 "by a few milliseconds ... to within the few milliseconds"、discussion.tex:72 "set mainly by its rules"

**なぜ問題か**
- 原稿は method.tex:352-353 で "No threshold of adequate agreement was set, and the estimates are described without evaluative words." と定めている。
- 「almost exactly」「almost the same」は、示されていない基準に照らした近さの判定であり、この自己規定に反する。
- 値（recall 0.996、一致の限界 −3〜3 ms）は強いので、評価の語を足しても主張は強くならない。読者が自分の閾値で読む余地を狭めるだけである。
- 「mainly」は量の主張なので、数で示せる。

**解消の条件**
- 例: "The macOS logger's rows agreed with the rows that its rules specify with pooled recall …, and the limits of agreement of their durations spanned …"
- 「mainly」は、主比較の取り逃しと誤検出のうち、参照と指定行の比較でも同じ扱いになったものの割合で示すか、語を削る。
- 「a few milliseconds」は表 10 の値に置き換える。

**自信: 高**

---

### m2 [minor] 「The scales of writing research」の段落: 並べる量と尺度の取り方が、書字研究の読者にとって部分的にしか役立たない

**位置と引用**
- discussion.tex:98-118。特に 106-108 "the signed error of the intervals between consecutive rows had a median of 0.0 ms, 0.0 ms and 0.0 ms"
- 同じく 111-116 "the durations of the sessions that paired ... were within 100 ms of the reference's in 69.8%–72.0% ..."

**なぜ問題か**
1. **符号つき誤差の中央値は精度を伝えない。** 正負が打ち消し合うので、0 になるのは当然である。精度を伝えるのは表 10 の 5〜95 パーセンタイル（−1〜1 ms）と最大（macOS で ±94 ms。table-key-timing.tex:17）である。
2. **書字研究の尺度は、休止の閾値（250 ms〜10 s）だけではない。** IKI の平均や押している時間では、数 ms から数十 ms の差が報告の単位である（G2: "paused 36 ms longer"、"mean key press time was 5 ms lower"、Conijn 2019）。押している時間は離鍵の時刻を使うが、この研究は離鍵を検証していない。この点を段落で並べていない。
3. **持続時間の一致は、休止の閾値の尺度の量ではない。** 書字研究で関係するのは、確定の前後の休止（G5、Crotti 2026 の (d)(e)）を測るのに、確定の時刻をどれだけ正確に置けるかである。表 4（logger.tex:158）は "Approximate … No" としている。§10 ¶3 は "The beginnings and the ends of the sessions were not compared separately" と認めている。段落を読むと、関連が示されないまま、閾値の尺度で十分かのように読める。
4. **IKI の定義が分かれている。** Crotti は IKI を "the time span or latency between releasing a key and pressing the next one" と定義し、Conijn は Fig. 1 で複数の定義を区別している。表 4 の "Inter-key intervals and pauses between presses" が押下から押下であることと、離鍵を使う IKI は検証していないことを明記していない。

**解消の条件**
- 間隔の誤差は、5〜95 パーセンタイルと最大で示す。
- 尺度として、休止の閾値に加えて ms 単位の IKI の効果の大きさを挙げる（Conijn 2019 を引ける）。
- 持続時間の一致は、休止の閾値ではなく「変換の時間」と「確定の前後の休止」に関わる量として並べ、始まりと終わりを分けていないことを同じ段落で書く。
- 可能なら、探索的な分析として、対になったセッションの終わりの時刻の誤差（確定の時刻の近似の誤差）を既存の対から出す。既存の探索の script と同じ枠でできる。
- 表 4 の IKI の行に「press-to-press; release-based intervals use release rows, which were not validated」を足す。
- なお、torrance2024 の引用（"any threshold a researcher might care to choose between perhaps 250 ms and 10 s"）は、読める一覧に原典が無いので逐語を確かめていない。

**自信: 中〜高**

---

### m3 [minor] Discussion に、結果の節に無い値が初めて出る

**位置と引用**
- discussion.tex:14-24: 指定行と論理ロガーの比較のプールした recall、miss rate、false-positive rate、一致の限界の幅
- discussion.tex:44-50: 層の外の recall と precision（0.960 など）
- discussion.tex:90-95: D12 で値の動いた層の数と最大の変化（"8 of the 36 strata ... by at most 0.080"）
- 一方、discussion.tex の冒頭のコメント（5-6 行）は "A value that the results sections already give is referred to there rather than repeated" としている。

**なぜ問題か**
- APA の構成では、解釈は結果の節の値を参照する。結果の節だけを読む読者は、これらの値を見つけられない。
- D12 の値は deviations.md:302-303 によると "added after the ranges had been seen" である。この経緯が原稿の D12 の記述（method.tex:113-115、表 7 の D12 の行）に無い。→ m7

**解消の条件**
- これらの値を §6.3 か補遺に置き、Discussion は参照する。
- または、新しい値であることと、事前登録の層の出力であること（登録 §6.4 の Layers）を明記する。

**自信: 高**

---

### m4 [minor] 方法の節に寄せた断りのうち、プールした Wilson 区間の注意が結果の節から見つからない

**位置と引用**
- results-agreement.tex:161-168 "Pooled over the strata of the primary scope, recall was …"（たとえば 0.896 [0.883, 0.908]）
- discussion.tex:14-20、44-50 も、注意なしでプールした区間を出している。
- 方法の節の側（method.tex:195-197）: "the design effect of the blocks within a stratum can reach about 3.4, which widens an interval up to about 1.8 times"

**なぜ問題か**
- 結果の節と Discussion の区間は、最大で約 1.8 倍狭く見えている。
- 依頼の「結果と限界だけを読む読者」の観点では、ここが実際の欠落である。限界の節（limitations.tex:72-73）にはこの注意がある。

**解消の条件**
- §6.3 と §10 で最初にプールした値を出すところに、1 句（"Wilson, ignoring clustering; Section 5.8"）を足す。

**自信: 高**

---

### m5 [minor] 内部の識別子と生成された定型の句（引き継ぎ #12 の残り）

**位置と引用**
- recoverability.tex:116、recommendations.tex:36-37、conclusions.tex:54-55 の `\rv{q4.windows.qualification}`。組むと "On Windows the same judgement gives: no_time near chance on Windows: no; counts_only near chance on Windows: no"（main.txt p.39、46、50）になる。
- fig-closed-set.tex:11-19 の凡例 `no_runs`・`bin1s`・`bin1s_count`。方法の節の名前（recoverability.tex:38-40 の *no time*、*1-s bins*、*1-s bin counts*）と一致しない。
- recoverability.tex:132-138 の "K1"・"K1+"・"K0"。本文に定義が無く、table-open-set.tex:4 の説明文も K1 と K1+ しか定義しない。候補の数 $K$ とも記号が衝突する。
- results-agreement.tex:237 "(\texttt{over\_limit})"、図 2 の説明文 "(under_limit)"

**なぜ問題か**
- 推奨と結論は単独で読まれる節である。そこに文として成り立たない句が出る。
- 規程の逐語: "Figures and tables are to be designed as per APA style."

**解消の条件**
- 生成する句を文の形にする。例: "On Windows, neither set met the rule either."
- 表、図、本文の特徴量の集合の名前を、方法の節の名前に統一する。
- 攻撃者の水準は、$K$ と衝突しない名前で本文に定義する。

**自信: 高**

---

### m6 [minor] 要旨が、典型的な一致の大きさと漏れの大きさを伝えない（引き継ぎ #1・#2 の残り）

**位置と引用**
- main.tex:122-140。区間の端の範囲と除いた層の数（"(strata left out: 4 and 6; 4 and 6)"）。Windows の括弧書き（"(3 and 3 strata left out; 21.1% set aside; 0.1% carried over; over all trials 0.000–1.000 and 0.000–1.000)"）。

**なぜ問題か**
- 要旨だけを読む利用者には、典型的な一致が 0.5 なのか 0.9 なのかが分からない。
- 「none is recommended」が、10 候補で 0.90 の同定を意味することも分からない。
- Open Practices（declarations.tex:84-86）は "the rule by which the abstract and the conclusions select their estimates beyond section 6.1 of the registration" を登録外と明記しているので、加えることは登録と矛盾しない。

**解消の条件**
- 除いた層の数などの括弧書き（合わせて 20 語前後）を本文に回す。
- 空いた分で、プールした recall と precision（各セル 1 つ）と、"identified the typed phrase among 10 candidates in 0.90 of trials" を入れる。250 語に収まる。

**自信: 中**（登録 §6.1 の要旨の規則の全文は読んでいない）

---

### m7 [minor] 逸脱 D11・D12 の開示: 原稿の記述が、記録より狭い

**位置と引用**
- method.tex:400-401 "two for reporting, made after all results had been seen"
- 表 7 の D12 の行（method.tex:457-461）

**なぜ問題か**
- deviations.md:302-303 によると、D12 の層ごとの変化の数は "were added after the ranges had been seen, when a review of the discussion found that the per-stratum estimates within the ranges change"。この段階が原稿に無い。
- D11・D12 のきっかけ（deviations.md:271-272、299-300 "a simulated review of the article before its submission"）も原稿に無い。
- D11 の登録の出力の値（0.000）は、本文の "is zero whatever the logger writes" から推せるが、表には出ていない。
- 開示そのものは率直で、規程の "explicitly indicate why, when, and how" の趣旨にはおおむね適う。

**解消の条件**
- 表 7 の D12 の行に「層ごとの変化の数と最大（Discussion）」を足し、それが範囲を見た後に足されたことを書く。
- 2 つの逸脱のきっかけを 1 句で書く。
- D11 の表の注に、登録の出力が 0.000 だったことを書く。

**自信: 高**

---

### m8 [minor] 表 4 に、ポインタとマウスの事象が無いことの行が無い

**位置と引用**
- logger.tex:155-168（表 4）。§4.1 にも記述が無い。
- 関連: logger.tex:161 "The conditions on revisions and on the place of insertion need the text and the cursor"

**なぜ問題か**
- マウスでカーソルを動かした挿入と修正は、このログから見えない。
- G2（バーストの定義の "without an insertion away from the leading edge"）と、Crotti の "invisibly monitoring keyboard and mouse activities" の観点では、利用者が最初に確かめる点である。

**解消の条件**
- 表 4 に "Pointer and mouse actions & No & No & No & Not recorded" の 1 行を足す。

**自信: 高**

---

### m9 [minor] 結論の漏れの一般化に、囮の長さの条件が付いていない

**位置と引用**
- conclusions.tex:58-59 "a log that records no text can still reveal which of a few known texts was typed"
- 条件の側: recoverability.tex:113-114 と limitations.tex:84-85 "The decoys were not matched to the true phrase in length"

**なぜ問題か**
- 結論は単独で読まれる。長さを揃えた候補（たとえば同じ課題の書き写しの文章）では、同定は低くなると原稿自身が予期している。
- G3: "word identification assumes the user types a dictionary word"（Monaco 2018）。攻撃の前提は主張と同じ場所に書く。

**解消の条件**
- "among candidates that differ in length" のような 1 句を足す。

**自信: 高**

---

### m10 [minor] §10 ¶2 の見出しが、示していない発見を約束している

**位置と引用**
- discussion.tex:37 "Disagreements that the registration listed and those it did not."
- discussion.tex:51-52 "this study did not separate them from any that it did not list"

**なぜ問題か**
- 登録していない不一致は、1 つも特定されていない。見出しを読むと、それがあるかのように読める。

**解消の条件**
- 見出しを "Disagreements that the registration listed" にする。

**自信: 中**

---

### n1 [nit] 公開する README に、開発中の言い回しが残っている（引き継ぎ #15・未解消）

- 位置と引用: README.md:25-27 "## Component staging areas / Subsequent components are built at the following locations."
- 解消の条件: 公開版の構成の説明に書き換える。
- 自信: 高

### n2 [nit] §10 ¶4 は §3 の言い直し

- 位置と引用: discussion.tex:69-78。observability.tex:114-128 と §11.4 の繰り返し。
- 解消の条件: 新しい内容（"set mainly by its rules rather than by their implementation" と、データセットでほかの規則を評価できること）を ¶1 に統合する。
- 自信: 中

### n3 [nit] §8 の中で「not a criterion of privacy」が 3 回出る

- 位置と引用: recoverability.tex:57、79、106
- 解消の条件: 方法の 1 回に寄せる。推奨と結論の分は残してよい。
- 自信: 高

### n4 [nit] 表 1 の Hybrid logger の「Text or key names」が "Text" だけ

- 位置と引用: related.tex:49 "& Text \citep{crotti2026} &"
- なぜ問題か: このロガーは Inputlog と併用しており、キーも記録する。CyWrite の行の "Text changes and keystrokes" と書き方が揃っていない。
- 解消の条件: "Text and keystrokes (Inputlog)" にする。
- 自信: 中

### n5 [nit] タイトル頁に頁番号が無い

- 位置と引用: submission/title-page.tex:12 `\pagestyle{empty}`
- 規程の逐語: "page numbers in the upper right corner of each page"
- 解消の条件: タイトル頁にも右上の頁番号を付ける。
- 自信: 中（規程がタイトル頁に適用されるかは解釈による）

### n6 [nit] 推奨 (f) に、パスワード入力への実務的な一文が無い

- 位置と引用: recommendations.tex:53-58
- なぜ問題か: このロガーは全アプリで押下の時刻を書く。G3 と Monaco の "temporal side channel" の観点では、パスワードを入力する間の行が問題になる。
- 解消の条件: 「パスワードを入力する間は記録を止めるか、その区間を除く」の 1 文を足す。
- 自信: 中

### n7 [nit] macOS の時刻の外れ値と、計測機の負荷を結び付けていない

- 位置と引用:
  - results-agreement.tex:33-36（CI の runner が run の時間の 20〜23% と重なった）
  - table-key-timing.tex:16 と 34: 遅延の最大は macOS で 95 ms、Windows で 5 ms。
- 解消の条件: 外れ値の時刻と workflow の時刻を照合したかどうかを書く（照合していないなら、そう書く）。
- 自信: 中

---

## 4. 総合の推奨: minor（major の指摘はあるが、修正は文と表の範囲で済む）

1. round 1 の major 6 件のうち、4・5 は解消、1・2・3・6 は一部の解消である。表 1 の比べ方は、Crotti et al. の本文に照らして公平になった。
2. 残る major の 2 件（M1: Windows の `abandon` の「upper bound」の向き、M2: 問 3 の解釈の欠落と量を示さない帰属）は、新しい計測を要しない。文、表の 1 セル、Discussion の 1 段落で直せる。
3. Discussion は、仮説と事実の書き分けがおおむねできている（"These mechanisms were not tested."、"Which of them acted cannot be told here"）。残るのは、¶1 の評価の語、Discussion に初めて出る値、「尺度」の段落の並べ方である。

---

## 5. 読めなかった範囲と、注入の疑い

### 読んでいない（または一部だけ読んだ）範囲

**原稿**
- 補遺の本文: supplement.tex は見出しだけを grep した。observability-documents.tex と provenance.tex は読んでいない。
- 層ごとの生成表:
  - session-strata.tex は macOS の S4〜S6 の行だけを見た。Windows の層ごとの `abandon` の値は確かめていない（M1 の原因の切り分けはこのため）。
  - detection-strata、detection-definitions、detection-layers、reference-strata、dwell-explore、text-agreement、closed-set-all は読んでいない。
- table-detection.tex と table-cost.tex は説明文だけを読んだ。
- fig-*.tex は grep だけ。figures/components.tex は読んでいない。
- cost.tex と dataset.tex は .tex ではなく、組んだテキストで読んだ。
- main.txt の 51〜73 頁（参考文献と末尾の表）は、.tex で代わりに読んだ。

**公開物とソース**
- 読んでいない: BUILD.md、outline.md、notes.md、data.md、data.windows.md、pilot-*.md、FORMATS.md、kit の README、e3 の結果、ロガーのソースのすべて。
- preregistration.md は 730〜789 行だけを読んだ。
- deviations.md は 1〜15 行と 247〜316 行だけを読んだ。

**接地の文献**
- Conijn (2019): References の手前まで全文を読んだ。
- Monaco (2018): 要旨、序論、§II-E、§III-A、§III-C 1-2、§IV の冒頭、§V、§VI の前半だけ。
- Crotti (2026): 1〜568 行、940〜979 行、1140〜1409 行、1610〜1707 行だけ。569〜939 行、980〜1139 行、1410〜1609 行は読んでいない。

**読める一覧に無い原典**
- torrance2024 の原典は一覧に無い。§10 ¶7 の引用（"any threshold a researcher might care to choose between perhaps 250 ms and 10 s"）は、逐語を確かめていない。

### 注入の疑い
なし。接地の 3 本と、読んだ原稿のファイル、公開物の中に、査読者や LLM に向けた指示の文は見つからなかった。.tex のコメントは著者の覚え書きで、指示ではない。

### 関係するファイル（絶対パス）
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\discussion.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\logger.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\results-text.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\results-agreement.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\recoverability.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\recommendations.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\conclusions.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\limitations.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\method.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\related.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\main.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\generated\table-session.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\generated\table-text-agreement.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\generated\table-key-timing.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\generated\fig-closed-set.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\generated\table-open-set.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\submission\title-page.tex
- C:\GSE-prototype\papers\ime-observation\experiment\deviations.md
- C:\GSE-prototype\papers\ime-observation\README.md
