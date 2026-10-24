import sys,json,math,time
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';plan=json.loads((OUT/'narrative_edit_plan.json').read_text());ap=json.loads((OUT/'audio_plan_v2.json').read_text());nar=json.loads((OUT/'narration_aligned.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();root=mp.GetRootFolder()
assert plan['name'] not in [p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)],'Do not overwrite a prior edit'
folder=mp.AddSubFolder(root,'旁白精修_人文科学_v2_20261017');assert folder;assert mp.SetCurrentFolder(folder)
def walk(f):
 yield from f.GetClipList()
 for sf in f.GetSubFolderList():yield from walk(sf)
pool={x.GetClipProperty('File Path'):x for x in walk(root)}
for s in plan['shots']:
 if s['path'] not in pool:
  x=mp.ImportMedia([s['path']]);assert x and len(x)==1,s['path'];pool[s['path']]=x[0]
t=mp.CreateEmptyTimeline(plan['name']);assert t;assert p.SetCurrentTimeline(t)
assert t.SetSetting('useCustomSettings','1')
for k,v in [('timelineFrameRate','25'),('timelineResolutionWidth','1920'),('timelineResolutionHeight','1080')]:assert t.SetSetting(k,v),(k,v)
assert t.SetStartTimecode('00:00:00:00');assert r.OpenPage('edit')
infos=[]
for s in plan['shots']:
 src=pool[s['path']];fps=float(src.GetClipProperty('FPS'));count=math.ceil(s['length_frames']/25*fps-1e-8);a=round(s['in']*fps)
 infos.append({'mediaPoolItem':src,'startFrame':a,'endFrame':a+count,'mediaType':1,'trackIndex':1,'recordFrame':s['record_frame']})
items=[]
for i in range(0,len(infos),20):
 batch=mp.AppendToTimeline(infos[i:i+20]);assert batch and len(batch)==len(infos[i:i+20]);items.extend(batch);print('PICTURE',len(items),flush=True)
