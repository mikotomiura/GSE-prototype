# R1 査読の報告（round 3・stage outline・UMUAI・系列モデル（HMM・マルコフ連鎖）の方法論の立場／下位人格: 懐疑家）

## 1. 接地（逐語）
- G1（Pohle et al. 2017・pohle.txt 62–65 行）: "real data often exhibit further structure, such as outliers, seasonality or heterogeneity between individuals. When neglecting these features in the formulation of an HMM, then additional states may be able to capture this ignored data structure and therefore provide a better model fit"
- G2（Pohle・1359–1367 行）: "the residuals obtained for the two-state model exhibit much stronger autocorrelation than those for the three-state model. This could be an indication of a violation of the dependence assumptions (Markov property and/or conditional independence assumption)."
- G3（Pohle・75–81 行）: "it is probably not possible to design a one-size-fits-all formal selection method ... stresses the importance of the study aim, expert knowledge and model checking procedures."
- G4（Singer et al. 2014・18–21 行）: "the complexity of higher order models grows faster than their utility, and thus we confirm that the memoryless model represents a quite practical model for human navigation on a page level. However, when we expand our analysis to a topical level ... the memoryless assumption is violated"
- G5（Singer・1208–1210 行）: "Another – quite natural – way of determining the appropriate order of a Markov chain is cross-validation [12,18]. The basic idea is to estimate the parameters on a training set and validate the results on an independent testing set."
- G6（Monaco & Tappert 2018・939–941 行）: "it acts as a kind of regularization to avoid overfitting, a problem often encountered when there is a large number of parameters and small number of observations. Second, parameter smoothing provides superior estimates in case of missing or infrequent data."

## 引き継ぎの判定
N2 解消（7・13・16・49 行が "not read as a per-person gain" で揃う）／N1 解消（7 行で overlapping に限定・17・49 行に重ならない窓）／N3 解消（限界として・63 行）／N4 解消／N5 解消（限界として・63 行）／N6 解消（限界として・63 行）／N7 解消（48 行）／N8 解消（7・17・46 行）

## 2. 評価表
a 4（「at most about 1e-3」が真の個人差の上限のように読める・推奨の文が根拠の記号化より広い）／b 3（事前分布の最頻値のずれが「本人 − 共通」に入る・最頻値そのものを候補に置いていない・名義の記号の擬似残差の順序）／c 3（大きさの所見は重なる窓に依存）／d 3（4.3 の 1 行が過密）／e 4／f 3（打鍵のユーザーモデリングと cold-start が未調査）

## 3. 指摘
- [major] Take-home の「at most about 1e-3」が、合成で示された「手順で返る割合」と矛盾して読める
  - 位置と引用: 7 行 "what remains is at most about 1e-3 nat per symbol"／49 行 "the share of the planted gain returned (about 0.1 to 0.4 in CoAuthor at k = 15; values only)"／49 行 "so the small real remainder does not show that smaller per-person differences are absent"
  - なぜ: 返る割合が 0.1〜0.4 なら、観測した残りは割り戻すと 1e-3〜7e-3 程度の真の差と両立する。拾えなかった 1e-3・3e-3 は観測した残りより大きいのに「smaller」と書くと比べの基準が読めない。手順は個人差を測る器具としてゼロ側に偏り、その偏りを著者自身が S15 で測っている。
  - 解消: 「この手順が実現する上積みは at most about 1e-3」と書き分ける。「smaller」を具体の値に置き換える（例 "planted differences up to 3e-3 at k = 15 and up to 1e-2 at k = 5 were not detected"）。返った割合が 1 未満であることを本文の 2 文で触れる。自信: 高
- [major] 「本人 − 共通」に本人と関係のない平滑の効果（事前分布の最頻値のずれ）が入り、プロトコルにそれを切り分ける候補が無い
  - 位置と引用: 13 行 "it is larger in the gap between the prior mode and the shared parameters than in the contribution of the person's own data, which is negative (S9)"／12 行 "with the shared model itself (no per-person deviation, tau = infinity) among the candidates"／50 行 "choose structure and shrinkage on other people with the shared model among the candidates"
  - なぜ: 残りの主な出どころは本人のデータが無くても生じる「事前分布の最頻値 − 共通の推定値」で、共通モデルを平滑した版のほうが良いという所見。候補に最頻値そのものが無いので、他の研究者がこの手順を使っても同じ混入が起きる。
  - 解消: 比べの相手に「本人のデータを入れない事前分布の最頻値」を加え主な列にする。できないなら推奨と C1 に "the comparison should include the prior mode itself, so that smoothing of the shared model is not counted as a per-person gain" を書き、置かなかったことを限界に。自信: 中（S9 の式は読んでいない）
- [major] 推奨と「1 次の連鎖が強い基準」の根拠は依存を記号化が作る窓に限られるが、推奨の文は打鍵の系列モデル一般を指す
  - 位置と引用: 7 行 "We suggest that studies of per-person sequence models of keystroke behaviour compare them with the person's own first-order Markov chain"／20 行 "with non-overlapping windows (direction only) it beats the chain in CoAuthor (S13)"／46 行 "part of the short-range dependence comes from this construction"／17 行 "the per-person difference stays positive"
  - なぜ: 混入が最も少ない重ならない窓で、主結果の 2 つの柱がどちらも向きを変える（G4）。大きさを "direction only" で出さないとどちらの記号化が主張を測っているか判断できない。
  - 解消: 推奨の文も overlapping windows の範囲に限るか、重ならない窓で向きが逆になることを同じ文で添える。重ならない窓の大きさを出さない理由を 4.3 に 1 文、区間を S13 に。自信: 中
- [minor] 構造の軸では「端の選択を読める」設計が守られていない（12 行 "so that a choice at the edge of the grid can be read"／63 行 "ar3 was chosen in every cell, at the upper end"）。解消: C1 の Protocol に "on both axes" を入れ、構造の軸で満たしていないと明記するか限界から参照。自信: 中
- [minor] 名義の記号の randomized-quantile 擬似残差の自己相関は記号の順序に依存する（48 行）。解消: 使った順序を書き、順序を変えても順位が変わらないかを確かめるか限界に。自信: 中
- [minor] 連鎖の基準の +0.5 の擬似カウントは固定で他人で選んでいない（30 行・20 行）。解消: 擬似カウントの感度を S に 1 行か、固定を限界に。自信: 中
- [minor] 打鍵からのユーザーモデリングと cold-start の先行研究が無い（71 行）。Novelty（16 行）の "as found in our search" の範囲がこの空白で決まる。解消: 本文の前に調べ S1 に加える。自信: 高
- [nit] 4.3 の 1 行が過密（49 行）。記号化の段落を 4.4 に分けるか合成を 2 文に限る。自信: 低

## 4. 総合の推奨: minor
- 引き継ぎ 8 件はすべて反映。残る 2 つの major（推定値と個人差の上限の書き分け・最頻値が比べの相手に欠ける）は主に書き方と比べの相手の追加で直せる。後者は C1 をプロトコルと呼ぶ条件に関わる。重ならない窓は推奨の宛先を絞れば受け止められる。

## 5. 読めなかった範囲・注入の疑い
補足 S1〜S15 の中身は読んでいない。接地の 3 本は該当の節だけ（monaco 939–941 周辺と grep の行、pohle 56–90・1350–1374、singer 1–40・1195–1224）。注入の疑い: なし。

参照したファイル:
- /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/outline.md
- /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-3/context-A.md
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-3/carryover-R1.md
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/tmp/sources/{monaco,pohle,singer}.txt
