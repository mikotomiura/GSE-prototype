"""Self-tests of the EH1 round 3 instruments (design 3.7; round 2 design 3.6 and 3.8; round 1 design 3.6, 3.8
and 7).

Usage: selftest.py <config.json> <work dir with at least the smoke sessions>
Exit 0 when every test passes.
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


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'PASS' if cond else 'FAIL'}  {name}{('  ' + detail) if detail else ''}")
    if not cond:
        FAILED.append(name)


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

    # --- names and verdicts (round 3 design 3.1-3.4)
    check("kind_of: PCcal, PCcal0, the grid and the oracles are not judged as configurations",
          [checks.kind_of(x) for x in ("PC1", "PCcal", "PCcal0", "PCcal@0.35", "ORC300-I300-W5",
                                        "ORCgap-I300-W5-recent60", "ORCcum-I300-W5", "raw-none-I300-W5")]
          == ["pc1", "pccal", "descriptive", "descriptive", "oracle", "oracle", "oracle", "config"])
    C = checks.configs(dict(cfg, pccal=dict(cfg["pccal"], lam=0.4)))
    names = [c.name for c in C["main"] + [C["pc1"], C["pccal"], C["pccal0"]] + C["orc"]]
    check("configs: 8 configurations, PC1, PCcal, PCcal0, 6 oracles, unique names",
          len(names) == 17 and len(set(names)) == 17 and sum(checks.kind_of(x) == "config" for x in names) == 8,
          str(names))

    def rec(up: float, lo: float, gain: float, nan: int = 0) -> dict:
        return {"upper_max": up, "lower_max": lo, "gain_max": gain, "n_nan_bounds": nan}

    def base_recs() -> dict:
        return {"PC1": rec(0.3, 0.2, 0.25), "PCcal": rec(0.07, 0.04, 0.05), "PCcal0": rec(0.01, -0.01, 0.0),
                "ORC300-I300-W5": rec(0.02, 0.0, 0.01), "raw-none-I300-W5": rec(0.029, 0.0, 0.01),
                "raw-none-I300-W5-recent60": rec(0.03, 0.0, 0.01)}

    nulls = {k: 0.01 for k in base_recs()}
    j = checks.judge(base_recs(), nulls, cfg, False)
    check("judge: everything works -> green below 0.03, red at 0.03 exactly, oracle narrow",
          j["detector_ok"] and j["verdicts"]["raw-none-I300-W5"] == "green"
          and j["verdicts"]["raw-none-I300-W5-recent60"] == "red"
          and j["verdicts"]["ORC300-I300-W5"] == "channel_narrow" and j["verdicts"]["PCcal0"] == "descriptive",
          str(j))
    cases = [
        ("PC1 lower 0.10 exactly fails", {"PC1": rec(0.3, 0.10, 0.2)}, nulls, ["weak_detector"]),
        ("PCcal lower 0.03 exactly fails", {"PCcal": rec(0.07, 0.03, 0.05)}, nulls, ["weak_detector"]),
        ("PCcal point 0.08 exactly works", {"PCcal": rec(0.1, 0.04, 0.08)}, nulls, []),
        ("PCcal point above 0.08 fails", {"PCcal": rec(0.1, 0.06, 0.0801)}, nulls, ["weak_detector"]),
        ("null 0.03 exactly fails", {}, dict(nulls, PCcal0=0.03), ["null"]),
        ("a NaN bound anywhere: the label is undecidable", {"PCcal0": rec(float("nan"), 0.0, 0.0, 1)}, nulls, ["nan"]),
    ]
    for name, patch, nl, reasons in cases:
        jj = checks.judge({**base_recs(), **patch}, nl, cfg, False)
        ok = jj["reasons"] == reasons and (jj["detector_ok"] == (not reasons))
        ok = ok and (jj["verdicts"]["raw-none-I300-W5"] == ("green" if not reasons else "undecidable"))
        if "nan" in reasons:
            ok = ok and jj["verdicts"]["ORC300-I300-W5"] == "undecidable"
        check(f"judge: {name}", ok, str(jj["reasons"]))
    jj = checks.judge({**base_recs(), "PCcal": rec(0.07, 0.02, 0.05)}, nulls, cfg, False)
    check("judge: an oracle is not narrow when PCcal fails", jj["verdicts"]["ORC300-I300-W5"] == "channel_partial")
    jj = checks.judge({}, None, cfg, True)
    check("judge: a failed fit makes the label undecidable", not jj["detector_ok"] and "fit_failed" in jj["reasons"])

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
              f"gain hgb={gains[0]:+.3f} lr={gains[1]:+.3f} on {len(use)} sessions")

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
              " ".join(f"{k}={v:+.3f}" for k, v in gains.items()) + f" on {len(use)} sessions")

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
              " ".join(f"{k}={v:+.3f}" for k, v in gains.items()) + f" on {len(use)} sessions")

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

    print(f"\n{len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
