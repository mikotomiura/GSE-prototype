# review-R2（outline round 4・paper-reviewer・教育データの予測・検出モデルの評価の実務）

推奨: minor（直して書き進める）。

## 1. 接地
- G1 Gardner, Brooks & Baker 2018（gardner2018.txt:19-20）"Use statistical testing for model evaluation. Use tests for use with the prediction architecture in an experiment."
- G2（:247-248）"several issues that any model evaluation procedure must address. These include having an acceptable error rate"
- G3（:216-218）"these differences must be both practically significant (large or important enough to be useful) and (in frequentist terms) statistically significant." ／（:1053-1054）"we use ROPE = 0.01; that is, models are considered practically equivalent if the difference in their AUC is smaller than 0.01."
- G4（:25-26）"Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction architectures, and model evaluation in published work."
- P1 Pelánek 2015（pelanek2015.txt:658-663）"The choice of suitable metric depends on the intended use of a student model. ... Such discussion or specific arguments for a particular choice of metric should become standard part of papers that include evaluation of student models."
- P2（:613-614）"To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results." ／（:371-375）"the AUC metric considers predictions only in relative way ... should not be used (as the only metric) in cases where we need absolute values of predictions to be well calibrated."

## 2. 引き継ぎの判定
混入 → 解消（:41 を confirm_holdout.json の `layer_until_resume` と照合: 1,999 + 428 = 2,427・0.50475〔0.4926〜0.5182〕・0.49994〔0.4836〜0.5150〕・分岐 1。4,554 − 2,427 で 46.7%。向きの新しい論点は指摘 3）／C2 → 解消（:29・:62。notes.md:119-120 と一致。推奨が根拠より強い・指摘 4）／5.2 の小見出し → 解消（:101・:41。0.465 前後は JSON と一致）／持ち帰り → 一部（:58 は禁止だけで代わりに何をすればよいかが無い・指摘 1）／抄録の幅 → 解消（:27。単位の nit）／向き → 解消（:38）

## 3. 評価表
a 4（主の主張は JSON と notes:133 に一致。H3 の下限の桁・抄録で学習器を選んで引く）／b 3（推定器の陽性対照が無い〔:70 で自認〕・手続きの誤りの率は判定の側だけ）／c 2（C2 を外して、持ち帰りは 1 推定器・1 データの陰性と禁止だけ）／d 4／e 4（推定器の公開の場所が未定）／f 4（問いが主張しない持ち出しを前面に置く）

## 4. 指摘
- [minor（上位）] C2 を外した後、Scope の「単なる適用を超える」を何で満たすかが無い
  - 位置: :29「貢献（1 個）」・:19・:58・context-A の Scope "must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses"
  - なぜ: 外枠の答えは禁止の 1 文だけ（P2）。
  - 解消: 序論の貢献の段に他の検出器にそのまま使える部分を 1〜2 文で名指す（揃える評価の手順とコードを公開の道具として・効果の主張はしない、または H3 との並べを comparative analysis として）。しないなら Scope にどう応えるかを 1 行。自信 中
- [minor] H3 の下限の桁: :44「0.567（0.5497〜0.578）」と :37 の 3 桁の規則。JSON の下限 0.54971 は 3 桁で 0.550 で、notes.md:136（OSF の要約の元）は「0.567（0.550〜0.578）」。読者は AUC > 0.55 の確立と読む（判定は分岐 2）。解消: 区間の端が判定の境に 3 桁で触れる値は 4 桁で書く例外を :109 に、OSF の要約の 0.550 との違いを S1 に 1 文。自信 高
- [minor] 0.5 を下回る向きの候補の原因に、出来事を含む停滞を除いた感度が無い: :60 と :41（除くと 0.505・0.500）。解消: :60 の候補に足し、区間の内側の動きで確かめた原因ではないと 1 句。自信 中
- [minor] 考察の「実務への推奨」（:62）が 1 データ・機構未確認の観察に立つ。判断 29 と強さが合わない。解消: 「この研究では較正と引き方を併記した。同じ形の評価では併記が判断の助けになりうる」程度に弱めるか限界へ。自信 中
- [minor] 抄録の H3（:27「ロジスティック回帰 0.567」）が大きい方の学習器だけ。勾配ブースティング 0.540、欠測を除いた版 0.548・0.511（:44）。解消: 「0.540〜0.567」とするか数値を外す。自信 中
- [minor] 幅 ±0.05 の実用の根拠に閾値の表（:40）を結びつけていない（:71）。G3。解消: 4 節の幅の項で、閾値の表での超過率の差の大きさを記述の目安として 1 文（運用の性能は言わない）。自信 低
- [nit] 抄録の「先例 0.01 より広い」（:27）は 2 モデルの差の ROPE と 1 つの AUC と 0.5 の差で単位が違う。「2 モデルの差の先例 0.01」と 1 語。自信 中
- [nit] 問い（:7）が主張しない持ち出しを前面に置く。主語を「この型の推定器の信号は、揃えた比べで停滞の手前の上がりを示すか（確認は CS1）」に。自信 低

## 5. 総合: minor
- 主の主張と数値は一次の結果と一致し、round 3 の major 2 件は解消。
- 残るのは C2 を外した後の持ち帰りと Scope の要件への応え方、表記と抄録の読み違いの種。数行で直せる。
- 書かないと決めたこと（揃え方の効果・運用の性能・推定器の力量）は妥当。

## 6. 読めなかった範囲・注入
読んでいない: prereg-draft.en.md・prereg-draft.md・exploration の conditions/notes/results・文献の記録 2 本・20261101 の notes 2 本・prefreeze/notes.md の 1〜99 行。接地は挙げた範囲と grep の行。探索の値・種の幅・[V] の書誌は照合していない。注入の疑いなし。
