## 背景

記録のスレッドは、書く行が無いまま flush の期限（5 秒）を過ぎると、待ち時間 0 の `recv_timeout` を回り続けていた。一時停止中は届いた行をゲートで落とすので、この条件に入る。配布中の O1 v0.1.40 でも、研究者の Mac で一時停止中に本体が 1 コアの 97〜99% を使うのを実測した（2026-10-30）。記録の内容には影響しない（影響は CPU・電池・発熱）。

## 変更点

- 待ちと flush の判断を `FlushClock` に切り出し、書く行が無くても期限が来たら次の期限へ進める。flush の意味（書いた行は最大 5 秒で書き出す）と、一時停止中は 1 バイトも書かない約束は変えていない。
- 期限の判断をループの先頭に移した（一時停止中に行を落とす `continue` の道も通るように）。

## 検証

- ロガーを実際に動かして CPU を測った: 何も送らない 93.23% → 0.00%、一時停止の後に行を送り続ける 98.33% → 0.00%。
- 回帰テスト: `flush_clock_idle_past_deadline_does_not_spin`（直す前に赤）、周回数のテスト `paused_logger_does_not_spin_past_flush_deadline`、`logger_flushes_written_line_at_deadline`。変異（元のバグに戻す・定期の flush を消す）で赤を確かめた。
- `cargo fmt --check`・`clippy -D warnings`・`cargo test --workspace`・`gse-replay --snapshot minimal` 緑。
- 実機（開発版）: 一時停止中の CPU は合計 約 3%（本体 1.2〜1.4%）で、記録中と同じ水準（`.steering/20261031-pause-auto-resume/results.md` の 5）。

## レビュー

code-reviewer・/cross-review（Codex）の指摘に対応済み（`.steering/20261030-logger-flush-busy-loop/decisions.md` 判断 2・4・7）。

## 残り

- 配る版（v0.1.41）に入れる。Windows の実機では測っていない。

Refs: .steering/20261030-logger-flush-busy-loop/

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01BUBYRxTQSivZDKJTppgVtQ
