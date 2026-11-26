"""経過が読めないことの確かめ (i)〜(iii)（ADR-056 D2・判断 9・conditions.md E3〜E5）。numpy だけ。

入力: queries.py の items.json と、overlay.mjs queries の明るさ（float32 × 160 × 問い合わせ）。
出力: 集計だけの summary（JSON）。項目ごとの値・予測は書き出さない（本人の記録でも Claude が読むのは summary だけ）。

特徴:
  (i)        1 対（q − 250 と q）: 明るさ L(q) 160 と動き |L(q) − L(q − 250)| 160
  (ii)(iii)  30 秒の列（1 秒おき 30 枚）: L の時間の平均 160・時間の標準偏差 160・隣どうしの差の絶対値の平均 160
予測: 1 日ずつ抜く交差検証（ADR-051 D3 と同じ分け方・止まりは日の中に入るので、止まりも分かれない）。
  学習の日だけで標準化 → PCA（k = 12）→ 主成分を単位分散に。対象は log(ラベルの秒)。
  予測器 2 つ（どちらも調整なし）: リッジ（λ = 1）と k 近傍（k = 15・平均）。
  当てやすさ = 抜いた日の予測を全部合わせた、予測と真のラベルの Spearman の順位相関。統計量 = 2 つの最大。
帰無: 日の中で、止まりの単位でラベルの組を入れ替える（R 回）。入れ替えた世界でも学習から全部やり直し、
  入れ替えたラベルとの順位相関の最大を取る。観測がその 95 パーセント点を超えたら「偶然を上回った」（片側 5%）。
"""
import json
import math
import os
import sys

import numpy as np

PCA_K = 12
RIDGE_LAM = 1.0
KNN_K = 15
NPIX = 160
MIN_DAYS = 2
MUT = set()   # 変異（selftest が設定する）


def rankdata(x):
    """平均順位（同点は平均）。"""
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=float)
    xs = x[order]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0
        i = j + 1
    return ranks


def spearman(a, b):
    ra, rb = rankdata(a), rankdata(b)
    ra -= ra.mean()
    rb -= rb.mean()
    d = math.sqrt(float((ra * ra).sum()) * float((rb * rb).sum()))
    return float((ra * rb).sum() / d) if d > 0 else 0.0


def features(items, lum, test):
    rows = []
    for it in items:
        frames = lum[it["q"]]
        if test == "i":
            prev, cur = frames
            rows.append(np.concatenate([cur, np.abs(cur - prev)]))
        else:
            rows.append(np.concatenate([frames.mean(0), frames.std(0), np.abs(np.diff(frames, axis=0)).mean(0)]))
    return np.asarray(rows, dtype=float)


class Folds:
    """1 日ずつ抜く折り目ごとに、ラベルに依らない部分（標準化・PCA・リッジの射影・近傍）を先に作る。"""

    def __init__(self, X, days):
        self.folds = []
        for d in np.unique(days):
            te = np.where(days == d)[0]
            tr = np.where(days != d)[0]
            if len(tr) < KNN_K + 2 or len(te) == 0:
                continue
            mu = X[tr].mean(0)
            sd = X[tr].std(0)
            sd[sd == 0] = 1.0
            Ztr = (X[tr] - mu) / sd
            Zte = (X[te] - mu) / sd
            k = min(PCA_K, Ztr.shape[0] - 1, Ztr.shape[1])
            _, _, vt = np.linalg.svd(Ztr - Ztr.mean(0), full_matrices=False)
            P = vt[:k].T
            Ptr, Pte = Ztr @ P, Zte @ P
            c = Ptr.mean(0)
            s = Ptr.std(0)
            s[s == 0] = 1.0
            Ptr, Pte = (Ptr - c) / s, (Pte - c) / s
            # リッジ: 予測 = 平均(y) + Pte (PtrᵀPtr + λI)⁻¹ Ptrᵀ (y − 平均(y))
            G = np.linalg.solve(Ptr.T @ Ptr + RIDGE_LAM * np.eye(k), Ptr.T)
            Hr = Pte @ G
            d2 = (Pte ** 2).sum(1)[:, None] + (Ptr ** 2).sum(1)[None, :] - 2 * Pte @ Ptr.T
            nn = np.argsort(d2, axis=1, kind="mergesort")[:, :KNN_K]
            self.folds.append((tr, te, Hr, nn))

    def predict(self, y):
        pr = np.empty(len(y))
        pk = np.empty(len(y))
        covered = np.zeros(len(y), dtype=bool)
        for tr, te, Hr, nn in self.folds:
            ytr = y[tr]
            m = ytr.mean()
            pr[te] = m + Hr @ (ytr - m)
            pk[te] = ytr[nn].mean(1)
            covered[te] = True
        return pr[covered], pk[covered], covered


