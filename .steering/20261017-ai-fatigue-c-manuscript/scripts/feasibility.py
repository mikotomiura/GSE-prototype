"""Feasibility estimate for C's confirmation set (not part of the registration).

Reads the additional-candidates table (judge 1 copy, SHA-256 checked) and simulates,
per record, whether it ends up as an included primary study, then walks the
post-registration screening order (GSRR-33: per-group shuffle with seed 20261018,
groups interleaved) to see how the confirmation set grows with the number of
records that both screeners have finished.

The rates are assumptions anchored in:
- the 34-record final decisions (judge 2 file, SHA-256 e302b711...be4a):
  direct studies 12 -> include 9, pending 3 (E6); adjacent studies 6 -> include 1;
- proposal v2 section 7.2: of the 61 records the AI marked include, judge 1 marked
  44 include and 14 pending; of the 10 the AI marked exclude, 5 include and 1 pending.

Usage:  python3 -I feasibility.py <candidates.xlsx> <sha256-record> > feasibility-output.txt
This output is an internal planning aid. It must not go into the registration or the
manuscript (it is a prediction of the result).
"""
import hashlib
import random
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict

SCREEN_SEED = 20261018
MC_SEED = 20261017
RUNS = 4000
CAL_REMOVE = 5            # one calibration round (GSRR-39); 10 or 15 if agreement is low
POOL_MIN = 25             # below this, calibration uses exploration records (GSRR-39)
TABLE_MIN = 10            # studies per table for proportions (GSRR-39)
R_SEARCH = 43             # review-search records, not in the table (GSRR-32)

POP = {
    "学生・学習者": "students_learners", "教員・研究者": "teachers_researchers",
    "働く人（医療・教育の外）": "workers_other", "医療者": "health_professionals",
    "消費者・一般の利用者": "consumers_general", "不明": "unknown",
}
POPULATION_ORDER = list(POP.values())

FATIGUE = re.compile(r"fatigu|tired|exhaust|deplet|burn-?out|weariness", re.I)

# Scenario parameters: (low, central, high)
SCEN = {
    # P(final decision after title/abstract stage = pass), by prior status
    "ta_J1_include": (0.90, 0.95, 1.00),
    "ta_J1_pending": (0.60, 0.80, 0.90),
    "ta_J1_exclude": (0.05, 0.15, 0.30),
    "ta_AI_include": (0.80, 0.90, 0.95),
    "ta_AI_exclude": (0.40, 0.50, 0.60),
    # P(include at full text | passed, full text obtained)
    "ft_title_term": (0.50, 0.70, 0.80),
    "ft_no_title_term": (0.10, 0.20, 0.35),
    # P(full text obtained) when no free version was found
    "obtain_nonfree": (0.30, 0.60, 0.85),
    # P(include) for records already read in full by judge 1 (8) and review-search records
    "p_fulltext_done": (0.00, 0.02, 0.05),
    "p_review_search": (0.00, 0.02, 0.05),
    # person-minutes
    "min_ta": (1.0, 1.5, 2.5),
    "min_ft": (20, 30, 45),
}
LEVELS = {"low": 0, "central": 1, "high": 2}


def read_sheet(path, name):
    z = zipfile.ZipFile(path)
    m = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    r_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        ss = ["".join(t.text or "" for t in si.iter(m + "t"))
              for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(m + "si")]
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    for s in ET.fromstring(z.read("xl/workbook.xml")).iter(m + "sheet"):
        if s.get("name") != name:
            continue
        target = rels[s.get(r_ns)].lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        out = []
        for row in ET.fromstring(z.read(target)).iter(m + "row"):
            cells = {}
            for c in row.findall(m + "c"):
                col = re.match(r"[A-Z]+", c.get("r")).group()
                if c.get("t") == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter(m + "t"))
                else:
                    v = c.find(m + "v")
                    val = "" if v is None else (ss[int(v.text)] if c.get("t") == "s" else v.text)
                cells[col] = val
            out.append(cells)
        return out
    sys.exit(f"sheet not found: {name}")


def load(path, sha_record):
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if digest not in open(sha_record, encoding="utf-8").read():
        sys.exit(f"SHA-256 mismatch: {digest}")
    rows = read_sheet(path, "スクリーニング")
    header = next(i for i, r in enumerate(rows) if r.get("A") == "ID")
    recs = []
    for r in rows[header + 1:]:
        rid = r.get("A", "")
        if not rid:
            continue
        pop_ja = r.get("Q", "").split("｜")[0]
        stage = r.get("S", "")
        if stage.startswith("全文段"):
            status = "fulltext_done"
        elif r.get("D", "") != "未判定":
            status = {"含める": "J1_include", "保留": "J1_pending"}.get(r["D"], "J1_exclude")
        else:
            status = "AI_include" if r.get("T", "").startswith("含める") else "AI_exclude"
        group = re.match(r"(G\d+|U\d+)", r.get("P", ""))
        recs.append({
            "id": rid,
            "population": POP.get(pop_ja, "review_type" if pop_ja == "レビュー等" else "unlabelled"),
            "status": status,
            "title_term": bool(FATIGUE.search(r.get("B", ""))),
            "free": r.get("O", "").startswith("無料の版あり"),
            "e5_group": group.group(1) if group else None,
            "judge1_ta_done": status.startswith("J1") or status == "fulltext_done",
        })
    for k in range(1, R_SEARCH + 1):
        recs.append({"id": f"R{k:02d}", "population": "review_search", "status": "review_search",
                     "title_term": False, "free": True, "e5_group": None, "judge1_ta_done": False})
    return recs, digest


