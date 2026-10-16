# 引き継ぎ: セッションのロガーが、書くものが無いと CPU を 1 コア使い続ける欠陥を直す

作成 2026-10-16（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号を多用しない。研究者に決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。PR を出すかは研究者に確かめる。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-logger-idle-busy-spin.md を読んで、/start-task でロガーの空回りを直すタスクを立て、/fix-bug で回帰テストから始めて。
```

このメモは枝 `spike/handmark-a-surface`（worktree `/Users/johnd/GSE-prototype-handmark-a`）にある。直す枝は `origin/main` から切る（`git fetch` してから・worktree を切る）。

## 1. 見つけたこと（一次は `.steering/20261016-handmark-ripple-spike/results.md` §5）

- 波紋の試作の計測の前（セッションを始める前）に、開発版のアプリが CPU を約 180〜195 % 使っていた。`sample` で採ると、セッションのロガーのスレッドが `recv_timeout` の中でほぼ全部の時間を使っていた（1002 サンプル中 993）。
- `src-tauri/src/logger.rs:1927` の `let timeout = flush_interval.saturating_sub(last_flush.elapsed());` に対し、`last_flush` を更新するのは `dirty` のときの flush（`:2451`）などだけ。書くものが無いまま最後の flush から 5 秒を過ぎると `timeout` が 0 になり、次の行が来るまで `recv_timeout(0)` を回し続ける。
- 本線（`origin/main`・2026-10-16 に確かめた）にも同じ形があり、`5feaaf90`（2026-03-09）から入っている。
- メインスレッドも CPU を使っていたが切り分けていない（別の原因かもしれない）。

## 2. 確かめていないこと

- セッション中（打鍵や pointer_bin の行が来続けるとき）にも空回りが起きる割合。行が 5 秒以上来ない間だけ起きるはず（未測定）。
- O1 の配布物（リリース版）でも同じだけ CPU を使うか。8 時間の負荷の測定（`next-session-windows-runtime-cost-8h.md` など）の数字に入っていたか。
- Windows でも同じか（コードは共通なので起きるはずだが未測定）。

## 3. 直し方の候補（決めるのは次のセッション）

- `dirty` でないときは `timeout` を `flush_interval` にする、または flush の判定とは別に `last_flush` を進める。
- 回帰テスト: 何も送らないロガーで、受け待ちが 0 にならないこと（例: 一定時間の受け待ちの回数を数える・純粋な関数に切り出して `timeout` を検査）。赤を先に見る。
- 直した後に、セッションを始める前の開発版の CPU を `sample` か `ps` で測り直す（陽性対照は直す前の版）。

## 4. 守ること

- `logger.rs` は data-privacy の Skill の対象。書く中身は変えない。
- HMM の挙動は変えないので `HMM_VERSION` は上げない見込み（確かめる）。
