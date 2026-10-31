#!/usr/bin/env python3
"""開発版の NDJSON から recording_pause の行と、行の種類ごとの数（時刻の範囲）だけを出す。
中身（キーストロークなど）は出さない。使い方: python3 -I pause-rows.py <ndjson>"""
import collections, datetime as dt, json, sys

if len(sys.argv) != 2:
    sys.exit("usage: pause-rows.py <ndjson>")
c = collections.Counter()
last = {}
with open(sys.argv[1], "rb") as fh:
    for n, line in enumerate(fh, 1):
        try:
            o = json.loads(line)
        except ValueError:
            c["(broken)"] += 1
            continue
        k = o.get("type")
        c[k] += 1
        t = o.get("t") or o.get("timestamp")
        if isinstance(t, (int, float)):
            last[k] = t
        if k == "recording_pause":
            print(n, dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%H:%M:%S.%f")[:-3], "paused=", o.get("paused"))
print(dict(c))
for k, t in sorted(last.items(), key=lambda x: x[1]):
    print("last", k, dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%H:%M:%S"))
