"""合成の記録（判断 4・設計 v2 §6）。人の記録を使わない。標準のライブラリだけ（random は種で固定）。

日ごとに 1 本のセッション（現地 10:00 から H 時間）を作る。潜在の状態を分の単位のマルコフ連鎖で動かす。
  flow  : 速く一定に打つ。削除は少ない
  warm  : 遅めで、ときどき 3〜8 秒止まる。削除は少ない
  stuck : 打鍵の時刻の分布（間隔・止まりの頻度と長さ）は warm と同じ。削除（backspace・delete）が多く、
          止まりの直前のキーが削除であることが多い
stuck と warm の違いはキーの種類にだけ出る（A は種類を見ないので、A からは見分けられない）。
これが無いと、漏れを注入しても A を超える情報が乗らず、陽性対照が働かない（設計 v2 §6）。

ときどき 4〜6 分の離席を入れる（除外の規則を通すため）。ポインタは状態に依らず 1 秒ごとに確率で動く。
出力の行: meta（session_start・hmm_version・s1_mode）・key（category・press）・pointer_bin・meta（session_end）。
"""
import argparse
import json
import os
import random

STATES = ("flow", "warm", "stuck")
STAY = 0.85
# 状態ごとの (打鍵の間隔の対数正規の中央値 ms, σ, 止まりの確率, 止まりの長さ ms の範囲,
#             止まりの直前のキーが削除である確率, それ以外のキーが削除である確率)
# warm と stuck は打鍵の時刻の分布（間隔・止まりの頻度と長さ）が同じで、違いはキーの種類（止まりの前が削除か・
# 削除の割合）にだけある。flow は速く、止まりが少ない（時刻にも違いが出る）。
PARAMS = {
    "flow": (170, 0.35, 0.01, (2500, 5000), 0.05, 0.04),
    "warm": (330, 0.55, 0.08, (3000, 8000), 0.05, 0.05),
    "stuck": (330, 0.55, 0.08, (3000, 8000), 0.80, 0.25),
}
LETTERS = ["alphabetic"] * 12 + ["space"] * 3 + ["punctuation", "enter", "numeric"]


def day_start_ms(day, utc_offset_secs):
    return (day * 86400 + 4 * 3600 - utc_offset_secs) * 1000


def session(rng, day, utc_offset_secs, hours, away_per_hour, no_flow=False):
    start = day_start_ms(day, utc_offset_secs) + 6 * 3600 * 1000 + rng.randrange(0, 600_000)
    end = start + int(hours * 3600 * 1000)
    rows = [{"type": "meta", "session_start": start, "hmm_version": "0.5.0", "s1_mode": True}]
    states = STATES if not no_flow else ("warm", "stuck")
    state = rng.choice(states)
    minute_end = start + 60_000
    t = start + 1_000
    away_until = 0
    aways = []
    while t < end:
        while t >= minute_end:
            if rng.random() > STAY:
                state = rng.choice([s for s in states if s != state])
            minute_end += 60_000
            if rng.random() < away_per_hour / 60.0:
                away_until = minute_end + rng.randrange(240_000, 360_000)
                aways.append((minute_end, away_until))
        if t < away_until:
            t = away_until
            continue
        med, sig, p_pause, pause_rng, p_del_before_pause, p_del = PARAMS[state]
        t += max(30, int(rng.lognormvariate(0, sig) * med))
        if t >= end:
            break
        # このキーの後に止まるか（頻度と長さは warm と stuck で同じ）。止まるときは、直前のキーが削除である確率が状態で違う。
        pause_after = rng.random() < p_pause
        is_del = rng.random() < (p_del_before_pause if pause_after else p_del)
        cat = rng.choice(["backspace"] * 4 + ["delete"]) if is_del else rng.choice(LETTERS)
        rows.append({"type": "key", "t": t, "category": cat, "press": True})
        rows.append({"type": "key", "t": t + 40 + rng.randrange(0, 60), "category": cat, "press": False})
        if pause_after:
            t += rng.randrange(*pause_rng)
    for s in range(start // 1000 + 1, end // 1000):
        # 離席の間はポインタも動かない（離席の候補の除外を通すため）
        if any(a < s * 1000 <= b for a, b in aways):
            continue
        if rng.random() < 0.25:
            rows.append({
                "type": "pointer_bin", "t": s * 1000, "moved": rng.randrange(1, 6),
                "buttons": 1 if rng.random() < 0.08 else 0, "wheel": 1 if rng.random() < 0.05 else 0,
            })
    rows.sort(key=lambda r: r.get("t", r.get("session_start", 0)))
    rows.append({"type": "meta", "session_end": end})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--days", type=int, required=True)
    ap.add_argument("--first-day", type=int, default=20_400)
    ap.add_argument("--hours", type=float, default=1.5)
    ap.add_argument("--away-per-hour", type=float, default=0.5)
    ap.add_argument("--utc-offset-secs", type=int, default=32_400)
    ap.add_argument("--no-flow", action="store_true", help="flow を使わない（打鍵の時刻が同じ 2 状態だけ）")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = random.Random(a.seed)
    for i in range(a.days):
        day = a.first_day + i
        rows = session(rng, day, a.utc_offset_secs, a.hours, a.away_per_hour, a.no_flow)
        with open(os.path.join(a.out, f"synth_{day}.ndjson"), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
