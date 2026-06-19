# タスクリスト — clipboard-paste-count

## 準備
- [x] 関連する docs / Skill を読む (data-privacy / hook-constraints / architecture-rules / rust-standards)
- [x] 影響範囲を file-finder / impact-analyzer で調査
- [x] 設計をユーザー承認 (検出方式 / 記録粒度)

## 実装
- [x] 1. `analysis/features.rs`: InputEvent に is_paste 追加 + test helper 3 箇所
- [x] 2. `input/hook.rs`: 変更なし (CTRL_DOWN Atomic 案は撤回・D3)
- [x] 3. `input/hook_windows.rs`: GetAsyncKeyState(VK_CONTROL) で V&&Ctrl → is_paste (D3)
- [x] 4. `input/hook_macos.rs`: get_flags() Command → Cmd+V → is_paste
- [x] 5. `schema_dto.rs`: LogEntryDto::Paste variant
- [x] 6. `logger.rs`: LogEntry::Paste + writer match
- [x] 7. `lib.rs`: analysis スレッドで is_paste → LogEntry::Paste 送出
- [x] 8. `bin/replay.rs`: ReplayEvent::Paste + timestamp()=None + run_replay match
- [x] 9. `README.md` / `README.ja.md`: InputEvent ドキュメント更新

## テスト
- [x] paste 検出ロジックの単体テスト追加 (logger read-back + replay parse)
- [x] `cargo test --workspace` 緑 (189 lib + 13 replay)
- [x] fixture に paste 行追加 → gse-replay parse 確認
- [x] `gse-replay --snapshot` byte-equal 確認
- [x] `emit_schema` 再生成 → src-tauri/schema/current.json 更新
- [x] gse-dataset へコピー → check_schema_parity.py exit 0

## レビュー
- [x] code-reviewer + security-checker 並列 (焦点=中身が一切残らない)
- [x] /cross-review → jq 不在のため Codex 系統 skip・Claude 単独へ縮退 (D3 サマリに明記)
- [x] CRITICAL/HIGH 指摘への対応 (HIGH×2 を D3 で解消)

## ドキュメント
- [x] README InputEvent 反映 (上記タスク9)

## 完了処理
- [x] design.md の最終化
- [x] decisions.md の作成 (検出方式・記録粒度・D3/D4/D5 の記録)
- [ ] git commit (feat(logger): ...)
- [ ] /finish-task
