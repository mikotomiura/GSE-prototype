"""止まりの一覧（gse-replay --stopped-stops）から、経過が読めないことの確かめ (i)〜(iii) の問い合わせを作る。

ADR-056 D2・設計案 §4.4 の確かめ方 2・conditions.md E2。時刻は Stage の時刻 τ（コマの時刻 q = τ + 遅れ）。
評価に入るのは立ち上がりの後（τ ≥ 止まりの始まり + rise）だけ。

  (i)   止まり 1 つにつき M1 個の対（q − 250 と q）。τ は [start + rise, end) から一様。ラベル = τ − start
  (ii)  長さが rise + W + S 以上の止まり 1 つにつき 1 本の列（S 秒・1 秒おき）。列の始まり τ0 は
        [start + rise + W, end − S] から一様。ラベル = τ0 − start（記憶の窓 W より前の経過）
  (iii) 長さが rise + S 以上の止まり 1 つにつき 1 本の列。τ0 は [start + rise, end − S] から一様。
        ラベル = τ0 − t0（手跡を出し始めた時刻 grid_start からの経過）

出力: q.ndjson（区間ごとにまとめ、q の昇順・gse-replay --stopped-queries の入力。e と s0 は対照の描画が使う）と
items.json（項目ごとの検定・止まり・日・ラベル・問い合わせの番号）。どちらも中間で、repo に置かない。
"""
import argparse
import json
import random

M1 = 4          # (i) の止まりあたりの対の数
SEQ_S = 30      # (ii)(iii) の列の長さ（秒）
SEQ_STEP = 1000  # 列のコマの間隔（ms）
PAIR_GAP = 250  # desk.rs の PAIR_GAP_MS
MIN_STOP_AFTER_RISE = 1000  # (i) に入れる止まりの長さの下限（立ち上がりの後に 1 秒）


def plan(stops, rise_ms, window_s, lag_ms, seed):
    # 検定ごとに別の乱数の流れ（(ii) の対象は W で変わるので、(i)(iii) の時刻が W と形に依らず同じになるように）
    rng_i, rng_ii, rng_iii = (random.Random(f"{seed}-{t}") for t in ("i", "ii", "iii"))
    w_ms = window_s * 1000
    s_ms = SEQ_S * 1000
    items = []   # {test, stop, day, label, taus}
    for si, st in enumerate(stops):
        a, b = st["start"], st["end"]
        lo = a + rise_ms
        # (i) は対の 1 枚目（τ − 250）も立ち上がりの後に置く（1 枚目が立ち上がりの途中だと、動きが「立ち上がりの
        # 直後か」を運ぶ。2026-11-22 の合成の陰性で止まりの層だけの画が上回った・判断 13）
        lo_i = lo + PAIR_GAP
        if b - lo_i >= MIN_STOP_AFTER_RISE:
            taus = sorted(rng_i.randrange(lo_i, b) for _ in range(M1))
            for tau in taus:
                if tau - PAIR_GAP < 0:
                    continue
                items.append({"test": "i", "stop": si, "day": st["day"], "label": tau - a,
                              "taus": [tau - PAIR_GAP, tau]})
        hi = b - s_ms
        if hi >= lo + w_ms:
            t0s = rng_ii.randrange(lo + w_ms, hi + 1)
            items.append({"test": "ii", "stop": si, "day": st["day"], "label": t0s - a,
                          "taus": [t0s + k * SEQ_STEP for k in range(SEQ_S)]})
        if hi >= lo:
            t0s = rng_iii.randrange(lo, hi + 1)
            items.append({"test": "iii", "stop": si, "day": st["day"], "label": t0s - st["t0"],
                          "taus": [t0s + k * SEQ_STEP for k in range(SEQ_S)]})
    # 問い合わせ: 区間ごと・q の昇順。同じ時刻が重なってもよい（昇順でなく非減少）
    qs = []
    for ii, it in enumerate(items):
        st = stops[it["stop"]]
        for k, tau in enumerate(it["taus"]):
            qs.append((st["seg"], tau + lag_ms, ii, k, st["t0"], tau - st["start"], tau - st["t0"]))
    qs.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    for it in items:
        it["q"] = [None] * len(it["taus"])
    lines = []
    for n, (seg, q, ii, k, t0, e, s0) in enumerate(qs):
        items[ii]["q"][k] = n
        lines.append(json.dumps({"seg": seg, "t0": t0, "q": q, "e": e, "s0": s0}, separators=(",", ":")))
    for it in items:
        del it["taus"]
    return items, lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stops")
    ap.add_argument("--rise-ms", type=int, required=True)
    ap.add_argument("--window-s", type=int, required=True)
    ap.add_argument("--lag-ms", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--queries", required=True)
    ap.add_argument("--items", required=True)
    a = ap.parse_args()
    with open(a.stops, encoding="utf-8") as f:
        stops = [json.loads(line) for line in f if line.strip()]
    items, lines = plan(stops, a.rise_ms, a.window_s, a.lag_ms, a.seed)
    with open(a.queries, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))
    with open(a.items, "w", encoding="utf-8") as f:
        json.dump({"items": items, "n_queries": len(lines), "n_stops": len(stops),
                   "rise_ms": a.rise_ms, "window_s": a.window_s, "m1": M1, "seq_s": SEQ_S}, f)


if __name__ == "__main__":
    main()
