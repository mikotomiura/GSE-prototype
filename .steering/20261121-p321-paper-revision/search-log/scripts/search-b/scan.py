import re, glob, os, sys
sys.stdout.reconfigure(encoding="utf-8")
D = r"C:\Users\johnd\AppData\Local\Temp\claude\bb8fe8b6e5b059fc\1def8c19-70cb-4b34-bdf8-1327407094d2\scratchpad\searchB\downloads"
pat = re.compile(r"consult\w*|help[- ]seek\w*|seek\w*\s+(?:for\s+)?help|unaided|without\s+(?:any\s+|external\s+)?(?:help|assistance|support)|on\s+their\s+own|external\s+(?:resources?|help)|self[- ]resolv\w*|resolved\s+without|independently|without\s+(?:asking|searching)", re.I)
for p in sorted(glob.glob(D + r"\K*.txt")):
    k = os.path.basename(p)[:-4]
    lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
    hits = [i for i, l in enumerate(lines) if pat.search(l)]
    print(f"##### {k} lines={len(lines)} hits={len(hits)}")
    last = -10
    for i in hits:
        if i - last < 3:
            continue
        last = i
        ctx = " ".join(x.strip() for x in lines[max(0, i - 1):i + 2])
        c2 = re.sub(r"\s+", " ", ctx)[:330]
        print(str(i + 1) + ": " + c2)
