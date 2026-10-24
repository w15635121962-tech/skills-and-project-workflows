import sys,json,time,base64,zipfile,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).parent;ROOT=OUT.parent;plan=json.loads((OUT/'edit_plan.json').read_text());ap=json.loads((OUT/'audio_plan.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';t=p.GetCurrentTimeline();assert t.GetName()==plan['name']
vs=t.GetItemListInTrack('video',1);assert len(vs)==len(plan['shots'])
checks=[]
for i,(it,s) in enumerate(zip(vs,plan['shots'])):
 assert it.GetStart()==s['record_frame'] and it.GetDuration()==s['length_frames'],(i,it.GetStart(),it.GetDuration())
 if i:assert vs[i-1].GetEnd()==it.GetStart(),'Picture gap or overlap'
 src=it.GetMediaPoolItem();assert src.GetClipProperty('File Path')==s['path'];assert src.GetClipProperty('Online Status')=='Online';assert Path(s['path']).is_file()
 assert abs(it.GetLeftOffset()/25-s['in'])<=1/25,'Source trim mismatch'
 if s['speed']!=1:
  comp=it.GetFusionCompByIndex(1);ts=next(x for x in comp.GetToolList(False).values() if x.GetAttrs().get('TOOLS_RegID')=='TimeSpeed');assert abs(ts.GetInput('Speed')-s['speed'])<.001
 checks.append({'index':i+1,'section':s['section'],'start':it.GetStart(),'end':it.GetEnd(),'path':s['path'],'online':True,'speed':s['speed']})
assert vs[0].GetStart()==0 and vs[-1].GetEnd()==plan['duration_frames']
assert t.GetEndFrame()==plan['duration_frames']
assert float(t.GetSetting('timelineFrameRate'))==25
aud=[]
for n in range(1,t.GetTrackCount('audio')+1):
 assert t.GetIsTrackEnabled('audio',n)
 for it in t.GetItemListInTrack('audio',n):
  src=it.GetMediaPoolItem();assert src.GetClipProperty('Online Status')=='Online';assert Path(src.GetClipProperty('File Path')).is_file()
  aud.append({'track':n,'start':it.GetStart(),'end':it.GetEnd(),'path':src.GetClipProperty('File Path')})
assert len(aud)==13
for expected in ap['speech']:
 actual=next(a for a in aud if a['path']==expected['path']);assert actual['start']==expected['record_frame'];assert 0<=expected['duration_frames']-(actual['end']-actual['start'])<=1
original=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()=='Timeline 1')
assert sum(len(original.GetItemListInTrack('video',i)) for i in range(1,original.GetTrackCount('video')+1))==0
assert original.GetEndFrame()==10407
assert len(original.GetItemListInTrack('audio',1))==1
assert len(t.GetMarkers())==25
# Collect rendered timeline thumbnails, including the Fusion slow-motion shots.
assert r.OpenPage('color')
def tc(fr):
 sec,f=divmod(int(fr),25);return f'{sec//3600:02}:{sec//60%60:02}:{sec%60:02}:{f:02}'
sections=list(dict.fromkeys(s['section'] for s in plan['shots']));thumbs=[]
for sec in sections:
 i=next(i for i,s in enumerate(plan['shots']) if s['section']==sec);it=vs[i];fr=it.GetStart()+min(it.GetDuration()//2,50)
 assert t.SetCurrentTimecode(tc(fr));time.sleep(.45)
 th=None
 for attempt in range(4):
  th=t.GetCurrentClipThumbnailImage()
  if th:break
  time.sleep(.5)
 if th:
  im=Image.frombytes('RGB',(th['width'],th['height']),base64.b64decode(th['data']));im.save(OUT/f'qa-section-{sec[:2]}.png');thumbs.append((sec,im,fr))
 else:print('NO THUMB',sec,flush=True)
print('THUMBNAILS',len(thumbs),flush=True)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',18);small=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',14)
sheet=Image.new('RGB',(1440,math.ceil(len(thumbs)/4)*235),(246,246,246));draw=ImageDraw.Draw(sheet)
for k,(sec,im,fr) in enumerate(thumbs):
 im=im.resize((360,202));x=k%4*360;y=k//4*235;sheet.paste(im,(x,y));draw.text((x+6,y+205),sec,font=font,fill=(25,25,25));draw.text((x+278,y+210),tc(fr),font=small,fill=(80,80,80))
sheet.save(ROOT/'粗剪画面总览.jpg',quality=92)
# Preserve native effects and edits in a timeline archive and a full project.
assert r.OpenPage('edit');assert t.SetCurrentTimecode('00:00:02:00');assert pm.SaveProject()
drt=ROOT/'学校_自动粗剪_v1.drt';drp=ROOT/'学校_自动粗剪_v1.drp'
assert not drt.exists() and not drp.exists(),'Refuse to overwrite an existing delivery'
assert t.Export(str(drt),r.EXPORT_DRT)
assert pm.ExportProject(p.GetName(),str(drp),True)
for path in [drt,drp]:
 assert path.is_file() and path.stat().st_size>1000
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
qa={'timeline':t.GetName(),'duration_frames':t.GetEndFrame(),'duration_seconds':t.GetEndFrame()/25,'fps':25,'resolution':[int(t.GetSetting('timelineResolutionWidth')),int(t.GetSetting('timelineResolutionHeight'))],'source_resolution':[1280,720],'video_items':checks,'audio_items':aud,'markers':t.GetMarkers(),'slow_motion_count':3,'picture_gaps':0,'offline_media':0,'original_timeline_preserved':True,'thumbnail_count':len(thumbs),'missing':plan['missing'],'delivery':[{'path':str(f),'size':f.stat().st_size} for f in [drt,drp]]}
(ROOT/'核验结果.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:qa[k] for k in ['timeline','duration_seconds','fps','resolution','slow_motion_count','picture_gaps','offline_media','thumbnail_count','delivery']},ensure_ascii=False),flush=True)
