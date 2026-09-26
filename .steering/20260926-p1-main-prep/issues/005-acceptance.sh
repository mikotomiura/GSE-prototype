#!/usr/bin/env bash
# issue 005（nested CV の fold と metric 表）の AC 検査
set -uo pipefail
fail() { echo "[acceptance 005] NG: $*" >&2; exit 1; }
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない: $REPO_ROOT"
PY="${PYTHON:-python}"; command -v "$PY" >/dev/null 2>&1 || PY=python3
export PYTHONUTF8=1

for f in scripts/p1_select.py scripts/tests/test_p1_select.py; do [ -f "$f" ] || fail "$f が無い"; done
git diff --quiet main -- src-tauri/prereg/ docs/preregistration-p1-episode.md || fail "凍結文書か凍結 JSON が変わっている"

log="$("$PY" -m unittest scripts.tests.test_p1_select -v 2>&1)"; rc=$?
printf '%s\n' "$log" | tail -5
[ "$rc" -eq 0 ] || fail "unittest が非 0 (rc=$rc)"
printf '%s' "$log" | grep -q "skipped" && fail "skip がある"
for t in test_folds_structure test_folds_deterministic test_seed_from_prereg test_metrics_values test_no_selection_output \
         test_exclusions_and_label_mismatch test_guards test_poles_independent; do
  printf '%s' "$log" | grep -Eq "^${t} .*\.\.\. ok$" || fail "テスト $t が ok で走っていない"
done

# ★ 判断 18 を静的にも: 選択・集約を示す語を識別子に使っていない
grep -Eiq '\b(best|winner|chosen|selected_config|argmin|argmax)\b' scripts/p1_select.py \
  && fail "p1_select.py に選択・集約の語がある（★ 判断 18: 表まで）"
# ★ 判断 11: 転帰を restart から作っていない
grep -q "restart" scripts/p1_select.py && fail "p1_select.py が restart に触れている（★ 判断 11）"
# ★ seed は凍結 JSON から読む（書き写さない）
grep -q "20260921" scripts/p1_select.py && fail "p1_select.py に seed を書き写している（★ search_protocol.seed から読む）"

# ★ 実物の凍結 JSON（pg1 無し）で exit 6
tmpd="$(mktemp -d)" || fail "一時ディレクトリを作れない"; trap 'rm -rf "$tmpd"' EXIT
mkdir -p "$tmpd/grid"; printf 'config_id,participant_id,session_id,pole,t0_ms,outcome\n' > "$tmpd/l.csv"
"$PY" scripts/p1_select.py --grid-out "$tmpd/grid" --labels "$tmpd/l.csv" --out "$tmpd/o.json" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 6 ] || fail "凍結 JSON（pg1 無し）で exit 6 にならない (rc=$rc)"

bash scripts/check-tests-are-wired.sh >/dev/null || fail "AC8: CI に配線されていない"
grep -q "scripts.tests.test_p1_select" .github/workflows/ci.yml || fail "AC8: ci.yml にモジュール名が無い"
echo "[acceptance 005] OK"
