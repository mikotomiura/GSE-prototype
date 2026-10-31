# 引き継ぎ — 「すぐ止める」まわりの画面の変更を Windows の実機で確かめる

> 作成: 2026-10-31（`.steering/20261031-pause-auto-resume/`・枝 `fix/pause-auto-resume`・worktree `/Users/johnd/GSE-prototype-pause-resume` の判断 7）。
> このメモを一次資料にしない。振る舞いはコードと results.md で確かめ直す。

## 0 始め方

1. `/start-task` → 確かめるだけなら記録だけ、直すなら `/fix-bug`。返答・記録・AskUserQuestion は日本語で。決めることは推奨と理由を添えて AskUserQuestion で聞く。
2. 版は `fix/pause-auto-resume` が merge 済みなら main、まだなら枝そのもの。Windows の機械では収集だけを頼み、直すのは文脈のある側で行う（memory `windows-agent-collection-only`）。
3. O1 の収集アプリは止めない・押さない。開発版は識別子を変えて並べる。NDJSON の生ログとキーストロークの内容は外部の LLM に送らない（行の種類と時刻だけを数える）。

## 1 macOS で入れた変更（Windows では確かめていない）

- 止めると再開を別のボタンにした（`RecordingControls.tsx`）。止めた後は「止めています」（押せない）、「記録を再開する」は下の行。
- 窓を前に出すクリックを捨てる見張り（`src/firstMouseGuard.ts`）を、自己ラベル・G1 の「送信する」・「記録を再開する」に付けた。Tauri の焦点の知らせの時刻と押し下げの時刻が 300ms 未満なら捨てる（判断を 150ms 遅らせる）。OS を問わず動く。
- 主窓の `acceptFirstMouse: true`（`tauri.conf.json`）は macOS だけで効く。Windows はもともと前面にない窓への 1 回目のクリックがボタンに届く。
- 参加者向けの README（`dist-readme-windows-o1.txt`）の再開の説明。

## 2 確かめること（Windows）

1. 前面にない窓で「すぐ止める」を 1 回 → 止める行が 1 つ、その後データの行が書かれない。
2. 「止めています」をもう一度押す → 行なし。
3. 前面にない窓で「記録を再開する」を 1 回 → 再開しない（見張り）。前面のまま押す → 再開する。
4. 自己ラベル（非 O1）と G1 の「送信する」も同じ（前面にない窓の 1 回目は捨てる・前面なら通る）。Windows で Tauri の焦点の知らせが押し下げのどれだけ前後に届くかで、見張りが効くかが決まる（macOS では約 1ms 後）。効かない・効きすぎるなら、時刻を測る一時的な計装を入れる（macOS では Rust のコマンドで tracing に出した・判断 6）。
5. 一時停止中の CPU（CPU のタスクの results.md の 7 の 7 番目の手順）。

## 3 関わる記録

- `.steering/20261031-pause-auto-resume/results.md`（3・7・8・9）・`decisions.md`（判断 5〜7）
- `docs/o1-distribution-tag.md`（v0.1.40 の注意・次の版の実機確認）
