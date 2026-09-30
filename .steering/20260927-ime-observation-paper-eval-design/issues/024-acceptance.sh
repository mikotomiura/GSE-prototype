#!/usr/bin/env bash
# issue 024 acceptance — 公開 repo への書き出し
# ★ 2026-09-30 に判断 67（絶対パスの規則）・68（測定用のロガーは書き出しからビルド・機械によらずバイト一致）・
#   69（逐語コピーの文字列リテラルを対訳表で英訳）に合わせて書き直した。
# ★ 2026-09-30 追補 2（判断 74〜76・main への merge の前の /cross-review 1 巡目）: 書き出し器は *.internal.* に改名して
#   公開しない（74）・書き出しの最後に _style_check.py を回す（75）・角括弧の被験者 ID も止める（76）・(a)〜(k) の陰性対照。
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
X="${K}/export/export.internal.py"
SC="$(cd "$(dirname "$0")" && pwd)/_style_check.py"
SRC="papers/ime-observation"

echo "[024] 公開 repo への書き出し"
for f in "${X}" "${K}/export/README.internal.md" "${K}/export/translations.internal.json" "${SRC}/CITATION.cff" "${SRC}/.zenodo.json"; do need_file "${f}"; done
for f in "${K}/export/export.py" "${K}/export/README.md"; do
  if [ ! -e "${f}" ]; then ok "判断 74: 旧名が無い: ${f}"; else ng "判断 74: 旧名が残っている: ${f}"; fi
done
selftest_ok "${X}"
# ★ ケース名は英語（判断 36）。逐語コピーはコメントを除き、日本語の文字列は対訳で置き換えて書き出す（判断 69）。
while IFS= read -r c; do
  [ -n "${c}" ] && need_grep "${X}" "${c}" "AC2 selftest ケース: ${c}"
done <<'CASES'
a participant identifier stops the export
an email address stops the export
a bracketed participant identifier stops the export
an internal marker word stops the export
comments are stripped from manifest-listed sources
internal fields are dropped from the public manifest
internal notes are not exported
a real home directory stops the export
a named user path stops the export
a fictional name on the allow list passes
line endings are normalized to LF
non-ASCII string literals are replaced from the translation table
an untranslated string literal stops the export
an untracked or modified file in a git checkout stops the export
a secret file name stops the export
a file name is checked like its content
an absolute path token with a user component stops the export
a link that leaves the source stops the export
an escaped spelling in JSON is checked after unescaping
git that cannot be run inside a work tree stops the export
a modified or linked translation table stops the export
an unreadable directory stops the export
a tracked file that was not collected stops the export
a file flagged as unchanged in the index stops the export
secret-looking content stops the export
a doubled separator does not hide a user path
a user path after a colon or inside a URL stops the export
the host name stops the export
the word check is skipped only for corpus data files
a name with internal outside the internal form stops the export
only files starting with a shebang are made executable
an output path inside the work tree stops the export
a style violation in the output stops the export
a missing or failing style checker stops the export
secret-looking content in the converted output stops the export
a mixed or dotted separator does not hide a user path
a web URL path is not a user path
a compiler flag does not hide a user path
git that reports no repository under a .git stops the export
a style checker that is not committed stops the export
a file type that the style checker does not read stops the export
a file in the corpus data other than a jsonl stops the export
the output appears only after every check passed
a secret-looking directory name stops the export
a deleted tracked translation table stops the export
CASES
if grep -qF "a bracketed reference number passes" "${X}"; then ng "判断 76: 旧ケース（角括弧の番号を通す）が残っている"; else ok "判断 76: 旧ケース（角括弧の番号を通す）が無い"; fi
run_ok "AC .zenodo.json が JSON" "${PY}" -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8'))" "${SRC}/.zenodo.json"
run_ok "AC 判断 69: 対訳表が JSON で entries を持つ" "${PY}" -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); assert isinstance(d.get('entries'),list) and d['entries']" "${K}/export/translations.internal.json"

# ---- AC3 / AC4 / AC5: 実物を書き出す（2 回）
run_ok "AC3 実物を書き出せる（試験モード）" "${PY}" "${X}" --out "${TMP}/e1" --allow-missing-license
run_ok "AC3 実物を書き出せる（2 回目）" "${PY}" "${X}" --out "${TMP}/e2" --allow-missing-license
if [ -f "${TMP}/e1/kit/logger/manifest.json" ]; then ok "AC3 manifest.json がある"; else ng "AC3 manifest.json が無い"; fi
BAD="$(cd "${TMP}/e1" 2>/dev/null && find . \( -name '*.jsonl' -o -name '*.ndjson' -o -name '*.internal.*' -o -name '*.zip' -o -name '.DS_Store' \
  -o -type d \( -name target -o -name sealed -o -name runs -o -name .build -o -name __pycache__ \) \) -print | grep -v '^\./kit/corpus/data/[^/]*\.jsonl$' || true)"
