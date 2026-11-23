"""フォーカスの遷移と受領（conditions.md）。打鍵の本文は読まない: NDJSON からは
`focus_transition` と `paste` の時刻と、`key` 行の押下の時刻だけを使う（`key` 行の category は読まない）。出力は集計だけ。

usage: analyze.py <work_dir with *.onsets.json> <sessions_dir> <seed> <out_dir> <from YYYYMMDD> <to YYYYMMDD>
"""
import bisect
import glob
import hashlib
import json
import os
import random
import statistics
import sys

W_MS = 30_000
HORIZONS = {"5min": 300_000, "10min": 600_000}
AWAY_MS = 180_000
B = 2000


def times(path):
    focus, paste, press = [], [], []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            # 前段の絞り込みは緩く（書式の空白に依らない）、型の判定は json の後で行う
            if '"focus_transition"' not in line and '"paste"' not in line and '"key"' not in line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            ty = o.get("type")
            if ty == "focus_transition":
                focus.append(o["t"])
            elif ty == "paste":
                paste.append(o["t"])
            elif ty == "key" and o.get("press") is True:
                press.append(o["t"])
    return sorted(focus), sorted(paste), sorted(press)


def any_in(xs, a, b):
    """xs に [a, b] の値があるか（閉区間）。"""
    i = bisect.bisect_left(xs, a)
    return i < len(xs) and xs[i] <= b


def first_in(xs, a, b):
    i = bisect.bisect_left(xs, a)
    return xs[i] if i < len(xs) and xs[i] <= b else None


def any_in_open_left(xs, a, b):
    """xs に (a, b] の値があるか。"""
    i = bisect.bisect_right(xs, a)
    return i < len(xs) and xs[i] <= b


def inside(intervals, a, b):
    return any(lo <= a and b <= hi for lo, hi in intervals)


def rr_rd(rows):
    e = [r for r in rows if r["exposed"]]
    u = [r for r in rows if not r["exposed"]]
    if not e or not u:
        return None, None, None
    pe = sum(r["y"] for r in e) / len(e)
    pu = sum(r["y"] for r in u) / len(u)
    rr = pe / pu if pu > 0 else None
    if pe == 0 or pu == 0:
        rr = None
    return rr, pe - pu, (pe, pu)


def pct(xs, q):
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def boot(by_day, seed):
    days = sorted(by_day)
    rng = random.Random(seed)
    rrs, rds, undefined = [], [], 0
    for _ in range(B):
        rows = [r for d in (rng.choice(days) for _ in days) for r in by_day[d]]
        rr, rd, _ = rr_rd(rows)
        if rd is not None:
            rds.append(rd)
        if rr is None:
            undefined += 1
        else:
            rrs.append(rr)
    out = {"undefined_rr_resamples": undefined, "B": B}
    if rrs:
        out["rr_ci95"] = [pct(rrs, 0.025), pct(rrs, 0.975)]
    if rds:
        out["rd_ci95"] = [pct(rds, 0.025), pct(rds, 0.975)]
    return out


def verdict(ci, undefined):
    if undefined > 0.05 * B or ci is None:
        return "undetermined"
    lo, hi = ci
    if lo > 1:
        return "precedes"
    if hi < 1:
        return "reverse"
    return "not_visible"


def sha256_prefix(path, n=16):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def file_date(name):
    """gse_o1_YYYYMMDD_HHMMSS.ndjson の日付。"""
    return name.split("_")[2]


