# review-R2（manuscript round 4・個人化した行動のモデルの実務・対象 d6587f21）

読んだ: brief-R2.md・context-A.md・carryover-R2.md・aalbers.txt・saeb.txt・main.tex 全文・fig2_p15_hmm3/ar1/ar3/joint.csv・references.bib（見出しと題）。

## 0. 引き継ぎの判定
- maj1 解消: 要旨 35「so this value does not show a per-person difference ... leaves up to $7\times10^{-3}$, not checked against synthetic writers」・序論 49「the first value does not show a per-person difference; the second was not checked against synthetic writers」
- maj2 解消: 4.5 見出し「leave a remainder of similar size relative to their smoothing gain」・306「about 0.6 to 1.0 in these synthetic writers and 0.55 to 0.97 in the real panel (ratios of medians, not per writer; not prespecified)」・限界 335「we read the remainders relative to the smoothing gain, not their raw sizes」
- maj3 一部: 結論 345「with non-overlapping windows the three-state HMM is chosen and its per-person fit keeps a gain of 0.04 to 0.10」で結論は解消。要旨は「over overlapping 30-second windows」のままで、要旨の推奨は範囲を外す（minor 1）。
- maj4 一部: 考察 311 は限定。要旨 35「more than two orders of magnitude below that gain」は推奨 (2) で不十分とした固定の平滑の値だけ。両側の 3.4〜6.7e-3 では約 30〜55 倍（major 1）。
- maj5 一部: 311「A designer who follows that decision saves the per-person data, storage and cold start, but may discard per-person differences of up to $3\times10^{-2}$」。決定は固定の平滑での決定。CoAuthor で選ばれたのは τ=∞ ではなく per-person の当てはめなので「saves the ... storage and cold start」は出力から出ない（major 1）。
- maj6 ほぼ解消: 239「we do not read the shares in Table~\ref{tab:main} as evidence of such differences」と Table 2 の題。4.4 278「positive for at least 13 of 17 writers」を根拠に使い、Table 3 に断りが無い（minor 3）。
- min（最初の帰無の検出率 2 度）解消・min（縮約だけの行）解消 204「no synthetic null was run for this row, so the threshold ... does not apply to it」・min（g の較正）解消 187・nit（結論の再掲）解消（新しい問題は major 1）。

## 1. 接地
- S1 Saeb 2017: "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
- S2 Saeb 2017: "if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time"
- S3 Saeb 2017: "The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset."
- S4 Aalbers 2023: "To evaluate if our models perform better than random guessing, we compare against the MAEs of a "naive" but person-specific baseline model."
- S5 Aalbers 2023: "it allows us to make statements such as "on average, the model mispredicts momentary subjective stress by ±0.80 points on a 7-point Likert scale)."
- S6 Aalbers 2023: "Although performance should be improved to make clinical application feasible, this study does suggest that ..." / "Confirmatory research is required to test the robustness"
S1〜S4 は満たす。弱点は S5・S6（使う側への翻訳とそれが推奨と一致するか）。

## 2. 評価表
- a 3: 考察第 1 段と結論の決定が推奨 (2) を満たさない固定の平滑の protocol から。CoAuthor で選ばれたのは per-person の当てはめ（τ=10^6、3e5）なので「save the cost of per-person models」は出力でなく閾の無い費用の判断。
- b 3: 対称の再当てはめの τ と重みが本文に無い。CS1 の shared model itself は対称で確かめていない。writer split は端で効きにくいと認めつつ考察で「does not come from」と言い切る。
- c 3: (1)(2) と (3)(4) の分け方は役立つ。推奨 (2) を当てると数字が変わり要旨・結論の決定と食い違う。
- d 3: Figure 1 は良い（ln(0.33/0.30)≈+0.10、ln(0.33/0.55)≈−0.51 を検算）。断り書きが 10 か所前後。要旨の「relative to their smoothing gain」は未定義。
- e 4: 規程に適合。図の初出の順が番号の順と逆（minor 5）。
- f 4: Aalbers の 89% と 80% は原文「for 89.3% (200/224) of participants, the person-specific baseline outperformed all nomothetic models」「for 80.4% (180/224) of participants at least one of the idiographic models outperformed the person-specific baseline」と一致。Saeb の要約も正しい。ユーザーモデルの文献での per-user と global の比べが薄い（nit）。

