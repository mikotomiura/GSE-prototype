#!/usr/bin/env bash
# issue 027 acceptance — 〔任意〕現代文コーパスの取り込み口
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
F="${K}/corpus/build_modern.py"

echo "[027] 現代文コーパス（任意）"
selftest_ok "${F}"
need_grep "${F}" "build_corpus" "AC2 build_corpus を使う"
forbid_grep "${F}" '^def [A-Za-z_]*reading' "AC2 読みの付与を再実装していない"
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/corpus/build_modern\.py$'
finish
