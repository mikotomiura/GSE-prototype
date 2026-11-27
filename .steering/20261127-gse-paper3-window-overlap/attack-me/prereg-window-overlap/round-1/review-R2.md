# 査読 R2（個人化した行動のモデルの実務・paper-reviewer / opus）
stage: prereg。対象: experiments/20261127-window-overlap-dose/conditions.md（158 行）

## 1. 接地
- S1 Saeb 2017 "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
- S2 Saeb 2017 "Subject identification, which we know to be relatively easy, thus replaces disease recognition, which we know to be hard."（重なりが生む従属が本人らしさの信号の代わりに得を作っていないか）
- S3 Saeb 2017 "very often, these are chosen such that the prediction error is minimized over the whole dataset. This makes the algorithms overfit"
- S4 Aalbers 2023 "To evaluate if our models perform better than random guessing, we compare against the MAEs of a 'naive' but person-specific baseline model."・"for 89.3% (200/224) of participants, the person-specific baseline outperformed all nomothetic models"
- S5 Aalbers 2023 "this comes at the cost of strongly reduced sample size, which limits model complexity and may lead to overfitting."
- S6 Aalbers 2023 "a confirmatory approach would be to test a small number of (preregistered) hypotheses that make explicit what relation we expect"

## 2. 評価表
- a 3: 確かめるのは「歩み」で 331 行の「重なり」とは別。D は r1 を含む。型 1 の文は R が「減る」でも「沿わなかった」と書く。
- b 2: (1) 量の交絡は挟めていない（A も B も情報の量は歩みとともに減る） (2) R は構造が入れ替わると比べられない (3) 予測の先の長さとの交絡は限界として書かれている。
- c 3: 図と 307 行の書き直しは決まるが、「どの歩みなら同じ構造の比べでどれだけ膨らむか」という実務家の形の出力が決まっていない。
- d 3: 2 段の引き継ぎを辿らないと組み上がらない。
- e 4: 固定・門はそろう。機械をまたぐ 1e-9 の門が外れたときの扱いが空いている。
- f 3: Pohle と Uto2020 だけ。重なる窓が評価を楽観に振る既知の問題（S1・S2 の系統）に位置を与えていない。
- g 3: 2 セルで割れたとき・欠けのときの型と論文の文が未定（S13 の notes 119・142 行と同じ穴）。開示に事実の誤り。

## 3. 指摘
- [major] 1. 開示が誤っている: 端の R は既に見ており、列 A の R は「減る」と読める
  - 位置: 21 行「端の R も未見である。」・supplement.tex 549 行 "The joint-choice remainder with $u$ is \e{5.8}{-4} (1.00) and \e{8.0}{-4} (0.94) at $k=5$ and 15"・同 "With $n$ the joint choice picks the \hmmthree{} for every writer in CoAuthor at $k=5$ and 15"・notes 128 行
  - 理由: R(1) ≈ 6e-4〜8e-4、R(30) は hmm3 が選ばれ R = C2b − C2a + G で約 0.096。列 A の R は「減る」とほぼ決まる。型 1 の条件は構造の入れ替わりで満たされ、文は「減った」を誤って述べる。Aalbers "make explicit what relation we expect"。
  - 解消: 21 行を直す（u の R の値と n の構造の選びが既知、列 A の R(30) が導ける）。型 1 と型 4 の R の条件を「沿わない」と「減る」に分け、文を先に決める。
  - 自信: 高
- [major] 2. R は選ばれる構造が歩みで変わると同じ量として比べられない
  - 位置: D4・D5 型 1
  - 理由: s = 1 で ar3 の残り、s = 30 で hmm3 の得。強い構造の比べが重なりに影響されるかを測っていない。Saeb "Subject identification ... replaces disease recognition"。
  - 解消: 主の R を構造を ar3 に固定した残り（既にある ar3 固定の行・τ は他人）に。ジョイントの R は副。または構造が変わったセルを「比べない（構造が変わる）」とする語を先に足す。
  - 自信: 高
- [major] 3. 量の交絡は「逆の側から挟む」になっていない
  - 位置: 29 行
  - 理由: 列 B の s = 30 はほぼ同じ写し 30 本で、情報は列 A の s = 30 とほぼ同じ。情報の量は A でも B でも歩みとともに減る。写しの重複が r1 と hmm3 を実際の情報より自信のある当てはめにする。Aalbers "strongly reduced sample size ... may lead to overfitting"。
  - 解消: 重なりを固定して量を変える列（s = 1 の列 A から各系列の連続する 1/s の区間を採る）か、k の軸で量を合わせた組（s = 1・k = 1 の 624 と s = 30・k = 15 の約 320）を先に指定し読みの語を決める。29 行の「挟む」を外す。
  - 自信: 高
