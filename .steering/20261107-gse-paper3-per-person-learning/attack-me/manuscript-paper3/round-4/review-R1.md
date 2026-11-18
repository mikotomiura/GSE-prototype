# review-R1（manuscript round 4・系列モデルの方法論・対象 d6587f21）

読んだ: brief-R1.md・context-A.md・carryover-R1.md・monaco/pohle/singer（grep と前後）・main.tex 全文・fig2_p15_hmm3/ar3/joint.csv。読まない: references.bib・fig2_p15_ar1.csv・fig2_p15.csv・kit/symbols/README.md。

## 0. 引き継ぎの判定
- M1 解消: 要旨「this value does not show a per-person difference」「leaves up to $7\times10^{-3}$, not checked against synthetic writers」・序論 49「the second was not checked against synthetic writers」・考察 315「at the lighter smoothing it was not compared with synthetic writers」。
- M2 一部: 4.5 見出し「of similar size relative to their smoothing gain」・比「about 0.6 to 1.0 in these synthetic writers and 0.55 to 0.97 in the real panel」・限界「we read the remainders relative to the smoothing gain, not their raw sizes」。比が差を植えた書き手でどう振る舞うかが無い（N2）。
- M3 解消: 280「At $\tau=10^6$ the per-person \arthree{} fit loses to it in the median at every $k$ ($-3.5\times10^{-4}$ to $-1.2\times10^{-4}$; 18 to 35\% ...)」。含意は未記（N3）。
- m1 解消: 313「the remainder ... against a stronger shared model at the fixed base smoothing is more than two orders of magnitude below」。連鎖は 315。
- m2 解消: 317–322 で「two practices were used here」と「Two further practices are needed ... but were not met here」。(2) の used here に新しい問題（N1・N5）。
- m3 解消: 335「It puts no differences between writers and no drift between a writer's sessions into the null; drift would lower the real remainder.」（文言は N9）。
- m4 解消: 334「information criteria and cross-validated likelihood alike tend to favour more states \citep{Pohle2017}」。
- n1 解消: 278「$3.4\times10^{-3}$ to $6.7\times10^{-3}$ at $k\ge5$ ... Its largest value is at $k=12$, where the other columns are unstable, and a lighter smoothing outside the grid may give more.」要旨・序論の up to 7e-3 に断りなし（N10）。
- n2 未解消（著者が採らなかった・重く数えない）。
- n3 解消: 189「(a value that does not depend on $k$)」。

## 1. 接地
1. Singer 2014: "Using the log-likelihoods of the specific order models is not enough, as we will always get a better fit to our training data using higher order Markov chains. The reason for this is that lower order models are nested within higher order models." / "we produced a random navigational dataset by randomly (uniformly) picking a next click state ... the higher the order the higher the corresponding log likelihoods are."
2. Singer 2014: "methods are necessary that balance the goodness-of-fit against the number of model parameters."
3. Pohle 2017: "traditional model selection criteria, and especially the AIC, often lead to the selection of much larger numbers of states than expected a priori" / "it is probably not possible to design a one-size-fits-all formal selection method ... we suggest a more pragmatic approach ... which takes into account formal criteria for guidance, but also stresses the importance of the study aim, expert knowledge and model checking procedures."
4. Pohle 2017: "real data often exhibit further structure, such as outliers, seasonality or heterogeneity between individuals. When neglecting these features in the formulation of an HMM, then additional states may be able to capture this ignored data structure"
5. Monaco 2018: "the dependency on event types introduces many more parameters ... Therefore, we address the problem of parameter smoothing, which acts as a kind of regularization and avoids overfitting" / "consistently outperform other leading anomaly detectors, including the standard HMM ... and is generally preferred over the HMM in a Monte Carlo goodness of fit test."

## 2. 評価表
- a 3: 書き分けは良い。結論の decision は固定の平滑の解析から出ており、推奨 (2) の手順に拠っていない（N1）。
- b 3: 2 つ目の帰無で 3e-2 が検出されない原因（閾か強い縮みか）を区別できない（N2）。重ならない窓との比べでデータ量が交絡（N6）。
- c 3: 「比べの相手しだいで利得は桁で変わる」「平滑は両側に」は持ち帰れる。推奨した手順の検出力は示されていない。
- d 3: 4.4 → 4.5 と Figure 1 は良い。要旨に限定の句が積み重なる。smoothing gain が要旨で未定義。
- e 4: 要旨 250・キーワード 6・Statements。Code availability は既知の未決。
- f 4: 系列モデルの平滑の先行は薄いまま（n2）。

## 3. 指摘
- [major] N1 結論の decision が推奨 (2) を満たさない解析から出ている
  - 位置と引用: 結論 345「the protocol that chooses structure and shrinkage on other people returned a decision rather than an estimate: in the CoAuthor 15-session panel a fit that gives each writer's own data at most 3\% of the weight ... A designer can follow that decision and save the cost of per-person models」・推奨 319「(2) choose structure, shrinkage and smoothing on other people ... and apply the chosen smoothing to the per-person fit and the shared model alike.」・4.4 278「every writer is given a finite $\tau$ inside the grid」
  - なぜ問題か: 推奨どおりの手順では有限の τ と 3.4e-3〜6.7e-3 の残り。結論と考察 311 の decision は固定の平滑（τ = 10^6・重み 0.06〜3%）だけから。要旨の「more than two orders of magnitude below that gain」も固定の平滑だけで、両側では 0.19/7e-3 ≈ 27 倍。「save the cost」は per-person の fit を選んだ決定と合わない（保存と cold start は消えない）。接地 Pohle「stresses the importance of the study aim ... and model checking procedures」。
  - 解消の条件: decision を「固定の平滑の下での決定」と明記し、推奨 (2) の場合の決定（α = 0.03 の τ と重み）を 1 文並べる。または (2) を「主解析では満たしていない」側へ。「save the cost」を CS1 と CoAuthor で分けて書く。
  - 自信: 高
