# タスクリスト

## 準備
- [x] 引き継ぎ・前タスクの decisions.md（判断 1〜19）・protocol-ja.md（全 760 行）を読む
- [x] PR #280 が MERGED（2026-09-30T18:34:15Z）を確かめ、worktree `C:\wt\ai-fatigue-judge-file` で origin/main から `docs/ai-fatigue-protocol-cont` を切る
- [x] 判定者用ファイルの SHA-256（archive・Downloads とも `48af51d3…`・未記入）
- [x] F19・F10 の一次資料（DB の r7・r10・v1.0 の §1・§2・E4・v1.0 の適用・254 件の題名の言語）
- [x] F19・F10・範囲・タスク名を聞く（判断 1）
- [x] requirement.md・design.md（変更の前に固定）・decisions.md

## 判定者用ファイル（F19・F10）
- [ ] `judge_xlsx.py`: 除外理由の選択肢に E7・『判定基準』の基準の版・尺度の原著の行・E7・『はじめに』の版の行
- [ ] `check_judge_xlsx.py`: E7 を判定の語に・変異 3 つ
- [ ] `check_judge_xlsx.py --selftest` PASS・`check_appraisal_xlsx.py` 違反 0
- [ ] 作り直す直前に Downloads の写しの SHA-256 → `--force --copy-to` → archive と Downloads の SHA-256 が一致・検査 違反 0

## プロトコル v0.2
- [ ] protocol-ja.md（冒頭・[GSRR-7]・[GSRR-35]・[GSRR-42]・付録 A の A31・付録 B・付録 F）
- [ ] `check_protocol_here.py` 違反 0・`--selftest` PASS

## 研究者の確認票
- [ ] `researcher-check.md`（期限ごとの表・判定者 1 が決めたこと・【案】の一覧）
- [ ] `scripts/check_here.py`（鍵の行・内部の語・メール・F の番号・【案】の数）と `--selftest`

## 検査とレビュー
- [ ] code-reviewer・security-checker（並列）→ 一次で確かめて対応
- [ ] `/cross-review` 2 巡（Codex の当日の実消費を先に確かめる）

## 完了処理
- [ ] 引き継ぎを次の段に差し替える
- [ ] コミット → push → PR → CI 緑なら merge → main の CI 発火確認
