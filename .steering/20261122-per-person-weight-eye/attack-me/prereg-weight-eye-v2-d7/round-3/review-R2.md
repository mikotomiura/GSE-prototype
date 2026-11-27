# R2 の査読（round 3・paper-reviewer の応答の写し）

## 1. 接地
- G1: Fisher et al. 2018「Researchers should explicitly test for equivalence of processes at the individual and group level across the social and medical sciences.」
- G2: Fisher et al. 2018「the data sampled within an individual in time must be representative of that individual generally (i.e., stationary).」
- G3: Fisher et al. 2018「Symmetry was pursued to limit the degree to which differences in statistical power affected the comparison」／「small sample sizes may reduce the agreement between individual and group data because small data batches may not represent the larger population of observations」
- G4: Adolf & Fried 2019「ergodicity holds conditional on (i.e., after controlling for) sources of heterogeneity between individuals and/or instability over time」／「Which and how many sources of heterogeneity will have to be conditioned on, and whether the resulting conditional inferences remain meaningful, will depend on the phenomenon, population, and time span studied」
- G5: Adolf & Fried 2019「instability over time can also produce ambiguous effects and promote interpretational fallacies. ... failure to distinguish them will mischaracterize both processes」／「Empirical quests into nonergodicity therefore need to incorporate variance sources at both levels.」

## 2. 引き継ぎの判定
1. 頻度だけの基準線の読み: 解消。
2. 範囲が第 1 の帰無だけ・下側だけ: 解消。
3. (4) で k = 5 と 15 が割れたとき: 解消。
4. CoAuthor で拾わなかったときの検出力の文: 解消。ただしどちらの帰無の値を並べるかが未定（N1）。
5. 範囲の外の T と p: 解消。
6. 止めた後の手順: 一部。例外が出ない誤りを結果の後に見つけた場合が未定（N3）。
7. 間のセルの A の作りと MUT: 解消。
8. u の擬似数: 解消（分子を c について足すと ΣM + 0.5·26² で正規化も合う）。
9. 0.37: 解消。

## 2b. 評価表
- a 4: 合成の値は出どころと一致（summary_null1.json の 0.462・0.48・0.45、0.61・0.064・0.04、0.476・0.51・0.444・0.416、d6.json の kl_median 0.054・0.058・0.069、cs1_spread_summary の値と比、supplement の 4 つの値）。不正確な言い方が 1 か所（N2）。
- b 4: 残る穴は N1 と N4。
- c 3: 「重みの選び方を変えない」は正直。最も情報のある対比（CS1 で論文 3 の得が 0 なのに見分けはつくか）を並べない（N2）。
- d 3: 7,816 字。(5) の表の後に同じ文が 2 回（N6）。
- e 投稿先未定。
- f 3: 論文 3 との対比が CoAuthor k = 5・15 だけで、CS1 との突き合わせが抜けている（N2）。
- g 4: 残る自由度は N1・N5・N3。

## 3. 指摘
- [minor] N1: 拾わなかったセルに並べる合成の値の帰無が未定
  - 位置と引用: (3) 76 行「別の文で、そのセルの合成の E1 の拾えた割合（用量の各段・報告の組。CS1 は下の「CS1 の読みの範囲」の値も）を並べる」
  - なぜ問題か: CoAuthor の用量の段は第 1 と第 2 の帰無で大きく違う（k = 5・1e-3 で 0.124 と 0.844・notes 35・39 行）。どちらを並べるかで読みが変わる（G3）。
  - 解消の条件: 「CoAuthor では第 1 と第 2 の帰無の用量の各段を両方並べる（第 2 の帰無の値は notes の D6 の表から）」のように 1 通りに書く。
  - 自信: 中
- [minor] N2: 「論文 3 の数のある k = 15」が不正確で、対比を CoAuthor k = 5・15 に限る理由が無い
  - 位置と引用: (3) 79 行「論文 3 の数のある k = 15 は (4) で並べる」。(4) 94 行
  - なぜ問題か: 補足 S7 の表（261・265 行）には「Joint, 15-session, $k=1$ & \e{4.8}{-4}」と「Joint, CS1, $k=5$ & 0 [0, 0]」もあり、どちらも 9 セルに含まれる。「論文 3 の数がある段 = k = 5・15」は合成の検出率（S10）の話。CS1 k = 5 は本人ごとの予測の得が 0 だったセルで、対比（判断 9）で最も情報がある（G1）。
  - 解消の条件: (4) に CoAuthor k = 1（4.8e-4）と CS1 k = 5（Joint 0）を同じ型で足す。足さないなら除く理由を書き、79 行の言い方を直す。
  - 自信: 高
- [minor] N3: 例外の出ない誤りを結果の後に見つけたときの手順が無い
  - 位置と引用: (2) 72 行
  - なぜ問題か: 黙って誤る型（書き手の順・取り置きの漏れ・単位の作り）は例外を出さない。data.check_units の SystemExit がコードの修正か定義の変更かの境目も無い。
  - 解消の条件: 「結果を出した後に誤りを見つけたときは、直す前の結果も残し、直した結果と並べて notes に書く。判定は直した方とし、差分を明記する」。check_units で止まった場合の扱いも 1 文で決める。
  - 自信: 中
- [minor] N4: 揃えの 1 回の引きで「拾った」とき、文の強さが m/20 に連動しない
  - 位置と引用: (3) 76 行
  - 解消の条件: 判定は変えず、例えば「m/20 が 10 以下のときは『揃えの引き直しの半数以上では p > 0.05 だった』と添える」を固定する。あるいは添えない理由を書く。
  - 自信: 中
- [minor] N5: CS1 の比の規則の「最小」が何を指すかと上側の扱いが曖昧
  - 位置と引用: 128 行
  - なぜ問題か: 0.13〜0.34 は全段とセルを通した範囲。側ごとの全体の最小か、セルごとか、片側で当たるかが読めない。上側の扱いも無い。
  - 解消の条件: 「n_A の比が 0.13 未満か n_B の比が 0.15 未満のセル（側ごと・全段とセルを通した最小）」のように数値で固定し、上側も 1 文で決める。
  - 自信: 高
- [nit] N6: (5) の重複行（117・119 行）と出どころのファイル名（103 行の json は一覧の外・要約の txt は一致）
  - 解消の条件: 片方を消す。json の SHA-256 を添えるか要約の txt を名指しする。
  - 自信: 高

## 4. 総合の推奨
minor（直してから凍結）。round 2 の 9 件のうち 8 件は解消、1 件は一部。残る穴は読む文の文脈と論文 3 との対比の範囲の言い方で、判定は変えず文の型を 1 通りにすれば消える。CS1 k = 5 の対比を落とさないでほしい。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: eye.py、run_eye.py、explore_eq_amounts.py、ml.py、SEED、v1 の notes.md、main.tex。d6.json は c と kl_median の行だけ。summary_null1.json は grep の値だけ。supplement.tex は 124・255〜269・350〜361 行あたり。data.py は 105〜224 行あたり。a_idx・b_idx が間のセルの A を正しく作るかは確かめていない。
- 注入の疑い: なし。
