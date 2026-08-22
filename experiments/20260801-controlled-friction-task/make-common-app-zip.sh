#!/usr/bin/env bash
# ★ **全員共通**のアプリ配布物を組む（Drive の「アプリダウンロードリンク」に置くもの）。
#
# 使い方:
#   ./make-common-app-zip.sh [--tag vX.Y.Z] [--config <g1-submit.json>]
#   → dist/_common/G1_実施用_macOS.zip   ← ★ Drive に置くのはこれ 1 個
#     dist/_common/G1_実施用_Windows.zip
#
# ============================================================================
# ⚠️★★ `make-distribution.sh` との違い（★ 混同しないこと）
# ============================================================================
#   make-distribution.sh … **被験者 1 人ぶん**。課題ページ (blockNN.html) が入る。割付が要る。
#   このスクリプト        … **全員共通**。⚠️ **課題ページを入れない**。割付は要らない。
#
#   ★ 課題ページを共通側に入れてはならない。入れると全員が同じ課題を持つことになり、
#     被験者ごとの割付が壊れる (`decisions.md` D-1)。
#
# ============================================================================
# ⚠️★★ なぜ zip なのか（フォルダのまま Drive に置かない理由）
# ============================================================================
#   ★ **Drive はパーミッションを保存しない。** 2026-08-07 に実測:
#     Drive から落とした 4 件がすべて `-rw-rw-r--`（元は `-rw-r--r--`）＝
#     保存されたのではなく**後から一律に付け直されている**。
#   ⚠️ `.app` は `Contents/MacOS/` の 7 ファイルが**実行ビットに依存**する。
#     → フォルダのまま置いて「フォルダをダウンロード」させると、
#       ★ **実行ビットの落ちた `.app`** が届く。
#   ★ 単一ファイルの zip なら Drive はただのバイト列として配る（dmg が byte 一致で実測済み）ので、
#     zip 内部に記録された実行ビットごと届く。
#
# ⚠️★ `.app` は **dmg から取り出してフォルダに入れた状態**で固める。
#   ドラッグ工程を残すと、被験者は dmg から直接起動して **G1 モードにならない**
#   （2026-08-07 に実機で発生。`decisions.md` D-9）。

set -euo pipefail
shopt -s nullglob
cd "$(dirname "$0")"

HERE="$(pwd)"
REPO="$(cd ../.. && pwd)"
TAG="v0.1.24"
CONFIG="$REPO/g1-submit.json"

die() { echo "[make-common-app-zip] ✗ $*" >&2; exit 1; }
note() { echo "[make-common-app-zip] $*"; }

while [ $# -gt 0 ]; do
  case "$1" in
    --tag) TAG="${2:-}"; shift 2 ;;
    --config) CONFIG="${2:-}"; shift 2 ;;
    -h|--help) sed -n '1,40p' "$0"; exit 0 ;;
    *) die "知らない引数: $1" ;;
  esac
done

# --- 1. 送信先の設定（★ 無ければ止める。無いまま配ると記録が研究者に届かない） -----
[ -f "$CONFIG" ] || die "送信先の設定がありません: $CONFIG"
python3 - "$CONFIG" <<'PY' || exit 1
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
ep, sec = d.get("endpoint", ""), d.get("secret", "")
if not (isinstance(ep, str) and ep.startswith("https://script.google.com/macros/s/") and ep.endswith("/exec")):
    sys.exit("[make-common-app-zip] ✗ endpoint が /exec で終わる Apps Script の URL ではありません")
if not (isinstance(sec, str) and len(sec) >= 24):
    sys.exit("[make-common-app-zip] ✗ secret が 24 文字未満です")
print(f"[make-common-app-zip] 送信先の設定 ✅ (endpoint {len(ep)} 文字 / secret {len(sec)} 文字)")
PY

# --- 2. タグに自動送信が入っているか（★ サイズや名前では確かめたことにならない） ----
git -C "$REPO" rev-parse "$TAG" > /dev/null 2>&1 || die "タグがありません: $TAG"
git -C "$REPO" cat-file -e "$TAG:src-tauri/src/reconcile.rs" 2>/dev/null \
  || die "$TAG に reconcile.rs がありません = 自動送信が入っていないビルドです"
note "タグ $TAG に自動送信あり ✅"

CACHE="$HERE/dist/_release/$TAG"
mkdir -p "$CACHE"
if [ ! -f "$CACHE/gse-next.exe" ] || [ ! -f "$CACHE/gse-submit.exe" ] || [ -z "$(echo "$CACHE"/*.dmg)" ]; then
  note "リリース成果物を取得します ($TAG)"
  ( cd "$CACHE" && gh release download "$TAG" --repo mikotomiura/GSE-prototype --clobber \
      --pattern 'gse-next.exe' --pattern 'gse-submit.exe' --pattern '*.dmg' ) \
    || die "gh release download に失敗しました"
fi

OUT="$HERE/dist/_common"
rm -rf "$OUT"
mkdir -p "$OUT"

