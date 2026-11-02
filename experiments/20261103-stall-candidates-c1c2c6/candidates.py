"""停滞の定義の候補 C1・C2・C6（conditions.md K1〜K7）。記述だけ・検定なし。

usage:
  candidates.py --selftest                          （K7 の陽性対照）
  candidates.py <work_dir> <out_json> <expected_digest> <ndjson>...
入力は停滞の分解の中間だけ（NDJSON は SHA-256 の照合にだけ使う）。出力は集計値だけ（時刻・ファイル名・日付を出さない）。
"""
import bisect
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DECOMP = os.path.join(HERE, "../20261102-stall-decomposition")
sys.path.insert(0, DECOMP)
sys.path.insert(0, os.path.join(DECOMP, "o1"))
sys.path.insert(0, os.path.join(HERE, "../20261101-klicke-early-stall-trigger/scripts"))
import types_core as tc  # noqa: E402  位置・まとまり・四分位
import analyze_o1 as ao  # noqa: E402  unit_sd
import analyze_item2 as t2  # noqa: E402  TEXT・DELETE の集合

W = 30_000            # p1-episode 1.2.0 w_ms
Q = 0.99              # q
WARM = 100            # warmup_count
GQ = 0.5              # C6 の g* の分位（K5）
PRE = 30_000          # 重なりの手前（[s − 30 秒, 原点]）
NAMES = ("C0", "C1", "C2", "C6")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- 因果に累積する分位（stall_onset.rs の ThetaAccumulator と同じ規則） ----------

class Acc:
    """(時刻, 値) を時刻の昇順に持ち、at(t) で時刻 t 以下の値の nearest-rank 分位を返す。t は単調非減少で呼ぶ。"""

    def __init__(self, pooled, q, warm):
        self.pooled = sorted(pooled)
        self.q, self.warm = q, warm
        self.vals = sorted({v for _, v in self.pooled})
        self.tree = [0] * (len(self.vals) + 1)
        self.pos = self.n = 0
        self.last_t = None

    def _add(self, v):
        i = bisect.bisect_left(self.vals, v) + 1
        while i < len(self.tree):
            self.tree[i] += 1
            i += i & -i
        self.n += 1

    def _kth(self, k):
        pos, rem = 0, k
        pw = 1 << max(0, len(self.vals).bit_length() - 1)
        while pw:
            nx = pos + pw
            if nx < len(self.tree) and self.tree[nx] < rem:
                pos, rem = nx, rem - self.tree[nx]
            pw >>= 1
        return self.vals[pos]

    def at(self, t):
        if self.last_t is not None and t < self.last_t:
            raise ValueError("Acc は時刻の昇順で引く")
        self.last_t = t
        while self.pos < len(self.pooled) and self.pooled[self.pos][0] <= t:
            self._add(self.pooled[self.pos][1])
            self.pos += 1
        if self.n == 0 or self.n < self.warm:
            return None
        rank = min(max(math.ceil(self.q * self.n), 1), self.n)
        return self._kth(rank), self.n


def gap_pool(ts, intervals):
    """同じ観測区間に入る隣り合う 2 点の (2 点目の時刻, 間隔)。全区間からプール（stall_onset.rs の pooled_theta_gaps）。"""
    out = []
    for a, b in intervals:
        x = ts[bisect.bisect_left(ts, a):bisect.bisect_right(ts, b)]
        out += [(y, y - p) for p, y in zip(x, x[1:])]
    return out


def count_win(ts, t):
    """(t − W, t] の数。"""
    return bisect.bisect_right(ts, t) - bisect.bisect_right(ts, t - W)


# ---------- 共通の検出器（K2） ----------

def detect(intervals, flow, cond, theta=None):
    """flow: 評価時刻を作る時刻の昇順の列。cond(t) は t の昇順で呼ばれる。theta: Acc か None（持続を課さない）。
    戻り値: (onsets [(s, 原点, θ or None)], warmup で立てなかった立ち上がりの数)"""
    inst_all = sorted(set(flow) | {t + W for t in flow})
    onsets, no_theta = [], 0
    for a, b in intervals:
        start = a + W
        if start > b:
            continue
        lo, hi = bisect.bisect_left(inst_all, start), bisect.bisect_right(inst_all, b)
        inst = sorted(set([start] + inst_all[lo:hi]))
        ca = [cond(t) for t in inst]
        prev = False
        for i, t in enumerate(inst):
            if ca[i] and not prev:
                if theta is None:
                    onsets.append((t, t, None))
                else:
                    th = theta.at(t)
                    if th is None:
                        no_theta += 1
                    elif t + th[0] <= b:
                        t0 = t + th[0]
                        j = i + 1
                        ok = True
                        while j < len(inst) and inst[j] <= t0:
                            if not ca[j]:
                                ok = False
                                break
                            j += 1
                        if ok:
                            onsets.append((t, t0, th[0]))
            prev = ca[i]
    return onsets, no_theta


