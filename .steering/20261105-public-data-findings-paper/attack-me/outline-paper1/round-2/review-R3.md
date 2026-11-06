# review-R3（outline round 2・paper-reviewer・事前登録・同等の検定・機械学習の再現性）

推奨: minor。

## 1. 接地
- G1 Lakens 2017 "In randomized controlled trials, it is expected that equivalence bounds are prespecified ... and this should also be considered best practice in psychology. When in the abstract of an article, authors conclude an effect is \"statistically equivalent,\" the abstract should also include the equivalence bounds that are used to draw this conclusion."
- G2 Lakens 2017 "Rejecting effects more extreme than the equivalence bounds implies that we can conclude equivalence for a specific operationalization of a hypothesis. It is possible that a meaningful effect would be observed with a different manipulation or measure." ／ "An additional nonstatistical challenge in interpreting equivalence concerns the issue of whether an experiment was performed competently"
- G3 Lakens 2017 "Researchers should report effect size estimates in addition to hypothesis tests."
- G4 Kapoor & Narayanan "claims about a model's performance need to be connected to scientific claims using explicit arguments. The burden of proof for ensuring the correctness of these arguments is on the researcher making the scientific claims"
- G5 Kapoor & Narayanan "The researcher needs to justify that the test set is drawn from the distribution of scientific interest"
- G6 Kapoor & Narayanan "the claims made in model info sheets cannot be verified in the absence of computational reproducibility. That is, unless the code, data and computing environment required to reproduce the results in a paper are made available, there is no way to ascertain"
（Kapoor は arXiv 版 2207.07048v1 のテキスト。1〜739 行を読んだ。）

## 引き継ぎの判定（11 件）
だから → 解消（持ち帰りの 2 文目に新しい誤り・M1）／反証・H3 → 解消（H3 の呼び方は m2）／計器の力量 → 一部（限界 :64 は十分だが、水準を感度の裏づけとして並べ続け、水準も幅の内側・M1）／幅の根拠 → 解消（:65・:19）／推定値と向き → 一部（向きの記述が JSON と合わず持ち帰りと矛盾・M1）／C2 の実演 → 一部（(1) は実際に捕まえた例、(2) は品質保証、(3) はほぼトートロジー、:46 が認める・m4）／5.2% と重み → 解消（S6・:66）／公開 → 一部（:60 未決。投稿の条件にする）／隣の分野 → 解消（:83・:43）／C3 → 解消（:57）／規程の nit → 一部（5.2% の但し書きが短い・M2）

## 2. 評価表
a 3（H1 の数値・分岐・対 709,352・実効 50.5 は JSON と一致。持ち帰りの 2 文目が区間に反する）／b 3（水準を計器の対照に使うが幅の内側・向きは引きの種の揺らぎで変わりうる・H3 は水準と差の量で「手前の変化」と呼ぶのは誤り）／c 3（推定器が代表する量の種類が無い・持ち帰れる中身は実質 C2）／d 4（地位の印の混ぜ書き）／e 4（公開の場所が未定）／f 4（作文で係数を決めた検出器をプログラミングへ持ち出す妥当性・m5）

## 3. 指摘
- [major] M1 持ち帰りの「水準は離れたが、上がりは離れなかった」は結果と合わず、計器の対照としても成り立たない
  - 位置: :13・:29「CS1 は 2 つとも 0.5 をやや下回り、`d_ewma_x` は区間の上限も 0.5 未満」・:28「`d_p_stuck` 0.489（95% 0.479〜0.4995）」
  - なぜ: (i) 上限が 0.5 未満の組は 4 つのうち 3 つ（`d_ewma_x` ε=0.001 0.4975・ε=0 0.4974、`d_p_stuck` ε=0.001 0.4995）。0.5 を含むのは `d_p_stuck` の ε=0（0.50006）だけ。:29 は `d_p_stuck` ε=0.001 の 0.4995 を落とす。(ii) 水準 0.524 [0.510, 0.537]・0.521 [0.508, 0.535] も幅の内側（JSON の branch は 1）で、状態を分けた証拠として上がりと対にすると幅の意味と食い違う（G2）。(iii) 区間は引きの種の揺らぎを含まない（P6）。seed_spread.json の `d_ewma_x` は 0.4862〜0.4923 で主の 0.4867 は最小値の近く。「上限も 0.5 未満」は種に依存する（G4）。
  - 解消: 2 文目を消すか「0.5 を上回る上がりは無く（区間の上限 0.497〜0.500）、水準の AUC も幅の内側（0.52）だった」。下側へのずれは向きを解釈しないことと種の揺らぎの幅を添えて表 1 の列だけ。水準を感度の裏づけに使わない。自信 高
