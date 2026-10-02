# タスクリスト

## 準備
- [x] grill（AskUserQuestion 3 回・11 問）→ requirement.md・decisions.md 判断 1
- [x] worktree `C:\wt\ai-fatigue-v2`（`docs/ai-fatigue-v2`・origin/main `f04b4995` から）
- [ ] design.md の承認
- [ ] 抄録の取得（`fetch_abstracts.py`・無料の API・メールアドレスなし）→ 取れなかった件を Chrome で確かめる

## 抄録段
- [ ] 道具: `common.py`・`build_ta_sheet.py`・`check_ta_sheet.py`（`--selftest`・メタ変異）
- [ ] 記入表 1 を作り、検査違反 0 → 判定者 1 に渡す
- [ ] 記入表 1 を読む（`read_ta_sheet.py`）→ ログ・X 番号
- [ ] 記入表 2 を作る → 判定者 1 が記入 → 読む

## 全文段
- [ ] 群ごとの本文の確保と抽出の波（サブエージェント・sonnet）
- [ ] 1 回目（Q1/Q2 の印つき）→ 2 回目 → 品質評価・抽出の確認

## まとめ
- [ ] 34 件のメモの論点の見直し（`memo-issues.md`）
- [ ] 追加候補の表を作り直す（`build_candidates.py`）→ `check_candidates.py --final` 違反 0・`--selftest`・メタ変異
- [ ] 提案のドキュメント v2（`anthropic-skills:docx` Skill を読む → 原稿 → .docx → `check_proposal.py`・目で見る）
- [ ] Downloads の退避ファイルの一覧 → 判定者 1 の確認 → 削除

## 完了
- [ ] 元の資料 4 つの SHA・前の 2 タスクのディレクトリに差分なし・ステージに抄録と本文なし
- [ ] code-reviewer ＋ security-checker（並列）→ /cross-review 2 巡
- [ ] 出荷（git-workflow ルール 6）