if [ -d "${TMP}/e1" ] && [ -z "${BAD}" ]; then ok "AC3 生ログ・生成物・内部の記録が無い"; else ng "AC3 除外されていない: $(echo "${BAD}" | tr '\n' ' ')"; fi
if [ -d "${TMP}/e1" ] && [ ! -e "${TMP}/e1/kit/export" ]; then ok "AC8c 判断 74: 書き出しに kit/export/ が無い（書き出し器は公開しない）"; else ng "AC8c 判断 74: 書き出しに kit/export/ がある、または書き出しが無い"; fi
if [ -f "${TMP}/e1/README.md" ] && ! grep -rqF "kit/export" "${TMP}/e1"; then ok "AC8c 判断 74: 書き出しの全体に kit/export が無い"; else ng "AC8c 判断 74: 書き出しに kit/export がある、または README が無い: $(grep -rlF "kit/export" "${TMP}/e1" 2>/dev/null | head -n 3 | tr '\n' ' ')"; fi
if [ -f "${TMP}/e1/kit/logger/check_manifest.py" ] && (cd "${TMP}/e1" && "${PY}" kit/logger/check_manifest.py --self >/dev/null 2>&1); then
  ok "AC4 書き出した側で check_manifest.py --self が緑"
else ng "AC4 書き出した側で manifest が照合できない"; fi
KEYS_PY='import glob,json,os,sys
d=sys.argv[1]; bad=[]; ms=sorted(glob.glob(os.path.join(d,"kit","logger","manifest*.json")))
if not ms: bad.append("no manifest")
for p in ms:
    m=json.load(open(p,encoding="utf-8"))
    if sorted(m.keys())!=["entries"]: bad.append("%s: top-level keys %s"%(os.path.basename(p),sorted(m.keys())))
    for e in m.get("entries",[]):
        extra=set(e)-{"kind","id","path","symbol","sha256","reason"}
        if extra: bad.append("%s: %s has %s"%(os.path.basename(p),e.get("id"),sorted(extra)))
print("; ".join(bad[:5])); sys.exit(1 if bad else 0)'
if [ -d "${TMP}/e1" ] && "${PY}" -c "${KEYS_PY}" "${TMP}/e1" > "${TMP}/keys.out" 2>&1; then
  ok "AC4 公開側の manifest の欄が kind / id / path / symbol / sha256 / reason だけ・最上位が entries だけ"
else ng "AC4 公開側の manifest に余分な欄がある（$(tail -n 1 "${TMP}/keys.out")）"; fi
if [ -d "${TMP}/e1" ] && ! grep -rqE '"(gse_|upstream_)' "${TMP}/e1/kit/logger/" 2>/dev/null; then ok "AC 判断 36: 公開側の manifest に出どころの欄が無い"; else ng "AC 判断 36: 公開側の manifest に出どころの欄が残っている"; fi
# ★ 判断 36: 書き出した全体に禁止語・地の文の日本語が無い（逐語コピーもコメントを除いた後なので対象）
if [ -d "${TMP}/e1" ] && "${PY}" "${SC}" --root "${TMP}/e1" . > "${TMP}/style-e1.out" 2>&1; then
  ok "AC9 判断 36: 書き出した全体が公開物の書き方に合う"
else ng "AC9 判断 36: 書き出した側に違反がある（$(tail -n 1 "${TMP}/style-e1.out" 2>/dev/null)・例: $(head -n 2 "${TMP}/style-e1.out" 2>/dev/null | tr '\n' ' ')）"; fi
# ★ 判断 69: 書き出した逐語コピーの範囲は ASCII だけ（コメントは除かれ、日本語の文字列は対訳で置き換わる）
ASCII_PY='import glob,json,os,sys
d=os.path.join(sys.argv[1],"kit","logger"); bad=[]; n=0
for p in sorted(glob.glob(os.path.join(d,"manifest*.json"))):
    for e in json.load(open(p,encoding="utf-8"))["entries"]:
        if e["kind"] not in ("file","excerpt"): continue
        ls=open(os.path.join(d,e["path"]),encoding="utf-8").read().split("\n")
        if e["kind"]=="excerpt":
            b=[i for i,l in enumerate(ls) if l.rstrip()=="// @excerpt-begin "+e["id"]]; x=[i for i,l in enumerate(ls) if l.rstrip()=="// @excerpt-end "+e["id"]]
            if len(b)!=1 or len(x)!=1: bad.append("%s: markers of %s"%(e["path"],e["id"])); continue
            rng=range(b[0]+1,x[0])
        else: rng=range(len(ls))
        for i in rng:
            n+=1
            if any(ord(ch)>127 for ch in ls[i]): bad.append("%s:%d"%(e["path"],i+1))
if n==0: bad.append("no verbatim lines were checked")
print("; ".join(bad[:5])+(" (%d)"%len(bad) if bad else "")); sys.exit(1 if bad else 0)'
if [ -d "${TMP}/e1" ] && "${PY}" -c "${ASCII_PY}" "${TMP}/e1" > "${TMP}/ascii.out" 2>&1; then
  ok "AC8b 判断 69: 書き出した逐語コピーの範囲に ASCII 以外の文字が無い"
else ng "AC8b 判断 69: 書き出した逐語コピーの範囲に ASCII 以外の文字がある（$(tail -n 1 "${TMP}/ascii.out")）"; fi
# ★ 判断 36 / 69: 写した元のファイル名（公開物に無いファイル）を書き出しに残さない（例 ime_cloak.rs のコンパイル時の assert の訳）
UP_HITS=""
if [ -d "${TMP}/e1" ]; then
  # ★ 追補 2 (l): 語として探す（run_logger.rs の中の logger.rs に当てない）・書き出しに実在するファイル名は除く
  for n in lib.rs ime_windows.rs hook_windows.rs hook_macos.rs anonymize.rs capabilities.rs logger.rs schema_dto.rs; do
    [ -n "$(find "${TMP}/e1" -name "${n}" -print 2>/dev/null | head -n 1)" ] && continue
    grep -rqwF "${n}" "${TMP}/e1" 2>/dev/null && UP_HITS="${UP_HITS} ${n}"
  done
