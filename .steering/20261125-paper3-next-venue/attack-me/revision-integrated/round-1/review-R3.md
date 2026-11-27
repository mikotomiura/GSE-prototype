# review-R3（評価の偏りと個人への推論の方法論・TMLR・round 1）

総合: major。読んだもの: brief-R3・context-A・varma・liumeng（1〜928 行）・main.tex・supplement.tex（296〜434 行・540 行〜末尾）。liumeng 929 行以降・supplement 1〜295 行と 435〜539 行・references.bib・figdata・kit README は読んでいない。注入の疑い: なし。

## 1. 接地
- V1（Varma & Simon 2006）"Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
- V2 "CV methods are proven to be unbiased only if all the various aspects of classifier training takes place inside the CV loop."
- V3 "The parameter selection bias, on the other hand, is always negative." ／ "Since the bias is caused by the variability in the estimates of prediction error for different values of the tuning parameters it is a general phenomenon."
- V4 "thus making the test set part of the training process."
- L1（Liu & Meng 2016）"if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust."
- L2 "When uncertainty assessments based on internal replications diverge from those based on external replications, a failure in statistical modelling has occurred, leading to unreplicable research"
- L3 "With this greater descriptive power comes the danger that our pattern captures features of the observed pixels that do not generalize (artifacts)."
- L4 "without this matching step, our inference ignores selection bias."

## 2. 評価表
a 3（本文はよく限定。ただし 325 行が S14 の制約を運ばない・題の "vanishes" と要旨が入れ替えの差と S14 を出さない）／b 3（入れ子なし・目標の書き手の漏れ・結果の後の格子の拡張と端での選択。開示済みだが主の比が依存。S14 は頻度だけの基準線が同じ T）／c 3（助言は安く使えるが実証は 1 記号化・CoAuthor 17 名。仕組みの説明は記述に留まる）／d 3（事後の確認が層をなす。S14 約 1,600 語が主の問いと結ばれない）／e 4（範囲に入る）／f 4（位置づけは適切。識別と予測の関係は補足の Dehling2024 だけ）

## 3. 指摘
- [major] S14 の頻度だけの基準線が同じ T なのに、本文の 1 文が「遷移の表の空間で」識別できたと書く
  - 位置と引用: supplement.tex:585–587（k=1 は 0.912 対 baseline 0.941・k=5 は 0.982 対 0.982・k=15 は 0.996 対 0.989）／supplement.tex:604 "The frequency baseline reflects marginal differences such as the pause share; no statement is made about the difference between it and the cross-likelihood."／main.tex:325 "in the space of one-state transition tables, a writer's training units ranked on the panel average closer to the writer's held-out units than other writers' training units did."
  - なぜ問題か: 識別を担うのが遷移でなく周辺分布であることと矛盾しない。読者は順序の依存が識別されたと読む（L3）。表の値を本文に書くのは読みの改変に当たらない。問い 1 への答えは「不十分」。
  - 解消の条件: 本文の文に事実として「a frequency-only baseline, which ignores transitions, ranked as well (T 0.941, 0.982, 0.989)」を足す。
  - 自信: 高
- [major] 限界の第 1 項の末尾の 1 文が確認の主張に読まれうる
  - 位置と引用: main.tex:325 "In an exploratory check with its reading committed before the data were read (\Sref{14}), in the same CoAuthor records at $k=5$ ..."（"The scientific question stays open." の項の最後）
  - なぜ問題か: "reading committed before the data were read" が確認のように響き、項の主題の直後に肯定の結果だけを置くので部分的な答えに読める。S14 の制約（supplement:576 drift・604「own」に装置と話題・頻度の基準線・補正なしの 9 セル）が本文に無い。L2 に照らし、同じ記録で逆の印象を与える両者の関係を書かない。
  - 解消の条件: 文を "...; this ranking does not separate the writer from closeness in time, device or topic, and a frequency-only baseline did as well, so it is not read as a stable per-person difference." のように閉じるか、本文から外して補足の案内だけにする。
  - 自信: 高
- [major] S14 は "lack sufficient depth" への答えとして働かず、論点を増やす
  - 位置と引用: supplement.tex:603 "Neither result is used to deny or support the other" ／ "The result does not change how the per-person weight is chosen."
  - なぜ問題か: 一句は仕組みと一般化の不足と読める。S14 は主の問いと結ばないと宣言し、新しい問い（識別できるのに予測で得をしない）を開いたまま置く。入れ替えの差（2.5e-2・全員）と合わせて論じれば深さになる。
  - 解消の条件: (a) 考察に識別と予測の得の差を説明する短い段（凍結した読みの外・事後と明示）。(b) S14 を本文から外し、深さは仕組みの節（弱い構造の共有に対し τ=0 の個人の当てはめが連続する記号の依存を直して見えることを、小さな解析か合成で示す）で示す。
  - 自信: 中
- [major] 入れ子が無く、結果の後の格子の拡張と端での選択に主の比が依存する
  - 位置と引用: main.tex:328 "the extensions of the $\tau$ grid and the structure families may favour a smaller remainder"／main.tex:330 "a nested design was not run, and the writer split does not cover the leak of the target writer's units into other writers' shared models."／supplement.tex:342 "Because the choices sit at the edges of both grids, the grid extensions made after seeing results lie outside what the split checks."
  - なぜ問題か: V1・V2 では格子の設計も選ぶ手順の一部。偏りは「小さい残り」＝見出しの側に働く。要旨の "shrank more than thirtyfold" がこの開示を運ばない。
  - 解消の条件: 入れ子を k=5 と 15 で回す、または要旨の比の文に「after grids were widened post hoc」を付け、拡張前の格子（τ≤10^4）での残りを表に 1 行並べる。
  - 自信: 中
- [minor] 題と要旨が書き手や時間に固有の信号を示す結果を落とす（main.tex:29 題・275 行 "The writer's own units beat the swapped fit by $4.7\times10^{-3}$ at $k=5$ and $2.5\times10^{-2}$ at $k=15$, for every writer"）。解消: 要旨に入れ替えの 1 文（時間の近さと量を分けないことを添えて）・題を中立な形に。自信: 中
- [minor] S14 の間引きの規則が CS1 を情報の無い状態にする（supplement.tex:597 "In CS1 one writer's held-out assignment has 48 transitions, so every $B$ is thinned to 48, and at $k=1$, $g=1$ every $A$ to 2."）。解消: CS1 の行を「範囲外のため読まない」と表で区切る。自信: 中
- [minor] 区間は条件つき（main.tex:175）。解消: 表 3 のキャプションにも "not procedure uncertainty" を揃える。自信: 低
- [nit] 事後の確認の地図が S8 にしかない（main.tex:177 "four analyses designed one after another and thirteen later checks"）。解消: 段と節の対応の 1 行の表か図。自信: 低

## 4. 推奨: major
主の主張は慎重に限定され技術的な正しさはおおむね満たすが、見出しの比が結果の後の格子と入れ子の無い選択に依存する。S14 と本文の 1 文は自らの制約を本文で運ばず誤読されうる。S14 は深さに答えていない。
