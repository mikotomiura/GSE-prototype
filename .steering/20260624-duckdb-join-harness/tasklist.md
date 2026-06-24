# タスクリスト — duckdb-join-harness

## 準備
- [x] handoff / decisions.md D5 / roadmap-xy Phase C / metrics.rs / 既存 Python 流儀を読む
- [x] metrics.json 実サンプル・由来 (path 由来キー) 確認
- [x] duckdb pip 導入 (1.5.4)・unittest 流儀確認
- [x] 設計判断のユーザー確認 (Python+duckdb / pip 導入)

## 実装
- [x] ブランチ作成 `feature/duckdb-join-harness` (be85b62 基点 — main checkout が無関係 WIP で阻止。
      #29 マージ後に main へ rebase 可能。commit は本タスク分のみで隔離)
- [x] `scripts/requirements-dev.txt` (duckdb==1.5.4)
- [x] `scripts/fixtures/analysis_join/` 合成 fixture (P-ID 4名 metrics/survey/sessions + README)
- [x] `scripts/build_analysis_db.py` 本体 (CLI / read_text+json_extract / outer join / export / privacy ガード)
- [x] `.gitignore` に `analysis.db` 等を追加 (使い捨て成果物)

## テスト
- [x] `scripts/tests/test_build_analysis_db.py` (T1-T7 + exit code 群、計 11)
- [x] `python -m unittest` 全通過 (11/11)
- [x] 実 gse-dataset (旧 outcome 無し 31 file) スモーク成功 — backward-compat OK
- [x] 既存 Rust/cargo/schema/他 scripts は不変 (新規ファイルのみ追加)

## レビュー
- [x] code-reviewer + security-checker 並列 (CRITICAL/HIGH なし)
- [x] /cross-review (Claude+Codex、jq 導入済)
- [x] 指摘対応: C1(HIGH path/regex)→path 相対導出に置換、C2(MED survey 重複)→fail-closed、
      phase 型ドリフト→VARCHAR 強制、PII ガード→日英 substring 化、L2 文書化。全 16 test pass

## 完了処理
- [x] design.md / decisions.md 最終化
- [ ] /finish-task → git commit (Refs:)
- [ ] handoff-duckdb-join.md を done マーク / 次タスク handoff (必要なら)
