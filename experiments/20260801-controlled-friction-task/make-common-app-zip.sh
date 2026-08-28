#!/usr/bin/env bash
# ★ **全員共通**のアプリ配布物を組む（Drive の「アプリダウンロードリンク」に置くもの）。
#
# 使い方:
#   ./make-common-app-zip.sh [--mode g1|o1] [--tag vX.Y.Z] [--config <g1-submit.json>]
#   → dist/_common/G1_実施用_macOS.zip   ← ★ Drive に置くのはこれ 1 個
#     dist/_common/G1_実施用_Windows.zip
#   ./make-common-app-zip.sh --selftest   # ★ macOS 無しでモード分岐だけ検査する
#
# ============================================================================
# ⚠️★★ `--mode` について（★ 既定は g1。⚠️ 引数を付けない呼び出しは**今までと同じ物**を作る）
# ============================================================================
#   g1 … G1 統制タスク実験（70 分・1 回きり）。マーカーは `g1.mode`。
#   o1 … ★ O1 (R3-a) ふだんの作業の長期記録（数日〜数週間・常時記録）。マーカーは `o1.mode`。
#
#   ⚠️★★★ **README を流用しない。** G1 は「70 分の 1 回きりのセッション」、
#     O1 は「実業務の常時記録」であり、被験者がやることが違う
#     （O1 には課題ページが無く、代わりに**毎日の自動起動**が要る）。
#   ⚠️★ O1 の被験者向け文面は **まだ研究者の承認を受けていない**（`【ドラフト・未承認】`）。
#     ★ 本スクリプトは承認の有無を判定できないので、**警告を出して続行**する
#       （止めると配布物を作って検算することすらできなくなる）。
#
#   ⚠️★★★ **`g1-submit.json` はファイル名を変えない。** O1 でも `g1-submit.json` のままである。
#     ★ 行き先は中身（endpoint / secret）で決まる（`Form_G1/GSE_O1_Submit.gs` 配備手順 6）。
#     ⚠️ 名前を変えると端末側（`submission.rs`）が読めなくなる。
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
# ★ 自分自身の絶対パス。⚠️ `$0` のままだと selftest が自分を呼べない
#   （`cd` 済みなので `$0` は "make-common-app-zip.sh" になり、PATH から探されて失敗する）。
SELF="$HERE/$(basename "$0")"
TAG="v0.1.24"
CONFIG="$REPO/g1-submit.json"
MODE=g1
SELFTEST=0
SELFTEST_DUMP=0

die() { echo "[make-common-app-zip] ✗ $*" >&2; exit 1; }
note() { echo "[make-common-app-zip] $*"; }

while [ $# -gt 0 ]; do
  case "$1" in
    # ⚠️★ 値なしで渡されたときに `shift 2` を踏むと、`set -e` で**出力ゼロの exit 1**になり
    #   原因が画面に出ない（★ `sync-session.sh` と同じ形にする）。
    --mode)   [ $# -ge 2 ] || die "--mode に値がありません（g1 か o1）"; MODE="$2"; shift 2 ;;
    --tag)    [ $# -ge 2 ] || die "--tag に値がありません"; TAG="$2"; shift 2 ;;
    --config) [ $# -ge 2 ] || die "--config に値がありません"; CONFIG="$2"; shift 2 ;;
    --selftest) SELFTEST=1; shift ;;
    # ★ selftest が子プロセスとして呼ぶ内部フラグ（同梱ファイルの一覧を出して終わる）。
    --selftest-dump) SELFTEST_DUMP=1; shift ;;
    -h|--help) sed -n '1,60p' "$0"; exit 0 ;;
    *) die "知らない引数: $1" ;;
  esac
done

