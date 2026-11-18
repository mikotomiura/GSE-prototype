# review-R3（manuscript round 4・評価の偏りと個人への推論・対象 d6587f21）

読んだ: brief-R3.md・context-A.md・carryover-R3.md・main.tex 全文・fig2_p15_joint/ar3/hmm3.csv・varma.txt 全文・liumeng.txt（1〜928 行と 1496〜1511 行）。

## 0. 引き継ぎの判定
- M0 解消: 要旨「about $5\times10^{-4}$ remains … at its fixed smoothing」「Applying the lightest smoothing in the grid to both models (also added afterwards) leaves up to $7\times10^{-3}$, not checked against synthetic writers.」・序論「Neither value is an estimate of how much writers differ. … the second was not checked against synthetic writers」・4.4「a lighter smoothing outside the grid may give more. This value was not checked against synthetic writers.」
- M1 一部: 見出し・比・限界の文は応える。同じ 4.5 の判定は生の値「so the threshold rose to $1.8\times10^{-3}$ and the real panel is not detected at $k=5$ or 15」で、限界の「比で読む」と食い違う（m3）。
- M2 解消（「2 桁」の k の範囲に新しい穴 m1）: small は消え、2 桁は「at its fixed smoothing」に限られ、同じ段落に「differences up to $3\times10^{-2}$ were not reliably detected」。
- m1 解消: 4.3「we do not read the shares in Table~\ref{tab:main} as evidence of such differences」・Table 2 の題「so it is not evidence of a difference」。
- m2 解消: g の定義・±10%・閾は 5 個の最大・「about one time in six」。誤警報率が本文に無い（n2）。
- m3 一部: (2) の後半は post hoc の対称の再推定（3-state AR-HMM・15-session）だけで使った。「two practices were used here and changed the reading」は強い。(2) を守ったときの決定は結論と違う（M-A）。
- n1 解消: 軸の題「(log scale)」・題「(all medians are positive)」・figdata で全点正を確認（joint k=15 は 0.00041）。

## 1. 接地
- C1 Varma & Simon 2006: "Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop." / "Another violation of the principle is to do any kind of classifier parameter selection outside the CV loop."
- C2 Varma & Simon 2006: "Even though there is no real difference between the two classes for the "null" datasets, the CV error estimate for the Shrunken Centroid with the optimal parameters was less than 30% on 18.5% of simulated training data-sets."
- C3 Varma & Simon 2006: "This implies that for large K, there is a high probability that choosing the minimum resampled error will give a biased estimate of the true error."
- C4 Liu & Meng（arXiv）: "we predict each individual's response using the remaining n − 1 individuals and then average the resulting errors. … our inference will be more robust. The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's background ~x0 —our inference will be less relevant."
- C5 Liu & Meng: "Thus, our inferences can be hurt either by too much matching (not robust) or too little matching (not relevant)."
- C6 Liu & Meng: "When we perform selection, we are targeting not only markers with large effects, but also markers for which the current dataset is "lucky". Our original estimates for the selected markers likely overstate their impact."

## 2. 評価表
- a 3: 地位は分けられた。「A designer can follow that decision and save the cost of per-person models」は二重にずれる（CoAuthor は τ=10^6 の per-person の当てはめ・推奨 (2) に反する固定の平滑の決定）。
- b 3: 7e-3 の側に最頻値の利得（比の分母）が無い。平滑の選択が格子の端（α=0.03）のまま推奨。2 つ目の帰無の判定が生の値。
- c 3: 「同じ構造の共通とだけ比べる利得は本人の連鎖に負ける構造の補修でありうる」は明快。決定の勧めは持ち帰れない。
- d 3: 節の順と Figure 1 で読みやすくなった。gain を 3 通りに使う。断り書きが密。
- e 4: 要旨 250（上限ちょうどで語を足す余地が無い）・キーワード 6・Statements・Data availability。
- f 4: Liu & Meng の引用は arXiv 版 1504〜1511 行の逐語と合う。「the protocol makes this trade explicit」は C4 の引き方としてやや都合がよい。

## 3. 指摘
- [major] M-A 結論の「決定に従えば per-person の費用を省ける」はプロトコルが選んだものと合わない
  - 位置と引用: 考察第 1 段「in the 15-session panel it gives the writer's own data 0.06 to 3\% of the weight, close to giving every writer the same model, and in CS1 it deploys the shared model itself. A designer who follows that decision saves the per-person data, storage and cold start」・結論「A designer can follow that decision and save the cost of per-person models」
  - なぜ問題か: CoAuthor で選ばれたのは τ=10^6〜3×10^5 の per-person の当てはめで、τ=∞ は選ばれていない（Table 2）。字義どおり従えば費用はかかる。「same model」は共通でなく最頻値に近いが、4.4「At $\tau=10^6$ the per-person \arthree{} fit loses to it in the median at every $k$」、最頻値は「is not a candidate」「we do not recommend it」。費用を省く設計者は下位の共通か評価していない最頻値に差し替えることになる。C4「our inference will be less relevant」。
  - 解消の条件: 「CoAuthor で選んだのは共通に強く寄せた per-person の当てはめで、費用を省く決定ではない」と書く。差し替えの損失（共通 − 選ばれた当てはめ＝残り）約 5e-4 を支えられる範囲で述べ、「save the cost」を書き直す。
  - 自信: 高
