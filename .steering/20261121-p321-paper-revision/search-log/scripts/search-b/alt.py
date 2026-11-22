import json, subprocess, urllib.parse, re, time
D = r"C:\Users\johnd\AppData\Local\Temp\claude\bb8fe8b6e5b059fc\1def8c19-70cb-4b34-bdf8-1327407094d2\scratchpad\searchB"
ws = {w["id"]: w for w in json.load(open(f"{D}\\works.json", encoding="utf-8"))}
miss = "K01 K02 K03 K04 K41 K53 K55 K59 K61 K73 K96 K131 K135 K136 K139 K143 K148 K149 K157 K109 K110".split()
for k in miss:
    t = ws[k]["title"]
    q = urllib.parse.quote('ti:"%s"' % re.sub(r'[^A-Za-z0-9 ]', ' ', t)[:120])
    r = subprocess.run(["curl", "-s", "-L", "--max-time", "30", f"https://export.arxiv.org/api/query?search_query={q}&max_results=2"], capture_output=True, text=True, encoding="utf-8")
    ents = re.findall(r"<entry>.*?<id>(.*?)</id>.*?<title>(.*?)</title>", r.stdout, re.S)
    print(k, t[:50], "->", [(a, re.sub(r"\s+", " ", b)[:60]) for a, b in ents])
    time.sleep(3)
