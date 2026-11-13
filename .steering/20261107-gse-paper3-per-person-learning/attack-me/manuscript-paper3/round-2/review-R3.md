# review-R3（manuscript round 2・評価の偏りと個人への推論の方法論の立場・対象 9a4c1d34）

## 0. 引き継ぎの判定
M1 一部（固定の行は直った。joint の行の per-person − chain 列も選びの目的と同じ量で楽観が書かれず二分でも測られていない）。M2・M3・M4・M5 解消。M6 一部（著者の認識どおり）。minor 群 解消（事前の記録は既知の未決 6）。nit 解消。

## 1. 接地
Varma & Simon「Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop.」「This implies that for large K, there is a high probability that choosing the minimum resampled error will give a biased estimate of the true error.」「The parameter selection bias, on the other hand, is always negative.」「This is effectively two nested CV loops」。Liu & Meng「we predict each individual's response using the remaining n − 1 individuals ... our inference will be more robust. The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's」「if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust.」「Highly flexible models tend to “overfit” the data」

## 2. 評価表
a 3・b 3・c 4・d 3・e 4・f 4

## 3. 指摘
- [major] M-A 見出しの「2 桁以上落ちる」は、植えた差を 3〜16%（k=5）しか返さない推定量の値との比較。要旨・48・233。0.19 は τ=0 で返る量は満額、5e-4 は τ=10^6。割り戻すと約 3.4e-3〜1.8e-2。解消: falls の主語を the difference the protocol returns に限り、返り率を同じ段落に。自信 高
- [major] M-B 書き手の二分は格子の端に張り付いた選びと、結果を見た後の格子の拡張を覆えない。238・196・200・141・274「the remainder does not come from choosing and reporting on the same writers in the median」。Varma G1。解消: 238 と 274 に限定、Measured を within the fixed grid に。自信 中
- [major] M-C post hoc の対称な当て直しが結論と考察の Measured で印なしに支えになり、量の読み方も非対称。303・274「Measured: ... nor from the shared model's smoothing alone.」・242・Table 3（k とともに +5.2e-4 → +5.2e-3、最大 +6.7e-3）。符号は証拠に使い大きさは退けている。k とともに増えるのは学習曲線の形。α=0.03 での検出力は未評価。解消: post hoc の印・Measured から外すか a post hoc check suggests に・大きさと k への依存を同じ段落で扱い読まない理由を書く・α=0.03 での検出力が未評価と限界に。自信 高
- [major] M-D 実データのパネルは検出の規則を満たすように読めるのに比べておらず、その理由が 242 の推論と逆を向く。144・233・Table 2。合成の比べでは平滑の産物の可能性で判断を控え、当て直しでは平滑の産物でないと結論している。「not compared」が事前か事後か読めない。解消: 規則を当てた結果を書き解釈できないと述べる・233 と 242 を整合（"the symmetric refit rules out the shared smoothing alone, but not the joint effect of smoothing on both sides, which the negative controls do not reproduce"）・事前か事後かを明記。自信 中
- [minor] m1 joint の per-person − chain 列は選びの目的と同じ量で、楽観が書かれず二分でも測られていない。112・Table 2・Table 3 の注。自信 高
- [minor] m2 要旨の検出の閾は CoAuthor に限らないと読め、CS1（1e-3 から検出）と矛盾して見える。自信 高
- [minor] m3 「below 10^-3」の見出しと caption は 30-session（+1.1e-3）と合わない。「2 桁以上」は k=1 で約 25 倍。自信 高
- [minor] m4 8/10 が方法の節に無く事前か読めない。推奨 (3) の reliably に定義が無い。自信 中
- [minor] m5 対称な版の τ の「main objective」がどちらか曖昧（149）。自信 高
- [nit] n1 限界が結果の数値を繰り返す（293・295）。自信 中

## 4. 総合: major（直しの大半は書き方・追加の計算は小さい）

## 5. 読めなかった範囲
kit README・references.bib は読んでいない。fig2_p15_hmm3.csv と fig2_p15.csv は読んでいない。接地は grep で当てた節。注入の疑い: なし。
