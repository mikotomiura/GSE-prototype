import json,urllib.request,urllib.parse,time,os,re
S='/private/tmp/claude-501/-Users-johnd-GSE-prototype/f99bdc93-3f93-41b7-863c-4ad0bd1f8194/scratchpad/refdb'
d=json.load(open(S+'/data.json'))
p=S+'/csl_raw.json'; out=json.load(open(p)) if os.path.exists(p) else {}
for k in d['works']:
    if k in out: continue
    t,_,v=k.partition(':')
    doi = v if t=='doi' else ('10.48550/arXiv.'+v if t=='arXiv' else None)
    if not doi: continue
    try:
        req=urllib.request.Request('https://doi.org/'+urllib.parse.quote(doi,safe='/'),headers={'Accept':'application/vnd.citationstyles.csl+json','User-Agent':'gse-refdb/0.1'})
        with urllib.request.urlopen(req,timeout=25) as r: out[k]=json.load(r)
    except Exception as e: out[k]={'_err':str(e)[:80]}
    if len(out)%50==0: json.dump(out,open(p,'w'),ensure_ascii=False); print(len(out),flush=True)
    time.sleep(0.2)
json.dump(out,open(p,'w'),ensure_ascii=False)
print('done',len(out),sum('_err' in x for x in out.values()))
