# 意図の監査（manuscript round 4・論文 2・対象 commit b89aa396）

読んだもの: brief-audit.md、context-A.md、context-B.md、carryover-audit.md、decisions.md、conditions-round5.md・round7.md・round8.md、本文の abstract・introduction・methods・results・discussion・limitations・conclusion、availability、declarations、appendix/supplement.tex・tab_s3.tex・tab_pause.tex。results/ は round5_length.json の全体、round8_causal.json の冒頭 120 行、round7_warm.json を grep した範囲。

## 0. 前の round の指摘が直ったか

- 1-A 解消（抄録 "the largest component of stall length stayed"）
- 1-B 解消（抄録・序論・結論の 3 か所に "below a criterion set after seeing point values"）
- 1-C 解消（抄録 "only for ten definitions combining a 15-s window (a level without precedent) with a writer quantile"）
- 1-D 解消（抄録・結論の終わりに "consistent, negligible or dependent on the definition"）
- 2-A 解消（results の Pauses 段落 "13 of the 18 intervals lay within ±0.1"）
- 2-B 一部。先例の格子は組んだ。ただし、その読みの書き方が本文の中で食い違う（下の 3-A）。
- 2-C 解消
- 2-D 解消
- 2-E 解消。ただし 100 個目より後の φ の数の数え方が別（下の 3-B）。
- 2-F 解消（"an English summary will accompany them"）
- 3-A 解消
- 3-B 解消
- 3-C 解消
- 3-D 解消
- 3-E 一部。results の休止の段落の頭は直した。序論と抄録は、休止の「有無」を事前の基準で動いたと読ませるまま（下の 2-A）。

## 1. 意図にあって対象物に無いもの

- **1-A 持ち帰り 3 の後半（先例の格子では速さの調整だけが一貫）が、本文の一部では違う形で届いている。** 意図は「全格子で一貫したのは固定の停滞の閾値だけ、先例の格子では速さの調整だけ」。考察はそのとおり書く（discussion.tex 49–50 行 "On the grid of levels with precedent, the speed-adjusted stall association read as consistently negative, and the other readings still depended on the definition"）。一方、結果は "On the grid of levels with precedent (12 definitions; …) the reading was the same except for speed" と書き（results.tex 156–157 行）、6 通りの部分格子でも一貫した読みを足す（"Taking only the default quantile among the writer-relative levels (6 definitions), the length-adjusted association read as negligible (6 of 6)"、158–159 行）。この 2 つの食い違いは 3-A で扱う。抄録と結論は格子の読みの具体（どれが一貫したか）を書かない。意図どおりの省略かもしれないが、持ち帰り 3 の後半は抄録・序論・結論のどこにも無い。
- **1-B 休止を速さで調整した結果（休止の固定の閾値は大半が正）は、結果と考察にだけある。** 抄録・序論・結論には無い。抄録は "an exploratory adjustment for typing speed left all stall definitions negative" までで、持ち帰り 2 の後半は届いていない。探索なので落としたのなら意図との差は小さい。ただし「調整の向きが検出器で分かれる」が持ち帰りなら、抄録に半句あるとよい。
- **1-C 押下だけで決まる 2 つの切り方で全結果を出したこと**（既知の限界）は、methods.tex 79–80 行・limitations.tex 21–23 行に届いている。問題なし。

## 2. 対象物にあって意図に無いもの・条件に先に書いた読み方との一致

