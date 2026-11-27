# 査読 R2 round 2（個人化した行動のモデルの実務・paper-reviewer / opus）

## 1. 接地
- S1 Saeb 2017 "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
- S2 Saeb 2017 "For CV to be valid, training and test sets need to be independent [ 30 ]. The definition of independence, however, depends on the use-case scenario."
- S3 Saeb 2017 "Subject identification, which we know to be relatively easy, thus replaces disease recognition, which we know to be hard."
- S4 Saeb 2017 "The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets"
- S5 Aalbers 2023 "we compare against the MAEs of a "naive" but person-specific baseline model"・"based on the person-specific average level of stress in the participant's train data (ie, first 80%) rather than all their data to prevent data leakage from train to test data."
- S6 Aalbers 2023 "a confirmatory approach would be to test a small number of (preregistered) hypotheses that make explicit what relation we expect"

## 2. carryover の判定
| round 1 | 判定 | 根拠 |
|---|---|---|
| major 1 開示の誤り | 一部だけ解消 | 表は直った（27–35 行）。既に見た値の一部が表に無い（M3） |
| major 2 R | 解消 | R_ar3 を主に（82 行）。ただし型に入っていない（M1） |
| major 3 量の交絡 | 解消 | 列 C と列 A 対 列 C（50・104 行）。覆う範囲の違いは限界（204 行） |
| major 4 D | 解消 | D_s（81 行） |
| major 5 割れ・欠け | 解消 | 判定の順（106–111 行）と決定表（127–133 行）。型 3 の文に新しい穴（M4） |
| minor 6 重なりの語 | 解消 | 18 行 |
| minor 7 M | 解消 | 121 行 |
| minor 8 機械をまたぐ門 | 解消 | 166 行 |
| minor 9 語の揺れ | 解消 | 96 行。値を文に返す規則は無い（m2） |
| nit 10 本文の位置 | 解消 | 6 行の逐語は main.tex 331 行と一致。依頼文の「307 行」は依頼文の側の取り違え |
| nit 11 列 B の Q(1) | 解消 | 38 行 |
| nit 12 P-MI | 解消 | 188 行 |
| 評価表 c | 形は入った。中身に交絡 | M2 |

## 3. 評価表
- a 3: 型 3 の文は型の条件が確かめていないことを言い切る（M4）。境の歩みの文は記号の数で決まりうる入れ替わりを歩みの効きとして書く（M2）。
- b 3: 列 C でおおむね手当て。D_s と ρ_h は列 C 対 列 A でほぼ構造上「短い側で大きい」。型 1 と型 2 の区別は実質 G だけで決まり、仕組みに固有の予測（R_ar3 が平ら）が型に無い（M1）。
- c 3: 実務家の出力は境の歩みの 1 句だけで、使う場面に近い列 A の値なのに歩みそのものの効きとして読める（M2）。
- d 3: D5 に詰まり主と記述の境が読みにくい。
- e 4: SHA-256・端の門・変異・凍結の後の扱い。停止の規則の既定が無い（m3）。
- f 3: 窓の重なりが評価を甘くする行動センシングの文脈（S2・S3）に置いていない。
- g 4: 大きく進んだ。残る自由度は m1・m2・m3。

## 4. 指摘
- [major] M1 型 1 と型 2 を分ける量が比べの作りからほぼ決まり、仕組みを他の説明と区別しない
  - 位置: 125 行「G の語で枠を決め、D_s・ρ_h の語で型を決める。R_ar3 の語は型の文に添える。」・104 行・39 行
  - 理由: ρ_h は遅れ 1 なので列 C では 1 秒先・列 A では s 秒先。既知の値（歩み 1 で 0.315 / 0.525、歩み 30 で 0.037 / 0.012）から列 C の s = 30 の Δ(30) ≥ m(30)/2 はほぼ確実（M と同じ性質）。D_s も同じ性質（歩み 1 で r1 − 共有 hmm3 が約 +0.70・歩み 30 でジョイントが全員 hmm3）。型 1 か 2 かは G の語だけで決まる。打鍵の持続という別の説明（18 行）でも 3 つはそろって短い側で大きい。仕組みに固有の予測は R_ar3 が「歩みで変わらない」ことで、型の外にある。Aalbers "test a small number of (preregistered) hypotheses that make explicit what relation we expect"。
  - 解消: (i) 型 1 に「R_ar3 が『歩みで変わらない』」を加え、G と R_ar3 が両方動く場合を別の型にする。または (ii) D_s と ρ_h を作りの確かめと明記し型の名を「得が歩みに沿う形」に弱める。どちらでも、型 1 が 18 行の別の説明を排除しないことを限界に。
  - 自信: 中〜高
