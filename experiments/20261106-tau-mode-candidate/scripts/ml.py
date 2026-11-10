"""CoAuthor と CS1 2021 で、τ の固定の行と相手に事前分布の最頻値 normalize(S̄) を足す（EM だけ）。
条件は conditions.md（前の試験 experiments/20261104-timeseries-tau-extend/conditions.md から変える所）、
作業記録は .steering/20261106-gse-tau-mode-candidate/（判断 1〜11）。前の試験の ml.py を写して変えた。
最頻値は選ぶ行の候補に入れない（判断 2）。最頻値の評価の −∞ はそのまま集計に入れ、JSON では文字列で書く（判断 4）。

使い方:
  python3 -I ml.py --selftest <seed> <out.json> [--mutate mX] [--only NAME,...] [--run-id ID]
  python3 -I ml.py <coauthor_work_obs> <cs1_work_obs> <seed> <out_dir> <jobs> [--only-dataset coauthor|cs1]
出力は集計値だけ。書き手・セッション・課題の番号を書かない。範囲の端を出さない。
ラベル（代理ラベルを含む）は使わない。評価の量は 1 歩先の予測の対数尤度だけ。
EM の状態に名前を付けない（ADR-046 D1）。
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as DT  # noqa: E402
import hmm2 as H  # noqa: E402
import hmm_b  # noqa: E402

# 前回の構造の並べ（乱数の流れを前回とそろえるためだけに使う・conditions D3 の注）
PREV_STRUCTS = [("hmm", 3), ("hmm", 6), ("hmm", 10), ("ar", 1), ("ar", 2), ("ar", 3)]
STRUCTS = [("hmm", 3), ("ar", 1), ("ar", 2), ("ar", 3)]
DROPPED = [s for s in PREV_STRUCTS if s not in STRUCTS]  # 当てはめず、乱数の開始点だけを引いて捨てる
SEQ_NO = {s: i for i, s in enumerate(PREV_STRUCTS)}       # 全員の共通の乱数の通し番号（hmm3 = 0・ar1 = 3・ar2 = 4・ar3 = 5）
TAUS_FIT = [0, 100, 1000, 10000, 30000, 100000, 300000, 1000000]  # 有限の τ（当てはめる）
INF = "inf"                                                     # τ = ∞（当てはめず、w を除く共通の母数を使う）
TAU_KEYS = [str(t) for t in TAUS_FIT] + [INF]                 # 選ぶ行の候補（前の試験と同じ 9 値・判断 2）
MODE = "mode"                                                   # 事前分布の最頻値（τ 固定の行と相手だけ）
PREV_TAU_KEYS = ["0", "100", "1000", "10000"]                   # 前回と重なる τ（P-REPRO・P-SUBSET）
B_BOOT = 2000
N_MIN = 6  # これより少ない人数の四分位・区間・割合・選ばれた値の人数は伏せて人数だけを出す（前回の D5）
MUT = set()  # m8: 他人で選ぶ v に w 自身を入れる・m11: τ = ∞ に全員の共通・m12: 2 段（他人）に w 自身・
#              m13: 共通 − r1 を中央値どうしの差・m14: 外した構造の乱数を引かない・
#              m16: 最頻値を全員の共通の S̄ から作る・m17: 最頻値の代わりに w を除く共通の母数・
#              m18: 最頻値の評価に確率 0 の扱いの無い pred_logprob（NaN の道）・m19: 最頻値が −∞ の書き手を集計の前に捨てる・
#              m20: ∞ を含んでも区間を linear で出す・m21: 相手「最頻値」を中央値どうしの差で配る・
#              m22: 最頻値を τ 他人の候補に足す・m23: 最頻値の評価の前に乱数を 1 回引く・m24: 共通の母数を float32 で書く・
#              m26: 副の「最頻値が有限の書き手だけ」に −∞ の書き手を残す・m27: 押下の量の上書き（判断 9）を外す

DATASETS = {
    "coauthor": dict(H=5, grid=[1, 2, 3, 5, 8, 12, 15, 20, 30],
                     panels={"P15": (20, [1, 2, 3, 5, 8, 12, 15]), "P30": (35, [1, 2, 3, 5, 8, 12, 15, 20, 30])}),
    "cs1": dict(H=1, grid=[1, 2, 3, 5], panels={"C5": (6, [1, 2, 3, 5])}),
}
OPPS = ("r1", "pool_same", "pool_hmm3", "fb", "mode_same")  # mode_same は末尾（判断 3）


def sname(s):
    return "%s%d" % s


def tau_val(t):
    """τ の鍵 → 数（∞ は float('inf')）。同点の並べに使う。"""
    return float("inf") if t == INF else float(t)


def tau_cands():
    """選ぶ行（τ 他人・τ 本人 CV）の τ の候補（大きい方が先）。最頻値は入れない（判断 2・m22 は ∞ の次に入れる）。"""
    c = sorted(TAU_KEYS, key=tau_val, reverse=True)
    return c[:1] + [MODE] + c[1:] if "m22" in MUT else c


def set_mut(mut):
    for mod in (H, DT):
        mod.MUT.clear()
        mod.MUT.update(mut)
    MUT.clear()
    MUT.update(mut)


# ---------------------------------------------------------------- 系列の取り出し
def seqs_of(units):
    return [s for u in units for s in u["seqs"]]


def pflags_of(units):
    return [f for u in units for f in u["pflag"]]


def non_eval(units, H_):
    """評価に使う単位を除いた単位（評価の単位を持たない書き手は全単位）。"""
    return units[:len(units) - H_] if len(units) >= H_ + 1 else units


def pool_units(writers, H_, exclude=None):
    return [u for j, ss in enumerate(writers) if j != exclude for u in non_eval(ss, H_)]


# ---------------------------------------------------------------- EM の部品
def frozen_start():
    return dict(kind="hmm", pi=hmm_b.PI0.copy(), A=hmm_b.A0.copy(), B=hmm_b.B0.copy())


POOL_STARTS = 10


def pool_starts(kind, K, rng, seqs):
    """全員の共通の開始点 10 個。K = 3 のふつうの HMM は凍結の正規化 ＋ 乱数 9 つ（前回と同じ）。"""
    _, h, T = H.r0_r1(seqs)
    st = []
    if (kind, K) == ("hmm", 3):
        st.append(("frozen", frozen_start()))
    while len(st) < POOL_STARTS:
        st.append(("rand%d" % len(st), H.random_model(kind, K, rng, r1=T, r0=h)))
    return st


def fit_pool_full(job):
    """全員の共通（構造ごと）。乱数は [SEED + 11, 前回の構造の通し番号]（job["si"] は SEQ_NO の値）。"""
    writers = _W[job["ds"]] if job.get("writers") is None else job["writers"]
    seqs = seqs_of(pool_units(writers, DATASETS[job["ds"]]["H"]))
    si, seed = job["si"], job["seed"]
    kind, K = PREV_STRUCTS[si]
    rng = np.random.default_rng([seed + 11, si])
    D = H.Batched(seqs, chunk=H.CHUNK)
    m, diag = H.fit(pool_starts(kind, K, rng, seqs), D, H.base_prior(kind, K))
    S, _ = H.counts(m, D)  # 全員の共通の S̄（保存と m16 だけが使う・当てはめは変えない）
    return m, diag, H.sbar_of(S, D.nobs)


def fit_pool_excl(job):
    """w を除く共通（1 開始点 = 全員の共通の解）。S̄ は最後の母数での E 段の期待度数 / 記号の総数。"""
    writers = _W[job["ds"]] if job.get("writers") is None else job["writers"]
    seqs = seqs_of(pool_units(writers, DATASETS[job["ds"]]["H"], exclude=job["w"]))
    m0 = job["start"]
    kind, K = m0["kind"], len(m0["pi"])
    D = H.Batched(seqs, chunk=H.CHUNK)
    m, diag = H.fit([("full_pool", m0)], D, H.base_prior(kind, K))
    S, _ = H.counts(m, D)
    return m, H.sbar_of(S, D.nobs), diag


class Eval:
    """評価の系列（切らない）。量は 1 歩先の対数尤度の 1 記号あたりの平均（全記号・窓に押下のある記号）。"""

    def __init__(self, seqs, pflags):
        keep = [i for i, s in enumerate(seqs) if len(s)]
        self.seqs = [seqs[i] for i in keep]
        self.D = H.Data(self.seqs)
        self.PF = np.zeros_like(self.D.M)
        for i, f in enumerate(pflags[j] for j in keep):
            self.PF[i, :len(f)] = f
        self.PF &= self.D.M

    def of_lp(self, lp):
        n, npf = self.D.M.sum(), self.PF.sum()
        return [float(lp[self.D.M].sum() / n), float(lp[self.PF].sum() / npf) if npf else None]

    def ll(self, m):
        return self.of_lp(H.pred_logprob(m, self.D))

    def ll_r1(self, h, T):
        lp = np.zeros(self.D.M.shape)
        for i, s in enumerate(self.seqs):
            s = np.asarray(s)
            lp[i, 0] = np.log(h[s[0]])
            lp[i, 1:len(s)] = np.log(T[s[:-1], s[1:]])
        return self.of_lp(lp)

    def ll_fb(self):
        O, M = hmm_b.pad(self.seqs)
        lp, _, _ = hmm_b.fb_engine(O, M, mutate_unnorm=False)
        return self.of_lp(lp)

    def ll_zero(self, m):
        """確率 0 のセルを持ちうる母数（最頻値）の評価。全記号の量が −∞ なら押下のある記号の量も −∞（判断 9）。
        m18 は確率 0 の扱いの無い pred_logprob を使う（NaN の道）。"""
        if "m18" in MUT:
            with np.errstate(divide="ignore", invalid="ignore"):
                return self.of_lp(H.pred_logprob(m, self.D))
        r = self.of_lp(H.pred_logprob_zero(m, self.D))
        if r[0] == -np.inf and r[1] is not None and "m27" not in MUT:
            r[1] = -np.inf
        return r

    def sum_ll(self, m):
        lp = H.pred_logprob(m, self.D)
        return float(lp[self.D.M].sum()), int(self.D.M.sum())


def fit_self_all(kind, K, D, pool_m, sb, rng, h, T):
    """本人の当てはめ（有限の τ）: τ = 0（開始点 = w を除く共通の解・乱数 1 つ）と τ > 0（共通の解・本人 τ = 0 の解）。
    τ どうしは独立に当てはめる（τ を足しても既にある τ の当てはめは変わらない）。返り値: {τ: 母数}・{τ: 診断}。"""
    out, diag = {}, {}
    m0, d0 = H.fit([("pool", pool_m), ("rand", H.random_model(kind, K, rng, r1=T, r0=h))], D, H.base_prior(kind, K))
    out[0], diag[0] = m0, d0
    for tau in TAUS_FIT[1:]:
        m, d = H.fit([("pool", pool_m), ("self0", m0)], D, H.make_prior(kind, K, tau, sb))
        out[tau], diag[tau] = m, d
    return out, diag


def discard_draws(s, units, H_, ks, rng, do_folds):
    """外した構造（hmm6・hmm10）の番: 当てはめはせず、前回と同じ形の乱数の開始点（random_model）だけを引いて捨てる。
    前回の並べは k ごとに（本人の主の当てはめの τ = 0 の乱数 1 つ → 折り目ごとに 1 つ）。ふつうの HMM の
    random_model は r1・r0 を使わないので、引く量は前回と同じ。"""
    kind, K = s
    n = len(units)
    for k in ks:
        train, _ = DT.split(n, k, H_)
        H.random_model(kind, K, rng)
        for _ in (DT.folds(train) if do_folds else []):
            H.random_model(kind, K, rng)


def mode_eval(ev, kind, pool_m, sb, full_sb, rng):
    """最頻値の評価（構造ごとに 1 回・k に依らない・乱数を引かない）。返り値: (評価 [全記号, 押下], 和 0 の行に当たったか)。
    m16 は全員の共通の S̄、m17 は w を除く共通の母数、m23 は評価の前に乱数を 1 回引く。"""
    if "m23" in MUT:
        rng.random()
    if "m17" in MUT:
        return ev.ll_zero(pool_m), False
    m, zero = H.mode_of(kind, full_sb if ("m16" in MUT and full_sb is not None) else sb)
    return ev.ll_zero(m), H.zero_row_hit(zero, ev.D)


def em_writer(units, H_, ks, pools, rng, structs=None, do_folds=True, full=None, keep_fits=False):
    """1 書き手の EM。pools: {構造名: (w を除く共通の母数, S̄)}。full: {構造名: (全員の共通の母数, その S̄)}（m11・m16 だけが使う）。
    最頻値は res["mode"]・res["mode_zero_row"] に置き、k ごとの self には入れない（前の試験と同じ鍵を保つ）。
    structs が None なら前回の並べ（PREV_STRUCTS）で回り、外した構造の番では乱数だけを引いて捨てる（m14 は引かない）。
    乱数の並べ: 構造 → k →（τ = 0 の乱数の開始点）→ 折り目（前回と同じ）。
    τ = ∞ は当てはめず、w を除く共通の母数を評価の単位でも折り目の評価の単位でも使う。"""
    n = len(units)
    _, test = DT.split(n, 1, H_)
    ev = Eval(seqs_of([units[i] for i in test]), pflags_of([units[i] for i in test]))
    res = dict(fb=ev.ll_fb(), pool={}, mode={}, mode_zero_row={}, k={}, n_eval=int(ev.D.M.sum()))
    if keep_fits:
        res["fits"] = {}
    for k in ks:
        train, test2 = DT.split(n, k, H_)
        assert test2 == test
        tr_seqs = seqs_of([units[i] for i in train])
        _, h, T = H.r0_r1(tr_seqs)
        res["k"][str(k)] = dict(r1=ev.ll_r1(h, T), self={}, fold={}, diag={}, n_train=int(sum(len(s) for s in tr_seqs)))
    order = PREV_STRUCTS if structs is None else structs
    for s in order:
        if s in DROPPED and structs is None:
            if "m14" not in MUT:
                discard_draws(s, units, H_, ks, rng, do_folds)
            continue
        kind, K = s
        name = sname(s)
        pool_m, sb = pools[name]
        inf_m = full[name][0] if ("m11" in MUT and full is not None) else pool_m  # m11 は全員の共通を渡した呼び出しだけで効く
        res["pool"][name] = ev.ll(pool_m)
        res["mode"][name], res["mode_zero_row"][name] = mode_eval(ev, kind, pool_m, sb, full[name][1] if full else None, rng)
        for k in ks:
            train, _ = DT.split(n, k, H_)
            tr = [units[i] for i in train]
            D = H.Data(seqs_of(tr), chunk=H.CHUNK)
            _, h, T = H.r0_r1(seqs_of(tr))
            fits, diag = fit_self_all(kind, K, D, pool_m, sb, rng, h, T)
            if keep_fits:
                res["fits"].setdefault(name, {})[str(k)] = {str(t): fits[t] for t in TAUS_FIT}
            rk = res["k"][str(k)]
            rk["self"][name] = {str(t): ev.ll(fits[t]) for t in TAUS_FIT}
            rk["self"][name][INF] = ev.ll(inf_m)
            rk["diag"][name] = {str(t): dict(winner=diag[t]["winner"], gap12=diag[t]["gap12"], nonconv=diag[t]["nonconv"],
                                             decreases=diag[t]["decreases"]) for t in TAUS_FIT}
            fsum = {t: [0.0, 0] for t in TAU_KEYS}
            fds = DT.folds(train) if do_folds else []
            for fit_i, ev_i in fds:
                fu = [units[i] for i in fit_i]
                Df = H.Data(seqs_of(fu), chunk=H.CHUNK)
                _, hf, Tf = H.r0_r1(seqs_of(fu))
                ff, _ = fit_self_all(kind, K, Df, pool_m, sb, rng, hf, Tf)
                fev = Eval(seqs_of([units[i] for i in ev_i]), pflags_of([units[i] for i in ev_i]))
                for t in TAUS_FIT:
                    a, b = fev.sum_ll(ff[t])
                    fsum[str(t)][0] += a
                    fsum[str(t)][1] += b
                a, b = fev.sum_ll(inf_m)
                fsum[INF][0] += a
                fsum[INF][1] += b
            rk["fold"][name] = fsum if fds else None
    return res


# ---------------------------------------------------------------- 1 書き手（ワーカー）
_W = {}


def _init(paths, seed, mut):
    set_mut(mut)
    for ds, path in paths.items():
        _W[ds] = load(ds, path, seed)[0]


def load(ds, path, seed):
    if ds == "coauthor":
        return DT.load_coauthor(path, seed)
    return DT.load_cs1(path, seed, "block")


def eval_writer(job):
    t0 = time.time()
    writers = _W[job["ds"]] if job.get("writers") is None else job["writers"]
    cfg = DATASETS[job["ds"]]
    w, H_ = job["w"], cfg["H"]
    units = writers[w]
    rng = np.random.default_rng([job["seed"] + 10, job["wseq"]])
    out = dict(n=len(units), em=em_writer(units, H_, job["ks"], job["pools"], rng, full=job["full"]))
    out["sec"] = time.time() - t0
    return out


# ---------------------------------------------------------------- 選び（他人・本人の CV・2 段）
def select_other(values, w, cands, maximize=True):
    """values: {書き手: {候補: Δ}}。w を除く v の Δ の中央値を最大（または最小）にする候補。
    同点は cands の先（呼ぶ側で大きい τ・単純な構造を先に並べる）。m8 は w 自身を入れる。"""
    vs = [v for v in values if v != w or "m8" in MUT]
    best, bv = None, None
    for c in cands:
        xs = [values[v][c] for v in vs if values[v].get(c) is not None]
        if not xs:
            continue
        m = float(np.median(xs))
        if bv is None or (m > bv if maximize else m < bv):
            best, bv = c, m
    return best


def select_cv(fold, cands, maximize=True):
    """fold: {候補: [和, 数]}。数の 0 の候補は捨てる。同点は cands の先（呼ぶ側で大きい方・単純な方を先に並べる）。"""
    best, bv = None, None
    for c in cands:
        s, n = fold[c]
        if n == 0:
            continue
        v = s / n
        if bv is None or (v > bv if maximize else v < bv):
            best, bv = c, v
    return best


def joint_cands(structs=None):
    """2 段（他人）の候補 (構造名, τ) の並べ: 大きい τ（∞ が最も大きい）が先、同じ τ の中では自由な母数の少ない構造が先。"""
    ss = STRUCTS if structs is None else structs
    return [(sname(s), t) for t in sorted(TAU_KEYS, key=tau_val, reverse=True)
            for s in sorted(ss, key=lambda s: H.n_free(*s))]


def select_joint(values, w, cands):
    """2 段（他人）: values {書き手: {(構造名, τ): 本人 − r1}}。w を除く v の中央値がいちばん大きい組をまとめて選ぶ。
    w の値は選びに入れない（m12 は入れる）。同点は cands の先。"""
    vs = [v for v in values if v != w or "m12" in MUT]
    best, bv = None, None
    for c in cands:
        xs = [values[v][c] for v in vs if values[v].get(c) is not None]
        if not xs:
            continue
        m = float(np.median(xs))
        if bv is None or m > bv:
            best, bv = c, m
    return best


# ---------------------------------------------------------------- 集計の部品
def q(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    if len(xs) < N_MIN:
        return dict(n=len(xs), suppressed=True)
    a = np.array(xs, dtype=float)
    qs = np.quantile(a, [0.25, 0.5, 0.75], method="inverted_cdf")
    return dict(median=float(qs[1]), q25=float(qs[0]), q75=float(qs[2]), n=len(xs))


def boot_median(vals, rng):
    """中央値の区間。復元抽出の中央値がすべて有限なら前の試験と同じ式（linear）。∞ を含むときは linear が NaN を
    出す（両端が同じ符号の ∞ の補間）ので inverted_cdf で出す（m20 は linear のまま）。乱数はどちらでも同じに引く。
    返り値: (区間, 式の名前)。"""
    a = np.array([v for v in vals if v is not None], dtype=float)
    if len(a) < N_MIN:
        return None, None
    idx = rng.integers(0, len(a), (B_BOOT, len(a)))
    with np.errstate(invalid="ignore"):
        meds = np.median(a[idx], axis=1)
    if np.isnan(meds).any():
        raise ValueError("復元抽出の中央値に NaN（+∞ と −∞ が混ざった）")
    if np.isfinite(meds).all() or "m20" in MUT:
        with np.errstate(invalid="ignore"):
            return [float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))], "linear"
    return [float(np.quantile(meds, 0.025, method="inverted_cdf")),
            float(np.quantile(meds, 0.975, method="inverted_cdf"))], "inverted_cdf"


def delta_stats(d, rng, better_pos=True):
    d = [x for x in d if x is not None]
    if not d:
        return None
    if any(np.isnan(x) for x in d):
        raise ValueError("差に NaN がある")
    if len(d) < N_MIN:
        return dict(n=len(d), suppressed=True)
    r = q(d)
    r["better_share"] = float(np.mean([(x > 0) if better_pos else (x < 0) for x in d]))
    r["ci"], cm = boot_median(d, rng)
    if cm != "linear":
        r["ci_method"] = cm
    r["n_pos_inf"] = int(sum(x == np.inf for x in d))
    r["n_neg_inf"] = int(sum(x == -np.inf for x in d))
    return r


def enc(x):
    """JSON へ: ±∞ は文字列 "+inf" / "-inf"、NaN は誤り（判断 4）。numpy の数も Python の数にする。"""
    if isinstance(x, dict):
        return {(k if isinstance(k, str) else str(k)): enc(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [enc(v) for v in x]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        x = float(x)
        if np.isnan(x):
            raise ValueError("NaN を JSON に書こうとした")
        if np.isinf(x):
            return "+inf" if x > 0 else "-inf"
        return x
    return x


def dump_json(obj, path, indent=None):
    with open(path, "w") as f:
        json.dump(enc(obj), f, indent=indent, ensure_ascii=False, allow_nan=False)


# ---------------------------------------------------------------- 共通の母数の保存（判断 6・repo の外・書き手の ID は書かない）
def pool_arrays(full, pools, elig):
    """{鍵: 配列}。full: {構造名: (全員の共通の母数, S̄)}。pools: {書き手: {構造名: (母数, S̄)}}。書き手は elig の中の位置で書く。"""
    arr = {}
    for name, (m, sb) in full.items():
        for k in H.keys_of(m["kind"]):
            arr["full/%s/%s" % (name, k)] = m[k]
            arr["fullsbar/%s/%s" % (name, k)] = sb[k]
    for j, w in enumerate(elig):
        for name, (m, sb) in pools[w].items():
            for k in H.keys_of(m["kind"]):
                arr["excl/%d/%s/%s" % (j, name, k)] = m[k]
                arr["sbar/%d/%s/%s" % (j, name, k)] = sb[k]
    return arr


def content_hash(arr):
    """中身のハッシュ（鍵・dtype・shape・bytes を鍵の順に）。np.savez は ZIP の時刻が変わるのでファイルの SHA-256 は揺れる。"""
    import hashlib
    h = hashlib.sha256()
    for k in sorted(arr):
        a = np.ascontiguousarray(arr[k])
        h.update(k.encode())
        h.update(str(a.dtype).encode())
        h.update(str(a.shape).encode())
        h.update(a.tobytes())
    return h.hexdigest()


def save_pools(path, arr):
    """npz に書く（pickle なし）。m24 は float32 で書く。返り値: 中身のハッシュ（書いた物を読み戻して計る）。"""
    out = {k: (v.astype(np.float32) if "m24" in MUT else v) for k, v in arr.items()}
    np.savez(path, **out)
    with np.load(path, allow_pickle=False) as z:
        return content_hash({k: z[k] for k in z.files})


def count_vals(vs):
    out = {}
    for v in vs:
        out[str(v)] = out.get(str(v), 0) + 1
    n = sum(out.values())
    return out if n >= N_MIN else dict(n=n, suppressed=True)


def tau_region(taus):
    """選ばれた τ を「格子の中（100〜300,000）・下の端（0）・上の有限の端（10^6）・∞」で数える（conditions D5）。"""
    taus = [t for t in taus if t is not None]
    r = dict(inside=0, low_end=0, high_finite_end=0, inf=0)
    for t in taus:
        if t == INF:
            r["inf"] += 1
        elif t == "0":
            r["low_end"] += 1
        elif t == str(TAUS_FIT[-1]):
            r["high_finite_end"] += 1
        else:
            r["inside"] += 1
    return r if len(taus) >= N_MIN else dict(n=len(taus), suppressed=True)


# ---------------------------------------------------------------- 集計: EM
def panel_members(results, cfg, ns):
    """{パネル名: {k: [書き手]}}。主のパネルと副（各 k で n_w ≥ k + H）。"""
    out = {}
    for pn, (nmin, ks) in cfg["panels"].items():
        ws = [w for w in results if ns[w] >= nmin]
        out[pn] = {k: ws for k in ks}
    out["secondary"] = {k: [w for w in results if ns[w] >= k + cfg["H"]] for k in cfg["grid"]}
    return out


def em_values(results, ws, k, s):
    """Δ_v(τ) = 本人(τ) − 共通（同じ構造・w を除く）の評価の尤度（全記号）。τ = ∞ の Δ_v は 0。"""
    return {v: {t: me_of(results, v, k, sname(s), t, 0) - results[v]["em"]["pool"][sname(s)][0]
                for t in tau_cands()} for v in ws}


def joint_values(results, ws, k):
    """2 段（他人）の選びの量: {v: {(構造名, τ): 本人_v(構造, τ) − r1_v}}（全記号）。"""
    out = {}
    for v in ws:
        rk = results[v]["em"]["k"][str(k)]
        out[v] = {(sname(s), t): rk["self"][sname(s)][t][0] - rk["r1"][0] for s in STRUCTS for t in TAU_KEYS}
    return out


def pool_r1_values(results, ws, k, name, j):
    """書き手ごとの「共通 − r1」（w を除く共通の評価の尤度 − 本人の r1・j = 0 全記号・1 押下のある記号）。
    m13 は中央値どうしの差を全員に配る（書き手ごとの差ではない）。"""
    ps = [results[w]["em"]["pool"][name][j] for w in ws]
    rs = [results[w]["em"]["k"][str(k)]["r1"][j] for w in ws]
    if "m13" in MUT:
        ok = [(a, b) for a, b in zip(ps, rs) if a is not None and b is not None]
        d = float(np.median([a for a, _ in ok]) - np.median([b for _, b in ok])) if ok else None
        return [d] * len(ws)
    return [None if a is None or b is None else a - b for a, b in zip(ps, rs)]


def summarize_em(results, cfg, ns, rng):
    S = {}
    members = panel_members(results, cfg, ns)
    taus_desc = tau_cands()                                # τ 他人の候補（最頻値は入れない・m22 だけ入れる）
    taus_cv = sorted(TAU_KEYS, key=tau_val, reverse=True)  # τ 本人 CV の候補（折り目の量がある 9 値）
    for pn, kmap in members.items():
        P = {}
        for k, ws in kmap.items():
            if not ws:
                continue
            E = dict(writers=len(ws), structs={}, kcv={}, two_stage={},
                     n_train=q([results[w]["em"]["k"][str(k)]["n_train"] for w in ws]),
                     n_eval=q([results[w]["em"]["n_eval"] for w in ws]))
            chosen_other = {}
            for s in STRUCTS:
                name = sname(s)
                vals = em_values(results, ws, k, s)
                rows = {}
                for t in TAU_KEYS + [MODE]:
                    rows["tau_" + t] = {w: t for w in ws}
                rows["tau_other"] = {w: select_other(vals, w, taus_desc) for w in ws}
                chosen_other[name] = rows["tau_other"]
                if k >= 3:
                    rows["tau_cv"] = {w: select_cv(results[w]["em"]["k"][str(k)]["fold"][name], taus_cv) for w in ws}
                St = em_rows(results, ws, k, {r: {w: (name, t) for w, t in m.items()} for r, m in rows.items()}, rng)
                St["chosen_tau_other"] = count_vals(rows["tau_other"].values())
                St["chosen_tau_other_region"] = tau_region(rows["tau_other"].values())
                if k >= 3:
                    St["chosen_tau_cv"] = count_vals(rows["tau_cv"].values())
                    St["chosen_tau_cv_region"] = tau_region(rows["tau_cv"].values())
                St["pool_minus_r1"] = {lab: delta_stats(pool_r1_values(results, ws, k, name, j), rng)
                                       for j, lab in enumerate(("all", "pressed"))}
                St["diag"] = em_diag(results, ws, k, name)
                St["mode_counts"] = mode_counts(results, ws, name)
                St["finite_mode"] = finite_rows(results, ws, k, {"tau_" + t: {w: (name, t) for w in ws} for t in FINITE_ROWS}, rng)
                E["structs"][name] = St
            # 2 段（他人）: (構造, τ) を w を除く v の「本人 − r1」の中央値でまとめて選ぶ
            jv = joint_values(results, ws, k)
            jc = joint_cands()
            pick = {w: select_joint(jv, w, jc) for w in ws}
            T = em_rows(results, ws, k, {"two_stage_other": pick}, rng)
            T["chosen_struct"] = count_vals(p[0] if p else None for p in pick.values())
            T["chosen_tau"] = count_vals(p[1] if p else None for p in pick.values())
            T["chosen_tau_region"] = tau_region(p[1] if p else None for p in pick.values())
            T["finite_mode"] = finite_rows(results, ws, k, {"two_stage_other": pick}, rng)
            E["two_stage"]["other"] = T
            if k >= 3:
                # 2 段（構造は他人・τ は本人 CV）: 構造は v の「共通 − r1」の中央値（w を除く）、τ はその構造の中で本人の折り目
                sv = {v: {sname(s): results[v]["em"]["pool"][sname(s)][0] - results[v]["em"]["k"][str(k)]["r1"][0]
                          for s in STRUCTS} for v in ws}
                sc = [sname(s) for s in sorted(STRUCTS, key=lambda s: H.n_free(*s))]
                pick2 = {}
                for w in ws:
                    nm = select_other(sv, w, sc)
                    pick2[w] = (nm, select_cv(results[w]["em"]["k"][str(k)]["fold"][nm], taus_cv)) if nm else None
                T2 = em_rows(results, ws, k, {"two_stage_struct_other_tau_cv": pick2}, rng)
                T2["chosen_struct"] = count_vals(p[0] if p else None for p in pick2.values())
                T2["chosen_tau"] = count_vals(p[1] if p else None for p in pick2.values())
                T2["chosen_tau_region"] = tau_region(p[1] if p else None for p in pick2.values())
                E["two_stage"]["struct_other_tau_cv"] = T2
                # K 本人 CV（族は ar と both・各構造の τ は τ 他人の値）
                fams = {"ar": [s for s in STRUCTS if s[0] == "ar"], "both": list(STRUCTS)}
                for fam, ss in fams.items():
                    ss = sorted(ss, key=lambda s: H.n_free(*s))
                    pk = {}
                    for w in ws:
                        fold = results[w]["em"]["k"][str(k)]["fold"]
                        cand = {sname(s): fold[sname(s)][chosen_other[sname(s)][w]] for s in ss
                                if chosen_other[sname(s)][w] is not None}
                        nm = select_cv(cand, [sname(s) for s in ss if sname(s) in cand])
                        pk[w] = (nm, chosen_other[nm][w]) if nm is not None else (sname(ss[0]), None)
                    E["kcv"][fam] = em_rows(results, ws, k, {"k_cv": pk}, rng)
                    E["kcv"][fam]["chosen_struct"] = count_vals(p[0] for p in pk.values())
            P[str(k)] = E
        S[pn] = P
    return S


def me_of(results, w, k, name, t, j):
    """行の値: τ が最頻値なら res["mode"]、それ以外は k ごとの self。"""
    if t == MODE:
        return results[w]["em"]["mode"][name][j]
    return results[w]["em"]["k"][str(k)]["self"][name][t][j]


FINITE_ROWS = ["100000", "300000", "1000000", MODE]  # 副の集計の行（判断 10・読みの形の τ と最頻値の行）


def finite_writers(results, ws, name_of):
    """最頻値の全記号の量が有限の書き手（name_of: 書き手 → 構造名・None は除く）。m26 は −∞ の書き手を残す。"""
    out = []
    for w in ws:
        nm = name_of(w)
        if nm is None:
            continue
        if "m26" in MUT or np.isfinite(results[w]["em"]["mode"][nm][0]):
            out.append(w)
    return out


def finite_rows(results, ws, k, rows, rng):
    """副（判断 10）: rows {行: {書き手: (構造名, τ)}} を、行ごとに最頻値が有限の書き手だけで集計する。選びは呼ぶ側で全員で済ませてある。"""
    out = {}
    for r, pick in rows.items():
        wf = finite_writers(results, ws, lambda w: pick[w][0] if pick[w] is not None else None)
        out[r] = dict(writers=len(wf), stats=em_rows(results, wf, k, {r: {w: pick[w] for w in wf}}, rng)[r] if wf else None)
    return out


def mode_counts(results, ws, name):
    """構造ごとに、最頻値の全記号の量が −∞ の書き手と、和 0 の行に評価で当たった書き手の人数（判断 4・8）。"""
    return dict(writers=len(ws), neg_inf=int(sum(results[w]["em"]["mode"][name][0] == -np.inf for w in ws)),
                zero_row_hit=int(sum(bool(results[w]["em"]["mode_zero_row"][name]) for w in ws)))


def em_rows(results, ws, k, rows, rng):
    """rows: {行: {書き手: (構造名, τ)}}。相手: r1・同じ構造の共通・K = 3 のふつうの HMM の共通・F-b・同じ構造の最頻値。
    全記号と窓に押下のある記号。行 tau_mode × 相手 mode_same は 0（τ = ∞ × 同じ構造の共通と同じ扱い）。"""
    out = {}
    for r, pick in rows.items():
        o = {}
        for j, lab in enumerate(("all", "pressed")):
            for opp in OPPS:
                o[lab + "/self_minus_" + opp] = delta_stats(row_deltas(results, ws, k, pick, j, opp), rng)
        out[r] = o
    return out


def row_deltas(results, ws, k, pick, j, opp):
    """書き手ごとの差（行 − 相手）の並び（ws の順・None は除外の印）。em_rows と P-AB が使う。"""
    d = []
    for w in ws:
        name, t = pick[w] if pick[w] is not None else (None, None)
        if t is None:
            d.append(None)
            continue
        rk = results[w]["em"]["k"][str(k)]
        me = me_of(results, w, k, name, t, j)
        if opp == "mode_same" and t == MODE:
            d.append(None if me is None else 0.0)
            continue
        if opp == "mode_same" and "m19" in MUT and results[w]["em"]["mode"][name][0] == -np.inf:
            d.append(None)
            continue
        if t == MODE and "m19" in MUT and me == -np.inf:
            d.append(None)
            continue
        if opp == "r1":
            other = rk["r1"][j]
        elif opp == "pool_same":
            other = results[w]["em"]["pool"][name][j]
        elif opp == "pool_hmm3":
            other = results[w]["em"]["pool"]["hmm3"][j]
        elif opp == "mode_same":
            other = results[w]["em"]["mode"][name][j]
        else:
            other = results[w]["em"]["fb"][j]
        d.append(None if me is None or other is None else me - other)
    if opp == "mode_same" and "m21" in MUT:
        me_l = [me_of(results, w, k, *pick[w], j) for w in ws if pick[w] is not None]
        ot_l = [results[w]["em"]["mode"][pick[w][0]][j] for w in ws if pick[w] is not None]
        d = [float(np.median(me_l) - np.median(ot_l))] * len(d)
    return d


def em_diag(results, ws, k, name):
    out = {}
    for t in TAUS_FIT:
        ds = [results[w]["em"]["k"][str(k)]["diag"][name][str(t)] for w in ws]
        out[str(t)] = dict(winner=count_vals(d["winner"] for d in ds), gap12=q([d["gap12"] for d in ds]),
                           nonconv_starts=int(sum(d["nonconv"] for d in ds)), decreases=int(sum(d["decreases"] for d in ds)))
    return out


# ---------------------------------------------------------------- 本計算
def run(paths, seed, out, jobs, only_ds=None, run_id=None):
    raw = os.environ.get("GSE_ML_RAW")
    pools_out = os.environ.get("GSE_ML_POOLS")
    repo = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
    if raw and os.path.realpath(raw).startswith(repo + os.sep):
        sys.exit("GSE_ML_RAW が repo の中を指している（書き手ごとの値は repo の外だけ）")
    if pools_out and os.path.realpath(pools_out).startswith(repo + os.sep):
        sys.exit("GSE_ML_POOLS が repo の中を指している（共通の母数は repo の外だけ）")
    S = dict(run_id=run_id, datasets={})
    for ds in ([only_ds] if only_ds else ["coauthor", "cs1"]):
        cfg = DATASETS[ds]
        H_ = cfg["H"]
        t0 = time.time()
        writers, _ = load(ds, paths[ds], seed)
        ns = [len(ss) for ss in writers]
        elig = [i for i, n in enumerate(ns) if n >= H_ + 1]
        for i in elig:
            assert all(DT.check_split(ns[i], k, H_) for k in cfg["grid"] if k <= ns[i] - H_)
        ex = ProcessPoolExecutor(jobs, initializer=_init, initargs=({ds: paths[ds]}, seed, sorted(MUT)))
        # 1 段目: 全員の共通（構造ごと・乱数の通し番号は前回のまま）
        full = list(ex.map(fit_pool_full, [dict(ds=ds, si=SEQ_NO[s], seed=seed) for s in STRUCTS]))
        full_m = {sname(s): (full[i][0], full[i][2]) for i, s in enumerate(STRUCTS)}
        # w を除く共通（開始点は全員の共通の解）
        pj = [dict(ds=ds, w=w, start=full[si][0]) for w in elig for si in range(len(STRUCTS))]
        pres = list(ex.map(fit_pool_excl, pj, chunksize=1))
        pools = {}
        pdiag = []
        it = iter(pres)
        for w in elig:
            pools[w] = {}
            for s in STRUCTS:
                m, sb, d = next(it)
                pools[w][sname(s)] = (m, sb)
                pdiag.append((sname(s), d))
        if pools_out:
            S.setdefault("pool_params_content_sha256", {})[ds] = save_pools(pools_out + "." + ds + ".npz",
                                                                           pool_arrays(full_m, pools, elig))
        t1 = time.time()
        # 2 段目: 書き手ごと（書き手の通し番号は前回と同じ elig の中の位置）
        jl = [dict(ds=ds, w=w, wseq=j, seed=seed, ks=[k for k in cfg["grid"] if k <= ns[w] - H_], pools=pools[w], full=full_m)
              for j, w in enumerate(elig)]
        res = list(ex.map(eval_writer, jl, chunksize=1))
        ex.shutdown()
        results = {w: r for w, r in zip(elig, res)}
        if raw:
            # 集計か JSON が NaN で止まっても書き手の段の結果が残るように、先に pickle で書く（repo の外・人が開いて読まない）
            import pickle
            with open(raw + "." + ds + ".pkl", "wb") as fp:
                pickle.dump(results, fp)
            dump_json({ds: {str(k): v for k, v in results.items()}}, raw + "." + ds + ".json")
        rng = np.random.default_rng(seed + 4)
        D = dict(em=summarize_em(results, cfg, ns, rng))
        D["pool_full_diag"] = {sname(s): dict(winner=d["winner"], gap12=d["gap12"], nonconv=d["nonconv"], decreases=d["decreases"])
                               for s, (_, d, _) in zip(STRUCTS, full)}
        D["pool_excl_diag"] = {sname(s): dict(nonconv=int(sum(d["nonconv"] for n, d in pdiag if n == sname(s))),
                                              decreases=int(sum(d["decreases"] for n, d in pdiag if n == sname(s))),
                                              iters=q([d["iters"][0] for n, d in pdiag if n == sname(s)]))
                               for s in STRUCTS}
        D["four_tuple"] = dict(writers=len(elig), units_per_writer=q([ns[w] for w in elig]),
                               eval_symbols=int(sum(results[w]["em"]["n_eval"] for w in elig)),
                               questions="使わない", stall_episodes="使わない（0）")
        D["writers_total"] = len(writers)
        D["seconds"] = dict(pools=t1 - t0, writers=time.time() - t1, per_writer=q([r["sec"] for r in res]))
        S["datasets"][ds] = D
        dump_json(S, os.path.join(out, "summary.json"), indent=1)


if __name__ == "__main__":
    argv = sys.argv[1:]
    mut = []
    while "--mutate" in argv:
        i = argv.index("--mutate")
        mut.append(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    set_mut(mut)
    if argv[0] == "--selftest":
        import selftest
        only, run_id = None, None
        if "--only" in argv:
            i = argv.index("--only")
            only = argv[i + 1].split(",")
            argv = argv[:i] + argv[i + 2:]
        if "--run-id" in argv:
            i = argv.index("--run-id")
            run_id = argv[i + 1]
            argv = argv[:i] + argv[i + 2:]
        sys.exit(selftest.main(int(argv[1]), argv[2], only, sorted(mut), run_id))
    only_ds, run_id = None, None
    if "--run-id" in argv:
        i = argv.index("--run-id")
        run_id = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if "--only-dataset" in argv:
        i = argv.index("--only-dataset")
        only_ds = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    run({"coauthor": argv[0], "cs1": argv[1]}, int(argv[2]), argv[3], int(argv[4]), only_ds, run_id)