# --- 0. モードごとの持ち物（★ ここが単一の真実源）------------------------------
# ⚠️★ 「どのファイルを入れるか」を 1 か所にまとめる。★ 散らすと片方のモードだけ
#   直して**もう片方に古いものが残る**（このプロジェクトが繰り返している事故の型）。
case "$MODE" in
  g1)
    LABEL="G1"
    MAC_README_SRC="$HERE/dist-readme-macos.txt"
    WIN_README_SRC=""                       # ★ G1 の Windows には README を入れていない（従来どおり）
    WIN_LAUNCHER_SRC="$HERE/launch-g1-windows.bat"
    WIN_LAUNCHER_DST="launch-g1-windows.bat"
    ;;
  o1)
    LABEL="O1"
    MAC_README_SRC="$HERE/dist-readme-macos-o1.txt"
    WIN_README_SRC="$HERE/dist-readme-windows-o1.txt"
    WIN_LAUNCHER_SRC="$HERE/launch-o1-windows.bat"
    # ★ 被験者がダブルクリックするもの。⚠️ README の【1】【3】と**同じ名前**であること
    #   （下の検査が突き合わせる）。
    WIN_LAUNCHER_DST="GSE_起動.bat"
    ;;
  *)
    die "--mode は g1 か o1 です（受け取った値: '$MODE'）"
    ;;
esac

# ★ macOS の README が**被験者を守る文言**を落としていないことを機械で確かめる（下の検査で使う）。
#   ⚠️★ 表記ゆれで検査が空回りしないよう、**README 側の文言をこの表に合わせる**こと
#     （2026-08-08 に「壊れてはいません」と書いて grep が 0 件になった）。
#   ★ 共通の 4 語は Gatekeeper の経路が同じなので O1 でも必要である。
# ⚠️★★ **配列で持つ**（code-reviewer 指摘・2026-08-28）。
#   ★ 旧版は `|` 区切りの文字列を `IFS='|'` + **クォート無し展開**で回していた。
#     ⚠️ 冒頭で `shopt -s nullglob` が有効なので、将来 `*` `?` `[` を含む語
#     （例:「[注意]」）を足すと **その語が黙って消えて検査が空振りする**。
#     ★ このファイル自身が繰り返し警戒している「見えないまま緑になる」経路そのもの。
README_MUST_COMMON=( "研究者と一緒に" "壊れていません" "ゴミ箱に入れないで" "ターミナルの窓へドラッグ" )
# ⚠️★ O1 固有。★ 「毎日動いていること」と「いつでも止められること」が落ちると、
#   O1 は (a) 記録が空の日ができ (b) 同意文書 §4 の約束が配布物から消える。
README_MUST_O1=( "自動的に立ち上がる" "すぐ止められます" "時間帯を指定して削除" "記録していません" "48 時間" )
README_MUST_NOT=( "右クリック" "開発元を確認できません" )

# ★ 内部ダンプ: このモードで同梱するファイルの実パスを 1 行ずつ出す。
#   ⚠️ ★ ここが `--selftest` の 1 番の検査対象である（★ 表と実体のずれを捕まえる）。
if [ "$SELFTEST_DUMP" -eq 1 ]; then
  printf '%s\n' "$MAC_README_SRC" "$WIN_LAUNCHER_SRC" "$HERE/初回セットアップ_mac.sh" \
                "$REPO/src-tauri/resources/pubkey.txt"
  [ -n "$WIN_README_SRC" ] && printf '%s\n' "$WIN_README_SRC"
  exit 0
fi

# ⚠️★ O1 の被験者向け文面は未承認である。★ 黙って配布物にしない。
readme_draft_warn () {
  [ "$MODE" = o1 ] || return 0
  if grep -q "【ドラフト・未承認】" "$MAC_README_SRC" 2>/dev/null; then
    note "⚠️★★ O1 の README はまだ **ドラフト（未承認）** です。研究者の承認まで被験者に配らないこと。"
  fi
}

