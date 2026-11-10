"""複製ごとの集計（conditions.md D4）と読みの形の当て（D7）。選びは tau-extend の関数（select_joint・select_other）。
合成の値だけを扱う。6 人未満でも伏せない（合成なので・D4）。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pinned import ml  # noqa: E402

SNAMES = [ml.sname(s) for s in ml.STRUCTS]
TAUS_DESC = sorted(ml.TAU_KEYS, key=ml.tau_val, reverse=True)
MAIN = {"coauthor": ["5", "15"], "cs1": ["5"]}
REAL_REMAINDER = (4.1e-4, 7.2e-4)  # 外枠の CoAuthor 15-session パネルの残り（k = 1〜15）


def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    a = np.array(xs, dtype=float)
    qs = np.quantile(a, [0.25, 0.5, 0.75], method="inverted_cdf")
    return dict(median=float(qs[1]), q25=float(qs[0]), q75=float(qs[2]), better_share=float(np.mean(a > 0)), n=len(xs))


def counts(vs):
    out = {}
    for v in vs:
        out[str(v)] = out.get(str(v), 0) + 1
    return out


def region(taus):
    r = dict(inside=0, low_end=0, high_finite_end=0, inf=0)
    for t in taus:
        if t == ml.INF:
            r["inf"] += 1
        elif t == "0":
            r["low_end"] += 1
        elif t == str(ml.TAUS_FIT[-1]):
            r["high_finite_end"] += 1
        else:
            r["inside"] += 1
    return r


def cell(R, k):
    """1 複製 × k の量。主の量 = 2 段（他人）の本人 − 同じ構造の共通（全記号）。"""
    W = R["writers"]
    ws = list(range(len(W)))
    jv = {v: {(s, t): W[v]["k"][k]["self"][s][t] - W[v]["k"][k]["r1"] for s in SNAMES for t in ml.TAU_KEYS} for v in ws}
    jc = ml.joint_cands()
    pick = {w: ml.select_joint(jv, w, jc) for w in ws}
    d = [W[w]["k"][k]["self"][pick[w][0]][pick[w][1]] - W[w]["pool"][pick[w][0]] for w in ws]
    dr1 = [W[w]["k"][k]["self"][pick[w][0]][pick[w][1]] - W[w]["k"][k]["r1"] for w in ws]
    g = [W[w]["g"] for w in ws]
    C = dict(main=stats(d), vs_r1=stats(dr1), g=stats(g),
             chosen_struct=counts(p[0] for p in pick.values()), chosen_tau=counts(p[1] for p in pick.values()),
             chosen_tau_region=region(p[1] for p in pick.values()),
             n_train=stats([W[w]["k"][k]["n_train"] for w in ws]), per_struct={})
    gm = C["g"]["median"]
    C["recovery"] = (C["main"]["median"] / gm) if R["rep"]["g"] > 0 and gm else None
    for s in SNAMES:
        vals = {v: {t: W[v]["k"][k]["self"][s][t] - W[v]["pool"][s] for t in ml.TAU_KEYS} for v in ws}
        ch = {w: ml.select_other(vals, w, TAUS_DESC) for w in ws}
        C["per_struct"][s] = dict(tau_other=stats([vals[w][ch[w]] for w in ws]), chosen_tau=counts(ch.values()))
    pl = R["planted"]
    if any(pl) and not all(pl):
        C["planted"] = dict(main=stats([d[w] for w in ws if pl[w]]), n=sum(pl),
                            moved=sum(1 for w in ws if pl[w] and pick[w][1] not in (ml.INF, str(ml.TAUS_FIT[-1]), "0")),
                            region=region(pick[w][1] for w in ws if pl[w]),
                            chosen_tau=counts(pick[w][1] for w in ws if pl[w]))
        C["unplanted"] = dict(main=stats([d[w] for w in ws if not pl[w]]), n=len(ws) - sum(pl))
    C["values"] = dict(main=d, g=g)  # 合成の書き手ごとの値（実データではない）
    return C


def summarize(reps):
    """reps: 複製の結果のリスト。返り値: 複製ごとのセルと読み（D7）。"""
    cells = []
    for R in reps:
        r = R["rep"]
        for k in sorted(R["writers"][0]["k"], key=int):
            c = cell(R, k)
            c.update(no=r["no"], strand=r["strand"], shape=r["shape"], K=r["K"], g_target=r["g"], seed=r["seed"], k=k,
                     lam=R["lam"], seconds=R["seconds"]["total"])
            cells.append(c)
    return dict(cells=cells, readings=readings(cells))


def _sel(cells, **kw):
    return [c for c in cells if all(c[a] == b for a, b in kw.items())]


def readings(cells):
    out = dict(dose={}, struct={}, dist={})
    levels = [0.0, 1e-3, 3e-3, 1e-2, 3e-2]
    U = {}
    for shape, ks in MAIN.items():
        for k in ks:
            key = "%s k=%s" % (shape, k)
            null = _sel(cells, strand="dose", shape=shape, k=k, g_target=0.0)
            if not null:
                continue
            u = max(c["main"]["median"] for c in null)
            U[key] = u
            lv = {}
            for g in levels:
                cs = _sel(cells, strand="dose", shape=shape, k=k, g_target=g)
                if not cs:
                    continue
                lv[str(g)] = dict(seeds=len(cs), medians=[c["main"]["median"] for c in cs],
                                  shares=[c["main"]["better_share"] for c in cs],
                                  g_medians=[c["g"]["median"] for c in cs],
                                  recovery=[c["recovery"] for c in cs],
                                  detect=g > 0 and all(c["main"]["median"] > u and c["main"]["better_share"] >= 0.8 for c in cs),
                                  mean_median=float(np.mean([c["main"]["median"] for c in cs])))
            ran = [g for g in levels[1:] if str(g) in lv]
            floor = None
            for i, g in enumerate(ran):
                if all(lv[str(h)]["detect"] for h in ran[i:]):
                    floor = g
                    break
            means = [lv[str(g)]["mean_median"] for g in levels if str(g) in lv]
            out["dose"][key] = dict(levels_run=[str(g) for g in levels if str(g) in lv],
                                    levels_not_run=[str(g) for g in levels if str(g) not in lv], U=u, null_medians=[c["main"]["median"] for c in null], levels=lv, floor=floor,
                                    rises=all(b >= a for a, b in zip(means, means[1:])),
                                    U_vs_real="same order (>= 1e-4)" if u >= 1e-4 else "below 1e-4")
    for k in MAIN["coauthor"]:
        key = "coauthor k=%s" % k
        n5 = _sel(cells, strand="struct", shape="coauthor", k=k, g_target=0.0)
        p5 = _sel(cells, strand="struct", shape="coauthor", k=k, g_target=1e-2)
        if n5 and key in U:
            u5 = max(c["main"]["median"] for c in n5)
            out["struct"][key] = dict(
                null_medians=[c["main"]["median"] for c in n5], U_K3=U[key], U_K5=u5,
                c1_larger_than_K3=all(c["main"]["median"] > U[key] for c in n5),
                c2_detect=bool(p5) and all(c["main"]["median"] > u5 and c["main"]["better_share"] >= 0.8 for c in p5),
                c2_medians=[c["main"]["median"] for c in p5], c2_shares=[c["main"]["better_share"] for c in p5])
        ds = _sel(cells, strand="dist", shape="coauthor", k=k)
        if ds and key in U:
            out["dist"][key] = dict(
                d1_detect=all(c["main"]["median"] > U[key] and c["main"]["better_share"] >= 0.8 for c in ds),
                panel_medians=[c["main"]["median"] for c in ds],
                d2_planted_medians=[c["planted"]["main"]["median"] for c in ds],
                d2_planted_above_U=all(c["planted"]["main"]["median"] > U[key] for c in ds),
                moved=[c["planted"]["moved"] for c in ds], planted_n=[c["planted"]["n"] for c in ds])
    out["real_remainder"] = REAL_REMAINDER
    return out
