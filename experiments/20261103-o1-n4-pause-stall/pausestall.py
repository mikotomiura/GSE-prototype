"""O1 の 4 人の休止の分布と停滞の率（conditions.md N2〜N6）。build_n4.py の中間だけを読み、記号を付けた集計値だけを出す。

usage: pausestall.py --selftest
       pausestall.py <work_dir> <seed> <out.json>
出力に P-ID・時刻・日付・ファイル名・版の文字列を書かない。版ごとの表は <work_dir>/versions.json（repo の外）。
"""
import json
import math
import os
import random
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../20261103-stall-candidates-c1c2c6"))
import candidates as cd  # noqa: E402  Day・day_rows・check_structure・summarize・gap_pool
from candidates import tc, ao  # noqa: E402

MIN_UNIT_MS = 4 * tc.H      # N2: SD に使う単位の観測時間の下限
MIN_UNITS = 5               # N2: SD を出す単位の数の下限
QS = (0.5, 0.75, 0.9, 0.95, 0.99, 0.999)
LONG_S = (2, 30, 180, 1800)
BIN = 0.02                  # N3: 階級の幅（log10 ms）
KMAX = 5
N_RANDOM_INIT = 9
SD_FLOOR = 0.02
TOL = 1e-9
MAX_IT = 2000


# ---------- N3 休止 ----------

def nearest_rank(xs_sorted, q):
    n = len(xs_sorted)
    return xs_sorted[min(max(math.ceil(q * n), 1), n) - 1]


def pause_stats(gaps):
    """gaps: ms の間隔の列。0 ms を外し、分位・割合・時間で重みを付けた割合を返す。"""
    zero = sum(1 for g in gaps if g <= 0)
    xs = sorted(g for g in gaps if g > 0)
    if not xs:
        return {"n": 0, "zero_ms_excluded": zero}
    tot = sum(xs)
    return {"n": len(xs), "zero_ms_excluded": zero,
            "quantiles_s": {str(q): round(nearest_rank(xs, q) / 1000, 4) for q in QS},
            "share_longer_than_s": {str(s): round(sum(1 for g in xs if g > s * 1000) / len(xs), 6) for s in LONG_S},
            "time_share_longer_than_s": {str(s): round(sum(g for g in xs if g > s * 1000) / tot, 6) for s in LONG_S},
            "total_pause_h": round(tot / tc.H, 3)}


def em_binned(x, c, mu, sd, w):
    n = c.sum()
    prev = -np.inf
    for it in range(MAX_IT):
        z = (x[:, None] - mu[None, :]) / sd[None, :]
        dens = w[None, :] * np.exp(-0.5 * z * z) / (sd[None, :] * math.sqrt(2 * math.pi))
        tot = dens.sum(axis=1)
        tot = np.maximum(tot, 1e-300)
        ll = float((c * np.log(tot)).sum())
        if ll - prev < TOL * n:
            return ll, mu, sd, w, it
        prev = ll
        r = dens / tot[:, None] * c[:, None]
        nk = np.maximum(r.sum(axis=0), 1e-12)
        w = nk / n
        mu = (r * x[:, None]).sum(axis=0) / nk
        sd = np.sqrt((r * (x[:, None] - mu[None, :]) ** 2).sum(axis=0) / nk)
        sd = np.maximum(sd, SD_FLOOR)
    z = (x[:, None] - mu[None, :]) / sd[None, :]
    tot = np.maximum((w[None, :] * np.exp(-0.5 * z * z) / (sd[None, :] * math.sqrt(2 * math.pi))).sum(axis=1), 1e-300)
    return float((c * np.log(tot)).sum()), mu, sd, w, MAX_IT


def binned(gaps):
    v = np.log10(np.asarray([g for g in gaps if g > 0], dtype=float))
    lo = math.floor(v.min() / BIN) * BIN
    hi = math.ceil(v.max() / BIN) * BIN
    nb = max(int(round((hi - lo) / BIN)), 1)
    c, edges = np.histogram(v, bins=nb, range=(lo, lo + nb * BIN))
    x = (edges[:-1] + edges[1:]) / 2
    keep = c > 0
    return v, x[keep], c[keep].astype(float)


