#!/usr/bin/env bash
# 被験者 1 人分の **配布フォルダ** を組む（Windows / macOS）。
#
# ★ 出力は dist/（.gitignore 済み）。⚠️ **`g1-submit.json` を含むのでそのまま公開しない。**
#
# 使い方:
#   ./make-distribution.sh <被験者ID> [win|mac|both] [--tag vX.Y.Z] [--config <g1-submit.json>]
# 例:
#   ./make-distribution.sh P015 both
#   ./make-distribution.sh PILOT-win win --tag v0.1.23
#
# ============================================================================
# ⚠️★★ このスクリプトが **やらないこと**（意図的）
# ============================================================================
#
#   1. ★ **割付 (`assign.py`) を回さない。**
#      割付は seed を使う **科学的な行為**であり、梱包のついでに走らせてよいものではない
#      (`reproducibility-discipline`)。⚠️ 取り違えると「同じ人に 2 通りの割付」が黙って生まれる。
#      → `blocks/<ID>.json` が無ければ **作らずに止まり**、打つべきコマンドを表示する。
#
#   2. ★ **アプリを手元でビルドしない。** 配るのは **CI が作ったリリース成果物**だけである
#      (`build-ci-and-pilot-distribution`)。手元ビルドは署名・entitlements の後処理が
#      CI と揃わない。→ `gh release download` で取る。
#
#   3. ★ **Drive へ上げない。** 上げるのは人の判断。ここは「上げる物を作る」までである。
#
# ============================================================================
# ★ 組み上がりの形（★ どちらも **平ら**。入れ子にしない）
# ============================================================================
#
#   dist/<ID>/G1_実施用_Windows/          dist/<ID>/G1_実施用_macOS/
#     gse-next.exe                          gse-next_<ver>_aarch64.dmg
#     gse-submit.exe                        g1.mode            (0 バイト)
#     launch-g1-windows.bat                 g1-submit.json
#     pubkey.txt                            README_先に読む.txt
#     g1.mode            (0 バイト)         block01..NN.html
#     g1-submit.json
#     block01..NN.html
#
# ⚠️★ `g1.mode` は **アプリの実行ファイルから見て決まった階層**に無いと効かない
#   (`src-tauri/src/g1.rs` の `exe_to_folder_levels`: Windows=1 / macOS=**4**)。
#   → Windows は `gse-next.exe` と同じ階層、macOS は **`.app` を置くフォルダ**である。
#   ★ macOS はユーザが dmg から `.app` をこのフォルダへ取り出して初めて成立するので、
#   その手順を `README_先に読む.txt` に書く。

set -euo pipefail
cd "$(dirname "$0")"

HERE="$(pwd)"
REPO="$(cd ../.. && pwd)"
TAG="v0.1.23"
CONFIG="$REPO/g1-submit.json"
SUBJECT=""
TARGET="both"

die() { echo "[make-distribution] ✗ $*" >&2; exit 1; }
note() { echo "[make-distribution] $*"; }

# --- 引数 -------------------------------------------------------------------
while [ $# -gt 0 ]; do
  case "$1" in
    --tag) TAG="${2:-}"; shift 2 ;;
    --config) CONFIG="${2:-}"; shift 2 ;;
    win|mac|both) TARGET="$1"; shift ;;
    -h|--help) sed -n '1,40p' "$0"; exit 0 ;;
    -*) die "知らないオプション: $1" ;;
    *) [ -z "$SUBJECT" ] || die "被験者 ID を 2 つ渡している: $SUBJECT / $1"; SUBJECT="$1"; shift ;;
  esac
done
[ -n "$SUBJECT" ] || die "被験者 ID を渡してください。例: ./make-distribution.sh P015 both"

# --- 1. 割付があるか（★ 無ければ作らずに止まる） ------------------------------
BLOCKS="$HERE/blocks/$SUBJECT.json"
if [ ! -f "$BLOCKS" ]; then
  echo "[make-distribution] ✗ 割付がありません: blocks/$SUBJECT.json" >&2
  echo "  ★ 割付は seed を使う科学的な行為なので、このスクリプトは作りません。" >&2
  echo "  先に次を実行してください:" >&2
  echo "      python3 assign.py --subject $SUBJECT" >&2
  echo "      python3 validate_blocks.py" >&2
  exit 1
fi
note "割付: blocks/$SUBJECT.json ✅"

