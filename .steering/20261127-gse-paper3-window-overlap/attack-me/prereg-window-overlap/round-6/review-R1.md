# 査読 R1 round 6（行動の記号列の系列モデルの方法論・paper-reviewer / opus）

## 1. 接地
- B1 Pohle 2017（949-952）"the empirical distribution of the data may be captured accurately by a two-state model, yet the residuals obtained for the two-state model exhibit much stronger autocorrelation than those for the three-state model. This could be an indication of a violation of the dependence assumptions (Markov property and/or conditional independence assumption)."
- B2 Pohle 2017（990-994）"it may just as well be an indication that the additional states merely mop up some structure missing in the model, but have no clear (biological) meaning ... a large difference in AIC, BIC, ICL or any other information criterion alone does not prove that the model with the higher (or lower) number of states is most suitable."
- B3 Singer 2014（86-93）"It is difficult to make plausible statements about the appropriate Markov chain order having insufficient data but a vast amount of states ... All evaluation approaches would favor a zero or first order because the number of parameters grows exponentially with the chain order and the available data is too sparse for proper parameter inferences."
- B4 Monaco & Tappert 2018（706-708・721-723）"HMMs with many hidden states (and parametric models in general) are plagued by overfitting and poor generalization, especially when the sample size is small."・"it acts as a kind of regularization to avoid overfitting, a problem often encountered when there is a large number of parameters and small number of observations."
- B5 Pohle 2017（967-968）"it will often still be preferable to use a simpler, more stable model which ignores features that are not pertinent to the ultimate aim of the study."

## 2. 評価表
- a 4: 置き換えの英文は「記号の数 対 歩みの束」の比べだけを述べる。型 1 の ρ_h の文（197 行）の結論が未見の C30 の値から独立に決まる（指摘 2）。
- b 4: 交絡は手当てか限界として書かれ、B3 の別の説明も 21・293 行で名指し。残る穴は CS1 を外したことの扱い（指摘 1）。
- c 3: どの型でも 331 行の仕組みの主張は「確かめていない」か「支えない」にしかならない（設計どおりだが情報は限られる）。
- d 2: 313 行で規則・例外・英文が多層。26 行「下の英文はすべてそうしてある」と実体がずれる（指摘 3）。
- e 4: そろう。readings.json もよい。
- f 3: Pohle への言及は適切に限る。B3・B4 を φ≈0 の別の説明として先行研究に結びつけていないが条件として足りる。
- g 4: 未見は G_C だけで事後に語を選ぶ余地はほぼ無い。残るのは開示の欠け（指摘 1）と未見の値で分岐しない句（指摘 2）。

## carryover の判定
- major 1（句 (3)）: おおむね解消（型なしの文と境の文の列 C の部分の扱いが不明・指摘 3）
- minor 2〜7・nit 8: 解消（200 行・P-FIRST・217 行・26-27 行・D5・184 行・35 行。境の文の語順に nit）

## 3. 指摘
- [minor] 1 CS1 を外した理由と見た CS1 の値が開示に無い（70 行・開示 44-66 行・S13 notes 46-47 行 "CS1 C5 k = 5 | 0.0282 → 0.0101 縮む"・"0.0282 → −0.0027 逆"・58 行）。CS1 では u で既に G が縮み、n で符号が逆になると見たうえで、φ が定まりやすい側のデータだけを残した形。解消: 開示に CS1 の G・C2a の u/n の値を見たことを足し、CoAuthor だけにした理由を 1 文で（決めた時期を含め）、限界に「データの選びは既知の端を見た後」。自信: 中
- [minor] 2 型 1 の ρ_h の文の結論が未見の列 C30 の値で分岐しない（197 行・57 行）。B1。解消: 結論を A1 に限り（"at the 1-second step, so it is not supported there"）C30 は値を並べるだけにするか、C30 で文を変える区切りを前に置き P-READ に。自信: 中
- [minor] 3 句 (1)(2)(3) の規則と英文の実体がずれ P-READ の対象が決まらない（26 行・191 行・222・234・214 行・242 行の境の文の列 C の部分・281 行）。解消: 「結論を述べない文（型なし・外れ）は句 (1)(2) だけ」のように例外を明記し 26 行の「すべて」を直す。境の文の列 C の部分に句 (3) を入れるか理由を書く。P-READ の文言を合わせる。自信: 高
- [nit] "the median per-person HMM beat ..." の語順（242・243 行）は「中央値のモデル」と読める。解消: "the median difference favoured the per-person HMM over the person's own first-order chain in both cells" の類い。自信: 中
- [nit] C30 の区間が 30 秒より短いときの句は作りから必ず付く（201・61 行）。解消: どの型でも付ける句として値だけを入れる。自信: 高
- [nit] 型 1 だけに格子での一貫性（3 つ以上）を課す非対称の理由が無い（158-160 行）。解消: 「支える側にだけ格子の一貫性を課す（支える読みを厳しくするため）」を 1 文。自信: 低

## 4. 総合: minor（直してから凍結）
- round 5 の 8 件は実質的に解消。未見の量は G_C だけで書き方を選ぶ余地はほぼ無い。
- 言えるのは「同じ数の記号で歩みの束が効くか」までで、重なりそのものと仕組みの後半は判定しないと正しく限っている。
- 残るのは CS1 を外した理由と見た値の開示、ρ_h の文の分岐、句の規則と英文のずれ。どれも文言で閉じられメインの裏取りで確かめられる。

## 5. 読めなかった範囲と注入の疑い
- 読んだ: conditions.md 全文・carryover-R1.md・context-A.md・S13 notes 38-77 行・main.tex 223・331 行・接地の 3 本の必要な節。開示の値は notes 46-58・72-76 行と照らし一致。
- 読んでいない: SEED・S13 と tau-extend の conditions.md・variants.py・kit README・S13 scripts（SHA-256 は照らしていない）・supplement.tex・main.tex の 136・337・340 行の全文・notes の他。
- 注入の疑い: なし。