def screening_order(recs):
    by_group = defaultdict(list)
    for r in recs:
        by_group[r["population"]].append(r["id"])
    groups = POPULATION_ORDER + sorted(set(by_group) - set(POPULATION_ORDER))
    queues = {}
    for g in groups:
        ids = sorted(by_group.get(g, []))
        random.Random(SCREEN_SEED).shuffle(ids)
        queues[g] = ids
    order = []
    while any(queues.values()):
        for g in groups:
            if queues[g]:
                order.append(queues[g].pop(0))
    return order


def p_pass(r, p):
    return p["ta_" + r["status"]]


def p_include(r, p):
    if r["status"] == "fulltext_done":
        return p["p_fulltext_done"]
    if r["status"] == "review_search":
        return p["p_review_search"]
    obtain = 1.0 if r["free"] else p["obtain_nonfree"]
    ft = p["ft_title_term"] if r["title_term"] else p["ft_no_title_term"]
    return p_pass(r, p) * obtain * ft


def minutes(r, p):
    """Expected person-minutes to bring one record to a final decision by both screeners."""
    if r["status"] in ("fulltext_done",):
        return p["min_ft"]                      # judge 2 reads the full text
    ta = p["min_ta"] * (1 if r["judge1_ta_done"] else 2)
    passed = 0.2 if r["status"] == "review_search" else p_pass(r, p)   # mostly E4 at TA
    return ta + passed * 2 * p["min_ft"]


def simulate(recs, order, p, checkpoints, rng):
    pos = {rid: i for i, rid in enumerate(order)}
    byid = {r["id"]: r for r in recs}
    out = {n: [] for n in checkpoints}
    for _ in range(RUNS):
        inc = [rid for rid in order if rng.random() < p_include(byid[rid], p)]
        for n in checkpoints:
            done = [rid for rid in inc if pos[rid] < n]
            studies, seen = [], set()
            for rid in done:
                g = byid[rid]["e5_group"]
                if g and g in seen:
                    continue
                if g:
                    seen.add(g)
                studies.append(rid)
            pool = len(studies)
            kept = studies
            if pool >= POOL_MIN:
                drop = set(rng.sample(sorted(studies), CAL_REMOVE))
                kept = [s for s in studies if s not in drop]
            per_pop = Counter(byid[s]["population"] for s in kept)
            out[n].append((pool, len(kept), sum(1 for v in per_pop.values() if v >= TABLE_MIN),
                           per_pop))
    return out


def q(xs, f):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(f * len(xs)))]


def main():
    recs, digest = load(sys.argv[1], sys.argv[2])
    order = screening_order(recs)
    print(f"candidates.xlsx SHA-256 {digest}")
    print(f"records {len(recs)} (table {len(recs) - R_SEARCH} + review search {R_SEARCH})")
    print("by population:", dict(Counter(r["population"] for r in recs)))
    print("by status:", dict(Counter(r["status"] for r in recs)))
    print("title term among TA-stage records:",
          dict(Counter((r["status"], r["title_term"]) for r in recs
                       if r["status"] not in ("fulltext_done", "review_search"))))
    print("no free version:", sum(1 for r in recs if not r["free"]))
    print("E5 groups:", len({r['e5_group'] for r in recs if r['e5_group']}),
          "records in them:", sum(1 for r in recs if r["e5_group"]))
    checkpoints = [30, 60, 90, 120, 150, 180, 220, len(order)]
    for name, lv in LEVELS.items():
        p = {k: v[lv] for k, v in SCEN.items()}
        rng = random.Random(MC_SEED)
        exp_total = sum(p_include(r, p) for r in recs)
        print(f"\n== scenario {name}: expected included records if all {len(recs)} are finished = "
              f"{exp_total:.1f}")
        print("expected included records by population (all finished):",
              {g: round(sum(p_include(r, p) for r in recs if r["population"] == g), 1)
               for g in POPULATION_ORDER + ["review_type", "unlabelled", "review_search"]})
        res = simulate(recs, order, p, checkpoints, rng)
        print("N_done | hours(2 people, this scenario) | pool median [10%,90%] | P(pool>=25) | "
              "kept median | groups with >=10 (mean) | per-group median at N")
        for n in checkpoints:
            hrs = sum(minutes({**r}, p) for r in recs if r["id"] in set(order[:n])) / 60
            pools = [x[0] for x in res[n]]
            kept = [x[1] for x in res[n]]
            g10 = sum(x[2] for x in res[n]) / RUNS
            per = {g: q([x[3].get(g, 0) for x in res[n]], 0.5) for g in POPULATION_ORDER}
            print(f"{n:6d} | {hrs:6.0f} | {q(pools, .5):3d} [{q(pools, .1)},{q(pools, .9)}] | "
                  f"{sum(1 for x in pools if x >= POOL_MIN) / RUNS:.2f} | {q(kept, .5):3d} | "
                  f"{g10:.2f} | {per}")
    hours_table(recs, order)


def hours_table(recs, order):
    """Hours for both screeners together, central screening rates, varying minutes per full text."""
    print("\n== hours (central rates) to finish the first N records in the screening order")
    print("N_done | FT 20 min | FT 30 min | FT 45 min")
    for n in [60, 90, 120, 150, 180, 220, len(order)]:
        done = set(order[:n])
        row = []
        for ft in (20, 30, 45):
            p = {k: v[1] for k, v in SCEN.items()}
            p["min_ft"] = ft
            row.append(sum(minutes(r, p) for r in recs if r["id"] in done) / 60)
        print(f"{n:6d} | " + " | ".join(f"{h:6.0f}" for h in row))


if __name__ == "__main__":
    main()
