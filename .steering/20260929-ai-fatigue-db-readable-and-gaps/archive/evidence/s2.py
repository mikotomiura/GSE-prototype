import json, urllib.request, urllib.parse, urllib.error, sys, time
qs=json.load(open(sys.argv[1],encoding="utf-8"))
out=[]
for it in qs:
    url="https://api.semanticscholar.org/graph/v1/paper/search/bulk?"+urllib.parse.urlencode({"query":it["q"],"fields":"title,year,externalIds,citationCount"},quote_via=urllib.parse.quote)
    d=None
    for k in range(8):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"gse-scoping-probe/0.1"}),timeout=60)); break
        except urllib.error.HTTPError as e:
            time.sleep(5*(k+1))
        except Exception as e:
            time.sleep(5)
    if d is None:
        print("ERR",it["q"]); out.append({"theme":it["theme"],"q":it["q"],"total":None}); continue
    top=sorted(d.get("data",[]),key=lambda x:-(x.get("citationCount") or 0))[:5]
    out.append({"theme":it["theme"],"q":it["q"],"total":d.get("total"),"top":[(x.get("year"),(x.get("externalIds") or {}).get("DOI"),x.get("title"),x.get("citationCount")) for x in top]})
    print(f'== {it["theme"]} | total={d.get("total")} | {it["q"]}')
    for t in out[-1]["top"]: print("    ",t)
    time.sleep(1.5)
json.dump(out,open(sys.argv[2],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
