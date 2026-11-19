# 引き継ぎ（R3・評価の偏りと個人への推論の方法論の立場・round 5 → round 6）

round 5 の版は commit cc30d57f、今回の版は e6fdad49。行番号は変わったので、今の main.tex で文から探してください。各指摘の裏取りの判定は、断りの無いものは「真」でした。著者の方針: 新しい計算はせず、書き方と既存の集計の提示で直した。考察は「発見の段 → 確かめた／確かめていないの段（What was established and what was not）→ 決定の段（What the protocol returns）」の順にした。

| round 5 の指摘 | 著者の採否と対応 | 未解決（著者の認識） |
|---|---|---|
| M-1 「共通に替えると失う精度」に、本人のデータを使わない prior mode が同じだけ得ることが並んでいない | 採用。決定の段と結論で、5e-4 を最頻値（+7.4e-4）と共通の平滑を軽くするだけの利得（+1.6e-3）と並べ、本人のデータの価値を示さないと書いた。「失う精度」の文は外し、決定に関わる比べは両側に同じ平滑を当てた版だとした | — |
| m-1 要旨の「Two checks came after seeing results」 | 採用。「The candidate grids were extended, and two checks added, after seeing results.」に | — |
| m-2 「What was established」の 1 文が逆に読める | 採用。「Lightening the smoothing of the shared model alone made the remainder vanish; applying the same smoothing to both models (post hoc) brought it back, about 6 and 12.5 times larger at k=5 and 15.」に | — |
| m-3 30-session 群の地位が考察と結論に無い | 採用。考察の確かめた／確かめていないの段に、30-session 群（k = 30 で本人の重み 39%・残り 1.1e-3・区間が 0 をまたぐ）は合成の書き手でも両側の当て直しでも確かめていないと 1 文 | — |
| m-4 結論の最後の文（重ならない窓）に精査が付いていない | 採用。4.2 と結論で、記号が約 1/30 でデータの量も映しうること・合成で確かめていないことを書き、結論は「発見は重なる窓の記号に限る」で閉じた | 値は補足 S13（著者の判断） |
| m-5 要旨が検出できなかったことの条件を落とす | 一部採用。要旨は「planted differences up to 3×10^-2 were not reliably detected」に。2 つ目の帰無であること・閾が高すぎるかもしれないことは本文（4.5・考察・結論）にあり、要旨には語数のため入れていない | 要旨の条件 |
| n-1 remainder の定義と両側の当て直しの値の食い違い | 採用。3.4 の定義に「対称の当て直しでは構造を 3-state AR-HMM に固定（その panel の joint choice が全セルで選ぶ構造）」を足し、4.4 の「only」を「In the settings reported」の形に弱めた | — |
| n-2 4.4 の見出しに post hoc が無い | 採用。見出しの両側の版に post hoc | — |

今回は、上の各指摘が解消したかを 1 件ずつ「解消 / 一部 / 未解消」で判定し（位置と逐語を添える）、そのうえで新しい穴を探してください。前の指摘の再掲は求めません。特に今回の直しで書き換えた部分（要旨・序論の第 4 段落・3.3 の選びの段落・3.4・3.6・4.4・4.5・考察・推奨・限界・結論）が、新しい矛盾や言い過ぎ・分析の地位の取り違えを生んでいないかを見てください。
