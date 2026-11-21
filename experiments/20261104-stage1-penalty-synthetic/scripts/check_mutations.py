"""変異の結果を確かめる（conditions.md C5）。各変異の終了コードが 3、JSON の run_id が今回のもの、
名指しの門が FAIL、変異の名が JSON に入っていること。どれかが違えば終了コード 3。
使い方: python3 -I -X utf8 check_mutations.py MUT_DIR RUN_ID"""
import json
import os
import sys

EXPECT = {"m1": "G2", "m2": "G3", "m3": "G1", "m4": "G8", "m5": "G4"}


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
        if j.get("gates", {}).get(g, {}).get("ok") is not False:
            bad.append(f"{m}: {g} が FAIL でない")
    print("mutations", "OK" if not bad else "FAIL", bad)
    sys.exit(0 if not bad else 3)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
