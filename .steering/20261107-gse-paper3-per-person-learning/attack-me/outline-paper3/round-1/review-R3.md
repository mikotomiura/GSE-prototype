# review-R3（方法論と再現性・round 1）

## 1. 接地
- G1 Varma & Simon: "Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
- G2 Varma & Simon: "The parameter selection bias, on the other hand, is always negative." / "This implies that for large K , there is a high probability that choosing the minimum resampled error will give a biased estimate of the true error."
- G3 Varma & Simon: "The second article presents only the minimum CV error estimate obtained on the training set. The true error obtained on an independent test set is not given for either."
- G4 Liu & Meng: "The degree of individualization should therefore scale with the reliability of our model." / "if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust."
- G5 Liu & Meng: "we predict each individual's response using the remaining n − 1 individuals ... our inference will be more robust. The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's background ~x0 —our inference will be less relevant."
- G6 Liu & Meng: "Ignoring the selection bias will lead to seriously flawed inferences (see Leeb and Pötscher, 2005)."

## 2. 評価表
a 2（"exactly zero" は定義上・C2 の対比が平滑の自己相関と未分離・"established" に不確かさが無い）／b 2（4 つの解析を結果を見て順に設計・格子の延長も事後・人数・無限大の log loss・組み入れが本文に無い）／c 3（手順は持ち帰れるが関連性の代価を書かない）／d 4／e 3（データの入手の声明・当てはめのコードの公開が無い）／f 2（階層・経験ベイズの partial pooling に対し位置づけが無い）

## 3. 指摘
1. [major] 解析の順の設計と格子の事後の延長で、選択が評価の外（outline:56・28）。解消: 3.4 に何を見て何を決めたかを本文で・条件の凍結の物証・選択の全体を外側の loop に入れた値か理由・延長が事後であることを明記。自信 高。
2. [major] CS1 の "exactly zero" は定義上（outline:7・15）。解消: 選択の結果として書く・本人の過去で τ を選ぶ値（S8）を併記し楽観の偏りを注記。自信 高。
3. [major] C2 の短い範囲の依存が記号化の平滑・30 秒窓・1 Hz の自己相関と未分離（outline:18・37、README:21–29）。解消: 平滑の無い記号か重ならない窓での対照・S6 を本文へ・または C2 を「この記号化の上で」に限定・合成の陰性対照。自信 中〜高。
4. [major] 不確かさと人数が本文に無く "established"（outline:16・23・58）。解消: 主表と図に n・IQR・割合・区間・"established" を言い換え。自信 高。
5. [major] 新規性（組み合わせ）が階層・経験ベイズに対し位置づけられていない（outline:27・43）。解消: 関連研究に多水準・階層の系列モデルの段・新規性を「この手順を当てて報告した例」に・未読 4 本を読む。自信 中。
6. [minor] 文献の検索の手順（outline:14・19）。解消: DB・検索式・日付・件数を補足に。
7. [minor] 組み入れと除外（無限大の log loss・パネル）が人の集合を選ぶ（outline:56・60）。解消: 規則と人数と、除外の有無の値。
8. [minor] "up to +0.19" が最大値（outline:7）。解消: 範囲と人数。
9. [minor] 外枠（outline:70 照合をこれから）と README（済み）のずれ・当てはめのコードの公開・データの声明。
10. [minor] Liu & Meng の引き方が代価の側を欠く（outline:26）。arXiv v1 と掲載版の照合。
11. [nit] 代理ラベルの段落を補足だけに。

## 4. 推奨: major
中心の主張が「手順が個人化しないことを選んだ」結果を「利得が消えた」と読ませる／C2 が平滑の自己相関と未分離・選択の偏りが本文で未開示／C3 を階層・経験ベイズと代価に対して位置づけ直す。

## 5. 読めなかった範囲・注入
liumeng.txt の一部（1025〜1374・1415〜1654・1775〜2013 行）は読んでいない。varma.txt は全部。注入の疑い: なし。
