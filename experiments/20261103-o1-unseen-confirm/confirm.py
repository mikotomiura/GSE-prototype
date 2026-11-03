"""O1 の見ていない期間での H4a・H5 の確かめと C1・C2・C6 の読みの並べ（conditions.md U1〜U5）。

usage:
  confirm.py --selftest                                   （U5 の陽性対照）
  confirm.py <work_dir> <seed_file> <out_json> <ndjson>...
入力は build_o1.py の中間だけ（NDJSON は SHA-256 の照合にだけ使う）。出力は集計値だけ（時刻・ファイル名・日付を出さない）。
"""
import bisect
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C1C2C6 = os.path.join(HERE, "../20261103-stall-candidates-c1c2c6")
sys.path.insert(0, C1C2C6)
import candidates as cc  # noqa: E402  検出器・Day・day_rows・summarize（K2〜K6）
tc, ao = cc.tc, cc.ao

H = tc.H
MIN_DAYS = 5                 # 判断 2
MIN_DAY_OBS = 4 * H          # 判断 2
MIN_BOUT_OBS = 60 * 60_000   # 判断 4
MIN_BOUTS = 10               # 判断 5（Claude が置いた下限）
B = 2000                     # ブートストラップ・並べ替えの回数
MIN_HALF_COUNT = 40          # 判断 7（H5 の前半と後半の件数の合計の下限）
ALPHA = 0.05
SD_RATIO_MIN = 1.5
PHI_UPPER_MAX = 2.25
RR_REFUTE = 1.25
FOURTEEN = os.path.join(C1C2C6, "results/candidates.json")


# ---------- χ² 分布（標準ライブラリだけ） ----------

