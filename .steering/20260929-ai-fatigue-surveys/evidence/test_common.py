"""common.py のテスト（固定の入力だけ。ネットワークは使わない）。"""
import io
import json
import os
import tempfile
import unittest
import urllib.error
import urllib.request

from common import (allowed_url, ensure_outside_repo, guarded_opener, is_inside, merge_abstract, open_exclusive,
                    repo_root, same_run, slice_between, write_pair)


class MergeAbstract(unittest.TestCase):
    def test_empty_does_not_overwrite(self):
        s = {}
        merge_abstract(s, "10.1/x", "Europe PMC の抄録")
        merge_abstract(s, "10.1/x", "")
        merge_abstract(s, "10.1/x", None)
        self.assertEqual(s["10.1/x"], "Europe PMC の抄録")

    def test_longer_wins(self):
        s = {}
        merge_abstract(s, "k", "short")
        merge_abstract(s, "k", "a longer abstract")
        merge_abstract(s, "k", "mid")
        self.assertEqual(s["k"], "a longer abstract")

    def test_first_empty_then_text(self):
        s = {}
        merge_abstract(s, "k", "")
        self.assertIn("k", s)
        merge_abstract(s, "k", "text")
        self.assertEqual(s["k"], "text")


class OutsideRepo(unittest.TestCase):
    def test_inside_repo_is_rejected(self):
        root = repo_root()
        self.assertIsNotNone(root)
        for p in [os.path.join(root, "tmp_abs"), os.path.join(root, ".steering", "x"), root.upper() if os.name == "nt" else root]:
            with self.assertRaises(RuntimeError):
                ensure_outside_repo(p, root)

    def test_outside_is_accepted(self):
        root = repo_root()
        with tempfile.TemporaryDirectory() as td:
            if not is_inside(td, root):
                self.assertEqual(ensure_outside_repo(td, root), td)

    def test_sibling_prefix_is_not_inside(self):
        with tempfile.TemporaryDirectory() as td:
            a = os.path.join(td, "repo")
            b = os.path.join(td, "repo-x")
            os.makedirs(a)
            os.makedirs(b)
            self.assertFalse(is_inside(b, a))


class Exclusive(unittest.TestCase):
    def test_existing_file_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "a.json")
            with open_exclusive(p) as fh:
                fh.write("1")
            with self.assertRaises(FileExistsError):
                open_exclusive(p)
            self.assertEqual(open(p, encoding="utf-8").read(), "1")


class Pair(unittest.TestCase):
    def test_pair_shares_run_id(self):
        with tempfile.TemporaryDirectory() as td:
            b, a = os.path.join(td, "bib.json"), os.path.join(td, "abs.json")
            rid = write_pair(b, a, {"runs": []}, {"k": "text"})
            bo, ao = json.load(open(b, encoding="utf-8")), json.load(open(a, encoding="utf-8"))
            self.assertEqual(bo["run_id"], rid)
            self.assertTrue(same_run(bo, ao))
            self.assertEqual(ao["abstracts"], {"k": "text"})

    def test_existing_abstract_file_blocks_both(self):
        with tempfile.TemporaryDirectory() as td:
            b, a = os.path.join(td, "bib.json"), os.path.join(td, "abs.json")
            open(a, "w", encoding="utf-8").write("old")
            with self.assertRaises(FileExistsError):
                write_pair(b, a, {}, {})
            self.assertFalse(os.path.exists(b))
            self.assertEqual(open(a, encoding="utf-8").read(), "old")

    def test_different_runs_do_not_match(self):
        self.assertFalse(same_run({"run_id": "a"}, {"run_id": "b"}))
        self.assertFalse(same_run({}, {}))


class Urls(unittest.TestCase):
    def test_allow_only_prefix_https(self):
        pre = ["https://www.jstage.jst.go.jp/"]
        self.assertTrue(allowed_url("https://www.jstage.jst.go.jp/article/x", pre))
        self.assertFalse(allowed_url("file:///C:/secret.txt", pre))
        self.assertFalse(allowed_url("http://www.jstage.jst.go.jp/article/x", pre))
        self.assertFalse(allowed_url("https://evil.example/https://www.jstage.jst.go.jp/", pre))
        self.assertFalse(allowed_url(None, pre))

    def test_host_is_compared_structurally(self):
        pre = ["https://trusted.example/article/"]
        self.assertTrue(allowed_url("https://trusted.example/article/x", pre))
        self.assertTrue(allowed_url("https://TRUSTED.example:443/article/x", pre))
        for bad in ["https://trusted.example.evil/article/x", "https://trusted.example@evil/article/x",
                    "https://user:pw@trusted.example/article/x", "https://trusted.example:8443/article/x",
                    "https://trusted.example/other/x", "https://trusted.example/articlex"]:
            self.assertFalse(allowed_url(bad, pre), bad)

    def test_prefix_without_trailing_slash_uses_segments(self):
        pre = ["https://trusted.example/article"]
        self.assertTrue(allowed_url("https://trusted.example/article", pre))
        self.assertTrue(allowed_url("https://trusted.example/article/x", pre))
        self.assertFalse(allowed_url("https://trusted.example/article-evil", pre))

    def test_redirect_to_other_host_is_refused(self):
        opener = guarded_opener(["https://trusted.example/"])
        h = next(x for x in opener.handlers if isinstance(x, urllib.request.HTTPRedirectHandler))
        req = urllib.request.Request("https://trusted.example/a")
        with self.assertRaises(urllib.error.URLError):
            h.redirect_request(req, io.BytesIO(), 302, "Found", {}, "https://evil.example/a")
        ok = h.redirect_request(req, io.BytesIO(), 302, "Found", {}, "https://trusted.example/b")
        self.assertEqual(ok.full_url, "https://trusted.example/b")


class Slice(unittest.TestCase):
    def test_stops_at_first_end_marker(self):
        page = "<nav>#author-information-wrap</nav><div class=abstract-wrap>ABS</div><div id=\"author-information-wrap\">A</div>"
        got = slice_between(page, "abstract-wrap>", ['id="author-information-wrap"', "<footer"])
        self.assertEqual(got, "abstract-wrap>ABS</div><div ")

    def test_missing_end_marker_returns_empty(self):
        self.assertEqual(slice_between("x abstract-wrap> text without end", "abstract-wrap>", ["END"]), "")

    def test_missing_start_marker_returns_empty(self):
        self.assertEqual(slice_between("nothing here", "abstract-wrap>", ["END"]), "")


if __name__ == "__main__":
    unittest.main()
