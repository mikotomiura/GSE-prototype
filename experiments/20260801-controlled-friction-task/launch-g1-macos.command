#!/bin/bash
# G1 統制タスク実験 — macOS 用 launcher（1 ブロック 1 回・ダブルクリックで起動する）
#
# ★ なぜ launcher が要るか（preregistration.md §5.4 / protocol.md §1.1）
#   `GSE_DISABLE_PROBES=1` を立てずに起動すると、アプリ内プローブが 5 分ブロックあたり
#   **57%** の確率で発火する。§2.6 は「アプリ内プローブを使わない」と凍結しており、
#   §3.6 は**ブロックの事後除外を禁じている** = 汚染された回は後から落とせない。
#   1 ブロック = 1 セッションで **10 回起動する**ので、手打ちだと必ずどこかで抜ける。
#
# ★ 2 つの落とし穴を構造的に潰してある
#   1. アプリ名は **gse-next**（tauri.conf.json の productName）。`open -a GSE` では起動しない。
#   2. `open -a` は**既に起動していると新しいプロセスを作らず前面に出すだけ**なので、
#      その回の環境変数が適用されない。→ 先に確実に終了させる。
#      （前ブロックのアプリが残っていると打鍵が 2 本の NDJSON に混ざる問題も同時に防ぐ。）
#
# 検証（2026-08-03・macOS 26.5.2 実測）: `VAR=1 open -a <App>` は環境変数をアプリに渡す。
# ⚠️ `ps eww` では確認できない（macOS は他プロセスの環境を出さない）。当日の確認は
#    アプリのログに `probe scheduler DISABLED by GSE_DISABLE_PROBES=1` が出ることで行う。
#    ★ **本当の確認は実施後**の `python3 validate_blocks.py --dataset ~/gse-dataset`
#      （`probe_assignment` 行が 1 行でもあれば赤）。自己申告で済ませない。

set -u

APP="gse-next"

echo "=== G1 launcher (macOS) ==="

# 1. 既存インスタンスを確実に終了させる
if pgrep -x "$APP" > /dev/null 2>&1; then
  echo "[1/3] 起動中の $APP を終了します..."
  osascript -e "quit app \"$APP\"" > /dev/null 2>&1 || true
  for _ in $(seq 1 20); do
    pgrep -x "$APP" > /dev/null 2>&1 || break
    sleep 0.5
  done
  if pgrep -x "$APP" > /dev/null 2>&1; then
    echo "  ⚠️ 終了しませんでした。手動で終了してから、もう一度このファイルを開いてください。"
    echo "     （このまま起動すると環境変数が効かず、プローブが発火する恐れがあります）"
    read -r -p "Enter で閉じます..." _
    exit 1
  fi
else
  echo "[1/3] 起動中の $APP はありません。"
fi

# 2. kill switch 付きで起動する
echo "[2/3] GSE_DISABLE_PROBES=1 で $APP を起動します..."
if ! GSE_DISABLE_PROBES=1 open -a "$APP"; then
  echo "  ⚠️ 起動に失敗しました。$APP.app が /Applications にあるか確認してください。"
  read -r -p "Enter で閉じます..." _
  exit 1
fi

# 3. 実験者向けの確認事項
cat <<'EOS'
[3/3] 起動しました。ブロックを始める前に確認してください:
  - 週の選択が「第1週 (blind 較正)」であること（既定のまま。触っていなければ OK）
  - アプリのログに `probe scheduler DISABLED by GSE_DISABLE_PROBES=1` が出ていること（当日 1 回でよい）
  - 記入パッド (writing-pad.html) を拡張機能なしのプロファイルで全画面表示していること
  - ★ 自己マーカー hotkey (Cmd+Shift+Alt+M) を押さないこと
EOS

read -r -p "Enter でこのウィンドウを閉じます..." _