def _gammainc_lower(a, x):
    """正規化した下側の不完全ガンマ P(a, x)。"""
    if x <= 0:
        return 0.0
    if x < a + 1:
        term = s = 1.0 / a
        n = a
        for _ in range(10_000):
            n += 1
            term *= x / n
            s += term
            if abs(term) < abs(s) * 1e-15:
                break
        return s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # 連分数（上側）
    b = x + 1 - a
    c = 1e300
    d = 1 / b
    h = d
    for i in range(1, 10_000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return 1 - math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi2_cdf(x, k):
    return _gammainc_lower(k / 2, x / 2)


def chi2_sf(x, k):
    return 1 - chi2_cdf(x, k)


def chi2_ppf(p, k):
    lo, hi = 0.0, max(10.0, 10.0 * k)
    while chi2_cdf(hi, k) < p:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if chi2_cdf(mid, k) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------- U1 日の選び方 ----------

def select_days(inters):
    """inters: 中間の dict の列。戻り値: (使う中間, 外した数の内訳)。"""
    used, excl = [], {"no_focus": 0, "obs_lt_4h": 0}
    for d in inters:
        if not d["focus"]:
            excl["no_focus"] += 1
            continue
        obs = sum(iv["b_ms"] - iv["a_ms"] for iv in d["observed_intervals"])
        if obs < MIN_DAY_OBS:
            excl["obs_lt_4h"] += 1
            continue
        used.append(d)
    return used, excl


# ---------- U2 H4a ----------

def post_warm(intervals, wend):
    """θ の温まり（wend より前）を除いた観測区間。wend が None なら空（判断 7）。"""
    if wend is None:
        return []
    return [(max(a, wend), b) for a, b in sorted(intervals) if b > max(a, wend)]


def h4a_stats(units):
    """units: [(obs_ms, n)]。主の量（判定の前・値は丸めない）。"""
    units = [u for u in units if u[0] > 0]
    D = len(units)
    tot_n = sum(n for _, n in units)
    tot_t = sum(t for t, _ in units) / H
    if D < 2 or tot_n == 0:
        return {"days": D, "defined": False}
    lam = tot_n / tot_t
    x2 = sum((n - lam * t / H) ** 2 / (lam * t / H) for t, n in units)
    k = D - 1
    # SD の比は analyze_o1.unit_sd と同じ式を、丸めずに計算する（unit_sd は 4 桁に丸めて返す）
    rates = [n / (t / H) for t, n in units]
    sd_b = statistics.stdev(rates)
    sd_p = statistics.mean(math.sqrt(statistics.mean(rates) / (t / H)) for t, _ in units)
    ratio = sd_b / sd_p if sd_p else None
    return {"days": D, "defined": True, "pooled_per_h": lam, "X2": x2, "df": k, "phi": x2 / k,
            "p_one_sided": chi2_sf(x2, k), "phi_upper95": x2 / chi2_ppf(0.025, k),
            "sd_between": sd_b, "sd_poisson": sd_p, "sd_ratio": ratio}


def h4a_verdict(st):
    if st["days"] < MIN_DAYS:
        return "undetermined_days"
    if not st["defined"]:
        return "undetermined"
    support = st["p_one_sided"] < ALPHA and st["sd_ratio"] is not None and st["sd_ratio"] >= SD_RATIO_MIN
    refute = st["phi_upper95"] < PHI_UPPER_MAX
    if support and refute:
        sys.exit("H4a: 支持と反証が同時に立った（U2）")
    return "support" if support else "refute" if refute else "undetermined"


def hour_counts(intervals, origins):
    """観測時間を頭から 1 時間ずつに切り、ブロックごとの原点の数（最後の 1 時間未満は捨てる）。
    断片はすべて半開 [x, y)（境界の原点を 2 度数えない）。"""
    origins = sorted(origins)
    out, acc = [], 0
    edges, piece = [], []
    for a, b in sorted(intervals):
        t = a
        while t < b:
            step = min(H - acc, b - t)
            piece.append((t, t + step))
            acc += step
            t += step
            if acc == H:
                edges.append(piece)
                piece, acc = [], 0
    for pcs in edges:
        out.append(sum(bisect.bisect_left(origins, y) - bisect.bisect_left(origins, x) for x, y in pcs))
    return out


def anova_f(groups):
    """一元配置の F。群の中の平方和が 0 なら、群の間の平方和が正のとき ∞、0 のとき None。"""
    groups = [g for g in groups if len(g) >= 2]
    k = len(groups)
    N = sum(len(g) for g in groups)
    if k < 2 or N <= k:
        return None
    grand = sum(sum(g) for g in groups) / N
    ssb = sum(len(g) * (statistics.mean(g) - grand) ** 2 for g in groups)
    ssw = sum((x - statistics.mean(g)) ** 2 for g in groups for x in g)
    if ssw == 0:
        return math.inf if ssb > 0 else None
    return (ssb / (k - 1)) / (ssw / (N - k))


def h4a_perm(groups, seed):
    groups = [g for g in groups if len(g) >= 2]
    f_obs = anova_f(groups)
    if f_obs is None:
        return {"defined": False, "days": len(groups)}
    rng = random.Random(seed)
    pool = [x for g in groups for x in g]
    sizes = [len(g) for g in groups]
    ge = 0
    for _ in range(B):
        rng.shuffle(pool)
        gs, i = [], 0
        for s in sizes:
            gs.append(pool[i:i + s])
            i += s
        f = anova_f(gs)
        if f is not None and f >= f_obs:
            ge += 1
    return {"defined": True, "F": "inf" if f_obs == math.inf else f_obs, "p_perm": (1 + ge) / (B + 1), "days": len(groups), "blocks": sum(sizes)}


# ---------- U3 H5 ----------

def warm_end(flow, intervals):
    """θ の標本が 100 個そろう時刻（Acc.at と同じく、時刻が t 以下の標本を数える）。そろわなければ None。"""
    pool = sorted(cc.gap_pool(flow, intervals))
    return pool[cc.WARM - 1][0] if len(pool) >= cc.WARM else None


def _clip(intervals, lo, hi):
    return [(max(a, lo), min(b, hi)) for a, b in intervals if min(b, hi) > max(a, lo)]


def _cut(segs, frac):
    """観測時間で frac の位置の時刻。"""
    R = sum(b - a for a, b in segs)
    target = R * frac
    acc = 0
    for a, b in segs:
        if acc + (b - a) >= target:
            return a + (target - acc)
        acc += b - a
    return segs[-1][1]


def bouts_of_day(intervals, press, wend, origins):
    """まとまり = [開始, そのまとまりの最後の押下]（判断 7）。開始は types_core.blocks_from_press（30 分の途切れ）。
    戻り値: [{early, late, R_ms, thirds:[n,n,n], warm_excluded_ms}]（観測 60 分以上のまとまりだけ）。"""
    press = sorted(press)
    starts = tc.blocks_from_press(press)
    if wend is None or not starts:
        return []
    intervals = sorted(intervals)
    origins = sorted(origins)
    out = []
    for i, a in enumerate(starts):
        nxt = starts[i + 1] if i + 1 < len(starts) else math.inf
        last = press[bisect.bisect_left(press, nxt) - 1]
        obs = _clip(intervals, a, last)
        if sum(y - x for x, y in obs) < MIN_BOUT_OBS:
            continue
        rem = _clip(obs, max(a + tc.EARLY_MS, wend), last)
        R = sum(y - x for x, y in rem)
        if R <= 0:
            continue
        m = _cut(rem, 0.5)
        c1, c2 = _cut(rem, 1 / 3), _cut(rem, 2 / 3)
        early = late = 0
        th = [0, 0, 0]
        for x, y in rem:
            for t in origins[bisect.bisect_left(origins, x):bisect.bisect_left(origins, y)]:
                if t < m:
                    early += 1
                else:
                    late += 1
                th[0 if t < c1 else 1 if t < c2 else 2] += 1
        out.append({"early": early, "late": late, "R_ms": R, "thirds": th,
                    "warm_excluded_ms": sum(y - x for x, y in obs) - R})
    return out


def rr(bouts):
    E = sum(b["early"] for b in bouts)
    L = sum(b["late"] for b in bouts)
    if E == 0 or L == 0:
        E, L = E + 0.5, L + 0.5
    return L / E


def h5(bouts, n_days, seed):
    """n_days: H5 に入れた日（θ の温まりがそろった日）の数。"""
    E, L = sum(b["early"] for b in bouts), sum(b["late"] for b in bouts)
    res = {"days": n_days, "bouts": len(bouts), "early_n": E, "late_n": L,
           "half_obs_h": sum(b["R_ms"] for b in bouts) / 2 / H,
           "warm_excluded_h": sum(b["warm_excluded_ms"] for b in bouts) / H}
    R = sum(b["R_ms"] for b in bouts)
    res["thirds_per_h"] = [sum(b["thirds"][j] for b in bouts) / (R / 3 / H) for j in range(3)] if R else None
    if bouts:
        obs = rr(bouts)
        rng = random.Random(seed)
        logs = [math.log(rr([bouts[rng.randrange(len(bouts))] for _ in bouts])) for _ in range(B)]
        se = statistics.stdev(logs) if len(logs) > 1 else 0.0
        lo, hi = math.exp(math.log(obs) - 1.96 * se), math.exp(math.log(obs) + 1.96 * se)
        res.update({"RR": obs, "se_log": se, "ci95": [lo, hi]})
    if n_days < MIN_DAYS:
        res["verdict"] = "undetermined_days"
    elif len(bouts) < MIN_BOUTS:
        res["verdict"] = "undetermined_bouts"
    elif E + L < MIN_HALF_COUNT:
        res["verdict"] = "undetermined_counts"
    else:
        lo, hi = res["ci95"]
        # 判断 7: 下限 > 1 なら支持（上限 < 1.25 でも支持を優先し、差が小さいと添える）
        res["verdict"] = "support" if lo > 1 else "refute" if hi < RR_REFUTE else "undetermined"
        res["support_but_small"] = lo > 1 and hi < RR_REFUTE
    return res


# ---------- U4 ----------

READ_RULES = {"a_C0_is_C2": lambda x: 0.35 <= x <= 0.65, "b_C0_hit_C1": lambda x: 0.30 <= x <= 0.60,
              "c_C1_inside_C0_stall": lambda x: x >= 0.80, "d_C6_per_h": lambda x: x <= 0.1,
              "e_theta1_over_theta": lambda x: x <= 0.5,
              "f_sd_ratio": lambda x: all(r is not None and r >= SD_RATIO_MIN for r in x.values())}


def readings(cur, ref):
    def g(d, *ks):
        for k in ks:
            d = d[k]
        return d

    def vals(d):
        def ratio(k):
            s = g(d, "O1_counts_rates", k, "day_unit_sd")
            return s["sd_between_units"] / s["sd_expected_poisson_mean"] if s and s["sd_expected_poisson_mean"] else None
        th0 = g(d, "O2_thresholds", "C0", "threshold_at_fire")
        th1 = g(d, "O2_thresholds", "C1", "threshold_at_fire")
        return {"a_C0_is_C2": g(d, "O4_overlap", "C0_is_C2", "ratio"),
                "b_C0_hit_C1": g(d, "O4_overlap", "C0_hit_C1", "ratio"),
                "c_C1_inside_C0_stall": g(d, "O4_overlap", "posthoc_C1_inside_C0_stall_to_resume", "ratio"),
                "d_C6_per_h": g(d, "O1_counts_rates", "C6", "pooled_per_h"),
                "e_theta1_over_theta": th1["median"] / th0["median"] if th0 and th1 and th0["median"] else None,
                "f_sd_ratio": {k: ratio(k) for k in ("C0", "C1", "C2")}}
    cv, rv = vals(cur), vals(ref)
    out = {}
    for k, rule in READ_RULES.items():
        x = cv[k]
        missing = x is None or (isinstance(x, dict) and any(v is None for v in x.values()))
        out[k] = {"value": x, "value_14_days": rv[k], "repeated": None if missing else rule(x)}
    return out


# ---------- 実行 ----------

def run(work, seed_file, out, *files):
    seed = int(open(seed_file).read().strip())
    inters = []
    for f in files:
        d = json.load(open(os.path.join(work, os.path.basename(f)[:-len(".ndjson")] + ".json")))
        if d["input_sha256"] != cc.sha256(f):
            sys.exit("中間と入力の SHA-256 が合わない")
        inters.append(d)
    match = {"files": 0, "onsets_replay": 0, "onsets_port": 0, "mismatch_files": 0}
    for d in inters:  # U1 の自己検査（c1c2c6 K2 と同じ）を、除外の前の全ファイルに・計算より前に
        dy = cc.Day(d)
        port = [(x[0], x[1]) for x in dy.c0()[0]]
        match["files"] += 1
        match["onsets_replay"] += len(dy.replay_onsets)
        match["onsets_port"] += len(port)
        if port != dy.replay_onsets:
            match["mismatch_files"] += 1
    if match["mismatch_files"]:
        sys.exit("自己検査: 検出器の C0 が gse-replay の onsets と一致しない " + json.dumps(match))
    used, excl = select_days(inters)
    days = [cc.Day(d) for d in used]
    all_rows, no_warm = [], {"C0": 0, "C1": 0}
    for dy in days:
        rows, nw = cc.day_rows(dy)
        cc.check_structure(dy, rows)
        all_rows.append(rows)
        for k in nw:
            no_warm[k] += nw[k]
    res = {"files": {"given": len(files), "excluded": excl, "used": len(days)}, "selfcheck": match,
           "H4a": {}, "H5": {}}
    for k in ("C0", "C1", "C2"):
        flow_of = (lambda dy: dy.act) if k == "C1" else (lambda dy: dy.press)  # θ の流れ（C2 は C0 の部分集合）
        units, units_incl, groups, short = [], [], [], 0
        for dy, r in zip(days, all_rows):
            ori = [x["o"] for x in r[k]]
            pw = post_warm(dy.intervals, warm_end(flow_of(dy), dy.intervals))
            if sum(b - a for a, b in pw) < MIN_DAY_OBS:   # θ がそろわない日も含む（判断 8）
                short += 1
                continue
            units.append((sum(b - a for a, b in pw), sum(1 for t in ori if any(a <= t <= b for a, b in pw))))
            units_incl.append((dy.obs, len(ori)))   # 記述は判定と同じ日で
            groups.append(hour_counts(pw, ori))
        st = h4a_stats(units)
        st["verdict"] = h4a_verdict(st) if k == "C0" else "not_judged"
        st["perm"] = h4a_perm(groups, seed)
        st["including_warmup"] = h4a_stats(units_incl)   # 14 日と同じ式（記述・判断 7）
        st["excluded_post_warm_lt_4h"] = short
        res["H4a"][k] = st
        bouts, n5 = [], 0
        for dy, r in zip(days, all_rows):
            we = warm_end(flow_of(dy), dy.intervals)
            if sum(b - a for a, b in post_warm(dy.intervals, we)) < MIN_DAY_OBS:
                continue
            n5 += 1
            bouts += bouts_of_day(dy.intervals, dy.press, we, [x["o"] for x in r[k]])
        h = h5(bouts, n5, seed)
        if k != "C0":
            h["verdict"] = "not_judged"
        res["H5"][k] = h
    if days:
        cur = cc.summarize(days, all_rows, no_warm)
        res["U4_summary"] = cur
        res["U4_readings"] = readings(cur, json.load(open(FOURTEEN)))
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    print(json.dumps({"selfcheck": match, "H4a": res["H4a"]["C0"]["verdict"], "H5": res["H5"]["C0"]["verdict"]}),
          file=sys.stderr)
    return res


# ---------- U5 陽性対照 ----------

def _poisson(rng, mu):
    n, t = 0, rng.expovariate(1.0)
    while t < mu:
        n += 1
        t += rng.expovariate(1.0)
    return n


def _synth_day(rng, start, hours, rate_per_h):
    """合成の 1 日の中間（打鍵は 5 秒おきの文字の押下・ところどころ止まる）。onsets は検出器の C0 を入れる。"""
    keys, t, end = [], start, start + int(hours * H)
    while t < end:
        keys.append([t, "alphabetic"])
        t += 5_000 if rng.random() > rate_per_h * 5 / 3600 else 5_000 + rng.randrange(60_000, 400_000)
    d = cc.synth(keys, pointer=(), focus=[start + 1000], intervals=((start, end),))
    d["onsets"] = [[s, t0] for s, t0, _ in cc.Day(d).c0()[0]]
    return d


def selftest():
    import tempfile
    # 2 χ² の値
    for (p, k, want) in [(0.95, 1, 3.8415), (0.95, 4, 9.4877), (0.95, 10, 18.307), (0.025, 4, 0.4844), (0.025, 1, 0.000982)]:
        got = chi2_ppf(p, k)
        assert abs(got - want) / want < 2e-3, (p, k, got)
    assert abs(chi2_sf(3.8415, 1) - 0.05) < 1e-4 and abs(chi2_sf(18.307, 10) - 0.05) < 1e-4
    # 2 手で出した例: n = 2,6,4,4,4・各 1 時間 → λ = 4・X² = 2・φ = 0.5・p = P(χ²_4 ≥ 2)
    st = h4a_stats([(H, 2), (H, 6), (H, 4), (H, 4), (H, 4)])
    assert abs(st["X2"] - 2.0) < 1e-9 and abs(st["phi"] - 0.5) < 1e-9 and abs(st["p_one_sided"] - 0.735759) < 1e-5, st
    assert abs(st["phi_upper95"] - 2.0 / chi2_ppf(0.025, 4)) < 1e-9
    assert abs(st["sd_ratio"] - (statistics.stdev([2, 6, 4, 4, 4]) / 2.0)) < 1e-3, st
    # 2 p だけが効く例: SD の比 ≥ 1.5 だが p > 0.05（件数 9・23・11・21・16 を各 1 時間・X² = 9.25）
    st = h4a_stats([(H, n) for n in (9, 23, 11, 21, 16)])
    assert st["sd_ratio"] >= 1.5 and 0.05 < st["p_one_sided"] < 0.06, st
    assert h4a_verdict(st) == "undetermined"
    # 2 SD の比だけが効く例: p は小さいが SD の比 < 1.5（40 日・各 1 時間・100 ± 13）
    st = h4a_stats([(H, 100 + (13 if i % 2 else -13)) for i in range(40)])
    assert st["p_one_sided"] < 0.01 and st["sd_ratio"] < 1.5 and st["phi_upper95"] > 2.25, st
    assert h4a_verdict(st) == "undetermined"
    st = h4a_stats([(H, 2), (H, 6), (H, 4), (H, 4), (H, 4)])
    assert st["sd_ratio"] == statistics.stdev([2, 6, 4, 4, 4]) / 2.0   # 丸めない
    # 1 ポアソンなら支持はまれ・日ごとに 3 倍なら支持・日数 4 は決まらない
    rng = random.Random(1)
    sup = 0
    for _ in range(400):
        sup += h4a_verdict(h4a_stats([(11 * H, _poisson(rng, 9 * 11)) for _ in range(10)])) == "support"
    assert sup / 400 <= 0.08, sup
    od = [(11 * H, _poisson(rng, (4.5 if i % 2 else 13.5) * 11)) for i in range(10)]
    assert h4a_verdict(h4a_stats(od)) == "support"
    assert h4a_verdict(h4a_stats(od[:4])) == "undetermined_days"
    # 反証: ポアソンで 40 日なら φ の上限は多くの回で 2.25 を下回る・一定の件数なら必ず反証
    ref = sum(h4a_verdict(h4a_stats([(11 * H, _poisson(rng, 9 * 11)) for _ in range(40)])) == "refute"
              for _ in range(100))
    assert ref >= 80, ref
    assert h4a_verdict(h4a_stats([(11 * H, 99)] * 30)) == "refute"
    # 2 θ の温まりを除いた観測区間
    assert post_warm([(0, 10), (20, 40)], 25) == [(25, 40)] and post_warm([(0, 10)], None) == []
    assert post_warm([(0, 10), (20, 40)], 5) == [(5, 10), (20, 40)]
    # 5 副の並べ替え
    day_eff = [[2, 3, 2, 3, 2, 3]] * 4 + [[12, 13, 12, 13, 12, 13]] * 4
    assert h4a_perm(day_eff, 7)["p_perm"] == 1 / (B + 1)
    same = [[3, 9, 3, 9, 3, 9]] * 8
    assert h4a_perm(same, 7)["p_perm"] > 0.5
    # 同点と ∞: [[1, 2], [1, 2]] は F = 0 で、並べ替えは F = 0 か ∞（群の中が 0）だけ → p = 1
    assert h4a_perm([[1, 2], [1, 2]], 7)["p_perm"] == 1.0
    assert h4a_perm([[1, 1], [2, 2]], 7)["F"] == "inf"
    # ブロック 2 未満の日は副に入れない
    assert h4a_perm([[5], [1, 2], [3, 5]], 7)["days"] == 2
    # 1 時間のブロック: 区間をまたいで観測時間で切る・境界の原点は 1 度だけ
    iv = [(0, 40 * 60_000), (60 * 60_000, 150 * 60_000)]
    hc = hour_counts(iv, [10 * 60_000, 79 * 60_000, 81 * 60_000, 139 * 60_000, 145 * 60_000, 50 * 60_000])
    assert hc == [2, 2], hc
    assert hour_counts([(0, 2 * H)], [H]) == [0, 1]
    # 3 H5
    rng = random.Random(3)

    def mk_bouts(n_bouts, rate_e, rate_l, length_min=130):
        out = []
        for _ in range(n_bouts):
            press = list(range(0, length_min * 60_000 + 1, 10_000))
            ori = []
            mid = 10 * 60_000 + (length_min - 10) * 60_000 / 2
            for t in range(10 * 60_000, length_min * 60_000, 1000):
                r = rate_e if t < mid else rate_l
                if rng.random() < r / 3600:
                    ori.append(t)
            out += bouts_of_day([(0, length_min * 60_000 + 40 * 60_000)], press, 0, ori)
        return out
    b2 = mk_bouts(20, 10, 20)
    assert h5(b2, 6, 5)["verdict"] == "support", h5(b2, 6, 5)
    b1 = mk_bouts(40, 15, 15)
    assert h5(b1, 6, 5)["verdict"] == "refute", h5(b1, 6, 5)
    bf = mk_bouts(12, 3, 3)
    assert h5(bf, 6, 5)["verdict"] == "undetermined", h5(bf, 6, 5)
    assert h5(b2[:9], 6, 5)["verdict"] == "undetermined_bouts"
    assert h5(b2, 4, 5)["verdict"] == "undetermined_days"
    # 区間の幅は log RR ± 1.96·SE
    r = h5(b2, 6, 5)
    assert abs(r["ci95"][0] - math.exp(math.log(r["RR"]) - 1.96 * r["se_log"])) < 1e-9
    assert abs(r["ci95"][1] - math.exp(math.log(r["RR"]) + 1.96 * r["se_log"])) < 1e-9
    assert r["se_log"] > 0.05
    # 件数の下限・0 の補正・同時に立つときは支持
    edge = [{"early": 2, "late": 2, "R_ms": H, "thirds": [1, 1, 2], "warm_excluded_ms": 0} for _ in range(10)]
    assert h5(edge, 5, 5)["verdict"] not in ("undetermined_bouts", "undetermined_counts", "undetermined_days")  # 10 まとまり・40 件・5 日ちょうど
    assert h5(edge[:9], 5, 5)["verdict"] == "undetermined_bouts"
    few = [{"early": 1, "late": 2, "R_ms": H, "thirds": [1, 1, 1], "warm_excluded_ms": 0} for _ in range(12)]
    assert h5(few, 6, 5)["verdict"] == "undetermined_counts"
    zero = [{"early": 0, "late": 4, "R_ms": H, "thirds": [0, 2, 2], "warm_excluded_ms": 0} for _ in range(12)]
    assert h5(zero, 6, 5)["RR"] == 48.5 / 0.5
    tight = [{"early": 100, "late": 110, "R_ms": H, "thirds": [1, 1, 1], "warm_excluded_ms": 0} for _ in range(12)]
    rt = h5(tight, 6, 5)
    assert rt["verdict"] == "support" and rt["support_but_small"], rt
    # 4 温まり・頭の 10 分・切れ目をまたぐ m_b・まとまりの終わり（最後の押下）
    iv = [(0, 40 * 60_000), (60 * 60_000, 200 * 60_000)]
    press = list(range(0, 130 * 60_000 + 1, 10 * 60_000))   # 1 つのまとまり・最後の押下 130 分
    bt = bouts_of_day(iv, press, 0, [5 * 60_000, 79 * 60_000, 81 * 60_000, 150 * 60_000])
    assert len(bt) == 1 and bt[0]["early"] == 1 and bt[0]["late"] == 1 and bt[0]["R_ms"] == 100 * 60_000, bt
    bt = bouts_of_day(iv, press, 0, [80 * 60_000])           # m_b ちょうどは後半
    assert bt[0]["early"] == 0 and bt[0]["late"] == 1, bt
    bt = bouts_of_day(iv, press, 20 * 60_000, [15 * 60_000, 30 * 60_000])
    assert bt[0]["early"] == 1 and bt[0]["late"] == 0 and bt[0]["R_ms"] == 90 * 60_000, bt
    # 区切りの沈黙（最後の押下の後 40 分）と次のまとまり: 沈黙の中の原点は数えず、分母にも入らない
    press2 = list(range(0, 70 * 60_000 + 1, 10_000)) + list(range(110 * 60_000, 180 * 60_000 + 1, 10_000))
    bt = bouts_of_day([(0, 200 * 60_000)], press2, 0, [90 * 60_000])
    assert len(bt) == 2 and all(b["early"] + b["late"] == 0 for b in bt) and bt[0]["R_ms"] == 60 * 60_000, bt
    p59 = list(range(0, 59 * 60_000 + 1, 10_000))
    assert bouts_of_day([(0, 200 * 60_000)], p59, 0, [30 * 60_000]) == []                # 60 分未満は使わない
    assert len(bouts_of_day([(0, 200 * 60_000)], p59 + [60 * 60_000], 0, [30 * 60_000])) == 1  # 60 分ちょうどは使う
    assert bouts_of_day(iv, press, None, [30 * 60_000]) == []                           # θ がそろわない日
    assert warm_end(list(range(0, 200 * 1000, 1000)), [(0, 10 ** 9)]) == 100 * 1000
    assert warm_end(list(range(0, 50 * 1000, 1000)), [(0, 10 ** 9)]) is None
    # 6 U1 の除外
    mk = lambda focus, hours: {"focus": focus, "observed_intervals": [{"a_ms": 0, "b_ms": int(hours * H)}]}
    used, ex = select_days([mk([1], 5), mk([], 10), mk([1], 3.9), mk([1], 4)])
    assert len(used) == 2 and ex == {"no_focus": 1, "obs_lt_4h": 1}, ex
    # U4 の読みの幅
    for k, x, want in [("a_C0_is_C2", 0.65, True), ("a_C0_is_C2", 0.66, False), ("a_C0_is_C2", 0.34, False),
                       ("b_C0_hit_C1", 0.30, True), ("b_C0_hit_C1", 0.61, False), ("c_C1_inside_C0_stall", 0.80, True),
                       ("c_C1_inside_C0_stall", 0.79, False), ("d_C6_per_h", 0.1, True), ("d_C6_per_h", 0.11, False),
                       ("e_theta1_over_theta", 0.5, True), ("e_theta1_over_theta", 0.51, False)]:
        assert READ_RULES[k](x) is want, (k, x)
    assert READ_RULES["f_sd_ratio"]({"C0": 1.5, "C1": 2, "C2": 3}) and not READ_RULES["f_sd_ratio"]({"C0": 1.49, "C1": 2, "C2": 3})
    ref14 = json.load(open(FOURTEEN))
    rd = readings(ref14, ref14)   # 14 日をそのまま入れると a〜f はすべて繰り返す（14 日の読みの写し）
    assert all(v["repeated"] is True for v in rd.values()), rd
    import copy
    miss = copy.deepcopy(ref14)
    miss["O1_counts_rates"]["C1"]["day_unit_sd"] = None
    assert readings(miss, ref14)["f_sd_ratio"]["repeated"] is None
    assert abs(rd["a_C0_is_C2"]["value"] - 0.5093) < 1e-4
    # 通し（run の配線）: 合成の 6 日（うち 1 日はフォーカス 0）を中間の形で置いて回す
    with tempfile.TemporaryDirectory() as tmp:
        rng = random.Random(11)
        files = []
        for i in range(7):
            f = os.path.join(tmp, f"day{i}.ndjson")
            open(f, "w").write(str(i))
            d = _synth_day(rng, 0, 6, 9 if i % 2 else 3)
            if i == 5:
                d["focus"] = []
            if i == 6:   # 押下が 100 個に満たず θ がそろわない 5 時間の日（U1 は通り、H4a・H5 から外れる）
                d = cc.synth([[j * 120_000, "alphabetic"] for j in range(60)], focus=[1000], intervals=((0, 5 * H),))
                d["onsets"] = [[s, t0] for s, t0, _ in cc.Day(d).c0()[0]]
            d["input_sha256"] = cc.sha256(f)
            json.dump(d, open(os.path.join(tmp, f"day{i}.json"), "w"))
            files.append(f)
        seed = os.path.join(tmp, "SEED")
        open(seed, "w").write("5")
        res = run(tmp, seed, os.path.join(tmp, "out.json"), *files)
        assert res["files"] == {"given": 7, "excluded": {"no_focus": 1, "obs_lt_4h": 0}, "used": 6}, res["files"]
        assert res["selfcheck"]["mismatch_files"] == 0 and res["selfcheck"]["files"] == 7
        c0 = res["H4a"]["C0"]
        assert c0["days"] == 5 and c0["verdict"] in ("support", "refute", "undetermined")
        assert res["selfcheck"]["onsets_port"] > 100 and c0["pooled_per_h"] > 0, res["selfcheck"]
        assert c0["including_warmup"]["days"] == 5 and c0["excluded_post_warm_lt_4h"] == 1
        # 温まりを除いた観測時間は含めた観測時間より短く、件数は同じ（C0 は温まりの中で立たない）
        assert c0["including_warmup"]["pooled_per_h"] < c0["pooled_per_h"]
        assert res["H4a"]["C1"]["verdict"] == "not_judged" and res["H5"]["C2"]["verdict"] == "not_judged"
        assert res["H5"]["C0"]["bouts"] == 5 and res["H5"]["C0"]["verdict"] == "undetermined_bouts"
        assert res["H5"]["C0"]["days"] == 5 and set(res["U4_readings"]) == set(READ_RULES)
        # 打鍵だけの合成なので C1 の流れは押下と同じ・C2 は 0 件（止まりの間は何も動かない）
        assert res["U4_summary"]["O1_counts_rates"]["C2"]["n"] == 0
        # 止まる道: 自己検査の不一致・入力の SHA-256 の不一致
        p0 = os.path.join(tmp, "day0.json")
        orig = open(p0).read()
        d6 = json.loads(orig)
        d6["onsets"] = d6["onsets"][1:]
        json.dump(d6, open(p0, "w"))
        for broken, msg in (("onsets", "自己検査"), ("sha", "SHA-256")):
            if broken == "sha":
                open(p0, "w").write(orig)
                open(files[1], "w").write("changed")
            try:
                run(tmp, seed, os.path.join(tmp, "out2.json"), *files)
            except SystemExit as e:
                assert msg in str(e), (broken, e)
            else:
                raise AssertionError("止まらなかった: " + broken)
    print("selftest ok", file=sys.stderr)


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(*sys.argv[1:])
