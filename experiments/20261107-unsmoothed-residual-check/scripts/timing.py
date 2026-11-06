"""Mac の合成で時間を測り、本計算の見積もりを出す（conditions D6）。合成のデータだけ。

測るもの:
- 書き手の段の比: 同じ合成の書き手で、tau-extend の em_writer（格子の全部の k・折り目つき）と、この試験の fit_writer
  （作る k だけ・折り目なし・乱数は捨てる）の時間の比（CoAuthor の格子と CS1 の格子）。
- 残差: 評価の記号 10,635（CS1 の評価の記号の中央値）の書き手 1 人で、AR(1)-HMM（K = 3）の予測 1 回と擬似残差の時間。
見積もり: tau-extend の HP Z2 の実測（summary.json の seconds）に、共通の段はそのまま（上の端）、書き手の段は比を掛ける。

使い方: python3 -I timing.py <seed> <tau-extend summary.json> <out.json>
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pinned import H, ml  # noqa: E402
import fit as F  # noqa: E402
import residual as R  # noqa: E402
import selftest as ST  # noqa: E402


def ratio(seed, grid, make, n_u, L_):
    writers, pools = ST.synth(seed, 60, 1, n_u, L_)
    u = writers[0]
    t0 = time.time()
    ml.em_writer(u, 5 if len(grid) > 4 else 1, grid, pools, np.random.default_rng([seed + 10, 0]), structs=None, do_folds=True)
    t1 = time.time()
    F.fit_writer(u, 5 if len(grid) > 4 else 1, grid, make, pools, np.random.default_rng([seed + 10, 0]))
    t2 = time.time()
    return dict(tau_extend_sec=t1 - t0, this_sec=t2 - t1, ratio=(t2 - t1) / (t1 - t0))


def residual_time(seed):
    rng = np.random.default_rng([seed, 61])
    m = H.random_model("ar", 3, rng, r1=np.full((26, 26), 1 / 26), r0=np.full(26, 1 / 26))
    seqs = H.sample(m, [10635], rng)
    E = R.EvalSeq([dict(seqs=seqs, pflag=[np.ones(len(seqs[0]), dtype=bool)])])
    t0 = time.time()
    R.writer_residuals(E, [("m", ("model", m))], seed, 1, 0, 0)
    return time.time() - t0


def main(seed, tau_summary, out):
    S = json.load(open(tau_summary))["datasets"]
    co = ratio(seed, [1, 2, 3, 5, 8, 12, 15], [1, 5, 15], 20, 300)
    cs = ratio(seed, [1, 2, 3, 5], [1, 5], 6, 1500)
    rt = residual_time(seed)
    # 共通の段は tau-extend の実測をそのまま（w を除く共通はパネルの書き手だけになり、少なくなる側）
    pools = S["coauthor"]["seconds"]["pools"] + S["cs1"]["seconds"]["pools"]
    wr = S["coauthor"]["seconds"]["writers"] * co["ratio"] + S["cs1"]["seconds"]["writers"] * cs["ratio"]
    # 残差: 1 書き手 × セル × モデル（11 前後）。CS1 23 人 × 2 セル・CoAuthor 17 人 × 3 セル（CoAuthor は評価の記号が約 1/3）
    res = rt * 11 * (23 * 2 + 17 * 3 / 3)
    col_o = pools + wr + res
    est = dict(o_sec=col_o, u_sec=col_o, n_sec=col_o / 30 + res / 30, selftests_sec=900)
    est["total_hours"] = sum(est.values()) / 3600
    json.dump(dict(coauthor_writer_ratio=co, cs1_writer_ratio=cs, residual_one_model_one_writer_sec=rt,
                   tau_extend_hp_z2_sec=dict(pools=pools, writers=S["coauthor"]["seconds"]["writers"] + S["cs1"]["seconds"]["writers"]),
                   estimate=est), open(out, "w"), indent=1)
    print(json.dumps(est))


if __name__ == "__main__":
    main(int(sys.argv[1]), sys.argv[2], sys.argv[3])
