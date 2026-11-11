"""計算 B の書き手ごとの値を作る（conditions.md D1・D4・D5）。本人の当てはめは回さない。

- P-REPRO: mode の pickle に mode の summarize_em を当て直し、mode の summary.json の em と JSON として同じ（外れれば止める）。
- B2: 本人の連鎖 r1(β)（CoAuthor と CS1・主のパネルの書き手 × k × β）。β = 0.5 が pickle の r1 とビットまで同じ（P-REPRO-R1）。
- B1: 共通の基の擬似度数 α 倍（CoAuthor だけ・P15 の書き手 × 構造 × α）。α = 1 を先に回し、pickle の pool とビットまで同じ（P-REPRO-POOL）。

使い方（HP Z2）: python3 -I compute.py <coauthor_work_obs> <cs1_work_obs> <raw_prefix> <bvals_out.pkl> <out_dir> <jobs> [--run-id ID]
出力: <bvals_out.pkl>（repo の外・人は開かない）・<out_dir>/repro_check.json・timing.json。
"""
import hashlib
import json
import os
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ab as AB  # noqa: E402
import pinned4  # noqa: E402
from pinned4 import H, ml  # noqa: E402

DT = ml.DT
MUT = set()  # s4: 基の倍率を放出のキーにだけ掛ける・s7: β を遷移にだけ足す（頭は 0.5 のまま）
SEED = pinned4.SEED
EMIS = {"B", "H", "C"}
PKL_SHA = {"coauthor": "a0d3627e281191a42e23d186034de79419931f73c02964f52e17d830d488f94c",   # mode の本計算の pickle
           "cs1": "08cdd31e567b164397473dbb0531a16f7b11729070317b78c0c9c6510d8bf7e6"}      # （mode-in-selection の provenance）
BUDGET_B1_HOURS = 6.0
ALPHA_CUTS = ["3", "0.03"]  # V2 の削る順


def set_mut(mut):
    MUT.clear()
    MUT.update(m for m in mut if m in ("s4", "s7"))
    AB.MUT.clear()
    AB.MUT.update(m for m in mut if m not in ("s4", "s7"))


# ---------------------------------------------------------------- 部品
def prior_alpha(kind, K, alpha):
    """基の擬似度数の全セル × α（D4）。s4 は放出のキーにだけ掛ける。"""
    pr = H.base_prior(kind, K)
    return {k: (v * alpha if ("s4" not in MUT or k in EMIS) else v) for k, v in pr.items()}


def r1_beta(seqs, beta):
    """hmm2.r0_r1 と同じ数え方の r1（頭の記号の頻度と 1 次の遷移）に β を足す（D5）。s7 は頭を 0.5 のまま。"""
    h = np.full(H.NSYM, 0.5 if "s7" in MUT else beta)
    T = np.full((H.NSYM, H.NSYM), beta)
    for s in seqs:
        s = np.asarray(s, dtype=np.int64)
        if len(s) == 0:
            continue
        h[s[0]] += 1
        np.add.at(T, (s[:-1], s[1:]), 1)
    return h / h.sum(), T / T.sum(1, keepdims=True)


def eval_of(units, H_):
    _, test = DT.split(len(units), 1, H_)
    return ml.Eval(ml.seqs_of([units[i] for i in test]), ml.pflags_of([units[i] for i in test]))


def writers_of(job):
    return job["writers"] if job.get("writers") is not None else ml._W[job["ds"]]


def job_full(job):
    """全員の共通（構造 × α）。mode の fit_pool_full と同じ単位・開始点・乱数 [SEED + 11, SEQ_NO]。"""
    writers = writers_of(job)
    kind, K = job["s"]
    seqs = ml.seqs_of(ml.pool_units(writers, ml.DATASETS[job["ds"]]["H"]))
    rng = np.random.default_rng([job["seed"] + 11, ml.SEQ_NO[job["s"]]])
    D = H.Batched(seqs, chunk=H.CHUNK)
    m, _ = H.fit(ml.pool_starts(kind, K, rng, seqs), D, prior_alpha(kind, K, job["alpha"]))
    return m