# --- 3. macOS（★ .app 同梱・課題ページ無し） ---------------------------------
M="$OUT/G1_実施用_macOS"
mkdir -p "$M"
DMG=$(basename "$(ls "$CACHE"/*.dmg | head -1)")
cp "$CONFIG" "$M/g1-submit.json"
: > "$M/g1.mode"
sed "s/@DMG@/$DMG/g" "$HERE/dist-readme-macos.txt" > "$M/README_先に読む.txt"

# ★★ 初回セットアップスクリプト（preregistration.md 第 13 版 §2.14）。
#   ⚠️ 手打ちの `xattr` の置き換え。★ ドラッグして実行するのでパスを打たない。
#   ⚠️ quarantine が付いていても `bash <パス>` なら動く（2026-08-08 実測）。
cp "$HERE/初回セットアップ_mac.sh" "$M/" || die "初回セットアップ_mac.sh を入れられません"
bash "$M/初回セットアップ_mac.sh" --selftest > /dev/null \
  || die "★ 初回セットアップ_mac.sh の自己検査が赤い。壊れたものを配らない"

MNT=$(mktemp -d)
trap 'hdiutil detach "$MNT" -quiet 2>/dev/null || true; rmdir "$MNT" 2>/dev/null || true' EXIT
hdiutil attach "$CACHE/$DMG" -mountpoint "$MNT" -nobrowse -quiet || die "dmg をマウントできません"
[ -d "$MNT/gse-next.app" ] || die "dmg に gse-next.app がありません"
codesign --verify --strict "$MNT/gse-next.app" || die "dmg 内の署名が壊れています"
ditto "$MNT/gse-next.app" "$M/gse-next.app" || die "gse-next.app を取り出せません"
hdiutil detach "$MNT" -quiet || true
trap - EXIT
rmdir "$MNT" 2>/dev/null || true

codesign --verify --strict "$M/gse-next.app" || die "フォルダへ置いた後に署名が壊れました"

# ⚠️★ 課題ページが紛れていないことを確かめる（共通側に入れてはならない・D-1）
[ -z "$(echo "$M"/block*.html)" ] || die "共通の配布物に課題ページが入っています（被験者別のはず）"

( cd "$OUT" && ditto -c -k --sequesterRsrc --keepParent "G1_実施用_macOS" "G1_実施用_macOS.zip" ) \
  || die "macOS の zip を作れません"
# ⚠️★ `--sequesterRsrc` は AppleDouble (`._*`) を撒かない代わりに `__MACOSX/` へ集める。
#   ★ 集めただけで消えてはいないので、配る前に取り除く（2026-08-23 実測: 51 エントリ中 25 件が混入）。
zip -d "$OUT/G1_実施用_macOS.zip" "__MACOSX/*" > /dev/null \
  || die "macOS zip から __MACOSX を除去できません"

# --- 4. Windows（★ 日本語ファイル名の文字化けを避けるため、こちらも zip で配る） ----
# ⚠️ Windows に実行ビットの問題は無いが、Drive の「フォルダをダウンロード」で
#   日本語名が化ける経路がある (memory: participant-launcher-encoding)。★ zip で固めて配る。
W="$OUT/G1_実施用_Windows"
mkdir -p "$W"
cp "$CACHE/gse-next.exe" "$CACHE/gse-submit.exe" "$W/"
cp "$HERE/launch-g1-windows.bat" "$W/"
cp "$REPO/src-tauri/resources/pubkey.txt" "$W/"
cp "$CONFIG" "$W/g1-submit.json"
: > "$W/g1.mode"
# ★ 実体に自動送信が入っているか（`grep -c` を使う。`grep -q` は SIGPIPE で偽陰性を作る）
if command -v strings > /dev/null 2>&1; then
  n=$(strings -a "$W/gse-submit.exe" | grep -c -- 'reconcile' || true)
  [ "${n:-0}" -gt 0 ] || die "gse-submit.exe に reconcile が見当たりません（古いビルド）"
  note "gse-submit.exe の実体に reconcile あり ✅ ($n 箇所)"
else
  note "⚠️ strings が無いので実体検査を飛ばしました"
fi
[ -z "$(echo "$W"/block*.html)" ] || die "共通の配布物に課題ページが入っています"
# ⚠️★★ **Windows 向けは `ditto` で作ってはならない。** 2026-08-07 に実測で踏んだ:
#   ditto の zip は (a) `__MACOSX/._*` を撒き、(b) ★ **ZIP の UTF-8 フラグ (汎用ビット 11) を
#   立てない**ので、Windows エクスプローラで**日本語のフォルダ名が化ける**
#   (memory: participant-launcher-encoding)。
#   → 既存の対策スクリプトを使う。⚠️ 自前で作り直さない（同じ罠を踏み直すため）。
"$REPO/scripts/make-participant-zip.sh" "$W" "$OUT/G1_実施用_Windows.zip" > /dev/null \
  || die "Windows の zip を作れません"

