import json, glob, os, re
D = r"C:\Users\johnd\AppData\Local\Temp\claude\bb8fe8b6e5b059fc\1def8c19-70cb-4b34-bdf8-1327407094d2\scratchpad\searchB"
ws = json.load(open(f"{D}\\works.json", encoding="utf-8"))
keepu = {}
for l in open(f"{D}\\keep_urls.tsv", encoding="utf-8"):
    p = l.rstrip("\n").split("\t")
    keepu[p[0]] = p[2]
alt = {}
for l in open(f"{D}\\arxiv_alt.txt"):
    a, b = l.split()
    alt[a] = b

cats = {
 "automated/LLM/ML/system work with no human help-seeking or resource use": "05 07 08 11 13 16 18 20 23 24 26 27 28 31 33 39 40 44 46 47 48 50 51 52 62 64 68 70 71 72 74 79 84 87 88 90 93 113 114 116 118 122 124 125 126 127 129 130 138 140 147 150 155 156 160 166 167 168 170 171 106 164 12 66 22 14 69 25 35 43 142 163 141 159 133",
 "network/security/infrastructure topic, not human help use": "67 82 89 92 37 58 63 32 80",
 "education/other non-programming or non-help topic": "06 10 17 29 30 34 38 42 45 49 54 56 57 65 75 76 77 78 83 85 86 91 102 103 104 107 111 112 120 121 123 128 134 137 144 145 146 151 152 153 154 158 162 165 13 47",
}
off = {}
for r, ids in cats.items():
    for i in ids.split():
        off.setdefault("K" + i, r)
keep = "01 02 03 04 09 15 19 21 36 41 53 55 59 60 61 73 81 94 95 96 97 98 99 100 101 105 108 109 110 115 117 119 131 132 135 136 139 143 148 149 157 161 169".split()
status = {}
note = {}
src = {}
for k in keep:
    k = "K" + k
    p = f"{D}\\downloads\\{k}.txt"
    if os.path.exists(p):
        status[k] = "NONE"; note[k] = "read; no relevant passage (all regex hits read in context)"
        src[k] = alt.get(k) and "https://arxiv.org/pdf/" + alt[k].split(":")[-1] or keepu[k]
for k, v in alt.items():
    src[k] = "https://arxiv.org/pdf/" + v.split("/")[-1]
src["K01"] = "https://arxiv.org/pdf/2210.03804"; src["K04"] = "https://arxiv.org/pdf/2308.05487"; src["K73"] = "https://arxiv.org/pdf/2511.18985"; src["K135"] = "https://arxiv.org/pdf/2609.04214"; src["K139"] = "https://arxiv.org/pdf/2606.06253"
status["K19"] = "INSTANCE"
note["K19"] = ('txt line 31 (abstract) and 367: "The students were able to find correct answers to almost 80% of the questions without support from the teaching staff." '
               '(abstract l.30-31: "most of the training question attempts resulted in finding the correct answer without help from the teaching staff"; drop in staff questions read as reduced need)')
status["K169"] = "NEAR"
note["K169"] = ('txt line 129: "The remaining questions were self-resolved, or marked by the student as no longer relevant." Reason: units that had a recorded request but no educator answer are read as self-resolved; consultation of staff was recorded, only no answer')
status["K73"] = "NONE"; note["K73"] = "read; help-seeking is the topic (executive vs instrumental queries); l.202 'do not reliably resolve on their own' is about help-seeking patterns not episodes"
status["K108"] = "NONE"; note["K108"] = "read; unaided is an assigned experimental condition (txt l.432,438), not an inference from absent consultation"
status["K95"] = "NONE"; note["K95"] = "read; independence of children scored by direct observation of adult support (l.245,270), not inferred from absent records"
for k in ("K109", "K110"):
    status[k] = "NONE"; note[k] = "same title as K105; arXiv version (K105 text) read; journal-version PDF 404, not read"
    src[k] = "https://arxiv.org/pdf/2508.05999 (K105 arXiv version)"
for k in "K02 K03 K41 K53 K55 K59 K61 K96 K131 K136 K143 K148 K149 K157".split():
    status[k] = "NOT-READ"; note[k] = "no free full text retrievable by plain curl (HTTP 403/401/000/HTML landing page or paywall); no arXiv version found by title"
    src[k] = keepu.get(k, "")
status["K96"] = "NOT-READ"; note["K96"] = "OA link returned HTML not PDF (doi.org landing); no arXiv version found by title"
rows = []
cnt = dict(INSTANCE=0, NEAR=0, NONE=0, **{"NOT-READ": 0})
for w in ws:
    k = w["id"]
    n = k[1:]
    q = ";".join(str(x) for x in w["queries"])
    if n in keep:
        st = status[k]; sc = "KEEP"; rs = "human programming/debugging/help-use context"
        cnt[st] += 1
        fu = src.get(k, "")
    else:
        st = "-"; sc = "OFF-TOPIC"; rs = off.get(k, "not about humans debugging/programming with help use")
        fu = ""; note[k] = "-"
    clean = lambda s: (s or "").replace("\t", " ").replace("\n", " ")
    rows.append([k, w["oa"], w["doi"] or "", clean(w["title"]), str(w["year"]), q, sc, rs, fu, st, clean(note[k])])
with open(f"{D}\\keyword-hits.tsv", "w", encoding="utf-8", newline="") as f:
    f.write("\t".join("id openalex_id doi title year queries screen screen_reason fulltext_url status note".split()) + "\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
print(cnt, sum(1 for r in rows if r[6] == "KEEP"), len(rows))
