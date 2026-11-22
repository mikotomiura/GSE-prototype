# R2 査読 round 5（本人ごとのモデル・個人差の立場）

## 接地
- Fisher 2018 "all models should be evaluated in terms of how well they represent individual-level processes before making generalizations from aggregate estimates."
- Fisher 2018 "we should not think of a correlation in group data as an estimate that generalizes to any given individual in the population."
- Fisher 2018 "Researchers should explicitly test for equivalence of processes at the individual and group level"／"both the within- and between-subject variation should be explicitly modeled in any approach"
- Adolf & Fried 2019 "instability over time can also produce ambiguous effects and promote interpretational fallacies ... Empirical quests into nonergodicity therefore need to incorporate variance sources at both levels."
- Adolf & Fried 2019 "recent work on ergodicity vs. nonergodicity has shifted away from a binary conceptualization to the idea of a continuum"／"statistical approaches such as structural equation or state-space modeling allow one to estimate conditional ergodicity by taking into account (un) observed sources of heterogeneity"
- Fisher 2018 "statistical estimates of repeated-measures data can be biased due to temporal dependence"

## 引き継ぎの判定
1〜6 すべて解消（synth.py:29 の MUT、λ_ρ の検算、650 × 30 + 500 = 20,000 を確かめた）

## 評価表
a 4（題と目が出す集団の量の隔たり・N1）／b 4（N2）／c 3（書き手の水準の推奨が予測の得に戻り、規則が無い）／d 3（同じ限定が 2〜3 か所に繰り返し・D5 の 5 の置き場所）／e 投稿先未定／f 3（分散成分・階層の縮めとの比較が無い）／g 4（N1・N5）

## 新しい指摘
- N1 [major] 書き手の水準の量（E1 の予測の得）に事前の判定の規則も帰無の較正も無い。予測の得は論文 3 の予測の点数と同じ型の量。後から足す較正は D8 で探索になり、実データの読みを損なう。解消: (a) 書き手の水準の規則を 1 つ事前に書き（予測の得の符号、または差なしの報告の組の書き手ごとの分布の 95% 点）、差なしの 7 筋での書き手ごとの偽陽性と分布の筋の 5 人の感度を報告する、または (b) 書き手の水準の判定を確認の対象にしないと D7 に明記し題と問いも合わせる。自信 高。
- N2 [minor] 安定した差と漂いの混合の筋が無く、実データの g の並びを読む比較の相手が欠ける。振幅が ρ ごとに 1 つで傾きの違いを分けられない。解消: 用量の安定した差に漂い（ρ = 0.9）を重ねた筋を報告の組に 1 つ足す、または「実データの g の並びは安定した差の有無の判定に使わない（記述だけ）」と D7 に。自信 中。
- N3 [minor] 正しい実装でも偶然の赤だけで研究全体が止まる確率が合わせて約 16%（1 − 0.9 × 0.965 × 0.965）で、その合計と止めた場合の報告の文言が書かれていない。自信 中。
- N4 [minor] 異質性の大きさを推定する系統（分散成分・階層の縮め・経験ベイズの濃度の推定）との比較が位置づけに無い。D2 に外した理由か名指しを 1〜2 文。自信 中。
- N5 [minor] D5 の 5 の揺れの筋の比べは、揺れの 1e-2・3e-2 が報告の組にしか無いので選びの組では計算できない。D6 の報告する量へ移し組とセルを明記。自信 高。
- N6 [nit] 二項の超過確率の算法（正確な上側確率 P(X ≥ 69) など）を 1 句添える。自信 低。

## 総合の推奨
minor（直してから凍結）。round 4 の 6 件はすべて解消。重い穴は N1 の 1 つで、文の追記で消える。N2〜N5 も凍結の前に直せば再査読は要らない。

## 読めなかった範囲
SEED、sens の conditions.md・notes.md・pinned.py、nfs の conditions.md・calibration.json・m0_fit.json、hmm2.py、supplement.tex。synth.py・data.py・ml.py・ten と nfs の notes.md は一部だけ。ハッシュは確かめていない。注入の疑いなし。
