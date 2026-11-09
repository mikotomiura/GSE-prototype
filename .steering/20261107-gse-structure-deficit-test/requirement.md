# 構造の足りなさの仮説を確かめる試験（structure-deficit-test）

## 背景

- `experiments/20261104-coauthor-ml-improve/notes.md`（185 行）の読みの仮説: B で本人の EM が共通に勝っていたのは、3 状態の HMM が前の記号への強い依存を運べず、その不足を本人の当てはめが一部埋めていたためかもしれない（人ごとの違いではなく、構造の足りなさを人ごとに補っていた）。
- `experiments/20261104-timeseries-tau-extend/notes.md`: hmm3 で本人の上積みが大きく（CoAuthor で最大 +0.19）、ar1〜ar3 で小さい（約 1e-3 以下）。「仮説と同じ向き」とだけ書いた。構造の族が 2 つ・量子化の列が 1 つだけだから。
- `experiments/20261106-tau-mode-candidate/notes.md`: CoAuthor の ar の大きい τ での差は主に最頻値と共通の違い（形 1）。hmm3 は形 2（本人の寄与が主）。
- 対抗する説明: 母数が多い構造ほど本人の記録では推せず、上積みが小さく見えるだけ。前の試験の hmm6・hmm10 の上積みが小さいことは、仮説とこの説明の両方で説明できる。
- 引き継ぎ: `.steering/_handoff/next-session-gse-hypothesis-structure-test.md`。研究者が 2026-11-07 に「論文 3 と並行して回す・結果は論文 3 に入れない」を選んだ。

## ゴール

構造の族（hmm3・hmm6・hmm10・ar1・ar2・ar3）× 量子化の列（10・26・50 記号）×（そのまま・セッションの中で記号の順を並べ替えた列）で、本人の上積み G と構造の足りなさ D を書き手ごとに出し、結果を見る前に決めた読みの形 A・B・C のどれに当たるかを書く。

## スコープ

### 含むもの
- 条件（`experiments/20261107-structure-deficit-test/conditions.md`）と `SEED` を、コードより前にコミットする。
- 前の試験のコード（`experiments/20261106-tau-mode-candidate/scripts/`）を写して変える。量子化の列の作り直し（ewma_x・ewma_y から）と並べ替えを足す。
- Mac の合成で陽性対照・変異の門・時間の見積もりを通す。
- 職場の PC（HP Z2）で回す手順を引き継ぎに書く。本計算は職場の PC。
- 結果の後の notes・code-reviewer・/cross-review（Codex を加える）。

### 含まないもの
- 結果を論文 3 に入れること（論文 3 の範囲は凍結）。
- 結果を段 1 の候補の採否や ADR-047 の根拠にすること（D2・D6）。
- AR(2) 以上の構造。1 軸の量子化の列。副のパネル。
- EM の状態に名前を付けること・閾値と検定を置くこと・CS1 を日本語や GSE の参加者へ広げること。
- 書き手ごとの値・共通の母数を repo に入れること・holdout の一覧を開くこと。
- push と PR（研究者が確かめてから）。

## 受け入れ条件

- [x] 条件と SEED のコミットが、コード（scripts/）のコミットより前にある。
- [x] Mac の合成で陽性対照がすべて通り、名指しの変異がすべて赤になる（変異の門）。
- [x] 量子化の門: 26 記号の列を ewma_x・ewma_y から作り直すと、全データの全 feat 行で obs と一致する（職場の PC で照らす。Mac は合成で門の働きを確かめる）。
- [x] P-REPRO: 26 記号・そのままの列の重なる行が前の試験の summary と照らせる（職場の PC）。
- [x] 時間の見積もりを Mac の合成の実測から条件に書く。
- [x] 職場の PC で回す引き継ぎがある。
- [x] 計算の前の code-reviewer の HIGH が直っている。

## 関連ドキュメント

- `experiments/20261104-timeseries-tau-extend/conditions.md`・`notes.md`
- `experiments/20261106-tau-mode-candidate/conditions.md`・`notes.md`・`scripts/`
- `experiments/20261104-coauthor-ml-improve/notes.md`
- `.steering/_handoff/next-session-gse-tau-mode-candidate-run-on-hp-z2.md`
- `docs/experiment-tracking.md`（reproducibility-discipline）

## 運用メモ
- /reimagine 適用: Yes
- 理由: 引き継ぎが指定。対照（並べ替え）・D の定義・量子化の作り方に複数の案があり、最良案が自明でない。
