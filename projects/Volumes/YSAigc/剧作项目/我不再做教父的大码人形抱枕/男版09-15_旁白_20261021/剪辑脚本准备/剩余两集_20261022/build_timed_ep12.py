"""EP12 only: original-speed observed-source AV plan. No Resolve or browser use.
Does not alter frozen five-episode files, source media, narration adoption or production progress.
"""
from pathlib import Path
import hashlib,json,sys
OUT=Path(__file__).resolve().parent/'EP12'; OUT.mkdir(exist_ok=True)
PREP=Path(__file__).resolve().parent.parent;ROOT=PREP.parent
sys.path.insert(0,str(PREP))
from subtitle_tools import write_srt,wrap_original
from semantic_srt_tools import phrase_cues
T=json.loads((Path(__file__).resolve().parent/'新旁白实际源词时码_EP12-15_候选待采用.json').read_text())
A=json.loads((ROOT/'ASR/同期对白与原带音轨核查.json').read_text())
I=json.loads((PREP/'media_inventory_native.json').read_text())
levels={f.get('path',f.get('source_path')):f for f in json.loads((ROOT/'ASR/source_levels.json').read_text())['files']}
levels.update({f['source_path']:f for f in json.loads((ROOT/'ASR/new_narration/source_levels.json').read_text())['files']})
source={v['filename']:v for e in I['episodes'] for v in e['videos']}
adopt={f'大码男版枕头12-{j:02d}-01':f'大码男版枕头12-{j:02d}-{2 if j in [7,8] else 1:02d}' for j in range(1,9)}
files=[f for f in T['files'] if f['episode']==12 and f['actual_basename']==adopt.get(f['logical_basename'])]
assert len(files)==8 and all(f['all_expected_tokens_have_actual_observed_span'] for f in files)
for f in files: assert hashlib.sha256(Path(f['source_path']).read_bytes()).hexdigest()==f['source_sha256']
para={p['docx_paragraph']:(f,p) for f in files for p in f['paragraphs']}
units={u['id']:u for u in A['dialogue_units'] if u['episode']==12}
video=[];narr=[];events=[];story=[];cursor=0

def picture(name,a,b,record,tag,speech=False):
 v=source[name];assert 0<=a<b<=int(v['video_streams'][0]['nb_frames']),(name,a,b)
 p=v['path'];video.append({'path':p,'source_start_frame':a,'source_end_frame':b,'record_frame':record,'speed_percent':100,'gain_db':levels[p]['suggested_speech_gain_db' if speech else 'suggested_ambience_under_vo_gain_db'],'tag':tag,'same_source_linked_sync_audio':True,'contains_protected_original_dialogue':speech})

def N(pars,shots,note):
 global cursor
 start=cursor
 for number in pars:
  f,p=para[number];a=p['candidate_source_start_frame'];b=p['candidate_source_end_frame_exclusive'];dur=b-a
  narr.append({'path':f['source_path'],'source_start_frame':a,'source_end_frame':b,'record_frame':cursor,'speed_percent':100,'gain_db':levels[f['source_path']]['suggested_speech_gain_db'],'tag':f'P{number} {p["original_text"]}','logical_basename':f['logical_basename'],'source_sha256':f['source_sha256'],'original_docx_paragraphs':[number]})
  for j,w in enumerate(p['canonical_word_events_source_seconds']):
   aa=round(w['start']*24);bb=max(aa+1,round(w['end']*24));assert a<=aa<=bb<=b,(number,w,a,b,aa,bb)
   events.append({'word':w['original_word'],'start_frame':cursor+aa-a,'end_frame':cursor+bb-a,'docx_paragraph':number,'source_path':f['source_path'],'source_start_seconds':w['start'],'source_end_seconds':w['end'],'canonical_original_token_index':p['expected_token_indices'][j],'observed_source_word_indices':w['observed_source_word_indices'],'boundary_before':j==0,'type':'original_new_narration','mapping':w['mapping'],'source_asr_json':w.get('source_asr_json',f['source_asr_json'])})
  cursor+=dur
 rec=start
 for name,a,b in shots:picture(name,a,b,rec,note);rec+=b-a
 assert rec==cursor,('Video/VO length mismatch',pars,cursor-start,rec-start)
 story.append({'paragraphs':pars,'start_frame':start,'end_frame':cursor,'note':note})

