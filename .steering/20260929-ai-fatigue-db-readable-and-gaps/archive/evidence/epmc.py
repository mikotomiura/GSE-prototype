import json, urllib.request, urllib.parse, sys, time
qs=json.load(open(sys.argv[1],encoding="utf-8"))
out=[]
for it in qs:
    url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode({"query":it["q"],"format":"json","pageSize":8,"sort":it.get("sort","CITED desc"),"resultType":"lite"},quote_via=urllib.parse.quote)
    d=None
    for k in range(6):
        try:
            d=json.load(urllib.request.urlopen(url,timeout=60)); break
        except Exception as e:
            time.sleep(10*(k+1))
    if d is None:
        print("ERR",it["q"]); continue
    top=[(r.get("pubYear"),r.get("doi"),(r.get("title") or "")[:130],r.get("journalTitle"),r.get("citedByCount"),r.get("pubType")) for r in d.get("resultList",{}).get("result",[])]
    out.append({"theme":it["theme"],"q":it["q"],"hitCount":d.get("hitCount"),"top":top})
    print(f'== {it["theme"]} | hits={d.get("hitCount")} | {it["q"]}')
    for t in top: print("   ",t)
    time.sleep(0.5)
json.dump(out,open(sys.argv[2],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
