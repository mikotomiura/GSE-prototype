# タスクリスト

## 準備
- [x] grill（判断 1〜5）・requirement
- [x] 既存の手跡のコード（駆動役・累計・行・削除・トレイ・lib.rs の配線）を読む
- [x] design.md・研究者の承認（2026-11-23）

## 実装
- [x] 日の累計: `DayRecord.reveal_count`・`add_reveal`・`subtract_count`・`subtract` の引数とテスト
- [x] 行: `HandmarkDayRow.reveal_count`・書き出し・`Evaluation::add_reveal`・`row`・`snap_of`・`scrub_record`・`unavailable_row`
- [x] 区間の削除: `HandmarkSnap`・`HandmarkSub` の `reveals`・差・行の書き換え・テスト
- [x] schema: `schema_dto.rs`・`emit_schema` で `current.json`・`handmark_guard` の一覧
- [x] 駆動役: `RevealItem`・`Effect::Reveal`・`Effect::RevealItem`・`toggle_reveal`・自動で戻す 3 か所・テスト
- [x] 純関数 `handmark_reveal.rs`（Windows の候補の判定・戻す順）とテスト
- [x] macOS `handmark_reveal_macos.rs`
- [x] Windows `handmark_reveal_windows.rs`
- [x] トレイの 2 つ目の項目と文言の検査
- [x] lib.rs の配線（出来事の実行・押下・mod）

## テスト
- [x] `cargo test`（macOS）
- [x] 変異 13 個（数える分岐・一時停止・自動で戻す 3 か所・削除の差と式・古い行・項目の出し方・押下で行を書く・Windows の候補・区切り・Drop）がすべて赤
- [x] clippy・fmt
- [x] Windows: 最小 crate を `cargo clippy --target x86_64-pc-windows-msvc` で型検査（陽性対照つき・警告なし）。本体の Windows の CI は 12-01 以降

## ドキュメント
- [x] ADR-051 の補訂
- [x] 同意文書の条件 4 の行
- [x] functional-design（PR 6 の節）。glossary は新しい語なし

## レビュー
- [x] code-reviewer ＋ security-checker（判断 6）
- [x] /cross-review（判断 7）
- [ ] /finish-task（schema parity は gse-dataset の写しの PR 待ち）

## 引き継ぎ
- [x] Mac の実機（12-09 以降）と Windows の実機（G-GEAR）の確かめ方（`.steering/_handoff/next-session-gse-handmark-reveal-real-machine.md`）
- [ ] gse-dataset の schema の写しの PR
