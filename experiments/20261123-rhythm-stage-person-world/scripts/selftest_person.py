"""Self-tests of the person world (design 3.7: G0-G5, R1, P1-P5, Q1-Q3, J1-J4) and their mutants.

Called by selftest.py (which owns `check`, FAILS and the mutant loop). Every test takes `chk(cond, name)` first. The tests
generate nothing with the run's seeds (SEED, SEED + 1, SEED + 2): they use TEST_SEED = 7.
"""

from __future__ import annotations

import contextlib
import hashlib
import inspect
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

import checks as ck
import gen_sessions as gs
import person as pe
import stage as st

HERE = Path(__file__).resolve().parent
SRC_DIR = HERE.parent.parent / "20261015-rhythm-stage-speed-shape-world" / "scripts"
TEST_SEED = 7
SRC_GEN_SHA = "b6e9e0c9c515c2756ea4ddc459992e69e3ab8646da91d6dc75cfc2631e6618d0"  # the copied generator (LF)
SHORT_S = 1800  # the self-test sessions (not the run's 10800 s)


@contextlib.contextmanager
def kinds(ks: tuple):
    """Fit only these classifiers inside a test (the tests of the fits are about wiring, not the classifier)."""
    old = pe.KINDS
    pe.KINDS = ks
    try:
        yield
    finally:
        pe.KINDS = old


def seg_signature(segs) -> list:
    return [(s.kind, s.dur_ms) for s in segs]


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def test_g0(chk, cfg: dict, config: Path, tmp: Path, hmm: str) -> None:
    """G0: every earlier world is written byte for byte as the copied generator writes it."""
    src = SRC_DIR / "gen_sessions.py"
    if not src.exists() or hashlib.sha256(src.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != SRC_GEN_SHA:
        chk(False, "G0: the copied generator is not the 1cf9fcb9 file (not run)")
        return
    seed_file = tmp / "SEED.g0"
    seed_file.write_text(f"{TEST_SEED}\n", encoding="utf-8")
    worlds = [("v1", []), ("v2", []), ("v3", []), ("v4", []), ("graded", ["--t", "0.5"]),
              ("confound", ["--c", "1.0"]), ("factor", ["--c", "2.0"]), ("drift", ["--c", "2.0"])]
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}  # ours last: the environment cannot turn it off
    all_same = True
    for w, extra in worlds:
        dirs = {}
        for tag, script in (("old", src), ("new", HERE / "gen_sessions.py")):
            d = tmp / f"g0-{tag}-{w}"
            subprocess.run([sys.executable, str(script), str(config), str(seed_file), str(d), "--hmm-version", hmm,
                            "--smoke", "--world", w, *extra], check=True, capture_output=True, env=env)
            dirs[tag] = d
        files = sorted(p.relative_to(dirs["old"]) for p in dirs["old"].rglob("*") if p.is_file())
        same = files == sorted(p.relative_to(dirs["new"]) for p in dirs["new"].rglob("*") if p.is_file())
        same = same and all((dirs["old"] / f).read_bytes() == (dirs["new"] / f).read_bytes() for f in files)
        all_same &= same
    chk(all_same and len(files) > 5, f"G0: the {len(worlds)} earlier worlds are byte for byte the copied generator's")
    other = tmp / "g0-neg"
    seed2 = tmp / "SEED.g0b"
    seed2.write_text("8\n", encoding="utf-8")
    subprocess.run([sys.executable, str(HERE / "gen_sessions.py"), str(config), str(seed2), str(other), "--hmm-version", hmm,
                    "--smoke", "--world", "v1"], check=True, capture_output=True, env=env)
    chk((other / "sessions.json").read_bytes() != (tmp / "g0-old-v1" / "sessions.json").read_bytes()
        or (other / "ndjson" / "P000.ndjson").read_bytes() != (tmp / "g0-old-v1" / "ndjson" / "P000.ndjson").read_bytes(),
        "G0: another seed writes other sessions (negative control)")


def person_sessions(cfg: dict, world: str, icc: float, k: float | None, ids: range, dur_s: int = SHORT_S) -> list:
    return [gs.person_session(TEST_SEED, cfg, world, icc, k, i, dur_s) for i in ids]


def test_g1(chk, cfg: dict) -> None:
    """G1: the segment sequence and the labels are the same for every world, ICC and k at one seed; z and eps too."""
    ids = range(0, 12)
    combos = [("person-m", 0.494, None), ("person-m", 0.679, None), ("person-r", 0.494, 0.01), ("person-r", 0.494, 0.1),
              ("person-r", 0.679, 0.01), ("person-r", 0.679, 0.1), ("person-r", 0.679, 1.0)]
    sigs = []
    for w, icc, k in combos:
        sess = person_sessions(cfg, w, icc, k, ids)
        sigs.append([(seg_signature(s), gs.seg_labels(s, SHORT_S).tobytes()) for s, _ in sess])
    chk(all(x == sigs[0] for x in sigs), "G1: 4 worlds/ICCs and 3 values of k: the same segments and L300 labels")
    # the manifests' latent values come from the same z and eps in every world (computed here from the raw streams)
    sb = cfg["person"]["sigma_b"]
    ok, by_k = True, {}
    for icc in (0.494, 0.679):
        sw = sb * math.sqrt((1 - icc) / icc)
        st_ = math.sqrt(sb * sb + sw * sw)
        for i in range(12):
            p, sl = divmod(i, 6)
            z = gs.derive_rng(TEST_SEED, "pz", p).standard_normal(4)
            e = gs.derive_rng(TEST_SEED, "pe", p, sl).standard_normal(4)
            lm = gs.person_session(TEST_SEED, cfg, "person-m", icc, None, i, SHORT_S)[1]
            ok &= abs(lm["m_log"] - (sb * z[0] + sw * e[0])) < 1e-12
            for k in (0.01, 1.0):
                lr = gs.person_session(TEST_SEED, cfg, "person-r", icc, k, i, SHORT_S)[1]
                by_k.setdefault((icc, i), []).append(lr)
                for j in (1, 2, 3):
                    ok &= abs(lr[f"x{j}"] - (math.sqrt(icc) * z[j] + math.sqrt(1 - icc) * e[j])) < 1e-12
                ok &= abs(lr["speed_log"] - st_ * e[0]) < 1e-12
    chk(ok, "G1: the manifests' m_log, x1-x3 and speed_log come from the same z and eps (ICC 0.494 and 0.679)")
    keys_ = ("x1", "x2", "x3", "speed_log")
    chk(all(all(v[0][q] == v[1][q] for q in keys_) for v in by_k.values()), "G1: person-r's latent values do not depend on k")
    other = [(seg_signature(s), gs.seg_labels(s, SHORT_S).tobytes())
             for s in (gs.person_session(TEST_SEED + 1, cfg, "person-m", 0.494, None, i, SHORT_S)[0] for i in ids)]
    chk(other != sigs[0], "G1: another seed draws other sequences (negative control)")
    # the keys do change with k (so the check above is not vacuous)
    a = gs.person_session(TEST_SEED, cfg, "person-r", 0.494, 0.01, 0, SHORT_S)[0]
    b = gs.person_session(TEST_SEED, cfg, "person-r", 0.494, 1.0, 0, SHORT_S)[0]
    chk(gs.assemble(a)[0].tolist() != gs.assemble(b)[0].tolist(), "G1: the key times do depend on k (negative control)")


def icc_of(x: np.ndarray) -> float:
    """The one-way ANOVA estimate of the between-person share (x: persons x sessions)."""
    P, S = x.shape
    gm = x.mean()
    msb = S * ((x.mean(axis=1) - gm) ** 2).sum() / (P - 1)
    msw = ((x - x.mean(axis=1, keepdims=True)) ** 2).sum() / (P * (S - 1))
    vb = (msb - msw) / S
    return float(vb / (vb + msw))


