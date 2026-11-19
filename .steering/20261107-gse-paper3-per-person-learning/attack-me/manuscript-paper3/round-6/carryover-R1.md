# 引き継ぎ（R1・行動の記号列の系列モデルの方法論の立場・round 5 → round 6）

round 5 の版は commit cc30d57f、今回の版は e6fdad49。行番号は変わったので、今の main.tex で文から探してください。各指摘の裏取りの判定は、断りの無いものは「真」でした。著者の方針: 新しい計算はせず、書き方と既存の集計の提示で直した。考察は「発見の段 → 確かめた／確かめていないの段（What was established and what was not）→ 決定の段（What the protocol returns）」の順にした。

| round 5 の指摘 | 著者の採否と対応 | 未解決（著者の認識） |
|---|---|---|
| M1 要旨の「Two checks came after seeing results」が主結果に効く事後の変更を隠す | 採用。要旨を「The candidate grids were extended, and two checks added, after seeing results.」に | — |
| M2 重ならない窓の比べで記号の数（約 1/30）とパラメータの数が交絡 | 採用。4.2 の大きさの文（does not fall by two orders of magnitude）を外し、記号が少なくパラメータの多い構造は推定しにくいので逆転はデータの量も映しうること・合成で確かめていないことを書いた。考察の Relation と結論も「データの量も映しうる」「発見は重なる窓の記号に限る」で閉じた | 値（k = 5・15 の差）は本文に出さず補足 S13（著者の判断） |
| M3 決定の段の「loses about 5e-4」は書き手のデータを使わずに取り戻せる | 採用。決定の段と結論で、5e-4 は最頻値（書き手のデータを使わない・+7.4e-4）や共通の平滑を軽くするだけの利得（+1.6e-3）と並べ、本人のデータの価値を示さないと書いた。「失う精度」の文は外し、決定に関わる比べは両側に同じ平滑を当てた版だとした | — |
| m1 両側の当て直しの残り（3〜7e-3）に重みと対照が無い | 一部採用。両側の版で選ばれる τ の範囲（10^2〜3×10^5・全員が格子の中）と、本人のデータの重みが固定の平滑のとき以上になることを決定の段に 1 句。書き手ごとの τ は出さない（限界に「格子の中としかまとめていない」）。平滑の効きに当たる対照は新しい計算になるので足していない | 両側の版の対照・合成の確かめは無い |
| m2 要旨の「two orders of magnitude」に k が無い | 採用。「at five and fifteen training sessions」 | — |
| m3 要旨の CS1 の文に平滑の断りが無い | 採用。「at the fixed smoothing」 | — |
| m4 3-state AR-HMM と own chain の残差の自己相関の値 | 採らなかった（残差の点検の要約は補足 S13 の予定・既知の未決 7） | — |
| m5 「What was established」の最後の文の論理 | 採用。「Lightening the smoothing of the shared model alone made the remainder vanish; applying the same smoothing to both models (post hoc) brought it back, about 6 and 12.5 times larger at k=5 and 15.」に | — |
| n1 4.5 の括弧の対応 | 採用。「873 of 935 at k = 5 and 783 of 935 at k = 15」の形に | — |
| n2 要旨が上限ちょうど | 採用。末尾の節を外して 248 語 | — |

今回は、上の各指摘が解消したかを 1 件ずつ「解消 / 一部 / 未解消」で判定し（位置と逐語を添える）、そのうえで新しい穴を探してください。前の指摘の再掲は求めません。特に今回の直しで書き換えた部分（要旨・序論の第 2〜4 段落・3.3 の選びの段落・3.4 の remainder の定義・4.2・4.3〜4.5・考察の 3 つの段・限界・結論）が、新しい矛盾や言い過ぎを生んでいないかを見てください。
