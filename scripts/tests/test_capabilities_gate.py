"""Regression tests for scripts/capabilities_gate.py (ADR-013 Migration 4).

⚠️★★★ 本ゲートが守るのは「**0 行の読み方**」である。
★ 「計器がコホートを跨げなかった」失敗が既に 2 件起きており、その両方が
「0 行 = 信号が無かった」と読んでしまった結果である。

実行方法:
    cd GSE-prototype
    PYTHONUTF8=1 python -m unittest scripts.tests.test_capabilities_gate -v
    # または
    PYTHONUTF8=1 python scripts/capabilities_gate.py --self-test
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GATE = REPO_ROOT / "scripts" / "capabilities_gate.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import capabilities_gate as cg  # noqa: E402

META_NEW = json.dumps(
    {
        "type": "meta",
        "session_start": 1,
        "hmm_version": "0.4.0",
        "app_version": "0.1.27",
        "capabilities": {
            "unconditional": ["key", "feat"],
            "threshold_gated": ["hook_health", "starve_window"],
            "config_gated": ["probe_assignment"],
        },
    },
    ensure_ascii=False,
)
META_OLD = json.dumps(
    {"type": "meta", "session_start": 1, "hmm_version": "0.3.0"}, ensure_ascii=False
)


def write(d: Path, name: str, rows) -> Path:
    p = d / name
    p.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return p


def verdict(paths, line_type: str) -> str:
    facts = [cg.read_file(p) for p in paths]
    return cg.judge(facts, [line_type]).verdicts[0].verdict


class JudgeTableTests(unittest.TestCase):
    """★ ADR-013 D1 の判定表を 1 行ずつ固定する。"""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.d = Path(self._tmp.name)
        self.new = write(
            self.d,
            "new.ndjson",
            [META_NEW, '{"type":"feat","t":1}', '{"type":"starve_window","t":2}'],
        )
        self.old = write(self.d, "old.ndjson", [META_OLD, '{"type":"key","t":1}'])

    def tearDown(self):
        self._tmp.cleanup()

    def test_unconditional_empty_means_signal_absent(self):
        """★ `unconditional` の 0 行だけが「測れて、無かった」と読める。"""
        self.assertEqual(verdict([self.new], "key"), cg.SIGNAL_ABSENT)

    def test_unconditional_present(self):
        self.assertEqual(verdict([self.new], "feat"), cg.PRESENT)

    def test_threshold_gated_empty_is_undecidable(self):
        """⚠️★★★ 閾値ゲート付きの 0 行は **判定不能**。ここが本ゲートの中心。"""
        self.assertEqual(verdict([self.new], "hook_health"), cg.UNDECIDABLE)

    def test_threshold_gated_present(self):
        self.assertEqual(verdict([self.new], "starve_window"), cg.PRESENT)

    def test_config_gated_empty_is_undecidable(self):
        """⚠️ G1 では probe 系が常に 0 行になる (設定で送出元ごと止まる)。"""
        self.assertEqual(verdict([self.new], "probe_assignment"), cg.UNDECIDABLE)

    def test_undeclared_and_empty_is_instrument_absent(self):
        """⚠️ 過去 2 件の失敗はここ。★ 「計器が無かった」を「信号が無かった」にしない。"""
        self.assertEqual(verdict([self.new], "ime_shadow"), cg.INSTRUMENT_ABSENT)

    def test_undeclared_but_present_is_a_declaration_bug(self):
        p = write(self.d, "bug.ndjson", [META_NEW, '{"type":"ime_shadow","t":1}'])
        self.assertEqual(verdict([p], "ime_shadow"), cg.DECLARATION_BUG)


class LegacyLogTests(unittest.TestCase):
    """⚠️★★★ `capabilities` キー自体が無い旧ログの扱い。

    ★ **「宣言はあるが載っていない」と混ぜてはならない** ——
    行が実在したときの読み方が逆になる。
    """

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.d = Path(self._tmp.name)
        self.old = write(self.d, "old.ndjson", [META_OLD, '{"type":"key","t":1}'])
        self.new = write(self.d, "new.ndjson", [META_NEW, '{"type":"feat","t":1}'])

    def tearDown(self):
        self._tmp.cleanup()

    def test_legacy_with_rows_is_present(self):
        """★ 目の前に行があるのだから読める。⚠️ `DECLARATION_BUG` にしてはならない。

        ⚠️ ここを間違えると Phase1 の 63 ファイルが丸ごと「宣言のバグ」に化ける。
        """
        self.assertEqual(verdict([self.old], "key"), cg.PRESENT)

    def test_legacy_without_rows_falls_back_to_instrument_absent(self):
        """⚠️ 旧ログでは「計器が無かった」と「信号が無かった」を区別できない → 安全側。"""
        self.assertEqual(verdict([self.old], "starve_window"), cg.INSTRUMENT_ABSENT)

    def test_mixed_cohort_is_rejected(self):
        """⚠️★★★ 新旧が混ざったコホートは **平均を取る前に止める**。"""
        self.assertEqual(verdict([self.new, self.old], "starve_window"), cg.MIXED)

    def test_legacy_and_undeclared_build_are_not_conflated(self):
        """⚠️ どちらも「群が無い」に見えるが、意味が違うので `MIXED` にする。"""
        self.assertEqual(verdict([self.new, self.old], "ime_shadow"), cg.MIXED)


class ExitCodeTests(unittest.TestCase):
    """⚠️ CLI として使ったときに **赤が赤として出る**ことを固定する。

    ★ `.steering/.../blockers.md` B-3 の罠 (`| tail` にパイプすると `$?` が
    tail のものになる) を踏まないよう、テストは `subprocess.run` の
    `returncode` を直接見る。
    """

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.d = Path(self._tmp.name)
        write(self.d, "new.ndjson", [META_NEW, '{"type":"feat","t":1}'])

    def tearDown(self):
        self._tmp.cleanup()

    def run_gate(self, *args):
        return subprocess.run(
            [sys.executable, str(GATE), str(self.d), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_readable_requirements_exit_zero(self):
        r = self.run_gate("--require", "feat", "--require", "key")
        self.assertEqual(r.returncode, cg.EXIT_OK, r.stderr)

    def test_undecidable_exits_three(self):
        r = self.run_gate("--require", "starve_window")
        self.assertEqual(r.returncode, cg.EXIT_UNDECIDABLE, r.stderr)

    def test_allow_undecidable_downgrades_only_that(self):
        r = self.run_gate("--require", "starve_window", "--allow-undecidable")
        self.assertEqual(r.returncode, cg.EXIT_OK, r.stderr)
        # ⚠️ ただし INSTRUMENT_ABSENT までは見逃さない。
        r2 = self.run_gate("--require", "ime_shadow", "--allow-undecidable")
        self.assertEqual(r2.returncode, cg.EXIT_INSTRUMENT_ABSENT, r2.stderr)

    def test_missing_require_is_a_usage_error(self):
        """★ 「何を読むか」を宣言しない解析は検査できない。"""
        r = self.run_gate()
        self.assertEqual(r.returncode, cg.EXIT_USAGE)

    def test_json_output_is_machine_readable(self):
        r = self.run_gate("--require", "feat", "--json")
        payload = json.loads(r.stdout)
        self.assertEqual(payload["verdicts"][0]["verdict"], cg.PRESENT)
        self.assertEqual(payload["files"][0]["app_version"], "0.1.27")

    def test_self_test_is_green(self):
        """⚠️ 検査自身が空振りしていないことを、テストからも確かめる。"""
        r = subprocess.run(
            [sys.executable, str(GATE), "--self-test"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(r.returncode, 0, r.stderr)


class PrivacyTests(unittest.TestCase):
    """⚠️★★★ `--json` は **コミットされうる**（`.gitignore` は `results/*.json` を塞がない）。

    ★ 実データのファイル名は **擬似 ID ＋ セッション開始時刻そのもの**なので、
    ⚠️ そこに実名を出すと「各参加者がいつ打鍵していたか」の全リストが公開されうる
    （security-checker HIGH・2026-08-21）。
    """

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.d = Path(self._tmp.name)
        self.f = write(self.d, "P010_gse_20260629_073659.ndjson", [META_NEW, '{"type":"feat","t":1}'])

    def tearDown(self):
        self._tmp.cleanup()

    def test_json_never_contains_the_file_name(self):
        payload = cg.judge([cg.read_file(self.f)], ["feat"]).as_dict()
        blob = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn("P010", blob)
        self.assertNotIn("20260629", blob)
        self.assertNotIn("path", payload["files"][0])

    def test_json_carries_a_stable_opaque_file_id(self):
        """★ 実名の代わりに突き合わせ用の ID を出す（端末表示と同じ値）。"""
        payload = cg.judge([cg.read_file(self.f)], ["feat"]).as_dict()
        fid = payload["files"][0]["file_id"]
        self.assertEqual(len(fid), 8)
        self.assertEqual(fid, cg.file_id_of(self.f))

    def test_cli_json_keeps_the_human_report_off_stdout(self):
        """⚠️ `--json > file` で保存されるのは JSON だけ。★ 本文は stderr へ。"""
        r = subprocess.run(
            [sys.executable, str(GATE), str(self.d), "--require", "feat", "--json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        json.loads(r.stdout)  # ★ stdout は純粋な JSON である
        self.assertNotIn("P010", r.stdout)
        self.assertIn("判定", r.stderr, "人が読む本文が stderr に出ていない")


class FailClosedTests(unittest.TestCase):
    """⚠️★★★ 「コホートが揃っている」ことを担保するゲートが、**コホートの縮小を見逃さない**こと。"""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.d = Path(self._tmp.name)
        write(self.d, "new.ndjson", [META_NEW, '{"type":"feat","t":1}'])

    def tearDown(self):
        self._tmp.cleanup()

    def test_a_missing_input_is_not_silently_dropped(self):
        """★ タイポ・未マウントのパスで**黙って 1 本減る**と、残りだけで exit 0 になる。"""
        with self.assertRaises(cg.MissingInputError):
            cg.collect_paths([str(self.d), str(self.d / "typo.ndjson")])

    def test_cli_stops_on_a_missing_input(self):
        r = subprocess.run(
            [sys.executable, str(GATE), str(self.d), str(self.d / "typo.ndjson"),
             "--require", "feat"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(r.returncode, cg.EXIT_USAGE, r.stdout)

    def test_empty_input_is_not_reported_as_readable(self):
        """⚠️ `except CapabilitiesGateError as e: log(str(e))` が**緑として記録しない**こと。"""
        empty = cg.Report([], []).summary()
        self.assertNotEqual(empty, "capabilities gate: すべての要求行種が読める")
        self.assertIn("1 本も無い", empty)

    def test_undecodable_bytes_do_not_abort_the_judgement(self):
        """⚠️ 不正バイト 1 個で `UnicodeDecodeError` を素通りさせない（判定表に無い exit になる）。"""
        p = self.d / "broken.ndjson"
        p.write_bytes(
            META_NEW.encode("utf-8")
            + bytes([0x0A, 0xFF, 0xFE, 0x20, 0x6E, 0x6F, 0x74, 0x0A])
        )
        facts = cg.read_file(p)
        self.assertGreaterEqual(facts.malformed_lines, 1)
        self.assertIsNotNone(facts.declared)


class PublicApiEdgeTests(unittest.TestCase):
    """⚠️ 公開関数として素の例外・無音を残さない (code-reviewer MEDIUM・2026-08-21)。"""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.d = Path(self._tmp.name)
        self.f = write(self.d, "new.ndjson", [META_NEW, '{"type":"feat","t":1}'])

    def tearDown(self):
        self._tmp.cleanup()

    def test_judge_on_an_empty_cohort_does_not_raise(self):
        """★ `next(iter(...))` の `StopIteration` を素通りさせない。"""
        report = cg.judge([], ["feat"])
        self.assertEqual(report.verdicts, [])
        self.assertIn("1 本も無い", report.summary())

    def test_require_meta_is_rejected_with_an_explanation(self):
        """⚠️ `meta` はどの群にも載らない設計。★ `DECLARATION_BUG` に見せない。"""
        r = subprocess.run(
            [sys.executable, str(GATE), str(self.d), "--require", "meta"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(r.returncode, cg.EXIT_USAGE)
        self.assertIn("meta", r.stderr)

    def test_allow_undecidable_is_never_silent(self):
        """⚠️ 「判定不能を受け入れた」ことが記録されないまま結論が出ないようにする。"""
        code = """
