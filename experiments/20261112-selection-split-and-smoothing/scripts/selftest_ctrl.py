"""対称版の対照と選ばれた τ の門（conditions.md の追記「対称版の対照と選ばれた τ」の「門」・合成だけ）。

使い方: python3 -I selftest_ctrl.py <out.json> [--mutate z1..z5] [--run-id ID]
返り値: 0 = すべて通った・3 = 通らない門がある。
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compute as CP  # noqa: E402
import ctrl as CT  # noqa: E402
import pinned4  # noqa: E402
from pinned4 import H, ml  # noqa: E402

NAMES = ["P-HASH", "P-MODEA", "P-WEIGHT", "P-CTRLCELL", "P-FORM"]
SEED = pinned4.SEED


def unit_of(seq):
    return dict(start=0, seqs=[seq], pflag=[np.ones(len(seq), dtype=bool)], probes=[], probes_all=[])


def p_hash():
    return dict(passed=True, hashes=pinned4.hashes())


def p_modea():
    """合成の書き手 4 人（各 10 単位）: 倍率 1 の最頻値が mode の em_writer の mode.ar3 とビットまで同じ。
    倍率 0.03 の最頻値が、基を 0.03 倍に差し替えた fit_pool_excl の S̄ の mode_of と同じで、倍率 1 とは違う。"""
    rng = np.random.default_rng([SEED, 31])
    A = 0.95 * np.eye(2) + 0.05 * rng.dirichlet(np.ones(2), 2)
    sub = lambda n: np.pad(rng.dirichlet(np.full(4, 3.0), n), ((0, 0), (0, H.NSYM - 4)))  # noqa: E731  記号 0〜3 だけ（最頻値を有限に）
    m = dict(kind="ar", pi=np.ones(2) / 2, A=A / A.sum(1, keepdims=True), H=sub(2),
             C=np.stack([sub(H.NSYM) for _ in range(2)]))
    writers = [[unit_of(s) for s in H.sample(m, [80] * 10, rng)] for _ in range(4)]
    w = 1
    full = {ml.sname(s): ml.fit_pool_full(dict(ds="coauthor", si=ml.SEQ_NO[s], seed=SEED, writers=writers))[0] for s in ml.STRUCTS}
    pools = {}
    for s in ml.STRUCTS:
        pm, sb, _ = ml.fit_pool_excl(dict(ds="coauthor", writers=writers, w=w, start=full[ml.sname(s)]))
        pools[ml.sname(s)] = (pm, sb)
    ks = [k for k in ml.DATASETS["coauthor"]["grid"] if k <= len(writers[w]) - 5]
    res = ml.em_writer(writers[w], 5, ks, pools, np.random.default_rng([SEED + 10, w]))
    f1 = CP.job_full(dict(ds="coauthor", s=CT.AR3, alpha=1.0, seed=SEED, writers=writers))
    mine1 = CT.job_excl_mode(dict(ds="coauthor", w=w, start=f1, alpha=1.0, writers=writers))
    f3 = CP.job_full(dict(ds="coauthor", s=CT.AR3, alpha=0.03, seed=SEED, writers=writers))
    mine3 = CT.job_excl_mode(dict(ds="coauthor", w=w, start=f3, alpha=0.03, writers=writers, sb1=mine1["sb"]))
    orig = H.base_prior
    H.base_prior = lambda kind, K: {k: v * 0.03 for k, v in orig(kind, K).items()}
    try:
        g3 = ml.fit_pool_full(dict(ds="coauthor", si=ml.SEQ_NO[CT.AR3], seed=SEED, writers=writers))[0]
        _, sb3, _ = ml.fit_pool_excl(dict(ds="coauthor", writers=writers, w=w, start=g3))
    finally:
        H.base_prior = orig
    ev = CP.eval_of(writers[w], 5)
    ref3 = ev.ll_zero(H.mode_of("ar", sb3)[0])
    ok1 = CP.same_bits(mine1["mode"], res["mode"]["ar3"]) and CP.same_bits(mine1["ll"], res["pool"]["ar3"])
    ok3 = CP.same_bits(mine3["mode"], ref3) and not CP.same_bits(mine3["mode"], mine1["mode"])
    fin = bool(np.isfinite(mine1["mode"][0]) and np.isfinite(mine3["mode"][0]))  # −∞ どうしでは違いを確かめられない
    return dict(passed=bool(ok1 and ok3 and fin), alpha1=bool(ok1), alpha003=bool(ok3), finite=fin)


def p_weight():
    """手の例: N = {100, 200, 300, 400, 500}、τ = {0, 100, 1000, 1000, ∞} → 中央値 τ = 1000・N の中央値 300・
    重み 300/1300。書き手ごとの重み {1, 2/3, 0.230769…, 0.285714…, 0} の中央値 = 0.285714…。τ の人数 0:1 100:1 1000:2 inf:1。"""
    picks = {0: "0", 1: "100", 2: "1000", 3: "1000", 4: ml.INF}
    nt = {0: 100, 1: 200, 2: 300, 3: 400, 4: 500}
    T = CT.tau_summary(picks, nt)
    ok = T["tau_median"] == 1000.0 and T["n_train_median"] == 300.0
    ok = ok and abs(T["weight_at_medians"] - 300 / 1300) < 1e-12 and abs(T["weight_median_per_writer"] - 400 / 1400) < 1e-12
    ok = ok and T["counts"] == {"0": 1, "100": 1, "1000": 2, "inf": 1}
    ok = ok and CT.weight(10, np.inf) == 0.0 and abs(CT.weight(10, 30) - 0.25) < 1e-15
    return dict(passed=bool(ok))


def p_ctrlcell():
    """手の例（6 人・k = 5）: 共通(0.03) = −1.0 + c_v（c = [0.01, 0.01, 0, 0, 0, 0]）。本人'(10^5) = −0.997、本人'(10^6) = −0.998、
    ほかの有限の τ は −1.002、r1 = −1.1 → 2 段は全員 10^5。最頻値(0.03) = −1.001（書き手 5 だけ −∞）、最頻値(1) = −0.999。
    手の値: 本人' − 最頻値(0.03) = [4e-3 ×5, +∞] → 中央値 4e-3・+∞ 1 人。Rs = [−7e-3, −7e-3, 3e-3 ×4] → 3e-3。
    C03 = [−0.011, −0.011, −1e-3 ×3, −∞]・C1x = [−9e-3, −9e-3, 1e-3 ×4]（中央値は ml.q の規則・inverted_cdf の値）。
    記録する τ が 2 段の選びであること: 乱数の例（書き手 8 人）で、2 段と τ 他人の選びの人数が違う例を探し、記録の人数が
    sym_picks の第 1 要素（2 段）の人数と一致する。"""
    ws = list(range(6))
    c = [0.01, 0.01, 0, 0, 0, 0]
    P03 = {v: [-1.0 + c[v], None] for v in ws}
    S03 = {v: {"5": {t: [-1.002, None] for t in ml.TAU_KEYS}} for v in ws}
    for v in ws:
        S03[v]["5"]["100000"] = [-0.997, None]
        S03[v]["5"]["1000000"] = [-0.998, None]
    R = {v: dict(em=dict(k={"5": dict(r1=[-1.1, None], n_train=1000 + v)})) for v in ws}
    M03 = {v: [-1.001, None] for v in ws}
    M03[5] = [-np.inf, None]
    M1 = {v: [-0.999, None] for v in ws}
    C = CT.ctrl_cell(ws, 5, R, S03, P03, M03, M1, np.random.default_rng(0))
    ctl = CT.controls(ws, P03, M03, M1, np.random.default_rng(0))
    sm = [(-0.997) - (-1.001)] * 5 + [np.inf]
    ok = C["self_minus_mode03"]["n"] == 6 and abs(C["self_minus_mode03"]["median"] - ml.q(sm)["median"]) < 1e-12
    ok = ok and C["self_minus_mode03"]["n_pos_inf"] == 1
    ok = ok and abs(C["rs"]["median"] - ml.q([(-0.997) - P03[v][0] for v in ws])["median"]) < 1e-12
    ok = ok and C["tau"]["counts"] == {"100000": 6}
    ok = ok and ctl["c03"]["n"] == 6 and ctl["c03"]["n_neg_inf"] == 1 and ctl["mode03_neg_inf"] == 1
    ok = ok and abs(ctl["c03"]["median"] - ml.q([M03[v][0] - P03[v][0] for v in ws])["median"]) < 1e-12
    ok = ok and abs(ctl["c1x"]["median"] - ml.q([M1[v][0] - P03[v][0] for v in ws])["median"]) < 1e-12
    rng = np.random.default_rng([SEED, 32])
    ws8 = list(range(8))
    found = False
    for _ in range(2000):
        Rr = {v: dict(em=dict(k={"5": dict(r1=[float(rng.normal()), None], n_train=1000)})) for v in ws8}
        S = {v: {"5": {t: [float(rng.normal()), None] for t in ml.TAU_KEYS}} for v in ws8}
        P = {v: [float(rng.normal()), None] for v in ws8}
        pj, pt = CT.SM.sym_picks(ws8, 5, Rr, S, P)
        cj, ct = CT.Counter(pj.values()), CT.Counter(pt.values())
        if cj != ct:
            M = {v: [float(rng.normal()), None] for v in ws8}
            Cr = CT.ctrl_cell(ws8, 5, Rr, S, P, M, M, np.random.default_rng(0))
            ok = ok and Cr["tau"]["counts"] == {str(k): v for k, v in cj.items()}
            found = True
            break
    return dict(passed=bool(ok and found), found_split_example=found)


def p_form():
    ok = CT.ctrl_form(2e-3, 1e-3, 1e-3) == "上回る"
    ok = ok and CT.ctrl_form(1e-3, 1e-3, 1e-3) == "並ぶ"          # Rs = C03 は上回らない
    ok = ok and CT.ctrl_form(2e-3, 1e-3, 0.0) == "並ぶ"           # 中央値 0 は上回らない
    ok = ok and CT.ctrl_form(1e-3, 1e-3, 0.0) == "及ばない"
    ok = ok and CT.ctrl_form(5e-4, 1e-3, -1e-4) == "及ばない"
    ok = ok and CT.panel_form({"5": "上回る", "15": "上回る"}) == "上回る"
    ok = ok and CT.panel_form({"5": "上回る", "15": "並ぶ"}) == "k で分かれる"
    return dict(passed=bool(ok))


FUNCS = {"P-HASH": p_hash, "P-MODEA": p_modea, "P-WEIGHT": p_weight, "P-CTRLCELL": p_ctrlcell, "P-FORM": p_form}


def main():
    argv = sys.argv[1:]
    mut, run_id = [], None
    while "--mutate" in argv:
        i = argv.index("--mutate"); mut.append(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    CT.MUT.clear()
    CT.MUT.update(mut)
    S = dict(run_id=run_id, mutate=mut)
    for n in NAMES:
        S[n] = FUNCS[n]()
        print(n, S[n]["passed"], flush=True)
    S["passed"] = all(S[n]["passed"] for n in NAMES)
    json.dump(S, open(argv[0], "w", newline="\n"), indent=1, default=str)
    return 0 if S["passed"] else 3


if __name__ == "__main__":
    sys.exit(main())
