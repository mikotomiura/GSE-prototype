# §3: overlay の透明窓がクリックを奪わないか（非侵襲的 `WindowFromPoint` hit-test）

## 対象ビルド

`src-tauri/target/release/gse-next.exe`（commit `22538cc`、`o1.mode` あり = O1 モード）。
2026-09-09 14:35 JST（`gse-app.log` 上は `2026-09-09T05:35:29Z`）に起動、PID 31540。

## 手法（`design.md` の GUI 操作の自動化判断どおり）

実クリックは送らない。`WindowFromPoint`（Win32 API、PowerShell + Add-Type C# で直接呼ぶ）で
「その画面座標のクリックがどのウィンドウに届くか」を非侵襲的に判定する。
`debug_overlay_window_state`（Tauri コマンド）は `GSE_DEBUG=1` に加えてフロント側の
`VITE_GSE_DEBUG=1`（ビルド時フラグ）二重ゲート下にあり、GUI（devtools コンソール）を
操作する手段がこのセッションに無いため直接は呼べなかった。★ 代わりに `EnumWindows` +
`GetWindowRect` + `GetWindowLong(GWL_EXSTYLE)` で同じ情報（位置・サイズ・可視性・
`WS_EX_TRANSPARENT`/`WS_EX_LAYERED`/`WS_EX_TOPMOST`）を外部から読み取った
（読み取り専用、窓は一切変更していない）。

## 観測1: `gse-next.exe` (PID 31540) の全ウィンドウ

```
hwnd=198684 title='GSE Overlay' class='Tauri Window' visible=False ex_topmost=True
             rect=(234,234)-(1050,843) ex_transparent=False ex_layered=False
hwnd=197824 title='gse-next'   class='Tauri Window' visible=True  ex_topmost=False
             rect=(156,156)-(972,795)
（他: global_hotkey_app / tray_icon_app / Tao Thread Event Target / IME 系 は非表示のヘルパー窓）
```

★ overlay 窓（`GSE Overlay`）は idle（O1 モードで介入 OFF・プローブ/Nudge 非表示）状態では
`visible=False`。`lib.rs:4669` の「窓自体は無条件に事前生成される・`visible(false)`」という
コメントと一致。

## 観測2: 四隅+中央の `WindowFromPoint`（画面 1920x1080、idle 状態のまま）

| 座標 | 返ったウィンドウ | プロセス |
|---|---|---|
| 左上 (5,5) | VS Code | Code |
| 右上 (1915,5) | ChatGPT (デスクトップアプリ) | ChatGPT |
| 左下 (5,1075) | タスクバー (`Shell_TrayWnd`) | explorer |
| 右下 (1915,1075) | タスクバー (`Shell_TrayWnd`) | explorer |
| 中央 (960,540) | ChatGPT (デスクトップアプリ) | ChatGPT |

★★ **5 箇所すべてで `gse-next.exe`（PID 31540）のウィンドウは一切返らなかった。**
idle 状態では overlay がクリックを奪っていないことを実測で確認した。

## ⚠️ 未検証: 表示状態（Nudge/プローブ表示中）でのクリック透過

`force_nudge` / `debug_force_probe` は Tauri コマンドで、GUI（フロントの devtools か
被験者と同じ操作）からしか起動できない。このセッションには Tauri ネイティブウィンドウ
（WebView2）を操作する手段がなく（`claude-in-chrome` は Chrome ブラウザ専用でネイティブ
アプリの webview には使えない）、**表示状態での hit-test は実施できなかった**。

O1 モードでは `INTERVENTION_ENABLED.store(false, ...)`（`lib.rs:3241`）により overlay は
そもそも `show()` されないため、O1 の通常運用中にこの状態には到達しない。ただし
`Overlay.tsx` のコメント（#11461 対策として「実寸縮小」方式を採用）が実際に機能しているかは
本セッションでは確認できていない — G1 モード等、実際に Nudge/プローブを表示できる文脈での
GUI 実機確認が別途必要。

## まとめ

| 状態 | 検証 | 結果 |
|---|---|---|
| idle（overlay 非表示） | 四隅+中央 hit-test | ✅ 5/5 箇所で奪っていない |
| 表示中（Nudge/プローブ） | — | ⚠️ 未検証（GUI 操作手段なし） |

→ 3 件中 1 件実測（idle 状態は確認済み）、表示状態は未検証として残る。