# --- 2. 転記の整合（★ 赤なら組まない） ---------------------------------------
python3 validate_blocks.py > /tmp/g1-validate.$$ 2>&1 || {
  sed 's/^/    /' /tmp/g1-validate.$$ >&2; rm -f /tmp/g1-validate.$$
  die "validate_blocks.py が通らないので梱包しません"
}
rm -f /tmp/g1-validate.$$
note "割付の整合 ✅"

# --- 3. 課題ページを生成（★ 割付から決まるので毎回作り直してよい） ------------
python3 build_task_pages.py --subject "$SUBJECT" > /dev/null
PAGES_DIR="$HERE/pages/$SUBJECT"
[ -d "$PAGES_DIR" ] || die "ページが生成されませんでした: pages/$SUBJECT"
PAGE_COUNT=$(find "$PAGES_DIR" -maxdepth 1 -name 'block*.html' | wc -l | tr -d ' ')
[ "$PAGE_COUNT" -gt 0 ] || die "pages/$SUBJECT に blockNN.html が 1 枚もありません"
note "課題ページ: $PAGE_COUNT 枚 ✅"

# --- 4. 送信先の設定（★ 無ければ止める） -------------------------------------
# ⚠️ 無いまま配ると `.age` は端末に貯まるだけで研究者に届かない。★ 黙って進まない。
[ -f "$CONFIG" ] || die "送信先の設定がありません: $CONFIG
  ★ Form_G1/README.md の受け口配備 (B-2) を先に済ませ、g1-submit.json を用意してください。
  別の場所にあるなら --config <パス> で渡してください。"
python3 - "$CONFIG" <<'PY' || exit 1
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception as e:
    sys.exit(f"[make-distribution] ✗ g1-submit.json が JSON として壊れています: {e}")
ep, sec = d.get("endpoint", ""), d.get("secret", "")
if not (isinstance(ep, str) and ep.startswith("https://script.google.com/macros/s/") and ep.endswith("/exec")):
    sys.exit("[make-distribution] ✗ endpoint が /exec で終わる Apps Script の URL ではありません")
if not (isinstance(sec, str) and len(sec) >= 24):
    sys.exit("[make-distribution] ✗ secret が 24 文字未満です (受け口の checkSubmitConfig と同じ基準)")
print(f"[make-distribution] 送信先の設定 ✅ (endpoint {len(ep)} 文字 / secret {len(sec)} 文字)")
PY

# --- 5. リリース成果物（★ CI が作ったものだけ） -------------------------------
# ⚠️★ タグの中身に自動送信が入っていることを **git で確かめる**。
#   サイズや名前では確かめたことにならない (v0.1.22 には reconcile.rs が無い)。
git -C "$REPO" rev-parse "$TAG" > /dev/null 2>&1 || die "タグがありません: $TAG"
git -C "$REPO" cat-file -e "$TAG:src-tauri/src/reconcile.rs" 2>/dev/null \
  || die "$TAG に reconcile.rs がありません = 自動送信が入っていないビルドです"
note "タグ $TAG に自動送信あり ✅"

