"""研究者のワークブック（09-18）の写しを作る（design.md §2）。

- 元のファイルの SHA-256 が repo の写し・Downloads とも既知の値であることを確かめる。
- 写しは archive と Downloads に同じバイト列で置く。どちらかが既にあれば止まる（上書きしない）。
使い方: python make_copy.py
"""
import os
import shutil
import sys

import common34 as C


def main():
    for p in (C.ORIGINAL, C.ORIGINAL_DOWNLOADS):
        got = C.sha256(p)
        if got != C.ORIGINAL_SHA256:
            sys.exit(f"元のファイルの SHA-256 が違う: {p} {got}")
    for p in (C.COPY_ARCHIVE, C.COPY_DOWNLOADS):
        if os.path.exists(p):
            sys.exit(f"写しが既にある（上書きしない）: {p}")
    os.makedirs(os.path.dirname(C.COPY_ARCHIVE), exist_ok=True)
    shutil.copyfile(C.ORIGINAL, C.COPY_ARCHIVE)
    shutil.copyfile(C.ORIGINAL, C.COPY_DOWNLOADS)
    a, d = C.sha256(C.COPY_ARCHIVE), C.sha256(C.COPY_DOWNLOADS)
    if not (a == d == C.ORIGINAL_SHA256):
        sys.exit(f"写しの SHA-256 が合わない: {a} {d}")
    with open(C.COPY_SHA_RECORD, "w", encoding="utf-8", newline="\n") as f:
        f.write(a + "\n")
    print("ok", a)


if __name__ == "__main__":
    main()
