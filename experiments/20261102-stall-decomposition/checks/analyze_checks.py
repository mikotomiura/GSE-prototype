"""段 1 の残りの確かめ（checks/conditions.md の R1〜R3）。記述だけ・検定なし。

usage:
  analyze_checks.py <seed> <out_json> <klicke_tar> <klicke_side> <coauthor_work> <holdout> <coauthor_zip> <meta1> <meta2> <o1_work> <ndjson>...
  analyze_checks.py --selftest
出力は集計値だけ（ID・時刻・ファイル名なし）。
"""
import bisect
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("..", "../o1", "../public", "../../20261102-public-data-landscape/scripts",
          "../../20261101-klicke-early-stall-trigger/scripts"):
    sys.path.insert(0, os.path.join(HERE, p))
import types_core as tc  # noqa: E402
import analyze_item2 as t2  # noqa: E402

PRE = 30_000
G_STALL = 30_000
CTRL_LO, CTRL_HI = 2_000, 30_000
MIN_FROM_START = 60_000
AI_PAD = 60_000
N_CTRL = 5
N_RAND = 10
B = 2000
MIN_UNIT_STALLS = 5
MIN_RATIO_N = 20
ORDERS = {"current": ("focus", "move_or_click", "delete2", "silence"),
          "delete_over_move": ("focus", "delete2", "move_or_click", "silence"),
          "focus_last": ("move_or_click", "delete2", "focus", "silence")}


def klass_order(fl, order):
    have = {"focus": fl["focus"], "move_or_click": fl["other_nontext"] or fl["click"], "delete2": fl["delete2"]}
    for c in order:
        if c == "silence" or have[c]:
            return c
    return "silence"


class Seg:
    """1 セッション（O1 は 1 日）。text_cat: [(t, category)] の文字の入力。"""

    def __init__(self, rec, text_cat, onsets, ai=()):
        self.rec = rec
        self.text_cat = sorted(text_cat)
        self.tt = [t for t, _ in self.text_cat]
        self.onsets = [tuple(o[:2]) for o in onsets]
        self.ai = sorted(ai)
        self.t_first = rec.press[0] if rec.press else None

    def next_text_gap(self, i):
        if i + 1 < len(self.tt):
            return self.tt[i + 1] - self.tt[i]
        return (self.rec.press[-1] - self.tt[i]) if self.rec.press else 0

    def window_ok(self, u):
        iv = self.rec.interval_of(u)
        return iv is not None and iv[0] <= u - PRE

    def near_ai(self, a, b):
        return tc.count_in(self.ai, a, b) > 0


def r1_unit(segs, rng, normal):
    """1 単位の停滞と対照。[(stall_flags, [control_flags], [random_flags])] と除外の数。"""
    excl = {"u_ge_s": 0, "near_start": 0, "window_outside": 0, "near_ai": 0, "no_u": 0, "gap_lt_30s": 0,
            "no_control": 0}
    stalls, cands = [], {}
    for k, sg in enumerate(segs):
        for s, t0 in sg.onsets:
            i = bisect.bisect_right(sg.tt, t0) - 1
            if i < 0:
                excl["no_u"] += 1
                continue
            u = sg.tt[i]
            if sg.next_text_gap(i) < G_STALL:
                excl["gap_lt_30s"] += 1
                continue
            if u >= s:
                excl["u_ge_s"] += 1
                continue
            if u - sg.t_first < MIN_FROM_START:
                excl["near_start"] += 1
                continue
            if not sg.window_ok(u):
                excl["window_outside"] += 1
                continue
            if normal and sg.near_ai(u - AI_PAD, u):
                excl["near_ai"] += 1
                continue
            stalls.append((u, k, sg.text_cat[i][1]))
        for t, c in control_candidates(sg, normal):
            cands.setdefault(c, []).append((t, k))
    used = set()
    out = []
    for u, k, c in sorted(stalls, key=lambda x: (x[1], x[0])):
        pool = [x for x in cands.get(c, []) if x not in used]
        if not pool:
            excl["no_control"] += 1
            continue
        pick = rng.sample(pool, min(N_CTRL, len(pool)))
        used.update(pick)
        sg = segs[k]
        sf = sg.rec.flags(u - PRE, u)
        cf = [segs[kk].rec.flags(t - PRE, t) for t, kk in pick]
        rf = []
        for _ in range(N_RAND):
            x = place(rng, sg.rec.intervals, PRE)
            if x is not None:
                rf.append(sg.rec.flags(x - PRE, x))
        out.append((sf, cf, rf))
    return out, excl


