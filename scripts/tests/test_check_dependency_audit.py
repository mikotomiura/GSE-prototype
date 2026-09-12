"""Regression tests for scripts/check_dependency_audit.py (F-2).

⚠️★★★ 本検査が守るのは「**除外が黙って古びない / 黙って広がらない**」である。
★ 2026-09-12 の実測で分かった 2 つの穴:
  (a) cargo-audit 0.22.2 は `[advisories] ignore` に入れた advisory を
      **出力から跡形もなく消す** → 「緑」と「除外したから緑」が区別できない。
  (b) ⚠️ **`$CARGO_HOME/audit.toml`(個人設定) も効く** → repo に書いていない除外が
      黙って適用されうる (★ cwd の隔離だけでは足りなかった)。

⚠️ 本 module は `cargo-audit` を呼ばない (実行環境に無くても走る)。
★ cargo-audit との結合は CI の実行そのものが検証する。

実行方法:
    cd GSE-prototype
    PYTHONUTF8=1 python -m unittest scripts.tests.test_check_dependency_audit -v
"""

import datetime
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_dependency_audit.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_dependency_audit as cda  # noqa: E402

TODAY = datetime.date(2026, 9, 12)
FUTURE = datetime.date(2026, 12, 12)
PAST = datetime.date(2026, 1, 1)


def _vuln(ident, crate="c", version="1.0.0"):
    return {
        "id": ident,
        "crate": crate,
        "version": version,
        "title": "synthetic finding",
        "patched": ">=2.0.0",
    }


class TestWaiverConfig(unittest.TestCase):
    def test_parses_repo_config(self):
        waivers = cda.read_ignore_config(REPO_ROOT / ".cargo" / "audit.toml")
        # ⚠️ 中身は固定しない (上流が直れば消える)。★ 形と「期日つき」だけを固定する。
        for ident, due in waivers.items():
            self.assertRegex(ident, r"^RUSTSEC-\d{4}-\d{4}$")
            self.assertIsInstance(due, datetime.date)

    def _write(self, td, body):
        p = Path(td) / "audit.toml"
        p.write_text(body, encoding="utf-8")
        return p

    def test_reads_ids_and_review_by(self):
        with TemporaryDirectory() as td:
            p = self._write(
                td,
                "[advisories]\n"
                'ignore = [\n    "RUSTSEC-2026-0194",  # review-by: 2026-12-12\n]\n',
            )
            self.assertEqual(
                cda.read_ignore_config(p), {"RUSTSEC-2026-0194": FUTURE}
            )

    def test_ignore_outside_advisories_is_refused(self):
        # ⚠️ 「最初の ignore を拾う」実装だと偽の waiver を読んでしまう (レビュー指摘)。
        with TemporaryDirectory() as td:
            p = self._write(
                td,
                "[packages]\n"
                'ignore = ["NOT-A-WAIVER"]\n'
                "[advisories]\n"
                'ignore = ["REAL-1"]  # review-by: 2026-12-12\n',
            )
            with self.assertRaises(cda.ConfigError):
                cda.read_ignore_config(p)

    def test_other_cargo_audit_settings_are_refused(self):
        # ⚠️ sandbox 実行では効かないのに素の実行では効く = 1 ファイルが 2 つの答えを出す。
        for body in (
            '[advisories]\nignore = []\nseverity = "low"\n',
            "[advisories]\nignore = []\n[output]\ndeny = []\n",
            "[advisories]\nignore = []\n[yanked]\nenabled = false\n",
        ):
            with self.subTest(body=body), TemporaryDirectory() as td:
                p = self._write(td, body)
                with self.assertRaises(cda.ConfigError):
                    cda.read_ignore_config(p)

    def test_waiver_without_review_by_is_refused(self):
        with TemporaryDirectory() as td:
            p = self._write(td, '[advisories]\nignore = ["X-1"]\n')
            with self.assertRaises(cda.ConfigError):
                cda.read_ignore_config(p)

    def test_single_quotes_are_read(self):
        with TemporaryDirectory() as td:
            p = self._write(
                td, "[advisories]\nignore = ['X-1']  # review-by: 2026-12-12\n"
            )
            self.assertEqual(cda.read_ignore_config(p), {"X-1": FUTURE})

    def test_missing_or_empty_means_nothing_waived(self):
        with TemporaryDirectory() as td:
            self.assertEqual(cda.read_ignore_config(Path(td) / "nope.toml"), {})
            p = self._write(td, "[advisories]\nignore = []\n")
            self.assertEqual(cda.read_ignore_config(p), {})
            p = self._write(td, "[advisories]\n")
            self.assertEqual(cda.read_ignore_config(p), {})


