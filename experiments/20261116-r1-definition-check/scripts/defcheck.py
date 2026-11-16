"""R1 に定義の検査を当てる（conditions.md の D・A・J・K）。登録の外の探索 [E-H]・判定は記述。

B0（門）と 8 つの定義（P1〜P4・N1〜N4）で、CS1 2019 の holdout の主の層について
(a) 推定器の 30 秒の上がりの H1（論文 1 の h1_summary）と (b) 学習器との差（論文 1 の探索 X11 の x11）を出す。
集計値だけを書く。書き手の ID・番号・書き手ごとの値・時刻は出さない。外部の LLM に渡さない。

使い方: OMP_NUM_THREADS=1 python -I defcheck.py <cs1 の holdout の中間> <holdout.json> <confirm_holdout.json>
        <explore_comparison.json> <出力の json>
  中間の横に <中間>_q995・<中間>_w15・<中間>_w60 が要る（論文 1 の build-variants.sh の出力）。
  DEFCHECK_ONLY=B0,N1 のように絞れる（試しの走り。結果は実験の dir の外に書く）。
"""
import copy
import json
import os
import random
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(EXP, "20261105-findings-paper1-prefreeze", "scripts"))
sys.path.insert(0, os.path.join(EXP, "20261106-findings-paper1-exploration", "scripts"))
sys.path.insert(0, os.path.join(EXP, "20261107-stall-shape-multiverse", "scripts"))
import confirm_p1 as C  # noqa: E402
import explore_comparison as X  # noqa: E402  x11 をそのまま使う
import core  # noqa: E402  論文 2 の一般化した検出器

SEED = 20261106
TOL = 1e-12
B0 = dict(W=30_000, theta=("q", 0.99), rule="net", seg="replay")
DETECT_CFG = {
    "B0": B0,
    "P2": dict(B0, theta=("q", 0.995), warm=200),
    "P3": dict(B0, W=15_000),
    "P4": dict(B0, W=60_000),
    "N1": dict(B0, theta=("q", 0.95), warm=100),
    "N2": dict(B0, theta=("fix", 10_000)),
    "N3": dict(B0, rule="ins"),
    "N4": dict(B0, seg="g5"),
}
REPLAY_DIR = {"P2": "q995", "P3": "w15", "P4": "w60"}
ORDER = ("B0", "P1", "P2", "P3", "P4", "N1", "N2", "N3", "N4")
DIFFS = ("logreg_minus_d_p_stuck", "logreg_minus_d_ewma_x", "hgb_minus_d_p_stuck", "hgb_minus_d_ewma_x")


# ---------------- onset ----------------

def unit_dict(w):
    """論文 2 の detect が読む形。押下の分類は k6 の TEXT と削除（論文 2 の prep.py と同じ集合）。"""
    t = np.asarray(w.press, dtype=np.int64)
    return {"t": t, "ins": np.array([c in core_text() for c in w.cats], dtype=bool),
            "dele": np.array([c in ("backspace", "delete") for c in w.cats], dtype=bool), "iv": list(w.intervals)}


def core_text():
    return C.k6.TEXT


def detect_onsets(w, cfg):
    return [(int(s), int(t0)) for s, t0, _, _ in core.detect(unit_dict(w), cfg)]


def replay_onsets(w):
    return [(int(o[0]), int(o[1])) for o in w.onsets]


def k1_mismatch(writers, cfg):
    return sum(1 for units in writers for w in units if detect_onsets(w, cfg) != replay_onsets(w))


class InsCondA:
    """N3 の条件 A の量: 窓の文字の押下の数（削除を数えない）。confirm_p1.net が読む press と pref だけを持つ。"""

    def __init__(self, w):
        self.press = w.ca.press
        pref = [0]
        for c in w.cats:
            pref.append(pref[-1] + (1 if c in C.k6.TEXT else 0))
        self.pref = pref


def detect_writers(writers, name):
    cfg = DETECT_CFG[name]
    out, n = [], 0
    for units in writers:
        nu = []
        for w in units:
            w2 = copy.copy(w)
            w2.onsets = [[s, t0, None, None] for s, t0 in detect_onsets(w, cfg)]
            if cfg["rule"] == "ins":
                w2.ca = InsCondA(w)
            w2.w_ms = cfg["W"]
            n += len(w2.onsets)
            nu.append(w2)
        out.append(nu)
    return out, n


