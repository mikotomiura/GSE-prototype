# 引き継ぎ（R3・round 1 → round 2）

round 1 のあなたの指摘と、裏取り・研究者の採否・対応。採否はすべて研究者が承認した。各行が外枠（commit 143fd602）で解消したかを判定してください。

| # | round 1 の指摘 | 裏取り | 対応（外枠の位置） |
|---|---|---|---|
| 1 | [major] 解析の順の設計と格子の事後の延長で、選択が評価の外 | 真 | 3.4 に逐次の設計（構造の族の追加・格子の延長を結果の後に）・S12 に逸脱の一覧・Limitations。外側の loop に入れた値は無い（未解決） |
| 2 | [major] CS1 の exactly zero は定義上 | 真 | 「共通のモデルそのものが全員で選ばれ、差は定義上 0」 |
| 3 | [major] C2 の依存が記号化と未分離 | 真 | 平滑の無い記号・重ならない窓・擬似残差の確かめを回した（S13・Limitations）。主の結果は元の記号化の上の測定に限定 |
| 4 | [major] 不確かさと人数が本文に無い・established | 真 | 何人中何人・IQR・主表に bootstrap の区間・「observed … (exploratory)」 |
| 5 | [major] 新規性が階層・経験ベイズに対し位置づけられていない | 真 | 文献の調べ。C1 Compared with（MAP 適応・多水準 HMM・境界の分散の推定との違い）。新規性を「この比べを当てて報告した例」に |
| 6 | [minor] 文献の検索の手順 | 真 | S1 に検索の記録 |
| 7 | [minor] 組み入れと除外 | 真 | S4 に規則と人数（無限大の log loss の書き手） |
| 8 | [minor] up to +0.19 が最大値 | 真 | 値・IQR・人数で書いた |
| 9 | [minor] 照合の段の食い違い・コードの公開・データの声明 | 真 | Statements and declarations の行・open items を更新 |
| 10 | [minor] Liu & Meng の代価の側 | 真 | 「who note the cost in relevance to the individual」 |
| 11 | [nit] 代理ラベルは補足だけに | 真 | S10 |

未解決として研究者が残したもの: 選択の全体を外側の loop に入れた評価はしていない（逐次の設計を開示して限界に置いた）。
