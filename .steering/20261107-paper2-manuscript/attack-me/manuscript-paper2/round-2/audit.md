# 意図の監査役の報告（manuscript round 2・論文 2・対象 commit 4d814bc7）

## 0. 引き継ぎの各指摘

| # | 判定 | 根拠 |
|---|---|---|
| 1-1 | 解消 | introduction.tex 46 "What generalises is the procedure; the score association is one worked example on one corpus." |
| 1-2 | 解消 | 考察から外れ、定義とともに S3 "Agreement in time" に移った |
| 1-3 | 解消 | abstract 15 "the code and the aggregate tables are released" |
| 1-4 | 解消 | methods "Relation to the companion study" の段落と S8 |
| 1-5 | 解消 | discussion 35–36、limitations 32 |
| 1-6 | 解消 | limitations 31 "non-linear remainders were not examined" |
| 1-7 | 解消 | 表 1 に "Access and holdout" の列を足した |
| 1-8 | 解消 | 題を "Which pause? A multiverse diagnostic of pause and stall definitions" に替えた |
| 1-9 | 解消 | 本文は 5,805 語 |
| 2-1 | 一部 | 考察は直った。序論の箇条で再発している（下の 2-A） |
| 2-2 | 解消 | 速さの段落は事実で書かれている |
| 2-3 | 解消 | "What the criteria established" |
| 2-4 | 一部 | 考察は質の対比になった。ただし新しく足した "as much as" が、順位づけと同じ型の比較になっている（2-B） |
| 2-5 | 解消 | results 265 "stayed the largest component" |
| 2-6 | 解消 | results 212 "1.21 in CS1 2021 blocks" と別に書いた |
| 2-7 | 解消 | 語は見当たらない |
| 2-8 | 解消 | 消えている |
| 2-9 | 解消 | conclusion 10–11 で 2 つの欄に限った |
| 2-10 | 解消 | 速さと長さを 1 文に並べた。ただし探索的な値を見出しに上げた点は 2-A に回す |
| 2-11 | 解消 | 但し書きは限界と S1 に置いた |
| 2-12 | 解消 | "only in the corner with a 15-s window" |
| 3-1 | 解消 | 単位で書き、"none in CS1 2021" も書いた |
| 3-2 | 解消 | "released for research" |
| 3-3〜3-6 | 未解消 | 外枠を直さない方針として受け入れ済み。この差が 1-A の意図どうしの矛盾として残っている |

## 1. 意図にあって対象物に無いもの

**1-A（意図どうしの矛盾が原稿に出ている）速さで調整した値を見出しに上げている。**
- 外枠 v8 は 2 か所で、速さで調整した値を中心の主張と推奨に上げないと書いている。
  - 判断 13: 「中心の主張・推奨に上げない」
  - 本文の書き方: 「4.1 の末尾の 1 段落だけで、題・持ち帰り・推奨の柱にしない」
- 一方 context-B の持ち帰り 2 は「速さを固定すると停滞の 89 通りすべて負」を持ち帰りにしている。
- 原稿は context-B の側に従い、この値を次のすべてに置いている。
  - 抄録 10: "given typing speed it was negative for all 89 stall definitions"
  - 序論の箇条 2
  - 独立した結果の節 "Adjustment moves the association as much as the definition"
  - 考察の推奨 42–43: "Report the association with and without adjustment for ... typing speed"
  - 結論 6
- 長さで調整した値は [A] なので、持ち帰り 2 は長さだけでも立つ。どちらの意図を正とするかを研究者が決める必要がある。

**1-B 休止の系統の読み方（conditions-round5 (a)）で、原稿に無いものが 3 つある。**
- (i) P-B の文が無い。round5_pause.json では CS1 2019/CoAuthor が 32/36、CoAuthor/KLiCKe が 31/36 で、25% を超える。条件はこのとき「休止の系統でも、データの間の比の向きは定義で入れ替わる」と書くこと、さらに「点の値を見る前の基準ではない」ことを開示するよう定めている。原稿（results 159–161）は数を並べるだけで、この結論の文も開示も無い。
- (ii) P-C の数が本文にも補足にも無い。条件は「P-C は数を書くだけ」と定めている。json では 26・1・8・1・6。
- (iii) 先行研究の値と並べていない。条件は休止の関連の範囲を「先行研究の値と並べる。比べは同じ向きか・範囲に入るかに限る」と定めている。関連研究 35 には "from about −0.15 to −0.43" とある。しかし結果と考察では、固定 10 秒の −0.06〜−0.13 がこの範囲より小さいこと、分位の +0.58〜+0.67 が向きも逆であることを、どちらも比べていない。

