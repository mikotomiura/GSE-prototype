#!/usr/bin/env bash
# 被験者 1 人分の **課題ページ** を Drive へ上げる準備をする。
#
# ★ このスクリプトは **上げない**。上げる物を用意し、上げたあとに突き合わせる
#   「照合表」を作るところまでである（`make-distribution.sh` と同じ流儀）。
#
# 使い方:
#   ./make-upload-manifest.sh <被験者ID>                … dist/<ID>/G1_実施用_* から取る
#   ./make-upload-manifest.sh --from-pages <被験者ID>   … ★ pages/<ID>/ から取る
#   → dist/<ID>/_upload/manifest.tsv      … 名前 / byte 数 / SHA-256
#     dist/<ID>/_upload/<name>.b64        … create_file に渡す base64（1 行）
#
# ★ `--from-pages` は **アプリを組まずに課題ページだけ配る**運用のためにある（2026-08-07）。
#   アプリは全員共通の zip で配るようになった (`make-common-app-zip.sh`) ので、
#   被験者ごとに要るのは課題ページだけであり、`make-distribution.sh`（dmg のマウント・
#   codesign・gh release download）を 15 回回す理由が無い。
#   ⚠️ ただし dist/<ID>/ が**既にある**ときは、そちらと食い違っていないことを確かめる
#     （★ 古い梱包が残ったまま新しいページを上げると、手渡し分と Drive 分で割付がずれる）。
#
# ============================================================================
# ⚠️★★ なぜ base64 なのか（★ textContent を使わない理由）
# ============================================================================
#   Drive MCP の `textContent` 送信は **中身次第でバイトが化ける**。
#   エスケープ列を含む HTML で **44B 欠損を実測**している (memory: drive-mcp-upload-fidelity)。
#   block ページは `writing-pad.html` 由来の JS を含むので、この経路に該当しうる。
#   → `base64Content` ＋ `disableConversionToGoogleType: true` で上げ、**上げた後に照合する**。
#
# ⚠️★ Drive MCP には **更新・削除のツールが無い**。壊すと重複が残って直せない。
#   → 「上げてから確かめる」ではなく「上げて、確かめて、**合わなければリンクを出さない**」。

set -euo pipefail
# ⚠️★ bash は一致しない glob を **リテラルのまま**残す（実測: `for f in dir/block*.html` が
#   0 件のとき `f` に `dir/block*.html` という文字列が入る）。そのまま basename に渡すと
#   「macOS 側に block*.html がありません」という**原因を取り違えさせるエラー**になる。
#   → nullglob にして 0 件は 0 回ループにする（件数の検査は下の PAGE/COUNT で別に行う）。
shopt -s nullglob
cd "$(dirname "$0")"

HERE="$(pwd)"
FROM_PAGES=0
if [ "${1:-}" = "--from-pages" ]; then FROM_PAGES=1; shift; fi
SUBJECT="${1:-}"

die() { echo "[make-upload-manifest] ✗ $*" >&2; exit 1; }
note() { echo "[make-upload-manifest] $*"; }

[ -n "$SUBJECT" ] || die "被験者 ID を渡してください。例: ./make-upload-manifest.sh P015"

WIN="$HERE/dist/$SUBJECT/G1_実施用_Windows"
MAC="$HERE/dist/$SUBJECT/G1_実施用_macOS"
PAGES="$HERE/pages/$SUBJECT"

# --- 1. 取り元があるか（★ 無ければ作らずに止まる） ----------------------------
SRC=""
if [ "$FROM_PAGES" -eq 1 ]; then
  [ -d "$PAGES" ] || die "課題ページがありません: pages/$SUBJECT/
  先に次を実行してください:
      ./prepare-subjects.sh $SUBJECT"
  SRC="$PAGES"
