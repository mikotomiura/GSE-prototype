import json,subprocess,os,re
from concurrent.futures import ThreadPoolExecutor
D='search-log/downloads/'
uni=json.load(open(D+'merged.json',encoding='utf8'))
os.makedirs(D+'pdf',exist_ok=True)
def cands(u):
    c=[]
    m=re.match(r'10\.48550/arxiv\.(.+)',u['doi'])
    if m: c.append('https://arxiv.org/pdf/'+m.group(1))
    if u['arx']: c.append('https://arxiv.org/pdf/'+u['arx'])
    c+= [x for x in u['oa'] if x]
    return list(dict.fromkeys(c))
def work(u):
    out=D+'pdf/%s.pdf'%u['id']
    for url in cands(u):
        try:
            r=subprocess.run(['curl','-sL','--max-time','60','-o',out,'-w','%{http_code}',url],capture_output=True,text=True,timeout=90)
        except Exception as e: continue
        try:
            ok=open(out,'rb').read(5)==b'%PDF-'
        except: ok=False
        if ok: return u['id'],url,r.stdout
        if os.path.exists(out): os.remove(out)
    return u['id'],None,''
with ThreadPoolExecutor(6) as ex:
    res=list(ex.map(work,uni))
json.dump(res,open(D+'dl.json','w'))
for r in res: print(*r)