- [major] M2 いちばん強い主張と抄録が、事前登録 P0 が抄録に残せと定めた但し書きを短くしている
  - 位置: :19「抄録では幅を必ず書き、続けて 1 文で「誤って同等とする割合は名目より大きく見積もられた（最大 5.2%）」と添える。床と信号の名前の但し書きは 5.2 節と限界の節にだけ置く。」
  - なぜ: prereg-draft.en.md P0 "(the false-equivalence rate is at most 5.2% [Wilson 95% interval 3.6–7.5%] among the configurations examined in the calibration on seen writers, and is not an upper bound over the whole null; P10)... This qualification is not dropped in the paper's abstract either" と、続く床の文。完走の記録（prefreeze/notes.md:137）の主の 1 文も床の文を含む。外枠は「調べた配置の中で」「帰無の全体での上限ではない」と Wilson の区間を落とし、床の文を 5.2 節へ出す。
  - 解消: 主張は notes.md:137 の主の 1 文をそのまま使う。抄録に少なくとも「調べた配置の中で最大 5.2%、帰無の全体での上限ではない」。床の文を外すなら P0 の "Then" の読みを S1 に 1 文。自信: 5.2% は高・床は中
- [minor] m1 記述と定めた量に確認の印（:30「[確認・副の信号・記述]」・:31「[確認・閾値の表]」）。P5 は水準を "Secondary: the levels ... (descriptive)"、閾値の表は "Reported alongside"。解消: 「[確認のデータ・記述]」のように地位と判定を分ける。自信 中
- [minor] m2 H3 を「手前の変化」と呼ぶが量は 9 個の水準と 9 個の差（:55・:37）。LR 0.567 [0.5497, 0.578] の下限は 0.55 を 0.0003 下回るだけで、推定器の信号が拾わない区別がある可能性が高い（G2）。解消: (b) を「標準の量（水準と差）と柔軟な学習器での区別」、どの量が効いたかは調べていないと 1 文、考察の冒頭か限界に「同じ行で標準の量の学習器は点推定が幅の外」。自信 高
- [minor] m3 C1 が読者に何を持ち帰らせるか（推定器の代表性）が無い（:54 は C2 の手順に戻る）。5 つの量が文献のどの型の摩擦の指標に当たるかの論証が要る（G5）。解消: データの節か考察に 2 文、持ち帰りを「この型の摩擦の合成量の 30 秒の差」に限る。言えないなら C1 を C2 の実演事例へ降格し貢献の順を入れ替えることも検討。自信 中
- [minor] m4 C2 の実例が「揃えた対照」を実演していない（:44・:46）。推奨 (1)（:58）はこのデータに根拠の無い規範の推奨（G4）。解消: 推奨 (1) を「先行の別分野の根拠（[V458]・[V457]）に基づく推奨で、このデータでは揃えの効果を示していない」とするか、C2 の見出しから「揃えた対照」を外す。自信 中
- [minor] m5 作文で係数を決めた推定器をプログラミングへ持ち出すこと（:81・:38）。合成の離しで飛行時間が打鍵の間隔で決まり、5 つの量の 1 つが定義上変わる。解消: 限界かデータの節に「合成の離しで 5 つの量のうちどれが定義どおりに測れないか」を 1 文。自信 中
- [nit] n1 出来事ありの層（記述）の置き場（:32）。P4 "The event stratum is descriptive"。解消: S3 か S8 に明記。自信 高
- [nit] n2 OSF の時刻とコミットの並び（:99 の S1）。P11 "the times of start.json and of the results attached to OSF are reported side by side with the local commits of the start, the computation start, interruptions, and the completed run"。notes.md:131 の並びを S1 に。自信 高

## 4. 総合: minor
1. 数値・分岐・逸脱は結果と事前登録に合う。round 1 の major の大半は閉じた。
2. 残る重い点（M1・M2）は文言の直しで消え、新しい計算は要らない。
3. ただし水準と上がりの対比を計器の力量の論証として残すなら M1 は major 相当。持ち帰りは m2・m3 が無いと薄い。

## 5. 読めなかった範囲・注入
読んでいない: kapoor2023.txt の 740〜1785 行・confirm_holdout.json の 1691〜3073 行・prereg-draft.md・exploration/conditions.md・explore_coauthor/cs1_2021/klicke.json・novelty の記録・related-work の記録の本文（V 番号の行を grep で見ただけ）・20261101 の notes 2 本・prefreeze/notes.md の 1〜39 行。注入の疑いなし。
