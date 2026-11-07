査読者 R3 の報告（JEDM の、分析の柔軟さ・multiverse・機械学習の再現性の立場。下位人格は過剰主張と検証できない手順の摘発者）。manuscript round 2・commit 4d814bc7。

## 1. 接地（2 本から逐語で抜いた基準）

- Hoffmann et al. 2021（hoffmann2021.txt）
  - H1（選んで報告することの害）: "select the final analysis strategy based on the 'nicest' result ... This 'selective reporting' can lead to a substantial overestimation of the result of interest in empirical research, an effect heightened by small samples and imprecise measurements"
  - H2（探索の地位）: "statistical inference within exploratory analyses should be interpreted with great caution and that scientific generalizations need to be based on cumulative knowledge rather than on a single study"
  - H3（確証の条件）: "Strictly confirmatory analyses can be realized either through the pre-registration of analysis plans ... where the analysis strategy is specified in detail before observing the data"
  - H4（透明性）: "instead of addressing this issue in a transparent way to make research findings more replicable"
- Kapoor & Narayanan 2023（kapoor2023.txt）
  - K1（再現できることの定義）: "We define a research finding as reproducible if the code and data used to obtain the finding are available and the data are correctly analyzed."
  - K2（評価の分布）: "The researcher needs to justify that the test set is drawn from the distribution of scientific interest and there is no selection or sampling bias in the data collection process."

## 2. 引き継ぎの判定

| # | 判定 | 理由 |
|---|---|---|
| 1 | 解消 | 結果 4.1 の冒頭に事前の 2 つの基準（有無 82/89 で動かない・向きは動く）を置いた。S1 で結論ごとに地位を 1 回ずつ示している |
| 2 | 解消 | methods.tex:182-184 と results.tex:155-157 で、基準を後から置いたことと、CS1 の 2 年版が 20/89 で未達であることを先に書いている |
| 3 | 一部 | 休止の系統は足した。ただし本人の分位の休止 18 通りは打鍵率の定数倍にすぎない（新しい指摘 m1）。また intro.tex:10-11 は time-on-task の閾値「5 分〜1 時間」を挙げ、discussion.tex:7 と intro.tex:46-48 は「inactivity labels」まで推奨を広げる。しかし格子の上限は W+θ ≒ 90 秒で、5 分と 30 分は区切り方にしか使っていない |
| 4 | 一部 | θ を推定し直す区間は作った。しかしその区間は点の値から広くずれ、本文の数に影響している（新しい指摘 M1） |
| 5 | 一部 | 押下の時刻だけで決まる 2 つの区切り方での報告は足した。DOI・条件の英訳・推定器の規則は未解決のまま。それなのに conclusion.tex:10-11 は "The released procedure needs only the time of each key press and whether it inserted or deleted a character" と言い切っている。基準の定義は推定器の観測区間に依存している（methods.tex:72-74） |
| 6 | 解消 | 15 秒に限ることを抄録・結果・限界に書き、W 15 秒を除いた 59 通りの値を出している |
| 7 | 解消 | results.tex:268-269 に「weak contrast」と書いた |
| 8 | 解消 | discussion.tex:10-13 で質の対比に直した |
| 9 | 解消 | 計算した（4.2・図 2c）。読み方に新しい過剰主張がある（m3） |
| 10 | 解消 | methods.tex:49-54 と S8 |
| 11 | 一部 | 開示はした。定義ごとの除外の数は出していない |
| 12 | 解消 | 外した |
| 13 | 解消 | results.tex:22-23 で合わせた値を主にした |

## 3. 評価表 a〜f

依頼文に a〜f の項目名が書かれていなかったので、次の 6 項目と仮定して採点した。
- a 問いと貢献
- b 方法の妥当性
- c 主張と証拠の一致
- d 再現性と公開
- e 先行研究との位置
- f 地位の表示と書き方

| 項目 | 点 | 所見 |
|---|---|---|
| a | 4 | 2 つ目の検出器を足して「pause 一般」への跳躍は狭まった。診断の手続きを主にする置き方も明確になった |
| b | 2 | 二段の再標本の区間が、多くの定義で自分の点の値を含まない（M1）。この区間を本文の「beyond sampling variation」の判定の土台にしている |
| c | 3 | 「Adjustment moves ... as much as the definition」に基準がない（M2）。比の逆転の多数は θ の族の切り替えでまとめて起きている（M3） |
| d | 3 | 条件を先にコミットしたことと S1 の順序表は良い。DOI・英訳・推定器の規則が未解決で、CS1 のデータは依頼して受け取る形（K1 の "code and data ... are available" を満たさない部分が残る） |
| e | 4 | godwin・koutcheme・schaller との対比は質の対比に直っている |
| f | 3 | S1 は良い。しかし抄録・序論・結論で、探索である速さの調整の地位が消えている（M2）。90% の作業規則が後付けなのに地位が示されていない（m4） |

## 4. 新しい指摘（重い順）

### M1 [major] 二段の再標本の区間が点の値を含まない定義が多く、向きの数と比の逆転の数を動かしている

