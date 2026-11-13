"""門（conditions.md V1）。実データは読まない（m0 は偽: sens の make_m0 を疎にしたもの）。

使い方: python3 -I selftest_null.py <out.json> [--mutate n1..n7] [--run-id ID] [--jobs 4]
返り値: 0 = すべて通った・3 = 通らない門がある。
"""
import json
import math
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_m0 as FM  # noqa: E402  (PINNED と m0_checks だけを使う。compute は読み込まない)
import null as NL  # noqa: E402
import pinned6  # noqa: E402
from pinned6 import AN, RS, SY, TEN, ml  # noqa: E402

NAMES = ["P-HASH", "P-PLAN", "P-M0", "P-M0USE", "P-SPARSE", "P-B", "P-PICK", "P-REAL", "P-READ", "P-SMOKE"]
SEED = NL.SEED_WANT
SY.SHAPES["tiny"] = dict(i=0, ds="coauthor", H=5, P=4, Pu=8, O=2, Ou=5, nseq=1, L=(200, 200), ks=[1, 3])
ACTIVE = [0, 3, 7, 11, 18, 22]
JOBS = [4]
_CACHE = {}


def fake_m0():
    """偽の m0: sens の make_m0(3) を、6 記号に集めた疎な母数にする（他のセルは 1e-9・行の和は 1）。"""
    m = SY.make_m0(3, SEED)
    mask = np.full(SY.NSYM, 1e-9)
    mask[ACTIVE] = 1.0
    Hh = m["H"] * mask
    C = m["C"] * mask[None, None, :]
    return dict(kind="ar", pi=m["pi"].copy(), A=m["A"].copy(), H=Hh / Hh.sum(1, keepdims=True), C=C / C.sum(2, keepdims=True))


def p_hash():
    h = pinned6.hashes()
    b = {os.path.relpath(p, pinned6.EXP): FM.sha(p) == v for p, v in FM.PINNED.items()}
    return dict(passed=all(b.values()), pinned=h, b_code=b)


def p_plan():
    rows = NL.plan()
    ok = rows == TEN.plan() and len(rows) == 55
    seeds = set(NL.gate_seeds())
    nos = {NL.gate_no(ai, si) for ai in range(len(NL.ALPHAS)) for si in range(len(NL.GATE_SEEDS))}
    ok = ok and not (seeds & {r["seed"] for r in rows}) and not (nos & {r["no"] for r in rows})
    ok = ok and nos == set(range(200, 212)) and NL.ALPHAS == ["1", "0.3", "0.1", "0.03"]
    return dict(passed=bool(ok), gate_seeds=sorted(seeds))


def p_m0():
    m = fake_m0()
    ok = NL.m0_ok(m) and FM.m0_checks(m)["rows_sum_1"]
    bad = dict(m, C=m["C"] * 1.1)
    ok = ok and not NL.m0_ok(bad) and not NL.m0_ok(dict(m, pi=np.ones(2) / 2))
    with tempfile.TemporaryDirectory() as d:
        npz, js = os.path.join(d, "m0.npz"), os.path.join(d, "m0.json")
        with open(npz, "wb") as f:
            np.savez(f, **{"a%s_%s" % (a, k): m[k] for a in NL.ALPHAS for k in NL.KEYS})
        json.dump(dict(alphas=NL.ALPHAS, npz_sha256=FM.sha(npz)), open(js, "w"))
        got, _ = NL.load_m0(npz, js)
        ok = ok and all(np.array_equal(got[a][k], m[k]) for a in NL.ALPHAS for k in NL.KEYS)
        json.dump(dict(alphas=NL.ALPHAS, npz_sha256="0" * 64), open(js, "w"))
        try:
            NL.load_m0(npz, js)
            ok = False
        except SystemExit:
            pass
    return dict(passed=bool(ok))


