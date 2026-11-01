"""conditions.md C4〜C5（L1〜L6）の記述の集計。検定はしない。

使い方:
  python3 -I analyze_landscape.py <klicke_work.tar.gz> <klicke_side.json> <coauthor_work_dir> <holdout.json> <out_dir>
  python3 -I analyze_landscape.py --selftest
出力は集計値だけ（書き手・セッションの ID も番号も出さない）: <out_dir>/landscape.json・counts.json。
"""
import bisect
import glob
import json
import math
import os
import statistics
import sys
import tarfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "../../20261101-klicke-early-stall-trigger/scripts"))
import analyze_item2 as t2  # noqa: E402  T2 の定義（TEXT・Theta・fires_current）をそのまま使う

TEXT = t2.TEXT
NAV = "navigation"
GAP_THR_S = [2, 5, 10, 30, 60, 180]
AI_PAD = 60_000
PRE_WIN = 30_000
AWAY = 180_000
RECEIPT_WIN = 5 * 60_000
MIN_WRITER_OBS = 10 * 60_000
MIN_STALLS_FOR_MEDIAN = 5
L5_MIN_SESSIONS, L5_MIN_OBS = 5, 5 * 60_000
P_TRIG = 0.60
H = 3_600_000


# ---------- 区間の道具 ----------

def merge(ivs):
    out = []
    for a, b in sorted(ivs):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def overlap_len(ivs_a, ivs_b):
    """2 つの区間の集まり（各々は重なりなしに併合済み）の重なりの長さ。"""
    i = j = 0
    tot = 0
    while i < len(ivs_a) and j < len(ivs_b):
        lo = max(ivs_a[i][0], ivs_b[j][0])
        hi = min(ivs_a[i][1], ivs_b[j][1])
        if hi > lo:
            tot += hi - lo
        if ivs_a[i][1] < ivs_b[j][1]:
            i += 1
        else:
            j += 1
    return tot


def count_in(sorted_ts, a, b, lo_open=False, hi_open=False):
    lo = bisect.bisect_right(sorted_ts, a) if lo_open else bisect.bisect_left(sorted_ts, a)
    hi = bisect.bisect_left(sorted_ts, b) if hi_open else bisect.bisect_right(sorted_ts, b)
    return max(0, hi - lo)


