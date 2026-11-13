"""変異の門の判定（conditions.md V1・追記）: 名指しの門が赤（exit 3・passed False）、run_id が今回のもの、
名指しの外で赤になる門が ALSO と完全に一致（全部を赤にする変異を素通りさせない）。外れれば exit 1。"""
import json
import os
import sys

WANT = {"n1": "P-PICK", "n2": "P-B", "n3": "P-PLAN", "n4": "P-REAL", "n5": "P-M0USE", "n6": "P-B", "n7": "P-READ",
        "n8": "P-RUN"}
# n5 は密な sens の m0 を使うので、P-B は小さな形で最頻値が全員 −∞（比べる人が 0）になり、P-RUN は渡った m0 の SHA-256 が合わない
ALSO = {"n5": {"P-B", "P-RUN"}}


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
        others = {n for n in S if n.startswith("P-") and n != ctl and not S[n]["passed"]}
        if S.get("run_id") != run_id or S.get("mutate") != [m] or S[ctl]["passed"] or others != ALSO.get(m, set()):
            bad.append((m, ctl, sorted(others)))
        print(m, ctl, "赤", "それ以外:", {n: S[n]["passed"] for n in S if n.startswith("P-") and n != ctl})
    if bad:
        sys.exit("変異の門が外れた: %r" % bad)
    print("変異の門: すべて名指しの門が赤")


if __name__ == "__main__":
    main()
