"""Generate synthetic keystroke sessions with stall labels (copied from EH1 round 5 of the portrait).

The only change from experiments/20261010-portrait-eh1-round5/scripts/gen_sessions.py is --world v3 and v4
(.steering/20261012-rhythm-stage-desk-check/design.md 1.6); v1 and v2 write the same sessions (selftest.py).
Graded world (.steering/20261014-rhythm-stage-graded-world/design.md 1.3): --world graded --t T copies
segments_v4 and sets only STRUGGLE's flight_median_ms and flight_sigma between v4 (t = 0) and v2 (t = 1); the
world and t are written to world.json next to sessions.json.
Confound world (.steering/20261014-rhythm-stage-speed-confound-world/design.md 1.3): --world confound --c C uses
the graded segments at t = speed_confound.base_t and draws every FLOW and STRUGGLE key interval with its log
median shifted by z(tau) = c * w(tau), where w is a session speed factor plus an Ornstein-Uhlenbeck drift drawn
from a stream of its own (Speed). Without --world confound no Speed is made and the sessions are those of the
copied generator; c = 0 writes the keys and labels of --world graded --t base_t.

Each session is a sequence of segments (FLOW, STRUGGLE, THINK, STALL_SILENT, AWAY, SLEEP).
A segment carries its own key presses relative to its start, so that sessions can share,
copy or reorder segments (sets O, J and D). The NDJSON holds only key rows (and the meta,
session_start and session_meta rows that gse-replay reads); the labels are written to a
separate file that the replay never sees.

Usage: gen_sessions.py <config.json> <SEED file> <work dir> --hmm-version V
                       [--world v1|v2|v3|v4|graded|confound] [--t T] [--c C] [--smoke] [--p-n N]
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

SEG_CODE = {"FLOW": 0, "STRUGGLE": 1, "THINK": 2, "STALL_SILENT": 3, "AWAY": 4, "SLEEP": 5}
STALL_CODES = (1, 3)
TYPING = ("FLOW", "STRUGGLE")
VK_BACKSPACE = 8
VK_SPACE = 32


@dataclass
class Segment:
    kind: str
    dur_ms: int
    # (t_ms relative, vk, dwell_ms). The dwell is drawn with the press, so a copied segment (O, D) or a
    # jittered session (J) keeps the same press-release pairs (design 1.2).
    presses: list[tuple[int, int, int]] = field(default_factory=list)


def derive_rng(seed: int, *names: object) -> np.random.Generator:
    """A generator whose stream depends only on the seed and the names."""
    digest = hashlib.sha256(("|".join(str(n) for n in names)).encode()).digest()
    words = [int.from_bytes(digest[i : i + 4], "little") for i in range(0, 16, 4)]
    return np.random.default_rng(np.random.SeedSequence([seed, *words]))


def key_seed(seed: int, *names: object) -> int:
    digest = hashlib.sha256(("key|" + "|".join(str(n) for n in names) + f"|{seed}").encode()).digest()
    return int.from_bytes(digest[:8], "little") & ((1 << 63) - 1)


def graded_segments(cfg: dict, t: float) -> dict:
    """design 1.3: segments_v4 with STRUGGLE's flight_median_ms = m4^(1-t) * m2^t and flight_sigma =
    (1-t) * s4 + t * s2, where m and s are those of segments_v4 (t = 0) and segments_v2 (t = 1). Both forms give
    the v4 and v2 values exactly at the two ends (design 1.3)."""
    if not 0.0 <= t <= 1.0:
        raise ValueError(f"t must be in [0, 1], got {t}")
    s4, s2 = cfg["segments_v4"]["STRUGGLE"], cfg["segments_v2"]["STRUGGLE"]
    seg = copy.deepcopy(cfg["segments_v4"])
    seg["STRUGGLE"]["flight_median_ms"] = s4["flight_median_ms"] ** (1.0 - t) * s2["flight_median_ms"] ** t
    seg["STRUGGLE"]["flight_sigma"] = (1.0 - t) * s4["flight_sigma"] + t * s2["flight_sigma"]
    return seg


def confound_delta(cfg: dict) -> float:
    """confound world design 1.3: the stall in log units, ln(STRUGGLE's median at base_t / FLOW's median)."""
    seg = graded_segments(cfg, cfg["speed_confound"]["base_t"])
    return math.log(seg["STRUGGLE"]["flight_median_ms"] / seg["FLOW"]["flight_median_ms"])


class Speed:
    """confound world design 1.3: z(tau) = c * w(floor(tau / 1000)) with w(k) = delta * (u + d(k)), where u ~ N(0, 1)
    is the session factor and d is a stationary unit Ornstein-Uhlenbeck series per second (d(0) ~ N(0, 1),
    d(k+1) = rho d(k) + sqrt(1 - rho^2) eps_k, rho = exp(-1 / tau_s)). u, d(0), eps_0, eps_1, ... are drawn in this
    order from derive_rng(seed, "speed", *names), apart from the streams of the segments and the keys. w does not
    depend on c, so z at 2c is exactly twice z at c (a product by 2 is exact in floating point).
    The series grows on demand, one draw per second in order, so w(k) does not depend on how far it was read: markov
    draws a whole segment before it cuts the last one at the session end, so the keys can run past duration_s."""

    def __init__(self, seed: int, names: tuple, c: float, cfg: dict, duration_s: int) -> None:
        self._r = derive_rng(seed, "speed", *names)
        self._rho = math.exp(-1.0 / cfg["speed_confound"]["tau_s"])
        self._q = math.sqrt(1.0 - self._rho * self._rho)
        self._delta = confound_delta(cfg)
        self._u = float(self._r.standard_normal())
        self._d = [float(self._r.standard_normal())]
        self.c = c
        self._grow(duration_s)

    def _grow(self, k: int) -> None:
        while len(self._d) <= k:
            self._d.append(self._rho * self._d[-1] + self._q * float(self._r.standard_normal()))

    def w(self, k: int) -> float:
        if k < 0:
            raise ValueError(f"second {k} is before the session start")
        self._grow(k)
        return self._delta * (self._u + self._d[k])

    def z(self, tau_ms: float) -> float:
        return self.c * self.w(int(tau_ms // 1000))


def draw_dwell(rng: np.random.Generator, cfg: dict) -> int:
    d, j = cfg["keys"]["dwell_ms"], cfg["keys"]["dwell_jitter_ms"]
    return int(rng.integers(d - j, d + j + 1))


def pick_vk(rng: np.random.Generator, p_bs: float, p_space: float) -> int:
    u = rng.random()
    if u < p_bs:
        return VK_BACKSPACE
    if rng.random() < p_space:
        return VK_SPACE
    return int(rng.integers(65, 91))


def gen_typing(rng: np.random.Generator, kind: str, dur_ms: int, cfg: dict, speed: Speed | None = None,
               t0_ms: int = 0) -> Segment:
    """speed (confound world design 1.3): the key interval drawn after a press at t ms of the segment has its log
    median shifted by speed.z(t0_ms + t), t0_ms being the segment's start in the session. None draws as before."""
    p = cfg["segments"][kind]
    p_space = cfg["keys"]["p_space"]
    seg = Segment(kind, dur_ms)
    t = float(rng.uniform(0, 300))
    by_duration = "burst_dur_min_s" in p  # world v2: a burst lasts a drawn time, whatever the key rate
    while t < dur_ms:
        last_vk = None
        if by_duration:
            burst_end = t + float(rng.uniform(p["burst_dur_min_s"], p["burst_dur_max_s"])) * 1000
            while t < dur_ms:
                last_vk = pick_vk(rng, p["p_backspace"], p_space)
                seg.presses.append((int(t), last_vk, draw_dwell(rng, cfg)))
                mu = np.log(p["flight_median_ms"])
                if speed is not None:
                    mu = mu + speed.z(t0_ms + t)
                nxt = t + float(rng.lognormal(mu, p["flight_sigma"]))
                if nxt >= burst_end:
                    t = burst_end  # the pause is measured from the drawn end, so slow typing does not lengthen it
                    break
                t = nxt
        else:
            n = int(rng.integers(p["burst_min"], p["burst_max"] + 1))
            for i in range(n):
                if t >= dur_ms:
                    break
                last_vk = pick_vk(rng, p["p_backspace"], p_space)
                seg.presses.append((int(t), last_vk, draw_dwell(rng, cfg)))
                if i < n - 1:
                    if speed is not None:
                        raise ValueError("the confound world needs bursts by duration (segments_v2 and later)")
                    t += float(rng.lognormal(np.log(p["flight_median_ms"]), p["flight_sigma"]))
        gap = min(float(rng.lognormal(np.log(p["gap_median_ms"]), p["gap_sigma"])), p["gap_cap_ms"])
        if (kind == "STRUGGLE" and "p_pause_after_bs" in p and last_vk == VK_BACKSPACE
                and rng.random() < p["p_pause_after_bs"]):
            gap = max(gap, p["pause_after_bs_min_ms"] + float(rng.uniform(0, p["pause_after_bs_extra_ms"])))
        t += gap
    return seg


