"""Selftest of split.py and compare.py (design 3.7). Synthetic arrays only; no gse-replay, no generated sessions.

Copied from experiments/20261015-rhythm-stage-speed-cause-split/scripts/selftest_split.py (d282691d), changed for the
shape world (design 1.4, 1.5, 3.3 (j)): the settings are under config.json split; the check of the imported earlier
instrument is gone (split.py imports this task's checks and stage); added the r-side controls' names, specs and
reading, the planted level and var signals against the drops, git_state, and compare.py.

Usage: selftest_split.py <config.json>
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

import compare as cp
import split as sp

ck, st = sp.ck, sp.st
FAILS: list[str] = []
OK = [0]


def check(cond: bool, what: str) -> None:
    if cond:
        OK[0] += 1
    else:
        FAILS.append(what)


def raises(fn, *a) -> bool:
    try:
        fn(*a)
    except (ValueError, KeyError, SystemExit):
        return True
    return False


# ---------------------------------------------------------------------------

def stage_names(fs: str) -> list[str]:
    names = ck.feature_names(sp.LABEL)[-3 * len(st.FEAT_NAMES):]
    return names[: len(st.FEAT_NAMES)] if fs == "small" else names


def keep_ok(keep_fn, drop: list[str], fs: str, n_dropped: int) -> bool:
    names = stage_names(fs)
    kept = [names[i] for i in keep_fn(drop, fs)]
    gone = {n for n in names if (n[3:] if n[:3] in ("d1_", "d2_") else n) in set(drop)}
    return kept == [n for n in names if n not in gone] and len(names) - len(kept) == n_dropped


def t_keep(cfg: dict) -> None:
    drops = cfg["split"]["drops"]
    want = {"R2": (6, 2), "Rall": (30, 10), "A2": (6, 2)}
    check(set(drops) == set(want), f"the drop groups are {sorted(want)}")
    check(set(drops["Rall"]) == {n for n in st.FEAT_NAMES if n.startswith("r_")}, "Rall is every r_ quantity")
    check(drops["R2"] == ["r_absdiff", "r_sd"] and drops["A2"] == ["a_absdiff", "a_sd"], "R2 and A2 as the cause split")
    for g, (nfull, nsmall) in want.items():
        check(keep_ok(sp.keep_columns, drops[g], "full", nfull), f"{g} full drops {nfull} named columns")
        check(keep_ok(sp.keep_columns, drops[g], "small", nsmall), f"{g} small drops {nsmall} named columns")
    check(sp.keep_columns([], "full") == list(range(60)) and sp.keep_columns([], "small") == list(range(20)),
          "no drop keeps every column in order")
    check(raises(sp.keep_columns, ["r_nope"], "full"), "an unknown quantity is refused")

    def shifted(drop, fs):  # mutation: one index off
        return [min(i + 1, 59 if fs == "full" else 19) for i in sp.keep_columns(drop, fs)]
    check(not keep_ok(shifted, drops["R2"], "full", 6), "mutation: shifted indices are caught")

    def no_diffs(drop, fs):  # mutation: the differences not dropped
        k = [i for i, n in enumerate(st.FEAT_NAMES) if n not in set(drop)]
        return k if fs == "small" else k + list(range(20, 60))
    check(not keep_ok(no_diffs, drops["R2"], "full", 6), "mutation: d1_/d2_ left in are caught")


def synth_scratch(tmp: Path, n_sess: int = 12, per: int = 40, nb: int = 5, seed: int = 7, plant=None) -> dict:
    """A synthetic L300 table in the scratch layout of checks.label_tables / main_split. plant(F, y, rng) puts a
    signal into the stage features (default: r_absdiff + 0.7 y)."""
    rng = np.random.default_rng(seed)
    n = n_sess * per
    G = np.repeat(np.arange(n_sess), per)
    y = (rng.random(n) < 0.3).astype(int)
    S = rng.normal(size=(n, nb)) + 0.8 * y[:, None] * (np.arange(nb) == 0)
    S[:, 1] = np.where(rng.random(n) < 0.7, 0.0, rng.random(n))  # many repeated values
    S[rng.random(n) < 0.02, 2] = np.nan
    F = rng.normal(size=(n, len(st.FEAT_NAMES)))
    if plant is None:
        F[:, st.FEAT_NAMES.index("r_absdiff")] += 0.7 * y
    else:
        plant(F, y, rng)
    ck.save(tmp, f"{sp.LABEL}-S", S)
    ck.save(tmp, f"{sp.LABEL}-rows", np.arange(n))
    ck.save(tmp, f"{sp.LABEL}-G", G)
    ck.save(tmp, "G_all", G)
    ck.save(tmp, "F-0", F)
    return {"y": y, "G": G, "S": S, "F": F, "n_sess": n_sess}


def t_build_and_models(cfg: dict) -> None:
    bins = cfg["split"]["bins"]
    drops = cfg["split"]["drops"]
    tmp = Path(tempfile.mkdtemp(prefix="st-build-"))
    try:
        d = synth_scratch(tmp)
        sp._init(str(tmp))
        nb = d["S"].shape[1]
        for fs in sp.FS:
            full = ck.build_x(sp.LABEL, "S", "F-0", fs)
            X, nbb = sp.build("F-0", fs, drops["R2"])
            keep = sp.keep_columns(drops["R2"], fs)
            check(nbb == nb and np.array_equal(X[:, :nb], full[:, :nb], equal_nan=True),
                  f"build {fs}: the base columns are A_speed unchanged")
            check(np.array_equal(X[:, nb:], full[:, nb:][:, keep]), f"build {fs}: the stage block keeps the kept columns")
            X0, _ = sp.build("F-0", fs, [])
            check(np.array_equal(X0, full, equal_nan=True), f"build {fs}: no drop equals checks.build_x")
        Xb, _ = sp.build(None, None, [])
        check(np.array_equal(Xb, d["S"], equal_nan=True), "build of the base is A_speed")

        # lrbin: the bin edges come from the training rows only
        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import KBinsDiscretizer
        X, _ = sp.build("F-0", "small", [])
        tr = np.arange(len(X)) < len(X) * 3 // 4
        m = sp.make_lrbin(nb, X.shape[1] - nb, False, bins)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            m.fit(X[tr], d["y"][tr])
            ref = KBinsDiscretizer(n_bins=bins, encode="onehot-dense", strategy="quantile",
                                   quantile_method="averaged_inverted_cdf", subsample=None).fit(
                SimpleImputer(strategy="median").fit_transform(X[tr, :nb]))
        ct = m.steps[0][1]
        kb = ct.named_transformers_["base"].named_steps["u"].transformer_list[0][1]
        check(all(np.array_equal(a, b) for a, b in zip(kb.bin_edges_, ref.bin_edges_)),
              "lrbin: the bin edges are those of the training rows")
        check(len(kb.bin_edges_[1]) - 1 < bins, "lrbin: repeated values drop bins without failing")
        check(type(ct.named_transformers_["stage"]).__name__ == "SimpleImputer", "lrbin: the stage columns are not binned")
        m2 = sp.make_lrbin(nb, X.shape[1] - nb, True, bins)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            m2.fit(X[tr], d["y"][tr])
        check(type(m2.steps[0][1].named_transformers_["stage"]).__name__ == "Pipeline", "lrbin2: the stage columns are binned")
        Xt = m.steps[0][1].transform(X[~tr])
        check(Xt.shape[1] > X.shape[1], "lrbin: the one-hot columns are added next to the values")

        # the lr and hgb route equals checks.e13_target's (_fit_job + _boot_job) on the same multipliers
        y, G = d["y"], d["G"]
        mults = sp.multipliers(5, d["n_sess"], 50)
        rng = np.random.default_rng(np.random.SeedSequence([5, 313, ck.LABEL_ID["L300"]]))
        ref = [np.bincount(rng.integers(0, d["n_sess"], size=d["n_sess"]), minlength=d["n_sess"]).astype(float)
               for _ in range(50)]
        check(ck.LABEL_ID["L300"] == 0 and np.array_equal(mults, np.array(ref)),
              "multipliers: those of checks.e13_target for L300 (SeedSequence([seed, 313, 0]))")
        np.save(tmp / "mults.npy", mults)
        for kind in ("lr", "hgb"):
            sp._base_job((kind, y, 5, 3, bins))
        for fs in sp.FS:
            preds_b, preds_a = {}, {}
            for kind in ("lr", "hgb"):
                preds_b[(fs, kind)] = ck._fit_job((0, sp.LABEL, "S", "F-0", fs, kind, y, 5, 3, "pred"))[1]
                preds_a[kind] = ck._fit_job((0, sp.LABEL, "S", None, None, kind, y, 5, 3, "pred"))[1]
            _, boots = ck._boot_job(("x", preds_b, preds_a, y, G, list(mults)))
            for kind in ("lr", "hgb"):
                _, r = sp._fit_job((0, kind, "F-0", fs, [], y, 5, 3, bins))
                ones = np.ones(len(y))
                gain = ck.weighted_auc(preds_b[(fs, kind)], y, ones) - ck.weighted_auc(preds_a[kind], y, ones)
                b = boots[f"{fs}/{kind}"]
                ci = [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
                check(r["gain"] == gain and r["ci95"] == ci, f"{fs}/{kind}: split's gain and interval equal checks'")
        sp._base_job(("lrbin", y, 5, 3, bins))
        _, r = sp._fit_job((0, "lrbin", "F-0", "full", [], y, 5, 3, bins))
        _, r2 = sp._fit_job((0, "lrbin2", "F-0", "full", [], y, 5, 3, bins))
        check(math.isfinite(r["gain"]) and math.isfinite(r2["gain"]), "lrbin and lrbin2 fit")
        check((tmp / "base-lrbin.npy").exists() and not (tmp / "base-lrbin2.npy").exists(),
              "lrbin2 shares the base of lrbin")
        _, rd = sp._fit_job((0, "lr", "F-0", "full", drops["R2"], y, 5, 3, bins))
        _, rn = sp._fit_job((0, "lr", "F-0", "full", [], y, 5, 3, bins))
        check(rd["gain"] < rn["gain"], "dropping r_absdiff (the planted signal) lowers the gain")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def gains_by_drop(cfg: dict, plant, seed: int) -> dict:
    """design 3.7: the small/lr gain of a planted signal under each drop (none, R2, Rall, A2)."""
    bins = cfg["split"]["bins"]
    drops = {"none": [], **cfg["split"]["drops"]}
    tmp = Path(tempfile.mkdtemp(prefix="st-plant-"))
    try:
        d = synth_scratch(tmp, n_sess=24, per=60, seed=seed, plant=plant)
        sp._init(str(tmp))
        np.save(tmp / "mults.npy", sp.multipliers(5, d["n_sess"], 20))
        sp._base_job(("lr", d["y"], 5, 3, bins))
        return {k: sp._fit_job((0, "lr", "F-0", "small", v, d["y"], 5, 3, bins))[1]["gain"] for k, v in drops.items()}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def plant_level(F, y, rng):
    """The type of PCr-level: the level of r moves with the label (mean, quantiles, end)."""
    for n in ("r_mean", "r_p10", "r_p50", "r_p90", "r_end"):
        F[:, st.FEAT_NAMES.index(n)] += 0.6 * y


def plant_var(F, y, rng):
    """The type of PCr-var: the spread of r moves with the label (sd, mean |diff|, the outer quantiles apart)."""
    for n, s in (("r_sd", 0.6), ("r_absdiff", 0.6), ("r_p10", -0.3), ("r_p90", 0.3)):
        F[:, st.FEAT_NAMES.index(n)] += s * y


def t_planted(cfg: dict) -> None:
    """design 3.7: where the two r-side signal types live against the drops."""
    lv = gains_by_drop(cfg, plant_level, 11)
    check(lv["none"] > 0.05 and lv["R2"] > 0.03 and lv["Rall"] < 0.03,
          f"planted level: kept after R2 ({lv['R2']:+.3f}), gone after Rall ({lv['Rall']:+.3f})")
    va = gains_by_drop(cfg, plant_var, 12)
    check(va["none"] > 0.05 and va["R2"] < va["none"] and va["Rall"] < 0.03,
          f"planted var: lowered by R2 ({va['none']:+.3f} -> {va['R2']:+.3f}), gone after Rall ({va['Rall']:+.3f})")
    check(abs(lv["A2"] - lv["none"]) < 0.02, "planted level: A2 (the a side) leaves it")


def t_gate(cfg: dict) -> None:
    tol = cfg["split"]["gate_tol"]
    prev = {"auc_A_speed": {"hgb": 0.9, "lr": 0.8},
            "configs": {n: {"attackers": {a: {"gain": 0.05, "ci95": [0.04, 0.06]} for a in ("full/lr", "small/hgb")}}
                        for n in ("S-a", "PCs-S-a")}}

    def got_of(delta: float = 0.0, drop_name: bool = False, nan: bool = False) -> dict:
        g = json.loads(json.dumps({"auc_A_speed": prev["auc_A_speed"],
                                   "configs": {n: {a: {"gain": r["gain"], "ci95": r["ci95"]}
                                                   for a, r in v["attackers"].items()}
                                               for n, v in prev["configs"].items()}}))
        g["configs"]["S-a"]["full/lr"]["ci95"][1] += delta
        if nan:
            g["configs"]["S-a"]["small/hgb"]["gain"] = float("nan")
        if drop_name:
            g["configs"]["S-new"] = {"full/lr": {"gain": 0.0, "ci95": [0.0, 0.0]}}
        return g
    names, atk = ["S-a", "PCs-S-a"], ["full/lr", "small/hgb"]

    def gt(g, n=names, a=atk):
        return sp.gate(prev, g, tol, n, a)
    r = gt(got_of())
    check(r["ok"] and r["n_compared"] == r["n_expected"] == 2 + 3 * 4, "gate: equal values pass, every value compared")
    g = got_of()
    del g["configs"]["PCs-S-a"]
    check(not gt(g)["ok"], "gate: a name missing from the rebuilt values stops")
    g = got_of()
    del g["configs"]["S-a"]["small/hgb"]
    check(not gt(g)["ok"], "gate: an attacker missing from the rebuilt values stops")
    g = got_of()
    del g["auc_A_speed"]["hgb"]
    check(not gt(g)["ok"], "gate: a missing AUC(A_speed) stops")
    check(not gt(got_of(), names + ["S-b"])["ok"], "gate: an expected name absent from both stops")
    check(gt(got_of(0.5 * tol))["ok"], "gate: a difference within tol passes")
    check(not gt(got_of(2 * tol))["ok"], "gate: a difference over tol stops")
    check(not gt(got_of(drop_name=True))["ok"], "gate: an unexpected name in the rebuilt values stops")
    for what, cut in (("a name", lambda q: q["configs"].pop("PCs-S-a")),
                      ("an attacker", lambda q: q["configs"]["S-a"]["attackers"].pop("small/hgb")),
                      ("AUC(A_speed) of hgb", lambda q: q["auc_A_speed"].pop("hgb"))):
        prev2 = json.loads(json.dumps(prev))
        cut(prev2)
        r2 = sp.gate(prev2, got_of(), tol, names, atk)
        check(not r2["ok"] and r2["missing"], f"gate: {what} missing from e13.json stops (and is listed as missing)")
    check(not gt(got_of(nan=True))["ok"], "gate: a NaN stops")
    check(not gt({"auc_A_speed": {}, "configs": {}})["ok"], "gate: nothing compared stops")
    check(not sp.gate(prev, {"auc_A_speed": {}, "configs": {}}, tol, [], [], ())["ok"], "gate: an empty expectation stops")
    g = got_of()
    g["auc_A_speed"]["lr"] += 1e-6
    check(not gt(g)["ok"], "gate: AUC(A_speed) is compared")
    # the gate reads the shape of this task's e13.json: L300 -> configs -> name -> attackers
    e13_like = {"L300": {"auc_A_speed": prev["auc_A_speed"], "configs": {
        n: {"attackers": v["attackers"], "verdict": "green"} for n, v in prev["configs"].items()}}}
    check(sp.gate(e13_like["L300"], got_of(), tol, names, atk)["ok"], "gate: the e13.json layout of checks.main_run passes")


def mx(lo, hi, gain=None):
    g = (lo + hi) / 2 if gain is None else gain
    return {"gain_max": g, "lower_max": lo, "upper_max": hi, "n_nan": sum(math.isnan(x) for x in (g, lo, hi))}


def t_read(cfg: dict) -> None:
    rd = cfg["split"]["read"]
    m, pl, pu = rd["margin"], rd["pc_lower"], rd["pc_upper"]
    check(m == 0.03 and pl == 0.03 and pu == 0.08 and rd["pcr_upper"] == 0.08,
          "the reading thresholds are 0.03 and 0.08 (design 3.3 (j))")
    pcs, pc0 = mx(0.04, 0.07), mx(-0.01, 0.01)
    check(sp.reading(mx(0.031, 0.05), pcs, pc0, m, pl, pu) == "remains", "remains above 0.03")
    check(sp.reading(mx(0.03, 0.05), pcs, pc0, m, pl, pu) == "undetermined", "a lower bound of exactly 0.03 does not remain")
    check(sp.reading(mx(0.0, 0.029), pcs, pc0, m, pl, pu) == "vanishes", "vanishes below 0.03")
    check(sp.reading(mx(0.0, 0.03), pcs, pc0, m, pl, pu) == "undetermined", "an upper bound of exactly 0.03 does not vanish")
    check(sp.reading(mx(0.04, 0.05), mx(0.03, 0.07), pc0, m, pl, pu) == "unreadable", "PC-stall lower 0.03 is unreadable")
    check(sp.reading(mx(0.04, 0.05), pcs, mx(0.0, 0.03), m, pl, pu) == "unreadable", "PC0 upper 0.03 is unreadable")
    check(sp.reading(mx(0.04, 0.05), mx(0.07, 0.11), pc0, m, pl, pu) == "unreadable",
          "a PC-stall point estimate above 0.08 is unreadable")
    check(sp.reading(mx(0.04, 0.05), mx(0.06, 0.10), pc0, m, pl, pu) == "remains",
          "a PC-stall point estimate of exactly 0.08 is readable")
    nan = float("nan")
    check(sp.reading(mx(nan, nan), pcs, pc0, m, pl, pu) == "undetermined", "a NaN candidate is undetermined")
    check(sp.reading(mx(0.04, 0.05), mx(nan, nan), pc0, m, pl, pu) == "unreadable", "a NaN PC-stall is unreadable")
    check(sp.reading(mx(0.04, 0.05), pcs, mx(nan, nan), m, pl, pu) == "unreadable", "a NaN PC0 is unreadable")
    check(sp.reading(mx(nan, 0.02, 0.01), pcs, pc0, m, pl, pu) == "undetermined",
          "a candidate with a NaN lower bound only does not vanish")
    check(sp.reading(mx(0.04, nan, 0.05), pcs, pc0, m, pl, pu) == "undetermined",
          "a candidate with a NaN upper bound only does not remain")
    check(sp.reading(mx(0.04, 0.05, nan), pcs, pc0, m, pl, pu) == "undetermined",
          "a candidate with a NaN point estimate only is undetermined")
    check(sp.reading(mx(0.04, 0.05), mx(0.04, nan, 0.05), pc0, m, pl, pu) == "unreadable",
          "a PC-stall with a NaN upper bound only is unreadable")
    check(sp.reading(mx(0.04, 0.05), pcs, mx(-0.01, 0.01, nan), m, pl, pu) == "unreadable",
          "a PC0 with a NaN point estimate only is unreadable")
    a = {"full/lr": {"gain": 0.02, "ci95": [0.01, 0.05]}, "small/lr": {"gain": 0.03, "ci95": [0.0, 0.04]}}
    check(sp.maxima(a) == {"gain_max": 0.03, "lower_max": 0.01, "upper_max": 0.05, "n_nan": 0},
          "maxima over the two attackers")
    for order in ("full first", "small first"):
        b = {"full/lr": {"gain": 0.05, "ci95": [0.04, 0.06]}, "small/lr": {"gain": 0.02, "ci95": [nan, 0.03]}}
        if order == "small first":
            b = dict(reversed(list(b.items())))
        mm = sp.maxima(b)
        check(math.isnan(mm["lower_max"]) and mm["n_nan"] == 1 and mm["upper_max"] == 0.06,
              f"maxima: a NaN of one attacker makes the maximum NaN ({order})")
        check(sp.reading(mm, pcs, pc0, m, pl, pu) == "undetermined", f"a NaN lower bound never remains ({order})")
        check(sp.reading(mx(0.04, 0.05), mm, pc0, m, pl, pu) == "unreadable",
              f"a PC-stall with a NaN lower bound is unreadable ({order})")
    v = sp.variants()
    check(len(v) == 13 and ("lrbin2", "none") in v and not any(m_ == "lrbin2" and d != "none" for m_, d in v),
          "13 variants; lrbin2 without drops")


def t_pcr(cfg: dict) -> None:
    """design 3.3 (j): the r-side controls' reading, variants and specs."""
    rd = cfg["split"]["read"]
    m, u = rd["margin"], rd["pcr_upper"]
    base = mx(-0.01, 0.01)
    rr = lambda ctl, b=base: sp.pcr_reading(ctl, b, m, u)
    nan = float("nan")
    check(rr(mx(0.031, 0.07, 0.05)) == "works", "pcr: lower above 0.03, gain <= 0.08 -> works")
    check(rr(mx(0.031, 0.12, 0.08)) == "works", "pcr: a gain of exactly 0.08 works")
    check(rr(mx(0.031, 0.12, 0.0801)) == "over", "pcr: a gain above 0.08 -> over")
    check(rr(mx(0.03, 0.07)) == "unclear", "pcr: a lower bound of exactly 0.03 does not work")
    check(rr(mx(-0.01, 0.029)) == "fails", "pcr: upper below 0.03 -> fails")
    check(rr(mx(-0.01, 0.03)) == "unclear", "pcr: an upper bound of exactly 0.03 does not fail")
    check(rr(mx(0.04, 0.07), mx(0.0, 0.03)) == "unreadable", "pcr: its baseline's upper bound of exactly 0.03 -> unreadable")
    check(rr(mx(0.04, 0.07), mx(0.0, 0.029)) == "works", "pcr: its baseline below 0.03 is fine")
    check(rr(mx(nan, 0.07, 0.05)) == "unreadable", "pcr: a NaN in the control -> unreadable")
    check(rr(mx(0.04, 0.07), mx(-0.01, 0.01, nan)) == "unreadable", "pcr: a NaN in its baseline -> unreadable")
    check(rr(None) == "not_calibrated" and rr(mx(0.04, 0.07), None) == "not_calibrated",
          "pcr: no lambda (not fitted) -> not_calibrated")
    # mutation: the comparisons swapped would make a failing control work
    check(rr(mx(-0.05, -0.01)) != "works", "pcr: a control below 0 never works")
    pv = sp.pcr_variants(cfg)
    check(pv == [(mm, d) for mm in sp.MODELS for d in ("none", "R2")] and len(pv) == 6,
          "pcr: 6 variants (lr, hgb, lrbin x none, R2; no Rall: cross-review 1)")
    for drops in (["none", "A2"], ["none", "R2", "Rall"], ["R2"]):
        bad = json.loads(json.dumps(cfg))
        bad["split"]["pcr_drops"] = drops
        check(raises(sp.pcr_variants, bad), f"pcr: pcr_drops {drops} is refused")
    cands = st.candidates()
    lam_r = {"level": {c: 0.1 for c in cands}, "var": {c: (None if i % 3 == 0 else 0.2) for i, c in enumerate(cands)}}
    specs = sp.pcr_specs(lam_r)
    n_var = sum(v is not None for v in lam_r["var"].values())
    check(len(specs) == 2 * (24 + n_var) and len({k for k, _, _ in specs}) == len(specs),
          "pcr: a control and its baseline per family and candidate with a lambda; none for a null")
    check(all((lam == 0.0) == ("0-" in name) for _, name, lam in specs), "pcr: the baselines are at lambda 0, the controls not")
    check(all(name.startswith(st.PCR_PREFIXES) for _, name, _ in specs), "pcr: every spec name is an r-side control")
    check(("PCrl-S-raw-hold-sec", "PCrl-S-raw-hold-sec", 0.1) in specs
          and not any(n == f"PCrv-{cands[0]}" for _, n, _ in specs), "pcr: the null var lambda of the first candidate is not fitted")
    names = st.pcr_names(cands)
    check(sorted(names) == ["level", "var"] and names["level"][cands[0]] == (f"PCrl-{cands[0]}", f"PCrl0-{cands[0]}")
          and names["var"][cands[0]] == (f"PCrv-{cands[0]}", f"PCrv0-{cands[0]}"), "pcr: the names per family")
    check(all(ck.kind_of(n, t) == "descriptive" for fam in names.values() for pair in fam.values() for n in pair
              for t in ("L300", "L60", "L1800")), "pcr: the r-side controls are descriptive on every label (never judged)")


