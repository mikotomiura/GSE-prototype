査読（R1・manuscript round 4・JEDM。打鍵の記録と作文・プログラミングの過程の測定の伝統に立つ査読者。下位人格は、その測定が本当にそれを測っているかを疑う懐疑家）

# 1. 接地: この立場が論文に求める基準（逐語）

- **G1（書き手ごとの閾値と打鍵の速さ）** Guo et al. 2020（guo2020.txt 302–305 行）: "A personalized threshold was necessary, rather than a single fixed threshold for all students, because students vary widely in their typing facility. Because they laboriously enter text letter by letter, poor typists may have many long pauses between keystrokes that are not indicative of planning behavior."
  → 固定の閾値の率は打鍵の速さを運ぶ。速さで調整した結果をどの地位で扱うかが要る。
- **G2（一般化と再現）** Guo et al. 2020（2209–2210 行）: "results may not necessarily generalize to a broader population or to different conditions so replication with other conditions and participant samples is typically recommended."
- **G3（作文の中での時間の位置）** Guo et al. 2020（2214–2216 行）: "our current modeling methods do not address the fact that writing behaviors, such as editing, may change in probability and contribution to essay quality over the course of a writing session"
- **G4（記録の品質による除外の報告）** Guo et al. 2020（526–527 行）: "we removed students whose keystroke logs were not captured correctly"
- **G5（場面をまたいだ特徴の一貫性）** Li & An 2026（bayesmix2026.txt・Discussion）: "establishing feature consistency is an initial first step ( Guo et al., 2018 ), where consistency refers to the extent to which feature properties behave similarly across settings."
- **G6（休止の構成概念の妥当性）** Li & An 2026（Discussion）: "imagine that a student paused 10 s when he was spelling “pen.” This does not reflect he had major cognitive difficulty on spelling. This happens simply because he stretched; or he was distracted"
- **G7（成果の指標の信頼性の報告）** Li & An 2026（3.5 節）: "Inter-rater reliability, measured by Krippendorff’s alpha ( Hayes and Krippendorff, 2007 ), was 0.92, indicating high agreement."

# 2. 引き継ぎの判定

- **M1 解消。** results.tex 122 行の見出しは "Adjusting for essay length leaves no stall definition negative and most values negligible" になった。134 行の「74 of the 89 intervals lay within ±0.1」は score.csv で数え直して一致した（lhi < 0.1 は基準を除いて 74、llo > 0 は 54、0 を含むのは 35）。146–147 行の対比も直っている。ただし 146 行の "uniform in opposite directions" に残る非対称は、新しい指摘の n1 に回す。
- **M2 解消。** methods.tex 179–183・193–195 行と supplement.tex 34–38 行（S1 の 9 行目）は「一段に戻った」と書き、正の通りが 10 → 14 → 10 と動いた経緯も示した。S2（160–171 行）の 74/270＝27% とも合う。
- **M3 解消。** methods.tex 192–193 行と S1 の 7・9 行目に "a first internal pre-submission check" / "a second internal check" とある。
- **m1 解消。** limitations.tex 18–21 行と methods.tex 181–183 行に "not resolved" と "not a comparison" が入り、"did not widen" は消えた。
- **m2 解消。** results.tex 136–137 行を 18 通りで書き直した。round5_length.json の pause36_by_family.fixed.p_both（pos_ci 15・neg_ci 0・incl0 3）と一致する。ただし、この数が要約に届いていない点は新しい指摘の m1 に回す。
- **m3 解消。** results.tex 143–144 行と discussion.tex 18–20 行に、休止の固定の閾値は大半が正（11/18）と書いた。抄録は字数の都合で停滞だけを書く旨が明示されている。
- **n1 解消。** 抄録 12 行に "with values mostly negligible (13 of 18 within ±0.1)" とある。
- **n2 解消。** methods.tex 22–23 行に participant の表記と「KLiCKe の時計の時間ではない」が入った。

# 3. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 問いと貢献 | 4 | 定義の幅を「結論の範囲」として報告する慣行を出す、という主張は明確で、JEDM の "generalizable methodologies" に合う。働く例が 1 コーパス・1 成果に寄っていることは本文が自認している。 |
| b 方法と測定の妥当性 | 3 | 条件を先にコミットする作法と状態の表は丁寧。懐疑家として次の 3 点が残る。休止の家族を長さで調整した結果が 3 値の読みに入っていない（m1）。「先例のある水準の格子」が、表 2 の自己記述では先例の無い水準を含む（m2）。成果（KLiCKe の総合点）の評定者間の信頼性が書かれていない（m3・G7）。 |
| c 結果と主張の一致 | 4 | score.csv で 72/10/7、58/3、中央値 −0.14、W=15 の 10 通り、57/59、長さで調整した 54/35/0 と 74、速さで調整した 71 を数え直し、すべて一致した。残るのは、要約が停滞の側だけを一般化する箇所（m1）と、φ を「CS1 では」と一般化する箇所（m4）。 |
| d 再現性と透明性 | 4 | S1 の順序・状態・逸脱の記録は模範的。DOI は未記入（研究者の保留として扱い、数えない）。 |
| e 位置づけ | 4 | 先行研究の休止の閾値・混合モデル・書き手ごとの閾値の扱いは公平。書き手ごとの閾値（Guo 2020）を格子から外した理由も限界に明記されている。 |
| f 書き方と構成 | 4 | 改訂で密度が上がり、結果 4.2 の「Reading by classes」の段は読むのが重い。新しい矛盾は小さい。 |

