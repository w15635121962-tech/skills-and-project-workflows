"""Offline maleEP13 native fragment from actually observed new VO and reviewed source shots.
No Resolve operations. Merge with all7 episodes only after final adopted44-VO list.
"""
from pathlib import Path
import hashlib,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from subtitle_tools import write_srt,parse_srt
from semantic_srt_tools import phrase_cues,CHUNKS_13
ROOT=Path(__file__).resolve().parent.parent;OUT=Path(__file__).resolve().parent
T=json.loads((OUT/'新旁白实际源词时码_EP12-15_候选待采用.json').read_text());A=json.loads((ROOT/'ASR/同期对白与原带音轨核查.json').read_text());I=json.loads((OUT/'media_inventory_native.json').read_text());L=json.loads((ROOT/'ASR/source_levels.json').read_text())
source={v['filename']:v for e in I['episodes'] for v in e['videos']};levels={f.get('path',f.get('source_path')):f for f in L['files']};levels.update({f.get('path',f.get('source_path')):f for f in json.loads((ROOT/'ASR/new_narration/source_levels.json').read_text())['files']});files=[f for f in T['files'] if f['episode']==13 and f['actual_basename'].endswith('-01')]
assert len(files)==5
para={p['docx_paragraph']:(f,p) for f in files for p in f['paragraphs']}
units={u['id']:u for u in A['dialogue_units'] if u['episode']==13}
video=[];narr=[];events=[];story=[];cursor=0

def picture(name,a,b,record,tag,speech=False):
 v=source[name];assert 0<=a<b<=int(v['video_streams'][0]['nb_frames']);p=v['path']
 video.append({'path':p,'source_start_frame':a,'source_end_frame':b,'record_frame':record,'speed_percent':100,'gain_db':levels[p]['suggested_speech_gain_db' if speech else 'suggested_ambience_under_vo_gain_db'],'tag':tag,'same_source_linked_sync_audio':True,'contains_protected_original_dialogue':speech})

def N(pars,shots,note):
 global cursor
 start=cursor
 for number in pars:
  f,p=para[number];a=p['candidate_source_start_frame'];b=p['candidate_source_end_frame_exclusive'];dur=b-a
  narr.append({'path':f['source_path'],'source_start_frame':a,'source_end_frame':b,'record_frame':cursor,'speed_percent':100,'gain_db':levels[f['source_path']]['suggested_speech_gain_db'],'tag':f'P{number} {p["original_text"]}','logical_basename':f['logical_basename'],'source_sha256':f['source_sha256'],'original_docx_paragraphs':[number]})
  for j,w in enumerate(p['canonical_word_events_source_seconds']):
   aa=round(w['start']*24);bb=max(aa+1,round(w['end']*24));assert a<=aa<=bb<=b,(number,w,a,b,aa,bb)
   events.append({'word':w['original_word'],'start_frame':cursor+aa-a,'end_frame':cursor+bb-a,'docx_paragraph':number,'source_path':f['source_path'],'source_start_seconds':w['start'],'source_end_seconds':w['end'],'boundary_before':j==0,'type':'original_new_narration','mapping':w['mapping']})
  cursor+=dur
 rec=start
 for name,a,b in shots:picture(name,a,b,rec,note);rec+=b-a
 assert rec==cursor,('Video/VO length mismatch',pars,cursor-start,rec-start)
 story.append({'paragraphs':pars,'start_frame':start,'end_frame':cursor,'note':note})

def D(number,name,a,b):
 global cursor
 uid=f'EP13_P{number:04d}_Q1';u=units[uid];cs=[c for c in u['source_candidates'] if Path(c['source_path']).name==name];assert len(cs)==1;c=cs[0]
 assert not c['substantive_content_variant'] and a<=c['source_in_frame'] and b>=c['source_out_frame_exclusive']
 start=cursor;picture(name,a,b,start,'完整原同期对白 '+uid,True)
 assert u['original_text'].split()==[w['original_word'] for w in c['word_events']]
 for j,w in enumerate(c['word_events']):
  aa=round(w['start']*24);bb=max(aa+1,round(w['end']*24));assert a<=aa<bb<=b
  events.append({'word':w['original_word'],'start_frame':start+aa-a,'end_frame':start+bb-a,'docx_paragraph':number,'source_path':c['source_path'],'boundary_before':j==0,'type':'original_sync_dialogue','dialogue_unit_id':uid})
 cursor+=b-a;story.append({'paragraphs':[number],'start_frame':start,'end_frame':cursor,'dialogue_unit_id':uid,'original_text':u['original_text'],'note':'Only one full source rendition; same-source V/A1 at identical bounds, no VO overlap.'})

