# 引き継ぎ（E・投稿先の担当編集者・round 5 → round 6）

round 5 の版は commit cc30d57f、今回の版は e6fdad49。行番号は変わったので、今の main.tex で文から探してください。各指摘の裏取りの判定は、断りの無いものは「真」でした。round 5 のあなたの判定は「直してから回す」でした。本文は 7,013 語から 7,219 語（+206）になった。足した分の一部は、細部を補足へ移して相殺した。

| round 5 の指摘 | 著者の採否と対応 | 未解決（著者の認識） |
|---|---|---|
| M1 要旨の後半が想定読者に読めない | 一部採用。要旨の末尾の節（満たせなかった要件）を外し、「improvement」を「the effect of the shared model's smoothing」の中立の語に、結果を見た後の変更を「The candidate grids were extended, and two checks added, after seeing results」に。要旨から両側の値（3〜7e-3）を外す案は採らなかった | — |
| M2 重ならない窓の逆転が本文で数値なしで埋もれ、結論で解釈なしで終わる | 一部採用。4.2 で、記号が約 1/30 でデータの量も映しうること・合成で確かめていないことを書き、結論は「発見は重なる窓の記号に限る・記号化を比べと一緒に報告する」で閉じた。値は本文に出さない | 値は補足 S13（著者の判断） |
| M3 remainder が定義の外でも使われている | 採用。3.4 の定義に対称の当て直しでは構造を固定することを足し、同じ量の advantage を gain / remainder にそろえた | — |
| M4 決定の段の答えが 2 つの平滑に割れている | 採用。確かめた／確かめていないの段を決定の段の前に置き、決定の段で、固定の平滑の 5e-4 は本人のデータの価値を示さない（最頻値・共通の平滑を軽くするだけの利得と並べた）、決定に関わる比べは両側に同じ平滑を当てた版、と書いた | — |
| m1 但し書きの繰り返し | 一部採用。割合の断り・確率 0 の 2 人・CS1 の理由・閾の確率の注などを補足へ移した | 「not checked against synthetic writers」はまだ 4 回ある |
| m2 定義なしの語 | 採用。perplexity を序論で平易に定義、idiographic に括弧の言い換え、DIC を展開、main row を外し、full protocol を joint choice にそろえた | — |
| m3 本文に置かなくてよい細部 | 採用。Code availability の列挙・4.4 と 4.5 の細部を補足へ | — |
| m4 新規性の置き方 | 採用。序論の第 2 段に、系列のモデルでは同じ構造の共通は自然な比べだが構造が依存を運べないとき弱い、と 1 文 | — |
| m5 考察の冒頭が新しさの対象を取り違える | 採用。考察の冒頭を「the per-person gain that the natural comparison, a shared model of the same weak structure, shows is far larger than the remainder against a stronger comparison chosen on other people」に | — |
| n1 図と表で量の名前が出ない | 一部採用。Table 2 の題を gain と remainder の語で書いた。図は変えていない | 図の軸 |
| n2 Figure 1 が中心の仕組みを示さない | 採らなかった（著者の判断） | — |

今回は、上の各指摘が解消したかを 1 件ずつ「解消 / 一部 / 未解消」で判定し（位置と逐語を添える）、そのうえで編集者として読み直してください。前の指摘の再掲は求めません。特に、要旨と序論だけから目的・方法・分かったことが想定読者に言えるか、直しで本文が伸びて貢献が埋もれていないかを見てください。
