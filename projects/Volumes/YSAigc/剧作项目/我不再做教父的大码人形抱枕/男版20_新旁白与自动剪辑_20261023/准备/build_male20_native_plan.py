from pathlib import Path
from copy import deepcopy
from difflib import SequenceMatcher
import json,math,re,hashlib
R=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕');B=R/'男版20_新旁白与自动剪辑_20261023';FPS=24
manifest=json.loads((B/'准备/剧情与旁白制作清单.json').read_text(encoding='utf-8'));draft=json.loads((B/'准备/选片草案_待旁白实际词码.json').read_text(encoding='utf-8'));candidates=json.loads((B/'ASR/EP20_原对白与源时码候选.json').read_text(encoding='utf-8'))['dialogue_units'];vmeta={x['filename']:x for x in manifest['actual_video_files']};rows={x['docx_paragraph']:x for x in manifest['ordered_source_entries']}
missing=[x['basename'] for x in manifest['segments'] if not (B/'ASR/raw_large-v3-turbo/narration'/(x['basename']+'.json')).exists()]
if missing:
 print(json.dumps({'status':'WAITING_FOR_REAL_MP3_AND_ASR','missing':missing},ensure_ascii=False));raise SystemExit(0)
levels=json.loads((B/'ASR/speech_levels.json').read_text(encoding='utf-8'));nlevels={x['sequence']:x for x in levels['files'] if x['kind']=='new_narration'}
if set(nlevels)!=set(range(1,10)):
 print(json.dumps({'status':'WAITING_FOR_ALL_NINE_MEASURED_VO_GAINS','missing_gain_sequences':sorted(set(range(1,10))-set(nlevels))}));raise SystemExit(0)
dialogue_gains={551:-1.4,554:4.0,561:-2.8,563:-.9}
video=[];narration=[];events=[];blocks=[];limitations=[];record=0

def video_clip(name,a,b,rec,kind,reason,paras=(),gain=-18):
 fn='男版20-'+name+'.mp4';src=vmeta[fn];maxf=int(src['frame_count']);a=int(a);b=min(int(b),maxf);assert b>a
 x={'path':src['path'],'source_start_frame':a,'source_end_frame':b,'source_start_seconds':a/FPS,'source_end_seconds':b/FPS,'record_frame':rec,'record_start_frame':rec,'record_end_frame':rec+b-a,'duration_frames':b-a,'gain_db':gain,'tag':reason,'kind':kind,'reason':reason,'canonical_text':' '.join(rows[p]['text'] for p in paras),'original_docx_paragraphs':list(paras),'source_native_fps':24,'speed_percent':100,'same_source_linked_sync_audio':True,'video_track':1,'audio_track':1};video.append(x);return x

def event(kind,sp,text,path,clipstart,clipend,rec,words,paras,evstart=None,evend=None):
 a=math.floor(min(w['start'] for w in words)*FPS) if evstart is None else evstart;b=math.ceil(max(w['end'] for w in words)*FPS) if evend is None else evend
 x={'kind':kind,'speaker':sp,'canonical_text':text,'source_path':path,'clip_source_start_frame':clipstart,'clip_source_end_frame':clipend,'source_start_frame':a,'source_end_frame':b,'source_start_seconds':a/FPS,'source_end_seconds':b/FPS,'record_frame':rec,'record_end_frame':rec+clipend-clipstart,'event_record_start_frame':rec+a-clipstart,'event_record_end_frame':rec+b-clipstart,'record_frame_basis':'whole source clip start; map each source word at record_frame + round(word.start * 24) - clip_source_start_frame','original_docx_paragraphs':list(paras),'docx_paragraph':paras[0],'observed_words':words}
 if kind=='narration' and list(paras)==[552,553]:x['word_timing_source']=str(B/'ASR/derived_timing/narration/大码男版枕头20-04-01_音近词对齐.json')
 events.append(x);return x

