"""漏れの統計（ADR-051 D3・設計 v2 §4・conditions.md）。numpy だけ。

入力: gse-replay --handmark-windows の表（NDJSON）と、pixels.mjs の画素の特徴（NDJSON・任意）。
出力: 集計だけの summary（JSON）。窓ごとの値・予測は書き出さない（本人の記録でも Claude が読むのは summary だけ）。

予測器:
  A        = 許した情報の特徴（22）
  B_state  = A + 描き直した状態の特徴（13）
  B_pixel  = A + 画素の特徴（16×10 の明るさと動きの平均 320 を学習の日だけで PCA して k 次元 + 全体の 5）
対象: T1（二値）・T2（3 値の一対他のマクロ AUC）。
"""
import json
import math
import os
import sys
import time

import numpy as np

# -I（隔離）で起動しても同じディレクトリの部品を読む
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict as V

LAMS = [1e-4, 1e-3, 1e-2, 1e-1, 1.0]   # 罰の強さ（平均の対数損失 + λ/2‖w‖²）
PCA_K = 12
PIX_COLS = 325   # 16×10 の動き 160・明るさ 160・全体の 5（pixels.mjs）
A2_BASE = ["n_press_30", "iki_median_30", "iki_cv_30", "max_gap_60", "since_last_press",
           "pauses_2s_30", "move_sum_30", "buttons_30"]
MIN_CLASS_WINDOWS = 50
MIN_CLASS_DAYS = 3
MIN_DAY_WINDOWS = 20
MIN_DAYS = 8
MAX_DROPPED_SHARE = 0.05
MUT = set()   # 変異（mutate.sh が設定する）
NONCONV = [0]   # ニュートン法が iters 回で収束しなかった回数（summary に書く）


# ---------------------------------------------------------------- 読み込み

def load_windows(path):
    header, rows, summary = None, [], None
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("kind") == "header":
                header = r
            elif r.get("kind") == "summary":
                summary = r
            else:
                rows.append(r)
    if header is None or summary is None:
        raise SystemExit(f"{path}: ヘッダか要約の行が無い")
    if [r.get("id") for r in rows] != list(range(len(rows))):
        raise SystemExit(f"{path}: 窓の番号が 0 からの連番でない")
    return header, rows, summary


def load_pixels(path, n, header):
    """画素の特徴を読む。1 行目のヘッダの標本の数と窓の数が、窓の表と合わなければ止める。"""
    pix = [None] * n
    with open(path, encoding="utf-8") as f:
        head = json.loads(f.readline())
        if head.get("kind") != "header" or head.get("samples") != header["samples"] or head.get("windows") != n:
            raise SystemExit(f"{path}: 画素の特徴が窓の表と合わない（{head}）")
        for line in f:
            r = json.loads(line)
            i, v = r.get("id"), r.get("v")
            if not isinstance(i, int) or isinstance(i, bool) or not 0 <= i < n or pix[i] is not None:
                raise SystemExit(f"{path}: 窓の番号が範囲の外か重なる（{i}）")
            if not isinstance(v, list) or len(v) != PIX_COLS or not all(
                    isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in v):
                raise SystemExit(f"{path}: 窓 {i} の画素の特徴が {PIX_COLS} 個の有限の数でない")
            pix[i] = v
    if any(p is None for p in pix):
        raise SystemExit(f"{path}: 画素の特徴が欠けた窓がある")
    return np.asarray(pix, dtype=float)


# ---------------------------------------------------------------- 回帰と AUC

def sigmoid(z):
    return 0.5 * (1.0 + np.tanh(0.5 * z))


def fit_logistic(X, y, lam, iters=100, tol=1e-9):
    """平均の対数損失 + λ/2‖w‖²（切片は罰さない）をニュートン法で最小にする。X は標準化済み。"""
    n, d = X.shape
    Xa = np.hstack([np.ones((n, 1)), X])
    beta = np.zeros(d + 1)
    pen = np.full(d + 1, lam)
    pen[0] = 0.0
    if "m4" in MUT:
        pen[0] = lam   # 変異: 切片も罰する
    for _ in range(iters):
        p = sigmoid(Xa @ beta)
        g = Xa.T @ (p - y) / n + pen * beta
        w = p * (1 - p) / n
        H = (Xa * w[:, None]).T @ Xa + np.diag(pen) + 1e-12 * np.eye(d + 1)
        step = np.linalg.solve(H, g)
        beta -= step
        if np.max(np.abs(step)) < tol:
            break
    else:
        NONCONV[0] += 1
    return beta


