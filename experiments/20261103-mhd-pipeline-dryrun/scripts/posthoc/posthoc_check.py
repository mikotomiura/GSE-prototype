import sys, numpy as np
sys.path.insert(0, sys.argv[1]); import dryrun as D
W = D.load(sys.argv[2]); P = D.build(W, int(sys.argv[3]))
# last_le が窓の右端より後の feat 行を返した件数（窓の右端より前に feat 行が無い）
rng = np.random.default_rng(int(sys.argv[3])); fut = 0; n = 0
for wi, ss in enumerate(W):
    for s in ss:
        for t in D.draw_probes(rng, s["a"], s["b"]):
            n += 1; fut += int(s["feat"][0, 0] > t - D.WIN_END)
print("probes", n, "feat の最初の行が窓の右端より後", fut)
# Newton 法の反復回数と分離の監視（主の分け方の B1・M1 を L-real で）
orig = D.fit_logistic; stats = {"calls": 0, "nonconv": 0}
def wrapped(X, y, lam=0.0, offset=None):
    n_ = len(y); Xd = np.hstack([np.ones((n_, 1)), X]) if X is not None and X.size else np.ones((n_, 1))
    off = np.zeros(n_) if offset is None else offset; beta = np.zeros(Xd.shape[1]); R = np.eye(Xd.shape[1]) * lam; R[0, 0] = 0
    for it in range(100):
        p = D.sigmoid(Xd @ beta + off); g = Xd.T @ (y - p) - R @ beta; H = (Xd * (p * (1 - p))[:, None]).T @ Xd + R
        step = np.linalg.solve(H + 1e-12 * np.eye(len(beta)), g); beta = beta + step
        if np.max(np.abs(step)) < 1e-8: break
    else: stats["nonconv"] += 1
    stats["calls"] += 1; return beta
D.fit_logistic = wrapped
D.add_syn(P, W, int(sys.argv[3]) + 1); tr, te = D.split_primary(P, W)
Y = np.array([p["y_real"] for p in P], float); groups = D.eval_groups(P, te)
for m in ("B1", "M1"):
    stats.update(calls=0, nonconv=0)
    pr = D.fit_predict(m, [P[i] for i in tr], [P[i] for i in te], Y[tr], None)
    c = D.ci(Y[te], pr, Y[tr].mean(), groups, np.random.default_rng(int(sys.argv[3]) + 4), 500, keys=("cal_slope",))
    print(m, "logit(p) の SD %.3f" % np.std(D.logit(pr)), "推定", stats["calls"], "収束しない", stats["nonconv"])