def test_g2(chk, cfg: dict) -> None:
    """G2: the mixing gives the ICC, and the person-m shift has the total SD sigma_t."""
    n_p, S = 4000, 6
    zs = np.empty((n_p, 4))
    es = np.empty((n_p, S, 4))
    for p in range(n_p):
        zs[p], es[p] = gs.raw_latents(TEST_SEED, p, S)
    ok, worst = True, 0.0
    for icc in (0.2, 0.494, 0.679):
        for j in (1, 2, 3):
            x = gs.mix(zs[:, j][:, None], es[:, :, j], icc)
            d = abs(icc_of(x) - icc)
            worst = max(worst, d)
            ok &= d < 0.02
    chk(ok, f"G2: x's between-person share equals the ICC within 0.02 (largest gap {worst:.4f}; ICC 0.2, 0.494, 0.679)")
    ok2, w2 = True, 0.0
    for icc in (0.494, 0.679):
        m = np.array([[gs.session_latents(cfg, "person-m", icc, 0.0, zs[p], es[p, s])[1]["m_log"] for s in range(S)]
                      for p in range(0, n_p, 4)])
        sd_t = gs.sigmas(cfg, icc)[2]
        w2 = max(w2, abs(m.std() - sd_t))
        ok2 &= abs(m.std() - sd_t) < 0.01 and abs(icc_of(m) - icc) < 0.03
    chk(ok2, f"G2: person-m's shift has the total SD sigma_t within 0.01 (gap {w2:.4f}) and the ICC (1000 persons)")
    chk(abs(gs.sigmas(cfg, 0.494)[2] - 0.7626) < 1e-3 and abs(gs.sigmas(cfg, 0.494)[1] - 0.5425) < 1e-3
        and abs(gs.sigmas(cfg, 0.679)[1] - 0.369) < 1e-3, "G2: sigma_w 0.543 / 0.369 and sigma_t 0.763 at ICC 0.494 / 0.679")


class ConstSpeed:
    def __init__(self, z: float):
        self.z = lambda tau: z


def reference_session(cfg: dict, seed: int, i: int, shift: float, dur_s: int) -> tuple:
    """The same session drawn by the copied gen_typing with a constant Speed: what person-r at k = 0 (shift = sigma_t
    eps0) and person-m (shift = m) must write."""
    pc = gs.person_cfg(cfg)
    fin = cfg["session"]["final_flow_s"] * 1000
    seq = gs.draw_sequence(gs.seq_rng(seed, i), dur_s * 1000 - fin, pc)
    segs = []
    for n, (kind, full, used) in enumerate(seq):
        if kind in gs.TYPING:
            seg = gs.gen_typing(gs.keys_rng(seed, i, n), kind, full, pc, ConstSpeed(shift), 0)
            seg = gs.truncate(seg, used) if used < full else seg
        else:
            seg = gs.Segment(kind, used)
        segs.append(seg)
    segs.append(gs.gen_typing(gs.keys_rng(seed, i, "final"), "FLOW", fin, pc, ConstSpeed(shift), 0))
    return gs.assemble(segs)


def indep_shift(cfg: dict, world: str, icc: float, i: int) -> float:
    """The session's speed shift computed here from the raw streams, not from gen_sessions' own functions."""
    sb = cfg["person"]["sigma_b"]
    sw = sb * math.sqrt((1 - icc) / icc)
    p, sl = divmod(i, 6)
    z = gs.derive_rng(TEST_SEED, "pz", p).standard_normal(4)
    e = gs.derive_rng(TEST_SEED, "pe", p, sl).standard_normal(4)
    return math.sqrt(sb * sb + sw * sw) * float(e[0]) if world == "person-r" else sb * float(z[0]) + sw * float(e[0])


def test_g3(chk, cfg: dict) -> None:
    """G3: person-r at k = 0 and person-m are the "constant shift per session, no type" build, byte for byte."""
    same_r, same_m, sep = True, True, False
    for icc in (0.494, 0.679):
        for i in (0, 1, 7, 13):
            segs, lat = gs.person_session(TEST_SEED, cfg, "person-r", icc, 0.0, i, SHORT_S)
            ref = reference_session(cfg, TEST_SEED, i, indep_shift(cfg, "person-r", icc, i), SHORT_S)
            got = gs.assemble(segs)
            same_r &= all(np.array_equal(a, b) for a, b in zip(got[:3], ref[:3])) and got[3] == ref[3]
            segs, lat = gs.person_session(TEST_SEED, cfg, "person-m", icc, None, i, SHORT_S)
            ref = reference_session(cfg, TEST_SEED, i, indep_shift(cfg, "person-m", icc, i), SHORT_S)
            got = gs.assemble(segs)
            same_m &= all(np.array_equal(a, b) for a, b in zip(got[:3], ref[:3])) and got[3] == ref[3]
            segs, lat = gs.person_session(TEST_SEED, cfg, "person-r", icc, 0.3, i, SHORT_S)
            sep |= not np.array_equal(gs.assemble(segs)[0], reference_session(cfg, TEST_SEED, i, indep_shift(cfg, "person-r", icc, i), SHORT_S)[0])
    chk(same_r, "G3: person-r at k = 0 equals the constant-shift build (the copied gen_typing) byte for byte")
    chk(same_m, "G3: person-m equals the constant-shift build byte for byte")
    chk(sep, "G3: person-r at k = 0.3 differs from it (negative control)")


def collect_normal(cfg: dict, mods: gs.Mods, dur_ms: int = 25_000_000, seed: int = 2) -> np.ndarray:
    """The drawn log intervals of ordinary bursts (with the burst number)."""
    col: list = []
    gs.gen_typing_person(gs.derive_rng(seed, "g4n"), "FLOW", dur_ms, gs.person_cfg(cfg), mods, collect=col)
    return np.array(col)


def collect_burst(cfg: dict, mods: gs.Mods, kind: str = "FLOW", dur_ms: int = 16_000_000, seed: int = 1) -> np.ndarray:
    """The drawn log intervals of one very long burst (design 3.7 G4: a made-up burst of about 10^5 intervals; a real burst
    ends on a long interval, which would bias the pooled draws)."""
    pc = gs.person_cfg(cfg)
    pc["segments"][kind]["burst_dur_min_s"] = pc["segments"][kind]["burst_dur_max_s"] = 1.0e7
    col: list = []
    gs.gen_typing_person(gs.derive_rng(seed, "g4", kind), kind, dur_ms, pc, mods, collect=col)
    return np.array(col)


