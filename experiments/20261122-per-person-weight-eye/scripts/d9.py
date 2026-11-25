"""D9: 1 状態の表に出る植えた差の大きさ（記述だけ）。合成の値だけを扱う。

使い方: python3 -I d9.py <out_json> --null <1|2> [--npz PATH] [--jobs 8]
  --null 1（この Mac）: 第 1 の帰無の用量（4 段）・構造（K = 5・1e-2）・揺れ（1e-2・3e-2）・漂い（ρ = 0・0.5・0.9）
  --null 2（HP Z2）: 第 2 の帰無の用量（4 段）

1 つの筋・段ごとに、書き手 40 人（種 7000〜7039）。書き手ごとの乱数は 1 本の流れ
[SEED + 91, 帰無の番号, 筋の番号, 段の番号, 種] で、引く順はこのファイルで固定（判断 42）:
  1. 母数（用量・構造: D_w。揺れ: D_w と当てる側 31 単位・評価の側 31 単位の D_{w,u}。漂い: 当てる側・評価の側それぞれの
     空回し 99 回と 31 単位の E の更新）
  2. 長さ 20,000 の系列を 3 本（m_w の当てる側 → m0 → m_w の評価の側）。単位のある筋は単位の境目で切る（650 × 30 + 500）。
  3. 単位ごとのずれ（用量・揺れ・漂い）: 当てる側の先頭 20 単位の真の母数それぞれから長さ 20,000 を 1 本、m0 から 1 本。
- g1 = 書き手ごとの「評価の側での、m_w から当てた表 − m0 から当てた表」の 1 遷移あたりの対数尤度の差、の 40 人の中央値。
- KL = 単位の表 ∥ m0 の表の行ごとの KL を、m0 の系列の行の占有 π で重み付けた和。書き手 × 単位の中央値。
- 表は D1 の数え方（系列・単位をまたがない隣り合う組）に 0.5 を足して行で割る。
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eye as EY  # noqa: E402
import gen as GN  # noqa: E402
import run_eye as RE  # noqa: E402

SY = GN.SY
N_W, SEEDS = 40, range(7000, 7040)
L_ALL, U_LEN, U_N = 20000, 650, 31
N_KL_UNITS = 20
_CTX = {}


def unit_lens():
    ls = [U_LEN] * (U_N - 1)
    ls.append(L_ALL - sum(ls))
    return ls


def table(counts):
    T = counts + 0.5
    return T / T.sum(1, keepdims=True)


def counts_of(seqs):
    N = np.zeros((GN.NSYM, GN.NSYM), dtype=np.int64)
    for s in seqs:
        N += EY.seq_counts(s, GN.NSYM)
    return N


def sample(model_C, m0, rng, lens):
    """C（K×J×J）の AR-HMM から、長さ lens の系列を（単位ごとに別の系列として）引く。"""
    m = dict(kind="ar", pi=m0["pi"].copy(), A=m0["A"].copy(), H=m0["H"].copy(), C=model_C)
    smp = SY.Sampler(m)
    return [smp.seq(rng.random((L, 2))) for L in lens]


def sample_units(Cs, m0, rng, lens):
    out = []
    for C, L in zip(Cs, lens):
        out += sample(C, m0, rng, [L])
    return out


def ll_per(T, seqs):
    N = counts_of(seqs)
    return float((N * np.log(T)).sum() / N.sum())


def kl_pi(Tu, T0, pi):
    return float((pi * (Tu * (np.log(Tu) - np.log(T0))).sum(1)).sum())


def params(strand, m0, lam, rho, rng):
    """当てる側と評価の側の単位ごとの C の列（長さ U_N）。用量・構造は全単位が同じ。"""
    C0 = m0["C"]
    if strand in ("dose", "struct"):
        D = SY.draw_D(m0, rng)
        C = SY.writer_model(m0, D, lam)["C"]
        return [C] * U_N, [C] * U_N
    if strand == "wobble":
        D_w = SY.draw_D(m0, rng)
        sides = []
        for _ in range(2):
            sides.append([GN._mix(C0, lam, 0.5 * D_w + 0.5 * SY.draw_D(m0, rng)) for _ in range(U_N)])
        return sides[0], sides[1]
    if strand == "drift":
        lam_d = GN.lam_drift(rho)
        sides = []
        for _ in range(2):
            E = SY.draw_D(m0, rng)
            for _ in range(99):
                E = rho * E + (1 - rho) * SY.draw_D(m0, rng)
            Cs = []
            for _ in range(U_N):
                E = rho * E + (1 - rho) * SY.draw_D(m0, rng)
                Cs.append(GN._mix(C0, lam_d, E))
            sides.append(Cs)
        return sides[0], sides[1]
    raise ValueError(strand)


def one_writer(a):
    null, strand, step, seed = a
    m0, lam, rho = _setup(null, strand, step)
    stepno = GN.RHO_STEP[step] if strand == "drift" else GN.STEP[step]
    rng = np.random.default_rng([GN.SEED + 91, null, GN.STRAND[strand], stepno, seed])
    fit_C, ev_C = params(strand, m0, lam, rho, rng)
    lens = unit_lens() if strand in ("wobble", "drift") else [L_ALL]
    if len(lens) == 1:
        fit_C, ev_C = fit_C[:1], ev_C[:1]
    fit = sample_units(fit_C, m0, rng, lens)
    base = sample(m0["C"], m0, rng, lens)
    ev = sample_units(ev_C, m0, rng, lens)
    Tw, T0 = table(counts_of(fit)), table(counts_of(base))
    out = dict(seed=seed, d=ll_per(Tw, ev) - ll_per(T0, ev))
    if strand != "struct":
        kC = (fit_C * N_KL_UNITS)[:N_KL_UNITS] if len(fit_C) == 1 else fit_C[:N_KL_UNITS]
        b0 = counts_of(sample(m0["C"], m0, rng, [L_ALL]))
        T0k = table(b0)
        pi = b0.sum(1) / b0.sum()
        out["kl"] = [kl_pi(table(counts_of(sample(C, m0, rng, [L_ALL]))), T0k, pi) for C in kC]
    return out


def _setup(null, strand, step):
    if null == 2:
        m0, lams = _CTX["second"]
        return m0, lams[step], 0.0
    if strand == "struct":
        return GN.m0_first(5), GN.lam_first(5, step), 0.0
    if strand == "drift":
        return GN.m0_first(3), 0.0, step
    return GN.m0_first(3), GN.lam_first(3, step), 0.0


def _init(npz):
    GN.assert_clean()
    if EY.MUT or GN.MUT:
        raise RuntimeError("変異が入っている")
    _CTX["second"] = GN.load_second(npz) if npz else None


def plan(null):
    if null == 2:
        return [("dose", g) for g in GN.DOSE]
    return ([("dose", g) for g in GN.DOSE] + [("struct", 1e-2)] + [("wobble", g) for g in (1e-2, 3e-2)]
            + [("drift", r) for r in (0.0, 0.5, 0.9)])


def main():
    argv = sys.argv[1:]
    opt = {}
    for key in ("--null", "--npz", "--jobs"):
        if key in argv:
            i = argv.index(key)
            opt[key] = argv[i + 1]
            argv = argv[:i] + argv[i + 2:]
    path = argv[0]
    null = int(opt["--null"])
    npz = opt.get("--npz")
    if (null == 2) != (npz is not None):
        sys.exit("第 2 の帰無だけ --npz を渡す")
    jobs = int(opt.get("--jobs", "8"))
    GN.assert_clean()
    R = dict(code_hash=RE.code_hash(), null=null, n_writers=N_W, length=L_ALL, rows=[])
    with ProcessPoolExecutor(jobs, initializer=_init, initargs=(npz,)) as ex:
        for strand, step in plan(null):
            res = list(ex.map(one_writer, [(null, strand, step, s) for s in SEEDS]))
            row = dict(strand=strand, step=step, g1=float(np.median([r["d"] for r in res])),
                       d=[r["d"] for r in res])
            if "kl" in res[0]:
                kl = np.concatenate([r["kl"] for r in res])
                row["kl_median"] = float(np.median(kl))
            R["rows"].append(row)
            print("D9 %s %s 終わり" % (strand, step), flush=True)
    json.dump(R, open(path, "w"), indent=1)
    print("書いた: %s" % path)


if __name__ == "__main__":
    main()
