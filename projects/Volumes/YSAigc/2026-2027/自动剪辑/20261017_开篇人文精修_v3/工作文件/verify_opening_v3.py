import sys,json,time,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageStat
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'开篇预览';PRE.mkdir(exist_ok=True);plan=json.loads((OUT/'opening_plan_v3.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name'];assert r.OpenPage('edit')
def tc(frame):
 sec,fr=divmod(frame,25);mins,ss=divmod(sec,60);hh,mm=divmod(mins,60)
 return f'{hh:02d}:{mm:02d}:{ss:02d}:{fr:02d}'
def capture(frame,name):
 path=PRE/(name+'.jpg');assert not path.exists();assert t.SetCurrentTimecode(tc(frame));time.sleep(.22);assert p.ExportCurrentFrameAsStill(str(path));im=Image.open(path).convert('RGB');assert im.size==(1920,1080);return path,im
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',16);records=[];images=[]
for s in plan['shots']:
 frame=s['record_frame']+s['length_frames']//2;path,im=capture(frame,f"{s['index']:02d}_{tc(frame).replace(':','-')}");records.append({'frame':frame,'path':str(path),'index':s['index']});images.append((s,im))
sheet=Image.new('RGB',(1440,5*254),(245,244,240));d=ImageDraw.Draw(sheet)
for i,(s,im) in enumerate(images):
 im=im.copy();im.thumbnail((360,203));x=i%4*360;y=i//4*254;sheet.paste(im,(x,y));d.text((x+5,y+205),f"{s['record_frame']/25:.2f}–{(s['record_frame']+s['length_frames'])/25:.2f}s",font=font,fill=(35,40,38));d.text((x+5,y+228),s['intent'][:22],font=font,fill=(35,40,38))
sheet.save(PRE/'开篇人文精修总览.jpg',quality=94)
samples=[]
for frame,label in [(0,'淡入首帧'),(6,'淡入中段'),(12,'淡入完成'),(382,'片名前一帧'),(383,'片名首帧'),(389,'片名缓入中'),(399,'片名已进入'),(430,'片名稳定画面'),(495,'片名淡出开始'),(501,'片名淡出中'),(507,'片名末帧'),(508,'片名退出后'),(1766,'开篇末帧'),(1767,'历史段承接首帧')]:
 path,im=capture(frame,f'{frame:05d}_{label}');samples.append({'frame':frame,'path':str(path),'mean':ImageStat.Stat(im).mean})
v1=t.GetItemListInTrack('video',1);audio=[{'track':i,'start':a.GetStart(),'end':a.GetEnd(),'offset':a.GetLeftOffset(),'path':a.GetMediaPoolItem().GetClipProperty('File Path')} for i in range(1,t.GetTrackCount('audio')+1) for a in t.GetItemListInTrack('audio',i)]
assert len(v1)==120 and t.GetEndFrame()==11507 and len(audio)==10
assert all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]));assert audio[0]['start']==0 and audio[0]['end']==10842
assert all(v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online' for v in v1)
report={'timeline':t.GetName(),'duration_frames':11507,'duration_seconds':460.28,'video_count':120,'overlay_count':1,'audio_count':10,'audio':audio,'frames':records,'entry_exit_samples':samples,'method':'Resolve ExportCurrentFrameAsStill, actual grade and Fusion output; no full MP4 render','picture_contiguous':True,'all_online':True}
(OUT/'native_verification_v3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');assert t.SetCurrentTimecode('00:00:00:20');assert pm.SaveProject();print('V3_PREVIEW_VERIFIED',len(records),flush=True)
