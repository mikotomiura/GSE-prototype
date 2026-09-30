import json, urllib.request, urllib.parse, urllib.error, sys, time
def get(url):
    for k in range(10):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"gse-scoping-probe/0.1"}), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code==429:
                ra=e.headers.get("Retry-After")
                time.sleep((int(ra) if ra and ra.isdigit() else 30)+3); continue
            raise
    raise RuntimeError("429 persists")
def count(q, flt=None):
    params={"search":q,"per-page":"5","select":"id,doi,title,publication_year,cited_by_count,type"}
    if flt: params["filter"]=flt
    d=get("https://api.openalex.org/works?"+urllib.parse.urlencode(params))
    return d["meta"]["count"], d["results"]
qs=json.load(open(sys.argv[1],encoding="utf-8"))
prev={}
try:
    for o in json.load(open(sys.argv[2],encoding="utf-8")):
        if o.get("count") is not None: prev[(o["q"],o.get("filter"))]=o
except Exception: pass
out=[]
for item in qs:
    q=item["q"]; flt=item.get("filter")
    if (q,flt) in prev:
        o=dict(prev[(q,flt)]); o["theme"]=item["theme"]; out.append(o); continue
    try:
        n,res=count(q,flt)
    except Exception as e:
        n,res=None,[]; print("ERR",q,e)
    out.append({"theme":item["theme"],"q":q,"filter":flt,"count":n,"top":[{"doi":x.get("doi"),"title":x.get("title"),"year":x.get("publication_year"),"cites":x.get("cited_by_count"),"type":x.get("type")} for x in res]})
    time.sleep(2.0)
json.dump(out,open(sys.argv[2],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
for o in out:
    print(f'{o["theme"]} | {o["q"]} | n={o["count"]}')
