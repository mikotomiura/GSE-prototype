"""acs_core の単体テスト（python3 -I -m unittest test_acs_core）。"""

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import acs_core as core  # noqa: E402


class SmoothTest(unittest.TestCase):
    def _run(self, labels, idle=None, forced_at=(), min_run=3, post=None):
        lab = np.array(labels)
        m = len(lab)
        idle = np.zeros(m, dtype=bool) if idle is None else np.array(idle)
        forced = np.zeros(m + 1, dtype=bool)
        forced[m] = True
        for i in forced_at:
            forced[i] = True
        k = max(lab.max() + 1, 1)
        post = np.full((m, k), 1.0 / k) if post is None else np.array(post)
        return core.smooth_labels(lab, post, idle, forced, min_run)

    def test_short_run_between_same_labels_is_absorbed(self):
        out, n = self._run([0, 0, 0, 1, 0, 0, 0])
        self.assertEqual(out.tolist(), [0] * 7)
        self.assertEqual(n, 1)

    def test_long_runs_are_kept(self):
        out, n = self._run([0, 0, 0, 1, 1, 1])
        self.assertEqual(out.tolist(), [0, 0, 0, 1, 1, 1])
        self.assertEqual(n, 0)

    def test_short_run_goes_to_higher_posterior_neighbour(self):
        post = [[1, 0, 0]] * 3 + [[0.1, 0.2, 0.7]] + [[0, 0, 1]] * 3
        out, _ = self._run([0, 0, 0, 1, 2, 2, 2], post=post)
        self.assertEqual(out.tolist(), [0, 0, 0, 2, 2, 2, 2])

    def test_idle_is_never_relabelled_and_forced_boundary_is_not_crossed(self):
        # 窓 3 の前に強制の境界。窓 3 の短い連続は左へ吸収できず、右へ行く。
        out, _ = self._run([0, 0, 0, 1, 2, 2, 2], forced_at=(3,))
        self.assertEqual(out.tolist(), [0, 0, 0, 2, 2, 2, 2])
        out, _ = self._run([0, 0, 0, 1, 0, 0, 0], idle=[0, 0, 0, 1, 0, 0, 0])
        self.assertEqual(out[3], core.IDLE)

    def test_isolated_short_run_with_barriers_on_both_sides_stays(self):
        out, n = self._run([0, 0, 0, 1, 2, 2, 2], forced_at=(3, 4))
        self.assertEqual(out.tolist(), [0, 0, 0, 1, 2, 2, 2])
        self.assertEqual(n, 0)


class MetricTest(unittest.TestCase):
    def test_ari_and_nmi_are_one_for_relabelled_partition(self):
        a = np.array([0, 0, 1, 1, 2, 2])
        b = np.array([5, 5, 3, 3, 9, 9])
        self.assertAlmostEqual(core.ari(a, b), 1.0)
        self.assertAlmostEqual(core.nmi(a, b), 1.0)

    def test_nmi_zero_when_one_side_constant(self):
        self.assertEqual(core.nmi(np.array([0, 1, 0, 1]), np.array([7, 7, 7, 7])), 0.0)

    def test_boundary_f1_tolerance(self):
        p, r, f = core.boundary_f1([1000, 50_000], [1500, 90_000], tol_ms=1000)
        self.assertEqual((p, r), (0.5, 0.5))
        self.assertAlmostEqual(f, 0.5)


class GmmTest(unittest.TestCase):
    def test_bic_picks_two_for_two_blobs_and_one_for_one(self):
        rng = np.random.default_rng(0)
        two = np.vstack([rng.normal(-4, 1, (200, 2)), rng.normal(4, 1, (200, 2))])
        one = rng.normal(0, 1, (400, 2))
        self.assertEqual(core.select_gmm(two, 6, 1, 3).k, 2)
        self.assertEqual(core.select_gmm(one, 6, 1, 3).k, 1)


class ForcedTest(unittest.TestCase):
    def test_long_idle_forces_both_edges(self):
        s = np.arange(10) * 60_000
        win = core.Windows(s, s + 60_000, np.zeros((10, len(core.FEATURE_NAMES))),
                           np.array([0, 0, 0, 1, 1, 1, 1, 1, 0, 0], dtype=bool))
        f = core.forced_boundaries(win, 300)
        self.assertTrue(f[3] and f[8] and f[10])
        self.assertFalse(f[1] or f[5])


class SeamTest(unittest.TestCase):
    def test_idle_run_is_cut_at_a_seam_and_gap_time_is_not_counted(self):
        # 窓 3 分。無操作 1 窓（180 秒）+ 継ぎ目 + 無操作 1 窓。どちらも 300 秒に届かないので強制の境界は立たない。
        s = np.array([0, 180, 360, 3600, 3780, 3960]) * 1000
        win = core.Windows(s, s + 180_000, np.zeros((6, len(core.FEATURE_NAMES))),
                           np.array([0, 0, 1, 1, 0, 0], dtype=bool))
        seams = np.zeros(7, dtype=bool)
        seams[[0, 3, 6]] = True
        f = core.forced_boundaries(win, 300, seams)
        self.assertFalse(f[2] or f[4])
        # 継ぎ目が無ければ 2 窓（360 秒）の無操作になり、両端に立つ。
        f2 = core.forced_boundaries(win, 300)
        self.assertTrue(f2[2] and f2[4])

    def test_concat_rejects_overlapping_files(self):
        a = core.Windows(np.array([0]), np.array([180_000]), np.zeros((1, len(core.FEATURE_NAMES))),
                         np.array([False]))
        b = core.Windows(np.array([100_000]), np.array([280_000]), np.zeros((1, len(core.FEATURE_NAMES))),
                         np.array([False]))
        with self.assertRaises(ValueError):
            core.concat_windows([a, b])


class BlockPermutationTest(unittest.TestCase):
    def setUp(self):
        mins = [11, 17, 12, 20, 14, 10, 19, 13, 15, 18]
        self.blocks = np.concatenate([[i] * m for i, m in enumerate(mins)])
        self.lab = np.concatenate([[i % 2] * m for i, m in enumerate(mins)])
        self.mins = mins

    def _ref(self, vals):
        return np.concatenate([[v] * m for v, m in zip(vals, self.mins)])

    def test_matching_declaration_is_significant(self):
        ref = self._ref(["a", "v"] * 5)
        obs, p = core.block_permutation_pvalue(self.lab, ref, self.blocks, 999, np.random.default_rng(0))
        self.assertAlmostEqual(obs, 1.0)
        self.assertLess(p, 0.05)

    def test_weak_chance_association_is_not_significant(self):
        # 10 ブロックのうち 4 つが重なるだけの宣言。巡回でずらす帰無分布では有意に出ていた（判断 15）。
        ref = self._ref(["a", "a", "v", "a", "v", "v", "a", "v", "v", "a"])
        _, p = core.block_permutation_pvalue(self.lab, ref, self.blocks, 999, np.random.default_rng(0))
        self.assertGreater(p, 0.05)

    def test_rejects_ref_that_varies_within_a_block(self):
        with self.assertRaises(ValueError):
            core.block_permutation_pvalue(np.array([0, 1, 0]), np.array(["a", "v", "a"]),
                                          np.array([0, 0, 1]), 9, np.random.default_rng(0))


if __name__ == "__main__":
    unittest.main()