def gen_segment(rng: np.random.Generator, kind: str, cfg: dict, speed: Speed | None = None,
                t0_ms: int = 0) -> Segment:
    p = cfg["segments"][kind]
    if kind == "AWAY":
        band = int(rng.choice(len(p["bands_s"]), p=p["band_p"]))
        lo, hi = p["bands_s"][band]
        return Segment(kind, int(rng.uniform(lo, hi) * 1000))
    dur_ms = int(rng.uniform(p["dur_min_s"], p["dur_max_s"]) * 1000)
    if kind in TYPING:
        return gen_typing(rng, kind, dur_ms, cfg, speed, t0_ms)
    return Segment(kind, dur_ms)


def truncate(seg: Segment, dur_ms: int) -> Segment:
    return Segment(seg.kind, dur_ms, [p for p in seg.presses if p[0] < dur_ms])


def markov(rng: np.random.Generator, total_ms: int, cfg: dict, start: str | None = None,
           speed: Speed | None = None, t0_ms: int = 0) -> list[Segment]:
    """t0_ms: where the first segment starts in the session (for speed only)."""
    trans = cfg["transitions"]
    segs: list[Segment] = []
    used = 0
    state = start
    while used < total_ms:
        table = trans["START"] if state is None else trans[state]
        kinds = list(table)
        state = str(rng.choice(kinds, p=[table[k] for k in kinds]))
        seg = gen_segment(rng, state, cfg, speed, t0_ms + used)
        if used + seg.dur_ms > total_ms:
            seg = truncate(seg, total_ms - used)
        segs.append(seg)
        used += seg.dur_ms
    return segs


