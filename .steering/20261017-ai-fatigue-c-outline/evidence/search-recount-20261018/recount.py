# Recount of the TRACE search proposal (OpenAlex), 2026-10-18. Run with: uv run --with openpyxl python -I recount.py XLSX RECORDS264
import json, sys, time, urllib.parse, urllib.request, openpyxl
F='(fatigue OR exhaustion OR exhausted OR burnout OR "burn-out" OR depletion OR depleted OR tiredness OR weariness)'
A='("artificial intelligence" OR "generative AI" OR GenAI OR ChatGPT OR "large language model" OR "large language models" OR LLM OR chatbot OR "AI tool" OR "AI tools" OR "AI assistant" OR "AI-assisted" OR "AI use")'
A2='("generative AI" OR GenAI OR ChatGPT OR "large language model" OR "large language models" OR LLM OR chatbot OR "AI assistant" OR "AI tools")'
X=' NOT ("fatigue life" OR "fatigue crack" OR "fatigue strength" OR "fatigue damage" OR "driver fatigue" OR "driver drowsiness" OR "fatigue detection" OR "muscle fatigue" OR "battery" OR "alloy" OR "welded")'
P='(survey OR questionnaire OR scale OR participants OR respondents OR interview OR interviews OR "self-report" OR students OR employees OR users)'
Q={'Q1':F+' AND '+A,'Q6':F+' AND '+A+X,'Q7':F+' AND '+A+' AND '+P+X,'Q8':F+' AND '+A2+' AND '+P+X,
   'Q4':'("AI fatigue" OR "AI-induced fatigue" OR "AI-related fatigue" OR "GenAI fatigue" OR "ChatGPT fatigue" OR "AI exhaustion" OR "AI burnout")'}
T=',type:article|review|preprint'
def count(f):
    u='https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':f,'per-page':1,'mailto':'trace-recount@example.org'})
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(u,timeout=60))['meta']['count']
        except Exception as e: err=str(e)[:60]; time.sleep(5)
    return 'ERR '+err
def doi_in(dois,q=None,date=None,typ=True):
    n=0
    for i in range(0,len(dois),40):
        f='doi:'+'|'.join('https://doi.org/'+d for d in dois[i:i+40])
        if q: f+=',title_and_abstract.search:'+q
        if date: f+=',from_publication_date:'+date
        if typ: f+=T
        c=count(f); time.sleep(1)
        if isinstance(c,str): return c
        n+=c
    return n
wb=openpyxl.load_workbook(sys.argv[1],read_only=True)
doi={r[0]:str(r[7]).strip().lower() for r in wb['文献DB'].iter_rows(min_row=5,values_only=True) if r[0] and str(r[0]).startswith('AF') and r[7]}
final={r[0]:r[5] for r in wb['スクリーニング'].iter_rows(min_row=5,values_only=True) if r[0] and str(r[0]).startswith('AF')}
inc=[a for a,v in final.items() if v=='含める']
print('included',len(inc),inc); print('DOI missing among included:',[a for a in inc if a not in doi])
rec=json.load(open(sys.argv[2])); d264=sorted({r['doi'].strip().lower() for r in rec if r.get('doi')})
d34=sorted(set(doi.values()))
print('264 with DOI:',len(d264),' 34 with DOI:',len(d34))
dates=['2022-11-30','2024-01-01','2025-01-01']
print('\n== counts (title_and_abstract, type article|review|preprint) ==')
for k,q in Q.items():
    row=[k]
    for dt in dates:
        row.append(f'{dt}:{count("title_and_abstract.search:"+q+",from_publication_date:"+dt+T)}'); time.sleep(1)
    print(' '.join(map(str,row)))
print('\n== recall of the 11 included (per record, no date) ==')
for a in inc:
    d=doi.get(a); row=[a,d]
    for k in ['Q6','Q7']:
        row.append(f'{k}={doi_in([d],Q[k],typ=False)}')
    row.append(f'inOA={doi_in([d],typ=False)}')
    print(' '.join(map(str,row)))
print('\n== overlap with the source DB (by DOI) ==')
for name,ds in [('264',d264),('34',d34)]:
    print(name,'inOA(any type)=',doi_in(ds,typ=False),' inOA(type ok, from 2022-11-30)=',doi_in(ds,date='2022-11-30'))
    for k in ['Q6','Q7']:
        print('  ',k,' '.join(f'{dt}:{doi_in(ds,Q[k],dt)}' for dt in dates))
