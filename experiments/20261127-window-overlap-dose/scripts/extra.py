"""足す量（conditions D4）: M と M_shuf・D_s・ρ_h（共有 hmm3・本人 hmm3）・頭を除く採点。当てはめはしない
（drive.py fit が書いた npz と選びを読む）。書き手ごとの値は repo の外、集計（数だけ）は parts に書く。

- M: パネルの書き手の評価の単位の記号で、系列の中の隣り合う組だけから数えた遅れ 1 の相互情報量（nats）。
  Miller–Madow: (使われた組のセルの数 − 使われた左の記号の数 − 使われた右の記号の数 + 1) / (2 · 組の数) を引く。
  周辺は組の左と右から取る。M_shuf は各系列の中で並べ替えた同じ量の 20 回の平均（乱数 [SEED + 61, c, 書き手の通し番号, r]）。
- D_s = 共有 ar1 − 共有 hmm3（どちらも w を除く共有・w の評価の単位で採点）。fit の葉と npz の読み戻しの両方で作り、ちょうど一致を確かめる。
- ρ_h: S13 の residual.py の擬似残差（同じ v の流れ [SEED + 51, 0, 書き手の通し番号, c]）の遅れ 1 の自己相関（x・y）と有効な組の割合。
- 頭を除く採点: 各系列の最初の記号を除いた 1 記号あたりの対数尤度（本人 hmm3（τ 他人）・共有 hmm3・r1）。
変異: m65 系列の境目をまたいで組を数える／m66 周辺を全記号の頻度で取る／m67 頭を除かずに分母だけ減らす／
m72 D_s に全員の共有（w を含む）を使う／m77 M_shuf を系列をまたいで並べ替える／m80 M_shuf を 1 回の並べ替えにする。
"""
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swap  # noqa: E402,F401
from swap import F, R, load_dose as LD  # noqa: E402
from pinned import DT, H, ml  # noqa: E402

NSYM = 26
NPERM = 20
MUT = set()


def set_mut(mut):
    MUT.clear()
    MUT.update(mut)


# ---------------------------------------------------------------- M
def pairs_of(seqs):
    seqs = [np.asarray(s, dtype=np.int64) for s in seqs if len(s)]
    if "m65" in MUT:
        flat = np.concatenate(seqs) if seqs else np.zeros(0, dtype=np.int64)
        return flat[:-1], flat[1:]
    a = [s[:-1] for s in seqs]
    b = [s[1:] for s in seqs]
    if not a:
        return np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int64)
    return np.concatenate(a), np.concatenate(b)


def mi_mm(seqs):
    """返り値: dict(mm, plugin, pairs, cells, left, right)。組が 0 なら None。"""
    a, b = pairs_of(seqs)
    N = len(a)
    if N == 0:
        return None
    J = np.bincount(a * NSYM + b, minlength=NSYM * NSYM).reshape(NSYM, NSYM).astype(np.float64)
    if "m66" in MUT:
        allsym = np.concatenate([np.asarray(s, dtype=np.int64) for s in seqs if len(s)])
        pa = pb = np.bincount(allsym, minlength=NSYM) / len(allsym)
    else:
        pa, pb = J.sum(1) / N, J.sum(0) / N
    nz = J > 0
    ii, jj = np.nonzero(nz)
    pj = J[nz] / N
    plugin = float(np.sum(pj * np.log(pj / (pa[ii] * pb[jj]))))
    cells, left, right = int(nz.sum()), int((J.sum(1) > 0).sum()), int((J.sum(0) > 0).sum())
    mm = plugin - (cells - left - right + 1) / (2.0 * N)
    return dict(mm=mm, plugin=plugin, pairs=int(N), cells=cells, left=left, right=right)


def shuffled(seqs, rng):
    seqs = [np.asarray(s, dtype=np.int64) for s in seqs if len(s)]
    if "m77" in MUT:
        flat = rng.permutation(np.concatenate(seqs))
        out, i = [], 0
        for s in seqs:
            out.append(flat[i:i + len(s)])
            i += len(s)
        return out
    return [rng.permutation(s) for s in seqs]


