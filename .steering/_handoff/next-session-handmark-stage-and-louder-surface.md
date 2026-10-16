# 引き継ぎ: 手跡の試作 —— 背景の層（デスクトップの高さの窓）の実現性と、右下の小面を少し主張させる版（Mac）

作成 2026-10-16（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号を多用しない。研究者に決めてほしいことは、報告の文章に並べず AskUserQuestion で、推奨と理由を添えて聞く。PR は出さず push で止める。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-handmark-stage-and-louder-surface.md を読んで、/start-task で手跡の背景の層の試作のタスクを立て、§3 の 1（小面を少し主張させる）から始めて。
```

このメモは枝 `spike/handmark-a-surface`（worktree `/Users/johnd/GSE-prototype-handmark-a`）にある。新しい枝はこの枝から切る（小面の窓のコードがここにある）。worktree を新しく切り、コミットの前に `git branch --show-current` を確かめる。

## 1. 何が決まったか

- 波紋の小面（28 px・灰・白い輪・250 ms・打ち切り）を研究者が試視して「見えずらかった。やはり、少し主張したい感じで、次は壁紙の箇所などでの背景にするか。あとはついでに右下の箇所も少し残した感じで次は試作」（`.steering/20261016-handmark-ripple-spike/results.md` §6）。
- 研究者の選択（同 decisions.md 判断 7・推奨どおり）:
  - 背景はデスクトップの高さの窓（壁紙の上・アイコンと他の窓の下）。壁紙の画像は書き換えない。
  - 右下の小面は残し、大きさと色の両方で主張させる。
  - 新しいセッション・新しい枝・新しいタスクで。
- 表現の議論（枝 `docs/tangibility-design` の `.steering/20261016-handmark-expression-design/decisions.md`）の判断 2・3・5・6 は前提のまま。判断 5（28 px・灰）はこの試視で見直しの条件に当たった。背景は打鍵だけで動かし推定を受け取らない（判断 2）。30 秒の窓の要約を 1 秒ごとに更新し滑らかに移す（判断 3・`res=sec`）。参加者に出すのは EH3 の後（判断 3）。D の写し方は仮（G-GEAR の机上の検査が未着手のため・判断 6）。

## 2. いまの事実

- 波紋の試作の結果（同 results.md）: 一定の間隔の列では、間隔が 250 ms より短いと波紋は途切れずに描かれ続けた（0.06〜0.15 秒で 100 %、バーストで 46 %）。遅れは全体で中央値 49 ms・95 パーセンタイル 66 ms、起動直後の 2 打だけ 314・282 ms（1 例・原因未確認）。窓は 32×32・右下・取り込みの除外の設定と fail-closed は前の試作のまま（標準のスクリーンショットには写る・Chrome と Zoom 自動には写らない）。
- 描画は `src/components/HandmarkSurface.tsx`（canvas・見本の甲-2 の式）。窓は `src-tauri/src/handmark_spike.rs`（`SIDE = 32`・`MARGIN = 14`）。計測は `GSE_HANDMARK_SPIKE_MEASURE=1` のときだけ。研究者の試視の起動は `env -u GSE_HANDMARK_SPIKE_MEASURE`（manual-check.md）。
- 合成の打鍵: `.steering/20261016-handmark-a-surface-spike/synthetic-keys.applescript`・`.steering/20261016-handmark-ripple-spike/synthetic-burst.applescript`。集計は scratchpad の Python で行った（残っていない。CSV の列の意味は design.md）。
- AX: osascript の `windows` は gse-next の窓を 0 枚と返した。AX API（swift で `AXUIElementCreateApplication`）なら窓とボタンが読め、「開始する」を AXPress で押せた。
- 本線の欠陥の候補（ロガーが書くものが無いと CPU 1 コアを使う）は別のタスク（`next-session-logger-idle-busy-spin.md`）。開発版を起動して「開始する」を押す前は CPU が約 180〜195 % になるので、負荷を測るときはこれを差し引くか、セッション中に測る。
- 背景の層の技術は確かめていない（`.steering/20261012-portrait-rhythm-motion/survey-results.md` §2 は枝 `docs/tangibility-design` 側にあるかもしれない・場所を確かめる）。macOS は `kCGDesktopWindowLevel` と `collectionBehavior`（`.canJoinAllSpaces` `.stationary`）が文書にあるが、アイコンの上下・Spaces・全画面・複数ディスプレイでの振る舞いは未確認。WebView は覆われた窓で描画やタイマーを絞る仕組みがあり（二次）、背景の窓で動きが止まるかもしれない。

## 3. 段

1. 右下の小面を少し主張させる: 大きさ（例 40 px）と色（輪を地と差の出る濃い色に・線を太く・地の点も濃く）。明るい壁紙と暗い壁紙の両方で見えるか。値は見本と並べて研究者に選んでもらう（AskUserQuestion）。窓の大きさを輪の最大に合わせ直す。
2. 背景の層の実現性: デスクトップの高さの窓に描けるか（アイコンとの上下・Spaces・全画面・複数ディスプレイ）、他の窓に覆われても 1 秒ごとの更新と移り変わりが続くか、会議の画面共有（Chrome の `getDisplayMedia`・Zoom の自動）と標準のスクリーンショットに写るか（陽性対照つき）、負荷（覆われているとき・電池のとき）。材料は打鍵の時刻だけ。推定を受け取る口を作らない。写し方は仮（見本の等高線の波など）。
3. 研究者が自分の画面で、背景と右下の小面を一緒に見る。

## 4. 守ること

- `src-tauri/src/analysis/portrait/`・EH3 の壁紙のファイル（`wallpaper*.rs`・`eh3.rs`）・G-GEAR の `experiments/` に触れない。新しい層が `engine`・`invitation`・`p_stuck` に依存しない。
- 打鍵の内容（キーの種類）を材料にしない。計測は合成の打鍵で。研究者の打鍵を記録に使わない。
- 背景の層の実現性は、確かめた範囲だけを書く（陽性対照つき）。
- 作業への妨げは、人に見せて試す前に測る。

## 5. その後

- 手跡の理論の語（`next-session-handmark-theory-term.md`・枝 `docs/tangibility-design`）。
