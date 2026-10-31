# 設計

## アプローチ

1. 調べ（results.md の 1・2）: 前回のセッションの記録と O1 の `recording_pause` の行・`gse-app.log` の tray state を突き合わせる。
2. 計装した開発版で、研究者が実マウスで押して送り手を確かめる（results.md の 3）。Claude は AX で押さない。
3. 原因（1 回目のクリックが届かない・1 つのボタンが向きを変える）を直す（判断 2・3）。

## 変更対象

- `src-tauri/tauri.conf.json`: 主窓に `"acceptFirstMouse": true`。
- `src/components/RecordingControls.tsx`: `togglePause` を `setPaused(next)` に変え、止めると再開を別のボタンにする。
- `src-tauri/src/lib.rs`: `set_recording_paused` のコメントを実装に合わせる（振る舞いは変えない）。
- `experiments/20260801-controlled-friction-task/dist-readme-{macos,windows}-o1.txt`: 再開の説明。

## テスト戦略

- 回帰テスト `src-tauri/tests/main_window_accept_first_mouse.rs`（設定ファイルを読む・OS を問わず走る）。直す前に赤を確かめた。
- 画面は自動テストが無いので、開発版で研究者が実マウスで確かめた（results.md の 3）。`npx tsc --noEmit`。
- 既存の `cargo test --workspace`・clippy・fmt・`gse-replay` のスナップショット。
