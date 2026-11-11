"""門（conditions.md V1・合成の値だけ・当てはめもデータも無い）。P-HASH は pinned4 の読み込みで止める。

使い方: python3 -I selftest.py <out.json> [--mutate o1..o3] [--run-id ID]
返り値: 0 = すべて通った・3 = 通らない門がある。
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import obj as OB  # noqa: E402
import pinned4  # noqa: E402
from pinned4 import SEL  # noqa: E402

NAMES = ["P-HASH", "P-MEAN", "P-NOW", "P-NEGINF", "P-SAMEMED"]
SEED = pinned4.SEED


def p_hash():
    return dict(passed=True, hashes=pinned4.all_hashes())


def p_mean():
    """中央値なら b・平均なら a になる値（w = "x" を除く 5 人）。"""
    vals = {v: dict(a=a, b=1.0) for v, a in zip("pqrst", [0.0, 0.0, 0.0, 10.0, 10.0])}
    vals["x"] = dict(a=-100.0, b=100.0)
    got = OB.select_mean(vals, "x", ["a", "b"])
    return dict(passed=got == "a", got=got)


def p_now():
    rng = np.random.default_rng([SEED, 91])
    cands = ["c%d" % i for i in range(6)]
    flips = 0
    for _ in range(200):
        vals = {v: {c: float(rng.normal()) for c in cands} for v in range(7)}
        a = OB.select_mean(vals, 0, cands)
        vals[0] = {c: float(rng.normal() * 10) for c in cands}
        flips += a != OB.select_mean(vals, 0, cands)
    return dict(passed=flips == 0, flips=flips)


def p_neginf():
    vals = {v: dict(a=a, b=1.0) for v, a in zip("pqrst", [-np.inf, 5.0, 5.0, 5.0, 5.0])}
    vals["x"] = dict(a=0.0, b=0.0)
    try:
        got = OB.select_mean(vals, "x", ["a", "b"])
        allinf = {v: dict(a=-np.inf, b=-np.inf) for v in "pqr"}
        got2 = OB.select_mean(allinf, "x", ["a", "b"])
    except (ValueError, FloatingPointError) as e:
        return dict(passed=False, note=str(e))
    return dict(passed=got == "b" and got2 == "a", got=got, got_all_inf=got2)


def p_samemed():
    """選びを中央値に戻すと sel の _select と同じ（乱数 200 回・−∞ を混ぜる）。"""
    rng = np.random.default_rng([SEED, 92])
    cands = ["c%d" % i for i in range(5)]
    diff = 0
    for _ in range(200):
        vals = {v: {c: (-np.inf if rng.random() < 0.05 else float(rng.normal())) for c in cands} for v in range(6)}
        for w in vals:
            diff += OB.select_agg(vals, w, cands, np.median) != SEL._select(vals, w, cands)
    return dict(passed=diff == 0, diff=int(diff))


FUNCS = {"P-HASH": p_hash, "P-MEAN": p_mean, "P-NOW": p_now, "P-NEGINF": p_neginf, "P-SAMEMED": p_samemed}


def main():
    argv = sys.argv[1:]
    mut, run_id = [], None
    while "--mutate" in argv:
        i = argv.index("--mutate"); mut.append(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    OB.MUT.clear()
    OB.MUT.update(mut)
    S = dict(run_id=run_id, mutate=mut)
    for n in NAMES:
        try:
            S[n] = FUNCS[n]()
        except Exception as e:  # noqa: BLE001
            S[n] = dict(passed=False, note="例外: %s: %s" % (type(e).__name__, e))
        print(n, S[n]["passed"], flush=True)
    S["passed"] = all(S[n]["passed"] for n in NAMES)
    with open(argv[0], "w", newline="\n") as f:
        json.dump(S, f, indent=1, default=str)
    return 0 if S["passed"] else 3


if __name__ == "__main__":
    sys.exit(main())
