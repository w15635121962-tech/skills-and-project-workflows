from pathlib import Path
import json,math,av
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';OUT.mkdir(exist_ok=True)
OLD=ROOT.parent/'20261017_旁白精修';old=json.loads((OLD/'工作文件/narrative_edit_plan.json').read_text());inventory=json.loads((ROOT.parent/'20261017_学校粗剪/工作文件/footage.json').read_text())
def src(group,token):
 found=[x for x in inventory if x['group']==group and token in x['name']];assert len(found)==1,(group,token,len(found));return found[0]['path']
new=[]
def add(start,end,path,a,intent,sentences):
 f0=round(start*25);f1=round(end*25);length=f1-f0
 with av.open(path) as c:
  v=c.streams.video[0];fps=float(v.average_rate);duration=float(v.duration*v.time_base) if v.duration else c.duration/1e6;resolution=[v.width,v.height]
 speed=.8 if '足球' in intent else 1
 assert a+length/25*speed<=duration+.04,(path,a,length,duration)
 s={'index':len(new)+1,'record_frame':f0,'length_frames':length,'in':a,'out':a+length/25*speed,'speed':speed,'path':path,'name':Path(path).name,'fps':fps,'is_photo':'画面资料' in path,'log':'拍摄素材转码' in path,'chapter':'开篇：书香与启航' if end<=26.68 else '青春校园：人文与科学','narration_sentence_ids':sentences,'intent':intent,'title':None,'resolution':resolution}
 new.append(s)
add(0,2.08,src('003','A003C139_'),7,'书页与光：由真实翻书动作缓缓进入校园',[1])
add(2.08,4.68,src('003','A003C133_'),.8,'由书页接到书架旁低头阅读的学生，书香落在人身上',[1])
add(4.68,9.36,src('001','20260924_C0007_'),5.8,'文化墙前自然入校的步伐，连接青春启航',[2])
add(9.36,13.60,src('003','A003C205_'),8.2,'师生围读，把深耕沃土落在陪伴与共读',[3])
add(13.60,20.32,src('004','A001C307_'),16,'透光树叶与校园；独立轻盈片名，保留画面呼吸',[4,5])
add(20.32,23.48,src('003','A003C001_'),6.2,'学生自然学习群像，青春筑梦落实于日常',[6])
add(23.48,26.68,src('006','C0210_'),7.4,'专注学生近景，收住憧憬，不使用摆拍手势',[6])
add(26.68,29.08,src('004','A001C085_'),3,'升旗队列建立仪式空间',[7])
add(29.08,33.44,src('004','A001C090_'),6,'国旗下的敬礼与目光，让庄重回到人',[7])
add(33.44,37.68,src('006','C0282_'),7,'学生朗读，保留自然翻页与书声姿态',[8])
add(37.68,40.88,src('002','A002C019_'),2,'明亮校园建筑承接空间，减少阴暗空镜停留',[9])
add(40.88,45.40,src('006','C0168_'),4,'课堂集体学习，从楼宇进入学生的求知',[9])
add(45.40,50.92,old['shots'][11]['path'],0,'书架前共同阅读，保留小学阶段真实人文气息',[10])
add(50.92,53.60,src('002','A002C043_'),4,'手部实验，探索未知',[11])
add(53.60,55.88,src('004','A001C257_'),25,'足球动作舒展青春，保留既有克制慢动作',[11])
add(55.88,58.48,src('003','A003C127_'),4,'学习更专注：先看学生低头阅读与思考',[12])
add(58.48,60.92,src('003','A003C097_'),4,'生活更有温度：教师俯身回应学生',[12])
add(60.92,63.72,src('004','A001C049_'),3,'古树、庭院与学校空间，人文自然相融',[13])
add(63.72,67.72,src('004','A001C337_'),6.2,'沙画手部艺术实践，知识与生活在动手中共生',[13])
add(67.72,70.68,src('003','A003C217_'),4,'学生自然回应与笑容，用人的温度收住开篇',[13])
for a,b in zip(new,new[1:]):assert a['record_frame']+a['length_frames']==b['record_frame']
assert new[-1]['record_frame']+new[-1]['length_frames']==1767
plan={'name':'学校_开篇人文精修_v3_20261017','base_timeline':old['name'],'fps':25,'resolution':[1920,1080],'duration_frames':11507,'scope_end_frame':1767,'shots':new,'preserve':'Duplicate live v2; keep all audio and picture after frame1767 unchanged','title':{'record_frame':383,'duration_frames':125,'main':'汇启新章 · 共育未来','sub':'文汇中学教育集团','style':'Separate editable Text+ overlay, white sans serif, no large opaque banner'}}
(OUT/'opening_plan_v3.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',15);sheet=Image.new('RGB',(1440,5*260),(245,244,240));d=ImageDraw.Draw(sheet)
for i,s in enumerate(new):
 tm=(s['in']+s['out'])/2
 with av.open(s['path']) as c:
  v=c.streams.video[0];c.seek(int(tm/v.time_base),stream=v)
  for f in c.decode(v):
   if f.time>=tm:im=f.to_image();break
 im.thumbnail((360,203));x=i%4*360;y=i//4*260;sheet.paste(im,(x,y));d.text((x+4,y+206),f"{s['index']:02d}  {s['record_frame']/25:.2f}–{(s['record_frame']+s['length_frames'])/25:.2f}s",font=font,fill='black');d.text((x+4,y+228),s['intent'][:23],font=font,fill='black')
sheet.save(OUT/'opening_source_selections.jpg',quality=94);print('PLAN_READY',len(new),flush=True)
