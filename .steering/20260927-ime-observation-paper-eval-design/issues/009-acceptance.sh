#!/usr/bin/env bash
# issue 009 acceptance — 参照入力欄 Windows (b) TSF 直受け
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os windows
D="${K}/refinput-windows"; M="${D}/Cargo.toml"; T="${D}/src/tsf.rs"; B="${D}/src/bin/refinput_tsf.rs"

echo "[009] 参照入力欄 Windows (b) TSF"
need_file "${T}"; need_file "${B}"

# AC1 / AC2
run_ok "AC1 cargo test が緑" cargo test --manifest-path "${M}"
run_ok "AC2 cargo build --release --bins が緑" cargo build --release --manifest-path "${M}" --bins
BIN="${D}/target/release/refinput_tsf.exe"; [ -f "${BIN}" ] || BIN="${D}/target/release/refinput_tsf"

# AC3
run_ok "AC3 --selftest が緑" "${BIN}" --selftest --out "${TMP}/gt.jsonl"
run_ok "AC3 selftest の出力が gt/1 の検査を通る" "${PY}" "${K}/formats/validate_logs.py" --kind gt "${TMP}/gt.jsonl"
if grep -q '"src":"win_tsf"' "${TMP}/gt.jsonl"; then ok "AC3 src が win_tsf"; else ng "AC3 src が win_tsf でない"; fi

# AC4 / AC5（コメントを除いて見る）
cat > "${TMP}/strip.py" <<'EOF'
import re, sys
src = open(sys.argv[1], encoding="utf-8").read()
src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
print("\n".join(l.split("//")[0] for l in src.splitlines()))
EOF
for f in "${T}" "${B}"; do
  "${PY}" "${TMP}/strip.py" "${f}" > "${TMP}/nocomment.rs"
  if grep -qE '\.(GetText|GetFormattedText|GetCompositionString)[[:space:]]*\(' "${TMP}/nocomment.rs"; then ng "AC4 文字列を取得する API を呼んでいる: ${f}"; else ok "AC4 文字列を取得しない: ${f}"; fi
  if grep -qE 'SetWindowsHookEx|SetWinEventHook|winapi|println!|eprintln!' "${TMP}/nocomment.rs"; then ng "AC5 禁止の API・出力がある: ${f}"; else ok "AC5 他プロセスを見ない・禁止の出力が無い: ${f}"; fi
done

# AC6
if grep -qE 'TSF の道: 道 [12]' "${D}/README.md"; then ok "AC6 README に採った道がある"; else ng "AC6 README に「TSF の道: 道 1|2」の行が無い"; fi

# 008 の bin を壊していない
run_ok "GUARD refinput_imm の selftest が緑のまま" "${D}/target/release/refinput_imm" --selftest --out "${TMP}/gt_imm.jsonl"

# AC7
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/refinput-windows/(Cargo\.toml|Cargo\.lock|README\.md|src/core\.rs|src/tsf\.rs|src/bin/refinput_tsf\.rs)$'
finish
