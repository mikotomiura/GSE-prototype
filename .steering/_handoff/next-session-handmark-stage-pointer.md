# 次のセッション: 手跡の背景の層の試作に、カーソルとクリックを持ち込む（ADR-040 の見直しを含む）

> 書いた日: 2026-10-21（Mac・研究者の依頼）
> 機械: Mac だけで完結する（G-GEAR の結果は待たない。Windows の実測もこのタスクでは待たない）
> 作業の枝: `spike/handmark-stage`（worktree `/Users/johnd/GSE-prototype-handmark-stage`）。コミットの前に `git branch --show-current` を確かめる。
> このメモと ADR-040 がある枝: `docs/tangibility-design`（worktree `/Users/johnd/GSE-prototype-tangibility`）
> 返答・記録・AskUserQuestion は日本語で。記号（★・⚠️）を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。
> PR は出さない（A4 の処理が続いている間は、PR を出す案を選択肢にも入れない）。push までにする。本線にマージしない。

## 0. 新しいセッションで最初に打ち込む文

```
/Users/johnd/GSE-prototype-tangibility/.steering/_handoff/next-session-handmark-stage-pointer.md を読んで、§2 から始めて。
```

## 1. 先に読むもの

- `docs/adr/ADR-040-handmark-input-not-recorded.md`（枝 `docs/tangibility-design`）。とくに D3 の 2 つの表・D4・D6・D7・Migration。ステータスは Proposed で、このタスクで見直すと書いてある（Migration 4）。
- `.steering/20261021-handmark-input-adr/decisions.md`（判断 1〜7）と `design.md`（レビューの指摘への対応・一次資料で確かめたこと）。
- `.steering/20261020-handmark-multi-input/decisions.md` の判断 2・9〜12 と `design.md` §1〜§4（macOS の実測・写し方）。見本は同じタスクの `handmark-nature-multi.html`（公開 https://claude.ai/artifact/4FCokjbqZd13PXgVw2MkSg ）。
- 試作の側（枝 `spike/handmark-stage`）: `.steering/20261016-handmark-stage-spike/`（decisions.md・results.md・manual-check.md）と `.steering/_handoff/next-session-handmark-stage-followups.md` §4「守ること」。
- 前例のテスト: `src-tauri/src/wallpaper.rs` の `person_operations_leave_no_trace_in_the_applog` と `the_wallpaper_layer_cannot_write_records`（R-P9）。

## 2. やること

1. **タスクを作る**（`/start-task`。作るのは枝 `spike/handmark-stage` の側）。
2. **ADR-040 を試作の枝でどう読むかを決める**。ADR-040 は `docs/tangibility-design` にしか無く、`spike/handmark-stage` には無い。取り込む（cherry-pick など）か、別の worktree から読むだけにするかを研究者に聞く。
3. **D3 の検査から書く**（Migration 1）。表の行き先ごとに、止め方と陽性対照を付ける。対照の文字列は実行時に組み立て、検査対象のファイルに書かない。
4. **カーソルの位置とクリックを入れる**（D6: 描画のたびに一点を読む。macOS は `NSEvent.mouseLocation`・`pressedMouseButtons`）。D4 の「溜めない」（Rust の側は最後の一点だけ・窓の側は名前を決めた固定数の枠・寿命を過ぎたら位置と時刻を消す・入力を切ったら取得を止めて配送待ちを捨てる）をテストで固定する。
5. **macOS でホイールを D7 の条件どおりに取れるかを確かめる**（権限なしで取れるか・権限ありの対照）。取れなければホイールは入れない。
6. **負荷は合成の入力か、ポインタを切った条件で測る**（判断 7）。研究者の手で動かしたポインタの描画の回数を CSV に書かない。
7. **研究者の試視**（見る前に Claude が起動して「開始する」を押せる。手順は `manual-check.md`）。
8. **ADR-040 を見直す**（Accepted にするか・D6 の未決を閉じるか・窓ごとにコマンドを止めるか）。Accepted にするなら `expression-channel.md` §8 の `E-11` の行に追記する（Migration 5）。ADR の本文は書き換えず、見直しの結果は新しい節か新しい ADR で足す。どちらにするかは研究者に聞く。
9. 完了時に `/cross-review`。push まで。

## 3. いまの試作で ADR-040 とぶつかりそうな所（2026-10-21 に読んだ範囲・実物で確かめ直す）

- 窓の側（`src/components/HandmarkStage.tsx`）は計測のために `invoke("handmark_stage_tick", ...)` を呼んでいる。ADR-040 D3 は窓の側のソース検査で `invoke` を含まないことを求める。ポインタを入れた版で計測の `invoke` をどう分けるか（計測の版を別にする・計測の口を合成の条件だけにする など）を決める必要がある。
- Rust の側（`src-tauri/src/handmark_stage_spike.rs`）は `src-tauri/src/` の直下にあり、計測の CSV を `std::fs::File::create` で書く。ADR-040 D3 は OS の API を読むコードを `input/` に、O1 の `observe*.rs` とは別のファイルとして置くと決めている。ポインタを読むコードの置き場所と、計測のファイルを持つモジュールとの分け方を決める。
- 打鍵は `handmark-stage-key` のイベントで `emit_to` している。ポインタは別の専用のイベント名にし、主窓のコードがその名前を `listen` しないことをソースで検査する（D3 の「他の窓への配送」）。主窓の `App.tsx` が target なしで `listen` していることは、レビューの報告で聞いただけで、行は確かめていない。
- `capabilities/handmark-stage.json` の記述どおり、窓ごとにアプリのコマンドは止められない（AppManifest が無い）。

## 4. 守ること

- 試作の枝の「守ること」（`next-session-handmark-stage-followups.md` §4）をそのまま守る。`analysis/portrait/`・`wallpaper*.rs`・`eh3.rs`・G-GEAR の `experiments/` に触れない。背景は `engine`・`invitation`・`p_stuck` に依存しない。
- 打鍵の内容（キーの種類）を材料にしない。研究者の打鍵とポインタを記録に使わない（試視の起動は `env -u GSE_HANDMARK_SPIKE_MEASURE`）。
- 計測の CSV は OS の一時ディレクトリの `gse-handmark-spike/` に残るので、測った後は消す。
- キーストロークの内容や NDJSON の生ログを Codex に送らない。

## 5. このタスクの外に残るもの

- Windows の実測（`GetCursorPos`・`GetAsyncKeyState`）。Windows 機の Claude Code に収集だけを頼む形で。依頼文はまだ書いていない。
- 50ms より短いクリックの取りこぼしの量（D6）。このタスクで測れれば測る。
- 多入力の伏せた見比べ（写し方が固まってから）。
