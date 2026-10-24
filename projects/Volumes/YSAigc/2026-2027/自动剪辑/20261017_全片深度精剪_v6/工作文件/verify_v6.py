import sys,json,time,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精剪预览';FR=PRE/'全片实际画面';FR.mkdir(exist_ok=True);DET=PRE/'改动切点与字幕';DET.mkdir(exist_ok=True)
plan=json.loads((OUT/'deep_edit_plan_v6.json').read_text());build=json.loads((OUT/'native_build_v6.json').read_text());r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name'];assert r.OpenPage('edit')
def tc(f):
 ss,ff=divmod(f,25);mm,ss=divmod(ss,60);hh,mm=divmod(mm,60);return f'{hh:02}:{mm:02}:{ss:02}:{ff:02}'
def cap(f,path):
 if path.exists():
  im=Image.open(path).convert('RGB');assert im.size==(1920,1080);return im
 assert t.SetCurrentTimecode(tc(f));time.sleep(.13);assert p.ExportCurrentFrameAsStill(str(path));im=Image.open(path).convert('RGB');assert im.size==(1920,1080);return im
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',16);records=[];mids=[]
for s in plan['shots']:
 frame=s['record_frame']+s['length_frames']//2;path=FR/f"{s['index']:03d}_{tc(frame).replace(':','-')}.jpg";im=cap(frame,path);rec={'index':s['index'],'start':s['record_frame'],'frame':frame,'path':str(path),'changed':s.get('revision_v6',False)};records.append(rec);mids.append((s,im))
 if s['index']%20==0:print('V6_ACTUAL_FRAMES',s['index'],flush=True)
for start in range(0,len(mids),24):
 part=mids[start:start+24];sheet=Image.new('RGB',(1440,math.ceil(len(part)/4)*248),(244,242,237));d=ImageDraw.Draw(sheet)
 for i,(s,im) in enumerate(part):
  im=im.copy();im.thumbnail((360,203));xx=i%4*360;yy=i//4*248;sheet.paste(im,(xx,yy));flag='精剪' if s.get('revision_v6') else '';d.text((xx+5,yy+205),f"{s['index']:03d} {s['record_frame']/25:.2f}s {flag}",font=font,fill=(35,40,35));d.text((xx+5,yy+226),s['intent'][:21],font=font,fill=(35,40,35))
 sheet.save(PRE/f'全片实际复核_{start//24+1}.jpg',quality=95)
changed=[s for s in plan['shots'] if s.get('revision_v6')];edge=[];triples=[]
for s in changed:
 row=[]
 for label,offset in [('入',0),('中',s['length_frames']//2),('出',s['length_frames']-1)]:
  frame=s['record_frame']+offset
  if label=='中':path=Path(next(a['path'] for a in records if a['start']==s['record_frame']));im=Image.open(path).convert('RGB')
  else:path=DET/f"{s['record_frame']}_{label}_{frame}.jpg";im=cap(frame,path)
  rec={'start':s['record_frame'],'frame':frame,'label':label,'path':str(path)};edge.append(rec);row.append((label,im))
 triples.append((s,row))
for start in range(0,len(triples),8):
 part=triples[start:start+8];sheet=Image.new('RGB',(1440,len(part)*295),(244,242,237));d=ImageDraw.Draw(sheet)
 for i,(s,row) in enumerate(part):
  for j,(label,im) in enumerate(row):
   im=im.copy();im.thumbnail((480,270));xx=j*480;yy=i*295;sheet.paste(im,(xx,yy));d.text((xx+5,yy+272),f"{s['record_frame']/25:.2f}s {label} {s['intent'][:15]}",font=font,fill=(35,40,35))
 sheet.save(PRE/f'精剪镜头首中尾_{start//8+1}.jpg',quality=95)
overlay_recs=[];oimgs=[]
for s in plan['interview_overlays_v6']:
 for label,off in [('入',0),('中',s['length_frames']//2),('出',s['length_frames']-1)]:
  frame=s['record_frame']+off;path=DET/f"采访补画_{s['record_frame']}_{label}.jpg";im=cap(frame,path);overlay_recs.append({'start':s['record_frame'],'frame':frame,'label':label,'path':str(path)});oimgs.append((s,label,im))
osheet=Image.new('RGB',(1440,2*295),(244,242,237));d=ImageDraw.Draw(osheet)
for i,(s,label,im) in enumerate(oimgs):
 im=im.copy();im.thumbnail((480,270));xx=i%3*480;yy=i//3*295;osheet.paste(im,(xx,yy));d.text((xx+5,yy+272),f"{s['record_frame']/25:.2f}s {label} {s['intent'][:17]}",font=font,fill=(35,40,35))
osheet.save(PRE/'校长完整原声_后半补画复核.jpg',quality=95)
title_recs=[];timgs=[]
for start,length in [(3832,59),(3954,97),(11407,100)]:
 fade= min(12,max(6,length//6)) if start!=11407 else 12
 for label,off in [('首帧',0),('渐入',fade//2),('稳定',length//2),('渐出',length-1-fade//2),('末帧',length-1)]:
  frame=start+off;path=DET/f'字幕_{start}_{label}.jpg';im=cap(frame,path);title_recs.append({'start':start,'frame':frame,'label':label,'path':str(path)});timgs.append((start,label,im))
ts=Image.new('RGB',(1600,3*205),(244,242,237));d=ImageDraw.Draw(ts)
for i,(start,label,im) in enumerate(timgs):
 im=im.copy();im.thumbnail((320,180));xx=i%5*320;yy=i//5*205;ts.paste(im,(xx,yy));d.text((xx+4,yy+182),f'{start/25:.2f}s {label}',font=font,fill=(35,40,35))
ts.save(PRE/'学校字标与片尾_实际复核.jpg',quality=95)
boundary_recs=[]
for frame in [11241,11242,11317,11318,11406,11407,11419,11457,11476,11496,11506,8395,8396,8472,8473]:
 path=DET/f'衔接_{frame}.jpg';im=cap(frame,path);boundary_recs.append({'frame':frame,'path':str(path)})
v1=t.GetItemListInTrack('video',1)
for s,v in zip(plan['shots'],v1):
 assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'] and v.GetMediaPoolItem().GetClipProperty('File Path')==s['path']
 assert v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
 if s.get('revision_v6'):
  # Resolve reports left offset on the timeline clock; source frame getters
  # can floor a floating-point value one frame early for an exact cut.
  assert v.GetLeftOffset()==round(s['in']*25)
  assert abs(v.GetSourceStartFrame()-s['source_start_frame'])<=1
assert t.GetEndFrame()==11507 and len(v1)==121 and all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]));assert t.GetIsTrackEnabled('video',2)
result={'timeline':t.GetName(),'method':'Resolve ExportCurrentFrameAsStill; real grade, actual Fusion, track compositing','duration_seconds':460.28,'picture_count':121,'midpoint_frames':records,'revised_picture_triplets':edge,'interview_cutaway_samples':overlay_recs,'caption_samples':title_recs,'boundary_samples':boundary_recs,'all_media_online':True,'no_picture_gaps':True,'no_continuous_perceptual_listen_or_watch':True}
(OUT/'native_verification_v6.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));assert t.SetCurrentTimecode('00:00:00:20');assert pm.SaveProject();print('V6_ACTUAL_QA_READY',flush=True)
