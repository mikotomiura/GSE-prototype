import re,subprocess,json,collections
BR=['origin/main','origin/docs/tangibility-design','origin/docs/ai-fatigue-c-outline','origin/docs/ai-fatigue-core1-item-analysis','origin/docs/ai-fatigue-core2-discriminant','origin/docs/ai-fatigue-motivation-claims']
def sh(*a): return subprocess.run(['git',*a],capture_output=True,text=True).stdout
works={}  # key -> dict
idmap={}  # (branch,id)->key
for b in BR:
    for l in sh('show',f'{b}:docs/references.md').split('\n'):
        m=re.match(r'^\| \[([PV]\d+)\] \| (.*)$',l)
        if not m: continue
        c=[x.strip() for x in l.strip().strip('|').split(' | ')]
        if len(c)<7: print('SKIP',b,l[:80]); continue
        if len(c)==7: i,key,at,src,url,note,dup,st=c[0].strip('[]'),c[1],c[2],c[3],c[4],c[5],'—',c[6]
        else: i,key,at,src,url,note,dup,st=c[0].strip('[]'),c[1],c[2],c[3],c[4],' | '.join(c[5:-2]),c[-2],c[-1]
        idmap[(b,i)]=key
        w=works.setdefault(key,{'key':key,'ids':collections.OrderedDict(),'at':at,'src':src,'url':url,'note':note,'st':st,'branches':[]})
        w['ids'].setdefault(i,[]).append(b)
        if b not in w['branches']: w['branches'].append(b)
        if b=='origin/main' or len(note)>len(w['note']): pass
cite=collections.defaultdict(set)  # key -> card files
other=collections.defaultdict(set)
for b in BR:
    files=sh('ls-tree','-r','--name-only',b,'--','docs','experiments').split()
    for f in files:
        if not f.endswith('.md') or f=='docs/references.md': continue
        txt=sh('show',f'{b}:{f}')
        for i in set(re.findall(r'\[([PV]\d+)\]',txt)):
            k=idmap.get((b,i))
            if not k: continue
            if f.startswith('docs/literature/') and not f.endswith('_index.md'): cite[k].add(f.split('/')[-1])
            else: other[k].add(f)
json.dump({'works':works,'cite':{k:sorted(v) for k,v in cite.items()},'other':{k:sorted(v) for k,v in other.items()}},open('/private/tmp/claude-501/-Users-johnd-GSE-prototype/f99bdc93-3f93-41b7-863c-4ad0bd1f8194/scratchpad/refdb/data.json','w'),ensure_ascii=False)
print('works',len(works),'card-cited',len(cite),'only-other',len([k for k in works if k not in cite and k in other]),'uncited',len([k for k in works if k not in cite and k not in other]))
