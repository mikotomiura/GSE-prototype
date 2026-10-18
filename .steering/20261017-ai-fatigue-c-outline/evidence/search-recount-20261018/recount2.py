import json,sys,time
exec(open('recount.py').read().split("wb=openpyxl")[0].replace("time.sleep(1)","time.sleep(2.5)"))
import openpyxl
wb=openpyxl.load_workbook(sys.argv[1],read_only=True)
doi={r[0]:str(r[7]).strip().lower() for r in wb['文献DB'].iter_rows(min_row=5,values_only=True) if r[0] and str(r[0]).startswith('AF') and r[7]}
inc=['AF001','AF002','AF004','AF005','AF006','AF007','AF008','AF010','AF011','AF012','AF019']
rec=json.load(open(sys.argv[2])); d264=sorted({r['doi'].strip().lower() for r in rec if r.get('doi')})
di=[doi[a] for a in inc]
print('11 included, type ok from 2022-11-30:',doi_in(di,date='2022-11-30'),' Q6:',doi_in(di,Q['Q6'],'2022-11-30'),' Q7:',doi_in(di,Q['Q7'],'2022-11-30'))
print('11 included, type ok from 2024-01-01:',doi_in(di,date='2024-01-01'),' Q7:',doi_in(di,Q['Q7'],'2024-01-01'))
for k in ['Q6','Q7']:
    print('264',k,' '.join(f'{dt}:{doi_in(d264,Q[k],dt)}' for dt in ['2022-11-30','2024-01-01']))
