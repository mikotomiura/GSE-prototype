#!/usr/bin/env python3
"""notes.md §1 に残った未解決 3 件について、候補定義を総当たりする**調査**スクリプト。

本体 (`diagnostics.py`) には混ぜない。総当たりの結論が出てから本体を直す。
定義の二重化を避けるため、ロード・φ・C-index・窓集約は `diagnostics.py` から import する。

対象:
  P1  `.idea` §1.1「並べ替え検定 68 件」  — セル数の定義
  P2  `.idea` §1.3「実 X と 0.25·φ(F1) の相関 r=0.78」— 相関の取り方
  P3  `.idea` §1.4「ICC f1=0.060 f3=0.055 f4=0.159 f5=0.156」— 式と前処理

usage: probe_variants.py <raw_root> <constants.json> <out_dir>

乱数は使わない (総当たりは決定論的)。出力は集計値のみで、書き出し前に
`diagnostics.assert_no_pii()` を通す。
"""
import collections
import json
import math
import os
import statistics
import sys

import diagnostics as D

# ---------------------------------------------------------------- 対象の記載値
IDEA = {
    "P1_permutation_cells": 68,
    "P2_r_x_vs_phi1": 0.78,
    "P3_icc": {"f1": 0.060, "f3": 0.055, "f4": 0.159, "f5": 0.156},
}

# feat イベントに載っている特徴量フィールド (per_feature_cindex.py の FEATS と同一)
FEAT_FIELDS = ["f1", "f3", "f4", "f5", "f6", "raw_x", "raw_y",
               "ewma_x", "ewma_y", "p_stuck", "p_flow", "p_inc"]
# 窓集約でのみ作られる「収集済みだが未使用」の信号 (.idea §1.5)
EXTRA_FIELDS = ["keys", "bs_rate", "paste_count", "paste_chars", "ime_dwell_med"]

PHI_FEATS = ["f1", "f3", "f5", "f6"]          # X の合成に入る 4 項
ICC_FEATS = ["f1", "f3", "f4", "f5", "f6"]


# ================================================================ 共通ユーティリティ
def pearson(a, b):
    """None を含むペアを落としてから Pearson 相関。落とした件数も返す。"""
    xs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(xs) < 2:
        return None, len(xs)
    ma = statistics.fmean(x for x, _ in xs)
    mb = statistics.fmean(y for _, y in xs)
    num = sum((x - ma) * (y - mb) for x, y in xs)
    da = math.sqrt(sum((x - ma) ** 2 for x, _ in xs))
    db = math.sqrt(sum((y - mb) ** 2 for _, y in xs))
    if not da or not db:
        return None, len(xs)
    return num / (da * db), len(xs)


def _mean_fisher_z(rs):
    """Fisher z 変換して平均し、r に戻す。相関の群平均の定石。

    |r|=1 は z が発散するのでわずかに内側へ寄せる (本データでは発生しないが、
    黙って inf を平均して nan を返すより落ちない形にしておく)。
    """
    zs = []
    for r in rs:
        r = min(max(r, -0.999999999999), 0.999999999999)
        zs.append(0.5 * math.log((1 + r) / (1 - r)))
    return math.tanh(statistics.fmean(zs))


def _average_rank(vals):
    """同順位は平均順位 (Spearman の標準的な tie 処理)。"""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for t in range(i, j + 1):
            ranks[order[t]] = avg
        i = j + 1
    return ranks


def spearman(a, b):
    xs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(xs) < 2:
        return None, len(xs)
    ra = _average_rank([x for x, _ in xs])
    rb = _average_rank([y for _, y in xs])
    return pearson(ra, rb)[0], len(xs)


def group_stats(vals):
    """(n, mean, 偏差平方和)。2 パスで計算し `Σx² − (Σx)²/n` の桁落ちを避ける。"""
    n = len(vals)
    if n == 0:
        return None
    m = statistics.fmean(vals)
    ss = sum((v - m) ** 2 for v in vals)
    return n, m, ss


def anova(stats):
    """群ごとの (n, mean, ss) から一元配置 ANOVA の要約を作る。

    群サイズが不均衡なので k0 (Snedecor & Cochran) も出す。
    総当たりの各組み合わせはこの要約から O(k) で導ける。
    """
    stats = [s for s in stats if s and s[0] >= 1]
    k = len(stats)
    n_total = sum(s[0] for s in stats)
    if k < 2 or n_total <= k:
        return None
    grand = sum(s[0] * s[1] for s in stats) / n_total
    ssb = sum(s[0] * (s[1] - grand) ** 2 for s in stats)
    ssw = sum(s[2] for s in stats)
    msb = ssb / (k - 1)
    msw = ssw / (n_total - k)
    k0 = (n_total - sum(s[0] ** 2 for s in stats) / n_total) / (k - 1)
    return {"k": k, "n": n_total, "ssb": ssb, "ssw": ssw, "sst": ssb + ssw,
            "msb": msb, "msw": msw, "k0": k0, "kbar": n_total / k}


