"""act_hmm の単体テスト（python3 -I -m unittest test_act_hmm）。

前向き後ろ向きと Viterbi を、欠測を 1 歩ずつ歩く素朴な HMM の総当たりと比べる。
"""

import itertools
import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import act_hmm as hm  # noqa: E402


def full_transition(k, p):
    if k == 1:
        return np.ones((1, 1))
    a = np.full((k, k), (1 - p) / (k - 1))
    np.fill_diagonal(a, p)
    return a


def brute(labels, missing, h):
    """窓を 1 歩ずつ歩く全経路の (尤度の和, 最大の経路の確率)。欠測の窓の出力は 1。"""
    k = h.k
    a = full_transition(k, h.p_stay)
    total, best = 0.0, 0.0
    for path in itertools.product(range(k), repeat=len(labels)):
        pr = h.pi[path[0]]
        for t, s in enumerate(path):
            if t > 0:
                pr *= a[path[t - 1], s]
            if not missing[t]:
                pr *= h.emis[s, labels[t]]
        total += pr
        best = max(best, pr)
    return total, best


def path_score(seq, path, h):
    lp = math.log(h.pi[path[0]]) + math.log(h.emis[path[0], seq.obs[0]])
    for t in range(1, len(path)):
        lp += math.log(hm.trans_max(h.k, h.p_stay, int(seq.gap[t]) + 1)[path[t - 1], path[t]])
        lp += math.log(h.emis[path[t], seq.obs[t]])
    return lp


class BruteForceTest(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(7)
        self.h = hm.Hmm(np.array([0.5, 0.3, 0.2]), rng.dirichlet(np.ones(4), size=3), 0.8)

    def _case(self, labels, missing):
        labels, missing = np.array(labels), np.array(missing, dtype=bool)
        # 頭の欠測は捨てる設計なので、比べる素朴な HMM も最初の観測から始める。
        first = int(np.argmax(~missing))
        seqs = hm.build_sequences(labels, missing, np.zeros(len(labels), dtype=bool))
        self.assertEqual(len(seqs), 1)
        total, best = brute(labels[first:], missing[first:], self.h)
        self.assertAlmostEqual(hm.loglik(seqs, self.h), math.log(total), places=10)
        path = hm.viterbi(seqs[0], self.h)
        self.assertAlmostEqual(path_score(seqs[0], path, self.h), math.log(best), places=10)

    def test_no_missing(self):
        self._case([0, 1, 1, 3, 2, 0], [0] * 6)

    def test_missing_in_middle(self):
        self._case([0, 9, 9, 3, 2, 9, 1], [0, 1, 1, 0, 0, 1, 0])

    def test_leading_missing(self):
        self._case([9, 9, 2, 2, 9, 0], [1, 1, 0, 0, 1, 0])

    def test_posteriors_sum_to_one(self):
        seqs = hm.build_sequences(np.array([0, 1, 2, 3, 0]), np.zeros(5, dtype=bool), np.zeros(5, dtype=bool))
        g, _ = hm.forward_backward(seqs[0], self.h)
        np.testing.assert_allclose(g.sum(axis=1), 1.0)


class TransitionTest(unittest.TestCase):
    def test_power_matches_matrix_power(self):
        for k in (2, 3, 5):
            a = full_transition(k, 0.9)
            for n in (1, 2, 7):
                np.testing.assert_allclose(hm.trans_sum(k, 0.9, n), np.linalg.matrix_power(a, n), atol=1e-12)

    def test_max_matches_brute(self):
        k, p = 3, 0.85
        a = full_transition(k, p)
        for n in (1, 2, 4):
            want = np.zeros((k, k))
            for i in range(k):
                for path in itertools.product(range(k), repeat=n):
                    pr, prev = 1.0, i
                    for s in path:
                        pr *= a[prev, s]
                        prev = s
                    want[i, path[-1]] = max(want[i, path[-1]], pr)
            np.testing.assert_allclose(hm.trans_max(k, p, n), want, atol=1e-12)


class SequenceTest(unittest.TestCase):
    def test_reset_splits_and_gap_counts(self):
        labels = np.array([0, 1, 9, 9, 2, 0, 1])
        missing = np.array([0, 0, 1, 1, 0, 0, 0], dtype=bool)
        reset = np.array([0, 0, 0, 0, 0, 1, 0], dtype=bool)
        seqs = hm.build_sequences(labels, missing, reset)
        self.assertEqual([s.obs.tolist() for s in seqs], [[0, 1, 2], [0, 1]])
        self.assertEqual(seqs[0].gap.tolist(), [0, 0, 2])
        self.assertEqual(seqs[1].gap.tolist(), [0, 0])
        self.assertEqual(seqs[1].index.tolist(), [5, 6])

    def test_reset_points(self):
        idle = np.array([0, 1, 1, 1, 0, 1, 0], dtype=bool)
        r = hm.reset_points(idle, None, 180, 540)
        self.assertEqual(np.flatnonzero(r).tolist(), [4])  # 3 窓（540 秒）の無操作の後だけ

    def test_reset_points_seams_break_idle_runs(self):
        idle = np.array([0, 1, 1, 1, 0], dtype=bool)
        seams = np.array([1, 0, 0, 1, 0, 1], dtype=bool)
        r = hm.reset_points(idle, seams, 180, 540)
        self.assertEqual(np.flatnonzero(r).tolist(), [0, 3])  # 継ぎ目で無操作の長さが切れる


class FitTest(unittest.TestCase):
    def _sample(self, rng, emis, blocks):
        lab = []
        truth = []
        for state, n in blocks:
            lab += list(rng.choice(emis.shape[1], size=n, p=emis[state]))
            truth += [state] * n
        return np.array(lab), np.array(truth)

    def test_two_tasks_are_recovered(self):
        rng = np.random.default_rng(1)
        emis = np.array([[0.7, 0.2, 0.1, 0.0], [0.0, 0.1, 0.3, 0.6]])
        lab, truth = self._sample(rng, emis, [(0, 30), (1, 20), (0, 25), (1, 30), (0, 20)])
        seqs = hm.build_sequences(lab, np.zeros(len(lab), dtype=bool), np.zeros(len(lab), dtype=bool))
        h = hm.select_hmm(seqs, 4, 4, hm.stay_prob(15), seed=3, n_init=3, pseudo=1.0)
        self.assertEqual(h.k, 2)
        dec = hm.decode(seqs, h, len(lab))
        agree = max((dec == truth).mean(), (dec == 1 - truth).mean())
        self.assertGreater(agree, 0.9)

    def test_single_task_selects_one(self):
        rng = np.random.default_rng(2)
        emis = np.array([[0.4, 0.3, 0.2, 0.1]])
        lab, _ = self._sample(rng, emis, [(0, 150)])
        seqs = hm.build_sequences(lab, np.zeros(len(lab), dtype=bool), np.zeros(len(lab), dtype=bool))
        h = hm.select_hmm(seqs, 4, 4, hm.stay_prob(15), seed=3, n_init=3, pseudo=1.0)
        self.assertEqual(h.k, 1)


class NameTest(unittest.TestCase):
    def test_names_by_total_duration(self):
        names = hm.name_states(np.array([1, 1, 0, -1, 1]), np.full(5, 180.0))
        self.assertEqual(names[1], "work-A")
        self.assertEqual(names[0], "work-B")
        self.assertEqual(names[-1], "none")


if __name__ == "__main__":
    unittest.main()