# 4. 新しい指摘（重い順）

**m1 [minor・上位] 長さで調整した休止の家族の結果（18 のうち 9 が +0.1 より上）が、3 値の読みと要約から抜けている**
- 位置と引用:
  - results.tex 136–137 行: "For the fixed pause thresholds, 15 of 18 were positive and none negative, and 9 had an interval above $+0.1$."
  - results.tex 150–155 行の読みの列挙は、停滞の長さ・速さの調整と、調整しない休止（"the fixed pause thresholds (13 of 18 negligible)"）だけを挙げる。
  - 抄録 12–14 行、discussion.tex 6 行、conclusion.tex 6–7 行の "Adjusting for essay length left no stall definition negative and most values negligible" は停滞に限っている。
  - round5_length.json 124 行で、固定の閾値の休止を長さで調整した値の中央値は 0.127。
- なぜ問題か: 休止では、長さで調整すると「大半が無視できる」（13/18）から「半数が +0.1 を超える正」へ読みが動く。論文が自ら「adjustment is an axis as well, since it can change the conclusion as a definition can」（discussion.tex 42 行）と言う、まさにその実例である。これを読みの段と要約から落とすと、長さで調整すると関連は消える、という印象が停滞から休止にまで広がる。G5（"feature properties behave similarly across settings"）の観点でも、2 つの検出器が長さの調整に逆の大きさで応えることは報告すべき所見である。
- 解消の条件: 計算は足さない。3 値の読みの段に「休止を長さで調整したもの（9 of 18 above +0.1; 定義に依る）」を加える。考察の "Why the direction can change" にも 1 文入れる。抄録は字数の都合で停滞に限ったままでもよいが、そのときは結論で「停滞では」と範囲を明示する。
- 自信: 高（数は JSON と本文で一致している）。

**m2 [minor] 「先例のある水準の格子」が、表 2 の自己記述では先例の無い水準を含む**
- 位置と引用:
  - 表 2（methods.tex 118–120 行）: "The grid of levels with precedent keeps the default window and condition, the writer-relative and the 10-s thresholds, and the three segmentations (12 definitions)."
  - 同じ表の 126–133 行: window は "we found no use of a window length outside the detector"、θ は "though not at these quantiles"、condition は "neither rule has a use outside the detector"。
  - discussion.tex 46・49 行は、この格子を一般の報告の作法として推奨し、"On the grid of levels with precedent, the speed-adjusted stall association read as consistently negative" と書く。
- なぜ問題か: 12 通りのうち窓・条件・分位の値は、検出器の既定か先例の無い値である。先例があるのは「書き手ごとの閾値という考え」と 10 秒と切り方だけで、名が実体より強い。読者が自分の研究でこの作法をまねるとき、何を「先例あり」とするかの基準がぶれる。
- 解消の条件: 名を "the grid of the default and of levels with precedent" などに改める。あるいは表 2 の脚注で「窓と条件は既定に固定。先例は閾値の型と切り方にだけある」と明記する。
- 自信: 中〜高。

**m3 [minor] 唯一の成果である KLiCKe の総合点の信頼性が書かれていない。「無視できる」の帯（|ρ| < 0.1）を、減衰を考えずに当てている**
- 位置と引用:
  - methods.tex 14–16 行: "each essay was scored by at least two raters, scores two or more points apart were discussed, and the corpus gives the mean, in steps of 0.5"。信頼性の係数は本文にも補足にも無い（"reliab" で grep して 0 件）。
  - methods.tex 157–158 行: "using $|\rho| < 0.1$ as negligible"
- なぜ問題か: 3 値の読みは大きさの境界に依る。成果の信頼性が低ければ、ρ は一律に 0 の側へ縮み、「無視できる」と読まれる定義が増える。G7 のとおり、この伝統では評定者間の信頼性を報告するのが通例である。
- 解消の条件: KLiCKe の原典にある評定者間の一致（あれば）を 1 文で引く。無ければ、限界の "One outcome and its length" に、信頼性が不明で大きさの読みは減衰の下限側にありうる、と書く。
- 自信: 中（KLiCKe の原典は読めていないので、係数が公表されているかは確かめていない）。

**m4 [minor] φ の結論を「CS1 では」と一般化しているが、事前の基準を満たしたのは CS1 の 4 つのセルのうち 2 つ**
- 位置と引用:
  - results.tex 235–237 行: "In the CS1 cells of these data, whether stall counts depart from a constant rate within writers is a property of the definition"
  - 抄録 16 行: "within-writer overdispersion depended on the definition"
  - discussion.tex 33–34 行: "within-writer departure from a constant rate depended on the definition in CS1"
  - 表 3: CS1 2021 assignments は 19（21%）で 25% に届かない。CS1 2019 blocks は "--"（基準の区間が 1.5 を含み数えない）。
