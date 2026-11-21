# 環境

- 機械: macOS 27.0.1・arm64（研究者の Mac）
- Python: 3.14.4・numpy 2.5.2（`requirements.txt`）。venv は repo の外（既定 `~/gse-venvs/handmark-desk`・`PYTHON` で変えられる）。数え方と判定（`stoprule.py count` の数える部分・`selftest.py`・`check_mutations.py`）は標準ライブラリだけで動く。numpy は見込み（daysim）にだけ要る
- Rust: gse-replay は `src-tauri/Cargo.lock` のまま（`cargo build --bin gse-replay`・debug）。HMM は `HMM_VERSION = 0.5.0`、停滞の定義の値は `src-tauri/prereg/p1-episode.json`（gse-replay の既定）
- 借りる部品: `experiments/20261103-mhd-dryrun-v2/scripts/daysim.py`（見込み）・`experiments/20261103-stall-candidates-c1c2c6/candidates.py`（C1・C2）・`experiments/20261102-stall-decomposition/o1/build_o1.py`（中間）・`experiments/20261115-handmark-leak-desk/scripts/prepare_records.py`（写し）。どれも変えずに読み込む
- スレッド: BLAS の並列は 1 に固定（run.sh）
