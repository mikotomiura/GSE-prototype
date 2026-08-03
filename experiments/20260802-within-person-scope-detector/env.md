# 実行環境

| 項目 | 値 |
|---|---|
| 解析 | `analyze.py`（Python 標準ライブラリのみ・外部依存なし） |
| Python | `python3`（`run.sh` が解決） |
| 乱数 seed | `SEED` = 20260802（並べ替え検定 10,000 回・T-1 と T-2 で同一 seed） |
| GSE-prototype commit（事前登録の凍結時点） | `d463113` |
| HMM_VERSION | ★ **本実験は非該当**。`gse-replay` も HMM も通さず、NDJSON の `key` レコードのみを直接集計するため |
| OS | macOS（Darwin 25.5.0） |

## 依存の少なさについて

`analyze.py` は標準ライブラリのみで動く（`json` / `statistics` / `random` / `math` / `pathlib`）。
numpy / scipy を使っていないのは、**再現に lockfile を要さないため**である。
将来 numpy を導入する場合は `requirements.txt` を本ディレクトリに追加すること。

## 実行時間の目安

並べ替え 10,000 回 × 2 検定（T-1 / T-2）。統計量は最大ギャップのみで O(n log n) のため
数秒で完了する（前ラウンドはプロファイル間距離行列を毎回計算していたため重かった）。
