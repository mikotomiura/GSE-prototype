"""Regression tests for scripts/check_workflow_invariants.py (F-8 / F-9).

⚠️★★★ 本検査が守るのは「**決めた判断が、検査されていない前提の上に乗らないこと**」である。
★ この repo で実際に起きた失敗:
  - F-5: job を足すとき `permissions:` を書き忘れ、**4 job が既定の広い権限を継いでいた**
  - F-8: `ci.yml` に「follow-up: action を SHA ピン」と**自分で書いたまま放置**されていた
→ ⚠️ どちらも「人が覚えている」に依存していた。★ だから機械に持たせる。

⚠️ 本 module は実ファイルの内容そのもの（どの SHA か等）は固定しない。
★ 固定するのは**規則の側**であり、値は版上げで変わるため。

実行方法:
    cd GSE-prototype
    PYTHONUTF8=1 python -m unittest scripts.tests.test_check_workflow_invariants -v
"""

import re
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_workflow_invariants.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_workflow_invariants as cwi  # noqa: E402

SHA = "a" * 40


def _wf(job, name="ci.yml", top=None):
    data = {"jobs": {"j": job}}
    if top is not None:
        data["permissions"] = top
    return [(name, data)]


class TestUsesParsing(unittest.TestCase):
    def test_splits_action_and_ref(self):
        self.assertEqual(cwi._uses_ref("owner/repo@" + SHA), ("owner/repo", SHA))

    def test_ignores_trailing_comment(self):
        # ★ 版名コメントを付ける運用なので、これを落とすと全部 NG に化ける。
        self.assertEqual(
            cwi._uses_ref("owner/repo@" + SHA + "  # v2.9.2"), ("owner/repo", SHA)
        )

    def test_missing_ref(self):
        self.assertEqual(cwi._uses_ref("./.github/actions/x"), ("./.github/actions/x", ""))


class TestPermissionsInvariant(unittest.TestCase):
    def test_job_without_permissions_is_flagged(self):
        v, _ = cwi.check(_wf({"runs-on": "ubuntu-latest", "steps": []}))
        self.assertTrue(any("permissions" in x for x in v), v)

    def test_top_level_permissions_satisfies_the_job(self):
        v, _ = cwi.check(
            _wf({"runs-on": "ubuntu-latest", "steps": []}, top={"contents": "read"})
        )
        self.assertEqual(v, [])

    def test_job_level_permissions_satisfies_the_job(self):
        v, _ = cwi.check(
            _wf({"permissions": {"contents": "write"}, "runs-on": "x", "steps": []})
        )
        self.assertEqual(v, [])


class TestThirdPartyPinning(unittest.TestCase):
    def _check_ref(self, ref):
        step = {"uses": "Swatinem/rust-cache" + (("@" + ref) if ref else "")}
        return cwi.check(_wf({"permissions": {}, "runs-on": "x", "steps": [step]}))[0]

    def test_mutable_refs_are_flagged(self):
        # ⚠️ `stable` はタグですらなくブランチ。★ 一番危ないので必ず入れる。
        for ref in ("v2", "v2.9.2", "stable", "main", "master", ""):
            with self.subTest(ref=ref):
                self.assertTrue(any("third-party" in x for x in self._check_ref(ref)))

    def test_short_sha_is_flagged(self):
        # ⚠️ 短縮 SHA は衝突を作れるので 40 桁を要求する。
        self.assertTrue(any("third-party" in x for x in self._check_ref("a" * 7)))
        self.assertTrue(any("third-party" in x for x in self._check_ref("A" * 40)))

    def test_full_sha_passes(self):
        self.assertEqual(self._check_ref(SHA), [])

    def test_first_party_and_local_are_exempt(self):
        for exempt in ("actions/checkout@v4", "actions/setup-node@v4", "./.github/actions/disk-guard"):
            with self.subTest(exempt=exempt):
                v, _ = cwi.check(
                    _wf({"permissions": {}, "runs-on": "x", "steps": [{"uses": exempt}]})
                )
                self.assertEqual(v, [])


