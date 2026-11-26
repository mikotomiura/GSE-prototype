"""R4 停滞の手前の窓の型（人ごと・記述）。usage: prewin.py <work_dir> <seed> <out_json> | --selftest

停滞の窓の型（同じ長さ `pre_class`・固定長 `pre_fixed_class`）と、同じ本の観測区間に一様に置いた無作為の窓の型の割合と差。
差の区間は人の中で日（名前の日付）を復元抽出（B 回）した百分位。
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_common as cm  # noqa: E402
import analyze_o1 as ao  # noqa: E402
import posthoc as ph  # noqa: E402
import types_core as tc  # noqa: E402

REPS = 10
B = 2000
KINDS = {"same_length": "pre_class", "fixed_30s": "pre_fixed_class"}


def file_counts(d, rng):
    """1 本の {kind: {"stall": {class: n}, "random": {class: n}}}。"""
    dy = ao.Day(d)
    out = {k: {"stall": {c: 0 for c in tc.CLASSES}, "random": {c: 0 for c in tc.CLASSES}} for k in KINDS}
    for s, t0 in d["onsets"]:
        r = dy.rec.stall(s, t0)
        if r.get("no_interval"):
            continue
        for kind, key in KINDS.items():
            c = r.get(key)
            if c is None:
                continue
            out[kind]["stall"][c] += 1
            length = (t0 - s + tc.PRE_WIN) if kind == "same_length" else tc.PRE_WIN
            for _ in range(REPS):
                u = ph.place(rng, dy.intervals, length)
                if u is None:
                    continue
                out[kind]["random"][tc.Rec.klass(dy.rec.flags(u - length, u))] += 1
    return out


def merge(counts):
    """同じ日の本の数を足す。"""
    out = {k: {"stall": {c: 0 for c in tc.CLASSES}, "random": {c: 0 for c in tc.CLASSES}} for k in KINDS}
    for x in counts:
        for k in KINDS:
            for side in ("stall", "random"):
                for c in tc.CLASSES:
                    out[k][side][c] += x[k][side][c]
    return out


def shares(units, kind, side):
    tot = {c: sum(u[kind][side][c] for u in units) for c in tc.CLASSES}
    den = sum(tot.values())
    return tot, den


def person(units, seed):
    rng = random.Random(seed)
    res = {"days_used": len(units)}
    for kind in KINDS:
        st, sd = shares(units, kind, "stall")
        rd, rn = shares(units, kind, "random")
        boots = {c: [] for c in tc.CLASSES}
        fails = 0
        for _ in range(B):
            smp = [units[rng.randrange(len(units))] for _ in units]
            bst, bsd = shares(smp, kind, "stall")
            brd, brn = shares(smp, kind, "random")
            if bsd == 0 or brn == 0:
                fails += 1
                continue
            for c in tc.CLASSES:
                boots[c].append(bst[c] / bsd - brd[c] / brn)
        res[kind] = {"stalls_typed": sd, "random_windows": rn, "boot_failures": fails, "by_class": {
            c: {"stall": {"num": st[c], "den": sd, "ratio": round(st[c] / sd, 4) if sd else None},
                "random": {"num": rd[c], "den": rn, "ratio": round(rd[c] / rn, 4) if rn else None},
                "diff": round(st[c] / sd - rd[c] / rn, 4) if sd and rn else None,
                "diff_ci95": cm.ci95(boots[c])}
            for c in tc.CLASSES}}
    return res


def run(work, seed, out):
    seed = int(seed)
    table, people = cm.load_people(work)
    res = {"people": {}}
    for k, rows in sorted(people.items()):
        rng = random.Random(f"{seed}-{k}")
        by_date = {}
        for f, d, _ in rows:
            if d["focus"] and cm.obs_ms(d) > 0:
                by_date.setdefault(f["date"], []).append(file_counts(d, rng))
        units = [merge(v) for _, v in sorted(by_date.items())]  # 区間の単位は日（同じ日の本は状態を共有する）
        res["people"][k] = person(units, seed) if units else {"days_used": 0}
    cm.write_public(res, work, "prewin", out, table)


def synth(rng, with_focus_before):
    """合成の 1 本: 観測区間 1 本（2 時間）・停滞 20 件。停滞の窓にだけ遷移を入れるか。背景の遷移はまばら。"""
    a, b = 0, 2 * cm.H
    onsets, focus, keys = [], [], []
    for i in range(20):
        s = a + 120_000 + i * 300_000
        t0 = s + 40_000
        onsets.append([s, t0])
        if with_focus_before:
            focus.append(t0 - 10_000)
    focus += [rng.uniform(a, b) for _ in range(3)]
    return {"keys": keys, "pointer": [], "focus": sorted(focus), "paste": [], "onsets": onsets,
            "observed_intervals": [{"a_ms": a, "b_ms": b}]}


def selftest():
    rng = random.Random(7)
    pos = [file_counts(synth(rng, True), rng) for _ in range(8)]
    r = person(pos, 1)
    ci = r["fixed_30s"]["by_class"]["focus"]["diff_ci95"]
    assert ci[0] > 0, r["fixed_30s"]["by_class"]["focus"]
    assert r["same_length"]["by_class"]["focus"]["diff_ci95"][0] > 0
    neg = [file_counts(synth(rng, False), rng) for _ in range(8)]
    r = person(neg, 1)
    ci = r["fixed_30s"]["by_class"]["focus"]["diff_ci95"]
    assert ci[0] <= 0 <= ci[1], ci
    # 無作為の窓の数は停滞 × REPS（置けた分）
    assert r["fixed_30s"]["random_windows"] == r["fixed_30s"]["stalls_typed"] * REPS
    # 窓の長さ: 遷移が 50 秒ごとにある本では、同じ長さ（70 秒）の無作為の窓は必ず遷移に当たり、固定長（30 秒）は当たらないこともある
    dense = {"keys": [], "pointer": [], "focus": list(range(25_000, 2 * cm.H, 50_000)), "paste": [],
             "onsets": [[300_000 + i * 300_000, 340_000 + i * 300_000] for i in range(10)],
             "observed_intervals": [{"a_ms": 0, "b_ms": 2 * cm.H}]}
    r = person([file_counts(dense, random.Random(3))], 1)
    assert r["same_length"]["by_class"]["focus"]["random"]["ratio"] == 1.0, r["same_length"]
    assert 0 < r["fixed_30s"]["by_class"]["focus"]["random"]["ratio"] < 1.0, r["fixed_30s"]
    m = merge([file_counts(synth(rng, True), rng), file_counts(synth(rng, True), rng)])
    assert m["fixed_30s"]["stall"]["focus"] == 40, m["fixed_30s"]["stall"]
    print("prewin selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(*sys.argv[1:])