def mixture(gaps, seed, kmax=KMAX):
    v, x, c = binned(gaps)
    n = len(v)
    rng = random.Random(seed)
    fits = []
    for k in range(1, kmax + 1):
        inits = [(np.array([float(np.quantile(v, (j - 0.5) / k)) for j in range(1, k + 1)]),
                  np.full(k, max(float(v.std()) / k, SD_FLOOR)), np.full(k, 1.0 / k))]
        for _ in range(N_RANDOM_INIT):
            idx = list(range(len(x)))
            pick = []
            wts = list(c)
            for _ in range(min(k, len(idx))):
                j = rng.choices(range(len(idx)), weights=wts)[0]
                pick.append(x[idx[j]])
                del idx[j], wts[j]
            while len(pick) < k:
                pick.append(float(v.mean()))
            inits.append((np.array(sorted(pick)), np.full(k, max(float(v.std()) / k, SD_FLOOR)), np.full(k, 1.0 / k)))
        best = None
        for mu, sd, w in inits:
            ll, m2, s2, w2, it = em_binned(x, c, mu.copy(), sd.copy(), w.copy())
            if best is None or ll > best[0]:
                best = (ll, m2, s2, w2, it)
        ll, mu, sd, w, it = best
        o = np.argsort(mu)
        pen = (3 * k - 1) * math.log(n)
        fits.append({"k": k, "loglik": round(ll, 3), "bic": round(-2 * ll + pen, 3), "iterations": it,
                     "components": [{"geo_mean_s": round(10 ** float(mu[i]) / 1000, 4), "sd_decades": round(float(sd[i]), 4),
                                     "weight": round(float(w[i]), 5), "mu_log10_ms": round(float(mu[i]), 4)} for i in o]})
    kbest = min(fits, key=lambda f: f["bic"])["k"]
    return {"n": n, "bin_decades": BIN, "bic_k": kbest, "hit_kmax": kbest == kmax, "fits": fits}


# ---------- N2・N4 単位と率 ----------

def unit_sd_4h(units):
    """units: [(obs_ms, n)]。4 時間以上の単位で unit_sd と比。5 単位未満なら単位不足。"""
    u = [x for x in units if x[0] >= MIN_UNIT_MS]
    if len(u) < MIN_UNITS:
        return {"status": "単位不足", "units_ge_4h": len(u)}
    r = ao.unit_sd(u)
    r["status"] = "ok"
    r["sd_ratio"] = round(r["sd_between_units"] / r["sd_expected_poisson_mean"], 4) if r["sd_expected_poisson_mean"] else None
    return r


def by_date(units, dates):
    g = {}
    for (ob, n), d in zip(units, dates):
        a = g.setdefault(d, [0, 0])
        a[0] += ob
        a[1] += n
    return [tuple(v) for _, v in sorted(g.items())]


class Person:
    def __init__(self, files):
        self.all, self.focus, self.dates_all, self.dates_focus = [], [], [], []
        self.zero_obs = self.no_focus = self.zero_obs_onsets = 0
        self.versions = {}
        for f in files:
            try:
                d = json.load(open(f["inter"]))
            except (OSError, ValueError):
                sys.exit("中間が読めない（パスは出さない）")
            if d["input_sha256"] != f["plain_sha256"]:
                sys.exit("中間と平文の SHA-256 が合わない")
            dy = cd.Day(d)
            if dy.obs <= 0:
                self.zero_obs += 1
                self.zero_obs_onsets += len(dy.replay_onsets)
                continue
            v = (str(f.get("app_version")), str(f.get("hmm_version")))
            self.versions[v] = self.versions.get(v, 0) + 1
            self.all.append(dy)
            self.dates_all.append(f["date"])
            if d["focus"]:
                self.focus.append(dy)
                self.dates_focus.append(f["date"])
            else:
                self.no_focus += 1


def selfcheck(people):
    """N5: 検出器の C0 と gse-replay の onsets の一致（観測 0 の本は onsets が空であること）。"""
    m = {"files": 0, "onsets_replay": 0, "mismatch_files": 0, "zero_obs_files_with_onsets": 0}
    for p in people.values():
        m["zero_obs_files_with_onsets"] += 1 if p.zero_obs_onsets else 0
        for dy in p.all:
            port = [(x[0], x[1]) for x in dy.c0()[0]]
            m["files"] += 1
            m["onsets_replay"] += len(dy.replay_onsets)
            if port != dy.replay_onsets:
                m["mismatch_files"] += 1
    if m["mismatch_files"] or m["zero_obs_files_with_onsets"]:
        sys.exit("N5 の自己検査: 検出器の C0 が gse-replay の onsets と一致しない " + json.dumps(m))
    return m


