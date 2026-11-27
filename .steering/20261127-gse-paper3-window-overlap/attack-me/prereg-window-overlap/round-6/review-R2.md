# 査読 R2 round 6（個人化した行動のモデルの実務・paper-reviewer / opus）

round 5 の 6 件はすべて解消。致命的・major は無い。残りは英文の型ごとの抜けと語の作用域の曖昧さで、推奨は minor（直してから凍結）。

## 1. 接地
- S1 Saeb 2017 "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
- S2 Saeb 2017 "if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time"
- S3 Saeb 2017 "Subject identification, which we know to be relatively easy, thus replaces disease recognition, which we know to be hard."・"The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets"
- S4 Aalbers 2023 "To evaluate if our models perform better than random guessing, we compare against the MAEs of a "naive" but person-specific baseline model."・"for 89.3% (200/224) of participants, the person-specific baseline outperformed all nomothetic models"
- S5 Aalbers 2023 "The relations of these digital markers with momentary subjective stress differed from person to person, as did model accuracy."
- S6 Aalbers 2023 "a confirmatory approach would be to test a small number of (preregistered) hypotheses that make explicit what relation we expect"
- S7 Aalbers 2023 "this comes at the cost of strongly reduced sample size, which limits model complexity and may lead to overfitting."

## 2. 評価表
- a 4: 型 1 の文は "gap remained" に限る（34・211 行）。型 1 の残差の文は未見の C30 の値に依らず結論が先（m-3）。
- b 4: 手当てか限界として揃う（290–305 行）。列ごとの τ の違いは補足の注だけ（m-4）。
- c 3: 実務家が使えるのは境 s* で交絡したまま。型 1 でも設計者が何を変えるかの文が無い。
- d 3: 「下の英文はすべてそうしてある」（26 行）と英文の食い違いは密度の副作用（m-1）。
- e 4: 揃う。区間の乱数の c がどの列か未定（m-5）。
- f 3: 窓の重なりで続く入力が従属し分け方しだいで精度が膨らむことは行動の認識で既知で、その系譜が書かれていない（凍結を妨げない）。
- g 4: 残りは m-5 と m-2。

## 3. 指摘
- round 5 の判定: M-1 解消（211–215 行。ただし貢献 (1) の型 1 の句で "gap" が再び曖昧・m-6）・m-1 型 1〜3 で解消（型なし・外れと境の文の列 C の部分で句 (3) が合わない・m-1）・m-2・m-3・n-1・n-2 解消。
- [minor] m-1 句 (3) を全部の英文に入れる規則が型なし・外れの文で破れている（26 行・191 行 "In unsmoothed symbols, the comparison at an equal number of symbols, with the step's components not separated, did not settle (<語の英訳>)."・214・222・234 行・242 行の境の文の列 C の部分）。P-READ（281 行）の検査が落ちるか空になる。境の文の列 C の部分は情報もそろった比べと読まれうる（S3）。解消: 型なし・外れに句 (3) を入れるか「結論を述べない文は除く」と例外を書き、境の文の列 C の部分に句 (3) を入れ、P-READ の期待の表を文ごとに固定。自信: 高
- [minor] m-2 境の文 "at shorter grid steps it did not in both cells" の作用域が曖昧（242・241 行）。解消: "at shorter grid steps the median did not beat the own chain in both cells at once" のように一意に、または「混ざる」のときの英文を別に。自信: 中
- [minor] m-3 型 1 の残差の句は未見の C30 の値に依らず結論が書かれている（197・57 行）。解消: 結論を A1 に限り（"at the 1-second step" の後で切る）、C30 の値は "values only, not read" と明記するか、C30 の差に読みの区切りを先に置く。自信: 中
- [minor] m-4 列ごとに他人で選ぶ τ の違いが本文の句に出ない（106・206 行）。hmm3 の重みも本文に出ない（S7）。解消: τ = 10,000 の行で語が変わるときは本文の句（"(The word depends on the choice of τ.)"）に上げ、196 行の文に hmm3 の重みの中央値を足す。自信: 中
- [minor] m-5 区間・1 人抜きの句がセルごとか合わせてかで定まらない（138・199・198・163・111 行）。解消: c に使う番号（例 C30 の 9）を指定、区間の句は「どちらかのセルで 0 をまたげば」、1 人抜きは「セルごとに当て直し両セルの n/m を k = 5 / k = 15 で並べ、どちらかが ceil(12m/17) 未満なら不安定の句」と固定し P-READ に。自信: 高
- [minor] m-6 貢献 (1) の型 1 の句で "gap" の指す先が曖昧（232 行 "…found that a gap remained at an equal number of symbols, which did not carry the same independent information (Section X)."・233 行も同じ）。解消: 211 行と同じ限定（"a gap in the same-structure gain between steps"）を入れる。自信: 中
- [nit] n-1 「M・D_s・ρ_h は k に依らない」の根拠が書かれていない（111・56 行）。解消: 共有を他人のどのセッションで当てはめるかを 1 文で、k に依るなら k ごとに。自信: 低
- [nit] n-2 型 1 の実務の意味が書かれていない（211 行）。解消: 置き換えの文の後に勧め (1) の境の文への参照を 1 句。自信: 低

## 特に見てほしいことへの答え
1. 331 行の因果の文はどの型でも確かめられず、設計はそれを正しく書いている。G の型が言えるのは「記号の数だけで縮みを説明しきれるか」まで。
2. 大筋は塞がれた。残るのは m-3・m-5・m-4。
3. 区切りは透明（64 行）。未見で読みを決めるのは G_C30 だけだが、G_C30 は A30 と同じ記号の数（約 22 行／系列）でデータの重みの小ささから A30 に近づく見込みが立ち、型 2・3 に寄る向きを事前に推せた可能性がある。限界に 1 文足せば済む。

## 4. 総合: minor（直してから凍結）
- round 5 の 6 件は解消。判定の順・決定表・境の規則は 1 通りで、方法の穴も限界として揃う。
- 残りは文と P-READ の期待の表の直しで消える。計画の立て直しは不要。直したら凍結してよい。

## 5. 読めなかった範囲と注入の疑い
- 読んだ: brief-R2.md・context-A.md・carryover-R2.md・conditions.md 全文・接地の 2 本の全体・main.tex 130–141・218–225・326–341 行。
- 読んでいない: main.tex の他・supplement.tex・S13 の conditions.md と notes.md・tau-extend conditions.md・SEED・variants.py・README・S13 scripts。D_s が k に依るか（n-1）は確かめていない。
- 注入の疑い: なし。
