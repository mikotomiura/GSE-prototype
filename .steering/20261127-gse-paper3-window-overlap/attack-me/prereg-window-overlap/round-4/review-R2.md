# 査読 R2 round 4（個人化した行動モデルの実務家・paper-reviewer / opus・対象 a2d3413c 第 4 版）

## 1. 接地
- B1 Saeb 2017 "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
- B2 Saeb 2017 "if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time"
- B3 Saeb 2017 "Subject identification, which we know to be relatively easy, thus replaces disease recognition, which we know to be hard."
- B4 Aalbers 2023 "for 89.3% (200/224) of participants, the person-specific baseline outperformed all nomothetic models"
- B5 Aalbers 2023 "this comes at the cost of strongly reduced sample size, which limits model complexity and may lead to overfitting."
- B6 Aalbers 2023 "a confirmatory approach would be to test a small number of (preregistered) hypotheses that make explicit what relation we expect"

## 2. carryover の判定
- M1・M2・m1・m2・m3・n1・n2: 解消（128-134・20・114・25・175・24・196・186 行）。m2 に関わる新しい点は n1。

## 3. 評価表
- a 3: 型 1 の名と貢献 (1) の句は R_ar3 の比べに識別の力がある前提で成り立つが、開示の値からほぼ無いと見込める（M1）。他の言い方の限り（17-27 行）は厳しい。
- b 3: R_ar3 の床は 255 行に限界として書くが読みの規則に入っていない（M1）。
- c 3: 持ち帰れるのは境の歩み s* と「記号の数をそろえると縮むか」の 1 語。列 C の得が使う場面の量でないことが書かれていない（m3）。
- d 3: 271 行。句の置き方の規則が Discussion にどう当たるかが読めない（m1）。
- e 4: そろっている。
- f 3: 予測の先の長さを変える性質を窓の重なりの扱いの文献と結びつけていない（許容）。
- g 4: 開いているのは重みの表を読みに使わないこと（M1）と置き換えの文の <値> と句の置き場（m1・n1）。

## 4. 指摘
- [major] M1 R_ar3 の比べは列 C30・A30 の記号の数では床に張りつき、型 1 と型 2 の分かれがほぼ先に決まっている
  - 位置: 46・148・166・255 行・S13 notes 13 行
  - 理由: 両方の列が s = 30 と同じ記号の数（学習で 1 セッション約 100 記号・k = 5 で約 500・k = 15 で約 1,600）。ar3 は 2,033 の母数で、τ = 10,000 でも本人の重みは約 5%（k = 5）〜14%（k = 15）。他人で選んだ τ では A1 の全データでも R_ar3 は 1e-3 程度。境 stay_G(30)/4 は k = 5 で約 0.012、k = 15 で約 0.0075 以上。仕組みと関係なく越えにくく、G が「列 C では縮みが小さい」なら型 1 はほぼ自動で、型 2 は実際には出ない。差を生むのは母数の数（83 と 2,033）と記号の数（B5）。B6 の意味で反証されうる予測でない。
  - 解消: 実データの前に、(a) 合成で列 C30 と同じ記号の数・τ の選び方のもと本人 ar3 に stay_G(30) 程度の差を置いたとき R_ar3 の語が「同じ程度以上」になるかの検出の力の対照を V2 に足し、通らなければ R_ar3 の語は「床で読めない」として型 2′ へ、(b) ar3 の選ばれた τ でのデータの重みの中央値に下限を置き、下回れば「小さい」を「重みで読めない」に、(c) 型 1 の名と文から「仕組みと合う形」を外し「構造を ar3 に固定した比べでは差が出なかった（この記号の数では本人 ar3 の重みが <値> で、差を出せる大きさかは確かめていない）」に限る、のどれか。どれでも開示に「R_ar3 が s = 30 の記号の数で床に張りつくことは既知の値から見込めた」と 1 項。
  - 自信: 高（数は notes 13 行の中央値からの粗い計算）
- [minor] m1 句の置き方の規則が Discussion の第 1 段落にどう当たるかが決まっていない（17・197 行・main.tex 331 行の第 1 文は 30 倍の結果）。書き手が句の場所を選べる。解消: Discussion の第 1 段落では置き換えた文の頭に入れると明記し、型ごとの文の原文に句を最初から書き込む。自信: 中
- [minor] m2 残す "We have not checked this in other domains." の "this" が指すものを失う（197・198 行）。解消: 型ごとに残す文を固定（例 "Whether this holds for other overlapping-window features is not checked."）するか、元の一般化の文を推測の形で残すかを型ごとに決める。自信: 中
- [minor] m3 列 C の得は使う場面の量ではない（59・187 行・B1）。解消: 言い方の限りに「列 C は仕組みを分けるための作りで、使う場面の推定ではない。勧め (1) の境は列 A だけで述べ、列 C の句は『記号の数をそろえた比べでは』と限る」。自信: 中
- [nit] n1 型 1・2・2′ の句の <値> がどれを指すかが無い（175 行）。解消: 「列 A1 の x・y の差の中央値（k = 5・15）」のように指定し、列 C30 の差も並べ、符号が反対なら「列 C30 では <値>」と添える。自信: 中
- [nit] n2 表題の「用量反応」に対して用量の読みが無い（1・24 行）。解消: 表題か問いに「用量の形は図で記述するだけ」。自信: 低

## 特に見てほしいことへの答え
- (1) 言えるのは「記号の数をそろえても歩み 1 の区間で得が残るか」の 1 点。331 行の "features computed over overlapping windows make consecutive inputs dependent" はどの型でも支えにも反証にもならず、設計は正しく禁じている（20 行）。後半は R_ar3 が担うが M1 のとおり識別の力をほぼ持たない。M − M_shuf は型を支えないと正しく書かれている。
- (2) ほぼ閉じている。残るのは m1 と n1。
- (3) 開示は丁寧。R_ar3 が s = 30 で床に張りつくことも見込めたのに型を決める量に置いた点が最も大きい偏り（M1）。

## 5. 総合: major（再査読は M1 の 1 件に絞ってよい）
- carryover の 7 件はすべて解消し、固定と記録の作法は凍結できる水準。
- R_ar3 の比べは記号の数と ar3 の母数のせいでほぼ先に「小さい」になり、「仕組みと合う形」と貢献の句が反証できない形で出る。
- 直し方（検出の力の対照・重みの下限・名の限定）は設計の選択なので、選んだ形を一度見てから凍結を勧める。

## 6. 読めなかった範囲・注入の疑い
- 読んでいない: SEED・S13 と tau-extend の conditions.md・variants.py・kit README・S13 scripts・supplement.tex。main.tex は 130-141・220-224・329-340 行と grep の行。notes.md は 13 行だけ。SHA-256 は照らしていない。接地の 2 本は全文を読んだ。
- 注入の疑い: なし。
