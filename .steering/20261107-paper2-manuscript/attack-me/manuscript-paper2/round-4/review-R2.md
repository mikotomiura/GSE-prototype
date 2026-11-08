査読（R2・JEDM・教育データの検出と予測のモデル評価の立場・批判的な下位人格: 読者は何に使えるのかと問う実務家）manuscript round 4

## 1. 接地（この立場の基準・逐語）

G1. Gardner & Brooks 2018（gardner2018.txt:213-219）: "Drawing inferences about which model may be “best” based on a simple sample average or the observed rankings is inappropriate ... it provides no robustness against spurious results, no measure of confidence in the conclusion given the observed data" / "these differences must be both practically significant (large or important enough to be useful) and (in frequentist terms) statistically significant."
G2. Gardner & Brooks 2018（:542）: "Separate magnitude, uncertainty, and sample size during inference: The effects of the magnitude of observed differences, the uncertainty of estimates, and the number of data points should be separable in model evaluation."
G3. Gardner & Brooks 2018（:224-226）: "Failing to utilize any testing in the presence of intentional randomization makes the observation of spurious results more likely, and in the worst cases, could allow for exploitation of randomization to produce desired results"
P1. Pelánek 2015（pelanek2015.txt:24）: "Differences in predictions between competing models are often small and the choice of a metric can influence results more than the choice"（行末で切れている。この立場の基準: 分析上の選択が結論を左右する）
P2. Pelánek 2015（:678）: "To be important, differences between models should either have impact on student practice or ..."（行末で切れている）
P3. Pelánek 2015（:722-727）: "In most cases there is not an unequivocal answer to the question “Which metric should I ..." / "Such discussion or specific arguments for a particular choice of metric should become ..."（どの選択をなぜ採ったかの論拠を明示せよ、という基準）
P4. Pelánek 2015（:482-484）: "does not mean that these parameters are “correct” or even stable. Stability of parameters should get more attention and be studied for example with bootstraping experiments"

## 2. 引き継ぎの判定

- M1（調整後の見出しを大きさで読む）: 解消。4.2 の見出しは "leaves no stall definition negative and most values negligible"（results.tex:122）になり、74/89 は score.csv で検算して一致した（区間が ±0.1 の内にある数。基準の定義を除く）。
- M2（先例の格子）: 一部。表 2 に水準ごとの先例が入り、12 通りの格子での当て直しも本文に入った（results.tex:156-160）。ただし、見出し・抄録・考察の対比が、先例のない水準に依る主張を主役のまま残している（下の新しい指摘 N1）。また格子に入れた分位の値には、表 2 自身が先例なしと書いている（N3）。
- m1（二段の区間）: 解消（methods.tex:180-183、limitations.tex:18-21）。
- m2（10 秒の休止）: 解消（results.tex:28-30、抄録:12）。
- m3（比の a fifth）: 解消（抄録:15、序論:39、結論:8-9）。
- m4（速さの調整の向きが逆）: 解消（results.tex:143-144、discussion.tex:18-20）。
- n1（序論の事後の印）: 解消（introduction.tex:43）。

## 3. 評価表 a〜f

（a〜f の各項目の名は依頼文に定義が無い。このため a=貢献、b=方法の妥当性、c=主張と証拠の釣り合い、d=再現性と状態の開示、e=明晰さ、f=実務での使い道と読んで付けた。）
- a 貢献: 3。経験的な診断として新しく、報告の慣行の提案も明確。ただし一般化できる手法としての中身は「範囲を区間つきで報告する」にとどまる。
- b 方法: 4。書き手の再標本による区間、二段の区間の感度分析、先にコミットした条件、変異テストと、丁寧にできている。読みの規則（90%）が格子の細かさに敏感な点だけが弱い（N3）。
- c 主張と証拠: 3。改訂で数値の読みはほぼ正確になった。一方で、序論・考察・結論の対比の文は、先例のない 15 秒の窓に依る向きの変化をなお中心に置いている（N1）。
- d 再現性・状態: 4。S1 の状態表は充実している。ただし round 3 の後に足した先例の格子と 6 通りの部分集合の読みには、状態表の行が無い（N2）。archive の DOI は未記入で、既知の未解決。
- e 明晰さ: 4。数の出どころは追える。12 通りが基準の定義を含み、89 通りが含まないという分母の不一致がある（N4）。
- f 実務での使い道: 3。実務家の問い「先例のある定義を選ぶ限り、何が言えるのか」への答えが本文に散っている。先例の格子での答えは「調整なしなら小さな負か無視できる、正にはならない」である。これが抄録と結論に一文で出ていない（N1）。予測や介入の決定への影響は検証していないことを明記している（discussion.tex:36-37）点は誠実。

