"""scripts/refdb/build.py のテスト（.steering/20261018-literature-db/）。

git もネットも使わない。枝の中身は一時ディレクトリに作り、DirSource で読む。

Run:
    python3 -m unittest scripts.tests.test_refdb_build -v
"""

from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFDB = REPO_ROOT / "scripts" / "refdb"
if str(REFDB) not in sys.path:
    sys.path.insert(0, str(REFDB))

import build  # noqa: E402

MAIN = "origin/main"
SIDE = "origin/docs/side"

HEAD = "| ID | key | 著者・題 | 出典 | URL | 接地 | 重複 | 状態 |\n|---|---|---|---|---|---|---|---|\n"
REFS_MAIN = HEAD + "\n".join([
    # 8 列
    "| [P1] | doi:10.1/a | Aa, A. — Alpha | *J. A* 1:1936–1962, 2020 | <https://doi.org/10.1/a> | 接地 A（d = .43 > .29） | — | active |",
    # 7 列（重複の列が無い）
    "| [P2] | doi:10.1/b | Bb, B. — Beta | CHI '10, pp.1851–1860 | — | 接地 B | active |",
    # 接地の中に ' | ' がある
    "| [V1] | url:example-c | Cc, C. — Gamma | Web, 2019 | https://example.org/c | 前半 | 後半 | — | **provisional** |",
    # 7 列で、接地の中に ' | ' がある
    "| [V3] | url:example-f | Ff, F. — Phi | Web, 2018 | — | 前 | 後 | active |",
    # どこからも引かれない
    "| [P3] | doi:10.1/d | Dd, D. — Delta | *J. D* 2021 | — | 接地 D | — | active |",
]) + "\n"
# 枝では P3 が別の文献を指す（番号の衝突）。P1 は同じ文献を V2 でも引く
REFS_SIDE = HEAD + "\n".join([
    "| [P1] | doi:10.1/a | Aa, A. — Alpha | *J. A* 1:1936–1962, 2020 | <https://doi.org/10.1/a> | 接地 A | — | active |",
    "| [P3] | doi:10.1/e | Ee, E. — Epsilon | *J. E* 2022 | — | 接地 E | — | active |",
    "| [V2] | doi:10.1/a | Aa, A. — Alpha | *J. A* 2020 | — | 接地 A | [P1] | active |",
]) + "\n"
INDEX = (
    "| 日付 | トピック | ファイル | 件数 | 要旨 |\n|---|---|---|---|---|\n"
    "| 2026-10-01 | ai-fatigue-x（★ **追補**） | [20261001-ai-fatigue-x.md](20261001-ai-fatigue-x.md) | 1 | 要旨 |\n"
)
CARD = (
    "# カード\n\n| # | 主張 | 温度 |\n|---|---|---|\n"
    "| 1 | Alpha は効く [P1]（★ 強い） | 確定 |\n"
    "### カード 2: Beta と Gamma [P2] [V1]\n"
)
SIDE_CARD = "| 1 | Epsilon の主張 [P3] | 2-1 |\n"


def make_tree(root: Path) -> None:
    def put(branch: str, path: str, text: str) -> None:
        p = root / branch.replace("/", "__") / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    put(MAIN, "docs/references.md", REFS_MAIN)
    put(MAIN, "docs/literature/_index.md", INDEX + "[P3] は索引からだけ\n")
    put(MAIN, "docs/literature/20261001-ai-fatigue-x.md", CARD)
    put(MAIN, "docs/adr/ADR-001.md", "根拠 [P1]\n")
    put(SIDE, "docs/references.md", REFS_SIDE)
    put(SIDE, "docs/literature/_index.md", "")
    put(SIDE, "docs/literature/20261002-handmark-y.md", SIDE_CARD)
    put(SIDE, "experiments/x/notes.md", "[V2]\n")


