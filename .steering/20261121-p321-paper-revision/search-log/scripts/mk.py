import json,os,sys
D='search-log/downloads/'
uni=json.load(open(D+'merged.json',encoding='utf8'))
dl=dict((a,b) for a,b,c in json.load(open(D+'dl.json')))
near={
'C04':'NEAR: reports low rate of consulting external resources but draws no inference about need for help. Verbatim: "Time spent checking external resources was limited (<5%), compared to a previously reported median of 15% for information seeking on the web [81]."',
'C29':'NEAR: low consult share read as not a time bottleneck, not as low need for help. Verbatim: "consult (2.3% of total time) were not major bottlenecks when debugging."',
}
for u in uni:
    i=u['id']; t=u['title'].replace('\t',' ').replace('\n',' ')
    url=dl.get(i) or ''
    if i in near: st,note=near[i][:4],near[i]
    elif url: st,note='NONE','Full text keyword-scanned (consult/help-seeking/unaided/without help/on their own/external resources); no passage meeting criterion.'
    else:
        st='NOT-READ'; note='No free full text found (OpenAlex/S2/arXiv title search; publisher PDFs not fetched). Judged on %d S2 context(s)/abstract: nothing relevant.'%len(u['ctx'])
    u.update(status=st,note=note,url=url)
rows=['\t'.join(['id','cites','title','year','doi_or_arxiv','sources','fulltext_url_read','status','note'])]
for u in uni:
    rows.append('\t'.join([u['id'],'+'.join(u['cites']) if len(u['cites'])<2 else 'both',u['title'].replace('\t',' ').replace('\n',' '),str(u['year'] or ''),u['doi'] or u['arx'],'/'.join(u['src']),u['url'],u['status'],u['note'].replace('\n',' ')]))
open('search-log/citing-works.tsv','w',encoding='utf8',newline='\n').write('\n'.join(rows)+'\n')
from collections import Counter
print(Counter(u['status'] for u in uni),len(uni),Counter(len(u['cites']) for u in uni),Counter('+'.join(u['cites']) for u in uni))
