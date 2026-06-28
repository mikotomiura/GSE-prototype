#!/bin/bash
# GSE セッション提出ツール (macOS ダブルクリック用ランチャ・T2)。
# このファイルと同じフォルダに gse-submit (本体) と pubkey.txt (研究者の公開鍵) を置いて、
# 本ファイルをダブルクリックしてください。最新のセッションが自動で提出物 (.age) に変換されます。
#
# 初回のみ: ダウンロード直後は macOS のセキュリティ警告が出ることがあります。
# その場合は gse-submit と本ファイルを右クリック →「開く」で一度許可してください。
cd "$(dirname "$0")" || exit 1
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
