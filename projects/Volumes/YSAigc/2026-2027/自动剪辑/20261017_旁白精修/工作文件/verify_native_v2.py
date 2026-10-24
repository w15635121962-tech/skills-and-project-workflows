import sys,json,time,base64,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageStat
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PREVIEW=ROOT/'精修预览';PREVIEW.mkdir(exist_ok=True)
plan=json.loads((OUT/'narrative_edit_plan.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool()
t=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==plan['name']);assert p.SetCurrentTimeline(t)
assert float(t.GetSetting('timelineFrameRate'))==25;assert t.GetEndFrame()==11507
items=t.GetItemListInTrack('video',1);assert len(items)==117
for s,v in zip(plan['shots'],items):
 assert v.GetStart()==s['record_frame'] and v.GetEnd()==s['record_frame']+s['length_frames'],s['index']
 assert v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online',s['path']
assert t.GetTrackCount('audio')==4
audio=[{'track':track,'start':a.GetStart(),'end':a.GetEnd(),'enabled':a.GetClipEnabled(),'name':a.GetName(),'path':a.GetMediaPoolItem().GetClipProperty('File Path')} for track in range(1,5) for a in t.GetItemListInTrack('audio',track)]
assert len(audio)==10
assert audio[0]['start']==0 and audio[0]['end']/25>=433.6588125
assert all(a['enabled'] for a in audio)
assert r.OpenPage('color');time.sleep(.8)
def tc(frame):
 sec,fr=divmod(frame,25);mins,ss=divmod(sec,60);hh,mm=divmod(mins,60)
 return f'{hh:02d}:{mm:02d}:{ss:02d}:{fr:02d}'
records=[];images=[]
for s in plan['shots']:
 frame=s['record_frame']+s['length_frames']//2
 assert t.SetCurrentTimecode(tc(frame));time.sleep(.65 if s['title'] or s['speed']!=1 else .35)
 thumb=None
 for retry in range(8):
  thumb=t.GetCurrentClipThumbnailImage()
  if thumb and thumb.get('data'):break
  time.sleep(.5)
 assert thumb and thumb.get('data'),s['index']
 raw=base64.b64decode(thumb['data']);im=Image.frombytes('RGB',(int(thumb['width']),int(thumb['height'])),raw)
 dest=PREVIEW/f"{s['index']:03d}_{tc(frame).replace(':','-')}.jpg";im.save(dest,quality=92)
 rec={'index':s['index'],'frame':frame,'timecode':tc(frame),'path':str(dest),'native_dimensions':im.size,'rgb_mean':ImageStat.Stat(im).mean,'title':s['title']}
 records.append(rec);images.append((s,im));
 if s['index']%20==0:print('VERIFIED_THUMBNAILS',s['index'],flush=True)
fnt=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',15)
for start in range(0,len(images),24):
 part=images[start:start+24];sheet=Image.new('RGB',(1440,math.ceil(len(part)/4)*252),(245,244,240));draw=ImageDraw.Draw(sheet)
 for k,(s,im) in enumerate(part):
  x=k%4*360;y=k//4*252;im=im.copy();im.thumbnail((360,203));sheet.paste(im,(x+(360-im.width)//2,y))
  draw.text((x+5,y+205),f"{s['index']:03d}  {s['record_frame']/25:.2f}s  {s['chapter'][:16]}",font=fnt,fill=(35,40,38))
  draw.text((x+5,y+226),s['intent'][:23],font=fnt,fill=(35,40,38))
 dest=PREVIEW/f'精修时间线_{start//24+1}.jpg';sheet.save(dest,quality=93);print('CONTACT_SHEET',dest,flush=True)
report={'timeline':t.GetName(),'duration_seconds':t.GetEndFrame()/25,'fps':t.GetSetting('timelineFrameRate'),'resolution':[t.GetSetting('timelineResolutionWidth'),t.GetSetting('timelineResolutionHeight')],'video_count':len(items),'audio_count':len(audio),'audio':audio,'all_picture_online':True,'picture_contiguous':True,'narration_complete':True,'other_timelines':[p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)],'thumbnails':records}
(OUT/'native_verification_v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert t.SetCurrentTimecode('00:00:02:00');assert r.OpenPage('edit');assert pm.SaveProject();print('VERIFIED_V2',flush=True)
