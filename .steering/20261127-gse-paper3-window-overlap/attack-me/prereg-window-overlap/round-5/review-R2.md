# 査読 R2 round 5（個人化した行動のモデルの実務・paper-reviewer / opus）

## 1. 接地
- S1 Saeb 2017 "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
- S2 Saeb 2017 "if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time"
- S3 Saeb 2017 "very often, these are chosen such that the prediction error is minimized over the whole dataset. This makes the algorithms overfit the available datasets"
- S4 Aalbers 2023 "we compare against the MAEs of a "naive" but person-specific baseline model"・"based on the person-specific average level of stress in the participant's train data (ie, first 80%) rather than all their data to prevent data leakage"
- S5 Aalbers 2023 "The relations of these digital markers with momentary subjective stress differed from person to person, as did model accuracy."
- S6 Aalbers 2023 "a confirmatory approach would be to test a small number of (preregistered) hypotheses that make explicit what relation we expect"

## 2. carryover の判定
- M1: 解消（13・120・174・55 行）
- m1: 一部が残る（203〜204・208・212・188 行に句 (2) が無い・下の m-1）
- m2・m3・n1・n2: 解消（202〜206・27・188・175・3 行）

## 3. 評価表
- a 3: 両端に条件づけた分析と明言（34 行）。208 行の英文の句が型の判定の量とずれる（M-1）。
- b 3: 列 C は記号の数が同じでも独立な情報が列 A より少ない。この代わりの説明が型 2・3 に無い（m-2）。
- c 3: 実務家が持ち帰れるのは境 s* だけで、本人の連鎖そのものが弱くなることと区別されていない（m-3）。
- d 3: 差し込みの規則（19 行）と実際の文（202〜212 行）の食い違いを書いた本人も見落としている。
- e 4: SEED は 2026110401 で一致、thinned_mask の定義も一致。
- f 3: Pohle との違いは書かれ、列 C は使う場面の推定でないと限る（27 行）ので S1 に外れない。
- g 4: 結果を見てから書き方を選ぶ余地はほぼ無い。残るのは 208 行の句の指す先だけ。

## 4. 指摘
- [major] M-1 208 行の英文の句が型を決める量と違うものを指し、型 1 では逆の意味に読める
  - 位置: 208 行・main.tex 223 行 "with non-overlapping windows, … the \hmmthree{} beats the own chain in CoAuthor and its per-person fit beats the shared \hmmthree{} at $k=5$ and 15, which may also reflect the smaller amount of data"
  - 理由: "which" が受けるのは重ならない窓で見えた形（C2a > 0 と G > 0）。型は φ(30) だけで決まり、列 C の C2a は 188 行で別に述べる。(i) 型 1 の "which persisted" は「重ならない窓の形が記号の数をそろえても続いた」と読め、型 1 の中身と逆。(ii) 型 2・3 の "also appeared" は列 C の C2a が正でなくても「本人の連鎖に勝つ形も現れた」と読め、188 行と矛盾しうる。「英訳の確定はこの意味で行う」に書き方を選ぶ余地が残る。
  - 解消: 英文の句の主語を量で明示（例 型 1 "the shrinkage of the per-person gain over the shared HMM was smaller at an equal number of symbols from a contiguous stretch at the 1-second step"）。C2a の向きは 188 行の分類の文を写して別の句に。型ごとの英文を条件の中で確定し「英訳の確定はこの意味で行う」を削る。P-READ に型 1 と列 C の C2a「両方正でない」の組を足す。
  - 自信: 高
- [minor] m-1 差し込みの文の一部に句 (2) が無く 19 行の規則と食い違う（203・212・208・188 行）。貢献の句 "persist at an equal number of symbols" は「窓の作りが原因」と読まれやすい。解消: 4 つの差し込みに句 (2) の英訳（例 "with the step, overlap, horizon and covered time not separated"）と "from a contiguous stretch at the 1-second step" を入れるか、19 行を「列 A と列 C の比べを述べる差し込みに限る」に改めその範囲の文に全部入れる。自信: 高
- [minor] m-2 型 2・3 の代わりの説明（列 C の独立な情報の少なさ）が無い（23・203・204・264 行）。列 C30 は 29/30 重なる記号を約 100 個連続で採り、独立に近い観測ははるかに少ない。仕組みが正しくても学べないと τ が大きく選ばれ G が小さくなりうる。型 2・3 は「記号の数だけが効く」と「仕組みはあるが列 C では学べない」を分けない（S1）。解消: 限界に「列 C は…独立に近い観測は列 A より少ない。型 2・3 は本人の当てはめが学べないことでも出うる」、列 C30 の hmm3 の重みが列 A30 より小さければ型 2・3 の文の補足に句を添えると決める。自信: 中
- [minor] m-3 境 s* が本人の連鎖そのものが弱くなることと区別されていない（188・48 行）。歩み 30 では本人の連鎖が共有 hmm3 にさえ負ける。解消: 境の文の後に同じ歩みでの r1 − 共有 hmm3 の 2 セルの符号を 1 句で添え（「その歩みでは本人の連鎖が共有 hmm3 にも負けた／負けなかった」）、分類の規則を 186 行と同じ形で決める。自信: 中
- [nit] n-1 人ごとのばらつきの報告が中央値に偏る（102・127〜128 行・S5）。解消: セルごとに「G_C30 > G_A30 の書き手の数 / m」と shrink_G(30) > 0 の人数を記述の量に。自信: 中
- [nit] n-2 切れ端が s = 1 にしか掛からないという主張を確かめる手段が無い（265 行）。解消: 列ごとに切れ端が掛かった系列の数を出し、0 でなければ限界の文を直す。自信: 低

## 特に見てほしいこと
- (1) 型 1 で言えるのは「平滑を外した u で、記号の数だけでは G の縮みを説明しきれない」まで。Discussion の主張は「記号の数という代わりの説明を 1 つ試した」に縮む。型ごとの文はこの範囲に収まる（M-1 と m-1 を除く）。
- (2) 残る余地は 208 行の英訳を結果の後に「意味で確定」する所だけ（M-1）。
- (3) 未知なのは実質 G_C30 と中間の歩みだけ。開示の数値は notes 46〜51・72〜73・81・88 と一致。ジョイントの残りの 5.8e-4 / 8.0e-4 は読んだ範囲の notes には見当たらなかった（確かめていない）。

## 5. 総合: minor（直してから凍結）
- 量・語・型・停止の規則は 1 通りで、round 4 の major は解消。
- 残る major は 208 行の英文の句の指す先のずれだけで、文を量で書き直せば消える。設計を変える必要は無い。
- m-1〜m-3 は句と限界の文と分類の規則で閉じる。再査読は不要と考える。

## 6. 読めなかった範囲と注入の疑い
- 読んでいない: supplement.tex・kit README・S13 と tau-extend の conditions.md・S13 scripts（SHA-256 は照合していない）・notes.md の 40〜89 行と grep の行以外・main.tex の 325〜342・52・223 行以外・variants.py の thinned_mask 以外。
- 注入の疑い: なし。
