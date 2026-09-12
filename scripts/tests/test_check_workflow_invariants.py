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
    """⚠️★★★ F-5 が守りたかったのは「**広い権限を持たないこと**」であって
    「宣言があること」ではない。★ top-level 宣言がある限り、存在だけを見る検査は
    **二度と発火しない**（2026-09-13 のレビューで実測された）。"""

    def test_job_without_permissions_is_flagged(self):
        v, _ = cwi.check(_wf({"runs-on": "ubuntu-latest", "steps": []}))
        self.assertTrue(any("no effective" in x for x in v), v)

    def test_top_level_permissions_satisfies_the_job(self):
        v, _ = cwi.check(
            _wf({"runs-on": "ubuntu-latest", "steps": []}, top={"contents": "read"})
        )
        self.assertEqual(v, [])

    def test_broad_permissions_are_flagged(self):
        for perms in ("write-all", {"contents": "write"},
                      {"contents": "read", "id-token": "write"}, ["nope"]):
            with self.subTest(perms=perms):
                v, _ = cwi.check(
                    _wf({"permissions": perms, "runs-on": "ubuntu-latest", "steps": []})
                )
                self.assertTrue(v, "広い権限が素通りした: " + repr(perms))

    def test_narrow_permissions_pass(self):
        for perms in ("read-all", {"contents": "read"}, {}):
            with self.subTest(perms=perms):
                v, _ = cwi.check(
                    _wf({"permissions": perms, "runs-on": "ubuntu-latest", "steps": []})
                )
                self.assertEqual(v, [])

    def test_allowlisted_write_scope_passes(self):
        # ★ `release` は GitHub Release を作るので `contents: write` が要る。
        v, _ = cwi.check([("ci.yml", {"jobs": {"release": {
            "permissions": {"contents": "write"}, "runs-on": "ubuntu-latest",
            "steps": []}}})])
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
    """⚠️★★★ 否定リスト（"self-hosted" を含むか）では 4 通り迂回できた（実測）。
    ★ 許可リスト（hosted と**証明できる**か）に反転している。"""

    def _flagged(self, runs_on, name="supply-chain.yml"):
        v, _ = cwi.check(
            _wf({"permissions": {}, "runs-on": runs_on, "steps": []}, name=name)
        )
        return bool(v)

    def test_hosted_runners_pass(self):
        for runs_on in ("ubuntu-latest", ["ubuntu-latest"], "ubuntu-24.04", "macos-15",
                        "windows-latest"):
            with self.subTest(runs_on=runs_on):
                self.assertFalse(self._flagged(runs_on))

    def test_self_hosted_and_undecidable_are_flagged(self):
        for runs_on in (
            ["self-hosted", "gse-mac"],
            "gse-win",                      # ⚠️ self-hosted ラベルを書かない形
            "${{ matrix.os }}",             # ⚠️ 式 = 静的に決まらない
            {"group": "gse-group"},         # ⚠️ runner group
            {"labels": ["gse-mac"]},
            [],
            None,
        ):
            with self.subTest(runs_on=runs_on):
                self.assertTrue(self._flagged(runs_on), repr(runs_on) + " が素通りした")

    def test_ci_on_self_hosted_is_allowed(self):
        self.assertFalse(self._flagged(["self-hosted", "gse-mac"], name="ci.yml"))

    def test_renaming_a_hosted_only_workflow_is_detected(self):
        # ⚠️ ファイル名を変えると不変条件 (3) が**無言で消える**。
        self.assertEqual(cwi.missing_hosted_only([("ci.yml", {})]), ["supply-chain.yml"])
        self.assertEqual(
            cwi.missing_hosted_only([("ci.yml", {}), ("supply-chain.yml", {})]), []
        )


class TestCompositeActions(unittest.TestCase):
    """⚠️★★★ `./` 参照は免除されるので、composite action の**中身**は死角になる。
    ★ `disk-guard` は鍵のある実機で無条件に走る。"""

    def test_third_party_inside_a_composite_is_flagged(self):
        v, c = cwi.check([], [("a/action.yml", {"runs": {"steps": [
            {"uses": "attacker/pwn@main"}]}})])
        self.assertTrue(any("third-party" in x for x in v), v)
        self.assertEqual((c["composites"], c["uses"]), (1, 1))

    def test_sha_pinned_inside_a_composite_passes(self):
        v, _ = cwi.check([], [("a/action.yml", {"runs": {"steps": [
            {"uses": "attacker/pwn@" + SHA}]}})])
        self.assertEqual(v, [])

    def test_repo_composites_are_scanned(self):
        comps = cwi.load_composite_actions(cwi.ACTION_DIR)
        # ⚠️ 0 件なら「違反なし」ではなく「見ていない」。★ 実在を固定する。
        self.assertGreaterEqual(len(comps), 1)


class TestFirstPartyExemption(unittest.TestCase):
    """★ 免除は**リリースタグ**に限る（⚠️ ブロックは F-8 が問題にした当のもの）。"""

    def _flagged(self, ref):
        step = {"uses": "actions/checkout" + (("@" + ref) if ref else "")}
        v, _ = cwi.check(
            _wf({"permissions": {}, "runs-on": "ubuntu-latest", "steps": [step]})
        )
        return bool(v)

    def test_release_tags_are_exempt(self):
        for ref in ("v4", "v4.1", "v4.1.2"):
            with self.subTest(ref=ref):
                self.assertFalse(self._flagged(ref))

    def test_branches_and_missing_refs_are_flagged(self):
        for ref in ("main", "master", "attacker", ""):
            with self.subTest(ref=ref):
                self.assertTrue(self._flagged(ref), repr(ref) + " が素通りした")


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
        # ⚠️ `ci.yml` 決め打ちにすると、3 枚目の workflow にコメント無しのピンを
        #    書いても緑になる (2026-09-13 のレビュー指摘)。→ 全 workflow を回す。
        seen = 0
        for path in sorted(cwi.WORKFLOW_DIR.glob("*.y*ml")):
            text = path.read_text(encoding="utf-8")
            pinned = re.findall(
                r"uses:\s+(\S+)@([0-9a-f]{40})(\s*#\s*\S.*)?$", text, re.M
            )
            seen += len(pinned)
            for action, _sha, comment in pinned:
                self.assertTrue(
                    comment and comment.strip(),
                    path.name + " の " + action + " に版名コメントが無い",
                )
        # ⚠️ 0 件なら「全部コメント付き」ではなく「1 つも見ていない」。
        self.assertGreater(seen, 0, "SHA 固定が 1 件も見つからない = 検査が空振り")


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
