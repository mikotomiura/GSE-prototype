"""O1 の停滞の型と主要アウトカムの候補（conditions.md C1〜C6）。記述だけ・検定なし。

usage:
  analyze_o1.py <work_dir> <seed> <out_dir> <ndjson>...   （ndjson は C1 で選んだファイル。中間と SHA-256 を照合する）
  analyze_o1.py --selftest
出力は集計値だけ（時刻・ファイル名・日付を出さない）: <out_dir>/o1.json。停滞の台帳は <work_dir>/ledger.json（repo の外）。
"""
import bisect
import hashlib
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "../../20261101-klicke-early-stall-trigger/scripts"))
import types_core as tc  # noqa: E402
import analyze_item2 as t2  # noqa: E402  TEXT・DELETE の集合

HORIZONS = {"5min": 5 * 60_000, "10min": 10 * 60_000}
AWAY = 180_000
PASTE_FOCUS_WIN = 30_000
MIN_BLOCK_OBS = 30 * 60_000
B = 2000
T3_TO = "20261030"
PROBE_WORDS = ("probe", "self", "esm", "report", "label", "marker", "activity")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def count_in(ts, a, b, lo_open=False, hi_open=False):
    return tc.count_in(ts, a, b, lo_open, hi_open)


# ---------- Aalen–Johansen（metrics.rs の cif_receipt と is_degenerate の写し） ----------

def is_degenerate(o):
    return o["elapsed_ms"] == 0 and o["kind"] != "receipt"


def cif_receipt(outcomes, horizon):
    if not outcomes:
        return None
    times = sorted({o["elapsed_ms"] for o in outcomes if o["kind"] != "censored"})
    n_at = sum(1 for o in outcomes if o["elapsed_ms"] >= horizon)
    if not any(t <= horizon for t in times) and n_at == 0:
        return None
    surv, cif = 1.0, 0.0
    for t in times:
        if t > horizon:
            break
        n = sum(1 for o in outcomes if o["elapsed_ms"] >= t)
        d1 = sum(1 for o in outcomes if o["elapsed_ms"] == t and o["kind"] == "receipt")
        d2 = sum(1 for o in outcomes if o["elapsed_ms"] == t and o["kind"] == "next_away_candidate")
        cif += surv * (d1 / n)
        surv *= 1.0 - (d1 + d2) / n
    return cif


def receipt_free(outcomes, horizon):
    tracked = [o for o in outcomes if not is_degenerate(o)]
    c = cif_receipt(tracked, horizon)
    return None if c is None else 1.0 - c


# ---------- 1 日（1 ファイル） ----------

class Day:
    def __init__(self, d):
        self.d = d
        ks = d["keys"]
        text = [t for t, c in ks if c in t2.TEXT]
        dele = [t for t, c in ks if c in t2.DELETE]
        other = [t for t, c in ks if c not in t2.TEXT and c not in t2.DELETE]
        clicks = [p[0] for p in d["pointer"] if p[2] > 0 or p[3] > 0]
        moves = [p[0] for p in d["pointer"] if p[1] > 0]
        self.intervals = [(iv["a_ms"], iv["b_ms"]) for iv in d["observed_intervals"]]
        self.rec = tc.Rec(text, dele, other, self.intervals, clicks=clicks, focus=d["focus"], moves=moves)
        self.paste = sorted(p[0] for p in d["paste"])
        self.paste_chars = [p[1] for p in d["paste"]]
        self.press = self.rec.press
        self.obs = sum(b - a for a, b in self.intervals)

    def rows(self):
        out = []
        for s, t0 in self.d["onsets"]:
            r = self.rec.stall(s, t0)
            if r.get("no_interval"):
                out.append(r)
                continue
            iv = r["interval"]
            r["pre_paste"] = count_in(self.paste, s - tc.PRE_WIN, t0) > 0
            r["s_to_resume_ms"] = r["resume"] - s if r["resume"] is not None else None
            if r["resume"] is not None and not r["pre_paste"]:
                r["c1b"] = count_in(self.paste, t0, r["resume"], lo_open=True) == 0
            else:
                r["c1b"] = None
            for k, hz in HORIZONS.items():
                if r["pre_paste"]:
                    r["c1c_" + k] = None
                    r["c1c_" + k + "_excl"] = "pre_paste"
                elif t0 + hz > iv[1]:
                    r["c1c_" + k] = None
                    r["c1c_" + k + "_excl"] = "horizon_outside_interval"
                else:
                    r["c1c_" + k] = count_in(self.paste, t0, t0 + hz, lo_open=True) > 0
                    r["c1c_" + k + "_excl"] = None
            out.append(r)
        return out

    def blocks(self):
        """[(obs_ms, n_stalls)]（押下で区切った作業のまとまり・C3 の 2）"""
        st = self.rec.block_starts
        press = self.press
        res = []
        for i, a in enumerate(st):
            nxt = st[i + 1] if i + 1 < len(st) else None
            j = bisect.bisect_left(press, nxt) if nxt is not None else len(press)
            b = press[j - 1]
            ob = sum(max(0, min(b, y) - max(a, x)) for x, y in self.intervals)
            res.append([ob, 0])
        return res

    def gaps(self):
        inside, crossing = [], []
        for a, b in zip(self.press, self.press[1:]):
            if b - a < AWAY:
                continue
            ia, ib = self.rec.interval_of(a), self.rec.interval_of(b)
            (inside if ia is not None and ia == ib else crossing).append(b - a)
        return inside, crossing


