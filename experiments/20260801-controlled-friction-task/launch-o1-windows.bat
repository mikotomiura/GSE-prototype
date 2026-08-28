@echo off
rem ★ chcp は日本語より前に置く（Phase1 の launcher 文字化けの再発防止）
chcp 65001 > nul
setlocal

rem GSE O1（ふだんの作業の長期記録）— Windows 用 launcher
rem
rem ⚠️★★★ **G1 の launcher と挙動が 3 か所ちがう。** 流用したと思って読まないこと。
rem
rem   1. ⚠️★★★ **動いていたら殺さない。何もせず終わる。**
rem      G1 は「1 ブロック 1 回」なので旧プロセスを確実に終了させるのが正しかった。
rem      ★ O1 は**常時記録**であり、この bat は**スタートアップから毎回起動される**。
rem      ⚠️ ここで taskkill すると、**記録中のアプリを毎回叩き落とす**ことになる。
rem      → ★ 既に動いていれば「動いています」と出して **exit 0**。二重起動も防げる。
rem
rem   2. ⚠️★★★ **終わりに pause を置かない。**
rem      ★ スタートアップから走るので、pause があると
rem        **黒い窓が毎朝出たまま残る**（被験者は毎日それを閉じることになる）。
rem      ⚠️ ただし**中断したときだけ** pause する（理由が読めないまま消えると直せない）。
rem
rem   3. ★ チェックリストを読み上げない。
rem      G1 は 1 回きりの実施なので毎回の確認に意味があったが、
rem      ⚠️ O1 は毎朝走る。★ 毎朝同じ文章を出しても読まれない（かえって印が埋もれる）。
rem
rem ★ このバッチと同じフォルダに **gse-next.exe / gse-submit.exe / pubkey.txt /
rem   o1.mode / g1-submit.json** を置く（★ 自動送信はこの 5 つが揃って初めて成立する）。
rem ⚠️★ `g1-submit.json` は **名前が g1- のままで正しい**。行き先は中身（endpoint）で決まる。
rem
rem 関連: .steering/20260828-o1-forms-and-distribution/design.md

rem 1. 既に動いていれば何もしない（★ 上のコメント 1）
tasklist /FI "IMAGENAME eq gse-next.exe" 2>nul | find /I "gse-next.exe" >nul
if not errorlevel 1 (
  echo GSE は既に動いています。そのままお使いください。
  exit /b 0
)

rem 2. 本体が無ければ中断する（★ ここだけ pause する）
if not exist "%~dp0gse-next.exe" (
  echo   [中断] このフォルダに gse-next.exe がありません。
  echo          研究者から渡された配布フォルダの中身をそのまま使ってください。
  pause
  exit /b 1
)

rem 3. ⚠️★ 自動送信に要るファイルの不足を知らせる（★ 止めはしない）。
rem    ★ 止めない理由: 記録そのものは取れるからである。⚠️ ただし黙ってもいけない
rem      （足りないと `.age` が端末に貯まるだけで、研究者に届かない）。
if not exist "%~dp0gse-submit.exe" echo   [注意] gse-submit.exe がありません（自動送信ができません）。
if not exist "%~dp0pubkey.txt"     echo   [注意] pubkey.txt がありません（暗号化ができません）。
if not exist "%~dp0o1.mode"        echo   [注意] o1.mode がありません（この研究のモードになりません）。
if not exist "%~dp0g1-submit.json" echo   [注意] g1-submit.json がありません（送信先が未設定です）。

rem 4. ⚠️★ プローブ（画面に出る質問）の 2 本目の引き金。
rem    ★ O1 では `start_session` を呼ばないので `SESSION_START_MS` が 0 のままであり、
rem      スケジューラは**構造的に**起動しない（lib.rs の probe スレッドは session_start!=0 を要求する）。
rem    ⚠️ それでも立てておくのは、将来 O1 で session_start を立てる変更が入ったときに
rem      **同意文書の「助言・介入は一切出しません」が黙って破れる**のを防ぐためである。
set GSE_DISABLE_PROBES=1

start "" "%~dp0gse-next.exe"
exit /b 0
