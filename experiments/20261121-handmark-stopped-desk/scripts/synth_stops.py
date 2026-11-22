"""止まりの多い合成の記録（人の記録を使わない・道具の通しと対照のため）。標準のライブラリだけ（random は種で固定）。

日ごとに 1 本のセッション（現地 10:00 から H 時間）を作る。打鍵のまとまり（5〜60 秒・間隔は対数正規）と止まりを
交互に置く。止まりの長さは 2 つの混ぜ: 4 割は 3〜8 秒（is_idle に届かない）、6 割は 20 秒〜15 分の対数一様。
ポインタは 1 秒ごとに確率で動く（打っている間 0.10・止まっている間 0.15）。1 日に 1 回、1〜5 分の記録の一時停止を
止まりの中に置く（一時停止の間の打鍵は書かない）。
出力の行: meta（session_start・hmm_version）・key（category・press）・pointer_bin・recording_pause・meta（session_end）。
"""
import argparse
import json
import math
import os
import random

LETTERS = ["alphabetic"] * 12 + ["space"] * 3 + ["punctuation", "enter", "numeric", "backspace"]


def day_start_ms(day, utc_offset_secs):
    return (day * 86400 + 4 * 3600 - utc_offset_secs) * 1000


def session(rng, day, utc_offset_secs, hours):
    start = day_start_ms(day, utc_offset_secs) + 6 * 3600 * 1000 + rng.randrange(0, 600_000)
    end = start + int(hours * 3600 * 1000)
    rows = [{"type": "meta", "session_start": start, "hmm_version": "0.5.0"}]
    t = start + 1_000
    typing = []   # (from, to) 打っている区間
    stops = []    # (from, to) 止まり
    while t < end:
        burst_end = t + rng.randrange(5_000, 60_000)
        a = t
        while t < min(burst_end, end):
            cat = rng.choice(LETTERS)
            rows.append({"type": "key", "t": t, "category": cat, "press": True})
            rows.append({"type": "key", "t": t + 40 + rng.randrange(0, 60), "category": cat, "press": False})
            t += max(40, int(rng.lognormvariate(0, 0.5) * 220))
        typing.append((a, t))
        if rng.random() < 0.4:
            gap = rng.randrange(3_000, 8_000)
        else:
            gap = int(math.exp(rng.uniform(math.log(20_000), math.log(900_000))))
        stops.append((t, t + gap))
        t += gap
    # 一時停止: 20 秒より長い止まりの中に 1 つ（打鍵と重ならない）
    long_stops = [s for s in stops if s[1] - s[0] > 90_000 and s[1] < end]
    if long_stops:
        a, b = rng.choice(long_stops)
        pa = a + rng.randrange(15_000, (b - a) // 2)
        pb = min(b - 1_000, pa + rng.randrange(60_000, 300_000))
        if pb > pa:
            rows.append({"type": "recording_pause", "t": pa, "paused": True})
            rows.append({"type": "recording_pause", "t": pb, "paused": False})
    for s in range(start // 1000 + 1, end // 1000):
        ms = s * 1000
        p = 0.10 if any(a <= ms < b for a, b in typing) else 0.15
        if rng.random() < p:
            rows.append({"type": "pointer_bin", "t": ms, "moved": rng.randrange(1, 6),
                         "buttons": 1 if rng.random() < 0.08 else 0, "wheel": 1 if rng.random() < 0.05 else 0})
    rows = [r for r in rows if r["type"] == "meta" or r["t"] < end]
    rows.sort(key=lambda r: r.get("t", r.get("session_start", 0)))
    rows.append({"type": "meta", "session_end": end})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--days", type=int, required=True)
    ap.add_argument("--first-day", type=int, default=20_400)
    ap.add_argument("--hours", type=float, default=3.0)
    ap.add_argument("--utc-offset-secs", type=int, default=32_400)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = random.Random(a.seed)
    for i in range(a.days):
        day = a.first_day + i
        rows = session(rng, day, a.utc_offset_secs, a.hours)
        with open(os.path.join(a.out, f"synth_{day}.ndjson"), "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
