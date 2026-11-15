# 環境

- 機械: macOS 27.0.1・arm64（研究者の Mac・CI の自前ランナーを兼ねる。判断 6）
- Rust: rustc 1.98.1・cargo 1.98.1。gse-replay・gse-handmark-table は `src-tauri/Cargo.lock` のまま（`cargo build --bin gse-replay`・debug）
- HMM: `HMM_VERSION = 0.5.0`（`src-tauri/src/analysis/engine.rs`）。合成の入力の推定は `--labels recomputed` で計算し直す
- Python: 3.14.4・numpy 2.5.2（`requirements.txt`）。venv は repo の外（既定 `~/gse-venvs/handmark-desk`・`PYTHON` で変えられる）
- Node: 22.22.0（.ts の型を除いて読む）。`@napi-rs/canvas` 1.0.13（Skia・ビルド済みのバイナリ）は、このディレクトリの `package.json`・`package-lock.json` に閉じる（`npm ci --ignore-scripts`）。アプリの依存には入れない
- 描画: `src/components/handmarkStageDraw.ts`（画面と同じ純関数）。WebKit と Skia の画素は完全には一致しない（限界）
- スレッド: BLAS の並列は 1 に固定（run.sh）。並列は組の単位で `JOBS`（既定 4）
