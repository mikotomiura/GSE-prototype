"""計算 (f): 実データの共通そのものを真の生成にした帰無（conditions.md D2〜D5）。合成の値だけを扱う。

使い方:
  python3 -I null.py gate   <seed> <m0.npz> <m0_fit.json> <out_dir> <jobs> [--run-id ID]   門（α を 1 つ選ぶ）
  python3 -I null.py run    <seed> <m0.npz> <m0_fit.json> <out_dir> <jobs> [--run-id ID] [--budget-hours 24]
  python3 -I null.py report <out_dir> [--run-id ID]
run は門を通った α の m0 で、較正 → D と同じ 55 本の複製（sens の run_rep をそのまま）を回す。
gate と run は複製の主の量を要約も表示もしない。門で止まるときは exit 5。
"""
import glob
import hashlib
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinned6  # noqa: E402
from pinned6 import AN, DC, DT, HM, RS, SY, TEN, ml  # noqa: E402

MUT = set()  # n1: 符号だけで大きい α から・n2: b = 共通 − 最頻値・n3: 門の種を 0〜2 に・n4: 実データを ar3 固定の行から・
#              n5: build に sens の make_m0・n6: −∞ を中央値から除く・n7: 規則が使える条件から FA' ≤ 0.2 を外す
HERE = os.path.dirname(os.path.abspath(__file__))
ALPHAS = ["1", "0.3", "0.1", "0.03"]
GATE_SEEDS = [100, 101, 102]
GATE_NO0 = 200
REAL_B = 7.4e-4          # mode の notes 89 行（CoAuthor P15・ar3・主の b）
AR3 = ("ar", 3)
MAIN_K = ["5", "15"]
FA_MAX = 0.2
KEYS = ("pi", "A", "H", "C")
SEED_WANT = 2026111001
EXIT_GATE_STOP = 5


class GateStop(Exception):
    pass


# ---------------------------------------------------------------- m0
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_m0(npz, m0_json):
    """npz の SHA-256 を m0_fit.json と照らし、{α: 母数}。値は表示しない。"""
    J = json.load(open(m0_json))
    if sha(npz) != J["npz_sha256"] or J["alphas"] != ALPHAS:
        sys.exit("m0 の npz の SHA-256 か倍率の一覧が m0_fit.json と違う")
    Z = np.load(npz)
    return {a: dict(kind="ar", **{k: np.array(Z["a%s_%s" % (a, k)]) for k in KEYS}) for a in ALPHAS}, J["npz_sha256"]


def m0_ok(m):
    """P-M0: K = 3・kind ar・有限・非負・行の和が 1（1e-9 以内）。"""
    try:
        K = len(m["pi"])
        shp = dict(pi=(K,), A=(K, K), H=(K, SY.NSYM), C=(K, SY.NSYM, SY.NSYM))
        return bool(K == 3 and m["kind"] == "ar" and all(np.shape(m[k]) == shp[k] for k in KEYS)
                    and all(np.isfinite(m[k]).all() and (m[k] >= 0).all() for k in KEYS)
                    and all(np.abs(m[k].sum(-1) - 1).max() <= 1e-9 for k in KEYS))
    except (KeyError, TypeError, ValueError):
        return False


def m0_for_build(m0, seed):
    return SY.make_m0(3, seed) if "n5" in MUT else m0


def m0s_for_run(m0, seed):
    return {3: m0_for_build(m0, seed)}


# ---------------------------------------------------------------- 門（D2）
def gate_seeds():
    return [0, 1, 2] if "n3" in MUT else list(GATE_SEEDS)


def gate_no(ai, si):
    return GATE_NO0 + 3 * ai + si


def null_writers(shape, gseed, m0, seed):
    """差 0 の合成（sens の build・筋 dose・λ = 0）。"""
    return SY.build(shape, 3, gseed, SY.lam_rule("dose", 0.0), m0_for_build(m0, seed), seed)


def b_of(mode_v, pool_v):
    return pool_v - mode_v if "n2" in MUT else mode_v - pool_v


def b_median(bs):
    """−∞ の書き手を −∞ として入れた中央値（n6 は除く）。"""
    xs = [b for b in bs if np.isfinite(b)] if "n6" in MUT else list(bs)
    return float(np.median(np.asarray(xs, dtype=float)))