**1-C 休止を速さで調整した結果が本文に無い。**
- round5_pause.json の PD.speed は、区間で負 4・正 29・0 を含む 3 である。休止では速さで調整しても向きがそろわない。
- 本文の速さの段落は停滞だけを書いている。休止は S3 の表の列にしか出てこない。
- 一方で節の題 "Adjustment moves the association..." と結論 6 "adjusting for typing speed ... moved it" は 2 つの検出器にまたがって読める。

**1-D 共通の基準の読み方（conditions-round7）が半分しか果たされていない。**
- 条件の定め: 固定 θ が 9 以上なら、読みを保ったうえで「非対称の大きさ（露出の 3〜10%）を方法と**限界**に書く」。
- 結果は 19 で、9 以上である。方法 76 には "3.2--10.3% of the exposure" がある。
- 限界 19–20 は "cannot detect before the 100th interval" とだけ書き、大きさが無い。

**1-E 結果を見た後に計算を足した回数が本文に無い。**
- context-B の既知の限界は「原稿の査読の後に 4 つ」、外枠の限界 5 は「5 回」と書く。
- 本文（methods 179–181）は "S1 gives the order" だけである。
- 査読の後に足したという事実は、S1 の順序の表の 7 行目と 8 行目にしか無い。

## 2. 対象物にあって意図に無いもの

**2-A 地位の書き違い（2-1 の再発）。**
- 序論 32 "By the criteria we set before each computation, the conclusions fall into three groups:" の下に、次の 2 つが入っている。
  - 箇条 2 の速さ: 原稿自身が S1 で [E]（探索）としている
  - 箇条 3 の比の逆転: 基準は点の値を見た後に置いた（methods 181–182）
- 抄録 7–14 も "By the criteria set before each computation" の段落の中に、速さの文と比の文を限定なしで続けている。

**2-B 測っていない比較を主張している。**
- 抄録 10 "Adjustment moved it as much"
- 序論 38 "moves the association as much as the definition"
- 結果の節の題 119
- 結論 6 "moved it as much as the definition did"
- 「同じくらい」を量る基準も量も、条件と結果のどこにも無い。context-B の持ち帰り 2 の「定義と同じくらい」が原因で、意図の段階から測っていない比較である。

**2-C 改訂の計算の書き方が、条件に先に書いた読み方と合っていない点。**
- (b) の区間の結果は、読み方が想定していない向きに出た。
  - 読み方は「区間で正の通りが 10 から**減って** 1 以上なら」と「0 になれば」の 2 つしか置いていない。
  - 結果は 10 から 14 に**増えた**（round5_theta.json の summary.recount_with_reestimated_theta.B.pos_ci = 14）。
  - S2 146–147 に "10 ... instead of 14" の開示はある。しかし読み方が想定していない結果だったことは書かれていない。
  - 新しく正になった 4 通りは、生の点の値が W15_q0.95_net_replay +0.026、W15_q0.99_ins_g30 +0.016、W15_q0.99_ins_replay +0.012、W15_q0.99_ins_g5 **−0.003** である（round5_length.json の rho_raw）。
  - 持ち帰り 1 と抄録の「14/89」は、区間がずれたことで増えた分を含んでいる。向きが入れ替わるという結論そのものは、元の 10 でも成り立つ。
- S1 の 7 行目の英訳が、条件と逆の意味に読める。
  - S1 は "the two-stage intervals replace the earlier ones whichever is narrower" と書く。
  - 条件は「どちらの区間が狭いかによらず置き換える」と定めている。
  - 英文は「狭い方で置き換える」と読める。"regardless of which is narrower" が正しい。
- (c) の長さの読み方は合っている。
  - "adjusting for length makes the direction uniform, and positive" は、読み方の「片方だけなら揃う（正）」と一致する。
  - 0.75 は 0.5 以上なので、限界 30 に書くという定めも満たしている。
  - "The 14 ... stayed positive" は summary に無い（stall_pos10 は元の 10 だけを数えている）。by_cfg で、足された 4 通りの p_both_ci がすべて正であることを確かめた。
- round7 の「25% をまたいだら、その結論の文に添える」が不完全である。
  - φ の CS1 2021 の課題は、片段の区間で 19 から 26 に増え、25%（22.25）をまたいだ。
  - 本文の φ の節 215 は "also for 26 in the CS1 2021 assignments (S2)" とだけ書く。25% の基準を満たすようになったことは書かれていない。φ の節には 25% の基準そのものが出てこない。
  - 「本文で 1 文だけ触れる」という定めも超えている。方法、結果 161–163、φ の節、限界の 4 か所で触れている。
- 結論が休止にも広がっている。
  - 結論 4–8 は "Across 89 ... and 36 ...: ... The ratio of rates between a programming course and an essay corpus ... also moved" と、2 つの検出器にまたがって書く。
  - 休止の系統の CS1/KLiCKe の逆転は 5/36 と 3/36 にとどまる（round5_pause.json の PB）。
