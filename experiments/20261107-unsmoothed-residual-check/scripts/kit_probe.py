"""kit（既定は papers/ の kit・selftest の変異では 1 か所を変えた写し）で、合成の 300 本の行と u の境界の値を出す（P-RAW・P-U）。

使い方: python3 -I kit_probe.py <kit_dir> <out.json>
出力: cases（各本の行 [t, o, u, x_raw(hex), y_raw(hex), x(hex), y(hex), alpha, path]）・edges（[o, x_raw, y_raw, u]）・constants。
合成のデータだけ（人のデータは無い）。
"""
import gzip
import json
import os
import sys

kit = os.path.realpath(sys.argv[1])
sys.path.insert(0, kit)
from symbolizer import load_constants  # noqa: E402
from variants import unsmoothed_symbol, variant_rows  # noqa: E402

C = load_constants()
with gzip.open(os.path.join(kit, "conformance", "data", "inputs.json.gz"), "rt", encoding="utf-8") as f:
    cases = json.load(f)["cases"]
out = []
for t0, presses in cases:
    rows = variant_rows(t0, [tuple(p) for p in presses], C)
    out.append([[r[0], r[1], r[2], r[3].hex(), r[4].hex(), r[5].hex(), r[6].hex(), r[7], r[8]] for r in rows])
pts = [i / 5 for i in range(6)] + [-0.3, -1e-12, 0.19999999999999998, 0.2, 0.9999999999999999, 1.0, 1.7]
edges = [[o, x, y, unsmoothed_symbol(o, x, y, C)] for o in (0, 7, 25) for x in pts for y in pts]
json.dump(dict(cases=out, edges=edges, constants=C), open(sys.argv[2], "w"))
