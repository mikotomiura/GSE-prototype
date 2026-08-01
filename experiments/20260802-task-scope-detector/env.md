# 実行環境

| 項目 | 値 |
|---|---|
| 解析 | `analyze.py`（Python 標準ライブラリのみ・外部依存なし） |
| Python | `python3`（`run.sh` が解決） |
| 乱数 seed | `SEED` = 20260802（並べ替え検定 10,000 回） |
| GSE-prototype commit | 実行時の `git rev-parse HEAD` を results 側に残すこと |
| HMM_VERSION | ★ **本実験は非該当**。`gse-replay` も HMM も通さず、NDJSON の `key` レコードのみを直接集計するため |
| OS | macOS（Darwin 25.5.0） |

## 依存の少なさについて

`analyze.py` は標準ライブラリのみで動く（`json` / `statistics` / `random` / `math` / `pathlib`）。
numpy / scipy を使っていないのは、**再現に lockfile を要さないため**である。
将来 numpy を導入する場合は `requirements.txt` を本ディレクトリに追加すること。
