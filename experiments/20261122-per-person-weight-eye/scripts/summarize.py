"""複製の集計（群 × セル × 案の拒否の数と MC SE、案どうしの対の差と SE）。repo に入れるのはこの集計だけ（複製の jsonl は入れない）。

使い方: python3 -I summarize.py <select|report> <out_dir> --null <1|2>
出力: <out_dir>/<組>/summary_null<n>.json
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eye as EY  # noqa: E402
import run_eye as RE  # noqa: E402

LEVELS = (0.05, 0.01, 0.001)
PAIRS = (("E1", "E2"), ("E1", "E3"), ("E2", "E3"))


def load(path, ch):
    rows = [json.loads(x) for x in open(path)]
    if {r["code_hash"] for r in rows} != {ch}:
        sys.exit("%s にコードのハッシュが違う行がある" % path)
    return rows


def summarize_group(rows):
    out = {}
    for cell in rows[0]["cells"]:
        n = len(rows)
        C = {}
        rej = {e: np.array([r["cells"][cell][e]["p"] <= 0.05 for r in rows], float) for e in EY.EYES}
        for e in EY.EYES:
            ps = np.array([r["cells"][cell][e]["p"] for r in rows])
            C[e] = {}
            for a in LEVELS:
                k = int((ps <= a).sum())
                ph = k / n
                C[e][str(a)] = dict(n_rej=k, rate=ph, se=math.sqrt(ph * (1 - ph) / n))
        C["pairs"] = {}
        for a, b in PAIRS:
            d = rej[a] - rej[b]
            C["pairs"]["%s-%s" % (a, b)] = dict(diff=float(d.mean()), se=float(d.std(ddof=1) / math.sqrt(n)) if n > 1 else None)
        C["n"] = n
        out[cell] = C
    return out


def main():
    argv = sys.argv[1:]
    i = argv.index("--null")
    null = int(argv[i + 1])
    argv = argv[:i] + argv[i + 2:]
    which, out = argv[0], argv[1]
    ch = RE.code_hash()
    d = os.path.join(out, which)
    groups = {}
    for r in RE.plan(which):
        if r["null"] == null:
            groups.setdefault(RE.group(r), set()).add(r["seed"])
    S = dict(which=which, null=null, code_hash=ch, groups={})
    for g, seeds in groups.items():
        rows = load(os.path.join(d, g + ".jsonl"), ch)
        if {r["seed"] for r in rows} != seeds or len(rows) != len(seeds):
            sys.exit("群 %s の複製が計画と合わない（分母は計画したすべての複製・D8）" % g)
        S["groups"][g] = summarize_group(rows)
    json.dump(S, open(os.path.join(d, "summary_null%d.json" % null), "w"), indent=1)
    print("集計を書いた: %s（%d 群）" % (os.path.join(d, "summary_null%d.json" % null), len(groups)))


if __name__ == "__main__":
    main()
