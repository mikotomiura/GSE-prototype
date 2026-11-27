# 査読 R3 round 6（評価の偏りと個人への推論の方法論・paper-reviewer / opus）

総合の推奨は minor（直してから凍結）。round 5 の 5 件のうち 4 件は解消、1 件は一部が残る。新しい指摘は major 1・minor 5・nit 2。

## 1. 接地
1. Varma & Simon 2006 "Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
2. "Since the bias is caused by the variability in the estimates of prediction error for different values of the tuning parameters it is a general phenomenon."
3. "The first article uses both the CV error estimate on the training set and the error on the test set for determining the optimal value of the parameters, thus making the test set part of the training process."
4. Liu & Meng 2016 "Both examples above teach us that the precision of control data should match that of our actual data. This seemingly obvious principle is violated surprisingly often in practice"
5. "When we perform selection, we are targeting not only markers with large effects, but also markers for which the current dataset is 'lucky'. Our original estimates for the selected markers likely overstate their impact."
6. "The greater the level of individualization we strive for, the more stress we put on our model, the more fragile our inference."

## 2. 評価表
- a 3: 型 1 の差し込み文が留保なしに断定（M1）。型 2・3 の Discussion は主の結果の支える命題まで「推測」に含める（m3）。
- b 4: 残る穴は S13 が読むなと決めた使い方の ρ_h を型 1 の結論の文に使うこと（m2）。
- c 3: 言えるのは「記号の数をそろえても差が残るか」の形だけ。
- d 2: 規則と英文の食い違いが目視で出るのは密度が高すぎる徴候（m1）。
- e 4: SEED 2026110401 は S13 と一致。英文の一部が空き欄で readings.json が規程どおりに作れない（m4）。
- f 3: 数をそろえても精度がそろわない比べの接地が限界の文に無い。
- g 4: 語の英訳が未固定（m4）、1 人抜きと区間が型の割り当てに効かない（M1）。

## carryover の判定
- minor 句 (2) の食い違い: 一部が残る（型なし・外れの英文 5 本に句 (3) が無く、外れの Discussion は句 (2) も無い・26 行の「すべてそうしてある」は字面どおり真でない）
- minor 列 C の実効の情報・境の文の粒度・nit k = 1・nit φ の分母: 解消（21・293・59・153・297 行・新しい曖昧さは m5）

