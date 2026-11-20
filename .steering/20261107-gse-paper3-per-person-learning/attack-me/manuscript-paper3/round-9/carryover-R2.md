# 引き継ぎ（R2・個人化した行動のモデルの実務の立場・round 8 → round 9）

round 8 の版は commit 77d5f324、今回の版は 1f4f4b5b。行番号は変わったので、今の main.tex で文から探してください。各指摘の裏取りの判定は、断りの無いものは「真」でした。著者の方針: 新しい計算はしていない（すべて書き方の直し）。入れ替えの対照の読みは、計算の前に決めた規則（自分の回で当てた当てはめが入れ替えに勝つ差 ≥ 残りの半分）として書き、差は残りの分け前ではない（入れ替えは共通にも負け、他人のデータの害を含む）と断った。別の書き手の k 単位は記号数も違い、同じ τ でも重みが変わることを、時間の近さと並ぶ交絡として断った（計算はしない）。入れ替えの対照は推奨に入れず、考察で点検の候補として 1 句にした。

| round 8 の指摘 | 著者の採否と対応 | 未解決（著者の認識） |
|---|---|---|
| minor 1 「more than half」の算出と、入れ替えが不一致の罰を含むこと | 採用。読みを計算の前に決めた規則として書き、差は分け前ではなく他人のデータの害を含むと断った。記号数の交絡も断った | 中立な作り直しの対照は計算しない |
| minor 2 入れ替えの差と植えた差の桁 | 採用。考察の確かめた段に「The margin of the swap control, up to 2.5e-2, is not on the scale of the planted differences, since it includes the loss from fitting another writer's data」 | — |
| minor 3 決定の段の冒頭が無条件・費用の目安 | 一部採用。冒頭を「at the fixed base smoothing」に限り、適応の場面の例（書き手の予測した状態でヒントの時機を決める支援）と、その決定が変わるかは測っていないことを 1 文。母数の数と待つ記号数は足していない | 費用の目安の量 |
| minor 4 入れ替えの対照を推奨に入れる | 推奨には入れず、考察の推奨の後の段に「a cheap candidate check ..., although here it did not separate the person from closeness in time or from the amount of data」 | — |
| nit 5 「left the median remainder unchanged」 | 採用。「left the median difference from choosing on the reported half at zero」 | — |
| nit 6 結果が方法の節にある | 採用。先頭の記号を除いた値を 4.4 の 1 段へ移し、3.4 は参照だけ | — |
| nit 7 Saeb の days | 採用。2 か所を records に | — |
| nit 8 fixed smoothing の揺れ | 採用。fixed base smoothing と symmetric refit に統一 | — |

今回は、上の各指摘が解消したかを 1 件ずつ「解消 / 一部 / 未解消」で判定し（位置と逐語を添える）、そのうえで新しい穴を探してください。前の指摘の再掲は求めません。 特に今回の直しで書き換えた部分（要旨・4.4 の対照の段・考察の決定の段・結論）が、新しい矛盾や言い過ぎを生んでいないか、使う側が持ち帰れるものが残っているかを見てください。
