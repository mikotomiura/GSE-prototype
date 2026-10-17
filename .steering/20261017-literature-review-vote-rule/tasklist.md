# タスクリスト

## 準備
- [x] 引き継ぎ（`docs/tangibility-design` 枝 `a6db6cdb`）と規約の一次を読む
- [x] 研究者に直し方を確かめる（判断 1〜4）
- [x] main から worktree を切る（`/Users/johnd/GSE-wt-vote-rule`・枝 `docs/literature-review-vote-rule`）

## 実装
- [x] `.claude/agents/evidence-axis-judge.md` を作る
- [x] `.claude/commands/literature-review.md` の Step 4・5・9・完了条件・アンチパターン・description を改める
- [x] `docs/loop-engineering.md` のモデル表に 1 行
- [x] `CLAUDE.md` のサブエージェント一覧に 1 語
- [x] `.claude/skills/literature-card/SKILL.md` の「3 票」
- [x] `.claude/skills/subagent-delegation/SKILL.md` のルール 4・5 に 1 文ずつ
- [x] `docs/literature/_index.md` に変更日の注記
- [x] 規約の側に残る「3 票」を grep で数え直す

## 検証
- [x] `empirical-prompt-tuning`（対応表の当てはめ・起動手順の書き出し）を頭打ちまで
- [x] `python3 scripts/check_citations.py` が違反なし
- [x] agent の `model:` と `loop-engineering.md` の表の一致

## レビュー
- [x] `/finish-task`（code-reviewer ＋ `/cross-review` 2 巡・判断 6・7）
- [x] HIGH 指摘への対応（実物の agent での確認は引き継ぎ next-session-evidence-axis-judge-live-check.md）
