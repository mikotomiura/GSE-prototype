#!/usr/bin/env bash
# issue 028 acceptance — 公開物の書き方（判断 36）に合わせる整理
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
L="${K}/logger"

echo "[028] 公開物の書き方の整理"
run_ok "AC1 公開物の書き方の違反が 0 件（papers/ime-observation 全体）" "${PY}" "$(dirname "$0")/_style_check.py" papers/ime-observation
run_ok "AC2 kit/check.sh が緑" bash "${K}/check.sh"
run_ok "AC2 kit/check.sh --compile が緑" bash "${K}/check.sh" --compile
run_ok "AC2 check-shell-portability が緑" bash scripts/check-shell-portability.sh
run_ok "AC3 check_manifest.py --self が緑" "${PY}" "${L}/check_manifest.py" --self
run_ok "AC3 check_manifest_upstream.internal.py --against-upstream が緑" "${PY}" "${L}/check_manifest_upstream.internal.py" --against-upstream
if grep -rqF -- "--against-gse" papers/ 2>/dev/null; then ng "AC3 旧名 --against-gse が papers/ に残っている"; else ok "AC3 旧名 --against-gse が papers/ に無い"; fi
if grep -rqE '"gse_(path|last_commit|repo_commit|range_sha256)"' "${L}" 2>/dev/null; then ng "AC3 manifest に旧名の gse_* の欄が残っている"; else ok "AC3 manifest の欄は upstream_* に改名済み"; fi
forbid_gse_changes
finish