def flow(rng: np.random.Generator, dur_ms: int, cfg: dict, speed: Speed | None = None, t0_ms: int = 0) -> Segment:
    return gen_typing(rng, "FLOW", dur_ms, cfg, speed, t0_ms)


def continuous(rng: np.random.Generator, total_ms: int, cfg: dict, speed: Speed | None = None) -> list[Segment]:
    segs: list[Segment] = []
    used = 0
    while used < total_ms:
        seg = gen_segment(rng, "FLOW", cfg, speed, used)
        if used + seg.dur_ms > total_ms:
            seg = truncate(seg, total_ms - used)
        segs.append(seg)
        used += seg.dur_ms
    return segs


def shuffle_jumps(sp: Speed, body: list[Segment], tail: Segment, perm: np.ndarray) -> dict:
    """confound world design 3.3 (h): at each boundary between consecutive segments, z of the first second of the
    next segment minus z of the last second of the one before, both at the times the segments were drawn (the
    a-order). In a they are neighbouring seconds; in b the shuffle makes the jumps."""
    starts = np.concatenate([[0], np.cumsum([s.dur_ms for s in body])]).astype(np.int64)
    first = {k: int(starts[k] // 1000) for k in range(len(body))}
    last = {k: int((starts[k + 1] - 1) // 1000) for k in range(len(body))}
    first[len(body)] = int(starts[-1] // 1000)  # the tail follows the body in both orders
    out = {}
    for role, order in (("a", list(range(len(body)))), ("b", [int(k) for k in perm])):
        seq = order + [len(body)]
        j = np.array([sp.c * (sp.w(first[y]) - sp.w(last[x])) for x, y in zip(seq[:-1], seq[1:])])
        out[role] = {"n": int(len(j)), "median_abs": float(np.median(np.abs(j))) if len(j) else 0.0,
                     "max_abs": float(np.max(np.abs(j))) if len(j) else 0.0}
    return out


def assemble(segs: list[Segment]) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Absolute press times (ms from session start), vks, dwells and the duration."""
    times: list[int] = []
    vks: list[int] = []
    dwells: list[int] = []
    t0 = 0
    for seg in segs:
        for t, vk, dw in seg.presses:
            times.append(t0 + t)
            vks.append(vk)
            dwells.append(dw)
        t0 += seg.dur_ms
    return (np.asarray(times, dtype=np.int64), np.asarray(vks, dtype=np.int16),
            np.asarray(dwells, dtype=np.int64), t0)


def seg_labels(segs: list[Segment], duration_s: int) -> np.ndarray:
    lab = np.zeros(duration_s, dtype=np.int8)
    t0 = 0
    for seg in segs:
        a = t0 // 1000
        b = min(duration_s, (t0 + seg.dur_ms) // 1000)
        lab[a:b] = SEG_CODE[seg.kind]
        t0 += seg.dur_ms
    return lab


def write_session(work: Path, sid: str, start_ms: int, times: np.ndarray, vks: np.ndarray, dwells: np.ndarray,
                  duration_s: int, labels: np.ndarray, cfg: dict) -> None:
    rows: list[tuple[int, int, int, bool]] = []
    for t, vk, dw in zip(times.tolist(), vks.tolist(), dwells.tolist()):
        rows.append((start_ms + t, 0, vk, True))
        rows.append((start_ms + t + dw, 1, vk, False))
    rows.sort(key=lambda r: (r[0], r[1]))
    meta = {
        "type": "meta",
        "session_start": start_ms,
        "hmm_version": cfg["_hmm_version"],
        "capabilities": {
            "unconditional": ["key", "session_meta", "session_start"],
            "threshold_gated": [],
            "config_gated": [],
        },
    }
    smeta = {"type": "session_meta", "track": "main", "task_kind": "argumentative", "monk_mode": False,
             "intervention_enabled": False, "condition": None, "label_pool": None, "head_id": "writing",
             "ts": start_ms}
    with open(work / "ndjson" / f"{sid}.ndjson", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(meta, separators=(",", ":")) + "\n")
        fh.write(json.dumps({"type": "session_start", "t": start_ms}, separators=(",", ":")) + "\n")
        fh.write(json.dumps(smeta, separators=(",", ":")) + "\n")
        for t, _, vk, press in rows:
            fh.write(f'{{"type":"key","t":{t},"vk":{vk},"press":{"true" if press else "false"}}}\n')
    np.savez_compressed(work / "labels" / f"{sid}.npz", seg=labels, presses_ms=times,
                        duration_s=np.int64(duration_s), start_ms=np.int64(start_ms))


def jitter(rng: np.random.Generator, times: np.ndarray, vks: np.ndarray, dwells: np.ndarray,
           j: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Move each press by a uniform +-j ms; its release moves with it (the dwell is kept)."""
    t = np.maximum(0, times + rng.integers(-j, j + 1, size=times.shape))
    order = np.argsort(t, kind="stable")
    return t[order], vks[order], dwells[order]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("seed_file")
    ap.add_argument("work")
    ap.add_argument("--hmm-version", required=True)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--world", choices=("v1", "v2", "v3", "v4", "graded", "confound"), default="v1",
                    help="v1 = frozen design 1.2; v2 = deviation: same pause structure for FLOW and STRUGGLE; "
                         "v3 = v2 with FLOW's key intervals in STRUGGLE and v1's pause after a backspace; "
                         "v4 = v2 with FLOW's key intervals in STRUGGLE (the stall shows only in corrections); "
                         "graded = between v4 (t = 0) and v2 (t = 1) in STRUGGLE's key intervals (needs --t); "
                         "confound = graded at speed_confound.base_t with a speed factor and drift of width c "
                         "(needs --c)")
    ap.add_argument("--t", type=float, default=None, help="graded world only: the step t in [0, 1]")
    ap.add_argument("--c", type=float, default=None, help="confound world only: the width c >= 0")
    ap.add_argument("--p-n", type=int, default=None,
                    help="round 2 pilot only (design 3.10): the number of P sessions; the default output is unchanged")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    cfg["_hmm_version"] = a.hmm_version
    if (a.world == "graded") != (a.t is not None):
        ap.error("--t is required with --world graded and only with it")
    if (a.world == "confound") != (a.c is not None):
        ap.error("--c is required with --world confound and only with it")
    if a.c is not None and not (math.isfinite(a.c) and a.c >= 0.0):
        ap.error(f"--c must be a finite number >= 0, got {a.c}")
    if a.world in ("v2", "v3", "v4"):
        cfg["segments"] = cfg[f"segments_{a.world}"]
    elif a.world == "graded":
        cfg["segments"] = graded_segments(cfg, a.t)
    elif a.world == "confound":
        cfg["segments"] = graded_segments(cfg, cfg["speed_confound"]["base_t"])
    seed = int(Path(a.seed_file).read_text().strip())

    def mk(names: tuple, duration_s: int) -> Speed | None:
        """confound world design 1.3: the speed series of a unit (a session or a pair); None outside the world."""
        return Speed(seed, names, a.c, cfg, duration_s) if a.world == "confound" else None

    work = Path(a.work)
    (work / "ndjson").mkdir(parents=True, exist_ok=True)
    (work / "labels").mkdir(parents=True, exist_ok=True)
    sc = cfg["session"]
    sets = cfg["sets"]
    scale = 0.05 if a.smoke else 1.0
    manifest: list[dict] = []
    counter = [0]

    def emit(sid: str, set_name: str, segs: list[Segment] | None, ks: int, extra: dict,
             presses: tuple[np.ndarray, np.ndarray, np.ndarray, int] | None = None) -> None:
        if presses is None:
            assert segs is not None
            times, vks, dwells, dur_ms = assemble(segs)
            duration_s = dur_ms // 1000
            labels = seg_labels(segs, duration_s)
        else:
            times, vks, dwells, duration_s = presses
            labels = extra.pop("_labels")
        start_ms = sc["epoch_ms"] + counter[0] * sc["session_spacing_ms"]
        counter[0] += 1
        write_session(work, sid, start_ms, times, vks, dwells, duration_s, labels, cfg)
        manifest.append({"sid": sid, "set": set_name, "duration_s": int(duration_s), "key_seed": ks, **extra})

    dur = sc["duration_s"] * 1000
    fin = sc["final_flow_s"] * 1000

    n_p = a.p_n if a.p_n is not None else max(12, int(round(sets["P"]["n"] * scale)))
    for i in range(n_p):
        r = derive_rng(seed, "P", i)
        sp = mk(("P", i), sc["duration_s"])
        segs = markov(r, dur - fin, cfg, speed=sp) + [flow(r, fin, cfg, sp, dur - fin)]
        emit(f"P{i:03d}", "P", segs, key_seed(seed, "P", i), {})

    o = sets["O"]
    n_o = max(4, int(round(o["pairs"] * scale)))
    for i in range(n_o):
        ra, rb, rs = derive_rng(seed, "Oa", i), derive_rng(seed, "Ob", i), derive_rng(seed, "Os", i)
        sp = mk(("O", i), o["prefix_s"] + o["shared_suffix_s"])  # one series per pair (confound world design 1.3)
        pre = o["prefix_s"] * 1000
        suffix = (markov(rs, o["shared_suffix_s"] * 1000 - fin, cfg, speed=sp, t0_ms=pre)
                  + [flow(rs, fin, cfg, sp, pre + o["shared_suffix_s"] * 1000 - fin)])
        a_segs = markov(ra, pre, cfg, speed=sp) + suffix
        b_segs = markov(rb, pre, cfg, speed=sp) + suffix
        ks = key_seed(seed, "O", i)
        emit(f"Oa{i:02d}", "O", a_segs, ks, {"pair": i, "role": "a"})
        emit(f"Ob{i:02d}", "O", b_segs, ks, {"pair": i, "role": "b"})
        times, vks, dwells, dur_ms = assemble(a_segs)
        jt, jv, jd = jitter(derive_rng(seed, "J", i), times, vks, dwells, sets["J"]["jitter_ms"])
        emit(f"J{i:02d}", "J", None, ks, {"pair": i, "role": "j", "_labels": seg_labels(a_segs, dur_ms // 1000)},
             (jt, jv, jd, dur_ms // 1000))

    d = sets["D_shuffled"]
    jumps: dict[str, dict] = {}
    for i in range(max(2, int(round(d["pairs"] * scale)))):
        r = derive_rng(seed, "Dsh", i)
        sp = mk(("Dsh", i), d["duration_s"])  # the b-session keeps each segment's keys as drawn in a (design 1.3)
        body = markov(r, d["duration_s"] * 1000 - fin, cfg, speed=sp)
        tail = flow(r, fin, cfg, sp, d["duration_s"] * 1000 - fin)
        perm = derive_rng(seed, "Dsh-perm", i).permutation(len(body))
        ks = key_seed(seed, "Dsh", i)
        emit(f"Dsh{i:02d}a", "D_shuffled", body + [tail], ks, {"pair": i, "role": "a"})
        emit(f"Dsh{i:02d}b", "D_shuffled", [body[k] for k in perm] + [tail], ks, {"pair": i, "role": "b"})
        if sp is not None:
            jumps[f"{i:02d}"] = shuffle_jumps(sp, body, tail, perm)
        # jitter copy of the a-session: the noise floor for the order-only ratio (design section 8)
        times, vks, dwells, dur_ms = assemble(body + [tail])
        jt, jv, jd = jitter(derive_rng(seed, "Jsh", i), times, vks, dwells, sets["J"]["jitter_ms"])
        emit(f"Jsh{i:02d}", "Jsh", None, ks, {"pair": i, "role": "j", "_labels": seg_labels(body + [tail], dur_ms // 1000)},
             (jt, jv, jd, dur_ms // 1000))

    d = sets["D_diffend"]
    for i in range(max(2, int(round(d["pairs"] * scale)))):
        rp, ra, rb = derive_rng(seed, "Dde-p", i), derive_rng(seed, "Dde-a", i), derive_rng(seed, "Dde-b", i)
        sp = mk(("Dde", i), d["shared_prefix_s"] + d["suffix_s"])  # one series per pair (design 1.3)
        pre, end = d["shared_prefix_s"] * 1000, (d["shared_prefix_s"] + d["suffix_s"]) * 1000 - fin
        prefix = markov(rp, pre, cfg, speed=sp)
        ks = key_seed(seed, "Dde", i)
        emit(f"Dde{i:02d}a", "D_diffend",
             prefix + markov(ra, d["suffix_s"] * 1000 - fin, cfg, speed=sp, t0_ms=pre) + [flow(ra, fin, cfg, sp, end)],
             ks, {"pair": i, "role": "a"})
        emit(f"Dde{i:02d}b", "D_diffend",
             prefix + markov(rb, d["suffix_s"] * 1000 - fin, cfg, speed=sp, t0_ms=pre) + [flow(rb, fin, cfg, sp, end)],
             ks, {"pair": i, "role": "b"})

    d = sets["D_noobs"]
    for i in range(d["n"] if not a.smoke else 1):
        r = derive_rng(seed, "Dno", i)
        presses = [(10_000 + 200 * k, int(r.integers(65, 91)), draw_dwell(r, cfg)) for k in range(d["keys"])]
        segs = [Segment("FLOW", 12_000, presses), Segment("AWAY", d["duration_s"] * 1000 - 12_000)]
        emit(f"Dno{i:02d}", "D_noobs", segs, key_seed(seed, "Dno", i), {})

    d = sets["D_continuous"]
    for i in range(d["n"] if not a.smoke else 1):
        r = derive_rng(seed, "Dco", i)
        sp = mk(("Dco", i), d["duration_s"])
        emit(f"Dco{i:02d}", "D_continuous", continuous(r, d["duration_s"] * 1000, cfg, sp), key_seed(seed, "Dco", i), {})

    d = sets["D_sleep"]
    for i in range(d["n"] if not a.smoke else 1):
        r = derive_rng(seed, "Dsl", i)
        sp = mk(("Dsl", i), d["duration_s"])  # the sleep advances the time of the series (design 1.3)
        before = markov(r, d["sleep_start_s"] * 1000, cfg, speed=sp)
        after_ms = d["duration_s"] * 1000 - d["sleep_start_s"] * 1000 - d["sleep_s"] * 1000
        wake = (d["sleep_start_s"] + d["sleep_s"]) * 1000
        after = (markov(r, after_ms - fin, cfg, start="AWAY", speed=sp, t0_ms=wake)
                 + [flow(r, fin, cfg, sp, wake + after_ms - fin)])
        segs = before + [Segment("SLEEP", d["sleep_s"] * 1000)] + after
        emit(f"Dsl{i:02d}", "D_sleep", segs, key_seed(seed, "Dsl", i), {})

    (work / "sessions.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    if a.world == "confound":  # confound world design 3.3 (h): described only, not judged
        (work / "speed_jumps.json").write_text(json.dumps({"c": a.c, "pairs": jumps}, indent=1), encoding="utf-8")
    world = {"world": a.world, "c": a.c} if a.world == "confound" else {"world": a.world, "t": a.t}
    (work / "world.json").write_text(json.dumps(world), encoding="utf-8")
    print(f"generated {len(manifest)} sessions into {work}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
