from common_v14 import *
r,pm,p,mp,t=connect();assert t.SetCurrentTimecode(tc(88));it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==60);print('BEFORE',it.GetFusionCompCount(),it.GetFusionCompNameList(),flush=True)
c=it.ImportFusionComp(str(OUT/'原生缓推_1_60.comp'));assert c;c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25});print('IMPORTED',it.GetFusionCompCount(),it.GetFusionCompNameList(),c.GetAttrs(),flush=True)
names=it.GetFusionCompNameList();name=next(iter(names.values())) if isinstance(names,dict) else names[0];print('LOAD',it.LoadFusionCompByName(name),flush=True);assert pm.SaveProject();r.Fusion().PurgeCache();assert r.OpenPage('edit');cap(p,t,116,PRE/'缓推导入复核_60_末.jpg',1)
assert pm.CloseProject(p);p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==60);print('REOPENED',it.GetFusionCompCount(),it.GetFusionCompNameList(),flush=True);cap(p,t,116,PRE/'缓推导入重开复核_60_末.jpg',1)
for tag in ['缓推导入复核_60_末.jpg','缓推导入重开复核_60_末.jpg']:
 print(tag,float(abs(np.array(Image.open(PRE/tag),float)-np.array(Image.open(PRE/'连续运动核验'/'书写_原版'/'0056.jpg'),float)).mean()),flush=True)
assert pm.SaveProject()
