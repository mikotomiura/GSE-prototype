# 入力データ

- CS1 2019 年版 [V243] の holdout の中間（論文 1 の確認で作ったもの・書き換えない）。
  - `~/gse-public-data/cs1/work2019_holdout/`（438 課題・145 人のうち観測 10 分以上の 140 人）。`build_summary.json` の `holdout_sha256` = `028f2256d4f0bb8223c17887925a54483822e6cbda8d642e970b4bf8a20afd77`。
  - 停滞の定義を変えて replay を回し直した中間 `work2019_holdout_q995`・`_w15`・`_w60`（論文 1 の `build-variants.sh`）。
  - 取り置きの一覧 `~/gse-public-data/cs1/holdout.json`（SHA-256 `a5a32fcefeb97b038afd170e2672262fd5a71230d5e851319eaa076b606bdc47`）は照合のためだけに読む。
- 参照する前の結果（repo の中）: `experiments/20261105-findings-paper1-prefreeze/results_holdout/confirm_holdout.json`・`experiments/20261106-findings-paper1-exploration/results/explore_comparison.json`。
- データは repo の外に置き、再配布しない。書き手ごとの値は repo に出さず、外部の LLM（Codex を含む）に送らない。
