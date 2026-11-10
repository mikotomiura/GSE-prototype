"""感度の合成の本計算（conditions.md D3〜D6）。複製ごとに真の生成 → 外枠の手順（tau-extend の関数）→ 書き手ごとの値を保存。

使い方:
  python3 -I run_synth.py <seed> <out_dir> <jobs> [--run-id ID] [--budget-hours 24]
出力: <out_dir>/calibration.json・replicates/<番号>.json（合成の書き手ごとの値・実データではない）・plan.json（時間の規則）。
複製の値はこのスクリプトでは要約も表示もしない（D6: 時間だけを見て削りを決める）。
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import synth as SY  # noqa: E402
from pinned import DT, H, ml  # noqa: E402

DOSE = [1e-3, 3e-3, 1e-2, 3e-2]


def plan():
    """D5 の表を上から並べた複製の一覧。番号は表の順（削っても番号は変えない）。"""
    rows = []
    add = lambda strand, shape, K, g, seeds: rows.extend(  # noqa: E731
        dict(strand=strand, shape=shape, K=K, g=g, seed=s) for s in seeds)
    add("dose", "coauthor", 3, 0.0, range(5))
    for g in DOSE:
        add("dose", "coauthor", 3, g, range(2))
    add("dose", "cs1", 3, 0.0, range(3))
    for g in DOSE:
        add("dose", "cs1", 3, g, range(1))
    add("struct", "coauthor", 5, 0.0, range(3))
    add("struct", "coauthor", 5, 1e-2, range(2))
    add("dist", "coauthor", 3, 3e-2, range(2))
    for i, r in enumerate(rows):
        r["no"] = i
    return rows


def cuts(rows):
    """D6 の削り（順に）: 各段で落とす複製の番号の集合。"""
    c1 = {r["no"] for r in rows if r["strand"] == "dose" and r["shape"] == "cs1" and r["g"] in (1e-3, 3e-3)}
    c2 = {r["no"] for r in rows if r["strand"] == "dose" and r["shape"] == "coauthor" and r["g"] in (1e-3, 3e-2)
          and r["seed"] == 1}
    c3 = {r["no"] for r in rows if r["strand"] == "dose" and r["shape"] == "cs1" and r["g"] == 0 and r["seed"] == 2}
    return [c1, c2, c3]


# ---------------------------------------------------------------- ワーカー
_CTX = {}


def _init(ds, writers, mut, smut):
    ml.set_mut(mut)
    SY.MUT.clear()
    SY.MUT.update(smut)
    ml._W[ds] = writers
    _CTX["writers"] = writers


def fit_full(job):
    """全員の共通（構造ごと・開始点 10）。乱数 [seed + 11, 複製の番号, 構造の番号]（D3）。"""
    writers = _CTX["writers"]
    kind, K = ml.STRUCTS[job["si"]]
    seqs = ml.seqs_of(ml.pool_units(writers, job["H"]))
    rng = np.random.default_rng([job["seed"] + 11, job["no"], job["si"]])
    D = H.Batched(seqs, chunk=H.CHUNK)
    return H.fit(ml.pool_starts(kind, K, rng, seqs), D, H.base_prior(kind, K))


def fit_excl(job):
    return ml.fit_pool_excl(job)


def writer_job(job):
    t0 = time.time()
    writers = _CTX["writers"]
    w, H_ = job["w"], job["H"]
    units = writers[w]
    rng = np.random.default_rng([job["seed"] + 10, job["no"], w])
    em = ml.em_writer(units, H_, job["ks"], job["pools"], rng, structs=ml.STRUCTS, do_folds=False)
    _, test = DT.split(len(units), 1, H_)
    ev_seqs = ml.seqs_of([units[i] for i in test])
    ref = job["pools"]["ar3"][0] if "ar3" in job["pools"] else None
    g = SY.gain(job["model"], job["m0"], ev_seqs, ref=ref)
    out = dict(g=g, n_eval=em["n_eval"], pool={s: v[0] for s, v in em["pool"].items()}, k={})
    for k, rk in em["k"].items():
        out["k"][k] = dict(r1=rk["r1"][0], n_train=rk["n_train"],
                           self={s: {t: v[0] for t, v in d.items()} for s, d in rk["self"].items()})
    out["sec"] = time.time() - t0
    return out


def run_rep(r, cal, m0s, seed, jobs, mut=(), smut=()):
    """1 複製。返り値: 書き手ごとの値（パネルだけ）と時間。"""
    t0 = time.time()
    sh = SY.SHAPES[r["shape"]]
    lam = cal[r["K"]][str(r["g"])]["lam"] if r["g"] > 0 else 0.0
    writers, models, lams, P = SY.build(r["shape"], r["K"], r["seed"], SY.lam_rule(r["strand"], lam), m0s[r["K"]], seed)
    ds, H_ = sh["ds"], sh["H"]
    ex = ProcessPoolExecutor(jobs, initializer=_init, initargs=(ds, writers, sorted(mut), sorted(smut)))
    full = list(ex.map(fit_full, [dict(si=si, seed=seed, no=r["no"], H=H_) for si in range(len(ml.STRUCTS))]))
    pj = [dict(ds=ds, w=w, start=full[si][0]) for w in range(P) for si in range(len(ml.STRUCTS))]
    pres = list(ex.map(fit_excl, pj, chunksize=1))
    pools, it = {}, iter(pres)
    for w in range(P):
        pools[w] = {}
        for s in ml.STRUCTS:
            m, sb, _ = next(it)
            pools[w][ml.sname(s)] = (m, sb)
    t1 = time.time()
    wj = [dict(w=w, H=H_, ks=sh["ks"], pools=pools[w], seed=seed, no=r["no"], model=models[w], m0=m0s[r["K"]])
          for w in range(P)]
    res = list(ex.map(writer_job, wj, chunksize=1))
    ex.shutdown()
    return dict(rep=r, lam=lam, lams=lams[:P], planted=[bool(x > 0) for x in lams[:P]], writers=res,
                pool_full_diag={ml.sname(s): dict(winner=d["winner"], nonconv=d["nonconv"])
                                for s, (_, d) in zip(ml.STRUCTS, full)},
                seconds=dict(pools=t1 - t0, writers=time.time() - t1, total=time.time() - t0))


def calibrate_all(seed, path):
    if os.path.exists(path):
        return {int(k): v for k, v in json.load(open(path)).items()}
    m0s = {K: SY.make_m0(K, seed) for K in (3, 5)}
    cal = {3: {}, 5: {}}
    for g in DOSE:
        cal[3][str(g)] = SY.calibrate(m0s[3], g, seed)
    cal[5][str(1e-2)] = SY.calibrate(m0s[5], 1e-2, seed)
    json.dump(cal, open(path, "w"), indent=1)
    return cal


def main():
    argv = sys.argv[1:]
    run_id, budget = None, 24.0
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    if "--budget-hours" in argv:
        i = argv.index("--budget-hours"); budget = float(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    seed, out, jobs = int(argv[0]), argv[1], int(argv[2])
    os.makedirs(os.path.join(out, "replicates"), exist_ok=True)
    t0 = time.time()
    cal = calibrate_all(seed, os.path.join(out, "calibration.json"))
    bad = [(K, g) for K in cal for g, c in cal[K].items() if not c["ok"]]
    if bad:
        sys.exit("較正が目標の ±10% に入らない（止めて逸脱として書く）: %r" % bad)
    m0s = {K: SY.make_m0(K, seed) for K in (3, 5)}
    rows = plan()
    P = dict(run_id=run_id, calibration_seconds=time.time() - t0, budget_hours=budget, rows=len(rows))

    def do(r):
        p = os.path.join(out, "replicates", "%02d.json" % r["no"])
        if os.path.exists(p):
            return json.load(open(p))["seconds"]["total"]
        R = run_rep(r, cal, m0s, seed, jobs)
        R["run_id"] = run_id
        json.dump(R, open(p, "w"))
        print("複製 %02d（%s・%s）%.0f 秒" % (r["no"], r["strand"], r["shape"], R["seconds"]["total"]), flush=True)
        return R["seconds"]["total"]

    # D6: CoAuthor と CS1 の最初の複製の時間で見積もり、24 時間を超えるなら順に削る
    first_co = next(r for r in rows if r["shape"] == "coauthor")
    first_cs = next(r for r in rows if r["shape"] == "cs1")
    tco, tcs = do(first_co), do(first_cs)
    keep = {r["no"] for r in rows}
    est = lambda ks: P["calibration_seconds"] + sum(tco if rows[n]["shape"] == "coauthor" else tcs for n in ks)  # noqa: E731
    P["estimate_hours_full"] = est(keep) / 3600
    applied = 0
    for c in cuts(rows):
        if est(keep) / 3600 <= budget:
            break
        keep -= c
        applied += 1
    P.update(cuts_applied=applied, estimate_hours=est(keep) / 3600, kept=sorted(keep),
             per_rep_seconds=dict(coauthor=tco, cs1=tcs))
    json.dump(P, open(os.path.join(out, "plan.json"), "w"), indent=1)
    print("見積もり %.1f 時間（削り %d 段）" % (P["estimate_hours"], applied), flush=True)
    for r in rows:
        if r["no"] in keep:
            do(r)
    P["seconds_total"] = time.time() - t0
    json.dump(P, open(os.path.join(out, "plan.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
