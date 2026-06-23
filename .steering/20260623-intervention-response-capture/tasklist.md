# タスクリスト

## 準備
- [x] 関連 docs / Skill を読む (roadmap-xy §2/§3, capture-freeze decisions, intervention-design, data-privacy)
- [x] 影響範囲を file-finder / impact-analyzer で調査
- [x] 設計フォーク3点を AskUserQuestion で確定 (D1)
- [x] requirement / design / decisions / tasklist 作成

## 実装
- [x] logger.rs: DismissReason に EarlyUnlock/Completed/IdleTimeout (as_str/parse)
- [x] logger.rs: LogEntry::InterventionResponse に elapsed_ms: Option<u64>
- [x] logger.rs: format_intervention_response_line に elapsed_ms 引数 + writer アーム
- [x] schema_dto.rs: DismissReasonDto + LogEntryDto::InterventionResponse.elapsed_ms (skip_serializing_if)
- [x] lib.rs: LogState pub(crate) + clone_log_tx() アクセサ、record_intervention_dismiss に elapsed_ms: None
- [x] wall_server.rs: log Sender + shake_at 配線、/shake 記録、/unlock で elapsed/reason + try_send (POST 限定・重複ガード)
- [x] emit_schema 再生成 → schema/current.json 更新 + gse-dataset 同期

## テスト
- [x] logger 単体: format (Wall Some / Nudge None)、新 DismissReason roundtrip、writer E2E に Wall 行
- [x] cargo test --workspace 緑 (224 passed)
- [x] --snapshot byte-equal (features 不触) 回帰確認 (15 snapshots match)
- [x] 旧 NDJSON (elapsed_ms 欠落) で gse-replay panic しない確認 (replay 後方互換テスト追加)
- [x] emit_schema parity (current.json + gse-dataset parity 緑)

## レビュー
- [x] code-reviewer + security-checker 並列 (CRITICAL/HIGH なし)
- [x] /cross-review (Claude ∥ Codex) — 両者一致 HIGH 2件
- [x] CRITICAL/HIGH 対応 (B 重複ガード適用 / A は reload 整合のため reject+根拠記録 / C/E/G 適用)

## 完了処理
- [x] design.md / decisions.md 作成
- [ ] /finish-task (schema parity guard 実走・drift で停止)
- [ ] git commit (別 PR・main 基点)
