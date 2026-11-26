# 設計

## アプローチ

`lib.rs::run()` で O1 の判定（`crate::o1::set_mode`）の後、`logger::default_log_path()`（ファイル名が時刻で決まる）より前に、
`crate::o1::wait_for_plausible_clock` を呼ぶ。O1 のときだけ。

- Tauri の Builder を組み立てる前なので、画面・トレイ・イベントループはまだ無い。待っている間は何も見えない（起動が遅れるだけ）。
- single-instance の判定も Builder の中なので、待っている間に 2 個目が起動しても、両方が待ち、抜けた後でいつもどおり 2 個目が止まる。
- 記録の起点（`O1_LOG_OPENED_MS`）・枠の起点・ファイル名・`meta` の時刻は、どれも待った後の時刻になる。

## 変更対象

- `src-tauri/src/o1.rs`: `clock_is_plausible(now_ms)`（既存の `MIN_PLAUSIBLE_EPOCH_MS..=MAX_PLAUSIBLE_EPOCH_MS`）と、
  `wait_for_plausible_clock(now, sleep, on_wait)`（時計と眠りを引数に取る・待った回数を返す）。
- `src-tauri/src/lib.rs`: `run()` の入口で O1 のときに呼ぶ。待つ間は 60 回に 1 回 `tracing::warn!`。

## 待ちの上限

上限を置かない（判断 2）。

## テスト戦略

- `o1.rs` の単体テスト: 範囲の内で 0 回・外から内へ移ったら抜ける・境界（MIN ちょうど / MIN-1）・未来側（MAX+1）。
- 偽の時計（呼ぶたびに進む）と偽の眠り（回数を数える）を渡す。実時間は眠らない。
- 回帰: `cargo test --workspace`・replay（`minimal.ndjson`）・clippy。
