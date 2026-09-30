#!/usr/bin/env bash
# issue 024 acceptance — 公開 repo への書き出し
# ★ 2026-09-30 に判断 67（絶対パスの規則）・68（測定用のロガーは書き出しからビルド・機械によらずバイト一致）・
#   69（逐語コピーの文字列リテラルを対訳表で英訳）に合わせて書き直した。
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
X="${K}/export/export.py"
SC="$(cd "$(dirname "$0")" && pwd)/_style_check.py"
SRC="papers/ime-observation"

echo "[024] 公開 repo への書き出し"
for f in "${X}" "${K}/export/README.md" "${K}/export/translations.internal.json" "${SRC}/CITATION.cff" "${SRC}/.zenodo.json"; do need_file "${f}"; done
selftest_ok "${X}"
# ★ ケース名は英語（判断 36）。逐語コピーはコメントを除き、日本語の文字列は対訳で置き換えて書き出す（判断 69）。
while IFS= read -r c; do
  [ -n "${c}" ] && need_grep "${X}" "${c}" "AC2 selftest ケース: ${c}"
done <<'CASES'
a participant identifier stops the export
an email address stops the export
a bracketed reference number passes
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
CASES
run_ok "AC .zenodo.json が JSON" "${PY}" -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8'))" "${SRC}/.zenodo.json"
run_ok "AC 判断 69: 対訳表が JSON で entries を持つ" "${PY}" -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); assert isinstance(d.get('entries'),list) and d['entries']" "${K}/export/translations.internal.json"

# ---- AC3 / AC4 / AC5: 実物を書き出す（2 回）
run_ok "AC3 実物を書き出せる（試験モード）" "${PY}" "${X}" --out "${TMP}/e1" --allow-missing-license
run_ok "AC3 実物を書き出せる（2 回目）" "${PY}" "${X}" --out "${TMP}/e2" --allow-missing-license
if [ -f "${TMP}/e1/kit/logger/manifest.json" ]; then ok "AC3 manifest.json がある"; else ng "AC3 manifest.json が無い"; fi
BAD="$(cd "${TMP}/e1" 2>/dev/null && find . \( -name '*.jsonl' -o -name '*.ndjson' -o -name '*.internal.*' -o -name '*.zip' -o -name '.DS_Store' \
  -o -type d \( -name target -o -name sealed -o -name runs -o -name .build -o -name __pycache__ \) \) -print | grep -v '^\./kit/corpus/data/[^/]*\.jsonl$' || true)"
if [ -d "${TMP}/e1" ] && [ -z "${BAD}" ]; then ok "AC3 生ログ・生成物・内部の記録が無い"; else ng "AC3 除外されていない: $(echo "${BAD}" | tr '\n' ' ')"; fi
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
  for n in lib.rs ime_windows.rs hook_windows.rs hook_macos.rs anonymize.rs capabilities.rs logger.rs schema_dto.rs; do
    grep -rqF "${n}" "${TMP}/e1" 2>/dev/null && UP_HITS="${UP_HITS} ${n}"
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
sys.stdout.write("".join(x[1]+"\n" for x in sorted(out)))'
list () { "${PY}" -c "${LIST_PY}" "$1"; }
L1="$( [ -d "${TMP}/e1" ] && list "${TMP}/e1" )"
if [ -n "${L1}" ] && [ "${L1}" = "$( [ -d "${TMP}/e2" ] && list "${TMP}/e2" )" ]; then ok "AC5 2 回の書き出しがバイト一致"; else ng "AC5 書き出しが無い、または 2 回が一致しない"; fi
if [ -d "${TMP}/e1" ] && [ -z "$(grep -rlI "$(printf '\r')" "${TMP}/e1" 2>/dev/null)" ]; then ok "AC5 判断 68: 書き出しのテキストに CR が無い"; else ng "AC5 判断 68: CR を含むファイルがある: $(grep -rlI "$(printf '\r')" "${TMP}/e1" 2>/dev/null | head -n 3 | tr '\n' ' ')"; fi
# ★ 判断 68: 別の機械の acceptance と同じ commit で比べる値（一致しなければ機械に依存する内容が混ざっている）
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

# ---- AC8: 実物の写しで秘匿の検査が効く（陰性対照）。★ 写しは git の外に作る（export.py は git に依存しない）
COPY_PY='import shutil,sys; shutil.copytree(sys.argv[1], sys.argv[2], ignore=shutil.ignore_patterns("target","__pycache__",".build","runs","sealed"))'
mkcopy () { rm -rf "${TMP}/c-$1"; "${PY}" -c "${COPY_PY}" "${SRC}" "${TMP}/c-$1/papers/ime-observation"; }
cx () { local n="$1"; shift; "${PY}" "${TMP}/c-${n}/papers/ime-observation/kit/export/export.py" --out "${TMP}/o-${n}" --allow-missing-license "$@"; }
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

check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/(kit/export/(export\.py|README\.md|translations\.internal\.json)|CITATION\.cff|\.zenodo\.json)$'
style_ok
finish