def gate_b(m0, gseed, no, seed, jobs, shape="coauthor", detail=False):
    """1 本の門: ar3 の全員の共通 → w を除く共通（パネル）→ 書き手ごとの b_w = 最頻値 − 共通（評価の単位・全記号）。"""
    sh = SY.SHAPES[shape]
    assert sh["H"] == ml.DATASETS[sh["ds"]]["H"]
    writers, models, lams, P = null_writers(shape, gseed, m0, seed)
    ds, H_ = sh["ds"], sh["H"]
    si = ml.STRUCTS.index(AR3)
    with ProcessPoolExecutor(jobs, initializer=RS._init, initargs=(ds, writers, [], [])) as ex:
        full_m, full_d = list(ex.map(RS.fit_full, [dict(si=si, seed=seed, no=no, H=H_)]))[0]
        pres = list(ex.map(RS.fit_excl, [dict(ds=ds, w=w, start=full_m) for w in range(P)], chunksize=1))
    bs, parts = [], []
    for w in range(P):
        m, sb, _ = pres[w]
        units = writers[w]
        _, test = DT.split(len(units), 1, H_)
        ev_units = [units[i] for i in test]
        ev_seqs = ml.seqs_of(ev_units)
        pool_v = ml.Eval(ev_seqs, ml.pflags_of(ev_units)).ll(m)[0]
        mode_v = DC.mode_eval(HM.mode_of("ar", sb)[0], ev_seqs)
        bs.append(b_of(mode_v, pool_v))
        if detail:
            parts.append(dict(m=m, sb=sb, ev_seqs=ev_seqs, ev_units=ev_units, pool=pool_v, mode=mode_v))
    out = dict(b=[float(x) for x in bs], median=b_median(bs), n_neg_inf=int(sum(np.isneginf(bs))),
               share_pos=float(np.mean(np.asarray(bs) > 0)), n=P,
               full_diag=dict(winner=full_d["winner"], nonconv=full_d["nonconv"]))
    if detail:
        out["parts"] = parts
        out["writers"] = writers
        out["models"] = models
    return out


def pick_alpha(G):
    """D2 の選び。G: {α: {"b_s": [3 種の中央値]}}。返り値: α。通る α が無ければ GateStop。"""
    ok = [a for a in ALPHAS if a in G and len(G[a]["b_s"]) == len(GATE_SEEDS) and all(x > 0 for x in G[a]["b_s"])]
    if not ok:
        raise GateStop("3 種とも b > 0 の倍率が無い")
    if "n1" in MUT:
        return ok[0]
    key = lambda a: (abs(math.log(float(np.median(G[a]["b_s"])) / REAL_B)), -float(a))  # noqa: E731
    return min(ok, key=key)


def code_hash():
    h = hashlib.sha256()
    for p in sorted(glob.glob(os.path.join(HERE, "*.py"))):
        h.update(os.path.basename(p).encode() + open(p, "rb").read())
    for f, v in sorted(pinned6.hashes().items()):
        h.update((f + v).encode())
    return h.hexdigest()


def write_json(obj, path):
    with open(path, "w", newline="\n") as f:
        json.dump(obj, f, indent=1)


def gate(seed, npz, m0_json, out, jobs, run_id):
    """gate.json を書き、選ばれた α を返す（止まるときは None）。既にあれば seed・コード・m0 を照らして読む。"""
    os.makedirs(out, exist_ok=True)
    m0s, m0_sha = load_m0(npz, m0_json)
    if not all(m0_ok(m0s[a]) for a in ALPHAS):
        sys.exit("P-M0: 読んだ m0 の形か行の和が条件と違う")
    ch = code_hash()
    p = os.path.join(out, "gate.json")
    if os.path.exists(p):
        old = json.load(open(p))
        if old.get("seed") != seed or old.get("code_hash") != ch or old.get("m0_sha256") != m0_sha:
            sys.exit("gate.json の seed・コード・m0 が今回と違う（消してからやり直す）")
        return old["chosen"]
    G = dict(run_id=run_id, seed=seed, code_hash=ch, m0_sha256=m0_sha, real_b=REAL_B, seeds=gate_seeds(), alphas={})
    t0 = time.time()
    for ai, a in enumerate(ALPHAS):
        G["alphas"][a] = dict(per_seed=[], b_s=[])
        for si, gs in enumerate(gate_seeds()):
            t1 = time.time()
            r = gate_b(m0s[a], gs, gate_no(ai, si), seed, jobs)
            r.update(gate_seed=gs, no=gate_no(ai, si), seconds=time.time() - t1)
            G["alphas"][a]["per_seed"].append(r)
            G["alphas"][a]["b_s"].append(r["median"])
            print("門 α %s・種 %d %.0f 秒" % (a, gs, r["seconds"]), flush=True)
        G["alphas"][a]["b_bar"] = float(np.median(G["alphas"][a]["b_s"]))
        G["alphas"][a]["all_positive"] = all(x > 0 for x in G["alphas"][a]["b_s"])
    try:
        G["chosen"] = pick_alpha(G["alphas"])
    except GateStop as e:
        G["chosen"], G["stop_reason"] = None, str(e)
    G["seconds"] = time.time() - t0
    write_json(G, p)
    return G["chosen"]