# ---------- 集計 ----------

def pct(xs, q):
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def unit_sd(units):
    """units: [(obs_ms, n)]。率の SD と、ポアソンの見込みの SD（俯瞰 L5 の式・1 人なので単位の間だけ）。"""
    units = [u for u in units if u[0] > 0]
    if len(units) < 2:
        return None
    rates = [n / (ob / tc.H) for ob, n in units]
    mean_rate = sum(n for _, n in units) / (sum(ob for ob, _ in units) / tc.H)
    return {"units": len(units), "pooled_rate_per_h": round(mean_rate, 4),
            "sd_between_units": round(statistics.stdev(rates), 4),
            "sd_expected_poisson_mean": round(statistics.mean(math.sqrt(mean_rate / (ob / tc.H)) for ob, _ in units), 4),
            "unit_obs_h": tc.quart([ob / tc.H for ob, _ in units]),
            "unit_rate_per_h": tc.quart(rates)}


def boot_share(by_day, key, seed):
    days = sorted(by_day)
    rng = random.Random(seed)
    vals, undefined = [], 0
    for _ in range(B):
        rows = [r for d in (rng.choice(days) for _ in days) for r in by_day[d]]
        den = [r for r in rows if r.get(key) is not None]
        if not den:
            undefined += 1
            continue
        vals.append(sum(1 for r in den if r[key]) / len(den))
    out = {"B": B, "undefined_resamples": undefined}
    if undefined <= 0.05 * B and vals:
        out["ci95"] = [round(pct(vals, 0.025), 4), round(pct(vals, 0.975), 4)]
    return out


