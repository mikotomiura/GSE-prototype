#!/usr/bin/env bash
# issue 013 acceptance — 単体ロガーの Windows ドライバ (1)
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os windows
L="${K}/logger"; M="${L}/Cargo.toml"; C="${L}/check_manifest.py"; DW="${L}/src/driver_windows.rs"; SUB="${L}/src/driver_windows"

echo "[013] 単体ロガーの Windows ドライバ (1)"
for f in "${DW}" "${SUB}/keyboard.rs" "${SUB}/ime_winevent.rs" "${L}/manifest.windows.json"; do need_file "${f}"; done

# AC1-3
run_ok "AC1 cargo test が緑（Windows）" cargo test --manifest-path "${M}"
run_ok "AC2 cargo build --release が緑（Windows）" cargo build --release --manifest-path "${M}"
run_ok "AC3 check_manifest.py --self が緑" "${PY}" "${C}" --self
run_ok "AC3 check_manifest.py --against-gse が緑" "${PY}" "${C}" --against-gse

# AC4
cat > "${TMP}/m4.py" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
ex = [e for e in m.get("entries", []) if e.get("kind") == "excerpt" and str(e.get("gse_path", "")).endswith("hook_windows.rs")]
syms = set(str(e.get("symbol")) for e in ex)
print("hook_windows excerpts:", len(ex), sorted(syms))
sys.exit(0 if {"is_observed_key", "classify_ime_nav_key"} <= syms else 1)
EOF
run_ok "AC4 hook_windows.rs の抜粋（is_observed_key / classify_ime_nav_key）" "${PY}" "${TMP}/m4.py" "${L}/manifest.windows.json"

# AC5-7（コメントを除いて見る）
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
for pat in ["WH_GETMESSAGE", "WH_CALLWNDPROC", "winapi", "println!", "eprintln!", "WINEVENT_INCONTEXT", "LLKHF_INJECTED"]:
    if pat in alls: fails.append("禁止: %s" % pat)
if "WINEVENT_OUTOFCONTEXT" not in alls: fails.append("WINEVENT_OUTOFCONTEXT を使っていない")
names = []
for s in raw.values(): names += re.findall(r"//\s*hook-callback:\s*([A-Za-z_][A-Za-z0-9_]*)", s)
if not names: fails.append("// hook-callback: <name> のコメントが無い")
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
    if "CallNextHookEx" not in body: fails.append("%s が CallNextHookEx を呼ばない" % name)
    for pat in ["tracing::", "println!", "Mutex", ".lock()"]:
        if pat in body: fails.append("%s の中に %s" % (name, pat))
for f in fails: print("NG:", f)
sys.exit(1 if fails else 0)
EOF
run_ok "AC5-7 禁じられたフック・コールバックの規則・合成入力を捨てない" "${PY}" "${TMP}/cb.py" "${DW}" "${SUB}"

# AC8
BIN="${L}/target/release/ime-observation-logger.exe"
run_ok "AC8 logger --selftest が緑" "${BIN}" --selftest --out "${TMP}/obs.jsonl"
run_ok "AC8 selftest の出力が obs/1 の検査を通る" "${PY}" "${K}/formats/validate_logs.py" --kind obs "${TMP}/obs.jsonl"
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/logger/(manifest\.windows\.json|src/driver_windows\.rs|src/driver_windows/(keyboard|ime_winevent)\.rs)$'
finish