def predict(beta, X):
    return sigmoid(beta[0] + X @ beta[1:])


def auc(score, y, weight=None):
    """Mann–Whitney の AUC（同点は 0.5）。weight は窓ごとの重み（引き直しの回数）。片方のクラスが無ければ nan。"""
    return Ranked(score, y).auc(np.ones(len(y)) if weight is None else np.asarray(weight, dtype=float))


class Ranked:
    """値の並べ替えを 1 回だけにして、重みを変えた AUC を何度も出す（予測を固定した日の引き直し用）。

    同じ値の塊ごとに: 塊の中の陽性 × (塊より下の陰性 + 塊の中の陰性 / 2) を足し、陽性 × 陰性で割る。
    """

    def __init__(self, score, y):
        _, self.inv = np.unique(np.asarray(score, dtype=float), return_inverse=True)
        self.y = np.asarray(y)
        self.n = int(self.inv.max()) + 1 if len(self.inv) else 0

    def auc(self, w):
        wp = np.where(self.y == 1, w, 0.0)
        wn = np.where(self.y == 0, w, 0.0)
        pos, neg = wp.sum(), wn.sum()
        if pos == 0 or neg == 0:
            return float("nan")
        bp = np.bincount(self.inv, weights=wp, minlength=self.n)
        bn = np.bincount(self.inv, weights=wn, minlength=self.n)
        below = np.cumsum(bn) - bn
        return float((bp * (below + 0.5 * bn)).sum() / (pos * neg))


def logloss(p, y):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


# ---------------------------------------------------------------- 特徴の組み立て（学習の日だけで当てる）

class Design:
    """予測器の特徴の作り方。fit(tr) で学習の窓だけから標準化・PCA を決め、X(idx) を返す。"""

    def __init__(self, fixed, pix=None, pix_scalars=None, k=PCA_K):
        self.fixed = fixed            # 窓 × 列（そのまま使う）
        self.pix = pix                # 窓 × 320（学習の日で PCA）
        self.pix_scalars = pix_scalars
        self.k = k

    def fit(self, tr):
        self.mu_pix = None
        if self.pix is not None:
            P = self.pix[tr]
            self.mu_pix = P.mean(axis=0)
            _, _, vt = np.linalg.svd(P - self.mu_pix, full_matrices=False)
            self.comp = vt[: self.k].T
        cols = self._raw(tr)
        self.mu = cols.mean(axis=0)
        sd = cols.std(axis=0)
        sd[sd == 0] = 1.0
        self.sd = sd
        return self

    def _raw(self, idx):
        parts = [self.fixed[idx]]
        if self.pix is not None:
            parts.append((self.pix[idx] - self.mu_pix) @ self.comp)
            parts.append(self.pix_scalars[idx])
        return np.hstack(parts)

    def X(self, idx):
        return (self._raw(idx) - self.mu) / self.sd


def fit_predict(design, y, tr, te, lam):
    """学習の窓で当て、試す窓の予測を返す。学習にクラスが欠ければ、学習の割合の定数（conditions.md）。"""
    ytr = y[tr]
    if ytr.min() == ytr.max():
        return np.full(len(te), float(ytr.mean())), True
    d = design.fit(tr)
    beta = fit_logistic(d.X(tr), ytr, lam)
    return predict(beta, d.X(te)), False


INNER_FOLDS = 5   # λ を選ぶ内側の検証の分割の数（日をまとめる・計算を抑えるため。conditions.md C3）


def inner_folds(days):
    """学習の日を時刻の順に並べ、順に INNER_FOLDS 個の組に配る（日を分けない）。"""
    days = np.sort(days)
    k = min(INNER_FOLDS, len(days))
    return [days[i::k] for i in range(k)]


def choose_lambda(design, y, groups, tr):
    """学習の日を日ごとの組に分けて抜き、平均の対数損失が最小の λ（同点は大きい方＝強い罰）。"""
    folds = inner_folds(np.unique(groups[tr]))
    best = None
    for lam in LAMS:
        losses = []
        for fd in folds:
            mask = np.isin(groups[tr], fd)
            itr = tr[~mask]
            ite = tr[mask]
            p, _ = fit_predict(design, y, itr, ite, lam)
            losses.append(logloss(p, y[ite]) * len(ite))
        loss = sum(losses) / len(tr)
        if best is None or loss <= best[0] + 1e-12:  # LAMS は昇順なので、同点は強い罰
            best = (loss, lam)
    return best[1]


