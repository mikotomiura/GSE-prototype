# 査読 R3 round 2（評価の偏りと個人への推論の方法論・paper-reviewer / opus）

## 1. 接地
- G1 Varma & Simon 2006 "CV methods are proven to be unbiased only if all the various aspects of classifier training takes place inside the CV loop."
- G2 Varma & Simon 2006 "the CV error estimate for the classifier with the optimal parameters was found to be a substantially biased estimate of the true error"・"The parameter selection bias, on the other hand, is always negative."
- G3 Varma & Simon 2006 "This can be accomplished by a large validation set that is independent of data used for parameter tuning."
- G4 Liu & Meng 2016 "Otherwise, a statistical uncertainty assessment amounts to only an internal consistency check, i.e., it answers whether the conclusion is reasonable given the current data, not whether the conclusion generalizes."
- G5 Liu & Meng 2016 "if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust."
- G6 Liu & Meng 2016 "Our choice of model resolution, R, should be compatible with the “data resolution.”"

## 2. 評価表
- a 3: 言い方の限り（16–21 行）はよく効く。型 1 はほぼ G の語 1 つで決まる。D_s と ρ_h の語は既知の値からほぼ決まる（M1）。型 1 の文は平滑を外した記号の結果なのに平滑した主の記号化の段落を書き換える（M3）。
- b 2: 列 C と列 A の違いは歩みのほかにセッションの中のどこを覆うかにもあり、限界に書かれただけ（M2）。本人の当てはめが従属を運ぶかは副の量で仕組みの環が切れる（M1）。
- c 3: 記号の数をそろえた用量反応と境の歩みはどの結果でも持ち帰れる。
- d 3: 密度が高い。列 B が記述だけなのに条件・門・変異の多くを占める。
- e 4: 揃っている。乱数の「列の番号・歩みの番号」が未定義（m3）。
- f 3: 窓で作った特徴が従属を生むことの方法論の先行が挙がっていない（prereg なので重くは見ない）。
- g 4: 判定の順・決定表・添えの文・持ち込みの文・停止と逸脱の扱いが 1 通り。前の試験の「結果を見た後の当て方」（S13 notes 140–142 行）は構造の上で塞がれている。残る未定義は m1・m2。

## 3. carryover の判定
- major R の構造: 解消（135–140 行）
- major 開示: 一部解消。既知の r1 − 共有 hmm3（33 行）が未見とする D_s の向きをほぼ決める（M1 に含める）
- major D と G の恒等式: 恒等式は解消。共通の項が残り連動を生む（M1）
- major 重なりと打鍵の持続: 研究者の選択として言い方の限りと限界で閉じた。受け入れる（18・203 行）
- major 量の交絡: 一部解消。区間の位置という新しい交絡（M2）
- major 型の分岐: 解消
- minor 構造の選びの語・M の門: 解消。語の揺れ: 本文に入らない（m1）
- nit 本文の位置・大きく超える: 解消（依頼文の「307 行」は表の行で、主張は 331 行として査読した）

## 4. 指摘
- [major] M1 型 1 の 3 条件のうち 2 つは既知の値からほぼ決まり、「仕組みと合う形」は実質 G の語 1 つで付く
  - 位置: 129・33・35・91 行・S13 notes 81 行「hmm3 の本人（τ 他人）も同じ程度だった（o: 0.29〜0.63、u: 0.24〜0.63）」
  - 理由: 列 C はどの s でも歩み 1 で、ρ_h は作りの上でほぼ確実に大きい。D_s は既知の r1 − 共有 hmm3 と構造が同じで人だけが違い、向きはほぼ予見できる。G と D_s は「− 共有 hmm3」の項を共有し、共有 hmm3 の点だけが下がってもそろって上がる。仕組みの環を確かめる量（本人の当てはめが従属を運ぶか）は副の量で、S13 では本人 hmm3 の残差の自己相関が共有と同程度で不利な値が既に出ている（notes 136 行は確かめていないと書いた）。G2・G3。
  - 解消: (i) 開示と限界に「D_s の向きは既知の r1 − 共有 hmm3 からほぼ予見でき、ρ_h の向きは作りからほぼ決まる」。(ii) 型 1 の名と文を弱めるか、本人と共有の ρ_h の差（または本人 hmm3 − 共有 ar1）を主に上げて型 1 の条件に加える。(iii) 貢献 (1) の「仕組みと合う形を測った」を外すか「歩みとの並びを測った」に。
  - 自信: 高
