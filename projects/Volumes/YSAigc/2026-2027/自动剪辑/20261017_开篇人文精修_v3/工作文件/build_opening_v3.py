import sys,json,math,time
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';plan=json.loads((OUT/'opening_plan_v3.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();base=p.GetCurrentTimeline();assert base.GetName()==plan['base_timeline'];assert base.GetEndFrame()==11507
def snap(t):
 return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
before=snap(base);(OUT/'live_before_v3.json').write_text(json.dumps({'timeline':base.GetName(),'timecode':base.GetCurrentTimecode(),'page':r.GetCurrentPage(),'selected_pool_media':[x.GetName() for x in (mp.GetSelectedClips() or [])],'snapshot':before},ensure_ascii=False,indent=2),encoding='utf-8')
assert plan['name'] not in [p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)]
backup=ROOT/'学校_开篇精修前备份.drp';assert pm.SaveProject()
if not backup.exists():assert pm.ExportProject('学校',str(backup),True)
else:assert backup.stat().st_size>1000
t=base.DuplicateTimeline(plan['name']);assert t and p.SetCurrentTimeline(t);assert r.OpenPage('edit')
assert snap(t)==before,'Native duplicate must preserve all existing media, timing and properties'
old=t.GetItemListInTrack('video',1);remove=[v for v in old if v.GetEnd()<=1767];assert len(remove)==17 and remove[-1].GetEnd()==1767
assert t.DeleteClips(remove,False);assert t.GetEndFrame()==11507
folder=next((f for f in mp.GetRootFolder().GetSubFolderList() if f.GetName()=='开篇人文精修_v3_20261017'),None)
if not folder:folder=mp.AddSubFolder(mp.GetRootFolder(),'开篇人文精修_v3_20261017')
assert folder and mp.SetCurrentFolder(folder)
def walk(f):
 yield from f.GetClipList()
 for sf in f.GetSubFolderList():yield from walk(sf)
pool={x.GetClipProperty('File Path'):x for x in walk(mp.GetRootFolder())}
for s in plan['shots']:
 if s['path'] not in pool:
  imported=mp.ImportMedia([s['path']]);assert imported and len(imported)==1;smi=imported[0];pool[s['path']]=smi
infos=[]
for s in plan['shots']:
 src=pool[s['path']];fps=float(src.GetClipProperty('FPS'));count=math.ceil(s['length_frames']/25*fps-1e-8);a=round(s['in']*fps)
 infos.append({'mediaPoolItem':src,'startFrame':a,'endFrame':a+count,'mediaType':1,'trackIndex':1,'recordFrame':s['record_frame']})
items=mp.AppendToTimeline(infos);assert items and len(items)==20
for i,(s,v) in enumerate(zip(plan['shots'],items)):
 assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'],(i,v.GetStart(),v.GetDuration())
 assert v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
 if s['log']:assert v.GetNodeGraph().SetLUT(1,'Sony/SLog3SGamut3.CineToLC-709TypeA.cube')
 v.SetClipColor('Blue')
 if i==0 or s['speed']!=1:
  comp=v.AddFusionComp();assert comp;mi=comp.FindToolByID('MediaIn');mo=comp.FindToolByID('MediaOut');prev=mi
  if s['speed']!=1:
   speed=comp.AddTool('TimeSpeed');assert speed and speed.ConnectInput('Input',prev);speed.SetInput('Speed',s['speed']);speed.SetInput('Delay',0);speed.SetInput('InterpolateBetweenFrames',1);assert abs(speed.GetInput('Speed')-s['speed'])<.001;prev=speed
  if i==0:
   bc=comp.AddTool('BrightnessContrast');assert bc and bc.ConnectInput('Input',prev);bc.Gain=comp.BezierSpline();bc.Gain[0]=0;bc.Gain[12]=1;prev=bc
  assert mo.ConnectInput('Input',prev);assert v.ExportFusionComp(str(OUT/f'v3-shot-{i+1}.comp'),1)
