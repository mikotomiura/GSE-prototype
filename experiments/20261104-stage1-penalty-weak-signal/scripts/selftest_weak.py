"""計算の前の門（conditions.md W3）。

W1: 係数 1 倍の外側の層が、前の sim の主のセル（同じ条件・同じ乱数）と同じ値を返す。
W2: 倍率が生成に効いている（真のモデルの C が倍率ごとに見込みの値に入り、陽性の率が合う）。
    陽性の率は、倍率 3 × 率 3 × σ_d 2 の 18 組の切片で確かめる。
W5: 本計算と同じ Pool（spawn のワーカー）の経路で、倍率 0.5・0.25 のセルが、親のプロセスで
    係数を k 倍に置いて前の sim.one_rep を呼んだ値と全部一致する（2 つの倍率を同じ Pool に続けて流す）。

使い方: python3 -I -X utf8 selftest_weak.py SEED OUT_JSON [--only W1] [--mutate w1] [--run-id ID]
どれかの門が落ちたら終了コード 3。
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weak  # noqa: E402

sim = weak.sim
W2_EXPECT = {1.0: 0.723, 0.5: 0.623, 0.25: 0.561}  # 率 0.25・σ_d 0・20 万件で前もって数えた値
W2_TOL = 0.015
W2_N = 200_000
W2_RATE_N = 50_000


def g_w1(seed):
    base = {c["id"]: c for c in sim.cells(seed, ["main"])}
    wc = [c for c in weak.cells(seed) if c["scale"] == 1.0]
    bad = []
    for c in wc:
        b = base[c["main_id"]]
        if c["id"] != b["id"] or c["a"] != b["a"] or any(c[k] != b[k] for k in ("n", "rate", "sd", "signal", "kind")):
            bad.append(f"セル {c['main_id']} の番号か条件が前と違う")
    picks = [c for c in wc if (c["n"], c["rate"], c["sd"]) in ((10, 0.25, 0.5), (50, 0.10, 0.0), (120, 0.40, 0.5))]
    for c in picks:
        b = base[c["main_id"]]
        for rep in range(4):
            got = weak._job((c, rep, seed, tuple(weak.MUT_W)))
            sim.BETA = weak.BASE_BETA.copy()
            exp = sim.one_rep(b, rep, seed)
            for k, v in exp.items():
                gv = got[k]
                same = np.array_equal(np.asarray(gv), np.asarray(v), equal_nan=True)
                if not same:
                    bad.append(f"セル {c['main_id']} 反復 {rep} の {k} が違う")
    weak.set_scale(1.0)
    return dict(ok=not bad, bad=bad[:10], n_cells=len(wc), n_checked=len(picks) * 4)


def g_w2(seed):
    rows = {}
    bad = []
    cl = {c["scale"]: c for c in weak.cells(seed) if c["rate"] == 0.25 and c["sd"] == 0.0 and c["n"] == 10}
    for k, c in cl.items():
        weak.set_scale(k)
        rng = np.random.default_rng([seed, 911, int(k * 100)])
        _, y, _, p = sim.gen(rng, W2_N, 0.0, c["a"], sim.BETA, "main", False)
        cidx = sim.auc(y, p)
        rate = float(y.mean())
        rows[str(k)] = dict(c=cidx, rate=rate)
        if abs(cidx - W2_EXPECT[k]) > W2_TOL:
            bad.append(f"倍率 {k} の C {cidx:.3f} が見込み {W2_EXPECT[k]} から外れた")
        if abs(rate - 0.25) > 0.01:
            bad.append(f"倍率 {k} の陽性の率 {rate:.3f}")
    rates = {}
    for c in weak.cells(seed):
        if c["n"] != 10:
            continue
        weak.set_scale(c["scale"])
        rng = np.random.default_rng([seed, 912, c["id"]])
        _, y, _, _ = sim.gen(rng, W2_RATE_N, c["sd"], c["a"], sim.BETA, "main", False)
        rt = float(y.mean())
        rates[f"{c['scale']}/{c['rate']}/{c['sd']}"] = rt
        if abs(rt - c["rate"]) > 0.01:
            bad.append(f"倍率 {c['scale']} 率 {c['rate']} σ_d {c['sd']} の陽性の率 {rt:.3f}")
    weak.set_scale(1.0)
    return dict(ok=not bad and len(rates) == 18, bad=bad, rows=rows, rates=rates)


def g_w5(seed):
    pick = [c for c in weak.cells(seed) if c["scale"] in (0.5, 0.25) and c["n"] == 20 and c["rate"] == 0.25 and c["sd"] == 0.5]
    got = weak.run_cells(seed, pick, 3, 2, tuple(weak.MUT_W))
    bad = []
    for c in pick:
        _, arr = got[c["id"]]
        for rep in range(3):
            sim.MUT.clear()
            sim.BETA = weak.BASE_BETA * c["scale"]
            exp = sim.one_rep(c, rep, seed)
            for k, v in exp.items():
                if not np.array_equal(np.asarray(arr[k][rep]), np.asarray(v), equal_nan=True):
                    bad.append(f"倍率 {c['scale']} 反復 {rep} の {k} が違う")
    sim.BETA = weak.BASE_BETA.copy()
    return dict(ok=not bad and len(pick) == 2, bad=bad[:10], n_cells=len(pick))


GATES = {"W1": g_w1, "W2": g_w2, "W5": g_w5}


def main(argv):
    seed, out = int(argv[0]), argv[1]
    opt = dict(zip(argv[2::2], argv[3::2]))
    only = [g for g in opt.get("--only", ",".join(GATES)).split(",") if g]
    mut = [m for m in opt.get("--mutate", "").split(",") if m]
    weak.MUT_W.update(mut)
    res = {g: GATES[g](seed) for g in only}
    ok = all(r["ok"] for r in res.values())
    json.dump(dict(run_id=opt.get("--run-id"), mutate=mut, gates=res, ok=ok), open(out, "w"),
              ensure_ascii=False, indent=1)
    print("selftest_weak", "OK" if ok else "FAIL", {g: r["ok"] for g, r in res.items()})
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main(sys.argv[1:])
