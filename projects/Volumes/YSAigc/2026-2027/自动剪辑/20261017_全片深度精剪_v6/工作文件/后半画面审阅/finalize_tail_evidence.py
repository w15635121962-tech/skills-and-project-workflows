import json,subprocess,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path('/Volumes/YSAigc/2026-2027');OUT=BASE/'自动剪辑/20261017_全片深度精剪_v6/工作文件/后半画面审阅';SRC=BASE/'文汇中学/拍摄素材转码';PLAN=BASE/'自动剪辑/20261017_开篇向往感精修_v5/工作文件/opening_plan_v5.json';old=json.loads(PLAN.read_text());look='/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py';probe='/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/probe.py'
ENG=next(s['path'] for s in old['shots'] if s['record_frame']==8332)
specs=[
(5035,122,SRC/'006/Proxies/C0255_Proxy.mov',1.0,'把“每个学生当成孩子”的画面纠正为教师俯身交流，温暖表情和真实视线关系对应关怀。','原C0258实为穿同款校服学生相互看作业，未见教师；C0255教师面部与俯身交流清楚。'),
(5435,108,SRC/'006/Proxies/C0179_Proxy.mov',1.0,'用黑板前一对一答疑呈现教师耐心，保留4.32秒完整相处。','原C097源7–11.32与开篇55.88–60.92源7–12.04完全重叠；新文件全片未用。'),
(5717,90,SRC/'005/Proxies/20260921_D0568_Proxy.mov',1.0,'沙画指尖绘出植物纹理，给素质教育之花一个有温度的操作细节，停留3.6秒。','替代已见过多次的课堂全景；此B机真实手部与暖光沙纹适合人文艺术质感，不另加慢速。'),
(8332,72,ENG,40.6,'保留真实前门外国语学校英语节身份来源，改用不同的语言游戏交流片段。','原69.28–72.16与四校介绍3891帧69.28–71.80重复；新段40.60–43.48未使用，画面学生站立交流；避开原资料出入转场，保留原资料活动字样。'),
(8473,90,SRC/'005/Proxies/20260921_D0577_Proxy.mov',1.0,'陶塑工具与指尖操作，补充艺术课程从全景到触觉细节的层次，保留3.6秒。','相邻仍保留教师艺术辅导照片和立体字展示；本段改用真实陶塑近景，未把手工误称化学实验。'),
(9452,78,SRC/'007/Proxies/C0022_Proxy.mov',7.0,'将第二张集团揭牌合影换为本次集团竖牌实拍细节，承接“一脉相承，共赴新程”。','9378帧真实揭牌合影保留，成绩与四校身份档案均不动；新片源可读中学教育集团文字，仅作牌匾细节，不冒称另一校区。'),
(9752,108,SRC/'003/Proxies/A003C224_26092473_Proxy.mov',1.0,'侧近景教师看学生、指向学习材料并交流，落实坚守育人初心。','原C0127源7–11.32与5157帧源4–7.72重叠0.72秒；新机位全片未用。'),
(10714,68,SRC/'005/Proxies/20260921_D0498_Proxy.mov',1.0,'在“激活智慧，不断创新”处看见学生协同拼装结构件，替换已重复的工程课区间。','原A001C229源15–17.72与8027帧源12–16.2重叠1.2秒；新片看得见轨道/框架与部件，不声称已完成机器人。')]
overlay_specs=[
(11242,76,SRC/'006/Proxies/C0234_Proxy.mov',1.0,'在“汇通中西”时补英语课堂师生文本交流。','本文件前面使用10–14.28及20–22.72，新段1–4.04不重叠；只称英语课堂，不指定未经证明的校区。'),
(11318,89,SRC/'005/Proxies/20260921_D0503_Proxy.mov',1.0,'在“胜任未来的创新能力”时补工程课工作台前的学生协作。','新文件全片未用，学生低头操作与抬身交流为真实拍摄；与10714帧D0498同类课程但不同机位、不同源。')]

