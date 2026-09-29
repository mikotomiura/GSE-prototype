import json, urllib.request, sys, time
dois=sys.argv[1:]
out=[]
for d in dois:
    try:
        with urllib.request.urlopen(urllib.request.Request("https://api.crossref.org/works/"+d, headers={"User-Agent":"gse-seed-check/0.1"}), timeout=60) as r:
            m=json.load(r)["message"]
        au="; ".join((a.get("family","")+" "+a.get("given","")[:1]) for a in m.get("author",[])[:3])
        yr=(m.get("issued",{}).get("date-parts") or [[None]])[0][0]
        out.append((d,"OK",yr,au,(m.get("title") or [""])[0][:140],(m.get("container-title") or [""])[0][:60]))
    except Exception as e:
        out.append((d,"ERR "+str(e)[:40],"","","",""))
    time.sleep(0.5)
for o in out: print(" | ".join(str(x) for x in o))
