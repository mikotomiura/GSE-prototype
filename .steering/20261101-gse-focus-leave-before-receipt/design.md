# 設計

- 条件は `experiments/20261101-focus-leave-before-receipt/conditions.md`。
- 手順: `gse-replay --features` を日ごとに回し、停滞の始まりの行だけを残した中間（repo の外）を作る → NDJSON から `focus_transition`・`paste` の時刻だけを読む → 集計を `results/` に出す。
- 打鍵の本文は読まない（`key` 行も使わない）。Codex には集計と条件とコードだけを渡す。
