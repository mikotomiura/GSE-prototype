# context-B —— 意図の監査役にだけ渡すもの（round 1）

## 想定読者と変えたいこと
行動ログ（打鍵・操作の履歴）から 1 人ごとのモデルを作る個人化の研究者。「本人で学ぶと良くなる」と主張する前に、共通の側の構造を良くした相手（同じ構造の共通のモデル・本人の 1 次のマルコフ）と比べるようにさせる。

## 持ち帰ってほしいこと（メインが書いた）
1. 1 人ごとの系列のモデルの上積みは、比べの相手の構造で決まる。3 状態の HMM では本人の当てはめが共通に勝つが、構造と縮小の強さを他人で選ぶと前の記号を条件にした AR(1)-HMM が選ばれ、本人の上積みは CoAuthor で約 1e-3 nats/記号以下（再現の検査のずれと同じ桁）、CS1 で 0 になる。
2. 3 状態の HMM は本人の 1 次のマルコフに負けるので、個人化の比べには 1 次のマルコフの基準を置くべきである。
3. 本人で勝っていたのは構造の足りなさを補っていたからかもしれないが、確かめていない（同じ向き・族 2 つ・量子化 1 つ）。

## 既知の限界と範囲の外
- データは 2 つ（CoAuthor のセッション・CS1 の課題）・量子化は 26 記号の 1 種類。セッションと課題は日ではない。
- EM の状態に名前を付けない。作業上の認知状態の構造とは読まない。閾値と検定を置かない（記述・中央値と四分位と良い側の割合）。
- 大きい縮小での約 1e-3 の差は、書き手ごとの配分ではなく中央値の比べ。CS1 は但し書きを残す。
- 仮説の試験（構造の族・量子化の列を増やす）は別の論文。この論文の範囲は 4 つの試験で凍結。

## 意図の資料（読んでよい・指定の節まで）
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/requirement.md（全体）
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/decisions.md（判断 1〜9）
- /Users/johnd/GSE-prototype-paper3/experiments/20261104-coauthor-ml-improve/notes.md（「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261104-timeseries-tau-extend/notes.md（「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261106-tau-mode-candidate/notes.md（「論文 3 へのつなぎ」と「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/docs/literature/20261107-per-person-gain-comparison-baselines.md（冒頭の「要点」の表と「論文 3 への還元」）
