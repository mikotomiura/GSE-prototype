# タスク

- [x] G-GEAR の runner を登録し直す（研究者が管理者の PowerShell で実行・2026-11-19・online・`gse-win`）
- [x] check の頭に優先度を下げる段と確かめの段を置く
- [x] `feature/*` の push を外す・docs/development-guidelines.md の 2 か所
- [x] 手元: check_workflow_invariants（self-test・本検査・unittest 34）緑
- [x] 変数 `GSE_WIN_FORCE_HOSTED` を消す（2026-11-19・PR #429）
- [x] /cross-review 1 巡目・HIGH を直した（判断 1）
- [ ] PR・実際の run で G-GEAR と Mac の check が緑で、優先度が下がっていることをログで確かめる
- [ ] frontend-check は無料分が戻るまで始まらない（研究者の決定・待つ）。戻ったら回し直して merge
- [ ] 研究者の計算と重なったときの check の所要時間を測り、timeout-minutes（self-hosted 30 分）を判断する（判断 1 の保留）
