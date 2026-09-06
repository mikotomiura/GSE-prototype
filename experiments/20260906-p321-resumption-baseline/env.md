# env.md — 環境固定

⚠️★★★ **`Cargo.lock` は本実験の環境ではない。** ★ 本実験は Rust を 1 行も走らせない
(`gse-replay` も `cargo test` も通らない)。→ `docs/experiment-tracking.md` の
「環境は Cargo.lock で固定」は **Python の requirements.txt** に読み替える
(→ `notes.md` §5)。

## 実行環境 (2026-09-06 の実測値)

| | |
|---|---|
| OS | Windows-10-10.0.26200-SP0 (Windows 11 Home 26200) |
| Python | **3.11.9** (`tags/v3.11.9:de54cf5`, MSC v.1938 64 bit AMD64) |
| shell | git-bash (⚠️ Hook はすべて bash 前提。PowerShell では動かない) |
| 文字コード | ⚠️★★ Windows コンソールは cp932 → **`PYTHONUTF8=1` を必ず付ける** |

## 依存

★ **`analyze_p321.py` は標準ライブラリだけで動く** (`json` / `re` / `math` /
`statistics` / `collections` / `hashlib` / `argparse` / `copy` / `pathlib`)。
→ ★ `requirements.txt` は **空 (pin なし)** であり、これは「書き忘れ」ではない。

⚠️ ただし **データ取得と検証には repo 外の道具が要る**:

| 用途 | 道具 | 備考 |
|---|---|---|
| zip の取得 | **実ブラウザ (Chrome)** | ⚠️ `curl` は figshare の bot チャレンジで取れない (`data.md` §2) |
| SHA-256 照合 | `sha256sum` (git-bash 同梱) | `run.sh` Step 0' |
| ⚠️ 論文 PDF の読解 (★ 本解析には不要) | `pypdf` **6.14.2** | ★ 既報値を一次で確認するために使っただけ。`run.sh` は使わない |

## 再現

```bash
# ★ repo 直下から。⚠️ Cargo は使わない
bash experiments/20260906-p321-resumption-baseline/run.sh
```

⚠️★★★ **`scripts/repro.sh` は本実験を包まない。** ★ `scripts/repro.sh` は較正コホート
(`run-calibration-cohort.sh`) のラッパであり、**GSE の NDJSON を前提にしている**。
→ ★ 本実験の 1 コマンド再現の入口は **`run.sh` 単独**である
(`docs/experiment-tracking.md` ルール 4 の読み替え・`notes.md` §5)。
