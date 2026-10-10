"""Self-tests of the EH1 round 5 instruments (round 5 design 3.7; round 4 design 3.7; round 3 design 3.7; round 2
design 3.6 and 3.8; round 1 design 3.6, 3.8 and 7).

Usage: selftest.py <config.json> <work dir with at least the smoke sessions>
Exit 0 when every hard test passes. Round 4 design 3.7 ("when a test fails"): the unit tests are hard (a failure
stops the run); the statistical tests (lambda = 0 of PCsize and PCcal, the E1-3 mutations) and the walk test of
raw PCsize are soft: a failure is printed as SOFT-FAIL and written to design section 8, the run goes on, and no
verdict depends on it.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

import checks
import portrait as pt

FAILED: list[str] = []
SOFT_FAILED: list[str] = []


def check(name: str, cond: bool, detail: str = "", soft: bool = False) -> None:
    tag = "PASS" if cond else ("SOFT-FAIL" if soft else "FAIL")
    print(f"{tag}  {name}{('  ' + detail) if detail else ''}")
    if not cond:
        (SOFT_FAILED if soft else FAILED).append(name)


def l300_gains(conf: pt.Config, sids: list, lab: dict, cfg: dict) -> dict:
    """The four L300 gains (fset/kind) of one configuration on the given sessions (seed 1)."""
    shape = {conf.name: np.vstack([pt.run(checks._session(sid), conf, cfg, 1, True, False)["windows"] for sid in sids])}
    xb = checks.attacker_sets(lab, shape, cfg)[conf.name]
    ones = np.ones(len(lab["Y"]))
    gains = {}
    for kind in ("hgb", "lr"):
        a0 = checks.weighted_auc(checks.oof_predict(lab["XA"], lab["Y"], lab["G"], kind, 1, cfg["e13"]["folds"]),
                                 lab["Y"], ones)
        for fs in ("full", "small"):
            pb = checks.oof_predict(xb[fs], lab["Y"], lab["G"], kind, 1, cfg["e13"]["folds"])
            gains[f"{fs}/{kind}"] = checks.weighted_auc(pb, lab["Y"], ones) - a0
    return gains


def fake_session(presses: list[float], dur: int, sleep: tuple[int, int] | None = None) -> pt.Session:
    seg = np.zeros(dur, dtype=np.int8)
    if sleep:
        seg[sleep[0] : sleep[1]] = pt.SLEEP_CODE
    p = np.asarray(sorted(presses), dtype=float)
    act = np.zeros(dur, dtype=bool)
    act[p.astype(int)] = True
    feat = {c: np.zeros(dur) for c in ("f1", "f3", "f4", "f5", "f6", "p_stuck", "keys")}
    return pt.Session("fake", "P", dur, p, act, seg, feat, 12345, seg == pt.SLEEP_CODE)


def main() -> int:
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    work = Path(sys.argv[2])

    # --- E1-1: the material boundary
    s = fake_session([1.0, 2.0], 100)
    mat = pt.material_slice(s, 0, 50)
    check("E1-1 material columns", set(mat) == set(pt.ALLOWED_MATERIAL), str(sorted(mat)))
    check("E1-1 PC2 adds only p_stuck", set(pt.material_slice(s, 0, 50, True)) == set(pt.ALLOWED_MATERIAL) | {"p_stuck"})
    check("E1-1 an oracle value adds only the oracle",
          set(pt.material_slice(s, 0, 50, False, 0.5)) == set(pt.ALLOWED_MATERIAL) | {"oracle"})
    so = fake_session([1.0], 600)
    so.seg[100:250] = 1
    ups_o = np.array([300, 450])
    orc300 = pt.oracle_values(so, ups_o, pt.Config("ordinal", "none", pt.Sched(), pc="ORC300"), 1)
    check("ORC300: stall share of seconds [u - 300, u)", np.allclose(orc300, [150 / 300, 100 / 300]), str(orc300))
    gap = pt.oracle_values(so, ups_o, pt.Config("ordinal", "none", pt.Sched(), pc="ORCgap"), 1)
    check("ORCgap: stall share of seconds [u_prev, u) (from 0 at the first update)",
          np.allclose(gap, [150 / 300, 0 / 150]), str(gap))
    try:
        pt.Generator("raw", "none", cfg, 1).update(dict(mat, oracle=np.zeros(1)), 50)
        check("E1-1 a plain generator refuses the oracle", False)
    except ValueError:
        check("E1-1 a plain generator refuses the oracle", True)
    try:
        pt.Generator("ordinal", "none", cfg, 1, pc="PC2").update(dict(mat, oracle=np.zeros(1)), 50)
        check("E1-1 PC2 refuses the oracle", False)
    except ValueError:
        check("E1-1 PC2 refuses the oracle", True)
    bad = dict(mat, p_stuck=np.zeros(50))
    for mapping in cfg["mappings"]:
        gen = pt.Generator(mapping, "none", cfg, 1)
        try:
            gen.update(bad, 50)
            check(f"E1-1 {mapping} generator refuses p_stuck", False)
        except ValueError:
            check(f"E1-1 {mapping} generator refuses p_stuck", True)

    # --- lattice (design 1.3)
    d = cfg["generator"]["lattice"]["delta"]
    check("lattice first class by the bounds only", [pt.lattice_class(v, None, d) for v in (0.0, 0.34, 0.7)] == [0, 1, 2])
    check("lattice hysteresis holds near a bound", pt.lattice_class(0.36, 0, d) == 0 and pt.lattice_class(0.39, 0, d) == 1
          and pt.lattice_class(0.30, 1, d) == 1 and pt.lattice_class(0.27, 1, d) == 0)
    check("lattice can jump two classes", pt.lattice_class(0.95, 0, d) == 2 and pt.lattice_class(0.05, 2, d) == 0)
    cells = pt.lattice_cells(cfg["canvas"]["w"], cfg["canvas"]["h"], cfg["generator"]["lattice"]["cell_px"])
    check("lattice cells: 16 x 9, the first is a centre cell", len(cells) == 144 and abs(cells[0][0] - 160) <= 10
          and abs(cells[0][1] - 90) <= 10, str(cells[:2]))
    ground = np.asarray(cfg["canvas"]["ground"], dtype=np.float32)
    cents = []
    for lvl in (0.0, 1.0):  # the cell depends on the ordinal only, not on the material
        g2 = pt.Generator("lattice", "none", cfg, 7)
        n = cfg["generator"]["neutral_active_s"]
        m2 = {c: np.full(n, lvl * (cfg["generator"]["raw_ranges"].get(c, [0, 1])[1])) for c in ("f1", "f3", "f4", "f5", "f6")}
        m2["active"] = np.ones(n, dtype=bool)
        img = g2.update(m2, n)
        dev = pt.deviation(img, ground)
        ys, xs = np.nonzero(dev > 0.05)
        cents.append((xs.mean(), ys.mean()))
    check("lattice: the first drawn update sits in the first cell whatever the material",
          all(abs(c[0] - cells[0][0]) < 4 and abs(c[1] - cells[0][1]) < 4 for c in cents), str(cents))
    # later updates, with an update without presses in between: the cell follows the drawn-update ordinal
    seqs = []
    for lvl in (0.0, 1.0):
        g2 = pt.Generator("lattice", "none", cfg, 7)
        mk = {c: np.full(n, lvl * (cfg["generator"]["raw_ranges"].get(c, [0, 1])[1])) for c in ("f1", "f3", "f4", "f5", "f6")}
        cs = []
        for k, act in enumerate((True, True, False, True)):
            mk["active"] = np.full(n, act)
            prev = g2.base.copy()
            g2.update(dict(mk), n * (k + 1))
            dv = np.abs(g2.base - prev).max(axis=2)
            ys, xs = np.nonzero(dv > 0.05)
            cs.append((round(float(xs.mean())), round(float(ys.mean()))) if len(xs) else None)
        seqs.append(cs)
    want = [cells[0], cells[1], None, cells[2]]
    ok = all(all((w is None and c is None) or (w is not None and c is not None and abs(c[0] - w[0]) < 4
                                               and abs(c[1] - w[1]) < 4) for c, w in zip(cs, want)) for cs in seqs)
    check("lattice: cells follow the drawn-update ordinal (k = 0, 1, skip, 2) whatever the material", ok, str(seqs))

    # --- PC2 (design 1.3): tint in the display only
    n = cfg["generator"]["neutral_active_s"]
    m3 = {c: np.linspace(0, 1, n) for c in ("f1", "f3", "f4", "f5", "f6")}
    m3["active"] = np.ones(n, dtype=bool)
    ga, gb = pt.Generator("ordinal", "none", cfg, 3, pc="PC2"), pt.Generator("ordinal", "none", cfg, 3)
    ia = ga.update(dict(m3, p_stuck=np.full(n, 0.9)), n)
    gb.update(m3, n)
    ia2 = ga.update(dict(m3, p_stuck=np.full(n, 0.1)), 2 * n)
    gb.update(m3, 2 * n)
    check("PC2: the drawn base is never tinted", np.array_equal(ga.base, gb.base))
    check("PC2: the display follows the last p_stuck", pt.mad(ia, ia2) > 0.02 and abs(ga.p_bar - 0.1) < 1e-9,
          f"mad={pt.mad(ia, ia2):.3f}")

    # --- E1-5: no text drawing in the generator module
    src = Path(pt.__file__).read_text(encoding="utf-8")
    check("E1-5 no text API", not re.search(r"ImageDraw|ImageFont|putText|\.text\(", src))

    # --- scheduler boundaries
    sc = pt.Sched("clock", 100, 5, False, False)
    s = fake_session([97.0, 150.0], 400)
    ups = pt.schedule(s, sc, 0.3, 1).tolist()
    check("sched skips a slot with typing in (slot-W, slot]", 100 not in ups and 200 in ups, str(ups))
    s = fake_session([10.0], 400, sleep=(150, 350))
    ups = pt.schedule(s, sc, 0.3, 1).tolist()
    check("sched skips slots in sleep and does not catch up", ups == [100], str(ups))
    s = fake_session([10.0, 250.0], 500)
    ups = pt.schedule(s, pt.Sched("clock", 100, 5, False, True), 0.3, 1).tolist()
    check("sched cap1: one update per absence", ups == [100, 300], str(ups))
    s = fake_session([10.0, 95.0, 290.0], 500)
    ups = pt.schedule(s, pt.Sched("recent", 100, 2, False, False), 0.3, 1).tolist()
    check("sched recent: no update inside an absence of 60 s or more", ups == [100, 300], str(ups))
    pc1 = {"stop_silence_s": 3, "min_gap_s": 60}
    s = fake_session([0.1, 3.2, 100.0], 200)
    ups = pt.schedule(s, pt.Sched("stop"), 0.3, 1, pc1).tolist()
    check("sched stop (PC1): no update after typing resumed (rounded time inside the silence)", ups == [7, 103], str(ups))

    # --- statistics
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 2000)
    sc_ = rng.random(2000)
    w = rng.integers(1, 4, 2000).astype(float)
    from sklearn.metrics import roc_auc_score
    check("weighted_auc equals sklearn", abs(checks.weighted_auc(sc_, y, w) - roc_auc_score(y, sc_, sample_weight=w)) < 1e-9)
    tied = np.round(sc_, 1)
    check("presorted AUC equals sklearn with ties", abs(checks.auc_w(checks.auc_prep(tied, y), w)
                                                        - roc_auc_score(y, tied, sample_weight=w)) < 1e-9)

    # --- L300 (design 1.4)
    cfl = dict(cfg, e13=dict(cfg["e13"], window_s=60))
    s = fake_session([5.0, 100.0, 400.0], 900)
    s.seg[0:250] = 1  # stall for 250 of the first 300 s
    ex, lab, actl, valid = pt.presence_features_long(s, cfl, 300)
    check("L300: windows with a full span only", valid.tolist() == [False] * 4 + [True] * 11, str(valid.tolist()))
    check("L300: label of the span (190 of 300 s stall in the second)", lab[4] == 1 and lab[5] == 1 and lab[6] == 0,
          str(lab[:7].tolist()))
    check("L300: presence of the span (longest gap, active seconds)", ex[4][0] == 200.0 and ex[4][3] == 2.0, str(ex[4].tolist()))
    groups = np.repeat(np.arange(40), 50)
    X0 = rng.normal(size=(2000, 6))
    yy = (rng.random(2000) < 0.3).astype(int)
    p0 = checks.oof_predict(X0, yy, groups, "hgb", 1, 5)
    a0 = checks.weighted_auc(p0, yy, np.ones(2000))
    X1 = np.hstack([X0, (yy + rng.normal(scale=0.7, size=2000))[:, None]])
    p1 = checks.oof_predict(X1, yy, groups, "hgb", 1, 5)
    a1 = checks.weighted_auc(p1, yy, np.ones(2000))
    check("E1-3 pipeline: no signal stays near chance", abs(a0 - 0.5) < 0.06, f"auc={a0:.3f}")
    check("E1-3 pipeline: a signal raises AUC", a1 - a0 > 0.2, f"gain={a1 - a0:.3f}")

    # --- L1800 (round 3 design 1.5)
    s = fake_session([5.0, 2000.0], 3600)
    s.seg[0:1000] = 1
    ex, lab, actl, valid = pt.presence_features_long(s, cfl, 1800)
    check("L1800: windows with a full span only (e >= 1800)", valid.tolist() == [False] * 29 + [True] * 31,
          f"first valid at {valid.tolist().index(True)}")
    check("L1800: label of the span (1000 of 1800 s stall in the first)", lab[29] == 1 and lab[45] == 0,
          str([int(lab[29]), int(lab[45])]))

    # --- clock60 and PCcal (round 3 design 1.2, 1.4)
    fx = pt.Sched("fixed", 60)
    s = fake_session([59.5, 119.0, 121.0], 400)
    ups = pt.schedule(s, fx, 0.3, 1).tolist()
    check("clock60: every 60 s whatever the presses", ups == [60, 120, 180, 240, 300, 360], str(ups))
    s = fake_session([10.0], 400, sleep=(100, 250))
    check("clock60: sleep seconds are skipped", pt.schedule(s, fx, 0.3, 1).tolist() == [60, 300, 360])
    sp = fake_session([1.0], 1200)
    sp.seg[300:700] = 3
    ups_c = pt.schedule(sp, fx, 0.3, 1)
    truth = [pt.stall_share(sp, int(u) - 300, int(u)) for u in ups_c]
    v1 = pt.oracle_values(sp, ups_c, pt.Config("raw", "none", fx, pc="PCcal", lam=1.0), 5)
    v0 = pt.oracle_values(sp, ups_c, pt.Config("raw", "none", fx, pc="PCcal", lam=0.0), 5)
    rng = np.random.default_rng(np.random.SeedSequence([5, sp.key_seed & 0xFFFFFFFF, pt.PCCAL_RNG_TAG]))
    draws = [(float(rng.random()), float(rng.random())) for _ in ups_c]
    check("PCcal: lambda = 1 shows q(u) at every update", np.allclose(v1, truth))
    check("PCcal: lambda = 0 shows N (the second draw of each update)", np.allclose(v0, [d[1] for d in draws]))
    vh = pt.oracle_values(sp, ups_c, pt.Config("raw", "none", fx, pc="PCcal", lam=0.5), 5)
    want = [t if d[0] < 0.5 else d[1] for t, d in zip(truth, draws)]
    check("PCcal: the same draws U, N for every lambda (U < lambda shows the truth)", np.allclose(vh, want))
    gp = pt.Generator("raw", "none", cfg, 3, pc="PCcal")
    n = cfg["generator"]["neutral_active_s"]
    m4 = {c: np.linspace(0, 1, n) for c in ("f1", "f3", "f4", "f5", "f6")}
    m4["active"] = np.ones(n, dtype=bool)
    i1 = gp.update(dict(m4, oracle=np.array([0.2])), n)
    i2 = gp.update(dict(m4, oracle=np.array([0.9])), 2 * n)
    ground = np.asarray(cfg["canvas"]["ground"], dtype=np.float32)
    check("PCcal: nothing is drawn (the base stays the ground)", bool((gp.base == ground).all()))
    check("PCcal: the display is one colour that follows the value", float(np.ptp(i1.reshape(-1, 3), axis=0).max()) < 1e-6
          and pt.mad(i1, i2) > 0.05, f"mad={pt.mad(i1, i2):.3f}")

    # --- ORCcum (round 3 design 1.4): the hue is the sum of the increments mod 1, also while neutral
    gc = pt.Generator("ordinal", "none", cfg, 3, pc="ORCcum")
    dh, h0 = cfg["pc2"]["dh"], cfg["pc2"]["h0"]
    m5 = {c: np.zeros(10) for c in ("f1", "f3", "f4", "f5", "f6")}
    m5["active"] = np.zeros(10, dtype=bool)
    qs = [0.9, 0.8, 0.7]
    for k, q in enumerate(qs):
        img = gc.update(dict(m5, oracle=np.array([q])), 10 * (k + 1))
    check("ORCcum: hue = (h0 + dh * sum q) mod 1", abs(gc.hue_cum - (h0 + dh * sum(qs)) % 1.0) < 1e-9,
          f"{gc.hue_cum:.4f}")
    check("ORCcum: the display stays the ground while neutral", bool((img == ground).all()))

    # --- PCsize (round 4 design 1.4, 3.7)
    v1 = pt.oracle_values(sp, ups_c, pt.Config("raw", "none", fx, pc="PCsize", lam=1.0), 5)
    v0 = pt.oracle_values(sp, ups_c, pt.Config("lattice", "diffuse", fx, pc="PCsize", lam=0.0), 5)
    vh = pt.oracle_values(sp, ups_c, pt.Config("raw", "diffuse", fx, pc="PCsize", lam=0.5), 5)
    rng = np.random.default_rng(np.random.SeedSequence([5, sp.key_seed & 0xFFFFFFFF, pt.PCSIZE_RNG_TAG]))
    draws_s = [(float(rng.random()), float(rng.random())) for _ in ups_c]
    check("PCsize: lambda = 1 gives q(u) at every update", np.allclose(v1, truth))
    check("PCsize: lambda = 0 gives N from its own stream (tag 17, not PCcal's)",
          np.allclose(v0, [d[1] for d in draws_s]) and not np.allclose(v0, [d[1] for d in draws]))
    check("PCsize: the same draws U, N for every lambda and form",
          np.allclose(vh, [t if d[0] < 0.5 else d[1] for t, d in zip(truth, draws_s)]))
    check("E1-1 PCsize and ORCband accept the oracle; PCcal's material boundary is unchanged",
          all(pt.Generator(mp, "none", cfg, 1, pc=p).update(dict(mat, oracle=np.full(k, 0.5)), 50) is not None
              for mp, p, k in (("raw", "PCsize", 1), ("lattice", "PCsize", 1), ("ordinal", "ORCband", pt.N_BANDS))))

    def size_run(mapping: str, drift: str, vs: list, acts: list, levels: float, seed: int = 9, mutation=None):
        g = pt.Generator(mapping, drift, cfg, 4242, pc="PCsize", mutation=mutation, seed=seed)
        for k, (v, a) in enumerate(zip(vs, acts)):
            mm = {c: np.full(60, levels * cfg["generator"]["raw_ranges"].get(c, [0, 1])[1]) for c in ("f1", "f3", "f4", "f5", "f6")}
            mm["active"] = np.zeros(60, dtype=bool)
            mm["active"][:a] = True
            g.update(dict(mm, oracle=np.array([v])), 60 * (k + 1))
        return g

    vs = [0.9, 0.1, 0.6, 0.3, 0.8, 0.2]
    acts = [30, 30, 0, 45, 20, 60]  # the first update waits in the buffer (30 < 60); the third draws nothing
    g = size_run("raw", "none", vs, acts, 0.0)
    want_v = [v for v, a in zip(vs, acts) if a > 0]
    check("PCsize raw: the size level of each drawn update is its own v, buffered updates included",
          [h[0] for h in g.size_hist] == want_v, str(g.size_hist))
    rng = np.random.default_rng(np.random.SeedSequence([9, 4242, pt.PCSIZE_DIR_TAG]))
    check("PCsize raw: n6 is one draw of the tag-18 stream per drawn update",
          np.allclose([h[1] for h in g.size_hist], [float(rng.random()) for _ in want_v]))
    g2 = size_run("raw", "diffuse", [0.5] * len(vs), acts, 1.0)
    check("PCsize raw: the n6 stream is the same whatever v, drift and material",
          [h[1] for h in g2.size_hist] == [h[1] for h in g.size_hist])
    ga, gb = size_run("raw", "none", vs, acts, 0.0), size_run("raw", "none", vs, acts, 1.0)
    check("PCsize raw: f1, f3 and f6 of the material do not reach the image (f1 = f3 = 0.5)", np.array_equal(ga.base, gb.base))
    la, lb = size_run("lattice", "none", vs, acts, 0.0), size_run("lattice", "none", vs, acts, 1.0)
    check("PCsize lattice: the material does not reach the image", np.array_equal(la.base, lb.base))
    d = cfg["generator"]["lattice"]["delta"]
    want_k, prev = [], None
    for v in want_v:
        prev = pt.lattice_class(v, prev, d)
        want_k.append(prev)
    check("PCsize lattice: f1, f3, f6 classes are those of 0.5; f4 follows lattice_class over v",
          [h[2] for h in la.lat_hist] == want_k and all(h[0] == h[1] == h[3] == 1 for h in la.lat_hist)
          and [h[0] for h in la.size_hist] == want_v, str(la.lat_hist))
    seq = [0.30, 0.36, 0.39, 0.30, 0.27, 0.75]  # crosses the bound 1/3 inside and outside the hysteresis
    lc = size_run("lattice", "none", seq, [60] * 6, 0.0)
    want_k, prev = [], None
    for v in seq:
        prev = pt.lattice_class(v, prev, d)
        want_k.append(prev)
    check("PCsize lattice: hysteresis across a bound", [h[2] for h in lc.lat_hist] == want_k == [0, 0, 1, 1, 0, 2],
          str([h[2] for h in lc.lat_hist]))

    # --- PCahead (round 5 design 1.4, 3.7): the look-ahead value
    def q300(sess: pt.Session, e: int) -> float:
        return float(np.isin(sess.seg[e - 300 : e], pt.STALL_CODES).mean())

    sa = fake_session([1.0], 1530)  # 25 windows of 60 s and 30 s more (the last window ends at 1500)
    sa.seg[200:500] = 1
    sa.seg[900:1000] = 3
    ups_a = np.array([300, 330, 420, 720, 1440])  # gaps holding 0, 2, 5, 12 and 1 window ends
    av = pt.ahead_values(sa, ups_a)
    want_a = [pt.stall_share(sa, 0, 300),  # E = {} (no window end in (300, 330]): q(300)
              np.mean([q300(sa, e) for e in (360, 420)]),
              np.mean([q300(sa, e) for e in range(480, 721, 60)]),
              np.mean([q300(sa, e) for e in range(780, 1441, 60)]),
              np.mean([q300(sa, e) for e in (1500,)])]  # the last update: up to the session length (1530)
    check("PCahead: a(u_j) is the mean of q300(e) over u_j < e <= u_{j+1} (0, 2, 5, 12 window ends; the last "
          "update reaches the session length; an empty set gives q(u_j))", np.allclose(av, want_a),
          f"{np.round(av, 4).tolist()} vs {np.round(want_a, 4).tolist()}")
    av2 = pt.ahead_values(sa, np.array([60, 120]))
    check("PCahead: window ends below 300 are not used (L300 needs a full span); none left gives q(u_j)",
          np.isclose(av2[0], pt.stall_share(sa, 0, 60))
          and np.isclose(av2[1], np.mean([q300(sa, e) for e in range(300, 1501, 60)])), str(av2))
    dsched = checks.scheds(cfg)[0]
    sa_ups = pt.schedule(sa, dsched, cfg["scheduler_jitter_frac"], 5)
    t_ahead = pt.ahead_values(sa, sa_ups)
    v1 = pt.oracle_values(sa, sa_ups, pt.Config("raw", "none", dsched, pc="PCahead", lam=1.0), 5)
    v0 = pt.oracle_values(sa, sa_ups, pt.Config("lattice", "diffuse", dsched, pc="PCahead", lam=0.0), 5)
    vh = pt.oracle_values(sa, sa_ups, pt.Config("raw", "diffuse", dsched, pc="PCahead", lam=0.5), 5)
    rng = np.random.default_rng(np.random.SeedSequence([5, sa.key_seed & 0xFFFFFFFF, pt.PCAHEAD_RNG_TAG]))
    draws_a = [(float(rng.random()), float(rng.random())) for _ in sa_ups]
    rng = np.random.default_rng(np.random.SeedSequence([5, sa.key_seed & 0xFFFFFFFF, pt.PCSIZE_RNG_TAG]))
    draws_17 = [(float(rng.random()), float(rng.random())) for _ in sa_ups]
    check("PCahead: lambda = 1 gives a(u_j) at every update", np.allclose(v1, t_ahead))
    check("PCahead: lambda = 0 gives N from its own stream (tag 19, not PCsize's tag 17)",
          np.allclose(v0, [d[1] for d in draws_a]) and not np.allclose(v0, [d[1] for d in draws_17]))
    check("PCahead: the same draws U, N for every lambda and form",
          np.allclose(vh, [t if d[0] < 0.5 else d[1] for t, d in zip(t_ahead, draws_a)]))
    check("E1-1 PCahead accepts the oracle (one value)",
          all(pt.Generator(mp, "none", cfg, 1, pc="PCahead").update(dict(mat, oracle=np.full(1, 0.5)), 50) is not None
              for mp in ("raw", "lattice")))

    # round 5 design 3.7: which updates draw a(u_j). A hand-made session on the default scheduler with an update
    # without presses, a neutral stretch and its end; the flow of run() is rebuilt here (run() returns no generator)
    sd = fake_session([], 3000)
    pr = [float(t) for t in range(10, 40, 1)]  # 30 active seconds before the first update: neutral (< 60)
    pr += [float(t) for t in range(400, 440, 1)]  # 40 more before the second: the neutral ends at the second
    pr += [float(t) for t in range(1000, 1050, 1)]  # nothing in (600, 900]: the third update draws nothing
    sd = fake_session(pr, 3000)
    sd.seg[0:700] = 1
    sd.seg[1500:2100] = 3
    sd_ups = pt.schedule(sd, dsched, cfg["scheduler_jitter_frac"], 5)
    a_sd = pt.ahead_values(sd, sd_ups)
    ok_draw = True
    detail = []
    for mapping, drift in (("raw", "none"), ("raw", "diffuse"), ("lattice", "none"), ("lattice", "diffuse")):
        conf = pt.Config(mapping, drift, dsched, pc="PCahead", lam=1.0)
        vals = pt.oracle_values(sd, sd_ups, conf, 5)
        g = pt.Generator(mapping, drift, cfg, sd.key_seed, "PCahead", None, 5)
        imgs = [g.ground_image()]
        prev = 0
        has = []
        for k, u in enumerate(sd_ups):
            mm = pt.material_slice(sd, prev, int(u), False, vals[k])
            has.append(bool(mm["active"].any()))
            imgs.append(g.update(mm, int(u)))
            prev = int(u)
        want_v = [a for a, h in zip(a_sd, has) if h]
        got_v = [h[0] for h in g.size_hist]
        first_drawn = next(i for i, im in enumerate(imgs) if not np.array_equal(im, g.ground_image()))
        cum = np.cumsum([int(pt.material_slice(sd, (0 if k == 0 else int(sd_ups[k - 1])), int(u))["active"].sum())
                         for k, u in enumerate(sd_ups)])
        want_first = 1 + int(np.argmax(cum >= cfg["generator"]["neutral_active_s"]))
        ok = np.allclose(got_v, want_v) and first_drawn == want_first and not all(has)
        if mapping == "lattice":
            d_ = cfg["generator"]["lattice"]["delta"]
            prevk, want_k = None, []
            for v in got_v:
                prevk = pt.lattice_class(v, prevk, d_)
                want_k.append(prevk)
            ok = ok and [h[2] for h in g.lat_hist] == want_k
        ok_draw = ok_draw and ok
        detail.append(f"{mapping}-{drift}: drawn {len(got_v)} of {len(sd_ups)}, first image {first_drawn} "
                      f"(want {want_first})")
    check("PCahead: each drawn update carries its own a(u_j) in order (buffered ones at the end of the neutral, "
          "none for an update without presses; lattice f4 classes follow lattice_class)", ok_draw, "; ".join(detail))

    # --- ORCband (round 4 design 1.4, 3.7)
    sb = fake_session([1.0], 900)
    sb.seg[0:60] = 1
    sb.seg[150:210] = 3
    bv = pt.band_values(sb, 300)
    check("ORCband: band k is the stall share of [u - 300 + 60k, u - 240 + 60k)",
          np.allclose(bv, [1.0, 0.0, 0.5, 0.5, 0.0]), str(bv))
    bv = pt.band_values(sb, 120)
    check("ORCband: bands with an empty span are NaN; a span cut at 0 uses its seconds from 0",
          np.isnan(bv[:3]).all() and np.allclose(bv[3:], [1.0, 0.0]), str(bv))
    gband = pt.Generator("ordinal", "none", cfg, 3, pc="ORCband")
    mb = {c: np.linspace(0, 1, 60) for c in ("f1", "f3", "f4", "f5", "f6")}
    mb["active"] = np.ones(60, dtype=bool)
    q5 = np.array([np.nan, 0.0, 0.25, 0.5, 1.0])
    imgb = gband.update(dict(mb, oracle=q5), 60)
    c2 = cfg["pc2"]
    w5 = cfg["canvas"]["w"] // pt.N_BANDS
    ok = np.array_equal(imgb[:, 0:w5], gband.base[:, 0:w5])
    for k in range(1, 5):
        want = (1 - c2["beta"]) * gband.base[:, k * w5 : (k + 1) * w5] + c2["beta"] * pt.hsv(c2["h0"] + c2["dh"] * q5[k], 0.6, 0.8)
        ok = ok and np.allclose(imgb[:, k * w5 : (k + 1) * w5], want, atol=1e-6)
    check("ORCband: each vertical band is tinted by its value; a NaN band shows the drawn base", bool(ok))
    check("ORCband: the drawn base is never tinted", not np.allclose(gband.base, imgb))

    # --- names and verdicts (round 3 design 3.1-3.4)
    check("kind_of: PCcal, PCsize, the baselines, the grid and the oracles are not judged as configurations",
          [checks.kind_of(x) for x in ("PC1", "PCcal", "PCcal0", "PCcal@0.35", "ORC300-I300-W5",
                                        "ORCgap-I300-W5-recent60", "ORCcum-I300-W5", "ORCband-I300-W5-recent60",
                                        "PCsize-raw-none", "PCsize0-lattice-diffuse", "PCsize-raw-diffuse@0.35",
                                        "PCsize-lattice-none@0.00", "raw-none-I300-W5")]
          == ["pc1", "pccal", "descriptive", "descriptive", "oracle", "oracle", "oracle", "oracle",
              "pcsize", "baseline", "descriptive", "descriptive", "config"])
    check("form_of: the form of a configuration, a PCsize and a PCsize0",
          [checks.form_of(x) for x in ("lattice-diffuse-I300-W5-recent60", "PCsize-raw-diffuse", "PCsize0-lattice-none")]
          == ["lattice-diffuse", "raw-diffuse", "lattice-none"])
    lams = {f: 0.3 for f in checks.forms(cfg)}
    alams = {k: 0.6 for k in checks.ahead_keys(cfg)}
    rlams = {b: 0.2 for b in checks.replicate_bases(cfg)}
    cfg_t = dict(cfg, pccal=dict(cfg["pccal"], lam=0.4), pcsize=dict(cfg["pcsize"], lam=lams),
                 pcahead=dict(cfg["pcahead"], lam=alams), replicate=dict(cfg["replicate"], lam=rlams))
    C = checks.configs(cfg_t)
    names = [c.name for c in C["main"] + [C["pc1"], C["pccal"], C["pccal0"]] + C["pcsize"] + C["pcsize0"] + C["orc"]
             + C["pcahead"] + C["pcahead0"]]
    check("configs: 8 configurations, PC1, PCcal, PCcal0, 4 PCsize, 4 PCsize0, 8 oracles, 8 PCahead, 8 PCahead0, "
          "unique names (round 5 design 3.2: 43)",
          len(names) == 43 and len(set(names)) == 43 and sum(checks.kind_of(x) == "config" for x in names) == 8
          and sum(checks.kind_of(x) == "oracle" for x in names) == 8
          and sum(checks.kind_of(x) == "pcahead" for x in names) == 8
          and sum(checks.kind_of(x) == "ahead_baseline" for x in names) == 8, str(names))
    check("configs: each PCahead serves the real configuration of the same name, on its scheduler",
          sorted(checks.ahead_key_of(c.name) for c in C["pcahead"]) == sorted(c.name for c in C["main"])
          and all(c.sched == m.sched and (c.mapping, c.drift) == (m.mapping, m.drift)
                  for c in C["pcahead"] + C["pcahead0"] for m in C["main"] if m.name == checks.ahead_key_of(c.name))
          and all(c.pc == "PCahead" and c.lam == 0.6 for c in C["pcahead"])
          and all(c.pc == "PCahead" and c.lam == 0.0 for c in C["pcahead0"]))
    ga_names = [c.name for c in C["grid_ahead"]]
    check("configs: the main pilot's grid is lambda 0 and the 20 candidates of each of the 8 PCahead, descriptive",
          len(ga_names) == 168 and len(set(ga_names)) == 168 and all(checks.kind_of(x) == "descriptive" for x in ga_names))
    gr = C["grid_rep"]
    gr_names = [c.name for v in gr.values() for c in v]
    check("configs: the replicate pilot's grid is the 20 candidates (no lambda 0) of each of the 12 controls",
          list(gr) == checks.replicate_bases(cfg) and len(gr_names) == 240 and len(set(gr_names)) == 240
          and all(checks.kind_of(x) == "descriptive" for x in gr_names) and not any(x.endswith("@0.00") for x in gr_names))
    rc = C["replicate"]
    check("configs: the 12 replicate controls in the fixed order, at their lambdas, PCsize on clock60 and PCahead on "
          "its scheduler", [c.name for c in rc] == [f"{b}@0.20" for b in checks.replicate_bases(cfg)]
          and all(c.sched.kind == "fixed" and c.pc == "PCsize" for c in rc[:4])
          and all(c.pc == "PCahead" and c.sched in checks.scheds(cfg) for c in rc[4:]), str([c.name for c in rc]))
    gnames = [c.name for c in C["grid"]]
    check("configs: the pilot's grid is lambda 0 and the 20 candidates for each of the 4 forms, unique names",
          len(gnames) == 84 and len(set(gnames)) == 84 and all(checks.kind_of(x) == "descriptive" for x in gnames))
    check("configs: PCsize runs on its form and on the 60 s clock",
          all(c.sched.kind == "fixed" and c.sched.interval_s == 60 and f"{c.mapping}-{c.drift}" == checks.form_of(c.name)
              for c in C["pcsize"] + C["pcsize0"]))

    def rec(up: float, lo: float, gain: float, nan: int = 0) -> dict:
        return {"upper_max": up, "lower_max": lo, "gain_max": gain, "n_nan_bounds": nan}

    FORMS = checks.forms(cfg)

    def base_recs() -> dict:
        r = {"PC1": rec(0.3, 0.2, 0.25), "PCcal": rec(0.07, 0.04, 0.05), "PCcal0": rec(0.01, -0.01, 0.0),
             "ORC300-I300-W5": rec(0.02, 0.0, 0.01), "ORCband-I300-W5": rec(0.02, 0.0, 0.01),
             "raw-none-I300-W5": rec(0.029, 0.0, 0.01), "raw-none-I300-W5-recent60": rec(0.03, 0.0, 0.01),
             "lattice-diffuse-I300-W5": rec(0.01, 0.0, 0.005)}
        for f in FORMS:
            r[f"PCsize-{f}"] = rec(0.07, 0.04, 0.05)
            r[f"PCsize0-{f}"] = rec(0.02, -0.01, 0.0)
        for k in checks.ahead_keys(cfg):
            r[f"PCahead-{k}"] = rec(0.07, 0.04, 0.05)
            r[f"PCahead0-{k}"] = rec(0.02, -0.01, 0.0)
        return r

    nulls = {k: 0.01 for k in base_recs()}
    j = checks.judge(base_recs(), nulls, cfg, False)
    check("judge: everything works -> green below 0.03, red at 0.03 exactly, oracles narrow, PCsize works",
          all(j["forms"][f]["detector_ok"] and j["forms"][f]["reasons"] == [] for f in FORMS)
          and j["verdicts"]["raw-none-I300-W5"] == "green" and j["verdicts"]["raw-none-I300-W5-recent60"] == "red"
          and j["verdicts"]["ORC300-I300-W5"] == j["verdicts"]["ORCband-I300-W5"] == "channel_narrow"
          and j["verdicts"]["PCcal0"] == "descriptive" and j["verdicts"]["PCsize-raw-none"] == "works"
          and j["verdicts"]["PCsize0-raw-none"] == "baseline_below", str(j))
    allf = {f: None for f in FORMS}  # None: the same reasons for every form
    cases = [
        ("PC1 lower 0.10 exactly fails", {"PC1": rec(0.3, 0.10, 0.2)}, nulls, ["weak_detector"], allf),
        ("PCcal lower 0.03 exactly fails", {"PCcal": rec(0.07, 0.03, 0.05)}, nulls, ["weak_detector"], allf),
        ("PCcal point 0.08 exactly works", {"PCcal": rec(0.1, 0.04, 0.08)}, nulls, [], allf),
        ("PCcal point above 0.08 fails", {"PCcal": rec(0.1, 0.06, 0.0801)}, nulls, ["weak_detector"], allf),
        ("null 0.03 exactly fails", {}, dict(nulls, PCcal0=0.03), ["null"], allf),
        ("a NaN bound anywhere: every form is undecidable, without weak_* or shape_baseline",
         {"PCcal0": rec(float("nan"), 0.0, 0.0, 1), "PCsize-raw-none": rec(0.07, 0.01, 0.05),
          "PCsize0-raw-none": rec(0.05, 0.0, 0.02)}, nulls, ["nan"], allf),
        ("PCsize lower 0.03 exactly fails its own form only", {"PCsize-raw-none": rec(0.07, 0.03, 0.05)}, nulls,
         [], {"raw-none": ["weak_shape_pc"]}),
        ("PCsize point 0.08 exactly works", {"PCsize-raw-none": rec(0.1, 0.04, 0.08)}, nulls, [], {}),
        ("PCsize point above 0.08 fails", {"PCsize-raw-none": rec(0.1, 0.06, 0.0801)}, nulls, [],
         {"raw-none": ["weak_shape_pc"]}),
        ("PCsize0 upper 0.03 exactly: shape_baseline", {"PCsize0-raw-none": rec(0.03, 0.0, 0.01)}, nulls, [],
         {"raw-none": ["shape_baseline"]}),
        ("PCsize0 upper just below 0.03 works", {"PCsize0-raw-none": rec(0.0299, 0.0, 0.01)}, nulls, [], {}),
        ("reasons are listed together", {"PC1": rec(0.3, 0.05, 0.2), "PCsize-raw-none": rec(0.07, 0.01, 0.05),
                                         "PCsize0-raw-none": rec(0.05, 0.0, 0.02)}, dict(nulls, PCcal0=0.04),
         ["weak_detector", "null"], {"raw-none": ["weak_detector", "weak_shape_pc", "shape_baseline", "null"]}),
    ]
    for name, patch, nl, reasons, per in cases:
        jj = checks.judge({**base_recs(), **patch}, nl, cfg, False)
        ok = True
        for f in FORMS:
            want = per.get(f) if per.get(f) is not None else reasons
            fo = jj["forms"][f]
            ok = ok and fo["reasons"] == want and fo["detector_ok"] == (not want)
        want_rn = per.get("raw-none") if per.get("raw-none") is not None else reasons
        want_ld = per.get("lattice-diffuse") if per.get("lattice-diffuse") is not None else reasons
        ok = ok and jj["verdicts"]["raw-none-I300-W5"] == ("green" if not want_rn else "undecidable")
        ok = ok and jj["verdicts"]["lattice-diffuse-I300-W5"] == ("green" if not want_ld else "undecidable")
        if "nan" in reasons:
            ok = ok and jj["verdicts"]["ORC300-I300-W5"] == "undecidable"
        check(f"judge: {name}", ok, str({f: jj["forms"][f]["reasons"] for f in FORMS}))
    jj = checks.judge({**base_recs(), "PCcal": rec(0.07, 0.02, 0.05)}, nulls, cfg, False)
    check("judge: an oracle is not narrow when PCcal fails (PCsize does not stand in for it)",
          jj["verdicts"]["ORC300-I300-W5"] == jj["verdicts"]["ORCband-I300-W5"] == "channel_partial")
    jj = checks.judge({}, None, cfg, True)
    check("judge: a failed fit makes every form undecidable",
          all(not jj["forms"][f]["detector_ok"] and "fit_failed" in jj["forms"][f]["reasons"] for f in FORMS))
    check("judge: a failed fit makes every configuration undecidable, without weak_ahead_pc or ahead_baseline",
          all(not d_["detector_ok"] and d_["reasons"] == ["fit_failed", "null"] for d_ in jj["detector"].values()),
          str(jj["detector"]))

    # round 5 design 3.2: the PCahead of each configuration
    KEYS_A = checks.ahead_keys(cfg)
    jj = checks.judge(base_recs(), nulls, cfg, False)
    check("judge: every PCahead works -> each configuration is judged by its own detector",
          all(jj["detector"][k]["detector_ok"] and jj["detector"][k]["reasons"] == [] for k in KEYS_A)
          and jj["verdicts"]["PCahead-raw-none-I300-W5"] == "works"
          and jj["verdicts"]["PCahead0-raw-none-I300-W5"] == "baseline_below", str(jj["detector"]))
    acases = [
        ("PCahead lower 0.03 exactly fails its own configuration only",
         {"PCahead-raw-none-I300-W5": rec(0.07, 0.03, 0.05)}, nulls, {"raw-none-I300-W5": ["weak_ahead_pc"]}),
        ("PCahead point 0.08 exactly works", {"PCahead-raw-none-I300-W5": rec(0.1, 0.04, 0.08)}, nulls, {}),
        ("PCahead point above 0.08 fails", {"PCahead-raw-none-I300-W5-recent60": rec(0.1, 0.06, 0.0801)}, nulls,
         {"raw-none-I300-W5-recent60": ["weak_ahead_pc"]}),
        ("PCahead0 upper 0.03 exactly: ahead_baseline", {"PCahead0-lattice-diffuse-I300-W5": rec(0.03, 0.0, 0.01)},
         nulls, {"lattice-diffuse-I300-W5": ["ahead_baseline"]}),
        ("PCahead0 upper just below 0.03 works", {"PCahead0-lattice-diffuse-I300-W5": rec(0.0299, 0.0, 0.01)},
         nulls, {}),
        ("a missing PCahead fails its configuration", {"PCahead-raw-none-I300-W5": None}, nulls,
         {"raw-none-I300-W5": ["weak_ahead_pc"]}),
        ("reasons are listed together, null last",
         {"PCsize-raw-none": rec(0.07, 0.01, 0.05), "PCahead-raw-none-I300-W5": rec(0.07, 0.01, 0.05),
          "PCahead0-raw-none-I300-W5": rec(0.05, 0.0, 0.02)}, dict(nulls, PCcal0=0.04),
         {**{k: ["null"] for k in KEYS_A},
          "raw-none-I300-W5": ["weak_shape_pc", "weak_ahead_pc", "ahead_baseline", "null"],
          "raw-none-I300-W5-recent60": ["weak_shape_pc", "null"]}),
    ]
    for name, patch, nl, per in acases:
        recs = {**base_recs(), **patch}
        recs = {k: v for k, v in recs.items() if v is not None}
        jj = checks.judge(recs, nl, cfg, False)
        ok = True
        for k in KEYS_A:
            want = per.get(k, [])
            ok = ok and jj["detector"][k]["reasons"] == want and jj["detector"][k]["detector_ok"] == (not want)
            if k in recs:
                ok = ok and jj["verdicts"][k] == ("undecidable" if want else ("green" if recs[k]["upper_max"] < 0.03
                                                                                else "red"))
        check(f"judge: {name}", ok, str({k: jj["detector"][k]["reasons"] for k in KEYS_A if jj["detector"][k]["reasons"]}))
    jj = checks.judge({**base_recs(), "raw-none-I300-W5": rec(0.029, 0.0, 0.01),
                       "PCahead-raw-none-I300-W5-recent60": rec(0.07, 0.02, 0.05)}, nulls, cfg, False)
    check("judge: a PCahead that fails on recent60 leaves the default configuration of the same form judged",
          jj["verdicts"]["raw-none-I300-W5"] == "green" and jj["verdicts"]["raw-none-I300-W5-recent60"] == "undecidable"
          and jj["verdicts"]["PCahead-raw-none-I300-W5-recent60"] == "fails")
    check("kind_of: PCahead, PCahead0 and the PCahead grid are told apart",
          [checks.kind_of(x) for x in ("PCahead-raw-none-I300-W5", "PCahead0-raw-none-I300-W5-recent60",
                                        "PCahead-lattice-diffuse-I300-W5@0.35", "PCahead-raw-none-I300-W5@0.00")]
          == ["pcahead", "ahead_baseline", "descriptive", "descriptive"]
          and checks.form_of("PCahead0-lattice-none-I300-W5-recent60") == "lattice-none"
          and checks.ahead_key_of("PCahead-raw-diffuse-I300-W5-recent60") == "raw-diffuse-I300-W5-recent60"
          and checks.ahead_key_of("raw-diffuse-I300-W5") == "raw-diffuse-I300-W5")

    # --- the choice of lambda (round 3 design 3.9)
    grid = [round(0.05 * i, 2) for i in range(1, 21)]
    lin = [0.1 * x for x in grid]  # 0.005 ... 0.1: 0.05 at lambda 0.5
    check("select_lambda: monotone values -> the closest", checks.select_lambda(grid, lin, 0.05, 0.08)["lam"] == 0.5)
    bumpy = list(lin)
    bumpy[9], bumpy[10], bumpy[11] = 0.06, 0.04, 0.05  # lambda 0.5, 0.55, 0.6 pool to 0.05
    sel = checks.select_lambda(grid, bumpy, 0.05, 0.08)
    check("select_lambda: a pooled block at the target -> its middle", sel["lam"] == 0.55, str(sel))
    sel = checks.select_lambda(grid, [0.01] * 20, 0.05, 0.08)
    check("select_lambda: all below the target -> 1.0", sel["lam"] == 1.0)
    sel = checks.select_lambda(grid, [0.09] * 20, 0.05, 0.08)
    check("select_lambda: the smallest above the upper bound -> 0.05", sel["lam"] == 0.05)
    withnan = list(lin)
    withnan[9] = float("nan")
    sel = checks.select_lambda(grid, withnan, 0.05, 0.08)
    check("select_lambda: a NaN candidate is left out", 0.5 not in [f[0] for f in sel["fit"]] and sel["excluded"] == [0.5]
          and sel["lam"] in (0.45, 0.55), str(sel["lam"]))
    check("select_lambda: no finite candidate -> 1.0", checks.select_lambda(grid, [float("nan")] * 20, 0.05, 0.08)["lam"] == 1.0)
    two = [0.04 if x < 0.5 else 0.06 for x in grid]  # 0.05 lies between two blocks: the smaller lambda side
    check("select_lambda: equally close above and below -> the block of the smaller lambda",
          checks.select_lambda(grid, two, 0.05, 0.08)["lam"] == 0.25)  # the run 0.05..0.45: its middle
    # round 4 design 3.9: one lambda per form, each from its own values; the baseline (lambda 0) is not used
    slopes = {"raw-none": 0.1, "raw-diffuse": 0.2, "lattice-none": 0.05, "lattice-diffuse": 0.01}
    l300 = {}
    for f, sl in slopes.items():
        l300[f"PCsize-{f}@0.00"] = rec(0.2, 0.1, 0.15)  # a large baseline must not move the choice
        for x in grid:
            l300[f"PCsize-{f}@{x:.2f}"] = rec(0.0, 0.0, sl * x)
    sels = checks.select_by_form(l300, cfg)
    check("select_by_form: each form chosen from its own grid, the baseline unused",
          {f: s["lam"] for f, s in sels.items()} == {"raw-none": 0.5, "raw-diffuse": 0.25, "lattice-none": 1.0,
                                                      "lattice-diffuse": 1.0}, str({f: s["lam"] for f, s in sels.items()}))
    # round 5 design 3.9: PCahead per form and scheduler (target 0.05); the replicate controls (target 0.035)
    l300a = {}
    slopes_a = {k: 0.02 * (i + 1) for i, k in enumerate(checks.ahead_keys(cfg))}  # 0.02 .. 0.16 per unit lambda
    for k, sl in slopes_a.items():
        l300a[f"PCahead-{k}@0.00"] = rec(0.2, 0.1, 0.15)
        for x in grid:
            l300a[f"PCahead-{k}@{x:.2f}"] = rec(0.0, 0.0, sl * x)
    sa_ = checks.select_ahead(l300a, cfg)
    want_sa = {k: (1.0 if sl < 0.05 else
                   min(grid, key=lambda x: (round(abs(sl * x - 0.05), 6), x))) for k, sl in slopes_a.items()}
    check("select_ahead: each form and scheduler from its own grid at target 0.05, the baseline unused",
          {k: s["lam"] for k, s in sa_.items()} == want_sa, str({k: s["lam"] for k, s in sa_.items()}))
    l300r = {}
    bases = checks.replicate_bases(cfg)
    slopes_r = {b: 0.01 * (i + 1) for i, b in enumerate(bases)}  # 0.01 .. 0.12 per unit lambda
    for b, sl in slopes_r.items():
        for x in grid:
            l300r[f"{b}@{x:.2f}"] = rec(0.0, 0.0, sl * x)
    sr = checks.select_replicate(l300r, cfg)
    want_sr = {b: (1.0 if sl < 0.035 else
                   min(grid, key=lambda x: (round(abs(sl * x - 0.035), 6), x))) for b, sl in slopes_r.items()}
    check("select_replicate: each of the 12 controls from its own grid at target 0.035 (replicate.target)",
          {b: s["lam"] for b, s in sr.items()} == want_sr and cfg["replicate"]["target"] == 0.035,
          str({b: s["lam"] for b, s in sr.items()}))
    big = {f"{b}@{x:.2f}": rec(0.0, 0.0, 0.09 + 0.01 * x) for b in bases for x in grid}
    check("select_replicate: the smallest candidate already above replicate.upper (0.08) -> 0.05",
          all(s["lam"] == 0.05 for s in checks.select_replicate(big, cfg).values()) and cfg["replicate"]["upper"] == 0.08)

    # --- the replicate summary (round 5 design 3.10)
    import summarize_replicates as sr_
    rp = cfg["replicate"]

    def arec(gains: list, los: list, ups: list) -> dict:
        return {"attackers": {a: {"gain": g, "ci95": [lo_, up_]} for a, g, lo_, up_ in zip(sr_.ATTACKERS, gains, los, ups)}}

    cl = lambda r_: sr_.classify(r_, cfg["e13"]["margin"], rp["lower"], rp["upper"])  # noqa: E731
    check("replicate classify: upper max < 0.03 is green_numeric; 0.03 exactly is not",
          cl(arec([0.01] * 4, [0.0] * 4, [0.0299] * 4))["cls"] == "green_numeric"
          and cl(arec([0.01] * 4, [0.0] * 4, [0.0299, 0.0299, 0.0299, 0.03]))["cls"] == "middle")
    check("replicate classify: detected needs lower max > 0.03 and point max <= 0.08; 0.03 / 0.08 exactly",
          cl(arec([0.08] * 4, [0.0301, 0, 0, 0], [0.1] * 4))["cls"] == "detected"
          and cl(arec([0.05] * 4, [0.03] * 4, [0.07] * 4))["cls"] == "middle"
          and cl(arec([0.0801, 0, 0, 0], [0.05] * 4, [0.1] * 4)) == {"cls": "middle", "strong": True})
    check("replicate classify: a non-finite point or bound, or a missing record, is unmeasurable",
          cl(arec([float("nan"), 0.05, 0.05, 0.05], [0.04] * 4, [0.06] * 4))["cls"] == "unmeasurable"
          and cl(arec([0.05] * 4, ["nan", 0.04, 0.04, 0.04], [0.06] * 4))["cls"] == "unmeasurable"
          and cl(None)["cls"] == "unmeasurable")
    base_seed = 20261009
    names12 = {f"{b}@0.20": 0.2 for b in bases}

    def rep_(r_: int, gain: float, up: float = 0.05, **kw) -> dict:
        d_ = {"rep_index": r_, "seed": base_seed + rp["seed_offset"] + r_, "crashed": False, "fit_failed": False,
              "controls": dict(names12), "config_sha256": "h", "instrument_commit": "c", "instrument_dirty": False,
              "configs": {n: arec([gain] * 4, [gain - 0.001] * 4, [up] * 4) for n in names12}}
        d_.update(kw)
        return d_

    def summ(reps: list, n_: int = 20):
        try:
            return sr_.summarize(reps, cfg_t, base_seed, n_)
        except ValueError as e:
            return str(e)

    check("replicate band_of: [0.030, 0.045) with at least 10 measured; 0.030 in, 0.045 out, 9 measured not judged",
          [sr_.band_of(x, n_, rp) for x, n_ in ((0.03, 10), (0.0449999, 20), (0.045, 20), (0.0299999, 20), (0.04, 9))]
          == ["in_band", "in_band", "out_of_band", "out_of_band", "not_judged"])
    full = [rep_(r_, 0.036, 0.045) for r_ in range(20)]
    s_ = summ(full)
    c0 = s_["controls"][bases[0]] if isinstance(s_, dict) else {}
    check("replicate summary: 20 replicates line up; counts, band and the fixed order",
          isinstance(s_, dict) and list(s_["controls"]) == bases and c0["n_measured"] == 20
          and c0["counts"]["detected"] == 20 and c0["band"] == "in_band" and s_["n_in_band"] == 12, str(s_)[:300])
    edge = [rep_(r_, 0.045 if r_ % 2 else 0.030, 0.05) for r_ in range(20)]  # mean 0.0375: in the band
    s_lo = summ([rep_(r_, 0.030, 0.05) for r_ in range(20)])
    s_hi = summ([rep_(r_, 0.045, 0.05) for r_ in range(20)])
    check("replicate summary: the band is [0.030, 0.045): 0.030 is in, 0.045 is out",
          isinstance(s_lo, dict) and isinstance(s_hi, dict) and s_lo["controls"][bases[0]]["band"] == "in_band"
          and s_hi["controls"][bases[0]]["band"] == "out_of_band" and s_hi["n_in_band"] == 0 and "reading" in s_hi
          and isinstance(summ(edge), dict))
    mixed = [rep_(r_, 0.036, 0.045, crashed=True, configs={}) if r_ < 5 else
             rep_(r_, 0.036, 0.045, fit_failed=True, configs={}) if r_ < 8 else rep_(r_, 0.036, 0.045)
             for r_ in range(20)]
    mixed[19]["configs"][f"{bases[0]}@0.20"] = arec([float("nan")] * 4, [0.0] * 4, [0.05] * 4)
    s_m = summ(mixed)
    cm = s_m["controls"][bases[0]] if isinstance(s_m, dict) else {}
    check("replicate summary: crashed (all 12), fit_failed (all 12) and NaN (one control, one replicate) are counted "
          "apart and left out of the shares; fewer than 10 measured -> the band is not judged",
          isinstance(s_m, dict) and cm["counts"]["unmeasurable_crashed"] == 5 and cm["counts"]["unmeasurable_fit_failed"] == 3
          and cm["counts"]["unmeasurable_nan"] == 1 and cm["n_measured"] == 11 and cm["band"] == "in_band"
          and s_m["controls"][bases[1]]["n_measured"] == 12, str(cm)[:300])
    few = [rep_(r_, 0.036, 0.045, crashed=True, configs={}) if r_ < 11 else rep_(r_, 0.036, 0.045) for r_ in range(20)]
    allc = [rep_(r_, 0.036, 0.045, crashed=True, configs={}) for r_ in range(20)]
    s_f, s_a = summ(few), summ(allc)
    check("replicate summary: 9 measured -> not_judged; none measured -> the share is not estimable",
          isinstance(s_f, dict) and s_f["controls"][bases[0]]["band"] == "not_judged"
          and isinstance(s_a, dict) and s_a["controls"][bases[0]]["share_green_numeric"] is None
          and s_a["controls"][bases[0]]["band"] == "not_judged")
    bad_cases = {
        "a replicate missing": full[:19],
        "a seed duplicated": full[:19] + [dict(full[18], rep_index=19)],
        "a seed off": full[:19] + [dict(full[19], seed=full[19]["seed"] + 1)],
        "one replicate with another lambda": full[:19] + [dict(full[19], controls={**names12, f"{bases[3]}@0.20": 0.25})],
        "one replicate with another config hash": full[:19] + [dict(full[19], config_sha256="x")],
        "one replicate with another commit": full[:19] + [dict(full[19], instrument_commit="x")],
        "one replicate with dirty instruments": full[:19] + [dict(full[19], instrument_dirty=True)],
        "a control missing in one replicate": full[:19] + [dict(full[19], configs={n: v for n, v in full[19]["configs"].items()
                                                                                   if not n.startswith(bases[5])})],
        "an attacker missing in one replicate": full[:19] + [dict(full[19], configs={**full[19]["configs"], f"{bases[2]}@0.20":
                                                                                    {"attackers": {a: {"gain": 0.04, "ci95": [0.03, 0.05]}
                                                                                                   for a in sr_.ATTACKERS[:3]}}})],
    }
    fails = {k: isinstance(summ(v), str) for k, v in bad_cases.items()}
    check("replicate summary: fails without writing when the replicates do not line up", all(fails.values()), str(fails))
    cp = sr_.clopper_pearson(0, 20)
    check("replicate summary: Clopper-Pearson 0 of 20 -> [0, about 0.168]", cp[0] == 0.0 and abs(cp[1] - 0.1684) < 1e-3,
          str(cp))

    # --- mutations on real synthetic sessions (design 3.8)
    manifest = json.loads((work / "sessions.json").read_text(encoding="utf-8"))
    ps = [m for m in manifest if m["set"] == "P"][:6]
    d = cfg["scheduler_default"]
    default = pt.Sched("clock", d["interval_s"], d["window_s"], False, False)
    v14 = v17 = 0
    v14_ok = v17_ok = 0
    for m in ps:
        sess = pt.load_session(work, m)
        r = pt.run(sess, pt.Config("ordinal", "none", default, mutation="fade_in_absence"), cfg, 1, False, False)
        v14 += sum(1 for ab in r["absences"] if ab["e14_violation"])
        r = pt.run(sess, pt.Config("ordinal", "none", default, mutation="neutral_on_low_recent"), cfg, 1, False, False)
        v17 += r["e17_violations"]
        r = pt.run(sess, pt.Config("ordinal", "none", default), cfg, 1, False, False)
        v14_ok += sum(1 for ab in r["absences"] if ab["e14_violation"])
        v17_ok += r["e17_violations"]
    check("mutation: fading in absence turns E1-4 red", v14 > 0, f"violations={v14}")
    check("mutation: neutral on low recent input turns E1-7 red", v17 > 0, f"violations={v17}")
    check("unmutated ordinal-none is clean on the same sessions", v14_ok == 0 and v17_ok == 0, f"{v14_ok}/{v17_ok}")

    # design 3.8 (third): raw with levels unrelated to the trace must not show a gain in E1-3
    p_all = [m for m in manifest if m["set"] == "P"]
    if len(p_all) < 40:
        print(f"SKIP  mutation: random levels keep the E1-3 gain below the margin  (only {len(p_all)} P sessions; "
              "runs in the full run)")
    else:
        use = p_all[:60]
        XA, Y, G, F = [], [], [], []
        conf = pt.Config("raw", "none", default, mutation="random_levels")
        for i, m in enumerate(use):
            sess = pt.load_session(work, m)
            fa, lab, _ = pt.presence_features(sess, cfg)
            XA.append(fa)
            Y.append(lab)
            G.append(np.full(len(lab), i))
            F.append(pt.run(sess, conf, cfg, 1, True, False)["windows"])
        XA, Y, G, F = np.vstack(XA), np.concatenate(Y), np.concatenate(G), np.vstack(F)
        XB = np.hstack([XA, checks.lagged(F, G, cfg["e13"]["lags"])])
        ones = np.ones(len(Y))
        gains = []
        for kind in ("hgb", "lr"):
            pa = checks.oof_predict(XA, Y, G, kind, 1, cfg["e13"]["folds"])
            pb = checks.oof_predict(XB, Y, G, kind, 1, cfg["e13"]["folds"])
            gains.append(checks.weighted_auc(pb, Y, ones) - checks.weighted_auc(pa, Y, ones))
        check("mutation: random levels keep the E1-3 gain below the margin", max(gains) < cfg["e13"]["margin"],
              f"gain hgb={gains[0]:+.3f} lr={gains[1]:+.3f} on {len(use)} sessions", soft=True)

        # design 3.8 (round 2): lattice with random levels, label L300, all four attacker sets
        checks._init(cfg, 1, str(work))
        conf = pt.Config("lattice", "none", default, mutation="random_levels")
        sids = [m["sid"] for m in use]
        shape = {conf.name: np.vstack([pt.run(checks._session(sid), conf, cfg, 1, True, False)["windows"] for sid in sids])}
        lab = checks.e13_labels(sids, cfg)["L300"]
        xb = checks.attacker_sets(lab, shape, cfg)[conf.name]
        ones = np.ones(len(lab["Y"]))
        gains = {}
        for kind in ("hgb", "lr"):
            a0 = checks.weighted_auc(checks.oof_predict(lab["XA"], lab["Y"], lab["G"], kind, 1, cfg["e13"]["folds"]),
                                     lab["Y"], ones)
            for fs in ("full", "small"):
                pb = checks.oof_predict(xb[fs], lab["Y"], lab["G"], kind, 1, cfg["e13"]["folds"])
                gains[f"{fs}/{kind}"] = checks.weighted_auc(pb, lab["Y"], ones) - a0
        check("mutation: lattice with random levels keeps the L300 gain below the margin",
              max(gains.values()) < cfg["e13"]["margin"],
              " ".join(f"{k}={v:+.3f}" for k, v in gains.items()) + f" on {len(use)} sessions", soft=True)

        # round 3 design 3.7: PCcal with lambda = 0 (noise only, on clock60) keeps the L300 gain below the margin
        conf = pt.Config("raw", "none", pt.Sched("fixed", cfg["pccal"]["interval_s"]), pc="PCcal", lam=0.0,
                         name_override="PCcal0")
        shape = {conf.name: np.vstack([pt.run(checks._session(sid), conf, cfg, 1, True, False)["windows"] for sid in sids])}
        xb = checks.attacker_sets(lab, shape, cfg)[conf.name]
        gains = {}
        for kind in ("hgb", "lr"):
            a0 = checks.weighted_auc(checks.oof_predict(lab["XA"], lab["Y"], lab["G"], kind, 1, cfg["e13"]["folds"]),
                                     lab["Y"], ones)
            for fs in ("full", "small"):
                pb = checks.oof_predict(xb[fs], lab["Y"], lab["G"], kind, 1, cfg["e13"]["folds"])
                gains[f"{fs}/{kind}"] = checks.weighted_auc(pb, lab["Y"], ones) - a0
        check("PCcal with lambda = 0 keeps the L300 gain below the margin",
              max(gains.values()) < cfg["e13"]["margin"],
              " ".join(f"{k}={v:+.3f}" for k, v in gains.items()) + f" on {len(use)} sessions", soft=True)

        # round 4 design 3.7: PCsize with lambda = 0 (the size level is noise) keeps the L300 point estimate
        # below the margin, for each form. Instrument check only: the verdicts use PCsize0 of the main run
        # (design 3.2, condition 3). These are sessions of the main run: nothing is changed on their values.
        fixed_s = pt.Sched("fixed", cfg["pcsize"]["interval_s"])
        for f in checks.forms(cfg):
            mp, dr = f.split("-")
            gains = l300_gains(pt.Config(mp, dr, fixed_s, pc="PCsize", lam=0.0, name_override=f"PCsize0-{f}"),
                               sids, lab, cfg)
            check(f"PCsize {f} with lambda = 0 keeps the L300 point estimate max below the margin",
                  max(gains.values()) < cfg["e13"]["margin"],
                  " ".join(f"{k}={v:+.3f}" for k, v in gains.items()) + f" on {len(use)} sessions", soft=True)

        # round 5 design 3.7: PCahead with lambda = 0 on its real scheduler, for each form and scheduler. Instrument
        # check only (the verdicts use PCahead0 of the main run: design 3.2, condition 3); nothing is changed on it.
        for sc in checks.scheds(cfg):
            for f in checks.forms(cfg):
                mp, dr = f.split("-")
                gains = l300_gains(pt.Config(mp, dr, sc, pc="PCahead", lam=0.0, name_override=f"PCahead0-{f}-{sc.name}"),
                                   sids, lab, cfg)
                check(f"PCahead {f}-{sc.name} with lambda = 0 keeps the L300 point estimate max below the margin",
                      max(gains.values()) < cfg["e13"]["margin"],
                      " ".join(f"{k}={v:+.3f}" for k, v in gains.items()) + f" on {len(use)} sessions", soft=True)

    # round 4 design 3.7: the raw PCsize walker does not stay at the edges (second half of each session, lambda = 1),
    # and the constant-heading mutation (the negative control) does
    fixed_s = pt.Sched("fixed", cfg["pcsize"]["interval_s"])
    W, H = cfg["canvas"]["w"], cfg["canvas"]["h"]

    def pinned_share(conf: pt.Config, m: dict) -> float:
        sess = pt.load_session(work, m)
        ups = pt.schedule(sess, conf.sched, cfg["scheduler_jitter_frac"], 1)
        vals = pt.oracle_values(sess, ups, conf, 1)
        g = pt.Generator(conf.mapping, conf.drift, cfg, sess.key_seed, conf.pc, conf.mutation, 1)
        prev = 0
        for k, u in enumerate(ups):
            g.update(pt.material_slice(sess, prev, int(u), False, vals[k]), int(u))
            prev = int(u)
        xy = np.asarray(g.mark_xy[len(g.mark_xy) // 2 :])
        if len(xy) == 0:
            return float("nan")
        edge = (np.isclose(xy[:, 0], 10) | np.isclose(xy[:, 0], W - 10) | np.isclose(xy[:, 1], 10)
                | np.isclose(xy[:, 1], H - 10))
        return float(edge.mean())

    p5 = [m for m in manifest if m["set"] == "P"][:5]
    walk = [pinned_share(pt.Config("raw", "none", fixed_s, pc="PCsize", lam=1.0), m) for m in p5]
    stuck = [pinned_share(pt.Config("raw", "none", fixed_s, pc="PCsize", lam=1.0, mutation="constant_heading"), m)
             for m in p5]
    check("PCsize raw: in the second half of each session, fewer than half of the marks sit at the edge clamp",
          all(np.isfinite(x) and x < 0.5 for x in walk), "shares " + " ".join(f"{x:.2f}" for x in walk), soft=True)
    check("PCsize raw: the constant-heading mutation pins at least one session (negative control)",
          any(np.isfinite(x) and x >= 0.5 for x in stuck), "shares " + " ".join(f"{x:.2f}" for x in stuck), soft=True)

    # design 3.8 (round 2, descriptive): does a jitter of +-50 ms keep the lattice classes?
    js = [m for m in manifest if m["set"] == "J"]
    if js:
        by_sid = {m["sid"]: m for m in manifest}
        same, tot = 0, 0
        for mj in js:
            ma = by_sid[f"Oa{mj['pair']:02d}"]
            hist = []
            for m in (ma, mj):
                g = pt.Generator("lattice", "none", cfg, m["key_seed"])
                sess = pt.load_session(work, m)
                prev = 0
                for u in pt.schedule(sess, default, cfg["scheduler_jitter_frac"], 1):
                    g.update(pt.material_slice(sess, prev, int(u)), int(u))
                    prev = int(u)
                hist.append(g.lat_hist)
            n = min(len(hist[0]), len(hist[1]))
            same += sum(hist[0][i] == hist[1][i] for i in range(n))
            tot += max(len(hist[0]), len(hist[1]))
        print(f"INFO  lattice classes kept under +-50 ms jitter: {same}/{tot} drawn updates ({len(js)} pairs)")

    print(f"\n{len(FAILED)} failed, {len(SOFT_FAILED)} soft-failed (round 5 design 3.7: write them to design "
          f"section 8; they do not stop the run){(': ' + '; '.join(SOFT_FAILED)) if SOFT_FAILED else ''}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
