# 引き継ぎ（R2・個人化した行動のモデルの実務の立場・round 9 → round 10）

round 9 の版は commit 1f4f4b5b、今回の版は c87c7d63。行番号は変わったので、今の main.tex で文から探してください。各指摘の裏取りの判定は、断りの無いものは「真」でした。著者の方針: 新しい計算はしていない（表 3 の区間は保存済みの集計の値を写した）。序論の貢献の段を 1 つの主張にまとめ、2 つ目の値が決定に関わる理由（平滑そのものを他人で選び両側に当てる。固定の平滑では強く縮めた本人の当てはめが共通より実質的に軽く平滑される）を 1 句書いた。

| round 9 の指摘 | 著者の採否と対応 | 未解決（著者の認識） |
|---|---|---|
| minor 要旨の検出の限界の範囲 | 採用。「at the fixed base smoothing, planted differences ... were not reliably detected under the post hoc null」 | — |
| minor 決定の段の例が隠れ状態を読まないことと食い違う | 採用。「times hints by the predicted probability that the next seconds are a pause」 | どの記号での差かは測っていない |
| minor 両側の版に区間が無い | 採用。表 3 の k = 5・15 に条件つきの 95% ブートストラップ区間（保存済みの集計） | 他の k は補足 |
| minor 推奨 (2) の選びの順 | 採用。行った順（平滑を共通のために選んで両側に当て、縮みはその下で選ぶ）と「choosing all three jointly was not tried」 | — |
| minor 費用の目安 | 採用。「about one (k = 5) to three (k = 15) hours of a writer's typing and 2,033 stored parameters per writer」 | — |
| nit 要旨の goes with | 採用。交絡の源を分けていないと書いた | — |
| nit 4.4 の入れ替えの段が詰まりすぎ | 採用。最頻値の 2 つの対照と入れ替えで段を分けた | — |
| nit reported post hoc の位置 | 採用。「The chosen τ, reported post hoc, is ...」 | — |
| nit asymmetric one | 採用。shared-only refit に | — |

今回は、上の各指摘が解消したかを 1 件ずつ「解消 / 一部 / 未解消」で判定し（位置と逐語を添える）、そのうえで新しい穴を探してください。前の指摘の再掲は求めません。 特に今回の直しで書き換えた部分（要旨・序論・4.4 の入れ替えの段・表 3・考察の決定の段・推奨 (2)・結論）が、新しい矛盾や言い過ぎを生んでいないか、使う側が持ち帰れるものが残っているかを見てください。