for i,(it,s) in enumerate(zip(items,plan['shots'])):
 assert it.GetStart()==s['record_frame'] and it.GetDuration()==s['length_frames'],(i+1,it.GetStart(),it.GetDuration(),s['length_frames'])
 assert it.GetMediaPoolItem().GetClipProperty('Online Status')=='Online',s['path']
 if s['log']:assert it.GetNodeGraph().SetLUT(1,'Sony/SLog3SGamut3.CineToLC-709TypeA.cube')
 if not (s['speed']!=1 or s['title'] or i in [0,len(items)-1]):continue
 comp=it.AddFusionComp();assert comp
 tools=list(comp.GetToolList(False).values());mi=next(z for z in tools if z.GetAttrs().get('TOOLS_RegID')=='MediaIn');mo=next(z for z in tools if z.GetAttrs().get('TOOLS_RegID')=='MediaOut');prev=mi
 resolution=it.GetMediaPoolItem().GetClipProperty('Resolution');w,h=map(int,resolution.split('x'))
 comp.SetPrefs({'Comp.FrameFormat.Width':w,'Comp.FrameFormat.Height':h,'Comp.FrameFormat.Rate':25})
 if s['speed']!=1:
  ts=comp.AddTool('TimeSpeed');assert ts and ts.ConnectInput('Input',prev);ts.SetInput('Speed',s['speed']);ts.SetInput('Delay',0);ts.SetInput('InterpolateBetweenFrames',1)
  assert abs(ts.GetInput('Speed')-s['speed'])<.001;prev=ts
 if s['title']:
  two='\n' in s['title'];center=.17 if two else .115
  rect=comp.AddTool('RectangleMask');bg=comp.AddTool('Background');merge=comp.AddTool('Merge');txt=comp.AddTool('TextPlus');txmerge=comp.AddTool('Merge');assert all([rect,bg,merge,txt,txmerge])
  rect.SetInput('Center',{1:.5,2:center});rect.SetInput('Width',.88 if two else .78);rect.SetInput('Height',.225 if two else .105);rect.SetInput('SoftEdge',.004)
  bg.SetInput('UseFrameFormatSettings',1);bg.SetInput('TopLeftRed',.035);bg.SetInput('TopLeftGreen',.045);bg.SetInput('TopLeftBlue',.05);bg.SetInput('TopLeftAlpha',.48)
  assert bg.ConnectInput('EffectMask',rect);assert merge.ConnectInput('Background',prev);assert merge.ConnectInput('Foreground',bg)
  txt.SetInput('StyledText',s['title']);txt.SetInput('Font','Heiti SC');txt.SetInput('Style','Light');txt.SetInput('Size',.059 if two else .045);txt.SetInput('Center',{1:.5,2:center});txt.SetInput('Red1',.97);txt.SetInput('Green1',.97);txt.SetInput('Blue1',.94)
  assert txt.GetInput('StyledText')==s['title'];txt.Alpha1=comp.BezierSpline();last=it.GetDuration()-1;fade=min(8,last//4);txt.Alpha1[0]=0;txt.Alpha1[fade]=1;txt.Alpha1[last-fade]=1;txt.Alpha1[last]=0
  assert txmerge.ConnectInput('Background',merge);assert txmerge.ConnectInput('Foreground',txt);prev=txmerge
 if i in [0,len(items)-1]:
  bc=comp.AddTool('BrightnessContrast');assert bc and bc.ConnectInput('Input',prev);bc.Gain=comp.BezierSpline();last=it.GetDuration()-1
  if i==0:bc.Gain[0]=0;bc.Gain[20]=1
  else:bc.Gain[last-30]=1;bc.Gain[last]=0
  prev=bc
 assert mo.ConnectInput('Input',prev)
 assert it.ExportFusionComp(str(OUT/f'v2-fusion-{i+1}.comp'),1)
 print('COMPOSITE',i+1,'title' if s['title'] else 'motion',flush=True)
while t.GetTrackCount('audio')<4:assert t.AddTrack('audio','stereo')
for i,name in enumerate(['旁白主线_完整原配音','现场口号与校长讲话','人文配乐_钢琴木吉他','探索配乐与尾声'],1):assert t.SetTrackName('audio',i,name);assert t.SetTrackEnable('audio',i,True)
assert t.SetTrackName('video',1,'画面_逐句对应旁白')
ab=mp.AddSubFolder(folder,'声音与配乐');assert ab and mp.SetCurrentFolder(ab)
audio_actual=[]
for a in ap['speech']+ap['music']:
 imported=mp.ImportMedia([a['path']]);assert imported and len(imported)==1;src=imported[0];fps=float(src.GetClipProperty('FPS') or 24);count=math.ceil(a['duration_frames']/25*fps-1e-8)
 args={'mediaPoolItem':src,'startFrame':0,'endFrame':count,'mediaType':2,'trackIndex':a['track'],'recordFrame':a['record_frame']}
 ret=mp.AppendToTimeline([args]);assert ret and len(ret)==1;it=ret[0]
 if it.GetDuration()>a['duration_frames']:
  assert t.DeleteClips([it],False);args['endFrame']=count-1;ret=mp.AppendToTimeline([args]);assert ret;it=ret[0]
 assert it.GetStart()==a['record_frame'] and 0<=a['duration_frames']-it.GetDuration()<=1,(a['kind'],it.GetDuration(),a['duration_frames'])
 if a['kind']=='location':
  vi=next(v for v in items if v.GetStart()==a['record_frame']);assert t.SetClipsLinked([vi,it],True)
 audio_actual.append({'kind':a['kind'],'path':a['path'],'start':it.GetStart(),'end':it.GetEnd(),'track':a['track']})
 print('AUDIO',a['kind'],it.GetStart(),it.GetDuration(),flush=True)
for c in nar['chapters']:
 start=round(c['start']*25);dur=max(1,round((c['end']-c['start'])*25));assert t.AddMarker(start,'Blue' if c['id']<6 else 'Green',c['name'],'按完整旁白解说精修；人文温度与科学求知',dur,'narrative-v2')
assert t.AddMarker(434*25,'Purple','尾声：师者与育人目标','教师和群体口号后接校长完整育人目标句，避免重复一分钟采访',round((460.28-434)*25),'narrative-v2-coda')
assert t.GetEndFrame()==plan['duration_frames'];assert pm.SaveProject();assert t.SetCurrentTimecode('00:00:02:00')
(OUT/'native_build_v2.json').write_text(json.dumps({'timeline':t.GetName(),'video_items':[{'name':v.GetName(),'start':v.GetStart(),'end':v.GetEnd(),'offset':v.GetLeftOffset(),'path':v.GetMediaPoolItem().GetClipProperty('File Path')} for v in items],'audio_items':audio_actual,'markers':t.GetMarkers()},ensure_ascii=False,indent=2),encoding='utf-8')
print('BUILT_V2',t.GetName(),t.GetEndFrame()/25,flush=True)
