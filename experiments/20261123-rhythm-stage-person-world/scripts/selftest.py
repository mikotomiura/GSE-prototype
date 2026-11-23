"""Self-tests of the rhythm stage desk check, relative timing (plan D) (design 3.7).

Design: .steering/20261122-rhythm-stage-relative-timing/design.md 3.7. Copied in part from
experiments/20261015-rhythm-stage-speed-shape-world/scripts/selftest.py (the file of 1cf9fcb9): the speed quantities and
the tables, the AUC and the fit rules, the closed input, causality, the stops, the rank, the window features, the lags,
the PC-stall and PC0, the twins, the judge, the statistics and the lambda choice, the gse-replay causality and the run's
own sessions (the PC-stall at lambda 1 and the seg mutation). Removed with the instruments they tested: the L1800 and
r-side controls, the cause split, the comparison table, and the world tests of the generator (the generator is not
changed: its file is checked byte for byte against the copied one instead).

Added (design 3.7):
- the copied files that are not changed (gen_sessions.py, baseline.py, replay_all.py, twins.py) equal the source's;
  the anchors, PC1, PC-corr, the PC-stall and PC0 of the anchors and the window features equal the source's stage;
- plan D: invariance to one factor on every interval (made-up sequences, s = 0.5 and 2), the count window (the 41st
  interval pushes the oldest out; an end exactly 300 s before t is in, 1 ms earlier out), the run boundary (3 times
  the median exactly is out), MIN_IVL and MIN_PAIRS, hand values, the 0 ms interval, causality, the closed input (D
  reads presses and active only), the stop, and the PC-stall of D (the block value per second, the hold, r = 0.5);
- N1 (sequences of the self-test generation, the graded world g050 at the smoke size, scaled by s = 2 and 0.5 from the
  session start; for s = 0.5 the press times are first moved to even ms so that the half is a whole ms) and N2 (only
  the intervals below N2_BURST_MS doubled): the shares compared and left out are printed;
- the two bases: base A and base A_speed are fitted on their own tables (each AUC equals a direct fit), and the A_speed
  verdict equals the copied checks.py's e13_target byte for byte on the same made-up input;
- the gate of pilot 0 (a step whose AUC(A) is at the ceiling stops; AUC(A_speed) alone does not), the pilot's parts per
  base, apply_pilot and main_lams per base, and the main run's PC-stall at each base's own lambda;
- --mutants: each mutant of design 3.7 is put in place in turn and must make its self-test fail (the unmutated test
  passes first).

Person world (.steering/20261123-rhythm-stage-person-world/design.md 3.7; the tests are in selftest_person.py): G0-G5 (the
generator), R1 (the closed input), P1-P5 ((5)), Q1-Q3 ((6)), J1-J4 (the verdict and the stops) and 14 more mutants.
gen_sessions.py and stage.py are no longer the copied files: G0 compares what the earlier worlds write, the stage test
compares the earlier names' output, both with the shape world's files.

A failing test stops the run. A failure is fixed in the instruments; the definitions of design 1 and 3 are not changed.

Usage: selftest.py <config.json> <tmp dir> --hmm-version V [--gse-replay BIN]
                   [--work DIR --seed-file FILE [--require-twins] [--jobs N]] [--mutants]
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

import baseline as bl
import ceiling as ce
import checks as ck
import gen_sessions as gs
import person as pe
import replay_all as ra
import selftest_person as sp
import stage as st
import twins as tw

HERE = Path(__file__).resolve().parent
SRC_DIR = HERE.parent.parent / "20261015-rhythm-stage-speed-shape-world" / "scripts"
# the copied files at 1cf9fcb9 (SHA-256 with LF line ends)
SRC_SHA = {"gen_sessions.py": "b6e9e0c9c515c2756ea4ddc459992e69e3ab8646da91d6dc75cfc2631e6618d0",
           "baseline.py": "570f93c3fcedb339da77ddb38d451c66a999cdef55bd2933aca59f1d07856aa6",
           "replay_all.py": "ef97720a4330d1ebeaf01139e8e8bfd5e369a5879659791eb44686682a2db28a",
           "twins.py": "db6e603b3529808cc47480fdec1bc3cee99dd2fb207cac08cd05d0ad0e4e2903",
           "stage.py": "7258f9a910479073e5ea055dc08327ebae33566db14df6a409c5e5a8696fe9b7",
           "checks.py": "59ca507b1d3c5bd5a248983b16f4bf7cb610390eab0336cecc23cd7f85d4112b"}
UNCHANGED = ("baseline.py", "replay_all.py", "twins.py")  # gen_sessions.py: the person worlds are added (G0 instead)
STEPS = {"g050": 0.5, "f200": 2.0}
WORLDS = {"g050": "graded", "f200": "factor"}
GRADED_05 = (219.08902300206645, 0.3)  # STRUGGLE's flight median and sigma at t = 0.5 (the copied selftest's values)
TEST_SEED = 7  # the self-test generation: not the run's seeds (SEED, SEED + 1, SEED + 2)
N2_BURST_MS = 600  # N2: the intervals below this count as inside a burst (the self-test's reading, design 3.7)
FAILS: list[str] = []


def check(cond: bool, name: str) -> None:
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def sha_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


# ---------------------------------------------------------------------------
# The copied files and the config
# ---------------------------------------------------------------------------

def test_unchanged() -> None:
    for f, want in SRC_SHA.items():
        src = SRC_DIR / f
        check(src.exists() and sha_lf(src) == want, f"source: {f} of the shape world is the 1cf9fcb9 file (SHA-256)")
    for f in UNCHANGED:
        check(sha_lf(HERE / f) == SRC_SHA[f], f"unchanged: our {f} equals the source's byte for byte (LF)")
    check(sha_lf(HERE / "stage.py") != SRC_SHA["stage.py"], "unchanged: stage.py does differ (negative control)")
    check(sha_lf(HERE / "gen_sessions.py") != SRC_SHA["gen_sessions.py"], "unchanged: gen_sessions.py does differ (G0 compares its output)")


def test_config(cfg: dict) -> None:
    c = cfg["ceiling"]
    check(c["steps"] == STEPS and c["worlds"] == WORLDS and c["main_auc"] == 0.9 and c["P"] == 240
          and c["seed_offset"] == 1, "config: steps g050 (graded, t 0.5) and f200 (factor, c 2), P 240, SEED + 1, 0.90")
    seed = int((HERE.parent / "SEED").read_text().strip())
    check(seed == 20261125, "config: SEED is 20261125 (person-world design section 9 item 1)")
    d = cfg["plan_d"]
    check(d == {"n_win": st.N_WIN, "max_age_s": st.MAX_AGE_S, "run_k": st.RUN_K, "spread_scale": "log 10",
                "irreg_scale": st.IRREG_SCALE, "min_ivl": st.MIN_IVL, "min_pairs": st.MIN_PAIRS, "init": st.D_INIT}
          and st.SPREAD_SCALE == math.log(10.0) and st.N_WIN == 40 and st.MAX_AGE_S == 300 and st.RUN_K == 3.0
          and st.MIN_IVL == 8 and st.MIN_PAIRS == 5, "config: plan_d equals stage.py's constants (design 1.2)")
    check(tuple(cfg["describe"]["d2_smooth"]) == ck.SMOOTH_NAMES
          and [st.FEAT_NAMES[i] for i in ck.SMOOTH_COLS] == list(ck.SMOOTH_NAMES),
          "config: the (d2) smoothness features are a_sd a_absdiff a_ac1 r_sd r_absdiff r_ac1")
    check(st.candidates() == ["D-run-hold-sec", "D-all-hold-sec", "S-raw-hold-sec", "S-raw-hold-sub",
                              "S-rank-hold-sec", "S-rank-hold-sub"], "config: the six candidates (design 0)")
    check(cfg["pc_stall"]["lam"] == {} or set(cfg["pc_stall"]["lam"]) <= set(STEPS),
          "config: pc_stall.lam is keyed by the steps (none copied over)")
    check("pc_r" not in cfg and "split" not in cfg and "lam_1800" not in cfg["pc_stall"],
          "config: no r-side control, cause split or L1800 lambda (decisions 8, 9)")
    p = cfg["person"]
    check(p["n_persons"] == st.N_PERSONS == 40 and p["sessions_per_person"] == st.SLOTS == 6 and p["order"] == [
        "m049", "m068", "r049", "r068"] and sorted(p["steps"]) == sorted(p["order"]),
          "config: person: 40 persons x 6 sessions (= stage.py's), the four steps m049 m068 r049 r068")
    check(abs(p["sigma_b"] - math.log(481.03 / 121.70) / (2 * 1.2816)) < 5e-4 and p["icc"] == {"049": 0.494, "068": 0.679},
          "config: sigma_b is ln(481.03 / 121.70) / (2 x 1.2816) = 0.536 and the ICCs 0.494 / 0.679 (decisions 7)")
    check(p["steps"]["m049"] == {"world": "person-m", "icc": 0.494} and p["steps"]["r068"]["world"] == "person-r"
          and p["steps"]["r068"]["target_step"] == "m068" and p["k_grid"] == sorted(p["k_grid"]) and len(p["k_grid"]) == 13
          and p["k_grid"][0] == 0.01 and p["k_grid"][-1] == 1.0 and p["k_tolerance"] == 0.02
          and p["pc_raw"]["gate_lower"] == 0.53 and p["bootstrap"] == cfg["e13"]["bootstrap"]
          and p["null_perms"] == cfg["e13"]["null_perms"] and p["folds"] == cfg["e13"]["folds"],
          "config: the steps' worlds and ICCs, the 13-point k grid, the 0.02 tolerance, the 0.53 gate, e13's sizes")
    check(list(gs.DIM_H) == p["h"] == [1.0, 1.0, 1.0] and p["seed_offsets"] == {"main": 0, "pilot": 1, "kgrid": 1,
                                                                              "ceiling": 1, "smoke": 2},
          "config: h = 1 and the seed offsets (design 1.3, section 9 item 4)")
    check(set(cfg["pc_person"]) == {"lam"} and set(cfg["pc_pers"]) == {"lam"}, "config: pc_person.lam and pc_pers.lam exist")


# ---------------------------------------------------------------------------
# Speed quantities, tables, AUC and the step rule (copied; the step rule per base)
# ---------------------------------------------------------------------------

def test_speed(cfg: dict) -> None:
    sp = cfg["speed"]
    p = np.array([10.0, 10.1, 10.2, 11.7, 12.0, 17.0])
    q = bl.speed5(p, 10.0, 25.0, sp)
    d = np.array([100.0, 100.0, 1500.0, 300.0])
    exp = [6.0, float(np.median(d)), float(np.percentile(d, 75) - np.percentile(d, 25)), 6 / 4, 1.0]
    check(np.allclose(q, exp), f"speed5: hand-made span {q} == {exp}")
    check(bl.speed5(p, 0.0, 10.0, sp) == [0.0, 2000.0, 0.0, 0.0, 0.0], "speed5: empty span -> 0, 2000, 0, 0, 0")
    ok200 = all(bl.speed5(np.array([t, t + 0.2]), t, t + 1.0, sp)[3] == 1.0 for t in (10.0, 1234.567, 3599.0))
    check(ok200, "speed5: an interval of exactly 200 ms breaks a run at any session time")
    ok2000 = all(bl.speed5(np.array([t, t + 1.0, t + 3.0]), t, t + 5.0, sp)[1:3] == [1000.0, 0.0]
                 for t in (0.3, 1234.567))
    check(ok2000, "speed5: an interval of exactly 2000 ms is not short")


def bursty_trace(rng: np.random.Generator, dur: int, sid: str = "T") -> bl.Trace:
    """Bursts of presses 100-300 ms apart separated by pauses of 0.5-30 s, in whole ms (as the generator)."""
    t, ms = float(rng.uniform(0, 5000)), []
    while t < dur * 1000:
        for _ in range(int(rng.integers(1, 12))):
            ms.append(int(t))
            t += float(rng.uniform(100, 300))
        t += float(rng.uniform(500, 30000))
    ms_arr = np.asarray([m for m in ms if m < dur * 1000], dtype=np.int64)
    presses = ms_arr / 1000.0
    seg = np.repeat(rng.integers(0, 5, size=dur // 60 + 1), 60)[:dur].astype(np.int8)
    active = np.zeros(dur, dtype=bool)
    active[presses.astype(int)] = True
    return bl.Trace(sid, dur, presses, active, seg)


def test_tables(cfg: dict, tmp: Path) -> None:
    rng = np.random.default_rng(7)
    work = tmp / "tables"
    (work / "labels").mkdir(parents=True, exist_ok=True)
    traces = [bursty_trace(rng, 3600, "P000"), bursty_trace(rng, 2400, "P001")]
    for t in traces:
        np.savez_compressed(work / "labels" / f"{t.sid}.npz", seg=t.seg, presses_ms=np.rint(t.presses * 1000).astype(np.int64),
                            duration_s=np.int64(t.duration_s), start_ms=np.int64(0))
    (work / "sessions.json").write_text(json.dumps([{"sid": t.sid, "set": "P"} for t in traces]), encoding="utf-8")
    tab = bl.tables(work, bl.p_sids(work), cfg)
    check(tab["L300"]["XA"].shape[1] == 15 and tab["L300"]["XS"].shape[1] == 33
          and np.array_equal(tab["L300"]["XS"][:, :15], tab["L300"]["XA"]),
          "tables: L300 A has 15 columns, A_speed 33 starting with A")
    check(len(ck.feature_names("A")) == 15 + 60 and len(ck.feature_names("S")) == 33 + 60,
          "importance: the feature names of base + the stage (full) per base")


def test_auc_and_choice(cfg: dict) -> None:
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(3)
    y = rng.integers(0, 2, 500)
    s = np.round(y + rng.normal(0, 1, 500), 1)
    check(np.isclose(ce.weighted_auc(s, y, np.ones(500)), roc_auc_score(y, s)), "AUC: equals sklearn with ties")
    X = rng.normal(size=(500, 3))
    g = np.repeat(np.arange(50), 10)
    y_one = np.zeros(500, dtype=int)
    y_one[:10] = 1
    check(ce._fit_job(("k", X, y_one, g, "lr", 1, 5))[1] is None, "fit: a training side with one class -> None")
    # design 3.0: the step's status is model A's; A_speed has its own status
    mk = lambda a_h, a_l, s_h, s_l: {"L300": {"hgb": {"auc_A": a_h, "auc_A_speed": s_h},
                                             "lr": {"auc_A": a_l, "auc_A_speed": s_l}}}
    ma = cfg["ceiling"]["main_auc"]
    r = ce.step_status(mk(0.76, 0.75, 0.999, 0.997), ma)
    check(r["status"] == "go" and r["status_A"] == "go" and r["status_A_speed"] == "ceiling",
          "steps: AUC(A_speed) alone at the ceiling -> the step goes on (A_speed's status is ceiling)")
    r = ce.step_status(mk(0.90, 0.90, 0.95, 0.95), ma)
    check(r["status"] == "ceiling" and r["status_A"] == "ceiling", "steps: AUC(A) 0.90 and 0.90 -> the step stops")
    r = ce.step_status(mk(0.8999, 0.95, 0.99, 0.99), ma)
    check(r["status"] == "go", "steps: one classifier's AUC(A) below 0.90 -> go")
    r = ce.step_status(mk(float("nan"), 0.7, 0.8, 0.8), ma)
    check(r["status"] == "unmeasured", "steps: a NaN AUC(A) -> unmeasured (the step stops)")
    r = ce.step_status(mk(0.7, 0.7, None, 0.8), ma)
    check(r["status"] == "go" and r["status_A_speed"] == "unmeasured", "steps: an unmeasured A_speed alone does not stop")
    got = ce.choose_steps({"g050": mk(0.76, 0.75, 0.999, 0.997), "f200": mk(0.7, 0.7, 0.8, 0.8)}, cfg)
    check(got["g050"] == {"world": "graded", "t": 0.5, **ce.step_status(mk(0.76, 0.75, 0.999, 0.997), ma)}
          and got["f200"]["world"] == "factor" and got["f200"]["c"] == 2.0 and "t" not in got["f200"],
          "steps: each step gets its world and its t (graded) or c (factor)")


# ---------------------------------------------------------------------------
# The stage (copied tests narrowed to the six candidates)
# ---------------------------------------------------------------------------

def fake_session(rng: np.random.Generator, dur: int = 3600, sid: str = "F") -> st.Session:
    tr = bursty_trace(rng, dur, sid)
    feat = {c: rng.uniform(0, 1, dur) for c in ("f3", "f5", "f6", "p_stuck")}
    feat["keys"] = rng.integers(0, 160, dur).astype(float)
    feat["f1"] = rng.uniform(40, 2000, dur)
    feat["f4"] = rng.uniform(0, 20, dur)
    feat["f1"][rng.random(dur) < 0.05] = np.nan
    return st.Session(sid, dur, tr.presses, tr.active, tr.seg, feat, int(rng.integers(0, 2 ** 62)))


def all_series(sess: st.Session, seed: int = 5) -> dict:
    return {c: st.series(sess, c, seed) for c in st.candidates()}


def same_series(x: dict, y: dict, upto: int | None = None) -> bool:
    sl = slice(None) if upto is None else slice(0, upto)
    return all(np.array_equal(x[c][0][sl], y[c][0][sl]) and np.array_equal(x[c][1][sl], y[c][1][sl]) for c in x)


def test_input_closure() -> None:
    rng = np.random.default_rng(11)
    sess = fake_session(rng)
    base = all_series(sess)
    mut = st.Session(sess.sid, sess.duration_s, sess.presses, sess.active, rng.integers(0, 5, sess.duration_s).astype(np.int8),
                     {**sess.feat, **{c: np.full(sess.duration_s, np.nan) for c in ("f3", "f5", "f6", "p_stuck")}},
                     sess.key_seed)
    check(same_series(base, all_series(mut)), "input closure: f3 f5 f6 p_stuck to NaN and other labels leave the 6 unchanged")
    inp = st.stage_input(sess)
    for c in ("f3", "f6", "p_stuck", "seg"):
        try:
            inp[c]
            ok = False
        except KeyError:
            ok = True
        check(ok, f"input closure: reading {c} raises")
    for c in st.D_CANDIDATES:
        inp = st.stage_input(sess)
        st.candidate_series(inp, c, 5, sess.key_seed)
        check(inp.read == set(st.D_INPUT), f"input closure: {c} reads presses and active only ({sorted(inp.read)})")
        pinp = st.stage_input(sess)
        a_block = np.full(sess.duration_s, 0.3)
        st.d_series(pinp, c, 5, sess.key_seed, a_block=a_block)
        check(pinp.read == set(st.D_INPUT), f"input closure: the PC-stall of {c} reads presses and active only")
    inp = st.stage_input(sess)
    st.candidate_series(inp, "S-raw-hold-sec", 5, sess.key_seed)
    check({"keys", "f1"} <= inp.read, "input closure: the record sees keys and f1 read by S-raw-hold-sec (negative control)")
    mut2 = st.Session(sess.sid, sess.duration_s, sess.presses, sess.active, sess.seg,
                      {**sess.feat, "keys": sess.feat["keys"][::-1].copy(), "f1": sess.feat["f1"][::-1].copy(),
                       "f4": sess.feat["f4"][::-1].copy()}, sess.key_seed)
    s2 = all_series(mut2)
    check(all(np.array_equal(base[c][0], s2[c][0]) and np.array_equal(base[c][1], s2[c][1]) for c in st.D_CANDIDATES)
          and not np.array_equal(base["S-raw-hold-sec"][0], s2["S-raw-hold-sec"][0]),
          "input closure: keys, f1 and f4 reversed leave D unchanged and change S-raw-hold-sec")


def test_stage_causal() -> None:
    rng = np.random.default_rng(12)
    sess = fake_session(rng)
    T = 1800
    feat = {c: v.copy() for c, v in sess.feat.items()}
    for c in feat:
        feat[c][T:] = rng.permutation(feat[c][T:])
    active = sess.active.copy()
    active[T:] = False
    cut = st.Session(sess.sid, sess.duration_s, sess.presses[sess.presses < T], active, sess.seg, feat, sess.key_seed)
    a, b = all_series(sess), all_series(cut)
    check(same_series(a, b, T * st.HZ), "causal (stage): later presses and F leave the 6 unchanged before T")
    check(not same_series(a, b), "causal (stage): they change the 6 after T (negative control)")
    T2 = 1800.35
    keep = sess.presses < T2
    active2 = np.zeros(sess.duration_s, dtype=bool)
    active2[sess.presses[keep].astype(int)] = True
    feat2 = {c: v.copy() for c, v in sess.feat.items()}
    for c in feat2:
        feat2[c][1800:] = rng.permutation(feat2[c][1800:])
    extra = np.array([1800.36, 1800.5, 1800.9])
    cut2 = st.Session(sess.sid, sess.duration_s, sess.presses[keep], active2, sess.seg, feat2, sess.key_seed)
    more = st.Session(sess.sid, sess.duration_s, np.sort(np.concatenate([sess.presses[keep], extra])),
                      active2 | (np.arange(sess.duration_s) == 1800), sess.seg, feat2, sess.key_seed)
    j2 = int(np.ceil(T2 * st.HZ))
    c2, m2 = all_series(cut2), all_series(more)
    check(same_series(c2, m2, j2) and same_series(a, c2, j2),
          "causal (stage): presses later in the same second (after 1800.35 s) leave every point before it unchanged")
    check(not same_series(c2, m2), "causal (stage): those presses do change later points (negative control)")
    # plan D per second: the value of second k does not depend on the presses at or after t = k + 1
    for dset in st.D_SETS:
        ds_full = st.d_seconds(sess.presses, sess.duration_s, dset)
        ds_cut = st.d_seconds(sess.presses[sess.presses < T], sess.duration_s, dset)
        check(np.array_equal(ds_full.a[:T], ds_cut.a[:T]) and np.array_equal(ds_full.r[:T], ds_cut.r[:T])
              and not np.array_equal(ds_full.a, ds_cut.a),
              f"causal (D-{dset}): second k < T unchanged when the presses from T go")
    edge = np.array([0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 1.9, 2.0])  # the last press exactly at t = 2
    d_e = st.d_seconds(edge, 3, "all")
    check(d_e.hi[1] == 9 and d_e.hi[2] == 10, "causal (D): an interval ending exactly at t = k + 1 belongs to second k + 1")


def test_stops() -> None:
    hz = st.HZ
    p = np.round(np.concatenate([np.arange(10, 20, 0.2), np.arange(80, 90, 0.2)]), 3)
    dur = 100
    act = np.zeros(dur, dtype=bool)
    act[p.astype(int)] = True
    inp = st.StageInput(dur, {"presses": p, "active": act, "keys": np.full(dur, 75.0), "f1": np.full(dur, 300.0),
                              "f4": np.zeros(dur)})
    last = p[p < 20][-1]
    j_stop = int(np.ceil((last + 2) * hz - 1e-9))
    out = st.candidate_series(inp, "S-raw-hold-sub", 1, 7)
    v0 = out[0][j_stop - 1]
    check(np.all(out[0][j_stop: 80 * hz] == v0) and v0 > 0, "stop hold (sub): the amplitude stays at the last moving value")
    _, _, stp = st.drive_sec(inp)
    check(not stp[20 * hz] and not stp[22 * hz - 1] and stp[22 * hz] and stp[81 * hz - 1] and not stp[81 * hz],
          "stop (sec): moving until t = 22, stopped on [22, 81), moving from 81")
    check(np.array_equal(st.d_stopped(act, dur), stp), "stop (D): the stopped points of plan D are those of res=sec")
    for c in st.D_CANDIDATES:
        a, r = st.candidate_series(inp, c, 1, 7)
        check(np.all(a[22 * hz: 81 * hz] == a[22 * hz - 1]) and np.all(r[22 * hz: 81 * hz] == r[22 * hz - 1]),
              f"stop (D): {c} holds a and r at the last moving value while stopped")
        check(np.all(a[: hz] == 0) and np.all(r[: hz] == 0), f"stop (D): {c} is 0 before the first moving point (hold)")
    rng = np.random.default_rng(4)
    x = np.round(rng.random(1500), 2)
    mv = rng.random(1500) < 0.7
    rk = st.running_rank(x, mv, chunk=97)
    q = np.rint(x * st.RANK_LEVELS)
    bf = np.full(1500, 0.5)
    for j in range(st.RANK_WARM_S * st.HZ, 1500):
        ref = q[: j + 1][mv[: j + 1]]
        if len(ref):
            bf[j] = ((ref < q[j]).sum() + 0.5 * (ref == q[j]).sum()) / len(ref)
    check(np.allclose(rk, bf), "rank: equals a brute force mid-rank over the moving points up to t")


def test_window_features() -> None:
    W = st.WIN_POINTS
    a = np.concatenate([np.full(W, 0.4), np.full(300, 0.2), np.full(300, 0.6)])
    r = np.concatenate([np.zeros(W), np.linspace(0, 1, W)])
    F = st.window_features(a, r, 2)
    check(F.shape == (2, 20) and F[0, 1] == 0 and F[0, 9] == 60.0 and abs(F[1, 9] - 30.0) < 1e-9,
          "window features: 20 per window, a constant window, a step at the middle")


def test_lags(cfg: dict) -> None:
    hz = st.HZ
    ok = True
    for L in (1.0, 3.0, 5.0):
        x = np.full(60 * hz, 0.2)
        x[int((20 + L) * hz):] = 0.8
        kind, lag = ck.event_lag(x, 20.0, cfg)
        ok &= kind == "lag" and abs(lag - L) <= 0.1 + 1e-9
    check(ok, "lags: steps at 1, 3 and 5 s are returned within 0.1 s")
    kinds = [ck.event_lag(np.full(40 * hz, v), 15.0, cfg)[0] for v in np.linspace(0, 1, 11)]
    check(all(k == "unchanged" for k in kinds), "lags: hold without the wobble -> unchanged in every event")
    check(all(ck.lags_readable(c) for c in st.candidates()), "lags: none of the six is a jitter candidate (all read)")
    ev = ck.stop_events(np.array([0.5, 5.0, 16.0, 17.0, 40.0, 95.0]), 100, cfg)
    check(ev == [(5.0, 16.0), (17.0, 40.0)], f"lags: stop events {ev}")


def test_pc() -> None:
    rng = np.random.default_rng(13)
    sess = fake_session(rng)
    blk = {lam: st.pc_blocks(sess.seg, sess.duration_s, sess.key_seed, 1, lam) for lam in (0.0, 0.3, 1.0)}
    check(np.array_equal(blk[0.0]["value"], blk[0.0]["N"]) and np.array_equal(blk[1.0]["value"], blk[1.0]["q"]),
          "PC: lambda 0 -> N everywhere, lambda 1 -> q everywhere")
    perm = st.Session(sess.sid, sess.duration_s, sess.presses, sess.active, rng.permutation(sess.seg), sess.feat, sess.key_seed)
    ok = all(np.array_equal(st.series(sess, f"PC0-{c}", 1)[0], st.series(perm, f"PC0-{c}", 1)[0]) for c in st.candidates())
    check(ok, "PC: PC0 of every candidate (D included) does not depend on the labels")
    for c in ("S-raw-hold-sec",) + st.D_CANDIDATES:
        check(not np.array_equal(st.series(sess, f"PCs-{c}", 1, lam=1.0)[0], st.series(perm, f"PCs-{c}", 1, lam=1.0)[0]),
              f"PC: PCs-{c} at 1 does (negative control)")
    # design 1.5: the PC-stall of D: per second the block value where the set suffices, else the previous value; r 0.5
    for c in st.D_CANDIDATES:
        dset = st.d_parse(c)
        q = blk[1.0]["q"]
        ds = st.d_seconds(sess.presses, sess.duration_s, dset, a_block=q[np.arange(sess.duration_s) // 60])
        k = np.arange(sess.duration_s)
        suff = ds.n_set >= st.MIN_IVL
        prev_ok = True
        for kk in np.nonzero(~suff)[0]:
            prev_ok &= ds.a[kk] == (ds.a[kk - 1] if kk > 0 else st.D_INIT)
        check(np.array_equal(ds.a[suff], q[k[suff] // 60]) and prev_ok and np.all(ds.r == 0.5) and (~suff).any()
              and suff.any(), f"PC (D): {c}'s a is the block value of block k // 60 where the set suffices, held "
                              "elsewhere; r is 0.5")
        a, r = st.series(sess, f"PCs-{c}", 1, lam=1.0)
        mv = ~st.d_stopped(sess.active, sess.duration_s)
        kp = np.arange(len(a)) // st.HZ - 1
        check(np.array_equal(a[mv], ds.a[kp[mv]]) and np.all(r[mv] == 0.5),
              f"PC (D): PCs-{c} at the moving points is that per-second value, r = 0.5")
    a = st.series(sess, "PC1", 1)[0]
    check(abs(a[100 * st.HZ + 5] - st.stall_share(sess.seg, 40, 100)) < 1e-12, "PC1: the stall share of the 60 s before")
    test_stage_source(sess)


def load_source_stage():
    """The shape world's stage.py, run from the bytes whose SHA-256 is checked (LF line ends): no .pyc is read from
    or written to the source directory (security-checker, 2026-11-23)."""
    path = SRC_DIR / "stage.py"
    src = path.read_bytes().replace(b"\r\n", b"\n")
    if hashlib.sha256(src).hexdigest() != SRC_SHA["stage.py"]:
        raise SystemExit("the shape world's stage.py is not the 1cf9fcb9 file")
    spec = importlib.util.spec_from_loader("stage_shape_src", loader=None, origin=str(path))
    old = importlib.util.module_from_spec(spec)
    old.__file__ = str(path)
    sys.modules[spec.name] = old  # the dataclass Session looks its module up there
    exec(compile(src, str(path), "exec"), old.__dict__)
    return old


def test_stage_source(sess: st.Session) -> None:
    """design 3.7: the names kept from the shape world's stage draw what its file (1cf9fcb9) draws."""
    if sha_lf(SRC_DIR / "stage.py") != SRC_SHA["stage.py"]:
        check(False, "stage: the shape world's stage.py is not the 1cf9fcb9 file")
        return
    old = load_source_stage()
    osess = old.Session(sess.sid, sess.duration_s, sess.presses, sess.active, sess.seg, sess.feat, sess.key_seed)
    names = ([(c, None) for c in st.ANCHORS] + [("PC1", None), ("PC-corr", None)]
             + [(f"PCs-{c}", 0.4) for c in st.ANCHORS] + [(f"PC0-{c}", None) for c in st.ANCHORS])
    same = all(np.array_equal(x, y) for n, lam in names
               for x, y in zip(st.series(sess, n, 3, lam=lam), old.series(osess, n, 3, lam=lam)))
    check(same and len(names) == 14, "stage: the 4 anchors, PC1, PC-corr, the PC-stall and PC0 of the anchors equal "
                                     "the shape world's stage")
    check(not np.array_equal(st.series(sess, f"PCs-{st.ANCHORS[0]}", 3, lam=0.4)[0],
                             old.series(osess, f"PCs-{st.ANCHORS[0]}", 3, lam=0.9)[0]),
          "stage: the comparison tells another lambda apart (negative control)")
    check(st.FEAT_NAMES == old.FEAT_NAMES and np.array_equal(
        st.window_features(*st.series(sess, st.ANCHORS[0], 3), 10),
        old.window_features(*old.series(osess, st.ANCHORS[0], 3), 10)),
        "stage: the window features equal the shape world's")


