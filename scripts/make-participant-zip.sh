#!/usr/bin/env bash
# make-participant-zip.sh — 被験者配布用 zip を作成する (Windows 標準解凍で日本語名が化けない)。
#
# 背景: macOS の zip / ditto はファイル名を UTF-8 で格納するが、ZIP の
# 「UTF-8 フラグ (汎用ビット 11)」を立てない。そのため Windows エクスプローラの
# 「すべて展開」が名前を CP932 と誤解釈し、`提出する_win.bat` 等が文字化けする。
# 本スクリプトは zip 作成後に全ヘッダ (local + central) のビット 11 を立て、
# Windows 側で UTF-8 として正しく解釈させる。中身 (ファイル内容) は一切変更しない。
#
# 使い方:
#   ./scripts/make-participant-zip.sh <配布フォルダ> [出力.zip]
# 例:
#   ./scripts/make-participant-zip.sh ./提出ツール 提出ツール.zip
#
# 配布フォルダには launcher (提出する_win.bat / 提出する_mac.command)、
# gse-submit(.exe)、pubkey.txt 等をあらかじめ入れておくこと。
set -euo pipefail

SRC="${1:-}"
if [[ -z "$SRC" || ! -d "$SRC" ]]; then
  echo "使い方: $0 <配布フォルダ> [出力.zip]" >&2
  echo "  <配布フォルダ> に launcher / gse-submit(.exe) / pubkey.txt を入れてから実行する。" >&2
  exit 2
fi

# 末尾スラッシュを除去してフォルダ名を確定
SRC="${SRC%/}"
PARENT="$(cd "$(dirname "$SRC")" && pwd)"
BASE="$(basename "$SRC")"
OUT="${2:-${BASE}.zip}"
# 出力先を絶対パス化 (cd で SRC の親へ移動するため)
case "$OUT" in
  /*) OUT_ABS="$OUT" ;;
  *)  OUT_ABS="$(pwd)/$OUT" ;;
esac

rm -f "$OUT_ABS"

# -r 再帰 / -X mac 拡張属性 (リソースフォーク等) を除外。.DS_Store も除外。
( cd "$PARENT" && zip -q -r -X "$OUT_ABS" "$BASE" -x '*/.DS_Store' '*/__MACOSX/*' )

# 全ヘッダの UTF-8 フラグ (bit 11 = 0x0800) を立てる。
python3 - "$OUT_ABS" <<'PY'
import struct, sys
fn = sys.argv[1]
d = bytearray(open(fn, "rb").read())
def set_flag(sig, flag_off):
    i = 0; n = 0
    while True:
        i = d.find(sig, i)
        if i < 0:
            break
        cur = struct.unpack_from('<H', d, i + flag_off)[0]
        struct.pack_into('<H', d, i + flag_off, cur | 0x0800)
        n += 1; i += 4
    return n
local   = set_flag(b'PK\x03\x04', 6)   # local file header: 汎用ビットは +6
central = set_flag(b'PK\x01\x02', 8)   # central directory header: 汎用ビットは +8
open(fn, "wb").write(d)
print(f"[utf8-flag] local={local} central={central} headers patched")
PY

# 健全性チェック: アーカイブ整合 + 先頭ローカルヘッダの bit11 を確認。
unzip -tq "$OUT_ABS" >/dev/null
python3 - "$OUT_ABS" <<'PY'
import struct, sys
d = open(sys.argv[1], "rb").read()
i = d.find(b'PK\x03\x04')
flag = struct.unpack_from('<H', d, i + 6)[0]
ok = bool(flag & 0x0800)
print(f"[verify] gp_flag=0x{flag:04x} UTF8_bit11={'SET' if ok else 'NOT set'}")
sys.exit(0 if ok else 1)
PY

echo "[done] $OUT_ABS を作成しました。Windows の「すべて展開」で日本語名が化けないことを確認してください。"
