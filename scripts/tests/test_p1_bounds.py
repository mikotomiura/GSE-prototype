"""Tests for scripts/p1_bounds.py (事前宣言 v1.1 冒頭 (3) の「軸ごとの上下界」).

⚠️★★★ **規則を 1 つずつ固定する。** ★ 各テストは、その規則だけが破れる実装で赤くなるように書く
(⚠️ 「極の順序を前提にする」「非適用の極を幅 0 で埋める」「軸をまたいで min / max を取る」は、
どれも**自然に書けてしまう**誤りで、単純な入力では緑のまま通る)。

⚠️ 本 module は実データも Rust も読まない (★ 入力はテストがその場で作る合成の数だけ)。

実行方法:
    cd GSE-prototype
    PYTHONUTF8=1 python -m unittest scripts.tests.test_p1_bounds -v
"""

import math
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import p1_bounds as pb  # noqa: E402


def _values(baseline=10.0, pointer_b=20.0, modifier_m_plus=5.0):
    return {"baseline": baseline, "pointer_b": pointer_b, "modifier_m_plus": modifier_m_plus}


def _applicable(pointer_b=True, modifier_m_plus=True, baseline=True):
    return {"baseline": baseline, "pointer_b": pointer_b, "modifier_m_plus": modifier_m_plus}


class AxisBoundsTest(unittest.TestCase):
    def test_both_applicable_ok(self):
        r = pb.axis_bounds(_values(baseline=10.0, pointer_b=15.5, modifier_m_plus=12.0), _applicable())
        self.assertEqual(
            r["pointer"],
            {"status": "ok", "min": 10.0, "max": 15.5, "width": 5.5, "poles_used": ["baseline", "pointer_b"]},
        )
        self.assertEqual(
            r["modifier"],
            {"status": "ok", "min": 10.0, "max": 12.0, "width": 2.0, "poles_used": ["baseline", "modifier_m_plus"]},
        )
        # ★ 両極が適用可で値が等しいのは「測って 0 だった」= ok の幅 0 (算出不可ではない)
        r = pb.axis_bounds(_values(baseline=7, pointer_b=7, modifier_m_plus=7), _applicable())
        for axis in ("pointer", "modifier"):
            self.assertEqual(r[axis]["status"], "ok", axis)
            self.assertEqual(r[axis]["width"], 0, axis)

    def test_order_not_assumed(self):
        # ⚠️ 極 B (M+) が baseline より上でも下でも、min / max は値の大小で決まる
        for other_name, axis in (("pointer_b", "pointer"), ("modifier_m_plus", "modifier")):
            for baseline, other in ((10.0, 25.0), (25.0, 10.0)):
                with self.subTest(axis=axis, baseline=baseline, other=other):
                    values = _values()
                    values["baseline"] = baseline
                    values[other_name] = other
                    r = pb.axis_bounds(values, _applicable())[axis]
                    self.assertEqual(r["status"], "ok")
                    self.assertEqual(r["min"], 10.0)
                    self.assertEqual(r["max"], 25.0)
                    self.assertEqual(r["width"], 15.0)

    def test_pointer_b_not_applicable_is_not_computable(self):
        # ★ 非適用の極 B の値は読まない: None でも、それらしい値 (baseline と恒等な値) でも同じ
        for pointer_b in (None, 10.0, 999.0):
            with self.subTest(pointer_b=pointer_b):
                r = pb.axis_bounds(_values(pointer_b=pointer_b), _applicable(pointer_b=False))["pointer"]
                self.assertEqual(r["status"], "not_computable")
                self.assertIsNone(r["min"])
                self.assertIsNone(r["max"])
                self.assertIsNone(r["width"])
                self.assertNotEqual(r["width"], 0)  # ⚠️ 測っていない幅を 0 として報告しない
                self.assertEqual(r["poles_used"], [])
        # ★ ポインタ軸が算出不可でも、修飾キー軸は別に報告できる
        r = pb.axis_bounds(_values(), _applicable(pointer_b=False))
        self.assertEqual(r["modifier"]["status"], "ok")

    def test_m_plus_not_applicable(self):
        sentinel = 8765432.5  # ⚠️ 結果のどこかに出たら、極 M+ を計算した (または漏らした) ことになる
        for m_plus in (None, sentinel):
            with self.subTest(modifier_m_plus=m_plus):
                r = pb.axis_bounds(
                    _values(baseline=10.0, modifier_m_plus=m_plus), _applicable(modifier_m_plus=False)
                )
                self.assertEqual(
                    r["modifier"],
                    {"status": "not_applicable", "min": 10.0, "max": 10.0, "width": 0, "poles_used": ["baseline"]},
                )
                self.assertIsNot(r["modifier"]["width"], None)  # ⚠️ ポインタ軸の算出不可とは違う: 幅は 0
                text = repr(r)
                self.assertNotIn("8765432", text)  # ★ 整数・小数どちらの書式でも
                self.assertNotIn("modifier_m_plus", text)  # ★ 極 M+ の名前も (使った極として) 出さない

    def test_axes_do_not_mix(self):
        base = pb.axis_bounds(_values(baseline=10.0, pointer_b=20.0, modifier_m_plus=5.0), _applicable())
        # ⚠️ 3 極の min / max を取る実装は、ポインタ軸の min が 5 (M+)・修飾キー軸の max が 20 (極 B) になる
        self.assertEqual((base["pointer"]["min"], base["pointer"]["max"]), (10.0, 20.0))
        self.assertEqual((base["modifier"]["min"], base["modifier"]["max"]), (5.0, 10.0))
        # ★ M+ の値・適用可否を変えても、ポインタ軸は変わらない
        for m_plus, applicable in ((-100.0, True), (100.0, True), (5.0, False), (None, False)):
            with self.subTest(modifier_m_plus=m_plus, applicable=applicable):
                r = pb.axis_bounds(
                    _values(baseline=10.0, pointer_b=20.0, modifier_m_plus=m_plus),
                    _applicable(modifier_m_plus=applicable),
                )
                self.assertEqual(r["pointer"], base["pointer"])
        # ★ 極 B の値・適用可否を変えても、修飾キー軸は変わらない
        for pointer_b, applicable in ((-100.0, True), (100.0, True), (20.0, False), (None, False)):
            with self.subTest(pointer_b=pointer_b, applicable=applicable):
                r = pb.axis_bounds(
                    _values(baseline=10.0, pointer_b=pointer_b, modifier_m_plus=5.0),
                    _applicable(pointer_b=applicable),
                )
                self.assertEqual(r["modifier"], base["modifier"])

    def test_invalid_inputs_raise(self):
        nan, inf = float("nan"), math.inf
        cases = {
            "baseline が非適用": (_values(), _applicable(baseline=False)),
            "baseline の値が None": (_values(baseline=None), _applicable()),
            "適用可の極 B の値が None": (_values(pointer_b=None), _applicable()),
            "適用可の極 M+ の値が None": (_values(modifier_m_plus=None), _applicable()),
            "値に知らない極名": ({**_values(), "pointer_a": 1.0}, _applicable()),
            "applicable に知らない極名": (_values(), {**_applicable(), "modifier_m_minus": True}),
            "baseline が NaN": (_values(baseline=nan), _applicable()),
            "適用可の極 B が NaN": (_values(pointer_b=nan), _applicable()),
            "適用可の極 M+ が NaN": (_values(modifier_m_plus=nan), _applicable()),
            "適用可の極 B が inf": (_values(pointer_b=inf), _applicable()),
            "値が bool": (_values(pointer_b=True), _applicable()),
            "値が文字列": (_values(pointer_b="20"), _applicable()),
            "applicable に極が無い": (_values(), {"baseline": True, "pointer_b": True}),
            "applicable が bool でない": (_values(), _applicable(pointer_b="yes")),
        }
        for label, (values, applicable) in cases.items():
            with self.subTest(label):
                with self.assertRaises(ValueError):
                    pb.axis_bounds(values, applicable)


