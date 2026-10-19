# 次のセッション: 手跡の表現の入力（カーソル・クリック・ホイール）を「表現には使うが記録しない」と決める ADR を起こす

> 書いた日: 2026-10-20（Mac・研究者の依頼）
> 機械: Mac だけで完結する（G-GEAR の結果は待たない）
> 枝: `docs/tangibility-design`（worktree `/Users/johnd/GSE-prototype-tangibility`）
> 返答・記録・AskUserQuestion は日本語で。記号（★・⚠️）を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。
> PR は出さない（A4 の処理が続いている間は、PR を出す案を選択肢にも入れない）。push までにする。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-handmark-input-adr.md を読んで、§2 から始めて。
```

## 1. 先に読むもの

- `.steering/20261020-handmark-multi-input/decisions.md` の判断 2・7・9・10・11（写し方・ADR を起こすこと・型と境界と振る舞いの 3 層・粒がカーソルへ寄る）。
- 同じタスクの `design.md` §1〜§4（macOS の実測・Windows の調べ・ロガーへ渡さない形・ADR の要否）。
- `.steering/20261018-handmark-nature-v3-grading/decisions.md` の判断 8（打鍵以外の入力を、記録せずに表現の入力として使う・条件 4 つ）。
- `docs/adr/ADR-014-continuous-natural-work-collection.md` の D4（ポインタの取り方と「入れないもの」の表。絶対座標・符号付きの dx/dy・一回ごとの列を名指ししている）。
- `docs/adr/ADR-025-no-self-quantification-return.md`（本人に量を返さない）。
- 前例のテスト: `src-tauri/src/wallpaper.rs` の `person_operations_leave_no_trace_in_the_applog` と `the_wallpaper_layer_cannot_write_records`（R-P9）。
- 見本: `.steering/20261020-handmark-multi-input/handmark-nature-multi.html`（公開 https://claude.ai/artifact/4FCokjbqZd13PXgVw2MkSg ）。

## 2. やること

1. **タスクを作る**（`/start-task`）。
2. **ADR の番号を決める**。2026-10-20 時点で main と本枝の最新は ADR-039。未マージの枝（`origin/docs/adr*` など）が番号を使っていないかを確かめてから決める。
3. **ADR の中身を研究者に確かめながら書く**。Claude の見立てでは、決めることは次のとおり。
   - 範囲: 表現（手跡の背景の層）の入力として、カーソルの位置・動き・クリック・ホイールを使ってよい。記録・送信はしない。ADR-014 D4 は O1 の収集の決まりで、表現の側を縛らないことを明示する（D4 の本文は書き換えない）。
   - 境界の 3 層（判断 9）: 型（`Serialize` も `Debug` も付けない）・境界（別モジュールとソース検査）・振る舞い（入力を与えて記録が増えないテスト）。
   - 溜めない: 最後の 1 点と数秒で戻る値だけを持つ。画面の上でも跡は数秒で消える（制約 1）。
   - 数で返さない（ADR-025）。
   - OS の差: macOS は位置（`NSEvent.mouseLocation`）とクリック（`pressedMouseButtons` の繰り返し読み）が権限なしで読めた（実測）。ホイールはどちらの OS も繰り返し読む方法がなく、イベントを取る仕組みが要る（Windows は O1 の Raw Input と受け先を奪い合う）。ホイールを実物に入れるかは見本を見てから（判断 6）。Windows は実測していない。
   - アプリの切り替えは使わない（判断 3）。
4. 引用が要る記述は `citation-ssot` に従う（ADR も対象）。
5. 完了時に `/cross-review` を行う。push まで。

## 3. 残っていること（この ADR の外）

- 研究者が見本を動かして見ること（入力を足すほど「自分の作業が一緒にいる」に寄るか、騒がしさに寄るか。粒の寄り方が弱すぎないか）。
- macOS のホイールを権限なしで取れるか（未確認）。権限ありの対照もまだ取っていない。
- Windows の実測（`GetCursorPos`・`GetAsyncKeyState`）。Windows 機で収集だけを頼む形で。
- 50ms より短いクリックの取りこぼし。
- 多入力の伏せた見比べ（写し方が固まってから）。
- 背景の層の試作（`spike/handmark-stage`）への持ち込み（ADR の後）。
