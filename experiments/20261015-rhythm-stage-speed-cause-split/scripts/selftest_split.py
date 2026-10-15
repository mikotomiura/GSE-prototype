"""Selftest of split.py (design 3.6). Synthetic arrays only; no gse-replay, no generated sessions.

Usage: selftest_split.py <config.json>
"""

from __future__ import annotations

import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

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

def t_prev(cfg: dict) -> None:
    check(sp.prev_problems(cfg) == [], f"the confound world's instrument matches config.json: {sp.prev_problems(cfg)}")
    tmp = Path(tempfile.mkdtemp(prefix="st-prev-"))
    try:
        for rel in cfg["prev"]["sha256"]:
            (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(sp.PREV_DIR / rel, tmp / rel)
        check(sp.prev_problems(cfg, tmp) == [], "a faithful copy passes")
        p = tmp / "scripts" / "checks.py"
        b = bytearray(p.read_bytes())
        b[-2] ^= 1
        p.write_bytes(bytes(b))
        check(any("checks.py" in x for x in sp.prev_problems(cfg, tmp)), "one byte changed in checks.py is caught")
        shutil.copyfile(sp.PREV_DIR / "scripts" / "checks.py", p)
        (tmp / "scripts" / "extra.py").write_text("", encoding="utf-8")
        check(any("extra.py" in x for x in sp.prev_problems(cfg, tmp)), "an extra script is caught")
        (tmp / "scripts" / "extra.py").unlink()
        (tmp / "results" / "c100" / "main" / "e13.json").unlink()
        check(any("missing" in x for x in sp.prev_problems(cfg, tmp)), "a missing e13.json is caught")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = json.loads(json.dumps(cfg))
    bad["prev"]["dir"] = "../elsewhere"
    check(any("prev.dir" in x for x in sp.prev_problems(bad)), "a prev.dir other than the imported one is caught")


def stage_names(fs: str) -> list[str]:
    names = ck.feature_names(sp.LABEL)[-3 * len(st.FEAT_NAMES):]
    return names[: len(st.FEAT_NAMES)] if fs == "small" else names


def keep_ok(keep_fn, drop: list[str], fs: str, n_dropped: int) -> bool:
    names = stage_names(fs)
    kept = [names[i] for i in keep_fn(drop, fs)]
    gone = {n for n in names if (n[3:] if n[:3] in ("d1_", "d2_") else n) in set(drop)}
    return kept == [n for n in names if n not in gone] and len(names) - len(kept) == n_dropped


def t_keep(cfg: dict) -> None:
    want = {"R2": (6, 2), "Rall": (30, 10), "A2": (6, 2)}
    check(set(cfg["drops"]) == set(want), f"the drop groups are {sorted(want)}")
    check(set(cfg["drops"]["Rall"]) == {n for n in st.FEAT_NAMES if n.startswith("r_")}, "Rall is every r_ quantity")
    for g, (nfull, nsmall) in want.items():
        check(keep_ok(sp.keep_columns, cfg["drops"][g], "full", nfull), f"{g} full drops {nfull} named columns")
        check(keep_ok(sp.keep_columns, cfg["drops"][g], "small", nsmall), f"{g} small drops {nsmall} named columns")
    check(sp.keep_columns([], "full") == list(range(60)) and sp.keep_columns([], "small") == list(range(20)),
          "no drop keeps every column in order")
    check(raises(sp.keep_columns, ["r_nope"], "full"), "an unknown quantity is refused")

    def shifted(drop, fs):  # mutation: one index off
        return [min(i + 1, 59 if fs == "full" else 19) for i in sp.keep_columns(drop, fs)]
    check(not keep_ok(shifted, cfg["drops"]["R2"], "full", 6), "mutation: shifted indices are caught")

    def no_diffs(drop, fs):  # mutation: the differences not dropped
        k = [i for i, n in enumerate(st.FEAT_NAMES) if n not in set(drop)]
        return k if fs == "small" else k + list(range(20, 60))
    check(not keep_ok(no_diffs, cfg["drops"]["R2"], "full", 6), "mutation: d1_/d2_ left in are caught")


def synth_scratch(tmp: Path, n_sess: int = 12, per: int = 40, nb: int = 5, seed: int = 7) -> dict:
    """A synthetic L300 table in the scratch layout of checks.label_tables / main_split."""
    rng = np.random.default_rng(seed)
    n = n_sess * per
    G = np.repeat(np.arange(n_sess), per)
    y = (rng.random(n) < 0.3).astype(int)
    S = rng.normal(size=(n, nb)) + 0.8 * y[:, None] * (np.arange(nb) == 0)
    S[:, 1] = np.where(rng.random(n) < 0.7, 0.0, rng.random(n))  # many repeated values (design 3.6)
    S[rng.random(n) < 0.02, 2] = np.nan
    F = rng.normal(size=(n, len(st.FEAT_NAMES)))
    F[:, st.FEAT_NAMES.index("r_absdiff")] += 0.7 * y
    ck.save(tmp, f"{sp.LABEL}-S", S)
    ck.save(tmp, f"{sp.LABEL}-rows", np.arange(n))
    ck.save(tmp, f"{sp.LABEL}-G", G)
    ck.save(tmp, "G_all", G)
    ck.save(tmp, "F-0", F)
    return {"y": y, "G": G, "S": S, "F": F, "n_sess": n_sess}


def t_build_and_models(cfg: dict) -> None:
    tmp = Path(tempfile.mkdtemp(prefix="st-build-"))
    try:
        d = synth_scratch(tmp)
        sp._init(str(tmp))
        nb = d["S"].shape[1]
        for fs in sp.FS:
            full = ck.build_x(sp.LABEL, "S", "F-0", fs)
            X, nbb = sp.build("F-0", fs, cfg["drops"]["R2"])
            keep = sp.keep_columns(cfg["drops"]["R2"], fs)
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
        m = sp.make_lrbin(nb, X.shape[1] - nb, False, cfg["bins"])
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            m.fit(X[tr], d["y"][tr])
            ref = KBinsDiscretizer(n_bins=cfg["bins"], encode="onehot-dense", strategy="quantile",
                                   quantile_method="averaged_inverted_cdf", subsample=None).fit(
                SimpleImputer(strategy="median").fit_transform(X[tr, :nb]))
        ct = m.steps[0][1]
        kb = ct.named_transformers_["base"].named_steps["u"].transformer_list[0][1]
        check(all(np.array_equal(a, b) for a, b in zip(kb.bin_edges_, ref.bin_edges_)),
              "lrbin: the bin edges are those of the training rows")
        check(len(kb.bin_edges_[1]) - 1 < cfg["bins"], "lrbin: repeated values drop bins without failing")
        check(type(ct.named_transformers_["stage"]).__name__ == "SimpleImputer", "lrbin: the stage columns are not binned")
        m2 = sp.make_lrbin(nb, X.shape[1] - nb, True, cfg["bins"])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            m2.fit(X[tr], d["y"][tr])
        check(type(m2.steps[0][1].named_transformers_["stage"]).__name__ == "Pipeline", "lrbin2: the stage columns are binned")
        Xt = m.steps[0][1].transform(X[~tr])
        check(Xt.shape[1] > X.shape[1], "lrbin: the one-hot columns are added next to the values")

        # the lr and hgb route equals checks.e13_target's (_fit_job + _boot_job) on the same multipliers
        y, G = d["y"], d["G"]
        rng = np.random.default_rng(np.random.SeedSequence([5, 313, 0]))
        mults = np.array([np.bincount(rng.integers(0, d["n_sess"], size=d["n_sess"]), minlength=d["n_sess"]
                                      ).astype(float) for _ in range(50)])
        np.save(tmp / "mults.npy", mults)
        for kind in ("lr", "hgb"):
            sp._base_job((kind, y, 5, 3, cfg["bins"]))
        for fs in sp.FS:
            preds_b, preds_a = {}, {}
            for kind in ("lr", "hgb"):
                preds_b[(fs, kind)] = ck._fit_job((0, sp.LABEL, "S", "F-0", fs, kind, y, 5, 3, "pred"))[1]
                preds_a[kind] = ck._fit_job((0, sp.LABEL, "S", None, None, kind, y, 5, 3, "pred"))[1]
            _, boots = ck._boot_job(("x", preds_b, preds_a, y, G, list(mults)))
            for kind in ("lr", "hgb"):
                _, r = sp._fit_job((0, kind, "F-0", fs, [], y, 5, 3, cfg["bins"]))
                ones = np.ones(len(y))
                gain = ck.weighted_auc(preds_b[(fs, kind)], y, ones) - ck.weighted_auc(preds_a[kind], y, ones)
                b = boots[f"{fs}/{kind}"]
                ci = [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
                check(r["gain"] == gain and r["ci95"] == ci, f"{fs}/{kind}: split's gain and interval equal checks'")
        sp._base_job(("lrbin", y, 5, 3, cfg["bins"]))
        _, r = sp._fit_job((0, "lrbin", "F-0", "full", [], y, 5, 3, cfg["bins"]))
        _, r2 = sp._fit_job((0, "lrbin2", "F-0", "full", [], y, 5, 3, cfg["bins"]))
        check(math.isfinite(r["gain"]) and math.isfinite(r2["gain"]), "lrbin and lrbin2 fit")
        check((tmp / "base-lrbin.npy").exists() and not (tmp / "base-lrbin2.npy").exists(),
              "lrbin2 shares the base of lrbin")
        _, rd = sp._fit_job((0, "lr", "F-0", "full", cfg["drops"]["R2"], y, 5, 3, cfg["bins"]))
        _, rn = sp._fit_job((0, "lr", "F-0", "full", [], y, 5, 3, cfg["bins"]))
        check(rd["gain"] < rn["gain"], "dropping r_absdiff (the planted signal) lowers the gain")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_gate(cfg: dict) -> None:
    tol = cfg["gate_tol"]
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
    check(sp.gate(prev, got_of(), tol)["ok"], "gate: equal values pass")
    check(sp.gate(prev, got_of(0.5 * tol), tol)["ok"], "gate: a difference within tol passes")
    check(not sp.gate(prev, got_of(2 * tol), tol)["ok"], "gate: a difference over tol stops")
    check(not sp.gate(prev, got_of(drop_name=True), tol)["ok"], "gate: a name missing from e13.json stops")
    check(not sp.gate(prev, got_of(nan=True), tol)["ok"], "gate: a NaN stops")
    check(not sp.gate(prev, {"auc_A_speed": {}, "configs": {}}, tol)["ok"], "gate: nothing compared stops")
    g = got_of()
    g["auc_A_speed"]["lr"] += 1e-6
    check(not sp.gate(prev, g, tol)["ok"], "gate: AUC(A_speed) is compared")


def t_read(cfg: dict) -> None:
    m, pl = cfg["read"]["margin"], cfg["read"]["pc_lower"]
    check(m == 0.03 and pl == 0.03, "the reading thresholds are 0.03 (design 3.2, 3.3)")

    def mx(lo, hi):
        return {"gain_max": (lo + hi) / 2, "lower_max": lo, "upper_max": hi}
    pcs, pc0 = mx(0.04, 0.07), mx(-0.01, 0.01)
    check(sp.reading(mx(0.031, 0.05), pcs, pc0, m, pl) == "remains", "remains above 0.03")
    check(sp.reading(mx(0.03, 0.05), pcs, pc0, m, pl) == "undetermined", "a lower bound of exactly 0.03 does not remain")
    check(sp.reading(mx(0.0, 0.029), pcs, pc0, m, pl) == "vanishes", "vanishes below 0.03")
    check(sp.reading(mx(0.0, 0.03), pcs, pc0, m, pl) == "undetermined", "an upper bound of exactly 0.03 does not vanish")
    check(sp.reading(mx(0.04, 0.05), mx(0.03, 0.07), pc0, m, pl) == "unreadable", "PC-stall lower 0.03 is unreadable")
    check(sp.reading(mx(0.04, 0.05), pcs, mx(0.0, 0.03), m, pl) == "unreadable", "PC0 upper 0.03 is unreadable")
    nan = float("nan")
    check(sp.reading(mx(nan, nan), pcs, pc0, m, pl) == "undetermined", "a NaN candidate is undetermined")
    check(sp.reading(mx(0.04, 0.05), mx(nan, nan), pc0, m, pl) == "unreadable", "a NaN PC-stall is unreadable")
    check(sp.reading(mx(0.04, 0.05), pcs, mx(nan, nan), m, pl) == "unreadable", "a NaN PC0 is unreadable")
    a = {"full/lr": {"gain": 0.02, "ci95": [0.01, 0.05]}, "small/lr": {"gain": 0.03, "ci95": [0.0, 0.04]}}
    check(sp.maxima(a) == {"gain_max": 0.03, "lower_max": 0.01, "upper_max": 0.05}, "maxima over the two attackers")
    v = sp.variants(cfg)
    check(len(v) == 13 and ("lrbin2", "none") in v and not any(m_ == "lrbin2" and d != "none" for m_, d in v),
          "13 variants; lrbin2 without drops")


def main() -> int:
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for t in (t_prev, t_keep, t_build_and_models, t_gate, t_read):
        t(cfg)
    for f in FAILS:
        print(f"FAIL: {f}")
    print(f"selftest_split: ok {OK[0]}, failed {len(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
