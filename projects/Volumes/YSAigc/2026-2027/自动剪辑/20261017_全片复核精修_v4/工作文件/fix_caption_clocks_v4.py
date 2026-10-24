import sys,json,time,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精修预览';DEST=PRE/'字幕最终复核';DEST.mkdir(exist_ok=True)
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()=='学校_全片复核精修_v4_20261017';assert r.OpenPage('edit');records=[]
def tc(f):
 ss,ff=divmod(f,25);mm,ss=divmod(ss,60);hh,mm=divmod(mm,60);return f'{hh:02}:{mm:02}:{ss:02}:{ff:02}'
def capture(frame,path):
 if path.exists():return Image.open(path).convert('RGB')
 assert t.SetCurrentTimecode(tc(frame));time.sleep(.25);assert p.ExportCurrentFrameAsStill(str(path));return Image.open(path).convert('RGB')
title_images=[]
for v in t.GetItemListInTrack('video',1):
 if v.GetStart() not in [3749,3832,3891,3954,11042,11407]:continue
 c=v.GetFusionCompByIndex(1);start=c.GetAttrs()['COMPN_RenderStart'];end=c.GetAttrs()['COMPN_RenderEnd'];scale=float(v.GetMediaPoolItem().GetClipProperty('FPS'))/25;fade=min(12,max(6,v.GetDuration()//6));cf=fade*scale;text=c.FindToolByID('TextPlus')
 text.Alpha1=c.BezierSpline();text.Alpha1[start]=1;text.Alpha1[end]=1
 for name in ['Merge1','Merge2']:
  merge=c.FindTool(name);merge.Blend=c.BezierSpline();merge.Blend[start]=0;merge.Blend[start+cf]=1;merge.Blend[end-cf]=1;merge.Blend[end]=0
 assert abs(c.FindTool('Merge2').GetInput('Blend',(start+end)/2)-1)<1e-8
 assert v.ExportFusionComp(str(OUT/f'v4-title-{v.GetStart()}-final.comp'),1)
 rec={'record_frame':v.GetStart(),'duration_frames':v.GetDuration(),'source_fps':float(v.GetMediaPoolItem().GetClipProperty('FPS')),'fusion_start':start,'fusion_end':end,'fade_timeline_frames':fade,'fade_source_frames':cf,'text':text.GetInput('StyledText'),'samples':[]}
 for label,offset in [('首帧',0),('渐入',max(1,fade//2)),('稳定',v.GetDuration()//2),('渐出',v.GetDuration()-1-max(1,fade//2)),('末帧',v.GetDuration()-1)]:
  frame=v.GetStart()+offset;path=DEST/f'{v.GetStart()}_{label}_{frame}.jpg';im=capture(frame,path);title_images.append((v.GetStart(),label,frame,im,path));rec['samples'].append({'frame':frame,'path':str(path),'label':label})
 # Update the existing working preview for this workflow after the frame-clock repair.
 frame=v.GetStart()+v.GetDuration()//2;match=next((p for p in (PRE/'实际画面').glob('*.jpg') if p.name.split('_',1)[1].startswith(tc(frame).replace(':','-'))),None);assert match
 im=next(im for a,b,f,im,path in title_images if a==v.GetStart() and b=='稳定');im.save(match,quality=94);records.append(rec)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',15);sheet=Image.new('RGB',(1600,6*205),(245,244,240));d=ImageDraw.Draw(sheet)
for k,(start,label,frame,im,path) in enumerate(title_images):
 im=im.copy();im.thumbnail((320,180));x=k%5*320;y=k//5*205;sheet.paste(im,(x,y));d.text((x+5,y+181),f'{start/25:.2f}s {label}',font=font,fill='black')
sheet.save(PRE/'字幕实际淡入淡出复核.jpg',quality=95)
plan=json.loads((OUT/'refined_plan_v4.json').read_text());ver=json.loads((OUT/'native_verification_v4.json').read_text());by={x['index']:x for x in ver['midpoint_frames']}
for first in [24,96,120]:
 part=plan['shots'][first:first+24];sheet=Image.new('RGB',(1440,math.ceil(len(part)/4)*252),(245,244,240));d=ImageDraw.Draw(sheet)
 for k,s in enumerate(part):
  im=Image.open(by[s['index']]['path']).convert('RGB');im.thumbnail((360,203));x=k%4*360;y=k//4*252;sheet.paste(im,(x,y));tag='精修' if s.get('revision_v4') else '';d.text((x+5,y+205),f"{s['index']:03d} {s['record_frame']/25:.2f}s {tag} {s['chapter'][:13]}",font=font,fill=(35,40,38));d.text((x+5,y+226),s['intent'][:23],font=font,fill=(35,40,38))
 sheet.save(PRE/f'全片实际画面_{first//24+1}.jpg',quality=94)
(OUT/'caption_final_timing_v4.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8');ver['caption_samples']=[{'start':rec['record_frame'],**sample} for rec in records for sample in rec['samples']];ver['caption_source_clocks_corrected']=True;(OUT/'native_verification_v4.json').write_text(json.dumps(ver,ensure_ascii=False,indent=2),encoding='utf-8');assert t.SetCurrentTimecode('00:00:00:20');assert pm.SaveProject();print('CAPTION_CLOCKS_FIXED',[(x['record_frame'],x['source_fps'],x['fusion_end']) for x in records],flush=True)
