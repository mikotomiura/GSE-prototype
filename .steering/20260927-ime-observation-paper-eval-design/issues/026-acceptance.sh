#!/usr/bin/env bash
# issue 026 acceptance — 〔任意〕S9 マウス確定の再現（macOS）
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os macos
D="${K}/refinput-macos"

echo "[026] S9 マウス確定（任意）"
run_ok "AC1 build.sh が緑" bash "${D}/build.sh"
run_ok "AC1 --selftest が緑" "${D}/.build/refinput-macos" --selftest --out "${TMP}/gt.jsonl"
run_ok "AC2 --rect-out 付きの selftest が緑" "${D}/.build/refinput-macos" --selftest --out "${TMP}/gt2.jsonl" --rect-out "${TMP}/rect.json"
run_ok "AC2 rect.json が数 4 つだけ" "${PY}" -c "import json,sys; d=json.load(open(sys.argv[1])); v=list(d.values()) if isinstance(d,dict) else d; sys.exit(0 if len(v)==4 and all(isinstance(x,(int,float)) and not isinstance(x,bool) for x in v) else 1)" "${TMP}/rect.json"
run_ok "AC3 backend_macos.py --probe が緑" "${PY}" "${K}/emit/backend_macos.py" --probe
run_ok "AC4 generate_plan.py --selftest が緑" "${PY}" "${K}/gen/generate_plan.py" --selftest
run_ok "AC4 emit.py --selftest が緑" "${PY}" "${K}/emit/emit.py" --selftest
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/(refinput-macos/RefInput\.swift|emit/backend_macos\.py|gen/recipes\.json)$'
style_ok
finish