class SummarizeTest(unittest.TestCase):
    def _unit(self, pointer_b_applicable, m_plus_applicable):
        return pb.axis_bounds(
            _values(), _applicable(pointer_b=pointer_b_applicable, modifier_m_plus=m_plus_applicable)
        )

    def test_summarize_counts_statuses(self):
        # (ポインタ軸, 修飾キー軸) = A: (ok, ok) ×3 / B: (not_computable, ok) ×1 /
        #   C: (ok, not_applicable) ×2 / D: (not_computable, not_applicable) ×1
        # ★ 軸ごとの件数が互いに違う値になるようにしてある (⚠️ 軸の取り違え・状態の取り違えを見逃さない)
        units = (
            [self._unit(True, True)] * 3
            + [self._unit(False, True)] * 1
            + [self._unit(True, False)] * 2
            + [self._unit(False, False)] * 1
        )
        self.assertEqual(
            pb.summarize(units),
            {
                "pointer": {"ok": 5, "not_computable": 2, "not_applicable": 0},
                "modifier": {"ok": 4, "not_computable": 0, "not_applicable": 3},
            },
        )
        # ★ 0 単位でも 0 件の状態のキーを残す (⚠️ 「該当なし」と「数えていない」を区別する)
        self.assertEqual(
            pb.summarize([]),
            {
                "pointer": {"ok": 0, "not_computable": 0, "not_applicable": 0},
                "modifier": {"ok": 0, "not_computable": 0, "not_applicable": 0},
            },
        )
        # ★ 知らない状態・軸の欠けた単位は数えずに止める
        with self.assertRaises(ValueError):
            pb.summarize([{"pointer": {"status": "wide"}, "modifier": {"status": "ok"}}])
        with self.assertRaises(ValueError):
            pb.summarize([{"pointer": {"status": "ok"}}])


if __name__ == "__main__":
    unittest.main()
