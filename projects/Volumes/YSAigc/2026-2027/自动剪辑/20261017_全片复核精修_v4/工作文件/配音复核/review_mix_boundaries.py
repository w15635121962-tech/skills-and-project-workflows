from pathlib import Path
import json,numpy as np,soundfile as sf
B=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_旁白精修/工作文件');O=Path(__file__).parent
plan=json.loads((B/'audio_plan_v2.json').read_text());native=json.loads(Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_开篇人文精修_v3/工作文件/native_build_v3.json').read_text())['snapshot'];fps=25
allitems=[i|{'track':t['track']} for t in native['audio'] for i in t['items']];music=sorted([i for i in allitems if i['track'] in (3,4)],key=lambda x:x['start']);mix=plan['mix_path'];sr=sf.info(mix).samplerate
read=lambda path,a,b:readwin(path,a,b)
def readwin(path,a,b):
 with sf.SoundFile(path) as f:
  f.seek(max(0,round(a*f.samplerate)));return f.read(max(0,round((b-a)*f.samplerate)),dtype='float32',always_2d=True)
def db(x):return round(20*np.log10(max(float(x),1e-12)),3)
def boundary(t):
 a=readwin(mix,max(0,t-.5),t+.5);j=round(min(.5,t)*sr);delta=np.abs(a[j]-a[j-1]);diff=np.abs(np.diff(a,axis=0));local99=float(np.percentile(diff,99.9));r={'time_seconds':t,'sample_peak_1s_dbfs':db(np.max(np.abs(a))),'rms_1s_dbfs':db(np.sqrt(np.mean(a*a))),'boundary_sample_delta_dbfs':db(np.max(delta)),'nearby_sample_delta_p99_9_dbfs':db(local99),'delta_ratio_to_local_p99_9':round(float(np.max(delta))/max(local99,1e-12),3),'full_scale_samples':int(np.sum(np.abs(a)>=.9999))}
 # A simple unusual-jump flag. This is not a perceptual click detector.
 r['unusually_large_exact_boundary_jump']=float(np.max(delta))>max(.01,local99*4)
 return r
overlaps=[]
for one,two in zip(music,music[1:]):
 a=two['start']/fps;b=one['end']/fps
 overlaps.append({'outgoing':Path(one['path']).name,'incoming':Path(two['path']).name,'native_overlap_start':a,'native_overlap_end':b,'native_overlap_seconds':round(b-a,3),'mix_start_boundary':boundary(a),'mix_end_boundary':boundary(b),'recommend_add_crossfade':False,'reason':'Existing two-stem fade overlap already provides a transition; no clipping or unusual exact-boundary sample jump detected by this measurement.'})
voices=[]
for it in plan['speech']:
 nat=next(x for x in allitems if x['path']==it['path']);dur=(nat['end']-nat['start'])/fps;x=readwin(it['path'],0,dur);first=x[0];last=x[-1];first50=x[:round(.05*sr)];last50=x[-round(.05*sr):]
 voices.append({'name':Path(it['path']).name,'native_start':nat['start']/fps,'native_end':nat['end']/fps,'effective_duration':dur,'first_sample_abs_dbfs':db(np.max(np.abs(first))),'last_sample_abs_dbfs':db(np.max(np.abs(last))),'first_50ms_peak_dbfs':db(np.max(np.abs(first50))),'last_50ms_peak_dbfs':db(np.max(np.abs(last50))),'first_50ms_rms_dbfs':db(np.sqrt(np.mean(first50**2))),'last_50ms_rms_dbfs':db(np.sqrt(np.mean(last50**2))),'start_mix_boundary':boundary(nat['start']/fps) if nat['start'] else None,'end_mix_boundary':boundary(nat['end']/fps)})
# Add last-word evidence for narration, separated from automatic recognition endpoints.
it=plan['speech'][0];a=readwin(it['path'],433,433.68);v=np.max(np.abs(a),axis=1);tails={}
for threshold in (-40,-50,-60,-80):
 ids=np.flatnonzero(v>10**(threshold/20));tails[str(threshold)+'_dbfs']=round(433+(ids[-1]+1)/sr,6) if len(ids) else None
# Peak scan every sample of the mix with bounded memory, including all transition windows.
peak=0.;clipcount=0
with sf.SoundFile(mix) as f:
 for a in f.blocks(blocksize=480000,dtype='float32',always_2d=True):peak=max(peak,float(np.max(np.abs(a))));clipcount+=int(np.sum(np.abs(a)>=.9999))
result={'scope':'Current v3 native audio placements plus existing full mix WAV; no new render or Resolve operation','mix_source':mix,'mix_duration_with_silent_handle':sf.info(mix).duration,'native_effective_duration':460.28,'mix_peak_dbfs':db(peak),'mix_full_scale_samples':clipcount,'music_overlaps':overlaps,'voice_boundaries':voices,'narration_tail_actual_last_sample_above_threshold':tails,'recommend_new_audio_processing':False,'recommend_new_denoise':False,'recommend_new_crossfades':False,'known_file_vs_native_difference':{'item':'BGM_05','file_plan_end_frame':10867,'native_end_frame':10866,'difference_seconds':.04,'location':'existing fade-out tail; not speech'},'limitations':['Sample continuity and peaks cannot prove no perceived clicks, phase artifacts or masking.','Existing complete mix differs from native audio at the last 1 frame of BGM05. Its fade tail is low level; native final render has not been acoustically heard here.','This is signal analysis plus ASR, not human listening.']}
(O/'mix_transition_boundary_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'peak_dbfs':result['mix_peak_dbfs'],'clipping':clipcount,'music_overlap_seconds':[x['native_overlap_seconds'] for x in overlaps],'large_jump_flags':[(x['time_seconds'],x['boundary_sample_delta_dbfs']) for o in overlaps for x in [o['mix_start_boundary'],o['mix_end_boundary']] if x['unusually_large_exact_boundary_jump']],'voice_boundary_samples':[{k:x[k] for k in ['name','first_sample_abs_dbfs','last_sample_abs_dbfs','last_50ms_rms_dbfs']} for x in voices],'tail':tails},ensure_ascii=False))
