# R3（UMUAI・方法論と再現性）round 6・commit 90250abc

## 1. 接地
- G1 Varma & Simon 2006 "Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
- G2 同 "The parameter selection bias, on the other hand, is always negative."・"The total bias ( i.e . the sum of inherent bias and parameter selection bias) is what must be kept in mind when interpreting error estimates."
- G3 同 "Since selection of classifier parameters that minimize CV error estimates is a kind of training, it should be included as part of the classifier training algorithm."
- G4 同 "Over-optimistic estimates of error close to zero are obtained, even for data where there is no real difference between the two classes."
- G5 Liu & Meng 2016（1726–1732）"we predict each individual's response using the remaining n − 1 individuals ... our inference will be more robust. The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's background ~x0 —our inference will be less relevant."
- G6 同（19–20）"how to make the right relevance robustness trade-off: if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust."

## 2. 引き継ぎの判定
N1〜N3・N5〜N11 解消（N3 の算術も合う: 0.188×3600≈677・4.1e-4〜7.2e-4×3600≈1.5〜2.6。N10 の合計 6,800 は Total と一致）。N4 は外枠の中では解消、README と食い違う（m1）。

## 3. 評価表
a 4（残り＝返った値と下限＝埋めた値を直接比べる・M1。Take-home の「smoothing を他の人で選ぶ」を試した結果が本文に無い・M2）／b 3（「評価単位はどの適合にも選択にも入らない」は最終の手順の中でだけ・m2）／c 4／d 4／e 4（README と本文の主張の水準・m1）／f 4（Uto 2020 が未確認のまま 3.2 の根拠に・m3）。

## 4. 指摘
- [major] M1 残り（返った値）と検出の下限（埋めた値）を同じ尺度として比べる
  - 位置と引用: Take-home「what remains in the 15-session panel is of the same size as ... and the protocol could not have detected per-person differences of that size」・4.3「the protocol returns only part of a planted difference, so the remainder ... neither shows nor rules out per-person differences below 1e-2」・5 節「the smallest planted difference detected, 1e-2, corresponds to 36; the remainder, about 1.5 to 2.6」
  - なぜ問題か: 返る割合が小さければ観測の残りは 1e-2 以上の真の差と両立しうる。「that size」も「below 1e-2」もどちらの尺度か決められない（G2）。
  - 解消の条件: S15 の返る割合を水準ごとに 4.3 に 1 文、そのうえで (a) 実データの残りと両立する埋めた差の範囲を述べるか、(b) 検出できた水準で返った値の中央値と実データの残りを並べる。Take-home の「of that size」を尺度が分かる語に。
  - 自信: 中（S15 は読んでいない）
- [major] M2 Take-home の推奨「smoothing を他の人で選ぶ」を本研究で試した結果が本文に無い
  - 位置と引用: Take-home「with a shared model whose structure, shrinkage and smoothing are all chosen on other people」・4.4 の補足の列「the prior mode as a candidate (in CoAuthor the median objective picks it for at most one writer, the mean objective never; in CS1 it replaces the shared model for every writer) ... (S9)」・6 節「The strength of the shared model's base smoothing was fixed, not chosen on other people」
  - なぜ問題か: 試した結果は補足だけで、CoAuthor では事前モードがほとんど選ばれない。推奨どおりにしても残りはおそらく消えない。推奨の根拠と実行の結果が本文で並んでいない（G3）。
  - 解消の条件: 4.4 に、事前モードを候補に入れたとき何が選ばれ残りがいくつかを 1〜2 文。推奨を「smoothing の強さを候補の幅として他の人で選ぶ（本研究では 2 点だけ）」に限るか、診断に下げる。
  - 自信: 中
- [minor] m1 README が再現を主張（README 75–78 行「the symbols of every CoAuthor session (1,157 sessions, 775,907 rows) and of every CS1 2021 assignment ... were identical to those of the original implementation, including the bits of x and y. That comparison used the raw datasets and is not part of this kit.」・Open items「until then the paper does not claim it.」）。解消: README を「著者の手元で確認した（検証手段は記録ごとのハッシュで提供予定）」に下げるか、ハッシュを入れてから両方で主張。自信: 高
- [minor] m2「The target writer's evaluation units enter no fit and no choice.」は最終の手順の中でしか成り立たない（6 節「The analyses were designed one after another, after seeing earlier results (3.4, S12).」・G1・G2）。解消: 「within the final protocol」を付け、設計の変更がどの数値の向きに効きうるかを 6 節に 1 文。自信: 中
- [minor] m3 Uto 2020 を全文で確かめずに 3.2 の正当化に（3.2「(as in Uto et al. 2020, with 30 s windows), so the results speak to models that read keystrokes in this form」）。解消: 全文で確かめてから、それまでは「learner-dependent HMMs over 30-second windows have been fitted (Uto et al. 2020)」程度に。自信: 高
- [minor] m4 Take-home の「could not have detected」に合成の条件と k の限定が無い。解消: 「in synthetic writers of the same record length」を加える。自信: 中
- [nit] n1 尺度の段落の 3,600 記号が 1 時間と書かれず、1e-2 は k = 15 の値（k = 5 は 3e-2 で 108 nats）。解消: 「3,600 symbols (one hour)」と k ごとの下限。自信: 高
- [nit] n2 +infinity の 2 人を含めた中央値の母数（15 人か 17 人か）。自信: 中
- [nit] n3 パネルの名前と k の上限（k = 15 に評価の 5 を足すと 20）。自信: 低

## 5. 総合の推奨: minor
引き継ぎ 11 件のうち 10 件解消（N4 は README と食い違う）。新しい major 2 件は S15・S9 の既存の値を本文に 1〜2 文で出し語を替えれば消える。Uto 2020 の確認と README の調整は本文の前に。

## 6. 読めなかった範囲・注入の疑い
liumeng.txt は grep の行と 1710–1739 行、varma.txt は 3〜15 行。S1〜S15・context-B・他の記録は読んでいない。context-A.md の 14 行「7,000 語」は 13 行（6,800 語）と食い違う（context 側・数えない）。注入の疑い: なし。