# ---------------- 行と集計 ----------------

def unit_key(w):
    return (w.press[0], w.press[-1], len(w.press))


ORIG_PAUSE_INFO = C.pause_info


def pause_info_key(w, u, end, cs1):
    r = ORIG_PAUSE_INFO(w, u, end, cs1)
    r["_key"] = (unit_key(w), u)
    return r


def make_rows(writers):
    cnt = Counter()
    rng = random.Random(SEED)
    rows = [C.h1_writer(u, rng, cnt, C.MAIN, feats=True) for u in writers]
    return rows, dict(cnt)


def stall_keys(rows):
    return {sv["_key"] for r in rows for cell, sv, _, _ in r if cell[1] == "none"}


def h1_block(rows):
    s = C.h1_summary(rows, SEED, "none", hide=False, sigs=C.SIGS + C.LEVELS, light=False)
    out = {}
    for sig in C.SIGS + C.LEVELS:
        e = {}
        for eps in ("eps_0.001", "eps_0"):
            x = s[sig][eps]
            e[eps] = {k: x[k] for k in ("pairs", "tie_share", "ci_width", "pooled_auc", "ci95", "branch")}
        e["effective_writers"] = s[sig]["weights"]["effective_writers"]
        e["writers_with_pairs"] = s[sig]["weights"]["writers_with_pairs"]
        out[sig] = e
    return out, s


def judge(h1, x11):
    a = all(h1[sig][eps]["branch"] == 1 for sig in C.SIGS for eps in ("eps_0.001", "eps_0"))
    fails = {m: x11["point"][m]["boot_failures"] for m in X.LEARNERS}
    if any(f > C.FAIL_MAX * x11["n_rep"] for f in fails.values()):
        b = "undecidable"
    else:
        b = all(x11["differences"][d]["ci95"][0] > 0 for d in DIFFS)
    return {"a_estimator_equivalent": a, "b_learners_above_changes": b, "kept": bool(a and b is True),
            "a_branches": {sig: {eps: h1[sig][eps]["branch"] for eps in ("eps_0.001", "eps_0")} for sig in C.SIGS},
            "b_lower_bounds": {d: x11["differences"][d]["ci95"][0] for d in DIFFS}, "boot_failures": fails}


def x11_block(writers, rows, conf_h):
    r = X.x11(writers, rows, conf_h)
    gates = r.pop("gates")
    return r, gates


# ---------------- 本体 ----------------