class TestReusableWorkflows(unittest.TestCase):
    """⚠️★★★ job 直下の `uses:` (reusable workflow 呼び出し) も見ること。

    ★ step の `uses:` だけを見ていると、**第三者の reusable workflow が素通り**する ——
    ⚠️ しかも reusable workflow は action より強く、**自前の job を持ち込む**。
    ★ 2026-09-13 に実装の穴として実際に見つけた。
    """

    def test_third_party_reusable_workflow_is_flagged(self):
        v, c = cwi.check(
            [("x.yml", {"permissions": {}, "jobs": {
                "call": {"uses": "evil/repo/.github/workflows/w.yml@v1"}}})]
        )
        self.assertTrue(any("third-party" in x for x in v), v)
        self.assertEqual((c["uses"], c["third_party"]), (1, 1))

    def test_sha_pinned_reusable_workflow_passes(self):
        v, _ = cwi.check(
            [("x.yml", {"permissions": {}, "jobs": {
                "call": {"uses": "org/repo/.github/workflows/w.yml@" + SHA}}})]
        )
        self.assertEqual(v, [])

    def test_local_reusable_workflow_is_exempt(self):
        v, _ = cwi.check(
            [("x.yml", {"permissions": {}, "jobs": {
                "call": {"uses": "./.github/workflows/local.yml"}}})]
        )
        self.assertEqual(v, [])


class TestHostedOnly(unittest.TestCase):
    def test_supply_chain_on_self_hosted_is_flagged(self):
        v, _ = cwi.check(
            _wf(
                {"permissions": {}, "runs-on": ["self-hosted", "gse-mac"], "steps": []},
                name="supply-chain.yml",
            )
        )
        self.assertTrue(any("self-hosted" in x for x in v), v)

    def test_ci_on_self_hosted_is_allowed(self):
        v, _ = cwi.check(
            _wf({"permissions": {}, "runs-on": ["self-hosted", "gse-mac"], "steps": []})
        )
        self.assertEqual(v, [])


class TestEmptyScanGuard(unittest.TestCase):
    """⚠️★★★ 「何も検査しなかった」を「違反なし」と読ませない。"""

    def test_zero_workflows_exits_two(self):
        self.assertEqual(
            cwi.report([], {"workflows": 0, "jobs": 0, "uses": 0, "third_party": 0},
                       stream=cwi._Sink()),
            cwi.EXIT_NOTHING_SCANNED,
        )

    def test_zero_jobs_exits_two(self):
        self.assertEqual(
            cwi.report([], {"workflows": 2, "jobs": 0, "uses": 0, "third_party": 0},
                       stream=cwi._Sink()),
            cwi.EXIT_NOTHING_SCANNED,
        )

    def test_workflow_without_jobs_is_flagged(self):
        v, _ = cwi.check([("x.yml", {"jobs": {}})])
        self.assertTrue(any("no jobs" in x for x in v), v)


class TestRealRepository(unittest.TestCase):
    """★ 実ファイルに対して規則が成立していること（⚠️ 値は固定しない）。"""

    def test_repo_workflows_satisfy_every_invariant(self):
        workflows = cwi.load_workflows(cwi.WORKFLOW_DIR)
        self.assertGreaterEqual(len(workflows), 2, "workflow が 2 枚未満は想定外")
        violations, counters = cwi.check(workflows)
        self.assertEqual(violations, [], "\n".join(violations))
        # ⚠️ 空振り検出: 実際に third-party を見ていること
        self.assertGreater(counters["third_party"], 0)
        self.assertGreater(counters["jobs"], 0)

    def test_pins_look_like_commit_shas_with_a_version_comment(self):
        # ★ 版名コメントは人が更新するための唯一の手がかりなので、形を固定する。
        text = (cwi.WORKFLOW_DIR / "ci.yml").read_text(encoding="utf-8")
        pinned = re.findall(r"uses:\s+(\S+)@([0-9a-f]{40})(\s*#\s*\S.*)?$", text, re.M)
        self.assertGreater(len(pinned), 0)
        for action, _sha, comment in pinned:
            self.assertTrue(comment and comment.strip(), action + " に版名コメントが無い")


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
        self.assertEqual(code, cwi.EXIT_OK, msg=err)
        self.assertIn("OK self-test", out)

    def test_real_run_is_green_and_states_counts(self):
        code, out, err = self._run([])
        self.assertEqual(code, cwi.EXIT_OK, msg=err + out)
        self.assertIn("workflow(s)", out)
        self.assertIn("third-party", out)

    def test_empty_directory_exits_two(self):
        with TemporaryDirectory() as td:
            code, out, _ = self._run(["--dir", td])
            self.assertEqual(code, cwi.EXIT_NOTHING_SCANNED, out)

    def test_missing_directory_is_usage_error(self):
        code, _, err = self._run(["--dir", "no/such/dir"])
        self.assertEqual(code, cwi.EXIT_USAGE)
        self.assertIn("not a directory", err)

    def test_unparseable_workflow_exits_three(self):
        with TemporaryDirectory() as td:
            (Path(td) / "broken.yml").write_text("a: [1,\n", encoding="utf-8")
            code, _, err = self._run(["--dir", td])
            self.assertEqual(code, cwi.EXIT_PARSE, err)


if __name__ == "__main__":
    unittest.main()