def control_candidates(sg, normal):
    """対照の候補 [(u′, category)]（R1）。"""
    spans = [(s - PRE, t0) for s, t0 in sg.onsets]
    out = []
    for i, (t, c) in enumerate(sg.text_cat):
        g = sg.next_text_gap(i)
        if not (CTRL_LO <= g < CTRL_HI):
            continue
        if t - sg.t_first < MIN_FROM_START or not sg.window_ok(t):
            continue
        if any(a <= t <= b for a, b in spans):
            continue
        if normal and sg.near_ai(t - AI_PAD, t + AI_PAD):
            continue
        out.append((t, c))
    return out


def place(rng, intervals, length):
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


def unit_counts(u, order, classes):
    """1 単位の (停滞の類ごとの数, 停滞の数, 対照の類ごとの数, 対照の数, 無作為の類ごとの数, 無作為の数)。"""
    st = [0] * len(classes)
    ct = [0] * len(classes)
    rd = [0] * len(classes)
    ix = {c: i for i, c in enumerate(classes)}
    for sf, cf, rf in u:
        st[ix[klass_order(sf, order)]] += 1
        for f in cf:
            ct[ix[klass_order(f, order)]] += 1
        for f in rf:
            rd[ix[klass_order(f, order)]] += 1
    return st, sum(st), ct, sum(ct), rd, sum(rd)


def pooled_shares(counts, k):
    st = [sum(c[0][i] for c in counts) for i in range(k)]
    ct = [sum(c[2][i] for c in counts) for i in range(k)]
    rd = [sum(c[4][i] for c in counts) for i in range(k)]
    ns, nc, nr = sum(c[1] for c in counts), sum(c[3] for c in counts), sum(c[5] for c in counts)
    return ([x / ns for x in st] if ns else None, [x / nc for x in ct] if nc else None,
            [x / nr for x in rd] if nr else None, ns, nc, nr)


def pct(xs, q):
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def r1_summary(units, classes, rng):
    res = {}
    K = len(classes)
    for name in ("current", "delete_over_move"):
        counts = [unit_counts(u, ORDERS[name], classes) for u in units]
        s, c, r, ns, nc, nr = pooled_shares(counts, K)
        cell = {"stalls": ns, "controls": nc, "random_windows": nr}
        if s is None or c is None:
            res[name] = cell
            continue
        boots = [[] for _ in range(K)]
        n = len(counts)
        for _ in range(B):
            # 単位ごとの数を再標本化して合わせる（停滞とその対照を組のまま）
            idx = [rng.randrange(n) for _ in range(n)]
            bst = [0] * K
            bct = [0] * K
            for j in idx:
                cj = counts[j]
                for i in range(K):
                    bst[i] += cj[0][i]
                    bct[i] += cj[2][i]
            bns, bnc = sum(bst), sum(bct)
            if bns and bnc:
                for i in range(K):
                    boots[i].append(bst[i] / bns - bct[i] / bnc)
        per_unit = [[] for _ in range(K)]
        for cj in counts:
            if cj[1] >= MIN_UNIT_STALLS and cj[3]:
                for i in range(K):
                    per_unit[i].append(cj[0][i] / cj[1] - cj[2][i] / cj[3])
        cell["by_class"] = {cl: {"stall": round(s[i], 4), "control": round(c[i], 4),
                                 "random": round(r[i], 4) if r else None, "diff": round(s[i] - c[i], 4),
                                 "diff_ci95": [round(pct(boots[i], 0.025), 4), round(pct(boots[i], 0.975), 4)]
                                 if boots[i] else None,
                                 "unit_median_diff": tc.quart(per_unit[i])} for i, cl in enumerate(classes)}
        cell["units_with_ge5"] = len(per_unit[0])
        res[name] = cell
    return res


def r2_summary(rows, u_class_len, classes):
    ok = [r for r in tc.typed(rows)]
    th = [r["t0"] - r["s"] for r in ok]
    if len(th) < 4:
        return None
    q = statistics.quantiles(th, n=4, method="inclusive")
    edges = [min(th) - 1, q[0], q[1], q[2], max(th)]

    def stratum(t):
        for i in range(4):
            if t <= edges[i + 1]:
                return i
        return 3
    res = {"theta_quartiles_s": [round(x / 1000, 2) for x in q]}
    for key in ("pre_class", "pre_fixed_class"):
        tab = {}
        for i in range(4):
            rs = [r for r in ok if stratum(r["t0"] - r["s"]) == i]
            cell = {}
            for c in classes:
                cr = [r for r in rs if r.get(key) == c]
                lens = [r["len_ms"] / 1000 for r in cr if r["len_ms"] is not None]
                cell[c] = {"n": len(cr), "len_median_s": round(statistics.median(lens), 2) if lens else None,
                           "long_share": round(sum(1 for r in cr if r["len_class"] == "long") / len(cr), 4) if cr else None}
            sl, op = cell.get("silence", {}), cell.get("move_or_click", {})
            cell["silence_over_move_median"] = (round(sl["len_median_s"] / op["len_median_s"], 3)
                                                if sl.get("n", 0) >= MIN_RATIO_N and op.get("n", 0) >= MIN_RATIO_N
                                                and op.get("len_median_s") else None)
            tab["Q%d" % (i + 1)] = cell
        res[key] = tab
    res["u_window_class_len"] = {c: {"n": len(v), "len_median_s": round(statistics.median(v), 2) if v else None}
                                 for c, v in u_class_len.items()}
    return res