def t_versions(cfg: dict) -> None:
    check(sp.package_problems(cfg) == [], f"the versions are the copied instruments': {sp.package_problems(cfg)}")
    bad = json.loads(json.dumps(cfg))
    bad["split"]["versions"]["sklearn"] = "0.0.0"
    check(len(sp.package_problems(bad)) == 1, "another scikit-learn version is caught")


def t_git_state() -> None:
    """design 1.4: git_state leaves results/ out (negative control: a change under scripts/ counts)."""
    tmp = Path(tempfile.mkdtemp(prefix="st-git-"))
    old = sp.EXP_DIR
    try:
        run = lambda *a: subprocess.run(["git", *a], cwd=tmp, capture_output=True, text=True, check=True)
        run("init", "-q")
        run("config", "user.email", "x@example.invalid")
        run("config", "user.name", "x")
        (tmp / "scripts").mkdir()
        (tmp / "scripts" / "a.py").write_text("1\n", encoding="utf-8")
        run("add", "scripts/a.py")
        run("commit", "-q", "-m", "x")
        sp.EXP_DIR = tmp
        check(sp.git_state()["dirty"] is False, "git_state: a clean tree is not dirty")
        (tmp / "results" / "d100" / "main").mkdir(parents=True)
        (tmp / "results" / "d100" / "main" / "e13.json").write_text("{}", encoding="utf-8")
        check(sp.git_state()["dirty"] is False, "git_state: untracked results/ are not counted")
        (tmp / "scripts" / "a.py").write_text("2\n", encoding="utf-8")
        check(sp.git_state()["dirty"] is True, "git_state: a change under scripts/ is counted (negative control)")
    finally:
        sp.EXP_DIR = old
        shutil.rmtree(tmp, ignore_errors=True)


