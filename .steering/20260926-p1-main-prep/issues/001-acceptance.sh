#!/usr/bin/env bash
# issue 001（軸ごとの上下界の結合器）の AC 検査
# ⚠️ loop-run.sh は worktree を cwd にして呼ぶ → repo root は cwd。
set -uo pipefail
fail() { echo "[acceptance 001] NG: $*" >&2; exit 1; }
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない: $REPO_ROOT"
PY="${PYTHON:-python}"; command -v "$PY" >/dev/null 2>&1 || PY=python3
export PYTHONUTF8=1

[ -f scripts/p1_bounds.py ] || fail "scripts/p1_bounds.py が無い"
[ -f scripts/tests/test_p1_bounds.py ] || fail "scripts/tests/test_p1_bounds.py が無い"

log="$("$PY" -m unittest scripts.tests.test_p1_bounds -v 2>&1)"; rc=$?
printf '%s\n' "$log" | tail -5
[ "$rc" -eq 0 ] || fail "unittest が非 0 (rc=$rc)"
printf '%s' "$log" | grep -q "skipped" && fail "skip がある（★ 検査していない緑）"

# ★ AC ↔ test 名: 名前が存在し、かつ ok で走ったこと（⚠️ 名前だけ在って走っていない、を弾く）
for t in test_both_applicable_ok test_order_not_assumed test_pointer_b_not_applicable_is_not_computable \
         test_m_plus_not_applicable test_axes_do_not_mix test_invalid_inputs_raise test_summarize_counts_statuses; do
  printf '%s' "$log" | grep -Eq "^${t} .*\.\.\. ok$" || fail "テスト $t が ok で走っていない"
done

# ★ AC3 の検査の検査: not_computable で width が 0 を返す変異を与えると、テストが赤になること
tmpd="$(mktemp -d)" || fail "一時ディレクトリを作れない"
trap 'rm -rf "$tmpd"' EXIT
mkdir -p "$tmpd/scripts/tests"
cp scripts/p1_bounds.py "$tmpd/scripts/"; cp scripts/tests/test_p1_bounds.py "$tmpd/scripts/tests/"
: > "$tmpd/scripts/__init__.py"; : > "$tmpd/scripts/tests/__init__.py"
"$PY" - "$tmpd/scripts/p1_bounds.py" <<'EOF' || fail "変異を注入できない"
import sys, re
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
# axis_bounds の戻り値に後段で細工する: not_computable の width を 0 に書き換える
s += "\n\n_orig_axis_bounds = axis_bounds\n" \
     "def axis_bounds(*a, **k):\n" \
     "    r = _orig_axis_bounds(*a, **k)\n" \
     "    for ax in r.values():\n" \
     "        if ax.get('status') == 'not_computable':\n" \
     "            ax['width'] = 0\n" \
     "    return r\n"
open(p, "w", encoding="utf-8").write(s)
EOF
( cd "$tmpd" && "$PY" -m unittest scripts.tests.test_p1_bounds >/dev/null 2>&1 ) \
  && fail "変異（not_computable の幅を 0 にする）でもテストが緑（★ AC3 が空振り）"

# AC8: 配線
bash scripts/check-tests-are-wired.sh >/dev/null || fail "AC8: CI に配線されていない"
grep -q "scripts.tests.test_p1_bounds" .github/workflows/ci.yml || fail "AC8: ci.yml にモジュール名が無い"

echo "[acceptance 001] OK"
