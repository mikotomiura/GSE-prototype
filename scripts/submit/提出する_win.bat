@echo off
chcp 65001 >nul
rem GSE セッション提出ツール (Windows ダブルクリック用ランチャ・T2)。
rem このファイルと同じフォルダに gse-submit.exe (本体) と pubkey.txt (研究者の公開鍵) を
rem 置いて、本ファイルをダブルクリックしてください。最新のセッションが自動で提出物 (.age) に
rem 変換されます。
rem
rem 初回のみ: SmartScreen の警告が出たら「詳細情報」→「実行」で一度許可してください。
rem
rem [文字コード注意] このファイルは UTF-8 (BOM 付き)。cmd は chcp 65001 より前を CP932 で
rem 読むため、必ず chcp を最初に実行してから日本語を読ませる。この行より前に日本語を置かない。
cd /d "%~dp0"
rem Windows SmartScreen 対策: ブラウザ/Drive 経由でダウンロードした exe には Mark-of-the-Web が
rem 付き、初回起動で警告が出る。本 bat は承認済みで実行できているので、同フォルダの実行ファイルの
rem MOTW (Zone.Identifier) を解除して以降の警告を抑える (ファイル内容は変更しない)。
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -LiteralPath '%~dp0' -File | Unblock-File" >nul 2>&1
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