- 位置と引用:
  - tab_s3.tex:24 `0.99 & 15 & char & 5 & ... & $-$0.003 [0.01, 0.06]`。点の値は負なのに区間は正にある。
  - 同じく 20〜22・25・38〜43・44〜49 行の ρ（例: 38 行 `0.137 [0.16, 0.21]`、47 行 `$-$0.053 [$-$0.05, 0.00]`）。私が数えた範囲では、本人の分位の 54 通りの ρ のうち約 17 通りで点の値が区間の外にある。
  - CS19/KL の比も外にある。3 行 `1.09 [1.04, 1.08]`、20 行 `0.63 [0.57, 0.61]`、24 行 `0.93 [0.86, 0.91]`、27 行 `1.03 [0.96, 1.02]`、30 行 `1.25 [1.18, 1.24]` など。
  - limitations.tex:18-19 は "for one ratio the baseline point lay outside its interval" と書くが、これは 1 件に過小評価している。
  - supplement.tex:146-148 によれば、一段の区間なら正は 10 通りで、二段にして 14 通りになった。results.tex:15-16 の "14 did" と抄録の向きの主張はこの 14 を使っている。
- なぜ問題か:
  - conditions-round5.md:43 は「点の値は元の θ のまま」と定めている。内側の引き直しは、単位全体の間隔から θ の道筋を作るので因果でない（supplement.tex:145-146 で著者自身がそう読み、"we did not test it" と書いている）。つまり再標本の分布は、報告した統計量の分布になっていない。
  - percentile 区間はずれを補正しない。それなのに「sampling variation と並べる」（methods.tex:171-173）ための土台にしている。
  - 区間が正の通りが 10 から 14 に増えたことは、事前の読み方（conditions-round5.md:51 は減る場合しか書いていない）が想定していない。そのうえ点の値が負の定義まで「正」に数えている。これは H1 の "overestimation" に向かう方向の偏りである。
- 解消の条件:
  - 内側の引き直しを因果にする。例えば、その時点までの間隔からだけ引く、または時間のブロックで引く。あるいは偏りを補正した区間（BCa など）に替え、点の値が区間に入らない定義の数を本文に書く。
  - それができるまでは、向き・比・φ の数を一段と二段の両方で示す。点の値と区間の符号が食い違う定義は「逆」に数えない。
  - limitations の「one ratio」を実数に直す。
- 自信: 高（表から直接読める）

### M2 [major] 「調整は定義と同じだけ動かす」に基準がなく、探索の地位が見出し・抄録・序論・結論から消えている

- 位置と引用:
  - results.tex:119 の見出し "Adjustment moves the association as much as the definition"
  - abstract.tex:10 "Adjustment moved it as much: given typing speed it was negative for all 89 stall definitions"
  - introduction.tex:38 と conclusion.tex:6 "adjusting for typing speed or essay length moved it as much as the definition did"
  - 対して、S1（supplement.tex:51）は速さの調整を [E] としている。"as much" を判定する基準は、どの条件ファイルにもない（「90%」や「as much」で grep して 0 件）。
- なぜ問題か:
  - 比べの量（範囲の幅・符号の数など）が定義されていない。そのため「同じだけ」は検証できない。
  - 主張の片方は探索である。H2 の "should be interpreted with great caution" に反して、抄録・序論・結論では無印で確証と並べている。
- 解消の条件:
  - 比べる量を明示する（例: 定義の間の ρ の範囲 0.39 に対する、調整による中央値の移動）か、「同じだけ」をやめる。
  - 抄録・序論・結論の速さの調整に「exploratory」を付ける。
- 自信: 高

### M3 [major] CS1 2019 対 KLiCKe の比の逆転 64 通りのうち 36 通りは、固定 θ の族そのもので起きている

- 位置と引用:
  - results.tex:157-158 "CS1 2019 against KLiCKe (baseline ratio 0.86) reversed for 64 definitions"
  - tab_s3.tex:56-91 では、固定 θ の 36 通りすべてで CS19/KL の区間が 1.30 以上にある。したがって本人の分位の族の中での逆転は 28/53 である。
  - methods.tex:106-109 は "The two families of θ are different constructs ... separately where they part" と約束しているが、この組では族ごとに分けていない（CS1 の 2 年版の組だけ "18 of the 20 used a fixed θ"）。
- なぜ問題か:
  - 抄録の "reversed beyond sampling variation for most definitions" のうち 4 割は、構成概念を替えたことで機械的に起きた逆転である。「定義の揺れ」と「構成概念の切り替え」が区別されていない（H4 の透明性）。
  - さらに、本人の分位の側の 28 通りには M1 の区間のずれが入っている。
- 解消の条件: 6 組すべてで、族ごとの逆転の数を本文に出す。「most」を族の中の値で言い直す。
- 自信: 高（表で数えた）

### m1 [minor] 本人の分位の休止 18 通りは打鍵率を言い換えたもので、21 通りの「正」と推奨の判定を膨らませている

