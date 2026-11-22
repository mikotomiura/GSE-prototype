# R1 査読 round 4（打鍵の生体認証の立場）

## 接地
- Teh 2013 §4.6 "keystroke dynamics are to behavioral biometrics where variability of typing is expected appear across different sittings [ 95 ]. Therefore, several sessions of data collection would ideally leverage one's typing evolution."／Shadman 2025 §3.1 "There was at least a one-day gap between successive sessions to reflect the temporal variation in typing of the subjects."
- Teh 2013 §4.6 "the greater number of samples collected the more accurate and conclusive a test result can be from statistical point of view."／Shadman 2025 "number of subjects that participated in the data collection, and the average number of keystrokes per subject."
- Teh 2013 §2.5 "Equal Error Rate (EER) is used to determine the overall accuracy as well as a comparative measurement against other systems."
- Shadman 2025 §3.3 "Using an individual threshold was better than using a global threshold for computing the EER"
- Shadman 2025 §2.4.4 "FAR, FRR, ROC, and AUC may not be sufficient, as they fail to illustrate the average keystroke count required"
- Shadman 2025 §3.2 "1) Statistical algorithm, 2) Distance-based algorithm, 3) Rhythm-based algorithm, and 4) Machine learning based algorithm."

## 引き継ぎの判定
1〜4・6 解消（λ_ρ ≈ 0.832・0.0695 を検算）／5 一部（読まないこと l.28 の門の検出力の文が D5 の 67/1000 と合わない・「8% 以上が無い」が強い）

## 評価表
a 4／b 4（合成は単位 1 つ = 1 歩で、実データのセッション間の時間は不均一・振幅を揃えたのは線形の空間だけ）／c 3／d 3（門の検出力の説明が読まないことと D6 に分かれ二重）／e 投稿先未定／f 3（学習の要らない距離を外す理由が無い）／g 4

## 新しい指摘
- 1 [minor] 門の検出力の文が D5 と D6 をまとめていて D5 の数と合わない。D5 の 67/1000 では 7% が通る確率は約 0.38、8% は約 0.07。D6 の 72/1000 は 8% を 19% で通すので「8% 以上が無い」とは言えない。解消: D5 と D6 で 7%・8%・10% の通る確率を別々に書き、「無い」を「この確率で落とす」に。自信 高。
- 2 [minor] 間を空けたセルが分けると言えるのは ρ ≤ 0.9 で単位の間隔が均一な場合に限られる。実データの単位の間の時間は一様でない。解消: 読まないことに明記し、D7 の追記で実データの g = 0・5・10 の並びを合成の ρ ごとの並びと比べて読むと予告。自信 中。
- 3 [minor] 漂いの振幅を揃えたのは線形の空間の偏差だけで、対数尤度の差は揃っていない（λ_ρ = 0.831 で C0 の重みは 0.17）。ρ の間の比べは ρ と振幅の違いを区別できない。解消: 明記し、D6 の漂いの並べに D9 の ρ ごとの g1 を必ず添える。自信 中。
- 4 [minor] 学習の要らない距離（打鍵の照合で標準の系統）を外す理由が無い（D2 l.51 は学習の自由度だけ）。解消: E3 だけを代表とする理由を 1 文、または位置づけの限界として。自信 中。
- 5 [nit] D4「偏差の大きさは (1 − ρ)/(1 + ρ) 倍」は分散の比。標準偏差はその平方根と書く。自信 高。
- 6 [nit] 「全体で 1 つの閾値の EER」は列ごとに順位に変えた後の値で、文献の global とは意味が違う。呼び名を変えるか、他の論文の EER と直接比べないと 1 文。自信 中。
- 7 [nit] 足した筋の乱数の鍵に形が無く CoAuthor と CS1 が同じ流れ。共有の意図を書くか形を入れる。引く順はコードで固定し code_hash に含むと書く。自信 中。

## 総合の推奨
minor（直してから凍結してよい）。round 3 の 6 件のうち 5 件が解消。新しい穴は読みの限界と言い方の直しで消え、手続きの固定は崩れていない。凍結の前に直すべきは、門の検出力の文（D5 と D6 を分ける）と、間のセルが分けられる範囲の明記の 2 点。

## 読めなかった範囲
接地の上に挙げた範囲の外、context-A の補足のファイル（SEED・sens・ten・nfs の記録・synth.py・pinned.py・data.py・ml.py・hmm2.py・supplement.tex）。値の照合はしていない。注入の疑いなし。