def analyze(days, seed):
    units = [dy.rows() for dy in days]
    allrows = [r for u in units for r in u]
    res = {"days": len(days), "obs_h": round(sum(dy.obs for dy in days) / tc.H, 3)}
    res["types"] = tc.summarize_types(units)
    # P3 位置ごとの率
    p3 = {}
    for p in tc.POS:
        num = den = 0
        per_day = []
        for dy, u in zip(days, units):
            n = sum(1 for r in u if not r.get("no_interval") and r["pos"] == p)
            ob = 0
            for i, a in enumerate(dy.rec.block_starts):
                nxt = dy.rec.block_starts[i + 1] if i + 1 < len(dy.rec.block_starts) else max(b for _, b in dy.intervals)
                lo, hi = (a, min(a + tc.EARLY_MS, nxt)) if p == "early" else (a + tc.EARLY_MS, nxt)
                if hi > lo:
                    ob += sum(max(0, min(hi, y) - max(lo, x)) for x, y in dy.intervals)
            num += n
            den += ob
            if ob > 0:
                per_day.append(n / (ob / tc.H))
        p3[p] = {"stalls": num, "obs_h": round(den / tc.H, 3),
                 "pooled_per_h": round(num / (den / tc.H), 4) if den else None, "day_median_per_h": tc.quart(per_day)}
    res["types"]["P3"] = p3
    # 候補 1a（ADR-024 の単位）
    fields = ("event_count", "source_episode_count", "receipt_count", "next_away_candidate_count", "censored_count",
              "degenerate_count", "n_at_risk_at_5min", "n_at_risk_at_10min")
    outs, mism = [], 0
    per_file = {"5min": [], "10min": []}
    for dy in days:
        r = dy.d["receipt_free_resumption"]
        outs += r["outcomes"]
        for k, hz in HORIZONS.items():
            mine = receipt_free(r["outcomes"], hz)
            theirs = r["receipt_free_at_" + k]
            if (mine is None) != (theirs is None) or (mine is not None and abs(mine - theirs) > 1e-12):
                mism += 1
            if theirs is not None:
                per_file[k].append(theirs)
    if mism:
        sys.exit("Aalen–Johansen の写しが replay の値と合わない")
    res["c1a_adr024_unit"] = {**{f: sum(dy.d["receipt_free_resumption"][f] for dy in days) for f in fields},
                              "pooled_receipt_free": {k: round(v, 4) if (v := receipt_free(outs, hz)) is not None else None
                                                      for k, hz in HORIZONS.items()},
                              "per_file_receipt_free": {k: tc.quart(v) for k, v in per_file.items()},
                              "files_with_value": {k: len(v) for k, v in per_file.items()},
                              "port_matches_replay_files": len(days)}
    ok = [r for r in allrows if not r.get("no_interval")]
    res["c1b_stall_unit_receipt_free_resumption"] = {
        "pre_paste_excluded": sum(1 for r in ok if r["pre_paste"]),
        "censored_excluded": sum(1 for r in ok if not r["pre_paste"] and r["resume"] is None),
        **tc.pooled(sum(1 for r in ok if r["c1b"]), sum(1 for r in ok if r["c1b"] is not None))}
    res["c1c_paste_after_stall"] = {k: {**tc.pooled(sum(1 for r in ok if r["c1c_" + k]),
                                                    sum(1 for r in ok if r["c1c_" + k] is not None)),
                                        "excluded": {why: sum(1 for r in ok if r["c1c_" + k + "_excl"] == why)
                                                     for why in ("pre_paste", "horizon_outside_interval")}}
                                    for k in HORIZONS}
    # 候補 2
    ins, cro = [], []
    for dy in days:
        a, b = dy.gaps()
        ins += a
        cro += b
    obs_h = sum(dy.obs for dy in days) / tc.H
    res["c2_clock"] = {"stall_len_s_resumed": tc.quart([r["len_ms"] / 1000 for r in ok if r["len_ms"] is not None]),
                       "s_to_resume_s": tc.quart([r["s_to_resume_ms"] / 1000 for r in ok if r["s_to_resume_ms"] is not None]),
                       "censored": sum(1 for r in ok if r["resume"] is None),
                       "gap180_inside_interval": {"n": len(ins), "per_obs_h": round(len(ins) / obs_h, 4),
                                                  "len_s": tc.quart([g / 1000 for g in ins])},
                       "gap180_crossing_interval": {"n": len(cro), "per_obs_h": round(len(cro) / obs_h, 4)}}
    # 候補 3
    types = {}
    for dy in days:
        for k, v in dy.d["types"].items():
            types[k] = types.get(k, 0) + v
    probe_like = {k: v for k, v in types.items() if any(w in k.lower() for w in PROBE_WORDS)}
    res["c3_self_report"] = {"row_types_all": dict(sorted(types.items())), "probe_or_self_report_like_types": probe_like,
                             "countable": False if not probe_like else None}
    # 単位
    day_units = [(dy.obs, sum(1 for r in u if not r.get("no_interval"))) for dy, u in zip(days, units)]
    blk = []
    for dy, u in zip(days, units):
        bl = dy.blocks()
        for r in u:
            if not r.get("no_interval") and r["block"] is not None:
                bl[r["block"]][1] += 1
        blk += [tuple(x) for x in bl]
    res["units"] = {"day": unit_sd(day_units), "block_obs_ge_30min": unit_sd([b for b in blk if b[0] >= MIN_BLOCK_OBS]),
                    "blocks_total": len(blk), "blocks_obs_ge_30min": sum(1 for b in blk if b[0] >= MIN_BLOCK_OBS),
                    "block_obs_h_all": tc.quart([b[0] / tc.H for b in blk])}
    # 受領の経路
    np_ = sum(len(dy.paste) for dy in days)
    with_focus = sum(1 for dy in days for p in dy.paste if count_in(dy.rec.focus, p - PASTE_FOCUS_WIN, p, hi_open=True) > 0)
    in_stall = 0
    for dy, u in zip(days, units):
        covered = set()
        for r in u:
            if r.get("no_interval"):
                continue
            lo = bisect.bisect_right(dy.paste, r["t0"])
            hi = bisect.bisect_right(dy.paste, r["t0"] + HORIZONS["5min"])
            covered.update(range(lo, hi))
        in_stall += len(covered)
    chars = [c for dy in days for c in dy.paste_chars]
    res["receipt_route"] = {"pastes": np_, "per_obs_h": round(np_ / obs_h, 4),
                            "with_focus_in_prev_30s": tc.pooled(with_focus, np_),
                            "in_some_stall_5min_unique": tc.pooled(in_stall, np_),
                            "chars_zero": sum(1 for c in chars if c == 0), "chars_null": sum(1 for c in chars if c is None)}
    # 段 2 の材料（C6）
    c6 = {}
    for c in tc.CLASSES:
        for p in tc.POS:
            by_day = {i: [r for r in tc.typed(u) if r["pre_class"] == c and r["pos"] == p] for i, u in enumerate(units)}
            rs = [r for v in by_day.values() for r in v]
            cell = {"n": len(rs)}
            for key in ("c1b", "c1c_5min"):
                den = [r for r in rs if r.get(key) is not None]
                cell[key] = {**tc.pooled(sum(1 for r in den if r[key]), len(den)),
                             "boot": boot_share(by_day, key, seed) if den else None}
            cell["c1c_5min_excluded"] = {why: sum(1 for r in rs if r["c1c_5min_excl"] == why)
                                         for why in ("pre_paste", "horizon_outside_interval")}
            cell["c1b_censored"] = sum(1 for r in rs if not r["pre_paste"] and r["resume"] is None)
            c6[f"{c}|{p}"] = cell
    res["c6_stage2"] = c6
    return res, allrows


