import sys; sys.stdout.reconfigure(encoding="utf-8")
import json,re,sys
D='search-log/downloads/'
works={}
def norm(t): return re.sub(r'[^a-z0-9]','',(t or '').lower())
def key_of(doi,arx,title):
    return None
recs=[]
for w,c in [('W4386603916','D1'),('W7128812742','D2')]:
    for r in json.load(open(D+'oa_%s.json'%w,encoding='utf8'))['results']:
        doi=(r.get('doi') or '').replace('https://doi.org/','').lower()
        arx=''
        for l in r.get('locations') or []:
            u=l.get('landing_page_url') or ''
            m=re.search(r'arxiv.org/abs/([\d.]+)',u)
            if m: arx=m.group(1)
        pdfs=[l.get('pdf_url') or l.get('landing_page_url') for l in (r.get('locations') or []) if l.get('is_oa')]
        recs.append(dict(src='openalex',cites=c,title=r['title'],year=r['publication_year'],doi=doi,arx=arx,oa=[p for p in pdfs if p],ctx=[]))
for i,c in [(1,'D1'),(2,'D1'),(3,'D2'),(4,'D2')]:
    for r in json.load(open(D+'s2_%d.json'%i,encoding='utf8'))['data']:
        p=r['citingPaper']; e=p.get('externalIds') or {}
        recs.append(dict(src='s2',cites=c,title=p['title'],year=p['year'],doi=(e.get('DOI') or '').lower(),arx=e.get('ArXiv') or '',oa=[(p.get('openAccessPdf') or {}).get('url')] if p.get('openAccessPdf') else [],ctx=r.get('contexts') or []))
uni=[]
def match(a,b):
    return (a['doi'] and a['doi']==b['doi']) or (a['arx'] and a['arx']==b['arx']) or norm(a['title'])==norm(b['title'])
for r in recs:
    for u in uni:
        if match(r,u):
            u['cites'].add(r['cites']); u['src'].add(r['src']); u['oa']+= [x for x in r['oa'] if x not in u['oa']]; u['ctx']+=r['ctx']
            u['doi']=u['doi'] or r['doi']; u['arx']=u['arx'] or r['arx']; break
    else:
        uni.append(dict(r,cites={r['cites']},src={r['src']}))
for i,u in enumerate(uni):
    u['id']='C%02d'%(i+1); u['cites']=sorted(u['cites']); u['src']=sorted(u['src'])
json.dump(uni,open(D+'merged.json','w',encoding='utf8'),ensure_ascii=False,indent=1,default=list)
print(len(recs),len(uni))
for u in uni: print(u['id'],'+'.join(u['cites']),'/'.join(u['src']),u['year'],(u['title'] or '')[:70],'|',u['doi'] or u['arx'],'|',len(u['oa']),len(u['ctx']))
