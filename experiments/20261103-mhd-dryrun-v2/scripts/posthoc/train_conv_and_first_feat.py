"""cross-review の Codex の指摘 1・2 の事後の確かめ（2026-11-03・計算の後）。
1. 学習の側のモデルの推定（B1・M1・M2）が Newton 法で収束したか（fit_logistic は収束のフラグを捨てる）。
2. 問いの窓の右端（t − 1 秒）より前に feat 行が 1 本も無い問いの数（last_le が先頭の行を返す＝未来の値を使う場合）。
"""
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import dryrun_v2 as D  # noqa: E402

work, seed = sys.argv[2], int(sys.argv[3])
writers = D.load(work)
P = D.build(writers, seed)
D.add_syn(P, writers, seed + 1)
rng = np.random.default_rng(seed)
bad = 0
total = 0
for wi, ss in enumerate(writers):
    for si, s in enumerate(ss):
        for t in D.draw_probes(rng, s["a"], s["b"]):
            total += 1
            if len(s["feat"]) == 0 or s["feat"][0, 0] > t - D.WIN_END:
                bad += 1
print("probes", total, "feat の最初の行が窓の右端より後", bad)
rocket = D.Rocket(seed + 2)
for lab in ("y_real", "y_syn"):
    Y = np.array([p[lab] for p in P], dtype=float)
    for name, (tr, te) in (("primary", D.split_primary(P, writers)), ("subject_holdout", D.split_subject(P, writers, seed + 3))):
        trp = [P[i] for i in tr]
        ytr = Y[tr]
        xb = D.logit(np.array([[p["tab"][3]] for p in trp]))
        _, c_b1 = D.fit_logistic_c(xb, ytr)
        a, _ = D.standardize(np.array([p["tab"] for p in trp]), np.array([p["tab"] for p in trp]))
        _, c_m1 = D.fit_logistic_c(a, ytr, lam=1.0)
        a2 = rocket.transform(np.array([p["ser"] for p in trp]))
        a2, _ = D.standardize(a2, a2)
        _, c_m2 = D.fit_logistic_c(a2, ytr, lam=10.0)
        print(lab, name, "B1", c_b1, "M1", c_m1, "M2", c_m2)
    for r in range(3, 10):
        tr = [i for i, p in enumerate(P) if p["s"] + 1 < r]
        te = [i for i, p in enumerate(P) if p["s"] + 1 == r]
        if not te or Y[tr].min() == Y[tr].max():
            continue
        trp = [P[i] for i in tr]
        xb = D.logit(np.array([[p["tab"][3]] for p in trp]))
        _, c_b1 = D.fit_logistic_c(xb, Y[tr])
        a, _ = D.standardize(np.array([p["tab"] for p in trp]), np.array([p["tab"] for p in trp]))
        _, c_m1 = D.fit_logistic_c(a, Y[tr], lam=1.0)
        a2 = rocket.transform(np.array([p["ser"] for p in trp]))
        a2, _ = D.standardize(a2, a2)
        _, c_m2 = D.fit_logistic_c(a2, Y[tr], lam=10.0)
        print(lab, "rolling", r, "B1", c_b1, "M1", c_m1, "M2", c_m2)
