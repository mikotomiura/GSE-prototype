# タスクリスト

## 場面ごとの対応（完了前に照合する）

| 場面 | 使うもの |
|---|---|
| 計算の条件 | 値の前にコミット（済: 0c6217e9） |
| スクリプト | code-reviewer ＋ /cross-review（Codex にはコードと条件だけ） |
| 事実の断定（前提の訂正） | verify-before-claiming（一次: confirm_holdout.json・supplement.tex） |
| 未決 | AskUserQuestion（日本語・推奨と理由） |

## 手順

- [x] 引き継ぎと ADR-054 を読み、一次と照合（判断 1）
- [x] grill（判断 2〜5）
- [x] worktree（判断 6）
- [x] conditions.md を値の前にコミット
- [ ] defcheck.py・run.sh・data.md・env.md
- [ ] 試しの走り（B0 だけ・dir の外）で K1・K2・K4 と所要時間
- [ ] スクリプトをコミットしてから本番の run.sh
- [ ] notes.md（結果の読み・言えないこと）
- [ ] code-reviewer ＋ /cross-review
- [ ] ADR-054 D4 を埋める記録と前提の訂正を main 側へ返す形を決める（AskUserQuestion）
- [ ] push（PR は確かめてから）
