# 設計

## アプローチ

- 条件は `experiments/20261107-stall-shape-multiverse/conditions.md`（計算の前のコミット `08010482`）。
- 停滞の検出は `20261103-stall-candidates-c1c2c6/candidates.py` の写し（replay と一致を照合済み）を、窓 W・θ・条件 A・観測区間を引数にして `scripts/core.py` に置いた。B0 は全 7,709 単位で replay と一致（K1）。論文 1 の付録の変種（W 15・60 秒・0.995 分位で下限 200 個）とも全単位で一致。
- 流れ: `prep.py`（作業場 → キャッシュ・D2/D3 の照合）→ `k1_match.py` → `run_configs.py`（90 通り × 全単位）→ `c3b.py` → `analyze.py`（C1・C2・C3・§J）。データと中間は `~/gse-public-data/paper2_work/`（repo の外）。
- 統計: statsmodels 0.15.0（`~/gse-public-data/venv-paper2`）。件数は `PoissonBayesMixedGLM`（変分ベイズ・疎な設計）、長さは `MixedLM`（REML）。

## 変更対象

- `experiments/20261107-stall-shape-multiverse/`（新規）
- `docs/literature/20261107-stall-shape-paper2-novelty.md`・`docs/references.md`（[V468]〜[V471]）・`docs/literature/_index.md`

## テスト戦略

- K1 照合（replay と全単位）・K2 陽性対照（`core.py --selftest`）・K3 変異（11 個すべて赤・改変なしの対照は緑）・K4 取り置きと課題の照合（`prep.py` が止める）・K5 分散成分の回復（`analyze.py` が模擬して当てはめ直す）。
- 集計のコードは合成の入力で全経路を通してから実データに当てる。