def person_result(p, seed):
    gp = [g for dy in p.all for _, g in cd.gap_pool(dy.press, dy.intervals)]
    ga = [g for dy in p.focus for _, g in cd.gap_pool(dy.act, dy.intervals)]
    res = {"files": {"used_all": len(p.all), "used_focus": len(p.focus), "excluded_zero_obs": p.zero_obs,
                     "no_focus_rows": p.no_focus, "app_version_kinds": len({a for a, _ in p.versions})},
           "obs_h_all": round(sum(d.obs for d in p.all) / tc.H, 3),
           "N3_pause": {"P_press": {"stats": pause_stats(gp), "mixture": mixture(gp, seed) if gp else None},
                        "A_activity": {"stats": pause_stats(ga), "mixture": mixture(ga, seed) if ga else None}}}
    # C0 だけ（フォーカスの行が 0 のファイルを含む）
    c0u = [(dy.obs, len(dy.c0()[0])) for dy in p.all]
    n0 = sum(n for _, n in c0u)
    res["N4_C0_all_files"] = {"n": n0, "pooled_per_h": round(n0 / (sum(o for o, _ in c0u) / tc.H), 4),
                              "unit_sd_file": unit_sd_4h(c0u), "unit_sd_date": unit_sd_4h(by_date(c0u, p.dates_all))}
    if p.focus:
        rows, nw = [], {"C0": 0, "C1": 0}
        for dy in p.focus:
            r, w = cd.day_rows(dy)
            cd.check_structure(dy, r)
            rows.append(r)
            for k in w:
                nw[k] += w[k]
        s = cd.summarize(p.focus, rows, nw)
        # c1c2c6 の day_unit_sd は 4 時間の下限をかけていない。N2 の SD と取り違えないよう名前を替える
        for k in s["O1_counts_rates"]:
            s["O1_counts_rates"][k]["day_unit_sd_no_4h_floor_not_N2"] = s["O1_counts_rates"][k].pop("day_unit_sd")
        sd = {}
        for k in ("C0", "C1", "C2"):
            u = [(dy.obs, len(r[k])) for dy, r in zip(p.focus, rows)]
            sd[k] = {"file": unit_sd_4h(u), "date": unit_sd_4h(by_date(u, p.dates_focus))}
        s["N4_unit_sd_ge_4h"] = sd
        res["N4_focus_files"] = s
    return res


def _sd(d, key):
    """unit_sd_4h の結果から値を取る。単位不足なら None（無くて当然の欠け）。"""
    return None if d["status"] == "単位不足" else d[key]