assert t.GetTrackCount('video')==1;assert t.AddTrack('video');assert t.SetTrackName('video',2,'片名_人文留白_独立可编辑');assert t.SetTrackName('video',1,'画面_书香与师生_开篇人文精修')
assert t.SetCurrentTimecode('00:00:15:08');assert t.SetTrackLock('video',1,True)
for track in before['audio']:assert t.SetTrackLock('audio',track['track'],True)
title=t.InsertFusionTitleIntoTimeline('Text+');assert title
assert t.SetTrackLock('video',1,False)
for track in before['audio']:assert t.SetTrackLock('audio',track['track'],track['locked'])
assert title.GetStart()==383 and title.GetDuration()==125,(title.GetStart(),title.GetDuration())
assert len(t.GetItemListInTrack('video',2))==1 and title.GetTrackTypeAndIndex()==['video',2],title.GetTrackTypeAndIndex()
assert title.SetName('汇启新章 · 共育未来｜文汇中学教育集团')
c=title.GetFusionCompByIndex(1);assert c;main=c.FindToolByID('TextPlus');mo=c.FindToolByID('MediaOut');assert main and mo
c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25})
def configure(txt,text,size,xy,shadow=False,delay=0):
 txt.SetInput('StyledText',text);txt.SetInput('Font','Heiti SC');txt.SetInput('Style','Light');txt.SetInput('Size',size);txt.SetInput('Center',{1:xy[0],2:xy[1]})
 for key,value in [('Red1',.025 if shadow else .97),('Green1',.035 if shadow else .965),('Blue1',.03 if shadow else .94)]:txt.SetInput(key,value)
 alpha=.65 if shadow else 1;txt.Alpha1=c.BezierSpline();txt.Alpha1[delay]=0;txt.Alpha1[delay+12]=alpha;txt.Alpha1[112]=alpha;txt.Alpha1[124]=0
 assert txt.GetInput('StyledText')==text
configure(main,plan['title']['main'],.041,(.5,.275))
sub=c.AddTool('TextPlus');shadow=c.AddTool('TextPlus');subshadow=c.AddTool('TextPlus');assert sub and shadow and subshadow
configure(sub,plan['title']['sub'],.024,(.5,.195),delay=4);configure(shadow,plan['title']['main'],.041,(.501,.273),True);configure(subshadow,plan['title']['sub'],.024,(.501,.193),True,4)
prev=shadow
for layer in [main,subshadow,sub]:
 merge=c.AddTool('Merge');assert merge and merge.ConnectInput('Background',prev) and merge.ConnectInput('Foreground',layer);prev=merge
assert mo.ConnectInput('Input',prev);assert title.ExportFusionComp(str(OUT/'v3-independent-title.comp'),1)
after=snap(t)
assert after['audio']==before['audio'],'All original audio properties and timings must be preserved'
before_outside=[x for x in before['video'][0]['items'] if x['start']>=1767];after_outside=[x for x in after['video'][0]['items'] if x['start']>=1767];assert before_outside==after_outside,'Picture outside opening must be preserved'
v1=t.GetItemListInTrack('video',1);assert len(v1)==120
assert v1[0].GetStart()==0 and v1[-1].GetEnd()==11507
assert all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]));assert t.GetEndFrame()==11507
assert t.AddMarker(0,'Cyan','v3 开篇：书香与陪伴','书页→阅读→自然入校→师生围读→晨光片名。音频保持原样；70.68秒后保留v2。',1767,'v3-human-opening')
assert pm.SaveProject();assert t.SetCurrentTimecode('00:00:01:00')
(OUT/'native_build_v3.json').write_text(json.dumps({'timeline':t.GetName(),'fps':25,'duration_frames':t.GetEndFrame(),'video_count':len(v1),'overlay_count':1,'preserved_audio':True,'preserved_picture_after_70_68':True,'snapshot':after},ensure_ascii=False,indent=2),encoding='utf-8');print('V3_BUILT',t.GetName(),len(v1),flush=True)
