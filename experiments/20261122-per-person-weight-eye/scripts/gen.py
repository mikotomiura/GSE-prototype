"""合成の生成（conditions.md D4）。sens の synth.py を写さずに読み込み（SHA-256 を照らす・P-HASH）、この研究で足した筋を作る。

筋の番号: 用量 0・分布 1・構造 2・揺れ 3・漂い 4・量 5・重ね 6。形の番号: CoAuthor 0・CS1 1。
- 用量・分布・構造（第 1 の帰無）と第 2 の帰無の用量は sens の build（SEED 2026111001）をそのまま呼ぶ。
- 揺れ・漂い・量・重ねは sens の部品（make_m0・draw_D・writer_model・Sampler）で、書き手と単位の数は build と同じ。
  乱数は [SEED + 筋 × 10 + 1, 形, 種]（D と長さ・r_w）・[SEED + 筋 × 10 + 4, 形, 種]（系列）。

変異 w6: 漂いの筋の空回しを外す（E の最初の引きの直後から記録する）。
"""
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
SENS = os.path.realpath(os.path.join(EXP, "..", "20261110-per-person-sensitivity"))
NFS = os.path.realpath(os.path.join(EXP, "..", "20261113-null-from-shared"))
SEED = int(open(os.path.join(EXP, "SEED")).read().strip())
SENS_SEED = 2026111001
PIN1 = {
    os.path.join(SENS, "scripts", "synth.py"): "41c60dd5ec954f6d1bd526560c318f96847641533e31f3826f099fb443d64ee3",
    os.path.join(SENS, "scripts", "pinned.py"): "02317ec7174be93aa60c18a022ba411d5652cc1f97aab7fd1c0408e254ab8006",
    os.path.join(SENS, "results", "calibration.json"): "d8c8c55f05e03f70e6c44b49789af4b46c95f3d6f99bcd570851a8bb2fe3f18d",
}
PIN2 = {
    os.path.join(NFS, "results", "calibration.json"): "011b5b350d9a5ea02c6b06d6130a494d17063bb8de79d6fef268cb85a44f1fb6",
    os.path.join(NFS, "results", "m0_fit.json"): "c86493f05f913cde70ed7285c30db478f612fdf0eec6a504a3865a945b34390a",
}
NPZ_SHA = "a4fbe2d6ca127547c451e2887ea271d3f48277b3cf51990a1cd6d3eb14761fb4"
NFS_ALPHA = "0.03"
STRAND = dict(dose=0, dist=1, struct=2, wobble=3, drift=4, volume=5, stack=6)
LONG = dict(coauthor=(300, 1000), cs1=(2500, 10000))   # 長さの不均一（D4 の長さの一覧）
DOSE = [1e-3, 3e-3, 1e-2, 3e-2]
STEP = {0.0: 0, 1e-3: 1, 3e-3: 2, 1e-2: 3, 3e-2: 4, 1.0: 5}
RHO_STEP = {0.0: 0, 0.5: 1, 0.9: 2}
MUT = set()


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_hashes(second=False, npz=None):
    """P-HASH。違えば止める。返り値: {パス: SHA-256}。"""
    pins = dict(PIN1)
    if second:
        pins.update(PIN2)
        if npz is None:
            sys.exit("第 2 の帰無には npz の置き場が要る")
        pins[npz] = NPZ_SHA
    got = {p: sha(p) for p in pins}
    bad = {p: v for p, v in got.items() if v != pins[p]}
    if bad:
        sys.exit("SHA-256 が条件の値と違う（P-HASH）: %r" % bad)
    if second and json.load(open(os.path.join(NFS, "results", "m0_fit.json")))["npz_sha256"] != NPZ_SHA:
        sys.exit("m0_fit.json の npz_sha256 が条件の値と違う")
    return got


check_hashes()
sys.path.insert(0, os.path.join(SENS, "scripts"))
import synth as SY  # noqa: E402
from pinned import DT, ml  # noqa: E402

NSYM = SY.NSYM


def assert_clean():
    """本計算と各変異の実行の始めに: 読み込んだ synth.py の MUT が空（V1）。data.py・ml.py の変異も空。"""
    if SY.MUT != set():
        sys.exit("synth.MUT が空でない: %r" % SY.MUT)
    if DT.MUT != set() or ml.MUT != set() or ml.H.MUT != set():
        sys.exit("data.MUT・ml.MUT・hmm2.MUT のどれかが空でない")


# ---------------------------------------------------------------- 母数と λ
def m0_first(K):
    return SY.make_m0(K, SENS_SEED)


def lam_first(K, g):
    if g == 0:
        return 0.0
    if g == 1.0:
        return 1.0
    cal = json.load(open(os.path.join(SENS, "results", "calibration.json")))["cal"]
    return float(cal[str(K)][str(g)]["lam"])


def load_second(npz):
    """第 2 の帰無の m0（α = 0.03）と λ。値は表示しない。"""
    check_hashes(second=True, npz=npz)
    Z = np.load(npz)
    m0 = dict(kind="ar", **{k: np.array(Z["a%s_%s" % (NFS_ALPHA, k)]) for k in ("pi", "A", "H", "C")})
    C = json.load(open(os.path.join(NFS, "results", "calibration.json")))
    if C["alpha"] != NFS_ALPHA or C["m0_sha256"] != NPZ_SHA:
        sys.exit("nfs の calibration.json の alpha か m0_sha256 が条件と違う")
    lams = {float(g): float(v["lam"]) for g, v in C["cal"]["3"].items()}
    return m0, lams