def D(number,name,a,b):
 global cursor
 uid=f'EP12_P{number:04d}_Q1';u=units[uid];cs=[c for c in u['source_candidates'] if Path(c['source_path']).name==name];assert len(cs)==1;c=cs[0]
 assert not c['substantive_content_variant'] and a<=c['source_in_frame'] and b>=c['source_out_frame_exclusive']
 start=cursor;picture(name,a,b,start,'完整原同期对白 '+uid,True)
 assert u['original_text'].split()==[w['original_word'] for w in c['word_events']]
 for j,w in enumerate(c['word_events']):
  aa=round(w['start']*24);bb=max(aa+1,round(w['end']*24));assert a<=aa<bb<=b
  events.append({'word':w['original_word'],'start_frame':start+aa-a,'end_frame':start+bb-a,'docx_paragraph':number,'source_path':c['source_path'],'source_start_seconds':w['start'],'source_end_seconds':w['end'],'canonical_original_token_index':j,'observed_source_word_indices':w['observed_source_word_indices'],'boundary_before':j==0,'type':'original_sync_dialogue','dialogue_unit_id':uid})
 cursor+=b-a;story.append({'paragraphs':[number],'start_frame':start,'end_frame':cursor,'dialogue_unit_id':uid,'original_text':u['original_text'],'note':'Only one complete source rendition; same-source V/A1, identical bounds, no VO overlap.'})

N([351,352],[('男版12-1-1.mp4',0,155)],'Oliver闭口、示意接电话；只取hard变体前无对白动作')
D(353,'男版12-1-2.mp4',0,145)
N([354],[('男版12-1-1.mp4',155,162),('男版12-2-1.mp4',0,67)],'她听完电话皱眉，接站起；电话对方是画外同期声，镜内她仅听')
D(355,'男版12-2-1.mp4',67,144)
N([356],[('男版12-2-1.mp4',144,157),('男版12-2-1.mp4',226,288)],'结束通话后披回外衣，只保留一次连续动作')
N([357],[('男版12-3-1.mp4',0,83)],'未盖的药膏与灯下床边关系')
N([358],[('男版12-3-1.mp4',106,224)],'Oliver床上抬眼，门口Vittoria停步回望')
D(359,'男版12-3-1.mp4',224,271)
N([360],[('男版12-3-2.mp4',50,125),('男版12-4-1.mp4',0,41)],'仅取替代角度原话前的门口姿态，不重复问题')
N([361],[('男版12-3-1.mp4',271,313),('男版12-4-1.mp4',41,116)],'回答前Oliver灯下独坐、平静看向门口')
D(362,'男版12-4-1.mp4',134,199)
N([363,364],[('男版12-5-2.mp4',0,48),('男版12-5-1.mp4',0,213)],'切到第六夜，空房建立到空衣柜；明确时间跳转，不伪作当夜换装')
N([365],[('男版12-5-1.mp4',257,361)],'交换名额对应Oliver查看文件')
N([366],[('男版12-5-2.mp4',48,85),('男版12-6-1.mp4',0,58)],'空衣柜过桥到Oliver手机来电，未提前使用说话部分')
N([367],[('男版12-6-1.mp4',58,174)],'他意识到母亲在听，停顿后开口，保护下句原声')
D(368,'男版12-6-1.mp4',174,405)
N([369],[('男版12-5-1.mp4',213,257),('男版12-7-1.mp4',0,56)],'画外管家挂断后，已收好的行李转小床物件')
N([370],[('男版12-7-1.mp4',56,160)],'除小床物件外均已收妥，视线转向枕头和玩偶')
N([371],[('男版12-7-1.mp4',160,263)],'枕头与玩偶仍在原位')
N([372],[('男版12-7-1.mp4',263,337),('男版12-8-1.mp4',0,78)],'接玩偶手部细节，不重复整次起身')
N([373],[('男版12-8-1.mp4',78,181)],'最后一夜，他看小床后起身准备离开卧室')
N([374],[('男版12-8-1.mp4',307,361)],'切到同次移动后的客厅坐定，不重新起身')
N([375],[('男版12-9-1.mp4',0,110)],'表与手机交代等待至凌晨，不循环等待素材')
N([376],[('男版12-9-1.mp4',160,230)],'手机抬至耳边，他接听后才说原台词')
D(377,'男版12-10-1.mp4',0,72)
N([378],[('男版12-10-1.mp4',72,164)],'说完后静听，保持电话在耳旁')
N([379],[('男版12-10-1.mp4',174,289)],'Oliver神色沉下，切客厅留白，Evan下一集开头再说；排除12-10-2/3疑似非原文人声')