def permute_blocks(rng, labels, stops, days):
    """日の中で、止まりの単位でラベルの組を入れ替える（組の中は時刻の順のまま）。"""
    out = labels.copy()
    for d in np.unique(days):
        idx_d = np.where(days == d)[0]
        st = np.unique(stops[idx_d])
        if len(st) < 2:
            continue
        blocks = [idx_d[stops[idx_d] == s] for s in st]
        sizes = {len(b) for b in blocks}
        if len(sizes) != 1:
            raise SystemExit("止まりあたりの項目の数がそろっていない（入れ替えられない）")
        perm = rng.permutation(len(blocks))
        for b, p in zip(blocks, perm):
            out[b] = labels[blocks[p]]
    return out


def score(folds, y):
    pr, pk, covered = folds.predict(y)
    yt = y[covered]
    rr, rk = spearman(pr, yt), spearman(pk, yt)
    return rr, rk, max(rr, rk)


def analyse(items, lum, test, seed, R):
    its = [it for it in items if it["test"] == test]
    out = {"n_items": len(its)}
    if not its:
        out["verdict"] = "undetermined"
        out["reason"] = "項目が無い"
        return out
    # 止まりの中は時刻の順（ラベルの順）に並べる（組を入れ替えるとき、組の中の対応を時刻の順にする）
    its.sort(key=lambda it: (it["day"], it["stop"], it["label"]))
    days = np.array([it["day"] for it in its])
    stops = np.array([it["stop"] for it in its])
    labels = np.log(np.maximum(np.array([it["label"] for it in its], dtype=float), 1.0) / 1000.0)
    X = features(its, lum, test)
    if "leak" in MUT:
        X = np.hstack([X, labels[:, None] * np.ones((1, 4))])   # 変異: ラベルを特徴に入れる（陽性対照）
    n_days = len(np.unique(days))
    out.update({"n_stops": int(len(np.unique(stops))), "n_days": int(n_days),
                "label_s": {"min": float(np.exp(labels.min())), "median": float(np.exp(np.median(labels))),
                            "max": float(np.exp(labels.max()))}})
    if n_days < MIN_DAYS:
        out["verdict"] = "undetermined"
        out["reason"] = f"日が {n_days}（{MIN_DAYS} 未満）"
        return out
    folds = Folds(X, days)
    # 学習の項目が足りずに落ちた折り目があれば、数えずに「決まらない」にする（黙って一部の日だけで判定しない）
    n_scored = sum(len(te) for _, te, _, _ in folds.folds)
    if n_scored != len(its):
        out["verdict"] = "undetermined"
        out["reason"] = f"学習の項目が {KNN_K + 2} 未満の折り目がある（{len(its)} 項目のうち {n_scored} だけ予測できる）"
        return out
    rr, rk, stat = score(folds, labels)
    rng = np.random.default_rng([seed, {"i": 1, "ii": 2, "iii": 3}[test]])
    null = np.empty(R)
    for r in range(R):
        yp = permute_blocks(rng, labels, stops, days)
        null[r] = score(folds, yp)[2]
    q95 = float(np.quantile(null, 0.95))
    above = stat > q95
    if "flip" in MUT:
        above = not above
    out.update({
        "rho_ridge": rr, "rho_knn": rk, "stat": stat,
        "null": {"R": R, "q95": q95, "q05": float(np.quantile(null, 0.05)), "mean": float(null.mean()),
                 "sd": float(null.std())},
        "p": float((1 + (null >= stat).sum()) / (R + 1)),
        "verdict": "above_chance" if above else "not_above_chance",
    })
    return out


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("items")
    ap.add_argument("--lum", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--R", type=int, default=1000)
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    with open(a.items, encoding="utf-8") as f:
        meta = json.load(f)
    lum = np.fromfile(a.lum, dtype=np.float32).astype(float)
    if lum.size != meta["n_queries"] * NPIX:
        raise SystemExit(f"明るさが {lum.size} 個（{meta['n_queries']} × {NPIX} のはず）")
    lum = lum.reshape(meta["n_queries"], NPIX)
    res = {"tag": a.tag, "n_stops_listed": meta["n_stops"], "rise_ms": meta["rise_ms"], "window_s": meta["window_s"],
           "m1": meta["m1"], "seq_s": meta["seq_s"], "pca_k": PCA_K, "ridge_lam": RIDGE_LAM, "knn_k": KNN_K,
           "numpy": np.__version__, "tests": {}}
    for test in ("i", "ii", "iii"):
        res["tests"][test] = analyse(meta["items"], lum, test, a.seed, a.R)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
