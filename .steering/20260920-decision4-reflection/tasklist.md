# タスクリスト

## 準備
- [x] 判断 4 の一次（`20260919-theory-ssot-promotion/decisions.md`）と引き継ぎを読む
- [x] 前セッションの未コミット分（判断 4 の記録・引き継ぎ）をコミット（`046f6c2`）
- [x] 反映先を一次で開く（ADR-034 全文・README の行・o1-roster §5・事前登録 第 18 版・analyze.py の版一致検査・CORE-CS §5.0・IDE・intervention-design・ADR-035 Consequences）
- [x] 改名の前件数を記録（`rename-counts-before.txt`）

## 2-1 ADR-034 の Accepted（`9a22f5b`）
- [x] ADR-034 ステータス行・Consequences 5 の状態
- [x] README の ADR-034 行・ADR-014 行（＋ ADR-016 行・ADR-032 行の注記 —— grep で見つけた）
- [x] `o1-roster-operations.md` §5
- [x] 「収集完了」の各ヒットを直す / 理由を記録（decisions 判断 1）
- [x] memory `project_g1_build_distribution_boundary.md`・`MEMORY.md` の索引

## 2-2 事前登録 第 19 版（`510c614`）
- [x] `preregistration.md` 第 19 版の改訂履歴
- [x] `config.json` の revision / `analyze.py` の `PREREG_REVISION`・`data.md` の状態
- [x] `check_frozen_sections.py` 緑・`analyze.py --selftest` 緑・`run.sh` 全項目通過（`PYTHONUTF8=1`）
- [x] ADR-034 Consequences 7 の状態

## 2-3 改名（`9df1478`）
- [x] サブエージェント（Sonnet）の置換を検収（前後件数・diff 33 行を置換規則で突き合わせ・不一致 0）
- [x] 注記の更新（測定辞書・分析契約）・`docs/theory/` 2 本の冒頭の改訂一覧
- [x] glossary（用語表に「誤採用」・禁止用語に旧名）
- [x] 後件数を記録（`rename-counts-after.txt`）・記録ファイルの件数が不変

## 2-4 CORE-CS §5.0 と Nudge の見直し候補（`9ea0bbe`）
- [x] CORE-CS §5.0 の未決を閉じる
- [x] IDE に「見直し候補（未決）」の節（R-1）・Skill から 1 行

## 2-5 引き継ぎの整理（`57c7584`）
- [x] 段 3 の引き継ぎ §2 注記・§3 に ADR-035 の未決 3 つ

## 検査
- [x] `check_citations.py` 違反なし・`check_doc_lexicon.py` 違反なし
- [x] 改名の残存検査（design.md「検査の記録」・陰性対照つき）
- [x] schema parity check → ⚠️ drift（`activity_label`）。★ 本タスクは schema に触れていない（`046f6c2..HEAD` で 0 ファイル）。既知の保留（`20260913-esm-audit-criterion-gate/decisions.md` 判断 3「同期は本ブランチのマージ後」）

## レビュー
- [x] `/cross-review` 1 巡目 Codex（70,586 tokens・CRITICAL/HIGH なし・4 件）
- [ ] `/cross-review` 1 巡目 Claude（code-reviewer・Opus）
- [ ] 1 巡目の指摘への対応
- [ ] `/cross-review` 2 巡目（自分が足した規則の境界条件）
- [ ] 2 巡目の指摘への対応

## 完了処理
- [ ] design.md の最終化
- [ ] 次の引き継ぎ（G1 / O1 の残タスクの棚卸し）へ観察を渡す
- [ ] git commit
