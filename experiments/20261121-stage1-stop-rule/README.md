# 段 1 の終了判定（2026-11-21）

事前登録 `docs/preregistration-stage1.md` の S1-G2（各人の最低の件数・割付の日数・区間の精度・最長の期間）と §3（要る日数の見込み）を計算する script。条件は `conditions.md`、作業記録は `.steering/20261121-stage1-prereg-values-and-stop-rule/`。

- `bash run.sh selftest` —— 自己検査・変異・借りる部品の陽性対照
- `RECORDS_DIR=... UTC_OFFSET_SECS=32400 [VALUES_JSON=...] bash run.sh records` —— 記録の件数（値があれば判定）
- `COUNTS_JSON=... bash run.sh need` —— 件数の要約から要る日数の見込み

判定は「届いた（reached）・続ける（continue）・判定不能（undecidable）」の 3 つ。管理シートに載せるのは件数と判定だけで、計算はシートでしない。
