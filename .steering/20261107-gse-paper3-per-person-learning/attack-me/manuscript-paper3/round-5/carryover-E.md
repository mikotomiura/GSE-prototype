# 引き継ぎ（E・担当編集者・round 4 → round 5）

round 4 の版は commit d6587f21、今回の版は cc30d57f。行番号は変わったので、今の main.tex で文から探してください。各指摘の裏取りの判定は、断りの無いものは「真」でした。著者の方針: 新しい計算はせず、書き方で直した。

| round 4 の指摘 | 著者の採否と対応 | 未解決（著者の認識） |
|---|---|---|
| N1 要旨と結論が違う話・逆転が要旨に無い | 一部採用。要旨の推奨に範囲の語「For overlapping-window symbols」を足し、2 つの post hoc の括弧を 1 つにまとめた。重ならない窓での逆転そのものは要旨に入れない（考察と結論に置く）。序論の「the positive instance」を「one dataset, CoAuthor, and one symbolization」に。結論に発見の文を戻した | 要旨に逆転を入れない |
| N2 要旨と序論に定義の無い語 | 採用。要旨は「the improvement from removing the shared model's smoothing」の平易な句に、本文は smoothing effect を 3.3（Prior mode の段落）で 1 回定義。7e-3 は「smoothing chosen on other writers (the grid's lightest)」に | — |
| N3 gain の別の意味・1 概念 2 語 | 採用。gain は定義の 1 義、連鎖との差は per-person minus own chain、平滑の差は smoothing effect。first null / second null、AR-HMM にそろえた | — |
| N4 同じ但し書きの繰り返し | 採用。要旨・該当の結果の節・限界の 1 回ずつを目安に減らし、表の題は節を指す | — |
| N5 Figure 1 に中心の仕組みが無い | 採らなかった（図の範囲は採点のしかたの例のまま） | — |
| N6 初見で追えない段落 | 採用。3.6 で first null・replicate（1 つの種の合成のパネル）・negative controls（差を植えない replicate）を定義した | — |
| N7 本文に置かなくてよい細部 | 採用。4.4 の二分の後半と確率 0 の書き手の細部の一部・限界の規則の文と開始点の項目を補足へ移した | — |
| N8 推奨 (2) の「使った」の範囲 | 採用。(2) に post hoc・1 構造 1 パネル・格子の端の断り | — |
| N9 図の番号と参照の順・図の語 | 採用。序論から Figure 1 を先に引く・Table 2 の略号を語に・Figure 3 (b) の題を own chain に | — |
| N10 考察が「決定」で始まり序論の貢献と 1 つにならない | 採用。考察の冒頭を発見の段（What is new を移した）に、決定はその次の段に。結論に発見の 1 文を戻した | — |

本文は 6,939 語から 7,013 語に増えた（+74。考察の発見の段と決定の段・4.5 の植えた差の文・smoothing effect の定義を足し、細部の一部を補足へ移した）。

今回は、上の各指摘が解消したかを 1 件ずつ「解消 / 一部 / 未解消」で判定し（位置と逐語を添える）、そのうえで新しい穴を探してください。前の指摘の再掲は求めません。特に、要旨と序論だけから 1 文が言えるか、考察と結論の貢献が序論と 1 つになったか、語の統一（gain・smoothing effect・remainder）が本文と図表で守られているか（見ること 7）を見てください。
