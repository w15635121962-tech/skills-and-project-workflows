"""Offline maleEP14 native fragment from actually observed new VO and reviewed source shots.
No Resolve operations. Merge with all7 episodes only after final adopted44-VO list.
"""
from pathlib import Path
import hashlib,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from subtitle_tools import write_srt,parse_srt
from semantic_srt_tools import phrase_cues,CHUNKS_14
ROOT=Path(__file__).resolve().parent.parent;OUT=Path(__file__).resolve().parent
T=json.loads((OUT/'新旁白实际源词时码_EP12-15_候选待采用.json').read_text());A=json.loads((ROOT/'ASR/同期对白与原带音轨核查.json').read_text());I=json.loads((OUT/'media_inventory_native.json').read_text());L=json.loads((ROOT/'ASR/source_levels.json').read_text())
source={v['filename']:v for e in I['episodes'] for v in e['videos']};levels={f.get('path',f.get('source_path')):f for f in L['files']};levels.update({f.get('path',f.get('source_path')):f for f in json.loads((ROOT/'ASR/new_narration/source_levels.json').read_text())['files']});adopt={r['logical_basename']:r['selected_basename'] for r in json.loads((ROOT/'ASR/旁白采用清单_草稿.json').read_text())['selections']};files=[f for f in T['files'] if f['episode']==14 and f['actual_basename']==adopt.get(f['logical_basename'])]
assert len(files)==9
para={p['docx_paragraph']:(f,p) for f in files for p in f['paragraphs']}
units={u['id']:u for u in A['dialogue_units'] if u['episode']==14}
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
 uid=f'EP14_P{number:04d}_Q1';u=units[uid];cs=[c for c in u['source_candidates'] if Path(c['source_path']).name==name];assert len(cs)==1;c=cs[0]
 assert not c['substantive_content_variant'] and a<=c['source_in_frame'] and b>=c['source_out_frame_exclusive']
 start=cursor;picture(name,a,b,start,'完整原同期对白 '+uid,True)
 assert u['original_text'].split()==[w['original_word'] for w in c['word_events']]
 for j,w in enumerate(c['word_events']):
  aa=round(w['start']*24);bb=max(aa+1,round(w['end']*24));assert a<=aa<bb<=b
  events.append({'word':w['original_word'],'start_frame':start+aa-a,'end_frame':start+bb-a,'docx_paragraph':number,'source_path':c['source_path'],'boundary_before':j==0,'type':'original_sync_dialogue','dialogue_unit_id':uid})
 cursor+=b-a;story.append({'paragraphs':[number],'start_frame':start,'end_frame':cursor,'dialogue_unit_id':uid,'original_text':u['original_text'],'note':'Only one full source rendition; same-source V/A1 at identical bounds, no VO overlap.'})

N([400],[('男版14-1-2.mp4',20,121),('男版14-1-1.mp4',167,181)],'哄睡无效、她仍清醒；避开片头非原文疑似人声')
N([401],[('男版14-1-1.mp4',181,299)],'Evan贴近、领口和颈侧动作连续，保留本源同期声')
D(402,'男版14-2-2.mp4',0,95)
N([403],[('男版14-2-2.mp4',167,234)],'Vittoria带兴味的反应')
N([404],[('男版14-2-2.mp4',95,153)],'Evan的近脸反打')
N([405],[('男版14-3-1.mp4',0,36),('男版14-2-2.mp4',234,313)],'Evan张扬贴近，她看向他；无重复对白')
N([406],[('男版14-3-1.mp4',62,150)],'Vittoria目光飘开，慢慢走神')
N([407],[('男版14-3-1.mp4',150,237),('男版14-3-2.mp4',0,76)],'眼前Evan的亲昵细节，带出Oliver静静读书的回忆')
N([408],[('男版14-4-1.mp4',0,89)],'回忆书本和Oliver低头阅读')
N([409],[('男版14-3-2.mp4',76,121),('男版14-4-1.mp4',89,219)],'书页插入后承接她拉近、他自然环抱，动作只一次')
N([410],[('男版14-4-1.mp4',229,323)],'回到现实她想起往日，嘴角稍动再开手机')
N([411],[('男版14-4-1.mp4',323,361),('男版14-5-1.mp4',0,102)],'手机微光下笑意冻结，保留侧后Evan关系')
N([412],[('男版14-5-1.mp4',102,140),('男版14-6-2.mp4',48,100)],'无人回复，她的眼神沉下去；没有提前重拨的动作')
N([413],[('男版14-5-1.mp4',140,201)],'Vittoria立刻拨号')
N([414],[('男版14-5-1.mp4',201,310)],'拨号等待与皱眉，三分钟由原旁白浓缩，不循环')
N([415],[('男版14-5-1.mp4',343,385)],'Evan再次贴近她')
D(416,'男版14-6-1.mp4',68,114)
N([417],[('男版14-6-1.mp4',173,337)],'嘴唇、眼神与关屏动作，压住一点慌意，动作到闭屏完成')
N([418],[('男版14-6-2.mp4',0,42),('男版14-7-1.mp4',0,110)],'手部过桥接回夜晚两人，她环近Evan，不再拨号')
N([420],[('男版14-7-1.mp4',110,248)],'切到次日Evan在床上，Vittoria手机无回音、起身不耐')
N([421],[('男版14-8-1.mp4',56,72),('男版14-8-1.mp4',179,245)],'留下Evan，门口背影、开车；裁掉片头非剧本话音，不重复出门')
N([422],[('男版14-8-1.mp4',245,289),('男版14-9-1.mp4',0,85)],'门锁、原密码仍有效、开入空房')
N([423],[('男版14-9-1.mp4',85,199)],'空荡房间转她的震惊近景，接第15集')

