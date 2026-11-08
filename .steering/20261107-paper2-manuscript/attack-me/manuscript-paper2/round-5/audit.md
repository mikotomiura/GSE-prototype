# 監査（意図の監査役・manuscript round 5・対象 commit 4bbed897）

この監査に査読者の記録と他の round の記録は使っていない。数の照合に使った集計は results/round9_classes.json（全部）、round7_warm.json（summary の節）、round8_causal.json（summary の節）の 3 つ。

## 0. 引き継ぎの各指摘

- 1-A: 解消。表は \ref で引かれている（PDF では Table 4）。ただし地位の書き方に新しい漂流がある（2-a）。
- 1-B: 解消（抄録・序論・結論に長さの調整の 9/18 がある。速さは考察だけ）。
- 2-A: 解消。
- 2-B: 解消（扱いどおり。36 通りは S3b）。
- 2-F: 解消（methods.tex 182–183 行 "Two-stage intervals ... are a sensitivity analysis (S2)."）。
- 2-G: 解消（本文に事後の 6 通りの格子の文は見当たらない）。
- 3-A: 解消（round9 の stall_default_precedent_fixed3 は below 3/3）。
- 3-B: 解消（S2 の "17 ..., 57 ..., not counted ..., 26 ... and 0" は round7_warm.json の A3 warm と一致。限界も直っている）。
- 3-C: 解消（表 4 の 5 行 × 3 列は round9_classes.json と全部一致）。
- 3-D: 解消（S1 の順序 10 [D]。methods.tex 198–199 行 "Sizes, the reading by classes of interval and the grid of default and precedented levels were set after seeing the results."）。
- 3-E: 解消（表 2 の注 "(12 definitions, including the baseline)"）。
- 判断 7「題を結論の側に寄せる」: 一部。下の 1-b。

## 1. 意図にあって対象物に無いもの

1-a. 持ち帰り 4「データの間の比は定義で動く（22% で 25% に届かない）」の但し書きが、抄録だけに無い。
- 抄録 abstract.tex 14–16 行: "Rate ratios between the programming editions and within-writer overdispersion also moved with the definition"
- 序論 40–41 行と結論 8–9 行には "below a criterion set after seeing point values" がある。
- 抄録だけを読むと、届かなかった比を「動いた」と読む。

1-b. 題が結論の側に寄っていない（判断 7）。
- main.tex 31 行: "What moves with the pause definition: a multiverse diagnostic of pause and stall labels in keystroke logs"
- 題は問いの形のままで、持ち帰り 1・2（向きは窓 15 秒と本人の分位の角でだけ入れ替わり、使われている水準では大きさが動く／調整も軸）は題に出ていない。
- 定義の主は停滞の 89 通りなのに、題は "pause definition" と書く。
- 外枠 v8 の題案（outline.md 8 行）は結論を題に入れていた。

1-c. 追加の条件 6 (a) の P-B の読み方（どれかの組が 36 通りの 25% 以上なら「休止の系統でも比の向きは入れ替わる」と書く）は、S3 には書かれている。
- supplement.tex 185–186 行 "the direction of a ratio changed with the definition in the pause family too"
- 本文 results.tex 195–197 行は数だけで、読みの文が無い。本文で使う 36 通りという分母の扱いは 3-c。

1-d. 追加の条件 6 (c) の「休止の 36 通りも同じ数を書く」について、長さで調整した後の負・0 を含む・正の数は、本文に固定の 18 通りの分しか無い（results.tex 137 行 "15 of 18 were positive and none negative, and 9 had an interval above $+0.1$"）。36 通りの集計の文は、読んだ範囲の S1・S2・S3 の地の文に見当たらない。表 S3b は読んでいない。

## 2. 対象物にあって意図に無いもの（漂流）と、条件の読み方との一致

2-a. 事後の [D] の量が「事前の基準」の文の中に入っている。
- 抄録 9–12 行: "By criteria set before the computations, ... its direction changed: ... and on a grid of default and precedented levels it was negative or negligible."
- 序論 34–36 行も同じ構文: "By criteria set before the computations, ... on the grid of default and precedented levels the association is negative or negligible."
- 先例のある格子は S1 で [D]、methods.tex 199 行で「結果を見た後」とされている。文の構造が地位を取り違えさせる。

2-b. 速さの調整が推奨の柱に入っている。
- 考察 discussion.tex 42–43 行: "with and without adjustment for quantities that do not contain the label, such as the length of the product and typing speed"
- 意図（context-B の持ち帰り 2「速さの調整は探索」）と外枠 v8 の 20・131 行（探索は中心の主張・推奨に上げない）とずれる。
- 表 4 にも探索の列があり、地位の印は付いている。

2-c. 長さの調整と条件 6 (c) の読み方: 一致（より控えめな書き方）。
- 条件の文は「片方だけなら『長さを固定すると向きは揃う（負／正）』と書く」。
- 本文 results.tex 133 行は "By the reading set before the computation, the sign became uniform: no definition was negative." で、「正に揃う」とは書いていない。54 正・35 が 0 を含む・0 負なので、控えめにした方向のずれで、問題はない。
- 「元の正の 10 通りがどうなるか」（"stayed positive"）と、得点と長さの相関が 0.5 以上なら限界に書くこと（limitations 37–39 行）は、どちらも満たしている。

