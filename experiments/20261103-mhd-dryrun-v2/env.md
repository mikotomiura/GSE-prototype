# 環境

- Python 3.14.4（`python3 -I`）・numpy 2.5.2。ほかの外部パッケージを使わない（第 1 版と同じ）。版は `results/provenance.json` にも刻む。
- macOS（研究者の Mac）。GSE のバイナリ・`HMM_VERSION` は使わない。(b) の `p_stuck`・`ewma_x` は第 1 版と同じ中間（そのバイナリの SHA-256 は `experiments/20261102-public-data-landscape/results/provenance.json`）。
- (a) は外部のデータを読まない（乱数だけ）。
