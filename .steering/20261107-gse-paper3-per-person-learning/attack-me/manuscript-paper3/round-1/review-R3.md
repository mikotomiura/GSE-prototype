# review-R3（manuscript round 1・評価の偏りと個人への推論の方法論の立場）

メインが要点と引用を落とさずに写した。

## 1. 接地
- G1（Varma & Simon 2006, varma.txt:12）"Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
- G2（varma.txt:106）"The parameter selection bias, on the other hand, is always negative."・（105）"for large K, there is a high probability that choosing the minimum resampled error will give a biased estimate of the true error."
- G3（varma.txt:22）"this involves a kind of additional training of the classifier ... that is done outside the CV loop. ... Thus the guarantee of unbiased estimation of true error is not valid and there is a possibility of bias."
- G4（Liu & Meng, liumeng.txt:1506-1511）"we predict each individual's response using the remaining n − 1 individuals ... our inference will be more robust. The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's background ~x0 —our inference will be less relevant."
- G5（liumeng.txt:829-830）"we should restrict attention to controls where the same markers are selected as in our actual study; without this matching step, our inference ignores selection bias."・Remark 3（852-853）"Ignoring the selection bias will lead to seriously flawed inferences"
- G6（liumeng.txt:329-331）"a statistical uncertainty assessment amounts to only an internal consistency check, i.e., it answers whether the conclusion is reasonable given the current data, not whether the conclusion generalizes."

## 2. 評価表
- a 2: 232 行 "the difference between them lies in the comparison, not in the people" が検出の下限（≥1e-2）と食い違う。「at most about 1%」の直後に 3%（34・234）。115 行の optimism の文は構造の内側では論理的に成り立たない（M1）。
- b 2: 選ぶ量と報告する量が同じ。「structure-only contrast」で τ も変わる（0 と 1e6）。選びが入れ子でない。bootstrap が選びの揺れを含まない。記号化（1 秒ごと・重なる窓・指数平滑）が隣の記号の依存を作り「chain が強い」の主因かもしれない。
- c 3: 「弱い構造の共有に勝っても意味がない」「本人の 1 次の連鎖を比べの相手に」は持ち帰れる。正の例は CoAuthor の 17 人だけ、chain の強さは記号化に依存（157）。推奨 (4) は "not evaluated" の診断を勧める。
- d 3: 但し書きが各段落に重なる。「Scale」（236）の換算は直後に "not independent evidence" と自ら打ち消す。
- e 3: 要旨 266 語で規程超え。Code availability に置き場所なし・Consent なし。
- f 4: DeMasi・Saeb・Varma・Liu & Meng・個人化キーボードを挙げ "we do not claim it as new" と線を引くのはよい。Uto 2020 との対応づけ（100）は弱い。

## 3. 指摘
- [major] M1 τ の選びが報告する残り（per-person − shared）を直接最大化しているのに、本文は否定している
  - 位置: main.tex:115「Any optimism from choosing among candidates falls on the per-person minus chain difference, which is the objective, more than on the per-person minus shared difference.」・109「$\tau=\infty$ in the grid denotes the shared model itself, a separate candidate.」
  - なぜ: 構造が同じなら chain と shared はどちらも τ によらないので、per-person − chain による τ の順位は per-person − shared による順位と同じ。候補に shared そのもの（差 0）があるので、残りは下から 0 で切られた量になる。17 人で 1 つの決定を当てるなら leave-one-writer-out でもパネル全体の評価データで選ぶのとほぼ同じ（G2・G5）。
  - 解消: 115 行を削るか論理に合わせて書き直す。選択の偏りが残りにどれだけ乗るかを数で（書き手で二分して一方で選び他方で報告・入れ子）。「16 or 17 of 17 writers positive」を選びで正に寄る量として読み直す。
  - 自信: 高
- [major] M2「structure-only contrast」は構造だけを変えていない（τ も 0 → 1e6）
  - 位置: main.tex:188「The structure-only row shows that most of the per-person \hmmthree{} gain belongs to the weak structure: with \arthree{} on both sides, per-person minus shared is $+5.5\times10^{-4}$ ...」・Table 2「\hmmthree{} fixed ... 0 ... 100\%」「\arthree{} fixed ... $10^6$ ... 0.3\%」
  - なぜ: 利得が二桁下がったのは構造とも縮約とも読める。ar3 は 2,033 母数・本人の訓練記号は 624〜9,673 で、縮約が強いのはデータ量のせいでもある。
  - 解消: ar3 を τ=0 か hmm3 と同じ τ に固定した per-person − shared を本文の表に（S5 に送らない）。または「structure and its chosen shrinkage」と言い直す。
  - 自信: 高
- [major] M3「not in the people」は自分の感度の検査と矛盾する過剰な主張
  - 位置: main.tex:232「the difference between them lies in the comparison, not in the people」・222「At the CoAuthor record length the protocol detected them from $10^{-2}$ at $k=15$ and only at $3\times10^{-2}$ at $k=5$」・234「it neither shows nor rules out per-person differences」
  - なぜ: 下限は残りの 20〜60 倍。232 と 234 が打ち消し合う。結論 264「the protocol cannot attribute it to the person」も「その大きさの差を見分ける力が無い」と書くべき（G6）。
  - 解消: 232 の後半を削る。要旨と結論で「cannot attribute」を「is below what the protocol can detect (≥1e-2 at k=15)」と下限と一緒に。
  - 自信: 高