# ================================================================ P1: セル数の定義
def p1_cell_counts(subjects, label_source, label_answered):
    """`.idea` §1.1 の「並べ替え検定 68 件」を再現する数え方を探す。

    セルの算出可能性 (= 並べ替え検定が走るか) は
      比較可能ペア ≥ 2 かつ ラベル水準 ≥ 2
    で決まる (`diagnostics.perm_p` / `FastCIndex.evaluate` の None 条件と同値)。
    """
    # feat 由来の 12 項目を明示的に渡す
    # (extra 5 項目は window_rows が別途 row に足すので、合わせて 17 項目になる)
    per, counts = D.window_rows(subjects, label_source, label_answered,
                                feats=FEAT_FIELDS)

    feats_all = FEAT_FIELDS + EXTRA_FIELDS
    pids = sorted(per)
    targets = {"Q1": "__q1", "Q2": "__q2"}

    # (feature, subject, target) → 算出可能か / n / ラベル水準数
    matrix = {}
    for f in feats_all:
        for pid in pids:
            for tname, tkey in targets.items():
                q = per[pid][tkey]
                v = per[pid].get(f, [])
                pairs = [(a, b) for a, b in zip(v, q) if a is not None]
                lv = len(set(b for _, b in pairs))
                matrix[(f, pid, tname)] = {
                    "n": len(pairs), "q_levels": lv,
                    "computable": len(pairs) >= 2 and lv >= 2,
                }

    def pooled_computable(f, subs, tkey):
        pairs = []
        for pid in subs:
            q = per[pid][tkey]
            v = per[pid].get(f, [])
            pairs += [(a, b) for a, b in zip(v, q) if a is not None]
        return len(pairs) >= 2 and len(set(b for _, b in pairs)) >= 2

    # ---- 意味のある名前付き集合だけを列挙する。
    # 任意の特徴量部分集合まで許すと 68 を作る組み合わせは無数にあり、
    # 「一致した」と言っても定義の復元にならない。
    FEATURE_SETS = {
        "phi5 (f1,f3,f4,f5,f6)": ICC_FEATS,
        "core7 (現行 diagnostics.FEATS)": ["f1", "f3", "f4", "f5", "f6", "raw_x", "raw_y"],
        "xset6 (Q1 対象の X 系・現行定義)": ["f1", "f3", "f4", "f5", "f6", "raw_x"],
        "xset5 (f4 を除く X 系)": ["f1", "f3", "f5", "f6", "raw_x"],
        "orig12 (per_feature_cindex.py)": FEAT_FIELDS,
        "diag12 (core7 + extra5)": ["f1", "f3", "f4", "f5", "f6", "raw_x", "raw_y"] + EXTRA_FIELDS,
        "extra5 (収集済み未使用)": EXTRA_FIELDS,
        "phi5+extra5": ICC_FEATS + EXTRA_FIELDS,
        "all17 (orig12 + extra5)": feats_all,
    }
    SUBJECT_SETS = {f"all{len(pids)}": pids}
    for drop in pids:
        SUBJECT_SETS[f"drop_{drop} ({len(pids) - 1}名)"] = [p for p in pids if p != drop]
    TARGET_SETS = {"Q1のみ": ["Q1"], "Q2のみ": ["Q2"], "Q1+Q2": ["Q1", "Q2"]}

    rows = []
    for fname, fs in FEATURE_SETS.items():
        for sname, subs in SUBJECT_SETS.items():
            for tname, ts in TARGET_SETS.items():
                n_all = len(fs) * len(subs) * len(ts)
                n_ok = sum(1 for f in fs for s in subs for t in ts
                           if matrix[(f, s, t)]["computable"])
                n_pool_all = len(fs) * len(ts)
                n_pool_ok = sum(1 for f in fs for t in ts
                                if pooled_computable(f, subs, targets[t]))
                for count_mode, base, pool in (
                        ("全セル", n_all, n_pool_all),
                        ("算出可能のみ", n_ok, n_pool_ok)):
                    for pooled in (False, True):
                        rows.append({
                            "features": fname, "n_features": len(fs),
                            "subjects": sname, "n_subjects": len(subs),
                            "targets": tname, "n_targets": len(ts),
                            "count_mode": count_mode, "pooled": pooled,
                            "count": base + (pool if pooled else 0),
                        })

    matches = [r for r in rows if r["count"] == IDEA["P1_permutation_cells"]]

    # ---- 構造的な解 (「全セル」で数えた場合は集合の中身に依らず個数だけで決まる)
    # count = |F|·|S|·|T| (+ pooled なら |F|·|T|) = 68 の整数解を全部出す。
    structural = []
    for nf in range(1, 41):
        for ns in range(1, 6):
            for nt in (1, 2):
                for pooled in (False, True):
                    c = nf * ns * nt + (nf * nt if pooled else 0)
                    if c == IDEA["P1_permutation_cells"]:
                        structural.append({"n_features": nf, "n_subjects": ns,
                                           "n_targets": nt, "pooled": pooled})

    return {
        "label_windows": dict(counts),
        "subjects": pids,
        "matrix_summary": {
            "cells_total": len(matrix),
            "n_features": len(feats_all), "n_subjects": len(pids), "n_targets": len(targets),
            "computable": sum(1 for v in matrix.values() if v["computable"]),
            "uncomputable_detail": sorted(
                [f"{f}/{p}/{t}(n={v['n']},lv={v['q_levels']})"
                 for (f, p, t), v in matrix.items() if not v["computable"]]),
        },
        "rows": rows,
        "matches": matches,
        "structural_solutions": structural,
    }


