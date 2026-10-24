import json,sys,time,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';DEST=ROOT/'精修预览'/'实际画面';DEST.mkdir(exist_ok=True)
plan=json.loads((OUT/'narrative_edit_plan.json').read_text());r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name'];assert r.OpenPage('edit')
def tc(frame):
 sec,fr=divmod(frame,25);mins,ss=divmod(sec,60);hh,mm=divmod(mins,60)
 return f'{hh:02d}:{mm:02d}:{ss:02d}:{fr:02d}'
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',15);images=[];records=[]
for s in plan['shots']:
 f=s['record_frame']+s['length_frames']//2;assert t.SetCurrentTimecode(tc(f));time.sleep(.32 if s['title'] or s['speed']!=1 else .12)
 dest=DEST/f"{s['index']:03d}_{tc(f).replace(':','-')}.jpg"
 assert p.ExportCurrentFrameAsStill(str(dest)),s['index'];assert dest.exists() and dest.stat().st_size>1000
 im=Image.open(dest).convert('RGB');assert im.size==(1920,1080),im.size;images.append((s,im.copy()));records.append({'index':s['index'],'frame':f,'path':str(dest),'method':'Resolve ExportCurrentFrameAsStill; includes native Fusion, grade and framing'})
 if s['title']:
  proof=ROOT/'精修预览'/f"字幕实际画面_{s['index']:03d}.jpg";im.save(proof,quality=95)
 if s['index']%20==0:print('ACTUAL_FRAMES',s['index'],flush=True)
for start in range(0,len(images),24):
 part=images[start:start+24];sheet=Image.new('RGB',(1440,math.ceil(len(part)/4)*252),(245,244,240));draw=ImageDraw.Draw(sheet)
 for k,(s,im) in enumerate(part):
  x=k%4*360;y=k//4*252;im=im.copy();im.thumbnail((360,203));sheet.paste(im,(x,y))
  draw.text((x+5,y+205),f"{s['index']:03d}  {s['record_frame']/25:.2f}s  {s['chapter'][:16]}",font=font,fill=(35,40,38));draw.text((x+5,y+226),s['intent'][:23],font=font,fill=(35,40,38))
 dest=ROOT/'精修预览'/f'精修时间线_{start//24+1}.jpg';sheet.save(dest,quality=94);print('ACTUAL_SHEET',dest,flush=True)
(OUT/'native_actual_frames.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
assert t.SetCurrentTimecode('00:00:02:00');assert pm.SaveProject();print('ACTUAL_PREVIEWS_COMPLETE',flush=True)
