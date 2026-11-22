"""D5 の案の選び（選びの組・CoAuthor k = 5・間なし）。規則は conditions.md D5 の 1〜4 の順。

使い方: python3 -I choose.py <out_dir> [--null2 <HP Z2 の summary_null2.json>]
読む: <out_dir>/select/summary_null1.json と、第 2 の帰無の集計（既定 <out_dir>/hpz2/select/summary_null2.json）。
出力: <out_dir>/select/d5.json（各量と選んだ案）。許された案が 0、外しの後が 0 なら止める（終了コード 4・D8）。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eye as EY  # noqa: E402
import run_eye as RE  # noqa: E402

CELL = "k5_g0"
ALLOW_MAX = 68
NULLS = [(1, "null1_dose_coauthor_0.0"), (2, "null2_dose_coauthor_0.0"), (1, "null1_struct_coauthor_0.0"),
         (1, "null1_wobble_coauthor_0.0"), (1, "null1_volume_coauthor_0.0"), (1, "null1_drift_coauthor_0.0"),
         (1, "null1_stack_coauthor_0.0")]
DROP = (2, "null2_dose_coauthor_0.03")
STAGES = [("段 1: 第 1 の帰無の 3e-3", (1, "null1_dose_coauthor_0.003")),
          ("段 2: 第 1 の帰無の 1e-2", (1, "null1_dose_coauthor_0.01")),
          ("段 3: 分布の筋", (1, "null1_dist_coauthor_0.03"))]
MARGIN = 0.03


def main():
    argv = sys.argv[1:]
    n2 = None
    if "--null2" in argv:
        i = argv.index("--null2")
        n2 = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    out = argv[0]
    d = os.path.join(out, "select")
    paths = {1: os.path.join(d, "summary_null1.json"), 2: n2 or os.path.join(out, "hpz2", "select", "summary_null2.json")}
    ch = RE.code_hash()
    S = {}
    for n in (1, 2):
        s = json.load(open(paths[n]))
        if s["code_hash"] != ch or s["which"] != "select":
            sys.exit("summary_null%d.json のコードのハッシュか組が違う" % n)
        S[n] = s["groups"]

    def q(key, e, what="n_rej"):
        n, g = key
        c = S[n][g][CELL]
        return c[e]["0.05"][what]

    R = dict(code_hash=ch, cell=CELL, allow={}, drop={}, stages=[], pairs={})
    # 1. 許す
    for e in EY.EYES:
        cnt = {g: q((n, g), e) for n, g in NULLS}
        R["allow"][e] = dict(counts=cnt, ok=all(v <= ALLOW_MAX for v in cnt.values()))
    left = [e for e in EY.EYES if R["allow"][e]["ok"]]
    R["after_allow"] = list(left)
    if not left:
        R["stop"] = "許された案が 0（D5 の 1・D8）"
        json.dump(R, open(os.path.join(d, "d5.json"), "w"), indent=1, ensure_ascii=False)
        print(R["stop"])
        sys.exit(4)
    # 2. 外す
    for e in left:
        pw = q(DROP, e, "rate")
        R["drop"][e] = dict(power=pw, keep=pw >= 0.8)
    left = [e for e in left if R["drop"][e]["keep"]]
    R["after_drop"] = list(left)
    if not left:
        R["stop"] = "第 2 の帰無の 3e-2 で 0.8 以上の案が 0（D5 の 2・D8）"
        json.dump(R, open(os.path.join(d, "d5.json"), "w"), indent=1, ensure_ascii=False)
        print(R["stop"])
        sys.exit(4)
    # 3. 選ぶ
    for name, key in STAGES:
        if len(left) == 1:
            break
        vals = {e: q(key, e, "rate") for e in left}
        mx = max(vals.values())
        keep = [e for e in left if mx - vals[e] < MARGIN]
        R["stages"].append(dict(stage=name, values=vals, max=mx, kept=keep))
        left = keep
    if len(left) > 1:
        left = [min(left, key=EY.EYES.index)]
        R["stages"].append(dict(stage="段 4: E1 > E2 > E3 の順", kept=list(left)))
    R["chosen"] = left[0]
    # 4. 対の差と SE（記述・0.03 は変えない）
    for name, key in [("drop", DROP)] + STAGES:
        n, g = key
        R["pairs"][g] = S[n][g][CELL]["pairs"]
    json.dump(R, open(os.path.join(d, "d5.json"), "w"), indent=1, ensure_ascii=False)
    print("選んだ案: %s" % R["chosen"])


if __name__ == "__main__":
    main()