def test_g4(chk, cfg: dict) -> None:
    """G4: dimensions 1 and 3 do not move the median of the log interval; the AR(1) keeps the SD and has the lag-1
    correlation tanh(s3); dimension 2 keeps the geometric mean of the burst length and the pause median."""
    pc = gs.person_cfg(cfg)
    p = pc["segments"]["FLOW"]
    mu0 = math.log(p["flight_median_ms"])
    ok, info = True, []
    for s1 in (1.0, -1.0):
        c = collect_burst(cfg, gs.Mods(s1=s1))
        d = abs(float(np.median(c[:, 0])) - mu0)
        sdr = float(np.std(c[:, 0])) / (p["flight_sigma"] * math.exp(s1))
        ok &= d < 0.01 and abs(sdr - 1) < 0.02
        info.append(f"s1={s1:+.0f} median gap {d:.4f} sd ratio {sdr:.3f}")
    chk(ok, f"G4: dimension 1 keeps the log median (within 0.01) and widens the SD as exp(s1): {'; '.join(info)}")
    ok, info = True, []
    for s3 in (1.0, -1.0):
        c = collect_burst(cfg, gs.Mods(s3=s3))
        d = abs(float(np.median(c[:, 0])) - mu0)
        sdr = float(np.std(c[:, 0])) / p["flight_sigma"]
        same = c[1:, 1] == c[:-1, 1]
        r = float(np.corrcoef(c[1:, 0][same], c[:-1, 0][same])[0, 1])
        ok &= d < 0.01 and abs(sdr - 1) < 0.02 and abs(r - math.tanh(s3)) < 0.01
        info.append(f"s3={s3:+.0f} median gap {d:.4f} sd ratio {sdr:.3f} lag-1 {r:+.3f} (want {math.tanh(s3):+.3f})")
    chk(ok, f"G4: dimension 3 (AR(1)) keeps the median and the SD, lag-1 correlation tanh(s3): {'; '.join(info)}")
    ok = True
    for s2 in (1.0, -1.0, 0.0):
        bm, gm = gs.dim2_scales(s2)
        ok &= abs(bm * gm - 1.0) < 1e-12 and abs(math.sqrt((p["burst_dur_min_s"] * bm) * (p["gap_median_ms"] * gm)
                                                          / (p["burst_dur_min_s"] * p["gap_median_ms"])) - 1) < 1e-12
    c = [len(gs.gen_typing_person(gs.derive_rng(1, "g4b", s2), "FLOW", 6_000_000, pc, gs.Mods(s2=s2)).presses)
         for s2 in (1.5, -1.5)]
    chk(ok and c[0] != c[1], "G4: dimension 2 keeps the geometric mean of burst length and pause median; it does change the typing")

    def dim2(s2):
        tr: list = []
        gs.gen_typing_person(gs.derive_rng(3, "g4c", 1), "FLOW", 40_000_000, pc, gs.Mods(s2=s2), trace=tr)
        a = np.array(tr)
        return float(a[:, 0].mean()), float(np.median(a[:, 1])), float(a[0, 2])

    b0, g0, c0 = dim2(0.0)
    ok = True
    for s2 in (1.5, -1.5):
        b1, g1, c1 = dim2(s2)
        ok &= (abs(b1 / b0 / math.exp(s2 / 2) - 1) < 0.05 and abs(g1 / g0 / math.exp(-s2 / 2) - 1) < 0.05
               and abs(c1 / c0 / math.exp(-s2 / 2) - 1) < 1e-9)
    chk(ok, "G4: dimension 2 in the generated draws: burst length x exp(+s2/2), pause median and cap x exp(-s2/2) (s2 = +-1.5)")
    cn = collect_normal(cfg, gs.Mods(s3=1.0))
    nb, x = cn[:, 1], cn[:, 0]
    cross = nb[1:] != nb[:-1]
    within = ~cross
    r_cross = float(np.corrcoef(x[1:][cross], x[:-1][cross])[0, 1])
    r_in = float(np.corrcoef(x[1:][within], x[:-1][within])[0, 1])
    chk(abs(r_cross) < 0.05 and abs(r_in - math.tanh(1.0)) < 0.03,
        f"G4: the AR(1) is redrawn at each burst start (lag-1 across a burst boundary {r_cross:+.3f}, within {r_in:+.3f})")


def test_g5(chk, cfg: dict) -> None:
    """G5: person-r's speed shift does not read the person's z0."""
    s0 = gs.sigmas(cfg, 0.494)[2]
    z = np.array([1.0, 0.2, -0.3, 0.4])
    e = np.array([0.7, 0.1, 0.2, 0.3])
    a = gs.session_latents(cfg, "person-r", 0.494, 0.3, z, e)[0].shift
    z2 = z.copy()
    z2[0] = -2.5
    b = gs.session_latents(cfg, "person-r", 0.494, 0.3, z2, e)[0].shift
    chk(a == b and abs(a - s0 * e[0]) < 1e-15, "G5: person-r's speed shift is sigma_t eps0 whatever z0 is")
    src = inspect.getsource(gs.r_speed)
    chk("z0" not in src.split('"""')[-1], "G5: r_speed's body does not read z0 (the reading record)")
    m1 = gs.session_latents(cfg, "person-m", 0.494, 0.0, z, e)[0].shift
    m2 = gs.session_latents(cfg, "person-m", 0.494, 0.0, z2, e)[0].shift
    chk(m1 != m2, "G5: person-m's shift does read z0 (negative control)")


# ---------------------------------------------------------------------------
# R1 and (5)
# ---------------------------------------------------------------------------

def test_r1(chk) -> None:
    """R1: the summaries read the rows' features and session index only; the stage's person controls read the session's
    name only (not the labels' content except q, not the features)."""
    rng = np.random.default_rng(3)
    F, G = rng.normal(size=(60, 4)), np.repeat(np.arange(12), 5)
    inp = pe.SummaryInput(F, G)
    try:
        m, s = pe.summarize(inp, 12)
        good = (inp.read == {"F", "G"} and m.shape == (12, 4) and np.allclose(m[0], F[:5].mean(0))
                and np.allclose(s[0], F[:5].std(0)))
    except KeyError:
        good = False
    chk(good, "R1: summarize reads F and G only (a read of anything else fails this check) and gives each session's mean and SD")
    try:
        pe.SummaryInput(F, G)["person"]
        closed = False
    except KeyError:
        closed = True
    chk(closed, "R1: the summary input refuses a person number")
    body = inspect.getsource(pe.summarize)
    chk(all(w not in body for w in ("person", "manifest", "m_log", "speed_log", "x1")),
        "R1: summarize's source names no person, manifest or latent value")
    body = inspect.getsource(pe.raw_features)
    chk(all(w not in body for w in ("person", "manifest", "m_log", "speed_log", "x1")),
        "R1: raw_features' source names no person, manifest or latent value")
    inp = pe.SummaryInput(F, G)
    try:
        pe.summarize(inp, 12)
        again = inp.read <= {"F", "G"}
    except KeyError:
        again = False
    chk(again, "R1: summarize reads nothing outside F and G")


