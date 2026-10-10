"""Run gse-replay on every synthetic session and keep the F series per second.

The replay prints the FeatSnapshot array (one row per 1 s tick) on stdout. Only the columns
that the portrait and its controls use are kept: f1 f3 f4 f5 f6 (material), p_stuck (the
positive control PC2 only) and keys. A tick that the replay did not emit stays NaN.

Usage: replay_all.py <gse-replay binary> <work dir> [--jobs N]
"""

from __future__ import annotations

import argparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

COLS = ("f1", "f3", "f4", "f5", "f6", "p_stuck", "keys")


def replay_one(binary: str, work: Path, sid: str, start_ms: int, duration_s: int) -> str:
    out = subprocess.run([binary, str(work / "ndjson" / f"{sid}.ndjson")], capture_output=True, check=False)
    if out.returncode != 0:
        raise RuntimeError(f"gse-replay failed on {sid}: exit {out.returncode}: {out.stderr.decode(errors='replace')[-400:]}")
    snaps = json.loads(out.stdout)
    arr = {c: np.full(duration_s, np.nan, dtype=np.float64) for c in COLS}
    for s in snaps:
        k = (int(s["timestamp"]) - start_ms) // 1000 - 1  # the tick at t covers [t-1 s, t) (run_replay steps before same-ms events)
        if 0 <= k < duration_s:
            for c in COLS:
                arr[c][k] = float(s[c])
    np.savez_compressed(work / "feat" / f"{sid}.npz", **arr, n_snapshots=np.int64(len(snaps)))
    return sid


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("binary")
    ap.add_argument("work")
    ap.add_argument("--jobs", type=int, default=12)
    a = ap.parse_args()
    work = Path(a.work)
    (work / "feat").mkdir(exist_ok=True)
    manifest = json.loads((work / "sessions.json").read_text(encoding="utf-8"))
    jobs = []
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for m in manifest:
            lab = np.load(work / "labels" / f"{m['sid']}.npz")
            jobs.append(ex.submit(replay_one, a.binary, work, m["sid"], int(lab["start_ms"]), int(lab["duration_s"])))
        for j in jobs:
            j.result()
    print(f"replayed {len(jobs)} sessions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
