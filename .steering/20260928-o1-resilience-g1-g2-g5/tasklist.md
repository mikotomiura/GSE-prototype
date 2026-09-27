# tasklist — o1-resilience-g1-g2-g5

- [x] grill・requirement / decisions / design（研究者承認 2026-09-28）
- [x] G-1 Mac 小実験 段階 A（TCC 維持・目印 OK）
- [ ] G-5: `UploadError` と `HttpUploader` の too large 判定（テスト＋変異）
- [ ] G-5: O1 の送信前サイズ検査・`oversize/` 隔離・`quarantined`（テスト＋G1 負の対照＋変異）
- [ ] G-5: `submit.rs` 要約 JSON・削除台帳 B-4
- [ ] G-2: `O1Periodic`・`periodic_reconcile_due`・ローテートスレッド相乗り・App.tsx コメント（テスト＋変異）
- [ ] G-1: `autostart.rs`（plist / Run 値の純関数・書き込み）・`autostart_action`・lib.rs 呼び出し・Cargo.toml feature（テスト＋変異）
- [ ] cargo test --workspace --features package / fmt / clippy -D warnings / tsc
- [ ] docs: functional-design / glossary / o1-deletion-ledger
- [ ] README 文面案 → 研究者承認
- [ ] code-reviewer + security-checker（並列）
- [ ] /finish-task（/cross-review 必須）→ PR → CI 緑 → merge
- [ ] 版上げ v0.1.38 → 研究者承認でタグ → Release 検証 → zip → o1-distribution-tag.md → Drive 照合
- [ ] 段階 B（新ビルドで本当のログイン・研究者）
