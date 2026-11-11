"""門（conditions.md V1・合成だけ）。P-HASH は pinned5 の読み込みで止める。

使い方: python3 -I selftest10.py <out.json> [--mutate e1..e4] [--run-id ID]
返り値: 0 = すべて通った・3 = 通らない門がある。
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinned5  # noqa: E402
import ten as TN  # noqa: E402
from pinned5 import RS, SY  # noqa: E402

NAMES = ["P-HASH", "P-PLAN", "P-RULE", "P-PAIR"]


def p_hash():
    return dict(passed=True, hashes=pinned5.hashes())


def p_plan():
    rows = TN.plan()
    old = RS.plan()
    ok = len(rows) == 55 and rows[:13] == old[:13] and all(r["strand"] == "dose" and r["shape"] == "coauthor" and r["K"] == 3
                                                         for r in old[:13])
    new = rows[13:]
    ok = ok and [r["no"] for r in new] == list(range(33, 75)) and not ({r["no"] for r in new} & {r["no"] for r in old})
    keys = [(r["g"], r["seed"]) for r in rows]
    ok = ok and len(keys) == len(set(keys))
    ok = ok and sorted(s for g, s in keys if g == 0) == list(range(15))
    ok = ok and all(sorted(s for g2, s in keys if g2 == g) == list(range(10)) for g in TN.LEVELS)
    return dict(passed=bool(ok))


def p_rule():
    """作った例: U の種 0〜4 の中央値 1〜5e-4 → U = 5e-4。FA の種 5〜14: 6e-4（良 0.9）・6e-4（良 0.5）・ほか 1e-4 → FA = 0.1。
    段 1e-3: 5 種が 6e-4（良 0.9）→ DR 0.5。3e-3: 8 種が 1e-3 → 0.8。1e-2: 10 種 → 1.0。3e-2: 9 種 → 0.9。L80 = 3e-3。"""
    cs = [dict(g=0.0, seed=s, median=(s + 1) * 1e-4, share=0.9) for s in range(5)]
    cs += [dict(g=0.0, seed=5, median=6e-4, share=0.9), dict(g=0.0, seed=6, median=6e-4, share=0.5)]
    cs += [dict(g=0.0, seed=s, median=1e-4, share=0.9) for s in range(7, 15)]
    hits = {1e-3: 5, 3e-3: 8, 1e-2: 10, 3e-2: 9}
    val = {1e-3: 6e-4, 3e-3: 1e-3, 1e-2: 1e-3, 3e-2: 1e-3}
    for g, n in hits.items():
        cs += [dict(g=g, seed=s, median=(val[g] if s < n else 1e-4), share=0.9) for s in range(10)]
    r = TN.rule(cs)
    DR = {g: r["levels"][str(g)]["DR"] for g in hits}
    ok = abs(r["U"] - 5e-4) < 1e-15 and r["fa_n"] == 10 and abs(r["FA"] - 0.1) < 1e-12
    ok = ok and DR == {1e-3: 0.5, 3e-3: 0.8, 1e-2: 1.0, 3e-2: 0.9} and r["L80"] == 3e-3
    ok = ok and r["null"]["n"] == 15 and r["null"]["above_real_low"] == 3 and r["null"]["above_real_high"] == 0
    return dict(passed=bool(ok), U=r["U"], FA=r["FA"], DR={str(k): v for k, v in DR.items()}, L80=r["L80"])


def p_pair():
    """同じ種の陰性対照と植えた段の単位の長さが同じで、陰性対照の書き手の真の母数が m0 と同じ（CoAuthor の実寸・種 5）。"""
    seed = pinned5.SENS_SEED
    m0 = SY.make_m0(3, seed)
    lam = pinned5.calibration()[3][str(1e-2)]["lam"]
    w0, mo0, _, _ = SY.build("coauthor", 3, 5, SY.lam_rule("dose", 0.0), m0, seed)
    w1, mo1, _, _ = SY.build("coauthor", 3, 5, SY.lam_rule("dose", lam), m0, seed)
    ok = all([len(s) for u in a for s in u["seqs"]] == [len(s) for u in b for s in u["seqs"]] for a, b in zip(w0, w1))
    ok = ok and all(np.array_equal(m["C"], m0["C"]) for m in mo0) and not all(np.array_equal(m["C"], m0["C"]) for m in mo1)
    return dict(passed=bool(ok))


FUNCS = {"P-HASH": p_hash, "P-PLAN": p_plan, "P-RULE": p_rule, "P-PAIR": p_pair}


def main():
    argv = sys.argv[1:]
    mut, run_id = [], None
    while "--mutate" in argv:
        i = argv.index("--mutate"); mut.append(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    TN.MUT.clear()
    TN.MUT.update(mut)
    S = dict(run_id=run_id, mutate=mut)
    for n in NAMES:
        S[n] = FUNCS[n]()
        print(n, S[n]["passed"], flush=True)
    S["passed"] = all(S[n]["passed"] for n in NAMES)
    json.dump(S, open(argv[0], "w"), indent=1, default=str)
    return 0 if S["passed"] else 3


if __name__ == "__main__":
    sys.exit(main())
