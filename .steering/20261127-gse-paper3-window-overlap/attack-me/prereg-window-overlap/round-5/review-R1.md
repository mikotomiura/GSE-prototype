# 査読 R1 round 5（行動の記号列の系列モデルの方法論・paper-reviewer / opus）

前の round の指摘 8 件のうち 7 件は解消し、1 件（minor 4）は一部だけ解消。新しい穴は major 1・minor 5・nit 1。どれも文の直しで閉じられるので推奨は minor（直してから凍結）。

## 1. 接地
- S1 Monaco & Tappert 2018 "consistency of the POHMM implementation under several different scenarios is validated in this section using computational methods"・"scenario 4 simply demonstrates the inability of the HMM to capture the dependence on event types, and results should indicate biased estimates"
- S2 Singer 2014（境目に RESET 状態）"to forget the history between different paths"
- S3 Singer 2014 "choosing the model with the highest likelihood is biased towards models with more parameters"・"It is difficult to make plausible statements about the appropriate Markov chain order having insufficient data but a vast amount of states"
- S4 Singer 2014 "One disadvantage of cross validation methods usually is that the results are dependent on how one splits the data"
- S5 Pohle 2017 "additional states may be able to capture this ignored data structure"・"the residuals obtained for the two-state model exhibit much stronger autocorrelation ... This could be an indication of a violation of the dependence assumptions"
- S6 Pohle 2017 "a large difference in AIC, BIC, ICL or any other information criterion alone does not prove that the model with the higher (or lower) number of states is most suitable ... What exactly these problems may be then needs to be investigated further"

## 2. 評価表
- a 3: φ の目安「記号の数だけが効けば φ ≈ 0」は記号の数＝データの量という前提に乗る（指摘 1）。223 行の which 節の置き換えは G の型だけで選ぶのに節は C2a も含む（指摘 3）。
- b 3: 列 C で「記号の数はそろうが独立な情報はそろわない」穴が限界に無い（列 B にだけ・指摘 1）。系列の頭の扱いが列 A と C で非対称（指摘 2）。
- c 3: 主張への寄与は限定的だが正直に書かれている。
- d 2: 差分の参照が多層で D5 が密。句の置き方の規則と型の文が食い違う（指摘 4）。
- e 4: そろう。M は系列の中の組だけで m65・m77 もある（S2）。
- f 3: 自己相関のある列での有効なデータの量という論点に触れていない。
- g 4: 残る余地は英訳を結果の後に確定できること（指摘 5）と境の文の「勝った」（指摘 6）。

## 3. 前の round の指摘の判定
- major 1・2・3: 解消（13・120・174・259・166・203・204 行）
- minor 4: 一部だけ解消（型 2・3・なしの文に句 (2) が無い・指摘 4）
- minor 5・6・nit 2 件: 解消（102・176 行）

## 4. 指摘
- [major] 1 列 C では「同じ記号の数」が「同じデータの量」にならないのに、φ の目安と型 2・3 の文が記号の数をデータの量として読む
  - 位置: 142 行「歩み（言い方の限りの (2) の 3 つ）だけが効けば φ ≈ 1、記号の数だけが効けば φ ≈ 0 になる」・264 行（列 B にだけ情報がそろわないと書く）・157 行（作りの確かめ (ii)）
  - 理由: 列 C は歩み 1 の連続した区間で続く記号はほぼ写し。CoAuthor の 1 セッションは約 670 行（notes の 588,227 行 ÷ 875 単位）で、歩み 30 で n_A は約 22、列 C30 の区間は約 22 秒で 1 つの窓（30 秒）より短く、実質 1 窓ぶんの情報しか持たない。作りの確かめ (ii) が通ることはこの不足を認めることでもあるのに交絡として読んでいない。φ ≈ 0（型 2）は「列 C の方が実効のデータが少なく本人の当てはめが育たない」でも出る。Singer。
  - 解消: (a) 142 行の目安を「データの量（記号の数。ただし列 C は続く記号の従属が強く独立な情報はそろわない）だけが効けば φ ≈ 0」に (b) 264 行と同じ趣旨の限界を列 C にも書き、区間の秒の長さが 30 秒を下回る歩みがあればその旨を本文の型の文に添える規則を D5 に (c) 型 2・3 の結果の文に「（記号の数はそろえたが、続く記号の従属が強いので独立な情報はそろわない）」。設計を変える必要はない。
  - 自信: 中〜高
