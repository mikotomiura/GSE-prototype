# logger-flush-busy-loop

## 背景

手跡の帯の試作（`spike/handmark-stage`）の計測中に、開発版がトレイで「停止中」のとき本体が 1 コアの 40〜94% を使い、「記録中」にすると 2〜4% に下がることを見つけた（一次: `GSE-prototype-handmark-stage/.steering/20261030-handmark-edge-strip-impl/results.md` の run7）。`sample` では、CPU の多くが記録のスレッドの `crossbeam` の待ち（`Backoff::snooze`・`LogEntry` の `recv`）だった。

`src-tauri/src/logger.rs` の記録のスレッドは、待ち時間を `flush_interval.saturating_sub(last_flush.elapsed())` で決めている。`last_flush` が進むのは書いて flush したときだけなので、書くものが無い（`dirty=false`）まま 5 秒を過ぎると、待ち時間 0 の `recv_timeout` を回り続ける。一時停止中に届いた行はゲートの `continue` で落とすため、`dirty` が立たないまま同じ状態になる。同じ行は `origin/main`（5d7c53be）にもある。

引き継ぎ: `GSE-prototype/.steering/_handoff/next-session-logger-flush-busy-loop.md`。

## 再現手順・期待と実際（/fix-bug Step 2）

- 再現手順: 開発版を起動してトレイから「停止中」にし、1 分ほど置いて本体の累積 CPU 時間の差を測る。
- 期待: 書くものが無いときは、記録のスレッドが次の期限まで眠る（CPU はほぼ 0）。
- 実際: 1 コアの 40〜94% を使う。エラーやログは出ない（`sample` のスタックが唯一の手がかり）。

## ゴール

書くものが無いまま flush の期限を過ぎても、記録のスレッドの待ち時間が 0 で回り続けないこと。flush の意味（書いたものは最大 5 秒で書き出す）と、一時停止中は 1 バイトも書かない約束を変えない。

## スコープ

### 含むもの
- 待ちの計算と flush の判断を小さな関数（または構造体）に切り出し、回帰の単体テストを先に書く（赤を見てから直す）
- 修正
- 直す前後で、開発版の「停止中」「記録中」の CPU を累積 CPU 時間の差で比べる
- O1 の被験者が一時停止・停止している間に同じことが起きるかの確認と、起きる場合に配る版の扱いを研究者に聞く

### 含まないもの
- GSE の CPU の内訳の洗い出しと、軽くする設計の検討（別タスク・2026-10-30 研究者の回答）
- logger.rs のループのその他のリファクタ

## 受け入れ条件

- [ ] 回帰テスト: 書くものが無いまま期限を過ぎた後でも、次の待ち時間が 0 にならない（修正前に赤）
- [ ] 既存の flush の約束（dirty なら期限で flush・`recording_pause` は即 flush）のテストが緑
- [ ] `cargo test --manifest-path src-tauri/Cargo.toml --workspace` 緑・clippy 緑
- [ ] 開発版の「停止中」の CPU が、直す前より桁で下がることを実測で確かめる

## 関連ドキュメント

- `docs/architecture.md`（logger のスレッド）
- `data-privacy` Skill（一時停止中に書かない約束）

## 運用メモ
- /reimagine 適用: No
- 理由: 原因はコードで特定でき、直し方の候補が実質 1 つ（期限で `last_flush` を進める）の小さな修正のため
