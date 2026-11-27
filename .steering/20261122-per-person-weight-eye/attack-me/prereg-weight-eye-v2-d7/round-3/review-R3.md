# R3 の査読（round 3・paper-reviewer の応答の写し）

## 1. 接地
- 基準 1: Morris et al. 2019 Table 1「Compute estimates of performance and Monte Carlo SEs for these estimates.」「Include Monte Carlo SE as an estimate of simulation uncertainty.」
- 基準 2: Morris et al. 2019 Table 1「For less-used performance measures, give explicit formulae for the avoidance of ambiguity.」
- 基準 3: Morris et al. 2019 Table 1「Set the random number seed once per simulation repetition.」「If running chunks of the simulation in parallel, use separate streams of random numbers」
- 基準 4: Morris et al. 2019 §3.1「Does the data-generating mechanism favour certain methods over others? How can this be checked and justified?」、§3.2「Simulation studies provide us with empirical results for specific scenarios.」
- 基準 5: Phipson & Smyth 2010「the exact permutation p-value is pu = (b + 1)/(m + 1)」「p-values must be directly evaluated as probabilities, not treated as if they were unknown parameters to be estimated」
- 基準 6: Phipson & Smyth 2010「When the number of tests is large, any systematic underestimation of p-values can lead to dangerously wrong conclusions at the family-wise level.」
- v1 D3 の式（v1 conditions.md:63）は基準 5 に合う。

## 2. 引き継ぎの判定
- M1 CoAuthor の c の範囲: 一部。範囲の内の文（122 行）は直ったが、範囲の外の文（121 行）は CoAuthor でも「c の較正の量の範囲の外」と「門で確かめた量の範囲の外」のまま（m-A）。
- M2 基準線の読み: 解消（77 行）。
- m1 CS1 の拾わなかったときの文: 解消（76 行）。
- m2 上限を超えたとき: 解消（121 行）。128 行の wide の比の規則は下だけ（nit-C）。
- m3 凍結の確かめ: 一部。git の履歴に push の時刻は無い（nit-B）。
- n1・n2・n3: 解消（MC SE の目安 √(0.25/500) = 0.0224、√(0.0475/500) = 0.0097 で式に合う）。
- 裏取り: 90 行の値は summary_null1.json と一致、KL は d6.json に合う、128 行の wide の値は cs1_spread_summary.txt と一致、(5) の表は eq_amounts_summary.txt と一致、(4) の 4 つの値は supplement.tex 181・182・262・263 行、論文 3 の記述は main.tex 49・337 行に一致。

## 2b. 評価表
- a 4: 合成の値はすべて出どころと一致。(4) で論文 3 の「出どころは分けていない」を正しく写している。弱いのは判定の名（m-B）と範囲の外の文（m-A）。
- b 4: CS1 の n_B は補足 S2 の四分位から合成の範囲の下に出ると事前に見込めるのに、その見込みが無い（m-C）。
- c 3: CS1 が範囲の外に出れば CS1 から持ち帰るものはほぼ無いことを事前に言っていない。
- d 3: 117 行と 119 行の重複。90 行の KL は実データで対応する量を計算しないので読みの役が無い。7,816 字で round 1 の約 2.2 倍。
- e 投稿先未定。
- f 4: p は (b+1)/(m+1)、MC SE の添えは Morris の基準に合う。Holm は記述にとどまる。
- g 4: 残る自由度は例外でない誤り（m-D）と範囲の外の文の語（m-A）。

## 3. 指摘
- [minor] m-B 判定の名「本人の表の予測の得が c を超えた」は、c が負なので「得がある」と読まれる
  - 位置と引用: 102 行
  - なぜ問題か: d6.json の c は 9 セルすべてで負（coauthor/k5_g0 = −0.0031349、cs1/k1_g0 = −0.0322151）。G_v = −0.001 の書き手も数えられる（基準 2）。
  - 解消の条件: 文に c の値と符号を入れる（例: 「G_v が c（= −0.0031・差なしの筋の 95% 点の最大）を超えた書き手の数。c は負で、超えても本人の表が共有の表より良いことを意味しない」）。G_v > 0 の人数を記述として並べるかを決める（並べるなら判定に使わない）。
  - 自信: 高
- [minor] m-A 範囲の外の文が第 1 の帰無だけの範囲を「c の較正」「門で確かめた」と呼ぶ
  - 位置と引用: 121 行・103 行・explore_eq_amounts.py:37
  - なぜ問題か: 門は両方の帰無にかかっている（d6.json の gates に null2_* の群）。CoAuthor の c も第 2 の帰無で決まった。確かめていない否定になる。
  - 解消の条件: 範囲の外の文を全セルで「第 1 の帰無の差なしの筋の量の範囲の外（下／上）」に統一し、「門」「c の較正」の語を範囲の文に使わない。
  - 自信: 高
- [minor] m-C CS1 が範囲の外（下）に出る見込みを公開の S2 の値から事前に書いていない
  - 位置と引用: 105–116 行の表の cs1 の n_B「2,690〜12,090」。supplement.tex:136「10,635 [2,965, 16,640]」
  - なぜ問題か: n_B はパネル 23 人の最小で、第 1 四分位がすでに 2,965。最小が約 1,600 を下回れば wide の比の範囲の外にも出る。見込みを事前に書かないと結果を見てから重みを選べる（基準 4）。
  - 解消の条件: 「補足 S2 の四分位から、CS1 の n_B は合成の範囲の下に出る見込みが高い。そのとき CS1 の 4 セルは規則どおり範囲の外と書き、論文 3 の本文では触れない」と足す。
  - 自信: 中
- [minor] m-D 例外でない誤りに結果を見た後で気づいたときの規則が無い
  - 位置と引用: 72 行
  - 解消の条件: 「直す前の出力を消さずに notes に並べ、両方の値を報告する。直したことが判定を変えたセルにはその旨を添える」。直してよい誤りの例を合成と同じ関数の誤りに限ってもよい。
  - 自信: 中
- [minor] m-E d6.json の 2 つの入力の SHA-256 が同じ（d6.json:5–6）
  - 解消の条件: 同じになる理由を 1 行書くか、帰無ごとのファイルのハッシュを出す。
  - 自信: 低
- [nit] nit-A 117・119 行の重複と、90 行の KL に比べる相手が無い。103 行の json と要約の txt の関係。
- [nit] nit-B 凍結の時点: 「凍結のコミットの hash と、それを含む push のホスト側の記録で示す」と書く。
- [nit] nit-C wide の比の規則が下側だけ（最大 n_A 0.34・n_B 0.28 を超えたときの文も足す）。

## 4. 総合の推奨
minor（直してから凍結）。round 2 の major 2 件は解消し、合成の値はすべて出どころと一致した。残る m-B・m-A・m-D は文の差し替えで直り、m-C を事前に 1 文書けば CS1 の重みを後から選ぶ余地が消える。直した後の再査読は要らない。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: notes.md（v2・v1）、SEED、eye.py、run_eye.py、data.py、ml.py。v1 conditions.md は該当行だけ。summary_null1.json と d6.json は引いた値の箇所だけ。eq_amounts.json は一覧に無い。Morris 2019 は約 400 行と grep、Phipson 2010 は約 250 行と grep。
- 注入の疑い: なし。
