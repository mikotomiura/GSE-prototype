# 引き継ぎ — 「すぐ止める」を押すと約 1 秒後に勝手に再開が記録される件を調べる（最優先）

> 使用済み（2026-10-31）: `.steering/20261031-pause-auto-resume/`（枝 `fix/pause-auto-resume`・push 済み）。本体に勝手に再開する欠陥は無く、前面にない窓の 1 回目のクリックと押すたびに向きを変えるボタンの組み合わせだった。直してある。

> 作成: 2026-10-30（CPU の内訳を測るタスク `.steering/20261030-gse-cpu-profile/`・枝 `chore/gse-cpu-profile`・worktree `/Users/johnd/GSE-prototype-cpu-profile` の判断 4）。
> このメモを一次資料にしない。時刻・行・挙動は、ログとコードで確かめ直す。一次は上のタスクの `results.md` の 4。

## 0 始め方

1. `/start-task`（タスク名の案: `pause-auto-resume`）→ `/fix-bug`。返答・記録・AskUserQuestion は日本語で。記号を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。
2. 版は空回りの修正の入った `fix/logger-flush-busy-loop`（140b376b）か、その PR が merge 済みなら main から worktree を切る。
3. O1 の収集アプリ（`~/Desktop/O1_実施用_macOS/gse-next.app`・研究者の Mac で記録中）は止めない・押さない。開発版は識別子を変えて並べて起動する（CPU のタスクの `probe/run-dev.sh` を写す）。
4. NDJSON の生ログとキーストロークの内容は外部の LLM に送らない。行の種類と時刻だけを数える。
5. G-GEAR の処理の状況を研究者に聞いてから PR を出す（処理中は push まで）。

## 1 見えたこと（開発版・非 O1・2026-10-30 UTC）

- 研究者が実際のマウスで開発版のダッシュボードの「すぐ止める」を押すたびに、`recording_pause` の `paused:true` の約 1 秒後（0.8〜2.5 秒）に `paused:false` が書かれた（5 回とも。研究者は「すぐ止める」だけを押し、再開は押していない）。画面は「記録を再開する」（止めている表示）のまま、`feat` などの行も書かれ続けた。その前の 14:17〜14:18 にも同じ組が 2 つ。
- Claude が AX（System Events の AXPress）で押した 3 回は、画面の文字だけが変わり、止める行も再開の行も書かれなかった。
- 研究者が「押した・再開に変わった」と答えた別の 2 回でも、行は書かれていなかった。

## 2 コードで分かっていること（確かめ直す）

- フロントで `set_recording_paused` を呼ぶのは `src/components/RecordingControls.tsx` の `togglePause` だけ。送る値は画面が持つ状態の逆（`!status.paused`）で、押した後に `get_recording_status` で読み直す。
- バックエンドは `lib.rs` の `set_recording_paused` だけ。`recording::set_paused` の直前の値と違うときだけ `LogEntry::RecordingPause` を送り、送れなければ警告を出す（警告は出ていない）。
- logger はグローバルのフラグではなく、ストリームの `RecordingPause` の行で止まる・再開する（`logger.rs` の書き出しの入口のコメント）。画面（グローバルのフラグ）とファイル（ストリーム）がずれうる作り。
- `RecordingControls` は主窓のダッシュボードにだけある（`Dashboard.tsx:281`・`App.tsx:1032`）。overlay の窓は `<Overlay>` だけを描く（`App.tsx:420-424`）ので、overlay から `togglePause` は呼べない（cross-review で訂正）。
- 再開の行は、フロントからもう一度 `set_recording_paused(false)` が届いたときにしか出ない（`recording::set_paused` を呼ぶのは `lib.rs:2028` だけ）。直前の値が同じなら行も警告も出ない（`lib.rs:2029`）。AX で押して行が出なかったのは、これで説明がつく見込み。
- `lib.rs:2018-2019` のコメント（止める行は `set_paused` の前に送る）と実装（後で送る）が食い違っている。

## 2.5 同じ夜に O1 で起きたこと（results.md の 8）

- 14:58〜15:09 UTC、研究者の O1 の収集アプリが一時停止中（メニューバー「○」）で、v0.1.40 の空回りで 1 コアを使っていた。13:55 には「● 計測中」だった。研究者が再開して戻った。
- 研究者が開発版のつもりで O1 の「すぐ止める」を押していた可能性がある。開発版で「押した・再開に変わった」のに行が無かった 2 回（13:19 ごろ・13:51 ごろ）と、開発版の「止める→約 1 秒後に再開」の組が、2 つのアプリの窓を行き来した押下で説明できるかを、最初に確かめる。O1 の NDJSON の `recording_pause` の時刻を読むなら、先に研究者の許可を取る（行の種類と時刻だけ・外に送らない）。

## 3 調べること

1. どこから `paused:false` が送られているか（どの窓の `togglePause` か・ほかの道があるか）。tracing を一時的に足すなら、開発版を動かしている間は Rust を直さない（`tauri dev` が作り直す）。
2. AX で押すと画面だけ変わって行が書かれない理由（直前の値が同じと判断されたのか、別の窓の状態か）。
3. **O1 の配布版（v0.1.40）でも起きるか**。被験者が止めても記録が続くなら、同意文書 §4 の約束が破れる。研究者の O1 のアプリで試さない。配る zip から作ったアプリを識別子を変えて起動して確かめる（Windows も別に要る）。起きるなら、配った版の扱いとすでに集めたデータの扱いを研究者に聞く（削除保証台帳 `docs/o1-deletion-ledger.md` に関わりうる）。
4. 直したら、一時停止中の CPU を測る（CPU のタスクで測れなかったもの・`results.md` の 7 の手順）。

## 4 関わる記録

- `/Users/johnd/GSE-prototype-cpu-profile/.steering/20261030-gse-cpu-profile/results.md`（4・7）・`decisions.md`（判断 4）
- `docs/o1-distribution-tag.md` の v0.1.40 の注意
