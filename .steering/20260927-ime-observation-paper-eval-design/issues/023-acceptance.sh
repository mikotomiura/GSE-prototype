#!/usr/bin/env bash
# issue 023 acceptance — E3 の器
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
E="${K}/e3"; SRC="experiments/20260903-o1-runtime-cost/scripts"

echo "[023] E3 の器"
for f in sample-macos.sh sample-windows.sh calibrate-cpu.sh run_e3.sh summarize_e3.py README.md; do need_file "${E}/${f}"; done
selftest_ok "${E}/summarize_e3.py"
need_grep "${E}/summarize_e3.py" "all zeros means not measured" "AC3 selftest ケース: 全部 0 は測れていない（陰性対照）"

# AC2: 写しの差はプロセス名の行だけ
cat > "${TMP}/diff.py" <<'EOF'
import difflib, sys
fails = []
for name in ["sample-macos.sh", "sample-windows.sh", "calibrate-cpu.sh"]:
    a = open(sys.argv[1] + "/" + name, encoding="utf-8").read().splitlines()
    b = open(sys.argv[2] + "/" + name, encoding="utf-8").read().splitlines()
    for l in difflib.unified_diff(a, b, lineterm="", n=0):
        if l.startswith(("---", "+++", "@@")): continue
        if l.startswith("+") and "E3_PROC" not in l: fails.append("%s: 追加行に E3_PROC が無い: %s" % (name, l))
        if l.startswith("-") and "gse-next" not in l: fails.append("%s: 消した行がプロセス名の行ではない: %s" % (name, l))
for f in fails: print("NG:", f)
sys.exit(1 if fails else 0)
EOF
run_ok "AC2 写しの差はプロセス名の行だけ" "${PY}" "${TMP}/diff.py" "${SRC}" "${E}"

forbid_grep "${E}/run_e3.sh" 'i-understand-this-sends-keys' "AC4 run_e3.sh が送出しない"
for f in run_e3.sh summarize_e3.py; do forbid_grep "${E}/${f}" 'experiments/20260903' "AC5 ${f} が GSE の experiments/ を参照しない"; done
run_ok "AC6 check-shell-portability が緑" bash scripts/check-shell-portability.sh
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/e3/(sample-macos\.sh|sample-windows\.sh|calibrate-cpu\.sh|run_e3\.sh|summarize_e3\.py|README\.md)$'
style_ok
finish
