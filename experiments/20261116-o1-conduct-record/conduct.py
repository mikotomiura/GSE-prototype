"""R2 実施の記録（人ごと）。usage: conduct.py <work_dir> <out_json> | --selftest"""
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_common as cm  # noqa: E402

TYPES = ("focus_transition", "pointer_bin", "paste", "ime_state", "ime_shadow", "feat", "hook_health",
         "recording_pause", "secure_input")
POINTER_PER_H = 60  # R2: 「ポインタあり」の下限（観測 1 時間あたりの pointer_bin の行）


def quart(xs):
    if not xs:
        return None
    s = sorted(xs)
    q = statistics.quantiles(s, n=4, method="inclusive") if len(s) > 1 else [s[0]] * 3
    return {"n": len(s), "q1": round(q[0], 3), "median": round(q[1], 3), "q3": round(q[2], 3)}


def day_numbers(nums):
    if not nums:
        return {"max_day_number": 0, "missing_day_numbers": 0, "duplicated_day_numbers": 0}
    mx = max(nums)
    seen = {}
    for n in nums:
        seen[n] = seen.get(n, 0) + 1
    return {"max_day_number": mx, "missing_day_numbers": sum(1 for k in range(1, mx + 1) if k not in seen),
            "duplicated_day_numbers": sum(1 for v in seen.values() if v >= 2)}


def pointer_usable(rows):
    """R2: pointer_bin の行が観測 1 時間あたり POINTER_PER_H 以上か（全部の本で数える）。"""
    obs = sum(cm.obs_ms(d) for _, d, _ in rows)
    n = sum(d["types"].get("pointer_bin", 0) for _, d, _ in rows)
    return obs > 0 and n / (obs / cm.H) >= POINTER_PER_H


def person(rows):
    obs = [cm.obs_ms(d) for _, d, _ in rows]
    tot_h = sum(obs) / cm.H
    res = {"files_used": len(rows), "files_zero_obs": sum(1 for o in obs if o <= 0),
           "files_no_focus": sum(1 for _, d, _ in rows if not d["focus"]),
           "calendar_days": len({f["date"] for f, _, _ in rows}),
           **day_numbers([x["day_number"] for _, _, x in rows]),
           "obs_h": round(tot_h, 3), "unit_obs_h": quart([o / cm.H for o in obs]),
           "app_version_kinds": len({str(f.get("app_version")) for f, _, _ in rows}),
           "pointer_usable": pointer_usable(rows), "rows": {}}
    counts = {"key_press": [len(d["keys"]) for _, d, _ in rows]}
    for t in TYPES:
        counts[t] = [d["types"].get(t, 0) for _, d, _ in rows]
    known = set(TYPES) | {"key"}
    counts["other_types"] = [sum(v for k, v in d["types"].items() if k not in known) for _, d, _ in rows]
    for k, v in counts.items():
        n = sum(v)
        has = sum(1 for x in v if x > 0)
        res["rows"][k] = {"total": n, "per_obs_h": round(n / tot_h, 3) if tot_h > 0 else None,
                          "files_with_rows": {"num": has, "den": len(v), "ratio": round(has / len(v), 4) if v else None}}
    return res


def run(work, out):
    table, people = cm.load_people(work)
    res = {"people": {k: person(v) for k, v in sorted(people.items())}}
    cm.write_public(res, work, "conduct", out, table)


def selftest():
    def mk(day, date, obs, types, keys=3, focus=True):
        d = {"observed_intervals": [{"a_ms": 0, "b_ms": obs}], "types": types, "keys": [[i, "alphabetic"] for i in range(keys)],
             "focus": [1] if focus else []}
        return ({"date": date, "app_version": "x"}, d, {"day_number": day})
    rows = [mk(1, "d1", cm.H, {"pointer_bin": 100, "focus_transition": 5, "key": 6, "weird": 2}),
            mk(2, "d1", cm.H, {"pointer_bin": 30, "paste": 1, "key": 4}, focus=False),
            mk(4, "d2", 0, {"key": 0}, keys=0),
            mk(4, "d3", 2 * cm.H, {"ime_state": 3})]
    r = person(rows)
    assert r["files_used"] == 4 and r["files_zero_obs"] == 1 and r["files_no_focus"] == 1, r
    assert r["calendar_days"] == 3
    assert (r["max_day_number"], r["missing_day_numbers"], r["duplicated_day_numbers"]) == (4, 1, 1), r
    assert r["obs_h"] == 4.0
    assert r["rows"]["pointer_bin"]["total"] == 130 and r["rows"]["pointer_bin"]["per_obs_h"] == 32.5
    assert r["rows"]["pointer_bin"]["files_with_rows"] == {"num": 2, "den": 4, "ratio": 0.5}
    assert r["rows"]["key_press"]["total"] == 9
    assert r["rows"]["other_types"]["total"] == 2
    assert r["pointer_usable"] is False  # 32.5 / h < 60
    rows[0][1]["types"]["pointer_bin"] = 300
    assert pointer_usable(rows) is True  # 330 / 4 h = 82.5
    assert day_numbers([]) == {"max_day_number": 0, "missing_day_numbers": 0, "duplicated_day_numbers": 0}
    print("conduct selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(*sys.argv[1:])
