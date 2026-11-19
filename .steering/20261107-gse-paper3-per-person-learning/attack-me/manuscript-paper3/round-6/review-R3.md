# R3 round 6 査読（評価の偏りと個人への推論の方法論の立場・UMUAI）

対象は /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex（commit e6fdad49）。行番号はこの版のもの。

## 0. 引き継ぎの判定

| round 5 の指摘 | 判定 | 位置と逐語 |
|---|---|---|
| M-1 「共通に替えて失う精度」の隣に、本人のデータを使わない比べが無い | 解消 | 考察 l.315「Nor does the remainder of about $5\times10^{-4}$ at that smoothing show a value of the writer's data: the prior mode, which uses none of the writer's data, beats the shared model by $7.4\times10^{-4}$, and lightening the shared model's smoothing alone gains $1.6\times10^{-3}$」。結論 l.346 にも同じ趣旨がある。「失う精度」の文は見当たらない。ただし同じ点検を両側の当て直しの値には当てていない（新しい指摘 N-1） |
| m-1 要旨の「Two checks came after seeing results」 | 解消 | l.35「The candidate grids were extended, and two checks added, after seeing results.」（どの 2 つかが分からない点は N-4） |
| m-2 「What was established」の 1 文が逆に読める | 解消 | l.313「Lightening the smoothing of the shared model alone made the remainder vanish; applying the same smoothing to both models (post hoc) brought it back, about 6 and 12.5 times larger at $k=5$ and 15.」（12.5 の丸めは nit N-7） |
| m-3 30-session 群の地位 | 解消 | l.313「The 30-session panel, where the writer's data carry 39\% ... was checked neither against synthetic writers nor with the symmetric refit.」 |
| m-4 結論の最後の文（重ならない窓）に精査が付いていない | 一部 | l.202 には「it was not checked against synthetic writers」と交絡の文があり、ここは解消している。結論 l.346「with non-overlapping windows, which also give far fewer symbols, the three-state HMM is chosen and its per-person fit keeps the direction of a gain」では、データの量のことは書いたが「合成で確かめていない」が落ちている。そのため「keeps the direction of a gain」が地位の印の無い肯定の発見に読める |
| m-5 要旨が検出できなかったことの条件を落とす | 一部（著者の判断どおり） | l.35「planted differences up to $3\times10^{-2}$ were not reliably detected」。「at the fixed smoothing」「under a null added post hoc whose threshold may be too high」が要旨に無い。本文（l.306・l.315・l.346）には在る |
| n-1 remainder の定義と両側の当て直しの食い違い | 解消 | l.176「(in the symmetric refit ..., with the structure fixed at the \arthree{}, which the joint choice picks in every cell of that panel)」。l.278「In the settings reported, the remainder at the fixed smoothing thus vanished only when ...」 |
| n-2 4.4 の見出しに post hoc が無い | 解消 | l.271「... and, post hoc, when the shared model's chosen smoothing is applied to both models」 |

## 1. 接地（この立場が論文に求める基準）

1. 選択の手順の全体を評価の輪の中に入れること。Varma & Simon 2006（varma.txt l.12）"Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
2. 選んだ後の最良値は楽観に偏る。候補が多いほど偏る。Varma & Simon（l.105）"This implies that for large K, there is a high probability that choosing the minimum resampled error will give a biased estimate of the true error." 同 l.106 "The parameter selection bias, on the other hand, is always negative."
3. 差の無いデータ（null）で手順を試し、差が無いのに差が出るかを見ること。Varma & Simon（l.8）"Even though there is no real difference between the two classes for the \"null\" datasets, the CV error estimate ... was less than 30% on 18.5% of simulated training data-sets."
4. 内部の対照（自分のデータから作った複製）は、外部の対照より多くの仮定を背負う。Liu & Meng（liumeng.txt l.341–344）"internal controls are usually of lower quality than external controls because they entail additional assumptions. When uncertainty assessments based on internal replications diverge from those based on external replications, a failure in statistical modelling has occurred, leading to unreplicable research"
5. 個人への推論では、関連性と頑健さの取り引きを明示すること。Liu & Meng（l.102–103）"our inferences can be hurt either by too much matching (not robust) or too little matching (not relevant)."
6. 対照の模様が本物か、ただの人工物かを見分けられないなら、そう言うこと。Liu & Meng（l.272–274）"Prediction algorithms which exploit this feature would do well on our simulated controls; they would do poorly on our actual problem if such a feature turns out to be an artifact. The point is, we have no way to assess whether such a feature is genuine or not"