# --- 0b. ★ selftest（⚠️ macOS が無い機械で「モード分岐が壊れていないか」だけ測る）------
#   ⚠️ ★ 限界を隠さない: ここで測れるのは **持ち物の表と README の文言**だけである。
#     `ditto` / `hdiutil` / `codesign` を要する工程は 1 つも実行していない。
#     ★ したがって「selftest が緑 = 配布物が作れる」ではない。
if [ "$SELFTEST" -eq 1 ]; then
  sp=0; sf=0
  ok_()  { echo "  ✅ $*"; sp=$((sp+1)); }
  ng_()  { echo "  ❌ $*"; sf=$((sf+1)); }
  echo "=== make-common-app-zip --selftest（★ モード分岐と README 文言だけ）==="

  # 1. 両モードの持ち物が実在するか
  for m in g1 o1; do
    out=$(bash "$SELF" --mode "$m" --selftest-dump 2>/dev/null) || { ng_ "$m: 持ち物を取り出せない"; continue; }
    missing=""
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      [ -f "$f" ] || missing="$missing $f"
    done <<< "$out"
    if [ -z "$missing" ]; then ok_ "$m: 同梱するファイルが全部ある"; else ng_ "$m: 無いファイル:$missing"; fi
  done

  # 2. ⚠️ 知らないモードは受け付けない
  if bash "$SELF" --mode g2 --selftest-dump > /dev/null 2>&1; then
    ng_ "知らない --mode を受け付けてしまう"
  else
    ok_ "知らない --mode を拒否する"
  fi

  # 3. README の文言（★ 共通 4 語）
  for m in g1 o1; do
    case "$m" in
      g1) r="$HERE/dist-readme-macos.txt" ;;
      o1) r="$HERE/dist-readme-macos-o1.txt" ;;
    esac
    miss=""
    for p in "${README_MUST_COMMON[@]}"; do
      grep -q "$p" "$r" 2>/dev/null || miss="$miss 「$p」"
    done
    if [ -z "$miss" ]; then ok_ "$m: macOS README に共通の 4 語がある"; else ng_ "$m: 欠けている語:$miss"; fi
  done

  # 4. ★ O1 固有の語（★ G1 の README には**無くてよい**ことも測る = 流用の検出）
  miss=""
  for p in "${README_MUST_O1[@]}"; do
    grep -q "$p" "$HERE/dist-readme-macos-o1.txt" 2>/dev/null || miss="$miss 「$p」"
  done
  if [ -z "$miss" ]; then ok_ "o1: macOS README に O1 固有の語がある"; else ng_ "o1: 欠けている語:$miss"; fi

  miss=""
  for p in "${README_MUST_O1[@]}"; do
    grep -q "$p" "$HERE/dist-readme-windows-o1.txt" 2>/dev/null || miss="$miss 「$p」"
  done
  if [ -z "$miss" ]; then ok_ "o1: Windows README に O1 固有の語がある"; else ng_ "o1: 欠けている語:$miss"; fi

  # 5. ⚠️ 旧版の案内が戻っていないこと
  for r in "$HERE/dist-readme-macos.txt" "$HERE/dist-readme-macos-o1.txt"; do
    bad=""
    for p in "${README_MUST_NOT[@]}"; do
      ! grep -q "$p" "$r" 2>/dev/null || bad="$bad 「$p」"
    done
    if [ -z "$bad" ]; then ok_ "$(basename "$r"): 旧版の案内が無い"; else ng_ "$(basename "$r"): 旧版が残っている:$bad"; fi
  done

  # 6. ★★ README が案内する launcher 名と、実際に入れる名前が一致するか
  #    ⚠️ ずれると被験者は**存在しないファイルを探す**（★ 実害が出るのは配った後）。
  if grep -q "GSE_起動.bat" "$HERE/dist-readme-windows-o1.txt" 2>/dev/null; then
    ok_ "o1: Windows README の launcher 名が配布物と一致する（GSE_起動.bat）"
  else
    ng_ "o1: Windows README が案内する launcher 名が配布物と食い違う"
  fi

  # 7. ⚠️★★★ マーカーを取り違えていないこと（★ 両方入ると lib.rs が起動を拒否する）
  if grep -q ': > "$M/o1.mode"' "$SELF" && grep -q ': > "$M/g1.mode"' "$SELF"; then
    ok_ "両モードのマーカー書き出しが別々に存在する"
  else
    ng_ "マーカーの書き出しが見つからない（★ ゲートの検査対象でもある）"
  fi

  # 7b. ⚠️★★ **同梱しない物を「入っているもの」に書かない**（security-checker 指摘・2026-08-28）。
  #     ★ macOS の配布物に `pubkey.txt` は入らない（鍵は `.app` の中）。⚠️ 書いてあると
  #       被験者は無いファイルを探し、「消さないでください」と言われた物が最初から無い状態になる。
  #     ★ Windows には**入る**ので、そちらは書いてあるのが正しい（★ 非対称を検査で固定する）。
  if grep -q "pubkey.txt" "$HERE/dist-readme-macos-o1.txt"; then
    ng_ "o1: macOS README が pubkey.txt を挙げている（★ macOS 配布物には入らない）"
  else
    ok_ "o1: macOS README が同梱しない pubkey.txt を挙げていない"
  fi
  if grep -q "pubkey.txt" "$HERE/dist-readme-windows-o1.txt"; then
    ok_ "o1: Windows README が同梱する pubkey.txt を挙げている"
  else
    ng_ "o1: Windows README に pubkey.txt が無い（★ Windows 配布物には入る）"
  fi

  # 8. ★ O1 の README がドラフトであることを明示しているか（★ 承認前配布の抑止）
  if grep -q "【ドラフト・未承認】" "$HERE/dist-readme-macos-o1.txt" \
     && grep -q "【ドラフト・未承認】" "$HERE/dist-readme-windows-o1.txt"; then
    ok_ "o1: README が未承認であることを明示している"
  else
    ng_ "o1: README にドラフト表示が無い（★ 承認済みならこの検査を外すこと）"
  fi

  echo
  echo "  selftest: 通過 $sp 件 / 失敗 $sf 件"
  if [ "$sf" -eq 0 ]; then
    echo "  ✅ モード分岐と文言は健全（⚠️ ★ dmg / 署名 / zip は 1 つも実行していない）"
    exit 0
  fi
  echo "  ❌ 上の ❌ を直すこと。"
  exit 1
