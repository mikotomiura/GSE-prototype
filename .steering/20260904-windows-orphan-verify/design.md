# design

## アプローチ

### ブランチ判断（★ 引き継ぎからの逸脱）

引き継ぎは `git checkout main` を指示するが、現在のワーキングツリーには
このタスクと無関係な未コミット変更が 25 件ある（別作業のスライド/pptx 等）。
ブランチを切り替えると意図せずそれらを巻き込む/コンフリクトのリスクがある。

→ ★ **現ブランチ (`feat/resumption-outcome-arbitration`) の HEAD のまま検証する。**
`git merge-base` で確認: origin/main に対して 65 コミット先行・2 コミット遅れ（遅れの 2 件は
`docs/steering` のみで `o1.rs` / `hook_windows.rs` / `reconcile.rs` に変更なしを grep で確認済み）。
→ 孤児回収 (`close_orphaned_sessions`)・`request_reinstall` 3 回上限・`LOCK_STALE_AFTER` は
現 HEAD に揃っている。

### GUI 操作の自動化判断

引き継ぎは §1-A（トレイから正常終了）を「トレイクリック」前提で書いているが、
`lib.rs:4796-4805` を読むと、正常終了に入る経路は `WindowEvent::CloseRequested`（main 窓の ×）
でも同じ `shutdown_and_exit` に入る。★ **PowerShell の `Process.CloseMainWindow()`（WM_CLOSE 送信）
で GUI クリックなしに同じ経路を通せる**ので、これを A の実装とする。

§1-B（強制終了）は `taskkill /F /IM gse-next.exe`（Task Manager の「タスクの終了」と同じ
TerminateProcess 系）で GUI 不要。

§3（overlay クリック透過）は実際のマウスクリックを送らず、Win32 `WindowFromPoint` による
非侵襲的 hit-test で「その座標のクリックがどのウィンドウに届くか」を判定する
（実クリックはデスクトップ上の無関係なウィンドウを誤操作するリスクがあるため避ける）。

§1-C（OS 再起動）だけは実機の再起動そのものが要る。ユーザーに確認し「今すぐ実施」の回答を得た。
→ `shutdown /r /t 60 /c "..."` で 60 秒の遅延・キャンセル可能な形で実行し、次回ログイン後の
**新セッション**で `gse-app.log` / NDJSON を確認する（本セッションはここで終了する）。

### ビルド

`src-tauri/target/release/gse-next.exe` を現 HEAD で再ビルドし、コミットハッシュを記録する。
実行はビルド場所 (`target/release/`) から直接行う（tauri のリソース解決パスを壊さないため、
別フォルダへコピーしない）。`o1.mode` を `target/release/` に置いて O1 モードにする。

## テスト戦略

- `cargo test --features package --workspace`（回帰確認）
- §1 A/B/C を実機で 1 回ずつ（正常/壊れ/べき等の 3 状態も追加で試す）
- §2 は 1 分スモーク → 8 時間本番 1 本（対照は回さない）
- §3 は起動直後・放置後で hit-test

## 変更対象

コード変更なし（検証タスク）。`.steering/` の記録と `experiments/20260903-o1-runtime-cost/`
の結果ファイルのみ追加。
