from scout_v7 import *
from copy import deepcopy
BASE=ROOT/'自动剪辑/20261017_镜头节奏与开篇重剪_v7/工作文件/base_plan_v6.json'
p=json.load(open(BASE));old={s['record_frame']:s for s in p['shots']}
# r, length, source group, source id, source in, inherited shot start, exact visual intent
spec=[
 (0,60,'004','A001C070',5.0,0,'红柱与窗棂构成干净纵深，第一秒进入校园文脉；此处无校名，不将小学单独冒作集团主体。'),
 (60,57,'006','C0206',6.0,0,'立即切到清楚的笔尖、按页手指与课本批注，以真实阅读书写落实“书香浸润”；弃用C140虚焦翻页。'),
 (117,58,'001','C0011',16.08,117,'校门女老师自然挥手迎接，将“青春启航的港湾”落实为被看见与被接纳。'),
 (175,59,'001','C0001',1.8,117,'迎面入校的学生接上老师问候，改掉旧横穿镜头；无摆姿势与空校门停留。'),
 (234,53,'003','A003C205',8.2,234,'围读师生的书本、专注与自然交流，保留温暖关系而缩短到2.12秒。'),
 (287,53,'003','A003C133',1.0,234,'书架间男生阅读近景，视线落在书页；用人的求知承接“点亮梦想”。'),
 (340,56,'004','A001C077',6.0,340,'文汇中学校名与仰拍立面建立真实身份；固定片名第一幅底图，左下无人物脸。'),
 (396,56,'007','C0017',7.0,340,'阳光楼角形成明亮通透的空间；固定片名第二幅底图，左下为暗部空地。'),
 (452,56,'004','A001C307',18.0,340,'校园树光只留2.24秒作为片名末幅，保留呼吸但去掉6.72秒冗长停留。'),
 (508,53,'003','A003C199',15.4,508,'同伴拍手自然互动，以真实关系开启青春段落。'),
 (561,53,'003','A003C229',5.2,587,'女生平静抬头倾听，保留真实专注目光，避免低头做题连段。'),
 (614,53,'003','A003C211',1.4,587,'少女自然回应与笑意，收在看向老师的目光，取段不与片尾15秒后区间重叠。'),
 (667,60,'004','A001C087',6.0,667,'升旗手展旗的完整短动作先落“旗帜飘扬”，不再先给静止队列。'),
 (727,55,'004','A001C090',6.6,727,'国旗与少年敬礼仰拍，保留风与仪式感，2.2秒完成信息。'),
 (782,54,'004','A001C086',5.0,727,'整齐的全校队列收束升旗组，近人与大场面交替而不拖长。'),
 (836,53,'006','C0282',7.0,836,'真实捧书朗读，以人声姿态对齐“琅琅书声”。'),
 (889,53,'006','C0283',5.6,836,'手指沿书页与翻阅细节补足书声段景别变化，不误将课堂全景当翻书特写。'),
 (942,60,'007','C0016',7.0,942,'明亮楼角2.4秒建立现代教学环境，替代原3.2秒持景。'),
 (1002,65,'006','C0168',4.0,1022,'窗边明亮课堂全景进入真实学习空间，承接教学楼到智慧课堂。'),
 (1067,68,'006','C0205',9.2,1022,'少年从书面抬头听讲的完整短动作，落在“求知之路”与人的专注。'),
 (1135,69,'003','A003C134',6.0,1135,'书架纵深中的女生阅读，图书馆段先明确场所，不再一镜5.52秒。'),
 (1204,69,'003','A003C129',4.0,1135,'阅览桌前女生顺页阅读，中近景接书架镜头，保留自然专注与真实图书馆。'),
 (1273,67,'002','A002C039',6.8,1273,'保留明确滴管、试管的真实化学操作；2.68秒已够紧凑，动作完整优先。'),
 (1340,57,'004','A001C262',20.32,1340,'保留飞身扑球的起跳接球动作，2.28秒无需再碎切。'),
 (1397,63,'003','A003C226',3.0,1397,'同伴围书讨论与指点，2.52秒对应“让学习更专注”。'),
 (1460,63,'003','A003C096',4.4,1397,'女老师俯近学生温和交流，清楚的脸与真实笑意对应“让生活更有温度”。'),
 (1523,61,'004','A001C037',3.0,1523,'石雕流水与树影2.44秒，对齐“人文与自然相融”，不把水景无限延长。'),
 (1584,61,'004','A001C337',6.2,1593,'沙画手部真实勾勒2.44秒，仅置于“知识与生活共生”的原语义位置。'),
 (1645,61,'004','A001C051',10.4,1523,'绿叶前景与红柱窗格的校园角落，叶片有层次但不遮住空间，承接“每一处角落”。'),
 (1706,61,'003','A003C217',4.0,1693,'学生自然笑容将校园的温度落回人，2.44秒收住开篇。')
]
segments=[]
for i,(r,l,g,t,ins,base_r,intent) in enumerate(spec,1):
 a=lookup(g,t);s=deepcopy(old[base_r]);s.update(index=i,record_frame=r,length_frames=l,path=a['path'],name=a['name'],fps=float(a['fps']),**{'in':ins,'out':round(ins+l/25,6)},speed=1,is_photo=False,log=True,resolution=[1280,720],title=None,revision_v7=True,intent=intent,source_start_frame=round(ins*a['fps']),source_count_frames=round(l*a['fps']/25),source_out_exclusive=round(ins+l/25,6),in_requested=ins)
 # remove stale animated photo bindings and source evidence from old assets
 for k in ['asset_id','source_photo','legacy_v2_index']:
  if k in s:s[k]=None
 s['evidence_v7']={'first_middle_last':[],'source_overlap_with_retained_v6':[],'viewed':False}
 segments.append(s)