CFG = {
    "branches": [MAIN, SIDE],
    "branch_names": {MAIN: "main", SIDE: "side"},
    "human_columns": ["読んだ", "メモ"],
    "strands": [
        {"name": "7 手跡", "patterns": ["handmark-"]},
        {"name": "9 AI 疲労", "patterns": ["ai-fatigue"]},
    ],
}
SUMMARIES = {"doi:10.1/a": {"summary": "Alpha の要約", "features": "種類: 実験", "basis": "抄録"}}
CSL_RAW = {
    "doi:10.1/a": {
        "type": "journal-article", "title": ["Alpha", "Alpha 2"], "volume": 1,
        "author": [{"family": "Aa", "given": "A.", "affiliation": [], "sequence": "first"}],
        "issued": {"date-parts": [[2020, None]]}, "container-title": ["J. A"],
    },
    "doi:10.1/b": {"type": "proceedings-article", "title": "Beta", "issued": {"date-parts": [[None]]}},
    "doi:10.1/e": {"_err": "HTTP Error 404"},
}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_tree(self.root / "tree")
        self.src = build.DirSource(self.root / "tree")
        (self.root / "config.json").write_text(json.dumps(CFG, ensure_ascii=False), encoding="utf-8")
        (self.root / "summaries.json").write_text(json.dumps(SUMMARIES, ensure_ascii=False), encoding="utf-8")
        cache = self.root / "cache"
        cache.mkdir()
        (cache / "csl_raw.json").write_text(json.dumps(CSL_RAW), encoding="utf-8")
        (cache / "abstracts.json").write_text(json.dumps({"doi:10.1/e": {"abs": "Epsilon abstract"}}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_build(self, *extra: str) -> tuple[int, Path]:
        out = self.root / "out"
        argv = [
            "--config", str(self.root / "config.json"), "--summaries", str(self.root / "summaries.json"),
            "--cache", str(self.root / "cache"), "--out", str(out), "--date", "2026-10-18", "--no-bib", *extra,
        ]
        return build.main(argv, source=self.src), out

    def rows(self, out: Path) -> dict[str, dict]:
        with (out / "GSE文献DB_2026-10-18.csv").open(encoding="utf-8-sig") as fp:
            return {r["key"]: r for r in csv.DictReader(fp)}


class ParseTest(unittest.TestCase):
    def test_eight_seven_and_split_note(self):
        lines = REFS_MAIN.split("\n")[2:5]
        a, b, c = (build.parse_ref_line(x) for x in lines)
        self.assertEqual((a["id"], a["dup"], a["st"], a["url"]), ("P1", "—", "active", "https://doi.org/10.1/a"))
        self.assertEqual((b["id"], b["note"], b["dup"], b["st"]), ("P2", "接地 B", "—", "active"))
        self.assertEqual(c["note"], "前半 | 後半")
        self.assertIsNone(build.parse_ref_line("| [P9] | 列が | 足りない |"))
        f = build.parse_ref_line(REFS_MAIN.split("\n")[5])
        self.assertEqual((f["id"], f["note"], f["dup"], f["st"]), ("V3", "前 | 後", "—", "active"))
        g = build.parse_ref_line("| [P8] | k | A — T | S | — | 接地 | →P430 | superseded |")
        self.assertEqual((g["note"], g["dup"], g["st"]), ("接地", "→P430", "superseded"))
        for dup in ("[P270]", "→ **[P116] が正**", "[V187] と同じ主題（別の論文）", "=V9"):
            h = build.parse_ref_line(f"| [P8] | k | A — T | S | — | 接地 | {dup} | active |")
            self.assertEqual((h["note"], h["dup"]), ("接地", dup), dup)

    def test_year(self):
        cases = {
            "*J. A* 1:1936–1962, 2020": 2020, "CHI '10, pp.1851–1860": None,
            "*PNAS* 118(14):e2013097118, 2021": 2021, "ISO 9186-1:2014(E)": 2014,
            "New Directions 15:41–56, 1983 (reprint: Springer 2014)": 1983,
            "2023–2026 preprint": 2023, "J (arXiv:2010.04124)": None,
            "Journal des sciences militaires 9（1883 年 1 月）": 1883,
        }
        for src, want in cases.items():
            self.assertEqual(build.year_of(src), want, src)

    def test_fill_url(self):
        self.assertEqual(build.fill_url("—", "doi:10.1/x"), "https://doi.org/10.1/x")
        self.assertEqual(build.fill_url("", "arXiv:2101.1"), "https://arxiv.org/abs/2101.1")
        self.assertEqual(build.fill_url("—", "url:x"), "")

    def test_temperature_not_in_dates_or_verbs(self):
        self.assertEqual(build.TEMP_RE.findall("2026-03-04 に 2026-12-10 で確定した"), [])
        self.assertEqual(build.TEMP_RE.findall("版（2026-12-1）"), [])  # 前の数字だけが手がかり
        self.assertEqual(build.TEMP_RE.findall("[検証済 2-1 / 3-0]・確定"), ["2-1", "3-0", "確定"])
        self.assertEqual(build.TEMP_RE.findall("否決（0-3）"), ["否決", "0-3"])

    def test_clean_keeps_inequalities(self):
        self.assertEqual(build.clean("★ d = .43 > .29・<https://a.b/c> **太字**"), "d = .43 > .29・https://a.b/c 太字")


class CslTest(unittest.TestCase):
    def test_array_title_null_year_and_names(self):
        row = {"著者・題": "Aa, A. — Alpha", "出典": "J", "年": 2020, "URL": "", "key": "doi:10.1/a",
               "研究の筋": "9 AI 疲労", "ID": "P1"}
        item, hit = build.csl_item(row, CSL_RAW["doi:10.1/a"], "P1", "要約")
        self.assertTrue(hit)
        self.assertEqual(item["title"], "Alpha")
        self.assertEqual(item["volume"], "1")
        self.assertEqual(item["container-title"], "J. A")
        self.assertEqual(item["issued"], {"date-parts": [[2020]]})
        self.assertEqual(item["author"], [{"family": "Aa", "given": "A."}])
        self.assertEqual(item["type"], "article-journal")
        self.assertEqual(item["note"], "GSE P1 ｜ 要約")

    def test_issued_all_null_drops_field(self):
        self.assertIsNone(build.fix_issued({"date-parts": [[None]]}))
        self.assertIsNone(build.fix_issued({"date-parts": [["spring"]]}))
        self.assertEqual(build.fix_issued({"date-parts": [["2019", 3]]}), {"date-parts": [[2019, 3]]})

    def test_minimal_when_fetch_failed(self):
        row = {"著者・題": "Ee, E. — Epsilon", "出典": "*J. E* 2022", "年": 2022, "URL": "", "key": "doi:10.1/e",
               "研究の筋": "", "ID": "P3"}
        item, hit = build.csl_item(row, CSL_RAW["doi:10.1/e"], "P3", "")
        self.assertFalse(hit)
        self.assertEqual((item["title"], item["DOI"], item["issued"]), ("Epsilon", "10.1/e", {"date-parts": [[2022]]}))
        self.assertEqual(item["author"], [{"literal": "Ee, E."}])


class BuildTest(Base):
    def test_rows_and_manifest(self):
        rc, out = self.run_build()
        self.assertEqual(rc, 0)
        r = self.rows(out)
        self.assertEqual(len(r), 6)
        self.assertEqual(r["url:example-f"]["接地（全文）"], "前 | 後")
        a = r["doi:10.1/a"]
        self.assertEqual(a["ID"], "P1; V2（side）")
        self.assertEqual(a["名前空間"], "PV")
        self.assertEqual(a["年"], "2020")
        self.assertEqual(a["研究の筋"], "9 AI 疲労")
        self.assertEqual(a["カード"], "ai-fatigue-x（ 追補）（20261001）")
        self.assertEqual(a["カードでの記述"], "20261001・確定: Alpha は効く （ 強い）")
        self.assertEqual(a["カード外の引用元"], "adr/ADR-001.md / experiments/x/notes.md")
        self.assertEqual(a["枝"], "main, side")
        self.assertEqual(a["要約"], "Alpha の要約")
        self.assertIn("> .29", a["接地（全文）"])
        # 番号の衝突: P3 が main では Delta、side では Epsilon
        self.assertEqual(r["doi:10.1/d"]["番号の衝突"], "あり")
        self.assertEqual(r["doi:10.1/e"]["番号の衝突"], "あり")
        self.assertEqual(r["doi:10.1/e"]["研究の筋"], "7 手跡")
        self.assertEqual(r["doi:10.1/e"]["カードでの記述"], "20261002・2-1: Epsilon の主張")
        self.assertEqual(r["doi:10.1/d"]["研究の筋"], build.OFF_CARD)  # _index.md からだけ
        self.assertEqual(r["url:example-c"]["状態"], "provisional")
        self.assertEqual(r["doi:10.1/b"]["年"], "")
        self.assertEqual(r["doi:10.1/b"]["URL"], "https://doi.org/10.1/b")
        self.assertEqual(r["doi:10.1/b"]["要約の材料"], build.NO_SUMMARY_CITED)
        m = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual((m["works"], m["summaries"], m["claims_works"], m["collided_ids"]), (6, 1, 4, 1))
        self.assertEqual((m["csl_from_cache"], m["csl_minimal"]), (2, 4))
        missing = json.loads((out / "missing_summaries.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(x["key"] for x in missing), ["doi:10.1/b", "doi:10.1/e", "url:example-c"])
        self.assertEqual([x["abstract"] for x in missing if x["key"] == "doi:10.1/e"], ["Epsilon abstract"])
        html = (out / "GSE文献DB_2026-10-18.html").read_text(encoding="utf-8")
        self.assertNotIn("__DATA__", html)
        self.assertIn("2 枝の docs/references.md を key でまとめた 6 件", html)

    def test_unique_cite_keys_on_collision(self):
        _, out = self.run_build()
        ids = [x["id"] for x in json.loads((out / "GSE文献DB_2026-10-18.csl.json").read_text(encoding="utf-8"))]
        self.assertEqual(sorted(ids), sorted(["P1", "P2", "V1", "V3", "P3", "P3_doi101e"]))


class OutputTest(Base):
    def test_failed_run_leaves_previous_outputs(self):
        rc, out = self.run_build()
        self.assertEqual(rc, 0)
        before = {p.name: p.read_bytes() for p in out.iterdir()}
        (self.root / "tree" / "origin__main" / "docs" / "references.md").write_text(
            REFS_MAIN + "| [P7] | doi:10.1/g | Gg — Gamma2 | J 2020 | — | 接地 | — | active |\n", encoding="utf-8")
        orig = build.write_page
        build.write_page = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("壊した"))
        try:
            rc2, _ = self.run_build()
        finally:
            build.write_page = orig
        self.assertEqual(rc2, 2)
        self.assertEqual({p.name: p.read_bytes() for p in out.iterdir()}, before)

    def test_no_bib_removes_stale_bib(self):
        _, out = self.run_build()
        stale = out / "GSE文献DB_2026-10-18_bibtex.bib"
        stale.write_text("古い", encoding="utf-8")
        self.run_build()
        self.assertFalse(stale.exists())

    def test_script_embedding(self):
        evil = {"doi:10.1/a": {**SUMMARIES["doi:10.1/a"], "summary": "a</script><!--<script>b"}}
        (self.root / "summaries.json").write_text(json.dumps(evil, ensure_ascii=False), encoding="utf-8")
        _, out = self.run_build()
        html = (out / "GSE文献DB_2026-10-18.html").read_text(encoding="utf-8")
        data = html.split("const DATA = ", 1)[1].split(";\n", 1)[0]
        self.assertNotIn("<", data)
        self.assertIn("a\\u003c/script>", data)


class FetchTest(unittest.TestCase):
    def test_transient_failures_are_not_cached(self):
        import urllib.error
        import fetch
        calls = []

        def fake(url, headers=None, timeout=20):
            calls.append(url)
            if "doi.org/10.1/gone" in url:
                raise urllib.error.HTTPError(url, 404, "nf", {}, None)
            raise TimeoutError("timed out")

        orig_get, orig_sleep = fetch._get, fetch.time.sleep
        fetch._get, fetch.time.sleep = fake, lambda s: None
        try:
            with TemporaryDirectory() as d:
                p = Path(d) / "csl.json"
                fetch.fetch_csl(["doi:10.1/gone", "doi:10.1/slow"], p)
                got = json.loads(p.read_text(encoding="utf-8"))
                self.assertEqual(sorted(got), ["doi:10.1/gone"])
                a = Path(d) / "abs.json"
                old = {"doi:10.1/old429": {"src": None, "abs": "", "err_s2": "HTTP Error 429: "},
                       "doi:10.1/old404": {"src": None, "abs": "", "err_oa": "HTTP Error 404: Not Found"}}
                a.write_text(json.dumps(old), encoding="utf-8")
                calls.clear()
                fetch.fetch_abstracts(["doi:10.1/slow", "doi:10.1/old429", "doi:10.1/old404"], a)
                got = json.loads(a.read_text(encoding="utf-8"))
                self.assertEqual(sorted(got), ["doi:10.1/old404", "doi:10.1/old429"])
                self.assertTrue(any("old429" in u for u in calls))  # 前の回の 429 は取り直す
                self.assertFalse(any("old404" in u for u in calls))
        finally:
            fetch._get, fetch.time.sleep = orig_get, orig_sleep


class KeepTest(Base):
    def write_sheet(self, rows: list[list[str]], as_json: bool) -> Path:
        p = self.root / ("sheet.json" if as_json else "sheet.csv")
        if as_json:
            p.write_text(json.dumps({"values": rows}, ensure_ascii=False), encoding="utf-8")
        else:
            with p.open("w", encoding="utf-8-sig", newline="") as fp:
                csv.writer(fp).writerows(rows)
        return p

    def test_rejoin_by_key_csv_and_json(self):
        sheet = [["ID", "key", "読んだ", "メモ"], ["P2", "doi:10.1/b", "✓", "後で読む"], ["P1", "doi:10.1/a", "", ""],
                 ["P3", "doi:10.1/d"]]  # get_values は末尾の空セルを返さない
        for as_json in (False, True):
            with self.subTest(as_json=as_json):
                rc, out = self.run_build("--keep", str(self.write_sheet(sheet, as_json)))
                self.assertEqual(rc, 0)
                r = self.rows(out)
                self.assertEqual((r["doi:10.1/b"]["読んだ"], r["doi:10.1/b"]["メモ"]), ("✓", "後で読む"))
                self.assertEqual(r["doi:10.1/a"]["メモ"], "")
                m = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(m["kept"], {"joined": 1, "orphans": 0})

    def test_orphan_stops(self):
        sheet = [["key", "読んだ", "メモ"], ["url:gone", "", "大事なメモ"]]
        rc, out = self.run_build("--keep", str(self.write_sheet(sheet, False)))
        self.assertEqual(rc, build.EXIT_ORPHANS)
        self.assertFalse((out / "GSE文献DB_2026-10-18.csv").exists())

    def test_rekey(self):
        sheet = [["key", "読んだ", "メモ"], ["url:gone", "", "大事なメモ"]]
        rc, out = self.run_build("--keep", str(self.write_sheet(sheet, False)), "--rekey", "url:gone=doi:10.1/d")
        self.assertEqual(rc, 0)
        self.assertEqual(self.rows(out)["doi:10.1/d"]["メモ"], "大事なメモ")

    def test_keep_orphans(self):
        sheet = [["key", "読んだ", "メモ"], ["url:gone", "✓", "大事なメモ"]]
        rc, out = self.run_build("--keep", str(self.write_sheet(sheet, False)), "--keep-orphans")
        self.assertEqual(rc, 0)
        r = self.rows(out)
        self.assertEqual((r["url:gone"]["ID"], r["url:gone"]["状態"], r["url:gone"]["メモ"]), ("—", build.ORPHAN_STATE, "大事なメモ"))
        m = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(m["works"], 6)

    def test_unchecked_box_is_not_a_memo(self):
        # get_values はチェックを外した 読んだ を "FALSE" で返す。消えた key でもそれだけなら止めない
        sheet = [["key", "読んだ", "メモ"], ["url:gone", "FALSE", ""], ["doi:10.1/b", "TRUE", ""]]
        rc, out = self.run_build("--keep", str(self.write_sheet(sheet, True)))
        self.assertEqual(rc, 0)
        r = self.rows(out)
        self.assertEqual(r["doi:10.1/b"]["読んだ"], "TRUE")
        self.assertEqual(r["doi:10.1/a"]["読んだ"], "")

    def test_bad_sheet_stops_before_writing(self):
        # 列の名前が違う・values が無い・空の表は、黙って空の 読んだ・メモ にせず止める（何も書かない）
        bad = {
            "renamed": ([["key", "読んだ ", "メモ欄"], ["doi:10.1/b", "TRUE", "x"]], False),
            "no_values": ({"error": {"code": 400}}, True),
            "empty": ([], True),
        }
        for name, (table, as_json) in bad.items():
            with self.subTest(name):
                if as_json:
                    path = self.root / f"{name}.json"
                    path.write_text(json.dumps(table), encoding="utf-8")
                else:
                    path = self.write_sheet(table, False)
                rc, out = self.run_build("--keep", str(path))
                self.assertEqual(rc, 2)
                self.assertFalse((out / "GSE文献DB_2026-10-18.csv").exists())

    def test_rows_that_cannot_be_rejoined_stop(self):
        cases = {
            "empty_key": [["key", "読んだ", "メモ"], ["", "", "手で足した行"]],
            "duplicate": [["key", "読んだ", "メモ"], ["doi:10.1/b", "TRUE", "m1"], ["doi:10.1/b", "", "m2"]],
        }
        for name, sheet in cases.items():
            with self.subTest(name):
                rc, out = self.run_build("--keep", str(self.write_sheet(sheet, False)))
                self.assertEqual(rc, build.EXIT_ORPHANS)
                self.assertFalse((out / "GSE文献DB_2026-10-18.csv").exists())
        same = [["key", "読んだ", "メモ"], ["doi:10.1/b", "", "m"], ["doi:10.1/b", "", "m"], ["doi:10.1/a", "", ""]]
        self.assertEqual(build.keep_map(same, ["読んだ", "メモ"], ["読んだ"]), {"doi:10.1/b": {"読んだ": "", "メモ": "m"}})

    def test_rekey_collision_stops(self):
        sheet = [["key", "読んだ", "メモ"], ["url:gone", "", "A"], ["doi:10.1/d", "", "B"]]
        rc, out = self.run_build("--keep", str(self.write_sheet(sheet, False)), "--rekey", "url:gone=doi:10.1/d")
        self.assertEqual(rc, build.EXIT_ORPHANS)
        self.assertFalse((out / "GSE文献DB_2026-10-18.csv").exists())

    def test_false_in_memo_is_kept(self):
        got = build.keep_map([["key", "読んだ", "メモ"], ["a", "FALSE", "false"]], ["読んだ", "メモ"], ["読んだ"])
        self.assertEqual(got, {"a": {"読んだ": "", "メモ": "false"}})



import merge_summaries  # noqa: E402


class MergeSummariesTest(unittest.TestCase):
    ABS = ("We recruited 290 adults and found that fatigue after long sessions with assistants "
           "predicted lower willingness to keep using the tools in the following weeks of the study")
    INPUTS = [{"key": "k1", "title": "T", "venue": "J 2026", "abstract": ABS, "gse_note": "α = .92"},
              {"key": "k2", "title": "U", "venue": "", "abstract": "", "gse_note": "接地"}]

    def good(self):
        return {"k1": {"summary": "成人 290 人で疲労が利用意向の低下を予測した。", "features": "種類: 調査 ｜ 対象・N: 290 ｜ 主な結果・数値: α = .92", "basis": "抄録"},
                "k2": {"summary": "（抄録なし）…", "features": "種類: 不明", "basis": "接地のみ"}}

    def test_ok(self):
        r = merge_summaries.check(self.good(), self.INPUTS, {})
        self.assertEqual(r, {"errors": [], "unverified_numbers": []})

    def test_copy_overlap(self):
        new = self.good()
        new["k1"]["summary"] = "要約: " + " ".join(self.ABS.split()[3:20])
        self.assertTrue(any("15 語" in e for e in merge_summaries.check(new, self.INPUTS, {})["errors"]))

    def test_number_not_in_material(self):
        new = self.good()
        new["k1"]["features"] = "種類: 調査 ｜ 対象・N: 300 ｜ 主な結果・数値: 不明"
        u = merge_summaries.check(new, self.INPUTS, {})["unverified_numbers"]
        self.assertEqual([(x["key"], x["numbers"]) for x in u], [("k1", ["300"])])

    def test_shape_keys_and_existing(self):
        new = self.good()
        del new["k2"]
        new["k3"] = {"summary": "x", "features": "y", "basis": "推測"}
        errs = merge_summaries.check(new, self.INPUTS, {"k1": {}})["errors"]
        self.assertEqual(len(errs), 4, errs)  # 返っていない k2・入力に無い k3・既にある k1・basis

    def test_write(self):
        with TemporaryDirectory() as d:
            d = Path(d)
            (d / "new.json").write_text(json.dumps(self.good(), ensure_ascii=False), encoding="utf-8")
            (d / "in.json").write_text(json.dumps(self.INPUTS, ensure_ascii=False), encoding="utf-8")
            (d / "s.json").write_text(json.dumps({"k0": {"summary": "s"}}), encoding="utf-8")
            rc = merge_summaries.main([str(d / "new.json"), "--input", str(d / "in.json"),
                                       "--summaries", str(d / "s.json"), "--write"])
            self.assertEqual(rc, 0)
            s = json.loads((d / "s.json").read_text(encoding="utf-8"))
            self.assertEqual(list(s), ["k0", "k1", "k2"])
            self.assertEqual(s["k1"]["basis"], "抄録")
            bad = self.good()
            bad["k1"]["basis"] = "推測"
            (d / "new.json").write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
            (d / "s2.json").write_text("{}", encoding="utf-8")
            rc = merge_summaries.main([str(d / "new.json"), "--input", str(d / "in.json"),
                                       "--summaries", str(d / "s2.json"), "--write"])
            self.assertEqual(rc, 1)
            self.assertEqual((d / "s2.json").read_text(encoding="utf-8"), "{}")


if __name__ == "__main__":
    unittest.main()
