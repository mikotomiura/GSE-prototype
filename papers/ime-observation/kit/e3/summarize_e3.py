#!/usr/bin/env python3
"""Summarise the samples of the execution-cost measurement (E3).

    python3 summarize_e3.py [LABEL=]samples.tsv [[LABEL=]samples.tsv ...]
    python3 summarize_e3.py --selftest

Each file is the output of `sample-macos.sh` or `sample-windows.sh` behind a header line. One block is
printed per file: CPU (mean, median, 95th percentile, maximum) and the slope of the resident memory in MB
per hour. Pass one file per condition (for example `idle=idle/samples.tsv working=working/samples.tsv`):
the cost is reported per condition, never as a single figure.

A run that was not measured is never reported as a low cost:
  - a file with no sample row, or whose rows are all zero (the process was never found), is `not measured`;
  - a file with fewer than --min-samples usable rows is `insufficient`: the figures are printed for
    inspection but must not be quoted as rates;
  - an empty CPU value (the first row of a run has no previous cumulative counter) is left out of the CPU
    statistics; it is never read as 0.

Exit status: 0 every file is measured, 1 a file is insufficient or not measured, 2 a usage error.
"""
from __future__ import annotations

import contextlib
import io
import math
import os
import sys
import tempfile

# kit: selftest

# Rows needed to cover eight hours at a 30-second interval is 960; half of it is the floor for a rate.
MIN_SAMPLES = 480


def parse_threads(v):
    """Thread count. `top` on macOS may print `31/1` (total/running); only the leading number is taken."""
    return int(str(v).split("/")[0] or 0)


def load(path):
    """Read a samples file. Returns (rows, skipped) where skipped holds every line that could not be read."""
    rows, skipped = [], []
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        parts = line.split("\t")
        if i == 0 and not parts[0].strip().isdigit():
            continue  # header line
        if len(parts) < 5:
            skipped.append(line)
            continue
        try:
            rows.append({
                "t": int(parts[0]),
                # An empty CPU value means "not measured"; it is kept as None and left out downstream.
                "cpu": float(parts[1]) if parts[1].strip() else None,
                "rss_kb": float(parts[2] or 0),
                "threads": parse_threads(parts[3]),
            })
        except ValueError:
            skipped.append(line)
    return rows, skipped


def percentile(sorted_values, q):
    """Percentile with linear interpolation between closest ranks (q in 0..100)."""
    n = len(sorted_values)
    if n == 0:
        return None
    if n == 1:
        return sorted_values[0]
    pos = (n - 1) * q / 100.0
    lo = int(math.floor(pos))
    hi = min(lo + 1, n - 1)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)


def slope_mb_per_h(rows):
    """Least-squares slope of the resident memory in MB per hour. None for fewer than two points."""
    pts = [(r["t"], r["rss_kb"] / 1024.0) for r in rows if r["rss_kb"] > 0]
    n = len(pts)
    if n < 2:
        return None
    t0 = pts[0][0]
    xs = [(t - t0) / 3600.0 for t, _ in pts]
    ys = [y for _, y in pts]
    mx = sum(xs) / n
    my = sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def summarise(rows, min_samples=MIN_SAMPLES):
    """Return a dict with `status` (measured / insufficient / not measured) and the statistics."""
    # Rows in which the process was absent carry zero in every column (the negative control of the sampler).
    present = [r for r in rows if r["rss_kb"] > 0 or r["threads"] > 0]
    out = {"n_rows": len(rows), "n_absent": len(rows) - len(present), "n_present": len(present)}
    if not rows:
        out["status"] = "not measured"
        out["reason"] = "the file has no sample row"
        return out
    if not present:
        out["status"] = "not measured"
        out["reason"] = "every row is zero: the process was never found (check the process name)"
        return out
    cpus = sorted(r["cpu"] for r in present if r["cpu"] is not None)
    out["n_cpu_empty"] = len(present) - len(cpus)
    if not cpus:
        out["status"] = "not measured"
        out["reason"] = "no CPU value could be measured"
        return out
    out["cpu_mean"] = sum(cpus) / len(cpus)
    out["cpu_median"] = percentile(cpus, 50)
    out["cpu_p95"] = percentile(cpus, 95)
    out["cpu_max"] = cpus[-1]
    out["rss_slope_mb_per_h"] = slope_mb_per_h(present)
    out["rss_final_mb"] = present[-1]["rss_kb"] / 1024.0
    out["hours"] = (present[-1]["t"] - present[0]["t"]) / 3600.0
    if len(present) < min_samples:
        out["status"] = "insufficient"
        out["reason"] = "%d usable rows, fewer than %d: do not quote these as rates" % (len(present), min_samples)
    else:
        out["status"] = "measured"
    return out


