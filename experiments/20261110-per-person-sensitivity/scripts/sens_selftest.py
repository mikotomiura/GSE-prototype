"""陽性対照（conditions.md V1・合成だけ）。

使い方: python3 -I sens_selftest.py <seed> <out.json> [--mutate v1|v2|v3|v4|v5] [--only P-A,P-B] [--run-id ID] [--jobs N]
返り値: 0 = すべて通った・3 = 通らない対照がある（変異の門は 3 を赤と読む）。
変異: v1・v2・v4 は synth.MUT、v3 は tau-extend の m12（ml.MUT）、v5 は m6（data.MUT）。
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analysis as AN  # noqa: E402
import pinned  # noqa: E402
import run_synth as RS  # noqa: E402
import synth as SY  # noqa: E402
from pinned import DT, H, ml  # noqa: E402

NAMES = ["P-HASH", "P-PLANT0", "P-MEAN", "P-DIFF", "P-CAL", "P-GROUP", "P-SPLIT", "P-NULLSAME", "P-JOINTW", "P-RECOVER"]
MUT_MAP = {"v3": ("ml", "m12"), "v5": ("ml", "m6")}


def p_hash(seed, jobs):
    h = pinned.hashes()
    return dict(passed=h == pinned.PINNED, hashes=h)


def p_plant0(seed, jobs):
    m0 = SY.make_m0(3, seed)
    rng = np.random.default_rng([seed, 1])
    D = SY.draw_D(m0, rng)
    mw = SY.writer_model(m0, D, 0.0)
    u = np.random.default_rng([seed, 2]).random((2000, 2))
    seqs = [SY.Sampler(mw).seq(u)]
    _, h, T = H.r0_r1(seqs)
    ref, _ = H.fit([("r", H.random_model("ar", 3, rng, r1=T, r0=h))], H.Data(seqs), H.base_prior("ar", 3))
    g = SY.gain(mw, m0, seqs, ref=ref)
    same = all(np.array_equal(mw[k], m0[k]) for k in ("pi", "A", "H", "C"))
    return dict(passed=bool(same and g == 0.0), same=bool(same), g=float(g))


def p_mean(seed, jobs):
    m0 = SY.make_m0(3, seed)
    rng = np.random.default_rng([seed, 3])
    K = len(m0["pi"])
    mx = 0.0
    for k in range(K):
        for j in range(SY.NSYM):
            d = rng.dirichlet(SY.D_CONC * m0["C"][k, j], size=20000).mean(0)
            mx = max(mx, float(np.abs(d - m0["C"][k, j]).max()))
    return dict(passed=mx < 0.01, max_abs=mx)


_BUILT = {}


def built(kind, seed):
    if kind not in _BUILT:
        m0 = SY.make_m0(3, seed)
        lam = {"dose": 0.3, "dist": 0.3, "null": 0.0}[kind]
        strand = "dist" if kind == "dist" else "dose"
        _BUILT[kind] = (SY.build("coauthor", 3, 0, SY.lam_rule(strand, lam), m0, seed), m0)
    return _BUILT[kind]


def p_diff(seed, jobs):
    (writers, models, lams, P), m0 = built("dose", seed)
    diff = not np.array_equal(models[0]["C"], models[1]["C"])
    return dict(passed=bool(diff and lams[0] > 0))


def p_cal(seed, jobs):
    m0 = SY.make_m0(3, seed)
    c = SY.calibrate(m0, 1e-2, seed, n_w=10, L=5000)
    return dict(passed=bool(c["ok"]), **c)


def p_group(seed, jobs):
    (writers, models, lams, P), m0 = built("dist", seed)
    got = [i for i, x in enumerate(lams) if x > 0]
    want = [i for i in range(len(lams)) if i % 4 == 0]
    return dict(passed=got == want, n_planted=len(got))


def p_split(seed, jobs):
    (writers, models, lams, P), m0 = built("null", seed)
    H_ = SY.SHAPES["coauthor"]["H"]
    ok = True
    for w in range(P):
        n = len(writers[w])
        for k in SY.SHAPES["coauthor"]["ks"]:
            tr, te = DT.split(n, k, H_)
            ok = ok and not (set(tr) & set(te)) and max(tr) < min(te)
        ev_ids = {id(writers[w][i]) for i in DT.split(n, 1, H_)[1]}
        for v in range(len(writers)):
            ok = ok and not (ev_ids & {id(u) for u in ml.pool_units(writers, H_, exclude=v)})
    return dict(passed=bool(ok))


def p_nullsame(seed, jobs):
    (writers, models, lams, P), m0 = built("null", seed)
    same = all(np.array_equal(models[i]["C"], m0["C"]) for i in range(len(models)))
    return dict(passed=bool(same))


def p_jointw(seed, jobs):
    jc = [("ar1", "inf"), ("ar1", "0")]
    made = {0: {jc[0]: 1.0, jc[1]: 0.0}, 1: {jc[0]: 0.0, jc[1]: 1.0}, 2: {jc[0]: 10.0, jc[1]: 0.0}}
    a = ml.select_joint(made, 2, jc)
    made2 = dict(made)
    made2[2] = {jc[0]: 0.0, jc[1]: 10.0}
    ok = a == ml.select_joint(made2, 2, jc)
    rng = np.random.default_rng([seed, 5])
    cands = ml.joint_cands()
    flips = 0
    for _ in range(200):
        vals = {v: {c: float(rng.normal()) for c in cands} for v in range(6)}
        a = ml.select_joint(vals, 0, cands)
        vals[0] = {c: float(rng.normal() * 10) for c in cands}
        flips += a != ml.select_joint(vals, 0, cands)
    return dict(passed=bool(ok and flips == 0), made_ok=bool(ok), flips=flips)


def p_recover(seed, jobs):
    SY.SHAPES["tiny"] = dict(i=9, ds="coauthor", H=5, P=8, Pu=20, O=0, Ou=0, nseq=1, L=(400, 400), ks=[15])
    m0 = SY.make_m0(3, seed)
    c = SY.calibrate(m0, 0.1, seed, n_w=10, L=5000)
    if not c["ok"]:
        return dict(passed=False, note="較正が入らない", cal=c)
    r = dict(no=99, strand="dose", shape="tiny", K=3, g=0.1, seed=0)
    R = RS.run_rep(r, {3: {"0.1": c}}, {3: m0}, seed, jobs, mut=sorted(ml.MUT), smut=sorted(SY.MUT))
    C = AN.cell(R, "15")
    return dict(passed=bool(C["main"]["median"] > 0 and C["main"]["better_share"] >= 0.75),
                main=C["main"], g=C["g"], chosen_tau=C["chosen_tau"], chosen_struct=C["chosen_struct"],
                seconds=R["seconds"])


FUNCS = {"P-HASH": p_hash, "P-PLANT0": p_plant0, "P-MEAN": p_mean, "P-DIFF": p_diff, "P-CAL": p_cal,
         "P-GROUP": p_group, "P-SPLIT": p_split, "P-NULLSAME": p_nullsame, "P-JOINTW": p_jointw, "P-RECOVER": p_recover}


def main():
    argv = sys.argv[1:]
    mut, only, run_id, jobs = [], None, None, 8
    while "--mutate" in argv:
        i = argv.index("--mutate"); mut.append(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if "--only" in argv:
        i = argv.index("--only"); only = argv[i + 1].split(","); argv = argv[:i] + argv[i + 2:]
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    if "--jobs" in argv:
        i = argv.index("--jobs"); jobs = int(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    seed, out = int(argv[0]), argv[1]
    ml.set_mut([MUT_MAP[m][1] for m in mut if m in MUT_MAP])
    SY.MUT.clear()
    SY.MUT.update(m for m in mut if m not in MUT_MAP)
    S = dict(run_id=run_id, mutate=mut)
    t0 = time.time()
    for name in (only or NAMES):
        t = time.time()
        S[name] = FUNCS[name](seed, jobs)
        S[name]["seconds"] = time.time() - t
        print(name, S[name]["passed"], flush=True)
    S["seconds"] = time.time() - t0
    S["passed"] = all(S[n]["passed"] for n in (only or NAMES))
    json.dump(S, open(out, "w"), indent=1, default=float)
    return 0 if S["passed"] else 3


if __name__ == "__main__":
    sys.exit(main())
