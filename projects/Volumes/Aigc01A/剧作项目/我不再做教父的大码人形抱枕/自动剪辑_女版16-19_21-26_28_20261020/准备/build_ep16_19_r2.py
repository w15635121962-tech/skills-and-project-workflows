from pathlib import Path
import json,math,datetime
R=Path.cwd();P=R/'自动剪辑_女版16-19_21-26_28_20261020/准备';M=P/'EP16-19_选片与新旁白方案.json'
base=json.loads(M.read_text()); BAK=P/'EP16-19_选片与新旁白方案.r1.json'; r1=json.loads(BAK.read_text()) if BAK.exists() else base; old={e['episode']:e for e in r1['episodes']}
ASR=P/'EP16-19_ASR';Q=P/'音频QC'; gains={Path(r['source']).stem:r['suggested_native_AudioVolume_db'] for r in json.loads((Q/'29条新旁白响度与原生增益建议.json').read_text())['records']}
FPS=24

def f(ep,g,take=1):
 cat=old[ep]['source_catalog']
 if ep==16:return next(c['path'] for c in cat if c['name']==f'大码枕头16-{g:02d}-{take:02d}.mp4')
 return next(c['path'] for c in cat if c['group']==g)
def dur(path):return next(c['video_frames'] for e in old.values() for c in e['source_catalog'] if c['path']==path)/24

def B(ep,g,a,b=None,why='',take=1,reframe=None):
 path=f(ep,g,take);return dict(source_path=path,source_start_frame=round(a*24),source_end_frame_exclusive=round((dur(path) if b is None else b)*24),reuse_reason=why,native_reframe=reframe)

def VO(ep,n,a=0,b=None):
 rec=next(v for v in old[ep]['new_narration'] if v['id']==f'大码女版枕头{ep:02d}-{n:02d}-01')
 return dict(source_path=rec['source_path'],source_in=a,source_out=rec['source_duration_seconds'] if b is None else b,text=rec['generation_text'],id=rec['id'])
class Edit:
 def __init__(self,ep):self.ep=ep;self.cursor=0;self.video=[];self.audio=[];self.blocks=[];self.reuse=[]
 def add(self,label,vos,bank,kind='narration',nframes=None):
  start=self.cursor;audio=[]
  if vos:
   for vo in vos:
    count=math.ceil((vo['source_out']-vo['source_in'])/1.1*24-1e-8)
    audio.append(dict(source_path=vo['source_path'],source_start_frame=vo['source_in']*24,source_end_frame_exclusive=vo['source_out']*24,source_in_seconds=vo['source_in'],source_out_seconds_exclusive=vo['source_out'],record_frame=self.cursor,track=2,speed_percent=110,native_speed110=True,pitch_correction=True,gain_db=gains[Path(vo['source_path']).stem],duration_frames=count,kind='new_benchmark_narration',original_generation_id=vo['id'],label=label,source_boundary_basis='blind ASR word times + PCM low-amplitude boundary QC; source seconds exact, Resolve may quantize <=1frame',fade_in_frames=1,fade_out_frames=1))
    self.cursor+=count
   length=self.cursor-start
  else:
   length=nframes if nframes is not None else sum(b['source_end_frame_exclusive']-b['source_start_frame'] for b in bank);self.cursor+=length
  available=sum(b['source_end_frame_exclusive']-b['source_start_frame'] for b in bank)
  if available<length:raise RuntimeError(f'EP{self.ep} {label}: video shortage {length-available} frames, {available}<{length}')
  remaining=length;record=start
  for i,b in enumerate(bank):
   if remaining<=0:break
   avail=b['source_end_frame_exclusive']-b['source_start_frame'];use=min(avail,remaining)
   # Avoid a final sub-half-second insert where the preceding source has room to be shortened.
   if remaining>avail and remaining-avail<12 and i+1<len(bank) and bank[i+1]['source_end_frame_exclusive']-bank[i+1]['source_start_frame']>=12:use=max(1,avail-(12-(remaining-avail)))
   c=dict(source_path=b['source_path'],source_start_frame=b['source_start_frame'],source_end_frame_exclusive=b['source_start_frame']+use,record_frame=record,track=1,speed_percent=100,duration_frames=use,kind='original_video',label=label,reuse_reason=b.get('reuse_reason',''),native_reframe=b.get('native_reframe'))
   if c['source_end_frame_exclusive']>b['source_end_frame_exclusive']:raise RuntimeError('Out of bank')
   self.video.append(c)
   sync=dict(source_path=c['source_path'],source_start_frame=c['source_start_frame'],source_end_frame_exclusive=c['source_end_frame_exclusive'],record_frame=record,track=1 if kind=='dialogue' else 3,speed_percent=100,duration_frames=use,kind='original_sync_dialogue' if kind=='dialogue' else 'original_sync_ambience',gain_db=0 if kind=='dialogue' else -12,label=label,linked_video_source_same_bounds=True,asr_is_not_human_listening=True)
   self.audio.append(sync)
   if b.get('reuse_reason'):self.reuse.append(dict(block=label,source_path=b['source_path'],source_start_frame=c['source_start_frame'],source_end_frame_exclusive=c['source_end_frame_exclusive'],record_frame=record,reason=b['reuse_reason'],native_reframe=b.get('native_reframe')))
   record+=use;remaining-=use
  assert remaining==0
  self.audio.extend(audio);self.blocks.append(dict(label=label,kind=kind,start_frame=start,end_frame_exclusive=self.cursor,duration_frames=length,new_narration_ids=[v['id'] for v in vos]))
 def result(self):
  return dict(episode=self.ep,english_episode=self.ep,chinese_episode=self.ep+1,fps=24,timeline_name_candidate=f'大码_女版_EP{self.ep:02d}_新旁白110_粗剪_v2',duration_frames=self.cursor,duration_seconds=self.cursor/24,video=self.video,audio=sorted(self.audio,key=lambda a:(a['record_frame'],a['track'])),blocks=self.blocks,explicit_broll_reuse=self.reuse,ready_for_native_rough_assembly=True,final_playback_verified=False,source_synchro_policy='Video and all original sync 100%, matching source+record frames. Canonical dialogue A1 protected; under narration original ambient sync A3 -12dB; new benchmark narration A2 native110 and pitch correction. No original narration standalone files imported.',visual_policy='No default freeze frames. Necessary borrowed material is marked. Use only same-space empty inserts or neutral reactions; no repeated spoken dialogue. Limited reused stable source shots are explicit.',verification_limits=['Blind ASR is not human listening or lip-sync acceptance','Word pronunciation variations from blind ASR are not script rewrites','Cross-episode empty broll has explicit source and reason; review native reframing in playback','No subtitle changes in this plan'])