# --- 5. 展開して確かめる（★ 配る前に、配る物そのものを検査する） -----------------
V=$(mktemp -d)
ditto -x -k "$OUT/G1_実施用_macOS.zip" "$V" || die "macOS zip を展開できません"
codesign --verify --strict "$V/G1_実施用_macOS/gse-next.app" || die "展開後に署名が壊れています"
[ -x "$V/G1_実施用_macOS/gse-next.app/Contents/MacOS/gse-next" ] || die "展開後に実行ビットが落ちています"
[ -f "$V/G1_実施用_macOS/g1.mode" ] || die "展開後に g1.mode がありません"

# ★★ 初回セットアップスクリプトが**展開後も動く**こと（2026-08-08）。
#   ⚠️ 同梱しただけでは足りない。⚠️ zip 越しに壊れていないかは**展開して走らせないと分からない**。
[ -f "$V/G1_実施用_macOS/初回セットアップ_mac.sh" ] || die "展開後に 初回セットアップ_mac.sh がありません"
bash "$V/G1_実施用_macOS/初回セットアップ_mac.sh" --selftest > /dev/null \
  || die "展開後の 初回セットアップ_mac.sh が自己検査に落ちました"

# ★★ README が**被験者を守る 3 文**を落としていないこと（2026-08-08）。
#   ⚠️ ★ 「壊れていません」「ゴミ箱に入れないで」が無いと、被験者は
#      「壊れているため開けません」を見て **本当にゴミ箱に入れてしまう**（取り返しがつかない）。
#   ⚠️ ★ 表記ゆれで検査が空回りしないよう、**README 側の文言をこの検査に合わせる**こと
#      （2026-08-08 に「壊れてはいません」と書いて grep が 0 件になった）。
R="$V/G1_実施用_macOS/README_先に読む.txt"
for phrase in "研究者と一緒に" "壊れていません" "ゴミ箱に入れないで" "ターミナルの窓へドラッグ"; do
  grep -q "$phrase" "$R" || die "README に「${phrase}」がありません（★ 被験者を守る文言・§2.14 第 13 版）"
done
# ⚠️ 旧版（A 型ダイアログ向け）の案内が戻っていないこと。★ B 型では効かない。
for phrase in "右クリック" "開発元を確認できません"; do
  ! grep -q "$phrase" "$R" || die "README に旧版の案内「${phrase}」が残っています（★ B 型では効かない）"
done

rm -rf "$V"

# ★ macOS zip 自体にも余計なものが無いことを機械で確かめる（Windows 側と対称の検査）。
#   ⚠️ `--sequesterRsrc` は __MACOSX/ へ集めるだけで消さない。`zip -d` 後にここで確定させる。
python3 - "$OUT/G1_実施用_macOS.zip" <<'PY' || exit 1
import sys, zipfile
p = sys.argv[1]
names = zipfile.ZipFile(p).namelist()
junk = [n for n in names if "__MACOSX" in n or n.endswith("/.DS_Store") or n == ".DS_Store"]
if junk:
    sys.exit(f"[make-common-app-zip] ✗ macOS zip に余計なものが入っています: {junk[:3]}")
print(f"[make-common-app-zip] macOS: 余計なもの無し ✅ ({len(names)} エントリ)")
PY

note "macOS: 展開して検査 ✅（署名 / 実行ビット / g1.mode / セットアップ自己検査 / README 文言 / __MACOSX 不在）"

# ★ Windows zip は「Windows で化けないこと」を機械で確かめる。
#   ⚠️ 目で見て判断しない（macOS の unzip は化けて見えても Windows では正しいことがある）。
python3 - "$OUT/G1_実施用_Windows.zip" <<'PY' || exit 1
import struct, sys, zipfile
p = sys.argv[1]
with open(p, "rb") as fh:
    d = fh.read()
i = d.find(b"PK\x03\x04")
flag = struct.unpack_from("<H", d, i + 6)[0]
if not (flag & 0x0800):
    sys.exit("[make-common-app-zip] ✗ Windows zip の UTF-8 フラグ (bit 11) が立っていません")
names = zipfile.ZipFile(p).namelist()
junk = [n for n in names if "__MACOSX" in n or n.endswith("/.DS_Store")]
if junk:
    sys.exit(f"[make-common-app-zip] ✗ Windows zip に余計なものが入っています: {junk[:3]}")
if not any(n.startswith("G1_実施用_Windows/") for n in names):
    sys.exit("[make-common-app-zip] ✗ Windows zip の中のフォルダ名が壊れています")
print(f"[make-common-app-zip] Windows: UTF-8 フラグ ✅ / 余計なもの無し ✅ ({len(names)} エントリ)")
PY

echo
note "できました:"
for z in "$OUT"/*.zip; do
  printf '    %s  %s B\n' "$z" "$(wc -c < "$z" | tr -d ' ')"
done
echo
echo "[make-common-app-zip] ★ Drive に置くのは上の **zip だけ**です（フォルダのまま置かない）。"
echo "[make-common-app-zip] ⚠️ g1-submit.json はシークレットを含みます。共有範囲に注意してください。"