def job_excl(job):
    """w を除く共通（開始点は同じ α の全員の共通の解）と、w の評価の単位での評価 [全記号, 押下]。"""
    writers = writers_of(job)
    H_ = ml.DATASETS[job["ds"]]["H"]
    m0 = job["start"]
    kind, K = m0["kind"], len(m0["pi"])
    seqs = ml.seqs_of(ml.pool_units(writers, H_, exclude=job["w"]))
    D = H.Batched(seqs, chunk=H.CHUNK)
    m, _ = H.fit([("full_pool", m0)], D, prior_alpha(kind, K, job["alpha"]))
    out = dict(ll=eval_of(writers[job["w"]], H_).ll(m))
    if job.get("keep_model"):
        out["m"] = m
    return out


def r1_values(writers, ws, ks_of, H_):
    """{w: {k: {β: [全記号, 押下]}}}。"""
    RV = {}
    for w in ws:
        units = writers[w]
        ev = eval_of(units, H_)
        RV[w] = {}
        for k in ks_of(w):
            train, _ = DT.split(len(units), k, H_)
            tr = ml.seqs_of([units[i] for i in train])
            RV[w][str(k)] = {b: ev.ll_r1(*r1_beta(tr, float(b))) for b in AB.BETAS}
    return RV


def pool_values(ds, path, ws, alphas, jobs, writers=None):
    """{w: {構造名: {α: [全記号, 押下]}}}（α の順に回す）。"""
    init = dict(initializer=ml._init, initargs=({ds: path}, SEED, [])) if writers is None else {}
    PV = {w: {n: {} for n in AB.SN} for w in ws}
    with ProcessPoolExecutor(jobs, **init) as ex:
        for a in alphas:
            full = list(ex.map(job_full, [dict(ds=ds, s=s, alpha=float(a), seed=SEED, writers=writers) for s in ml.STRUCTS]))
            pj = [dict(ds=ds, w=w, start=full[si], alpha=float(a), writers=writers) for w in ws for si in range(len(ml.STRUCTS))]
            it = iter(ex.map(job_excl, pj, chunksize=1))
            for w in ws:
                for s in ml.STRUCTS:
                    PV[w][ml.sname(s)][a] = next(it)["ll"]
    return PV


def same_bits(a, b):
    """[全記号, 押下] がビットまで同じ（長さも・None は None とだけ・レビューの指摘 3）。"""
    if len(a) != len(b) or len(a) != 2:
        return False
    return all((x is None and y is None) or (x is not None and y is not None and np.float64(x).tobytes() == np.float64(y).tobytes())
               for x, y in zip(a, b))


def repro(results, ds):
    cfg = ml.DATASETS[ds]
    ns = {w: results[w]["n"] for w in results}
    got = json.loads(json.dumps(ml.enc(ml.summarize_em(results, cfg, ns, np.random.default_rng(SEED + 4))), allow_nan=False))
    want = json.load(open(pinned4.MODE_SUMMARY))["datasets"][ds]["em"]
    return got == want


