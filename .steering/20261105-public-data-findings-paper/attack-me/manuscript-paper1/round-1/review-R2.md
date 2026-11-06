# review-R2（manuscript round 1・評価の実務の査読者・応答をメインが保存）

総合: major。注入の疑い: なし。読んでいない: references.bib の全文（grep のみ）・README・deviation-1・notes 2 本・conditions・探索の JSON 4 本・文献の記録 2 本・confirm_holdout.json の 714 行以降の区間・事前登録の全文（grep のみ）。

## 接地
- G1 Gardner & Brooks 2018: "Use statistical testing for model evaluation. Use tests for use with the prediction architecture in an experiment."
- G2 同: "The effects of the magnitude of observed differences, the uncertainty of estimates, and the number of data points should be separable in model evaluation."
- G3 同: "Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction"
- P1 Pelánek 2015: "the AUC metric should not be used (as the only metric) in cases where we need absolute values of predictions to be well calibrated."
- P2 同: "To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."
- P3 同: "Predictive ability of student models is not an end in itself, but mainly a mean to improving behaviour of educational systems and for getting insight into the learning process."

## 評価表
a 3（結論の "no basis for a seconds-scale trigger" が検定した時点 u より広い・漏れの後の確認であることを要旨と序論が伝えない）／b 3（全組を数える重みで有効 50.5・推定器の陽性対照なし・較正は有効 97 の見た書き手）／c 2（推定器は非公開の自作・手順の検出力の実例なし・比べの分析なし）／d 3（但し書きの逐語の繰り返し・要旨が重い）／e 3（コード未定・係数の数値が無い・申告の "in all sections" が粗い）／f 4（打鍵から情意・離脱を検出する EDM の系譜〔Bixler・D'Mello・Epp〕が無い）

## 指摘
- [major] 検定した時点（u）と主張する契機の時点のずれ: conclusion「These signals gave no basis for a seconds-scale trigger before stalls in character production.」・design「The intended use is a trigger that fires during a pause」・data「47% of stalls contained a run ... inside the pause」。休止が 2 s に達した後の情報は検定していない（停滞の中で u の後に上がる 0.135→0.193）。解消: 結論・要旨・考察を「u までの 30 秒の変化」に限る（u+2 s の比べを [E-H] で足してもよい）。自信 高。
- [major] 推定器・コード・推定の行の公開が未定: abstract「[repository to be added before submission]」・discussion Materials・limitations。推定器の行列・基準値・関与の軸の重みの数値が本文にも補足にも無い。解消: 公開を確定、公開できなくても全係数の表を補足に・推定の行を公開。自信 高。
- [major] 持ち帰れるものが手順に限られ、手順の検出力の実例が無い: results「We did not compare the learners with the estimator's signals.」・limitations「the positive-control gate was applied only to the learners」。学習器（0.567）は推定器の信号（0.487〜0.489）より高く、推定器の側が弱いという読みを支える。解消: 同じ組・同じ統計量で推定器の信号と学習器を並べる記述と、推定器の信号に既知の差を埋め込む陽性対照。自信 中。
- [major] 「確認」の情報価値が要旨と序論で過大: supplement「an output of a pre-freeze computation leaked the constants ...」・prereg P10「a confirmation made after the direction in seen writers was known, so it is not written as a test of a prediction that could fail.」・abstract「The test was preregistered on a random holdout」。解消: 要旨と序論に「見た書き手の向きを知った後の、同じ母集団での確認」と 1 句。自信 高。
- [minor] 要約の重みが停滞の数のほぼ二乗（results「each with up to five controls, for 709,352 pairs」・補足の分母 |S||K|）。解消: 全組を数える定義と重みの帰結を 1 文、書き手均等の版を主の文の中で。自信 高。
- [minor] 較正が取り置きより有効な書き手の多い条件（補足「97 of 312 ... 50.5 of 139」）。区間の端と帯の端の距離（約 0.05）も書く。自信 中。
- [minor] 閾値の表の数値 2 つが出どころと合わない: 補足「19.3%, 9.3% and 5.3% for the friction axis」（JSON 0.052481 → 5.2%）・書き手ごとの中央値の対照「19.5%, 9.6% and 4.6%」（exceed_median 0.04545 → 4.5%）。自信 高。
- [minor] 「the rise in an unmatched comparison was not replicated」の rise が何を指すか分からない（見たデータでも上がりは無かった）。解消: 何の上がりかを書き、定型の文言は S1 へ。自信 中。
- [minor] 学習器の結果の書き方が控えめすぎる（discussion「the relation to the upper end of the band was undecidable」・LR 0.5497〜0.578・θ×1 で 0.5519）。解消: 区間の位置をそのまま書き、(b) を「データと整合的」と。自信 中。
- [nit] 見た書き手の人数（319・312・316）の出どころが本文に無い（487−146=341 との差）。S2 に 1 文。自信 高。
- [nit] 生成 AI の申告の "in all sections"（規程は "mention precisely all sections or subsections"）。自信 中。
