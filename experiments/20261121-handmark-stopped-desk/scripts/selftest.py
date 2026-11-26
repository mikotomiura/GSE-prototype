"""elapsed.py の自己検査（人の記録を使わない）。numpy だけ。

1. 順位相関（同点・定数）・止まりの単位の入れ替え（日の中・組の中の順・ラベルの多重集合）。
2. 陰性: 特徴がラベルと無関係な合成で、「偶然を上回った」が確かめ (i)〜(iii) のそれぞれで 40 回中 6 回以下（片側 5% の 2 回の見込みに余裕）。
3. 陽性: ラベルを特徴に入れる変異（leak）で、3 つの確かめのどれも「偶然を上回った」になる。
4. 変異: 判定を逆にする変異（flip）で 2 が崩れる（検査が判定を見ていることの確かめ）。
5. 学習の項目が足りずに落ちる折り目があれば「決まらない」になる。
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import elapsed as E


def synth_items(rng, days=6, stops_per_day=25):
    items, nq = [], 0
    for d in range(days):
        for s in range(stops_per_day):
            sid = d * 1000 + s
            length = float(np.exp(rng.uniform(np.log(30_000), np.log(900_000))))
            for _ in range(E_M1):
                items.append({"test": "i", "stop": sid, "day": d, "label": int(rng.uniform(2_000, length)),
                              "q": [nq, nq + 1]})
                nq += 2
            for t in ("ii", "iii"):
                items.append({"test": t, "stop": sid, "day": d, "label": int(rng.uniform(2_000, length)),
                              "q": list(range(nq, nq + 30))})
                nq += 30
    return items, nq


E_M1 = 4


def check(cond, msg):
    if not cond:
        raise SystemExit(f"自己検査の不合格: {msg}")


def main():
    check(abs(E.spearman([1, 2, 3, 4], [2, 4, 6, 8]) - 1.0) < 1e-12, "単調の順位相関")
    check(abs(E.spearman([1, 1, 2, 2], [1, 2, 3, 4]) - 0.8944271909999159) < 1e-12, "同点の順位相関")
    check(E.spearman([1, 1, 1], [1, 2, 3]) == 0.0, "定数の順位相関")
    rng = np.random.default_rng(1)
    labels = np.arange(12, dtype=float)
    stops = np.repeat(np.arange(6), 2)
    days = np.repeat([0, 1], 6)
    for _ in range(20):
        p = E.permute_blocks(rng, labels, stops, days)
        for d in (0, 1):
            check(sorted(p[days == d]) == sorted(labels[days == d]), "日の中のラベルの多重集合")
        for s in range(6):
            b = p[stops == s]
            check(b[1] - b[0] == 1 and b[0] % 2 == 0, "組の中の順と組の単位")
    # 陰性と変異
    above, flipped = 0, 0
    above_by = {"i": 0, "ii": 0, "iii": 0}
    for k in range(40):
        r = np.random.default_rng(100 + k)
        items, nq = synth_items(r)
        lum = r.normal(size=(nq, E.NPIX))
        for t in ("i", "ii", "iii"):
            above_by[t] += E.analyse(items, lum, t, 7, 200)["verdict"] == "above_chance"
        E.MUT.add("flip")
        flipped += sum(E.analyse(items, lum, "i", 7, 200)["verdict"] == "above_chance" for _ in [0])
        E.MUT.discard("flip")
    for t, n in above_by.items():
        check(n <= 6, f"陰性の {t} で偶然を上回った回数が {n}/40")
    above = "・".join(f"{t} {n}" for t, n in above_by.items())
    check(flipped >= 30, f"flip の変異が効かない（{flipped}/40）")
    # 折り目が落ちると「決まらない」（1 日だけ項目が多く、他の日を抜くと学習の項目が足りない合成）
    r = np.random.default_rng(9)
    few = [{"test": "iii", "stop": s, "day": 0 if s < 30 else s - 29, "label": 2_000 + s, "q": list(range(s * 30, s * 30 + 30))}
           for s in range(32)]
    v = E.analyse(few, r.normal(size=(32 * 30, E.NPIX)), "iii", 7, 20)
    check(v["verdict"] == "undetermined", f"折り目が落ちても判定した（{v['verdict']}）")
    check("折り目" in v.get("reason", ""), f"折り目でない理由で決まらない（{v.get('reason')}）")
    # 陽性
    r = np.random.default_rng(5)
    items, nq = synth_items(r)
    lum = r.normal(size=(nq, E.NPIX))
    E.MUT.add("leak")
    res = {t: E.analyse(items, lum, t, 7, 200) for t in ("i", "ii", "iii")}
    E.MUT.discard("leak")
    for t, v in res.items():
        check(v["verdict"] == "above_chance", f"陽性の {t} が拾えない（{v.get('stat')} ≤ {v['null']['q95']}）")
    print(f"selftest ok: 陰性（/40）{above}・flip {flipped}/40・陽性 3/3")


if __name__ == "__main__":
    main()
