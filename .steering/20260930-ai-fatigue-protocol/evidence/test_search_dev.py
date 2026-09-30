"""search_dev.py の組み立てと数え方の検査（design.md §5）。ネットワークに出ない。

使い方: python -m unittest test_search_dev （このディレクトリで）
"""
import json
import os
import unittest

import search_dev as S

HERE = os.path.dirname(os.path.abspath(__file__))


class TestQuote(unittest.TestCase):
    def test_phrase_and_hyphen_are_quoted(self):
        self.assertEqual(S.quote("machine learning"), '"machine learning"')
        self.assertEqual(S.quote("burn-out"), '"burn-out"')
        self.assertEqual(S.quote("fatigue"), "fatigue")


class TestBuilders(unittest.TestCase):
    def test_epmc(self):
        self.assertEqual(S.epmc_query(["AI", "machine learning"], ["fatigue"]),
                         'TITLE_ABS:(AI OR "machine learning") AND TITLE_ABS:(fatigue)')

    def test_s2_with_and_without_negation(self):
        self.assertEqual(S.s2_query(["AI"], ["fatigue", "burn-out"]), '(AI) + (fatigue | "burn-out")')
        self.assertEqual(S.s2_query(["AI"], ["fatigue"], ["fatigue life"]), '(AI) + (fatigue) + -("fatigue life")')

    def test_eric_searches_title_and_description(self):
        self.assertEqual(S.eric_query(["AI"], ["fatigue"]),
                         "(title:(AI) OR description:(AI)) AND (title:(fatigue) OR description:(fatigue))")

    def test_arxiv_expands_each_term_to_ti_and_abs(self):
        self.assertEqual(S.arxiv_query(["AI"], ["burn-out"]), '(ti:AI OR abs:AI) AND (ti:"burn-out" OR abs:"burn-out")')

    def test_v0_blocks_are_the_fixed_design_values(self):
        v = S.VERSIONS["v0"]
        self.assertEqual(len(v["A"]), 23)
        self.assertEqual(len(v["F"]), 13)
        self.assertEqual(len(v["B1"]), 10)
        self.assertIn("burnt out", v["F"])
        # 範囲の語 C を狭めない（design.md §2.5）
        for t in ("fatigue", "exhaustion", "burnout", "weariness", "depletion"):
            self.assertIn(t, v["F"])

    def test_queries_cover_the_designed_sources(self):
        got = {(s, n) for s, n, _q in S.queries("v0")}
        self.assertEqual(got, {("epmc", "main"), ("epmc", "b1"), ("s2", "main"), ("s2", "main_v2"), ("s2", "b1"),
                               ("eric", "main"), ("arxiv", "main"), ("zenodo", "main")})


class TestRecall(unittest.TestCase):
    def test_norm_doi(self):
        self.assertEqual(S.norm_doi("https://doi.org/10.1016/J.X.1"), "10.1016/j.x.1")
        self.assertEqual(S.norm_doi("doi: 10.1/AB"), "10.1/ab")
        self.assertIsNone(S.norm_doi(""))

    def test_recall_matches_case_insensitively_and_ignores_non_doi_ids(self):
        seeds = {"K1": {"doi": "10.1/AB"}, "K2": {"doi": "10.2/cd"}, "K3": {"doi": None}}
        ids = {("doi", "10.1/ab"), ("s2", "10.2/cd")}
        self.assertEqual(S.recall(ids, seeds), {"K1": True, "K2": False})


class TestSeeds(unittest.TestCase):
    def test_seed_file_is_the_fixed_25(self):
        d = json.load(open(os.path.join(HERE, "seeds.json"), encoding="utf-8"))
        self.assertEqual(len(d), 25)
        groups = {}
        for v in d.values():
            groups[v["group"]] = groups.get(v["group"], 0) + 1
        self.assertEqual(groups, {"term16": 16, "supp3": 3, "seed5": 5, "title1": 1})
        self.assertEqual(len({v["doi"] for v in d.values()}), 25)


class TestGuard(unittest.TestCase):
    def test_get_refuses_urls_outside_the_allow_list(self):
        with self.assertRaises(ValueError):
            S.get("https://api.openalex.org/works?search=x")
        with self.assertRaises(ValueError):
            S.get("http://export.arxiv.org/api/query?search_query=x")


if __name__ == "__main__":
    unittest.main()
