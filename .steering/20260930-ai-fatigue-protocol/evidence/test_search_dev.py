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


class TestFetchFixes(unittest.TestCase):
    """★ 2026-10-01（decisions.md 判断 11）の取得の直し。語は v0 のまま変えない。"""

    def test_zenodo_split_keeps_every_F_term_and_the_whole_A_block(self):
        v = S.VERSIONS["v0"]
        subs = S.zenodo_subqueries(v["A"], v["F"])
        self.assertEqual(len(subs), len(v["F"]))
        a_block = "(" + " OR ".join(map(S.quote, v["A"])) + ")"
        for t, sq in zip(v["F"], subs):
            self.assertEqual(sq, f"{a_block} AND ({S.quote(t)})")
        self.assertIn("zenodo", S.SPLIT_BY_F)

    def test_zenodo_pages_within_the_anonymous_limit(self):
        self.assertLessEqual(S.ZENODO_PAGE, 25)
        seen = []
        orig = S.get
        try:
            S.get = lambda url, tries=6: seen.append(url) or json.dumps({"hits": {"total": 30, "hits": [
                {"doi": f"10.5281/zenodo.{len(seen)}{i}"} for i in range(25 if len(seen) == 1 else 5)]}})
            ids = S.fetch_ids("zenodo", "(AI) AND (fatigue)")
        finally:
            S.get = orig
        self.assertEqual(len(seen), 2)  # 30 件を 25 件ずつ 2 ページ
        self.assertTrue(all("size=25" in u for u in seen))
        self.assertEqual(len(ids), 30)

    def test_get_retries_an_incomplete_read(self):
        import http.client
        calls = []

        class _R:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                calls.append(1)
                if len(calls) == 1:
                    raise http.client.IncompleteRead(b"x", 10)
                return b'{"ok": 1}'

        orig_open, orig_sleep = S.OPENER.open, S.time.sleep
        try:
            S.OPENER.open = lambda req, timeout=90: _R()
            S.time.sleep = lambda s: None
            self.assertEqual(S.get("https://zenodo.org/api/records?q=x"), '{"ok": 1}')
        finally:
            S.OPENER.open, S.time.sleep = orig_open, orig_sleep
        self.assertEqual(len(calls), 2)

    def test_eric_doi_only_from_doi_links(self):
        self.assertEqual(S.eric_doi("http://dx.doi.org/10.1111/BJET.70043"), "10.1111/bjet.70043")
        self.assertEqual(S.eric_doi("https://doi.org/10.1/x"), "10.1/x")
        self.assertIsNone(S.eric_doi("https://files.eric.ed.gov/fulltext/ED1.pdf"))
        self.assertIsNone(S.eric_doi("https://example.org/doi.org/10.1/x"))
        self.assertIsNone(S.eric_doi(None))

    def test_s2_presence_uses_arxiv_id_for_arxiv_dois(self):
        seen = []
        orig = S.get
        try:
            S.get = lambda url, tries=6: seen.append(url) or "{}"
            self.assertTrue(S.seed_presence("s2", "10.48550/arXiv.2609.00506"))
            self.assertTrue(S.seed_presence("s2", "10.1016/j.x.1"))
        finally:
            S.get = orig
        self.assertTrue(seen[0].startswith("https://api.semanticscholar.org/graph/v1/paper/ARXIV:2609.00506?"))
        self.assertTrue(seen[1].startswith("https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.x.1?"))


