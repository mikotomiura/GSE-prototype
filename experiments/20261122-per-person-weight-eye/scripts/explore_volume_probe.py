# 探索（門の判定に使わない）: 量の筋で、書き手の記録の量と AUC_v（本人の対の順位）の関係を見る。種は報告の組と重ならない 900000〜。
import sys, numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, sys.argv[1])
import eye as EY, gen as GN, run_eye as RE
SHAPE, K = sys.argv[2], int(sys.argv[3])
def one(seed):
    r = dict(null=1, strand="volume", shape=SHAPE, step=0.0, seed=seed)
    w, P = GN.make(r)
    sh = GN.SY.SHAPES[SHAPE]
    UC = EY.count_writers(w, GN.NSYM)
    vol = np.array([sum(uc.sum() for uc in UC[v]) for v in range(P)], float)
    rng = np.random.default_rng([seed, 7])
    perms = EY.draw_perms(rng, P)
    out = EY.eval_cell(UC, P, sh["H"], K, 0, perms)
    def rk(x):   # 平均の順位（同点は平均を振る）
        x = np.asarray(x, float)
        o = np.argsort(x, kind="mergesort")
        r = np.empty(len(x))
        r[o] = np.arange(len(x))
        for v in np.unique(x):
            m = x == v
            r[m] = r[m].mean()
        return r
    return {e: float(np.corrcoef(rk(vol), rk(np.array(out[e]["auc"])))[0, 1]) for e in EY.EYES}, {e: out[e]["p"] for e in EY.EYES}
if __name__ == "__main__":
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, range(900000, 900160)))
    for e in EY.EYES:
        c = np.array([r[0][e] for r in res]); p = np.array([r[1][e] for r in res])
        print(SHAPE, "k=%d" % K, e, "量と AUC_v の順位相関 平均 %.3f（SE %.3f）・p≤0.05 の割合 %.3f" % (c.mean(), c.std(ddof=1)/np.sqrt(len(c)), (p <= 0.05).mean()))
