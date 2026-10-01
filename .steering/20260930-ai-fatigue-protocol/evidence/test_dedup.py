"""dedup.py の観点（design.md §7.2）の陽性・陰性の検査。ネットワークに出ない。

使い方: python -m unittest test_dedup （このディレクトリで）
"""
import unittest

import dedup as D


def rec(key, title, doi=None, year=2026, label="", sheet="候補"):
    return dict(key=key, sheet=sheet, title=title, label=label, year=year, journal="", pubtype="", doi=doi)


def meta(authors, relations=(), source="crossref"):
    return dict(source=source, type="journal-article", title="", container="", issued=None,
                authors=[[f, ""] for f in authors], relations=[list(r) for r in relations])


def persp(pairs, a, b):
    for p in pairs:
        if {p["a"], p["b"]} == {a, b}:
            return p["perspectives"]
    return []


class TestHelpers(unittest.TestCase):
    def test_norm_title_and_ratio(self):
        self.assertEqual(D.norm_title("AI <i>Fatigue</i>: A Study!"), "ai fatigue a study")
        self.assertGreater(D.title_ratio("AI fatigue among students", "AI Fatigue Among Students."), 0.99)
        self.assertEqual(D.title_ratio("", "x"), 0.0)

    def test_sample_numbers(self):
        self.assertEqual(D.sample_numbers("A survey of 460 knowledge workers (N = 1,045) in 2024."), {460, 1045})
        self.assertEqual(D.sample_numbers("Published in 2025 with 12 students."), set())

    def test_countries_word_boundary(self):
        self.assertEqual(D.countries("Students in China and the UK."), {"china", "uk"})
        self.assertNotIn("india", D.countries("Indiana University students"))

    def test_label_families(self):
        self.assertEqual(D.label_families("Honggang W, Khoso AK, Althubyani AR 2026"), ["honggang", "khoso", "althubyani"])

    def test_preprint_prefix(self):
        self.assertTrue(D.is_preprint_doi("10.21203/rs.3.rs-1/v1"))
        self.assertFalse(D.is_preprint_doi("10.1016/j.x"))
        self.assertFalse(D.is_preprint_doi(None))


