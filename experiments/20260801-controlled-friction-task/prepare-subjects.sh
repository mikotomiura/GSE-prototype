#!/usr/bin/env bash
# 被験者 **複数人ぶん** の割付と課題ページをまとめて用意し、Drive へドラッグする形に並べる。
#
# 使い方:
#   ./prepare-subjects.sh --range P001 P015     # 範囲
#   ./prepare-subjects.sh P003 P007 P012        # 任意の集合
#
# 出力:
#   blocks/<ID>.json          … 割付（★ 既に有れば **触らない**）
#   pages/<ID>/blockNN.html   … 課題ページ（割付から決まる生成物・毎回作り直す）
#   dist/_drive/<ID>/         … ★ **Drive へドラッグするのはここ**（課題ページだけが入る）
#   dist/<ID>/_upload/        … 照合表 (manifest.tsv) と base64
#
# ============================================================================
# ⚠️★★ このスクリプトが **やらないこと**（意図的）
# ============================================================================
#
#   1. ★ **既存の `blocks/<ID>.json` を上書きしない。**
#      実施後の `blocks/<ID>.json` には `file` / `produced_chars` /
#      `manipulation_check_answers` が **書き足されている**（`blocks/README.md`）。
#      ⚠️ 再生成して上書きすると、**測定値が黙って消える**。
#      → 既に有れば読み飛ばし、整合は `validate_blocks.py` に判定させる
#        （★ あれが「条件・題材 ID・課題文パスが assign.py の決定的出力と一致するか」を見る単一の真実源）。
#
#   2. ★ **アプリを組まない。** アプリは全員共通の zip で配る (`make-common-app-zip.sh`)。
#      ⚠️ 課題ページを共通側に入れてはならない (`decisions.md` D-1)。ここは**課題ページ専用**である。
#
#   3. ★ **Drive へ上げない。** 上げるのは人（ドラッグ）。ここは「上げる物を並べる」までである。
#      ⚠️ 上げたあとの照合は `verify-drive-upload.py`。★ 照合が緑になるまでリンクを配らない。
#
# ============================================================================
# ⚠️★ 2026-08-07 に踏んだ罠
# ============================================================================
#   `python3 assign.py --subject P001` **だけでは `blocks/P001.json` は作られない**
#   （印刷用の表を標準出力に出すだけ）。★ `--json` が要る。
#   → ここでは **一時ファイルに出して JSON として読めることを確かめてから** 置く。
#     ⚠️ `> blocks/<ID>.json` に直接リダイレクトすると、失敗しても**空ファイルが残る**。

set -euo pipefail
shopt -s nullglob
cd "$(dirname "$0")"

HERE="$(pwd)"

die() { echo "[prepare-subjects] ✗ $*" >&2; exit 1; }
note() { echo "[prepare-subjects] $*"; }