- なぜ問題か: 基準を満たしたのは 2019 assignments（54）と 2021 blocks（49）だけで、2021 assignments は 100 個目の間隔より後に限ったときにだけ越える。「CS1 では」は 4 セル全部を指すように読め、地位（[P, A]）以上の範囲を主張している。さらに、主張の語は「1 からの乖離」だが、基準は「1.5 を挟んだ反転」で、物差しも混ざっている。
- 解消の条件: 「CS1 の 4 つのセルのうち 2 つ（時間を限ると 3 つ）で、1.5 を挟んだ判断が定義に依った」と、セルの数と物差しを書く。
- 自信: 高。

**m5 [minor] 時間の位置を見ていない。30 分の固定の時計の下で、終盤の待ち・見直しが停滞の率を作る経路が限界に無い**
- 位置と引用:
  - methods.tex 13–14 行: "with a 30-minute timer and the submit button disabled until 30 minutes had passed"
  - limitations.tex 36–37 行: "because the observation time is nearly fixed in KLiCKe, time spent in stalls reduces the time left for writing"
- なぜ問題か: 書き終えた速い（得点の高い）書き手は、最後の打鍵までの間に見直しや待ちの長い間を作りうる。そうなると、停滞の率と得点の関係の一部、とくに正の隅（W=15 と書き手の分位）や長さで調整した後の正は、作文の終盤という時間の位置で生じている可能性がある。G3 は、行動の意味が作文の経過で変わることを、この伝統の既知の穴として挙げている。G6（休止は必ずしも認知の困難ではない）とも同じ型である。
- 解消の条件: 計算を足さなくてよい。限界に「停滞の時間の位置（序盤の計画・終盤の見直しや待ち）を分けていない。正の隅と長さで調整した正は、その経路と区別できない」と 1 文足す。足すなら終盤の数分を除いた感度だが、それは次の版でもよい。
- 自信: 中（過去の round で触れられたかは、引き継ぎからは分からない）。

**n1 [nit] "uniform in opposite directions" が、2 つの調整の地位の差を隠す**
- 位置と引用: results.tex 146 行 "The two adjustments made the sign of the stall association uniform in opposite directions"
- 速さで調整したものは 89/89 の区間が 0 より下にある。長さで調整したものは負が無いだけで、35/89 の区間が 0 を含む。「長さでは点の値が全部正、区間は 54 が正」と書き分ける。

**n2 [nit] 探索的な速さの調整から、限定の語なしに「一貫して負」と読んでいる**
- 位置と引用: discussion.tex 49 行 "On the grid of levels with precedent, the speed-adjusted stall association read as consistently negative"
- 共変量は結果を見た後に 2 度選ばれている（S1 の [E]）。ここに "(exploratory)" を添える。

**n3 [nit] 12 通り・6 通りの格子は基準を含むが、89 通りの格子は基準を除く**
- 位置と引用: methods.tex 110–111 行 "with the baseline removed, 89 remain" と、表 2 の "(12 definitions)"、results.tex 159 行 "(6 definitions)"
- 「基準を含む」と一言書く。

# 5. 総合の推奨: minor

- 前の round の 8 件はすべて解消した。数え直した数（停滞の 72/10/7・58/3・57/59、長さで調整した 54/35/74、速さで調整した 71）は score.csv・round5_length.json と一致し、改訂で新しい数の誤りは見つからなかった。
- 新しい穴は、要約と読みの段が停滞の側に寄ったこと（休止を長さで調整した正 9/18 の欠落）、名と範囲の書きすぎ（先例の格子・φ の「CS1 では」）、成果の信頼性と時間の位置という測定の注記。どれも文の修正と 1 文の限界で閉じ、計算を足す必要は無い。
- m1 は論文自身の推奨（調整も軸である）を支える所見を落としているので、最初に直す。

# 6. 読めなかった範囲と注入の疑い

- **読んでいない:**
  - main.tex と PDF（図の見た目は確かめていない）。
  - 補足は supplement.tex の 200 行目以降（S3 の後半〜S8）を読んでいない。tab_s3.tex・tab_s4.tex・tab_pause.tex も読んでいない。
  - figdata は score.csv だけを読み、ratio_*.csv・phi.csv・lengths.csv は読んでいない。
  - conditions*.md 9 本は読んでいない。
  - results/*.json は round5_length.json の 1–1776 行だけを読んだ。他の JSON は読んでいない（休止の 13/18・9/18 の定義ごとの値は、この範囲では確かめていない）。
  - guo2020.txt は 1–2010 行と 2200–2249 行だけを読んだ（付録と表の残りは読んでいない）。
  - references.bib は読んでいない。
- **一覧の外に触れた:** 一覧の外にある `[一覧の外のパス・保存時に伏せた]` が、Grep（experiments の下で「先例|precedent」を検索）の結果として 3 行表示された。意図して開いたものではなく、指摘の根拠には使っていない（m2 は表 2 の本文だけに基づく）。
- **注入の疑い:** なし。