def run(work, seed, out_dir, *files):
    seed = int(seed)
    days, excl, excl_press, t3_onsets = [], 0, 0, 0
    for f in files:
        b = os.path.basename(f)[:-len(".ndjson")]
        d = json.load(open(os.path.join(work, b + ".json")))
        if d["input_sha256"] != sha256(f):
            sys.exit("中間と入力の SHA-256 が合わない: 中間を作り直す")
        if not d["focus"]:
            excl += 1
            excl_press += len(d["keys"])
            continue
        dy = Day(d)
        days.append(dy)
        if b.split("_")[2] <= T3_TO:
            t3_onsets += len(d["onsets"])
    res, allrows = analyze(days, seed)
    res["files"] = {"given": len(files), "excluded_no_focus": excl, "excluded_presses": excl_press, "used": len(days),
                    "replay_stderr_nonempty": sum(1 for dy in days if any(dy.d["replay_stderr_bytes"].values())),
                    "check_t3_12_files_onsets": t3_onsets, "t3_reported_onsets": 1313}
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(os.path.join(out_dir, "o1.json"), "w"), indent=1)
    json.dump([{k: v for k, v in r.items() if k not in ("interval",)} for r in allrows],
              open(os.path.join(work, "ledger.json"), "w"))
    print(json.dumps(res["files"]))


