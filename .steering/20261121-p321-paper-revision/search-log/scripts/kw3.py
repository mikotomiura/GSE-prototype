import json,subprocess,urllib.parse,time,sys
sys.stdout.reconfigure(encoding='utf-8')
terms=["without consulting","without seeking help","rarely consult","resolved on their own","unaided","without external help","self-resolved"]
for t in terms:
    q='debugging %s'%t
    url='https://api.semanticscholar.org/graph/v1/paper/search?query='+urllib.parse.quote(q)+'&year=2021-2026&limit=25&fields=title,year,externalIds,abstract'
    d={}
    for k in range(6):
        r=subprocess.run(['curl','-s','-w','\n%{http_code}',url],capture_output=True,text=True,encoding='utf8')
        body,code=r.stdout.rsplit('\n',1)
        if code=='200': d=json.loads(body);break
        time.sleep(8)
    json.dump(d,open('search-log/downloads/kw3_%s.json'%t.replace(' ','_'),'w',encoding='utf8'))
    print('##',q,code,d.get('total'),len(d.get('data',[])),flush=True)
    for r in d.get('data',[]):
        a=(r.get('abstract') or '').lower()
        flag='*' if any(w in a for w in ['unaided','without consult','without seeking','without external','on their own','self-resol','rarely consult','without help']) else ' '
        print(' ',flag,r['year'],(r['title'] or '')[:85],flush=True)
    time.sleep(2)
