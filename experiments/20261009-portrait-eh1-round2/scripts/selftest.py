"""Self-tests of the EH1 round 2 instruments (design 3.6, 3.8 and 6; round 1 design 3.6, 3.8 and 7).

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
    check("E1-1 ORC adds only the oracle", set(pt.material_slice(s, 0, 50, False, True)) == set(pt.ALLOWED_MATERIAL) | {"oracle"})
    so = fake_session([1.0], 600)
    so.seg[100:250] = 1
    check("ORC: stall share of the 300 s before the update", abs(pt.material_slice(so, 0, 300, False, True)["oracle"][0] - 0.5) < 1e-12)
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
    cfl = dict(cfg, e13=dict(cfg["e13"], window_s=60, long_s=300))
    s = fake_session([5.0, 100.0, 400.0], 900)
    s.seg[0:250] = 1  # stall for 250 of the first 300 s
    ex, lab, actl, valid = pt.presence_features_long(s, cfl)
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
