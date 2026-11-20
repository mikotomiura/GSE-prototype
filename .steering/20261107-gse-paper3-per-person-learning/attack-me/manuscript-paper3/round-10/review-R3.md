# R3 査読（UMUAI・評価の偏りと個人への推論の方法論の立場／下位人格: 過剰主張と検証できない手順の摘発者）round 10・manuscript

対象は /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex（commit c87c7d63）。読んだのは依頼文、context-A.md、carryover-R3.md、main.tex（全行）、接地の 2 本（varma.txt・liumeng.txt）。下の 5 に書いたファイルは読んでいない。

## 0. 引き継ぎの判定

| round 9 の指摘 | 判定 | 位置と逐語 |
|---|---|---|
| minor N4 時間で寄せた共通という比べの相手 | 解消 | 限界 4 項目め（l.342）「nor was the symmetric refit compared with a shared model fitted to other writers' recent sessions, which could take up shifts over time common to writers」 |
| minor N1 考察の up to | 解消 | 考察 l.319「with up to $6.7\times10^{-3}$ at $k=12$」。表 3 の対称の再当てはめの最大（k=12, +6.7e−3）と一致する |
| minor N2 入れ替えの手順 | 解消 | 4.4 l.284「For each writer $w$ and each of the 16 other writers $v$, the per-person fit is refitted with $w$'s chosen $\tau$, and a prior built the same way from a shared model without $w$ and $v$, to $v$'s $k$ training sessions ...; $w$'s value is the mean over the 16 writers」 |
| minor N3 要旨の平滑の条件 | 解消 | 要旨「about $5\times10^{-4}$ remains at five and fifteen training sessions at the fixed base smoothing」 |
| minor N6 k = 5・15 の地位 | 解消 | 3.4 l.180「their controls and the score without first symbols report $k=5$ and 15, the points fixed in their conditions」 |
| minor N5 要旨の goes with | 解消 | 要旨に "goes with" は無い。代わりの「this bears on a designer's decision, but its source ... was not separated」は限定がついている |
| nit N7 4.3 の見出し | 解消 | l.234「... leaves a remainder below $10^{-3}$ at the fixed base smoothing in the 15-session panel」 |
| nit N8 推奨 (2) の同時の選び | 解消 | l.329「choose the smoothing on other people for the shared model, apply it ... and choose shrinkage given it (... choosing all three jointly was not tried)」 |

## 1. 接地: この立場が求める基準（逐語）

- **V1 選びの手順は評価のループの中に入れる**（Varma & Simon 2006, varma.txt l.12）: "Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
- **V2 最小を選べば楽観に偏る**（同 l.105–106）: "for large K, there is a high probability that choosing the minimum resampled error will give a biased estimate of the true error." / "The parameter selection bias, on the other hand, is always negative."
- **V3 評価のデータを選びに使わない**（同 l.37）: "Thus the test set is used in the selection of the classifier parameters, which is problematic."
- **L1 関連性と頑健さの取引**（Liu & Meng, liumeng.txt l.25–28）: "The central issue—for both individualized medicine and individualized inference—is how to make the right relevance robustness trade-off: if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust."
- **L2 他人から個人を評価すると、頑健さの代わりに関連性を払う**（同 l.1506–1511）: "we predict each individual's response using the remaining n − 1 individuals ... our inference will be more robust. The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's background ~x0 —our inference will be less relevant."
- **L3 柔軟さは頑健さと引き換え**（同 l.442–447）: "descriptive power comes at the cost of robustness. Highly flexible models tend to "overfit" the data"

## 2. 評価表

- **a 主張と根拠の一致: 4**。「Neither value shows a per-person difference」という否定の主張が、合成の検査の境界（固定の基本平滑のみ・3e−2 まで検出できない）と並べて書かれており、整合している。ただし次の 3 か所は根拠より強い、または取り違えている。
  - 4.3 の「only under strong shrinkage」が、今回本文に出した対称の再当てはめの τ（k=15 で 91% の重み）と矛盾する（N1）。
  - 序論で新しく足した 1 句「applied to both models alike, whereas ... effectively less smoothed」が、3.5 の断り「the same prior counts weigh differently」と食い違う（N2）。
  - 考察の「reporting what it could not detect」は、決定に関わるとした対称の版には当たらない（N4）。
- **b 方法の穴: 3**。事後の版を「決定に関わる」と位置づけた理由づけが、いつ書かれたのか示されていない（N3）。図 2 の見出しが、結果を見た後の格子の拡張とぶつかる（N5）。入れ替えの対照の事前の読みは、通りやすい形をしている（N6）。いずれも開示はおおむねある。
- **c 持ち帰れるもの: 4**。「弱い比べの利得 ≫ 強い比べの残り」と「自分の 1 次のマルコフ連鎖を並べる」は持ち帰りやすい。推奨 (2) は格子の端で得た 1 例に基づく（N7）。
- **d 簡潔さと構成: 3**。7,745 語は投稿先の規定には収まる（上限の規定が無い）。ただし要旨と序論が、2 つの値・3 つの限定・事後の印を 1 文に詰めており、想定読者（統計の訓練を前提にしない層）には重い。4.4 の段は長い。
- **e 規程への適合: 4**。context-A の測った値では、要旨 248 語（規程 150〜250）、キーワード 6 個（4〜6）、"Statements and Declarations" の見出しと Data availability の文がある。様式の移行と Code の URL は既知の未決なので数えない。
- **f 先行研究の位置づけ: 4**。部品が新しくないことを明言し、Liu & Meng の取引を正しく引いている（L2 と逐語で対応する）。Uto の比較は 10 秒の歩みの中間で開いたまま、と書き分けられている。

