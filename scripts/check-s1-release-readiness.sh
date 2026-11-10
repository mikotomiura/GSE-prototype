#!/usr/bin/env bash
# check-s1-release-readiness.sh — 段 1（ADR-043）の配布物を **配る前** に通す門。
#
# 何を見るか（.steering/20261107-gse-m5-s1-replay-gate/design.md の「PR 2」）:
#   [1] 組み立てと launcher: 本人用の印（s1.mode の中身 audience=self）を段 1 の分岐の中で両 OS に書く／
#       eh3.mode を書かない／段 1 の launcher がプローブを止める環境変数を付けない・BOM・CRLF・chcp が先。
#   [2] リリースタグ: 段 1 の実装（s1.rs・s1_driver.rs）を含むタグがあり、その後にコードが動いていない。
#   [3] 同意: 本人用（--audience self）は段 1 の同意文書の承認を求めない（計画の判断 5）。
#       他の参加者向け（--audience participants）は承認の印を求める。
#   [4] 配布物（--dist ごと・フォルダか zip）: o1.mode と s1.mode があり g1.mode と eh3.mode が無い
#       （計画の判断 7）／s1.mode の中身が audience に合う（本人用の配布物を他の参加者向けの門で弾く）／
#       .bat がプローブを止める環境変数を付けない／gse-next の実体が段 1 を知っている。
#
# 使い方:
#   bash scripts/check-s1-release-readiness.sh --audience self --dist <Windows の zip> --dist <macOS の zip>
#     （片方の OS だけを配るときは --os-only windows|macos）
#   bash scripts/check-s1-release-readiness.sh --audience participants --consent <段 1 の同意文書> --dist …
#   bash scripts/check-s1-release-readiness.sh --selftest   # 門自身を壊して赤になるか測る
#
# 終了コード: 0 = 配ってよい / 1 = まだ配れない / 2 = 引数が不正
#
# 限界: 組み立ての本文は静的に読む（主の防御は組み立ての展開後の検査とこの門の [4] の実体の検査）。
#   アプリは s1.mode の中身を読まないので、本人用の配布物をこの門を通さずに他の人へ渡すことや、
#   中身を書き換えて渡すことは防げない（`audience=` はラベル。防ぐのは門を通す運用）。
#   配布物のバイナリが [2] のタグから作られたことは確かめない（実体に段 1 の文字列があることだけを見る）。
# Windows では git-bash から実行すること。

set -uo pipefail

MODE=main
AUDIENCE=""
CONSENT=""
DISTS=()
OS_ONLY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) MODE=selftest; shift ;;
    --audience)
      [ $# -ge 2 ] || { echo "--audience に値がありません（self か participants）" >&2; exit 2; }
      AUDIENCE="$2"; shift 2 ;;
    --consent)
      [ $# -ge 2 ] || { echo "--consent に値がありません" >&2; exit 2; }
      CONSENT="$2"; shift 2 ;;
    --dist)
      [ $# -ge 2 ] || { echo "--dist に値がありません" >&2; exit 2; }
      DISTS+=("$2"); shift 2 ;;
    # 片方の OS だけを配るときに明示する（既定は Windows と macOS の両方を求める・/cross-review LOW）。
    --os-only)
      [ $# -ge 2 ] || { echo "--os-only に値がありません（windows か macos）" >&2; exit 2; }
      case "$2" in windows|macos) OS_ONLY="$2" ;; *) echo "--os-only は windows か macos" >&2; exit 2 ;; esac
      shift 2 ;;
    -h|--help) sed -n '1,26p' "$0"; exit 0 ;;
    # 知らない引数を黙って無視しない（打ち間違いが「緑だった」に化ける）。
    *) echo "知らない引数: $1" >&2; exit 2 ;;
  esac
done

if [ "$MODE" = main ]; then
  case "${AUDIENCE}" in
    self|participants) : ;;
    *) echo "--audience に self か participants を渡すこと（受け取った値: '${AUDIENCE}'）" >&2; exit 2 ;;
  esac
  if [ "${#DISTS[@]}" -eq 0 ]; then
    echo "--dist に配布物（zip かフォルダ）を 1 つ以上渡すこと" >&2; exit 2
  fi
fi

SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
# --dist・--consent の相対パスは呼び出した場所から解く。
CALL_DIR="$(pwd)"
cd "$(dirname "$0")/.." || { echo "リポジトリ直下へ移動できません" >&2; exit 1; }

PASS=0; FAIL=0
ok()    { echo "  ✅ $*"; PASS=$((PASS+1)); }
ng()    { echo "  ❌ $*"; FAIL=$((FAIL+1)); }
head_() { echo; echo "[$1] $2"; }

EXP="experiments/20260801-controlled-friction-task"
BUILD="${EXP}/make-common-app-zip.sh"
BUILD_G1="${EXP}/make-distribution.sh"
LAUNCHER="${EXP}/launch-s1-windows.bat"
SETUP_MAC="${EXP}/初回セットアップ_mac.sh"

