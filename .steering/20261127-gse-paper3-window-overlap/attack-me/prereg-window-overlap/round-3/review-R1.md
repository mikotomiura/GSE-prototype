# 査読 R1 round 3（行動の記号列の系列モデルの方法論・paper-reviewer / opus）

## 1. 接地
- B1 Pohle 2017（67-69）"When neglecting these features in the formulation of an HMM, then additional states may be able to capture this ignored data structure and therefore provide a better model fit"・（990-991）"it may just as well be an indication that the additional states merely mop up some structure missing in the model"
- B2 Pohle 2017（949-952）"the residuals obtained for the two-state model exhibit much stronger autocorrelation than those for the three-state model. This could be an indication of a violation of the dependence assumptions"
- B3 Singer 2014（87-93）"It is difficult to make plausible statements about the appropriate Markov chain order having insufficient data but a vast amount of states … the number of parameters grows exponentially with the chain order and the available data is too sparse for proper parameter inferences"
- B4 Singer 2014（610-613）"One disadvantage of cross validation methods usually is that the results are dependent on how one splits the data"
- B5 Monaco & Tappert 2018（730-733）"The effect is to bias parameters that depend on event types with low frequency toward the marginals … while parameters that depend on event types with high frequency will remain unchanged"
- B6 Monaco & Tappert 2018（163-166）"Typing behavior generally evolves over time … A user's keystroke dynamics is also generally dependent on the typing task"

## carryover の判定
- 7 件すべて解消（決定表 156-163・作りの確かめ 40/152/241・φ と P-READ 122-124/228・150・175・201・依頼文）。

## 2. 評価表
- a 4: 言い方の限りは厳しい。「歩みに沿う」は覆う時間の長さの違いまで歩みのせいにする（指摘 1）。
- b 3: C′ と τ 固定の行は入った。R_ar3 の縮みの床（指摘 2）と覆う時間の交絡（指摘 1）が読みの語に届いていない。
- c 4: 列 C と φ は S13 の未決を直接に切る。境の歩みも実務に持ち帰れる。
- d 3: 255 行で添えの句が 5 種類。
- e 4: 作りの確かめが外れたときの論文の文が 1 通りでない（指摘 6）。
- f 3: B3 と B5 が読みの限界として位置づけられていない。
- g 4: 残りは φ > 1 と stay_R が大きく負の語（指摘 4）と作りの確かめが外れたときの文（指摘 6）。

## 3. 指摘
- [major] 1 「歩みに沿う」は同じ記号の数で覆うセッションの時間の長さとも交絡する
  - 位置: 53・124・18・240・186 行
  - 理由: 記号の数を固定すると覆う時間は「記号の数 × 歩み」で歩みと 1 対 1。C30 は A30 の約 1/30 の時間。連続した短い区間は非定常（B6）で中身がそろいやすく、従属が強く実効の標本が小さい（B3）。C′ は位置だけ。読む人は従属が効いたと受け取る。
  - 解消: (i) 言い方の限り・φ の定義・型の名・持ち込みの全文で「歩み（窓の重なり・予測の先の長さ・同じ記号の数で覆う時間の長さ。この試験は分けない）」と書く。または (ii) 列 D（歩み 1 の短い連続の束〔例 10 行〕をセッション全体に等間隔に散らした列）を足す（足すなら再査読）。
  - 自信: 高
- [major] 2 R_ar3 の「小さい」は縮みの作りだけでほぼ必ず出る
  - 位置: 141・82・168 行・main.tex 335 行 "a strongly shrunk fit (0.06 to 3% of the weight on the writer's data)"・開示 33 行
  - 理由: ar3 は母数が多く、他人で選んだ τ で本人 ar3 は共有へ強く縮む（B5）。記号の少ない A30・C30 ではなおさら（B3）。どの歩みでも R_ar3 ≈ 0 で「小さい」になり、型 1 と 2 の分かれ目が τ の選びで決まりうる。仕組みの後半が反証されうる形でない。
  - 解消: (a) τ = 10,000 の固定の行での R_ar3 の語も添えの句に (b) 列ごと・構造ごとの選ばれた τ でのデータの重み N/(N+τ) の中央値を主の表に (c) 限界に「R_ar3 の『小さい』は縮みの床からも出うる」 (d) 型 1 の文で、固定の τ でも R_ar3 が「小さい」のときだけ「構造を ar3 に固定した比べでは小さかった」、そうでなければ「（他人で選んだ縮みのもとで）」と限る。
  - 自信: 中
- [minor] 3 型 1 の文が、仕組みの環の 1 つが既に逆向きと分かっていることを添えない（241・186 行）。B2。解消: 型 1・2・2′ の文に「本人 hmm3 の擬似残差の遅れ 1 の自己相関は共有と同じ程度で（副の量）、得は本人の当てはめが従属を運んだことからは来ていない」に当たる句。自信: 高
- [minor] 4 φ > 1 と stay_R が大きく負の場合の語が意味とずれる（128・143 行）。解消: φ(30) > 1 で「（φ > 1: 記号の数をそろえた区間の得が歩み 1 の全体の得を越えた）」を添え、R_ar3 に「逆」（stay_R(30) ≤ −stay_G(30)/4）を足して決定表の行を決める。P-READ に。自信: 高
- [minor] 5 作りの確かめ M の補正は 20,000 組でしか確かめていない（223・151 行・S13 notes 13 行）。約 100 組で 676 セルでは偏りが残る。解消: P-MI にパネルの組の数（約 100 組・1 次マルコフと独立）の確かめを足し、(i)・(ii) を M − M_shuf で判定。自信: 中
- [minor] 6 作りの確かめが外れたときの論文の文が 1 通りでない（151・191 行）。解消: そのときの結果の文・Discussion の文・223 行の置き換えを 1 通りに。自信: 高
- [minor] 7 区間が 0 をまたいでも主の語が付く（109・128 行）。解消: stay_G(30)・stay_R(30) の区間が 0 をまたぐとき「（区間が 0 をまたぐ）」を添える。自信: 中
- [minor] 8 型 1 の Discussion の書き直しが主の記号化（平滑あり）では確かめていないことを書かない（186 行・main.tex 136 行 "our results concern this overlapping, smoothed form"）。解消: 型 1・2・2′ の文に「平滑した主の記号化では確かめていない」。自信: 中
- [nit] 型 2 の名「構造に依らず」は ar3 の 1 つだけ（159 行）。解消: 「構造を ar3 に固定しても得が歩みに沿う」。自信: 高
- [nit] φ の分子と分母で書き手の集合が違いうる（87・122 行）。解消: A1・A30・C30 のすべてに値のある書き手で取る。自信: 中

## 4. 総合: minor（直してから凍結・major と minor の境）
- 書き方を結果の後に選ぶ余地はほぼ閉じた。carryover の 7 件はすべて解消。
- 残る 2 件の major（覆う時間の交絡・R_ar3 の縮みの床）は、言い方・添えの句・限界の文で閉じる。
- 指摘 1 の (ii)（列 D）を採るなら読みの規則が変わるので再査読。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: monaco.txt 1117-1728 行・pohle.txt の大半・singer.txt の大半・supplement.tex・S13 と tau-extend の conditions.md・kit README・S13 scripts（SHA-256 は照らしていない）・variants.py の thinned_mask 以外・main.tex の 132-139・219-226・325-342 行以外。
- 注入の疑い: 無し。
