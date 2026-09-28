#!/usr/bin/env bash
# issue 012 acceptance — 単体ロガーの macOS ドライバ
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os macos
L="${K}/logger"; M="${L}/Cargo.toml"; C="${L}/check_manifest.py"; DM="${L}/src/driver_macos.rs"

echo "[012] 単体ロガーの macOS ドライバ"
for f in "${DM}" "${L}/src/driver_macos/keymap.rs" "${L}/src/driver_macos/ime_source.rs" "${L}/manifest.macos.json"; do need_file "${f}"; done

# AC1 / AC2
run_ok "AC1 cargo test が緑（macOS）" cargo test --manifest-path "${M}"
run_ok "AC2 cargo build --release が緑（macOS）" cargo build --release --manifest-path "${M}"

# AC3
run_ok "AC3 check_manifest.py --self が緑" "${PY}" "${C}" --self
run_ok "AC3 check_manifest.py --against-upstream が緑" "${PY}" "${C}" --against-upstream

# AC4: hook_macos.rs の抜粋が 2 件で、2 つの関数を含む
cat > "${TMP}/m4.py" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
ex = [e for e in m.get("entries", []) if e.get("kind") == "excerpt" and str(e.get("upstream_path", "")).endswith("hook_macos.rs")]
syms = sorted(str(e.get("symbol")) for e in ex)
ok = {"is_observed_key", "macos_vk_to_vk"} <= set(syms)
print("hook_macos excerpts:", len(ex), syms)
sys.exit(0 if ok else 1)
EOF
run_ok "AC4 hook_macos.rs の抜粋の symbol に is_observed_key / macos_vk_to_vk" "${PY}" "${TMP}/m4.py" "${L}/manifest.macos.json"

# AC5 / AC6: コールバックの本体とタップの種類
cat > "${TMP}/cb.py" <<'EOF'
import glob, re, sys
files = [sys.argv[1]] + sorted(glob.glob(sys.argv[2] + "/*.rs"))
src = {f: open(f, encoding="utf-8").read() for f in files}
names = []
for s in src.values():
    names += re.findall(r"//\s*tap-callback:\s*([A-Za-z_][A-Za-z0-9_]*)", s)
if not names:
    print("NG: // tap-callback: <name> のコメントが無い"); sys.exit(1)
fails = []
for name in names:
    body = None
    for s in src.values():
        m = re.search(r"fn\s+" + name + r"\s*[<(]", s)
        if m:
            j = s.find("{", m.end()); d = 0
            for k in range(j, len(s)):
                if s[k] == "{": d += 1
                elif s[k] == "}":
                    d -= 1
                    if d == 0: body = s[j:k + 1]; break
            break
    if body is None:
        fails.append("コールバック %s の本体が見つからない" % name); continue
    code = "\n".join(l.split("//")[0] for l in body.splitlines())
    for pat in ["println!", "eprintln!", "tracing::", "info!", "debug!", "warn!", "error!"]:
        if pat in code:
            fails.append("コールバック %s の中に %s" % (name, pat))
alls = "\n".join(src.values())
if not re.search(r"ListenOnly|kCGEventTapOptionListenOnly", alls):
    fails.append("listen-only のタップを作っていない")
if re.search(r"CGEventTapOptions::Default|kCGEventTapOptionDefault", alls):
    fails.append("改変可能なタップ（Default）を作っている")
for f in fails: print("NG:", f)
sys.exit(1 if fails else 0)
EOF
run_ok "AC5/AC6 コールバックでログを出さず、listen-only で作る" "${PY}" "${TMP}/cb.py" "${DM}" "${L}/src/driver_macos"

# AC7
BIN="${L}/target/release/ime-observation-logger"
run_ok "AC7 logger --selftest が緑" "${BIN}" --selftest --out "${TMP}/obs.jsonl"
run_ok "AC7 selftest の出力が obs/1 の検査を通る" "${PY}" "${K}/formats/validate_logs.py" --kind obs "${TMP}/obs.jsonl"

# AC8
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/logger/(manifest\.macos\.json|src/driver_macos\.rs|src/driver_macos/(keymap|ime_source|tests)\.rs)$'
style_ok
finish
