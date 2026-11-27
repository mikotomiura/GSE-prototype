# 査読 R3 round 4（評価の偏りと個人への推論の方法論・paper-reviewer / opus）

## 1. 接地
- B1 Varma & Simon 2006 "Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
- B2 "The parameter selection bias, on the other hand, is always negative."・"The total bias ( i.e . the sum of inherent bias and parameter selection bias) is what must be kept in mind when interpreting error estimates."
- B3 "It must be noted that reducing the set of parameters over which one optimizes, as we have done here, may potentially reduce the amount of bias obtained."
- B4 Liu & Meng（758–760）"Both examples above teach us that the precision of control data should match that of our actual data. This seemingly obvious principle is violated surprisingly often in practice"・（743）"since problems with very different sample sizes are not comparable, we want our controls to have a matching sample size of n."
- B5 Liu & Meng（829–830）"we should restrict attention to controls where the same markers are selected as in our actual study; without this matching step, our inference ignores selection bias."
- B6 Liu & Meng（102–103）"our inferences can be hurt either by too much matching (not robust) or too little matching (not relevant)."

## 2. carryover の判定
- M-A（R_ar3 の床）: 一部だけ解消（166・113・46 行は入ったが、s = 30 の列で τ = 10,000 の重みが床に近いことが読みに入っていない・新 M-1）
- M-B・M-C・m-1・m-3: 解消。m-2: 本文では解消（論文に入れる句の側の残りは nit-1）。nit: そのままでよい。

## 3. 評価表
- a 4: 残りは M-1 だけ。
- b 3: R_ar3 の比べに入るデータの重みが G とそろわない点が限界の文（255 行）で止まる（M-1）。
- c 4: 列 C で S13 の未決に答えられ、型 3 も文まで決めてある。
- d 3: 添えの句が最大 7 つ付くと文が読めなくなる。本文と補足の振り分けが無い（nit-2）。
- e 4: Mac と HP Z2 は BLAS が違い回し直しの見込みは高いが扱いは決めてある。
- f 3: 記号の数（精度）をそろえて比べる考えに方法論の出典が無い（B4・必須ではない）。
- g 4: 決まっていないのは Discussion の第 1 段落での句の置き方（minor-1）と M-1 の重みの条件。

## 4. 指摘
- [major] M-1 型 1 の「τ = 10,000 でも小さい」は、s = 30 の列では本人のデータの重みが床に近い所で判定され、G の比べと重みがそろっていない
  - 位置: 98・166・255・113 行
  - 理由: S13 notes 13 行で n の評価の記号の中央値は 107。学習が k = 5 で数百記号なら N/(N + 10,000) は 0.05 ほど、k = 15 でも 0.1 台。本人 ar3 は共有 ar3 からほとんど動けず |stay_R(30)| < stay_G(30)/4 はほぼ決まる。G は他人で選んだ τ の hmm3 で重みが違う。格子に 0・100・1,000 があるのに τ = 10,000 を選んだ理由が無い（B3）。B4 の精度をそろえるにも外れる。開示（46 行）で R_ar3(A1) が小さいと分かったうえで閾値を置いた。型 1 は「列 C で縮みが小さい」が出ればほぼ自動。
  - 解消（どれか 1 つ）: (i) 型 1 に R_ar3^fix の行の C30・A30 の本人 ar3 の重みの中央値が G の hmm3 の同じ列の重みの中央値以上を要し、満たさなければ「重みが小さく決まらない」で型 2′、(ii) 固定の行を s = 30 の列で重みが 0.5 前後になる τ（0・100・1,000 のどれかを記号の数の公式から前に決める）に替えるか足す、(iii) τ = 10,000 のままなら型 1 の名と文に「本人 ar3 の重み <値> のもとで」を添え、Discussion の語を「仕組みと矛盾しない形」に下げる。重みの表の値を読みのどこで使うかを 1 文で。
  - 自信: 中
- [minor] minor-1 Discussion の第 1 段落での句の置き方が 1 通りでない（17・197 行・main.tex 331 行の第 1 文）。型 1 の置き換える文（198 行）に「平滑を外した記号（S13 の u）で」が付いていない。解消: Discussion の第 1 段落だけ例外とし句 (1)(2) を置き換える文の中に入れる。雛形にも句を入れた形で。自信: 高
- [minor] minor-2 2 セルの一致を頑健さとして読ませない（140 行）。k = 5 と 15 は同じ 17 人で学習も重なる（B6）。解消: 限界に「2 セルは同じ書き手と重なるデータで独立の再現ではない」、結果の文で「両セルで」を再現の意味に使わない。自信: 中
- [nit] nit-1 1 人抜きの句に選びを繰り返していないことが乗らない（180・116 行・B1・B5）。解消: 「（1 人抜きで中央値だけを取り直して同じ語 …）」。自信: 高
- [nit] nit-2 添えの句が最大 7 つ付いたときの本文と補足の分け方（173–181・208 行）。解消: 本文に置く句と補足に置く句を名指しで分ける。自信: 中

## 5. 特に見てほしいことへの答え
- (1) 型 3 なら 331 行の仕組みの文は推測に下がり、S13 の縮みは記号の数の側に寄る（明確に言える）。型 1 で言えるのは、記号の数をそろえても歩み 1 の連続した区間で差が残りそれが弱い構造の比べに偏る、まで。用量の形には語を付けない。M − M_shuf はほぼ必ず通る。型 1 の後半の分ける力は M-1 で弱い。
- (2) 残るのは minor-1 と nit-2。
- (3) 偏りの残りは R の側（R_ar3(A1) が小さいと知ったうえで R の閾値と τ = 10,000 の行を置いた）。G の側の列 C は未見で偏りは小さい。

## 6. 総合: major（再査読は M-1 の 1 つの規則と minor-1 の雛形に限ってよい）
- round 3 の major 3 件のうち 2 件は解消し、固定と再現の作法は凍結してよい水準。
- 型 1 と型 2 を分ける判定が、s = 30 の列で本人のデータの重みが床に近い固定の行に頼っている。重みの条件を実データの前に 1 つの規則として書けば閉じる。

## 7. 読めなかった範囲と注入の疑い
- 読んでいない: S13 conditions.md・SEED・variants.py・README・S13 scripts・supplement.tex・liumeng.txt 929 行以降・notes.md 81 行以降の大半・tau-extend の conditions.md の大半・main.tex の 325–344 行以外。N は評価の記号の数からの推定。
- 注入の疑い: なし。
