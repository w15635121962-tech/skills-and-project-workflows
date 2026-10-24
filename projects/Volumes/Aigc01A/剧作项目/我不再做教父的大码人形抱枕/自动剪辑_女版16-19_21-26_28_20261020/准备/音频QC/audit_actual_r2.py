from pathlib import Path
import array, concurrent.futures, hashlib, json, math, os, subprocess, sys, wave

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ASR=BASE/'EP16-19_ASR'
SCRIPTS=Path('/Users/zc/.codex/skills/ffmpeg-skill/scripts')
ENV=dict(os.environ)
ENV['PATH']='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin'+os.pathsep+ENV.get('PATH','')

def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def run(name,args):
 p=subprocess.run([sys.executable,str(SCRIPTS/name),*map(str,args)],env=ENV,capture_output=True,text=True,timeout=180)
 if p.returncode:raise RuntimeError(p.stderr+'\n'+p.stdout)
 return json.loads(p.stdout)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

plans=[(p,json.loads(p.read_text())['episodes'][0]) for ep in [16,17,18,19] if (p:=BASE/f'EP{ep}_可执行r2.json').exists()]
sources=sorted({Path(a['source_path']) for p,e in plans for a in e['audio'] if a['track'] in [1,2]})
save(OUT/'实际r2_所有A1A2源_probe.json',run('probe.py',[*sources,'--json']))

def pcm(p):
 wav=OUT/(p.stem+'_source_decode.wav')
 if not wav.exists():
  save(OUT/(p.stem+'_decode_plan.json'),run('audio.py',[p,'-o',wav,'--dry-run','--json']))
  save(OUT/(p.stem+'_decode.json'),run('audio.py',[p,'-o',wav,'--json']))
 with wave.open(str(wav),'rb') as w:
  sr=w.getframerate();ch=w.getnchannels();width=w.getsampwidth();raw=w.readframes(w.getnframes())
 assert width==2
 a=array.array('h',raw)
 if sys.byteorder!='little':a.byteswap()
 return sr,ch,a

def peakwin(pcm,t,pre=.01,post=.01):
 sr,ch,a=pcm;n=len(a)//ch
 start=max(0,round((t-pre)*sr));end=min(n,round((t+post)*sr));v=a[start*ch:end*ch]
 pk=max(map(abs,v),default=0)/32768;rms=math.sqrt(sum(x*x for x in v)/max(1,len(v)))/32768
 return {'start':start/sr,'end':end/sr,'rms_dbfs':round(20*math.log10(max(rms,1e-12)),2),'peak_dbfs':round(20*math.log10(max(pk,1e-12)),2)}