def between(per):
    """人の間の幅（N3・N4）。per: {記号: 人の結果}。無くて当然の欠けだけを None にし、キーの誤りは止める。"""
    def take(f, needs_focus=False):
        out = {}
        for k, r in sorted(per.items()):
            out[k] = None if needs_focus and "N4_focus_files" not in r else f(r)
        vs = [v for v in out.values() if v is not None]
        return {"by_person": out, "min": min(vs) if vs else None, "max": max(vs) if vs else None,
                "max_over_min": round(max(vs) / min(vs), 4) if len(vs) > 1 and min(vs) > 0 else None}

    def st(r, s):
        x = r["N3_pause"][s]["stats"]
        return None if x["n"] == 0 else x

    def mx(r, s):
        return r["N3_pause"][s]["mixture"]
    b = {}
    for s in ("P_press", "A_activity"):
        for q in QS:
            b[f"{s}_q{q}_s"] = take(lambda r, s=s, q=q: None if st(r, s) is None else st(r, s)["quantiles_s"][str(q)])
        for L in LONG_S:
            b[f"{s}_share_gt_{L}s"] = take(lambda r, s=s, L=L: None if st(r, s) is None else st(r, s)["share_longer_than_s"][str(L)])
            b[f"{s}_time_share_gt_{L}s"] = take(
                lambda r, s=s, L=L: None if st(r, s) is None else st(r, s)["time_share_longer_than_s"][str(L)])
        b[f"{s}_bic_k"] = take(lambda r, s=s: None if mx(r, s) is None else mx(r, s)["bic_k"])
    for k in ("C0", "C1", "C2"):
        b[f"{k}_pooled_per_h"] = take(lambda r, k=k: r["N4_focus_files"]["O1_counts_rates"][k]["pooled_per_h"], True)
        b[f"{k}_sd_ratio_file"] = take(lambda r, k=k: _sd(r["N4_focus_files"]["N4_unit_sd_ge_4h"][k]["file"], "sd_ratio"), True)
        b[f"{k}_sd_ratio_date"] = take(lambda r, k=k: _sd(r["N4_focus_files"]["N4_unit_sd_ge_4h"][k]["date"], "sd_ratio"), True)
        b[f"{k}_sd_between_units_file"] = take(
            lambda r, k=k: _sd(r["N4_focus_files"]["N4_unit_sd_ge_4h"][k]["file"], "sd_between_units"), True)
        b[f"{k}_share_long_or_censored"] = take(
            lambda r, k=k: None if r["N4_focus_files"]["O3_lengths"][k]["long"]["ratio"] is None else
            round(r["N4_focus_files"]["O3_lengths"][k]["long"]["ratio"] + r["N4_focus_files"]["O3_lengths"][k]["censored"]["ratio"], 4), True)
    for k in ("C0", "C1"):
        b[f"{k}_theta_median_s"] = take(
            lambda r, k=k: None if r["N4_focus_files"]["O2_thresholds"][k]["threshold_at_fire"] is None else
            r["N4_focus_files"]["O2_thresholds"][k]["threshold_at_fire"]["median"] / 1000, True)
    b["C0_is_C2_share"] = take(lambda r: r["N4_focus_files"]["O4_overlap"]["C0_is_C2"]["ratio"], True)
    b["C0_all_files_pooled_per_h"] = take(lambda r: r["N4_C0_all_files"]["pooled_per_h"])
    b["C0_all_files_sd_ratio_file"] = take(lambda r: _sd(r["N4_C0_all_files"]["unit_sd_file"], "sd_ratio"))
    # 人の間の率の SD と、人の中の単位の率の SD の平均（N4）
    for k in ("C0", "C1", "C2"):
        rates = [v for v in b[f"{k}_pooled_per_h"]["by_person"].values() if v is not None]
        within = [v for v in b[f"{k}_sd_between_units_file"]["by_person"].values() if v is not None]
        b[f"{k}_sd_between_people_vs_within"] = {
            "sd_between_people": round(statistics.stdev(rates), 4) if len(rates) > 1 else None,
            "mean_sd_within_person": round(statistics.mean(within), 4) if within else None,
            "people": len(rates), "people_with_within_sd": len(within)}
    return b


# ---------- 公開用の丸め（判断 7） ----------

# 件数・本数を表すキー（丸める）。ここに無い整数（θ の ms・K・反復の回数など）は丸めない。
COUNT_KEYS = {"n", "num", "den", "days", "files", "units", "units_ge_4h", "used_all", "used_focus",
              "excluded_zero_obs", "no_focus_rows", "no_position", "odd_names_excluded", "held_out_files",
              "onsets_replay", "zero_ms_excluded", "rises_without_threshold_warmup", "C0_neither_C2_nor_hit_C1",
              "posthoc_C1_inside_C0_stalls_with_ge3_C1", "posthoc_C1_not_hit_C0_but_inside_C0_stall",
              "input_files", "zero_obs_files", "presses_in_zero_obs_files", "feat_rows_in_zero_obs_files",
              "pointer_rows", "focus_rows", "presses"}
HOUR_KEYS = {"obs_h", "obs_h_all", "total_pause_h"}
MIN_DEN = 20   # 分母がこれ未満の割合は伏せる（丸めた分子と分母から件数が戻るため）


def round_count(v):
    """件数・本数: 50 未満は 5 単位、50 以上は 100 単位。"""
    return int(5 * round(v / 5)) if v < 50 else int(100 * round(v / 100))


