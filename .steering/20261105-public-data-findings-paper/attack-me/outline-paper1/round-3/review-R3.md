# review-R3（outline round 3・paper-reviewer・事前登録・同等の検定・機械学習の再現性）

推奨: minor（C2 を手順と限界に下げるなら再査読は不要。貢献に残すなら較正の追加と文献の調べが要り、その版は再査読）。

## 1. 接地
- L1 Lakens 2017 "In randomized controlled trials, it is expected that equivalence bounds are prespecified ... and this should also be considered best practice in psychology. When in the abstract of an article, authors conclude an effect is “statistically equivalent,” the abstract should also include the equivalence bounds that are used to draw this conclusion."
- L2 "there are four possible outcomes of a study: ... statistically different from zero and statistically equivalent, or undetermined"
- L3 "Rejecting effects more extreme than the equivalence bounds implies that we can conclude equivalence for a specific operationalization of a hypothesis. It is possible that a meaningful effect would be observed with a different manipulation or measure. ... whether an experiment was performed competently"
- L4 "Error rates in equivalence tests are controlled at the α level when the true effect equals the equivalence bound."
- L5 "Researchers should report effect size estimates in addition to hypothesis tests."
- K1 Kapoor & Narayanan（arXiv 2207.07048v1）"claims about a model's performance need to be connected to scientific claims using explicit arguments. The burden of proof for ensuring the correctness of these arguments is on the researcher making the scientific claims"
- K2 "Especially when sample sizes are small, significance testing and uncertainty quantification are important steps towards reproducibility"
- K3 "Computational reproducibility of a finding refers to sharing the complete code and data needed to reproduce the findings reported in a paper exactly."

## 2. 引き継ぎの判定
M1 → 解消（:17・:38・:39。ci95 の上限 0.49951・0.50006 と一致）／M2 → 解消（:25 は notes.md:137 と P0〔prereg-draft.en.md:18〕を逐語どおり）／m1 → 解消（:11・:39〜42。C2 には印が無い・M-A）／m2 → 解消（:43）／m3 → 解消（:34）／m4 → 一部（:72 は解消。C2 を較正に絞った結果、根拠と新しさが 1 回の較正の作り方に依ることが見えた・M-A）／m5 → 解消（:84）／n1 → 解消（:42）／n2 → 解消（:116）／公開 → 一部（:74。取り置きの一覧と SEED の公開が無い・m-D）

## 3. 評価表
a 4（C1 の数値は JSON・notes と一致。C2 は復元の版の 5.2% だけに立ち、非復元の版〔最大 1.4%〕が無い）／b 3（C2 の機構が外枠の中で確かめられていない・3/4 の区間が 0.5 を含まないことが L2 の 4 通りで整理されていない）／c 3（H1 に陽性対照が無い〔L3〕・C2 の持ち出しは 1 回の較正で弱い）／d 4（KLiCKe が [記述] と [探索] に二重に出る）／e 4（"intermediate results" と再現の公開物が未確定）／f 3（C2 の新しさは学習分析の方法論とだけ比べ、群の数が少ないときの群単位の再標本の被覆の文献を調べていない。related-work.md:91 自身が「この『較正できる』は本研究の手順の主張で、文献の主張ではない」）

