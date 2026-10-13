"""The seed formula of the preregistration ("Candidates, scope and numbers", random numbers; config.json seed_derivation)."""
import hashlib
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
USES = ("split", "eval_sample", "decoys", "window_start", "r5_sub", "r6_perm", "r7_drop", "bootstrap", "enja_decoys",
        "negative_control", "check7", "synthetic",
        # exploratory analyses (decisions 55 and 56; exploratory.json; config.json seed_uses is frozen and unchanged)
        "exploratory_unicity", "exploratory_dp")


def read_seed(path=None):
    with open(path or os.path.join(HERE, "..", "SEED"), encoding="utf-8") as f:
        return f.read().strip()


def seed_int(seed, use, prompt="", writer="", N="", k="", draw=""):
    if use not in USES:
        raise ValueError("unknown seed use: %r" % (use,))
    s = f"{seed}:{use}:{prompt}:{writer}:{N}:{k}:{draw}"
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


def rng(seed, use, prompt="", writer="", N="", k="", draw=""):
    """numpy.random.default_rng from the formula; unused fields are empty strings."""
    return np.random.default_rng(seed_int(seed, use, prompt, writer, N, k, draw))
