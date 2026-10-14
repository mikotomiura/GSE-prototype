"""Self-tests of the rhythm stage desk check instruments (design 3.7).

Pilot 0 (design 3.0): the world (v1 and v2 write what EH1 round 5 wrote; v3 and v4 are v2 with the declared
changes), the speed quantities and model A_speed, the AUC and the choice rule.
After the freeze: the closed input of the stage, its causality, the stop behaviours and the wobble, the rank, the
window features, the lag measure, the positive controls, the twins, the verdicts (judge), the statistics, the
causality of gse-replay (with --gse-replay), and on the run's own sessions (with --work) the twins, the PC-stall at
lambda 1 and the seg mutation (40 P sessions or more).

A failing test stops the run. A failure is fixed in the instruments; the definitions of design 1 and 3 are not
changed (design 3.7).

Usage: selftest.py <config.json> <EH1 round 5 dir> <tmp dir> --hmm-version V [--gse-replay BIN]
                   [--work DIR --seed-file FILE [--require-twins] [--jobs N]]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

import baseline as bl
import ceiling as ce
import checks as ck
import gen_sessions as gs
import replay_all as ra
import stage as st
import twins as tw

HERE = Path(__file__).resolve().parent
GEN_KEYS = ("session", "segments", "segments_v2", "transitions", "keys", "sets")
V3_CHANGED = ("flight_median_ms", "flight_sigma", "p_pause_after_bs", "pause_after_bs_min_ms",
              "pause_after_bs_extra_ms")
FAILS: list[str] = []


def check(cond: bool, name: str) -> None:
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def generate(script: Path, config: Path, seed_file: Path, work: Path, world: str, hmm: str) -> None:
    subprocess.run([sys.executable, str(script), str(config), str(seed_file), str(work), "--hmm-version", hmm,
                    "--world", world, "--smoke"], check=True, capture_output=True)


def digest(work: Path) -> dict:
    """The bytes of every NDJSON and of sessions.json, and the arrays of every label file (an npz holds zip
    timestamps, so its bytes are not compared)."""
    out = {"sessions.json": hashlib.sha256((work / "sessions.json").read_bytes()).hexdigest()}
    for f in sorted((work / "ndjson").glob("*.ndjson")):
        out[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
    for f in sorted((work / "labels").glob("*.npz")):
        z = np.load(f)
        h = hashlib.sha256()
        for k in sorted(z.files):
            h.update(k.encode())
            h.update(np.ascontiguousarray(z[k]).tobytes())
        out[f.name] = h.hexdigest()
    return out


def press_rows(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Press times (ms from the session start) and vks of one generated NDJSON (selftest only: the vk is read
    here to find the intervals after a backspace; the instruments never read it)."""
    t, v, start = [], [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["type"] == "session_start":
            start = r["t"]
        elif r["type"] == "key" and r["press"]:
            t.append(r["t"] - start)
            v.append(r["vk"])
    return np.asarray(t, dtype=np.int64), np.asarray(v)


def interval_stats(work: Path) -> dict:
    """Per kind (FLOW, STRUGGLE): the intervals below 1 s, and among the gaps after a backspace the share >= 2 s."""
    seg_of = {0: "FLOW", 1: "STRUGGLE"}
    short = {"FLOW": [], "STRUGGLE": []}
    gaps = {"FLOW": [], "STRUGGLE": []}
    after_bs = {"FLOW": [], "STRUGGLE": []}
    vks = {"FLOW": [], "STRUGGLE": []}
    for sid in bl.p_sids(work):
        t, v = press_rows(work / "ndjson" / f"{sid}.ndjson")
        seg = np.load(work / "labels" / f"{sid}.npz")["seg"]
        d = np.diff(t)
        sec = np.minimum(t // 1000, len(seg) - 1)
        for code, kind in seg_of.items():
            vks[kind] += v[seg[sec] == code].tolist()
            m = (seg[sec[:-1]] == code) & (seg[sec[1:]] == code)  # both presses in a segment of this kind
            short[kind] += d[m & (d < 1000)].tolist()
            gaps[kind] += d[m & (d >= 1000)].tolist()
            # the pause after a backspace acts on the gap after a burst whose last press is a backspace, so look
            # at the gaps (intervals of 1 s or longer: a flight of 150 or 320 ms median almost never reaches 1 s) that follow a backspace
            after_bs[kind] += (d[m & (v[:-1] == 8) & (d >= 1000)] >= 2000).tolist()
    q = lambda a, p: float(np.percentile(a, p)) if len(a) else float("nan")
    return {k: {"short_median": float(np.median(short[k])), "short_p10": q(short[k], 10), "short_p90": q(short[k], 90),
                "gap_p10": q(gaps[k], 10), "gap_p50": q(gaps[k], 50), "gap_p90": q(gaps[k], 90),
                "bs_rate": float(np.mean(np.asarray(vks[k]) == 8)), "n_presses": len(vks[k]),
                "after_bs_ge2s": float(np.mean(after_bs[k])), "n_after_bs": len(after_bs[k])} for k in short}


def test_world(cfg: dict, config: Path, eh1: Path, tmp: Path, hmm: str) -> None:
    eh1_cfg = json.loads((eh1 / "config.json").read_text(encoding="utf-8"))
    # round 2 design 1.2: sets.pilot is the only generator setting changed (P 240, bootstrap 2000; the generator never
    # reads it), so it is compared to its round 2 value and the rest to EH1 round 5
    strip = lambda c: {k: ({kk: vv for kk, vv in c[k].items() if kk != "pilot"} if k == "sets" else c[k])
                       for k in GEN_KEYS + ("e13",)}
    check(strip(cfg) == strip(eh1_cfg) and cfg["sets"]["pilot"] == {"seed_offset": 1, "P": 240, "bootstrap": 2000},
          "world: generator settings and e13 equal EH1 round 5 (sets.pilot is round 2's)")
    v2, v3 = cfg["segments_v2"], cfg["segments_v3"]
    same_rest = all(v3[k] == v2[k] for k in v2 if k != "STRUGGLE") and set(v3) == set(v2)
    s2, s3 = v2["STRUGGLE"], v3["STRUGGLE"]
    same_struggle = all(s3[k] == s2[k] for k in s2 if k not in V3_CHANGED) and set(s3) == set(s2) | set(V3_CHANGED)
    check(same_rest and same_struggle, "world v3: only the five declared STRUGGLE fields differ from v2")
    check(s3["flight_median_ms"] == v2["FLOW"]["flight_median_ms"] and s3["flight_sigma"] == v2["FLOW"]["flight_sigma"]
          and all(s3[k] == cfg["segments"]["STRUGGLE"][k] for k in V3_CHANGED[2:]),
          "world v3: STRUGGLE key intervals as FLOW, pause after a backspace as v1")
    seed_file = tmp / "SEED.selftest"
    seed_file.write_text("20261009\n")
    for world in ("v1", "v2"):
        generate(eh1 / "scripts" / "gen_sessions.py", eh1 / "config.json", seed_file, tmp / f"eh1-{world}", world, hmm)
        generate(HERE / "gen_sessions.py", config, seed_file, tmp / f"ours-{world}", world, hmm)
        a, b = digest(tmp / f"eh1-{world}"), digest(tmp / f"ours-{world}")
        check(a == b and len(a) > 3, f"world {world}: the sessions equal EH1 round 5's generator ({len(a)} files, SHA-256)")
    check(digest(tmp / "ours-v1") != digest(tmp / "ours-v2"), "world: the comparison tells v1 from v2 (negative control)")
    generate(HERE / "gen_sessions.py", config, seed_file, tmp / "ours-v3", "v3", hmm)
    st2, st3 = interval_stats(tmp / "ours-v2"), interval_stats(tmp / "ours-v3")
    print(f"     v2 intervals {st2}\n     v3 intervals {st3}")
    f3, g3 = st3["FLOW"]["short_median"], st3["STRUGGLE"]["short_median"]
    check(abs(g3 - f3) / f3 < 0.1, "world v3: STRUGGLE's short-interval median within 10% of FLOW's")
    check(st2["STRUGGLE"]["short_median"] > 1.5 * st2["FLOW"]["short_median"],
          "world v2 (contrast): STRUGGLE's short-interval median above 1.5 x FLOW's")
    check(st3["STRUGGLE"]["after_bs_ge2s"] > st2["STRUGGLE"]["after_bs_ge2s"] + 0.1
          and st3["STRUGGLE"]["n_after_bs"] > 50,
          "world v3: more gaps of 2 s or longer after a backspace in STRUGGLE than v2")
    # world v4 (decisions 16): v2 with FLOW's key intervals in STRUGGLE, no pause after a backspace
    v4 = cfg["segments_v4"]
    s4 = v4["STRUGGLE"]
    check(all(v4[k] == v2[k] for k in v2 if k != "STRUGGLE") and set(v4) == set(v2) and set(s4) == set(s2)
          and all(s4[k] == s2[k] for k in s2 if k not in V3_CHANGED[:2])
          and s4["flight_median_ms"] == v2["FLOW"]["flight_median_ms"] and s4["flight_sigma"] == v2["FLOW"]["flight_sigma"],
          "world v4: only STRUGGLE's flight median and sigma differ from v2 (as FLOW), no pause field")
    timing_keys = [k for k in v4["FLOW"] if k != "p_backspace"]
    check(all(s4[k] == v4["FLOW"][k] for k in timing_keys if k not in ("dur_min_s", "dur_max_s"))
          and s4["p_backspace"] != v4["FLOW"]["p_backspace"],
          "world v4: STRUGGLE's key timing settings equal FLOW's; only the backspace rate (and the lengths) differ")
    generate(HERE / "gen_sessions.py", config, seed_file, tmp / "ours-v4", "v4", hmm)
    st4 = interval_stats(tmp / "ours-v4")
    print(f"     v4 intervals {st4}")
    check(abs(st4["STRUGGLE"]["short_median"] - st4["FLOW"]["short_median"]) / st4["FLOW"]["short_median"] < 0.1,
          "world v4: STRUGGLE's short-interval median within 10% of FLOW's")
    check(abs(st4["STRUGGLE"]["after_bs_ge2s"] - st4["FLOW"]["after_bs_ge2s"]) < 0.1
          and st4["STRUGGLE"]["after_bs_ge2s"] < st3["STRUGGLE"]["after_bs_ge2s"] - 0.2,
          "world v4: gaps after a backspace in STRUGGLE as in FLOW (no pause), unlike v3")
    # Codex (v4 diff): check the generated output, not only the settings
    f4, g4 = st4["FLOW"], st4["STRUGGLE"]
    check(all(abs(g4[k] - f4[k]) / f4[k] < 0.1 for k in ("short_p10", "short_p90", "gap_p10", "gap_p50", "gap_p90")),
          "world v4: the 10/90 percentiles of the short intervals and the 10/50/90 of the gaps within 10% of FLOW's")
    check(abs(g4["bs_rate"] - s4["p_backspace"]) < 0.02 and abs(f4["bs_rate"] - v4["FLOW"]["p_backspace"]) < 0.01
          and min(g4["n_presses"], f4["n_presses"]) > 5000,
          f"world v4: the generated backspace rates {g4['bs_rate']:.3f} / {f4['bs_rate']:.3f} match STRUGGLE / FLOW")


def test_speed(cfg: dict) -> None:
    sp = cfg["speed"]
    # presses (s): a run of 3 at 100 ms, a 1.5 s interval, a run of 2 at 300 ms apart, then a 5 s gap
    p = np.array([10.0, 10.1, 10.2, 11.7, 12.0, 17.0])
    q = bl.speed5(p, 10.0, 25.0, sp)  # the final 10 s [15, 25) hold one press
    d = np.array([100.0, 100.0, 1500.0, 300.0])  # the intervals below 2000 ms (5000 ms is excluded)
    exp = [6.0, float(np.median(d)), float(np.percentile(d, 75) - np.percentile(d, 25)), 6 / 4, 1.0]
    check(np.allclose(q, exp), f"speed5: hand-made span {q} == {exp}")
    check(bl.speed5(p, 0.0, 10.0, sp) == [0.0, 2000.0, 0.0, 0.0, 0.0], "speed5: empty span -> 0, 2000, 0, 0, 0")
    check(bl.speed5(np.array([5.0]), 0.0, 10.0, sp) == [1.0, 2000.0, 0.0, 1.0, 1.0],
          "speed5: one press -> a run of 1, no interval")
    check(bl.speed5(p, 10.0, 10.2, sp)[0] == 2.0, "speed5: the span end is open")
    check(np.isclose(bl.speed5(np.array([0.0, 0.199, 0.4]), 0.0, 1.0, sp)[3], 1.5),
          "speed5: an interval of 199 ms continues a run, 201 ms breaks it")
    # /cross-review (both): 10.2 - 10.0 is 199.9999... ms in floating point; exactly 200 ms must break the run
    # and exactly 2000 ms must not count as short, wherever the presses sit in the session
    ok200 = all(bl.speed5(np.array([t, t + 0.2]), t, t + 1.0, sp)[3] == 1.0 for t in (10.0, 1234.567, 3599.0))
    check(ok200, "speed5: an interval of exactly 200 ms breaks a run at any session time")
    # intervals 1000 and 2000 ms: excluding 2000 gives median 1000 and IQR 0; including it would give 1500 and 500
    # (a single 2000 ms interval would not tell the two apart: /cross-review round 2)
    ok2000 = all(bl.speed5(np.array([t, t + 1.0, t + 3.0]), t, t + 5.0, sp)[1:3] == [1000.0, 0.0]
                 for t in (0.3, 1234.567))
    check(ok2000, "speed5: an interval of exactly 2000 ms is not short")
    check(bl.speed5(np.array([9.9, 10.05]), 10.0, 20.0, sp)[:2] == [1.0, 2000.0],
          "speed5: an interval across the span start does not count")


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
    tr = bursty_trace(rng, 3600)
    ws = bl.window_speed(tr, cfg)
    check(ws.shape == (60, 5 + 2 * cfg["speed"]["lags"]), "A_speed: window quantities have 5 + 2 x lags columns")
    check(np.array_equal(ws[0, 5:7], [0.0, 2000.0]) and np.array_equal(ws[5, 5:7], ws[4, 0:2])
          and np.array_equal(ws[5, 11:13], ws[1, 0:2]), "A_speed: the lags are the earlier windows' quantities 1 and 2")
    check(np.isfinite(ws[:, 1]).all() and (ws[:, 1] < 2000).mean() > 0.5,
          "A_speed: the bursty test trace has short intervals in most windows (the causal test reaches quantities 2-4)")
    short = bl.Trace("S", 120, tr.presses[tr.presses < 120], tr.active[:120], tr.seg[:120])
    sws = bl.window_speed(short, cfg)
    check(sws.shape == (2, 13) and np.array_equal(sws[:, 7:13], np.tile([0.0, 2000.0], (2, 3))),
          "A_speed: a session shorter than the lags keeps the empty value")
    # causality: removing the presses after T leaves every window ending at or before T unchanged
    T = 1800
    cut = bl.Trace("T", tr.duration_s, tr.presses[tr.presses < T], tr.active.copy(), tr.seg)
    cut.active[T:] = False
    for name, f in (("window_speed", lambda s: bl.window_speed(s, cfg)),
                    ("span_speed L300", lambda s: bl.span_speed(s, cfg, 300)),
                    ("span_speed L1800", lambda s: bl.span_speed(s, cfg, 1800)),
                    ("presence_features", lambda s: bl.presence_features(s, cfg)[0]),
                    ("presence_features_long L300", lambda s: bl.presence_features_long(s, cfg, 300)[0]),
                    ("presence_features_long L1800", lambda s: bl.presence_features_long(s, cfg, 1800)[0])):
        check(np.array_equal(f(tr)[: T // 60], f(cut)[: T // 60]), f"causal: {name} before T unchanged by later presses")
    # tables(): two sessions written as the generator writes labels/*.npz
    work = tmp / "tables"
    (work / "labels").mkdir(parents=True, exist_ok=True)
    traces = [bursty_trace(rng, 3600, "P000"), bursty_trace(rng, 2400, "P001")]
    for t in traces:
        np.savez_compressed(work / "labels" / f"{t.sid}.npz", seg=t.seg, presses_ms=np.rint(t.presses * 1000).astype(np.int64),
                            duration_s=np.int64(t.duration_s), start_ms=np.int64(0))
    (work / "sessions.json").write_text(json.dumps([{"sid": t.sid, "set": "P"} for t in traces]), encoding="utf-8")
    tab = bl.tables(work, bl.p_sids(work), cfg)
    n_a = {"L60": 11, "L300": 15, "L1800": 15}
    n_s = {"L60": 24, "L300": 33, "L1800": 33}
    check(all(tab[l]["XA"].shape[1] == n_a[l] and tab[l]["XS"].shape[1] == n_s[l] for l in bl.LABELS),
          "tables: A has 11 / 15 / 15 columns and A_speed 24 / 33 / 33 (L60 / L300 / L1800)")
    check(all(np.array_equal(tab[l]["XS"][:, : n_a[l]], tab[l]["XA"]) and len(tab[l]["XS"]) == len(tab[l]["Y"])
              for l in bl.LABELS), "tables: A_speed starts with A on the same rows")
    first2 = int(np.argmax(tab["L60"]["G"] == 1))
    check(first2 == 60 and np.array_equal(tab["L60"]["XS"][first2, 16:24], np.tile([0.0, 2000.0], 4)),
          "tables: the lags do not leak from one session into the next")
    w = 9  # the 10th window of session 1 ends at 600 s: L300 row = A300 + window quantities + span quantities
    rows300 = np.nonzero(tab["L300"]["rows"])[0]
    r = int(np.nonzero(rows300 == w)[0][0])
    exp = np.concatenate([bl.window_speed(traces[0], cfg)[w], bl.speed5(traces[0].presses, 300, 600, cfg["speed"])])
    check(np.array_equal(tab["L300"]["XS"][r, 15:], exp) and tab["L300"]["G"][r] == 0,
          "tables: an L300 row holds its own window's and span's quantities")
    check(int(tab["L1800"]["rows"].sum()) == (60 - 29) + (40 - 29), "tables: L1800 keeps the windows with a full span")


def test_auc_and_choice(cfg: dict) -> None:
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(3)
    y = rng.integers(0, 2, 500)
    s = np.round(y + rng.normal(0, 1, 500), 1)  # ties included
    check(np.isclose(ce.weighted_auc(s, y, np.ones(500)), roc_auc_score(y, s)), "AUC: equals sklearn with ties")
    X = rng.normal(size=(500, 3))
    g = np.repeat(np.arange(50), 10)
    y1 = (g % 2).astype(int)  # every fold trains on both classes
    y_one = np.zeros(500, dtype=int)
    y_one[:10] = 1  # one positive session: the fold that tests it trains on one class
    check(ce._fit_job(("k", X, y_one, g, "lr", 1, 5))[1] is None, "fit: a training side with one class -> None")
    check(ce._fit_job(("k", X, y1, g, "lr", 1, 5))[1] is not None, "fit: two classes everywhere -> an AUC")
    try:
        ce._fit_job(("k", X[:400], y1, g, "lr", 1, 5))
        raised = False
    except ValueError:
        raised = True
    check(raised, "fit: a table that does not line up raises (not read as a failed fit)")

    # the rule on two worlds (the config's prefer may name one: the second pilot 0 runs v4 only)
    ccfg = {**cfg, "ceiling": {**cfg["ceiling"], "prefer": ["v2", "v3"]}}

    def res(v2_hgb, v2_lr, v3_hgb, v3_lr):
        mk = lambda h, l: {"L300": {"hgb": {"auc_A_speed": h}, "lr": {"auc_A_speed": l}}}
        return {"v2": mk(v2_hgb, v2_lr), "v3": mk(v3_hgb, v3_lr)}
    check(ce.choose(res(0.85, 0.95, 0.5, 0.5), ccfg)["chosen"] == "v2", "choice: 0.85 exactly is usable; the smaller counts")
    check(ce.choose(res(0.86, 0.95, 0.80, 0.99), ccfg)["chosen"] == "v3", "choice: v3 when v2 is not usable")
    check(ce.choose(res(0.80, 0.80, 0.70, 0.70), ccfg)["chosen"] == "v2", "choice: v2 is preferred")
    c = ce.choose(res(0.86, 0.9, 0.86, 0.9), ccfg)
    check(c["chosen"] is None and c["back_to_researcher"], "choice: none usable -> back to the researcher")
    c = ce.choose(res(None, 0.9, 0.8, 0.8), ccfg)
    check(c["chosen"] is None and c["unmeasured"] == ["v2"], "choice: an unmeasured v2 is not read as a ceiling")
    c = ce.choose(res(0.8, 0.8, float("nan"), 0.8), ccfg)
    check(c["chosen"] is None and c["unmeasured"] == ["v3"], "choice: a NaN in v3 also goes back to the researcher")


# ---------------------------------------------------------------------------
# The stage (design 3.7, after the freeze)
# ---------------------------------------------------------------------------

def fake_session(rng: np.random.Generator, dur: int = 3600, sid: str = "F") -> st.Session:
    """A bursty press trace with a random F series (every column of replay_all.COLS) and random labels."""
    tr = bursty_trace(rng, dur, sid)
    feat = {c: rng.uniform(0, 1, dur) for c in ("f3", "f5", "f6", "p_stuck")}
    feat["keys"] = rng.integers(0, 160, dur).astype(float)
    feat["f1"] = rng.uniform(40, 2000, dur)
    feat["f4"] = rng.uniform(0, 20, dur)
    feat["f1"][rng.random(dur) < 0.05] = np.nan  # a tick gse-replay did not emit
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
    check(same_series(base, all_series(mut)), "input closure: f3 f5 f6 p_stuck to NaN and other labels leave the 24 unchanged")
    inp = st.stage_input(sess)
    check(sorted(inp._cols) == sorted(st.ALLOWED_INPUT), "input closure: the stage input holds ALLOWED_INPUT only")
    for c in ("f3", "f6", "p_stuck", "seg"):
        try:
            inp[c]
            ok = False
        except KeyError:
            ok = True
        check(ok, f"input closure: reading {c} raises")
    # a mapping that reads a column outside ALLOWED_INPUT fails instead of running
    def bad(inp: st.StageInput) -> np.ndarray:
        return inp["f3"]
    try:
        bad(inp)
        ok = False
    except KeyError:
        ok = True
    check(ok, "input closure: a mutant mapping reading f3 raises")
    # the drive changes when an allowed column changes (the closure is not vacuous)
    mut2 = st.Session(sess.sid, sess.duration_s, sess.presses, sess.active, sess.seg,
                      {**sess.feat, "keys": sess.feat["keys"][::-1].copy(), "f1": sess.feat["f1"][::-1].copy()},
                      sess.key_seed)
    s2 = all_series(mut2)
    check(not np.array_equal(base["S-raw-hold-sec"][0], s2["S-raw-hold-sec"][0])
          and not np.array_equal(base["S-raw-hold-sec"][1], s2["S-raw-hold-sec"][1]),
          "input closure: keys and f1 do reach the sec candidates (negative control)")


def test_stage_causal() -> None:
    rng = np.random.default_rng(12)
    sess = fake_session(rng)
    T = 1800
    feat = {c: v.copy() for c, v in sess.feat.items()}
    for c in feat:  # the F series of ticks k >= T see presses at or after T (replay_all: tick k covers [k, k + 1))
        feat[c][T:] = rng.permutation(feat[c][T:])
    active = sess.active.copy()
    active[T:] = False
    cut = st.Session(sess.sid, sess.duration_s, sess.presses[sess.presses < T], active, sess.seg, feat, sess.key_seed)
    a, b = all_series(sess), all_series(cut)
    check(same_series(a, b, T * st.HZ), "causal (stage): later presses and F leave the 24 unchanged before T")
    check(not same_series(a, b), "causal (stage): they change the 24 after T (negative control)")
    # a press exactly at T counts from the point at T (sub) and not before
    p = np.array([10.0, 10.2, 10.4, 20.0])
    inp = st.StageInput(30, {"presses": p, "active": np.isin(np.arange(30), [10, 20]), "keys": np.zeros(30),
                             "f1": np.zeros(30), "f4": np.zeros(30)})
    ua, _, stp = st.drive_sub(inp)
    check(ua[199] < ua[200] and not stp[200] and stp[199], "causal (sub): a press at 20.0 s counts from t = 20.0 s")
    # inside a second (Codex): cut at T2 = 1800.35 s; the points before T2 do not change
    T2 = 1800.35
    keep = sess.presses < T2
    active2 = np.zeros(sess.duration_s, dtype=bool)
    active2[sess.presses[keep].astype(int)] = True
    feat2 = {c: v.copy() for c, v in sess.feat.items()}
    for c in feat2:  # ticks k >= 1800 cover presses at or after 1800 s
        feat2[c][1800:] = rng.permutation(feat2[c][1800:])
    extra = np.array([1800.36, 1800.5, 1800.9])  # presses inside the cut second, after T2
    cut2 = st.Session(sess.sid, sess.duration_s, sess.presses[keep], active2, sess.seg, feat2, sess.key_seed)
    more = st.Session(sess.sid, sess.duration_s, np.sort(np.concatenate([sess.presses[keep], extra])),
                      active2 | (np.arange(sess.duration_s) == 1800), sess.seg, feat2, sess.key_seed)
    j2 = int(np.ceil(T2 * st.HZ))  # the points t < T2
    c2, m2 = all_series(cut2), all_series(more)
    check(same_series(c2, m2, j2) and same_series(a, c2, j2),
          "causal (stage): presses later in the same second (after 1800.35 s) leave every point before it unchanged")
    check(not same_series(c2, m2), "causal (stage): those presses do change later points (negative control)")
    # the wobble of the first points does not depend on the session length (Codex)
    w_long, w_short = st.wobble(5000, 3, 99), st.wobble(1200, 3, 99)
    check(all(np.array_equal(w_long[i][:1200], w_short[i]) for i in (0, 1)),
          "causal (jitter): the wobble of a and r over the first points does not depend on the session length")
    # no press at all (Codex): no drive, stopped everywhere
    empty = st.StageInput(30, {"presses": np.zeros(0), "active": np.zeros(30, dtype=bool), "keys": np.zeros(30),
                               "f1": np.zeros(30), "f4": np.zeros(30)})
    ua, ur, stp = st.drive_sub(empty)
    check(not ua.any() and not ur.any() and stp.all(), "sub: a session without a press gives 0 and stopped")
    # decisions 19: F1 = 0 (no interval in the window) is tempo 0; 80 ms is 1; NaN holds
    inp = st.StageInput(6, {"presses": np.array([0.5, 1.5, 2.5]), "active": np.array([1, 1, 1, 0, 0, 0], dtype=bool),
                            "keys": np.zeros(6), "f1": np.array([80.0, 0.0, np.nan, 340.0, 0.0, 600.0]),
                            "f4": np.zeros(6)})
    _, ur, _ = st.drive_sec(inp)
    check(np.allclose(ur[10::10], [1.0, 0.0, 0.0, 0.5, 0.0]), f"sec: F1 80 / 0 / NaN (holds 0) / 340 / 0 -> {ur[10::10]}")


def test_stops() -> None:
    hz = st.HZ
    # presses every 0.2 s over [10, 20), then none until 80 s, then every 0.2 s until 90 s
    p = np.round(np.concatenate([np.arange(10, 20, 0.2), np.arange(80, 90, 0.2)]), 3)
    dur = 100
    act = np.zeros(dur, dtype=bool)
    act[p.astype(int)] = True
    inp = st.StageInput(dur, {"presses": p, "active": act, "keys": np.full(dur, 75.0), "f1": np.full(dur, 300.0),
                              "f4": np.zeros(dur)})
    last = p[p < 20][-1]
    j_stop = int(np.ceil((last + 2) * hz - 1e-9))  # the first stopped point (sub)
    out = {s: st.candidate_series(inp, f"S-raw-{s}-sub", 1, 7) for s in st.STOPS}
    v0 = out["hold"][0][j_stop - 1]
    check(np.all(out["hold"][0][j_stop: 80 * hz] == v0) and v0 > 0,
          "stop hold (sub): the amplitude stays at the last moving value")
    check(np.all(out["ground"][0][j_stop: 80 * hz] == 0) and out["ground"][0][j_stop - 1] > 0,
          "stop ground (sub): 0 from 2 s after the last press, not before")
    el = (np.arange(j_stop, 80 * hz) - (j_stop - 1)) * st.DT
    check(np.allclose(out["decay"][0][j_stop: 80 * hz], v0 * np.exp(-el / st.DECAY_TAU_S)),
          "stop decay (sub): v0 exp(-elapsed / 60 s)")
    check(abs(out["decay"][0][80 * hz - 1] - v0 * np.exp(-((80 * hz - 1 - (j_stop - 1)) * st.DT) / 60)) < 1e-12,
          "stop decay (sub): about 58 s after the stop it is v0 e^-58/60")
    # res=sec: second k is used from t = k + 1; stopped after two silent seconds
    sec = {s: st.candidate_series(inp, f"S-raw-{s}-sec", 1, 7) for s in st.STOPS}
    _, _, stp = st.drive_sec(inp)
    check(not stp[20 * hz] and not stp[22 * hz - 1] and stp[22 * hz] and stp[81 * hz - 1] and not stp[81 * hz],
          "stop (sec): moving until t = 22 (second 19 typed is among the last two), stopped on [22, 81), moving "
          "from 81 (second 80 typed)")
    check(np.all(sec["ground"][0][22 * hz: 81 * hz] == 0) and np.all(sec["hold"][0][22 * hz: 81 * hz] == 0.5)
          and sec["ground"][0][22 * hz - 1] == 0.5, "stop (sec): ground 0 and hold keeps keys 75 / 150 while stopped")
    # jitter: the wobble goes on while stopped; the raw value does not move
    jh = st.candidate_series(inp, "S-jitter-hold-sub", 1, 7)[0][j_stop: 80 * hz]
    check(np.std(jh) > 0.02 and np.all(out["hold"][0][j_stop: 80 * hz] == v0), "jitter: the wobble moves while stopped")
    n = 200000
    w = st.ar1(n, np.random.default_rng(3))
    ac = np.corrcoef(w[1:], w[:-1])[0, 1]
    check(abs(np.std(w) - st.JIT_SD) < 0.01 and abs(ac - st.JIT_PHI) < 0.01, f"jitter: AR(1) sd {np.std(w):.3f} ac {ac:.3f}")
    a1 = st.wobble(1000, 1, 5)
    a2 = st.wobble(1000, 1, 5)
    check(np.array_equal(a1[0], a2[0]) and not np.array_equal(a1[0], a1[1]), "jitter: same seed same wobble; a and r differ")
    # rank against a brute force on a short series
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
    check(np.all(st.running_rank(np.full(2000, 0.3), np.ones(2000, dtype=bool)) == 0.5), "rank: a constant is 0.5")
    # smooth: the EMA has time constant 30 s
    y = st.ema(np.ones(3000), st.SMOOTH_TAU_S)
    check(abs(y[299] - (1 - np.exp(-30 / 30))) < 1e-9, "smooth: 1 - e^-1 after 30 s of a unit step")


def test_window_features() -> None:
    W = st.WIN_POINTS
    a = np.concatenate([np.full(W, 0.4), np.full(300, 0.2), np.full(300, 0.6)])
    r = np.concatenate([np.zeros(W), np.linspace(0, 1, W)])
    F = st.window_features(a, r, 2)
    check(F.shape == (2, 20), "window features: 20 per window")
    check(F[0, 1] == 0 and F[0, 7] == 0 and F[0, 9] == 60.0 and F[0, 8] == 0.4, "window features: a constant window")
    check(abs(F[1, 9] - 30.0) < 1e-9 and F[1, 8] == 0.6 and abs(F[1, 0] - 0.4) < 1e-12,
          "window features: a step at the middle -> 30 s since the change")
    check(F[0, 15] == 1.0 and F[1, 19] == 0.1 and abs(F[1, 6 + 10] - 1 / (W - 1)) < 1e-12,
          "window features: ground share, a change at the last point, mean |diff|")


def test_lags(cfg: dict) -> None:
    hz = st.HZ
    ok = True
    for L in (1.0, 3.0, 5.0):
        x = np.full(60 * hz, 0.2)
        x[int((20 + L) * hz):] = 0.8
        kind, lag = ck.event_lag(x, 20.0, cfg)
        ok &= kind == "lag" and abs(lag - L) <= 0.1 + 1e-9
        kind, lag = ck.event_lag(1 - x, 20.0, cfg)  # downward
        ok &= kind == "lag" and abs(lag - L) <= 0.1 + 1e-9
    check(ok, "lags: steps at 1, 3 and 5 s (up and down) are returned within 0.1 s")
    x = np.full(60 * hz, 0.2)
    x[int(20.5 * hz): int(21.0 * hz)] = 0.8  # a blip shorter than 1 s, then the real change at 4 s
    x[24 * hz:] = 0.8
    kind, lag = ck.event_lag(x, 20.0, cfg)
    check(kind == "lag" and abs(lag - 4.0) <= 0.1 + 1e-9, f"lags: a blip that does not hold 1 s is not the change ({lag})")
    # negative (design section 8, decisions 18): hold without the wobble -> unchanged for every event. With the
    # jitter wobble only, the lag measure answers in most events (the share is printed, not a gate): the lags of the
    # six jitter candidates are not read (checks.describe marks them)
    kinds = [ck.event_lag(np.full(40 * hz, v), 15.0, cfg)[0] for v in np.linspace(0, 1, 11)]
    check(all(k == "unchanged" for k in kinds), "lags: hold without the wobble -> unchanged in every event")
    # the 0.05 boundary from both sides (code-reviewer M4): small noise and a 0.04 ramp are unchanged, a 0.06 step
    # is a lag
    rng = np.random.default_rng(10)
    noisy = [ck.event_lag(0.5 + rng.normal(0, 0.005, 40 * hz), 15.0, cfg)[0] for _ in range(50)]
    ramp = np.concatenate([np.full(15 * hz, 0.5), 0.5 + 0.04 * np.arange(10 * hz) / (10 * hz), np.full(15 * hz, 0.54)])
    step = np.concatenate([np.full(17 * hz, 0.5), np.full(23 * hz, 0.56)])
    check(all(k == "unchanged" for k in noisy) and ck.event_lag(ramp, 15.0, cfg)[0] == "unchanged"
          and ck.event_lag(step, 15.0, cfg) == ("lag", 2.0),
          "lags: noise of sd 0.005 and a 0.04 ramp are unchanged; a 0.06 step at 2 s is a lag of 2 s")
    rng = np.random.default_rng(9)
    kinds = [ck.event_lag(np.clip(0.5 + st.ar1(40 * hz, rng), 0, 1), 15.0, cfg)[0] for _ in range(300)]
    share = np.mean([k in ("unchanged", "ge10") for k in kinds])
    print(f"     (descriptive) hold + wobble only -> unchanged or >= 10 s in {share:.2f} of events (decisions 18)")
    check(all(not c.startswith("S-jitter-") or not ck.lags_readable(c) for c in st.candidates())
          and sum(ck.lags_readable(c) for c in st.candidates()) == 18, "lags: the jitter candidates are marked unread")
    ev = ck.stop_events(np.array([0.5, 5.0, 16.0, 17.0, 40.0, 95.0]), 100, cfg)
    check(ev == [(5.0, 16.0), (17.0, 40.0)], f"lags: stop events {ev}")
    # exactly 10 000 ms is an event wherever it sits (code-reviewer L1: 1234.567 + 10 - 1234.567 < 10 in floats)
    ok = all(len(ck.stop_events(np.array([t, round(t + 10.0, 3), 1700.0]), 1800, cfg)) == 2
             for t in np.round(np.arange(1.0, 1500.0, 0.007)[:3000], 3))
    check(ok, "lags: a gap of exactly 10 s is an event at any session time")


def test_pc() -> None:
    rng = np.random.default_rng(13)
    sess = fake_session(rng)
    blk = {lam: st.pc_blocks(sess.seg, sess.duration_s, sess.key_seed, 1, lam) for lam in (0.0, 0.3, 0.7, 1.0)}
    check(all(np.array_equal(blk[0.0]["U"], b["U"]) and np.array_equal(blk[0.0]["N"], b["N"]) for b in blk.values()),
          "PC: U and N are the same draws for every lambda")
    check(np.array_equal(blk[0.0]["value"], blk[0.0]["N"]) and np.array_equal(blk[1.0]["value"], blk[1.0]["q"]),
          "PC: lambda 0 -> N everywhere, lambda 1 -> q everywhere")
    m = blk[0.7]["U"] >= 0.7
    check(np.array_equal(blk[0.3]["value"][m], blk[0.7]["value"][m]) and m.any(), "PC: blocks with U >= 0.7 agree at 0.3 and 0.7")
    perm = st.Session(sess.sid, sess.duration_s, sess.presses, sess.active, rng.permutation(sess.seg), sess.feat, sess.key_seed)
    ok = all(np.array_equal(st.series(sess, f"PC0-{c}", 1)[0], st.series(perm, f"PC0-{c}", 1)[0]) for c in st.candidates())
    check(ok, "PC: PC0 of every candidate does not depend on the labels")
    check(not np.array_equal(st.series(sess, "PCs-S-raw-hold-sec", 1, lam=1.0)[0],
                             st.series(perm, "PCs-S-raw-hold-sec", 1, lam=1.0)[0]), "PC: PC-stall at 1 does (negative control)")
    for res in st.RESOLUTIONS:
        r = st.series(sess, f"PCs-S-raw-hold-{res}", 1, lam=0.5)[1]
        _, _, stp = st.drive(st.stage_input(sess), res)
        check(np.all(r[~stp] == 0.5), f"PC: u_r = 0.5 at the moving points ({res})")
    q = blk[1.0]["q"]
    check(q[0] == 0.0 and abs(q[6] - st.stall_share(sess.seg, 60, 360)) < 1e-12, "PC: q is the stall share of the 300 s before")
    a = st.series(sess, "PC1", 1)[0]
    check(abs(a[100 * st.HZ + 5] - st.stall_share(sess.seg, 40, 100)) < 1e-12, "PC1: the stall share of the 60 s before")


def test_twins(tmp: Path) -> None:
    rng = np.random.default_rng(14)
    t = np.sort(rng.choice(200000, 3000, replace=False)).astype(np.int64)
    tt = tw.redraw(t, rng)
    check(np.array_equal(np.bincount(t // 1000, minlength=200), np.bincount(tt // 1000, minlength=200)),
          "twins: every second keeps its press count")
    check(np.all(np.diff(tt) > 0) and not np.array_equal(t, tt), "twins: the order is kept (no repeats) and times move")
    cfg = {"_hmm_version": "x", "keys": {}}
    d = tmp / "twin-unit"
    (d / "ndjson").mkdir(parents=True, exist_ok=True)
    (d / "labels").mkdir(parents=True, exist_ok=True)
    times = np.array([100, 180, 1500, 1550], dtype=np.int64)  # the second press of vk 65 comes before its release
    vks = np.array([65, 65, 66, 8], dtype=np.int16)
    dw = np.array([100, 70, 80, 90], dtype=np.int64)
    gs.write_session(d, "U", 5000, times, vks, dw, 3, np.zeros(3, dtype=np.int8), cfg)
    start, t2, v2, d2 = tw.read_keys(d / "ndjson" / "U.ndjson")
    check(start == 5000 and np.array_equal(t2, times) and np.array_equal(v2, vks) and np.array_equal(d2, dw),
          "twins: read_keys pairs releases with presses (overlapping presses of one key)")


def test_judge(cfg: dict) -> None:
    cands = ["S-raw-hold-sec", "S-raw-ground-sub"]
    c0, c1 = cands

    def att(g, lo, hi, kinds=("hgb", "lr")):
        return {a: {"gain": g, "ci95": [lo, hi]} for a in ck.ATTACKERS}

    def base():
        d = {"PC1": att(0.2, 0.15, 0.25)}
        for c in cands:
            d[c] = att(0.0, -0.01, 0.02)
            d[f"PCs-{c}"] = att(0.05, 0.035, 0.07)
            d[f"PC0-{c}"] = att(0.0, -0.01, 0.02)
        return d
    nulls = {n: [{a: 0.0 for a in ck.ATTACKERS}] * 20 for n in base()}
    auc = {"hgb": 0.7, "lr": 0.7}
    j = ck.judge(base(), nulls, auc, cands, cfg, False)
    check(j["verdicts"][c0] == "green" and j["verdicts"]["PC1"] == "works" and j["verdicts"][f"PCs-{c0}"] == "works",
          "judge: everything works -> green below 0.03")
    def v(patch, nl=nulls, au=auc, ff=False):
        d = base()
        d.update(patch)
        return ck.judge(d, nl, au, cands, cfg, ff)
    check(v({c0: att(0.02, -0.01, 0.03)})["verdicts"][c0] == "red_unconfirmed", "judge: 0.03 exactly -> red (unconfirmed)")
    check(v({c0: att(0.05, 0.031, 0.07)})["verdicts"][c0] == "red_detected", "judge: lower > 0.03 -> red detected")
    check(v({c0: att(0.05, 0.03, 0.07)})["verdicts"][c0] == "red_unconfirmed", "judge: lower 0.03 exactly -> unconfirmed")
    check(v({"PC1": att(0.15, 0.10, 0.2)})["detector"][c0]["reasons"] == ["weak_detector"],
          "judge: PC1 lower 0.10 exactly does not work")
    check(v({f"PCs-{c0}": att(0.08, 0.04, 0.1)})["verdicts"][c0] == "green", "judge: PC-stall point 0.08 exactly works")
    jj = v({f"PCs-{c0}": att(0.081, 0.04, 0.1)})
    check(jj["verdicts"][c0] == "undecidable" and jj["detector"][c0]["reasons"] == ["weak_stall_pc"]
          and jj["verdicts"][c1] == "green", "judge: a PC-stall above 0.08 -> its candidate undecidable, the other judged")
    check(v({f"PCs-{c0}": att(0.05, 0.03, 0.07)})["detector"][c0]["reasons"] == ["weak_stall_pc"],
          "judge: PC-stall lower 0.03 exactly does not work")
    jj = v({f"PC0-{c0}": att(0.01, 0.0, 0.03)})
    check(jj["detector"][c0]["reasons"] == ["stall_baseline"] and jj["verdicts"][c0] == "undecidable",
          "judge: a PC0 upper of 0.03 exactly -> stall_baseline")
    jj = v({f"PC0-{c0}": att(0.05, 0.031, 0.07)})
    check(jj["verdicts"][c0] == "red_detected_stop_path", "judge: PC0 lower > 0.03 -> red detected (stop path)")
    nl = {**nulls, f"PC0-{c1}": [{a: 0.03 for a in ck.ATTACKERS}] * 20}
    jj = v({}, nl=nl)
    check(jj["detector"][c1]["reasons"] == ["null"] and jj["verdicts"][c0] == "green" and jj["null_all_73_ok"] is False,
          "judge: the null of a candidate's own PC0 at 0.03 -> that candidate only; the overall null is described")
    jj = v({f"PC0-{c0}": att(0.05, 0.031, 0.07)}, nl={**nulls, c0: [{a: 0.04 for a in ck.ATTACKERS}] * 20})
    check(jj["verdicts"][c0] == "undecidable", "judge: the stop path needs the candidate's null")
    jj = v({}, au={"hgb": 0.90, "lr": 0.7})
    check(jj["ceiling_kinds"] == ["hgb"] and jj["attackers_used"] == ["full/lr", "small/lr"] and jj["verdicts"][c0] == "green",
          "judge: 0.90 exactly is the ceiling; that classifier is left out")
    jj = v({c0: {**att(0.0, -0.01, 0.02), "full/hgb": {"gain": 0.2, "ci95": [0.1, 0.3]}}}, au={"hgb": 0.95, "lr": 0.7})
    check(jj["verdicts"][c0] == "green", "judge: a large gain on the ceiling classifier does not count")
    nl = {**nulls, "PC1": [{**{a: 0.0 for a in ck.ATTACKERS}, "full/hgb": 0.2}] * 20}
    check(v({}, nl=nl, au={"hgb": 0.95, "lr": 0.7})["verdicts"][c0] == "green", "judge: the null of a ceiling classifier is left out")
    jj = v({}, au={"hgb": 0.95, "lr": 0.91})
    check(jj["verdicts"][c0] == "undecidable" and jj["detector"][c0]["reasons"] == ["ceiling"],
          "judge: both classifiers at the ceiling -> undecidable (ceiling)")
    jj = v({c0: {**att(0.0, -0.01, 0.02), "small/lr": {"gain": 0.0, "ci95": [float("nan"), 0.02]}}})
    check(jj["verdicts"][c0] == "undecidable" and jj["verdicts"][c1] == "undecidable",
          "judge: a NaN bound makes the label undecidable (the candidate with it and the other)")
    jj = v({"PC-corr": {**att(0.0, -0.01, 0.02), "small/lr": {"gain": 0.0, "ci95": [float("nan"), 0.02]}}})
    check(jj["verdicts"][c0] == "green" and jj["verdicts"]["PC-corr"] == "descriptive",
          "judge: a NaN bound of PC-corr (descriptive) does not stop the label")
    # one attacker alone (code-reviewer M3): the maxima take each attacker in use
    for a_ in ck.ATTACKERS:
        one = {**att(0.0, -0.01, 0.02), a_: {"gain": 0.05, "ci95": [0.031, 0.07]}}
        up = {**att(0.0, -0.01, 0.02), a_: {"gain": 0.01, "ci95": [-0.01, 0.031]}}
        check(v({c0: one})["verdicts"][c0] == "red_detected" and v({c0: up})["verdicts"][c0] == "red_unconfirmed",
              f"judge: {a_} alone above the bounds -> red detected / unconfirmed")
    # the null is the 95th percentile of the per-permutation maxima: 1 of 20 at 0.05 passes, 2 of 20 do not
    for k, want in ((1, []), (2, ["null"])):
        nl = {**nulls, c0: [{**{a: 0.0 for a in ck.ATTACKERS}, "small/lr": 0.05}] * k
              + [{a: 0.0 for a in ck.ATTACKERS}] * (20 - k)}
        check(v({}, nl=nl)["detector"][c0]["reasons"] == want, f"judge: {k} of 20 permutations at 0.05 on one attacker")
    jj = ck.judge(base(), {n: nulls[n] for n in list(nulls)[:-1]}, auc, cands, cfg, False)
    check(jj["null_all_73_ok"] is False, "judge: a judged name without a null is not read as a passing overall null")
    jj = ck.judge({}, {}, None, cands, cfg, True)
    check(all(jj["verdicts"].get(c, "undecidable") == "undecidable" for c in cands)
          and jj["detector"][c0]["reasons"][0] == "fit_failed", "judge: a failed fit -> undecidable")
    check(v({}, nl=None)["detector"][c0]["reasons"] == ["null"], "judge: no null run -> not judged")


def test_lam_config(cfg: dict) -> None:
    """Codex round 2: the main run takes only lambdas of the pilot's grid, one per candidate."""
    good = {c: 0.15 for c in st.candidates()}
    mk = lambda lam: {**cfg, "pc_stall": {**cfg["pc_stall"], "lam": lam}}
    check(ck.lam_problems(mk(good)) == [], "lambda config: one grid value per candidate passes")
    for name, lam in (("missing", {k: v for k, v in list(good.items())[1:]}),
                      ("a string", {**good, "S-raw-hold-sec": "0.15"}),
                      ("NaN", {**good, "S-raw-hold-sec": float("nan")}),
                      ("off the grid", {**good, "S-raw-hold-sec": 0.12}),
                      ("above 1", {**good, "S-raw-hold-sec": 1.05}),
                      ("an unknown name", {**good, "S-raw-hold-min": 0.15})):
        check(len(ck.lam_problems(mk(lam))) == 1, f"lambda config: {name} is refused")


def test_select_lambda(cfg: dict) -> None:
    """Round 2 design 3.7 (the addition) and 3.9: the band (l > 0.03, g <= 0.08), the aim 0.055 on the isotonic fit,
    the ties, NaN and the fallback; then the pilot's names -> choice -> config.json -> lam_problems (Codex)."""
    ps = cfg["pc_stall"]
    grid = [float(x) for x in ps["pilot_grid"]]
    check(grid == [round(0.025 * i, 3) for i in range(1, 13)] and ps["aim"] == 0.055 and ps["lower"] == 0.03
          and ps["upper"] == 0.08, "select_lambda: the round 2 grid (0.025 to 0.300) and the aim 0.055")
    nan = float("nan")
    sel = lambda g, lo: ck.select_lambda(grid, g, lo, ps["aim"], ps["lower"], ps["upper"])
    a = [round(0.01 * (i + 1) + 0.003, 6) for i in range(12)]  # 0.013, 0.023, ..., 0.053 at 0.125, 0.063 at 0.150
    lo_a = [round(x - 0.008, 6) for x in a]
    check(sel(a, lo_a)["lam"] == 0.125, "select_lambda: in the band, the fitted value closest to 0.055")
    lo_b = list(lo_a)
    lo_b[4] = 0.03
    check(sel(a, lo_b)["lam"] == 0.15, "select_lambda: the closest with a lower bound of exactly 0.03 is out of the band")
    lo_n = list(lo_a)
    lo_n[4] = nan
    check(sel(a, lo_n)["lam"] == 0.15, "select_lambda: a NaN lower bound is out of the band")
    g_n = list(a)
    g_n[4] = nan
    r = sel(g_n, lo_a)
    check(r["lam"] == 0.15 and r["excluded"] == [0.125], "select_lambda: a NaN point estimate is left out")
    small = [0.01 + 0.001 * i for i in range(11)]
    r = sel(small + [0.08], [x - 0.008 for x in small] + [0.07])
    check(r["band"] == [0.3] and r["lam"] == 0.3, "select_lambda: a point estimate of exactly 0.08 is in the band")
    r = sel(small + [0.0801], [x - 0.008 for x in small] + [0.07])
    check(r["band"] == [] and "no lambda in the band" in r["rule"] and r["lam"] == 0.3,
          "select_lambda: above 0.08 is out of the band; none in the band -> the closest over the grid")
    r = sel(small + [0.021], [x - 0.008 for x in small] + [0.013])
    check(r["band"] == [] and r["lam"] == 0.3, "select_lambda: all below the band -> the closest (the largest) over the grid")
    flat = [0.01, 0.02, 0.03, 0.04, 0.055, 0.055, 0.055, 0.07, 0.08, 0.09, 0.10, 0.11]
    check(sel(flat, [x - 0.008 for x in flat])["lam"] == 0.15, "select_lambda: three tied -> the middle")
    bumpy = [0.01, 0.02, 0.03, 0.04, 0.06, 0.05, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12]
    r = sel(bumpy, [x - 0.008 for x in bumpy])
    check(r["fit"][4][1] == r["fit"][5][1] and r["lam"] == 0.125, "select_lambda: a pooled pair -> the smaller middle")
    check(sel([nan] * 12, [nan] * 12)["lam"] is None, "select_lambda: no finite point estimate -> no choice")
    lo_gap = [x - 0.008 for x in flat]
    lo_gap[5] = 0.02  # 0.150 of the tied run 0.125-0.175 drops out of the band: the ties 0.125 and 0.175 are apart
    r = sel(flat, lo_gap)
    check(r["ties"] == [0.125, 0.175] and r["lam"] == 0.125, "select_lambda: ties apart on the grid -> the smaller middle")
    two = [0.01, 0.02, 0.03, 0.04, 0.045, 0.05, 0.06, 0.065, 0.07, 0.08, 0.09, 0.10]
    r = sel(two, [x - 0.008 for x in two])
    check(r["ties"] == [0.15, 0.175] and r["lam"] == 0.15, "select_lambda: one below and one above at the same distance -> the smaller")
    top = [0.01, 0.012, 0.014, 0.016, 0.018, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02]
    r = sel(top, [x - 0.008 for x in top])
    check(r["band"] == [] and r["lam"] == 0.225, "select_lambda: none in the band, a flat top -> the middle of the flat top")
    wig = [0.01, 0.02, 0.03, 0.04, 0.08, 0.03, 0.07, 0.09, 0.10, 0.11, 0.12, 0.13]
    r = sel(wig, [x - 0.008 for x in wig])
    check(r["lam"] == 0.125 and r["fit"][4][1] == r["fit"][5][1],
          "select_lambda: a raw g of exactly 0.08 in the band may win by its pooled fitted value (design 3.9)")
    over = [0.01, 0.02, 0.03, 0.04, 0.085, 0.035, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14]
    r = sel(over, [x - 0.008 for x in over])
    check(r["fit"][4][1] <= 0.08 and 0.125 not in r["band"] and r["lam"] == 0.1,
          "select_lambda: the band uses the raw g (0.085 is out even when its pooled value is 0.06)")
    near = [0.01, 0.02, 0.03, 0.04, 0.051, 0.059, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12]
    r = sel(near, [x - 0.008 for x in near])
    check(r["ties"] == [0.125, 0.15] and r["lam"] == 0.125,
          "select_lambda: distances equal at 6 decimals tie (unrounded, 0.059 would win by float error)")
    nf = {"PC1": {"lower_max": 0.2}, ck.pilot_key("S-raw-hold-sec", 0.025): None}
    check(ck.choose_all(nf, cfg)["S-raw-hold-sec"]["lam"] is None, "pilot: a candidate with no finite value -> no choice")
    # the path the pilot takes: names -> merged maxima -> choice -> config.json -> the main run's check
    cands = st.candidates()
    keys = [ck.pilot_key(c, x) for c in cands for x in [0.0] + grid]
    check(len(set(keys)) == len(keys) == 13 * len(cands) and ck.pilot_key(cands[0], 0.025).endswith("@0.025")
          and ck.pilot_key(cands[0], 0.075).endswith("@0.075"), "pilot: 13 distinct names per candidate (three decimals)")
    rec = lambda g, lo: {"gain_max": g, "lower_max": lo, "upper_max": g + 0.008, "n_nan_bounds": 0}
    shift = {c: i % 5 for i, c in enumerate(cands)}  # candidate i aims at the grid index 4 + its shift
    merged = {"PC1": rec(0.3, 0.25)}
    for c in cands:
        merged[ck.pilot_key(c, 0.0)] = rec(0.004, -0.004)
        for i, x in enumerate(grid):
            g = round(0.055 + 0.01 * (i - 4 - shift[c]) + 0.001, 6)
            merged[ck.pilot_key(c, x)] = rec(g, g - 0.008)
    sels = ck.choose_all(merged, cfg)
    want = {c: grid[4 + shift[c]] for c in cands}
    check({c: sels[c]["lam"] for c in cands} == want, "pilot: each candidate gets its own lambda")
    zero = dict(merged)
    for c in cands:  # lambda 0 would win if it were a choice: exactly the aim, the grid at 0.07 and above
        zero[ck.pilot_key(c, 0.0)] = rec(0.055, 0.05)
        for i, x in enumerate(grid):
            zero[ck.pilot_key(c, x)] = rec(0.07 + 0.01 * i, 0.062 + 0.01 * i)
    zs = ck.choose_all(zero, cfg)
    check(all(zs[c]["lam"] == grid[0] and zs[c]["fit"][0][0] == grid[0] for c in cands),
          "pilot: lambda = 0 is never a choice (it would win at exactly the aim)")
    st_, ss = ck.pilot_decide(merged, {"PC1": {"fit_failed": False}}, cfg, [])
    check(st_ is None and {c: ss[c]["lam"] for c in cands} == want, "pilot: decide -> no stop and the choices")
    nfm = dict(merged)
    for x in grid:
        nfm[ck.pilot_key(cands[0], x)] = None
    st_, ss = ck.pilot_decide(nfm, {"PC1": {"fit_failed": False}}, cfg, [])
    check(st_ == "no_finite_pcs" and ss[cands[0]]["lam"] is None, "pilot: decide -> a candidate with no finite value stops")
    st_, ss = ck.pilot_decide({**merged, "PC1": rec(0.1, 0.1)}, {"PC1": {"fit_failed": False}}, cfg, [])
    check(st_ == "weak_detector" and ss == {}, "pilot: decide -> a weak PC1 stops with no selection")
    sp = cfg["sets"]["pilot"]
    good = {"stop": None, "rule": {k: cfg["pc_stall"][k] for k in ck.RULE_KEYS}, "seed": 20261013 + sp["seed_offset"],
            "n_sessions": sp["P"], "bootstrap": sp["bootstrap"], "selection": sels,
            "configs": {k: {kk: v[kk] for kk in ck.REC_KEYS} for k, v in merged.items()}}
    with tempfile.TemporaryDirectory() as d:
        cp, pp = Path(d) / "config.json", Path(d) / "pilot.json"
        (Path(d) / "SEED").write_text("20261013\n", encoding="utf-8")
        cp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        pp.write_text(json.dumps(good), encoding="utf-8")
        ck.apply_pilot(cp, pp)
        back = json.loads(cp.read_text(encoding="utf-8"))
        rest = lambda c: {**c, "pc_stall": {k: v for k, v in c["pc_stall"].items() if k != "lam"}}
        check(back["pc_stall"]["lam"] == want and ck.lam_problems(back) == [] and rest(back) == rest(cfg),
              "pilot: --apply-pilot writes pc_stall.lam only, the main run accepts it")
        cp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tampered = {**sels, cands[0]: {**sels[cands[0]], "lam": grid[0]}}
        for name, bad in (("a stopped pilot (no selection)", {**good, "stop": "weak_detector", "selection": {}}),
                          ("a stopped pilot with a full selection", {**good, "stop": "no_finite_pcs"}),
                          ("a round 1 pilot.json (no stop, no rule)", {k: v for k, v in good.items() if k not in ("stop", "rule")}),
                          ("another seed", {**good, "seed": 20261010}),
                          ("another P", {**good, "n_sessions": 40}),
                          ("another rule", {**good, "rule": {**good["rule"], "aim": 0.05}}),
                          ("a selection that does not follow from the maxima", {**good, "selection": tampered})):
            pp.write_text(json.dumps(bad), encoding="utf-8")
            try:
                ck.apply_pilot(cp, pp)
                refused = False
            except SystemExit:
                refused = True
            check(refused and json.loads(cp.read_text(encoding="utf-8"))["pc_stall"]["lam"] == cfg["pc_stall"]["lam"],
                  f"pilot: --apply-pilot refuses {name} and leaves config.json as it was")
    ok = {"PC1": {"fit_failed": False}}
    pc1 = lambda lo: {"PC1": {"lower_max": lo}}
    check(ck.pilot_stop(pc1(0.11), ok, cfg, []) is None, "pilot stop: PC1 lower bound 0.11 -> go on")
    check(ck.pilot_stop(pc1(0.10), ok, cfg, []) == "weak_detector", "pilot stop: PC1 lower bound exactly 0.10 -> stop")
    check(ck.pilot_stop(pc1(nan), ok, cfg, []) == "weak_detector", "pilot stop: a NaN PC1 lower bound -> stop")
    check(ck.pilot_stop({"PC1": None}, ok, cfg, []) == "weak_detector", "pilot stop: no PC1 -> stop")
    check(ck.pilot_stop(pc1(0.2), {**ok, "S-raw-hold-sec": {"fit_failed": True}}, cfg, []) == "fit_failed",
          "pilot stop: a failed fit -> stop")
    check(ck.pilot_stop(pc1(0.2), ok, cfg, ["hgb", "lr"]) == "ceiling", "pilot stop: both classifiers at the ceiling -> stop")


def test_stats(cfg: dict) -> None:
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 2000)
    sc_ = rng.random(2000)
    w = rng.integers(1, 4, 2000).astype(float)
    from sklearn.metrics import roc_auc_score
    check(abs(ck.weighted_auc(sc_, y, w) - roc_auc_score(y, sc_, sample_weight=w)) < 1e-9, "stats: weighted AUC equals sklearn")
    strata = rng.integers(0, 4, 2000)
    yp = ck.stratified_permutation(y, strata, rng)
    check(all(y[strata == s].sum() == yp[strata == s].sum() for s in range(4)) and not np.array_equal(y, yp),
          "stats: the permutation keeps the positives of each stratum")
    test_select_lambda(cfg)
    F = rng.normal(size=(10, 3))
    g = np.array([0] * 4 + [1] * 6)
    D = ck.diffs(F, g, 2)
    check(np.array_equal(D[4], np.zeros(6)) and np.array_equal(D[5, :3], F[5] - F[4]) and np.array_equal(D[5, 3:], np.zeros(3))
          and np.allclose(D[7, 3:], F[7] - F[5]), "B-full: differences to the two earlier windows, none across sessions")


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
    """design 3.7: three sessions cut at T; the F series of ticks before T as without the cut."""
    T = 3600
    ok, n = True, 0
    for sid in bl.p_sids(work)[:3]:
        lab = np.load(work / "labels" / f"{sid}.npz")
        start, dur = int(lab["start_ms"]), int(lab["duration_s"])
        lines = (work / "ndjson" / f"{sid}.ndjson").read_text(encoding="utf-8").splitlines()
        keep = [l for l in lines if json.loads(l).get("type") != "key" or json.loads(l)["t"] < start + T * 1000]
        cut = tmp / f"cut-{sid}.ndjson"
        cut.write_text("\n".join(keep) + "\n", encoding="utf-8", newline="\n")
        full = replay_cols(binary, work / "ndjson" / f"{sid}.ndjson", start, dur)
        part = replay_cols(binary, cut, start, dur)
        # the replay emits no tick after the last event of the stream, so the cut session stops at its last key
        # row: every tick it emits equals the full session's, and it emits every tick up to that row
        last_t = max(json.loads(l)["t"] for l in keep if json.loads(l).get("type") == "key")
        k_last = (last_t - start) // 1000
        emitted = np.isfinite(part["keys"][:T])
        ok &= all(np.array_equal(full[c][:T][emitted], part[c][:T][emitted]) for c in ra.COLS)
        ok &= bool(emitted[:k_last].all()) and k_last > T - 600
        n += 1
    check(ok and n == 3, "causal (gse-replay): with the NDJSON cut at T, every tick before T equals the full session's "
          "and none is missing before the last kept key (3 sessions)")


def test_twins_work(work: Path) -> None:
    tw_dir = work / "twins"
    sids = bl.p_sids(work)
    ok = len(sids) > 0 and (tw_dir / "feat").is_dir() and sorted(bl.p_sids(tw_dir)) == sorted(sids)
    for sid in sids if ok else []:
        o = np.load(work / "labels" / f"{sid}.npz")["presses_ms"]
        t = np.load(tw_dir / "labels" / f"{sid}.npz")["presses_ms"]
        ok &= np.array_equal(np.bincount(o // 1000), np.bincount(t // 1000)) and np.all(np.diff(t) > 0)
        ok &= np.isfinite(np.load(tw_dir / "feat" / f"{sid}.npz")["f1"]).mean() > 0.9
    check(ok, f"twins (run data): every one of the {len(sids)} P sessions has a replayed twin with its per-second "
          "counts and order")


def test_work(work: Path, cfg: dict, seed: int, jobs: int) -> None:
    """design 3.7 (PC at lambda 1, the seg mutation) through the main run's own path: run_stage -> label_tables ->
    the scratch memory maps -> build_x -> _fit_job -> e13_target (code-reviewer M2)."""
    import shutil
    import tempfile

    ms = st.manifest_p(work)
    n = len(ms)
    # the keys are names judge() knows (a PC-stall on the grid is descriptive; the mutation is read as a candidate)
    PCS, MUT, PC0, RAW = "PCs-S-raw-hold-sec@1.00", "S-raw-hold-sec-MUTseg", "PC0-S-raw-hold-sec", "S-raw-hold-sec"
    specs = [(PCS, "PCs-S-raw-hold-sec", 1.0), (MUT, "S-raw-hold-sec", None, "seg"), (PC0, "PC0-S-raw-hold-sec", 0.0),
             (RAW, "S-raw-hold-sec", None)]
    scratch = Path(tempfile.mkdtemp(prefix="selftest-", dir=work))
    try:
        tab = ck.label_tables(work, [m["sid"] for m in ms], cfg, scratch)
        F = ck.run_stage(specs, ms, work, seed, jobs)
        s0 = st.load_session(work, ms[1])
        n0 = st.load_session(work, ms[0]).duration_s // 60
        direct = st.window_features(*st.series(s0, "S-raw-hold-sec", seed), s0.duration_s // 60)
        check(np.array_equal(F[RAW][n0: n0 + len(direct)], direct),
              "wiring: run_stage keeps the session order (the second session's rows are its own windows)")
        if n < 40:  # Codex round 2: the wiring above runs on any run; the gains need the sessions of the pilot
            print(f"SKIP  PC at lambda 1 and the seg mutation (only {n} P sessions; they run with 40 or more)")
            return
        names = {}
        for i, (key, *_) in enumerate(specs):
            ck.save(scratch, f"F-{i}", F[key])
            names[key] = f"F-{i}"
        r = ck.e13_target("L300", tab["L300"], names, [], cfg, seed, jobs, 50, 0, scratch, [])
        g = {k: r["configs"][k]["gain_max"] for k in names}
        check(g[PCS] > 0.10, f"PC: PCs-S-raw-hold-sec at lambda 1 -> L300 point max {g[PCS]:+.3f} > 0.10 (main path)")
        check(g[MUT] > 0.10, f"mutation: seg mixed into the mapping -> L300 point max {g[MUT]:+.3f} > 0.10 (main path)")
        check(g[PC0] < 0.03, f"PC0-S-raw-hold-sec L300 point max {g[PC0]:+.3f} < 0.03 (negative control)")
        print(f"     (S-raw-hold-sec unmutated L300 point max {g[RAW]:+.3f}; not judged here)")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("eh1_dir")
    ap.add_argument("tmp")
    ap.add_argument("--hmm-version", required=True)
    ap.add_argument("--gse-replay", default=None, help="design 3.7: the gse-replay causality test (skipped without it)")
    ap.add_argument("--work", default=None, help="the run's replayed sessions: twins, PC at 1 and the mutation")
    ap.add_argument("--seed-file", default=None)
    ap.add_argument("--require-twins", action="store_true", help="the smoke and the main run: the twins must exist")
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    config = Path(a.config).resolve()
    cfg = json.loads(config.read_text(encoding="utf-8"))
    tmp = Path(a.tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    test_speed(cfg)
    test_tables(cfg, tmp)
    test_auc_and_choice(cfg)
    test_world(cfg, config, Path(a.eh1_dir).resolve(), tmp, a.hmm_version)
    test_input_closure()
    test_stage_causal()
    test_stops()
    test_window_features()
    test_lags(cfg)
    test_pc()
    test_twins(tmp)
    test_judge(cfg)
    test_stats(cfg)
    test_lam_config(cfg)
    if a.gse_replay:
        test_replay_causal(a.gse_replay, tmp / "ours-v4", tmp)
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
