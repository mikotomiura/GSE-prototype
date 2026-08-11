"""展開ツリーのファイルをテキスト/バイナリに分類する (標準ライブラリのみ)。

判定: 先頭 8192 バイトに NUL バイトが含まれるか / UTF-8 or latin-1 でデコードできるか。
"""
import sys
import os
from collections import Counter

root = sys.argv[1]

counts = Counter()
binaries = []
empties = []
total = 0
total_bytes = 0

for dirpath, dirnames, filenames in os.walk(root):
    for name in filenames:
        p = os.path.join(dirpath, name)
        total += 1
        size = os.path.getsize(p)
        total_bytes += size
        if size == 0:
            counts["empty"] += 1
            empties.append(p)
            continue
        with open(p, "rb") as fh:
            head = fh.read(8192)
        if b"\x00" in head:
            counts["binary(NUL)"] += 1
            binaries.append((size, p))
            continue
        try:
            head.decode("utf-8")
            counts["text(utf-8)"] += 1
        except UnicodeDecodeError:
            # 8192 境界で多バイト文字が切れた可能性を除外してから判定する
            try:
                head[:-4].decode("utf-8")
                counts["text(utf-8)"] += 1
            except UnicodeDecodeError:
                counts["text(non-utf8 bytes)"] += 1
                binaries.append((size, p))

print(f"root            : {root}")
print(f"total files     : {total}")
print(f"total bytes     : {total_bytes:,}")
print("--- classification ---")
for k, v in counts.most_common():
    print(f"  {k:24s} {v}")

if binaries:
    print("--- non-text files (size desc, top 30) ---")
    for size, p in sorted(binaries, reverse=True)[:30]:
        print(f"  {size:>12,}  {p}")
if empties:
    print(f"--- empty files: {len(empties)} (top 10) ---")
    for p in empties[:10]:
        print(f"  {p}")