def detect_runs(intervals, flow, cond):
    """持続を課さない検出（C6・判断 4）。立ち上がりを 1 件とし、次は条件が W 続けて偽になってから立つ。
    戻り値: [(s, e)]（e = 件を閉じた偽の始まり。区間の終わりまで真なら b）。区間をまたがない。"""
    inst_all = sorted(set(flow) | {t + W for t in flow})
    runs = []
    for a, b in intervals:
        start = a + W
        if start > b:
            continue
        lo, hi = bisect.bisect_left(inst_all, start), bisect.bisect_right(inst_all, b)
        inst = sorted(set([start] + inst_all[lo:hi]))
        prev, cur, f = False, None, None
        for t in inst:
            c = cond(t)
            if c and not prev:
                if cur is not None and t - f >= W:
                    runs.append((cur, f))
                    cur = None
                if cur is None:
                    cur = t
            elif not c and prev:
                f = t
            prev = c
        if cur is not None:
            runs.append((cur, b if prev else f))
    return runs


# ---------- 1 日 ----------

class Day:
    def __init__(self, d):
        self.intervals = sorted((iv["a_ms"], iv["b_ms"]) for iv in d["observed_intervals"])
        ks = sorted(d["keys"], key=lambda k: k[0])
        self.press = [t for t, _ in ks]
        self.text = [t for t, c in ks if c in t2.TEXT]
        self.dele = [t for t, c in ks if c in t2.DELETE]
        self.td = sorted(self.text + self.dele)
        self.act = sorted(set(self.press) | {p[0] for p in d["pointer"]} | set(d["focus"]))
        self.replay_onsets = [tuple(x) for x in d["onsets"]]
        self.rec = tc.Rec(self.text, self.dele, [t for t, c in ks if c not in t2.TEXT and c not in t2.DELETE],
                          self.intervals)
        self.obs = sum(b - a for a, b in self.intervals)

    def net(self, t):
        return count_win(self.text, t) - count_win(self.dele, t)

    def c0(self):
        acc = Acc(gap_pool(self.press, self.intervals), Q, WARM)
        return detect(self.intervals, self.press, lambda t: self.net(t) < 1, acc)

    def c1_cond(self, t):
        return count_win(self.act, t) == 0

    def c1(self):
        acc = Acc(gap_pool(self.act, self.intervals), Q, WARM)
        return detect(self.intervals, self.act, self.c1_cond, acc)

    def g_samples(self):
        out = []
        for a, b in self.intervals:
            x = self.td[bisect.bisect_left(self.td, a):bisect.bisect_right(self.td, b)]
            for p in x:
                g = bisect.bisect_right(x, p) - bisect.bisect_right(x, max(p - W, a - 1))
                out.append((p, g))
        return out

    def c6(self):
        acc = Acc(self.g_samples(), GQ, WARM)
        gstar = []

        def cond(t):
            g = acc.at(t)
            if g is None:
                return False
            ok = self.net(t) < 1 and count_win(self.td, t) >= g[0]
            if ok:
                gstar.append((t, g[0]))
            return ok
        runs = detect_runs(self.intervals, self.td, cond)
        gs = dict(gstar)
        self.c6_span = [e - s for s, e in runs]
        return [(s, s, gs[s]) for s, _ in runs]

    def is_c2(self, s, t0):
        """[s, t0] のすべての時刻で C1 の条件 A が偽か（K3 の注: {s} ∪ {e + W} だけで評価すれば足りる）。"""
        if self.c1_cond(s):
            return False
        lo = bisect.bisect_left(self.act, s - W)
        hi = bisect.bisect_right(self.act, t0 - W)
        return all(not self.c1_cond(e + W) for e in self.act[lo:hi] if s <= e + W <= t0)

    def interval_of(self, t):
        return self.rec.interval_of(t)

    def resume(self, ts, t):
        iv = self.interval_of(t)
        j = bisect.bisect_right(ts, t)
        return ts[j] if iv is not None and j < len(ts) and ts[j] <= iv[1] else None


