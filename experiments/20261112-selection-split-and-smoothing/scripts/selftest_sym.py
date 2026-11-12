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

NAMES = ["P-HASH", "P-REPLAY", "P-REPLAY03", "P-SYMPRIOR", "P-SELW", "P-SYMCELL"]
SEED = pinned4.SEED


def unit_of(seq):
    return dict(start=0, seqs=[seq], pflag=[np.ones(len(seq), dtype=bool)], probes=[], probes_all=[])


def p_hash():
    """記録だけ（ハッシュが違えば pinned4 の import の時点で止まる）。"""
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


def p_replay03():
    """倍率 0.03 の引き直しが、mode の em_writer の基を 0.03 倍に差し替えた独立の参照と同じで、倍率 1 の値とは違う
    （本人に倍率が渡っているか・レビュー MEDIUM 1）。"""
    rng = np.random.default_rng([SEED, 24])
    A = 0.95 * np.eye(2) + 0.05 * rng.dirichlet(np.ones(2), 2)
    m = dict(kind="ar", pi=np.ones(2) / 2, A=A / A.sum(1, keepdims=True), H=rng.dirichlet(np.ones(H.NSYM), 2),
             C=np.stack([rng.dirichlet(np.full(H.NSYM, 0.3), H.NSYM) for _ in range(2)]))
    writers = [[unit_of(s) for s in H.sample(m, [80] * 9, rng)] for _ in range(4)]
    full = {ml.sname(s): ml.fit_pool_full(dict(ds="coauthor", si=ml.SEQ_NO[s], seed=SEED, writers=writers))[0] for s in ml.STRUCTS}
    pools = {}
    for s in ml.STRUCTS:
        pm, sb, _ = ml.fit_pool_excl(dict(ds="coauthor", writers=writers, w=1, start=full[ml.sname(s)]))
        pools[ml.sname(s)] = (pm, sb)
    ks = [k for k in ml.DATASETS["coauthor"]["grid"] if k <= len(writers[1]) - 5]
    orig = H.base_prior
    H.base_prior = lambda kind, K: {k: v * 0.03 for k, v in orig(kind, K).items()}
    try:
        ref = ml.em_writer(writers[1], 5, ks, pools, np.random.default_rng([SEED + 10, 1]))
    finally:
        H.base_prior = orig
    mine = SM.replay_writer(writers[1], 5, ks, [3], pools["ar3"][0], pools["ar3"][1], np.random.default_rng([SEED + 10, 1]), 0.03)
    one = SM.replay_writer(writers[1], 5, ks, [3], pools["ar3"][0], pools["ar3"][1], np.random.default_rng([SEED + 10, 1]), 1.0)
    ts = list(map(str, ml.TAUS_FIT))
    ok = all(mine["3"][t] == ref["k"]["3"]["self"]["ar3"][t] for t in ts) and any(mine["3"][t] != one["3"][t] for t in ts)
    return dict(passed=bool(ok))


def p_symcell():
    """手の例（書き手 6 人・k = 5）: 本人' は有限の τ で共通(0.03) − 1e-3（10^6 だけ +2e-3）、共通(0.03) は −1.0、r1 は −1.1、
    共通(1) は −1.0005。対称 2 段は他の 5 人の 本人' − r1 の中央値で 10^6（+0.102）を選び、本人' − 共通(0.03) = +2e-3、
    本人' − r1 = +0.102、本人' − 共通(1) = +2.5e-3。対称 τ 他人も 10^6（+2e-3 > ∞ の 0）。形: R0 = 1e-3 で「戻る」、
    R0 = 5e-3 で「縮む」、Rs = 0 で「消えたまま」。"""
    ws = list(range(6))
    R = {v: dict(em=dict(pool={"ar3": [-1.0005, None]}, k={"5": dict(r1=[-1.1, None], self={"ar3": {}})})) for v in ws}
    S03 = {v: {"5": {t: [(-1.0 + 2e-3) if t == "1000000" else (-1.0 - 1e-3), None] for t in ml.TAU_KEYS}} for v in ws}
    P03 = {v: [-1.0, None] for v in ws}
    for v in ws:
        R[v]["em"]["k"]["5"]["self"]["ar3"] = {t: [-1.0, None] for t in ml.TAU_KEYS}
    C = SM.sym_cell(ws, 5, R, S03, P03, np.random.default_rng(0))
    j = C["joint"]
    ok = abs(j["self_minus_pool03"]["median"] - 2e-3) < 1e-12 and abs(j["self_minus_r1"]["median"] - 0.102) < 1e-12
    ok = ok and abs(j["self_minus_pool1"]["median"] - 2.5e-3) < 1e-12 and j["chosen_tau_region"]["high_finite_end"] == 6
    ok = ok and abs(C["tau_other"]["self_minus_pool03"]["median"] - 2e-3) < 1e-12
    # ∞ が選ばれる例: 有限の τ をすべて悪くすると 2 段の 本人' − 共通(0.03) はちょうど 0
    S03b = {v: {"5": {t: [-1.5, None] for t in ml.TAU_KEYS}} for v in ws}
    Cb = SM.sym_cell(ws, 5, R, S03b, P03, np.random.default_rng(0))
    ok = ok and Cb["joint"]["self_minus_pool03"]["median"] == 0.0 and Cb["joint"]["chosen_tau_region"]["inf"] == 6
    ok = ok and SM.sym_form(1e-3, 2e-3) == "戻る" and SM.sym_form(5e-3, 2e-3) == "縮む" and SM.sym_form(1e-3, 0.0) == "消えたまま"
    ok = ok and SM.sym_form(4e-3, 2e-3) == "戻る"
    return dict(passed=bool(ok))


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


FUNCS = {"P-HASH": p_hash, "P-REPLAY": p_replay, "P-REPLAY03": p_replay03, "P-SYMPRIOR": p_symprior, "P-SELW": p_selw,
         "P-SYMCELL": p_symcell}


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
