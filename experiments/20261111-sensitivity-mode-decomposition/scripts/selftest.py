"""門（conditions.md V1・合成だけ）。P-HASH は pinned2 の読み込みで止める。

使い方: python3 -I selftest.py <out.json> [--mutate u1..u5] [--jobs N] [--run-id ID]
返り値: 0 = すべて通った・3 = 通らない門がある（変異の門は 3 を赤と読む）。
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decomp as DC  # noqa: E402
import pinned2  # noqa: E402
from pinned2 import HM, SY, ml  # noqa: E402

NAMES = ["P-HASH", "P-ZERO", "P-MODEW", "P-NEGINF", "P-AB", "P-PICK"]
SEED = pinned2.REP_SEED
_TINY = {}


def tiny(jobs):
    """P-RECOVER の形（パネル 8 人 × 20 セッション × 400 記号・共通だけの書き手 0・g* = 0.1・sens の selftest と同じ較正）。"""
    if "r" not in _TINY:
        SY.SHAPES["tiny"] = dict(i=9, ds="coauthor", H=5, P=8, Pu=20, O=0, Ou=0, nseq=1, L=(400, 400), ks=[15])
        m0 = SY.make_m0(3, SEED)
        c = SY.calibrate(m0, 0.1, SEED, n_w=10, L=5000)
        if not c["ok"]:
            raise ValueError("tiny の較正が入らない")
        r = dict(no=99, strand="dose", shape="tiny", K=3, g=0.1, seed=0)
        _TINY["r"] = DC.rebuild(r, {3: {"0.1": c}}, {3: m0, 5: None}, SEED, jobs, want_full_sb=True)
    return _TINY["r"]


def p_hash(jobs):
    return dict(passed=True, hashes=pinned2.hashes())  # 外れれば pinned2 の読み込みで止まっている


def p_zero(jobs):
    """確率 0 の無い母数で、mode_eval が ml.Eval.ll と一致。"""
    m0 = SY.make_m0(3, SEED)
    rng = np.random.default_rng([SEED, 77])
    seqs = [SY.Sampler(m0).seq(rng.random((500, 2))) for _ in range(3)]
    a = DC.mode_eval(m0, seqs)
    b = ml.Eval(seqs, [np.ones(len(s), dtype=bool) for s in seqs]).ll(m0)[0]
    return dict(passed=bool(abs(a - b) < 1e-12), mode_eval=a, eval_ll=b)


def p_modew(jobs):
    """最頻値が w を除く共通の S̄ から作られている（独立に作り直した値と一致）・全員の S̄ とも母数とも違う。"""
    out, _, X = tiny(jobs)
    ml._W[X["ds"]] = X["writers"]
    same_direct, diff_full, diff_pool = True, 0, 0
    for w in range(X["P"]):
        units = X["writers"][w]
        _, test = pinned2.DT.split(len(units), 1, X["H"])
        ev_seqs = ml.seqs_of([units[i] for i in test])
        for si, s in enumerate(ml.STRUCTS):
            name = ml.sname(s)
            if w < 2:  # 独立の照らし（2 人 × 4 構造）
                m, sb, _ = ml.fit_pool_excl(dict(ds=X["ds"], w=w, start=X["full"][si]))
                direct = DC.mode_eval(HM.mode_of(s[0], sb)[0], ev_seqs)
                same_direct = same_direct and direct == out[w]["mode"][name]
            diff_full += out[w]["mode"][name] != out[w]["mode_full_sb"][name]
            diff_pool += out[w]["mode"][name] != out[w]["pool"][name]
    return dict(passed=bool(same_direct and diff_full > 0 and diff_pool > 0), same_direct=same_direct,
                diff_full=int(diff_full), diff_pool=int(diff_pool))


def p_neginf(jobs):
    """確率 0 のセルを持つ最頻値で −∞（NaN でない）・a = +∞・b = −∞・±∞ の人数・NaN が無い。"""
    m0 = SY.make_m0(3, SEED)
    m = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in m0.items()}
    m["C"][:, 0, 1] = 0.0  # 記号 0 → 1 の遷移の確率を 0 に（行を足し直す）
    m["C"][:, 0, :] /= m["C"][:, 0, :].sum(-1, keepdims=True)
    seqs_hit = [np.array([0, 1, 2, 3] * 50)]
    seqs_ok = [np.array([2, 3, 4, 5] * 50)]
    try:
        v_hit = DC.mode_eval(m, seqs_hit)
        v_ok = DC.mode_eval(m, seqs_ok)
    except ValueError as e:
        return dict(passed=False, note=str(e))
    trip = [DC.abc(-1.0, v_hit, -1.1), DC.abc(-1.0, v_ok, -1.1), DC.abc(-1.0, -1.05, -1.1), DC.abc(-1.2, -1.15, -1.1)]
    try:
        R = DC.row_stats(trip)
    except ValueError as e:
        return dict(passed=False, note=str(e))
    import run_decomp as RD
    rt = RD.dec(json.loads(json.dumps(RD.enc(dict(m=v_hit, t=list(trip[0]))), allow_nan=False)))
    ok = (rt["m"] == -np.inf and rt["t"][0] == np.inf and rt["t"][1] == -np.inf
          and v_hit == -np.inf and np.isfinite(v_ok) and trip[0][0] == np.inf and trip[0][1] == -np.inf
          and R["a"]["pos_inf"] == 1 and R["b"]["neg_inf"] == 1 and R["a"]["n"] == 4 and R["finite"]["n"] == 3)
    return dict(passed=bool(ok), v_hit=str(v_hit), v_ok=v_ok, a=R["a"], b=R["b"])


def p_ab(jobs):
    """有限の書き手ごとに a + b = c（作り直しの tiny の値と、でたらめな本人の値で）。"""
    out, _, X = tiny(jobs)
    rng = np.random.default_rng([SEED, 78])
    trip = []
    for w in range(X["P"]):
        for s in ("ar1", "ar3"):
            sv = out[w]["pool"][s] + float(rng.normal() * 1e-3)
            trip.append(DC.abc(sv, out[w]["mode"][s], out[w]["pool"][s]))
    R = DC.row_stats(trip)
    V = R["values"]
    ok = all(abs(a + b - c) < 1e-12 for a, b, c in zip(V["a"], V["b"], V["c"]) if np.isfinite(b))
    return dict(passed=bool(ok), n=len(trip))


def p_pick(jobs):
    """2 段の選びに w の値を書き換えて渡しても w の選びが変わらない（乱数 200 回）。"""
    rng = np.random.default_rng([SEED, 79])
    flips = 0
    for _ in range(200):
        W = [dict(k={"5": dict(r1=0.0, self={s: {t: float(rng.normal()) for t in ml.TAU_KEYS} for s in DC.SNAMES})})
             for _ in range(6)]
        a = DC.pick_joint(W, "5")[0]
        W[0]["k"]["5"]["self"] = {s: {t: float(rng.normal() * 10) for t in ml.TAU_KEYS} for s in DC.SNAMES}
        flips += a != DC.pick_joint(W, "5")[0]
    return dict(passed=flips == 0, flips=flips)


FUNCS = {"P-HASH": p_hash, "P-ZERO": p_zero, "P-MODEW": p_modew, "P-NEGINF": p_neginf, "P-AB": p_ab, "P-PICK": p_pick}


def main():
    argv = sys.argv[1:]
    mut, run_id, jobs = [], None, 8
    while "--mutate" in argv:
        i = argv.index("--mutate"); mut.append(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    if "--jobs" in argv:
        i = argv.index("--jobs"); jobs = int(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    out = argv[0]
    DC.MUT.clear()
    DC.MUT.update(mut)
    S = dict(run_id=run_id, mutate=mut)
    t0 = time.time()
    for n in NAMES:
        t = time.time()
        try:  # 門の中の例外は赤（exit 3）に揃える（レビュー MEDIUM 5）
            S[n] = FUNCS[n](jobs)
        except Exception as e:  # noqa: BLE001
            S[n] = dict(passed=False, note="例外: %s: %s" % (type(e).__name__, e))
        S[n]["seconds"] = time.time() - t
        print(n, S[n]["passed"], flush=True)
    S["seconds"] = time.time() - t0
    S["passed"] = all(S[n]["passed"] for n in NAMES)
    json.dump(S, open(out, "w"), indent=1, default=str)
    return 0 if S["passed"] else 3


if __name__ == "__main__":
    sys.exit(main())
