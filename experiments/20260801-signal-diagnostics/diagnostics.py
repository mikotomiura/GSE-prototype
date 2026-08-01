#!/usr/bin/env python3
"""D1-D7: `.idea/20260801-architecture-signal-and-online-learning.md` §1 の実測値を再現する。

入力: gse-dataset の匿名化済み NDJSON (Phase1 確証カット = calibration_blind 40 セッション)。
出力: results/*.json (機械可読) と results/*.txt (人間可読)。**集計値のみ**を出す。

使い方: diagnostics.py <raw_root> <constants.json> <out_dir> <seed> <n_perm>
"""
import collections
import glob
import json
import math
import os
import random
import re
import statistics
import sys

FEATS = ["f1", "f3", "f4", "f5", "f6", "raw_x", "raw_y"]
PHI_FEATS = ["f1", "f3", "f4", "f5", "f6"]


# ---------------------------------------------------------------- φ (Rust 再実装)
def make_phi(kappa):
    def phi(x, beta):
        if beta <= 0.0:
            return 0.0
        return min(max((x - beta) / (kappa * beta), 0.0), 1.0)
    return phi


# ---------------------------------------------------------------- C-index
def cindex(pairs):
    """pairs=[(v,q)] 方向付き順序 C-index。既存 per_feature_cindex.py と同一定義。"""
    c = 0.0
    n = 0
    for i in range(len(pairs)):
        v1, q1 = pairs[i]
        for j in range(i + 1, len(pairs)):
            v2, q2 = pairs[j]
            if q1 == q2:
                continue
            n += 1
            if v1 == v2:
                c += 0.5
            elif (v1 > v2) == (q1 > q2):
                c += 1.0
    return c / n if n else None


class FastCIndex:
    """C-index を「v の密ランク × q の水準」のバケット集計で O(k·R + k·n) で評価する。

    素朴な O(n^2) 実装を並べ替えのたびに回すと現実的な時間で終わらない
    (numpy が無い環境のため純 Python)。q の水準数 k は 1-5 と小さく、
    v は並べ替えで動かないので、v の密ランクを一度だけ作れば
    各並べ替えは水準割り当ての張り替えだけで済む。

    定義は素朴実装 `cindex()` と同一で、`self_check()` で両者の一致を検証する。
    """

    def __init__(self, pairs):
        self.n = len(pairs)
        vals = [v for v, _ in pairs]
        qs = [q for _, q in pairs]
        uniq_v = sorted(set(vals))
        self.R = len(uniq_v)
        v_rank = {v: i for i, v in enumerate(uniq_v)}
        self.ranks = [v_rank[v] for v in vals]
        uniq_q = sorted(set(qs))
        self.k = len(uniq_q)
        q_lv = {q: i for i, q in enumerate(uniq_q)}
        self.levels = [q_lv[q] for q in qs]

    def evaluate(self, levels):
        """水準割り当て `levels` に対する C-index。比較可能ペアが無ければ None。"""
        k, R = self.k, self.R
        if k < 2:
            return None
        cnt = [[0] * R for _ in range(k)]
        members = [[] for _ in range(k)]
        for r, a in zip(self.ranks, levels):
            cnt[a][r] += 1
            members[a].append(r)
        cum = [list(_accumulate(c)) for c in cnt]
        total = 0.0
        n_pairs = 0
        for a in range(k):
            ca, cua, na = cnt[a], cum[a], len(members[a])
            if not na:
                continue
            for b in range(a + 1, k):
                mb = members[b]
                if not mb:
                    continue
                n_pairs += na * len(mb)
                # 水準 a < b なので「b 側の v が大きい」= concordant
                total += sum(cua[r] - 0.5 * ca[r] for r in mb)
        return total / n_pairs if n_pairs else None

    def observed(self):
        return self.evaluate(self.levels)

    def self_check(self, pairs, rng=None, n_random=5):
        """素朴実装との一致を検証する (実装差による静かなズレの検知)。

        観測配置だけでなく **乱数シャッフルした配置**でも照合する。
        並べ替え検定は evaluate() を 1 万回呼ぶので、観測 1 点だけの検算では
        「並べ替え時にだけ壊れるバグ」を捕まえられない。
        """
        vals = [v for v, _ in pairs]

        def cmp_once(levels, label):
            uniq_q = sorted(set(q for _, q in pairs))
            naive = cindex(list(zip(vals, [uniq_q[a] for a in levels])))
            fast = self.evaluate(levels)
            if naive is None and fast is None:
                return None
            if naive is None or fast is None:
                return f"{label}: 片方だけ None (naive={naive} fast={fast})"
            if abs(naive - fast) > 1e-9:
                return f"{label}: 不一致 naive={naive!r} fast={fast!r}"
            return None

        why = cmp_once(self.levels, "観測配置")
        if why:
            return False, why
        if rng is not None:
            lv = self.levels[:]
            for i in range(n_random):
                rng.shuffle(lv)
                why = cmp_once(lv, f"乱数配置#{i}")
                if why:
                    return False, why
        return True, None


def _accumulate(seq):
    s = 0
    for x in seq:
        s += x
        yield s


def perm_p(pairs, rng, n_perm):
    """被験者内でラベルをシャッフルして両側 p 値を出す。

    被験者間の絶対値差を帰無仮説へ持ち込まないため **被験者内** シャッフルにする
    (pooled でやると被験者間差が有意性を作ってしまう)。
    """
    if len(pairs) < 2:
        return None, None, 0, None
    fc = FastCIndex(pairs)
    ok, why = fc.self_check(pairs, rng=rng)
    if not ok:
        raise AssertionError(f"FastCIndex が素朴実装と一致しない: {why}")
    obs = fc.observed()
    if obs is None:
        return None, None, 0, None
    dev = abs(obs - 0.5)
    lv = fc.levels[:]
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(lv)
        c = fc.evaluate(lv)
        if c is not None and abs(c - 0.5) >= dev:
            hits += 1
    # +1 補正 (Phipson & Smyth 2010): p=0 を出さない
    return obs, (hits + 1) / (n_perm + 1), n_perm, fc.k


