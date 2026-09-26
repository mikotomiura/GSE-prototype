# タスクリスト —— D. P1 本体の準備

## grill（Opus・2026-09-26・完了）
- [x] 引き継ぎメモと一次（事前宣言 v1.1 全文・ADR-030 補訂 2 の該当節・personalization §10 / G2・loop-engineering 全文）を読む
- [x] 収集状況を中身を開かずに確かめる（記録票 A〜C 未記入）→ 研究者回答: G1・O1 とも未開始
- [x] 判断分岐を閉じる（`decisions.md` 判断 1〜15・18）。#8 は影響の実測を研究者へ再提示して再確認
- [x] 用語を `docs/glossary.md` に追加（上下界の軸・算出不可・PG-1 分布集計・episode 表・探索格子）

## 分解（Opus・完了）
- [x] `issues/001〜010.md` ＋ `00X-acceptance.sh`（`bash -n` 済み）
- [x] `_issue-plan.md`（DAG・ウェーブ・交差表・自己検査）
- [x] `_loop-config.json`（モード C・base `feat/p1-main-prep`・parallel 2）
- [x] 前提の実測（2026-09-26）: 004 / 008 が呼ぶ過去 acceptance 3 本（p1-prereg-cli-poles 003・008 ／ mhd-feature-offline-tiers 003）は **rc=0**・`check-tests-are-wired.sh` rc=0
- [ ] （任意）TASK-PRE: `codex-consult` で issue 独立性の第二意見 → `_codex-preplan.md`

## 実行（★ 別セッション・`/clear` の後・Sonnet）
- [ ] `bash scripts/loop-run.sh .steering/20260926-p1-main-prep`（初回は安い issue 1 本を parallel=1 で回して基盤を確かめる）
- [ ] 全 issue done → メインが clean な checkout で acceptance 10 本 ＋ 過去 acceptance 3 本
- [ ] `/finish-task`（code-reviewer ＋ security-checker 並列・`/cross-review` 2 巡・push → PR → CI 緑 → merge → main CI 確認）