fi
if [ -d "${TMP}/e1" ] && [ -z "${UP_HITS}" ]; then ok "AC8b 判断 69: 写した元のファイル名が書き出しに無い"; else ng "AC8b 判断 69: 写した元のファイル名が書き出しにある:${UP_HITS}"; fi
if [ -d "${TMP}/e1" ] && [ -z "$(find "${TMP}/e1" -name '*.internal.*' -print)" ]; then ok "AC 判断 36 / 43 / 69: *.internal.*（対訳表を含む）が無い"; else ng "AC 判断 36 / 43 / 69: *.internal.* が書き出されている"; fi
LIST_PY='import hashlib,os,sys
r=sys.argv[1]; out=[]
for d,ds,fs in os.walk(r):
    for f in fs:
        p=os.path.join(d,f); rel=os.path.relpath(p,r).replace(os.sep,"/")
        out.append((rel.encode("utf-8"), rel+" "+hashlib.sha256(open(p,"rb").read()).hexdigest()))
sys.stdout.buffer.write("".join(x[1]+"\n" for x in sorted(out)).encode("utf-8"))'
# ★ 2026-09-30: 一覧はバイトで書く。テキストの stdout だと Windows の Python が改行を CRLF にし、
#   下の「別の機械と比べる」値だけが機械によって変わっていた（中身は一致していた・B13）。
list () { "${PY}" -c "${LIST_PY}" "$1"; }
L1="$( [ -d "${TMP}/e1" ] && list "${TMP}/e1" )"
if [ -n "${L1}" ] && [ "${L1}" = "$( [ -d "${TMP}/e2" ] && list "${TMP}/e2" )" ]; then ok "AC5 2 回の書き出しがバイト一致"; else ng "AC5 書き出しが無い、または 2 回が一致しない"; fi
if [ -d "${TMP}/e1" ] && [ -z "$(grep -rlI "$(printf '\r')" "${TMP}/e1" 2>/dev/null)" ]; then ok "AC5 判断 68: 書き出しのテキストに CR が無い"; else ng "AC5 判断 68: CR を含むファイルがある: $(grep -rlI "$(printf '\r')" "${TMP}/e1" 2>/dev/null | head -n 3 | tr '\n' ' ')"; fi
# ★ 判断 68: 別の機械の acceptance と同じ commit で比べる値（一致しなければ機械に依存する内容が混ざっている）
case "${L1}" in *"$(printf '\r')"*) ng "AC5 判断 68: 一覧そのものに CR がある（比べる値が機械に依存する・B13）" ;; esac
[ -n "${L1}" ] && echo "  ℹ️ 書き出しの一覧の SHA-256（別の機械と比べる）: $(printf '%s\n' "${L1}" | "${PY}" -c "import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())")（$(printf '%s\n' "${L1}" | wc -l | tr -d ' ') ファイル）"

# ---- AC6: ライセンスが無ければ止まる・既存の書き出し先を消さない
run_exit 2 "AC6 ライセンスが無ければ exit 2（★ 公開の前）" "${PY}" "${X}" --out "${TMP}/e3"
if [ ! -e "${TMP}/e3" ]; then ok "AC6 止まったときに書き出し先が残らない"; else ng "AC6 止まったのに書き出し先が残っている"; fi
run_exit 2 "AC6 既にある書き出し先は exit 2" "${PY}" "${X}" --out "${TMP}/e1" --allow-missing-license
if [ -n "${L1}" ] && [ "${L1}" = "$(list "${TMP}/e1")" ]; then ok "AC6 既にある書き出し先の中身は変わらない"; else ng "AC6 既にある書き出し先の中身が変わった"; fi

# ---- AC7: 書き出した側が動く（コメントの除去・文字列の置き換えが字句を壊さない）
if command -v cargo >/dev/null 2>&1; then
  run_ok "AC7 書き出した側で cargo test --locked（ロガー）が緑" env CARGO_TARGET_DIR="${TMP}/cargo-target" cargo test --locked --manifest-path "${TMP}/e1/kit/logger/Cargo.toml"
else ng "AC7 cargo が無い（書き出した側のテストを回せない）"; fi
if command -v rustfmt >/dev/null 2>&1; then
  RF_BAD=""; RF_N=0
  while IFS= read -r f; do
    RF_N=$((RF_N + 1))
    rustfmt --edition 2021 --emit stdout "${f}" >/dev/null 2>&1 || RF_BAD="${RF_BAD} ${f#"${TMP}"/e1/}"
  done <<EOF_RS
$(find "${TMP}/e1" -name '*.rs' -type f | LC_ALL=C sort)
EOF_RS
  if [ "${RF_N}" -gt 1 ] && [ -z "${RF_BAD}" ]; then ok "AC7 書き出したすべての *.rs（${RF_N} 本・別の OS の専用ファイルを含む）を rustfmt が構文解析できる"
  else ng "AC7 rustfmt が構文解析できない *.rs がある、または対象が無い（${RF_N} 本）:${RF_BAD}"; fi