def selftest():
    tc.selftest()
    # AJ: 受領 1・競合 1・打ち切り 1
    outs = [{"elapsed_ms": 1000, "kind": "receipt"}, {"elapsed_ms": 2000, "kind": "next_away_candidate"},
            {"elapsed_ms": 400_000, "kind": "censored"}]
    assert abs(cif_receipt(outs, 300_000) - 1 / 3) < 1e-12
    # 競合が先・受領が後（競合がリスク集合と生存を減らす）
    outs2 = [{"elapsed_ms": 1000, "kind": "next_away_candidate"}, {"elapsed_ms": 2000, "kind": "receipt"},
             {"elapsed_ms": 400_000, "kind": "censored"}]
    assert abs(cif_receipt(outs2, 300_000) - 1 / 3) < 1e-12
    assert receipt_free([{"elapsed_ms": 0, "kind": "next_away_candidate"}], 300_000) is None
    assert cif_receipt([{"elapsed_ms": 1000, "kind": "censored"}], 300_000) is None
    # 1 日の合成
    text = [i * 1000 for i in range(100)] + [130_000 + i * 1000 for i in range(10)]
    keys = [[t, "alphabetic"] for t in text] + [[95_500, "backspace"], [96_500, "backspace"]]
    keys.sort()
    d = {"keys": keys, "pointer": [[100_000, 3, 0, 0]], "focus": [50_000], "paste": [[120_000, 5], [700_000, None]],
         "observed_intervals": [{"a_ms": 0, "b_ms": 800_000}], "onsets": [[105_000, 110_000]],
         "receipt_free_resumption": {"outcomes": outs, "receipt_free_at_5min": 2 / 3, "receipt_free_at_10min": 2 / 3,
                                     **{f: 0 for f in ("event_count", "source_episode_count", "receipt_count",
                                                       "next_away_candidate_count", "censored_count",
                                                       "degenerate_count", "n_at_risk_at_5min", "n_at_risk_at_10min")}},
         "types": {"key": len(keys)}, "replay_stderr_bytes": {"features": 0, "metrics": 0}}
    dy = Day(d)
    rows = dy.rows()
    r = rows[0]
    assert r["pre_class"] == "delete2" and r["pre_flags"]["move"] and not r["pre_flags"]["focus"], r
    assert r["c1b"] is False and r["c1c_5min"] is True and r["c1c_10min"] is True, r
    res, _ = analyze([dy], 1)
    assert res["c1b_stall_unit_receipt_free_resumption"]["num"] == 0
    assert res["receipt_route"]["in_some_stall_5min_unique"]["num"] == 1
    assert res["receipt_route"]["chars_null"] == 1
    assert res["c6_stage2"]["delete2|early"]["n"] == 1
    assert res["c3_self_report"]["countable"] is False
    # 前の窓に貼り付け → 1b・1c から外す
    d2 = dict(d, paste=[[108_000, 3]])
    r2 = Day(d2).rows()[0]
    assert r2["pre_paste"] and r2["c1b"] is None and r2["c1c_5min_excl"] == "pre_paste"
    # 貼り付けが再開の押下と同じ時刻（O1 の Cmd+V は v の押下と同じ ms に記録される）→ 受領ありの再開
    d2b = dict(d, paste=[[130_000, 3]])
    assert Day(d2b).rows()[0]["c1b"] is False
    # 地平が区間を出る
    d3 = dict(d, observed_intervals=[{"a_ms": 0, "b_ms": 300_000}])
    r3 = Day(d3).rows()[0]
    assert r3["c1c_5min"] is None and r3["c1c_5min_excl"] == "horizon_outside_interval"
    # 180 秒の途切れ: 区間の中と切れ目
    dg = dict(d, keys=[[0, "alphabetic"], [200_000, "alphabetic"], [500_000, "alphabetic"]],
              observed_intervals=[{"a_ms": 0, "b_ms": 300_000}, {"a_ms": 450_000, "b_ms": 800_000}])
    ins, cro = Day(dg).gaps()
    assert ins == [200_000] and cro == [300_000]
    print("o1 selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(*sys.argv[1:])
