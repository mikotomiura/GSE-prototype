# 引き継ぎ — logger.rs の書き出しの待ちが 0 で回り続ける見込みの件を本線で直す

> 使用済み（2026-10-30）: `.steering/20261030-logger-flush-busy-loop/`（worktree `GSE-prototype-logger-flush`・枝 `fix/logger-flush-busy-loop`・push 済み）で直した。§2.5 の「軽くする設計」は別タスク。

> 作成: 2026-10-30（手跡の帯の試作のタスク `spike/handmark-stage` の計測中に見つけた・研究者が AskUserQuestion で次のタスクに選んだ）。
> このメモを一次資料にしない。行番号と挙動は、コードと実測で確かめ直す。

## §0 始め方

1. `/start-task` → `/fix-bug`（回帰のテストを先に書く）。枝は main から worktree で切る（`git fetch` してから）。
2. 返答・記録・AskUserQuestion は日本語で。記号を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。
3. O1 の収集アプリ（`~/Desktop/O1_実施用_macOS/gse-next.app`・研究者の Mac で記録中）は止めない・起動しない。開発版を動かすなら識別子を変えて並べて起動する（下の §3）。
4. NDJSON の生ログとキーストロークの内容は外部の LLM に送らない。

## §1 見つけたこと（試作の枝での実測・2026-10-30）

- 一次: `/Users/johnd/GSE-prototype-handmark-stage/.steering/20261030-handmark-edge-strip-impl/results.md` の run7 の節。
- 開発版がトレイで「停止中」のとき、本体が 1 コアの 78.8%・42.8%（別の回に 94% も）を使った。「記録中」にすると 2〜4% に下がった。
- `sample` で見ると、本体の CPU の多くが記録のスレッドの `crossbeam` の待ち（`Backoff::snooze`・`LogEntry` の `recv`）だった。
- コードを読んだ見立て（未確認）: `src-tauri/src/logger.rs` の記録のスレッドのループ（2026-10-30 の main で 1927 行付近）で、待ち時間を `flush_interval.saturating_sub(last_flush.elapsed())` で決めている。書くものが無い（`dirty=false`）まま 5 秒を過ぎると `last_flush` が更新されず、待ち時間が 0 のまま `recv_timeout(0)` を回り続ける。
- 同じ行は `origin/main` にもある。O1 の収集アプリは記録中なので書くものが絶えず来て、平均 約 0.9%（6.6 日で CPU 81 分）と目立たない。

## §2 確かめること・直すこと

1. 見立てを確かめる: 「停止中」で `last_flush` が更新されない道と、その間の `recv_timeout` の待ち時間を、テストかログで確かめる。「停止中」で記録のスレッドが生きている理由（どのエントリを待っているか）も。
2. 回帰のテストを先に書く（書くものが無いまま 5 秒を過ぎても、待ち時間が 0 にならない）。赤を見てから直す。
3. 直す（例: 書くものが無くても期限が来たら `last_flush` を進める）。flush の意味（5 秒ごとに書き出す・記録の約束）を変えないこと。`data-privacy` Skill と、一時停止中は 1 バイトも書かない約束（同じループの上のコメント）を崩さないこと。
4. O1 の配布物への影響: 被験者が記録を止めている間（一時停止・停止）に同じことが起きるかを確かめる。起きるなら、配る版の扱いを研究者に聞く（`docs/o1-distribution-tag.md`）。
5. 研究者の関心（2026-10-30）: GSE をもっと軽く動かす設計の検討。手跡の帯の確かめの最後に、重い処理の間はトレイから前面に出られなかった。この件を直した後に、何が CPU を使っているかを測り直すと、軽くする検討の出発点になる（今回のタスクの範囲かは研究者に聞く）。

## §3 計測の道具（試作の枝にある）

- `/Users/johnd/GSE-prototype-handmark-stage/.steering/20261030-handmark-edge-strip-impl/probe/run-dev.sh`（識別子を `com.johnd.gse-next-spike` に変えて O1 と並べて起動・記録は一時フォルダ）と `cpu-window.sh`（プロセスごとの CPU の差分）。本線用に写すときは、試作の環境変数（`GSE_HANDMARK_STAGE_SPIKE`）を外す。
- `top -l 2` は CPU% を過小に出す（記憶 `macos-top-l2-undercounts-cpu`）。累積の CPU 時間の差で測る。
- 開発版を止めるときは、自分が起動したプロセス番号・npx・vite だけを止め、一時フォルダを消す。前の起動の vite がポート 1420 に残ると起動に失敗する。
