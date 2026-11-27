"""Mac の合成で時間を測り、本計算の見積もりを出す（conditions D6）。合成のデータだけ。

測るもの: S13 の timing.py の「書き手の段」と同じ合成と引数で、S13 の fit_writer（作る k = 1・5・15・折り目なし）の 1 書き手の時間。
S13 の HP Z2 の同じ測り（results/timing.json の coauthor_writer_ratio.this_sec）との比を、HP Z2 の速さに対する Mac の速さとする。
見積もり: S13 の HP Z2 の列 u・CoAuthor の実測（summary の fit.seconds の pools + writers）× 速さの比 × 列ごとの記号の数の比
（e2e の合成で数えた比ではなく、規則から: A1・B は約 1、A・C・C′ の s は約 1/s）＋ 残差と足す量（e2e の合成で測った列ごとの時間の比を当てる）。
使い方: python3 -I timing_dose.py <seed> <S13 の timing.json> <S13 の summary.json> <e2e.json> <out.json> <jobs>
"""
import importlib.util
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S13 = os.path.realpath(os.path.join(HERE, "../../20261107-unsmoothed-residual-check/scripts"))
sys.path.insert(0, HERE)
sys.path.insert(1, S13)


def load_as(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main(seed, t13, s13, e2e, out, jobs):
    import pinned  # noqa: F401  S13（tau-extend の SHA-256 を照らす）
    ST = load_as("selftest", os.path.join(S13, "selftest.py"))  # S13 の selftest（kit の同名のファイルに隠れないように先に読む）
    import fit as F
    writers, pools = ST.synth(seed, 60, 1, 20, 300)
    t0 = time.time()
    F.fit_writer(writers[0], 5, [1, 2, 3, 5, 8, 12, 15], [1, 5, 15], pools, np.random.default_rng([seed + 10, 0]))
    mac = time.time() - t0
    hp = json.load(open(t13))["coauthor_writer_ratio"]["this_sec"]
    speed = mac / hp
    u = json.load(open(s13))["columns"]["u"]["coauthor"]["fit"]["seconds"]
    col_u_hp = u["pools"] + u["writers"]
    frac = {"A1": 1.0}
    for s in (5, 10, 15, 30):
        for p in ("A%d", "C%d", "P1-%d", "P3-%d"):
            frac[p % s] = 1.0 / s
        frac["B%d" % s] = 1.0
    E = json.load(open(e2e))["seconds_per_column"]
    est = {c: col_u_hp * speed * f for c, f in frac.items()}
    tot = sum(est.values())
    no_b = sum(v for c, v in est.items() if not c.startswith("B"))
    R = dict(mac_fit_writer_sec=mac, hp_z2_fit_writer_sec=hp, mac_over_hp=speed, s13_u_coauthor_hp_sec=dict(u, total=col_u_hp),
             symbol_fraction=frac, estimate_sec=est, estimate_hours=tot / 3600, estimate_hours_without_B=no_b / 3600,
             e2e_synthetic_seconds_per_column=E, jobs=jobs,
             note="EM の時間は記号の数に比例とみなす（短い列では上の側）。残差と足す量は列あたり数分以内（e2e の値）で、見積もりに含めない。")
    json.dump(R, open(out, "w"), indent=1)
    print(json.dumps(dict(mac_over_hp=speed, estimate_hours=R["estimate_hours"], without_B=R["estimate_hours_without_B"])))


if __name__ == "__main__":
    a = sys.argv[1:]
    main(int(a[0]), a[1], a[2], a[3], a[4], int(a[5]))
