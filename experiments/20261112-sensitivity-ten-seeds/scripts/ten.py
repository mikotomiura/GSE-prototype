"""計算 D: 感度の合成の種を 10 に増やす（conditions.md D1〜D5）。複製の当てはめは sens の run_rep をそのまま使う。

使い方:
  python3 -I ten.py run <seed> <out_dir> <jobs> [--run-id ID] [--budget-hours 24]   複製を回す（時間の規則つき）
  python3 -I ten.py report <out_dir> [--run-id ID]                                   summary.json・tables.md・machine_check.json
複製の値は run では要約も表示もしない（D5: 時間だけを見て削りを決める）。
"""
import glob
import hashlib
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinned5  # noqa: E402
from pinned5 import AN, RS, SY, ml  # noqa: E402

MUT = set()  # e1: U を陰性対照 15 種すべてから・e2: 検出の条件から良い側の割合を外す・e3: FA を種 0〜4 で・e4: 足す行の番号を 0 から
HERE = os.path.dirname(os.path.abspath(__file__))
U_SEEDS = list(range(5))
FA_SEEDS = list(range(5, 15))
PLANT_SEEDS = list(range(10))
LEVELS = [1e-3, 3e-3, 1e-2, 3e-2]
MAIN_K = ["5", "15"]
REAL_REMAINDER = (4.1e-4, 7.2e-4)
FIRST_NEW = 33  # sens が 0〜32 を使った


# ---------------------------------------------------------------- 計画
def plan():
    """55 行: sens の 0〜12（CoAuthor の用量の筋）と、足す 42 行（33〜74・陰性対照 5〜14 → 段の順 → 種の順）。"""
    rows = [dict(r) for r in RS.plan()[:13]]
    add = [dict(strand="dose", shape="coauthor", K=3, g=0.0, seed=s) for s in FA_SEEDS]
    for g in LEVELS:
        add += [dict(strand="dose", shape="coauthor", K=3, g=g, seed=s) for s in PLANT_SEEDS[2:]]
    base = 0 if "e4" in MUT else FIRST_NEW
    for i, r in enumerate(add):
        r["no"] = base + i
    return rows + add


def cuts(rows):
    """D5 の削り（順に）。"""
    c1 = {r["no"] for r in rows if r["g"] == 0 and r["seed"] >= 10}
    c2 = {r["no"] for r in rows if r["g"] > 0 and r["seed"] in (8, 9)}
    c3 = {r["no"] for r in rows if r["g"] > 0 and r["seed"] in (6, 7)}
    return [c1, c2, c3]


def code_hash():
    h = hashlib.sha256()
    for p in sorted(glob.glob(os.path.join(HERE, "*.py"))):
        h.update(os.path.basename(p).encode() + open(p, "rb").read())
    for f, v in sorted(pinned5.hashes().items()):
        h.update((f + v).encode())
    return h.hexdigest()


def run(seed, out, jobs, run_id, budget):
    os.makedirs(os.path.join(out, "replicates"), exist_ok=True)
    if seed != pinned5.SENS_SEED:
        sys.exit("SEED が sens と違う")
    ch = code_hash()
    cal = pinned5.calibration()
    m0s = {K: SY.make_m0(K, seed) for K in (3, 5)}
    rows = plan()
    P = dict(run_id=run_id, seed=seed, code_hash=ch, budget_hours=budget, rows=rows, reused=[], seconds={})

    def do(r):
        p = os.path.join(out, "replicates", "%02d.json" % r["no"])
        if os.path.exists(p):
            old = json.load(open(p))
            if old.get("seed") != seed or old.get("code_hash") != ch or old["rep"] != r:
                sys.exit("複製 %02d の seed・コードのハッシュ・行が今回と違う（消してからやり直す）" % r["no"])
            P["reused"].append(r["no"])
            return old["seconds"]["total"]
        R = RS.run_rep(r, cal, m0s, seed, jobs)
        R.update(run_id=run_id, seed=seed, code_hash=ch)
        json.dump(R, open(p, "w"))
        print("複製 %02d（g* %g・種 %d）%.0f 秒" % (r["no"], r["g"], r["seed"], R["seconds"]["total"]), flush=True)
        return R["seconds"]["total"]

    t1 = do(rows[0])
    keep = {r["no"] for r in rows}
    est = lambda ks: t1 * len(ks)  # noqa: E731
    P["estimate_hours_full"] = est(keep) / 3600
    applied = 0
    for c in cuts(rows):
        if est(keep) / 3600 <= budget:
            break
        keep -= c
        applied += 1
    P.update(cuts_applied=applied, estimate_hours=est(keep) / 3600, kept=sorted(keep), first_rep_seconds=t1)
    json.dump(P, open(os.path.join(out, "plan.json"), "w"), indent=1)
    print("見積もり %.1f 時間（削り %d 段）" % (P["estimate_hours"], applied), flush=True)
    if P["estimate_hours"] > budget:
        sys.exit("削りを全部当てても見積もりが %.1f 時間（予算 %.0f）。止めて研究者に聞く" % (P["estimate_hours"], budget))
    t0 = time.time()
    for r in rows:
        if r["no"] in keep:
            P["seconds"][str(r["no"])] = do(r)
    P["seconds_total_after_first"] = time.time() - t0
    json.dump(P, open(os.path.join(out, "plan.json"), "w"), indent=1)


