# evidence（本タスク: S-15・S-14・S-13 と判定者用ファイル）

| ファイル | 何か |
|---|---|
| `search_round.py` | 3 本で共通の検索（design.md「サーヴェイ」S0〜S3・判断 8 の補い `S-14s`）。書誌だけを repo に書き、抄録は repo の外（scratchpad）に `common.write_pair` で対にして書く |
| `S-15/s15_results_2026-09-30.json` ほか | 検索の書誌の記録（題名・著者・年・掲載誌・DOI・0 段目／0b 段・既出・抄録の有無）。抄録は持たない |
| `S-1x/s1x_extraction_2026-09-30.tsv` | サブエージェント（Sonnet）の抽出の表（抄録から・判定はしていない）。★ 事実のファイルに載せた行は、メインが抄録で確かめた |
| `oa_2026-09-30.json` | 判定者用ファイルの DOI の OpenAlex の `open_access`（`scripts/fetch_oa.py`） |

- ★ 前タスクの `../../20260929-ai-fatigue-surveys/evidence/common.py` を import して使う（空の抄録で上書きしない・repo の外の確認・対の書き出し・URL の柵）。
- ⚠️ `search_round.py` は実行した版の記録。再実行すると出力先が既にあるので止まる（上書きしない）。
- ⚠️ 抄録の前処理はタグの名前を限って除く（`p < .001` の `<` を消さない・前タスク判断 11）。
- 連絡先（メールアドレス）は学術 API に送っていない。
