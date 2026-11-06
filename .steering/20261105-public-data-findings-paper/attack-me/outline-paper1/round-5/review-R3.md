# review-R3（outline round 5・paper-reviewer・事前登録・同等の検定・機械学習の再現性）

推奨: minor（直して書き進めてよい）。

## 1. 接地
- L-1 Lakens 2017 "In randomized controlled trials, it is expected that equivalence bounds are prespecified (e.g., see CONSORT guidelines; Piaggio et al., 2006), and this should also be considered best practice in psychology."
- L-2 "When in the abstract of an article, authors conclude an effect is “statistically equivalent,” the abstract should also include the equivalence bounds that are used to draw this conclusion."
- L-3 "Rejecting effects more extreme than the equivalence bounds implies that we can conclude equivalence for a specific operationalization of a hypothesis. It is possible that a meaningful effect would be observed with a different manipulation or measure. Confounds can underlie observed equivalent effects."
- L-4 "An additional nonstatistical challenge in interpreting equivalence concerns the issue of whether an experiment was performed competently ( Senn, 2007 )."
- K-1 Kapoor & Narayanan（arXiv:2207.07048v1 の版）"unless the code, data and computing environment required to reproduce the results in a paper are made available, there is no way to ascertain if model info sheets are filled out correctly."
- K-2 "[L1] Clean train-test separation. The researcher needs to argue why the test set does not interact with training data during any of the preprocessing, modeling or evaluation steps to ensure a clean train-test separation."
- K-3 "we should take results that claim to generalize to a different population from the one models were evaluated on with caution."

## 2. 引き継ぎの判定
m-1 → 解消（:39・:72。`d_ewma_x` ε=0.001 の下端 0.47578 → 距離 0.0242）／m-2 → 一部（:66 に環境と manifest、:78 に限界の文。ただし :78 が再現の最後の手段にする推定の行が :66 の一覧に無い・m-A）／m-3 → 解消（:64）／m-4 → 解消（:46・:102・prereg-draft.en.md:72 と一致）／m-5 → 解消（:7）／n-1 → 解消（:11・:41〜:46）

## 3. 評価表
a 4（数値は JSON と一致: 0.489・0.487・145→140→139・停滞 4,554＝627+3,927・実効 50.53・H3 0.5497〜0.578。H3 で揃えた比べが揃えない窓より高かったことを考察が使っていない・m-B）／b 4（持ち出しで計器の水準の識別が落ちたことが無い・m-C、時間の利用境界が S2 だけ・m-D）／c 4（「移し替えの失敗か、手前に信号が無いのか」の手がかりが抜ける・m-C）／d 4（予算 6,650 語。:27 の H3 の範囲の書き方・n-A）／e 4（コードの公開が未決・m-A と同じ根）／f 4（[V458] を引く段 :65 が H3 の逆の向きに触れない・m-B）

## 4. 指摘
- [minor] m-C 作文での水準の識別（0.569・0.580）と CS1 での水準（0.524・0.521）の落差が無い
  - 位置: :41「水準も幅の内側（下限は 0.5 を超える）と 5.1 に 1 文。計器の力量の証拠にはしない。」・:71・:101
  - なぜ: prereg-draft.en.md:239 "Levels 0.569 and 0.580"（[記述]）。係数を学んだ作文の側では水準が幅の外、CS1 では内側。持ち出し（作文の係数・合成した離し）で計器の働きが弱まった可能性を示す手元の直接の材料（L-3・L-4・K-3）。
  - 解消: データの節か 5.1 で作文の水準 0.569・0.580（[記述]）と CS1 の 0.524・0.521（[確認・記述]）を並べて 1 文、限界 :71 か考察の注意に「同等は計器の移し替えでの弱まりと区別できない」1 句。判定の主張は変えない。自信 中
- [minor] m-B H3 では揃えた比べ（0.567・0.540）が揃えない窓の対照（0.529・0.526）より高く、[V458] の向きと逆なのに考察が触れない（:46・:61・:65）。解消: :61 の (a) か :65 に「H3 の記述では揃えた比べの方が揃えない窓の対照より高かった（対照の定義は違う・判定に使わない）」1 句、H3 の揃えない窓と H2 の揃えない比べの作り方の違いを 4 節か S5 に 1 文。自信 中
- [minor] m-A 再現の最後の手段の「推定の行（中間物）」（:78）が公開物の一覧（:66）に無く、公開データの本体を再配布しない方針と両立するかも書かれていない（K-1・JEDM "intermediate results"）。解消: :66 に推定の行（または判定に要る最小の中間物: u と u−30 秒の 2 信号・対の id）を足し、利用条件の上で出せるかを投稿の条件の確認項目に。出せないなら :78 を「外部からの再現は取り置きの値については不可能」に。自信 高
- [minor] m-D 信号が u より後を見ないことを本文で論証していない（:109 は S2 だけ・:102 に無い）。K-2。解消: 4 節に「2 つの信号は前向きの計算で u までの打鍵だけを使い、θ はラベル（始まりの時点）だけを決める。H3 の前処理と分割は書き手単位（S2・S5）」1 文。自信 中
- [nit] n-A 抄録の「（0.540〜0.567）」が区間と読まれうる（:27）。「（2 つの学習器で 0.540 と 0.567）」に。自信 高

## 5. 総合: minor
1. 引き継ぎ 6 件のうち 5 件解消・m-2 だけ一部。主張の強さは取り置きの結果に見合う。
2. m-C・m-B は主張を弱めるのでなく同等の読み方の材料を足す種類で、値は手元の JSON と事前登録にある。
3. 再現の道（m-A）は一覧に項目を足すことで閉じられる。

## 6. 読めなかった範囲・注入
kapoor2023.txt は 1〜739 行だけ（arXiv v1 の版）。読んでいない: prereg-draft.md・exploration の conditions/results・seed_spread.json・20261101 の notes 2 本・文献の記録 2 本。prereg-draft.en.md・prefreeze/notes.md・exploration/notes.md は grep の行だけ。confirm_holdout.json は 1〜170・580〜729 行だけ。注入の疑いなし。