def u_class_lengths(segs, classes):
    out = {c: [] for c in classes}
    for sg in segs:
        for s, t0 in sg.onsets:
            r = sg.rec.stall(s, t0)
            if r.get("no_interval") or r["len_ms"] is None:
                continue
            i = bisect.bisect_right(sg.tt, t0) - 1
            if i < 0 or not sg.window_ok(sg.tt[i]):
                continue
            u = sg.tt[i]
            out[tc.Rec.klass(sg.rec.flags(u - PRE, u))].append(r["len_ms"] / 1000)
    return out


def r3_summary(rows, classes):
    ok = tc.typed(rows)
    n = len(ok)
    res = {"n": n}
    for name, order in ORDERS.items():
        cnt = {c: 0 for c in classes}
        for r in ok:
            cnt[klass_order(r["pre_flags"], order)] += 1
        res[name] = {c: round(v / n, 4) if n else None for c, v in cnt.items()}
    res["flag_share_overlapping"] = {k: round(sum(1 for r in ok if r["pre_flags"][k]) / n, 4) if n else None
                                     for k in ("focus", "other_nontext", "click", "delete2")}
    return res


def dataset(units_segs, rows_units, classes, rng, normal):
    r1u, excl = [], {}
    for segs in units_segs:
        out, ex = r1_unit(segs, rng, normal)
        r1u.append(out)
        for k, v in ex.items():
            excl[k] = excl.get(k, 0) + v
    rows = [r for u in rows_units for r in u]
    ucl = {c: [] for c in classes}
    for segs in units_segs:
        for c, v in u_class_lengths(segs, classes).items():
            ucl[c] += v
    return {"R1": {**r1_summary([u for u in r1u if u], classes, rng), "excluded": excl},
            "R2": r2_summary(rows, ucl, classes), "R3": r3_summary(rows, classes)}


# ---------- 読み込み ----------

def public_segs(sessions):
    import analyze_public as ap
    segs = []
    for s in sessions:
        rec = ap.to_rec(s)
        tcat = [(t, c) for t, c in s.keys if c in t2.TEXT]
        segs.append(Seg(rec, tcat, s.onsets, ai=s.ai))
    return segs


def run(seed, out, ktar, kside, cwork, hold_p, czip, m1, m2, o1work, *files):
    import analyze_landscape as land
    import analyze_public as ap
    import analyze_o1 as ao
    rng = random.Random(int(seed))
    hold = json.load(open(hold_p))
    kw, _ = land.load_klicke(ktar, kside, set(hold["klicke"]))
    if set(json.load(open(kside))) & {"%05d" % i for i in hold["klicke"]}:
        sys.exit("取っておく書き手が KLiCKe の補いに入っている")
    cw = land.load_coauthor(cwork, land.coauthor_hold_idx(czip, [m1, m2], set(hold["coauthor"])))
    kw = [w for w in kw if sum(s.obs_ms() for s in w) >= land.MIN_WRITER_OBS]
    cw = [w for w in cw if sum(s.obs_ms() for s in w) >= land.MIN_WRITER_OBS]
    pc = ("move_or_click", "delete2", "silence")
    res = {"klicke": dataset([public_segs(w) for w in kw],
                             [[r for s in w for r in ap.session_rows(s, False)] for w in kw], pc, rng, False),
           "coauthor_all": dataset([public_segs(w) for w in cw],
                                   [[r for s in w for r in ap.session_rows(s, False)] for w in cw], pc, rng, False),
           "coauthor_normal": dataset([public_segs(w) for w in cw],
                                      [[r for s in w for r in ap.session_rows(s, True)] for w in cw], pc, rng, True)}
    days = []
    for f in files:
        b = os.path.basename(f)[:-len(".ndjson")]
        d = json.load(open(os.path.join(o1work, b + ".json")))
        if d["input_sha256"] != ao.sha256(f):
            sys.exit("中間と入力の SHA-256 が合わない")
        if d["focus"]:
            days.append(ao.Day(d))
    o1_segs = [[Seg(dy.rec, [(t, c) for t, c in dy.d["keys"] if c in t2.TEXT], dy.d["onsets"])] for dy in days]
    res["o1"] = dataset(o1_segs, [dy.rows() for dy in days], tc.CLASSES, rng, False)
    res["o1"]["days"] = len(days)
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: v["R1"]["current"].get("stalls") for k, v in res.items()}))


