"""Self-tests of the EH1 instruments (design 3.6, 3.8 and 7).

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
    gen = pt.Generator("raw", "none", cfg, 1)
    bad = dict(mat, p_stuck=np.zeros(50))
    try:
        gen.update(bad, 50)
        check("E1-1 generator refuses p_stuck", False)
    except ValueError:
        check("E1-1 generator refuses p_stuck", True)

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

    # --- statistics
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 2000)
    sc_ = rng.random(2000)
    w = rng.integers(1, 4, 2000).astype(float)
    from sklearn.metrics import roc_auc_score
    check("weighted_auc equals sklearn", abs(checks.weighted_auc(sc_, y, w) - roc_auc_score(y, sc_, sample_weight=w)) < 1e-9)
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

    print(f"\n{len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
