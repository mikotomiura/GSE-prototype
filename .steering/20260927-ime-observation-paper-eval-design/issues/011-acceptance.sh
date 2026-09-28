#!/usr/bin/env bash
# issue 011 acceptance — 単体ロガーの核（逐語コピー・シム・manifest）
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
L="${K}/logger"; M="${L}/Cargo.toml"; C="${L}/check_manifest.py"

echo "[011] 単体ロガーの核"
for f in "${M}" "${L}/Cargo.lock" "${L}/README.md" "${L}/manifest.json" "${C}" "${L}/src/main.rs" "${L}/src/driver_api.rs" \
         "${L}/src/key_category.rs" "${L}/src/input/hook.rs" "${L}/src/input/ime_compose.rs" \
         "${L}/src/input/ime_cloak.rs" "${L}/src/input/ime_mode.rs"; do need_file "${f}"; done

# ★ 逐語コピーの直接照合（manifest を経ずに一次どうしを比べる）
for f in ime_compose.rs ime_cloak.rs ime_mode.rs; do
  if cmp -s "src-tauri/src/input/${f}" "${L}/src/input/${f}"; then ok "逐語コピー: ${f} が GSE とバイト一致"; else ng "逐語コピー: ${f} が GSE と一致しない"; fi
done

# AC1
run_ok "AC1 cargo test が緑（コピーした状態機械のテストを含む）" cargo test --manifest-path "${M}"

# AC2-4
run_ok "AC2 check_manifest.py --self が緑" "${PY}" "${C}" --self
run_ok "AC3 check_manifest.py --against-gse が緑" "${PY}" "${C}" --against-gse
selftest_ok "${C}"

# AC5
run_ok "AC5 cargo build --release が緑" cargo build --release --manifest-path "${M}"
BIN="${L}/target/release/ime-observation-logger.exe"; [ -f "${BIN}" ] || BIN="${L}/target/release/ime-observation-logger"
run_ok "AC5 logger --selftest が緑" "${BIN}" --selftest --out "${TMP}/obs.jsonl"
run_ok "AC5 selftest の出力が obs/1 の検査を通る" "${PY}" "${K}/formats/validate_logs.py" --kind obs "${TMP}/obs.jsonl"
if grep -q '"type":"ime_shadow"' "${TMP}/obs.jsonl"; then ok "AC5 ime_shadow 行が出ている"; else ng "AC5 ime_shadow 行が無い"; fi

# ★ manifest の形: path は kit/logger/ 基準・差し込み口は載せない・抜粋に symbol がある
cat > "${TMP}/mf.py" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8")); fails = []
for e in m.get("entries", []):
    p = str(e.get("path", ""))
    if p.startswith("papers/") or p.startswith("/") or ":" in p: fails.append("path が kit/logger/ 基準でない: " + p)
    if p in ("src/driver_macos.rs", "src/driver_windows.rs"): fails.append("差し込み口を manifest.json に載せている: " + p)
    if e.get("kind") == "excerpt" and not e.get("symbol") and "key_category" not in p: fails.append("抜粋に symbol が無い: " + p)
kinds = sorted({str(e.get("kind")) for e in m.get("entries", [])})
if "file" not in kinds or "excerpt" not in kinds: fails.append("file / excerpt のエントリが無い: %r" % kinds)
for f in fails: print("NG:", f)
sys.exit(1 if fails else 0)
EOF
run_ok "manifest.json の形（path の基準・差し込み口を載せない）" "${PY}" "${TMP}/mf.py" "${L}/manifest.json"
if grep -q '@excerpt-begin' "${L}/src/key_category.rs" && grep -q '@excerpt-end' "${L}/src/key_category.rs"; then ok "key_category.rs に抜粋の目印がある"; else ng "key_category.rs に // @excerpt-begin / @excerpt-end が無い"; fi

# AC7
for f in "${L}/src/main.rs" "${L}/src/input/hook.rs" "${L}/src/driver_macos.rs" "${L}/src/driver_windows.rs"; do
  forbid_grep "${f}" 'winapi|println!|eprintln!' "AC7 禁止の API・出力が無い: ${f}"
done

# AC6 / AC8
forbid_gse_changes
check_entry_green
only_allowed '^papers/ime-observation/kit/logger/(Cargo\.toml|Cargo\.lock|README\.md|manifest\.json|check_manifest\.py|src/(main\.rs|driver_api\.rs|key_category\.rs|driver_macos\.rs|driver_windows\.rs|input/(mod|hook|ime_compose|ime_cloak|ime_mode)\.rs))$'
finish
