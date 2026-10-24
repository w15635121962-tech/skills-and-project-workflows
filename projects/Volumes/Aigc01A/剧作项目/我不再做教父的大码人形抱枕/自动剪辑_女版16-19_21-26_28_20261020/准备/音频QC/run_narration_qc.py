from pathlib import Path
import array, concurrent.futures, csv, hashlib, json, math, os, subprocess, sys, wave

ROOT=Path.cwd()
OUT=Path(__file__).resolve().parent
SCRIPTS=Path('/Users/zc/.codex/skills/ffmpeg-skill/scripts')
ASR=OUT.parent/'EP16-19_ASR'
ENV=dict(os.environ)
ENV['PATH']='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin'+os.pathsep+ENV.get('PATH','')
FILES=sorted(p for ep in (16,17,18,19) for p in (ROOT/'对标音色旁白制作_20261020/音频'/f'第{ep}集').glob('*.mp3'))

def save(p,d):
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def run(name,args):
    p=subprocess.run([sys.executable,str(SCRIPTS/name),*map(str,args)],env=ENV,capture_output=True,text=True,timeout=180)
    if p.returncode: raise RuntimeError(p.stderr+'\n'+p.stdout)
    return json.loads(p.stdout)

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def measure(p):
    h=digest(p)
    d=run('loudness.py',[p,'--measure-only','--json'])
    save(OUT/(p.stem+'_loudness.json'),d)
    m={k:float(v) for k,v in d['measured'].items()}
    desired=-18-m['input_i'];peak_safe=-1.5-m['input_tp']
    gain=round(min(desired,peak_safe),2)
    return {'source':str(p),'sha256':h,'integrated_lufs':m['input_i'],'true_peak_dbtp':m['input_tp'],'lra_lu':m['input_lra'],'suggested_native_AudioVolume_db':gain,'predicted_lufs_at_constant_gain':round(m['input_i']+gain,2),'predicted_tp_at_constant_gain':round(m['input_tp']+gain,2),'loudness_target_limited_by_peak':peak_safe<desired,'source_unchanged':h==digest(p),'measurement_scope':'full unretimed original file; Resolve 110% retime and assembled mix require remeasurement','human_listening_verified':False}

probe=run('probe.py',[*FILES,'--json'])
save(OUT/'29条原始文件_probe.json',probe)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    rows=list(ex.map(measure,FILES))
save(OUT/'29条新旁白响度与原生增益建议.json',{'target_lufs':-18,'true_peak_ceiling_dbtp':-1.5,'method':'skill loudness.py measure-only; suggested gain=min(-18-I,-1.5-TP); no compression/gating/normalization written','originals_modified':False,'records':rows})
with (OUT/'29条原生增益建议.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

cuts={'16-01':[2.60],'16-02':[2.95],'16-03':[5.70],'16-04':[3.50],'16-05':[8.20],'17-08':[5.05,5.083333333333333,6.50],'19-03':[4.02],'18-06':[1.70,11.10,11.18],'18-07':[5.60],'17-03':[2.50],'17-05':[6.00],'18-02':[7.70],'18-04':[3.50],'19-07':[6.30,6.333333333333333]}
evidence=[]
for key,ts in cuts.items():
    p=next(p for p in FILES if key+'-01' in p.stem)
    wav=OUT/(p.stem+'_source_decode.wav')
    if not wav.exists():
        plan=run('audio.py',[p,'-o',wav,'--dry-run','--json']);save(OUT/(p.stem+'_decode_plan.json'),plan)
        d=run('audio.py',[p,'-o',wav,'--json']);save(OUT/(p.stem+'_decode.json'),d)
    with wave.open(str(wav),'rb') as w:
        sr=w.getframerate();ch=w.getnchannels();width=w.getsampwidth();raw=w.readframes(w.getnframes())
    if width!=2:raise RuntimeError(f'Need PCM16, got {width}')
    pcm=array.array('h',raw)
    if sys.byteorder!='little':pcm.byteswap()
    # Extraction has no processing. Original source clock is preserved; output duration is probed by audio.py.
    bins=[]
    step=round(sr*.01)
    for n in range(0,len(pcm)//ch,step):
        vals=pcm[n*ch:min((n+step)*ch,len(pcm))]
        rms=math.sqrt(sum(v*v for v in vals)/max(1,len(vals)))/32768
        peak=max(map(abs,vals),default=0)/32768
        bins.append({'start_s':n/sr,'end_s':min(n+step,len(pcm)//ch)/sr,'rms_dbfs':round(20*math.log10(max(rms,1e-12)),2),'peak_dbfs':round(20*math.log10(max(peak,1e-12)),2)})
    rec=json.loads((ASR/(p.stem+'.json')).read_text())
    assert rec['source_sha256']==digest(p), f'ASR source changed: {p}'
    words=[w for s in rec['segments'] for w in s.get('words',[])]
    save(OUT/(p.stem+'_waveform_10ms.json'),{'source':str(p),'decoded_wav':str(wav),'sample_rate':sr,'channels':ch,'timing':'original source seconds; no speed transform','words':words,'bins':bins})
    for t in ts:
        left=max((w for w in words if w['end']<=t),key=lambda w:w['end'],default=None)
        right=min((w for w in words if w['start']>=t),key=lambda w:w['start'],default=None)
        overlap=[w for w in words if w['start']<t<w['end']]
        window=[b for b in bins if t-.3<=b['start_s']<=t+.3]
        idx=next(i for i,b in enumerate(bins) if b['start_s']<=t<b['end_s'])
        # This amplitude interval is evidence, not a declaration that low-energy speech is absent.
        lo=hi=idx
        while lo>0 and bins[lo-1]['peak_dbfs']<=-45:lo-=1
        while hi+1<len(bins) and bins[hi+1]['peak_dbfs']<=-45:hi+=1
        evidence.append({'source':str(p),'candidate_cut_s':t,'candidate_at_24fps_frame':round(t*24),'candidate_at_24fps_s':round(t*24)/24,'outgoing_word':left,'incoming_word':right,'asr_word_overlap':overlap,'at_cut_10ms':bins[idx],'contiguous_low_amplitude_interval_at_minus45_peak':{'start_s':bins[lo]['start_s'],'end_s':bins[hi]['end_s'],'at_cut_below_threshold':bins[idx]['peak_dbfs']<=-45},'local_600ms_waveform':window,'human_listening_verified':False,'status':'source-word and waveform evidence only; audition final native110 cut/fades before claiming pass'})
save(OUT/'候选拆句边界_ASR与波形共同证据.json',{'cuts':evidence,'source_clock':'unretimed original MP3 decoded via skill audio.py, 10ms RMS and peak; ASR words same source hash','fixed_padding_used':False,'human_listening_verified':False,'final_timeline_110_waveform_verified':False})
print(json.dumps({'files':len(rows),'integrated_lufs_range':[min(x['integrated_lufs'] for x in rows),max(x['integrated_lufs'] for x in rows)],'gain_db_range':[min(x['suggested_native_AudioVolume_db'] for x in rows),max(x['suggested_native_AudioVolume_db'] for x in rows)],'cuts':[{k:d[k] for k in ['source','candidate_cut_s','outgoing_word','incoming_word','asr_word_overlap','at_cut_10ms','contiguous_low_amplitude_interval_at_minus45_peak']} for d in evidence]},ensure_ascii=False,indent=2))