def ep16():
 e=Edit(16)
 e.add('Alessia不敢置信，随后接她的反问',[VO(16,1,0,2.60)],[B(16,1,4.375,5.875,'黑衣V2反问结束后的无口型反应，避免V1浅色外袍造成同场服装跳变',take=2),B(16,1,0,.875,take=2)])
 e.add('情人反问human mattress，保原同期声',[],[B(16,1,.875,4.375,take=2)],kind='dialogue')
 e.add('男主沉默与日记/睡衣/眼睛闪回',[VO(16,1,2.60)],[B(16,1,4.375,None,take=2),B(16,1,5.5,9.1,'备用版不同闪回细节：两版本仅选无对白区，不重放反问',take=1)])
 e.add('情人冷笑穿衣',[VO(16,2,0,2.95)],[B(16,2,0,.75),B(16,2,4.125,5.25,'同组两句之间的无对白停顿作穿衣/观察插入'),B(16,2,7.125,7.875,'同组停顿，保留其责问前从容状态'),B(16,2,23.30,23.95,'同组最后一句后、启步前的短反应，未重复对白')])
 e.add('情人揭穿十年伤害与不配被爱，保整段同期声',[],[B(16,2,.75,23.50)],kind='dialogue')
 e.add('支票与摔门离开',[VO(16,2,2.95)],[B(16,2,23.5),B(16,3,0,1.15,'出门声后转男主床边反应，承接到下一场，无主动动作倒置')])
 e.add('男主坐在旧床位、摸床单',[VO(16,3,0,5.70)],[B(16,3,1.15,6.6)])
 e.add('十年与忍耐的自问，保原同期声',[],[B(16,3,9.625)],kind='dialogue')
 e.add('第一次想起四年前',[VO(16,3,5.70)],[B(16,3,6.6,9.625,'同组床边无对白反应，接自问后的内心回望'),B(16,1,6.5,7.9,'V1仅日记/睡衣的闪回物证，不出现浅色外袍Alessia，避免妆造跳变',take=1)])
 e.add('女主的疼痛不止身体，反思闪回',[VO(16,4,0,3.50)],[B(16,1,9.0,None,'备用版女主红眼，不重复新行动；为明确回忆闪回',take=1),B(16,1,5.85,7.2,'日记细节回忆插入，原片已有的罪证',take=1)])
 e.add('三个月后名单与Eliza名字、取大衣',[VO(16,4,3.50),VO(16,5,0,8.20)],[B(16,4,0,9.125),B(16,4,6.0,8.5,'同组名单稳定细节补读名时长；不倒放、不重复取衣动作',reframe={'zoom_x':1.12,'zoom_y':1.12}),B(16,4,3.0,4.65,'同组男主静看文件的反应，补纸面停留')])
 e.add('准备飞机去纽约，保原同期声',[],[B(16,4,9.125)],kind='dialogue')
 e.add('初到纽约',[VO(16,5,8.20)],[B(17,3,5.65,9.85,'跨集仅纽约天空/鲜花/床边花瓶空镜；已逐帧抽看无人，无日记/储物箱/减重人物状态')])
 e.add('真正属于自己的公寓、床品、枕头与空间',[VO(16,6),VO(16,7)],[B(16,5,0),B(17,3,5.65,10.65,'跨集同纽约公寓鲜花/床边空镜，无人物和未来动作；给自由生活的旁白呼吸'),B(17,3,8.45,10.70,'同床边花瓶细节再构图，稳定空镜补足实际不足；源5/15仅10秒，旁白本段16.95秒',reframe={'zoom_x':1.15,'zoom_y':1.15})])
 return e.result()