# ---------------------------------------------------------------- 本計算（D3）
def plan():
    return TEN.plan()


def calibrate(m0, seed, path, ch, m0_sha, alpha):
    if os.path.exists(path):
        d = json.load(open(path))
        if d.get("seed") != seed or d.get("code_hash") != ch or d.get("m0_sha256") != m0_sha or d.get("alpha") != alpha:
            sys.exit("calibration.json の seed・コード・m0・α が今回と違う（消してからやり直す）")
        return {int(k): v for k, v in d["cal"].items()}
    t0 = time.time()
    cal = {3: {str(g): SY.calibrate(m0, g, seed) for g in TEN.LEVELS}}
    write_json(dict(seed=seed, code_hash=ch, m0_sha256=m0_sha, alpha=alpha, cal=cal, seconds=time.time() - t0), path)
    return cal


def run(seed, npz, m0_json, out, jobs, run_id, budget):
    if seed != SEED_WANT:
        sys.exit("SEED が条件の値と違う")
    alpha = gate(seed, npz, m0_json, out, jobs, run_id)
    if alpha is None:
        print("門で止まった（3 種とも b > 0 の倍率が無い）。本計算に入らない。研究者に聞く", flush=True)
        sys.exit(EXIT_GATE_STOP)
    m0s, m0_sha = load_m0(npz, m0_json)
    m0 = m0s[alpha]
    ch = code_hash()
    cal = calibrate(m0, seed, os.path.join(out, "calibration.json"), ch, m0_sha, alpha)
    bad = [g for g, c in cal[3].items() if not c["ok"]]
    if bad:
        sys.exit("較正が目標の ±10% に入らない（止めて逸脱として書く）: %r" % bad)
    os.makedirs(os.path.join(out, "replicates"), exist_ok=True)
    rows = plan()
    P = dict(run_id=run_id, seed=seed, code_hash=ch, m0_sha256=m0_sha, alpha=alpha, budget_hours=budget, rows=rows,
             reused=[], seconds={})
    m0s_run = m0s_for_run(m0, seed)

    def do(r):
        p = os.path.join(out, "replicates", "%02d.json" % r["no"])
        if os.path.exists(p):
            old = json.load(open(p))
            if (old.get("seed") != seed or old.get("code_hash") != ch or old["rep"] != r or old.get("m0_sha256") != m0_sha
                    or old.get("alpha") != alpha):
                sys.exit("複製 %02d の seed・コード・行・m0・α が今回と違う（消してからやり直す）" % r["no"])
            P["reused"].append(r["no"])
            return old["seconds"]["total"]
        R = RS.run_rep(r, cal, m0s_run, seed, jobs)
        R.update(run_id=run_id, seed=seed, code_hash=ch, m0_sha256=m0_sha, alpha=alpha)
        write_json(R, p)
        print("複製 %02d（g* %g・種 %d）%.0f 秒" % (r["no"], r["g"], r["seed"], R["seconds"]["total"]), flush=True)
        return R["seconds"]["total"]

    t1 = do(rows[0])
    keep = {r["no"] for r in rows}
    est = lambda ks: t1 * len(ks)  # noqa: E731
    P["estimate_hours_full"] = est(keep) / 3600
    applied = 0
    for c in TEN.cuts(rows):
        if est(keep) / 3600 <= budget:
            break
        keep -= c
        applied += 1
    P.update(cuts_applied=applied, estimate_hours=est(keep) / 3600, kept=sorted(keep), first_rep_seconds=t1)
    write_json(P, os.path.join(out, "plan.json"))
    print("見積もり %.1f 時間（削り %d 段）" % (P["estimate_hours"], applied), flush=True)
    if P["estimate_hours"] > budget:
        sys.exit("削りを全部当てても見積もりが %.1f 時間（予算 %.0f）。止めて研究者に聞く" % (P["estimate_hours"], budget))
    t0 = time.time()
    P["seconds"][str(rows[0]["no"])] = t1
    for r in rows[1:]:  # 最初の 1 本は見積もりで回した（もう一度 do に通すと「再利用」に数えてしまう）
        if r["no"] in keep:
            P["seconds"][str(r["no"])] = do(r)
    P["seconds_total_after_first"] = time.time() - t0
    write_json(P, os.path.join(out, "plan.json"))


