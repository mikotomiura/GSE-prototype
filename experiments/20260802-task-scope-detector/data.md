# 入力データの固定

## 出所

[mikotomiura/gse-dataset](https://github.com/mikotomiura/gse-dataset)（private）の `raw/P0{10..14}/*.ndjson`。

| 項目 | 値 |
|---|---|
| gse-dataset commit | `c2f960c0b9a04778e616dbd212517c65a76f132c` |
| 参照パス | `raw/P010` `raw/P011` `raw/P012` `raw/P013` `raw/P014` |
| 除外 | `raw/P000`（開発者の動作確認用・較正コホート外。`analyze.py` で明示的に除外） |
| セッション数 | P010=12 / P011=5 / P012=7 / P013=10 / P014=6（計 40） |
| 解析対象 | 38（`press < 200` の事前基準で 2 セッション除外: P013 の 108 press・P014 の 9 press） |
| `session_meta.task_kind` | 全セッション `argumentative`（分散ゼロ） |
| `session_meta.condition` | 全セッション `blind_calibration` |

## プライバシー

- ⚠️ **raw NDJSON は本リポジトリに一切コミットしない**（`docs/development-guidelines.md` §10 / `data-privacy`）。
- NDJSON には**本文が含まれない**（content-free）。`key` レコードは `{t, press, category}` のみで、
  `category` は `alphabetic` / `space` / `enter` / `backspace` / `delete` / `numeric` / `other` の粗い分類。
- 本実験の出力（`metrics.json` / `exploratory-pause-split.json`）は**集計値のみ**。
- ⚠️ **NDJSON も打鍵内容も外部 LLM に送信していない**（解析はすべてローカル）。

## 匿名化

⚠️ 本 repo は **ビルドのため一時的に public にする運用がある**（Actions 分数の都合）。
そのため成果物には **セッション名の日時を出力しない**。`analyze.py` はファイル名順の安定した
連番（`P013-s03` 等）へ置き換える。**対応表は repo に残さない**（gse-dataset 側から再構成可能）。

被験者 ID（`P0xx`）は gse-dataset が既に採用している仮名であり、そのまま用いる。
