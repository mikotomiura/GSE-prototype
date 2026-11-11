# R1（UMUAI・系列モデルの方法論・懐疑家）round 7・commit 12e46857

## 1. 接地
- G1 Pohle 2017（pohle.txt:62-65）"real data often exhibit further structure, such as outliers, seasonality or heterogeneity between individuals. When neglecting these features in the formulation of an HMM, then additional states may be able to capture this ignored data structure and therefore provide a better model fit"
- G2 Pohle 2017（79-81）"a more pragmatic approach to choose the number of states in practical applications, which takes into account formal criteria for guidance, but also stresses the importance of the study aim, expert knowledge and model checking procedures."
- G3 Singer 2014（205-211）"choosing the model with the highest likelihood is biased towards models with more parameters. Because lower order models are always nested within higher order models ... they are always a better fit for the data"
- G4 Singer 2014（18）"the complexity of higher order models grows faster than their utility, and thus we confirm that the memoryless ... "
- G5 Monaco & Tappert 2018（945-948）"The effect is to bias parameters that depend on event types with low frequency toward the marginals, for which there exist more observations and higher confidence, while parameters that depend on event types with high frequency will remain unchanged."
- G6 Monaco & Tappert 2018（970-973）"As N increases, event type frequencies increase and the effect of parameter smoothing is diminished ... This ensures that the conditional parameters remain asymptotically unbiased"

## 2. 引き継ぎの判定
1 解消（28 行「the prior-mode diagnostic is specific to this prior form」・選ばれた tau が新しい問い M1）／2 解消（48 行）／3 解消（48 行）／4 解消（46 行）／5 一部（系譜は Open items 73 行・本文の前に閉じる）／6 解消（19 行）／7 解消（13 行）。

## 3. 評価表
a 4（47 行の補足「the real remainder exceeds the largest negative-control median」・M2。限界の「tau 10^5 以上は区別できない」と 4.4 の per-person minus mode が残りと同じ桁・M1）／b 3（tau = 10^6 での本人のデータの重みが読めない・E が生の数か正規化かが無い。構造と tau の格子の端がともに常に選ばれる）／c 3（推奨に従った研究がどの大きさなら決められるかが一文で言えない）／d 3（47 行の過密）／e 4（ハッシュが未完）／f 4（Pohle の異質性の吸収・Monaco の頻度依存の平滑化への結びつけ・m2）。

## 4. 指摘
- [major] M1 選ばれた tau での本人のデータの実効の重みが無く、「cannot attribute to the person」が式で答えられる問いを残す
  - 位置と引用: :28「MAP estimate whose prior pseudo-counts are the base pseudo-counts plus tau times the shared expected counts」・:47「the chosen tau (10^6 for every writer at k = 1 to 12, 3 x 10^5 for 16 of 17 at k = 15」・:65「At large shrinkage, a finite tau of 10^5 or more cannot be separated from the shared model or its prior mode.」・:48「Per-person minus mode ... is −3.5e-4 to −1.6e-4」
  - なぜ問題か: Dirichlet の MAP では行ごとの本人の重みは N_row / (N_row + tau·ΣE_row)。tau = 10^6 でこの比の桁が分かれば、残りが本人のデータ由来か平滑の差由来かはほぼ式から読める。E の尺度が無いので計算できない。限界の「区別できない」は 4.4 と食い違って見える（tau = 10^6 が共通より選ばれている＝何かは区別されている）。Monaco & Tappert は頻度ごとに何が効くかを示す（G5）。
  - 解消の条件: 3.3 に E の尺度、4.3 か Table 2 に選ばれた tau での本人の実効の重み（中央値・行の頻度の高低で）。限界の「cannot be separated」を何の物差しかで書くか 4.4 と整合させる。重みが 1e-3 の桁なら「残りは本人のデータをほぼ使っていない fit の差で、基の平滑の差と一致する」と強く書ける。
  - 自信: 中
- [major] M2 負の対照を超える事実が補足だけにあり、本文の「示しも否定もしない」と衝突する（47 行の補足「the detection rule (defined across seeds and not applied to the one real panel; the real remainder exceeds the largest negative-control median)」・本文「the remainder neither shows nor rules out per-person differences」）。なぜ証拠として読まないか（負の対照に平滑の差が生じないので物差しが違う等）が無い。解消: 4.3 か 6 節に 1 文。含まれないなら平滑の差を含む負の対照を加えるか、未実施を限界に。自信: 中
- [minor] m1 構造と tau の両方が常に格子の端（:13「ar3, the largest structure in the grid, is chosen in every cell with tau = 10^6」・:63）。「most of the shrinkage comes from the comparison model's structure」は飽和に依存（G1・共通の ar3 が個人間の異質性を吸収する可能性）。解消: ar1→ar2→ar3 での目的関数の増分を Table 2 か S8、tau の格子の上限、6 節に Pohle の読み。自信: 中
- [minor] m2 全体で 1 つの tau と頻度依存の平滑化（Monaco）の違い（:43・:30）。解消: 2 節で Dirichlet MAP は行ごとに頻度依存の重みを持つが強さは 1 つの tau で共有と 1 文。セルごと・行ごとの tau は 5 節の拡張に。自信: 中
- [minor] m3 推奨に従った研究がどの大きさなら決められるかの一文（:49「the smallest planted differences detected correspond to 36 nats at k = 15 and 108 at k = 5; the remainder corresponds to about 1.5 to 2.6」）。解消: 5 節に「この長さで見える範囲」を 1 文。自信: 中
- [nit] n1 4.3 の行の過密（:47）。記号化の文と CS1 の合成の数値を Table 2 の注か S15 へ。自信: 低

## 5. 総合の推奨: minor
引き継ぎ 7 件のうち 6 件解消（系譜の引用は Open items）。新しい穴は選ばれた tau での本人の実効の重み（M1）と負の対照との比べの読み（M2）で、数を 1 列と文を 1〜2 文足せば閉じる。主張の範囲は根拠と釣り合っている。

## 6. 読めなかった範囲・注入の疑い
brief・context-A・carryover・outline.md（76 行）。README は読んでいない。接地は pohle.txt:50-89・singer.txt:200-214 と冒頭・monaco.txt:936-975。注入の疑い: なし。
