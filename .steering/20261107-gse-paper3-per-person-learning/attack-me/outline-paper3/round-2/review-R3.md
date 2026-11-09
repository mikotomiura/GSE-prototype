# review-R3（評価の偏りと再現性・round 2・要約）
推奨: major（文言と報告の直しが主）。引き継ぎ 11 件中 8 解消・3 一部。評価 a3 b3 c3 d4 e4 f4。
接地: Varma "all aspects of training ... takes place on the data not left out"・total bias、Liu & Meng "Ignoring the selection bias"・"our inference will be less relevant"・"inject misinformation"。
- N1 [major] take-home の「評価のデータを使わずに選ぶ」は、候補の族と格子を結果の後に決めた手続きと食い違う（outline:7・44）。
- N2 [major] 残りの出どころは本人のデータではない。最頻値と共通が一致しない理由・人ごとの寄与の符号の人数。
- N3 [major] 手順の残りの記号化への頑健さが無い（重ならない窓）。
- N4 [major] "disappears" を判定する基準が無い・30-session の 6/9・ar1 の参考の行が一桁大きい・"up to"。
- N5 [minor] 無限大の log loss の除外が結果に依存しうる。
- N6 [minor] 3.2 の特徴量の説明が README の 5 つの特徴と食い違う。
- N7 [minor] 元の記号との一致を読者が検証できない（記号列のハッシュの公開）。
- N8 [nit] Liu & Meng の「モデルの質が個別化の上限」で位置づけ。
注入の疑い: なし。
