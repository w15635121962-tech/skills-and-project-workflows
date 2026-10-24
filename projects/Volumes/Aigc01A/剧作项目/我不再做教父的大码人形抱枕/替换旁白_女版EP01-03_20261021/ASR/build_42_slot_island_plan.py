from pathlib import Path
import datetime,hashlib,json,sys

ROOT=Path.cwd()
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'达芬奇剪辑_EP21-25_20261020/转录'))
import run_local_asr as b
import numpy as np
from mlx_whisper.audio import load_audio,SAMPLE_RATE

mapping=json.loads((BASE/'旧剪口到新旁白_逐词映射候选.json').read_text())
snapshot=json.loads((BASE/'替换前_完整时间线实读.json').read_text())
cache={}
for pair in mapping['pairs']:
 p=pair['new_source'];d=json.loads(Path(pair['new_ASR']).read_text());a=np.array(load_audio(p))
 assert b.digest(p)==pair['new_source_sha256']
 step=round(SAMPLE_RATE*.005);padded=np.pad(a,(0,(-len(a))%step));blocks=padded.reshape(-1,step)
 peak=20*np.log10(np.maximum(np.max(np.abs(blocks),axis=1),1e-12))
 rms=20*np.log10(np.maximum(np.sqrt(np.mean(blocks*blocks,axis=1)),1e-12))
 cache[p]={'record':d,'audio':a,'peak5ms':peak,'rms5ms':rms,'words':[w for s in d['segments'] for w in s['words']]}

def edge_wave(c,t,half=.015):
 a=c['audio'];lo=max(0,round((t-half)*SAMPLE_RATE));hi=min(len(a),round((t+half)*SAMPLE_RATE));v=a[lo:hi]
 if len(v)==0:return {'window_start':lo/SAMPLE_RATE,'window_end':hi/SAMPLE_RATE,'peak_dbfs':-240,'rms_dbfs':-240}
 return {'window_start':lo/SAMPLE_RATE,'window_end':hi/SAMPLE_RATE,'peak_dbfs':round(float(20*np.log10(max(np.max(np.abs(v)),1e-12))),2),'rms_dbfs':round(float(20*np.log10(max(np.sqrt(np.mean(v*v)),1e-12))),2)}