# ---------------------------------------------------------------- 規則（D3）
def detected(c, U):
    return c["median"] > U and ("e2" in MUT or c["share"] >= 0.8)


def rule(cs):
    """cs: [{g, seed, median, share}]（1 セル）。返り値: U・FA・DR・L80 と並べる量。"""
    nulls = [c for c in cs if c["g"] == 0]
    U = max(c["median"] for c in nulls if ("e1" in MUT or c["seed"] in U_SEEDS))
    fa_set = [c for c in nulls if c["seed"] in (U_SEEDS if "e3" in MUT else FA_SEEDS)]
    out = dict(U=U, fa_n=len(fa_set), FA=float(np.mean([detected(c, U) for c in fa_set])) if fa_set else None, levels={})
    for g in LEVELS:
        lv = [c for c in cs if c["g"] == g]
        if not lv:
            continue
        ms = [c["median"] for c in lv]
        out["levels"][str(g)] = dict(n=len(lv), DR=float(np.mean([detected(c, U) for c in lv])),
                                     median_mean=float(np.mean(ms)), median_min=float(min(ms)), median_max=float(max(ms)),
                                     old_rule_seeds01=all(detected(c, U) for c in lv if c["seed"] in (0, 1)))
    ran = [g for g in LEVELS if str(g) in out["levels"]]
    out["L80"] = next((g for i, g in enumerate(ran) if all(out["levels"][str(h)]["DR"] >= 0.8 for h in ran[i:])), None)
    nm = [c["median"] for c in nulls]
    out["null"] = dict(n=len(nm), min=float(min(nm)), median=float(np.median(nm)), max=float(max(nm)),
                       above_real_low=int(sum(x > REAL_REMAINDER[0] for x in nm)),
                       above_real_high=int(sum(x > REAL_REMAINDER[1] for x in nm)))
    return out


# ---------------------------------------------------------------- report
def load_reps(out, plan_):
    reps = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(out, "replicates", "*.json")))]
    nos = [R["rep"]["no"] for R in reps]
    if len(nos) != len(set(nos)) or sorted(nos) != sorted(plan_["kept"]):
        sys.exit("複製の番号が計画の kept と一致しない")
    rows = {r["no"]: r for r in plan_["rows"]}
    if any(R["rep"] != rows[R["rep"]["no"]] for R in reps):
        sys.exit("複製の行が計画と違う")
    if {(R.get("seed"), R.get("code_hash")) for R in reps} != {(plan_["seed"], plan_["code_hash"])}:
        sys.exit("複製の seed かコードのハッシュが計画と揃っていない")
    return reps


