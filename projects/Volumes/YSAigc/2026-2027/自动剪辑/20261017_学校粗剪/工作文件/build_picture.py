import sys,json,base64,time
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).parent;plan=json.loads((OUT/'edit_plan.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool()
existing=[p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)]
assert plan['name'] not in existing,'Timeline already exists, inspect instead of overwriting'
f=mp.AddSubFolder(mp.GetRootFolder(),'自动剪辑_20261017');assert f;assert mp.SetCurrentFolder(f)
t=mp.ImportTimelineFromFile(str(OUT.parent/'学校_自动粗剪.fcpxml'),{'timelineName':plan['name'],'importSourceClips':True})
assert t,'FCPXML import failed';assert p.SetCurrentTimeline(t)
assert float(t.GetSetting('timelineFrameRate'))==25
items=t.GetItemListInTrack('video',1)
print('IMPORTED',len(items),'DURATION',t.GetEndFrame()-t.GetStartFrame(),flush=True)
assert len(items)==len(plan['shots']),(len(items),len(plan['shots']))
data=[]
for i,(it,s) in enumerate(zip(items,plan['shots'])):
 data.append({'index':i,'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'fps':it.GetMediaPoolItem().GetClipProperty('FPS'),'path':it.GetMediaPoolItem().GetClipProperty('File Path')})
 assert it.GetDuration()==s['length_frames'],(i,it.GetDuration(),s['length_frames'])
for a in range(1,t.GetTrackCount('audio')+1):assert t.SetTrackEnable('audio',a,False)
(OUT/'picture_import.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
assert pm.SaveProject()
page=r.GetCurrentPage();assert r.OpenPage('color');time.sleep(.3)
def tc(fr):
 sec,ff=divmod(int(fr),25);return f'{sec//3600:02}:{sec//60%60:02}:{sec%60:02}:{ff:02}'
for i in [0,17,42,52,76,83]:
 it=items[i];assert t.SetCurrentTimecode(tc(it.GetStart()+it.GetDuration()//2));time.sleep(.25)
 th=t.GetCurrentClipThumbnailImage()
 if th:
  Image.frombytes('RGB',(th['width'],th['height']),base64.b64decode(th['data'])).save(OUT/f'native-before-{i+1}.png')
 else:print('NO THUMB',i+1,flush=True)
assert r.OpenPage(page)
print(json.dumps({'timeline':t.GetName(),'fps':t.GetSetting('timelineFrameRate'),'duration_seconds':(t.GetEndFrame()-t.GetStartFrame())/25,'video_items':len(items),'video_tracks':t.GetTrackCount('video'),'audio_tracks':t.GetTrackCount('audio')},ensure_ascii=False),flush=True)
