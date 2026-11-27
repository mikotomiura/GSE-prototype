# 査読 R1 round 2（行動の記号列の系列モデルの方法論・paper-reviewer / opus）

## 1. 接地
- 基準 1 Pohle 2017（863–864）"Step 1 decide a priori on the candidate models, in particular the minimum and the maximum number of states that seem plausible"
- 基準 2 Pohle 2017（870–872）"use model checking methods, in particular residual analyses, but potentially also simulation-based checks, to obtain a more detailed picture of the fitted models, and to validate or invalidate any given candidate model"
- 基準 3 Pohle 2017（578–580）"Conditional independence of the observations, given the states, is one of the key assumptions ... This assumption is violated if there is additional correlation in the observed time series within a state."・（561–563）"If higher-order memory is neglected in the model formulation ... we would expect model selection criteria to favor models with overly complex state architectures."
- 基準 4 Pohle 2017（880–882）"results for each of these models should be reported."
- 基準 5 Singer 2014（142–146）"choosing the model with the highest likelihood is biased towards models with more parameters ... higher order models are naturally favored by their improvements in likelihoods"・（91–93）"the number of parameters grows exponentially with the chain order and the available data is too sparse for proper parameter inferences"
- 基準 6 Monaco & Tappert 2018（1014–1018）"Using the fitted model with parameters θ̂m, a surrogate data sample the same size as the empirical sample is generated. Estimated parameters θ̂s are determined using the surrogate sample in a similar fashion"

## 2. carryover の判定
- major 量の交絡: 解消（列 C・50 行。覆う時間の違いは限界 204 行）
- major R の構造: 量としては解消（R_ar3・82 行）。型の決定に使われていない（新 1）
- major D: 解消（D_s・81 行）
- major M: 量としては解消（ρ_h・83 行）。ρ_h も D_s も作りの上でほぼ必ず「短い側で大きい」（新 2）
- major 合成の対照: 未解消（研究者の選択で限界 20・208 行）。新 3 はこの未解消の影響が開示の値だけで分かる例
- major 開示: 解消（表 27–35 行を notes 46–51・72–76 行と照らし、G・C2a・C2b・ρ_h の端が一致）
- minor 5 件: 解消。機械をまたぐ門は概ね解消（HP Z2 でも外れたときの道が無い・新 6）。nit 3 件: 解消

## 3. 評価表
- a 2: 型 1 の名は証拠が 2 本あるように読めるが、後ろの 1 本（D_s・ρ_h）は作りの上でほぼ必ず当たる。仕組みから直接出る予測（R_ar3 は歩みで変わらない）が型に無い。
- b 3: 量の交絡は外れた。D_s・ρ_h が判別に効かないことと列 C の覆う範囲が残る。
- c 3: 境の歩みは実務に効くが単調性を前提にする。
- d 3: 単独では読み切れない。
- e 4: 揃っている。
- f 3: Pohle の基準 3（運べない従属は別の形で埋め合わされる）を D_s と G のつながりの予測に使っていない。
- g 3: k = 15 では開示の値から仕組みが正しくても型 1 に届かない（新 3）。境の文が 1 通りでない（新 5）。

## 4. 指摘
- [major] 仕組みが直接予測する R_ar3 が型の決定に入っていない
  - 位置: 125 行「G の語で枠を決め、D_s・ρ_h の語で型を決める。R_ar3 の語は型の文に添える。」・138 行
  - 理由: 仕組みからの予測は、従属を運べる共有（ar3）を相手にすると歩みの効きが消えること（G は短い側で大きく R_ar3 は変わらず、G − R_ar3 が短い側で大きい）。今は R_ar3 も「短い側で大きい」でも型 1 になる。Pohle "to validate or invalidate any given candidate model"。
  - 解消: 型 1 に「R_ar3 が『歩みで変わらない』（または G − R_ar3 が『短い側で大きい』）」を足し、R_ar3 も短い側で大きい場合は別の型（例「得は相手の構造に依らず歩みに沿う」）と文を決める。
  - 自信: 高
