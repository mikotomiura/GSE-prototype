"""search_noise.py の検査（ネットワークに出ない）。使い方: python -m unittest test_search_noise"""
import unittest

import search_noise as N


class TestSample(unittest.TestCase):
    def test_sample_is_fixed_by_seed_and_uses_dois_only(self):
        ids = {("doi", f"10.1/{i:04d}") for i in range(200)} | {("s2", "abc"), ("epmc", "MED:1")}
        a, b = N.sample(ids), N.sample(set(ids))
        self.assertEqual(a, b)
        self.assertEqual(len(a), 50)
        self.assertTrue(all(x.startswith("10.1/") for x in a))
        self.assertNotEqual(a, N.sample(ids, seed=1))

    def test_small_population_returns_all(self):
        self.assertEqual(sorted(N.sample({("doi", "10.1/a"), ("doi", "10.1/b")})), ["10.1/a", "10.1/b"])


class TestGuard(unittest.TestCase):
    def test_refuses_hosts_outside_the_allow_list(self):
        with self.assertRaises(ValueError):
            N.get_json("https://api.openalex.org/works/doi:10.1/x")
        with self.assertRaises(ValueError):
            N.get_json("https://api.crossref.org.evil/works/10.1/x")


if __name__ == "__main__":
    unittest.main()
