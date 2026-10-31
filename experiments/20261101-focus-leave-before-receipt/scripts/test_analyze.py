"""analyze.py の境界の合成テスト（記録は使わない）。run.sh が集計の前に回す。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A  # noqa: E402

# 曝露の窓は閉区間 [a, t0]
assert A.any_in([100], 100, 200) and A.any_in([200], 100, 200)
assert not A.any_in([99], 100, 200) and not A.any_in([201], 100, 200)
# 結果の窓は (t0, t0 + h]
assert not A.any_in_open_left([100], 100, 400) and A.any_in_open_left([400], 100, 400)
assert not A.any_in_open_left([401], 100, 400)
# 観測区間に収まる
assert A.inside([(0, 500)], 100, 500) and not A.inside([(0, 499)], 100, 500)
assert not A.inside([(0, 200), (200, 500)], 100, 300)  # 1 つの区間に収まる必要がある
# 片方の群が空・片方の受領が 0 → RR は定まらない
assert A.rr_rd([{"exposed": True, "y": True}])[0] is None
assert A.rr_rd([{"exposed": True, "y": False}, {"exposed": False, "y": True}])[0] is None
assert A.rr_rd([]) == (None, None, None)
rr, rd, _ = A.rr_rd([{"exposed": True, "y": True}, {"exposed": True, "y": False},
                     {"exposed": False, "y": True}, {"exposed": False, "y": False}, {"exposed": False, "y": False}])
assert abs(rr - 1.5) < 1e-12 and abs(rd - (0.5 - 1 / 3)) < 1e-12
# 判定の規則
assert A.verdict([1.01, 2.0], 0) == "precedes"
assert A.verdict([1.0, 2.0], 0) == "not_visible"
assert A.verdict([0.5, 0.99], 0) == "reverse"
assert A.verdict([1.5, 2.0], int(0.05 * A.B) + 1) == "undetermined"
assert A.verdict([1.5, 2.0], int(0.05 * A.B)) == "precedes"
assert A.verdict(None, 0) == "undetermined"
assert A.file_date("gse_o1_20261018_070010.ndjson") == "20261018"
print("test_analyze: ok")