# ================================================================ 標本テーブル
def build_samples(subjects, const, label_source, label_answered):
    """feat 1 件 = 1 行の並列配列。X 候補と φ 項候補を全部持たせる。

    抽出条件は `diagnostics.d2_d3` の D3 と同じ (φ 5 特徴量 + raw_x が揃う行) にする。
    ここを変えると現行値 0.763 を基準に置けなくなる。
    """
    phi = D.make_phi(const["kappa"])
    b = const["beta"]
    wx = const["weights_x"]
    keys = (["pid", "sid", "x_logged", "ewma_x",
             "x_recalc_writing", "x_real"]
            + [f"w_{f}" for f in PHI_FEATS] + [f"r_{f}" for f in PHI_FEATS])
    S = {k: [] for k in keys}
    W = {k: [] for k in keys}       # ラベル窓集約 (n=200)

    for pid, sessions in subjects.items():
        for si, s in enumerate(sessions):
            ev = s["ev"]
            feats = sorted(ev.get("feat", []), key=lambda o: o["t"])
            ime_states = sorted(ev.get("ime_state", []), key=lambda o: o["t"])
            ime_open = D.ime_open_series(ime_states, feats)
            loc = {k: [] for k in keys}
            times = []
            for o, is_open in zip(feats, ime_open):
                if not all(f in o for f in D.PHI_FEATS) or "raw_x" not in o:
                    continue
                ctx_real = "WRITING" if is_open else "CODING"

                def term(f, ctx):
                    return wx[f"phi{f[1]}"] * phi(o[f], b[f"BETA_{ctx}_{f.upper()}"])

                w = {f: term(f, "WRITING") for f in PHI_FEATS}
                r = {f: term(f, ctx_real) for f in PHI_FEATS}
                # 加算順を diagnostics.d2_d3 の compose (phi3+phi6+phi1+phi5) に揃える。
                # 4 桁表示では見えないが、「本体の再現」を名乗る以上は同じ順にする。
                def comp(d):
                    return min(max(d["f3"] + d["f6"] + d["f1"] + d["f5"], 0.0), 1.0)
                loc["pid"].append(pid)
                loc["sid"].append(f"{pid}#{si}")
                loc["x_logged"].append(o["raw_x"])
                loc["ewma_x"].append(o.get("ewma_x"))
                loc["x_recalc_writing"].append(comp(w))
                loc["x_real"].append(comp(r))
                for f in PHI_FEATS:
                    loc[f"w_{f}"].append(w[f])
                    loc[f"r_{f}"].append(r[f])
                times.append(o["t"])
            for k in keys:
                S[k] += loc[k]

            # ---- ラベル窓集約 (窓内中央値)
            labels = [o for o in ev.get("realtime_label", [])
                      if o.get("source") == label_source
                      and o.get("answered") is label_answered]
            for lb in labels:
                ws, we = lb["analysis_window_start_ms"], lb["analysis_window_end_ms"]
                idx = [i for i, t in enumerate(times) if ws <= t <= we]
                if not idx:
                    continue
                W["pid"].append(pid)
                W["sid"].append(f"{pid}#{si}")
                for k in keys:
                    if k in ("pid", "sid"):
                        continue
                    vs = [loc[k][i] for i in idx if loc[k][i] is not None]
                    W[k].append(statistics.median(vs) if vs else None)
    return S, W


