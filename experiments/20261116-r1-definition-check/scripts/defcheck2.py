"""R1 の定義の検査の 2 回目（conditions-2.md の L・G・K）。登録の外の探索・判定は記述。

使い方: OMP_NUM_THREADS=1 python -I defcheck2.py length <cs1 holdout の中間> <holdout.json> <defcheck.json> <出力>
        OMP_NUM_THREADS=1 python -I defcheck2.py grid   <cs1 holdout の中間> <holdout.json> <defcheck.json> <出力>
        OMP_NUM_THREADS=1 python -I defcheck2.py klicke <klicke の work> <explore_klicke.json> <出力>
  DEFCHECK_ONLY=B0 のように絞れる（試しの走り。結果は実験の dir の外に書く）。
集計値だけを書く。書き手の ID・番号・書き手ごとの値・時刻は出さない。外部の LLM に渡さない。
"""
import copy
import glob
import json
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import defcheck as D  # noqa: E402  1 回目のスクリプト（書き換えない）

C, X, core = D.C, D.X, D.core
TOL = 1e-12
SIGS = C.SIGS
EPS = ("eps_0.001", "eps_0")
GRID_TO_RUN1 = {"W30_q0.99_net_replay": "B0", "W15_q0.99_net_replay": "P3", "W60_q0.99_net_replay": "P4",
                "W30_q0.95_net_replay": "N1", "W30_fix10s_net_replay": "N2", "W30_q0.99_ins_replay": "N3",
                "W30_q0.99_net_g5": "N4"}
KLICKE_DEFS = {"B0": D.B0, "P2": D.DETECT_CFG["P2"], "P3": D.DETECT_CFG["P3"], "P4": D.DETECT_CFG["P4"],
               "N1": D.DETECT_CFG["N1"], "N2": D.DETECT_CFG["N2"], "N3": D.DETECT_CFG["N3"], "N4": D.DETECT_CFG["N4"]}


def stop(res, out, msg):
    dump(res, out)
    sys.exit(msg)


def dump(res, out):
    with open(out + ".tmp", "w") as f:
        json.dump(res, f, indent=1)
    os.replace(out + ".tmp", out)


def detect_ws(writers, cfg):
    """1 回目の detect_writers と同じ（名前でなく設定を受ける）。"""
    out, n = [], 0
    for units in writers:
        nu = []
        for w in units:
            w2 = copy.copy(w)
            w2.onsets = [[s, t0, None, None] for s, t0 in D.detect_onsets(w, cfg)]
            if cfg["rule"] == "ins":
                w2.ca = D.InsCondA(w)
            w2.w_ms = cfg["W"]
            n += len(w2.onsets)
            nu.append(w2)
        out.append(nu)
    return out, n


def evaluate(ws, seed, cs1):
    cnt = Counter()
    rng = random.Random(seed)
    rows = [C.h1_writer(u, rng, cnt, C.MAIN, feats=True, cs1=cs1) for u in ws]
    s = C.h1_summary(rows, seed, "none", hide=False, sigs=C.SIGS + C.LEVELS, light=False)
    h1 = {}
    for sig in C.SIGS + C.LEVELS:
        e = {eps: {k: s[sig][eps][k] for k in ("pairs", "tie_share", "ci_width", "pooled_auc", "ci95", "branch")}
             for eps in EPS}
        e["effective_writers"] = s[sig]["weights"]["effective_writers"]
        e["writers_with_pairs"] = s[sig]["weights"]["writers_with_pairs"]
        h1[sig] = e
    d = {"counts": dict(cnt), "H1": h1, "stall_keys": D.stall_keys(rows)}
    try:
        x11 = X.x11(ws, rows, {"H3": {m: {"auc": float("nan"), "ci95": [0, 0], "boot_failures": -1}
                                      for m in X.LEARNERS}})
        x11.pop("gates")
        d["X11"] = x11
        d["judgement"] = D.judge(h1, x11)
    except (TypeError, ValueError) as e:
        # 学習器が全データで失敗する・両方がそろって成功した引き直しが 0 など（コードレビューの指摘・§J の「判定できない」）
        a = all(h1[s][e2]["branch"] == 1 for s in C.SIGS for e2 in EPS)
        d["X11"] = {"error": type(e).__name__}
        d["judgement"] = {"a_estimator_equivalent": a, "b_learners_above_changes": "undecidable", "kept": False,
                          "a_branches": {s: {e2: h1[s][e2]["branch"] for e2 in EPS} for s in C.SIGS},
                          "b_lower_bounds": None, "boot_failures": None}
    return d