# ---------------------------------------------------------------------------
# Plan D (design 1.2, 3.7)
# ---------------------------------------------------------------------------

def even_ms(pm: np.ndarray) -> np.ndarray:
    """Press times moved to even ms (strictly increasing kept), so that a half is a whole ms."""
    out = (pm // 2) * 2
    for i in range(1, len(out)):
        if out[i] <= out[i - 1]:
            out[i] = out[i - 1] + 2
    return out


def window_sets(pm: np.ndarray, dur: int, dset: str) -> dict:
    p = pm / 1000.0
    vals, ends, idx = st.d_intervals(p)
    lo, hi = st.d_window_bounds(ends, dur)
    ds = st.d_seconds(p, dur, dset)
    return {"vals": vals, "idx": idx, "lo": lo, "hi": hi, "ds": ds}


def match_seconds(w1: dict, w2: dict, dur1: int, dur2: int) -> list[tuple[int, int | None]]:
    """For each second k of sequence 1 with a window, the first second of sequence 2 whose window ends at the same
    press (None when there is none)."""
    first = {}
    for k2 in range(dur2):
        if w2["hi"][k2] > 0:
            first.setdefault(int(w2["idx"][w2["hi"][k2] - 1]), k2)
    return [(k, first.get(int(w1["idx"][w1["hi"][k] - 1]))) for k in range(dur1) if w1["hi"][k] > 0]


def compare_scaled(pm1: np.ndarray, pm2: np.ndarray, dset: str) -> dict:
    """N1 / the made-up invariance: per matched second, the windows by press index; where they are the same set the
    sufficient quantities must be equal. Returns the counts."""
    dur1, dur2 = int(pm1.max() // 1000) + 2, int(pm2.max() // 1000) + 2
    w1, w2 = window_sets(pm1, dur1, dset), window_sets(pm2, dur2, dset)
    n = {"seconds": 0, "unmatched": 0, "other_window": 0, "compared": 0, "equal": 0, "held": 0}
    for k, k2 in match_seconds(w1, w2, dur1, dur2):
        n["seconds"] += 1
        if k2 is None:
            n["unmatched"] += 1
            continue
        s1 = w1["idx"][w1["lo"][k]: w1["hi"][k]]
        s2 = w2["idx"][w2["lo"][k2]: w2["hi"][k2]]
        if not np.array_equal(s1, s2):
            n["other_window"] += 1
            continue
        d1, d2 = w1["ds"], w2["ds"]
        if d1.n_set[k] < st.MIN_IVL or d1.n_pairs[k] < st.MIN_PAIRS or d2.n_set[k2] < st.MIN_IVL \
                or d2.n_pairs[k2] < st.MIN_PAIRS:
            n["held"] += 1
            continue
        n["compared"] += 1
        n["equal"] += int(d1.a[k] == d2.a[k2] and d1.r[k] == d2.r[k2])
    return n


def made_up_ms(rng: np.random.Generator, dur_s: int) -> np.ndarray:
    """Even ms: bursts of 5-15 presses 120-550 ms apart, 700-900 ms between bursts, now and then a pause of
    4.5-9 s. No interval crosses 2000 ms when it is halved or doubled; 40 intervals take well under 150 s."""
    t, out = 0, []
    while t < dur_s * 1000:
        m = int(rng.integers(5, 16))
        for i in range(m):
            out.append(t)
            if i < m - 1:
                t += 2 * int(rng.integers(60, 276))
        t += 2 * int(rng.integers(350, 451)) if rng.random() < 0.8 else 2 * int(rng.integers(2250, 4501))
    return np.asarray(out, dtype=np.int64)


def test_plan_d() -> None:
    """design 3.7: plan D's definitions on made-up sequences."""
    rng = np.random.default_rng(21)
    pm = made_up_ms(rng, 1800)
    for dset in st.D_SETS:
        for s, a, b in ((2.0, pm, pm * 2), (0.5, pm, pm // 2)):
            n = compare_scaled(a, b, dset)
            matched = n["seconds"] - n["unmatched"]  # compressing (s = 0.5) leaves seconds no window ends at
            share = n["compared"] / max(matched, 1)
            check(n["compared"] > 0 and n["equal"] == n["compared"] and share >= 0.9,
                  f"invariance (made-up): D-{dset} at s = {s}: {n['equal']} of {n['compared']} compared seconds equal "
                  f"({share:.3f} of {matched} matched seconds compared; other windows {n['other_window']}, held "
                  f"{n['held']}, unmatched {n['unmatched']})")
    # the count window: 41 intervals of 100 ms ending at 100 .. 4100 ms; the 41st pushes the oldest out
    p = np.arange(0, 4200, 100) / 1000.0
    vals, ends, idx = st.d_intervals(p)
    lo, hi = st.d_window_bounds(ends, 6)
    check((lo[2], hi[2]) == (0, 29) and (lo[3], hi[3]) == (0, 39) and (lo[4], hi[4]) == (1, 41) and len(vals) == 41,
          f"count window: 29 / 39 intervals by t = 3 / 4, then the last 40 of 41 at t = 5 (lo {lo[4]}, hi {hi[4]})")
    # the age cap: an end exactly 300 s before t is in, 1 ms earlier out
    ends = np.array([99_999, 100_000, 100_500, 399_000], dtype=np.int64)
    lo, hi = st.d_window_bounds(ends, 400)
    check(lo[399] == 1 and hi[399] == 4, "age cap: at t = 400 s an end at 100.000 s is in, 99.999 s is out")
    # the run boundary: exactly 3 times the median is out
    w = np.array([100.0, 100.0, 100.0, 300.0, 299.0])
    check(list(st.d_select(w, "run")) == [True, True, True, False, True] and st.d_select(w, "all").all(),
          "run: 300 ms (3 x the median 100) is out, 299 ms in; all keeps every interval")
    # hand values
    v = np.array([100.0, 120, 150, 200, 250, 300, 350, 400, 1000])
    p10, p90 = np.percentile(v, [10, 90])
    check(st.d_spread(v) == float(np.clip(math.log(p90 / p10) / math.log(10), 0, 1)),
          "spread: log(p90 / p10) / log 10 (numpy's linear percentiles)")
    check(st.d_spread(np.array([1.0, 1.0, 1000.0, 1000.0])) == 1.0 and st.d_spread(np.full(8, 200.0)) == 0.0,
          "spread: clipped to [0, 1]")
    w = np.array([100.0, 200, 100, 400, 100, 100])
    adj = np.array([False, True, True, False, True, True])
    irr, npair = st.d_irregularity(w, adj, np.ones(6, dtype=bool))
    check(npair == 4 and irr is None, "tempo: 4 adjacent pairs (a break in the press sequence cuts one) < MIN_PAIRS")
    w7 = np.array([100.0, 200, 100, 400, 100, 100, 300])
    adj7 = np.ones(7, dtype=bool)
    irr, npair = st.d_irregularity(w7, adj7, np.ones(7, dtype=bool))
    want = float(np.median(np.abs(np.log(w7[1:] / w7[:-1]))))
    check(npair == 6 and irr == min(1.0, want), f"tempo: the median of |log ratio| over 6 pairs ({irr})")
    w6 = w7[:6]
    irr5, npair5 = st.d_irregularity(w6, np.ones(6, dtype=bool), np.ones(6, dtype=bool))
    want5 = float(np.median(np.abs(np.log(w6[1:] / w6[:-1]))))
    check(npair5 == st.MIN_PAIRS == 5 and irr5 == min(1.0, want5),
          f"tempo: exactly MIN_PAIRS (5) pairs give a value ({irr5}); 4 hold (above)")
    sel = np.array([True, True, True, False, True, True, True])
    _, npair = st.d_irregularity(w7, adj7, sel)
    check(npair == 4, "tempo: a pair needs both intervals in the set")
    # MIN_IVL: a session with 7 intervals holds 0.5; with 8 the spread is computed
    p7 = np.cumsum(np.r_[1000, [100, 200, 150, 300, 120, 250, 180]]) / 1000.0
    p8 = np.cumsum(np.r_[1000, [100, 200, 150, 300, 120, 250, 180, 90]]) / 1000.0
    d7, d8 = st.d_seconds(p7, 5, "all"), st.d_seconds(p8, 5, "all")
    check(d7.a[4] == st.D_INIT and d8.n_set[4] == 8 and d8.a[4] != st.D_INIT,
          "MIN_IVL: 7 intervals hold the start value, 8 give the spread")
    # 0 ms intervals are left out
    pz = np.array([1.0, 1.1, 1.1, 1.2])
    vals, _, idx = st.d_intervals(pz)
    check(list(vals) == [100.0, 100.0] and list(idx) == [1, 3], "intervals: a 0 ms interval is left out")


def test_n1_n2(work: Path) -> None:
    """design 3.7 N1 and N2 on the self-test generation's g050 sequences (smoke size). The shares are recorded."""
    sids = bl.p_sids(work)
    tot = {}
    for sid in sids:
        pm = np.load(work / "labels" / f"{sid}.npz")["presses_ms"].astype(np.int64)
        pm = np.sort(pm)
        ev = even_ms(pm)
        for dset in st.D_SETS:
            for s, a, b in ((2.0, pm, pm * 2), (0.5, ev, ev // 2)):
                n = compare_scaled(a, b, dset)
                t = tot.setdefault((dset, s), {k: 0 for k in n})
                for k in n:
                    t[k] += n[k]
    for (dset, s), n in sorted(tot.items()):
        check(n["compared"] > 0 and n["equal"] == n["compared"],
              f"N1: D-{dset} at s = {s}: {n['equal']} of {n['compared']} compared seconds equal")
        print(f"     (N1 D-{dset} s = {s}) of {n['seconds']} seconds with a window: compared "
              f"{n['compared'] / n['seconds']:.3f}, other window (2000 ms or 300 s cap) {n['other_window'] / n['seconds']:.3f}, "
              f"unmatched {n['unmatched'] / n['seconds']:.3f}, held {n['held'] / n['seconds']:.3f}")
    # positive control: S-raw-hold-sub's tempo at the moment of a press is not the same after the scaling
    sid = sids[0]
    pm = np.sort(np.load(work / "labels" / f"{sid}.npz")["presses_ms"].astype(np.int64))
    for s, a, b in ((2.0, pm, pm * 2),):
        def tempo_at_presses(x):
            dur = int(x.max() // 1000) + 2
            act = np.zeros(dur, dtype=bool)
            act[(x // 1000).astype(int)] = True
            inp = st.StageInput(dur, {"presses": x / 1000.0, "active": act, "keys": np.zeros(dur), "f1": np.zeros(dur),
                                      "f4": np.zeros(dur)})
            _, r = st.candidate_series(inp, "S-raw-hold-sub", 1, 1)
            return r[np.minimum(-(-x // 100), len(r) - 1)]
        ra_, rb_ = tempo_at_presses(a), tempo_at_presses(b)
        check(np.mean(ra_ == rb_) < 0.5, f"N1 (positive control): S-raw-hold-sub's tempo differs after s = {s} "
                                         f"({np.mean(ra_ == rb_):.3f} of the presses equal)")
    # N2: only the intervals below N2_BURST_MS doubled
    n2 = {d: {"compared": 0, "differ": 0, "seconds": 0, "same_run_scaled": 0, "same_run_equal": 0} for d in st.D_SETS}
    for sid in sids:
        pm = np.sort(np.load(work / "labels" / f"{sid}.npz")["presses_ms"].astype(np.int64))
        d = np.diff(pm)
        d2 = np.where(d < N2_BURST_MS, 2 * d, d)
        pm2 = np.concatenate([[pm[0]], pm[0] + np.cumsum(d2)])
        scaled = np.concatenate([[False], d < N2_BURST_MS])  # per press index: its interval was doubled
        for dset in st.D_SETS:
            dur1, dur2 = int(pm.max() // 1000) + 2, int(pm2.max() // 1000) + 2
            w1, w2 = window_sets(pm, dur1, dset), window_sets(pm2, dur2, dset)
            for k, k2 in match_seconds(w1, w2, dur1, dur2):
                n2[dset]["seconds"] += 1
                if k2 is None:
                    continue
                i1 = w1["idx"][w1["lo"][k]: w1["hi"][k]]
                i2 = w2["idx"][w2["lo"][k2]: w2["hi"][k2]]
                if not np.array_equal(i1, i2):
                    continue
                ds1, ds2 = w1["ds"], w2["ds"]
                if ds1.n_set[k] < st.MIN_IVL or ds2.n_set[k2] < st.MIN_IVL or ds1.n_pairs[k] < st.MIN_PAIRS \
                        or ds2.n_pairs[k2] < st.MIN_PAIRS:
                    continue
                n2[dset]["compared"] += 1
                same = ds1.a[k] == ds2.a[k2] and ds1.r[k] == ds2.r[k2]
                n2[dset]["differ"] += int(not same)
                if dset == "run":
                    sel1 = st.d_select(w1["vals"][w1["lo"][k]: w1["hi"][k]], "run")
                    sel2 = st.d_select(w2["vals"][w2["lo"][k2]: w2["hi"][k2]], "run")
                    if np.array_equal(sel1, sel2) and scaled[i1[sel1]].all():
                        n2[dset]["same_run_scaled"] += 1
                        n2[dset]["same_run_equal"] += int(same)
    a_, r_ = n2["all"], n2["run"]
    check(a_["compared"] > 0 and a_["differ"] > 0,
          f"N2: D-all changes when only the burst intervals double ({a_['differ']} of {a_['compared']} compared seconds, "
          f"{a_['differ'] / max(a_['compared'], 1):.3f})")
    check(r_["same_run_scaled"] > 0 and r_["same_run_equal"] == r_["same_run_scaled"],
          f"N2: D-run is unchanged where its set is the same and wholly doubled ({r_['same_run_equal']} of "
          f"{r_['same_run_scaled']})")
    print(f"     (N2 D-run) of {r_['compared']} compared seconds: the set the same and wholly doubled in "
          f"{r_['same_run_scaled'] / max(r_['compared'], 1):.3f}; changed in {r_['differ'] / max(r_['compared'], 1):.3f}")


# ---------------------------------------------------------------------------
# The self-test generation (g050 and f200 at the smoke size, TEST_SEED)
# ---------------------------------------------------------------------------

def generate(config: Path, seed_file: Path, work: Path, step: str, hmm: str) -> None:
    v = STEPS[step]
    extra = ["--world", WORLDS[step], "--t" if WORLDS[step] == "graded" else "--c", repr(float(v))]
    subprocess.run([sys.executable, str(HERE / "gen_sessions.py"), str(config), str(seed_file), str(work),
                    "--hmm-version", hmm, "--smoke", *extra], check=True, capture_output=True)


def test_generation(cfg: dict, config: Path, tmp: Path, hmm: str) -> dict:
    seed_file = tmp / "SEED.test"
    seed_file.write_text(f"{TEST_SEED}\n", encoding="utf-8")
    g = gs.graded_segments(cfg, 0.5)
    check(abs(g["STRUGGLE"]["flight_median_ms"] - GRADED_05[0]) < 1e-12 and abs(g["STRUGGLE"]["flight_sigma"] - GRADED_05[1]) < 1e-12,
          "graded t = 0.5: STRUGGLE's flight median 219.09 ms and sigma 0.30")
    works = {}
    for step in STEPS:
        w = tmp / f"gen-{step}"
        generate(config, seed_file, w, step, hmm)
        doc = json.loads((w / "world.json").read_text(encoding="utf-8"))
        check(doc == ck.step_doc(cfg, step) == ce.world_doc(WORLDS[step], STEPS[step]),
              f"generation {step}: world.json {doc} is the step's world doc")
        check(ck.world_problems(w, cfg, step) == [] and ck.world_problems(w, cfg, [s for s in STEPS if s != step][0]) != [],
              f"generation {step}: world_problems passes its step and refuses the other")
        works[step] = w
    check((works["f200"] / "speed_jumps.json").exists() and not (works["g050"] / "speed_jumps.json").exists(),
          "generation: speed_jumps.json in the factor world only")
    # (d2): session_u is the u of gen_sessions.Speed
    seg_cfg = json.loads(json.dumps(cfg))
    seg_cfg["segments"] = gs.graded_segments(cfg, cfg["speed_confound"]["base_t"])
    ok = all(abs(ck.session_u(TEST_SEED, f"P{i:03d}") - gs.Speed(TEST_SEED, ("P", i), 2.0, seg_cfg, 10, "factor")._u) == 0
             for i in range(12))
    check(ok, "(d2): session_u equals gen_sessions.Speed's u of each P session")
    return works


# ---------------------------------------------------------------------------
# Twins, the judge, the bases, the statistics, the pilot and the gate
# ---------------------------------------------------------------------------

def test_twins(tmp: Path) -> None:
    rng = np.random.default_rng(14)
    t = np.sort(rng.choice(200000, 3000, replace=False)).astype(np.int64)
    tt = tw.redraw(t, rng)
    check(np.array_equal(np.bincount(t // 1000, minlength=200), np.bincount(tt // 1000, minlength=200))
          and np.all(np.diff(tt) > 0), "twins: every second keeps its press count and the order")


def att(g, lo, hi):
    return {a: {"gain": g, "ci95": [lo, hi]} for a in ck.ATTACKERS}


def test_judge(cfg: dict) -> None:
    cands = ["D-run-hold-sec", "S-raw-hold-sub"]
    c0, c1 = cands

    def base():
        d = {"PC1": att(0.2, 0.15, 0.25)}
        for c in cands:
            d[c] = att(0.0, -0.01, 0.02)
            d[f"PCs-{c}"] = att(0.05, 0.035, 0.07)
            d[f"PC0-{c}"] = att(0.0, -0.01, 0.02)
        return d
    nulls = {n: [{a: 0.0 for a in ck.ATTACKERS}] * 20 for n in base()}
    auc = {"hgb": 0.7, "lr": 0.7}

    def v(patch, nl=nulls, au=auc, ff=False, forced=None):
        d = base()
        d.update(patch)
        return ck.judge(d, nl, au, cands, cfg, ff, forced=forced)
    j = v({})
    check(j["verdicts"][c0] == "green" and j["verdicts"]["PC1"] == "works", "judge: everything works -> green")
    check(v({c0: att(0.02, -0.01, 0.03)})["verdicts"][c0] == "red_unconfirmed", "judge: 0.03 exactly -> red (unconfirmed)")
    check(v({c0: att(0.05, 0.031, 0.07)})["verdicts"][c0] == "red_detected", "judge: lower > 0.03 -> red detected")
    check(v({c0: att(0.05, 0.03, 0.07)})["verdicts"][c0] == "red_unconfirmed", "judge: lower 0.03 exactly -> unconfirmed")
    check(v({"PC1": att(0.15, 0.10, 0.2)})["detector"][c0]["reasons"] == ["weak_detector"],
          "judge: PC1 lower 0.10 exactly does not work")
    jj = v({f"PCs-{c0}": att(0.081, 0.04, 0.1)})
    check(jj["verdicts"][c0] == "undecidable" and jj["detector"][c0]["reasons"] == ["weak_stall_pc"]
          and jj["verdicts"][c1] == "green", "judge: a PC-stall above 0.08 -> its candidate undecidable")
    jj = v({f"PC0-{c0}": att(0.01, 0.0, 0.03)})
    check(jj["detector"][c0]["reasons"] == ["stall_baseline"], "judge: a PC0 upper of 0.03 exactly -> stall_baseline")
    jj = v({}, au={"hgb": 0.90, "lr": 0.7})
    check(jj["ceiling_kinds"] == ["hgb"] and jj["attackers_used"] == ["full/lr", "small/lr"],
          "judge: 0.90 exactly is the ceiling of the base; that classifier is left out")
    jj = v({}, au={"hgb": 0.95, "lr": 0.91})
    check(jj["detector"][c0]["reasons"] == ["ceiling"], "judge: both classifiers at the base's ceiling -> undecidable")
    jj = v({c0: {**att(0.0, -0.01, 0.02), "small/lr": {"gain": 0.0, "ci95": [float("nan"), 0.02]}}})
    check(jj["verdicts"][c0] == "undecidable" and jj["verdicts"][c1] == "undecidable", "judge: a NaN bound -> undecidable")
    jj = ck.judge({k: x for k, x in base().items() if not k.startswith("PCs-")}, None, {"hgb": 0.99, "lr": 0.99}, cands,
                  cfg, False, forced="pilot_stop")
    check(jj["detector"][c0]["reasons"] == ["pilot_stop", "ceiling"] and jj["null_all_73_ok"] is None,
          "judge: the S base whose pilot part stopped at the ceiling -> pilot_stop then ceiling, no overall null")
    check(v({}, nl=None)["detector"][c0]["reasons"] == ["null"], "judge: no null run -> not judged")
    check(ck.kind_of("D-all-hold-sec") == "candidate" and ck.kind_of("PCs-D-run-hold-sec") == "pcs"
          and ck.kind_of("PCs-D-run-hold-sec@0.150") == "descriptive" and ck.kind_of("PC0-D-all-hold-sec") == "pc0",
          "names: plan D's candidate, PC-stall and PC0 are read as such")
    for bad in ("PC1-1800", "PCl-S-raw-hold-sec", "PCrl-S-raw-hold-sec"):
        try:
            ck.kind_of(bad)
            refused = False
        except ValueError:
            refused = True
        check(refused, f"names: {bad} is not a name of this task")


def synth_scratch(d: Path, rng: np.random.Generator) -> tuple[dict, dict, list[str], dict]:
    """A made-up L300 table: model A (3 columns, one weak signal), A_speed = A + 2 columns (a strong signal), and
    stage features (20 columns, an independent signal in two of them)."""
    n_s, n_w = 40, 30
    G = np.repeat(np.arange(n_s), n_w)
    n = len(G)
    za, zs, zf = rng.normal(size=n), rng.normal(size=n), rng.normal(size=n)
    y = (0.6 * za + 1.6 * zs + 1.0 * zf + rng.normal(size=n) > 0.5).astype(int)
    XA = np.column_stack([za + rng.normal(size=n), rng.normal(size=n), rng.normal(size=n)])
    XS = np.column_stack([XA, zs + 0.3 * rng.normal(size=n), rng.normal(size=n)])
    strata = rng.integers(0, 3, size=n)
    ck.save(d, "L300-A", XA)
    ck.save(d, "L300-S", XS)
    ck.save(d, "L300-rows", np.arange(n))
    ck.save(d, "L300-G", G)
    ck.save(d, "G_all", G)
    cands = ["S-raw-hold-sub", "S-raw-hold-sec"]  # anchor names: the copied checks.py does not know D- names
    names = {}
    for i, nm in enumerate(cands + ["PC1"] + [f"PCs-{c}" for c in cands] + [f"PC0-{c}" for c in cands]):
        F = rng.normal(size=(n, 20))
        if nm in cands or nm == "PC1":
            F[:, 0] += zf * (1.0 if nm != cands[1] else 0.2)
            F[:, 13] += 0.5 * zf
        ck.save(d, f"F-{i}", F)
        names[nm] = f"F-{i}"
    tab = {"Y": y, "G": G, "strata": strata}
    for k, v in tab.items():
        np.save(d / f"tab-{k}.npy", v)
    return tab, names, cands, {"XA": XA, "XS": XS}


def test_build_x_drop(tmp: Path) -> None:
    """design 1.6 (decisions 14, /cross-review round 2): a drop leaves out the features and their differences to the
    earlier windows, for small and full."""
    d = tmp / "build-x"
    d.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(5)
    G = np.repeat(np.arange(4), 6)
    n = len(G)
    XA, F = rng.normal(size=(n, 3)), rng.normal(size=(n, 20))
    rows = np.arange(2, n)
    ck.save(d, "L-A", XA[rows])
    ck.save(d, "L-rows", rows)
    ck.save(d, "G_all", G)
    ck.save(d, "F", F)
    ck._init(str(d))
    try:
        for drop in ("smooth", "a", "r"):
            keep = ck.keep_cols(drop)
            Fk = F[:, keep]
            want_s = np.hstack([XA[rows], Fk[rows]])
            want_f = np.hstack([XA[rows], Fk[rows], ck.diffs(Fk, G, 2)[rows]])
            xs, xf = ck.build_x("L", "A", "F", "small", drop), ck.build_x("L", "A", "F", "full", drop)
            check(np.array_equal(xs, want_s) and np.array_equal(xf, want_f) and xf.shape[1] == 3 + 3 * len(keep),
                  f"build_x: drop {drop} leaves out its {20 - len(keep)} features and their differences "
                  f"(small {xs.shape[1]}, full {xf.shape[1]} columns)")
        full = ck.build_x("L", "A", "F", "full", None)
        check(full.shape[1] == 3 + 60 and not np.array_equal(full[:, :45], ck.build_x("L", "A", "F", "full", "smooth")),
              "build_x: no drop keeps all 20 and their 40 differences (negative control)")
    finally:
        ck._MM.clear()


SRC_RUN = r"""
import json, sys
from pathlib import Path
import numpy as np
import checks
d = Path(sys.argv[1])
cfg = json.loads((d / "cfg.json").read_text(encoding="utf-8"))
names = json.loads((d / "names.json").read_text(encoding="utf-8"))
cands = json.loads((d / "cands.json").read_text(encoding="utf-8"))
tab = {k: np.load(d / f"tab-{k}.npy") for k in ("Y", "G", "strata")}
seed, jobs, nboot, nperm = (int(x) for x in sys.argv[2:6])
r = checks.e13_target("L300", tab, names, [], cfg, seed, jobs, nboot, nperm, d, cands)
checks.dump(d / "src.json", r)
"""

COMPARED_KEYS = ("configs", "ceiling_kinds", "attackers_used", "nan", "fit_failed", "pc1_ok", "null_all_73_ok",
                 "detector")


def test_bases(cfg: dict, tmp: Path, jobs: int, source: bool = True) -> None:
    """design 3.7: the two bases are fitted on their own tables (each AUC equals a direct fit; the mutant that swaps
    them fails here), and base S equals the copied checks.py's e13_target byte for byte."""
    d = (tmp / "bases").resolve()
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    rng = np.random.default_rng(31)
    tab, names, cands, X = synth_scratch(d, rng)
    seed, nboot, nperm = 3, 30, 2
    ra_ = ck.e13_target("L300", tab, names, cfg, seed, jobs, nboot, nperm, d, cands, base="A")
    rs_ = ck.e13_target("L300", tab, names, cfg, seed, jobs, nboot, nperm, d, cands, base="S")
    ck._init(str(d))
    y, G = tab["Y"], tab["G"]
    ones = np.ones(len(y))
    ok = True
    for b, r, XB in (("A", ra_, X["XA"]), ("S", rs_, X["XS"])):
        for k in ck.KINDS:
            direct = ck.weighted_auc(ck.oof_predict(XB, y, G, k, seed, 5), y, ones)
            ok &= r["auc_base"][k] == direct
        for c in (cands[0],):
            F = np.load(d / f"{names[c]}.npy")
            for fs, k in (("small", "lr"), ("full", "hgb")):
                Xc = np.hstack([XB, F] + ([ck.diffs(F, G, 2)] if fs == "full" else []))
                direct = ck.weighted_auc(ck.oof_predict(Xc, y, G, k, seed, 5), y, ones)
                ok &= r["configs"][c]["attackers"][f"{fs}/{k}"]["auc_B"] == direct
    check(ok, "bases: AUC(base) and AUC(base + the stage) of each base equal direct fits on that base's own table")
    ga = ra_["configs"][cands[0]]["gain_max"]
    gs_ = rs_["configs"][cands[0]]["gain_max"]
    check(ra_["base"] == "A" and rs_["base"] == "A_speed" and ga > gs_ + 0.01 and rs_["auc_base"]["lr"] > ra_["auc_base"]["lr"],
          f"bases: the made-up stage gains more over A ({ga:+.3f}) than over A_speed ({gs_:+.3f})")
    sma = ck.speed_minus_a(ra_, rs_, tab)
    check(all(abs(sma[k]["diff"] - (rs_["auc_base"][k] - ra_["auc_base"][k])) < 1e-15 and sma[k]["ci95"][0] <= sma[k]["diff"]
              <= sma[k]["ci95"][1] for k in ck.KINDS), "(d1): AUC(A_speed) - AUC(A) and its interval")
    rat = ck.ratio_to_speed(ra_, sma, cands, cfg)
    a0 = "small/lr"
    want = ra_["configs"][cands[0]]["attackers"][a0]["gain"] / sma["lr"]["diff"] if sma["lr"]["diff"] >= 0.03 else None
    check(rat[cands[0]][a0] == want, "(d1): the ratio is the gain over A over AUC(A_speed) - AUC(A) (none below 0.03)")
    low = {k: {"diff": 0.02, "ci95": [0, 0.04]} for k in ck.KINDS}
    check(all(v is None for v in ck.ratio_to_speed(ra_, low, cands, cfg)[cands[0]].values()),
          "(d1): no ratio when the difference is below 0.03")
    if not source:
        return
    for f, v in (("cfg.json", cfg), ("names.json", names), ("cands.json", cands)):
        (d / f).write_text(json.dumps(v), encoding="utf-8")
    # no .pyc written to the source directory, and none read from its __pycache__ (the cache goes under d)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPYCACHEPREFIX": str(d / "pycache")}
    r = subprocess.run([sys.executable, "-c", SRC_RUN, str(d), str(seed), str(jobs), str(nboot), str(nperm)],
                       cwd=str(SRC_DIR), env=env, capture_output=True, text=True)
    if r.returncode != 0:
        check(False, f"bases: the copied checks.py ran ({r.stderr[-400:]})")
        return
    src = json.loads((d / "src.json").read_text(encoding="utf-8"))
    ours = ck.clean(ck.public(rs_))
    same = all(json.dumps(ours[k], sort_keys=True) == json.dumps(src[k], sort_keys=True) for k in COMPARED_KEYS)
    check(same and json.dumps(ours["auc_base"], sort_keys=True) == json.dumps(src["auc_A_speed"], sort_keys=True)
          and json.dumps(ck.clean(ra_["auc_base"]), sort_keys=True) == json.dumps(src["auc_A"], sort_keys=True),
          "bases: base S equals the copied e13_target's A_speed verdict byte for byte (configs, nulls, detector, AUC)")
    src2 = json.loads(json.dumps(src))
    src2["configs"][cands[0]]["verdict"] = "x"
    check(json.dumps(ours["configs"], sort_keys=True) != json.dumps(src2["configs"], sort_keys=True),
          "bases: the comparison tells a changed verdict apart (negative control)")


def test_stats(cfg: dict) -> None:
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 2000)
    sc_ = rng.random(2000)
    w = rng.integers(1, 4, 2000).astype(float)
    from sklearn.metrics import roc_auc_score
    check(abs(ck.weighted_auc(sc_, y, w) - roc_auc_score(y, sc_, sample_weight=w)) < 1e-9, "stats: weighted AUC equals sklearn")
    strata = rng.integers(0, 4, 2000)
    yp = ck.stratified_permutation(y, strata, rng)
    check(all(y[strata == s].sum() == yp[strata == s].sum() for s in range(4)), "stats: the permutation keeps the strata")
    F = rng.normal(size=(10, 20))
    g = np.array([0] * 4 + [1] * 6)
    D = ck.diffs(F, g, 2)
    check(np.array_equal(D[4], np.zeros(40)) and np.array_equal(D[5, :20], F[5] - F[4]), "B-full: differences, none across sessions")
    check(ck.keep_cols("a") == list(range(10, 20)) and ck.keep_cols("r") == list(range(10)) and len(ck.keep_cols(None)) == 20,
          "drops: the a side is columns 0-9, the r side 10-19 (design 1.6)")
    kept = [st.FEAT_NAMES[i] for i in ck.keep_cols("smooth")]
    check(sorted(ck.DROP_COLS) == ["a", "r", "smooth"] and len(kept) == 14
          and not set(kept) & set(cfg["describe"]["d2_smooth"]) and "a_since_change" in kept and "a_mean" in kept,
          "drops: smooth leaves out exactly the six smoothness features of (d2) (design 1.6, decisions 14)")
    test_select_lambda(cfg)


def rec(g, lo):
    return {"gain_max": g, "lower_max": lo, "upper_max": g + 0.008, "n_nan_bounds": 0}


def merged_for(shift: dict, grid: list[float]) -> dict:
    m = {"PC1": rec(0.3, 0.25)}
    for c in st.candidates():
        m[ck.pilot_key(c, 0.0)] = rec(0.004, -0.004)
        for i, x in enumerate(grid):
            g = round(0.055 + 0.01 * (i - 4 - shift[c]) + 0.001, 6)
            m[ck.pilot_key(c, x)] = rec(g, g - 0.008)
    return m


def test_select_lambda(cfg: dict) -> None:
    ps = cfg["pc_stall"]
    grid = [float(x) for x in ps["pilot_grid"]]
    check(grid == [round(0.025 * i, 3) for i in range(1, 13)] and ps["aim"] == 0.055 and ps["lower"] == 0.03
          and ps["upper"] == 0.08, "select_lambda: the grid 0.025 to 0.300, the aim 0.055, the band (0.03, 0.08]")
    sel = lambda g, lo: ck.select_lambda(grid, g, lo, ps["aim"], ps["lower"], ps["upper"])
    a = [round(0.01 * (i + 1) + 0.003, 6) for i in range(12)]
    lo_a = [round(x - 0.008, 6) for x in a]
    check(sel(a, lo_a)["lam"] == 0.125, "select_lambda: in the band, the fitted value closest to 0.055")
    flat = [0.01, 0.02, 0.03, 0.04, 0.055, 0.055, 0.055, 0.07, 0.08, 0.09, 0.10, 0.11]
    check(sel(flat, [x - 0.008 for x in flat])["lam"] == 0.15, "select_lambda: three tied -> the middle")
    check(sel([float("nan")] * 12, [float("nan")] * 12)["lam"] is None, "select_lambda: no finite value -> no choice")
    cands = st.candidates()
    shift = {c: i % 5 for i, c in enumerate(cands)}
    merged = merged_for(shift, grid)
    want = {c: grid[4 + shift[c]] for c in cands}
    check({c: s["lam"] for c, s in ck.choose_all(merged, cfg).items()} == want, "pilot: each candidate gets its own lambda")
    ok = {"PC1": {"fit_failed": False}}
    check(ck.pilot_stop({"PC1": {"lower_max": 0.10}}, ok, cfg, []) == "weak_detector"
          and ck.pilot_stop({"PC1": {"lower_max": 0.2}}, ok, cfg, ["hgb", "lr"]) == "ceiling"
          and ck.pilot_stop({"PC1": {"lower_max": 0.2}}, {"x": {"fit_failed": True}}, cfg, []) == "fit_failed",
          "pilot stop: weak PC1 (0.10 exactly), the base's ceiling, a failed fit")


def part_doc(merged: dict, cfg: dict, auc=None, skipped=None) -> dict:
    auc = auc or {"hgb": 0.7, "lr": 0.7}
    per = {k: {"fit_failed": False} for k in (["PC1"] if skipped else ["PC1"] + st.candidates())}
    stop, sels, ceil = ck.part_result(merged, per, auc, cfg)
    return {"stop": stop, "selection": sels, "auc_base": auc, "ceiling_kinds": ceil, "per_batch": per,
            "skipped_after": skipped, "configs": {k: ({kk: v[kk] for kk in ck.REC_KEYS} if v else None)
                                                  for k, v in merged.items()}}


def pilot_doc(cfg: dict, step: str, parts: dict, base_seed: int) -> dict:
    sp = cfg["sets"]["pilot"]
    return {"world_doc": ck.step_doc(cfg, step), "step": step, "stop": parts["A"]["stop"],
            "rule": {k: cfg["pc_stall"][k] for k in ck.RULE_KEYS}, "seed": base_seed + sp["seed_offset"],
            "n_sessions": sp["P"], "bootstrap": sp["bootstrap"], "config_fingerprint": ce.cfg_fingerprint(cfg),
            "code_fingerprint": ce.code_fingerprint(), "parts": parts}


def test_apply_pilot(cfg: dict) -> None:
    """design 1.5: pilot.json -> lam.<step>.A and .S -> the main run's check; the S part stopping leaves S out."""
    cands = st.candidates()
    grid = [float(x) for x in cfg["pc_stall"]["pilot_grid"]]
    base_seed = 20261122
    sh_a = {c: i % 5 for i, c in enumerate(cands)}
    sh_s = {c: (i + 2) % 5 for i, c in enumerate(cands)}
    ma, ms_ = merged_for(sh_a, grid), merged_for(sh_s, grid)
    want_a = {c: grid[4 + sh_a[c]] for c in cands}
    want_s = {c: grid[4 + sh_s[c]] for c in cands}
    pa, ps_ = part_doc(ma, cfg), part_doc(ms_, cfg)
    good = pilot_doc(cfg, "f200", {"A": pa, "S": ps_}, base_seed)
    ceil_s = part_doc({"PC1": rec(0.3, 0.25)}, cfg, auc={"hgb": 0.999, "lr": 0.997}, skipped="PC1")
    check(ceil_s["stop"] == "ceiling", "pilot: an S part skipped after PC1 at the ceiling stops with ceiling")
    stopped_s = pilot_doc(cfg, "g050", {"A": pa, "S": ceil_s}, base_seed)
    pre = json.loads(json.dumps(cfg))
    pre["pc_stall"]["lam"] = {"g050": {"A": {c: grid[0] for c in cands}}}
    with tempfile.TemporaryDirectory() as d:
        cp, pp = Path(d) / "config.json", Path(d) / "pilot.json"
        (Path(d) / "SEED").write_text(f"{base_seed}\n", encoding="utf-8")
        fresh = lambda c=pre: cp.write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        fresh()
        pp.write_text(json.dumps(good), encoding="utf-8")
        ck.apply_pilot(cp, pp, "f200")
        back = json.loads(cp.read_text(encoding="utf-8"))
        check(back["pc_stall"]["lam"] == {"g050": pre["pc_stall"]["lam"]["g050"], "f200": {"A": want_a, "S": want_s}}
              and want_a != want_s, "pilot: --apply-pilot writes lam.f200.A and lam.f200.S (each its own), keeps g050")
        check(ck.main_lams(back, pp, base_seed, "f200") == ({"A": want_a, "S": want_s}, None),
              "main: the step's pilot.json and config.json agree per base")
        h = json.loads(json.dumps(back))
        h["pc_stall"]["lam"]["f200"]["A"], h["pc_stall"]["lam"]["f200"]["S"] = want_s, want_a
        try:
            ck.main_lams(h, pp, base_seed, "f200")
            refused = False
        except SystemExit:
            refused = True
        check(refused, "main: pc_stall.lam with the bases swapped stops the run")
        fresh()
        pp.write_text(json.dumps(stopped_s), encoding="utf-8")
        ck.apply_pilot(cp, pp, "g050")
        back2 = json.loads(cp.read_text(encoding="utf-8"))
        check(back2["pc_stall"]["lam"]["g050"] == {"A": want_a}
              and ck.main_lams(back2, pp, base_seed, "g050") == ({"A": want_a}, "ceiling"),
              "pilot: a stopped S part writes lam.g050.A only; the main run reads the S stop")
        swap = lambda part, **kw: {**good, "parts": {**good["parts"], part: {**good["parts"][part], **kw}}}
        flip = lambda s_, c: {**s_, c: {**s_[c], "lam": grid[0] if s_[c]["lam"] != grid[0] else grid[1]}}
        edited = json.loads(json.dumps(pre))
        edited["e13"]["pc_lower"] = 0.11
        bad_cases = (
            ("another step", {**good, "step": "g050"}),
            ("another world doc", {**good, "world_doc": {"world": "factor", "c": 1.0}}),
            ("a stopped A part", {**swap("A", stop="weak_detector"), "stop": "weak_detector"}),
            ("an A stop that differs from the pilot's", {**good, "stop": "fit_failed"}),
            ("an S part claimed stopped while its values do not stop", swap("S", stop="weak_detector")),
            ("an A selection that does not follow from its maxima", swap("A", selection=flip(pa["selection"], cands[0]))),
            ("the A selection put in the S part", swap("S", selection=pa["selection"])),
            ("a missing S part", {**good, "parts": {"A": pa}}),
            ("an extra L1800 part", {**good, "parts": {**good["parts"], "L1800": pa}}),
            ("another seed", {**good, "seed": base_seed}),
            ("another P", {**good, "n_sessions": 40}),
            ("another rule", {**good, "rule": {**good["rule"], "aim": 0.05}}),
            ("another config (fingerprint)", {**good, "config_fingerprint": ce.cfg_fingerprint(edited)}),
            ("other instruments (code fingerprint)", {**good, "code_fingerprint": "0" * 64}))
        for name, bad in bad_cases:
            fresh()
            pp.write_text(json.dumps(bad), encoding="utf-8")
            try:
                ck.apply_pilot(cp, pp, "f200")
                refused = False
            except SystemExit:
                refused = True
            now = json.loads(cp.read_text(encoding="utf-8"))
            check(refused and now["pc_stall"] == pre["pc_stall"], f"pilot: --apply-pilot refuses {name}")
    check(ce.cfg_fingerprint(back) == ce.cfg_fingerprint(pre) == ce.cfg_fingerprint({**pre, "_comment": "x"}),
          "fingerprint: the lambda tables and the comments do not change it")
    deep = json.loads(json.dumps(pre))
    deep["plan_d"]["n_win"] = 30
    check(ce.cfg_fingerprint(deep) != ce.cfg_fingerprint(pre), "fingerprint: a plan D setting changes it")
    test_main_specs(want_a, want_s)


def test_main_specs(want_a: dict, want_s: dict) -> None:
    """design 1.5: the main run fits the PC-stall of each base at that base's own lambda (the mutant that shares A's
    fails here); a base whose pilot part stopped has none."""
    cands = st.candidates()
    specs, per = ck.main_specs(cands, {"A": want_a, "S": want_s}, None)
    by_key = {s[0]: s for s in specs}
    ok = all(by_key[per[b]["PCs-" + c]][2] == lam[c] and by_key[per[b]["PCs-" + c]][1] == f"PCs-{c}"
             for b, lam in (("A", want_a), ("S", want_s)) for c in cands)
    check(ok and len(set(s[0] for s in specs)) == len(specs), "main specs: each base's PC-stall at its own lambda, once")
    same = {c: want_a[c] for c in cands}
    specs2, _ = ck.main_specs(cands, {"A": want_a, "S": same}, None)
    check(len(specs2) == len(cands) * 2 + 2 + len(cands), "main specs: one run when the two bases chose the same lambda")
    specs3, per3 = ck.main_specs(cands, {"A": want_a}, "ceiling")
    check(not any(k.startswith("PCs-") for k in per3["S"]) and all(f"PCs-{c}" in per3["A"] for c in cands),
          "main specs: a stopped S part has no PC-stall")


def test_ceiling_gate(cfg: dict) -> None:
    """design 3.0: a step runs only when ceiling.json says go (by AUC(A)) and was made under this config."""
    base_seed = 20261122
    mk = lambda a, s: {"L300": {"hgb": {"auc_A": a, "auc_A_speed": s}, "lr": {"auc_A": a, "auc_A_speed": s}}}
    res = {"g050": mk(0.76, 0.998), "f200": mk(0.75, 0.85)}
    doc = {"seed": base_seed + cfg["ceiling"]["seed_offset"], "main_auc": cfg["ceiling"]["main_auc"],
           "P": {s: cfg["ceiling"]["P"] for s in cfg["ceiling"]["steps"]}, "config_fingerprint": ce.cfg_fingerprint(cfg),
           "code_fingerprint": ce.code_fingerprint(), "results": res, "steps": ce.choose_steps(res, cfg)}
    check(ck.ceiling_problems(doc, cfg, base_seed, "g050") == [] and ck.ceiling_problems(doc, cfg, base_seed, "f200") == [],
          "ceiling gate: g050 with AUC(A_speed) alone at the ceiling goes on; f200 goes on")
    ceil_a = {**res, "g050": mk(0.92, 0.999)}
    doc2 = {**doc, "results": ceil_a, "steps": ce.choose_steps(ceil_a, cfg)}
    check(ck.ceiling_problems(doc2, cfg, base_seed, "g050") != [] and ck.ceiling_problems(doc2, cfg, base_seed, "f200") == [],
          "ceiling gate: a step whose AUC(A) is at the ceiling stops (design 3.0)")
    for name, d_ in (
            ("a go status over AUC(A) at the ceiling", {**doc, "results": ceil_a}),
            ("a step missing", {**doc, "steps": {"f200": doc["steps"]["f200"]}}),
            ("another t", {**doc, "steps": {**doc["steps"], "g050": {**doc["steps"]["g050"], "t": 0.75}}}),
            ("another seed", {**doc, "seed": base_seed}),
            ("another config (fingerprint)", {**doc, "config_fingerprint": "0" * 64}),
            ("other instruments (code fingerprint)", {**doc, "code_fingerprint": "0" * 64})):
        check(ck.ceiling_problems(d_, cfg, base_seed, "g050") != [], f"ceiling gate: {name} is refused")


# ---------------------------------------------------------------------------
# gse-replay and the run's own sessions (copied)
# ---------------------------------------------------------------------------

def replay_cols(binary: str, nd: Path, start_ms: int, dur: int) -> dict:
    out = subprocess.run([binary, str(nd)], capture_output=True, check=True)
    arr = {c: np.full(dur, np.nan) for c in ra.COLS}
    for s in json.loads(out.stdout):
        k = (int(s["timestamp"]) - start_ms) // 1000 - 1
        if 0 <= k < dur:
            for c in ra.COLS:
                arr[c][k] = float(s[c])
    return arr


def test_replay_causal(binary: str, work: Path, tmp: Path) -> None:
    """Three sessions cut at T whose last kept key is within 600 s of T (a session away before T is skipped: the
    replay emits no tick after the last event); the F series of the ticks before T as without the cut."""
    T = 3600
    ok, n, skipped = True, 0, 0
    for sid in bl.p_sids(work):
        if n == 3:
            break
        lab = np.load(work / "labels" / f"{sid}.npz")
        start, dur = int(lab["start_ms"]), int(lab["duration_s"])
        lines = (work / "ndjson" / f"{sid}.ndjson").read_text(encoding="utf-8").splitlines()
        keep = [l for l in lines if json.loads(l).get("type") != "key" or json.loads(l)["t"] < start + T * 1000]
        last_t = max(json.loads(l)["t"] for l in keep if json.loads(l).get("type") == "key")
        k_last = (last_t - start) // 1000
        if k_last <= T - 600:
            skipped += 1
            continue
        cut = tmp / f"cut-{sid}.ndjson"
        cut.write_text("\n".join(keep) + "\n", encoding="utf-8", newline="\n")
        full = replay_cols(binary, work / "ndjson" / f"{sid}.ndjson", start, dur)
        part = replay_cols(binary, cut, start, dur)
        emitted = np.isfinite(part["keys"][:T])
        ok &= all(np.array_equal(full[c][:T][emitted], part[c][:T][emitted]) for c in ra.COLS)
        ok &= bool(emitted[:k_last].all())
        n += 1
    check(ok and n == 3, f"causal (gse-replay): with the NDJSON cut at T, every tick before T equals the full session's "
                         f"and none is missing before the last kept key (3 sessions; {skipped} away before T skipped)")


def test_twins_work(work: Path) -> None:
    tw_dir = work / "twins"
    sids = bl.p_sids(work)
    ok = len(sids) > 0 and (tw_dir / "feat").is_dir() and sorted(bl.p_sids(tw_dir)) == sorted(sids)
    for sid in sids if ok else []:
        o = np.load(work / "labels" / f"{sid}.npz")["presses_ms"]
        t = np.load(tw_dir / "labels" / f"{sid}.npz")["presses_ms"]
        ok &= np.array_equal(np.bincount(o // 1000), np.bincount(t // 1000)) and np.all(np.diff(t) > 0)
    check(ok, f"twins (run data): every one of the {len(sids)} P sessions has a replayed twin")


def test_work(work: Path, cfg: dict, seed: int, jobs: int) -> None:
    """The PC-stall at lambda 1 and the seg mutation through the main run's path, on base A (the primary base)."""
    ms = st.manifest_p(work)
    n = len(ms)
    specs = [("PCs-S-raw-hold-sec@1.00", "PCs-S-raw-hold-sec", 1.0), ("PCs-D-run-hold-sec@1.00", "PCs-D-run-hold-sec", 1.0),
             ("S-raw-hold-sec-MUTseg", "S-raw-hold-sec", None, "seg"), ("D-run-hold-sec-MUTseg", "D-run-hold-sec", None, "seg"),
             ("PC0-S-raw-hold-sec", "PC0-S-raw-hold-sec", 0.0), ("PC0-D-run-hold-sec", "PC0-D-run-hold-sec", 0.0),
             ("D-run-hold-sec", "D-run-hold-sec", None)]
    scratch = Path(tempfile.mkdtemp(prefix="selftest-", dir=work))
    try:
        tab = ck.label_tables(work, [m["sid"] for m in ms], cfg, scratch)
        F = ck.run_stage(specs, ms, work, seed, jobs)
        s0 = st.load_session(work, ms[1])
        n0 = st.load_session(work, ms[0]).duration_s // 60
        direct = st.window_features(*st.series(s0, "D-run-hold-sec", seed), s0.duration_s // 60)
        check(np.array_equal(F["D-run-hold-sec"][n0: n0 + len(direct)], direct),
              "wiring: run_stage keeps the session order (the second session's rows are its own windows)")
        if n < 40:
            print(f"SKIP  PC at lambda 1 and the seg mutation (only {n} P sessions; they run with 40 or more)")
            return
        names = {}
        for i, (key, *_) in enumerate(specs):
            ck.save(scratch, f"F-{i}", F[key])
            names[key] = f"F-{i}"
        r = ck.e13_target("L300", tab["L300"], names, cfg, seed, jobs, 50, 0, scratch, [], base="A")
        g = {k: r["configs"][k]["gain_max"] for k in names}
        for k in ("PCs-S-raw-hold-sec@1.00", "PCs-D-run-hold-sec@1.00", "S-raw-hold-sec-MUTseg", "D-run-hold-sec-MUTseg"):
            check(g[k] > 0.10, f"PC / mutation: {k} -> L300 point max over A {g[k]:+.3f} > 0.10 (main path)")
        for k in ("PC0-S-raw-hold-sec", "PC0-D-run-hold-sec"):
            check(g[k] < 0.03, f"{k}: L300 point max over A {g[k]:+.3f} < 0.03 (negative control)")
        print(f"     (D-run-hold-sec unmutated, over A: {g['D-run-hold-sec']:+.3f}; not judged here)")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# ---------------------------------------------------------------------------
# Mutants (design 3.7)
# ---------------------------------------------------------------------------

def _time_window(ends_ms, duration_s):
    t = (np.arange(duration_s, dtype=np.int64) + 1) * 1000
    return np.searchsorted(ends_ms, t - 30_000, side="left"), np.searchsorted(ends_ms, t, side="left")


def _reads_keys(inp):
    inp["keys"]
    return np.asarray(inp["presses"]), np.asarray(inp["active"])


def _fixed_ms(w, dset):
    if dset == "run":
        return w < 600.0
    return np.ones(len(w), dtype=bool)


def _diff_spread(v):
    p10, p90 = np.percentile(v, [10, 90])
    return float(np.clip((p90 - p10) / 1000.0, 0.0, 1.0))


def test_person(cfg: dict, config: Path, tmp: Path, hmm: str) -> None:
    """design 3.7: G0-G5, R1, P1-P5, Q1-Q3, J1-J4 and the seed rules (selftest_person.py)."""
    sp.test_g0(check, cfg, config, tmp, hmm)
    sp.test_g1(check, cfg)
    sp.test_g2(check, cfg)
    sp.test_g3(check, cfg)
    sp.test_g4(check, cfg)
    sp.test_g5(check, cfg)
    sp.test_r1(check)
    sp.test_r1_stage(check, tmp)
    sp.test_records(check, cfg, tmp)
    sp.test_p1(check)
    sp.test_p2(check)
    sp.test_p3(check)
    sp.test_p4(check)
    sp.test_p5(check)
    sp.test_q1(check)
    sp.test_q2(check)
    sp.test_q3(check)
    sp.test_j1(check, cfg)
    sp.test_j2(check, cfg)
    sp.test_j3(check, cfg)
    sp.test_j4(check, cfg)
    sp.test_seed_rules(check, cfg)
    sp.test_person_stage(check, fake_session)
    sp.test_raw(check, cfg)


def mutants(cfg: dict, tmp: Path, jobs: int) -> list[tuple[str, object, str, object, object]]:
    """(name, module, attribute, replacement, the self-test it must fail)."""
    other = {"A": "S", "S": "A"}
    return [
        ("the window back to the last 30 s (a time window)", st, "d_window_bounds", _time_window, test_plan_d),
        ("plan D reads keys", st, "d_inputs", _reads_keys, test_input_closure),
        ("the run boundary at a fixed 600 ms", st, "d_select", _fixed_ms, test_plan_d),
        ("a from the difference p90 - p10 (not the log ratio)", st, "d_spread", _diff_spread, test_plan_d),
        ("the bases swapped for the stage names", ck, "names_base", lambda b: other[b],
         lambda: test_bases(cfg, tmp, jobs, source=False)),
        ("the PC-stall lambda shared between the bases (A's)", ck, "lam_of", lambda lams, b: lams["A"],
         lambda: test_apply_pilot(cfg)),
        ("the step stopped by AUC(A_speed)", ce, "GATE_MODEL", "A_speed", lambda: test_auc_and_choice(cfg)),
    ] + [(f"person {name}", mod, attr, repl, (lambda t: (lambda: t(check)))(thunk))
         for name, mod, attr, repl, thunk in sp.mutant_list(cfg)]


def run_mutants(cfg: dict, tmp: Path, jobs: int) -> int:
    global FAILS
    survived = []
    for name, mod, attr, repl, test in mutants(cfg, tmp, jobs):
        FAILS = []
        test()
        clean_before = not FAILS
        orig = getattr(mod, attr)
        setattr(mod, attr, repl)
        FAILS = []
        try:
            test()
        except Exception as e:  # a crash under the mutant also counts as caught
            FAILS.append(f"raised {type(e).__name__}: {e}")
        finally:
            setattr(mod, attr, orig)
        caught = bool(FAILS)
        print(f"MUTANT {'caught  ' if caught and clean_before else 'SURVIVED'} {name} "
              f"(unmutated {'passes' if clean_before else 'FAILS'}; {len(FAILS)} failing checks: {FAILS[:2]})")
        if not (caught and clean_before):
            survived.append(name)
    FAILS = []
    print(f"mutants: {len(survived)} survived" + (f": {survived}" if survived else ""))
    return 1 if survived else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("tmp")
    ap.add_argument("--hmm-version", required=True)
    ap.add_argument("--gse-replay", default=None, help="the gse-replay causality test (skipped without it)")
    ap.add_argument("--work", default=None, help="the run's replayed sessions: twins, PC at 1 and the mutation")
    ap.add_argument("--seed-file", default=None)
    ap.add_argument("--require-twins", action="store_true", help="the smoke and the main run: the twins must exist")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--mutants", action="store_true", help="design 3.7: the mutants instead of the self-tests")
    a = ap.parse_args()
    config = Path(a.config).resolve()
    cfg = json.loads(config.read_text(encoding="utf-8"))
    tmp = Path(a.tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    if a.mutants:
        return run_mutants(cfg, tmp, a.jobs)
    test_unchanged()
    if FAILS:  # the copied files are not what they were: nothing from them is run
        print(f"selftest: {len(FAILS)} failed: {FAILS}")
        return 1
    test_config(cfg)
    test_speed(cfg)
    test_tables(cfg, tmp)
    test_auc_and_choice(cfg)
    works = test_generation(cfg, config, tmp, a.hmm_version)
    test_input_closure()
    test_stage_causal()
    test_stops()
    test_window_features()
    test_lags(cfg)
    test_pc()
    test_plan_d()
    test_n1_n2(works["g050"])
    test_twins(tmp)
    test_judge(cfg)
    test_bases(cfg, tmp, a.jobs)
    test_stats(cfg)
    test_build_x_drop(tmp)
    test_apply_pilot(cfg)
    test_ceiling_gate(cfg)
    test_person(cfg, config, tmp, a.hmm_version)
    if a.gse_replay:
        test_replay_causal(a.gse_replay, works["g050"], tmp)
    else:
        print("SKIP  causal (gse-replay): no --gse-replay")
    if a.work:
        work = Path(a.work)
        if a.require_twins:
            test_twins_work(work)
        else:
            print("SKIP  twins (run data): not required in this mode")
        seed = int(Path(a.seed_file).read_text().strip()) if a.seed_file else 1
        test_work(work, cfg, seed, a.jobs)
    print(f"selftest: {len(FAILS)} failed" + (f": {FAILS}" if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