else ng "AC7 rustfmt が無い（別の OS の専用ファイルの構文を確かめられない）"; fi
run_ok "AC7 書き出した側で kit/check.sh が緑" env PYTHONDONTWRITEBYTECODE=1 bash "${TMP}/e1/kit/check.sh"
# ★ 追補 2 (j): 実行権限は #!/ で始まるファイルだけ（POSIX で。Windows では実行権限の印を持たない）
case "$(uname -s 2>/dev/null)" in
  Darwin|Linux)
    XRS="$(find "${TMP}/e1" -name '*.rs' -type f -perm -u+x -print 2>/dev/null | head -n 3)"
    XSH="$(find "${TMP}/e1" -name '*.sh' -type f -perm -u+x -print 2>/dev/null | head -n 1)"
    if [ -d "${TMP}/e1" ] && [ -z "${XRS}" ] && [ -n "${XSH}" ]; then ok "AC8c (j) *.rs に実行権限が無く、*.sh にはある"
    else ng "AC8c (j) 実行権限が #!/ の規則と違う（*.rs: ${XRS:-なし}・*.sh: ${XSH:-なし}）"; fi ;;
  *) echo "  ℹ️ AC8c (j) 実行権限の検査は POSIX だけ（この OS では飛ばす）" ;;
esac

# ---- AC8: 実物の写しで秘匿の検査が効く（陰性対照）。★ 写しは git の外に作る（export.py は git に依存しない）
COPY_PY='import shutil,sys; shutil.copytree(sys.argv[1], sys.argv[2], ignore=shutil.ignore_patterns("target","__pycache__",".build","runs","sealed"))'
mkcopy () { rm -rf "${TMP}/c-$1"; "${PY}" -c "${COPY_PY}" "${SRC}" "${TMP}/c-$1/papers/ime-observation"; }
XC="kit/export/export.internal.py"
cx () { local n="$1"; shift; "${PY}" "${TMP}/c-${n}/papers/ime-observation/${XC}" --out "${TMP}/o-${n}" --allow-missing-license --style-check "${SC}" "$@"; }
mkcopy p0
run_ok "AC8 陽性対照: 混ぜない写しは書き出せる" cx p0
# judge <期待する終了コード> <名前> <出力にあるべきファイル名> <説明>  ★ cx の結果を判定する（異常終了・書き出し先の残り・ファイル名）
judge () {
  local want="$1" name="$2" fname="$3" d="$4" rc="$5"
  if [ "${rc}" -ne "${want}" ]; then ng "AC8 ${d}（exit ${rc}・期待 ${want}）"
  elif grep -qE "Traceback|can't open file|No such file" "${TMP}/neg-${name}.out"; then ng "AC8 ${d}（拒否ではなく異常終了）"
  elif [ -e "${TMP}/o-${name}" ]; then ng "AC8 ${d}（止まったのに書き出し先が残っている）"
  elif ! grep -qF "${fname}" "${TMP}/neg-${name}.out"; then ng "AC8 ${d}（当たったファイル名 ${fname} が出力に無い）"
  else ok "AC8 ${d}"; fi
}
# neg <名前> <写しの中のファイル> <足す 1 行> <説明> [export.py に足す引数...]
neg () {
  local name="$1" rel="$2" line="$3" d="$4" rc
  shift 4
  mkcopy "${name}"
  printf '%s\n' "${line}" >> "${TMP}/c-${name}/papers/ime-observation/${rel}"
  cx "${name}" "$@" > "${TMP}/neg-${name}.out" 2>&1; rc=$?
  judge 1 "${name}" "$(basename "${rel}")" "${d}" "${rc}"
}
# newf <期待する終了コード> <名前> <写しに足すファイル> <中身> <説明>
newf () {
  local want="$1" name="$2" rel="$3" body="$4" d="$5" rc
  mkcopy "${name}"
  printf '%s\n' "${body}" > "${TMP}/c-${name}/papers/ime-observation/${rel}"
  cx "${name}" > "${TMP}/neg-${name}.out" 2>&1; rc=$?
  judge "${want}" "${name}" "$(basename "${rel}")" "${d}" "${rc}"
}
neg pid "README.md" "Session recorded by P017." "被験者 ID を混ぜると exit 1"
# ★ 追補（2026-09-30・レビュー）: `_` は被験者 ID の境界（P017_windows・run_P017）
neg pid2 "kit/pilot/README.md" "Raw logs such as P017_windows were removed." "追補: P017_windows（_ 続き）を混ぜると exit 1"
# ★ 判断 71: 絶対パスの字句の中の Users / home の成分の次の成分を名前として照合する
neg fileurl "kit/e3/README.md" "The trace is at file:///Users/zed/notes.txt for reference." "判断 71: file:///Users/<名> を混ぜると exit 1"
neg unc "kit/refinput-windows/README.md" 'The canonical path was \\?\C:\Users\zed\work.' "判断 71: \\\\?\\C:\\Users\\<名> を混ぜると exit 1"
neg nonascii "kit/e2/README.md" "Data were copied from /Users/山田/work." "判断 71: ASCII でない名前の /Users/<名> を混ぜると exit 1"
newf 1 fname "experiment/notes-P017.md" "Notes for one session." "追補: 名前に被験者 ID を持つファイルを足すと exit 1"
newf 2 secret "experiment/.env" "API_KEY=placeholder" "判断 70: 秘密の名前の型（.env）のファイルがあれば exit 2"
mkcopy short
cx short --also-user mk > "${TMP}/neg-short.out" 2>&1; rc=$?
if [ "${rc}" -eq 2 ] && ! grep -qE "Traceback" "${TMP}/neg-short.out" && [ ! -e "${TMP}/o-short" ]; then ok "AC8 追補: --also-user が 2 文字なら exit 2（黙って捨てない）"
else ng "AC8 追補: --also-user が 2 文字でも止まらない（exit ${rc}）"; fi
# ★ 判断 70: 写しを一時的な git repo にする（★ 作業中の repo ではない）。clean なら通り、追跡していないファイル・変更で exit 2
mkcopy git
G="${TMP}/c-git"
if git -C "${G}" init -q >/dev/null 2>&1 && git -C "${G}" add papers >/dev/null 2>&1 \
   && git -C "${G}" -c user.name=acceptance -c user.email=acceptance@example.invalid -c commit.gpgsign=false commit -q -m base >/dev/null 2>&1; then
  run_ok "AC8 判断 70: 陽性対照: clean な git の写しは書き出せる" cx git
  rm -rf "${TMP}/o-git"
  printf '%s\n' "A draft note." > "${G}/papers/ime-observation/kit/draft-note.md"
  cx git > "${TMP}/neg-git.out" 2>&1; rc=$?
  judge 2 git "draft-note.md" "判断 70: git の写しに追跡していないファイルがあれば exit 2" "${rc}"
  rm -f "${G}/papers/ime-observation/kit/draft-note.md"
  rm -rf "${TMP}/o-git"   # ★ 前の試行が（直す前の成果物で）書き出してしまった場合に、次の判定へ波及させない
  printf '%s\n' "An uncommitted line." >> "${G}/papers/ime-observation/kit/gen/README.md"
  cx git > "${TMP}/neg-git.out" 2>&1; rc=$?
  judge 2 git "README.md" "判断 70: git の写しで追跡中のファイルに未コミットの変更があれば exit 2" "${rc}"