def test_r1_stage(chk, tmp: Path) -> None:
    """R1 through run_stage: the stage names (candidates, controls) give the same windows whatever latent values the
    manifest entries carry (the path the run uses passes ms, which holds the latents)."""
    w = tmp / "r1work"
    (w / "labels").mkdir(parents=True, exist_ok=True)
    (w / "feat").mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(17)
    ms_a, ms_b = [], []
    for i in range(3):
        sid, dur = f"P{i:03d}", 600
        t = np.sort(rng.choice(dur * 1000, 1500, replace=False)).astype(np.int64)
        seg = np.repeat(rng.integers(0, 5, size=dur // 60), 60).astype(np.int8)
        np.savez_compressed(w / "labels" / f"{sid}.npz", seg=seg, presses_ms=t, duration_s=np.int64(dur), start_ms=np.int64(0))
        feat = {c: rng.uniform(0, 1, dur) for c in ("f1", "f3", "f4", "f5", "f6", "p_stuck", "keys")}
        np.savez_compressed(w / "feat" / f"{sid}.npz", **feat)
        base = {"sid": sid, "set": "P", "key_seed": 1000 + i, "person": 0, "slot": i}
        ms_a.append({**base, "m_log": 0.1 * i, "x1": 1.0, "speed_log": 0.3})
        ms_b.append({**base, "m_log": -5.0 + i, "x1": -2.0, "speed_log": 9.9})
    specs = [("d", "D-run-hold-sec", None), ("s", "S-raw-hold-sec", None), ("id", "PC1-id", None),
             ("pp", "PCp-D-run-hold-sec", 0.3), ("pz", "PC0-id-S-raw-hold-sec", 0.3), ("pe", "PCps-S-raw-hold-sec", 0.3)]
    fa = ck.run_stage(specs, ms_a, w, 5, 1)
    fb = ck.run_stage(specs, ms_b, w, 5, 1)
    chk(all(np.array_equal(fa[k], fb[k]) for k in fa),
        "R1: run_stage's windows (candidates and controls) do not change with the manifest's latent values")
    src = inspect.getsource(ck._stage_task) + inspect.getsource(st.load_session) + inspect.getsource(st.person_series)
    chk(all(wd not in src for wd in ("m_log", "speed_log", "x1", '["person"]', '["slot"]')),
        "R1: the stage's loading and control code names no latent value, person or slot field")


def made_up_summaries(rng: np.random.Generator, n_p: int = 40, S: int = 6) -> tuple:
    person = np.repeat(np.arange(n_p), S)
    base = rng.normal(size=(n_p * S, 4))  # no person information
    own = rng.normal(size=n_p)
    pc1 = np.repeat(own, S)[:, None] + rng.normal(0, 0.05, (n_p * S, 1))
    pc0 = rng.normal(size=(n_p * S, 1))  # one value per session, tied to no person
    return person, base, pc1, pc0


def test_p1(chk) -> None:
    person = np.repeat(np.arange(40), 6)
    fop = pe.fold_of_person(TEST_SEED, 40, 5)
    fold_s = fop[person]
    a, b = np.triu_indices(240, 1)
    same = (person[a] == person[b])
    chk(int(same.sum()) == 600 and int((~same).sum()) == 28080, "P1: 240 sessions: 600 same-person and 28,080 other pairs")
    I, J = pe.eval_pairs(fold_s, 5)
    y = person[I] == person[J]
    blocks = range(0, 5 * 1128, 1128)
    chk(len(I) == 5 * 1128 and int(y.sum()) == 600 and int((~y).sum()) == 5040
        and all(len(set(fold_s[I[k:k + 1128]])) == 1 and int(y[k:k + 1128].sum()) == 120 for k in blocks),
        "P1: the validation pairs: 120 same-person and 1,008 other pairs in each of the 5 folds")
    ok, bad = True, False
    for f in range(5):
        TI, TJ, ty = pe.train_pairs(person, fold_s, f)
        ok &= int(ty.sum()) == 480 and int((1 - ty).sum()) == 17856
        val = set(np.nonzero(fop == f)[0].tolist())
        bad |= bool((set(person[TI].tolist()) | set(person[TJ].tolist())) & val)
    chk(ok, "P1: each training set holds 480 same-person and 17,856 other pairs")
    chk(not bad, "P1: no person of a validation fold is in its training pairs")


def test_p2(chk) -> None:
    """P2: the bootstrap's weighted per-fold AUC (mean of the folds) equals the same mean on the duplicated persons' pairs."""
    rng = np.random.default_rng(11)
    n_p, S = 6, 3
    person = np.repeat(np.arange(n_p), S)
    fold_p = np.array([0, 0, 0, 1, 1, 1])
    a, b = np.triu_indices(len(person), 1)
    keep = fold_p[person[a]] == fold_p[person[b]]  # pairs inside a validation fold only
    a, b = a[keep], b[keep]
    pf = fold_p[person[a]]
    score = rng.normal(size=len(a)) + 0.8 * (person[a] == person[b]) + 3.0 * pf  # the folds' scales differ
    y = (person[a] == person[b]).astype(int)
    m = np.array([2.0, 0.0, 1.0, 3.0, 1.0, 2.0])
    w = pe.pair_weights(m, person[a], person[b])
    got = pe.fold_auc(score, y, pf)(w)
    copies = [(i, c) for i in range(len(person)) for c in range(int(m[person[i]]))]
    idx = {(i, j): t for t, (i, j) in enumerate(zip(a, b))}
    per_fold = {0: ([], []), 1: ([], [])}
    for u in range(len(copies)):
        for v in range(u + 1, len(copies)):
            (i, ci), (j, cj) = copies[u], copies[v]
            if i == j or (person[i] == person[j] and ci != cj) or (min(i, j), max(i, j)) not in idx:
                continue
            t = idx[(min(i, j), max(i, j))]
            per_fold[int(pf[t])][0].append(score[t])
            per_fold[int(pf[t])][1].append(y[t])
    want = float(np.mean([ck.weighted_auc(np.array(sc), np.array(ys), np.ones(len(sc))) for sc, ys in per_fold.values()]))
    chk(abs(got - want) < 1e-12, f"P2: weighted per-fold AUC {got:.6f} equals the duplicated persons' per-fold AUC mean {want:.6f}")
    chk(np.all(pe.pair_weights(np.ones(n_p), person[a], person[b]) == 1.0), "P2: all multiplicities 1 -> unit weights")


def test_p6(chk) -> None:
    """P6: the matching AUC is the mean of the validation folds' AUCs, not the AUC of the pooled scores."""
    rng = np.random.default_rng(13)
    y = np.tile([0, 1], 200)
    pf = np.repeat(np.arange(5), 80)
    score = (y + rng.normal(0, 0.05, 400)) * 1.0 - 5.0 * pf  # perfect inside each fold, folds on other scales
    got = pe.fold_auc(score, y, pf)()
    pooled = ck.weighted_auc(score, y, np.ones(400))
    chk(got > 0.99 and pooled < 0.9, f"P6: per-fold mean {got:.3f} is not the pooled AUC {pooled:.3f}")


def test_p3(chk) -> None:
    """P3: the oracle's matching AUC on made-up normal latents equals the closed form (generation not used)."""
    from scipy.stats import f as fdist

    rng = np.random.default_rng(5)
    n = 40000
    ok, notes = True, []
    for icc in (0.494, 0.679):
        for dims in (1, 3):
            z = rng.normal(size=(n, dims))
            e = rng.normal(size=(2, n, dims))
            x1, x2 = gs.mix(z, e[0], icc), gs.mix(z, e[1], icc)
            same = pe.oracle_pair(x1, x2)
            other = pe.oracle_pair(x1, np.roll(x2, 1, axis=0))
            auc = ck.weighted_auc(np.concatenate([same, other]), np.concatenate([np.ones(n), np.zeros(n)]).astype(int),
                                  np.ones(2 * n))
            want = (2 / math.pi) * math.atan(1 / math.sqrt(1 - icc)) if dims == 1 else float(fdist.cdf(1 / (1 - icc), 3, 3))
            ok &= abs(auc - want) < 0.005
            notes.append(f"{dims}d ICC {icc}: {auc:.4f} vs {want:.4f}")
    chk(ok, "P3: the oracle AUC equals the closed form within 0.005: " + "; ".join(notes))
    chk(abs((2 / math.pi) * math.atan(1 / math.sqrt(1 - 0.494)) - 0.607) < 0.002
        and abs((2 / math.pi) * math.atan(1 / math.sqrt(1 - 0.679)) - 0.672) < 0.002, "P3: 1-d values 0.607 / 0.672 (design 3.4)")


def test_p4(chk) -> None:
    ok, overlap = True, []
    person = np.repeat(np.arange(40), 6)
    for r in range(6):
        fake, slot = pe.permute_persons(TEST_SEED, r, 240, 6)
        ok &= bool(np.all(np.bincount(fake, minlength=40) == 6)) and all(sorted(slot[fake == q]) == list(range(6))
                                                                       for q in range(40))
        a, b = np.triu_indices(240, 1)
        sf = fake[a] == fake[b]
        overlap.append(float((person[a][sf] == person[b][sf]).mean()))
    chk(ok, "P4: every fake person has exactly 6 sessions with slots 0-5")
    chk(max(overlap) < 0.08, f"P4: the fake persons are independent of the real ones (same-real share {max(overlap):.3f} < 0.08)")
    f0, _ = pe.permute_persons(TEST_SEED, 0, 240, 6)
    f1, _ = pe.permute_persons(TEST_SEED, 1, 240, 6)
    chk(not np.array_equal(f0, f1), "P4: two permutations differ")


def test_p5(chk) -> None:
    """P5: on made-up summaries PC1-id's gain is above 0.10 and PC0-id's below 0.03 (the wiring of the controls)."""
    rng = np.random.default_rng(9)
    person, base, pc1, pc0 = made_up_summaries(rng)
    mats = {"PC1-id": {"small": np.hstack([base, pc1])}, "PC0-id-X": {"small": np.hstack([base, pc0])}}
    with kinds(("lr",)):
        sc, b, pairs = pe.fit5(mats, base, person, TEST_SEED, 5, 1)
        rec, auc_b = pe.gain_records(sc, b, pairs, person, None)
    g1, g0 = rec["PC1-id"]["small/lr"]["gain"], rec["PC0-id-X"]["small/lr"]["gain"]
    chk(g1 > 0.10 and g0 < 0.03, f"P5: made-up summaries: PC1-id gain {g1:+.3f} > 0.10 and PC0-id {g0:+.3f} < 0.03")
    chk(abs(auc_b["lr"] - 0.5) < 0.06, f"P5: the base alone matches at chance ({auc_b['lr']:.3f})")


# ---------------------------------------------------------------------------
# (6)
# ---------------------------------------------------------------------------

def made_up_windows(rng: np.random.Generator, pc0_same_sign: bool, n_p: int = 40, S: int = 6, W: int = 14) -> dict:
    n_sess = n_p * S
    G = np.repeat(np.arange(n_sess), W)
    person_s = np.arange(n_sess) // S
    slot_s = np.arange(n_sess) % S
    y = (rng.random(n_sess * W) < 0.35).astype(int)
    XA = rng.normal(size=(n_sess * W, 3))
    sgn_pers = np.array([st.pers_sign(TEST_SEED, int(p), n_p) for p in person_s[G]])
    sgn_p0 = np.array([st.pc0p_sign(TEST_SEED, int(p), n_p) for p in person_s[G]])
    f1 = (0.5 + sgn_pers * (y - 0.5) + rng.normal(0, 0.1, len(y)))[:, None]
    f0 = (0.5 + sgn_p0 * (y - 0.5) + rng.normal(0, 0.1, len(y)))[:, None]
    return {"y": y, "XA": XA, "G": G, "person_s": person_s, "slot_s": slot_s, "f1": f1, "f0": f0, "n_sess": n_sess}


def test_q1(chk) -> None:
    n_p, S, W = 10, 6, 4
    person_w = np.repeat(np.arange(n_p), S * W)
    slot_w = np.tile(np.repeat(np.arange(S), W), n_p)
    ts = (0, 1, 2)
    ok = True
    for p in range(n_p):
        tr, te = pe.personal_split(person_w, slot_w, p, ts)
        ok &= bool(np.array_equal(tr, np.nonzero((person_w == p) & (slot_w <= 2))[0])
                   and np.array_equal(te, np.nonzero((person_w == p) & (slot_w >= 3))[0]))
        ok &= bool(np.all(person_w[tr] == p) and np.all(slot_w[tr] <= 2) and np.all(slot_w[te] >= 3)
                   and len(tr) == 3 * W and len(te) == 3 * W)
    chk(ok, "Q1: a person's reader learns from that person's slots 0-2 only and reads slots 3-5")
    fop = pe.fold_of_person(TEST_SEED, n_p, 5)
    fold_w = fop[person_w]
    ok = True
    for f in range(5):
        m = pe.common_train_mask(fold_w, f, slot_w)
        ok &= bool(np.all(fold_w[m] != f)) and not bool(np.any(m & (fold_w == f)))
    chk(ok, "Q1: the common reader's training windows hold no window (slots 0-2 included) of a validation person")


def test_q2(chk) -> None:
    rng = np.random.default_rng(21)
    d = made_up_windows(rng, True)
    n_p = 40
    fop = pe.fold_of_person(TEST_SEED, n_p, 5)
    person_w, slot_w = d["person_s"][d["G"]], d["slot_s"][d["G"]]
    Xs = {"PC1-pers": {"small": np.hstack([d["XA"], d["f1"]])}, "PC0p-X": {"small": np.hstack([d["XA"], d["f0"]])}}
    with kinds(("lr",)):
        got = pe.fit6(Xs, d["XA"], d["y"], person_w, slot_w, fop, TEST_SEED, 1, (0, 1, 2))
        M = pe.boot_counts(TEST_SEED, "q2", n_p, 200)
        rec, auc_a = pe.six_records(got, M)
    p1, p0 = rec["PC1-pers"]["small/lr"], rec["PC0p-X"]["small/lr"]
    chk(p1["gain"] > 0.10, f"Q2: PC1-pers: D {p1['gain']:+.3f} > 0.10 (delta_pers {p1['d_pers']:+.3f}, delta_comm {p1['d_comm']:+.3f})")
    chk(p0["ci95"][1] < 0.03, f"Q2: PC0p: D's upper bound {p0['ci95'][1]:+.3f} < 0.03 (D {p0['gain']:+.3f})")
    chk(p0["d_pers"] > 0.2 and p0["d_comm"] > 0.2 and abs(p0["gain"]) < 0.05,
        f"Q2: a same-direction signal: delta_pers {p0['d_pers']:+.3f} and delta_comm {p0['d_comm']:+.3f} both large, D near 0")
    chk(abs(auc_a["lr"]["pers"] - 0.5) < 0.1 and abs(auc_a["lr"]["comm"] - 0.5) < 0.1, "Q2: model A's readers are at chance")


def test_q3(chk) -> None:
    rng = np.random.default_rng(23)
    d = made_up_windows(rng, True, n_p=10, S=6, W=6)
    person_w, slot_w = d["person_s"][d["G"]], d["slot_s"][d["G"]]
    y = d["y"].copy()
    m0 = (person_w == 0) & (slot_w <= 2)
    y[m0] = 0  # person 0 has one class in the fitting slots
    fop = pe.fold_of_person(TEST_SEED, 10, 5)
    with kinds(("lr",)):
        pers, comm, left = pe.reader_aucs(np.hstack([d["XA"], d["f1"]]), y, person_w, slot_w, fop, "lr", TEST_SEED, (0, 1, 2))
    chk(left >= 1 and np.isnan(pers[0]) and np.isnan(comm[0]) and np.isfinite(pers[1:]).sum() >= 1,
        f"Q3: a person whose fitting slots hold one class is left out (left out {left}), the others are read")


# ---------------------------------------------------------------------------
# The verdict
# ---------------------------------------------------------------------------

def att(g, lo, hi):
    return {a: {"gain": g, "ci95": [lo, hi]} for a in ck.ATTACKERS}


def judge_inputs(cands: list[str], q: str):
    pre = {r: p for r, p in pe.ROLES[q]}
    attk = {pre["pc1"]: att(0.2, 0.15, 0.25)}
    for c in cands:
        attk[c] = att(0.0, -0.01, 0.02)
        attk[f"{pre['pcs']}{c}"] = att(0.05, 0.035, 0.07)
        attk[f"{pre['pc0']}{c}"] = att(0.0, -0.01, 0.02)
    nulls = {n: [{a: 0.0 for a in ck.ATTACKERS}] * 20 for n in attk}
    return attk, nulls


def test_j1(chk, cfg: dict) -> None:
    cands = ["D-run-hold-sec", "S-raw-hold-sub"]
    auc = {"hgb": 0.7, "lr": 0.7}
    ok = True
    rng = np.random.default_rng(31)
    for q in ("id", "pers"):
        for t in range(10):
            attk, nulls = judge_inputs(cands, q)
            attk[cands[0]] = att(float(rng.uniform(-0.02, 0.1)), float(rng.uniform(-0.05, 0.05)),
                                 float(rng.uniform(0.0, 0.12)))
            r = pe.judge_q(q, attk, nulls, auc, cands, cfg, False)
            old = ck.judge({pe.to_old(q, n): v for n, v in attk.items()}, {pe.to_old(q, n): v for n, v in nulls.items()},
                           auc, cands, cfg, False)
            ok &= r["verdicts"] == {pe.from_old(q, n): v for n, v in old["verdicts"].items()}
    chk(ok, "J1: judge_q equals checks.judge on the same input (names mapped in and back), 20 made-up inputs")
    chk("def judge(" not in inspect.getsource(pe), "J1: person.py does not define its own judge")
    chk(pe.judge_q.__globals__["ck"].judge is ck.judge, "J1: the judge used is checks.judge")


LIT = {"id": ("PC1-id", "PCp-", "PC0-id-"), "pers": ("PC1-pers", "PCps-", "PC0p-")}  # written out, not read from ROLES


def test_j2(chk, cfg: dict) -> None:
    cand = "D-run-hold-sec"
    auc = {"hgb": 0.7, "lr": 0.7}
    for q, (n1, npcs, npc0) in LIT.items():
        chk(dict(pe.role_prefixes(q)) == {"pc1": n1, "pcs": npcs, "pc0": npc0},
            f"J2: ({q}) the roles are PC1 = {n1}, PC-stall = {npcs}X, PC0 = {npc0}X (written out)")
        nulls_names = [n1, cand, npcs + cand, npc0 + cand]
        nulls = {n: [{a: 0.0 for a in ck.ATTACKERS}] * 20 for n in nulls_names}
        attk = {n1: att(0.2, 0.15, 0.25), cand: att(0.0, -0.01, 0.02), npcs + cand: att(0.05, 0.035, 0.07),
                npc0 + cand: att(0.0, -0.05, 0.01)}
        v = pe.judge_q(q, attk, nulls, auc, [cand], cfg, False)["verdicts"]
        chk(v[npcs + cand] == "works" and v[npc0 + cand] == "baseline_below" and v[cand] == "green" and v[n1] == "works",
            f"J2: ({q}) {npcs}X is judged as the PC-stall, {npc0}X as PC0, the candidate green")
        attk[npcs + cand] = att(0.0, -0.01, 0.02)
        attk[npc0 + cand] = att(0.04, 0.0, 0.07)
        r = pe.judge_q(q, attk, nulls, auc, [cand], cfg, False)
        chk(r["detector"][cand]["reasons"] == ["weak_person_pc", "stall_baseline"] and r["verdicts"][cand] == "undecidable",
            f"J2: ({q}) a weak {npcs}X is weak_person_pc and a high {npc0}X is stall_baseline (not the other way)")
    for lit in ("PC1-id", "PCp-", "PC0-id-", "PC1-pers", "PCps-", "PC0p-"):
        chk(f'"{lit}' in inspect.getsource(st.person_series) and f'"{lit}' in inspect.getsource(pe.run_main),
            f"J2: stage.person_series and person.run_main both use the name {lit}")
    chk(tuple(st.PERSON_NAMES) == ("PC1-id", "PCp-", "PC0-id-", "PC1-pers", "PCps-", "PC0p-"),
        "J2: stage.PERSON_NAMES are the six written-out names")


def test_j3(chk, cfg: dict) -> None:
    """J3: the without-smooth variants carry no verdict word and need no controls of their own (decisions 10)."""
    src = inspect.getsource(pe.run_main)
    chk("judge_variants" not in src and "variant_lam" not in inspect.getsource(pe) and "vnulls" not in src,
        "J3: run_main does not judge the variants and has no variant lambda or null")
    chk(pe.variant_name("D-run-hold-sec") == "D-run-hold-sec~ws" and '"without_smooth"' in src,
        "J3: the variant is reported as a description (parent and without_smooth records)")
    chk(pe.lam_key_problems([0.025, 0.05]) == [] and pe.lam_key_problems([0.1, 0.1004]) != [],
        "J3: two lambdas that print alike with three decimals are refused")


def test_j4(chk, cfg: dict) -> None:
    g = pe.pilot_gate(False, {"A": "go", "S": "go"}, "go")
    chk(not g["five"] and g["five_reason"] == "no_person_signal" and g["six"] and g["go"],
        "J4: PC-raw not working stops (5) (no_person_signal) and (6) is still run")
    g = pe.pilot_gate(False, {"A": "ceiling", "S": "go"}, "ceiling")
    chk(not g["go"], "J4: (5) and (6) both stopped -> the step does not go on")
    g = pe.pilot_gate(True, {"A": "ceiling", "S": "go"}, "go")
    chk(not g["five"] and g["five_reason"] == "ceiling" and g["six"], "J4: a ceiling at A stops (5) only")
    grid = [0.01, 0.015, 0.02, 0.03, 0.045, 0.07]
    r = pe.choose_k(grid, [0.52, 0.53, 0.55, 0.58, 0.60, 0.61], 0.75, 0.02)
    chk(r["k"] is None and r["status"] == "k_unreached", "J4: a target above the curve -> k_unreached")
    r = pe.choose_k(grid, [0.52, 0.52, 0.52, 0.80, 0.80, 0.80], 0.66, 0.02)
    chk(r["k"] is None and r["status"] == "k_unreached", "J4: a target in a jump of the curve (nearest fit more than 0.02 away) -> k_unreached")
    r = pe.choose_k(grid, [0.52, 0.55, 0.58, 0.60, 0.62, 0.64], 0.60, 0.02)
    chk(r["k"] == 0.03 and r["status"] == "ok", "J4: a reachable target picks the nearest point")
    r = pe.choose_k(grid, [0.52, 0.60, 0.60, 0.60, 0.62, 0.64], 0.60, 0.02)
    chk(r["k"] == 0.015, "J4: the same distance picks the smaller k")
    r = pe.choose_k(grid, [0.52, 0.58, 0.55, 0.60, 0.62, 0.64], 0.565, 0.02)
    chk(r["status"] == "ok" and abs(r["fit"][1][1] - 0.565) < 1e-9, "J4: a non-monotone curve is fitted by the isotonic blocks")


def test_seed_rules(chk, cfg: dict) -> None:
    s = 20261125
    ok = (pe.run_seed("main", s, cfg) == s and pe.run_seed("pilot", s, cfg) == s + 1 and pe.run_seed("pilot-k", s, cfg) == s + 1
          and pe.run_seed("ceiling", s, cfg) == s + 1 and pe.run_seed("smoke", s, cfg) == s + 2)
    chk(ok, "seeds: main SEED, pilots / k grid / ceiling SEED + 1, smoke SEED + 2")
    chk(pe.run_seed("pilot-k", s, cfg) != pe.run_seed("main", s, cfg), "seeds: the k grid is not run at the main seed")


# ---------------------------------------------------------------------------
# The stage's person controls
# ---------------------------------------------------------------------------

def test_person_stage(chk, fake_session) -> None:
    from scipy.special import ndtr

    rng = np.random.default_rng(41)
    sess = fake_session(rng, 3600, "P013")  # person 2, slot 1
    a, r = st.series(sess, "PC1-id", 5)
    chk(np.all(a == a[0]) and abs(a[0] - float(ndtr(gs.derive_rng(5, "pcid", 2).standard_normal()))) < 1e-15
        and np.all(r == 0.5), "stage: PC1-id is Phi(z'_p) on every second, r = 0.5")
    other = st.Session("P014", sess.duration_s, sess.presses, sess.active, sess.seg, sess.feat, sess.key_seed)
    chk(st.series(other, "PC1-id", 5)[0][0] == a[0] and st.series(st.Session("P018", sess.duration_s, sess.presses,
        sess.active, sess.seg, sess.feat, sess.key_seed), "PC1-id", 5)[0][0] != a[0],
        "stage: PC1-id is one value per person (sessions of a person share it, another person's differs)")
    perm = st.Session(sess.sid, sess.duration_s, sess.presses, sess.active, rng.permutation(sess.seg), sess.feat, sess.key_seed)
    for c in ("S-raw-hold-sec", "D-run-hold-sec"):
        x = st.series(sess, f"PCp-{c}", 5, lam=1.0)
        y = st.series(perm, f"PCp-{c}", 5, lam=1.0)
        chk(np.array_equal(x[0], y[0]), f"stage: PCp-{c} at lambda 1 does not read the labels")
        x0 = st.series(sess, f"PC0-id-{c}", 5, lam=1.0)
        y0 = st.series(sess, f"PCp-{c}", 5, lam=1.0)
        chk(not np.array_equal(x0[0], y0[0]), f"stage: PC0-id-{c} (a session value) is not PCp-{c} (the person's)")
        ps = st.series(sess, f"PCps-{c}", 5, lam=1.0)
        pp = st.series(perm, f"PCps-{c}", 5, lam=1.0)
        chk(not np.array_equal(ps[0], pp[0]), f"stage: PCps-{c} at lambda 1 reads the labels (negative control)")
        p0 = st.series(sess, f"PC0p-{c}", 5, lam=0.4)
        old = st.series(sess, f"PCs-{c}", 5, lam=0.4)
        chk(np.array_equal(p0[0], old[0]) and np.array_equal(p0[1], old[1]), f"stage: PC0p-{c} is the PC-stall's picture PCs-{c} byte for byte")
    signs = [st.pers_sign(5, p, 40) for p in range(40)]
    chk(sum(s > 0 for s in signs) == 20 and sum(s < 0 for s in signs) == 20, "stage: s_p is +1 for 20 persons and -1 for 20")
    a1, _ = st.series(sess, "PC1-pers", 5)
    blk = st.pc_blocks(sess.seg, sess.duration_s, sess.key_seed, 5, 1.0)["q"]
    chk(np.allclose(a1[: len(blk) * 600][::600][: len(blk)], 0.5 + signs[2] * (blk - 0.5)) and len(a1) == sess.duration_s * 10,
        "stage: PC1-pers is 0.5 + s_p (q - 0.5) per 60 s block")


# ---------------------------------------------------------------------------
# The raw-keystroke features
# ---------------------------------------------------------------------------

def test_raw(chk, cfg: dict) -> None:
    rc = cfg["person"]["pc_raw"]
    # hand values: bursts of 4 presses 100 ms apart separated by 5000 ms, in whole ms
    pm = np.array([0, 100, 200, 300, 5300, 5400, 5500, 5600, 10600, 10700, 10800, 10900])
    f = pe.raw_features(pm, 20, rc)
    ok = abs(f[4 - 1] - 0.0) < 1e-12  # sd of log(100 ms) intervals is 0
    ok &= abs(f[1] - math.log(100.0)) < 1e-12 and abs(f[6] - 2 / 11) < 1e-12 and f[8] == 4.0 and abs(f[9] - 0.3) < 1e-12
    ok &= abs(f[7] - math.log(5000.0)) < 1e-12 and abs(f[10] - 12 / 3) < 1e-12 and abs(f[11] - 3 / 20) < 1e-12
    ok &= abs(f[0] - math.log(100.0)) < 1e-12 and abs(f[2] - math.log(100.0)) < 1e-12 and f[4] == 0.0 and f[5] == 0.0
    chk(bool(ok), f"raw: 12 hand values of three 4-press bursts ({np.round(f, 3).tolist()})")
    alt = np.concatenate([[0], np.cumsum(np.tile([100, 200], 10))])  # 20 intervals alternating 100 / 200 ms
    g = pe.raw_features(alt, 10, rc)
    logs = np.log(np.tile([100.0, 200.0], 10))
    chk(np.allclose(g[[0, 1, 2]], np.percentile(logs, [10, 50, 90])) and abs(g[3] - math.log(2) / 2) < 1e-12
        and abs(g[4] + 1.0) < 1e-12 and abs(g[5] - math.log(2)) < 1e-12,
        f"raw: alternating 100 / 200 ms: p10 p50 p90, the SD log2/2, lag-1 correlation -1 and |log ratio| log2 ({np.round(g[:6], 3).tolist()})")
    chk(np.all(np.isnan(pe.raw_features(np.array([], dtype=np.int64), 100, rc))[:10]), "raw: no press -> NaN quantities, no crash")
    rng = np.random.default_rng(2)
    t = np.sort(rng.choice(500000, 800, replace=False))
    chk(np.array_equal(pe.raw_features(t, 500, rc), pe.raw_features(rng.permutation(t), 500, rc), equal_nan=True),
        "raw: the order of the press array does not matter")


# ---------------------------------------------------------------------------
# The seams (mutants of design 3.7)
# ---------------------------------------------------------------------------

def mutant_list(cfg: dict) -> list:
    """(name, module, attribute, replacement, the test (a thunk taking chk) it must fail). Built before any is put in
    place, so each replacement holds the unmutated functions it needs."""
    orig_params = gs.interval_params
    orig_ar = gs.ar1_step
    orig_mix = gs.mix
    orig_speed = gs.r_speed
    orig_split = pe.personal_split
    orig_mask = pe.common_train_mask

    def m1(median_ms, sigma0, shift, s1):  # the mean kept, not the median
        mu, sg = orig_params(median_ms, sigma0, shift, s1)
        return mu - (sg * sg - sigma0 * sigma0) / 2.0, sg

    def m2(e_prev, rho, eta):  # sqrt(1 - rho^2) dropped
        return rho * e_prev + eta

    def m3(z, eps, icc):  # sqrt(ICC) and sqrt(1 - ICC) swapped
        return math.sqrt(1.0 - icc) * z + math.sqrt(icc) * eps

    def m4(z0, eps0, sigma_t):  # the person's own z0 mixed into the speed
        return sigma_t * (0.5 * z0 + 0.8660254037844386 * eps0)

    def m5(seed, i, cfg_, mods, dur_ms, fin_ms):  # the sequence drawn from the same stream as the keys
        rng = gs.derive_rng(seed, "seq", i)
        segs, used, state = [], 0, None
        total = dur_ms - fin_ms
        while used < total:
            table = cfg_["transitions"]["START"] if state is None else cfg_["transitions"][state]
            kinds_ = list(table)
            state = str(rng.choice(kinds_, p=[table[k] for k in kinds_]))
            p = cfg_["segments"][state]
            if state == "AWAY":
                band = int(rng.choice(len(p["bands_s"]), p=p["band_p"]))
                lo, hi = p["bands_s"][band]
                full = int(rng.uniform(lo, hi) * 1000)
            else:
                full = int(rng.uniform(p["dur_min_s"], p["dur_max_s"]) * 1000)
            d = min(full, total - used)
            seg = gs.gen_typing_person(rng, state, full, cfg_, mods) if state in gs.TYPING else gs.Segment(state, full)
            segs.append(gs.truncate(seg, d) if d < full else seg)
            used += d
        segs.append(gs.gen_typing_person(rng, "FLOW", fin_ms, cfg_, mods))
        return segs

    def m6(fold_s, f):  # the validation fold's persons are in the training pairs
        return np.arange(len(fold_s))

    def m7(m, pi, pj):  # sessions resampled, not persons: a same-person pair counts m_p^2
        return m[pi] * m[pj]

    def m8(seed, r, n_sess, slots):  # the 6 sessions of a fake person not kept
        rng = gs.derive_rng(seed, "perm", r)
        return rng.integers(0, n_sess // slots, n_sess), rng.integers(0, slots, n_sess)

    def m9(person_w, slot_w, p, train_slots):  # the person's reader fitted on slots 3-5
        return orig_split(person_w, slot_w, p, (3, 4, 5))

    def m10(fold_w, f, slot_w):  # the validation person's slots 0-2 in the common reader's training
        return orig_mask(fold_w, f, slot_w) | (slot_w <= 2)

    def m11(seed, p, n_persons=40):  # PC0p with a person-specific direction
        return st.pers_sign(seed, p, n_persons)

    def m12(inp, n_sess):  # the summary reads the person number
        inp["person"]
        return orig_summ(inp, n_sess)

    orig_summ = pe.summarize
    orig_dim2 = gs.dim2_scales

    def m15(q):  # PC-stall and PC0 roles swapped
        d = dict(pe.ROLES[q])
        d["pcs"], d["pc0"] = d["pc0"], d["pcs"]
        return d

    def m16(s2):  # the factors put on the wrong things
        a, b = orig_dim2(s2)
        return b, a

    def m17(e_prev):  # the AR(1) carried across bursts
        return e_prev

    def m13(mode, base_seed, cfg_):  # the k grid at the main run's seed
        return base_seed if mode == "pilot-k" else base_seed + int(cfg_["person"]["seed_offsets"][pe.SEED_MODE[mode]])

    def m18(score, y, pf):  # the folds' scores pooled
        return pe.FoldAuc(score, y, np.zeros_like(pf))

    def m19(v):  # no cut
        return v

    T = lambda f, *a: (lambda chk: f(chk, *a))
    return [
        ("1 dimension 1 keeps the mean, not the median", gs, "interval_params", m1, T(test_g4, cfg)),
        ("2 AR(1) without sqrt(1 - rho^2)", gs, "ar1_step", m2, T(test_g4, cfg)),
        ("3 sqrt(ICC) and sqrt(1 - ICC) swapped", gs, "mix", m3, T(test_g2, cfg)),
        ("4 person-r's speed mixes in z0", gs, "r_speed", m4, lambda chk: (test_g5(chk, cfg), test_g3(chk, cfg))),
        ("5 the sequence drawn from the keys' stream", gs, "person_segments", m5, T(test_g1, cfg)),
        ("6 the validation persons in the pair training", pe, "train_sessions", m6, lambda chk: test_p1(chk)),
        ("7 the bootstrap over sessions", pe, "pair_weights", m7, lambda chk: test_p2(chk)),
        ("8 a permutation that does not keep 6 sessions", pe, "permute_persons", m8, lambda chk: test_p4(chk)),
        ("9 the person's reader fitted on slots 3-5", pe, "personal_split", m9, lambda chk: test_q1(chk)),
        ("10 the common reader trained on a validation person's slots 0-2", pe, "common_train_mask", m10,
         lambda chk: test_q1(chk)),
        ("11 PC0p with a sign per person", st, "pc0p_sign", m11, lambda chk: test_q2(chk)),
        ("12 the summary reads the person number", pe, "summarize", m12, lambda chk: test_r1(chk)),
        ("13 the k grid at the main seed", pe, "run_seed", m13, T(test_seed_rules, cfg)),
        ("15 the PC-stall and PC0 roles swapped", pe, "role_prefixes", m15, T(test_j2, cfg)),
        ("16 dimension 2's factors on the wrong things", gs, "dim2_scales", m16, T(test_g4, cfg)),
        ("17 the AR(1) not redrawn at a burst start", gs, "ar1_reset", m17, T(test_g4, cfg)),
        ("18 the validation folds' scores pooled", pe, "fold_auc", m18, lambda chk: (test_p2(chk), test_p6(chk))),
        ("19 the type factors not cut", gs, "clip_log_scale", m19, T(test_clip, cfg)),
    ]


def test_records(chk, cfg: dict, tmp: Path) -> None:
    """Fail closed: a later mode refuses a missing, foreign or inconsistent record."""
    d = tmp / "rec" / "results" / "m049"
    (d / "ceiling").mkdir(parents=True, exist_ok=True)
    base = 20261125

    def stops(fn, *a) -> bool:
        try:
            fn(*a)
            return False
        except SystemExit:
            return True

    chk(stops(pe.require_ceiling, cfg, base, "m049", d), "records: no ceiling.json -> the run stops")
    good = {"step": "m049", "seed": pe.run_seed("ceiling", base, cfg), "config_fingerprint": pe.cfg_fingerprint(cfg),
            "code_fingerprint": pe.code_fingerprint(), "k": None, "gate": {"five": True, "six": True, "go": True}}
    f = d / "ceiling" / "ceiling.json"
    f.write_text(json.dumps(good), encoding="utf-8")
    chk(not stops(pe.require_ceiling, cfg, base, "m049", d), "records: a matching ceiling.json is accepted")
    for key, val in (("seed", 1), ("step", "m068"), ("config_fingerprint", "x"), ("code_fingerprint", "x"), ("k", 0.5)):
        f.write_text(json.dumps({**good, key: val}), encoding="utf-8")
        chk(stops(pe.require_ceiling, cfg, base, "m049", d), f"records: a ceiling.json with another {key} -> the run stops")
    f.write_text(json.dumps({k: v for k, v in good.items() if k != "gate"}), encoding="utf-8")
    chk(stops(pe.require_ceiling, cfg, base, "m049", d), "records: a ceiling.json without a gate -> the run stops")
    gate = {"five": True, "six": True}
    pilot = {"five": {"A": {"stop": None, "lam": {"c": 0.1}}, "S": {"stop": "ceiling"}}, "six": {"stop": None, "lam": {"c": 0.05}}}
    ok_cfg = ({"A": {"c": 0.1}}, {"c": 0.05})
    chk(pe.lam_problems(gate, pilot, *ok_cfg) == [], "records: lambdas equal to the pilot's (S stopped) -> no problem")
    chk(pe.lam_problems(gate, pilot, {}, {"c": 0.05}) != [], "records: apply-pilot not run for (5) -> a problem")
    chk(pe.lam_problems(gate, pilot, {"A": {"c": 0.1}}, None) != [], "records: apply-pilot not run for (6) -> a problem")
    chk(pe.lam_problems(gate, pilot, {"A": {"c": 0.2}}, {"c": 0.05}) != [], "records: a lambda that is not the pilot's -> a problem")
    chk(pe.lam_problems({"five": False, "six": True}, pilot, *ok_cfg) != [], "records: the gate stops (5) but the pilot ran it -> a problem")
    chk(pe.lam_problems(gate, {"five": {}, "six": pilot["six"]}, *ok_cfg) != [], "records: the gate runs (5) but the pilot has none -> a problem")
    w = tmp / "rec" / "work"
    w.mkdir(parents=True, exist_ok=True)
    (w / "world.json").write_text(json.dumps({"world": "person-m", "icc": 0.494, "k": None, "seed": 5, "mode": "main"}),
                                  encoding="utf-8")
    chk(not stops(pe.check_world, w, cfg, "m049", "main", 5) and stops(pe.check_world, w, cfg, "m068", "main", 5),
        "records: world.json must be the step's world and ICC")
    chk(stops(pe.check_world, w, cfg, "m049", "smoke", 5) and stops(pe.check_world, w, cfg, "m049", "main", 6),
        "records: world.json must be made for this mode and seed")
    good_summary = {"five": {"A": {"judge": {"maxima": {"PC1-id": {"gain_max": 0.4, "upper_max": 0.5},
                                                        "PC0-id-X": {"gain_max": 0.0, "upper_max": 0.01}}}}}, "six": {}}
    chk(pe.wiring_problems(good_summary) == [], "wiring: PC1-id above 0.10 and PC0-id below 0.03 -> no problem")
    bad = json.loads(json.dumps(good_summary))
    bad["five"]["A"]["judge"]["maxima"]["PC1-id"]["gain_max"] = 0.05
    bad["five"]["A"]["judge"]["maxima"]["PC0-id-X"]["upper_max"] = 0.05
    chk(len(pe.wiring_problems(bad)) == 2, "wiring: a weak PC1-id and a high PC0-id are both reported")


def test_clip(chk, cfg: dict) -> None:
    """The type dimensions' log factors are cut to [-1.5, 1.5]; k is at most 1; k = 1 with extreme x runs to the end."""
    z = np.array([0.0, 6.0, -6.0, 6.0])
    e = np.array([0.0, 6.0, -6.0, 6.0])
    mods, lat = gs.session_latents(cfg, "person-r", 0.494, 1.0, z, e)
    chk(mods.s1 == gs.LOG_SCALE_MAX and mods.s2 == -gs.LOG_SCALE_MAX and mods.s3 == gs.LOG_SCALE_MAX
        and lat["clipped"] == [True, True, True], "clip: k h x = +-8.5 is cut to +-1.5 and recorded as clipped")
    mods, lat = gs.session_latents(cfg, "person-r", 0.494, 0.1, z * 0.1, e * 0.1)
    chk(lat["clipped"] == [False, False, False] and abs(mods.s1) < 1.5, "clip: small values are not cut")
    chk(gs.K_MAX == 1.0, "clip: k is at most 1.0")
    try:
        gs.person_world_args("person-r", 0.494, 1.5)
        refused = False
    except ValueError:
        refused = True
    chk(refused and gs.person_world_args("person-r", 0.494, 1.0)["k"] == 1.0, "clip: --k above 1.0 is refused")
    ok = True
    for sgn in (1.0, -1.0):
        for dims in ((6, 6, 6), (6, -6, 6), (-6, 6, -6)):
            zz = np.array([0.0, *[sgn * d for d in dims]])
            mods, _ = gs.session_latents(cfg, "person-r", 0.494, 1.0, zz, zz)
            segs = gs.person_segments(TEST_SEED, 0, gs.person_cfg(cfg), mods, 1800 * 1000, 60 * 1000)
            t = gs.assemble(segs)[0]
            ok &= bool(len(t) > 100 and np.all(np.isfinite(t)) and np.all(np.diff(t) >= 0))
    chk(ok, "clip: k = 1.0 with extreme x draws a finite, ordered session to the end (6 cases)")


def test_speed_only(chk, cfg: dict) -> None:
    """In person-r a person's speed shift alone does not identify the person (made-up draws, no generation of keys)."""
    n_p, S = 200, 6

    def lat(world: str, p: int, sl: int) -> dict:
        z, e = gs.raw_latents(TEST_SEED + 1000, p, S)
        return gs.session_latents(cfg, world, 0.494, 0.5 if world == "person-r" else 0.0, z, e[sl])[1]

    person = np.repeat(np.arange(n_p), S)
    sp = np.array([[lat("person-r", p, sl)["speed_log"]] for p in range(n_p) for sl in range(S)])
    auc = pe.oracle_auc(sp, person)
    chk(abs(auc - 0.5) < 0.03, f"speed only: person-r's speed_log alone matches at chance ({auc:.3f}, within 0.5 +- 0.03)")
    spm = np.array([[lat("person-m", p, sl)["m_log"]] for p in range(n_p) for sl in range(S)])
    chk(pe.oracle_auc(spm, person) > 0.55, "speed only: person-m's m_log does identify (negative control)")
