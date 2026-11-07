# audit（manuscript round 5・意図の監査役・メインが要約して保存）

引き継ぎ: 解消 10（1-C・3-2／1-D・1-2・3-4／1-1〔3-1 を参照〕／1-4・3-1／2-1／2-2／2-3／2-4／3-3／3-5）・一部 1（1-3: 断りの無い言い方が limitations 42-43「the definition of a stall itself ties stalls to less preceding typing」と supplement 440-442 に残る）・解消（出どころは一部）1（3-6: 71 は差し引きで記録には 118 だけ）・判定しない 1（3-A・3-D）。数値は主・閾値の表・学習器と差・X16〜X18・停滞と対の数・水準・図 1 の座標で出どころと一致。注入の疑いなし。

1 意図にあって無いもの:
- 1-1（重）陽性対照で注入した向きが逆だったことが、抄録 13・序論 66-67・結論 8-9 に無い（「barely to changes of the observed size」だけ）。向きは results 174 と限界 10 にだけある。
- 1-2 事前登録 P10（l.167「It is read together with the floor and ceiling proportions ...」）が求める Stuck 状態の確率の天井の割合が無い（confirm_holdout.json の ceiling_gt_098 は 0.0）。
- 1-3 事前登録 H3 の書き方の後半（l.15「However, the same learner did not exceed a lower bound of 0.55 on unmatched windows either」）が文になっていない（値だけ）。

2 漂流:
- 2-1（重）discussion 31-32「The learners point to a difference of another kind: stalls were preceded by less typing, a level rather than a change」が、results 131「we did not decompose the learners」を越えて学習器の差を水準に帰する（根拠は単独の量の AUC だけ）。
- 2-2 discussion 29-30「so part of the insensitivity lies in taking the difference over 30~s」は X10・X13 の条件で決めていない読み（条件の外と断る句が無い）。
- 2-3 要旨・序論の「by 0.05--0.08」は向きを固定した値。勾配ブースティングの向きを問わない差は約 0.027〜0.029。
- 2-4 limitations 23-24「the preregistration requires this qualification in the main sentence wherever it appears」は事前登録 l.18「This qualification is not dropped in the paper's abstract either.」を強めて言い換えている。

3 矛盾:
- 3-1 context-B 1・判断 38 (2)「主の貢献は結果」と判断 39「比較の分析」で、序論 63「The contribution is a comparative analysis of one estimator.」が探索の比べを貢献の名にし、「主の貢献は確認した結果」と言う文が本文から無くなった（判断 39 の決定なので漂流に数えない）。
- 3-2 外枠 v6 l.124（5.2% を考察と結論に書かない）と事前登録（主の文に付ける）。記録として。
- 3-3 X18 の外れの定義が本文では 3 条件のうち 2 つ（28〜32 秒の外が無い）。
- 3-4 考察と結論の但し書きが逐語から縮む（「among the configurations examined」「on seen writers」が落ちる）。
- 3-5 換算「0.1--1.8 points」の下端 0.1 が補足 438 の 2 つの範囲（8.2--8.9・8.9--10.0）から出ない（0.0〜1.8）。記録にも 1.8 が見つからない。
- 3-6 相互参照: design 52-53 の (Section~\ref{sec:res-main}) は感度の小節・supplement 442 の (Section~\ref{sec:res-bounds}) は sec:res-learners。
- 3-7 discussion 39-40「fell in the same category [C-D]」が読み違えられうる。

読めなかった範囲: 補足の一部・事前登録の大部分・公開物の README と要約とスクリプト・逸脱・多くの notes と JSON・文献の記録・requirement.md・confirm_holdout.json の一部。
