# context-A（prereg-window-overlap round 4・stage prereg）

## 対象物

窓の重なりの用量反応の実験の条件（事前登録の下書き・凍結の前）。commit a2d3413c（第 4 版）（枝 exp/gse-per-person-window-overlap）。コードと実データの計算はまだ無い。この条件は、論文 3（per-person-learning・付録 S13 と本文の Discussion の第 1 段落）の仕組みの主張を確かめるために書かれた。条件の本文は、前の試験（S13 の試験）から変える所だけを書き、書いていない所は前の試験の条件のとおりとする。

## 読んでよいファイルの一覧（これだけ）

| ファイル | 印 | 役割 |
|---|---|---|
| /Users/johnd/GSE-prototype-window-overlap/experiments/20261127-window-overlap-dose/conditions.md | 本体 | 対象物 |
| /Users/johnd/GSE-prototype-window-overlap/experiments/20261127-window-overlap-dose/SEED | 固定の根拠 | 乱数の種 |
| /Users/johnd/GSE-prototype-window-overlap/experiments/20261107-unsmoothed-residual-check/conditions.md | 固定の根拠 | 引き継ぐ前の試験の条件（S13 の試験） |
| /Users/johnd/GSE-prototype-window-overlap/experiments/20261107-unsmoothed-residual-check/notes.md | 固定の根拠 | 前の試験の結果（集計値・端の値の開示の確かめに使う） |
| /Users/johnd/GSE-prototype-window-overlap/experiments/20261104-timeseries-tau-extend/conditions.md | 固定の根拠 | 前の試験がさらに引き継ぐ条件 |
| /Users/johnd/GSE-prototype-window-overlap/papers/per-person-learning/kit/symbols/variants.py | 固定の根拠 | 重ならない窓の間引きの規則（thinned_mask） |
| /Users/johnd/GSE-prototype-window-overlap/papers/per-person-learning/kit/symbols/README.md | 固定の根拠 | 記号化の説明 |
| /Users/johnd/GSE-prototype-window-overlap/experiments/20261107-unsmoothed-residual-check/scripts/load.py | 固定の根拠 | 差し替える列の読み込み |
| /Users/johnd/GSE-prototype-window-overlap/experiments/20261107-unsmoothed-residual-check/scripts/fit.py | 固定の根拠 | 読み込んで使う当てはめの駆動 |
| /Users/johnd/GSE-prototype-window-overlap/experiments/20261107-unsmoothed-residual-check/scripts/residual.py | 固定の根拠 | 読み込んで使う擬似残差 |
| /Users/johnd/GSE-prototype-window-overlap/experiments/20261107-unsmoothed-residual-check/scripts/pinned.py | 固定の根拠 | SHA-256 の照合 |
| /Users/johnd/GSE-prototype-window-overlap/papers/per-person-learning/manuscript/main.tex | 文脈 | 論文 3 の本文（確かめたい主張は Discussion の第 1 段落（331 行）と 136・223・340 行） |
| /Users/johnd/GSE-prototype-window-overlap/papers/per-person-learning/manuscript/supplement.tex | 文脈 | 論文 3 の補足（S3 記号化・S12・S13） |

## 測った値

- 対象物の conditions.md は 271 行。前の試験の conditions.md 139 行・notes.md 143 行。
- 計算の見積もり（対象物の D6）: Mac で、HP Z2 の約 2.5〜3 時間の数倍。

## 規程

事前登録は repo への commit で凍結する内部の登録で、登録所の書式の規程は無い。論文 3 の投稿先の規程は今回の対象ではない。