def ep17():
 e=Edit(17)
 e.add('旧日记、撕痕、无波澜、改0000封存十年',[VO(17,1),VO(17,2),VO(17,3,0,2.50)],[B(17,1,0,12),B(17,1,5,7,'同组持书静反应作回望插入，不重复改密码/合箱动作',reframe={'zoom_x':1.08,'zoom_y':1.08}),B(17,1,12),B(17,1,20,None,'箱已收好后的床区稳定终态，补足3.9秒实际旁白不足')])
 e.add('一年研究、治疗、游泳/朋友、体重与目光改变',[VO(17,3,2.50),VO(17,4),VO(17,5,0,6.0)],[B(17,2,0,24.85)])
 e.add('房东谈邻居、鲜花与想到Matteo又压下',[VO(17,5,6.0),VO(17,6),VO(17,7)],[B(17,2,24.85,27.35,'同集纽约街头中性过渡，先接回公寓，不改变人物阶段'),B(17,3,0),B(17,3,5.65,10.65,'同组纯鲜花/床边空镜作为回忆气味插入，无人物/无动作重置',reframe={'zoom_x':1.10,'zoom_y':1.10})])
 e.add('下班Evan叫住女主',[VO(17,8,0,5.125)],[B(17,2,26.875,None,'同集纽约街头中性走路反应；与此前尾段少量重叠，隔鲜花场，不重复对白'),B(17,4,4.0,4.9,'同组女主听对方开口前的沉默反应'),B(17,4,6.7,7.3,'同组无对白停顿，仅中性面部，不提前重复摸颈动作')])
 e.add('Evan猫会fetch，原同期声',[],[B(17,4,0,2.35)],kind='dialogue')
 e.add('女主忍不住笑',[VO(17,8,5.125,6.50)],[B(17,4,2.35,4.0)])
 e.add('女主反问猫会fetch，原同期声',[],[B(17,4,4.9,6.9)],kind='dialogue')
 e.add('Evan说真的还会捡球，原同期声',[],[B(17,4,7.3)],kind='dialogue')
 e.add('Evan紧张摸后颈',[VO(17,8,6.50)],[B(17,5,0,2.9)])
 e.add('Evan邀请来看，原同期声和等待',[],[B(17,5,2.9,5.55)],kind='dialogue')
 e.add('女主答应并一同离开，原同期声',[],[B(17,5,5.55)],kind='dialogue')
 return e.result()