- **2-A 休止の「有無が動いた」を、事前の基準による結論として書いている（序論・抄録）。** 序論 34–35 行: "By criteria set before the computations, an association is present for most stall definitions but its direction changes, and among fixed pause thresholds both its presence and its direction move"。抄録 9–12 行も、"By criteria set before the computations," で始まる文の流れの中で "Among the fixed pause thresholds both the presence and the direction of the association moved" と書く。条件 6（conditions-round5.md (a) の読み方）は休止について向きの基準しか置いていない。結果は "By the criterion for presence used for stalls, which was not set in advance for pauses"（results.tex 29–30 行）、考察は "The presence of the pause association … were judged after seeing results"（35 行）、S1 は "by the stall criterion applied after seeing the results"、context-B は「有無の基準は停滞のものを後から当てた」と書く。序論は地位を書き違えている。抄録も同じ誤読を招く。
- **2-B 条件 6 (c) の読み方（長さ）**: 「片方だけなら『長さを固定すると向きは揃う』」と「元の正の 10 通りがどうなるかを数で」は満たしている（results.tex 133 行 "By the reading set before the computation, the sign became uniform: no definition was negative"、"the 10 definitions that were positive without adjustment stayed positive"。round5_length.json の stall_pos10 では p_both_pos_ci 10 で一致）。「休止の 36 通りも同じ数を書く」は、本文では固定の 18 通り（15 正・0 負）だけを書く。36 通り（pos_ci 33・incl0 3・neg_ci 0）は本文にも S3 の文にも無い（表 S3b の各行にはある）。判断 6 で固定の 18 を見出しにしたことによる差で、条件どおりではない。
- **2-C 条件 6 (a) の読み方（休止の比）**: 「36 通りの 25% 以上なら…と書く・点の値の後の基準と開示」は満たしている（results.tex 182–183 行 "by a criterion set after seeing point values"）。
- **2-D 条件 7 の読み方**: 固定 θ の逆転は 19 で 9 以上なので、読みを保ち、非対称の大きさを方法と限界に書く。どちらも満たしている（methods.tex 80–82 行、limitations.tex 25 行）。「本文で 1 文だけ触れる」は、方法（80–82 行）・結果の比（185 行）・結果の φ（234–235 行）・限界（26–27 行）の 4 か所にある。ただし φ は 25% をまたいだので、条件 7 の「その結論の文に添える」に当たる。超過は意図どおりと読める。
- **2-E 条件 8 の読み方**: 5% を超えたので一段を主に戻し、二段は 2 つとも感度として補足に置き、外に出た数（φ 74/270）を書き、得点の向きを両方の区間で書く。いずれも満たしている（S2 160–171 行。round8_causal.json の outside phi [74, 270]・recount_causal score pos 10・neg 74 と一致）。
- **2-F 範囲を超えた言い方: methods.tex 179–183 行の二段の区間の要約。** "we also computed two-stage intervals … Under them the score and ratio conclusions read the same; for φ they were shifted above the point values"。2 つの二段の区間をまとめて書いている。だが S2 では、1 つ目は得点でも 18/54・比でも 11/324 が点を区間の外に出した（"shifted against the point values: 18 of 54 score values, 11 of 324 ratios"）。得点の正の通りも 14 で（S1 の順 9）、「φ だけがずれた」は 2 つ目にしか当たらない。限界（limitations.tex 18–20 行）は 2 つ目だけの話として正しく書いている。方法の文は 1 つ目について言い過ぎ。
- **2-G 結果を見た後の部分格子（6 通り）での読み。** results.tex 158–159 行の "Taking only the default quantile among the writer-relative levels (6 definitions)…" は、判断 6（先例の格子 12 通りと全格子の 2 つ）にも、考察の提案（"apply the reading twice, to the grid of levels with precedent and to the grid with the levels around the default added"）にも無い 3 つ目の格子。どの段で決めたかの地位も書いていない。提案の「2 つの格子で読む」を本文が自分で崩している。

## 3. 矛盾（意図どうし・対象物の中・本文と results/）