# --- 引数 -------------------------------------------------------------------
SUBJECTS=()
if [ "${1:-}" = "--range" ]; then
  [ $# -eq 3 ] || die "--range は開始と終了の 2 つを取ります。例: --range P001 P015"
  START="$2"; END="$3"
  for v in "$START" "$END"; do
    [[ "$v" =~ ^P[0-9]{3}$ ]] || die "被験者 ID の形が違います: $v （P001 のような形）"
  done
  s=$((10#${START#P})); e=$((10#${END#P}))
  [ "$s" -le "$e" ] || die "範囲が逆です: $START > $END"
  # ⚠️★ 打ち間違い（--range P001 P999）で数百人ぶん回さない。
  [ $((e - s + 1)) -le 50 ] || die "範囲が広すぎます（$((e - s + 1)) 人）。50 人までにしてください"
  for ((i = s; i <= e; i++)); do SUBJECTS+=("$(printf 'P%03d' "$i")"); done
elif [ $# -gt 0 ]; then
  for v in "$@"; do
    [[ "$v" =~ ^P[0-9]{3}$ ]] || die "被験者 ID の形が違います: $v （P001 のような形）"
    SUBJECTS+=("$v")
  done
else
  sed -n '1,10p' "$0"; exit 1
fi

# ⚠️★ 同じ ID を 2 回渡されたら止める（後段の照合が「余分」を出して原因を取り違えさせる）
DUP=$(printf '%s\n' "${SUBJECTS[@]}" | sort | uniq -d | tr '\n' ' ')
[ -z "$DUP" ] || die "同じ被験者 ID が重複しています: $DUP"

[ -f "$HERE/SEED" ] || die "SEED がありません（★ 割付の根拠なので無いまま進めない）"
note "対象 ${#SUBJECTS[@]} 人: ${SUBJECTS[*]}"
echo

# --- 1. 割付（★ 無い人だけ作る。有る人は触らない） ----------------------------
MADE=0; KEPT=0
for ID in "${SUBJECTS[@]}"; do
  B="$HERE/blocks/$ID.json"
  if [ -f "$B" ]; then
    KEPT=$((KEPT + 1))
    note "割付 $ID: 既にあります（★ 上書きしません）"
    continue
  fi
  TMP="$(mktemp)"
  # ⚠️★ `--json` が要る。無いと表が出て、下の JSON 検査で落ちる。
  if ! python3 assign.py --subject "$ID" --json > "$TMP" 2>/tmp/g1-assign-err.$$; then
    sed 's/^/    /' /tmp/g1-assign-err.$$ >&2 || true
    rm -f "$TMP" /tmp/g1-assign-err.$$
    die "assign.py が失敗しました: $ID"
  fi
  rm -f /tmp/g1-assign-err.$$
  # ★ 置く前に「読める JSON で、その被験者のもので、ブロックが入っている」ことを確かめる。
  python3 - "$TMP" "$ID" <<'PY' || { rm -f "$TMP"; exit 1; }
import json, sys
path, sid = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(path, encoding="utf-8"))
except Exception as e:
    sys.exit(f"[prepare-subjects] ✗ assign.py の出力が JSON ではありません（--json を付け忘れていませんか）: {e}")
if d.get("subject") != sid:
    sys.exit(f"[prepare-subjects] ✗ subject が {d.get('subject')!r} です（{sid} のはず）")
n = len(d.get("blocks") or [])
if n == 0:
    sys.exit("[prepare-subjects] ✗ blocks が空です")
PY
  mv "$TMP" "$B"
  chmod 644 "$B"
  MADE=$((MADE + 1))
  note "割付 $ID: 作りました"
done
echo
note "割付: 新規 $MADE 人 / 既存 $KEPT 人"

# --- 2. 転記の整合（★ 赤なら 1 枚も作らない） ---------------------------------
# ⚠️ `validate_blocks.py` は blocks/ 全体を見る。★ ここが「割付が assign.py の決定的出力と
#   一致するか」を判定する単一の真実源であり、上書き禁止の裏返しでもある。
if ! python3 validate_blocks.py > /tmp/g1-validate.$$ 2>&1; then
  sed 's/^/    /' /tmp/g1-validate.$$ >&2
  rm -f /tmp/g1-validate.$$
  die "validate_blocks.py が通らないので課題ページを作りません"
fi
rm -f /tmp/g1-validate.$$
note "割付の整合 ✅"
echo

# --- 3. 課題ページ（★ 毎回作り直す。⚠️ 古い枚数が残らないよう入れ替える） ------
# ⚠️ `build_task_pages.py` は出力先を消さない。★ 10 ブロック → 8 ブロックに変えたときに
#   block09/10 が居残ると、**配布物に古い割付が混ざる**。→ 一時ディレクトリに作って差し替える。
for ID in "${SUBJECTS[@]}"; do
  WANT=$(python3 -c "import json,sys;print(len(json.load(open(sys.argv[1],encoding='utf-8'))['blocks']))" "$HERE/blocks/$ID.json")
  TMPD="$(mktemp -d)"
  python3 build_task_pages.py --subject "$ID" --out "$TMPD" > /dev/null \
    || { rm -rf "$TMPD"; die "build_task_pages.py が失敗しました: $ID"; }
  GOT=$(find "$TMPD/$ID" -maxdepth 1 -name 'block*.html' 2>/dev/null | wc -l | tr -d ' ')
  [ "$GOT" -eq "$WANT" ] \
    || { rm -rf "$TMPD"; die "$ID: 課題ページが $GOT 枚しかありません（割付は $WANT ブロック）"; }
  rm -rf "$HERE/pages/$ID"
  mkdir -p "$HERE/pages"
  mv "$TMPD/$ID" "$HERE/pages/$ID"
  rm -rf "$TMPD"
  note "課題ページ $ID: $GOT 枚 ✅"
done
echo

# --- 4. ★ Drive へドラッグする置き場（課題ページ **だけ**） -------------------
# ⚠️★ `pages/` を直接ドラッグさせない。★ `pages/` には PILOT-win / PILOT-mac が居るので、
#   全選択でドラッグすると **パイロットの割付が被験者に配られる**。
#   → 今回の対象だけを並べた専用の置き場を作る。
#
# ⚠️★★ フォルダ名は **`G1課題文_<P-ID>`** である（2026-08-07 に実 Drive の名前へ合わせた）。
#   ★ GAS 側 (`Form_G1/GSE_G1_Form_Builder.gs` の `g1MaterialsFolderNames_`) が
#     「`P006`」と「`G1課題文_P006`」の **完全一致 2 通りだけ**を認める。
#   ⚠️ ここを勝手に変えると、GAS がフォルダを見つけられず **受付メールが黙って 2 便運用に落ちる**
#     （壊れないので気づきにくい）。★ 変えるなら両方を同時に直すこと。
DRIVE_PREFIX="G1課題文_"
DRIVE="$HERE/dist/_drive"
rm -rf "$DRIVE"
mkdir -p "$DRIVE"
for ID in "${SUBJECTS[@]}"; do
  mkdir -p "$DRIVE/${DRIVE_PREFIX}$ID"
  cp "$HERE/pages/$ID"/block*.html "$DRIVE/${DRIVE_PREFIX}$ID/"
done

# ⚠️★ シークレットや余計なものが紛れていないことを、**置いたあとの実体で**確かめる。
#   (`decisions.md` D-1: 被験者別フォルダに置いてよいのは課題ページだけ)
BAD=$(find "$DRIVE" -mindepth 1 ! -name 'block*.html' ! -type d | head -5)
[ -z "$BAD" ] || die "課題ページ以外が紛れています:
$BAD"
# ⚠️★ GAS が認める名前 (`g1MaterialsFolderNames_`) から 1 文字でも外れたら止める。
#   ★ ここが緩いと「上げたのに GAS が見つけられない」を配布まで持ち越す。
BADDIR=$(find "$DRIVE" -mindepth 1 -maxdepth 1 -type d ! -name "${DRIVE_PREFIX}P[0-9][0-9][0-9]" | head -5)
[ -z "$BADDIR" ] || die "GAS が認めない名前のフォルダがあります（${DRIVE_PREFIX}P0NN のはず）:
$BADDIR"
NDIR=$(find "$DRIVE" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
[ "$NDIR" -eq "${#SUBJECTS[@]}" ] \
  || die "フォルダが $NDIR 個です（${#SUBJECTS[@]} 人ぶんのはず）"
DEPTH=$(find "$DRIVE" -mindepth 2 -maxdepth 2 -type d | head -5)
[ -z "$DEPTH" ] || die "入れ子のフォルダがあります（★ 平らでなければならない）:
$DEPTH"
# ⚠️★ `${DRIVE}` と括る。★ bash は全角文字を**変数名の一部**として読むので、
#   `$DRIVE（` は `DRIVE（` という別の（存在しない）変数になり、`set -u` で落ちる（実測）。
note "ドラッグ用: ${DRIVE}（${#SUBJECTS[@]} フォルダ・課題ページのみ ✅）"

# --- 5. 照合表 ---------------------------------------------------------------
for ID in "${SUBJECTS[@]}"; do
  ./make-upload-manifest.sh --from-pages "$ID" > /dev/null \
    || die "照合表を作れませんでした: $ID"
done
note "照合表: dist/<ID>/_upload/manifest.tsv を ${#SUBJECTS[@]} 人ぶん ✅"
echo

# --- 6. ⚠️★ 被験者どうしが**取り違えても気づける**かを実測する -----------------
# ★ 課題ページには被験者 ID が入っていない（実測）。したがって Drive でフォルダを
#   取り違えて置いても、ページを見ただけでは分からない。
#   ⚠️ 唯一の番人は「照合表が被験者ごとに違う」ことである。同じなら**取り違えは検出できない**。
#   → 同一の照合表を持つ被験者がいれば、ここで**名指しで警告する**（★ 黙って進めない）。
python3 - "$HERE" "${SUBJECTS[@]}" <<'PY' || exit 1
import pathlib, sys
here = pathlib.Path(sys.argv[1])
subjects = sys.argv[2:]
# ⚠️★ 見るのは **名前 + byte 数** だけ。★ SHA-256 を混ぜてはならない。
#   Drive の一覧 (`search_files`) が返すのは `fileSize` であり、`verify-drive-upload.py` が
#   突き合わせられるのもそこまでである。★ SHA まで含めて「相異なる」と言うと、
#   **実際の検出力より強い保証を名乗る**ことになる（照合表は違うのに Drive では区別できない、が起きうる）。
sig = {}
for s in subjects:
    lines = (here / "dist" / s / "_upload" / "manifest.tsv").read_text(encoding="utf-8").strip().split("\n")
    key = tuple(tuple(l.split("\t")[:2]) for l in lines)
    sig.setdefault(key, []).append(s)
clashes = [v for v in sig.values() if len(v) > 1]
if clashes:
    print("[prepare-subjects] ⚠️★ 照合表が同一の被験者がいます（取り違えを byte 照合で検出できません）:")
    for c in clashes:
        print("    " + " = ".join(c))
    print("    ★ Drive へ置くときは 1 人ずつ、フォルダ名を読み上げて確かめてください。")
else:
    print(f"[prepare-subjects] 名前+byte 数は {len(subjects)} 人ぶんすべて相異なる ✅（Drive で取り違えても照合で捕まる）")
PY
echo

cat <<EOS
[prepare-subjects] ★ 次にやること（★ 上げるのは人）

  1. Finder で開く:
       open "$DRIVE"
  2. Drive の「G1_課題ページ_被験者別」フォルダを開き、**${#SUBJECTS[@]} 個のフォルダを丸ごと**ドラッグする。
     ⚠️ 親フォルダは**制限付き（非公開）**のままにすること (decisions.md D-7)。
  3. ★ **フォルダを 1 つずつ**「リンクを知っている全員（閲覧者）」にする。
     ⚠️ 親を共有にして継承させてはならない。1 回で**全被験者分が見える** = fail-open。
  4. 上げたあと、byte 照合が緑になるまで**リンクを配らない**:
       ./verify-drive-upload.py dist/<ID>/_upload/manifest.tsv <search_files の出力.json>
EOS