def ep18():
 e=Edit(18)
 e.add('猫、朋友桌游与留宿',[VO(18,1),VO(18,2,0,7.70)],[B(18,1,0),B(18,2,0,9.65)])
 e.add('次日阳台、未换的花、三七天枯萎与邻居出差推测',[VO(18,2,7.70),VO(18,3),VO(18,4,0,3.50)],[B(18,3,0,5.5),B(17,3,5.65,7.8,'跨集同阳台仅鲜花/纽约天际线空镜，用于未更换时的鲜花起态，无人物、无新身份'),B(17,3,11.05,13.9,'跨集同公寓同成年女主一年后、相同衣服/发型的静看阳台中性反应；不借邀请/猫/日记动作'),B(18,3,5.5),B(18,3,7.5,None,'同组花逐渐枯萎的稳定细节再构图，补实际旁白长度，不倒转花期',reframe={'zoom_x':1.15,'zoom_y':1.15}),B(18,5,7.8,10.5,'同集深夜阳台枯花空镜，承接七天无人；不借好友申请UI或人物状态'),B(18,5,8.5,9.75,'同枯花空镜更紧的再构图，延续深夜终态，无动作重复',reframe={'zoom_x':1.12,'zoom_y':1.12})])
 e.add('第十天陌生短信、无署名和删除',[VO(18,4,3.50)],[B(18,4,0)])
 e.add('Serafina申请好友，未联系一年，她第一条消息',[VO(18,5),VO(18,6,0,1.70)],[B(18,5,0,7.8),B(18,5,10.5,None)])
 e.add('住院求助的原画面阅读停顿，不新增消息配音',[],[B(18,5,11.18)],kind='ambience')
 e.add('女主礼貌回复、对方沉默与最后恳求、语气改变',[VO(18,6,1.70,11.18),VO(18,7,0,5.60)],[B(18,6,0)])
 r=e.result();r['message_policy']='EP18 quoted texts excluded from new narration generation; blind video ASR did not establish canonical spoken message voice. Preserve original visible phone/message imagery and source ambience, do not invent dialogue or add subtitles. Readability of generated phone text requires playback review.'
 return r

def ep19():
 e=Edit(19)
 e.add('决定订次日机票、偿还最后人情',[VO(19,1)],[B(19,2,0),B(19,1,0)])
 e.add('医院门卫未认出、Serafina放行',[VO(19,2)],[B(19,3,0),B(19,4,0,1.50)])
 e.add('去顶层病房，护士轻声解释的引句',[VO(19,3,0,4.02)],[B(19,4,1.50,2.35),B(19,4,11.80,14.73,'同组护士和女主走廊静反应；只用说完之后的无对白区，避开原护士台词')])
 e.add('护士药酒过量的完整说明，原同期声',[],[B(19,4,2.35,11.80)],kind='dialogue')
 e.add('电梯打开、隔玻璃看见男主',[VO(19,3,4.02)],[B(19,4,14.73),B(19,5,0,6.0)])
 e.add('一年未治失眠、孤身病床、没有枪保镖家徽',[VO(19,4),VO(19,5),VO(19,6)],[B(19,5,6.0),B(19,6,0),B(19,7,0,4.0),B(19,5,4.5,8.75,'同组病床宽镜无对白稳定细节，补旁白，女主不重复入门动作；可轻微原生紧构图',reframe={'zoom_x':1.10,'zoom_y':1.10})])
 e.add('进门后男主长时间凝望确认她是真实的',[VO(19,7,0,6.25)],[B(19,6,1.0,4.50,'同组男主枕上静反应，不重复走位/牵手动作'),B(19,5,11.50,None,'同组床单/男主手部稳定细节，保留紧张等待状态')])
 e.add('女主问Serafina和为什么药酒混合，原同期声',[],[B(19,7,4.0)],kind='dialogue')
 e.add('男主嗓音干涩沙哑的引句',[VO(19,7,6.25)],[B(19,6,13.0,None,'同组女主静听与病床关系，无新动作/对白'),B(19,9,3.0,4.0,'同组男主床上未开口的稳定反应，避开后续拒绝Alessia的口型')])
 e.add('男主说没有你不能睡，原同期声',[],[B(19,8,0)],kind='dialogue')
 e.add('女主问Alessia，男主拒绝只要Eliza，原同期声',[],[B(19,9,0)],kind='dialogue')
 return e.result()

if __name__=='__main__':
 import sys
 target=int(sys.argv[1]) if len(sys.argv)>1 else 16
 r=globals()[f'ep{target}']();out=P/f'EP{target}_可执行r2.json';out.write_text(json.dumps({'revision':'r2_audio_first_native110','frame_convention':'all source/record ends exclusive; 24fps; source VO frame positions float permitted','episodes':[r]},ensure_ascii=False,indent=2)+'\n')
 backup=P/'EP16-19_选片与新旁白方案.r1.json'
 if not backup.exists():backup.write_text(M.read_text())
 base['revision']=f'r2_incremental_EP{target}_added';base['episodes']=[r if e['episode']==target else e for e in base['episodes']];base['apply_now']={'ready_episode_numbers':[e['episode'] for e in base['episodes'] if e.get('ready_for_native_rough_assembly')],'other_episode_r1_audio_candidates':False};M.write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n')
 print(out,'frames',r['duration_frames'],'video',len(r['video']),'audio',len(r['audio']))