islands=[];slices=[]
for e in snapshot['timelines']:
 ep=e['ep'];fps=e['fps'];cs=sorted([c for c in mapping['clips'] if c['episode']==ep],key=lambda c:c['record_start_frame']);groups=[]
 for c in cs:
  if groups and groups[-1][-1]['new_source']==c['new_source'] and groups[-1][-1]['record_end_frame_exclusive']==c['record_start_frame']:groups[-1].append(c)
  else:groups.append([c])
 for k,g in enumerate(groups,1):
  ident=f'EP{ep:02d}_island{k:02d}';source=g[0]['new_source'];c=cache[source];d=c['record'];allw=c['words'];words=[];seen=set()
  for item in g:
   for w in item['new_complete_words']:
    key=(w['start'],w['end'],w['word'])
    if key not in seen:words.append(w);seen.add(key)
  words.sort(key=lambda w:(w['start'],w['end']))
  first=next(i for i,w in enumerate(allw) if w==words[0]);last=next(i for i,w in enumerate(allw) if w==words[-1]);assert words==allw[first:last+1]
  full=first==0 and last==len(allw)-1
  # Whole-source contiguous islands stay whole, avoiding any ASR/phoneme cut.
  # Only real record-gap edges get a short buffer. Use ASR plus observed decay,
  # keep extra syllable tails, and retain an explicit listening limitation.
  ni=0 if first==0 else max(0,words[0]['start']-.020)
  head_repair=None
  if first>0 and edge_wave(c,ni)['peak_dbfs']>-45:
   lower=max(allw[first-1]['end'],words[0]['start']-.400)
   lo=max(0,int(lower/.005));hi=min(len(c['peak5ms'])-1,int(words[0]['start']/.005))
   quiet=[j for j in range(lo,hi) if max(c['peak5ms'][j:j+2])<=-60]
   if quiet:
    repaired=quiet[-1]*.005
    head_repair={'old_ASR_minus20ms_in':ni,'old_edge_peak_dbfs':edge_wave(c,ni)['peak_dbfs'],'repaired_in_at_two_low_peak_bins':repaired,'source_window_start':lower,'ASR_first_word_start':words[0]['start'],'note':'ASR boundary lies after actual sound onset; retreat to preceding observed quiet valley. Targeted listening still required.'}
    ni=repaired
  no=d['duration']
  tail_observation=None
  if last<len(allw)-1:
   next_start=allw[last+1]['start'];limit=min(d['duration'],next_start-.020,words[-1]['end']+.350)
   lo=max(0,int(words[-1]['end']/.005));hi=max(lo,int(limit/.005));indices=np.flatnonzero(c['peak5ms'][lo:hi]>-60)
   observed=max(words[-1]['end'],(lo+int(indices[-1])+1)*.005) if len(indices) else words[-1]['end']
   no=min(limit,observed+.020)
   tail_observation={'ASR_last_word_end':words[-1]['end'],'next_word_ASR_start':next_start,'observation_window_end':limit,'observed_last_minus60_peak_bin_end':observed,'buffer_after_observed_activity_ms':round(max(0,no-observed)*1000,3),'threshold_is_not_listening_proof':True}
  start=g[0]['record_start_frame'];end=g[-1]['record_end_frame_exclusive'];frames=end-start;seconds=frames/fps;scalar=(no-ni)/seconds
  original_items=[{'old_item_id':item['old_clip_id'],'clip_index_zero_based':item['clip_index_zero_based'],'record_start_frame':item['record_start_frame'],'record_end_frame_exclusive':item['record_end_frame_exclusive'],'record_duration_frames':item['record_duration_frames']} for item in g]
  island={'island_id':ident,'episode':ep,'fps':fps,'old_item_ids':[x['old_item_id'] for x in original_items],'original_items':original_items,'record_start_frame':start,'record_end_frame_exclusive':end,'record_duration_frames':frames,'record_duration_seconds':seconds,'new_source_path':source,'new_source_sha256':d['source_sha256'],'new_source_in_seconds':round(ni,6),'new_source_out_seconds_exclusive':round(no,6),'new_source_duration_seconds':round(no-ni,6),'uses_entire_new_source_file':full,'first_word_index_zero_based':first,'last_word_index_zero_based':last,'words':words,'complete_words_text':' '.join(w['word'].strip() for w in words),'tempo_needed':round(scalar,9),'tempo_percent':round(scalar*100,6),'output_sample_rate_hz':48000,'output_samples_exact':round(seconds*48000),'pitch_preserve_required':True,'head_boundary_repair':head_repair,'tail_waveform_observation':tail_observation,'head_waveform':edge_wave(c,ni),'tail_waveform':edge_wave(c,no),'audition_verified':False,'source_edge_status':'Whole-source island: no interior source trim' if full else 'ASR-word plus measured waveform candidate at true record-gap edge; targeted final audition required','internal_slice_policy':'Render this entire island once with pitch preserved and exact output length, then cut output at original record frame offsets. Never independently source-trim/fade internal slices.'}
  islands.append(island)
  for item in g:
   offset=item['record_start_frame']-start;dur=item['record_duration_frames'];est_in=ni+(offset/fps)*scalar;est_out=ni+((offset+dur)/fps)*scalar
   sl={'episode':ep,'clip_index_zero_based':item['clip_index_zero_based'],'old_item_id':item['old_clip_id'],'island_id':ident,'record_start_frame':item['record_start_frame'],'record_end_frame_exclusive':item['record_end_frame_exclusive'],'record_duration_frames':dur,'fps':fps,'new_source_path':source,'new_source_sha256':d['source_sha256'],'new_source_in_seconds':round(est_in,6),'new_source_out_seconds_exclusive':round(est_out,6),'new_source_in_seconds_estimate_only':round(est_in,6),'new_source_out_seconds_estimate_only':round(est_out,6),'island_new_source_in_seconds':island['new_source_in_seconds'],'island_new_source_out_seconds_exclusive':island['new_source_out_seconds_exclusive'],'tempo_needed':island['tempo_needed'],'tempo_percent':island['tempo_percent'],'output_island_slice_start_sample_48k':round(offset/fps*48000),'output_island_slice_end_sample_exclusive_48k':round((offset+dur)/fps*48000),'output_samples_exact':round(dur/fps*48000),'nominal_original_phrase_words':item['new_complete_words'],'tokens':[w['word'].strip() for w in item['new_complete_words']],'buffer_policy':'No per-slice buffers/fades inside continuous island; only island outer edges carry <=20ms suggested padding after measured activity.','do_not_independently_render_source_range':len(g)>1,'word_continuity_preserved_by_shared_island_output':True}
   slices.append(sl)

