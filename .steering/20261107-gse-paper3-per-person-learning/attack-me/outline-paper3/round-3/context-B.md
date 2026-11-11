# context-B —— 意図の監査役にだけ渡すもの（round 3）

## 想定読者と変えたいこと
行動ログ（打鍵・操作の履歴）から 1 人ごとのモデルを作る個人化の研究者と、適応する系の設計者。「本人で学ぶと良くなる」と主張する前に、構造を良くした共通のモデル（本人を除いて当てた・構造と縮小の強さを他人で選んだ）と、本人の 1 次のマルコフを相手に置いて比べるようにさせる。

## 持ち帰ってほしいこと（メインが書いた）
1. 1 人ごとの系列のモデルの上積みは、比べの相手で大きく変わる。CoAuthor では 3 状態の HMM の本人の当てはめが同じ構造の共通に勝つが、構造と縮小の強さを他人で選ぶと AR(1)-HMM が選ばれ、本人の上積みは 1 記号あたり数万分の 1 nats まで小さくなる（符号はほぼ全員でそろう）。CS1 では共通のモデルそのものが選ばれ、差は定義上 0。
2. この比べ方（評価の手順）を、行動の記号列の 1 人ごとのモデルの評価に勧める。
3. 本人の 1 次のマルコフは強い基準で、3 状態の HMM はそれに負ける。

## 既知の限界と範囲の外
- データは 2 つ（CoAuthor のセッション・CS1 の課題）・主の結果の量子化は 26 記号の 1 種類。セッションと課題は日ではない。
- EM の状態に名前を付けない。作業上の認知状態の構造とは読まない。検定を置かない（記述・中央値と四分位と良い側の割合と人数）。
- 解析は前の結果を見て順に設計した（探索的）。
- 手順の感度: 既知の大きさの個人差を埋めた合成（条件はコードより前にコミット）で、CoAuthor の記録の量では 1e-2 未満の個人差を拾えなかった。実データの残りは、それより小さい個人差が無いことを示さない。CS1 の形では 1e-3 から拾えた。
- 後から足した 2 つの確かめ: 平滑の無い記号と擬似残差のモデル検査（主の結果は元の記号化の上の測定に限る）、構造の補いの読みの確かめ（事前に決めた形では支持されず、主の結果の説明に使わない）。

## 意図の資料（読んでよい・指定の節まで）
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/requirement.md（全体）
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/decisions.md（判断 10〜23）
- /Users/johnd/GSE-prototype-paper3/experiments/20261104-timeseries-tau-extend/notes.md（「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261106-tau-mode-candidate/notes.md（「論文 3 へのつなぎ」と「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261107-unsmoothed-residual-check/notes.md（「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-structure-deficit/experiments/20261107-structure-deficit-test/notes.md（「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261110-per-person-sensitivity/notes.md（「D7 の当て」「外枠への持ち込み」「結果を見た後に気づいたこと」の節）
