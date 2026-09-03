# 実行環境の固定 — experiments/20260903-o1-runtime-cost

`reproducibility-discipline` ルール 2 / 3。⚠️ **測るときに埋める**（★ 未測定なので空欄がある）。

| 項目 | 値 |
|---|---|
| OS (A: Windows) | **（未記入）** ★ `winver` の値をそのまま |
| OS (B: macOS) | **（未記入）** ★ `sw_vers -productVersion` |
| 機種 / 電源 | **（未記入）** ⚠️ **AC 接続かバッテリー駆動かを必ず書く**（★ 3 の対照が成立しない） |
| GSE のバージョン | **（未記入）** ★ `meta.app_version`（NDJSON の 1 行目） |
| HMM_VERSION | **`0.5.0`**（`src-tauri/src/analysis/engine.rs`）★ 測定時に読み直して更新する |
| Cargo.lock | `src-tauri/Cargo.lock`（★ 本実験はビルド済みバイナリを測るので、**どのビルドか**を app_version で固定する） |
| Python | **（未記入）** ★ `summarize.py` は標準ライブラリのみで動く（追加依存なし） |
| seed | `SEED`（**20260903**）⚠️★ **本実験に乱数は無い**。★ 刻むのは規約のため |

## ⚠️ 依存している実装（★ 変わったら本実験の値は無効になる）

| 参照先 | 依存している事実 |
|---|---|
| `src-tauri/src/analysis/loop_step.rs` | 推論が **1Hz ゲート**であること |
| `src-tauri/src/o1.rs` `ROTATE_AFTER_MS` | 日次ローテート = **24 時間**（★ 指標 4「1 日あたりのサイズ」の定義） |
| `src-tauri/src/o1.rs` `close_orphaned_sessions` | ⚠️ 2026-09-03 追加。★ 起動時に走査するので**起動直後の CPU に山が出る**（★ 平均に混ぜない） |
| `src-tauri/src/input/liveness.rs` | 打鍵が無いとき何を書かない / 書くか（★ 指標 4 の下限） |