# 門の本文に出る語。⚠️ 検査の対象（組み立て・launcher・配布物）はこのファイルではないので
#   空回りはしないが、selftest が埋める対照は実行時に連結して作る（O1 の門の先例）。
DP_WORD="$(printf '%s%s' 'GSE_DISABLE' '_PROBES')"
# `${M}` の形も拾う。分岐の行は「印を書く 1 文だけ」の形に限る（後ろに別の文を続けた行を許さない・点検 LOW）。
S1_WRITE_RE='(>|tee|cp|touch|mv)[^#]*\$\{?[A-Za-z_]+\}?"?/s1\.mode'
EH3_WRITE_RE='(>|tee|cp|touch|mv)[^#]*\$\{?[A-Za-z_]+\}?"?/eh3\.mode'
# 許す書き出しは次の 2 行だけ（前後の空白を除いて完全一致）。
S1_ALLOWED_M="$(printf '[ "$MODE" = s1 ] && printf %s%s%s %s > "$M/s1.mode"' "'" '%s\n' "'" "'audience=self'")"
S1_ALLOWED_W="$(printf '[ "$MODE" = s1 ] && printf %s%s%s %s > "$W/s1.mode"' "'" '%s\n' "'" "'audience=self'")"
trim_ () { sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'; }

abs_path_ () { case "$1" in /*) printf '%s' "$1" ;; *) printf '%s/%s' "${CALL_DIR}" "$1" ;; esac; }
# コメントでない行（CR を落とす）。
code_lines_ () { [ -f "$1" ] && tr -d '\r' < "$1" | grep -vE '^[[:space:]]*#' || true; }

# launcher のバイト形式と中身を python で見る（BOM・全行 CRLF・chcp が最初の非 ASCII の行より前・
# コメントでない行に環境変数・eh3.mode の中断）。出力は「KEY=値」の行。
launcher_facts_ () {
  python3 - "$1" "${DP_WORD}" <<'PY'
import re, sys
p, word = sys.argv[1], sys.argv[2].lower()
try:
    b = open(p, "rb").read()
    print("BOM=%d" % b.startswith(b"\xef\xbb\xbf"))
    body = b[3:] if b.startswith(b"\xef\xbb\xbf") else b
    lf = body.count(b"\n"); crlf = body.count(b"\r\n")
    print("CRLF=%d" % (lf > 0 and lf == crlf))
    lines = body.decode("utf-8", "replace").replace("\r\n", "\n").split("\n")
    chcp = next((i for i, l in enumerate(lines) if re.match(r"\s*chcp\s+65001", l, re.I)), None)
    nonascii = next((i for i, l in enumerate(lines) if any(ord(c) > 127 for c in l)), None)
    print("CHCP_FIRST=%d" % (chcp is not None and (nonascii is None or chcp < nonascii)))
    code = [l for l in lines if not re.match(r"\s*(rem(\s|$)|::)", l, re.I)]
    # Windows の環境変数は大文字小文字を区別しない（2026-11-07 点検 両者一致）。
    print("DISABLE=%d" % any(word in l.lower() for l in code))
    print("EH3_ABORT=%d" % any(re.search(r'if\s+exist\s+"%~dp0eh3\.mode"', l, re.I) for l in code))
    print("DONE=1")
except Exception as e:
    print("ERR=%s" % type(e).__name__)
PY
}

# 配布物（フォルダか zip）を展開せずに読む。zip は 1 段のフォルダに包まれていればその中を根とみなす
# （`__MACOSX/` は無視する）。⚠️ 例外のときは DONE を出さず ERR を出す。呼び出し側は DONE=1 が無ければ赤にする
# （2026-11-07 点検 両者一致の HIGH: 途中で落ちると後ろの検査が緑に倒れていた）。
dist_facts_ () {
  python3 - "$1" "${DP_WORD}" "${LAUNCHER}" "${SETUP_MAC}" <<'PY'
import os, re, stat, sys, unicodedata, zipfile
p, word = sys.argv[1], sys.argv[2].lower()
want_bat = open(sys.argv[3], "rb").read() if os.path.isfile(sys.argv[3]) else None
want_setup = open(sys.argv[4], "rb").read() if os.path.isfile(sys.argv[4]) else None
def has_ctl(n):
    return any(ord(c) < 32 or ord(c) == 127 for c in n)
def esc(n):
    return n.encode("unicode_escape").decode()[:80]
MARKERS = ("o1.mode", "s1.mode", "g1.mode", "eh3.mode")
MAX_MEMBER = 1 << 30          # 1 GiB を超えるメンバーは読まない（壊れた・悪い zip で門が落ちないように）
LITS = (b"s1.mode", b"GSE_S1_MODE")
def norm(name):
    # Windows と macOS の既定は大文字小文字を区別しない。Windows は末尾の点と空白を落とす。
    # macOS は濁点・半濁点を分解した形（NFD）で名前を持つので NFC にそろえる（実物の zip で誤って赤になった）。
    return unicodedata.normalize("NFC", name).lower().rstrip(". ")
def zip_name(i):
    # ditto の zip は UTF-8 の印（bit 11）を立てないので、zipfile は cp437 で読んで化かす。UTF-8 で読み直す。
    if i.flag_bits & 0x800:
        return i.filename
    try:
        return i.filename.encode("cp437").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return i.filename
def bat_bad(data):
    t = data.decode("utf-8-sig", "replace").replace("\r\n", "\n")
    return any(word in l.lower() for l in t.split("\n") if not re.match(r"\s*(rem(\s|$)|::)", l, re.I))
def scan(fh):
    found = set(); tail = b""
    while True:
        chunk = fh.read(1 << 20)
        if not chunk:
            break
        buf = tail + chunk
        for lit in LITS:
            if lit in buf:
                found.add(lit)
        tail = buf[-32:]
    return found
try:
    bad_names = []
    entries = []   # (name, size, opener)
    if os.path.isdir(p):
        for d, dirs, fs in os.walk(p):
            for f in fs + [x for x in dirs if os.path.islink(os.path.join(d, x))]:
                full = os.path.join(d, f)
                rel = os.path.relpath(full, p).replace(os.sep, "/")
                # 名前の制御文字は出力の行を偽れる（/cross-review 2 巡目 Codex P2）。逃がして赤にする。
                if has_ctl(rel):
                    bad_names.append(esc(rel)); continue
                if os.path.islink(full):
                    bad_names.append(esc(rel) + "(link)"); continue
                entries.append((rel, os.path.getsize(full), (lambda full=full: open(full, "rb"))))
    elif zipfile.is_zipfile(p):
        z = zipfile.ZipFile(p)
        infos = [i for i in z.infolist() if not i.is_dir() and not i.filename.startswith("__MACOSX/")]
        raw = [zip_name(i) for i in infos]
        tops = {n.split("/", 1)[0] for n in raw}
        prefix = ""
        if len(tops) == 1 and all("/" in n for n in raw):
            prefix = next(iter(tops)) + "/"
        for i in infos:
            n = zip_name(i)
            if n.startswith("/") or "\\" in n or ".." in n.split("/") or ":" in n \
               or has_ctl(n):
                bad_names.append(esc(n)); continue
            if stat.S_ISLNK(i.external_attr >> 16):      # zip の中のシンボリックリンク（/cross-review Codex P1）
                bad_names.append(esc(n) + "(link)"); continue
            entries.append((n[len(prefix):], i.file_size, (lambda i=i: z.open(i))))
    else:
        print("KIND=bad"); sys.exit(0)
    print("KIND=ok")
    names = [e[0] for e in entries]
    normed = [norm(n) for n in names]
    dups = sorted({n for n in normed if normed.count(n) > 1})
    print("BAD_NAMES=" + ",".join(bad_names + ["dup:" + d for d in dups])[:300])
    by = {norm(e[0]): e for e in entries}
    root = {norm(n) for n in names if "/" not in n}
    for m in MARKERS:
        print("HAS_%s=%d" % (m.split(".")[0].upper(), m in root))
    # 小文字の完全一致でない印（`S1.mode` など）と、根以外の階層の印は赤にする。
    odd = [n for n in names if "/" not in n and norm(n) in MARKERS and n != norm(n)]
    deep = [n for n in names if "/" in n and norm(n.rsplit("/", 1)[1]) in MARKERS]
    print("ODD_MARKERS=" + ",".join(odd + deep)[:300])
    big = [n for n, size, _ in entries if size > MAX_MEMBER]
    print("BIG=" + ",".join(big)[:300])
    if "s1.mode" in root:
        with by["s1.mode"][2]() as fh:
            body = fh.read(4096).decode("utf-8", "replace").strip()
        print("S1_BODY=" + "".join(c for c in body if c.isprintable())[:80])
    launchers = [e for e in entries if norm(e[0]).endswith((".bat", ".cmd"))]
    print("BATS=%d" % len([e for e in launchers if "/" not in e[0]]))
    bad = []
    for n, size, op in launchers:
        if size > MAX_MEMBER:
            continue
        with op() as fh:
            if bat_bad(fh.read()):
                bad.append(n)
    print("BAT_DISABLE=" + ",".join(sorted(bad))[:300])
    print("WINDOWS=%d" % ("gse-next.exe" in root))
    print("MACOS=%d" % ("gse-next.app/contents/macos/gse-next" in by))
    # 自動送信に要るファイル（/cross-review 両者一致）。中身は読まない（secret を含む）。
    # 0 バイトは無いものとみなす（/cross-review 2 巡目 LOW）。
    need = ["g1-submit.json"]
    if "gse-next.exe" in root:
        need += ["gse-submit.exe", "pubkey.txt"]
    if "gse-next.app/contents/macos/gse-next" in by:
        need += ["gse-next.app/contents/macos/gse-submit", "gse-next.app/contents/resources/resources/pubkey.txt"]
    print("MISSING=" + ",".join(n for n in need if n not in by or by[n][1] == 0))
    # 段 1 の配布物に組み立てが書いたタグ（[2] のタグと照らす・/cross-review 2 巡目 Codex P1）。
    if "s1-release-tag.txt" in root:
        with by["s1-release-tag.txt"][2]() as fh:
            t = fh.read(256).decode("utf-8", "replace").strip()
        print("REL_TAG=" + "".join(c for c in t if c.isprintable())[:80])
    # 根の別の入口（launcher の検査を迂回しうる）。
    other = [n for n in names if "/" not in n and norm(n).endswith((".ps1", ".vbs", ".vbe", ".js", ".wsf", ".lnk", ".com", ".scr", ".pif"))]
    print("OTHER_ENTRY=" + ",".join(esc(n) for n in other)[:300])
    # macOS の初回セットアップは repo の原本とバイト一致。
    if "gse-next.app/contents/macos/gse-next" in by:
        setup = by.get(norm("初回セットアップ_mac.sh"))
        ok_setup = False
        if setup is not None and want_setup is not None and setup[1] <= MAX_MEMBER:
            with setup[2]() as fh:
                ok_setup = fh.read() == want_setup
        print("SETUP_OK=%d" % ok_setup)
    # 根の launcher は repo の段 1 の launcher とバイト一致（空・別物への差し替えを弾く・Codex P2）。
    root_bats = [e for e in launchers if "/" not in e[0]]
    differ = []
    for n, size, op in root_bats:
        with op() as fh:
            if want_bat is None or size > MAX_MEMBER or fh.read() != want_bat:
                differ.append(n)
    print("BAT_DIFFER=" + ",".join(sorted(differ))[:300])
    bins = [by[k] for k in ("gse-next.exe", "gse-next.app/contents/macos/gse-next") if k in by]
    print("BINS=%d" % len(bins))
    lacks = []
    for n, size, op in bins:
        if size > MAX_MEMBER:
            lacks.append(n + ":too-big"); continue
        with op() as fh:
            found = scan(fh)
        lacks += ["%s:%s" % (n, l.decode()) for l in LITS if l not in found]
    print("BIN_LACKS=" + ",".join(lacks))
    print("DONE=1")
except SystemExit:
    raise
except Exception as e:
    print("ERR=%s" % type(e).__name__)
PY
}
fact_ () { printf '%s\n' "$1" | sed -n "s/^$2=//p" | head -1; }

run_checks () {

# --- 1. 組み立てと launcher ----------------------------------------------------
head_ 1 "組み立てと launcher（${BUILD}・${LAUNCHER}）"
if [ ! -f "${BUILD}" ]; then
  ng "組み立てが無い: ${BUILD}"
else
  s1w=$(code_lines_ "${BUILD}" | grep -E "${S1_WRITE_RE}" || true)
  s1w_t=$(printf '%s\n' "${s1w}" | grep . | trim_ || true)
  s1w_bad=$(printf '%s\n' "${s1w_t}" | grep . | grep -vxF -e "${S1_ALLOWED_M}" -e "${S1_ALLOWED_W}" || true)
  if [ -n "${s1w_bad}" ]; then
    ng "組み立てに段 1 の分岐の外で s1.mode を書く行がある（O1 の配布物に入りうる）:
$(printf '%s\n' "${s1w_bad}" | sed 's/^/        /')"
  elif printf '%s\n' "${s1w_t}" | grep -qxF -e "${S1_ALLOWED_M}" \
       && printf '%s\n' "${s1w_t}" | grep -qxF -e "${S1_ALLOWED_W}"; then
    ok "組み立てが本人用の印（audience=self）を macOS と Windows の両方に段 1 の分岐で書く"
  else
    ng "組み立てが本人用の印（audience=self）を macOS と Windows の両方に書いていない"
  fi
  # case の枝ごとに切り出して見る（o1 の枝に紛れると O1 の配布物から環境変数が消える・/cross-review LOW）。
  branch_ () { tr -d '\r' < "${BUILD}" | awk -v b="$1" '$0 ~ "^  "b"\\)" { f = 1; next } f && (/^    ;;/ || /^  [a-z0-9|*]+\)/ || /^esac/) { f = 0 } f'; }
  if branch_ s1 | grep -qF 'WIN_LAUNCHER_SRC="$HERE/launch-s1-windows.bat"' \
     && ! branch_ o1 | grep -qF 'launch-s1-windows.bat' && ! branch_ g1 | grep -qF 'launch-s1-windows.bat'; then
    ok "組み立ての段 1 が段 1 の launcher を入れる"
  else
    ng "組み立ての段 1 が段 1 の launcher（launch-s1-windows.bat）を入れていない"
  fi
fi
eh3w=""
for f in "${BUILD}" "${BUILD_G1}"; do
  eh3w="${eh3w}$(code_lines_ "$f" | grep -E "${EH3_WRITE_RE}" || true)"
done
if [ -n "${eh3w}" ]; then
  ng "組み立てが eh3.mode を書く（段 1 と EH3 の印が同居すると両方が落ちる・計画の判断 7）"
else
  ok "組み立ては eh3.mode を書かない"
fi
if [ ! -f "${LAUNCHER}" ]; then
  ng "段 1 の launcher が無い: ${LAUNCHER}"
elif ! command -v python3 > /dev/null 2>&1; then
  ng "python3 が無いので launcher を検査できない"
else
  lf_=$(launcher_facts_ "${LAUNCHER}")
  if [ "$(fact_ "${lf_}" DONE)" != 1 ]; then
    ng "launcher の検査が最後まで走らなかった（$(fact_ "${lf_}" ERR)）"
  fi
  if [ "$(fact_ "${lf_}" BOM)" = 1 ] && [ "$(fact_ "${lf_}" CRLF)" = 1 ]; then
    ok "launcher が BOM ＋ 全行 CRLF"
  else
    ng "launcher のバイト形式が BOM ＋ 全行 CRLF でない（日本語の Windows で化ける）"
  fi
  if [ "$(fact_ "${lf_}" CHCP_FIRST)" = 1 ]; then
    ok "launcher の chcp 65001 が日本語より前"
  else
    ng "launcher の chcp 65001 が日本語の行より後か、無い"
  fi
  if [ "$(fact_ "${lf_}" DISABLE)" != 0 ]; then
    ng "launcher がプローブを止める環境変数を付けている（計画の判断 6・段 1 では付けない）か、判定できなかった"
  else
    ok "launcher はプローブを止める環境変数を付けない"
  fi
  if [ "$(fact_ "${lf_}" EH3_ABORT)" = 1 ]; then
    ok "launcher が eh3.mode の同居で中断する"
  else
    ng "launcher が eh3.mode の同居を確かめていない（計画の判断 7）"
  fi
fi

# --- 2. リリースタグ ------------------------------------------------------------
head_ 2 "リリースタグ（段 1 の実装を含み、その後にコードが動いていない）"
s1_tag=""
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  ng "git リポジトリではないので、段 1 を含むタグを確かめられない"
else
  # 手元の origin/main がリモートの main と同じかを先に確かめる（両方の参照が古いと誤って緑になる・/cross-review 2 巡目 MEDIUM）。
  # ⚠️ ネットワークが無い・origin が無いときは判定できないので赤。
  if ! git remote get-url origin > /dev/null 2>&1; then
    ng "origin が無いので、リモートの main と比べられない"
  else
    remote_sha=$(git ls-remote origin refs/heads/main 2>/dev/null | cut -f1 || true)
    local_sha=$(git rev-parse --verify --quiet 'origin/main^{commit}' 2>/dev/null || true)
    if [ -z "${remote_sha}" ]; then
      ng "リモートの main を読めない（ネットワークか権限）。読めるところで走らせる"
    elif [ "${remote_sha}" != "${local_sha}" ]; then
      ng "手元の origin/main がリモートの main と違う（先に git fetch origin を走らせる）"
    else
      ok "手元の origin/main はリモートの main と同じ"
    fi
  fi
  # 比較先は origin/main と main の両方（片方が古くても、もう片方のタグの後の変更を拾う・/cross-review Codex P2）。
  cmp_refs=""
  for r in origin/main main; do
    if git rev-parse --verify --quiet "${r}^{commit}" > /dev/null 2>&1; then cmp_refs="${cmp_refs} ${r}"; fi
  done
  # 段 1 の実装を含む v* のタグのうち、比較先のどれかの祖先である最も新しいもの。
  # それより新しい祖先でないタグは注意として出す（試し用の枝のタグで止まらない・/cross-review 2 巡目 LOW）。
  skipped=""
  while IFS= read -r t; do
    [ -n "$t" ] || continue
    git cat-file -e "${t}:src-tauri/src/s1.rs" 2>/dev/null \
      && git cat-file -e "${t}:src-tauri/src/s1_driver.rs" 2>/dev/null || continue
    anc=0
    for r in ${cmp_refs}; do
      git merge-base --is-ancestor "${t}" "${r}" 2>/dev/null && anc=1
    done
    if [ "${anc}" = 1 ]; then s1_tag="$t"; break; fi
    skipped="${skipped} ${t}"
  done <<< "$(git tag -l 'v*' --sort=-v:refname 2>/dev/null)"
  [ -z "${skipped}" ] || echo "  （注意）段 1 を含むが main の祖先でないタグを飛ばした:${skipped}"
  if [ -z "${cmp_refs}" ]; then
    ng "比較先（origin/main / main）が解決できないため、タグの鮮度を判定できない"
  elif [ -z "${s1_tag}" ]; then
    ng "段 1 の実装（s1.rs・s1_driver.rs）を含み main の祖先であるリリースタグが 1 つも無い（s1.mode を置いても問いが出ない）"
  else
    # 見る範囲は配るバイナリに入りうるもの全部（src-tauri の全体・フロントエンドとそのビルドの設定・依存の固定）。
    # ⚠️ src-tauri/tests だけの変更でも「古い」になる（数えすぎる側に倒す）。
    stale=""
    for r in ${cmp_refs}; do
      if ! one=$(git log --oneline "${s1_tag}..${r}" -- src-tauri src public index.html package.json \
                   package-lock.json vite.config.ts 'tsconfig*.json' rust-toolchain.toml 2>/dev/null); then
        stale="(git log が失敗した)"; break
      fi
      stale="$(printf '%s\n%s\n' "${stale}" "${one}" | grep . | sort -u || true)"
    done
    stale_n=$(printf '%s' "${stale}" | grep -c . || true)
    if [ "${stale}" = "(git log が失敗した)" ]; then
      ng "タグ ${s1_tag} の後の変更を数えられない（git log が失敗した）"
    elif [ "${stale_n:-0}" -gt 0 ]; then
      ng "リリースタグ ${s1_tag} は古い（タグの後にコードが ${stale_n} コミット動いている。再ビルドして新しいタグを切る）:
$(printf '%s\n' "${stale}" | head -10 | sed 's/^/        /')"
    else
      ok "段 1 の実装を含むリリースタグがある（${s1_tag}）・その後に配布物のコードの変更なし"
    fi
  fi
fi

# --- 3. 同意 --------------------------------------------------------------------
head_ 3 "同意（${AUDIENCE}）"
if [ "${AUDIENCE}" = self ]; then
  ok "本人用（計画の判断 5）: 段 1 の同意文書の承認は求めない（登録の画面の本人の同意の印で問いを開く）"
  if [ -n "${CONSENT}" ]; then
    ng "本人用に --consent が渡された（本人用か参加者向けかの取り違えを疑う）"
  fi
else
  if [ -z "${CONSENT}" ]; then
    ng "段 1 の同意文書（R4）を --consent で渡していない（他の参加者に配るには承認が要る）"
  else
    cpath="$(abs_path_ "${CONSENT}")"
    if [ ! -f "${cpath}" ]; then
      ng "段 1 の同意文書が無い: ${CONSENT}"
    else
      # 行頭完全一致（説明文の中の印に一致させない）。印は研究者が入れる。
      # フェンス（```）の中の行は数えない。印はちょうど 1 回（点検 MEDIUM）。
      n_mark=$(tr -d '\r' < "${cpath}" | awk '/^[[:space:]]*(```|~~~)/ { f = !f; next } !f' \
                 | grep -cE '^<!-- s1-esm-consent: approved -->[[:space:]]*$' || true)
      if [ "${n_mark:-0}" -eq 1 ]; then
        ok "段 1 の同意文書が研究者に承認されている（s1-esm-consent: approved）"
      elif [ "${n_mark:-0}" -gt 1 ]; then
        ng "段 1 の同意文書に承認の印が ${n_mark} 回ある（1 回だけにする）"
      else
        ng "段 1 の同意文書に承認の印（行頭の <!-- s1-esm-consent: approved -->・フェンスの外）が無い"
      fi
      if grep -q "（実施前に記入）" "${cpath}"; then
        ng "段 1 の同意文書に未記入の欄が残っている（『（実施前に記入）』）"
      else
        ok "段 1 の同意文書に未記入の欄が無い"
      fi
    fi
  fi
fi

# --- 4. 配布物 ------------------------------------------------------------------
head_ 4 "配布物（${#DISTS[@]} 件）"
want_body="audience=${AUDIENCE}"
seen_win=0; seen_mac=0
for d in "${DISTS[@]}"; do
  dp="$(abs_path_ "$d")"
  label="$(basename "$d")"
  if [ ! -e "${dp}" ]; then
    ng "${label}: 配布物が無い: ${d}"; continue
  fi
  if ! command -v python3 > /dev/null 2>&1; then
    ng "${label}: python3 が無いので配布物を検査できない"; continue
  fi
  df_=$(dist_facts_ "${dp}")
  if [ "$(fact_ "${df_}" KIND)" = bad ]; then
    ng "${label}: フォルダでも zip でもない"; continue
  fi
  if [ "$(fact_ "${df_}" DONE)" != 1 ]; then
    ng "${label}: 配布物の検査が最後まで走らなかった（$(fact_ "${df_}" ERR)・読めないメンバーか壊れた zip）"; continue
  fi
  [ -z "$(fact_ "${df_}" BAD_NAMES)" ] && ok "${label}: メンバーの名前に異常が無い（重複・..・制御文字・リンク）" \
    || ng "${label}: メンバーの名前に異常がある: $(fact_ "${df_}" BAD_NAMES)"
  [ -z "$(fact_ "${df_}" ODD_MARKERS)" ] && ok "${label}: 印は根に小文字の名前でだけある" \
    || ng "${label}: 根以外の階層か、大文字を含む名前の印がある: $(fact_ "${df_}" ODD_MARKERS)"
  [ -z "$(fact_ "${df_}" BIG)" ] || ng "${label}: 1 GiB を超えるメンバーがある（読まない）: $(fact_ "${df_}" BIG)"
  [ "$(fact_ "${df_}" HAS_O1)" = 1 ] && ok "${label}: o1.mode がある" \
    || ng "${label}: o1.mode が無い（段 1 は O1 の器の上でだけ立つ）"
  if [ "$(fact_ "${df_}" HAS_S1)" = 1 ]; then
    ok "${label}: s1.mode がある"
    body="$(fact_ "${df_}" S1_BODY)"
    if [ "${body}" = "${want_body}" ]; then
      ok "${label}: s1.mode の中身が ${want_body}"
    elif [ "${AUDIENCE}" = participants ] && [ "${body}" = "audience=self" ]; then
      ng "${label}: 本人用の配布物（audience=self）を他の参加者向けに配ろうとしている（計画の判断 5）"
    else
      ng "${label}: s1.mode の中身が ${want_body} でない（受け取った値: '${body}'）"
    fi
  else
    ng "${label}: s1.mode が無い（問いが出ない）"
  fi
  [ "$(fact_ "${df_}" HAS_G1)" = 1 ] && ng "${label}: g1.mode が混ざっている（G1 が勝ち、O1 として記録されない）" \
    || ok "${label}: g1.mode が無い"
  [ "$(fact_ "${df_}" HAS_EH3)" = 1 ] && ng "${label}: eh3.mode が混ざっている（段 1 と EH3 の両方が落ちる・計画の判断 7）" \
    || ok "${label}: eh3.mode が無い"
  [ -z "$(fact_ "${df_}" MISSING)" ] && ok "${label}: 自動送信に要るファイルがそろっている" \
    || ng "${label}: 自動送信に要るファイルが無い: $(fact_ "${df_}" MISSING)"
  [ "$(fact_ "${df_}" WINDOWS)" = 1 ] && seen_win=1
  [ "$(fact_ "${df_}" MACOS)" = 1 ] && seen_mac=1
  rel_tag="$(fact_ "${df_}" REL_TAG)"
  if [ -z "${s1_tag}" ]; then
    ng "${label}: 配布物のタグを照らせない（[2] で段 1 のタグが決まっていない）"
  elif [ "${rel_tag}" = "${s1_tag}" ]; then
    ok "${label}: 配布物は ${s1_tag} から組まれた（s1-release-tag.txt）"
  else
    ng "${label}: 配布物の s1-release-tag.txt が ${s1_tag} でない（受け取った値: '${rel_tag}'・古いバイナリの使い回しを疑う）"
  fi
  [ -z "$(fact_ "${df_}" OTHER_ENTRY)" ] \
    || ng "${label}: 根に launcher の検査を迂回しうる入口がある: $(fact_ "${df_}" OTHER_ENTRY)"
  if [ "$(fact_ "${df_}" MACOS)" = 1 ] && [ "$(fact_ "${df_}" SETUP_OK)" != 1 ]; then
    ng "${label}: macOS の初回セットアップが無いか、repo の原本と一致しない"
  fi
  if [ -n "$(fact_ "${df_}" BAT_DIFFER)" ]; then
    ng "${label}: launcher が repo の段 1 の launcher と一致しない（空・別物への差し替え）: $(fact_ "${df_}" BAT_DIFFER)"
  fi
  bad_bats="$(fact_ "${df_}" BAT_DISABLE)"
  if [ -n "${bad_bats}" ]; then
    ng "${label}: launcher がプローブを止める環境変数を付けている: ${bad_bats}"
  elif [ "$(fact_ "${df_}" WINDOWS)" = 1 ] && [ "$(fact_ "${df_}" BATS)" = 0 ]; then
    ng "${label}: Windows の配布物に launcher（.bat）が無い"
  else
    ok "${label}: launcher はプローブを止める環境変数を付けない"
  fi
  if [ "$(fact_ "${df_}" BINS)" -lt 1 ] 2>/dev/null || [ -z "$(fact_ "${df_}" BINS)" ]; then
    ng "${label}: gse-next の実体が無い（gse-next.exe か gse-next.app）"
  elif [ -n "$(fact_ "${df_}" BIN_LACKS)" ]; then
    ng "${label}: gse-next の実体が段 1 を知らない（無い文字列: $(fact_ "${df_}" BIN_LACKS)）"
  else
    ok "${label}: gse-next の実体に s1.mode と GSE_S1_MODE がある"
  fi
done
# 渡した配布物の全体で両 OS を見たか（片方だけで「配ってよい」を出さない・/cross-review LOW）。
case "${OS_ONLY}" in
  windows) [ "${seen_win}" = 1 ] && ok "Windows の配布物を検査した（--os-only windows）" || ng "Windows の配布物が無い（--os-only windows）" ;;
  macos)   [ "${seen_mac}" = 1 ] && ok "macOS の配布物を検査した（--os-only macos）" || ng "macOS の配布物が無い（--os-only macos）" ;;
  *)
    if [ "${seen_win}" = 1 ] && [ "${seen_mac}" = 1 ]; then
      ok "Windows と macOS の両方の配布物を検査した"
    else
      ng "Windows と macOS の両方の配布物を渡していない（片方だけを配るなら --os-only windows|macos）"
    fi ;;
esac
}

# =============================================================================
# selftest — 門自身が空回りしていないかを測る（本物のリポジトリは 1 バイトも変えない）
# =============================================================================
selftest () {
  local repo fix sp sf
  repo="$(pwd)"
  fix="$(mktemp -d)"
  trap 'rm -rf "${fix:?}"' RETURN
  trap 'rm -rf "${fix:?}"; exit 130' INT
  trap 'rm -rf "${fix:?}"; exit 143' TERM
  sp=0; sf=0
  local self_body w_dir m_dir
  self_body="$(printf '%s%s' 'audience=' 'self')"
  w_dir="$fix/dist/S1_実施用_Windows"
  m_dir="$fix/dist/S1_実施用_macOS"

  make_dist_ () {
    rm -rf "${fix:?}/dist"
    mkdir -p "${w_dir}" "${m_dir}/gse-next.app/Contents/MacOS"
    for x in "${w_dir}" "${m_dir}"; do
      : > "$x/o1.mode"
      printf '%s\n' "${self_body}" > "$x/s1.mode"
    done
    printf 'MZ..%s..%s..\n' 's1.mode' 'GSE_S1_MODE' > "${w_dir}/gse-next.exe"
    printf 'x\n' > "${w_dir}/gse-submit.exe"; printf 'k\n' > "${w_dir}/pubkey.txt"
    printf '{}\n' > "${w_dir}/g1-submit.json"; printf '{}\n' > "${m_dir}/g1-submit.json"
    printf 'x\n' > "${m_dir}/gse-next.app/Contents/MacOS/gse-submit"
    mkdir -p "${m_dir}/gse-next.app/Contents/Resources/resources"
    printf 'k\n' > "${m_dir}/gse-next.app/Contents/Resources/resources/pubkey.txt"
    cp "$repo/${SETUP_MAC}" "${m_dir}/"
    printf '%s\n' 'v9.9.9' > "${w_dir}/s1-release-tag.txt"; printf '%s\n' 'v9.9.9' > "${m_dir}/s1-release-tag.txt"
    printf 'MACHO..%s..%s..\n' 's1.mode' 'GSE_S1_MODE' > "${m_dir}/gse-next.app/Contents/MacOS/gse-next"
    cp "$repo/${LAUNCHER}" "${w_dir}/GSE_起動.bat"
    ( cd "$fix/dist" && python3 -c "
import os, sys, zipfile
with zipfile.ZipFile('win.zip', 'w') as z:
    for d, _, fs in os.walk('S1_実施用_Windows'):
        for f in fs: z.write(os.path.join(d, f))
" )
  }
  build () {
    rm -rf "${fix:?}/w"
    mkdir -p "$fix/w/scripts" "$fix/w/${EXP}" "$fix/w/src-tauri/src"
    cp "${SCRIPT_PATH}" "$fix/w/scripts/gate.sh"
    cp "$repo/${BUILD}" "$repo/${BUILD_G1}" "$repo/${LAUNCHER}" "$repo/${SETUP_MAC}" "$fix/w/${EXP}/"
    printf 'pub const MARKER_FILE_NAME: &str = "s1.mode";\n' > "$fix/w/src-tauri/src/s1.rs"
    printf '// driver\n' > "$fix/w/src-tauri/src/s1_driver.rs"
    git -C "$fix/w" init -q -b main 2>/dev/null || { git -C "$fix/w" init -q; git -C "$fix/w" checkout -q -b main; }
    commit_ "selftest"
    git -C "$fix/w" tag v9.9.9 > /dev/null 2>&1
    # リモートの main と比べる検査のために、手元の bare の origin を置く。
    rm -rf "${fix:?}/origin.git" "${fix:?}/other"
    git clone -q --bare "$fix/w" "$fix/origin.git" 2>/dev/null
    git -C "$fix/w" remote add origin "$fix/origin.git"
    git -C "$fix/w" fetch -q origin 2>/dev/null
    make_dist_
    ARGS=(--audience self --dist "${w_dir}" --dist "${m_dir}" --dist "$fix/dist/win.zip")
  }
  commit_ () {
    git -C "$fix/w" add -A > /dev/null 2>&1
    git -C "$fix/w" -c user.email=s@e -c user.name=s commit -qm "$1" > /dev/null 2>&1
  }
  run_gate_ () { bash "$fix/w/scripts/gate.sh" "${ARGS[@]}" 2>&1; }
  expect_red () {
    local out; out=$(run_gate_)
    if printf '%s\n' "$out" | grep -E '^  ❌' | grep -q -- "$1"; then
      echo "  ✅ 壊すと赤になる: $2"; sp=$((sp+1))
    else
      echo "  ❌ 壊しても緑のまま: $2"; sf=$((sf+1))
    fi
  }
  expect_green () {
    local out; out=$(run_gate_)
    if printf '%s\n' "$out" | grep -E '^  ✅' | grep -q -- "$1"; then
      echo "  ✅ 満たすと緑になる: $2"; sp=$((sp+1))
    else
      echo "  ❌ 満たしても赤のまま: $2"; sf=$((sf+1))
    fi
  }
  expect_rc () {
    local rc
    bash "$fix/w/scripts/gate.sh" "${ARGS[@]}" > /dev/null 2>&1; rc=$?
    if [ "$rc" -eq "$1" ]; then
      echo "  ✅ 終了コード ${1}: $2"; sp=$((sp+1))
    else
      echo "  ❌ 終了コードが ${rc}（期待 ${1}）: $2"; sf=$((sf+1))
    fi
  }
  # .bat に行を足す（CRLF のまま）。
  bat_add_ () { printf '%s\r\n' "$2" >> "$1"; }
  local dp_line bat
  dp_line="$(printf 'set %s=1' "${DP_WORD}")"
  bat="$fix/w/${LAUNCHER}"

  echo "=== selftest 0: 基準（本人用の正しい配布物）は全部緑 ==="
  build; expect_rc 0 "本人用の配布物 3 件（フォルダ 2・zip 1）"
  build; ARGS=(--audience bogus --dist "${w_dir}"); expect_rc 2 "知らない audience"
  build; ARGS=(--audience self); expect_rc 2 "--dist が無い"
  build; ARGS=(--audience self --dist "${w_dir}" --bogus); expect_rc 2 "知らない引数"

  echo
  echo "=== selftest 1: 組み立てと launcher ==="
  build; sed -i.bak 's|> "$W/s1.mode"|> "$W/s1x.mode"|' "$fix/w/${BUILD}"
  expect_red "両方に書いていない" "Windows 側の印の書き出しを消す"
  build; printf '\n: > "$M/s1''.mode"\n' >> "$fix/w/${BUILD}"
  expect_red "分岐の外で s1.mode" "段 1 の分岐の外の書き出し"
  build; printf '\n# : > "$M/s1''.mode"\n' >> "$fix/w/${BUILD}"
  expect_green "両方に段 1 の分岐で書く" "コメントの中の書き出しは数えない"
  build; sed -i.bak 's|launch-s1-windows.bat|launch-o1-windows.bat|' "$fix/w/${BUILD}"
  expect_red "段 1 の launcher（launch-s1-windows.bat）を入れていない" "段 1 に O1 の launcher を入れる"
  build; printf '\n: > "$M/eh3''.mode"\n' >> "$fix/w/${BUILD_G1}"
  expect_red "eh3.mode を書く" "G1 の組み立てに eh3.mode の書き出し"
  build; bat_add_ "$bat" "${dp_line}"
  expect_red "launcher がプローブを止める環境変数を付けている" "launcher に環境変数"
  build; bat_add_ "$bat" "rem ${dp_line}"
  expect_green "launcher はプローブを止める環境変数を付けない" "launcher のコメントの中の環境変数は数えない"
  build; tail -c +4 "$repo/${LAUNCHER}" > "$bat"
  expect_red "BOM ＋ 全行 CRLF でない" "launcher の BOM を外す"
  build; printf 'echo x\n' >> "$bat"
  expect_red "BOM ＋ 全行 CRLF でない" "launcher の 1 行だけ LF"
  build; python3 - "$bat" <<'PY'
import sys
p = sys.argv[1]; b = open(p, "rb").read()
b = b.replace(b"chcp 65001 > nul\r\n", b"", 1) + b"chcp 65001 > nul\r\n"
open(p, "wb").write(b)
PY
  expect_red "chcp 65001 が日本語の行より後" "chcp を末尾へ動かす"
  build; python3 - "$bat" <<'PY'
import sys
p = sys.argv[1]; b = open(p, "rb").read()
b = b.replace(b'if exist "%~dp0eh3.mode"', b'if exist "%~dp0eh3x.mode"')
open(p, "wb").write(b)
PY
  expect_red "eh3.mode の同居を確かめていない" "launcher の eh3.mode の中断を外す"
  build; rm -f "$bat"; expect_red "段 1 の launcher が無い" "launcher ごと消す"

  echo
  echo "=== selftest 2: リリースタグ ==="
  build; git -C "$fix/w" tag -d v9.9.9 > /dev/null 2>&1
  expect_red "リリースタグが 1 つも無い" "タグが無い"
  build; git -C "$fix/w" tag -d v9.9.9 > /dev/null 2>&1
  git -C "$fix/w" rm -q src-tauri/src/s1_driver.rs; commit_ "no driver"; git -C "$fix/w" tag v9.9.8 > /dev/null 2>&1
  expect_red "リリースタグが 1 つも無い" "s1_driver.rs を含まないタグは数えない（タグの新しさで代用しない）"
  build; printf '// later\n' >> "$fix/w/src-tauri/src/s1.rs"; commit_ "later"
  expect_red "は古い" "タグの後に src-tauri/src が動く"
  build; mkdir -p "$fix/w/docs"; printf 'x\n' > "$fix/w/docs/x.md"; commit_ "docs only"
  expect_green "その後に配布物のコードの変更なし" "タグの後に docs だけが動いても緑"

  echo
  echo "=== selftest 3: 同意 ==="
  local cons approved
  cons="$fix/consent.md"
  approved="$(printf '<!-- s1-esm-consent: %s -->' 'approved')"
  build; ARGS=(--audience self --consent "$cons" --dist "${w_dir}" --os-only windows)
  expect_red "本人用に --consent" "本人用に同意文書を渡す（取り違え）"
  build; sed -i.bak "s/^${self_body}\$/audience=participants/" "${w_dir}/s1.mode"
  ARGS=(--audience participants --dist "${w_dir}" --os-only windows)
  expect_red "--consent で渡していない" "参加者向けに同意文書が無い"
  build; sed -i.bak "s/^${self_body}\$/audience=participants/" "${w_dir}/s1.mode"
  printf '# 同意\n説明: 承認したら %s を入れる\n' "${approved}" > "$cons"
  ARGS=(--audience participants --consent "$cons" --dist "${w_dir}" --os-only windows)
  expect_red "承認の印（行頭の" "印が説明文の中にあるだけ（行頭でない）"
  build; sed -i.bak "s/^${self_body}\$/audience=participants/" "${w_dir}/s1.mode"
  printf '# 同意\n%s\n連絡先: （実施前に記入）\n' "${approved}" > "$cons"
  ARGS=(--audience participants --consent "$cons" --dist "${w_dir}" --os-only windows)
  expect_green "研究者に承認されている" "行頭の承認の印"
  expect_red "未記入の欄" "未記入の欄が残る"
  build; sed -i.bak "s/^${self_body}\$/audience=participants/" "${w_dir}/s1.mode"
  printf '# 同意\n%s\n' "${approved}" > "$cons"
  ARGS=(--audience participants --consent "$cons" --dist "${w_dir}" --os-only windows)
  expect_rc 0 "承認済みの同意と参加者向けの配布物は全部緑"

  echo
  echo "=== selftest 4: 配布物 ==="
  build; rm -f "${w_dir}/s1.mode"; expect_red "s1.mode が無い" "s1.mode を消す"
  build; rm -f "${m_dir}/o1.mode"; expect_red "o1.mode が無い" "macOS の o1.mode を消す"
  build; : > "${w_dir}/g1.mode"; expect_red "g1.mode が混ざっている" "g1.mode を足す"
  build; : > "${m_dir}/eh3.mode"; expect_red "eh3.mode が混ざっている" "eh3.mode を足す"
  build; : > "${w_dir}/s1.mode"; expect_red "s1.mode の中身が" "s1.mode を 0 バイトにする"
  build; ARGS=(--audience participants --consent "$cons" --dist "${w_dir}" --os-only windows)
  printf '%s\n' "${approved}" > "$cons"
  expect_red "本人用の配布物（audience=self）を他の参加者向け" "本人用の配布物を参加者向けの門に通す（計画の判断 5）"
  build; bat_add_ "${w_dir}/GSE_起動.bat" "${dp_line}"
  expect_red "launcher がプローブを止める環境変数を付けている:" "配布物の launcher に環境変数"
  build; rm -f "${w_dir}/GSE_起動.bat"; expect_red "launcher（.bat）が無い" "Windows の配布物から launcher を消す"
  build; printf 'MZ..%s..\n' 's1.mode' > "${w_dir}/gse-next.exe"
  expect_red "実体が段 1 を知らない" "gse-next.exe に GSE_S1_MODE が無い"
  build; rm -rf "${m_dir}/gse-next.app"; expect_red "gse-next の実体が無い" "macOS の .app を消す"
  build; ( cd "$fix/dist" && python3 -c "
import zipfile
src = zipfile.ZipFile('win.zip')
with zipfile.ZipFile('win2.zip', 'w') as z:
    for n in src.namelist():
        if not n.endswith('/eh3.mode'):
            z.writestr(n, src.read(n))
    z.writestr('S1_実施用_Windows/eh3.mode', b'')
" && mv win2.zip win.zip )
  expect_red "win.zip: eh3.mode が混ざっている" "zip の中の eh3.mode も見る"
  build; ARGS=(--audience self --dist "$fix/dist/none.zip"); expect_red "配布物が無い" "無いパス"
  build; printf 'not a zip\n' > "$fix/dist/bad.zip"; ARGS=(--audience self --dist "$fix/dist/bad.zip")
  expect_red "フォルダでも zip でもない" "壊れた zip"

  echo
  echo "=== selftest 5: 点検の指摘（2026-11-07）の対照 ==="
  # 途中で読めないメンバーがあっても緑に倒れない（両者一致の HIGH・chmod 000 で再現された）。
  build; chmod 000 "${w_dir}/gse-next.exe"; ARGS=(--audience self --dist "${w_dir}" --os-only windows)
  expect_red "最後まで走らなかった" "読めない gse-next.exe（フォルダ）"
  chmod 644 "${w_dir}/gse-next.exe"
  build; ( cd "$fix/dist" && python3 -c "
import zipfile
b = bytearray(open('win.zip', 'rb').read())
z = zipfile.ZipFile('win.zip')
i = z.getinfo('S1_実施用_Windows/gse-next.exe')
off = i.header_offset + 30 + len(i.filename.encode()) + len(i.extra)
b[off] ^= 0xff
open('win.zip', 'wb').write(bytes(b))
" ); ARGS=(--audience self --dist "$fix/dist/win.zip" --os-only windows)
  expect_red "最後まで走らなかった" "CRC の壊れた gse-next.exe（zip）"
  # Windows の環境変数は大文字小文字を区別しない（両者一致）。
  local dp_lower
  dp_lower="$(printf 'set %s=1' "$(printf '%s' "${DP_WORD}" | tr 'A-Z' 'a-z')")"
  build; bat_add_ "$bat" "${dp_lower}"
  expect_red "launcher がプローブを止める環境変数を付けている" "launcher に小文字の環境変数"
  build; bat_add_ "${w_dir}/GSE_起動.bat" "${dp_lower}"
  expect_red "launcher がプローブを止める環境変数を付けている:" "配布物の launcher に小文字の環境変数"
  build; mkdir -p "${w_dir}/tools"; printf '%s\r\n' "${dp_line}" > "${w_dir}/tools/x.cmd"
  expect_red "launcher がプローブを止める環境変数を付けている:" "下の階層の .cmd も見る"
  # 印の名前の大文字小文字と階層（security HIGH・MEDIUM）。
  build; : > "${m_dir}/EH3.mode"; expect_red "大文字を含む名前の印" "EH3.mode（大文字）"
  build; : > "${m_dir}/gse-next.app/Contents/eh3.mode"; expect_red "根以外の階層" ".app の中の eh3.mode"
  build; ln -s "${w_dir}/s1.mode" "${w_dir}/link.txt"; expect_red "名前に異常がある" "シンボリックリンク"
  build; ( cd "$fix/dist" && python3 -c "
import zipfile, warnings
warnings.simplefilter('ignore')
with zipfile.ZipFile('win.zip', 'a') as z:
    z.writestr('S1_実施用_Windows/s1.mode', b'audience=participants')
" ); ARGS=(--audience self --dist "$fix/dist/win.zip" --os-only windows)
  expect_red "名前に異常がある" "zip の中の同名の s1.mode（見る中身と配る中身がずれうる）"
  build; ( cd "$fix/dist" && python3 -c "
import zipfile
with zipfile.ZipFile('win.zip', 'a') as z:
    z.writestr('S1_実施用_Windows/../evil.txt', b'x')
" ); ARGS=(--audience self --dist "$fix/dist/win.zip" --os-only windows)
  expect_red "名前に異常がある" "zip の中の .. を含む名前"
  build; ( cd "$fix/dist" && python3 -c "
import zipfile
with zipfile.ZipFile('win.zip', 'a') as z:
    z.writestr('__MACOSX/S1_実施用_Windows/._s1.mode', b'x')
" ); ARGS=(--audience self --dist "$fix/dist/win.zip" --os-only windows)
  expect_rc 0 "zip の __MACOSX/ は無視する"
  # 組み立ての書き出しの形（LOW・両者）。
  build; printf '\n%s; : > "$M/s1''.mode"\n' '[ "$MODE" = s1 ] && true' >> "$fix/w/${BUILD}"
  expect_red "分岐の外で s1.mode" "分岐の形の後ろに書き出しを続けた行"
  build; printf '\n: > "${W}/s1''.mode"\n' >> "$fix/w/${BUILD}"
  expect_red "分岐の外で s1.mode" "\${W} の形の書き出し"
  # 同意の印はフェンスの外にちょうど 1 回（security MEDIUM）。
  build; sed -i.bak "s/^${self_body}\$/audience=participants/" "${w_dir}/s1.mode"
  printf '# 同意\n```\n%s\n```\n' "${approved}" > "$cons"
  ARGS=(--audience participants --consent "$cons" --dist "${w_dir}" --os-only windows)
  expect_red "承認の印（行頭の" "印がコードのフェンスの中にあるだけ"
  printf '# 同意\n%s\n%s\n' "${approved}" "${approved}" > "$cons"
  expect_red "承認の印が 2 回" "印が 2 回ある"
  # タグの後に依存の固定（package-lock.json）が動いても古いとみなす（security LOW）。
  build; printf '{}\n' > "$fix/w/package-lock.json"; commit_ "lock"
  expect_red "は古い" "タグの後に package-lock.json が動く"

  echo
  echo "=== selftest 6: /cross-review（Claude ∥ Codex）の対照 ==="
  build; rm -f "${w_dir}/pubkey.txt"; expect_red "自動送信に要るファイルが無い: pubkey.txt" "Windows の pubkey.txt を消す"
  build; rm -f "${m_dir}/g1-submit.json"; expect_red "自動送信に要るファイルが無い: g1-submit.json" "macOS の g1-submit.json を消す"
  build; rm -f "${m_dir}/gse-next.app/Contents/MacOS/gse-submit"; expect_red "自動送信に要るファイルが無い: gse-next.app" "macOS の gse-submit を消す"
  build; : > "${w_dir}/GSE_起動.bat"; expect_red "launcher が repo の段 1 の launcher と一致しない" "配布物の launcher を空にする"
  build; ( cd "$fix/dist" && python3 -c "
import zipfile
zi = zipfile.ZipInfo('S1_実施用_Windows/link')
zi.external_attr = (0o120777) << 16
with zipfile.ZipFile('win.zip', 'a') as z:
    z.writestr(zi, 's1.mode')
" ); ARGS=(--audience self --dist "$fix/dist/win.zip" --os-only windows)
  expect_red "名前に異常がある" "zip の中のシンボリックリンク"
  build; ARGS=(--audience self --dist "$fix/dist/S1_実施用_Windows"); expect_red "両方の配布物を渡していない" "Windows だけを渡す"
  build; ARGS=(--audience self --dist "${w_dir}" --os-only windows); expect_rc 0 "Windows だけを --os-only windows で渡す"
  build; ARGS=(--audience self --dist "${w_dir}" --os-only macos); expect_red "macOS の配布物が無い" "--os-only macos に Windows だけ"
  build; ARGS=(--audience self --dist "${w_dir}" --os-only linux); expect_rc 2 "知らない --os-only"
  build; printf '%s\n' "  o1)" "    WIN_LAUNCHER_SRC=\"\$HERE/launch-s1-windows.bat\"" "    ;;" >> "$fix/w/${BUILD}"
  expect_red "段 1 の launcher（launch-s1-windows.bat）を入れていない" "o1 の枝に段 1 の launcher"
  build; printf 'x\n' > "$fix/w/vite.config.ts"; commit_ "vite"
  expect_red "は古い" "タグの後に vite.config.ts が動く"
  build; git -C "$fix/w" tag -d v9.9.9 > /dev/null 2>&1; git -C "$fix/w" tag zz-s1-not-release > /dev/null 2>&1
  expect_red "リリースタグが 1 つも無い" "v で始まらないタグは数えない"
  build; git -C "$fix/w" checkout -q -b side; printf '// side\n' >> "$fix/w/src-tauri/src/s1.rs"; commit_ "side"
  git -C "$fix/w" tag v9.9.10 > /dev/null 2>&1; git -C "$fix/w" checkout -q main
  expect_green "リリースタグがある（v9.9.9）" "main に入っていない新しいタグは飛ばし、祖先のタグを選ぶ"
  git -C "$fix/w" tag -d v9.9.9 > /dev/null 2>&1
  expect_red "main の祖先であるリリースタグが 1 つも無い" "main に入っていないタグしか無い"
  build; sed -i.bak "s/^${self_body}\$/audience=participants/" "${w_dir}/s1.mode"
  printf '# 同意\n~~~\n%s\n~~~\n' "${approved}" > "$cons"
  ARGS=(--audience participants --consent "$cons" --dist "${w_dir}" --os-only windows)
  expect_red "承認の印（行頭の" "印が ~~~ のフェンスの中にあるだけ"

  echo
  echo "=== selftest 7: /cross-review 2 巡目の対照 ==="
  build; git clone -q "$fix/origin.git" "$fix/other" 2>/dev/null
  printf '// remote\n' >> "$fix/other/src-tauri/src/s1.rs"
  git -C "$fix/other" add -A > /dev/null 2>&1
  git -C "$fix/other" -c user.email=s@e -c user.name=s commit -qm remote > /dev/null 2>&1
  git -C "$fix/other" push -q origin main 2>/dev/null
  expect_red "リモートの main と違う" "リモートの main が進んでいるのに fetch していない"
  git -C "$fix/w" fetch -q origin 2>/dev/null
  expect_red "は古い" "fetch すると、リモートの main の変更で古いとわかる"
  build; git -C "$fix/w" remote remove origin; expect_red "origin が無い" "origin が無い"
  build; git -C "$fix/w" remote set-url origin "$fix/nowhere.git"; expect_red "リモートの main を読めない" "リモートを読めない"
  build; printf '%s\n' 'v9.9.8' > "${w_dir}/s1-release-tag.txt"; ARGS=(--audience self --dist "${w_dir}" --os-only windows)
  expect_red "s1-release-tag.txt が v9.9.9 でない" "配布物のタグの記録が古い"
  build; rm -f "${m_dir}/s1-release-tag.txt"; expect_red "s1-release-tag.txt が v9.9.9 でない" "配布物にタグの記録が無い"
  build; : > "${w_dir}/pubkey.txt"; expect_red "自動送信に要るファイルが無い: pubkey.txt" "0 バイトの pubkey.txt"
  build; rm -f "${m_dir}/gse-next.app/Contents/Resources/resources/pubkey.txt"
  expect_red "自動送信に要るファイルが無い: gse-next.app/contents/resources" "macOS の .app の中の鍵を消す"
  build; printf 'x\n' > "${w_dir}/run.ps1"; expect_red "迂回しうる入口" "根の .ps1"
  build; printf '\n# x\n' >> "${m_dir}/初回セットアップ_mac.sh"; expect_red "初回セットアップが無いか" "セットアップを書き換える"
  build; rm -f "${m_dir}/初回セットアップ_mac.sh"; expect_red "初回セットアップが無いか" "セットアップを消す"
  build; ln -s "${w_dir}/s1.mode" "${w_dir}/$(printf 'a\nHAS_EH3=0\nb')"; : > "${w_dir}/eh3.mode"
  ARGS=(--audience self --dist "${w_dir}" --os-only windows)
  expect_red "名前に異常がある" "改行を含む名前で出力の行を偽る"
  expect_red "eh3.mode が混ざっている" "偽の行があっても本物の eh3.mode を見逃さない"
  build; printf '\n: > "$M"/s1''.mode\n' >> "$fix/w/${BUILD}"
  expect_red "分岐の外で s1.mode" "引用が / の前で閉じる書き出し"
  # ditto の zip の形（UTF-8 の印なし・名前は NFD）でも読める（実物の O1 の zip で誤って赤になった）。
  build; ( cd "$fix/dist" && python3 -c "
import os, unicodedata, zipfile
with zipfile.ZipFile('mac.zip', 'w') as z:
    for d, _, fs in os.walk('S1_実施用_macOS'):
        for f in fs:
            full = os.path.join(d, f)
            z.write(full, unicodedata.normalize('NFD', full))
b = bytearray(open('mac.zip', 'rb').read())
for sig, off in ((b'PK\x03\x04', 6), (b'PK\x01\x02', 8)):
    i = b.find(sig)
    while i >= 0:
        b[i + off] &= 0xF7
        i = b.find(sig, i + 4)
open('mac.zip', 'wb').write(bytes(b))
z = zipfile.ZipFile('mac.zip')
assert not any(i.flag_bits & 0x800 for i in z.infolist())
" ) && ARGS=(--audience self --dist "${w_dir}" --dist "$fix/dist/mac.zip")
  expect_rc 0 "UTF-8 の印の無い・NFD の名前の macOS の zip"

  echo
  echo "────────────────────────────────────────"
  echo "  selftest: 通過 ${sp} 件 / 失敗 ${sf} 件"
  if [ "${sf}" -eq 0 ]; then
    echo "  ✅ 門の各検査は実際に発火している。"
    return 0
  fi
  echo "  ❌ 空回りしている検査がある。上の ❌ を直すこと。"
  return 1
}

if [ "$MODE" = selftest ]; then
  selftest; exit $?
fi

run_checks

echo
echo "────────────────────────────────────────"
echo "  通過 ${PASS} 件 / 未達 ${FAIL} 件（--audience ${AUDIENCE}）"
if [ "${FAIL}" -eq 0 ]; then
  echo "  ✅ 段 1 の配布物を配ってよい状態です（${AUDIENCE}）。"
  exit 0
fi
echo "  ❌ まだ配れません。上の ❌ を全部消すこと。"
echo "────────────────────────────────────────"
exit 1