def build(spec,overlay=False):
 rf,n,path,src,intent,desc=spec;path=str(path);end=round(src+n/25,8);times=[round(src+.04,3),round(src+n/50,3),round(end-.04,3)];stem=f'final_{rf}';prefix=OUT/(stem+'.png');cmd=['python3',look,path]
 for t in times:cmd+=['--at',str(t)]
 cmd+=['-o',str(prefix),'--no-timecode','--overwrite','--json'];r=subprocess.run(cmd,capture_output=True,text=True);(OUT/(stem+'_look.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,(rf,r.stderr)
 p=subprocess.run(['python3',probe,path,'--json'],capture_output=True,text=True);(OUT/(stem+'_probe.json')).write_text(p.stdout);assert p.returncode==0
 ev=[str(OUT/(f'{stem}_{t:.3f}s.png')) for t in times];assert all(Path(x).exists() for x in ev)
 previous=[s for s in old['shots'] if s['path']==path and s['record_frame']!=rf];overlaps=[]
 for s in previous:
  overlap=max(0,min(end,s['out'])-max(src,s['in']))
  if overlap>.0001:overlaps.append({'record_frame':s['record_frame'],'source_in':s['in'],'source_out':s['out'],'overlap_seconds':overlap})
 assert not overlaps,(rf,overlaps)
 item={'record_frame':rf,'length_frames':n,'path':path,'in':src,'out':end,'speed':1,'intent':intent,'evidence':{'description':desc,'source_times_seconds':times,'frames':ev,'first_middle_last_viewed':False},'picture_only':True,'source_audio_import':False,'fps':24.0 if path==ENG else 25.0,'is_photo':False,'log':path!=ENG,'resolution':[960,544] if path==ENG else [1280,720],'preserves_duration':True,'source_overlap_with_full_v5':overlaps}
 if overlay:item.update({'track':'V2','kind':'interview_broll','preserve_underlying_interview_picture_and_audio':True})
 else:item.update({'track':'V1','kind':'equal_length_replacement','replaces':next(s for s in old['shots'] if s['record_frame']==rf)})
 return item

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 patches=list(pool.map(lambda x:build(x),specs));overlays=list(pool.map(lambda x:build(x,True),overlay_specs))
meta={'base_plan':str(PLAN),'fps':25,'duration_frames':11507,'duration_seconds':460.28,'scope':'picture only; complete narration/music/location sound unchanged; do not add interviews','first_middle_last_review':'pending final contact sheet inspection','preserved':'existing historic archives, all school identity sections, achievement evidence, complete 433.65877s narration, all audio and original principal statement'}
(OUT/'v6_tail_change_groups.json').write_text(json.dumps({**meta,'changes':patches},ensure_ascii=False,indent=2));(OUT/'v6_interview_broll_recommendations.json').write_text(json.dumps({**meta,'principal_on_camera_before_broll':{'start_frame':11042,'end_frame_exclusive':11242,'seconds':8.0},'changes':overlays},ensure_ascii=False,indent=2))
font=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',19)
for page in range(3):
 items=(patches+overlays)[page*4:page*4+4];canvas=Image.new('RGB',(1440,len(items)*306),(24,24,24));draw=ImageDraw.Draw(canvas)
 for row,item in enumerate(items):
  for col,impath in enumerate(item['evidence']['frames']):
   im=Image.open(impath).convert('RGB');im.thumbnail((480,270));canvas.paste(im,(col*480,row*306+36));label=f"R{item['record_frame']} {'EnglishFestival' if item['path']==ENG else Path(item['path']).stem} {item['evidence']['source_times_seconds'][col]:.2f}s";draw.text((col*480+6,row*306+7),label,font=font,fill='white')
 canvas.save(OUT/f'最终八项及采访补画首中末_{page+1:02d}.jpg',quality=94)
print(json.dumps({'changes':len(patches),'overlays':len(overlays),'source_overlap_count':0,'contact_sheets':3},ensure_ascii=False))
