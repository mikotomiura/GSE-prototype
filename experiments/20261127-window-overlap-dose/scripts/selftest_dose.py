"""この試験で足す陽性対照（合成のデータだけ・conditions V2）。S13 と tau-extend の対照は、それぞれの selftest をそのまま回す（run.sh）。

使い方: python3 -I selftest_dose.py <seed> <out.json> [--mutate mX] [--only NAME,...] [--run-id ID] [--jobs N]
返り値: 0 = すべて通った・3 = 通らない対照がある（変異の門は 3 を「赤」と読む）。例外は Python の既定（1）。
P-MI の ±3%・±0.02 は配管の対照の通る条件で、実データの読みの区切りではない。
"""
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import swap  # noqa: E402,F401
from swap import F, load_dose as LD, masks as MK  # noqa: E402
from pinned import DT, H, ml  # noqa: E402
import extra as EX  # noqa: E402
import readings as RD  # noqa: E402
import synth_work as SW  # noqa: E402

NAMES = ["P-STRIDE", "P-BLOCK", "P-PHASE", "P-TIME", "P-MI", "P-DS", "P-FIRST", "P-PAIR", "P-SWAP", "P-READ"]
JOBS = 2


def set_mut(mut):
    LD.set_mut(mut)
    EX.set_mut(mut)
    RD.set_mut(mut)


