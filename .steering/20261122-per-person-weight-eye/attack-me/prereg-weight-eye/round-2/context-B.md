# context-B（意図の監査役にだけ渡す）

## 意図の資料（絶対パスと節）

- /Users/johnd/GSE-prototype-weight-eye/.steering/20261122-per-person-weight-eye/requirement.md（全体: 背景・ゴール・Done・Stop・スコープ）
- /Users/johnd/GSE-prototype-weight-eye/.steering/20261122-per-person-weight-eye/decisions.md（判断 1〜19。判断 4・5 は判断 11・12 で改めた。判断 13〜19 は round 1 の対応）
- /Users/johnd/GSE-prototype-weight-eye/.steering/20261122-per-person-weight-eye/design.md（実装アプローチ・目の候補・選びと止め）

## 想定読者

行動データの個人差のモデル（本人ごとの学習・縮み）を扱う研究者。論文 3 を読んだ人。

## 持ち帰ってほしいこと（メインが書いた・未実測の数値は書かない）

1. 予測の点数で見つからなかった本人ごとの差を、同じ記録の量でパラメータの空間の「目」が拾えるかを、実データの前に合成で確かめる。
2. 目の案の選び方と止めどころは、合成の結果を見る前に 1 通りに決まっている。
3. 目が使えると分かったときだけ、実データの読みの基準を足して凍結する。

## 既知の限界

- 1 状態の表は真の生成（3・5 状態）と構造が違う。
- 第 2 の帰無の生成の母数は実データの全員の共有から当てたもので、HP Z2 にしかない。
- 実データの読みの基準（D7）はこの段では書かない。
