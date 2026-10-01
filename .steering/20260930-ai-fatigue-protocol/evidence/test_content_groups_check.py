"""content_groups_check.py（design.md §7.7）の検査。ネットワークに出ない・抄録を読まない。"""
import unittest

import content_groups_check as K

PRIMARY = dict(kind="一次研究", pop="医療者", ai="記録支援・下書き", design="無作為化")
REVIEW = dict(kind="レビュー等", pop="—", ai="—", design="—")


class TestValues(unittest.TestCase):
    def test_defined_values_pass(self):
        self.assertEqual(K.check_values("A", PRIMARY), [])
        self.assertEqual(K.check_values("A", REVIEW), [])
        self.assertEqual(K.check_values("A", dict(PRIMARY, pop="不明", ai="不明", design="不明")), [])

    def test_spelling_variants_fail(self):
        # 読み手が表記を変えた値（半角の空白の欠け・半角の括弧・別の語）は通さない
        self.assertTrue(K.check_values("A", dict(PRIMARY, ai="生成AI・対話")))
        self.assertTrue(K.check_values("A", dict(PRIMARY, pop="働く人(医療・教育の外)")))
        self.assertTrue(K.check_values("A", dict(PRIMARY, design="混合法")))
        self.assertTrue(K.check_values("A", dict(PRIMARY, kind="レビュー")))

    def test_review_must_have_dashes(self):
        self.assertTrue(K.check_values("A", dict(REVIEW, pop="医療者")))
        self.assertTrue(K.check_values("A", dict(REVIEW, design="-")))  # 半角のハイフンは違う

    def test_group_name(self):
        self.assertEqual(K.group_name(PRIMARY), "医療者｜記録支援・下書き｜無作為化")
        self.assertEqual(K.group_name(REVIEW), "レビュー等")

    def test_diff_axes(self):
        self.assertEqual(K.diff_axes(PRIMARY, dict(PRIMARY)), [])
        self.assertEqual(K.diff_axes(PRIMARY, dict(PRIMARY, design="横断調査")), ["design"])
        self.assertEqual(K.diff_axes(PRIMARY, REVIEW), ["kind", "pop", "ai", "design"])


class TestNormalize(unittest.TestCase):
    def test_only_listed_variants_are_fixed(self):
        v, n = K.normalize(dict(PRIMARY, ai="生成AI・対話"))
        self.assertEqual((v["ai"], n), ("生成 AI・対話", 1))
        self.assertEqual(K.check_values("A", v), [])
        v, n = K.normalize(dict(PRIMARY, ai="AI一般・導入"))
        self.assertEqual((v["ai"], n), ("AI 一般・導入", 1))
        # 表に無い表記ゆれは直さず、check_values が止める
        v, n = K.normalize(dict(PRIMARY, ai="生成AI"))
        self.assertEqual(n, 0)
        self.assertTrue(K.check_values("A", v))
        # 別の軸の同じ文字列は直さない
        v, n = K.normalize(dict(PRIMARY, pop="生成AI・対話"))
        self.assertEqual(n, 0)


class TestWrap(unittest.TestCase):
    def test_no_text_lost_and_lines_short(self):
        text = " ".join(f"word{i}" for i in range(2000))
        lines = K.wrap("抄録", text)
        self.assertTrue(all(len(l) <= K.WRAP for l in lines))
        self.assertEqual(" ".join(l.strip() for l in lines), "- 抄録: " + text)
        self.assertTrue(all(l.startswith("  ") for l in lines[1:]))

    def test_short_value_is_one_line(self):
        self.assertEqual(K.wrap("題名", "A  short\n title"), ["- 題名: A short title"])


if __name__ == "__main__":
    unittest.main()