# Every logical narration source from frame0 to its reviewed voice-safe end occurs
# once; all video intervals are contiguous and within episode14.
for kind,rows in [('video',video),('narration',narr)]:
 last=0;ranges={}
 for c in rows:
  assert c['record_frame']>=last
  if kind=='video':assert c['record_frame']==last
  for a,b in ranges.setdefault(c['path'],[]):assert c['source_end_frame']<=a or c['source_start_frame']>=b
  ranges[c['path']].append((c['source_start_frame'],c['source_end_frame']));last=c['record_frame']+c['source_end_frame']-c['source_start_frame']
 assert last==cursor
assert len([b for b in story if b.get('dialogue_unit_id')])==2
for f in files:
 used=sorted((c['source_start_frame'],c['source_end_frame']) for c in narr if c['path']==f['source_path'])
 assert used[0][0]==0 and used[-1][1]==f['candidate_last_voice_safe_end_frame']
 assert all(a[1]==b[0] for a,b in zip(used,used[1:]))
cues=phrase_cues(events,cursor,CHUNKS_14);srt=ROOT/'字幕/EP14.srt'
if srt.exists() and parse_srt(srt)!=[(c['start_frame'],c['end_frame'],c['text']) for c in cues]:
 backup=srt.parent/'版本留痕/EP14_初版4秒切分.srt';backup.parent.mkdir(exist_ok=True)
 if not backup.exists():backup.write_bytes(srt.read_bytes())
write_srt(srt,cues)
actual_differences=[{'basename':f['actual_basename'],'differences':f['differences']} for f in files if f['differences']]
ep={'episode':14,'timeline_name':'大码_男版_EP14_新男版音色_原速旁白_自动剪辑_v1','duration_frames':cursor,'video':video,'narration':narr,'subtitle_srt':str(srt),'story_blocks':story,'original_word_events':events,'limitations':['All source-only cuts and new VO are100%; only nonspeech tails were trimmed. No source loops, frozen frames or time stretching.','Adopt14-01/03 take02 from the current draft. The14-01 collar/color homophone and proper-name spellings remain explicit listening-review limits, not a claim of exact human pronunciation audit.','This offline native fragment requires merging with all7 episodes and the final adopted44-VO selection list before assembly. No Resolve save/import/playback performed by this script.'],'canonical_ASR_differences_pending_final_listening':actual_differences}
plan={'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':24,'episodes':[ep],'scope':'EP14 native fragment only; must merge with other6 male episodes and match final44 narration adoption before executing the all-episode assembler.','offline_verified':{'contiguous_picture':True,'source_ranges_not_reused':True,'all9_new_voice_segments_complete_once':True,'all2_original_dialogue_quotes_complete_once':True,'all_words_have_actual_source_time_span':True,'max_srt_lines':max(len(c['text'].splitlines()) for c in cues),'max_line_characters':max(len(l) for c in cues for l in c['text'].splitlines()),'cue_count':len(cues),'voice_speed_percent':100,'resolve_used':False}}
(OUT/'EP14_真实帧剪辑计划.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
(OUT/'EP14_原文词事件.json').write_text(json.dumps({'fps':24,'canonical_original_words_verified':True,'original_text_source':'manifest and original role dialogue audit; timing is observed-source span, pronunciation review limits remain in plan','episodes':[{'episode':14,'duration_frames':cursor,'events':events}]},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'plan':str(OUT/'EP14_真实帧剪辑计划.json'),'frames':cursor,'seconds':cursor/24,'video_items':len(video),'narration_items':len(narr),'srt':str(srt),'cues':len(cues),'max_lines':max(len(c['text'].splitlines()) for c in cues)},ensure_ascii=False,indent=2))