# ---------------------------------------------------------------- 行の選び
def gappy_series(seed):
    """時刻に抜けのある系列（間引きを時刻で行うか行の番号で行うかを分ける）と、抜けの無い系列。"""
    rng = np.random.default_rng([seed, 61])
    out = []
    for s0, n in ((5_000, 400), (1_000_500, 300), (7_777_000, 25), (3_000_000, 61), (9_000_000, 1)):
        t = s0 + 1000 * np.arange(n)
        if n > 30:
            drop = rng.choice(np.arange(1, n), size=n // 10, replace=False)
            t = np.delete(t, drop)
        out.append([int(x) for x in t])
    out.append([int(x) for x in 4_000_000 + 1000 * np.arange(97)])
    return out


def p_stride(seed):
    series = gappy_series(seed)
    kit = MK.kit_variants()
    n, bad = 0, 0
    for s in MK.STRIDES:
        for t, m in zip(series, MK.series_masks_a(series, s)):
            exp = [True] * len(t) if s == 1 else kit.thinned_mask(list(t), step_ms=1000 * s)
            n += 1
            bad += int(list(m) != list(exp))
    return dict(passed=n > 0 and bad == 0, series_checked=n, mismatched=bad)


def p_block(seed):
    rng = np.random.default_rng([seed, 70])
    series = [[int(x) for x in 2_000_000 * j + 1000 * np.arange(int(rng.integers(31, 700)))] for j in range(12)]
    series.append([int(x) for x in 1000 * np.arange(30)])  # n_A = 0 の系列（s = 30）
    n, bad = 0, 0
    for arm, frac in (("C", 2), ("P1", 4), ("P3", None)):
        for s in (5, 10, 15, 30):
            col = ("%s%d" if arm == "C" else "%s-%d") % (arm, s)
            rows = LD.series_rows(series, col)
            for t, rr in zip(series, rows):
                n += 1
                L = len(t)
                nA = sum(MK.mask_a(t, s))
                r = rr[0]
                free = L - nA
                st = {"C": free // 2, "P1": free // 4, "P3": (3 * free) // 4}[arm]
                ok = len(rr) == 1 and len(r) == nA and all(0 <= i < L for i in r)
                if nA:
                    ok = ok and r[0] == st and list(r) == list(range(st, st + nA))
                bad += int(not ok)
    return dict(passed=n > 0 and bad == 0, series_checked=n, mismatched=bad)


def p_phase(seed):
    series = gappy_series(seed)
    n, bad = 0, 0
    for s in (5, 10, 15, 30):
        ph = MK.series_phases_b(series, s)
        ma = MK.series_masks_a(series, s)
        for t, p, m in zip(series, ph, ma):
            n += 1
            flat = [i for r in p for i in r]
            want = [i for i, x in enumerate(t) if x - t[0] >= 1000 * s and (x - t[0]) % 1000 == 0]
            ok = len(p) == s and len(flat) == len(set(flat)) and sorted(flat) == want and all(0 <= i < len(t) for i in flat)
            ok = ok and p[0] == [i for i, v in enumerate(m) if v]
            bad += int(not ok)
    return dict(passed=n > 0 and bad == 0, series_checked=n, mismatched=bad)


def p_time(seed):
    """時刻の差が 1,000 ms でない所のある合成の入力で読み込みが止まり、ない入力では止まらない。"""
    with tempfile.TemporaryDirectory() as td:
        co, side = SW.make(os.path.join(td, "bad"), seed, n_w=2, n_u=6, lengths=(40, 60), gap_at=(1, 3))
        try:
            LD.load_u_and_times(co, side, seed)
            stopped = False
        except SystemExit:
            stopped = True
        co2, side2 = SW.make(os.path.join(td, "good"), seed, n_w=2, n_u=6, lengths=(40, 60))
        try:
            LD.load_u_and_times(co2, side2, seed)
            clean_ok = True
        except SystemExit:
            clean_ok = False
    return dict(passed=stopped and clean_ok, gap_input_stopped=stopped, clean_input_loaded=clean_ok)


# ---------------------------------------------------------------- M
def markov(rng, n, T, pi):
    s = np.empty(n, dtype=np.int64)
    s[0] = rng.choice(26, p=pi)
    cum = np.cumsum(T, 1)
    u = rng.random(n)
    for i in range(1, n):
        s[i] = min(int(np.searchsorted(cum[s[i - 1]], u[i], side="right")), 25)
    return s


def true_mi(T, pi):
    return float(sum(pi[a] * T[a, b] * math.log(T[a, b] / pi[b]) for a in range(26) for b in range(26) if T[a, b] > 0))


def ref_shuf_mean(seqs, seed, c, w):
    """M_shuf の参照: 20 回の並べ替え（系列ごと・乱数 [SEED + 61, c, w, r]）の Miller–Madow の平均を独立に作る。"""
    vals = []
    for r in range(20):
        rng = np.random.default_rng([seed + 61, c, w, r])
        sh = [rng.permutation(np.asarray(s, dtype=np.int64)) for s in seqs]
        a = np.concatenate([x[:-1] for x in sh])
        b = np.concatenate([x[1:] for x in sh])
        J = np.bincount(a * 26 + b, minlength=676).reshape(26, 26).astype(float)
        N = len(a)
        pa, pb = J.sum(1) / N, J.sum(0) / N
        ii, jj = np.nonzero(J)
        pj = J[ii, jj] / N
        mm = float(np.sum(pj * np.log(pj / (pa[ii] * pb[jj])))) - (len(ii) - (pa > 0).sum() - (pb > 0).sum() + 1) / (2 * N)
        vals.append(mm)
    return float(np.mean(vals))


def p_mi(seed):
    rng = np.random.default_rng([seed, 65])
    T = 0.6 * np.eye(26) + 0.4 / 26
    pi = np.full(26, 1 / 26)
    tm = true_mi(T, pi)
    long = markov(rng, 20_001, T, pi)
    a = EX.mi_mm([long])
    a_ok = tm >= 0.5 and a is not None and abs(a["mm"] - tm) <= 0.03 * tm and a["pairs"] == 20_000
    c = 99
    meds = {}
    for kind in ("indep", "markov", "mixture"):
        diffs, Ms = [], []
        for w in range(20):
            seqs = []
            for j in range(30):
                if kind == "indep":
                    seqs.append(rng.integers(0, 26, 23))
                elif kind == "markov":
                    seqs.append(markov(rng, 23, T, pi))
                else:
                    p = rng.dirichlet(np.full(26, 0.3))
                    seqs.append(rng.choice(26, size=23, p=p))
            r = EX.m_record(seqs, seed, c, w)
            diffs.append(r["M_diff"])
            Ms.append(r["M"])
        meds[kind] = dict(M_diff_median=float(np.median(diffs)), M_median=float(np.median(Ms)))
    b_ok = abs(meds["indep"]["M_diff_median"]) <= 0.02 and meds["markov"]["M_diff_median"] > 0
    mix_ok = meds["mixture"]["M_median"] > 0.02 and abs(meds["mixture"]["M_diff_median"]) <= 0.02
    # 手で作った組: [[0, 1], [0, 1]] は組 2・plug-in 0・補正 0（境目をまたぐ組と全記号の周辺を分ける）
    h = EX.mi_mm([np.array([0, 1]), np.array([0, 1])])
    hand_ok = h is not None and h["pairs"] == 2 and h["plugin"] == 0.0 and h["mm"] == 0.0
    # 20 回の平均（参照と一致）
    seqs = [rng.integers(0, 26, 23) for _ in range(30)]
    ms, sd, vals = EX.m_shuf(seqs, seed, c, 5)
    shuf_ok = len(vals) == 20 and ms is not None and abs(ms - ref_shuf_mean(seqs, seed, c, 5)) <= 1e-12
    return dict(passed=bool(a_ok and b_ok and mix_ok and hand_ok and shuf_ok), true_mi=tm, long_mm=a and a["mm"],
                long_ok=bool(a_ok), short=meds, short_ok=bool(b_ok), mixture_ok=bool(mix_ok), hand_ok=bool(hand_ok),
                shuffle_mean_of_20_ok=bool(shuf_ok))


# ---------------------------------------------------------------- 当てはめを使う対照の合成
def synth(seed, tag, n_w, n_u, L_):
    rng = np.random.default_rng([seed, tag])
    cm = H.random_model("hmm", 3, rng)
    cm["A"] = 0.9 * np.eye(3) + 0.1 * cm["A"]
    writers = [[dict(start=0, seqs=[s], pflag=[rng.random(len(s)) < 0.7], probes=[], probes_all=[])
                for s in H.sample(cm, [L_] * n_u, rng)] for _ in range(n_w)]

    def pools_from(tag2):
        r2 = np.random.default_rng([seed, tag, tag2])
        pool = H.sample(cm, [400] * 10, r2)
        _, hp, Tp = H.r0_r1(pool)
        Dp = H.Data(pool, chunk=H.CHUNK)
        out = {}
        for s in ml.STRUCTS:
            m = H.random_model(s[0], s[1], r2, r1=Tp, r0=hp)
            S, _ = H.counts(m, Dp)
            out[ml.sname(s)] = (m, H.sbar_of(S, Dp.nobs))
        return out
    return writers, pools_from(0), pools_from(1)


def p_ds(seed):
    writers, pools, other = synth(seed, 72, 2, 7, 160)
    full = {k: v[0] for k, v in other.items()}  # 「全員の共有」の代わり（w を除く共有と違う母数）
    Hh, ks = 5, [1, 2]
    n, bad = 0, 0
    with tempfile.TemporaryDirectory() as td:
        flat, outs = {}, []
        for w, units in enumerate(writers):
            res, par = F.fit_writer(units, Hh, ks, ks, pools, np.random.default_rng([seed + 10, w]))
            outs.append(res)
            flat.update(F.flat_params(w, par))
        p = os.path.join(td, "p.npz")
        np.savez_compressed(p, **flat)
        with np.load(p) as z:
            for w, units in enumerate(writers):
                _, test = DT.split(len(units), 1, Hh)
                te = [units[i] for i in test]
                ev = ml.Eval(ml.seqs_of(te), ml.pflags_of(te))
                exp = ev.ll(pools["ar1"][0])[0] - ev.ll(pools["hmm3"][0])[0]
                leaf, rb = EX.ds_leaf(outs[w]), EX.ds_readback(ev, z, w, full=full)
                n += 1
                bad += int(not (leaf == rb == exp))
    return dict(passed=n > 0 and bad == 0, writers=n, mismatched=bad)


def p_first(seed):
    writers, pools, _ = synth(seed, 67, 1, 6, 120)
    rng = np.random.default_rng([seed, 67, 9])
    seqs = [np.asarray(s) for s in H.sample(pools["hmm3"][0], [40, 1, 77, 13], rng)]
    ev = ml.Eval(seqs, [np.ones(len(s), dtype=bool) for s in seqs])
    n, bad = 0, 0
    _, h, T = H.r0_r1(seqs)
    for lp in (H.pred_logprob(pools["hmm3"][0], ev.D), H.pred_logprob(pools["ar2"][0], ev.D), EX.lp_r1(ev, h, T)):
        s, cnt = EX.nohead(ev, lp)
        M = ev.D.M
        head = M & (ev.D.P < 0)
        exact = sum(Fraction(float(x)) for x in lp[M]) - sum(Fraction(float(x)) for x in lp[head])
        n += 1
        bad += int(not (s == float(exact) and cnt == int(M.sum()) - len(seqs) and int(head.sum()) == len(seqs)))
    return dict(passed=n > 0 and bad == 0, scorers=n, mismatched=bad)


# ---------------------------------------------------------------- 対応のある差
def p_pair(seed):
    cols = ["A1", "A5", "A10", "A15", "A30", "C5", "C10", "C15", "C30"]
    G = {c: {} for c in cols}
    rng = np.random.default_rng([seed, 74])
    for w in range(13):
        base = float(rng.normal(0.1, 0.05))
        for c in cols:
            G[c][str(w)] = base + float(rng.normal(0, 0.03))
    for c in cols:  # 14 人目は C30 だけ欠け、ほかの列には極端な値
        if c != "C30":
            G[c]["13"] = 5.0 if c.startswith("C") else -5.0
    ws = RD.common(G, cols)
    want = ws is not None and sorted(ws, key=int) == [str(w) for w in range(13)]
    exp = float(np.quantile([G["C5"][str(w)] - G["A5"][str(w)] for w in range(13)], 0.5, method="inverted_cdf"))
    got = RD.paired(G, "C5", "A5", ws)
    dom = float(np.quantile([G["C5"][str(w)] for w in range(13)], 0.5, method="inverted_cdf")) - float(
        np.quantile([G["A5"][str(w)] for w in range(13)], 0.5, method="inverted_cdf"))
    ok = bool(want) and got == exp and abs(dom - exp) > 1e-6
    # 共通の集合が 12 人未満なら「欠けがある」（列ごとには 12 人以上）
    G2 = {c: {} for c in cols}
    for w in range(16):
        for c in cols:
            G2[c][str(w)] = 0.1
    for j, c in enumerate(cols):  # 列ごとに別の 1 人を欠く → 共通は 16 − 9 = 7 人、列ごとは 15 人
        del G2[c][str(j)]
    word, det = RD.g_word(G2)
    ok2 = word == "欠けがある"
    return dict(passed=bool(ok and ok2), common_ok=bool(want), paired_ok=bool(got == exp), missing_word=word)


# ---------------------------------------------------------------- 差し替え
def run_sub(args, env=None):
    return subprocess.run([sys.executable, "-I", "-X", "utf8"] + args, capture_output=True, text=True,
                          env=dict(os.environ, **(env or {})))


def p_swap(seed, mut):
    with tempfile.TemporaryDirectory() as td:
        co, side = SW.make(td, seed, n_w=3, n_u=21, lengths=(90, 200), tag=68)
        S13 = os.path.dirname(F.__file__)
        outs = {}
        env = {"DOSE_MUT": ",".join(m for m in mut if m in ("m68",))}
        for name, args in (("drive_A1", [os.path.join(HERE, "drive.py"), "fit", "A1"]),
                           ("direct_u", [os.path.join(S13, "fit.py"), "coauthor", "u"]),
                           ("drive_A5", [os.path.join(HERE, "drive.py"), "fit", "A5"])):
            raw = os.path.join(td, "raw_" + name)
            os.makedirs(raw)
            r = run_sub(args + [co, side, str(seed), os.path.join(td, "res_" + name), raw, str(JOBS), "--run-id", "swap"],
                        env=env if name.startswith("drive") else None)
            if r.returncode != 0:
                return dict(passed=False, note="%s が走らない" % name, stderr=r.stderr[-2000:])
            col = args[-1]
            outs[name] = json.load(open(os.path.join(raw, "unsmoothed_residual_writer_values.coauthor.%s.json" % col)))
        a, b = outs["drive_A1"], outs["direct_u"]
        cells, diff = 0, 0
        for w in b["panel"]:
            ra, rb = a["results"][str(w)]["em"], b["results"][str(w)]["em"]
            cells += 2
            diff += int(ra["pool"] != rb["pool"]) + int(ra["n_eval"] != rb["n_eval"])
            for k, kb in rb["k"].items():
                ka = ra["k"].get(k)
                cells += 1
                if kb is None or ka is None:
                    diff += int(ka != kb)
                    continue
                for f in ("r1", "self", "diag", "n_train"):
                    cells += 1
                    diff += int(ka[f] != kb[f])
        same_panel = a["panel"] == b["panel"]
        # 子のプロセスにも差し替えが効いているか: 列 A5 の評価の記号の数が、この場で読んだ列 A5 の数と一致する
        LD.set_mut([m for m in mut if m in ("m68",)])
        wr = LD.load_column("coauthor", co, side, seed, "A5")
        LD.set_mut(mut)
        ns = [len(x) for x in wr]
        elig = [i for i, n in enumerate(ns) if n >= 6]
        a5 = outs["drive_A5"]
        n5 = all(a5["results"][str(w)]["em"]["n_eval"] == sum(len(s) for i in DT.split(len(wr[elig[w]]), 1, 5)[1]
                                                               for s in wr[elig[w]][i]["seqs"]) for w in a5["panel"])
        n5_differs_from_u = any(a5["results"][str(w)]["em"]["n_eval"] != b["results"][str(w)]["em"]["n_eval"] for w in a5["panel"])
    return dict(passed=bool(cells > 0 and diff == 0 and same_panel and n5 and n5_differs_from_u), cells=cells, differing=diff,
                same_panel=bool(same_panel), child_swap_A5=bool(n5), A5_differs_from_u=bool(n5_differs_from_u))


# ---------------------------------------------------------------- 読み
PH2_LONG = "(window overlap, prediction horizon and time covered by the same number of symbols, not separated)"
PH2_SHORT = "the step's components not separated"


def ph1(s):
    return "nsmoothed symbols" in s


def ph2(s):
    return PH2_LONG in s or PH2_SHORT in s


def ph3(s):
    return "did not carry the same independent information" in s or "not carrying the same independent information" in s


OFFS = [(j - 8) / 64.0 for j in range(17)]  # 17 人の書き手のずれ（2 進の数で差がちょうど出る）


def mkcell(levels, offs=OFFS):
    """levels: {列: 値}。書き手 w の値 = 値 + ずれ[w]（全列で同じずれ → 対応のある差は列の値の差にちょうど等しい）。"""
    return {c: {str(w): v + o for w, o in enumerate(offs)} for c, v in levels.items()}


def gl(a1, a30, c=None, cprime=None):
    """G の列の値: A は 1〜30 を直線で、C は c(s, A_s)、C′ は cprime（無ければ C と同じ）。"""
    L = {"A1": a1}
    for s in RD.STEPS:
        L["A%d" % s] = a1 - (a1 - a30) * (s - 1) / 29.0
    for s in RD.STEPS:
        L["C%d" % s] = c(s, L["A%d" % s]) if c else L["A%d" % s]
        L["P1-%d" % s] = L["P3-%d" % s] = (cprime(s, L["A%d" % s]) if cprime else L["C%d" % s])
    return L


def mkV(g5, g15, mdiff=None, c2a=None, r1p=None, nohead=None, t10000=None, ds=None):
    cols = ["A1"] + ["%s%d" % (p, s) for p in ("A", "C") for s in RD.STEPS]
    md = mdiff or dict({"A1": 0.08, "A5": 0.06, "A10": 0.04, "A15": 0.03, "A30": 0.01},
                       **{"C%d" % s: 0.09 for s in RD.STEPS})
    dsv = ds or {c: (0.2 if c.startswith("C") else 0.1) for c in cols}
    c2 = c2a or {c: (-0.5 if c in ("A1",) else 0.2) for c in list(g5)}
    rp = r1p or {c: -0.1 for c in list(g5)}
    V = dict(cells={}, constr=dict(M_diff=mkcell(md), D_s=mkcell(dsv), rho_x=mkcell(dsv), rho_y=mkcell(dsv)))
    for k, g in (("5", g5), ("15", g15)):
        V["cells"][k] = dict(G=mkcell(g), C2a=mkcell(c2), R1P=mkcell(rp), G_nohead=mkcell(nohead[k] if nohead else g),
                             G_t10000=mkcell(t10000[k] if t10000 else g))
    V["desc"] = dict(stretch_C30_sec=22.0,
                     w_ar3={c: {"5": 0.01, "15": 0.02} for c in ("A30", "C30")},
                     w_ar3_t10000={c: {"5": 0.002, "15": 0.004} for c in ("A30", "C30")},
                     w_hmm3={c: {"5": 0.3, "15": 0.4} for c in ("A30", "C30")},
                     resid_diff={c: {"5": dict(x=0.01, y=-0.02), "15": dict(x=0.0, y=0.03)} for c in ("A1", "C30")})
    return V


def dy(a1, a30, c=None, **kw):
    return gl(a1, a30, c, **kw)


def p_read(seed):
    chk = {}
    step_only = lambda s, a: None  # noqa: E731
    # 開示の端の値に「歩みだけが効く」（G_Cs = G_A1）・「記号の数だけが効く」（G_Cs = G_As）・「比が大きい」を置く
    g5s = gl(0.140, 0.043, lambda s, a: 0.140)
    g15s = gl(0.155, 0.096, lambda s, a: 0.155)
    R = RD.assemble(mkV(g5s, g15s), seed, ml)
    chk["edge_step_only"] = R["word"] == "列 C では縮みが小さい" and R["type"] == "1"
    R2 = RD.assemble(mkV(gl(0.140, 0.043), gl(0.155, 0.096)), seed, ml)
    chk["edge_count_only"] = R2["word"] == "列 C でも同じ程度に縮む" and R2["type"] == "2"
    big = lambda a1: (lambda s, a: a1 + 0.3 if s == 30 else a)  # noqa: E731
    R3 = RD.assemble(mkV(gl(0.140, 0.043, big(0.140)), gl(0.155, 0.096, big(0.155))), seed, ml)
    chk["edge_ratio_big"] = R3["word"] == "比が 1.5 を超える" and R3["type"] == "なし"
    # 作りの確かめが全部の列で負 → 外れ（正の条件を外す m79 では型が付いてしまう値の組）
    neg = dict({"A1": -0.01, "A5": -0.02, "A10": -0.03, "A15": -0.04, "A30": -0.05}, **{"C%d" % s: -0.005 for s in RD.STEPS})
    R4 = RD.assemble(mkV(g5s, g15s, mdiff=neg), seed, ml)
    chk["construction_negative_is_out"] = R4["type"] == "外れ"
    # φ の境（2 進の数でちょうど）: A1 = 0.5・A_s = 0.25 → shrink = 0.25
    def phi_case(cval, npos=4):
        def c(s, a):
            if s == 30:
                return cval
            return a + (0.0625 if RD.STEPS.index(s) < npos - 1 else -0.0625)
        G = mkcell({**{"A1": 0.5}, **{"A%d" % s: 0.25 for s in RD.STEPS}, **{"C%d" % s: c(s, 0.25) for s in RD.STEPS}})
        return RD.g_word(G)[0]
    eps = 2.0 ** -20
    cases = [(0.625, "列 C では縮みが小さい"), (0.625 + eps, "比が 1.5 を超える"), (0.375, "列 C では縮みが小さい"),
             (0.375 - eps, "形が定まらない"), (0.3125, "形が定まらない"), (0.3125 - eps, "列 C でも同じ程度に縮む"),
             (0.1875, "列 C でかえって大きく縮む"), (0.1875 + eps, "列 C でも同じ程度に縮む")]
    chk["phi_cut_points"] = all(phi_case(v) == w for v, w in cases)
    chk["three_or_more"] = phi_case(0.375, npos=3) == "列 C では縮みが小さい" and phi_case(0.375, npos=2) == "形が定まらない"
    Gs = mkcell({**{"A1": 0.25}, **{"A%d" % s: 0.25 for s in RD.STEPS}, **{"C%d" % s: 0.3 for s in RD.STEPS}})
    chk["no_shrink"] = RD.g_word(Gs)[0] == "列 A で縮まない"
    G12 = {c: {w: v for w, v in d.items() if int(w) < 11} for c, d in mkcell(gl(0.5, 0.25)).items()}
    chk["m_below_12"] = RD.g_word(G12)[0] == "欠けがある"
    chk["combine"] = (RD.combine(["欠けがある", "列 C では縮みが小さい"]) == "欠けがある" and
                      RD.combine(["列 C でも同じ程度に縮む", "列 C では縮みが小さい"]) == "割れる" and
                      RD.combine(["形が定まらない", "形が定まらない"]) == "形が定まらない")
    # 決定表の 5 行
    g3 = lambda a1, a30: gl(a1, a30, lambda s, a: a - 0.1)  # noqa: E731
    R5 = RD.assemble(mkV(g3(0.140, 0.043), g3(0.155, 0.096)), seed, ml)
    chk["table_rows"] = (R["type"], R2["type"], R5["type"], R3["type"], R4["type"]) == ("1", "2", "3", "なし", "外れ")
    # 句の置き方（文ごと）
    ok = True
    for Rx in (R, R2, R5):
        S = Rx["sentences"]
        for s in (S["new_section_result"], S["discussion_replace"]["new"], S["main_223"]["add"], S["contribution_add"]):
            ok = ok and ph1(s) and ph2(s) and ph3(s)
        if S["recommendation1_boundary_colC"]:
            ok = ok and ph1(S["recommendation1_boundary_colC"]) and ph2(S["recommendation1_boundary_colC"]) and ph3(
                S["recommendation1_boundary_colC"])
    for Rx in (R3, R4):
        S = Rx["sentences"]
        for s in (S["new_section_result"], S["discussion_replace"]["new"], S["main_223"]["add"], S["contribution_add"]):
            ok = ok and ph1(s) and ph2(s)
    S = R["sentences"]
    for s in [S["main_136_insert"], S["main_337_insert"], S["abstract_replace"]["new"]] + S["recommendation1_boundary_colA"][:1]:
        ok = ok and ph1(s) and not ph2(s) and not ph3(s)
    ok = ok and ph1(S["new_section_first_two"]) and ph2(S["new_section_first_two"])
    chk["phrases"] = bool(ok)
    # 語の英訳の表の語だけ
    en = set(RD.W_EN.values())
    tn = R3["sentences"]["new_section_result"]
    chk["words_from_table"] = RD.W_EN[R3["word"]] in tn and all(
        any(e in x for e in en) for x in R3["sentences"]["new_section_result_reservations"] if "the word is:" in x)
    # 留保の句が型 1〜3 で 3 か所に同じ条件で付く（型なしは新しい節だけ・外れは付けない）
    same3 = all(Rx["sentences"]["new_section_result_reservations"] == Rx["sentences"]["main_223_reservations"] ==
                Rx["sentences"]["contribution_reservations"] and len(Rx["sentences"]["main_223_reservations"]) >= 1
                for Rx in (R, R2, R5))
    chk["reservations_three_places"] = bool(same3 and R3["sentences"]["main_223_reservations"] == [] and
                                            len(R3["sentences"]["new_section_result_reservations"]) >= 1 and
                                            R4["sentences"]["new_section_result_reservations"] == [])
    # 型 1 の残差の文に結論の語が無い・型 1 にだけ付く
    rs = [x for x in R["sentences"]["new_section_after_result"] if x.startswith("Values only")]
    chk["type1_residual_no_conclusion"] = len(rs) == 1 and not any(
        w in rs[0].lower() for w in ("support", "consistent", "confirm", "mechanism", "because", "explain")) and not any(
        x.startswith("Values only") for x in R2["sentences"]["new_section_after_result"])
    chk["after_result_phrases"] = all(any(x.startswith("(The contiguous stretch") for x in Rx["sentences"]["new_section_after_result"])
                                      and any(x.startswith("With the structure fixed") for x in Rx["sentences"]["new_section_after_result"])
                                      for Rx in (R, R2, R3, R5)) and R4["sentences"]["new_section_after_result"] == []
    # 型 1 と列 C の C2a が「両方正でない」: 223 行の文は C2a に触れず、境の文と食い違わない
    c2a = {c: (-0.5 if c in ("A1", "A5") else 0.2) for c in g5s}
    for s in RD.STEPS:
        c2a["C%d" % s] = -0.2
    R6 = RD.assemble(mkV(g5s, g15s, c2a=c2a), seed, ml)
    t223 = R6["sentences"]["main_223"]["add"].lower()
    chk["type1_colC_c2a_not_pos"] = (R6["type"] == "1" and R6["boundary"]["s_star"] == 10 and
                                     R6["boundary"]["colC_at_s_star"] == "両方正でない" and
                                     not any(w in t223 for w in ("own chain", "first-order", "favour")) and
                                     "did not favour the per-person HMM in both cells at once" in R6["sentences"]["recommendation1_boundary_colC"])
    # 本文の句: 1 人抜き・不安定・区間・頭・τ = 10,000（reservations を直接）
    lo = {"5": dict(same=12, m=17, threshold=math.ceil(12 * 17 / 17)), "15": dict(same=11, m=15, threshold=math.ceil(12 * 15 / 17))}
    iv0 = {k: dict(ci=[0.1, 0.2], spans_zero=False) for k in RD.CELLS}
    r0 = RD.reservations(lo, iv0, "列 C では縮みが小さい", "列 C では縮みが小さい", "列 C では縮みが小さい")
    lo2 = {"5": dict(same=11, m=17, threshold=12), "15": dict(same=11, m=15, threshold=11)}
    r1 = RD.reservations(lo2, {**iv0, "15": dict(ci=[-0.1, 0.2], spans_zero=True)}, "列 C では縮みが小さい", "形が定まらない", "割れる")
    lo3 = {"5": dict(same=17, m=17, threshold=12), "15": dict(same=10, m=15, threshold=11)}
    r3 = RD.reservations(lo3, iv0, "列 C では縮みが小さい", "列 C では縮みが小さい", "列 C では縮みが小さい")
    chk["reservation_phrases"] = (lo["5"]["threshold"] == 12 and lo["15"]["threshold"] == 11 and len(r0) == 1 and
                                  r0[0].startswith("(Same word in 12 of 17 and 11 of 15") and
                                  "(The word is unstable when one writer is left out.)" in r1 and
                                  "(The interval spans zero in at least one cell.)" in r1 and
                                  "(Without the first symbol of each sequence the word is: %s.)" % RD.W_EN["形が定まらない"] in r1 and
                                  "(With τ fixed at 10,000 the word is: %s.)" % RD.W_EN["割れる"] in r1 and
                                  "(The word is unstable when one writer is left out.)" in r3)
    # 頭・τ = 10,000 の語の違いが assemble でも句になる
    R7 = RD.assemble(mkV(g5s, g15s, nohead={"5": gl(0.140, 0.043), "15": gl(0.155, 0.096)}), seed, ml)
    chk["nohead_phrase"] = any("Without the first symbol" in x for x in R7["sentences"]["new_section_result_reservations"])
    # 境の歩み: 分類 4 つ・単調でない並び・混ざる・r1 − 共有 hmm3 の分類 3 つ・列 C の分類
    chk["classify"] = (RD.classify(0.1, 0.2), RD.classify(-0.1, 0.0), RD.classify(0.1, -0.1), RD.classify(None, 0.1)) == CLS4

    def bcase(signs5, signs15, r1p_s=None, colc=None):
        c2 = {}
        for s, a, b in zip(RD.GRID, signs5, signs15):
            c2["A%d" % s] = (a, b)
        V = mkV(g5s, g15s)
        for k, j in (("5", 0), ("15", 1)):
            vals = {c: v[j] for c, v in c2.items()}
            vals.update({"C%d" % s: (colc[j] if colc else -0.2) for s in RD.STEPS})
            V["cells"][k]["C2a"] = mkcell(vals, offs=[o / 100 for o in OFFS])
            rp = {c: (r1p_s[j] if r1p_s else -0.1) for c in vals}
            V["cells"][k]["R1P"] = mkcell(rp, offs=[o / 100 for o in OFFS])
        return RD.boundary(V)
    N_, P_ = -0.2, 0.2
    nm = bcase([N_, P_, N_, P_, P_], [N_, P_, N_, P_, P_])
    mono = bcase([N_, N_, P_, P_, P_], [N_, N_, P_, P_, P_])
    mixed = bcase([N_, P_, P_, P_, P_], [N_, N_, P_, P_, P_])
    rp_pos = bcase([N_, N_, P_, P_, P_], [N_, N_, P_, P_, P_], r1p_s=(0.1, 0.1), colc=(0.2, 0.2))
    rp_mix = bcase([N_, N_, P_, P_, P_], [N_, N_, P_, P_, P_], r1p_s=(0.1, -0.1), colc=(0.2, -0.2))
    s_nm = RD.boundary_sentences(nm)
    s_mixed = RD.boundary_sentences(mixed)
    chk["boundary"] = (nm["s_star"] is None and "no grid step separated" in s_nm[0][0] and s_nm[1] is None and
                       mono["s_star"] == 10 and mono["r1p_at_s_star"] == "両方正でない" and
                       mixed["s_star"] == 10 and mixed["mixed_below"] == [5] and
                       any(x == "(At 5 s it favoured the per-person HMM in one cell only.)" for x in s_mixed[0]) and
                       rp_pos["r1p_at_s_star"] == "両方正" and rp_pos["colC_at_s_star"] == "両方正" and
                       "still favoured the own chain" in " ".join(RD.boundary_sentences(rp_pos)[0]) and
                       "also favoured the per-person HMM in both cells" in RD.boundary_sentences(rp_pos)[1] and
                       rp_mix["r1p_at_s_star"] == "混ざる" and "differed between cells" in " ".join(RD.boundary_sentences(rp_mix)[0]) and
                       RD.boundary_sentences(rp_mix)[1].endswith("the two cells disagreed.") and
                       "also favoured the shared HMM over the own chain" in " ".join(RD.boundary_sentences(mono)[0]) and
                       "(fewer symbols at longer steps)" in RD.boundary_sentences(mono)[0][0])
    # 補足の注: 列 C′ で語が変わる・見込みと違った
    R8 = RD.assemble(mkV(g5s, g15s, ds={c: (0.1 if c.startswith("C") else 0.2) for c in ["A1"] + [
        "%s%d" % (p, s) for p in ("A", "C") for s in RD.STEPS]}), seed, ml)
    chk["supplement_expectation_note"] = (R8["type"] == "1" and not R8["construction"]["as_expected"] and any(
        "did not follow the expected direction" in x for x in R8["sentences"]["supplement_notes"]))
    g5p = gl(0.140, 0.043, lambda s, a: 0.140, cprime=lambda s, a: a)
    g15p = gl(0.155, 0.096, lambda s, a: 0.155, cprime=lambda s, a: a)
    R9 = RD.assemble(mkV(g5p, g15p), seed, ml)
    chk["supplement_position_note"] = any(x.startswith("The word changes with the position of the stretch") for x in
                                          R9["sentences"]["supplement_notes"]) and R["sentences"]["supplement_notes"] == []
    return dict(passed=all(chk.values()), checks=chk)


CLS4 = ("両方正", "両方正でない", "混ざる", "欠け")


# ---------------------------------------------------------------- 入口
def main(seed, out, only, mut, run_id):
    set_mut(mut)
    t0 = time.time()
    want = set(only) if only else set(NAMES)
    Rr = dict(run_id=run_id, mutate=mut)
    fns = {"P-STRIDE": lambda: p_stride(seed), "P-BLOCK": lambda: p_block(seed), "P-PHASE": lambda: p_phase(seed),
           "P-TIME": lambda: p_time(seed), "P-MI": lambda: p_mi(seed), "P-DS": lambda: p_ds(seed), "P-FIRST": lambda: p_first(seed),
           "P-PAIR": lambda: p_pair(seed), "P-SWAP": lambda: p_swap(seed, mut), "P-READ": lambda: p_read(seed)}
    for n in NAMES:
        if n in want:
            t1 = time.time()
            Rr[n] = fns[n]()
            Rr[n]["seconds"] = time.time() - t1
    Rr["seconds"] = time.time() - t0
    Rr["all_passed"] = all(Rr[n]["passed"] for n in NAMES if n in Rr)
    json.dump(Rr, open(out, "w"), indent=1, default=float, ensure_ascii=False)
    print(json.dumps({n: Rr[n]["passed"] for n in NAMES if n in Rr}))
    return 0 if Rr["all_passed"] else 3


if __name__ == "__main__":
    argv = sys.argv[1:]
    mut, only, run_id = [], None, None
    while "--mutate" in argv:
        i = argv.index("--mutate")
        mut.append(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    for flag in ("--only", "--run-id", "--jobs"):
        if flag in argv:
            i = argv.index(flag)
            v = argv[i + 1]
            argv = argv[:i] + argv[i + 2:]
            if flag == "--only":
                only = v.split(",")
            elif flag == "--run-id":
                run_id = v
            else:
                JOBS = int(v)
    sys.exit(main(int(argv[0]), argv[1], only, sorted(mut), run_id))