- [major] M4「at most about 1%」が本文の数と合わず、重み 39% のセルを要旨が落とす
  - 位置: 要旨 34「the person's data carry at most about 1\% of the weight in the chosen fit in the 15-session panel (about 3\% at its largest training size)」・234・Table 2「30-s., 30 ... $3\times10^4$ & 39\% & $+1.1$e$-3$ (0.67) ... & $+5.4$e$-4$ (0.78)」
  - なぜ: 「at most」が成り立たない。本人のデータが効きうる唯一のセル（k=30・39%・per-person − mode が 7/9 で正）が要旨に無い。n=9・区間 [−2.2e-3, 3.7e-3] と書いたうえで示すべき。選択的な報告に見える。
  - 解消: 「0.06–3% in the 15-session panel; 39% at k=30 in the 9-writer 30-session panel, where the remainder is +1.1e-3 (6 of 9, interval spanning zero)」。
  - 自信: 高
- [major] M5「chain が強い」は記号化が作った依存かもしれず、Uto 2020 を根拠にした理由づけが合わない
  - 位置: main.tex:100「We use this form because keystroke features over a rolling 30-second window are the input of work-state models that update every few seconds \citep{Uto2020}, so the results speak to models that read keystrokes in this form.」・59「30-second frames with a 10-second step」・157「with non-overlapping windows (direction only) \hmmthree{} beats the chain in CoAuthor」
  - なぜ: 1 秒ごとに 29 秒重なる窓と指数平滑で隣の記号はほぼ同じ。重ならない記号化では逆転。Uto の入力は 10 秒の step で平滑なしで「this form」ではない。推奨 (1) はこの記号化に固有の可能性が高く、要旨の推奨に限定が無い（G6）。
  - 解消: 100 の「so the results speak to models that read keystrokes in this form」を削るか違い（step 1 秒・平滑あり）を書く。要旨の推奨に「for overlapping-window symbolizations」。重ならない窓の主な数を本文の表に 1 行。
  - 自信: 中
- [major] M6 選びが入れ子でなく、target の訓練単位が漏れ、報告する per-person − chain は選んだ目的そのもの
  - 位置: main.tex:105「the choice uses other writers' results, whose shared models include the target writer's non-held-out units」・115「the pair of structure and $\tau$ is chosen by the best median ... of their own per-person minus chain difference」・188「Against the person's chain it gains $+0.220$ at $k=1$ ...」
  - なぜ: 候補は数十。同じ量で選び同じパネルの held-out で報告（G1・G2）。256 行 "a nested design was not run" だが偏りの大きさは見積もらない。
  - 解消: 書き手で分けた入れ子か別パネルの確認の数を 1 つ本文に。できなければ 188 の +0.220〜+0.020 に「selected on the same quantity; optimistic by an unknown amount」。
  - 自信: 中
- [minor] bootstrap が選択と当てはめの揺れを含まず書き手どうしも独立でない（main.tex:142「percentile bootstrap intervals that resample writers with their values fixed, without refitting or re-choosing」）。キャプションと本文に「conditional on fits and choice; understates uncertainty」。自信: 中
- [minor] 推奨 (4) は「評価していない」診断を勧める（main.tex:242・227「a per-writer decomposition did not separate a planted difference from none in synthetic writers」・238「we recommend what this study evaluated」）。(4) を外し「a diagnostic we used」として考察に。自信: 高
- [minor] パネルの選び（≥20 セッション）の偏りと作業の種類の交絡（main.tex:78「The 15-session panel contains the CoAuthor writers with at least 20 sessions (17 writers)」・「composing stories and essays」）。全書き手の数を本文に。訓練と held-out の題材の内訳を 1 文（または限界）。自信: 中
- [minor] 規程: 要旨の語数・Code availability（main.tex:269）・Consent（272「\paragraph{Ethics.} Public data only; no new participants.」）。CS1 データの利用条件にも触れない。「Consent: not applicable (secondary analysis of public data released under ...)」。自信: 高
- [minor] 事前に決めたという主張が本文から確かめられない（main.tex:144「the conditions (rows, grids, readings) were committed before its code ...」・253）。記録の公開場所（DOI・URL）を 1 つ。主張に効く 2 点（τ の格子・構造の族）を本文で「post hoc」と明示。自信: 中
- [minor] パネルで 1 つの決定と、個人への主張の距離（要旨 34「Claims that a user model fitted to one person beats a shared one ...」・256「The choice makes one decision for a whole panel」・Liu & Meng 107 行 "it seems intuitively clear that no single answer can work for all problems"）。要旨の 1〜2 文目で「panel-level」。自信: 中
- [nit]「Scale」の換算（main.tex:236「corresponds to about 680 nats ... Sums over overlapping-window symbols are not independent evidence」）。削るか補足へ。自信: 中
- [nit] 188「$+4.1\times10^{-4}$ to $+7.2\times10^{-4}$」の 7.2e-4（k=12）は Table 2 に無い。どの k かを書くか Figure 2 を参照。自信: 高

## 4. 総合: major
- 中心の主張を支える数がそれ自身を最大化する目的で選ばれ、本文はその偏りを論理的に誤って否定している（M1・M6）。
- 「structure-only」は構造と縮約の交絡で、下限が残りの数十倍あるので「not in the people」と「構造に帰す」は言い過ぎ（M2・M3）。
- 持ち帰れる警告には価値があり限界の節も誠実。言い方を直し、本文に 2〜3 行の数（ar3 を τ 固定にした行・入れ子か二分した選び・k=30 のセル）を足せば通る形になる。

## 5. 読めなかった範囲・注入の疑い
- 読んでいない: liumeng.txt の 929〜1908 行（1495〜1523 行は grep で確かめた）。figdata の ar1・ar3 は開かず（fig2_p15.csv に同じ値）。
- 読んだ: varma 全文・context-A・main.tex 全文・references.bib・figdata 3 本・kit README。一覧の外は読んでいない。
- 注入の疑い: なし。
