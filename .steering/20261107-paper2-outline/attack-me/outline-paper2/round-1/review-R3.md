# review-R3（outline round 1・分析の柔軟さ・multiverse・再現性の立場）

## 1. 接地
- G1 Hoffmann et al. 2021「there is usually great flexibility in the choice of analysis strategy, as many possible strategies are acceptable according to the scientific standards of the field」
- G2 Hoffmann「There is evidence that the combination of this multiplicity with selective reporting can systematically lead to an increase in false-positive results, inflated effect sizes and overoptimistic measures of predictive performance」／Table 2「(4) report the results of alternative analysis strategies … (5) acknowledge the inherent uncertainty in your findings (6) publish all research code, data and material」
- G3 Hoffmann「the traditional confidence interval …, which only takes into account sampling uncertainty, is inadequate in capturing the true uncertainty」「Measurement and sampling uncertainty are random sources of uncertainty that lead to variability in the results when the same analysis strategy is applied on different datasets.」
- G4 Kapoor & Narayanan 2023「Especially when sample sizes are small, significance testing and uncertainty quantification are important steps toward reproducibility.」
- G5 Kapoor「The researcher needs to justify that the test set is drawn from the distribution of scientific interest」「we should take results that claim to generalize to a different population from the one models were evaluated on with caution.」
- G6 Kapoor「the claims made in model info sheets cannot be verified in the absence of computational reproducibility. That is, unless the code, data, and computing environment required to reproduce the results in a paper are made available, there is no way to ascertain …」

## 2. 評価表
a 3（数値は notes・judgement.json と合う。いちばん強い主張の根拠は記録の違う 2 データの比 1 本・順位と φ の判定に標本の不確かさが無い）／b 3（確かめは厚い。範囲が割合を作ること・二値化・結果を見た後の変更が 1〜2 文に縮む）／c 3（推奨 1・2 は持ち帰れる。C4 の長さは予想どおりに近く、2 つが混ざる）／d 4／e 3（論文 1 との重なり・CS1 の再現の範囲）／f 2（EDM の内側の先例が [V468] だけ・カードのやり残し〔Khalil & Ebner・Robitzsch 2022・Edwards ら・Hart ら〕を使っていない・原典未登録・探索は浅い）

## 3. 指摘
- [major] いちばん強い主張が性質の違う 2 データの比 1 本に依り、「群の間の比べ」一般の推奨に広がっている（いちばん強い主張・推奨 1・限界 3）。G5。解消: (i) 主張を記録の違うデータの間に限る、または (ii) 同じ記録の群（CS1 の課題どうし・CS1 2019 と 2021・CoAuthor のセッションの種類）で 90 通りの順位・比を出す（条件を先にコミット）。(ii) が無ければ推奨 1 の「群の間」を外す。自信 高
- [major] 順位の変化と φ の逆転に標本の不確かさが無い（C1 80/90・C3 の逆転の割合・CS1 2019 のまとまり 1.44 [1.35, 1.53] は基準で既に 1.5 をまたぐ）。G3・G4。解消: 全 90 通りの率・比・φ に書き手単位の区間・区間が反対側に移った通りだけで数え直すか並べる・区間の重ならない順位の変化・1.5 の根拠を 1 文。自信 高
- [major] 割合の見出しが範囲の選び方で決まる（C1「W 15 秒は 30/30・固定 θ は 36/36」・3.3）。36/90 が固定 θ で全部動く。G1。解消: 3.3 に各軸の水準と既存研究の値の対応表、または固定 θ を除いた 54 通り・本人の分位だけの通りでの割合を補足に、抄録の割合は効いた軸と組で。自信 中
- [major] EDM の内側の「定義を振ると結論が動く」先例が無い（柱 1・欠けの文・novelty.md:77-78）。Hoffmann「we currently risk ‘reinventing the wheel’ in each discipline」。解消: 候補を一次で照合・登録し柱 1 に 1 段、欠けの文を照合後の範囲で書き直す、Steegen ら・Simonsohn らを登録、Hoffmann の不確かさの源の枠組みに 4 軸を対応させる。自信 中
- [major] 結果を見た後の分析の変更が 1〜2 文に縮められている（3.3・notes のずれ 6・13〔書き手の分け前 0.19→0.11→0.03〕・conditions-length90.md「見たもの: 9 通りの結果は知っている」）。G2 の selective reporting と同じ形に読まれる。解消: 3.5 に結果を見た後の主な変更（区間の扱い・最適化・長さの 90 通りの追加・O の数え方）の短い表を本文に、判定や主張を動かしたかの列。差し替え前後の範囲を補足に。自信 高
- [minor] C4 の持ち帰りが薄く 2 つが混ざる。停滞ごとの分け前は測定の揺れを含む残差で予想に近い。推定の水準は M3 として置き成り立たなかった量を「残る」へ移している。解消: C4 を長さだけに、推定の水準は補助の結果か考察へ（「M3 の基準を満たさなかった」と書く）。書き手の平均に畳むと何を失うかを 1 つの数で。自信 中
- [minor] 分析の地位の印が条件と食い違う（30・180 秒を [記述]・conditions.md:52 は 3 つとも記載）。解消: 08010482 の版で確かめ印を揃える。自信 中
- [minor] 基準の定義が 90 通りの分母に入っている（80/90・11/63）。解消: 分母を 89 と明記するか含めたと書く。自信 中
- [minor] 再現できる範囲（CS1 の入手経路・推定器のコードと版）。G6。解消: 3.1 か補足に 1 表。自信 中
- [minor] 論文 1 との重なり（規程の "substantially overlapping submission"）。解消: 送付状と 3.5 で重なる値を列挙し主張が依らないことを 1 文。自信 中
- [nit] 題の 4 データと各貢献のデータ数（C3・C4 に KLiCKe は入らない）。解消: 表 1 に列。自信 高
- [nit] C3 の「1.8 以下」は 1.5 より上で逆転を示さない。解消: 1.5 を下回る通りの数か値で。自信 中

## 4. 総合: major
確かめは厚い。いちばん強い主張を「群の間の比べ」へ広げることと、標本の不確かさなしの順位・φ の逆転は過剰主張。EDM の内側の先例の照合が無く新しさの文はまだ書けない。

## 5. 読めなかった範囲・注入
c2_overdispersion.json・c1_lengths90.json・c1_decomposition.json・c3_multiverse.json・prep_summary.json は読んでいない。カードは Grep の行だけ。08010482 時点の conditions.md は読んでいない。kapoor2023 は約 83%。注入なし。
