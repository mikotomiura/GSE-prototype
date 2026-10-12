"""Self-tests of the rhythm stage desk check instruments (design 3.7). This file holds the tests that pilot 0
(design 3.0) needs: the world (v1 and v2 write what EH1 round 5 wrote; v3 is v2 with the two declared changes),
the speed quantities and model A_speed, the AUC and the choice rule. Later stages add theirs here.

A failing test stops the run. A failure is fixed in the instruments; the definitions of design 1 and 3 are not
changed (design 3.7).

Usage: selftest.py <config.json> <EH1 round 5 dir> <tmp dir> --hmm-version V
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

import baseline as bl
import ceiling as ce

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
    after_bs = {"FLOW": [], "STRUGGLE": []}
    for sid in bl.p_sids(work):
        t, v = press_rows(work / "ndjson" / f"{sid}.ndjson")
        seg = np.load(work / "labels" / f"{sid}.npz")["seg"]
        d = np.diff(t)
        sec = np.minimum(t // 1000, len(seg) - 1)
        for code, kind in seg_of.items():
            m = (seg[sec[:-1]] == code) & (seg[sec[1:]] == code)  # both presses in a segment of this kind
            short[kind] += d[m & (d < 1000)].tolist()
            # the pause after a backspace acts on the gap after a burst whose last press is a backspace, so look
            # at the gaps (intervals of 1 s or longer: a flight of 150 or 320 ms median almost never reaches 1 s) that follow a backspace
            after_bs[kind] += (d[m & (v[:-1] == 8) & (d >= 1000)] >= 2000).tolist()
    return {k: {"short_median": float(np.median(short[k])), "after_bs_ge2s": float(np.mean(after_bs[k])),
                "n_after_bs": len(after_bs[k])} for k in short}


def test_world(cfg: dict, config: Path, eh1: Path, tmp: Path, hmm: str) -> None:
    eh1_cfg = json.loads((eh1 / "config.json").read_text(encoding="utf-8"))
    check(all(cfg[k] == eh1_cfg[k] for k in GEN_KEYS + ("e13",)), "world: generator settings and e13 equal EH1 round 5")
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("eh1_dir")
    ap.add_argument("tmp")
    ap.add_argument("--hmm-version", required=True)
    a = ap.parse_args()
    config = Path(a.config).resolve()
    cfg = json.loads(config.read_text(encoding="utf-8"))
    tmp = Path(a.tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    test_speed(cfg)
    test_tables(cfg, tmp)
    test_auc_and_choice(cfg)
    test_world(cfg, config, Path(a.eh1_dir).resolve(), tmp, a.hmm_version)
    print(f"selftest: {len(FAILS)} failed" + (f": {FAILS}" if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
