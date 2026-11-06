"""期待の痕跡を作る（公開しない）。合成の入力を元の変換と同じ NDJSON にし、試験と同じ replay（SHA-256 固定）に通す。

使い方: python3 -I make_expected.internal.py <inputs.json> <gse-replay> <out_expected.json>
出力: 各ケースの行 [t, ewma_x の 16 進, ewma_y の 16 進, obs, alpha]。
"""
import json
import subprocess
import sys
import tempfile
import os

DWELL = 100


def ndjson(t0, presses):
    lines = [{"type": "meta", "session_start": t0, "hmm_version": "0.5.0"}, {"type": "session_start", "t": t0}]
    for i, (t, cat) in enumerate(presses):
        rel = t + DWELL
        if i + 1 < len(presses):
            rel = min(rel, max(t, presses[i + 1][0] - 1))
        lines.append({"type": "key", "t": t, "category": cat, "press": True})
        lines.append({"type": "key", "t": rel, "category": cat, "press": False})
    return "".join(json.dumps(x) + "\n" for x in lines)


def main():
    inp, replay, out = sys.argv[1:4]
    cases = json.load(open(inp))["cases"]
    res = []
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "c.ndjson")
        for t0, presses in cases:
            open(p, "w").write(ndjson(t0, presses))
            r = subprocess.run([replay, p], capture_output=True, stdin=subprocess.DEVNULL)
            if r.returncode != 0:
                sys.exit("replay failed")
            rows = json.loads(r.stdout)
            res.append([[x["timestamp"], float(x["ewma_x"]).hex(), float(x["ewma_y"]).hex(), x["obs"], x["alpha"]] for x in rows])
    json.dump({"expected": res}, open(out, "w"), separators=(",", ":"))


if __name__ == "__main__":
    main()