class TestWiring(unittest.TestCase):
    """★ 判断 17（code-reviewer MEDIUM）: 直しが補助の関数だけでなく、取得の経路に配線されていること。"""

    def _with_get(self, payloads):
        seen = []
        orig = S.get

        def fake(url, tries=6):
            seen.append(url)
            return json.dumps(payloads[min(len(seen), len(payloads)) - 1])
        S.get = fake
        return seen, orig

    def test_fetch_eric_adds_dois_from_url(self):
        seen, orig = self._with_get([{"response": {"numFound": 2, "docs": [
            {"id": "EJ1", "url": "http://dx.doi.org/10.1/AB"}, {"id": "EJ2", "url": "https://files.eric.ed.gov/x.pdf"}]}}])
        try:
            ids = S.fetch_ids("eric", "q")
        finally:
            S.get = orig
        self.assertEqual(ids, {("eric", "EJ1"), ("eric", "EJ2"), ("doi", "10.1/ab")})
        self.assertIn("fields=id%2Curl", seen[0])

    def test_fetch_s2_adds_arxiv_dois(self):
        seen, orig = self._with_get([{"data": [{"paperId": "p1", "externalIds": {"ArXiv": "2609.00506"}},
                                               {"paperId": "p2", "externalIds": {"DOI": "10.1/X"}}]}])
        orig_sleep = S.time.sleep
        try:
            S.time.sleep = lambda s: None
            ids = S.fetch_ids("s2", "q")
        finally:
            S.get, S.time.sleep = orig, orig_sleep
        self.assertIn(("doi", "10.48550/arxiv.2609.00506"), ids)
        self.assertIn(("doi", "10.1/x"), ids)
        self.assertIn(("s2", "p1"), ids)

    def test_main_fetch_splits_zenodo_by_F(self):
        import tempfile
        calls = []
        orig = S.fetch_ids
        try:
            S.fetch_ids = lambda src, q: calls.append((src, q)) or {("doi", f"10.1/{len(calls)}")}
            with tempfile.TemporaryDirectory() as td:
                S.main(["fetch", "--version", "v0", "--source", "zenodo", "--store", td])
                d = json.load(open(os.path.join(td, "ids_v0_zenodo_main.json"), encoding="utf-8"))
        finally:
            S.fetch_ids = orig
        v = S.VERSIONS["v0"]
        self.assertEqual([q for _s, q in calls], S.zenodo_subqueries(v["A"], v["F"]))
        self.assertEqual(d["subqueries"], S.zenodo_subqueries(v["A"], v["F"]))
        self.assertEqual(len(d["ids"]), len(v["F"]))


class TestDoiGuard(unittest.TestCase):
    """★ 判断 17（security-checker L-2）: DOI の . と .. の区切りをパスに入れない。"""

    def test_accepts_real_dois_and_rejects_dot_segments(self):
        import doi_guard as G
        self.assertEqual(G.doi_path("10.1016/S0301-0511(96)05223-4", safe="/()"), "10.1016/S0301-0511(96)05223-4")
        self.assertEqual(G.doi_path("10.1234/AB"), "10.1234/AB")
        for bad in ["10.1234/../../members", "10.1234/./x", "10.1234/x/..", "11.1234/x", "10.1/x", "10.1234/", "", None,
                    "10.1234/a b"]:
            with self.assertRaises(ValueError):
                G.doi_path(bad)

    def test_seed_presence_uses_the_guard(self):
        with self.assertRaises(ValueError):
            S.seed_presence("s2", "10.1234/../../x")


