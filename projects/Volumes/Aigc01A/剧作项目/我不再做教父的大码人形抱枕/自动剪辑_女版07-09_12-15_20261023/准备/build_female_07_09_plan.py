from pathlib import Path
from difflib import SequenceMatcher
import json,re,math,unicodedata
R=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕');B=R/'自动剪辑_女版07-09_12-15_20261023';FPS=24
script=json.loads((B/'剧本顺序依据.json').read_text(encoding='utf-8'))
inv=json.loads((B/'素材盘点.json').read_text(encoding='utf-8'))
probe={x['path']:x for x in inv['files']}
def tok(t):return re.findall(r"[a-z]+(?:'[a-z]+)?|[0-9]+",unicodedata.normalize('NFKD',t.replace('’',"'")).lower())
def prep(ep):
 e=next(x for x in script['episodes'] if x['episode']==ep);rows={x['docx_paragraph_0_based']:x for x in e['ordered_source_entries']}
 c=json.loads((B/'ASR'/f'EP{ep:02d}_complete.json').read_text(encoding='utf-8'));F={Path(x['source_path']).name:json.loads(Path(x['json_path']).read_text(encoding='utf-8')) for x in c['files']}
 ct=[];owners=[]
 for i,row in rows.items():
  if row['kind']=='narration':
   ts=tok(row['raw_source_text']);ct+=ts;owners += [i]*len(ts)
 aw=[];wt=[]
 for f in sorted([x for x in F.values() if x['kind']=='narration'],key=lambda x:x['order']):
  for wi,w in enumerate(f['words']):
   for t in tok(w['word']):wt.append(t);aw.append((f,wi,w))
 mapped={}
 for m in SequenceMatcher(None,ct,wt,autojunk=False).get_matching_blocks():
  for k in range(m.size):mapped[m.a+k]=m.b+k
 bounds={}
 for i,row in rows.items():
  if row['kind']!='narration':continue
  ids=[j for j,v in enumerate(owners) if v==i];ms=[mapped[j] for j in ids if j in mapped];assert ms,(ep,i)
  first,last=aw[min(ms)],aw[max(ms)];assert first[0]['source_path']==last[0]['source_path'],(ep,i,'crossfile')
  f=first[0];words=f['words'];a=first[2]['start'];b=last[2]['end'];fi,li=first[1],last[1]
  pre=words[fi-1]['end'] if fi else 0;post=words[li+1]['start'] if li+1<len(words) else f['source_duration_seconds']
  a=max(0,a-.08,pre+.015 if fi else 0);b=min(f['source_duration_seconds'],b+.14,post-.015 if li+1<len(words) else post)
  sf=max(0,math.floor(a*FPS));ef=math.ceil(b*FPS)
  bounds[i]={'path':f['source_path'],'a':sf,'b':ef,'asr_start':first[2]['start'],'asr_end':last[2]['end'],'match_ratio':len(ms)/len(ids),'asr_words':words[fi:li+1],'canonical':row['raw_source_text'].strip(),'source_paragraph':i+1}
 return rows,F,bounds
