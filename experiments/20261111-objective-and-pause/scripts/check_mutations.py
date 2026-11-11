"""変異の門の判定（conditions.md V1）: 名指しの門が赤（exit 3・passed False）で、run_id が今回のもの。外れれば exit 1。"""
import json
import os
import sys

WANT = {"o1": "P-MEAN", "o2": "P-NOW", "o3": "P-NEGINF"}


def main():
    d, run_id = sys.argv[1], sys.argv[2]
    bad = []
    for m, ctl in WANT.items():
        ex = open(os.path.join(d, m + ".exit")).read().strip()
        p = os.path.join(d, m + ".json")
        if ex != "3" or not os.path.exists(p):
            bad.append((m, "exit " + ex))
            continue
        S = json.load(open(p))
        if S.get("run_id") != run_id or S[ctl]["passed"]:
            bad.append((m, ctl))
        print(m, ctl, "赤", "それ以外:", {n: S[n]["passed"] for n in S if n.startswith("P-") and n != ctl})
    if bad:
        sys.exit("変異の門が外れた: %r" % bad)
    print("変異の門: すべて名指しの門が赤")


if __name__ == "__main__":
    main()
