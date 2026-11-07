# 引き継ぎ —— 手跡 PR 1: 段 1 の後期を始められる最小の切れ端（ADR-051 D7）

> 作成: 2026-11-08（Mac のセッション・`.steering/20261108-handmark-to-main-plan/`）。このメモは入口で、一次ではない。決定の一次は ADR-051 と ADR-050、計画の一次はそのタスクの `decisions.md`（判断 P・1・1b・2・3・5・6b）。

## 入口の文

```
/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-handmark-pr1-late-slice.md を読んで、手跡の PR 1（後期を始められる最小の切れ端）を /start-task から始めて。
```

## 前提

- PR 0（ADR-050・ADR-051・README・地図 R10）が main に入っていること。入っていなければ、`docs/handmark-to-main-plan` の PR の状態を研究者に聞く。glossary「手跡」と理論 §1.4 は別の引き継ぎ（`next-session-gse-handmark-pr0-glossary-theory.md`）なので、PR 1 はそれを待たなくてよい。
- 枝は `git fetch` してから origin/main で切り、worktree を作る（memory: parallel-sessions-share-checkout）。

## 何を入れるか（ADR-051 D4・D5・D2 の一部）

1. **割付の表を読む処理**: 研究者が配布前に作る人ごとの表を読む。中身は、前期の長さ（後期の開始日）と後期の日ごとの「あり・なし」。表の SHA-256 を検める。
   - 置き場所と形式は、このタスクで決める。候補は `~/.gse/`、または配布物のフォルダの `s1.mode` の隣。
   - 研究者が表を作る小さな道具（種から表と SHA-256 を出す）も、このタスクか別の PR で用意する。
2. **日ごとの行種**: 割付の上の状態・割付の上の開始日・初めて表示した日・出ていた時間・見えていた時間・切った／戻した時刻・表の SHA-256・描画の種・出せなかった理由。
   - `schema_dto.rs` → `emit_schema` → `schema/current.json`。gse-dataset との parity（`/finish-task` Step 3）を通す。
   - `capabilities.rs` には、段 1 のときだけ `config_gated` として宣言する（既存の 4 行種と同じ作法）。
   - 区間の削除（`redaction.rs`）で、この行をどう扱うかを決める。
3. **入口の門**:
   - 段 1 のモード（`s1.rs` の判定: 配布形は印 `s1.mode`、開発・検証は `GSE_S1_MODE=1`）で、かつ表があり SHA-256 が合うときだけ動く。
   - それ以外では、窓も作らず tap も張らない。fail-closed で、出せない理由を日ごとの行に書く。
4. **状態の純関数（決定性）**:
   - ライブの契約と再生の契約に分ける（ADR-051 D5）。状態は `f(打鍵の時刻の列, ポインタの入力, 種, t)` で決め、固定の時間刻みで進める。再生ではポインタの口に `pointer_bin` からの近似を入れる。PR 1 の入力は打鍵だけで、ポインタの口は空でよい。
   - 描画の回数は状態に影響させない。
   - 同じ入力から同じ状態がバイト単位で出ることを、性質のテストで縛る。種を変えれば変わることも確かめる（陰性の対照）。
   - 試作の `handmark_wind.rs` を写して、この形に直す。
5. **背景の層（macOS・打鍵だけ）**:
   - 試作の `handmark_stage_spike.rs` と `HandmarkStage.tsx` の描画を写す。
   - 窓は、状態を描くだけにする。
   - `lib.rs` の受信ループに、押下の時刻を渡す 1 か所を足す。試作は `event.is_press && !recording::is_paused()` のときに渡していた。
6. **切る／戻す**: トレイの項目。その日のうちだけ続き、翌日は割付に戻る。時刻を日ごとの行に書く。
7. **記録の検査**:
   - 試作の `handmark_stage_guard.rs` の考え方（語の検査と陽性対照）を写す。
   - 手跡が動いても、日ごとの行以外の行が 1 行も増えないことをテストする。
   - ADR-050 D3 の表のうち、打鍵だけの PR 1 に当たる行を先に入れる。

大きすぎると分かったら、1a（OS 非依存: 1〜4・7）と 1b（5・6・配線）に割り、続けて出す（判断 6b）。

## 入れないもの（PR 1 では）

帯（PR 2）・カーソルとクリック（PR 3）・ホイール（PR 5）・「背景を見る」（PR 6）・日の問いの項目（PR 7）。小面と計測の仕掛けは、どの PR にも入れない。

## 試作の在り処

- worktree `/Users/johnd/GSE-prototype-handmark-stage`（枝 `spike/handmark-stage`・351f94e5）。読むだけで、rebase しない。
- 記録: `.steering/20261016-handmark-stage-spike/`・`20261021-handmark-stage-pointer/`・`20261030-handmark-edge-strip-impl/`（その枝の中）。
- 衝突の見込み: `lib.rs`（main 側 +1413 行）と `tray.rs`。main の `tray.rs` には、招待の項目の差し込み（`menu.insert(item, 2)`）と `request_quit` がある。配線は main に合わせて書き直す。

## 守ること

- 規約: `architecture-rules`・`rust-standards`・`typescript-standards`・`data-privacy`（新しい行種）。OS の API は `analysis/` に置かない。
- UI を変えるので、画面を見るまで完了にしない（memory: ui-changes-need-eyes）。研究者本人の gse-next（`/Users/johnd/GSE-S1-self/S1_実施用_macOS/gse-next.app`）が動いている間は、同じ名前のプロセスに AX で押さない（memory: jxa-same-name-process-ax-crosstalk）。
- 本人の段 1 の記録（O1・段 1 の NDJSON）を開かない。Codex に送らない。
- 完了時は code-reviewer・security-checker と /cross-review（Codex を加える）。
- この Mac の空きは 2026-11-08 に約 9.5 GiB で、self-hosted の macOS の検査が止まる 8 GiB に近い。CI を起こす前に空きを確かめる。
- push・PR は研究者に確かめてから。

## このタスクで決めること（研究者に 1 問ずつ）

1. 表の置き場所と形式。研究者が表を作る道具を、この PR に入れるか。
2. 日ごとの行の名前と、区間の削除での扱い。
3. 1a と 1b に割るか。
4. 日ごとの行を書き出す時点（起動・終了・日付の変わり目・一定の間隔）と、同じ日の行が複数あるときの合わせ方。落ちても失われないこと、二重に数えないことをテストで縛る（ADR-051 D4）。
5. 入口の門を検め直す契機（起動・日付の変わり目・一定の間隔）。表を消した後に窓と tap が壊れることをテストで縛る（ADR-051 D5）。
6. 同じ日に再起動したときの、切った状態の保ち方（ADR-051 D2）。
