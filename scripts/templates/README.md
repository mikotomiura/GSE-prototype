# survey CSV テンプレート (pilot-pipeline-runbook GAP③ / D-PP4)

`survey-template.csv` は研究者が Google Form 由来データを `build_analysis_db.py` に渡すための
**最小スキーマ**。実フォームの列名が PreReg で凍結されたら追従する前提の仮置き。

## 配置規約
- 置き場所: `<gse-dataset>/survey/` 配下。
- 推奨ファイル名: **参加者別 `survey/P###.csv`** (受領単位と一致・追記が楽)。
  1 ファイルに全員束ねる `survey/all.csv` 形式も可 — `build_analysis_db.py` は `survey/*.csv` を
  `union_by_name` で結合する。
- グレイン: **(participant_id, phase) で一意**。同一 (P-ID, pre|post) の重複行があると
  `build_analysis_db.py` は exit 4 で停止する (D2/D3)。

## 列

| 列 | 必須 | 意味 |
|---|---|---|
| `participant_id` | ✓ | P### (join キー) |
| `phase` | ✓ | `pre` / `post` (join キー) |
| `gse_total` | 推奨 | 一般性自己効力感 GSE 合計 (10-40, D3) |
| `nasa_tlx_total` | 任意 | NASA-TLX 合計 |
| `walk_done` | post のみ | **D8 WoZ**: Wall で席を立ち歩いたか (0/1) |
| `returned_to_work` | post のみ | **D8 WoZ**: 歩行後に作業へ戻れたか (1-5 Likert) |
| `inconvenience_benefit_accepted` | post のみ | **D8 WoZ**: 不便益として受容できたか (1-5 Likert) |

WoZ 3 列は散歩介入 (Lv3/Lv4) の**受容性**を自己申告で拾うためのもの。Phase 1 では歩数/移動の
実計測コードは作らず (D8)、post survey のこの数値だけで受容を評価する。pre 行では空欄。

## プライバシー (data-privacy / decisions.md D1)
- **数値の尺度得点と P-ID/phase のみ**。実名・メール・電話・住所・生年月日・所属などの PII 列は禁止。
- 列名に PII トークン (`name`/`mail`/`氏名`/`メール` 等) が含まれると `build_analysis_db.py` が
  exit 6 で停止する (早期検知ネット。最終防衛は「PII を survey CSV に入れない」運用)。
- 実名↔P-ID 対応表は **repo 外** で研究者が管理する。
- **CSV formula injection 注意**: セル値は**数値の尺度得点のみ**にする。`=`/`+`/`-`/`@` で始まる
  文字列セルを入れない。`cross_section.csv` を Excel/Sheets で開くと数式として実行され得るため
  (build_analysis_db は列名 PII ガードのみで**セル値はサニタイズしない**)。手編集 CSV は信頼できる
  ものだけを開くこと。
