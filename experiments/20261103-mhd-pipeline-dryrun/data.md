# 入力データ

- CoAuthor [V348] の中間 `~/gse-public-data/landscape/coauthor_work/`（`experiments/20261102-public-data-landscape/` の run.sh の C3 で作った。元の `coauthor.zip` の SHA-256 と取得は `experiments/20261031-coauthor-pre-request-signal/data.md`）。取っておく書き手（同 C2）のセッションは作る段で除いてある（`build_summary.json` の `held_out_sessions` 288）。
- 使った中間のファイルの数と、ファイルごとの SHA-256 を並べた列の SHA-256 は `results/provenance.json`。
- `~/gse-public-data/landscape/holdout.json` は開いていない。
- 記録を外部の LLM（Codex を含む）に送っていない。repo に出すのは集計値だけ。
