@echo off
rem GSE セッション提出ツール (Windows ダブルクリック用ランチャ・T2)。
rem このファイルと同じフォルダに gse-submit.exe (本体) と pubkey.txt (研究者の公開鍵) を
rem 置いて、本ファイルをダブルクリックしてください。最新のセッションが自動で提出物 (.age) に
rem 変換されます。
rem
rem 初回のみ: SmartScreen の警告が出たら「詳細情報」→「実行」で一度許可してください。
chcp 65001 >nul
cd /d "%~dp0"
gse-submit.exe
set STATUS=%ERRORLEVEL%
echo.
if "%STATUS%"=="0" (
  echo [OK] 完了しました。生成された .age ファイルを研究者の Dropbox に提出してください。
) else (
  echo [NG] 提出物を作成できませんでした。上のメッセージを研究者に共有してください。
)
echo.
pause