D(382,'男版13-1-2.mp4',26,121)
N([383],[('男版13-1-1.mp4',113,231)],'告白说完后的Evan与Vittoria烟花关系反应，未重复同一句')
D(384,'男版13-2-1.mp4',10,85)
D(385,'男版13-2-2.mp4',50,152)
N([386],[('男版13-3-1.mp4',0,92)],'Vittoria在烟花下浅笑改口；切在本源Fine首词之前')
D(387,'男版13-3-2.mp4',90,145)
N([388,389],[('男版13-3-1.mp4',141,289),('男版13-4-1.mp4',49,83)],'Oliver移开手机，夜窗前留恋消失')
N([390],[('男版13-4-1.mp4',117,259)],'清晨机场拉箱，随后机舱落座，保持先后')
N([391],[('男版13-4-2.mp4',60,90),('男版13-5-1.mp4',0,104)],'成年机舱回想，切庄园建立与少年，明确回忆层次')
N([392],[('男版13-5-1.mp4',104,248)],'十三岁少年在人群中紧张、走向庄园')
N([393],[('男版13-5-1.mp4',248,261),('男版13-5-2.mp4',0,96)],'少年手指收紧与抬眼；be brave由内心新旁白说，不新增儿童嘴型')
N([394,395],[('男版13-5-1.mp4',284,313),('男版13-6-1.mp4',0,241)],'切回二十三岁机舱，完整一次旧SIM换新卡；不重复抽卡')
N([396,397],[('男版13-7-1.mp4',155,265)],'云层转成年Oliver侧脸，心里说keep going；保留完整内心原文')

# Every logical narration source from frame0 to its reviewed voice-safe end occurs
# once; all video intervals are contiguous and within episode13.
for kind,rows in [('video',video),('narration',narr)]:
 last=0;ranges={}
 for c in rows:
  assert c['record_frame']>=last
  if kind=='video':assert c['record_frame']==last
  for a,b in ranges.setdefault(c['path'],[]):assert c['source_end_frame']<=a or c['source_start_frame']>=b
  ranges[c['path']].append((c['source_start_frame'],c['source_end_frame']));last=c['record_frame']+c['source_end_frame']-c['source_start_frame']
 assert last==cursor
assert len([b for b in story if b.get('dialogue_unit_id')])==4
for f in files:
 used=sorted((c['source_start_frame'],c['source_end_frame']) for c in narr if c['path']==f['source_path'])
 assert used[0][0]==0 and used[-1][1]==f['candidate_last_voice_safe_end_frame']
 assert all(a[1]==b[0] for a,b in zip(used,used[1:]))
cues=phrase_cues(events,cursor,CHUNKS_13);srt=ROOT/'字幕/EP13.srt'
if srt.exists() and parse_srt(srt)!=[(c['start_frame'],c['end_frame'],c['text']) for c in cues]:
 backup=srt.parent/'版本留痕/EP13_初版4秒切分.srt';backup.parent.mkdir(exist_ok=True)
 if not backup.exists():backup.write_bytes(srt.read_bytes())
write_srt(srt,cues)
actual_differences=[{'basename':f['actual_basename'],'differences':f['differences']} for f in files if f['differences']]
ep={'episode':13,'timeline_name':'大码_男版_EP13_新男版音色_原速旁白_自动剪辑_v1','duration_frames':cursor,'video':video,'narration':narr,'subtitle_srt':str(srt),'story_blocks':story,'original_word_events':events,'limitations':['All source-only cuts and new VO are100%; only nonspeech tails were trimmed. No source loops, frozen frames or time stretching.','Canonical original subtitle spelling is retained for ASR proper-name/number/contraction differences; these observed-span mappings are explicit, not a claim of exact human pronunciation audit.','This offline native fragment requires merging with all7 episodes and the final adopted44-VO selection list before assembly. No Resolve save/import/playback performed by this script.'],'canonical_ASR_differences_pending_final_listening':actual_differences}
plan={'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':24,'episodes':[ep],'scope':'EP13 native fragment only; must merge with other6 male episodes and match final44 narration adoption before executing the all-episode assembler.','offline_verified':{'contiguous_picture':True,'source_ranges_not_reused':True,'all5_new_voice_segments_complete_once':True,'all4_original_dialogue_quotes_complete_once':True,'all_words_have_actual_source_time_span':True,'max_srt_lines':max(len(c['text'].splitlines()) for c in cues),'max_line_characters':max(len(l) for c in cues for l in c['text'].splitlines()),'cue_count':len(cues),'voice_speed_percent':100,'resolve_used':False}}
(OUT/'EP13_真实帧剪辑计划.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
(OUT/'EP13_原文词事件.json').write_text(json.dumps({'fps':24,'canonical_original_words_verified':True,'original_text_source':'manifest and original role dialogue audit; timing is observed-source span, pronunciation review limits remain in plan','episodes':[{'episode':13,'duration_frames':cursor,'events':events}]},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'plan':str(OUT/'EP13_真实帧剪辑计划.json'),'frames':cursor,'seconds':cursor/24,'video_items':len(video),'narration_items':len(narr),'srt':str(srt),'cues':len(cues),'max_lines':max(len(c['text'].splitlines()) for c in cues)},ensure_ascii=False,indent=2))