# ---------------------------------------------------------------- 入力ロード
def load(raw_root, parse_failures):
    """被験者 → セッション のイベントを読む。生値は返さず、以降の集計に必要な形にする。"""
    subjects = collections.OrderedDict()
    for pid in sorted(os.listdir(raw_root)):
        d = os.path.join(raw_root, pid)
        if not pid.startswith("P0") or not os.path.isdir(d):
            continue
        sessions = []
        for path in sorted(glob.glob(os.path.join(d, "*.ndjson"))):
            ev = collections.defaultdict(list)
            for line in open(path, encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    parse_failures[0] += 1
                    continue
                ev[o.get("type")].append(o)
            if not ev:
                continue
            # ファイル名 gse_YYYYMMDD_HHMMSS.ndjson は**セッション開始の絶対時刻そのもの**。
            # data.md が「絶対 epoch 時刻なし」を約束しているので保持しない。
            sessions.append({"sid": len(sessions), "ev": ev})
        if sessions:
            subjects[pid] = sessions
    return subjects


def ime_open_series(ime_states, feats):
    """feat には ime_open が無いので ime_state の直近 `on` を前方補完する。

    feat / ime_state とも時刻順なので、二重ループでなく一度のスイープで解く
    (feat は 1 セッション数千件・全体 12 万件規模)。
    """
    out = []
    i = 0
    on = False
    for o in feats:
        t = o["t"]
        while i < len(ime_states) and ime_states[i]["t"] <= t:
            on = bool(ime_states[i].get("on"))
            i += 1
        out.append(on)
    return out


# ---------------------------------------------------------------- D1 / D5
def window_rows(subjects, label_source="random_probe", label_answered=True, feats=None):
    """ラベル窓ごとに、既存特徴量と『収集済みだが未使用』の信号を集約する。

    `feats` は集約する feat フィールド (既定 `FEATS`)。probe_variants.py が
    別の特徴量集合で数え直すために使う。module 変数 `FEATS` を外から書き換えて
    呼ぶ形にすると、差し替えが呼ばれる側から見えず静かに壊れる。
    """
    feats_wanted = FEATS if feats is None else feats
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    counts = collections.Counter()
    for pid, sessions in subjects.items():
        for s in sessions:
            ev = s["ev"]
            feats = sorted(ev.get("feat", []), key=lambda o: o["t"])
            keys = [o for o in ev.get("key", []) if o.get("press")]
            pastes = ev.get("paste", [])
            shadows = ev.get("ime_shadow", [])
            # `bool(...)` だと文字列 "false" / "0" まで True になる。厳格に比較する。
            labels = [o for o in ev.get("realtime_label", [])
                      if o.get("source") == label_source
                      and o.get("answered") is label_answered]
            for lb in labels:
                ws, we = lb["analysis_window_start_ms"], lb["analysis_window_end_ms"]
                win = [o for o in feats if ws <= o["t"] <= we]
                if not win:
                    counts["no_feat_in_window"] += 1
                    continue
                counts["usable"] += 1
                row = {}
                for k in feats_wanted:
                    vs = [o[k] for o in win if k in o]
                    row[k] = statistics.median(vs) if vs else None
                # ---- 収集済みだが未使用の信号 (.idea §1.5)
                kw = [o for o in keys if ws <= o["t"] <= we]
                row["keys"] = len(kw)
                row["bs_rate"] = (
                    sum(1 for o in kw if o.get("category") == "backspace") / len(kw)
                    if kw else None
                )
                pw = [o for o in pastes if ws <= o["t"] <= we]
                row["paste_count"] = len(pw)
                # external_paste_chars は匿名化で null になりうる (文字数は内容量の漏洩になる)。
                # null を 0 と混同すると「貼り付け量ゼロ」と区別できないので、
                # 非 null が 1 件も無い窓は None (= 欠測) にする。
                chars = [o["external_paste_chars"] for o in pw
                         if o.get("external_paste_chars") is not None]
                row["paste_chars"] = sum(chars) if chars else (0 if not pw else None)
                sw = [o["dwell_ms"] for o in shadows
                      if ws <= o["t"] <= we and "dwell_ms" in o]
                row["ime_dwell_med"] = statistics.median(sw) if sw else None
                per[pid]["__q1"].append(lb["q1_friction"])
                per[pid]["__q2"].append(lb["q2_progress"])
                for k, v in row.items():
                    per[pid][k].append(v)
    return per, counts


def d1_d5(per, seed, n_perm, extra_feats):
    rng = random.Random(seed)
    cells = []
    for target, tname in (("__q1", "Q1_friction"), ("__q2", "Q2_progress")):
        for k in FEATS + extra_feats:
            for pid in sorted(per):
                q = per[pid][target]
                v = per[pid].get(k, [])
                pairs = [(a, b) for a, b in zip(v, q) if a is not None]
                ci, p, np_, kq = perm_p(pairs, rng, n_perm)
                if ci is None:
                    n_lv = len(set(b for _, b in pairs))
                    if not pairs:
                        reason = "特徴量が全欠測 (窓内に該当イベントが無い)"
                    elif n_lv < 2:
                        reason = "ラベル分散なし (q が定数 → 比較可能ペアがゼロ)"
                    else:
                        reason = "有効サンプル不足"
                    cells.append({"target": tname, "feature": k, "subject": pid,
                                  "n": len(pairs), "cindex": None, "p": None,
                                  "q_levels": n_lv, "reason": reason})
                    continue
                # 相異なる並べ替え数 M = n! / Π(n_i!) から p の構造的下限 2/M を出す。
                # M 自体は天文学的な整数になるので出力には載せない (p_floor だけ持つ)。
                qc = collections.Counter(b for _, b in pairs)
                m = math.factorial(len(pairs))
                for v in qc.values():
                    m //= math.factorial(v)
                cells.append({"target": tname, "feature": k, "subject": pid,
                              "n": len(pairs), "q_levels": kq,
                              "cindex": round(ci, 4),
                              "p": round(p, 5), "n_perm": np_,
                              # 厳密並べ替えの両側 p の下限の**近似**。厳密には統計量の
                              # 離散性・同値の重複で 2/M ちょうどとは限らないので目安。
                              "p_floor_exact_approx": (2.0 / m) if m else None,
                              # Monte Carlo 推定値そのものの下限 (+1 補正のため)
                              "p_floor_mc": 1.0 / (np_ + 1) if np_ else None})
    computable = [c for c in cells if c["cindex"] is not None]
    # 並べ替え検定の p には**構造的な下限**がある。相異なる並べ替えが M 通りしか無ければ
    # 両側 p の下限は 2/M。n が小さいセルは Bonferroni 閾値に原理的に到達できないので、
    # 「通過ゼロ」を語る前に到達可能セル数を出す。
    bonf_pre = 0.05 / len(computable) if computable else None
    for c in computable:
        fe, fm = c.get("p_floor_exact_approx"), c.get("p_floor_mc")
        # 両方の下限が閾値以下でなければ「通過しえない」。
        # exact 側は近似なので、判定は保守的に (= 到達可能と数える側に厳しく) 取る。
        c["bonferroni_attainable"] = (
            bonf_pre is not None and fe is not None and fm is not None
            and fe <= bonf_pre and fm <= bonf_pre)
    attainable = [c for c in computable if c.get("bonferroni_attainable")]
    core = [c for c in cells if c["feature"] in FEATS]
    core_ok = [c for c in core if c["cindex"] is not None]
    extra_cells = [c for c in cells if c["feature"] in extra_feats]
    extra_ok = [c for c in extra_cells if c["cindex"] is not None]
    # X 系 = Q1 (摩擦) を対象にした既存 5 特徴量 + raw_x
    xset = ["f1", "f3", "f4", "f5", "f6", "raw_x"]
    x_cells = [c for c in cells if c["target"] == "Q1_friction"
               and c["feature"] in xset and c["cindex"] is not None]
    bonf = 0.05 / len(computable) if computable else None
    nominal = [c for c in computable if c["p"] < 0.05]
    passed = [c for c in computable if bonf and c["p"] < bonf]
    return {
        "cells_total": len(cells),
        "cells_core_total": len(core),
        "cells_core_computable": len(core_ok),
        "cells_extra_total": len(extra_cells),
        "cells_extra_computable": len(extra_ok),
        "x_axis_cells_computable": len(x_cells),
        "x_axis_nominal_sig_count": sum(1 for c in x_cells if c["p"] < 0.05),
        "cells_computable": len(computable),
        "cells_uncomputable": len(cells) - len(computable),
        "nominal_sig_count": len(nominal),
        "bonferroni_threshold": bonf,
        "bonferroni_attainable_count": len(attainable),
        "bonferroni_passed_count": len(passed),
        "nominal_sig": sorted(nominal, key=lambda c: c["p"])[:20],
        "cells": cells,
    }


# ---------------------------------------------------------------- D2 / D3
def d2_d3(subjects, const):
    phi = make_phi(const["kappa"])
    b = const["beta"]
    wx = const["weights_x"]
    rails = {mode: {f: {"zero": 0, "one": 0, "total": 0} for f in PHI_FEATS}
             for mode in ("beta_writing_fixed", "ime_state_derived")}
    ime_mode_counts = collections.Counter()
    x_recalc, x_real, x_logged = [], [], []
    term_series = {"phi3": [], "phi6": [], "phi1": [], "phi5": []}
    term_real = {"phi3": [], "phi6": [], "phi1": [], "phi5": []}
    max_abs_err = 0.0
    max_abs_err_real = 0.0
    resid_real = []  # ime_state 由来 β で再計算した X と feat.raw_x の残差

    for pid, sessions in subjects.items():
        for s in sessions:
            feats = sorted(s["ev"].get("feat", []), key=lambda o: o["t"])
            ime_states = sorted(s["ev"].get("ime_state", []), key=lambda o: o["t"])
            ime_open = ime_open_series(ime_states, feats)
            for o, is_open in zip(feats, ime_open):
                for mode in ("beta_writing_fixed", "ime_state_derived"):
                    if mode == "beta_writing_fixed":
                        ctx = "WRITING"
                    else:
                        ctx = "WRITING" if is_open else "CODING"
                        ime_mode_counts[ctx] += 1
                    for f in PHI_FEATS:
                        if f not in o:
                            continue
                        val = phi(o[f], b[f"BETA_{ctx}_{f.upper()}"])
                        r = rails[mode][f]
                        r["total"] += 1
                        if val <= 0.0:
                            r["zero"] += 1
                        elif val >= 1.0:
                            r["one"] += 1
                # ---- D3: X を再計算し feat.raw_x と突き合わせる
                if all(f in o for f in PHI_FEATS) and "raw_x" in o:
                    ctx_real = "WRITING" if is_open else "CODING"

                    def terms(c):
                        return (
                            phi(o["f1"], b[f"BETA_{c}_F1"]),
                            phi(o["f3"], b[f"BETA_{c}_F3"]),
                            phi(o["f5"], b[f"BETA_{c}_F5"]),
                            phi(o["f6"], b[f"BETA_{c}_F6"]),
                        )

                    def compose(p1, p3, p5, p6):
                        return min(max(wx["phi3"] * p3 + wx["phi6"] * p6
                                       + wx["phi1"] * p1 + wx["phi5"] * p5, 0.0), 1.0)

                    # (a) β_writing 固定 = .idea §1.3 の再現条件
                    w1, w3, w5, w6 = terms("WRITING")
                    x_recalc.append(compose(w1, w3, w5, w6))
                    # (b) ime_state 由来の実 β = Rust の挙動に対応。φ 実装の検算に使う
                    r1, r3, r5, r6 = terms(ctx_real)
                    x_real.append(compose(r1, r3, r5, r6))

                    x_logged.append(o["raw_x"])
                    term_series["phi3"].append(wx["phi3"] * w3)
                    term_series["phi6"].append(wx["phi6"] * w6)
                    term_series["phi1"].append(wx["phi1"] * w1)
                    term_series["phi5"].append(wx["phi5"] * w5)
                    term_real["phi3"].append(wx["phi3"] * r3)
                    term_real["phi6"].append(wx["phi6"] * r6)
                    term_real["phi1"].append(wx["phi1"] * r1)
                    term_real["phi5"].append(wx["phi5"] * r5)
                    max_abs_err = max(max_abs_err, abs(x_recalc[-1] - o["raw_x"]))
                    d_real = abs(x_real[-1] - o["raw_x"])
                    max_abs_err_real = max(max_abs_err_real, d_real)
                    resid_real.append(d_real)

    for mode in rails:
        for f, r in rails[mode].items():
            t = r["total"] or 1
            r["zero_pct"] = round(100.0 * r["zero"] / t, 1)
            r["one_pct"] = round(100.0 * r["one"] / t, 1)
            r["rail_pct"] = round(100.0 * (r["zero"] + r["one"]) / t, 1)

    def pearson(a, bb):
        if len(a) != len(bb):
            raise AssertionError(f"pearson: 長さ不一致 {len(a)} != {len(bb)}")
        if len(a) < 2:
            return None
        ma, mb = statistics.fmean(a), statistics.fmean(bb)
        num = sum((x - ma) * (y - mb) for x, y in zip(a, bb))
        da = math.sqrt(sum((x - ma) ** 2 for x in a))
        db = math.sqrt(sum((y - mb) ** 2 for y in bb))
        return num / (da * db) if da and db else None

    def corr_map(series, base, base_name):
        out = {}
        for k, v in series.items():
            r = pearson(base, v)
            out[f"r({base_name}, {k}_term)"] = round(r, 4) if r is not None else None
        return out

    corr = corr_map(term_series, x_logged, "x_logged")       # β_writing 項 × 記録 X
    corr_real = corr_map(term_real, x_logged, "x_logged")    # 実 β 項 × 記録 X
    # `.idea` §1.3 の条件: §1.3 は「124,517 サンプルで φ を再計算 (β_writing 基準)」なので
    # **両辺とも β_writing 基準の再計算 X** で相関を取っている。記録された raw_x は
    # IME 状態で切り替わる実 β で作られており基準が違う。この差が
    # 「.idea r=0.78 / 再現 0.763」の原因 (probe_variants.py P2 で総当たり確認)。
    corr_recalc = corr_map(term_series, x_recalc, "x_recalc_beta_writing")

    # 相関はスケール不変なので重みが効かない。「どの項が X を動かしているか」は
    # 標準化寄与 w_i·sd(phi_i)/sd(X) の方が答えになる。
    def sd(xs):
        return statistics.pstdev(xs) if len(xs) > 1 else 0.0

    sd_x = sd(x_logged)
    std_contrib = {k: (round(sd(v) / sd_x, 4) if sd_x else None)
                   for k, v in term_real.items()}
    return {
        "rails": rails,
        "ime_state_derived_context_counts": dict(ime_mode_counts),
        "feat_samples_used_for_x": len(x_recalc),
        "x_recalc_vs_logged": {
            "beta_writing_fixed": {
                "max_abs_error": max_abs_err,
                "pearson_r": round(pearson(x_recalc, x_logged), 6) if x_recalc else None,
                "note": ".idea §1.3 の再現条件。実 β は IME 状態で切り替わるため一致はしない",
            },
            "ime_state_derived": {
                "max_abs_error": max_abs_err_real,
                "pearson_r": round(pearson(x_real, x_logged), 6) if x_real else None,
                "residual": _resid_stats(resid_real),
                "note": ("Rust の挙動に対応。厳密一致は原理的に不可能 —"
                         " NDJSON は f1:.2 / f5:.1 / raw_x:.4 に丸めて記録するため"
                         " (logger.rs)、Python は丸め後の入力から再計算している。"
                         " 加えて ime_state の前方補完が遷移点で実 IME 状態とずれる"),
            },
        },
        "term_correlations_with_logged_x": corr,
        "term_correlations_real_beta": corr_real,
        "term_correlations_with_recalc_x_beta_writing": corr_recalc,
        "standardized_contributions": std_contrib,
    }


def _resid_stats(xs):
    """再計算 X と記録値の残差分布。丸め由来 (小・多数) と文脈誤判定由来 (大・少数) を分ける。"""
    if not xs:
        return None
    ss = sorted(xs)
    n = len(ss)
    big = sum(1 for v in ss if v > 0.01)
    return {
        "n": n,
        "median": ss[n // 2],
        "p95": ss[min(n - 1, int(0.95 * n))],
        "max": ss[-1],
        "gt_0_01": big,
        "gt_0_01_pct": round(100.0 * big / n, 3),
    }


# ---------------------------------------------------------------- D4
def _icc1(groups):
    """ICC(1) = (MSB - MSW) / (MSB + (k0-1) MSW)。k0 は不均衡設計の平均群サイズ。"""
    if len(groups) < 2:
        return None, None
    n_total = sum(len(g) for g in groups)
    k_groups = len(groups)
    means = [statistics.fmean(g) for g in groups]
    grand = sum(m * len(g) for m, g in zip(means, groups)) / n_total
    ssb = sum(len(g) * (m - grand) ** 2 for m, g in zip(means, groups))
    ssw = sum((v - m) ** 2 for m, g in zip(means, groups) for v in g)
    msb = ssb / (k_groups - 1)
    msw = ssw / (n_total - k_groups) if n_total > k_groups else None
    if not msw:
        return None, None
    k0 = (n_total - sum(len(g) ** 2 for g in groups) / n_total) / (k_groups - 1)
    return (msb - msw) / (msb + (k0 - 1) * msw), k0


def d4_icc(subjects):
    """ICC(1)、群 = 被験者、feat 全件。被験者 5 名なので LOO 範囲も併記する。"""
    out = {}
    for f in ["f1", "f3", "f4", "f5", "f6"]:
        groups = []
        for pid, sessions in subjects.items():
            vals = [o[f] for s in sessions for o in s["ev"].get("feat", []) if f in o]
            if len(vals) >= 2:
                groups.append(vals)
        if len(groups) < 2:
            out[f] = {"icc": None, "reason": "群が 2 未満"}
            continue
        n_total = sum(len(g) for g in groups)
        k_groups = len(groups)
        # 群平均は一度だけ計算する。内包表記の中で fmean(g) を呼ぶと
        # 要素ごとに群全体を舐めて O(|g|^2) になる (feat は 1 群 2 万件規模)。
        means = [statistics.fmean(g) for g in groups]
        grand = sum(m * len(g) for m, g in zip(means, groups)) / n_total
        ssb = sum(len(g) * (m - grand) ** 2 for m, g in zip(means, groups))
        ssw = sum((v - m) ** 2 for m, g in zip(means, groups) for v in g)
        msb = ssb / (k_groups - 1)
        msw = ssw / (n_total - k_groups) if n_total > k_groups else None
        if msw is None or msw == 0:
            out[f] = {"icc": None, "reason": "MSW=0"}
            continue
        # 不均衡設計の k0 (Snedecor & Cochran)
        k0 = (n_total - sum(len(g) ** 2 for g in groups) / n_total) / (k_groups - 1)
        icc = (msb - msw) / (msb + (k0 - 1) * msw)
        # 群 (被験者) が 5 つしかないので点推定を 4 桁で語ると精度を過大に主張することになる。
        # 1 名ずつ抜いた再計算の範囲を併記する。
        loo = []
        for i in range(len(groups)):
            v, _ = _icc1([g for j, g in enumerate(groups) if j != i])
            if v is not None:
                loo.append(v)
        # η² = SSB/SST も併記する。`.idea` §1.4 が「ICC」と書いていた値の正体がこれで
        # (f1=0.060 f3=0.055 f4=0.159 f5=0.156 と 3 桁一致・probe_variants.py で確認)、
        # 併記しておかないと将来また「1.2-1.3 倍ずれている」と追跡し直すことになる。
        # η² は群平方和に自由度 k-1 しか与えないので、群数 k が小さいと ICC を
        # 系統的に過小評価する (k=5 の本データで 0.75-0.78 倍)。
        # 「個人差の割合 = 分散成分比」を主張したいなら ICC(1) の方が正しい推定量。
        eta2 = ssb / (ssb + ssw) if (ssb + ssw) else None
        out[f] = {"icc": round(icc, 4), "n_total": n_total, "n_groups": k_groups,
                  "k0": round(k0, 2), "msb": msb, "msw": msw,
                  "eta_squared": round(eta2, 4) if eta2 is not None else None,
                  "loo_min": round(min(loo), 4) if loo else None,
                  "loo_max": round(max(loo), 4) if loo else None}
    return out


# ---------------------------------------------------------------- D6 / D7
def d6_d7(subjects):
    dead = {}
    paste = {}
    for pid, sessions in subjects.items():
        nav_nz = ab_nz = shadow_n = 0
        p_cnt = k_cnt = 0
        zero_sessions = 0
        sess_n = 0
        for s in sessions:
            ev = s["ev"]
            for o in ev.get("ime_shadow", []):
                shadow_n += 1
                if o.get("nav"):
                    nav_nz += 1
                if o.get("abandon"):
                    ab_nz += 1
            pk = len(ev.get("paste", []))
            kk = sum(1 for o in ev.get("key", []) if o.get("press"))
            p_cnt += pk
            k_cnt += kk
            # 1 ファイル = 複数セッションのことがあるので session_meta 数で数える
            n_meta = max(1, len(ev.get("session_meta", [])))
            sess_n += n_meta
            if pk == 0:
                zero_sessions += n_meta
        dead[pid] = {"ime_shadow_events": shadow_n,
                     "nav_nonzero": nav_nz, "abandon_nonzero": ab_nz}
        paste[pid] = {
            "paste_events": p_cnt,
            "key_presses": k_cnt,
            "paste_per_1000_keys": round(1000.0 * p_cnt / k_cnt, 2) if k_cnt else None,
            "_paste_per_1000_keys_raw": (1000.0 * p_cnt / k_cnt) if k_cnt else None,
            "sessions": sess_n,
            "sessions_with_zero_paste": zero_sessions,
        }
    # 比は**丸める前の値**で取る。表示用に round した率で割ると比が歪む
    # (実測: 丸め後 99.9 / 生値 96.6 — .idea の「97 倍」と一致するのは後者)。
    # また `if v[...]` の falsy 判定は率ちょうど 0.0 の被験者を黙って除外するので
    # `is not None` で判定する。
    rates = [v["_paste_per_1000_keys_raw"] for v in paste.values()
             if v["_paste_per_1000_keys_raw"] is not None]
    nonzero = [r for r in rates if r > 0]
    ratio = (max(rates) / min(nonzero)) if rates and nonzero else None
    return {"dead_fields": dead,
            "paste": paste,
            "paste_rate_max_min_ratio": round(ratio, 1) if ratio else None,
            "paste_rate_zero_subjects": sum(1 for r in rates if r == 0)}



# ---------------------------------------------------------------- 出力ガード
_PII_PATTERNS = [
    (r"gse_\d{8}", "logger 由来のセッションファイル名 (= 開始絶対時刻)"),
    (r"\.ndjson", "NDJSON ファイル名"),
    # 絶対パスの境界は「区切り文字の直後」ではなく「識別子文字の直後でない」で取る。
    # 旧実装は空白/引用符始まりしか見ておらず `path=/Users/...` `~/gse-dataset` を
    # 素通りさせていた (独立レビュー指摘)。GSE_DATASET は環境ごとに任意パスを取る。
    (r"(?<![\w.])(?:~|/(?:Users|home|Volumes))/", "絶対パス / ホーム相対パス"),
    (r"(?<![\w.])[A-Za-z]:[\\/]", "Windows 絶対パス"),
    (r"\\\\Users\\\\", "Windows 絶対パス (エスケープ済み)"),
    (r"https?://", "URL"),
    # probe_variants.py が内部で使う `P010#3` 形式のセッション識別子。
    # data.md は「セッション単位の生値は出さない」と約束しているが、
    # 現状それを守っているのは集計の構造だけで、機械検査が無かった (独立レビュー指摘)。
    (r"P\d{3}#\d+", "セッション識別子 (pid#session_index)"),
]


def assert_no_pii(obj):
    """出力に生ログ由来の識別子が混ざっていないか検査する (fail-closed)。

    data.md は「集計値のみ・絶対 epoch 時刻なし・ファイル名なし」を約束している。
    将来この診断を拡張したときに、その約束を**黙って**破らないための最終防衛。
    """
    blob = json.dumps(obj, ensure_ascii=False)
    bad = []
    for pat, what in _PII_PATTERNS:
        m = re.search(pat, blob)
        if m:
            bad.append(f"{what} ({m.group(0)!r})")
    # 絶対 epoch ms は 1e12 前後の**整数**。浮動小数の仮数と区別するため int だけ見る。
    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                yield from walk(v, f"{path}[{i}]")
        elif isinstance(o, int) and not isinstance(o, bool) and abs(o) >= 10 ** 12:
            yield path, o

    for path, v in walk(obj):
        bad.append(f"絶対時刻らしき整数 {path}={v}")
    if bad:
        print("[diagnostics] FAILED: 出力に PII らしきものが含まれる — " + " / ".join(bad),
              file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------- main
def main():
    if len(sys.argv) != 6:
        print("usage: diagnostics.py <raw_root> <constants.json|config.json> <out_dir> "
              "<seed> <n_perm>", file=sys.stderr)
        sys.exit(1)
    raw_root, const_path, out_dir, seed, n_perm = sys.argv[1:]
    seed, n_perm = int(seed), int(n_perm)
    const = json.load(open(const_path, encoding="utf-8"))
    # config.json は constants.json と同じディレクトリにある前提
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(const_path)), "config.json")
    cfg = json.load(open(cfg_path, encoding="utf-8")) if os.path.isfile(cfg_path) else {}
    lf = cfg.get("label_filter", {})
    label_source = lf.get("source", "random_probe")
    label_answered = lf.get("answered", True)

    parse_failures = [0]
    subjects = load(raw_root, parse_failures)
    if not subjects:
        print(f"[diagnostics] FAILED: {raw_root} に P0* が無い", file=sys.stderr)
        sys.exit(1)
    if parse_failures[0]:
        # 件数を数えるだけで続けると、途中切断ログが混ざったときに
        # 集計が黙って減る。ADR の入力にする以上ここは止める。
        print(f"[diagnostics] FAILED: NDJSON の parse に失敗した行が "
              f"{parse_failures[0]} 件ある。入力の健全性を先に確認すること",
              file=sys.stderr)
        sys.exit(1)

    # 対象被験者は config で宣言する。ディスク上の状態依存にすると
    # raw/ に別の P0XX が置かれた瞬間に黙って混入する。
    want = cfg.get("subjects")
    if want and sorted(subjects) != sorted(want):
        print(f"[diagnostics] FAILED: 被験者集合が config と違う "
              f"(config={sorted(want)} / 実際={sorted(subjects)})", file=sys.stderr)
        sys.exit(1)

    versions = collections.Counter(
        o.get("hmm_version") for ss in subjects.values() for s in ss
        for o in s["ev"].get("meta", []) if o.get("hmm_version")
    )
    expected = cfg.get("hmm_version_expected") if cfg else None
    if expected and set(versions) != {expected}:
        print(f"[diagnostics] FAILED: hmm_version が期待値 {expected!r} と違う: "
              f"{dict(versions)}", file=sys.stderr)
        sys.exit(1)

    inventory = {
        pid: {
            "files": len(ss),
            "sessions": sum(max(1, len(s["ev"].get("session_meta", []))) for s in ss),
            "feat": sum(len(s["ev"].get("feat", [])) for s in ss),
            "answered_random_probe": sum(
                sum(1 for o in s["ev"].get("realtime_label", [])
                    if o.get("source") == "random_probe" and o.get("answered"))
                for s in ss),
        }
        for pid, ss in subjects.items()
    }

    per, counts = window_rows(subjects, label_source, label_answered)
    extra = ["keys", "bs_rate", "paste_count", "paste_chars", "ime_dwell_med"]
    res = {
        "seed": seed,
        "n_perm": n_perm,
        "hmm_version": dict(versions),
        "json_parse_failures": parse_failures[0],
        "inventory": inventory,
        "inventory_total": {
            "files": sum(v["files"] for v in inventory.values()),
            "sessions": sum(v["sessions"] for v in inventory.values()),
            "feat": sum(v["feat"] for v in inventory.values()),
            "answered_random_probe": sum(v["answered_random_probe"] for v in inventory.values()),
        },
        "label_windows": dict(counts),
        "D1_D5_cindex_permutation": d1_d5(per, seed, n_perm, extra),
        "D2_D3_phi_rails_and_x": d2_d3(subjects, const),
        "D4_icc": d4_icc(subjects),
        "D6_D7_dead_fields_and_paste": d6_d7(subjects),
    }
    # ---- 検算 (fail-closed): Python 側 φ 実装が Rust と等価か
    # 厳密一致は logger.rs の丸め (f1:.2 / f5:.1 / raw_x:.4) のため原理的に不可能。
    # 「丸め由来の小さな残差が大多数・文脈誤判定由来の大きな残差がごく少数」を閾値にする。
    chk = res["D2_D3_phi_rails_and_x"]["x_recalc_vs_logged"]["ime_state_derived"]
    rs = chk["residual"]
    problems = []
    if chk["pearson_r"] is None or chk["pearson_r"] < 0.999:
        problems.append(f"pearson_r={chk['pearson_r']} < 0.999")
    if rs["median"] > 1e-3:
        problems.append(f"残差中央値={rs['median']} > 1e-3")
    if rs["gt_0_01_pct"] > 0.5:
        problems.append(f"残差>0.01 の割合={rs['gt_0_01_pct']}% > 0.5%")
    if problems:
        print("[diagnostics] FAILED: Python φ が Rust と等価でない — "
              + " / ".join(problems), file=sys.stderr)
        print("  engine.rs の合成式か β が変わった可能性がある。"
              "extract_constants.py の形状チェックを通り抜ける変更に注意。", file=sys.stderr)
        sys.exit(1)
    res["phi_equivalence_check"] = {
        "passed": True,
        "thresholds": {"pearson_r_min": 0.999, "residual_median_max": 1e-3,
                       "gt_0_01_pct_max": 0.5},
        "observed": {"pearson_r": chk["pearson_r"], "residual_median": rs["median"],
                     "gt_0_01_pct": rs["gt_0_01_pct"]},
    }

    assert_no_pii(res)

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "diagnostics.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    render(res, os.path.join(out_dir, "diagnostics.txt"))

    # metrics.json = 共有する主要指標だけを抜き出したもの (docs/experiment-tracking.md の規約)
    dd = res["D1_D5_cindex_permutation"]
    pd_ = res["D6_D7_dead_fields_and_paste"]
    rails = res["D2_D3_phi_rails_and_x"]["rails"]["beta_writing_fixed"]
    metrics = {
        "experiment": "20260801-signal-diagnostics",
        "kind": "exploratory",
        "hmm_version": res["hmm_version"],
        "n_feat": res["inventory_total"]["feat"],
        "n_labels": res["inventory_total"]["answered_random_probe"],
        "x_axis_cells_computable": dd["x_axis_cells_computable"],
        "x_axis_nominal_sig_count": dd["x_axis_nominal_sig_count"],
        "nominal_sig_count": dd["nominal_sig_count"],
        "bonferroni_attainable_count": dd["bonferroni_attainable_count"],
        "bonferroni_passed_count": dd["bonferroni_passed_count"],
        "phi_rail_pct_beta_writing": {k: v["rail_pct"] for k, v in rails.items()},
        "icc": {k: {"point": v.get("icc"), "loo_min": v.get("loo_min"),
                    "loo_max": v.get("loo_max"), "eta_squared": v.get("eta_squared")}
                for k, v in res["D4_icc"].items()},
        "paste_rate_max_min_ratio": pd_["paste_rate_max_min_ratio"],
        "phi_equivalence_check": res.get("phi_equivalence_check", {}).get("passed"),
    }
    with open(os.path.join(out_dir, "..", "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"[diagnostics] OK -> {out_dir}/diagnostics.json / diagnostics.txt / ../metrics.json")


def render(res, path):
    L = []
    a = L.append
    inv = res["inventory_total"]
    a("########## 入力インベントリ")
    a(f"files={inv['files']} sessions={inv['sessions']} feat={inv['feat']} "
      f"answered_random_probe={inv['answered_random_probe']}")
    a(f"hmm_version={res['hmm_version']} json_parse_failures={res['json_parse_failures']}")
    pe = res.get("phi_equivalence_check", {})
    a(f"φ 等価性検査: {'PASS' if pe.get('passed') else 'N/A'} {pe.get('observed', '')}")
    a(f"ラベル窓: {res['label_windows']}")
    a("")

    d = res["D1_D5_cindex_permutation"]
    a("########## D1/D5 並べ替え検定 (被験者内シャッフル)")
    a(f"セル総数={d['cells_total']} 算出可能={d['cells_computable']} "
      f"算出不能={d['cells_uncomputable']}")
    a(f"  うち既存特徴量セル: {d['cells_core_computable']}/{d['cells_core_total']} 算出可能")
    a(f"  うち追加信号セル  : {d['cells_extra_computable']}/{d['cells_extra_total']} 算出可能")
    a(f"  X 系 (Q1 対象・既存5特徴量+raw_x): 算出可能={d['x_axis_cells_computable']} "
      f"名目有意={d['x_axis_nominal_sig_count']} 件")
    thr = d["bonferroni_threshold"]
    thr_s = f"{thr:.6f}" if thr is not None else "—"
    a(f"名目 p<0.05 = {d['nominal_sig_count']} 件 / Bonferroni 閾値={thr_s} "
      f"通過={d['bonferroni_passed_count']} 件")
    a(f"  ※ Bonferroni に**原理的に到達可能**なセルは {d['bonferroni_attainable_count']}/"
      f"{d['cells_computable']} 件")
    a("     (n が小さいセルは厳密並べ替えの p 下限 ~2/M が閾値を上回る。"
      "2/M は離散性を無視した近似なので目安)")
    if d["nominal_sig"]:
        a("-- 名目有意 (p 昇順) --")
        for c in d["nominal_sig"]:
            a(f"  {c['target']:<12} {c['feature']:<14} {c['subject']} "
              f"n={c['n']:<4} C={c['cindex']:.3f} p={c['p']:.4f}")
    a("")

    r = res["D2_D3_phi_rails_and_x"]
    a("########## D2 φ レール飽和率")
    for mode in ("beta_writing_fixed", "ime_state_derived"):
        a(f"-- {mode} --")
        a(f"{'phi':<6}{'0に張付':>10}{'1.0飽和':>10}{'レール上':>10}{'n':>10}")
        for f, v in r["rails"][mode].items():
            a(f"{f:<6}{v['zero_pct']:>9.1f}%{v['one_pct']:>9.1f}%"
              f"{v['rail_pct']:>9.1f}%{v['total']:>10}")
    a(f"ime_state 由来の文脈内訳: {r['ime_state_derived_context_counts']}")
    a("")
    a("########## D3 X の再計算と項ごとの寄与")
    xv = r["x_recalc_vs_logged"]
    a(f"(n={r['feat_samples_used_for_x']})")
    for mode in ("beta_writing_fixed", "ime_state_derived"):
        m = xv[mode]
        a(f"  {mode:<20} max_abs_err={m['max_abs_error']:.6g} r={m['pearson_r']}")
        rs = m.get("residual")
        if rs:
            a(f"    残差 |Δ|: 中央={rs['median']:.6g} p95={rs['p95']:.6g} "
              f"max={rs['max']:.6g} / >0.01 の件数={rs['gt_0_01']} ({rs['gt_0_01_pct']}%)")
    a("  -- 相関 (β_writing 項 × 記録 X) --")
    for k, v in r["term_correlations_with_logged_x"].items():
        a(f"    {k} = {v}")
    a("  -- 相関 (実 β 項 × 記録 X = 基準が揃った条件) --")
    for k, v in r["term_correlations_real_beta"].items():
        a(f"    {k} = {v}")
    a("  -- 相関 (β_writing 項 × 再計算 X(β_writing) = .idea §1.3 の条件) --")
    for k, v in r["term_correlations_with_recalc_x_beta_writing"].items():
        a(f"    {k} = {v}")
    a("  -- 標準化寄与 sd(項)/sd(X) — 「どの項が X を動かすか」はこちら --")
    for k, v in r["standardized_contributions"].items():
        a(f"    {k}: {v}")
    a("")

    a("########## D4 ICC (群=被験者・feat 全件)")
    a(f"{'feat':<6}{'ICC(1)':>9}{'LOO範囲':>18}{'η²':>9}{'n':>10}{'groups':>8}")
    for f, v in res["D4_icc"].items():
        icc = f"{v['icc']:.4f}" if v.get("icc") is not None else "—"
        loo = ("{:.3f}–{:.3f}".format(v["loo_min"], v["loo_max"])
               if v.get("loo_min") is not None else "—")
        eta = f"{v['eta_squared']:.4f}" if v.get("eta_squared") is not None else "—"
        a(f"{f:<6}{icc:>9}{loo:>18}{eta:>9}"
          f"{v.get('n_total','—'):>10}{v.get('n_groups','—'):>8}")
    a("  ※ η² = SSB/SST は `.idea` §1.4 が「ICC」と書いていた値 (3 桁一致)。")
    a("     群数 k=5 では ICC を 0.75-0.78 倍に過小評価する。主張には ICC(1) を使う。")
    a("")

    dd = res["D6_D7_dead_fields_and_paste"]
    a("########## D6 ime_shadow の死んだフィールド")
    a(f"{'pid':<7}{'shadow件数':>12}{'nav≠0':>8}{'abandon≠0':>11}")
    for pid, v in dd["dead_fields"].items():
        a(f"{pid:<7}{v['ime_shadow_events']:>12}{v['nav_nonzero']:>8}{v['abandon_nonzero']:>11}")
    a("")
    a("########## D7 paste の被験者間分散")
    a(f"{'pid':<7}{'paste':>8}{'打鍵':>9}{'/1000打鍵':>11}{'0pasteセッション':>18}")
    for pid, v in dd["paste"].items():
        rate = v["paste_per_1000_keys"]
        rate_s = f"{rate:.2f}" if rate is not None else "—"
        zero_s = "{}/{}".format(v["sessions_with_zero_paste"], v["sessions"])
        a(f"{pid:<7}{v['paste_events']:>8}{v['key_presses']:>9}{rate_s:>11}{zero_s:>18}")
    a(f"最大/最小比 = {dd['paste_rate_max_min_ratio']}")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
