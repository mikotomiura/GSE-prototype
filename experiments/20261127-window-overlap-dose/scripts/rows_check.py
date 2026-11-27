"""P-ROWS（conditions V1）と入力の時刻の照合: 実データで、列ごとの行の数が規則どおりかを系列ごとに照らす。当てはめはしない。

- 列 A: 行の数が kit の thinned_mask(times, 1,000 · s) の真の数（s = 1 は全行）。
- 列 C・C′: 系列ごとの行の数が列 A と同じ。
- 列 B: 位相の行の数の和が t − t0 ≥ 1,000 · s の行の数。
読み込みは load_dose と同じ（obs と data.py の系列の一致・時刻の数・時刻の差 1,000 ms は読み込みの中で照らす）。
出すのは照らした系列の数・外れた系列の数だけ。

使い方: python3 -I rows_check.py <work> <sidecar> <seed> <out.json>
返り値: 0 = 外れ 0・3 = 外れがある。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swap  # noqa: E402,F401
from swap import load_dose as LD, masks as MK  # noqa: E402


def check(times_all, col):
    arm, s = LD.parse(col)
    series = [tu["t"] for tun in times_all for tu in tun]
    rows = LD.series_rows(series, col)
    n, bad = 0, 0
    for t, rr in zip(series, rows):
        n += 1
        got = sum(len(r) for r in rr)
        if arm == "A":
            exp = len(t) if s == 1 else sum(MK.kit_variants().thinned_mask(list(t), step_ms=LD.TICK * s))
        elif arm == "B":
            exp = sum(1 for x in t if x - t[0] >= LD.TICK * s)
        else:
            exp = len(t) if s == 1 else sum(MK.kit_variants().thinned_mask(list(t), step_ms=LD.TICK * s))
        bad += int(got != exp)
    return dict(series=n, mismatched=bad)


def main(work, side, seed, out):
    wu, times_all = LD.load_u_and_times(work, side, int(seed))  # 読み込みの照合（obs・時刻の数・1,000 ms）
    R = dict(units=sum(len(u) for u in times_all), columns={c: check(times_all, c) for c in LD.ORDER})
    R["passed"] = all(v["mismatched"] == 0 and v["series"] > 0 for v in R["columns"].values())
    json.dump(R, open(out, "w"), indent=1)
    print(json.dumps(dict(passed=R["passed"], mismatched=sum(v["mismatched"] for v in R["columns"].values()))))
    return 0 if R["passed"] else 3


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
