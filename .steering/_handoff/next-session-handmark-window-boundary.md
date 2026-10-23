# 次のセッション: 手跡の背景の層が窓に覆われる問題 —— 画面・窓・背景の境界をどう設計し、どうつなぐかを議論する

> 書いた日: 2026-10-23（Mac・研究者の依頼）
> 機械: Mac だけで完結する（議論が中心。G-GEAR・Windows の結果は待たない）
> このメモがある枝: `docs/tangibility-design`（worktree `/Users/johnd/GSE-prototype-tangibility`）。試作の枝は `spike/handmark-stage`（worktree `/Users/johnd/GSE-prototype-handmark-stage`）。コミットの前に `git branch --show-current` を確かめる。
> 返答・記録・AskUserQuestion は日本語で。記号（★・⚠️）を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。
> PR は出さない（A4 の処理が続いている間は、PR を出す案を選択肢にも入れない）。push までにする。本線にマージしない。
> O1 の収集アプリ（`~/Desktop/O1_実施用_macOS/gse-next.app`）は Claude が止めない・起動しない。試作を起動して見る必要が出たら、O1 を止めるかを研究者に聞く。研究者の画面を撮らない（撮るなら先に聞く）。

## 0. 新しいセッションで最初に打ち込む文

```
/Users/johnd/GSE-prototype-tangibility/.steering/_handoff/next-session-handmark-window-boundary.md を読んで、/start-task で議論のタスクを立て、§3 の論点の順番を研究者と決めるところから始めて。
```

## 1. 研究者が挙げた課題（2026-10-23・言葉のまま）

> メディア表現での箇所の現状の課題は, 背景としては起動しているが, フル画面にしたら遮られてしまうこと.そのため, 画面, ウィンドウと背景(壁紙などの位置に当たる存在の箇所)の境界などの具体的にどうデザインし, 接続を図るべきかを次セッションで議論したい.

## 2. いまの作り（2026-10-23 に読んだ範囲）

- 背景の窓は `src-tauri/src/handmark_stage_spike.rs` の `prepare()` で、主画面の全体の大きさにし、層をデスクトップの層（`CGWindowLevelForKey(kCGDesktopWindowLevelKey)`・アイコンの層より下）に置いている。Spaces の扱いは `CanJoinAllSpaces | Stationary | IgnoresCycle`、クリックは透過（`setIgnoresMouseEvents(true)`）、前に出すが key にしない。
- つまり、作りの上で「壁紙の上・アイコンの下」にいる。普通の窓が重なれば、その分だけ隠れる。窓を最大化すればほぼ全部が隠れる。
- macOS の全画面（緑のボタン）は、その窓に専用の Space を作る。デスクトップの層の窓がその Space に出るか、`FullScreenAuxiliary` を足すと何が変わるかは確かめていない（推測で決めない。要るなら最小の試作で確かめる）。
- 主画面だけを覆う。複数のディスプレイ、暗い壁紙は見ていない（`spike/handmark-stage` の `.steering/20261021-handmark-stage-pointer/results.md` §2）。
- 覆われている間も描画は止めていない（入力が無い間は 1 秒に約 10 回に絞るだけ。同 results.md §3・判断 10）。覆われている間は見えないのに負荷がかかる、という論点にもなる。
- 画面端の小面（案 A・右下の波紋）は別の試作で、背景の層とは別の面（`.steering/20261016-handmark-expression-design/decisions.md` 判断 4・5）。

## 3. 議論の論点（順番は研究者と決める・Claude の案で、決まったことではない）

1. **覆われることを、欠点と見るか、性質と見るか。** 壁紙は「窓をどけたときに見えるもの」という性質を持つ。覆われるのを受け入れるなら、課題は「どう見せるか」ではなく「のぞいたときに何が見えるか」になる（覆われていた間の打鍵を、溜めずにどう残すか。ADR-040 D4 の「溜めない」と、判断 2・3 の「打鍵だけで動かす・ゆっくり動かす」との関係）。
2. **境界に出すか。** 窓の縁・窓と窓の隙間・メニューバーや Dock のまわりなど、窓が覆わない所に表現を寄せる案。他のアプリの窓の位置と大きさを読む必要が出るなら、それは新しい入力になる（ADR-040 の D3・D6 の範囲の外。何を読むか・記録しないことの保証をどう検査するかを先に決める）。
3. **前に出るか。** 全画面の上にも出る薄い層（クリック透過）にする案。「背景」から「重ね」へ役割が変わるので、作業を邪魔しないこと・注意を引かないこと（判断 4 の小面の条件、glossary の「予期しない・評価を含まない驚き」）を改めて満たすかを問う。
4. **背景と小面をつなぐか。** 覆われている間は小面が受け持ち、デスクトップが見えたら背景が受け持つ、という分担の案。どちらも打鍵から作るが、同じ打鍵が 2 か所に出ることの意味（一つの世界の二つの窓か、別々の表現か）を決める。
5. **見えないときに描くか。** 覆われているか・全画面かを知って描画を止める案（負荷の論点）。窓の重なりを知る方法によっては、2 と同じく新しい入力になる。
6. **打鍵との接続度。** 試視での研究者の言葉「最初の線の頃の方が打鍵との接続度は強く感じる」（判断 13・未決）。境界の設計で、線の表現に戻すかどうかの判断が変わるかもしれないので、一緒に扱うかを決める。
7. **Windows ではどうなるか。** 壁紙の層に描く手段（WorkerW など）は試していない。macOS で決めた設計が Windows で成り立つかは、別に確かめる必要がある（収集だけの依頼で）。

## 4. 先に読むもの

- `docs/adr/ADR-040-handmark-input-not-recorded.md` と、その末尾の補訂 1（この枝）。とくに D3・D4・D6・D7。
- `.steering/20261016-handmark-expression-design/decisions.md`（判断 2〜6・10〜15）と glossary の「予期しない・評価を含まない驚き」の行。
- 試作の側（枝 `spike/handmark-stage`）: `.steering/20261021-handmark-stage-pointer/decisions.md`（判断 1〜19、とくに 10・13・14）と `results.md` §2・§3・§5、`src-tauri/src/handmark_stage_spike.rs` の `prepare()`。
- 見本: `.steering/20261020-handmark-multi-input/handmark-nature-multi.html`（公開 https://claude.ai/artifact/4FCokjbqZd13PXgVw2MkSg ）。境界の案を見比べるなら、この見本を元に「窓が重なった画面」の見本を作る手がある（実機の画面を撮らずに済む）。

## 5. 議論の後に残っている、本線へ入れる前のタスク（このセッションでは扱わなくてよい）

- macOS: ホイールを切った条件と比べて打鍵の tap の失効が増えないか、入れ切りや一時停止を繰り返してもホイールの tap が残らないか（判断 15・19・ADR-040 補訂 1 の Accepted の条件 (b)）。どちらも O1 を止める必要があり、1 回にまとめる。
- Windows: `GetCursorPos`・`GetAsyncKeyState` の実測（Accepted の条件 (a)・収集だけの依頼で）。
- 2 巡目のレビューの直しの後の画面を見ていない。