def lodo(design, y, groups, lam=None):
    """1 日ずつ抜く交差検証の予測（全部の窓）。lam が None なら折り目ごとに内側で選ぶ。"""
    pred = np.empty(len(y))
    lams, const = [], 0
    for d in np.unique(groups):
        tr = np.where(groups != d)[0]
        te = np.where(groups == d)[0]
        l = choose_lambda(design, y, groups, tr) if lam is None else lam
        lams.append(l)
        pred[te], c = fit_predict(design, y, tr, te, l)
        const += int(c)
    return pred, lams, const


# ---------------------------------------------------------------- 引き直し

def boot_days(rng, days):
    return rng.choice(days, size=len(days), replace=True)


def weights_for(sample, groups):
    """引き直した日の回数を窓の重みにする（AUC を引き直した日を合わせて計算する）。"""
    days, gi = np.unique(groups, return_inverse=True)
    cnt = np.bincount(np.searchsorted(days, sample), minlength=len(days)).astype(float)
    return cnt[gi]


def target_auc(preds, ys, w):
    """対象の AUC。preds・ys は一対他の列（T1 は 1 本・T2 は 3 本）。どれかが nan なら nan（クラス欠け）。"""
    vals = [auc(p, yy, w) for p, yy in zip(preds, ys)]
    if any(math.isnan(v) for v in vals):
        return float("nan")
    return float(np.mean(vals))


def interval(vals):
    return float(np.quantile(vals, 0.05)), float(np.quantile(vals, 0.95))


def fixed_bootstrap(pa, pb, ys, groups, R, rng):
    """予測を固定して日を引き直す。返り値は (差の標本, A の AUC の標本, 落とした数)。"""
    days = np.unique(groups)
    ra = [Ranked(p, yy) for p, yy in zip(pa, ys)]
    rb = [Ranked(p, yy) for p, yy in zip(pb, ys)]
    diffs, aucs_a, dropped = [], [], 0
    for _ in range(R):
        s = boot_days(rng, days)
        if "m2" in MUT:
            # 変異: 日でなく窓の単位で引き直す
            w = np.bincount(rng.integers(0, len(groups), len(groups)), minlength=len(groups)).astype(float)
        else:
            w = weights_for(s, groups)
        va = [r.auc(w) for r in ra]
        vb = [r.auc(w) for r in rb]
        if any(math.isnan(v) for v in va + vb):
            dropped += 1
            continue
        a, b = float(np.mean(va)), float(np.mean(vb))
        diffs.append(b - a)
        aucs_a.append(a)
    return np.array(diffs), np.array(aucs_a), dropped


def nested_bootstrap(design_a, design_b, ys_onevsrest, groups, lams, R, rng):
    """日を引き直し、引き直した標本の中で 1 日ずつ抜く学習をやり直す（λ は主の解析で選んだ値に固定）。

    同じ元の日の写しは一緒に抜く（元の日を単位に抜く）。
    """
    days = np.unique(groups)
    diffs, aucs_a, dropped = [], [], 0
    for _ in range(R):
        s = boot_days(rng, days)
        idx = np.concatenate([np.where(groups == d)[0] for d in s])
        g = groups[idx]
        pa_all, pb_all = [], []
        ok = True
        for k, yfull in enumerate(ys_onevsrest):
            yy = yfull[idx]
            if yy.min() == yy.max():
                ok = False
                break
            pa = np.empty(len(idx))
            pb = np.empty(len(idx))
            for d in np.unique(g):
                tr = np.where(g != d)[0]
                te = np.where(g == d)[0]
                pa[te], _ = fit_predict(_Sub(design_a, idx), yy, tr, te, lams["A"][k])
                pb[te], _ = fit_predict(_Sub(design_b, idx), yy, tr, te, lams["B"][k])
            pa_all.append(pa)
            pb_all.append(pb)
        if not ok:
            dropped += 1
            continue
        ys = [yfull[idx] for yfull in ys_onevsrest]
        a = target_auc(pa_all, ys, None)
        b = target_auc(pb_all, ys, None)
        if math.isnan(a) or math.isnan(b):
            dropped += 1
            continue
        diffs.append(b - a)
        aucs_a.append(a)
    return np.array(diffs), np.array(aucs_a), dropped


class _Sub:
    """引き直した窓の列（idx）の上で Design を使う。"""

    def __init__(self, design, idx):
        self.d = design
        self.idx = idx

    def fit(self, tr):
        self.d.fit(self.idx[tr])
        return self

    def X(self, sub):
        return self.d.X(self.idx[sub])


