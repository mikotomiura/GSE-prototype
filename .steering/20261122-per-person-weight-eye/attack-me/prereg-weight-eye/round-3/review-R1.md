# R1 査読 round 3（打鍵の生体認証の立場）

## 接地
- Teh 2013 "Adaptability implies the ability of a system to accommodate gradual typing changes of user across time."／§4.6 "variability of typing is expected appear across different sittings [ 95 ]. Therefore, several sessions of data collection would ideally leverage one's typing evolution."／"If keystroke template remains unaccustomed to the gradually shift of typing pattern over time, system accuracy will be degraded over time."
- Shadman 2025 "it is assumed that the keystroke samples in the instance of enrollment and verification have an equal distribution, which is not usually the case"
- Teh 2013 §4.5 "The greater amount of samples used in constructing reference template, the closer it resembles one's typing model [ 93 ] and recognition rate may also be potentially better"／Shadman 2025 "differing amounts of samples needed to develop the model, individual or global threshold, the database size"
- Shadman 2025 "Using an individual threshold was better than using a global threshold for computing the EER because an individual threshold is a value specific to a user"／Teh 2013 "Equal Error Rate (EER) is used to determine the overall accuracy as well as a comparative measurement against other systems."
- Teh 2013 §4.4 "An alternative that may resolve this issue is by partitioning user sample data into two subsets. The first subset is used as training while the remaining as testing sample [ 41 ]. ... this method is only applicable if every subject's input is identical."

## 引き継ぎの判定
N1〜N5 解消（間を空けたセルの単位の番号・ml.py:75 を確かめた）／N2 は採用した範囲で解消（揺れの段 0 は長さの帰無で、揺れの帰無ではない）／N6 一部（EER の閾値の取り方が未定・E1 の列の尺度が混ざる）

## 評価表
a 4（70 行目「安定した差は 0」が作りの上で成り立たない）／b 3／c 4／d 3（判断番号の参照・D4 と D6 の表を照らさないと分からない）／e 投稿先未定／f 3（個人ごとの閾値の EER が無い・template ageing との対応）／g 4

## 新しい指摘
- 1 [major] 漂いの筋の初期値が定常でなく「安定した差は 0」が成り立たない。E_{w,1} は全単位に ρ^{u−1} で残る書き手固有の成分で、ρ = 0.9 では B（単位 16〜20）にも約 0.15〜0.21 の重み。分散は定常値 (1 − ρ)/(1 + ρ)·V（ρ = 0.9 で約 0.05 V、0.5 で約 0.33 V）に近づき、g = 10 の A は約 0.46 V 以上、B は定常に近い。λ = 0.191 は安定した D で較正した値で、ρ の間の比べに漂いの大きさの違いが混ざる。間を空けたセルを読む条件が合成の結果でどう制約されるかも未定。解消: E_{w,1} を定常から（焼き入れか、平均 C0 のまわりの偏差を √(1 − ρ²) で保つ形）、漂いの筋の g1 を D9 で、「漂いだけの筋で間を空けたセルの拾えた割合が X を超えたら実データの間のセルを安定した差として読まない」を事前に。ρ = 0（単位ごとに独立な揺れだけ）を間のセルの門に足すのが最も単純。自信 高。
- 2 [minor] 交換可能性の門（構造・揺れの段 0・量）が選びに入らず、選んだ案が D6 で赤になると報告の組を見た後に分かれ道。解消: これらの差なしに選びの組を足して D5 の許しに加える、または次の版の案の選び方を事前に 1 文。自信 中。
- 3 [minor] CS1 のセルは第 1 の用量の差なししか門が無い。CS1 は単位が 6 つで量の差の効きが大きい可能性。解消: 量（と揺れの段 0）を CS1 でも作り門に入れる、または読まないことと D7 に明記。自信 中。
- 4 [minor] EER の閾値の取り方（全体で 1 つか書き手ごとか）が未定で E1 では列の尺度が混ざる。主要の T は書き手ごとの閾値に相当。解消: 両方出すか 1 つに決めて明記。自信 高。
- 5 [minor] 門 71/1000 が見逃す膨らみ（真の率 7% で約半分・8% で約 16% 通る）を書く、または報告で偽陽性の点推定と区間を読みに使うと書く。自信 高。
- 6 [nit] 門の表の「揺れの段 0」は「長さの不均一（揺れの筋の段 0）」と書く。

## 総合の推奨
minor（直してから凍結）。引き継ぎ 6 件に手当てがあり、主要指標・選び・止め・再開は 1 通り。残る実質の穴は新 1 だけで、直し方が局所的。新 1 の直しで生成が変わるので、その部分の式だけは凍結の前に確かめてほしい。

## 読めなかった範囲
SEED、sens・ten・nfs の記録と calibration.json・m0_fit.json、pinned.py、hmm2.py、supplement.tex、接地の上に挙げた以外の部分。ハッシュ・λ・S10 の数は照合していない。注入の疑いなし。
