# context-B —— 意図の監査役にだけ渡すもの（round 5）

## 想定読者と変えたいこと
行動ログ（打鍵・操作の履歴）から 1 人ごとの系列のモデルを作る個人化の研究者と、適応する系の設計者。「本人で学ぶと良くなる」と主張する前に、3 つの相手と比べるようにさせる: 構造と縮小の強さを他人で選んだ共通のモデル（本人を除いて当てた）、その共通の事前分布の最頻値（本人のデータを使わない・平滑の擬似度数を除いた期待度数）、本人の 1 次のマルコフ。最頻値は比べの相手に置く（候補には置かない）。

## 持ち帰ってほしいこと（メインが書いた）
1. 比べの相手が弱いと 1 人ごとの系列のモデルは大きく勝つが、構造と縮小を他人で選ぶと、CoAuthor の 15-session のパネルの残りは手順の検出の下限より下で、本人のデータを使わない最頻値を上回らない。残りの大部分は共通の平滑と最頻値の差である（本人の上積みではない）。CS1 では共通そのものが選ばれる。
2. この比べ方を、パネル全体で 1 人ごとのモデルを使うかを決める研究に勧める。残りの大きさは記号化に依る。手順は埋めた差の一部しか返さないので、記録の長さでの検出の下限を合成で報告する。
3. 重なる窓の記号化では、本人の 1 次のマルコフは強い基準で、3 状態の HMM はそれに負ける。

## 既知の限界と範囲の外
- データは 2 つ・主の量子化は 26 記号の 1 種類・重なる窓の記号化。セッションと課題は日ではない。CS1 の評価の記号は約 7 割が休止の秒。
- EM の状態に名前を付けない。検定と閾値を置かない。
- 解析は前の結果を見て順に設計した（探索的）。構造の格子は 3 状態で止まり、ar3 がすべてのセルで選ばれた。
- 最頻値に勝たないことは個人差の不在を示さない。30-session の k = 30 では本人が最頻値を上回る（9 人・読みに使わない）。
- 選びの目的（他人の中央値）は予測の良さそのものではない。平均の対数尤度で選んでも読みは同じだった。選びは到着の前に固定したものではない。
- 最頻値の分解は合成で較正できず、根拠に使わない。

## 意図の資料（読んでよい・指定の節まで）
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/requirement.md（全体）
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/decisions.md（判断 10〜24）
- /Users/johnd/GSE-prototype-paper3/.steering/20261111-gse-paper3-round3-computations/decisions.md（判断 1〜10）
- /Users/johnd/GSE-prototype-paper3/experiments/20261104-timeseries-tau-extend/notes.md（「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261106-tau-mode-candidate/notes.md（「論文 3 へのつなぎ」と「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261107-unsmoothed-residual-check/notes.md（「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-structure-deficit/experiments/20261107-structure-deficit-test/notes.md（「言えること・言えないこと」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261110-per-person-sensitivity/notes.md（「D7 の当て」「外枠への持ち込み」「結果を見た後に気づいたこと」「追記の結果」の節）
- /Users/johnd/GSE-prototype-paper3/experiments/20261111-sensitivity-mode-decomposition/notes.md（全体）
- /Users/johnd/GSE-prototype-paper3/experiments/20261111-mode-in-selection/notes.md（全体）
- /Users/johnd/GSE-prototype-paper3/experiments/20261111-objective-and-pause/notes.md（全体）
