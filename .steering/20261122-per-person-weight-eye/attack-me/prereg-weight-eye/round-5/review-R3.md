# R3 査読 round 5（シミュレーションによる手法評価・並べ替え検定・事前登録の立場）

## 接地
- Morris 2019（2430–2433 行）"write detailed simulation protocols before writing code. This would ideally protect against authors choosing to report favourable results and force one to be clear about 'ADEMP' in advance"／"protocols must justify the rationale for choices: as well as describing what is planned, there is a burden to explain why."
- Morris 2019 表 1 "Choose a value of 𝑛sim that achieves acceptable Monte Carlo SE for key performance measures."／"Include Monte Carlo SE as an estimate of simulation uncertainty."
- Morris 2019（1257–1258 行）"if the test does not control type I error at level 𝛼, power should be interpreted with caution."
- Morris 2019 表 1 "For method comparison studies, make a careful review of the literature to ensure inclusion of relevant methods."
- Morris 2019 表 1 "Set the random number seed once per simulation repetition."／"If running chunks of the simulation in parallel, use separate streams of random numbers"／"Publish code to execute the simulation study including user-written routines."
- Phipson & Smyth（598–599 行）"\"unbiased\" estimators of p-values such as p̂ should not be used, because they can't be guaranteed to control the type I error rate."／（622–623 行）"Permutation assumes that the items being permuted are statistically independent"／（38–39 行）"they make no assumptions other than that the observations are independent and identically distributed under the null hypothesis"

## 引き継ぎの判定
N1〜N8 すべて解消（副次の水準の偽陽性は新しい指摘 5、P-STAT の確率は nit 7、MC SE の端は nit 6 に回す）

## 評価表
a 4（間のセルの基準の検出力が無い）／b 4（第 2 の帰無の再現性と機械間の一致・偶然の止めの合計）／c 4／d 3（同じ但し書きが 3 か所・D4 と D9 の差分で読む）／e 投稿先未定／f 3（遷移表の均一性の検定の系統）／g 4

## 新しい指摘
- 1 [minor] 間を空けたセルの基準（0.069）の検出力が無い。500 複製で ≤ 34 を通る確率は真の率 7% で約 0.47、8% で約 0.18、10% で約 0.01。解消: 通る確率を書き、読まないことに見逃しうる膨らみを添える。自信 高。
- 2 [minor] 正しい実装でも偶然で止まる確率が全体で合計されていない（V1 約 10% とセルの門約 3.5% で約 13〜14%）。D8 に 1 行。自信 中。
- 3 [minor] 第 2 の帰無は母数を公開しないので第三者は再現できないことを書く。Mac と HP Z2 で numpy の版が違えば共通乱数の前提が黙って崩れうる。両機で numpy の版を固定するか、第 1 の帰無の 1 複製を両機で作り単位の列のハッシュが一致する検査を V1 に。自信 中。
- 4 [minor] 比べから外した系統に遷移行列の均一性の検定（尤度比・カイ二乗）が無い。単位の間の過分散で帰無が保たれない見込みという外す理由を D2 に 1 文。自信 低。
- 5 [minor] 副次の水準（p ≤ 0.01・0.001）でも各差なしの拒否率と MC SE を並べ、0.001 では 1,000 複製で偽陽性の水準を確かめられないと添える。自信 中。
- 6 [nit] 合成の段の読みの判定の数（12）と 1 つあたりの誤りの目安（片側約 2.3%）を脚注に。
- 7 [nit] p̂ ∈ {0, 1} のとき MC SE が 0 になる。Clopper–Pearson の区間を添える。
- 8 [nit] P-STAT の種と書き手の対応、比の偶然の振れ幅の見積もり。
- 9 [nit] 門の閾値の正当化は和の上界（7 × 0.0051 ≈ 0.036・55 × 0.00065 ≈ 0.036）で依存の形に依らず言える。「独立なら」を書き換える。

## 総合の推奨
minor（直してから凍結）。round 4 の 8 件はすべて解消。残る 3 つ（間のセルの基準の検出力・偶然の止めの合計・第 2 の帰無の再現性と機械間の一致）は書き足すだけで閉じる。設計そのものは妥当。

## 読めなかった範囲
SEED、sens の conditions.md・notes.md・pinned.py・calibration.json、ten の notes.md、nfs の conditions.md・calibration.json・m0_fit.json、data.py・ml.py・hmm2.py、supplement.tex。experiments 全体を Grep したとき一覧の外のファイルの断片が出た（読み進めず根拠にも使っていない）。注入の疑いなし。
