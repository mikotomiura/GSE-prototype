# タスクリスト

## 準備
- [x] requirement.md・decisions.md 判断 1（ヒアリング 7 問）
- [x] design.md（聞く前に固定）・ユーザーの承認（2026-10-01）
- [x] ワークブックの写しを作る（`make_copy.py`・元の SHA-256 を確かめる）
- [x] 波 1 の入力（束 X1〜X5・用途の判定を含まない）を作る
- [x] 波 1 を投げる（5 本並列・sonnet・入れ子禁止・締切 25 分）
- [x] 待つ間: `write_workbook.py`・`check_workbook.py`（`--selftest` つき）・ログの形
- [x] 戻りを確かめる → `wave1/extract-X*.md`（下書き）。1 回目に載せる事実は件ごとにメインが本文で照合（群 1・2 は済み）

## 34 件（群の順・design.md §4）
- [x] 群 1 AF001
- [x] 群 2 AF007・AF006・AF009・AF008
- [x] 群 3 AF002・AF003（2 件とも保留 E6）
- [x] 群 4 AF004・AF034
- [x] 群 5 AF005・AF011・AF010
- [x] 群 6 AF012・AF019・AF023
- [x] 群 7 AF024・AF021・AF022
- [x] 群 8 AF020
- [x] 群 9 AF017・AF013・AF014・AF015・AF016・AF018（抽出の確定は 10-02）
- [x] 群 10 AF026・AF028・AF027・AF025・AF029（AF028 の本文を Tilburg から取り直した）
- [x] 群 11 AF030・AF031・AF033・AF032（AF031 の本文を RGU から取り直した）
- [x] 品質評価の確定（含める一次研究 9 件・群 1〜6 で確定済み）
- [x] 『AI判定比較』を書く（34 件の判定の後・2026-10-02）
- [x] `判定者1_確認の結果`（確認事項 12・次の確認・作業 34・ユーザーのメモ 8・2026-10-02）

## B: 新規性の確認
- [x] `novelty-check.md`（既存レビュー 6 件＋Nobles 2026 × 測定の批判・自動化の系譜／データ・コードブックの公開）
- [x] 結論の箇所をメインが原文で確かめる（grep と行の読み・2026-10-02）

## 完了
- [x] `check_workbook.py --final` 違反 0・`--selftest` PASS（実の写しとログで通し・2026-10-02）
- [x] 元のファイルの SHA-256 が変わっていない・ステージに本文が無い（2026-10-02）
- [x] code-reviewer ＋ security-checker（並列・判断 12 で全件対応）
- [x] /cross-review の Codex 1 巡目（道具・記録・2026-10-02・計 99,882 tokens）→ 指摘 9 件に対応（判断 14）・写しを作り直し（`3499b70f…`）・`--final` 違反 0・`--selftest` PASS・検査器のメタ変異 9/9
- [x] /cross-review の 2 巡目（判断 14 で足した規則の境界条件・Codex ＋ code-reviewer ＋ security-checker）→ 判断 15 で対応・メタ変異 21/21
- [x] 引き継ぎ（次のタスク: C の決定・提案のドキュメント・D）→ `_handoff/next-session-ai-fatigue-after-34.md`
- [ ] 出荷（git-workflow ルール 6）