fi

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
# ⚠️★★★ **`rm -rf "$OUT"` にしない**（code-reviewer 指摘・2026-08-28）。
#   ★ `dist/_common` は**両モード共通**なので、まるごと消すと
#     `--mode o1` を回した瞬間に **さっき作った G1 の zip 2 本が黙って消える**。
#   ⚠️ 末尾の「できました:」は `"$OUT"/*.zip` を列挙するので O1 の 2 本しか出ず、
#     **G1 が消えたことが画面に出ない**。★ G1 は実施中であり、実害になる。
#   → ★ **自分のモードの生成物だけ**を消す。
mkdir -p "$OUT"
rm -rf "${OUT:?}/${LABEL}_実施用_"*

# --- 3. macOS（★ .app 同梱・課題ページ無し） ---------------------------------
readme_draft_warn
M="$OUT/${LABEL}_実施用_macOS"
mkdir -p "$M"
DMG=$(basename "$(ls "$CACHE"/*.dmg | head -1)")
cp "$CONFIG" "$M/g1-submit.json"   # ⚠️★ O1 でも名前は g1-submit.json のまま（中身で行き先が決まる）
# ⚠️★★★ マーカーは**モードごとに literal で書く**。★ 変数にまとめない:
#   `scripts/check-o1-release-readiness.sh` が「`o1.mode` を**書き出す文**があるか」を
#   grep で検査しており、変数にすると検査から見えなくなる（★ 緑にならないのではなく
#   **見えないまま緑になる**経路を作らないため、あえて 2 行に分ける）。
# ⚠️★★★ **両方あるときアプリは止まらない。** `lib.rs` は `tracing::error!` を 1 行出したうえで
#   ★ **G1 を勝たせて起動する**（`o1::resolve`。⚠️ 理由: G1 の 1 ブロックは事後除外できない）。
#   → ⚠️ O1 の配布物に `g1.mode` が混ざると、被験者の端末は **黙って G1 として動く**:
#     「開始する」を押すまで記録されず、日次ローテートも自動提出も動かない。
#     ⚠️★ **その日のデータは丸ごと取れないのに、画面上は何も壊れて見えない。**
#   ★ だから配布物の側で 1 つだけ置き、下の検査でもう片方の不在を確かめる。
if [ "$MODE" = o1 ]; then
  : > "$M/o1.mode"
else
  : > "$M/g1.mode"
fi
sed "s/@DMG@/$DMG/g" "$MAC_README_SRC" > "$M/README_先に読む.txt"

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

( cd "$OUT" && ditto -c -k --sequesterRsrc --keepParent "${LABEL}_実施用_macOS" "${LABEL}_実施用_macOS.zip" ) \
  || die "macOS の zip を作れません"