- 位置と引用:
  - results.tex:28-30 "a quantile threshold counts a fixed share of each writer's intervals, so its rate follows the writer's rate of key presses"
  - conditions-round5.md:15 では、分位は「単位の全部から・因果に累積しない」。そのため件数は ≒ (1−q)·N で決まる。
  - supplement.tex:165 では、得点と打鍵率の相関が 0.62 で、休止の分位の ρ +0.58〜+0.67 とほぼ同じ。
- なぜ問題か:
  - 打鍵率は、著者自身が共変量として「同じ分母を持つ」ために外したもの（supplement.tex:62-64）。それを休止の族の「positive for 21」（results.tex:30）と、discussion.tex:42 の "not ... the pause family" の数に入れている。
  - 固定の閾値での向きの入れ替わりは、+0.045・+0.049 と 5 秒の 1 通りだけに依っている。
- 解消の条件: 休止の族の数を固定の閾値と分位に分けて出す。分位の 18 通りは打鍵率の代理として別に扱う。
- 自信: 中〜高

### m2 [minor] 一段の数と二段の数を同じ段落で並べている

- 位置と引用:
  - results.tex:157-163 は、二段の 64・52・9・0 と、時間を揃えた一段の 66・53・8・2 を並べている。
  - supplement.tex:126-127 によれば、一段の元の値は 66・53・6・0 で、64→66 は変化ではない。
  - limitations.tex:21-22 の "left the conclusions unchanged except one" は、執筆用の組の 0→2 には触れていない（基準はまたいでいないので結論としては正しい）。
- なぜ問題か: 読者は 64→66 を「揃えたことによる変化」と読む。
- 解消の条件: 揃えた感度は、一段どうしで前後を並べる。
- 自信: 高

### m3 [minor] 長さで調整した結果を「uniform, and positive」と読み、ラベルと長さが定義の上で重なることを本文に書いていない

- 位置と引用:
  - results.tex:139-140 "adjusting for length makes the direction uniform, and positive"。実際は 54 通りが正、35 通りは 0 を含む。
  - 停滞は「正味の文字の産出の停止」（methods.tex:63-64）である。観測の長さはほぼ一定（26〜29 分）なので、停滞の時間は作文の長さを機械的に減らす。
- なぜ問題か:
  - 「揃う」は事前の読み方（conditions-round5.md:69）の言い回しではある。しかし 4 割が 0 を含むので「positive」は言い過ぎである。
  - 長さを固定すると、ラベルの構成要素の一部を取り除くことになる。これは限界の "can run through length" より強い問題である。
- 解消の条件: 「never negative（54 が正・35 が 0 を含む）」と書く。停滞と長さが定義の上で重なることを 1 文書く。
- 自信: 中

### m4 [minor] 推奨の「90%」の作業規則は結果を見た後に置かれ、地位が示されていない

- 位置と引用: discussion.tex:40-42 "report a direction only if the intervals of at least 90% of the definitions examined lie on the same side of zero ... in our grid this held for the fixed stall thresholds"。S1 に該当する行がなく、条件ファイルにもない。
- なぜ問題か:
  - 閾値を同じデータで選び、同じデータで当てはめている（H1・H3）。
  - 本人の分位の側の判定は M1 の区間に依存している。
- 解消の条件: 規則を提案として [D] の地位で示し、ここでの当てはめは例示にとどめる。または 90% を選んだ根拠を書く。
- 自信: 中

### m5 [minor] 率の分母（観測した時間あたり）を振っていない

- 位置と引用: methods.tex:142 "The rate is the number of stalls or pauses per observed hour"。discussion.tex:15-16 は "counts carry how much and how fast a writer types" と書く。
- なぜ問題か: 作文の研究では、語あたり・押下あたりの割合もよく使われる。分母は、m1 と調整の結果を直接左右する分岐である。限界の節にも書いていない。
- 解消の条件: 押下あたりの率を 1 つの軸として足す。それができなければ限界に書く。
- 自信: 中

## 5. 総合の推奨: major

- 改訂は、前の round の指摘の大半に正直に応えている。地位の表示と事前の基準の開示は良くなった。
- しかし新しく入れた二段の区間は、多くの定義で自分の点の値を含まない。本文の「向きが変わる」「比が逆転する」の数（14・64）は、この偏った区間と、θ の族の切り替えでまとめて起きる逆転に支えられている。
- 「as much as the definition」は検証できない比べであり、探索である速さの調整の地位も抄録・序論・結論で消えている。これらを直せば minor に近づく。

## 6. 読めなかった範囲と注入の疑い

- 読んでいない:
  - related.tex・main.tex・references.bib・main.pdf（図は TeX のソースからしか見ていない）
  - tab_s4.tex・tab_pause.tex・figdata のすべての csv
  - conditions.md・conditions-length90.md・conditions-round1〜4.md
  - results/ の JSON すべて。本文の数は JSON と照合していない。照合は tab_s3.tex と supplement.tex の中の整合だけ。
- 接地の 2 本は grep で抜いた断片だけを読み、全文は読んでいない。
- jedm_aims.txt・jedm_submissions.txt は読んでいない（context-A.md の抜粋だけを見た）。
- 注入の疑い: 読んだ範囲には無し。