# ================================================================ P2: 相関の取り方
def p2_correlations(S, W):
    """`.idea` §1.3「実 X と 0.25·φ(F1) の相関は r=0.78」を作る条件を探す。"""
    X_CANDS = ["x_logged", "x_recalc_writing", "x_real", "ewma_x"]
    TERM_CANDS = ([(f"w_{f}", f"0.25·φ({f.upper()}) β_writing固定") for f in PHI_FEATS]
                  + [(f"r_{f}", f"0.25·φ({f.upper()}) 実β") for f in PHI_FEATS])
    CORRS = {"pearson": pearson, "spearman": spearman}

    def agg_none(T):
        return [("pooled", T)]

    def agg_by(T, key):
        out = collections.OrderedDict()
        for i, g in enumerate(T[key]):
            out.setdefault(g, []).append(i)
        return list(out.items())

    rows = []
    for scope, T in (("feat全件", S), ("ラベル窓集約(n=200)", W)):
        for xc in X_CANDS:
            for tc, tlabel in TERM_CANDS:
                for cname, cfn in CORRS.items():
                    def row(agg, rv, n):
                        # 表示は 4 桁に丸めるが、**判定は丸める前の値**で行う。
                        # 丸め後の値で境界判定すると、判定窓の端で候補が
                        # 丸め方向に依存して落ちる (一意性の主張に効く)。
                        return {"scope": scope, "x": xc, "term": tc,
                                "term_label": tlabel, "corr": cname, "agg": agg,
                                "r": None if rv is None else round(rv, 4),
                                "r_raw": rv, "n": n}

                    # (a) プール
                    r, n = cfn(T[xc], T[tc])
                    rows.append(row("pooled", r, n))
                    # (b) 被験者ごと / (c) セッションごとに計算して平均。
                    # 相関の群平均は Fisher z 変換後に平均するのが定石なので、
                    # 単純平均と z 平均の両方を候補に入れる (どちらか片方だけだと
                    # `.idea` の作者が z 平均していた可能性を排除できない)。
                    for aname, gkey in (("被験者ごとの平均", "pid"),
                                        ("セッションごとの平均", "sid")):
                        vals = []
                        for _, idx in agg_by(T, gkey):
                            rr, _n = cfn([T[xc][i] for i in idx], [T[tc][i] for i in idx])
                            if rr is not None:
                                vals.append(rr)
                        for how, fn in (("", lambda v: statistics.fmean(v)),
                                        (" (Fisher z)", _mean_fisher_z)):
                            rows.append(row(aname + how,
                                            fn(vals) if vals else None, len(vals)))

    # 一致判定は round() でなく絶対差で、かつ**丸める前の値**で取る。
    # round は二進表現＋偶数丸めのため境界 (0.7750 / 0.7850) 付近の候補が
    # 非対称に落ち、「一致は 1 つだけ」という一意性の主張が判定式の揺れに依存する。
    target = IDEA["P2_r_x_vs_phi1"]
    matches = [r for r in rows
               if r["r_raw"] is not None and abs(r["r_raw"] - target) < 0.005]
    # φ(F1) 項に限った一致 (`.idea` の記述は F1 名指し)
    matches_f1 = [r for r in matches if r["term"].endswith("f1")]
    # 重み 0.25 を掛けない素の φ(F1) との相関 (スケール不変の確認)
    r_weighted, _ = pearson(S["x_logged"], S["w_f1"])
    r_unweighted, _ = pearson(S["x_logged"], [v / 0.25 for v in S["w_f1"]])
    # 一意性がどれだけ余裕を持って成立しているかの目安 (判定域のすぐ外の次点)
    f1_rows = [r for r in rows
               if r["term"].endswith("f1") and r["r_raw"] is not None
               and abs(r["r_raw"] - target) >= 0.005]
    nearest = min(f1_rows, key=lambda r: abs(r["r_raw"] - target)) if f1_rows else None
    if nearest:
        nearest = dict(nearest, delta=round(abs(nearest["r_raw"] - target), 4))
    return {
        "rows": rows,
        "match_criterion": "|r - 0.78| < 0.005",
        "matches": matches,
        "matches_f1_only": matches_f1,
        "nearest_miss_f1": nearest,
        "scale_invariance_check": {
            "r(x_logged, 0.25·φ1)": round(r_weighted, 6),
            "r(x_logged, φ1)": round(r_unweighted, 6),
            "identical": abs(r_weighted - r_unweighted) < 1e-12,
            "_note": "相関はスケール不変なので重み 0.25 の有無では動かない (確認)",
        },
    }