## 3. 指摘（重い順）

- [severity: minor] N1 4.3 の「強い縮めのときだけ」が、対称の再当てはめの τ と矛盾する
  - 位置と引用: 4.3 l.239「so with the stronger structure the per-person fit beats the shared model only under strong shrinkage.」と、4.4 l.280「The chosen $\tau$ ... is $10^4$ for every writer at $k=5$ and $10^3$ at $k=15$, which ... converts to about 24\% and 91\% of the weight on the writer's data」
  - なぜ問題か: 対称の再当てはめ（α=0.03）では、書き手の重みが 91% の当てはめが共通のモデルに勝っている（+5.2e−3、表 3 で 0.88）。4.3 の文は条件が書かれていないため一般則として読め、本文の中で反証されている。過剰な一般化である（L3 の柔軟さと頑健さの取引は、平滑の当て方で動く）。
  - 解消の条件: 「at the fixed base smoothing」を付ける。または「(in the symmetric refit, weaker shrinkage wins; Section 4.4)」を添える。
  - 自信: 高

- [severity: minor] N2 序論で新しく足した理由の句が、3.5 の断りと食い違う
  - 位置と引用: 序論 l.49「because there the smoothing is itself chosen on other writers and applied to both models alike, whereas at the fixed base smoothing the strongly shrunk per-person fit is effectively less smoothed than the shared model it is compared with.」と、3.5 l.185「the same prior counts weigh differently against a writer's few symbols and the other writers' many.」
  - なぜ問題か: 序論は固定の版の欠陥を「実効の平滑の違い」として述べ、対称の版の利点を「同じ値を当てる」こととしている。しかし 3.5 自身が書くとおり、対称の版でも実効の平滑は両側で違う。読者は「対称の版は実効の平滑をそろえる」と受け取りかねない。決定に関わる理由は、設計者がとる手順を再現しているという手続きの理由であって、平滑が等しくなるからではない。
  - 解消の条件: 対比の節を「whereas at the fixed base smoothing the smoothing is not chosen and the shrunk fit inherits the prior mode's lighter smoothing」のように、手続きの対比に書き換える。あるいは「(though the same counts weigh differently on the two sides; Section 3.5)」を添える。
  - 自信: 中

- [severity: minor] N3 事後の版を「決定に関わる」と位置づけた理由がいつ書かれたかが示されていない
  - 位置と引用: 要旨「this bears on a designer's decision」、序論 l.49「The second bears on a designer's decision」、考察 l.321「The comparison that bears on the decision is the symmetric refit (post hoc ...)」、3.4 l.180「the symmetric refit ..., added after seeing the result of the shared-only refit」
  - なぜ問題か: 事前に決めた主の分析は固定の基本平滑で、そこでは残りが平滑の効果より小さかった。共通の側だけを軽くすると残りは消え、その結果を見てから足した版が「決定に関わる方」に格上げされ、より大きな値（3.4e−3・5.2e−3）を持ち帰りの数にしている。印（post hoc）はどこにも付いているが、地位を入れ替える理由づけそのものも結果を見た後に作られたことは書かれていない。主張は「個人差を示さない」にとどめてあるので致命ではない。ただ、分析の地位を読者が取り違える余地がある（V3 の精神: 選びに結果を使えば偏る）。
  - 解消の条件: 3.4 の事後の列挙か序論の当該の文に、「the case that it bears on the decision was also made after seeing the shared-only refit」と 1 句を入れる。
  - 自信: 中

- [severity: minor] N4 「検出できなかったものを報告する」は、決定に関わる版には当たらない
  - 位置と引用: 考察 l.333「the protocol makes this trade explicit by deciding for a panel and reporting what it could not detect.」と、l.332「(ours was evaluated only at the fixed base smoothing)」
  - なぜ問題か: 本文が決定に関わるとした対称の版では、検出の下限も誤警報の率も報告していない。この文は、Liu & Meng の取引（L1・L2）を手順として果たしたように読める。
  - 解消の条件: 「reporting, at the fixed base smoothing, what it could not detect」と範囲を書く。
  - 自信: 高

