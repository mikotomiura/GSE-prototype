# 設計

## アプローチ

- 定義と検出器は c1c2c6（`experiments/20261103-stall-candidates-c1c2c6/candidates.py`）をそのまま import して使う。中間は停滞の分解の `o1/build_o1.py` をそのまま呼ぶ。新しく書くのは、`.age` の復号と人ごとの束ね（`build_n4.py`）、休止の分布と人の間の幅（`pausestall.py`）、変異（`mutants.py`）だけ。
- 休止の分布の主はモデルに依らない量（分位・長い休止の割合・時間で重みを付けた割合）。混合モデルは分布の形の要約として従に置く（成分を休止の種類として読まない）。
- 人の記号は SEED で付け直し、対応は repo の外。

## 変更対象

- 新規: `experiments/20261103-o1-n4-pause-stall/`（conditions.md・data.md・env.md・SEED・run.sh・build_n4.py・pausestall.py・mutants.py・後で notes.md と results/）
- 既存のコードは変えない。

## テスト戦略

- `pausestall.py --selftest`（N6 の 2〜5）と c1c2c6 の `--selftest`。
- `mutants.py`: 要の 8 行を壊した写しで対照が赤になる。
- 実データ: 検出器の C0 と `gse-replay` の一致（N5）。

## 記録を開く順

1. 条件・コードをレビュー（code-reviewer）→ 直す → コミット（計算の前）。
2. `run.sh` を 1 回。
3. notes.md → code-reviewer・security-checker・/cross-review（Codex にはコードと条件の文だけ）。
