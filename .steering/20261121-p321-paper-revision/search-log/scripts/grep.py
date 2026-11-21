import re,sys,glob,os
sys.stdout.reconfigure(encoding='utf-8')
D='search-log/downloads/txt/'
pat=re.compile(r'(consult\w*|seek(?:s|ing)? (?:for )?(?:help|assistance|information|resources)|help[- ]seeking|unaided|without (?:external |any )?(?:help|assistance|resources|consult\w*|looking up|searching)|(?:on|by) (?:their|his|her) own|resolved (?:on|by|without)|self[- ]resol\w*|self[- ]sufficien\w*|rarely (?:consult|search|use|look)\w*|external (?:resource|information|source|help)\w*|did not (?:consult|search|look up|use (?:any )?(?:external|online))\w*|no (?:external|online) (?:resource|search)\w*)',re.I)
ids=sys.argv[1:] or sorted(os.path.basename(f)[:-4] for f in glob.glob(D+'*.txt'))
for i in ids:
    t=re.sub(r'\s+',' ',open(D+i+'.txt',encoding='utf8',errors='ignore').read())
    hits=[m for m in pat.finditer(t)]
    print('=====',i,len(t),len(hits))
    last=-999
    for m in hits:
        if m.start()-last<300: continue
        last=m.start()
        print('  -',t[max(0,m.start()-120):m.end()+120])