- [minor] 2 系列の頭の扱いが列 A と列 C で違い、歩み 30 で G をずらしうる。頭を外す採点が補足にしか効かない（66・68・181 行）。歩み 30 では頭が評価の記号の約 5%。列 A30 の頭はセッションの始まりから 30 秒の書き手どうしで似やすい記号、列 C30 の頭は中ほどの記号（S4・S2）。解消: (a) 頭を外した採点で G の語が違えば本文の添えの句に「（系列の頭を除くと語が <語>）」、または (b) 型 1 を全記号と頭を外した採点の両方で「列 C では縮みが小さい」のときに限る。自信: 中
- [minor] 3 223 行の which 節の置き換えを G の型だけで選ぶが節は C2a も含む（208 行・main.tex 223 行 "the \hmmthree{} beats the own chain in CoAuthor and its per-person fit beats the shared \hmmthree{} at $k=5$ and 15, which may also reflect the smaller amount of data"）。解消: G の型と列 C30 の C2a の分類の組で決める表にするか、which 節を 2 つに割り G の部分だけを型で置き換える。自信: 高
- [minor] 4 句 (2) の置き方の規則が型 2・3・なしの文（203・204・205 行）と 208・212 行の英訳の句で守られていない（19 行）。解消: 句 (2) を入れるか、入れない場合を規則に明記。自信: 高
- [minor] 5 本文に入る文の英訳が結果の前に確定していない（208 行「（英訳の確定はこの意味で行う）」・202〜205 行は日本語だけ）。語の強さを結果を見てから選ぶ余地。解消: 型ごとの英文を凍結の版に逐語で。自信: 高
- [minor] 6 境の文の「勝った」は中央値の符号なのに本文の対の文は "for every writer"（188 行・main.tex 221 行 "loses to the own chain ... for every writer at every $k$"）。解消: 「（中央値で）」と入れ、良い側の割合を添える。自信: 中
- [minor] 7 読みの規則が仕組みの分かっている合成のデータで確かめられていない（267・246 行・Monaco の 4 つの場合）。解消: 限界の文は今のままでよく、型の文の直後に「読みの規則は合成のデータで確かめていない」を 1 句入れるか既にそうなっていることを示す。自信: 中
- [nit] 8 型 1 の「4 つの s のうち 3 つ以上で stay_G(s) > 0」は中間の歩みを判定に使う（147・30 行）。符号の条件で勾配ではないが、30 行の例外に「型 1 の符号の条件」を書く。自信: 高

## 5. 特に見てほしいこと
1. 型 1 でも言えるのは、平滑を外した記号の上で歩み（3 つを分けない）が G に効くことまで。仕組みの前半も後半も確かめない。本人の当てはめの環は既知の値から支えられず、添えの句で正しく扱われている。操作の確かめは作りが効いたことと情報の不足を同時に示す。
2. 指摘 3・4・5 に残る。文の固定で閉じる。
3. 未見の値は実質 G_C30 だけ。開示は透明。型 1 にだけ追加の符号の条件があるのは型 1 を出しにくくする保守的な向き。

## 6. 総合: minor（直してから凍結）
- 設計は 1 通りに固定。新しい major（列 C で情報がそろわない）は φ の目安・限界・型 2・3 の文の直しで閉じる。
- minor は文の固定。メインが直しを目で確かめれば凍結してよい。指摘 2 で (b) を選ぶときは決定表の 1 行だけ確かめ直す。

## 7. 読めなかった範囲・注入の疑い
- 読んでいない: monaco.txt 1117〜1728 行・singer.txt 705〜1198 行・pohle.txt の大半・main.tex の 134〜136・221〜223・325〜344 行以外・supplement.tex・SEED・kit README・S13 scripts・tau-extend conditions.md。SHA-256 は確かめていない。
- 注入の疑い: 無し。
