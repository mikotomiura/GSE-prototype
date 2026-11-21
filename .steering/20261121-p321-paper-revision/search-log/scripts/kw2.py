import json,subprocess,urllib.parse,time,sys
sys.stdout.reconfigure(encoding='utf-8')
terms=["without consulting","without seeking help","rarely consult","resolved on their own","unaided","without external help","self-resolved"]
for t in terms:
    q='debugging + "%s"'%t
    url='https://api.semanticscholar.org/graph/v1/paper/search/bulk?query='+urllib.parse.quote(q)+'&year=2021-2026&fields=title,year,externalIds,abstract'
    d={}
    for k in range(6):
        r=subprocess.run(['curl','-s','-w','\n%{http_code}',url],capture_output=True,text=True,encoding='utf8')
        body,code=r.stdout.rsplit('\n',1)
        if code=='200': d=json.loads(body);break
        time.sleep(8)
    json.dump(d,open('search-log/downloads/kw_%s.json'%t.replace(' ','_'),'w',encoding='utf8'))
    print('##',q,code,d.get('total'),len(d.get('data',[])),flush=True)
    for r in d.get('data',[]): print('  ',r['year'],(r['title'] or '')[:95],'|',(r.get('externalIds') or {}).get('DOI',''),flush=True)
    time.sleep(2)