def selftest():
    # 単位: 文字 1 秒ごと 0..199 秒（区切りは alphabetic）、停滞は 235 秒の t0 の前で 199 秒が最後の文字
    text = [i * 1000 for i in range(200)] + [300_000 + i * 1000 for i in range(100)]
    ctrl_gap = [(400_000 + i * 5000) for i in range(20)]  # 5 秒おきの文字 = 対照の候補
    text_all = sorted(text + ctrl_gap)
    rec = tc.Rec(text_all, [], [190_000], [(0, 600_000)], clicks=[])
    sg = Seg(rec, [(t, "alphabetic") for t in text_all], [(229_000, 235_000)])
    rng = random.Random(1)
    out, ex = r1_unit([sg], rng, False)
    assert len(out) == 1 and len(out[0][1]) == 5 and len(out[0][2]) == N_RAND, (out, ex)
    sf = out[0][0]
    assert sf["other_nontext"] and tc.Rec.klass(sf) == "move_or_click"
    # 停滞の [s − 30 秒, t0] に入る候補は対照にしない
    sg2 = Seg(rec, [(t, "alphabetic") for t in text_all], [(229_000, 235_000), (410_000, 420_000)])
    c1 = [t for t, _ in control_candidates(sg, False)]
    c2 = [t for t, _ in control_candidates(sg2, False)]
    assert any(380_000 <= t <= 420_000 for t in c1) and not any(380_000 <= t <= 420_000 for t in c2)
    assert len(c1) == 19  # 5 秒おきの 19 個（最後は次の文字が無い）
    # 30 秒以上の間は対照にしない（停滞にも足りない間）
    tx = sorted(text_all + [530_000])
    sg5 = Seg(tc.Rec(tx, [], [], [(0, 600_000)]), [(t, "alphabetic") for t in tx], [(229_000, 235_000)])
    assert 495_000 not in [t for t, _ in control_candidates(sg5, False)]
    # 停滞の窓は u の前の 30 秒（u の後の操作は数えない）
    rec6 = tc.Rec(text_all, [], [205_000], [(0, 600_000)])
    sg6 = Seg(rec6, [(t, "alphabetic") for t in text_all], [(229_000, 235_000)])
    out6, _ = r1_unit([sg6], random.Random(1), False)
    assert tc.Rec.klass(out6[0][0]) == "silence"
    # 区切りの種類がそろわなければ対照なし
    sg3 = Seg(rec, [(t, "space" if t >= 400_000 else "alphabetic") for t in text_all], [(229_000, 235_000)])
    out3, ex3 = r1_unit([sg3], random.Random(1), False)
    assert out3 == [] and ex3["no_control"] == 1
    # 優先順
    fl = {"focus": False, "other_nontext": True, "click": False, "delete2": True, "move": False}
    assert klass_order(fl, ORDERS["current"]) == "move_or_click"
    assert klass_order(fl, ORDERS["delete_over_move"]) == "delete2"
    fl2 = dict(fl, focus=True)
    assert klass_order(fl2, ORDERS["focus_last"]) == "move_or_click"
    assert klass_order(dict(fl, other_nontext=False, delete2=False), ORDERS["current"]) == "silence"
    # 現在の順は types_core と同じ
    for f in (fl, fl2, dict(fl, other_nontext=False)):
        assert klass_order(f, ORDERS["current"]) == tc.Rec.klass(f)
    # u ≥ s は外す
    sg4 = Seg(rec, [(t, "alphabetic") for t in text_all], [(150_000, 235_000)])
    _, ex4 = r1_unit([sg4], random.Random(1), False)
    assert ex4["u_ge_s"] == 1
    cnt = unit_counts(out, ORDERS["current"], ("move_or_click", "delete2", "silence"))
    assert cnt[1] == 1 and cnt[3] == 5 and cnt[5] == N_RAND and cnt[0] == [1, 0, 0]
    sh = pooled_shares([cnt, cnt], 3)
    assert sh[0] == [1.0, 0.0, 0.0] and sh[3] == 2 and sh[4] == 10
    print("checks selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(*sys.argv[1:])
