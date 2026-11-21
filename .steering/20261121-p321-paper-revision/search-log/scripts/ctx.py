import re,sys
sys.stdout.reconfigure(encoding='utf-8')
i,pat,w=sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 500
t=re.sub(r'\s+',' ',open('search-log/downloads/txt/%s.txt'%i,encoding='utf8',errors='ignore').read())
for m in re.finditer(pat,t,re.I): print('>>',t[max(0,m.start()-w):m.end()+w],'\n')