# ⚠️★ `--sequesterRsrc` は AppleDouble (`._*`) を撒かない代わりに `__MACOSX/` へ集める。
#   ★ 集めただけで消えてはいないので、配る前に取り除く（2026-08-23 実測: 51 エントリ中 25 件が混入）。
zip -d "$OUT/${LABEL}_実施用_macOS.zip" "__MACOSX/*" > /dev/null \
  || die "macOS zip から __MACOSX を除去できません"

# --- 4. Windows（★ 日本語ファイル名の文字化けを避けるため、こちらも zip で配る） ----
# ⚠️ Windows に実行ビットの問題は無いが、Drive の「フォルダをダウンロード」で
#   日本語名が化ける経路がある (memory: participant-launcher-encoding)。★ zip で固めて配る。
W="$OUT/${LABEL}_実施用_Windows"
mkdir -p "$W"
cp "$CACHE/gse-next.exe" "$CACHE/gse-submit.exe" "$W/"
cp "$WIN_LAUNCHER_SRC" "$W/$WIN_LAUNCHER_DST" || die "launcher を入れられません: $WIN_LAUNCHER_SRC"
# ★ O1 だけ Windows にも README を入れる（★ 自動起動の手順が要る・研究者判断 2026-08-28）。
#   ⚠️ G1 は従来どおり入れない（★ G1 は対面で読み上げるため）。
if [ -n "$WIN_README_SRC" ]; then
  cp "$WIN_README_SRC" "$W/README_先に読む.txt" || die "Windows の README を入れられません"
fi
cp "$REPO/src-tauri/resources/pubkey.txt" "$W/"
cp "$CONFIG" "$W/g1-submit.json"   # ⚠️★ O1 でも名前は g1-submit.json のまま
# ⚠️★★★ macOS 側と同じ理由で literal で書く（★ ゲートの grep から見えるようにする）。
if [ "$MODE" = o1 ]; then
  : > "$W/o1.mode"
else
  : > "$W/g1.mode"
fi
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
"$REPO/scripts/make-participant-zip.sh" "$W" "$OUT/${LABEL}_実施用_Windows.zip" > /dev/null \
  || die "Windows の zip を作れません"

# --- 5. 展開して確かめる（★ 配る前に、配る物そのものを検査する） -----------------
V=$(mktemp -d)
ditto -x -k "$OUT/${LABEL}_実施用_macOS.zip" "$V" || die "macOS zip を展開できません"
codesign --verify --strict "$V/${LABEL}_実施用_macOS/gse-next.app" || die "展開後に署名が壊れています"
[ -x "$V/${LABEL}_実施用_macOS/gse-next.app/Contents/MacOS/gse-next" ] || die "展開後に実行ビットが落ちています"
# ⚠️★★★ **正しいマーカーが 1 つだけ**入っていること。
#   ★ 「あるか」だけでなく「**もう片方が無いか**」も見る —— 両方あると
#     `lib.rs` は起動を拒否する（"BOTH g1.mode and o1.mode are present"）。
if [ "$MODE" = o1 ]; then
  [ -f "$V/${LABEL}_実施用_macOS/o1.mode" ] || die "展開後に o1.mode がありません"
  [ ! -f "$V/${LABEL}_実施用_macOS/g1.mode" ] || die "⚠️ O1 の配布物に g1.mode が混ざっています（★ G1 が勝ち、O1 として記録されません）"
else
  [ -f "$V/${LABEL}_実施用_macOS/g1.mode" ] || die "展開後に g1.mode がありません"
  [ ! -f "$V/${LABEL}_実施用_macOS/o1.mode" ] || die "⚠️ G1 の配布物に o1.mode が混ざっています（★ 取り違えの証拠。配らない）"
fi

# ★★ 初回セットアップスクリプトが**展開後も動く**こと（2026-08-08）。
#   ⚠️ 同梱しただけでは足りない。⚠️ zip 越しに壊れていないかは**展開して走らせないと分からない**。
[ -f "$V/${LABEL}_実施用_macOS/初回セットアップ_mac.sh" ] || die "展開後に 初回セットアップ_mac.sh がありません"
bash "$V/${LABEL}_実施用_macOS/初回セットアップ_mac.sh" --selftest > /dev/null \
  || die "展開後の 初回セットアップ_mac.sh が自己検査に落ちました"