# ---------- 集計 ----------

def len_class(d):
    return "censored" if d is None else "short" if d <= tc.SHORT_MS else "mid" if d <= tc.LONG_MS else "long"


def spans_hit(spans, a, b):
    """互いに交わらず昇順の spans [(s, e)] に、[a, b] と交わる（閉区間）ものがあるか。"""
    i = bisect.bisect_right([s for s, _ in spans], b) - 1
    return i >= 0 and spans[i][1] >= a


def day_rows(dy):
    c0, nw0 = dy.c0()
    c1, nw1 = dy.c1()
    c6 = dy.c6()
    c2 = [o for o in c0 if dy.is_c2(o[0], o[1])]
    cand = {"C0": c0, "C1": c1, "C2": c2, "C6": c6}
    s6 = [s for s, _, _ in c6]
    sp1 = [(s, e) for s, e, _ in c1]
    rows = {k: [] for k in NAMES}
    for k, on in cand.items():
        for i, (s, o, th) in enumerate(on):
            r = {"s": s, "o": o, "th": th, "pos": dy.rec.position(o)[0]}
            if k == "C6":
                r["span"] = dy.c6_span[i]
            if k != "C6":
                rs = dy.resume(dy.act if k == "C1" else dy.text, o)
                r["len"] = None if rs is None else rs - o
                r["len_class"] = len_class(r["len"])
                r["has_c6"] = tc.count_in(s6, s - PRE, o) > 0
            if k in ("C0", "C2"):
                r["hit_c1"] = spans_hit(sp1, s, o)
            rows[k].append(r)
    for r in rows["C0"]:
        r["c2"] = dy.is_c2(r["s"], r["o"])
    sp0 = [(r["s"], r["o"]) for r in rows["C0"]]
    # 事後（conditions.md に無い・レビュー M4 の後）: C0 の停滞の [s, 再開]（打ち切りは区間の終わり）の中に C1 の [s1, t1] が入るか
    full0 = []
    for r in rows["C0"]:
        iv = dy.interval_of(r["o"])
        full0.append((r["s"], r["o"] + r["len"] if r["len"] is not None else iv[1]))
    for r in rows["C1"]:
        r["hit_c0"] = spans_hit(sp0, r["s"], r["o"])
        r["in_c0_stall"] = any(a <= r["s"] and r["o"] <= b for a, b in full0)
    for r in rows["C6"]:
        for k in ("C0", "C1", "C2"):
            r["in_" + k] = any(x["s"] - PRE <= r["s"] <= x["o"] for x in rows[k])
    return rows, {"C0": nw0, "C1": nw1}


def check_structure(dy, rows):
    """構造から出る関係（K3 の注）。破れたら止める。"""
    if any(r["hit_c1"] for r in rows["C2"]):
        sys.exit("C2 と C1 の区間が交わった（K3 の構造が破れた）")
    c0 = {(r["s"], r["o"]) for r in rows["C0"]}
    if not all((r["s"], r["o"]) in c0 for r in rows["C2"]):
        sys.exit("C2 が C0 の部分集合でない")
    for r in rows["C6"]:
        if dy.net(r["s"]) >= 1:
            sys.exit("C6 の立ち上がりで C0 の条件 A が偽")


def share(num, den):
    return tc.pooled(num, den)


