"""How long the A4 generation still needs, from the progress log and the count of finished files (no content).

The time of a writer is the difference between consecutive "writer n/500 done (s so far)" lines of one attempt (the
first writer of an attempt also carries the model load). The estimate is the median of the last --last writers times
the writers without a file. It assumes the GPU keeps running: a stop and the wait for a reboot are not in it.

    python scripts/a4_eta.py                 # prints the estimate
    python scripts/a4_eta.py --within 25     # exit 0 when the estimate is 25 h or less, 1 otherwise (2: no estimate)
"""
import argparse
import datetime
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "..")
DONE = re.compile(r"^writer (\d+)/(\d+) done \((\d+) s so far\)$")


def writer_times(lines):
    times, prev = [], None
    for ln in lines:
        if re.match(r"^\S+Z attempt \d+$", ln):
            prev = None
            continue
        m = DONE.match(ln)
        if m:
            s = int(m.group(3))
            times.append(s - prev if prev is not None else s)
            prev = s
    return times


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=os.path.join(EXP, "raw", "derived_a4_progress.log"))
    ap.add_argument("--dir", default=os.path.join(EXP, "raw", "derived", "a4"))
    ap.add_argument("--total", type=int, default=500)
    ap.add_argument("--last", type=int, default=10)
    ap.add_argument("--within", type=float, help="exit 0 when the estimate is at most this many hours")
    a = ap.parse_args()
    with open(a.log, encoding="utf-8", errors="replace") as f:
        lines = [ln.rstrip("\n") for ln in f]
    done = sum(1 for n in os.listdir(a.dir) if n.endswith(".json")) if os.path.isdir(a.dir) else 0
    times = writer_times(lines)
    tail = [ln for ln in lines if ln.strip()][-1:] or [""]
    state = "GPU not visible (waiting)" if "GPU not visible" in tail[0] else "running or between attempts"
    remaining = max(a.total - done, 0)
    if not times:
        print("done %d/%d; no writer time yet; %s" % (done, a.total, state))
        sys.exit(2 if a.within is not None else 0)
    per = statistics.median(times[-a.last:])
    hours = remaining * per / 3600
    end = datetime.datetime.now() + datetime.timedelta(hours=hours)
    print("done %d/%d; median of last %d writers %.1f min; remaining %.1f h; end about %s (local, if the GPU keeps "
          "running); %s" % (done, a.total, min(a.last, len(times)), per / 60, hours, end.strftime("%Y-%m-%d %H:%M"),
                             state))
    if a.within is not None:
        sys.exit(0 if hours <= a.within else 1)


if __name__ == "__main__":
    main()