## 2. 評価表

- a 主張と根拠の一致: 3。固定の平滑での 5e-4 については、本人のデータの価値を示さないと正しく限っている。しかし考察が「判断に関わる比べ」と名指す両側の当て直し（3.4〜5.2e-3）には、5e-4 を退けたのと同じ点検（その平滑での prior mode の効果）を当てていない（N-1）。見出しの「2 桁」も、著者自身が判断に関わらないとした平滑に依っている（N-2）。
- b 方法の穴: 3。選ばれた値が格子の端に集まっている。格子は結果を見た後に広げた。両側の当て直しも結果を見た後である。いずれも書いてはある。ただし比（remainder ÷ smoothing effect）で合成と実データを並べる読みは、比が平滑の強さに依らないという仮定に立っており、その仮定を確かめていない（N-5）。
- c 持ち帰れるもの: 4。「弱い比べの gain」と「強い比べの remainder」の対比、および自分の連鎖を基準に加えるべきだという勧めは、持ち帰れる。
- d 簡潔さと構成: 3。発見 → 確かめた/確かめていない → 決定、という並びは良い。ただ、同じ但し書きが要旨・序論・4.4・考察・結論で形を変えて現れ、読み手が値ごとの地位を追いにくい。記号 α を 2 つの意味で使っている（N-6）。
- e 規程への適合: 4。要旨 248 語（上限 250）、キーワード 6、Statements and Declarations と Data availability がある。語数・頁の上限は規程に無い。様式の移行と URL は既知の未決なので数えない。
- f 先行研究の位置づけ: 4。部品を新規と主張しないと明言し、Varma・Cawley・Liu & Meng・個人化キーボードの先行に正しく帰している。Liu & Meng の要約（l.62・l.325）は、接地の文（基準 5）と整合する。

## 3. 指摘の一覧

- [severity: major] N-1 「判断に関わる比べ」と名指した両側の当て直しの remainder に、5e-4 を退けたのと同じ対照を当てていない
  - 位置と引用: 考察 l.315「The comparison that bears on the decision applies the smoothing chosen on other writers to both models. Done post hoc ... it gives every writer a $\tau$ between $10^2$ and $3\times10^5$, so the writer's data carry at least as much weight as at the fixed smoothing, and leaves a remainder of $3.4\times10^{-3}$ at $k=5$ and $5.2\times10^{-3}$ at $k=15$.」。結論 l.346「When the smoothing chosen on other writers is applied to both models (post hoc), $3.4\times10^{-3}$ to $5.2\times10^{-3}$ remains」。4.4 l.278「this check does not separate the writer's data from other effects of refitting the per-person prior」「$\alpha=0.03$ is the lowest value of the grid, and a lighter smoothing may give more」
  - なぜ問題か: 固定の平滑での 5e-4 は、本人のデータを使わない prior mode（+7.4e-4）と並べて「本人のデータの価値を示さない」と退けた。同じ平滑で 3.4〜5.2e-3 が残るのに、α=0.03 での prior mode の効果は報告していない。α=0.03 は格子の端で、さらに軽い平滑が効く余地を著者自身が認めている。だから、この remainder もまた「共通の模型の平滑の残り」である可能性を、5e-4 のときと同じ論法では排除できていない。それにもかかわらず考察の段は「writer's data carry at least as much weight」と書いて値を続けるので、読み手は本人のデータの価値と読む。4.4 にある「分離できない」の断りが、決定の段と結論に来ていない。この値は合成の書き手でも確かめていない（null なし）。Varma & Simon の基準 3 は、差の無いデータで手順を試してから値を読むことを求める。その null がこの値には無い。
  - 解消の条件: 次のどちらか。(i) α=0.03 の共通模型の prior mode の効果（保存済みの値から出せるなら）を決定の段に並べる。(ii) 決定の段と結論に「この値は本人のデータとその他の当て直しの効果を分けず、格子の端の平滑で、合成で確かめていない。よって本人のデータの価値を示すとはまだ言えない」の 1 文を足し、要旨の推奨の文もそれに合わせる。
  - 自信: 高

