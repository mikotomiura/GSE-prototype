## 背景

「すぐ止める」を押すと約 1 秒後に勝手に再開が記録される、という報告を調べた。本体に勝手に再開する欠陥は無く、次の 2 つの組み合わせだった。

- macOS では、前面にない窓への 1 回目のクリックがボタンに届かない（Tauri の既定 `acceptFirstMouse=false`）。
- 1 つのボタンが押すたびに向きを変える作りで、押し直しや確かめの押下が再開になっていた。

## 変更点

- 主窓に `acceptFirstMouse: true`（回帰テスト `src-tauri/tests/main_window_accept_first_mouse.rs`）。
- 「すぐ止める」と「記録を再開する」を別のボタンに分けた。止めた後は押せない「止めています」に変わる。
- 窓を前に出すクリックを捨てる見張り（`src/firstMouseGuard.ts`）を、「記録を再開する」・自己ラベル・G1 の「送信する」に付けた。「すぐ止める」には付けない（1 回で止まる約束を守る）。
- O1 で止めている間は、宣言の行を「止めています · 作業の種類」にし、「選ぶ・変える」を押せなくした（backend はもともと止めている間の宣言を断る）。
- 参加者向けの README 2 本の再開の説明を新しい画面に合わせた。`logger.rs` と `lib.rs` のコメントを実装に合わせた。

## 検証

- 計装した開発版と研究者の実マウスで原因を再現し、直した後に Claude が pid から合成クリックで確かめた（前面にない窓での「すぐ止める」は 1 回で止まる・止めていた間の行は 0）。
- O1 の形の開発版で、止めている間の表示とボタンを AX と画面で確かめた。
- `cargo fmt --check`・`clippy -D warnings`・`cargo test --workspace`（1021 件）・`gse-replay --snapshot minimal`・`tsc` 緑。

## レビュー

code-reviewer（HIGH なし）・/cross-review（Codex）の指摘に対応済み（`.steering/20261031-pause-auto-resume/decisions.md` 判断 5〜7・`.steering/20261031-pause-status-row/decisions.md` 判断 1）。

## 残り

- Windows の実機での確かめ（`.steering/_handoff/next-session-pause-ui-windows.md`）。G1 の「送信する」の見張りは実機で確かめていない。

Refs: .steering/20261031-pause-auto-resume/ .steering/20261031-pause-status-row/

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01BUBYRxTQSivZDKJTppgVtQ
