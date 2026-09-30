"""search_dev_summary.py の検査（ネットワークに出ない）。使い方: python -m unittest test_search_dev_summary"""
import unittest

import search_dev_summary as M


class TestGroups(unittest.TestCase):
    def test_group_of(self):
        self.assertEqual(M.group_of("AF001"), "DB")
        self.assertEqual(M.group_of("S04-41"), "S04 作業負荷・時間の比較（S04-41〜S04-87）")
        self.assertEqual(M.group_of("S04-87"), "S04 作業負荷・時間の比較（S04-41〜S04-87）")
        self.assertEqual(M.group_of("S04-40"), "S04 のほか")
        self.assertEqual(M.group_of("S04-88"), "S04 のほか")
        self.assertEqual(M.group_of("S15-01"), "S08・S15")
        self.assertEqual(M.group_of("S12-03"), "S12")


class TestSummarize(unittest.TestCase):
    def test_union_overlap_and_noise_terms(self):
        ids = {("epmc", "main"): {("doi", "10.1/a"), ("epmc", "MED:1")}, ("s2", "main"): {("doi", "10.1/a"), ("doi", "10.1/b")},
               ("s2", "main_v2"): {("doi", "10.1/a")}, ("eric", "main"): {("eric", "EJ1")}, ("arxiv", "main"): set(),
               ("zenodo", "main"): {("doi", "10.1/c")}, ("epmc", "b1"): {("doi", "10.1/d")}, ("s2", "b1"): {("doi", "10.1/a")}}
        recs = [dict(key="AF001", doi="10.1/A"), dict(key="S04-41", doi="10.1/z"), dict(key="S12-01", doi=None)]
        noise = {"epmc": dict(n=2, n_doi_population=9, sample_sha256="x",
                              titles=[{"title": "AI fatigue in nurses"}, {"title": "Fatigue life of alloys"}])}
        out = M.summarize(ids, recs, noise)
        self.assertEqual(out["main_union"]["n_doi"], 3)
        self.assertEqual(out["main_union"]["n_non_doi_not_deduplicated"], 2)
        self.assertEqual(out["b1_not_in_main"], 1)
        self.assertEqual(out["s2_main_minus_v2"], 1)
        o = out["overlap_259"]
        self.assertEqual((o["with_doi"], o["without_doi"], o["in_main_union"]), (2, 1, 1))
        self.assertEqual(o["groups"]["S12"], dict(total=1, not_in_union=1))
        self.assertEqual(o["groups"]["DB"], dict(total=1, not_in_union=0))
        n = out["noise"]["epmc"]
        self.assertEqual((n["titles"], n["a_in_title"], n["f_in_title"], n["both"]), (2, 1, 2, 1))


class TestLoadStore(unittest.TestCase):
    """★ 判断 18: 版を混ぜない・式がコードと違う記録で止まる。"""

    def _write(self, td, fn, **kw):
        import json
        import os
        json.dump(dict(ids=[["doi", "10.1234/a"]], **kw), open(os.path.join(td, fn), "w", encoding="utf-8"))

    def test_reads_only_the_version_and_checks_queries(self):
        import tempfile
        q = {(s, n): q for s, n, q in M.S.queries("v0")}
        with tempfile.TemporaryDirectory() as td:
            self._write(td, "ids_v0_epmc_main.json", version="v0", source="epmc", name="main", query=q[("epmc", "main")])
            self._write(td, "ids_v1_epmc_main.json", version="v1", source="epmc", name="main", query="other")
            got = M.load_store(td, "v0")
            self.assertEqual(list(got), [("epmc", "main")])
            self._write(td, "ids_v0_s2_main.json", version="v0", source="s2", name="main", query="changed")
            with self.assertRaises(SystemExit):
                M.load_store(td, "v0")


if __name__ == "__main__":
    unittest.main()
