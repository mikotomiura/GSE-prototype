import os, re, sys
root = sys.argv[1]
pat_abs = re.compile(rb'[A-Za-z]:[\/][A-Za-z0-9_.\/ -]{3,}')
pat_user = re.compile(rb'johnd', re.I)
hits_abs, hits_user = [], []
for dp, dn, fn in os.walk(root):
    for n in fn:
        p = os.path.join(dp, n)
        d = open(p,'rb').read().replace(b'\x00', b'')
        for m in pat_abs.findall(d):
            hits_abs.append((p, m[:90]))
        if pat_user.search(d):
            hits_user.append(p)
print("root:", root)
print("絶対パスらしき出現:", len(hits_abs))
for p, m in hits_abs[:15]:
    print("   ", p, "->", m)
print("ユーザー名 johnd:", len(hits_user))
for p in hits_user[:10]:
    print("   ", p)
