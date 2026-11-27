# 査読 R3 round 5（評価の偏りと個人への推論の方法論・paper-reviewer / opus）

総合の推奨は minor（直してから凍結）。round 4 の major（M-1）は解消。新しい fatal と major は無い。残るのは句の置き方の規則と用意した文の食い違い（round 4 minor-1 の残り）と、限界への書き足し 2 点。

## 1. 接地
- V1 Varma & Simon 2006 "CV methods are proven to be unbiased only if all the various aspects of classifier training takes place inside the CV loop."・"Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
- V2 "this involves a kind of additional training of the classifier (in the form of selecting the classifier parameter) that is done outside the CV loop. ... Thus the guarantee of unbiased estimation of true error is not valid and there is a possibility of bias."
- V3 "Since the bias is caused by the variability in the estimates of prediction error for different values of the tuning parameters it is a general phenomenon."・"The parameter selection bias, on the other hand, is always negative."
- L1 Liu & Meng "Both examples above teach us that the precision of control data should match that of our actual data. This seemingly obvious principle is violated surprisingly often in practice"
- L2 "When we perform selection, we are targeting not only markers with large effects, but also markers for which the current dataset is “lucky”."・"without this matching step, our inference ignores selection bias."
- L3 "Otherwise, a statistical uncertainty assessment amounts to only an internal consistency check, i.e., it answers whether the conclusion is reasonable given the current data, not whether the conclusion generalizes."
- L4 "Since few individuals match Mr. Payne’s background completely, it is harder to estimate µ~x than µ. This increase in estimation error can wipe out benefits from matching."

## 2. 引き継ぎの判定
- major M-1: 解消（13・120・174・259 行・型の表 163–169 行に R_ar3 が無い）
- minor-1: 一部だけ解消（19 行の規則に対して用意した文の多くに句 (2) が無い）
- minor-2・nit-1・nit-2: 解消（32・262・176・33・128・173–182 行）

## 3. 評価表
- a 4: どの型でも 331 行の仕組みの文を肯定しない（202–206 行）。型 1 の名も限った（29 行）。境の文の「勝った」は全員と読まれうる（minor-3）。
- b 3: 3 つの要素の交絡と学習・評価の未分離は限界にある。「同じ記号の数」が「同じ量の情報」でないことは列 B だけに書き、主の比べの列 C に無い（minor-2）。
- c 3: どの結果でも仕組みの文を支えられない。正直に書いてあるが「深さ」への答えとしては弱い。
- d 3: 277 行に規則・例外・添えの句が重なり、19 行と 188・203–212 行の食い違いに気づきにくい。
- e 4: SHA-256・端の門・変異・乱数の番号がそろう。SEED 2026110401 は SEED ファイルと一致、thinned_mask の記述（66–67 行）は variants.py 69–77 行と一致。
- f 3: Pohle との区別・Uto2020 へ広げない禁止は良い。記号の数をそろえた比べが情報をそろえない点の文献や言い方は無い。
- g 4: 残る自由は句 (2) の規則と文の食い違い（minor-1）と開示に k = 1 の値が無いこと（nit-1）。

## 4. 指摘
- [minor] 句 (2) を「差し込む文そのものに入れる」規則と用意した文が食い違う（19 行・188 行の境の文・203–204 行の型 2・3 の Discussion の文・208 行 "which persisted at an equal number of symbols in unsmoothed symbols (Section X)"・212 行 "found the gap to persist at an equal number of symbols"）。規則と文のどちらに従うかを結果の後に選べる。句 (2) が無いと 208・212 行は「重なりの効き」と読まれうる（23 行が禁じる読み）。解消: (a) 各文に句 (2) の英訳の短い形を書き込む、または (b) 19 行を「句 (2) は歩みの差を原因として述べる文にだけ入れる」に改め対象の文を名指し。自信: 高
- [minor] 列 C は記号の数をそろえるが実効の情報はそろえない。主の比べの限界に無い（264・23・157 行）。同じ N でも列 C の連続した行は強く従属し、本人の当てはめが得る情報は列 A と違う。G への効きの向きは決まらない。L1。解消: 限界に「列 C と列 A は記号の数をそろえるが、従属の強さが違うので実効の情報はそろわない。これが G に効く向きは決まらず、この試験は分けない」を足し、句 (2) に「実効の情報」を加えるか限界の文を指す。自信: 中
- [minor] 境の文の「勝った」は全員と読まれうる（188・186 行・main.tex 53 行 "loses to it for every writer"）。s = 30 で正、s = 1 で負が既知で s* を決めるのは 5・10・15 だけ（L2）。解消: 「中央値で」を入れ、境の端 2 つが既知であることを限界か句に。自信: 中
- [nit] 開示の表に既に見た k = 1 の値が無い（40 行・S13 notes 58 行「k = 1（値だけ）: G は o 0.0125・u 0.0874・n 0.0008（CoAuthor）」）。解消: k = 1 の G・C2a を見ていたことを開示に 1 行。自信: 中
- [nit] φ の分母に下限が無い（140・261 行）。解消: (a) 下限（例 shrink_G(30) < 0.01 なら「列 A で縮まない」に含める）を決めるか、(b) 置かないことを判断として明記。自信: 低

## 5. 特に見てほしいことへの答え
1. 331 行を支えられる結果は無い。型 1 なら「歩みの束が記号の数をそろえても効く」に限った言い換え、型 2・3 なら「推測したが支えなかった」への格下げ。置き換えの文がこの範囲を越えないことを確かめた（202–206 行）。
2. ほぼ閉じている。残るのは minor-1 と φ の分母の下限。
3. 区切りが端を見てから置かれたこと・φ の定義が round 2 の後に置かれたことは開示されている（38–57・266 行）。この試験は既知の端に条件づけた内部の確かめと自らを限り（34・263 行）、妥当。開示に k = 1 の値を足せば十分。

## 6. 総合: minor（直してから凍結）
- round 4 の major は R_ar3 を記述へ移し重みを本文の句に添えて解消。
- 判定の順・決定表・置き換えの文・停止の規則は 1 通り。残る自由は句 (2) の食い違いだけ。
- 限界に足す 2 点（実効の情報・境の文の粒度）は 1 文ずつで閉じる。

## 7. 読めなかった範囲と注入の疑い
- 読んでいない: liumeng.txt 929–1908 行・supplement.tex・S13 と tau-extend の conditions.md・kit README・S13 scripts（SHA-256 は確かめていない）・main.tex は 53・74・165・340 行と 223・331 行の一部だけ。
- 読んだ: conditions.md 全文・carryover-R3.md・context-A.md・S13 notes.md 全文・SEED・thinned_mask・varma.txt 全文・liumeng.txt 1–928 行。
- 注入の疑い: 無し。