- [severity: major] N-2 見出しの「2 桁以上」は、著者自身が判断に関わらないとした平滑での値に依っている
  - 位置と引用: 要旨 l.35「over two orders of magnitude below that gain at five and fifteen training sessions」。考察 l.311「more than two orders of magnitude lower at $k=5$ and 15」。一方 l.315「The comparison that bears on the decision applies the smoothing chosen on other writers to both models.」
  - なぜ問題か: 両側を同じ平滑にした版では 0.188/3.4e-3 ≈ 55 倍（k=5）、0.165/5.2e-3 ≈ 32 倍（k=15）で、2 桁に届かない（約 1.5 桁）。決定の段では「両側を同じ平滑にした比べが判断に関わる」と言いながら、発見の段と要旨の大きさは非対称な固定の平滑で数えている。分析の地位の取り違えであり、強い方の数字を見出しに選んでいる（基準 2 の楽観の向きと同じ）。
  - 解消の条件: 発見の文で「at the fixed smoothing」を大きさの句に付けたうえで、両側の当て直しでは約 30〜55 倍であることを並べる。あるいは見出しを「1.5〜2.5 桁」のように両方を覆う形にする。
  - 自信: 高

- [severity: minor] N-3 要旨の最後の推奨が、根拠の地位（post hoc・1 構造・1 群・格子の端）を落としている
  - 位置と引用: l.35「studies deciding for a group whether to model each person should compare with both baselines and choose structure, shrinkage and smoothing on other people, applying smoothing to both models.」。本文 l.321「(here applied post hoc, to one structure and one panel, with the chosen multiplier at the edge of the grid)」
  - なぜ問題か: 本文の推奨 (2) には条件が付いているのに、要旨では無条件の「should」になっている。また推奨 (3)(4)「needed to read the remainder but were not met here」が要旨に無い。読み手は、要旨の手順で remainder が読めると受け取る。
  - 解消の条件: 語数の許す範囲で「(applied here post hoc)」を足すか、「should」を「we suggest」に弱める。
  - 自信: 中

- [severity: minor] N-4 要旨の地位の印が本文の規約と合わない
  - 位置と引用: l.35「The candidate grids were extended, and two checks added, after seeing results. Synthetic writers without per-person differences left a similar remainder relative to the effect of the shared model's smoothing (not prespecified)」。規約は l.178「we mark the last two \emph{post hoc} where they are reported. Values that the conditions did not ask for are marked \emph{not prespecified}.」
  - なぜ問題か: 要旨では、どの 2 つが後から足されたかが分からない。第二の null の文には「(not prespecified)」（比の地位）しか付いておらず、null そのものが post hoc であることが要旨から読めない。両側の当て直しの文にも post hoc が無い。本文は「post hoc は報告の場所で印す」と定めており、要旨はその場所の一つである。
  - 解消の条件: 該当の 2 文に「(post hoc)」を付け、前の文は「The candidate grids were extended after seeing results」に縮める。
  - 自信: 中

- [severity: minor] N-5 比で合成と実データを並べる読みは、比が平滑の強さに依らないことを仮定している
  - 位置と引用: 4.5 l.306「Relative to the smoothing effect, the remainder is about 0.6 to 1.0 in these synthetic writers ... and 0.56 to 0.97 in the real panel」。限界 l.337「so we read the remainders relative to the smoothing effect, not their raw sizes」
  - なぜ問題か: 合成の smoothing effect は実データの 2.4 倍である。それを比で揃えて読めるのは、remainder が smoothing effect にほぼ比例する場合に限る。その関係は、α 一点の null からは確かめられない。比例しないなら、「similar remainder relative to」は合成と実データの同等性を言えない（基準 4）。round 5 以前に触れていたら重複なので、自信は低くした。
  - 解消の条件: 限界に「比で読むことは、remainder が smoothing effect に比例すると仮定しており、それを確かめていない」の 1 句を足す。
  - 自信: 低

