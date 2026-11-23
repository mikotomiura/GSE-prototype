# 環境

- Python 3.14.4（`python3 -I`）・numpy 2.5.2。ほかの外部パッケージを使わない（ロジスティック回帰・ROCKET・再標本化は `scripts/dryrun.py` に書いた）。
- macOS（研究者の Mac）。GSE のバイナリ・`HMM_VERSION` は使わない（`p_stuck`・`ewma_x` は中間を作った時の replay の出力で、そのバイナリの SHA-256 は `experiments/20261102-public-data-landscape/results/provenance.json`）。
