"""Round 4 design 3.6 (descriptive): compare the values of the names round 3 also ran (8 configurations, PC1,
PCcal, PCcal0, the 6 one-value oracles) with round 3's e13.json, label by label.

Values compared: the point estimate and both ends of the 95% interval of each of the 4 attackers, the null gain
of each permutation and null95. Verdicts are listed side by side with what may have changed them (the null over
27 names instead of 17, the per-form conditions, or the values); they are not compared as one flag, because round 3
had one detector per label and round 4 one per form.

Usage: compare_round3.py <round 3 e13.json> <round 4 e13.json> <out json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

LABELS = ("L300", "L60", "L1800")
KEYS = [f"{fs}/{k}" for fs in ("full", "small") for k in ("hgb", "lr")]


def num(x) -> float:
    return float(x)  # checks.clean writes non-finite values as the strings "nan", "inf", "-inf"


def main() -> int:
    r3 = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    r4 = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    out: dict = {"_note": "Round 4 design 3.6: descriptive; no verdict depends on it."}
    for t in LABELS:
        c3, c4 = r3[t]["configs"], r4[t]["configs"]
        rows = {}
        worst = 0.0
        for n, a in c3.items():
            b = c4.get(n)
            if b is None:
                rows[n] = {"missing_in_round4": True}
                continue
            diffs = []
            for k in KEYS:
                diffs.append(abs(num(a[k]["gain"]) - num(b[k]["gain"])))
                diffs += [abs(num(x) - num(y)) for x, y in zip(a[k]["ci95"], b[k]["ci95"])]
            if "null_gain_max_by_perm" in a and "null_gain_max_by_perm" in b:
                diffs += [abs(num(x) - num(y)) for x, y in zip(a["null_gain_max_by_perm"], b["null_gain_max_by_perm"])]
                diffs.append(abs(num(a["null95"]) - num(b["null95"])))
            d = max(diffs) if diffs else float("nan")
            worst = max(worst, d)
            rows[n] = {"max_abs_diff": d, "verdict_round3": a.get("verdict"), "verdict_round4": b.get("verdict"),
                       "verdict_changed": a.get("verdict") != b.get("verdict")}
        out[t] = {"max_abs_diff": worst, "names": rows,
                  "round3_detector": {k: r3[t].get(k) for k in ("pc1_ok", "pccal_ok", "null_ok", "detector_ok", "reasons")},
                  "round4_detector": {k: r4[t].get(k) for k in ("pc1_ok", "pccal_ok", "null_ok", "nan", "fit_failed",
                                                                "forms")}}
        changed = [n for n, r in rows.items() if r.get("verdict_changed")]
        print(f"{t}: max |diff| = {worst:.3g} over {len(rows)} names; verdicts changed: {changed or 'none'}")
    Path(sys.argv[3]).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