def quart(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    q = statistics.quantiles(xs, n=4, method="inclusive") if len(xs) > 1 else [xs[0]] * 3
    return {"n": len(xs), "q1": round(q[0], 4), "median": round(statistics.median(xs), 4), "q3": round(q[2], 4)}


def pooled(num, den):
    return {"num": num, "den": den, "ratio": round(num / den, 4) if den else None}


# ---------- 1 セッション ----------

class Session:
    def __init__(self, d, clicks=(), receipts=(), ai=()):
        self.keys = d["keys"]
        self.press = [k[0] for k in self.keys]
        self.cats = [k[1] for k in self.keys]
        self.feat = d["feat"]
        self.onsets = d["onsets"]
        self.intervals = [tuple(iv) for iv in d["observed_intervals"]]
        self.text = [t for t, c in self.keys if c in TEXT]
        self.nontext = [t for t, c in self.keys if c not in TEXT]
        self.nav = [t for t, c in self.keys if c == NAV]
        self.clicks = sorted(clicks)
        self.receipts = sorted(receipts)
        self.ai = sorted(ai)
        self.t_start, self.t_end = self.press[0], self.press[-1]
        self.theta = t2.Theta(self.press, self.intervals)
        self.ai_cover = merge([[t - AI_PAD, t + AI_PAD] for t in self.ai])

    # 長さ
    def obs_ms(self):
        return sum(b - a for a, b in self.intervals)

    def span_ms(self):
        return self.t_end - self.t_start

    def normal_obs_ms(self):
        return self.obs_ms() - overlap_len(merge([list(iv) for iv in self.intervals]), self.ai_cover)

    def normal_span_ms(self):
        return self.span_ms() - overlap_len([[self.t_start, self.t_end]], self.ai_cover)

    def near_ai(self, a, b):
        return count_in(self.ai, a - AI_PAD, b + AI_PAD) > 0

    def theta_last(self):
        for v in reversed(self.theta.step):
            if v is not None:
                return v
        return None

    def gaps(self):
        return list(zip(self.press, self.press[1:]))

    def resume(self, t0):
        i = bisect.bisect_right(self.text, t0)
        return self.text[i] if i < len(self.text) else None

    def stalls(self):
        """[(s, t0, resume or None, end_of_window)]"""
        out = []
        for o in self.onsets:
            s, t0 = o[0], o[1]
            r = self.resume(t0)
            out.append((s, t0, r, r if r is not None else self.t_end))
        return out

    def feat_in_obs(self):
        out = []
        for t, p, x in self.feat:
            if any(a <= t <= b for a, b in self.intervals):
                out.append((t, p if p is not None and math.isfinite(p) else 0.0, x))
        return out


# ---------- 1 書き手（セッションの集まり） ----------

def writer_l1(sessions, normal):
    span = sum(s.normal_span_ms() if normal else s.span_ms() for s in sessions)
    obs = sum(s.normal_obs_ms() if normal else s.obs_ms() for s in sessions)
    gcount = {thr: 0 for thr in GAP_THR_S}
    gtot = 0
    stalls, durs, censored = 0, [], 0
    for s in sessions:
        for a, b in s.gaps():
            if normal and s.near_ai(a, b):
                continue
            gtot += 1
            for thr in GAP_THR_S:
                if b - a >= thr * 1000:
                    gcount[thr] += 1
        for st, t0, r, end in s.stalls():
            if normal and s.near_ai(st - PRE_WIN, end):
                continue
            stalls += 1
            if r is None:
                censored += 1
            else:
                durs.append((r - t0) / 1000)
    return {"span_ms": span, "obs_ms": obs, "gaps": gtot, "gap_counts": gcount, "stalls": stalls,
            "durs": durs, "censored": censored}


def writer_l2(sessions, normal):
    ps, xs, fires, obs = [], [], 0, 0
    for s in sessions:
        rows = s.feat_in_obs()
        if normal:
            rows = [r for r in rows if not s.near_ai(r[0], r[0])]
        ps += [r[1] for r in rows]
        xs += [r[2] for r in rows if r[2] is not None and math.isfinite(r[2])]
        fs = t2.fires_current(s)
        if normal:
            fs = [f for f in fs if not s.near_ai(f, f)]
        fires += len(fs)
        obs += s.normal_obs_ms() if normal else s.obs_ms()
    if not ps:
        return None
    xs_sorted = sorted(xs)
    return {"p_median": statistics.median(ps), "p_ge": sum(1 for p in ps if p >= P_TRIG) / len(ps),
            "x_median": statistics.median(xs) if xs else None,
            "x_p90": xs_sorted[min(len(xs_sorted) - 1, math.ceil(0.9 * len(xs_sorted)) - 1)] if xs else None,
            "fires_per_h": fires / (obs / H) if obs else None, "fires": fires}


def writer_l3(sessions, normal):
    rec = []
    for s in sessions:
        for st, t0, r, end in s.stalls():
            if normal and s.near_ai(st - PRE_WIN, end):
                continue
            pre = (st - PRE_WIN, t0)
            row = {}
            for name, ts in (("nontext", s.nontext), ("nav", s.nav), ("click", s.clicks)):
                row["pre_" + name] = count_in(ts, *pre) > 0
                row["post_" + name] = count_in(ts, t0, end, lo_open=True, hi_open=r is not None) > 0
            rec.append(row)
    return rec


def writer_l4(sessions):
    span = sum(s.span_ms() for s in sessions)
    receipts = sum(len(s.receipts) for s in sessions)
    st_tot = st_before = st_5min = 0
    away = away_rec = 0
    for s in sessions:
        for st, t0, r, end in s.stalls():
            st_tot += 1
            if count_in(s.receipts, t0, end, lo_open=True) > 0:
                st_before += 1
            if count_in(s.receipts, t0, t0 + RECEIPT_WIN, lo_open=True) > 0:
                st_5min += 1
        for a, b in s.gaps():
            if b - a >= AWAY:
                away += 1
                if count_in(s.receipts, b, b + RECEIPT_WIN) > 0:
                    away_rec += 1
    return {"span_ms": span, "receipts": receipts, "stalls": st_tot, "receipt_before_resume": st_before,
            "receipt_5min": st_5min, "away": away, "away_receipt_5min": away_rec}


def writer_l6(sessions):
    """各セッションを 3 等分し、セッションの値を出す（書き手の値は呼び出し側で中央値）。"""
    out = []
    for s in sessions:
        L = s.span_ms()
        if L <= 0:
            continue
        cuts = [s.t_start + L * k / 3 for k in range(4)]
        ivs = merge([list(iv) for iv in s.intervals])
        rows = s.feat_in_obs()
        row = {}
        for k in range(3):
            a, b = cuts[k], cuts[k + 1]
            ob = overlap_len(ivs, [[a, b]])
            n = sum(1 for o in s.onsets if a <= o[1] < b or (k == 2 and o[1] == b))
            fr = [r for r in rows if a <= r[0] < b or (k == 2 and r[0] == b)]
            dfrom = s.theta.defined_from
            tdef = 0 if dfrom is None else max(0.0, b - max(a, dfrom)) if dfrom < b else 0
            row[k] = {"stall_per_h": n / (ob / H) if ob > 0 else None,
                      "p_ge": sum(1 for r in fr if r[1] >= P_TRIG) / len(fr) if fr else None,
                      "x_median": statistics.median([r[2] for r in fr if r[2] is not None]) if fr else None,
                      "theta_defined_frac": tdef / (b - a) if b > a else None}
        out.append(row)
    return out


# ---------- 書き手の分布へ ----------

def summarize(writers, normal, has_click):
    """writers: [[Session, ...], ...]（観測時間で絞った後）"""
    l1 = [writer_l1(w, normal) for w in writers]
    res = {"writers": len(writers)}
    gtot = sum(x["gaps"] for x in l1)
    res["L1"] = {
        "gap_share_pooled": {str(thr): pooled(sum(x["gap_counts"][thr] for x in l1), gtot) for thr in GAP_THR_S},
        "gap_per_h": {str(thr): quart([x["gap_counts"][thr] / (x["span_ms"] / H) for x in l1 if x["span_ms"] > 0])
                      for thr in GAP_THR_S},
        "theta_last_s": quart([statistics.median(v) / 1000 for v in
                               [[t for t in (s.theta_last() for s in w) if t is not None] for w in writers] if v]),
        "stall_per_h": quart([x["stalls"] / (x["obs_ms"] / H) for x in l1 if x["obs_ms"] > 0]),
        "stalls": sum(x["stalls"] for x in l1),
        "stall_duration_s": quart([d for x in l1 for d in x["durs"]]),
        "stall_censored": sum(x["censored"] for x in l1),
    }
    l2 = [x for x in (writer_l2(w, normal) for w in writers) if x]
    res["L2"] = {"writers": len(l2),
                 "p_stuck_median": quart([x["p_median"] for x in l2]),
                 "p_stuck_ge_060_share": quart([x["p_ge"] for x in l2]),
                 "p_stuck_ge_060_writers_with_zero": sum(1 for x in l2 if x["p_ge"] == 0),
                 "ewma_x_median": quart([x["x_median"] for x in l2]),
                 "ewma_x_p90": quart([x["x_p90"] for x in l2]),
                 "current_trigger_per_h": quart([x["fires_per_h"] for x in l2]),
                 "current_trigger_writers_with_zero": sum(1 for x in l2 if x["fires"] == 0)}
    l3w = [writer_l3(w, normal) for w in writers]
    names = ["nontext", "nav"] + (["click"] if has_click else [])
    l3 = {}
    for side in ("pre", "post"):
        for nm in names:
            key = side + "_" + nm
            allrows = [r[key] for rows in l3w for r in rows]
            l3[key] = {"pooled": pooled(sum(allrows), len(allrows)),
                       "writer_median": quart([sum(r[key] for r in rows) / len(rows) for rows in l3w
                                               if len(rows) >= MIN_STALLS_FOR_MEDIAN])}
    res["L3"] = l3
    return res


def summarize_l4(writers):
    l4 = [writer_l4(w) for w in writers]
    return {"writers": len(l4),
            "receipt_per_h": quart([x["receipts"] / (x["span_ms"] / H) for x in l4 if x["span_ms"] > 0]),
            "receipt_writers_with_zero": sum(1 for x in l4 if x["receipts"] == 0),
            "stall_receipt_before_resume": pooled(sum(x["receipt_before_resume"] for x in l4),
                                                  sum(x["stalls"] for x in l4)),
            "stall_receipt_within_5min": pooled(sum(x["receipt_5min"] for x in l4), sum(x["stalls"] for x in l4)),
            "away_per_h": quart([x["away"] / (x["span_ms"] / H) for x in l4 if x["span_ms"] > 0]),
            "away_count_per_writer": quart([x["away"] for x in l4]),
            "away_writers_with_zero": sum(1 for x in l4 if x["away"] == 0),
            "away_receipt_within_5min": pooled(sum(x["away_receipt_5min"] for x in l4), sum(x["away"] for x in l4))}


def summarize_l6(writers):
    per_writer = []
    for w in writers:
        rows = writer_l6(w)
        if not rows:
            continue
        agg = {}
        for k in range(3):
            agg[k] = {m: (statistics.median(v) if v else None) for m, v in
                      ((m, [r[k][m] for r in rows if r[k][m] is not None])
                       for m in ("stall_per_h", "p_ge", "x_median", "theta_defined_frac"))}
        per_writer.append(agg)
    out = {}
    for k, nm in enumerate(("early", "middle", "late")):
        out[nm] = {m: quart([w[k][m] for w in per_writer]) for m in
                   ("stall_per_h", "p_ge", "x_median", "theta_defined_frac")}
    out["writers"] = len(per_writer)
    return out


def summarize_l5(writers):
    """CoAuthor: θ が定義され観測 5 分以上のセッションが 5 本以上ある書き手。"""
    rates, thetas, counts = [], [], []
    for w in writers:
        ok = [s for s in w if s.theta.defined_from is not None and s.obs_ms() >= L5_MIN_OBS]
        if len(ok) < L5_MIN_SESSIONS:
            continue
        rates.append([len(s.onsets) / (s.obs_ms() / H) for s in ok])
        thetas.append([s.theta_last() / 1000 for s in ok])
        counts += [len(s.onsets) for s in ok]

    def decompose(groups):
        if len(groups) < 2:
            return None
        means = [statistics.mean(g) for g in groups]
        var_between = statistics.variance(means)
        var_within = statistics.mean(statistics.variance(g) for g in groups)
        return {"writers": len(groups), "sessions": sum(len(g) for g in groups),
                "grand_mean": round(statistics.mean(means), 4),
                "sd_between_writer_means": round(math.sqrt(var_between), 4),
                "sd_within_mean": round(statistics.mean(statistics.stdev(g) for g in groups), 4),
                "between_share": round(var_between / (var_between + var_within), 4)
                if var_between + var_within > 0 else None}
    return {"stall_per_h": decompose(rates), "theta_last_s": decompose(thetas),
            "stalls_per_session": quart(counts)}


# ---------- 読み込み ----------

def load_klicke(tar_p, side_p, hold):
    side = json.load(open(side_p))
    out, seen_hold = [], 0
    with tarfile.open(tar_p, "r:gz") as tf:
        for m in tf:
            b = m.name.rsplit("/", 1)[-1]
            if not (b.startswith("w") and b.endswith(".json")):
                continue
            idx = int(b[1:-5])
            if idx in hold:
                seen_hold += 1
                continue
            d = json.load(tf.extractfile(m))
            sd = side["%05d" % idx]
            out.append([Session(d, clicks=sd["clicks"], receipts=sd["pastes"])])
    return out, seen_hold


def load_coauthor(work, hold_n):
    sess_w = json.load(open(os.path.join(work, "sessions.json")))
    by_w = {}
    for p in sorted(glob.glob(os.path.join(work, "s*.json"))):
        k = os.path.basename(p)[1:-5]
        if k not in sess_w:
            continue
        d = json.load(open(p))
        rec = [t for t, n in d["events"] if n in ("suggestion-select", "multi-insert")]
        ai = [t for t, n in d["events"] if n.startswith("suggestion") or n == "api-insert"]
        by_w.setdefault(sess_w[k], []).append(Session(d, receipts=rec, ai=ai))
    return [by_w[w] for w in sorted(by_w)]


def run(tar_p, side_p, cwork, hold_p, out_dir):
    hold = json.load(open(hold_p))
    kw, seen = load_klicke(tar_p, side_p, set(hold["klicke"]))
    side_keys = set(json.load(open(side_p)))
    if side_keys & {"%05d" % i for i in hold["klicke"]}:
        sys.exit("取っておく書き手が KLiCKe の補いに入っている")
    cw = load_coauthor(cwork, len(hold["coauthor"]))
    counts = {"klicke": {"writers_loaded": len(kw), "holdout_skipped_in_tar": seen},
              "coauthor": {"writers_loaded": len(cw), "sessions_loaded": sum(len(w) for w in cw)}}
    k_el = [w for w in kw if sum(s.obs_ms() for s in w) >= MIN_WRITER_OBS]
    c_el = [w for w in cw if sum(s.obs_ms() for s in w) >= MIN_WRITER_OBS]
    counts["klicke"]["excluded_obs_lt_10min"] = len(kw) - len(k_el)
    counts["coauthor"]["excluded_obs_lt_10min"] = len(cw) - len(c_el)
    counts["coauthor"]["sessions_eligible"] = sum(len(w) for w in c_el)
    res = {"klicke": summarize(k_el, normal=False, has_click=True),
           "coauthor_normal": summarize(c_el, normal=True, has_click=False),
           "coauthor_all": summarize(c_el, normal=False, has_click=False)}
    res["klicke"]["L4"] = summarize_l4(k_el)
    res["coauthor_all"]["L4"] = summarize_l4(c_el)
    res["coauthor_all"]["L5"] = summarize_l5(c_el)
    res["klicke"]["L6"] = summarize_l6(k_el)
    res["coauthor_all"]["L6"] = summarize_l6(c_el)
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(os.path.join(out_dir, "landscape.json"), "w"), indent=1)
    json.dump(counts, open(os.path.join(out_dir, "counts.json"), "w"), indent=1)
    print(json.dumps(counts))


