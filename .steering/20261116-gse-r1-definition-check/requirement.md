# 予測の検査（R1）に定義の検査を当てる

## 背景

ADR-054 D4 は、R1（論文 1 の否定の結果）に定義の検査を当てることを「これから」に置いた。引き継ぎ（`.steering/_handoff/next-session-gse-r1-definition-check.md`・origin/main）と ADR-054 Context 6 は、論文 1 の感度解析は停滞の定義を変えていない、という前提で書かれている。

一次で確かめると、推定器の側の前提は違っていた（判断 1）。

- 論文 1 の事前登録の感度（P9）は、停滞の定義を変えた 4 版を holdout で計算していた: θ を課題をまたいで累積・q = 0.995・W = 15 秒・W = 60 秒。付録の表（`papers/public-data-findings/manuscript/appendix/supplement.tex:231-234`）に載っており、推定器の 30 秒の上がりの AUC は 0.487〜0.494 で、どれも同等だった（`experiments/20261105-findings-paper1-prefreeze/results_holdout/confirm_holdout.json` の `sensitivity`）。
- 確かめていないのは次の 2 つ。
  1. 学習器（ロジスティック回帰・勾配ブースティング）は主の定義でしか回していない。推定器との順位と差（同じ対で logreg − Δp_stuck = +0.078、`experiments/20261106-findings-paper1-exploration/results/explore_comparison.json`）が、定義を変えても保たれるかは分からない。
  2. 論文 2 の定義の軸のうち、θ の分位の低い側・θ を固定秒にする版・条件 A を文字の押下だけで数える版・観測区間の切り方は、論文 1 では試していない。

## ゴール

代表的な停滞の定義で、(a) 推定器の 30 秒の上がりが帯 [0.45, 0.55] の内にとどまるか、(b) 同じ対での学習器 − 推定器の差が正のままか、を CS1 の holdout で数える。条件は値を見る前にコミットする（`experiments/20261116-r1-definition-check/conditions.md`）。

## スコープ

### 含むもの
- 新しい実験 `experiments/20261116-r1-definition-check/`（条件・スクリプト・集計値の結果・notes）
- 定義は主（門）＋ 8 つ（論文 1 の 4 版と、論文 2 の軸の未確認の端 4 つ）
- ADR-054 D4 を埋める記録と、前提の訂正の記録（main 側へ返す形は完了時に決める）

### 含まないもの
- 論文 1・論文 2 の原稿の変更（判断 4・査読の返事が来たときの改訂の材料にする）
- KLiCKe・CoAuthor・CS1 の見た書き手での計算
- 一言（ADR-054 D1）を変える判断（結果を見て別に行う）

## 受け入れ条件

- [ ] 条件（定義の選び方・基準・門）が値を見る前にコミットされている
- [ ] 門（検出器の replay との一致・主の定義での X11 の再現・論文 1 の 4 版の H1 の再現）が通っている
- [ ] 8 つの定義それぞれで (a)(b) の結果と、全体の判定が `results/` に集計値だけで書かれている
- [ ] /cross-review（Claude と Codex）を通した

## 関連ドキュメント

- `docs/adr/ADR-054-positioning-three-checks.md`（origin/main）D4
- 論文 1: `papers/public-data-findings/manuscript/`・`experiments/20261105-findings-paper1-prefreeze/`・`experiments/20261106-findings-paper1-exploration/`
- 論文 2: `papers/stall-shape-multiverse/manuscript/sections/methods.tex`（4 つの軸）・`experiments/20261107-stall-shape-multiverse/scripts/core.py`

## 運用メモ
- /reimagine 適用: No
- 理由: 計算の手順は論文 1 の X11 をそのまま使い、新しい設計判断は grill（判断 2〜5）で閉じた。
