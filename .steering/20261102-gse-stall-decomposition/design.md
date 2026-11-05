# 設計

## アプローチ

- 条件: `experiments/20261102-stall-decomposition/conditions.md`（計算の前にコミット）。
- 公開データ（`public/`）: 俯瞰の `analyze_landscape.py` の読み込みと `Session` を import し、型の集計だけを足す。中間は作り直さない。
- O1（`o1/`）: T2 で固定した `gse-replay` で `--features`（停滞の始まり）と `--metrics --json`（ADR-024 の単位）を 14 本に回し、停滞ごとの台帳を repo の外に作り、集計だけを `results/` に出す。
- 自己検査: 合成の入力で窓の開閉・優先順・打ち切り・Aalen–Johansen の写しを確かめ、変異で赤になることを見る。

## 変更対象

- `experiments/20261102-stall-decomposition/` だけ（`docs/`・アプリのコードは変えない）。

## テスト戦略

- `--selftest`（合成の入力）・陽性対照（取っておいた書き手が入ると止まる・中間の hash が違うと止まる）・T3 の 1,313 件との照合。
