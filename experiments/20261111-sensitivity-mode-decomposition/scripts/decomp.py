"""感度の合成の CoAuthor の複製に最頻値の分解を当てる（conditions.md D2〜D5）。合成の値だけ。

- 作り直し: sens の run_rep と同じ手順で合成の書き手・全員の共通・w を除く共通を作り（新しい乱数は引かない）、
  パネルの書き手ごとに pool・g・最頻値の評価を測る。pool と g は sens の複製の JSON とビットまで一致を門にする（P-REPRO）。
- 分解: a = 本人(τ) − 最頻値、b = 最頻値 − 共通、c = 本人(τ) − 共通（書き手ごと）。最頻値が −∞ なら a = +∞・b = −∞。
- 形（mode の形 1〜3・5）と読み（D5）。
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pinned2 import AN, DT, H, HM, RS, SY, ml  # noqa: E402

MUT = set()  # u1: 全員の共通の S̄・u2: w を除く共通の母数・u3: −∞ を捨てる・u4: 確率 0 の扱い無し・u5: 中央値どうしの差
SNAMES = [ml.sname(s) for s in ml.STRUCTS]
ROW_SUB = ["ar1", "ar2", "ar3"]
TAU_SUB = "1000000"
KS = ["1", "5", "15"]
MAIN_KS = ["5", "15"]
LEVELS = [0.0, 1e-3, 3e-3, 1e-2, 3e-2]


# ---------------------------------------------------------------- 最頻値の評価
def mode_model(kind, sb, pool_m, sb_full=None):
    """最頻値の母数。u1 は全員の共通の S̄、u2 は w を除く共通の母数をそのまま使う。"""
    if "u2" in MUT:
        return pool_m
    m, _ = HM.mode_of(kind, sb_full if ("u1" in MUT and sb_full is not None) else sb)
    return m


def mode_eval(m, seqs):
    """1 記号あたりの平均の対数尤度（mode の Eval.ll_zero の全記号と同じ）。確率 0 の後は −∞。u4 は pred_logprob（NaN の道）。"""
    D = HM.Data([s for s in seqs if len(s)])
    with np.errstate(divide="ignore", invalid="ignore"):
        lp = HM.pred_logprob(m, D) if "u4" in MUT else HM.pred_logprob_zero(m, D)
    return float(lp[D.M].sum() / D.M.sum())


# ---------------------------------------------------------------- 作り直し（1 複製）
def rebuild(r, cal, m0s, seed, jobs, want_full_sb=False):
    """返り値: (書き手ごとの {pool, g, mode, n_eval}, 全員の共通の診断)。sens の run_rep と同じ乱数・同じ呼び方。"""
    sh = SY.SHAPES[r["shape"]]
    assert sh["H"] == ml.DATASETS[sh["ds"]]["H"]  # run_rep と同じ照らし（レビュー LOW 13）
    lam = cal[r["K"]][str(r["g"])]["lam"] if r["g"] > 0 else 0.0
    writers, models, lams, P = SY.build(r["shape"], r["K"], r["seed"], SY.lam_rule(r["strand"], lam), m0s[r["K"]], seed)
    ds, H_ = sh["ds"], sh["H"]
    ex = ProcessPoolExecutor(jobs, initializer=RS._init, initargs=(ds, writers, [], []))
    full = list(ex.map(RS.fit_full, [dict(si=si, seed=seed, no=r["no"], H=H_) for si in range(len(ml.STRUCTS))]))
    pj = [dict(ds=ds, w=w, start=full[si][0]) for w in range(P) for si in range(len(ml.STRUCTS))]
    pres = list(ex.map(RS.fit_excl, pj, chunksize=1))
    ex.shutdown()
    full_sb = {}
    if want_full_sb or "u1" in MUT:
        seqs_all = ml.seqs_of(ml.pool_units(writers, H_))
        Dall = H.Batched(seqs_all, chunk=H.CHUNK)
        for si, s in enumerate(ml.STRUCTS):
            S, _ = H.counts(full[si][0], Dall)
            full_sb[ml.sname(s)] = H.sbar_of(S, Dall.nobs)
    out, it = [], iter(pres)
    for w in range(P):
        units = writers[w]
        _, test = DT.split(len(units), 1, H_)
        ev_units = [units[i] for i in test]
        ev_seqs = ml.seqs_of(ev_units)
        ev = ml.Eval(ev_seqs, ml.pflags_of(ev_units))
        o = dict(pool={}, mode={}, mode_full_sb={}, n_eval=int(ev.D.M.sum()))
        pools = {}
        for s in ml.STRUCTS:
            m, sb, _ = next(it)
            name = ml.sname(s)
            pools[name] = m
            o["pool"][name] = ev.ll(m)[0]
            o["mode"][name] = mode_eval(mode_model(s[0], sb, m, full_sb.get(name)), ev_seqs)
            if want_full_sb:
                o["mode_full_sb"][name] = mode_eval(HM.mode_of(s[0], full_sb[name])[0], ev_seqs)
        o["g"] = SY.gain(models[w], m0s[r["K"]], ev_seqs, ref=pools.get("ar3"))
        out.append(o)
    diag = {ml.sname(s): dict(winner=d["winner"], nonconv=d["nonconv"]) for s, (_, d) in zip(ml.STRUCTS, full)}
    if want_full_sb:  # selftest だけ: 独立の照らしに使う
        return out, diag, dict(writers=writers, full=[f[0] for f in full], P=P, H=H_, ds=ds)
    return out, diag


# ---------------------------------------------------------------- 分解
def abc(self_v, mode_v, pool_v):
    """書き手ごとの a・b・c。最頻値が −∞ なら a = +∞・b = −∞（mode の判断 4・9）。"""
    if mode_v == -np.inf:
        return np.inf, -np.inf, self_v - pool_v
    return self_v - mode_v, mode_v - pool_v, self_v - pool_v


def stats(xs):
    """中央値・四分位（inverted_cdf）・良い側の割合・±∞ の人数。u3 は −∞ と +∞ を捨てる。"""
    xs = [x for x in xs if x is not None]
    if "u3" in MUT:
        xs = [x for x in xs if np.isfinite(x)]
    if not xs:
        return None
    a = np.array(xs, dtype=float)
    if np.isnan(a).any():
        raise ValueError("NaN が出た（コードの誤り）")
    qs = np.quantile(a, [0.25, 0.5, 0.75], method="inverted_cdf")
    return dict(median=float(qs[1]), q25=float(qs[0]), q75=float(qs[2]), better_share=float(np.mean(a > 0)), n=len(xs),
                pos_inf=int(np.sum(a == np.inf)), neg_inf=int(np.sum(a == -np.inf)))


def row_stats(trip):
    """trip: 書き手ごとの (a, b, c)。主の集計と「有限」の集計。u5 は a を中央値どうしの差で配る。"""
    A = [t[0] for t in trip]
    B = [t[1] for t in trip]
    C = [t[2] for t in trip]
    if "u5" in MUT:
        cm = float(np.median(C))
        bm = float(np.median(B))
        A = [cm - bm] * len(A)
    fin = [i for i, t in enumerate(trip) if np.isfinite(t[1])]
    return dict(a=stats(A), b=stats(B), c=stats(C), values=dict(a=A, b=B, c=C),
                finite=dict(n=len(fin), a=stats([A[i] for i in fin]), b=stats([B[i] for i in fin]),
                            c=stats([C[i] for i in fin])))


def pick_joint(W, k):
    """2 段（他人）: sens の analysis.cell と同じ値と関数。"""
    ws = list(range(len(W)))
    jv = {v: {(s, t): W[v]["k"][k]["self"][s][t] - W[v]["k"][k]["r1"] for s in SNAMES for t in ml.TAU_KEYS} for v in ws}
    jc = ml.joint_cands()
    return {w: ml.select_joint(jv, w, jc) for w in ws}


def cell(R, M, k):
    """R: sens の複製の JSON・M: 作り直しの書き手ごとの値。返り値: 主の 2 段の行と副の 10^6 の行。"""
    W = R["writers"]
    ws = list(range(len(W)))
    pick = pick_joint(W, k)
    # 共通は作り直しの値（M）を使う（P-REPRO で sens と同じ・P-SAME が作り直しにも依存するように・レビュー LOW 8）
    trip = [abc(W[w]["k"][k]["self"][pick[w][0]][pick[w][1]], M[w]["mode"][pick[w][0]], M[w]["pool"][pick[w][0]])
            for w in ws]
    two = row_stats(trip)
    two["chosen_struct"] = AN.counts(p[0] for p in pick.values())
    two["chosen_tau"] = AN.counts(p[1] for p in pick.values())
    two["n_inf"] = sum(1 for p in pick.values() if p[1] == ml.INF)
    sub = {s: row_stats([abc(W[w]["k"][k]["self"][s][TAU_SUB], M[w]["mode"][s], M[w]["pool"][s]) for w in ws])
           for s in ROW_SUB}
    C = dict(two_stage=two, tau_1e6=sub)
    pl = R["planted"]
    if any(pl) and not all(pl):
        C["planted_a"] = stats([trip[w][0] for w in ws if pl[w]])
        C["unplanted_a"] = stats([trip[w][0] for w in ws if not pl[w]])
    return C


def form(row, two_stage=False, n=None):
    """mode の形 1〜3・5（conditions.md D4）。返り値: (形, どちらで読んだか)。"""
    if two_stage and n is not None and row.get("n_inf", 0) * 2 > n:
        return "読まない（a = −b）", "main"
    a, b, c = row["a"], row["b"], row["c"]
    src = "main"
    if not (np.isfinite(a["median"]) and np.isfinite(b["median"])):
        F = row["finite"]
        if F["n"] < 4:
            return "読まない（有限 4 人未満）", "finite"
        a, b, c, src = F["a"], F["b"], F["c"], "finite"
    am, bm, cm = a["median"], b["median"], c["median"]
    if abs(am) < abs(bm) and cm != 0 and np.sign(bm) == np.sign(cm):
        return "1", src
    if abs(am) > abs(bm) and am > 0 and a["better_share"] > 0.5:
        return "2", src
    return "3", src


# ---------------------------------------------------------------- 読み（D5）
def readings(cells):
    """cells: [{no, strand, K, g_target, seed, k, two_stage, tau_1e6, form...}]。
    本数（陰性対照 5 種・各段 2 種）が D5 と違えば読みを出さない（レビュー LOW 7）。"""
    out = dict(main={}, take_home=None)
    sel = lambda **kw: [c for c in cells if all(c[x] == y for x, y in kw.items())]  # noqa: E731
    want = {0.0: 5, 1e-3: 2, 3e-3: 2, 1e-2: 2, 3e-2: 2}
    got = {g: len(sel(strand="dose", k="15", g_target=g)) for g in want}
    if got != want:
        out["note"] = "本数が D5 と違うので読みを出さない: %r" % got
        return out
    for k in MAIN_KS:
        null = sel(strand="dose", k=k, g_target=0.0)
        n1 = bool(null) and all(c["form"] == "1" for c in null)
        lv = {}
        for g in LEVELS:
            cs = sel(strand="dose", k=k, g_target=g)
            if cs:
                lv[str(g)] = dict(forms=[c["form"] for c in cs], all2=all(c["form"] == "2" for c in cs),
                                  all1=all(c["form"] == "1" for c in cs))
        ran = [g for g in LEVELS[1:] if str(g) in lv]
        D = None
        for i, g in enumerate(ran):
            if all(lv[str(h)]["all2"] for h in ran[i:]):
                D = g
                break
        out["main"]["k=" + k] = dict(N1=n1, null_forms=[c["form"] for c in null], levels=lv, D=D)
    m15, m5 = out["main"].get("k=15"), out["main"].get("k=5")
    if m15 is None or m5 is None:
        return out
    if not m15["N1"] or m15["D"] is None:
        out["take_home"] = "やめる"
    elif m15["D"] == 1e-3 and m5["N1"] and m5["D"] == 1e-3:
        out["take_home"] = "残す"
    else:
        out["take_home"] = "弱める"
    return out


def summarize(pairs):
    """pairs: [(sens の複製 R, 作り直し M)]。返り値: セルと読み。"""
    cells = []
    for R, M in pairs:
        r = R["rep"]
        n = len(R["writers"])
        for k in KS:
            C = cell(R, M, k)
            f, src = form(C["two_stage"], two_stage=True, n=n)
            C.update(no=r["no"], strand=r["strand"], K=r["K"], g_target=r["g"], seed=r["seed"], k=k, form=f, form_src=src,
                     forms_1e6={s: form(C["tau_1e6"][s])[0] for s in ROW_SUB},
                     mode_neg_inf={s: int(sum(M[w]["mode"][s] == -np.inf for w in range(n))) for s in SNAMES})
            cells.append(C)
    return dict(cells=cells, readings=readings(cells))