- **3-A 先例の格子での固定の停滞の閾値の読みが、結果と考察・意図で食い違う。** 先例の格子は Table 2 の説明で「既定の窓と条件・本人の分位と 10 秒・3 つの切り方」の 12 通り。tab_s3 の 10 s・W 30・net の 3 行は ρ が −0.240 [−0.27, −0.21]、−0.248 [−0.27, −0.22]、−0.241 [−0.27, −0.21] で、3/3 が −0.1 より下にある。結果の "the reading was the same except for speed"（固定の閾値は全格子と同じく一貫、加えて速さも一貫）はこれと合う。考察の "the other readings still depended on the definition" と、context-B の「先例の格子では速さの調整だけ」はこれと合わない。どちらかに揃える必要がある（固定の閾値の部分族は先例の格子では 3 通りしかない、と書く手もある）。
- **3-B 100 個目より後の φ の逆転を、主の規則と違う規則で数えている。** S2 129–139 行は "The reversals of φ at 1.5, counted with the interval alone, were 17, 57, 53, 26 and 0 (in the full time: not counted, 54, 49, 19 and 0)"。全時間の側は条件 8 の改めた規則（点と区間の両方）で数え、本文は "by the same counting rule"（results.tex 232 行）と書く。本文 234–235 行の "Restricted to the time after the 100th interval, the CS1 2021 assignments reversed for 26 (29%), crossing 25%" は、規則の違う 2 つの数を比べて「またいだ」と言っており、本文はその違いを書かない。限界の "left the conclusions unchanged except one"（limitations.tex 27 行）もこの比べに乗っている。
- **3-C 3 値の読みと先例の格子の数え直しの集計が results/ に無い。** results/ の全 JSON を grep した（"negligible|class|precedent|equiv"）。0 件だった。本文の 74/89、71/89、13/18、36/36、先例の格子の 3・5・9/12・12/12・6/6 は、集計ファイルに出どころが無い。declarations は "check the numbers against the result files" と書く。tab_s3・tab_pause の丸めた区間から手で確かめると、13/18 と先例の格子の「5 negligible」は境の値で決まる。tab_pause の char 10 s・30 は [−0.10, −0.05]、tab_s3 の 0.99・W 30・net・5 は [−0.10, −0.05] で、丸めのため私には判定できなかった。round 3 の後の「数え直し」の結果は、archive に入る集計として置くのが条件と結果の対応の作法に合う。
- **3-D 方法の「状態」の節が 3 回目の点検の後の数え直しを書かない。** context-B は「3 回目の後は数え直しだけ」と書く。methods.tex 191–195 行は 1 回目と 2 回目の後の追加だけを書き、S1 の順序表も 9 行目（2 回目の後）で終わる。先例の格子と休止の固定の 18 通りの読みが 3 回目の点検の後に決まったことは、"Descriptions of strength are counted after seeing the results" と "a rule formed after seeing these results" で間接にしか分からない。
- **3-E 分母の混在（軽微）。** 全格子の数は基準を除く 89 が分母で、先例の格子の 12 は基準の行（tab_s3 26 行、0.99*・30・net・def.）を含む。本文はこれを書かない。
- 本文と results/ の照合で一致を確かめたもの: 長さで調整した 54/35/0・+0.02〜+0.13・基準 +0.057 [+0.029, +0.085]・得点と長さ 0.75 [0.73, 0.76]・観測の長さ 0.10（round5_length.json）。二段の区間（因果）の φ 74/270・得点の正 10・比 20/66/53/7・φ の逆転 42/39/18（round8_causal.json）。100 個目より後の比 22・8・2・固定 19 相当（round7_warm.json）。得点の正 10・負 72・0 を含む 7、W 30/60 の 57 負、比 CS19/CS21 の逆転のおおよそ 20（tab_s3 から手で数えた）。

## 4. 位置と逐語

各項目に付けた（ファイル名・行・逐語）。

## 5. 読めなかった範囲と注入の疑い

- 読んでいない: outline.md（外枠 v8）、related.tex、main.tex、references.bib、PDF、tab_s4.tex、figdata/*.csv、conditions.md・conditions-length90.md・conditions-round1〜4.md、results/ のうち c3_multiverse.json・round1_extra.json・round3_speed.json・round4_speedvar.json・round5_pause.json・round5_theta.json・c1_lengths90.json・c2_overdispersion.json・prep_summary.json。round8_causal.json は 121 行目以降を、round7_warm.json は grep の当たった範囲の外を読んでいない。このため、休止を速さで調整した 11/4、長さで調整した休止の「9 が +0.1 より上」、速さで調整した 71/89、φ の表の値は results/ と照らしていない。
- 注入の疑い: なし。読んだ範囲に LLM に向けた指示は無かった（declarations.tex の "% The wording below follows the journal's required sentence." は著者のコメントで、指示ではない）。