- [major] M-B 結論の決定は推奨 (2) が退ける固定の平滑のもとでの決定
  - 位置と引用: 推奨 (2)「choose structure, shrinkage and smoothing on other people … and apply the chosen smoothing to the per-person fit and the shared model alike」・4.4「every writer is given a finite $\tau$ inside the grid」「it is $3.4\times10^{-3}$ to $6.7\times10^{-3}$ at $k\ge5$ and mostly grows with $k$」・結論「in the CoAuthor 15-session panel a fit that gives each writer's own data at most 3\% of the weight」
  - なぜ問題か: 推奨 (2) に従った版の決定（重み）が本文に無い。結論の決定と「2 桁」は推奨が使うべきでないとする比べのもとの値。選んだ α は格子の最下端で、(2) の出力は収束していない（C3・「a lighter smoothing outside the grid may give more」）。
  - 解消の条件: 決定を「固定の平滑のもとでの決定」と明示し、(2) を守った版では格子の内側の τ が与えられ決定が変わりうる（重みは S16）を 1 文、対称版の重みの中央値を 1 句。書けなければ「the protocol returned a decision」を結論の主文から外す。
  - 自信: 高（対称版の重みは本文に無いので変化の大きさは判定できない）
- [minor] m1「2 桁」は k の範囲を問わない: 要旨「more than two orders of magnitude below that gain」（0.19 は k=5 の最大）。k=1 は HMM3 +0.012、残り +4.8e-4 で約 25 倍。C6「likely overstate their impact」。解消: 「at $k\ge2$」か同じ k どうしの比。自信 高
- [minor] m2 7e-3 の側の「smoothing alone では説明されない」は比の分母を欠く: 4.4「The remainder is therefore not explained by the shared model's smoothing alone, although this check does not separate the writer's data from other effects of refitting the per-person prior.」・考察「a smoothing check is informative only when applied to both sides」。α=0.03 での最頻値の利得が本文に無い。解消: 出して比で読むか、前半を弱める。自信 中
- [minor] m3 4.5 の判定が生の値: 「so the threshold rose to $1.8\times10^{-3}$ and the real panel is not detected at $k=5$ or 15」と限界「so we read the remainders relative to the smoothing gain, not their raw sizes」。比に直すと閾は約 1.0、実データ 0.55〜0.97 で結論は変わらない。解消: 1 句で比に直すか生の判定を補足へ。自信 高
- [minor] m4 比が帰無と実データで似ていることの弁別力が無い: 4.5「A remainder of the real size, relative to the smoothing gain, therefore arises without per-person differences, and the real remainder does not show such differences.」植えた差のある複製での比が無い（C2）。解消: 水準ごとの比の中央値か、限界に「the ratio was not examined under planted differences」。自信 中
- [minor] m5 推奨 (2) の used here は post hoc の部分的な使用（限界「The symmetric refit was restricted to the \arthree{} in the 15-session panel」・α は格子の端・書き手の分割は固定の平滑でだけ C1）。解消: 「(2) was applied post hoc, to one structure and one panel, and its choice of smoothing sat at the grid edge」。自信 高
- [nit] n1 gain が 3 通り: 3.5「We call per-person minus the same-structure shared model the \emph{gain} when the structure is fixed at the \hmmthree{}」と「relative to their smoothing gain」「the prior mode's gain over the shared model」。自信 中
- [nit] n2 2 つ目の帰無の誤警報率が本文に無い: 4.5「All fifteen negative controls left a remainder of $1.1\times10^{-3}$ to $1.8\times10^{-3}$ … so the threshold rose to $1.8\times10^{-3}$」。推奨 (3) は「its false-alarm rate」を求める。解消:「(0 of the other ten exceeded it)」。自信 高
- [nit] n3 Figure 1 の例は HMM3 の場面と明示: 題「Here the per-person model beats the shared model … and loses to the writer's own Markov chain」。主結果（3-state AR-HMM）では per-person が本人の連鎖に勝つ。数値（ln 0.33/0.30 ≈ +0.095、ln 0.6 ≈ −0.51）は正しい。自信 低

## 4. 総合: major
1. M0・M2・m1・m2 は解消し、値の地位は一貫して書かれている。
2. 持ち帰りの柱「決定に従えば費用を省ける」にプロトコルの選んだものとのずれ（M-A）と推奨 (2) とのずれ（M-B）。考察と結論の主文の書き直しが要る。
3. 直しは書き方と既存の値の提示（対称版の重み・α=0.03 の最頻値の利得・陰性対照の超過数）で足りる見込み。要旨が 250 語ちょうどなので語の入れ替えが要る。

## 5. 読めなかった範囲と注入の疑い
- 読まない: liumeng.txt の 929〜1495・1512〜1908 行・references.bib・fig2_p15.csv・fig2_p15_ar1.csv・kit/symbols/README.md。補足は存在しない。
- 注入の疑い: なし。