class TestEvaluate(unittest.TestCase):
    def test_unwaived_finding_blocks(self):
        b, w, s, e = cda.evaluate([_vuln("A")], {"A"}, {}, TODAY)
        self.assertEqual([v["id"] for v in b], ["A"])
        self.assertEqual((w, s, e), ([], [], []))

    def test_waived_finding_is_reported_not_dropped(self):
        b, w, s, e = cda.evaluate([_vuln("A")], {"A"}, {"A": FUTURE}, TODAY)
        self.assertEqual(b, [])
        self.assertEqual([v["id"] for v in w], ["A"])
        self.assertEqual((s, e), ([], []))

    def test_stale_waiver_is_detected(self):
        # ⚠️★★★ cargo-audit 単体では絶対に出ない判定。
        b, w, s, e = cda.evaluate([], set(), {"A": FUTURE}, TODAY)
        self.assertEqual((b, w, s, e), ([], [], ["A"], []))

    def test_expired_waiver_is_detected(self):
        # ⚠️★★★ stale だけでは、上流が直さない限り**永久に緑**になる。
        b, w, s, e = cda.evaluate([_vuln("A")], {"A"}, {"A": PAST}, TODAY)
        self.assertEqual(e, ["A"])
        self.assertEqual(s, [])

    def test_warning_only_id_is_not_stale(self):
        # ★ cargo-audit の ignore は warnings にも効くので、warnings だけの ID を
        #   waive しても stale にしてはならない (誤って削除を指示してしまう)。
        b, w, s, e = cda.evaluate([], {"WARN-1"}, {"WARN-1": FUTURE}, TODAY)
        self.assertEqual((b, w, s, e), ([], [], [], []))

    def test_mixed(self):
        b, w, s, e = cda.evaluate(
            [_vuln("A"), _vuln("B")], {"A", "B"}, {"B": FUTURE, "C": FUTURE}, TODAY
        )
        self.assertEqual([v["id"] for v in b], ["A"])
        self.assertEqual([v["id"] for v in w], ["B"])
        self.assertEqual((s, e), (["C"], []))


class TestExtractFindings(unittest.TestCase):
    """⚠️ cargo-audit の JSON 形式が変わったら気付けること (fixture 固定)。"""

    # ★ 実測の形 (cargo-audit 0.22.2・2026-09-12) を最小化したもの。
    REPORT = {
        "database": {
            "advisory-count": 1243,
            "last-updated": "2026-09-09T12:49:52+02:00",
        },
        "lockfile": {"dependency-count": 630},
        "settings": {"ignore": []},
        "vulnerabilities": {
            "found": True,
            "count": 1,
            "list": [
                {
                    "advisory": {
                        "id": "RUSTSEC-2026-0194",
                        "package": "quick-xml",
                        "title": "Quadratic run time when checking a start tag",
                    },
                    "package": {"name": "quick-xml", "version": "0.38.4"},
                    "versions": {"patched": [">=0.41.0"], "unaffected": []},
                    "affected": None,
                }
            ],
        },
        "warnings": {
            "unmaintained": [
                {
                    "kind": "unmaintained",
                    "package": {"name": "fxhash", "version": "0.2.1"},
                    "advisory": {"id": "RUSTSEC-2025-0057", "title": "unmaintained"},
                    "versions": {"patched": []},
                    "affected": None,
                }
            ],
            # ⚠️ `yanked` は advisory が None (実測) — ここで落ちないこと。
            "yanked": [
                {
                    "kind": "yanked",
                    "package": {"name": "chacha20", "version": "0.10.1"},
                    "advisory": None,
                    "versions": None,
                    "affected": None,
                }
            ],
        },
    }

    def test_shape(self):
        vulns, ids, crates, db, date = cda.extract_findings(self.REPORT)
        self.assertEqual(crates, 630)
        self.assertEqual(db, 1243)
        self.assertEqual(date, "2026-09-09T12:49:52+02:00")
        self.assertEqual([v["id"] for v in vulns], ["RUSTSEC-2026-0194"])
        self.assertEqual(vulns[0]["crate"], "quick-xml")
        self.assertEqual(vulns[0]["patched"], ">=0.41.0")
        # ★ warnings 側の ID も「報告された」集合に入ること
        self.assertIn("RUSTSEC-2025-0057", ids)
        self.assertIn("RUSTSEC-2026-0194", ids)

    def test_empty_report_yields_zeroes(self):
        vulns, ids, crates, db, date = cda.extract_findings({})
        self.assertEqual((vulns, ids, crates, db), ([], set(), 0, 0))
        self.assertEqual(date, "unknown")

    def test_warning_counts(self):
        self.assertEqual(
            cda.summarise_warnings(self.REPORT), [("unmaintained", 1), ("yanked", 1)]
        )


