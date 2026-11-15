# 引き継ぎ —— 予測の検査（R1）に定義の検査を当てる

> 作成: 2026-11-15（`.steering/20261115-gse-core-and-edge/` 判断 6・ADR-054 D4）。このメモは入口で一次ではない。一次は ADR-054・論文 1・論文 2 の原稿と実験の notes。

## 0 入口の文

```
/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-r1-definition-check.md を読んで、予測の検査に定義の検査を当てる計算を /start-task から始めて。
```

- 新しい worktree を切る（本線のチェックアウトを共有しない）。論文 1 の枝 `docs/public-data-findings-paper` と論文 2 の枝 `docs/gse-paper2-stall-shape` のコードを使う。どちらを土台に切るかは grill で決める。
- 実験なので `reproducibility-discipline`（experiments/ の規約・seed・入力の固定）に従う。条件は値を見る前にコミットする（memory「必要な計算は行う」）。

## 1 なぜやるか

ADR-054 は一言を「本文を保存しない打鍵の観測から、作業の停滞についてどこまで言えるかを、予測・定義・漏れの 3 つの検査で確かめる」にした。予測の検査の材料（R1）は論文 1 の否定の結果（手で決めた推定器の 30 秒の上がりは、停滞の手前を同じ書き手の短い休止の手前から分けない）。論文 1 の感度解析（`papers/public-data-findings/manuscript/sections/results.tex:137-152`）は床・対照・層の 4 種で、停滞の定義そのものは変えていない。Codex（2026-11-15 の codex-consult）が「R3（定義しだい）は R1 にも返る」と指摘した。手順を自分の結果に当て切るのがこのタスク。

## 2 確かめる問い（grill で詰める）

- 代表的な停滞の定義（論文 2 の multiverse の中から、事前に決めた少数）で、推定器の 30 秒の上がりの AUC と、前の打鍵の単純な量の学習器の AUC の順位と差が保たれるか。
- 論文 1 の停滞の定義: 条件 A（直前 30 秒の挿入から削除を引いた押下が 1 未満）が立ち上がって θ（書き手のそれまでの打鍵間隔の 0.99 分位）続いた時点を始まりとし、始まりの手前の最後の文字の入力 u から次の文字の入力まで 30 秒以上（`papers/public-data-findings/manuscript/sections/data.tex:26-40`）。
- 論文 2 の定義の空間: `experiments/20261107-stall-shape-multiverse/`（枝 `docs/gse-paper2-stall-shape`）。

## 3 先に決めること（値を見る前にコミット）

1. 選ぶ定義の数と選び方（multiverse の軸の端と中央など）。選ぶ理由は R1 の値を見ずに書く。
2. データ。CS1 の holdout は論文 1 の確認に使ったので、新しい定義での読みは探索になる。探索と書くか、別の分け方をするか。
3. 何をもって「保たれる」とするか（順位・差の符号・帯の内外）。
4. 結果の置き場（新しい experiments/ のフォルダ）と、論文 1・2 のどちらに還元するか（還元しない選択も含む）。

## 4 既知の制約

- NDJSON・O1 の記録は外部の LLM に送らない（集計値だけ）。
- 投稿先と状態は公開物と docs に書かない。
- 結果は ADR-054 D4 の「これから」を埋めるもので、一言を変える判断は結果を見て別に行う。
