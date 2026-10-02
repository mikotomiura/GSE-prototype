# タスクリスト

## 準備
- [x] grill（AskUserQuestion 2 回・8 問）→ requirement.md・decisions.md 判断 1
- [x] 記録先を新しいスプレッドシートに変更（判断 2）→ design.md（聞く前に固定）・ユーザーの承認（2026-10-02）
- [x] 探索のサブエージェント（sonnet・入れ子禁止・締切 20 分 → 実際は約 35 分・5,721 件・判断 4）
- [x] 群 1〜3 の本文（Zenodo・出版社の OA・Chrome。X01 はユーザーが保存）
- [x] 道具: `common.py`・`log_add.py`・`build_candidates.py`・`check_candidates.py`（`--selftest` 陰性対照＋変異 19 PASS）

## 追加候補の判定（2 段・design.md §1・§2）
- [x] 群 1 AI 疲労のレビュー: S02-08（除外 E4・Zenodo の唯一の版＝原稿の写しと一致）→ X01（除外 E4・AI の判定なし）→ S08-03（保留 E6）
- [x] 群 2 隣の疲労・自動化のレビュー: S15-23（E4 → 保留）→ S13-20（E4 → 保留）
- [x] 群 3 研究計画・一次研究: S12-05（中心-A → 保留）→ S12-19（保留 → E1）→ S12-23（保留 → E1）
- [x] 探索の戻り → `review-search.md`・`data/search-*.json`（判断 4〜7: 候補に足す判定は次のタスク・読む一覧 46 件）
- [—] 群 4 探索で足した記録（判断 4 で次のタスクへ）
- [x] 抽出の確定（群 1〜3 の 5 件・X01）・品質評価（含めた一次研究なし）
- [x] 追加候補の表を書く（`build_candidates.py`）→ `check_candidates.py --final` 違反 0（`0b9363b7…`）

## B の続き・C
- [x] 本文の抽出（サブエージェント 4 本・38 件）→ 取れなかった 10 件を Chrome で開き直し（ユーザーが R47・R01・R14 を保存）
- [x] `novelty-check.md`（本タスクの版・本文 37 本）: 結論の箇所をメインが本文で確かめた
- [x] C の決定 → 研究者に構想を示してから決める（判断 9）

## 提案のドキュメント v1
- [x] `anthropic-skills:docx` Skill を読む
- [x] `proposal/proposal-v1.md`（§0〜§9）
- [x] `build_proposal.py` → Downloads と archive の .docx・`check_proposal.py` 違反 0・`--selftest` PASS（陰性対照＋変異 6）
- [x] LibreOffice で PDF にして 1・3 頁を目で見た（表の列幅を中身に合わせるよう直した）
- [x] 直した後の表の頁を目で見る（付録の表の列の折り返し）→ 狭い列が折り返していたので列幅の決め方を直し、13 頁を見直した（判断 10・`2faae616…`）

## 完了（→ 次のセッション・引き継ぎ `_handoff/next-session-ai-fatigue-after-34-finish.md`）
- [x] PR #288 の Codex 2 巡（道具・記録）→ 指摘への対応 → #288 の merge（`8cf19570`・34 件のタスクの判断 14・15）
- [x] 同じ型の穴を本タスクの道具にも当てる（答えと判定・式・全文抽出・判定者 2 に渡す版の列）→ 表を作り直し（`2d681d6f…`）・提案のドキュメントの直し（判断 10）
- [ ] 元の資料の SHA-256 が変わっていない・前のタスクの `check_workbook.py --final` 違反 0・ステージに本文が無い
- [ ] code-reviewer ＋ security-checker（並列）
- [ ] /cross-review 2 巡（Codex の当日の実消費を先に確かめる）
- [ ] 引き継ぎ（次のタスク: 残りの 213 件・提案のドキュメント v2）
- [ ] 出荷（git-workflow ルール 6）