def p_m0use():
    m = fake_m0()
    writers, models, lams, P = NL.null_writers("tiny", 0, m, SEED)
    ok = all(np.array_equal(md[k], m[k]) for md in models for k in NL.KEYS) and all(x == 0 for x in lams)
    ok = ok and all(np.array_equal(NL.m0s_for_run(m, SEED)[3][k], m[k]) for k in NL.KEYS)
    return dict(passed=bool(ok))


def p_sparse():
    m = fake_m0()
    rng = np.random.default_rng([SEED, 9])
    ok = (m["C"] < 1e-6).any()
    worst = 0.0
    with np.errstate(all="raise"):
        for _ in range(2000):
            D = SY.draw_D(m, rng)
            if not np.isfinite(D).all():
                ok = False
                break
            worst = max(worst, float(np.abs(D.sum(2) - 1).max()))
    return dict(passed=bool(ok and worst <= 1e-9), worst_row_sum_err=worst)


def own_mode(sb):
    """独立の最頻値: S̄ を自前で正規化（和 0 の C の行は一様）。"""
    out = dict(kind="ar")
    for k in NL.KEYS:
        X = np.asarray(sb[k], dtype=float)
        tot = X.sum(-1, keepdims=True)
        out[k] = np.where(tot > 0, X / np.where(tot > 0, tot, 1), 1.0 / X.shape[-1])
    return out


def gate_tiny():
    if "g" not in _CACHE:
        _CACHE["g"] = NL.gate_b(fake_m0(), NL.gate_seeds()[0], NL.gate_no(0, 0), SEED, JOBS[0], shape="tiny", detail=True)
    return _CACHE["g"]


def p_b():
    g = gate_tiny()
    compared, bad = 0, []
    for w, pt in enumerate(g["parts"]):
        mo = own_mode(pt["sb"])
        ref, _ = NL.HM.mode_of("ar", pt["sb"])
        same_mode = all(np.abs(mo[k] - ref[k]).max() <= 1e-15 for k in NL.KEYS)
        with np.errstate(divide="ignore", invalid="ignore"):
            ind = ml.Eval(pt["ev_seqs"], ml.pflags_of(pt["ev_units"])).ll(mo)[0]
        if np.isfinite(pt["mode"]):
            compared += 1
            ok_w = same_mode and abs(ind - pt["mode"]) <= 1e-12 and abs(g["b"][w] - (ind - pt["pool"])) <= 1e-12
        else:
            ok_w = same_mode and not np.isfinite(ind) and np.isneginf(g["b"][w])
        if not ok_w:
            bad.append(w)
    med_ok = NL.b_median([-np.inf, -np.inf, 1.0, 2.0, 3.0]) == 1.0
    return dict(passed=bool(compared >= 2 and not bad and med_ok), compared=compared, bad=bad, median_with_neginf=med_ok)


def p_pick():
    G1 = {"1": dict(b_s=[1e-5, 2e-5, 3e-5]), "0.3": dict(b_s=[5e-4, 6e-4, 7e-4]), "0.1": dict(b_s=[2e-3, 3e-3, 4e-3]),
          "0.03": dict(b_s=[-1e-4, 1e-2, 1e-2])}
    ok = NL.pick_alpha(G1) == "0.3"
    G2 = dict(G1, **{"0.3": dict(b_s=[5e-4, -1e-6, 7e-4])})
    ok = ok and NL.pick_alpha(G2) == "0.1"   # |log(3e-3/7.4e-4)| = 1.40 < |log(2e-5/7.4e-4)| = 3.61
    G3 = {a: dict(b_s=[-1e-5, 1e-4, 1e-4]) for a in NL.ALPHAS}
    try:
        NL.pick_alpha(G3)
        ok = False
    except NL.GateStop:
        pass
    G4 = {"1": dict(b_s=[-1.0, 1, 1]), "0.3": dict(b_s=[1e-3, 1e-3, 1e-3]), "0.1": dict(b_s=[1e-3, 1e-3, 1e-3]),
          "0.03": dict(b_s=[-1.0, 1, 1])}
    ok = ok and NL.pick_alpha(G4) == "0.3"
    return dict(passed=bool(ok))


