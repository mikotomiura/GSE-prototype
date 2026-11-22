# R2 査読 round 4（本人ごとのモデル・個人差の立場）

## 接地
- Fisher 2018 "Researchers should explicitly test for equivalence of processes at the individual and group level"
- Fisher 2018 "the data sampled within an individual in time must be representative of that individual generally (i.e., stationary)"
- Fisher 2018 "all models should be evaluated in terms of how well they represent individual-level processes before making generalizations from aggregate estimates"
- Fisher 2018 "nonergodicity in the natural sciences may also be driven by variation in temporal dependencies across individuals in a sample"
- Adolf & Fried 2019 "Empirical quests into nonergodicity therefore need to incorporate variance sources at both levels."
- Adolf & Fried 2019 "Which and how many sources of heterogeneity will have to be conditioned on, and whether the resulting conditional inferences remain meaningful, will depend on the phenomenon, population, and time span studied"

## 引き継ぎの判定
N1〜N7 すべて解消（draw_D の期待値が C0 なので λ_ρ = 0.831 でも共有の平均はずれない、を synth.py で確かめた）

## 評価表
a 4（「偏差の大きさ」が分散と標準偏差で混ざる・「書き手の水準の回復」は量の性質より強い名前）／b 4（指摘 1・4・2）／c 3（書き手の水準で何が決まるかの読みの規則が無い）／d 3（乱数の配列が D3・D4・D9 に散る）／e 投稿先未定／f 4／g 4（指摘 3・1）

## 新しい指摘
- 1 [major] 書き手ごとの AUC_v は他の書き手の異質性で 0.5 より上がる（分布の筋で植えていない v でも約 (11·0.5 + 5·1)/16 ≈ 0.66）。「書き手の水準の回復」として読めず、植えた/植えていないを分ける AUC も押し上げの分だけ縮む。実データで書き手ごとの AUC_v を並べると少数の異質な書き手が全員を押し上げる。解消: 他の書き手の構成に依らない量（E1 での本人の表の予測の得 p_v^A − S、または書き手ごとの置換の帰無）を並べる。合成で真に対する書き手の水準の量の回復を事前の読みの規則で書く。読まないことに「書き手ごとの AUC_v は他の書き手の異質性で 0.5 より上がり、本人の差の印ではない」。選び・門・止めには触れない。自信 高。
- 2 [minor] この研究の変異の名前 v1・v2・v4・v6 が synth.py の MUT（v1・v2・v4・v6 を使う。v6 は draw_D の濃度を一様にする・synth.py:29・53）と重なる。解消: 別の登録簿か接頭辞つきの名前にし、本計算と各変異の始めに synth.MUT == set() を確かめる。自信 中。
- 3 [minor] 24 時間超過で研究者に問うた後に何を変えてよいか。解消: 変えてよいのは計算の割り振りだけで、複製の数・置換の数・筋・セルは変えない。収まらなければ定義を変えた版。自信 中。
- 4 [minor] 差なしの帰無が単一の要因だけで、量 × 長さの不均一 × ρ = 0 を重ねたときの交換可能性を見ていない。解消: 重ねた差なしを D5 と D6 に足すか、読まないことに書く。自信 中。
- 5 [nit] 「偏差の分散は (1 − ρ)/(1 + ρ) 倍（標準偏差は √ 倍）」と書く。
- 6 [nit] D9 の揺れの筋で 20,000 が 650 で割り切れない（30.8 単位）。単位の数か端の扱いを書く。

## 総合の推奨
minor（直してから凍結）。引き継ぎ 7 件はすべて解消。残る major（指摘 1）は記述の量の定義と読みの規則の直しで、選び・門・止めには触れないので差分の確認で足り再査読は要らない。指摘 1 の解消の条件の 1 と 2 は凍結の前に入れる。

## 読めなかった範囲
SEED、sens の conditions.md・notes.md・pinned.py、ten・nfs の記録、data.py・ml.py・hmm2.py、supplement.tex。論文 3 の数・ml.non_eval・data.split は確かめていない。注入の疑いなし。