def fmt(v, spec):
    return "n/a" if v is None else format(v, spec)


def report(label, path, min_samples):
    """Print one block. Returns True when the file is measured."""
    rows, skipped = load(path)
    s = summarise(rows, min_samples)
    print("== %s (%s)" % (label, path))
    print("rows: %d usable, %d with the process absent, %d unreadable"
          % (s["n_present"], s["n_absent"], len(skipped)))
    if skipped:
        print("warning: %d line(s) could not be read, for example %r" % (len(skipped), skipped[0][:70]))
    if s.get("n_cpu_empty"):
        print("note: %d row(s) had an empty CPU value and were left out of the CPU statistics"
              % s["n_cpu_empty"])
    if s["status"] == "not measured":
        print("status: not measured -- %s" % s["reason"])
        return False
    print("cpu %% (one core = 100): mean %s  median %s  p95 %s  max %s"
          % (fmt(s["cpu_mean"], ".2f"), fmt(s["cpu_median"], ".2f"), fmt(s["cpu_p95"], ".2f"),
             fmt(s["cpu_max"], ".2f")))
    print("resident memory: final %s MB  slope %s MB/h  over %s h"
          % (fmt(s["rss_final_mb"], ".1f"), fmt(s["rss_slope_mb_per_h"], ".2f"), fmt(s["hours"], ".2f")))
    if s["status"] == "insufficient":
        print("status: insufficient -- %s" % s["reason"])
        return False
    print("status: measured")
    return True


# ---------------------------------------------------------------- selftest

def _tsv(rows):
    head = "epoch_s\tcpu_pct\trss_kb\tthreads\tbattery_pct\trss_alt_kb\tenergy_impact\tref_energy_impact\n"
    return head + "".join("\t".join(str(x) for x in r) + "\n" for r in rows)


def _row(t, cpu, rss_kb=100000, th=5):
    return [t, "" if cpu is None else cpu, rss_kb, th, "", rss_kb, 0, ""]


def _cpu_from_cputime(times, cputimes):
    """The arithmetic of the macOS sampler: 100 * (increase of CPU seconds) / (increase of wall seconds)."""
    out = [None]
    for i in range(1, len(times)):
        d = times[i] - times[i - 1]
        out.append(100.0 * (cputimes[i] - cputimes[i - 1]) / d if d > 0 else None)
    return out