- 考察に条件に無い新しい規則がある。
  - 推奨 40–41 "report a direction only if the intervals of at least 90% of the definitions ... lie on the same side" は、条件にも外枠（「大半なら」）にも無い数の基準である。
  - 「in our grid this held for the fixed stall thresholds」は点検していない。固定の 36 通りの区間の内訳は本文に無い。

## 3. 矛盾（本文の数と results/ の集計の食い違いを含む）

- **3-1 区間の外に点がある、という開示が足りない。** 限界 18–19 と S2 は「for one ratio the baseline point lay outside its interval」とだけ書く（context-B も「比が 1 つ」）。しかし W15_q0.99_ins_g5 の得点の関連は、点が −0.003 で、二段の区間は [+0.007, +0.061] である（round5_theta.json の by_cfg）。この通りは本文の「区間で正の 14」に数えられている。得点の関連でも、点が区間の外に出ている通りが少なくとも 1 つある。
- **3-2 区間の作り方の異なる数を同じ段落で並べている。** 結果 157–163 は、主の数（二段の区間で 64・52・9）に続けて、共通の基準の数 "66, 53, 8 and 2" を書く。共通の基準の数は片段の区間で、比べるべき相手は片段の 66・53・6・0 である。読者は 64→66、9→8 と動いたと読む。φ の 26（片段）と表 3 の 21（二段）も同じ構図である。方法の Intervals 段落 168–171 は例外として休止の分位と調整後の値を挙げるが、共通の基準が片段であることは挙げていない。
- **3-3 序論の書き方が方法と食い違う。** 序論 29–30 "Each conclusion is reported with an interval ... in which the writer-relative threshold is estimated again" に対し、方法 170–171 は "The pause family's quantile and the adjusted correlations keep the threshold fixed" と書く。
- **3-4 [A] の定義と、比の逆転の扱いが合わない。** S1 の [A] の定義は "criterion committed before that quantity was seen" である。しかし比の逆転の行（基準は点の値を見た後に置いた）にも [A] が付いている。
- **3-5 5 秒の休止の書き方が表と食い違う。** 結果 27 は "around zero at 5 s"、33–35 は "no relation (a 5-s pause threshold)" と書く。しかし表 4 では、5 秒で全押下に区間が負の通りが 1、文字の間隔に区間が正の通りが 1 ある（本文 28 自身も "and one at 5 s" と書く）。PD の固定の負 7 は、10 秒の 6 と全押下の 5 秒の 1 の合計である。
- **3-6 固定の閾値の範囲が節によって違う。** 方法 134–135 は "fixed 2, 5 and 10 s, the range of fixed thresholds in writing" と書くが、表 2 は "fixed thresholds in writing span about 0.25--10 s" と書く。
- **3-7 一致を確かめた数。** 抄録と結果の 92%（82/89 = 68+14）、14/89、59 通り中 53 が負、長さの 54/35/0・59・33/36、0.75 [0.73, 0.76]・0.10、φ の 16/55/54/21/0、比の 20（固定 18）・64・52・9・0、共通の基準の 22（19）・66・53・8・2・26、得点と速さの数は、results/ と一致した。不一致は 3-1 と 3-2 だけである。
- **3-8 区間の照合の許容幅の変更（開示済み）。** conditions-round5 (b) の確かめは「外側だけの区間が 0.05 以内、超えれば止めて調べる」と定めているが、実測は 0.0697 だった（round5_theta.json の control_outer_only_max_diff）。S1 の (17) は、許容幅を 0.08 に広げたことを開示している。止めずに許容幅を広げたこと自体は、条件からのずれである。

## 4. 位置と逐語

各項目の中に書いた。

## 5. 読めなかった範囲と注入の疑い

- 読んでいないファイル: PDF、references.bib、appendix/tab_s3.tex・tab_s4.tex・tab_pause.tex、figdata の CSV 全部、conditions.md・conditions-length90.md・conditions-round1〜4.md。
- 読んでいない JSON: round1_extra、round3_speed、round4_speedvar、c1_lengths90、c2_overdispersion、c3_multiverse、prep_summary。
- 一部だけ読んだ JSON: round5_theta、round5_length、round5_pause、round7_warm は、summary と、上に名前を挙げた by_cfg の数件だけを読んだ。
- このため、ほかに点が区間の外に出ている通りの数、順位の 80/89 と入れ替わりの 11、CS1 2019 の 4.4〜46.0、所見 2-C の「固定の秒で 90% が成り立つ」は照合していない。
- 注入の疑い: 無し。

照合に使った主な資料:
- /Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round5_theta.json
- /Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round5_length.json
- /Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round5_pause.json
- /Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round7_warm.json
- /Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/*.tex
- /Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/appendix/supplement.tex