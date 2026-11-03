"""cross-review 2 巡目の Codex 1 の事後の確かめ（2026-11-03・計算の後）。
系列の特徴（M2 の入力の第 3 チャネル p_stuck）は窓の 30 点すべてで last_le を呼ぶ。
窓の左端（t − 31 秒 + 1 秒 = 系列の最初の点）より後に最初の feat 行がある問いの数と、未来の値で埋まった点の数を数える。
"""
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import dryrun_v2 as D  # noqa: E402

work, seed = sys.argv[2], int(sys.argv[3])
writers = D.load(work)
rng = np.random.default_rng(seed)
total = probes_hit = points_hit = 0
for ss in writers:
    for s in ss:
        for t in D.draw_probes(rng, s["a"], s["b"]):
            total += 1
            edges = (t - D.WIN_START) + np.arange(31) * 1000
            first = s["feat"][0, 0]
            k = int((edges[1:] < first).sum())
            points_hit += k
            probes_hit += k > 0
print("probes", total, "系列の点の一部が最初の feat 行より前の問い", probes_hit, "そうなった点", points_hit, "of", total * 30)
