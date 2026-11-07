@echo off
chcp 65001 > nul
rem chcp は日本語より前に置く（Phase1 の launcher 文字化けの再発防止）
setlocal

rem GSE 段 1（ADR-043・本人の試し）— Windows 用 launcher
rem
rem O1 の launcher（launch-o1-windows.bat）を元にして、違いは 3 つ。
rem
rem   1. プローブを止める環境変数を付けない（計画の判断 6）。
rem      段 1 のアプリはその環境変数を見ないが、付けると
rem      手で起動した日と自動起動の日で起動の仕方が割れて見える。
rem      止めるときは s1.mode を外す。
rem   2. s1.mode が無いことを知らせる（無いと素の O1 として動き、問いが出ない）。
rem   3. eh3.mode が同じフォルダにあれば中断する（計画の判断 7）。
rem      アプリは両方の印を落として素の O1 として動くので、黙らせない。
rem
rem 動いていたら何もせず終わる・終わりに pause を置かない、は O1 と同じ
rem （スタートアップから毎回起動されうるため）。
rem
rem このバッチと同じフォルダに gse-next.exe / gse-submit.exe / pubkey.txt /
rem o1.mode / s1.mode / g1-submit.json を置く。
rem 関連: .steering/20261107-gse-m5-s1-replay-gate/design.md（PR 2）

rem 1. 既に動いていれば何もしない
tasklist /FI "IMAGENAME eq gse-next.exe" 2>nul | find /I "gse-next.exe" >nul
if not errorlevel 1 (
  echo GSE は既に動いています。そのままお使いください。
  exit /b 0
)

rem 2. 本体が無ければ中断する（ここだけ pause する）
if not exist "%~dp0gse-next.exe" (
  echo   [中断] このフォルダに gse-next.exe がありません。
  echo          研究者から渡された配布フォルダの中身をそのまま使ってください。
  pause
  exit /b 1
)

rem 3. EH3 の印と同居していたら中断する（計画の判断 7）
if exist "%~dp0eh3.mode" (
  echo   [中断] このフォルダに eh3.mode があります（段 1 の配布物には入れません）。
  echo          このままでは問いが出ません。研究者に連絡してください。
  pause
  exit /b 1
)

rem 4. 足りないファイルを知らせる（止めはしない。記録そのものは取れる）
if not exist "%~dp0gse-submit.exe" echo   [注意] gse-submit.exe がありません（自動送信ができません）。
if not exist "%~dp0pubkey.txt"     echo   [注意] pubkey.txt がありません（暗号化ができません）。
if not exist "%~dp0o1.mode"        echo   [注意] o1.mode がありません（この研究のモードになりません）。
if not exist "%~dp0s1.mode"        echo   [注意] s1.mode がありません（問いが出ません）。
if not exist "%~dp0g1-submit.json" echo   [注意] g1-submit.json がありません（送信先が未設定です）。

start "" "%~dp0gse-next.exe"
exit /b 0
