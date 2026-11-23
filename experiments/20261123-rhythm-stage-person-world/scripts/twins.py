"""Twin sessions of the rhythm stage desk check (design 3.4 item 6).

For each P session, a twin keeps the number of presses of every second and redraws the press times inside the second
uniformly (whole ms, without repeats inside a second), keeping the order of the presses, their keys and their dwell
(press-release pairs). The twin goes through gse-replay like the original, so its F series follows its own times.
The random stream of a session is SeedSequence([seed, key_seed & 0xFFFFFFFF, 41]) (design 3.8).

The twin of P007 is written as P007 into <work>/twins/ with the original's manifest row, its labels (seg) and its
start time, so that replay_all.py and stage.load_session read it as they read the original.

The vk is read from the original NDJSON only to copy it; no instrument of the stage reads it (design 1.2).

Usage: twins.py <config.json> <seed file> <work dir> --hmm-version V
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from pathlib import Path

import numpy as np

import gen_sessions as gs

TWIN_TAG = 41


def read_keys(path: Path) -> tuple[int, np.ndarray, np.ndarray, np.ndarray]:
    """(session start ms, press times ms from the start, vks, dwells ms) of one generated NDJSON. A release is paired
    with the earliest open press of the same vk."""
    start, open_ = None, defaultdict(deque)
    presses: list[list[int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["type"] == "session_start":
            start = int(r["t"])
        elif r["type"] == "key":
            if r["press"]:
                presses.append([int(r["t"]), int(r["vk"]), -1])
                open_[int(r["vk"])].append(len(presses) - 1)
            else:
                i = open_[int(r["vk"])].popleft()
                presses[i][2] = int(r["t"]) - presses[i][0]
    assert start is not None and all(p[2] >= 0 for p in presses), path
    a = np.asarray(presses, dtype=np.int64).reshape(-1, 3)
    return start, a[:, 0] - start, a[:, 1], a[:, 2]


def redraw(times_ms: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Same count per second, uniform whole-ms times inside the second, sorted (the order of the presses is kept)."""
    sec = times_ms // 1000
    out = np.empty_like(times_ms)
    i = 0
    n = len(times_ms)
    while i < n:
        j = i
        while j < n and sec[j] == sec[i]:
            j += 1
        out[i:j] = sec[i] * 1000 + np.sort(rng.choice(1000, size=j - i, replace=False))
        i = j
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("seed_file")
    ap.add_argument("work")
    ap.add_argument("--hmm-version", required=True)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    cfg["_hmm_version"] = a.hmm_version
    seed = int(Path(a.seed_file).read_text().strip())
    work = Path(a.work)
    out = work / "twins"
    (out / "ndjson").mkdir(parents=True, exist_ok=True)
    (out / "labels").mkdir(parents=True, exist_ok=True)
    manifest = [m for m in json.loads((work / "sessions.json").read_text(encoding="utf-8")) if m["set"] == "P"]
    for m in manifest:
        sid = m["sid"]
        start, t, vks, dw = read_keys(work / "ndjson" / f"{sid}.ndjson")
        lab = np.load(work / "labels" / f"{sid}.npz")
        assert int(lab["start_ms"]) == start and np.array_equal(np.sort(lab["presses_ms"]), np.sort(t)), sid
        order = np.argsort(t, kind="stable")
        t, vks, dw = t[order], vks[order], dw[order]
        rng = np.random.default_rng(np.random.SeedSequence([seed, int(m["key_seed"]) & 0xFFFFFFFF, TWIN_TAG]))
        tt = redraw(t, rng)
        gs.write_session(out, sid, start, tt, vks, dw, int(lab["duration_s"]), lab["seg"], cfg)
    (out / "sessions.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"wrote {len(manifest)} twins into {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
