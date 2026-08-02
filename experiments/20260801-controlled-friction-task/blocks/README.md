# blocks/ — 被験者ごとの割付ファイル（**コミットしない**）

`analyze.py` の入力。1 被験者 1 ファイル（`P0xx.json`）。

## 作り方

```bash
python3 assign.py --subject P015 --json > blocks/P015.json
```

そのうえで、各 block に**実施後**に 2 つのキーを書き足す:

| キー | 何を書くか | 出所 |
|---|---|---|
| `file` | そのブロックの NDJSON ファイル名 | 記録用紙（`protocol.md §2.2`） |
| `produced_chars` | ブロック終了時に実験者が数えた**産出文字数** | 同上（`preregistration.md §3.5` の報告義務） |

さらに、操作チェックの回答をファイル末尾に足す:

```json
"manipulation_check_answers": [
  {"block": 3, "harder": 2},
  {"block": 4, "harder": 4},
  ...
]
```

`harder` = 「より詰まった」と選ばれた**ブロック番号**。
★ **同条件ペア（HI-HI / LO-LO）は `analyze.py` が自動で分母から外す**（`preregistration.md §2.6`）。

## ⚠️ コミットしない理由

NDJSON のファイル名には**セッション日時**が入る（`P0xx_gse_YYYYMMDD_HHMMSS.ndjson`）。
被験者の作業時刻は再識別の手がかりになるため、`.gitignore` で除外している。
`analyze.py` の出力（`results/metrics.json`）には**ファイル名も日時も出さない**。