def t_compare(cfg: dict) -> None:
    """design 1.5: the comparison copies what it reads; a step that did not run is not_run, never green."""
    cands = st.candidates()

    def summ(v300):  # the first two candidates as given, the other 22 green
        v = list(v300) + ["green"] * (len(cands) - len(v300))
        return {**{c: {"L300": x, "L60": "green", "L1800": "green"} for c, x in zip(cands, v)}, "_x": {}}
    e13 = {t: {"auc_A_speed": {"hgb": 0.8, "lr": 0.7}} for t in cp.LABELS}
    pcr = {f"{m}|{d}": {f: {c: "works" for c in cands} for f in ("level", "var")} for m in sp.MODELS for d in ("none", "R2")}
    split = {"counts": {"lr|R2": {}}, "readings": {k: {c: "vanishes" for c in cands} for k in cp.R2_KEYS},
             "pcr_counts": {}, "pcr_readings": pcr, "main_ceiling_kinds_L300": []}
    col_ceiling = cp.world_column("ceiling", None, None, None)
    check(col_ceiling == {"status": "ceiling", "ran": False, "state": "not_run"}, "compare: a ceiling step is not_run")
    col_nomain = cp.world_column("go", None, None, None)
    check(not col_nomain["ran"], "compare: a go step with no main run is not_run")
    red = cp.world_column("go", summ(["red_detected", "green"]), e13, split, "h", "h")
    green = cp.world_column("go", summ(["green", "green"]), e13, None)
    check(red["state"] == "red" and green["state"] == "clean" and green["split"] == "not_run"
          and isinstance(red["split"], dict), "compare: red and clean are copied; a missing split is not_run")
    stale = cp.world_column("go", summ(["red_detected", "green"]), e13, split, "old", "new")
    nosha = cp.world_column("go", summ(["red_detected", "green"]), e13, split, None, "new")
    check(stale["split"] == "stale" and nosha["split"] == "stale",
          "compare: a split whose gate read another e13.json (or none) is stale (cross-review 1)")
    check(red["verdict_counts"]["L300"]["red_detected"] == 1 and red["verdict_counts"]["L300"]["green"] == 23,
          "compare: the counts follow the verdicts")
    stop = cp.world_column("go", summ(["red_detected_stop_path", "green"]), e13, None)
    check(stop["state"] == "red", "compare: red_detected_stop_path counts as red")
    for vs in (["red_unconfirmed", "green"], ["undecidable", "green"], ["undecidable", "undecidable"]):
        check(cp.world_column("go", summ(vs), e13, None)["state"] == "unsettled",
              f"compare: {vs} is unsettled, not no red (cross-review 1)")
    h = red
    unset = cp.world_column("go", summ(["undecidable", "undecidable"]), e13, None)
    check(cp.reading_i(h, green, red) == "red_in_drift_only" and cp.reading_i(h, red, green) == "red_in_factor_only"
          and cp.reading_i(h, red, red) == "red_in_both" and cp.reading_i(h, green, green) == "red_in_neither",
          "compare: the table of design 3.3 (i)")
    check(cp.reading_i(h, col_ceiling, red) == "not_run" and cp.reading_i(h, green, col_nomain) == "not_run",
          "compare: no reading when either world did not run (mutation: not_run read as green)")
    check(cp.reading_i(h, unset, red) == "unsettled" and cp.reading_i(h, red, unset) == "unsettled",
          "compare: no reading when either world is unsettled (all undecidable is not clean)")
    check(cp.reading_i(green, green, red) == "no_target" and cp.reading_i(unset, green, red) == "confound_unsettled"
          and cp.reading_i(col_ceiling, green, red) == "confound_not_run",
          "compare: no reading when the confound world itself has no red there (and why)")
    check(raises(cp.world_state, {c: "green" for c in cands[:23]})
          and raises(cp.world_state, {**{c: "green" for c in cands}, "S-extra-x-y": "green"}),
          "compare: a summary without exactly the 24 candidates stops (not clean: cross-review 2)")
    # design 3.3 (j) (cross-review 2): a control's R2 reading is used only when the same model and family work at none
    # and the model was not at the ceiling
    sp2 = json.loads(json.dumps(split))
    sp2["pcr_readings"]["lr|none"]["var"][cands[0]] = "fails"
    sp2["pcr_readings"]["lr|R2"]["var"][cands[0]] = "fails"
    sp2["pcr_readings"]["lrbin|none"]["level"][cands[1]] = "over"
    sp2["main_ceiling_kinds_L300"] = ["hgb"]
    t = cp.pcr_r2_table(sp2)
    check(t["lr|R2"]["var"][cands[0]] == {"none": "fails", "R2": "fails", "used": False, "why": "none_not_working"}
          and t["lr|R2"]["level"][cands[0]]["used"] and t["lrbin|R2"]["level"][cands[1]]["used"]
          and all(not v["used"] and v["why"] == "ceiling" for f in t["hgb|R2"].values() for v in f.values()),
          "compare: the R2 reading of a control is not used when its none does not work or its model was at the ceiling")
    col = cp.world_column("go", summ(["red_detected", "green"]), e13, sp2, "h", "h")
    check(col["split"]["main_ceiling_kinds_L300"] == ["hgb"] and col["split"]["pcr_R2"] == t,
          "compare: the column carries the ceiling and the table of used readings")
    t_compare_build(cfg, summ, e13, split)
    check(sorted(cfg["compare"]["pairs"]) == ["1", "2"]
          and all(set(v) == {"confound", "factor", "drift"} for v in cfg["compare"]["pairs"].values())
          and all(cfg["ceiling"]["worlds"][v[w]] == w for v in cfg["compare"]["pairs"].values() for w in ("factor", "drift"))
          and all(cfg["ceiling"]["steps"][v["factor"]] == cfg["ceiling"]["steps"][v["drift"]] == float(c)
                  for c, v in cfg["compare"]["pairs"].items()),
          "compare: the pairs put the factor and drift steps of the same c next to the confound world's")
    exp_root = Path(sp.EXP_DIR).parent
    check(cp.load_prev(cfg, exp_root).keys() == cfg["compare"]["prev_sha256"].keys(),
          "compare: the earlier tasks' files match their SHA-256")
    bad = json.loads(json.dumps(cfg))
    k0 = next(iter(bad["compare"]["prev_sha256"]))
    bad["compare"]["prev_sha256"][k0] = "0" * 64
    check(raises(cp.load_prev, bad, exp_root), "compare: a SHA-256 that does not match stops")


