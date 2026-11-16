# 環境

- macOS（Darwin 27.0.0・Apple Silicon・10 コア）。Python は論文 1 の確認と同じ venv `~/gse-public-data/venv-findings1`（`experiments/20261105-findings-paper1-prefreeze/requirements-confirm.txt`: numpy 2.5.2・scikit-learn 1.7.2・joblib 1.6.0・scipy 1.18.1）。
- `OMP_NUM_THREADS=1`・`OPENBLAS_NUM_THREADS=1`・`CONFIRM_JOBS=8`（X11 と同じ）。
- 推定器の行は holdout の中間の `feat`（HMM_VERSION 0.5.0・停滞の定義 `p1-episode.json` 1.2.0・replay の SHA-256 は論文 1 の env.md）。この実験は replay を回さない。
- 読み込むスクリプト（書き換えない）: `20261105-findings-paper1-prefreeze/scripts/confirm_p1.py`・`prefreeze.py`・`20261101-klicke-early-stall-trigger/scripts/analyze_item2.py`・`20261106-findings-paper1-exploration/scripts/explore_comparison.py`・`20261107-stall-shape-multiverse/scripts/core.py`・`20261103-stall-candidates-c1c2c6/candidates.py`。SHA-256 は `results/provenance.json`。
