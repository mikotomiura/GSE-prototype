# タスクリスト — Phase 1 Task 1/3: Backend ログ基盤 + GT 入力経路

> **3 分割運用**: 本タスクは Phase 1 全体の 1/3。Metrics 算出は `phase1-metrics/`、Counter UI + E2E は `phase1-counter-ui/` 参照。

## 準備
- [x] requirement.md の v2 整合修正（Step A 完了）
- [x] Skill: `data-privacy` / `rust-standards` 参照
- [x] file-finder / impact-analyzer による調査完了

## 実装
- [x] T1-1: `src-tauri/src/logger.rs` に `UserLabelKind` enum 追加（Flow / Incubation / Stuck + `as_str()` + `parse()`）
- [x] T1-2: `LogEntry::UserLabel { timestamp, label, recovered_at }` バリアント追加
- [x] T1-3: 手書きシリアライザ match に `UserLabel` アーム追加（`format_user_label_line` 経由）
- [x] T1-4: `src-tauri/Cargo.toml` に `tauri-plugin-global-shortcut = "2"` 追加
- [x] T1-5: `src-tauri/capabilities/default.json` に global-shortcut 権限 3 件追加
- [x] T1-6: `src-tauri/src/lib.rs` に `LAST_LABEL_MS: AtomicU64` + `LABEL_DEBOUNCE_MS` 定数追加
- [x] T1-7: `record_label_internal(log, label)` 共通ヘルパー実装（2秒デバウンス + log_tx 送信 + tracing）
- [x] T1-8: `#[tauri::command] record_user_label(app, label, log)` 実装（バリデーション + emit）
- [x] T1-9: `invoke_handler!` に `record_user_label` 登録
- [x] T1-10: `tauri_plugin_global_shortcut::Builder` 初期化 + with_handler でラベル判定
- [x] T1-11: `.setup()` 内で 3 ショートカット (⌘⇧⌥F/I/S) を `app.global_shortcut().register()`

## テスト
- [x] T-T1: logger.rs `#[cfg(test)]` モジュール新設（8 本のユニットテスト）
- [x] T-T2: `cargo test -p gse-next --lib logger::tests` で 8 本全 PASS を確認
- [x] T-T3: `cargo test --workspace` で退行ゼロ（36 PASS）
- [x] T-T4: `cargo check --target aarch64-apple-darwin` 成功（Tauri plugin API 整合確認済）
- [x] T-T5: `cargo build --target aarch64-apple-darwin` warning 0
- [x] T-T6: `tests/snapshots/minimal.json` byte-equal 維持（`gse-replay --snapshot`, 15 snapshots OK）

## レビュー
- [x] R-T1: `code-reviewer` 起動（Task 1 スコープ: logger.rs / lib.rs / capabilities / Cargo.toml）
- [x] R-T2: `security-checker` 起動（`record_user_label` 外部入力経路を扱うため必須）
- [x] R-T3: HIGH 0 件、MEDIUM 対応: D2 (TOCTOU→compare_exchange) / D3 (is-registered 削除) / D4 (emit warn)

## ドキュメント
- [x] D-T1: Task 2 / Task 3 への依存関係を各 requirement.md に明記（完了）

## 完了処理
- [x] decisions.md に `/reimagine` v2 採用根拠を記録（D1〜D4）
- [ ] git commit: `feat(gt): backend user label logging + global shortcut (Phase 1 task 1/3)`

## 本タスクのスコープ外（他タスクへ）

| 項目 | 移管先 |
|---|---|
| `analysis/metrics.rs` / `--metrics` / `--json` / `baseline_metrics.md` | `phase1-metrics/` |
| Dashboard counter widget / E2E 検証 / Phase 1 全体レビュー / retrospective | `phase1-counter-ui/` |
| `ml/analyze.py`（オプショナル） | データ収集後に別タスク |
