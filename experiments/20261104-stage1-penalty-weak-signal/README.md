# 段 1 の罰の強さ —— 弱い信号での確かめ

- 何を: 前の実験（`../20261104-stage1-penalty-synthetic/`）の案 B（τ = 0.5）を、係数 0.5 倍・0.25 倍の合成で確かめる。条件は `conditions.md`。
- データ: すべて合成。O1 と段 1 の記録は使わない。HMM_VERSION・gse-dataset は当たらない。
- 再現: `bash run.sh`（門 W1・W2 → 変異 → 本計算 → report と W4）。`JOBS`・`REPS`・`OUT` で変えられる。
- 出力: `results/summary.json`・`tables.md`・`provenance.json`・`selftest.json`・`mutations/`。`results/raw/` は git に入れない。
- 結果と読み: `notes.md`。作業記録: `.steering/20261104-stage1-penalty-weak-signal/`。