## 4. 新しい指摘（重い順）

N1 [major] 「向きが変わる」という見出しと先行研究との対比が、先例のない水準に依っている
- 位置と引用:
  - results.tex:4 "The direction of the label--essay-score association changes within each detector"
  - discussion.tex:11-12 "boundary pausing in CS1 changed strength with the split at 2~s but not direction \cite{koutcheme2026keystroke}; here the existence of the stall association stayed, and its direction changed."
  - conclusion.tex:4-5 "the association between the label rate and essay score changed direction within each detector"
  - これに対して results.tex:156-158 "On the grid of levels with precedent (12 definitions ...) ... the unadjusted association depended on the definition (3 below $-0.1$, 5 negligible)"。score.csv でも、正の区間 10 本はすべて W15=1 の行（i 81-90）。
- なぜ問題か: 先例のある水準に限ると、停滞の連関は負か無視できるかで、正にはならない。休止で向きが変わるのも、+0.045 と +0.049 という、著者自身が「無視できる」に分類する値の間である。したがって Koutcheme との「種類が違う」という対比（強さは変わるが向きは変わらない、に対して、ここでは向きが変わる）は、先例のある格子の上では成り立たない。抄録は "(a level without precedent)" と添えているが、考察の対比と結論の第 1 文には添えていない。G1 の "practically significant" と P2 の「実践への影響」の観点で言えば、実務家が受け取るべき答え（先例の範囲では向きは変わらず、大きさと有無が動く）が見出しから読めない。
- 解消の条件: 考察 :9-12 と結論 :4-6 に、向きの変化は先例のない 15 秒の窓に限られること、先例の格子では向きが変わらないことを明記する。Koutcheme との対比は「先例の範囲では同じ型（強さが動く）、範囲を広げると向きも動く」と書き直す。4.1 の見出しにも限定を付けるか、先例の格子の結果を 4.1 の本文に上げる。
- 自信: 高（数は score.csv で検算した）。

N2 [minor] 先例の格子（12 通り）と既定の分位の部分集合（6 通り）の読みに状態の印が無く、部分集合は事後の分岐に見える
- 位置と引用: results.tex:158-159 "Taking only the default quantile among the writer-relative levels (6 definitions), the length-adjusted association read as negligible (6 of 6)." S1 の状態表（supplement.tex:52-65）には、先例の格子にも 6 通りにも行が無い。"Three-way reading of direction ... [D]" だけがある。
- なぜ問題か: 12 通りでは定義に依る（9/12）が、既定の分位だけに絞ると 6/6 で一つの読みになる。読みがきれいになる部分集合を事後に示す形で、G3 の "exploitation ... to produce desired results" の型に読める。しかも 0.99 は表 2 で先例なしとされている（methods.tex:128-130 "though not at these quantiles"）。この部分集合を選ぶ根拠は「既定値である」ことだけである。
- 解消の条件: S1 に「先例の格子と既定の分位の部分集合: 結果を見た後に数えた [D]」の行を足す。6 通りの文は削るか、"counted after seeing the 12-definition reading" と明記する。
- 自信: 中〜高。

