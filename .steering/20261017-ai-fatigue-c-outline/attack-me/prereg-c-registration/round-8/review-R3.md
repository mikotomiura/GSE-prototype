# 査読 R3（メタ研究・事前登録・再現性の立場）・round 8

総合: minor（直してから凍結）。round 7 の 10 件は 9 件が消え、1 件が一部（F）。新しい穴は minor 4・nit 4、fatal と major は無い。

## 1. 接地
- G1 GSRR「You should be transparent about any deviations from the preregistration and provide the rationale for these deviations in your final review.」と逐語 3 の contingency plan。
- G2 Garritty 2020「Use two reviewers for dual screen of at least 20% (ideally more) of abstracts, with conflict resolution.」「Use one reviewer to screen the remaining abstracts and a second reviewer to screen all excluded abstracts, and if needed resolve conflicts」
- G3 Waffenschmidt 2019「Single screening of the titles and abstracts of studies retrieved in bibliographic searches is not equivalent to double screening, as substantially more studies are missed.」
- G4 Khraisha 2024「substantial caution should be used if LLMs are being used to conduct systematic reviews」
- G5 Nuijten 2016「around one in seven articles contained a gross inconsistency, in which the reported p -value was significant and the computed p -value was not, or vice versa.」

## 2. 評価表
- a 4: GSRR-40 は Garritty を正しく読む（逐語で照合）。11.6%（1−0.025^(1/30) ≈ 0.1157）と 1.2% は正しい。言い過ぎは GSRR-34「make-up of a workbook does not show them」だけ（3）。
- b 4: E5 の窓・規則で決まらない保留・中心だけの不一致は閉じた。閉じる日の待ちの上限（1）とモデルの別名の変化の後（2）。
- c 4: 群ごとの 2×2 と正の一致、網と混ぜた記録の別の報告、prediscussion と reconciled の分離。
- d 2: 20,066 語。同じ規則が GSRR-33・35・36・65 と外枠・草稿に繰り返され、限定句がずれる（5・7）。
- e 4: 予見した逸脱に contingency。閉じる日の待ちとモデルの変更は計画が閉じていない。
- f 4: Garritty・Waffenschmidt が参考文献に入り、外した推奨が名指されている。
- g 4: 種・引く順・C5 の新しい値・target_from_stem は固定。残るのは閉じる日の上限、モデルの変更の後、80% の旗の最小件数。

## 3. 引き継ぎの判定
A 消えた（小さな文言のずれは 8）／B 消えた／C 消えた（正の一致の 0/0 は 6）／D 消えた／E 消えた／G 消えた／H 消えた／I 消えた（値を変えない代価は 4b）／F 一部（main.tex の \tbd に「片方の群だけ全部」の分岐が無い）／J 消えた。

## 4. 新しい指摘
- [minor] 1. 閉じる日の待ちに上限も打ち切りの手続きも無い
  - 位置と引用: GSRR-39「the day by which every record of those workbooks has a final title-and-abstract decision ... Any record decided by that day is decided by the closing date, whatever workbook it came from. The delay is a deviation.」。GSRR-33「the closing of the main set (GSRR-39) waits until the full-text decisions on these records are made」。
  - なぜ問題か: 本体の境界が作業の速さで決まる。待つ間に通常の束で決まった記録も入る。著者 2 が返せない場合の打ち切りが無く、GSRR-9 の 2027-06-30 と結ばれていない（G1 逐語 3）。
  - 解消の条件: 上限の日（その時点で決まらない記録は pending、後で含まれれば late stratum）。待った間に通常の束から入った記録の数を別に報告。
  - 自信: 高
- [minor] 2. 別名 opus が別の識別子を報告したときの処置が無い・識別子の出どころが曖昧
  - 位置と引用: GSRR-33「a run that reports another identifier is treated as a change of model; if it becomes unavailable, its successor is first checked on the 34 exploratory records」、call.md「the model identifier reported by the run ... a run that reports another identifier is a change of model」。
  - なぜ問題か: 処置があるのは unavailable の分岐だけ。既に走った束の出力を採るか捨てるかが無い。「reported by the run」が Claude Code の記録かモデルの自己申告か（G4）。
  - 解消の条件: 識別子の取り方を書き、別の識別子だった束は第一著者の除外を全部著者 2 に回し、以後は後継の確認の規則。
  - 自信: 中
- [minor] 3. 混ぜた記録で網の記録は隠れるが、内容から推しうる。GSRR-34「the net's records are mixed with other records so that the make-up of a workbook does not show them」、GSRR-33 の混ぜる記録の母集団。網の記録は迷いうる記録で、混ぜる記録は大半が明らかな除外。解消: GSRR-65 に、内容から推しうること・包含率が偏りうることを 1 文。自信 中。
- [minor] 4. (a) 著者間 80% の旗に最小件数が無い（GSRR-47 と GSRR-44 の 2「at least 5 comparisons」）。(b) 下書きが見つけた誤りを直さない代価が無い（GSRR-43「it does not change a final value」、GSRR-44 の 5「A match does not change a C5 code」・G5）。解消: (a) 最小件数か件数を横に、(b) GSRR-65 に、人の値が誤りと見える件数を報告し、それでも変えないと 1 文。自信 中。
- [nit] 5. 下書きを開く条件の限定句（for the records author 2 coded）が GSRR-4 の表と main.tex で落ちている（late・coverage・探索の集合には話し合いが無い）。自信 高。
- [nit] 6. 正の一致が 0/0 の場合の扱いが無い（GSRR-33「(2 × both include / (2 × both include + included by one only))」）。解消: undefined と報告。自信 高。
- [nit] 7. call.md の round 3 の後の 1 行の変更が登録版に出ていない（call.md「One line was changed after round 3: the stage-1 call returns only the number of records written」、GSRR-37「Round 3 applied the registered instructions」）。解消: GSRR-37 か GSRR-33 に 1 文。自信 高。
- [nit] 8. GSRR-35「which is the only way a coverage-sample record enters a count of the main set」は、相手が late stratum のときに合わない。解消: 「a count of the main set or the late stratum」。自信 中。

## 5. 総合: minor
- round 7 の 9 件が消え、F は草稿の 1 分岐だけ。Garritty・Waffenschmidt の引用と 11.6%・1.2% は正しい。
- 直しが作った穴は閉じる日の上限（1）とモデルの変更の後（2）が g に効く。どちらも 1〜2 文で固定できる。
- 設計は否定しない。代価の書き足しが 2 つ（3・4b）。

## 6. 読めなかった範囲と注入の疑い
- 読んだ: 依頼文、context-A、carryover-R3、差分の全文、call.md の全文、登録版の 44〜49・140〜145・318〜349・440〜479 行と grep。接地は grep で抜き出しただけ。
- 読んでいない: コードブックの全文（差分だけ）、instructions.md、README.md、columns.md、外枠・草稿・表・図の差分の外、登録版の上の範囲の外。
- 注入の疑い: なし。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