2-d. 条件 7 の読み方: 一致。
- 固定 θ の逆転は共通の基準で 19（round7_warm.json の A1_cs1_fixed warm 19 ≥ 9）なので、族の読み（"18 of the 20 used a fixed θ"）は保ってよく、非対称の大きさ 3.2–10.3% も方法と限界に書かれている。
- φ の CS1 2021 の課題が 19→26 で 25% をまたいだことは、本文に添えてある（results.tex 248–249 行）。
- 得点の区間の符号の入れ替わりが 0 であることも S2 に書かれている。

2-e. 条件 8 の読み方: 一致。
- 外に出た割合の最大は 0.274（φ 74/270）で 5% を超えたので、一段の区間を主に戻した。この判定と、両方の区間での得点の向き（正 10・負 74 と 72）は S2 で round8_causal.json と一致する。
- 限界 19–21 行 "for $\varphi$ it was shifted above the point values" は、点が区間の下に出たことの言い換えで、正しい。

## 3. 矛盾（意図どうし・対象物の中・本文と results/）

3-a. S1 の地位の表の中で自分と矛盾している。
- supplement.tex 55–58 行: "For pauses the reading was stated over all 36 definitions and was met there, through the control alone; the main text reports the 18 fixed-threshold definitions, in which it is also met"
- "through the control alone"（36 通りでは対照の側だけで満たした）と "in which it is also met"（固定の 18 通りでも満たした）が両立しない。
- 本文の表 3 では、固定の 18 通りに区間が正のものが 3、負のものが 7 あるので、後半の方が正しい。

3-b. 意図の文書の表の番号が対象物と違う。
- context-B の持ち帰り 3 と carryover 1-A は、類の読みの表を「表 5」と書く。
- ビルドした PDF では類の読みは Table 4（11 頁）で、Table 5 は φ の表（12 頁）。
- 原稿の中は \ref なので食い違わないが、意図の側の誤り。

3-c. 休止の比の分母が本文の中で揃っていない。
- 本文は本人の分位の休止 18 通りを「押下の率の対照で、休止のラベルではない」と分けている（methods.tex 147–149 行 "we report these as a control for the key-press rate rather than as pause labels"）。
- それなのに比の段落では対照を含む 36 通りで数える（results.tex 195–197 行 "the two CS1 editions reversed for none of the 36 definitions, whereas the pairs with CoAuthor ... reversed for 31 or 32"）。
- S3 によれば、固定の閾値だけでは 14 と 13/18。

3-d. 100 個目より後に制限した φ の変化を、本文と限界が一部しか書いていない。
- 限界 26–28 行: "left the conclusions unchanged except for $\varphi$ in the CS1 2021 assignments ... and in the CS1 2021 blocks"
- CS1 2019 のまとまりは、基準の区間 [1.28, 1.45] が 1.5 を外れて、数えない → 17/89（19%）に変わった（S2 と round7_warm.json の A3 warm 17）。25% はまたいでいないが、「数えられなかった」という本文の結論（results.tex 248、250–251 行 "or could not be counted"）は動いた。
- 抄録と結論の「CS1 の 2 セル」は、制限すると 2019 の課題と 2021 の課題に入れ替わる（2021 のまとまりは数えられなくなる）。その注記は本文に無い（S2 にはある）。

3-e. 本文の数と results/ の照合は、照らした範囲では全部一致した。
- 得点: −0.063 [−0.091, −0.034]、−0.25〜+0.14、中央値 −0.14、正 10・負 72・0 を含む 7。
- 比の逆転: 20・66・53・6・0 と、100 個目より後の 22。
- φ の表 5 の基準・中央値・範囲・1 を超える数・逆転の数。
- 表 4 の全セル。
- ひとつ注記: 全格子を速さで調整した行は 71/79 = 89.9% で、90% の規則にわずかに届かず「定義に依る」になっている。規則どおりだが境界の上の判定なので、類の読みが刻みに敏感なことの実例になっている（探索の列）。

## 4. 位置と逐語
各項目の中に書いた。

## 5. 読めなかった範囲と注入の疑い

読んでいない（照合していない）もの:
- 本文の related.tex、declarations.tex
- appendix の tab_s3.tex、tab_s4.tex、tab_pause.tex
- supplement.tex の 216 行より後
- figdata の CSV 全部
- conditions.md、conditions-length90.md、conditions-round1〜4.md
- results の c3_multiverse、round1_extra、round3_speed、round4_speedvar、round5_pause、round5_theta、round5_length、c1_lengths90、c2_overdispersion、prep_summary
- round7_warm.json の 2256 行より後（定義ごとの値）と、round8_causal.json の 171 行より後
- outline.md は 1–30 行と grep で当たった行だけ
- PDF は 11–13 頁だけ

上の数の照合（たとえば "58 definitions ... at least 0.1"、"3 a positive one"、休止の 9/18、15/18）は、読んだ集計で確かめられた範囲に限る。休止の値は round9 の数とだけ一致を見た。

注入の疑い: 読んだ範囲には無い。