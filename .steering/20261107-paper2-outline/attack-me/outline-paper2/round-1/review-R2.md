# review-R2（outline round 1・教育データの検出・予測のモデルの評価の実務の立場）

## 1. 接地
- G1 Gardner & Brooks 2018 (gardner2018.txt:19)「Use statistical testing for model evaluation.」(216-217)「this approach naı̈vely assumes that any differences observed must be due to genuine differences in model performance (and not, for instance, random variation)」
- G2 Gardner (25-26)「Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction architectures, and model evaluation in published work.」(733)「which provides no basis for comparison for future work that attempts to replicate these findings on new data.」
- G3 Pelánek 2015 (613-614)「To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results.」
- G4 Pelánek (623-625)「models differ only slightly in a summary metric, but their predictions are not well correlated, i.e., individual predictions are actually quite different ... In such a case the model difference may be of significant practical importance.」
- G5 Pelánek (658-663)「The choice of suitable metric depends on the intended use of a student model. ... Such discussion or specific arguments for a particular choice of metric should become standard part of papers」

## 2. 評価表
a 3（数値は judgement.json・notes と一致。φ の逆転は 1.5 の閾値に、一致は入れ子と不一致を区別しない指標に、順位は不確かさなしに依る。C4 は振っていない推定器の量を混ぜる）／b 3（範囲の妥当性の根拠が薄い・率に区間が無い・0.5・±20%・1.5 の線そのものが分析者の選択）／c 2（下流への影響を測っていない・実務の比べは同じ研究の中の群）／d 4／e 3（論文 1 との重なりの扱いが S9 の 1 行・CS1 が集計値だけの再現の書き方）／f 3（新しさのカードがやり残しとした最も近い先行〔Hart ら・Edwards ら SIGCSE 2022・Khalil & Ebner・Robitzsch 2022〕が無い・原典未登録）

## 3. 指摘
- [major] 順位の入れ替わりと比の幅に不確かさが無い（outline.md:35・:43）。c3_multiverse.json の rate_pooled は点の値だけ。11 通りの除外は 1 組だけの事後の手当て。G1。解消: 各通り・各データの率に書き手単位の再標本の区間を付け、区間の重ならない順位の変化の数と比の区間を図 2 に。自信 高
- [major] φ の逆転は 1.5 の閾値と基準の値の近さに依る（:31・:45「CS1 2019 のまとまり 1.44 [1.35, 1.53]」）。実務は φ > 1 で判断。推奨 3 と線が噛み合わない。G5。解消: 1.5 の理由・区間の下端 > 1 による逆転の割合・閾値ごとの感度を S4。主張は φ が何倍動くか（3.82→2.82 以下）を主に。自信 高
- [major] 一致の指標は入れ子と不一致を区別しない（:27・:44）。例 W15_q0.95_net_replay・CS1 2019 は agree_b0_in_cfg 0.849・agree_cfg_in_b0 0.090 で基準をほぼ含む上位集合。G4 を支えるのは率の近い 11/63 だけ。解消: 両方向を別の軸に・主張の数は 11/63 に限る・51%〜80% は注記して補足へ。自信 高
- [major] 下流への影響が測られていない（:61・:58）。G3・JEDM の範囲。解消: (i) データにある外の変数（成績・提出・得点）との関係が 90 通りでどう動くかを 1 つ示す、または (ii) 読者の結びつけを記述の研究に絞り考察を弱める。自信 中
- [major] C4 は 2 種の量を混ぜ、推定の水準は M3 が成り立たなかった結果の言い換え（:46・conditions.md:69・judgement.json:14）。推定器は読者が再現できず値も 4.84〜6.39 と動く。解消: C4 を長さだけに・推定の水準は否定の結果として 4.4 末尾か S7、または C1 側へ。自信 高
- [major] 振る範囲が妥当であることの根拠が外の実務の定義に結びついていない（:13・:100）。G2。解消: 3.3 に各軸の値と先行研究で使われた値（2 秒の休止・CS1 の閾値・5 分と 30 分のセッション）の対応表・範囲の外の慣行（2 秒の固定 θ）の理由。自信 中
- [major] 最も近い先行が外枠に無い（:85・:86・novelty.md:77・outline-priors.md:48）。Hart らは同じ種類の CS1 打鍵データで閾値を扱う可能性。解消: 候補の本文を読んで柱 1・2 に入れ、Q3 の検索を済ませ S8 に範囲。自信 中
- [minor] 論文 1 との重なりの扱いが規程と二重盲検に対して設計されていない（:20・notes.md:103）。開けた取り置きも共有。解消: S9 に重なりうる値の表と主張が依らないこと・送付状で開示・本文では第三者の文献として引く。自信 中
- [minor] 長さの「残る」がありふれた結果でないことの説明が無い（:46）。実務で意味があるのは書き手の平均の信頼性が低いこと（ICC 約 0.03）。解消: 級内相関として出し、必要な人数・件数を換算・[V152] などと並べる。自信 中
- [minor] [条件]・[記述] の印が条件と食い違う（:19）。conditions.md:52 は 30・60・180 秒を事前に置いている。解消: 30・180 秒を [条件]（判定に使わない記述量）に。自信 高
- [minor] CS1 の追試の道が無い（:120）。解消: 3.1 に入手の手順と利用条件、公開元から得れば同じ集計が再現できること。自信 中
- [nit] 題の four datasets と分析ごとのデータ数のずれ（:8）。解消: 表 1 に分析ごとのデータの列。自信 中

## 4. 総合: major
見出しの数（89%・66%・51%〜80%）が不確かさの無い点の値・自分で置いた閾値・入れ子を数える指標に依り、命題が測る側にも当てはまる。持ち帰りは手順で、下流は示されない。最も近い先行が未読。構成は投稿に耐える。

## 5. 読めなかった範囲・注入
conditions-length90.md・c2_overdispersion.json・c3b_aligned_level.json・c1_lengths90.json・c1_decomposition.json・prep_summary.json と、judgement.json・c3_multiverse.json の後半・カードの通読・接地の残り・[Vn] の書誌・論文 1 は読んでいない。注入なし。
