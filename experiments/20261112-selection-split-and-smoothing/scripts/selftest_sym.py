"""B1 の対称版の門（conditions.md の追記「門」・合成だけ）。

使い方: python3 -I selftest_sym.py <out.json> [--mutate y1..y3] [--run-id ID]
返り値: 0 = すべて通った・3 = 通らない門がある。
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinned4  # noqa: E402
import sym as SM  # noqa: E402
from pinned4 import H, ml  # noqa: E402

NAMES = ["P-HASH", "P-REPLAY", "P-SYMPRIOR", "P-SELW"]
SEED = pinned4.SEED


def unit_of(seq):
    return dict(start=0, seqs=[seq], pflag=[np.ones(len(seq), dtype=bool)], probes=[], probes_all=[])


def p_hash():
    return dict(passed=True, hashes=pinned4.hashes())


def p_replay():
    """合成の書き手 4 人（各 10 単位）で、倍率 1 の引き直しの本人 ar3 の評価が mode の em_writer と同じで、
    書き手の乱数を引き終えた状態も同じ（折り目の乱数の引き忘れを捕まえる）。"""
    rng = np.random.default_rng([SEED, 21])
    A = 0.95 * np.eye(2) + 0.05 * rng.dirichlet(np.ones(2), 2)
    m = dict(kind="ar", pi=np.ones(2) / 2, A=A / A.sum(1, keepdims=True), H=rng.dirichlet(np.ones(H.NSYM), 2),
             C=np.stack([rng.dirichlet(np.full(H.NSYM, 0.3), H.NSYM) for _ in range(2)]))
    writers = [[unit_of(s) for s in H.sample(m, [80] * 10, rng)] for _ in range(4)]
    full = {ml.sname(s): ml.fit_pool_full(dict(ds="coauthor", si=ml.SEQ_NO[s], seed=SEED, writers=writers))[0] for s in ml.STRUCTS}
    ok, n = True, 0
    for w in (0, 2):
        pools = {}
        for s in ml.STRUCTS:
            pm, sb, _ = ml.fit_pool_excl(dict(ds="coauthor", writers=writers, w=w, start=full[ml.sname(s)]))
            pools[ml.sname(s)] = (pm, sb)
        ks = [k for k in ml.DATASETS["coauthor"]["grid"] if k <= len(writers[w]) - 5]
        r1 = np.random.default_rng([SEED + 10, w])
        res = ml.em_writer(writers[w], 5, ks, pools, r1)
        r2 = np.random.default_rng([SEED + 10, w])
        mine = SM.replay_writer(writers[w], 5, ks, [2, 5], pools["ar3"][0], pools["ar3"][1], r2, 1.0)
        for k in ("2", "5"):
            for t in map(str, ml.TAUS_FIT):
                ok = ok and mine[k][t] == res["k"][k]["self"]["ar3"][t]
                n += 1
        ok = ok and r1.bit_generator.state == r2.bit_generator.state
    return dict(passed=bool(ok), compared=n)


def p_symprior():
    rng = np.random.default_rng([SEED, 22])
    ok = True
    for kind, K in (("ar", 3), ("hmm", 3)):
        base = H.base_prior(kind, K)
        sb = {k: rng.random(v.shape) for k, v in base.items()}
        p = SM.prior_sym(kind, K, 1e5, sb, 0.03)
        ok = ok and all(np.array_equal(p[k], base[k] * 0.03 + 1e5 * sb[k]) for k in base)
        p1, q1 = SM.prior_sym(kind, K, 1e5, sb, 1.0), H.make_prior(kind, K, 1e5, sb)
        ok = ok and all(np.array_equal(p1[k], q1[k]) for k in base)
        ok = ok and all(np.array_equal(SM.prior_sym(kind, K, 0, None, 0.03)[k], base[k] * 0.03) for k in base)
    return dict(passed=bool(ok))


def p_selw():
    """sym_picks の選びに、w = 0 の本人' と共通(0.03) を書き換えて渡しても、w = 0 の選びが変わらない（乱数 200 回）。"""
    rng = np.random.default_rng([SEED, 23])
    ws = list(range(8))
    flips = 0
    for _ in range(200):
        R = {v: dict(em=dict(k={"5": dict(r1=[float(rng.normal()), None])})) for v in ws}
        S03 = {v: {"5": {t: [float(rng.normal()), None] for t in ml.TAU_KEYS}} for v in ws}
        P03 = {v: [float(rng.normal()), None] for v in ws}
        a = SM.sym_picks(ws, 5, R, S03, P03)
        S03[0] = {"5": {t: [float(rng.normal() * 10), None] for t in ml.TAU_KEYS}}
        P03[0] = [float(rng.normal() * 10), None]
        b = SM.sym_picks(ws, 5, R, S03, P03)
        flips += (a[0][0] != b[0][0]) + (a[1][0] != b[1][0])
    return dict(passed=bool(flips == 0), flips=int(flips))


FUNCS = {"P-HASH": p_hash, "P-REPLAY": p_replay, "P-SYMPRIOR": p_symprior, "P-SELW": p_selw}


def main():
    argv = sys.argv[1:]
    mut, run_id = [], None
    while "--mutate" in argv:
        i = argv.index("--mutate"); mut.append(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    SM.MUT.clear()
    SM.MUT.update(mut)
    S = dict(run_id=run_id, mutate=mut)
    for n in NAMES:
        S[n] = FUNCS[n]()
        print(n, S[n]["passed"], flush=True)
    S["passed"] = all(S[n]["passed"] for n in NAMES)
    json.dump(S, open(argv[0], "w", newline="\n"), indent=1, default=str)
    return 0 if S["passed"] else 3


if __name__ == "__main__":
    sys.exit(main())