def t_compare_build(cfg: dict, summ, e13: dict, split: dict) -> None:
    """compare.build on a made-up results directory: the worlds of ceiling.json, the stale split, a not-run step."""
    tmp = Path(tempfile.mkdtemp(prefix="st-cmp-"))
    try:
        steps = cfg["ceiling"]["steps"]
        ceil = {"steps": {s: {"world": cfg["ceiling"]["worlds"][s], "c": c, "status": "ceiling" if s == "f100" else "go"}
                          for s, c in steps.items()}}
        (tmp / "results" / "ceiling").mkdir(parents=True)
        (tmp / "results" / "ceiling" / "ceiling.json").write_text(json.dumps(ceil), encoding="utf-8")
        for s in ("f200", "d100", "d200"):
            m = tmp / "results" / s / "main"
            m.mkdir(parents=True)
            (m / "summary.json").write_text(json.dumps(summ(["red_detected" if s == "d200" else "green", "green"])),
                                            encoding="utf-8")
            (m / "e13.json").write_text(json.dumps(e13), encoding="utf-8")
            sd = tmp / "results" / s / "split"
            sd.mkdir(parents=True)
            (sd / "split.json").write_text(json.dumps(split), encoding="utf-8")
            sha = cp.sha256(m / "e13.json") if s != "d100" else "0" * 64
            (sd / "reproduce.json").write_text(json.dumps({"e13_sha256": sha}), encoding="utf-8")
        prev = cp.load_prev(cfg, Path(sp.EXP_DIR).parent)
        doc = cp.build(cfg, tmp, prev)
        w1, w2 = doc["by_c"]["1"]["worlds"], doc["by_c"]["2"]["worlds"]
        check(w1["factor"]["state"] == "not_run" and w1["drift"]["split"] == "stale" and doc["by_c"]["1"]["reading_i"]
              == "not_run" and w1["confound"]["step"] == "c100" and w1["confound"]["ran"],
              "compare build: f100 at the ceiling is not_run, d100's split is stale, the confound column is c100's")
        check(doc["by_c"]["2"]["reading_i"] == "red_in_drift_only" and isinstance(w2["drift"]["split"], dict),
              "compare build: c = 2 reads the factor (clean) and drift (red) columns")
        bad = json.loads((tmp / "results" / "ceiling" / "ceiling.json").read_text(encoding="utf-8"))
        bad["steps"]["d100"]["world"] = "factor"
        (tmp / "results" / "ceiling" / "ceiling.json").write_text(json.dumps(bad), encoding="utf-8")
        check(raises(cp.build, cfg, tmp, prev), "compare build: a step whose world differs in ceiling.json stops")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for t in (t_versions, t_keep, t_build_and_models, t_planted, t_gate, t_read, t_pcr, t_compare):
        t(cfg)
    t_git_state()
    for f in FAILS:
        print(f"FAIL: {f}")
    print(f"selftest_split: ok {OK[0]}, failed {len(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