class TestDetect(unittest.TestCase):
    def test_p1_relation_inside_the_set_only(self):
        recs = [rec("K1", "Alpha", "10.1/a"), rec("K2", "Beta", "10.1/b"), rec("K3", "Gamma", "10.1/c")]
        m = {"K1": meta(["x"], [("has-preprint", "10.1/b"), ("has-preprint", "10.9/outside")]), "K2": meta(["y"]),
             "K3": meta(["z"], [("references", "10.1/a")])}
        pairs = D.detect(recs, m, {})
        self.assertEqual(persp(pairs, "K1", "K2"), ["P1"])
        self.assertEqual(persp(pairs, "K1", "K3"), [])  # 関係の種類が版でない

    def test_p1_datacite_type_is_case_insensitive(self):
        recs = [rec("K1", "Alpha", "10.5281/zenodo.1"), rec("K2", "Beta", "10.5281/zenodo.2")]
        m = {"K1": meta(["x"], [("isversionof", "10.5281/zenodo.2")], source="datacite"), "K2": meta(["y"])}
        self.assertIn("P1", persp(D.detect(recs, m, {}), "K1", "K2"))

    def test_p2_high_ratio_or_low_ratio_with_shared_author(self):
        recs = [rec("K1", "AI fatigue among students in higher education", year=2020),
                rec("K2", "AI fatigue among students in higher education.", year=2024),
                rec("K3", "AI fatigue among nurses in hospitals", year=2020),
                rec("K4", "AI fatigue among nurses in clinics", year=2024)]
        m = {"K1": meta(["lee"]), "K2": meta(["kim"]), "K3": meta(["park", "choi"]), "K4": meta(["choi", "han"])}
        pairs = D.detect(recs, m, {})
        self.assertIn("P2", persp(pairs, "K1", "K2"))
        self.assertIn("P2", persp(pairs, "K3", "K4"))  # 比 0.6 以上で著者 1 名が重なる
        self.assertNotIn("P2", persp(pairs, "K1", "K3"))

    def test_p3_two_shared_or_first_author_within_a_year(self):
        recs = [rec("K1", "Alpha", year=2025), rec("K2", "Beta", year=2026), rec("K3", "Gamma", year=2020),
                rec("K4", "Delta", year=2025)]
        m = {"K1": meta(["wang", "khoso"]), "K2": meta(["wang", "li"]), "K3": meta(["wang", "zhao"]),
             "K4": meta(["zhang", "khoso", "li"])}
        pairs = D.detect(recs, m, {})
        self.assertIn("P3", persp(pairs, "K1", "K2"))  # 筆頭が同じ・年の差 1
        self.assertNotIn("P3", persp(pairs, "K1", "K3"))  # 筆頭は同じだが年の差 5・重なり 1
        self.assertNotIn("P3", persp(pairs, "K2", "K4"))  # 筆頭が違い、重なりは 1 名（li）だけ

    def test_p3_needs_two_shared_when_first_author_differs(self):
        recs = [rec("K1", "Alpha", year=2020), rec("K2", "Beta", year=2026)]
        m = {"K1": meta(["zhang", "khoso"]), "K2": meta(["li", "khoso"])}
        self.assertNotIn("P3", persp(D.detect(recs, m, {}), "K1", "K2"))
        m = {"K1": meta(["zhang", "khoso", "li"]), "K2": meta(["li", "khoso"])}
        self.assertIn("P3", persp(D.detect(recs, m, {}), "K1", "K2"))

    def test_p4_preprint_with_similar_title(self):
        recs = [rec("K1", "Burnout and generative AI use in nursing", "10.21203/rs.3.rs-9/v1"),
                rec("K2", "Burnout and generative AI use among nurses", "10.1016/j.nurse.1"),
                rec("K3", "Something entirely different", "10.1016/j.other.2")]
        pairs = D.detect(recs, {"K1": meta(["a"]), "K2": meta(["b"]), "K3": meta(["c"])}, {})
        self.assertIn("P4", persp(pairs, "K1", "K2"))
        self.assertEqual(persp(pairs, "K1", "K3"), [])

    def test_p5_same_n_needs_country_or_author(self):
        recs = [rec("K1", "Alpha"), rec("K2", "Beta"), rec("K3", "Gamma")]
        m = {"K1": meta(["a"]), "K2": meta(["b"]), "K3": meta(["c"])}
        abs_ = {"K1": "We surveyed 832 students in China.", "K2": "Data from 832 university students in China.",
                "K3": "We surveyed 832 employees in Spain."}
        pairs = D.detect(recs, m, abs_)
        self.assertIn("P5", persp(pairs, "K1", "K2"))
        self.assertNotIn("P5", persp(pairs, "K1", "K3"))


class TestRefine(unittest.TestCase):
    def test_p3_only_pairs_need_two_same_people(self):
        m = {"K1": dict(authors=[["Wang", "Li"], ["Zhang", "Wei"]]), "K2": dict(authors=[["Wang", "Jun"], ["Zhang", "Wei"]]),
             "K3": dict(authors=[["Wang", "Li"], ["Zhang", "Wen"]]), "K4": dict(authors=[["Wang", "L."], ["Zhang", "W"]])}
        pairs = [dict(a="K1", b="K2", perspectives=["P3"]), dict(a="K1", b="K3", perspectives=["P3"]),
                 dict(a="K1", b="K4", perspectives=["P3"]), dict(a="K2", b="K3", perspectives=["P2", "P3"])]
        keep, drop = D.refine(pairs, m)
        self.assertIn(["K1", "K3"], keep)  # 同じ頭文字で 2 名（Wang L・Zhang W）
        self.assertIn(["K1", "K4"], keep)  # 頭文字だけの名でも同じ
        self.assertIn(["K1", "K2"], drop)  # Wang の名が違う → 1 名だけ
        self.assertIn(["K2", "K3"], keep)  # ほかの観点でも当たった組は外さない


if __name__ == "__main__":
    unittest.main()
