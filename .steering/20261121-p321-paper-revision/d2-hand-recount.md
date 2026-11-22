# D2 の 17 件を手で数え直す（研究者用・判断 25）

> 目的: 解析のコード（`analysis/d2.py`）と 2 つ目の実装は、どちらも LLM で作った。人が 1 回だけ、転記から 2×2 の表を数え直して、コードの数と合うかを確かめる。
> 所要: 15 分ほど。ここには、コードが出した数を書いていない（先に見ると確かめにならない）。

## 開くもの

論文用リポジトリ `C:\self-resolution-measure` の次の 2 つ（Excel かテキストエディタで開く）。

1. `data\li-coblenz-2026\transcription_a.csv`（17 行・1 行が 1 件）
2. `data\li-coblenz-2026\text_external.csv`（本文の逐語 3 行）

転記と PDF の照合は、2026-09-28 に済んでいます。今回は PDF を開かなくてかまいません。

## 決まり（本文 §4.2 の定義）

- 解決: `resolved` 列が `Y`。
- 相談した（表 5 だけで数える）: `documentation`・`social_technical`・`web_sources` のどれかが `1`。
- 相談した（表 5 と本文で数える）: 上のどれかが `1`、または `text_external.csv` の `task_id` に出てくる件。
- a = 解決して、相談していない件の数。
- b = 解決せず、相談していない件の数。
- N = 全件の数。S = 解決した件の数。

## 記入表

| task_id | 解決 (Y/N) | 相談・表 5 だけ (Y/N) | 相談・表 5 と本文 (Y/N) |
|---|---|---|---|
| P1TA | | | |
| P2TA | | | |
| P2TB | | | |
| P3TA | | | |
| P4TA | | | |
| P5TA | | | |
| P5TB | | | |
| P5TC | | | |
| P6TA | | | |
| P6TB | | | |
| P7TA | | | |
| S1TA | | | |
| S2TA | | | |
| S3TA | | | |
| S4TA | | | |
| S4TB | | | |
| S5TA | | | |

## 返してほしいもの（チャットに 2 行で）

```
表 5 だけ:     N=__ S=__ a=__ b=__
表 5 と本文:   N=__ S=__ a=__ b=__
```

気づいたこと（迷った行・転記の疑問）があれば、一緒に書いてください。

## 受け取った後（Claude がすること）

- `results/metrics.json` の `d2.results.<mode>.counts` と照らす（a = `resolved_no_consult`、b = `unresolved_no_consult`、N − (a+b) が相談した件）。
- 結果と日付を decisions.md に書き、本文 §5「Use of large language models」・§8 と `audit/independent-recount/README.md` に「著者が D2 の 17 件を転記から手で数え直し、一致した（または、食い違いとその理由）」と書く。
