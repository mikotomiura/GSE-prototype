"""変異の結果を確かめる（conditions.md W3）。各変異の終了コードが 3、JSON の run_id が今回のもの、
名指しの門が FAIL、変異の名が JSON に入っていること。どれかが違えば終了コード 3。
使い方: python3 -I -X utf8 check_mutations.py MUT_DIR RUN_ID"""
import json
import os
import sys

EXPECT = {"w1": "W1", "w2": "W2", "w3": "W5", "w4": "W1", "w5": "W5"}


def main(d, run_id):
    bad = []
    for m, g in EXPECT.items():
        try:
            code = int(open(os.path.join(d, f"{m}.exit")).read().strip())
            j = json.load(open(os.path.join(d, f"{m}.json")))
        except (OSError, ValueError) as e:
            bad.append(f"{m}: 読めない（{e}）")
            continue
        if code != 3:
            bad.append(f"{m}: 終了コード {code}")
        if j.get("run_id") != run_id:
            bad.append(f"{m}: run_id が違う")
        if m not in j.get("mutate", []):
            bad.append(f"{m}: 変異が JSON に無い")
        gate = j.get("gates", {}).get(g, {})
        if gate.get("ok") is not False:
            bad.append(f"{m}: {g} が FAIL でない")
        if m == "w4":  # 狙いは値の比べ: 番号か条件の食い違いで赤になったなら狙いを外している
            reasons = gate.get("bad", [])
            if not reasons or any("番号か条件" in b for b in reasons) or not all("が違う" in b for b in reasons):
                bad.append(f"{m}: {g} の赤の理由が値の比べでない {reasons[:2]}")
    print("mutations", "OK" if not bad else "FAIL", bad)
    sys.exit(0 if not bad else 3)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
