import re,sys,glob,os
sys.stdout.reconfigure(encoding='utf-8')
D='search-log/downloads/txt/'
res=r'(?:stack ?overflow|search engine|googl\w*|web search|documentation|online resource\w*|external (?:resource|source|help|knowledge)\w*|help|assistance|ChatGPT|copilot)'
neg=r'(?:rarely|seldom|infrequent\w*|few (?:participants|developers|sessions|episodes|tasks)|did not (?:use|need|consult|seek|search|rely)|never (?:used|consulted|sought|searched)|without|no need|not need\w*|didn.t need|unaided|independent\w*|on their own|by themselves|alone)'
pat=re.compile(r'(?:%s.{0,120}%s|%s.{0,120}%s)'%(res,neg,neg,res),re.I)
ids=sys.argv[1:] or sorted(os.path.basename(f)[:-4] for f in glob.glob(D+'*.txt'))
for i in ids:
    t=re.sub(r'\s+',' ',open(D+i+'.txt',encoding='utf8',errors='ignore').read())
    hs=list(pat.finditer(t)); print('=====',i,len(hs)); last=-999
    for m in hs:
        if m.start()-last<400: continue
        last=m.start(); print('  -',m.group(0)[:300])