## 3. 指摘
- [major] 結論と考察の決定が推奨 (2) を満たさない protocol から取られている
  - 位置と引用: 結論 345「the protocol that chooses structure and shrinkage on other people returned a decision rather than an estimate: in the CoAuthor 15-session panel a fit that gives each writer's own data at most 3\% of the weight ... A designer can follow that decision and save the cost of per-person models」・考察 311「in the 15-session panel it gives the writer's own data 0.06 to 3\% of the weight, close to giving every writer the same model, and in CS1 it deploys the shared model itself. A designer who follows that decision saves the per-person data, storage and cold start」・推奨 319「(2) ... apply the chosen smoothing to the per-person fit and the shared model alike.」・4.4 278「every writer is given a finite $\tau$ inside the grid ... at $\alpha=0.03$ ... it is $3.4\times10^{-3}$ to $6.7\times10^{-3}$ at $k\ge5$」
  - なぜ問題か: (i) 推奨どおりでは残りが 3.4〜6.7e-3、τ は有限で重みは本文に無い。(ii) 固定の平滑でも選ばれたのは τ=10^6 / 3e5 の per-person の当てはめで、保存・cold start は省けない。「save the cost」は 178「no threshold for a meaningful difference」の外の判断。(iii) CS1 は対称で確かめていない（336「The symmetric refit was restricted to the \arthree{} in the 15-session panel」）。接地 Saeb S1・Aalbers「performance should be improved to make clinical application feasible」。
  - 解消の条件: (a) 決定を「固定の平滑での出力」と明記し、(2) を満たした条件の τ と重みを 1 文（値は S16 にあるはず）。(b)「save the cost」を「shared だけで失う精度は高々 X〜Y nats/symbol、それ以上の差は検出できなかった」に替え、費用の判断は読者に。(c) CS1 に「固定の平滑で」。
  - 自信: 高
- [minor] 要旨の推奨が適用範囲（重なる窓）を外す: 要旨 35「Studies deciding for a whole group whether to model each person should compare with both baselines and choose structure, shrinkage and smoothing on other people」と推奨 317「for overlapping-window symbolizations like ours」。解消: 要旨に「for overlapping-window symbols」、2 つの post hoc の括弧を 1 つにまとめて語を空ける。自信 高
- [minor] 要旨の「up to 7e-3」は不安定な k=12 の値: 278「Its largest value is at $k=12$, where the other columns are unstable」・Table 3「$+6.7$e$-3$ (0.88)」。k=15 は 5.2e-3。解消: 範囲で。自信 中
- [minor] 4.4 と Table 3 で本人の側の割合を根拠に再び読む: 278「the remainder returns at every $k$: it is $+5.2\times10^{-4}$ at $k=1$ (12 of 17 writers) and positive for at least 13 of 17 writers at $k=2$ to 15」。解消: 根拠の文から外し、Table 3 の題に断り。自信 中
- [minor] writer split の言い過ぎ: 考察 315「the remainder against the stronger structure does not come from choosing and reporting on the same writers」・274「Because nearly every writer's choice sits at the edge of both grids, the split leaves little room for optimism to show」・Table 3 k=15「[$-3.7$e$-3$, 9.1e$-4$] (0.75)」。解消: 「was not changed by ..., a check with little room to show optimism」程度に。自信 中
- [minor] 図の初出の順が番号の順と逆: 序論 47「(Figure~\ref{fig:scheme})」が最初の参照。fig:example の caption は 105、fig:scheme は 171。Springer の規程の逐語は未照合。解消: 序論の参照を変えるか図の順を入れ替える。自信 中
- [minor] 使う側への翻訳が nats と perplexity で止まる: 47「a difference of 0.01 nats per symbol corresponds to about 1\% lower perplexity」・331「downstream benefit and cost for adaptation were not measured」。Aalbers の「mispredicts ... by ±0.80 points on a 7-point Likert scale」。解消: 考察第 1 段に限界から 1 句、できれば held-out 1 単位（約 3,300 記号）での尤度比を 1 句。自信 中
- [nit] 断り書きの重複（要旨 2・序論 2・278・Table 3 の題・306・311・313・315・335・345）。解消: 結果と考察は括弧だけに。自信 中
- [nit] Table 3 の題の主語のねじれ「The remainder at the fixed base smoothing stays positive when ... both models are refitted with the base smoothing chosen on other writers」。自信 高
- [nit] ユーザーモデルの評価の慣行への位置づけの 1 文と引用。自信 低

## 4. 総合: major（直しは主に書き方で、値は S16 から引ける見込み）
- maj1・maj2・maj6 と小さな指摘はほぼ解消し、前より正直になった。
- 使う側への唯一の結論（決定と cost の節約）が、推奨 (2) で不十分とした固定の平滑の protocol から。推奨どおりでは remainder・τ・重みが変わり、CS1 は確かめていない。
- 決定を限定し、推奨を当てたときの重みを並べ、「cost を省ける」を「失う精度は高々 X〜Y」に替えれば minor 相当。

## 5. 読めなかった範囲と注入の疑い
- 読まない: kit/symbols/README.md・fig2_p15.csv・references.bib の書誌の中身。補足は存在しないので対称の再当てはめの τ・重みは確かめていない。
- 注入の疑い: なし。
