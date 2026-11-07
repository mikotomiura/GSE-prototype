# 設計

## 根本原因

`src-tauri/src/logger.rs` の記録のスレッド（`SessionLogger::spawn` 内のループ）:

```rust
let timeout = flush_interval.saturating_sub(last_flush.elapsed());
match rx.recv_timeout(timeout) { ... }
if dirty && last_flush.elapsed() >= flush_interval { flush; last_flush = now; dirty = false; }
```

`last_flush` を進めるのは「flush したとき」だけで、flush は `dirty` のときだけ起きる。書くものが無い（`dirty=false`）まま 5 秒を過ぎると `timeout` は 0 のまま戻らず、`recv_timeout(0)` を回り続ける。次に書く行が届くまで続く。

この状態に入る道は 2 つある。

1. 何も届かない: 非 O1 で「開始する」を押す前など。
2. 届くが全部落とす: 一時停止中（O1 のトレイの「停止中」は `recording::is_paused()`）。ゲートの `continue` で落とすので `dirty` が立たない。しかも `continue` はループ末尾の flush の判断も飛ばす。

## 実装アプローチ

flush の時計を小さな構造体 `FlushClock` に切り出し、時刻を引数で渡す形にして単体テストできるようにする（`recording` の純関数と同じ作り）。

```rust
struct FlushClock { interval: Duration, last: Instant }
impl FlushClock {
    fn new(interval, now) -> Self
    fn wait(&self, now: Instant) -> Duration          // 次の期限までの待ち
    fn on_tick(&mut self, now: Instant, dirty: bool) -> bool  // 期限が来ていれば時計を進め、dirty なら true（= flush せよ）
    fn reset(&mut self, now: Instant)                 // 即 flush した箇所（recording_pause・BlockEnd・Rotate）用
}
```

修正の中身は 1 点: 期限が来たら、`dirty` でなくても `last` を進める。flush するのは従来どおり `dirty` のときだけ。

あわせて、期限の判断をループの末尾から先頭（`recv_timeout` の前）へ移す。こうすると一時停止中の `continue` の道も期限の判断を通る。flush の時刻は変わらない（末尾で判断していたものを、次の周回の先頭で判断するだけで、その間に待ちは入らない）。`End` と `Disconnected` はループを抜けた後の `writer.flush()` が従来どおり拾う。

TDD の順: まず `FlushClock` を今の挙動のまま（`dirty` のときだけ進める）書いてループを置き換え、既存テストが緑のまま回帰テストが赤になるのを見る。その後で直す。

## 変更対象

### 修正するファイル
- `src-tauri/src/logger.rs` — `FlushClock` の追加、記録のスレッドのループで `last_flush` / `flush_interval` を `FlushClock` に置き換え、回帰テストの追加

### 新規作成・削除するファイル
- なし

## 影響範囲

- logger.rs の記録のスレッドの中だけ。`FlushClock` は非公開。
- 書く内容・書く順は変えない（`writeln!` の各腕には手を入れない）。一時停止のゲートも変えない。
- `recording_pause` / `BlockEnd` / `Rotate` の即 flush は `clock.reset(now)` に置き換えるだけ。

## 既存パターンとの整合性

- `recording::is_writable_while_paused`、`tray::measure_state` と同じく、判断を純粋な部分に切り出して単体テストする。
- `Instant` を引数で受けるので、テストで眠らずに時刻を進められる。

## テスト戦略

- 単体テスト（回帰）: `dirty=false` のまま期限を過ぎて `on_tick` を呼んだ後、`wait` が 0 にならない（修正前は赤）。
- 単体テスト（約束の保持）: `dirty=true` なら期限で `on_tick` が true／期限前は false／`reset` の後は `wait` が `interval` に戻る。
- ループの回帰（code-reviewer の MEDIUM を受けて追加）: 実際のロガーで一時停止中に行を 500ms ごとに 13 本流し、ループの周回数が 200 未満（`#[cfg(test)]` の個体ごとの数え上げ）。
- 定期の flush（Codex の指摘を受けて追加）: 一時停止せずに 1 行送り、終了の前に期限でファイルに出ることを確かめる。
- 既存の logger のテスト（一時停止中に書かない・`recording_pause` の即 flush など）が緑のまま。
- `cargo test --manifest-path src-tauri/Cargo.toml --workspace`・clippy。
- `gse-replay --snapshot` は HMM に触れないので任意（念のため回す）。
- 実機: 開発版（識別子を変えて O1 と並べる）の「停止中」の CPU を、直す前後で累積 CPU 時間の差で比べる。

## ロールバック計画

1 コミットの revert で戻る。ファイルの形式は変わらない。
