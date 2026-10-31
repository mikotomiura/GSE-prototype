import json,sys
# gse-replay --features の出力から停滞の始まりの行と provenance だけを残す（行ごとの特徴量は捨てる・repo に入れない）。
# usage: slim.py features.json out.json  -> onsets + provenance (no per-tick rows)
d=json.load(open(sys.argv[1]))
on=[{'s':r['stall_onset']['s_ms'],'t0':r['stall_onset']['t0_ms'],'theta':r['stall_onset']['theta_person_ms'],
     'n':r['stall_onset']['theta_sample_n'],'task_kind':r['stall_onset']['task_kind'],'ime_overlap':r['stall_onset']['ime_overlap'],
     'restart':r['restart']} for r in d['rows'] if r['stall_onset']['is_onset']]
p=d['provenance']
json.dump({'config':d['config'],'provenance':{k:p[k] for k in ('source_basename','source_sha256_prefix','session_start','hmm_version','app_version','o1_mode','capabilities','observed_intervals','idle_trim','input_gap_trim')},
           'n_rows':len(d['rows']),'onsets':on},open(sys.argv[2],'w'))
