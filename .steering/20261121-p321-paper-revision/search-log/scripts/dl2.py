import json,subprocess,os,re,urllib.parse,time
D='search-log/downloads/'
uni={u['id']:u for u in json.load(open(D+'merged.json',encoding='utf8'))}
res=dict((a,b) for a,b,c in json.load(open(D+'dl.json')))
def getpdf(out,url):
    subprocess.run(['curl','-sL','--max-time','60','-o',out,url],timeout=90)
    try: ok=open(out,'rb').read(5)==b'%PDF-'
    except: ok=False
    if not ok and os.path.exists(out): os.remove(out)
    return ok
def norm(t): return re.sub(r'[^a-z0-9]','',t.lower())
for i,u in uni.items():
    if res[i]: continue
    out=D+'pdf/%s.pdf'%i
    # retry listed
    for url in u['oa']:
        if url and getpdf(out,url): res[i]=url;break
    if res[i]: continue
    t=u['title'] or ''
    if not t or 'ï¿' in t or len(t)<10: continue
    q=urllib.parse.quote('ti:"%s"'%re.sub(r'[^\w\s]',' ',t))
    r=subprocess.run(['curl','-s','--max-time','30','http://export.arxiv.org/api/query?search_query='+q+'&max_results=2'],capture_output=True,text=True,encoding='utf8')
    for m in re.finditer(r'<entry>.*?<id>http://arxiv.org/abs/([^<]+?)(v\d+)?</id>.*?<title>(.*?)</title>',r.stdout,re.S):
        if norm(m.group(3))==norm(t):
            if getpdf(out,'https://arxiv.org/pdf/'+m.group(1)): res[i]='https://arxiv.org/pdf/'+m.group(1)
            break
    time.sleep(3)
    print(i,res[i])
json.dump([(a,b,'') for a,b in res.items()],open(D+'dl.json','w'))
