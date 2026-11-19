"""対称版の対照と選ばれた τ（conditions.md の追記「対称版の対照と選ばれた τ」・判断 34 の A と C）。
CoAuthor P15・構造 ar3。共通を倍率 1 と 0.03 で当て直し、最頻値(α) を評価する。本人の当てはめは回さず、
選ばれた τ は保存済みの対称版の値から sym_picks で選び直す。

使い方（HP Z2）: python3 -I ctrl.py <coauthor_work_obs> <raw_prefix> <bvals.pkl> <sym_vals.pkl> <ctrl_out.pkl> <out_dir> <jobs> [--run-id ID]
出力: <ctrl_out.pkl>（repo の外・人は開かない）・<out_dir>/ctrl_summary.json・ctrl_tables.md・ctrl_check.json・ctrl_timing.json。
"""
import hashlib
import json
import os
import pickle
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ab as AB  # noqa: E402
import compute as CP  # noqa: E402
import pinned4  # noqa: E402
import sym as SM  # noqa: E402
from pinned4 import H, ml  # noqa: E402

MUT = set()  # z1: 最頻値に倍率 1 の S̄ を使う・z2: 重みを τ/(N + τ) にする・z3: τ 他人の選びを記録する・
#              z4: ±∞ を除いて中央値を取る・z5: 形の比べを ≥ にする
BUDGET_HOURS = 1.5
SEED = pinned4.SEED
AR3 = ("ar", 3)
ALPHA = "0.03"
DS = "coauthor"
SYM_VALS_SHA = "8596a3c79c16377ba6239f5e79ef094b7b636e0755402ab6df1a7eae366fa32b"  # 対称版の本計算（sym_check.json）


# ---------------------------------------------------------------- 当てはめ（共通と最頻値）
def job_excl_mode(job):
    """w を除く共通（ar3・倍率 α）の評価と、その S̄ の最頻値の評価（ll_zero）。z1 は渡された倍率 1 の S̄ を使う。"""
    r = SM.job_excl_sb(job)
    sb = job["sb1"] if ("z1" in MUT and job.get("sb1") is not None) else r["sb"]
    m, zero = H.mode_of("ar", sb)
    ev = CP.eval_of(CP.writers_of(job)[job["w"]], ml.DATASETS[job["ds"]]["H"])
    return dict(ll=r["ll"], mode=ev.ll_zero(m), zero_row=bool(H.zero_row_hit(zero, ev.D)), sb=r["sb"])


# ---------------------------------------------------------------- 集計
def drop_inf(d):
    return [x for x in d if np.isfinite(x)] if "z4" in MUT else d


def tau_num(t):
    return np.inf if t == ml.INF else float(t)


def weight(n, t):
    """書き手のデータの重み N/(N + τ)（τ = ∞ は 0）。z2 は τ/(N + τ)。"""
    if t == np.inf:
        return 1.0 if "z2" in MUT else 0.0
    return t / (n + t) if "z2" in MUT else n / (n + t)


