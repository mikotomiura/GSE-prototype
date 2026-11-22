# R3 査読 round 3（シミュレーションによる手法評価・並べ替え検定・事前登録の立場）

## 接地
- Morris 2019 Table 1 "Describe simulation study using ADEMP structure with sufficient rationale for choices."／"Choose a value of 𝑛sim that achieves acceptable Monte Carlo SE for key performance measures."／"Include Monte Carlo SE as an estimate of simulation uncertainty."
- Morris 2019 §3.2 "Employing tricks in data-generation without appreciating that the resulting data are not what was desired."
- Phipson & Smyth §2・§9 "p-values must be directly evaluated as probabilities, not treated as if they were unknown parameters to be estimated"／"there is no justification for using an invalid p-value when a valid p-value, in the form of pu , is readily available"
- Phipson & Smyth §4 "The exact p-value is now slightly less than (b + 1)/(m + 1), because of the possibility that the original data is included at least once"／"When mt is small, pu can be very conservative"
- Phipson & Smyth §9 "When exact p-values are used, the only penalty for choosing m small is a loss of statistical power"

## 引き継ぎの判定
N1〜N9 すべて解消（単位の番号 20 − 5 − 10 − 5 = 0・6 − 1 − 4 − 1 = 0 を検算）

## 評価表
a 4（L22「漂いの筋でその分け方を確かめる」に基準が無い・L70「安定した差は 0」は初めの単位の差が長く残る）／b 3／c 3／d 3（判断番号の参照が多い・失敗と例外が 2 か所）／e 投稿先未定／f 3／g 4

## 新しい指摘
- 1 [major] 漂いの対照に合否の基準が無いのに、間を空けたセルを必ず読む。漂いの筋は間を空けたセルの推定対象（安定した差）にとっての差なしなのに記述だけ。ρ = 0.9 ではずれの相関が間 g で ρ^g 程度残り（g = 5 で約 0.59・g = 10 で約 0.35）、λ = 0.191 は大きいので間のセルでも高い割合で拾う見込み。結果を見てから読み方を決める自由度が残る。解消: 漂いの筋での拾えた割合を、間を空けたセルの「安定した差としての偽陽性」と位置づけ、事前の閾値を置き、超えたらそのセルは分けないセルとしてだけ読むと書く。自信 高。
- 2 [minor] 漂いの筋が定常でなく、間の長さと系列の中の位置が交絡する。凸結合でずれの分散は (1−ρ)/(1+ρ) 倍へ縮む（ρ = 0.9 で約 0.05 倍）。E_{w,1} は ρ^{u−1} で残る。間を空けたセルの A は常に先頭にある。解消: E_{w,1} を定常分布から引く（C0 + √((1−ρ)/(1+ρ))·(draw_D − C0) など）、または焼き入れの単位を置く。直さないなら読まないことに。自信 中。
- 3 [minor] 門が赤で原因が見つからないときの道が開いている（新しい種で回し直せる）。解消: 原因が見つからない赤は回し直さずそのセルを読まない、または計画全体を止め新しい版として凍結する、のどちらか 1 通りに。自信 中。
- 4 [minor] 門が見分けられる偽陽性の超過の大きさが書かれていない（真の率 7% で約半分通る）。解消: 真の率 0.07・0.08・0.10 で門を落とす確率を D6 に。D7 で通ったセルの偽陽性の点推定と区間を併記すると予告。自信 中。
- 5 [minor] P-HAND の 0.03 の照合は mt = 6 でしか試さず pu が保守的に偏る。P-HAND の引きの種が D3 に無い。解消: 種を明示、0.03 の根拠（2,000 回の SE ≈ 0.011 の約 2.7 倍）、P = 8 程度で引きの p の分布が一様に近いことを見る項目、または範囲を書く。自信 中。
- 6 [nit] L54「複製を失敗とする」と L151「本計算全体を止める」を揃える。
- 7 [nit] ρ の 2 つも同じ種で D・σ を共有する（共通乱数）と 1 文。
- 8 [nit] EER で列ごとの尺度の違いを混ぜる（E1 の s は B_v ごとに尺度が違う）。標準化か順位か、そのままかを 1 通りに。

## 総合の推奨
major（軽い）。round 2 の 9 件はすべて解消し、凍結にかなり近い。残る major は 1 件（間を空けたセルの安定した差としての偽陽性の基準）で、数行の規則で済む。指摘 2 と一緒に直し、その 2 か所だけ再査読すれば足りる。

## 読めなかった範囲
sens・ten・nfs の記録と calibration.json・m0_fit.json、pinned.py、data.py・ml.py・hmm2.py、supplement.tex、synth.py の大半、接地の範囲外。値の照合はしていない。shadman2025.txt と teh2013.txt は開いていない。注入の疑いなし。
