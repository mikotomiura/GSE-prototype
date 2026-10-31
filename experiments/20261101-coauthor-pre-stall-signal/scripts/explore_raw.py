"""探索（conditions.md で事前に決めていない・判定に使わない）: 推定を通さず打鍵から直接作る量で、停滞の手前と対照を比べる。

目的: 「打鍵に停滞の予兆が無い」のか「予兆はあるが今の推定が拾えていない」のかを分ける。
量（u 以前 30 秒の押下から）: 打鍵間隔の中央値・2 秒以上の間隔の数・後退の割合。
標本と対照は analyze_stall.py と同じ規則・同じ SEED で作る。ただし押下が 3 つ未満の時刻（停滞・対照とも）を除くので、
乱数の進み方がずれ、対照は本解析と別の標本になる（主の 4 信号も同じ標本で併記して比べる）。
使い方: python3 -I explore_raw.py <work2_dir> <meta_creative.csv> <meta_argumentative.csv> <seed> <out.json>
"""
import bisect
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A  # noqa: E402
import analyze_stall as S  # noqa: E402

RAW = ["iki_median", "pauses_ge2s", "backspace_share"]


def raw_at(s, u):
    lo = bisect.bisect_left(s.press, u - 30_000)
    hi = bisect.bisect_right(s.press, u)
    ts, cs = s.press[lo:hi], s.cat[lo:hi]
    if len(ts) < 3:
        return None
    gaps = [b - a for a, b in zip(ts, ts[1:])]
    return {"iki_median": statistics.median(gaps), "pauses_ge2s": sum(g >= 2000 for g in gaps),
            "backspace_share": sum(c == "backspace" for c in cs) / len(cs)}


def main():
    orig = S.sig_at

    def both(s, u):
        a, b = orig(s, u), raw_at(s, u)
        if a is None or b is None:
            return None
        a.update(b)
        return a
    S.sig_at = both
    S.SIGNALS = S.SIGNALS + RAW
    out = sys.argv[5]
    import tempfile
    tmpd = tempfile.TemporaryDirectory()
    tmp = tmpd.name
    sys.argv = [sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], tmp]
    S.main()
    import json
    res = {"counts": json.load(open(os.path.join(tmp, "counts.json"))), "auc": json.load(open(os.path.join(tmp, "auc.json")))}
    json.dump(res, open(out, "w"), indent=1)
    tmpd.cleanup()


if __name__ == "__main__":
    main()