# ================================================================ P3: ICC の式と前処理
def _icc_formulas(a):
    """ANOVA 要約 `a` から ICC 系の指標を全部出す。"""
    msb, msw, k0, kbar = a["msb"], a["msw"], a["k0"], a["kbar"]
    out = {
        # 現行 diagnostics.d4_icc
        "ICC(1) k0補正 [現行]": (msb - msw) / (msb + (k0 - 1) * msw) if (msb + (k0 - 1) * msw) else None,
        "ICC(1) 単純平均群サイズ": (msb - msw) / (msb + (kbar - 1) * msw) if (msb + (kbar - 1) * msw) else None,
        "η² = SSB/SST": a["ssb"] / a["sst"] if a["sst"] else None,
        "ω² (バイアス補正η²)": ((a["ssb"] - (a["k"] - 1) * msw) / (a["sst"] + msw)
                              if a["sst"] + msw else None),
        "MSB/(MSB+MSW)": msb / (msb + msw) if (msb + msw) else None,
        "ICC(1,k) = (MSB−MSW)/MSB": (msb - msw) / msb if msb else None,
        # 後で埋める (群平均が要る)。母分散 (pvariance) を使うので k=5 では下方バイアス。
        # 候補列挙としては妥当だが推定量ではない。
        "群平均の母分散比 (非加重)": None,
        "SSB/SSW": a["ssb"] / a["ssw"] if a["ssw"] else None,
    }
    return out