def main():
    work, hold_p, conf_h_p, x11_p, out_p = sys.argv[1:]
    only = set(os.environ["DEFCHECK_ONLY"].split(",")) if os.environ.get("DEFCHECK_ONLY") else None
    if only and os.path.realpath(out_p).startswith(os.path.realpath(os.path.join(HERE, ".."))):
        sys.exit("試しの走りは実験の dir の外に書く")
    conf_h, x11_ref = json.load(open(conf_h_p)), json.load(open(x11_p))
    C.pause_info = pause_info_key
    res = {"seed": SEED, "status": "[E-H] exploration on the opened CS1 2019 holdout", "gates": {}, "mutations": {},
           "definitions": {}}

    base, chk = C.load_cs1(work, hold_p, "holdout")
    res["checks_load_holdout"] = chk
    variants = {}
    for name, suf in REPLAY_DIR.items():
        if only and name not in only:
            continue
        variants[name], res["checks_load_" + name] = C.load_cs1(work + "_" + suf, hold_p, "holdout", suf)

    # K1 と K4（値を出す前）
    g = res["gates"]
    g["K1_B0_mismatch_units"] = k1_mismatch(base, B0)
    for name, ws in variants.items():
        g["K1_%s_mismatch_units" % name] = k1_mismatch(ws, DETECT_CFG[name])
    res["mutations"]["m1_W_plus_1ms_mismatch_units"] = k1_mismatch(base, dict(B0, W=30_001))
    res["mutations"]["m2_q0989_mismatch_units"] = k1_mismatch(base, dict(B0, theta=("q", 0.989)))
    res["units"] = sum(len(u) for u in base)
    if any(v for k, v in g.items() if k.startswith("K1_")):
        json.dump(res, open(out_p, "w"), indent=1)
        sys.exit("K1 が外れた: " + json.dumps(g))
    if not all(v > 0 for v in res["mutations"].values()):
        json.dump(res, open(out_p, "w"), indent=1)
        sys.exit("K4 の変異が K1 を赤にしなかった: " + json.dumps(res["mutations"]))

    onset_counts = {"B0": sum(len(w.onsets) for u in base for w in u)}
    sets = {}
    for name in ORDER:
        if only and name not in only:
            continue
        if name == "B0":
            ws = base
        elif name == "P1":
            ws, oc = C.cross_theta_writers(base)
            onset_counts["P1"] = oc["onsets_cross_task_theta"]
        elif name in REPLAY_DIR:
            ws = variants[name]
            onset_counts[name] = sum(len(w.onsets) for u in ws for w in u)
        else:
            ws, onset_counts[name] = detect_writers(base, name)
        rows, cnt = make_rows(ws)
        h1, h1_full = h1_block(rows)
        x11, xg = x11_block(ws, rows, conf_h)
        sets[name] = stall_keys(rows)
        d = {"onsets": onset_counts[name], "counts": cnt, "H1": h1, "X11": x11}
        if name == "B0":
            g["K2_counts_equal_confirm"] = cnt == conf_h["h1_counts"]
            g["K2_x11_learner_point_and_ci_equal_confirm"] = all(xg.values())
            pt = all(abs(x11["point"][k]["paired_auc_eps0"] - x11_ref["point"][k]["paired_auc_eps0"]) <= TOL
                     for k in x11_ref["point"])
            df = all(abs(x11["differences"][k]["point"] - v["point"]) <= TOL and
                     all(abs(a - b) <= TOL for a, b in zip(x11["differences"][k]["ci95"], v["ci95"]))
                     for k, v in x11_ref["differences"].items())
            g["K2_x11_points_equal_explore"] = pt
            g["K2_x11_differences_equal_explore"] = df
            g["K2_h1_equal_confirm"] = all(abs(h1[s][e]["pooled_auc"] - conf_h["H1"][s][e]["pooled_auc"]) <= TOL
                                           for s in C.SIGS for e in ("eps_0.001", "eps_0"))
            if not all(v for k, v in g.items() if k.startswith("K2_")):
                json.dump(res, open(out_p, "w"), indent=1)
                sys.exit("K2 が外れた: " + json.dumps(g))
        else:
            d["judgement"] = judge(h1, x11)
            ref = {"P1": "theta_cross_task", "P2": "replay_q995", "P3": "replay_w15", "P4": "replay_w60"}.get(name)
            if ref:
                ok = all(abs(h1[s][e]["pooled_auc"] - conf_h["sensitivity"][ref]["H1"][s][e]["pooled_auc"]) <= TOL
                         for s in C.SIGS for e in ("eps_0.001", "eps_0"))
                g["K3_%s_h1_equal_confirm" % name] = ok
                if not ok:
                    json.dump(res, open(out_p, "w"), indent=1)
                    sys.exit("K3 が外れた: " + name)
            else:
                g["K5_%s_onsets_differ_from_B0" % name] = onset_counts[name] != onset_counts["B0"]
        res["definitions"][name] = d
        json.dump(res, open(out_p, "w"), indent=1)  # 途中で止まっても済んだ定義を残す
        print(name, "done", flush=True)

    if "B0" in sets:
        for name, s in sets.items():
            if name == "B0":
                continue
            inter = len(sets["B0"] & s)
            res["definitions"][name]["overlap_with_B0"] = {
                "b0_stall_rows": len(sets["B0"]), "stall_rows": len(s),
                "share_of_b0_in_def": inter / len(sets["B0"]) if sets["B0"] else None,
                "share_of_def_in_b0": inter / len(s) if s else None}
    judged = {k: v["judgement"] for k, v in res["definitions"].items() if "judgement" in v}
    res["overall"] = {"definitions_judged": len(judged), "all_kept": len(judged) == 8 and all(j["kept"] for j in judged.values()),
                      "not_kept": sorted(k for k, j in judged.items() if not j["kept"])}
    if any(k.startswith("K5_") and not v for k, v in g.items()):
        res["overall"]["warning"] = "K5: onset の数が B0 と同じ定義がある"
    json.dump(res, open(out_p, "w"), indent=1)
    print(json.dumps({"gates": g, "overall": res["overall"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