def selftest():
    fails = []
    tmp = tempfile.mkdtemp(prefix="e3_selftest_")
    n = [0]

    def write(rows):
        n[0] += 1
        p = os.path.join(tmp, "s%d.tsv" % n[0])
        with open(p, "w", encoding="utf-8") as f:
            f.write(_tsv(rows))
        return p

    def check(name, cond, detail=""):
        if not cond:
            fails.append("%s %s" % (name, detail))

    def near(a, b, eps=1e-6):
        return a is not None and abs(a - b) < eps

    try:
        # Case: CPU time rises by 0.02 s every second -> 2.0 %.
        times = list(range(0, 600))
        cpu = _cpu_from_cputime(times, [0.02 * t for t in times])
        rows, _ = load(write([_row(t, None if c is None else round(c, 2)) for t, c in zip(times, cpu)]))
        s = summarise(rows, min_samples=100)
        check("known series (0.02 s/s is 2.0 %)", s["status"] == "measured" and near(s["cpu_mean"], 2.0)
              and near(s["cpu_median"], 2.0) and near(s["cpu_p95"], 2.0), repr(s))
        check("first row has an empty CPU value and is left out, not read as 0", s["n_cpu_empty"] == 1, repr(s))

        # Case: 1..100 gives mean 50.5, median 50.5, 95th percentile 95.05 (linear interpolation), max 100.
        rows, _ = load(write([_row(30 * i, float(i + 1)) for i in range(100)]))
        s = summarise(rows, min_samples=100)
        check("statistics of 1..100", near(s["cpu_mean"], 50.5) and near(s["cpu_median"], 50.5)
              and near(s["cpu_p95"], 95.05) and near(s["cpu_max"], 100.0), repr(s))

        # Case: resident memory growing by 10 MB per hour.
        rows, _ = load(write([_row(30 * i, 1.0, rss_kb=int(100 * 1024 + 10 * 1024 * (30 * i) / 3600.0))
                              for i in range(200)]))
        s = summarise(rows, min_samples=100)
        check("slope of 10 MB per hour", near(s["rss_slope_mb_per_h"], 10.0, 0.01), repr(s))

        # Negative controls.
        rows, _ = load(write([_row(30 * i, 0, rss_kb=0, th=0) for i in range(600)]))
        s = summarise(rows)
        check("all zeros means not measured", s["status"] == "not measured", repr(s))
        rows, _ = load(write([]))
        s = summarise(rows)
        check("a file with no sample row is not measured", s["status"] == "not measured", repr(s))
        rows, _ = load(write([_row(30 * i, None) for i in range(600)]))
        s = summarise(rows)
        check("a file with no CPU value is not measured", s["status"] == "not measured", repr(s))
        rows, _ = load(write([_row(30 * i, 1.0) for i in range(50)]))
        s = summarise(rows)
        check("a short run is insufficient, not measured-as-low", s["status"] == "insufficient", repr(s))
        rows, _ = load(write([_row(30 * i, 0, rss_kb=0, th=0) for i in range(300)]
                             + [_row(30 * (300 + i), 4.0) for i in range(600)]))
        s = summarise(rows)
        check("rows with the process absent are left out of the mean",
              s["status"] == "measured" and near(s["cpu_mean"], 4.0) and s["n_absent"] == 300, repr(s))

        # Row reading: the `31/1` thread form is kept, an unreadable line is counted, not dropped silently.
        p = write([_row(0, 1.0)])
        with open(p, "a", encoding="utf-8") as f:
            f.write("30\t2.0\t100000\t31/1\t\t100000\t0\t\n")
            f.write("60\tnot-a-number\t100000\t5\n")
            f.write("90\t2.0\n")
        rows, skipped = load(p)
        check("the 31/1 thread form is read", len(rows) == 2 and rows[1]["threads"] == 31, repr(rows))
        check("unreadable lines are counted", len(skipped) == 2, repr(skipped))

        # Command line: an all-zero file exits 1, a measured file exits 0.
        bad = write([_row(30 * i, 0, rss_kb=0, th=0) for i in range(600)])
        good = write([_row(30 * i, 2.0) for i in range(600)])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc_bad = main([bad])
            rc_good = main(["working=" + good, "idle=" + good])
            rc_none = main([])
            rc_missing = main([os.path.join(tmp, "absent.tsv")])
        check("main exits 1 for an all-zero file", rc_bad == 1)
        check("main exits 0 for a measured file", rc_good == 0)
        check("main exits 2 without a file", rc_none == 2)
        check("main exits 2 for a missing file", rc_missing == 2)
    finally:
        for name in os.listdir(tmp):
            os.remove(os.path.join(tmp, name))
        os.rmdir(tmp)
    if fails:
        for m in fails:
            print("FAIL " + m)
        print("selftest failed: %d" % len(fails))
        return 1
    print("selftest OK")
    return 0


def main(argv):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    args = list(argv)
    if "--selftest" in args:
        return selftest()
    min_samples = MIN_SAMPLES
    if "--min-samples" in args:
        i = args.index("--min-samples")
        try:
            min_samples = int(args[i + 1])
        except (IndexError, ValueError):
            print("summarize_e3: --min-samples needs an integer", file=sys.stderr)
            return 2
        del args[i:i + 2]
    if not args or any(a.startswith("-") for a in args):
        print(__doc__, file=sys.stderr)
        return 2
    targets = []
    for a in args:
        label, sep, path = a.partition("=")
        if not sep:
            label, path = os.path.basename(os.path.dirname(os.path.abspath(a))) or a, a
        if not os.path.isfile(path):
            print("summarize_e3: no such file: %s" % path, file=sys.stderr)
            return 2
        targets.append((label, path))
    all_ok = True
    for label, path in targets:
        all_ok = report(label, path, min_samples) and all_ok
        print()
    if len(targets) == 1:
        print("note: one condition only. The cost is reported for the idle and the working condition, "
              "never as a single figure.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