def p3_icc(subjects, label_source, label_answered):
    """`.idea` §1.4 の ICC (f1=0.060 f3=0.055 f4=0.159 f5=0.156) を作る式×前処理を探す。"""
    pids = sorted(subjects)

    # ---- 前処理ごとに「被験者 → 値配列」を作る
    def vals_all_feat():
        out = {}
        for pid, sessions in subjects.items():
            for f in ICC_FEATS:
                out[(pid, f)] = [o[f] for s in sessions
                                 for o in s["ev"].get("feat", []) if f in o]
        return out

    def vals_session_mean():
        out = collections.defaultdict(list)
        for pid, sessions in subjects.items():
            for s in sessions:
                for f in ICC_FEATS:
                    vs = [o[f] for o in s["ev"].get("feat", []) if f in o]
                    if vs:
                        out[(pid, f)].append(statistics.fmean(vs))
        return dict(out)

    def vals_window():
        per, _ = D.window_rows(subjects, label_source, label_answered, feats=ICC_FEATS)
        return {(pid, f): [v for v in per[pid].get(f, []) if v is not None]
                for pid in per for f in ICC_FEATS}

    def clip(base, lo_p, hi_p):
        """特徴量ごとにプール分布の分位で外れ値を落とす (被験者間で共通の閾値)。"""
        out = {}
        for f in ICC_FEATS:
            pool = sorted(v for (p, ff), vs in base.items() if ff == f for v in vs)
            if not pool:
                continue
            lo = pool[int(lo_p * (len(pool) - 1))]
            hi = pool[int(hi_p * (len(pool) - 1))]
            for p in pids:
                out[(p, f)] = [v for v in base.get((p, f), []) if lo <= v <= hi]
        return out

    def iqr_filter(base):
        out = {}
        for f in ICC_FEATS:
            pool = sorted(v for (p, ff), vs in base.items() if ff == f for v in vs)
            if not pool:
                continue
            q1 = pool[int(0.25 * (len(pool) - 1))]
            q3 = pool[int(0.75 * (len(pool) - 1))]
            lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
            for p in pids:
                out[(p, f)] = [v for v in base.get((p, f), []) if lo <= v <= hi]
        return out

    def log1p_tr(base):
        return {k: [math.log1p(v) for v in vs if v > -1] for k, vs in base.items()}

    base_all = vals_all_feat()
    PREPROCS = collections.OrderedDict([
        ("feat全件 [現行]", base_all),
        ("ラベル窓集約(n=200)", vals_window()),
        ("セッション平均", vals_session_mean()),
        ("feat全件 1–99%クリップ", clip(base_all, 0.01, 0.99)),
        ("feat全件 5–95%クリップ", clip(base_all, 0.05, 0.95)),
        ("feat全件 IQR1.5除去", iqr_filter(base_all)),
        ("feat全件 log1p", log1p_tr(base_all)),
    ])

    SUBJECT_SETS = collections.OrderedDict([(f"all{len(pids)}", pids)])
    for drop in pids:
        SUBJECT_SETS[f"drop_{drop}"] = [p for p in pids if p != drop]

    rows = []
    for pname, base in PREPROCS.items():
        # 群統計は前処理ごとに 1 回だけ計算する (以降の組み合わせは O(k))
        gs = {(p, f): group_stats(base.get((p, f), [])) for p in pids for f in ICC_FEATS}
        for sname, subs in SUBJECT_SETS.items():
            per_formula = collections.defaultdict(dict)
            n_used = {}
            for f in ICC_FEATS:
                stats = [gs[(p, f)] for p in subs if gs[(p, f)] and gs[(p, f)][0] >= 2]
                a = anova(stats)
                if not a:
                    continue
                n_used[f] = a["n"]
                vals = _icc_formulas(a)
                means = [s[1] for s in stats]
                within = statistics.fmean([s[2] / s[0] for s in stats])
                vb = statistics.pvariance(means) if len(means) > 1 else 0.0
                vals["群平均の母分散比 (非加重)"] = vb / (vb + within) if (vb + within) else None
                for k, v in vals.items():
                    per_formula[k][f] = None if v is None else round(v, 4)
            for formula, vv in per_formula.items():
                diffs = [abs(vv[f] - IDEA["P3_icc"][f])
                         for f in IDEA["P3_icc"] if vv.get(f) is not None]
                rows.append({
                    "preproc": pname, "subjects": sname, "formula": formula,
                    "icc": vv, "n": n_used.get("f1"),
                    "max_abs_diff_vs_idea": round(max(diffs), 4) if len(diffs) == 4 else None,
                    "ratio_idea_over_this": {
                        f: (round(IDEA["P3_icc"][f] / vv[f], 3)
                            if vv.get(f) else None) for f in IDEA["P3_icc"]},
                })

    scored = [r for r in rows if r["max_abs_diff_vs_idea"] is not None]
    scored.sort(key=lambda r: r["max_abs_diff_vs_idea"])
    # 一致の判定: `.idea` は 3 桁表記なので四捨五入で 3 桁一致を「一致」とする
    exact = [r for r in rows
             if all(r["icc"].get(f) is not None
                    and round(r["icc"][f], 3) == IDEA["P3_icc"][f] for f in IDEA["P3_icc"])]

    # ---- ICC(1) と η² の関係を ANOVA 要約から明示する。
    # どちらも F = MSB/MSW の単調関数だが、分母の重みが違う:
    #   ICC(1) = (F−1)/(F+k0−1)          … 分散成分比 σ²b/(σ²b+σ²w) の推定量
    #   η²     = (k−1)F/((k−1)F+(N−k))   … この標本で群が説明する平方和の割合
    # η² は群平方和に自由度 k−1 しか与えないため、群数 k が小さいと ICC を過小評価する。
    relation = {}
    gs_all = {(p, f): group_stats(base_all.get((p, f), [])) for p in pids for f in ICC_FEATS}
    for f in ICC_FEATS:
        a = anova([gs_all[(p, f)] for p in pids if gs_all[(p, f)]])
        if not a:
            continue
        icc1 = (a["msb"] - a["msw"]) / (a["msb"] + (a["k0"] - 1) * a["msw"])
        eta2 = a["ssb"] / a["sst"]
        relation[f] = {
            "k_groups": a["k"], "n": a["n"], "k0": round(a["k0"], 2),
            "F_msb_over_msw": round(a["msb"] / a["msw"], 2) if a["msw"] else None,
            "ICC(1)_k0": round(icc1, 4), "eta2_SSB_over_SST": round(eta2, 4),
            "eta2_over_icc1": round(eta2 / icc1, 4) if icc1 else None,
            "idea_value": IDEA["P3_icc"].get(f),
        }
    return {"rows": rows, "best": scored[:15], "exact_matches": exact,
            "icc1_vs_eta2_relation": relation}


