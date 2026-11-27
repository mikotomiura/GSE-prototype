"""合成のデータ（CoAuthor の中間の形と新しい中間の形）を一時の dir に作る（selftest_dose・e2e_dose・timing_dose が使う）。実データは読まない。

中間: <root>/co/sessions.json と s<番号>.json（keys・feat・observed_intervals・events）。feat 行は 1 秒ごと（gap_at を渡すと
その単位の 1 か所だけ 2 秒あける・P-TIME 用）。新しい中間: <root>/side.json.gz（data.py と同じ並べ・o・u・n）。
"""
import gzip
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load_dose  # noqa: E402,F401  S13 の scripts を sys.path に入れる（pinned の読み込みの前に）
from pinned import H  # noqa: E402
import masks as MK  # noqa: E402


def make(root, seed, n_w=3, n_u=21, lengths=(90, 260), gap_at=None, tag=90):
    """n_w 人 × n_u 単位。単位の行の数は lengths の範囲の一様。gap_at = (書き手, 単位) なら、その単位の中ほどで時刻を 2 秒あける。"""
    rng = np.random.default_rng([seed, tag])
    cm = H.random_model("hmm", 3, rng)
    cm["A"] = 0.9 * np.eye(3) + 0.1 * cm["A"]
    co = os.path.join(root, "co")
    os.makedirs(co, exist_ok=True)
    s2w, W, i = {}, {}, 0
    for w in range(n_w):
        for u in range(n_u):
            n = int(rng.integers(lengths[0], lengths[1] + 1))
            a = 10_000_000 * i + 1000
            t = a + 1000 * np.arange(n)
            if gap_at == (w, u):
                t[n // 2:] += 1000
            obs = H.sample(cm, [n], rng)[0]
            uu = (obs + rng.integers(0, 3, n)) % 26
            feat = [[int(t[j]), 0.0, 0.0, 0.5, 0.1, 0.8, int(obs[j]), 0.3] for j in range(n)]
            kt = t[rng.random(n) < 0.15] - 500
            keys = [[int(x), "a"] for x in kt] or [[int(t[0]) - 500, "a"]]
            json.dump(dict(keys=keys, feat=feat, onsets=[], observed_intervals=[[int(a), int(t[-1])]], events=[]),
                      open(os.path.join(co, "s%05d.json" % i), "w"))
            s2w[str(i).zfill(5)] = "w%02d" % w
            nm = MK.kit_variants().thinned_mask([int(x) for x in t])
            W.setdefault("w%02d" % w, []).append((a, dict(o=[obs.tolist()], u=[uu.tolist()], n=[[int(b) for b in nm]])))
            i += 1
    json.dump(s2w, open(os.path.join(co, "sessions.json"), "w"))
    side = os.path.join(root, "side.json.gz")
    with gzip.open(side, "wt", encoding="utf-8") as f:
        json.dump(dict(dataset="coauthor", writers=[[r for _, r in sorted(W[w], key=lambda x: x[0])] for w in sorted(W)]), f)
    return co, side
