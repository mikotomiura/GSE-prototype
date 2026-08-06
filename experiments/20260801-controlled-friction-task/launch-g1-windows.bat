@echo off
rem ★ chcp は日本語より前に置く（Phase1 の launcher 文字化けの再発防止）
chcp 65001 > nul
setlocal

rem G1 統制タスク実験 — Windows 用 launcher（1 ブロック 1 回・ダブルクリックで起動する）
rem
rem ★★ なぜ launcher が要るか（2026-08-07 に理由が 1 つ減った。★ 残る理由が本体である）
rem
rem   1. ⚠️★ **旧プロセスを確実に終わらせる**（★ これが今の主目的）
rem      前ブロックの gse-next.exe が残ったまま起動すると、打鍵が 2 本の NDJSON に割れる。
rem      アプリ側にも二重起動の検知はあるが **警告を出すだけで終了させない**
rem      （lib.rs の spawn_duplicate_instance_check → "second-instance-blocked" イベント）。
rem      ★ 終了できたことを確認するまで起動しない（/cross-review 2026-08-03 の両者一致 HIGH）。
rem
rem   2. 起動前チェックリストを毎回目に入れる（下の [3/3]）。
rem
rem   3. GSE_DISABLE_PROBES=1 を立てる
rem      → ⚠️★ **v0.1.23 以降は冗長**。配布フォルダの `g1.mode` マーカーがあるだけで
rem        プローブスケジューラは起動しない（lib.rs: disabled_by_env || disabled_by_g1）。
rem        ★ それでも残すのは **2 本目の引き金として無害**であり、マーカーの置き忘れ
rem        （フォルダ構成を崩した配布）を 1 段だけ拾えるためである。
rem      ⚠️ v0.1.22 以前のバイナリには **マーカー経路が無い**ので、その場合はこの行が唯一の防波堤。
rem
rem ★ 実行ファイル名は gse-next.exe（tauri.conf.json の productName）。GSE.exe ではない。
rem   Windows で配っているのは portable の gse-next.exe（インストーラは無い）。
rem   ⚠️ ★ このバッチと同じフォルダに **gse-next.exe / gse-submit.exe / pubkey.txt /
rem   g1.mode / g1-submit.json** を置く（★ 自動送信はこの 5 つが揃って初めて成立する）。

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
  echo          研究者から渡された配布フォルダの中身をそのまま使ってください。
  pause
  exit /b 1
)
rem ⚠️★ 自動送信に要るファイルの不足を **起動前に**知らせる（止めはしない）。
rem   ★ 止めない理由: 記録そのものは取れるからである。⚠️ ただし黙ってもいけない
rem     （足りないと `.age` が端末に貯まるだけで、研究者に届かない）。
if not exist "%~dp0gse-submit.exe" echo   [注意] gse-submit.exe がありません（自動送信ができません）。
if not exist "%~dp0pubkey.txt"     echo   [注意] pubkey.txt がありません（暗号化ができません）。
if not exist "%~dp0g1.mode"        echo   [注意] g1.mode がありません（G1 モードになりません）。
if not exist "%~dp0g1-submit.json" echo   [注意] g1-submit.json がありません（送信先が未設定です）。
echo [2/3] gse-next.exe を起動します...
rem ★ マーカー（g1.mode）が主。この env は 2 本目の引き金（上のコメント 3 を参照）。
set GSE_DISABLE_PROBES=1
start "" "%~dp0gse-next.exe"

echo [3/3] 起動しました。ブロックを始める前に確認してください:
echo   - ★ 参加者 ID が入っていること（研究者から渡された P0xx。入っていないと開始できません）
echo   - ★ 前のブロックの「送信しますか？」が残っていたら、先に「送信する」を押すこと
echo     （押すまで送られません。押さなくても記録は端末に残ります）
echo   - 週の選択が「第1週 (blind 較正)」であること（既定のまま。触っていなければ OK）
echo   - ブロックが終わったら「30 秒チェック」を行うこと（protocol.md 6.1）
echo       findstr /C:"probe_assignment" /C:"probe_triggered" /C:"realtime_label" そのブロックの.ndjson
echo       （場所は %%USERPROFILE%%\Documents\GSE-sessions\ ）
echo     何も表示されなければ OK。1 行でも出たらそのブロックは使えない
echo   ※ 「ログに probe scheduler DISABLED が出ること」は確認手段にならない
echo     （release ビルドは windows_subsystem="windows" でコンソールを持たない）
echo   - ★ そのブロックの blockNN.html を「1 つだけ」開いていること
echo     （記入欄はページに内蔵されている。protocol.md 1.2 / preregistration.md 2.13）
echo     拡張機能なしのプロファイルで開く。次のブロックのファイルを先に開かない
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
