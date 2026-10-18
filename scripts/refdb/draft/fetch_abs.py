import json,urllib.request,urllib.parse,time,sys,os
S='/private/tmp/claude-501/-Users-johnd-GSE-prototype/f99bdc93-3f93-41b7-863c-4ad0bd1f8194/scratchpad/refdb'
d=json.load(open(S+'/data.json'))
out_p=S+'/abstracts.json'
out=json.load(open(out_p)) if os.path.exists(out_p) else {}
def get(url,hdr=None):
    req=urllib.request.Request(url,headers=hdr or {'User-Agent':'gse-refdb/0.1'})
    with urllib.request.urlopen(req,timeout=20) as r: return json.load(r)
def inv(ii):
    pos=[(p,w) for w,ps in ii.items() for p in ps]; return ' '.join(w for p,w in sorted(pos))
for k in [k for k in d['works'] if k in d['cite']]:
    if k in out: continue
    t,_,v=k.partition(':')
    if t=='arXiv': doi='10.48550/arXiv.'+v
    elif t=='doi': doi=v
    else: continue
    rec={'src':None,'abs':''}
    try:
        j=get('https://api.openalex.org/works/doi:'+urllib.parse.quote(doi,safe='/'))
        if j.get('abstract_inverted_index'): rec={'src':'openalex','abs':inv(j['abstract_inverted_index'])}
        rec['type']=j.get('type'); rec['title']=j.get('title')
    except Exception as e: rec['err_oa']=str(e)[:80]
    if not rec['abs']:
        try:
            j=get('https://api.semanticscholar.org/graph/v1/paper/DOI:'+urllib.parse.quote(doi,safe='/')+'?fields=abstract,tldr')
            if j.get('abstract'): rec.update(src='s2',abs=j['abstract'])
        except Exception as e: rec['err_s2']=str(e)[:80]
        time.sleep(1.1)
    if not rec['abs']:
        try:
            j=get('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='/'))['message']
            if j.get('abstract'): rec.update(src='crossref',abs=j['abstract'])
        except Exception as e: rec['err_cr']=str(e)[:80]
    out[k]=rec
    if len(out)%25==0: json.dump(out,open(out_p,'w'),ensure_ascii=False); print(len(out),flush=True)
    time.sleep(0.15)
json.dump(out,open(out_p,'w'),ensure_ascii=False)
import collections
print('done',len(out),collections.Counter(r['src'] for r in out.values()))
