# context-B —— 意図の監査役にだけ渡すもの（round 4・下書き 2026-11-11）

## 想定読者と変えたいこと
行動ログ（打鍵・操作の履歴）から 1 人ごとのモデルを作る個人化の研究者と、適応する系の設計者。「本人で学ぶと良くなる」と主張する前に、3 つの相手と比べるようにさせる: 構造を良くした共通のモデル（本人を除いて当てた・構造と縮小の強さを他人で選んだ）、その共通の事前分布の最頻値（本人のデータを使わない）、本人の 1 次のマルコフ。最頻値と共通そのものは選ぶ候補にも置く。

## 持ち帰ってほしいこと（メインが書いた）
1. 1 人ごとの系列のモデルの上積みは、比べの相手で大きく変わる。CoAuthor では 3 状態の HMM の本人の当てはめが同じ構造の共通に勝つが、構造と縮小の強さを他人で選ぶと AR(1)-HMM が選ばれ、共通に対する残りは 1 記号あたり 1e-3 nats 以下（手順が返した量で、個人差の上限ではない）。その残りは、共通の事前分布の最頻値に対しては上回らない（15-session のパネルで中央値が負）。CS1 では最頻値（候補に無ければ共通そのもの）が全員に選ばれ、差は作りの上で 0。
2. この比べ方（評価の手順）を、パネル全体で 1 人ごとのモデルを使うかを決める研究に勧める。残りの大きさは記号化に依る。
3. 本人の 1 次のマルコフは強い基準で、3 状態の HMM はそれに負ける。

## 既知の限界と範囲の外
- データは 2 つ（CoAuthor のセッション・CS1 の課題）・主の結果の量子化は 26 記号の 1 種類・重なる窓の記号化。セッションと課題は日ではない。
- EM の状態に名前を付けない。作業上の認知状態の構造とは読まない。検定と閾値を置かない（記述・中央値と四分位と良い側の割合と人数）。
- 解析は前の結果を見て順に設計した（探索的）。構造の格子は 3 状態で止まり、ar3 がすべてのセルで上端に選ばれた。
- 手順の感度: 既知の大きさの個人差を埋めた合成（条件はコードより前）で、CoAuthor の記録の量では 1e-2 未満を拾えず、返る量は埋めた差の 0.1〜0.4。CS1 の形では 1e-3 から各段 2 種とも拾えた（陰性対照 5 種）。5/17 人だけの差はパネルの中央値で拾えない。
- 最頻値の分解（残りを最頻値と共通の差と本人の寄与に分ける）は、合成で差 0 と埋めた差を分けなかったので根拠に使わない（合成では最頻値がいつも共通より悪く、実データの形を確かめる作りでなかった・回し直さない）。
- 最頻値は確率 0 のセルを持ちうる。他人で選ぶと、その最頻値の下で確率 0 になる書き手に割り当てられることがあった（k = 1〜8 の 1 人）。
- 選びの目的は他人の「本人 − 連鎖」の中央値で、予測の良さとも個人化の利得とも同じではない。他人で選ぶ選びは、対象の書き手の訓練の単位を含む他人の共通を使うので、到着の前に固定した選びではない。
- 後から足した確かめ: 平滑の無い記号と擬似残差のモデル検査、構造の補いの読みの確かめ（事前に決めた形では支持されず、主の結果の説明に使わない）、感度の合成、最頻値を相手と候補に置く集計。

## 意図の資料（読んでよい・指定の節まで）
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/requirement.md（全体）
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/decisions.md（判断 10〜24）
- /Users/johnd/GSE-prototype-paper3/.steering/20261111-gse-paper3-round3-computations/decisions.md（判断 1〜7）
- /Users/johnd/GSE-prototype-paper3/experiments/20261104-timeseries-tau-extend/notes.md（「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261106-tau-mode-candidate/notes.md（「論文 3 へのつなぎ」と「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261107-unsmoothed-residual-check/notes.md（「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-structure-deficit/experiments/20261107-structure-deficit-test/notes.md（「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261110-per-person-sensitivity/notes.md（「D7 の当て」「外枠への持ち込み」「結果を見た後に気づいたこと」「追記の結果」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261111-sensitivity-mode-decomposition/notes.md（全体）
- /Users/johnd/GSE-prototype-paper3/experiments/20261111-mode-in-selection/notes.md（全体）