# ================================================================ 出力
def render(res, path):
    L = []
    a = L.append
    a("########## probe_variants — notes.md §1 未解決 3 件の候補定義 総当たり")
    a("(調査用スクリプト。本体 diagnostics.py の結果は変えない)")
    a("")

    p1 = res["P1_permutation_cell_count"]
    a("========== P1: `.idea` §1.1「並べ替え検定 68 件」のセル数定義")
    ms = p1["matrix_summary"]
    a(f"{ms['n_features']} 特徴量 × {ms['n_subjects']} 被験者 × {ms['n_targets']} ターゲット "
      f"= {ms['cells_total']} セル / 算出可能 {ms['computable']}")
    a(f"算出不能セル: {len(ms['uncomputable_detail'])} 件")
    for s in ms["uncomputable_detail"]:
        a(f"    {s}")
    a("")
    a(f"-- 名前付き集合の総当たり {len(p1['rows'])} 通り中、68 になったもの: "
      f"{len(p1['matches'])} 件 --")
    if p1["matches"]:
        a(f"{'特徴量セット':<34}{'被験者':<16}{'ターゲット':<10}{'数え方':<14}{'pooled':<8}")
        for r in p1["matches"]:
            a(f"{r['features']:<34}{r['subjects']:<16}{r['targets']:<10}"
              f"{r['count_mode']:<14}{'あり' if r['pooled'] else 'なし':<8}")
    else:
        a("    なし")
    a("")
    a("-- 構造的な解 (「全セル」で数える場合、count = |F|·|S|·|T| (+pooled なら |F|·|T|)) --")
    a("   ※ 中身に依らず個数だけで決まるので、この式の整数解が候補の全体になる")
    for s in p1["structural_solutions"]:
        a(f"    |F|={s['n_features']:>3}  |S|={s['n_subjects']}  |T|={s['n_targets']}  "
          f"pooled={'あり' if s['pooled'] else 'なし'}")
    a("")

    p2 = res["P2_correlation"]
    a("========== P2: `.idea` §1.3「実 X と 0.25·φ(F1) の相関 r=0.78」")
    sc = p2["scale_invariance_check"]
    a(f"スケール不変性の確認: r(x_logged, 0.25·φ1)={sc['r(x_logged, 0.25·φ1)']} / "
      f"r(x_logged, φ1)={sc['r(x_logged, φ1)']} → 同一={sc['identical']}")
    a(f"-- 総当たり {len(p2['rows'])} 通り中、|r − 0.78| < 0.005 になったもの --")
    a(f"   φ(F1) 項に限る: {len(p2['matches_f1_only'])} 件 / 全項: {len(p2['matches'])} 件")
    nm = p2.get("nearest_miss_f1")
    if nm:
        a(f"   φ(F1) の次点 (判定域外): {nm['x']} × {nm['term']} {nm['corr']} {nm['agg']} "
          f"r={nm['r']} (|Δ|={nm['delta']}) — 判定域を広げても一意性がすぐ崩れないかの目安")
    a("")
    a(f"{'scope':<20}{'X':<20}{'項':<10}{'相関':<10}{'集約':<20}{'r':>8}{'n':>8}")
    for r in p2["matches"]:
        mark = " ★" if r["term"].endswith("f1") else ""
        a(f"{r['scope']:<20}{r['x']:<20}{r['term']:<10}{r['corr']:<10}"
          f"{r['agg']:<20}{r['r']:>8}{r['n']:>8}{mark}")
    a("")
    a("-- 参考: φ(F1) 項の全変種 --")
    a(f"{'scope':<20}{'X':<20}{'項':<10}{'相関':<10}{'集約':<20}{'r':>8}{'n':>8}")
    for r in p2["rows"]:
        if r["term"].endswith("f1"):
            a(f"{r['scope']:<20}{r['x']:<20}{r['term']:<10}{r['corr']:<10}"
              f"{r['agg']:<20}{str(r['r']):>8}{r['n']:>8}")
    a("")

    p3 = res["P3_icc"]
    a("========== P3: `.idea` §1.4 の ICC (f1=0.060 f3=0.055 f4=0.159 f5=0.156)")
    a(f"総当たり {len(p3['rows'])} 通り (式 × 前処理 × 被験者集合)")
    a(f"3 桁完全一致: {len(p3['exact_matches'])} 件")
    for r in p3["exact_matches"]:
        a(f"    ★ {r['formula']} / {r['preproc']} / {r['subjects']} → {r['icc']}")
    a("")
    a("-- `.idea` に近い順 上位 15 --")
    a(f"{'式':<28}{'前処理':<24}{'被験者':<12}{'最大差':>8}  ICC")
    for r in p3["best"]:
        icc = " ".join(f"{f}={r['icc'].get(f)}" for f in ICC_FEATS if f in r["icc"])
        a(f"{r['formula']:<28}{r['preproc']:<24}{r['subjects']:<12}"
          f"{r['max_abs_diff_vs_idea']:>8}  {icc}")
    a("")
    a("-- 比 (.idea ÷ 本実験) の上位候補 --")
    a(f"{'式':<28}{'前処理':<24}{'被験者':<12}  比")
    for r in p3["best"][:10]:
        a(f"{r['formula']:<28}{r['preproc']:<24}{r['subjects']:<12}  "
          f"{r['ratio_idea_over_this']}")
    a("")
    a("-- ICC(1) と η² の関係 (feat 全件・5 被験者) --")
    a("   ICC(1) = (F−1)/(F+k0−1)         : 分散成分比 σ²b/(σ²b+σ²w) の推定量")
    a("   η²     = (k−1)F/((k−1)F+(N−k))  : この標本で群が説明する平方和の割合")
    a("   η² は群平方和に自由度 k−1 しか与えないので、群数 k が小さいと ICC を過小評価する")
    a(f"{'feat':<6}{'k':>4}{'N':>10}{'k0':>12}{'F=MSB/MSW':>13}"
      f"{'ICC(1)':>10}{'η²':>10}{'η²/ICC':>10}{'.idea':>9}")
    for f, v in p3["icc1_vs_eta2_relation"].items():
        a(f"{f:<6}{v['k_groups']:>4}{v['n']:>10}{v['k0']:>12}{v['F_msb_over_msw']:>13}"
          f"{v['ICC(1)_k0']:>10}{v['eta2_SSB_over_SST']:>10}{v['eta2_over_icc1']:>10}"
          f"{str(v['idea_value']):>9}")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")


