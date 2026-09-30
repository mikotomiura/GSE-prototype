#!/usr/bin/env bash
# issue 023 acceptance — E3 の器
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
E="${K}/e3"; SRC="experiments/20260903-o1-runtime-cost/scripts"

echo "[023] E3 の器"
for f in sample-macos.sh sample-windows.sh calibrate-cpu.sh run_e3.sh summarize_e3.py README.md PROVENANCE.internal.md; do need_file "${E}/${f}"; done
selftest_ok "${E}/summarize_e3.py"
need_grep "${E}/summarize_e3.py" "all zeros means not measured" "AC3 selftest ケース: 全部 0 は測れていない（陰性対照）"

# AC2: 計測器の写しは、注釈（# の行・#! を除く）と空行を除くと、差はプロセス名の行だけ（判断 60）
cat > "${TMP}/diff.py" <<'EOF'
import difflib, sys
def code(path):
    out = []
    for l in open(path, encoding="utf-8").read().splitlines():
        t = l.strip()
        if not t or (t.startswith("#") and not t.startswith("#!")):
            continue
        out.append(l)
    return out
fails = []
for name in ["sample-macos.sh", "sample-windows.sh"]:
    a = code(sys.argv[1] + "/" + name)
    b = code(sys.argv[2] + "/" + name)
    for l in difflib.unified_diff(a, b, lineterm="", n=0):
        if l.startswith(("---", "+++", "@@")): continue
        if l.startswith("+") and "E3_PROC" not in l: fails.append("%s: 追加行に E3_PROC が無い: %s" % (name, l))
        if l.startswith("-") and "gse-next" not in l: fails.append("%s: 消した行がプロセス名の行ではない: %s" % (name, l))
for f in fails: print("NG:", f)
sys.exit(1 if fails else 0)
EOF
run_ok "AC2 計測器の写しは注釈を除くとプロセス名の行だけが違う" "${PY}" "${TMP}/diff.py" "${SRC}" "${E}"
# AC2 の陽性対照: 写しの実行される行を 1 行変えると検出する（検査が常に真でないこと）
mkdir -p "${TMP}/mut"; cp "${E}/sample-macos.sh" "${E}/sample-windows.sh" "${TMP}/mut/"
echo 'echo extra-line' >> "${TMP}/mut/sample-macos.sh"
run_fail "AC2 陽性対照: 実行される行を足すと検出する" "${PY}" "${TMP}/diff.py" "${SRC}" "${TMP}/mut"

forbid_grep "${E}/run_e3.sh" 'i-understand-this-sends-keys' "AC4 run_e3.sh が送出しない"
for f in run_e3.sh summarize_e3.py calibrate-cpu.sh README.md; do forbid_grep "${E}/${f}" 'experiments/20260903' "AC5 ${f} が GSE の experiments/ を参照しない"; done
forbid_grep "${E}/README.md" '[Cc]opied' "AC5 公開の README に写した関係を書かない（判断 61）"
for f in sample-macos.sh sample-windows.sh; do
  need_grep "${E}/PROVENANCE.internal.md" "${SRC}/${f}" "AC5 PROVENANCE.internal.md に ${f} の元のパス"
  h="$("${PY}" -c "import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${SRC}/${f}")"
  need_grep "${E}/PROVENANCE.internal.md" "${h}" "AC5 PROVENANCE.internal.md に ${f} の元の SHA-256"
done
run_ok "AC6 check-shell-portability が緑" bash scripts/check-shell-portability.sh
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/e3/(sample-macos\.sh|sample-windows\.sh|calibrate-cpu\.sh|run_e3\.sh|summarize_e3\.py|README\.md|PROVENANCE\.internal\.md)$'
style_ok
finish