def evaluate_keys(ws):
    """B0 の停滞の行の鍵だけ（続きから回すとき・対照の引きは evaluate と同じ流れ）。"""
    cnt = Counter()
    rng = random.Random(D.SEED)
    rows = [C.h1_writer(u, rng, cnt, C.MAIN, feats=False, cs1=True) for u in ws]
    return D.stall_keys(rows)


def same(d, ref):
    """H1 の Δ と水準の点推定（2 つの ε）と、X11 の点推定と差の点推定が 1e-12 で一致するか。"""
    ok = all(abs(d["H1"][s][e]["pooled_auc"] - ref["H1"][s][e]["pooled_auc"]) <= TOL
             for s in C.SIGS + C.LEVELS for e in EPS)
    ok &= all(abs(d["X11"]["point"][k]["paired_auc_eps0"] - v["paired_auc_eps0"]) <= TOL
              for k, v in ref["X11"]["point"].items())
    ok &= all(abs(d["X11"]["differences"][k]["point"] - v["point"]) <= TOL
              for k, v in ref["X11"]["differences"].items())
    return bool(ok)


def finish(d):
    """書き出す形（stall_keys は重なりの計算にだけ使い、書かない）。"""
    return {k: v for k, v in d.items() if k != "stall_keys"}


def overlap(b0, s):
    inter = len(b0 & s)
    return {"b0_stall_rows": len(b0), "stall_rows": len(s),
            "share_of_b0_in_def": inter / len(b0) if b0 else None, "share_of_def_in_b0": inter / len(s) if s else None}


def provenance():
    import hashlib
    import subprocess
    root = os.path.realpath(os.path.join(HERE, "..", "..", ".."))
    files = [os.path.join(HERE, f) for f in ("defcheck.py", "defcheck2.py")] + \
            [os.path.join(HERE, "..", f) for f in ("conditions.md", "conditions-2.md", "run2.sh", "results/defcheck.json")] + \
            [os.path.join(root, f) for f in (
                "experiments/20261105-findings-paper1-prefreeze/scripts/confirm_p1.py",
                "experiments/20261105-findings-paper1-prefreeze/scripts/prefreeze.py",
                "experiments/20261101-klicke-early-stall-trigger/scripts/analyze_item2.py",
                "experiments/20261106-findings-paper1-exploration/scripts/explore_comparison.py",
                "experiments/20261106-findings-paper1-exploration/results/explore_klicke.json",
                "experiments/20261107-stall-shape-multiverse/scripts/core.py",
                "experiments/20261103-stall-candidates-c1c2c6/candidates.py")]
    head = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", root, "status", "--porcelain", "--"] + files, capture_output=True,
                           text=True).stdout.strip()
    return {"git_head": head, "uncommitted_inputs": bool(dirty),
            "sha256": {os.path.relpath(f, root): hashlib.sha256(open(f, "rb").read()).hexdigest()
                       for f in files if os.path.exists(f)}}


def guard_out(out, only):
    if only and os.path.realpath(out).startswith(os.path.realpath(os.path.join(HERE, ".."))):
        sys.exit("試しの走りは実験の dir の外に書く")


# ---------------- L 停滞の長さ ----------------

