#!/usr/bin/env bash
# issue 024 acceptance — 公開 repo への書き出し
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
X="${K}/export/export.py"

echo "[024] 公開 repo への書き出し"
for f in "${X}" "${K}/export/README.md" papers/ime-observation/CITATION.cff papers/ime-observation/.zenodo.json; do need_file "${f}"; done
selftest_ok "${X}"
need_grep "${X}" "被験者 ID を混ぜると止まる" "AC2 selftest ケース: 被験者 ID を混ぜると止まる"
need_grep "${X}" "メールを混ぜると止まる" "AC2 selftest ケース: メールを混ぜると止まる"
need_grep "${X}" "逐語コピーの中の .steering/ は通る" "AC2 selftest ケース: 逐語コピーの中の .steering/ は通る（許可リスト）"
need_grep "${X}" "文献番号は通る" "AC2 selftest ケース: 文献番号は通る"
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
list () { (cd "$1" && find . -type f | LC_ALL=C sort | while IFS= read -r f; do "${PY}" -c "import hashlib,sys; print(sys.argv[1], hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${f}"; done); }
L1="$( [ -d "${TMP}/e1" ] && list "${TMP}/e1" )"
if [ -n "${L1}" ] && [ "${L1}" = "$( [ -d "${TMP}/e2" ] && list "${TMP}/e2" )" ]; then ok "AC5 2 回の書き出しがバイト一致"; else ng "AC5 書き出しが無い、または 2 回が一致しない"; fi

# AC6
run_exit 2 "AC6 ライセンスが無ければ exit 2（★ M12 の前）" "${PY}" "${X}" --out "${TMP}/e3"

check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/(kit/export/(export\.py|README\.md)|CITATION\.cff|\.zenodo\.json)$'
finish
