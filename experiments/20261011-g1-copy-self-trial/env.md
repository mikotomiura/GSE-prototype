# 実行環境

| 項目 | 値 |
|---|---|
| repo commit（開始時） | `b34b069c`（main） |
| ブランチ | `docs/g1-copy-self-trial`（worktree `C:/wt/g1-copy-self-trial`） |
| 機械 | G-GEAR（Windows 11 Home 10.0.26300） |
| Python | 3.11.9 |
| SudachiPy | 0.7.0（Apache-2.0）・SudachiDict-core 20260723.1（前の実測と同じ） |
| numpy | 2.2.6（照合の計算だけ） |
| `HMM_VERSION` | 使わない（GSE のコードを実行しない。記録は種類の列として読むだけ。記録の `meta` の `hmm_version` は P009 が 0.5.0・P010 が 0.3.0） |
| 復号 | `src-tauri/target/release/gse-unpack.exe`（main の checkout でビルド済みのもの） |

`.venv/Scripts/python -m pip freeze`（2026-10-11）:

```text
numpy==2.2.6
sudachidict-core==20260723.1
SudachiPy==0.7.0
```