def summarize(days, all_rows, no_warm):
    obs_h = sum(dy.obs for dy in days) / tc.H
    res = {"days": len(days), "obs_h": round(obs_h, 3)}
    o1, o2, o3, o5 = {}, {}, {}, {}
    for k in NAMES:
        per_day = [r[k] for r in all_rows]
        n = sum(len(x) for x in per_day)
        o1[k] = {"n": n, "pooled_per_h": round(n / obs_h, 4),
                 "day_per_h": tc.quart([len(x) / (dy.obs / tc.H) for x, dy in zip(per_day, days) if dy.obs > 0]),
                 "day_unit_sd": ao.unit_sd([(dy.obs, len(x)) for x, dy in zip(per_day, days)])}
        if k != "C2":
            o2[k] = {"unit": "presses_per_30s" if k == "C6" else "ms",
                     "threshold_at_fire": tc.quart([r["th"] for x in per_day for r in x]),
                     "day_median_threshold": tc.quart([tc.quart([r["th"] for r in x])["median"]
                                                       for x in per_day if x])}
            if k in no_warm:
                o2[k]["rises_without_threshold_warmup"] = no_warm[k]
        if k != "C6":
            rs = [r for x in per_day for r in x]
            o3[k] = {c: share(sum(1 for r in rs if r["len_class"] == c), len(rs)) for c in tc.LEN}
            o3[k]["len_s_resumed"] = tc.quart([r["len"] / 1000 for r in rs if r["len"] is not None])
        else:
            o3[k] = {"span_s": tc.quart([r["span"] / 1000 for x in per_day for r in x])}
        pos = {}
        for p in tc.POS:
            num = den = 0
            for x, dy in zip(per_day, days):
                num += sum(1 for r in x if r["pos"] == p)
                st = dy.rec.block_starts
                end = max(b for _, b in dy.intervals)
                for i, a in enumerate(st):
                    nxt = st[i + 1] if i + 1 < len(st) else end
                    lo, hi = (a, min(a + tc.EARLY_MS, nxt)) if p == "early" else (a + tc.EARLY_MS, nxt)
                    if hi > lo:
                        den += sum(max(0, min(hi, y) - max(lo, xx)) for xx, y in dy.intervals)
            pos[p] = {"n": num, "obs_h": round(den / tc.H, 3), "pooled_per_h": round(num / (den / tc.H), 4) if den else None}
        pos["no_position"] = sum(1 for x in per_day for r in x if r["pos"] is None)
        o5[k] = pos
    flat = {k: [r for x in all_rows for r in x[k]] for k in NAMES}
    c0, c1, c6 = flat["C0"], flat["C1"], flat["C6"]
    o4 = {"C0_hit_C1": share(sum(1 for r in c0 if r["hit_c1"]), len(c0)),
          "C1_hit_C0": share(sum(1 for r in c1 if r["hit_c0"]), len(c1)),
          "C0_is_C2": share(sum(1 for r in c0 if r["c2"]), len(c0)),
          "C0_neither_C2_nor_hit_C1": sum(1 for r in c0 if not r["c2"] and not r["hit_c1"]),
          "C6_in_pre_or_span": {k: share(sum(1 for r in c6 if r["in_" + k]), len(c6)) for k in ("C0", "C1", "C2")},
          "has_C6_in_pre_or_span": {k: share(sum(1 for r in flat[k] if r["has_c6"]), len(flat[k]))
                                    for k in ("C0", "C1", "C2")}}
    # K6: 日ごとの値の中央値・四分位（O3・O4・O5）
    def dq(f):
        return tc.quart([v for x, dy in zip(all_rows, days) if (v := f(x, dy)) is not None])

    def ratio(rs, key):
        return sum(1 for r in rs if r[key]) / len(rs) if rs else None
    for k in ("C0", "C1", "C2"):
        o3[k]["day_median_len_s"] = dq(lambda x, dy, k=k: tc.quart([r["len"] / 1000 for r in x[k] if r["len"] is not None])["median"]
                                      if any(r["len"] is not None for r in x[k]) else None)
        o3[k]["day_share_long_or_censored"] = dq(
            lambda x, dy, k=k: sum(1 for r in x[k] if r["len_class"] in ("long", "censored")) / len(x[k]) if x[k] else None)
    o4["posthoc_C1_inside_C0_stall_to_resume"] = share(sum(1 for r in c1 if r["in_c0_stall"]), len(c1))
    o4["posthoc_C1_not_hit_C0_but_inside_C0_stall"] = sum(1 for r in c1 if r["in_c0_stall"] and not r["hit_c0"])
    o4["day"] = {"C0_is_C2": dq(lambda x, dy: ratio(x["C0"], "c2")),
                 "C0_hit_C1": dq(lambda x, dy: ratio(x["C0"], "hit_c1")),
                 "C1_hit_C0": dq(lambda x, dy: ratio(x["C1"], "hit_c0"))}
    for k in NAMES:
        o5[k]["day_note"] = "位置ごとの日の率は出さない（序盤の観測が日に 1 時間に満たない）"
    res.update({"O1_counts_rates": o1, "O2_thresholds": o2, "O3_lengths": o3, "O4_overlap": o4, "O5_position": o5})
    return res


