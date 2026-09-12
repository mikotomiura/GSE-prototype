"""Regression tests for scripts/check_toolchain_advisories.py (F-1).

⚠️★★★ 本検査が守るのは「**比較できなかったことを緑と読まない**」である。
★ 本 repo は同じ失敗を 3 回踏んでいる —— (a) `--exact` の名前間違いで
`running 0 tests` / exit 0、(b) CI 待機ループを `pending == 0` で判定して
**未発火を完了と誤読**、(c) R-4 が直した無音 skip。
→ ⚠️ 「何も起きていない」と「成功した」を区別しない判定を書かない。

実行方法:
    cd GSE-prototype
    PYTHONUTF8=1 python -m unittest scripts.tests.test_check_toolchain_advisories -v
    # または
    PYTHONUTF8=1 python scripts/check_toolchain_advisories.py --self-test
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_toolchain_advisories.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_toolchain_advisories as cta  # noqa: E402


def _run(args, cwd=REPO_ROOT):
    """Run the script as a subprocess and return (returncode, stdout, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestVersionParsing(unittest.TestCase):
    def test_normalises_short_versions(self):
        self.assertEqual(cta.parse_version("1.98"), (1, 98, 0))
        self.assertEqual(cta.parse_version("1.98.1"), (1, 98, 1))
        self.assertEqual(cta.parse_version("2"), (2, 0, 0))

    def test_rejects_non_versions(self):
        # ⚠️ これらが (0,0,0) などに化けると「どの advisory にも当たらない」= 偽の緑になる。
        for bad in ("stable", "nightly-2026-01-01", "1.98.1-x86_64-pc-windows-msvc", ""):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    cta.parse_version(bad)


class TestRangeEvaluation(unittest.TestCase):
    def test_closed_range(self):
        # ★ `first_patched_version` が null なので、範囲そのものを読む必要がある。
        rng = ">= 1.87.0, < 1.89.0"
        self.assertFalse(cta.version_in_range((1, 86, 9), rng))
        self.assertTrue(cta.version_in_range((1, 87, 0), rng))
        self.assertTrue(cta.version_in_range((1, 88, 0), rng))
        self.assertFalse(cta.version_in_range((1, 89, 0), rng))

    def test_open_ranges(self):
        self.assertTrue(cta.version_in_range((1, 77, 1), "< 1.77.2"))
        self.assertFalse(cta.version_in_range((1, 77, 2), "< 1.77.2"))
        self.assertTrue(cta.version_in_range((1, 58, 0), "<= 1.58.0"))
        self.assertFalse(cta.version_in_range((1, 58, 1), "<= 1.58.0"))
        self.assertTrue(cta.version_in_range((2, 0, 0), "> 1.99.0"))
        self.assertTrue(cta.version_in_range((1, 98, 1), "= 1.98.1"))

    def test_unknown_range_raises(self):
        # ⚠️ 読めない範囲を False (= 当たらない) にしてはならない。
        for bad in ("~> 1.2.3", "1.2.3", ">= abc", "", "^1.2.3"):
            with self.subTest(bad=bad):
                with self.assertRaises(cta.RangeError):
                    cta.version_in_range((1, 98, 1), bad)

    def test_advisory_without_vulnerabilities_raises(self):
        with self.assertRaises(cta.RangeError):
            cta.evaluate((1, 98, 1), [{"cve_id": "X", "vulnerabilities": []}])

    def test_advisory_with_empty_range_raises(self):
        with self.assertRaises(cta.RangeError):
            cta.evaluate(
                (1, 98, 1),
                [{"cve_id": "X", "vulnerabilities": [{"vulnerable_version_range": "  "}]}],
            )


class TestChannelReading(unittest.TestCase):
    def test_reads_repo_toolchain_file(self):
        channel = cta.read_channel(REPO_ROOT / "rust-toolchain.toml")
        # ⚠️ 値そのものは固定しない (版上げで変わる)。★ 比較可能であることだけを固定する。
        self.assertEqual(cta.parse_version(channel)[:1], (1,))

    def test_rejects_file_without_exactly_one_channel(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "rust-toolchain.toml"
            p.write_text('[toolchain]\nprofile = "minimal"\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                cta.read_channel(p)
            p.write_text(
                '[toolchain]\nchannel = "1.1.1"\nchannel = "2.2.2"\n', encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                cta.read_channel(p)


class TestPayloadShape(unittest.TestCase):
    """⚠️★★★ list 以外が `evaluate()` に届くと `AttributeError` で **exit 1** になり、
    ★ 「advisory が当たった」と**外形上まったく区別が付かない**。"""

    def test_non_list_payloads_are_refused(self):
        for bad in ({"message": "Not Found"}, "nope", 3, None, True):
            with self.subTest(bad=bad):
                with self.assertRaises(cta.RangeError):
                    cta.coerce_advisories(bad)

    def test_list_of_non_objects_is_refused(self):
        with self.assertRaises(cta.RangeError):
            cta.coerce_advisories(["x"])

    def test_empty_list_is_a_valid_shape(self):
        # ★ 空であること自体は main() が exit 3 で弾く (層を分けている)。
        self.assertEqual(cta.coerce_advisories([]), [])


class TestPagination(unittest.TestCase):
    """⚠️ ページが 1 枚だけという暗黙の前提を置かないこと。"""

    def test_concatenated_arrays(self):
        self.assertEqual(len(cta.parse_pages('[{"a":1}] [{"b":2},{"c":3}]')), 3)

    def test_single_array(self):
        self.assertEqual(len(cta.parse_pages('[{"a":1}]')), 1)

    def test_bare_object(self):
        self.assertEqual(len(cta.parse_pages('{"a":1}')), 1)

    def test_empty_body_raises(self):
        for bad in ("", "   ", "\n"):
            with self.subTest(bad=bad):
                with self.assertRaises(RuntimeError):
                    cta.parse_pages(bad)

    def test_scalar_payload_raises(self):
        with self.assertRaises(RuntimeError):
            cta.parse_pages("3")

    def test_next_link(self):
        header = '<https://api.github.com/x?page=2>; rel="next", <https://x?page=9>; rel="last"'
        self.assertEqual(cta._next_link(header), "https://api.github.com/x?page=2")
        self.assertIsNone(cta._next_link('<https://x?page=9>; rel="last"'))
        self.assertIsNone(cta._next_link(None))
        self.assertIsNone(cta._next_link(""))


class TestWithdrawn(unittest.TestCase):
    def test_withdrawn_advisory_is_not_a_hit(self):
        # ⚠️ 取り下げられた advisory で赤にすると、誰も直しようがない偽赤になる。
        withdrawn = [
            {
                "cve_id": "CVE-2099-0001",
                "severity": "critical",
                "summary": "retracted",
                "withdrawn_at": "2026-01-01T00:00:00Z",
                "vulnerabilities": [{"vulnerable_version_range": "< 99.0.0"}],
            }
        ]
        lines, hits = cta.evaluate((1, 98, 1), withdrawn)
        self.assertEqual(hits, [])
        self.assertIn("withdrawn", " ".join(lines))


class TestExitCodes(unittest.TestCase):
    """⚠️★★★ 本体。★ script が **赤になるべきときに赤になる**ことを固定する。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = TemporaryDirectory()
        cls.fixture = Path(cls.tmp.name) / "advisories.json"
        cls.fixture.write_text(
            json.dumps(cta._FIXTURE, ensure_ascii=False), encoding="utf-8"
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _offline(self, channel):
        return _run(
            ["--channel", channel, "--advisories-file", str(self.fixture)]
        )

    def test_pinned_version_is_clean(self):
        code, out, _ = self._offline("1.98.1")
        self.assertEqual(code, cta.EXIT_OK)
        # ★ 「何件検査したか」が必ず出力に出ること (= 空振りを見分けられること)。
        self.assertIn("advisories fetched: 6", out)
        self.assertIn("OK: none of the 6", out)

    def test_affected_version_is_red(self):
        code, out, _ = self._offline("1.88.0")
        self.assertEqual(code, cta.EXIT_HIT)
        self.assertIn("CVE-2025-11233", out)
        self.assertIn("HIT", out)

    def test_critical_advisory_is_red(self):
        code, out, _ = self._offline("1.76.0")
        self.assertEqual(code, cta.EXIT_HIT)
        self.assertIn("CVE-2024-24576", out)

    def test_uncomparable_channel_is_not_green(self):
        for bad in ("stable", "nightly-2026-01-01", "beta"):
            with self.subTest(bad=bad):
                code, _, err = self._offline(bad)
                self.assertEqual(code, cta.EXIT_CHANNEL_UNCOMPARABLE)
                self.assertIn("not a plain version", err)

    def test_empty_advisory_list_is_not_green(self):
        with TemporaryDirectory() as td:
            empty = Path(td) / "empty.json"
            empty.write_text("[]", encoding="utf-8")
            code, _, err = _run(
                ["--channel", "1.98.1", "--advisories-file", str(empty)]
            )
            self.assertEqual(code, cta.EXIT_FETCH_OR_PARSE)
            self.assertIn("0 advisories returned", err)

    def test_unparseable_range_is_not_green(self):
        with TemporaryDirectory() as td:
            bad = Path(td) / "bad.json"
            bad.write_text(
                json.dumps(
                    [
                        {
                            "cve_id": "CVE-9999-0001",
                            "severity": "high",
                            "summary": "synthetic",
                            "vulnerabilities": [
                                {"vulnerable_version_range": "~> 1.2.3"}
                            ],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            code, _, err = _run(
                ["--channel", "1.98.1", "--advisories-file", str(bad)]
            )
            self.assertEqual(code, cta.EXIT_FETCH_OR_PARSE)
            self.assertIn("unparseable constraint", err)

    def test_missing_toolchain_file_is_usage_error(self):
        code, _, err = _run(["--toolchain-file", "no/such/file.toml"])
        self.assertEqual(code, cta.EXIT_USAGE)
        self.assertIn("ERROR", err)

    def test_self_test_passes(self):
        code, out, err = _run(["--self-test"])
        self.assertEqual(code, cta.EXIT_OK, msg=err)
        self.assertIn("OK self-test", out)


if __name__ == "__main__":
    unittest.main()
