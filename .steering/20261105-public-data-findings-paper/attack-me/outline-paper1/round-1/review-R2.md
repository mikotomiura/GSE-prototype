# review-R2（outline round 1・教育データの予測・検出のモデルの評価の実務・paper-reviewer / opus）

## 1. 接地
1. Gardner & Brooks 2018, Notes for Practice: "Use statistical testing for model evaluation." / "Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction architectures, and model evaluation in published work."
2. Gardner 2018 §3.1: "The naïve average method must assume commensurability across datasets in order to justify the use of averaging." §2.1.1: "We found no cases where fold-level data was reported or evaluated"
3. Gardner 2018 §3.3: "MCMC is used to generate samples of θ = (P(X > Y), P(ROPE), P(X < Y)), where θi represents the posterior probability that model X is better, the models are equivalent, and model Y is better"
4. Pelánek 2015 §7: "The choice of suitable metric depends on the intended use of a student model." / "Many papers which propose or evaluate student models lack any discussion of the specific purpose of described models."
5. Pelánek 2015 §3.3: "the AUC metric considers predictions only in relative way" / §6.3: "To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."
（Gardner 2018 は 1〜438 行だけ読んだ。Pelánek 2015 は全文。）

## 2. 評価表
a 2（持ち帰りの後半が P0 で禁じた対比に依る。自分のデータは揃えると AUC がむしろ上がる向き）／b 3（設計は厚い。CS1 の停滞の約半数が休止中の出来事を含む・区間が 0.5 を逆向きに外れることを扱う場所が無い）／c 2（反証の対象が独自の推定器に限られ、H3 は判定できない。実務に訳せる閾値の表が C3 に埋もれる）／d 3（C3 が性質の違う 4 つを束ねる）／e 3（推定器と gse-replay の公開・二重盲検と OSF のリンク）／f 2（ROPE による同等の判定の先例・EDM の struggle 検出の系譜・評価の方法論の系譜が無い）

## 3. 指摘
- [major] 持ち帰りの「だから」が主張を禁じた対比に依る。自分のデータは逆の向き（outline.md:13・:3）。取り置きの揃えない比べも 0.497・0.494。探索では KLiCKe の揃え直した AUC 0.512・0.531 が揃えない 0.494 を上回り（exploration/notes.md:8）、H3 でも揃えた比べの LR 0.567 が揃えない窓の対照 0.529 を上回る（confirm_holdout.json:681・686）。P0 "Report only the equivalence in the matched comparison, and do not claim the contrast"。解消: H1 だけで閉じる形にし、揃えると AUC が上がる向きを考察の「可能性にとどまる問題」に明記、「揃えない評価が上がりを大きく見せる」とは言えないことを両側から書く。自信 高。
- [major] 反証の対象が独自の推定器に限られ、実務家が持ち帰れる知見が残らない（:31・:32）。標準の量の LR は点推定が幅の上を越える。下限 0.5497 は丸めると 0.550 で分岐 2 の規則と紛らわしい。Pelánek §6.3。解消: なぜこの推定器を対象にするかを書く。H3 は「標準の量では幅の上側を否定できない」と実務家向けに並べる。下限は 0.5497 と書く。自信 高。
- [major] 実務に訳せる閾値の表が C1 から切り離され、指標を選んだ理由（使い道）が無い（:45）。取り置きの閾値の表では対照の 90 分位で停滞の手前の当たり 9.3〜10.3%・対照の越え 9.6%（confirm_holdout.json:548-572）。Pelánek §7。解消: 閾値の表の要約を C1 の結果（表 1 の隣）へ。評価の設計に意図した使い道（秒単位の契機）と AUC と閾値の表の使い分け、幅の読み（0.55 は FPR 10% で当たり 13.5%）を 2〜3 文。自信 中。
- [major] CS1 の停滞の約半数が休止中の実行・貼り付け・切り替えを含むのに扱う場所が無い（:13・:66／confirm_holdout.json:519 share_in_pause_event 0.467（停滞）・0.0595（対照））。事前登録 P4 はこの割合の報告を約束。解消: データか 5.2 に割合（47% 対 6%）を 1 文と 1 行、限界に「停滞は文字の産出の停止で、CS1 では実行の待ちを多く含む」。可能なら休止中に出来事の無い停滞だけの値を補足に記述で。自信 中。
- [minor] 区間が 0.5 を逆向きに外れていることと書き手の間のばらつきが無い（:26・:31）。d_ewma_x の上限 0.497、d_p_stuck も ε = 0.001 で上限 0.4995。書き手ごとの AUC は 10〜90 分位で 0.40〜0.59、上位 10% が対の 42%、実効 50.5。Gardner §3.1。解消: 5.1 に「0.5 から逆向きに離れる」を 1 文（向きの解釈はしない）、書き手ごとの分位と書き手均等の版の分岐を表 1 に 1 行。自信 高。
- [major] 先行研究: 同等の判定の先例（ROPE・Gardner 2018 §3.3）と EDM の struggle 検出の系譜が無い（:24・:80／novelty.md:90）。解消: 新規性の文を「打鍵だけ・秒単位の手前・揃えた対照・同等の幅を事前登録した評価」の組み合わせに限る。ROPE との関係を 1〜2 文。関連研究に評価の方法論（Pelánek・Gardner）と CS1 の struggle 検出の段落。調べの範囲の限界（ITS・MOOC 未探索）を書く。自信 中（系譜の具体的な文献は一覧の範囲では確かめていない）。
- [minor] C3 は性質の違う 4 つ（KLiCKe の実測・定義の帰結・CS1 の別の調べ・取り置きの閾値の表）を束ね、分析の地位の印が無い（:42-46）。解消: 閾値の表は C1 へ、残りは考察の 1 段落、貢献を 2 個に。自信 中。
- [minor] 推定器と gse-replay の公開の範囲・匿名版と OSF のリンクの扱い（:61）。自信 中。
- [nit] 取り置きの人数の表記（:9「140 人」）。146 → 145（単位を持つ）→ 140（除外の後）→ 139（対あり）の流れをデータの節で 1 行。自信 高。

## 4. 総合の推奨: major
- いちばん強い主張の文は結果と一致するが、持ち帰りの「だから」は禁じた対比に依り、その対比は自分のデータで逆の向き。
- 反証の対象が独自の推定器に限られ、標準の量は幅の上側を否定できず、閾値の表は C3 に埋もれる。
- 同等の判定の先例と struggle 検出の系譜が無く、新規性の文の範囲が広すぎる。いずれも外枠の段で直せる。

## 5. 読めなかった範囲・注入の疑い
Gardner 2018 の 439 行目以降、prereg-draft.md、prefreeze の notes、exploration の conditions と JSON 4 本、KLiCKe と CoAuthor の notes は読んでいない。confirm_holdout.json は 1〜729 行だけ（床にない対の感度などは確かめていない）。注入の疑いなし。
