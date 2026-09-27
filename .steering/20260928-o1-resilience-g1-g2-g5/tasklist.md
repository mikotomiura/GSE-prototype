# tasklist — o1-resilience-g1-g2-g5

- [x] grill・requirement / decisions / design（研究者承認 2026-09-28）
- [x] G-1 Mac 小実験 段階 A（TCC 維持・目印 OK）
- [x] G-5: `UploadError` と `HttpUploader` の too large 判定（テスト＋変異）
- [x] G-5: O1 の送信前サイズ検査・`oversize/` 隔離・`quarantined`（テスト＋G1 負の対照＋変異）
- [x] G-5: `submit.rs` 要約 JSON・削除台帳 B-4
- [x] G-2: `O1Periodic`・`periodic_reconcile_due`・ローテートスレッド相乗り・App.tsx コメント（テスト＋変異）
- [x] G-1: `autostart.rs`（plist / Run 値の純関数・書き込み）・`autostart_action`・lib.rs 呼び出し・Cargo.toml feature（テスト＋変異）
- [x] cargo test --workspace --features package / fmt / clippy -D warnings / tsc
- [x] docs: functional-design / glossary / o1-deletion-ledger
- [x] README 文面案 → 研究者承認
- [x] code-reviewer + security-checker（並列）
- [x] /finish-task（/cross-review 必須）→ PR → CI 緑 → merge
- [ ] 版上げ v0.1.38（PR: chore/o1-release-v0.1.38・4 ファイル） → 研究者承認でタグ → Release 検証 → zip → o1-distribution-tag.md → Drive 照合
- [ ] 段階 B（新ビルドで本当のログイン・研究者）

## 記録
- PR #246 merged（`b955cf05`・2026-09-28）。PR の CI 全緑（Windows / macOS の check・frontend・audit）。main の run 発火を確認。
- 版上げ後の O1 ゲート: 通過 22 / 未達 2（タグが古い＝`v0.1.38` で解消予定／同意文書の「未了」＝研究者判断待ち・範囲外）。
