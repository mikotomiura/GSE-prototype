"""擬似残差（乱数化した分位の残差）と、その自己相関（conditions D4）。当てはめはしない（fit.py の npz と選びを読む）。

1 歩先の予測の分布 p(· | 前までの記号)（26 値・tau-extend の hmm2.pred_dist と同じ前向き。r1 は前の記号の行）を、
25 を除いて正規化し、x の帯（記号 // 5）・y の帯（記号 % 5）の周辺に畳む。観測の帯 b で
U = F(b − 1) + v · (F(b) − F(b − 1))、z = Φ⁻¹(U)（U は [1e-12, 1 − 1e-12] に切る）。観測が 25 の時刻は欠け。
v は共通の乱数: default_rng([SEED + 51, データの番号, 書き手の通し番号, 列の番号]) から、評価の単位の時刻の順に
2 つずつ（x が先）引く。どのモデルでも同じ v を使う。v は 25 の時刻にも引く（使わない・並べを観測に依らせないため）。

使い方:
  python3 -I residual.py <coauthor|cs1> <col> <work> <sidecar|-> <seed> <out_dir> <raw_dir> [--run-id ID]
出力: <out_dir>/parts/res.<データ>.<列>.json（集計値だけ）。
返り値: 0 = 済んだ、3 = npz から読み戻した母数の評価の尤度が fit.py の値と一致しない（P-NPZ の実データ版）。
"""
import json
import os
import sys
import time
from statistics import NormalDist

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I では自分のディレクトリが入らない
import pinned  # noqa: E402
from pinned import DT, H, ml
import fit as F
import load as L

DS_NO = {"coauthor": 0, "cs1": 1}
LAGS = list(range(1, 11))
CLIP = 1e-12
G = 5  # 格子の帯の数（kit の constants.json の grid_bins）
RUN = 25
MUT = set()  # m45: o_t を見たフィルタで o_t を予測する・m46: v を 0.5 に固定・m47: x と y の帯を入れ替える・m48: モデルごとに v を引く
_ND = NormalDist()


def set_mut(mut):
    MUT.clear()
    MUT.update(mut)


# ---------------------------------------------------------------- 予測の分布
def pred_dist_model(m, D):
    """D（評価の系列）の各時刻の予測の分布（n × T × 26）。m45 は o_t を見たフィルタ（alpha_t）から o_t を予測する漏れ。"""
    if "m45" not in MUT:
        dist, _, _ = H.pred_dist(m, D)
        return dist
    alpha, _, _ = H.forward(m, D)
    if m["kind"] == "hmm":
        return alpha @ m["B"]
    head = D.P < 0
    prev = np.where(head, 0, D.P)
    Cp = np.moveaxis(m["C"][:, prev, :], 0, 2)
    dist = np.einsum("ntk,ntks->nts", alpha, Cp)
    return np.where(head[..., None], alpha @ m["H"], dist)


def pred_dist_r1(h, T, D):
    """r1: 系列の頭は頭の分布 h、それ以外は前の記号の行 T[前]。"""
    prev = np.where(D.P < 0, 0, D.P)
    dist = T[prev]
    return np.where((D.P < 0)[..., None], h[None, None, :], dist)


# ---------------------------------------------------------------- 擬似残差
def crn_v(seed, ds_no, wseq, col_no, n, model_no=0):
    """共通の乱数（n × 2・x が先）。m46 は 0.5 に固定、m48 はモデルごとに別の流れ。"""
    if "m46" in MUT:
        return np.full((n, 2), 0.5)
    key = [seed + 51, ds_no, wseq, col_no] + ([model_no] if "m48" in MUT else [])
    return np.random.default_rng(key).random((n, 2))


def inv_norm(u):
    return np.array([_ND.inv_cdf(float(x)) for x in u])