import sys
sys.path.insert(0, %r)
import capabilities_gate as cg
cg.preflight([%r], ["starve_window"], allow_undecidable=True)
""" % (str(REPO_ROOT / "scripts"), str(self.d))
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**__import__("os").environ, "PYTHONUTF8": "1"},
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("判定不能", r.stderr, "★ API 経由だと無音だった")


class PreflightApiTests(unittest.TestCase):
    """★ 解析スクリプトが 1 行目で呼ぶ入口。"""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.d = Path(self._tmp.name)
        write(self.d, "new.ndjson", [META_NEW, '{"type":"feat","t":1}'])

    def tearDown(self):
        self._tmp.cleanup()

    def test_preflight_passes_for_readable_types(self):
        report = cg.preflight([str(self.d)], required=["feat"])
        self.assertEqual(report.verdicts[0].verdict, cg.PRESENT)

    def test_preflight_raises_when_zero_rows_would_be_misread(self):
        with self.assertRaises(cg.CapabilitiesGateError):
            cg.preflight([str(self.d)], required=["starve_window"])

    def test_preflight_raises_on_empty_input(self):
        with TemporaryDirectory() as empty:
            with self.assertRaises(cg.CapabilitiesGateError):
                cg.preflight([empty], required=["feat"])


if __name__ == "__main__":
    unittest.main()
