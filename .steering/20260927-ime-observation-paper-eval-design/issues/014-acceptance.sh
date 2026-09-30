#!/usr/bin/env bash
# issue 014 acceptance — 単体ロガーの Windows ドライバ (2)
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os windows
L="${K}/logger"; M="${L}/Cargo.toml"; C="${L}/check_manifest.py"; CU="${L}/check_manifest_upstream.internal.py"; DW="${L}/src/driver_windows.rs"; SUB="${L}/src/driver_windows"

echo "[014] 単体ロガーの Windows ドライバ (2)"
for f in "${SUB}/cloak.rs" "${SUB}/candidate.rs" "${L}/manifest.windows.json"; do need_file "${f}"; done
# AC8（判断 41・2026-09-28）: 候補窓の観測関数を核に渡す
need_grep "${L}/src/driver_windows.rs" "candidate_window_observer" "AC8 driver_windows.rs が候補窓の観測関数を核に渡す"
need_grep "${SUB}/candidate.rs" "is_stale_winevent_active" "AC8 candidate.rs が stale のリセットを行う"

run_ok "AC1 cargo test が緑（Windows）" cargo test --manifest-path "${M}"
run_ok "AC2 cargo build --release が緑" cargo build --release --manifest-path "${M}"
run_ok "AC3 check_manifest.py --self が緑" "${PY}" "${C}" --self
run_ok "AC3 check_manifest_upstream.internal.py --against-upstream が緑" "${PY}" "${CU}" --against-upstream

cat > "${TMP}/m4.py" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
ex = [e for e in m.get("entries", []) if e.get("kind") == "excerpt"]
win = [e for e in ex if str(e.get("upstream_path", "")).endswith("ime_windows.rs")]
hw = set(str(e.get("symbol")) for e in ex if str(e.get("upstream_path", "")).endswith("hook_windows.rs"))
print("ime_windows:", len(win), "hook_windows symbols:", sorted(hw))
sys.exit(0 if (len(win) >= 1 and all(e.get("symbol") for e in win) and {"is_observed_key", "classify_ime_nav_key"} <= hw) else 1)
EOF
run_ok "AC4 ime_windows.rs の抜粋があり、013 の抜粋が残っている" "${PY}" "${TMP}/m4.py" "${L}/manifest.windows.json"

cat > "${TMP}/cb.py" <<'EOF'
import glob, re, sys
files = [sys.argv[1]] + sorted(glob.glob(sys.argv[2] + "/*.rs"))
raw = {f: open(f, encoding="utf-8").read() for f in files}
def strip(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return "\n".join(l.split("//")[0] for l in s.splitlines())
code = {f: strip(s) for f, s in raw.items()}
alls = "\n".join(code.values())
fails = []
for pat in ["WH_GETMESSAGE", "WH_CALLWNDPROC", "winapi", "println!", "eprintln!", "WINEVENT_INCONTEXT"]:
    if pat in alls: fails.append("禁止: %s" % pat)
names = []
for s in raw.values(): names += re.findall(r"//\s*winevent-callback:\s*([A-Za-z_][A-Za-z0-9_]*)", s)
if not names: fails.append("// winevent-callback: <name> のコメントが無い")
for name in names:
    body = None
    for s in code.values():
        m = re.search(r"fn\s+" + name + r"\s*[<(]", s)
        if m:
            j = s.find("{", m.end()); d = 0
            for k in range(j, len(s)):
                if s[k] == "{": d += 1
                elif s[k] == "}":
                    d -= 1
                    if d == 0: body = s[j:k + 1]; break
            break
    if body is None: fails.append("コールバック %s の本体が無い" % name); continue
    for pat in ["tracing::", "println!", "Mutex", ".lock()", "DwmGetWindowAttribute"]:
        if pat in body: fails.append("%s の中に %s" % (name, pat))
for f in fails: print("NG:", f)
sys.exit(1 if fails else 0)
EOF
run_ok "AC5/AC6 禁じられたフックとコールバックの規則" "${PY}" "${TMP}/cb.py" "${DW}" "${SUB}"

BIN="${L}/target/release/ime-observation-logger.exe"
run_ok "AC7 logger --selftest が緑" "${BIN}" --selftest --out "${TMP}/obs.jsonl"
run_ok "AC7 selftest の出力が obs/1 の検査を通る" "${PY}" "${K}/formats/validate_logs.py" --kind obs "${TMP}/obs.jsonl"
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/logger/(manifest\.windows\.json|src/driver_windows\.rs|src/driver_windows/(cloak|candidate)\.rs)$'
style_ok
finish
