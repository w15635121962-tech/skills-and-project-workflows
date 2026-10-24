from pathlib import Path
from copy import deepcopy
import json,hashlib
B=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/自动剪辑_女版07-09_12-15_20261023');FPS=24
p=B/'female_edit_plan_EP08.json';d=json.loads(p.read_text(encoding='utf-8'));e=d['episodes'][0];old=deepcopy(e)
(B/'female_edit_plan_EP08_修复字头前.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
# Source frame begins include 80 ms before actual proper-name onset.
fixes={253:100,258:163,264:261,274:0}
ops=[]
for n in e['narration']:
 para=n['original_docx_paragraphs'][0]
 if para in fixes:
  new=fixes[para];delta=n['source_start_frame']-new;assert delta>0
  ops.append({'paragraph':para,'old_source_start_frame':n['source_start_frame'],'new_source_start_frame':new,'insert_record_frame_old':n['record_end_frame'],'delta_frames':delta,'path':n['path']})
def shift(x):return x+sum(o['delta_frames'] for o in ops if o['insert_record_frame_old']<=x)
for v in e['video']:
 st,en=v['record_frame'],v['record_end_frame'];ns,ne=shift(st),shift(en)
 # A correction inside a V1 cut extends that cut into previously unused quiet source frames.
 extra=(ne-ns)-(en-st)
 v['source_end_frame']+=extra
 v['record_frame']=v['record_start_frame']=ns;v['record_end_frame']=ne;v['source_end_seconds']=v['source_end_frame']/FPS
 if extra:
  v['reason']+='；恢复VO专名词头后延长未用自然反应画面'+str(extra)+'帧';v['tag']=v['reason']
for n in e['narration']:
 st,en=n['record_frame'],n['record_end_frame'];n['record_frame']=n['record_start_frame']=shift(st);n['record_end_frame']=shift(en)
 para=n['original_docx_paragraphs'][0]
 if para in fixes:
  n['source_start_frame']=fixes[para];n['source_start_seconds']=fixes[para]/FPS;n['asr_match_ratio_note']='Restored unmatched leading proper name by actual ASR word onset; fuzzy lexical ratio is not accepted as a word-head cut criterion.'
for ev in e['audio_events']:
 ev['record_frame']=shift(ev['record_frame']);para=ev['docx_paragraph']
 if ev['kind']=='narration' and para in fixes:
  sf=fixes[para];ev['source_start_frame']=sf;ev['source_start_seconds']=sf/FPS;ev['clip_source_start_frame']=sf
  asr=json.loads((B/'ASR/raw_large-v3-turbo/EP08/narration'/(Path(ev['source_path']).stem+'.json')).read_text(encoding='utf-8'))
  ev['observed_words']=[w for w in asr['words'] if w['start']>=sf/FPS-.001 and w['end']<=ev['source_end_frame']/FPS+.001]
 ev['event_record_start_frame']=ev['record_frame']+ev['source_start_frame']-ev['clip_source_start_frame'];ev['event_record_end_frame']=ev['record_frame']+ev['source_end_frame']-ev['clip_source_start_frame'];ev['record_end_frame']=ev['record_frame']+ev['clip_source_end_frame']-ev['clip_source_start_frame']
for b in e['story_blocks']:b['record_start_frame']=shift(b['record_start_frame']);b['record_end_frame']=shift(b['record_end_frame'])
e['duration_frames']=shift(old['duration_frames']);e['duration_seconds']=e['duration_frames']/FPS
e['original_paragraph_timeline_anchors']=[{'docx_paragraph':x['docx_paragraph'],'kind':x['kind'],'record_start_frame':x['event_record_start_frame'],'record_end_frame':x['event_record_end_frame'],'canonical_text':x['canonical_text']} for x in e['audio_events']]
e['revision']='EP08_restore_four_leading_names_v2_20261023';e['word_head_restoration']=ops
e['limitations'].append('修复初版4处旁白专名词头；按实际ASR首词恢复Alessia及Matteo开头，所有后续record累计顺延69帧。未对声音加速或改词。')
for a,b in zip(e['video'],e['video'][1:]):assert a['record_end_frame']==b['record_frame']
assert e['video'][-1]['record_end_frame']==e['duration_frames']
for c in e['video']+e['narration']:assert c['source_end_frame']-c['source_start_frame']==c['record_end_frame']-c['record_frame'],(Path(c['path']).name,c)
for i,a in enumerate(e['video']):
 for b in e['video'][i+1:]:assert a['path']!=b['path'] or max(a['source_start_frame'],b['source_start_frame'])>=min(a['source_end_frame'],b['source_end_frame'])
for n in e['narration']:
 for v in e['video']:
  if v['kind']=='synchronous_dialogue':assert max(n['record_frame'],v['record_frame'])>=min(n['record_end_frame'],v['record_end_frame'])
assert len(e['narration'])==12
for para in fixes:
 ev=next(x for x in e['audio_events'] if x['docx_paragraph']==para);assert ev['observed_words'];print(para,ev['observed_words'][0]['word'],ev['source_start_frame'],ev['record_frame'])
e['offline_validation']['source_ranges_overlap_frames']=0;e['offline_validation']['restored_leading_names_count']=4;e['offline_validation']['revision']=e['revision']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
q=B/'female_edit_plan_EP07-09.json';combo=json.loads(q.read_text(encoding='utf-8'));combo['episodes']=[e if x['episode']==8 else x for x in combo['episodes']];q.write_text(json.dumps(combo,ensure_ascii=False,indent=2),encoding='utf-8')
(B/'EP08_词头修复记录.json').write_text(json.dumps({'status':'PASS_OFFLINE_WAITING_INDEPENDENT_QA','old_duration_frames':old['duration_frames'],'new_duration_frames':e['duration_frames'],'delta_frames':sum(x['delta_frames'] for x in ops),'changes':ops,'all_original_speed_percent':100,'video_and_A1_same_source_ranges':True,'VO_dialogue_overlap_frames':0,'source_repeated_overlap_frames':0},ensure_ascii=False,indent=2),encoding='utf-8')
print('EP08 frames',e['duration_frames'],'seconds',e['duration_seconds'])
