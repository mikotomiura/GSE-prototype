# タスクリスト

## 準備
- [x] 引き継ぎ・issue（S-09・S-11）・A 群の design.md §0・検査器を読む
- [x] 研究者に次の段・タスク名・範囲を聞く（判断 1）
- [x] worktree（`C:\wt\ai-fatigue-judge-file`）で origin/main から `docs/ai-fatigue-theory-and-usage` を切る
- [x] design.md §0〜§2 を抄録の取得の前に固定（2026-09-30 18:05）

## 道具
- [ ] `evidence/screen.py`（語形・G・枠組みの正規表現）と `evidence/test_screen.py`（陽性・陰性）を書いて緑にする
- [ ] `evidence/fetch_abstracts.py`（4 情報源・URL の柵・抄録は scratchpad・`write_pair`）
- [ ] `scripts/check_surveys_here.py`（前タスクの検査器を本タスクに当てる）

## 取得とふるい
- [ ] 入力の xlsx の SHA-256 を確かめる
- [ ] 259 件の抄録を取る（DOI の無い 4 件は題名で）
- [ ] S-09 の原典（2.2）・原著（2.4）の抄録を取る
- [ ] ふるいを回す（S-11 の語形・G、S-09 の枠組み）

## S-11
- [ ] 語を使う記録の抄録を読み、意味を与える文を抜き出す
- [ ] 抄録に無く無料の本文があるものは本文で確かめる
- [ ] 用法の例（1.4）・プロンプト疲れの概念分析の本体を辿る
- [ ] `survey-S-11.md`・`survey-S-11-ai-judgments.md`・`survey-S-11-gse.md`

## S-09
- [ ] 2.2 の原典を読む（抄録・無料の本文）
- [ ] 2.4 の原著を読む（5 件以上の枠組みだけ）
- [ ] `survey-S-09.md`・`survey-S-09-ai-judgments.md`（理論の節の草稿・DB への提案）・`survey-S-09-gse.md`

## 検査とレビュー
- [ ] `check_surveys_here.py` 違反 0・`test_screen.py` 緑
- [ ] code-reviewer・security-checker（並列）
- [ ] `/cross-review` 2 巡（Codex の当日の実消費を先に確かめる）

## 完了処理
- [ ] issue の状態（`issue-status` 相当）・引き継ぎ
- [ ] コミット → push → PR → CI 緑なら merge → main の CI 発火確認
