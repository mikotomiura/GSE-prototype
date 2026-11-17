# R1 の応答（再識別・匿名化への攻撃の評価・round 4・commit bf0d2450）

総合: minor（計算を足さず文の置き換えと限定で消える）。

## 1. 接地（grep で該当箇所と前後を読んだ）
- G1 narayanan.txt:13 "robust to perturbation in the data and tolerate some mistakes in the adversary's background knowledge."
- G2 narayanan :45 "priori that the adversary's knowledge is limited to a fixed set of "quasi-identifier" attributes. Our model thus" / :82 "it is impossible to tell in advance which attributes might be available to the adversary"
- G3 narayanan :287–291 "If (max−max2)/σ < φ, where φ is a fixed parameter called the eccentricity, then there is no match; otherwise, the matching set consists of the record with the highest score."
- G4 stadler.txt:295–297 "A good anonymisation mechanism should result in a high privacy gain for all records in the population and under any potential privacy adversary."
- G5 stadler :313–317 "the privacy risks of data sharing are not uniformly distributed across the population … outliers or members of minorities largely remain vulnerable."
- G6 rocher.txt:127–131 "the likelihood of a re-identification to be correct, even in a heavily sampled dataset, can be accurately estimated, and is often high. Our results reject the claims that … sampling or releasing partial datasets provide plausible deniability."

## 2. 評価表
a 3（「4 倍以内」は登録に無い切りで R4(4) の区間の上端が超える・登録の λ = 4 の 45 倍を抄録・序論・結論が言わない・結論の "did not stay there" は N を限らず N = 10 で偽）／b 3（探索は格子の端 λ = 2 で 14 組中 13 勝・R3-u に当てていない・探索の変種に陰性対照が無い）／c 4（余裕の大きい照合が正しいことが §7.4 の 1 文に埋もれる）／d 3（§7.2 l.67–79 に 4 層・抄録 348 語・related の重複）／e 4（12 頁内・余白 0.3 頁・必須の節は正しい）／f 4（margin は Narayanan の eccentricity と同じ考えなのに触れない）。

## 3. 引き継ぎ
1 一部（"within four times $1/N$" も登録に無い切り）／2 一部（探索は正しい対応。抄録・序論・結論が λ = 4 を言わない・R3-u を強めていない・N の範囲）／3 解消（discussion.tex l.74–76。探索で N = 10 の R4(4) が 78.1% は未記載）／4 解消／5 解消／6 一部 nit（KeyTAR が表 3・§5・§7.4・§8.1 に残る）／7〜11 解消。

## 4. 指摘
- [major] M1 「4 倍以内」は登録に無い切りで、R4(4) の区間は切りを超える
  - 位置: abstract.tex l.14・results.tex l.153–154 "Only R4(4) and R4(8) brought the strongest attacker within four times $1/N$"・main-1000.tex l.12 "R4(4) & 0.35 & 0.35 [0.07, 0.73] & A0 (95) & 3.5"・protocol.tex l.13–14 "No pass or fail criterion is set"
  - 理由: 根拠も定義も無い。R4(4) の上端 0.73% は 7.3 倍。登録の量「A0 からの利得」は R4(4)・R4(8) とも 0.0 [0.0, 0.04]・[0.0, 0.18] で同じことが言える。round 3 の 0.84 と同じ型。G4。
  - 解消: 「within four times chance」を登録の量で書き換え（"left no gain over the total-length attacker"）、倍数は表の値として添える。残すなら §6 に事後の要約の切りと理由を書き区間で判定。
  - 自信: 高
