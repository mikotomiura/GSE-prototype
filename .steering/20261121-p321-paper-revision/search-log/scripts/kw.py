import json,subprocess,urllib.parse,time,sys
sys.stdout.reconfigure(encoding='utf-8')
terms=["without consulting","without seeking help","rarely consult","resolved on their own","unaided","without external help","self-resolved"]
out=[]
for t in terms:
    q='debugging "%s"'%t
    url='https://api.openalex.org/works?search='+urllib.parse.quote(q)+'&filter=publication_year:2021-2026&per-page=50&select=id,doi,title,publication_year,abstract_inverted_index'
    for k in range(5):
        r=subprocess.run(['curl','-s','-w','\n%{http_code}',url],capture_output=True,text=True,encoding='utf8')
        body,code=r.stdout.rsplit('\n',1)
        if code=='200': break
        time.sleep(10)
    d=json.loads(body) if code=='200' else {}
    res=d.get('results',[])
    json.dump(d,open('search-log/downloads/kw_%s.json'%t.replace(' ','_'),'w',encoding='utf8'))
    out.append((q,code,d.get('meta',{}).get('count'),len(res)))
    print('##',q,code,d.get('meta',{}).get('count'),len(res))
    for r in res: print('  ',r['id'][-11:],r['publication_year'],(r['title'] or '')[:90])
    time.sleep(1)
