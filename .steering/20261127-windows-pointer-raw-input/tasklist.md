# タスクリスト

## 準備
- [x] 引き継ぎ 2 本を読む（`next-session-ggear-s1-n3-windows-before-start.md` §1・`next-session-ggear-windows-pointer-raw-input.md`）
- [x] `observe_windows.rs` のループを読む

## 診断
- [x] 使い捨てのテストで、今の形と手本の形の件数を比べる（675 → 0・677 → 677）

## 実装（TDD）
- [x] ループを `pump_messages_except_raw_input` に切り出し、回帰テストが今の形で赤になることを確かめる
- [x] 手本の形に直し、回帰テストが緑
- [x] `#[ignore]` の実機テスト（`SendInput`）を足す
- [x] レビューの指摘（失敗時の後始末・上限・`unsafe fn dispatch`・テストの注記）

## テスト
- [x] `cargo test --workspace`（1450 passed・3 ignored・/cross-review の反映後）
- [x] `cargo test --lib observe -- --include-ignored`（20 passed）
- [x] clippy `-D warnings`・fmt
- [x] 実アプリで実際のマウス（研究者・約 60 秒）: `pointer_bin` 32 行・`focus_transition` 2 行
- [ ] CI の windows（Actions の含まれる分は 12-01 に戻る。走らなければ上の手元の結果で代え、そう書く）

## レビュー
- [x] code-reviewer + security-checker（並列・HIGH なし）
- [x] `/cross-review`（Codex 60,994・指摘は design.md の「/cross-review の採否」）

## 完了処理
- [x] push と PR（2026-11-28 に研究者が「push と PR まで」を選んだ。merge は研究者に確かめてから）
- [ ] 配る版の変更の記録に「Windows で `pointer_bin` が記録され始める」を書く（main に入れた後・配布のとき）
- [x] 配る前の条件に「Windows でポインタの行が記録される」を足すか研究者に聞く → 足す。条件 15 として Mac がすでに足していたので、出所の欄にこの直しと確かめを書いた（配る版での確かめは残る）
