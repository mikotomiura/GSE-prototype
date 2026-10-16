# 引き継ぎ: 手跡の試作 —— 小面を波紋にする・背景の層の実現性を Mac で確かめる

作成 2026-10-16（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない。研究者に決めてほしいことは、報告の文章に並べず AskUserQuestion で、推奨と理由を添えて聞く。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-handmark-spike-ripple-and-stage.md を読んで、/start-task で手跡の試作のタスクを立て、§3 の段 1（小面を波紋にする）から始めて。
```

このメモは枝 `docs/tangibility-design`（worktree `/Users/johnd/GSE-prototype-tangibility`）にある。

## 1. 何が決まったか（一次は `.steering/20261016-handmark-expression-design/decisions.md` 判断 1〜6）

- 背景は打鍵だけで動かし、推定を受け取らない。招待は右上の図像のまま（判断 2）。
- 背景のステージは、30 秒の窓の要約を 1 秒ごとに更新し、滑らかに移す（`res=sec`）。参加者に出すのは EH3 の後のまま。Mac での実現性の試作だけを先に行う（判断 3）。親タスク判断 15 の「時計で更新・打鍵の最中は動かさない」は、ステージについては改めた。
- 小面: 打鍵の時刻にもキーの種類にも依らない反応（判断 4）。形は波紋（甲-2）、大きさ 28 px、位置は右下、動きは 250 ms、続けて打ったら打ち切って次を始める（判断 5）。色は未決（見本の既定は灰）。
- 案 D は F-1 の文法（`raw` / `lattice`）に揃える。案 C はその回の D の形を、小面の上に開く 16:9 の小窓で数秒かけて再生する。小窓は試作の段の仮の置き場で、最終の置き場は試作で見てから決める（判断 6）。
- 見本のページ: https://claude.ai/artifact/5uejeC8kJ9PF2sFTyUquzc（研究者の非公開の artifact。見本の HTML は Claude のスクラッチパッドにあり、残らない）。

## 2. いまの事実

- 小面の試作: 枝 `spike/handmark-a-surface`（worktree `/Users/johnd/GSE-prototype-handmark-a`・`251875b6`）。見た目は `src/components/HandmarkSurface.tsx`（14 px の灰色の丸が白く光る）。遅れ・フォーカス・クリック透過・取り込みの記録は `.steering/20261016-handmark-a-surface-spike/results.md`。合成の打鍵は `synthetic-keys.applescript`。
- 背景の層の技術は確かめていない（`.steering/20261012-portrait-rhythm-motion/survey-results.md` §2）。macOS は `kCGDesktopWindowLevel` と `collectionBehavior`（`.canJoinAllSpaces` `.stationary`）が文書にあるが、アイコンの上下・Spaces・全画面・複数ディスプレイでの振る舞いは未確認。WebView は覆われた窓で描画やタイマーを絞る仕組みがあり（二次）、背景の窓で動きが止まるかもしれない。取り込みからの除外は ScreenCaptureKit で効かない報告がある（二次）。
- 相対のタイミングの漏れの検査（`next-session-tangibility-relative-timing-desk-check.md`）は G-GEAR で未着手。D と C の形はそれまで仮なので、この試作では D の写し方は仮の写像（例: 見本の等高線の波）でよい。

## 3. 段（順番は研究者と確かめる）

1. 小面を波紋にする（既存の枝 `spike/handmark-a-surface` の続き）: 28 px・右下・250 ms・打ち切る。速打ち（合成の打鍵）で「直近 10 秒のうち小面が動いていた割合」を測る（判断 5 の見直しの条件）。遅れの記録を前の試作と同じ方法で取り直す。取り込みからの除外と fail-closed は前の試作の設定のまま。
2. 背景の層の実現性（新しい枝・Mac）: デスクトップの高さの窓に描けるか（アイコンとの上下・Spaces・全画面・複数ディスプレイ）、他の窓に覆われても 1 秒ごとの更新と移り変わりが続くか、会議の画面共有（Chrome の `getDisplayMedia`・Zoom の自動）と標準のスクリーンショットに写るか（陽性対照つき）、負荷（覆われているとき・電池のとき）。材料は打鍵の時刻だけ（`res=sec`）。推定を受け取る口を作らない。
3. 必要なら、C の小窓（小面の上に開く・きっかけを記録しない）。

## 4. 守ること

- `src-tauri/src/analysis/portrait/`・EH3 の壁紙のファイル・G-GEAR の `experiments/` に触れない。肖像と招待の分け方（親タスク判断 2・16）を守る: 新しい層が `engine`・`invitation`・`p_stuck` に依存しない。
- 打鍵の内容（キーの種類）を材料にしない（data-privacy）。合成の打鍵で測る。研究者の打鍵を記録に使うなら、そう決めてから。
- 背景の層の実現性は、確かめた範囲だけを書く（断定しない・陽性対照つき）。
- 作業への妨げは、人に見せて試す前に測る（判断 3 のトレードオフ）。この試作は研究者が自分の画面で見るまで。
- PR は出さず、push で止める。

## 5. 試作の後

- 手跡の理論の語（`next-session-handmark-theory-term.md`）。研究者の選んだ順は「試作 → 理論の語」。