def main():
    work, sessions, seed, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    date_from, date_to = sys.argv[5], sys.argv[6]
    os.makedirs(out, exist_ok=True)
    excluded_files, files = [], []
    base_rows = []
    lags = []
    for sp in sorted(glob.glob(os.path.join(work, "*.onsets.json"))):
        d = json.load(open(sp))
        name = d["provenance"]["source_basename"]
        if not (date_from <= file_date(name) <= date_to):
            excluded_files.append({"file": name, "reason": "outside period (C2; 10-31 excluded as still being written, decisions 4)"})
            continue
        src = os.path.join(sessions, name)
        # 中間が今の入力から作られたことを確かめる（使い回しで古い中間を読まない）
        want = d["provenance"]["source_sha256_prefix"]
        got = sha256_prefix(src, len(want))
        if got != want:
            sys.exit(f"stale intermediate for {name}: source sha256 {got} != {want}; delete WORK and rerun")
        focus, paste, press = times(src)
        if not focus:
            excluded_files.append({"file": name, "reason": "focus_transition 0 rows (config_gated)"})
            continue
        if not press:
            print(f"warning: no key presses parsed in {name}", file=sys.stderr)
        intervals = [(iv["a_ms"], iv["b_ms"]) for iv in d["provenance"]["observed_intervals"]]
        files.append({"file": name, "source_sha256_prefix": want, "hmm_version": d["provenance"]["hmm_version"],
                      "prereg_version": d["config"].get("prereg_version"), "onsets": len(d["onsets"]),
                      "focus_rows": len(focus), "paste_rows": len(paste)})
        for o in d["onsets"]:
            s, t0 = o["s"], o["t0"]
            a = s - W_MS
            exposed = any_in(focus, a, t0)
            paste_in_window = any_in(paste, a, t0)
            # 沈黙の長さ（記述 5）: s − W から t0 の後の最初の押下まで。押下が無ければ None（層に入れない）。
            j = bisect.bisect_right(press, t0)
            silence = press[j] - a if j < len(press) else None
            fi = first_in(focus, a, t0)
            if fi is not None:
                lags.append({"lag_to_t0_ms": t0 - fi, "before_s": fi < s})
            r = {"day": name, "exposed": exposed, "paste_in_window": paste_in_window, "t0": t0, "a": a,
                 "silence_ms": silence}
            for h, hm in HORIZONS.items():
                r["in_obs_" + h] = inside(intervals, t0, t0 + hm)
                # 感度（レビューの後に足した・判定に使わない）: 曝露の窓も同じ観測区間に収まる
                r["in_obs_with_exposure_" + h] = inside(intervals, a, t0 + hm)
                r["y_" + h] = any_in_open_left(paste, t0, t0 + hm)
            base_rows.append(r)

    result = {"files_used": files, "files_excluded": excluded_files, "n_onsets_total": len(base_rows)}
    for h in HORIZONS:
        excl = {"paste_in_window": 0, "horizon_outside_observation": 0}
        rows = []
        for r in base_rows:
            if r["paste_in_window"]:
                excl["paste_in_window"] += 1
                continue
            if not r["in_obs_" + h]:
                excl["horizon_outside_observation"] += 1
                continue
            rows.append({"day": r["day"], "exposed": r["exposed"], "y": r["y_" + h], "silence_ms": r["silence_ms"],
                         "obs_exposure": r["in_obs_with_exposure_" + h]})
        by_day = {}
        for r in rows:
            by_day.setdefault(r["day"], []).append(r)
        rr, rd, ps = rr_rd(rows)
        b = boot(by_day, seed)
        ne = sum(r["exposed"] for r in rows)
        ye = sum(r["y"] for r in rows if r["exposed"])
        yu = sum(r["y"] for r in rows if not r["exposed"])
        res = {
            "excluded": excl, "n": len(rows), "n_days": len(by_day),
            "exposed": {"n": ne, "receipt": ye}, "unexposed": {"n": len(rows) - ne, "receipt": yu},
            "rr": rr, "rd": rd, "p_exposed": ps[0] if ps else None, "p_unexposed": ps[1] if ps else None,
            **b,
            "trigger_view": {
                "false_alarm_share_among_exposed": (ne - ye) / ne if ne else None,
                "exposed_share_among_receipts": ye / (ye + yu) if (ye + yu) else None,
                "unexposed_share_of_stalls": (len(rows) - ne) / len(rows) if rows else None,
            },
        }
        res["verdict"] = verdict(b.get("rr_ci95"), b["undefined_rr_resamples"])
        strata = {}
        for name_, pred in (("silence_over_180s", lambda x: x is not None and x > AWAY_MS),
                            ("silence_180s_or_less", lambda x: x is not None and x <= AWAY_MS),
                            ("no_press_after_t0", lambda x: x is None)):
            sr = [r for r in rows if pred(r["silence_ms"])]
            srr, srd, sps = rr_rd(sr)
            strata[name_] = {"n": len(sr), "n_exposed": sum(r["exposed"] for r in sr), "rr": srr, "rd": srd,
                             "p_exposed": sps[0] if sps else None, "p_unexposed": sps[1] if sps else None}
        res["strata_by_silence"] = strata
        sens = [r for r in rows if r["obs_exposure"]]
        s_by_day = {}
        for r in sens:
            s_by_day.setdefault(r["day"], []).append(r)
        srr, srd, sps = rr_rd(sens)
        sb = boot(s_by_day, seed)
        res["sensitivity_exposure_window_observed"] = {
            "n": len(sens), "n_exposed": sum(r["exposed"] for r in sens), "rr": srr, "rd": srd,
            "p_exposed": sps[0] if sps else None, "p_unexposed": sps[1] if sps else None, **sb}
        result[h] = res
    if lags:
        lv = [x["lag_to_t0_ms"] for x in lags]
        result["first_focus_lag_to_t0_ms"] = {
            "n": len(lv), "median": statistics.median(lv), "q1": pct(lv, 0.25), "q3": pct(lv, 0.75),
            "share_before_s": sum(x["before_s"] for x in lags) / len(lags),
        }
    json.dump(result, open(os.path.join(out, "result.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps({h: {k: result[h][k] for k in ("n", "rr", "rr_ci95", "verdict") if k in result[h]} for h in HORIZONS},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