def main():
    if len(sys.argv) != 4:
        print("usage: probe_variants.py <raw_root> <constants.json> <out_dir>",
              file=sys.stderr)
        sys.exit(1)
    raw_root, const_path, out_dir = sys.argv[1:]
    const = json.load(open(const_path, encoding="utf-8"))
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(const_path)), "config.json")
    cfg = json.load(open(cfg_path, encoding="utf-8")) if os.path.isfile(cfg_path) else {}
    lf = cfg.get("label_filter", {})
    label_source = lf.get("source", "random_probe")
    label_answered = lf.get("answered", True)

    parse_failures = [0]
    subjects = D.load(raw_root, parse_failures)
    if not subjects:
        print(f"[probe] FAILED: {raw_root} に P0* が無い", file=sys.stderr)
        sys.exit(1)
    if parse_failures[0]:
        print(f"[probe] FAILED: NDJSON parse 失敗 {parse_failures[0]} 件", file=sys.stderr)
        sys.exit(1)
    want = cfg.get("subjects")
    if want and sorted(subjects) != sorted(want):
        print(f"[probe] FAILED: 被験者集合が config と違う "
              f"(config={sorted(want)} / 実際={sorted(subjects)})", file=sys.stderr)
        sys.exit(1)
    # 単体起動でも入力の版を照合する (acceptance.sh 経由なら run.sh が先に落ちるが、
    # このスクリプトだけを直接叩いたときに別版のデータで総当たりしても気づけない)。
    versions = collections.Counter(
        o.get("hmm_version") for ss in subjects.values() for s in ss
        for o in s["ev"].get("meta", []) if o.get("hmm_version"))
    expected = cfg.get("hmm_version_expected")
    if expected and set(versions) != {expected}:
        print(f"[probe] FAILED: hmm_version が期待値 {expected!r} と違う: {dict(versions)}",
              file=sys.stderr)
        sys.exit(1)

    S, W = build_samples(subjects, const, label_source, label_answered)
    res = {
        "_note": "調査用の総当たり。本体 diagnostics.py の結果ではない。",
        "idea_values": IDEA,
        "hmm_version": dict(versions),
        "subjects": sorted(subjects),
        "n_feat_samples": len(S["x_logged"]),
        "n_label_windows": len(W["x_logged"]),
        "P1_permutation_cell_count": p1_cell_counts(subjects, label_source, label_answered),
        "P2_correlation": p2_correlations(S, W),
        "P3_icc": p3_icc(subjects, label_source, label_answered),
    }
    D.assert_no_pii(res)

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "probe_variants.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    render(res, os.path.join(out_dir, "probe_variants.txt"))
    print(f"[probe] OK -> {out_dir}/probe_variants.json / probe_variants.txt")


if __name__ == "__main__":
    main()
