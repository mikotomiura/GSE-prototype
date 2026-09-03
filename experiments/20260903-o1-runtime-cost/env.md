# 実行環境の固定 — experiments/20260903-o1-runtime-cost

`reproducibility-discipline` ルール 2 / 3。⚠️ **測るときに埋める**（★ 未測定なので空欄がある）。

| 項目 | 値 |
|---|---|
| OS (B: macOS) | **macOS 26.5.2 (25F84)** ★ 2026-09-03 実測 |
| 機種 (macOS) | **Mac16,12 / Apple M4 / 16GB** |
| ⚠️ 電源 (macOS) | ★ **AC 接続**（`pmset -g batt` = `Now drawing from \'AC Power\'`・開始時 75%・not charging）。⚠️★★★ **バッテリー駆動ではないので、指標 3（バッテリー持ち）は測っていない** —— ★ `summarize.py` は対照が無いと `DataInsufficient` を返す |
| 測定バイナリ (macOS) | ★ **v0.1.31**（`~/Desktop/O1_計測用_macOS/gse-next.app`）。⚠️ 2026-09-03 に `main` の `c9f6fec` から `npx tauri build --bundles app --features package --target aarch64-apple-darwin` でビルド。★ **PR #151（孤児回収）を含む**。⚠️ 配布版 v0.1.30 とは**別物** |
| ⚠️ 自動提出 | ★ **外してある**（`~/.gse/o1_consent_ack` を `.bak` へ退避）。⚠️ 記録は続くが送信経路は閉じている（`auto_submit_enabled()` が false）→ ★ **計測の代表性は保たれる** |
| OS (A: Windows) | **（未記入）** ★ `winver` の値をそのまま |
| 機種 / 電源 (Windows) | **（未記入）** ⚠️ 同上 |
| GSE のバージョン | **0.1.31**（`src-tauri/Cargo.toml`）★ 実測時に `meta.app_version` で照合する |
| HMM_VERSION | **`0.5.0`**（`src-tauri/src/analysis/engine.rs`・2026-09-03 実測） |
| Cargo.lock | `src-tauri/Cargo.lock`（★ 本実験はビルド済みバイナリを測るので、**どのビルドか**を app_version で固定する） |
| Python (macOS) | **3.14.4** ★ `summarize.py` は標準ライブラリのみ（追加依存なし） |
| seed | `SEED`（**20260903**）⚠️★ **本実験に乱数は無い**。★ 刻むのは規約のため |

## ⚠️★★★ メモリの指標が OS で違う（★ 2026-09-03 に実測して判明）

★ `samples.tsv` は **メモリを 2 列**持つ。⚠️ **どちらか一方だけでは後から意味が決まらない。**

| 列 | macOS | Windows | 意味 |
|---|---|---|---|
| `rss_kb`（主） | `top` の **MEM** = **phys_footprint** | `WorkingSet64` | ★ Activity Monitor / タスクマネージャが「メモリ」として見せる値 |
| `rss_alt_kb`（対照） | `ps rss` | `PrivateMemorySize64` | ★ 常駐セット / プライベート領域 |

⚠️★★ **同じプロセスでも 15 倍違う。** ★ 2026-09-03 に Finder で実測:
`top` = **546M** / `ps rss` = **36MB**。
→ ⚠️ **OS をまたいで絶対値を比べない。** ★ 判定表 (README) の閾値は **OS ごとに**当てる。
★ リーク検知に使う**傾き (MB/h)** はどちらの定義でも同じ向きに出るので、そちらを主に見る。

⚠️★ **`top` の MEM には `+` / `-` の接尾辞が付く**（前サンプルからの増減の印）。
★ `sample-macos.sh` は `tr -d '+-'` で先に落としている ——
⚠️ **落とさないと単位判定に当たらず、8 時間ぶんのメモリが黙って全部 0 になる**（実測で発見）。

## ⚠️ 依存している実装（★ 変わったら本実験の値は無効になる）

| 参照先 | 依存している事実 |
|---|---|
| `src-tauri/src/analysis/loop_step.rs` | 推論が **1Hz ゲート**であること |
| `src-tauri/src/o1.rs` `ROTATE_AFTER_MS` | 日次ローテート = **24 時間**（★ 指標 4「1 日あたりのサイズ」の定義） |
| `src-tauri/src/o1.rs` `close_orphaned_sessions` | ⚠️ 2026-09-03 追加。★ 起動時に走査するので**起動直後の CPU に山が出る**（★ 平均に混ぜない） |
| `src-tauri/src/input/liveness.rs` | 打鍵が無いとき何を書かない / 書くか（★ 指標 4 の下限） |
