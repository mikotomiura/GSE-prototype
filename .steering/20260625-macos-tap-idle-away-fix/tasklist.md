# タスクリスト

## 準備
- [x] 関連 docs / phase2-followups.md / next-session-prompt.md を読む
- [x] hook-constraints Skill を読む
- [x] core-graphics 0.24 の CGEventType / CGEventTapEnable API を確認
- [x] 影響範囲 (hook_macos.rs / lib.rs / probe_scheduler.rs) を確認

## 実装 (TDD: テスト先行)
- [ ] (C) `driver_idle_ms` 純関数 + 回帰テストを probe_scheduler.rs に追加 (先に red)
- [ ] (C) lib.rs:1608 を driver_idle_ms に置換
- [ ] (B) hook_macos.rs:637/:612 の LAST_KEY_MS.store(0) 削除
- [ ] (A) hook_macos.rs: extern CGEventTapEnable + TAP_PORT 静的 + callback 再有効化
- [ ] (A) tap 生成後 TAP_PORT 格納 / runloop 退出時 null クリア

## テスト
- [ ] cargo test --workspace green
- [ ] gse-replay --snapshot tests/snapshots/minimal.json 一致 (HMM 不変)
- [ ] cargo clippy / fmt クリーン
- [ ] tsc (フロント不変だが念のため確認は不要)

## レビュー
- [ ] code-reviewer + security-checker 並列 (input/ フック変更)
- [ ] /finish-task で /cross-review
- [ ] HIGH 指摘への対応

## ドキュメント
- [ ] decisions.md 作成 (callback 再有効化の hook-constraints 逸脱根拠 / last_key==0 の扱い)
- [ ] phase2-followups.md の F4 を「Phase1 で対応済み」に更新 (任意)

## 完了処理
- [ ] design.md 最終化
- [ ] git commit (fix(hook): ... Refs)
- [ ] 実機検証は研究者作業 (runbook) として申し送り