def mode_lambda(lams):
    vals, cnt = np.unique(lams, return_counts=True)
    return float(vals[np.argmax(cnt)])


# ---------------------------------------------------------------- 本体

def class_check(y_cols, groups):
    """クラスの最小の数（conditions.md 1）。各一対他の列の陽性クラスについて、窓の数と日の数を数える。"""
    out = []
    for yy in y_cols:
        out.append({
            "windows": int(yy.sum()),
            "days": int(len(np.unique(groups[yy == 1]))),
            "neg_windows": int((1 - yy).sum()),
            "neg_days": int(len(np.unique(groups[yy == 0]))),
        })
    ok = all(c["windows"] >= MIN_CLASS_WINDOWS and c["days"] >= MIN_CLASS_DAYS
             and c["neg_windows"] >= MIN_CLASS_WINDOWS and c["neg_days"] >= MIN_CLASS_DAYS for c in out)
    return ok, out


def analyse(rows, header, pix, seed, R=2000, R_nested=0, diagnostics=True, day_filter=None):
    """全体を回して集計を返す。day_filter は感度分析で使う日の集合（None なら全部）。"""
    t_start = time.time()
    NONCONV[0] = 0

    def stream(*key):
        """(対象・B・方式) ごとに別の乱数の流れ（判定に入れない処理の有無で、主の標本が変わらないように）。"""
        return np.random.default_rng([seed, *key])

    if day_filter is not None:
        keep = [i for i, r in enumerate(rows) if r["day"] in day_filter]
        rows = [rows[i] for i in keep]
        pix = pix[keep] if pix is not None else None
    groups = np.array([r["day"] for r in rows])
    A = np.array([r["a"] for r in rows], dtype=float)
    Bs = np.array([r["b_state"] for r in rows], dtype=float)
    t1 = np.array([r["t1"] for r in rows], dtype=float)
    t1_all = np.array([r["t1_all"] for r in rows], dtype=float)
    since = np.array([r["t_since_t0"] for r in rows], dtype=float) / 1000.0
    t2 = np.array([r["t2"] for r in rows])
    if "m1" in MUT:
        A, Bs = np.hstack([A, Bs]), A   # 変異: A と B を入れ替える（A に見た目を入れる）
    day_counts = {int(d): int((groups == d).sum()) for d in np.unique(groups)}
    good_days = sum(1 for v in day_counts.values() if v >= MIN_DAY_WINDOWS)
    out = {
        "n_windows": len(rows),
        "n_days": len(day_counts),
        "days_with_min_windows": good_days,
        "day_gate_passed": good_days >= MIN_DAYS,   # C6 の日数の門（越えなければ回に数えない・S1-F5）
        "targets": {},
    }
    if good_days < MIN_DAYS:
        out["overall"] = V.UNDETERMINED
        out["reason"] = f"有効な窓が {MIN_DAY_WINDOWS} 以上の日が {good_days} 日（{MIN_DAYS} 日未満）"
        return out
    designs = {"A": Design(A), "state": Design(np.hstack([A, Bs]))}
    if pix is not None:
        designs["pixel"] = Design(A, pix=pix[:, :320], pix_scalars=pix[:, 320:])
    if diagnostics:
        perm = Bs.copy()
        prng = stream(99)
        for d in np.unique(groups):
            ii = np.where(groups == d)[0]
            perm[ii] = Bs[prng.permutation(ii)]
        designs["state_perm"] = Design(np.hstack([A, perm]))
        names = header["a_names"]
        base = A[:, [names.index(n) for n in A2_BASE]]
        extra = [base ** 2]
        for i in range(len(A2_BASE)):
            for j in range(i + 1, len(A2_BASE)):
                extra.append((base[:, i] * base[:, j])[:, None])
        designs["A2"] = Design(np.hstack([A] + extra))
        # 経過時間（区間の始まりからの秒）を A に足したもの。画素には drift（経過時間）が写るので、
        # B_pixel の上積みが経過時間で説明できるかを見る（判定には入れない・レビューの指摘 7）
        designs["A_time"] = Design(np.hstack([A, since[:, None], np.log1p(since)[:, None]]))
    targets = {"T1": [t1], "T2": [(t2 == k).astype(float) for k in range(3)]}
    per_target = {}
    out["t1_all_windows"] = int(t1_all.sum())   # C1 の副（判定には使わない）
    for ti, (tname, ys) in enumerate(targets.items()):
        ok, counts = class_check(ys, groups)
        res = {"class_counts": counts}
        if not ok:
            res["verdict"] = V.UNDETERMINED
            res["reason"] = "クラスの最小の数を満たさない"
            per_target[tname] = res
            out["targets"][tname] = res
            continue
        preds, lams = {}, {}
        for dn, des in designs.items():
            cols, lcols, consts = [], [], 0
            for yy in ys:
                p, ls, c = lodo(des, yy, groups)
                cols.append(p)
                lcols.append(mode_lambda(ls))
                consts += c
            preds[dn] = cols
            lams[dn] = lcols
            res.setdefault("const_folds", {})[dn] = consts
        res["auc"] = {dn: target_auc(p, ys, None) for dn, p in preds.items()}
        res["lambda"] = lams
        per_b = {}
        for bi, bn in enumerate(b for b in ("state", "pixel") if b in preds):
            diffs, aa, dropped = fixed_bootstrap(preds["A"], preds[bn], ys, groups, R, stream(ti, bi, 0))
            info = judge(diffs, aa, dropped, R)
            info["diff"] = res["auc"][bn] - res["auc"]["A"]
            if R_nested:
                nd, na, ndrop = nested_bootstrap(designs["A"], designs[bn], ys, groups,
                                                 {"A": lams["A"], "B": lams[bn]}, R_nested, stream(ti, bi, 1))
                info["nested"] = judge(nd, na, ndrop, R_nested)
            per_b[bn] = (info["verdict"], info["ceiling"])
            res[bn] = info
        for bn in ("state", "pixel"):
            if bn not in per_b:
                # B の 2 つがそろわなければ「満たす」にしない（/cross-review の指摘）
                per_b[bn] = (V.UNDETERMINED, False)
                res[bn] = {"verdict": V.UNDETERMINED, "ceiling": False, "reason": "特徴が無い"}
        if diagnostics:
            for dn in ("state_perm", "A2", "A_time"):
                res.setdefault("diagnostics", {})[dn] = res["auc"][dn] - res["auc"]["A"]
        res["verdict"], res["ceiling"] = V.target_verdict(per_b)
        per_target[tname] = res
        out["targets"][tname] = res
    v = V.combine_both(per_target["T1"]["verdict"], per_target["T2"]["verdict"])
    out["overall"] = v
    out["newton_nonconverged"] = NONCONV[0]
    out["seconds"] = round(time.time() - t_start, 1)
    return out