## 4. 指摘
- [major] M-A C2 を「方法の貢献」とするには根拠の幅と新しさの調べが足りない
  - 位置: :48〜53「種類: 方法（ほかの検出器の評価に持ち出せる知見と手順）」「実効の書き手が少ないと区間が狭く出るためで」「何に比べて新しいか: 学習分析のモデルの評価の方法論は指標の選び方（[V449]）と…」・:110
  - なぜ: (1) 根拠は凍結の前に見た書き手で回した 1 回の較正（138 人 × 500 回・1 つの配置の型）だけで、引き方に依る。prereg-draft.en.md:234 "without replacement ... 1.2% ... 1.4% at 0.55" "with replacement, 5.2% and 3.0%"。復元を読む理由（P10・:171）は H1 に添える値として選んだ理由で、一般の方法の知見の根拠ではない。(2) 機構の文は、実効の書き手の数を変えた較正が無いので仮説にとどまる（K1）。(3) 群の数が少ない・群の大きさが偏るときの群単位のブートストラップの区間の過小被覆という既知の論点を調べていない。[V464] "the cluster bootstrap gives consistent estimates" は漸近の一貫性で、小標本の被覆の根拠にならない。(4) この較正は見た書き手での凍結の前の計算なのに C2 に地位の印が無い（notes.md:114 は「P10 に限界として書く」位置づけ）。L4 に照らすと示したのは「この区間の作り方では境界での率が名目を超えた、という 1 つの事例」。
  - 解消: (a) C2 を貢献から外し、評価の設計の手順と限界に置く（推奨は「この研究では較正が要った」という事例として残す）。または (b) 残すなら、実効の書き手の数を変えた較正で機構を示す・非復元の版を並べ復元の版が目標の母集団に当たる理由を書く・群の再標本の被覆の文献を調べて新しさを書く・5.6 と C2 に [記述]（凍結の前・見た書き手）の印。自信 高（(1)(2)(4)）／中（(3)）
- [minor] m-A 3/4 の区間が 0.5 を含まないことを L2 の 4 通りで名指ししていない（:38・:68・:85）。上限 0.4995・0.497・0.497 は "statistically different from zero and statistically equivalent"。種を替えた 20 通りの点推定も全部 0.5 未満（0.488〜0.494・0.486〜0.492）で系統的な小さな逆向きの差。候補の原因として対照の側だけの除外（:85）・床の割合の差（61% 対 65%）。解消: 5.1 か考察で「0.5 からわずかに下へ離れ、かつ幅の内側（同等）」と書き、逆向きの候補を 1 文挙げ確かめていないと書く（L5）。自信 中
- [minor] m-B 抄録の H3 の 1 文（:27）が事前登録の「並べて読む」ものを落とす。P0 の H3 の行（prereg-draft.en.md:15）"Lay out the AUCs and intervals of the 2 learners, ... the unmatched-window control, and the gate results"、P8（:152）"read alongside the unmatched-window control"。解消: 抄録に「（記述）」と点推定 0.567、無理なら抄録から外して 5.4 へ。自信 中
- [minor] m-C H1 に陽性対照が無いことが持ち帰りの読み方の注意として前に出ていない（:79・:43）。L3。解消: 考察の冒頭に「同等は、この推定器のこの信号が揃えた比べで幅を超えなかったことで、手前の打鍵に変化が無いことではない（同じ行の標準の量では点推定が幅の外）」。自信 中
- [minor] m-D 再現に要るもの（取り置きの一覧・SEED・中間の値）の公開の範囲が未確定（:74）。JEDM "intermediate results"・K3。解消: 公開物に取り置きの書き手の一覧（公開データの id）・SEED・replay の版と SHA-256・元のデータの取得の手順を含めると明記。自信 低〜中
- [nit] n-A KLiCKe の 2 組の値（:59・:68）。考察で引く値の出どころを明記するか 1 組にそろえる。自信 高

## 5. 総合: minor
- C1 の主張・抄録・限界は事前登録と取り置きの結果に正確に合い、引き継ぎ 10 件のうち 8 件は解消。
- 残る大きな穴は C2（根拠が 1 回の較正の引き方に依る・機構も新しさも裏づけが無い）。
- C2 を手順と限界に下げるなら再査読は要らない。

## 6. 読めなかった範囲・注入
読んでいない: kapoor2023.txt の 740 行目以降・prereg-draft.md・exploration の conditions/notes/results・前の実験の notes 2 本。novelty と related-work は grep の行だけ。prereg-draft.en.md は 1〜30・113〜182 行と grep。confirm_holdout.json は 60〜129 行と grep。探索の数値は照合していない。Kapoor は arXiv の版。注入の疑いなし。