assert sum(s['length_frames'] for s in segments)==1767
assert all(segments[i]['record_frame']+segments[i]['length_frames']==segments[i+1]['record_frame'] for i in range(len(segments)-1))
assert all(45<=s['length_frames']<=70 for s in segments)
kept=[s for s in p['shots'] if s['record_frame']>=1767]+p['interview_overlays_v6']
for s in segments:
 for k in kept:
  if s['path']==k['path']:
   a=max(s['in'],k['in']);z=min(s['out'],k['in']+k['length_frames']/25)
   if z-a>.001:s['evidence_v7']['source_overlap_with_retained_v6'].append({'record_frame':k['record_frame'],'overlap':z-a})
 assert not s['evidence_v7']['source_overlap_with_retained_v6'],(s['record_frame'],s['path'])
 a=next(a for a in F if a['path']==s['path']);assert s['out']<=a['duration']+.001
for batchstart in range(0,len(segments),5):
 batch=segments[batchstart:batchstart+5];im=Image.new('RGB',(1680,len(batch)*345),(245,243,238));d=ImageDraw.Draw(im)
 for row,s in enumerate(batch):
  times=[s['in'],s['in']+(s['length_frames']//2)/25,s['out']-.04]
  for col,sec in enumerate(times):
   fr=frame(s['path'],sec);dest=OUT/f"选定_{s['record_frame']:04d}_{col+1}_{sec:.2f}.jpg";fr.save(dest,quality=92)
   s['evidence_v7']['first_middle_last'].append({'time':round(sec,4),'path':str(dest)})
   fr=fr.resize((560,315));im.paste(fr,(col*560,row*345))
   caption=f"{s['record_frame']/25:.2f}s / {s['path'].split('/')[-3]}/{s['name'].split('_Proxy')[0]} / 源{sec:.2f}s"
   d.text((col*560+5,row*345+317),caption,font=font,fill=(25,25,25))
 path=OUT/f'选定首中尾_{batchstart//5+1:02d}.jpg';im.save(path,quality=93);print(path,flush=True)
# all front/middle/end frames must be visually approved by the caller before delivery
json.dump(segments,open(OUT/'segments_pending_view.json','w'),ensure_ascii=False,indent=2)