- [major] M2 勧め (1) の「境の歩み」が記号の数と交絡したまま歩みの効きとして入る
  - 位置: 146 行・160 行
  - 理由: 列 A は歩みと記号の数が一緒に動く（7 行）。r1 は 26 × 26 の表で、記号が約 1/30 になると r1 そのものが弱くなる。列 C の C2a は添えるだけで文を変えない。型 3 が出ても本文は「歩みが短いと負けた」と書き食い違う。ただし実務家には記録の時間を固定して歩みを選ぶ列 A が使う場面に近い（Saeb S1）。
  - 解消: 文を「この記号化で、同じ記録の時間から歩み <境> 秒より短く記号を作ると（記号の数も歩みとともに増える）、本人 hmm3 は本人の連鎖に負けた」に固定。列 C の C2a が入れ替わらないときの句（例「記号の数をそろえると入れ替わらなかった」）を逐語で決める。
  - 自信: 高
- [major] M3 仕組みの直接の量にあたる既に見た値が開示に無い
  - 位置: 91 行（副の量・本人と共有の ρ_h の差）・開示の表 27–35 行・S13 notes 81 行「hmm3 の本人（τ 他人）も同じ程度だった（o: 0.29〜0.63、u: 0.24〜0.63）」
  - 理由: 331 行の主張に最も近い観測は本人の当てはめが共有の運べない従属を運ぶかで、歩み 1 でほぼ差が無いことを書き手は知っている。それを副に置き型に使わない選択が既に見た値の後。構造の足りなさの試験の結果を見たかも開示に無い（notes 136 行）。Aalbers "to prevent data leakage from train to test data"。
  - 解消: 開示に本人 hmm3 の ρ_h の行を足す。構造の足りなさの試験の結果を見たかを 1 文。副に置いた理由を書き、型 1 の文に「本人の当てはめが運ぶ従属は副の量で、型に使っていない」と添える。
  - 自信: 中
- [major] M4 型 3 の持ち込みの文が型の条件で確かめていないことを言い切る
  - 位置: 131 行・157 行
  - 理由: 型 3 の条件は Q_C(s) ≈ Q_A(s) だけ。「歩み 1 の区間でも縮んだ」には列 C の G が A1 から C30 へ下がることが要るが、それは記述の語で型に使わない（117 行）。列 A と C がそろって縮まない場合でも型 3 になり、文は事実に反する。
  - 解消: 型 3 を 2 つに分ける（列 C の G が「減る」なら今の文、そうでなければ「記号の数をそろえると歩みの差は見えなかった。縮みの出どころはこの試験では決まらない」）。分けないなら「縮みは記号の数と合い」を外す。
  - 自信: 高
- [minor] m1 331 行以外の関連の文（main.tex 223 行 "which may also reflect the smaller amount of data"・337 行 "so whether it holds for symbolizations like theirs is open"・136 行 "our results concern this overlapping, smoothed form"）の書き換えが決まっていない。型 1 の文に「平滑を外した記号で」が無い。解消: 型ごとに 223・337 行の書き換えを逐語で決め、型 1〜4 の文に「平滑を外した記号（S13 の u）で」を入れる規則。自信: 高
- [minor] m2 語の揺れが低いときの扱いが無い（96 行）。解消: 例「主の語の割合が 12/17 未満なら、型の文に『書き手を 1 人抜くと語が変わる場合がある（x/17）』を添える」。自信: 中
- [minor] m3 停止の規則に既定が無い（167 行）。解消: 例「10 時間を超えたら列 B を外す」を既定に。自信: 中
- [minor] m4 列 C の区間が評価でも中ほどだけになり、頭の記号が抜けることが G の差と交絡（50・204 行）。解消: 限界に 1 文、副の採点がこの交絡の一部しか見ないことも。自信: 中
- [nit] n1 依頼文の「307 行」は main.tex では表の行（文は 331 行）。

## 5. 総合: major
- round 1 の 13 件はほぼ解消し g は大きく進んだ。
- 型を分ける D_s と ρ_h は列 C 対 列 A でほぼ作りから決まり、仕組みに固有の予測（R_ar3 が平ら）は型の外（M1）。本人側の ρ_h も開示に無い（M3）。
- 境の歩みの文（M2）と型 3 の文（M4）は型が保証しないことを言い切る。読みの型が変わるので再査読が要る。

## 6. 読めなかった範囲と注入の疑い
- 読んでいない: SEED・tau-extend conditions.md・kit・S13 scripts・supplement.tex。main.tex は 136・223・300–361 行だけ。
- 注入の疑い: なし。
