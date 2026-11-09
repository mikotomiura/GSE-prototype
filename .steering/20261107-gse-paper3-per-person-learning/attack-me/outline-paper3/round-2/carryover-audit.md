# 引き継ぎ（意図の監査役・round 1 → round 2）

round 1 のあなたの指摘と、裏取り・研究者の採否・対応。採否はすべて研究者が承認した。各行が外枠（commit 143fd602）で解消したかを判定してください。意図（context-B）も round 2 で書き直した（中心を評価の手順と実例に・後から足した 2 つの確かめ）。

| # | round 1 の指摘 | 裏取り | 対応 |
|---|---|---|---|
| 1-1 | CS1 では hmm3 の本人が共通に一貫して勝たないのに、take-home と C1 の Evidence が両データで勝つように読める | 真 | 実例を CoAuthor に限り、CS1 は「一貫して勝たない」と書いた。take-home は「can gain a lot」 |
| 3-1 | C3 の格子の拡張の目的の 2 つの書き方が食い違う | 真 | 目的を「端の選択を読めるように」の 1 つに（C1 Protocol） |
| 3-2 | パネルの呼び方の不揃い | 真 | 15-session・30-session・five-assignment に揃えた |
| 3-3 | 持ち帰り 1 が notes より強い | 真 | context-B を書き直した |
| 3-4 | tau-mode notes の 10^5 の扱いの食い違い | 真 | 外枠では大きい縮小での残りを「中央値で比べると最頻値の側が大きい」と書き、S9 に置いた |
| 3-5 | Status が古い | 真 | 更新した |
| 3-6 | 照合できなかった値 | +4.1e-4〜+7.2e-4 は偽陽性（tau-extend の結果 3 の P15 の行）。他は指定の節の外 | 意図の資料に節を足した |
| 3-7 | CS1 の単位が分からない | 真 | CS1 は課題（five-assignment panel・評価は最後の課題） |
| 他 | τ = ∞ を pooled limit と呼ぶ・§3.2 の timing・README の語 | 真 | "the shared model itself (tau = infinity)"・合成の打鍵の特徴・README の語を外した |