def m_shuf(seqs, seed, c, wseq):
    """返り値: (平均, 標準偏差（ddof = 1）, 各回の値)。"""
    vals = []
    for r in range(1 if "m80" in MUT else NPERM):
        rng = np.random.default_rng([seed + 61, c, wseq, r])
        d = mi_mm(shuffled(seqs, rng))
        vals.append(None if d is None else d["mm"])
    if any(v is None for v in vals):
        return None, None, vals
    a = np.array(vals)
    return float(a.mean()), (float(a.std(ddof=1)) if len(a) > 1 else float("nan")), vals


def entropy(seqs):
    allsym = np.concatenate([np.asarray(s, dtype=np.int64) for s in seqs if len(s)])
    p = np.bincount(allsym, minlength=NSYM) / len(allsym)
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def m_record(seqs, seed, c, wseq):
    seqs = [s for s in seqs if len(s)]
    d = mi_mm(seqs)
    out = dict(n_series=len(seqs), const_series=int(sum(1 for s in seqs if np.all(np.asarray(s) == s[0]))),
               entropy=entropy(seqs) if seqs else None, M=None, M_shuf=None, M_shuf_sd=None, M_diff=None)
    if d is None:
        return out
    ms, sd, _ = m_shuf(seqs, seed, c, wseq)
    out.update(M=d["mm"], M_plugin=d["plugin"], pairs=d["pairs"], cells=d["cells"], M_shuf=ms, M_shuf_sd=sd)
    if ms is not None and math.isfinite(d["mm"]) and math.isfinite(ms):
        out["M_diff"] = d["mm"] - ms
    return out


# ---------------------------------------------------------------- D_s
def ds_leaf(res):
    p = res["pool"]
    return p["ar1"][0] - p["hmm3"][0]


def ds_readback(ev, z, wseq, full=None):
    """w を除く共有 ar1 − w を除く共有 hmm3（npz から読み戻して採点）。m72 は全員の共有（full: {構造名: 母数}）。"""
    if "m72" in MUT and full is not None:
        a, b = full["ar1"], full["hmm3"]
    else:
        a, b = F.get_pool(z, wseq, "ar1"), F.get_pool(z, wseq, "hmm3")
    return ev.ll(a)[0] - ev.ll(b)[0]


# ---------------------------------------------------------------- ρ_h
def rho(E, m, seed, wseq, c):
    st = R.writer_residuals(E, [("m", ("model", m))], seed, 0, wseq, c, debug=True)["m"]
    zx, zy = st["_z"]
    same = E.sid[:-1] == E.sid[1:]
    possible = int(same.sum())
    out = dict(x=st["acf_x"]["1"], y=st["acf_y"]["1"], possible_pairs=possible)
    for ax, zz in (("x", zx), ("y", zy)):
        ok = ~np.isnan(zz)
        used = int((ok[:-1] & ok[1:] & same).sum())
        out["valid_" + ax] = used / possible if possible else None
    return out


# ---------------------------------------------------------------- 頭を除く採点
def lp_r1(ev, h, T):
    lp = np.zeros(ev.D.M.shape)
    for i, s in enumerate(ev.seqs):
        s = np.asarray(s)
        lp[i, 0] = np.log(h[s[0]])
        lp[i, 1:len(s)] = np.log(T[s[:-1], s[1:]])
    return lp


def nohead(ev, lp):
    """返り値: (頭を除いた対数尤度の和（math.fsum）, 記号の数)。m67 は頭を除かずに分母だけ減らす。"""
    M = ev.D.M
    head = M & (ev.D.P < 0)
    keep = M if "m67" in MUT else (M & ~head)
    return math.fsum(lp[keep].tolist()), int(M.sum() - head.sum())