else ng "AC8 判断 70: 陰性対照の準備（一時的な git repo）に失敗した"; fi
HOME_NATIVE="$("${PY}" -c "import os; print(os.path.expanduser('~'))")"
neg home "experiment/notes.md" "Output was written under ${HOME_NATIVE}/work." "書き出す機械のホームディレクトリを混ぜると exit 1"
if [ -f "${TMP}/neg-home.out" ] && grep -qF "${HOME_NATIVE}/work" "${TMP}/neg-home.out"; then ng "AC8 当たった値（混ぜた行の中身）が出力に出ている"; else ok "AC8 当たった値（混ぜた行の中身）を出力に出さない"; fi
# ★ 上のホームは「名前つきの形」の規則にも当たる（C:\Users\<名> / /Users/<名>）。実在の値の規則だけを切り分けるため、
#   形の規則に当たらない値を --also-home / --also-user で渡して止まること、渡さなければ通ることを確かめる。
#   ⚠️ 値は `/` で始めない（Windows の git-bash は `/opt/...` のような引数を `C:/Program Files/Git/opt/...` に書き換えて
#   python に渡すので、混ぜた行と一致しなくなる —— 2026-09-30 に試作で実測）。ドライブ文字の形は書き換えられない。
neg alsohome "experiment/env.md" 'Data were kept in Z:\lab\zed-home\runs.' "--also-home で渡した値を混ぜると exit 1（形の規則に当たらない値）" --also-home 'Z:\lab\zed-home'
rm -rf "${TMP}/o-alsohome"
run_ok "AC8 陽性対照: 同じ写しでも --also-home を渡さなければ通る" cx alsohome
neg alsouser "kit/emit/README.md" "Prepared by zedlogin for the pilot." "--also-user で渡したログイン名を混ぜると exit 1" --also-user zedlogin
rm -rf "${TMP}/o-alsouser"
run_ok "AC8 陽性対照: 同じ写しでも --also-user を渡さなければ通る" cx alsouser
neg named "kit/formats/FORMATS.md" "An example path: /Users/zed/work/x." "一覧に無い名前の /Users/<名> を混ぜると exit 1"
neg steer "kit/run/README.md" "See .steering/notes for details." "逐語コピーでないファイルの .steering/ を混ぜると exit 1"
neg word "kit/gen/README.md" "This generator is part of GSE." "語としての GSE を混ぜると exit 1"
# ★ 判断 69: 逐語コピーに対訳の無い日本語のリテラルを足す。写しの manifest を直して、元の側の照合（--self）は緑にしておく
#   （★ 止まる理由が「manifest の食い違い」ではなく「対訳が無い」であることを確かめるため）。
mkcopy untr
LD="${TMP}/c-untr/papers/ime-observation/kit/logger"
printf '%s\n' 'const _UNTRANSLATED_FOR_ACCEPTANCE: &str = "対訳の無い文";' >> "${LD}/src/input/ime_mode.rs"
FIX_PY='import glob,json,os,sys
d=sys.argv[1]; sys.path.insert(0,d); import check_manifest as c
for p in sorted(glob.glob(os.path.join(d,"manifest*.json"))):
    raw=open(p,"rb").read(); m=json.loads(raw.decode("utf-8")); hit=False
    for e in m["entries"]:
        if e.get("path")=="src/input/ime_mode.rs":
            e["sha256"]=c.sha(c.copy_bytes(d,e)); hit=True
    if hit:
        open(p,"w",encoding="utf-8",newline="\n").write(json.dumps(m,ensure_ascii=False,indent=2)+"\n")'