def run_length(work, hold_p, run1_p, out, only):
    run1 = json.load(open(run1_p))["definitions"]
    base, chk = C.load_cs1(work, hold_p, "holdout")
    res = {"mode": "length", "seed": D.SEED, "checks_load": chk, "provenance": provenance(), "gates": {},
           "definitions": {}}
    saved = C.STALL_GAP
    keys = {}
    try:
        for name, gap in (("B0", 30_000), ("L60", 60_000), ("L90", 90_000)):
            if only and name not in only:
                continue
            C.STALL_GAP = gap
            d = evaluate(base, D.SEED, True)
            keys[name] = d["stall_keys"]
            d["stall_gap_ms"] = gap
            if name == "B0":
                res["gates"]["B0_equals_run1"] = same(d, run1["B0"])
                if not res["gates"]["B0_equals_run1"]:
                    stop(res, out, "門: B0 が 1 回目と一致しない")
            elif "B0" in keys:
                d["overlap_with_B0"] = overlap(keys["B0"], keys[name])
            res["definitions"][name] = finish(d)
            dump(res, out)
            print(name, "done", flush=True)
    finally:
        C.STALL_GAP = saved
    j = {k: v["judgement"] for k, v in res["definitions"].items() if k != "B0"}
    res["overall"] = {"judged": len(j), "all_kept": len(j) == 2 and all(v["kept"] for v in j.values()),
                      "not_kept": sorted(k for k, v in j.items() if not v["kept"])}
    dump(res, out)
    print(json.dumps({"gates": res["gates"], "overall": res["overall"]}, ensure_ascii=False))


# ---------------- G 全格子 ----------------

def run_grid(work, hold_p, run1_p, out, only):
    run1 = json.load(open(run1_p))["definitions"]
    base, chk = C.load_cs1(work, hold_p, "holdout")
    res = {"mode": "grid", "seed": D.SEED, "checks_load": chk, "provenance": provenance(), "gates": {},
           "definitions": {}}
    cfgs = {core.cfg_id(c): c for c in core.CONFIGS}
    assert len(cfgs) == 90 and set(GRID_TO_RUN1) <= set(cfgs)
    order = list(GRID_TO_RUN1) + [k for k in cfgs if k not in GRID_TO_RUN1]  # 門の 7 つを先に回す
    b0_keys = None
    if os.environ.get("DEFCHECK_RESUME") and os.path.exists(out):
        # 途中で止まった走りの続き: 済んだ定義はそのまま使い、門の 7 つが通っていることだけ確かめる
        prev = json.load(open(out))
        if not all(prev["gates"].get("%s_equals_run1_%s" % (k, v)) for k, v in GRID_TO_RUN1.items()):
            sys.exit("続きから回すには、前の走りで門の 7 つが通っている必要がある")
        res["gates"], res["definitions"] = prev["gates"], prev["definitions"]
        res["resumed_from_git_head"] = prev["provenance"]["git_head"]
        b0_keys = None  # 重なりは B0 の鍵が要る。続きの定義では B0 を回し直して鍵だけ取る
        ws0, _ = detect_ws(base, cfgs["W30_q0.99_net_replay"])
        b0_keys = evaluate_keys(ws0)
    for name in order:
        if only and name not in only:
            continue
        if name in res["definitions"]:
            continue
        ws, n_on = detect_ws(base, cfgs[name])
        if n_on == 0:
            stop(res, out, "門: onset が 0 の定義 " + name)
        d = evaluate(ws, D.SEED, True)
        d["onsets"] = n_on
        d["config"] = {"W": cfgs[name]["W"], "theta": list(cfgs[name]["theta"]), "rule": cfgs[name]["rule"],
                       "seg": cfgs[name]["seg"]}
        if name in GRID_TO_RUN1:
            ok = same(d, run1[GRID_TO_RUN1[name]])
            res["gates"]["%s_equals_run1_%s" % (name, GRID_TO_RUN1[name])] = ok
            if not ok:
                stop(res, out, "門: %s が 1 回目の %s と一致しない" % (name, GRID_TO_RUN1[name]))
        if name == "W30_q0.99_net_replay":
            b0_keys = d["stall_keys"]
        elif b0_keys is not None:
            d["overlap_with_B0"] = overlap(b0_keys, d["stall_keys"])
        res["definitions"][name] = finish(d)
        dump(res, out)
        print(name, "done", flush=True)
    res["summary"] = grid_summary(res["definitions"])
    dump(res, out)
    print(json.dumps({"gates": res["gates"], "summary_overall": res["summary"]["overall"]}, ensure_ascii=False))