# ---------------------------------------------------------------- 読み（D4・D5）
def read_real():
    """実データの残り（2 段〔他人〕の 本人 − 同じ構造の共通・P15）。n4 は ar の k_cv の行から読む。"""
    S = json.load(open(pinned6.MODE_SUMMARY))
    out = {}
    for k in MAIN_K:
        e = S["datasets"]["coauthor"]["em"]["P15"][k]
        v = e["kcv"]["ar"]["k_cv"] if "n4" in MUT else e["two_stage"]["other"]["two_stage_other"]
        v = v["all/self_minus_pool_same"]
        out[k] = dict(median=float(v["median"]), share=float(v["better_share"]), n=int(v["n"]))
    return out


def reading(rules, real):
    """D5 の場合分け。rules: {k: ten.rule の返り値}、real: {k: {median, share}}。"""
    per = {}
    for k in MAIN_K:
        r = rules[k]
        usable = True if "n7" in MUT else (r["FA"] is not None and r["FA"] <= FA_MAX)
        per[k] = dict(usable=bool(usable), detected=bool(TEN.detected(real[k], r["U"])), U=r["U"], FA=r["FA"],
                      L80=r["L80"], real_median=real[k]["median"], real_share=real[k]["share"])
    if all(per[k]["usable"] for k in MAIN_K) and all(per[k]["detected"] for k in MAIN_K):
        case = "R1"
    elif all(per[k]["usable"] for k in MAIN_K) and not any(per[k]["detected"] for k in MAIN_K):
        case = "R2"
    else:
        case = "R3"
    return dict(case=case, per_k=per)


def d_pair(reps, k):
    """並べるだけ: D の同じ番号の複製との主の量の中央値の差（新 − D）の中央値と範囲。"""
    ds = []
    for R in reps:
        p = os.path.join(pinned6.D_REPS, "%02d.json" % R["rep"]["no"])
        if not os.path.exists(p):
            continue
        O = json.load(open(p))
        if O["rep"] != R["rep"]:
            continue
        ds.append(AN.cell(R, k)["main"]["median"] - AN.cell(O, k)["main"]["median"])
    if not ds:
        return None
    return dict(n=len(ds), median=float(np.median(ds)), min=float(min(ds)), max=float(max(ds)))