- [major] M2 登録の副次の分析がすでに R4(4) を破っていたことを抄録・序論・結論が言わない
  - 位置: abstract.tex l.15–17・conclusion.tex l.7–8 "brought these attackers with their main penalty within four times chance; stronger attackers tried afterwards as an exploration did not stay there"・results.tex l.69–70・l.91 "(R4(4) not against A2 with $\lambda = 4$ …)"
  - 理由: 登録の範囲（λ ∈ {4, 8, 16}）で A0 を超えなかったと頑健に言える粗い形は R4(8) だけ（explore-lambda-scan-1000.tex l.11: A2 は λ = 2〜16 で 0.08%）。1 つのパラメータで結論が変わる形を見出しに置くのは弱い（G1）。
  - 解消: 「with their main penalty」を「for every registered penalty, only R4(8)」に置き換える（「登録の攻撃者 λ = 4, 8, 16 のすべてで A0 を超えなかったのは R4(8) だけで、R4(4) は主の λ でのみ」）。
  - 自信: 高
- [major] M3 探索は R4 と R7 だけを強めたので、強めた後の前線・支配の比べが非対称になるのに本文が言わない
  - 位置: appendix-exploratory.tex l.69 "The sixth analysis runs A2 on R3, R4($w$) and R7($p$), and A1$'$ on R3 and R7($p$)"・results.tex l.144–146 "R7(0.25) dominates R3-u, with a lower accuracy (14.3\% against 36.0\%)"・discussion.tex l.67–69 "of the coarsened and suppressed forms only R4(8) and R7(0.5) stayed there against the exploratory attackers"
  - 理由: 探索で R7(0.25) は 62.3% で R3-u の 36.0% を超え、支配は登録の攻撃者でだけ成り立つ。R3-u が 40% 未満に見えるのは強めなかった産物でありうる。
  - 解消: §7.3 の支配の文に「登録の攻撃者で」。§7.2 か付録 D に「R3-u は探索で強めていない」。図は λ = 8 のままでよい。
  - 自信: 高
- [minor] m1 探索の N の範囲が結論と §8 冒頭で落ちる（conclusion.tex l.8・discussion.tex l.11–12）。N = 10 では探索でも R4(8) は 30.3%（3.0 倍・explore-strongest.tex l.6）。§8.3 の N = 10 の文は探索で R4(4) が 31.2% → 78.1% を言わない。解消: 「at $N = 1{,}000$」を足し、§8.3 に括弧で 78%。自信 高。
- [minor] m2 探索の攻撃者に陰性対照が無く、格子の端の勝ちは上限を示さない（appendix-exploratory.tex l.72–74・89–91）。λ = 2 で R7(0.5) の A2 は 0.0 → 0.2 → 1.0% と上がる（explore-lambda-scan-1000.tex l.19）。解消: R4(8)・R7(0.5) で A2-scan と λ = 2 の陰性対照、無理なら「R7(0.5) stayed at A0」に「λ < 2 は試していない」。自信 中。
- [minor] m3 「余裕の大きい照合は当たる」が本文で 1 文・持ち帰りに無い（results.tex l.171–173・explore-margin.tex l.28 R7(0.25) 上位 10% で 57.2%、R4(2) 4.4% → 25.4%）。G3・G6・G5。解消: §8.3 に 1 文、§7.2 の窓の細部（l.70–71）を付録へ。margin が eccentricity と同じ考えであることを 1 句。自信 中。
- [minor] m4 §7.2 の 1 段落の過積載（l.67–79）と抄録の長さ。解消: 窓の文を §7.4 か付録へ、探索は別段落、抄録の探索の文は短く。自信 中。
- [nit] n1 related.tex l.46–47 の重複。自信 高。
- [nit] n2 data.tex l.79・l.81 で表 2 の R3-t の行が released key を残すように読める → "As R3"。自信 中。

## 5. 推奨: minor
C1 は事前登録と陰性対照に支えられ強い。探索を手順の固定の後に回したのも正面からの対応。残るのは C2 の言い方（4 倍の切り・λ = 4 の省略・R3-u の非対称・N の範囲）で、文の限定で消える。陰性対照（m2）は望ましいが受理の条件にしない。

## 6. 読めなかった範囲・注入の疑い
付録 A・B・C・E・多くの生成の表・references.bib は読んでいない。事前登録は grep の 2 か所。接地は grep の周辺。utility-r0 の列は推定（0.81 は再計算で一致）。注入の疑い: なし。
