import json, re, urllib.request, urllib.parse, time, xml.etree.ElementTree as ET
AI=re.compile(r"(AI|ＡＩ|人工知能|生成|ChatGPT|チャットGPT|LLM|大規模言語モデル)")
FT=re.compile(r"(疲|燃え尽き|バーンアウト|テクノストレス|消耗|負担|ストレス)")
qs=["生成AI 疲労","AI 疲労","AI疲れ","人工知能 疲労","生成AI テクノストレス","ChatGPT 負担","生成AI バーンアウト","生成AI 認知負荷"]
res={}
def jstage(q):
    url="https://api.jstage.jst.go.jp/searchapi/do?"+urllib.parse.urlencode({"service":3,"text":q,"count":100})
    x=urllib.request.urlopen(url,timeout=60).read()
    root=ET.fromstring(x); ns={"a":"http://www.w3.org/2005/Atom","o":"http://a9.com/-/spec/opensearch/1.1/"}
    tot=root.find("o:totalResults",ns).text
    items=[]
    for e in root.findall("a:entry",ns):
        ja=e.find("a:article_title/a:ja",ns); en=e.find("a:article_title/a:en",ns)
        t=(ja.text if ja is not None and ja.text else "") or (en.text if en is not None else "")
        link=e.find("a:article_link/a:ja",ns)
        yr=e.find("a:pubyear",ns)
        items.append((t,(link.text if link is not None else ""),(yr.text if yr is not None else "")))
    return tot,items
def cinii(q):
    url="https://cir.nii.ac.jp/opensearch/all?"+urllib.parse.urlencode({"q":q,"format":"json","count":100},quote_via=urllib.parse.quote)
    d=json.load(urllib.request.urlopen(url,timeout=60))
    tot=d.get("opensearch:totalResults")
    items=[(it.get("title",""),it.get("@id",""),(it.get("prism:publicationDate") or "")[:4]) for it in d.get("items",[])]
    return tot,items
out={}
for q in qs:
    for name,f in (("J-STAGE",jstage),("CiNii",cinii)):
        try:
            tot,items=f(q)
        except Exception as e:
            print("ERR",name,q,e); continue
        hit=[i for i in items if AI.search(i[0]) and FT.search(i[0])]
        out[f"{name}|{q}"]={"total":tot,"top100_title_hits":hit}
        print(f"{name} | {q} | total={tot} | 上位100件中 題名に AI語×疲労語 = {len(hit)}")
        time.sleep(1)
json.dump(out,open("jp_out.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
seen={}
for k,v in out.items():
    for t,l,y in v["top100_title_hits"]:
        seen.setdefault(t,(l,y,k))
print("---- unique titles:",len(seen))
for t,(l,y,k) in sorted(seen.items(), key=lambda x:x[1][1], reverse=True):
    print(y,"|",t[:110],"|",l)