coverage=[]
for p,c in cache.items():
 related=[i for i in islands if i['new_source_path']==p];assigned=[(w['start'],w['end'],w['word']) for i in related for w in i['words']];expected=[(w['start'],w['end'],w['word']) for w in c['words']]
 assert assigned==expected,(p,'word coverage mismatch')
 for prev,nxt in zip(related,related[1:]):
  assert prev['new_source_out_seconds_exclusive']<=nxt['new_source_in_seconds'],(p,'overlapping source across true record gap')
 coverage.append({'source':p,'source_sha256':c['record']['source_sha256'],'ASR_word_count':len(expected),'assigned_word_count':len(assigned),'all_words_assigned_exactly_once_in_source_order':assigned==expected,'source_island_ranges_nonoverlapping':True,'island_ids':[i['island_id'] for i in related]})

report={'status':'CONTINUOUS_ISLAND_RENDER_PLAN_NO_AUDIO_GENERATED','ready_for_parent_whole_island_render':True,'created_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'scope':[1,2,3],'user_authorized_policy':'Keep existing picture/subtitle/other-audio timing; adapt new narration tempo to existing A4 slots.','source_snapshot':str(BASE/'替换前_完整时间线实读.json'),'source_snapshot_sha256':b.digest(BASE/'替换前_完整时间线实读.json'),'output_slices':len(slices),'merged_island_count':len(islands),'all_words_assigned_exactly_once':True,'all_source_island_ranges_nonoverlapping':True,'source_media_modified':False,'audio_or_processed_WAV_generated':False,'Resolve_or_UI_modified':False,'generation_text_reference':str(ROOT/'对标音色旁白制作_20261020/制作与下载进度.json'),'all_inputs_have_hash_verified_blind_word_ASR':True,'frame_to_sample_mapping':'All3 target timelines30fps; at48kHz each frame is1600 samples exactly. Output whole island once, then partition its PCM at listed exact sample offsets without resampling or fades between adjacent slices.','ASR_only_lexical_differences':[{'episode':p['episode'],'sequence':p['sequence'],'differences':p['ASR_only_differences']} for p in mapping['pairs'] if p['ASR_only_differences']],'clips':slices,'merged_islands':islands,'source_word_coverage':coverage,'limitations':['All words assigned exactly once is a lexical/ASR assertion; final processed-audio listening is still required to verify quiet phonemes, pauses and timbre.','Internal source-in/out estimates are NOT independent trimming instructions. Internal slices must come from one continuously rendered island, so a word spanning a record cut remains continuous.','Only true record-gap island edges use ASR-word and in-memory source PCM observations; no threshold alone proves a phoneme absent.','Exact output slot length is preserved. Original subtitle word-onset timing inside a merged island may still differ and should be checked in playback.']}
assert len(slices)==42 and len(islands)==30
(BASE/'EP01-03_42切新旁白槽位计划.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for ep in (1,2,3):
 er={**report,'scope':[ep],'clips':[s for s in slices if s['episode']==ep],'merged_islands':[i for i in islands if i['episode']==ep]};er['output_slices']=len(er['clips']);er['merged_island_count']=len(er['merged_islands'])
 (BASE/f'EP{ep:02d}_新旧旁白词边界对应.json').write_text(json.dumps(er,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'output_slices':len(slices),'islands':len(islands),'by_episode':[{'episode':ep,'slices':sum(s['episode']==ep for s in slices),'islands':sum(i['episode']==ep for i in islands),'tempo_range_percent':[min(i['tempo_percent'] for i in islands if i['episode']==ep),max(i['tempo_percent'] for i in islands if i['episode']==ep)]} for ep in (1,2,3)],'output':str(BASE/'EP01-03_42切新旁白槽位计划.json')},ensure_ascii=False,indent=2),flush=True)
