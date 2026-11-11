"""門（conditions.md V1・合成の書き手の値だけ・当てはめは無い）。P-HASH は pinned3 の読み込みで止める。

使い方: python3 -I selftest.py <out.json> [--mutate n1..n4] [--run-id ID]
返り値: 0 = すべて通った・3 = 通らない門がある。
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinned3  # noqa: E402
import sel as SL  # noqa: E402
from pinned3 import ml  # noqa: E402

NAMES = ["P-HASH", "P-OLDSAME", "P-MODECAND", "P-ZEROCOL", "P-ORDER", "P-NEGINF"]
SEED = pinned3.SEED
SN = [ml.sname(s) for s in ml.STRUCTS]
KS = ["1", "2", "3", "5"]


def fake_results(rng, n_w=8, mode_neg=()):
    """CS1 の形（C5: n ≥ 6・k = 1, 2, 3, 5）の合成の書き手の値。全記号と押下のある記号。"""
    R = {}
    for w in range(n_w):
        pool = {s: [float(-1.2 + 0.01 * rng.normal()), float(-1.3 + 0.01 * rng.normal())] for s in SN}
        mode = {s: ([-np.inf, -np.inf] if w in mode_neg else [pool[s][0] + float(1e-3 * rng.normal()),
                                                              pool[s][1] + float(1e-3 * rng.normal())]) for s in SN}
        k = {}
        for kk in KS:
            self_ = {s: {t: ([pool[s][0], pool[s][1]] if t == ml.INF else
                             [pool[s][0] + float(1e-3 * rng.normal()), pool[s][1] + float(1e-3 * rng.normal())])
                         for t in ml.TAU_KEYS} for s in SN}
            k[kk] = dict(r1=[-1.25 + float(0.01 * rng.normal()), -1.35], self=self_)
        R[w] = dict(n=6, em=dict(pool=pool, mode=mode, k=k))
    return R


def p_hash():
    return dict(passed=True, hashes=pinned3.hashes())


def p_oldsame():
    """最頻値を除いた並べが mode の候補と同じ・選びが mode の select_other / select_joint と同じ（乱数 200 回）。"""
    ok_c = ([t for t in SL.tau_cands_mode() if t != SL.MODE] == ml.tau_cands()
            and [c for c in SL.joint_cands_mode() if c[1] != SL.MODE] == ml.joint_cands())
    rng = np.random.default_rng([SEED, 1])
    diff = 0
    tc, jc = ml.tau_cands(), ml.joint_cands()
    for _ in range(200):
        tv = {v: {t: float(rng.normal()) for t in tc} for v in range(7)}
        jv = {v: {c: float(rng.normal()) for c in jc} for v in range(7)}
        diff += SL._select(tv, 0, tc) != ml.select_other(tv, 0, tc)
        diff += SL._select(jv, 0, jc) != ml.select_joint(jv, 0, jc)
    return dict(passed=bool(ok_c and diff == 0), cands_same=ok_c, diff=diff)


def p_modecand():
    """他の書き手の最頻値がとても良いと w に最頻値が選ばれ、w 自身の値を書き換えても w の選びは変わらない。"""
    rng = np.random.default_rng([SEED, 2])
    jc = SL.joint_cands_mode()
    jv = {v: {c: (10.0 if (c[1] == SL.MODE and v != 0) else float(rng.normal())) for c in jc} for v in range(6)}
    made = SL._select(jv, 0, jc)
    made_ok = made is not None and made[1] == SL.MODE
    flips = 0
    for _ in range(200):
        vals = {v: {c: float(rng.normal()) for c in jc} for v in range(6)}
        a = SL._select(vals, 0, jc)
        vals[0] = {c: float(rng.normal() * 10) for c in jc}
        flips += a != SL._select(vals, 0, jc)
    return dict(passed=bool(made_ok and flips == 0), made=list(made) if made else None, flips=flips)


def p_zerocol():
    """最頻値が選ばれた書き手の 本人 − 最頻値 がちょうど 0、∞ が選ばれた書き手の 本人 − 共通 がちょうど 0。"""
    R = fake_results(np.random.default_rng([SEED, 3]))
    ws = sorted(R)
    pick = {w: ("ar3", SL.MODE if w % 2 == 0 else ml.INF) for w in ws}
    ok = True
    for j in (0, 1):
        dm = SL.deltas(R, ws, "5", pick, j, "mode_same")
        dp = SL.deltas(R, ws, "5", pick, j, "pool_same")
        ok = ok and all(dm[i] == 0.0 for i, w in enumerate(ws) if w % 2 == 0)
        ok = ok and all(dp[i] == 0.0 for i, w in enumerate(ws) if w % 2 == 1)
    return dict(passed=bool(ok))


def p_order():
    """同点: ∞ → 最頻値 → 10^6 の順に選ばれる。"""
    jc = SL.joint_cands_mode()
    flat = {v: {c: 0.0 for c in jc} for v in range(4)}
    a = SL._select(flat, 0, jc)
    no_inf = {v: {c: (None if c[1] == ml.INF else 0.0) for c in jc} for v in range(4)}
    b = SL._select(no_inf, 0, jc)
    no_mode = {v: {c: (None if c[1] in (ml.INF, SL.MODE) else 0.0) for c in jc} for v in range(4)}
    c = SL._select(no_mode, 0, jc)
    ok = a[1] == ml.INF and b[1] == SL.MODE and c[1] == "1000000"
    tc = SL.tau_cands_mode()
    ok = ok and tc[0] == ml.INF and tc[1] == SL.MODE and tc[2] == "1000000"
    return dict(passed=bool(ok), picks=[list(a), list(b), list(c)])


def p_neginf():
    """最頻値が −∞ の書き手を含む合成で、選びが手の答えどおり・NaN が出ない・±∞ の人数が手の数と一致。"""
    rng = np.random.default_rng([SEED, 4])
    R = fake_results(rng, n_w=8, mode_neg=(1, 2, 3, 4))
    ws = sorted(R)
    jc = SL.joint_cands_mode()
    # 他の書き手の値: 最頻値の行は +1（−∞ の 4 人は −∞）、ほかは 0 → w = 0 では 7 人中 4 人が −∞ なので中央値は −∞、∞ が選ばれる
    jv = {v: {c: ((-np.inf if v in (1, 2, 3, 4) else 1.0) if c[1] == SL.MODE else 0.0) for c in jc} for v in ws}
    pick0 = SL._select(jv, 0, jc)
    ok = pick0 is not None and pick0[1] == ml.INF
    pick = {w: ("ar3", SL.MODE) for w in ws}
    try:
        st = SL.row_stats(R, ws, "5", pick, np.random.default_rng([SEED, 5]))
        json.dumps(ml.enc(st), allow_nan=False)
    except ValueError as e:
        return dict(passed=False, note=str(e))
    s_pool = st["all/self_minus_pool_same"]
    s_r1 = st["all/self_minus_r1"]
    ok = ok and s_pool["n_neg_inf"] == 4 and s_r1["n_neg_inf"] == 4 and st["all/self_minus_mode_same"]["n_neg_inf"] == 0
    return dict(passed=bool(ok), pick0=list(pick0) if pick0 else None, neg_inf=s_pool["n_neg_inf"])


FUNCS = {"P-HASH": p_hash, "P-OLDSAME": p_oldsame, "P-MODECAND": p_modecand, "P-ZEROCOL": p_zerocol,
         "P-ORDER": p_order, "P-NEGINF": p_neginf}


def main():
    argv = sys.argv[1:]
    mut, run_id = [], None
    while "--mutate" in argv:
        i = argv.index("--mutate"); mut.append(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    SL.MUT.clear()
    SL.MUT.update(mut)
    S = dict(run_id=run_id, mutate=mut)
    for n in NAMES:
        S[n] = FUNCS[n]()
        print(n, S[n]["passed"], flush=True)
    S["passed"] = all(S[n]["passed"] for n in NAMES)
    json.dump(S, open(argv[0], "w"), indent=1, default=str)
    return 0 if S["passed"] else 3


if __name__ == "__main__":
    sys.exit(main())