- [major] M2 列 C 対 列 A で歩みとセッションの中の位置が交絡し、手当てが限界の文だけ
  - 位置: 50・51・204 行
  - 理由: 学習と評価の両方が「中ほどの連続した区間」か「全体に散った点」か。中ほどの均質な区間なら本人の得は従属と関係なく増減しうる。始まりを 1 か所に固定した設計は G5 の形。
  - 解消: 感度の列 C'（始まりを floor((L − n_A)/4) と floor(3(L − n_A)/4) の 2 版）を事前に固定し、主の量の語が列 C と違えば「割れる（区間の位置）」と添え、型は「なし」か文に限定。足さないなら型 3 と型 1 の文に「中ほどの区間で」と書く。
  - 自信: 中
- [major] M3 型の持ち込みの文が平滑を外した記号の結果を平滑した主の記号化の段落に書く
  - 位置: 155 行・main.tex 136 行 "Because consecutive windows share 29 of their 30 seconds and the values are smoothed, consecutive symbols are strongly dependent…our results concern this overlapping, smoothed form"・44 行
  - 理由: 列はすべて u。型 1〜4 の文に「平滑を外した記号で」が無く、主の記号化でも成り立つように読める。S13 では u と o の CS1 の G が割れた（notes 46 行）。
  - 解消: 言い方の限りと型 1〜4・型なしの文に「平滑を外した記号（S13 の u）で」を固定し、「主の記号化（平滑あり）へは広げない」と書く。
  - 自信: 高
- [minor] m1 語の揺れ（1 人抜き）が本文の文に入らない。s = 5・10・15 の Δ は符号だけで数え、大きさは s = 30 だけ。解消: 型を決めた G の語の 1 人抜きの一致の割合を型の文の直後に数で書く、または割合が一定以下なら「（1 人抜きで揺れる）」と添える。自信: 中
- [minor] m2 境の歩みが単調でないときの文が無い（146・160 行）。解消: 境より長い全部の歩みで 2 セルとも正のときだけ使い、そうでなければ歩みごとの符号を並べる。「<境> 秒以上の格子の歩みでは」と書く。自信: 高
- [minor] τ の選びが列ごとに違い、G の差の一部が縮みの選びの差になる（73 行）。解消: τ 固定の 1 行（例 τ = 10,000）を事前に決め、その行で G の「列 C と列 A」の語を副として出し、主と違えば「割れる（τ の選び）」と添える。自信: 中
- [minor] m3 新しい列・歩みでの乱数の番号が未定義（83・92・95 行・S13 conditions 65 行「列の番号（o 0・u 1・n 2）」）。P-REPRO-U・N には列 A の s = 1 は v の流れで u の番号 1、s = 30 は n の番号 2 が要る。解消: 13 組それぞれの番号と残差の v の番号の表を足す。自信: 高
- [nit] 「仕組みと合う形を測った」は言い方の限りの際にある（155・19 行）。M1 の (iii) と同じ。自信: 中

## 5. 総合: minor
- 前の round の major 6 件のうち 4 件は解消。残る 2 件は形を変えて M1・M2 に残る。決定表と持ち込みの文が全部の語を覆い、結果を見てから書き方を選ぶ余地は構造の上でほぼ塞がれた。
- 確かめられるのは「記号の数をそろえても得が歩みに沿うか」まで。D_s と ρ_h は既知の値と作りからほぼ決まり、331 行の仕組みを確かめたとは言えない（M1）。区間の位置（M2）と平滑の範囲（M3）も文に入れる。
- M1〜M3 は文の固定と小さな感度の列で閉じられる。解消の条件のとおりなら再査読なしで凍結してよい。

## 6. 読めなかった範囲と注入の疑い
- 読んでいない: supplement.tex・tau-extend conditions.md・kit README・SEED・S13 scripts。variants.py は thinned_mask だけ（最初の行が落ちることは確かめた）。Liu & Meng は要旨と一部だけ。SHA-256 は照らしていない。
- 注入の疑い: 無し。