class Plan:
 def __init__(self,ep):
  self.ep=ep;self.rows,self.files,self.bounds=prep(ep);self.record=0;self.video=[];self.narr=[];self.events=[];self.blocks=[];self.limit=[]
 def src(self,k):
  fn=k if k.endswith('.mp4') else f'女版{self.ep}-{k}.mp4';return self.files[fn]
 def v(self,k,a,b,rec,kind,reason,paras=None,gain=-18):
  f=self.src(k);p=probe[f['source_path']];maxf=int(p['video_streams'][0]['nb_frames']);aa=round(a*FPS) if isinstance(a,float) else a;bb=round(b*FPS) if isinstance(b,float) else b;bb=min(bb,maxf)
  assert bb>aa,(k,aa,bb)
  d={'path':f['source_path'],'source_start_frame':aa,'source_end_frame':bb,'source_start_seconds':aa/FPS,'source_end_seconds':bb/FPS,'record_frame':rec,'record_start_frame':rec,'record_end_frame':rec+bb-aa,'gain_db':gain,'tag':reason,'kind':kind,'canonical_text':' '.join(self.rows[i]['raw_source_text'].strip() for i in (paras or [])),'reason':reason,'speed_percent':100,'same_source_linked_sync_audio':True,'audio_track':1,'video_track':1,'source_native_fps':24,'original_docx_paragraphs':[i+1 for i in (paras or [])]};self.video.append(d);return bb-aa
 def vo(self,paras,pool,reason):
  st=self.record
  for i in paras:
   x=self.bounds[i];n=x['b']-x['a'];d={'path':x['path'],'source_start_frame':x['a'],'source_end_frame':x['b'],'source_start_seconds':x['a']/FPS,'source_end_seconds':x['b']/FPS,'record_frame':self.record,'record_start_frame':self.record,'record_end_frame':self.record+n,'gain_db':0,'tag':'女版原速旁白 '+str(i+1),'kind':'narration','canonical_text':x['canonical'],'reason':'原文顺序，逐句原速分割，给下一句对白留出独占声场','speed_percent':100,'audio_track':2,'original_docx_paragraphs':[i+1],'asr_match_ratio':round(x['match_ratio'],4)};self.narr.append(d)
   self.events.append({'kind':'narration','speaker':'Eliza Mercer','canonical_text':x['canonical'],'source_path':x['path'],'source_start_frame':x['a'],'source_end_frame':x['b'],'source_start_seconds':x['a']/FPS,'source_end_seconds':x['b']/FPS,'record_frame':self.record,'record_end_frame':self.record+n,'docx_paragraph':i+1,'observed_words':x['asr_words']});self.record+=n
  need=self.record-st;cur=st
  for k,a,b in pool:
   if need<=0:break
   aa=round(a*FPS);bb=round(b*FPS);n=min(need,bb-aa)
   self.v(k,aa,aa+n,cur,'picture_with_linked_natural_audio',reason,paras);cur+=n;need-=n
  assert need<=0,(self.ep,paras,'not enough cover frames',need)
  self.blocks.append({'kind':'narration_with_picture','record_start_frame':st,'record_end_frame':self.record,'source_paragraphs':[i+1 for i in paras],'reason':reason})
 def dlg(self,paras,k,a,b,reason):
  f=self.src(k);st=self.record;n=self.v(k,round(a*FPS),round(b*FPS),st,'synchronous_dialogue',reason,paras,0);self.record+=n
  for i in paras:
   row=self.rows[i];text=' '.join(x['text'] for x in row['audio_parts_in_source_order'] if x['kind']!='narration');words=f['words']
   self.events.append({'kind':'dialogue','speaker':row['speaker'],'canonical_text':text,'source_path':f['source_path'],'source_start_frame':round(a*FPS),'source_end_frame':round(b*FPS),'source_start_seconds':a,'source_end_seconds':b,'record_frame':st,'record_end_frame':self.record,'docx_paragraph':i+1,'observed_words':[w for w in words if a-.01<=w['start'] and w['end']<=b+.01],'note':'Multiple dialogue units in one clip are individually anchored by candidate words in ASR/EPxx_dialogue_candidates.json; use candidate bounds for subtitles, not whole clip duration.'})
  self.blocks.append({'kind':'dialogue','record_start_frame':st,'record_end_frame':self.record,'source_paragraphs':[i+1 for i in paras],'reason':reason})
 def silent(self,k,a,b,reason):
  n=self.v(k,round(a*FPS),round(b*FPS),self.record,'silent_reaction_with_linked_natural_audio',reason,[], -6);self.record+=n
 def done(self):
  for a,b in zip(self.video,self.video[1:]):assert a['record_end_frame']==b['record_frame']
  assert self.video[0]['record_frame']==0 and self.video[-1]['record_end_frame']==self.record
  for n in self.narr:
   for v in self.video:
    if v['kind']=='synchronous_dialogue':assert max(n['record_frame'],v['record_frame'])>=min(n['record_end_frame'],v['record_end_frame'])
  return {'episode':self.ep,'source_script_episode':self.ep,'mapping_basis':'Actual blind ASR dialogue and narration plus viewed contact sheet match this original female script episode. User folder episode numbers 07/08/09 confirmed; no extrapolation from other folders.','timeline_name':f'大码_女版_EP{self.ep:02d}_原速旁白_自动剪辑_20261023_v1','duration_frames':self.record,'duration_seconds':self.record/FPS,'video':self.video,'narration':self.narr,'audio_events':self.events,'story_blocks':self.blocks,'limitations':self.limit+['Contact sheets viewed at 20%/75%; selected frame ranges and words aligned offline. Full-motion and listening review still required after assembly.','All source audio accompanies identical V1 ranges on A1; natural audio under VO reduced to -18 dB rather than muted. Dialogue ranges are 0 dB and never overlap A2 VO.','ASR proper names/inflections may differ from source spelling; canonical text retained from original female script, no new synthetic dialogue.']}