- [major] N2 2 つ目の帰無で、植えた差の下での残りが本文に無く、検出の失敗の原因が読めない
  - 位置と引用: 4.5 306「No planted level up to $3\times10^{-2}$ was reliably detected (at most 3 of 10 seeds), so the protocol also cannot rule out differences of that size. Because the null's smoothing gain is too large, its threshold may be too high and its detection rates too low.」
  - なぜ問題か: 閾 1.8e-3 で 3e-2 が検出されないなら植えた差の 6% 未満しか戻っていない。(i) 閾が高すぎる、(ii) 他人で選んだ τ = 10^6 が書き手の差を構造的に消す、のどちらか本文から決められない。(ii) なら推奨 (1)(2) の手順に強い縮みの下での検出力が無い。比が帰無と差のある場合を分けられるかも不明。接地 Singer の人工データの対照。
  - 解消の条件: 植えた水準ごとの残りの中央値・選ばれた τ の分布・比を 1 行ずつ示し、(i)(ii) のどちらかを 1 文。
  - 自信: 中（保存済みの値で答えられるかは確かめていない）
- [minor] N3 最頻値との比べから直接言えることを書いていない: 280 の値は、固定の平滑で選ばれた重みでは書き手のデータを加えると 65〜82% の書き手で悪くなるという意味。本文は「shows the same dependence on smoothing directly」だけ。解消: 「固定の平滑の下では書き手のデータを加えた分は中央値で負で、残りは平滑から来る」を 1 文、確率 0 の書き手 2 人を per-person の勝ちに数えたことに触れる。自信 中
- [minor] N4 考察で post hoc の印の位置が取り違えられている: 315「Post hoc, lightening the smoothing of the shared model alone made the remainder vanish, whereas applying it to both models did not」と 178「the symmetric refit ... added after seeing the result of the asymmetric one」。共通の側だけの版は事前の解析。解消:「Lightening ... alone made the remainder vanish; applying it to both models (post hoc) did not」。自信 高
- [minor] N5 推奨 (2) を used here と書くのは言い過ぎ: 317「two practices were used here and changed the reading」・336「The symmetric refit was restricted to the \arthree{} in the 15-session panel」・276「picks the lowest multiplier, $\alpha=0.03$, for all 17 writers」。解消: 「partly used (post hoc, one structure and panel)」、端なら格子を広げると (2) に添える。自信 中
- [minor] N6 記号化の比べでデータの量が交絡: 202「with non-overlapping windows, which give about one-thirtieth of the symbols ... the joint choice picks the \hmmthree{}」・345「The decision depends on the symbolization」。パラメータ 2,033 の 3-state AR-HMM は 1/30 の記号で不利（Singer「balance the goodness-of-fit against the number of model parameters」）。+0.043〜+0.096 を gain と呼ぶのは 176 の定義と合わない。解消: 「the symbolization and the resulting number of symbols」、どちらの目的で選んだ τ かを明記し語を定義に合わせる。自信 中
- [minor] N7 要旨が 5e-4 の前提の post hoc の変更を印していない: 178「the extension of the $\tau$ grid and of the structure families, which bear on the main result」。解消: 要旨か序論に「the grid was extended after seeing results」。自信 中
- [minor] N8 2 つ目の帰無の誤警報の率が本文に無い: 187「the other ten measure the false-alarm rate」・推奨 (3) 321「its false-alarm rate」。解消: 4.5 に「false alarms 0 of 10」など。自信 高
- [nit] N9 335「It puts no differences between writers ... into the null」は何の差か分からない。自信 中
- [nit] N10 要旨と序論の「up to $7\times10^{-3}$」に k = 12 の断りが無い。序論は「3–7×10^-3」。自信 中
- [nit] N11 要旨の「relative to their smoothing gain」が未定義。自信 中
- [nit] N12 202「small values for the \arthree{} and the own chain (\Sref{13})」の 3-state AR-HMM の自己相関の範囲を本文に。自信 低

## 4. 総合: major（minor との境目）
1. round 3 の指摘は M2 を除いて解消。値の書き分けと地位の印はほぼ整った。
2. 結論と考察の decision と「2 桁」は固定の平滑の解析だけから出て、推奨 (2) と食い違う（N1）。
3. 推奨した手順の検出力が実データに似た帰無の下で読めない（N2）。どちらも保存済みの値と書き直しで直せる見込み。

## 5. 読めなかった範囲と注入の疑い
- 読まない: references.bib・fig2_p15_ar1.csv・fig2_p15.csv・kit/symbols/README.md。接地は grep の箇所と前後だけ（Monaco の当てはまりの検定の詳細と Pohle 第 4 節は読んでいない）。補足は存在しない。
- 注入の疑い: なし。