CACHE="$HERE/dist/_release/$TAG"
mkdir -p "$CACHE"
need_dl=0
[ "$TARGET" = "mac" ] || { [ -f "$CACHE/gse-next.exe" ] && [ -f "$CACHE/gse-submit.exe" ] || need_dl=1; }
[ "$TARGET" = "win" ] || { ls "$CACHE"/*.dmg > /dev/null 2>&1 || need_dl=1; }
if [ "$need_dl" -eq 1 ]; then
  note "リリース成果物を取得します ($TAG)"
  ( cd "$CACHE" && gh release download "$TAG" --repo mikotomiura/GSE-prototype --clobber \
      --pattern 'gse-next.exe' --pattern 'gse-submit.exe' --pattern '*.dmg' ) \
    || die "gh release download に失敗しました"
fi

# --- 6. 組む -----------------------------------------------------------------
OUT="$HERE/dist/$SUBJECT"
mkdir -p "$OUT"

build_win() {
  local W="$OUT/G1_実施用_Windows"
  mkdir -p "$W"
  cp "$CACHE/gse-next.exe" "$CACHE/gse-submit.exe" "$W/"
  cp "$HERE/launch-g1-windows.bat" "$W/"
  cp "$REPO/src-tauri/resources/pubkey.txt" "$W/"
  cp "$CONFIG" "$W/g1-submit.json"
  : > "$W/g1.mode"                       # ★ 0 バイトで正しい
  cp "$PAGES_DIR"/block*.html "$W/"
  # ⚠️★ 配るバイナリに自動送信が入っているかを **実体で** 確かめる。
  #   (タグの git 検査は「ソースにある」までしか言えない)
  if command -v strings > /dev/null 2>&1; then
    # ⚠️★ `strings | grep -q` にしてはならない。grep が最初の一致で終了 → strings が
    #   SIGPIPE で落ちる → `set -o pipefail` がパイプライン失敗と見なし、
    #   ★ **一致しているのに「見つからない」と判定する**（実測で踏んだ）。
    #   → 全部読み切る `grep -c` で数える。
    local n
    n=$(strings -a "$W/gse-submit.exe" | grep -c -- 'reconcile' || true)
    [ "${n:-0}" -gt 0 ] \
      || die "gse-submit.exe に reconcile が見当たりません (古いビルドの可能性)"
    note "gse-submit.exe の実体に reconcile あり ✅ ($n 箇所)"
  else
    note "⚠️ strings が無いので実体検査を飛ばしました (★ 飛ばしたことを記録に残すこと)"
  fi
  note "Windows: $(find "$W" -type f | wc -l | tr -d ' ') ファイル"
}

build_mac() {
  local M="$OUT/G1_実施用_macOS"
  local DMG
  DMG=$(basename "$(ls "$CACHE"/*.dmg | head -1)")
  # ⚠️★ **先に消す。** 2026-08-07 に踏んだ: dmg の同梱をやめたのに、前回の実行で置いた
  #   dmg がフォルダに残り続け、★ **配布物に「取り出してください」の残骸**が混ざった。
  #   dist/ は毎回作り直してよい生成物なので、積み上げない。
  rm -rf "$M"
  mkdir -p "$M"
  cp "$CONFIG" "$M/g1-submit.json"
  : > "$M/g1.mode"
  cp "$PAGES_DIR"/block*.html "$M/"

  # --- ★★ `.app` を **最初からフォルダに入れて**配る（2026-08-07） ---------------
  # ⚠️★★ **なぜ dmg を配るのをやめたか（実測で踏んだ事故）**
  #   旧版は dmg を同梱し、README で「`.app` をこのフォルダへドラッグしてください」と頼んでいた。
  #   ★ 2026-08-07、**README を書いた本人**が dmg から直接起動し、G1 モードにならず
  #     **プローブが発火した**（`~/.gse/g1_participant_id` が作られず、通常モードの
  #     自動生成 ID が使われていたことで確定）。⚠️ 在宅の被験者なら確実に起きる。
  #   ★ マーカーは実行ファイルから **4 階層上**の 1 か所しか見ない (`g1.rs: exe_to_folder_levels`)。
  #     dmg から起動すると `/Volumes/…` を見るので、フォルダの `g1.mode` は**あっても効かない**。
  #   ⚠️ アプリは何の警告も出さずに普通に動く。これが最も悪い性質である。
  #   ⚠️ ★ **macOS の launcher で解決してはならない** — `open -a` は名前解決して
  #     `/Applications` の通常アプリを起こすため 2026-08-05 に**廃止済み**
  #     (`preregistration.md §5.4-5`・`launch-g1-macos.command` に理由が残っている)。
  #   → ★ **ドラッグという工程そのものを無くす。** `§5.4-5` の凍結された配布形
  #     （`g1.mode` と `gse-next.app` と `blockNN.html` が同居する `G1-app/`）と一致する。
  #
  # ⚠️★ **署名に触らない**（`§5.4-5`: 中身は 1 バイトも変えない）。`ditto` で取り出して
  #   `ditto -c -k` で固めるだけである。2026-08-07 に往復を実測した:
  #     dmg 内 → コピー後 → zip → 展開後 の 4 点すべてで `codesign --verify --strict` が OK、
  #     実行ビットも `-rwxr-xr-x` のまま。
  local MNT
  MNT=$(mktemp -d)
  # ⚠️★ 途中で失敗してもマウントを残さない（残すと次回の attach が別名になって気づけない）
  trap 'hdiutil detach "$MNT" -quiet 2>/dev/null || true; rmdir "$MNT" 2>/dev/null || true' RETURN
  hdiutil attach "$CACHE/$DMG" -mountpoint "$MNT" -nobrowse -quiet \
    || die "dmg をマウントできませんでした: $DMG"
  [ -d "$MNT/gse-next.app" ] || die "dmg の中に gse-next.app がありません"
  # ★ 配る実体の署名を、取り出す前に確かめる（壊れた成果物を配らない）
  codesign --verify --strict "$MNT/gse-next.app" \
    || die "dmg 内の gse-next.app の署名が壊れています"
  ditto "$MNT/gse-next.app" "$M/gse-next.app" || die "gse-next.app を取り出せませんでした"
  hdiutil detach "$MNT" -quiet || true
  trap - RETURN
  rmdir "$MNT" 2>/dev/null || true

  # ★ フォルダに置いた状態でもう一度確かめる（`g1.mode` を同居させても署名は無傷であること）
  codesign --verify --strict "$M/gse-next.app" \
    || die "フォルダへ置いた gse-next.app の署名が壊れました"

  sed "s/@DMG@/$DMG/g" "$HERE/dist-readme-macos.txt" > "$M/README_先に読む.txt"

  # ★★ 初回セットアップスクリプト（preregistration.md 第 13 版 §2.14）。
  #   ⚠️ 手打ちの `xattr` を置き換える。研究者が同席して 1 回だけ実行する。
  #   ★ ドラッグして実行するので**パスを 1 文字も打たない**。
  #   ⚠️ quarantine が付いていても `bash <パス>` なら動く（2026-08-08 実測）。
  cp "$HERE/初回セットアップ_mac.sh" "$M/" || die "初回セットアップ_mac.sh を入れられません"
  bash "$M/初回セットアップ_mac.sh" --selftest > /dev/null \
    || die "★ 初回セットアップ_mac.sh の自己検査が赤い。壊れたものを配らない"

  # --- ★ 配るのは **zip 1 個**。⚠️ フォルダのままだと Drive が固め直して .app が壊れうる -----
  #   ★ zip なら Drive は**ただのファイル**として配るので、バイトが変わらない。
  local Z="$OUT/G1_実施用_macOS.zip"
  rm -f "$Z"
  ( cd "$OUT" && ditto -c -k --sequesterRsrc --keepParent "G1_実施用_macOS" "$(basename "$Z")" ) \
    || die "zip を作れませんでした"
  note "macOS: $(find "$M" -type f | wc -l | tr -d ' ') ファイル + gse-next.app（★ 同梱済み）"
  note "macOS zip: $(basename "$Z") ($(wc -c < "$Z" | tr -d ' ') B) ← ★ Drive にはこれを置く"
}

case "$TARGET" in
  win) build_win ;;
  mac) build_mac ;;
  both) build_win; build_mac ;;
esac

# --- 7. 照合表（★ Drive へ上げたあとに突き合わせる） --------------------------
MAN="$OUT/MANIFEST.txt"
{
  echo "# G1 配布物 — 被験者 $SUBJECT / タグ $TAG"
  echo "# 生成元 commit: $(git -C "$REPO" rev-parse --short HEAD)"
  echo "# ⚠️ サイズ一致は同一の証明にならない。実機で SHA-256 を突き合わせること:"
  echo "#     Windows: certutil -hashfile <file> SHA256"
  echo "#     macOS  : shasum -a 256 <file>"
  echo
  for d in "$OUT"/G1_実施用_*; do
    [ -d "$d" ] || continue
    echo "## $(basename "$d")"
    ( cd "$d" && for f in *; do
        if [ -d "$f" ]; then
          # ⚠️★ `.app` は**ディレクトリ**である。`wc -c < dir` は 0 を返すので、
          #   そのまま出すと **「0 B」= 空に見える**（2026-08-07 に実測で踏んだ）。
          #   → 中のファイルの合計 byte 数と、★ **署名の検証結果**を出す。
          printf '%-34s %10d B  %s (%s ファイル)\n' "$f/" \
            "$(find "$f" -type f -exec wc -c {} + | tail -1 | awk '{print $1}')" \
            "$(codesign --verify --strict "$f" > /dev/null 2>&1 && echo 'codesign OK' || echo '⚠️ codesign NG')" \
            "$(find "$f" -type f | wc -l | tr -d ' ')"
        else
          printf '%-34s %10d B  %s\n' "$f" "$(wc -c < "$f" | tr -d ' ')" "$(shasum -a 256 "$f" | cut -c1-16)"
        fi
      done )
    echo
  done
} > "$MAN"

echo
note "できました: $OUT"
sed 's/^/    /' "$MAN"
echo "[make-distribution] ⚠️ g1-submit.json はシークレットを含みます。共有範囲に注意してください。"
