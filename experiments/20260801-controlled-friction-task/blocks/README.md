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
| `produced_chars` | ブロック終了時の**産出文字数** | ★ **記入パッドの表示**（`preregistration.md §2.11 / §3.5`） |

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

## ★ 手で書かない・書いたら必ず検査する

操作チェックは **7 回の二択**であり、しかも `§5.3` のとおり**どの分母でも 1 問しか外せない**。
すなわち **転記ミス 1 件で合否が反転しうる**。手転記を経路から外す:

```bash
python3 forms_to_blocks.py --csv <G1-M回答.csv> --subject P015 --write   # フォーム → JSON
python3 validate_blocks.py --dataset ~/gse-dataset                        # 転記の整合を検査
```

`validate_blocks.py` が見るもの（★ **検出だけ。除外も判定もしない**）:

- ブロック 1..10 が揃い、1 と 10 が `copy`、2..9 が HI4/LO4 か
- ★ 条件・題材 ID・課題文パスが **`assign.py` の決定的出力と一致**するか（再生成して突き合わせる）
- `file` が全ブロックにあり、**被験者内でも被験者間でも重複していない**か
- `manipulation_check_answers` が 7 件あり、ブロック 3〜9 に対応し、**二択の中に収まっている**か
- `produced_chars` が桁外れでないか（★ **WARN であって除外ではない**・`§3.6`）
- `--dataset` 時: NDJSON が実在するか、★ **`probe_assignment` 行が 0 か**（`§5.4` の客観検証）

## ⚠️ コミットしない理由

NDJSON のファイル名には**セッション日時**が入る（`P0xx_gse_YYYYMMDD_HHMMSS.ndjson`）。
被験者の作業時刻は再識別の手がかりになるため、`.gitignore` で除外している。
`analyze.py` の出力（`results/metrics.json`）には**ファイル名も日時も出さない**。