# ---------------------------------------------------------------- 本計算
def main():
    argv = sys.argv[1:]
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    coa, cs1, raw, bout, out, jobs = argv[0], argv[1], argv[2], argv[3], argv[4], int(argv[5])
    if not all(AB.outside_repo(p) for p in (raw + ".coauthor.pkl", raw + ".cs1.pkl", bout)):
        sys.exit("書き手ごとの値が repo の中を指している")
    os.makedirs(out, exist_ok=True)
    rc = dict(run_id=run_id, pkl_sha256={}, p_repro={}, p_repro_r1={}, p_repro_pool=None)
    T = dict(run_id=run_id)
    dump = lambda: AB.write_json(rc, os.path.join(out, "repro_check.json"))  # noqa: E731
    BV = {}
    paths = {"coauthor": coa, "cs1": cs1}
    for ds in ("coauthor", "cs1"):
        t0 = time.time()
        p = raw + "." + ds + ".pkl"
        rc["pkl_sha256"][ds] = hashlib.sha256(open(p, "rb").read()).hexdigest()
        dump()
        if rc["pkl_sha256"][ds] != PKL_SHA[ds]:
            sys.exit("mode の pickle の SHA-256 が条件の値と違う（%s）" % ds)
        with open(p, "rb") as fp:
            results = pickle.load(fp)  # mode の本計算が書いた自前の pickle（人は開かない）
        rc["p_repro"][ds] = repro(results, ds)
        dump()
        if not rc["p_repro"][ds]:
            sys.exit("P-REPRO が外れた（%s）" % ds)
        cfg = ml.DATASETS[ds]
        H_ = cfg["H"]
        writers, _ = ml.load(ds, paths[ds], SEED)
        if any(len(writers[w]) != results[w]["n"] for w in results):
            sys.exit("中間のデータの単位の数が pickle と違う（%s）" % ds)
        ns = {w: results[w]["n"] for w in results}
        members = ml.panel_members(results, cfg, ns)
        ws = sorted({w for pn in AB.MAIN_PANELS[ds] for w in next(iter(members[pn].values()))})
        ks = sorted({k for pn in AB.MAIN_PANELS[ds] for k in members[pn]})
        ks_of = lambda w: [k for k in ks if str(k) in results[w]["em"]["k"]]  # noqa: E731
        RV = r1_values(writers, ws, ks_of, H_)
        cmp = [(RV[w][str(k)]["0.5"], results[w]["em"]["k"][str(k)]["r1"]) for w in ws for k in ks_of(w)]
        rc["p_repro_r1"][ds] = dict(passed=all(same_bits(a, b) for a, b in cmp), compared=len(cmp),
                                    max_abs_diff=float(max(abs(a[0] - b[0]) for a, b in cmp)))
        dump()
        if not rc["p_repro_r1"][ds]["passed"]:
            sys.exit("P-REPRO-R1 が外れた（%s）" % ds)
        BV[ds] = dict(r1=RV)
        T[ds + "_r1_sec"] = time.time() - t0
        if ds == "coauthor":
            # B1: P15 の書き手（P30 は含まれる）。α = 1 を先に回して照らす
            p15 = next(iter(members["P15"].values()))
            assert set(next(iter(members["P30"].values()))) <= set(p15)
            t1 = time.time()
            PV = pool_values(ds, paths[ds], p15, ["1"], jobs)
            cmp = [(PV[w][n]["1"], results[w]["em"]["pool"][n]) for w in p15 for n in AB.SN]
            rc["p_repro_pool"] = dict(passed=all(same_bits(a, b) for a, b in cmp), compared=len(cmp),
                                      max_abs_diff=float(max(abs(a[0] - b[0]) for a, b in cmp)))
            dump()
            if not rc["p_repro_pool"]["passed"]:
                sys.exit("P-REPRO-POOL が外れた（α = 1 の当て直しが mode の共通と同じにならない）。止めて研究者に聞く")
            T["alpha_1_sec"] = time.time() - t1
            print("P-REPRO-POOL 通過（%.0f 秒）" % T["alpha_1_sec"], flush=True)
            rest = [a for a in AB.ALPHAS if a != "1"]
            # V2 の時間の規則: α = 1 の時間 × 回す α の数が 6 時間を超えたら、α = 3 → α = 0.03 の順に外す
            T["alpha_cut"] = []
            for c in ALPHA_CUTS:
                if T["alpha_1_sec"] * (1 + len(rest)) / 3600 <= BUDGET_B1_HOURS:
                    break
                rest.remove(c)
                T["alpha_cut"].append(c)
            T["alphas_run"] = ["1"] + rest
            if T["alpha_1_sec"] * (1 + len(rest)) / 3600 > BUDGET_B1_HOURS:
                AB.write_json(T, os.path.join(out, "timing.json"))
                sys.exit("削っても B1 の見積もりが 6 時間を超える。止めて研究者に聞く")
            t2 = time.time()
            PV2 = pool_values(ds, paths[ds], p15, rest, jobs)
            for w in p15:
                for n in AB.SN:
                    PV[w][n].update(PV2[w][n])
            T["alpha_rest_sec"] = time.time() - t2
            BV[ds]["pool"] = PV
        AB.write_json(T, os.path.join(out, "timing.json"))
    with open(bout, "wb") as fp:
        pickle.dump(BV, fp)
    rc["bvals_sha256"] = hashlib.sha256(open(bout, "rb").read()).hexdigest()
    dump()


if __name__ == "__main__":
    main()
