# 引き継ぎ — G-GEAR の処理が済んだら、空回りと「すぐ止める」の修正を main に入れ、O1 の v0.1.41 を切る

> 作成: 2026-10-31（`.steering/20261031-trim-ui-polling/` の後・研究者の指示「G-GEAR の方での処理が終わったら手を打てれる感じにして、push する」）。
> このメモを一次資料にしない。枝の中身と手順は、git と各タスクの記録で確かめ直す。

## 0 なぜやるか（1 行）

配布中の O1 v0.1.40 は、記録を止めている間に記録のスレッドが 1 コアの約 98% を使い続ける（研究者の O1 で 2026-10-30 に実測）。直したコードは枝にあるが、配るまでは参加者の手元で起き続ける。

## 1 始める条件

1. G-GEAR の長い処理が終わったかを研究者に聞く（memory `feedback-push-only-no-pr-during-runs`。self-hosted CI と重なるので、処理中は PR を出さない）。
2. 返答・記録・AskUserQuestion は日本語で。記号を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。
3. O1 の収集アプリ（`~/Desktop/O1_実施用_macOS/gse-next.app`）は止めない・押さない。開発版や配布物の確かめは識別子を変え、HOME を一時フォルダにする（`.steering/20261031-pause-status-row/probe/run-dev-o1.sh`）。
4. NDJSON の生ログとキーストロークの内容は外部の LLM に送らない。

## 2 枝の並び（2026-10-31 時点・3 本とも origin/main 5d7c53be の真上で、衝突なく入ることを `git merge-tree` で確かめた）

```
main 5d7c53be
 └ fix/logger-flush-busy-loop   140b376b  空回りの修正（4 コミット）       ← v0.1.41 に要る
    ├ chore/gse-cpu-profile      a2e763f2  CPU の内訳の記録（docs だけ）     ← 任意
    └ fix/pause-auto-resume      3aa0cc4b  「すぐ止める」と止めている間の表示 ← v0.1.41 に要る
       └ refactor/trim-ui-polling（この引き継ぎを入れたコミットが先頭）  取得の削り・CPU の記録 ← 任意（入れて害はない）
```

- 先に `git fetch` し、main が動いていたら各枝が今も衝突なく入るかを確かめ直す（`git merge-tree --write-tree origin/main origin/<枝>`）。
- PR の本文の下書き: `.steering/_handoff/o1-v0141-pr-bodies/`（pr1〜pr4。数字は出す順）。末尾の attribution はその時のセッションのものに差し替える。

## 3 PR を出す順（git-workflow ルール 6・止まる条件もそのまま守る）

1. `fix/logger-flush-busy-loop` → `gh pr create --base main --head fix/logger-flush-busy-loop --body-file .steering/_handoff/o1-v0141-pr-bodies/pr1-logger-flush.md`。CI 緑で merge。main の CI の発火も確かめる。
2. `fix/pause-auto-resume` → base main で PR（pr2）。1 の merge の後なら、差分はこの枝の 3 コミットだけになる。CI 緑で merge。
3. 任意: `refactor/trim-ui-polling`（pr3）・`chore/gse-cpu-profile`（pr4・docs だけ）。研究者に出すかを聞く。3 は 2 の上にあるので 2 の後。
- 研究者が「PR まで」と言ったら merge しない（その指示が常に優先）。

## 4 v0.1.41 を切る（研究者の承認の後）

1. 版を 0.1.40 → 0.1.41 にする: `package.json`・`src-tauri/tauri.conf.json`・`src-tauri/Cargo.toml`（と `Cargo.lock` の gse-next の行）。作業の枝を切り、PR で入れる。
2. 注釈付きタグ `v0.1.41` を、研究者の承認のうえで push する。CI の `build-macos` / `build-windows` / `release` が緑かを確かめる。
3. 配布物を作る: `bash make-common-app-zip.sh --mode o1 --tag v0.1.41 --config "$REPO/Form_O1/o1_submit.json"`（`experiments/20260801-controlled-friction-task/`）。スクリプトの自己検査に加え、別の場所に展開して検算する（v0.1.40 の節と同じ: 版の番号・codesign・Release の資産との byte 一致・`o1.mode`）。
4. 実機の確かめ（配る zip から作ったアプリ・識別子を変えて・HOME を一時フォルダに・研究者の O1 と並べる）。手順の一次は `.steering/20261030-gse-cpu-profile/results.md` の 7（chore/gse-cpu-profile の枝にある）。要点:
   - 記録中・無操作の CPU を 60 秒 × 2。
   - 実際のマウスで「すぐ止める」を 1 回。`recording_pause` の `paused:true` が 1 行、その後 2 分以上、再開の行もデータの行も無い（画面ではなく行で確かめる）。止めている間は宣言の行が「止めています」になり、「選ぶ・変える」が押せない。
   - 一時停止中の CPU を 60 秒 × 2。本体が記録中と同じか低い（v0.1.40 の欠陥なら 1 コア近く）。
   - 前面にない窓で「記録を再開する」を 1 回 → 再開しない。前面で押す → `paused:false` の行の後にデータの行が戻る。
   - Windows でも同じ（`.steering/_handoff/next-session-pause-ui-windows.md`）。Mac の確かめは代わりにならない。
5. `docs/o1-distribution-tag.md` に v0.1.41 の節を書く（タグ・コミット・CI の run・zip の SHA-256・確かめたこと・未実施のこと）。v0.1.40 の注意の末尾に「直した版は v0.1.41」を足す。
6. Drive の差し替えと参加者への知らせは研究者が行う。

## 5 決まっていること・決めること

- 同意文書の §2 の文面（「記録中はいつも『記録中 · 作業の種類: ○○』と出ています」）は今は変えない（2026-10-31・研究者）。止めている間は「止めています」と出るが、約束は破らない側のずれ。
- 参加者向けの README 2 本（`dist-readme-{macos,windows}-o1.txt`）の再開の説明は、`fix/pause-auto-resume` で新しい画面に合わせ済み。
- v0.1.41 に `refactor/trim-ui-polling` を含めるかは研究者が決める（効きは小さく、害もない。通常運用の介入の振る舞いは変えていない）。
- schema（`schema_dto.rs`・`schema/current.json`）は 3 本とも変えていない。gse-dataset の同期は要らない見込み（PR の前に `git diff --stat origin/main -- src-tauri/schema src-tauri/src/schema_dto.rs` で確かめる）。

## 6 残っている候補（v0.1.41 とは別）

- O1 では経過を分単位にして、毎秒の描き替えを減らす（約 1 ポイントの見込み・参加者の画面が変わる・`.steering/20261031-trim-ui-polling/results.md` 6）。
- 通常運用で窓を最小化すると、介入の判定が 1 秒に 1 回に遅くなる（既存・WebKit のタイマーの間引き・同 results.md 3）。判定の時計を Rust へ移す案と関わる。
- 打鍵のフックが止まっている間も、宣言の行が「記録中」と出る（既存・`.steering/20261031-pause-status-row/decisions.md` 判断 1）。
- 13:19 ごろ・13:51 ごろの「押したのに行が無い」件は説明がついていない（`.steering/20261031-pause-auto-resume/results.md` の 2・3・6）。
- 非 O1 のトレイは一時停止を表示しない（設計どおり）。
