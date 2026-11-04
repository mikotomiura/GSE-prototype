"""CoAuthor と CS1 2021 で、1 人ごとの学習の改善（共通への寄せ・EM の構造・λ の選び方・書き手の中の見分け）を比べる。
条件は conditions.md、設計は .steering/20261104-gse-coauthor-ml-improve/design.md（判断 3〜8 が優先）。

使い方:
  python3 -I ml.py --selftest <seed> <out.json> [--mutate mX] [--only NAME,...] [--run-id ID]
  python3 -I ml.py <coauthor_work_obs> <cs1_work_obs> <seed> <out_dir> <jobs> [--only-dataset coauthor|cs1]
出力は集計値だけ。書き手・セッション・課題の番号を書かない。範囲の端を出さない。
代理ラベル（CoAuthor の提案の要求・CS1 の補完の受け入れ）は詰まりでも作業上の認知状態でもない。
EM の状態に名前を付けない（ADR-046 D1）。
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
import logit as LG  # noqa: E402

STRUCTS = [("hmm", 3), ("hmm", 6), ("hmm", 10), ("ar", 1), ("ar", 2), ("ar", 3)]
TAUS = [0, 100, 1000, 10000]
B_BOOT = 2000
MUT = set()   # m8: 他人で選ぶ v に w 自身を入れる・m10: 本人のモデルを本人の学習の問いで標準化する

DATASETS = {
    "coauthor": dict(H=5, grid=[1, 2, 3, 5, 8, 12, 15, 20, 30],
                     panels={"P15": (20, [1, 2, 3, 5, 8, 12, 15]), "P30": (35, [1, 2, 3, 5, 8, 12, 15, 20, 30])},
                     probe_sets=["main"]),
    "cs1": dict(H=1, grid=[1, 2, 3, 5], panels={"C5": (6, [1, 2, 3, 5])}, probe_sets=["main", "all"]),
}
VERS = ["tab", "recal"]


def sname(s):
    return "%s%d" % s


def set_mut(mut):
    for mod in (H, LG, DT):
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
    """評価に使う単位を除いた単位（評価の単位を持たない書き手は全単位）。"""
    return units[:len(units) - H_] if len(units) >= H_ + 1 else units


def pool_units(writers, H_, exclude=None):
    return [u for j, ss in enumerate(writers) if j != exclude for u in non_eval(ss, H_)]


# ---------------------------------------------------------------- EM の部品
def frozen_start():
    return dict(kind="hmm", pi=hmm_b.PI0.copy(), A=hmm_b.A0.copy(), B=hmm_b.B0.copy())


POOL_STARTS = 10


def pool_starts(kind, K, rng, seqs):
    """全員の共通の開始点 10 個（design §3.3 の 3 個を判断 9 で 10 個に）。K = 3 のふつうの HMM は凍結の正規化 ＋ 乱数 9 つ。"""
    _, h, T = H.r0_r1(seqs)
    st = []
    if (kind, K) == ("hmm", 3):
        st.append(("frozen", frozen_start()))
    while len(st) < POOL_STARTS:
        st.append(("rand%d" % len(st), H.random_model(kind, K, rng, r1=T, r0=h)))
    return st


def fit_pool_full(job):
    """全員の共通（構造ごと）。乱数は [SEED + 11, 構造の通し番号]。"""
    writers = _W[job["ds"]] if job.get("writers") is None else job["writers"]
    seqs = seqs_of(pool_units(writers, DATASETS[job["ds"]]["H"]))
    si, seed = job["si"], job["seed"]
    kind, K = STRUCTS[si]
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

    def ll_fb(self):
        O, M = hmm_b.pad(self.seqs)
        lp, _, _ = hmm_b.fb_engine(O, M, mutate_unnorm=False)
        return self.of_lp(lp)

    def sum_ll(self, m):
        lp = H.pred_logprob(m, self.D)
        return float(lp[self.D.M].sum()), int(self.D.M.sum())


def fit_self_all(kind, K, D, pool_m, sb, rng, h, T):
    """本人の当てはめ: τ = 0（開始点 = w を除く共通の解・乱数 1 つ）と τ > 0（共通の解・本人 τ = 0 の解）。
    返り値: {τ: 母数}・{τ: 診断}。"""
    out, diag = {}, {}
    m0, d0 = H.fit([("pool", pool_m), ("rand", H.random_model(kind, K, rng, r1=T, r0=h))], D, H.base_prior(kind, K))
    out[0], diag[0] = m0, d0
    for tau in TAUS[1:]:
        m, d = H.fit([("pool", pool_m), ("self0", m0)], D, H.make_prior(kind, K, tau, sb))
        out[tau], diag[tau] = m, d
    return out, diag


def em_writer(units, H_, ks, pools, rng, structs=None, do_folds=True):
    """1 書き手の EM。pools: {構造名: (母数, S̄)}。乱数の並べ: 構造 → k → (τ = 0 の乱数の開始点) → 折り目。"""
    n = len(units)
    _, test = DT.split(n, 1, H_)
    ev = Eval(seqs_of([units[i] for i in test]), pflags_of([units[i] for i in test]))
    res = dict(fb=ev.ll_fb(), pool={}, k={})
    for k in ks:
        train, test2 = DT.split(n, k, H_)
        assert test2 == test
        _, h, T = H.r0_r1(seqs_of([units[i] for i in train]))
        res["k"][str(k)] = dict(r1=ev.ll_r1(h, T), self={}, fold={}, diag={})
    for s in (structs or STRUCTS):
        kind, K = s
        name = sname(s)
        pool_m, sb = pools[name]
        res["pool"][name] = ev.ll(pool_m)
        for k in ks:
            train, _ = DT.split(n, k, H_)
            tr = [units[i] for i in train]
            D = H.Data(seqs_of(tr), chunk=H.CHUNK)
            _, h, T = H.r0_r1(seqs_of(tr))
            fits, diag = fit_self_all(kind, K, D, pool_m, sb, rng, h, T)
            rk = res["k"][str(k)]
            rk["self"][name] = {str(t): ev.ll(fits[t]) for t in TAUS}
            rk["diag"][name] = {str(t): dict(winner=diag[t]["winner"], gap12=diag[t]["gap12"], nonconv=diag[t]["nonconv"],
                                             decreases=diag[t]["decreases"]) for t in TAUS}
            fsum = {str(t): [0.0, 0] for t in TAUS}
            for fit_i, ev_i in (DT.folds(train) if do_folds else []):
                fu = [units[i] for i in fit_i]
                Df = H.Data(seqs_of(fu), chunk=H.CHUNK)
                _, hf, Tf = H.r0_r1(seqs_of(fu))
                ff, _ = fit_self_all(kind, K, Df, pool_m, sb, rng, hf, Tf)
                fev = Eval(seqs_of([units[i] for i in ev_i]), pflags_of([units[i] for i in ev_i]))
                for t in TAUS:
                    a, b = fev.sum_ll(ff[t])
                    fsum[str(t)][0] += a
                    fsum[str(t)][1] += b
            rk["fold"][name] = fsum if (do_folds and DT.folds(train)) else None
    return res


# ---------------------------------------------------------------- ロジスティックの部品
def probes_of(units, ps):
    key = "probes" if ps == "main" else "probes_all"
    return [p for u in units for p in u[key]]


def xy(items, ver):
    X = np.array([p[ver] for p in items], dtype=float).reshape(len(items), len(items[0][ver]) if items else (5 if ver == "tab" else 1))
    return X, np.array([p["y"] for p in items], dtype=float)


def pool_logistic(writers, H_, w, ver, ps):
    """w を除く書き手の評価以外の問いで: 標準化・寄せる先 β_共通（書き手の切片つき）・1 つの切片の共通・基準率。"""
    Xs, ys = [], []
    for j, ss in enumerate(writers):
        if j == w:
            continue
        X, y = xy(probes_of(non_eval(ss, H_), ps), ver)
        Xs.append(X)
        ys.append(y)
    Xall, yall = np.vstack(Xs), np.concatenate(ys)
    std = LG.Std(Xall)
    bc, conv_fe = LG.fit_fe([std(X) for X in Xs], ys)
    single, conv_s = LG.fit_logistic(std(Xall), yall, lam=LG.LAM0, pseudo=True)
    return dict(std=std, beta_c=bc, single=single, base=float(yall.mean()) if len(yall) else 0.5,
                conv_fe=conv_fe, conv_single=conv_s)


def fit_lambdas(Ztr, ytr, Zte, beta_c):
    """λ ごとの本人の当てはめ → 評価の予測と診断。"""
    preds, flags, raw = {}, {}, {}
    for lam in LG.LAMS:
        b, beta, conv = LG.fit_self(Ztr, ytr, beta_c, lam)
        preds[str(lam)] = LG.predict(b, beta, Zte).tolist() if len(Zte) else []
        flags[str(lam)] = dict(nonconv=not conv, far=bool(np.any(np.abs(beta - beta_c) > 10)))
        raw[str(lam)] = (b, beta)
    return preds, flags, raw


def logistic_writer(units, H_, ks, P, ver, ps):
    """1 書き手 × 版 × 問いの組。P は pool_logistic の結果。"""
    n = len(units)
    _, test = DT.split(n, 1, H_)
    Xte, yte = xy(probes_of([units[i] for i in test], ps), ver)
    std = P["std"]
    out = dict(y=yte.tolist(), pooled_single=LG.predict(P["single"][0], P["single"][1:], std(Xte)).tolist() if len(yte) else [],
               base_pool=P["base"], k={})
    for k in ks:
        train, _ = DT.split(n, k, H_)
        Xtr, ytr = xy(probes_of([units[i] for i in train], ps), ver)
        sstd = LG.Std(Xtr) if ("m10" in MUT and len(Xtr)) else std
        preds, flags, raw = fit_lambdas(sstd(Xtr), ytr, sstd(Xte), P["beta_c"])
        rec = dict(train_n=int(len(ytr)), train_pos=int(ytr.sum()), one_class=bool(len(set(ytr.tolist())) < 2),
                   b0_self=float((ytr.sum() + 0.5) / (len(ytr) + 1)), pred=preds, flags=flags,
                   raw_slope_inf=(raw["inf"][1] / sstd.sd).tolist())
        fl = {}
        fds = DT.folds(train)
        for lam in LG.LAMS:
            tot, cnt = 0.0, 0
            for fit_i, ev_i in fds:
                Xf, yf = xy(probes_of([units[i] for i in fit_i], ps), ver)
                Xe, ye = xy(probes_of([units[i] for i in ev_i], ps), ver)
                if len(ye) == 0:
                    continue
                fstd = LG.Std(Xf) if ("m10" in MUT and len(Xf)) else std
                b, beta, _ = LG.fit_self(fstd(Xf), yf, P["beta_c"], lam)
                tot += LG.logloss_sum(ye, LG.predict(b, beta, fstd(Xe)))
                cnt += len(ye)
            fl[str(lam)] = [tot, cnt]
        rec["fold"] = fl if fds else None
        out["k"][str(k)] = rec
    return out


# ---------------------------------------------------------------- 1 書き手（ワーカー）
_W = {}


def _init(paths, seed, mut):
    set_mut(mut)
    for ds, path in paths.items():
        _W[ds] = load(ds, path, seed)[0]


def load(ds, path, seed):
    if ds == "coauthor":
        return DT.load_coauthor(path, seed)
    return DT.load_cs1(path, seed, "block")


def eval_writer(job):
    t0 = time.time()
    writers = _W[job["ds"]] if job.get("writers") is None else job["writers"]
    cfg = DATASETS[job["ds"]]
    w, H_ = job["w"], cfg["H"]
    units = writers[w]
    rng = np.random.default_rng([job["seed"] + 10, job["wseq"]])
    out = dict(n=len(units), em=em_writer(units, H_, job["ks"], job["pools"], rng), lg={})
    for ps in cfg["probe_sets"]:
        for ver in VERS:
            P = pool_logistic(writers, H_, w, ver, ps)
            r = logistic_writer(units, H_, job["ks"], P, ver, ps)
            r["beta_c"] = P["beta_c"].tolist()
            r["pool_flags"] = dict(nonconv_fe=not P["conv_fe"], nonconv_single=not P["conv_single"])
            out["lg"][ps + "/" + ver] = r
    out["sec"] = time.time() - t0
    return out


# ---------------------------------------------------------------- 選び（他人・本人の CV）
def select_other(values, w, cands, maximize=True):
    """values: {書き手: {候補: Δ}}。w を除く v の Δ の中央値を最大（または最小）にする候補。
    同点は cands の先（呼ぶ側で大きい τ・λ を先に並べる）。m8 は w 自身を入れる。"""
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


def select_cv(fold, cands, maximize=True):
    """fold: {候補: [和, 数]}。数の 0 の候補は捨てる。同点は cands の先（呼ぶ側で大きい方・単純な方を先に並べる）。"""
    best, bv = None, None
    for c in cands:
        s, n = fold[c]
        if n == 0:
            continue
        v = s / n
        if bv is None or (v > bv if maximize else v < bv):
            best, bv = c, v
    return best


# ---------------------------------------------------------------- 集計の部品
def q(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    a = np.array(xs, dtype=float)
    qs = np.quantile(a, [0.25, 0.5, 0.75], method="inverted_cdf")
    return dict(median=float(qs[1]), q25=float(qs[0]), q75=float(qs[2]), n=len(xs))


def boot_median(vals, rng):
    a = np.array([v for v in vals if v is not None], dtype=float)
    if len(a) < 2:
        return None
    idx = rng.integers(0, len(a), (B_BOOT, len(a)))
    meds = np.median(a[idx], axis=1)
    return [float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))]


def delta_stats(d, rng, better_pos=True):
    d = [x for x in d if x is not None]
    if not d:
        return None
    r = q(d)
    r["better_share"] = float(np.mean([(x > 0) if better_pos else (x < 0) for x in d]))
    r["ci"] = boot_median(d, rng)
    return r


def boot_c(cn, rng):
    """cn: 書き手ごとの (一致の数, 組の数)。書き手の復元抽出でパーセンタイル区間。組が 0 の再標本は捨てる。"""
    a = np.array(cn, dtype=float)
    if len(a) < 2:
        return None, 0
    idx = rng.integers(0, len(a), (B_BOOT, len(a)))
    c, n = a[idx, 0].sum(1), a[idx, 1].sum(1)
    ok = n > 0
    if not ok.any():
        return None, int((~ok).sum())
    v = c[ok] / n[ok]
    return [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))], int((~ok).sum())


# ---------------------------------------------------------------- 集計: EM
def panel_members(results, cfg, ns):
    """{パネル名: {k: [書き手]}}。主のパネルと副（各 k で n_w ≥ k + H）。"""
    out = {}
    for pn, (nmin, ks) in cfg["panels"].items():
        ws = [w for w in results if ns[w] >= nmin]
        out[pn] = {k: ws for k in ks}
    out["secondary"] = {k: [w for w in results if ns[w] >= k + cfg["H"]] for k in cfg["grid"]}
    return out


def em_values(results, ws, k, s):
    """Δ_v(τ) = 本人(τ) − 共通（同じ構造）の評価の尤度（全記号）。"""
    return {v: {str(t): results[v]["em"]["k"][str(k)]["self"][sname(s)][str(t)][0] - results[v]["em"]["pool"][sname(s)][0]
                for t in TAUS} for v in ws}


def summarize_em(results, cfg, ns, rng):
    S = {}
    members = panel_members(results, cfg, ns)
    taus = [str(t) for t in TAUS]
    for pn, kmap in members.items():
        P = {}
        for k, ws in kmap.items():
            if not ws:
                continue
            E = dict(writers=len(ws), structs={}, kcv={})
            chosen_other = {}
            for s in STRUCTS:
                name = sname(s)
                vals = em_values(results, ws, k, s)
                rows = {}
                for t in taus:
                    rows["tau_" + t] = {w: t for w in ws}
                rows["tau_other"] = {w: select_other(vals, w, taus[::-1]) for w in ws}
                chosen_other[name] = rows["tau_other"]
                if k >= 3:
                    rows["tau_cv"] = {w: select_cv(results[w]["em"]["k"][str(k)]["fold"][name], taus[::-1]) for w in ws}
                E["structs"][name] = em_rows(results, ws, k, {r: {w: (name, t) for w, t in m.items()} for r, m in rows.items()}, rng)
                E["structs"][name]["chosen_tau_other"] = count_vals(rows["tau_other"].values())
                if k >= 3:
                    E["structs"][name]["chosen_tau_cv"] = count_vals(rows["tau_cv"].values())
                E["structs"][name]["diag"] = em_diag(results, ws, k, name)
            if k >= 3:
                fams = {"hmm": [s for s in STRUCTS if s[0] == "hmm"], "ar": [s for s in STRUCTS if s[0] == "ar"],
                        "both": sorted(STRUCTS, key=lambda s: H.n_free(*s))}
                for fam, ss in fams.items():
                    ss = sorted(ss, key=lambda s: H.n_free(*s))
                    pick = {}
                    for w in ws:
                        fold = results[w]["em"]["k"][str(k)]["fold"]
                        cand = {sname(s): fold[sname(s)][chosen_other[sname(s)][w]] for s in ss}
                        nm = select_cv(cand, [sname(s) for s in ss])
                        pick[w] = (nm, chosen_other[nm][w])
                    E["kcv"][fam] = em_rows(results, ws, k, {"k_cv": pick}, rng)
                    E["kcv"][fam]["chosen_struct"] = count_vals(p[0] for p in pick.values())
            P[str(k)] = E
        S[pn] = P
    return S


def count_vals(vs):
    out = {}
    for v in vs:
        out[str(v)] = out.get(str(v), 0) + 1
    return out


def em_rows(results, ws, k, rows, rng):
    """rows: {行: {書き手: (構造名, τ)}}。相手: r1・同じ構造の共通・K = 3 のふつうの HMM の共通・F-b。全記号と窓に押下のある記号。"""
    out = {}
    for r, pick in rows.items():
        o = {}
        for j, lab in enumerate(("all", "pressed")):
            for opp in ("r1", "pool_same", "pool_hmm3", "fb"):
                d = []
                for w in ws:
                    name, t = pick[w]
                    if t is None:
                        d.append(None)
                        continue
                    rk = results[w]["em"]["k"][str(k)]
                    me = rk["self"][name][t][j]
                    if opp == "r1":
                        other = rk["r1"][j]
                    elif opp == "pool_same":
                        other = results[w]["em"]["pool"][name][j]
                    elif opp == "pool_hmm3":
                        other = results[w]["em"]["pool"]["hmm3"][j]
                    else:
                        other = results[w]["em"]["fb"][j]
                    d.append(None if me is None or other is None else me - other)
                o[lab + "/self_minus_" + opp] = delta_stats(d, rng)
        out[r] = o
    return out


def em_diag(results, ws, k, name):
    out = {}
    for t in TAUS:
        ds = [results[w]["em"]["k"][str(k)]["diag"][name][str(t)] for w in ws]
        out[str(t)] = dict(winner=count_vals(d["winner"] for d in ds), gap12=q([d["gap12"] for d in ds]),
                           nonconv_starts=int(sum(d["nonconv"] for d in ds)), decreases=int(sum(d["decreases"] for d in ds)))
    return out


# ---------------------------------------------------------------- 集計: ロジスティック
def lg_models(results, ws, k, key):
    """書き手ごとの予測の行。λ の主（本人の CV・立たなければ他人）・副（他人）・固定 5・共通（1 つの切片）・B0-self・B0-pool。"""
    lams = [str(lam) for lam in LG.LAMS]
    rec = {w: results[w]["lg"][key] for w in ws}
    vals = {}
    for w in ws:
        r = rec[w]
        y = r["y"]
        if not y:
            vals[w] = {}
            continue
        b0 = LG.losses(y, [r["k"][str(k)]["b0_self"]] * len(y))[1]
        vals[w] = {lam: LG.losses(y, r["k"][str(k)]["pred"][lam])[1] - b0 for lam in lams}
    other = {w: select_other(vals, w, lams[::-1], maximize=False) for w in ws}
    main, src = {}, {"cv": 0, "other": 0}
    for w in ws:
        f = rec[w]["k"][str(k)]["fold"]
        c = select_cv(f, lams[::-1], maximize=False) if f else None
        if c is None:
            c = other[w]
            src["other"] += 1
        else:
            src["cv"] += 1
        main[w] = c
    models = {}
    for w in ws:
        r = rec[w]
        rk = r["k"][str(k)]
        n = len(r["y"])
        m = {"lam_" + lam: rk["pred"][lam] for lam in lams}
        m["self_main"] = rk["pred"][main[w]] if main[w] else None
        m["self_other"] = rk["pred"][other[w]] if other[w] else None
        m["pooled_single"] = r["pooled_single"]
        m["b0_self"] = [rk["b0_self"]] * n
        m["b0_pool"] = [r["base_pool"]] * n
        models[w] = m
    return models, dict(main=count_vals(main.values()), other=count_vals(other.values()), main_source=src)


def summarize_lg(results, cfg, ns, rng, ds):
    S = {}
    members = panel_members(results, cfg, ns)
    for pn, kmap in members.items():
        P = {}
        for k, ws in kmap.items():
            if not ws:
                continue
            E = {}
            for ps in cfg["probe_sets"]:
                for ver in VERS:
                    key = ps + "/" + ver
                    models, chosen = lg_models(results, ws, k, key)
                    ys = {w: results[w]["lg"][key]["y"] for w in ws}
                    rows = {}
                    for mn in next(iter(models.values())).keys():
                        wl = [w for w in ws if ys[w] and models[w][mn] is not None]
                        cn = [LG.conc_counts(ys[w], models[w][mn]) for w in wl]
                        C, nw = LG.within_c([ys[w] for w in wl], [models[w][mn] for w in wl])
                        ci, dropped = boot_c(cn, rng)
                        d_brier = [LG.losses(ys[w], models[w][mn])[0] - LG.losses(ys[w], models[w]["b0_self"])[0] for w in wl]
                        row = dict(C=C, C_minus_half=None if C is None else C - 0.5, writers_with_pairs=nw, C_ci=ci,
                                   C_boot_dropped=dropped, brier_minus_b0_self=delta_stats(d_brier, rng, better_pos=False))
                        if ds == "cs1":
                            row["auc_per_writer"] = q([LG.auc(ys[w], models[w][mn]) for w in wl])
                        rows[mn] = row
                    # 共通の逆向きの分け (a)
                    wl = [w for w in ws if ys[w]]
                    rows["pooled_single"]["pooled_auc"] = LG.pooled_auc([ys[w] for w in wl], [models[w]["pooled_single"] for w in wl])
                    flags = {f: int(sum(results[w]["lg"][key]["k"][str(k)]["flags"][lam][f] for w in ws for lam in
                                        [str(x) for x in LG.LAMS])) for f in ("nonconv", "far")}
                    E[key] = dict(writers=len(ws), models=rows, chosen_lambda=chosen,
                                  train_labels=q([results[w]["lg"][key]["k"][str(k)]["train_n"] for w in ws]),
                                  train_pos=q([results[w]["lg"][key]["k"][str(k)]["train_pos"] for w in ws]),
                                  test_labels=q([len(ys[w]) for w in ws]),
                                  test_pos=q([int(sum(ys[w])) for w in ws]),
                                  one_class_train=int(sum(results[w]["lg"][key]["k"][str(k)]["one_class"] for w in ws)),
                                  fit_flags_all_lambdas=flags)
            P[str(k)] = E
        S[pn] = P
    return S


def coef_split(writers, H_, ps, ver, results):
    """共通の逆向きの分け (b): 全員の評価以外の問いで、1 つの切片の版と書き手の切片の版の係数（標準化した尺度）。
    w を除く版の β_共通 の符号が全員の版と違う書き手の割合も出す。"""
    Xs, ys = [], []
    for ss in writers:
        X, y = xy(probes_of(non_eval(ss, H_), ps), ver)
        Xs.append(X)
        ys.append(y)
    Xall, yall = np.vstack(Xs), np.concatenate(ys)
    std = LG.Std(Xall)
    single, _ = LG.fit_logistic(std(Xall), yall, lam=LG.LAM0, pseudo=True)
    fe, _ = LG.fit_fe([std(X) for X in Xs], ys)
    key = ps + "/" + ver
    flips = []
    for j in range(len(fe)):
        bs = [np.sign(results[w]["lg"][key]["beta_c"][j]) for w in results]
        flips.append(float(np.mean([b != np.sign(fe[j]) for b in bs])))
    return dict(single=single[1:].tolist(), fixed_effects=fe.tolist(), fe_sign_flip_share_over_w=flips,
                probes=int(len(yall)), positives=int(yall.sum()))


# ---------------------------------------------------------------- 本計算
def run(paths, seed, out, jobs, only_ds=None):
    S = dict(datasets={})
    for ds in ([only_ds] if only_ds else ["coauthor", "cs1"]):
        cfg = DATASETS[ds]
        H_ = cfg["H"]
        t0 = time.time()
        writers, lstats = load(ds, paths[ds], seed)
        ns = [len(ss) for ss in writers]
        elig = [i for i, n in enumerate(ns) if n >= H_ + 1]
        for i in elig:
            assert all(DT.check_split(ns[i], k, H_) for k in cfg["grid"] if k <= ns[i] - H_)
        ex = ProcessPoolExecutor(jobs, initializer=_init, initargs=({ds: paths[ds]}, seed, sorted(MUT)))
        # 1 段目: 全員の共通（構造ごと）
        full = list(ex.map(fit_pool_full, [dict(ds=ds, si=si, seed=seed) for si in range(len(STRUCTS))]))
        # w を除く共通（開始点は全員の共通の解）
        pj = [dict(ds=ds, w=w, start=full[si][0]) for w in elig for si in range(len(STRUCTS))]
        pres = list(ex.map(fit_pool_excl, pj, chunksize=1))
        pools = {}
        pdiag = []
        it = iter(pres)
        for w in elig:
            pools[w] = {}
            for s in STRUCTS:
                m, sb, d = next(it)
                pools[w][sname(s)] = (m, sb)
                pdiag.append((sname(s), d))
        t1 = time.time()
        # 2 段目: 書き手ごと
        jl = [dict(ds=ds, w=w, wseq=j, seed=seed, ks=[k for k in cfg["grid"] if k <= ns[w] - H_], pools=pools[w])
              for j, w in enumerate(elig)]
        res = list(ex.map(eval_writer, jl, chunksize=1))
        ex.shutdown()
        results = {w: r for w, r in zip(elig, res)}
        raw = os.environ.get("GSE_ML_RAW")
        if raw:
            json.dump({ds: {str(k): v for k, v in results.items()}}, open(raw + "." + ds + ".json", "w"))
        rng = np.random.default_rng(seed + 4)
        D = dict(em=summarize_em(results, cfg, ns, rng), lg=summarize_lg(results, cfg, ns, rng, ds))
        D["coef_split"] = {ps + "/" + ver: coef_split(writers, H_, ps, ver, results) for ps in cfg["probe_sets"] for ver in VERS}
        D["pool_full_diag"] = {sname(s): dict(winner=d["winner"], gap12=d["gap12"], nonconv=d["nonconv"], decreases=d["decreases"])
                               for s, (_, d) in zip(STRUCTS, full)}
        D["pool_excl_diag"] = {sname(s): dict(nonconv=int(sum(d["nonconv"] for n, d in pdiag if n == sname(s))),
                                              decreases=int(sum(d["decreases"] for n, d in pdiag if n == sname(s))),
                                              iters=q([d["iters"][0] for n, d in pdiag if n == sname(s)]))
                               for s in STRUCTS}
        lab = [len(probes_of(writers[w][len(writers[w]) - H_:], "main")) for w in elig]
        pos = [sum(p["y"] for p in probes_of(writers[w][len(writers[w]) - H_:], "main")) for w in elig]
        D["four_tuple"] = dict(writers=len(elig), units_per_writer=q([ns[w] for w in elig]), labels_test=int(sum(lab)),
                               positives_test=int(sum(pos)), stall_episodes="使わない（0）")
        D["writers_total"] = len(writers)
        D["probe_stats"] = lstats
        D["seconds"] = dict(pools=t1 - t0, writers=time.time() - t1, per_writer=q([r["sec"] for r in res]))
        S["datasets"][ds] = D
        json.dump(S, open(os.path.join(out, "summary.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    argv = sys.argv[1:]
    mut = []
    while "--mutate" in argv:
        i = argv.index("--mutate")
        mut.append(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    set_mut(mut)
    if argv[0] == "--selftest":
        import selftest
        only, run_id = None, None
        if "--only" in argv:
            i = argv.index("--only")
            only = argv[i + 1].split(",")
            argv = argv[:i] + argv[i + 2:]
        if "--run-id" in argv:
            i = argv.index("--run-id")
            run_id = argv[i + 1]
            argv = argv[:i] + argv[i + 2:]
        sys.exit(selftest.main(int(argv[1]), argv[2], only, sorted(mut), run_id))
    only_ds = None
    if "--only-dataset" in argv:
        i = argv.index("--only-dataset")
        only_ds = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    run({"coauthor": argv[0], "cs1": argv[1]}, int(argv[2]), argv[3], int(argv[4]), only_ds)