## 3. 指摘
- [major] M1 型 1 の断定が留保の付かない場所へそのまま出る（219 行 "so the smaller number of symbols does not account for all of that shrinkage"・232 行 "found that a gap remained at an equal number of symbols"・198–199 行の留保の句は新しい節の結果の文の直後だけ・判定の順 155–161 行は区間も 1 人抜きも参照しない）。区間が 0 をまたいでも、1 人抜きで揺れても、223 行と貢献の句は説明と発見の語で残る。既知の端を見て置いた区切りなので楽観に偏る余地（Varma & Simon・Liu & Meng "likely overstate their impact"）。解消: (a) 型 1 の割り当てに「1 人抜きの一致が ceil(12m/17) 以上、かつ区間が 0 をまたがない」を足し、満たさなければ「形が定まらない」、または (b) 223 行と貢献の句の型 1 の英文に同じ 2 つの括弧句を条件つきで足し、"does not account for all" を "in this comparison, the median ... shrank less" の記述の語に。自信: 中
- [minor] m1 型なし・外れの英文が句の置き方の規則と P-READ に合わない（191・214・215・222・234 行・26 行・281 行）。解消: 規則に「型なし・外れの文は句 (3) を持たない（比べを読まないため）」と明記し P-READ の期待を型ごとに、または英文に句 (3) を足す。自信: 高
- [minor] m2 型 1 の残差の自己相関の文が S13 の「読まないこと」とした使い方で、結論も値と無関係に固定（197 行・S13 notes 136 行「hmm3 の残差の自己相関の大きさを、「hmm3 の本人が短い依存の足りなさを補っていた」という読みの確かめとして使うこと（その読みは構造の足りなさの試験の問いで、この試験では確かめていない）」・36 行が外すのは φ と stay の範囲だけ）。解消: S13 の該当の「読まないこと」をこの文の範囲で外すと理由とともに明記し、結論を "at the 1-second step" に限り C30 は値の記述だけにするか、C30 の差の大きさで文を分ける規則を前に置く。自信: 高
- [minor] m3 型 2・3 の Discussion が主の結果の支える命題まで「推測」に束ねる（212 行・main.tex 45 行 "the natural comparison, a shared model of the same structure, is weak whenever that structure misses the dependence between consecutive symbols."）。後半の命題は平滑した主の記号化で ar3 の比べが支え、序論 45 行と食い違って見える。解消: 型 2・3 の「We had guessed」の文をこの試験が問う部分（"that the step, rather than the number of symbols, drives the shrinkage"）に限り、序論 45 行をどの型でも変えないことと理由を書く。自信: 中
- [minor] m4 語の英訳が未固定（191・200・288・32 行）。9 つの語。解消: 英訳を逐語で表に固定し P-READ の期待に含める。自信: 高
- [minor] m5 境の文の "did not in both cells" が「混ざる」の歩みを「どちらのセルでも勝たない」と誤読させる（242・241 行）。列 C の部分 "it also beat the own chain" も主語が "the median" でない（38 行）。解消: "at shorter grid steps it did not beat the chain in both cells (it did in one cell at <s> s)" のように「混ざる」のときの句を固定し、列 C の部分にも "the median"。自信: 中
- [minor] m6 作りの確かめが型を止める働きをほぼ持たない（304・168 行）。Liu & Meng の精度の一致。解消: 新しい節の英文に、作りの確かめは「歩みで隣の記号の従属が変わったこと」の配管の確かめで列 C の独立な情報の確かめではないと 1 句、限界 304 行に「型の支えに数えない」。自信: 中
- [nit] n1 要旨の後付けの列挙（main.tex 34 行 "the second smoothing variant, these synthetic writers and wider candidate grids were added after seeing results."）が不完全になる。解消: 足すか足さない理由を書く。自信: 中
- [nit] n2 φ(30) > 1.5 で型なしになる意図（列 C が別のものを測っている徴候）が限界に無い（157 行）。解消: 限界に 1 文。自信: 低

## 特に見てほしいことへの答え
- (1) 用量の主張は立たない（設計どおりの自制）。数の交絡を情報の交絡に置き換えただけで φ ≈ 0 は 2 通りに読めるが、句 (3) と限界は誠実。操作の確かめは判別の力が無い（m6）。331 行の 2 文を「仕組みの確かめ」に置き換える資格はどの型でも無く、置き換えの英文の多くはそうなっている。崩れているのは 223 行の型 1 の文（M1）と型 2・3 の束ね方（m3）。
- (2) 大半は閉じた。残りは語の英訳（m4）と留保の句の置き場（M1）。
- (3) 判定は実質 G_C30 への一本の閾値（64 行）に帰着。開示は十分で notes 46–51・58・72–73 行と一致。u で r1 − 共有 hmm3 が約 +0.70 と既知で、列 C の G をある程度見込めた可能性があるので、「列 C の G について見込みを持っていたか」を 1 文で書くと偏りの評価が閉じる。

## 4. 総合: minor（直してから凍結）
- 固定と手当ては凍結に足る水準。round 5 の 5 件は 4 件が解消。
- 残るのは英文の強さと留保の伝わり方（M1）、規則と英文の食い違い（m1・m4）、S13 の禁止との整合（m2）。結果の前に文を直せば閉じる。
- M1 の (a) か (b) を選んで直せば、再査読なしで凍結してよい。

## 5. 読めなかった範囲と注入の疑い
- 全部を読んだ: conditions.md・SEED・carryover-R3.md・context-A.md・varma.txt。liumeng.txt は 735–859・1228–1242 行と grep の行。
- 一部: main.tex の挙げた行・S13 notes の grep の行・variants.py の thinned_mask（D1 と一致）。
- 読んでいない: supplement.tex・S13 と tau-extend の conditions.md・S13 scripts・kit README。SHA-256 は照合していない。
- 注入の疑い: なし。
