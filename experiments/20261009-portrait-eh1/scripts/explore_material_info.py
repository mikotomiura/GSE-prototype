"""Exploratory, outside the frozen criteria (design section 8, added after the results were read).

Question: in each world, does the generator's material carry stall information beyond model A?
If it does while PC2 (p_stuck mapped to shrinking under the default scheduler) shows no gain, the
E1-3 detector has not been shown to work through the default scheduler, and the zero gain of the
real generators is not evidence that the default-scheduler shape is leak-free.

Model A, the window labels, the folds and the out-of-fold AUC are the ones in checks.py. Added to A:
the 60 s window mean of p_stuck, or of the F levels (f1 f3 f4 f5 f6). One fit per classifier,
no bootstrap. Reads the work dir of a production run; writes one JSON.

Usage: explore_material_info.py <config.json> <SEED> <work dir> <out json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

import checks as ck
import portrait as pt

F_COLS = ("f1", "f3", "f4", "f5", "f6")


def window_means(sess: pt.Session, col: str, n_w: int, ws: int) -> np.ndarray:
    with np.errstate(all="ignore"):
        return np.nanmean(sess.feat[col][: n_w * ws].reshape(n_w, ws), axis=1)


def main() -> int:
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    seed = int(Path(sys.argv[2]).read_text().strip())
    work, out = Path(sys.argv[3]), Path(sys.argv[4])
    manifest = [m for m in json.loads((work / "sessions.json").read_text(encoding="utf-8")) if m["set"] == "P"]
    ws, folds = cfg["e13"]["window_s"], cfg["e13"]["folds"]
    XA, Y, G, PS, FL = [], [], [], [], []
    for i, m in enumerate(manifest):
        s = pt.load_session(work, m)
        fa, lab, _ = pt.presence_features(s, cfg)
        n_w = len(lab)
        XA.append(fa)
        Y.append(lab)
        G.append(np.full(n_w, i))
        PS.append(window_means(s, "p_stuck", n_w, ws)[:, None])
        FL.append(np.stack([window_means(s, c, n_w, ws) for c in F_COLS], axis=1))
    XA, Y, G, PS, FL = np.vstack(XA), np.concatenate(Y), np.concatenate(G), np.vstack(PS), np.vstack(FL)
    ones = np.ones(len(Y))
    ps_alone = np.nan_to_num(PS[:, 0], nan=float(np.nanmedian(PS[:, 0])))
    res = {"_note": "Outside the frozen criteria; added after the results were read (design section 8).",
           "n_windows": int(len(Y)), "n_sessions": len(manifest), "prevalence": float(Y.mean()),
           "auc_p_stuck_alone": ck.weighted_auc(ps_alone, Y, ones)}
    for k in ("hgb", "lr"):
        a = ck.weighted_auc(ck.oof_predict(XA, Y, G, k, seed, folds), Y, ones)
        b_ps = ck.weighted_auc(ck.oof_predict(np.hstack([XA, PS]), Y, G, k, seed, folds), Y, ones)
        b_fl = ck.weighted_auc(ck.oof_predict(np.hstack([XA, FL]), Y, G, k, seed, folds), Y, ones)
        res[k] = {"auc_A": a, "auc_A_plus_p_stuck": b_ps, "gain_p_stuck": b_ps - a,
                  "auc_A_plus_F_levels": b_fl, "gain_F_levels": b_fl - a}
    out.write_text(json.dumps(ck.clean(res), indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(ck.clean(res)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