def run(work, out, expected_digest, *files):
    cat = hashlib.sha256()
    shas = [sha256(f) for f in files]
    for h in shas:
        cat.update(h.encode())
    if cat.hexdigest() != expected_digest:
        sys.exit("入力の digest が停滞の分解の来歴と合わない")
    days, excl = [], 0
    for f, h in zip(files, shas):
        d = json.load(open(os.path.join(work, os.path.basename(f)[:-len(".ndjson")] + ".json")))
        if d["input_sha256"] != h:
            sys.exit("中間と入力の SHA-256 が合わない")
        if not d["focus"]:
            excl += 1
            continue
        days.append(Day(d))
    if len(days) != 14 or excl != 4:
        sys.exit(f"使う日が 14 本・外す日が 4 本でない（{len(days)}・{excl}）")
    match = {"files": 0, "onsets_replay": 0, "onsets_port": 0, "mismatch_files": 0}
    for dy in days:  # K2 の自己検査を C1・C6 の計算より前に（レビュー L4）
        port = [(x[0], x[1]) for x in dy.c0()[0]]
        match["files"] += 1
        match["onsets_replay"] += len(dy.replay_onsets)
        match["onsets_port"] += len(port)
        if port != dy.replay_onsets:
            match["mismatch_files"] += 1
    if match["mismatch_files"]:
        sys.exit("K2 の自己検査: 検出器の C0 が gse-replay の onsets と一致しない " + json.dumps(match))
    all_rows, no_warm = [], {"C0": 0, "C1": 0}
    for dy in days:
        rows, nw = day_rows(dy)
        check_structure(dy, rows)
        all_rows.append(rows)
        for k in nw:
            no_warm[k] += nw[k]
    res = summarize(days, all_rows, no_warm)
    res["O6_selfcheck"] = match
    res["files"] = {"given": len(files), "excluded_no_focus": excl, "used": len(days)}
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(match), file=sys.stderr)


# ---------- K7 陽性対照 ----------

def synth(keys, pointer=(), focus=(), intervals=None, onsets=()):
    """区間の既定は最初の押下から最後の押下まで（最後の押下の後に止まりを作らない）。"""
    if intervals is None:
        intervals = ((0, max(k[0] for k in keys)),)
    return {"keys": sorted(keys), "pointer": [[t, 1, 0, 0] for t in pointer], "focus": list(focus),
            "observed_intervals": [{"a_ms": a, "b_ms": b} for a, b in intervals], "onsets": list(onsets)}


