import sys, numpy as np
sys.path.insert(0, sys.argv[1]); import dryrun as D
orig = D.calib
def swapped(y, p):  # 条件どおりの変異: 傾きの計算で y と p を取り違える
    lp = D.logit(p); ly = D.logit(np.asarray(y, float))
    slope = None if np.var(ly) < 1e-12 else float(D.fit_logistic(ly[:, None], np.asarray(p, float))[1])
    return float(D.fit_logistic(None, y, offset=lp)[0]), slope
D.calib = swapped
sys.exit(D.selftest(sys.argv[2], int(sys.argv[3])))