p=Plan(7)
p.vo([225,226],[('7-2',0.,2.6),('1-1',3.3,12.8)],'前床侧两人对视接床上亲近，保留当夜人物和大码体型；两take均已看联系图')
p.vo([227],[('7-3',.9,4.95)],'补镜男主抱起女主到床边，画面动作对应抱到床上')
p.dlg([229],'2-2',.30,2.40,'采用17秒完整主take第一句；舍弃4秒压缩版，保留词首词尾')
p.vo([230,231],[('2-2',2.40,9.50),('3-1',0.,1.6)],'主take两句中间的相视与手部接近，接女主手指抓紧的细节')
p.dlg([232],'2-2',9.55,15.40,'完整男主坦白第二句，保持原同期口型，不与旁白重叠')
p.vo([233,234,235,236,237,238],[('3-1',1.6,14.),('4-2',0.,4.0),('4-2',5.85,11.),('4-1',0.,1.7)],'连续亲近的手、脸与女主反应；避开4-2名字呼唤区和4-1疑似Hello区')
p.vo([239],[('5-1',0.,3.4)],'进入事后盖被的手部动作，承接未转身离开')
p.vo([240],[('5-1',3.4,8.1)],'拉被圈抱与亲近的事后延续，停在男主开口之前')
p.dlg([241],'5-1',8.1,9.4,"保留原Don't leave同期声及尾部呼吸")
p.vo([242,243,244],[('5-1',9.4,12.),('6-1',0.,6.4),('6-1',8.4,15.)],'事后抚背到女主眼神的希望，避开6-1 Oh疑点区')
p.vo([245,246,247,248],[('7-1',0.,4.),('7-4',0.,5.9),('7-1',13.2,15.3),('7-4',7.9,14.05)],'次日铃声、ALLIE手机细节与女主反应；避开各take额外名字呼唤区')
p.limit+=['7-2-1压缩且中句不完整，未采用对白；7-2-2保留全部3条原文对白。','7-3-1两个模型均有互不一致的模板/零时长词幻觉；不产生这些字幕，保留源自然声低增益，仍需成片听审。','7-4-2、7-7-1/2/4名字呼唤区在VO覆盖画面中避开；未把无独立原台词的名字另增成对白。','原有人工EP07时间线不修改，本计划只供新建独立v1时间线。']
e7=p.done();(B/'female_edit_plan_EP07.json').write_text(json.dumps({'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':24,'source_end_frame_exclusive':True,'episodes':[e7]},ensure_ascii=False,indent=2),encoding='utf-8');print('EP07',e7['duration_seconds'])

p=Plan(8)
p.vo([251,252],[('1-1',0.,6.5)],'女主递电话后男主接听的同一主take，先交代来电')
p.dlg([253,254,255,256],'1-1',8.25,20.65,'保留Alessia电话原声四句，男主听电话表情；原呼吸停顿保留')
p.vo([257,258],[('1-1',20.65,22.),('2-1',0.,5.0)],'电话结束，男主笑意退去，跨两组同场近景接续')
p.vo([259],[('2-1',5.0,9.5)],'男主近景审视身边女主，停在问话前')
p.dlg([260],'2-1',11.3,13.2,'男主问昨夜为何是她，留词尾')
p.vo([261],[('2-1',13.2,18.8),('2-1',21.5,22.4)],'女主反应近景承受寒意，额外静反应接在回答前而不重复对白')
p.dlg([262],'2-1',18.8,21.5,'女主完整反问It was me / Who did you think it was')
p.vo([263],[('3-1',0.,3.4)],'男主从停顿到嘲笑，接下句开口')
p.dlg([264],'3-1',3.4,6.0,'男主嘲讽女主离不开自己')
p.vo([265],[('3-1',6.0,11.1)],'支票拿出及动作发生在两句之间，不压对白')
p.dlg([266],'3-1',12.,15.45,'保留obedient和enough两小句完整同期')
p.vo([267],[('4-1',0.,2.4)],'门铃响起时的男主床边反应')
p.vo([268],[('4-2',0.,2.6)],'Alessia持香槟入门补镜')
p.vo([269],[('4-3',1.5,5.)],'同场入门后Alessia打量床，选独立入门补镜，避免整段重复')
p.dlg([271],'5-2',0.,2.55,'补镜先给两人关系再转女主，完整by the night/by the pound一句')
p.silent('5-2',2.7,3.45,'留女主收紧唇角的反应半秒，A1自然声保留')
p.dlg([272],'5-1',8.25,10.75,'主take第二句bed collapse，不重复前一句')
p.vo([273],[('5-1',10.75,13.3)],'男主站在情人身旁未维护的关系画面')
p.dlg([274,275],'6-1',.55,9.05,'男主take money、stay pillow、stop imagining全句同期，原停顿保留')
p.silent('6-1',13.0,15.0,'女主离床反应作为结尾，不再重复男主台词')
p.limit+=['8-4-1主模型重复厨房模板、二次模型只有感叹号；不作对白或字幕；源自然声保留-18 dB待听审。','8-4-2/3输入ASR也有不合剧情的碎词；只用于入门动作画面，未把这些碎词当原对白。','5-2第一句和5-1第二句各用一次；5-3同句补镜备用未重复插入。']
e8=p.done();(B/'female_edit_plan_EP08.json').write_text(json.dumps({'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':24,'source_end_frame_exclusive':True,'episodes':[e8]},ensure_ascii=False,indent=2),encoding='utf-8');print('EP08',e8['duration_seconds'])

