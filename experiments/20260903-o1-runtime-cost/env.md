# 実行環境の固定 — experiments/20260903-o1-runtime-cost

`reproducibility-discipline` ルール 2 / 3。⚠️ **測るときに埋める**（★ 未測定なので空欄がある）。

| 項目 | 値 |
|---|---|
| OS (B: macOS) | **macOS 26.5.2 (25F84)** ★ 2026-09-03 実測 |
| 機種 (macOS) | **Mac16,12 / Apple M4 / 16GB** |
| ⚠️ 電源 (macOS) | ★ **AC 接続**（`pmset -g batt` = `Now drawing from \'AC Power\'`・開始時 75%・not charging）。⚠️★★★ **バッテリー駆動ではないので、指標 3（バッテリー持ち）は測っていない** —— ★ `summarize.py` は対照が無いと `DataInsufficient` を返す |
| 測定バイナリ (macOS) | ★ **v0.1.31**（`~/Desktop/O1_計測用_macOS/gse-next.app`）。⚠️ 2026-09-03 に `main` の `c9f6fec` から `npx tauri build --bundles app --features package --target aarch64-apple-darwin` でビルド。★ **PR #151（孤児回収）を含む**。⚠️ 配布版 v0.1.30 とは**別物** |
| ⚠️ 自動提出 | ★ **外してある**（`~/.gse/o1_consent_ack` を `.bak` へ退避）。⚠️ 記録は続くが送信経路は閉じている（`auto_submit_enabled()` が false）→ ★ **計測の代表性は保たれる** |
| OS (A: Windows) | **Windows 11 Home**（`systeminfo` 実測: `10.0.26200 N/A ビルド 26200`）★ 2026-09-09 実測 |
| 機種 / 電源 (Windows) | **Micro-Star International Co., Ltd. / MS-7E66**（デスクトップ機）。⚠️★★★ **バッテリーが物理的に存在しない**（`Get-CimInstance Win32_Battery` が空応答＝インスタンス無し。`wmic` はこの機のWindowsビルドに存在せず使えなかった）→ ★ **エネルギー影響/バッテリー系の指標はこの機では原理的に測定不能**（測り忘れではない） |
| 測定バイナリ (Windows) | commit `22538ccb5654c6e55a6ac0327cf7ece3b2f9dfd9` を `npm run build && npm run tauri build -- --no-bundle` でビルド（`.steering/20260904-windows-orphan-verify/decisions.md` 判断3。素の `cargo build --release` は devUrl 依存の欠陥ビルドになるため使わない）。バイナリ mtime 2026-09-09 15:06。実測時の作業ツリー HEAD は `8146f08`（`22538cc` との間に build-relevant path の変更なし＝ビルドは現HEADと等価と確認済み） |
| GSE のバージョン (macOS) | **0.1.31**（`src-tauri/Cargo.toml` の値。⚠️ 「実測時に `meta.app_version` で照合する」という当初の記述は、実際に照合した記録が本ファイル自体には残っていないため**未確認の方針メモとして扱う**。過去セッションで実際に照合したかは`verify-before-claiming`に従い断定しない） |
| GSE のバージョン (Windows) | **0.1.33**（`git show 22538cc:src-tauri/Cargo.toml` の `version` 行を実測。`app_version()` は `env!("CARGO_PKG_VERSION")` でビルド時にこの値を埋め込む＝ `capabilities.rs:271`）。⚠️★★★ **この実測では NDJSON の `meta.app_version` を照合していない**（測定後にNDJSONを削除してしまい、事後の照合ができなくなった。`run.sh`が書く`meta.json`にも`app_version`フィールドは無く、そちらでの照合はそもそも不可能）。★ Cargo.toml が build-relevant pathの一部であり、判断3の再ビルド後に変更されていないことは別途 git log で確認済みなので値そのものは信頼できるが、**次回以降は削除前に対象NDJSONの`meta.app_version`を一次資料として確認する手順を先に踏むこと**（教訓） |
| HMM_VERSION | **`0.5.0`**（`src-tauri/src/analysis/engine.rs`・2026-09-03 実測） |
| Cargo.lock | `src-tauri/Cargo.lock`（★ 本実験はビルド済みバイナリを測るので、**どのビルドか**を app_version で固定する） |
| Python (macOS) | **3.14.4** ★ `summarize.py` は標準ライブラリのみ（追加依存なし） |
| seed | `SEED`（**20260903**）⚠️★ **本実験に乱数は無い**。★ 刻むのは規約のため |

## ★ エネルギー影響（`energy_impact` / `ref_energy_impact`）— 2026-09-04 追加

★ `top -stats power`（**sudo 不要**）＝ Activity Monitor の「**エネルギー影響**」。

⚠️★★★ **ワットではない。** CPU・wakeup・GPU・ディスクを合成した **Apple 内部の無次元の指標**であり、
★ **「バッテリーが何時間減るか」には換算できない。**
→ ★ だから **参照プロセス（`Finder`）の同時刻の値を `ref_energy_impact` に併記**する。
⚠️ **単独の絶対値で判定しない。** ★ 読み方は「常駐している軽いアプリと比べて何倍か」。

### ⚠️ なぜバッテリー % の対照実験をやめたか

★ 2026-09-04 に 8 時間の対照を回して**何も得られなかった**（`notes.md` 参照）。理由:

1. ⚠️ バッテリー消費は **画面輝度と人の操作**が支配的で、GSE の寄与が埋もれる
2. ⚠️ 2 日間まったく同じ使い方をするのは**不可能**
3. ⚠️ 16 時間ラップトップを電源から外して拘束する

→ ★ **プロセス単位で取れる指標に替えれば、対照は要らず AC のままで測れる。**

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
