#!/usr/bin/env bash
# issue 024 acceptance — 公開 repo への書き出し
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
X="${K}/export/export.py"

echo "[024] 公開 repo への書き出し"
for f in "${X}" "${K}/export/README.md" papers/ime-observation/CITATION.cff papers/ime-observation/.zenodo.json; do need_file "${f}"; done
selftest_ok "${X}"
# ★ 2026-09-28・判断 36: ケース名は英語。逐語コピーはコメントを除いて書き出すので、作業記録のパスの許可リストは要らなくなった。
need_grep "${X}" "a participant identifier stops the export" "AC2 selftest ケース: 被験者 ID を混ぜると止まる"
need_grep "${X}" "an email address stops the export" "AC2 selftest ケース: メールを混ぜると止まる"
need_grep "${X}" "a bracketed reference number passes" "AC2 selftest ケース: 文献番号は通る"
need_grep "${X}" "an internal marker word stops the export" "AC2 selftest ケース（判断 36）: 禁止語（内部の名前・パス・記号）を混ぜると止まる"
need_grep "${X}" "comments are stripped from verbatim copies" "AC2 selftest ケース（判断 36）: 逐語コピーのコメントを除く（文字列の中の // や # は残す）"
need_grep "${X}" "upstream fields are dropped from the public manifest" "AC2 selftest ケース（判断 36）: 公開側の manifest から出どころの欄を落とす"
need_grep "${X}" "internal notes are not exported" "AC2 selftest ケース（判断 36）: *.internal.md を書き出さない"
run_ok "AC .zenodo.json が JSON" "${PY}" -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8'))" papers/ime-observation/.zenodo.json

# AC3 / AC4 / AC5
run_ok "AC3 実物を書き出せる（試験モード）" "${PY}" "${X}" --out "${TMP}/e1" --allow-missing-license
run_ok "AC3 実物を書き出せる（2 回目）" "${PY}" "${X}" --out "${TMP}/e2" --allow-missing-license
if [ -f "${TMP}/e1/kit/logger/manifest.json" ]; then ok "AC3 manifest.json がある"; else ng "AC3 manifest.json が無い"; fi
BAD="$(cd "${TMP}/e1" 2>/dev/null && find . \( -name '*.jsonl' -o -name '*.ndjson' -o -type d -name target -o -type d -name sealed \) -print | grep -v '^\./kit/corpus/data/' || true)"
if [ -d "${TMP}/e1" ] && [ -z "${BAD}" ]; then ok "AC3 生ログ・生成物が無い"; else ng "AC3 除外されていない: $(echo "${BAD}" | tr '\n' ' ')"; fi
if [ -f "${TMP}/e1/kit/logger/check_manifest.py" ] && (cd "${TMP}/e1" && "${PY}" kit/logger/check_manifest.py --self >/dev/null 2>&1); then
  ok "AC4 書き出した側で check_manifest.py --self が緑"
else ng "AC4 書き出した側で manifest が照合できない"; fi
# ★ 判断 36: 書き出した全体に禁止語・地の文の日本語が無い（逐語コピーもコメントを除いた後なので対象）
if [ -d "${TMP}/e1" ] && "${PY}" "$(dirname "$0")/_style_check.py" --root "${TMP}/e1" . > "${TMP}/style-e1.out" 2>&1; then
  ok "AC 判断 36: 書き出した全体が公開物の書き方に合う"
else ng "AC 判断 36: 書き出した側に違反がある（$(tail -n 1 "${TMP}/style-e1.out" 2>/dev/null)）"; fi
if [ -d "${TMP}/e1" ] && ! grep -rqE '"(gse_|upstream_)' "${TMP}/e1/kit/logger/" 2>/dev/null; then ok "AC 判断 36: 公開側の manifest に出どころの欄が無い"; else ng "AC 判断 36: 公開側の manifest に出どころの欄が残っている"; fi
if [ -d "${TMP}/e1" ] && [ -z "$(find "${TMP}/e1" -name '*.internal.md' -print)" ]; then ok "AC 判断 36: *.internal.md が無い"; else ng "AC 判断 36: *.internal.md が書き出されている"; fi
list () { (cd "$1" && find . -type f | LC_ALL=C sort | while IFS= read -r f; do "${PY}" -c "import hashlib,sys; print(sys.argv[1], hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${f}"; done); }
L1="$( [ -d "${TMP}/e1" ] && list "${TMP}/e1" )"
if [ -n "${L1}" ] && [ "${L1}" = "$( [ -d "${TMP}/e2" ] && list "${TMP}/e2" )" ]; then ok "AC5 2 回の書き出しがバイト一致"; else ng "AC5 書き出しが無い、または 2 回が一致しない"; fi

# AC6
run_exit 2 "AC6 ライセンスが無ければ exit 2（★ M12 の前）" "${PY}" "${X}" --out "${TMP}/e3"

check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/(kit/export/(export\.py|README\.md)|CITATION\.cff|\.zenodo\.json)$'
style_ok
finish
