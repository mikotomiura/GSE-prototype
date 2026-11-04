"""中間の全ファイルの SHA-256 の一覧（manifest）を作る・照らす。別の PC で生データの代わりに入力を照らすため（判断 13）。

使い方:
  python3 -I manifest.py make <data_dir> <out.json> [raw_checked.json]   Mac で作る（repo の外に置く・ファイル名に番号が入るので repo に入れない）
  python3 -I manifest.py check <data_dir> <manifest.json>                 照らす。1 つでも違えば終了コード 1。件数だけを出す
対象は data_dir の下の 4 つの中間（landscape/coauthor_work・landscape/coauthor_work_obs・cs1/work2021_obs・cs1/work2021_ref）。
"""
import hashlib
import json
import os
import sys

DIRS = ["landscape/coauthor_work", "landscape/coauthor_work_obs", "cs1/work2021_obs", "cs1/work2021_ref"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def listing(data_dir):
    out = {}
    for d in DIRS:
        root = os.path.join(data_dir, d)
        for name in sorted(os.listdir(root)):
            p = os.path.join(root, name)
            if os.path.isfile(p):
                out[d + "/" + name] = sha(p)
    return out


def main():
    mode, data_dir, path = sys.argv[1:4]
    if mode == "make":
        m = dict(files=listing(data_dir))
        if len(sys.argv) > 4:
            m["raw_checked_on_mac"] = json.load(open(sys.argv[4]))
        json.dump(m, open(path, "w"), indent=0)
        print(json.dumps({d: sum(1 for k in m["files"] if k.startswith(d + "/")) for d in DIRS}))
        return 0
    m = json.load(open(path))
    got = listing(data_dir)
    bad = sum(1 for k, v in m["files"].items() if got.get(k) != v)
    extra = sum(1 for k in got if k not in m["files"])
    print(json.dumps(dict(files=len(m["files"]), mismatched_or_missing=bad, extra=extra)))
    return 0 if bad == 0 and extra == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