# ---------------------------------------------------------------- 本計算
def run(col, work, side, seed, out, raw_dir, run_id):
    F.check_outside_repo(raw_dir)
    t0 = time.time()
    H_ = ml.DATASETS["coauthor"]["H"]
    ks = F.PANELS["coauthor"][2]
    c = LD.COLS[col]
    writers = LD.load_column("coauthor", work, side, seed, col)
    base = os.path.join(raw_dir, "unsmoothed_residual_%s.%s.%s")
    WV = json.load(open(base % ("writer_values", "coauthor", col) + ".json"))
    if WV.get("run_id") != run_id:
        sys.exit("書き手ごとの値の run_id が今回の実行と違う（別の実行の当てはめを読んでいる）")
    z = np.load(base % ("params", "coauthor", col) + ".npz")
    ns = [len(ss) for ss in writers]
    elig = [i for i, n in enumerate(ns) if n >= H_ + 1]
    per, ds_checked, ds_bad = {}, 0, 0
    for wseq in WV["panel"]:
        w = elig[wseq]
        res = WV["results"][str(wseq)]["em"]
        _, test = DT.split(len(writers[w]), 1, H_)
        te = [writers[w][i] for i in test]
        seqs = [s for s in ml.seqs_of(te) if len(s)]
        rec = m_record(seqs, seed, c, wseq)
        rec["k"] = {}
        if not seqs:
            per[str(wseq)] = rec
            continue
        E = R.EvalSeq(te)
        if E.n != res["n_eval"]:
            sys.exit("評価の単位の記号の数が fit.py と違う")
        leaf, rb = ds_leaf(res), ds_readback(E.ev, z, wseq)
        ds_checked += 1
        ds_bad += int(leaf != rb)
        rec["D_s"] = leaf
        pool = F.get_pool(z, wseq, "hmm3")
        rec["rho_pool_hmm3"] = rho(E, pool, seed, wseq, c)
        s_pool, cnt = nohead(E.ev, H.pred_logprob(pool, E.D))
        for k in map(str, ks):
            if res["k"].get(k) is None:
                continue
            t = WV["picks"][k]["tau_other"]["hmm3"].get(str(wseq))
            if t is None:
                continue
            ms = F.get_self(z, wseq, "hmm3", k, t)
            s_self, _ = nohead(E.ev, H.pred_logprob(ms, E.D))
            s_r1, _ = nohead(E.ev, lp_r1(E.ev, *F.get_r1(z, wseq, k)))
            rec["k"][k] = dict(rho_self_hmm3=rho(E, ms, seed, wseq, c),
                               G_nohead=(s_self - s_pool) / cnt if cnt else None,
                               C2a_nohead=(s_self - s_r1) / cnt if cnt else None, n_nohead=cnt)
        per[str(wseq)] = rec
    z.close()
    lens_all = [len(s) for ss in writers for u in ss for s in u["seqs"]]
    lens_panel = [len(s) for wseq in WV["panel"] for u in writers[elig[wseq]] for s in u["seqs"]]
    path = os.path.join(raw_dir, "extra_writer_values.coauthor.%s.json" % col)
    F.check_outside_repo(path)
    json.dump(dict(run_id=run_id, column=col, writers=per), open(path, "w"))
    agg = dict(run_id=run_id, dataset="coauthor", column=col, ds_check=dict(checked=ds_checked, mismatched=ds_bad),
               series_total=len(lens_all), series_over_chunk=int(sum(1 for n in lens_all if n > H.CHUNK)),
               panel_series_rows_median=ml.q(lens_panel), seconds=time.time() - t0)
    os.makedirs(os.path.join(out, "parts"), exist_ok=True)
    json.dump(agg, open(os.path.join(out, "parts", "extra.coauthor.%s.json" % col), "w", encoding="utf-8"), indent=1)
    print(json.dumps(dict(column=col, ds_checked=ds_checked, ds_mismatched=ds_bad)))
    return 0 if ds_checked > 0 and ds_bad == 0 else 3