def lam_drift(rho):
    """λ_ρ = λ_{3e-2} × √((1 + ρ)/(1 − ρ))（D4）。"""
    return lam_first(3, 3e-2) * np.sqrt((1 + rho) / (1 - rho))


# ---------------------------------------------------------------- sens の build を呼ぶ筋
def build_sens(strand, shape, K, seed, lam, m0):
    writers, models, lams, P = SY.build(shape, K, seed, SY.lam_rule(strand, lam), m0, SENS_SEED)
    return writers, P, lams


# ---------------------------------------------------------------- この研究で足した筋
def _mix(C0, lam, X):
    return C0.copy() if lam == 0 else (1 - lam) * C0 + lam * X


def build_new(strand, shape, seed, m0, lam=0.0, rho=0.0, n_writers=None, seqs=True):
    """揺れ（lam）・漂い（rho）・量・重ね。返り値: writers・P・各単位の C（P-STAT と D9 のため）。
    引く順（書き手ごと）: r_w（量・重ね）→ D_w（揺れ）→ 空回し（漂い・重ね）→ 単位ごとに（長さ → D_{w,u} か E の更新）。
    その後に系列（rng4）を書き手・単位・系列の順に引く。rng1 と rng4 は別の流れなので、n_writers・seqs=False
    （P-STAT: 先頭の書き手の母数だけ）でも先頭の書き手の母数は本計算と同じ。"""
    sh = SY.SHAPES[shape]
    si = STRAND[strand]
    N = sh["P"] + sh["O"]
    rng1 = np.random.default_rng([SEED + si * 10 + 1, sh["i"], seed])
    rng4 = np.random.default_rng([SEED + si * 10 + 4, sh["i"], seed])
    C0 = m0["C"]
    if strand in ("drift", "stack"):
        lam_d = lam_drift(rho if strand == "drift" else 0.0)
        r_ = rho if strand == "drift" else 0.0
    Lr = LONG[shape] if strand in ("wobble", "stack") else sh["L"]
    writers, unitC = [], []
    for i in range(N if n_writers is None else n_writers):
        nu = sh["Pu"] if i < sh["P"] else sh["Ou"]
        r_w = float(np.exp(rng1.uniform(np.log(0.5), np.log(2.0)))) if strand in ("volume", "stack") else 1.0
        if strand == "wobble":
            D_w = SY.draw_D(m0, rng1)
        if strand in ("drift", "stack"):
            E = SY.draw_D(m0, rng1)
            if "w6" not in MUT:
                for _ in range(99):
                    E = r_ * E + (1 - r_) * SY.draw_D(m0, rng1)
        lens, Cs = [], []
        for _ in range(nu):
            ls = rng1.integers(Lr[0], Lr[1] + 1, size=sh["nseq"]).tolist()
            if r_w != 1.0:
                ls = [int(round(r_w * L)) for L in ls]
            if strand == "wobble":
                D_u = SY.draw_D(m0, rng1)
                C = _mix(C0, lam, 0.5 * D_w + 0.5 * D_u)
            elif strand in ("drift", "stack"):
                E = r_ * E + (1 - r_) * SY.draw_D(m0, rng1)
                C = _mix(C0, lam_d, E)
            else:
                C = C0.copy()
            lens.append(ls)
            Cs.append(C)
        units = []
        for ls, C in zip(lens, Cs) if seqs else []:
            mw = dict(kind="ar", pi=m0["pi"].copy(), A=m0["A"].copy(), H=m0["H"].copy(), C=C)
            smp = SY.Sampler(mw)
            ss = [smp.seq(rng4.random((L, 2))) for L in ls]
            units.append(dict(seqs=ss, pflag=[np.ones(len(x), dtype=bool) for x in ss]))
        writers.append(units)
        unitC.append(Cs)
    return writers, sh["P"], unitC


# ---------------------------------------------------------------- 複製の一覧の 1 行 → 単位
def make(row, second=None):
    """row: dict(null, strand, shape, step（g か ρ）, seed)。second: load_second の返り値（第 2 の帰無）。"""
    st, shape, seed = row["strand"], row["shape"], row["seed"]
    if row["null"] == 2:
        m0, lams = second
        lam = 0.0 if row["step"] == 0 else lams[row["step"]]
        w, P, _ = build_sens("dose", shape, 3, seed, lam, m0)
        return w, P
    if st in ("dose", "dist", "struct"):
        K = 5 if st == "struct" else 3
        w, P, _ = build_sens(st, shape, K, seed, lam_first(K, row["step"]), m0_first(K))
        return w, P
    if st == "wobble":
        w, P, _ = build_new(st, shape, seed, m0_first(3), lam=lam_first(3, row["step"]))
    elif st == "drift":
        w, P, _ = build_new(st, shape, seed, m0_first(3), rho=row["step"])
    else:
        w, P, _ = build_new(st, shape, seed, m0_first(3))
    return w, P