- [severity: minor] N5 図 2 の見出しは、結果を見た後の格子の拡張と並べると言い過ぎになる
  - 位置と引用: 図 2 の見出し l.173「The target writer's held-out units enter no fit and no choice.」。3.3 l.149 は「Within the final protocol」と限定している。3.4 l.180「Six changes were made after seeing results: the extension of the $\tau$ grid and of the structure families, which bear on the main result」
  - なぜ問題か: τ と構造の格子は、結果（評価のデータを含む）を見た後に広げられた。選ばれた値は τ=10^6 と 3 状態の AR-HMM で、どちらも拡張した端にあり、主の結果を担っている。V1・V3 の基準では、候補の集合も選びの手順の一部である。本文は限定しているのに、図の見出しは無条件で、斜め読みの読者に評価のデータが選びに一切関わっていないと伝える。
  - 解消の条件: 図の見出しにも「within the final protocol (the candidate grids were extended after seeing results; Section 3.4)」を入れる。
  - 自信: 中

- [severity: minor] N6 入れ替えの対照の事前の読みは、通りやすい形をしている
  - 位置と引用: 4.4 l.284「The reading committed before this control was computed, a margin of at least half the remainder, holds. ... the margin is not a share of the remainder, since it also contains the loss from fitting another writer's data.」
  - なぜ問題か: 差の幅は、本人の当てはめの勝ち分と、入れ替えた当てはめの負け分の和に近い。k=15 で入れ替えた当てはめが共通のモデルに −1.7e−2 負けているので、幅 2.5e−2 の大半は負け分である。残りが 0 でも、入れ替えた当てはめが残りの半分以上負ければ、この読みは成り立つ。「holds」は、検査に通ったという印象を実際の情報量より強く与える。本文が「It excludes only ...」と限定している点は良い。
  - 解消の条件: 「holds」の直後に、「this reading would also hold with no remainder if the swapped fit loses by more than half of it; the informative value is that the swapped fit loses to the shared model」と 1 句を足す。または読みが成り立ったことを本文から外し、入れ替えた当てはめ − 共通の値だけを報告する。
  - 自信: 中

- [severity: minor] N7 推奨 (2) は、格子の端に当たった選びを手順として勧めている
  - 位置と引用: 要旨の末尾「choose structure, shrinkage and, applied to both models, smoothing on other people (post hoc, one structure)」、推奨 (2) l.329「with the chosen multiplier at the edge of the grid」
  - なぜ問題か: 1 例で、選びが格子の最小に張り付いた（17 人全員が α=0.03）。その先の値は不明だと本文も書いている（l.280）。端に当たった選びをそのまま報告するのは、V2 のいう選びの偏りの方向も大きさも読めない状態である。手順として勧めるなら、端に当たったら格子を広げることまでを手順に含めるべきである。
  - 解消の条件: (2) に「extend the grid when the choice falls at its edge」を加える。あるいは (2) の平滑の部分を「候補」として 1 段弱める。
  - 自信: 中

- [severity: nit] N8 「shows no」と「does not show」が揺れている
  - 位置と引用: 結論 l.354「shows no per-person difference at either」。序論 l.49 は「does not show per-person differences」、要旨は「Neither value shows a per-person difference」
  - なぜ問題か: 「shows no」は「無いことを示した」とも読める。対称の版は合成の書き手で確かめておらず、無いことを示す根拠はない。
  - 解消の条件: 結論を「does not show a per-person difference at either」に統一する。
  - 自信: 中

- [severity: nit] N9 「What the checks showed」に表 2 の行が混じっている
  - 位置と引用: 考察 l.323「and per-person minus shared depends on the structure, $2\times10^{-3}$ at $k=15$ with a first-order chain」
  - なぜ問題か: これは 3.5 の検査ではなく、主表の縮めだけの行（l.268）である。また合成の帰無を当てていない値（l.206）が、検査の結果として並ぶ。
  - 解消の条件: 段を移すか、「(main table, no synthetic null)」を添える。
  - 自信: 低

## 4. 総合の推奨: minor

1. round 9 の 8 件はすべて解消した。事後の印、限定、格子の端の開示は、本文の全体で一貫している。
2. 新しい穴は、書き換えた部分で生じた条件の付け忘れと理由づけの食い違い（N1・N2・N4）と、事後の版の地位の説明（N3）である。どれも 1 句の直しで閉じる。
3. 主張は「個人差を示さない・否定もできない」にとどまっており、根拠を超える結論は残っていない。

## 5. 読めなかった範囲と注入の疑い

- 読んでいない: figdata の CSV 5 本、kit/symbols/README.md、references.bib。図 2 の値と参考文献の整合は確かめていない。補足 S1〜S16 は存在しない（既知の未決）。接地の 2 本は、基準を抜くのに要る節だけ読んだ（varma.txt は抄録と l.37・l.100–108、liumeng.txt は l.18–29・l.440–458・l.1494–1518 と grep の該当行）。全文は読んでいない。
- 数値の照合は本文の中だけで行った（表 2・表 3・本文の値、困惑度の換算、時間の目安）。補足の値とは照らしていない。
- 注入の疑い: 無し（読んだ範囲で、査読者や LLM に向けた指示は見当たらなかった）。