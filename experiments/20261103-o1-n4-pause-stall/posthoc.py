"""事後（conditions.md に無い・notes の逸脱 1〜3）。結果を見た後に足した量で、判定に使わない。

1. 単位の観測時間の下限を 1 時間・2 時間に下げた C0 の日の揺れ（SD・見込みとの比・数え上げの分を引いた超過の SD）。
   条件の 4 時間の下限では A 以外の SD が出なかったため。
2. データの量の内訳: 観測 0 の本の数と、その本の押下・feat 行の数／押下が観測区間に入る割合／ポインタとフォーカスの行の数。
   notes の「計器が切れていたか」「C1・C2 を比べられるか」の読みの根拠。
3. 観測が 1 時間に満たない人を除いた人の間の幅（C0 の率・θ・分位など）。

usage: posthoc.py <work_dir> <out.json>
"""
import bisect
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pausestall as ps  # noqa: E402

MIN_PERSON_OBS_H = 1.0   # 3. の人の下限


def sd_floor(units, floor_h):
    u = [x for x in units if x[0] >= floor_h * ps.tc.H]
    if len(u) < ps.MIN_UNITS:
        return {"status": "単位不足", "units": len(u)}
    r = ps.ao.unit_sd(u)
    r["status"] = "ok"
    sd, ex = r["sd_between_units"], r["sd_expected_poisson_mean"]
    r["sd_ratio"] = round(sd / ex, 4) if ex else None
    r["excess_sd"] = round(math.sqrt(sd * sd - ex * ex), 4) if sd >= ex else 0.0
    return r


def volume(files):
    """2. 本ごとの中間から、観測 0 の本と、観測のある本の中の押下の割合・行の数を数える。"""
    out = {"zero_obs_files": 0, "presses_in_zero_obs_files": 0, "feat_rows_in_zero_obs_files": 0,
           "presses": 0, "presses_in_observed": 0, "pointer_rows": 0, "focus_rows": 0}
    for f in files:
        try:
            d = json.load(open(f["inter"]))
        except (OSError, ValueError):
            sys.exit("中間が読めない（パスは出さない）")
        iv = sorted((x["a_ms"], x["b_ms"]) for x in d["observed_intervals"])
        ks = [k[0] for k in d["keys"]]
        if sum(b - a for a, b in iv) <= 0:
            out["zero_obs_files"] += 1
            out["presses_in_zero_obs_files"] += len(ks)
            out["feat_rows_in_zero_obs_files"] += d["types"].get("feat", 0)
            continue
        starts = [a for a, _ in iv]
        out["presses"] += len(ks)
        for t in ks:
            i = bisect.bisect_right(starts, t) - 1
            out["presses_in_observed"] += 1 if i >= 0 and iv[i][1] >= t else 0
        out["pointer_rows"] += len(d["pointer"])
        out["focus_rows"] += len(d["focus"])
    out["share_presses_in_observed"] = round(out["presses_in_observed"] / out["presses"], 4) if out["presses"] else None
    del out["presses_in_observed"]
    return out


def width(full, keys, people):
    out = {}
    for key in keys:
        v = {k: full["between_people"][key]["by_person"][k] for k in people}
        vs = [x for x in v.values() if x is not None]
        out[key] = {"by_person": v, "sd": round(statistics.stdev(vs), 4) if len(vs) > 1 else None,
                    "max_over_min": round(max(vs) / min(vs), 4) if len(vs) > 1 and min(vs) > 0 else None}
    return out


def main(work, out):
    table = json.load(open(os.path.join(work, "files.json")))
    full = json.load(open(os.path.join(work, "full.json")))
    res = {"sd_floor": {}, "volume": {}}
    for v in table["people"].values():
        k = v["symbol"]
        p = ps.Person(v["files"])
        c0u = [(dy.obs, len(dy.c0()[0])) for dy in p.all]
        res["sd_floor"][k] = {f"floor_{h}h": {"file": sd_floor(c0u, h), "date": sd_floor(ps.by_date(c0u, p.dates_all), h)}
                              for h in (1, 2)}
        res["volume"][k] = volume(v["files"])
    keep = sorted(k for k, r in full["people"].items() if r["obs_h_all"] >= MIN_PERSON_OBS_H)
    res["width_people_ge_1h"] = {"people": keep, "min_person_obs_h": MIN_PERSON_OBS_H, **width(full, [
        "C0_pooled_per_h", "C0_theta_median_s", "C0_share_long_or_censored", "P_press_q0.5_s", "P_press_q0.99_s",
        "P_press_q0.999_s", "P_press_share_gt_30s", "P_press_share_gt_180s", "P_press_time_share_gt_180s"], keep)}
    res["sd_floor"] = dict(sorted(res["sd_floor"].items()))
    res["volume"] = dict(sorted(res["volume"].items()))
    text = json.dumps(ps.public(res), indent=1, ensure_ascii=False)
    vers = {s for v in table["people"].values() for f in v["files"] for s in (str(f.get("app_version")), str(f.get("hmm_version")))}
    lk = ps.leaks(text, table["people"], vers)
    if lk:
        sys.exit("漏れ: " + "・".join(lk))
    open(out, "w").write(text)


if __name__ == "__main__":
    main(*sys.argv[1:])