def report(out, run_id):
    plan_ = json.load(open(os.path.join(out, "plan.json")))
    if plan_.get("code_hash") != code_hash():
        sys.exit("plan.json のコードのハッシュが今のコードと違う")
    G = json.load(open(os.path.join(out, "gate.json")))
    if G.get("chosen") != plan_.get("alpha") or G.get("m0_sha256") != plan_.get("m0_sha256"):
        sys.exit("gate.json と plan.json の α か m0 が違う")
    reps, extra = TEN.load_reps(out, plan_)
    if {(R.get("m0_sha256"), R.get("alpha")) for R in reps} != {(plan_["m0_sha256"], plan_["alpha"])}:
        sys.exit("複製の m0 か α が計画と揃っていない")
    real = read_real()
    S = dict(run_id=run_id, run_ids=sorted({R.get("run_id") for R in reps}), alpha=plan_["alpha"], m0_sha256=plan_["m0_sha256"],
             gate={a: dict(b_s=v["b_s"], b_bar=v["b_bar"], all_positive=v["all_positive"],
                           n_neg_inf=[s["n_neg_inf"] for s in v["per_seed"]], share_pos=[s["share_pos"] for s in v["per_seed"]])
                   for a, v in G["alphas"].items()},
             real=real, plan=plan_, extra_files_not_in_plan=extra, cells={})
    for k in MAIN_K + ["1"]:
        cs = []
        for R in reps:
            c = AN.cell(R, k)
            cs.append(dict(no=R["rep"]["no"], g=R["rep"]["g"], seed=R["rep"]["seed"], median=c["main"]["median"],
                           share=c["main"]["better_share"], g_median=c["g"]["median"], recovery=c["recovery"],
                           vs_r1=c["vs_r1"]["median"], chosen_tau_region=c["chosen_tau_region"]))
        S["cells"][k] = dict(replicates=cs, rule=TEN.rule(cs) if k in MAIN_K else None,
                             d_pair=d_pair(reps, k) if k in MAIN_K else None)
    S["reading"] = reading({k: S["cells"][k]["rule"] for k in MAIN_K}, real)
    write_json(S, os.path.join(out, "summary.json"))
    L = ["# 共通のモデルそのものから作った帰無の表（合成の値だけ・実データの値は残りの中央値と良い側の割合だけ）", "",
         "真の生成 = 実データの CoAuthor の全員の共通 ar3（基の倍率 α = %s・門で選んだ）。主の量 = 2 段（他人）の本人 − 同じ構造の共通（全記号）。"
         "U' = 陰性対照の種 0〜4 の中央値の最大。検出 = 中央値 > U' かつ良い側の割合 ≥ 0.8。FA' = 種 5〜14 の検出の割合。" % plan_["alpha"], "",
         "## 門（b = 最頻値 − 共通・ar3・17 人の中央値・実データは +7.4e-4）", "",
         "| α | 種 100・101・102 の b | 3 種の中央値 | 3 種とも正 | −∞ の人数 |", "|---|---|---|---|---|"]
    for a, v in S["gate"].items():
        L.append("| %s | %s | %.2e | %s | %s |" % (a, "・".join("%.2e" % x for x in v["b_s"]), v["b_bar"], v["all_positive"],
                                                 "・".join(str(x) for x in v["n_neg_inf"])))
    L += ["", "読みの場合: **%s**" % S["reading"]["case"], ""]
    for k in MAIN_K:
        r, pk, dp = S["cells"][k]["rule"], S["reading"]["per_k"][k], S["cells"][k]["d_pair"]
        L += ["## k = %s" % k, "",
              "U' = %.3e・FA' = %s（%d 種）・L80' = %s・規則が使える %s・実データ %.3e（良 %.2f）の検出 %s" % (
                  r["U"], "—" if r["FA"] is None else "%.2f" % r["FA"], r["fa_n"], r["L80"], pk["usable"],
                  pk["real_median"], pk["real_share"], pk["detected"]),
              "陰性対照 %d 種の中央値 [%.2e, %.2e, %.2e]・実データの残りの下端を超える %d 種・上端を超える %d 種" % (
                  r["null"]["n"], r["null"]["min"], r["null"]["median"], r["null"]["max"], r["null"]["above_real_low"],
                  r["null"]["above_real_high"]),
              "D の同じ番号の複製との差（新 − D）: %s" % ("—" if dp is None else "中央値 %.2e [%.2e, %.2e]（%d 本）" % (
                  dp["median"], dp["min"], dp["max"], dp["n"])), "",
              "| 段 | 種の数 | DR' | 中央値の平均 [最小, 最大] |", "|---|---|---|---|"]
        for g, v in r["levels"].items():
            L.append("| %s | %d | %.2f | %.2e [%.2e, %.2e] |" % (g, v["n"], v["DR"], v["median_mean"], v["median_min"], v["median_max"]))
        L.append("")
    with open(os.path.join(out, "tables.md"), "w", newline="\n") as f:
        f.write("\n".join(L) + "\n")


def main():
    argv = sys.argv[1:]
    run_id, budget = None, 24.0
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    if "--budget-hours" in argv:
        i = argv.index("--budget-hours"); budget = float(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if argv[0] == "gate":
        a = gate(int(argv[1]), argv[2], argv[3], argv[4], int(argv[5]), run_id)
        print("門: %s" % ("α = " + a if a else "止まる"), flush=True)
        sys.exit(0 if a else EXIT_GATE_STOP)
    if argv[0] == "run":
        run(int(argv[1]), argv[2], argv[3], argv[4], int(argv[5]), run_id, budget)
    else:
        report(argv[1], run_id)


if __name__ == "__main__":
    main()
