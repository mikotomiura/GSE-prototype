# 引き継ぎ — GSE の CPU の内訳を測り、軽くする設計の出発点を作る

> 使用済み（2026-10-30）: `.steering/20261030-gse-cpu-profile/`（枝 `chore/gse-cpu-profile`・push 済み）で測った。軽くする候補の 1 は 2026-10-31 に `.steering/20261031-trim-ui-polling/` で確かめ、効きは小さかった（約 0.5 ポイント）。

> 作成: 2026-10-30（logger の空回りの修正 `.steering/20261030-logger-flush-busy-loop/` の後。判断 1 で「CPU の内訳と軽くする設計は別タスク」と分けたもの）。
> このメモを一次資料にしない。数字と挙動は、コードと実測で確かめ直す。

## 0 始め方

1. G-GEAR の処理が終わっているかを研究者に聞く。終わっていれば、先に `fix/logger-flush-busy-loop` の PR を git-workflow ルール 6 の手順で出す（push 済み・PR 未作成）。終わっていなければ PR は出さずに 2 へ進む。
2. `/start-task`（タスク名の案: `gse-cpu-profile`）。今回は測って内訳を出すまでで、コードは直さない（直すなら別タスク）。範囲は研究者に AskUserQuestion で確かめる。
3. 返答・記録・AskUserQuestion は日本語で。記号を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。
4. O1 の収集アプリ（`~/Desktop/O1_実施用_macOS/gse-next.app`・研究者の Mac で記録中）は止めない・起動しない。開発版は識別子を変えて並べて起動する。
5. NDJSON の生ログとキーストロークの内容は外部の LLM に送らない。
6. Mac でできる作業だけを選ぶ（G-GEAR の結果を待たない）。

## 1 測る版

- 空回りの修正が入った版で測る。main にまだ入っていないので、修正の枝 `fix/logger-flush-busy-loop`（worktree `/Users/johnd/GSE-prototype-logger-flush`）から新しい worktree を切るか、PR が merge 済みなら main から切る。直す前の版で測ると、空回りが内訳を塗りつぶす。

## 2 測ること

1. 状態ごとの本体の CPU（累積の CPU 時間の差で。`top -l 2` は過小に出る）
   - 開始前の「停止中」・記録中で打鍵あり・記録中で打鍵なし・一時停止中
   - 一時停止中は、修正の後に 0% 近くまで下がることを実機で初めて確かめる場になる（修正のタスクでは実機の一時停止を試せなかった。判断 6）。
2. スレッドごとの内訳: `sample` で、どのスレッド（記録・分析・フック・UI・WebKit の子）が使っているか。WebKit の子は責任者の pid で拾う（記憶 `macos-top-l2-undercounts-cpu`）。
3. 前面に出られない件: 前の引き継ぎには「重い処理の間はトレイから前面に出られなかった」とあるが、試作の記録（`/Users/johnd/GSE-prototype-handmark-stage/.steering/20261030-handmark-edge-strip-impl/results.md` の 20 行目）では、全画面の中かどうかで分かれる見込みと書かれている。CPU と関係があるかを分けて確かめる。
4. 余力があれば: 試作の枝の run7 で、開始前に `feat` が出ていなかった理由（開発版の本線では 1 秒ごとに出ていた。判断 6）。

## 3 道具

- `/Users/johnd/GSE-prototype-logger-flush/.steering/20261030-logger-flush-busy-loop/probe/run-dev.sh`（識別子を変えて O1 と並べて起動・記録は一時フォルダ）と `cpu-window.sh`（プロセスごとの CPU の差分。秒の不正で rc=2、プロセスが無いと rc=3）。
- 開発版を止めるときは、自分が起動したプロセス番号・npx・vite だけを止め、一時フォルダを消す。前の vite がポート 1420 に残ると起動に失敗する。

## 4 出すもの

- results.md に、状態ごとの CPU とスレッドの内訳の表。
- 軽くする候補を、効きの見込みの大きい順に並べた一覧（直すかどうか・どれからやるかは研究者が決める）。
- 次に O1 の版を切るときの実機確認の手順（一時停止中の CPU を含む）を、`docs/o1-distribution-tag.md` の v0.1.40 の注意とつなげて書く。