else
  [ -d "$WIN" ] && SRC="$WIN"
  [ -z "$SRC" ] && [ -d "$MAC" ] && SRC="$MAC"
  if [ -z "$SRC" ]; then
    echo "[make-upload-manifest] ✗ 配布物がありません: dist/$SUBJECT/" >&2
    echo "  先に次を実行してください:" >&2
    echo "      ./make-distribution.sh $SUBJECT both" >&2
    exit 1
  fi
fi

# --- 2. ⚠️ 取り元どうしで課題ページが同一か ------------------------------------
# ★ 片方だけ作り直した状態を配ると、OS によって / 経路によって違う割付を渡すことになる。
#   ⚠️ `--from-pages` のときも、**古い梱包が残っていれば**そこと突き合わせる
#     （手渡し分と Drive 分でずれるのが一番気づきにくい）。
compare_against() {
  local other="$1" label="$2" f b n=0
  [ -d "$other" ] || return 0
  for f in "$SRC"/block*.html; do
    b=$(basename "$f")
    [ -f "$other/$b" ] || die "$label に $b がありません（片方だけ古い可能性）"
    cmp -s "$f" "$other/$b" || die "$label と $b の中身が違います（作り直してください）"
    n=$((n + 1))
  done
  # ⚠️★ 向こうにしか無い block を見逃さない（枚数が減ったときに古いページが残る経路）
  local g
  g=$(find "$other" -maxdepth 1 -name 'block*.html' | wc -l | tr -d ' ')
  [ "$g" -eq "$n" ] || die "$label の課題ページが $g 枚、こちらが $n 枚です（作り直してください）"
  note "$label と課題ページが同一 ✅ ($n 枚)"
}
if [ "$FROM_PAGES" -eq 1 ]; then
  compare_against "$WIN" "dist/$SUBJECT/G1_実施用_Windows（既存の梱包）"
  compare_against "$MAC" "dist/$SUBJECT/G1_実施用_macOS（既存の梱包）"
elif [ -d "$WIN" ] && [ -d "$MAC" ] && [ "$SRC" = "$WIN" ]; then
  compare_against "$MAC" "macOS 側"
fi

# --- 3. 課題ページがあるか ----------------------------------------------------
COUNT=$(find "$SRC" -maxdepth 1 -name 'block*.html' | wc -l | tr -d ' ')
[ "$COUNT" -gt 0 ] || die "$SRC に blockNN.html が 1 枚もありません"

# --- 4. ⚠️★ シークレットを混ぜない --------------------------------------------
# 被験者別フォルダに上げてよいのは **課題ページだけ** である (decisions.md D-1)。
# ★ ここで名前を絞っているので、g1-submit.json が紛れ込む経路が無い。
OUT="$HERE/dist/$SUBJECT/_upload"
rm -rf "$OUT"
mkdir -p "$OUT"

MAN="$OUT/manifest.tsv"
: > "$MAN"
for f in "$SRC"/block*.html; do
  b=$(basename "$f")
  case "$b" in
    block*.html) ;;
    *) die "想定外のファイルを掴みました: $b" ;;
  esac
  bytes=$(wc -c < "$f" | tr -d ' ')
  sha=$(shasum -a 256 "$f" | cut -d' ' -f1)
  printf '%s\t%s\t%s\n' "$b" "$bytes" "$sha" >> "$MAN"
  # ⚠️★ 改行を入れない（1 行の base64 にする）。macOS の base64 は既定で折り返さない。
  base64 -i "$f" | tr -d '\n' > "$OUT/$b.b64"
done

note "課題ページ $COUNT 枚 ✅"
note "できました: $OUT"
echo
sed 's/^/    /' "$MAN"
echo
echo "[make-upload-manifest] 次: Drive の 課題ページ_被験者別/ に $SUBJECT フォルダを作り、"
echo "                       各 .b64 を base64Content で上げ、verify-drive-upload.py で照合する。"
echo "[make-upload-manifest] ⚠️ 照合が緑になるまでフォルダの URL を配らないこと。"