def selftest():
    # 共通: 1 秒ごとに文字を 200 回（θ の標本 199 個・すべて 1,000 ms → p99 = 1,000）
    base = [[i * 1000, "alphabetic"] for i in range(200)]
    last = 199_000
    # 1 全チャネルが止まる → C0（s = last + W, t0 = s + 1000）と C1（同じ）・C2 なし
    d = synth(base + [[600_000, "alphabetic"]])
    dy = Day(d)
    c0, _ = dy.c0()
    c1, _ = dy.c1()
    assert c0[0][:2] == (last + W, last + W + 1000), c0  # 6（手で出した値）
    assert c1[0][:2] == (last + W, last + W + 1000), c1
    rows, _ = day_rows(dy)
    assert rows["C2"] == [] and rows["C0"][0]["hit_c1"] and not rows["C0"][0]["c2"]
    check_structure(dy, rows)
    # 2 文字だけ止まり、ポインタが 5 秒ごと → C0 が立ち C2。C1 は立たない
    ptr = list(range(last + 5000, 600_000, 5000))
    d = synth(base + [[600_000, "alphabetic"]], pointer=ptr)
    dy = Day(d)
    rows, _ = day_rows(dy)
    assert len(rows["C0"]) == 1 and len(rows["C2"]) == 1 and rows["C1"] == [], rows
    check_structure(dy, rows)
    # 2b 途中でポインタが W 以上途切れる → C2 にならない
    ptr2 = [t for t in ptr if not (300_000 <= t <= 340_000)]
    dy = Day(synth(base + [[600_000, "alphabetic"]], pointer=ptr2))
    rows, _ = day_rows(dy)
    # C0 の t0 = last+W+θ0。θ0 は press の間隔の p99（ポインタは C0 の標本に入らない）= 1000。途切れは t0 より後なので C2 のまま
    assert len(rows["C2"]) == 1
    dy = Day(synth(base + [[600_000, "alphabetic"]], pointer=[t for t in ptr if t > last + 40_000]))
    rows, _ = day_rows(dy)
    assert len(rows["C0"]) == 1 and rows["C2"] == [], rows  # [s, t0] の中で活動が W 途切れた
    # 3 打っては消す: 普段 30 秒に 30 打。止めた後、30 秒に挿入 10・削除 10（g = 20 < 30）→ 立たない。
    #   20 + 20（g = 40 ≥ 30）→ 立つ
    def churn(n_each):
        ks = list(base)
        t = last + 60_000
        for _ in range(n_each):
            ks.append([t, "alphabetic"])
            ks.append([t + 500, "backspace"])
            t += 1000
        return Day(synth(ks + [[900_000, "alphabetic"]]))
    assert churn(10).c6() == []
    c6 = churn(20).c6()
    assert len(c6) == 1 and c6[0][2] == 30, c6
    dyc = churn(20)
    rows, _ = day_rows(dyc)
    check_structure(dyc, rows)
    assert len(rows["C6"]) == 1
    # 3b 空回りが 2 回: 間が W 以上偽なら 2 件・W 未満なら 1 件（判断 4 の不応期）
    def churn2(short_false):
        ks = list(base)
        t = last + 60_000
        for blk in range(2):
            for _ in range(20):
                ks.append([t, "alphabetic"])
                ks.append([t + 500, "backspace"])
                t += 1000
            if short_false:  # 1 文字入れて 10 秒後に消す → 偽は約 10 秒（< W）
                ks += [[t, "alphabetic"], [t + 10_000, "backspace"]]
                t += 10_500
            else:  # 5 文字残す → 窓から抜けるまで偽（≥ W）
                ks += [[t + j * 1000, "alphabetic"] for j in range(5)]
                t += 60_000
        return Day(synth(ks + [[t + 300_000, "alphabetic"]]))
    assert len(churn2(False).c6()) == 2, churn2(False).c6()
    assert len(churn2(True).c6()) == 1, churn2(True).c6()
    # 4 標本が 100 未満 → C1・C6 は立たない
    few = [[i * 1000, "alphabetic"] for i in range(50)]
    dy = Day(synth(few + [[600_000, "alphabetic"]]))
    assert dy.c1()[0] == [] and dy.c1()[1] >= 1 and dy.c6() == []
    # 5 区間の切れ目: 区間 2 の頭の W は評価しない。区間 2 が W に届かなければ何も立たない
    ks = base + [[400_000 + i * 1000, "alphabetic"] for i in range(5)]
    dy = Day(synth(ks, intervals=((0, 205_000), (400_000, 420_000))))
    assert dy.c0()[0] == [] and dy.c1()[0] == []
    # 区間 1 の中で W + θ に届けば立つ
    dy = Day(synth(ks, intervals=((0, last + W + 1000), (400_000, 420_000))))
    assert dy.c0()[0][0][:2] == (last + W, last + W + 1000)
    # 5b 区間の頭（s = a + W）の C0: 頭の W に活動が無ければ C2 でない・ポインタがあれば C2
    ks = base + [[340_000 + i * 1000, "alphabetic"] for i in range(5)]
    iv2 = ((0, last), (300_000, 344_000))
    dy = Day(synth(ks, intervals=iv2))
    rows, _ = day_rows(dy)
    assert [(r["s"], r["o"]) for r in rows["C0"]] == [(330_000, 331_000)] and rows["C2"] == [], rows
    dy = Day(synth(ks, pointer=range(302_000, 340_000, 5000), intervals=iv2))
    rows, _ = day_rows(dy)
    assert len(rows["C2"]) == 1 and rows["C1"] == [], rows
    # 7 θ0 が長い合成（温まり前に 60 秒の間隔を 3 つ。標本 203 個の rank = ⌈0.99·203⌉ = 201 → 上から 3 番目 = 60 秒）で、
    #   [s, t0] の途中の途切れを見る（レビュー H1）
    lk = [[i * 60_000, "alphabetic"] for i in range(4)]
    lk += [[181_000 + i * 1000, "alphabetic"] for i in range(200)]
    ll = 380_000
    s7, t7 = ll + W, ll + W + 60_000
    end7 = [[t7 + 5000, "alphabetic"]]
    # 7a s から 20 秒はポインタ（5 秒ごと）、その後 t0 まで途切れる（W 以上）→ C2 でない
    p7a = list(range(ll + 5000, s7 + 20_001, 5000))
    dy = Day(synth(lk + end7, pointer=p7a))
    rows, _ = day_rows(dy)
    assert [(r["s"], r["o"]) for r in rows["C0"]] == [(s7, t7)] and rows["C2"] == [], rows
    check_structure(dy, rows)
    # 7b 最後のポインタがちょうど t0 − W（t0 で C1 の条件 A が真になる・閉区間の端）→ C2 でない
    p7b = list(range(ll + 5000, t7 - W, 5000)) + [t7 - W]
    dy = Day(synth(lk + end7, pointer=p7b))
    rows, _ = day_rows(dy)
    assert len(rows["C0"]) == 1 and rows["C2"] == [], rows
    # 7c 同じでポインタが t0 − W + 1 まで続く → C2
    dy = Day(synth(lk + end7, pointer=p7b[:-1] + [t7 - W + 1]))
    rows, _ = day_rows(dy)
    assert len(rows["C2"]) == 1, rows
    # 8 C1 の流れ（レビュー M1）: 押下の間にポインタ（+500）→ θ1 = 500（θ0 = 1000 と違う）・s1 は最後のポインタ + W
    pm = [i * 1000 + 500 for i in range(200)]
    dy = Day(synth(base + [[600_000, "alphabetic"]], pointer=pm))
    c1, _ = dy.c1()
    assert c1[0][:3] == (last + 500 + W, last + 500 + W + 500, 500), c1
    assert dy.c0()[0][0][:2] == (last + W, last + W + 1000)
    # 8b フォーカスの遷移だけが 5 秒ごとに続く → C1 は立たず C2
    dy = Day(synth(base + [[600_000, "alphabetic"]], focus=range(last + 5000, 600_000, 5000)))
    rows, _ = day_rows(dy)
    assert rows["C1"] == [] and len(rows["C2"]) == 1, rows
    # 9 g がちょうど g*（15 往復 = 30 押下）→ 立つ（g ≥ g*・レビュー L1）
    assert len(churn(15).c6()) == 1 and churn(14).c6() == []
    # 10 重なりと幅（レビュー M2）: 空回りの直後に C0 が立ち、C6 はその手前 30 秒に入る
    dyc = churn(20)
    rows, _ = day_rows(dyc)
    c0_after = [r for r in rows["C0"] if r["s"] > last + 60_000]
    assert len(c0_after) == 1 and c0_after[0]["has_c6"] is True, rows["C0"]
    assert rows["C6"][0]["in_C0"] is True and rows["C6"][0]["in_C1"] is False, rows["C6"]
    assert sum(r["has_c6"] for r in rows["C0"]) == 1
    # 空回りの押下は 259,000 から 500 ms ごとに 40 個。30 個目（273,500・削除の直後で正味 0）で立ち、
    # 11 個目（264,000）が窓から抜ける 294,000 で g = 29 < g* = 30 になって閉じる → 幅 20,500
    assert rows["C6"][0]["s"] == 273_500 and rows["C6"][0]["span"] == 20_500, rows["C6"]
    # 11 事後の量: 文字が止まってもポインタが 60 秒動き、その後全部止まる → C0 は先に立ち、C1 は C0 の t0 の後
    #    （[s, t0] とは交わらないが、C0 の停滞の [s, 再開] の中に入る）
    dy = Day(synth(base + [[600_000, "alphabetic"]], pointer=range(last + 5000, last + 60_001, 5000)))
    rows, _ = day_rows(dy)
    assert len(rows["C0"]) == 1 and len(rows["C1"]) == 1, rows
    assert rows["C1"][0]["hit_c0"] is False and rows["C1"][0]["in_c0_stall"] is True, rows["C1"]
    # 不応期: 条件 A が続く間は 2 件目が立たない
    dy = Day(synth(base + [[900_000, "alphabetic"]]))
    assert len(dy.c0()[0]) == 1 and len(dy.c1()[0]) == 1
    # Acc は時刻の昇順でしか引けない
    a = Acc([(1, 5)], 0.5, 1)
    a.at(2)
    try:
        a.at(1)
        raise AssertionError("Acc の逆順が通った")
    except ValueError:
        pass
    # spans_hit
    assert spans_hit([(0, 10), (20, 30)], 10, 15) and not spans_hit([(0, 10), (20, 30)], 11, 19)
    print("candidates selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(*sys.argv[1:])