def pit_z(dist, obs, v):
    """dist: N × 26 の予測の分布・obs: N 個の観測・v: N × 2。返り値: zx・zy（観測が 25 の時刻は nan）。"""
    N = len(obs)
    zx, zy = np.full(N, np.nan), np.full(N, np.nan)
    ok = obs != RUN
    if not ok.any():
        return zx, zy
    p = dist[ok, :RUN]
    p = p / p.sum(1, keepdims=True)
    P = p.reshape(-1, G, G)  # [x の帯, y の帯]（記号 = x の帯 · 5 + y の帯）
    o = obs[ok]
    marg = {"x": (P.sum(2), o // G), "y": (P.sum(1), o % G)}
    if "m47" in MUT:
        marg = {"x": marg["y"], "y": marg["x"]}
    outs = []
    for j, ax in enumerate(("x", "y")):
        pm, b = marg[ax]
        Fc = np.cumsum(pm, 1)
        hi = Fc[np.arange(len(b)), b]
        lo = np.where(b > 0, Fc[np.arange(len(b)), np.maximum(b - 1, 0)], 0.0)
        U = np.clip(lo + v[ok, j] * (hi - lo), CLIP, 1 - CLIP)
        outs.append(inv_norm(U))
    zx[ok], zy[ok] = outs
    return zx, zy


def acf(z, sid, sel=None):
    """遅れ 1〜10 の自己相関。平均と分母はその書き手の欠けでない z 全部（sel があればその中）。組は同じ系列の中だけ。"""
    ok = ~np.isnan(z) if sel is None else (~np.isnan(z) & sel)
    out = {}
    if ok.sum() < 2:
        return {str(l): None for l in LAGS}
    zb = z[ok].mean()
    den = float(((z[ok] - zb) ** 2).sum())
    for l in LAGS:
        if len(z) <= l or den == 0:
            out[str(l)] = None
            continue
        a = ok[:-l] & ok[l:] & (sid[:-l] == sid[l:])
        out[str(l)] = float(((z[:-l][a] - zb) * (z[l:][a] - zb)).sum() / den) if a.any() else None
    return out


def writer_stats(zx, zy, sid, pf, obs):
    """書き手ごとの量: 遅れ 1〜10 の自己相関・z の平均と分散・25 の割合・欠けでない z の数・押下のある時刻どうしの遅れ 1。"""
    out = dict(share25=float(np.mean(obs == RUN)), n_valid=int((~np.isnan(zx)).sum()))
    for ax, z in (("x", zx), ("y", zy)):
        ok = ~np.isnan(z)
        out["acf_" + ax] = acf(z, sid)
        out["mean_" + ax] = float(z[ok].mean()) if ok.any() else None
        out["var_" + ax] = float(z[ok].var()) if ok.any() else None
        out["acf1_pressed_" + ax] = acf(z, sid, sel=pf)["1"]
    return out


class EvalSeq:
    """評価の単位の系列（空の系列は除く）と、平らにした観測・系列の番号・押下の印。"""

    def __init__(self, units):
        ev = ml.Eval(ml.seqs_of(units), ml.pflags_of(units))
        self.ev, self.D = ev, ev.D
        M = ev.D.M
        self.obs = ev.D.O[M]
        self.sid = np.broadcast_to(np.arange(M.shape[0])[:, None], M.shape)[M]
        self.pf = ev.PF[M]
        self.n = int(M.sum())


def writer_residuals(E, models, seed, ds_no, wseq, col_no, debug=False):
    """models: [(名前, ("model", 母数) か ("r1", (h, T)))]。返り値: {名前: 書き手ごとの量}（debug なら使った v も）。"""
    out = {}
    v = crn_v(seed, ds_no, wseq, col_no, E.n)
    for mi, (name, (typ, m)) in enumerate(models):
        vv = crn_v(seed, ds_no, wseq, col_no, E.n, model_no=mi) if "m48" in MUT else v
        dist = pred_dist_model(m, E.D) if typ == "model" else pred_dist_r1(m[0], m[1], E.D)
        zx, zy = pit_z(dist[E.D.M], E.obs, vv)
        out[name] = writer_stats(zx, zy, E.sid, E.pf, E.obs)
        if debug:
            out[name]["_v"] = vv
            out[name]["_z"] = (zx, zy)
    return out


# ---------------------------------------------------------------- 実データ
def model_list(z, wseq, k, picks):
    """モデル（conditions D4）: 4 構造の同じ構造の共通・4 構造の本人（τ 他人）・2 段（他人）で選ばれた (s, τ) の本人・r1。"""
    out = []
    for s in ml.STRUCTS:
        nm = ml.sname(s)
        out.append(("pool_" + nm, ("model", F.get_pool(z, wseq, nm))))
    for s in ml.STRUCTS:
        nm = ml.sname(s)
        t = picks["tau_other"][nm].get(str(wseq))
        if t is not None:
            out.append(("self_" + nm, ("model", F.get_self(z, wseq, nm, k, t))))
    p = picks["two_stage"].get(str(wseq))
    if p is not None:
        out.append(("two_stage", ("model", F.get_self(z, wseq, p[0], k, p[1]))))
    out.append(("r1", ("r1", F.get_r1(z, wseq, k))))
    return out


def npz_check(E, z, wseq, k, res):
    """P-NPZ（実データ版）: 読み戻した母数の評価の尤度（全記号）が fit.py の値とちょうど一致するか。返り値: (照らした数, 外れた数)。"""
    n, bad = 0, 0
    for s in ml.STRUCTS:
        nm = ml.sname(s)
        n += 1
        bad += int(E.ev.ll(F.get_pool(z, wseq, nm))[0] != res["pool"][nm][0])
        for t in ml.TAUS_FIT:
            n += 1
            bad += int(E.ev.ll(F.get_self(z, wseq, nm, k, str(t)))[0] != res["k"][k]["self"][nm][str(t)][0])
    h, T = F.get_r1(z, wseq, k)
    n += 1
    bad += int(E.ev.ll_r1(h, T)[0] != res["k"][k]["r1"][0])
    return n, bad


def agg(per):
    """per: [書き手ごとの量]。中央値・四分位（inverted_cdf）・人数（6 人未満は伏せる・tau-extend と同じ）。区間は付けない。"""
    out = {}
    for ax in ("x", "y"):
        out["acf_" + ax] = {l: ml.q([p["acf_" + ax][l] for p in per]) for l in map(str, LAGS)}
        for f in ("mean_", "var_", "acf1_pressed_"):
            out[f + ax] = ml.q([p[f + ax] for p in per])
    out["share25"] = ml.q([p["share25"] for p in per])
    out["n_valid"] = ml.q([p["n_valid"] for p in per])
    return out


def run(ds, col, work, side, seed, out, raw_dir, run_id):
    F.check_outside_repo(raw_dir)
    t0 = time.time()
    H_ = ml.DATASETS[ds]["H"]
    pn, nmin, ks = F.PANELS[ds]
    writers = L.load_column(ds, work, side, seed, col)
    base = os.path.join(raw_dir, "unsmoothed_residual_%s.%s.%s")
    WV = json.load(open(base % ("writer_values", ds, col) + ".json"))
    z = np.load(base % ("params", ds, col) + ".npz")
    ns = [len(ss) for ss in writers]
    elig = [i for i, n in enumerate(ns) if n >= H_ + 1]
    S, checked, mism = {}, 0, 0
    per_cell = {str(k): {} for k in ks}
    for wseq in WV["panel"]:
        w = elig[wseq]
        res = WV["results"][str(wseq)]["em"]
        _, test = DT.split(len(writers[w]), 1, H_)
        te = [writers[w][i] for i in test]
        if F.ntok(ml.seqs_of(te)) == 0:
            continue
        E = EvalSeq(te)
        if E.n != res["n_eval"]:
            sys.exit("評価の単位の記号の数が fit.py と違う")
        for k in map(str, ks):
            if res["k"].get(k) is None:
                continue
            c, b = npz_check(E, z, wseq, k, res)
            checked += c
            mism += b
            st = writer_residuals(E, model_list(z, wseq, k, WV["picks"][k]), seed, DS_NO[ds], wseq, L.COLS[col])
            for name, v in st.items():
                per_cell[k].setdefault(name, []).append(v)
    for k in map(str, ks):
        S[k] = dict(models={name: agg(per) for name, per in per_cell[k].items()},
                    writers=len(per_cell[k].get("r1", [])))
    os.makedirs(os.path.join(out, "parts"), exist_ok=True)
    json.dump(dict(run_id=run_id, dataset=ds, column=col, residual={pn: S},
                   npz_check=dict(checked=checked, mismatched=mism), seconds=time.time() - t0),
              open(os.path.join(out, "parts", "res.%s.%s.json" % (ds, col)), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(dict(dataset=ds, column=col, npz_checked=checked, npz_mismatched=mism)))
    return 0 if checked > 0 and mism == 0 else 3


if __name__ == "__main__":
    argv = sys.argv[1:]
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id")
        run_id = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    ds, col, work, side, seed, out, raw_dir = argv[:7]
    sys.exit(run(ds, col, work, None if side == "-" else side, int(seed), out, raw_dir, run_id))