for block in draft['ordered_blocks']:
 st=record;kind=block['kind'];reason=block['reason']
 if kind=='narration':
  seg=manifest['segments'][block['sequence']-1];src=Path(seg['target_audio_path']);asrpath=B/'ASR/raw_large-v3-turbo/narration'/(seg['basename']+'.json');asr=json.loads(asrpath.read_text(encoding='utf-8'));assert Path(asr['source_path'])==src and src.exists();assert hashlib.sha256(src.read_bytes()).hexdigest()==asr['source_sha256'];assert nlevels[block['sequence']]['source_sha256']==asr['source_sha256'];ws=asr['words'];assert ws
  # Never derive cut edges from the first EXACT canonical word: retain actual first phonetic word, including names.
  a=max(0,math.floor((min(w['start'] for w in ws)-.12)*FPS));b=min(math.floor(asr['decoded_duration_seconds']*FPS),math.ceil((max(w['end'] for w in ws)+.20)*FPS));assert b>math.ceil(max(w['end'] for w in ws)*FPS)-1
  n=b-a;record+=n;x={'path':str(src),'source_start_frame':a,'source_end_frame':b,'source_start_seconds':a/FPS,'source_end_seconds':b/FPS,'record_frame':st,'record_start_frame':st,'record_end_frame':record,'duration_frames':n,'gain_db':nlevels[block['sequence']]['conservative_gain_db'],'kind':'narration','tag':seg['basename'],'canonical_text':seg['text'],'reason':'原文纯旁白100%原速，实际第一发声音近词完整保留，外部人物对白在另一独立V1/A1段穿插','original_docx_paragraphs':seg['source_docx_paragraphs'],'speed_percent':100,'audio_track':2,'asr_evidence':str(asrpath),'source_sha256':asr['source_sha256']};narration.append(x);event('narration','Oliver',seg['text'],str(src),a,b,st,ws,seg['source_docx_paragraphs'])
  cur=st;need=n
  for name,aa,bb in block['video_pool']:
   if need<=0:break
   aa=round(aa*FPS);bb=round(bb*FPS);take=min(need,bb-aa);video_clip(name,aa,aa+take,cur,'picture_with_linked_natural_audio',reason,seg['source_docx_paragraphs']);cur+=take;need-=take
  assert need<=0,('need more same-state unused cover',block['sequence'],need)
  tokens=lambda s:re.findall(r"[a-z]+(?:'[a-z]+)?",s.lower().replace('’',"'"))
  ratio=SequenceMatcher(None,tokens(seg['text']),tokens(asr['text']),autojunk=False).ratio()
  if ratio<.9:limitations.append({'segment':seg['basename'],'issue':'Blind ASR lexical fidelity below0.90; keep full audio and canonical original, require independent review','ratio':ratio,'observed':asr['text']})
 elif kind=='dialogue':
  aa,bb=[round(x*FPS) for x in block['source_seconds']];paras=block['paragraphs'];v=video_clip(block['video'],aa,bb,st,'synchronous_dialogue',reason,paras,dialogue_gains.get(paras[0],0));record=v['record_end_frame']
  for pn in paras:
   unit=next(u for u in candidates if u['docx_paragraph']==pn);c=next(c for c in unit['source_candidates'] if c['source_path']==v['path']);ws=c['observed_words'];assert min(w['start'] for w in ws)*FPS>=aa and max(w['end'] for w in ws)*FPS<=bb
   event('dialogue',rows[pn]['speaker'],unit['original_text'],v['path'],aa,bb,st,ws,[pn])
 elif kind=='silent_reaction':
  aa,bb=[round(x*FPS) for x in block['source_seconds']];v=video_clip(block['video'],aa,bb,st,'silent_reaction_with_linked_natural_audio',reason,(),-6);record=v['record_end_frame']
 blocks.append({'kind':kind,'sequence':block.get('sequence'),'source_paragraphs':seg['source_docx_paragraphs'] if kind=='narration' else block.get('paragraphs',[]),'record_start_frame':st,'record_end_frame':record,'reason':reason})

assert video[0]['record_frame']==0 and video[-1]['record_end_frame']==record
for a,b in zip(video,video[1:]):assert a['record_end_frame']==b['record_frame']
for i,a in enumerate(video):
 for b in video[i+1:]:assert a['path']!=b['path'] or max(a['source_start_frame'],b['source_start_frame'])>=min(a['source_end_frame'],b['source_end_frame']),('source repeated',a,b)
for n in narration:
 for v in video:
  if v['kind']=='synchronous_dialogue':assert max(n['record_frame'],v['record_frame'])>=min(n['record_end_frame'],v['record_end_frame'])
assert [x['docx_paragraph'] for x in events if x['kind']=='dialogue']==[549,551,554,557,559,561,563,565]
limitations += ['No Resolve or browser operation by offline preparation. Full-motion and listening validation is separate from structural/frame/word verification.','Source script itself includes Madam Blackwood after no one else around. Narration retained verbatim; visible mother stays seated in selected continuity.','1-1 primary ASR next-video repetitions and short reaction vocalizations in other alternate takes are not original dialogue and never become subtitles. Source audio remains linked at reduced natural gain during narration.','Main3-1 male still has outer shirt after P550 coat action. Use white-T3-2 for male question; only female-only6sec+ portion from3-1 is retained.']
e={'episode':20,'source_script_episode':20,'mapping_basis':manifest['episode_mapping_verification']['basis'],'timeline_name':draft['timeline_name'],'duration_frames':record,'duration_seconds':record/FPS,'video':video,'narration':narration,'audio_events':events,'story_blocks':blocks,'limitations':limitations,'original_paragraph_timeline_anchors':[{'docx_paragraph':x['docx_paragraph'],'source_paragraphs':x['original_docx_paragraphs'],'kind':x['kind'],'record_start_frame':x['event_record_start_frame'],'record_end_frame':x['event_record_end_frame'],'canonical_text':x['canonical_text']} for x in events],'offline_validation':{'narration_speed_percent':100,'same_V1_A1_source_boundaries':True,'source_repeated_overlap_frames':0,'VO_dialogue_overlap_frames':0,'original_dialogue_units':8,'narration_segments':9,'first_actual_ASR_word_preserved_for_every_narration':True,'generation_state':'All actual MP3 files SHA matched ASR, no estimated durations used'}}
d={'status':'READY_FOR_NATIVE_ASSEMBLY_WAITING_INDEPENDENT_REVIEW','project':'大码枕头','fps':24,'source_end_frame_exclusive':True,'all_original_speed_percent':100,'mix_gain_basis':{'measurement_file':str(B/'ASR/speech_levels.json'),'VO_target_lufs':-18,'VO_true_peak_ceiling_dbtp':-2,'dialogue_gain_db_by_source_paragraph':dialogue_gains,'only_timeline_clip_gain_changed_source_files_unmodified':True},'scope':'男版EP20新男版音色原速旁白，保留完整同期对白；不改既有时间线','source_script_path':manifest['authority_script_path'],'source_script_sha256':manifest['authority_script_sha256'],'episodes':[e]}
q=B/'final_native_plan.json';q.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');(B/'准备/男版20_原生剪辑计划.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'path':str(q),'duration_frames':record,'duration_seconds':record/FPS,'video_cuts':len(video),'VO_segments':len(narration),'dialogue':8},ensure_ascii=False))