def grid_summary(defs):
    j = {k: v for k, v in defs.items() if k != "W30_q0.99_net_replay"}
    kept = {k: v["judgement"]["kept"] for k, v in j.items()}
    n = len(kept)
    share = (sum(kept.values()) / n) if n else None
    out = {"overall": {"judged": n, "kept": sum(kept.values()), "share_kept": share,
                       "not_kept": sorted(k for k, v in kept.items() if not v)}}

    def lvl(v, axis):
        c = v["config"]
        if axis == "theta_family":
            return "quantile" if c["theta"][0] == "q" else "fixed"
        if axis == "theta":
            return "%s%g" % (c["theta"][0], c["theta"][1])
        return str(c[axis])
    for axis in ("theta_family", "W", "theta", "rule", "seg"):
        g = {}
        for k, v in j.items():
            g.setdefault(lvl(v, axis), []).append(kept[k])
        out[axis] = {}
        for lv, ks in g.items():
            nk = len(ks) - sum(ks)
            out[axis][lv] = {"n": len(ks), "kept": sum(ks), "not_kept_share": nk / len(ks),
                             "concentrated": bool(share is not None and share < 1 and
                                                  nk / len(ks) >= 2 * (1 - share))}
    reasons = {}
    for k, v in j.items():
        if kept[k]:
            continue
        jj = v["judgement"]
        reasons[k] = {"a_branches": jj["a_branches"], "b": jj["b_learners_above_changes"],
                      "b_lower_bounds": jj["b_lower_bounds"]}
    out["not_kept_reasons"] = reasons
    return out


# ---------------- K KLiCKe ----------------

def run_klicke(kwork, ref_p, out, only):
    ref = json.load(open(ref_p))
    seed = ref["seed"]
    paths = sorted(glob.glob(os.path.join(kwork, "w*.json")))
    base = [[C.k6.Writer(p)] for p in paths]
    res = {"mode": "klicke", "seed_controls_and_h1": seed, "seed_learners": X.SEED, "writers": len(base),
           "provenance": provenance(), "gates": {}, "definitions": {}}
    g = res["gates"]
    g["K1_B0_mismatch_units"] = D.k1_mismatch(base, D.B0)
    if g["K1_B0_mismatch_units"]:
        stop(res, out, "K1 が外れた")
    keys, n_b0 = {}, None
    for name, cfg in KLICKE_DEFS.items():
        if only and name not in only:
            continue
        ws, n_on = detect_ws(base, cfg)
        if name == "B0":
            n_b0 = n_on
        elif n_b0 is not None:
            g["K5_%s_onsets_differ_from_B0" % name] = n_on != n_b0
            if n_on == n_b0:
                stop(res, out, "K5 が外れた: " + name)
        d = evaluate(ws, seed, False)
        d["onsets"] = n_on
        keys[name] = d["stall_keys"]
        if name == "B0":
            r = ref["klicke"]
            g["K2_counts_equal_explore"] = d["counts"] == r["counts"]
            g["K2_h1_equal_explore"] = all(abs(d["H1"][s][e]["pooled_auc"] - r["H1"][s][e]["pooled_auc"]) <= TOL
                                           for s in SIGS for e in EPS)
            if not (g["K2_counts_equal_explore"] and g["K2_h1_equal_explore"]):
                stop(res, out, "K2 が外れた: " + json.dumps(g))
        elif "B0" in keys:
            d["overlap_with_B0"] = overlap(keys["B0"], keys[name])
        res["definitions"][name] = finish(d)
        dump(res, out)
        print(name, "done", flush=True)
    j = {k: v["judgement"] for k, v in res["definitions"].items() if k != "B0"}
    res["overall"] = {"judged": len(j), "all_kept": len(j) == 7 and all(v["kept"] for v in j.values()),
                      "not_kept": sorted(k for k, v in j.items() if not v["kept"]),
                      "b0_judgement_described": res["definitions"].get("B0", {}).get("judgement")}
    dump(res, out)
    print(json.dumps({"gates": g, "overall": res["overall"]}, ensure_ascii=False))


def main():
    mode = sys.argv[1]
    only = set(os.environ["DEFCHECK_ONLY"].split(",")) if os.environ.get("DEFCHECK_ONLY") else None
    out = sys.argv[-1]
    guard_out(out, only)
    C.pause_info = D.pause_info_key
    if mode == "length":
        run_length(*sys.argv[2:5], out, only)
    elif mode == "grid":
        run_grid(*sys.argv[2:5], out, only)
    elif mode == "klicke":
        run_klicke(*sys.argv[2:4], out, only)
    else:
        sys.exit("mode は length・grid・klicke")


if __name__ == "__main__":
    main()
