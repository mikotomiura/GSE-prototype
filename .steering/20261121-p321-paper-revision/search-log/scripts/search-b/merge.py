import json, sys
D = r"C:\Users\johnd\AppData\Local\Temp\claude\bb8fe8b6e5b059fc\1def8c19-70cb-4b34-bdf8-1327407094d2\scratchpad\searchB"
works = {}
order = []
for q in range(1, 8):
    d = json.load(open(f"{D}\\downloads\\kw_{q}.json", encoding="utf-8"))
    for w in d["results"]:
        i = w["id"]
        if i not in works:
            works[i] = {"w": w, "q": []}
            order.append(i)
        works[i]["q"].append(q)

def abst(w):
    ii = w.get("abstract_inverted_index")
    if not ii:
        return ""
    pos = {}
    for k, v in ii.items():
        for p in v:
            pos[p] = k
    return " ".join(pos[p] for p in sorted(pos))

out = []
for n, i in enumerate(order, 1):
    w = works[i]["w"]
    oa = (w.get("open_access") or {})
    loc = (w.get("primary_location") or {})
    rec = dict(id=f"K{n:02d}", oa=i, doi=w.get("doi"), title=w.get("title"), year=w.get("publication_year"),
               queries=works[i]["q"], oa_url=oa.get("oa_url"), is_oa=oa.get("is_oa"),
               landing=loc.get("landing_page_url"), abstract=abst(w))
    out.append(rec)
json.dump(out, open(f"{D}\\works.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out))
with open(f"{D}\\screen.txt", "w", encoding="utf-8") as f:
    for r in out:
        f.write(f"{r['id']} q{r['queries']} {r['year']} | {r['title']}\n   {r['abstract'][:350]}\n")
