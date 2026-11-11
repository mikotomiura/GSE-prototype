# R1（UMUAI・系列モデルの方法論・懐疑家）round 6・commit 90250abc

## 1. 接地
1 Pohle 2017（pohle.txt l.4453-4455）"AIC and BIC tend to favor models with too many states, since any structure in the data that is neglected in the model formulation will, to some extent, be mopped up by additional model states"
2 Pohle 2017（l.1352-1353, 1359）"model validation, i.e. the assessment if any given candidate model adequately represents the data-generating process"・"a model check based on pseudo-residuals (Patterson et al., 2009)"
3 Singer 2014（l.205-211）"choosing the model with the highest likelihood is biased towards models with more parameters. Because lower order models are always nested within higher order models ... they are always a better fit"
4 Singer 2014（l.18-21）"the memoryless model represents a quite practical model for human navigation on a page level. However ... at a topical level ... the memoryless assumption is violated"
5 Monaco & Tappert 2018（l.939-941, 1040-1041）"parameter smoothing ... acts as a kind of regularization to avoid overfitting"・"parameter smoothing, whose effect diminishes as N increases. Consequently, the smoothed POHMM estimates approach that of the unsmoothed"

## 2. 評価表
a 4（物差しはそろった。4.4 の "both directions are smaller than the protocol could detect" は観測した対比と植えた差を同じ尺度で比べる・指摘 2）／b 3（tau → ∞ で共有でなく prior mode に近づくので残りが平滑の差と同じ大きさになるのはパラメータ化から機械的に生じうるのに、選ばれた tau が本文に無い・指摘 1。有限の書き手だけの中央値の偏り・指摘 3。離散の擬似残差の定義・指摘 4）／c 3（prior mode の診断が一般の手順か本研究の事前分布の形に固有か不明）／d 3（4.3 と 4.4 が過密）／e 4／f 4（AR(1)-HMM を離散の Markov-switching の系譜に結びつけていない・指摘 5）。

## 引き継ぎの判定
1 解消（Take-home の "could not have detected" は nit）／2 解消／3 解消（開示として）／4 解消（中央値の取り方は指摘 3）／5 解消（680・70〜800・36・1.5〜2.6 は 3,600 倍で一致）／6 解消／7 一部（指摘 4）。

## 3. 指摘
- [major] per-person の事前分布の極限が共有モデルを含まないので残りがパラメータ化から生じうる。選ばれた tau を本文に出していない
  - 位置と引用: Comparison models「As tau grows the fit approaches the prior mode, not the shared model; tau = infinity in the grid denotes the shared model itself, a separate candidate.」／Limitations「At large shrinkage, a finite tau of 10^5 or more cannot be separated from the shared model or its prior mode.」／4.3 の本文に chosen tau が無い（"Chosen tau and K ... (S8)"）
  - なぜ問題か: 縮小の族は共有モデルを含まず prior mode へ向かうので、tau を大きくすれば本人のデータをほとんど使わずに共有の平滑の強すぎる分を取り戻せる。4.4 の「prior mode minus shared が残りと同じ大きさ」は設計から予想される結果の可能性。per-person minus mode が負で minus shared が正であることも、per-person が shared と mode の間にある（族の端の効果）という読みと矛盾しない（Monaco & Tappert「the smoothed POHMM estimates approach that of the unsmoothed」）。
  - 解消の条件: Table 2 か 4.3 に選ばれた tau の分布（中央値と範囲・10^5 以上の割合）。あわせて (i) 事前の擬似カウントを「base + tau × 共有の事後カウント（base を含む）」にして tau → ∞ で共有モデルに一致させた族で残りを報告する（1 行の確認）、または (ii) prior mode の診断は本研究の事前分布の形に対する診断と C1 と 5 章で範囲を限り、一般の手順として勧めない。
  - 自信: 中（選ばれた tau を見ていない）
- [minor] 4.4 で観測した対比の大きさを植えた差の検出水準と比べている（4.4「both directions are smaller than the protocol could detect, so we do not read a direction」）。解消: その対比の合成の陰性対照との比べに置き換えるか、「方向を読まない」とだけ書き検出の物差しを持ち出さない。自信: 中
- [minor] per-person minus mode の中央値を有限の書き手だけで取ると負に偏る（4.4「(positive for 1 to 4 of the 15 writers with finite values; 2 writers have +infinity ...)」）。+infinity の 2 人は per-person が勝つ側。解消: 17 人全員での中央値（+infinity を含む）と正の人数（3〜6）を併記するか、除外の偏りを 1 文。自信: 高
- [minor] 離散の記号に対する擬似残差の定義と記号 25 の扱い（4.2「one-step-ahead pseudo-residuals on the two ordered grid axes leave a lag-1 autocorrelation of 0.23 to 0.64 for hmm3」・README「Symbol 25 replaces the grid symbol at the first typing second after a run of 14 or more consecutive deletions」）。解消: mid かランダム化か・x 軸と y 軸の周辺・記号 25 の扱いを一句、詳細は S13。自信: 中
- [minor]「AR(1)-HMM」を記号列の離散モデルの系譜に結びつけていない（冒頭「ar1, ar2 and ar3 are AR(1)-HMMs with 1 to 3 states (ar1 is a first-order Markov chain)」）。解消: 3.3 で「state-dependent first-order transition among symbols」と定義し、自由パラメータの数を表に。2 章に double chain / MTD 系を 1 文と 1 引用。自信: 中
- [minor] 本人の連鎖が強い相手であることが重なった窓と平滑化に由来するかを変種で示していない（4.3「non-overlapping windows, direction only: hmm3 is chosen in CoAuthor and the difference stays positive」・Supporting evidence「On overlapping-window symbolizations the per-person three-state HMM loses to it」・Singer 接地 4）。解消: 記号化の一文に非重なりでの per-person minus chain の方向、勧告を「重なった窓の記号化では」に限るか変種で裏づける。自信: 中
- [nit] Take-home の "could not have detected"（4 水準 × 2 種）。解消: "did not detect, in synthetic writers of this record length," に。自信: 高

## 4. 総合の推奨: minor
引き継ぎ 7 件のうち 6 件解消・1 件一部。残る最大の穴は事前分布の極限が共有モデルを含まないことで、選ばれた tau を本文に出し、範囲を限るか 1 行の確認で片づく。ほかは一句か補足への参照で直せる。

## 5. 読めなかった範囲・注入の疑い
S1〜S15・要旨・参考文献・context-B・他の記録は読んでいない。接地は grep の周辺だけ。grep が sources 全体に掛かり saeb.txt・varma.txt の断片が出た（使っていない）。注入の疑い: なし。
