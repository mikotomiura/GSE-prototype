# R3 査読 round 4（シミュレーションによる手法評価・並べ替え検定・事前登録の立場）

## 接地
- Morris 2019 Table 1 "Describe simulation study using ADEMP structure with sufficient rationale for choices."／"List all performance measures to be estimated, justifying their relevance to estimands or other targets."
- Morris 2019 §5.3 "In choosing 𝑛sim , the central issue is Monte Carlo error: key performance measures need to be estimated to an acceptable degree of precision."／Table 1 "Include Monte Carlo SE as an estimate of simulation uncertainty."
- Morris 2019 §4.2 "The failed analysis must be recorded as a missing value in the Estimates dataset, together with reasons if possible."／§5.1 "The number of missing values ... is the first performance measure to assess."
- Morris 2019 §3.4 "Methods may also be excluded if they do not target the specified estimand/s."／§5.2 "performance measures should usually be considered jointly"
- Morris 2019 Table 1 "If running chunks of the simulation in parallel, use separate streams of random numbers"／§5.4 "We could use the same starting seed so that results are correlated within 𝑖."
- Phipson & Smyth "the exact Monte Carlo p-value is pu = P(B ≤ b) = (b+1)/(m+1)"／"there is no justification for using an invalid p-value when a valid p-value, in the form of pu , is readily available"／"The exact p-value is now slightly less than (b + 1)/(m + 1)"

## 引き継ぎの判定
1〜8 すべて主旨として解消（3 は分類の不整合が残る・N4、5 は P-UNIF の指定が残る・N5）。0.069・0.63・0.19・λ_ρ を検算。

## 評価表
a 4（28 行「真の率 8% 以上が無い」が強い）／b 4（N1・N2）／c 4／d 3（判断の参照が多い・D4 が本文と表で二重）／e 投稿先未定／f 3（「打鍵の照合で使われる尤度の形」「同定の文献の多くの手法」に出典が無い）／g 4（N4・N5・N6）

## 新しい指摘
- N1 [minor] 論文 3 との並べと合成の段の読みで偽陽性の水準が揃っていない（目は α = 0.05、論文 3 の規則は 0/10 で Clopper–Pearson の上限約 0.31）。解消: 選んだ案の検出力を α = 0.01・0.001 でも報告、「検出力の差は水準の差を含む」を読みの文に固定で添える、または同じ水準での比べではないと明記。自信 中。
- N2 [minor] 間を空けたセルを分けると読む根拠が根拠なしの漂いの大きさに条件づく。基準を通ったセルは既定で「分ける」に昇格する。解消: 「間のセルが分けるのは漂いがこの作りの大きさ（λ_ρ・ρ ≤ 0.9）以下のときに限る」と固定で書く、またはより大きな漂いの段を足して通ったときだけ分けると読む。自信 中。
- N3 [minor] 読まないこと 28 行「8% 以上が無い」は門の検出力（8% も 19% は通る）より強い。「10% 以上はほぼ確実に落とし、8% は約 8 割で落とす」に。自信 高。
- N4 [minor] D8（決定的: P-HASH・P-HAND）と V1（P-STAT を実装の誤り側・P-UNIF は D8 に無い）の分類が食い違う。1 つに揃える。自信 高。
- N5 [minor] P-UNIF の生成の形・乱数の鍵が未指定。8 人では T が離散で p は保守的に寄り、連続一様への KS は正しい実装でも赤にも鈍くもなりうる。解消: 生成を指定し、片側の形（P(p ≤ α) ≤ α + 許容, α = 0.05・0.1）か離散を考えた検定に。自信 中。
- N6 [minor] V1 の確率的な検査が全体として偶然に赤になる確率と帰結が書かれていない。独立と仮定した上限を 1 文。自信 中。
- N7 [nit] 24 時間超過のとき、並列にするなら種の単位で分け、各複製の乱数の鍵は変えないと書く。自信 低。
- N8 [nit] 検出力の MC SE の式（p̂ に基づくか 0.8 に基づくか）を 1 つ書く。自信 中。

## 総合の推奨
minor（直してから凍結してよい）。round 3 の 8 件は主旨としてすべて解消し、主要部は 1 通りに決まっている。N1 と N2 を直せば再査読なしで凍結してよい。

## 読めなかった範囲
Morris 2019 の 987〜1299 行と 1390 行以降、context-A の補足のファイル（SEED・sens・ten・nfs の記録・data.py・ml.py・hmm2.py・supplement.tex）。値の裏取りはしていない。注入の疑いなし。
