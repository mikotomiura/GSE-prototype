# タスクリスト — pilot-pipeline-runbook

## 準備
- [x] 関連 docs / ソース先読み (calibration-smoke-runbook / build_analysis_db / sync-session / package)
- [x] gse-replay の category 対応を確認 (#29/D-RC3 で逆写像済)
- [x] 依存 (#6 build_analysis_db) の git 配置確認 → スタック PR 化 (D-PP2)
- [x] age CLI 不在を確認 → decrypt を Rust bin に決定 (D-PP1)

## 実装
- [x] GAP①: `src-tauri/src/bin/unpack.rs` (gse-unpack: decrypt + --keygen)
- [x] GAP①: `src-tauri/Cargo.toml` に `[[bin]] gse-unpack` (required-features=package)
- [x] GAP②: `scripts/gen_sessions_manifest.py` (metrics 走査→sessions.csv、phase 保全マージ)
- [x] GAP③: `scripts/templates/survey-template.csv` + README に D8 WoZ 列追記
- [x] GAP④: `docs/pilot-runbook.md` (被験者 + 研究者 end-to-end 手順)
- [x] GAP⑤: `scripts/pilot-smoke.sh` (合成 session で全段スモーク)
- [x] `.gitignore` に age 鍵パターン追加 (多層防御)

## テスト
- [x] `cargo test --features package` (gse-unpack 往復・id 検証) — 2 passed
- [x] `scripts/pilot-smoke.sh` が cross_section を生成 (E2E ゲート) — PASS, rows=2
- [x] 回帰不変: `cargo test --workspace` (239) / `gse-replay --snapshot` (15) / `emit_schema` parity
- [x] gen_sessions_manifest 単体 (5) + clippy/fmt clean

## レビュー
- [x] code-reviewer + security-checker 並列 (復号・鍵・個人データ) — CRITICAL 0
- [x] HIGH/MEDIUM 対応: gitignore 平文パターン拡張 / find 優先順位 / out_dir 空 / vk 監査拡張 /
      Windows 鍵 ACL 警告 / pubkey grep 堅牢化 / CSV injection 注記
- [x] /cross-review — **Codex 系統は縮退** (run-codex-review.sh が `git diff` 固定で staged diff 非対応・
      無関係 working diff を参照。docx 混入も理由。Claude 単独に縮退・本タスク外の tooling 課題)。
      Claude 側で追加検出: H1 dropped 表示順 (可読性) / H2 ROWS 文言依存 (コメント) / M4 phase typo 警告 /
      L3 template id → P999。全て対応済。
- [x] 残 CRITICAL/HIGH なし

## ドキュメント
- [ ] design.md / decisions.md 最終化
- [ ] (任意) glossary に gse-unpack 追加検討

## 完了処理
- [ ] git commit (新規ファイルのみ stage)
- [ ] /finish-task