class TestRound1Fixes(unittest.TestCase):
    """★ 判断 18（Codex 1 巡目）: arXiv の ID の形・取得が総数に届いたか・記録の版と式の一致。"""

    def test_s2_presence_rejects_bad_arxiv_ids(self):
        for bad in ["10.48550/arxiv.x/../../members", "10.48550/arxiv.2609.00506?x=1", "10.48550/arxiv.2609.00506#a"]:
            with self.assertRaises(ValueError):
                S.seed_presence("s2", bad)
        seen = []
        orig = S.get
        try:
            S.get = lambda url, tries=6: seen.append(url) or "{}"
            self.assertTrue(S.seed_presence("s2", "10.48550/arxiv.hep-th/9901001v2"))
        finally:
            S.get = orig
        self.assertIn("/paper/ARXIV:hep-th/9901001v2?", seen[0])

    def test_fetch_records_whether_the_total_was_reached(self):
        pages = [f"<opensearch:totalResults>3</opensearch:totalResults><id>http://arxiv.org/abs/2601.0000{i}v1</id>"
                 for i in (1, 2)] + ["<opensearch:totalResults>3</opensearch:totalResults>"]
        calls = []
        orig, orig_sleep = S.get, S.time.sleep
        try:
            S.get = lambda url, tries=6: calls.append(url) or pages[len(calls) - 1]
            S.time.sleep = lambda s: None
            S.fetch_ids("arxiv", "q")
        finally:
            S.get, S.time.sleep = orig, orig_sleep
        self.assertEqual(S.STATS, {"total": 3, "raw": 1})  # 1 ページ目だけ受け取って 500 件ずつの次で終わる

    def test_main_fetch_marks_incomplete(self):
        import tempfile
        orig = S.fetch_ids

        def fake(src, q):
            S.STATS.clear()
            S.STATS.update(total=5, raw=4)
            return {("doi", "10.1234/x")}
        try:
            S.fetch_ids = fake
            with tempfile.TemporaryDirectory() as td:
                S.main(["fetch", "--version", "v0", "--source", "epmc", "--name", "main", "--store", td])
                d = json.load(open(os.path.join(td, "ids_v0_epmc_main.json"), encoding="utf-8"))
        finally:
            S.fetch_ids = orig
        self.assertFalse(d["complete"])
        self.assertEqual(d["stats"], [{"total": 5, "raw": 4, "complete": False}])

    def test_check_store_record_refuses_other_versions_and_queries(self):
        q = dict((f"{s} {n}", q) for s, n, q in S.queries("v0"))["epmc main"]
        ok = {"version": "v0", "source": "epmc", "name": "main", "query": q}
        S.check_store_record(ok, "v0", "epmc", "main", q)
        for bad in [dict(ok, version="v1"), dict(ok, query=q + " x"), dict(ok, name="b1")]:
            with self.assertRaises(SystemExit):
                S.check_store_record(bad, "v0", "epmc", "main", q)


class TestRecordsByRef(unittest.TestCase):
    """★ 判断 13: 記録の JSON は検索式を SHA-256 で持ち、式の本文は search-dev.md にある。"""

    def test_by_ref_replaces_queries_and_keeps_the_rest(self):
        obj = {"version": "v0", "runs": [{"source": "epmc", "query": "q1", "count": 3,
                                          "subqueries": ["a", "b"], "nested": {"query": "q2"}}]}
        got = S.by_ref(obj)
        r = got["runs"][0]
        self.assertNotIn("query", r)
        self.assertEqual(r["query_sha256"], S.qsha("q1"))
        self.assertEqual(r["subqueries_sha256"], [S.qsha("a"), S.qsha("b")])
        self.assertEqual(r["nested"], {"query_sha256": S.qsha("q2")})
        self.assertEqual(r["count"], 3)

    def test_committed_records_match_the_code_and_search_dev_md(self):
        want = {(s, n): S.qsha(q) for s, n, q in S.queries("v0")}
        md = open(os.path.join(HERE, "search-dev.md"), encoding="utf-8").read()
        for s, n, q in S.queries("v0"):
            self.assertIn(q, md, f"search-dev.md に {s} {n} の式の本文が無い")
            self.assertIn(S.qsha(q), md)
        for fn in sorted(os.listdir(HERE)):
            if not (fn.startswith("search_dev_") and fn.endswith(".json")) or "seeds" in fn:
                continue
            d = json.load(open(os.path.join(HERE, fn), encoding="utf-8"))
            for r in d["runs"]:
                self.assertNotIn("query", r, fn)
                self.assertEqual(r["query_sha256"], want[(r["source"], r["name"])], fn)
                if r.get("subqueries_sha256") is not None:  # ★ 判断 17: 分けた式もコードと突き合わせる
                    v = S.VERSIONS["v0"]
                    self.assertEqual(r["subqueries_sha256"], [S.qsha(q) for q in S.zenodo_subqueries(v["A"], v["F"])], fn)
                    for q in S.zenodo_subqueries(v["A"], v["F"]):
                        self.assertIn(S.qsha(q), md)


class TestGuard(unittest.TestCase):
    def test_get_refuses_urls_outside_the_allow_list(self):
        with self.assertRaises(ValueError):
            S.get("https://api.openalex.org/works?search=x")
        with self.assertRaises(ValueError):
            S.get("http://export.arxiv.org/api/query?search_query=x")


if __name__ == "__main__":
    unittest.main()
