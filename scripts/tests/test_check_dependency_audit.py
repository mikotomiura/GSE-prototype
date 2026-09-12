"""Regression tests for scripts/check_dependency_audit.py (F-2).

⚠️★★★ 本検査が守るのは「**除外が黙って古びない**」である。
★ 2026-09-12 の実測: cargo-audit 0.22.2 は `[advisories] ignore` に入れた advisory を
**出力から跡形もなく消す**ので、「緑」と「除外したから緑」が区別できない。
→ ⚠️ 除外は必ず印字し、⚠️ **もう当たらない除外 (stale) は赤にする**。

⚠️ 本 module は `cargo-audit` を呼ばない (実行環境に無くても走る)。
★ cargo-audit との結合は `--self-test` ではなく **CI の実行そのもの**が検証する。

実行方法:
    cd GSE-prototype
    PYTHONUTF8=1 python -m unittest scripts.tests.test_check_dependency_audit -v
"""

import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_dependency_audit.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_dependency_audit as cda  # noqa: E402


def _vuln(ident, crate="c", version="1.0.0"):
    return {
        "id": ident,
        "crate": crate,
        "version": version,
        "title": "synthetic finding",
        "patched": ">=2.0.0",
    }


class TestIgnoreListParsing(unittest.TestCase):
    def test_parses_repo_config(self):
        ids = cda.read_ignore_list(REPO_ROOT / ".cargo" / "audit.toml")
        # ⚠️ 中身は固定しない (上流が直れば消える)。★ 形だけを固定する。
        for i in ids:
            self.assertRegex(i, r"^RUSTSEC-\d{4}-\d{4}$")

    def test_comments_do_not_leak_ids(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "audit.toml"
            p.write_text(
                '# background: "RUSTSEC-9999-9999" is unrelated\n'
                "[advisories]\n"
                'ignore = [\n    "RUSTSEC-2026-0194",  # still unfixed upstream\n]\n',
                encoding="utf-8",
            )
            self.assertEqual(cda.read_ignore_list(p), ["RUSTSEC-2026-0194"])

    def test_missing_file_means_nothing_waived(self):
        with TemporaryDirectory() as td:
            self.assertEqual(cda.read_ignore_list(Path(td) / "nope.toml"), [])

    def test_config_without_ignore_means_nothing_waived(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "audit.toml"
            p.write_text("[advisories]\nseverity = 'low'\n", encoding="utf-8")
            self.assertEqual(cda.read_ignore_list(p), [])


class TestEvaluate(unittest.TestCase):
    def test_unwaived_finding_blocks(self):
        b, w, s = cda.evaluate([_vuln("A")], [])
        self.assertEqual([v["id"] for v in b], ["A"])
        self.assertEqual(w, [])
        self.assertEqual(s, [])

    def test_waived_finding_is_reported_not_dropped(self):
        b, w, s = cda.evaluate([_vuln("A")], ["A"])
        self.assertEqual(b, [])
        self.assertEqual([v["id"] for v in w], ["A"])
        self.assertEqual(s, [])

    def test_stale_ignore_is_detected(self):
        # ⚠️★★★ 本 module の中心。★ cargo-audit 単体では絶対に出ない判定。
        b, w, s = cda.evaluate([], ["A"])
        self.assertEqual((b, w, s), ([], [], ["A"]))

    def test_mixed(self):
        b, w, s = cda.evaluate([_vuln("A"), _vuln("B")], ["B", "C"])
        self.assertEqual([v["id"] for v in b], ["A"])
        self.assertEqual([v["id"] for v in w], ["B"])
        self.assertEqual(s, ["C"])


class TestReportTextAndExitCodes(unittest.TestCase):
    def _report(self, blocking, waived, stale, crates=630):
        return cda.report_text(
            Path("src-tauri/Cargo.lock"),
            Path(".cargo/audit.toml"),
            crates,
            1243,
            blocking,
            waived,
            stale,
            [("unmaintained", 7)],
        )

    def test_clean_is_zero_and_states_the_counts(self):
        text, code = self._report([], [], [])
        self.assertEqual(code, cda.EXIT_OK)
        # ★ 「何件走査したか」が必ず出ること = 空振りと成功を見分けられること。
        self.assertIn("630 crate dependencies", text)
        self.assertIn("OK: 630 crates scanned", text)

    def test_vulnerability_is_one(self):
        text, code = self._report([_vuln("A")], [], [])
        self.assertEqual(code, cda.EXIT_VULN)
        self.assertIn("VULNERABLE", text)
        self.assertIn("A", text)

    def test_waived_is_zero_but_printed(self):
        text, code = self._report([], [_vuln("RUSTSEC-2026-0194")], [])
        self.assertEqual(code, cda.EXIT_OK)
        self.assertIn("WAIVED", text)
        self.assertIn("RUSTSEC-2026-0194", text)

    def test_stale_is_two(self):
        text, code = self._report([], [], ["RUSTSEC-1999-0001"])
        self.assertEqual(code, cda.EXIT_STALE_IGNORE)
        self.assertIn("STALE IGNORE", text)

    def test_vulnerability_outranks_stale(self):
        _, code = self._report([_vuln("A")], [], ["B"])
        self.assertEqual(code, cda.EXIT_VULN)

    def test_report_is_ascii_printable(self):
        # ⚠️ Windows の cp932 コンソールで落ちないこと (2026-09-12 に実際に踏んだ)。
        text, _ = self._report([_vuln("A")], [_vuln("B")], ["C"])
        text.encode("cp932")


class TestZeroCrateGuard(unittest.TestCase):
    def test_zero_crates_is_not_green(self):
        # ★ extract_findings が 0 を返した場合、main は EXIT_TOOL で落ちる。
        vulns, crates, db = cda.extract_findings({})
        self.assertEqual((vulns, crates, db), ([], 0, 0))


class TestCli(unittest.TestCase):
    def _run(self, args):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)] + args,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return proc.returncode, proc.stdout, proc.stderr

    def test_self_test_passes(self):
        code, out, err = self._run(["--self-test"])
        self.assertEqual(code, cda.EXIT_OK, msg=err)
        self.assertIn("OK self-test", out)

    def test_missing_lockfile_is_usage_error(self):
        code, _, err = self._run(["--lockfile", "no/such/Cargo.lock"])
        self.assertEqual(code, cda.EXIT_USAGE)
        self.assertIn("lockfile not found", err)


if __name__ == "__main__":
    unittest.main()
