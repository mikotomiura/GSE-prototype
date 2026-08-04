@echo off
rem ★ chcp は日本語より前に置く（Phase1 の launcher 文字化けの再発防止）
chcp 65001 > nul
setlocal

rem G1 統制タスク実験 — Windows 用 launcher（1 ブロック 1 回・ダブルクリックで起動する）
rem
rem ★ なぜ launcher が要るか（preregistration.md §5.4 / protocol.md §1.1）
rem   GSE_DISABLE_PROBES=1 を立てずに起動すると、アプリ内プローブが 5 分ブロックあたり
rem   57%% の確率で発火する。§2.6 は「アプリ内プローブを使わない」と凍結しており、
rem   §3.6 はブロックの事後除外を禁じている = 汚染された回は後から落とせない。
rem   1 ブロック = 1 セッションで 10 回起動するので、手打ちだと必ずどこかで抜ける。
rem
rem ★ 実行ファイル名は gse-next.exe（tauri.conf.json の productName）。GSE.exe ではない。
rem   v0.1.22 の Release で配っているのは portable の gse-next.exe（インストーラは無い）。
rem   このバッチと同じフォルダに gse-next.exe を置いて使う。

echo === G1 launcher (Windows) ===

rem 1. 既存インスタンスを確実に終了させる
rem    ⚠️ ★ 終了したことを必ず確認する（/cross-review 2026-08-03 の両者一致 HIGH）。
rem       taskkill を撃ちっぱなしにして固定時間待つだけだと、応答しない場合に
rem       旧プロセスが残ったまま新プロセスが起動し、(a) 打鍵が 2 本の NDJSON に混ざる
rem       (b) 環境変数が効かない という、まさにこの launcher が防ぎたい事故が起きる。
call :ensure_stopped
if errorlevel 1 (
  echo   [中断] gse-next.exe を終了できませんでした。
  echo          手動で終了してから、もう一度このファイルを実行してください。
  echo          このまま起動すると環境変数が効かず、プローブが発火する恐れがあります。
  pause
  exit /b 1
)

rem 2. kill switch 付きで起動する
if not exist "%~dp0gse-next.exe" (
  echo   [中断] このフォルダに gse-next.exe がありません。
  echo          v0.1.22 の Release から gse-next.exe をこのフォルダに置いてください。
  pause
  exit /b 1
)
echo [2/3] GSE_DISABLE_PROBES=1 で gse-next.exe を起動します...
set GSE_DISABLE_PROBES=1
start "" "%~dp0gse-next.exe"

echo [3/3] 起動しました。ブロックを始める前に確認してください:
echo   - 週の選択が「第1週 (blind 較正)」であること（既定のまま。触っていなければ OK）
echo   - ブロックが終わったら「30 秒チェック」を行うこと（protocol.md 6.1）
echo       findstr /C:"probe_assignment" /C:"probe_triggered" /C:"realtime_label" ^
echo         "%%USERPROFILE%%\Documents\GSE-sessions\<そのブロック>.ndjson"
echo     何も表示されなければ OK。1 行でも出たらそのブロックは使えない
echo   ※ 「ログに probe scheduler DISABLED が出ること」は確認手段にならない
echo     （release ビルドは windows_subsystem="windows" でコンソールを持たない）
echo   - 記入パッド (writing-pad.html) を拡張機能なしのプロファイルで全画面表示していること
echo   - ★ 自己マーカー hotkey (Ctrl+Shift+Alt+M) を押さないこと
echo.
pause
endlocal
exit /b 0

rem --------------------------------------------------------------------
rem gse-next.exe が動いていなければ errorlevel 0、動いていれば 1 を返す
:is_stopped
tasklist /FI "IMAGENAME eq gse-next.exe" 2>nul | find /I "gse-next.exe" >nul
if errorlevel 1 exit /b 0
exit /b 1

rem 終了できたら errorlevel 0、できなければ 1（呼び出し側が中断する）
:ensure_stopped
call :is_stopped
if not errorlevel 1 (
  echo [1/3] 起動中の gse-next.exe はありません。
  exit /b 0
)
echo [1/3] 起動中の gse-next.exe を終了します...
taskkill /IM gse-next.exe >nul 2>&1
timeout /t 3 /nobreak >nul
call :is_stopped
if not errorlevel 1 exit /b 0
echo   応答しないため強制終了します...
taskkill /F /IM gse-next.exe >nul 2>&1
timeout /t 2 /nobreak >nul
call :is_stopped
if not errorlevel 1 exit /b 0
exit /b 1
