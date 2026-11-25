"""変異（V1）: 各変異で名指しの対照が赤（終了コード 3）・変異なしは全部緑。合わなければ止める。"""
import json
import os
import sys

NAMED = dict(w1=["P-NULL"], w2=["P-HAND", "P-POS"], w3=["P-HAND"], w4=["P-HAND"], w5=["P-HAND"], w6=["P-STAT"], w7=["P-EQ"])


def main():
    d, base, run_id = sys.argv[1], sys.argv[2], sys.argv[3]
    B = json.load(open(base))
    bad = []
    if B["red"] or B.get("run_id") != run_id or B.get("mutate") is not None:
        bad.append("変異なしの selftest が緑でないか run_id が違う: %r" % B["red"])
    out = dict(run_id=run_id, code_hash=B.get("code_hash"), base_red=B["red"], mutations={})
    for m, want in NAMED.items():
        ex = int(open(os.path.join(d, m + ".exit")).read().strip())
        R = json.load(open(os.path.join(d, m + ".json")))
        ok = (ex == 3 and all(n in R["red"] for n in want) and R.get("run_id") == run_id and R.get("mutate") == m
              and R.get("code_hash") == B.get("code_hash"))
        out["mutations"][m] = dict(exit=ex, red=R["red"], named=want, ok=ok)
        if not ok:
            bad.append("%s: 名指しの対照 %r が赤にならない（赤 %r・終了 %d）" % (m, want, R["red"], ex))
    out["ok"] = not bad
    json.dump(out, open(os.path.join(d, "check.json"), "w"), indent=1, ensure_ascii=False)
    if bad:
        sys.exit("\n".join(bad))
    print("変異 7 個: 名指しの対照がすべて赤・変異なしは緑")


if __name__ == "__main__":
    main()
