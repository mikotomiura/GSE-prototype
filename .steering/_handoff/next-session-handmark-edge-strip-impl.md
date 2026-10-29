# 次のセッション: 手跡の下の縁の帯とどける操作を試作の枝に入れる

> 書いた日: 2026-10-29（Mac）。設計のタスク: `.steering/20261029-handmark-edge-strip-design/`（枝 `docs/tangibility-design`・worktree `/Users/johnd/GSE-prototype-tangibility`）。
> 実装する枝: `spike/handmark-stage`（worktree `/Users/johnd/GSE-prototype-handmark-stage`）。本線にマージしない。PR は出さない（push までにする）。コミットの前に `git branch --show-current`。
> 機械: Mac だけ。返答・記録・AskUserQuestion は日本語で。記号を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。目で見たことは文章で聞く。
> O1 の収集アプリ（`~/Desktop/O1_実施用_macOS/gse-next.app`）は止めない・起動しない。研究者の画面を撮らない。試作を動かして画面が切り替わる・アプリが隠れるなら、その都度先に聞く。
> キーストロークの内容と NDJSON の生ログは外部の LLM に送らない。アプリの名前はログに書かない。

## 最初に打ち込む文

```
/Users/johnd/GSE-prototype-tangibility/.steering/_handoff/next-session-handmark-edge-strip-impl.md を読んで、手跡の下の縁の帯とどける操作を試作の枝に入れるタスクを始めて。
```

`/start-task` で試作の枝の worktree に `.steering/[日付]-handmark-edge-strip-impl/` を切る。

## 決まっていること（設計のタスクの decisions.md 判断 2〜6・design.md）

- 帯は GSE 本体の窓 1 枚。非アクティブの NSPanel・浮く層・`canJoinAllSpaces` / `stationary` / `ignoresCycle` / `fullScreenAuxiliary`・クリック透過。プロセスは 1 つのまま（/reimagine で v2 を採用・試し 4 で regular の NSPanel が全画面の上に出た）。先例は `overlay_panel.rs`。
- 帯の中身は、風で揺れる線 1 本を主にし、薄い霧 1 本と粒を少し。風は背景と同じもの（`WIND_TICK_MS` 250）を 1 か所で計算して両方に配る。打鍵の時刻は背景と同じ経路で受け取る。
- 描く回数は、入力がある間 30 回/秒、ない間 10 回/秒。帯が全部覆われたら止める。帯はいつも出す。カーソルが近づいたら薄くする。Dock とは何もしない。太さ 14 点・濃さ 70% は仮。
- どける操作の入口はトレイのメニュー 1 項目（「背景を見る」と「戻す」を切り替える）。自分を前面に出して最大 1 秒待ち、出られなければ隠さずにやめる。ただしこの判定は試作では全画面の外でも出られず（試し 5）、本体で確かめてから決める（判断 7。分かれなければ事後確認に切り替える）。本体の終了時に戻す・焦点を奪わない・やめたことを知らせる（design.md 論点 6）。戻すときは、覚えたアプリだけを、元の重なりの奥から順に前へ出し、最後に元の前面のアプリを出す。覚えた一覧は捨てて記録しない。
- どける回数の記録は、試作の段では入れない（方針は design.md 論点 7）。

## 最初に確かめること（design.md の末尾）

1. Tauri の webview の窓を非アクティブの NSPanel にした帯が、全画面の上に出るか。
2. 普段使うアプリ（ブラウザ・エディタ）の全画面で同じか。
3. 本体のトレイを押したとき、前面に出られるか。全画面の外（出られるはず＝陽性対照）と中の両方で（判断 7）。
4. 帯の webview の負荷（30・10 回/秒）。比べる相手は Swift の試作の約 7〜11%（60 回/秒）。

## 先に読むもの

- 設計のタスクの `design.md`・`decisions.md`・`probe-results.md`
- 試作の枝の `src-tauri/src/overlay_panel.rs`・`handmark_stage_spike.rs`・`tray.rs`、`src/components/HandmarkStage.tsx`
- memory の macos-overlay-clickthrough-bug（NSPanel のクリック透過の穴）
