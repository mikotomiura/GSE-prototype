"""Check 5, first step: the structure of the Translog-II XML of ENJA15, by element paths and attribute names only
(no attribute value, no text). Also the names of the Alignment files.

    python -I scripts/enja15_structure.py --root raw/enja15 --out results/enja15_structure.json
"""
import argparse
import json
import os
import re
import xml.etree.ElementTree as ET
from collections import Counter

NAME = re.compile(r"^P(\d+)_T(\d+)$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    xml_dir = os.path.join(args.root, "Translog-II")
    al_dir = os.path.join(args.root, "Alignment")
    paths, attrs, files_with = Counter(), Counter(), Counter()
    names = sorted(f for f in os.listdir(xml_dir) if f.endswith(".xml"))
    for fn in names:
        seen = set()
        stack = []
        for ev, el in ET.iterparse(os.path.join(xml_dir, fn), events=("start", "end")):
            if ev == "start":
                stack.append(el.tag)
                p = "/".join(stack[-3:]) if len(stack) > 3 else "/".join(stack)
                paths[p] += 1
                for a in el.attrib:
                    attrs[p + "@" + a] += 1
                    seen.add(p + "@" + a)
                seen.add(p)
            else:
                stack.pop()
                el.clear()
        files_with.update(seen)
    stems = [f[:-4] for f in names]
    parsed = [NAME.match(s) for s in stems]
    al = Counter(os.path.splitext(f)[1] for f in os.listdir(al_dir))
    al_stems = {os.path.splitext(f)[0] for f in os.listdir(al_dir)}
    out = {"xml_files": len(names), "name_pattern_P_T": sum(1 for m in parsed if m),
           "participants": len({m.group(1) for m in parsed if m}),
           "texts": len({m.group(2) for m in parsed if m}),
           "sessions_per_text": dict(Counter(m.group(2) for m in parsed if m)),
           "alignment_files_by_extension": dict(al), "alignment_stems_equal_xml_stems": al_stems == set(stems),
           "element_paths": {p: {"count": c, "files": files_with[p]} for p, c in sorted(paths.items())},
           "attribute_names": {p: {"count": c, "files": files_with[p]} for p, c in sorted(attrs.items())}}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
