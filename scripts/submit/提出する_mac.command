#!/bin/bash
# GSE セッション提出ツール (macOS ダブルクリック用ランチャ・T2)。
# このファイルと同じフォルダに gse-submit (本体) と pubkey.txt (研究者の公開鍵) を置いて、
# 本ファイルをダブルクリックしてください。最新のセッションが自動で提出物 (.age) に変換されます。
#
# 初回のみ: ダウンロード直後は macOS のセキュリティ警告が出ることがあります。
# その場合は gse-submit と本ファイルを右クリック →「開く」で一度許可してください。
cd "$(dirname "$0")" || exit 1
# macOS Gatekeeper 対策: ブラウザ/Drive 経由でダウンロードした未署名 (ad-hoc 署名) の CLI は
# com.apple.quarantine が付き、そのまま実行すると Gatekeeper に SIGKILL される (exit 137)。
# 本スクリプトはユーザーが右クリック→「開く」で一度承認して実行できているので、この時点で
# 同じフォルダ内の隔離属性 (gse-submit / gse-package 等) を解除すれば、以降の ./gse-submit が
# 起動できる。鍵やデータは書き換えない (xattr 属性の除去のみ)。
xattr -dr com.apple.quarantine "$(dirname "$0")" 2>/dev/null
chmod +x ./gse-submit 2>/dev/null
./gse-submit
status=$?
echo ""
if [ "$status" -eq 0 ]; then
  echo "✓ 完了しました。生成された .age ファイルを研究者の Dropbox に提出してください。"
else
  echo "× 提出物を作成できませんでした。上のメッセージを研究者に共有してください。"
fi
echo ""
read -n 1 -s -r -p "何かキーを押すとこのウィンドウを閉じます..."
echo ""
