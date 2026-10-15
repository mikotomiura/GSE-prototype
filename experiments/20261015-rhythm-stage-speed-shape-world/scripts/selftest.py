"""Self-tests of the rhythm stage desk check instruments (design 3.7).

Pilot 0 (design 3.0): the world (v1 and v2 write what EH1 round 5 wrote; v3 and v4 are v2 with the declared
changes), the speed quantities and model A_speed, the AUC and the choice rule.
After the freeze: the closed input of the stage, its causality, the stop behaviours and the wobble, the rank, the
window features, the lag measure, the positive controls, the twins, the verdicts (judge), the statistics, the
causality of gse-replay (with --gse-replay), and on the run's own sessions (with --work) the twins, the PC-stall at
lambda 1 and the seg mutation (40 P sessions or more).

Confound world (.steering/20261014-rhythm-stage-speed-confound-world/design.md 3.7): the copied generator, the
speed series (its draw order, c times w, c = 0 against graded t = 0.5) and its wiring (a test series by session time),
world.json, the refusals of --c; the steps are c050 / c100 / c200.
Shape world (.steering/20261015-rhythm-stage-speed-shape-world/design.md 3.7; copied from
experiments/20261014-rhythm-stage-speed-confound-world/scripts/selftest.py at 7d38df98): the confound world's generator
and stage (SHA-256) write and draw what ours do; the factor and drift worlds (the decomposition of w, c = 0 against
graded t = 0.5, the wiring of each world, world.json and the steps f100 / f200 / d100 / d200 with ceiling.worlds); the
r-side controls PCrl- / PCrv- (their drive, stream, lambda 0, causality, and lambda 1 on the main path); the pilot's
L300r part and pc_r.lam (apply, check, fingerprint). The confound world's checks below are kept with the step names
replaced.
Graded world (.steering/20261014-rhythm-stage-graded-world/design.md 3.7): the steps of the world, the L1800 controls
(PC1-1800, PCl-), the judge on L1800, the step rule of pilot 0, and the pilot's and the main run's checks of the
step (pilot.json, lam.<step>, lam_1800.<step>).

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
from collections import Counter
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


def generate(script: Path, config: Path, seed_file: Path, work: Path, world: str, hmm: str,
             t: float | None = None, c: float | None = None) -> None:
    extra = ([] if t is None else ["--t", repr(float(t))]) + ([] if c is None else ["--c", repr(float(c))])
    subprocess.run([sys.executable, str(script), str(config), str(seed_file), str(work), "--hmm-version", hmm,
                    "--world", world, "--smoke", *extra], check=True, capture_output=True)


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
    test_graded(cfg, config, seed_file, tmp, hmm, st2, st4)
    test_confound(cfg, config, seed_file, tmp, hmm)
    test_shape(cfg, config, seed_file, tmp, hmm)


# confound world design 1.3, 3.7: the copied generator (graded world, 424d9500) and the written values
GRADED_SRC = HERE.parent.parent / "20261014-rhythm-stage-graded-world" / "scripts" / "gen_sessions.py"
GRADED_SRC_SHA = "8bd3ffa9dde633e4c86aea03f58aa61767205b84a54eacf8751accf4763fafd4"
DELTA_WANT = 0.3788428508487583  # ln(219.08902300206645 / 150), python repr 2026-10-14
# shape world design 1.2, 3.7: the confound world's generator and stage (7d38df98) and the steps of this task
CONFOUND_SRC = HERE.parent.parent / "20261014-rhythm-stage-speed-confound-world" / "scripts" / "gen_sessions.py"
CONFOUND_SRC_SHA = "d391f2fd76413100403c6f6370edd9418433cef35288d935f601bbc638353e23"
STAGE_SRC = CONFOUND_SRC.parent / "stage.py"
STAGE_SRC_SHA = "ccc73914e6fd3cb6002fdf6d839f1d719cd020dcaa2718658924420876e8207b"
SHAPE_STEPS = {"f100": 1.0, "f200": 2.0, "d100": 1.0, "d200": 2.0}
SHAPE_WORLDS = {"f100": "factor", "f200": "factor", "d100": "drift", "d200": "drift"}
BIG_Z = 3.0  # the test series: intervals about 20 times longer inside a window
# the windows (s) of the test series per unit name: a part drawn by markov and a final FLOW per set (code-reviewer
# round 1 H2: the time origin of each part)
WINDOWS = {"P": [(1000, 4000), (10740, 10800)], "O": [(3600, 4740), (4740, 4800)],
           "Dde": [(3600, 4740), (4740, 4800)], "Dsl": [(10800, 12540), (12540, 12600)], "Dco": [(2000, 3000)],
           "Dsh": [(1000, 2000), (5340, 5400)]}
MADE: list = []  # (names, c, duration_s, shape) of every WindowSpeed made (code-reviewer round 2 H2)


class WindowSpeed:
    """A test series for gen_sessions.Speed: z = BIG_Z at the session times inside the unit's windows, else 0. The
    shape is recorded (shape world design 3.7: each world asks for its own)."""

    def __init__(self, seed, names, c, cfg, duration_s, shape="both"):
        self.names, self.c = names, 1.0
        MADE.append((tuple(names), c, duration_s, shape))

    def z(self, tau_ms):
        return BIG_Z if any(a * 1000 <= tau_ms < b * 1000 for a, b in WINDOWS.get(self.names[0], [])) else 0.0

    def w(self, k):
        return self.z(k * 1000.0)


def window_intervals(work: Path, sid: str, windows: list) -> tuple[int, int, int]:
    """(intervals starting inside the windows, of them below 400 ms, intervals below 400 ms starting outside)."""
    t = np.load(work / "labels" / f"{sid}.npz")["presses_ms"]
    d, start = np.diff(t), t[:-1]
    inside = np.zeros(len(d), dtype=bool)
    for a, b in windows:
        inside |= (start >= a * 1000) & (start < b * 1000)
    return int(inside.sum()), int((inside & (d < 400)).sum()), int((~inside & (d < 400)).sum())


class RecRng:
    """A generator that records the lognormal and uniform draws of gen_typing (code-reviewer round 2 M)."""

    def __init__(self, g):
        self.g, self.calls = g, []

    def lognormal(self, mean, sigma):
        self.calls.append(("lognormal", float(mean), float(sigma)))
        return self.g.lognormal(mean, sigma)

    def uniform(self, lo, hi):
        self.calls.append(("uniform", float(lo), float(hi)))
        return self.g.uniform(lo, hi)

    def random(self):
        return self.g.random()

    def integers(self, *a):
        return self.g.integers(*a)


class ConstSpeed:
    """z = K at every time; records the times it is read at."""
    K = 0.7

    def __init__(self):
        self.c, self.taus = 1.0, []

    def z(self, tau_ms):
        self.taus.append(tau_ms)
        return self.K


def run_gen_in_process(config: Path, seed_file: Path, work: Path, hmm: str, speed_cls, world: str = "confound") -> None:
    old_argv, old_speed = sys.argv, gs.Speed
    sys.argv = ["gen_sessions.py", str(config), str(seed_file), str(work), "--hmm-version", hmm, "--world",
                world, "--c", "1", "--smoke"]
    gs.Speed = speed_cls
    try:
        gs.main()
    finally:
        sys.argv, gs.Speed = old_argv, old_speed


def test_confound(cfg: dict, config: Path, seed_file: Path, tmp: Path, hmm: str) -> None:
    """confound world design 3.7."""
    gen = HERE / "gen_sessions.py"
    # the copied generator and the paths that do not use the speed series
    # line ends made LF before hashing, as ceiling.code_fingerprint (a CRLF checkout is the same file)
    src_ok = (GRADED_SRC.exists()
              and hashlib.sha256(GRADED_SRC.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == GRADED_SRC_SHA)
    check(src_ok, f"confound: the graded world generator {GRADED_SRC.name} is the 424d9500 file (SHA-256)")
    if src_ok:
        src_cfg = GRADED_SRC.parent.parent / "config.json"
        for world, t in (("v1", None), ("v2", None), ("v3", None), ("v4", None), ("graded", 0.25), ("graded", 0.5),
                         ("graded", 0.75)):
            tag = world if t is None else f"{world}{t}"
            generate(GRADED_SRC, src_cfg, seed_file, tmp / f"src-{tag}", world, hmm, t)
            ours = tmp / f"ours-{tag}"
            if not ours.exists():
                generate(gen, config, seed_file, ours, world, hmm, t)
            same = (digest(ours) == digest(tmp / f"src-{tag}")
                    and (ours / "world.json").read_bytes() == (tmp / f"src-{tag}" / "world.json").read_bytes())
            check(same, f"confound: world {tag} writes what the graded world generator writes (with world.json)")
    # the settings and the stall
    seg = gs.graded_segments(cfg, cfg["speed_confound"]["base_t"])
    check(cfg["speed_confound"]["base_t"] == 0.5 and cfg["speed_confound"]["tau_s"] == 300
          and abs(seg["STRUGGLE"]["flight_median_ms"] - 219.08902300206645) < 1e-12
          and abs(seg["STRUGGLE"]["flight_sigma"] - 0.3) < 1e-12 and abs(gs.confound_delta(cfg) - DELTA_WANT) < 1e-12,
          f"confound: base_t 0.5, tau_s 300, STRUGGLE 219.089... ms / 0.3 and delta {gs.confound_delta(cfg)!r}")
    # shape world design 3.7: the confound world's own generator (7d38df98) writes what ours writes for it
    csrc_ok = (CONFOUND_SRC.exists()
               and hashlib.sha256(CONFOUND_SRC.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == CONFOUND_SRC_SHA)
    check(csrc_ok, f"shape: the confound world generator {CONFOUND_SRC.name} is the 7d38df98 file (SHA-256)")
    if csrc_ok:
        csrc_cfg = CONFOUND_SRC.parent.parent / "config.json"
        for c_ in (0.5, 1.0):
            generate(CONFOUND_SRC, csrc_cfg, seed_file, tmp / f"csrc-c{c_}", "confound", hmm, c=c_)
            generate(gen, config, seed_file, tmp / f"ours-confound{c_}", "confound", hmm, c=c_)
            a_, b_ = tmp / f"csrc-c{c_}", tmp / f"ours-confound{c_}"
            same = (digest(a_) == digest(b_) and all((a_ / f).read_bytes() == (b_ / f).read_bytes()
                                                    for f in ("world.json", "speed_jumps.json")))
            check(same, f"shape: confound c = {c_} writes what the confound world generator writes (world.json, "
                        f"speed_jumps.json)")
    # the draw order of the series (u, d(0), eps_0, ...) and its growth on demand
    sp = gs.Speed(20261020, ("P", 3), 1.0, cfg, 5)
    r = gs.derive_rng(20261020, "speed", "P", 3)
    u, d0, e0, e1 = (float(r.standard_normal()) for _ in range(4))
    rho = np.exp(-1.0 / 300)
    q = np.sqrt(1.0 - rho * rho)
    hand = [DELTA_WANT * (u + d0), DELTA_WANT * (u + rho * d0 + q * e0),
            DELTA_WANT * (u + rho * (rho * d0 + q * e0) + q * e1)]
    check(all(abs(sp.w(k) - hand[k]) < 1e-12 for k in range(3)),
          f"confound: w(0..2) {[sp.w(k) for k in range(3)]} follow u, d(0), eps_0, eps_1 of the speed stream")
    short, long_ = gs.Speed(20261020, ("P", 3), 1.0, cfg, 10), gs.Speed(20261020, ("P", 3), 1.0, cfg, 3000)
    check(all(short.w(k) == long_.w(k) for k in range(0, 2500, 7)), "confound: the series grown on demand equals "
          "the series drawn long at once")
    check(gs.Speed(20261020, ("P", 4), 1.0, cfg, 5).w(0) != sp.w(0), "confound: another P session has another series")
    half, two = gs.Speed(20261020, ("P", 3), 0.5, cfg, 5), gs.Speed(20261020, ("P", 3), 2.0, cfg, 5)
    check(all(two.z(k * 1000.0) == 4 * half.z(k * 1000.0) != 0 for k in range(5)), "confound: z is c times w")
    # code-reviewer round 2 H1: z at a session time reads w of its whole second, times c (not w * delta again)
    exact = all(x.z(k * 1000.0 + f) == x.c * x.w(k) for x in (half, sp, two) for k in range(5) for f in (0.0, 999.9))
    check(exact and sp.z(999.9) != sp.z(1000.0) and abs(sp.z(0.0) - hand[0]) < 1e-12,
          "confound: z(k s + f ms) = c * w(k) for f in [0, 1000) and changes at the next whole second")
    # code-reviewer round 2 M: only the intervals inside a burst are shifted, by exactly z, read at the press time
    cfg2 = {**cfg, "segments": gs.graded_segments(cfg, 0.5)}
    p_s = cfg2["segments"]["STRUGGLE"]
    for kind_speed in (None, ConstSpeed()):
        rec = RecRng(np.random.default_rng(11))
        seg_ = gs.gen_typing(rec, "STRUGGLE", 60_000, cfg2, kind_speed, 5_000)
        shift = 0.0 if kind_speed is None else ConstSpeed.K
        fl = [c_ for c_ in rec.calls if c_[0] == "lognormal" and c_[2] == p_s["flight_sigma"]]
        gp = [c_ for c_ in rec.calls if c_[0] == "lognormal" and c_[2] == p_s["gap_sigma"]]
        un = {c_[1:] for c_ in rec.calls if c_[0] == "uniform"}
        ok = (len(fl) == len(seg_.presses) > 10 and len(gp) > 3 and len(fl) + len(gp) == sum(
            c_[0] == "lognormal" for c_ in rec.calls)
              and all(c_[1] == np.log(p_s["flight_median_ms"]) + shift for c_ in fl)
              and all(c_[1] == np.log(p_s["gap_median_ms"]) for c_ in gp)
              and un <= {(0.0, 300.0), (float(p_s["burst_dur_min_s"]), float(p_s["burst_dur_max_s"]))})
        if kind_speed is not None:
            taus = kind_speed.taus
            ok = ok and len(taus) == len(seg_.presses) and all(
                0 <= tau - 5_000 - pr[0] < 1 for tau, pr in zip(taus, seg_.presses))
        check(ok, f"confound: gen_typing with {'no speed' if kind_speed is None else 'z = K'} shifts only the burst "
                  f"intervals ({len(fl)}) by {shift}, not the gaps ({len(gp)}) or the burst lengths, z read at "
                  f"the press time")
    # Codex round 2 and 3: an interval that does not advance the time stops the generator
    under = ConstSpeed()
    under.K = -1e6
    try:
        gs.gen_typing(np.random.default_rng(11), "STRUGGLE", 60_000, cfg2, under, 0)
        raised = False
    except ValueError:
        raised = True
    check(raised, "confound: a key interval that underflows to 0 stops gen_typing")
    # c = 0 against graded t = 0.5 (keys and labels), and c > 0 differs
    generate(gen, config, seed_file, tmp / "ours-c0", "confound", hmm, c=0.0)
    generate(gen, config, seed_file, tmp / "ours-c0.5", "confound", hmm, c=0.5)
    check(digest(tmp / "ours-c0") == digest(tmp / "ours-graded0.5"),
          "confound c = 0: the NDJSON, labels and sessions.json equal graded t = 0.5's")
    check(digest(tmp / "ours-c0.5") != digest(tmp / "ours-graded0.5"), "confound c = 0.5 differs from graded t = 0.5 "
          "(negative control)")
    wj = json.loads((tmp / "ours-c0.5" / "world.json").read_text(encoding="utf-8"))
    check(wj == {"world": "confound", "c": 0.5}, f"confound c = 0.5: world.json {wj}")
    # shape world design 3.7: a confound, graded or v4 work directory is refused as any step of this task
    check(all(ck.world_problems(tmp / w_, cfg, s_) != [] for w_ in ("ours-confound1.0", "ours-graded0.5", "ours-v4")
              for s_ in SHAPE_STEPS), "shape: confound c = 1, graded t = 0.5 and v4 work directories are refused as steps")
    jumps = json.loads((tmp / "ours-c0.5" / "speed_jumps.json").read_text(encoding="utf-8"))
    check(jumps["c"] == 0.5 and len(jumps["pairs"]) == 2 and jumps["quantity"].startswith("z jump")
          and all(v["b"]["n"] == v["a"]["n"] > 0 for v in jumps["pairs"].values()),
          "confound: speed_jumps.json has each D_shuffled pair's boundaries in a and b")
    wiring(cfg, config, seed_file, tmp, hmm, "confound")
    # the spread of the session medians (a diagnostic only: confound world design 3.7, Codex round 1)
    diagnostic_spread(config, seed_file, tmp, hmm, "confound")
    for args in (["--world", "confound"], ["--world", "graded", "--t", "0.5", "--c", "1"], ["--world", "v4", "--c", "1"],
                 ["--world", "confound", "--c", "-1"], ["--world", "confound", "--c", "nan"],
                 ["--world", "confound", "--c", "inf"], ["--world", "confound", "--c", "5"]):
        r = subprocess.run([sys.executable, str(gen), str(config), str(seed_file), str(tmp / "ours-bad"),
                            "--hmm-version", hmm, "--smoke", *args], capture_output=True)
        check(r.returncode != 0, f"confound: gen_sessions refuses {' '.join(args)}")
    r = subprocess.run([sys.executable, str(gen), str(config), str(seed_file), str(tmp / "ours-c4"), "--hmm-version",
                        hmm, "--smoke", "--world", "confound", "--c", "4"], capture_output=True)
    check(r.returncode == 0, "confound: gen_sessions accepts the upper bound --c 4")


def wiring(cfg: dict, config: Path, seed_file: Path, tmp: Path, hmm: str, world: str) -> None:
    """confound world design 3.7 (shape world 3.7: for each world): a test series that is large only inside windows
    of session time."""
    shape = gs.SPEED_WORLDS[world]
    w = tmp / f"ours-window-{world}"
    MADE.clear()
    run_gen_in_process(config, seed_file, w, hmm, WindowSpeed, world)
    man = {m["sid"]: m for m in json.loads((w / "sessions.json").read_text(encoding="utf-8"))}
    # code-reviewer round 2 H2: one series per unit, made once, with the unit's own name and length, and c from --c
    sets_ = cfg["sets"]
    n_of = lambda prefix: len({m["pair"] for m in man.values() if m["sid"].startswith(prefix)})
    want = ({(("P", i), cfg["session"]["duration_s"]) for i in range(12)}
            | {(("O", i), sets_["O"]["prefix_s"] + sets_["O"]["shared_suffix_s"]) for i in range(n_of("Oa"))}
            | {(("Dsh", i), sets_["D_shuffled"]["duration_s"]) for i in range(n_of("Dsh"))}
            | {(("Dde", i), sets_["D_diffend"]["shared_prefix_s"] + sets_["D_diffend"]["suffix_s"])
               for i in range(n_of("Dde"))}
            | {(("Dco", 0), sets_["D_continuous"]["duration_s"]), (("Dsl", 0), sets_["D_sleep"]["duration_s"])})
    got = [(names, dur) for names, _, dur, _ in MADE]
    check(len(got) == len(set(got)) and set(got) == want and all(c_ == 1.0 for _, c_, _, _ in MADE)
          and all(sh == shape for *_, sh in MADE) and n_of("Oa") == 4 and n_of("Dsh") == 2 and n_of("Dde") == 2,
          f"{world} wiring: {len(got)} series, one per unit, named by the unit (P i, O i, Dsh i, Dde i, Dco 0, "
          f"Dsl 0) with its length, c = 1 and the shape {shape}")
    units = {"P": ["P000", "P005"], "O": ["Oa00", "Ob00", "Oa03"], "Dde": ["Dde00a", "Dde00b", "Dde01b"],
             "Dsl": ["Dsl00"], "Dco": ["Dco00"], "Dsh": ["Dsh00a", "Dsh01a"]}
    for unit, sids in units.items():
        for sid in sids:
            # a few short intervals inside are possible without z (the rest of a burst plus an unshifted gap, or an
            # interval across a segment boundary: code-reviewer round 2 M), so a rate, not zero; each window alone
            # (Codex round 3: a short window is not diluted by a long one)
            for win in WINDOWS[unit]:
                n_in, short_in, short_out = window_intervals(w, sid, [win])
                check(sid in man and n_in >= 5 and short_in <= 0.02 * n_in and short_out >= 100,
                      f"{world} wiring: {sid}: {n_in} intervals start inside {win} s, {short_in} of them below "
                      f"400 ms; {short_out} below 400 ms outside")
            x0 = WINDOWS[unit][0][0] * 1000
            t_w = np.load(w / "labels" / f"{sid}.npz")["presses_ms"]
            t_0 = np.load(tmp / "ours-c0" / "labels" / f"{sid}.npz")["presses_ms"]
            check(np.array_equal(t_w[t_w < x0], t_0[t_0 < x0]) and (t_0 < x0).sum() > 100,
                  f"{world} wiring: {sid}: the presses before {x0 // 1000} s equal c = 0's (nothing outside slowed)")
    for i in (0, 1):
        a_j = json.loads((w / "speed_jumps.json").read_text(encoding="utf-8"))["pairs"][f"{i:02d}"]["a"]
        check(a_j["max_abs_z_jump"] in (0.0, BIG_Z) and a_j["median_abs_z_jump"] in (0.0, BIG_Z),
              f"{world}: Dsh{i:02d}a's z jumps under the test series are 0 or {BIG_Z} ({a_j})")
    for i in (0, 1):
        # the b-session carries the segments drawn in a: the intervals slowed inside the a-window (those that do not
        # cross a segment boundary) reappear in b, wherever the shuffle put them (a multiset check)
        a_t = np.load(w / "labels" / f"Dsh{i:02d}a.npz")["presses_ms"]
        b_t = np.load(w / "labels" / f"Dsh{i:02d}b.npz")["presses_ms"]
        a_d, a_s = np.diff(a_t), a_t[:-1]
        in_b = Counter(np.diff(b_t).tolist())
        for lo, hi in WINDOWS["Dsh"]:
            slowed = Counter(a_d[(a_s >= lo * 1000) & (a_s < hi * 1000)].tolist())
            kept = sum(min(n, in_b[v]) for v, n in slowed.items())
            total = sum(slowed.values())
            check(len(a_t) == len(b_t) and not np.array_equal(a_t, b_t) and total >= 5 and kept >= 0.8 * total,
                  f"{world} wiring: Dsh{i:02d}b has {kept} of the {total} intervals slowed in a in {(lo, hi)} s "
                  f"(the segments move with their keys)")
    check(np.array_equal(np.load(w / "labels" / "Dno00.npz")["presses_ms"],
                         np.load(tmp / "ours-c0" / "labels" / "Dno00.npz")["presses_ms"]),
          f"{world} wiring: D_noobs is not slowed")


def diagnostic_spread(config: Path, seed_file: Path, tmp: Path, hmm: str, world: str) -> None:
    """confound world design 3.7 (a diagnostic only, not a test): the SD over P sessions of the log FLOW
    short-interval median at c = 0 / 0.5 / 1 / 2."""
    gen = HERE / "gen_sessions.py"
    sds = []
    for c in (0.0, 0.5, 1.0, 2.0):
        wc = tmp / (f"ours-c{c}" if world == "confound" else f"ours-{world}{c}")
        if not wc.exists():
            generate(gen, config, seed_file, wc, world, hmm, c=c)
        meds = []
        for f in sorted((wc / "labels").glob("P*.npz")):
            z = np.load(f)
            t, seg = z["presses_ms"], z["seg"]
            dd = np.diff(t)
            sec = np.minimum(t[:-1] // 1000, len(seg) - 1)
            ok = (dd < 1000) & (seg[sec] == 0) & (seg[np.minimum(t[1:] // 1000, len(seg) - 1)] == 0)
            if ok.sum():
                meds.append(np.log(np.median(dd[ok])))
        sds.append(round(float(np.std(meds)), 4))
    print(f"     diagnostic ({world}): SD over P sessions of the log FLOW short-interval median at c = 0 / 0.5 / 1 / 2: "
          f"{sds}")


def test_shape(cfg: dict, config: Path, seed_file: Path, tmp: Path, hmm: str) -> None:
    """shape world design 1.2, 3.7: the factor and drift worlds."""
    gen = HERE / "gen_sessions.py"
    check(cfg["ceiling"]["steps"] == SHAPE_STEPS and cfg["ceiling"]["worlds"] == SHAPE_WORLDS
          and gs.SPEED_WORLDS == {"confound": "both", "factor": "factor", "drift": "drift"},
          "shape: the steps f100 / f200 / d100 / d200 at c = 1 / 2 with their worlds")
    # the decomposition of w, and each shape's w from the stream by hand
    for names in (("P", 3), ("O", 1), ("Dsh", 0)):
        both, fac, dri = (gs.Speed(20261020, names, 1.0, cfg, 5, sh) for sh in ("both", "factor", "drift"))
        ks = range(0, 2500, 7)
        check(all(abs(both.w(k) - (fac.w(k) + dri.w(k))) <= 1e-12 * max(1.0, abs(both.w(k))) for k in ks),
              f"shape {names}: w of the confound world is the factor's plus the drift's")
        r = gs.derive_rng(20261020, "speed", *names)
        u, d0, e0 = (float(r.standard_normal()) for _ in range(3))
        rho = np.exp(-1.0 / 300)
        q = np.sqrt(1.0 - rho * rho)
        check(all(fac.w(k) == DELTA_WANT * u or abs(fac.w(k) - DELTA_WANT * u) < 1e-12 for k in ks)
              and len({fac.w(k) for k in ks}) == 1, f"shape {names}: the factor's w is delta * u at every second")
        check(abs(dri.w(0) - DELTA_WANT * d0) < 1e-12 and abs(dri.w(1) - DELTA_WANT * (rho * d0 + q * e0)) < 1e-12
              and dri.w(0) != dri.w(1), f"shape {names}: the drift's w is delta * d(k) (no u)")
        check(all(fac.z(k * 1000.0 + 500) == fac.c * fac.w(k) for k in range(5)), f"shape {names}: z = c * w (factor)")
    for sh in ("factor", "drift"):  # cross-review 1 (Codex): both shapes, c = 1 against c = 2
        two = gs.Speed(20261020, ("P", 3), 2.0, cfg, 5, sh)
        one = gs.Speed(20261020, ("P", 3), 1.0, cfg, 5, sh)
        check(all(two.z(k * 1000.0) == 2 * one.z(k * 1000.0) != 0 for k in range(5)), f"shape: the {sh}'s z is c times w")
    try:
        gs.Speed(1, ("P", 0), 1.0, cfg, 5, "other")
        bad_shape = False
    except ValueError:
        bad_shape = True
    check(bad_shape, "shape: an unknown shape is refused")
    # c = 0 against graded t = 0.5, c = 1 differs, world.json and speed_jumps.json, and the steps' check
    for world in ("factor", "drift"):
        generate(gen, config, seed_file, tmp / f"ours-{world}0.0", world, hmm, c=0.0)
        generate(gen, config, seed_file, tmp / f"ours-{world}1.0", world, hmm, c=1.0)
        check(digest(tmp / f"ours-{world}0.0") == digest(tmp / "ours-graded0.5"),
              f"{world} c = 0: the NDJSON, labels and sessions.json equal graded t = 0.5's")
        check(digest(tmp / f"ours-{world}1.0") != digest(tmp / "ours-graded0.5")
              and digest(tmp / f"ours-{world}1.0") != digest(tmp / "ours-confound1.0"),
              f"{world} c = 1 differs from graded t = 0.5 and from confound c = 1 (negative control)")
        wj = json.loads((tmp / f"ours-{world}1.0" / "world.json").read_text(encoding="utf-8"))
        check(wj == {"world": world, "c": 1.0}, f"{world} c = 1: world.json {wj}")
        jumps = json.loads((tmp / f"ours-{world}1.0" / "speed_jumps.json").read_text(encoding="utf-8"))
        maxes = [v[r_]["max_abs_z_jump"] for v in jumps["pairs"].values() for r_ in ("a", "b")]
        check(jumps["c"] == 1.0 and len(jumps["pairs"]) == 2
              and ((world == "factor" and all(x == 0.0 for x in maxes)) or (world == "drift" and max(maxes) > 0)),
              f"{world}: speed_jumps.json has the pairs; the factor's jumps are 0, the drift's are not ({maxes})")
    want_ok = {("ours-factor1.0", "f100"), ("ours-drift1.0", "d100")}
    for w_ in ("ours-factor1.0", "ours-drift1.0"):
        for s_ in SHAPE_STEPS:
            got_ok = ck.world_problems(tmp / w_, cfg, s_) == []
            check(got_ok == ((w_, s_) in want_ok), f"shape: {w_} {'passes' if got_ok else 'is refused'} as step {s_}")
    bad_cfg = json.loads(json.dumps(cfg))
    del bad_cfg["ceiling"]["worlds"]["d200"]
    try:
        ck.step_world(bad_cfg, "d100")
        refused = False
    except SystemExit:
        refused = True
    check(refused, "shape: a ceiling.worlds that does not name every step is refused")
    # the wiring of each world (the test series replaces Speed, so the wiring is the same code for all three)
    for world in ("factor", "drift"):
        wiring(cfg, config, seed_file, tmp, hmm, world)
    diagnostic_spread(config, seed_file, tmp, hmm, "factor")
    diagnostic_spread(config, seed_file, tmp, hmm, "drift")
    for args in (["--world", "factor"], ["--world", "drift"], ["--world", "factor", "--c", "-1"],
                 ["--world", "drift", "--c", "5"], ["--world", "drift", "--c", "nan"],
                 ["--world", "factor", "--c", "1", "--t", "0.5"]):  # cross-review 1: only --t is wrong
        r = subprocess.run([sys.executable, str(gen), str(config), str(seed_file), str(tmp / "ours-bad"),
                            "--hmm-version", hmm, "--smoke", *args], capture_output=True)
        check(r.returncode != 0, f"shape: gen_sessions refuses {' '.join(args)}")


# graded world design 1.3: the values written out (not computed by the instrument's function; code-reviewer M4)
GRADED_WANT = {0.25: (181.2825238414061, 0.275), 0.5: (219.08902300206645, 0.3), 0.75: (264.7800735717499, 0.325)}


def test_graded(cfg: dict, config: Path, seed_file: Path, tmp: Path, hmm: str, st2: dict, st4: dict) -> None:
    """graded world design 3.7: the settings of each step, the two ends against v4 and v2 byte for byte, the
    short intervals rising with t, and world.json."""
    v4 = cfg["segments_v4"]
    two = ("flight_median_ms", "flight_sigma")
    for t, (m, sd) in GRADED_WANT.items():
        g = gs.graded_segments(cfg, t)
        rest_same = (set(g) == set(v4) and all(g[k] == v4[k] for k in v4 if k != "STRUGGLE")
                     and set(g["STRUGGLE"]) == set(v4["STRUGGLE"])
                     and all(g["STRUGGLE"][k] == v4["STRUGGLE"][k] for k in v4["STRUGGLE"] if k not in two))
        check(rest_same, f"graded t = {t}: every setting but STRUGGLE's flight median and sigma equals segments_v4")
        check(abs(g["STRUGGLE"]["flight_median_ms"] - m) < 1e-12 and abs(g["STRUGGLE"]["flight_sigma"] - sd) < 1e-12,
              f"graded t = {t}: flight median {g['STRUGGLE']['flight_median_ms']!r} and sigma "
              f"{g['STRUGGLE']['flight_sigma']!r} are the written values {m} / {sd}")
    check(cfg["segments_v4"] == json.loads(config.read_text(encoding="utf-8"))["segments_v4"],
          "graded: graded_segments does not change segments_v4 in place")
    generate(HERE / "gen_sessions.py", config, seed_file, tmp / "ours-g0", "graded", hmm, 0.0)
    generate(HERE / "gen_sessions.py", config, seed_file, tmp / "ours-g1", "graded", hmm, 1.0)
    check(digest(tmp / "ours-g0") == digest(tmp / "ours-v4"), "graded t = 0: the sessions equal world v4's (SHA-256)")
    check(digest(tmp / "ours-g1") == digest(tmp / "ours-v2"), "graded t = 1: the sessions equal world v2's (SHA-256)")
    check(digest(tmp / "ours-g0") != digest(tmp / "ours-g1"), "graded: t = 0 and t = 1 differ (negative control)")
    meds = [st4["STRUGGLE"]["short_median"]]
    for t in GRADED_WANT:
        w = tmp / f"ours-graded{t}"
        generate(HERE / "gen_sessions.py", config, seed_file, w, "graded", hmm, t)
        stt = interval_stats(w)
        meds.append(stt["STRUGGLE"]["short_median"])
        # confound world design 3.7: kept apart from the step table (the steps are the widths c now)
        check(json.loads((w / "world.json").read_text(encoding="utf-8")) == {"world": "graded", "t": t},
              f"graded t = {t}: world.json names the graded world at t")
    meds.append(st2["STRUGGLE"]["short_median"])
    print(f"     STRUGGLE short-interval medians v4, t 0.25 / 0.5 / 0.75, v2: {meds}")
    check(all(a < b for a, b in zip(meds, meds[1:])), "graded: STRUGGLE's short-interval median rises with t (v4 to v2)")
    for args in (["--world", "graded"], ["--world", "v4", "--t", "0.5"], ["--world", "graded", "--t", "1.5"]):
        r = subprocess.run([sys.executable, str(HERE / "gen_sessions.py"), str(config), str(seed_file),
                            str(tmp / "ours-bad"), "--hmm-version", hmm, "--smoke", *args], capture_output=True)
        check(r.returncode != 0, f"graded: gen_sessions refuses {' '.join(args)}")


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

    # graded world design 3.0: the step rule (both classifiers' L300 AUC(A_speed) >= 0.90 -> ceiling)
    mk = lambda h, l: {"L300": {"hgb": {"auc_A_speed": h}, "lr": {"auc_A_speed": l}}}
    ma = cfg["ceiling"]["main_auc"]
    check(ma == 0.9 and cfg["ceiling"]["P"] == 240 and cfg["ceiling"]["seed_offset"] == 1
          and cfg["ceiling"]["steps"] == SHAPE_STEPS and cfg["ceiling"]["worlds"] == SHAPE_WORLDS,
          "steps: f100 / f200 / d100 / d200 (c = 1 / 2), P 240, SEED + 1, the ceiling at 0.90")
    check(ce.step_status(mk(0.90, 0.90), ma)["status"] == "ceiling", "steps: 0.90 and 0.90 -> ceiling (equality is the ceiling)")
    check(ce.step_status(mk(0.8999, 0.95), ma)["status"] == "go", "steps: one classifier below 0.90 -> go")
    check(ce.step_status(mk(0.95, 0.8999), ma)["status"] == "go", "steps: the other classifier below 0.90 -> go")
    check(ce.step_status(mk(float("nan"), 0.95), ma)["status"] == "unmeasured", "steps: a NaN -> unmeasured (not a ceiling)")
    check(ce.step_status(mk(None, 0.5), ma)["status"] == "unmeasured", "steps: a failed fit -> unmeasured")
    got = ce.choose_steps({"f100": mk(0.95, 0.91), "f200": mk(0.92, 0.89), "d100": mk(0.8, 0.7), "d200": mk(0.7, 0.7)},
                          cfg)
    check({k: v["status"] for k, v in got.items()} == {"f100": "ceiling", "f200": "go", "d100": "go", "d200": "go"}
          and got["d100"]["c"] == 1.0 and got["d100"]["world"] == "drift" and got["f200"]["world"] == "factor",
          "steps: each step gets its own status, c and world")


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
    test_pc_1800(sess)
    test_pcr(sess)
    test_stage_source(sess)


def test_pc_1800(base: st.Session) -> None:
    """graded world design 1.4, 3.7: PC1-1800 and PCl- at the edges of their spans, causal, and PCl- as PCs- with
    another q."""
    dur = 3600
    seg = np.zeros(dur, dtype=np.int8)
    seg[700:1000] = 1  # stall seconds 700..999 and 2400..2599
    seg[2400:2600] = 3
    sess = st.Session(base.sid, dur, base.presses, base.active, seg, base.feat, base.key_seed)
    a = st.series(sess, st.PC1L_NAME, 1)[0]
    at = lambda f: float(a[f * st.HZ + 5])  # a point with floor(t) = f
    direct = lambda lo, hi: float(np.isin(seg[max(lo, 0): hi], st.STALL_CODES).mean()) if hi > 0 else 0.0
    check(abs(at(2500) - 400 / 1800) < 1e-12, "PC1-1800: [700, 2500) holds 300 + 100 stall seconds (written value 400 / 1800)")
    ok = all(abs(at(f) - direct(f - 1800, f)) < 1e-12 for f in (100, 1000, 1799, 1800, 1801, 2399, 2400, 2401, 2499,
                                                                  2500, 2501, 2799, 2800, 2801, 3599))
    check(ok, "PC1-1800: the stall share of [floor(t) - 1800, floor(t)) at both edges and where the span is shortened")
    check(abs(at(2400) - at(2399)) < 1e-12 and abs(at(2401) - at(2400) - 1 / 1800) < 1e-12,
          "PC1-1800: the stall second 2400 enters at floor(t) = 2401, not 2400 (the right edge is open)")
    b30 = st.pc_blocks(seg, dur, sess.key_seed, 1, 1.0)
    b18 = st.pc_blocks(seg, dur, sess.key_seed, 1, 1.0, st.PCL_SPAN_S)
    check(np.array_equal(b30["U"], b18["U"]) and np.array_equal(b30["N"], b18["N"]) and not np.array_equal(b30["q"], b18["q"]),
          "PCl: the same U and N as PCs-, another q")
    q = b18["q"]
    check(abs(q[42] - 400 / 1800) < 1e-12 and abs(q[40] - 300 / 1800) < 1e-12 and q[0] == 0.0,
          "PCl: q of block 42 is [720, 2520) (400 stall seconds), of block 40 is [600, 2400) (300); block 0 is empty")
    check(all(abs(q[b] - direct(60 * b - 1800, 60 * b)) < 1e-12 for b in range(len(q))),
          "PCl: q of every block is the stall share of [60 b - 1800, 60 b)")
    seg2 = seg.copy()
    seg2[3000:3060] = 1  # block 50, no stall before
    q2 = st.pc_blocks(seg2, dur, sess.key_seed, 1, 1.0, st.PCL_SPAN_S)["q"]
    check(q2[50] == q[50] and q2[51] != q[51], "PCl: the stall seconds inside a block do not change its q (the next one's do)")
    T = 2000
    seg3 = seg.copy()
    seg3[T:] = 1 - np.minimum(seg3[T:], 1)
    late = st.Session(sess.sid, dur, sess.presses, sess.active, seg3, sess.feat, sess.key_seed)
    for name, lam in ((st.PC1L_NAME, None), (f"{st.PCL_PREFIX}S-raw-hold-sec", 1.0), (f"{st.PCL_PREFIX}S-smooth-decay-sub", 1.0)):
        x, y = st.series(sess, name, 1, lam=lam)[0], st.series(late, name, 1, lam=lam)[0]
        check(np.array_equal(x[: T * st.HZ], y[: T * st.HZ]) and not np.array_equal(x, y),
              f"{name}: the stall after T changes no value before T (and some after: negative control)")
    for c in ("S-raw-hold-sec", "S-rank-ground-sub", "S-jitter-decay-sec"):
        x, y = st.series(sess, f"{st.PCL_PREFIX}{c}", 1, lam=0.0), st.series(sess, f"PC0-{c}", 1)
        check(np.array_equal(x[0], y[0]) and np.array_equal(x[1], y[1]), f"PCl-{c} at lambda 0 is PC0-{c}")


def test_stage_source(sess: st.Session) -> None:
    """shape world design 3.7: the names of the confound world's stage draw what its file (7d38df98) draws."""
    import importlib.util
    ok = (STAGE_SRC.exists()
          and hashlib.sha256(STAGE_SRC.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == STAGE_SRC_SHA)
    check(ok, f"stage: the confound world's {STAGE_SRC.name} is the 7d38df98 file (SHA-256)")
    if not ok:
        return
    spec = importlib.util.spec_from_file_location("stage_confound_src", STAGE_SRC)
    old = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = old  # the dataclass Session looks its module up there
    spec.loader.exec_module(old)
    osess = old.Session(sess.sid, sess.duration_s, sess.presses, sess.active, sess.seg, sess.feat, sess.key_seed)
    cands = st.candidates()
    names = ([(c, None) for c in cands] + [("PC1", None), ("PC-corr", None), (st.PC1L_NAME, None)]
             + [(f"PCs-{c}", 0.4) for c in cands] + [(f"PC0-{c}", None) for c in cands]
             + [(f"{st.PCL_PREFIX}{c}", 0.4) for c in cands])
    same = all(np.array_equal(x, y) for n, lam in names
               for x, y in zip(st.series(sess, n, 3, lam=lam), old.series(osess, n, 3, lam=lam)))
    check(same, f"stage: the {len(names)} earlier names equal the confound world's stage")
    check(not np.array_equal(st.series(sess, f"PCs-{cands[0]}", 3, lam=0.4)[0],
                             old.series(osess, f"PCs-{cands[0]}", 3, lam=0.9)[0]),
          "stage: the comparison tells another lambda apart (negative control)")
    check(st.FEAT_NAMES == old.FEAT_NAMES and np.array_equal(
        st.window_features(*st.series(sess, cands[0], 3), 10), old.window_features(*old.series(osess, cands[0], 3), 10)),
        "stage: the window features equal the confound world's")


def test_pcr(base: st.Session) -> None:
    """shape world design 1.3, 3.7: the r-side controls."""
    cfg = json.loads((HERE.parent / "config.json").read_text(encoding="utf-8"))
    check(st.PCR_VAR_SD == cfg["pc_r"]["var_sd"] == 0.2 and st.PCR_TAG == 43 and st.PCRV_TAG == 47
          and len({st.PC_TAG, st.PCR_TAG, st.PCRV_TAG, st.JITTER_TAG}) == 4,
          "PCr: var_sd 0.2 (config.json and stage.py agree), streams 43 and 47 apart from the others")
    check(st.pcr_parse("PCrl-S-raw-hold-sec") == ("level", "S-raw-hold-sec", False)
          and st.pcr_parse("PCrv0-S-rank-ground-sub") == ("var", "S-rank-ground-sub", True),
          "PCr: the names parse to family, candidate and lambda 0")
    for bad in ("PCrx-S-raw-hold-sec", "PCrl-S-raw-hold-min", "PCrl-raw-hold-sec"):
        check(raises_value(st.pcr_parse, bad), f"PCr: {bad} is refused")
    sess = base
    n = sess.duration_s * st.HZ
    # the blocks: PC-stall's construction from their own stream
    b37 = st.pc_blocks(sess.seg, sess.duration_s, sess.key_seed, 1, 0.5)
    b43 = st.pc_blocks(sess.seg, sess.duration_s, sess.key_seed, 1, 0.5, st.PC_SPAN_S, st.PCR_TAG)
    check(not np.array_equal(b37["U"], b43["U"]) and np.array_equal(b37["q"], b43["q"]),
          "PCr: the blocks have the PC-stall's q from another stream (U, N)")
    v = np.repeat(b43["value"], st.PC_BLOCK_S * st.HZ)[:n]
    check(np.array_equal(st.pcr_drive(sess, "level", 0.5, 1), v), "PCr-level: u_r is the block value at every point")
    # level through raw / hold: r is the block value where moving, a is 0.5 where moving
    for res in st.RESOLUTIONS:
        a, r = st.series(sess, f"PCrl-S-raw-hold-{res}", 1, lam=0.5)
        _, _, stp = st.drive(st.stage_input(sess), res)
        check(np.array_equal(r[~stp], np.clip(v, 0, 1)[~stp]) and np.all(a[~stp] == 0.5) and (~stp).sum() > 1000,
              f"PCr-level ({res}): r = the block value and a = 0.5 at the moving points")
    # var: the mean stays 0.5 and the spread of each block is var_sd * its value
    vd = st.pcr_drive(sess, "var", 1.0, 1)
    vals = st.pc_blocks(sess.seg, sess.duration_s, sess.key_seed, 1, 1.0, st.PC_SPAN_S, st.PCR_TAG)["value"]
    blocks = vd[: (n // 600) * 600].reshape(-1, 600)
    sds, wants = blocks.std(axis=1), st.PCR_VAR_SD * vals[: len(blocks)]
    keep = wants > 0.02
    check(keep.sum() >= 10 and np.all(np.abs(sds[keep] / wants[keep] - 1) < 0.1)
          and abs(blocks.mean() - 0.5) < 0.02, f"PCr-var: block sd = var_sd * value (within 10 %, {keep.sum()} blocks), mean 0.5")
    zero = vals[: len(blocks)] == 0
    check(np.all(sds[zero] == 0), "PCr-var: a block of value 0 does not move")
    a, r = st.series(sess, "PCrv-S-raw-hold-sec", 1, lam=1.0)
    _, _, stp = st.drive(st.stage_input(sess), "sec")
    check(np.allclose(r[~stp], np.clip(vd, 0, 1)[~stp]) and np.all(a[~stp] == 0.5),
          "PCr-var (raw, hold, sec): r = the drive (clipped) and a = 0.5 at the moving points")
    # the level and var families use the same blocks; lambda 0 does not read the labels; lambda 1 does
    lv = st.pcr_drive(sess, "level", 0.3, 1)
    e = np.random.default_rng(np.random.SeedSequence([1, sess.key_seed & 0xFFFFFFFF, st.PCRV_TAG])).standard_normal(n)
    check(np.allclose(st.pcr_drive(sess, "var", 0.3, 1), 0.5 + st.PCR_VAR_SD * lv * e),
          "PCr: level and var share the blocks (var = 0.5 + var_sd * level value * e)")
    rng = np.random.default_rng(31)
    perm = st.Session(sess.sid, sess.duration_s, sess.presses, sess.active, rng.permutation(sess.seg), sess.feat,
                      sess.key_seed)
    ok = all(np.array_equal(st.series(sess, f"{pre}{c}", 1)[1], st.series(perm, f"{pre}{c}", 1)[1])
             for pre in ("PCrl0-", "PCrv0-") for c in st.candidates())
    check(ok, "PCr: PCrl0 and PCrv0 of every candidate do not depend on the labels")
    for pre in ("PCrl-", "PCrv-"):
        check(not np.array_equal(st.series(sess, f"{pre}S-raw-hold-sec", 1, lam=1.0)[1],
                                 st.series(perm, f"{pre}S-raw-hold-sec", 1, lam=1.0)[1]),
              f"PCr: {pre} at lambda 1 does (negative control)")
        x0 = st.series(sess, f"{pre}S-raw-hold-sec", 1, lam=0.0)
        y0 = st.series(sess, f"{pre[:-1]}0-S-raw-hold-sec", 1)
        check(all(np.array_equal(p_, q_) for p_, q_ in zip(x0, y0)), f"PCr: {pre} at lambda 0 is its baseline")
    # causal: the labels after T change nothing before T
    T = 2000
    seg3 = sess.seg.copy()
    seg3[T:] = 1 - np.minimum(seg3[T:], 1)
    late = st.Session(sess.sid, sess.duration_s, sess.presses, sess.active, seg3, sess.feat, sess.key_seed)
    for name in ("PCrl-S-raw-hold-sec", "PCrv-S-smooth-decay-sub", "PCrl-S-rank-ground-sec", "PCrv-S-jitter-hold-sub"):
        x, y = st.series(sess, name, 1, lam=1.0), st.series(late, name, 1, lam=1.0)
        check(all(np.array_equal(p_[: T * st.HZ], q_[: T * st.HZ]) for p_, q_ in zip(x, y))
              and not all(np.array_equal(p_, q_) for p_, q_ in zip(x, y)),
              f"{name}: the stall after T changes no value before T (and some after: negative control)")
    # cross-review 1 (code-reviewer): the a of an r-side control depends on neither lambda nor family, so with every
    # r quantity dropped a control's features are its baseline's (design 1.4: the controls take no Rall)
    for c in ("S-raw-hold-sub", "S-smooth-decay-sec", "S-rank-ground-sub", "S-jitter-hold-sec"):
        a_s = [st.series(sess, f"PCrl-{c}", 1, lam=0.7)[0], st.series(sess, f"PCrv-{c}", 1, lam=0.2)[0],
               st.series(sess, f"PCrl0-{c}", 1)[0], st.series(sess, f"PCrv0-{c}", 1)[0]]
        check(all(np.array_equal(a_s[0], x) for x in a_s[1:]), f"PCr {c}: a is the same for both families and every lambda")
    # the stop of the candidate acts on the control: ground puts r to 0 while stopped
    a, r = st.series(sess, "PCrl-S-raw-ground-sub", 1, lam=1.0)
    _, _, stp = st.drive(st.stage_input(sess), "sub")
    check(np.all(r[stp] == 0) and np.all(a[stp] == 0) and stp.sum() > 100, "PCr: the candidate's stop (ground) acts on r and a")


def raises_value(fn, *a) -> bool:
    try:
        fn(*a)
    except (ValueError, AssertionError):
        return True
    return False


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
    j = ck.judge(base(), nulls, auc, cands, cfg, False, tag="L300")
    check(j["verdicts"][c0] == "green" and j["verdicts"]["PC1"] == "works" and j["verdicts"][f"PCs-{c0}"] == "works",
          "judge: everything works -> green below 0.03")
    def v(patch, nl=nulls, au=auc, ff=False):
        d = base()
        d.update(patch)
        return ck.judge(d, nl, au, cands, cfg, ff, tag="L300")
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
    jj = ck.judge(base(), {n: nulls[n] for n in list(nulls)[:-1]}, auc, cands, cfg, False, tag="L300")
    check(jj["null_all_73_ok"] is False, "judge: a judged name without a null is not read as a passing overall null")
    jj = ck.judge({}, {}, None, cands, cfg, True, tag="L300")
    check(all(jj["verdicts"].get(c, "undecidable") == "undecidable" for c in cands)
          and jj["detector"][c0]["reasons"][0] == "fit_failed", "judge: a failed fit -> undecidable")
    check(v({}, nl=None)["detector"][c0]["reasons"] == ["null"], "judge: no null run -> not judged")
    test_judge_1800(cfg, cands, att)


def test_judge_1800(cfg: dict, cands: list[str], att) -> None:
    """graded world design 1.2, 1.4, 3.7: on L1800 the detector reads PC1-1800 and PCl-; PC1 and PCs- are
    descriptive; L300 refuses the new names; a forced pilot_stop."""
    c0, c1 = cands
    P1, PL = st.PC1L_NAME, st.PCL_PREFIX

    def base():
        d = {P1: att(0.2, 0.15, 0.25), "PC1": att(0.05, 0.04, 0.06)}
        for c in cands:
            d[c] = att(0.0, -0.01, 0.02)
            d[f"{PL}{c}"] = att(0.05, 0.035, 0.07)
            d[f"PCs-{c}"] = att(0.01, 0.0, 0.02)
            d[f"PC0-{c}"] = att(0.0, -0.01, 0.02)
        return d
    judged = [n for n in base() if ck.kind_of(n, "L1800") != "descriptive"]
    check(sorted(judged) == sorted([P1] + cands + [f"{PL}{c}" for c in cands] + [f"PC0-{c}" for c in cands]),
          "judge L1800: the judged names are the candidates, PC1-1800, PCl- and PC0-")
    nulls = {n: [{a: 0.0 for a in ck.ATTACKERS}] * 20 for n in judged}
    auc = {"hgb": 0.7, "lr": 0.7}

    def v(patch=None, nl=nulls, forced=None):
        d = base()
        d.update(patch or {})
        return ck.judge(d, nl, auc, cands, cfg, False, tag="L1800", forced=forced)
    j = v()
    check(j["verdicts"][c0] == "green" and j["verdicts"][P1] == "works" and j["verdicts"]["PC1"] == "descriptive"
          and j["verdicts"][f"{PL}{c0}"] == "works" and j["verdicts"][f"PCs-{c0}"] == "descriptive" and j["pc1_ok"],
          "judge L1800: PC1-1800 and PCl- work while the round 2 PC1 and PCs- are weak and descriptive -> green")
    check(v({P1: att(0.15, 0.10, 0.2), "PC1": att(0.3, 0.25, 0.35)})["detector"][c0]["reasons"] == ["weak_detector"],
          "judge L1800: a strong round 2 PC1 does not stand in for a weak PC1-1800")
    check(v({f"{PL}{c0}": att(0.05, 0.03, 0.07), f"PCs-{c0}": att(0.05, 0.035, 0.07)})["detector"][c0]["reasons"]
          == ["weak_stall_pc"], "judge L1800: a working PCs- does not stand in for a weak PCl-")
    nl = {**nulls, f"{PL}{c0}": [{a: 0.03 for a in ck.ATTACKERS}] * 20}
    check(v(nl=nl)["detector"][c0]["reasons"] == ["null"] and v(nl=nl)["verdicts"][c1] == "green",
          "judge L1800: the null of the candidate's PCl- counts (four names)")
    nl = {**nulls, P1: [{a: 0.03 for a in ck.ATTACKERS}] * 20}
    check(v(nl=nl)["detector"][c0]["reasons"] == ["null"], "judge L1800: the null of PC1-1800 counts")
    jj = v({"PC1": {**att(0.0, -0.01, 0.02), "small/lr": {"gain": 0.0, "ci95": [float("nan"), 0.02]}}})
    check(not jj["nan"] and jj["verdicts"][c0] == "green", "judge L1800: a NaN bound of the descriptive PC1 does not stop the label")
    check(jj["null_all_73_ok"] is True, "judge L1800: the overall null is over the judged names (no null run for PC1, PCs-)")
    jj = v(forced="pilot_stop")
    check(all(jj["verdicts"][c] == "undecidable" and jj["detector"][c]["reasons"][0] == "pilot_stop" for c in cands)
          and jj["null_all_73_ok"] is None,
          "judge L1800: a stopped L1800 part of the pilot -> every candidate undecidable (pilot_stop first); no overall null")
    jj = ck.judge(base(), nulls, {"hgb": 0.95, "lr": 0.95}, cands, cfg, False, tag="L1800", forced="pilot_stop")
    check(jj["detector"][c0]["reasons"] == ["pilot_stop", "ceiling"],
          "judge L1800: the forced reason keeps the other reasons (code-reviewer round 2 L2)")
    for n in (P1, f"{PL}{c0}"):
        try:
            ck.kind_of(n, "L300")
            refused = False
        except ValueError:
            refused = True
        check(refused, f"judge: {n} is refused on L300 (fitted on L1800 only)")
    cn = st.config_names(cands)
    names = {n: f"F-{i}" for i, n in enumerate(cands + cn["pc1"] + cn["pcs"] + cn["pc0"] + cn["pccorr"]
                                               + cn["pc1_1800"] + cn["pcl"])}
    f300, n300 = ck.label_names(names, "L300", cn)
    f18, n18 = ck.label_names(names, "L1800", cn)
    check(sorted(f300) == sorted(cands + cn["pc1"] + cn["pcs"] + cn["pc0"] + cn["pccorr"]) and n300 is None,
          "label names: L300 fits the round 2 names only, with every null (as round 2)")
    check(sorted(f18) == sorted(names) and sorted(n18) == sorted(judged + cn["pccorr"]),
          "label names: L1800 fits every name; the null runs on the judged names and PC-corr only")


def test_lam_config(cfg: dict) -> None:
    """Codex round 2: the main run takes only lambdas of the pilot's grid, one per candidate; graded world design
    1.2: per step, and the copied config holds none."""
    steps = set(cfg["ceiling"]["steps"])
    check(all(isinstance(cfg["pc_stall"][k], dict) and set(cfg["pc_stall"][k]) <= steps for k in ("lam", "lam_1800"))
          and isinstance(cfg["pc_r"]["lam"], dict) and set(cfg["pc_r"]["lam"]) <= steps,
          "lambda config: lam, lam_1800 and pc_r.lam are tables keyed by the steps (no lambdas copied over)")
    good = {c: 0.15 for c in st.candidates()}
    mk = lambda lam: {**cfg, "pc_stall": {**cfg["pc_stall"], "lam": {"f100": lam}, "lam_1800": {"f100": lam}}}
    check(ck.lam_problems(mk(good), "f100") == [] and ck.lam_problems(mk(good), "f100", "lam_1800") == [],
          "lambda config: one grid value per candidate passes (lam and lam_1800 of the step)")
    check(ck.lam_problems(mk(good), "d100") != [], "lambda config: another step's table does not pass")
    check(ck.lam_problems({**cfg, "pc_stall": {**cfg["pc_stall"], "lam": good}}, "f100") != [],
          "lambda config: a round 2 table (not per step) does not pass")
    # shape world design 1.3: pc_r.lam.<step> = {level, var} x every candidate, a grid value or null
    goodr = {"level": dict(good), "var": {c: (None if i % 2 else 0.2) for i, c in enumerate(st.candidates())}}
    mkr = lambda t: {**cfg, "pc_r": {**cfg["pc_r"], "lam": {"d100": t}}}
    check(ck.lam_r_problems(mkr(goodr), "d100") == [], "pc_r config: grid values and nulls per family pass")
    check(ck.lam_r_problems(mkr(goodr), "f100") != [], "pc_r config: another step's table does not pass")
    for name, t in (("a missing family", {"level": goodr["level"]}),
                    ("an extra family", {**goodr, "both": goodr["level"]}),
                    ("a missing candidate", {**goodr, "var": dict(list(goodr["var"].items())[1:])}),
                    ("off the grid", {**goodr, "level": {**goodr["level"], "S-raw-hold-sec": 0.12}}),
                    ("a string", {**goodr, "var": {**goodr["var"], "S-raw-hold-sec": "0.2"}}),
                    ("NaN", {**goodr, "var": {**goodr["var"], "S-raw-hold-sec": float("nan")}})):
        check(ck.lam_r_problems(mkr(t), "d100") != [], f"pc_r config: {name} is refused")
    check(ck.lam_r_problems(mkr({**goodr, "level": {**goodr["level"], "S-raw-hold-sec": 0.8}}), "d100") == [],
          "pc_r config: a value of the extended grid (0.8) passes")
    mk = lambda lam: {**cfg, "pc_stall": {**cfg["pc_stall"], "lam": {"f100": lam}}}
    mkp = lambda lam: (mk(lam), "f100")
    for name, lam in (("missing", {k: v for k, v in list(good.items())[1:]}),
                      ("a string", {**good, "S-raw-hold-sec": "0.15"}),
                      ("NaN", {**good, "S-raw-hold-sec": float("nan")}),
                      ("off the grid", {**good, "S-raw-hold-sec": 0.12}),
                      ("above 1", {**good, "S-raw-hold-sec": 1.05}),
                      ("an unknown name", {**good, "S-raw-hold-min": 0.15})):
        check(len(ck.lam_problems(*mkp(lam))) == 1, f"lambda config: {name} is refused")


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
    test_apply_pilot(cfg, merged, sels, want)
    ok = {"PC1": {"fit_failed": False}}
    pc1 = lambda lo: {"PC1": {"lower_max": lo}}
    check(ck.pilot_stop(pc1(0.11), ok, cfg, []) is None, "pilot stop: PC1 lower bound 0.11 -> go on")
    check(ck.pilot_stop(pc1(0.10), ok, cfg, []) == "weak_detector", "pilot stop: PC1 lower bound exactly 0.10 -> stop")
    check(ck.pilot_stop(pc1(nan), ok, cfg, []) == "weak_detector", "pilot stop: a NaN PC1 lower bound -> stop")
    check(ck.pilot_stop({"PC1": None}, ok, cfg, []) == "weak_detector", "pilot stop: no PC1 -> stop")
    check(ck.pilot_stop(pc1(0.2), {**ok, "S-raw-hold-sec": {"fit_failed": True}}, cfg, []) == "fit_failed",
          "pilot stop: a failed fit -> stop")
    check(ck.pilot_stop(pc1(0.2), ok, cfg, ["hgb", "lr"]) == "ceiling", "pilot stop: both classifiers at the ceiling -> stop")
    p18 = lambda lo: {st.PC1L_NAME: {"lower_max": lo}, "PC1": {"lower_max": 0.5}}
    check(ck.pilot_stop(p18(0.11), ok, cfg, [], st.PC1L_NAME) is None
          and ck.pilot_stop(p18(0.10), ok, cfg, [], st.PC1L_NAME) == "weak_detector",
          "pilot stop (L1800): PC1-1800's lower bound is read, not PC1's")
    check(ck.PILOT_PARTS == {"L300": ("PC1", "PCs-", "lam"), "L1800": (st.PC1L_NAME, st.PCL_PREFIX, "lam_1800")},
          "pilot: the L300 part reads PC1 and PCs-, the L1800 part PC1-1800 and PCl-")


def pilot_doc(cfg: dict, step: str, parts: dict, base_seed: int) -> dict:
    sp = cfg["sets"]["pilot"]
    return {"world": cfg["ceiling"]["worlds"][step], "c": cfg["ceiling"]["steps"][step], "step": step,
            "stop": parts["L300"]["stop"], "rule_r": {"pilot_grid": ck.pcr_grid(cfg)},
            "rule": {k: cfg["pc_stall"][k] for k in ck.RULE_KEYS}, "seed": base_seed + sp["seed_offset"],
            "n_sessions": sp["P"], "bootstrap": sp["bootstrap"], "config_fingerprint": ce.cfg_fingerprint(cfg),
            "code_fingerprint": ce.code_fingerprint(),
            "parts": parts}


def part_doc(tag: str, merged: dict, cfg: dict, auc=None) -> dict:
    """A part as pilot_part writes it, from hand-made maxima (part_result gives its stop and selection)."""
    auc = auc or {"hgb": 0.7, "lr": 0.7}
    per = {f"{tag}-{k}": {"fit_failed": False} for k in ("x", "y")}
    stop, sels, ceil = ck.part_result(tag, merged, per, auc, cfg)
    return {"stop": stop, "selection": sels, "auc_A_speed": auc, "ceiling_kinds": ceil, "per_batch": per,
            "configs": {k: ({kk: v[kk] for kk in ck.REC_KEYS} if v else None) for k, v in merged.items()}}


def r_part_doc(merged_r: dict, cfg: dict, auc=None) -> dict:
    """The L300r part as pilot_r_part writes it, from hand-made maxima (shape world design 1.3)."""
    auc = auc or {"hgb": 0.7, "lr": 0.7}
    sels, ceil = ck.pilot_r_result(merged_r, auc, cfg)
    per = {f"{ck.PILOT_R_TAG}-{f}-{c}": {"fit_failed": all(
        merged_r.get(ck.pilot_key(c, x, p)) is None for x in [0.0] + ck.pcr_grid(cfg))}
        for f, p in ck.PCR_FAMILIES.items() for c in st.candidates()}
    return {"stop": None, "selection": sels, "auc_A_speed": auc, "ceiling_kinds": ceil, "per_batch": per,
            "configs": {k: ({kk: v[kk] for kk in ck.REC_KEYS} if v else None) for k, v in merged_r.items()}}


def test_apply_pilot(cfg: dict, merged: dict, sels: dict, want: dict) -> None:
    """graded world design 1.2, 3.7 (and the cross-review round 2): pilot.json -> lam.<step>, lam_1800.<step> -> the
    main run's check; the L1800 choices differ from the L300 ones, so the two parts cannot be swapped unseen; the other
    steps' tables are kept; another step, a stopped or recomputed-differently part, a tampered selection, another config
    or a hand-edited config are refused."""
    cands = st.candidates()
    grid = [float(x) for x in cfg["pc_stall"]["pilot_grid"]]
    base_seed = 20261016
    rec = lambda g, lo: {"gain_max": g, "lower_max": lo, "upper_max": g + 0.008, "n_nan_bounds": 0}
    # the L1800 part: the L300 maxima under PCl- names, one grid step later (code-reviewer round 2 M1)
    merged18 = {st.PC1L_NAME: rec(0.3, 0.25)}
    for c in cands:
        merged18[ck.pilot_key(c, 0.0, st.PCL_PREFIX)] = rec(0.004, -0.004)
        for i, x in enumerate(grid):
            src = merged[ck.pilot_key(c, grid[max(i - 1, 0)])]
            merged18[ck.pilot_key(c, x, st.PCL_PREFIX)] = src if i > 0 else rec(0.0, -0.008)
    want18 = {c: grid[grid.index(want[c]) + 1] for c in cands}
    check({c: s["lam"] for c, s in ck.choose_all(merged18, cfg, st.PCL_PREFIX).items()} == want18 and want18 != want
          and ck.choose_all(merged18, cfg)[cands[0]]["lam"] is None,
          "pilot (L1800): the PCl- names give their own choices (not L300's); PCs- names are not read for L1800")
    p300, p18 = part_doc("L300", merged, cfg), part_doc("L1800", merged18, cfg)
    check(p300["stop"] is None and p18["stop"] is None, "pilot: the hand-made parts do not stop")
    # shape world design 1.3: the L300r part, level one grid step earlier than L300 and var one later, and the var of
    # the first candidate with no finite value (null, not a stop)
    rgrid = ck.pcr_grid(cfg)
    check(rgrid[: len(grid)] == grid and rgrid[len(grid):] == [0.4, 0.5, 0.6, 0.8, 1.0],
          "pilot (L300r): pc_r.pilot_grid is the PC-stall's grid and 0.4 / 0.5 / 0.6 / 0.8 / 1.0 (decisions 10)")
    merged_r = {}
    for c in cands:
        for i, x in enumerate(rgrid):  # the PC-stall's grid values as before; the steps above 0.3 far over the band
            if i >= len(grid):
                far = rec(0.2 + i * 0.01, 0.19 + i * 0.01)
                merged_r[ck.pilot_key(c, x, "PCrl-")] = far
                merged_r[ck.pilot_key(c, x, "PCrv-")] = None if c == cands[0] else far
                continue
            merged_r[ck.pilot_key(c, x, "PCrl-")] = merged[ck.pilot_key(c, grid[min(i + 1, len(grid) - 1)])]
            merged_r[ck.pilot_key(c, x, "PCrv-")] = (None if c == cands[0] else
                                                     merged[ck.pilot_key(c, grid[max(i - 1, 0)])] if i else rec(0.0, -0.008))
        merged_r[ck.pilot_key(c, 0.0, "PCrl-")] = merged_r[ck.pilot_key(c, 0.0, "PCrv-")] = rec(0.004, -0.004)
    merged_r[ck.pilot_key(cands[0], 0.0, "PCrv-")] = None  # a failed batch is null throughout (cross-review 2)
    want_r = {"level": {c: grid[grid.index(want[c]) - 1] for c in cands},
              "var": {c: (None if c == cands[0] else grid[grid.index(want[c]) + 1]) for c in cands}}
    pr = r_part_doc(merged_r, cfg)
    got_r = {f: {c: pr["selection"][f][c]["lam"] for c in cands} for f in ck.PCR_FAMILIES}
    check(got_r == want_r and want_r["level"] != want and ck.PCR_FAMILIES == {"level": "PCrl-", "var": "PCrv-"},
          "pilot (L300r): each family has its own choices; a candidate with no finite value gets null")
    # a control that reaches the band only above 0.3 is chosen there (the extended grid is read)
    late = dict(merged_r)
    for i, x in enumerate(rgrid):
        g_ = {0.6: 0.056, 0.8: 0.07, 1.0: 0.078}.get(x, 0.005 + 0.001 * i)  # rising: one closest value, no ties
        late[ck.pilot_key(cands[2], x, "PCrl-")] = rec(g_, g_ - 0.011)
    check(ck.pilot_r_result(late, {"hgb": 0.7, "lr": 0.7}, cfg)[0]["level"][cands[2]]["lam"] == 0.6,
          "pilot (L300r): a control in the band only at 0.6 and above gets 0.6 (the grid beyond 0.3 is used)")
    check(ck.choose_all(late, cfg, "PCrl-")[cands[2]]["lam"] == grid[-1],
          "pilot (L300r): the PC-stall's grid alone would stop at 0.3 (negative control)")
    # part_result reads the part's own label's AUC (code-reviewer round 2 M3)
    s18c = ck.part_result("L1800", merged18, p18["per_batch"], {"hgb": 0.92, "lr": 0.95}, cfg)
    s300 = ck.part_result("L300", merged, p300["per_batch"], {"hgb": 0.7, "lr": 0.7}, cfg)
    check(s18c[0] == "ceiling" and s300[0] is None, "pilot: a part at its own label's ceiling stops; the other part does not")
    good = pilot_doc(cfg, "d100", {"L300": p300, "L1800": p18, ck.PILOT_R_TAG: pr}, base_seed)
    old = {c: grid[0] for c in cands}  # another step's tables, written before (Codex round 2 P1)
    old_r = {"level": dict(old), "var": dict(old)}
    pre = json.loads(json.dumps(cfg))
    # only f100 before: the real config.json gains a table per step as the steps run (confound world design 8)
    pre["pc_stall"]["lam"] = {"f100": old}
    pre["pc_stall"]["lam_1800"] = {"f100": old}
    pre["pc_r"]["lam"] = {"f100": old_r}
    # shape world design 1.3: checked by name before --apply-pilot relies on it (a failure here, not a refusal below)
    check(ce.cfg_fingerprint(pre) == ce.cfg_fingerprint({**pre, "pc_r": {**pre["pc_r"], "lam": {}}}),
          "fingerprint: pc_r.lam (written after the pilots) does not change it")
    with tempfile.TemporaryDirectory() as d:
        cp, pp = Path(d) / "config.json", Path(d) / "pilot.json"
        (Path(d) / "SEED").write_text(f"{base_seed}\n", encoding="utf-8")
        fresh = lambda c=pre: cp.write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        fresh()
        pp.write_text(json.dumps(good), encoding="utf-8")
        ck.apply_pilot(cp, pp, "d100")
        back = json.loads(cp.read_text(encoding="utf-8"))
        rest = lambda c: {**c, "pc_stall": {k: v for k, v in c["pc_stall"].items() if k not in ("lam", "lam_1800")},
                          "pc_r": {k: v for k, v in c["pc_r"].items() if k != "lam"}}
        check(back["pc_stall"]["lam"] == {"f100": old, "d100": want}
              and back["pc_stall"]["lam_1800"] == {"f100": old, "d100": want18}
              and back["pc_r"]["lam"] == {"f100": old_r, "d100": want_r} and rest(back) == rest(pre),
              "pilot: --apply-pilot writes lam.d100 (L300's), lam_1800.d100 (L1800's) and pc_r.lam.d100 (L300r's), "
              "keeps f100, nothing else")
        check(ck.main_lams(back, pp, base_seed, "d100") == (want, want18, None)
              and ck.main_lams_r(back, pp, base_seed, "d100") == want_r,
              "main: the step's pilot.json and config.json agree (L300, L1800 and L300r each its own)")
        hand_edits = [(f"lam.<step>", lambda h: h["pc_stall"]["lam"]["d100"]),
                      (f"lam_1800.<step>", lambda h: h["pc_stall"]["lam_1800"]["d100"]),
                      ("pc_r.lam.<step>.level", lambda h: h["pc_r"]["lam"]["d100"]["level"]),
                      ("pc_r.lam.<step>.var", lambda h: h["pc_r"]["lam"]["d100"]["var"])]
        for name, where in hand_edits:
            h = json.loads(json.dumps(back))
            t = where(h)
            t[cands[1]] = grid[0] if t[cands[1]] != grid[0] else grid[1]
            refused = []
            for fn in (ck.main_lams, ck.main_lams_r):
                try:
                    fn(h, pp, base_seed, "d100")
                    refused.append(False)
                except SystemExit:
                    refused.append(True)
            check(refused[0] if name.startswith("lam") else refused[1],
                  f"main: a hand-edited {name} that is not the pilot's choice stops the run")
        h = json.loads(json.dumps(back))
        h["pc_r"]["lam"]["d100"]["level"], h["pc_r"]["lam"]["d100"]["var"] = (h["pc_r"]["lam"]["d100"]["var"],
                                                                               h["pc_r"]["lam"]["d100"]["level"])
        try:
            ck.main_lams_r(h, pp, base_seed, "d100")
            refused = False
        except SystemExit:
            refused = True
        check(refused, "main: pc_r.lam with the families swapped stops the run")
        for other in ("f100", "d200"):
            try:
                ck.main_lams(back, pp, base_seed, other)
                refused = False
            except SystemExit:
                refused = True
            check(refused, f"main: the pilot.json of step d100 is refused for step {other}")
        # a stopped L1800 part (PC1-1800 weak): lam only; the main run reads the stop from pilot.json
        weak18 = part_doc("L1800", {**merged18, st.PC1L_NAME: rec(0.12, 0.08)}, cfg)
        stopped = pilot_doc(cfg, "d100", {"L300": p300, "L1800": weak18, ck.PILOT_R_TAG: pr}, base_seed)
        check(weak18["stop"] == "weak_detector", "pilot: a weak PC1-1800 stops the L1800 part")
        fresh()
        pp.write_text(json.dumps(stopped), encoding="utf-8")
        ck.apply_pilot(cp, pp, "d100")
        back2 = json.loads(cp.read_text(encoding="utf-8"))
        check(back2["pc_stall"]["lam"] == {"f100": old, "d100": want} and back2["pc_stall"]["lam_1800"] == {"f100": old}
              and back2["pc_r"]["lam"] == {"f100": old_r, "d100": want_r},
              "pilot: a stopped L1800 part writes lam.<step> and pc_r.lam.<step>, no lam_1800.<step> (f100 kept)")
        check(ck.main_lams(back2, pp, base_seed, "d100") == (want, None, "weak_detector"),
              "main: a stopped L1800 part -> L1800 undecidable (pilot_stop), L300 and L60 go on")
        try:
            ck.main_lams(back, pp, base_seed, "d100")
            refused = False
        except SystemExit:
            refused = True
        check(refused, "main: lam_1800.<step> set while the pilot's L1800 part stopped stops the run")
        swap = lambda part, **kw: {**good, "parts": {**good["parts"], part: {**good["parts"][part], **kw}}}
        flip = lambda sels_, c: {**sels_, c: {**sels_[c], "lam": grid[0] if sels_[c]["lam"] != grid[0] else grid[1]}}
        edited = json.loads(json.dumps(pre))
        edited["e13"]["pc_lower"] = 0.11
        bad_cases = (
            ("another step of the same c (f100)", {**good, "step": "f100", "world": "factor"}),
            ("another step (d200's c)", {**good, "step": "d200", "c": 2.0}),
            ("the right step name with another c", {**good, "c": 2.0}),
            ("another world", {**good, "world": "v4"}),
            ("the factor world at the same c", {**good, "world": "factor"}),
            ("the confound world at the same c", {**good, "world": "confound"}),
            ("a graded world pilot.json at the same value", {**{k: v for k, v in good.items() if k != "c"},
                                                              "world": "graded", "t": good["c"]}),
            ("a missing L300r part", {**good, "parts": {k: v for k, v in good["parts"].items() if k != ck.PILOT_R_TAG}}),
            ("an L300r part claimed stopped", swap(ck.PILOT_R_TAG, stop="weak_detector")),
            ("an L300r part without its fits", {**good, "parts": {**good["parts"], ck.PILOT_R_TAG: {
                k: v for k, v in pr.items() if k != "per_batch"}}}),
            ("an L300r level selection that does not follow from the maxima", swap(ck.PILOT_R_TAG, selection={
                **pr["selection"], "level": flip(pr["selection"]["level"], cands[1])})),
            ("an L300r var null replaced by a value", swap(ck.PILOT_R_TAG, selection={
                **pr["selection"], "var": {**pr["selection"]["var"], cands[0]: {"lam": grid[0]}}})),
            ("another L300r grid", {**good, "rule_r": {"pilot_grid": grid}}),
            ("an emptied L300r part (every control null)", swap(ck.PILOT_R_TAG, configs={}, selection={
                f: {c: {"lam": None} for c in cands} for f in ck.PCR_FAMILIES})),
            ("an L300r value nulled while its batch did not fail", swap(ck.PILOT_R_TAG, configs={
                **pr["configs"], ck.pilot_key(cands[1], 0.1, "PCrl-"): None})),
            ("an L300r value emptied to {} while its batch did not fail", swap(ck.PILOT_R_TAG, configs={
                **pr["configs"], ck.pilot_key(cands[1], 0.1, "PCrl-"): {}})),
            ("an L300r failed batch with a finite value (at lambda 0, which the selection does not read)",
             swap(ck.PILOT_R_TAG, configs={**pr["configs"], ck.pilot_key(cands[0], 0.0, "PCrv-"): rec(0.004, -0.004)})),
            ("an L300r part with a batch missing", swap(ck.PILOT_R_TAG, per_batch={
                k: v for k, v in pr["per_batch"].items() if not k.endswith(cands[1])})),
            ("no L300r grid", {k: v for k, v in good.items() if k != "rule_r"}),
            ("the L300r families swapped", swap(ck.PILOT_R_TAG, selection={
                "level": pr["selection"]["var"], "var": pr["selection"]["level"]})),
            ("a stopped L300 part", {**swap("L300", stop="weak_detector"), "stop": "weak_detector"}),
            ("an L300 stop that differs from the pilot's", {**good, "stop": "fit_failed"}),
            ("an L1800 part claimed stopped while its values do not stop", swap("L1800", stop="weak_detector")),
            ("an L1800 part claimed fine while its values stop", {**stopped, "parts": {
                **stopped["parts"], "L1800": {**weak18, "stop": None, "selection": p18["selection"]}}}),
            ("a missing L1800 part", {**good, "parts": {"L300": good["parts"]["L300"]}}),
            ("an L1800 part without its fits", {**good, "parts": {**good["parts"], "L1800": {
                k: v for k, v in p18.items() if k != "per_batch"}}}),
            ("an L300 selection that does not follow from the maxima", swap("L300", selection=flip(p300["selection"], cands[0]))),
            ("an L1800 selection that does not follow from the maxima", swap("L1800", selection=flip(p18["selection"], cands[0]))),
            ("L300's selection put in the L1800 part", swap("L1800", selection=p300["selection"])),
            ("a round 2 pilot.json (no parts)", {k: v for k, v in good.items() if k != "parts"}),
            ("another seed", {**good, "seed": 20261014}),
            ("another P", {**good, "n_sessions": 40}),
            ("another rule", {**good, "rule": {**good["rule"], "aim": 0.05}}),
            ("another config (fingerprint)", {**good, "config_fingerprint": ce.cfg_fingerprint(edited)}),
            ("other instruments (code fingerprint)", {**good, "code_fingerprint": "0" * 64}))
        for name, bad in bad_cases:
            fresh()
            pp.write_text(json.dumps(bad), encoding="utf-8")
            try:
                ck.apply_pilot(cp, pp, "d100")
                refused = False
            except SystemExit:
                refused = True
            now = json.loads(cp.read_text(encoding="utf-8"))
            check(refused and now["pc_stall"] == pre["pc_stall"] and now["pc_r"] == pre["pc_r"],
                  f"pilot: --apply-pilot refuses {name} and leaves config.json as it was")
        fresh(edited)
        pp.write_text(json.dumps(good), encoding="utf-8")
        try:
            ck.apply_pilot(cp, pp, "d100")
            refused = False
        except SystemExit:
            refused = True
        check(refused, "pilot: a config.json changed after the pilot (e13.pc_lower) refuses the pilot (fingerprint)")
    deep = json.loads(json.dumps(pre))
    deep["pc_stall"]["_comment_x"] = "x"
    check(ce.cfg_fingerprint(back) == ce.cfg_fingerprint(pre) == ce.cfg_fingerprint({**pre, "_comment": "x"})
          == ce.cfg_fingerprint(deep), "fingerprint: the lambda tables and the comments (at any depth) do not change it")
    deep["pc_stall"]["aim"] = 0.06
    check(ce.cfg_fingerprint(deep) != ce.cfg_fingerprint(pre), "fingerprint: a setting inside a section changes it")
    vs = json.loads(json.dumps(pre))
    vs["pc_r"]["var_sd"] = 0.3
    check(ce.cfg_fingerprint(vs) != ce.cfg_fingerprint(pre) and back["pc_r"]["lam"] != pre["pc_r"]["lam"],
          "fingerprint: pc_r.lam does not change it (above), pc_r.var_sd does")
    ws = json.loads(json.dumps(pre))
    ws["ceiling"]["worlds"]["d100"] = "factor"
    check(ce.cfg_fingerprint(ws) != ce.cfg_fingerprint(pre), "fingerprint: a step's world changes it")
    with tempfile.TemporaryDirectory() as d:
        sd = Path(d) / "scripts"
        sd.mkdir()
        (Path(d) / "run.sh").write_bytes(b"a\r\nb\n")
        (sd / "x.py").write_bytes(b"print(1)\n")
        f1 = ce.code_fingerprint(sd)
        (Path(d) / "run.sh").write_bytes(b"a\nb\n")
        f2 = ce.code_fingerprint(sd)
        (sd / "x.py").write_bytes(b"print(2)\n")
        check(f1 == f2 != ce.code_fingerprint(sd), "code fingerprint: line ends do not change it; a change of a script does")
    test_ceiling_gate(cfg, base_seed)
    test_label_plan()


def test_ceiling_gate(cfg: dict, base_seed: int) -> None:
    """graded world design 3.0 (cross-review round 2): a step runs only when ceiling.json says go and was made under
    this config."""
    mk = lambda h, l: {"L300": {"hgb": {"auc_A_speed": h}, "lr": {"auc_A_speed": l}}}
    doc = {"seed": base_seed + cfg["ceiling"]["seed_offset"], "main_auc": cfg["ceiling"]["main_auc"],
           "P": {s: cfg["ceiling"]["P"] for s in cfg["ceiling"]["steps"]}, "config_fingerprint": ce.cfg_fingerprint(cfg),
           "code_fingerprint": ce.code_fingerprint(),
           "results": {s: mk(0.7, 0.72) for s in cfg["ceiling"]["steps"]},
           "steps": {s: {"world": cfg["ceiling"]["worlds"][s], "c": c, "status": "go"}
                     for s, c in cfg["ceiling"]["steps"].items()}}
    check(ck.ceiling_problems(doc, cfg, base_seed, "d100") == [], "ceiling gate: a go step of this config passes")
    moved = json.loads(json.dumps(cfg))
    moved["ceiling"]["steps"]["d100"] = 0.9
    for name, d_, c_ in (
            ("a ceiling step", {**doc, "steps": {**doc["steps"], "d100": {**doc["steps"]["d100"], "status": "ceiling"}}}, cfg),
            ("an unmeasured step", {**doc, "steps": {**doc["steps"], "d100": {**doc["steps"]["d100"],
                                                                              "status": "unmeasured"}}}, cfg),
            ("a step missing", {**doc, "steps": {"f100": doc["steps"]["f100"]}}, cfg),
            ("another world for the step", {**doc, "steps": {**doc["steps"], "d100": {**doc["steps"]["d100"],
                                                                                      "world": "factor"}}}, cfg),
            ("another seed", {**doc, "seed": base_seed}, cfg),
            ("another P", {**doc, "P": {**doc["P"], "d100": 40}}, cfg),
            ("another main_auc", {**doc, "main_auc": 0.85}, cfg),
            ("a c moved in config.json after pilot 0", doc, moved),
            ("another config (fingerprint)", {**doc, "config_fingerprint": "0" * 64}, cfg),
            ("other instruments (code fingerprint)", {**doc, "code_fingerprint": "0" * 64}, cfg),
            ("a go status over values at the ceiling", {**doc, "results": {**doc["results"], "d100": mk(0.93, 0.95)}}, cfg),
            ("a go status with no measured values", {k: v for k, v in doc.items() if k != "results"}, cfg)):
        check(ck.ceiling_problems(d_, c_, base_seed, "d100") != [], f"ceiling gate: {name} is refused")


def test_label_plan() -> None:
    """graded world design 1.2, 3.9 (code-reviewer round 2 M3): the main run's plan per label."""
    cands = st.candidates()
    cn = st.config_names(cands)
    base = cands + cn["pc1"] + cn["pcs"] + cn["pc0"] + cn["pccorr"]
    names = {n: f"F-{i}" for i, n in enumerate(base + cn["pc1_1800"] + cn["pcl"])}
    for tag in ("L300", "L60"):
        f, nl, forced = ck.label_plan(names, tag, cn, "weak_detector")
        check(sorted(f) == sorted(base) and nl is None and forced is None,
              f"label plan: {tag} fits the round 2 names with every null and is never forced (even if L1800 stopped)")
    f, nl, forced = ck.label_plan(names, "L1800", cn, None)
    check(sorted(f) == sorted(names) and forced is None, "label plan: L1800 with its controls is not forced")
    stopped = {n: v for n, v in names.items() if n in base}  # the main run leaves the 25 out when L1800 stopped
    f, nl, forced = ck.label_plan(stopped, "L1800", cn, "weak_detector")
    check(sorted(f) == sorted(base) and forced == "pilot_stop", "label plan: L1800 forced to pilot_stop when its part stopped")


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
    PCL = f"{st.PCL_PREFIX}S-raw-hold-sec@1.00"  # graded world design 3.7: the L1800 control on the main path
    # shape world design 3.7: the r-side controls at lambda 1 and their baselines on the main path
    PRL, PRV = "PCrl-S-raw-hold-sub@1.00", "PCrv-S-raw-hold-sub@1.00"
    PRL0, PRV0 = "PCrl0-S-raw-hold-sub", "PCrv0-S-raw-hold-sub"
    specs = [(PCS, "PCs-S-raw-hold-sec", 1.0), (MUT, "S-raw-hold-sec", None, "seg"), (PC0, "PC0-S-raw-hold-sec", 0.0),
             (RAW, "S-raw-hold-sec", None), (PCL, f"{st.PCL_PREFIX}S-raw-hold-sec", 1.0),
             (PRL, "PCrl-S-raw-hold-sub", 1.0), (PRV, "PCrv-S-raw-hold-sub", 1.0), (PRL0, PRL0, 0.0), (PRV0, PRV0, 0.0)]
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
        n300 = {k: v for k, v in names.items() if k != PCL}
        r = ck.e13_target("L300", tab["L300"], n300, [], cfg, seed, jobs, 50, 0, scratch, [])
        g = {k: r["configs"][k]["gain_max"] for k in n300}
        r18 = ck.e13_target("L1800", tab["L1800"], {PCL: names[PCL]}, [], cfg, seed, jobs, 50, 0, scratch, [])
        g18 = r18["configs"][PCL]["gain_max"]
        check(g18 > 0.10, f"PC: PCl-S-raw-hold-sec at lambda 1 -> L1800 point max {g18:+.3f} > 0.10 (main path)")
        check(g[PCS] > 0.10, f"PC: PCs-S-raw-hold-sec at lambda 1 -> L300 point max {g[PCS]:+.3f} > 0.10 (main path)")
        check(g[MUT] > 0.10, f"mutation: seg mixed into the mapping -> L300 point max {g[MUT]:+.3f} > 0.10 (main path)")
        check(g[PC0] < 0.03, f"PC0-S-raw-hold-sec L300 point max {g[PC0]:+.3f} < 0.03 (negative control)")
        check(g[PRL] > 0.10, f"PCr: PCrl-S-raw-hold-sub at lambda 1 -> L300 point max {g[PRL]:+.3f} > 0.10 (main path)")
        check(g[PRV] > 0.05, f"PCr: PCrv-S-raw-hold-sub at lambda 1 -> L300 point max {g[PRV]:+.3f} > 0.05 (main path)")
        check(g[PRL0] < 0.03 and g[PRV0] < 0.03,
              f"PCr: their baselines at lambda 0 -> {g[PRL0]:+.3f} / {g[PRV0]:+.3f} < 0.03 (negative control)")
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
        test_replay_causal(a.gse_replay, tmp / "ours-drift1.0", tmp)  # shape world: a d100 work directory
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