- [major] 4. D は「本人の連鎖 − 共有 hmm3」で個人化が混ざる。G との結びつきも集計の並びだけ
  - 位置: D4・main.tex 331 行 "a shared model whose structure misses that dependence makes a per-person fit look good"
  - 理由: 仕組みを測るには、共有どうしの差（共有 ar1 または ar3 − 共有 hmm3）と、本人の hmm3 が共有 hmm3 より従属を運ぶかの印（擬似残差の遅れ 1 の減り）が要る。予測の先の長さが両方に同時に効くので、同じ向きに動くことは十分な印にならない。Aalbers の person-specific baseline と共有の構造の足りなさは別の比べ。
  - 解消: D を共有 ar1 − 共有 hmm3 に置き換えるか主に、r1 − 共有 hmm3 は副に。本人 hmm3 と共有 hmm3 の残差の遅れ 1 の差を量に足し型の条件に入れる。少なくとも型 1 の「運べない従属」を測った量の名に直す。
  - 自信: 中
- [major] 5. 割れたときと欠けたときに型と論文の文が決まっていない（S13 と同じ穴）
  - 位置: D5・型 3・notes 119 行・142 行
  - 理由: G が割れれば型 3、D が割れれば型 2 に落ちるが意図か不明。列 A の G は k = 15 で既知の端（0.155 → 0.096、差 0.059 < m/2 = 0.078）から「増える」にならず、k = 5 は「増える」になりうる。列 A の G はすでに割れると見え、型 3 の付記の語が結果の前に決まっている。
  - 解消: 各量の語が「割れる」「欠け」「定まらない」のときの扱いと論文の文を表で先に決める。型 3 の付記に列 A の G の既知の端からの予見を開示する。
  - 自信: 高
- [minor] 6. 確かめられるのは「歩み」の用量で、「重なり」と「他の分野」には届かない。型 1 の「貢献に仕組みを足す」は言い過ぎ
  - 解消: 文を「歩み（重なりと先の長さが同時に変わる）に沿う形を測った」に限り、「仕組みと合う形を足す」と書く。窓の長さ W を変えて歩みを固定する列（例 歩み 10・W ∈ {10, 20, 30}）を限界か次の試験として明記。自信: 中
- [minor] 7. 操作の門 M は列 B ではほぼ必ず通る。列 A では plug-in の偏りが逆向き（評価の記号の中央値 107 で 26 × 26）。解消: 門を共有 hmm3 の擬似残差の遅れ 1 が列 B で増えるに置き換えるか並べる。列 A の M は Miller–Madow を主に。自信: 中
- [minor] 8. 機械をまたぐ 1e-9 の門が外れたときの道が無い（HP Z2 は Windows、今回は Mac）。解消: 外れたときの道を先に（HP Z2 で回す、または数値の違いと分かる場合の許容と判定）。自信: 中
- [minor] 9. 語は 17 人の中央値の点だけで決まり揺れを見ない。解消: 書き手を 1 人ずつ抜いたときの語の一致の割合を記述として並べる。自信: 中
- [nit] 10. 307 行の指し方が本文と合わない（文は main.tex 331 行）。解消: 節のラベルと英文の逐語。自信: 高
- [nit] 11. 列 B の Q(1) は既知の値で、主の読みの m と端の差はそれに依る。解消: 「主の読みの Q(1) は既知」と 1 文。自信: 高
- [nit] 12. P-MI の ±5% は plug-in の偏りと同じ程度の幅（676 の組で約 0.016 nats）。解消: 真の値を偏りより十分大きく取るか、補正後で照らす。自信: 低

## 4. 総合: major
- 開示の 21 行が事実と違う。R の端は既知で、R は構造の入れ替わりで比べられない。型 1 の判定と文が結果の前から崩れている。
- 列 A・列 B のどちらも情報の量を一定にしていない。
- 割れたとき・欠けたときの型と文が空いている。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: tau-extend conditions.md・kit README・S13 scripts・variants.py の thinned_mask 以外・main.tex 1〜119 行・supplement の S13 前半以外。SHA-256 は照らしていない。
- 注入の疑い: なし。