for kind,rows in [('video',video),('narration',narr)]:
 last=0;ranges={}
 for c in rows:
  assert c['record_frame']>=last
  if kind=='video':assert c['record_frame']==last
  for a,b in ranges.setdefault(c['path'],[]):assert c['source_end_frame']<=a or c['source_start_frame']>=b,(kind,Path(c['path']).name,a,b,c)
  ranges[c['path']].append((c['source_start_frame'],c['source_end_frame']));last=c['record_frame']+c['source_end_frame']-c['source_start_frame']
 assert last==cursor
assert len([b for b in story if b.get('dialogue_unit_id')])==6
for f in files:
 used=sorted((c['source_start_frame'],c['source_end_frame']) for c in narr if c['path']==f['source_path'])
 assert used[0][0]==0 and used[-1][1]==f['candidate_last_voice_safe_end_frame']
 assert all(a[1]==b[0] for a,b in zip(used,used[1:]))
chunks={353:["Vittoria, I nicked my finger packing the camping gear.","It hurts so bad...","I'm so clumsy, I ruin everything without you here..."],365:['Thanks to my top grades,','Professor Warren managed to snag the spot for me.'],368:["I've been accepted into an exchange program abroad.",'My flight leaves tomorrow.',"I'm going far away, and our paths will never cross again.",'Madam Blackwood can rest easy.'],372:['Vittoria was picky about beds,','feeling off if even one toy was missing.'],373:['Ten years sharing a bed,','tonight was supposed to be the last time tucking her in.'],375:['She never texted back,','so I waited until one in the morning for her call.'],379:['Unlike my tense silence,',"Evan's bright, bubbly voice chimed in first."]}
cues=phrase_cues(events,cursor,chunks);srt=OUT/'EP12.srt';write_srt(srt,cues)
actual_differences=[{'basename':f['actual_basename'],'differences':f['differences']} for f in files if f['differences']]
ep={'episode':12,'timeline_name':'大码_男版_EP12_新男版音色_原速旁白_自动剪辑_v1','duration_frames':cursor,'video':video,'narration':narr,'subtitle_srt':str(srt),'story_blocks':story,'original_word_events':events,'limitations':['Offline actual-word-frame plan only; no Resolve operations or full normal-speed human audition.','All source AV and new VO100%; no loops, frozen frames or stretching.','EP12-04 planned/plan is an ASR lexical review limitation; original subtitle planned retained, not called verified pronunciation.','Previous five completed episodes are frozen and excluded.'],'canonical_ASR_differences_pending_final_listening':actual_differences}
plan={'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':24,'episodes':[ep],'scope':'Only remaining male EP12; actual8 narration files hashed and timed. Must match final adopted narration manifest before native assembly.','offline_verified':{'contiguous_picture':True,'source_ranges_not_reused':True,'all8_new_voice_segments_complete_once':True,'all6_original_dialogue_quotes_complete_once':True,'all_words_have_actual_source_time_span':True,'max_srt_lines':max(len(c['text'].splitlines()) for c in cues),'max_line_characters':max(len(l) for c in cues for l in c['text'].splitlines()),'cue_count':len(cues),'voice_speed_percent':100,'resolve_used':False}}
(OUT/'EP12_真实帧剪辑计划.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
(OUT/'EP12_原文词事件.json').write_text(json.dumps({'fps':24,'canonical_original_words_verified':True,'original_text_source':'Manifest and original role dialogue audit; timing observed-source spans; pending pronunciation/human listening restrictions stay explicit.','episodes':[{'episode':12,'duration_frames':cursor,'events':events}]},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'plan':str(OUT/'EP12_真实帧剪辑计划.json'),'frames':cursor,'seconds':cursor/24,'video_items':len(video),'narration_items':len(narr),'srt':str(srt),'cues':len(cues),'max_lines':max(len(c['text'].splitlines()) for c in cues)},ensure_ascii=False,indent=2))