# ---------- 自己検査（合成の入力） ----------

def selftest():
    assert merge([[0, 5], [3, 8], [10, 12]]) == [[0, 8], [10, 12]]
    assert overlap_len([[0, 10]], [[5, 15]]) == 5
    assert overlap_len([[0, 10], [20, 30]], [[5, 25]]) == 10
    assert count_in([1, 2, 3], 1, 3) == 3
    assert count_in([1, 2, 3], 1, 3, lo_open=True) == 2
    assert count_in([1, 2, 3], 1, 3, lo_open=True, hi_open=True) == 1
    # 1 秒ごとの 'a' を 200 回、60 秒の沈黙、また 50 回
    press = [i * 1000 for i in range(200)] + [259_000 + i * 1000 for i in range(50)]
    d = {"keys": [[t, "alphabetic"] for t in press], "feat": [[t, 0.7, 0.1] for t in press],
         "onsets": [[229_000, 235_000, 1000, 199]], "observed_intervals": [[0, 199_000], [259_000, 308_000]]}
    s = Session(d, clicks=[230_000], receipts=[259_000], ai=[500_000])
    assert s.resume(235_000) == 259_000
    assert s.span_ms() == 308_000 and s.obs_ms() == 199_000 + 49_000
    assert s.normal_span_ms() == 308_000  # AI は区間の外
    s2 = Session(d, ai=[100_000])
    assert s2.normal_obs_ms() == s2.obs_ms() - 120_000
    assert s2.near_ai(150_000, 160_000) and not s2.near_ai(170_000, 180_000)
    l1 = writer_l1([s], normal=False)
    assert l1["gap_counts"][30] == 1 and l1["gap_counts"][60] == 1 and l1["gap_counts"][180] == 0
    assert l1["stalls"] == 1 and l1["durs"] == [24.0] and l1["censored"] == 0
    l3 = writer_l3([s], normal=False)
    assert l3[0]["pre_click"] and not l3[0]["post_click"] and not l3[0]["pre_nontext"]
    l4 = writer_l4([s])
    # 受領は再開の時刻と同じ（含む）
    assert l4["receipt_before_resume"] == 1 and l4["receipt_5min"] == 1 and l4["away"] == 0
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(*sys.argv[1:6])
