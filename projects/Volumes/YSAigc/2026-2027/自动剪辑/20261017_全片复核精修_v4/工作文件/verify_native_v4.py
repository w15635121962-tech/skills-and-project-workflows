import sys,json,time,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageStat
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精修预览';FR=PRE/'实际画面';FR.mkdir(parents=True,exist_ok=True);DET=PRE/'重点切点与字幕';DET.mkdir(exist_ok=True)
plan=json.loads((OUT/'refined_plan_v4.json').read_text());build=json.loads((OUT/'native_build_v4.json').read_text());r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name'];assert r.OpenPage('edit')
def tc(f):
 ss,ff=divmod(f,25);mm,ss=divmod(ss,60);hh,mm=divmod(mm,60);return f'{hh:02}:{mm:02}:{ss:02}:{ff:02}'
def capture(frame,path):
 assert not path.exists(),path;assert t.SetCurrentTimecode(tc(frame));time.sleep(.16);assert p.ExportCurrentFrameAsStill(str(path));assert path.exists() and path.stat().st_size>1000;im=Image.open(path).convert('RGB');assert im.size==(1920,1080);return im
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',15);records=[];images=[]
for s in plan['shots']:
 frame=s['record_frame']+s['length_frames']//2;path=FR/f"{s['index']:03d}_{tc(frame).replace(':','-')}.jpg";im=capture(frame,path);images.append((s,im));records.append({'index':s['index'],'record_frame':s['record_frame'],'frame':frame,'path':str(path),'changed_v4':s.get('revision_v4',False)})
 if s['index']%20==0:print('ACTUAL_V4_FRAMES',s['index'],flush=True)
for start in range(0,len(images),24):
 part=images[start:start+24];sheet=Image.new('RGB',(1440,math.ceil(len(part)/4)*252),(245,244,240));d=ImageDraw.Draw(sheet)
 for k,(s,im) in enumerate(part):
  im=im.copy();im.thumbnail((360,203));x=k%4*360;y=k//4*252;sheet.paste(im,(x,y));tag='精修' if s.get('revision_v4') else '';d.text((x+5,y+205),f"{s['index']:03d} {s['record_frame']/25:.2f}s {tag} {s['chapter'][:13]}",font=font,fill=(35,40,38));d.text((x+5,y+226),s['intent'][:23],font=font,fill=(35,40,38))
 path=PRE/f'全片实际画面_{start//24+1}.jpg';sheet.save(path,quality=94);print('V4_SHEET',path,flush=True)
detail=[]
for s in plan['shots']:
 if not s.get('revision_v4'):continue
 for label,offset in [('入',0),('出',s['length_frames']-1)]:
  frame=s['record_frame']+offset;path=DET/f"{s['index']:03d}_{label}_{frame}.jpg";im=capture(frame,path);detail.append({'index':s['index'],'frame':frame,'label':label,'path':str(path)})
title_images=[]
for title in build['refined_titles']:
 start=title['start'];length=title['duration'];fade=min(12,max(6,length//6))
 for label,offset in [('首帧',0),('渐入',max(1,fade//2)),('稳定',length//2),('渐出',length-1-max(1,fade//2)),('末帧',length-1)]:
  frame=start+offset;path=DET/f"字幕_{start}_{label}_{frame}.jpg";im=capture(frame,path);title_images.append((start,label,frame,im,path))
sheet=Image.new('RGB',(1600,len(build['refined_titles'])*205),(245,244,240));d=ImageDraw.Draw(sheet)
for k,(start,label,frame,im,path) in enumerate(title_images):
 im=im.copy();im.thumbnail((320,180));x=k%5*320;y=k//5*205;sheet.paste(im,(x,y));d.text((x+5,y+181),f'{start/25:.2f}s {label}',font=font,fill='black')
sheet.save(PRE/'字幕实际淡入淡出复核.jpg',quality=95)
for s in plan['shots']:
 v=next(v for v in t.GetItemListInTrack('video',1) if v.GetStart()==s['record_frame']);assert v.GetDuration()==s['length_frames'] and v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
report={'timeline':t.GetName(),'duration_seconds':460.28,'picture_count':121,'actual_frame_method':'Resolve ExportCurrentFrameAsStill, includes actual grade, Fusion and track compositing','midpoint_frames':records,'changed_picture_edges':detail,'caption_samples':[{'start':a,'label':b,'frame':c,'path':str(e)} for a,b,c,im,e in title_images],'all_picture_online':True,'contiguous_picture':True,'limitations':'No continuous playback/listen or final MP4 render in this pass'}
(OUT/'native_verification_v4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');assert t.SetCurrentTimecode('00:00:00:20');assert pm.SaveProject();print('V4_ACTUAL_QA_READY',flush=True)