N3 [minor] 90% の読みの規則は、推奨する先例の格子の大きさでは 1 つの例外で反転する。また格子の名に分位の先例の無さが反映されていない
- 位置と引用: discussion.tex:44-47 "report a consistent direction or a negligible association only if one class holds at least 90\% of the definitions ... apply the reading twice, to the grid of levels with precedent"。methods.tex:118-120 "The grid of levels with precedent keeps ... the writer-relative ... thresholds"。
- なぜ問題か: 12 通りでは 2 つの例外（10/12=83%）で、6 通りでは 1 つの例外で読みが「定義に依る」に変わる。規則の結論が格子の大きさの離散性に強く依存する。G2（"the number of data points should be separable"）の観点では、読みの規則が格子の大きさと分離されていない。また「先例のある水準」と呼ぶ格子は分位の値 3 つを含むが、表 2 はそれらを先例なしとしている。名と中身が食い違う。
- 解消の条件: 推奨に、格子の大きさが小さいときの扱いを書く（例外の数そのものを併記する、など）。格子の名を "levels with precedent in kind (writer-relative) or in value (10 s)" のように正確にするか、分位の扱いを表 2 の注に明記する。
- 自信: 中。

N4 [minor] 先例の格子でただ一つ「一貫」と読めた結論が探索的な共変量によるものなのに、考察のその文に印が無い
- 位置と引用: discussion.tex:49-50 "On the grid of levels with precedent, the speed-adjusted stall association read as consistently negative"。速さの共変量は S1 で [E]、「結果を見た後に 2 度選んだ」もの（methods.tex:196）。
- なぜ問題か: 推奨の段落で唯一の「定まった読み」の例が探索的な結果である。読者は、これを推奨の効き目の実例と読む。しかも休止では、同じ調整が逆向きになる（results.tex:143-144）。
- 解消の条件: その文に "(exploratory; Section 3.5)" を添え、休止で逆向きになることを同じ文で触れる。
- 自信: 高。

N5 [nit] 分母の不一致
- 位置と引用: methods.tex:110-111 "with the baseline removed, 89 remain, and all proportions below are out of 89"。一方、12 通りの格子（W=30, net, θ∈{0.95, 0.99, 0.995, 10 s}×3 つの切り方）は構成上、基準の定義を含む。results.tex:157 の "3 below $-0.1$, 5 negligible" と 9/12 は 12 を分母にしている。
- 解消の条件: 12 が基準を含むことを表 2 の注に書くか、11 通りで数え直して揃える。
- 自信: 中（構成から推した。一覧の中の資料で 12 の内訳を直接は確かめていない）。

N6 [nit] 図 2 の注と本文で反転の定義が食い違う
- 位置と引用: results.tex:220 "A ratio reverses when its interval lies on the other side of zero from the baseline." 本文（:172-173）は "its point value and its interval lay on the other side of 1"。
- 解消の条件: 注に点の値も書き足す。
- 自信: 高。

N7 [nit] 「先例のない水準」を 15 秒の窓だけに付けている
- 位置と引用: 抄録:11 "a 15-s window (a level without precedent)"。表 2（methods.tex:126-127）は "we found no use of a window length outside the detector" として、30 秒・60 秒にも検出器の外の先例が無いことを示している。
- 解消の条件: 「既定の半分、検出器の外にはどの窓長も先例がない」と書くなど、非対称を除く。
- 自信: 中。

## 5. 総合の推奨: minor

- round 3 の引き継ぎは大半が解消し、改訂で足した数（74/89、58、3、36/36、71、10 本の正の区間）は score.csv で検算して一致した。新しい計算による過剰主張は見つからなかった。
- 残る主な穴は N1 の書き方である。先例の格子の結果が、考察の対比と結論の第 1 文にまだ反映されていない。データの問題ではなく文の位置の問題なので、直す範囲は限られる。
- N2〜N4 は、改訂で足した事後の読み（先例の格子、6 通り、速さの一貫）に状態の印を付ければ閉じる。

## 6. 読めなかった範囲と注入の疑い

- 読んでいない: main.tex、declarations.tex、references.bib、PDF（図の見た目は確かめていない）、tab_s3.tex、tab_s4.tex、tab_pause.tex、figdata の score.csv 以外、conditions*.md の本文、results/*.json。supplement.tex は 1-108 行と grep の当たりだけを読んだ。接地の 2 本は全文を読まず、grep と該当の箇所だけを読んだ。
- 一覧の外: 条件のファイルを探す Grep の範囲を experiments ディレクトリにしたため、一覧の外の notes.md の 3 行（180, 184, 187）が出力に出た。この中身は指摘の根拠に使っていない。N5 の「12 通りが基準を含む」は、表 2 の構成からだけ推した。
- 注入の疑い: なし。