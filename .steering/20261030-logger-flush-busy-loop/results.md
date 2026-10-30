# 実測の記録

測り方: `probe/cpu-window.sh`（`ps` の累積 CPU 時間の差を秒で割る。1 コア = 100%）。`top -l 2` は使っていない。

## 1. 開発版の「停止中」（直す前・main 5d7c53be・2026-10-30 15:45 JST）

- `probe/run-dev.sh` で識別子 `com.johnd.gse-next-logger-flush` の開発版を O1 の収集アプリと並べて起動した。トレイは「停止中」（非 O1・開始前）。
- 本体 60 秒 × 2: **1.60% / 0.75%**。空回りは起きなかった。
- `sample` で見ると、記録のスレッドは `park_timeout` → `semaphore_timedwait_trap` で眠っていた。
- 理由: この状態でも 1 秒ごとに `feat` 行が書かれていた（約 2.5 分で `feat` 128 行・`pointer_bin` 33 行など）。`dirty` が 5 秒ごとに立つので、期限で flush されて `last_flush` が進む。
- つまり非 O1 の開始前の「停止中」は空回りの条件に入らない。試作の枝の run7 で 40〜94% が出た理由（その起動で `feat` が出ていなかった理由）は、この枝では確かめていない。
- 一時停止のボタン（「すぐ止める」）は開始後のダッシュボードにだけ出るので、開発版の UI では一時停止を起こさなかった。開発版は止め、一時フォルダを消した。

## 2. ロガーを実際に動かすテストでの再現（コミットしない一時のテスト）

`SessionLogger::start` で記録のスレッドを起こし、テストのプロセスの CPU を外から測った（`#[ignore]` の一時のテスト 2 本。測った後に消した）。

| 条件 | 0〜4 秒 | 8〜38 秒（直す前） | 8〜38 秒（直した後） |
|---|---|---|---|
| (a) 何も送らない | 0.00% | **93.23%** | **0.00%** |
| (b) `RecordingPause{paused:true}` の後、1 秒ごとに `FocusTransition` を送る（全部落とされる） | 0.00% | **98.33%** | **0.00%** |

- 直す前は、開始から 5 秒を過ぎたところで 1 コアを使い切る。見立てどおり（`dirty=false` のまま期限を過ぎると `last_flush` が進まず、`recv_timeout(0)` を回る）。
- (b) は O1 の被験者の一時停止中と同じ道（`feat` などのデータ行がゲートの `continue` で落とされる）。

## 3. 単体テストの赤と緑

- 切り出しだけ（挙動はそのまま）で `flush_clock_idle_past_deadline_does_not_spin` が赤（`期限を過ぎた後の待ちが 0 のまま: 0ns`）、ほかの logger のテスト 98 件は緑。
- 直した後: logger のテスト 99 件が緑。
- ループの周回数のテスト `paused_logger_does_not_spin_past_flush_deadline`（code-reviewer の MEDIUM を受けて追加・decisions.md 判断 2）: 直した版で緑（6.5 秒）。変異で赤を確かめた: 元のバグに戻す → 383,764 周、ループから `on_tick` の呼び出しを消す → 373,319 周（しきい値 200）。
- 全体: `cargo fmt --check` 緑、`cargo test --workspace` 1019 件 passed・2 ignored、`cargo clippy --all-targets -- -D warnings` 緑、`gse-replay --snapshot minimal` 15 件一致。
- Codex の指摘を受けた直し（decisions.md 判断 7）の後:
  - 周回数のテストは、一時停止の行を処理し終えた時刻から 5.5 秒たつまで待ち、届いた 14 行を処理し終えた（周回数 15 以上）のを確かめてから数える。
  - 足したテスト `logger_flushes_written_line_at_deadline`: 一時停止せずに 1 行送り、終了の前にファイルに出るのを待つ（8 秒で諦める）。
  - 変異: 元のバグに戻す → 単体 1 本と周回数のテストが赤（375,176 周）。ループの定期の `writer.flush()` を消す → `logger_flushes_written_line_at_deadline` が赤（「8 秒たってもファイルに出ていない」）。
  - 全体: fmt 緑、`cargo test --workspace` 1020 件 passed・2 ignored、clippy 緑。

## 4. O1 の配布物への影響

- O1 で配っている v0.1.40（`bb1b1eed` の注釈付きタグ）にも同じループがある（`logger.rs:1874` の待ち・`:2378` の期限の判断）。コードの起源は v2.19 の macOS 移植のコミット `5feaaf90`。
- O1 では記録中も 1 秒ごとに `feat` が来るので、ふつうは空回りしない。ただし `feat` は推定の結果がある周にだけ送られる（`lib.rs` の `if let Some(f) = out.feat`）ので、IME の候補窓の間など行が 5 秒以上途切れると、記録中でも途切れている間は起きうる（cross-review の指摘で書き方を弱めた。途切れる道を全部は洗っていない）（研究者の Mac の O1 は 6.6 日で CPU 81 分・平均 約 0.9%）。
- **被験者が「すぐ止める」で一時停止している間は、空回りの条件に入る**（2 の (b) と同じ道）。再開するまで 1 コアを使い続ける見込み。Windows も同じコード（crossbeam の待ち）なので同じ見込み（Windows では測っていない）。
- 記録の内容には影響しない（落とす行は従来どおり落とし、書く行は従来どおり書く）。影響は CPU・電池・発熱。
