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
- [x] 版上げ v0.1.38（PR #247・`afe6b0d7`）→ タグ push（研究者承認）→ Release 検証 → zip → `docs/o1-distribution-tag.md` v0.1.38 節
- [x] Drive の zip 差し替え（研究者・2026-09-28）→ コネクタで照合: `O1_実施用_macOS.zip` 10,434,926 B（id `1eeFtGS-…`）／`O1_実施用_Windows.zip` 5,983,577 B（id `1RDeKfvh…`）= ローカルと一致。同名の古い版は Drive 検索で 0 件
- [x] O1 同意フォームの再配備（研究者が `migrateO1ConsentForm()` を実行・「追加する同意項目はありません」。★ 説明文の新しい 1 文は**研究者が実物を目で確認**・2026-09-28）
- [ ] 段階 B（新ビルドで本当のログイン・研究者）

## 記録
- PR #246 merged（`b955cf05`・2026-09-28）。PR の CI 全緑（Windows / macOS の check・frontend・audit）。main の run 発火を確認。
- 版上げ後の O1 ゲート: 通過 22 / 未達 2（タグが古い＝`v0.1.38` で解消予定／同意文書の「未了」＝研究者判断待ち・範囲外）。
- タグ `v0.1.38`（`afe6b0d7`）・Release run `36367017514` success。O1 zip: macOS `f5ad9a90…`（10,434,926 B）／Windows `e8c69975…`（5,983,577 B）。O1 ゲート 23 / 1（残りは同意文書の「未了」）。
