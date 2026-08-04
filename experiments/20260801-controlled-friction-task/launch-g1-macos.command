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

#
# ★★ macOS のセキュリティ 3 関門（2026-08-04 実測で切り分け）
#   1. 実行ビット: Drive/zip 経由でダウンロードすると +x が落ちる
#      → ダブルクリックが "permission denied" になる（実測）
#   2. quarantine: ダウンロード物に com.apple.quarantine が付く → Gatekeeper が止める
#   3. ★ アプリ本体: CI は ad-hoc 署名 (APPLE_SIGNING_IDENTITY: "-") で **未公証**
#      → .app も同じ関門に当たる。★ これが本命である
#
#   ★★ 1 と 2 は `bash <このファイル>` で両方回避できる（3 状態すべてで動くことを実測）。
#      → 推奨: ~/.zshrc に  alias g1='bash <このファイルのフルパス>'
#              以降はターミナルで `g1`。10 回の再実行は ↑ + Enter で済む。
#   ⚠️ 3 はアプリ側なので回避できない。下の PRE-FLIGHT が検出して直し方を出す。
#
# ⚠️★★ Phase1 の先行事例を踏まえること
#   `.steering/20260629-submit-inapp-button-and-mac-gatekeeper/requirement.md` が
#   **同じ問題**（`提出する_mac.command`）で以下を確定している:
#     「2層構造: ①`.command` 自身が quarantine → ダブルクリックでブロック（被験者がここで停止）
#       ②中で呼ぶバイナリも quarantine → SIGKILL。
#       スクリプト内の `xattr -dr` は**②しか解決しない**（起動して初めて走るため①に無力）」
#   → Phase1 は **`.command` 経路そのものを廃止**し、Gatekeeper 承認済みのアプリ内ボタンにした
#     (`docs/pilot-runbook.md`)。
#   ⚠️ ★ **下の PRE-FLIGHT も②の対策であり、①には無力である。**
#      ①を消す手は 2 つしかない: (a) `bash` 経由で起動する  (b) launcher 自体を無くす。
#   ⚠️ `xattr -cr` は使わない（全属性を消して署名を壊す・README.md:147）。`-dr` を使う。

set -u

APP="gse-next"

echo "=== G1 launcher (macOS) ==="

# ---- PRE-FLIGHT: アプリの所在と quarantine を先に見る（★ 起動してから気づかない） ----
APP_PATH=""
for cand in "/Applications/$APP.app" "$HOME/Applications/$APP.app"; do
  [ -d "$cand" ] && APP_PATH="$cand" && break
done

if [ -z "$APP_PATH" ]; then
  echo "  ⚠️ $APP.app が /Applications にも ~/Applications にも見つかりません。"
  echo "     .dmg を開いて $APP.app を /Applications にコピーしてください。"
  read -r -p "Enter で閉じます..." _
  exit 1
fi
echo "[0/3] アプリ: $APP_PATH"

if xattr -p com.apple.quarantine "$APP_PATH" > /dev/null 2>&1; then
  echo "  ⚠️ ★ $APP.app に quarantine が付いています（ダウンロード物）。"
  echo "     CI は ad-hoc 署名 (\"-\") で **未公証** なので、Gatekeeper がこのまま止めます。"
  echo "     ★ 次の 1 行をターミナルに貼って解除してください（研究者本人の端末での正当な操作）:"
  echo
  echo "       xattr -dr com.apple.quarantine \"$APP_PATH\""
  echo
  echo "     解除したら、このファイルをもう一度開いてください。"
  read -r -p "Enter で閉じます..." _
  exit 1
fi

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
# ⚠️ ★ アプリ名の形を使う。`VAR=1 open -a <アプリ名>` が env を渡すことは 2026-08-03 に
#    テスト用 .app で実測済みだが、`open -a <フルパス>` の形は**確かめていない**。
#    PRE-FLIGHT で所在は確認済みなので、ここは検証済みの形のままにする。
if ! GSE_DISABLE_PROBES=1 open -a "$APP"; then
  echo "  ⚠️ 起動に失敗しました。"
  echo "     ★ Gatekeeper で止まっている場合は次を試してください:"
  echo "       xattr -dr com.apple.quarantine \"$APP_PATH\""
  echo "     ⚠️ 「開発元を検証できません」のダイアログが出た場合は"
  echo "        システム設定 > プライバシーとセキュリティ の下部で「このまま開く」。"
  read -r -p "Enter で閉じます..." _
  exit 1
fi

# 3. 実験者向けの確認事項
cat <<'EOS'
[3/3] 起動しました。ブロックを始める前に確認してください:
  - 週の選択が「第1週 (blind 較正)」であること（既定のまま。触っていなければ OK）
  - ★ そのブロックの blockNN.html を「1 つだけ」開いていること
    （記入欄はページに内蔵されている。protocol.md §1.2 / preregistration.md §2.13）
    拡張機能なしのプロファイルで開く。⚠️ 次のブロックのファイルを先に開かない
  - ★ 自己マーカー hotkey (Cmd+Shift+Alt+M) を押さないこと

⚠️ 「アプリのログに probe scheduler DISABLED … が出ること」は確認手段にならない。
   open -a 起動では stdout がどこにも出ない（Windows の windows_subsystem="windows" と同じ）。
   ★ 代わりに、各ブロックが終わったら「30 秒チェック」を行う:

     f=$(ls -t ~/Documents/GSE-sessions/gse_*.ndjson | head -1)
     grep -c -E '"type":"(probe_assignment|probe_triggered|realtime_label)"' "$f"

   → 0 なら続行。1 以上ならそのブロックは使えない。
   ⚠️ grep -c は 0 件でも 0 を出す。「何も出ない」ではなく数字を読むこと。
EOS

read -r -p "Enter でこのウィンドウを閉じます..." _
