import json
D = r"C:\Users\johnd\AppData\Local\Temp\claude\bb8fe8b6e5b059fc\1def8c19-70cb-4b34-bdf8-1327407094d2\scratchpad\searchB"
KEEP = "01 02 03 04 09 15 19 21 36 41 53 55 59 60 61 73 81 94 95 96 97 98 99 100 101 105 108 109 110 115 117 119 131 132 135 136 139 143 148 149 157 161 169".split()
ws = json.load(open(f"{D}\\works.json", encoding="utf-8"))
with open(f"{D}\\keep_urls.tsv", "w", encoding="utf-8") as f:
    for w in ws:
        n = w["id"][1:]
        if n in KEEP:
            f.write(f"{w['id']}\t{w['is_oa']}\t{w['oa_url']}\t{w['doi']}\t{w['title'][:60]}\n")
