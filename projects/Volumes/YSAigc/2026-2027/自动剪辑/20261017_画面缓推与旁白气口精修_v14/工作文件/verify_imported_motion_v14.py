from common_v14 import *
r,pm,p,mp,t=connect();it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==60);print('PRE_SAVE',it.GetFusionCompCount(),it.GetFusionCompNameList(),flush=True);assert pm.SaveProject();assert r.OpenPage('edit');cap(p,t,116,PRE/'缓推导入复核_60_末.jpg',1)
assert pm.CloseProject(p);p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==60);print('REOPENED',it.GetFusionCompCount(),it.GetFusionCompNameList(),flush=True);cap(p,t,116,PRE/'缓推导入重开复核_60_末.jpg',1)
for tag in ['缓推导入复核_60_末.jpg','缓推导入重开复核_60_末.jpg']:
 print(tag,float(abs(np.array(Image.open(PRE/tag),float)-np.array(Image.open(PRE/'连续运动核验'/'书写_原版'/'0056.jpg'),float)).mean()),flush=True)
print('A1',[(x.GetStart(),x.GetEnd()) for x in t.GetItemListInTrack('audio',1)],flush=True);assert pm.SaveProject()