def machine_check(out, reps):
    """P-MACHINE（記録だけ）: 番号 0〜12 の今の値と sens の Mac の値。"""
    res = []
    for R in reps:
        no = R["rep"]["no"]
        p = os.path.join(pinned5.SENS_REPS, "%02d.json" % no)
        if no > 12 or not os.path.exists(p):
            continue
        O = json.load(open(p))
        diffs = []
        for a, b in zip(R["writers"], O["writers"]):
            diffs.append(abs(a["g"] - b["g"]))
            diffs += [abs(a["pool"][s] - b["pool"][s]) for s in a["pool"]]
            for k in a["k"]:
                diffs.append(abs(a["k"][k]["r1"] - b["k"][k]["r1"]))
                diffs += [abs(a["k"][k]["self"][s][t] - b["k"][k]["self"][s][t]) for s in a["k"][k]["self"] for t in a["k"][k]["self"][s]]
        cells = {}
        for k in MAIN_K:
            ca, cb = AN.cell(R, k), AN.cell(O, k)
            cells[k] = dict(main_median_diff=ca["main"]["median"] - cb["main"]["median"],
                            same_choice_counts=ca["chosen_struct"] == cb["chosen_struct"] and ca["chosen_tau"] == cb["chosen_tau"])
        res.append(dict(no=no, max_abs_diff=float(max(diffs)), bit_same=max(diffs) == 0.0, cells=cells))
    json.dump(dict(replicates=res), open(os.path.join(out, "machine_check.json"), "w"), indent=1)


def report(out, run_id):
    plan_ = json.load(open(os.path.join(out, "plan.json")))
    if plan_.get("code_hash") != code_hash():
        sys.exit("plan.json のコードのハッシュが今のコードと違う")
    reps = load_reps(out, plan_)
    S = dict(run_id=run_id, run_ids=sorted({R.get("run_id") for R in reps}), plan=plan_, cells={})
    for k in MAIN_K + ["1"]:
        cs = []
        for R in reps:
            c = AN.cell(R, k)
            cs.append(dict(no=R["rep"]["no"], g=R["rep"]["g"], seed=R["rep"]["seed"], median=c["main"]["median"],
                           share=c["main"]["better_share"], g_median=c["g"]["median"], recovery=c["recovery"],
                           vs_r1=c["vs_r1"]["median"], chosen_tau_region=c["chosen_tau_region"]))
        S["cells"][k] = dict(replicates=cs, rule=rule(cs) if k in MAIN_K else None)
    json.dump(S, open(os.path.join(out, "summary.json"), "w"), indent=1)
    L = ["# 感度の合成を 10 種に増やした表（合成の値だけ・実データではない）", "",
         "主の量 = 2 段（他人）の本人 − 同じ構造の共通（全記号）。U = 陰性対照の種 0〜4 の中央値の最大。"
         "検出 = 中央値 > U かつ良い側の割合 ≥ 0.8。FA = 陰性対照の種 5〜14 の検出の割合。DR = 段の種 0〜9 の検出の割合。", ""]
    for k in MAIN_K:
        r = S["cells"][k]["rule"]
        L += ["## k = %s" % k, "",
              "U = %.3e・FA = %s（%d 種）・L80 = %s・陰性対照 %d 種の中央値 [%.2e, %.2e, %.2e]・実データの残りの下端を超える %d 種・上端を超える %d 種" % (
                  r["U"], "—" if r["FA"] is None else "%.2f" % r["FA"], r["fa_n"], r["L80"], r["null"]["n"], r["null"]["min"],
                  r["null"]["median"], r["null"]["max"], r["null"]["above_real_low"], r["null"]["above_real_high"]), "",
              "| 段 | 種の数 | DR | 中央値の平均 [最小, 最大] | 種 0・1 の前の規則 |", "|---|---|---|---|---|"]
        for g, v in r["levels"].items():
            L.append("| %s | %d | %.2f | %.2e [%.2e, %.2e] | %s |" % (g, v["n"], v["DR"], v["median_mean"], v["median_min"],
                                                                     v["median_max"], v["old_rule_seeds01"]))
        L.append("")
    open(os.path.join(out, "tables.md"), "w").write("\n".join(L) + "\n")
    machine_check(out, reps)


def main():
    argv = sys.argv[1:]
    run_id, budget = None, 24.0
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    if "--budget-hours" in argv:
        i = argv.index("--budget-hours"); budget = float(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if argv[0] == "run":
        run(int(argv[1]), argv[2], int(argv[3]), run_id, budget)
    else:
        report(argv[1], run_id)


if __name__ == "__main__":
    main()