# ★★ README が**被験者を守る 3 文**を落としていないこと（2026-08-08）。
#   ⚠️ ★ 「壊れていません」「ゴミ箱に入れないで」が無いと、被験者は
#      「壊れているため開けません」を見て **本当にゴミ箱に入れてしまう**（取り返しがつかない）。
#   ⚠️ ★ 表記ゆれで検査が空回りしないよう、**README 側の文言をこの検査に合わせる**こと
#      （2026-08-08 に「壊れてはいません」と書いて grep が 0 件になった）。
R="$V/${LABEL}_実施用_macOS/README_先に読む.txt"
for phrase in "${README_MUST_COMMON[@]}"; do
  grep -q "$phrase" "$R" || die "README に「${phrase}」がありません（★ 被験者を守る文言・§2.14 第 13 版）"
done
# ⚠️ 旧版（A 型ダイアログ向け）の案内が戻っていないこと。★ B 型では効かない。
for phrase in "${README_MUST_NOT[@]}"; do
  ! grep -q "$phrase" "$R" || die "README に旧版の案内「${phrase}」が残っています（★ B 型では効かない）"
done

# ⚠️★★★ O1 固有の文言（★ 落ちると (a) 記録が空の日ができ (b) 同意文書 §4 の
#   約束が配布物から消える）。★ Windows 側の README も**同じ表で**検査する。
if [ "$MODE" = o1 ]; then
  # ⚠️★★ **macOS と Windows の README を両方見る**（code-reviewer 指摘・2026-08-28）。
  #   ★ 旧版は変数名こそ `RW` だったが中身は macOS の README で、
  #     **同じファイルを 2 度検査していた**。⚠️ O1 は Windows が主ターゲットであり、
  #     自動起動の手順（`shell:startup`）が落ちても誰も気づかない状態だった。
  #   ★ `$W` は zip 化前の実体なのでここでまだ読める。
  for R_O1 in "$V/${LABEL}_実施用_macOS/README_先に読む.txt" "$W/README_先に読む.txt"; do
    [ -f "$R_O1" ] || die "O1 の README がありません: $R_O1"
    for phrase in "${README_MUST_O1[@]}"; do
      grep -q "$phrase" "$R_O1" || die "O1 の README に「${phrase}」がありません: $(basename "$(dirname "$R_O1")")"
    done
    # ⚠️★ 「G1 の文面を流用していないか」を機械で見る。★ O1 に課題ページは無い。
    for phrase in "課題のページ" "block01.html"; do
      ! grep -q "$phrase" "$R_O1" || die "⚠️ O1 の README に G1 の文面（${phrase}）が混ざっています"
    done
  done
fi

rm -rf "$V"

# ★ macOS zip 自体にも余計なものが無いことを機械で確かめる（Windows 側と対称の検査）。
#   ⚠️ `--sequesterRsrc` は __MACOSX/ へ集めるだけで消さない。`zip -d` 後にここで確定させる。
python3 - "$OUT/${LABEL}_実施用_macOS.zip" <<'PY' || exit 1
import sys, zipfile
p = sys.argv[1]
names = zipfile.ZipFile(p).namelist()
junk = [n for n in names if "__MACOSX" in n or n.endswith("/.DS_Store") or n == ".DS_Store"]
if junk:
    sys.exit(f"[make-common-app-zip] ✗ macOS zip に余計なものが入っています: {junk[:3]}")
print(f"[make-common-app-zip] macOS: 余計なもの無し ✅ ({len(names)} エントリ)")
PY

note "macOS: 展開して検査 ✅（署名 / 実行ビット / ${MODE}.mode / セットアップ自己検査 / README 文言 / __MACOSX 不在）"

# ★ Windows zip は「Windows で化けないこと」を機械で確かめる。
#   ⚠️ 目で見て判断しない（macOS の unzip は化けて見えても Windows では正しいことがある）。
python3 - "$OUT/${LABEL}_実施用_Windows.zip" "$LABEL" <<'PY' || exit 1
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
if not any(n.startswith(f"{sys.argv[2]}_実施用_Windows/") for n in names):
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