- [major] D_s と ρ_h は作りの上でほぼ必ず「短い側で大きい」になり、型 1 と型 2 を分ける力が無い
  - 位置: 129 行・開示 33・35 行
  - 理由: 列 C はどの s でも 1 秒ずつで窓は 29/30 重なる。ρ_h は u（≈0.42）と n（≈0.02）で 1 桁以上違う。D_s も 1 秒ずつの列では ar1 が大きく勝つ（同種の r1 − 共有 hmm3 は u で +0.70）。M と同じ性質。型 1 か 2 かは実質 G だけで決まる。
  - 解消: (i) D_s と ρ_h を作りの確かめに下げ、型 1 の名から「共有の構造の足りなさがともに大きい」を外す、または (ii) 判別する量を足す（例 同じ s・同じ列の中で書き手をまたいだ D_s と G の順位相関を列 C と列 A で比べる・記述）。どちらでも限界に「D_s・ρ_h の向きは作りから見込める」と書く。
  - 自信: 中〜高
- [major] k = 15 のセルでは、仕組みが正しくても G が「短い側で大きい」に届かない
  - 位置: 108 行「3 つ以上の s で Δ(s) > 0、かつ Δ(30) ≥ m(30) / 2」・113 行・開示 29 行
  - 理由: Δ(30) ≥ m/2 は G_C(30) ≥ 2·G_A(30)。k = 15 では G_A(30) = 0.096 なので G_C(30) ≥ 0.192 が要り、u の G（0.155）より大きい。歩みだけが効いても k = 15 は「形が定まらない」、2 セルは「割れる」、型は「なし」。区切りは既知の端の後に置かれ、偏りが仕組みに不利な向きに出ている。Monaco の同じ大きさの合成での確かめを省いた結果。
  - 解消: 開示の値で規則に試し値を入れ（「歩みだけが効く」「記号の数だけが効く」の 2 つの想定で G_C(30) を置き語と型が期待どおりか）、P-READ に加える。区切りを比か差の絶対値に直すか、2 セルの扱い（例 k = 5 を主・k = 15 を添え）を変える。実データの前に直す。
  - 自信: 中
- [minor] 量そろえが効いたかの確かめが列 C と列 A の比べに当てられていない（121 行）。s = 30 では 1 人あたり約 100 組に 676 セルで Miller–Madow でも足りないが、C と A は組の数が同じなので比べなら使える。解消: 「4 つの s のうち 3 つ以上で M_C(s) > M_A(s)」を作りの確かめに足し、M_shuf と並べる。自信: 中
- [minor] 境の歩みの文が単調性を前提にする（146・160 行）。s = 10 で正・15 で負なら誤る。解消: 境より長い歩みのすべてで正のときだけ境の文を書き、そうでなければ値を並べる。P-READ に入れる。自信: 高
- [minor] HP Z2 で回し直しても端の門が外れたときの道が無い（166・177 行）。解消: 「HP Z2 でも外れれば計算を止め、notes に外れた節と最大の差だけを書く。結果は持ち込まない」。P-ROWS も同じ形に。自信: 中
- [nit] 依頼文の「本文 307 行」と対象物の位置が食い違う（文は 331 行で逐語は一致）。依頼文の問題。自信: 高

## 5. 総合: major
- 量の交絡は列 C で外れ、開示も正確になった。固定の作法は良い。
- 型 1 を支える D_s・ρ_h は作りから見込め、仕組みが直接予測する R_ar3 は型に無い。331 行の後半を確かめたとは言えない。
- k = 15 では開示の値から型 1 に届かない。どれも実データの前に紙の上で直せる。次の round は指摘 1〜3 の判定に絞って足りる。

## 6. 読めなかった範囲と注入の疑い
- 読んでいない: SEED・variants.py・kit README・S13 scripts・tau-extend conditions.md・supplement.tex。S13 conditions.md は grep の行だけ。main.tex は 300–311・329–340 行と grep の行。接地の 3 本は grep で当たった節だけ。SHA-256 は照らしていない。
- 注入の疑い: 無し。