def public(x, key=None, parent=None):
    """repo に入れる版（判断 7）。観測時間（10 時間単位）・単位の観測時間の四分位（1 時間単位）・件数と本数（COUNT_KEYS）を
    丸め、分母が MIN_DEN 未満の割合を伏せ、単位不足の単位の数を伏せ、対数尤度と BIC の絶対値を最小との差に替える。
    率・割合・分位・SD・比・θ はそのまま。"""
    if isinstance(x, dict):
        if "fits" in x and "bic_k" in x:
            best = min(f["bic"] for f in x["fits"])
            x = {**x, "fits": [{kk: vv for kk, vv in f.items() if kk not in ("loglik", "bic")} |
                               {"delta_bic": round(f["bic"] - best, 1)} for f in x["fits"]]}
        if set(x) >= {"num", "den", "ratio"} and isinstance(x["den"], int) and x["den"] < MIN_DEN:
            x = {**x, "num": None, "ratio": None}
        if x.get("status") == "単位不足":
            x = {k: (None if k in ("units", "units_ge_4h") else v) for k, v in x.items()}
        return {k: public(v, k, key) for k, v in x.items()}
    if isinstance(x, list):
        return [public(v, key, parent) for v in x]
    if isinstance(x, bool) or x is None:
        return x
    if parent == "unit_obs_h" and isinstance(x, (int, float)) and key != "n":
        return round(x)
    if key in HOUR_KEYS and isinstance(x, (int, float)):
        return int(10 * round(x / 10))
    if isinstance(x, int) and key in COUNT_KEYS:
        return round_count(x)
    return x


def leaks(text, pids, versions):
    """出力の全文に P-ID・日付や時刻の形・版の文字列が無いか。見つかったものの種類を返す。"""
    import re
    found = []
    if any(pid in text for pid in pids):
        found.append("P-ID")
    if re.search(r"\d{8}_\d{6}", text) or re.search(r"(?<!\d)20[0-9]{2}(0[1-9]|1[0-2])([0-2][0-9]|3[01])(?!\d)", text):
        found.append("日付・時刻の形")
    if any(v and v != "None" and v in text for v in versions):
        found.append("版の文字列")
    return found


def run(work, seed, out):
    seed = int(seed)
    table = json.load(open(os.path.join(work, "files.json")))
    people = {v["symbol"]: Person(v["files"]) for v in table["people"].values()}
    m = selfcheck(people)
    per = {k: person_result(p, seed) for k, p in sorted(people.items())}
    res = {"selfcheck_N5": m, "odd_names_excluded": table["odd_names"], "held_out_files": table["held_out"],
           "people": per, "between_people": between(per)}
    for k, r in per.items():  # フォーカスの本がある人で主な値が欠けたら止める（M3）
        if "N4_focus_files" in r and res["between_people"]["C0_pooled_per_h"]["by_person"][k] is None:
            sys.exit("フォーカスの本がある人で主な値が欠けた")
    json.dump(res, open(os.path.join(work, "full.json"), "w"), indent=1, ensure_ascii=False)
    text = json.dumps(public(res), indent=1, ensure_ascii=False)
    vers = {s for p in people.values() for v in p.versions for s in v}
    lk = leaks(text, table["people"], vers)
    if lk:
        sys.exit("公開用の出力に漏れ: " + "・".join(lk))
    open(out, "w").write(text)
    json.dump({k: {f"{a} / {h}": n for (a, h), n in p.versions.items()} for k, p in people.items()},
              open(os.path.join(work, "versions.json"), "w"), indent=1)
    print(json.dumps(m), file=sys.stderr)


# ---------- N6 陽性対照 ----------

def synth_inter(focus, obs_h, seed, date_gap=False):
    """合成の中間 1 本。2 秒前後の打鍵に、ときどき 60〜300 秒の休止。ポインタは休止の半分で動く。"""
    rng = random.Random(seed)
    b = int(obs_h * tc.H)
    keys, ptr, t = [], [], 0
    while t < b:
        if rng.random() < 0.01:
            gap = rng.randint(60_000, 300_000)
            if rng.random() < 0.5:
                ptr += [[u, 1, 0, 0] for u in range(t + 1000, min(t + gap, b), 5000)]
            t += gap
        else:
            t += rng.randint(300, 3000)
        if t < b:
            keys.append([t, "alphabetic" if rng.random() < 0.9 else "backspace"])
    d = {"observed_intervals": [{"a_ms": 0, "b_ms": b}] if b else [], "keys": keys, "pointer": ptr,
         "focus": [5000] if focus else [], "onsets": [], "input_sha256": "x"}
    if b:
        d["onsets"] = [[s, t0] for s, t0, _ in cd.Day(d).c0()[0]]
    return d