if "${PY}" -c "${FIX_PY}" "${LD}" >/dev/null 2>&1 && (cd "${LD}" && "${PY}" check_manifest.py --self >/dev/null 2>&1); then
  cx untr > "${TMP}/neg-untr.out" 2>&1; rc=$?
  if [ "${rc}" -eq 1 ] && ! grep -qE "Traceback" "${TMP}/neg-untr.out" && [ ! -e "${TMP}/o-untr" ] && grep -qF "ime_mode.rs" "${TMP}/neg-untr.out"; then
    ok "AC8 判断 69: 逐語コピーの対訳の無い日本語のリテラルで exit 1"
  else ng "AC8 判断 69: 対訳の無いリテラルで止まらない（exit ${rc}・$(tail -n 2 "${TMP}/neg-untr.out" | tr '\n' ' ')）"; fi
else ng "AC8 判断 69: 陰性対照の準備（写しの manifest の直し）に失敗した"; fi

# ---- AC8c: 追補 2（判断 74〜76・decisions.md の (a)〜(k)）の陰性対照（2026-09-30・main への merge の前）
neg brpid "kit/e2/README.md" "Sessions [P017, P021] were excluded." "判断 76: 角括弧の被験者 ID を混ぜると exit 1"
neg dblsep "kit/e3/README.md" "The trace was under /Users//zed/work." "(f) 連続する区切りの /Users//<名> を混ぜると exit 1"
neg colon "kit/pilot/README.md" "Copied with scp from zed@labhost:/home/zed/data." "(f) : の直後の /home/<名> を混ぜると exit 1"
neg url "kit/formats/FORMATS.md" "A mirror is at https://host/C:/Users/zed/x for reference." "(f) URL の path の C:/Users/<名> を混ぜると exit 1"
HOST_NATIVE="$("${PY}" -c "import socket; print(socket.gethostname().split('.')[0])")"
if [ "${#HOST_NATIVE}" -ge 3 ]; then neg host "experiment/env.md" "Measured on ${HOST_NATIVE} last week." "(g) 書き出す機械のホスト名を混ぜると exit 1"
else echo "  ℹ️ (g) ホスト名が 3 文字未満なので飛ばす"; fi
neg styleja "experiment/notes.md" "パイロットの結果はここに書く。" "判断 75: 地の文の日本語を混ぜると exit 1（書き出しの最後の検査）"
if [ -f "${TMP}/neg-styleja.out" ] && grep -qF "パイロットの結果" "${TMP}/neg-styleja.out"; then ng "判断 75: 当たった値（日本語の文）が出力に出ている"; else ok "判断 75: 当たった値（日本語の文）を出力に出さない"; fi
neg styleref "kit/run/README.md" "This was settled in decision 72." "判断 75: 内部の番号を混ぜると exit 1"
neg stylerel "kit/gen/README.md" "The upstream copy is identical." "判断 75: 関係の語を混ぜると exit 1"
mkcopy corpus
mkdir -p "${TMP}/c-corpus/papers/ime-observation/kit/corpus/data"
printf '%s\n' "Built for GSE." > "${TMP}/c-corpus/papers/ime-observation/kit/corpus/data/notes.md"
cx corpus > "${TMP}/neg-corpus.out" 2>&1; rc=$?
# ★ 追補 3 (d): kit/corpus/data/ の下は直下の *.jsonl だけ（それ以外は検査の道具が読まないので exit 2）
judge 2 corpus "notes.md" "(h)(d) kit/corpus/data/ の .jsonl でないファイルで exit 2" "${rc}"
newf 2 tokentxt "experiment/zenodo_token.txt" "placeholder" "(e) 秘密の名前の型（*token*.txt）で exit 2"
newf 2 idrsa "kit/id_rsa" "placeholder" "(e) 秘密の名前の型（id_rsa）で exit 2"
AGEK="$(printf '%s%s%s' 'AGE-SEC' 'RET-KEY-' '1')$(printf 'Q%.0s' $(seq 1 58))"
newf 2 agekey "experiment/keys.md" "The key is ${AGEK} here." "(e) 秘密鍵に見える中身で exit 2"
if [ -f "${TMP}/neg-agekey.out" ] && grep -qF "QQQQQQQQ" "${TMP}/neg-agekey.out"; then ng "(e) 当たった値（鍵に見える中身）が出力に出ている"; else ok "(e) 当たった値（鍵に見える中身）を出力に出さない"; fi
newf 2 intname "kit/notes_internal.md" "Notes." "(i) .internal. の形でない internal を語として含む名前で exit 2"
# 判断 75: 検査の道具が無ければ exit 2（git の無い写しは既定の場所を引けない・明示した道具が無い）
mkcopy nosc
"${PY}" "${TMP}/c-nosc/papers/ime-observation/${XC}" --out "${TMP}/o-nosc" --allow-missing-license > "${TMP}/neg-nosc.out" 2>&1; rc=$?
if [ "${rc}" -eq 2 ] && ! grep -q Traceback "${TMP}/neg-nosc.out" && [ ! -e "${TMP}/o-nosc" ]; then ok "AC8c 判断 75: git の無い写しで --style-check を省くと exit 2（黙って飛ばさない）"
else ng "AC8c 判断 75: 検査の道具を引けないのに止まらない（exit ${rc}）"; fi
rm -rf "${TMP}/o-nosc"   # ★ 直す前の版が 1 つ目で書き出した場合に、次の判定へ波及させない
"${PY}" "${TMP}/c-nosc/papers/ime-observation/${XC}" --out "${TMP}/o-nosc" --allow-missing-license --style-check "${TMP}/no-such-style-check.py" > "${TMP}/neg-nosc2.out" 2>&1; rc=$?
if [ "${rc}" -eq 2 ] && ! grep -q Traceback "${TMP}/neg-nosc2.out" && [ ! -e "${TMP}/o-nosc" ]; then ok "AC8c 判断 75: --style-check のファイルが無ければ exit 2"
else ng "AC8c 判断 75: --style-check のファイルが無いのに止まらない（exit ${rc}）"; fi
# ★ git の写し（2）: (a) git が PATH に無い・(b) 対訳表の変更・(d) assume-unchanged・(c) 読めない dir（POSIX）・(k) 作業ツリーの中の --out
mkcopy git2
G2="${TMP}/c-git2"
if git -C "${G2}" init -q >/dev/null 2>&1 && git -C "${G2}" add papers >/dev/null 2>&1 \
   && git -C "${G2}" -c user.name=acceptance -c user.email=acceptance@example.invalid -c commit.gpgsign=false commit -q -m base >/dev/null 2>&1; then
  run_ok "AC8c 陽性対照: clean な git の写し（2）は書き出せる" cx git2
  rm -rf "${TMP}/o-git2"
  PYX="$("${PY}" -c 'import sys; print(sys.executable)')"
  mkdir -p "${TMP}/nogit"
  env PATH="${TMP}/nogit" "${PYX}" "${G2}/papers/ime-observation/${XC}" --out "${TMP}/o-git2" --allow-missing-license --style-check "${SC}" > "${TMP}/neg-nogit.out" 2>&1; rc=$?
  if [ "${rc}" -eq 2 ] && ! grep -q Traceback "${TMP}/neg-nogit.out" && [ ! -e "${TMP}/o-git2" ]; then ok "AC8c (a) git の作業ツリーで git が PATH に無ければ exit 2"
  else ng "AC8c (a) git の作業ツリーなのに git が無くても止まらない（exit ${rc}）"; fi
  rm -rf "${TMP}/o-git2"
  env PATH="${TMP}/nogit" "${PYX}" "${TMP}/c-p0/papers/ime-observation/${XC}" --out "${TMP}/o-nogit-p0" --allow-missing-license --style-check "${SC}" > "${TMP}/pos-nogit.out" 2>&1; rc=$?
  if [ "${rc}" -eq 0 ]; then ok "AC8c (a) 陽性対照: git の無い写しは git が PATH に無くても書き出せる"
  else ng "AC8c (a) 陽性対照: git の無い写しが git 無しで書き出せない（exit ${rc}・$(tail -n 1 "${TMP}/pos-nogit.out")）"; fi
  printf '\n' >> "${G2}/papers/ime-observation/kit/export/translations.internal.json"
  cx git2 > "${TMP}/neg-git2.out" 2>&1; rc=$?
  judge 2 git2 "translations.internal.json" "(b) git の写しで対訳表に未コミットの変更があれば exit 2" "${rc}"
  git -C "${G2}" checkout -q -- papers/ime-observation/kit/export/translations.internal.json
  rm -rf "${TMP}/o-git2"
  git -C "${G2}" update-index --assume-unchanged papers/ime-observation/kit/gen/README.md
  printf '%s\n' "A hidden change." >> "${G2}/papers/ime-observation/kit/gen/README.md"
  cx git2 > "${TMP}/neg-git2.out" 2>&1; rc=$?
  judge 2 git2 "kit/gen/README.md" "(d) assume-unchanged の印を付けて変えたファイルがあれば exit 2" "${rc}"
  git -C "${G2}" update-index --no-assume-unchanged papers/ime-observation/kit/gen/README.md
  git -C "${G2}" checkout -q -- papers/ime-observation/kit/gen/README.md
  rm -rf "${TMP}/o-git2"
  # ★ 追補 3 (c): 元が git の作業ツリーなら、検査の道具も追跡済み・HEAD と一致でなければ exit 2（git の外の写しを渡す）
  cp "${SC}" "${TMP}/sc-loose.py"
  "${PY}" "${G2}/papers/ime-observation/${XC}" --out "${TMP}/o-git2" --allow-missing-license --style-check "${TMP}/sc-loose.py" > "${TMP}/neg-scloose.out" 2>&1; rc=$?
  if [ "${rc}" -eq 2 ] && ! grep -q Traceback "${TMP}/neg-scloose.out" && [ ! -e "${TMP}/o-git2" ]; then ok "AC8d (c) git の元で、追跡されていない検査の道具なら exit 2"
  else ng "AC8d (c) git の元で、追跡されていない検査の道具でも止まらない（exit ${rc}）"; fi
  rm -rf "${TMP}/o-git2"
  case "$(uname -s 2>/dev/null)" in
    Darwin|Linux)
      if [ "$(id -u)" != "0" ]; then
        chmod 000 "${G2}/papers/ime-observation/kit/gen"
        cx git2 > "${TMP}/neg-git2.out" 2>&1; rc=$?
        chmod 755 "${G2}/papers/ime-observation/kit/gen"
        judge 2 git2 "gen" "(c) 読めない dir があれば exit 2" "${rc}"
        rm -rf "${TMP}/o-git2"
      else echo "  ℹ️ (c) root では読めない dir を作れないので飛ばす"; fi ;;
    *) echo "  ℹ️ (c) 読めない dir の検査は POSIX だけ（この OS では selftest の差し替えで確かめる）" ;;
  esac
  "${PY}" "${G2}/papers/ime-observation/${XC}" --out "${G2}/pub" --allow-missing-license --style-check "${SC}" > "${TMP}/neg-outin.out" 2>&1; rc=$?
  if [ "${rc}" -eq 2 ] && ! grep -q Traceback "${TMP}/neg-outin.out" && [ ! -e "${G2}/pub" ]; then ok "AC8c (k) --out が元を含む git の作業ツリーの中なら exit 2"
  else ng "AC8c (k) --out が作業ツリーの中でも止まらない（exit ${rc}）"; fi
