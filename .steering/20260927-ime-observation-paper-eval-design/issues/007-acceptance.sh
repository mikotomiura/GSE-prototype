#!/usr/bin/env bash
# issue 007 acceptance — 参照入力欄 macOS
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os macos
D="${K}/refinput-macos"

echo "[007] 参照入力欄 macOS"
need_file "${D}/RefInput.swift"; need_file "${D}/build.sh"; need_file "${D}/README.md"

# AC1
run_ok "AC1 build.sh が緑" bash "${D}/build.sh"
BIN="${D}/.build/refinput-macos"
if [ -x "${BIN}" ]; then ok "AC1 バイナリがある: ${BIN}"; else ng "AC1 バイナリが無い: ${BIN}"; fi

# AC2
run_ok "AC2 --selftest が緑" "${BIN}" --selftest --out "${TMP}/gt.jsonl"

# AC3
run_ok "AC3 selftest の出力が gt/1 の検査を通る" "${PY}" "${K}/formats/validate_logs.py" --kind gt "${TMP}/gt.jsonl"
if grep -q '"ev":"set_marked"' "${TMP}/gt.jsonl" && grep -q '"ev":"insert_text"' "${TMP}/gt.jsonl"; then ok "AC3 set_marked と insert_text が記録されている"; else ng "AC3 set_marked / insert_text が無い"; fi

# AC4: ⚠️ 渡した文字列が出力に無い
if grep -qE 'にほんご|日本語' "${TMP}/gt.jsonl"; then ng "AC4 本文が出力に漏れている"; else ok "AC4 渡した文字列が出力に無い"; fi

# AC5: ⚠️ 記録関数が String を受け取らない
NAME="$(grep -E '^記録関数の名前: `[A-Za-z_][A-Za-z0-9_]*`' "${D}/README.md" | head -n 1 | sed -E 's/.*`([A-Za-z_][A-Za-z0-9_]*)`.*/\1/')"
if [ -z "${NAME}" ]; then ng "AC5 README に「記録関数の名前: \`<name>\`」の行が無い"
else
  DECL="$("${PY}" -c 'import re,sys; s=open(sys.argv[1],encoding="utf-8").read(); m=re.search(r"func\s+"+sys.argv[2]+r"\s*\((.*?)\)\s*(->[^{]*)?\{", s, re.S); print(m.group(0) if m else "")' "${D}/RefInput.swift" "${NAME}")"
  if [ -z "${DECL}" ]; then ng "AC5 記録関数 ${NAME} の宣言が見つからない"
  elif echo "${DECL}" | grep -q 'String'; then ng "AC5 記録関数 ${NAME} が String を受け取る: ${DECL}"
  else ok "AC5 記録関数 ${NAME} の宣言に String が無い"; fi
fi

# AC6
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/refinput-macos/(RefInput\.swift|build\.sh|README\.md)$'
finish