def selftest():
    rng = np.random.default_rng(20261103)
    # 2. 混合
    a = np.concatenate([rng.normal(2.3, 0.2, 80_000), rng.normal(4.0, 0.4, 20_000)])
    f2 = mixture(list(10 ** a), 1)
    assert f2["bic_k"] == 2, f2["bic_k"]
    comp = f2["fits"][1]["components"]
    assert abs(comp[0]["mu_log10_ms"] - 2.3) < 0.05 and abs(comp[1]["mu_log10_ms"] - 4.0) < 0.05, comp
    assert abs(comp[0]["weight"] - 0.8) < 0.02, comp
    assert mixture(list(10 ** rng.normal(2.5, 0.3, 100_000)), 1)["bic_k"] == 1
    # 3. モデルに依らない量
    st = pause_stats([0, 1000, 2000, 3000, 100_000])
    assert st["zero_ms_excluded"] == 1 and st["n"] == 4, st
    assert st["quantiles_s"]["0.5"] == 2.0 and st["quantiles_s"]["0.99"] == 100.0, st
    assert st["share_longer_than_s"]["2"] == 0.5 and st["share_longer_than_s"]["30"] == 0.25, st
    assert abs(st["time_share_longer_than_s"]["30"] - 100 / 106) < 1e-5, st
    v, x, c = binned([10 ** 2] * 99 + [10 ** 4])
    ll, mu, sd, w, _ = em_binned(x, c, np.array([3.0]), np.array([1.0]), np.array([1.0]))
    assert abs(mu[0] - (2 * 99 + 4) / 100) < 0.02, mu
    # 4. 単位の除外（Person の振り分け）
    import tempfile
    sys.path.insert(0, HERE)
    import build_n4
    tmp = tempfile.mkdtemp()
    files = []
    for i, (fo, oh) in enumerate([(False, 5), (True, 5), (True, 1), (True, 0)]):
        fp = os.path.join(tmp, f"u{i}.json")
        json.dump(synth_inter(fo, oh, i), open(fp, "w"))
        files.append({"inter": fp, "plain_sha256": "x", "date": str(i), "app_version": "v", "hmm_version": "h"})
    p = Person(files)
    assert len(p.all) == 3 and len(p.focus) == 2 and p.no_focus == 1 and p.zero_obs == 1, \
        (len(p.all), len(p.focus), p.no_focus, p.zero_obs)
    u = [(dy.obs, 1) for dy in p.all] + [(5 * tc.H, 2)] * 3
    r = unit_sd_4h(u)
    assert r["status"] == "ok" and r["units"] == 5, r
    assert unit_sd_4h(u[:4])["status"] == "単位不足"
    # 日付の単位は同じ日付の本を足す
    assert by_date([(1, 2), (3, 4), (5, 6)], ["a", "a", "b"]) == [(4, 6), (5, 6)]
    # 4b. run() を合成の 4 人で最後まで通す
    work = os.path.join(tmp, "work")
    os.makedirs(work)
    table = {"odd_names": 0, "held_out": 0, "people": {}}
    sym = build_n4.symbols(build_n4.PIDS, 7)
    for j, pid in enumerate(build_n4.PIDS):
        rows = []
        for i in range(9):
            fo = i != 0
            fp = os.path.join(work, f"{pid}_{i}.json")
            json.dump(synth_inter(fo, 6, 100 * j + i), open(fp, "w"))
            rows.append({"inter": fp, "plain_sha256": "x", "date": str(i // 2), "app_version": "9.9.9-test", "hmm_version": "8.8.8-test"})
        table["people"][pid] = {"symbol": sym[pid], "files": rows}
    json.dump(table, open(os.path.join(work, "files.json"), "w"))
    outp = os.path.join(tmp, "out.json")
    run(work, 1, outp)
    full = json.load(open(os.path.join(work, "full.json")))
    pubtext = open(outp).read()
    assert not leaks(pubtext, build_n4.PIDS, {"9.9.9-test", "8.8.8-test"}), leaks(pubtext, build_n4.PIDS, {"9.9.9-test", "8.8.8-test"})
    for k in "ABCD":
        r = full["people"][k]
        assert r["files"]["used_all"] == 9 and r["files"]["used_focus"] == 8, r["files"]
        exp_a = sum(len(cd.gap_pool(cd.Day(json.load(open(f["inter"]))).act, [(0, 6 * tc.H)]))
                    for f in next(v for v in table["people"].values() if v["symbol"] == k)["files"][1:])
        n_zero = r["N3_pause"]["A_activity"]["stats"]["zero_ms_excluded"]
        assert r["N3_pause"]["A_activity"]["stats"]["n"] + n_zero == exp_a, (r["N3_pause"]["A_activity"]["stats"]["n"], exp_a)
        # フォーカスの本 8 本の日付は 0,1,1,2,2,3,3,4 → 日付の単位は 5（2 本の日は 12 時間）
        dd = r["N4_focus_files"]["N4_unit_sd_ge_4h"]["C0"]["date"]
        assert dd["units"] == 5 and dd["unit_obs_h"]["q3"] == 12.0, dd
        assert r["N4_focus_files"]["N4_unit_sd_ge_4h"]["C0"]["file"]["units"] == 8
    for key in ("C0_pooled_per_h", "C1_pooled_per_h", "C0_sd_ratio_file", "P_press_q0.5_s", "A_activity_q0.99_s"):
        assert all(v is not None for v in full["between_people"][key]["by_person"].values()), key
    pub = json.loads(pubtext)
    assert pub["people"]["A"]["files"]["used_all"] == 10 and pub["people"]["A"]["obs_h_all"] % 10 == 0, pub["people"]["A"]["files"]
    assert all("loglik" not in f and "delta_bic" in f for f in pub["people"]["A"]["N3_pause"]["P_press"]["mixture"]["fits"])
    # 5. 記号と漏れの走査
    s1, s2 = build_n4.symbols(build_n4.PIDS, 7), build_n4.symbols(build_n4.PIDS, 7)
    assert s1 == s2 and sorted(s1.values()) == list("ABCD")
    # 塩は repo の外に 1 度だけ作られ、権限は 600・2 回目は同じ値
    sw = os.path.join(tmp, "saltwork")
    os.makedirs(sw)
    a1, a2 = build_n4.salt(sw), build_n4.salt(sw)
    assert a1 == a2 and len(a1) == 64 and (os.stat(os.path.join(sw, "symbol_salt")).st_mode & 0o777) == 0o600
    assert leaks('{"x": "P011"}', build_n4.PIDS, set()) == ["P-ID"]
    assert leaks('{"x": "a_20261009_051916"}', build_n4.PIDS, set()) == ["日付・時刻の形"]
    assert leaks('{"x": 1.20261009}', build_n4.PIDS, set()) == ["日付・時刻の形"]
    assert leaks('{"v": "0.1.40"}', build_n4.PIDS, {"0.1.40"}) == ["版の文字列"]
    assert not leaks('{"A": 1}', build_n4.PIDS, {"0.1.40"})
    assert round_count(17) == 15 and round_count(1459) == 1500
    pu = public({"threshold_at_fire": {"n": 1459, "median": 40700}, "x": {"num": 3, "den": 5, "ratio": 0.6},
                 "u": {"status": "単位不足", "units_ge_4h": 3}, "k": 4})
    assert pu["threshold_at_fire"] == {"n": 1500, "median": 40700}, pu
    assert pu["x"]["ratio"] is None and pu["x"]["num"] is None and pu["u"]["units_ge_4h"] is None and pu["k"] == 4, pu
    # 6. 選ぶ規則: 取り置きは本人だけ・形の合わない名前と直下のファイルを数える
    rec = os.path.join(tmp, "recv")
    for pid, names in {"P009": ["P009_o1day01_gse_o1_20261101_083029.age", "P009_o1day02_gse_o1_20261101_083030.age"],
                       "P006": ["P006_o1day01_gse_o1_20261101_083030.age", "P006_o1day02_gse_o1_20261101_083030_dup-1.age",
                                "P011_o1day03_gse_o1_20261001_000000.age"]}.items():
        os.makedirs(os.path.join(rec, pid))
        for n in names:
            open(os.path.join(rec, pid, n), "w").close()
    open(os.path.join(rec, "stray.age"), "w").close()
    use, odd, held = build_n4.select(rec)
    assert [x[0] for x in use["P009"]] == ["P009_o1day01_gse_o1_20261101_083029"], use
    assert [x[0] for x in use["P006"]] == ["P006_o1day01_gse_o1_20261101_083030"], use
    assert held == 1 and odd == 3, (held, odd)
    print("selftest ok", file=sys.stderr)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selftest"]:
        selftest()
    else:
        run(*sys.argv[1:])