else ng "AC8c 陰性対照の準備（一時的な git repo・2）に失敗した"; fi

# ---- AC8d: 追補 3（判断 78・decisions.md の (a)〜(n)）の陰性対照と陽性対照（2026-09-30・/cross-review 2 巡目）
neg mixsep "kit/e3/README.md" 'The trace was under C:/Users/\zed/work.' "判断 78: 混ざった区切りの C:/Users/<区切り><名> を混ぜると exit 1"
neg dotsep "kit/e2/README.md" "The trace was under /Users/./zed/work." "判断 78: /Users/./<名> を混ぜると exit 1"
neg flagpath "kit/run/README.md" "Link with -L/Users/zed/lib when needed." "(g) -L/Users/<名> を混ぜると exit 1"
mkcopy urlok
printf '%s\n' "See https://stackoverflow.com/users/12345/name and https://github.com/users/octocat/projects/1." "Docs are at https://example.org/home/docs for reference." >> "${TMP}/c-urlok/papers/ime-observation/kit/formats/FORMATS.md"
run_ok "AC8d (e) 陽性対照: web の URL の /users/<id>・/home/<x> は通る" cx urlok
PGPL="$(printf '%s%s%s' '-----BEGIN PGP PRIV' 'ATE KEY BL' 'OCK-----')"
newf 2 pgp "experiment/keys2.md" "${PGPL}" "(a) PGP の秘密鍵の BEGIN 行で exit 2"
SKA="$(printf '%s%s' 'sk-' 'ant-')$(printf 'a%.0s' $(seq 1 30))"
newf 2 skant "experiment/keys3.md" "The key ${SKA} was used." "(a) sk-ant- の鍵に見える中身で exit 2"
if [ -f "${TMP}/neg-skant.out" ] && grep -qF "aaaaaaaaaaaa" "${TMP}/neg-skant.out"; then ng "(a) 当たった値（鍵に見える中身）が出力に出ている"; else ok "(a) 当たった値（sk-ant- の中身）を出力に出さない"; fi
mkcopy secdir
mkdir -p "${TMP}/c-secdir/papers/ime-observation/kit/.aws"
printf '%s\n' "[default]" > "${TMP}/c-secdir/papers/ime-observation/kit/.aws/config"
cx secdir > "${TMP}/neg-secdir.out" 2>&1; rc=$?
judge 2 secdir ".aws" "(i) 秘密の名前の型の dir（.aws）で exit 2" "${rc}"
mkcopy tex
mkdir -p "${TMP}/c-tex/papers/ime-observation/manuscript"
printf '%s\n' "Introduction." > "${TMP}/c-tex/papers/ime-observation/manuscript/draft.tex"
cx tex > "${TMP}/neg-tex.out" 2>&1; rc=$?
judge 2 tex "draft.tex" "(d) 検査の道具が読まない種類（.tex）で exit 2" "${rc}"
# (b) .git が壊れている（指す先が無い）と git は「not a git repository」を返す → exit 2
mkcopy brokengit
printf 'gitdir: %s\n' "${TMP}/no-such-gitdir" > "${TMP}/c-brokengit/.git"
cx brokengit > "${TMP}/neg-brokengit.out" 2>&1; rc=$?
if [ "${rc}" -eq 2 ] && ! grep -q Traceback "${TMP}/neg-brokengit.out" && [ ! -e "${TMP}/o-brokengit" ]; then ok "AC8d (b) 壊れた .git の下では exit 2"
else ng "AC8d (b) 壊れた .git の下でも止まらない（exit ${rc}）"; fi

check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/(kit/export/(export\.py|README\.md|export\.internal\.py|README\.internal\.md|translations\.internal\.json)|kit/analysis/pipeline\.py|README\.md|CITATION\.cff|\.zenodo\.json)$'
style_ok
finish