class TestReportTextAndExitCodes(unittest.TestCase):
    def _report(self, blocking, waived, stale, expired, crates=630, db=1243):
        waivers = {i: FUTURE for i in list(stale) + list(expired)}
        waivers.update({v["id"]: FUTURE for v in waived})
        return cda.report_text(
            Path("src-tauri/Cargo.lock"),
            Path(".cargo/audit.toml"),
            crates,
            db,
            "2026-09-09T12:49:52+02:00",
            blocking,
            waived,
            stale,
            expired,
            waivers,
            [("unmaintained", 7)],
        )

    def test_clean_is_zero_and_states_the_counts(self):
        text, code = self._report([], [], [], [])
        self.assertEqual(code, cda.EXIT_OK)
        self.assertIn("630 crate dependencies", text)
        self.assertIn("db last updated 2026-09-09", text)
        self.assertIn("OK: 630 crates scanned", text)

    def test_vulnerability_is_one(self):
        text, code = self._report([_vuln("A")], [], [], [])
        self.assertEqual(code, cda.EXIT_VULN)
        self.assertIn("VULNERABLE", text)

    def test_waived_is_zero_but_printed_with_date(self):
        text, code = self._report([], [_vuln("RUSTSEC-2026-0194")], [], [])
        self.assertEqual(code, cda.EXIT_OK)
        self.assertIn("WAIVED", text)
        self.assertIn("RUSTSEC-2026-0194", text)
        self.assertIn("review-by: 2026-12-12", text)

    def test_stale_and_expired_are_two(self):
        _, code = self._report([], [], ["RUSTSEC-1999-0001"], [])
        self.assertEqual(code, cda.EXIT_STALE_IGNORE)
        text, code = self._report([], [], [], ["RUSTSEC-1999-0002"])
        self.assertEqual(code, cda.EXIT_STALE_IGNORE)
        self.assertIn("EXPIRED WAIVER", text)

    def test_vulnerability_outranks_stale(self):
        _, code = self._report([_vuln("A")], [], ["B"], ["C"])
        self.assertEqual(code, cda.EXIT_VULN)

    def test_report_survives_cp932(self):
        # ⚠️ 2026-09-12 に実際に踏んだ: 非 ASCII が cp932 で落ち、未捕捉例外の exit 1 が
        #    「脆弱性検出」と区別できなかった。
        text, _ = self._report([_vuln("A")], [_vuln("B")], ["C"], ["D"])
        text.encode("cp932")


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

    def test_bad_config_is_usage_error(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "audit.toml"
            p.write_text('[advisories]\nignore = ["X-1"]\n', encoding="utf-8")
            code, _, err = self._run(["--config", str(p)])
            self.assertEqual(code, cda.EXIT_USAGE)
            self.assertIn("review-by", err)


if __name__ == "__main__":
    unittest.main()
