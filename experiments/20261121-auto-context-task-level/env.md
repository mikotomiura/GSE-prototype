# env.md — 環境の固定（auto-context-task-level）

- OS: macOS 27.0.1
- rustc: rustc 1.98.1 (48a229cea 2026-09-01)
- Cargo.lock の SHA-256: `417f95785177b7183850cb186d399a2f537a19853a097108bdd7276202b624e4`
- gse-replay: debug ビルド（`cargo build --bin gse-replay`・コミット 422ec19c の作業ツリー・Rust は 1 段目の枝から変えていない）
- Python: 3.14.4・numpy 2.5.2（scikit-learn は使わない）
- HMM_VERSION: `pub const HMM_VERSION: &str = "0.5.0";`
- 1 段目: `experiments/20261121-auto-context-segmentation/` の config.json・SEED・criteria.json をそのまま読む（書き換えない）
