#!/usr/bin/env bash
# issue 016 acceptance — 統計の部品（既知の値）
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
S="${K}/analysis/stats.py"

echo "[016] 統計の部品"
selftest_ok "${S}"
need_grep "${S}" "クラスタ内相関で区間が広がる" "AC4 selftest ケース: クラスタ内相関で区間が広がる（陽性対照）"

cat > "${TMP}/known.py" <<'EOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("stats", sys.argv[1]); s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
fails = []
def near(name, got, want, tol):
    if got is None or abs(got - want) > tol: fails.append("%s: got %r want %r" % (name, got, want))
m = [[9,2,5,8],[6,1,3,2],[8,4,6,8],[7,1,2,6],[10,5,6,9],[6,2,4,7]]
near("ICC(1,1)", s.icc(m, kind="1,1"), 0.1657, 0.0005)
near("ICC(2,1)", s.icc(m, kind="2,1"), 0.2898, 0.0005)
near("ICC(3,1)", s.icc(m, kind="3,1"), 0.7148, 0.0005)
near("Wilson 0/10 hi", s.wilson(0, 10)[1], 0.2775, 0.0005)
near("Wilson 10/10 lo", s.wilson(10, 10)[0], 0.7225, 0.0005)
near("kappa", s.cohen_kappa([[20, 5], [10, 15]]), 0.40, 0.0005)
ba = s.bland_altman([2, 3, 4, 5, 6], [1, 1, 1, 1, 1])
near("BA bias", ba["bias"], 3.0, 0.0005)
near("BA sd", ba["sd"], 1.5811, 0.0005)
near("BA loa_hi", ba["loa_hi"], 3.0 + 1.95996 * 1.5811388, 0.002)
cl = [[1.0, 1.2, 0.9], [2.0, 2.1], [0.5, 0.4, 0.6, 0.5], [1.5]]
mean = lambda cs: sum(v for c in cs for v in c) / sum(len(c) for c in cs)
a = s.cluster_bootstrap(cl, mean, B=500, seed=7); b = s.cluster_bootstrap(cl, mean, B=500, seed=7)
if a != b: fails.append("cluster_bootstrap が同じ seed で違う区間: %r %r" % (a, b))
for f in fails: print("NG:", f)
sys.exit(1 if fails else 0)
EOF
run_ok "AC2/AC3/AC5 既知の値と決定性" "${PY}" "${TMP}/known.py" "${S}"
forbid_grep "${S}" '(^|[^.A-Za-z_])random\.(seed|random|choice|choices|gauss|randint|shuffle)\(' "AC5 グローバルな乱数状態に触らない"

check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/analysis/stats\.py$'
finish