def with_sensitivity(rows, header, pix, seed, R=2000, R_nested=0, diagnostics=True, sensitivity=True, late_days=0):
    """主（全部の窓）と感度分析（`sens` の印の窓・conditions C7）を回し、ADR-051 D3 の表で合わせる。

    返り値は主の集計に `sensitivity` と `combined` を足したもの。`overall` は主のまま（合成の対照と同じ読み）。
    感度分析では診断と入れ子は回さない（判定だけを使う）。
    - sensitivity=False（回 1 = early・事前登録 S1-F5）: 回さず「未実施」。
    - 後期の「あり」の日（late_days）が 1 日も無い: 「未実施」。
    - 後期の「あり」の日はあるが C7 で全部除いた: 「判定不能」（除外が多いほど甘くならないように・/cross-review 指摘 8）。
    """
    res = analyse(rows, header, pix, seed, R=R, R_nested=R_nested, diagnostics=diagnostics)
    idx = [i for i, r in enumerate(rows) if r.get("sens") is True]
    if not sensitivity:
        sens = {"overall": V.NOT_RUN, "n_windows": 0, "reason": "回 1（early）では感度分析を回さない（S1-F5）"}
    elif not idx and late_days > 0:
        sens = {"overall": V.UNDETERMINED, "n_windows": 0,
                "reason": "後期の「あり」の日はあるが、C7 の条件で全部の日を除いた"}
    elif idx:
        sens = analyse([rows[i] for i in idx], header, pix[idx] if pix is not None else None, seed + 1,
                       R=R, diagnostics=False)
    else:
        sens = {"overall": V.NOT_RUN, "n_windows": 0, "reason": "感度分析の窓が無い（後期の「あり」の日がまだ無い）"}
    overall, provisional = V.combine_main_sensitivity(res["overall"], sens["overall"])
    res["sensitivity"] = sens
    res["combined"] = {"main": res["overall"], "sensitivity": sens["overall"], "overall": overall,
                       "provisional_meets": provisional}
    return res


