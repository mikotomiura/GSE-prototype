# review-R1（manuscript round 2・行動の記号列の系列モデルの方法論の立場・対象 9a4c1d34）

## 0. 引き継ぎの判定
M1 解消（112「The two objectives can pick different $\tau$ for the same structure; they do so in the 15-session panel at $k=15$」）。M2 一部（確かめは入ったが見出しの数は他人の選びが 17 人すべてで退けた α=1 の値のまま。両側の当て直しは事後・ar3 と 15-session に限る・感度の検査は当て直していない）。M3 解消（167）・小さな残り N6。M4 未解消（著者の判断・端の軸が 4 つに増えた）。M5 解消（144・233）。CS1 は 2 種。M6 解消。m1 未解消（Table 3 の Only shared refitted の 0 は同点の規則に依存しうる）。m2・m3・m5・n1 解消。m4 既知の未決 6。

## 1. 接地
Pohle「the plug-in estimator is biased due to overfitting: on average, the model fits the given sample better than an average sample.」／「A key assumption of both AIC and BIC is that the true data-generating process can indeed be represented by one of the candidate models considered.」／「Step 3 use model checking methods, in particular residual analyses, but potentially also simulation-based checks」／「in cases where there seems to be no strong reason to prefer one particular model over another (or several other) candidate model(s), results for each of these models should be reported.」。Singer「choosing the model with the highest likelihood is biased towards models with more parameters」「This method requires priors (i.e., fake counts …) – otherwise prediction of unseen states is not possible.」。Monaco「only samples from the 4th session … are used for training and sessions 5-8 … for testing」「Confidence intervals for both the ACC and EER are obtained over users in each dataset」

## 2. 評価表
a 3・b 3・c 3・d 3・e 4・f 4

## 3. 指摘
- [major] N1 合成の検出の規則を実データに当てた結果を書かず、「neither shows」の根拠を要旨で取り違えている。233「No negative-control median reached the real remainder, but the negative controls did not reproduce the real ordering of prior mode and shared model, so the two are not compared」・要旨「planted differences below $10^{-2}$ nats per symbol were not reliably detected, so the remainder neither shows nor rules out per-person differences」・144。実データ（k=5 +5.5e−4・1.00、k=15 +4.1e−4・0.94）は規則の 2 条件を満たすように読める。shows しない根拠は帰無の誤指定で検出率ではない。帰無が実データの平滑の効き方を再現しないなら誤警報率 0/10 も実データに当てはまらず、推奨 (3) が勧めると誤る。解消: 規則を実データに当てた結果を明示し帰属できないと書く。要旨・結論の so を二つに割る。推奨 (3) に帰無の条件。できれば共通そのものから生成する帰無。自信 高
- [major] N2 見出しの「二桁以上」は他人の選びが退けた平滑での値で、好まれた平滑での残りは感度の検査と照らされていない。要旨「the gain at a fixed smoothing of the shared model falls by more than two orders of magnitude, to about $5\times10^{-4}$」・240「picks the lowest multiplier, $\alpha=0.03$, for all 17 writers」・Table 3 Both refitted +5.2e−4〜+6.7e−3。0.188/6.7e−3≈28。返る割合 14〜40% を当てると 5.2e−3 は 1e−2 超の植えた差に当たる。242 の読まない理由は理解できるが非対称が要旨で見えない。hmm3 の 0.19 は α=0.03 で当て直していない。解消: (a) α=0.03 で合成の規則と返る割合を測り直す、(b) α=0.03 での本人 − 最頻値、(c) 要旨・結論で「固定の平滑で二桁以上、他人が選ぶ平滑で両側を当て直すと約一桁半、ただし事後」。最低限 (c)。自信 高
- [major] N3 見出しの数は 4 つの調整の軸（構造・τ・α・β）がすべて端かその近く。292・294。k=12・15 の二分の下 2.5% 点が負。解消: α と τ の格子を 1 段外へ延ばす（事後と明記）か、要旨に「at grid-edge settings」。自信 中
- [minor] N4 「smoothed alike」は言い過ぎ（α は共通のために選び本人へ移しただけ）。4.5 見出し・149・294。Table 3 の注で ar3 内の τ の選びと明記。30-session の非対称の確かめの値を本文に 1 文。自信 中
- [minor] N5 「強い基準」が一次の連鎖で止まる。97・292。本人の二次の連鎖（加える値を他人で選ぶ）を 1 行か、限界に主張に響くと明記。Singer「higher order models are naturally favored by their improvements in likelihoods」。自信 中
- [minor] N6 縮約だけの行（165 の ar1 vs chain・k=15 +0.007）が選び直した連鎖（167 の +0.012）と比べられていない。自信 中
- [minor] N7 10 種の割合に二項の区間（0/10 の上限約 0.31・9/10 の下限約 0.55）。自信 高
- [minor] N8 k=15 で二分の中央値 7.4e−4 が全体 4.1e−4 を上回る理由が無い。二分の側の τ の分布を 1 文。自信 中
- [minor] N9 結論 303 で post hoc の印が落ちている。自信 高
- [nit] N10 要旨が 250 語ちょうどで直す余地が無い。自信 高

## 4. 総合: major
改訂は round 1 の中核に計算で応えた。ただし見出しの数は本稿自身の確かめが退けた平滑と格子の端の上にあり、好まれた平滑での残りは感度の検査と照らされていない。「neither shows」は事前の検出の規則が実データに detected を返すことを書かないまま帰無の誤指定で退け、要旨はそれを検出率から導いている。

## 5. 読めなかった範囲
references.bib・kit README・fig2_p15.csv は読んでいない。接地は grep と部分の読み。注入の疑い: なし。
