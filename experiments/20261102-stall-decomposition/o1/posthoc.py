"""事後の確かめ（conditions.md に無い・判定に使わない・notes の逸脱 2）。集計値だけを出す。

usage: posthoc.py <work_dir> <seed> <out_json> <ndjson>...
1. 押下の category の割合
2. 貼り付けの行と、同じ時刻か直前の押下との時刻の差・その押下の category
3. 停滞の θ（t0 − s）の分布
4. 基準率: 停滞ごとに、同じ長さ（30 秒 + θ）の窓と固定長 30 秒の窓を、同じ日の観測区間の中に一様に 10 回ずつ置き、
   手の様子の類の割合を出す（停滞の前の窓の割合が、窓の長さと出来事の密度だけで出る値とどれだけ違うか）
"""
import bisect
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "../../20261101-klicke-early-stall-trigger/scripts"))
import analyze_o1 as a  # noqa: E402
import types_core as tc  # noqa: E402

REPS = 10


def place(rng, intervals, length):
    """長さ length の窓 [u − length, u] を、1 つの観測区間に収まるように一様に置く。置けなければ None。"""
    ok = [(x + length, y) for x, y in intervals if y - x >= length]
    tot = sum(y - x for x, y in ok)
    if tot <= 0:
        return None
    v = rng.uniform(0, tot)
    for x, y in ok:
        if v <= y - x:
            return x + v
        v -= y - x
    return ok[-1][1]


def main(work, seed, out, *files):
    rng = random.Random(int(seed))
    cats, dif, dif_cat, theta = {}, [], {}, []
    base = {"same_length": {c: 0 for c in tc.CLASSES}, "fixed_30s": {c: 0 for c in tc.CLASSES}}
    obs_stall = {c: 0 for c in tc.CLASSES}
    nbase = {"same_length": 0, "fixed_30s": 0}
    focus_rows = obs_h = 0
    for f in files:
        b = os.path.basename(f)[:-len(".ndjson")]
        d = json.load(open(os.path.join(work, b + ".json")))
        if d["input_sha256"] != a.sha256(f):
            sys.exit("中間と入力の SHA-256 が合わない")
        if not d["focus"]:
            continue
        dy = a.Day(d)
        focus_rows += len(d["focus"])
        obs_h += dy.obs / tc.H
        for _, c in d["keys"]:
            cats[c] = cats.get(c, 0) + 1
        kt = [k[0] for k in d["keys"]]
        for t, _ in d["paste"]:
            i = bisect.bisect_right(kt, t) - 1
            if i >= 0:
                dif.append(t - kt[i])
                c = d["keys"][i][1]
                dif_cat[c] = dif_cat.get(c, 0) + 1
        for s, t0 in d["onsets"]:
            theta.append((t0 - s) / 1000)
            r = dy.rec.stall(s, t0)
            if r.get("no_interval") or r["pre_class"] is None:
                continue
            obs_stall[r["pre_class"]] += 1
            for kind, length in (("same_length", t0 - s + tc.PRE_WIN), ("fixed_30s", tc.PRE_WIN)):
                for _ in range(REPS):
                    u = place(rng, dy.intervals, length)
                    if u is None:
                        continue
                    base[kind][tc.Rec.klass(dy.rec.flags(u - length, u))] += 1
                    nbase[kind] += 1
    tot = sum(cats.values())
    nst = sum(obs_stall.values())
    res = {"key_category_share": {k: round(v / tot, 4) for k, v in sorted(cats.items(), key=lambda kv: -kv[1])},
           "paste_minus_last_press_ms": tc.quart(dif), "paste_same_ms_as_press": tc.pooled(sum(1 for x in dif if x == 0), len(dif)),
           "last_press_category_before_paste": dif_cat,
           "stall_theta_s": tc.quart(theta),
           "focus_rows_per_obs_h": round(focus_rows / obs_h, 2),
           "stall_pre_window_class_share": {c: tc.pooled(v, nst) for c, v in obs_stall.items()},
           "random_window_class_share": {k: {c: tc.pooled(v, nbase[k]) for c, v in base[k].items()} for k in base},
           "random_windows_per_stall": REPS}
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        rng = random.Random(1)
        for _ in range(200):
            u = place(rng, [(0, 10), (100, 200)], 50)
            assert 150 <= u <= 200
        assert place(rng, [(0, 10)], 50) is None
        print("posthoc selftest ok")
    else:
        main(*sys.argv[1:])
