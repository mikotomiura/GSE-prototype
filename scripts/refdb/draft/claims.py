import re,subprocess,json,collections
S='/private/tmp/claude-501/-Users-johnd-GSE-prototype/f99bdc93-3f93-41b7-863c-4ad0bd1f8194/scratchpad/refdb'
BR=['origin/main','origin/docs/tangibility-design','origin/docs/ai-fatigue-c-outline','origin/docs/ai-fatigue-core1-item-analysis','origin/docs/ai-fatigue-core2-discriminant','origin/docs/ai-fatigue-motivation-claims']
def sh(*a): return subprocess.run(['git',*a],capture_output=True,text=True).stdout
idmap={}
for b in BR:
    for l in sh('show',f'{b}:docs/references.md').split('\n'):
        m=re.match(r'^\| \[([PV]\d+)\] \| ([^|]*) \|',l)
        if m: idmap[(b,m.group(1))]=m.group(2).strip()
TEMP=re.compile(r'(確定|PLAUSIBLE BUT UNPROVEN|判定不能|否決|confirmed|refuted|3-0|2-1|1-2|0-3)')
def clean(s):
    s=re.sub(r'[★⚠️]+','',s); s=s.replace('**','').replace('`','')
    return re.sub(r'\s+',' ',s).strip()
out=collections.defaultdict(dict)  # key -> {(card,text):temp}
for b in BR:
    for f in sh('ls-tree','--name-only',b,'docs/literature/').split():
        fn=f.split('/')[-1]
        if fn.startswith('_') or 'template' in fn: continue
        for l in sh('show',f'{b}:{f}').split('\n'):
            if not (l.startswith('|') or l.startswith('### ')): continue
            ids=set(re.findall(r'\[([PV]\d+)\]',l))
            if not ids: continue
            if l.startswith('|'):
                cells=[c.strip() for c in l.strip().strip('|').split('|')]
                if all(set(c)<=set('-: ') for c in cells): continue
                # claim text = the longest cell
                txt=max(cells,key=len)
            else:
                txt=re.sub(r'^### ','',l)
            t=TEMP.findall(l)
            temp=t[-1] if t else ''
            txt=clean(re.sub(r'\[[PV]\d+\]','',txt))[:220]
            for i in ids:
                k=idmap.get((b,i))
                if k: out[k][(fn[:8],txt)]=temp
res={k:[{'d':c,'t':t,'temp':tp} for (c,t),tp in v.items()] for k,v in out.items()}
json.dump(res,open(S+'/claims.json','w'),ensure_ascii=False)
n=sum(len(v) for v in res.values())
print('文献',len(res),'主張の行',n, collections.Counter(x['temp'] for v in res.values() for x in v).most_common(12))
