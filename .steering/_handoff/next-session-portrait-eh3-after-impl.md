# 引き継ぎ — EH3 の実装の後（実機の確認の残り・ADR-035・見本の選択・凍結まで）

> 作成: 2026-10-11（EH3 の実装のタスク・G-GEAR）。このメモは一次資料にしない。
> 一次は `.steering/20261011-portrait-eh3-impl/`（requirement・design §10〜11・decisions 判断 1〜10・tasklist）、
> 要件 `.steering/20261011-portrait-eh3-prereg/implementation-requirements.md`、稿 `experiments/20261011-portrait-eh3/preregistration-draft.md` §10・§10.1。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-eh3-after-impl.md を読んで、EH3 の実装の後の作業を始めてください。
PR #353 が main に merge 済みであることを先に確かめてください。
```

## §1 いまの状態

- EH3 の実装は 4 本の PR で main に入った（#350 記録とモード・#351 招待・#352 肖像と壁紙・#353 配布と文書と `/cross-review` 2 巡の対応）。
- 研究者の決定は判断 1〜3・6（実装の前提・招待の面と日の数え方・O1 の器・終わりの時点・ESM はアプリの外・停止中は出さない・繰り越さない・GSE の窓への遷移を記録しない・self-marker を止める）。
- Windows の実機は自動でできる範囲だけ確かめた（判断 8: 日の割り当てで壁紙が替わる・強制終了の後に EH3 の印を外すと元の壁紙と同じ SHA-256 に戻る）。
- 見本のページ（研究者の非公開の artifact `https://claude.ai/artifact/6kMdvCWz1iQZgmhBiWgDx1`）を研究者に見せた。F-1（形の文法と drift）と F-3（図像）は、研究者の決定で凍結の前に選ぶ。
- Codex の日の上限を 450,000 → 600,000 に上げた（台帳のコメント）。450,000 に戻すかは研究者が決める。

## §2 次にやること（順に）

1. **研究者に伝えて確かめる**（判断 9 の読み替え）:
   - 判断 2 #2 の「条件はその日の最初の起動で決まり」を「最初の打鍵」に読み替えた理由（起動で決めると seed の印が翌朝に見えない）。
   - R-P8 のアンインストールは満たさない（やめる前に「壁紙を元に戻す」を案内する）。
   - 稿 §10.1 の値（F-2 の 30 秒・60 秒・30 分・{1,2,4}・時間帯）と R-9 の組み直しの規則の案。
   - `raw` の歩みは縁に留まりやすい（EH1 と同じ挙動・見本に出ている）。F-1 の材料として。
2. **Windows の実機の残り**（研究者の手が要る。研究者の O1 の配布物を先に終了してもらう・memory「Injected keys not recorded」）: 肖像の成長（打鍵を続けて 5 分ごとの予定）・終了時の seed（トレイの終了）・スリープと復帰・再起動・本人の差し替え・トレイの「壁紙を元に戻す」・招待の図像（推定の停滞が要る）と説明と設定の窓・画面共有からの除外。試験は `USERPROFILE`・`HOME`・`GSE_DATASET` を一時フォルダに替えて起動する。
3. **macOS の実機**: `.steering/_handoff/next-session-portrait-eh3-macos-verification.md`（Mac で）。
4. **ADR-035 の見直しと Accepted**（研究者の決定: 実機で図像と設定の窓を確かめた後）。本文は書き換えず、見直しの記録（R-1 (i) の読み方・D2 の既定値・D3 の選択肢・D6 の設定の画面）を付けて状態を変える。D6 が Accepted になったら `expression-channel.md` §8 `E-11` の該当部分を閉じる（Migration 2）。
5. **F-1・F-3 を研究者が選ぶ**: 図像は `src/components/InvitationGlyph.tsx` の `INVITATION_GLYPH` だけを替える。文法と drift は印 `eh3.mode` の `grammar=` と `drift=`。説明と設定の窓の文面（`InvitationSettings.tsx`）も F-3 で研究者に見せる（「消えてから 30 分」は実装では出てから 31 分・「記録には含めません」の範囲）。
6. **罪悪感の尺度のサーヴェイ（F-6）と反発の尺度の選択**・稿 §10 の残り（F-7 の ESM の文面・F-8 の閾値・F-10 の割り当ての表・F-11 同意文書・F-13）。
7. **凍結の直前**: attack-me（stage `prereg`・Codex に送るときは `--preview` で研究者の OK）と `/cross-review` 2 巡。
8. `schema_dto.rs` の `Eh3Day` の doc（出し直しの契機の書き漏らし）は、次に schema を触るときに直す（gse-dataset の同期と一緒に）。

## §3 守ること

- 応答は日本語にする。★・⚠️ は多用しない。
- `git add` はファイルを名指しする。main checkout（`C:\GSE-prototype`）の git には触らない（worktree を切る）。
- 生のログ・NDJSON を Codex や外部の LLM に送らない。
- 研究者の決定（prereg の判断 1・2、impl の判断 1・2・3・6）の中身を変えない。変えるべき理由が出たら研究者に聞く。
- 壁紙を書き換える実機の確認は、研究者の了承を取ってから。終わったら元の壁紙（パスと SHA-256）に戻ったことを確かめて報告する。

## §4 片付け（任意・研究者の判断）

- worktree `C:\wt\portrait-eh3-impl`（merge の後）。
- 古い引き継ぎ `next-session-portrait-eh3-implementation.md` は本タスクで消化した。