def p_real():
    r = NL.read_real()
    ok = (abs(r["5"]["median"] - 5.531e-4) < 5e-8 and abs(r["5"]["share"] - 1.0) < 5e-4
          and abs(r["15"]["median"] - 4.136e-4) < 5e-8 and abs(r["15"]["share"] - 0.941) < 5e-4
          and r["5"]["n"] == 17 and r["15"]["n"] == 17)
    return dict(passed=bool(ok))


def p_read():
    rl = lambda U, FA: dict(U=U, FA=FA, L80=1e-2)  # noqa: E731
    real = {"5": dict(median=5e-4, share=1.0), "15": dict(median=4e-4, share=0.94)}
    cases = [
        ({"5": rl(1e-4, 0.0), "15": rl(1e-4, 0.1)}, real, "R1"),
        ({"5": rl(1e-3, 0.0), "15": rl(1e-3, 0.0)}, real, "R2"),
        ({"5": rl(1e-4, 0.0), "15": rl(1e-3, 0.0)}, real, "R3"),
        ({"5": rl(1e-4, 0.0), "15": rl(1e-4, 0.3)}, real, "R3"),
        ({"5": rl(5e-4, 0.0), "15": rl(4e-4, 0.0)}, real, "R2"),                       # 中央値 = U' ちょうどは検出しない
        ({"5": rl(1e-4, 0.0), "15": rl(1e-4, 0.0)}, {"5": dict(median=5e-4, share=0.8),
                                                     "15": dict(median=4e-4, share=0.8)}, "R1"),  # 良 0.8 ちょうどは検出
    ]
    got = [NL.reading(rs, re_)["case"] for rs, re_, _ in cases]
    return dict(passed=got == [c[2] for c in cases], got=got)


def p_smoke():
    g = gate_tiny()
    ok = len(g["b"]) == 4 and all(k in g for k in ("median", "n_neg_inf", "share_pos", "full_diag"))
    r = dict(strand="dose", shape="tiny", K=3, g=0.0, seed=0, no=0)
    R = RS.run_rep(r, {3: {}}, NL.m0s_for_run(fake_m0(), SEED), SEED, JOBS[0])
    R = json.loads(json.dumps(R))
    c = AN.cell(R, "1")
    ok = ok and len(R["writers"]) == 4 and math.isfinite(c["main"]["median"]) and "better_share" in c["main"]
    return dict(passed=bool(ok), seconds=R["seconds"]["total"])


FUNCS = {"P-HASH": p_hash, "P-PLAN": p_plan, "P-M0": p_m0, "P-M0USE": p_m0use, "P-SPARSE": p_sparse, "P-B": p_b,
         "P-PICK": p_pick, "P-REAL": p_real, "P-READ": p_read, "P-SMOKE": p_smoke}


def main():
    argv = sys.argv[1:]
    mut, run_id = [], None
    while "--mutate" in argv:
        i = argv.index("--mutate"); mut.append(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    if "--jobs" in argv:
        i = argv.index("--jobs"); JOBS[0] = int(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    NL.MUT.clear()
    NL.MUT.update(mut)
    S = dict(run_id=run_id, mutate=mut)
    for n in NAMES:
        try:
            S[n] = FUNCS[n]()
        except Exception as e:  # noqa: BLE001  門の中の例外は赤に揃える
            S[n] = dict(passed=False, error="%s: %s" % (type(e).__name__, e))
        print(n, S[n]["passed"], flush=True)
    S["passed"] = all(S[n]["passed"] for n in NAMES)
    with open(argv[0], "w", newline="\n") as f:
        json.dump(S, f, indent=1, default=str)
    return 0 if S["passed"] else 3


if __name__ == "__main__":
    sys.exit(main())