def tau_summary(picks, ntrain):
    """picks: {w: τ の鍵}・ntrain: {w: 訓練の記号の数}。τ の値ごとの人数・中央値・重み（中央値の換算と書き手ごとの中央値）。"""
    ws = sorted(picks)
    taus = sorted(tau_num(picks[w]) for w in ws)
    t_med = float(taus[(len(taus) - 1) // 2])  # 下の中央値（17 人ではちょうど真ん中・格子の値の 1 つ）
    n_med = float(np.median([ntrain[w] for w in ws]))
    return dict(counts={str(k): v for k, v in sorted(Counter(picks[w] for w in ws).items(), key=lambda kv: tau_num(kv[0]))},
                tau_median=("inf" if t_med == np.inf else t_med), n_train_median=n_med,
                weight_at_medians=weight(n_med, t_med),
                weight_median_per_writer=float(np.median([weight(ntrain[w], tau_num(picks[w])) for w in ws])))


def ctrl_cell(ws, k, R, S03, P03, M03, M1, rng):
    """対照・本人' − 最頻値(0.03)・Rs・選ばれた τ。M03・M1: {w: [全記号, 押下]}（最頻値の評価）。"""
    pj, pt = SM.sym_picks(ws, k, R, S03, P03)
    pick = pt if "z3" in MUT else pj
    selfp = lambda w: P03[w][0] if pick[w] == ml.INF else S03[w][str(k)][pick[w]][0]  # noqa: E731
    st = lambda d: ml.delta_stats(drop_inf(d), rng)  # noqa: E731
    ntrain = {w: R[w]["em"]["k"][str(k)]["n_train"] for w in ws}
    return dict(self_minus_mode03=st([selfp(w) - M03[w][0] for w in ws]),
                rs=st([selfp(w) - P03[w][0] for w in ws]),
                tau=tau_summary(pick, ntrain))


def controls(ws, P03, M03, M1, rng):
    st = lambda d: ml.delta_stats(drop_inf(d), rng)  # noqa: E731
    return dict(c03=st([M03[w][0] - P03[w][0] for w in ws]), c1x=st([M1[w][0] - P03[w][0] for w in ws]),
                mode03_neg_inf=int(sum(M03[w][0] == -np.inf for w in ws)),
                mode1_neg_inf=int(sum(M1[w][0] == -np.inf for w in ws)))


def ctrl_form(rs, c03, sm):
    """読みの形（conditions の追記）。rs・c03・sm は中央値。z5 は比べを ≥ にする。"""
    gt = (lambda a, b: a >= b) if "z5" in MUT else (lambda a, b: a > b)
    a, b = gt(rs, c03), gt(sm, 0.0)
    if a and b:
        return "上回る"
    if not a and not b:
        return "及ばない"
    return "並ぶ"


def panel_form(forms):
    return forms["5"] if forms["5"] == forms["15"] else "k で分かれる"


def write_tables(S, path):
    S = json.loads(json.dumps(ml.enc(S)))
    c = S["controls"]
    L = ["# 対称版の対照と選ばれた τ（CoAuthor P15・ar3・倍率 0.03・集計値だけ）", "",
         "対照 C03 最頻値(0.03) − 共通(0.03): %s・副 C1x 最頻値(1) − 共通(0.03): %s・最頻値の −∞: 0.03 で %d 人・1 で %d 人" % (
             AB.st(c["c03"]), AB.st(c["c1x"]), c["mode03_neg_inf"], c["mode1_neg_inf"]), "",
         "| k | Rs 本人' − 共通(0.03) | 本人' − 最頻値(0.03) | τ の中央値 | 重み（中央値の換算） | 重み（書き手ごとの中央値） | τ の人数 | 形 |",
         "|---|---|---|---|---|---|---|---|"]
    for k, C in S["cells"].items():
        t = C["tau"]
        L.append("| %s | %s | %s | %s | %.4f | %.4f | %s | %s |" % (
            k, AB.st(C["rs"]), AB.st(C["self_minus_mode03"]), t["tau_median"], t["weight_at_medians"],
            t["weight_median_per_writer"], " ".join("%s:%d" % kv for kv in t["counts"].items()), S["readings"]["k_forms"][k]))
    L += ["", "パネルの形（k = 5 と 15）: %s" % S["readings"]["panel_form"]]
    open(path, "w", newline="\n").write("\n".join(L) + "\n")


# ---------------------------------------------------------------- 本計算
def main():
    argv = sys.argv[1:]
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    coa, raw, bvals, svals, cout, out, jobs = argv[0], argv[1], argv[2], argv[3], argv[4], argv[5], int(argv[6])
    pkl = raw + "." + DS + ".pkl"
    if not all(AB.outside_repo(p) for p in (pkl, bvals, svals, cout)):
        sys.exit("書き手ごとの値が repo の中を指している")
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
    rc = json.load(open(os.path.join(out, "repro_check.json")))
    if sha(pkl) != CP.PKL_SHA[DS] or sha(bvals) != rc["bvals_sha256"] or sha(svals) != SYM_VALS_SHA:
        sys.exit("pickle・B の値・対称版の値のどれかが本計算のものと違う")
    with open(pkl, "rb") as fp:
        R = pickle.load(fp)  # 人は開かない
    with open(bvals, "rb") as fp:
        BV = pickle.load(fp)  # 人は開かない
    with open(svals, "rb") as fp:
        SV = pickle.load(fp)  # 人は開かない
    cfg = ml.DATASETS[DS]
    H_ = cfg["H"]
    members = ml.panel_members(R, cfg, {w: R[w]["n"] for w in R})
    ws = next(iter(members["P15"].values()))
    ks_fit = sorted(members["P15"])
    if any(v != ws for v in members["P15"].values()) or len(ws) != 17:
        sys.exit("P15 の書き手が k で違うか 17 人でない")
    writers, _ = ml.load(DS, coa, SEED)
    if any(len(writers[w]) != R[w]["n"] for w in R):
        sys.exit("中間のデータの単位の数が pickle と違う")
    del writers
    S03, P03 = SV[ALPHA]["self"], SV[ALPHA]["pool"]
    ck = dict(run_id=run_id, pkl_sha256=sha(pkl), bvals_sha256=sha(bvals), sym_values_sha256=sha(svals))
    # P-REPRO-SYMSUM（当てはめの前・数秒）: sym.py と同じ乱数と並べで sym_cell を当て直し、保存済みの cells と同じ
    saved = json.load(open(os.path.join(out, "sym_summary.json")))["cells"]
    rng_s = np.random.default_rng([SEED + 4, 5])
    same = []
    for k in ks_fit:
        C = json.loads(json.dumps(ml.enc(SM.sym_cell(ws, k, R, S03, P03, rng_s))))
        sv = {x: y for x, y in saved[str(k)].items() if x != "current"}
        same.append(C == sv)
    ck["p_repro_symsum"] = dict(passed=all(same), compared=len(same))
    AB.write_json(ck, os.path.join(out, "ctrl_check.json"))
    if not ck["p_repro_symsum"]["passed"]:
        sys.exit("P-REPRO-SYMSUM が外れた（選び直した対称 2 段が sym_summary と違う）。止めて報告する")
    print("P-REPRO-SYMSUM 通過", flush=True)
    T = dict(run_id=run_id)
    t0 = time.time()
    V = {}
    with ProcessPoolExecutor(jobs, initializer=ml._init, initargs=({DS: coa}, SEED, [])) as ex:
        for a in ("1", ALPHA):
            full = ex.submit(CP.job_full, dict(ds=DS, s=AR3, alpha=float(a), seed=SEED)).result()
            jl = [dict(ds=DS, w=w, start=full, alpha=float(a), sb1=(V["1"]["sb"][w] if a == ALPHA else None)) for w in ws]
            res = dict(zip(ws, ex.map(job_excl_mode, jl, chunksize=1)))
            T["pool_%s_sec" % a] = time.time() - t0
            V[a] = dict(pool={w: res[w]["ll"] for w in ws}, mode={w: res[w]["mode"] for w in ws},
                        zero_row={w: res[w]["zero_row"] for w in ws}, sb={w: res[w]["sb"] for w in ws})
            if a == "1":
                cmp = [(V[a]["mode"][w], R[w]["em"]["mode"]["ar3"]) for w in ws] + \
                      [(V[a]["pool"][w], R[w]["em"]["pool"]["ar3"]) for w in ws]
                ok = all(CP.same_bits(x, y) for x, y in cmp)
                fin = [abs(x[j] - y[j]) for x, y in cmp for j in (0, 1)
                       if x[j] is not None and y[j] is not None and np.isfinite(x[j]) and np.isfinite(y[j])]
                ck["p_repro_mode1"] = dict(passed=bool(ok), compared=len(cmp), max_abs_diff_finite=float(max(fin) if fin else 0.0))
                AB.write_json(ck, os.path.join(out, "ctrl_check.json"))
                if not ok:
                    sys.exit("P-REPRO-MODE1 が外れた（倍率 1 の最頻値か共通が mode の pickle と違う）。止めて報告する")
                print("P-REPRO-MODE1 通過（%.0f 秒）" % (time.time() - t0), flush=True)
                if (time.time() - t0) * 2 / 3600 > BUDGET_HOURS:
                    AB.write_json(T, os.path.join(out, "ctrl_timing.json"))
                    sys.exit("見積もりが 1.5 時間を超える。止めて報告する")
            else:
                cmp = [(V[a]["pool"][w], BV[DS]["pool"][w]["ar3"][ALPHA]) for w in ws] + [(V[a]["pool"][w], P03[w]) for w in ws]
                ok = all(CP.same_bits(x, y) for x, y in cmp)
                ck["p_repro_b1"] = dict(passed=bool(ok), compared=len(cmp),
                                        max_abs_diff=float(max(abs(x[0] - y[0]) for x, y in cmp)))
                AB.write_json(ck, os.path.join(out, "ctrl_check.json"))
                if not ok:
                    sys.exit("P-REPRO-B1 が外れた（倍率 0.03 の共通が B1・対称版の値と違う）。止めて報告する")
    with open(cout, "wb") as fp:
        pickle.dump({a: {x: y for x, y in V[a].items() if x != "sb"} for a in V}, fp)
    ck["ctrl_values_sha256"] = sha(cout)
    AB.write_json(ck, os.path.join(out, "ctrl_check.json"))
    AB.write_json(T, os.path.join(out, "ctrl_timing.json"))
    rng = np.random.default_rng([SEED + 4, 6])
    M03, M1 = V[ALPHA]["mode"], V["1"]["mode"]
    ctl = controls(ws, P03, M03, M1, rng)
    ctl["mode03_zero_row_hit"] = int(sum(V[ALPHA]["zero_row"].values()))
    cells = {str(k): ctrl_cell(ws, k, R, S03, P03, M03, M1, rng) for k in ks_fit}
    forms = {k: ctrl_form(C["rs"]["median"], ctl["c03"]["median"], C["self_minus_mode03"]["median"]) for k, C in cells.items()}
    S = dict(run_id=run_id, writers=len(ws), alpha=ALPHA, controls=ctl, cells=cells,
             readings=dict(k_forms=forms, panel_form=panel_form(forms)))
    AB.write_json(S, os.path.join(out, "ctrl_summary.json"))
    write_tables(S, os.path.join(out, "ctrl_tables.md"))


if __name__ == "__main__":
    main()
