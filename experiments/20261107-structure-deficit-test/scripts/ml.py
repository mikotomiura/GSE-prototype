"""構造の足りなさの仮説を確かめる試験（EM だけ）。条件は conditions.md（tau-extend の条件から変える所）、
作業記録は .steering/20261107-gse-structure-deficit-test/（判断 1〜）。前の試験（tau-mode-candidate）の ml.py を写して変えた。

変えた所（conditions D1〜D4）:
- 列 q ∈ {3, 5, 7}（記号の数 q² + 1）× 順（o そのまま・p 系列の中で並べ替え）の 6 組を順に回す。
- 構造は hmm3・hmm6・hmm10・ar1・ar2・ar3 の 6 つすべて。最頻値・F-b・K = 3 の共通の相手・折り目の当てはめは作らない。
- k は P15 {1, 5, 15}・P30 {30}・C5 {1, 5}。作らない k と折り目の番では、tau-extend と同じ形の乱数を引いて捨てる。
- 量 G・G0・D = r1 − 共通・S0（他の人の τ = 0 の本人の当てはめを w に当てた値 − 共通の、v の中央値）。

使い方:
  python3 -I ml.py --selftest <seed> <out.json> [--mutate mX] [--only NAME,...] [--run-id ID]
  python3 -I ml.py <coauthor_work_obs> <cs1_work_obs> <seed> <out_dir> <jobs> [--only-dataset coauthor|cs1] [--groups q5_o,...]
出力は集計値だけ。書き手・セッション・課題の番号を書かない。範囲の端を出さない。
ラベルは使わない。評価の量は 1 歩先の予測の対数尤度だけ。EM の状態に名前を付けない（ADR-046 D1）。
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as DT  # noqa: E402
import hmm2 as H  # noqa: E402
import hmm_b  # noqa: E402

PREV_STRUCTS = [("hmm", 3), ("hmm", 6), ("hmm", 10), ("ar", 1), ("ar", 2), ("ar", 3)]
STRUCTS = list(PREV_STRUCTS)                               # 6 つすべてを当てはめる（判断 3）
SEQ_NO = {s: i for i, s in enumerate(PREV_STRUCTS)}       # 全員の共通の乱数の通し番号（ml-improve と同じ）
TAUS_FIT = [0, 100, 1000, 10000, 30000, 100000, 300000, 1000000]
INF = "inf"
TAU_KEYS = [str(t) for t in TAUS_FIT] + [INF]
B_BOOT = 2000
N_MIN = 6
GROUPS = [(5, "o"), (5, "p"), (3, "o"), (3, "p"), (7, "o"), (7, "p")]  # (5, o) が先（P-REPRO を先に照らす・D6）
OPPS = ("r1", "pool_same")
MUT = set()  # 引き継ぐ: m1〜m3・m6〜m8・m15。足す: m31〜m39（conditions V2）

DATASETS = {
    "coauthor": dict(H=5, no=0, grid=[1, 2, 3, 5, 8, 12, 15, 20, 30],
                     panels={"P15": (20, [1, 5, 15]), "P30": (35, [30])}),
    "cs1": dict(H=1, no=1, grid=[1, 2, 3, 5], panels={"C5": (6, [1, 5])}),
}


def gname(q_, order):
    return "q%d_%s" % (q_, order)


def sname(s):
    return "%s%d" % s


def tau_val(t):
    return float("inf") if t == INF else float(t)


def tau_cands():
    """τ 他人の候補（大きい方が先・同点は大きい τ）。"""
    return sorted(TAU_KEYS, key=tau_val, reverse=True)


def set_mut(mut):
    for mod in (H, DT):
        mod.MUT.clear()
        mod.MUT.update(mut)
    MUT.clear()
    MUT.update(mut)


# ---------------------------------------------------------------- 系列の取り出し
def seqs_of(units):
    return [s for u in units for s in u["seqs"]]


def pflags_of(units):
    return [f for u in units for f in u["pflag"]]


def non_eval(units, H_):
    return units[:len(units) - H_] if len(units) >= H_ + 1 else units


def pool_units(writers, H_, exclude=None):
    return [u for j, ss in enumerate(writers) if j != exclude for u in non_eval(ss, H_)]


# ---------------------------------------------------------------- EM の部品
def frozen_start():
    return dict(kind="hmm", pi=hmm_b.PI0.copy(), A=hmm_b.A0.copy(), B=hmm_b.B0.copy())


POOL_STARTS = 10


def pool_starts(kind, K, rng, seqs):
    """全員の共通の開始点 10 個。K = 3 のふつうの HMM は、記号が 26 の列（q = 5）だけ凍結の正規化 ＋ 乱数 9 つ
    （tau-extend と同じ）。ほかの列は凍結の放出の表の幅が合わないので乱数 10 個（条件の後の変更・判断 10）。"""
    _, h, T = H.r0_r1(seqs)
    st = []
    if (kind, K) == ("hmm", 3) and H.NSYM == 26:
        st.append(("frozen", frozen_start()))
    while len(st) < POOL_STARTS:
        st.append(("rand%d" % len(st), H.random_model(kind, K, rng, r1=T, r0=h)))
    return st


def fit_pool_full(job):
    """全員の共通（構造ごと）。乱数は [SEED + 11, 構造の通し番号]。"""
    writers = _W[job["ds"]] if job.get("writers") is None else job["writers"]
    seqs = seqs_of(pool_units(writers, DATASETS[job["ds"]]["H"]))
    si, seed = job["si"], job["seed"]
    kind, K = PREV_STRUCTS[si]
    rng = np.random.default_rng([seed + 11, si])
    D = H.Batched(seqs, chunk=H.CHUNK)
    m, diag = H.fit(pool_starts(kind, K, rng, seqs), D, H.base_prior(kind, K))
    return m, diag


def fit_pool_excl(job):
    """w を除く共通（1 開始点 = 全員の共通の解）。S̄ は最後の母数での E 段の期待度数 / 記号の総数。"""
    writers = _W[job["ds"]] if job.get("writers") is None else job["writers"]
    seqs = seqs_of(pool_units(writers, DATASETS[job["ds"]]["H"], exclude=job["w"]))
    m0 = job["start"]
    kind, K = m0["kind"], len(m0["pi"])
    D = H.Batched(seqs, chunk=H.CHUNK)
    m, diag = H.fit([("full_pool", m0)], D, H.base_prior(kind, K))
    S, _ = H.counts(m, D)
    return m, H.sbar_of(S, D.nobs), diag


class Eval:
    """評価の系列（切らない）。量は 1 歩先の対数尤度の 1 記号あたりの平均（全記号・窓に押下のある記号）。"""

    def __init__(self, seqs, pflags):
        keep = [i for i, s in enumerate(seqs) if len(s)]
        self.seqs = [seqs[i] for i in keep]
        self.D = H.Data(self.seqs)
        self.PF = np.zeros_like(self.D.M)
        for i, f in enumerate(pflags[j] for j in keep):
            self.PF[i, :len(f)] = f
        self.PF &= self.D.M

    def of_lp(self, lp):
        n, npf = self.D.M.sum(), self.PF.sum()
        return [float(lp[self.D.M].sum() / n), float(lp[self.PF].sum() / npf) if npf else None]

    def ll(self, m):
        return self.of_lp(H.pred_logprob(m, self.D))

    def ll_r1(self, h, T):
        lp = np.zeros(self.D.M.shape)
        for i, s in enumerate(self.seqs):
            s = np.asarray(s)
            lp[i, 0] = np.log(h[s[0]])
            lp[i, 1:len(s)] = np.log(T[s[:-1], s[1:]])
        return self.of_lp(lp)


def eval_of(units, H_):
    n = len(units)
    _, test = DT.split(n, 1, H_)
    return Eval(seqs_of([units[i] for i in test]), pflags_of([units[i] for i in test]))


def fit_self_all(kind, K, D, pool_m, sb, rng, h, T):
    """本人の当てはめ（有限の τ）: τ = 0（開始点 = w を除く共通の解・乱数 1 つ）と τ > 0（共通の解・本人 τ = 0 の解）。
    out["0r"] は τ = 0 の乱数の開始点（本人の学習の記号の r1・r0 と本人の乱数の流れだけから作る）の解（判断 11・S0 と G0r）。
    勝者の選びと乱数の流れは前の試験と同じ（開始点ごとの解を取っておくだけ）。"""
    out, diag = {}, {}
    m0, d0, alls = H.fit([("pool", pool_m), ("rand", H.random_model(kind, K, rng, r1=T, r0=h))], D, H.base_prior(kind, K),
                         keep_all=True)
    out[0], diag[0] = m0, d0
    out["0r"] = alls["rand"]
    for tau in TAUS_FIT[1:]:
        m, d = H.fit([("pool", pool_m), ("self0", m0)], D, H.make_prior(kind, K, tau, sb))
        out[tau], diag[tau] = m, d
    return out, diag


def discard_one(kind, K, units_tr, rng):
    """作らない番の乱数: 前の試験の τ = 0 の当てはめが引いた開始点と同じ形（r1・r0 もその番の学習の記号から）を引いて捨てる。
    m39 は引かない。"""
    if "m39" in MUT:
        return
    _, h, T = H.r0_r1(seqs_of(units_tr))
    H.random_model(kind, K, rng, r1=T, r0=h)


def em_writer(units, H_, ks, fit_ks, pools, rng, structs=None, keep="0"):
    """1 書き手の EM。pools: {構造名: (w を除く共通の母数, S̄)}。ks: 前の試験の並べ（乱数の位置）の k、fit_ks: 当てはめる k。
    乱数の並べ: 構造 → k →（τ = 0 の乱数の開始点）→ 折り目（tau-extend と同じ）。当てはめない k と折り目は引いて捨てる。
    keep: "0" は τ = 0 の母数を返す（S0 用）、"all" は全 τ の母数を返す（m38 の対照用）。
    τ = ∞ は当てはめず、w を除く共通の母数を使う。"""
    n = len(units)
    ev = eval_of(units, H_)
    res = dict(pool={}, k={}, n_eval=int(ev.D.M.sum()), fits={})
    for k in fit_ks:
        train, _ = DT.split(n, k, H_)
        tr_seqs = seqs_of([units[i] for i in train])
        _, h, T = H.r0_r1(tr_seqs)
        res["k"][str(k)] = dict(r1=ev.ll_r1(h, T), self={}, diag={}, n_train=int(sum(len(s) for s in tr_seqs)))
    for s in (PREV_STRUCTS if structs is None else structs):
        kind, K = s
        name = sname(s)
        pool_m, sb = pools[name]
        res["pool"][name] = ev.ll(pool_m)
        for k in ks:
            train, _ = DT.split(n, k, H_)
            tr = [units[i] for i in train]
            if k in fit_ks:
                D = H.Data(seqs_of(tr), chunk=H.CHUNK)
                _, h, T = H.r0_r1(seqs_of(tr))
                fits, diag = fit_self_all(kind, K, D, pool_m, sb, rng, h, T)
                kept = {"0r": fits["0r"]} if keep == "0" else {str(t): fits[t] for t in TAUS_FIT}
                kept["0r"] = fits["0r"]
                res["fits"].setdefault(name, {})[str(k)] = kept
                rk = res["k"][str(k)]
                rk["self"][name] = {str(t): ev.ll(fits[t]) for t in TAUS_FIT}
                rk.setdefault("self0r", {})[name] = ev.ll(fits["0r"])
                rk["self"][name][INF] = ev.ll(pool_m)
                rk["diag"][name] = {str(t): dict(winner=diag[t]["winner"], gap12=diag[t]["gap12"],
                                                 nonconv=diag[t]["nonconv"], decreases=diag[t]["decreases"])
                                    for t in TAUS_FIT}
            else:
                discard_one(kind, K, tr, rng)
            for fit_i, _ in DT.folds(train):
                discard_one(kind, K, [units[i] for i in fit_i], rng)
    return res


# ---------------------------------------------------------------- ワーカー
_W = {}


def _init(paths, seed, mut, q_, order):
    set_mut(mut)
    H.set_nsym(q_ * q_ + 1)
    for ds, path in paths.items():
        _W[ds] = DT.variant(load(ds, path, seed)[0], q_, order, seed, DATASETS[ds]["no"], DATASETS[ds]["H"])


def load(ds, path, seed):
    if ds == "coauthor":
        return DT.load_coauthor(path, seed)
    return DT.load_cs1(path, seed, "block")


def eval_writer(job):
    t0 = time.time()
    writers = _W[job["ds"]] if job.get("writers") is None else job["writers"]
    H_ = DATASETS[job["ds"]]["H"]
    rng = np.random.default_rng([job["seed"] + 10, job["wseq"]])
    em = em_writer(writers[job["w"]], H_, job["ks"], job["fit_ks"], job["pools"], rng, structs=job.get("structs"),
                   keep=job.get("keep", "0"))
    fits = em.pop("fits")
    return dict(n=len(writers[job["w"]]), em=em, fits=fits, sec=time.time() - t0)


def eval_others(job):
    """S0 の材料: w の評価の単位で、他の人 v の母数（job["others"] {k: {構造名: [母数]}}）の評価 − w を除く共通の評価。
    返り値 {k: {構造名: [全記号の v の中央値, 押下の v の中央値]}}。新しい当てはめはしない。"""
    writers = _W[job["ds"]] if job.get("writers") is None else job["writers"]
    ev = eval_of(writers[job["w"]], DATASETS[job["ds"]]["H"])
    out = {}
    for k, by in job["others"].items():
        out[k] = {}
        for name, ms in by.items():
            pool = job["pool"][name]
            vals = [ev.ll(m) for m in ms]
            out[k][name] = [float(np.median([v[0] - pool[0] for v in vals])) if vals else None,
                            float(np.median([v[1] - pool[1] for v in vals]))
                            if vals and pool[1] is not None and all(v[1] is not None for v in vals) else None]
    return out


# ---------------------------------------------------------------- 選び
def select_other(values, w, cands, maximize=True):
    """values: {書き手: {候補: Δ}}。w を除く v の Δ の中央値を最大にする候補。同点は cands の先。m8 は w 自身を入れる。"""
    vs = [v for v in values if v != w or "m8" in MUT]
    best, bv = None, None
    for c in cands:
        xs = [values[v][c] for v in vs if values[v].get(c) is not None]
        if not xs:
            continue
        m = float(np.median(xs))
        if bv is None or (m > bv if maximize else m < bv):
            best, bv = c, m
    return best


# ---------------------------------------------------------------- 集計の部品
def q(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    if len(xs) < N_MIN:
        return dict(n=len(xs), suppressed=True)
    a = np.array(xs, dtype=float)
    qs = np.quantile(a, [0.25, 0.5, 0.75], method="inverted_cdf")
    return dict(median=float(qs[1]), q25=float(qs[0]), q75=float(qs[2]), n=len(xs))


def boot_median(vals, rng):
    a = np.array([v for v in vals if v is not None], dtype=float)
    if len(a) < N_MIN:
        return None
    idx = rng.integers(0, len(a), (B_BOOT, len(a)))
    meds = np.median(a[idx], axis=1)
    return [float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))]


def delta_stats(d, rng, better_pos=True):
    d = [x for x in d if x is not None]
    if not d:
        return None
    if any(not np.isfinite(x) for x in d):
        raise ValueError("差に有限でない値がある")
    if len(d) < N_MIN:
        return dict(n=len(d), suppressed=True)
    r = q(d)
    r["better_share"] = float(np.mean([(x > 0) if better_pos else (x < 0) for x in d]))
    r["ci"] = boot_median(d, rng)
    return r


def enc(x):
    if isinstance(x, dict):
        return {(k if isinstance(k, str) else str(k)): enc(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [enc(v) for v in x]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        x = float(x)
        if not np.isfinite(x):
            raise ValueError("有限でない値を JSON に書こうとした")
        return x
    return x


def dump_json(obj, path, indent=None):
    with open(path, "w") as f:
        json.dump(enc(obj), f, indent=indent, ensure_ascii=False, allow_nan=False)


def count_vals(vs):
    out = {}
    for v in vs:
        out[str(v)] = out.get(str(v), 0) + 1
    n = sum(out.values())
    return out if n >= N_MIN else dict(n=n, suppressed=True)


def tau_region(taus):
    taus = [t for t in taus if t is not None]
    r = dict(inside=0, low_end=0, high_finite_end=0, inf=0)
    for t in taus:
        if t == INF:
            r["inf"] += 1
        elif t == "0":
            r["low_end"] += 1
        elif t == str(TAUS_FIT[-1]):
            r["high_finite_end"] += 1
        else:
            r["inside"] += 1
    return r if len(taus) >= N_MIN else dict(n=len(taus), suppressed=True)


def kendall_b(x, y):
    """Kendall の τ_b（記述・閾値は置かない）。値が 2 つ未満・どちらかが全部同じなら None。"""
    n = len(x)
    if n < 2:
        return None
    c = d = tx = ty = 0
    for i in range(n):
        for j in range(i + 1, n):
            a = np.sign(x[i] - x[j])
            b = np.sign(y[i] - y[j])
            if a == 0 and b == 0:
                continue
            if a == 0:
                tx += 1
            elif b == 0:
                ty += 1
            elif a == b:
                c += 1
            else:
                d += 1
    den = np.sqrt((c + d + tx) * (c + d + ty))
    return None if den == 0 else float((c - d) / den)


# ---------------------------------------------------------------- 集計: EM
def panel_members(results, cfg, ns):
    """{パネル名: [書き手]}（n_w ≥ nmin）。results の書き手だけ。"""
    return {pn: [w for w in results if ns[w] >= nmin] for pn, (nmin, _) in cfg["panels"].items()}


def fit_ks_of(n_w, cfg):
    """書き手が当てはめる k（入っているパネルの k の和）。"""
    return sorted({k for nmin, ks in cfg["panels"].values() if n_w >= nmin for k in ks})


def panel_of_k(cfg):
    return {k: pn for pn, (_, ks) in cfg["panels"].items() for k in ks}


def self_of(results, w, k, name, t, j):
    return results[w]["em"]["k"][str(k)]["self"][name][t][j]


def em_values(results, ws, k, name):
    """Δ_v(τ) = 本人(τ) − 共通（同じ構造・w を除く）（全記号）。τ = ∞ の Δ_v は 0。"""
    return {v: {t: self_of(results, v, k, name, t, 0) - results[v]["em"]["pool"][name][0] for t in TAU_KEYS} for v in ws}


def row_deltas(results, ws, k, pick, j, opp):
    """書き手ごとの差（行 − 相手）の並び（ws の順・None は除外の印）。"""
    d = []
    for w in ws:
        name, t = pick[w] if pick[w] is not None else (None, None)
        if t is None:
            d.append(None)
            continue
        me = self_of(results, w, k, name, t, j)
        other = results[w]["em"]["k"][str(k)]["r1"][j] if opp == "r1" else results[w]["em"]["pool"][name][j]
        d.append(None if me is None or other is None else me - other)
    return d


def em_rows(results, ws, k, rows, rng):
    out = {}
    for r, pick in rows.items():
        o = {}
        for j, lab in enumerate(("all", "pressed")):
            for opp in OPPS:
                o[lab + "/self_minus_" + opp] = delta_stats(row_deltas(results, ws, k, pick, j, opp), rng)
        out[r] = o
    return out


def pool_r1_values(results, ws, k, name, j, sign=1):
    """書き手ごとの sign · (共通 − r1)。sign = −1 が D = r1 − 共通（足りなさ・D4）。m36 は中央値どうしの差を配る。"""
    ps = [results[w]["em"]["pool"][name][j] for w in ws]
    rs = [results[w]["em"]["k"][str(k)]["r1"][j] for w in ws]
    if "m36" in MUT and sign == -1:
        ok = [(a, b) for a, b in zip(ps, rs) if a is not None and b is not None]
        d = float(np.median([b for _, b in ok]) - np.median([a for a, _ in ok])) if ok else None
        return [d] * len(ws)
    return [None if a is None or b is None else sign * (a - b) for a, b in zip(ps, rs)]


def g0r_values(results, ws, k, name, j):
    """G0r = 本人の τ = 0 の乱数の開始点の解 − w を除く共通（S0 と同じ土台・判断 11）。"""
    out = []
    for w in ws:
        a = results[w]["em"]["k"][str(k)]["self0r"][name][j]
        b = results[w]["em"]["pool"][name][j]
        out.append(None if a is None or b is None else a - b)
    return out


def s0_values(S0, ws, k, name, j):
    return [S0.get(w, {}).get(str(k), {}).get(name, [None, None])[j] for w in ws]


def em_diag(results, ws, k, name):
    out = {}
    for t in TAUS_FIT:
        ds = [results[w]["em"]["k"][str(k)]["diag"][name][str(t)] for w in ws]
        out[str(t)] = dict(winner=count_vals(d["winner"] for d in ds), gap12=q([d["gap12"] for d in ds]),
                           nonconv_starts=int(sum(d["nonconv"] for d in ds)), decreases=int(sum(d["decreases"] for d in ds)))
    return out


def chosen_other(results, ws, k, name):
    vals = em_values(results, ws, k, name)
    return {w: select_other(vals, w, tau_cands()) for w in ws}


def summarize_em(results, S0, cfg, ns, rng, structs=None):
    structs = STRUCTS if structs is None else structs
    S = {}
    for pn, ws in panel_members(results, cfg, ns).items():
        P = {}
        for k in cfg["panels"][pn][1]:
            if not ws:
                continue
            if len(ws) < N_MIN:  # 人数の少ないパネルは節ごと伏せる（診断の和も出さない・security-checker LOW-1）
                P[str(k)] = dict(writers=len(ws), suppressed=True)
                continue
            E = dict(writers=len(ws), structs={},
                     n_train=q([results[w]["em"]["k"][str(k)]["n_train"] for w in ws]),
                     n_eval=q([results[w]["em"]["n_eval"] for w in ws]))
            for s in structs:
                name = sname(s)
                rows = {"tau_" + t: {w: (name, t) for w in ws} for t in TAU_KEYS}
                co = chosen_other(results, ws, k, name)
                rows["tau_other"] = {w: (name, co[w]) for w in ws}
                St = em_rows(results, ws, k, rows, rng)
                St["chosen_tau_other"] = count_vals(co.values())
                St["chosen_tau_other_region"] = tau_region(co.values())
                St["pool_minus_r1"] = {lab: delta_stats(pool_r1_values(results, ws, k, name, j), rng)
                                       for j, lab in enumerate(("all", "pressed"))}
                St["deficit"] = {lab: delta_stats(pool_r1_values(results, ws, k, name, j, sign=-1), rng)
                                 for j, lab in enumerate(("all", "pressed"))}
                St["S0"] = {lab: delta_stats(s0_values(S0, ws, k, name, j), rng)
                            for j, lab in enumerate(("all", "pressed"))}
                St["G0r"] = {lab: delta_stats(g0r_values(results, ws, k, name, j), rng)
                             for j, lab in enumerate(("all", "pressed"))}
                St["diag"] = em_diag(results, ws, k, name)
                E["structs"][name] = St
            E["kendall"] = kendall_cells(E, structs)
            P[str(k)] = E
        S[pn] = P
    return S


def med_of(st):
    return None if st is None or st.get("suppressed") else st["median"]


def kendall_cells(E, structs):
    """記述（D4・判定に使わない）: 6 構造の D の中央値と G（τ 他人）・G0 の中央値の Kendall の τ_b（全記号）。"""
    names = [sname(s) for s in structs]
    Dm = [med_of(E["structs"][n]["deficit"]["all"]) for n in names]
    out = {}
    for lab, row in (("G", "tau_other"), ("G0", "tau_0")):
        Gm = [med_of(E["structs"][n][row]["all/self_minus_pool_same"]) for n in names]
        ok = [(a, b) for a, b in zip(Dm, Gm) if a is not None and b is not None]
        out[lab] = kendall_b([a for a, _ in ok], [b for _, b in ok]) if len(ok) == len(names) else None
    return out


# ---------------------------------------------------------------- S0 の段（他人の当てはめの評価）
def others_jobs(ds, results, fits, pools_val, cfg, ns, chosen=None, pools_m=None, structs=None):
    """書き手 w ごとに、同じパネル・同じ k の他の書き手 v の τ = 0 の乱数の開始点の解を集める（判断 11）。
    m37 は v = w を入れる。m38 は v の τ 他人で選んだ τ の母数（∞ は v を除く共通）を使う（chosen・pools_m が要る）。"""
    pk = panel_of_k(cfg)
    members = panel_members(results, cfg, ns)
    jobs = []
    for w in results:
        others = {}
        for k in fit_ks_of(ns[w], cfg):
            ws = members[pk[k]]
            if w not in ws:
                continue
            by = {}
            for s in (STRUCTS if structs is None else structs):
                name = sname(s)
                ms = []
                for v in ws:
                    if v == w and "m37" not in MUT:
                        continue
                    if "m38" in MUT:
                        t = chosen[(pk[k], k, name)][v]
                        ms.append(pools_m[v][name][0] if t == INF else fits[v][name][str(k)][t])
                    else:
                        ms.append(fits[v][name][str(k)]["0r"])
                by[name] = ms
            others[str(k)] = by
        jobs.append(dict(ds=ds, w=w, others=others, pool=pools_val[w]))
    return jobs


# ---------------------------------------------------------------- 1 組・1 データ
def run_one(ds, path, seed, q_, order, jobs, raw=None, ex_writers=None, structs=None):
    """1 組（列 q・順 order）× 1 データ。返り値: (summary の節, 中身)。ex_writers は selftest が合成の書き手を渡すとき
    （そのときは列と順の作り直しをせず、渡された単位の seqs をそのまま使う）。structs は selftest が構造を絞るとき
    （そのときは外した構造の乱数を捨てない・本計算は None）。"""
    SS = STRUCTS if structs is None else structs
    cfg = DATASETS[ds]
    H_ = cfg["H"]
    t0 = time.time()
    H.set_nsym(q_ * q_ + 1)
    if ex_writers is None:
        writers = DT.variant(load(ds, path, seed)[0], q_, order, seed, cfg["no"], H_)
        initargs = ({ds: path}, seed, sorted(MUT), q_, order)
        wj = None
    else:
        writers = ex_writers
        initargs = ({}, seed, sorted(MUT), q_, order)
        wj = writers
    ns = [len(ss) for ss in writers]
    elig = [i for i, n in enumerate(ns) if n >= H_ + 1]
    nmin_all = min(nmin for nmin, _ in cfg["panels"].values())
    memb = [w for w in elig if ns[w] >= nmin_all]  # どれかのパネルに入る書き手だけを当てはめる
    for i in memb:
        assert all(DT.check_split(ns[i], k, H_) for k in cfg["grid"] if k <= ns[i] - H_)
    with ProcessPoolExecutor(jobs, initializer=_init, initargs=initargs) as ex:
        full = list(ex.map(fit_pool_full, [dict(ds=ds, si=SEQ_NO[s], seed=seed, writers=wj) for s in SS]))
        pj = [dict(ds=ds, w=w, start=full[si][0], writers=wj) for w in memb for si in range(len(SS))]
        pres = list(ex.map(fit_pool_excl, pj, chunksize=1))
        pools, pdiag, it = {}, [], iter(pres)
        for w in memb:
            pools[w] = {}
            for s in SS:
                m, sb, d = next(it)
                pools[w][sname(s)] = (m, sb)
                pdiag.append((sname(s), d))
        t1 = time.time()
        # 書き手の通し番号は前の試験と同じ（elig の中の位置）
        keep = "all" if "m38" in MUT else "0"
        jl = [dict(ds=ds, w=w, wseq=elig.index(w), seed=seed, ks=[k for k in cfg["grid"] if k <= ns[w] - H_],
                   fit_ks=fit_ks_of(ns[w], cfg), pools=pools[w], keep=keep, writers=wj, structs=structs) for w in memb]
        res = list(ex.map(eval_writer, jl, chunksize=1))
        results = {w: dict(n=r["n"], em=r["em"], sec=r["sec"]) for w, r in zip(memb, res)}
        fits = {w: r["fits"] for w, r in zip(memb, res)}
        t2 = time.time()
        chosen = None
        if "m38" in MUT:
            pk = panel_of_k(cfg)
            mem = panel_members(results, cfg, ns)
            chosen = {(pk[k], k, sname(s)): chosen_other(results, mem[pk[k]], k, sname(s))
                      for k in pk for s in SS if mem[pk[k]]}
        oj = others_jobs(ds, results, fits, {w: results[w]["em"]["pool"] for w in memb}, cfg, ns, chosen, pools, SS)
        for j in oj:
            j["writers"] = wj
        S0 = dict(zip([j["w"] for j in oj], ex.map(eval_others, oj, chunksize=1)))
    if raw:
        import pickle
        with open(raw + ".%s.%s.pkl" % (gname(q_, order), ds), "wb") as fp:
            pickle.dump(dict(results=results, S0=S0), fp)
    rng = np.random.default_rng(seed + 4)
    D = dict(em=summarize_em(results, S0, cfg, ns, rng, SS), nsym=H.NSYM)
    D["pool_full_diag"] = {sname(s): dict(winner=d["winner"], gap12=d["gap12"], nonconv=d["nonconv"], decreases=d["decreases"])
                           for s, (_, d) in zip(SS, full)}
    D["pool_excl_diag"] = {sname(s): dict(nonconv=int(sum(d["nonconv"] for n, d in pdiag if n == sname(s))),
                                          decreases=int(sum(d["decreases"] for n, d in pdiag if n == sname(s))),
                                          iters=q([d["iters"][0] for n, d in pdiag if n == sname(s)]))
                           for s in SS}
    D["four_tuple"] = dict(writers=len(memb), units_per_writer=q([ns[w] for w in memb]),
                           eval_symbols=int(sum(results[w]["em"]["n_eval"] for w in memb)),
                           questions="使わない", stall_episodes="使わない（0）")
    D["writers_total"] = len(writers)
    D["seconds"] = dict(pools=t1 - t0, writers=t2 - t1, others=time.time() - t2, per_writer=q([r["sec"] for r in res]))
    return D, dict(results=results, S0=S0, pools=pools, fits=fits, ns=ns, full=full)


# ---------------------------------------------------------------- 本計算
def raw_in_repo(raw):
    """書き手ごとの値の置き場が repo（この worktree、またはどこかの git の作業ツリー）の中か。大文字小文字をそろえて比べる。"""
    import subprocess
    nc = lambda p: os.path.normcase(os.path.realpath(p))
    repo = nc(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
    d = os.path.dirname(os.path.abspath(raw)) or "."
    if nc(raw).startswith(repo + os.sep) or nc(d) == repo:
        return True
    while not os.path.isdir(d):
        d = os.path.dirname(d)
    r = subprocess.run(["git", "-C", d, "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() == "true"


def q_gate_all(paths, seed, only_ds=None):
    """P-Q（V1）: 全データの全 feat 行で、q = 5 の作り直しが中間の obs と一致するか。"""
    out = {}
    for ds in ([only_ds] if only_ds else ["coauthor", "cs1"]):
        n, bad = DT.q_gate(load(ds, paths[ds], seed)[0])
        out[ds] = dict(rows=n, mismatched=bad)
    return out


def run(paths, seed, out, jobs, only_ds=None, run_id=None, groups=None):
    raw = os.environ.get("GSE_ML_RAW")
    if raw and raw_in_repo(raw):
        sys.exit("GSE_ML_RAW が repo の中を指している（書き手ごとの値は repo の外だけ）")
    qg = q_gate_all(paths, seed, only_ds)
    dump_json(dict(run_id=run_id, datasets=qg), os.path.join(out, "q_gate.json"), indent=1)
    if any(v["mismatched"] for v in qg.values()):
        sys.exit("P-Q: q = 5 の作り直しが obs と一致しない行がある（止めて研究者に聞く）")
    sp = os.path.join(out, "summary.json")
    S = json.load(open(sp)) if os.path.exists(sp) else dict(run_id=run_id, groups={})
    for q_, order in GROUPS:
        g = gname(q_, order)
        if groups and g not in groups:
            continue
        for ds in ([only_ds] if only_ds else ["coauthor", "cs1"]):
            D, _ = run_one(ds, paths[ds], seed, q_, order, jobs, raw)
            S["groups"].setdefault(g, dict(q=q_, order=order, datasets={}))["datasets"][ds] = D
            S["run_id"] = run_id
            dump_json(S, sp, indent=1)


def _opt(argv, name):
    if name in argv:
        i = argv.index(name)
        return argv[i + 1], argv[:i] + argv[i + 2:]
    return None, argv


if __name__ == "__main__":
    argv = sys.argv[1:]
    mut = []
    while "--mutate" in argv:
        m_, argv = _opt(argv, "--mutate")
        mut.append(m_)
    set_mut(mut)
    if argv[0] == "--selftest":
        import selftest
        only, argv = _opt(argv, "--only")
        run_id, argv = _opt(argv, "--run-id")
        sys.exit(selftest.main(int(argv[1]), argv[2], only.split(",") if only else None, sorted(mut), run_id))
    run_id, argv = _opt(argv, "--run-id")
    only_ds, argv = _opt(argv, "--only-dataset")
    groups, argv = _opt(argv, "--groups")
    run({"coauthor": argv[0], "cs1": argv[1]}, int(argv[2]), argv[3], int(argv[4]), only_ds, run_id,
        groups.split(",") if groups else None)