p=Plan(9)
p.vo([278],[('1-1',1.4,6.5)],'母亲递续约合约的开场主take，避开起始气声')
p.dlg([279,280],'1-2',0.,5.8,'母亲近景补镜两句连贯完整，避免与主take重复')
p.vo([281,282],[('1-1',12.4,17.2)],'女主反应及合同细节，先交代半薪再逼签')
p.dlg([283],'1-3',.4,1.65,'单独Sign it补镜，保留后续手指反应待VO用')
p.dlg([284],'2-1',.6,4.5,'母亲第一句羞辱原同期')
p.dlg([285],'2-1',6.65,15.5,'完整长句羞辱，覆盖所有词尾，不做中途跳字剪切')
p.vo([286,287],[('2-1',15.5,21.),('1-3',1.65,4.0),('1-1',1.4,5.75)],'红圈慈善礼服照片、女主双手与母亲的冷淡反应；相同照片只取一段')
p.vo([288,289,290],[('3-1',0.,4.05),('3-1',6.05,9.7),('3-2',0.,2.85)],'续约回忆和迟疑，避开3-1非原文I am sorry所在4.34–5.84秒')
p.vo([291],[('3-1',9.7,14.),('3-2',2.85,5.55),('4-2',0.,1.0)],'支票与女主沉默的闪回，随后转当前合约，交代下决定的触发')
p.silent('4-2',5.6,8.85,'近景合约合拢与横放笔的可见动作，留给女主决定落点')
p.dlg([293,294],'4-2',8.85,13.9,'采用24秒正常语速主take，避免4秒压缩版；致谢和拒续约完整')
p.vo([295],[('4-2',13.9,17.7)],'拒绝之后母亲反应，VO不盖女主刚才说话')
p.vo([296],[('4-3',0.,.55),('4-4',0.,2.95)],'女主从椅边起身到坚定站稳的两角度补镜')
p.dlg([297],'4-4',2.95,4.8,'近景My job ends here完整收尾；不用压缩版重复')
p.limit+=['9-3-1非原文I am sorry区未采用；9-3-2长零时长模板不作字幕，保留所选画面A1自然声低增益待听审。','9-4-1为4秒压缩三句话版未用于对白；正常24秒主take承载前两句，4-4独立近景承载结句。','母亲冷淡反应1-1 1.4–5.75秒在后段照片说明中重用；单独列出是明确的反应插镜复用，未将动作当新事件。']
e9=p.done();(B/'female_edit_plan_EP09.json').write_text(json.dumps({'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':24,'source_end_frame_exclusive':True,'episodes':[e9]},ensure_ascii=False,indent=2),encoding='utf-8');print('EP09',e9['duration_seconds'])
res={'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':24,'source_end_frame_exclusive':True,'all_original_speed_percent':100,'scope':'仅用户女版素材EP07、08、09；新建独立时间线，不改既有人工作品EP07；V1/A1同源同入出点，A2逐句原速旁白。','source_script_path':script['authority_source_path'],'source_script_sha256':script['source_sha256'],'visual_review_evidence':[str(B/'画面联系图'/f'EP{ep:02d}_p1.jpg') for ep in [7,8,9]],'episodes':[e7,e8,e9]}
(B/'female_edit_plan_EP07-09.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
