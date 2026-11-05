# 取得したデータ（CS1 打鍵データ [V243]）

- 取得: 2026-11-04 08:39（+0900）。Dataverse の API（`/api/datasets/:persistentId/` でファイルの一覧 → `/api/access/datafile/<id>`）。取得の時刻はファイルの更新時刻。
- 置き場: `~/gse-public-data/cs1/raw/<年>/`（repo の外・再配布しない）。
- 取ったのは `keystrokes.csv` と `readme.txt` だけ（判断 1・問い合わせで約束した範囲）。
- 2026-11-04 に API で版と大きさを照合し直した（下の表と一致）。

| 年版 | DOI | Dataverse 版 | ファイル | file id | バイト | SHA-256 |
|---|---|---|---|---|---|---|
| 2019 | doi:10.7910/DVN/6BPCXN | 5.2 | keystrokes.csv | 6157950 | 455,078,162 | `b54d8cf56b7719ae0ec9ecf19e5b3788168f087bd4a50238dca1e06f6bfe7955` |
| 2019 | 同上 | 5.2 | readme.txt | 12130010 | 3,474 | `c08acb613e2a871074136c4586c151548efba5bef7707d2215a672bbe54cdf61` |
| 2021 | doi:10.7910/DVN/BVOF7S | 7.0 | keystrokes.csv | 6157942 | 193,521,644 | `950a587bb3a410efc4aad0e64974d6442806345fddd13af76676dfb8006a22b6` |
| 2021 | 同上 | 7.0 | readme.txt | 7457666 | 2,158 | `15c094fdf688a85283ebeab9ba8067d7019e77d6176e4b7dcd7304b101b0d06d` |

`run.sh` は `keystrokes.csv` の SHA-256 が違えば止まる。
