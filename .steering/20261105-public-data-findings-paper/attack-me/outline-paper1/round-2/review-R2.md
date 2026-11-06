# review-R2（outline round 2・paper-reviewer・教育データの予測・検出モデルの評価の実務）

推奨: minor。持ち帰りの 1 文が結果と食い違い、同等の主張が幅の取り方に依ることが書かれていない。

## 1. 接地
- G1 Gardner & Brooks 2018（Notes for Practice）"Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction architectures, and model evaluation in published work."
- G2 Gardner 2018 §3.1 "these differences must be both practically significant (large or important enough to be useful) and (in frequentist terms) statistically significant."
- G3 Gardner 2018（実験の節）"we use ROPE = 0.01; that is, models are considered practically equivalent if the difference in their AUC is smaller than 0.01."
- P1 Pelánek 2015 §7 "The choice of suitable metric depends on the intended use of a student model." ／ "Many papers which propose or evaluate student models lack any discussion of the specific purpose of described models."
- P2 Pelánek 2015 §3.3 "the AUC metric should not be used (as the only metric) in cases where we need absolute values of predictions to be well calibrated"
- P3 Pelánek 2015 §6.3 "To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."

## 2. 評価表
a 3（C1 の数値は confirm_holdout.json と一致: 0.489・0.487 と区間、水準 0.524・0.521、床 61%・65%、休止中の出来事 46.7%・6.0%、実効 50.5、閾値の表 10.3%・9.3%・9.6%、書き手ごとの分位。持ち帰りの第 2 文が区間の向きと矛盾）／b 3（幅 ±0.05 への依存・X8 の取り置きでの実行と対の減り）／c 2（実務の材料は閾値の表だけ・推奨 (1) は揃えが結論を変えると示さずに手順を勧める・C2 の根拠が弱い）／d 4（予算と節番号の食い違い）／e 4（コードの公開の場所が未定）／f 3（ROPE の幅 0.01 との差を書いていない・AUC に TOST を当てた先例は未探索〔記録のやり残し〕）

## 3. 引き継ぎの判定
1 だから → 解消（第 2 文に新しい問題）／2 反証の対象・H3 の下限 → 一部（EDM の読者がなぜ気にすべきかに未回答）／3 閾値の表 → 解消（:31）／4 休止中の出来事 → 解消（:34）／5 向き → 一部（持ち帰りが列と逆を言う）／6 ROPE と系譜 → 一部（幅 0.01 と ±0.05 の違い）／7 C3 → 解消（:57）／8 公開 → 一部（外枠の段で許容）／9 人数 → 解消（145 → 140 → 139 は JSON と一致・146 は未照合）

## 4. 指摘
- [major] 1 持ち帰りの第 2 文が区間の向きと食い違い、記述の副の信号を性能の根拠に使う
  - 位置: :13「同じ推定器の水準は 0.5 から離れたが、手前の上がりは離れなかった。」・:29・:64「（水準では 0.5 から離れた）」
  - なぜ: 上がりの区間は d_ewma_x [0.4758, 0.4975]・[0.4758, 0.4974]、d_p_stuck（ε = 0.001）[0.4787, 0.4995] で、4 つのうち 3 つが 0.5 を下側に外す。水準 0.524（0.510〜0.537）も幅の内側で、事前登録 P5 は水準を "Secondary ... (descriptive)" とする。記述を確認のように読ませ、力量も示さない。
  - 解消: 消すか「水準は 0.5 をわずかに上回り（下限 0.510）、手前の上がりは 0.5 をわずかに下回った。どちらも幅の内側」。限界は「水準も幅の内側なので、計器の力量の証拠にはならない」。自信 高
- [major] 2 同等の結論が幅 ±0.05 に依ることを、分野の先例 ROPE 0.01 と並べていない
  - 位置: :43「ROPE との違いは 1〜2 文: ROPE は 2 つのモデルの差を比べる処方で、本研究は 1 つの推定器の AUC と 0.5 を比べる」・:65
  - なぜ: 先例は AUC の差 0.01（G3）で本研究の幅はその 5 倍。幅 0.01 で読むと d_p_stuck の下限 0.479 は 0.49 を下回り同等は立たない。G2。
  - 解消: 柱 3 か評価の設計に 1〜2 文（先例の幅 0.01・点推定と 0.5 の距離 約 0.011〜0.013・幅を狭めれば同等と言えない）。抄録に「事前に置いた広い幅での」の限定。自信 高
- [major] 3 C2 の実例が弱い（:44 の (3)・:46・:58 の (1)）。(3) は定義から自明、(2) は手続きの記録、実質は (1) の較正だけ。Gardner は方法の違いで結論が変わる事例で方法を勧めた。解消: C2 を (1) の較正に絞り「書き手の再標本の区間で同等を言うと誤って同等とする割合が名目を超えうる。その較正の手順」を前に。推奨 (1) は先行の値と比べる相手を明示するためと限るか、可能性の側へ。自信 中
- [minor] 4 X8 は取り置きを確認の後に使った探索なのに確認と混ぜた印（:33）。3 区分の対 394,394 は主の 709,352 から約 44% 減。解消: 「[確認・感度] 境界か否か」と「[探索・取り置きを確認の後に使用] 3 区分」に分け、S3・S7 に対の数。自信 高
- [minor] 5 出来事の層（記述）の結果が無い（:34・:32）。H1_event_layer_described は 4 つとも分岐 1（0.495・0.496）・実効 35.7・対 90,185。解消: 表 1 の脚注か S3 に 1 行（[記述]）。自信 中
- [nit] 6 閾値の表を pooled だけで書く（:31）。書き手ごとの中央値は 9.1%・8.7% で対照の 9.55% を下回る。解消: S8 に中央値、本文は「どちらの集計でも偶然と同程度」。自信 高
- [nit] 7 予算と節番号の食い違い（:52「7・700 語」・:62「8・350 語」と表 :94-95）。自信 高

## 5. 総合: minor
1. C1 の数値は一次の JSON と一致し、round 1 の major 5 件のうち 3 件は解消。
2. 残る major 3 件は新しい計算なしに外枠の書き方で直せる。
3. 2 と 3 を直さないと「独自の推定器の、広い幅での陰性の結果」としか読めない。

## 6. 読めなかった範囲・注入
読んでいない: gardner2018.txt の 439 行目以降（Grep の行だけ・指摘 2 の引用は Grep の行 1053-1054）・prereg-draft.md・prefreeze/notes.md・exploration/conditions.md・explore_coauthor/cs1_2021/klicke.json・seed_spread.json・novelty の記録・20261101 の notes 2 つ・confirm_holdout.json の 590 行目以降（Grep を除く）・prereg-draft.en.md は 80〜174 行と Grep。照合していない値: KLiCKe と CoAuthor・5.2% の内訳・人数 146・H3・H2。注入の疑いなし。
