import sys,json,base64,time
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).parent;plan=json.loads((OUT/'edit_plan.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();root=mp.GetRootFolder()
def walk(f):
 yield from f.GetClipList()
 for sf in f.GetSubFolderList():yield from walk(sf)
lookup={it.GetClipProperty('File Path'):it for it in walk(root)}
f=next((f for f in root.GetSubFolderList() if f.GetName()=='自动剪辑_20261017'),None) or mp.AddSubFolder(root,'自动剪辑_20261017')
assert mp.SetCurrentFolder(f)
existing=[p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)]
if plan['name'] in existing:
 t=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==plan['name'])
 old=t.GetItemListInTrack('video',1)
 previous=json.loads((OUT/'picture_import.json').read_text()) if (OUT/'picture_import.json').exists() else plan['shots']
 assert len(old)==len(previous) and all(it.GetMediaPoolItem().GetClipProperty('File Path')==s['path'] for it,s in zip(old,previous)),'Generated timeline changed, inspect before rebuilding'
 assert not any(t.GetItemListInTrack('audio',n) for n in range(1,t.GetTrackCount('audio')+1))
 assert t.DeleteClips(old,False)
else:t=mp.CreateEmptyTimeline(plan['name'])
assert t;assert p.SetCurrentTimeline(t)
assert t.SetSetting('useCustomSettings','1')
for key,val in [('timelineFrameRate','25'),('timelinePlaybackFrameRate','25'),('timelineResolutionWidth','1920'),('timelineResolutionHeight','1080')]:
 result=t.SetSetting(key,val);print('SETTING',key,result,flush=True)
assert float(t.GetSetting('timelineFrameRate'))==25
assert t.SetStartTimecode('00:00:00:00')
infos=[]
for s in plan['shots']:
 src=lookup.get(s['path']);assert src,s['name']
 fps=float(src.GetClipProperty('FPS'));a=round(s['in']*fps);count=round(s['length_frames']/25*fps)
 infos.append({'mediaPoolItem':src,'startFrame':a,'endFrame':a+count,'mediaType':1,'trackIndex':1,'recordFrame':s['record_frame']})
items=[]
for i in range(0,len(infos),20):
 batch=mp.AppendToTimeline(infos[i:i+20]);assert batch and len(batch)==len(infos[i:i+20]),i;items.extend(batch);print('APPENDED',len(items),flush=True)
data=[]
assert r.OpenPage('edit')
for i,(it,s) in enumerate(zip(items,plan['shots'])):
 assert it.GetStart()==s['record_frame'],(i,it.GetStart(),s['record_frame'])
 assert it.GetDuration()==s['length_frames'],(i,it.GetDuration(),s['length_frames'])
 if s['speed']!=1:
  comp=it.AddFusionComp();assert comp
  tools=comp.GetToolList(False)
  mi=next(tool for tool in tools.values() if tool.GetAttrs().get('TOOLS_RegID')=='MediaIn')
  mo=next(tool for tool in tools.values() if tool.GetAttrs().get('TOOLS_RegID')=='MediaOut')
  ts=comp.AddTool('TimeSpeed');assert ts
  attrs=comp.GetAttrs();start=attrs.get('COMPN_RenderStart',attrs.get('COMPN_GlobalStart',0))
  assert ts.ConnectInput('Input',mi)
  ts.SetInput('Speed',s['speed'])
  ts.SetInput('Delay',start*(1-s['speed']))
  ts.SetInput('InterpolateBetweenFrames',1)
  assert abs(ts.GetInput('Speed')-s['speed'])<.0001
  assert abs(ts.GetInput('Delay')-start*(1-s['speed']))<.0001
  assert mo.ConnectInput('Input',ts)
  print('RETIME',i+1,'START',start,'SPEED',s['speed'],flush=True)
  (OUT/f'retime-{i+1}.json').write_text(json.dumps({'attrs':attrs,'input_names':[v.GetAttrs() for v in ts.GetInputList().values()]},ensure_ascii=False,indent=2),encoding='utf-8')
  assert it.ExportFusionComp(str(OUT/f'retime-{i+1}.comp'),1)
  assert it.SetProperty('RetimeProcess',2)
 data.append({'index':i,'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'fps':it.GetMediaPoolItem().GetClipProperty('FPS'),'path':it.GetMediaPoolItem().GetClipProperty('File Path')})
assert t.GetEndFrame()==plan['duration_frames']
(OUT/'picture_import.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
assert pm.SaveProject();assert r.OpenPage('color');time.sleep(.3)
def tc(fr):
 sec,ff=divmod(int(fr),25);return f'{sec//3600:02}:{sec//60%60:02}:{sec%60:02}:{ff:02}'
for i in [0,17,41,52,75,83]:
 it=items[i];assert t.SetCurrentTimecode(tc(it.GetStart()+it.GetDuration()//2));time.sleep(.25);th=t.GetCurrentClipThumbnailImage()
 if th:Image.frombytes('RGB',(th['width'],th['height']),base64.b64decode(th['data'])).save(OUT/f'native-before-{i+1}.png')
assert r.OpenPage('edit');assert t.SetCurrentTimecode('00:00:00:00')
print('BUILT',t.GetName(),'SECONDS',(t.GetEndFrame()-t.GetStartFrame())/25,flush=True)
