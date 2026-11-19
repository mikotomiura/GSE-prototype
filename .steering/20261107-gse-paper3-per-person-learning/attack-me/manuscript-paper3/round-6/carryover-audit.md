# 引き継ぎ（意図の監査役・round 5 → round 6）

round 5 の版は commit cc30d57f、今回の版は e6fdad49。行番号は変わったので、今の main.tex で文から探してください。各指摘の裏取りの判定は、断りの無いものは「真」でした。意図（context-B.md）の持ち帰り 1〜3 は、判断 32・33 に合わせて書き直した（5e-4 は本人のデータの価値を示さない・決定に関わる比べは両側の版・発見は重なる窓に限る）。

| round 5 の指摘 | 著者の採否と対応 | 未解決（著者の認識） |
|---|---|---|
| 1-1 重ならない窓の結果を合成で確かめていないことが無い | 採用。4.2・考察の Relation・結論に、合成で確かめていないこととデータの量も映しうることを書いた | 値は補足 S13 |
| 1-2 決定の段に「決定は記号化に依る」が無い | 採用。決定の段の冒頭に「the choice depends on the symbolization」 | — |
| 1-3 τ = 10^6 と構造が格子の端であること・格子の拡張が要旨・考察・結論に無い | 一部採用。要旨に「The candidate grids were extended ... after seeing results」。推奨 (2) に倍率が格子の端であること。τ と構造が格子の端であることは限界にだけある | 要旨・結論の格子の端 |
| 2-1 要旨が結果を見た後の変更を 2 つに減らす | 採用（1-3 と同じ直し） | — |
| 2-2 smoothing effect が「improvement」に固定 | 採用。要旨は「the effect of the shared model's smoothing」 | — |
| 2-3 remainder の定義からはみ出た使い方 | 採用。3.4 の定義に対称の当て直しでは構造を固定することを足した。advantage を gain / remainder にそろえた | — |
| 2-4 要旨の検出の文から planted が落ちる | 採用。「planted differences up to 3×10^-2」 | 2 つ目の帰無であることは要旨に無い（語数） |
| 2-5 4.3 の見出しに固定の平滑の限定が無い | 採用。「at the fixed smoothing」 | — |
| 2-6 考察の冒頭が弱さの所在を「同じ構造」に移す | 採用。「a shared model of the same weak structure」と「a stronger comparison chosen on other people」に | — |
| 2-7 推奨 (2) と 4.4 の版の取り違え | 採用。「as recommendation (2) below asks」を外し、決定の段で「Done post hoc in the 15-session panel with the structure fixed at the 3-state AR-HMM」と書いた | — |
| 3-1 L317 の論理が逆 | 採用。片側だけでは消え、両側では 6〜12.5 倍で戻った、の向きで書き直した | — |
| 3-2 向きだけで読むと書いたのに大きさの文 | 採用。大きさの文を外した | — |
| 3-3 4.4 の二分の文が意図の資料とずれる | 採用。「most choices sit at the edge of a grid」に | — |
| 3-4 比の地位の印が節で違う | 採用。序論で帰無に post hoc、比に not prespecified を分けた | — |
| 3-5 結論の重ならない窓の文が 2 つの選びを 1 つにする | 採用。結論を「the three-state HMM is chosen and its per-person fit keeps the direction of a gain」に | — |
| 3-6 要旨の CS1 の文に固定の平滑の限定が無い | 採用。「at the fixed smoothing」 | — |

今回は、上の各指摘が効いているかを確かめ、そのうえで新しい食い違いを探してください。特に、今回の直し（要旨・考察の 3 つの段・結論）で平易な語への言い換えが新しい漂流を生んでいないか（「does not show a value of the writer's data」の根拠と範囲、両側の版の τ の範囲の言い方、重ならない窓の「データの量も映しうる」の言い方）を見てください。
