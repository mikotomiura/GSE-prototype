"""Generate synthetic key-press sequences for the conformance check (no human data).

Each case is (t0, presses). The generator mixes typing gaps, dense typing that overflows
the event buffer within the 30 s window, pauses of 2 to 90 s, ties (gap 0), deletion runs
of up to 20 presses, ignored keys, a start time before the first press, and sequences
longer than the event buffer. Branch coverage is reported by selftest.py.

Usage: python3 generate_inputs.py <seed> <n_cases> <out.json>
"""
import json
import random
import sys

CATS = ["alphabetic"] * 30 + ["space"] * 6 + ["numeric", "punctuation", "sentence_punctuation", "enter", "tab",
        "navigation", "other", "escape"]


def gap(rng):
    r = rng.random()
    if r < 0.04:
        return 0
    if r < 0.10:
        return rng.randint(1, 100)
    if r < 0.70:
        return rng.randint(60, 450)
    if r < 0.88:
        return rng.randint(450, 2600)
    if r < 0.97:
        return rng.randint(2000, 30000)
    return rng.randint(30000, 90000)


def dense_case(rng):
    """More than 300 presses within 30 s, so that the event buffer overflows inside the window."""
    t = t_first = rng.randint(1_600_000_000_000, 1_700_000_000_000)
    presses = []
    for _ in range(rng.randint(320, 420)):
        presses.append((t, "backspace" if rng.random() < 0.2 else rng.choice(CATS[:36])))
        t += rng.randint(0, 60) if rng.random() < 0.8 else rng.randint(250, 400)
    return [t_first - rng.randint(0, 500), presses]


def case(rng):
    if rng.random() < 0.1:
        return dense_case(rng)
    n = rng.choice([2, 3, 5, 20, 80, 200, 400, 700])
    t = rng.randint(1_600_000_000_000, 1_700_000_000_000)
    t0 = t - rng.choice([0, 0, 0, rng.randint(1, 1500), rng.randint(2000, 40000)])
    presses = []
    while len(presses) < n:
        if rng.random() < 0.03:
            for _ in range(rng.randint(5, 20)):
                presses.append((t, rng.choice(["backspace", "backspace", "delete"])))
                t += rng.choice([0, rng.randint(20, 200)])
            continue
        presses.append((t, rng.choice(CATS) if rng.random() > 0.08 else "backspace"))
        t += gap(rng)
    return [t0, presses[:n]]


def main():
    seed, n, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    rng = random.Random(seed)
    cases = [case(rng) for _ in range(n)]
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"seed": seed, "cases": cases}, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