- [severity: minor] N-6 記号 α を「解析の基底平滑の乗数」と「第二の null の生成器の平滑の乗数」の 2 つに使っている
  - 位置と引用: 4.5 l.306「The second null (post hoc) used the multiplier $\alpha=0.03$」。3.5 l.187「all fits use the fixed base smoothing」。推奨 l.324「ours was evaluated only at the fixed base smoothing」
  - なぜ問題か: 両側の当て直しも α=0.03 なので、読み手は「第二の null は α=0.03 の解析で評価した」と読み、推奨 (4) の「固定の平滑でだけ評価した」と矛盾するように見える。地位の取り違えを招く。
  - 解消の条件: 生成器の乗数を別の記号にする（例 α_gen）か、「the generator's base smoothing multiplied by 0.03; fits at the fixed base smoothing」と書く。
  - 自信: 中

- [severity: minor] N-7 結論の重ならない窓の文に「合成で確かめていない」が無い（m-4 の残り）
  - 位置と引用: l.346「the three-state HMM is chosen and its per-person fit keeps the direction of a gain」
  - なぜ問題か: l.202 では確かめていないことを明示しているが、結論にその断りが無いので、肯定の発見に読める。
  - 解消の条件: 「(not checked against synthetic writers)」を足す。
  - 自信: 中

- [severity: nit] N-8 「about 6 and 12.5 times」の丸め
  - 位置と引用: l.313「about 6 and 12.5 times larger at $k=5$ and 15」
  - なぜ問題か: 5.2e-3/4.1e-4 ≈ 12.7 で、「about 13」の方が自然。
  - 解消の条件: 「about 6 and 13 times」にする。
  - 自信: 中

- [severity: nit] N-9 要旨の上限 7e-3 は、本文が「他の列が不安定」とする k=12 の値
  - 位置と引用: l.35「leaves 3 to $7\times10^{-3}$ from five training sessions on」。l.278「The largest value is at $k=12$, where the other columns are unstable」
  - なぜ問題か: 要旨の幅の上端に、不安定とされた点が使われている。考察と結論は k=5・15 の 3.4〜5.2e-3 を使っており、揃っていない。
  - 解消の条件: 要旨を「3.4 to $5.2\times10^{-3}$ at five and fifteen training sessions」に揃える。
  - 自信: 中

## 4. 総合の推奨

minor（ただし N-1 と N-2 は投稿前に必ず直す）
- round 5 の引き継ぎは 8 件中 6 件が解消し、残る 2 件（m-4・m-5）も一部まで進んだ。固定の平滑での 5e-4 を本人のデータの価値と読まない、という線は全体で一貫した。
- 新しい穴の中心は書き直した決定の段にある。「判断に関わる」とした両側の当て直しの値（3.4〜5.2e-3）に、5e-4 を退けたのと同じ対照（その平滑での prior mode・null）を当てずに値を差し出している。見出しの「2 桁」もその対照の無い側の平滑で数えている。
- どちらも新しい計算なしに 1〜2 文で限れる（N-1 の (ii)・N-2 の句の追加）ので、major ではなく minor とした。直さなければ major に相当する。

## 5. 読めなかった範囲と注入の疑い

- 読んだもの: brief-R3.md、context-A.md、carryover-R3.md、main.tex の全文、figdata の fig2_p15_hmm3/ar1/ar3/joint.csv、varma.txt の全文、liumeng.txt の 1〜400 行。
- 読んでいない: references.bib、figdata/fig2_p15.csv、kit/symbols/README.md、liumeng.txt の 401 行以降。そのため、参考文献の書誌の正しさ、記号化キットの説明と本文の整合、Liu & Meng の後半（ピボット・ミニマックス・部分照合の節）と本文の引き方の整合は確かめていない。
- 図 2 の CSV は、本文と表 2 の値（例 joint k=15 の 0.00041、AR3 k=15 の 0.00076、HMM3 k=5 の 0.188）と一致した。
- 注入の疑い: なし。読んだ範囲に、査読者や LLM に向けた指示の文は見当たらなかった。