def holdout_truth(rows, pix):
    """母集団の差の近似（S5・conditions C4）: 日を偶奇で二つに分け、片方で学習（λ は内側で選ぶ）して
    もう片方の AUC(B) − AUC(A) を出し、向きを入れ替えた 2 回の平均。大きな合成でだけ使う。"""
    groups = np.array([r["day"] for r in rows])
    A = np.array([r["a"] for r in rows], dtype=float)
    Bs = np.array([r["b_state"] for r in rows], dtype=float)
    t1 = np.array([r["t1"] for r in rows], dtype=float)
    t2 = np.array([r["t2"] for r in rows])
    designs = {"A": Design(A), "state": Design(np.hstack([A, Bs]))}
    if pix is not None:
        designs["pixel"] = Design(A, pix=pix[:, :320], pix_scalars=pix[:, 320:])
    days = np.unique(groups)
    halves = [np.isin(groups, days[0::2]), np.isin(groups, days[1::2])]
    out = {}
    for tname, ys in {"T1": [t1], "T2": [(t2 == k).astype(float) for k in range(3)]}.items():
        diffs = {b: [] for b in designs if b != "A"}
        for h in (0, 1):
            tr, te = np.where(halves[h])[0], np.where(halves[1 - h])[0]
            aucs = {}
            for dn, des in designs.items():
                vals = []
                for yy in ys:
                    lam = choose_lambda(des, yy, groups, tr)
                    p, _ = fit_predict(des, yy, tr, te, lam)
                    vals.append(auc(p, yy[te]))
                aucs[dn] = float(np.mean(vals))
            for b in diffs:
                diffs[b].append(aucs[b] - aucs["A"])
        out[tname] = {b: float(np.mean(v)) for b, v in diffs.items()}
    return {"n_windows": len(rows), "n_days": int(len(days)), "truth": out}


def judge(diffs, aucs_a, dropped, R):
    """引き直しの標本から 3 値と天井（固定の予測と入れ子で同じ規則・conditions C5・C6）。"""
    info = {"dropped": dropped, "kept": len(diffs)}
    if dropped > MAX_DROPPED_SHARE * R or len(diffs) == 0:
        info.update({"verdict": V.UNDETERMINED, "ceiling": False, "reason": "引き直しで欠けた標本が 5% を超えた"})
        return info
    lo, hi = interval(diffs)
    a_lo = float(np.quantile(aucs_a, 0.05))
    if "m3" in MUT:
        v = V.MEETS if a_lo > 1 - V.DELTA else V.three_valued(lo, hi)   # 変異: 天井を差と別の経路に
        c = a_lo > 1 - V.DELTA
    else:
        v, c = V.with_ceiling(lo, hi, a_lo)
    info.update({"ci90": [lo, hi], "auc_a_lo": a_lo, "verdict": v, "ceiling": c})
    return info


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("windows")
    ap.add_argument("--pixels")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--R", type=int, default=2000)
    ap.add_argument("--R-nested", type=int, default=0)
    ap.add_argument("--no-diagnostics", action="store_true")
    ap.add_argument("--mut", default="")
    ap.add_argument("--truth", action="store_true", help="母集団の差の近似だけを出す（S5）")
    ap.add_argument("--no-sensitivity", action="store_true", help="感度分析を回さない（回 1 = early・S1-F5）")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    MUT.update(x for x in a.mut.split(",") if x)
    header, rows, summary = load_windows(a.windows)
    pix = load_pixels(a.pixels, len(rows), header) if a.pixels else None
    if a.truth:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(holdout_truth(rows, pix), f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
        return
    late = (summary.get("sensitivity") or {}).get("late_days", 0)
    res = with_sensitivity(rows, header, pix, a.seed, R=a.R, R_nested=a.R_nested, diagnostics=not a.no_diagnostics,
                           sensitivity=not a.no_sensitivity, late_days=late)
    res["desk"] = {k: header[k] for k in ("desk_version", "labels", "inject_stuck", "samples", "table_sha256")}
    # 日の番号は暦の日付に戻せるので、summary には数だけを書く（security-checker LOW）
    res["desk_summary"] = {k: summary[k] for k in ("windows", "excluded", "segments", "segments_recorded_t0",
                                                  "label_check")}
    res["desk_summary"]["seed_mismatch_days"] = len(summary.get("seed_mismatch_days", []))
    res["desk_summary"]["overflow_days"] = len(summary.get("overflow_days", []))
    res["desk_summary"]["sensitivity"] = summary.get("sensitivity")
    res["desk_summary"]["redactions_given"] = summary.get("redactions_given")
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
