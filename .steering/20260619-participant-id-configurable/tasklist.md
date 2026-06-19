# タスクリスト

## 準備
- [x] 関連する docs / Skill を読む (data-privacy / rust-standards / development-guidelines §10)
- [x] 影響範囲を file-finder / impact-analyzer で調査
  (GSE_DATASET/default_log_path 参照箇所、GSE_PID 二重管理発見)

## 実装
- [x] `is_valid_participant_id()` allowlist バリデーション (`[A-Za-z0-9_-]`, 1..=64)
- [x] Windows 予約デバイス名 (CON/NUL 等) の拒否
- [x] `select_participant_id()` 純粋関数 (優先順選択 + trim)
- [x] `resolve_participant_id()` env 解決 (GSE_PARTICIPANT_ID → GSE_PID → P000) + warn
- [x] `default_log_path()` の `P000` ハードコード解消 + doc コメント更新

## テスト
- [x] 単体テスト 10 件追加 (canonical/拡張/空/トラバーサル/特殊文字/長さ境界/予約名/優先順/fallback/trim)
- [x] `cargo test --workspace` green (180 lib + 12 bin)
- [x] `gse-replay --snapshot` byte-equal (15/15, exit 0)
- [x] `emit_schema` drift なし

## レビュー
- [x] code-reviewer (HIGH 指摘なし、MEDIUM 2 件対応)
- [x] security-checker (パストラバーサル: 問題なし、Low の予約名を対応)
- [x] /cross-review → jq 不在のため Codex 系統 skip、Claude 単独レビューで代替 (理由明記)

## ドキュメント
- [x] docs/development-guidelines.md §10.2 に GSE_PARTICIPANT_ID/GSE_PID 設定手順を追記
- [ ] glossary への用語追加 (不要: 既存用語の範囲内)

## Part 2: 自動生成 + 永続化 (D4、2026-06-19 実装完了)
- [x] env 受け取り (Part 1) を feature ブランチで foundation commit (4c9cd7b)
- [x] `generate_participant_id()` — `P` + 12桁ランダム hex (rand 0.8、既存依存)
- [x] `load_persisted_id()` / `persist_id()` — `~/.gse/participant_id` (USERPROFILE/HOME 起点)
- [x] `resolve_participant_id()` を新フローに更新 (永続化値 → env → 自動生成+永続化 → P000)
- [x] 純粋関数 `resolve_with_store(persisted, env1, env2, generated) -> Resolution` に分離しテスト可能化
- [x] 単体テスト追加 (first_valid_id×4 / 生成形式×2 / 解決順×5 / env は永続化しない / 永続化往復×1)
- [x] docs/development-guidelines.md §10.2 に自動生成 + リセット手順を追記
- [x] code-reviewer (HIGH なし、MEDIUM 3件対応) + security-checker (CRITICAL/HIGH/MEDIUM なし) 並列
- [x] /cross-review → jq 不在で Codex 系統 skip、Claude 単独レビューで代替 (理由明記)
- [x] cargo test --workspace 緑 (200: 188 lib + 12 bin) / snapshot 15/15 byte-equal / schema drift なし
- [x] /finish-task (commit 6fa5bba)

### code-reviewer MEDIUM 対応 (D4 addendum 参照)
- [x] MEDIUM-1: `persist_id_to`/`load_id_from` を path 引数化し env 非依存の往復テスト追加
- [x] MEDIUM-2: `persist_id_to` を tmp+rename のアトミック書込に変更 (空/部分書込で ID 変化を防止)
- [x] MEDIUM-3: 衝突確率コメントを定量化 (N²/2⁴⁹)
- [ ] LOW: `~/.gse/participant_id` のファイルモード厳密化 (0o600) は不透明 ID・非 PII のため見送り (D4 addendum)

## Part 3: sync スクリプト追従 (Part 2 マージ後・別 /start-task 推奨)
- [ ] sync-session.{sh,ps1}: PID を `raw/<PID>/` パスから導出 (fallback GSE_PID→~/.gse→P000)
- [ ] sync-all.{sh,ps1}: `raw/*/` を participant ごとに反復し `metrics/<PID>/` へ振り分け
- [ ] スクリプト側 allowlist 検証 (logger との非対称解消、code-reviewer MEDIUM 本対応)
- [ ] docs §10.2 を per-participant 反復に更新
- [ ] bash -n + dry-run / PowerShell 手動確認 / schema parity 緑
- 詳細は handoff-next-session.md「Part 3」節を参照

## 完了処理 (Part 1)
- [x] design.md の最終化
- [x] decisions.md の作成 (D1 受取専念 / D2 解決順 / D3 allowlist / D4 自動生成)
- [ ] git commit (Part 2 と合わせて feature ブランチで実施)
