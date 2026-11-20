# 引き継ぎ（R1・行動の記号列の系列モデルの方法論の立場・round 8 → round 9）

round 8 の版は commit 77d5f324、今回の版は 1f4f4b5b。行番号は変わったので、今の main.tex で文から探してください。各指摘の裏取りの判定は、断りの無いものは「真」でした。著者の方針: 新しい計算はしていない（すべて書き方の直し）。入れ替えの対照の読みは、計算の前に決めた規則（自分の回で当てた当てはめが入れ替えに勝つ差 ≥ 残りの半分）として書き、差は残りの分け前ではない（入れ替えは共通にも負け、他人のデータの害を含む）と断った。別の書き手の k 単位は記号数も違い、同じ τ でも重みが変わることを、時間の近さと並ぶ交絡として断った（計算はしない）。入れ替えの対照は推奨に入れず、考察で点検の候補として 1 句にした。

| round 8 の指摘 | 著者の採否と対応 | 未解決（著者の認識） |
|---|---|---|
| minor 1 入れ替えの「more than half」が数から導けない | 採用。4.4 で「The margin exceeds the whole remainder, so the reading fixed before the computation (a margin of at least half the remainder) holds」「The margin is not a share of the remainder, since it also contains the loss from fitting another writer's data」。序論・決定の段・結論は「the writer's own sessions predict better than another writer's under the same τ」にそろえた | 書き手の差と時間の近さ・記号数は分けない |
| minor 2 序論と結論の植えた差の未検出に帰無が無い | 採用。「under the second null (post hoc)」 | — |
| minor 3 要旨の 30〜55 倍は平滑の違う値の比 | 採用。要旨から倍率を外した。序論の「over two orders of magnitude」は同じ固定の平滑の値どうし | 序論・考察に 2 つ目の値の倍率は残していない |
| minor 4 要旨の Neither の根拠 | 採用。要旨に「goes with the writer's most recent sessions and was not checked on synthetic writers」 | — |
| minor 5 EM の better の基準・共通の始点 | 採用。「keeps the one with the higher MAP objective on the training symbols」と共通の 10 個の始点・書き手を除く当て直しの始点。限界に「run from two starting points」 | 再始動の間の変動は計算しない |
| nit 6 remainder の定義と両側の版 | 採用。「we also call remainder the same difference in the symmetric refit」 | — |
| nit 7 Pohle の交差検証 | 採用。2 か所を「asymptotically cross-validated likelihood」に | — |
| nit 8 3 つの対照の post hoc | 採用 | — |
| nit 9 表 2 の 16 of 17 | 採用 | — |

今回は、上の各指摘が解消したかを 1 件ずつ「解消 / 一部 / 未解消」で判定し（位置と逐語を添える）、そのうえで新しい穴を探してください。前の指摘の再掲は求めません。 特に今回の直しで書き換えた部分（要旨・4.4 の対照の段・考察・結論）が、新しい矛盾や言い過ぎを生んでいないかを見てください。