pcmcache={p:pcm(p) for p in sources}
source_asr={p:json.loads((ASR/(p.stem+'.json')).read_text()) for p in sources}
assert all(digest(p)==source_asr[p]['source_sha256'] for p in sources)
results=[];measure=[]
for pp,e in plans:
 fps=e['fps'];aud=e['audio'];a1=[a for a in aud if a['track']==1];a2=[a for a in aud if a['track']==2]
 overlaps=[]
 for aa in a1:
  for bb in a2:
   lo=max(aa['record_frame'],bb['record_frame']);hi=min(aa['record_frame']+aa['duration_frames'],bb['record_frame']+bb['duration_frames'])
   if hi>lo:overlaps.append({'start_record_frame':lo,'end_record_frame_exclusive':hi,'duration_frames':hi-lo,'A1_source':aa['source_path'],'A2_source':bb['source_path']})
 edges=[]
 for j,a in enumerate(aud):
  if a['track'] not in [1,2]:continue
  p=Path(a['source_path']);start=a.get('source_in_seconds',a['source_start_frame']/fps);end=a.get('source_out_seconds_exclusive',a['source_end_frame_exclusive']/fps)
  words=[w for s in source_asr[p]['segments'] for w in s.get('words',[])]
  src=pcmcache[p]
  cross_start=[w for w in words if w['start']+1e-6<start<w['end']-1e-6];cross_end=[w for w in words if w['start']+1e-6<end<w['end']-1e-6]
  retained=[w for w in words if start-1e-6<=w['start'] and w['end']<=end+1e-6]
  rec={'plan_index':j,'track':a['track'],'source':str(p),'source_in_s':start,'source_out_exclusive_s':end,'record_frame':a['record_frame'],'duration_frames':a['duration_frames'],'speed_percent':a['speed_percent'],'gain_db_current':a.get('gain_db'),'ASR_words_crossing_in':cross_start,'ASR_words_crossing_out':cross_end,'first_fully_retained_word':retained[0] if retained else None,'last_fully_retained_word':retained[-1] if retained else None,'in_20ms_waveform':peakwin(src,start),'out_20ms_waveform':peakwin(src,end),'final_timeline_waveform_and_listening_checked':False}
  # The actual cut point is checked, not a universal padding rule. Two-frame centered
  # fades have half a timeline frame's source-time width on either side at native110.
  half=(1/fps)*a['speed_percent']/100
  rec['centered_2frame_source_half_width_s']=half
  rec['in_centered_2frame_window']=peakwin(src,start,half,half)
  rec['out_centered_2frame_window']=peakwin(src,end,half,half)
  edges.append(rec)
  if a['track']==1:measure.append((e['episode'],j,a,start,end))
 # Check union of A2 source ranges for every ASR word: a split must not silently discard it.
 coverage=[]
 for p in {Path(a['source_path']) for a in a2}:
  spans=[(a.get('source_in_seconds',a['source_start_frame']/fps),a.get('source_out_seconds_exclusive',a['source_end_frame_exclusive']/fps)) for a in a2 if Path(a['source_path'])==p]
  words=[w for s in source_asr[p]['segments'] for w in s.get('words',[])]
  missing=[w for w in words if not any(lo-1e-6<=w['start'] and w['end']<=hi+1e-6 for lo,hi in spans)]
  coverage.append({'source':str(p),'ranges':spans,'ASR_words_not_fully_contained_by_any_kept_range':missing,'source_sha_matches_ASR':True})
 results.append({'episode':e['episode'],'plan':str(pp),'plan_sha256':digest(pp),'A1_A2_record_overlap_count':len(overlaps),'A1_A2_record_overlaps':overlaps,'source_edge_checks':edges,'A2_word_coverage':coverage})

def a1measure(item):
 ep,j,a,start,end=item;p=Path(a['source_path']);wav=OUT/f'EP{ep}_A1_plan{j:02d}_{p.stem}_{start:.4f}-{end:.4f}.wav'
 if not wav.exists():
  save(wav.with_suffix('.cutplan.json'),run('cut.py',[p,'--start',start,'--end',end,'--accurate','-o',wav,'--dry-run','--json']))
  save(wav.with_suffix('.cut.json'),run('cut.py',[p,'--start',start,'--end',end,'--accurate','-o',wav,'--json']))
 d=run('loudness.py',[wav,'--measure-only','--json']);save(wav.with_suffix('.loudness.json'),d)
 m={k:float(v) for k,v in d['measured'].items()};gain=min(-18-m['input_i'],-1.5-m['input_tp']);gain=round(gain,2)
 return {'episode':ep,'plan_index':j,'source_path':str(p),'source_in_s':start,'source_out_exclusive_s':end,'record_frame':a['record_frame'],'duration_frames':a['duration_frames'],'gain_db_current':a.get('gain_db'),'label':a.get('label'),'integrated_lufs':m['input_i'],'true_peak_dbtp':m['input_tp'],'lra_lu':m['input_lra'],'suggested_native_AudioVolume_db':gain,'predicted_lufs':round(m['input_i']+gain,2),'predicted_true_peak':round(m['input_tp']+gain,2),'measurement_content':'entire retained synchronous source sound including any embedded music/ambience; not isolated dialogue','human_listening_verified':False}

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:measured=list(ex.map(a1measure,measure))
save(OUT/'实际r2_A1同期对白响度与增益建议.json',{'target_lufs':-18,'true_peak_ceiling_dbtp':-1.5,'native_property':'AudioVolume in dB','originals_modified':False,'records':measured})
save(OUT/'实际r2_A1A2范围与逐词波形复核.json',{'plans':results,'note':'offline source-word/waveform and planned record ranges only; no UI/Resolve mutation or listening verification'})
print(json.dumps({'episodes':[r['episode'] for r in results],'A1A2overlaps':[(r['episode'],r['A1_A2_record_overlap_count']) for r in results],'word_crossing_edges':[r for ep in results for r in ep['source_edge_checks'] if r['ASR_words_crossing_in'] or r['ASR_words_crossing_out']],'A2_missing_words':[r for ep in results for r in ep['A2_word_coverage'] if r['ASR_words_not_fully_contained_by_any_kept_range']],'A1_gains':measured},ensure_ascii=False,indent=2))
